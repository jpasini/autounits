"""
dimension.py:
Library of physical dimensions.
"""

from __future__ import division

class DimensionError(Exception): pass
class IncompatibleDimensionsError(DimensionError): pass


class Dimension(object):
    """Class describing dimensions: length, time, etc. and derivative dimensions."""
    
    def __init__(self, M = 0, L = 0, T = 0, Q = 0, Theta = 0):
        """Can be initialized like this:
        Dimension(L = 1, T = -2) using named arguments,
        Dimension(d) using another dimension
        Dimension("L/T") using a string."""
        # check the first argument in case it's a different type
        if type(M) == type(self): # it's a dimension
            # To do: check that there are no other arguments?
            self.M = M.M
            self.L = M.L
            self.T = M.T
            self.Q = M.Q
            self.Theta = M.Theta
        elif type(M) == str:
            pass
        else:
            self.M = M
            self.L = L
            self.T = T
            self.Q = Q
            self.Theta = Theta
            
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

