# G-code Generation

Export toolpaths to G-code for desktop 3D printers.

## Key Features

- `create_gcode_text()` - Generate G-code from printpoints
- `GcodeConfig` - Configure printer parameters (temps, speeds, retraction)
- Purge line, heating sequence, shutdown sequence
- Volumetric extrusion calculation

## Source

:material-github: [`examples/4_gcode_generation/`](https://github.com/compas-dev/compas_slicer/tree/master/examples/4_gcode_generation)

```bash
python examples/4_gcode_generation/example_4_gcode.py
```

Output: `examples/4_gcode_generation/data/output/output.gcode`
