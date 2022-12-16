"""
dimension.py:
Library of physical dimensions.
"""

from __future__ import division
from functools import reduce


class DimensionError(Exception):
    pass


class IncompatibleDimensionsError(DimensionError):
    pass


class Dimension(object):
    """Class describing dimensions: length, time, etc. and derivative dimensions."""

    def __init__(self, *args, **kwargs):
        """Can be initialized like this:
        Dimension(L = 1, T = -2) using named arguments,
        Dimension(d) using another dimension
        Dimension("L/T") using a string <== Not yet."""
        self._dimensions_considered = ["M", "L", "T", "Q", "Theta"]
        # If args contains something, it should be a dimension
        if len(args) > 1:
            raise DimensionError
        elif len(args) == 1:
            d = args[0]
            if type(d) != type(self):  # it's not a dimension
                raise DimensionError
            if len(kwargs) > 0:  # shouldn't have included more inputs
                raise DimensionError
            for k in self._dimensions_considered:
                self.__dict__[k] = d.__dict__[k]
        else:  # len(args) == 0, so I should only have named arguments
            if len(set(kwargs.keys()) - set(self._dimensions_considered)) > 0:
                raise DimensionError
            for k in self._dimensions_considered:
                self.__dict__[k] = 0 if k not in kwargs else kwargs[k]

    def __repr__(self):
        args = ", ".join(
            ["%s=%s" % (k, repr(self.__dict__[k])) for k in self._dimensions_considered]
        )
        return "Dimension(%s)" % args

    def __str__(self):
        return self.str(use_braces=False)

    def is_primitive(self):
        """The dimension is primitive if it's either dimensionless or only one."""
        number_of_ones = 0
        number_of_nonzeros_and_nonones = 0
        for k in self._dimensions_considered:
            p = self.__dict__[k]  # power of this dimension
            if p == 1:
                number_of_ones += 1
            elif p != 0:
                number_of_nonzeros_and_nonones += 1
        return number_of_nonzeros_and_nonones == 0 and number_of_ones in [0, 1]

    def str(self, use_braces=False):
        if use_braces:
            lbrace, rbrace = "{}"
        else:
            lbrace = rbrace = ""
        numerator = ""
        denominator = ""
        for k in self._dimensions_considered:
            v = self.__dict__[k]
            if v == 0:
                continue
            if v == 1:
                numerator += "%s%s%s" % (lbrace, k, rbrace)
            elif v == -1:
                denominator += "%s%s%s" % (lbrace, k, rbrace)
            elif v > 0:
                numerator += "%s%s%s^%s" % (lbrace, k, rbrace, v)
            else:
                denominator += "%s%s%s^%s" % (lbrace, k, rbrace, -v)
        if numerator == "":
            numerator = "1"
        if denominator != "":
            denominator = "/" + denominator
        return numerator + denominator

    def __eq__(self, other):
        """Check for equality."""
        return (
            self.M == other.M
            and self.L == other.L
            and self.T == other.T
            and self.Q == other.Q
            and self.Theta == other.Theta
        )

    def __ne__(self, other):
        """Check for difference."""
        return (
            self.M != other.M
            or self.L != other.L
            or self.T != other.T
            or self.Q != other.Q
            or self.Theta != other.Theta
        )

    def __add__(self, other):
        """Addition: checks for compatibility."""
        if self != other:
            raise IncompatibleDimensionsError
        else:
            return Dimension(self)  # create a copy of self.

    def __sub__(self, other):
        """Subtraction: checks for compatibility."""
        if self != other:
            raise IncompatibleDimensionsError
        else:
            return Dimension(self)  # create a copy of self.

    def __mul__(self, other):
        """Multiplication."""
        return Dimension(
            M=self.M + other.M,
            L=self.L + other.L,
            T=self.T + other.T,
            Q=self.Q + other.Q,
            Theta=self.Theta + other.Theta,
        )

    def __div__(self, other):
        """Division (when __future__.division is not defined)."""
        return Dimension(
            M=self.M - other.M,
            L=self.L - other.L,
            T=self.T - other.T,
            Q=self.Q - other.Q,
            Theta=self.Theta - other.Theta,
        )

    def __truediv__(self, other):
        """Division (when __future__.division is defined).."""
        return Dimension(
            M=self.M - other.M,
            L=self.L - other.L,
            T=self.T - other.T,
            Q=self.Q - other.Q,
            Theta=self.Theta - other.Theta,
        )

    def __pow__(self, other):
        """Raise to integer or fractional powers"""
        return Dimension(
            M=self.M * other,
            L=self.L * other,
            T=self.T * other,
            Q=self.Q * other,
            Theta=self.Theta * other,
        )


def get_number():
    from pyparsing import Word, nums, ParseException

    def validate_and_convert_number(tokens):
        try:
            return float(tokens[0])
        except ValueError:
            raise ParseException("Invalid number (%s)" % tokens[0])

    number = Word(nums + "-" + "+" + ".").setResultsName(
        "value"
    )  # do not allow scientific notation
    number.setParseAction(validate_and_convert_number)
    return number


def get_units_literals(units_value_dictionary):
    from pyparsing import Literal, replaceWith, Or

    def make_literal(unit_string, val):
        return Literal(unit_string).setParseAction(replaceWith(val))

    units_value_dictionary["1"] = 1  # add one more term for dimensionless quantities
    return Or([make_literal(s, v) for (s, v) in units_value_dictionary.items()])


def get_term(units_value_dictionary):
    from pyparsing import Optional

    n = get_number()
    unit = get_units_literals(units_value_dictionary)
    term = unit + Optional("^" + n)

    def exponentiate_if_needed(tokens):
        if len(tokens) < 2:
            return tokens[0]
        else:
            return tokens[0] ** tokens[2]

    term.setParseAction(exponentiate_if_needed)
    # term.setParseAction(lambda t: float(t[0]))
    return term


def get_numerator(units_value_dictionary):
    from pyparsing import OneOrMore

    term = get_term(units_value_dictionary)
    numerator = OneOrMore(term)

    def multiply_tokens(tokens):
        return reduce(lambda x, y: x * y, tokens)

    numerator.setParseAction(multiply_tokens)
    return numerator


def get_expression(units_value_dictionary):
    from pyparsing import Optional, stringEnd

    numerator = get_numerator(units_value_dictionary)
    expression = numerator + Optional("/" + numerator) + stringEnd

    def calculate_final_value(tokens):
        l = len(tokens)
        if l == 1:
            return tokens[0]
        else:
            return tokens[0] / tokens[2]

    expression.setParseAction(calculate_final_value)
    return expression


cached_unit_string_parsers = {}


def parse_unit_string(unit_string, units_value_dictionary):
    """Parse a string containing units.
    For example:
    
    LT/M^3Q
    
    and return the corresponding value, after replacing with values
    from units_value_dictionary, which contains, for example
    {'L': 1, 'M': 1, 'T': 60, 'Q': 1, 'Theta': 1}
    """
    combo = unit_string, tuple((k, v) for k, v in units_value_dictionary.items())
    if combo not in cached_unit_string_parsers:
        cached_unit_string_parsers[combo] = get_expression(units_value_dictionary)
    return cached_unit_string_parsers[combo].parseString(unit_string)[0]
