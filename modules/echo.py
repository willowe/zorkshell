import sys
from lib.common import *
from module import ZorkModule

class Echo(ZorkModule):

    def echo( self, subprocess, args ):
        sys.stdout.write( "# echo:" )
        for a in args:
            sys.stdout.write( "%s" % a )
            sys.stdout.write( "\n" )
        return 0

    def __init__( self ):
        register_zorkshell_command( '/echo', self.echo )

m = Echo()
register_zorkshell_module( 'Echo', m )
