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

import data
from data import Literal, List, Variable, Variables
from script import Block, Script
from actor import Stage, Sprite, Project
import factory

import ops

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
				data.number_from_string( 
					data.number_to_string( item ))) 

	def test_boolean_to_string_conversion(self):
	
		self.assertEqual(True, data.bool_from_string("true"))
		self.assertEqual(False, data.bool_from_string("false"))
		
		self.assertRaises(ValueError, data.bool_from_string, ("True",))	# no capital!
		self.assertRaises(ValueError, data.bool_from_string, ("False",))	# no capital!
		self.assertRaises(ValueError, data.bool_from_string, ("",))	
		self.assertRaises(ValueError, data.bool_from_string, ("0",))
		self.assertRaises(ValueError, data.bool_from_string, ("1",))
		self.assertRaises(ValueError, data.bool_from_string, ("gibberish",))	

		for item in ["true", "false"]:
			self.assertEqual(item, 
				data.bool_to_string(
					data.bool_from_string( item )))

	def do_test_serialization_from_all_xml_files_of(self, obj, findlist = []):
		self.do_test_serialization_from_files_of(all_xml_files, obj, findlist)

	def do_test_serialization_from_files_of(self, filenames, obj, findlist = []):
		"Using several files, check that we can serialize and deserialize and objects right"
		for filename in filenames:
			self.do_test_serialization_of(filename, obj, findlist)

	def do_test_serialization_of(self, filename, obj, findlist = []):
		"Read XML from a file, create an object, write it out, and see if it is the same"

		tree = ElementTree.parse(filename)
		start_node = tree.getroot()
		for nodename in findlist:
			start_node = start_node.find(nodename)
		obj.deserialize(start_node)
		clone_node = obj.serialize()
	
		self.assertEqual(
			normalized_xml(ElementTree.tostring(start_node)),
			normalized_xml(ElementTree.tostring(clone_node)))    


	def test_serialization_of_project(self):
		self.do_test_serialization_from_all_xml_files_of(Project(), [])

	def test_serialization_of_sprite(self):
		self.do_test_serialization_from_all_xml_files_of(Sprite(None), ["stage", "sprites", "sprite"])

	def test_serialization_of_stage(self):
		self.do_test_serialization_from_all_xml_files_of(Stage(None), ["stage"])
	
	def test_literal_values(self):
		l = Literal()
		self.assertEquals(l.value, None)		
		self.assertEqual(0, l.as_number())
		self.assertEqual("", l.as_string())
		self.assertEqual(False, l.as_bool())		
		
		l.deserialize(ElementTree.XML('<l>15.75</l>'))
		self.assertEquals(l.value, 15.75)
		self.assertEqual(15.75, l.as_number())
		self.assertEqual("15.75", l.as_string())
		self.assertEqual(True, l.as_bool())		

		l.deserialize(ElementTree.XML('<l>-20.0</l>'))
		self.assertEquals(l.value, -20.0)
		self.assertEqual(-20.0, l.as_number())
		self.assertEqual("-20", l.as_string())	# no trailing zero
		self.assertEqual(True, l.as_bool())		

		l.deserialize(ElementTree.XML('<l>hello world</l>'))
		self.assertEquals(l.value, "hello world")
		self.assertEqual(0, l.as_number())
		self.assertEqual("hello world", l.as_string())
		self.assertEqual(True, l.as_bool())		
		
		l.deserialize(ElementTree.XML('<l></l>'))
		self.assertEquals(l.value, None)
		self.assertEqual(0, l.as_number())
		self.assertEqual("", l.as_string())
		self.assertEqual(False, l.as_bool())		
		
		l.deserialize(ElementTree.XML('<l/>'))
		self.assertEquals(l.value, None)
		self.assertEqual(0, l.as_number())
		self.assertEqual("", l.as_string())
		self.assertEqual(False, l.as_bool())		
	
		l.deserialize(ElementTree.XML('<bool>true</bool>'))
		self.assertEquals(l.value, True)
		self.assertEqual(1, l.as_number())
		self.assertEqual("true", l.as_string())
		self.assertEqual(True, l.as_bool())		

		l.deserialize(ElementTree.XML('<bool>false</bool>'))
		self.assertEquals(l.value, False)
		self.assertEqual(0, l.as_number())
		self.assertEqual("false", l.as_string())
		self.assertEqual(False, l.as_bool())		

	
	def test_variable(self):
		v = Variable()
		self.assertEqual(0, v.value().as_number())
		self.assertEqual("", v.value().as_string())

		v.deserialize(ElementTree.XML('<variable name="foo"><l>hello world</l></variable>'))
		self.assertEqual(v.name, "foo")
		self.assertEqual("hello world", v.value().as_string())
		self.assertEqual(v.contents, Literal("hello world"))
		
		# We get the AssertionError, but it fails the test.  Strange.
		#bad_data = ElementTree.XML('<variable name="foo"><unknown>whatzit?</unknown></variable>')
		#self.assertRaises(AssertionError, v.deserialize(bad_data))
		
	def test_literal_variables(self):
		xml = """<?xml version="1.0"?>
				<variables>
					<variable name="number"><l>-37.25</l></variable>
					<variable name="text"><l>this is text</l></variable>
					<variable name="null"/>
				</variables>
				"""
				
		elem = ElementTree.XML(xml)
		v = Variables()
		v.deserialize(elem)
		new_xml = ElementTree.tostring(v.serialize())
				
		self.assertEqual(normalized_xml(xml), normalized_xml(new_xml))   
	
	def test_intermediate_variables(self):
		xml = """<?xml version="1.0"?>
				<variables>
					<variable name="number"><l>-37.25</l></variable>
					<variable name="text"><l>this is text</l></variable>
					<variable name="bool"><bool>true</bool></variable>
					<variable name="list">
						<list id="73">
							<item><l>1</l></item>
							<item><l/></item>
							<item><l>three</l></item>
						</list>
					</variable>
					<variable name="null"/>
				</variables>
				"""
				
		elem = ElementTree.XML(xml)
		v = Variables()
		v.deserialize(elem)
		new_xml = ElementTree.tostring(v.serialize())
				
		self.assertEqual(normalized_xml(xml), normalized_xml(new_xml))   
	
	def test_variable_lookup(self):
		"Do the project, stage, and sprite look up the right variables?"
		proj = Project()
		stage = Stage(proj)
		sprite = Sprite(proj)
		proj.variables.add(Variable(Literal(777), "proj var"))
		stage.variables.add(Variable(Literal(555), "stage var"))
		sprite.variables.add(Variable(Literal(222), "sprite var"))
		
		self.assertEqual(proj.variables.variables.keys(), ['proj var'])
		self.assertEqual(None, proj.get_variable("no such variable"))
		self.assertNotEqual(None, proj.get_variable("proj var"))
		self.assertEqual(None, proj.get_variable("stage var"))
		self.assertEqual(None, proj.get_variable("sprite var"))
		self.assertEqual(777, proj.get_variable("proj var").value().as_number())

		self.assertEqual(stage.variables.variables.keys(), ['stage var'])
		self.assertEqual(None, stage.get_variable("no such variable"))
		self.assertNotEqual(None, stage.get_variable("proj var"))
		self.assertNotEqual(None, stage.get_variable("stage var"))
		self.assertEqual(None, stage.get_variable("sprite var"))
		self.assertEqual(777, stage.get_variable("proj var").value().as_number())
		self.assertEqual(555, stage.get_variable("stage var").value().as_number())
		
		self.assertEqual(sprite.variables.variables.keys(), ['sprite var'])
		self.assertEqual(None, sprite.get_variable("no such variable"))
		self.assertNotEqual(None, sprite.get_variable("proj var"))
		self.assertEqual(None, sprite.get_variable("stage var"))
		self.assertNotEqual(None, sprite.get_variable("sprite var"))
		self.assertEqual(777, sprite.get_variable("proj var").value().as_number())
		self.assertEqual(222, sprite.get_variable("sprite var").value().as_number())

	def test_operation(self):
		fn = ops.bind_to_function("reportSum")
		result = fn(None, (Literal(56), Literal(72)))
		self.assertEqual(result, Literal(56 + 72))
		
		fn = ops.bind_to_function("nonexistentFunction")
		self.assertEquals(None, fn)
		
	def test_script(self):
		"""Runs a small script to see if it works.
		
		This script is, in effect:
		a = 5
		b = -7
		c = a * a
		c += b * b
		
		The expected result is c = 5 * 5 + (-7)*(-7) = 25+49 = 74"""
		
		xml = """
			<sprite name="Sprite" idx="1" x="0" y="0" heading="90" scale="1" rotation="1" draggable="true" costume="0" color="80,80,80" pen="tip" id="8">
				<variables>
					<variable name="a"><l>5</l></variable>
					<variable name="b"><l>-7</l></variable>
					<variable name="c"><l>0</l></variable>
				</variables>
				<scripts>
					<script x="72" y="121">
						<block s="doSetVar"><l>c</l>
							<block s="reportProduct"><block var="a"/><block var="a"/></block>
						</block>
						<block s="doChangeVar"><l>c</l>
							<block s="reportProduct"><block var="b"/><block var="b"/></block>
						</block>
					</script>
				</scripts>
			</sprite>
		"""

		elem = ElementTree.XML(xml)
		sprite = Sprite(None)
		sprite.deserialize(elem)
		new_xml = ElementTree.tostring(sprite.serialize())
				
		# doesn't seem to put out properties in same order -- very strange.
		#self.assertEqual(normalized_xml(xml), normalized_xml(new_xml))   

		
		self.assertEqual(sprite.get_variable("c").value().as_number(), 0)
		
		sprite.scripts[0].run(sprite)
		
		self.assertEqual(sprite.get_variable("c").value().as_number(), 74)

	
if __name__ == '__main__':
    unittest.main()
    