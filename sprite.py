from xml.etree.cElementTree import Element

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
		self.nest = None	# optional attribute
		self.costumes = None
		self.sounds = None
		self.variables = None
		self.blocks = None
		self.scripts = None
	
	def deserialize(self, elem):
		"Loads this class from an element tree representation"
		
		assert(elem.tag == "sprite")
			
		# attributes
		self.name = elem.get("name")
		self.idx  = int(elem.get("idx"))
		self.x = float(elem.get("x"))
		self.y = float(elem.get("y"))
		self.heading = float(elem.get("heading"))
		self.scale = float(elem.get("scale"))
		self.rotation = float(elem.get("rotation"))
		self.draggable = util.bool_from_string(elem.get("draggable"))
		self.costume = int(elem.get("costume"))
		self.color = elem.get("color")
		self.pen = elem.get("pen")
		self.id = int(elem.get("id"))
		
		# children
		self.nest = elem.find("nest")
		self.costumes = elem.find("costumes")
		self.sounds = elem.find("sounds")
		self.variables = elem.find("variables")
		self.blocks = elem.find("blocks")
		self.scripts = elem.find("scripts")

	def serialize(self):
		"Return an elementtree representing this object"
		
		script = Element("sprite", 
						name = self.name, 
					  	idx = util.number_to_string(self.idx),
						x = util.number_to_string(self.x),
						y = util.number_to_string(self.y),
						heading = util.number_to_string(self.heading),
						scale = util.number_to_string(self.scale),
						rotation = util.number_to_string(self.rotation),
						draggable = util.bool_to_string(self.draggable),
						costume = util.number_to_string(self.costume),
						color = self.color,
						pen = self.pen,
						id = util.number_to_string(self.id))
		
		for child in (self.nest, self.costumes, self.sounds, self.variables, 
					  self.blocks, self.scripts):
			if child is not None:
				script.append(child)
		return script		
