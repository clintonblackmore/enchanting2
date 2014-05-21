
import operator_blocks
import variable_blocks

search_list = (operator_blocks, variable_blocks)

def bind_to_function(function_name):
	"""Takes the name of a function (like "reportSum") and returns
	a reference to that function if it is a known operation."""

	for module in search_list:
		try:
			return getattr(module, function_name)
		except AttributeError:
			pass
	return None

	