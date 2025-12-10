# Examples

Complete working examples demonstrating COMPAS Slicer capabilities.

All examples are available in the [`examples/`](https://github.com/compas-dev/compas_slicer/tree/master/examples) folder of the repository.

<div class="grid cards" markdown>

-   :material-layers-outline:{ .lg .middle } **Planar Slicing**

    ---

    Basic horizontal slicing workflow with brim, raft, and seam alignment

    [:octicons-arrow-right-24: Example](01_planar_slicing.md)

-   :material-sine-wave:{ .lg .middle } **Curved Slicing**

    ---

    Non-planar slicing using interpolation between boundary curves

    [:octicons-arrow-right-24: Example](02_curved_slicing.md)

-   :material-sort-ascending:{ .lg .middle } **Vertical Sorting**

    ---

    Organize branching paths into vertical layers for efficient printing

    [:octicons-arrow-right-24: Example](03_vertical_sorting.md)

-   :material-file-code-outline:{ .lg .middle } **G-code Generation**

    ---

    Export toolpaths to G-code for desktop 3D printers

    [:octicons-arrow-right-24: Example](04_gcode.md)

-   :material-gradient-vertical:{ .lg .middle } **Scalar Field Slicing**

    ---

    Slice along custom scalar field contours

    [:octicons-arrow-right-24: Example](05_scalar_field.md)

-   :material-transfer:{ .lg .middle } **Attribute Transfer**

    ---

    Transfer mesh attributes (colors, normals) to printpoints

    [:octicons-arrow-right-24: Example](06_attributes.md)

</div>

## Running Examples

```bash
# Clone the repository
git clone https://github.com/compas-dev/compas_slicer.git
cd compas_slicer

# Install
pip install -e .

# Run an example
python examples/1_planar_slicing_simple/example_1_planar_slicing_simple.py
```

Output files are saved to `examples/<example>/data/output/`.
