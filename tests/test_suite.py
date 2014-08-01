import sys
import os
import glob
from xml.etree import cElementTree as ElementTree
from xml.dom import minidom

import six
from lxml import etree
from lxml import objectify


try:
    import unittest2 as unittest
except ImportError:
    import unittest

from collections import OrderedDict

sys.path.append('..')

import data
from data import Literal, List, Variable, Variables
from script import Block, Script
from actor import Stage, Sprite, Project
import factory
import event_loop

import ops

sample_document = "sample_project_no_media.xml"
all_xml_files = glob.glob('*.xml')


def normalized_xml(xml):
    "We convert the xml to an object tree and back and return the result, without whitespace"

    parser = etree.XMLParser(remove_blank_text=True)  # lxml.etree only!
    root = etree.XML(xml, parser)
    xml_stage_2 = etree.tostring(root)

    reparsed = minidom.parseString(xml_stage_2)
    return reparsed.toprettyxml()


def clean_output_directories():
    "Make sure that output directories exist and are empty"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for subdir in ("original_xml", "serialized_xml"):
        absolute_subdir = os.path.join(script_dir, subdir)
        if not os.path.isdir(absolute_subdir):
            os.mkdir(absolute_subdir)
        else:
            for filename in os.listdir(absolute_subdir):
                file_path = os.path.join(absolute_subdir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception, e:
                    print e


def search_tree_for_anomalies(tree):
    for elem in tree.getiterator():
        print_ancestry = False
        if elem is None:
            print "None elem found"
        else:
            for key in elem.keys():
                value = elem.get(key)
                if not isinstance(value, six.string_types):
                    print "In %s found bad attr val: %s -> %s" % (elem.tag, key, repr(value))


class PyInterpreterTestCase(unittest.TestCase):
    def test_number_to_string_conversion(self):
        for item in [0, 7, 40, 500, 0.2, 1e5, -14.7, 138.86512022365332]:
            self.assertEqual(item,
                             data.number_from_string(
                                 data.number_to_string(item)))

    def compare_xml(self, xml, new_xml, save_to_files, test_file_name):
        "Compare the old and new XML, and write them to files for diffing on request"

        xml = normalized_xml(xml)
        new_xml = normalized_xml(new_xml)
        if save_to_files:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            for subdir, data in (("original_xml", xml), ("serialized_xml", new_xml)):
                filename = os.path.join(script_dir, subdir, test_file_name)
                with open(filename, 'w') as f:
                    f.write(data)
        self.assertEqual(xml, new_xml)


    def test_boolean_to_string_conversion(self):

        self.assertEqual(True, data.bool_from_string("true"))
        self.assertEqual(False, data.bool_from_string("false"))

        self.assertRaises(ValueError, data.bool_from_string, ("True",))  # no capital!
        self.assertRaises(ValueError, data.bool_from_string, ("False",))  # no capital!
        self.assertRaises(ValueError, data.bool_from_string, ("",))
        self.assertRaises(ValueError, data.bool_from_string, ("0",))
        self.assertRaises(ValueError, data.bool_from_string, ("1",))
        self.assertRaises(ValueError, data.bool_from_string, ("gibberish",))

        for item in ["true", "false"]:
            self.assertEqual(item,
                             data.bool_to_string(
                                 data.bool_from_string(item)))

    def do_test_serialization_from_all_xml_files_of(self, obj, findlist=[]):
        self.do_test_serialization_from_files_of(all_xml_files, obj, findlist)

    def do_test_serialization_from_files_of(self, filenames, obj, findlist=[]):
        "Using several files, check that we can serialize and deserialize and objects right"
        for filename in filenames:
            self.do_test_serialization_of(filename, obj, findlist)

    def do_test_serialization_of(self, filename, obj, findlist=[]):
        "Read XML from a file, create an object, write it out, and see if it is the same"

        tree = ElementTree.parse(filename)
        start_node = tree.getroot()
        for nodename in findlist:
            start_node = start_node.find(nodename)
        obj.deserialize(start_node)
        clone_node = obj.serialize()

        search_tree_for_anomalies(clone_node)

        self.compare_xml(
            ElementTree.tostring(start_node),
            ElementTree.tostring(clone_node),
            True,
            "".join((obj.__class__.__name__, "_", filename)))

    def do_test_using_factory(self, xml, filename):
        obj = factory.deserialize_value(ElementTree.XML(xml))
        new_xml = ElementTree.tostring(obj.serialize())
        self.compare_xml(xml, new_xml, True, filename)

    def test_serialization_of_project(self):
        self.do_test_serialization_from_all_xml_files_of(Project(None), [])

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
        self.assertEqual("-20", l.as_string())  # no trailing zero
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

    def test_literal_with_option(self):
        xml = "<l><option>space</option></l>"
        l = Literal()
        l.deserialize(ElementTree.XML(xml))
        new_xml = ElementTree.tostring(l.serialize())
        self.compare_xml(xml, new_xml, True, "literal_option.xml")

    def test_literal_repr(self):
        x = Literal()
        self.assertEqual(x, eval(repr(x)))

        x = Literal(12)
        self.assertEqual(x, eval(repr(x)))

        x = Literal("text")
        self.assertEqual(x, eval(repr(x)))

        x = Literal(True)
        self.assertEqual(x, eval(repr(x)))

        x = Literal(False)
        self.assertEqual(x, eval(repr(x)))

        x = Literal(None)
        self.assertEqual(x, eval(repr(x)))

    def test_literal_comparisons(self):
        self.assertEqual(Literal(10), Literal(10))
        self.assertEqual(Literal(10), Literal("10"))
        self.assertEqual(Literal("10"), Literal("10"))
        self.assertEqual(Literal("10"), Literal(10))

        self.assertNotEqual(Literal(10), Literal(20))
        self.assertNotEqual(Literal(10), Literal("20"))
        self.assertNotEqual(Literal("10"), Literal("20"))
        self.assertNotEqual(Literal("10"), Literal(20))

        self.assertNotEqual(Literal(10), Literal("ten"))

        self.assertEqual(Literal("apple"), Literal("ApPlE"))

        self.assertTrue(Literal(10) < Literal(20))
        self.assertTrue(Literal(10) < Literal("20"))
        self.assertTrue(Literal("10") < Literal("20"))
        self.assertTrue(Literal("10") < Literal(20))
        self.assertTrue(Literal("Apple") < Literal("Banana"))
        self.assertTrue(Literal("A") < Literal("B"))
        self.assertTrue(Literal("a") < Literal("B"))
        self.assertTrue(Literal("A") < Literal("b"))
        self.assertTrue(Literal("a") < Literal("b"))

        self.assertFalse(Literal(10) > Literal(20))
        self.assertFalse(Literal(10) > Literal("20"))
        self.assertFalse(Literal("10") > Literal("20"))
        self.assertFalse(Literal("10") > Literal(20))
        self.assertFalse(Literal("Apple") > Literal("Banana"))
        self.assertFalse(Literal("A") > Literal("B"))
        self.assertFalse(Literal("a") > Literal("B"))
        self.assertFalse(Literal("A") > Literal("b"))
        self.assertFalse(Literal("a") > Literal("b"))

        self.assertTrue(Literal(10) < Literal("ten"))  # string comparison

    def test_list_with_items(self):
        xml = """
			<list id="73">
				<item><l>1</l></item>
				<item><l/></item>
				<item><l>three</l></item>
			</list>
		"""
        self.do_test_using_factory(xml, "list_with_items.xml")

    def test_list_without_items(self):
        xml = """
			<list id="73">
				<l>1</l>
				<l/>
				<l>three</l>
			</list>
		"""
        self.do_test_using_factory(xml, "list_without_items.xml")

    def test_variable(self):
        v = Variable()
        self.assertEqual(0, v.value().as_number())
        self.assertEqual("", v.value().as_string())

        v.deserialize(ElementTree.XML('<variable name="foo"><l>hello world</l></variable>'))
        self.assertEqual(v.name, "foo")
        self.assertEqual("hello world", v.value().as_string())
        self.assertEqual(v.contents, Literal("hello world"))

    # We get the AssertionError, but it fails the test.  Strange.
    # bad_data = ElementTree.XML('<variable name="foo"><unknown>whatzit?</unknown></variable>')
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

        self.compare_xml(xml, new_xml, True, "literals_simple.xml")

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

        self.compare_xml(xml, new_xml, True, "literals_intermediate.xml")

    def test_variable_lookup(self):
        "Do the project, stage, and sprite look up the right variables?"
        proj = Project(None)
        stage = Stage(proj)
        sprite = Sprite(proj)
        proj.variables.add(Variable("proj var", Literal(777)))
        stage.variables.add(Variable("stage var", Literal(555)))
        sprite.variables.add(Variable("sprite var", Literal(222)))

        self.assertEqual(
            [key for key in proj.variables.variables.keys() if not key.startswith("@")],
            ['proj var'])
        self.assertEqual(None, proj.get_variable("no such variable"))
        self.assertNotEqual(None, proj.get_variable("proj var"))
        self.assertEqual(None, proj.get_variable("stage var"))
        self.assertEqual(None, proj.get_variable("sprite var"))
        self.assertEqual(777, proj.get_variable("proj var").value().as_number())

        self.assertEqual(
            [key for key in stage.variables.variables.keys() if not key.startswith("@")],
            ['stage var'])
        self.assertEqual(None, stage.get_variable("no such variable"))
        self.assertNotEqual(None, stage.get_variable("proj var"))
        self.assertNotEqual(None, stage.get_variable("stage var"))
        self.assertEqual(None, stage.get_variable("sprite var"))
        self.assertEqual(777, stage.get_variable("proj var").value().as_number())
        self.assertEqual(555, stage.get_variable("stage var").value().as_number())

        self.assertEqual(
            [key for key in sprite.variables.variables.keys() if not key.startswith("@")],
            ['sprite var'])
        self.assertEqual(None, sprite.get_variable("no such variable"))
        self.assertNotEqual(None, sprite.get_variable("proj var"))
        self.assertEqual(None, sprite.get_variable("stage var"))
        self.assertNotEqual(None, sprite.get_variable("sprite var"))
        self.assertEqual(777, sprite.get_variable("proj var").value().as_number())
        self.assertEqual(222, sprite.get_variable("sprite var").value().as_number())

    def test_variable_repr(self):
        x = Variable("name", Literal("val"))
        self.assertEqual(x, eval(repr(x)))

    def test_variables_repr(self):
        v = Variables(OrderedDict([
            ('x', Variable('x', Literal(47.0))),
            ('y', Variable('y', Literal(52.0)))]))
        self.assertEqual(v, eval(repr(v)))

    def test_operation(self):
        fn = ops.bind_to_function("reportSum")
        result = fn(None, None, (Literal(56), Literal(72)))
        self.assertEqual(result, Literal(56 + 72))

        fn = ops.bind_to_function("nonexistentFunction")
        self.assertEquals(None, None, fn)

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

        # Woohoo.  We can compare this successfully now!
        self.compare_xml(xml, new_xml, True, "script.xml")

        self.assertEqual(sprite.get_variable("c").value().as_number(), 0)

        sprite.scripts[0].run(sprite)

        self.assertEqual(sprite.get_variable("c").value().as_number(), 74)

    def test_costume(self):

        xml = """
			<costume name="costume1" center-x="125" center-y="63" image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAALCAYAAABLcGxfAAAAlklEQVQoU2NkQAUKQK4+EBtAhS8A6YtA/ACmjBHKACnsB+IANANg3A1ARiFII0gDyLT9QCwAkv1vjaqF8Sic/wHIcgRpADH40RWi2wTV+AGk4T8hxXD3A22jkwZsnsXhB7CTFgBxPD5NSCG1EBYPE4Aa8mGmwgIBSSFIaiIQF8A0gARA8VEApUGxDQKgWAbFNshAEM0AANFJJceqzy0EAAAAAElFTkSuQmCC" id="16"/>
		"""

        self.do_test_using_factory(xml, "costume.xml")

    def test_costumes(self):

        xml = """
		<costumes>
			<list id="15">
				<item>
					<costume name="costume1" center-x="125" center-y="63" image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAALCAYAAABLcGxfAAAAlklEQVQoU2NkQAUKQK4+EBtAhS8A6YtA/ACmjBHKACnsB+IANANg3A1ARiFII0gDyLT9QCwAkv1vjaqF8Sic/wHIcgRpADH40RWi2wTV+AGk4T8hxXD3A22jkwZsnsXhB7CTFgBxPD5NSCG1EBYPE4Aa8mGmwgIBSSFIaiIQF8A0gARA8VEApUGxDQKgWAbFNshAEM0AANFJJceqzy0EAAAAAElFTkSuQmCC" id="16"/>
				</item>
			</list>
		</costumes>
		"""

        self.do_test_using_factory(xml, "costumes.xml")

    def test_empty_costumes(self):

        xml = """
		<costumes>
			<list id="26" />
		</costumes>
		"""

        self.do_test_using_factory(xml, "costumes.xml")

    def do_test_script(self, filename, pre_check={}, post_check={}, injection={}):
        "Lets you easily test the first script of the first sprite"

        unused_loop = None  #event_loop.EventLoop()

        tree = ElementTree.parse(filename)
        project = Project(unused_loop)
        project.deserialize(tree.getroot())

        sprite = project.stage.sprites[0]
        test_script = sprite.scripts[0]

        # Run the pre-check
        for variable_name, start_value in pre_check.items():
            self.assertEqual(sprite.get_variable(variable_name).value(), start_value)

        # Inject any values
        for variable_name, injected_value in injection.items():
            sprite.set_variable(variable_name, injected_value)

        # Run the script
        test_script.run(sprite)

        # Run the post-check
        for variable_name, final_value in post_check.items():
            self.assertEqual(sprite.get_variable(variable_name).value(), final_value)


    def test_repeat_block(self):

        """Increment a counter five times in a loop.

        set count to 0
        repeat 5
            change count by 1

        The final result should be 5."""

        self.do_test_script("simple_repeat_loop.xml",
                            {"count": Literal(0)},
                            {"count": Literal(5)})


    def test_nested_repeat_block(self):
        """Increment a counter in a loop that is within a loop

        set count to 0
        repeat 10
            repeat 5
                change count by 1

        The final result should be 50."""

        self.do_test_script("nested_repeat_loops.xml",
                            {"count": Literal(0)},
                            {"count": Literal(50)})

    def test_bad_repeat_blocks(self):
        """Try out various pathological loops.

        set count to 0			count is 0
        repeat count            repeats 0x
            change count by 1
        repeat 0                repeats 0x
            change count by 1
        repeat -1               repeats 0x
            change count by 1
        repeat 0.5              repeats 0x
            change count by 1
        change count by 1       count goes from 0 -> 1
        repeat count            repeats 1x
            change count by 1

        The final result should be 2."""

        self.do_test_script("bad_repeat_loops.xml",
                            {"count": Literal(0)},
                            {"count": Literal(2)})

    def test_if_block(self):
        """Tests some if blocks

        Tests doIf, doIfElse, and reportEquals

        set result to "meh"
        if feeling == "happy"
            set result to "smile"
        else
            if feeling == "sad"
                set result to "frown"
        """

        filename = "if_test.xml"

        self.do_test_script(filename,
            {}, {"result": Literal("smile")}, {"feeling": Literal("happy")})

        self.do_test_script(filename,
            {}, {"result": Literal("frown")}, {"feeling": Literal("sad")})

        self.do_test_script(filename,
            {}, {"result": Literal("meh")}, {"feeling": Literal("whatever")})


if __name__ == '__main__':
    clean_output_directories()
    unittest.main()
    