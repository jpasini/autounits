"""
physical_quantities.py:
Library of physical quantities, with automatic unit conversion.
"""

from __future__ import division


class PhysicalQuantityStringParser(object):
    """Object that parses a string representing an amount with units."""
    def __init__(self, units_dictionary):
        """Define a parser based on the given units_dictionary.
        For example, for distances you would use:
        
        units_dictionary = {'m': 1, 'mi': 1609.344}
        
        Note that the unit associated with "1" would be the basic unit.
        """
        from pyparsing import CaselessLiteral, replaceWith, Or, nums, Word
        
        def makeLit(s, val):
            ret = CaselessLiteral(s).setName(s)
            return ret.setParseAction(replaceWith(val))
            
        unitDefinitions = [(k,v) for k,v in units_dictionary.iteritems()]
        units = Or( [ makeLit(s,v) for s,v in unitDefinitions ] )
        number = Word(nums + '.')
        self._dimension = number + units
        
    def __call__(self, quantity_string):
        """Parse the given string."""
        a = self._dimension.parseString(quantity_string)
        return float(a[0])*a[1]
        

class Distance(object):
    def __init__(self, distance_string = None):
        self._meters = None
        # Conversion constants
        self._meters_in = {'m': 1, 'mi': 1609.344, 'km': 1000, 'marathon': 42194.988 }
        self._parser = PhysicalQuantityStringParser(self._meters_in)
        if distance_string is not None:
            self._meters = self._parser(distance_string)
        
    @property
    def m(self):
        '''Distance in meters.'''
        return self._meters
        
    @m.setter
    def m(self, value):
        self._meters = value
        
    @property
    def mi(self):
        '''Distance in miles.'''
        return self._meters/self._meters_in['mi']
        
    @mi.setter
    def mi(self, value):
        self._meters = value*self._meters_in['mi']
        
    @property
    def km(self):
        '''Distance in km.'''
        return self._meters/self._meters_in['km']
        
    @km.setter
    def km(self, value):
        self._meters = value*self._meters_in['km']
        
    @property
    def marathon(self):
        '''Distance in marathons.'''
        return self._meters/self._meters_in['marathon']
        
    @marathon.setter
    def marathon(self, value):
        self._meters = value*self._meters_in['marathon']


class Time(object):
    def __init__(self, time_string = None):
        self._secs = None
        # Conversion constants
        self._secs_in = {'s': 1, 'min': 60, 'hr': 3600 }
        self._parser = PhysicalQuantityStringParser(self._secs_in)
        if time_string is not None:
            self._secs = self._parser(time_string)
        
    @property
    def s(self):
        '''Time in seconds.'''
        return self._secs
        
    @s.setter
    def s(self, value):
        self._secs = value
        
    @property
    def min(self):
        '''Time in minutes.'''
        return self._secs/self._secs_in['min']
        
    @min.setter
    def min(self, value):
        self._secs = value*self._secs_in['min']
        
    @property
    def hr(self):
        '''Time in hours.'''
        return self._secs/self._secs_in['hr']
               
    @hr.setter
    def hr(self, value):
        self._secs = value*self._secs_in['hr']
        
    @property
    def str(self):
        secs = self._secs
        hours = int(secs/self._secs_in['hr'])
        secs = secs - hours*self._secs_in['hr']
        mins = int(secs/self._secs_in['min'])
        secs = int(secs - mins*self._secs_in['min'])
        result = ""
        if hours > 0:
            result = result + str(hours) + ":"
        result = result + '{0:02d}:{1:02d}'.format(mins,secs)
        return result


class Speed(object):
    def __init__(self, speed_string = None):
        self._mps = None # store internally in meters/sec
        # Conversion constants
        self._mps_in = {'mps': 1, 'mph': Distance('1 mi').m/Time('1 hr').s }
        self._parser = PhysicalQuantityStringParser(self._mps_in)
        if speed_string is not None:
            self._mps = self._parser(speed_string)
        
    @property
    def mps(self):
        '''Speed in meters/second.'''
        return self._mps
        
    @mps.setter
    def mps(self, value):
        self._mps = value
        
    @property
    def mph(self):
        '''Speed in miles per hour.'''
        return self._mps/self._mps_in['mph']
        
    @mph.setter
    def mph(self, value):
        self._mps = value*self._mps_in['mph']
        
    def pace(self, distance):
        '''Return time to cover given distance.'''
        t = Time()
        t.s = distance.m/self.mps
        return t
        
