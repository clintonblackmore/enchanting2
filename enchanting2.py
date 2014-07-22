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

	# Create our media environment
	# (now that we have dimensions for the screen)
	media_environment = media.PyGameMediaEnvironment()
	media_environment.setup_for_project(project)

	for sprite in all_actors:
		sprite.convert_art(media_environment)
	
	while True:
		media_environment.check_for_events()
		
		for sprite in all_actors:
			for script in sprite.scripts:
				try:
					script.step(sprite)
				except StopIteration:
					pass

		# note: the stage is the first sprite in the list, and erases the screen
		for sprite in all_actors:
			sprite.draw(media_environment)
		pygame.display.flip()
		media_environment.finished_frame()
	
if __name__ == "__main__":
    main(sys.argv)