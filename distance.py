from __future__ import division

class Distance(object):
    def __init__(self, distance_string = None):
        self._meters = None
        # Conversion constants
        self._meters_in = {
            'mi': 1609.344, 
            'km': 1000, 
            'marathon': 42194.988 }
        if distance_string is not None:
            self._meters = self.distance_from_string(distance_string)
        
    def distance_from_string(self, distance_string):
        '''Define a grammar to get the distance from the given string.
        Examples: .3m, 10mi, 0.7marathons, 5 m, 2 km, 6 Km, 8 miles, etc.
        '''
        from pyparsing import CaselessLiteral, replaceWith, Or, nums, Word
        
        def makeLit(s, val):
            ret = CaselessLiteral(s).setName(s)
            return ret.setParseAction(replaceWith(val))
            
        unitDefinitions = [
            ('m', 1),
            ('km', 1000),
            ('mi', 1609.344),
            ('marathon', 42194.988),
            ]        
        units = Or( [ makeLit(s,v) for s,v in unitDefinitions ] )
        number = Word(nums + '.')
        dimension = number + units
        a = dimension.parseString(distance_string)
        return float(a[0])*a[1]
        

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

