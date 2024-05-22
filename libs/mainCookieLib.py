import argparse
import sys
import os
import shutil

# implemented libs and functions
from utils.prettyPrintLib import printColor
from libs.RemotingManager import editLoginFile, cloneRepo, remoteConfig, pullChanges, pushChanges
from libs.IndexManager import stageFiles, generateStatus, createCommit, unstageFiles 
from libs.BranchingManager import checkoutSnapshot, createBranch, updateHead, deleteBranch, createTag, deleteTag
from libs.BasicUtils import createDirectoryStructure, dumpResource, getResource, safeWrite, clearCommand
from libs.UndoLib import undoCommand
from libs.MergeManager import mergeSourceIntoTarget
from libs.LogsManager import logSequence
from libs.server.serverSetup import initializeServer

cookieWordArt='''
                                 __   .__        
              ____  ____   ____ |  | _|__| ____  
            _/ ___\/  _ \ /  _ \|  |/ /  |/ __ \ 
            \  \__(  <_> |  <_> )    <|  \  ___/ 
             \___  >____/ \____/|__|_ \__|\___  >
                 \/                  \/       \/ 
'''
config_template = '''
{
    "host":"<hostname>",
    "port":"<port for ssh (22)>",
    "remote_user":"<remote username>",
    "local_ssh_private_key":"<path to local key>",
    "host_os":"<nt/posix>",
    "remote_path":"<path to remote repositories>"
}
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
argsp.add_argument("-s",
                   action='store_true',
                   help="Initialize server.")

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
argsp.add_argument("-s",
                   action='store_true',
                   help="Check remote status.")

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
                   metavar="ref",
                   nargs="?",
                   default=None,
                   help="Hash or branch to checkout.")
argsp.add_argument("-r",
                   action='store_true',
                   help="Option to reset local changes.")

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
argsp.add_argument("-c",
                   action='store_true',
                   help="Create with checkout.")

#Branch deletion subcommand definition
argsp = argsubparsers.add_parser("delete_branch", help="Delete an existing branch.")
argsp.add_argument("-b",
                   "--branch",
                   metavar="branch",
                   default=None,
                   required=True,
                   help="Branch name to delete.")

#Undo subcommand definition
argsp = argsubparsers.add_parser("merge", help="Merge Commits or branches.")
argsp.add_argument("-t",
                   "--target",
                   metavar="target",
                   nargs="?",
                   required=True,
                   help="Target branch or commit upon which to perform merge.")
argsp.add_argument("-s",
                   "--source",
                   metavar="source",
                   nargs="?",
                   required=True,
                   help="Source content(s) for merge.")

# Tag creation subcommand definition
argsp = argsubparsers.add_parser("create_tag", help="Create a new tag.")
argsp.add_argument("-t",
                   "--tag",
                   metavar="tag",
                   default=None,
                   required=True,
                   help="Tag name to create.")
argsp.add_argument("ref",
                   metavar="ref",
                   nargs="?",
                   default=None,
                   help="Hash or branch to base new tag upon. If left empty will create based on current ref")
argsp.add_argument("-c",
                   action='store_true',
                   help="Create with checkout.")

# Tag deletion subcommand definition
argsp = argsubparsers.add_parser("delete_tag", help="Delete an existing tag.")
argsp.add_argument("-t",
                   "--tag",
                   metavar="tag",
                   default=None,
                   required=True,
                   help="Tag name to delete.")

#Undo subcommand definition
argsp = argsubparsers.add_parser("log", help="Print commit data.")
argsp.add_argument("-b",
                   action='store_true',
                   help="Priority for main branches and not merges.")

#Undo subcommand definition
argsp = argsubparsers.add_parser("clone", help="Clone remote repository.")
argsp.add_argument("name",
                   metavar="name",
                   default=None,
                   help="Repository name to clone.")
argsp.add_argument("-c",
                   "--config",
                   metavar="config",
                   default=None,
                   help="Path to clone configuration.")
argsp.add_argument("-p",
                   "--path",
                   metavar="path",
                   default=os.getcwd(),
                   help="Where to clone the repository.")
argsp.add_argument("-b",
                   "--branch",
                   metavar="branch",
                   default="master",
                   help="Branch name to clone.")
argsp.add_argument("-s",
                   action='store_true',
                   help="Option to clone sparsely.")

# Configure remote subcommand definition
argsp = argsubparsers.add_parser("rconfig", help="Configure remote data.")
argsp.add_argument("-f",
                   "--file",
                   metavar="file",
                   required=False,
                   default=None,
                   help="Path to config file.")
argsp.add_argument("-i",
                   "--ip",
                   metavar="hostname",
                   default=None,
                   help="Remote hostname(ip).")
argsp.add_argument("-p",
                   "--port",
                   metavar="port",
                   default=None,
                   help="Remote hostname port(22).")
argsp.add_argument("-u",
                   "--user",
                   metavar="user",
                   default=None,
                   help="Remote username.")
argsp.add_argument("-s",
                   "--ssh",
                   metavar="ssh",
                   default=None,
                   help="Path to local ssh private key(C:\\Users\\user\\.ssh\\id_rsa).")
argsp.add_argument("-o",
                   "--os",
                   metavar="os",
                   default=None,
                   help="Remote operating system(nt).")
argsp.add_argument("-r",
                   "--rpath",
                   metavar="rpath",
                   default=None,
                   help="Remote path to repositories(D:\\CookieRepositories).")
argsp.add_argument("-n",
                   "--name",
                   metavar="name",
                   default=None,
                   help="Name of remote repository.")

# Clear subcommand definition
argsp = argsubparsers.add_parser("clear", help="Clear local data(caches, history).")

# Clear subcommand definition
argsp = argsubparsers.add_parser("pull", help="Pull changes from remote.")

# Clear subcommand definition
argsp = argsubparsers.add_parser("push", help="Push changes to remote.")

#Undo subcommand definition
argsp = argsubparsers.add_parser("undo", help="Undo a command.")
argsp.add_argument("index",
                   metavar="index",
                   nargs="?",
                   default=None,
                   help="Command index to undo")


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    if args.command == 'add':               # add files to staging area
        add(args)
    elif args.command == 'remove':          # remove files from staging area
        remove(args)
    elif args.command == 'init':            # initialize cookie repository
        init(args)
    elif args.command == 'commit':          # commit staging area
        commit(args)
    elif args.command == 'checkout':        # checkout branch/tag/commit
        checkout(args)
    elif args.command == 'create_branch':   # create a branch
        create_branch(args)
    elif args.command == 'delete_branch':   # delete a branch
        delete_branch(args)
    elif args.command == 'create_tag':      # create a tag
        create_tag(args)
    elif args.command == 'delete_tag':      # delete a tag
        delete_tag(args)
    elif args.command == 'status':          # show status
        status(args)
    elif args.command == 'login':           # login with username/email
        login(args)
    elif args.command == 'delete':          # delete repo DEV ONLY!
        delete(args)
    elif args.command == 'undo':            # undo last command
        undo(args)
    elif args.command == 'log':             # log show commits
        log(args)
    elif args.command == 'merge':           # merge two branches/two commits
        merge(args)
    elif args.command == 'clone':           # clone remote
        clone(args)
    elif args.command == 'rconfig':         # configure remote data
        rconfig(args)
    elif args.command == 'clear':           # clear local data
        clear(args)
    elif args.command == 'pull':            # pull data from remote
        pull(args)
    elif args.command == 'push':            # pull data from remote
        push(args)
    else:
        printColor("Unknown command: {}".format(args.command),'red')
        sys.exit(1)

def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer

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

@parametrized
def addToUndoCache(fct, saveResource=[]):
    def inner(*args, **kwargs):
        history=getResource("history")
        index=history["index"]
        for resource_name in saveResource:
            resource=getResource(resource_name)
            safeWrite(os.path.join(".cookie", "cache", "undo_cache", str(index+1), resource_name), resource, jsonDump=True)
        rez=fct(*args, **kwargs)
        commandData=vars(args[0])
        if commandData["command"]=="delete":
            printColor("There's no undo-ing this...", "red")
            printColor("Clone Repository again!", "blue")
        else:
            history["commands"][index+1]=commandData
            history["index"]=history["index"]+1
            dumpResource("history", history)
        return rez
    return inner

def init(args):
    
    if args.s:
        initializeServer(args)
    else:
        print(cookieWordArt)
        createDirectoryStructure(args)

def clone(args):
    
    if not args.config :
        printColor("Please provide a path to a configuration file.", "red")
        print("     <> Usage:")
        print("         cookie <repository_name> -c <path_to_config>")
        print("=============================================================")
        print("     <> Configuration template:")
        print(config_template)
        sys.exit(1)
    print(cookieWordArt)
    cloneRepo(args)

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

@addToUndoCache(saveResource=["staged"])
@cookieRepoCertified
def add(args):
    generateStatus(args,quiet=True)
    stageFiles(args.paths)

@addToUndoCache(saveResource=["staged"])
@cookieRepoCertified
def remove(args):
    generateStatus(args, quiet=True)
    unstageFiles(args.paths)

@addToUndoCache(saveResource=["head"])
@cookieRepoCertified
def checkout(args):
    generateStatus(args, quiet=True)
    if args.r:
        checkoutSnapshot(args)
    else:
        checkoutSnapshot(args, reset = True)
@addToUndoCache()
@cookieRepoCertified
def create_branch(args):
    createBranch(args.branch, args.ref==None, args.ref, checkout=args.c)
    updateHead(args.branch, args.ref==None, args.ref)

@addToUndoCache()
@cookieRepoCertified
def delete_branch(args):
    deleteBranch(args.branch)

@addToUndoCache()
@cookieRepoCertified
def create_tag(args):
    createTag(args.tag, args.ref==None, args.ref, checkout=args.c)
    updateHead(args.tag, args.ref==None, args.ref)

@addToUndoCache()
@cookieRepoCertified
def delete_tag(args):
    deleteTag(args.branch)

@cookieRepoCertified
def status(args):
    generateStatus(args, quiet=False)

@addToUndoCache(saveResource=["refs", "index", "head", "logs", "staged"])
@cookieRepoCertified
def commit(args):
    createCommit(args, DEBUG=DEBUG)

@addToUndoCache(saveResource=["userdata"])
@cookieRepoCertified
def login(args):
    editLoginFile(args)

@cookieRepoCertified
def log(args):
    logSequence(args)

@addToUndoCache(saveResource=["refs", "index", "head", "logs", "staged"])
@cookieRepoCertified
def merge(args):
    mergeSourceIntoTarget(args.target, args.source)

@cookieRepoCertified
def undo(args):
    undoCommand(args)

@addToUndoCache(saveResource=["remote_config"])
@cookieRepoCertified
def rconfig(args):
    remoteConfig(args)

@cookieRepoCertified
def clear(args):
    clearCommand()

@addToUndoCache(saveResource=["logs", "refs"])
@cookieRepoCertified
def pull(args):
    pullChanges(args)

@cookieRepoCertified
def push(args):
    pushChanges(args)