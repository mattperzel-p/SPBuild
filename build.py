from epb import Environment, FileAction, FileTimeCompare, FileExtTransform, CopyCommand, CopyTransform, SubProcessCommand, delete, copy
import argparse

parser = argparse.ArgumentParser(description='Super Lightweight Build System')
parser.add_argument('target', metavar='t', nargs='+', help='target')
args = parser.parse_args()
targets = args.target

env = Environment("build\\")

def clean():
    delete( env.output )

def build():
    coffee = FileAction('CoffeeScript Compiler',
                    compare=FileTimeCompare(),
                    src='source\\scripts\\*.coffee', dest=env.output + 'scripts\\',
                    command=SubProcessCommand('utils\\CoffeeSharp\\Coffee.exe',
                    ['-o', '$DEST$', '-c', '$CHANGEDFILES$']), transform=FileExtTransform('js'))

    copy_files = FileAction( 'Copying client', src='source\\*.*', dest=env.output, command=CopyCommand(), transform=CopyTransform(), compare=FileTimeCompare() )
    env.add_action( coffee )
    env.add_action( copy_files )
    env.run()

for k in targets:
    if locals()[k]:
        locals()[k]()


