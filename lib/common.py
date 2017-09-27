# common.py
# common routines for zorkshell

__zorkshell_commands = {}

def register_zorkshell_command( command, handler ):
    if __zorkshell_commands.has_key( command ):
        raise "Already registered zorkshell command %s" % command
    else:
        __zorkshell_commands[command.lower()] = handler


def zorkshell_command_dispatch( commandline, subprocess ):

    args = commandline.split()
    command = args.pop(0).lower()

    if not __zorkshell_commands.has_key( command ):
        subprocess.stdin.write( "# no command registered for \\%s" % command )
    else:
        __zorkshell_commands[command]( subprocess, args )
    

