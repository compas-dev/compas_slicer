__all__ = ['region_splitting']


def region_splitting():
    """
    Curved slicing pre-processing step.

    Takes one continuous mesh with various saddle points and splits it up
    at every saddle point, so that the resulting mesh has no remaining saddle points,
    only minima and maxima.

    The result is a series of split meshes whose vertes attributes have been updated
    to reflect the initial attributes.
    (i.e. they all have vertex 'boundary' attributes 1,2 on their lower and uppper
    boundaries)

    For each newly created mesh, a separate slicer needs to be created. Like that,
    we will always have one slicer per mesh with the correct attributes already assigned.
    However, it can still happen that the slicer takes a mesh that outputs various
    segments (vertical layers). Then topological sorting is needed both in
    this pre-processing step, and in the curved_print_organizer.

    """
    pass  # TODO, bring region split from Stratum here.
