import os
import json
import subprocess
import shutil
from tests.test_branching import test_branching1, test_cleanup
###################################################################
#               Preconditions:
#
#   - there should be not directory named 'Test_Repo' as this test
#       will create it and apply basic commands on it
#
##################################################################

cookiePath="D:\\stuffs\\Licenta"

def test_merging1():
    test_branching1()

# def test_clean_merge():
#     test_cleanup()