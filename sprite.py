from collections import OrderedDict

import util

class Sprite:
	"Represents a Snap! Sprite"
	
	def __init__(self):
	
		# "@" attributes
		self.name = "No name"
		self.idx = -1
		self.x = 0
		self.y = 0
		self.heading = 90
		self.scale = 1
		self.rotation = 1
		self.draggable = False
		self.costume = 0
		self.color="80,80,80"
		self.pen = "tip"
		self.id = -1
		
		# children
		self.costumes = None
		self.sounds = None
		self.variables = None
		self.blocks = None
		self.scripts = None
	
	def deserialize(self, tree):
		"Loads this class from a nested dictionary representation"
		
		# attributes
		self.name = tree[u"@name"]
		self.idx  = int(tree[u"@idx"])
		self.x = float(tree[u"@x"])
		self.y = float(tree[u"@y"])
		self.heading = float(tree[u"@heading"])
		self.scale = float(tree[u"@scale"])
		self.rotation = float(tree[u"@rotation"])
		self.draggable = util.bool_from_string(tree[u"@draggable"])
		self.costume = int(tree[u"@costume"])
		self.color = tree[u"@color"]
		self.pen = tree[u"@pen"]
		self.id = int(tree[u"@id"])
		
		# children
		self.costumes = tree[u"costumes"]
		self.sounds = tree[u"sounds"]
		self.variables = tree[u"variables"]
		self.blocks = tree[u"blocks"]
		self.scripts = tree[u"scripts"]

	def serialize(self):
		"Saves this class as a nested dictionary representation"
		
		return OrderedDict([
			# attributes
			(u"@name", self.name),
			(u"@idx", util.number_to_string(self.idx)),
			(u"@x", util.number_to_string(self.x)),
			(u"@y", util.number_to_string(self.y)),
			(u"@heading", util.number_to_string(self.heading)),
			(u"@scale", util.number_to_string(self.scale)),
			(u"@rotation", util.number_to_string(self.rotation)),
			(u"@draggable", util.bool_to_string(self.draggable)),
			(u"@costume", util.number_to_string(self.costume)), 
			(u"@color", self.color),
			(u"@pen", self.pen),
			(u"@id", util.number_to_string(self.id)),
			
			# children
			(u"costumes", self.costumes),
			(u"sounds", self.sounds),
			(u"variables", self.variables),
			(u"blocks", self.blocks),
			(u"scripts", self.scripts)
		])
		