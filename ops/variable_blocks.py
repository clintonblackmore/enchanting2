"""These are the orange 'variable' blocks"""

import data


def var(target_actor, parent_script, name):
    """We expect a variable 'name', not the regular 'args' parameter,
    as the XML for this block is different."""
    return parent_script.value_of_variable(target_actor, name)


def doSetVar(target_actor, parent_script, args):
    name, value = (args[0].as_string(), args[1])
    return parent_script.set_variable(target_actor, name, value)


def doChangeVar(target_actor, parent_script, args):
    name, incr = (args[0].as_string(), args[1])
    return parent_script.increment_variable(
        target_actor,
        name,
        incr.as_number())


def doShowVar(target_actor, parent_script, args):
    name = args[0].as_string()
    return parent_script.show_variable(target_actor, name, True)


def doHideVar(target_actor, parent_script, args):
    name = args[0].as_string()
    return parent_script.show_variable(target_actor, name, False)


def doDeclareVariables(target_actor, parent_script, args):
    list_of_vars = args[0]
    for var_name in list_of_vars.list:
        parent_script.variables.add(data.Variable(var_name.as_string()))

# many more to do here
