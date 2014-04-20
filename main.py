
import array
import codestream
from statement import *


def main():
    print "doing stuff"
    my_array = array.array('B',[1,2,3,4, 5,6])
    c = codestream.CodeStream(my_array)
    print c.read_statement()
    
    print Number(52.7)
    fn = Function(0, 
                    Function(1, Number(80), Number(31)),
                    Function(2, Number(2), Number(4)));
    print fn
    print fn.evaluate()
    
    buf = array.array('B', '\0' * 50)
    d = codestream.CodeStream()
    d.write_statement(fn)
    print d
    print d.buffer
    
    print fn.__repr__()
    print fn


main()


