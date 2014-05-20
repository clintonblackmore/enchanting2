
from literal import Literal
from list import List

class_map = { "l" : Literal, "bool" : Literal, "list" : List }

def deserialize_value(element):
	"Get an object representing this element, be it a literal, list or what-not"
	item = class_map[element.tag]()
	item.deserialize(element)
	return item
	
	