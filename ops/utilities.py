from . import operator_blocks
from . import variable_blocks
from . import control_blocks
from . import looks_blocks
from . import motion_blocks

search_list = (operator_blocks, variable_blocks,
               control_blocks, looks_blocks,
               motion_blocks)


def bind_to_function(function_name):
    """Takes the name of a function (like "reportSum") and returns
    a reference to that function if it is a known operation."""

    for module in search_list:
        try:
            return getattr(module, function_name)
        except AttributeError:
            pass
    return None
