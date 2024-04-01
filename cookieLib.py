import argparse
import sys
import os
import json
from time import time
from IndexManager import *
from ObjectManager import Commit
import shutil
from prettyPrintLib import printColor

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
        os.mkdir(project_dir)
        os.mkdir(os.path.join(project_dir, "objects"))
        os.mkdir(os.path.join(project_dir, "branches"))
        os.mkdir(os.path.join(project_dir, "logs"))
        os.mkdir(os.path.join(project_dir, "refs"))
        with open(os.path.join(project_dir, "index"), 'w') as fp:
            fp.write('{}')
        with open(os.path.join(project_dir, "staged"), 'w') as fp:
            fp.write('{"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}')
        with open(os.path.join(project_dir, "unstaged"), 'w') as fp:
            fp.write('{"A":{},"D":{},"M":{}}')
        with open(os.path.join(project_dir, "HEAD"), 'w') as fp:
            pass
        with open(os.path.join(project_dir, "userdata"), 'w') as fp:
            fp.write('{"user":"","email":""}')
    except OSError:
        printColor("Already a cookie repository at {}".format(project_dir),'red')
        sys.exit(1)
    printColor("Successfully initialized a cookie repository at {}".format(project_dir),'green')

@cookieCertified
def delete(args):
    shutil.rmtree('.cookie')
    printColor("    --> .cookie directory deleted. Objects kept", 'red')

@cookieCertified
def add(args):
    stageFiles(args.paths)

@cookieCertified
def checkout(args):
    pass

@cookieCertified
def status(args, quiet=False):
    compareToIndex()
    resolveStagingMatches()
    if not quiet:
        print("")
        printStaged()
        print("")
        printUnstaged()

@cookieCertified
def commit(args):
    status(args,quiet=True)
    if not isThereStagedStuff():
        printColor("There is noting to commit...", "blue")
        printColor("    Use 'cookie add <filename>' in order to prepare any change for commit.","blue")
        sys.exit(1) 
    metaData=['C']
    if os.stat(os.path.join('.cookie', 'HEAD')).st_size == 0:
        metaData.append('None')
    else:
        with open(os.path.join('.cookie', 'HEAD'), 'r') as headFile:
            metaData.append(headFile.read())
    metaData.append('A')
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
        headFile.write(newCommit.getHash())
    resetStagingArea()
    saveIndex(targetDirs)
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