from utils.prettyPrintLib import printColor
from libs.BasicUtils import dumpResource, getResource, safeWrite
from libs.BranchingManager import checkoutSnapshot
from libs.objectLib.ObjectManager import load
import paramiko
import os
from stat import S_ISDIR, S_ISREG
import sys
import time
import traceback
import json


def lockPath(sftp, pathname):
    with sftp.open("{}.lock".format(pathname), 'w') as remote_file:
        pass

def unlockPath(sftp, pathname):
    sftp.remove("{}.lock".format(pathname))

def isLocked(sftp, pathname):
    try:
        sftp.stat("{}.lock".format(pathname))
        return True
    except FileNotFoundError:
        return False

def remotePathExists(sftp, pathname):
    try:
        sftp.stat(pathname)
        return True
    except FileNotFoundError:
        return False
        
def getRemoteResource(sftp, remotePath, resourceName, sep):
    localPath = os.path.join(".cookie", "cache", "remote_cache")
    remoteResourcePath = sep.join([remotePath, ".cookie", resourceName])
    sftp.get(remoteResourcePath, os.path.join(localPath, resourceName))
    return getResource(resourceName, specificPath=localPath)

def dumpRemoteResource(sftp, remotePath, resourceName, content, sep):
    localPath = os.path.join(".cookie", "cache", "remote_cache")
    safeWrite(os.path.join(localPath, resourceName), content, jsonDump=True)
    remoteResourcePath = sep.join([remotePath, ".cookie", resourceName])
    sftp.put(os.path.join(localPath, resourceName), remoteResourcePath)

def pullDirectory(sftp, remotedir, localdir, sep):
    for entry in sftp.listdir_attr(remotedir):
        if localdir=='.':
            localpath=entry.filename
        else:
            localpath = os.path.join(localdir, entry.filename)
        if remotedir=='.':
            remotepath=entry.filename
        else:
            remotepath = sep.join([remotedir, entry.filename])
        mode = entry.st_mode
        if S_ISDIR(mode):
            try:
                os.mkdir(localpath)
            except OSError:     
                pass
            pullDirectory(sftp, remotepath, localpath, sep)
        elif S_ISREG(mode):
            if "objects" in remotepath or "refs" in remotepath:
                if os.path.exists(localpath):       # no point in replacing objects since they are unique
                    continue
            sftp.get(remotepath, localpath)

def pushDirectory(sftp, localdir, remotedir, sep, ignoreList):
    for entry in os.listdir(localdir):
        if entry in ignoreList:
            continue
        if localdir=='.':
            localpath=entry
        else:
            localpath = os.path.join(localdir, entry)
        if remotedir=='.':
            remotepath=entry
        else:
            remotepath = sep.join([remotedir, entry])
        mode = os.lstat(localpath).st_mode
        if S_ISDIR(mode):
            try:
                sftp.mkdir(remotepath)
            except:     
                pass
            pushDirectory(sftp, localpath, remotepath, sep, ignoreList)
        elif S_ISREG(mode):
            if "objects" in remotepath:
                if remotePathExists(sftp, remotepath) or "refs" in remotepath:       # no point in replacing objects since they are unique
                    continue
            sftp.put(localpath, remotepath)

def editLoginFile(args):
    if args.user == None:
            printColor("Please enter a valid username (empty to keep old one): ", 'white')
            user=input()
    else:
        user=args.user
    if args.email == None:
        printColor("Please enter a valid email: (empty to keep old one)", 'white')
        email=input()
    else:
        email=args.email
    data=getResource("userdata")
    if user != '':
        data["user"] = user
    if email != '':
        data["email"] = email
    dumpResource("userdata", data)
    printColor("Successfully logged in. Hello {}!".format(data["user"]), "green")

def cloneRepo(args):
    config = getResource(os.path.basename(args.config), specificPath=os.path.dirname(args.config), rconfig=True)
    private_key = paramiko.RSAKey.from_private_key_file(config["local_ssh_private_key"])
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(config["host"] , config["port"], config["remote_user"], pkey=private_key)
    except TimeoutError:
        printColor("Connection attempt timed out!", "red")
        printColor("Check remote host configuration", "red")
        sys.exit(1)

    sftp = ssh_client.open_sftp()
    if config["remote_os"] == 'nt':
        sep = '\\'
    else :
        sep = '/'
    full_remote_path = sep.join([config["remote_path"], "CookieRepositories", args.name])
    if args.path :
        full_local_path = args.path
        try:
            if os.listdir(full_local_path) != 0 :
                printColor("Given directory '{}' exists and is not empty, please clear first!".format(full_local_path), "red")
                sys.exit(1)
        except FileNotFoundError:
            pass
        except NotADirectoryError:
            printColor("Given path '{}' is not a directory".format(full_local_path), "red")
            sys.exit(1)
    else:
        full_local_path = args.name
    
    if not os.path.isdir(full_local_path):
        os.makedirs(full_local_path, exist_ok=True)
    if os.listdir(full_local_path)!=[]:
        printColor("Directory {} exists and is not empty. Aborting...".format(full_local_path), "red")
        sys.exit(1)
    printColor("Cloning repository {} to {}...".format(args.name, full_local_path), "green")
    try:
        pullDirectory(sftp, full_remote_path, full_local_path, sep)
    except FileNotFoundError:
        printColor("Please make sure given remote repository exists...", "red")
        sys.exit(1)
    sftp.close()
    ssh_client.close()
    os.chdir(full_local_path)
    os.makedirs(os.path.join(".cookie", "cache",  "undo_cache"))
    os.makedirs(os.path.join(".cookie", "cache",  "index_cache"))
    os.makedirs(os.path.join(".cookie", "cache",  "merge_cache"))
    os.makedirs(os.path.join(".cookie", "cache",  "remote_cache"))
    safeWrite(os.path.join(".cookie", "index"), {}, jsonDump=True)
    safeWrite(os.path.join(".cookie", "staged"), {"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}, jsonDump=True)
    safeWrite(os.path.join(".cookie", "unstaged"), {"A":{},"D":{},"M":{}}, jsonDump=True)
    safeWrite(os.path.join(".cookie", "head"), {"name":"master","hash":""}, jsonDump=True)
    safeWrite(os.path.join(".cookie", "userdata"), {"user":"", "email":""}, jsonDump=True)
    safeWrite(os.path.join(".cookie", "history"), {"index":0,"commands":{}}, jsonDump=True)

    checkoutSnapshot(None, specRef=args.branch, force=True, reset=True)
    safeWrite(os.path.join(".cookie", "remote_config"), config, jsonDump=True)

def remoteConfig(args):
    if args.file :
        if not os.path.isfile(args.file):
            printColor("Given path '{}' is not a file and cannot be used as config...".format(args.file), "red")
            sys.exit(1)
        givenConfig = getResource(os.path.basename(args.file), specificPath=os.path.dirname(args.file))
        dumpResource("remote_config", givenConfig)
        printColor("Successfully updated remote configuration.", "green")
        print(json.dumps(givenConfig, indent=2))
    else:
        rconfig = getResource("remote_config")
        if args.ip or args.port or args.user or args.ssh or args.os or args.rpath or args.name:
            if args.ip:
                rconfig["host"]=args.ip
                printColor("Changed IP to '{}'.".format(args.ip), "green")
            if args.port:
                rconfig["port"]=args.port
                printColor("Changed port to '{}'.".format(args.port), "green")
            if args.user:
                rconfig["remote_user"]=args.user
                printColor("Changed remote username to '{}'.".format(args.user), "green")
            if args.ssh:
                rconfig["local_ssh_private_key"]=args.ssh
                printColor("Changed path to local ssh private key to '{}'.".format(args.ssh), "green")
            if args.os:
                if args.os not in ["posix", "nt"]:
                    printColor("Unknown OS '{}'. Give <posix/nt>".format(args.os), "red")
                    sys.exit(1)
                rconfig["remote_os"]=args.os
                printColor("Changed remote operating system to '{}'.".format(args.os), "green")
            if args.rpath:
                rconfig["remote_path"]=args.rpath
                printColor("Changed remote path to '{}'.".format(args.rpath), "green")
            if args.name:
                rconfig["repo_name"]=args.name
                printColor("Changed remote repo name to '{}'.".format(args.name), "green")
        else:
            printColor("Configuring remote configuration at {}...".format(os.path.join(".cookie", "remote_config")), "green")
            print                                   ("=============================================================")
            rconfig["host"] =input                  (" <> Please provide the hostname                          : ")
            rconfig["port"] =input                  (" <> Please provide the port                              : ")
            rconfig["remote_user"] = input          (" <> Please provide the remote user                       : ")
            rconfig["local_ssh_private_key"] = input(" <> Please provide the path to the local private ssh key : ")
            rconfig["remote_os"] = input            (" <> Please provide the remote OS (nt for windows)        : ") 
            rconfig["remote_path"] = input          (" <> Please provide the remote path to repositories       : ")
            rconfig["repo_name"] = input            (" <> Please provide the remote name of repository         : ")
            print                                   ("=============================================================")
        dumpResource("remote_config", rconfig)
        printColor("Successfully updated remote configuration.", "green")
        print(json.dumps(rconfig, indent=2))

def pullChanges(args):
    config = getResource("remote_config")
    try:
        private_key = paramiko.RSAKey.from_private_key_file(config["local_ssh_private_key"])
    except OSError:
        printColor("Please configure remote data first!", "red")
        sys.exit(1)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(config["host"] , config["port"], config["remote_user"], pkey=private_key)
    except TimeoutError:
        printColor("Connection attempt timed out!", "red")
        traceback.print_exc()
        printColor("Check remote host configuration", "red")
        sys.exit(1) 
        
    if config["remote_os"] == 'nt':
        sep = '\\'
    else :
        sep = '/'
    sftp = ssh_client.open_sftp()
    remotePath = sep.join([config["remote_path"], "CookieRepositories", config["repo_name"]])
    
    refs = getResource("refs")
    head = getResource("head")
    if head["name"] == "DETACHED":
        printColor("Please checkout a branch before pulling changes...", "red")
        sys.exit(1)
    remoteRefs = getRemoteResource(sftp, remotePath, "refs", sep)
    if refs["B"][head["name"]] ==  remoteRefs["B"][head["name"]]:
        printColor("Local branch is on par with remote branch.", "green")
        sys.exit(0)

    refs["B"][head["name"]] = remoteRefs["B"][head["name"]]

    printColor("Pulling changes from remote, please wait...", "green")
    pullDirectory(sftp, remotePath, '.', sep)
    sftp.close()
    ssh_client.close()
    
    dumpResource("refs", refs)

    if refs["B"][head["name"]] != head["hash"]:   
        if head["name"] == 'DETACHED':          
            checkoutSnapshot(None, specRef = refs["B"][head["name"]], force=True, reset=True)
        else:
            checkoutSnapshot(None, specRef = head["name"], force=True, reset=True)
        
def fetchChanges(args):
    config = getResource("remote_config")
    try:
        private_key = paramiko.RSAKey.from_private_key_file(config["local_ssh_private_key"])
    except OSError:
        printColor("Please configure remote data first!", "red")
        sys.exit(1)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(config["host"] , config["port"], config["remote_user"], pkey=private_key)
    except TimeoutError:
        printColor("Connection attempt timed out!", "red")
        traceback.print_exc()
        printColor("Check remote host configuration", "red")
        sys.exit(1) 
        
    if config["remote_os"] == 'nt':
        sep = '\\'
    else :
        sep = '/'
    sftp = ssh_client.open_sftp()
    remotePath = sep.join([config["remote_path"], "CookieRepositories", config["repo_name"]])
    
    refs = getResource("refs")
    head = getResource("head")
    remoteRefs = getRemoteResource(sftp, remotePath, "refs", sep)
    if refs["B"][head["name"]] ==  remoteRefs["B"][head["name"]]:
        printColor("Local branch is on par with remote branch.", "green")
        sys.exit(0)

    printColor("Pulling changes from remote, please wait...", "green")
    pullDirectory(sftp, remotePath, '.', sep)
    sftp.close()
    ssh_client.close()
    refs["B"][head["name"]] = remoteRefs["B"][head["name"]]
    dumpResource("refs", refs)

    if refs["B"][head["name"]] != head["hash"]:   
        printColor("Local branch is different then remote, checkout to receive changes...", "green")
        
def findParent(head, target):
    currentCommit=load(head, os.path.join('.cookie', 'objects'))
    while currentCommit.getHash()!="None":
        if currentCommit.parents[0] == target:
            return True
        elif currentCommit.parents[0] == "None":
            return False
        else:
            currentCommit = load(currentCommit.parents[0], os.path.join('.cookie', 'objects'))
    return False

def pushChanges(args):
    config = getResource("remote_config")
    try:
        private_key = paramiko.RSAKey.from_private_key_file(config["local_ssh_private_key"])
    except OSError:
        printColor("Please configure remote data first!", "red")
        printColor("    <> Use 'cookie rconfig' or edit file at '{}'.".format(os.path.join(".cookie", "remote_config")), "white")
        sys.exit(1)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(config["host"] , config["port"], config["remote_user"], pkey=private_key)
    except TimeoutError:
        printColor("Connection attempt timed out!", "red")
        traceback.print_exc()
        printColor("Check remote host configuration", "red")
        sys.exit(1) 
    except Exception:
        printColor("Connection attempt failed!", "red")
        traceback.print_exc()
        printColor("Check remote host configuration", "red")
        sys.exit(1) 
    if config["remote_os"] == 'nt':
        sep = '\\'
    else :
        sep = '/'
    sftp = ssh_client.open_sftp()
    remotePath = sep.join([config["remote_path"], "CookieRepositories", config["repo_name"]])

    try: 
        sftp.mkdir(remotePath)
        sftp.mkdir(sep.join([remotePath, ".cookie"]))
        sftp.mkdir(sep.join([remotePath, ".cookie", "objects"]))
    except:
        pass
    if isLocked(sftp, remotePath):
        printColor("Another user currently pushing.", "cyan")
        printColor("    <> Waiting to finish...", "cyan")
    while isLocked(sftp, remotePath):
        time.sleep(1)
    refs = getResource("refs")
    head = getResource("head")
    try:
        remoteRefs = getRemoteResource(sftp, remotePath, "refs", sep)
        if refs["B"][head["name"]] ==  remoteRefs["B"][head["name"]]:
            printColor("Local branch is on par with remote branch.", "green")
            printColor("Nothing to push...", "green")
            sys.exit(1)
        else:
            if not findParent(refs["B"][head["name"]], remoteRefs["B"][head["name"]]):
                printColor("New changes on remote branch, please pull or fetch first...", "red")
                sys.exit(1)
    except FileNotFoundError:
        printColor("This is the first push.", "green")
    try:
        lockPath(sftp, remotePath)
        printColor("Pushing objects, please wait...", "green")
        remoteRefs["B"][head["name"]] = refs["B"][head["name"]]
        pushDirectory(sftp, os.path.join(".cookie", "objects"), sep.join([remotePath, ".cookie", "objects"]), sep, [])
        dumpRemoteResource(sftp, remotePath, "refs", remoteRefs, sep=sep)
        sftp.put(os.path.join(".cookie", "refs"), sep.join([remotePath, ".cookie", "refs.bak"]))
        sftp.put(os.path.join(".cookie", "logs"), sep.join([remotePath, ".cookie", "logs.bak"]))
        try:
            sftp.remove(sep.join([remotePath, ".cookie", "refs"]))
        except:
            pass
        sftp.rename(sep.join([remotePath, ".cookie", "refs.bak"]), sep.join([remotePath, ".cookie", "refs"]))
        try:
            sftp.remove(sep.join([remotePath, ".cookie", "logs"]))
        except:
            pass
        sftp.rename(sep.join([remotePath, ".cookie", "logs.bak"]), sep.join([remotePath, ".cookie", "logs"]))
        unlockPath(sftp, remotePath)
        printColor("Pushed changes to remote", "green")
    except:
        unlockPath(sftp, remotePath)
        traceback.print_exc()
        printColor("Failed to push changes to remote...", "red")
        sys.exit(1)