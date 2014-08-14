"""exec.py contains items that execute code.  To wit:

 block - a block is an executable statement
 script - a collection of blocks to execute
 block-definition - defines a user-created block
 blocks - a collection of block definitions
"""

import pdb

from xml.etree.cElementTree import Element

import gevent

import data
import factory
import ops


def terse_debug_id(obj):
    """Returns a terse ID for the object for debugging purposes"""
    return hex(id(obj)).upper()[-5:-1]


def debug_name_for_object(obj):
    if obj.__class__.__name__ == "Script":
        return obj.debug_name()
    else:
        return "~%s<%s>" % (obj.__class__.__name__, terse_debug_id(obj))


class BlockType(object):

    """A simple enum to represent the type of a block"""
    unknown, regular, custom = range(0, 3)
    name_list = ["", "block", "custom-block"]

    @staticmethod
    def block_type_from_name(name):
        return BlockType.name_list.index(name)

    @staticmethod
    def block_type_name_from_value(value):
        return BlockType.name_list[value]


class Block(object):

    """This is a code block, representing an instruction to execute"""

    def __init__(self):
        self.function = None  # used to actually call the function
        self.function_name = ""  # the original, textual name of the function
        self.arguments = []
        self.var_name = None  # only set if this is a 'var' block
        self.type = BlockType.unknown

    def deserialize(self, elem):
        """Load from an xml element tree"""

        # What kind of block are we?
        self.type = BlockType.block_type_from_name(elem.tag)
        assert (self.type != BlockType.unknown)

        # Get the function name and look up the function
        self.function_name = elem.get("s")
        if self.function_name is None:
            # there is no function name; this must be a var block
            self.var_name = elem.get("var")
            self.function_name = "var"
        if self.type == BlockType.regular:
            self.function = ops.bind_to_function(self.function_name)
        else:
            # Custom functions are defined after they are used in the XML
            self.function = None

        self.arguments = [factory.deserialize_value(child)
                          for child in elem]

    def serialize(self):
        """Save out as an element tree"""
        if self.var_name is None:
            # this is a standard block, not a variable block
            block = Element(
                BlockType.block_type_name_from_value(self.type),
                s=self.function_name)
        else:
            # this is a var block (note: not a 'custom-block')
            block = Element("block", var=self.var_name)
        for arg in self.arguments:
            block.append(arg.serialize())
        return block

    def is_hat_block(self):
        """Is this a hat-shaped, script-triggering block?"""
        # appropriate function names include receiveGo, receiveKey,
        # receiveBroadcast
        return self.type is BlockType.regular and \
            self.function_name.startswith("receive")

    def evaluate(self, target, script):
        # evaluate each of the arguments
        if self.var_name is None:
            args = []
            args = [arg.evaluate(target, script) for arg in self.arguments
                    if not isinstance(arg, data.Comment)]
            # if not isinstance(arg, (data.Comment, Script))]
        else:
            args = self.var_name

        if self.function is None and self.type is BlockType.custom:
            # The definitions have been loaded -- what is this function?
            bd = target.find_block_definition(self.function_name)
            if bd is not None:
                self.function = bd.run

        # now, run this function
        if self.function is not None:
            result = self.function(target, script, args)
        else:
            print "Unknown function: %s" % self.function_name
            pdb.set_trace()
            result = data.Literal(None)

        # to do -- save args and result with timestamp

        return result

    def __repr__(self):
        # Shows state; can't reconstruct from this info
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        return "%s(%s)" % (
            self.function_name, ", ".join([str(s) for s in self.arguments]))


class Script(object):

    "Represents a sequence of instructions"

    def __init__(self):
        # Only top-level scripts contain x and y values
        self.x = None
        self.y = None
        self.blocks = []
        self.parent_script = None
        self.from_start()

    def from_start(self):
        """Sets or re-sets the script to begin and the start"""
        self.code_pos = 0
        self.subscript = None  # set by flow control blocks
        self.repeat = 0  # adjusted by flow control blocks
        self.stopped = False
        self.variables = data.Variables()
        return self

    def parallel_copy(self):
        """Clone script -- keep code, but create new flow control information

        Especially for custom blocks (or worse, recursive blocks!), the same
        script may run more than once concurrently. It needs to have its own
        equivalent to a call stack and heap, but the code itself remains the
        same.  To achieve that end, we point at the existing list of blocks,
        but we create a new copy of the code position, etc."""
        clone = Script()
        clone.blocks = self.blocks
        clone.x, clone.y = self.x, self.y
        clone.parent_script = self.parent_script
        clone.from_start()
        return clone

    def deserialize(self, elem):
        """Loads this class from an element tree representation"""
        assert (elem.tag == "script")

        # attributes
        self.x = elem.get("x")
        self.y = elem.get("y")

        self.from_start()

        # our children are a sequence of blocks or custom blocks
        self.blocks = []
        for block in elem:
            b = Block()
            b.deserialize(block)
            self.blocks.append(b)

    def serialize(self):
        """Return an elementtree representing this object"""

        # We have sprite objects and watcher nodes; make a tree of nodes
        if self.x is None or self.y is None:
            script = Element("script")
        else:
            script = Element("script", x=self.x, y=self.y)

        for block in self.blocks:
            script.append(block.serialize())

        return script

    def top_block(self):
        """Returns the first block in the script
        (which may be used to trigger the script)"""
        if self.blocks and len(self.blocks) > 0:
            return self.blocks[0]
        return None

    def step(self, target):
        """Execute a line of code; raises StopIteration
        when there is no more code"""

        # Are we inside a nested script?
        if self.subscript:
            # step the script until it is done
            try:
                # print "(sub) ",
                self.subscript.step(target)
            except StopIteration as e:
                # print "(exit)"
                self.subscript = None
                result = e.args[0]
                if result is not None:
                    raise e
        else:
            if self.code_pos < len(self.blocks):
                current_block = self.blocks[self.code_pos]
            else:
                raise StopIteration(None)

            # print "%s: %s" % (debug_name_for_object(self), current_block)
            current_block.evaluate(target, self)
            # print "(repeat %s)" % self.repeat
            if not self.repeat:
                self.code_pos += 1

    def evaluate(self, target, script):
        """Scripts (in arguments) evaluate to themselves.
        [They can be run separately]"""
        return self

    def run(self, target):
        """Runs the code until it is done (if it ever finishes)"""
        self.stopped = False
        try:
            while not self.stopped:
                self.step(target)
                gevent.sleep(0.01)
        except StopIteration as e:
            # The StopIteration's parameter is the return value
            # It is typically None, but if a 'report' block
            # was used, we'll have a value
            result = e.args[0]
            return result

    def stop(self):
        "Call this to stop a script (such as when the stop sign is pressed)"
        self.stopped = True

    def activate_subscript(self, subscript):
        """Lets you run a nested script (like a 'repeat' or 'if' block)"""
        self.subscript = subscript.parallel_copy()
        self.subscript.parent_script = self

    def starts_on_trigger(self):
        """After the script runs, should it be queued up
        to be triggered again?"""
        tb = self.top_block()
        if tb:
            return tb.is_hat_block()
        return False

    def __str__(self):
        return "Script <%s>" % ", ".join([str(s) for s in self.blocks])

    def debug_name(self):
        """Outputs a name for this object, suitable for debugging"""
        self_and_parents = []
        script = self
        while script:
            part_name = terse_debug_id(script)
            self_and_parents.append(part_name)
            script = script.parent_script

            assert(len(self_and_parents) < 500)  # infinite loop

        self_and_parents.reverse()
        return "Script<%s>" % ".".join(self_and_parents)

    # Code that deals with variables
    def get_variable(self, actor, name):
        """Returns the named variable or None.
        Searched script variables, sprite variables,
        and then project variables in turn."""

        script = self
        while script:
            ret = script.variables.get_variable(name)
            if ret:
                return ret
            script = script.parent_script

        ret = actor.variables.get_variable(name)
        if ret:
            return ret

        ret = actor.project.variables.get_variable(name)
        if ret:
            return ret

        return None

    def owner_of_variable(self, actor, name):
        """Debugging; returns who owns variable instead of var itself"""

        script = self
        while script:
            ret = script.variables.get_variable(name)
            if ret:
                return script
            script = script.parent_script

        ret = actor.variables.get_variable(name)
        if ret:
            return actor

        ret = actor.project.variables.get_variable(name)
        if ret:
            return actor.project

        return None

    def full_debug_name_of_variable(self, actor, var_name):
        owner = self.owner_of_variable(actor, var_name)
        return "%s.%s" % (debug_name_for_object(owner), var_name)

    def value_of_variable(self, actor, name):
        v = self.get_variable(actor, name)
        if v:
            result = v.value()
            if result:
                return result
        return data.Literal(None)

    def set_variable(self, actor, name, value):
        v = self.get_variable(actor, name)
        if v:
            # print "%s -> %s" % (
            #    self.full_debug_name_of_variable(actor, name), value)
            v.set(value)
        return None

    def increment_variable(self, actor, name, increment):
        v = self.get_variable(actor, name)
        if v:
            v.set(data.Literal(v.value().as_number() + increment))
        return None

    def show_variable(self, actor, name, visible):
        # Not actually implemented
        v = self.get_variable(actor, name)
        if v:
            v.show(True)
        return None


class BlockDefinition(object):

    """This is a definition of a custom block.

    A sample block definition in XML might look like:

    <block-definition s="sum of %'alpha' and %'beta'"
                      type="reporter" category="looks">
        <inputs>
            <input type="%s"/>
            <input type="%s"/>
        </inputs>
        <script>
            <block s="doReport">
                <block s="reportSum">
                    <block var="alpha"/>
                    <block var="beta"/>
                </block>
            </block>
        </script>
    </block-definition>

    and would be called by a block like:

    <custom-block s="sum of %s and %s">
        <l>12</l>
        <l>47</l>
    </custom-block>

    """

    def __init__(self):

        # Note: Say we have a block called "sum of alpha and beta"
        # (which just adds alpha to beta and returns the result)
        # The custom block that calls it will have a function name of:
        # "sum of %s and %s", yet this block will have a specification of
        # "sum of %'alpha' and %'beta'"

        # Properties

        # Which category does this block belong in? ("lists", "control", etc)
        self.category = None
        # What is the function's specification? (See note for __init__())
        self.specification = None
        # What type is this block? "reporter", "command", or "predicate"?
        self.type = None

        # Child elements
        # 'header' and 'code' are empty in all the examples I've looked at
        self.header = None
        self.code = None
        self.input_types = []
        self.script = Script()
        self.extra_scripts = None   # left-over blocks, not a part of the fn

        # Psuedo Properties
        # (These are calculated from values in the XML)
        self.parameter_names = []  # ex. ["alpha", "beta"]
        self.function_name = ""    # ex. "sum of %s and %s"

    def deserialize_inputs(self, input_node):
        """Takes an XML node with inputs and stores what matters in a list"""
        assert(input_node.tag == "inputs")
        self.input_types = []
        for child in input_node:
            self.input_types.append(child.get("type"))

    def serialize_inputs(self):
        """Takes our input type data and turns it back into an XML tree"""
        inputs = Element("inputs")
        for item in self.input_types:
            inputs.append(Element("input", type=item))
        return inputs

    def determine_names(self):
        """Determines function name and parameter names.

        Example Input:
          self.specification = "sum of %'alpha' and %'beta'"
          self.input_types = ["%s", "%s"]

        Example Output:
          self.parameter_names = ["alpha", "beta"]
          self.function_name = "sum of %s and %s"

        """

        # Note: variable names can contain spaces
        # ex. <block-definition s="foo %'long name input'" ...>
        # OTOH, it doesn't seem to be legal to have a ' in the function name
        # but I was able to put them into variable names.

        # For now, we will declare single quotes in variable names to be
        # illegal, as it will make the present implementation much simpler.

        tokens = self.specification.split("'")
        function_name_list = []
        self.parameter_names = []
        for index, token in enumerate(tokens):
            # [(0, 'sum of %'), (1, 'alpha'), (2, ' and %'),
            #  (3, 'beta'), (4, '')]
            if index % 2 == 0:
                # even entries go into the new list for the function name
                function_name_list.append(token)
            else:
                # odd entries are input names
                self.parameter_names.append(token)
                # and the function name gets the input type for this slot
                # without the redundant '%' symbol
                specifier = self.input_types[index // 2]
                function_name_list.append(specifier[1:])

        self.function_name = "".join(function_name_list)

    def deserialize(self, elem):
        """Load from an xml element tree"""
        assert (elem.tag == "block-definition")

        # Properties
        self.specification = elem.get("s")
        self.category = elem.get("category")
        self.type = elem.get("type")

        # Children
        self.header = elem.find("header")
        self.code = elem.find("code")
        self.deserialize_inputs(elem.find("inputs"))
        self.script.deserialize(elem.find("script"))
        self.extra_scripts = elem.find("scripts")
        self.determine_names()

    def serialize(self):
        """Save out as an element tree"""
        definition = Element("block-definition",
                             s=self.specification,
                             category=self.category,
                             type=self.type)

        for child in (self.header, self.code,
                      self.serialize_inputs(), self.script.serialize(),
                      self.extra_scripts):
            if child is not None:
                definition.append(child)

        return definition

    def run(self, target, parent_script, params):
        """Runs the defined block, and returns a value afterwards"""

        script = self.script.parallel_copy()
        script.parent_script = parent_script
        # set input parameters
        for index, parameter in enumerate(params):
            name = self.parameter_names[index]
            script.variables.add(data.Variable(name, parameter))
        # initial_vars = str(script.variables)
        result = script.run(target)
        # print "Done %s: %s (%s) -> %s (%s)" % (debug_name_for_object(script),
        #                                  self.function_name, initial_vars,
        #                                  result, script.variables)
        return result


class Blocks(object):

    """A list of block definitions"""

    def __init__(self):
        self.definitions = []

    def deserialize(self, elem):
        """Load from an xml element tree"""
        assert (elem.tag == "blocks")
        for child in elem:
            self.definitions.append(factory.deserialize_value(child))

    def serialize(self):
        """Save out as an element tree"""
        blocks_node = Element("blocks")
        for definition in self.definitions:
            blocks_node.append(definition.serialize())
        return blocks_node

    def find_block_definition(self, function_name):
        for definition in self.definitions:
            if definition.function_name == function_name:
                return definition
        return None

#
#    def get_custom_block(self, function_name):
#        """Do we have a block definition for this block?"""

#        block_definition = self.find_block_definition(function_name)
#        if block_definition is not None:
# return block_definition.script.parallel_copy()  # need to return a function!
#        return None
