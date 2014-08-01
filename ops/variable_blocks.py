"""These are the orange 'variable' blocks"""


def var(target_actor, parent_script, name):
    """We expect a variable 'name', not the regular 'args' parameter,
    as the XML for this block is different."""
    return target_actor.value_of_variable(name)


def doSetVar(target_actor, parent_script, args):
    name, value = (args[0].as_string(), args[1])
    return target_actor.set_variable(name, value)


def doChangeVar(target_actor, parent_script, args):
    name, incr = (args[0].as_string(), args[1])
    return target_actor.increment_variable(name, incr.as_number())


def doShowVar(target_actor, parent_script, args):
    name = args[0].as_string()
    return target_actor.show_variable(name, True)


def doHideVar(target_actor, parent_script, args):
    name = args[0].as_string()
    return target_actor.show_variable(name, False)

# many more to do here



	
