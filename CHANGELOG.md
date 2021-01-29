# Changelog

As of January 2021 all notable changes to this project will be documented in this file.


## 2021-01-25
Added : ScalarFieldPrintOrganization as a slicing method

Transfer of attributes from mesh faces and vertices to PrintPoints (utilities/attributes_transfer.py). Added the necessary attributes in the PrintPoints. Also added an example (example_6_attributes_transfer.py) showcasing this functionality.

Changed: Cleaned up the 'printout_info' methods in the BaseSlicer and BasePrintOrganizer

Refactored GradientEvaluation so that it can be applied in general for scalar fields, instead of just for interpolation fields

Removed: -


## 2021-01-25
Added : ScalarFieldContours as a slicing method

Changed: Bug fixes on CurvedSlicingPreprocessor

Removed: -
