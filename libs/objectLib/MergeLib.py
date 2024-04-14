from libs.objectLib.ObjectManager import store, load, getObjectType
from libs.objectLib.Commit import Commit
from libs.objectLib.Blob import Blob


def mergeBlobs(target, source, objectsPath): #the args are hashes
    newBlobData=["B"]
    # this is way easier, difflib the 2 contents, parse result create new blob, ask to solve conflict if there is conflict
    # if that sounds good at that point too, here's sample, ly
            # import difflib

            # with open('file1.txt','r') as f1, open('file2.txt','r') as f2:
            #     for line in difflib.unified_diff(f1.read(), f2.read(), fromfile='file1', tofile='file2', lineterm=''):
            #         print(line)
    store(Blob('?'.join(newBlobData)), objectsPath)
    pass

def mergeTrees(target, source, objectsPath): # the args are hashes
    targetTree=load(target, objectsPath)
    sourceTree=load(source, objectsPath)
    newTree=load(target)
    for item in targetTree.map:
        try:
            if targetTree.map[item] != sourceTree.map[item]:
                if (getObjectType(targetTree.map[item])=='B'): #conflict case
                    newTree.map[item]=mergeBlobs(targetTree.map[item], sourceTree.map[item])
                else:
                    newTree.map[item]=mergeTrees(targetTree.map[item], sourceTree.map[item])
        except KeyError:
            # targetTree has file that source tree doesn't, thus sourceTree.map[item] cannot be accessed, continuing...
            continue
    store(newTree, objectsPath)
    return newTree.computeHash()

def mergeCommits(target, source, objectsPath):
    mergeCommitData=['C']
    mergeCommitData.append('whatever matters in commit idk')
    #new commit has snapshot mergeTrees(target.getSnapshot(), source.getSnapshot())
    store(Commit('?'.join(mergeCommitData)), objectsPath)
