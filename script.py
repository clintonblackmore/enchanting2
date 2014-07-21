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
		
	def evaluate(self, target, script):
		# evaluate each of the arguments
		if self.var_name is None:
			args = []
			args = [arg.evaluate(target, script) for arg in self.arguments 
					if not isinstance(arg, (data.Comment))]
					#if not isinstance(arg, (data.Comment, Script))]
		else:
			args = self.var_name
		
		# now, run this function
		if self.function is not None:
			result = self.function(target, script, args)		
		else:
			print "Unknown function: %s" % self.function_name
			result = data.Literal(None)
	
		# to do -- save args and result with timestamp
		
		return result

	def __repr__(self):
		# Shows state; can't reconstruct from this info
		return "%s(%r)" % (self.__class__, self.__dict__)

	def __str__(self):
		return "%s(%s)" % (self.function_name, ", ".join([str(s) for s in self.arguments])) 

class Script(object):
	"Represents a sequence of instructions"
	
	def __init__(self):
	
		# Only top-level scripts contain x and y values
		self.x = None
		self.y = None
		self.blocks = []
		self.from_start()
		
	def from_start(self):
		"Sets or re-sets the script to begin and the start"
		self.code_pos = 0
		self.subscript = None	# set by flow control blocks
		self.repeat = 0			# adjusted by flow control blocks
		return self
	
	def deserialize(self, elem):
		"Loads this class from an element tree representation"
		assert(elem.tag == "script")

		# attributes
		self.x = elem.get("x")
		self.y = elem.get("y")

		self.from_start()

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

		# Are we inside a nested script?
		if self.subscript:
			# step the script until it is done
			try:
#				print "(sub) ",
				self.subscript.step(target)
			except StopIteration:
#				print "(exit)"
				self.subscript = None
		else:
			if self.code_pos < len(self.blocks):
				current_block = self.blocks[self.code_pos]
			else:
				raise StopIteration
		
#			print current_block,
			current_block.evaluate(target, self)
#			print "(repeat %s)" % self.repeat
			if not self.repeat:
				self.code_pos += 1

	def evaluate(self, target, script):
		"Scripts (in arguments) evaluate to themselves.  [They can be run separately]"
		return self

	def run(self, target):
		"Runs the code until it is done (if it ever finishes)"
		try:
			while True:
				self.step(target)
		except StopIteration:
			pass
				
	def __str__(self):
		return "Script <%s>" % ", ".join([str(s) for s in self.blocks])

		