# Autounits

This is a Python library designed to handle physical quantities. It derives
the dimensions of expressions using these quantities and checks for consistency
when performing some operations.

See `design_notes.md` for discussion on how this library is and could be designed.

## Example use

The code has many unit tests, which can be seen as examples of how to use this.

There are two main classes:
* `Dimension` only contains the dimension of a quantity (e.g., a length squared)
* `PhysicalQuantity` is something that has both a dimension and a value in some units.

For example,

```
d = Dimension(L = 2, T = -1) # a dimension of area per unit time
p = PhysicalQuantity(d, "3m^2/s")
print(p['km^2/s']) # 3e-6
```

