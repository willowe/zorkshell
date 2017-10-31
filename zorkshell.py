#!/usr/bin/env python

import os
import sys
import subprocess
import errno
import select
import pty
import time
import re

from lib.common import *
import modules.echo
import modules.save

READ_BUFFSIZE=1024

def read_subprocess( p, sockets ):
    stdout = ''
    done = False

    ending_regexp = re.compile( '>$|\?\r\n$|The game is over\.\r\n$', re.MULTILINE )
    
    debug( "read_subprocess" )
        
    while not done:
        debug( "select" )
        fds = select.select([ masters[0], masters[1] ], [], [], 0)[0]
        debug( "returned %d fds" % len(fds) )
        if len(fds) > 0:
            for fd in fds:
                try:
                    data = os.read(fd, 1024)
                    debug( "read: %s" % data )
                    if len(data) > 0:
                        stdout += data
                        sys.stdout.write( data )
                        sys.stdout.flush()
                except OSError as e:
                    done = True
                    if e.errno != errno.EIO:
                        raise
        time.sleep(.01)
        if p.poll():
            done = True
        
        if ending_regexp.search( stdout ):
            done = True

#    if( stdout ):
#        sys.stdout.write( stdout )
#        sys.stdout.flush()
    return ( stdout )

# void main() 

if os.geteuid() == 0:
    sys.stderr.write("Don't run me as root.\n")
    os.exit(1)
    
masters, slaves = zip(pty.openpty(), pty.openpty())
p = subprocess.Popen('zork', stdin=subprocess.PIPE, stdout=slaves[0], stderr=slaves[1])
for fd in slaves: os.close(fd)

game_over = re.compile( 'The game is over.\r\n$', re.MULTILINE )

zork_output = read_subprocess( p, masters )

done = False
while not done:
    
    if game_over.search( zork_output ):
        done = True
    else:
        input = sys.stdin.readline()

        if command_prefix.match( input ):
            zorkshell_command_dispatch( input.strip(), p )
        else:
            p.stdin.write( input )
            time.sleep( .01 )
            zork_output = read_subprocess( p, masters )
            run_zork_output_processors( zork_output )

for fd in masters: os.close(fd)
p.wait()

    
