from xml.etree.cElementTree import Element

from stage import Stage
from variables import Variables

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
		self.stage = Stage(self)
		self.hidden = None
		self.headers = None
		self.code = None
		self.blocks = None
		self.variables = Variables()
	
	def deserialize(self, elem):
		"Loads this class from an element tree representation"
		
		assert(elem.tag == "project")
		
		# attributes
		self.name = elem.get("name")
		self.app = elem.get("app")
		self.version = elem.get("version")
		
		# children
		self.notes = elem.find("notes")
		self.thumbnail = elem.find("thumbnail")
		self.stage.deserialize(elem.find("stage"))
		self.hidden = elem.find("hidden")
		self.headers = elem.find("headers")
		self.code = elem.find("code")
		self.blocks = elem.find("blocks")
		self.variables.deserialize(elem.find("variables"))
		
	def serialize(self):
		"Return an elementtree representing this object"
		
		project = Element("project", name=self.name, 
						  app=self.app, version=self.version)
		
		for child in (self.notes, self.thumbnail, self.stage.serialize(), 
					  self.hidden, self.headers, self.code, self.blocks, 
		              self.variables.serialize()):
			project.append(child)
		return project
		
	def get_variable(self, name):
		"Gets a named variable; returns None if it does not exist"
		return self.variables.get_variable(name)
