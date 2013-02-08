from __future__ import division

import unittest
from dimension import Dimension, parse_unit_string
from dimension import DimensionError, IncompatibleDimensionsError


class TestDimension(unittest.TestCase):
    """Test the Dimension class."""
    
    def test_create_dimension(self):
        """Simple Dimension objects."""
        # default: dimensionless
        d1 = Dimension()
        self.assertEqual(d1.M, 0) # mass
        self.assertEqual(d1.L, 0) # length
        self.assertEqual(d1.T, 0) # time
        self.assertEqual(d1.Q, 0) # electric charge
        self.assertEqual(d1.Theta, 0) # absolute temperature
        # any omitted dimensions are zero
        d2 = Dimension(L = 1, T = 2, M = -1)
        self.assertEqual(d2.M, -1)
        self.assertEqual(d2.L, 1)
        self.assertEqual(d2.T, 2)
        self.assertEqual(d2.Q, 0)
        self.assertEqual(d2.Theta, 0)
        
    def test_repr(self):
        """Test that I can use repr() to recreate a Dimension object."""
        d1 = Dimension()
        d2 = eval(repr(d1))
        self.assertEqual(d1, d2)
        # a time with a long representation
        d1 = Dimension(T = 1/3)
        d2 = eval(repr(d1))
        self.assertEqual(d1, d2)
        
    def test_str(self):
        """Test __str__()for a Dimension object."""
        self.assertEqual(str(Dimension()), "1")
        self.assertEqual(str(Dimension(M = 1)), "M")
        self.assertEqual(str(Dimension(L = 1)), "L")
        self.assertEqual(str(Dimension(T = 1)), "T")
        self.assertEqual(str(Dimension(Q = 1)), "Q")
        self.assertEqual(str(Dimension(Theta = 1)), "Theta")
        self.assertEqual(str(Dimension(M = 2)), "M^2")
        self.assertEqual(str(Dimension(L = 1, T = 1)), "LT")
        self.assertEqual(str(Dimension(L = 1, T = -1)), "L/T")
        self.assertEqual(str(Dimension(T = -1)), "1/T")
        self.assertEqual(str(Dimension(T = -0.5)), "1/T^0.5")
        self.assertEqual(str(Dimension(L = 1, T = -0.5)), "L/T^0.5")
        self.assertEqual(str(Dimension(M = 2, L = 1, T = -0.5)), "M^2L/T^0.5")
        self.assertEqual(str(Dimension(M = -2, L = 1, T = -0.5)), "L/M^2T^0.5")        
        
    def test_create_from_other_dimension(self):
        """Create dimensions from other dimensions."""
        d1 = Dimension(L = 1, T = -1)
        d2 = Dimension(d1)
        self.assertEqual(d2.M, 0)
        self.assertEqual(d2.L, 1)
        self.assertEqual(d2.T, -1)
        self.assertEqual(d2.Q, 0)
        self.assertEqual(d2.Theta, 0)
        
    def test_create_with_bad_input(self):
        """Create dimensions with bad inputs."""
        d1 = Dimension(L = 1, T = -1)
        # too many arguments
        self.assertRaises(DimensionError, Dimension, d1, d1)
        # if only one positional argument, it should be a dimension
        self.assertRaises(DimensionError, Dimension, 4)
        # if dimension given, nothing else should be there
        self.assertRaises(DimensionError, Dimension, d1, L=1)
        # Keyword arguments should only be in L,M,T,Q,Theta
        self.assertRaises(DimensionError, Dimension, L=1,s=2)
        
    def test_for_primitive_dimension(self):
        """Some dimensions may be 'primitive'."""
        # Primitive dimensions
        self.assertTrue(Dimension().is_primitive()) # convention: dimensionless is primitive
        self.assertTrue(Dimension(M=1).is_primitive())
        self.assertTrue(Dimension(L=1).is_primitive())
        self.assertTrue(Dimension(T=1).is_primitive())
        self.assertTrue(Dimension(Q=1).is_primitive())
        self.assertTrue(Dimension(Theta=1).is_primitive())
        # Derived dimensions
        self.assertFalse(Dimension(M=2).is_primitive())
        self.assertFalse(Dimension(L=1,T=1).is_primitive())
        self.assertFalse(Dimension(L=1,T=-1).is_primitive())
        self.assertFalse(Dimension(T=-1).is_primitive())
        
    def test_string_representation(self):
        """Check that they appear in the order M L T Q Theta in either the numerator and denominator."""
        self.assertEqual(Dimension().str(), "1")
        self.assertEqual(Dimension(M = 1).str(), "M")
        self.assertEqual(Dimension(L = 1).str(), "L")
        self.assertEqual(Dimension(T = 1).str(), "T")
        self.assertEqual(Dimension(Q = 1).str(), "Q")
        self.assertEqual(Dimension(Theta = 1).str(), "Theta")
        self.assertEqual(Dimension(M = 2).str(), "M^2")
        self.assertEqual(Dimension(L = 1, T = 1).str(), "LT")
        self.assertEqual(Dimension(L = 1, T = -1).str(), "L/T")
        self.assertEqual(Dimension(T = -1).str(), "1/T")
        self.assertEqual(Dimension(T = -0.5).str(), "1/T^0.5")
        self.assertEqual(Dimension(L = 1, T = -0.5).str(), "L/T^0.5")
        self.assertEqual(Dimension(M = 2, L = 1, T = -0.5).str(), "M^2L/T^0.5")
        self.assertEqual(Dimension(M = -2, L = 1, T = -0.5).str(), "L/M^2T^0.5")
        # version with braces 
        self.assertEqual(Dimension().str(use_braces = True), "1")
        self.assertEqual(Dimension(M = 1).str(use_braces = True), "{M}")
        self.assertEqual(Dimension(L = 1).str(use_braces = True), "{L}")
        self.assertEqual(Dimension(T = 1).str(use_braces = True), "{T}")
        self.assertEqual(Dimension(Q = 1).str(use_braces = True), "{Q}")
        self.assertEqual(Dimension(Theta = 1).str(use_braces = True), "{Theta}")
        self.assertEqual(Dimension(M = 2).str(use_braces = True), "{M}^2")
        self.assertEqual(Dimension(L = 1, T = 1).str(use_braces = True), "{L}{T}")
        self.assertEqual(Dimension(L = 1, T = -1).str(use_braces = True), "{L}/{T}")
        self.assertEqual(Dimension(T = -1).str(use_braces = True), "1/{T}")
        self.assertEqual(Dimension(T = -0.5).str(use_braces = True), "1/{T}^0.5")
        self.assertEqual(Dimension(L = 1, T = -0.5).str(use_braces = True), "{L}/{T}^0.5")
        self.assertEqual(Dimension(M = 2, L = 1, T = -0.5).str(use_braces = True), "{M}^2{L}/{T}^0.5")
        self.assertEqual(Dimension(M = -2, L = 1, T = -0.5).str(use_braces = True), "{L}/{M}^2{T}^0.5")
    
    def test_parsing_elements(self):
        from dimension import get_number
        from pyparsing import ParseException
        n = get_number()
        self.assertEqual(n.parseString("40").value, 40)
        self.assertEqual(n.parseString("+40").value, 40)
        self.assertEqual(n.parseString("-40").value, -40)
        self.assertEqual(n.parseString("-40.45").value, -40.45)
        self.assertEqual(n.parseString("-0.45").value, -0.45)
        self.assertRaises(ParseException, n.parseString, "- 40")
        self.assertRaises(ParseException, n.parseString, "40+")
        
        unit_values = {'M': 2, 'L': 3, 'T': 4, 'Q': 5, 'Theta': 6}

        from dimension import get_units_literals
        u = get_units_literals(unit_values)
        self.assertEqual(u.parseString("1")[0], 1) 
        self.assertEqual(u.parseString("M")[0], 2) 
        self.assertEqual(u.parseString("L")[0], 3)
        self.assertEqual(u.parseString("T")[0], 4)
        self.assertEqual(u.parseString("Q")[0], 5)
        self.assertEqual(u.parseString("Theta")[0], 6)
        self.assertRaises(ParseException, u.parseString, "2")
    
        from dimension import get_term
        t = get_term(unit_values)
        self.assertEqual(t.parseString("L^2")[0], 9)
        self.assertEqual(t.parseString("L^-2")[0], 1/9)
        self.assertEqual(t.parseString("T^0.5")[0], 2)
        
        from dimension import get_numerator
        n = get_numerator(unit_values)
        self.assertEqual(n.parseString("L^2T^3")[0], 9*64)
        self.assertEqual(n.parseString("ThetaTTTheta")[0], 6*4*4*6)

        from dimension import get_expression
        e = get_expression(unit_values)
        self.assertEqual(e.parseString("L^2T^3")[0], 9*64)
        self.assertEqual(e.parseString("ThetaTTTheta")[0], 6*4*4*6)
        self.assertEqual(e.parseString("L/M^2T^0.5")[0], 3/(4*2))
        # insensitive to spaces        
        self.assertEqual(e.parseString("L / M^2T^0.5")[0], 3/(4*2))        
        self.assertEqual(e.parseString("L/M^2 T^0.5")[0], 3/(4*2))        
        self.assertEqual(e.parseString("L/M ^ 2 T^0.5")[0], 3/(4*2))        
        self.assertEqual(e.parseString("1")[0], 1)
        self.assertEqual(e.parseString("1/Q^2")[0], 1/25)
        # should fail if there's extra stuff
        self.assertRaises(ParseException, e.parseString, "T^1/2") # fractions should not fail silently
        
    def test_parse_string_representation(self):
        unit_values = {'M': 2, 'L': 3, 'T': 4, 'Q': 5, 'Theta': 6}
        self.assertEqual(parse_unit_string(Dimension().str(), unit_values), 1)
        self.assertEqual(parse_unit_string(Dimension(M = 1).str(), unit_values), 2)
        self.assertEqual(parse_unit_string(Dimension(L = 1).str(), unit_values), 3)
        self.assertEqual(parse_unit_string(Dimension(T = 1).str(), unit_values), 4)
        self.assertEqual(parse_unit_string(Dimension(Q = 1).str(), unit_values), 5)
        self.assertEqual(parse_unit_string(Dimension(Theta = 1).str(), unit_values), 6)
        self.assertEqual(parse_unit_string(Dimension(M = 2).str(), unit_values), 4)
        self.assertEqual(parse_unit_string(Dimension(L = 1, T = 1).str(), unit_values), 3*4)
        self.assertEqual(parse_unit_string(Dimension(L = 1, T = -1).str(), unit_values), 3/4)
        self.assertEqual(parse_unit_string(Dimension(L = 1, T = -1, Theta = 2).str(), unit_values), 3/4*36)
        self.assertEqual(parse_unit_string(Dimension(T = -1).str(), unit_values), 1/4)
        self.assertEqual(parse_unit_string(Dimension(T = -0.5).str(), unit_values), 1/2)
        self.assertEqual(parse_unit_string(Dimension(L = 1, T = -0.5).str(), unit_values), 3/2)
        self.assertEqual(parse_unit_string(Dimension(M = 2, L = 1, T = -0.5).str(), unit_values), 4*3/2)
        self.assertEqual(parse_unit_string(Dimension(M = -2, L = 1, T = -0.5).str(), unit_values), 3/4/2)
    
    def test_for_equality(self):
        """Equality is based on dimension content."""
        d1 = Dimension()
        d2 = Dimension(L = 1, T = -1)
        self.assertTrue(d1 != d2)
        self.assertFalse(d1 == d2)
        d3 = Dimension(L = 0)
        self.assertTrue(d1 == d3)
        self.assertFalse(d1 != d3)
        
    def test_add_subtract_dimension(self):
        """Add and subtract dimensions doesn't change anything."""
        d1 = Dimension(L = 1, T = -1)
        d2 = Dimension(d1)
        d3 = d1 + d2
        self.assertTrue(d3 == d1)
        d4 = d1 - d2
        self.assertTrue(d4 == d1)
        
    def test_for_incompatible_dimensions(self):
        d1 = Dimension()
        d2 = Dimension(L = 1)
        self.assertRaises(IncompatibleDimensionsError, d1.__add__, d2)
        self.assertRaises(IncompatibleDimensionsError, d1.__sub__, d2)

    def test_multiply_and_divide_dimensions(self):
        """Multiply and divide dimensions."""
        d1 = Dimension(L = 4, T = -1)
        d2 = Dimension(L = 1, M = 2, T = 1)
        d3 = d1*d2
        self.assertEqual(d3.M, 2)
        self.assertEqual(d3.L, 5)
        self.assertEqual(d3.T, 0)
        self.assertEqual(d3.Q, 0)
        self.assertEqual(d3.Theta, 0)
        d4 = d1/d2
        self.assertEqual(d4.M, -2)
        self.assertEqual(d4.L, 3)
        self.assertEqual(d4.T, -2)
        self.assertEqual(d4.Q, 0)
        self.assertEqual(d4.Theta, 0)


if __name__ == '__main__':
    unittest.main()
