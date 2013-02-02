"""
physical_quantities.py:
Library of physical quantities, with automatic unit conversion.
"""

from __future__ import division

class PhysicalQuantityError(Exception): pass
class BadInputError(PhysicalQuantityError): pass
class BadUnitDictionaryError(PhysicalQuantityError): pass

class PhysicalQuantityStringParser(object):
    """Object that parses a string representing an amount with units."""
    def __init__(self, units_dictionary):
        """Define a parser based on the given units_dictionary.
        For example, for distances you would use:
        
        units_dictionary = {('m', 'meters'): 1, 'mi': 1609.344}
        
        """
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
                    
        self.flat_units_dictionary = new_dictionary
        
        from pyparsing import Literal, replaceWith, \
            Or, nums, Word, stringEnd, ParseException
        
        def make_literal(unit_string, val):
            return Literal(unit_string).setParseAction(replaceWith(val))
        units = Or( [ make_literal(s,v) for s,v in new_dictionary.iteritems() ] )
        
        def validate_number(tokens):
            try:
                float(tokens[0])
            except ValueError:
                raise ParseException("Invalid number (%s)" % tokens[0])
        number = Word(nums + 'e' + '-' + '+' + '.')
        number.setParseAction(validate_number)
        
        self._dimension = number + units + stringEnd
        
    def __call__(self, quantity_string):
        """Parse the given string."""
        from pyparsing import ParseException
        try:
            a = self._dimension.parseString(quantity_string)
        except ParseException:
            raise BadInputError
        return float(a[0])*a[1]
        
class PhysicalQuantity(object):
    def __init__(self, units_dictionary, value = None):
        self._amount_in_basic_units = None
        self._parser = PhysicalQuantityStringParser(units_dictionary)
        if value is not None:
            if type(value) == str:
                self._amount_in_basic_units = self._parser(value)
            elif type(value) == type(self):
                self._amount_in_basic_units = value._amount_in_basic_units
        
        # Add the getter/setter properties for each unit
        def make_getter(yardstick):
            return lambda s: s._amount_in_basic_units/yardstick
            
        def make_setter(yardstick):
            return lambda s,val: setattr(s,'_amount_in_basic_units', val*yardstick)
            
        for unit_name, yardstick in self._parser.flat_units_dictionary.iteritems():
            getter = make_getter(yardstick)
            setter = make_setter(yardstick)
            setattr(self.__class__, unit_name, property(getter, setter))
                
    def __eq__(self, other):
        """Equality is defined by the type and amount."""
        return type(self) == type(other) and self._amount_in_basic_units == other._amount_in_basic_units
    
    def __add__(self, other):
        result = type(self)() # Derived classes should initialize without arguments
        result._amount_in_basic_units = self._amount_in_basic_units + other._amount_in_basic_units
        return result
        
    def __sub__(self, other):
        result = type(self)() # Derived classes should initialize without arguments
        result._amount_in_basic_units = self._amount_in_basic_units - other._amount_in_basic_units
        return result


class Distance(PhysicalQuantity):
    def __init__(self, value = None):
        # Conversion constants
        meters_in = {('m', 'meters'): 1, ('mi', 'miles'): 1609.344, ('km', 'kilometers'): 1000, 'marathon': 42194.988 }
        PhysicalQuantity.__init__(self, meters_in, value)

class Time(PhysicalQuantity):
    def __init__(self, value = None):
        # Conversion constants
        secs_in = {('s', 'seconds'): 1, ('min', 'minutes'): 60, ('hr', 'hours'): 3600 }
        PhysicalQuantity.__init__(self, secs_in, value)
        
    @property
    def str(self):
        secs = self.s
        h, m = Time("1 hr"), Time("1 min")
        hours = int(secs/h.s)
        secs = secs - hours*h.s
        mins = int(secs/m.s)
        secs = int(secs - mins*m.s)
        result = ""
        if hours > 0:
            result = result + str(hours) + ":"
        result = result + '{0:02d}:{1:02d}'.format(mins,secs)
        return result
        

class Speed(PhysicalQuantity):
    def __init__(self, value = None):
        # Conversion constants
        mps_in = {('mps', 'm/s'): 1, 'mph': Distance('1 mi').m/Time('1 hr').s }
        PhysicalQuantity.__init__(self, mps_in, value)
        
    def pace(self, distance):
        """Return time to cover given distance."""
        t = Time()
        t.s = distance.m/self.mps
        return t
        
