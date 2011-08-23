import argparse
import shutil
import glob
import os
import subprocess
import time



class Environment( object ):
    def __init__( self, output ):
        self.actions = []
        self.output = output

    def add_action( self, action ):
        self.actions.append( action )

    def run( self ):
        for action in self.actions:
            action()

class Action( object ):
    def __init__( self, description, **arguments ):
        self.description = description
        self.arguments = arguments

    def call_command( self ):
        if 'command' in self.arguments:
            self.arguments['command']( self )
        else:
            return

    def call_transform( self ):
        transformed = None
        if 'transform' in self.arguments:
            transformed = self.arguments['transform']( getFileList( self.get_var( '$SRC$' ) ), self.get_var( '$DEST$' ) )
        else:
            trans = DefaultTransform()
            transformed = trans( self )
        return transformed

    def call_compare( self, transformed ):
        changedFiles = None
        if 'compare' in self.arguments:
            changedFiles = self.arguments['compare']( transformed )
        else:
            changedFiles = [x[0] for x in transformed ]
        return changedFiles

    def get_var( self, var ):
        if len(var) > 2 and var[0] == '$' and var[-1] == '$':
            strVar =  var[1:-1].lower()
            if strVar in self.arguments:
                return self.arguments[strVar]
            elif strVar in self.__dict__: 
                return self.__dict__[strVar]

        return None

    def __call__( self ):
        print( "Calling a interface..." )

class FileAction( Action ):
    def __call__( self, output = None):
        print( "Starting " + self.description + "....." )
        
        self.transformed = self.call_transform()
        self.changedfiles = self.call_compare( self.transformed )

        destination = self.get_var('$DEST$')
        
        if len(self.changedfiles) > 0 or 'processIfEmpty' in self.arguments:
            if not os.path.exists( destination ):
                print( 'Making dir ' + destination )
                os.makedirs(destination)

            self.call_command()

        print( "Finished " + self.description + "." )

class CopyTransform( object ):
    def __init__( self ):
        pass

    def __call__( self, files, dest ):
        transformed = []
        for file in files:
            path, filename = os.path.split( file )
            transformed.append( [file, dest + filename] )

        return transformed

class DefaultTransform( object ):
    def __call__(self, files, dest):
        transformed = []
        for file in files:
            path, filename = os.path.split( file )            
            transformed.append( [file, dest + filename] )


class FileExtTransform( object ):
    def __init__( self, destExt ):
        self.destExt = destExt

    def __call__( self, files, dest ):
        transformed = []
        for file in files:
            path, filename = os.path.split( file )
            basename, extension = os.path.splitext(filename)
            transformed.append( [file, dest + basename + '.' + self.destExt] )

        return transformed

class FileTimeCompare( object ):
    def __call__( self, transformedFiles ):
        changedFileList = []
        for file in transformedFiles:
            stats = os.stat(file[0])
            srcLastmod_date = time.localtime(stats[8])
            destLastmod_date =  None
            if os.path.exists( file[1] ):
                stats = os.stat( file[1] )
                destLastmod_date = time.localtime( stats[8] )

            if destLastmod_date != None:
                if srcLastmod_date > destLastmod_date:
                    changedFileList.append( file[0] )
        return changedFileList

class SubProcessCommand( object ):
    def __init__( self, command, parameters ):
        self.command = command
        self.parameters = parameters

    def __call__( self, action ):
        call = [self.command]

        for param in self.parameters:
            var = action.get_var( param )
            if var == None:
                var = param

            print( var )
            if type(var) == list:
                call += var
            else:
                call.append( var )

        print call
        output = subprocess.check_call( call )
        print( output )

class CopyCommand( object ):
    def __call__( self, action ):
        var = action.get_var( '$CHANGEDFILES$' )
        output = action.get_var( '$DEST$' )
        copy( var, output )


def clean():
    delete( output )

def build():
    env = Environment("build\\")

    coffee = FileAction('CoffeeScript Compiler',
                    compare=FileTimeCompare(),
                    src='source\\scripts\\*.coffee', dest=env.output + 'scripts\\',
                    command=SubProcessCommand('utils\\CoffeeSharp\\Coffee.exe',
                    ['-o', '$DEST$', '-c', '$CHANGEDFILES$']), transform=FileExtTransform('js'))

    copy_files = FileAction( 'Copying client', src='source\\*.*', dest=env.output, command=CopyCommand(), transform=CopyTransform(), compare=FileTimeCompare() )
    env.add_action( coffee )
    env.add_action( copy_files )
    env.run()

#copy = Action( 'source/*.*', output, copy, True, False )

def copy( files, dest ):
    for file in files:
        print( "Copying " + file + " to " + dest )
        shutil.copy( file, dest )

def getFileList( path ):
    return glob.glob( path )

def delete( dir ):
    print( 'Deleting %(directory)s' % {'directory':dir} )
    shutil.rmtree( dir )


			
	
		
		
		

