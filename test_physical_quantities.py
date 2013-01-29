from __future__ import division

import unittest
from physical_quantities import Distance

class TestDistances(unittest.TestCase):
    """Tests for the Distance class."""
    meters_in = {
        'm' : 1,
        'mi': 1609.344, 
        'km': 1000, 
        'marathon': 42194.988 }
        
    def test_create_simple_distances(self):
        """Simple distances."""
        for unit,meters in self.meters_in.iteritems():
            d = Distance('1' + unit) # create "1x" where x is the unit
            self.assertEqual(d.m, meters) # the meters should be correct
            
    def test_consistency(self):
        """In its own units, the value should be 1."""
        for unit,meters in self.meters_in.iteritems():
            d = Distance('1' + unit) # create "1x" where x is the unit
            evaluate_in_own_units = getattr(d, unit)
            self.assertEqual(evaluate_in_own_units, 1)
        

if __name__ == '__main__':
    unittest.main()
