
"""This package contains a number of functions that
operate on sprites or classes.  You look up the function
that you want using ops.bind_to_function("function_name").
This setup (as opposed to being class methods) allows
for easily adding to the block library, and lets you bind
to a function when you don't know which sprite you are going
to operate on."""


# Make the most useful function readily available
# (through it, a client gets at all the other functions)
from utilities import bind_to_function

