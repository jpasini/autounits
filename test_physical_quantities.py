from __future__ import division

import unittest
from physical_quantities import Distance

class TestDistances(unittest.TestCase):
    """Tests for the Distance class."""

    def test_create_simple_distances(self):
        """Simple distances."""
        meters_in = {
            'm' : 1,
            'mi': 1609.344, 
            'km': 1000, 
            'marathon': 42194.988 }
        
        for k,v in meters_in.iteritems():
            print '1'+k
            d = Distance('1' + k) # create "1x" where x is the unit
            self.assertEqual(d.m, v) # the meters should correct
        

