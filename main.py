
import array
import codestream
import environment
from statement import *


def main():
    env = environment.Environment()
    print "doing stuff"
    
    #my_array = array.array('B',[1,2,3,4, 5,6])
    #c = codestream.CodeStream(my_array)
    #print c.read_statement()
    
    #print Number(52.7)
    #fn = Function(0, 
                    #Function(1, Number(80), Number(31)),
                    #Function(2, Number(2), Number(4)));
    #print fn
    #print fn.evaluate(environment)
    
    #buf = array.array('B', '\0' * 50)
    #d = codestream.CodeStream()
    #d.write_statement(fn)
    #print d
    #print d.buffer
    
    #print fn.__repr__()
    #print fn
    
    
    f = Function(4, [Number(17)])
    
    a = Function(4, [Number(1)], None)
    r = Repeat(Number(3), f)
    b = Function(4, (Number(2),), next_block = None)
    ro = Repeat(Number(2), r)

    a.next_block = ro
    r.next_block = b
    
    env.run(a)
    

    

    
    print "a"
    print a.__repr__()
    
    env.run(eval(a.__repr__()))
     
    print "done"


main()


