import os
from lib.common import *
from module import ZorkModule

class ZSave(ZorkModule):

    def zsave( self, subprocess, args ):
        self.__saving=True
        self.__name = "%s.dat" % args.pop()
        subprocess.stdin.write( "save\n" )

    def output_processor( self, text ):
        if self.__saving == True:
            if text.startswith( 'Saved.' ):
                os.rename( 'dsave.dat', self.__name )
                log( "saved game to %s" % self.__name )
            else:
                log( "failed zsaving" )
            self.__saving=False
            self.__name = None
                           
    def __init__( self ):
        self.__saving=False
        register_zorkshell_command( '\zsave', self.zsave )

m = ZSave()
register_zorkshell_module( 'ZSave', m )

