"""exec.py contains items that execute code.  To wit:

 block - a block is an executable statement
 script - a collection of blocks to execute
"""

from xml.etree.cElementTree import Element

import data
import factory
import ops

class Block(object):
	"""This is a code block, representing an instruction to execute"""
	
	def __init__(self):
		self.function = None	# used to actually call the function
		self.function_name = ""	# the original, textual name of the function
		self.arguments = []
		self.var_name = None	# only set if this is a 'var' block
								
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "block") # or elem.tag == "custom-block")
		self.function_name = elem.get("s")
		if self.function_name is None:
			# there is no function name; this must be a var block
			self.var_name = elem.get("var")
			self.function_name = "var"		
		self.function = ops.bind_to_function(self.function_name)
			
		self.arguments = [factory.deserialize_value(child) 
		                  for child in elem]
	
	def serialize(self):
		"Save out as an element tree"
		if self.var_name is None:
			# this is a standard block
			block = Element("block", s=self.function_name)
		else:
			# this is a var block
			block = Element("block", var=self.var_name)
		for arg in self.arguments:
			block.append(arg.serialize())
		return block
		
	def evaluate(self, target):
		# evaluate each of the arguments
		if self.var_name is None:
			args = [arg.evaluate(target) for arg in self.arguments]
		else:
			args = self.var_name
		
		# now, run this function
		result = self.function(target, args)		
	
		# to do -- save args and result with timestamp
		
		return result



class Script(object):
	"Represents a sequence of instructions"
	
	def __init__(self):
	
		# Only top-level scripts contain x and y values
		self.x = None
		self.y = None

		self.blocks = []
		
		self.code_pos = None
	
	def deserialize(self, elem):
		"Loads this class from an element tree representation"
		assert(elem.tag == "script")

		# attributes
		self.x = elem.get("x")
		self.y = elem.get("y")

		# our children are a sequence of blocks or custom blocks
		self.blocks = []
		for block in elem:
			b = Block()
			b.deserialize(block)
			self.blocks.append(b)

	def serialize(self):
		"Return an elementtree representing this object"
		
		# We have sprite objects and watcher nodes; make a tree of nodes
		if self.x is None or self.y is None:
			script = Element("script")
		else:
			script = Element("script", x=self.x, y=self.y)
					
		for block in self.blocks:
			script.append(block.serialize())
						
		return script	

	def step(self, target):
		"Execute a line of code; raises StopIteration when there is no more code"
		if not self.code_pos:
			self.code_pos = self.blocks.__iter__()
		current_block = self.code_pos.next()
		current_block.evaluate(target)
		
	def run(self, target):
		"Runs the code until it is done (if it ever finishes)"
		try:
			while True:
				self.step(target)
		except StopIteration:
			pass
				
		

		