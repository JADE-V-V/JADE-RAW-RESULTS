import shutil
import os

ROOT = r'R:\AC_ResultsDB\Jade\03_JADEv300_root\Tests\Post-Processing\Single_Libraries'


for root, dirs, files in os.walk(ROOT):
    if root.endswith('Raw_Data'):
        rel_path = os.path.relpath(root, ROOT)
        try:
            shutil.copytree(root, os.path.join(r'ROOT', rel_path))
        except FileExistsError:
            # this behaviour could be changed to overwrite the existing folder
            pass
