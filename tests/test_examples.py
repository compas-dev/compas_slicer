import sys
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

examples = [
    ("1_planar_slicing_simple", "example_1_planar_slicing_simple"),
    ("2_curved_slicing", "ex2_curved_slicing"),
    ("3_planar_slicing_vertical_sorting", "example_3_planar_vertical_sorting"),
    ("4_gcode_generation", "example_4_gcode"),
    ("5_non_planar_slicing_on_custom_base", "scalar_field_slicing"),
    ("6_attributes_transfer", "example_6_attributes_transfer"),
]


@pytest.mark.parametrize("folder,module", examples)
def test_example(folder, module):
    """Run example as integration test."""
    example_path = str(EXAMPLES_DIR / folder)
    sys.path.insert(0, example_path)
    try:
        mod = __import__(module)
        mod.main()
    finally:
        sys.path.remove(example_path)
