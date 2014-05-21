from core import Literal

"""These block functions perform math operations"""

def add(target, args):
	return Literal(args[0].as_number() + args[1].as_number())
	

	
