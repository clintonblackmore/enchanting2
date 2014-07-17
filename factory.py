"""factory.py lets you deserialize an unknown type from XML"""

import xml.etree.cElementTree as ElementTree


import data
import script
import media


def deserialize_value(element):
	"Get an object representing this element, be it a literal, list or what-not"
	
	class_map = { "l" : data.Literal, 
				  "bool" : data.Literal, 
				  "color" : data.Color,
				  "comment" : data.Comment,
				  "list" : data.List,
				  "block" : script.Block,
				  "script" : script.Script,
				  "costume" : media.Costume,
				  "costumes" : media.Costumes,
				}
	
	#if element.tag == "list":
	#	ElementTree.dump(element)
								
	item = class_map[element.tag]()
	item.deserialize(element)
	return item
