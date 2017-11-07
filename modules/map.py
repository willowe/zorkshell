import hashlib
import re
import pickle
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

# room names are sequences of capitalized words
# still need to handle "Bottom of Well"
room_name_regexp = re.compile( "^[A-Z][a-z\-]+\s*(of|to|[A-Z][a-z\-]+\s*)*$" )

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

        if room_name_regexp.match( lines[0] ):

            name = lines[0]
            if not self.rooms.has_key( name ):
                log( "map: new room" )
                r = ZorkRoom( name )
                self.rooms[name] = r
            
            if self.current_room and is_motion:
                log( "map: adding exit %s to %s: %s" % ( last_action, self.current_room.name, name )) 
                self.current_room.add_exit( last_action, name )

            self.current_room = self.rooms[name]

        else:
            
            if re.match( "^l(ook)?", last_action ) and text.startswith( "You are" ) and self.current_room:
                log( "map: updated room description for %s" % self.current_room.name )
                self.current_room.update_description( text )
            else:
                self.current_room = None
                
        # todo:  keep an inventory of what's in each room based on "you can see:"
        
    def save_map( self, z, args ):

        filename = "map.pickle"
        if len(args) > 0:
            filename = "%s.pickle" % args.pop()

        f = open( filename, "w" )
        pickle.dump( self.rooms, f )
        f.close

        log( "saved map to %s" % filename )
            

    def load_map( self, z, args ):

        filename = "map.pickle"
        if len(args) > 0:
            filename = "%s.pickle" % args.pop()

        f = open( filename, "w" )
        self.rooms = pickle.load( f )
        f.close

        log( "loaded map to %s" % filename )

        
    def __init__( self ):
        self.rooms = {}
        self.current_room = None
        register_zorkshell_command( "/map", self.show_map )
        register_zorkshell_command( "/savemap", self.save_map )
        register_zorkshell_command( "/loadmap", self.save_map )
        log( "map: please make sure \"brief\" descriptions are on." )
        

m = ZorkMap()
register_zorkshell_module( 'Map', m )
