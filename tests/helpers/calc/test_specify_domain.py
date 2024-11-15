

from pytest import raises
import numpy as np
from voluptuous import Error
from mitxgraders.helpers.calc import specify_domain
from mitxgraders.helpers.calc.exceptions import DomainError, ArgumentError
from mitxgraders.helpers.calc.math_array import equal_as_arrays, random_math_array
from mitxgraders.exceptions import ConfigError

def get_somefunc(display_name=None):

    if display_name:
        # Takes: scalar, [2, 3] matrix, 3-component vector, 2-component vector
        @specify_domain(input_shapes=[1, [2, 3], 3, 2], display_name=display_name)
        def somefunc(w, x, y, z):
            return w*x*y + z
    else:
        # Takes: scalar, [2, 3] matrix, 3-component vector, 2-component vector
        @specify_domain(input_shapes=[1, [2, 3], 3, 2])
        def somefunc(w, x, y, z):
            return w*x*y + z

    return somefunc

def get_somefunc_from_static_method(display_name=None):
    """
    Uses specify_domain.make_decorator to decorate the function.
    Unlike author-facing specify_domain, make_decorator's shapes must ALL be tuples.
    """
    shapes = [
        (1,), # scalar
        (2, 3), # 2 by 3 matrix
        (3,), # vector of length 3
        (2,) # vector of length 2
    ]
    if display_name:
        # Takes: scalar, [2, 3] matrix, 3-component vector, 2-component vector

        @specify_domain.make_decorator(*shapes, display_name=display_name)
        def somefunc(w, x, y, z):
            return w*x*y + z
    else:
        # Takes: scalar, [2, 3] matrix, 3-component vector, 2-component vector
        @specify_domain.make_decorator(*shapes)
        def somefunc(w, x, y, z):
            return w*x*y + z

    return somefunc

def test_correct_arguments_get_passed_to_function():
    f = get_somefunc()

    w = np.random.uniform(-10, 10)
    x = random_math_array([2, 3])
    y = random_math_array([3])
    z = random_math_array([2])

    assert equal_as_arrays(f(w, x, y, z), w*x*y + z)

def test_incorrect_arguments_raise_errors():
    f = get_somefunc()
    F = get_somefunc_from_static_method()

    w = np.random.uniform(-10, 10)
    x = random_math_array([2, 2])
    y = np.random.uniform(-10, 10)
    z = random_math_array([2])

    match = (r"There was an error evaluating function {0}\(...\)"
             r"\n1st input is ok: received a scalar as expected"
             r"\n2nd input has an error: received a matrix of shape \(rows: 2, cols: 2\), "
             r"expected a matrix of shape \(rows: 2, cols: 3\)"
             r"\n3rd input has an error: received a scalar, expected a vector of length 3"
             r"\n4th input is ok: received a vector of length 2 as expected")
    with raises(DomainError, match=match.format('somefunc')):
        f(w, x, y, z)
    with raises(DomainError, match=match.format('somefunc')):
        F(w, x, y, z)

    # Test display name
    g = get_somefunc('puppy')
    G = get_somefunc_from_static_method('puppy')
    with raises(DomainError, match=match.format('puppy')):
        g(w, x, y, z)
    with raises(DomainError, match=match.format('puppy')):
        G(w, x, y, z)

def test_incorrect_number_of_inputs_raises_useful_error():
    f = get_somefunc()
    match = r'Wrong number of arguments passed to somefunc\(...\): Expected 4 inputs, but received 2.'
    with raises(DomainError, match=match):
        f(1, 2)

    # Test min_length length argument error
    @specify_domain(input_shapes=[1], min_length=2)
    def testfunc(*args):
        return min(args)

    with raises(ArgumentError, match=r"Wrong number of arguments passed to testfunc\(...\): "
                                     r"Expected at least 2 inputs, but received 0."):
        testfunc()

def test_author_facing_decorator_raises_errors_with_invalid_config():

    match = r"required key not provided @ data\[u?'input_shapes'\]. Got None"
    with raises(Error, match=match):
        @specify_domain()
        def f():
            pass

    match = (r"expected shape specification to be a positive integer, or a "
             r"list/tuple of positive integers \(min length 1, max length None\) @ "
             r"data\[u?'input_shapes'\]\[1\]. Got 0")
    with raises(Error, match=match):
        @specify_domain(input_shapes=[5, 0, [1, 2]])
        def g():
            pass

    match = ("SpecifyDomain was called with a specified min_length, which "
             "requires input_shapes to specify only a single shape. "
             "However, 2 shapes were provided.")
    with raises(ConfigError, match=match):
        @specify_domain(input_shapes=[5, 1], min_length=2)
        def h(*args):
            pass
