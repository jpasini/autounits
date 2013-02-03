"""
dimension.py:
Library of physical dimensions.
"""

from __future__ import division

class DimensionError(Exception): pass
class IncompatibleDimensionsError(DimensionError): pass


class Dimension(object):
    """Class describing dimensions (length, time, mass, and derivative dimensions.)"""
        
