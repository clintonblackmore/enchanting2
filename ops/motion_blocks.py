#import data

"""These are the blue 'motion' blocks"""

def gotoXY(target_actor, parent_script, args):
	x, y = args[0], args[1]
	target_actor.set_variable("@x", x)
	target_actor.set_variable("@y", y)
	return None

	
def setXPosition(target_actor, parent_script, args):
	value = args[0]
	return target_actor.set_variable("@x", value)
	
def changeXPosition(target_actor, parent_script, args):
	incr = args[0]
	return target_actor.increment_variable("@x", incr)
	
def xPosition(target_actor, parent_script, args):
	return target_actor.value_of_variable("@x")

	
def setYPosition(target_actor, parent_script, args):
	value = args[0]
	return target_actor.set_variable("@y", value)
	
def changeYPosition(target_actor, parent_script, args):
	incr = args[0]
	return target_actor.increment_variable("@y", incr)
	
def yPosition(target_actor, parent_script, args):
	return target_actor.value_of_variable("@y")
	

# to do -- lots!