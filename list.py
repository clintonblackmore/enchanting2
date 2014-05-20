from xml.etree.cElementTree import Element

import factory

class List:
	"""Represents a list.
	
	A sample list in xml might look like:
	
	<list id="73">
		<item><l>1</l></item>
		<item><l/></item>
		<item><l>three</l></item>
	</list>"""
	
	
	def __init__(self):
		self.list = []
		self.id = -1
		
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "list")
		self.id = elem.get("id")
		for item in elem:
			self.list.append(factory.deserialize_value(item[0]))
		
	def serialize(self):
		"Save out as an element tree"
		lst = Element("list", id=self.id)
		for entry in self.list:
			item = Element("item")
			item.append(entry.serialize())
			lst.append(item)
		return lst
			
	def as_number(self):
		return 0
			
	def as_string(self):
		return "[a list]"	# to do
		
	def as_bool(self):
		return True			# seems to be how Snap! responds
		
		
	
	
			