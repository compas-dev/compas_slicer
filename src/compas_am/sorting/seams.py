import logging

logger = logging.getLogger('logger')

__all__ = ['seams_align',
           'seams_random']

def seams_align(layers):
    sorted_layers = layers
    logger.warning("Align seams method needs to be implemented")
    return sorted_layers


def seams_random(layers):
    sorted_layers = layers
    logger.warning("Align seams random method needs to be implemented")
    return sorted_layers


if __name__ == "__main__":
    pass
