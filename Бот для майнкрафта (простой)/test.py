from my_types import *

a = String.write('aboba') + String.write('hi')
print(a)
b, index = String.read(a, 0)
print(b)
b, index = String.read(a, index)
print(b)