# common.py
# common routines for zorkshell

import sys
import re

__all__ = [ 'log', 'debug', 'command_prefix', 
            'register_zorkshell_command', 'zorkshell_command_dispatch',
            'register_zorkshell_module',
            'run_zork_output_processors' ]

__zorkshell_commands = {}
__zorkshell_modules  = {}

command_prefix = re.compile( '^/.*' )

DEBUG=False

def debug(*args):
    if DEBUG:
        sys.stdout.write( "[DEBUG %s]\n" % ' '.join(args) )

def log(*args):
    sys.stdout.write( "[LOG   %s]\n" % ' '.join(args) )

def register_zorkshell_command( command, handler ):
    if not command_prefix.match( command ):
        log( "Warning:  register_zorkshell_command: %s doesn't start with the command prefix and won't be executed" % command )
    
    if __zorkshell_commands.has_key( command ):
        raise "Already registered zorkshell command %s" % command
    else:
        debug( "registering handler for %s" % command )
        __zorkshell_commands[command.lower()] = handler


def zorkshell_command_dispatch( commandline, subprocess ):
    args = commandline.split()
    command = args.pop(0).lower()

    if not __zorkshell_commands.has_key( command ):
        log( "ERROR: no command registered for %s" % command )
    else:
        __zorkshell_commands[command]( subprocess, args )

def register_zorkshell_module( name, module ):
    if __zorkshell_modules.has_key( name ):
        raise "Already registered zork module %s" % name
    else:
        log( "Registering module: %s" % name )
        __zorkshell_modules[name] = module

def run_zork_output_processors( text ):
    k = __zorkshell_modules.keys()
    k.sort()
    for name in k:
        __zorkshell_modules[name].output_processor( text )
    

