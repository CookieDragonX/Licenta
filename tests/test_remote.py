import os
import subprocess
from tests.test_merging import test_merging1
from libs.MergeManager import mergeSourceIntoTarget
from libs.BasicUtils import getResource

if os.name == 'nt':
    interpreter = ["py", "-3"]
else:
    interpreter = ["python3"]


cookiePath=os.getcwd()

