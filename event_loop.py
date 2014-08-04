"""The event loop triggers and runs all the scripts, as appropriate"""

import gevent
import gevent.pool

try:
    from gevent.lock import BoundedSemaphore
except:
    from gevent.coros import BoundedSemaphore


import factory
import server

port = 8080


def is_trigger_key(top_block, media_and_event):
    """True if user pressed key hat block is waiting for."""
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

    def __init__(self, media_environment):
        self.active_scripts = gevent.pool.Group()
        self.sleeping_scripts = []
        self.project = None
        self.media_environment = media_environment
        # Get the script_lock before adding or removing scripts
        self.script_lock = BoundedSemaphore(1)
        self.clients = []

    def queue(self, script, sprite):
        """Queues up a script"""
        # Scripts usually start with a hat block and do nothing until it is
        # activated
        with self.script_lock:
            self.sleeping_scripts.append((script, sprite))

    def run_forever(self):
        """Runs all the scripts in the project"""

        # First, fire up the webserver
        server.ClientConnection.event_loop = self
        gevent.spawn(server.run_web_servers, port)

        # This is the main loop
        # It checks for events (from pygame)
        # and it updates the screen every so often

        while True:
            self.media_environment.check_for_events(self)
            gevent.sleep(1.0 / 30)  # max 30 fps
            self.media_environment.draw(self.project)

    def trigger_quit_event(self):
        """Anything we need to do before quitting? Do it now!"""
        print "Quitting"
        pass

    def trigger_key_press(self, media_and_event):
        """A key was pressed"""
        self.trigger_scripts("receiveKey", is_trigger_key, media_and_event)

    def trigger_green_flag(self):
        """The green flag was pressed / the project is starting"""
        self.stop_all_scripts()
        self.trigger_scripts("receiveGo")

    def stop_all_scripts(self):
        """The stop button was pressed -- halt execution of all scripts"""
        if self.project:
            self.project.stop_all_scripts()

    def broadcast_message(self, message_string):
        """A message was broadcast"""
        self.trigger_scripts(
            "receiveMessage", does_match_broadcast, message_string)

    def trigger_scripts(self, function_name_match, callback=None, data=None):
        """Trigger all sleeping scripts that match specified conditions"""

        with self.script_lock:
            # We can't remove items from the list in-place,
            # so we create a new list of sleeping scripts
            new_sleeping_scripts = []
            # print "sleeping scripts: %s, active scripts: %s" % \
            #    (len(self.sleeping_scripts), len(self.active_scripts))
            for script, sprite in self.sleeping_scripts:
                top_block = script.top_block()
                if top_block and top_block.function_name == function_name_match \
                        and (callback is None or callback(top_block, data)):
                    # activate this script
                    greenlet = gevent.spawn(self.run_script, script, sprite)
                    self.active_scripts.add(greenlet)
                else:
                    # return script to sleeping list
                    new_sleeping_scripts.append((script, sprite))
            self.sleeping_scripts = new_sleeping_scripts

    def run_script(self, script, sprite):
        """Runs a script, and queues it up to run again if needs be"""
        script.run(sprite)
        if script.starts_on_trigger():
            self.queue(script.from_start(), sprite)

    def purge_all_scripts(self):
        """Reset everything -- purge all running and queued scripts"""
        self.stop_all_scripts()
        with self.script_lock:
            self.active_scripts.kill()
            self.sleeping_scripts = []

    def load_project_from_disk(self, filename):
        """Loads a project from a file, and starts executing it"""
        self.purge_all_scripts()
        self.project = factory.deserialize_file(filename, self)
        self.media_environment.setup_for_project(self.project)
        # gevent.spawn(self.trigger_green_flag)

    def load_project_from_xml(self, xml):
        """Loads a file from xml"""
        self.purge_all_scripts()
        self.project = factory.deserialize_xml(xml, self)
        self.media_environment.setup_for_project(self.project)
        # gevent.spawn(self.trigger_green_flag)

    def client_connected(self, client):
        self.clients.append(client)
        print "Now serving %s clients; %s just connected" \
              % (len(self.clients), client)
        # Send the client a copy of the current world (if there is one)
        if self.project:
            message = "load_project %s" % factory.xml_for_object(self.project)
            client.ws.send(message)

    def client_disconnected(self, client):
        self.clients.remove(client)
        print "Now serving %s clients; %s just disconnected" \
              % (len(self.clients), client)

    def message_from_client(self, message, client):
        split = message.find(" ")
        if split == -1:
            print "Unrecognized message: %s" % message
        command = message[:split]

        if command == "load_project":
            xml = message[split + 1:]
            self.load_project_from_xml(xml)
            self.send_message_to_other_clients(message, client)
        elif command == "green_flag_press":
            self.trigger_green_flag()
        elif command == "stop_sign_press":
            self.stop_all_scripts()
        else:
            print "Unrecognized command: %s" % command

    def send_message_to_other_clients(self, message, source_client=None):
        """Send a message to all web clients, except the source"""
        for client in self.clients:
            if client != source_client:
                client.ws.send(message)
