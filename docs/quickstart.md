# Quick Start

Get started with COMPAS Slicer in under 5 minutes.

## Basic Workflow

COMPAS Slicer follows a simple pipeline:

```mermaid
graph LR
    A[Load Mesh] --> B[Slice]
    B --> C[Post-process]
    C --> D[Print Organization]
    D --> E[Export]
```

## Minimal Example

```python
from pathlib import Path
from compas.datastructures import Mesh
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.print_organization import PlanarPrintOrganizer

# Load a mesh
mesh = Mesh.from_obj("model.obj")

# Slice with 2mm layer height
slicer = PlanarSlicer(mesh, layer_height=2.0)
slicer.slice_model()

# Create printpoints
organizer = PlanarPrintOrganizer(slicer)
organizer.create_printpoints()

# Export
organizer.printout_info()
```

## Complete Example with G-code

```python
from pathlib import Path
from compas.datastructures import Mesh
from compas.geometry import Point

from compas_slicer.slicers import PlanarSlicer
from compas_slicer.pre_processing import move_mesh_to_point
from compas_slicer.post_processing import generate_brim, simplify_paths_rdp
from compas_slicer.print_organization import PlanarPrintOrganizer, set_extruder_toggle
from compas_slicer.print_organization import create_gcode_text
from compas_slicer.config import GcodeConfig

# Load and position mesh
mesh = Mesh.from_obj("model.obj")
move_mesh_to_point(mesh, Point(100, 100, 0))

# Slice
slicer = PlanarSlicer(mesh, layer_height=0.2)
slicer.slice_model()

# Post-processing
generate_brim(slicer, layer_width=0.4, number_of_brim_offsets=3)
simplify_paths_rdp(slicer, threshold=0.1)

# Print organization
organizer = PlanarPrintOrganizer(slicer)
organizer.create_printpoints()
set_extruder_toggle(organizer, slicer)

# Generate G-code
gcode = create_gcode_text(organizer, GcodeConfig())
Path("output.gcode").write_text(gcode)
```

## Key Concepts

### Slicers

| Slicer | Use Case |
|--------|----------|
| `PlanarSlicer` | Standard horizontal slicing |
| `InterpolationSlicer` | Curved/non-planar slicing |
| `ScalarFieldSlicer` | Slicing along scalar field contours |

### Post-processing

- `simplify_paths_rdp()` - Reduce point count using RDP algorithm
- `generate_brim()` - Add adhesion brim
- `generate_raft()` - Add raft layers
- `seams_align()` - Align layer start points

### Print Organization

- `PlanarPrintOrganizer` - For planar slicing
- `InterpolationPrintOrganizer` - For curved slicing

## Next Steps

- [:material-book-open-variant: Tutorials](tutorials/index.md) - Learn the fundamentals
- [:material-code-tags: Examples](examples/index.md) - See complete workflows
- [:material-api: API Reference](api/index.md) - Detailed documentation
