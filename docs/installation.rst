************
Installation
************

.. rst-class:: lead

COMPAS_SLICER can be easily installed on multiple platforms.

Basic installation steps
========================

Step 1: Install compas
----------------------

Create a new environment (you can replace 'compas_slicer' with your own environment name),
and install compas, compas_cgal, and libigl.

.. code-block:: bash

    conda create -n compas_slicer python=3.7
    conda activate compas_slicer
    conda install COMPAS
    conda install COMPAS compas_cgal
    conda install -c conda-forge igl


Step 2: Install compas_slicer
-----------------------------

Clone the repository and activate your environment.

.. code-block:: bash

    git clone https://github.com/dbt-ethz/compas_slicer.git
    conda activate compas_slicer

Navigate to the folder where you cloned the compas_slicer repository and install compas_slicer using:

.. code-block:: bash

    pip install -e .

You should get the message 'Successfully installed compas-slicer' (amongst other packages)


Step 3. Install compas_viewers
------------------------------

Install compas_viewers (https://github.com/compas-dev/compas_viewers).

Download the wheel file from here: https://www.lfd.uci.edu/~gohlke/pythonlibs/

To install on an existing environment with python=3.7, use:

.. code-block:: bash

    conda activate <environment_name>
    pip install PySide2 
    pip install <path/to/file>/PyOpenGL‑3.1.5‑cp37‑cp37m‑win_amd64.whl
    pip install <path/to/compas_viewers>


Step 4. Test if the library works
---------------------------------
Run the file examples/1_versions_check.py


Troubleshooting
===============

If you encounter a problem that is not described here, please file an issue 
using the `Issue Tracker <https://github.com/dbt-ethz/compas_slicer/issues>`_.

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
