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
        self._dimensions_considered = ['M', 'L', 'T', 'Q', 'Theta']
        # If args contains something, it should be a dimension
        if len(args) > 1:
            raise DimensionError
        elif len(args) == 1:
            d = args[0]
            if type(d) != type(self): # it's not a dimension
                raise DimensionError
            if len(kwargs) > 0: # shouldn't have included more inputs
                raise DimensionError
            for k in self._dimensions_considered:
                self.__dict__[k] = d.__dict__[k]
        else: # len(args) == 0, so I should only have named arguments
            if len(set(kwargs.keys()) - set(self._dimensions_considered)) > 0:
                raise DimensionError
            for k in self._dimensions_considered:
                self.__dict__[k] = 0 if k not in kwargs else kwargs[k]
            
    def is_primitive(self):
        """The dimension is primitive if it's either dimensionless or only one."""
        number_of_ones = 0
        number_of_nonzeros_and_nonones = 0
        for k in self._dimensions_considered:
            p = self.__dict__[k] # power of this dimension
            if p == 1:
                number_of_ones += 1
            elif p != 0:
                number_of_nonzeros_and_nonones += 1
        return number_of_nonzeros_and_nonones == 0 and number_of_ones in [0, 1]
    
    def str(self):
        numerator = ""
        denominator = ""
        for k in self._dimensions_considered:
            v = self.__dict__[k]
            if v == 0:
                continue
            if v == 1:
                numerator += "%s" % k
            elif v == -1:
                denominator += "/%s" % k
            elif v > 0:
                numerator += "%s^%s" % (k, v)
            else:
                denominator += "/%s^%s" % (k, -v)
        if numerator == "":
            numerator = "1"
        return numerator + denominator
            
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

