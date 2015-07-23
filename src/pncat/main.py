"""
Usage:

pncat [OPTIONS] convert PATH_FROM [PATH_TO]


The OPTIONS placeholder corresponds to zero or more of the following options:

 --help, -h
   Shows this message.

 --no-asserts
   Disables defensive programming verifications.

 --from-format
   Input format

 --to-format
   Output format
"""

try :
    from util import *

    import os
    import sys
    import resource
    #import networkx
    import argparse

    import ptnet

except ImportError, e:
    error_missing_package (e)

if sys.version_info < (2, 7, 0) or sys.version_info >= (3, 0, 0) :
    print ("")
    print ("*** ERROR ***")
    print ("This tool relies on Python 2.7!!")
    print ("Install Python 2.7 or modify the first line of the file 'po-discovery.py' so that it calls Python 2.7")
    print ("")
    sys.exit (1)

class MyArgumentParser (argparse.ArgumentParser) :
    def format_help (self) :
        return __doc__
    def parse_args (self) :
        if len (sys.argv) == 1 :
            self.print_usage ()
            self.exit (1)
        return argparse.ArgumentParser.parse_args (self)

class Main :
    def __init__ (self) :
        self.args = None

    def parse_cmdline_args (self) :

        cmd_choices = [
                "convert",
                ]
        from_formats_choices = [
                "pnml",
                "ll_net",
                "pt1",
                ]
        to_formats_choices = [
                "pnml",
                "ll_net",
                "pt1",
                "dot",
                "prod",
                ]

        usage = "pncat [OPTION]... CMD PATH [PATHs]\n" + \
                "Try 'pncat --help' for more information."
        p = MyArgumentParser (prog="pncat", usage = usage)
        #g = p.add_mutually_exclusive_group ()
        #p.add_argument ("--log-fraction-truncate", type=float)
        p.add_argument ("--from-format", choices=from_formats_choices)
        p.add_argument ("--to-format", choices=to_formats_choices)
        p.add_argument ("--no-asserts", action="store_true")

        p.add_argument ('cmd', metavar="CMD", choices=cmd_choices)
        p.add_argument ('cmd_args', metavar="CMD_ARGS", nargs="*")

        self.args = p.parse_args ()
        print "pncat: args:", self.args

        if self.args.cmd == "convert" :
            if len (self.args.cmd_args) != 2 :
                p.error ("convert expects 2 arguments")
            if self.args.from_format is None :
                p.error ("convert expects --from-format to be set")
            if self.args.to_format is None :
                p.error ("convert expects --to-format to be set")
            self.args.from_path = self.args.cmd_args[0]
            self.args.to_path = self.args.cmd_args[1]
        else :
            raise AssertionError, "Internal error"

        output_dict (sys.stdout, self.args.__dict__, "pncat: args: ")

    def main (self) :
        self.parse_cmdline_args ()
        #sys.exit (0)

        if self.args.cmd == "convert" :
            self.cmd_convert ()
        else :
            raise AssertionError, "Internal error"

    def cmd_convert (self) :
        n = ptnet.load_net (self.args.from_path, self.args.from_format, \
                "pncat: ")
        ptnet.save_net (self.args.to_path, n, self.args.to_format, \
                "pncat: ")

