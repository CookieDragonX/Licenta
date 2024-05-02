import os
import socket
from utils.prettyPrintLib import printColor
import getpass
import json

cookieServerString = """
                     __   .__                                                 
  ____  ____   ____ |  | _|__| ____     ______ ______________  __ ___________ 
_/ ___\/  _ \ /  _ \|  |/ /  |/ __ \   /  ___// __ \_  __ \  \/ // __ \_  __ \
\  \__(  <_> |  <_> )    <|  \  ___/   \___ \\  ___/|  | \/\   /\  ___/|  | \/
 \___  >____/ \____/|__|_ \__|\___  > /____  >\___  >__|    \_/  \___  >__|   
     \/                  \/       \/       \/     \/                 \/       

"""

def initializeServer(args):
    print(cookieServerString)
    os.chdir(args.path)
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    config = dict()
    config["host"] = IPAddr
    port = None
    while not port:
        try:
            port = int(input("Please provide the ssh port: "))
        except:
            printColor("SSH port should be a valid integer!", "red")
            port = None
    printColor("Selected port {} for ssh connection.".format(str(port)), "green")
    config["port"] = str(port)
    config["username"] = getpass.getuser()
    config["local_ssh_private_key"]="<replace_with_path>"
    config["remote_os"] = os.name
    config["remote_path"] = args.path
    os.makedirs("CookieRepositories")

    with open('remote_config', 'w') as fp:
        fp.seek(0)
        fp.write(json.dumps(config, indent=4))
    printColor("Cookie Server initialized at {}.".format(config["remote_path"]), "green")
