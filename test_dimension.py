from __future__ import division

import unittest
from dimension import Dimension, IncompatibleDimensionsError


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
        
    def test_create_from_other_dimension(self):
        """Create dimensions from other dimensions."""
        d1 = Dimension(L = 1, T = -1)
        d2 = Dimension(d1)
        self.assertEqual(d2.M, 0)
        self.assertEqual(d2.L, 1)
        self.assertEqual(d2.T, -1)
        self.assertEqual(d2.Q, 0)
        self.assertEqual(d2.Theta, 0)
    
    def test_create_from_string(self):
        """Create dimensions from strings."""
        d1 = Dimension("L/T")
        self.assertEqual(d1.M, 0) # mass
        self.assertEqual(d1.L, 1) # length
        self.assertEqual(d1.T, -1) # time
        self.assertEqual(d1.Q, 0) # electric charge
        self.assertEqual(d1.Theta, 0) # absolute temperature
        d2 = Dimension("L/T^2")
        self.assertEqual(d2.M, 0)
        self.assertEqual(d2.L, 1)
        self.assertEqual(d2.T, -2)
        self.assertEqual(d2.Q, 0)
        self.assertEqual(d2.Theta, 0)
        d3 = Dimension("Q^2L/T^2/M^4/Theta^3")
        self.assertEqual(d3.M, -4)
        self.assertEqual(d3.L, 1)
        self.assertEqual(d3.T, -2)
        self.assertEqual(d3.Q, 2)
        self.assertEqual(d3.Theta, 3)
        d4 = Dimension("Q^2L/(T^2M^4Theta^3)")
        self.assertEqual(d3, d4)
        d5 = Dimension("Q^2 L/(T^2 M^4 Theta^3)")
        self.assertEqual(d3, d5)        
        
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
        self.assertEqual(d3.M, -2)
        self.assertEqual(d3.L, 3)
        self.assertEqual(d3.T, -2)
        self.assertEqual(d3.Q, 0)
        self.assertEqual(d3.Theta, 0)
        

if __name__ == '__main__':
    unittest.main()
