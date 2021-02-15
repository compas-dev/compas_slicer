Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.1.3
----------

**Added**

* Fancy badges in the readme

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.1.2
----------

**Fixed**

* Small bug in example 1 regarding the raft

0.1.1
----------

**Added**

* Generate raft functionality

* is_raft parameter to the Layer

**Changed**

* Simplify paths to exclude simplification of raft layers

* Error raised when brim is attempted to be applied to a raft layer.

**Fixed**

* Small bug in print time calculation



2021-02-11
----------

**Added**

* UVcontours, UVslicer

* VerticalLayersManager

**Changed**

* Renamed the curved_slicer and all processes named after that (i.e. curved_preprocessor, curved_slicing_parameters, curved_print_organizer etc) to interpolation_slicer. These changes make this PR a breaking change.

* Reorganized the parameters folder. A lot of parameters where considered 'curved_slicing_parameters' although they were more general. So I broke those down into separate files. More parameters will be added in the future to those files.

**Fixed**

* Some documentation

* Slicer printout_info bug

**Deprecated**

**Removed**

* folder slicers.curved_slicing and all its contents.



2021-02-03
----------

**Added**

* Reorder vertical layers functionality

* Added z_height attribute to Layer and min_max_z_height to VerticalLayer

**Changed**

* Extension of CHANGELOG

* Changed naming of *sort_per_vertical_segment* to *sort_into_vertical_layers*

* Changed naming of *get_segments_centroids_list* to *get_vertical_layers_centroids_list*

**Fixed**

* Typo in wait time

**Deprecated**

**Removed**

2021-01-25
----------

**Added**

* ScalarFieldPrintOrganization as a slicing method

* Transfer of attributes from mesh faces and vertices to PrintPoints (utilities/attributes_transfer.py). Added the necessary attributes in the PrintPoints. Also added an example (example_6_attributes_transfer.py) showcasing this functionality.

**Changed** 

* Cleaned up the 'printout_info' methods in the BaseSlicer and BasePrintOrganizer

* Refactored GradientEvaluation so that it can be applied in general for scalar fields, instead of just for interpolation fields

2021-01-25
----------

**Added** 

*ScalarFieldContours as a slicing method

**Changed**

* Bug fixes on CurvedSlicingPreprocessor
