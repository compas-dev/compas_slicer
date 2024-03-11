.. _compas_slicer_installation:

************
Installation
************

.. rst-class:: lead

COMPAS_SLICER can be easily installed on multiple platforms.

Basic installation steps
========================

Install compas slicer
-----------------------------


The recommended way to install `compas_slicer` is with `conda <https://conda.io/docs/>`_.
For example, create an environment named ``my-project`` (or replace with your own environment name) and install as follows:

.. code-block:: bash

    conda config --add channels conda-forge
    conda create -n my-project compas_slicer
    conda activate my-project


* Install COMPAS CGAL

.. code-block:: bash

    conda install -c conda-forge compas_cgal


* Install Grasshopper components

The Grasshopper components are automatically installed with the `compas_rhino` installation, e.g.:

.. code-block:: bash

    conda activate my-project
    python -m compas_rhino.install -v 7.0


* Test if the library works

Activate your environment and run the following command:

.. code-block:: bash

    conda activate my-project
    python -m compas_slicer

Enjoy!



Contributions
===============

Before contributing code:

- Install development dependencies:

.. code-block:: bash
    pip install -r requirements-dev.txt

- Make sure all tests pass:
.. code-block:: bash
    invoke test

- Make sure you pass flake8 tests. (hint: This is the most annoying part of the process)
.. code-block:: bash
    invoke lint

- Add your code in the appropriate folder. If you are not sure where to put it, contact [@ioannaMitropoulou](https://github.com/ioannaMitropoulou).

- Add an example on the examples folder that uses the new functionality. Run the example and make sure it works smoothly.

- Add your name to the authors in README.md.

- Create a pull request for the master branch, where you explain in detail what you fixed. When you create a pull request, there is an automatic action that runs the tests for your code again on the server.
Make sure the pull request passes the automatic tests as well. If not, then inspect the result, find what went wrong, fix it, and push again the result on your branch. The action will run again automatically on the open pull request.



Troubleshooting
===============

If you encounter a problem that is not described here, please file an issue 
using the `Issue Tracker <https://github.com/compas-dev/compas_slicer/issues>`_.

Installing Planarity
--------------------

.. code-block:: bash

    ModuleNotFoundError: No module named 'Cython'

The installation process with pip can fail while installing planarity because Cython is not installed.
In that case, install cython using pip (or conda) and then run the installation of COMPAS_SLICER again.

.. code-block:: bash

    pip install cython --install-option="--no-cython-compile"

Microsoft Visual C++ Build Tools
--------------------------------

.. code-block:: bash

    error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/

The installation with pip can fail because “Microsoft Visual C++ Build Tools are missing”. 
To install the Microsoft Visual C++ Build Tools choose one of the options provided here: 
https://www.scivision.dev/python-windows-visual-c-14-required/ and just follow the instructions. 
Then run the pip installation commands again.

Numpy error
-----------

.. code-block:: bash

    RuntimeError: The current Numpy installation ('C:\\Users\\<username>\\.conda\\envs\\compas_slicer\\lib\\site-packages\\numpy\\__init__.py') fails to pass a sanity check due to a bug in the windows runtime. See this issue for more information: https://tinyurl.com/y3dm3h86

A conflict between Numpy and Python can appear, in order to fix this you need to downgrade Numpy to 1.19.3 (from 1.19.4).
Make sure you are in the correct environment and type:

.. code-block:: bash

    pip install numpy==1.19.3

Fractions error
---------------
.. code-block:: bash

    ImportError: cannot import name 'gcd' from 'fractions' (C:\ProgramData\Anaconda3\envs\compas_slicer\lib\fractions.py)

This issue can be solved, as explained here:  https://stackoverflow.com/questions/66174862/import-error-cant-import-name-gcd-from-fractions
by typing the following command (make sure you are in the correct environment)

.. code-block:: bash

    conda install -c conda-forge networkx=2.5

