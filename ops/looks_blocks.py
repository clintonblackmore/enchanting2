#import data

"""These are the purple 'looks' blocks"""

def bubble(target_actor, parent_script, args):
	message = args[0].as_string()
	target_actor.say_or_think(message, False)
	return None		# command-blocks always return None
					# reporter blocks always return a value 
					# (usually a 'Literal' object)

def doThink(target_actor, parent_script, args):
	message = args[0].as_string()
	target_actor.say_or_think(message, True)
	return None	

# to do -- lots!