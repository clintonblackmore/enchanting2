"""media.py.  

Here we deal with all media-relate stuff (ie. sounds and images).

All audio and graphics are to be done here, 
so that a fork of Enchanting 2 could be done without
requiring pygame."""

from xml.etree.cElementTree import Element
import base64
from cStringIO import StringIO
import pygame

import data


def load_image_from_string(s):
	"""Takes a string like data:image/png;base64,iVBORw0KGgoAAA...
	and returns an image object"""
	
	assert(s[:10] == "data:image")
	
	# Find the file extension
	ext_start = s.find("/") + 1
	ext_end = s.find(";")
	extension = s[ext_start:ext_end]
	namehint = "somefile.%s" % extension
	
	# Get the data into a file-like object
	data_start = s.find(",") + 1
	data = StringIO(base64.b64decode(s[data_start:]))

	# Read the object
	return pygame.image.load(data, namehint)
	

class Costume(object):
	"""A costume is a graphical representation of a stage or sprite.
	
	Each stage or sprite has zero or more costumes.
	
	The XML for a costume looks like this:
	
	<costume name="costume1" center-x="78" center-y="32" image="data:image/png;base64,iVBORw0KGgoAAA..." id="16"/>
	"""
	
		
	def __init__(self):

		self.name = "???"
		self.center_x = 0
		self.center_y = 0
		self.raw_image = None
		self.id = 0
	
	def deserialize(self, elem):
		"Loads this class from an element tree representation"
		assert(elem.tag == "costume")

		self.name = elem.get("name")
		self.center_x = int(elem.get("center-x"))
		self.center_y = int(elem.get("center-y"))
		self.raw_image = elem.get("image")
		self.id = int(elem.get("id"))

		self.image = load_image_from_string(self.raw_image)

	def serialize(self):
		"Return an elementtree representing this object"
		
		node = Element("costume")

		node.set("name", self.name)		
		node.set("center-x", data.number_to_string(self.center_x))
		node.set("center-y", data.number_to_string(self.center_y))
		node.set("image", self.raw_image)
		node.set("id", data.number_to_string(self.id))
	
		return node
		
class Costumes(object):
	"""A stage or sprite is depicted by drawing its current costume.
	
	Each sprite or stage has zero or more costumes.
	
		
	Here is an object with no costumes (but it is drawn as a turtle):
	
	<costumes>
		<list id="22"/>
	</costumes>
	
	Here is XML for a sprite with 3 costumes:
	
	<costumes>
		<list id="15">
			<item>
				<costume name="costume1" center-x="78" center-y="32" image="data:image/png;base64,iVBORw0KGgoAAA..." id="16"/>
			</item>
			<item>
				<costume name="costume2" center-x="163" center-y="75" image="data:image/png;base64,iVBORw0KGgoAA..." id="17"/>
			</item>
			<item>
				<costume name="costume3" center-x="188" center-y="76" image="data:image/png;base64,iVBORw0KGgoAAA..." id="18"/>
			</item>
		</list>
	</costumes>	
	"""
	
#	def __init__(self):
#		self.list_node = []
	
	def deserialize(self, elem):
		"Loads this class from an element tree representation"
		assert(elem.tag == "costumes")
		assert(len(elem) == 1)			# we should have one child -- a list node
		self.list_node = data.List()
		self.list_node.deserialize(elem[0])
		
	def serialize(self):
		"Return an elementtree representing this object"
		costumes_node = Element("costumes")
		costumes_node.append(self.list_node.serialize())
		return costumes_node

