import compas
from loguru import logger

import compas_slicer

if __name__ == '__main__':
    logger.info(f'COMPAS: {compas.__version__}')
    logger.info(f'COMPAS Slicer: {compas_slicer.__version__}')
    logger.info('Awesome! Your installation worked! :)')
