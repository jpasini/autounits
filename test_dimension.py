from __future__ import division

import unittest
from dimension import Dimension


class TestDimension(unittest.TestCase):
    """Test the Dimension class."""
    
    def test_create_dimension(self):
        """Simple Dimension objects."""
        d1 = Dimension() # default: dimensionless
        d2 = Dimension({'L': 0, 'T': 0, 'M': 0})
        self.assertTrue(d1 == d2)
        
    def test_add_subtract_dimension(self):
        """Add and subtract dimensions doesn't change anything."""
        d1 = Dimension()
        d2 = Dimension()
        d3 = d1 + d2
        self.assertTrue(d3 == d1)
        d4 = d1 - d2
        self.assertTrue(d4 == d1)

    def test_multiply_dimension(self):
        """Multiply dimensions."""
        d1 = Dimension()
        d2 = Dimension({'L': 1})
        d3 = d1*d2                    

if __name__ == '__main__':
    unittest.main()
