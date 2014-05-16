import sys
import xmltodict

try:
    import unittest2 as unittest
except ImportError:
    import unittest

sys.path.append('..')
from project import Project
from sprite import Sprite
import util

sample_document = "sample_project.xml"

    
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
		tree = xmltodict.parse(open(sample_document))
		p = Project()
		p.deserialize(tree)
		new_tree = p.serialize()
		#xmltodict.unparse(new_tree)		# just to be sure it works

		self.assertEqual(tree, new_tree)

	def test_serialization_of_sprite(self):
		tree = xmltodict.parse(open(sample_document))["project"]["stage"]["sprites"]["sprite"][0]
		s = Sprite()
		s.deserialize(tree)
		new_tree = s.serialize()
		
		self.assertEqual(tree, new_tree)

if __name__ == '__main__':
    unittest.main()
    