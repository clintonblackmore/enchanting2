import array
import struct

import statement_id_map

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
        type_class = statement_id_map.statement_class_from_id(type_id)
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
        type_id = statement_id_map.id_from_statement_class(type_class)
        self.write_byte(type_id)
        statement.write_to_stream(self)
        

