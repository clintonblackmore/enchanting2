"""enchanting2.py

This is the main entry point of the system"""

import sys
import xml.etree.cElementTree as ElementTree

import actor
import media
import event_loop

def main(argv):
	"""Load the project and start it running"""
	
	loop = event_loop.EventLoop()
	
	filename = argv[1]	# xml file to open
	tree = ElementTree.parse(filename)
	project = actor.Project(loop)
	project.deserialize(tree.getroot())
	
	# Create our media environment
	# (now that we have dimensions for the screen)
	media_environment = media.PyGameMediaEnvironment()
	media_environment.setup_for_project(project)

	loop.run(project, media_environment)
	
if __name__ == "__main__":
    main(sys.argv)