

import random
import math
import numpy as np
from pytest import approx, raises
from mitxgraders.helpers.calc.exceptions import DomainError, FunctionEvalError
from mitxgraders.helpers.calc.mathfuncs import (
    arctan2, kronecker,
    cot, arccot,
    csc, arccsc,
    sec, arcsec,
    coth, arccoth,
    csch, arccsch,
    sech, arcsech,
    ARRAY_ONLY_FUNCTIONS, ARRAY_FUNCTIONS)
from mitxgraders.helpers.calc.math_array import (
    MathArray, random_math_array, equal_as_arrays)

def test_math_functions():
    """Test the math functions that we've implemented"""
    x = random.uniform(0, 1)
    assert cot(x) == approx(1/math.tan(x))
    assert sec(x) == approx(1/math.cos(x))
    assert csc(x) == approx(1/math.sin(x))
    assert sech(x) == approx(1/math.cosh(x))
    assert csch(x) == approx(1/math.sinh(x))
    assert coth(x) == approx(1/math.tanh(x))
    assert arcsec(sec(x)) == approx(x)
    assert arccsc(csc(x)) == approx(x)
    assert arccot(cot(x)) == approx(x)
    assert arcsech(sech(x)) == approx(x)
    assert arccsch(csch(x)) == approx(x)
    assert arccoth(coth(x)) == approx(x)

    x = random.uniform(-1, 0)
    assert cot(x) == approx(1/math.tan(x))
    assert sec(x) == approx(1/math.cos(x))
    assert csc(x) == approx(1/math.sin(x))
    assert sech(x) == approx(1/math.cosh(x))
    assert csch(x) == approx(1/math.sinh(x))
    assert coth(x) == approx(1/math.tanh(x))
    assert -arcsec(sec(x)) == approx(x)
    assert arccsc(csc(x)) == approx(x)
    assert arccot(cot(x)) == approx(x)
    assert -arcsech(sech(x)) == approx(x)
    assert arccsch(csch(x)) == approx(x)
    assert arccoth(coth(x)) == approx(x)

def test_array_functions_preserve_type():

    for name in ['re', 'im', 'conj']:
        func = ARRAY_FUNCTIONS[name]
        result = func(random_math_array((3, 3)))
        assert isinstance(result, MathArray)

    for name in ['trans', 'ctrans', 'adj']:
        func = ARRAY_ONLY_FUNCTIONS[name]
        result = func(random_math_array((3, 3)))
        assert isinstance(result, MathArray)

def test_det_and_tr_raise_error_if_not_square():

    det = ARRAY_ONLY_FUNCTIONS['det']
    match = (r"There was an error evaluating function det\(...\)\n"
             r"1st input has an error: received a matrix of shape "
             r"\(rows: 2, cols: 3\), expected a square matrix")
    with raises(DomainError, match=match):
        det(random_math_array((2, 3)))

    tr = ARRAY_ONLY_FUNCTIONS['trace']
    match = (r"There was an error evaluating function trace\(...\)\n"
             r"1st input has an error: received a matrix of shape "
             r"\(rows: 2, cols: 3\), expected a square matrix")
    with raises(DomainError, match=match):
        tr(random_math_array((2, 3)))

def test_array_abs_input_types():
    array_abs = ARRAY_ONLY_FUNCTIONS['abs']

    x = random.uniform(0, 10)
    assert array_abs(x) == x
    assert array_abs(-x) == x

    assert array_abs(MathArray([2, -3, 6])) == 7

    match = (r"The abs\(...\) function expects a scalar or vector. To take the "
             r"norm of a matrix, try norm\(...\) instead.")
    with raises(FunctionEvalError, match=match):
        array_abs(MathArray([[1, 2], [3, 4]]))

def test_cross():
    cross = ARRAY_ONLY_FUNCTIONS['cross']
    a = MathArray([2, -1, 3.5])
    b = MathArray([1.5, 2.25, -1])
    a_cross_b = MathArray([-6.875, 7.25, 6.])

    assert equal_as_arrays(cross(a, b), a_cross_b)

    vec_3 = random_math_array((3,))
    vec_4 = random_math_array((4,))
    match = (r"There was an error evaluating function cross\(...\)\n"
             r"1st input is ok: received a vector of length 3 as expected\n"
             r"2nd input has an error: received a vector of length 4, expected "
             r"a vector of length 3")
    with raises(DomainError, match=match):
        cross(vec_3, vec_4)

    match = (r"There was an error evaluating function cross\(...\)\n"
             r"1st input has an error: received a vector of length 4, expected "
             r"a vector of length 3\n"
             r"2nd input is ok: received a vector of length 3 as expected")
    with raises(DomainError, match=match):
        cross(vec_4, vec_3)

def test_arctan2():
    assert arctan2(-1, 1) == 3*np.pi/4
    assert arctan2(-1, -1) == -3*np.pi/4
    assert arctan2(1, -1) == -np.pi/4
    assert arctan2(1, 1) == np.pi/4
    assert arctan2(-1, 0) == np.pi

    for (x, y) in np.random.rand(20, 2):
        # We reversed the order compared to numpy
        assert np.arctan2(y, x) == arctan2(x, y)

    match = r'arctan2\(0, 0\) is undefined'
    with raises(FunctionEvalError, match=match):
        arctan2(0, 0)

def test_kronecker():
    assert kronecker(1, 1) == 1
    assert kronecker(1, 0) == 0
    assert kronecker(0, 1) == 0
    assert kronecker(0, 0) == 1
    assert kronecker(1.5, 1.5) == 1
