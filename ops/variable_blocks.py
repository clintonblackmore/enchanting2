import data

"""These are the orange 'variable' blocks"""

def var(target, args):
	name = args[0].as_string()
	v = target.get_variable(name)
	if v:
		result = v.value()
		if result:
			return result
	return data.Literal(None)

def doSetVar(target, args):
	name, value = (args[0].as_string(), args[1])
	v = target.get_variable(name)
	if v:
		v.set(value)
	return None
	
def doChangeVar(target, args):
	name, incr = (args[0].as_string(), args[1])
	v = target.get_variable(name)
	if v:
		v.set(data.Literal(v.value().as_number() + incr.as_number()))	
	return None

def doShowVar(target, args):
	name = args[0].as_string()
	v = target.get_variable(name)
	if v:
		v.show(True)
	return None

def doHideVar(target, args):
	name = args[0].as_string()
	v = target.get_variable(name)
	if v:
		v.show(False)
	return None


# many more to do here



	
