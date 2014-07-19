import data

"""These are the orange 'variable' blocks"""

def var(target, name):
	"""We expect a variable 'name', not the regular 'args' parameter,
	as the XML for this block is different."""
	return target.value_of_variable(name)

def doSetVar(target, args):
	name, value = (args[0].as_string(), args[1])
	return target.set_variable(name, value)
	
def doChangeVar(target, args):
	name, incr = (args[0].as_string(), args[1])
	return target.increment_variable(name, incr)

def doShowVar(target, args):
	name = args[0].as_string()
	return target.show_variable(name, True)

def doHideVar(target, args):
	name = args[0].as_string()
	return target.show_variable(name, False)

# many more to do here



	
