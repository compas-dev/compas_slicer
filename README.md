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
- You should get the message 'succesfully installed compas-slicer' (amongst other packages)

### Step 2. Install compas_viewers

- Install compas_viewers (https://github.com/compas-dev/compas_viewers).

To install on an existing environment with python=3.7, use:
```bash
conda activate <environment_name>
pip install PySide2 
pip install PyOpenGL 
pip install path/to/compas_viewers
```

### Step 3. Test if the library works
- Run the file examples/1_versions_check.py

Enjoy!


Additional Features
------------

### Compas_cal
Compas_cgal offers a very fast planar slicing method, in order to install it on your <environment> follow the steps described below

- Clone compas_cgal repository (https://github.com/BlockResearchGroup/compas_cgal)
```bash
conda activate <environment>
conda install eigen boost-cpp mpir mpfr cgal-cpp">=5.0" pybind11
```
- Navigate to the folder where you cloned the compas_cgal repository and install compas_cgal using:
```bash
pip install -e .
```
- You should get the message 'succesfully installed compas-cgal'

### Stratum, library for curved slicing. 

If you want to create curved slices, you need to install the stratum library. 
You can find it here: https://github.com/ioanna21/stratum

If you cannot access the repository, contact Ioanna <<mitropoulou@arch.ethz.ch>>.
Once you have it, then download it and install it.

- Then install igl
```bash
conda activate <environment>
conda install -c conda-forge igl
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

- Add an example on the examples folder that uses the new functionality. Run the example and make sure it works smoothly. Ideally also add a visualization of the result using compas.MeshPlotter (see the other examples in the same folder)

- Run the python file: `` tests/test_examples.py ``.  Visually inspect the results that appear to see that no example produces unexpected results. To make sure that none of the examples throws an error, check your terminal. When all examples have been executed you should see the message  `` ---- Successfully executed all examples``


Authors
-------------

* Ioanna Mitropoulou <<mitropoulou@arch.ethz.ch>> [@ioanna21](https://github.com/ioanna21)
* Joris Burger <<burger@arch.ethz.ch>> [@joburger](https://github.com/joburger)
