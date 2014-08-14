import gevent

import data

"""These are the yellow 'control' blocks"""

# The 'receive' blocks don't actually do their work here


def receiveGo(target_actor, parent_script, args):
    return None


def receiveKey(target_actor, parent_script, args):
    return None


def receiveMessage(target_actor, parent_script, args):
    return None


def receiveClick(target_actor, parent_script, args):
    return None


def doWait(target_actor, parent_script, args):
    gevent.sleep(args[0].as_number())
    return None


def doRepeat(target_actor, parent_script, args):
    # We are in a loop
    initial_count, script = args

    # Did we just start for the first time?
    if not parent_script.repeat:
        # Yes, this is the first time
        parent_script.repeat = initial_count.evaluate(
            target_actor, parent_script).as_number()
    else:
        parent_script.repeat -= 1

    if parent_script.repeat >= 1:
        parent_script.activate_subscript(script)
    else:
        parent_script.repeat = 0
    return data.Literal(parent_script.repeat)


def doForever(target_actor, parent_script, args):
    script = args[0]
    parent_script.repeat = True
    parent_script.activate_subscript(script)
    return None


def doIf(target_actor, parent_script, args):
    condition, true_block = args
    if condition.evaluate(target_actor, parent_script).as_bool():
        parent_script.activate_subscript(true_block)


def doIfElse(target_actor, parent_script, args):
    condition, true_block, false_block = args
    if condition.evaluate(target_actor, parent_script).as_bool():
        parent_script.activate_subscript(true_block)
    else:
        parent_script.activate_subscript(false_block)


def doBroadcast(target_actor, parent_script, args):
    message = args[0].as_string()
    target_actor.project.event_loop.broadcast_message(message)


def doReport(target_actor, parent_script, args):
    result = args[0]
    raise StopIteration(result)

# to do -- lots!
