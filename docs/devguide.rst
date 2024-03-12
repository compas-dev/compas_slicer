***************
Developer Guide
***************


Contributions
===============

Before contributing code:

* Fork [the repository](https://github.com/compas-dev/compas_slicer) and clone the fork.

* Install compas_slicer from your local forked copy:

   .. code-block:: bash

      pip install -e .

* Install development dependencies:

   .. code-block:: bash

      pip install -r requirements-dev.txt

* BEFORE you start working on your updates, make sure all tests pass:

   .. code-block:: bash

      invoke test

* BEFORE you start working on your updates, make sure you pass flake8 tests.

   .. code-block:: bash

      invoke lint

* Now you can add your code in the appropriate folder. If you are not sure where to put it, contact `@ioannaMitropoulou <https://github.com/ioannaMitropoulou>`_.

* Add an example in the examples folder that uses the new functionality. Run the example and ensure it works smoothly.

* Add your name to the authors in README.md.

* Make sure again that all tests pass, and that flake8 is also happy!

* Create a [pull request](https://help.github.com/articles/about-pull-requests/) for the master branch, where you explain in detail what you fixed. When you create a pull request, there is an automatic action that runs the tests for your code again on the server. Make sure the pull request passes the automatic tests as well. If not, inspect the result, find what went wrong, fix it, and push the result again to your branch. The action will run again automatically on the open pull request.


During development, use [pyinvoke](http://docs.pyinvoke.org/) tasks on the
command line to ease recurring operations:

* `invoke clean`: Clean all generated artifacts.
* `invoke check`: Run various code and documentation style checks.
* `invoke docs`: Generate documentation.
* `invoke test`: Run all tests and checks in one swift command.
* `invoke`: Show available tasks.


Increase version
===================

To increase the version of compas_slicer, do the following:

* Push all your changes to the main branch and make sure that your local copy is on the main branch and has no updates.

* Use the command 'release' with the options major / minor / patch

   .. code-block:: bash

      invoke release patch

This automatically pushes the new changes to pip. Conda forge will pick it up and in a few hours you will receive an email. Approve the PR request and then the updated version also goes to conda.