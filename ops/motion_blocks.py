#import data

"""These are the blue 'motion' blocks"""

def gotoXY(target, args):
	x, y = args[0], args[1]
	target.set_variable("@x", x)
	target.set_variable("@y", y)
	return None

	
def setXPosition(target, args):
	value = args[0]
	return target.set_variable("@x", value)
	
def changeXPosition(target, args):
	incr = args[0]
	return target.increment_variable("@x", incr)
	
def xPosition(target, args):
	return target.value_of_variable("@x")

	
def setYPosition(target, args):
	value = args[0]
	return target.set_variable("@y", value)
	
def changeYPosition(target, args):
	incr = args[0]
	return target.increment_variable("@y", incr)
	
def yPosition(target, args):
	return target.value_of_variable("@y")
	

# to do -- lots!