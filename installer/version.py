"""Print pyemsi.__version__ without importing pyemsi: the one version both installers and CI use."""

import re
import sys
from pathlib import Path

init_text = (Path(__file__).resolve().parents[1] / "pyemsi" / "__init__.py").read_text(encoding="utf-8")
match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', init_text, re.MULTILINE)
if match is None:
    sys.exit("Could not find __version__ in pyemsi/__init__.py")
print(match.group(1).strip())
