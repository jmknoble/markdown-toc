import logging

logger = logging.getLogger(__name__)

# Imports, if any

# fmt: off

__author__ = 'jmknoble'
__email__ = 'jmknoble@pobox.com'
__version__ = '0.3.0'

# fmt: on


def get_version(thing=None):
    if thing is None:
        return __version__
    return "{thing} v{version}".format(thing=thing, version=__version__)
