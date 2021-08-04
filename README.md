# compas_slicer

[![build](https://github.com/compas-dev/compas_slicer/workflows/build/badge.svg)](https://github.com/compas-dev/compas_slicer/actions)
[![GitHub - License](https://img.shields.io/github/license/compas-dev/compas_slicer.svg)](https://github.com/compas-dev/compas_slicer/blob/master/LICENSE) 
[![PyPI - Latest Release](https://img.shields.io/pypi/v/COMPAS-SLICER.svg)](https://pypi.python.org/project/COMPAS-SLICER)

Slicing package for FDM 3D Printing with COMPAS.


## Main features

* Planar slicing (default method, and method based on Cgal library)
* Curved slicing (interpolation of boundaries, UV slicing, scalar field slicing)
* Generation of fabrication-related information
* Export print data to Json and gcode formats

## Getting started

### Step 1: Installation

The recommended way to install `compas_slicer` is with [conda](https://conda.io/docs/).
For example, create an environment named ``my-project`` (or replace with your own environment name) and install as follows:

    conda config --add channels conda-forge
    conda create -n my-project compas_slicer

### Step 2: Optional installation steps

#### COMPAS Viewers

Follow the instructions to install `compas_view2` (https://github.com/compas-dev/compas_view2).

#### COMPAS CGAL

    conda install -n my-project compas_cgal

#### Grasshopper

The Grasshopper components are automatically installed with the `compas_rhino` installation, e.g.:

    conda activate my-project
    python -m compas_rhino.install -v 6.0

### Step 3. Test if the library works

Activate your environment and run the following command:

    conda activate my-project
    python -m compas_slicer

Enjoy!

## Troubleshooting

See here: https://compas.dev/compas_slicer/installation.html#troubleshooting-1

## Contributions

Before contributing code:

- Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

- Make sure all tests pass:
```bash
invoke test
```

- Make sure you pass flake8 tests. (hint: This is the most annoying part of the process)
```bash
invoke lint
```

- Add an example on the examples folder that uses the new functionality. Run the example and make sure it works smoothly. 

- Create a pull request for the master branch, where you explain in detail what you fixed. When you create a pull request, there is an automatic action that runs the tests for your code again on the server.
Make sure the pull request passes the automatic tests as well. If not, then inspect the result, find what went wrong, fix it, and push again the result on your branch. The action will run again automatically on the open pull request.


## Authors

* Ioanna Mitropoulou <<mitropoulou@arch.ethz.ch>> [@ioannaMitropoulou](https://github.com/ioannaMitropoulou)
* Joris Burger <<burger@arch.ethz.ch>> [@joburger](https://github.com/joburger)
* Andrei Jipa <<jipa@arch.ethz.ch>> [@stratocaster](https://github.com/stratocaster)