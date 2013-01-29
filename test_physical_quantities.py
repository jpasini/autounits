from __future__ import division

import unittest
from physical_quantities import Distance, Time, Speed, PhysicalQuantityStringParser


class TestQuantityStringParser(unittest.TestCase):
    """Tests for the string parser for physical quantities."""
    
    def test_simple_parser(self):
        meters_in = {'m' : 1, 'meter': 1, 'km': 1000}
        p = PhysicalQuantityStringParser(meters_in)
        # The results are in meters because that was the basic unit.
        self.assertEqual(p('1 m'), 1)
        self.assertEqual(p('2 meter'), 2)
        self.assertEqual(p('4 meters'), 4)
        self.assertEqual(p('4 meterswhatever else'), 4) # ignores tail
        self.assertEqual(p('2Km'), 2000)
        self.assertEqual(p('0.1 kms'), 100)


class TestDistance(unittest.TestCase):
    """Tests for the Distance class."""
    meters_in = {'m' : 1, 'mi': 1609.344, 'km': 1000, 'marathon': 42194.988 }
        
    def test_create_simple_distances(self):
        """Simple distances."""
        for unit,meters in self.meters_in.iteritems():
            d = Distance('1' + unit) # create "1x" where x is the unit
            self.assertEqual(d.m, meters) # the meters should be correct
            
    def test_consistency(self):
        """In its own units, the value should be 1."""
        for unit in self.meters_in.keys():
            d = Distance('1' + unit) # create "1x" where x is the unit
            evaluate_in_own_units = getattr(d, unit)
            self.assertEqual(evaluate_in_own_units, 1)
        

class TestTime(unittest.TestCase):
    """Tests for the Time class."""
    seconds_in = {'s' : 1, 'min': 60, 'hr': 3600 }
        
    def test_create_simple_times(self):
        """Simple times."""
        for unit,seconds in self.seconds_in.iteritems():
            t = Time('1' + unit) # create "1x" where x is the unit
            self.assertEqual(t.s, seconds) # the seconds should be correct
            
    def test_consistency(self):
        """In its own units, the value should be 1."""
        for unit in self.seconds_in.keys():
            t = Time('1' + unit) # create "1x" where x is the unit
            evaluate_in_own_units = getattr(t, unit)
            self.assertEqual(evaluate_in_own_units, 1)
        
        
class TestSpeed(unittest.TestCase):
    """Tests for the Speed class."""
    # speed, distance for pace, pace
    known_values = [
        ['1 mps', '1 km', '1000s'],
        ['1 mph', '1 mi', '1 hr']
        ]
        
    def test_simle_speeds(self):
        """Create a few speeds and check the value."""
        s = Speed('1 mph')
        self.assertEqual(s.mph, 1)
        s.mph = 2.5
        self.assertEqual(s.mph, 2.5)
        self.assertEqual(s.mps, 2.5*Distance('1mi').m/Time('1hr').s)

    def test_check_known_pace(self):
        """Check pace for some speeds."""
        for speed, distance, pace in self.known_values:
            s, d, t = Speed(speed), Distance(distance), Time(pace)
            self.assertEqual(s.pace(d).s, t.s) # the seconds should be correct
                    

if __name__ == '__main__':
    unittest.main()
