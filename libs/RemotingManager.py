from utils.prettyPrintLib import printColor
from libs.BasicUtils import dumpResource, getResource

def  editLoginFile(args):
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