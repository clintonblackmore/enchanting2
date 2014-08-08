"""factory.py lets you deserialize an unknown type from XML"""

import xml.etree.cElementTree as ElementTree

import data
import script
import media
import actor


def deserialize_value(element, *args):
    """Get an object representing this element,
    be it a literal, list or what-not"""

    class_map = {
        "block-definition": script.BlockDefinition,
        "block": script.Block,
        "blocks": script.Blocks,
        "bool": data.Literal,
        "color": data.Color,
        "comment": data.Comment,
        "costume": media.Costume,
        "costumes": media.Costumes,
        "l": data.Literal,
        "list": data.List,
        "project": actor.Project,
        "script": script.Script,
    }

    # if element.tag == "list":
    #    ElementTree.dump(element)

    item = class_map[element.tag](*args)
    item.deserialize(element)
    return item


def deserialize_xml(xml, *args):
    """Take some XML and return an object for it"""
    return deserialize_value(ElementTree.XML(xml), *args)


def deserialize_file(filename, *args):
    """Return the object represented by the data in the file"""
    return deserialize_value(ElementTree.parse(filename).getroot(), *args)


def xml_for_object(object):
    """Return the XML that represents this object"""
    return ElementTree.tostring(object.serialize())
