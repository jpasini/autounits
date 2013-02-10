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


from pyparsing import ParseException
from pyparsing import Literal, replaceWith, Or, stringEnd

class PhysicalQuantityStringParser(object):
    """Object that parses a string representing an amount with units."""
    
    _primitive_units_dictionaries = None
    _parsers = {}
    _flat_unit_dictionaries = {}
    
    def __init__(self, dimension, primitive_units_dictionaries):
        # Create the dictionary for the dimensions given
        self._is_dimensionless = (dimension == Dimension()) # dimensionless quantities receive special treatment 
        dimension_str = dimension.str()
        
        if primitive_units_dictionaries != PhysicalQuantityStringParser._primitive_units_dictionaries:
            # we're changing unit sets, so I need to clear everything
            PhysicalQuantityStringParser._primitive_units_dictionaries = primitive_units_dictionaries
            PhysicalQuantityStringParser._parsers = {}
            PhysicalQuantityStringParser._flat_unit_dictionaries = {}
        else:
            # check: we might have done this case already
            if dimension_str in PhysicalQuantityStringParser._parsers:
                self.flat_units_dictionary = PhysicalQuantityStringParser._flat_unit_dictionaries[dimension_str]
                self._dimension = PhysicalQuantityStringParser._parsers[dimension_str]
                return

        
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
        
        def make_literal(unit_string, val):
            return Literal(unit_string).setParseAction(replaceWith(val))
        units = Or( [ make_literal(s,v) for s,v in new_dictionary.iteritems() ] )
        
        from pyparsing import Regex
        number = Regex(r'\d+(\.\d*)?([eE][+-]?\d+)?')
        number.setParseAction(lambda tokens: float(tokens[0]))
        
        if self._is_dimensionless:
            self._dimension = number + stringEnd
        else:
            self._dimension = number + units + stringEnd
        # add to our stock
        PhysicalQuantityStringParser._flat_unit_dictionaries[dimension_str] = self.flat_units_dictionary 
        PhysicalQuantityStringParser._parsers[dimension_str] = self._dimension 
        
    def __call__(self, quantity_string):
        """Parse the given string."""
        try:
            a = self._dimension.parseString(quantity_string)
        except ParseException:
            raise BadInputError
        if self._is_dimensionless:
            return a[0]
        else:
            return a[0]*a[1]

# mapping from dimension strings to derived types
mapping_to_derived_types = {}

from functools import total_ordering

@total_ordering
class PhysicalQuantity(object):
    # For caching:
    _parsers = {}
    _default_units = {}
    # Conversion constants for primitive quantities
    _primitive_units = {}
    _primitive_units['M'] = {('kg', 'kilogram', 'kilograms'): 1, ('g', 'gr', 'gram', 'grams'): 0.001}
    _primitive_units['L'] = {('m', 'meter', 'meters'): 1, ('mi', 'mile', 'miles'): 1609.344, ('km', 'kilometer', 'kilometers'): 1000, 'marathon': 42194.988}
    _primitive_units['T'] = {('s', 'sec', 'secs', 'second', 'seconds'): 1, ('min', 'mins', 'minute', 'minutes'): 60, ('hr', 'hrs', 'hour', 'hours'): 3600}
    _primitive_units['Q'] = {('C', 'coulomb'): 1}
    _primitive_units['Theta'] = {('K', 'kelvin'): 1, ('R', 'rankine'): 5/9}
    
    def __init__(self, dimension = Dimension(), value = None):
        if type(dimension) != Dimension:
            raise PhysicalQuantityError

        self.dimension = dimension
        
        # create the parser if it doesn't exist already. Index by string representation
        dimension_str = dimension.str()
        if dimension_str not in PhysicalQuantity._parsers:
            PhysicalQuantity._parsers[dimension_str] = PhysicalQuantityStringParser(dimension, PhysicalQuantity._primitive_units)
        self._parser = PhysicalQuantity._parsers[dimension_str]
        # choose default units for printing and store if they're not stored already 
        if dimension_str not in PhysicalQuantity._default_units:
            # choose basic units (something that gives a conversion of 1) and the shortest representation
            candidates = [k for (k,v) in self._parser.flat_units_dictionary.iteritems() if v == 1]
            PhysicalQuantity._default_units[dimension_str] = min(candidates, key=len)
        self._default_unit_for_printing = PhysicalQuantity._default_units[dimension_str]
        
        self._amount_in_basic_units = None
        if value is not None:
            if type(value) == str:
                self._amount_in_basic_units = self._parser(value)
            else:
                if self.dimension != value.dimension:
                    raise IncompatibleUnitsError
                self._amount_in_basic_units = value._amount_in_basic_units
        
    def __getitem__(self, key):
        return self._amount_in_basic_units/self._parser.flat_units_dictionary[key]
                
    def __setitem__(self, key, value):
        self._amount_in_basic_units = value*self._parser.flat_units_dictionary[key]
        
    def get_available_units(self):
        return self._parser.flat_units_dictionary.keys()
    
    def __repr__(self):
        unit = self._default_unit_for_printing
        unit_to_print = "" if unit == "1" else " %s" % unit
        return "PhysicalQuantity(%s,'%s%s')" % (repr(self.dimension), repr(self[unit]), unit_to_print)  
                
    def __str__(self):
        unit = self._default_unit_for_printing
        unit_to_print = "" if unit == "1" else " %s" % unit
        return "%g%s" % (self[unit], unit_to_print)  
                
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

    @classmethod
    def get_correct_type(cls, dimension):
        """Return the type that matches "dimension", or else return PhysicalQuantity."""
        dimension_str = str(dimension)
        try:
            return mapping_to_derived_types[dimension_str]
        except KeyError:
            return lambda: PhysicalQuantity(dimension) # create a function that can be called without arguments 
    
    @classmethod
    def register_type(cls):
        dimension_str = str(cls._dim)
        if dimension_str not in mapping_to_derived_types:
            mapping_to_derived_types[dimension_str] = cls
            
    def create_coerced_type(self, other):
        """For some binary operations: the result attempts to be of a derived type if possible,
        first on the left and then on the right. If not possible, then it will be a PhysicalQuantity.
        (This only makes sense for operations that require them to be of the same dimensions.)"""
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError # Type coercion: make sure
        if type(self) != PhysicalQuantity:
            result = type(self)()
        elif type(other) != PhysicalQuantity:
            result = type(other)()
        else:
            result = PhysicalQuantity(self.dimension)
        return result

    def __add__(self, other):
        result = self.create_coerced_type(other)
        result._amount_in_basic_units = self._amount_in_basic_units + other._amount_in_basic_units
        return result
        
    def __sub__(self, other):
        result = self.create_coerced_type(other)
        result._amount_in_basic_units = self._amount_in_basic_units - other._amount_in_basic_units
        return result

    def __mul__(self, other):
        new_dimension = self.dimension*other.dimension
        new_type = self.get_correct_type(new_dimension)
        result = new_type()
        result._amount_in_basic_units = self._amount_in_basic_units*other._amount_in_basic_units
        return result
        
    def __div__(self, other):
        new_dimension = self.dimension/other.dimension
        new_type = self.get_correct_type(new_dimension)
        result = new_type()
        result._amount_in_basic_units = self._amount_in_basic_units/other._amount_in_basic_units
        return result
        
    def __truediv__(self, other):
        new_dimension = self.dimension/other.dimension
        new_type = self.get_correct_type(new_dimension)
        result = new_type()
        result._amount_in_basic_units = self._amount_in_basic_units/other._amount_in_basic_units
        return result
        

class Mass(PhysicalQuantity):
    _dim = Dimension(M = 1)
    def __init__(self, value = None):
        super(Mass, self).__init__(Mass._dim, value)


class Distance(PhysicalQuantity):
    _dim = Dimension(L = 1)
    def __init__(self, value = None):
        super(Distance, self).__init__(Distance._dim, value)
        

class Time(PhysicalQuantity):
    _dim = Dimension(T = 1)
    _hr_in_secs = PhysicalQuantity(_dim, "1 hr")['s']
    _min_in_secs = PhysicalQuantity(_dim, "1 min")['s']

    def __init__(self, value = None):
        super(Time, self).__init__(Time._dim, value)
        
    @property
    def str(self):
        secs = self['s']
        hours = int(secs/Time._hr_in_secs)
        secs = secs - hours*Time._hr_in_secs
        mins = int(secs/Time._min_in_secs)
        secs = int(secs - mins*Time._min_in_secs)
        result = ""
        if hours > 0:
            result = result + str(hours) + ":"
        result = result + '{0:02d}:{1:02d}'.format(mins,secs)
        return result
        

class Temperature(PhysicalQuantity):
    _dim = Dimension(Theta = 1)
    def __init__(self, value = None):    
        super(Temperature, self).__init__(Temperature._dim, value)        

    def __getitem__(self, key):
        if key == 'C':
            K = self._amount_in_basic_units/self._parser.flat_units_dictionary['K']
            return K - 273.15
        elif key == 'F':
            C = self._amount_in_basic_units/self._parser.flat_units_dictionary['K'] - 273.15
            return C*9/5 + 32
        else:
            return super(Temperature, self).__getitem__(key)
            
    def __setitem__(self, key, value):
        if key == 'C':
            self._amount_in_basic_units = (value + 273.15)*self._parser.flat_units_dictionary['K'] 
        elif key == 'F':
            self._amount_in_basic_units = ((value - 32)*5/9 + 273.15)/self._parser.flat_units_dictionary['K']
        else:
            super(Temperature, self).__setitem__(key, value)


# Some important derived quantities        


class Speed(PhysicalQuantity):
    _dim = Dimension(L = 1, T = -1)
    def __init__(self, value = None):    
        super(Speed, self).__init__(Speed._dim, value)
        
    def pace(self, distance):
        """Return time to cover given distance."""
        # Cast is important to make the "str" method available.
        return Time(distance / self)
        
# Initialize by registering all derived types
for derivedclass in [Mass, Distance, Time, Temperature, Speed]:
    derivedclass.register_type()