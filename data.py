"""data.py contains classes that wrap or deal with data.

It includes:
  some utility functions for converting/massaging data
  Literal - which wraps numbers, strings, bools, and None
  List - which contain many Literals (or other Lists)
  Variable - contains a named piece of data
  Variables - a collection of Variable objects
"""

from xml.etree.cElementTree import Element
from collections import OrderedDict

# Utility functions

def number_from_string(s):
	"Takes a string and returns a number"
	return float(s)

def number_to_string(n):
	"Returns a number as a string, favouring integers over floats"
	if int(n) == n:
		return str(int(n))
	#return str(n)
	return repr(n)	# gives us more (in)significant digits

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

def deserialize_value(element):
	"Get an object representing this element, be it a literal, list or what-not"
	class_map = { "l" : Literal, "bool" : Literal, "list" : List }
	item = class_map[element.tag]()
	item.deserialize(element)
	return item


class Literal:
	"""Represents a single value.
	It might be a number, a boolean, a string, or so on.
	It is not a variable, and has no name."""
	
	# I am not sure yet if this should do booleans as well or not
	# A list, on the other hand, is a separate beast
	# (it'll need to keep track of changes in time differently,
	# for example).  Also note sure about functions, etc.
	
	def __init__(self, value = None):
		self.set_value(value)
		
	def set_value(self, value):
		"In order of priority, value is a boolean, number, or string"
		if isinstance(value, bool):
			self.value = value
		else:
			try:
				self.value = float(value)
			except:
				self.value = value
		
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "l" or elem.tag == "bool")
		if elem.tag == "l":
			self.set_value(elem.text)
		else: # elem.tag == "bool":
			self.set_value(elem.text == "true")
	
	def serialize(self):
		"Save out as an element tree"
		if isinstance(self.value, bool):
			literal = Element("bool")
			literal.text = self.as_string()
			return literal

		literal = Element("l")
		if self.value is not None:
			if isinstance(self.value, float):
				literal.text = number_to_string(self.value)
			else:
				literal.text = str(self.value)
		return literal
		
	def __eq__(self, other):
		return self.value == other.value
		
	def evaluate(self, target):
		"Literals are already evaluated, but the caller doesn't know that"
		return self
		
	# expose as different types
	def as_number(self):
		try:
			return float(self.value)
		except:
			return 0

	def as_string(self):
		if self.value is None:
			return ""
		if isinstance(self.value, float):
			return number_to_string(self.value)	# no trailing .0
		if isinstance(self.value, bool):
			return "true" if self.value else "false"	# all lowercase
		return str(self.value)
		
	def as_bool(self):
		return bool(self.value)
	
	# may need to add things like bool, nil, function, etc.
	


class List:
	"""Represents a list.
	
	A sample list in xml might look like:
	
	<list id="73">
		<item><l>1</l></item>
		<item><l/></item>
		<item><l>three</l></item>
	</list>"""
	
	
	def __init__(self):
		self.list = []
		self.id = -1
		
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "list")
		self.id = elem.get("id")
		for item in elem:
			self.list.append(deserialize_value(item[0]))
		
	def serialize(self):
		"Save out as an element tree"
		lst = Element("list", id=self.id)
		for entry in self.list:
			item = Element("item")
			item.append(entry.serialize())
			lst.append(item)
		return lst
			
	def as_number(self):
		return 0
			
	def as_string(self):
		return "[a list]"	# to do
		
	def as_bool(self):
		return True			# seems to be how Snap! responds
		


class Variable:
	"""Represents a value that changes over time.  
	Contains something like a Literal, Bool, or List"""
	
	def __init__(self, contents = None, name = "No name"):
		self.contents = contents
		self.name = name
		
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "variable")
		self.name = elem.get("name")

		# We should have one child
		self.contents = None
		if len(elem) > 0:
			self.contents = deserialize_value(elem[0])
			assert(self.contents is not None)
	
	def serialize(self):
		"Save out as an element tree"
		variable = Element("variable", name=self.name)
		if self.contents is not None:
			variable.append(self.contents.serialize())
		return variable
		
	def set(self, value):
		"Sets a variable.  Pass in a Literal or other object as a value"
		self.contents = value
		# to do -- record if there has been a change
				
	def value(self):
		if self.contents is not None:
			return self.contents
		return Literal(None)
			
	def show(self, visible):
		# to do -- record if a variable is to be shown or hidden
		pass
		


class Variables:
	"""This is a collection of 'Variable' objects, as used by the project, stage, and sprites"""
	
	def __init__(self):
		# ordered dict so we can serialize in the order we deserialized
		# (possibly doesn't really matter, but it helps with the unit tests)
		self.variables = OrderedDict()	
				
	def add(self, v):
		self.variables[v.name] = v
		
	def deserialize(self, elem):
		"Loads this class from an element tree representation"
		assert(elem.tag == "variables")
		
		# Read in all the variables
		self.variables.clear()
		for child_node in elem:
			v = Variable()
			v.deserialize(child_node)
			self.add(v)
		
	def serialize(self):
		"Return an elementtree representing this object"
		variables = Element("variables")
		for child in self.variables.values():
			variables.append(child.serialize())
		return variables

	def get_variable(self, name):
		if name in self.variables:
			return self.variables[name]
		return None
	
		
		

			
	
	
			
