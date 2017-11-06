#!/usr/bin/env python

import os
import sys
import time
import re

from lib.common import *
from lib.zorkprocess import ZorkProcess
import modules

# void main() 

if os.geteuid() == 0:
    sys.stderr.write("Don't run me as root.\n")
    os.exit(1)
    
z = ZorkProcess()
z.start_zork()
    
game_over = re.compile( 'The game is over.\r\n$', re.MULTILINE )

zork_output = z.read_zork_output()
sys.stdout.write( zork_output )
sys.stdout.flush()

done = False
while not done:

    if game_over.search( zork_output ):
        done = True

    else:
        if z.needs_read():
            zork_output = z.read_zork_output()
            sys.stdout.write( zork_output )
            sys.stdout.flush()
            run_zork_output_processors( zork_output, z )
        else:
            input = sys.stdin.readline()

            if command_prefix.match( input ):
                zorkshell_command_dispatch( input.strip(), z )
            else:
                z.write_to_zork( input, echo=False )
                



    
