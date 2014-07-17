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

	"Create our media environment"	
	media_environment = media.PyGameMediaEnvironment()
	media_environment.setup_for_project(project)
	
	
#	pygame.init()
#	width = project.stage.width
#	height = project.stage.height
#	screen = pygame.display.set_mode((width, height))
	
#	white = (255, 255, 255)
#	black = (0, 0, 0)
	
	while True:

		media_environment.check_for_events()
		
		for sprite in all_actors:
			for script in sprite.scripts:
				try:
					script.step(sprite)
				except StopIteration:
					pass

#		screen.fill(white)

		# note: we assume stage is first sprite in list
		for sprite in all_actors:
			sprite.draw(media_environment)
		pygame.display.flip()
		media_environment.finished_frame()
	
if __name__ == "__main__":
    main(sys.argv)