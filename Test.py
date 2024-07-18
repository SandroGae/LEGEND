import os
import l200geom

try:
    print("l200geom module path: ", os.path.dirname(l200geom.__file__))
except AttributeError:
    print("The module 'l200geom' does not have a __file__ attribute. It may not be properly installed.")
except ImportError as e:
    print("Error importing l200geom: ", e)
