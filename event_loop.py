"""The event loop triggers and runs all the scripts, as appropriate"""

import gevent
import gevent.pool

class EventLoop(object):

	def __init__(self):
		self.active_scripts = gevent.pool.Group()
		self.sleeping_scripts = []

	def queue(self, script, sprite):
		"Queues up a script"
		# Scripts usually start with a hat block and do nothing until it is activated
		self.sleeping_scripts.append((script, sprite))

	def run(self, project, media_environment):
		"Runs all the scripts in the project"
		
		# This is the main loop
		# It checks for events (from pygame)
		# and it updates the screen every so often
		
		gevent.spawn_later(1, self.trigger_green_flag)
		
		while True:
			media_environment.check_for_events(self)
			gevent.sleep(1.0/30)	# max 30 fps
			media_environment.draw(project)

	def trigger_quit_event(self):
		"Anything we need to do before quitting? Do it now!"
		print "QUIT EVENT"
		pass
		
	def trigger_key_press(self, unicode):
		"A key was pressed"
		print "Key press: %s", unicode

	def trigger_green_flag(self):
		"The green flag was pressed / the project is starting"
		print "Green flag pressed"
		self.trigger_scripts("receiveGo")
	
	def trigger_scripts(self, function_name_match, callback = None):
		"Trigger all sleeping scripts that match specified conditions"
		
		# We can't remove items from the list in-place, 
		# so we create a new list of sleeping scripts
		new_sleeping_scripts = []
		for script, sprite in self.sleeping_scripts:
			top_block = script.top_block()
			if top_block and top_block.function_name == function_name_match:
				if callback == None or callback(script) == True:
					gevent.spawn(self.run_script, script, sprite)
				else:
					# return to sleeping list
					new_sleeping_scripts.append((script, sprite))
		self.sleeping_scripts = new_sleeping_scripts				

	def run_script(self, script, sprite):
		"Runs a script, and queues it up to run again if needs be"
		script.run(sprite)
		if script.starts_on_trigger():
			self.queue(script, sprite)
