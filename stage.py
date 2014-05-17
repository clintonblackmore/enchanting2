from xml.etree.cElementTree import Element

from sprite import Sprite
import util

class Stage:
	"Represents a Snap! Stage"
	
	def __init__(self):
	
		# "@" attributes
		self.name = "Stage"
		self.width = 480
		self.height = 360
		self.costume = 0
		self.tempo = 60
		self.threadsafe = False
		self.lines = u"round"
		self.codify = False
		self.scheduled = True
		self.id = -1
		
		# children
		# Note: sprites have all the same children, except for pentrails and sprites
		self.pentrails = None	# unique to stage
		self.costumes = None
		self.sounds = None
		self.variables = None
		self.blocks = None
		self.scripts = None
		self.sprites = None		# unique to stage		
	
	def deserialize(self, elem):
		"Loads this class from an element tree representation"
		assert(elem.tag == "stage")

		# attributes
		self.name = elem.get("name")
		self.width = int(elem.get("width"))
		self.height = int(elem.get("height"))
		self.costume = int(elem.get("costume"))
		self.tempo = float(elem.get("tempo"))
		self.threadsafe = util.bool_from_string(elem.get("threadsafe"))
		self.lines = elem.get("lines")
		self.codify = util.bool_from_string(elem.get("codify"))
		self.scheduled = util.bool_from_string(elem.get("scheduled"))
		self.id = int(elem.get("id"))
		
		# children
		self.pentrails = elem.find("pentrails")
		self.costumes = elem.find("costumes")
		self.sounds = elem.find("sounds")
		self.variables = elem.find("variables")
		self.blocks = elem.find("blocks")
		self.scripts = elem.find("scripts")
		
		# The sprites and divided into sprite and watcher elements; 
		# keep them all in order
		sprites = elem.find("sprites")
		self.sprites = []
		for child in sprites:
			if child.tag == "sprite":
				s = Sprite()
				s.deserialize(child)
				self.sprites.append(s)
			else:
				# it is a 'watcher' node
				self.sprites.append(child)	

	def serialize(self):
		"Return an elementtree representing this object"
		
		# We have sprite objects and watcher nodes; make a tree of nodes
		sprites = Element("sprites")
		for item in self.sprites:
			if isinstance(item, Sprite):
				sprites.append( item.serialize() )
			else:
				# it is a 'watcher' node
				sprites.append( item )
		
		stage = Element("stage", 
						name = self.name,
						width = util.number_to_string(self.width),
						height = util.number_to_string(self.height),
						costume = util.number_to_string(self.costume),
						tempo = util.number_to_string(self.tempo),
						threadsafe = util.bool_to_string(self.threadsafe),
						lines = self.lines,
						codify = util.bool_to_string(self.codify),
						scheduled = util.bool_to_string(self.scheduled),
						id = util.number_to_string(self.id))
				
		for child in (self.pentrails, self.costumes, self.sounds, 
					  self.variables, self.blocks, self.scripts, sprites):
			stage.append(child)
		return stage		

	