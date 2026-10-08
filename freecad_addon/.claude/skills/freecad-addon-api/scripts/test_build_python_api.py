"""One stdlib fixture for source aliases, guards, signatures and lifecycle docs."""

import ast
from pathlib import Path

from build_python_api import build, exports, import_target
from build_references import temporary_workspace


with temporary_workspace() as root:
    source = root / "facade.py"
    source.write_text('''"""Facade documentation."""
from factory import make_line as makeLine
if App.GuiUp:
    from gui import Provider
else:
    def unavailable():
        """Fallback behavior."""
        return None
try:
    from optional import Feature
except ImportError:
    Feature = None
__all__ = ["makeLine", "Shape", "old"]
@deprecated(deprecated_in="26.3", removed_in="28.3", replacement="new")
def old(value, /, *, option=True):
    """Legacy function purpose."""
    return value
class Shape(Base):
    """Shape purpose."""
    @property
    def value(self):
        """Getter behavior."""
        return 1
    @value.setter
    def value(self, value):
        """Setter behavior."""
        pass
def _internal(): pass
''', encoding="utf-8")
    factory = root / "factory.py"
    factory.write_text('def make_line(first, last=None):\n    """Create a line."""\n    return None\n', encoding="utf-8")
    output = root / "references/python-api"
    result = build(root, output, {"Draft": source, "factory": factory})
    module = (output / "Draft/index.md").read_text(encoding="utf-8")
    shape = (output / "Draft/Shape.md").read_text(encoding="utf-8")
    assert "from factory import make_line as makeLine" in module
    assert "Draft.makeLine" in module and "factory.make_line" in module
    assert "Source module `factory`" in module and "Facade reexport declaration" in module
    assert "if App.GuiUp" in module and "else of (App.GuiUp)" in module
    assert "try block at line" in module and "except ImportError" in module
    assert "def old(value, /, *, option=True):" in module
    assert "deprecated_in='26.3'" in module and "removed_in='28.3'" in module
    assert "Legacy function purpose." in module and "listed in literal __all__" in module
    assert "Export declaration evidence" in module and "__all__ = ['makeLine', 'Shape', 'old']" in module
    assert "Internal definitions not expanded" in module and "Draft._internal" in module
    assert "class Shape(Base):" in shape and "Shape purpose." in shape
    assert "Getter behavior." in shape and "Setter behavior." in shape and "@value.setter" in shape
    assert result["modules"] == 2 and result["classes"] == 1
    node = ast.parse("from .helper import value").body[0]
    assert import_target("package", node, is_package=True) == "package.helper"
    assert import_target("package.module", node) == "package.helper"
    assert exports(ast.parse('__all__ = ["first"]\nif GuiUp:\n    __all__ = ["second"]')) is None
    assert exports(ast.parse('__all__ = ["first"]\n__all__.extend(extra)')) is None
print("Python-source catalogue check passed.")
