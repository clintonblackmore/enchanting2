from collections import OrderedDict

from xml.etree.cElementTree import Element, SubElement

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
		self.stage = elem.find("stage")
		self.hidden = elem.find("hidden")
		self.headers = elem.find("headers")
		self.code = elem.find("code")
		self.blocks = elem.find("blocks")
		self.variables = elem.find("variables")
		
	def serialize(self):
		"Return an elementtree representing this object"
		
		project = Element("project", name=self.name, 
						  app=self.app, version=self.version)
		
		for child in (self.notes, self.thumbnail, self.stage, self.hidden,
		              self.headers, self.code, self.blocks, self.variables):
			project.append(child)
		return project
		