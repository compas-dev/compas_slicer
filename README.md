# compas_slicer

[![Licence MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/dbt-ethz/compas_am/blob/master/LICENSE) [![Travis](https://travis-ci.org/dbt-ethz/compas_am.svg?branch=master)](https://travis-ci.org/dbt-ethz/compas_am)

Additive manufacturing package for the COMPAS framework.


Main features
-------------

* Planar slicing
* Curved slicing (using the stratum library)


Getting started
------------

Clone the repository 

```bash
git clone --recursive https://github.com/dbt-ethz/compas_slicer.git
```

Create a new conda environment.

To install compas_am from this folder use: 

```bash
pip install -e <path>.
```

Then run the file examples/1_versions_check.py

Note: 

To use the curved slicer you also need to go to the folder dependencies/stratum and run
```bash
pip install -e .
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
