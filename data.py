"""data.py contains classes that wrap or deal with data.

It includes:
  some utility functions for converting/massaging data
  Literal - which wraps numbers, strings, bools, and None
  List - which contain many Literals (or other Lists)
  Variable - contains a named piece of data
  Variables - a collection of Variable objects
"""

from xml.etree.cElementTree import Element
from collections import OrderedDict

import factory


# Utility functions

def number_from_string(s):
    """Takes a string and returns a number"""
    return float(s)


def number_to_string(n):
    """Returns a number as a string, favouring integers over floats"""
    if int(n) == n:
        return str(int(n))
        # return str(n)
    return repr(n)  # gives us more (in)significant digits


def bool_from_string(s):
    """Takes an xml string and returns a bool"""
    if s == "true":
        return True
    if s == "false":
        return False
    raise ValueError("Boolean value from xml must be 'true' or 'false'")


def bool_to_string(b):
    """Takes a python boolean and returns a string for xml"""
    if b:
        return "true"
    return "false"


class Literal(object):

    """Represents a single value.
    It might be a number, a boolean, a string, or so on.
    It is not a variable, and has no name."""

    # I am not sure yet if this should do booleans as well or not
    # A list, on the other hand, is a separate beast
    # (it'll need to keep track of changes in time differently,
    # for example).  Also note sure about functions, etc.

    def __init__(self, value=None):
        self.set_value(value)
        self.is_option = False  # Is this an option selected from a combo box?

    def set_value(self, value):
        """In order of priority, value is a boolean, number, or string"""
        if isinstance(value, bool):
            self.value = value
        else:
            try:
                self.value = float(value)
            except:
                self.value = value

    def deserialize(self, elem):
        """Load from an xml element tree"""
        assert (elem.tag == "l" or elem.tag == "bool")

        if elem.tag == "l":
            option_node = elem.find("option")
            if option_node is not None:
                self.is_option = True
                self.set_value(option_node.text)
            else:
                self.set_value(elem.text)
        else:  # elem.tag == "bool":
            self.set_value(elem.text == "true")

    def serialize(self, **kwargs):
        """Save out as an element tree"""
        if isinstance(self.value, bool):
            literal = Element("bool")
            literal.text = self.as_string()
        else:
            literal = Element("l")
            if self.is_option:
                option = Element("option")
                option.text = str(self.value)
                literal.append(option)
            elif self.value is not None:
                if isinstance(self.value, float):
                    literal.text = number_to_string(self.value)
                else:
                    literal.text = str(self.value)
        return literal

    def __eq__(self, other):
        # Do both sides evaluate to numbers?
        try:
            return float(self.value) == float(other.value)
        except:
            pass
        # Return result of case-insensitive string comparison
        return self.as_string().upper() == other.as_string().upper()

    def __gt__(self, other):
        # Do both sides evaluate to numbers?
        try:
            return float(self.value) > float(other.value)
        except:
            pass
        # Return result of case-insensitive string comparison
        return self.as_string().upper() > other.as_string().upper()

    def __lt__(self, other):
        # Do both sides evaluate to numbers?
        try:
            return float(self.value) < float(other.value)
        except:
            pass
        # Return result of case-insensitive string comparison
        return self.as_string().upper() < other.as_string().upper()

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

    def __str__(self):
        return str(self.value)

    def evaluate(self, target, script):
        """Literals are already evaluated, but the caller doesn't know that"""
        return self

    # expose as different types
    def as_number(self):
        try:
            return float(self.value)
        except:
            return 0

    def as_number_if_number(self):
        """Returns a number if a number; None otherwise"""
        try:
            return float(self.value)
        except:
            return 0

    def as_string(self):
        if self.value is None:
            return ""
        if isinstance(self.value, float):
            return number_to_string(self.value)  # no trailing .0
        if isinstance(self.value, bool):
            return "true" if self.value else "false"  # all lowercase
        return str(self.value)

    def as_bool(self):
        return bool(self.value)

    # may need to add things like bool, nil, function, etc.


class Color(object):

    """Represents a color.

    Note: at the moment, we don't care about what it means
    We just want to be able to read it and write it back to the xml

    Sample XML: <color>200,200,200,1</color>

    We may potentially deal with this case, too, in the future:
    <someelem ... color="243,118,29" ... />
    """

    def __init__(self):
        self.color_string = None

    def deserialize(self, elem):
        "Load from an xml element tree"
        assert (elem.tag == "color")
        self.color_string = elem.text

    def serialize(self, **kwargs):
        "Save out as an element tree"
        color = Element("color")
        color.text = self.color_string
        return color

    def __eq__(self, other):
        return self.color_string == other.color_string

    def evaluate(self, target, script):
        """Colors are already evaluated, but the caller doesn't know that"""
        return self

    # expose as different types
    def as_number(self):
        return 0

    def as_number_if_number(self):
        return None

    def as_string(self):
        return self.color_string

    def as_bool(self):
        return False


class Comment(object):

    """This is a comment off to the side of a block.  Example XML:
    <block s="receiveGo">
        <comment w="90" collapsed="false">rear right rotor</comment>
    </block>
    at present, we do nothing with a comment except store it.
    """

    def __init__(self):
        self.comment_node = None

    def deserialize(self, elem):
        "Load from an xml element tree"
        assert (elem.tag == "comment")
        self.comment_node = elem

    def serialize(self, **kwargs):
        "Save out as an element tree"
        return self.comment_node


class List(object):

    """Represents a list.

    A sample list in xml might look like:

    <list id="73">
        <item><l>1</l></item>
        <item><l/></item>
        <item><l>three</l></item>
    </list>

    when used as the value of a variable, but like this:

    <block s="reportNewList">
        <list>
            <l>1</l>
            </l>
            <l>three</l>
        </list>
    </block>

    when created as a literal value.
    (We of course do not parse the 'block' part.)

    """

    def __init__(self):
        self.list = []
        self.id = None
        self.broken_into_items = False

    def deserialize(self, elem):
        """Load from an xml element tree"""
        assert (elem.tag == "list")
        self.id = elem.get("id")

        "Does this list use <item> tags?"
        if elem.find("item"):
            self.broken_into_items = True
            self.list = [factory.deserialize_value(item[0])
                         for item in elem]
        else:
            self.broken_into_items = False
            self.list = [factory.deserialize_value(item)
                         for item in elem]

    def serialize(self, **kwargs):
        """Save out as an element tree"""
        list_node = Element("list")
        if self.id is not None:
            list_node.set("id", self.id)

        for entry in self.list:
            datum_node = entry.serialize(**kwargs)
            if not self.broken_into_items:
                list_node.append(datum_node)
            else:
                item_node = Element("item")
                item_node.append(datum_node)
                list_node.append(item_node)

        return list_node

    def __eq__(self, other):
        # This should be adequate
        return self.list == other.list

        # def __repr__(self):

    # return "%s(%r, %r)" % (self.__class__.__name__, self.name,
    # self.contents)

    def __str__(self):
        return "%r" % (self.list, )

    def __len__(self):
        return len(self.list)

    def evaluate(self, target, script):
        """Lists are already evaluated, but the caller doesn't know that"""
        return self

    def as_number(self):
        return 0

    def as_number_if_number(self):
        return None

    def as_string(self):
        return "[a list]"  # to do

    def as_bool(self):
        return True  # seems to be how Snap! responds

    def index_in_range(self, index):
        return 0 <= index < len(self.list)

    def item_at_index(self, index):
        if self.index_in_range(index):
            return self.list[index]
        return None


class Variable(object):

    """Represents a value that changes over time.
    Contains something like a Literal, Bool, or List"""

    def __init__(self, name="No name", contents=None):
        self.contents = contents
        self.name = name

    def deserialize(self, elem):
        """Load from an xml element tree"""
        assert (elem.tag == "variable")
        self.name = elem.get("name")

        # We should have one child
        self.contents = None
        if len(elem) > 0:
            self.contents = factory.deserialize_value(elem[0])
            assert (self.contents is not None)

    def serialize(self, **kwargs):
        """Save out as an element tree"""
        variable = Element("variable", name=self.name)
        if self.contents is not None:
            variable.append(self.contents.serialize(**kwargs))
        return variable

    def __eq__(self, other):
        return self.name == other.name and self.contents == other.contents

    def __repr__(self):
        return "%s(%r, %r)" % (
            self.__class__.__name__, self.name, self.contents)

    def __str__(self):
        return "%r: %s" % (self.name, self.contents)

    def set(self, value):
        """Sets a variable.  Pass in a Literal or other object as a value"""
        self.contents = value

    # to do -- record if there has been a change

    def value(self):
        if self.contents is not None:
            return self.contents
        return Literal(None)

    def show(self, visible):
        # to do -- record if a variable is to be shown or hidden
        pass


class Variables(object):

    """This is a collection of 'Variable' objects,
    as used by the project, stage, and sprites"""

    def __init__(self, input=None):
        # ordered dict so we can serialize in the order we deserialized
        # (possibly doesn't really matter, but it helps with the unit tests)
        if input is None:
            self.variables = OrderedDict()
        else:
            self.variables = input

    def add(self, v):
        self.variables[v.name] = v

    def deserialize(self, elem):
        """Loads this class from an element tree representation"""
        assert (elem.tag == "variables")

        # Clear out all non-internal variables
        # self.variables.clear()
        for var_name in self.variables.keys():
            if not var_name.startswith("@"):
                del self.variables[var_name]

        # Read in all the variables
        for child_node in elem:
            v = Variable()
            v.deserialize(child_node)
            self.add(v)

    def serialize(self, **kwargs):
        """Return an elementtree representing this object"""
        variables = Element("variables")
        for variable in self.variables.values():
            # Do not serialize internal variables
            if not variable.name.startswith("@"):
                variables.append(variable.serialize(**kwargs))
        return variables

    def __eq__(self, other):
        return self.variables == other.variables

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.variables)

    def __str__(self):
        var_list = self.variables.values()
        return "{%s}" % ", ".join(str(var) for var in var_list)

    def get_variable(self, name):
        if name in self.variables:
            return self.variables[name]
        return None
