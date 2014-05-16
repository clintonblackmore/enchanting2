import xmltodict


def walk(node, indent = 0):
	for key, item in node.items():
		if isinstance(item, dict):
			walk(item, indent + 1)
		else:
			print "  " * indent + "%s:%s" % (key, str(item)[:40])
#			print "  " * indent + "key is %s" % (key,) 
#			print "  " * indent + "item is %s" % (item,) 

#def walk(node, indent = 0, parent_name = None):
#	if isinstance(node, dict):
#		for key, item in node.items():
#			walk(item, indent + 1, key)
#	else if isinstance(node, list):
#		for index, item in enumerate(node):
#			walk(item, index + 1, "%d" % index)
#	else:
#		print "  " * indent + parent_name + 
			

filename = "copter.xml"

tree = xmltodict.parse(open(filename))

p = new Project()
p.from_tree(tree)


indent = 0
#walk(tree)

