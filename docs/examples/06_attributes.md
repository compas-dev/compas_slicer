# Attribute Transfer

This example demonstrates how to transfer mesh attributes (overhang angles, normals, colors, custom data) to printpoints for variable printing parameters based on geometry.

## What You'll Learn

- Adding face and vertex attributes to meshes
- Transferring attributes from mesh to printpoints
- Using transferred data for variable printing
- Understanding face vs vertex attribute interpolation

## Why Attribute Transfer?

Different parts of a model may need different printing parameters:

- **Overhangs** need slower speeds and more cooling
- **Visible surfaces** need finer resolution
- **Structural areas** need higher infill
- **Colored regions** need different materials

Attribute transfer lets you encode this information on the mesh and automatically apply it to toolpaths.

## The Pipeline

```mermaid
flowchart LR
    A[Mesh] --> B[Add Attributes]
    B --> C[Slice]
    C --> D[Create PrintPoints]
    D --> E[Transfer Attributes]
    E --> F[Variable Parameters]
```

## Step-by-Step Walkthrough

### 1. Load Mesh

```python
from pathlib import Path
from compas.datastructures import Mesh

mesh = Mesh.from_obj(DATA_PATH / 'distorted_v_closed_low_res.obj')
```

### 2. Add Face Attributes

Face attributes are values assigned to each face of the mesh. They can be any type: float, bool, string, list, etc.

#### Overhang Angle (Float)

Calculate how much each face is tilted from vertical:

```python
from compas.geometry import Vector

mesh.update_default_face_attributes({'overhang': 0.0})

for f_key, data in mesh.faces(data=True):
    face_normal = mesh.face_normal(f_key, unitized=True)
    # Dot product with up vector: 1 = horizontal face, 0 = vertical face
    data['overhang'] = Vector(0.0, 0.0, 1.0).dot(face_normal)
```

| Overhang Value | Meaning |
|----------------|---------|
| 1.0 | Horizontal (flat top) |
| 0.0 | Vertical (wall) |
| -1.0 | Horizontal facing down (overhang) |

#### Boolean Attribute

Check if face normal points toward positive Y:

```python
mesh.update_default_face_attributes({'positive_y_axis': False})

for f_key, data in mesh.faces(data=True):
    face_normal = mesh.face_normal(f_key, unitized=True)
    is_positive_y = Vector(0.0, 1.0, 0.0).dot(face_normal) > 0
    data['positive_y_axis'] = is_positive_y
```

### 3. Add Vertex Attributes

Vertex attributes must be numeric types that can be interpolated (float, numpy array).

#### Distance from Plane (Float)

```python
from compas.geometry import Point, Vector, distance_point_plane

mesh.update_default_vertex_attributes({'dist_from_plane': 0.0})

plane = (Point(0.0, 0.0, -30.0), Vector(0.0, 0.5, 0.5))

for v_key, data in mesh.vertices(data=True):
    v_coord = mesh.vertex_coordinates(v_key, axes='xyz')
    data['dist_from_plane'] = distance_point_plane(v_coord, plane)
```

#### Direction Vector (Array)

```python
import numpy as np
from compas.geometry import normalize_vector

mesh.update_default_vertex_attributes({'direction_to_pt': 0.0})

target_pt = Point(4.0, 1.0, 0.0)

for v_key, data in mesh.vertices(data=True):
    v_coord = mesh.vertex_coordinates(v_key, axes='xyz')
    direction = Vector.from_start_end(v_coord, target_pt)
    data['direction_to_pt'] = np.array(normalize_vector(direction))
```

### 4. Slice and Create PrintPoints

```python
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.print_organization import PlanarPrintOrganizer

slicer = PlanarSlicer(mesh, layer_height=5.0)
slicer.slice_model()
simplify_paths_rdp(slicer, threshold=1.0)

print_organizer = PlanarPrintOrganizer(slicer)
print_organizer.create_printpoints()
```

### 5. Transfer Attributes

```python
from compas_slicer.utilities.attributes_transfer import transfer_mesh_attributes_to_printpoints

transfer_mesh_attributes_to_printpoints(mesh, print_organizer.printpoints)
```

This function:

1. Finds which mesh face each printpoint lies on
2. For **face attributes**: Directly copies the value
3. For **vertex attributes**: Interpolates using barycentric coordinates

### 6. Access Transferred Attributes

```python
# Get all values of an attribute across all printpoints
overhangs = print_organizer.get_printpoints_attribute(attr_name='overhang')
positive_y = print_organizer.get_printpoints_attribute(attr_name='positive_y_axis')
distances = print_organizer.get_printpoints_attribute(attr_name='dist_from_plane')
directions = print_organizer.get_printpoints_attribute(attr_name='direction_to_pt')
```

Or access individual printpoint attributes:

```python
for ppt in print_organizer.printpoints_iterator():
    if ppt.attributes.get('overhang', 0) < 0:
        # This is an overhang - adjust printing parameters
        ppt.velocity = 20.0  # Slow down
```

## How Interpolation Works

### Face Attributes

Face attributes are discrete - each point on a face gets the same value:

```
Face A (overhang=0.8)    Face B (overhang=0.3)
      _____                  _____
     |  ●  |                |  ●  |
     |_____|                |_____|

   Point gets 0.8         Point gets 0.3
```

### Vertex Attributes

Vertex attributes are interpolated using barycentric coordinates:

```
        V1 (dist=10)
           ●
          /|\
         / | \
        /  ●P \      P is at barycentric coords (0.2, 0.3, 0.5)
       /   |   \     dist(P) = 0.2×10 + 0.3×5 + 0.5×2 = 4.5
      ●----+----●
    V2 (dist=5)  V3 (dist=2)
```

The interpolation formula:

$$\text{attr}(P) = \lambda_1 \cdot \text{attr}(V_1) + \lambda_2 \cdot \text{attr}(V_2) + \lambda_3 \cdot \text{attr}(V_3)$$

Where $\lambda_1 + \lambda_2 + \lambda_3 = 1$ are the barycentric coordinates.

## Practical Applications

### Variable Velocity by Overhang

Slow down on overhangs for better print quality:

```python
from compas_slicer.print_organization import set_linear_velocity_by_range

set_linear_velocity_by_range(
    print_organizer,
    param_func=lambda ppt: ppt.attributes.get('overhang', 0),
    parameter_range=[-1.0, 1.0],    # overhang range
    velocity_range=[15, 60],         # slow for overhangs, fast for flat
)
```

### Color-Based Material Selection

```python
# Assume 'color' attribute is 0 (white) or 1 (black)
for ppt in print_organizer.printpoints_iterator():
    if ppt.attributes.get('color', 0) > 0.5:
        ppt.extruder_id = 1  # Use second extruder
    else:
        ppt.extruder_id = 0
```

### Structural Reinforcement

```python
# Higher flow rate in structural regions
for ppt in print_organizer.printpoints_iterator():
    if ppt.attributes.get('is_structural', False):
        ppt.flowrate = 1.2  # 20% more material
```

## Attribute Type Requirements

| Attribute Location | Allowed Types | Interpolation |
|--------------------|---------------|---------------|
| Face | Any (float, bool, str, list, dict) | None (direct copy) |
| Vertex | Numeric only (float, np.array) | Barycentric |

!!! warning "Vertex Attribute Limitation"
    Vertex attributes must be numeric types that can be meaningfully multiplied by floats. Boolean or string vertex attributes will cause errors during interpolation.

## Complete Code

```python
--8<-- "examples/6_attributes_transfer/example_6_attributes_transfer.py"
```

## Running the Example

```bash
cd examples/6_attributes_transfer
python example_6_attributes_transfer.py
```

With visualization:

```bash
python example_6_attributes_transfer.py --visualize
```

## Output Files

| File | Description |
|------|-------------|
| `slicer_data.json` | Sliced geometry |
| `out_printpoints.json` | PrintPoints with attributes |
| `overhangs_list.json` | Overhang values per point |
| `positive_y_axis_list.json` | Boolean values per point |
| `dist_from_plane_list.json` | Distance values per point |
| `direction_to_pt_list.json` | Direction vectors per point |

## Key Takeaways

1. **Face vs vertex attributes**: Face attributes are discrete, vertex attributes are interpolated
2. **Numeric vertex attributes only**: Must be floats or arrays for barycentric interpolation
3. **Automatic transfer**: One function call transfers all mesh attributes to printpoints
4. **Variable parameters**: Use transferred attributes to drive printing parameters

## Next Steps

- [Print Organization](../concepts/print-organization.md) - More on fabrication parameters
- [Curved Slicing](02_curved_slicing.md) - Combine with non-planar techniques
- [API Reference](../api/utilities.md) - `transfer_mesh_attributes_to_printpoints` details
