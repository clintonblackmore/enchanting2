import sys
import glob

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
from literal import Literal

import util

sample_document = "sample_project_no_media.xml"
all_xml_files = glob.glob('*.xml')


def normalized_xml(xml):
	"We convert the xml to an object tree and back and return the result, without whitespace"
	obj = objectify.fromstring(xml)
	return etree.tostring(obj)
	    
class PyInterpreterTestCase(unittest.TestCase):

	def test_number_to_string_conversion(self):
		for item in [0, 7, 40, 500, 0.2, 1e5, -14.7, 138.86512022365332]:
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

	def do_test_serialization_from_all_xml_files_of(self, filenames, klass, findlist = []):
		self.do_test_serialization_from_files_of(all_xml_files, klass, findlist)

	def do_test_serialization_from_files_of(self, filenames, klass, findlist = []):
		"Using several files, check that we can serialize and deserialize and objects right"
		for filename in filenames:
			self.do_test_serialization_of(filename, klass, findlist)

	def do_test_serialization_of(self, filename, klass, findlist = []):
		"Read XML from a file, create an object, write it out, and see if it is the same"

		tree = ElementTree.parse(filename)
		start_node = tree.getroot()
		for nodename in findlist:
			start_node = start_node.find(nodename)
		obj = klass()
		obj.deserialize(start_node)
		clone_node = obj.serialize()
	
		self.assertEqual(
			normalized_xml(ElementTree.tostring(start_node)),
			normalized_xml(ElementTree.tostring(clone_node)))    


	def test_serialization_of_project(self):
		self.do_test_serialization_from_all_xml_files_of(sample_document, Project, [])

	def test_serialization_of_sprite(self):
		self.do_test_serialization_from_all_xml_files_of(sample_document, Sprite, ["stage", "sprites", "sprite"])

	def test_serialization_of_stage(self):
		self.do_test_serialization_from_all_xml_files_of(sample_document, Stage, ["stage"])
	
	def test_literal_values(self):
		l = Literal()
		self.assertEquals(l.value, None)		
		self.assertEqual(0, l.as_number())
		self.assertEqual("", l.as_string())
		
		l.deserialize(ElementTree.XML('<l>15.75</l>'))
		self.assertEquals(l.value, 15.75)
		self.assertEqual(15.75, l.as_number())
		self.assertEqual("15.75", l.as_string())

		l.deserialize(ElementTree.XML('<l>-20.0</l>'))
		self.assertEquals(l.value, -20.0)
		self.assertEqual(-20.0, l.as_number())
		self.assertEqual("-20", l.as_string())	# no trailing zero

		l.deserialize(ElementTree.XML('<l>hello world</l>'))
		self.assertEquals(l.value, "hello world")
		self.assertEqual(0, l.as_number())
		self.assertEqual("hello world", l.as_string())
		
		l.deserialize(ElementTree.XML('<l></l>'))
		self.assertEquals(l.value, None)
		self.assertEqual(0, l.as_number())
		self.assertEqual("", l.as_string())
		
		l.deserialize(ElementTree.XML('<l/>'))
		self.assertEquals(l.value, None)
		self.assertEqual(0, l.as_number())
		self.assertEqual("", l.as_string())
	
if __name__ == '__main__':
    unittest.main()
    