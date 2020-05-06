import pytest
# from os.path import dirname, basename, isfile, join
import os, sys, glob
import compas
from compas.datastructures import Mesh

EXAMPLES_PATH = os.path.join(os.path.dirname(__file__), '..', 'examples')
sys.path.append(EXAMPLES_PATH)

modules = glob.glob(os.path.join(EXAMPLES_PATH, "*.py"))
__all__ = [ os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]

if __name__ == "__main__":
    for module in __all__:
        i = __import__(module)
        print ("\n ---- Running example : " + str(module))
        i.main()

    print ("\n ---- Successfully executed all examples")