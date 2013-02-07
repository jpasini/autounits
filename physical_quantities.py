"""
physical_quantities.py:
Library of physical quantities, with automatic unit conversion.
"""

from __future__ import division

class PhysicalQuantityError(Exception): pass
class BadInputError(PhysicalQuantityError): pass
class BadUnitDictionaryError(PhysicalQuantityError): pass
class IncompatibleUnitsError(PhysicalQuantityError): pass

from dimension import Dimension, parse_unit_string

def flatten_dictionary(units_dictionary):
    # Make sure there are no name clashes in the units
    from itertools import chain, ifilter
    k = units_dictionary.keys()
    tuples     = list(ifilter(lambda x: type(x) == tuple, k)) # find tuples
    not_tuples = list(ifilter(lambda x: type(x) != tuple, k))
    flattened_tuples = list(chain(*tuples))
    # join
    rejoined = flattened_tuples + not_tuples
    flattened_keys = set(rejoined)
    if len(flattened_keys) != len(rejoined):
        raise BadUnitDictionaryError
            
    # At this point there are no name clashes, so flatten
    new_dictionary = dict()
    for k,v in units_dictionary.iteritems():
        if type(k) != tuple:
            new_dictionary[k] = v
        else:
            for l in k:
                new_dictionary[l] = v
    return new_dictionary


class PhysicalQuantityStringParser(object):
    """Object that parses a string representing an amount with units."""
    def __init__(self, dimension, primitive_units_dictionaries):
        # To-do: Check if dimensionless quantities can receive a string
        
        # Create the dictionary for the dimensions given
        dimension_str = dimension.str()
        pattern = dimension.str(use_braces = True)
        d = {}
        for k,v in primitive_units_dictionaries.iteritems():
            d[k] = flatten_dictionary(v)
        
        # go systematically through all primitive unit-set combinations
        from itertools import product        
        p = list(product(d['M'].keys(), d['L'].keys(), d['T'].keys(), d['Q'].keys(), d['Theta'].keys()))
        new_dictionary = {}
        for units in p:
            # generate the string representing the units (e.g, "m/s^2")
            units_string_dictionary = dict(zip(['M','L','T','Q','Theta'], units))
            unit_string = pattern.format(**units_string_dictionary)
            # it could be repeated at this stage if the target quantity has only limited dimensions 
            unit_values = [d[k][units_string_dictionary[k]] for k in ['M','L','T','Q','Theta']]
            units_value_dictionary = dict(zip(['M','L','T','Q','Theta'], unit_values))
            # I need a parser to evaluate this expression
            if unit_string in new_dictionary.keys(): continue
            new_dictionary[unit_string] = parse_unit_string(dimension_str, units_value_dictionary)

        self.flat_units_dictionary = new_dictionary
        
        from pyparsing import Literal, replaceWith, \
            Or, nums, Word, stringEnd, ParseException
        
        def make_literal(unit_string, val):
            return Literal(unit_string).setParseAction(replaceWith(val))
        units = Or( [ make_literal(s,v) for s,v in new_dictionary.iteritems() ] )
        
        def validate_and_convert_number(tokens):
            try:
                return float(tokens[0])
            except ValueError:
                raise ParseException("Invalid number (%s)" % tokens[0])
        number = Word(nums + 'e' + '-' + '+' + '.')
        number.setParseAction(validate_and_convert_number)
        
        self._dimension = number + units + stringEnd
        
    def __call__(self, quantity_string):
        """Parse the given string."""
        from pyparsing import ParseException
        try:
            a = self._dimension.parseString(quantity_string)
        except ParseException:
            raise BadInputError
        return a[0]*a[1]
        
from functools import total_ordering

@total_ordering
class PhysicalQuantity(object):
    def __init__(self, dimension = Dimension(), value = None):
        if type(dimension) != Dimension:
            raise PhysicalQuantityError

        self.dimension = dimension
        # Conversion constants for primitive quantities
        self._primitive_units = {}
        self._primitive_units['M'] = {'kg': 1}
        self._primitive_units['L'] = {('m', 'meters'): 1, ('mi', 'miles'): 1609.344, ('km', 'kilometers'): 1000, 'marathon': 42194.988}
        self._primitive_units['T'] = {('s', 'seconds'): 1, ('min', 'minutes'): 60, ('hr', 'hours'): 3600}
        self._primitive_units['Q'] = {'C': 1}
        self._primitive_units['Theta'] = {'K': 1}
        
        self._parser = PhysicalQuantityStringParser(dimension, self._primitive_units)
        
        ## Create parsers for all primitive units.
        #self._parsers = {k: PhysicalQuantityStringParser(v) for k,v in self._primitive_units.iteritems()}

        self._amount_in_basic_units = None
        
        # Create units_dictionary for creating parser
        #self._parser = PhysicalQuantityStringParser(units_dictionary)
        if value is not None:
            if type(value) == str:
                self._amount_in_basic_units = self._parser(value)
            elif type(value) == type(self):
                if self.dimension != value.dimension:
                    raise IncompatibleUnitsError
                self._amount_in_basic_units = value._amount_in_basic_units
        
    def __getitem__(self, key):
        return self._amount_in_basic_units/self._parser.flat_units_dictionary[key]
                
    def __setitem__(self, key, value):
        self._amount_in_basic_units = value*self._parser.flat_units_dictionary[key]
                
    def __eq__(self, other):
        """Equality is defined by the dimension and amount."""
        return self.dimension == other.dimension and self._amount_in_basic_units == other._amount_in_basic_units
    
    def __ne__(self, other):
        """Equality is defined by the dimension and amount."""
        return self.dimension != other.dimension or self._amount_in_basic_units != other._amount_in_basic_units
    
    def __lt__(self, other):
        """Less-than comparison."""
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError
        return self._amount_in_basic_units < other._amount_in_basic_units
    
    def __add__(self, other):
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError        
        result = PhysicalQuantity(self.dimension)
        result._amount_in_basic_units = self._amount_in_basic_units + other._amount_in_basic_units
        return result
        
    def __sub__(self, other):
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError        
        result = PhysicalQuantity(self.dimension)
        result._amount_in_basic_units = self._amount_in_basic_units - other._amount_in_basic_units
        return result

    def __mul__(self, other):
        result = PhysicalQuantity(self.dimension*other.dimension)
        result._amount_in_basic_units = self._amount_in_basic_units*other._amount_in_basic_units
        return result
        
    def __div__(self, other):
        result = PhysicalQuantity(self.dimension/other.dimension)
        result._amount_in_basic_units = self._amount_in_basic_units/other._amount_in_basic_units
        return result
        
    def __truediv__(self, other):
        result = PhysicalQuantity(self.dimension/other.dimension)
        result._amount_in_basic_units = self._amount_in_basic_units/other._amount_in_basic_units
        return result
        


class Distance(PhysicalQuantity):
    def __init__(self, value = None):
        PhysicalQuantity.__init__(self, Dimension(L = 1), value)
        

class Time(PhysicalQuantity):
    def __init__(self, value = None):
        PhysicalQuantity.__init__(self, Dimension(T = 1), value)
        
    @property
    def str(self):
        secs = self['s']
        h, m = Time("1 hr"), Time("1 min")
        hours = int(secs/h['s'])
        secs = secs - hours*h['s']
        mins = int(secs/m['s'])
        secs = int(secs - mins*m['s'])
        result = ""
        if hours > 0:
            result = result + str(hours) + ":"
        result = result + '{0:02d}:{1:02d}'.format(mins,secs)
        return result
        

class Speed(PhysicalQuantity):
    def __init__(self, value = None):
        PhysicalQuantity.__init__(self, Dimension(L = 1, T = -1), value)
        
    def pace(self, distance):
        """Return time to cover given distance."""
        t = distance/self
        return t
        
