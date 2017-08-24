__version__ = '0.1.4'

import logging
import logging.config
import sys 


logging.basicConfig(stream=sys.stdout, level=logging.INFO, disable_existing_loggers=False)

from .core import IPySig 
