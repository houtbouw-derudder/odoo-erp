from pyparsing import Forward, Literal, Or, ParseResults, ParseException, Regex, Suppress, Word, ZeroOrMore, alphas, alphanums
from math import ceil

def _parse_numeric(tok):
    return ('value', float(tok[0]))


def _parse_param(tok):
    return ('param', tok[0])


def _parse_function(tok):
    return ('function', tok[0], tok[1:-1], tok[-1])


def _parse_grouped_expr(tok):
    return [tok]


def _get_grammar():
    lpar, rpar = map(Suppress, "()")
    oper = Or(map(Literal, "+-/*"))
    param = Word(alphas, alphanums + "_").setParseAction(_parse_param)
    numeric = Regex(r"[+-]?\d+(?:\.\d*)?").setParseAction(_parse_numeric)
    func_names = Or(map(Literal, ['round', 'ceil']))

    expr = Forward()
    func = (func_names + lpar + expr + Suppress(",") +
            expr.setParseAction(_parse_grouped_expr) + rpar).setParseAction(_parse_function)
    operand = func | param | numeric | (
        lpar + expr + rpar).setParseAction(_parse_grouped_expr)
    expr <<= operand + ZeroOrMore(oper + operand)

    return expr


def parse(expression):
    return _get_grammar().parseString(expression, parseAll=True)


def extract_parameters(parsed):
    if isinstance(parsed, list) or isinstance(parsed, ParseResults):
        params = []

        for elem in parsed:
            params = params + extract_parameters(elem)

        return list(set(params))
    elif isinstance(parsed, tuple):
        if parsed[0] == 'param':
            return [parsed[1]]
        elif parsed[0] == 'function':
            return extract_parameters(parsed[2]) + extract_parameters(parsed[3])
        else:
            return []
    else:
        return []

def _round_func(value, precision):
    factor = 10 ** int(precision)
    return round(value * factor) / factor

def _ceil_func(value, precision):
    return ceil(value / precision) * precision
    
_func_impl = {
    'round': _round_func,
    'ceil': _ceil_func
}

def _add(a, b):
    return a + b

def _subtract(a, b):
    return a - b

def _multiply(a, b):
    return a * b

def _divide(a, b):
    return a / b

_op_impl = {
    '+': _add,
    '-': _subtract,
    '*': _multiply,
    '/': _divide
}

def _do_calculate(args, idx):
    l, op, r = args[idx - 1: idx + 2]
    r = _op_impl[op](l, r)
    return args[0:idx - 1] + [r] + args[idx + 2:]

def _calculate(args):
    temp = list(args)
    while len(temp) > 1:
        for op in "*/+-":
            op_pos = [idx for idx in range(0, len(temp)) if temp[idx] == op]
            if len(op_pos) > 0:
                temp = _do_calculate(temp, op_pos[0])
                break

    return temp[0]

def evaluate(parsed, vals):
    if isinstance(parsed, list) or isinstance(parsed, ParseResults):
        evaluated = [evaluate(elem, vals) for elem in parsed]
        non_simple_values = [elem for elem in evaluated if isinstance(elem, list) or isinstance(elem, ParseResults) or isinstance(elem, list)]
        if len(non_simple_values) > 0:
            print("still contains non_simple_values")
        else:
            if len(evaluated) == 1:
                return evaluated[0]
            elif len(evaluated) == 2:
                raise RuntimeError("Bizare situation detected")
            else:
                return _calculate(evaluated)
        
        return evaluated
    elif isinstance(parsed, tuple):
        if parsed[0] == 'value':
            return parsed[1]
        elif parsed[0] == 'param':
            if parsed[1] not in list(vals.keys()):
                raise RuntimeError("Key '{0}' not found in provided values".format(parsed[1]))
            return vals[parsed[1]]
        elif parsed[0] == 'function':
            func_name = parsed[1]
            evaluated = evaluate(parsed[2], vals)
            func_args = evaluate(parsed[3], vals)
            return _func_impl[func_name](evaluated, func_args)
        else:
            raise RuntimeError("Unsupported tuple")
    else:
        return parsed

