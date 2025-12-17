# compas_slicer

[![build](https://github.com/compas-dev/compas_slicer/workflows/build/badge.svg)](https://github.com/compas-dev/compas_slicer/actions)
[![GitHub - License](https://img.shields.io/github/license/compas-dev/compas_slicer.svg)](https://github.com/compas-dev/compas_slicer/blob/master/LICENSE) 
[![PyPI - Latest Release](https://img.shields.io/pypi/v/COMPAS-SLICER.svg)](https://pypi.python.org/project/COMPAS-SLICER)
[![DOI](https://zenodo.org/badge/226364384.svg)](https://zenodo.org/badge/latestdoi/226364384)

Python slicing package for FDM 3D Printing based on the [COMPAS](https://block.arch.ethz.ch/brg/tools/compas-computational-framework-for-collaboration-and-research-in-architecture-structures-and-digital-fabrication) framework.

## What's New in 0.7.0

Major refactor with ~10x performance improvement:

* **CGAL backend** - pure python replaced with `compas_cgal`, `igl` dependency removed
* **Modern docs** - migrated to `mkdocs` with full API reference
* **COMPAS 2.x** - full compatibility with new serialization API
* **Visualization** - examples now use `compas_viewer`
* **Vectorized ops** - hot loops rewritten with `numpy` (see `_numpy_ops.py`)
* **Type hints** - throughout codebase
* **Medial axis infill** - via CGAL straight skeleton

See [CHANGELOG.md](CHANGELOG.md) for details.

## Getting started

You can find tutorials and documentation of the project in the [compas_slicer page](https://compas.dev/compas_slicer/latest/)

For installation instructions, see here: [installation](https://compas.dev/compas_slicer/latest/installation.html)

For troubleshooting, see here: [troubleshooting](https://compas.dev/compas_slicer/installation.html#troubleshooting-1)

## Main features

* Planar slicing (default method, and method based on Cgal library)
* Curved slicing (interpolation of boundaries, UV slicing, scalar field slicing)
* Generation of fabrication-related information
* Export print data to Json and gcode format
* Visualization of results in grasshopper

## Authors

* Ioanna Mitropoulou [@ioannaMitropoulou](https://github.com/ioannaMitropoulou)
* Joris Burger [@joburger](https://github.com/joburger)
* Andrei Jipa [@stratocaster](https://github.com/stratocaster)
* Jelle Feringa [@jf---](https://github.com/jf---)


