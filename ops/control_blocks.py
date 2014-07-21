import math
import random

import data

"""These are the yellow 'control' blocks"""

def receiveGo(target_actor, parent_script, args):
	return None

def doRepeat(target_actor, parent_script, args):
	# We are in a loop
	initial_count, script = args
	
	# Did we just start for the first time?
	if not parent_script.repeat:
		# Yes, this is the first time
		parent_script.repeat = initial_count.evaluate(target_actor, parent_script).as_number()
	else:
		parent_script.repeat -= 1
	
	if parent_script.repeat >= 1:
		parent_script.subscript = script.from_start()
	else:
		parent_script.repeat = 0
	return data.Literal(parent_script.repeat)
	
def forever(target, args):
	return None

# to do -- lots!