# compas_slicer

[![Licence MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/dbt-ethz/compas_am/blob/master/LICENSE) [![Travis](https://travis-ci.org/dbt-ethz/compas_am.svg?branch=master)](https://travis-ci.org/dbt-ethz/compas_am)

Additive manufacturing package for the COMPAS framework.


Main features
-------------

* Planar slicing
* Curved slicing (using the stratum library)


Getting started
------------

### Step 1: Install compas_cal
- Clone compas_cgal repository (https://github.com/BlockResearchGroup/compas_cgal)
- Create a new environment (you can replace 'compas_slicer' with your own environment name) and install COMPAS.
```bash
conda create -n compas_slicer python=3.7 eigen boost-cpp mpir mpfr cgal-cpp">=5.0" pybind11 COMPAS">=0.16.0"
conda activate compas_slicer
```
- Navigate to the folder where you cloned the compas_cgal repository and install compas_cgal using:
```bash
pip install -e .
```
- You should get the message 'succesfully installed compas-cgal'

### Step 2: Install compas_slicer
- Clone the repository and activate your environment. Do not forget to clone the repository using --recursive or the submodules will not work. 
```bash
git clone --recursive https://github.com/dbt-ethz/compas_slicer.git
conda activate compas_slicer
```
- Navigate to the folder where you cloned the compas_slicer repository and install compas_slicer using:
```bash
pip install -e .
```
- You should get the message 'succesfully installed compas-slicer' (amongst other packages)

### Step 3: Install stratum
- Navigate to the compas_slicer repository folder/dependencies/stratum and install stratum using:
```bash
pip install -e
```
- You should get the message 'succesfully installed stratum'
- Then install igl
```bash
pip install -e .
```

### Step 4. Install compas_fab
- Install compas_fab (https://gramaziokohler.github.io/compas_fab/latest/) in your current environment using:
```bash
pip install compas_fab
```


### Step 5. Test if the library works
- Run the file examples/1_versions_check.py



Submodules
------------

Stratum, https://github.com/ioanna21/stratum

To update the submodules use 

```bash
git pull --recurse-submodules
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
