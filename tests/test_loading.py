import sys
import xmltodict

from xml.etree import cElementTree as ElementTree

from lxml import etree
from lxml import objectify

try:
    import unittest2 as unittest
except ImportError:
    import unittest

sys.path.append('..')
from project import Project
from sprite import Sprite
from stage import Stage

import util

#sample_document = "sample_project.xml"
sample_document = "sample_project_no_media.xml"


def normalized_xml(xml):
	"We convert the xml to an object tree and back and return the result, without whitespace"
	obj = objectify.fromstring(xml)
	return etree.tostring(obj)
	
    
class PyInterpreterTestCase(unittest.TestCase):

	def test_number_to_string_conversion(self):
		for item in [0, 7, 40, 500, 0.2, 1e5, -14.7]:
			self.assertEqual(item, 
				util.number_from_string( 
					util.number_to_string( item ))) 

	def test_boolean_to_string_conversion(self):
	
		self.assertEqual(True, util.bool_from_string("true"))
		self.assertEqual(False, util.bool_from_string("false"))
		
		self.assertRaises(ValueError, util.bool_from_string, ("True",))	# no capital!
		self.assertRaises(ValueError, util.bool_from_string, ("False",))	# no capital!
		self.assertRaises(ValueError, util.bool_from_string, ("",))	
		self.assertRaises(ValueError, util.bool_from_string, ("0",))
		self.assertRaises(ValueError, util.bool_from_string, ("1",))
		self.assertRaises(ValueError, util.bool_from_string, ("gibberish",))	

		for item in ["true", "false"]:
			self.assertEqual(item, 
				util.bool_to_string(
					util.bool_from_string( item )))

	def test_serialization_of_project(self):
		tree = ElementTree.parse(sample_document)
		p = Project()
		p.deserialize(tree.getroot())
		new_tree = ElementTree.ElementTree(p.serialize())
		
		self.assertEqual(
				normalized_xml(ElementTree.tostring(tree.getroot())),
				normalized_xml(ElementTree.tostring(new_tree.getroot())))

	def test_serialization_of_sprite(self):
		tree = ElementTree.parse(sample_document)
		start_node = tree.getroot().find("stage").find("sprites").find("sprite")
		s = Sprite()
		s.deserialize(start_node)
		new_tree = ElementTree.ElementTree(s.serialize())
		
		self.assertEqual(
				normalized_xml(ElementTree.tostring(start_node)),
				normalized_xml(ElementTree.tostring(new_tree.getroot())))

	def test_serialization_of_stage(self):
		tree = xmltodict.parse(open(sample_document))["project"]["stage"]
		s = Stage()
		s.deserialize(tree)
		new_tree = s.serialize()
		
		self.assertEqual(tree, new_tree)


if __name__ == '__main__':
    unittest.main()
    