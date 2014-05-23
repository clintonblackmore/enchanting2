"""factory.py lets you deserialize an unknown type from XML"""

import data
import script

import xml.etree.cElementTree as ElementTree


def deserialize_value(element, target = None):
	"Get an object representing this element, be it a literal, list or what-not"
	
	class_map = { "l" : data.Literal, 
				  "bool" : data.Literal, 
				  "color" : data.Color,
				  "comment" : data.Comment,
				  "list" : data.List,
				  "block" : script.Block,
				  "script" : script.Script 
				}
	
	if element.tag == "color":
		ElementTree.dump(element)
				
	item = class_map[element.tag]()
	item.deserialize(element)
	return item
