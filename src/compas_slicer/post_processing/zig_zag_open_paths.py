import logging

logger = logging.getLogger('logger')

__all__ = ['zig_zag_open_paths']


def zig_zag_open_paths(slicer):
    """ Reverses half of the open paths of the slicer, so that they can be printed in a zig zag motion. """
    reverse = False
    for layer in slicer.layers:
        for i, path in enumerate(layer.paths):
            if not path.is_closed:
                if not reverse:
                    reverse = True
                else:
                    path.points.reverse()
                    reverse = False

                path.is_closed = True  # label as closed so that it is printed without interruption
