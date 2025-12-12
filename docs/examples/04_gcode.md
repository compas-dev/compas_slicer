# G-code Generation

This example demonstrates exporting toolpaths to G-code for desktop FDM 3D printers like Prusa, Ender, or Ultimaker.

## What You'll Learn

- Configuring printer parameters with `GcodeConfig`
- Positioning mesh for delta vs cartesian printers
- Generating G-code from printpoints
- Understanding the G-code structure (header, purge, toolpath, footer)

## G-code Basics

G-code is the standard language for CNC machines and 3D printers. Each line is a command:

```gcode
G1 X100 Y50 Z0.2 E1.5 F3600  ; Move to X=100, Y=50, Z=0.2 while extruding 1.5mm at 3600mm/min
```

Common commands:

| Command | Description |
|---------|-------------|
| `G0` / `G1` | Linear move (G0 = rapid, G1 = controlled) |
| `G28` | Home axes |
| `G90` / `G91` | Absolute / relative positioning |
| `M104` / `M109` | Set extruder temp (no wait / wait) |
| `M140` / `M190` | Set bed temp (no wait / wait) |
| `M106` / `M107` | Fan on / off |

## The Pipeline

```mermaid
flowchart LR
    A[Slice Mesh] --> B[Create PrintPoints]
    B --> C[Configure GcodeConfig]
    C --> D[Generate G-code]
    D --> E[Save .gcode File]
```

## Step-by-Step Walkthrough

### 1. Setup and Configuration

```python
from pathlib import Path
from compas.datastructures import Mesh
from compas.geometry import Point
from compas_slicer.config import GcodeConfig
from compas_slicer.pre_processing import move_mesh_to_point

mesh = Mesh.from_obj(DATA_PATH / 'simple_vase_open_low_res.obj')

# Create G-code configuration
gcode_config = GcodeConfig()
```

### 2. Position Mesh for Printer Type

```python
if gcode_config.delta:
    # Delta printers: origin at center
    move_mesh_to_point(mesh, Point(0, 0, 0))
else:
    # Cartesian printers: center in build volume
    move_mesh_to_point(mesh, Point(
        gcode_config.print_volume_x / 2,
        gcode_config.print_volume_y / 2,
        0
    ))
```

!!! info "Delta vs Cartesian"
    - **Delta printers**: Circular build plate, origin at center (0, 0, 0)
    - **Cartesian printers**: Rectangular build plate, origin at corner (0, 0, 0)

### 3. Slice and Process

```python
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.post_processing import generate_brim, simplify_paths_rdp, seams_smooth

slicer = PlanarSlicer(mesh, layer_height=4.5)
slicer.slice_model()

generate_brim(slicer, layer_width=3.0, number_of_brim_offsets=4)
simplify_paths_rdp(slicer, threshold=0.6)
seams_smooth(slicer, smooth_distance=10)
```

### 4. Create PrintPoints

```python
from compas_slicer.print_organization import PlanarPrintOrganizer, set_extruder_toggle

print_organizer = PlanarPrintOrganizer(slicer)
print_organizer.create_printpoints()
set_extruder_toggle(print_organizer, slicer)
```

### 5. Generate and Save G-code

```python
from compas_slicer.utilities import save_to_text_file

gcode_text = print_organizer.output_gcode(gcode_config)
save_to_text_file(gcode_text, OUTPUT_PATH, 'my_gcode.gcode')
```

## GcodeConfig Parameters

The `GcodeConfig` dataclass controls all printer parameters:

### Hardware Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `nozzle_diameter` | 0.4 mm | Nozzle diameter |
| `filament_diameter` | 1.75 mm | Filament diameter (1.75 or 2.85) |
| `delta` | False | Delta printer flag |
| `print_volume` | (300, 300, 600) | Build volume (x, y, z) in mm |

### Temperature & Fan

| Parameter | Default | Description |
|-----------|---------|-------------|
| `extruder_temperature` | 200°C | Hotend temperature |
| `bed_temperature` | 60°C | Heated bed temperature |
| `fan_speed` | 255 | Part cooling fan (0-255) |
| `fan_start_z` | 0.0 mm | Height to enable fan |

### Extrusion

| Parameter | Default | Description |
|-----------|---------|-------------|
| `layer_width` | 0.6 mm | Extrusion width |
| `flowrate` | 1.0 | Flow multiplier |
| `flow_over` | 1.0 | Overextrusion factor near bed |
| `min_over_z` | 0.0 mm | Height for overextrusion |

### Motion

| Parameter | Default | Description |
|-----------|---------|-------------|
| `feedrate` | 3600 mm/min | Print speed (60 mm/s) |
| `feedrate_travel` | 4800 mm/min | Travel speed (80 mm/s) |
| `feedrate_low` | 1800 mm/min | First layer speed (30 mm/s) |
| `feedrate_retraction` | 2400 mm/min | Retraction speed |
| `acceleration` | 0 | Acceleration (0 = default) |
| `jerk` | 0 | Jerk (0 = default) |

### Retraction

| Parameter | Default | Description |
|-----------|---------|-------------|
| `z_hop` | 0.5 mm | Z lift during travel |
| `retraction_length` | 1.0 mm | Filament retraction distance |
| `retraction_min_travel` | 6.0 mm | Minimum travel to trigger retraction |

## Custom Configuration

Override defaults when creating the config:

```python
gcode_config = GcodeConfig(
    extruder_temperature=210,
    bed_temperature=65,
    feedrate=2400,  # 40 mm/s
    layer_width=0.45,
    retraction_length=0.8,
)
```

Or load from a TOML file using `PrintConfig`:

```python
from compas_slicer.config import PrintConfig

config = PrintConfig.from_toml("my_printer.toml")
gcode_config = config.gcode
```

## G-code Structure

The generated G-code has four sections:

### 1. Header
```gcode
;G-code generated by compas_slicer
T0                             ;select tool 0
G21                            ;metric units
G90                            ;absolute positioning
M140 S60                       ;set bed temp (no wait)
M104 S200                      ;set extruder temp (no wait)
M109 S200                      ;wait for extruder temp
M190 S60                       ;wait for bed temp
G28 X0 Y0                      ;home X and Y
G28 Z0                         ;home Z
```

### 2. Purge Line
```gcode
;Purge line
G1 Z0.2                        ;move to purge height
G1 X5 Y5                       ;move to purge start
G1 Y150 E3.5                   ;purge line 1
G1 X5.6                        ;step over
G1 Y5 E3.5                     ;purge line 2
G92 E0                         ;reset extruder position
```

### 3. Toolpath
```gcode
;Begin toolpath
G1 F1800                       ;slow feedrate for adhesion
G1 X50.000 Y30.000 Z0.200
G1 X51.234 Y30.567 E0.125
...
```

### 4. Footer
```gcode
;End of print
G1 E-1.0                       ;final retract
G1 Z10.000                     ;lift nozzle
G1 X0 Y0                       ;move to home
M104 S0                        ;extruder heater off
M140 S0                        ;bed heater off
M84                            ;motors off
```

## Volumetric Extrusion

The G-code generator calculates extrusion using volumetric math:

$$E = \frac{d \cdot h \cdot w}{\pi (D/2)^2} \cdot f$$

Where:

- $E$ = extrusion length (mm)
- $d$ = travel distance (mm)
- $h$ = layer height (mm)
- $w$ = path width (mm)
- $D$ = filament diameter (mm)
- $f$ = flow rate multiplier

This ensures correct material deposition regardless of layer height or path width.

## Complete Code

```python
--8<-- "examples/4_gcode_generation/example_4_gcode.py"
```

## Running the Example

```bash
cd examples/4_gcode_generation
python example_4_gcode.py
```

With visualization:

```bash
python example_4_gcode.py --visualize
```

Output: `examples/4_gcode_generation/data/output/my_gcode.gcode`

## Key Takeaways

1. **Configure for your printer**: Set temperatures, speeds, and retraction for your specific machine
2. **Position mesh correctly**: Delta vs cartesian printers have different origins
3. **Volumetric extrusion**: Automatically calculates correct E values
4. **Modular structure**: Header/purge/toolpath/footer makes debugging easier

## Next Steps

- [Scalar Field Slicing](05_scalar_field.md) - Custom slicing patterns
- [Print Organization](../concepts/print-organization.md) - More fabrication parameters
