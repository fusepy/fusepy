__version__ = '1.2'

try:
    from fuse3x import *
except ImportError:
    from fuse2x import *
