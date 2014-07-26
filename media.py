"""media.py.  

Here we deal with all media-relate stuff (ie. sounds and images).

All audio and graphics are to be done here, 
so that a fork of Enchanting 2 could be done without
requiring pygame."""

from xml.etree.cElementTree import Element
import base64
from cStringIO import StringIO
import pygame
import sys

import data
import actor


class PyGameMediaEnvironment(object):
	def __init__(self):
		pygame.init()
		self.width = 0
		self.height = 0
		self.screen = None
		
		# Fonts
		self.speech_font = None
		
	
	def setup_for_project(self, project):
		"We have loaded a new project.  Adjust setup if necessary"
		self.width = project.stage.width
		self.height = project.stage.height
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption(project.name)
		self.speech_font = pygame.font.Font(None, 36)

		# convert media
		all_actors = [project.stage]
		all_actors.extend([sprite for sprite in project.stage.sprites
					   if isinstance(sprite, actor.BaseActor)])
		for sprite in all_actors:
			sprite.convert_art(self)

	def draw(self, project):
		for sprite in project.sprites_in_drawing_order():
			sprite.draw(self)
		self.finished_frame()

	def finished_frame(self):
		"Called after every sequence of drawing commands"
		pygame.display.update()

	def check_for_events(self, event_loop):
		"Called between frames"
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				event_loop.trigger_quit_event() 
				sys.exit()
			if event.type == pygame.KEYDOWN:
				event_loop.trigger_key_press(event.unicode)

	def stage_pos_to_screen_pos(self, stage_pos):
		"Sprites are positioned on the stage; we need to know where to draw them on the screen"
		stage_x, stage_y = stage_pos
		
		# for a typical 480x360 stage,
		#   stage coordinates are from (-240, 180) - (239, 179)
		#   screen coordinates are (0, 0) - (479, 359)
		
		screen_x = stage_x + self.width / 2
		screen_y = self.height / 2 - stage_y 
		
		return (screen_x, screen_y)

	def stage_pos_to_nearest_screen_pos(self, stage_pos):
		"Returns integer coordinates after mapping a stage position onto a screen position"
		screen_x, screen_y = self.stage_pos_to_screen_pos(stage_pos)
		return (int(round(screen_x)), int(round(screen_y)))

	def create_speech_message(self, message, is_thought_bubble):
		"Creates a speech message and returns it in some format"
		return self.speech_font.render(message, 1, (0, 0, 0)).convert_alpha()
		
	def draw_speech_message(self, speech_message, position):
		"Shows a speech message created by 'create_speech_message'"
		self.screen.blit(speech_message, self.stage_pos_to_nearest_screen_pos(position))
		

def load_image_from_string(s):
	"""Takes a string like data:image/png;base64,iVBORw0KGgoAAA...
	and returns an image object"""

	if len(s) == 0:
		return None
	
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
		self.center_x = data.number_from_string(elem.get("center-x"))
		self.center_y = data.number_from_string(elem.get("center-y"))
		self.raw_image = elem.get("image")
		self.id = int(elem.get("id"))

		self.image = load_image_from_string(self.raw_image)
		#if self.image == None:
		#	import xml.etree.cElementTree as ElementTree
		#	print "Bad Image Node: " + ElementTree.dump(elem)

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
	
	def __init__(self):
		self.list_node = None
	
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

	def convert_art(self, media_env):
		if self.list_node:
			for costume in self.list_node.list:
				costume.image = costume.image.convert_alpha()

	def draw_stage(self, media_env, index):
		"Draws a background for the stage"
		index -= 1 	# convert 1-based index to 0-based index
		image = None

		if self.list_node and self.list_node.index_in_range(index):
			image = self.list_node.item_at_index(index).image

		if not image:
			# No image -- draw the background in white
			media_env.screen.fill((255, 255, 255))
		else:
			media_env.screen.blit(image, (0, 0))

	def draw(self, media_env, index, x_pos, y_pos, heading, scale):
		"Draws the costume"
		
		# Look up the image at this index
		index -= 1	# convert 1-based index to standard 0-based index
		# (Note that there may not be one -- in which case, we draw a 'turtle')
		image = None

		if self.list_node and self.list_node.index_in_range(index):
			image = self.list_node.item_at_index(index).image
		
		pos = media_env.stage_pos_to_nearest_screen_pos((x_pos, y_pos))

		if not image:
			# No image -- draw a turtle
			# For now, draw a circle
			color = (255, 120, 0)
			radius = 15
			pygame.draw.circle(media_env.screen, color, pos, radius) 
		else:
			rect = image.get_rect()
			rect.center = pos
			media_env.screen.blit(image, rect)
			
