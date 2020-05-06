# compas_am

[![Licence MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/dbt-ethz/compas_am/blob/master/LICENSE) [![Travis](https://travis-ci.org/dbt-ethz/compas_am.svg?branch=master)](https://travis-ci.org/dbt-ethz/compas_am)

Additive manufacturing package for the COMPAS framework.


Main features
-------------

* Slicing functionality for COMPAS


Requirements
------------

* [compas](https://compas-dev.github.io/)


Installation
------------

Create a new conda environment.

To install compas_am from this folder use: 

```bash
pip install -e <path>.
```

Then run the file examples/1_versions_check.py

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

- Add an example on the examples folder that uses the new functionality. Run the example and make sure it works smoothly.

- Run the python file: `` tests/test_examples.py ``.  Visually inspect the results that appear to see that no example produces unexpected results. To make sure that none of the examples throws an error, check your terminal. When all examples have been executed you should see the message  `` ---- Successfully executed all examples``


Authors
-------------

* Ioanna Mitropoulou <<mitropoulou@arch.ethz.ch>> [@ioanna21](https://github.com/ioanna21)
* Joris Burger <<burger@arch.ethz.ch>> [@joburger](https://github.com/joburger)
