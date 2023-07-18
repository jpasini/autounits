# Design Notes

I'd like to use this project to apply the lessons from John Ousterhout's _A Philosophy of Software Design_. 

Chapter 11, _Design It Twice_, advises to quickly try out a couple of _very different designs_ before deciding which one is the best.

I'll start by focusing on the interface, to try and push complexity down to the implementation, thus making the classes deeper.

## Design 1 (current)


There are two main classes:
* `Dimension` only contains the dimension of a quantity (e.g., a length squared)
* `PhysicalQuantity` is something that has both a dimension and a value in some units.

For example,

```
d = Dimension(L = 2, T = -1) # a dimension of area per unit time
p = PhysicalQuantity(d, "3m^2/s")
print(p['km^2/s']) # 3e-6
```

### Questions:

* How to deal with arrays of physical quantities?

## Design 2 (conform to popular interfaces)

The idea is to look at widely-used interfaces, like numpy, pandas, scikit-learn, and make sure they can be used seamlessly.

## Design 3 (?)
