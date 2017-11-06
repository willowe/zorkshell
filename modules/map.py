import hashlib
import re
from module import ZorkModule
from lib.common import *

ignore = { "You can't go that way.\r\n>": 1,
           "I don't understand that.\r\n>": 1,
           "Huh?\r\n>": 1,
           "There is a wall there.\r\n>": 1,
           "The game is over.\r\n": 1,
           ">": 1
}

motion_commands = [ "north", "south", "east", "west", "up", "down", "ne", "se", "nw", "sw" ]

first_sentence = re.compile( "^[^\.].*\.?" )

class ZorkRoom:
    def __init__( self, name ):
        self.name = name
        self.descr = None
        self.directions = {}

    def add_exit( self, dir, name ):
        self.directions[dir] = name

    def update_description( self, text ):
        self.descr = text
        
class ZorkMap( ZorkModule ):

    def show_map( self, z, args ):

        if not self.current_room:
            log( "map: I don't know what room we're in" )
            return
        
        log( "map: showing exits for %s" % self.current_room.name )

        for d in self.current_room.directions.keys():
            s = self.rooms[self.current_room.directions[d]]
            log( "map:               %2s: %s" % (d, s.name) )
        
    def output_processor( self, text, z ):
        
        if ignore.has_key( text ):
            debug( "map: ignored" )
            return

        last_action = z.last_write().lower().strip()
        is_motion = False
        for x in motion_commands:
            if x.startswith( last_action ):
                is_motion = True

        lines = re.split( "\r\n", text )

        if re.match( "^l(ook)?", last_action ) and text.startswith( "You are" ) and self.current_room:
            self.current_room.update_description( text )
        
        if text.startswith( "You " ) or text.startswith( "The ") or text.startswith( "There is " ):
            return
        
        if not is_motion:
            debug( "map: last action wasn't motion" )
            return

        name = lines[0]
        
        if not self.rooms.has_key( name ):
            log( "map: new room" )
            r = ZorkRoom( name )
            self.rooms[name] = r
            
        if self.current_room:
            self.current_room.add_exit( last_action, name )

        self.current_room = self.rooms[name]
        
        # todo:  keep an inventory of what's in each room based on "you can see:"
        

    def __init__( self ):
        self.rooms = {}
        self.current_room = None
        register_zorkshell_command( "/map", self.show_map )
        log( "map: please make sure \"brief\" descriptions are on." )
        

m = ZorkMap()
register_zorkshell_module( 'Map', m )
