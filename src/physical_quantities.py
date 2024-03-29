"""
physical_quantities.py:
Library of physical quantities, with automatic unit conversion.
"""

from __future__ import division

from functools import total_ordering
from numbers import Number

from pyparsing import Literal, Or, ParseException, replaceWith, stringEnd

from dimension import Dimension, parse_unit_string


class PhysicalQuantityError(Exception):
    """Base class for errors in this module."""


class BadInputError(PhysicalQuantityError):
    """Bad string input to create a quantity."""


class BadUnitDictionaryError(PhysicalQuantityError):
    """Need better description here."""  # FIXME


class IncompatibleUnitsError(PhysicalQuantityError):
    """Illegal operation with incompatible units."""


def flatten_dictionary(units_dictionary):
    """
    Utility function I should document better!!
    """
    # Make sure there are no name clashes in the units
    from itertools import chain

    k = units_dictionary.keys()
    tuples = list(filter(lambda x: isinstance(x, tuple), k))  # find tuples
    not_tuples = list(filter(lambda x: not isinstance(x, tuple), k))
    flattened_tuples = list(chain(*tuples))
    # join
    rejoined = flattened_tuples + not_tuples
    flattened_keys = set(rejoined)
    if len(flattened_keys) != len(rejoined):
        raise BadUnitDictionaryError

    # At this point there are no name clashes, so flatten
    new_dictionary = dict()
    for key, value in units_dictionary.items():
        if not isinstance(key, tuple):
            new_dictionary[key] = value
        else:
            for label in key:
                new_dictionary[label] = value
    return new_dictionary


class PhysicalQuantityStringParser:
    """Object that parses a string representing an amount with units."""

    _primitive_units_dictionaries = None
    _parsers = {}
    _flat_unit_dictionaries = {}

    def __init__(self, dimension, primitive_units_dictionaries):
        # Create the dictionary for the dimensions given
        self._is_dimensionless = (
            dimension == Dimension()
        )  # dimensionless quantities receive special treatment
        dimension_str = dimension.str()

        if (
            primitive_units_dictionaries
            != PhysicalQuantityStringParser._primitive_units_dictionaries
        ):
            # we're changing unit sets, so I need to clear everything
            PhysicalQuantityStringParser._primitive_units_dictionaries = (
                primitive_units_dictionaries
            )
            PhysicalQuantityStringParser._parsers = {}
            PhysicalQuantityStringParser._flat_unit_dictionaries = {}
        else:
            # check: we might have done this case already
            if dimension_str in PhysicalQuantityStringParser._parsers:
                self.flat_units_dictionary = PhysicalQuantityStringParser._flat_unit_dictionaries[
                    dimension_str
                ]
                self._dimension = PhysicalQuantityStringParser._parsers[dimension_str]
                return

        pattern = dimension.str(use_braces=True)
        d = {}
        for key, value in primitive_units_dictionaries.items():
            d[key] = flatten_dictionary(value)

        # go systematically through all primitive unit-set combinations
        from itertools import product

        p = list(
            product(
                d["M"].keys(),
                d["L"].keys(),
                d["T"].keys(),
                d["Q"].keys(),
                d["Theta"].keys(),
            )
        )
        new_dictionary = {}
        for units in p:
            # generate the string representing the units (e.g, "m/s^2")
            units_string_dictionary = dict(zip(["M", "L", "T", "Q", "Theta"], units))
            unit_string = pattern.format(**units_string_dictionary)
            # it could be repeated at this stage if the target quantity has only limited dimensions
            unit_values = [
                d[k][units_string_dictionary[k]] for k in ["M", "L", "T", "Q", "Theta"]
            ]
            units_value_dictionary = dict(
                zip(["M", "L", "T", "Q", "Theta"], unit_values)
            )
            # I need a parser to evaluate this expression
            if unit_string in new_dictionary.keys():
                continue
            new_dictionary[unit_string] = parse_unit_string(
                dimension_str, units_value_dictionary
            )

        self.flat_units_dictionary = new_dictionary

        def make_literal(unit_string, val):
            return Literal(unit_string).setParseAction(replaceWith(val))

        units = Or([make_literal(s, v) for s, v in new_dictionary.items()])

        from pyparsing import Regex

        number = Regex(r"\d+(\.\d*)?([eE][+-]?\d+)?")
        number.setParseAction(lambda tokens: float(tokens[0]))

        if self._is_dimensionless:
            self._dimension = number + stringEnd
        else:
            self._dimension = number + units + stringEnd
        # add to our stock
        PhysicalQuantityStringParser._flat_unit_dictionaries[
            dimension_str
        ] = self.flat_units_dictionary
        PhysicalQuantityStringParser._parsers[dimension_str] = self._dimension

    def __call__(self, quantity_string):
        """Parse the given string."""
        try:
            a = self._dimension.parseString(quantity_string)
        except ParseException:
            raise BadInputError
        if self._is_dimensionless:
            return a[0]
        return a[0] * a[1]


# mapping from dimension strings to derived types
_mapping_to_derived_types = {}


class PhysicalQuantityFactory:
    """Factory for PhysicalQuantity objects."""

    @staticmethod
    def new(dimension, value=None):
        dimension_str = str(dimension)
        if dimension_str not in _mapping_to_derived_types:
            return PhysicalQuantity(dimension, value)
        return _mapping_to_derived_types[dimension_str](value)


@total_ordering
class PhysicalQuantity:
    """
    Main class describing a quantity with associated units.
    """

    # For caching:
    _parsers = {}
    _default_units = {}
    # Conversion constants for primitive quantities
    _primitive_units = {}
    _primitive_units["M"] = {
        ("kg", "kilogram", "kilograms"): 1,
        ("g", "gr", "gram", "grams"): 0.001,
    }
    _primitive_units["L"] = {
        ("m", "meter", "meters"): 1,
        ("mi", "mile", "miles"): 1609.344,
        ("km", "kilometer", "kilometers"): 1000,
        "marathon": 42194.988,
    }
    _primitive_units["T"] = {
        ("s", "sec", "secs", "second", "seconds"): 1,
        ("min", "mins", "minute", "minutes"): 60,
        ("hr", "hrs", "hour", "hours"): 3600,
    }
    _primitive_units["Q"] = {("C", "coulomb"): 1}
    _primitive_units["Theta"] = {("K", "kelvin"): 1, ("R", "rankine"): 5 / 9}

    def __init__(self, dimension=Dimension(), value=None):
        """Initialization value may be either a string (to be parsed) or another
        object of the same dimensions."""
        if not isinstance(dimension, Dimension):
            raise PhysicalQuantityError

        self.dimension = dimension

        # create the parser if it doesn't exist already. Index by string representation
        dimension_str = dimension.str()
        if dimension_str not in PhysicalQuantity._parsers:
            PhysicalQuantity._parsers[dimension_str] = PhysicalQuantityStringParser(
                dimension, PhysicalQuantity._primitive_units
            )
        self._parser = PhysicalQuantity._parsers[dimension_str]
        # choose default units for printing and store if they're not stored already
        if dimension_str not in PhysicalQuantity._default_units:
            # Choose basic units (something that gives a conversion of 1)
            # and the shortest representation
            candidates = [
                k for (k, v) in self._parser.flat_units_dictionary.items() if v == 1
            ]
            PhysicalQuantity._default_units[dimension_str] = min(candidates, key=len)
        self._default_unit_for_printing = PhysicalQuantity._default_units[dimension_str]

        self._amount_in_basic_units = None
        if value is not None:
            if isinstance(value, str):
                self._amount_in_basic_units = self._parser(value)
            else:
                if self.dimension != value.dimension:
                    raise IncompatibleUnitsError
                self._amount_in_basic_units = value._amount_in_basic_units

    def __getitem__(self, key):
        return self._amount_in_basic_units / self._parser.flat_units_dictionary[key]

    def __setitem__(self, key, value):
        self._amount_in_basic_units = value * self._parser.flat_units_dictionary[key]

    def get_available_units(self):
        return self._parser.flat_units_dictionary.keys()

    def __repr__(self):
        unit = self._default_unit_for_printing
        unit_to_print = "" if unit == "1" else " %s" % unit
        return "PhysicalQuantity(%s,'%s%s')" % (
            repr(self.dimension),
            repr(self[unit]),
            unit_to_print,
        )

    def __str__(self):
        unit = self._default_unit_for_printing
        unit_to_print = "" if unit == "1" else " %s" % unit
        return "%g%s" % (self[unit], unit_to_print)

    def __eq__(self, other):
        """Equality is defined by the dimension and amount."""
        return (
            self.dimension == other.dimension
            and self._amount_in_basic_units == other._amount_in_basic_units
        )

    def __ne__(self, other):
        """Equality is defined by the dimension and amount."""
        return (
            self.dimension != other.dimension
            or self._amount_in_basic_units != other._amount_in_basic_units
        )

    def __lt__(self, other):
        """Less-than comparison."""
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError
        return self._amount_in_basic_units < other._amount_in_basic_units

    @classmethod
    def register_type(cls):
        """Register this class as the one to use when creating objects of these dimensions.
        (To be called by derived classes)"""
        dimension_str = str(cls._dim)
        if dimension_str not in _mapping_to_derived_types:
            _mapping_to_derived_types[dimension_str] = cls

    def __add__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError
        result = PhysicalQuantityFactory().new(self.dimension)
        result._amount_in_basic_units = (
            self._amount_in_basic_units + other._amount_in_basic_units
        )
        return result

    def __radd__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError
        result = PhysicalQuantityFactory().new(self.dimension)
        result._amount_in_basic_units = (
            self._amount_in_basic_units + other._amount_in_basic_units
        )
        return result

    def __sub__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError
        result = PhysicalQuantityFactory().new(self.dimension)
        result._amount_in_basic_units = (
            self._amount_in_basic_units - other._amount_in_basic_units
        )
        return result

    def __rsub__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        if self.dimension != other.dimension:
            raise IncompatibleUnitsError
        result = PhysicalQuantityFactory().new(self.dimension)
        result._amount_in_basic_units = (
            other._amount_in_basic_units - self._amount_in_basic_units
        )
        return result

    def __mul__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = self.dimension * other.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = (
            self._amount_in_basic_units * other._amount_in_basic_units
        )
        return result

    def __rmul__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = self.dimension * other.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = (
            self._amount_in_basic_units * other._amount_in_basic_units
        )
        return result

    def __div__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = self.dimension / other.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = (
            self._amount_in_basic_units / other._amount_in_basic_units
        )
        return result

    def __rdiv__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = other.dimension / self.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = (
            other._amount_in_basic_units / self._amount_in_basic_units
        )
        return result

    def __truediv__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = self.dimension / other.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = (
            self._amount_in_basic_units / other._amount_in_basic_units
        )
        return result

    def __rtruediv__(self, other):
        if isinstance(other, Number):
            other = PhysicalQuantity(Dimension(), "%s" % other)
        new_dimension = other.dimension / self.dimension
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = (
            other._amount_in_basic_units / self._amount_in_basic_units
        )
        return result

    def __pow__(self, other):
        if not isinstance(other, Number):
            # it can only be a dimensionless quantity, so extract the value
            other = other["1"]
        new_dimension = self.dimension ** other
        result = PhysicalQuantityFactory().new(new_dimension)
        result._amount_in_basic_units = self._amount_in_basic_units ** other
        return result


class Dimensionless(PhysicalQuantity):
    _dim = Dimension()

    def __init__(self, value=None):
        super(Dimensionless, self).__init__(Dimensionless._dim, value)


class Mass(PhysicalQuantity):
    _dim = Dimension(M=1)

    def __init__(self, value=None):
        super(Mass, self).__init__(Mass._dim, value)


class Distance(PhysicalQuantity):
    _dim = Dimension(L=1)

    def __init__(self, value=None):
        super(Distance, self).__init__(Distance._dim, value)


class Time(PhysicalQuantity):
    _dim = Dimension(T=1)
    _hr_in_secs = PhysicalQuantity(_dim, "1 hr")["s"]
    _min_in_secs = PhysicalQuantity(_dim, "1 min")["s"]

    def __init__(self, value=None):
        super(Time, self).__init__(Time._dim, value)

    @property
    def str(self):
        secs = self["s"]
        hours = int(secs / Time._hr_in_secs)
        secs = secs - hours * Time._hr_in_secs
        mins = int(secs / Time._min_in_secs)
        secs = int(secs - mins * Time._min_in_secs)
        result = ""
        if hours > 0:
            result = result + str(hours) + ":"
        result = result + "{0:02d}:{1:02d}".format(mins, secs)
        return result


class Charge(PhysicalQuantity):
    _dim = Dimension(Q=1)

    def __init__(self, value=None):
        super(Charge, self).__init__(Charge._dim, value)


class Temperature(PhysicalQuantity):
    """Temperature: need to add some conversions that are not just factors."""

    _dim = Dimension(Theta=1)

    def __init__(self, value=None):
        super(Temperature, self).__init__(Temperature._dim, value)

    def __getitem__(self, key):
        if key == "C":
            K = self._amount_in_basic_units / self._parser.flat_units_dictionary["K"]
            return K - 273.15
        elif key == "F":
            C = (
                self._amount_in_basic_units / self._parser.flat_units_dictionary["K"]
                - 273.15
            )
            return C * 9 / 5 + 32
        else:
            return super(Temperature, self).__getitem__(key)

    def __setitem__(self, key, value):
        if key == "C":
            self._amount_in_basic_units = (
                value + 273.15
            ) * self._parser.flat_units_dictionary["K"]
        elif key == "F":
            self._amount_in_basic_units = (
                (value - 32) * 5 / 9 + 273.15
            ) / self._parser.flat_units_dictionary["K"]
        else:
            super(Temperature, self).__setitem__(key, value)


# Some important derived quantities


class Speed(PhysicalQuantity):
    _dim = Dimension(L=1, T=-1)

    def __init__(self, value=None):
        super(Speed, self).__init__(Speed._dim, value)

    def pace(self, distance):
        """Return time to cover given distance."""
        return distance / self


class Energy(PhysicalQuantity):
    """Energy: Need to define additional synonyms."""

    _dim = Dimension(M=1, L=2, T=-2)
    _Btu_2_J = 1055.05585

    def __init__(self, value=None):
        super(Energy, self).__init__(Energy._dim, value)

    def __getitem__(self, key):
        if key == "J":
            return (
                self._amount_in_basic_units
                / self._parser.flat_units_dictionary["kgm^2/s^2"]
            )
        elif key == "Btu":
            return (
                self._amount_in_basic_units
                / self._parser.flat_units_dictionary["kgm^2/s^2"]
                / self._Btu_2_J
            )
        else:
            return super(Energy, self).__getitem__(key)

    def __setitem__(self, key, value):
        if key == "J":
            self._amount_in_basic_units = (
                value * self._parser.flat_units_dictionary["kgm^2/s^2"]
            )
        elif key == "Btu":
            self._amount_in_basic_units = (
                value / self._parser.flat_units_dictionary["kgm^2/s^2"] * self._Btu_2_J
            )
        else:
            super(Energy, self).__setitem__(key, value)


# Initialize by registering all derived types
for derivedclass in [
    Dimensionless,
    Mass,
    Distance,
    Time,
    Charge,
    Temperature,
    Speed,
    Energy,
]:
    derivedclass.register_type()
