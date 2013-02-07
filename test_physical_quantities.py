from __future__ import division

import unittest
from physical_quantities import PhysicalQuantity, Distance, Time, Speed
from physical_quantities import BadInputError, BadUnitDictionaryError, IncompatibleUnitsError
from dimension import Dimension


class TestPhysicalQuantity(unittest.TestCase):
    """Test the abstract PhysicalQuantity class."""
    
    def test_create_simply_physical_quantity(self):
        """Simple physical quantities."""
        d = Dimension(L = 1)
        p = PhysicalQuantity(d, "3m")
        self.assertEqual(p['m'], 3)
        self.assertEqual(p['meters'], 3)
        self.assertEqual(p['km'], 0.003)
        self.assertEqual(p['kilometers'], 0.003)
        p['km'] = 2
        self.assertEqual(p['m'], 2000)
        self.assertEqual(p['meters'], 2000)
        self.assertEqual(p['km'], 2)
        self.assertEqual(p['kilometers'], 2)
        
    def test_comparisons(self):
        """All comparisons should be available between quantities of the same type."""
        p1 = PhysicalQuantity(Dimension(L=1), "2m")
        p2 = PhysicalQuantity(Dimension(L=1), "2m")
        self.assertTrue(p1 == p2)
        self.assertTrue(p1 >= p2)
        self.assertTrue(p1 <= p2)
        self.assertFalse(p1 != p2)
        self.assertFalse(p1 < p2)
        self.assertFalse(p1 > p2)
        p2['km'] = 1
        self.assertFalse(p1 == p2)
        self.assertFalse(p1 >= p2)
        self.assertTrue(p1 <= p2)
        self.assertTrue(p1 != p2)
        self.assertFalse(p1 > p2)
        self.assertTrue(p1 < p2)
        
# Test primitive quantities
        
class TestDistance(unittest.TestCase):
    """Tests for the Distance class."""
    meters_in = {'m' : 1, 'meters': 1, 'mi': 1609.344, 'miles': 1609.344, 'km': 1000, 'kilometers': 1000, 'marathon': 42194.988 }
        
    def test_create_simple_distances(self):
        """Simple distances."""
        # Check consistency
        for unit,meters in self.meters_in.iteritems():
            d = Distance('1' + unit) # create "1x" where x is the unit
            self.assertEqual(d['m'], meters) # the meters should be correct
        # Check creating from other distances
        d1 = Distance("1 m")
        d2 = Distance(d1)
        self.assertEqual(d1['m'], d2['m'])
        # Check creating from another quantity with same dimensions
        d1 = PhysicalQuantity(Dimension(L = 1), "1 m")
        d2 = Distance(d1)
        self.assertEqual(d1['m'], d2['m'])
        
            
    def test_consistency(self):
        """In its own units, the value should be 1."""
        for unit in self.meters_in.keys():
            d = Distance('1' + unit) # create "1x" where x is the unit
            self.assertEqual(d[unit], 1)
            
    def test_distance_adding(self):
        """Test adding distances."""
        d1 = Distance("10 m")
        d2 = Distance("3 km")
        d3 = d1 + d2
        self.assertEqual(d1.dimension, d3.dimension) # type is the same
        self.assertEqual(d3['m'], 3010)
        
    def test_distance_subtracting(self):
        """Test subtracting distances."""
        d1 = Distance("10 m")
        d2 = Distance("3 km")
        d3 = d2 - d1
        self.assertEqual(d1.dimension, d3.dimension) # type is the same
        self.assertEqual(d3['m'], 2990)
        
    def test_for_distance_equality(self):
        """Test that distances are only compared by length."""
        d1 = Distance("1m")
        d2 = Distance("0.001km")
        self.assertEqual(d1['m'], d2['m']) # sanity check before the real test
        self.assertEqual(d1, d2)
        
    def test_creating_from_other_distance(self):
        """I can create a distance from another."""
        d1 = Distance("10 m")
        d2 = Distance(d1)
        self.assertEqual(d1, d2)
        d2['m'] = 2
        self.assertEqual(d2['m'], 2)
        self.assertEqual(d1['m'], 10)
        
class TestTime(unittest.TestCase):
    """Tests for the Time class."""
    seconds_in = {'s': 1, 'seconds': 1, 'min': 60, 'minutes': 60, 'hr': 3600, 'hours': 3600 }
        
    def test_create_simple_times(self):
        """Simple times."""
        for unit,seconds in self.seconds_in.iteritems():
            t = Time('1' + unit) # create "1x" where x is the unit
            self.assertEqual(t['s'], seconds) # the seconds should be correct
            
    def test_consistency(self):
        """In its own units, the value should be 1."""
        for unit in self.seconds_in.keys():
            t = Time('1' + unit) # create "1x" where x is the unit
            self.assertEqual(t[unit], 1)
            
    def test_string_output(self):
        """Test time output in string format."""
        t = Time("1 min")
        self.assertEqual(t.str, "01:00")
        t = Time("60 s")
        self.assertEqual(t.str, "01:00")
        t = Time("3661 s")
        self.assertEqual(t.str, "1:01:01")
        t = Time("0.1 s")
        self.assertEqual(t.str, "00:00")
        
# Test derived quantities
    
class TestSpeed(unittest.TestCase):
    """Tests for the Speed class."""
        
    def test_simple_speeds(self):
        """Create a few speeds and check the value."""
        s = Speed('1 mi/hr')
        self.assertEqual(s['mi/hr'], 1)
        s['miles/hr'] = 2.5
        self.assertEqual(s['mi/hr'], 2.5)
        self.assertEqual(s['m/s'], 2.5*Distance('1mi')['m']/Time('1hr')['s'])

    def test_check_known_pace(self):
        """Check pace for some speeds."""
        # speed, distance for pace, pace
        known_values = [
                        ['1 m/s', '1 km', '1000s'],
                        ['1 meters/s', '1 km', '1000s'],
                        ['1 mi/hr', '1 mi', '1 hr']
                        ]
        for speed, distance, pace in known_values:
            s, d, t = Speed(speed), Distance(distance), Time(pace)
            self.assertEqual(s.pace(d)['s'], t['s']) # the seconds should be correct


class TestCombinedDimensions(unittest.TestCase):
    """Test combinations of units."""
    
    def test_comparison_of_combined_units(self):
        d = Distance("10m")
        t = Time("5s")
        self.assertFalse(d.dimension == t.dimension)
        self.assertRaises(IncompatibleUnitsError, d.__lt__, t)
        self.assertRaises(IncompatibleUnitsError, d.__gt__, t)
        self.assertRaises(IncompatibleUnitsError, d.__le__, t)
        self.assertRaises(IncompatibleUnitsError, d.__ge__, t)
        
    def test_addition_and_subtraction_of_combined_units(self):
        d = Distance("10m")
        t = Time("5s")
        self.assertRaises(IncompatibleUnitsError, d.__add__, t)
        self.assertRaises(IncompatibleUnitsError, d.__sub__, t)
        
    def test_multiplication_and_division_of_combined_units(self):
        d = Distance("10m")
        t = Time("5s")
        s1 = d/t
        s2 = Speed("2m/s")
        self.assertEqual(s1.dimension, s2.dimension)
        self.assertEqual(s1, s2)
        
        
if __name__ == '__main__':
    unittest.main()
