"""
dimension.py:
Library of physical dimensions.
"""

from __future__ import division

class DimensionError(Exception): pass
class IncompatibleDimensionsError(DimensionError): pass


class Dimension(object):
    """Class describing dimensions: length, time, etc. and derivative dimensions."""
    
    def __init__(self, *args, **kwargs):
        """Can be initialized like this:
        Dimension(L = 1, T = -2) using named arguments,
        Dimension(d) using another dimension
        Dimension("L/T") using a string <== Not yet."""
        dimensions_considered = ['M', 'L', 'T', 'Q', 'Theta']
        # If args contains something, it should be a dimension
        if len(args) > 1:
            raise DimensionError
        elif len(args) == 1:
            d = args[0]
            if type(d) != type(self): # it's not a dimension
                raise DimensionError
            if len(kwargs) > 0: # shouldn't have included more inputs
                raise DimensionError
            for k in dimensions_considered:
                self.__dict__[k] = d.__dict__[k]
        else: # len(args) == 0, so I should only have named arguments
            if len(set(kwargs.keys()) - set(dimensions_considered)) > 0:
                raise DimensionError
            for k in dimensions_considered:
                self.__dict__[k] = 0 if k not in kwargs else kwargs[k]
            
    def __eq__(self, other):
        """Check for equality."""
        return self.M == other.M and self.L == other.L \
            and self.T == other.T and self.Q == other.Q and self.Theta == other.Theta
    
    def __ne__(self, other):
        """Check for difference."""
        return self.M != other.M or self.L != other.L \
            or self.T != other.T or self.Q != other.Q or self.Theta != other.Theta
            
    def __add__(self, other):
        """Addition: checks for compatibility."""
        if self != other:
            raise IncompatibleDimensionsError
        else:
            return Dimension(self) # create a copy of self.

    def __sub__(self, other):
        """Subtraction: checks for compatibility."""
        if self != other:
            raise IncompatibleDimensionsError
        else:
            return Dimension(self) # create a copy of self.

    def __mul__(self, other):
        """Multiplication."""
        return Dimension(M = self.M + other.M,
            L = self.L + other.L,
            T = self.T + other.T,
            Q = self.Q + other.Q,
            Theta = self.Theta + other.Theta)

    def __div__(self, other):
        """Division (when __future__.division is not defined)."""
        return Dimension(M = self.M - other.M,
            L = self.L - other.L,
            T = self.T - other.T,
            Q = self.Q - other.Q,
            Theta = self.Theta - other.Theta)

    def __truediv__(self, other):
        """Division (when __future__.division is defined).."""
        return Dimension(M = self.M - other.M,
            L = self.L - other.L,
            T = self.T - other.T,
            Q = self.Q - other.Q,
            Theta = self.Theta - other.Theta)

