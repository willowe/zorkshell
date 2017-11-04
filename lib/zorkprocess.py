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

ending_regexp = re.compile( '>$|\?\r\n$|The game is over\.\r\n$', re.MULTILINE )

class ZorkProcess:

    def __init__(self):
        self.__read_buffsize = 1024
        self.__masters = []
        self.__slaves = []
        self.__subprocess = None
        self.__last_command = None
        self.__needs_read = False
        
    def start_zork( self ):
        self.__masters, self.__slaves = zip(pty.openpty(), pty.openpty())
        self.__subprocess = subprocess.Popen('zork', stdin=subprocess.PIPE, stdout=self.__slaves[0], stderr=self.__slaves[1])
        for fd in self.__slaves:
            os.close(fd)

    def write_to_zork( self, input, echo=True ):
        if echo:
            log( " telling zork \"%s\"" % input.strip() )
        self.__subprocess.stdin.write( input )
        time.sleep( .01 ) # yield CPU to zork 
        self.__last_command = input
        self.__needs_read = True
        
    def read_zork_output( self ): 
        stdout = ''
        done = False

        while not done:
            fds = select.select([ self.__masters[0], self.__masters[1] ], [], [], 0)[0]
            if len(fds) > 0:
                for fd in fds:
                    try:
                        data = os.read(fd, self.__read_buffsize)
                        debug( "read: %s" % data )
                        if len(data) > 0:
                            stdout += data
                    except OSError as e:
                        done = True
                        if e.errno != errno.EIO:
                            raise
                time.sleep(.01)

            if self.__subprocess.poll():
                done = True
        
            if ending_regexp.search( stdout ):
                done = True

        self.__needs_read = False
        return stdout

    def needs_read( self ):
        return self.__needs_read
    
    def shutdown( self ):
        for fd in self.__masters:
            os.close(fd)
        self.__subprocess.wait()
