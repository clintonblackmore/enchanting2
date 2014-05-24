"""enchanting2.py

This is the main entry point of the system"""

import sys
import xml.etree.cElementTree as ElementTree

import actor

def main(argv):
	"""This is a naive, blocking, co-operatively multitasking approach"""
	
	filename = argv[1]	# xml file to open
	tree = ElementTree.parse(filename)
	project = actor.Project()
	project.deserialize(tree.getroot())
	
	# Now, we can run the code
	all_actors = [project.stage]
	all_actors.extend([sprite for sprite in project.stage.sprites])
	
	while True:
		for sprite in all_actors:
			# Check that it is really a sprite, and not a 'Watcher'
			# (Ugly!)
			if isinstance(sprite, actor.BaseActor):
				print sprite.name
				for script in sprite.scripts:
					try:
						script.step(sprite)
					except StopIteration:
						pass
						


if __name__ == "__main__":
    main(sys.argv)