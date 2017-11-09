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
# except for a few like "Bottom of Well" and "Entrance to Hades"
room_name_regexp = re.compile( "^[A-Z][a-z\-\']+\s*(of\s|to\s|[A-Z][a-z\-\']+\s*)*$" )

# needs to handle: "You can see:  foo"
inventory_regexp = re.compile( "^There (?:is|are) (.*) here.$" )

class ZorkRoom:
    def __init__( self, name ):
        self.name = name
        self.descr = None
        self.directions = {}
        self.inventory = []
        
    def add_exit( self, dir, name ):
        self.directions[dir] = name

    def update_description( self, text ):
        self.descr = text

    def update_inventory( self, args ):
        self.inventory = []
        for a in args:
            self.inventory.append( a )

    def _next_exit( self, e ):
        exits = self.directions.keys().sort()
        if len(exits) < 1:
            return None

        if e == None:
            return exits[0]

        i = 0
        found = 0
        while i < len(exits) and not found:
            if exits[i] == e:
                found = i + 1
            i += 1

        if found < len(exits):
            return exits[found]
            
        return None
        

class ZorkMap( ZorkModule ):

    def find_a_path( self, z, args ):
        room_name = " ".join( args )
        
        if not self.rooms.has_key( room_name ):
            log( "I can't find a room named %s" % room_name )
            return
        
        log( "searching for a path to %s" % room_name )

        c = self.current_room
        path = []
        e = c._next_exit( None )

        path.append( (c, e) )
        
    
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

        # what room are we in?
        if room_name_regexp.match( lines[0] ):

            name = lines[0]
            if not self.rooms.has_key( name ):
                log( "map: new room" )
                r = ZorkRoom( name )
                self.rooms[name] = r
            
            if self.current_room and is_motion:
                debug( "map: adding exit %s to %s: %s" % ( last_action, self.current_room.name, name )) 
                self.current_room.add_exit( last_action, name )


            self.current_room = self.rooms[name]

        else:
            
            if re.match( "^l(ook)?", last_action ) and text.startswith( "You are" ) and self.current_room:
                debug( "map: updated room description for %s" % self.current_room.name )
                self.current_room.update_description( text )
            elif is_motion:
                self.current_room = None

        inventory = []
        you_can_see = False
        for l in lines:
            if you_can_see and not l.endswith( "contains:" ) and not ignore.has_key( l ):
                inventory.append( l )
            else:
                m = inventory_regexp.match( l )
                if m != None:
                    inventory.append( m.group(1) )
            if l.startswith( "You can see: " ):
                you_can_see = True
                inventory.append( l.split( ": " )[1] )

        if self.current_room:
            if len(inventory) > 0:
                log( "map: found %d items: %s" % ( len(inventory), ",".join(inventory) ))
            self.current_room.update_inventory( inventory )
                

        
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

    def find_item( self, z, args ):
        text = args.pop()

        log( "map: searching for an item matching \"%s\"" % text )
        
        for n,r in self.rooms.items():
            for i in r.inventory:
                if i.find( text ) != -1:
                    log( "map: %s: %s" % ( n, i ) )
        
    def __init__( self ):
        self.rooms = {}
        self.current_room = None
        register_zorkshell_command( "/map", self.show_map )
        register_zorkshell_command( "/savemap", self.save_map )
        register_zorkshell_command( "/loadmap", self.save_map )
        register_zorkshell_command( "/finditem", self.find_item )
        log( "map: please make sure \"brief\" descriptions are on." )
        

m = ZorkMap()
register_zorkshell_module( 'Map', m )
