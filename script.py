"""exec.py contains items that execute code.  To wit:

 block - a block is an executable statement
 script - a collection of blocks to execute
"""

from xml.etree.cElementTree import Element

import data
import ops

class Block:
	"""This is a code block, representing an instruction to execute"""
	
	def __init__(self):
		self.function = None	# used to actually call the function
		self.function_name = ""	# the original, textual name of the function
		self.arguments = []
								
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "block") # or elem.tag == "custom-block")
		self.function_name = elem.get("s")
		self.function = ops.bind_to_function(self.function_name)
			
		self.arguments.clear()
		for child in elem:
			self.arguments.append(data.deserialize_value(child))
	
	def serialize(self):
		"Save out as an element tree"
		block = Element("block", s=self.function_name)
		for arg in self.arguments:
			block.append(arg.serialize())
		return block
		
	def evaluate(self, target):
		# evaluate each of the arguments
		args = [arg.evaluate(target) for arg in self.arguments]
		
		# now, run this function
		result = self.function(target, args)		
	
		# to do -- save args and result with timestamp
		
		return result



class Script:
	"Represents a sequence of instructions"
	
	def __init__(self, target):
	
		self.target = target	# this is a sprite or stage that we modify
	
		self.x = 0
		self.y = 0

		self.blocks = []
		
		self.code_pos = None
	
	def deserialize(self, elem):
		"Loads this class from an element tree representation"
		assert(elem.tag == "script")

		# attributes
		self.x = int(elem.get("x"))
		self.y = int(elem.get("y"))

		# our children are a sequence of blocks or custom blocks
		for block in elem:
			b = Block()
			b.deserialize(block)
			self.blocks.append(b)

	def serialize(self):
		"Return an elementtree representing this object"
		
		# We have sprite objects and watcher nodes; make a tree of nodes
		script = Element("script", 
						 x=data.number_to_string(self.x), 
						 y=data.number_to_string(self.y))
		
		for block in self.blocks:
			script.append(block.serialize())
						
		return script	

	def step(self):
		"Execute a line of code; raises StopIteration when there is no more code"
		self.block[self.code_index].evaluate(self.target)
		
		if not self.code_pos:
			self.code_pos = self.blocks.__iter__()
		current_block = self.code_pos.next()
		current_block.evaluate()
		
	def run(self):
		"Runs the code until it is done (if it ever finishes)"
		try:
			while True:
				self.step()
		except StopIteration:
			pass
				
		

		