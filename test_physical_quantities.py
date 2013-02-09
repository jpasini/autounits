from __future__ import division

import unittest
from physical_quantities import PhysicalQuantity, Mass, Distance, Time, Speed, Temperature
from physical_quantities import BadInputError, BadUnitDictionaryError, IncompatibleUnitsError
from dimension import Dimension

class TestAuxiliaryFunctions(unittest.TestCase):
    
    def test_flatten_good_dictionary(self):
        """Test flattening a units dictionary."""
        from physical_quantities import flatten_dictionary
        units_dictionary = {('kg', 'kilogram'): 1, ('g', 'gr', 'gram'): 0.001}
        flat_dictionary = flatten_dictionary(units_dictionary)
        self.assertEqual(flat_dictionary, {'kg': 1, 'kilogram': 1, 'g': 0.001, 'gr': 0.001, 'gram': 0.001})

    def test_flatten_bad_dictionary(self):
        """Flattening a units dictionary with repeats should fail."""
        from physical_quantities import flatten_dictionary
        units_dictionary = {('kg', 'kilogram'): 1, ('g', 'gr', 'kg'): 0.001}
        self.assertRaises(BadUnitDictionaryError, flatten_dictionary, units_dictionary)
        
    def test_parser(self):
        from physical_quantities import PhysicalQuantityStringParser
        primitive_units_dictionaries = {
            'M': {('kg', 'kilogram'): 1, ('g', 'gr', 'gram'): 0.001},
            'L': {('m', 'meter'): 1, 'km': 1000},
            'T': {'s': 1, ('min', 'minute'): 60},
            'Q': {'C': 1 },
            'Theta': {'K': 1} }
        d1 = Dimension(M = 1, L = -2, T = 4, Theta = -1)
        p1 = PhysicalQuantityStringParser(d1, primitive_units_dictionaries)
        self.assertEqual(len(p1.flat_units_dictionary), 5*3*3*1)
        # repeat the same case (should use caching)
        p2 = PhysicalQuantityStringParser(d1, primitive_units_dictionaries)
        self.assertEqual(p1.flat_units_dictionary, p2.flat_units_dictionary)
        d2 = Dimension(T = -1, Q = 1, Theta = -2)
        p3 = PhysicalQuantityStringParser(d2, primitive_units_dictionaries)
        self.assertEqual(p3.flat_units_dictionary, {"C/sK^2": 1, "C/minK^2": 1/60, "C/minuteK^2": 1/60})
        # Check a simple case
        self.assertEqual(p3("60 C/minK^2"), 1)
        self.assertEqual(p3("2.4e-2 C/minK^2"), 4e-4)
        # Bad input should raise an exception 
        self.assertRaises(BadInputError, p3, "60 C/min K^2") # spaces in units
        self.assertRaises(BadInputError, p3, "60.3.2 C/minK^2") # bad number
        

class TestPhysicalQuantity(unittest.TestCase):
    """Test the PhysicalQuantity class."""

    def test_dimensionless_quantity(self):
        """Test dimensionless quantities."""
        d = Dimension()
        # creating
        p = PhysicalQuantity(d)
        # assigning & getting the value. The "unit" is "1": need a better interface.
        p["1"] = 4 
        self.assertEqual(p["1"], 4)
        # creating from a string
        p = PhysicalQuantity(d, "7")
        self.assertEqual(p["1"], 7)
        # creating from a string: trying to use "1" as unit in the string fails
        self.assertRaises(BadInputError, PhysicalQuantity, d, "7 1")
        
    def test_bad_creation(self):
        """Creation with bad inputs should raise exceptions."""
        from physical_quantities import PhysicalQuantityError
        d = 3
        self.assertRaises(PhysicalQuantityError, PhysicalQuantity, d, "3m") # not a dimension
    
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
        
    def test_get_available_units(self):
        """Test that I can get the available units."""
        self.assertEqual(set(PhysicalQuantity(Dimension()).get_available_units()), set(["1"]))
        # test only whether it's a subset, so it doesn't fail as I add more units 
        self.assertTrue(set(["kg", "kilogram", "g", "gram"])
                        <= set(PhysicalQuantity(Dimension(M = 1)).get_available_units()))
        self.assertTrue(set(["m/s", "meters/second", "miles/hour", "mi/hr"])
                        <= set(Speed().get_available_units()))
        
    def test_comparisons(self):
        """All comparisons should be available between quantities of the same type."""
        p1 = PhysicalQuantity(Dimension(L = 1), "2m")
        p2 = PhysicalQuantity(Dimension(L = 1), "2m")
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
        
    def test_repr(self):
        """repr() should give something that can be used to recreate the object."""
        p1 = PhysicalQuantity(Dimension(L = 1), "2m")
        p2 = eval(repr(p1))
        self.assertEqual(p1, p2)
        # special case: dimensionless quantities
        p1 = PhysicalQuantity(Dimension(), "2")
        p2 = eval(repr(p1))
        self.assertEqual(p1, p2)
        # derived quantities should also work
        t1 = Time("3 min")
        t2 = eval(repr(t1))
        self.assertEqual(t1, t2)
        # a more complicated case
        p1 = Speed("30m/s")/Time("2s")/PhysicalQuantity(Dimension(M = 1), "3kg")
        p2 = eval(repr(p1))
        self.assertEqual(p1, p2)

    def test_str(self):
        """str() prints a reasonable form for the quantity."""
        # dimensionless case
        p = PhysicalQuantity(Dimension(), "2.1e2")
        self.assertEqual(str(p), "210")
        # For quantities that are NOT dimensionless we use the "basic unit" (whatever has a unit conversion
        # factor, so it's SI in our case) with the shortest string representation.
        # Also, in both the numerator and denominator the order followed is M L T Q Theta 
        p = Speed("60 km/min")
        self.assertEqual(str(p), "1000 m/s")
        p = PhysicalQuantity(Dimension(Q = 1), "4 coulomb")
        self.assertEqual(str(p), "4 C")
        p = Temperature("4 kelvin")
        self.assertEqual(str(p), "4 K")
        p = Speed("30m/s")/Time("2s")/PhysicalQuantity(Dimension(M = 1), "3kg")
        self.assertEqual(str(p), "5 m/kgs^2")
                
        
# Test primitive quantities
        
class TestMass(unittest.TestCase):
    """Tests for the Mass class."""
    kilograms_in = {'kg' : 1, 'kilograms': 1, 'g': 0.001, 'grams': 0.001 }
        
    def test_create_simple_masses(self):
        """Simple masses."""
        # Check consistency
        for unit,kilograms in self.kilograms_in.iteritems():
            m = Mass('1' + unit) # create "1x" where x is the unit
            self.assertEqual(m['kg'], kilograms) # the kilograms should be correct
        # Check creating from other distances
        m1 = Mass("1 kg")
        m2 = Mass(m1)
        self.assertEqual(m1['kg'], m2['kg'])
        # Check creating from another quantity with same dimensions
        m1 = PhysicalQuantity(Dimension(M = 1), "1 kg")
        m2 = Mass(m1)
        self.assertEqual(m1['kg'], m2['kg'])
        # Check creating from another quantity with different dimensions
        t = PhysicalQuantity(Dimension(T = 1), "1 s")
        self.assertRaises(IncompatibleUnitsError, Mass, t)       
        
            
    def test_consistency(self):
        """In its own units, the value should be 1."""
        for unit in self.kilograms_in.keys():
            m = Mass('1' + unit) # create "1x" where x is the unit
            self.assertEqual(m[unit], 1)
            
    def test_mass_adding(self):
        """Test adding masses."""
        m1 = Mass("10 kg")
        m2 = Mass("300 g")
        m3 = m1 + m2
        self.assertEqual(m1.dimension, m3.dimension) # type is the same
        self.assertEqual(m3['kg'], 10.3)
        
    def test_mass_subtracting(self):
        """Test subtracting masses."""
        m1 = Mass("10 kg")
        m2 = Mass("300 g")
        m3 = m1 - m2
        self.assertEqual(m1.dimension, m3.dimension) # type is the same
        self.assertAlmostEqual(m3['g'], 9700)
        
    def test_for_mass_equality(self):
        """Test that masses are only compared by length."""
        m1 = Mass("1g")
        m2 = Mass("0.001kg")
        self.assertEqual(m1['kg'], m2['kg']) # sanity check before the real test
        self.assertEqual(m1, m2)
        
    def test_creating_from_other_mass(self):
        """I can create a mass from another."""
        m1 = Mass("10 kg")
        m2 = Mass(m1)
        self.assertEqual(m1, m2)
        m2['kg'] = 2
        self.assertEqual(m2['kg'], 2)
        self.assertEqual(m1['kg'], 10) # check that we didn't modify the original one
        

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
        # Check creating from another quantity with different dimensions
        d1 = PhysicalQuantity(Dimension(T = 1), "1 s")
        self.assertRaises(IncompatibleUnitsError, Distance, d1)        
        
            
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


class TestTemperature(unittest.TestCase):
    """Tests for the Temperature class."""
    # kelvin, rankine, celsius, fahrenheit 
    known_values = [
                    [273.15, 491.67, 0, 32],
                    [373.15, 671.67, 100, 212]]
    
    kelvins_in = {'K': 1, 'R': 5/9 }
        
    def test_create_simple_temperatures(self):
        """Simple temperatures."""
        for unit,kelvins in self.kelvins_in.iteritems():
            t = Temperature('1' + unit) # create "1x" where x is the unit
            self.assertEqual(t['K'], kelvins) # the seconds should be correct
            
    def test_consistency(self):
        """In its own units, the value should be 1."""
        for unit in self.kelvins_in.keys():
            t = Temperature('1' + unit) # create "1x" where x is the unit
            self.assertEqual(t[unit], 1)
            
    def test_known_values(self):
        t1 = Temperature()
        t2 = Temperature()
        t3 = Temperature()
        t4 = Temperature()
        for K, R, C, F in self.known_values:
            t1['K'] = K
            self.assertAlmostEqual(t1['K'], K)
            self.assertAlmostEqual(t1['R'], R)
            self.assertAlmostEqual(t1['C'], C)
            self.assertAlmostEqual(t1['F'], F)
            t2['R'] = R
            self.assertAlmostEqual(t2['K'], K)
            self.assertAlmostEqual(t2['R'], R)
            self.assertAlmostEqual(t2['C'], C)
            self.assertAlmostEqual(t2['F'], F)
            t3['C'] = C
            self.assertAlmostEqual(t3['K'], K)
            self.assertAlmostEqual(t3['R'], R)
            self.assertAlmostEqual(t3['C'], C)
            self.assertAlmostEqual(t3['F'], F)
            t4['F'] = F
            self.assertAlmostEqual(t4['K'], K)
            self.assertAlmostEqual(t4['R'], R)
            self.assertAlmostEqual(t4['C'], C)
            self.assertAlmostEqual(t4['F'], F)
            
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
        s1 = d/t # division
        s2 = Speed("2m/s")
        self.assertEqual(s1.dimension, s2.dimension)
        self.assertEqual(s1, s2)
        d2 = s2*t # multiplication
        self.assertEqual(d2, d)
        
        
if __name__ == '__main__':
    unittest.main()
