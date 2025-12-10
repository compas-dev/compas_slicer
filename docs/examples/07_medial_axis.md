# Medial Axis Infill

This example demonstrates generating infill paths using the medial axis (straight skeleton) of each layer contour - a geometry-aware approach that adapts to the shape.

## What You'll Learn

- Generating medial axis infill using CGAL's straight skeleton
- Controlling infill density with `min_length`
- Understanding bisector vs inner_bisector edges
- When to use medial axis vs traditional infill patterns

## Why Medial Axis Infill?

Traditional infill patterns (grid, honeycomb, gyroid) ignore the geometry - they apply the same pattern everywhere. Medial axis infill follows the natural centerlines of the shape:

```
Traditional Grid:              Medial Axis:
  ┌─────────────┐               ┌─────────────┐
  │ │ │ │ │ │ │ │               │      │      │
  │─┼─┼─┼─┼─┼─┼─│               │   ╲  │  ╱   │
  │ │ │ │ │ │ │ │               │    ╲ │ ╱    │
  │─┼─┼─┼─┼─┼─┼─│               │─────╳│╳─────│
  │ │ │ │ │ │ │ │               │    ╱ │ ╲    │
  └─────────────┘               └─────────────┘
   (ignores shape)              (follows geometry)
```

Benefits:

- **Adaptive density**: Naturally denser in thin walls, sparser in open areas
- **Follows geometry**: Infill aligns with the shape's structure
- **Handles complexity**: Works well with irregular shapes, holes, and thin features

## The Pipeline

```mermaid
flowchart LR
    A[Slice Mesh] --> B[For Each Layer]
    B --> C[Compute Straight Skeleton]
    C --> D[Extract Skeleton Edges]
    D --> E[Filter by Length]
    E --> F[Add as Infill Paths]
```

## Step-by-Step Walkthrough

### 1. Load and Slice

```python
from pathlib import Path
from compas.datastructures import Mesh
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import simplify_paths_rdp

mesh = Mesh.from_obj(DATA_PATH / 'simple_vase_open_low_res.obj')

slicer = PlanarSlicer(mesh, layer_height=2.0)
slicer.slice_model()

# Simplify paths first (recommended)
simplify_paths_rdp(slicer, threshold=0.5)
```

### 2. Generate Medial Axis Infill

```python
from compas_slicer.post_processing import generate_medial_axis_infill

generate_medial_axis_infill(
    slicer,
    min_length=2.0,        # Skip edges shorter than 2mm
    include_bisectors=True  # Include spokes to boundary
)
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `min_length` | Minimum skeleton edge length to include (mm) |
| `include_bisectors` | Include edges connecting skeleton to boundary |

### 3. Continue with Print Organization

```python
from compas_slicer.print_organization import PlanarPrintOrganizer

print_organizer = PlanarPrintOrganizer(slicer)
print_organizer.create_printpoints()
# ... rest of print organization
```

## How It Works

### The Straight Skeleton

The straight skeleton is computed by "shrinking" the polygon inward at constant speed. Where the shrinking boundary meets itself, skeleton edges form:

```
Original polygon:           After shrinking:
    ┌───────┐                  ┌───────┐
    │       │                  │╲     ╱│
    │       │        →         │ ╲   ╱ │
    │       │                  │  ╲ ╱  │
    └───────┘                  └───╳───┘
                                  skeleton
```

CGAL's `interior_straight_skeleton()` returns a graph with:

- **Boundary edges**: Original polygon edges
- **Inner bisector edges**: Internal skeleton (medial axis)
- **Bisector edges**: Spokes connecting skeleton to boundary vertices

### Edge Types

```
      ●─────────────●
     ╱│   boundary  │╲
    ╱ │             │ ╲
   ╱  │   inner_    │  ╲
  ●───●   bisector  ●───●
   ╲  │             │  ╱
    ╲ │   bisector  │ ╱
     ╲│   (spoke)   │╱
      ●─────────────●
```

| Edge Type | Description | Use Case |
|-----------|-------------|----------|
| `boundary` | Original polygon edges | Skipped (already in perimeter) |
| `inner_bisector` | Internal skeleton | Always included |
| `bisector` | Skeleton to boundary | Optional (include_bisectors) |

## Tuning Parameters

### min_length

Controls infill density:

| Value | Effect |
|-------|--------|
| Small (1-2mm) | Dense infill, more paths |
| Medium (5-10mm) | Moderate infill |
| Large (20mm+) | Sparse, only main skeleton |

### include_bisectors

```
include_bisectors=True:     include_bisectors=False:
    ┌───────┐                   ┌───────┐
    │╲     ╱│                   │       │
    │ ╲   ╱ │                   │   │   │
    │  ╲ ╱  │                   │   │   │
    │───╳───│                   │───┼───│
    │  ╱ ╲  │                   │   │   │
    │ ╱   ╲ │                   │       │
    └───────┘                   └───────┘
  (more support)              (cleaner look)
```

## Complete Code

```python
--8<-- "examples/7_medial_axis_infill/example_7_medial_axis_infill.py"
```

## Running the Example

```bash
cd examples/7_medial_axis_infill
python example_7_medial_axis_infill.py
```

With visualization:

```bash
python example_7_medial_axis_infill.py --visualize
```

## When to Use Medial Axis Infill

**Good for:**

- Irregular shapes with varying wall thickness
- Organic geometries (vases, sculptures)
- Parts with thin features that need internal support
- Single-wall prints that need occasional bridging

**Not ideal for:**

- Regular mechanical parts (use grid/honeycomb)
- High infill density requirements (use traditional patterns)
- Parts needing uniform strength in all directions

## Comparison with Traditional Infill

| Aspect | Medial Axis | Grid/Honeycomb |
|--------|-------------|----------------|
| Adapts to geometry | Yes | No |
| Density control | Via min_length | Via infill % |
| Thin wall support | Excellent | May miss thin areas |
| Computation | Per-layer skeleton | Simple patterns |
| Uniform strength | No (follows shape) | Yes |

## Key Takeaways

1. **Geometry-aware**: Infill follows the natural structure of the shape
2. **Adaptive density**: Automatically denser where needed
3. **CGAL powered**: Uses robust straight skeleton computation
4. **Tunable**: Control density with `min_length`, coverage with `include_bisectors`

## Next Steps

- [Planar Slicing](01_planar_slicing.md) - Basic slicing workflow
- [Print Organization](../concepts/print-organization.md) - Fabrication parameters
- [API Reference](../api/post_processing.md) - Full function documentation
