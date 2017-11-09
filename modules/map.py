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

        exits = self.directions.keys()
        exits.sort()
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
        path.append( (c, None ) )
                     
        done = False
        while len(path) > 0 and not done:

            r = path[-1][0]                 # last room in the path
            e = r._next_exit(path[-1][1])   # exit in "r" we're about to walk through
            path.pop()                      # remove the last exit we tried

            if e:
                walked_in_a_circle = False
                path_string = ""
                for s in path:
                    if s[0].name == r.name:
                        walked_in_a_circle = True
                    path_string = " ".join([ path_string, "%s:%s" % (s[0].name, s[1]) ])
                path_string = " ".join( [ path_string, "%s:%s" % (r.name, e) ] )
                log( "map: inspecting path %s" % path_string )

                path.append( (r, e) )           # walk through the new exit
                n = r.directions[e]             # name of room we'll end up in 

                if walked_in_a_circle:
                    # zilly zork maps have cycles
                    log( "detected cycle" )
                    next 
                elif n == room_name:
                    # woohoo
                    done = True
                    log( "FOUND PATH" )
                else:
                    path.append( (self.rooms[n], None) )  # repeat in the next room
                
    
    def show_map( self, z, args ):
        if not self.current_room:
            log( "map: I don't know what room we're in" )
            return
        
        log( "map: showing exits for %s" % self.current_room.name )
        exits = self.current_room.directions.keys()
        exits.sort()
        for e in exits:
            s = self.rooms[self.current_room.directions[e]]
            log( "map:               %2s: %s" % (e, s.name) )
        
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
                    log( "map: found matching item %s in %s" % ( i,n ) )
        
    def __init__( self ):
        self.rooms = {}
        self.current_room = None
        register_zorkshell_command( "/map", self.show_map )
        register_zorkshell_command( "/savemap", self.save_map )
        register_zorkshell_command( "/loadmap", self.save_map )
        register_zorkshell_command( "/finditem", self.find_item )
        register_zorkshell_command( "/nav", self.find_a_path )
        log( "map: please make sure \"brief\" descriptions are on." )
        

m = ZorkMap()
register_zorkshell_module( 'Map', m )
