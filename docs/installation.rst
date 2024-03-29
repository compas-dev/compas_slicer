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


* Install from local folder

If you would like to install the latest code from github, or to make modifications on the code and have the updated version
run in your environment, then you can install compas_slicer from a local folder in your computer. To do that, after following
the steps described above clone the compas_slicer repository using the command

.. code-block:: bash

    git clone https://github.com/compas-dev/compas_slicer.git

Navigate to the compas_slicer folder and after you activate the desired environment, install compas_slicer from the local copy
with the following command:

.. code-block:: bash
    conda activate my-project
    pip install -e .


Enjoy!


Troubleshooting
===============

If you encounter a problem that is not described here, please file an issue 
using the `Issue Tracker <https://github.com/compas-dev/compas_slicer/issues>`_.

* Grasshopper components not working

If despite completing all the compas_slicer installation steps, the compas_slicer grasshopper components still do not work, then
you can fix this by manually adding the correct folder to your paths in Rhino.
In Rhino, type "EditPythonScript", go to Tools > Options > Add to search path and add the following folder:
<path>/compas_slicer/src/grasshopper_visualization'



* Installing Planarity

.. code-block:: bash

    ModuleNotFoundError: No module named 'Cython'

The installation process with pip can fail while installing planarity because Cython is not installed.
In that case, install cython using pip (or conda) and then run the installation of COMPAS_SLICER again.

.. code-block:: bash

    pip install cython --install-option="--no-cython-compile"

* Microsoft Visual C++ Build Tools

.. code-block:: bash

    error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/

The installation with pip can fail because “Microsoft Visual C++ Build Tools are missing”. 
To install the Microsoft Visual C++ Build Tools choose one of the options provided here: 
https://www.scivision.dev/python-windows-visual-c-14-required/ and just follow the instructions. 
Then run the pip installation commands again.

* Numpy error

.. code-block:: bash

    RuntimeError: The current Numpy installation ('C:\\Users\\<username>\\.conda\\envs\\compas_slicer\\lib\\site-packages\\numpy\\__init__.py') fails to pass a sanity check due to a bug in the windows runtime. See this issue for more information: https://tinyurl.com/y3dm3h86

A conflict between Numpy and Python can appear, in order to fix this you need to downgrade Numpy to 1.19.3 (from 1.19.4).
Make sure you are in the correct environment and type:

.. code-block:: bash

    pip install numpy==1.19.3

* Fractions error

.. code-block:: bash

    ImportError: cannot import name 'gcd' from 'fractions' (C:\ProgramData\Anaconda3\envs\compas_slicer\lib\fractions.py)

This issue can be solved, as explained here:  https://stackoverflow.com/questions/66174862/import-error-cant-import-name-gcd-from-fractions
by typing the following command (make sure you are in the correct environment)

.. code-block:: bash

    conda install -c conda-forge networkx=2.5



Bug reports
===========

When `reporting a bug <https://github.com/compas-dev/compas_slicer/issues>`_, please include:

- Operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

Feature requests
================

When `proposing a new feature <https://github.com/compas-dev/compas_slicer/issues>`_, please include:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
