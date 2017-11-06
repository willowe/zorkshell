import os
import shutil
from lib.common import *
from module import ZorkModule

class ZSave(ZorkModule):

    zork_builtin_save_filename = 'dsave.dat'
    
    def save( self, z, args ):
        self.__saving=True
        self.__name = "%s.dat" % args.pop()
        log( "save: starting save to %s" % self.__name )
        z.write_to_zork( "save\n" )

    def restore( self, z, args ):
        self.__name = "%s.dat" % args.pop()
        
        if not os.path.exists( self.__name ):
            log( "Can't restore; save file %s doesn't exist" % self.__name )
            self.__name = None
            return 

        shutil.copyfile( self.__name, ZSave.zork_builtin_save_filename )
        self.__restoring = True
        z.write_to_zork( "restore\n" )
        
        
    def output_processor( self, text, z ):
        if self.__saving == True:
            if text.startswith( 'Saved.' ):
                os.rename( ZSave.zork_builtin_save_filename, self.__name )
                log( "saved game to %s" % self.__name )
            else:
                log( "failed zsaving" )
            self.__saving=False
            self.__name = None

        if self.__restoring:
            if text.startswith( 'Restored.' ):
                log( "restored from %s" % self.__name )
            self.__restoring = False
            self.__name = None

    def __init__( self ):
        self.__saving=False
        self.__restoring=False
        register_zorkshell_command( '/restore', self.restore )        
        register_zorkshell_command( '/save', self.save )


m = ZSave()
register_zorkshell_module( 'ZSave', m )

