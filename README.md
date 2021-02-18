# compas_slicer

[![build](https://github.com/compas-dev/compas_slicer/workflows/build/badge.svg)](https://github.com/compas-dev/compas_slicer/actions)
[![GitHub - License](https://img.shields.io/github/license/compas-dev/compas_slicer.svg)](https://github.com/compas-dev/compas_slicer/blob/master/LICENSE) 
[![PyPI - Latest Release](https://img.shields.io/pypi/v/COMPAS-SLICER.svg)](https://pypi.python.org/project/COMPAS-SLICER)

Slicing package for FDM 3D Printing with COMPAS.


Main features
-------------

* Planar slicing (default method, and method based on Cgal library)
* Curved slicing (interpolation of boundaries, UV slicing, scalar field slicing)
* Generation of fabrication-related information
* Export print data to Json and gcode formats

Getting started
------------

### Step 1: Install compas

- Create a new environment (you can replace 'compas_slicer' with your own environment name),
and install compas, compas_cgal, and libigl.

```bash
conda create -n compas_slicer python=3.7
conda activate compas_slicer
conda install COMPAS
conda install COMPAS compas_cgal
conda install -c conda-forge igl
```

### Step 2: Install compas_slicer

- Clone the repository and activate your environment.
```bash
git clone https://github.com/compas-dev/compas_slicer.git
conda activate compas_slicer
```
- Navigate to the folder where you cloned the compas_slicer repository and install compas_slicer using:
```bash
pip install -e .
```
- You should get the message 'Successfully installed compas-slicer' (amongst other packages)

### Step 3. Install compas_viewers (optional)

- Install compas_viewers (https://github.com/compas-dev/compas_viewers).

- Download the wheel file from here: https://www.lfd.uci.edu/~gohlke/pythonlibs/
To install on an existing environment with python=3.7, use:
```bash
conda activate <environment_name>
pip install PySide2 
pip install <path/to/file>/PyOpenGL‑3.1.5‑cp37‑cp37m‑win_amd64.whl
pip install <path/to/compas_viewers>
```

### Step 4. Test if the library works
- Run the file examples/1_versions_check.py

Enjoy!

Troubleshooting
---------------

See here: https://compas.dev/compas_slicer/installation.html#troubleshooting-1


Contributions
------------

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

- Add an example on the examples folder that uses the new functionality. Run the example and make sure it works smoothly. Ideally also add a visualization of the result using compas.MeshPlotter (see the other examples in the same folder)

- Create a pull request for the master branch, where you explain in detail what you fixed. When you create a pull request, there is an automatic action that runs the tests for your code again on the server.
Make sure the pull request passes the automatic tests as well. If not, then inspect the result, find what went wrong, fix it, and push again the result on your branch. The action will run again automatically on the open pull request.


Authors
-------------

* Ioanna Mitropoulou <<mitropoulou@arch.ethz.ch>> [@ioanna21](https://github.com/ioanna21)
* Joris Burger <<burger@arch.ethz.ch>> [@joburger](https://github.com/joburger)
* Andrei Jipa <<jipa@arch.ethz.ch>> [@stratocaster](https://github.com/stratocaster)