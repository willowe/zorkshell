# lib/zorkprocess.py
# wrap up all the logic for actually talking to a Zork instance

import subprocess
import errno
import select
import sys
import pty
import os
import re
import time
from common import *

class ZorkProcess:

    def __init__(self):
        self.read_buffsize = 1024
        self.masters = []
        self.slaves = []
        self.subprocess = None
        self.last_command = None
        
    def start_zork( self ):

        self.masters, self.slaves = zip(pty.openpty(), pty.openpty())
        self.subprocess = subprocess.Popen('zork', stdin=subprocess.PIPE, stdout=self.slaves[0], stderr=self.slaves[1])
        for fd in self.slaves:
            os.close(fd)

    def write_to_zork( self, input, echo=True ):
        if echo:
            sys.stdout.write( input )
        self.subprocess.stdin.write( input )
        self.last_command = input
        
    def read_zork_output( self ): 
        stdout = ''
        done = False

        ending_regexp = re.compile( '>$|\?\r\n$|The game is over\.\r\n$', re.MULTILINE )
    
        while not done:
            fds = select.select([ self.masters[0], self.masters[1] ], [], [], 0)[0]
            if len(fds) > 0:
                for fd in fds:
                    try:
                        data = os.read(fd, 1024)
                        debug( "read: %s" % data )
                        if len(data) > 0:
                            stdout += data
                    except OSError as e:
                        done = True
                        if e.errno != errno.EIO:
                            raise
                time.sleep(.01)

            if self.subprocess.poll():
                done = True
        
            if ending_regexp.search( stdout ):
                done = True

        return stdout

    def shutdown( self ):
        for fd in self.masters:
            os.close(fd)
        self.subprocess.wait()
