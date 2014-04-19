
import struct
import array




class CodeStream:
    "A stream of data representing code that the execution engine runs."
    
    def __init__(self, buffer = 0):
        if buffer != 0:
            self.buffer = buffer
        else:
            self.buffer = array.array("B")
        self.offset = 0
        
    def read_formatted_data(self, fmt):
        offset = self.offset
        self.offset += struct.calcsize(fmt)
        return struct.unpack_from(fmt, self.buffer, offset)

    def read_byte(self):
        return self.read_formatted_data("!B")[0]        
        
    def read_short(self):
        return self.read_formatted_data("!H")[0]

    def read_bool(self):
        return self.read_formatted_data("!?")[0]
        
    def read_float(self):
        return self.read_formatted_data("!f")[0]
        
    def read_statement(self):
        type_id = self.read_byte()
        type_class = statement_type[type_id]
        new_statement = type_class()
        new_statement.read_from_stream(self)
        return new_statement
   

    def write_formatted_data(self, fmt, *args):
        offset = self.offset
        self.offset += struct.calcsize(fmt)
        #struct.pack_into(fmt, self.buffer, offset, *args)
        self.buffer.fromstring(struct.pack(fmt, *args))

    def write_byte(self, value):
        self.write_formatted_data("!B", value);       
        
    def write_short(self, value):
        self.write_formatted_data("!H", value);       

    def write_bool(self, value):
        self.write_formatted_data("!?", value); 
        
    def write_float(self, value):
        self.write_formatted_data("!f", value);       
        
    def write_statement(self, statement):
        type_class = statement.__class__
        type_id = id_from_statement[type_class]
        self.write_byte(type_id)
        statement.write_to_stream(self)
        

class Statement:
    "A statement is a one or more pieces of data or code, and the base class for such"

    def __repr__(self):
        return "%s()" % (self.__class__.__name__)
    
    def evaluate(self):
        """Perform necessary steps to reduce this to a single data type.
        For example, if it is an addition function, add the inputs and return a number"""
        return self;
    
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

    def __repr__(self):
        return 'Nil' 
    
    def read_from_stream(self, stream):
        # Nil statement requires no additional information
        pass

    # as_number, as_bool, and as_string are as in the base class

class Number(Statement):
    "A value that indicates no value"

    def __init__(self, value = 0):
        self.value = value

    def __str__(self):
        return "#" + str(self.value)

    def __repr__(self):
        return "%s(%f)" % (self.__class__.__name__, self.value)

    def read_from_stream(self, stream):
        self.value = stream.read_float()

    def as_number(self):
        return self.value;
    
    def as_bool(self):
        return self.value == 0.0;
    
    def as_string(self):
        return str(self.value);

    def read_from_stream(self, stream):
        self.value = stream.read_float()
    
    def write_to_stream(self, stream):
        stream.write_float(self.value)

class Function(Statement):
    "A statement that represents a function"

    operations = {
        0: ["+", lambda x, y: x + y], 
        1: ["-", lambda x, y: x - y], 
        2: ["*", lambda x, y: x * y], 
        3: ["/", lambda x, y: x / y]
    }

    def __init__(self, opcode=None, *args):
        self.opcode = opcode
        self.args = args

    def __str__(self):
        if self.opcode in Function.operations:
            op = Function.operations[self.opcode][0]
            return "(%s %s %s)" % (self.args[0], op, self.args[1])
        return "op%d %s" % (self.opcode, self.args)

    def __repr__(self):
        return "%s(%d, %s)" % (self.__class__.__name__, self.opcode, 
                               ", ".join(arg.__repr__() for arg in self.args))
                          
    def evaluate(self):
        op = Function.operations[self.opcode][1]
        arg_values = [arg.evaluate().as_number() for arg in self.args]
        return Number(op(*arg_values))

    def read_from_stream(self, stream):
        count = stream.read_byte()
        self.args = []
        for i in range(count):
            self.args.append(stream.read_statement())
    
    def write_to_stream(self, stream):
        stream.write_byte(len(self.args))
        for arg in self.args:
            stream.write_statement(arg)

statement_type = {0 : Nil, 1 : Number, 2 : Function}
id_from_statement = {}
for key, value in statement_type.iteritems():
    id_from_statement[value] = key

print "doing stuff"
my_array = array.array('B',[1,2,3,4, 5,6])
c = CodeStream(my_array)
print c.read_statement()

print Number(52.7)
fn = Function(0, 
                Function(1, Number(80), Number(31)),
                Function(2, Number(2), Number(4)));
print fn
print fn.evaluate()

buf = array.array('B', '\0' * 50)
d = CodeStream()
d.write_statement(fn)
print d
print d.buffer

print fn.__repr__()
print fn