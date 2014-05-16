from collections import OrderedDict

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
	
	def deserialize(self, tree):
		"Loads this class from a nested dictionary representation"
		
		# attributes
		self.name = tree[u"@name"]
		self.width = int(tree[u"@width"])
		self.height = int(tree[u"@height"])
		self.costume = int(tree[u"@costume"])
		self.tempo = float(tree[u"@tempo"])
		self.threadsafe = util.bool_from_string(tree[u"@threadsafe"])
		self.lines = tree[u"@lines"]
		self.codify = util.bool_from_string(tree[u"@codify"])
		self.scheduled = util.bool_from_string(tree[u"@scheduled"])
		self.id = int(tree[u"@id"])
		
		# children
		self.pentrails = tree[u"pentrails"]
		self.costumes = tree[u"costumes"]
		self.sounds = tree[u"sounds"]
		self.variables = tree[u"variables"]
		self.blocks = tree[u"blocks"]
		self.scripts = tree[u"scripts"]
		self.sprites = tree[u"sprites"]

	def serialize(self):
		"Saves this class as a nested dictionary representation"
		
		return OrderedDict([
			# attributes
			(u"@name", self.name),
			(u"@width", util.number_to_string(self.width)),
			(u"@height", util.number_to_string(self.height)),
			(u"@costume", util.number_to_string(self.costume)),
			(u"@tempo", util.number_to_string(self.tempo)),
			(u"@threadsafe", util.bool_to_string(self.threadsafe)),
			(u"@lines", self.lines),
			(u"@codify", util.bool_to_string(self.codify)),
			(u"@scheduled", util.bool_to_string(self.scheduled)),
			(u"@id", util.number_to_string(self.id)),
		
			# children
			(u"pentrails", self.pentrails),
			(u"costumes", self.costumes),
			(u"sounds", self.sounds),
			(u"variables", self.variables),
			(u"blocks", self.blocks),
			(u"scripts", self.scripts),
			(u"sprites", self.sprites)
		])

		