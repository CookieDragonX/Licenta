import argparse
import sys
import os
import shutil

# implemented libs and functions
from utils.prettyPrintLib import printColor
from libs.RemotingManager import editLoginFile
from libs.IndexManager import stageFiles, generateStatus, createCommit, unstageFiles 
from libs.BranchingManager import checkoutSnapshot, createBranch, updateHead, deleteBranch
from libs.BasicUtils import createDirectoryStructure, dumpResource, getResource
from libs.LogsManager import printCommitData
from libs.UndoLib import undoCommand


cookieWordArt='''
                                 __   .__        
              ____  ____   ____ |  | _|__| ____  
            _/ ___\/  _ \ /  _ \|  |/ /  |/ __ \ 
            \  \__(  <_> |  <_> )    <|  \  ___/ 
             \___  >____/ \____/|__|_ \__|\___  >
                 \/                  \/       \/ 
'''
DEBUG=False  #make manual testing easier, but paradoxically make automated tests fail D:

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

#remove subcommand definition
argsp = argsubparsers.add_parser("remove", help="Remove a file to staging area.")
argsp.add_argument("paths",
                   nargs="+",
                   help="File(s) to remove from staging area")

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
                   default=None,
                   required=True,
                   help="Branch name to create.")
argsp.add_argument("ref",
                   metavar="ref",
                   nargs="?",
                   default=None,
                   help="Hash or branch to base new branch upon. If left empty will create based on current branch")

#Branch deletion subcommand definition
argsp = argsubparsers.add_parser("delete_branch", help="Delete an existing branch.")
argsp.add_argument("-b",
                   "--branch",
                   metavar="branch",
                   default=None,
                   required=True,
                   help="Branch name to create.")

#Undo subcommand definition
argsp = argsubparsers.add_parser("log", help="Print commit data.")

#Undo subcommand definition
argsp = argsubparsers.add_parser("undo", help="Undo a command")
argsp.add_argument("index",
                   metavar="index",
                   nargs="?",
                   default=None,
                   help="Command index to undo")


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    if args.command == 'add':
        add(args)
    elif args.command == 'remove':
        remove(args)
    elif args.command == 'init':
        init(args)
    elif args.command == 'commit':
        commit(args)
    elif args.command == 'checkout':
        checkout(args)
    elif args.command == 'create_branch':
        create_branch(args)
    elif args.command == 'delete_branch':
        delete_branch(args)
    elif args.command == 'status':
        status(args)
    elif args.command == 'login':
        login(args)
    elif args.command == 'delete':
        delete(args)
    elif args.command == 'undo':
        undo(args)
    elif args.command == 'log':
        log(args)
    else:
        printColor("Unknown command: {}".format(args.command),'red')
        sys.exit(1)

def cookieRepoCertified(fct):       #decorator for functions that work with objects to that everything happens at correct repo location
    def inner(*args, **kwargs):
        prevwd=""
        initial=os.getcwd()
        while '.cookie' not in os.listdir():
            prevwd=os.getcwd()
            os.chdir('..')
            if prevwd==os.getcwd():
                printColor('Could not resolve cookie repository at this location!','red')
                printColor('Make sure you are in the correct location...','white')
                sys.exit(1)
        rez=fct(*args, **kwargs)
        os.chdir(initial)
        return rez
    return inner

def addToUndoCache(fct):
    def inner(*args, **kwargs):
        rez=fct(*args, **kwargs)
        commandData=vars(args[0])
        if commandData["command"]=="delete":
            printColor("There's no undo-ing this...", "red")
            printColor("Clone Repository again!", "blue")
        else:
            history=getResource("history")
            index=history["index"]
            history["commands"][index+1]=commandData
            history["index"]=history["index"]+1
            dumpResource("history", history)
        return rez
    return inner

def init(args):
    print(cookieWordArt)
    createDirectoryStructure(args)

@cookieRepoCertified
def delete(args):
    if DEBUG:
        shutil.rmtree('.cookie')
        printColor(".cookie directory deleted. Files kept...", 'red')
    else:
        printColor("Command is for cookie developers only...", 'red')
        printColor("Delete repo manually if needed.", "red")
        printColor("Cookie does not assume responsability!", "red")
        sys.exit(1)

@addToUndoCache
@cookieRepoCertified
def add(args):
    generateStatus(args,quiet=True)
    stageFiles(args.paths)

@addToUndoCache
@cookieRepoCertified
def remove(args):
    generateStatus(args, quiet=True)
    unstageFiles(args.paths)

@addToUndoCache
@cookieRepoCertified
def checkout(args):
    checkoutSnapshot(args)

@addToUndoCache
@cookieRepoCertified
def create_branch(args):
    createBranch(args.branch, args.ref==None, args.ref)
    updateHead(args.branch, args.ref==None, args.ref)

@addToUndoCache
@cookieRepoCertified
def delete_branch(args):
    deleteBranch(args.branch)

@cookieRepoCertified
def status(args):
    generateStatus(args, quiet=False)

@addToUndoCache
@cookieRepoCertified
def commit(args):
    createCommit(args, DEBUG=DEBUG)

@addToUndoCache
@cookieRepoCertified
def login(args):
    editLoginFile(args)

@cookieRepoCertified
def log(args):
    head=getResource("HEAD")
    printCommitData(head["hash"])

@cookieRepoCertified
def undo(args):
    undoCommand(args)

