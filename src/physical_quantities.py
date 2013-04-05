"""
physical_quantities.py:
Library of physical quantities, with automatic unit conversion.
"""

from __future__ import division

from numbers import Number

class PhysicalQuantityError(Exception): pass
class BadInputError(PhysicalQuantityError): pass
class BadUnitDictionaryError(PhysicalQuantityError): pass
class IncompatibleUnitsError(PhysicalQuantityError): pass

from dimension import Dimension, parse_unit_string

def flatten_dictionary(units_dictionary):
    """Units dictionaries include synonyms for units, defined in a nested way to avoid repeating,
    as in this example:
    
        d = {('kg', 'kilogram'): 1, ('g', 'gr'): 0.001, 'ton': 1000}
    The flat version would be  
        flat_d = {'kg': 1, 'kilogram': 1, 'g': 0.001, 'gr': 0.001, 'ton': 1000}
        
    This means there could be a name clash in the keys after flattening. If that's the case, we
    raise an exception.
    """
    # Make sure there are no name clashes in the units
    from itertools import chain, ifilter
    units = units_dictionary.keys()
    tuples     = list(ifilter(lambda x: type(x) == tuple, units)) # find tuples
    not_tuples = list(ifilter(lambda x: type(x) != tuple, units))
    flattened_tuples = list(chain(*tuples))
    # join
    rejoined = flattened_tuples + not_tuples
    flattened_keys = set(rejoined)
    name_clash_detected = (len(flattened_keys) != len(rejoined))
    if name_clash_detected:
        raise BadUnitDictionaryError
            
    # At this point there are no name clashes, so flatten
    flattened_dictionary = dict()
    for unit, conversion_factor in units_dictionary.iteritems():
        # units may come along or in tuples associated with the same conversion factor
        if type(unit) != tuple:
            flattened_dictionary[unit] = conversion_factor
        else:
            for u in unit:
                flattened_dictionary[u] = conversion_factor
    return flattened_dictionary


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

        
        d = {}
        for k,v in primitive_units_dictionaries.iteritems():
            d[k] = flatten_dictionary(v)
        
        pattern = dimension.str(use_braces = True)
        # go systematically through all primitive unit-set combinations
        from itertools import product        
        p = list(product(d['M'].keys(), d['L'].keys(), d['T'].keys(), d['Q'].keys(), d['Theta'].keys()))
        new_dictionary = {}
        for units in p:
            # 1. generate the string representing the units (e.g, "m/s^2")
            # 1a. Generate mapping, such as {'M': 'kg', 'L': 'mile', etc.}
            units_string_dictionary = dict(zip(['M','L','T','Q','Theta'], units))
            # 1b. Replace the unit in the dimension string: '{M}{L}^2' --> 'kgmile^2'
            unit_string = pattern.format(**units_string_dictionary)
            # the string could be repeated at this stage if the target quantity
            # has only limited dimensions. For example, if the dimension is ML^2,
            # we'll get the same string when we cycle over possible units for T
            if unit_string in new_dictionary.keys(): continue
            # 2. Find the conversion factor for this specific set of units
            # 2a. Prepare a dictionary with the conversion factors for this set of units   
            unit_values = [d[k][units_string_dictionary[k]] for k in ['M','L','T','Q','Theta']]
            units_value_dictionary = dict(zip(['M','L','T','Q','Theta'], unit_values))
            # 2b. Use the Dimension parser to get the conversion factor
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

from functools import total_ordering

# mapping from dimension strings to derived types
_mapping_to_derived_types = {}

class PhysicalQuantityFactory(object):
    """Factory for PhysicalQuantity objects."""

    @staticmethod    
    def new(dimension, value = None):
        dimension_str = str(dimension)
        if dimension_str not in _mapping_to_derived_types:
            return PhysicalQuantity(dimension, value)
        else:
            return _mapping_to_derived_types[dimension_str](value)
        
# Notes:
# PhysicalQuantity mixes two concepts: (it does too much!)
# - It's a physical quantity, but embedded within it is a system of units.
# - I might be better off creating a separate system of units which is used by physical quantities.

# Once I add a unit for a derived quantity, such as J for energy, the system should allow me
# to use it in combination with primitive units.
# For example, Power may be in W, but I should be able to specify it in J/s, even though
# J was associated later with energy and is not a "primitive" unit. This means that the
# system of units should have a way of incorporating new units to the primitive set.

# For example, given this primitive set
#    _primitive_units['M'] = {('kg', 'kilogram'): 1, ('g', 'gr'): 0.001}
#    _primitive_units['L'] = {('m', 'meter'): 1, ('km', 'kilometer'): 1000}
#    _primitive_units['T'] = {('s'): 1}
#    _primitive_units['Q'] = {('C'): 1}
#    _primitive_units['Theta'] = {('K'): 1}
# After I add that 1 J = 1 kg m^2/s^2 I now also have these identities
#     1 kg = 1 J s^2/m^2 
#     1 m  = 1 J^(1/2) s/kg^(1/2) 
# and so I could have
#    _primitive_units['M'] = {('kg', 'kilogram', 'J s^2/m^2'): 1, ('g', 'gr'): 0.001, ('J s^2/km^2'): 1e-6}
#    _primitive_units['L'] = {('m', 'meter', 'J^(1/2) s/kg^(1/2)'): 1, ('km', 'kilometer'): 1000, ('J^(1/2) s/g^(1/2)'): 1000**0.5}
#    _primitive_units['T'] = {('s'): 1}
#    _primitive_units['Q'] = {('C'): 1}
#    _primitive_units['Theta'] = {('K'): 1}
# One problem now is that the new "primitive units" are no longer simple tokens.
# A possible solution would be to expand the unit system, but add equivalences.
# In other words, I could add this:
#    _derived_units['E'] = {('J', 'Joule'}: 1, ('Btu'): 1055.05585}
# together with the dimensional equivalence
#    _dimension['E'] = Dimension(M = 1, L = 2, T = -2)

class UnitSystem(object):
    
    def __init__(self):
        # For caching:
        self._parsers = {}
        self._default_units = {}
        # Conversion constants for primitive quantities
        self._primitive_units = {}
        self._primitive_units['M'] = {('kg', 'kilogram', 'kilograms'): 1, ('g', 'gr', 'gram', 'grams'): 0.001}
        self._primitive_units['L'] = {('m', 'meter', 'meters'): 1, ('mi', 'mile', 'miles'): 1609.344, ('km', 'kilometer', 'kilometers'): 1000, 'marathon': 42194.988}
        self._primitive_units['T'] = {('s', 'sec', 'secs', 'second', 'seconds'): 1, ('min', 'mins', 'minute', 'minutes'): 60, ('hr', 'hrs', 'hour', 'hours'): 3600}
        self._primitive_units['Q'] = {('C', 'coulomb'): 1}
        self._primitive_units['Theta'] = {('K', 'kelvin'): 1, ('R', 'rankine'): 5/9}
    
    def register_if_not_there(self, dimension):
        """Register this dimension in the unit system if it's not there already."""
        if type(dimension) != Dimension:
            raise PhysicalQuantityError
        
        # create the parser if it doesn't exist already. Index by string representation
        dimension_str = dimension.str()
        if dimension_str not in self._parsers:
            self._parsers[dimension_str] = PhysicalQuantityStringParser(dimension, self._primitive_units)
            
        # choose default units for printing and store if they're not stored already 
        if dimension_str not in self._default_units:
            # choose basic units (something that gives a conversion of 1) and the shortest representation
            candidates = [k for (k,v) in self._parsers[dimension_str].flat_units_dictionary.iteritems() if v == 1]
            self._default_units[dimension_str] = min(candidates, key=len)
            
    def get_conversion_factor(self, dimension, unit):
        """Return the conversion factor from the given unit into 'native' units
        for a quantity of the given Dimension.
        For example, if kg is the 'native' unit of mass, then
        get_conversion_factor(Dimension(M=1), 'g') == 0.001
        because that's the factor to convert from g to kg"""
        return self._parsers[dimension.str()].flat_units_dictionary[unit]
    
    def get_available_units(self, dimension):
        return self._parsers[dimension.str()].flat_units_dictionary.keys()
        
_unit_system = UnitSystem()

@total_ordering
class PhysicalQuantity(object):
    
    def __init__(self, dimension = Dimension(), value = None):
        """Initialization value may be either a string (to be parsed)
        or another object of the same dimensions."""
        if type(dimension) != Dimension:
            raise PhysicalQuantityError
        
        _unit_system.register_if_not_there(dimension)
        self._default_unit_for_printing = _unit_system._default_units[dimension.str()]

        self.dimension = dimension
        
        self._amount_in_basic_units = None
        if value is not None:
            if type(value) == str:
                self._amount_in_basic_units = _unit_system._parsers[dimension.str()](value)
            else:
                if self.dimension != value.dimension:
                    raise IncompatibleUnitsError
                self._amount_in_basic_units = value._amount_in_basic_units
        
    def __getitem__(self, unit):
        return self._amount_in_basic_units/_unit_system.get_conversion_factor(self.dimension, unit)
                
    def __setitem__(self, unit, value):
        self._amount_in_basic_units = value*_unit_system.get_conversion_factor(self.dimension, unit)
        
    def get_available_units(self):
        return _unit_system.get_available_units(self.dimension)
    
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
    def register_type(cls):
        """Register this class as the one to use when creating objects of these dimensions.
        (To be called by derived classes)"""
        dimension_str = str(cls._dim)
        if dimension_str not in _mapping_to_derived_types:
            _mapping_to_derived_types[dimension_str] = cls
            
    def __add__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError
        result = PhysicalQuantityFactory().new(self.dimension)
        result._amount_in_basic_units = self._amount_in_basic_units + other._amount_in_basic_units
        return result
        
    def __radd__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError
        result = PhysicalQuantityFactory().new(self.dimension)
        result._amount_in_basic_units = self._amount_in_basic_units + other._amount_in_basic_units
        return result
        
    def __sub__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError
        result = PhysicalQuantityFactory().new(self.dimension)
        result._amount_in_basic_units = self._amount_in_basic_units - other._amount_in_basic_units
        return result

    def __rsub__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError
        result = PhysicalQuantityFactory().new(self.dimension)
        result._amount_in_basic_units = other._amount_in_basic_units - self._amount_in_basic_units 
        return result

    def __mul__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = self.dimension*other.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = self._amount_in_basic_units*other._amount_in_basic_units
        return result
        
    def __rmul__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = self.dimension*other.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = self._amount_in_basic_units*other._amount_in_basic_units
        return result
        
    def __div__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = self.dimension/other.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = self._amount_in_basic_units/other._amount_in_basic_units
        return result
        
    def __rdiv__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = other.dimension/self.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = other._amount_in_basic_units/self._amount_in_basic_units
        return result
        
    def __truediv__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = self.dimension/other.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = self._amount_in_basic_units/other._amount_in_basic_units
        return result

    def __rtruediv__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = other.dimension/self.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = other._amount_in_basic_units/self._amount_in_basic_units
        return result


class Dimensionless(PhysicalQuantity):
    _dim = Dimension()
    def __init__(self, value = None):
        super(Dimensionless, self).__init__(Dimensionless._dim, value)


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


class Charge(PhysicalQuantity):
    _dim = Dimension(Q = 1)
    def __init__(self, value = None):
        super(Charge, self).__init__(Charge._dim, value)        
        

class Temperature(PhysicalQuantity):
    """Temperature: need to add some conversions that are not just factors."""
    _dim = Dimension(Theta = 1)
    def __init__(self, value = None):    
        super(Temperature, self).__init__(Temperature._dim, value)        

    def __getitem__(self, unit):
        if unit == 'C':
            K = self._amount_in_basic_units/_unit_system.get_conversion_factor(self._dim, 'K')
            return K - 273.15
        elif unit == 'F':
            C = self._amount_in_basic_units/_unit_system.get_conversion_factor(self._dim, 'K') - 273.15
            return C*9/5 + 32
        else:
            return super(Temperature, self).__getitem__(unit)
            
    def __setitem__(self, unit, value):
        if unit == 'C':
            self._amount_in_basic_units = (value + 273.15)*_unit_system.get_conversion_factor(self._dim, 'K') 
        elif unit == 'F':
            self._amount_in_basic_units = ((value - 32)*5/9 + 273.15)/_unit_system.get_conversion_factor(self._dim, 'K')
        else:
            super(Temperature, self).__setitem__(unit, value)


# Some important derived quantities        


class Speed(PhysicalQuantity):
    _dim = Dimension(L = 1, T = -1)
    def __init__(self, value = None):    
        super(Speed, self).__init__(Speed._dim, value)
        
    def pace(self, distance):
        """Return time to cover given distance."""
        return distance / self
    

class Energy(PhysicalQuantity):
    """Energy: Need to define additional synonyms."""
    
    _dim = Dimension(M = 1, L = 2, T = -2)
    _Btu_2_J = 1055.05585
    
    def __init__(self, value = None):    
        super(Energy, self).__init__(Energy._dim, value)
        
    def __getitem__(self, unit):
        if unit == 'J':
            return self._amount_in_basic_units/_unit_system.get_conversion_factor(self._dim, 'kgm^2/s^2')
        elif unit == 'Btu':
            return self._amount_in_basic_units/_unit_system.get_conversion_factor(self._dim, 'kgm^2/s^2')/self._Btu_2_J
        else:
            return super(Energy, self).__getitem__(unit)
            
    def __setitem__(self, unit, value):
        if unit == 'J':
            self._amount_in_basic_units = value*_unit_system.get_conversion_factor(self._dim, 'kgm^2/s^2') 
        elif unit == 'Btu':
            self._amount_in_basic_units = value/_unit_system.get_conversion_factor(self._dim, 'kgm^2/s^2')*self._Btu_2_J
        else:
            super(Energy, self).__setitem__(unit, value)


    
# Initialize by registering all derived types
for derivedclass in [Dimensionless, Mass, Distance, Time, Charge, Temperature, Speed, Energy]:
    derivedclass.register_type()