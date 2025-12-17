"""Performance benchmarks and regression tests for compas_slicer.

Run benchmarks:
    pytest tests/test_performance.py --benchmark-only

Save baseline:
    pytest tests/test_performance.py --benchmark-save=baseline

Compare to baseline:
    pytest tests/test_performance.py --benchmark-compare=baseline

Fail on regression (>20% slower):
    pytest tests/test_performance.py --benchmark-compare=baseline --benchmark-compare-fail=mean:20%
"""

import numpy as np
import pytest
from compas.datastructures import Mesh
from compas.geometry import Sphere

from compas_slicer._numpy_ops import (
    batch_closest_points,
    edge_gradient_from_vertex_gradient,
    face_gradient_from_scalar_field,
    min_distances_to_set,
    per_vertex_divergence,
    vectorized_distances,
    vertex_gradient_from_face_gradient,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def small_mesh():
    """Small mesh for quick tests (~200 faces)."""
    sphere = Sphere(5)
    mesh = Mesh.from_shape(sphere, u=10, v=10)
    mesh.quads_to_triangles()
    return mesh


@pytest.fixture
def medium_mesh():
    """Medium mesh for benchmarks (~2k faces)."""
    sphere = Sphere(5)
    mesh = Mesh.from_shape(sphere, u=32, v=32)
    mesh.quads_to_triangles()
    return mesh


@pytest.fixture
def large_mesh():
    """Large mesh for stress testing (~8k faces)."""
    sphere = Sphere(5)
    mesh = Mesh.from_shape(sphere, u=64, v=64)
    mesh.quads_to_triangles()
    return mesh


def mesh_to_arrays(mesh):
    """Convert COMPAS mesh to numpy arrays."""
    V = np.array([mesh.vertex_coordinates(v) for v in mesh.vertices()], dtype=np.float64)
    F = np.array([mesh.face_vertices(f) for f in mesh.faces()], dtype=np.intp)
    edges = np.array(list(mesh.edges()), dtype=np.intp)
    face_normals = np.array([mesh.face_normal(f) for f in mesh.faces()], dtype=np.float64)
    face_areas = np.array([mesh.face_area(f) for f in mesh.faces()], dtype=np.float64)
    return V, F, edges, face_normals, face_areas


# =============================================================================
# Correctness Tests (run always)
# =============================================================================


class TestNumpyOpsCorrectness:
    """Test that vectorized ops produce correct results."""

    def test_batch_closest_points(self):
        """Test KDTree-based closest point search."""
        query = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]], dtype=np.float64)
        target = np.array([[0.1, 0, 0], [1, 1, 1.1], [5, 5, 5]], dtype=np.float64)

        indices, distances = batch_closest_points(query, target)

        assert indices[0] == 0  # closest to [0.1, 0, 0]
        assert indices[1] == 1  # closest to [1, 1, 1.1]
        assert distances[0] == pytest.approx(0.1, abs=1e-6)

    def test_vectorized_distances(self):
        """Test distance matrix computation."""
        p1 = np.array([[0, 0, 0], [1, 0, 0]], dtype=np.float64)
        p2 = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64)

        dists = vectorized_distances(p1, p2)

        assert dists.shape == (2, 3)
        assert dists[0, 0] == pytest.approx(0.0)
        assert dists[0, 1] == pytest.approx(1.0)
        assert dists[1, 0] == pytest.approx(1.0)

    def test_vertex_gradient_from_face_gradient(self, small_mesh):
        """Test vertex gradient computation."""
        V, F, _, _, face_areas = mesh_to_arrays(small_mesh)

        # Create simple face gradients (pointing up)
        face_gradient = np.zeros((len(F), 3), dtype=np.float64)
        face_gradient[:, 2] = 1.0  # all gradients point up

        result = vertex_gradient_from_face_gradient(V, F, face_gradient, face_areas)

        assert result.shape == (len(V), 3)
        # All vertex gradients should point up (z-component positive)
        assert np.all(result[:, 2] > 0)

    def test_edge_gradient_from_vertex_gradient(self, small_mesh):
        """Test edge gradient computation."""
        V, F, edges, _, _ = mesh_to_arrays(small_mesh)

        # Create vertex gradients
        vertex_gradient = np.ones((len(V), 3), dtype=np.float64)

        result = edge_gradient_from_vertex_gradient(edges, vertex_gradient)

        assert result.shape == (len(edges), 3)
        # Each edge gradient should be sum of two vertex gradients = [2, 2, 2]
        np.testing.assert_array_almost_equal(result, np.full_like(result, 2.0))

    def test_face_gradient_from_scalar_field(self, small_mesh):
        """Test face gradient from scalar field."""
        V, F, _, face_normals, face_areas = mesh_to_arrays(small_mesh)

        # Use z-coordinate as scalar field (gradient should point in z)
        scalar_field = V[:, 2].copy()

        result = face_gradient_from_scalar_field(V, F, scalar_field, face_normals, face_areas)

        assert result.shape == (len(F), 3)
        # Gradient of z should have significant z-component
        assert np.mean(np.abs(result[:, 2])) > 0

    def test_per_vertex_divergence(self, small_mesh):
        """Test divergence computation."""
        V, F, _, _, _ = mesh_to_arrays(small_mesh)

        # Create uniform gradient field
        X = np.ones((len(F), 3), dtype=np.float64)
        cotans = np.ones((len(F), 3), dtype=np.float64) * 0.5

        result = per_vertex_divergence(V, F, X, cotans)

        assert result.shape == (len(V),)
        # Result should be finite
        assert np.all(np.isfinite(result))


# =============================================================================
# Benchmark Tests
# =============================================================================


class TestBenchmarkDistances:
    """Benchmark distance computations."""

    def test_batch_closest_1k_points(self, benchmark):
        """Benchmark: find closest points for 1k queries in 1k targets."""
        np.random.seed(42)
        query = np.random.rand(1000, 3).astype(np.float64)
        target = np.random.rand(1000, 3).astype(np.float64)

        result = benchmark(batch_closest_points, query, target)

        assert len(result[0]) == 1000

    def test_min_distances_1k_points(self, benchmark):
        """Benchmark: minimum distances for 1k points."""
        np.random.seed(42)
        query = np.random.rand(1000, 3).astype(np.float64)
        target = np.random.rand(1000, 3).astype(np.float64)

        result = benchmark(min_distances_to_set, query, target)

        assert len(result) == 1000

    def test_distance_matrix_500x500(self, benchmark):
        """Benchmark: full distance matrix 500x500."""
        np.random.seed(42)
        p1 = np.random.rand(500, 3).astype(np.float64)
        p2 = np.random.rand(500, 3).astype(np.float64)

        result = benchmark(vectorized_distances, p1, p2)

        assert result.shape == (500, 500)


class TestBenchmarkGradients:
    """Benchmark gradient computations."""

    def test_vertex_gradient_medium_mesh(self, benchmark, medium_mesh):
        """Benchmark: vertex gradient on medium mesh."""
        V, F, _, _, face_areas = mesh_to_arrays(medium_mesh)
        face_gradient = np.random.rand(len(F), 3).astype(np.float64)

        result = benchmark(vertex_gradient_from_face_gradient, V, F, face_gradient, face_areas)

        assert result.shape == (len(V), 3)

    def test_face_gradient_medium_mesh(self, benchmark, medium_mesh):
        """Benchmark: face gradient from scalar field on medium mesh."""
        V, F, _, face_normals, face_areas = mesh_to_arrays(medium_mesh)
        scalar_field = V[:, 2].copy()

        result = benchmark(face_gradient_from_scalar_field, V, F, scalar_field, face_normals, face_areas)

        assert result.shape == (len(F), 3)

    def test_divergence_medium_mesh(self, benchmark, medium_mesh):
        """Benchmark: divergence on medium mesh."""
        V, F, _, _, _ = mesh_to_arrays(medium_mesh)
        X = np.random.rand(len(F), 3).astype(np.float64)
        cotans = np.random.rand(len(F), 3).astype(np.float64)

        result = benchmark(per_vertex_divergence, V, F, X, cotans)

        assert result.shape == (len(V),)


class TestBenchmarkLargeMesh:
    """Stress tests on large meshes."""

    def test_vertex_gradient_large_mesh(self, benchmark, large_mesh):
        """Benchmark: vertex gradient on large mesh (~8k faces)."""
        V, F, _, _, face_areas = mesh_to_arrays(large_mesh)
        face_gradient = np.random.rand(len(F), 3).astype(np.float64)

        result = benchmark(vertex_gradient_from_face_gradient, V, F, face_gradient, face_areas)

        assert result.shape[0] == len(V)

    def test_batch_closest_5k_points(self, benchmark):
        """Benchmark: closest points for 5k queries."""
        np.random.seed(42)
        query = np.random.rand(5000, 3).astype(np.float64)
        target = np.random.rand(5000, 3).astype(np.float64)

        result = benchmark(batch_closest_points, query, target)

        assert len(result[0]) == 5000


# =============================================================================
# Regression Guards
# =============================================================================


class TestPerformanceRegression:
    """Tests that fail if performance regresses significantly.

    These use explicit timing assertions as a fallback when
    pytest-benchmark comparison is not available.
    """

    def test_batch_closest_should_be_fast(self):
        """Closest point search for 1k points should complete in < 50ms."""
        import time

        np.random.seed(42)
        query = np.random.rand(1000, 3).astype(np.float64)
        target = np.random.rand(1000, 3).astype(np.float64)

        start = time.perf_counter()
        for _ in range(10):
            batch_closest_points(query, target)
        elapsed = (time.perf_counter() - start) / 10

        assert elapsed < 0.05, f"batch_closest_points too slow: {elapsed * 1000:.1f}ms"

    def test_vertex_gradient_should_be_fast(self, medium_mesh):
        """Vertex gradient on 2k face mesh should complete in < 20ms."""
        import time

        V, F, _, _, face_areas = mesh_to_arrays(medium_mesh)
        face_gradient = np.random.rand(len(F), 3).astype(np.float64)

        start = time.perf_counter()
        for _ in range(10):
            vertex_gradient_from_face_gradient(V, F, face_gradient, face_areas)
        elapsed = (time.perf_counter() - start) / 10

        assert elapsed < 0.02, f"vertex_gradient too slow: {elapsed * 1000:.1f}ms"
