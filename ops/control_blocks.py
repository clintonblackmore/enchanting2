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
        parent_script.repeat = initial_count.evaluate(target_actor, parent_script).as_number()
    else:
        parent_script.repeat -= 1

    if parent_script.repeat >= 1:
        parent_script.subscript = script.from_start()
    else:
        parent_script.repeat = 0
    return data.Literal(parent_script.repeat)


def doForever(target_actor, parent_script, args):
    script = args[0]
    parent_script.repeat = True
    parent_script.subscript = script.from_start()
    return None


def doIf(target_actor, parent_script, args):
    condition, true_block = args
    if condition.evaluate(target_actor, parent_script).as_bool():
        parent_script.subscript = true_block.from_start()


def doIfElse(target_actor, parent_script, args):
    condition, true_block, false_block = args
    if condition.evaluate(target_actor, parent_script).as_bool():
        parent_script.subscript = true_block.from_start()
    else:
        parent_script.subscript = false_block.from_start()


def doBroadcast(target_actor, parent_script, args):
    message = args[0].as_string()
    target_actor.project.event_loop.broadcast_message(message)





    # to do -- lots!