
#import struct
#import array

#import codestream


class Statement(object):
    "A statement is a one or more pieces of data or code, and the base class for such"

    def __init__(self, next_block = None):
        self.next_block = next_block

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.repr_next(""))
    
    def repr_next(self, prepend=", "):
        if self.next_block:
            return "%snext_block = %s" % (prepend, self.next_block.__repr__())
        return ""
    
    def evaluate(self, environment):
        """Perform necessary steps to reduce this to a single data type.
        For example, if it is an addition function, add the inputs and return a number"""
        return self
    
    def next_statement(self, environment):
        """Which statement should be run next? 
        Default: The following in code.
        Branching/looping constructs may override."""
        return self.next_block
    
    def as_number(self):
        return 0
    
    def as_bool(self):
        return false
    
    def as_string(self):
        return ""
    
    def read_from_stream(self, stream):
        pass
    
    def write_to_stream(self, stream):
        pass

class Nil(Statement):
    "A value that indicates no value"
    
    def read_from_stream(self, stream):
        # Nil statement requires no additional information
        pass

    # as_number, as_bool, and as_string are as in the base class

class Number(Statement):
    "A value that indicates no value"

    def __init__(self, value = 0, next_block = None):
        self.value = value
        super(self.__class__, self).__init__(next_block)

    def __str__(self):
        return "#" + str(self.value)

    def __repr__(self):
        return "%s(%f%s)" % (self.__class__.__name__, self.value, self.repr_next())

    def read_from_stream(self, stream):
        self.value = stream.read_float()

    def as_number(self):
        return self.value;
    
    def as_bool(self):
        return self.value != 0.0;
    
    def as_string(self):
        return str(self.value);

    def read_from_stream(self, stream):
        self.value = stream.read_float()
    
    def write_to_stream(self, stream):
        stream.write_float(self.value)

def print_hack(x):
    print "Value is %s" % x
    return Nil()
    

class Function(Statement):
    "A statement that represents a function"

    operations = {
        0: ["+", lambda x, y: Number(x.as_number() + y.as_number())], 
        1: ["-", lambda x, y: Number(x.as_number() - y.as_number())], 
        2: ["*", lambda x, y: Number(x.as_number() * y.as_number())], 
        3: ["/", lambda x, y: Number(x.as_number() / y.as_number())],
        4: ["print", print_hack]
    }

    def __init__(self, opcode=None, args=[], next_block=None):
        self.opcode = opcode
        self.args = args
        assert len(self.args) > 0   # Make sure we were provided with an array of some sort
        super(self.__class__, self).__init__(next_block)

    def __str__(self):
        if self.opcode in Function.operations:
            op = Function.operations[self.opcode][0]
            if len(self.args) == 2:
                return "(%s %s %s)" % (self.args[0], op, self.args[1])
            else:
                return "(%s %s)" % (op, ", ".join(self.args))
        return "op%d %s" % (self.opcode, self.args)

    def __repr__(self):
        return "%s(%d, [%s]%s)" % (self.__class__.__name__, self.opcode, 
                               ", ".join(arg.__repr__() for arg in self.args),
                               self.repr_next())
                          
    def evaluate(self, environment):
        op = Function.operations[self.opcode][1]
        evaluated_args = [arg.evaluate(environment) for arg in self.args]
        return op(*evaluated_args)

    def read_from_stream(self, stream):
        count = stream.read_byte()
        self.args = []
        for i in range(count):
            self.args.append(stream.read_statement())
    
    def write_to_stream(self, stream):
        stream.write_byte(len(self.args))
        for arg in self.args:
            stream.write_statement(arg)


class Repeat(Statement):
    "Repeats the enclosed blocks a specified number of times"
    
    def __init__(self, repeat_arg = None, inner_block = None, next_block = None):
        self.repeat_arg = repeat_arg    # statement telling us how many times to repeat
        self.repeat_count = 0
        self.inner_block = inner_block
        super(self.__class__, self).__init__(next_block)
        
    def __str__(self):
        return "Repeat (%s) { %s }" % (self.repeat_count, self.inner_block)
    
    def __repr__(self):
        return "%s(%s, %s%s)" % \
               (self.__class__.__name__,
                self.repeat_arg.__repr__(), 
                self.inner_block.__repr__(),
                self.repr_next())
        
    def evaluate(self, environment):
        if not environment.am_on_top_of_stack(self):
            # We are just starting a series of repetitions
            self.repeat_count = self.repeat_arg.evaluate(environment).as_number()
            environment.push_on_stack(self)

        self.repeat_count -= 1
        if self.repeat_count < 0:
            environment.pop_off_stack(self)

    def next_statement(self, environment):
        "If the repeat is active, the next block is our inner block."
        if environment.am_on_top_of_stack(self):
            return self.inner_block
        return self.next_block

class IfThenElse(Statement):
    "Represents 'if (condition) then do true_block else do false_block'"
    def __init__(self, condition = None, 
                 true_block = None, false_block = None, next_block = None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
        self.result = None
        super(self.__class__, self).__init__(next_block)
        
    def __str__(self):
        return "if %s then { %s } else { %s }" % \
               (self.condition, self.true_block, self.false_block)
    
    def __repr__(self):
        return "%s(%s, %s, %s%s)" % \
               (self.__class__.__name__,
                self.condition.__repr__(), 
                self.true_block.__repr__(), 
                self.false_block.__repr__(),
                self.repr_next())

    def evaluate(self, environment):
        if not environment.am_on_top_of_stack(self):
            # First time into if statement
            self.result = self.condition.evaluate(environment).as_bool()
            print self.result
            environment.push_on_stack(self)
        else:
            # Inner execution finished, and we are called again
            self.result = None
            environment.pop_off_stack(self)

    def next_statement(self, environment):
        if self.result == None:
            return self.next_block
        if self.result == True:
            return self.true_block
        return self.false_block

class Variable(Statement):

    # The operations are:
    #   code 1: read (get) the variable
    #   code 2: write (set) the variable
    #   code 3: change (increment) the variable
    
    def __init__(self, id, opcode, value=None, next_block=None):
        """A statement representing a variable or variable operation
        
        :param id: an integer representing the variable. (Think 'var1', 'var2', 'var3')
        :type id: a number
        :param opcode: which operation we are performing (1 = get, 2 = set, 3 = increment)
        :type opcode: a number
        :param value: 
            For 'get' - None (as it is unused)
            For 'set' - the value we are setting the variable to
            For 'increment' - how much we are incrementing the variable by
        :type value: a Statement.  (It is an expression evaluated each time the code is run)
        :param next_block: the block that follows this one, or None
        :type next_block: a Statement
        """        
        self.id = id
        self.opcode = opcode
        self.value = value
        super(self.__class__, self).__init__(next_block)
        
    def name(self):
        "Returns the variable's name"
        return "var%d" % id
        
    def __str__(self):
        if self.opcode == 1:
            return "(%s)" % self.name()
        if self.opcode == 2:
            return "%s = %s" % (self.name(), self.value)
        if self.opcode == 3:
            return "%s += %s" % (self.name(), self.value)

    def __repr__(self):
        return "%s(%d, %d, %s%s)" % (self.__class__.__name__, self.id, 
                                     self.opcode, self.value.__repr__(),
                                     self.repr_next())

    def read_from_stream(self, stream):
        # We need to read our id, opcode, and value
        self.id = stream.read_short()
        self.opcode = stream.read_byte()
        self.value = stream.read_statement()
    
    def write_to_stream(self, stream):
        # Write our id, opcode, and value
        stream.write_short(self.id)
        stream.write_byte(self.opcode)
        stream.write_statement(self.value)
        
    def evaluate(self, environment):
        if self.opcode == 1:
            return self.get(environment)
        if self.opcode == 2:
            return self.set(environment, self.value.evaluate(environment))
        if self.opcode == 3:
            return self.increment(environment)

    def get(self, env):
        result = env.get_variable(self.id)
        if result is not None:
            return result
        return Nil()
        
    def set(self, env, final_value):
        env.set_variable(self.id, final_value)
        return Nil()
    
    def increment(self, env):
        self.set(env, Number(self.get(env).as_number() + 
                             self.value.evaluate(env).as_number()))
        return Nil()