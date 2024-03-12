Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

0.7.0
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.6.2
----------

**Added**
* Costa surface on curved slicing example

**Changed**

**Fixed**
* Fixed bug in sorting to vertical layers 

**Deprecated**

**Removed**

0.6.1
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.6.0
----------

**Added**
* Output nested printpoints  

**Changed**
* Updates in the visualization of PrintPoints
* Added seams_align(next_path) to the standard planar slicing routine
* Added unify_path_orientation back into the standard planar slicing routine
* The way the normal and up_vector are calculated in the print organizers
* Small updates in grasshopper visualization functions

**Fixed**
* spiralize_contours : After function points are reprojected on the mesh
* Curved slicing grasshopper file improved
* Bug in post-processing of slicer paths generation

**Deprecated**

**Removed**

0.5.0
----------

**Added**
* Zenodo integration

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.4.0
----------

**Added**
* Documentation updates
* rdp libigl function (faster than the regular rdp)
* sort_paths_minimum_travel_time: Function to sort paths by least travel time between contours in a layer

**Changed**
* Changed the blend radius to add a blend radius of 0 for the first and last point of a path
* Changed planar_slicing_cgal to add the possibility of slicing open paths with planar_slicing_cgal
* Added the option to toggle generation of mesh normals on/off in create_printpoints
* Added the possibility to slice only a certain section of the geometry by using slice_height_range in the PlanarSlicer

**Fixed**
* Fixed some bugs in seams_align
* Small bug in extruder_toggle
* Small bug in simplify_paths_rdp_igl with printing remaining no of points
* Bug in seams_smooth

**Deprecated**

* close_paths in the BaseSlicer is unused for now, as it should not be necessary

**Removed**

0.3.5
----------

**Added**

* Add GH Python package to the installation.

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.3.4
----------

**Added**
* Alternative union operations in curved slicing.
* function that adds wait time at sharp corners. 

**Changed**

 *Small improvements in gcode
 *Updated examples, and setup tutorials content (which is still empty - remaining to be filled)
 *set_blend_radius function assigns 0 to ppts that have a wait time (so that we are sure they are reached exactly)

**Fixed**

**Deprecated**

**Removed**
 * csWeightedUnion (outdated)

0.3.3
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

* Removed libigl from the requirements, since it is not on pip we cannot have it in the requirements for now. We should also update the installation instructions for conda and pip.

0.3.2
----------

**Added**

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.3.1
----------

**Changed**

* Version to 0.3.1

0.3.0
----------

**Added**
* Zig Zag paths in print organization
* Added automatic install on Rhino and GH when compas core is installed. 

**Changed**

* Switched from compas_viewers to compas_viewers2
* Updated csLoadPrintpoint.ghuser component on the data/gh_components and on the gh examples

**Fixed**
* Bug in PrintPoint.get_frame() method. (It was throwing a 0-division error when contours where situated on flat surfaces) x 2
* Bug in calculation of desired number of isocurves in interpolation slicer
* Bug in safety points (their frame was not matching their point position)
* Bug in tool plane in grasshopper visualization. (Its axis did not match the compas_fab convention.)

**Deprecated**

**Removed**
* Feasibility parameter from printpoints visualization. (Had forgotten to delete it from visualization when it was deleted from printpoints )

0.2.1
----------

**Added**

* Bumped version to 0.2.1

**Changed**

**Fixed**

**Deprecated**

**Removed**

0.2.0
----------

**Added**

* Iterators through printpoints in PrintOrganizer
* Iterative smoothing of attributes on printpoints (ex smooth velocities, orientations etc)
* Export of (jsonable) PrintPoint attributes to json (in previous versions they were ignored upon export)

**Changed**

* added first layer in the slicing process that was previously removed.
* set_velocity function was split into separate functions depending on type (constant, by layer, by range, by overhang)

**Fixed**

* Fixed bug on the calculation of the Printpoint frame (both on PrintOrganizer and on the gh visualization).

**Deprecated**

**Removed**

* VerticalConnectivity from CurvedPrintOrganizer. This function does not need to be on its own class.
* Checking feasibility of Printpoints in PrintOrganizer (anyway it was a function left not-implemented in most PrintOrganizers). Might be re-introduced in the future but with more specific tasks.
* Planar slicing using MeshCut (and meshcut library from requirements).

0.1.3
----------

**Added**

* Fancy badges in the readme
* Export to Gcode

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
