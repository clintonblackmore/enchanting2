import sys
import xmltodict

try:
    import unittest2 as unittest
except ImportError:
    import unittest

sys.path.append('..')
from project import Project

    
class PyInterpreterTestCase(unittest.TestCase):

	def test_serialization(self):
		from project import Project

		filename = "sample_project.xml"
		tree = xmltodict.parse(open(filename))
		p = Project()
		p.deserialize(tree)
		new_tree = p.serialize()
		xmltodict.unparse(new_tree)		# just to be sure it works

		self.assertEqual(tree, new_tree)


if __name__ == '__main__':
    unittest.main()
    