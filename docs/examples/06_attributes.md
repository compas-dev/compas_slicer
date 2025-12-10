# Attribute Transfer

Transfer mesh attributes (overhang, normals, colors) to printpoints.

## Key Features

- `transfer_mesh_attributes_to_printpoints()` - Project attributes from mesh to toolpath
- Supports face attributes (boolean, float, text)
- Supports vertex attributes (interpolated via barycentric coordinates)
- Useful for variable printing parameters based on geometry

## Source

:material-github: [`examples/6_attributes_transfer/`](https://github.com/compas-dev/compas_slicer/tree/master/examples/6_attributes_transfer)

```bash
python examples/6_attributes_transfer/example_6_attributes_transfer.py
```
