#!/usr/bin/env python

import os
import sys
import subprocess
import errno
import select
import pty
import time
import re

DEBUG=False
READ_BUFFSIZE=1024

def log(*args):
    if DEBUG:
        print "# ", args
    

def read_subprocess( p, sockets ):
    stdout = ''
    done = False

    ending_regexp = re.compile( '>$|\?\r\n$|The game is over\.\r\n$', re.MULTILINE )
    
    log( "read_subprocess" )
        
    while not done:
        log( "select" )
        fds = select.select([ masters[0], masters[1] ], [], [], 0)[0]
        log( "returned %d fds" % len(fds) )
        if len(fds) > 0:
            for fd in fds:
                try:
                    data = os.read(fd, 1024)
                    log( "read: %s" % data )
                    if len(data) > 0:
                        stdout += data
                except OSError as e:
                    done = True
                    if e.errno != errno.EIO:
                        raise
        time.sleep(.01)
        if p.poll():
            done = True
        
        if ending_regexp.search( stdout ):
            done = True

    if( stdout ):
        sys.stdout.write( stdout )
        sys.stdout.flush()
    return ( stdout )

def zorkshell_command_dispatch( command ):
    print "## zorkshell command \"%s\" not implemented." % command

# void main() 

if os.geteuid() == 0:
    sys.stderr.write("Don't run me as root.\n")
    os.exit(1)
command = 'zork'
masters, slaves = zip(pty.openpty(), pty.openpty())
p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=slaves[0], stderr=slaves[1])
for fd in slaves: os.close(fd)

zork_output = read_subprocess( p, masters )

done = False
while not done:

    game_over = re.compile( 'The game is over.\r\n$', re.MULTILINE )
    command_prefix = re.compile( '^\\\\' )
    
    if game_over.search( zork_output ):
        done = True
    else:
        input = sys.stdin.readline()

        if command_prefix.match( input ):
            zorkshell_command_dispatch( input.strip() )
        else:
            p.stdin.write( input )
            time.sleep( .01 )
            zork_output = read_subprocess( p, masters )

for fd in masters: os.close(fd)
p.wait()

    
