# compas_slicer

[![Licence MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/dbt-ethz/compas_slicer/blob/master/LICENSE) [![Travis](https://travis-ci.org/dbt-ethz/compas_slicer.svg?branch=master)](https://travis-ci.org/dbt-ethz/compas_slicer)

Additive manufacturing package for the COMPAS framework.


Main features
-------------

* Planar slicing
* Curved slicing (using the stratum library)
* Export robotic commands in Json format

Getting started
------------

### Step 1: Install compas_slicer
- Create a new environment (you can replace 'compas_slicer' with your own environment name).
```bash
conda create -n compas_slicer python=3.7
```
- Clone the repository and activate your environment.
```bash
git clone https://github.com/dbt-ethz/compas_slicer.git
conda activate compas_slicer
```
- Navigate to the folder where you cloned the compas_slicer repository and install compas_slicer using:
```bash
pip install -e .
```
- You should get the message 'Successfully installed compas-slicer' (amongst other packages)

### Step 2. Install compas_viewers

- Install compas_viewers (https://github.com/compas-dev/compas_viewers).

Download the wheel file from here: https://www.lfd.uci.edu/~gohlke/pythonlibs/
To install on an existing environment with python=3.7, use:
```bash
conda activate <environment_name>
pip install PySide2 
pip install <path/to/file>/PyOpenGL‑3.1.5‑cp37‑cp37m‑win_amd64.whl
pip install <path/to/compas_viewers>
```


### Step 3. Test if the library works
- Run the file examples/1_versions_check.py

Enjoy!


Additional Features
------------

### Compas_cal
Compas_cgal offers a very fast planar slicing method, in order to install it on your <environment> follow the steps described below

```bash
conda activate <environment>
conda install COMPAS compas_cgal
```

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
