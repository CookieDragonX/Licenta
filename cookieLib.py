import argparse
import sys
import os
import json
from time import time
from IndexManager import *
from SnapshotManager import *
from ObjectManager import Commit, getObjectType
import shutil
from prettyPrintLib import printColor
from errors import NoSuchObjectException

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
                   metavar="directory",
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
    elif args.command == 'new_branch':
        new_branch(args)
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
    project_dir=os.path.join(args.path, '.cookie')
    try:
        os.makedirs(project_dir)
        os.mkdir(os.path.join(project_dir, "objects"))
        os.mkdir(os.path.join(project_dir, "logs"))
        with open(os.path.join(project_dir, "index"), 'w') as fp:
            fp.write('{}')
        with open(os.path.join(project_dir, "staged"), 'w') as fp:
            fp.write('{"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}')
        with open(os.path.join(project_dir, "unstaged"), 'w') as fp:
            fp.write('{"A":{},"D":{},"M":{}}')
        with open(os.path.join(project_dir, "HEAD"), 'w') as fp:
            fp.write('{"name":"master","hash":""}')
        with open(os.path.join(project_dir, "userdata"), 'w') as fp:
            fp.write('{"user":"","email":""}')
        with open(os.path.join(project_dir, "refs"), 'w') as fp:
            fp.write('{"B":{"master":""},"T":{}}')
    except OSError:
        printColor("Already a cookie repository at {}".format(project_dir),'red')
        sys.exit(1)
    printColor("Successfully initialized a cookie repository at {}".format(project_dir),'green')

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
    if args.ref == None:
        printColor("This does nothing, but is allowed. Give me some arguments!", "blue")
        sys.exit(0)
    with open(os.path.join('.cookie', 'refs'), 'r') as refsFile:
        refs=json.load(refsFile)
    if args.ref not in refs['B'] and args.ref not in refs['T']:
        try:
            objType=getObjectType(args.ref)
        except NoSuchObjectException:
            printColor("There is no such commit to check out!", "red")
            sys.exit(1)
        if objType != 'C':
            printColor("That's not the hash of a commit, where did you get that?", "red") 
            sys.exit(1)                                                                             #there's improvement to be done here
        snapshot=getSnapshotFromCommit(args.ref)                                                    #get snapshot and raise notACommitError
    else:
        if args.ref in refs['B']:
            printColor("Checking out branch {}...".format(args.refs), "green")
            snapshot=getSnapshotFromCommit(refs['B'][args.ref])
        if args.ref in refs['T']:
            printColor("Checking out tag {}...".format(args.refs), "green")
            snapshot=getSnapshotFromCommit(refs['T'][args.ref])
    resetToSnapshot(snapshot)

@cookieCertified
def new_branch(args):
    with open(os.path.join('.cookie', 'HEAD'), 'r') as headFile:
        head=json.load(headFile)  

@cookieCertified
def status(args, quiet=False):
    compareToIndex()
    resolveStagingMatches()
    if not quiet:
        printStaged()
        printUnstaged()

@cookieCertified
def commit(args):
    status(args,quiet=True)
    if not isThereStagedStuff():
        printColor("There is noting to commit...", "blue")
        printColor("    Use 'cookie add <filename>' in order to prepare any change for commit.","blue")
        sys.exit(1) 
    metaData=['C']
    with open(os.path.join('.cookie', 'HEAD'), 'r') as headFile:
        head=json.load(headFile)
    if head["hash"] == "" :
        metaData.append('None')
    else :
        metaData.append(head["hash"])
    metaData.append('A')
    if DEBUG:
        metaData.append("Totally_Valid_Username")
    else:
        with open(os.path.join('.cookie', 'userdata'), 'r') as fp:
            userdata=json.load(fp)
            
        if userdata['user'] == "":
            printColor("Please login with a valid e-mail first!",'red')
            printColor("Use 'cookie login'",'white')
            sys.exit(0)
        else:
            metaData.append(userdata['user'])
    metaData.append(args.message)
    metaData.append(str(time()))
    targetDirs=getTargetDirs()
    metaData.append(generateSnapshot(targetDirs))
    newCommit=Commit(':'.join(metaData))
    store(newCommit, os.path.join('.cookie', 'objects'))
    with open(os.path.join('.cookie', 'HEAD'), 'w') as headFile:
        head["hash"]=newCommit.getHash()
        json.dump(head, headFile)
    resetStagingArea()
    #saveIndex(targetDirs)
    printColor("Successfully commited changes.","green")
    printColor("Current commit hash: "+newCommit.getHash(), 'green')

@cookieCertified
def login(args):
    printColor("Please enter a valid username (empty to keep old one): ", 'white')
    user=input()
    printColor("Please enter a valid email: (empty to keep old one)", 'white')
    email=input()
    with open(os.path.join('.cookie', 'userdata'), 'r') as fp:
        data=json.load(fp)
    if user != '':
        data["user"] = user
    if email != '':
        data["email"] = email
    print(data)
    with open(os.path.join('.cookie', 'userdata'), 'w') as fp:
        json.dump(data, fp)
