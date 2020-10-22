************
Installation
************

.. rst-class:: lead

COMPAS_SLICER can be easily installed on multiple platforms.

Basic installation steps
========================

Step 1: Install compas_slicer
-----------------------------

Create a new environment (you can replace 'compas_slicer' with your own environment name).

.. code-block:: bash

    conda create -n compas_slicer python=3.7

Clone the repository and activate your environment.

.. code-block:: bash

    git clone https://github.com/dbt-ethz/compas_slicer.git
    conda activate compas_slicer

Navigate to the folder where you cloned the compas_slicer repository and install compas_slicer using:

.. code-block:: bash

    pip install -e .

You should get the message 'Successfully installed compas-slicer' (amongst other packages)


Step 2. Install compas_viewers
------------------------------

Install compas_viewers (https://github.com/compas-dev/compas_viewers).

Download the wheel file from here: https://www.lfd.uci.edu/~gohlke/pythonlibs/

To install on an existing environment with python=3.7, use:

.. code-block:: bash

    conda activate <environment_name>
    pip install PySide2 
    pip install <path/to/file>/PyOpenGL‑3.1.5‑cp37‑cp37m‑win_amd64.whl
    pip install <path/to/compas_viewers>


Step 3. Test if the library works
---------------------------------
Run the file examples/1_versions_check.py


Additional Features
===================

compas_cal
----------

Compas_cgal offers a very fast method for planar slicing.
It is available via conda-forge for Windows, OSX, and Linux, and can be installed using conda.

.. code-block:: bash

    conda activate <environment>
    conda install COMPAS compas_cgal