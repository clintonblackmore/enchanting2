"""actor.py contains things that do things, specifically:

  BaseActor - base class for Stage and Sprite
  Sprite - an entity that moves around on the screen and runs scripts
  Stage - the screen background, which also runs scripts
  Project - the overarching project containing the Stage and everything.
"""

from xml.etree.cElementTree import Element
import math

import data
import script
import media
import factory


# Helper functions

def get_blocks(elem):
    """Returns the list of block definitions, if it is defined."""
    blocks_node = elem.find("blocks")
    if blocks_node is not None:
        return factory.deserialize_value(blocks_node)
    return None

def get_blocks_node(blocks):
    """Returns the node that represents the blocks, or none"""
    if blocks is None:
        return None
    return blocks.serialize()


class BaseActor(object):

    """Common things between Sprite and Stage"""

    def __init__(self, project):

        self.project = project

        self.costumes = None
        self.sounds = None
        self.variables = data.Variables()
        self.blocks = None
        self.scripts = []

    def deserialize(self, elem):
        """Loads this class from an element tree representation"""
        assert (elem.tag in ("stage", "sprite"))

        # children
        costumes_node = elem.find("costumes")
        if costumes_node:
            self.costumes = media.Costumes()
            self.costumes.deserialize(costumes_node)
        else:
            self.costumes = None

        self.sounds = elem.find("sounds")
        self.variables.deserialize(elem.find("variables"))
        self.blocks = get_blocks(elem)
        self.scripts = []

        event_loop = None
        if self.project:
            event_loop = self.project.event_loop

        for item in elem.find("scripts"):
            new_script = script.Script()
            new_script.deserialize(item)
            self.scripts.append(new_script)
            if event_loop:
                event_loop.queue(new_script, self)

    def serialize_scripts(self):
        """Returns a script node for use in serialization"""
        scripts_node = Element("scripts")
        for item in self.scripts:
            scripts_node.append(item.serialize())
        return scripts_node

    def __str__(self):
        return "%s %s" % (self.__class__.__name__, self.variables)

    def get_variable(self, name):
        """Gets a variable by name; returns None if it does not exist"""
        v = self.variables.get_variable(name)
        if v:
            return v
        if self.project:
            return self.project.get_variable(name)
        return None

    def value_of_variable(self, name):
        v = self.get_variable(name)
        if v:
            result = v.value()
            if result:
                return result
        return data.Literal(None)

    def set_variable(self, name, value):
        v = self.get_variable(name)
        if v:
            v.set(value)
        return None

    def increment_variable(self, name, increment):
        v = self.get_variable(name)
        if v:
            v.set(data.Literal(v.value().as_number() + increment))
        return None

    def show_variable(self, name, visible):
        v = target.get_variable(name)
        if v:
            v.show(True)
        return None

    def convert_art(self, media_env):
        if self.costumes:
            self.costumes.convert_art(media_env)

    def set_costume(self, literal):
        if self.costumes:
            self.costume = self.costumes.index_for_costume(literal)

    def next_costume(self):
        if self.costumes:
            self.costume = self.costumes.index_for_next_costume(self.costume)

    def stop_all_scripts(self):
        for script in self.scripts:
            script.stop()


class Sprite(BaseActor):

    """Represents a Snap! Sprite"""

    def __init__(self, project):
        super(Sprite, self).__init__(project=project)

        # "@" attributes
        self.name = "No name"
        self.idx = -1

        self.variables.add(data.Variable("@x", data.Literal(0)))
        self.variables.add(data.Variable("@y", data.Literal(0)))
        self.variables.add(data.Variable("@heading", data.Literal(90)))
        self.variables.add(data.Variable("@scale", data.Literal(1)))

        self.rotation = 1
        self.draggable = False
        self.costume = 0
        self.color = "80,80,80"
        self.pen = "tip"
        self.id = -1

        # children specific to sprite
        self.nest = None  # optional child

        # Not serialized
        self.speech_message = ""
        self.speech_is_thought = False  # False == though, True == speech
        self.speech_image = None
        self.create_new_speech_message = False

    def deserialize(self, elem):
        """Loads this class from an element tree representation"""

        assert (elem.tag == "sprite")

        super(Sprite, self).deserialize(elem)

        # attributes
        self.name = elem.get("name")
        self.idx = int(elem.get("idx"))

        self.set_variable("@x", data.Literal(float(elem.get("x"))))
        self.set_variable("@y", data.Literal(float(elem.get("y"))))
        self.set_variable("@heading", data.Literal(float(elem.get("heading"))))
        self.set_variable("@scale", data.Literal(float(elem.get("scale"))))

        self.rotation = float(elem.get("rotation"))
        self.draggable = data.bool_from_string(elem.get("draggable"))
        self.costume = int(elem.get("costume"))
        self.color = elem.get("color")
        self.pen = elem.get("pen")
        self.id = int(elem.get("id"))

        # unique children
        self.nest = elem.find("nest")

    def serialize(self):
        """Return an elementtree representing this object"""

        variables_node = self.variables.serialize()
        scripts_node = self.serialize_scripts()
        blocks_node = get_blocks_node(self.blocks)

        if self.costumes:
            costumes_node = self.costumes.serialize()
        else:
            costumes_node = None

        x = self.value_of_variable("@x").as_string()

        sprite = Element("sprite",
                         name=self.name,
                         idx=data.number_to_string(self.idx),
                         x=data.number_to_string(
                             self.value_of_variable("@x").as_number()),
                         y=self.value_of_variable("@y").as_string(),
                         heading=data.number_to_string(
                             self.value_of_variable("@heading").as_number()),
                         scale=self.value_of_variable("@scale").as_string(),
                         rotation=data.number_to_string(self.rotation),
                         draggable=data.bool_to_string(self.draggable),
                         costume=data.number_to_string(self.costume),
                         color=self.color,
                         pen=self.pen,
                         id=data.number_to_string(self.id))

        for child in (self.nest, costumes_node, self.sounds,
                      variables_node, blocks_node, scripts_node):
            if child is not None:
                sprite.append(child)
        return sprite

    def __str__(self):
        return "%s %r %s" % (
            self.__class__.__name__, self.name, self.variables)

    def say_or_think(self, message, is_thought):
        if message != self.speech_message or \
                is_thought != self.speech_is_thought:
            self.speech_message = message
            self.speech_is_thought = is_thought
            if len(self.speech_message) > 0:
                self.create_new_speech_message = True

    def draw(self, media_environment):
        x = self.value_of_variable("@x").as_number()
        y = self.value_of_variable("@y").as_number()
        if self.costumes:
            self.costumes.draw(media_environment,
                               self.costume, x, y,
                               self.value_of_variable("@heading").as_number(),
                               self.value_of_variable("@scale").as_number())
        if len(self.speech_message) > 0:
            if self.create_new_speech_message:
                self.speech_image = \
                    media_environment.create_speech_message(
                        self.speech_message, self.speech_is_thought)
                self.create_new_speech_message = False
            media_environment.draw_speech_message(
                self.speech_image, (x + 30, y + 30))

    def radians_from_heading(self):
        """Returns an angle representing the heading, in the range (0, 360)"""
        angle = (self.value_of_variable("@heading").as_number() - 90.0) % 360.0
        return math.radians(angle)

    def move_forward(self, distance):
        radians = self.radians_from_heading()
        dX = math.cos(radians) * distance
        dY = -math.sin(radians) * distance
        self.increment_variable("@x", dX)
        self.increment_variable("@y", dY)


class Stage(BaseActor):

    """Represents a Snap! Stage"""

    def __init__(self, project):

        super(Stage, self).__init__(project=project)

        # "@" attributes
        self.name = "Stage"
        self.width = 480
        self.height = 360
        self.costume = 0
        self.tempo = 60
        self.threadsafe = False
        self.lines = u"round"
        self.codify = False
        self.scheduled = True
        self.id = -1

        # unique children
        self.pentrails = None  # unique to stage
        self.sprites = []  # unique to stage

    def deserialize(self, elem):
        """Loads this class from an element tree representation"""
        assert (elem.tag == "stage")

        super(Stage, self).deserialize(elem)

        # attributes
        self.name = elem.get("name")
        self.width = int(elem.get("width"))
        self.height = int(elem.get("height"))
        self.costume = int(elem.get("costume"))
        self.tempo = float(elem.get("tempo"))
        self.threadsafe = data.bool_from_string(elem.get("threadsafe"))
        self.lines = elem.get("lines")
        self.codify = data.bool_from_string(elem.get("codify"))
        self.scheduled = data.bool_from_string(elem.get("scheduled"))
        self.id = int(elem.get("id"))

        # unique children
        self.pentrails = elem.find("pentrails")

        # The sprites and divided into sprite and watcher elements;
        # keep them all in order
        sprites = elem.find("sprites")
        self.sprites = []
        for child in sprites:
            if child.tag == "sprite":
                s = Sprite(self.project)
                s.deserialize(child)
                self.sprites.append(s)
            else:
                # it is a 'watcher' node
                self.sprites.append(child)

    def serialize(self):
        """Return an elementtree representing this object"""

        # We have sprite objects and watcher nodes; make a tree of nodes
        sprites = Element("sprites")
        for item in self.sprites:
            if isinstance(item, Sprite):
                sprites.append(item.serialize())
            else:
                # it is a 'watcher' node
                sprites.append(item)

        variables_node = self.variables.serialize()
        scripts_node = self.serialize_scripts()
        blocks_node = get_blocks_node(self.blocks)


        if self.costumes:
            costumes_node = self.costumes.serialize()
        else:
            costumes_node = None

        stage = Element("stage",
                        name=self.name,
                        width=data.number_to_string(self.width),
                        height=data.number_to_string(self.height),
                        costume=data.number_to_string(self.costume),
                        tempo=data.number_to_string(self.tempo),
                        threadsafe=data.bool_to_string(self.threadsafe),
                        lines=self.lines,
                        codify=data.bool_to_string(self.codify),
                        scheduled=data.bool_to_string(self.scheduled),
                        id=data.number_to_string(self.id))

        for child in (self.pentrails, costumes_node, self.sounds,
                      variables_node, blocks_node, scripts_node, sprites):
            if child is not None:
                stage.append(child)
        return stage

    def draw(self, media_environment):
        if self.costumes:
            self.costumes.draw_stage(media_environment, self.costume)


class Project:

    """Represents a Snap! Project"""

    def __init__(self, event_loop):
        self.event_loop = event_loop

        # "@" attributes
        self.name = "No name"
        self.app = "Snap! 4.0, http://snap.berkeley.edu"
        self.version = 1

        # children
        self.notes = None
        self.thumbnail = None
        self.stage = Stage(self)
        self.hidden = None
        self.headers = None
        self.code = None
        self.blocks = None
        self.variables = data.Variables()

    def deserialize(self, elem):
        """Loads this class from an element tree representation"""

        assert (elem.tag == "project")

        # attributes
        self.name = elem.get("name")
        self.app = elem.get("app")
        self.version = elem.get("version")

        # children
        self.notes = elem.find("notes")
        self.thumbnail = elem.find("thumbnail")
        self.stage.deserialize(elem.find("stage"))
        self.hidden = elem.find("hidden")
        self.headers = elem.find("headers")
        self.code = elem.find("code")
        self.blocks = get_blocks(elem)
        self.variables.deserialize(elem.find("variables"))

    def serialize(self):
        """Return an elementtree representing this object"""

        project = Element("project", name=self.name,
                          app=self.app, version=self.version)

        for child in (self.notes, self.thumbnail, self.stage.serialize(),
                      self.hidden, self.headers, self.code,
                      get_blocks_node(self.blocks), self.variables.serialize()):
            if child is not None:
                project.append(child)
        return project

    def get_variable(self, name):
        """Gets a named variable; returns None if it does not exist"""
        return self.variables.get_variable(name)

    def all_actors(self):
        """Returns the stage and all sprites"""

        all_actors = [self.stage]
        all_actors.extend([sprite for sprite in self.stage.sprites
                           if isinstance(sprite, BaseActor)])
        return all_actors

    def actors_in_drawing_order(self):
        """Returns sprites in the order they should be drawn, back to front"""

        # Sprites should have some sort of z-order parameter, but
        # I don't know what it is yet.
        # Most important is that the stage goes first.
        return self.all_actors()

    def stop_all_scripts(self):
        for actor in self.all_actors():
            actor.stop_all_scripts()
