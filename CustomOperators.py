'''
    Demo on adding 'custom operators'.  At least, as much as we can while
    still using python's AST system.
'''

import ast
import operator

from simpleeval import EvalWithCompoundTypes, DEFAULT_OPERATORS, PYTHON3

s = EvalWithCompoundTypes()

# Here's the only 'real' custom operator:

def custop(x, y):
    ''' Overload the ^ BitXor operator to fold functions into inline calls '''
    if callable(x):
        return x(y)
    elif callable(y):
        return lambda z:y(x,z)
    else:
        return x ^ y

s.operators[ast.BitXor] = custop

# Now we're going to use that to 'fake' any more that we want.
# The following functions and test cases are from Rod8LE:

s.functions['juggler'] = lambda x,y: y - 2 * x if (y-x)>x else y-x

s.functions['crosses_above'] = lambda t, s: t[1] > s[1] if t[0]< s[0] else False

assert s.eval('1 ^juggler^ 7') == 5
assert s.eval('[2, 4] ^crosses_above^ [2.5, 3.5]') == True
assert s.eval('(2, 3) ^crosses_above^ [2.5, 3.5]') == False

# and make sure we didn't break normal BitXor:

assert s.eval('1 ^ 2') == 1 ^ 2

# and now we can do funky text transformations to make it pretty again:

def eval2(expr):
    e = expr.replace('juggler', '^juggler^')
    e = e.replace('crosses_above', '^crosses_above^')
    return s.eval(e)

assert eval2('1 juggler 7') == 5
assert eval2('[2, 4] crosses_above [2.5, 3.5]') == True
assert eval2('(2, 3) crosses_above [2.5, 3.5]') == False

# Alas, the problem with that is that we lose the ability to use those functions
# as normal functions ( "juggler(2)" -> "^juggler^(2)".

# You could probably figure out a clever regexp to sort it out if you really
# wanted to - but I'm not clever enough.

# If we didn't mind having haskell style `backticks` for infix operators,
# then you can trivially continue to use the functions as functions too:

def eval3(expr):
    return s.eval(expr.replace('`','^'))

assert eval3('1 `juggler` 7') == 5
assert eval3('juggler(1, 7)') == 5
assert eval3('[2, 4] `crosses_above` [2.5, 3.5]') == True
assert eval3('crosses_above([2, 4], [2.5, 3.5])') == True

# Now, here's a version of eval2 (no backticks) with it all
# done automatically in a class.

class EvalWithCustomOps(EvalWithCompoundTypes):
    def __init__(self, operators=None, functions=None, names=None):
        operators[ast.BitXor] = custop
        super(EvalWithCustomOps, self).__init__(operators, functions, names)

        self.replaces = []

        for op in self.operators.keys():
            if isinstance(op, str if PYTHON3 else basestring):
                func = self.operators[op]
                self.functions[op] = func
                self.replaces.append(op)

    def eval(self, expr=None):
        if isinstance(expr, str if PYTHON3 else basestring):
            for op in self.replaces:
                expr = expr.replace(op, '^%s^' % op)
        return super(EvalWithCustomOps, self).eval(expr)

s2 = EvalWithCustomOps(operators={
    'juggler': lambda x,y: y - 2 * x if (y-x)>x else y-x,
    'crosses_above': lambda t, s: t[1] > s[1] if t[0]< s[0] else False})

assert s2.eval('1 juggler 7') == 5
assert s2.eval('[2, 4] crosses_above [2.5, 3.5]') == True
assert s2.eval('(2, 3) crosses_above [2.5, 3.5]') == False


