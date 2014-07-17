"""enchanting2.py

This is the main entry point of the system"""

import sys
import xml.etree.cElementTree as ElementTree
import pygame

import actor
import media

def main(argv):
	"""This is a naive, blocking, co-operatively multitasking approach"""
	
	filename = argv[1]	# xml file to open
	tree = ElementTree.parse(filename)
	project = actor.Project()
	project.deserialize(tree.getroot())
	
	# Now, we can run the code
	all_actors = [project.stage]
	all_actors.extend([sprite for sprite in project.stage.sprites
					   if isinstance(sprite, actor.BaseActor)])
	
	pygame.init()
	width = project.stage.width
	height = project.stage.height
	screen = pygame.display.set_mode((width, height))
	
	white = (255, 255, 255)
	black = (0, 0, 0)
	
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				sys.exit()
		
		for sprite in all_actors:
			for script in sprite.scripts:
				try:
					script.step(sprite)
				except StopIteration:
					pass

		screen.fill(white)
		for sprite in all_actors:
			if not isinstance(sprite, actor.Stage):		
				color = black
				pos = (int(sprite.x + width / 2), int(height / 2 - sprite.y))
				radius = 15
				pygame.draw.circle(screen, color, pos, radius) 
		pygame.display.flip()
	
if __name__ == "__main__":
    main(sys.argv)