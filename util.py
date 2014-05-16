# Utility functions

def number_from_string(s):
	"Takes a string and returns a number"
	return float(s)

def number_to_string(n):
	"Returns a number as a string, favouring integers over floats"
	if int(n) == n:
		return str(int(n))
	return str(n)

def bool_from_string(s):
	"Takes an xml string and returns a bool"
	if s == "true":
		return True
	if s == "false":
		return False
	raise ValueError("Boolean value from xml must be 'true' or 'false'")
	
def bool_to_string(b):
	"Takes a python boolean and returns a string for xml"
	if b:
		return "true"
	return "false"


