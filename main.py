
import array
import codestream
import environment
from statement import *


def main():
    env = environment.Environment()
    print "doing stuff"

   # env.run(IfThenElse(condition=Number(3), true_block=Function(4, [Number(1)]), false_block=Function(4, [Number(2)]), 
    #                   next_block=None) )       


    env.run(Variable(1, 2, Number(47), next_block=Repeat(Number(10), Variable(1, 3, Number(10)),next_block=Function(4,[Variable(1,1)]))))

    print "Done again"
main()


