
from collections import OrderedDict

class Project:
	"Represents a Snap! Project"
	
	def __init__(self):
	
		# "@" attributes
		self.name = "No name"
		self.app = "Snap! 4.0, http://snap.berkeley.edu"
		self.version = 1
		
		# children
		self.notes = None
		self.thumbnail = None
		self.stage = None
		self.hidden = None
		self.headers = None
		self.code = None
		self.blocks = None
		self.variables = None	
	
	def deserialize(self, tree):
		"Loads this class from a nested dictionary representation"
		proj = tree["project"]
		
		self.name = proj[u"@name"]
		self.app = proj[u"@app"]
		self.version = proj[u"@version"]
		
		self.notes = proj[u"notes"]
		self.thumbnail = proj[u"thumbnail"]
		self.stage = proj[u"stage"]
		self.hidden = proj[u"hidden"]
		self.headers = proj[u"headers"]
		self.code = proj[u"code"]
		self.blocks = proj[u"blocks"]
		self.variables = proj[u"variables"]
		
	def serialize(self):
		"Saves this class as a nested dictionary representation"
		proj = OrderedDict([
			(u"@name", self.name),
			(u"@app", self.app),
			(u"@version", self.version),
			
			(u"notes", self.notes),
			(u"thumbnail", self.thumbnail),
			(u"stage", self.stage),
			(u"hidden", self.hidden),
			(u"headers", self.headers),
			(u"code", self.code),
			(u"blocks", self.blocks),
			(u"variables", self.variables)
		])
		
		return OrderedDict([(u"project", proj)])
		