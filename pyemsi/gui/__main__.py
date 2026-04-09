"""Allow running pyemsi.gui as a module: python -m pyemsi.gui [workspace]"""

import argparse

parser = argparse.ArgumentParser(prog="pyemsi", description="pyemsi GUI")
parser.add_argument("workspace", nargs="?", default=None, help="Folder to open as workspace")
args = parser.parse_args()

from pyemsi.gui import launch

launch(workspace_path=args.workspace)
