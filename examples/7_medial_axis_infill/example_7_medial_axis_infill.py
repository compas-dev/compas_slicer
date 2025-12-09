"""Example: Medial Axis Infill Generation

This example demonstrates how to generate medial axis based infill
paths using CGAL's straight skeleton.

The medial axis naturally follows the centerlines of the geometry,
producing adaptive infill that handles thin walls and complex shapes.
"""
import logging
import os
import time

from compas.datastructures import Mesh

from compas_slicer.post_processing import generate_medial_axis_infill
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.utilities import save_to_json
from compas_slicer.visualization import should_visualize, visualize_slicer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("logger")


def main(visualize: bool = False):
    start_time = time.time()

    # Paths
    DATA = os.path.join(os.path.dirname(__file__), "data")
    OUTPUT = os.path.join(DATA, "output")
    os.makedirs(OUTPUT, exist_ok=True)

    # Load mesh - use the vase from example 1
    mesh_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "1_planar_slicing_simple",
        "data",
        "simple_vase_open_low_res.obj",
    )
    mesh = Mesh.from_obj(mesh_path)

    # Slice the mesh
    logger.info("Slicing mesh...")
    slicer = PlanarSlicer(mesh, slicer_type="cgal", layer_height=2.0)
    slicer.slice_model()

    # Simplify paths first (optional but recommended)
    simplify_paths_rdp(slicer, threshold=0.5)

    # Count paths before infill
    paths_before = sum(len(layer.paths) for layer in slicer.layers)
    logger.info(f"Paths before infill: {paths_before}")

    # Generate medial axis infill
    logger.info("Generating medial axis infill...")
    generate_medial_axis_infill(
        slicer,
        min_length=2.0,        # Skip very short skeleton edges
        include_bisectors=True  # Include bisectors connecting skeleton to boundary
    )

    # Count paths after infill
    paths_after = sum(len(layer.paths) for layer in slicer.layers)
    logger.info(f"Paths after infill: {paths_after}")
    logger.info(f"Infill paths added: {paths_after - paths_before}")

    # Save results
    slicer.printout_info()
    save_to_json(slicer.to_data(), OUTPUT, "medial_axis_slicer.json")

    end_time = time.time()
    logger.info(f"Total time: {end_time - start_time:.2f} seconds")

    if visualize:
        visualize_slicer(slicer, mesh)


if __name__ == "__main__":
    main(visualize=should_visualize())
