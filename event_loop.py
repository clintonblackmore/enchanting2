"""The event loop triggers and runs all the scripts, as appropriate"""

import gevent
import gevent.pool

import data


def is_trigger_key(top_block, media_and_event):
    "True if the key code matches the key in the wait for keypress hat block"
    key_name = top_block.arguments[0].as_string()
    media_env, event = media_and_event
    return media_env.does_key_event_match(key_name, event)


def does_match_broadcast(top_block, message_string):
    message_to_start_script = top_block.arguments[0].as_string()
    if message_to_start_script == "any message":
        return True
    else:
        return message_string == message_to_start_script


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

        # (Deferred mostly to confirm that scripts wait to be triggered)
        gevent.spawn_later(1, self.trigger_green_flag)

        while True:
            media_environment.check_for_events(self)
            gevent.sleep(1.0 / 30)  # max 30 fps
            media_environment.draw(project)

    def trigger_quit_event(self):
        "Anything we need to do before quitting? Do it now!"
        print "Quitting"
        pass

    def trigger_key_press(self, media_and_event):
        "A key was pressed"
        self.trigger_scripts("receiveKey", is_trigger_key, media_and_event)

    def trigger_green_flag(self):
        "The green flag was pressed / the project is starting"
        self.trigger_scripts("receiveGo")

    def broadcast_message(self, message_string):
        "A message was broadcast"
        self.trigger_scripts("receiveMessage", does_match_broadcast, message_string)

    def trigger_scripts(self, function_name_match, callback=None, data=None):
        "Trigger all sleeping scripts that match specified conditions"

        # We can't remove items from the list in-place,
        # so we create a new list of sleeping scripts
        new_sleeping_scripts = []
        # print "sleeping scripts: %s, active scripts: %s" % \
        #	(len(self.sleeping_scripts), len(self.active_scripts))
        for script, sprite in self.sleeping_scripts:
            top_block = script.top_block()
            if top_block and top_block.function_name == function_name_match \
                    and (callback == None or callback(top_block, data) == True):
                # activate this script
                greenlet = gevent.spawn(self.run_script, script, sprite)
                self.active_scripts.add(greenlet)
            else:
                # return script to sleeping list
                new_sleeping_scripts.append((script, sprite))
        self.sleeping_scripts = new_sleeping_scripts

    def run_script(self, script, sprite):
        "Runs a script, and queues it up to run again if needs be"
        script.run(sprite)
        if script.starts_on_trigger():
            self.queue(script.from_start(), sprite)
