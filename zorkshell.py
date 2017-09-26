#!`which python`

import os
import sys
import subprocess
import errno
import select
import pty
import time
import re

READ_BUFFSIZE=1024

def log(*args):
    print "# ", args
    
if os.geteuid() == 0:
    sys.stderr.write("Don't run me as root.\n")
    os.exit(1)
command = 'zork'
masters, slaves = zip(pty.openpty(), pty.openpty())
p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=slaves[0], stderr=slaves[1], shell=True, executable='/bin/bash')
for fd in slaves: os.close(fd)

def read_subprocess( p ):
    stdout = ''
    stderr = ''
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
        time.sleep(.1)
        if p.poll():
            done = True
        
        if ending_regexp.search( stdout ):
            done = True

    if( stdout ):
        sys.stdout.write( stdout )
        sys.stdout.flush()
    return ( stdout, stderr )

while not p.poll():

    read_subprocess( p )

    input = sys.stdin.readline()
    try:
        p.stdin.write( input )
    except OSError as e:
        if e.errno != errno.EIO:
            raise
    time.sleep( .01 )


for fd in masters: os.close(fd)


    
