from utils.prettyPrintLib import printColor
from libs.BasicUtils import dumpResource, getResource
import paramiko
import os
from stat import S_ISDIR, S_ISREG
from libs.BranchingManager import checkoutSnapshot

def transferDirectory(sftp, remotedir, localdir, sep):
    for entry in sftp.listdir_attr(remotedir):
        remotepath = sep.join([remotedir, entry.filename])
        localpath = os.path.join(localdir, entry.filename)
        mode = entry.st_mode
        if S_ISDIR(mode):
            try:
                os.mkdir(localpath)
            except OSError:     
                pass
            transferDirectory(sftp, remotepath, localpath, sep)
        elif S_ISREG(mode):
            sftp.get(remotepath, localpath)

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
    config = getResource(os.path.basename(args.config), specificPath=os.path.dirname(args.config))
    hostname = config["host"]  
    port = config["port"]  
    username = config["remote_user"]
    private_key_path = config["local_ssh_private_key"]

    # Create an SSH key object
    private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname, port, username, pkey=private_key)

    sftp = ssh_client.open_sftp()
    if config["remote_os"] == 'win32':
        sep = '\\'
    else :
        sep = '/'
    full_remote_path = sep.join([config["remote_path"], "CookieRepositories", args.name])
    if args.path :
        full_local_path = os.path.join(args.path, args.name)
    else:
        full_local_path = args.name

    if not os.path.isdir(full_local_path):
        os.makedirs(full_local_path, exist_ok=True)

    transferDirectory(sftp, full_remote_path, full_local_path, sep)
    sftp.close()
    ssh_client.close()
    os.chdir(full_local_path)
    checkoutSnapshot(None, specRef=args.branch)

def remoteConfig(args):
    pass

def pullChanges(args):
    pass

def pushCommit(args):
    pass
def pushTree(args):
    pass
def pushObject(args):
    pass


