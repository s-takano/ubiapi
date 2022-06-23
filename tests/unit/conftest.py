#
# conftest.py
import sys
from os.path import dirname as d
from os.path import abspath, join
root_dir = d(d(d(abspath(__file__))))
sys.path.append(root_dir)

# print(f"conftest1:{sys.path}")