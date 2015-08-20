#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import os

from .. import available_transform
from ..transformation import transform_compressed_clauses,StopClauses
from . import dimacs2compressed_clauses


__docstring__ =\
"""Utilities to apply to a dimacs CNF file, a transformation which
increase the hardness of the formula

Accept a cnf in dimacs format in input

Copyright (C) 2013, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

import sys

# Python 2.6 does not have argparse library
try:
    import argparse
    from argparse import RawDescriptionHelpFormatter
except ImportError:
    print("Sorry: %s requires `argparse` library, which is missing.\n"%__progname__,file=sys.stderr)
    print("Either use Python 2.7 or install it from one of the following URLs:",file=sys.stderr)
    print(" * http://pypi.python.org/pypi/argparse",file=sys.stderr)
    print(" * http://code.google.com/p/argparse",file=sys.stderr)
    print("",file=sys.stderr)
    exit(-1)



def setup_command_line(parser):
    """Setup general command line options

    Arguments:
    - `parser`: parser to fill with options
    """
    parser.add_argument('transformation',
                        metavar="<method>",
                        choices=available_transform().keys(),
                        default='none',
                        help="""
                        Transformation method the CNF formula to make it harder.
                        """)

    parser.add_argument('hardness',
                        metavar="<hardness>",
                        nargs='?',
                        type=int,
                        default=None,
                        help="""
                        Hardness parameter for the transformation procedure.
                        """)

    parser.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The input formula is read as a dimacs CNF file file instead of
                        standard input. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)

    parser.add_argument('--output','-o',
                        type=argparse.FileType('wb',0),
                        metavar="<output>",
                        default='-',
                        help="""Output file. The formula is saved
                        on file instead of being sent to standard
                        output. Setting '<output>' to '-' is another
                        way to send the formula to standard output.
                        (default: -)
                        """)

    parser.add_argument('--noheader', '-n',action='store_false',dest='header',
                        help="""Do not output the preamble, so that formula generation is faster (one
                        pass on the data).""")


### Produce the dimacs output from the data
def dimacstransform(inputfile, method, rank, output, header=True):

    # Generate the basic formula
    if header:
        
        from cStringIO import StringIO
        output_cache=StringIO()

    else:
        output_cache=output

    o_header,_,o_clauses = dimacs2compressed_clauses(inputfile)

    cls_iter=transform_compressed_clauses(o_clauses,method,rank)

    try:

        while True:
            cls = cls_iter.next()
            print(" ".join([str(l) for l in cls])+" 0",file=output_cache)
            
    except StopClauses as cnfinfo:

        if header:
            # clauses cached in memory
            print("c Formula transformed with method '{}' or rank {}\nc".format(method,rank),
                  file=output)
            print("\n".join(("c "+line).rstrip() for line in o_header.split('\n')[:-1]),
                  file=output)
            print("p cnf {} {}".format(cnfinfo.variables,cnfinfo.clauses),
                  file=output)
            output.write(output_cache.getvalue())

        else:
            # clauses have been already sent to output
            pass    
        return cnfinfo

###
### Register signals
###
import signal
def signal_handler(insignal, frame):
    assert(insignal!=None)
    assert(frame!=None)
    print('Program interrupted',file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

###
### Main program
###
def command_line_utility(argv=sys.argv):

    # Parse the command line arguments
    help_epilogue = "Available transformations:\n\n" + \
                    "\n".join("  {}\t:  {}".format(k,entry[0])
                              for k,entry in available_transform().iteritems()) 
    

    parser=argparse.ArgumentParser(prog   = os.path.basename(argv[0]),
                                   epilog = help_epilogue ,
                                   formatter_class = RawDescriptionHelpFormatter)


    setup_command_line(parser)

    # Process the options
    args=parser.parse_args(argv[1:])

    dimacstransform(args.input,
                    args.transformation,
                    args.hardness,
                    args.output,
                    args.header)

### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
