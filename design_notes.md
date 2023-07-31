# Design Notes

I'd like to use this project to apply the lessons from John Ousterhout's _A Philosophy of Software Design_. 

Chapter 11, _Design It Twice_, advises to quickly try out a couple of _very different designs_ before deciding which one is the best.

I'll start by focusing on the interface, to try and push complexity down to the implementation, thus making the classes deeper.

## Design 1 (current)


There are two main classes:
* `Dimension` only contains the dimension of a quantity (e.g., a length squared)
* `PhysicalQuantity` is something that has both a dimension and a value in some units.

For example,

```python
d = Dimension(L = 2, T = -1) # a dimension of area per unit time
p = PhysicalQuantity(d, "3m^2/s")
print(p['km^2/s']) # 3e-6
```

### Questions:

* How to deal with _arrays_ of physical quantities?
* Is using square brackets a bad idea? Will it interfere with list/tuple indexing `l[i]` or dict element access `d['key']`?

## Design 2 (conform to popular interfaces)

The idea is to look at widely-used interfaces, like numpy, pandas, scikit-learn, and make sure they can be used seamlessly.

It seems `scimath` has defined units for working with scalars and arrays [using decorators](http://docs.enthought.com/scimath/units/unit_numpy.html). I should study this: perhaps it does everything I need.

See also:

* [UnitScalar](http://docs.enthought.com/scimath/units/user_ref.html#scimath.units.unit_scalar.UnitScalar)
* [UnitArray](http://docs.enthought.com/scimath/units/user_ref.html#scimath.units.unit_scalar.UnitArray)
* [Unitted functions](http://docs.enthought.com/scimath/units/unit_funcs.html#unit-funcs). I'm not a fan of unitted functions doing unit conversions. I prefer that they return a physical quantity, and we choose the units afterward.
* I do like the approach of [using units explicitly](http://docs.enthought.com/scimath/units/intro.html) to give dimensions to quantities, as they _should_ be specified when first created. E.g., having `cm` be a defined object, so `x = 3*cm` makes `x` a distance and gives a default unit for display.
* I should try to use `sklearn` algorithms with these objects, to see if (a) they work and (b) they retain the units after being processed into derived quantities.

Another library that attempts this is [QuantiPhy](https://github.com/KenKundert/quantiphy), but it doesn't seem to be what I'm looking for.

There's a [list of alternatives](https://kdavies4.github.io/natu/seealso.html) in the `natu` documentation.

### Questions:

Say we have a regressor from scikit-learn and we have two numpy.array-like objects that are physical quantities that the regressor is able to consume during training, will the outputs _still_ be physical quantities? Let's say we want to estimate the spring constant `k` in `F=-kx`. We have an array `F` with _force_ dimensions and an array `x` of distance. Will `k` have dimensions of force/distance? Given `x`, will predictions from the model have dimensions of force?

To make this concrete:

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression()
# need to complete the example
```

## Design 3 (Separate System of Units class)

In the `feature/betterinput` branch I started developing this idea that the PhysicalQuantity class was doing too much and starting to become a Frankenclass. The concept here is to separate the class that holds the quantity (dimension and magnitude) from the set of units, including derived units, that could be used to express a physical quantity.

This is mostly about internal implementation, but for the design discussion I want to understand first how this may change (improve?) the interface. On the other hand, it could be best if this does not have a visible impact on the interface, and just becomes a natural way of implementing it.

