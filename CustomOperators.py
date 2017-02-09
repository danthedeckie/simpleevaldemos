'''
    Demo on adding 'custom operators'.  At least, as much as we can while
    still using python's AST system.
'''

import ast
import operator

from simpleeval import EvalWithCompoundTypes, DEFAULT_OPERATORS

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

s.functions['juggler'] = lambda x,y: y - 2 * x if (y-x)>x else y-x

s.functions['crosses_above'] = lambda t, s: t[1] > s[1] if t[0]< s[0] else False

assert s.eval('1 ^juggler^ 7') == 5
assert s.eval('[2, 4] ^crosses_above^ [2.5, 3.5]') == True
assert s.eval('(2, 3) ^crosses_above^ [2.5, 3.5]') == False

# and make sure we didn't break normal BitXor:

assert s.eval('1 ^ 2') == 1 ^ 2
