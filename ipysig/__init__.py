from ipysig.version import __version__

import logging
import logging.config
import sys 


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, disable_existing_loggers=False)

from .core import IPySig 
