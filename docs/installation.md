# Installation

COMPAS Slicer can be installed on Windows, macOS, and Linux.

## Requirements

- Python 3.9 or higher
- [COMPAS](https://compas.dev/) >= 2.15
- [compas_cgal](https://github.com/compas-dev/compas_cgal) >= 0.9

## Quick Install

=== "pip"

    ```bash
    pip install compas_slicer
    ```

=== "conda"

    ```bash
    conda install -c conda-forge compas_slicer
    ```

## Development Install

To install from source for development:

```bash
# Clone the repository
git clone https://github.com/compas-dev/compas_slicer.git
cd compas_slicer

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Verify Installation

Test that the installation works:

```bash
python -c "import compas_slicer; print(compas_slicer.__version__)"
```

## Grasshopper Integration

To use COMPAS Slicer in Rhino/Grasshopper:

```bash
python -m compas_rhino.install -v 8.0
```

!!! tip
    Replace `8.0` with your Rhino version (e.g., `7.0` for Rhino 7).

## Troubleshooting

### Grasshopper components not working

If the Grasshopper components don't load after installation, manually add the path in Rhino:

1. In Rhino, type `EditPythonScript`
2. Go to **Tools > Options > Add to search path**
3. Add: `<path>/compas_slicer/src/grasshopper_visualization`

### Microsoft Visual C++ Build Tools (Windows)

If you see:

```
error: Microsoft Visual C++ 14.0 or greater is required
```

Install the [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

### CGAL Issues

COMPAS Slicer requires `compas_cgal`. If you have issues:

```bash
conda install -c conda-forge compas_cgal
```

## Bug Reports

When [reporting a bug](https://github.com/compas-dev/compas_slicer/issues), please include:

- Operating system and version
- Python version
- COMPAS Slicer version (`python -c "import compas_slicer; print(compas_slicer.__version__)"`)
- Complete error traceback
- Steps to reproduce
