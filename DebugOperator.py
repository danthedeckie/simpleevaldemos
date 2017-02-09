'''
    Abusing the ~ Invert operator to have a debug/print side-effect.
'''

import ast
from simpleeval import SimpleEval

def print_thing(x):
    print('DEBUG: %s' % x)
    return x

s = SimpleEval()
s.operators[ast.Invert] = print_thing

print(s.eval('100 + ~randint(200)'))
