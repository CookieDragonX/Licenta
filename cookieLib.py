import argparse
import sys
import os
from prettyPrintLib import printColor
import shutil
from RemotingManager import editLoginFile
from IndexManager import createDirectoryStructure, stageFiles, generateStatus, createCommit
from BranchingManager import checkoutSnapshot

#                      __   .__                              
#   ____  ____   ____ |  | _|__| ____   ___  __ ____   ______
# _/ ___\/  _ \ /  _ \|  |/ /  |/ __ \  \  \/ // ___\ /  ___/
# \  \__(  <_> |  <_> )    <|  \  ___/   \   /\  \___ \___ \ 
#  \___  >____/ \____/|__|_ \__|\___  >   \_/  \___  >____  >
#      \/                  \/       \/             \/     \/                     
# 

DEBUG=True  #make testing easier :D

argparser = argparse.ArgumentParser(description="Cookie: World's Best SCM!")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

#init subcommand definition
argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=os.getcwd(),
                   help="Where to create the repository.")

#add subcommand definition
argsp = argsubparsers.add_parser("add", help="Add a file to staging area.")
argsp.add_argument("paths",
                   nargs="+",
                   help="File(s) to add to staging area")

#status subcommand definition
argsp = argsubparsers.add_parser("status", help="Report the status of the current cookie repository.")

#commit subcommand definition
argsp = argsubparsers.add_parser("commit", help="Commit your changes.")
argsp.add_argument("-m",
                   "--message",
                   metavar="message",
                   required=True,
                   help="Message for this commit.")

#login subcommand definition
argsp = argsubparsers.add_parser("login", help="Set username and email for local user.")
argsp.add_argument("-u",
                   "--user",
                   metavar="user",
                   nargs="?",
                   default=None,
                   help="Username.")
argsp.add_argument("-e",
                   "--email",
                   metavar="email",
                   nargs="?",
                   default=None,
                   help="E-mail address.")

#Delete subcommand definition
argsp = argsubparsers.add_parser("delete", help="Delete repository at a certain location. ->DEBUG ONLY<-")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=os.getcwd(),
                   help="Path to repo that needs deletion")

#Checkout subcommand definition
argsp = argsubparsers.add_parser("checkout", help="Checkout a previous snapshot.")
argsp.add_argument("ref",
                   metavar="directory",
                   nargs="?",
                   default=None,
                   help="Hash or branch to checkout.")

#Branch creation subcommand definition
argsp = argsubparsers.add_parser("create_branch", help="Create a new branch.")
argsp.add_argument("-b",
                   "--branch",
                   metavar="branch",
                   nargs="?",
                   default=None,
                   help="Branch name to create.")
argsp.add_argument("ref",
                   metavar="ref",
                   nargs="?",
                   default=None,
                   help="Hash or branch to base new branch upon. If left empty will create based on current branch")

def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    if args.command == 'add':
        add(args)
    elif args.command == 'init':
        init(args)
    elif args.command == 'commit':
        commit(args)
    elif args.command == 'checkout':
        checkout(args)
    elif args.command == 'create_branch':
        create_branch(args)
    elif args.command == 'status':
        status(args)
    elif args.command == 'login':
        login(args)
    elif args.command == 'delete':
        delete(args)
    else:
        printColor("Unknown command: {}".format(args.command),'red')
        sys.exit(1)

def cookieCertified(fct):       #decorator for functions that work with objects to that everything happens at correct repo location
    def inner(*argv, **kwargs):
        prevwd=""
        initial=os.getcwd()
        while '.cookie' not in os.listdir():
            prevwd=os.getcwd()
            os.chdir('..')
            if prevwd==os.getcwd():
                printColor('Could not resolve cookie repository at this location!','red')
                printColor('Make sure you are in the correct location...','white')
                sys.exit(1)
        rez=fct(*argv, **kwargs)
        os.chdir(initial)
        return rez
    return inner


def init(args):
    createDirectoryStructure(args)

@cookieCertified
def delete(args):
    if DEBUG:
        shutil.rmtree('.cookie')
        printColor(".cookie directory deleted. Objects kept", 'red')
    else:
        printColor("Command is for developer only. Delete repo manually if needed.", 'red')
        printColor("Cookie does not assume responsability!", "red")

@cookieCertified
def add(args):
    status(args,quiet=True)
    stageFiles(args.paths)

@cookieCertified
def checkout(args):
    checkoutSnapshot(args)

@cookieCertified
def create_branch(args):
    pass

@cookieCertified
def status(args, quiet=False):
    generateStatus(args, quiet=False)

@cookieCertified
def commit(args):
    createCommit(args, DEBUG=DEBUG)

@cookieCertified
def login(args):
    editLoginFile(args)
