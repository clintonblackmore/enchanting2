"""actor.py contains things that do things, specifically:

  (BaseActor - not as yet implemented base class for Stage and Sprite)
  Sprite - an entity that moves around on the screen and runs scripts
  Stage - the screen background, which also runs scripts
  Project - the overarching project containing the Stage and everything.
"""


from xml.etree.cElementTree import Element

import data

class Sprite:
	"Represents a Snap! Sprite"
	
	def __init__(self, project):
	
		self.project = project
	
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
		self.nest = None	# optional child
		self.costumes = None
		self.sounds = None
		self.variables = data.Variables()
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
		self.draggable = data.bool_from_string(elem.get("draggable"))
		self.costume = int(elem.get("costume"))
		self.color = elem.get("color")
		self.pen = elem.get("pen")
		self.id = int(elem.get("id"))
		
		# children
		self.nest = elem.find("nest")
		self.costumes = elem.find("costumes")
		self.sounds = elem.find("sounds")
		self.variables.deserialize(elem.find("variables"))
		self.blocks = elem.find("blocks")
		self.scripts = elem.find("scripts")

	def serialize(self):
		"Return an elementtree representing this object"
		
		variables_node = self.variables.serialize()
		
		script = Element("sprite", 
						name = self.name, 
					  	idx = data.number_to_string(self.idx),
						x = data.number_to_string(self.x),
						y = data.number_to_string(self.y),
						heading = data.number_to_string(self.heading),
						scale = data.number_to_string(self.scale),
						rotation = data.number_to_string(self.rotation),
						draggable = data.bool_to_string(self.draggable),
						costume = data.number_to_string(self.costume),
						color = self.color,
						pen = self.pen,
						id = data.number_to_string(self.id))
		
		for child in (self.nest, self.costumes, self.sounds, 
					  variables_node, self.blocks, self.scripts):
			if child is not None:
				script.append(child)
		return script		

	def get_variable(self, name):
		"Gets a variable by name; returns None if it does not exist"
		v = self.variables.get_variable(name)
		if v:
			return v
		if self.project:
			return self.project.get_variable(name)
		return None



class Stage:
	"Represents a Snap! Stage"
	
	def __init__(self, project):
	
		self.project = project
	
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
		self.variables = data.Variables()
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
		self.threadsafe = data.bool_from_string(elem.get("threadsafe"))
		self.lines = elem.get("lines")
		self.codify = data.bool_from_string(elem.get("codify"))
		self.scheduled = data.bool_from_string(elem.get("scheduled"))
		self.id = int(elem.get("id"))
		
		# children
		self.pentrails = elem.find("pentrails")
		self.costumes = elem.find("costumes")
		self.sounds = elem.find("sounds")
		self.variables.deserialize(elem.find("variables"))
		self.blocks = elem.find("blocks")
		self.scripts = elem.find("scripts")
				
		# The sprites and divided into sprite and watcher elements; 
		# keep them all in order
		sprites = elem.find("sprites")
		self.sprites = []
		for child in sprites:
			if child.tag == "sprite":
				s = Sprite(self.project)
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
				sprites.append(item.serialize())
			else:
				# it is a 'watcher' node
				sprites.append(item)
		
		variables_node = self.variables.serialize()
		
		stage = Element("stage", 
						name = self.name,
						width = data.number_to_string(self.width),
						height = data.number_to_string(self.height),
						costume = data.number_to_string(self.costume),
						tempo = data.number_to_string(self.tempo),
						threadsafe = data.bool_to_string(self.threadsafe),
						lines = self.lines,
						codify = data.bool_to_string(self.codify),
						scheduled = data.bool_to_string(self.scheduled),
						id = data.number_to_string(self.id))
				
		for child in (self.pentrails, self.costumes, self.sounds, 
					  variables_node, self.blocks, self.scripts, sprites):
			stage.append(child)
		return stage		

	def get_variable(self, name):
		"Gets a variable by name; returns None if it does not exist"
		v = self.variables.get_variable(name)
		if v:
			return v
		if self.project:
			return self.project.get_variable(name)
		return None




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
		self.variables = data.Variables()
	
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
