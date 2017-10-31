import sys
from lib.common import *
from module import ZorkModule

class Echo(ZorkModule):

    def echo( self, subprocess, args ):
        log( "ECHO: %s" % ' '.join(args) )

    def __init__( self ):
        register_zorkshell_command( '/echo', self.echo )

m = Echo()
register_zorkshell_module( 'Echo', m )
