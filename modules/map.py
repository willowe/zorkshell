import hashlib
import re
from module import ZorkModule
from lib.common import *

class ZorkMap( ZorkModule ):

    def __init__( self ):
        self.__map = {}

    def output_processor( self, text ):

        ignore = { "You can't go that way.\n": 1,
                   "I don't understand that.\n": 1,
                   "Huh?\n": 1 }
        
        if ignore.has_key( text ):
            log( "mapper ignored" )
            return
        
        pass

m = ZorkMap()
register_zorkshell_module( 'Map', m )
