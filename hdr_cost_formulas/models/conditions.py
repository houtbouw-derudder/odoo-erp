from pyparsing import Forward, Group, Literal, Or, ParseResults, Regex, Suppress, Word, ZeroOrMore, alphas, alphanums

def _parse_numeric(tok):
    return float(tok[0])

def _parse_expr(tok):
    return [(g[0], g[1], g[2]) for g in tok]

def _parse_grouped_expr(tok):
    return [tok]

def _get_grammar():
    lpar, rpar, quote = map(Suppress, "()'")
    param = Word(alphas, alphanums + "_")
    oper = Or(map(Literal, ['=', '!=', '<', '>', '<=', '>=']))
    logical_op = Or(map(Literal, ['and', 'or']))
    numeric = Regex(r"[+-]?\d+(?:\.\d*)?").setParseAction(_parse_numeric)
    textual = (quote + Word(alphanums + '-_ ') + quote)
    atom_expr = Group(param + oper + (numeric | textual) | lpar + param + oper + (numeric | textual) + rpar).setParseAction(_parse_expr)
    expr = Forward()
    expr <<= (atom_expr + ZeroOrMore(logical_op + expr)) | (lpar + atom_expr + ZeroOrMore(logical_op + expr) + rpar).setParseAction(_parse_grouped_expr)
    return expr + ZeroOrMore(logical_op + expr)

def parse(condition):
    return _get_grammar().parseString(condition, parseAll=True)

def _and_func(a, b):
    return a and b

def _or_func(a, b):
    return a or b

def _equal_func(a, b):
    return a == b

def _inequal_func(a, b):
    return a != b

def _lt_func(a, b):
    return a < b

def _le_func(a, b):
    return a <= b

def _gt_func(a, b):
    return a > b

def _ge_func(a, b):
    return a >= b

_op_funcs = {
    'and': _and_func,
    'or': _or_func,
    '=': _equal_func,
    '!=': _inequal_func,
    '<': _lt_func,
    '<=': _le_func,
    '>': _gt_func,
    '>=': _ge_func
}

def extract_parameters(parsed):
    params = []

    if isinstance(parsed, list) or isinstance(parsed, ParseResults):
        if len(parsed) >= 3:
            l, op, r = parsed[:3]
            params = params + extract_parameters(l)
            params = params + extract_parameters(r)

            remaining = parsed[3:]
            if len(remaining > 1):
                params = params + extract_parameters(remaining)
    elif isinstance(parsed, tuple):
        return [parsed[0]]

    return params

def evaluate(result, vals):
    if isinstance(result, list) or isinstance(result, ParseResults):
        if len(result) < 3:
            return evaluate(result[0], vals)

        l, op, r = result[:3]
        _result = [_op_funcs[op](evaluate(l, vals), evaluate(r, vals))] + result[3:]
        if len(_result) > 1:
            return evaluate(_result, vals)
        else:
            return _result[0]
        
    elif isinstance(result, tuple):
        param, op, val = result
        if param not in list(vals.keys()):
            raise RuntimeError("No value for param: {0}".format(param))

        param_val = vals[param]
        return _op_funcs[op](param_val, val)
    elif isinstance(result, bool):
        return result
    else:
        raise RuntimeError("Unsupported data type {0} {1}".format(result, type(result)))

if __name__ == "__main__":
    import unittest

    class ConditionsTest(unittest.TestCase):

        def test_parse_string_value(self):
            try:
                parsed = parse("dries = '0-600'")
                self.assertIsInstance(parsed, ParseResults)
            finally:
                pass
        
        def test_parse_float_value(self):
            try:
                parsed = parse("dries < 600")
                self.assertIsInstance(parsed, ParseResults)
            finally:
                pass

    unittest.main()