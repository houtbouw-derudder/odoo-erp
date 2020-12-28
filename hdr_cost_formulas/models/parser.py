from pyparsing import delimitedList, Forward, Group, Literal, OneOrMore, Or, ParseResults, ParseException, Regex, Suppress, Word, ZeroOrMore, alphas, alphanums
from math import ceil


class ExpressionException(Exception):
    def __init__(self, message):
        self.message = message


_op_funcs = {}
_op_funcs['and'] = lambda a, b: a and b
_op_funcs['or'] = lambda a, b: a or b
_op_funcs['='] = lambda a, b: a == b
_op_funcs['!='] = lambda a, b: a != b
_op_funcs['<'] = lambda a, b: a < b
_op_funcs['<='] = lambda a, b: a <= b
_op_funcs['>'] = lambda a, b: a > b
_op_funcs['>='] = lambda a, b: a >= b
_op_funcs['+'] = lambda a, b: a + b
_op_funcs['-'] = lambda a, b: a - b
_op_funcs['*'] = lambda a, b: a * b
_op_funcs['/'] = lambda a, b: a / b
_op_funcs['round'] = lambda val, prec: round(
    val * (10 ** int(prec))) / (10 ** int(prec))
_op_funcs['ceil'] = lambda val, prec: ceil(val / prec) * prec


def _parse_numeric(tok):
    return ('value', float(tok[0]))


def _parse_text(tok):
    return ('value', str(tok[0]))


def _parse_param(tok):
    return ('param', tok[0])


def _parse_grouped_expr(tok):
    return [tok]


def _parse_function(tok):
    return ('function', tok[0], list(tok[1]), list(tok[-1]))


_lpar = Suppress("(")
_rpar = Suppress(")")
_quote = Suppress("'")
_func_name = Or(map(Literal, ['round', 'ceil']))

_param = Word(alphas, alphanums + '_').setParseAction(_parse_param)
_param_list = delimitedList(_param)
_numeric = Regex(r"[+-]?\d+(?:\.\d*)?").setParseAction(_parse_numeric)
_textual = (_quote + Word(alphanums + "-_") +
            _quote).setParseAction(_parse_text)

_math_operations = ['*', '/', '+', '-']
_math_oper = Or(map(Literal, _math_operations))
_math_expr = Forward()
_math_func = (_func_name + _lpar + _math_expr + Suppress(",") +
              _math_expr.setParseAction(_parse_grouped_expr) + _rpar).setParseAction(_parse_function)
_math_operand = _math_func | _param | _numeric | (
    _lpar + _math_expr + _rpar).setParseAction(_parse_grouped_expr)
_math_expr <<= _math_operand + ZeroOrMore(_math_oper + _math_operand)

_comparison_operations = ['=', '!=', '<', '>', '<=', '>=']
_comparison_oper = Or(map(Literal, _comparison_operations))
_comparison_expr = Forward()
_comparison_operand = _math_expr | _textual | (
    _lpar + _comparison_expr + _rpar).setParseAction(_parse_grouped_expr)
_comparison_expr <<= (_comparison_operand + _comparison_oper +
                      _comparison_operand).setParseAction(_parse_grouped_expr)

_logical_operations = ['and', 'or']
_logical_oper = Or(map(Literal, _logical_operations))
_logical_expr = Forward()
_logical_operand = _comparison_expr | (
    _lpar + _logical_expr + _rpar).setParseAction(_parse_grouped_expr)
_logical_expr <<= _logical_operand + \
    ZeroOrMore(_logical_oper + _logical_operand)


def _extract_parameters(parsed):
    if isinstance(parsed, ParseResults) or isinstance(parsed, list):
        result = []
        for val in map(_extract_parameters, list(parsed)):
            result = result + val
        unique = []
        for x in result:
            if x not in unique:
                unique.append(x)

        return unique
    elif isinstance(parsed, tuple):
        if parsed[0] == "param":
            return [parsed[1]]
        elif parsed[0] == "function":
            return _extract_parameters(parsed[2]) + _extract_parameters(parsed[3])
        else:
            return []
    else:
        return []


def validate_parameter_list(params):
    try:
        if params is None or len(params.strip()) < 1:
            return

        _param_list.parseString(params, parseAll=True)
    except ParseException as parseEx:
        raise ExpressionException(str(parseEx))


def _validate_expression(grammar, expression, params):
    try:
        parsed = grammar.parseString(expression, parseAll=True)
        used_parameters = _extract_parameters(parsed)

        defined_parameters = []
        if params is not None and len(params.strip()) > 1:
            parsed_params = _param_list.parseString(params, parseAll=True)
            defined_parameters = _extract_parameters(parsed_params)
    except ParseException as parseEx:
        raise ExpressionException(str(parseEx))

    undefined = [p for p in used_parameters if p not in defined_parameters]
    if len(undefined) > 0:
        raise ExpressionException(
            "Undefined parameters: {0}".format(undefined))


def validate_math_expression(expression, params):
    _validate_expression(_math_expr, expression, params)


def validate_logical_expression(expression, params):
    _validate_expression(_logical_expr, expression, params)


def _evaluate_operator(group, operator_index):
    l, op, r = group[operator_index - 1: operator_index + 2]
    r = _op_funcs[op](l, r)
    return group[0:operator_index - 1] + [r] + group[operator_index + 2:]


def _evaluate_group(group):
    operators = _math_operations + _comparison_operations
    temp = list(group)

    while len([x for x in temp if x in operators]) > 0:
        for op in operators:
            op_pos = [idx for idx in range(0, len(temp)) if temp[idx] == op]
            if len(op_pos) > 0:
                temp = _evaluate_operator(temp, op_pos[0])
                break

    while len(temp) > 2:
        l, op, r = temp[0:3]
        temp = [_op_funcs[op](l, r)] + temp[3:]

    if len(temp) < 2:
        return temp[0]
    else:
        raise ExpressionException("TODO")


def _evaluate_parsed_expression(parsed_expression, parameter_values):
    if isinstance(parsed_expression, ParseResults) or isinstance(parsed_expression, list):
        evaluated = [_evaluate_parsed_expression(
            elem, parameter_values) for elem in parsed_expression]

        non_simple_values = [x for x in evaluated if isinstance(
            x, ParseResults) or isinstance(x, list) or isinstance(x, tuple)]
        if len(non_simple_values) > 0:
            print("some non-simple values are left")
            raise ExpressionException("Unknown situation")
        else:
            if len(evaluated) == 1:
                return evaluated[0]
            elif len(evaluated) == 2:
                raise ExpressionException("Unknown situation")
            else:
                return _evaluate_group(evaluated)
    elif isinstance(parsed_expression, tuple):
        if parsed_expression[0] == 'value':
            return parsed_expression[1]
        elif parsed_expression[0] == 'param':
            return parameter_values[parsed_expression[1]]
        elif parsed_expression[0] == 'function':
            func_name = parsed_expression[1]
            func_expr = _evaluate_parsed_expression(
                parsed_expression[2], parameter_values)
            func_arg = _evaluate_parsed_expression(
                parsed_expression[3], parameter_values)
            return _op_funcs[func_name](func_expr, func_arg)
        else:
            raise ExpressionException("Unknown situation")
    else:
        return parsed_expression


def _evaluate_expression(grammar, expression, parameter_values):
    try:
        parsed = grammar.parseString(expression, parseAll=True)
        return _evaluate_parsed_expression(parsed, parameter_values)
    except ParseException as parseEx:
        raise ExpressionException(str(parseEx))


def evaluate_math_expression(expression, parameter_values):
    return _evaluate_expression(_math_expr, expression, parameter_values)


def evaluate_logical_expression(expression, parameter_values):
    return _evaluate_expression(_logical_expr, expression, parameter_values)
