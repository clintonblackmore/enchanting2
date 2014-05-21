from core import Literal

"""These are the orange 'variable' blocks"""

def var(target, args):
	name = args[0].as_string()
	return target.variables.get_value_of(name)

def doSetVar(target, args):
	name, value = (args[0].as_string(), args[1])
	target.variables.set(name, value)
	return None
	
def doChangeVar(target, args):
	name, value = (args[0].as_string(), args[1])
	target.variables.increment(name, value)
	return None

def doShowVar(target, args):
	name = args[0].as_string()
	target.variables.show(name, True)
	return None

def doHideVar(target, args):
	name = args[0].as_string()
	target.variables.show(name, False)
	return None


# many more to do here



	
