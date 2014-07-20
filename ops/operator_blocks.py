import math
import random

import data

"""These are the green 'operations' blocks, many of which do math"""

# to do
# reifyScript, reifyReporter, reifyPredicate

def reportSum(target_actor, parent_script, args):
	return data.Literal(args[0].as_number() + args[1].as_number())
	
def reportDifference(target_actor, parent_script, args):
	return data.Literal(args[0].as_number() - args[1].as_number())

def reportProduct(target_actor, parent_script, args):
	return data.Literal(args[0].as_number() * args[1].as_number())

def reportQuotient(target_actor, parent_script, args):
	a, b = (args[0].as_number(), args[1].as_number())
	return data.Literal(a / b)
	# system will need to know if a div by zero error occurs

def reportModulus(target_actor, parent_script, args):
	return data.Literal(args[0].as_number() % args[1].as_number())

def reportRound(target_actor, parent_script, args):
	return data.Literal(math.round(args[0].as_number()))

#def reportMonadic(target_actor, parent_script, args):
#	"This one does all the functions, like sqrt, etc"
#	raise NotImplementedError
#	return None
	
def reportRandom(target_actor, parent_script, args):	
	min, max = (args[0].as_number(), args[1].as_number())
	return data.Literal(random.randrange(min, max))
	
# to do:
# reportLessThan, reportEquals, reportGreaterThan, reportAnd, reportOr, reportNot

def reportTrue(target_actor, parent_script, args):
	return data.Literal(True)
	
def reportFalse(target_actor, parent_script, args):
	return data.Literal(False)

# many more to do here



	
