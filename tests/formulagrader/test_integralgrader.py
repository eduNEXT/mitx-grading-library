

from pytest import raises
import platform
from mitxgraders.version import __version__
from mitxgraders import CalcError
from mitxgraders.formulagrader.integralgrader import IntegralGrader, IntegrationError
from mitxgraders.exceptions import InvalidInput, ConfigError, MissingInput
from mitxgraders.sampling import DependentSampler
from tests.helpers import round_decimals_in_string

# Configuration Error Test
def test_wrong_number_of_inputs_raises_error():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        input_positions={
            'integrand': 1,
            'lower': 2,
            'upper': 3
        },
        variables=['a', 'b']
    )
    student_input = ['a', 'b']
    expected_message = (r"Expected 3 student inputs but found 2. "
                        r"Inputs should  appear in order \[u?'integrand', u?'lower', u?'upper'\].")
    with raises(ConfigError, match=expected_message):
        grader(None, student_input)

def test_duplicate_input_positions():
    expected_message = "Key input_positions has repeated indices."
    with raises(ConfigError, match=expected_message):
        IntegralGrader(
            answers={
                'lower': 'a',
                'upper': 'b',
                'integrand': 'x^2',
                'integration_variable': 'x'
            },
            input_positions={
                'integrand': 1,
                'lower': 2,
                'upper': 3,
                'integration_variable': 3
            },
            variables=['a', 'b']
        )

def test_skipped_input_positions():
    expected_message = ("Key input_positions values must be consecutive positive "
                        "integers starting at 1")
    with raises(ConfigError, match=expected_message):
        IntegralGrader(
            answers={
                'lower': 'a',
                'upper': 'b',
                'integrand': 'x^2',
                'integration_variable': 'x'
            },
            input_positions={
                'integrand': 1,
                'integration_variable': 3,
            },
            variables=['a', 'b']
        )


# Input Error Tests
def test_user_provided_integration_conflict_raises_error():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        variables=['a', 'b']
    )
    student_input = ['a', 'b', 'pi^2', 'pi']
    msg = ("Cannot use pi as integration variable; it is already has "
           "another meaning in this problem.")
    with raises(InvalidInput, match=msg):
        grader(None, student_input)

def test_user_provided_integration_variable_has_invalid_name():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        variables=['a', 'b']
    )
    student_input = ['a', 'b', '_x^2', '_x']
    msg = ("Integration variable _x is an invalid variable name."
           "Variable name should begin with a letter and contain alphanumeric"
           "characters or underscores thereafter, but may end in single quotes.")
    with raises(InvalidInput, match=msg):
        grader(None, student_input)

def test_empty_input_raises_error():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        variables=['a', 'b']
    )
    student_input = ['a', 'b', 'x^2', '']
    msg = ("Please enter a value for integration_variable, it cannot be empty.")
    with raises(MissingInput, match=msg):
        grader(None, student_input)

# Integral Evaluation tests
def test_quadratic_integral_finite():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        variables=['a', 'b'],
    )
    # The same answer as instructor
    student_input0 = ['a', 'b', 'x^2', 'x']
    # u = ln(x)
    student_input1 = ['ln(a)', 'ln(b)', 'e^(3*u)', 'u']
    expected_result = {'ok': True, 'grade_decimal': 1, 'msg': ''}
    assert grader(None, student_input0) == expected_result
    assert grader(None, student_input1) == expected_result

def test_convergent_improper_integral_on_infinite_domain():
    grader = IntegralGrader(
        answers={
            'lower': '1',
            'upper': 'infty',
            'integrand': '1/x^5',
            'integration_variable': 'x'
        },
        variables=['a', 'b'],
    )
    # The same answer as instructor
    student_input0 = ['1', 'infty', '1/x^5', 'x']
    # tan(u) = x
    student_input1 = ['pi/4', 'pi/2', '1/tan(u)^5*sec(u)^2', 'u']
    # The numerical value, integrated over interval with width 1
    student_input2 = ['0', '1', '1/4', 't']
    expected_result = {'ok': True, 'grade_decimal': 1, 'msg': ''}
    assert grader(None, student_input0) == expected_result
    assert grader(None, student_input1) == expected_result
    assert grader(None, student_input2) == expected_result

def test_convergent_improper_integral_on_finite_domain_with_poles():
    grader = IntegralGrader(
        answers={
            'lower': '-1',
            'upper': '1',
            'integrand': '1/sqrt(1-x^2)',
            'integration_variable': 'x'
        }
    )
    # The same answer as instructor
    student_input0 = ['-1', '1', '1/sqrt(1-t^2)', 't']
    # x = cos(u)
    student_input1 = ['-pi/2', 'pi/2', '1/cos(u)*cos(u)', 'u']
    expected_result = {'ok': True, 'grade_decimal': 1, 'msg': ''}
    assert grader(None, student_input0) == expected_result
    assert grader(None, student_input1) == expected_result

def test_wrong_answer():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        input_positions={
            'integrand': 1,
            'lower': 2,
            'upper': 3
        },
        variables=['a', 'b']
    )
    student_input = ['x', '2', '3']
    expect = {'grade_decimal': 0, 'msg': '', 'ok': False}
    assert grader(None, student_input) == expect

def test_author_provided_integration_variable():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        input_positions={
            'lower': 1,
            'upper': 2,
            'integrand': 3
        },
        variables=['a', 'b']
    )
    student_input = ['a', 'b', 'x^2']
    expected_result = {'ok': True, 'grade_decimal': 1, 'msg': ''}
    assert grader(None, student_input) == expected_result

def test_reordered_inputs():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        input_positions={
            'integrand': 1,
            'lower': 3,
            'upper': 2,
        },
        variables=['a', 'b']
    )
    student_input = ['x^2', 'b', 'a']
    expected_result = {'ok': True, 'grade_decimal': 1, 'msg': ''}
    assert grader(None, student_input) == expected_result

def test_integration_options_are_passed_correctly():
    grader0 = IntegralGrader(
        answers={
            'lower': '-1',
            'upper': '2',
            'integrand': '1/x',
            'integration_variable': 'x'
        }
    )
    # grader1 will pass options to scipy.integrate.quad so as to
    # avoid the singularity at x=0
    grader1 = IntegralGrader(
        answers={
            'lower': '-1',
            'upper': '2',
            'integrand': '1/x',
            'integration_variable': 'x'
        },
        integrator_options={
            'points': [0]
        }
    )
    student_input = ['-1', '2', '1/x', 'x']
    expected_result = {'ok': True, 'grade_decimal': 1, 'msg': ''}
    msg = ("There appears to be an error with the integral you entered: "
           "The integral is probably divergent, or slowly convergent.")
    # grader0 should raise an error because of singularity
    with raises(IntegrationError, match=msg):
        grader0(None, student_input)
    # grader1 avoids the singularity and should work
    assert grader1(None, student_input) == expected_result

def test_complex_integrand_grades_as_expected():
    grader = IntegralGrader(
        complex_integrand=True,
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'e^(i*x)',
            'integration_variable': 'x'
        },
        variables=['a', 'b'],
    )
    # Correct
    student_input_a = ['a', 'b', 'cos(x)+i*sin(x)', 'x']
    expected_a = {'ok': True, 'grade_decimal': 1, 'msg': ''}
    assert grader(None, student_input_a) == expected_a
    # correct real part / imag part
    student_input_b1 = ['a', 'b', 'cos(x)+i*x', 'x']
    student_input_b2 = ['a', 'b', 'x+i*sin(x)', 'x']
    expected_b = {'ok': False, 'grade_decimal': 0, 'msg': ''}
    assert grader(None, student_input_b1) == expected_b
    assert grader(None, student_input_b2) == expected_b

def test_with_single_input():
    grader = IntegralGrader(
        answers={
            'lower': '-a',
            'upper': '+a',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        input_positions = {
            'integrand': 1
        },
        variables=['a'],
    )
    # The same answer as instructor
    student_input0 = 'x^2'
    # same, but with an extra odd function that integrates to zero
    student_input1 = 'x^2 + x^3'
    assert grader(None, student_input0)['ok']
    assert grader(None, student_input1)['ok']

# Integral Evaluation Error tests
def test_learner_divergent_integral_real_part_raises_integration_error():
    msg = ("There appears to be an error with the integral you entered: "
           "The integral is probably divergent, or slowly convergent.")
    with raises(IntegrationError, match=msg):
        grader = IntegralGrader(
            answers={
                'lower': '1',
                'upper': 'infty',
                'integrand': '1/x^2',
                'integration_variable': 'x'
            }
        )
        student_input = ['0', '1', '1/x^2', 'x']
        grader(None, student_input)

def test_author_divergent_integral_real_part_raises_config_error():
    with raises(ConfigError, match="The algorithm does not converge"):
        grader = IntegralGrader(
            answers={
                'lower': '-1',
                'upper': '1',
                'integrand': '1/(x-0.276)^2',
                'integration_variable': 'x'
            }
        )
        student_input = ['-1', '1', 'x^2', 'x']
        grader(None, student_input)

def test_learner_divergent_integral_imag_part_raises_integration_error():
    msg = ("There appears to be an error with the integral you entered: "
           "The integral is probably divergent, or slowly convergent.")
    with raises(IntegrationError, match=msg):
        grader = IntegralGrader(
            complex_integrand=True,
            answers={
                'lower': '1',
                'upper': 'infty',
                'integrand': 'e^(-x) + i/x^2',
                'integration_variable': 'x'
            }
        )
        student_input = ['0', '1', 'e^(-x) + i/x^2', 'x']
        grader(None, student_input)

def test_author_divergent_integral_imag_part_raises_config_error():
    with raises(ConfigError, match="The algorithm does not converge"):
        grader = IntegralGrader(
            complex_integrand=True,
            answers={
                'lower': '-1',
                'upper': '1',
                'integrand': 'x + i/(x-0.276)^2',
                'integration_variable': 'x'
            }
        )
        student_input = ['-1', '1', 'x^2', 'x']
        grader(None, student_input)

def test_author_has_complex_limits_raises_ConfigError():
    with raises(ConfigError,
                match=(
                    "Integration Error with author's stored answer: "
                    "Integration limits must be real but have evaluated to complex numbers."
                    )
               ):
        grader = IntegralGrader(
            answers={
                'lower': '0',
                'upper': 'sqrt(1-a^2)',
                'integrand': 'x',
                'integration_variable': 'x'
            },
            variables=['a'],
            sample_from={
                'a': [2, 4]
            }
        )
        student_input = ['0', '1', 'x^2', 'x']
        grader(None, student_input)

def test_student_has_complex_limits_raises_IntegrationError():
    with raises(IntegrationError,
                match=(
                    "There appears to be an error "
                    "with the integral you entered: Integration limits "
                    "must be real but have evaluated to complex numbers."
                    )
               ):
        grader = IntegralGrader(
            answers={
                'lower': '0',
                'upper': 'a',
                'integrand': 'x',
                'integration_variable': 'x'
            },
            variables=['a'],
            sample_from={
                'a': [2, 4]
            }
        )
        student_input = ['0', 'sqrt(1-a^2)', 'x^2', 'x']
        grader(None, student_input)

def test_athor_has_unexpected_complex_integrand_raises_ConfigError():
    with raises(ConfigError, match="Integration Error with author's stored answer: Integrand"):
        grader = IntegralGrader(
            answers={
                'lower': '0',
                'upper': '1',
                'integrand': 'x+sqrt(-x)',
                'integration_variable': 'x'
            },
            variables=['a'],
            sample_from={
                'a': [2, 4]
            }
        )
        student_input = ['0', '1', 'x^2', 'x']
        grader(None, student_input)

def test_student_has_unexpected_complex_integrand_raises_IntegrationError():
    with raises(IntegrationError,
                match=(
                    "There appears to be an error "
                    "with the integral you entered: Integrand has evaluated "
                    "to complex number but must evaluate to a real."
                    )
               ):
        grader = IntegralGrader(
            answers={
                'lower': '0',
                'upper': '1',
                'integrand': 'x',
                'integration_variable': 'x'
            },
            variables=['a'],
            sample_from={
                'a': [2, 4]
            }
        )
        student_input = ['0', '1', 'x+sqrt(-x)', 'x']
        grader(None, student_input)

def test_blacklist_grading():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        variables=['a', 'b'],
        blacklist=['sin', 'cos']
    )

    # Correct answer with forbidden functions raises error
    student_input0 = ['a', 'b', 'x^2 * cos(0) + sin(0)', 'x']
    with raises(InvalidInput, match=r"Invalid Input: function\(s\) 'cos', 'sin' "
                                     "not permitted in answer"):
        grader(None, student_input0)

    # Incorrect answer with forbidden functions marked wrong
    student_input1 = ['a', 'b', 'x^2 * cos(0) + sin(pi/2)', 'x']
    assert not grader(None, student_input1)['ok']

def test_whitelist_grading():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        variables=['a', 'b'],
        whitelist=['sin', 'cos']
    )

    # Correct answer with forbidden functions raises error
    student_input0 = ['a', 'b', 'x^2 * cos(0) + tan(0)*sec(0)', 'x']
    with raises(InvalidInput, match=r"Invalid Input: function\(s\) 'sec', 'tan' "
                                    "not permitted in answer"):
        grader(None, student_input0)

    # Incorrect answer with forbidden functions marked wrong
    student_input1 = ['a', 'b', 'x^2 * cos(0) + tan(pi/4)', 'x']
    assert not grader(None, student_input1)['ok']


# Debug Test
def test_debug_message():
    grader = IntegralGrader(
        answers={
            'lower': '1',
            'upper': '8',
            'integrand': 'sin(s)',
            'integration_variable': 's'
        },
        debug=True,
        samples=2
    )
    student_input = ['1', '8', 'sin(x)', 'x']
    expected_message = (
        "<pre>MITx Grading Library Version {version}<br/>\n"
        "Running on edX using python {python_version}<br/>\n"
        "Student Responses:<br/>\n"
        "1<br/>\n"
        "8<br/>\n"
        "sin(x)<br/>\n"
        "x<br/>\n"
        "<br/>\n"
        "==============================================================<br/>\n"
        "IntegralGrader Debug Info<br/>\n"
        "==============================================================<br/>\n"
        "Functions available during evaluation and allowed in answer:<br/>\n"
        "{{'abs': <function absolute at 0x...>,<br/>\n"
        " 'arccos': <function arccos at 0x...>,<br/>\n"
        " 'arccosh': <function arccosh at 0x...>,<br/>\n"
        " 'arccot': <function arccot at 0x...>,<br/>\n"
        " 'arccoth': <function arccoth at 0x...>,<br/>\n"
        " 'arccsc': <function arccsc at 0x...>,<br/>\n"
        " 'arccsch': <function arccsch at 0x...>,<br/>\n"
        " 'arcsec': <function arcsec at 0x...>,<br/>\n"
        " 'arcsech': <function arcsech at 0x...>,<br/>\n"
        " 'arcsin': <function arcsin at 0x...>,<br/>\n"
        " 'arcsinh': <function arcsinh at 0x...>,<br/>\n"
        " 'arctan': <function arctan at 0x...>,<br/>\n"
        " 'arctan2': <function arctan2 at 0x...>,<br/>\n"
        " 'arctanh': <function arctanh at 0x...>,<br/>\n"
        " 'ceil': <function ceil at 0x...>,<br/>\n"
        " 'conj': &lt;ufunc 'conjugate'&gt;,<br/>\n"
        " 'cos': <function cos at 0x...>,<br/>\n"
        " 'cosh': <function cosh at 0x...>,<br/>\n"
        " 'cot': <function cot at 0x...>,<br/>\n"
        " 'coth': <function coth at 0x...>,<br/>\n"
        " 'csc': <function csc at 0x...>,<br/>\n"
        " 'csch': <function csch at 0x...>,<br/>\n"
        " 'exp': <function exp at 0x...>,<br/>\n"
        " 'fact': <function factorial at 0x...>,<br/>\n"
        " 'factorial': <function factorial at 0x...>,<br/>\n"
        " 'floor': <function floor at 0x...>,<br/>\n"
        " 'im': <function imag at 0x...>,<br/>\n"
        " 'kronecker': <function kronecker at 0x...>,<br/>\n"
        " 'ln': <function log at 0x...>,<br/>\n"
        " 'log10': <function log10 at 0x...>,<br/>\n"
        " 'log2': <function log2 at 0x...>,<br/>\n"
        " 'max': <function max at 0x...>,<br/>\n"
        " 'min': <function min at 0x...>,<br/>\n"
        " 're': <function real at 0x...>,<br/>\n"
        " 'sec': <function sec at 0x...>,<br/>\n"
        " 'sech': <function sech at 0x...>,<br/>\n"
        " 'sin': <function sin at 0x...>,<br/>\n"
        " 'sinh': <function sinh at 0x...>,<br/>\n"
        " 'sqrt': <function sqrt at 0x...>,<br/>\n"
        " 'tan': <function tan at 0x...>,<br/>\n"
        " 'tanh': <function tanh at 0x...>}}<br/>\n"
        "Functions available during evaluation and disallowed in answer:<br/>\n"
        "{{}}<br/>\n"
        "<br/>\n"
        "<br/>\n"
        "==============================================<br/>\n"
        "Integration Data for Sample Number 1 of 2<br/>\n"
        "==============================================<br/>\n"
        "Variables: {{'e': 2.718281828459045,<br/>\n"
        " 'i': 1j,<br/>\n"
        " 'infty': inf,<br/>\n"
        " 'j': 1j,<br/>\n"
        " 'pi': 3.141592653589793,<br/>\n"
        " 's': 5.530375019455111,<br/>\n"
        " 'x': 5.530375019455111}}<br/>\n"
        "<br/>\n"
        "========== Student Integration Data, Real Part<br/>\n"
        "Numerical Value: 0.685802339677<br/>\n"
        "Error Estimate: 5.23517337969e-14<br/>\n"
        "Number of integrand evaluations: 21<br/>\n"
        "========== Student Integration Data, Imaginary Part<br/>\n"
        "Numerical Value: None<br/>\n"
        "Error Estimate: None<br/>\n"
        "Number of integrand evaluations: None<br/>\n"
        "<br/>\n"
        "========== Author Integration Data, Real Part<br/>\n"
        "Numerical Value: 0.685802339677<br/>\n"
        "Error Estimate: 5.23517337969e-14<br/>\n"
        "Number of integrand evaluations: 21<br/>\n"
        "========== Author Integration Data, Imaginary Part<br/>\n"
        "Numerical Value: None<br/>\n"
        "Error Estimate: None<br/>\n"
        "Number of integrand evaluations: None<br/>\n"
        "<br/>\n"
        "<br/>\n"
        "==============================================<br/>\n"
        "Integration Data for Sample Number 2 of 2<br/>\n"
        "==============================================<br/>\n"
        "Variables: {{'e': 2.718281828459045,<br/>\n"
        " 'i': 1j,<br/>\n"
        " 'infty': inf,<br/>\n"
        " 'j': 1j,<br/>\n"
        " 'pi': 3.141592653589793,<br/>\n"
        " 's': 5.530375019455111,<br/>\n"
        " 'x': 5.530375019455111}}<br/>\n"
        "<br/>\n"
        "========== Student Integration Data, Real Part<br/>\n"
        "Numerical Value: 0.685802339677<br/>\n"
        "Error Estimate: 5.23517337969e-14<br/>\n"
        "Number of integrand evaluations: 21<br/>\n"
        "========== Student Integration Data, Imaginary Part<br/>\n"
        "Numerical Value: None<br/>\n"
        "Error Estimate: None<br/>\n"
        "Number of integrand evaluations: None<br/>\n"
        "<br/>\n"
        "========== Author Integration Data, Real Part<br/>\n"
        "Numerical Value: 0.685802339677<br/>\n"
        "Error Estimate: 5.23517337969e-14<br/>\n"
        "Number of integrand evaluations: 21<br/>\n"
        "========== Author Integration Data, Imaginary Part<br/>\n"
        "Numerical Value: None<br/>\n"
        "Error Estimate: None<br/>\n"
        "Number of integrand evaluations: None<br/>\n"
        "<br/>\n"
        "<br/>\n"
        "==========================================<br/>\n"
        "Comparison Data for All 2 Samples<br/>\n"
        "==========================================<br/>\n"
        "Comparer Function: EqualityComparer({{'transform': <function identity_transform at 0x...>}})<br/>\n"
        "Comparison Results:<br/>\n"
        "[{{'grade_decimal': 1.0, 'msg': '', 'ok': True}},<br/>\n"
        " {{'grade_decimal': 1.0, 'msg': '', 'ok': True}}]<br/>\n"
        "</pre>"
    ).format(version=__version__, python_version=platform.python_version())
    expected_message = expected_message.replace("<func", "&lt;func").replace("...>", "...&gt;")
    expected_message = round_decimals_in_string(expected_message)
    result = grader(None, student_input)
    assert result['ok'] is True
    assert result['grade_decimal'] == 1.0
    assert expected_message == round_decimals_in_string(result['msg'])

def test_debug_message_complex_integrand():
    grader = IntegralGrader(
        complex_integrand=True,
        answers={
            'lower': '-2',
            'upper': '4',
            'integrand': 'cos(s) + i*sin(s)',
            'integration_variable': 's'
        },
        debug=True
    )
    student_input = ['-1', '5', 'sqrt(x)', 'x']
    expected_message = (
        "<pre>MITx Grading Library Version {version}<br/>\n"
        "Running on edX using python {python_version}<br/>\n"
        "Student Responses:<br/>\n"
        "-1<br/>\n"
        "5<br/>\n"
        "sqrt(x)<br/>\n"
        "x<br/>\n"
        "<br/>\n"
        "==============================================================<br/>\n"
        "IntegralGrader Debug Info<br/>\n"
        "==============================================================<br/>\n"
        "Functions available during evaluation and allowed in answer:<br/>\n"
        "{{'abs': <function absolute at 0x...>,<br/>\n"
        " 'arccos': <function arccos at 0x...>,<br/>\n"
        " 'arccosh': <function arccosh at 0x...>,<br/>\n"
        " 'arccot': <function arccot at 0x...>,<br/>\n"
        " 'arccoth': <function arccoth at 0x...>,<br/>\n"
        " 'arccsc': <function arccsc at 0x...>,<br/>\n"
        " 'arccsch': <function arccsch at 0x...>,<br/>\n"
        " 'arcsec': <function arcsec at 0x...>,<br/>\n"
        " 'arcsech': <function arcsech at 0x...>,<br/>\n"
        " 'arcsin': <function arcsin at 0x...>,<br/>\n"
        " 'arcsinh': <function arcsinh at 0x...>,<br/>\n"
        " 'arctan': <function arctan at 0x...>,<br/>\n"
        " 'arctan2': <function arctan2 at 0x...>,<br/>\n"
        " 'arctanh': <function arctanh at 0x...>,<br/>\n"
        " 'ceil': <function ceil at 0x...>,<br/>\n"
        " 'conj': &lt;ufunc 'conjugate'&gt;,<br/>\n"
        " 'cos': <function cos at 0x...>,<br/>\n"
        " 'cosh': <function cosh at 0x...>,<br/>\n"
        " 'cot': <function cot at 0x...>,<br/>\n"
        " 'coth': <function coth at 0x...>,<br/>\n"
        " 'csc': <function csc at 0x...>,<br/>\n"
        " 'csch': <function csch at 0x...>,<br/>\n"
        " 'exp': <function exp at 0x...>,<br/>\n"
        " 'fact': <function factorial at 0x...>,<br/>\n"
        " 'factorial': <function factorial at 0x...>,<br/>\n"
        " 'floor': <function floor at 0x...>,<br/>\n"
        " 'im': <function imag at 0x...>,<br/>\n"
        " 'kronecker': <function kronecker at 0x...>,<br/>\n"
        " 'ln': <function log at 0x...>,<br/>\n"
        " 'log10': <function log10 at 0x...>,<br/>\n"
        " 'log2': <function log2 at 0x...>,<br/>\n"
        " 'max': <function max at 0x...>,<br/>\n"
        " 'min': <function min at 0x...>,<br/>\n"
        " 're': <function real at 0x...>,<br/>\n"
        " 'sec': <function sec at 0x...>,<br/>\n"
        " 'sech': <function sech at 0x...>,<br/>\n"
        " 'sin': <function sin at 0x...>,<br/>\n"
        " 'sinh': <function sinh at 0x...>,<br/>\n"
        " 'sqrt': <function sqrt at 0x...>,<br/>\n"
        " 'tan': <function tan at 0x...>,<br/>\n"
        " 'tanh': <function tanh at 0x...>}}<br/>\n"
        "Functions available during evaluation and disallowed in answer:<br/>\n"
        "{{}}<br/>\n"
        "<br/>\n"
        "<br/>\n"
        "==============================================<br/>\n"
        "Integration Data for Sample Number 1 of 1<br/>\n"
        "==============================================<br/>\n"
        "Variables: {{'e': 2.718281828459045,<br/>\n"
        " 'i': 1j,<br/>\n"
        " 'infty': inf,<br/>\n"
        " 'j': 1j,<br/>\n"
        " 'pi': 3.141592653589793,<br/>\n"
        " 's': 1.8831785881043805,<br/>\n"
        " 'x': 0.022981166359782736}}<br/>\n"
        "<br/>\n"
        "========== Student Integration Data, Real Part<br/>\n"
        "Numerical Value: 7.453559925<br/>\n"
        "Error Estimate: 8.27511384416e-15<br/>\n"
        "Number of integrand evaluations: 357<br/>\n"
        "========== Student Integration Data, Imaginary Part<br/>\n"
        "Numerical Value: 0.666666666667<br/>\n"
        "Error Estimate: 7.40148683083e-16<br/>\n"
        "Number of integrand evaluations: 357<br/>\n"
        "<br/>\n"
        "========== Author Integration Data, Real Part<br/>\n"
        "Numerical Value: 0.152494931518<br/>\n"
        "Error Estimate: 4.2752835891e-14<br/>\n"
        "Number of integrand evaluations: 21<br/>\n"
        "========== Author Integration Data, Imaginary Part<br/>\n"
        "Numerical Value: 0.237496784316<br/>\n"
        "Error Estimate: 4.1882074502e-14<br/>\n"
        "Number of integrand evaluations: 21<br/>\n"
        "<br/>\n"
        "<br/>\n"
        "==========================================<br/>\n"
        "Comparison Data for All 1 Samples<br/>\n"
        "==========================================<br/>\n"
        "Comparer Function: EqualityComparer({{'transform': <function identity_transform at 0x...>}})<br/>\n"
        "Comparison Results:<br/>\n"
        "[{{'grade_decimal': 0, 'msg': '', 'ok': False}}]<br/>\n"
        "</pre>"
    ).format(version=__version__, python_version=platform.python_version())
    expected_message = expected_message.replace("<func", "&lt;func").replace("...>", "...&gt;")
    expected_message = round_decimals_in_string(expected_message)
    result = grader(None, student_input)
    assert result['ok'] is False
    assert result['grade_decimal'] == 0.0
    assert expected_message == round_decimals_in_string(result['msg'])

def test_error_catching():
    grader = IntegralGrader(
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': 'x^2',
            'integration_variable': 'x'
        },
        input_positions={
            'integrand': 1,
            'lower': 2,
            'upper': 3
        },
        variables=['a', 'b']
    )
    student_input = ['1+', '1', '2']
    expected_message = r"Invalid Input: Could not parse '1\+' as a formula"
    with raises(CalcError, match=expected_message):
        grader(None, student_input)

    student_input = ['1/0', '1', '2']
    expected_message = ("Division by zero occurred. Check your input's denominators.")
    with raises(CalcError, match=expected_message):
        grader(None, student_input)

def test_integral_with_complex_integrand():
    grader = IntegralGrader(
        complex_integrand=True,
        answers={
            'lower': 'a',
            'upper': 'b',
            'integrand': '(cos(q) + i*sin(q))^2',
            'integration_variable': 'q'
        },
        variables=['a', 'b'],
    )
    # Correct answers
    correct_input0 = ['a', 'b', 'cos(2*t) + i * sin(2*t)', 't']
    correct_input1 = ['a', 'b', 'cos(2*t) + i * sin(2*t)', 't']
    # Incorrect answers
    wrong_input0 = ['a', 'b', 'i*cos(2*t) + sin(2*t)', 't']
    wrong_input1 = ['a', 'b', 'cos(2*w)', 'w']
    wrong_input2 = ['a', 'b', 'i*sin(2*q)', 'q']

    correct_result0 = grader(None, correct_input0)
    correct_result1 = grader(None, correct_input1)
    wrong_result0 = grader(None, wrong_input0)
    wrong_result1 = grader(None, wrong_input1)
    wrong_result2 = grader(None, wrong_input2)

    correct_expected_result = {'ok': True, 'grade_decimal': 1, 'msg': ''}
    wrong_expected_result = {'ok': False, 'grade_decimal': 0, 'msg': ''}

    assert correct_result0 == correct_expected_result
    assert correct_result1 == correct_expected_result
    assert wrong_result0 == wrong_expected_result
    assert wrong_result1 == wrong_expected_result
    assert wrong_result2 == wrong_expected_result

def test_numbered_vars():
    grader = IntegralGrader(
        answers={
            'lower': '0',
            'upper': '1',
            'integrand': 'a_{2}*x',
            'integration_variable': 'x'
        },
        numbered_vars=['a'],
    )
    # Correct answers
    correct_input = ['0', '1', 't*a_{2}', 't']
    # Incorrect answers
    wrong_input = ['0', '1', 't*a_{3}', 't']

    correct_result = grader(None, correct_input)
    wrong_result = grader(None, wrong_input)

    assert correct_result == {'ok': True, 'grade_decimal': 1, 'msg': ''}
    assert wrong_result == {'ok': False, 'grade_decimal': 0, 'msg': ''}

def test_suffixes():
    grader = IntegralGrader(
        answers={
            'lower': '1m',
            'upper': '1e9',
            'integrand': '1%*x',
            'integration_variable': 'x'
        },
        metric_suffixes=True
    )
    assert grader(None, ['1e-3', '1G', 't/100', 't']) == {'ok': True, 'grade_decimal': 1, 'msg': ''}

def test_instructor_vars():
    """Ensures that instructor variables are not available to students"""
    grader = IntegralGrader(
        answers={
            'lower': '0',
            'upper': '1',
            'integrand': 'c*t',
            'integration_variable': 't'
        },
        input_positions={
            'integrand': 1
        },
        variables=['x', 'c'],
        sample_from={
            'x': [-3.14159, 3.14159],
            'c': DependentSampler(depends=["x"], formula="cos(x)")
        },
        instructor_vars=['c', 'pi', 'nothere']  # nothere will be ignored
    )

    assert grader(None, 'cos(x)*t')['ok']
    with raises(CalcError, match="'c' not permitted in answer as a variable"):
        grader(None, 'c*t')
    with raises(CalcError, match="'pi' not permitted in answer as a variable"):
        grader(None, 'pi*t')

def test_forbidden():
    """Ensures that answers don't contain forbidden strings"""
    grader = IntegralGrader(
        answers={
            'lower': '0',
            'upper': '1',
            'integrand': '2*t',
            'integration_variable': 't'
        },
        forbidden_strings=['+'],
        forbidden_message='No addition!'
    )
    assert grader(None, ['0', '1', '2*t', 't'])['ok']
    with raises(InvalidInput, match="No addition!"):
        grader(None, ['0', '1', 't+t', 't'])
    with raises(InvalidInput, match="No addition!"):
        grader(None, ['0', '0+1', '2*t', 't'])

def test_required_funcs():
    """Ensures that required functions must be used"""
    grader = IntegralGrader(
        answers={
            'lower': '0',
            'upper': '1',
            'integrand': 'tan(x)',
            'integration_variable': 'x'
        },
        input_positions={
            'integrand': 1
        },
        required_functions=['tan']
    )

    assert grader(None, 'tan(x)')['ok']
    with raises(InvalidInput, match="Answer must contain the function tan"):
        grader(None, 'sin(x)/cos(x)')
