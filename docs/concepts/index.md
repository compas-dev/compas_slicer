# Concepts

Understanding the theory and architecture behind COMPAS Slicer.

## Overview

These guides explain *how* COMPAS Slicer works - the data structures, algorithms, and design decisions that power the library.

<div class="grid cards" markdown>

-   :material-sitemap:{ .lg .middle } **Architecture**

    ---

    Core data structures and pipeline flow - from mesh to G-code.

    [:octicons-arrow-right-24: Architecture](architecture.md)

-   :material-layers-triple:{ .lg .middle } **Slicing Algorithms**

    ---

    How planar, curved, and scalar field slicing work under the hood.

    [:octicons-arrow-right-24: Slicing Algorithms](slicing-algorithms.md)

-   :material-printer-3d-nozzle:{ .lg .middle } **Print Organization**

    ---

    Transforming geometry into fabrication-ready toolpaths.

    [:octicons-arrow-right-24: Print Organization](print-organization.md)

</div>

## Quick Reference

### The Pipeline

```
Mesh → Slicer → Layers/Paths → PrintOrganizer → PrintPoints → Output
```

### Key Classes

| Class | Purpose |
|-------|---------|
| `Layer` | One slice containing paths |
| `Path` | Single contour (closed or open) |
| `PrintPoint` | Point with fabrication data |
| `PlanarSlicer` | Horizontal plane slicing |
| `InterpolationSlicer` | Curved slicing between boundaries |
| `PlanarPrintOrganizer` | Generate printpoints from planar paths |

### Typical Workflow

```python
from compas.datastructures import Mesh
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.print_organization import PlanarPrintOrganizer

# 1. Load
mesh = Mesh.from_obj("model.obj")

# 2. Slice
slicer = PlanarSlicer(mesh, layer_height=0.4)
slicer.generate_paths()

# 3. Organize
organizer = PlanarPrintOrganizer(slicer)
organizer.create_printpoints()

# 4. Export
gcode = organizer.output_gcode()
```
