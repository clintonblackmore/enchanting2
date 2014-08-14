# import data

"""These are the blue 'motion' blocks"""

import data


def gotoXY(target_actor, parent_script, args):
    x, y = args[0], args[1]
    target_actor.set_property("@x", x)
    target_actor.set_property("@y", y)
    return None


def setXPosition(target_actor, parent_script, args):
    value = args[0]
    return target_actor.set_property("@x", value)


def changeXPosition(target_actor, parent_script, args):
    incr = args[0]
    return target_actor.increment_property("@x", incr.as_number())


def xPosition(target_actor, parent_script, args):
    return target_actor.value_of_property("@x")


def setYPosition(target_actor, parent_script, args):
    value = args[0]
    return target_actor.set_property("@y", value)


def changeYPosition(target_actor, parent_script, args):
    incr = args[0]
    return target_actor.increment_property("@y", incr.as_number())


def yPosition(target_actor, parent_script, args):
    return target_actor.value_of_property("@y")


def forward(target_actor, parent_script, args):
    distance = args[0].as_number()
    target_actor.move_forward(distance)
    return None


def turn(target_actor, parent_script, args):
    angle = args[0].as_number()
    target_actor.increment_property("@heading", angle)
    return None  # target_actor.value_of_property("@heading")


def turnLeft(target_actor, parent_script, args):
    angle = -args[0].as_number()
    target_actor.increment_property("@heading", angle)
    # to do -- hearding should not exceed +- 360 degrees
    return None  # target_actor.value_of_property("@heading")


def setHeading(target_actor, parent_script, args):
    angle = args[0].as_number()
    target_actor.set_property("@heading", data.Literal(angle))
    return None  # target_actor.value_of_property("@heading")


def direction(target_actor, parent_script, args):
    return target_actor.value_of_property("@heading")

    # to do -- lots!
