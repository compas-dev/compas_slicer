# Planar Slicing

This example demonstrates the complete planar slicing workflow - from mesh to printpoints with brim, raft, and seam control.

![Brim comparison](figures/01_brim.jpg)
*Left: Without brim. Right: With brim for bed adhesion*

## What You'll Learn

- Loading and positioning a mesh
- Basic planar slicing with `PlanarSlicer`
- Adding brim and raft for bed adhesion
- Simplifying paths with RDP algorithm
- Controlling seam position and smoothness
- Creating printpoints with fabrication parameters

## The Pipeline

```mermaid
flowchart LR
    A[Load Mesh] --> B[Position at Origin]
    B --> C[Slice]
    C --> D[Add Brim/Raft]
    D --> E[Simplify Paths]
    E --> F[Align Seams]
    F --> G[Create PrintPoints]
    G --> H[Set Parameters]
    H --> I[Export JSON]
```

## Step-by-Step Walkthrough

### 1. Setup and Load Mesh

```python
from pathlib import Path
from compas.datastructures import Mesh
from compas.geometry import Point
from compas_slicer.pre_processing import move_mesh_to_point

# Load the mesh
mesh = Mesh.from_obj(Path("data/simple_vase_open_low_res.obj"))

# Move to origin (important for consistent slicing)
move_mesh_to_point(mesh, Point(0, 0, 0))
```

!!! tip "Why move to origin?"
    Moving the mesh ensures the first layer starts at Z=0, which is expected by most 3D printers and simplifies debugging.

### 2. Slice the Mesh

```python
from compas_slicer.slicers import PlanarSlicer

slicer = PlanarSlicer(mesh, layer_height=1.5)
slicer.slice_model()
```

This intersects the mesh with horizontal planes spaced 1.5mm apart using CGAL's robust mesh-plane intersection.

### 3. Align Seams

```python
from compas_slicer.post_processing import seams_align

seams_align(slicer, "next_path")
```

Seams are where each layer starts/ends. Without alignment, seams appear randomly, creating a visible vertical line. Options:

| Mode | Description |
|------|-------------|
| `"next_path"` | Align with next layer's closest point |
| `"x_axis"` | Align along X axis |
| `"y_axis"` | Align along Y axis |
| `"origin"` | Align toward origin |

### 4. Generate Brim

```python
from compas_slicer.post_processing import generate_brim

generate_brim(
    slicer,
    layer_width=3.0,           # Width of each brim line
    number_of_brim_offsets=4   # Number of concentric loops
)
```

A brim adds concentric loops around the first layer to improve bed adhesion. Unlike a raft, the brim is on the same layer as the print.

### 5. Generate Raft

```python
from compas_slicer.post_processing import generate_raft

generate_raft(
    slicer,
    raft_offset=20,            # Distance from model edge
    distance_between_paths=5,   # Spacing between raft lines
    direction="xy_diagonal",    # Line pattern direction
    raft_layers=1              # Number of raft layers
)
```

A raft creates a sacrificial base layer beneath the print. The model is printed on top of the raft.

!!! note
    Typically use brim OR raft, not both. This example shows both for demonstration.

### 6. Simplify Paths

```python
from compas_slicer.post_processing import simplify_paths_rdp

simplify_paths_rdp(slicer, threshold=0.6)
```

The Ramer-Douglas-Peucker algorithm removes points that don't contribute significantly to the path shape. A threshold of 0.6mm means points within 0.6mm of the simplified line are removed.

**Before:** 10,000 points → **After:** 2,000 points (faster printing, same quality)

### 7. Smooth Seams

```python
from compas_slicer.post_processing import seams_smooth

seams_smooth(slicer, smooth_distance=10)
```

Smooths the transition between layers by blending the path near the seam point over a 10mm distance.

### 8. Create PrintPoints

```python
from compas_slicer.print_organization import PlanarPrintOrganizer

print_organizer = PlanarPrintOrganizer(slicer)
print_organizer.create_printpoints(generate_mesh_normals=False)
```

This converts geometric points to `PrintPoint` objects with fabrication metadata.

### 9. Set Fabrication Parameters

```python
from compas_slicer.print_organization import (
    set_extruder_toggle,
    add_safety_printpoints,
    set_linear_velocity_constant,
)

# Enable/disable extrusion based on path structure
set_extruder_toggle(print_organizer, slicer)

# Add Z-hop between paths to avoid collisions
add_safety_printpoints(print_organizer, z_hop=10.0)

# Set constant print speed
set_linear_velocity_constant(print_organizer, v=25.0)
```

### 10. Export

```python
from compas_slicer.utilities import save_to_json

# Flat format
printpoints_data = print_organizer.output_printpoints_dict()
save_to_json(printpoints_data, OUTPUT_PATH, 'out_printpoints.json')

# Nested format (layer > path > point)
nested_data = print_organizer.output_nested_printpoints_dict()
save_to_json(nested_data, OUTPUT_PATH, 'out_printpoints_nested.json')
```

## Complete Code

```python
--8<-- "examples/1_planar_slicing_simple/example_1_planar_slicing_simple.py"
```

## Running the Example

```bash
cd examples/1_planar_slicing_simple
python example_1_planar_slicing_simple.py
```

Add `--visualize` flag to see the results:

```bash
python example_1_planar_slicing_simple.py --visualize
```

## Output Files

| File | Description |
|------|-------------|
| `slicer_data.json` | Raw slicer output (layers, paths) |
| `out_printpoints.json` | Flat list of printpoints |
| `out_printpoints_nested.json` | Nested structure by layer/path |

## Key Takeaways

1. **Order matters**: Brim/raft before simplification, seam alignment early
2. **Simplification saves time**: RDP can reduce points 5x with no quality loss
3. **Seam control is important**: Random seams create visible artifacts
4. **Safety moves prevent crashes**: Z-hop between paths avoids collisions

## Next Steps

- [Curved Slicing](02_curved_slicing.md) - Non-planar toolpaths
- [G-code Generation](04_gcode.md) - Export for 3D printers
- [Print Organization](../concepts/print-organization.md) - Deep dive into fabrication parameters
