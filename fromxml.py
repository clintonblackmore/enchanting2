import xmltodict

from project import Project

filename = "copter.xml"
tree = xmltodict.parse(open(filename))
p = Project()
p.deserialize(tree)

new_tree = p.serialize()
xmltodict.unparse(new_tree)

print 
print new_tree == tree

