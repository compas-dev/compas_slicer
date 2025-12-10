# Planar Slicing

Basic horizontal slicing workflow with brim, raft, and seam alignment.

![Brim comparison](figures/01_brim.jpg)
*Left: Without brim. Right: With brim*

## Key Features

- `PlanarSlicer` - CGAL-based mesh-plane intersection
- `generate_brim()` - Bed adhesion
- `generate_raft()` - Support structure
- `simplify_paths_rdp()` - Point reduction
- `seams_align()` / `seams_smooth()` - Layer transition control

## Source

:material-github: [`examples/1_planar_slicing_simple/`](https://github.com/compas-dev/compas_slicer/tree/master/examples/1_planar_slicing_simple)

```bash
python examples/1_planar_slicing_simple/example_1_planar_slicing_simple.py
```
