"""These are the purple 'looks' blocks"""
import gevent

import data


def bubble(target_actor, parent_script, args):
    message = args[0].as_string()
    target_actor.say_or_think(message, False)
    return None  # command-blocks always return None


# reporter blocks always return a value
# (usually a 'Literal' object)

def doSayFor(target_actor, parent_script, args):
    message = args[0].as_string()
    duration = args[1].as_number()
    target_actor.say_or_think(message, False)
    gevent.sleep(duration)
    target_actor.say_or_think("", False)


def doThink(target_actor, parent_script, args):
    message = args[0].as_string()
    target_actor.say_or_think(message, True)
    return None


def doSayFor(target_actor, parent_script, args):
    message = args[0].as_string()
    duration = args[1].as_number()
    target_actor.say_or_think(message, True)
    gevent.sleep(duration)
    target_actor.say_or_think("", True)


def doSwitchToCostume(target_actor, parent_script, args):
    target_actor.set_costume(args[0])
    return None


def doWearNextCostume(target_actor, parent_script, args):
    target_actor.next_costume()
    return None


def getCostumeIdx(target_actor, parent_script, args):
    return data.Literal(target_actor.costume)


def changeScale(target_actor, parent_script, args):
    delta_scale = args[0].as_number() / 100
    target_actor.increment_variable("@scale", delta_scale)
    return None


def setScale(target_actor, parent_script, args):
    scale = args[0].as_number() / 100
    target_actor.set_variable("@scale", data.Literal(scale))
    return None


def getScale(target_actor, parent_script, args):
    scale = target_actor.value_of_variable("@scale")
    return data.Literal(scale.as_number() * 100)

# to do -- lots!
