"""Runnable stdlib check for signature fidelity, provenance and safe cleanup."""

import json
from pathlib import Path
import re

from build_references import build, temporary_workspace


with temporary_workspace() as temporary:
    root = Path(temporary)
    (root / "version.json").write_text(json.dumps({"version_major": 1, "version_minor": 2, "version_patch": 3}), encoding="utf-8")
    stubs = root / "stubs"
    (stubs / "Part").mkdir(parents=True)
    (stubs / "Part/__init__.pyi").write_text('''from typing import Any, overload, Final
from FreeCAD.Base import Vector as Vector
Alias = Vector
def makeBox(length: float, /, *, option: bool = ...) -> Any:
    """Build a box."""
    ...
class Shape(Base):
    """Shape documentation."""
    @overload
    def copy(self, deep: bool, /) -> Shape: ...
    @overload
    def copy(self) -> Shape: ...
    @property
    def value(self) -> int: ...
    @value.setter
    def value(self, value: str | int) -> None: ...
    label: Final[str]
    """Attribute documentation."""
    def unknown(self, *args: Any, **kwargs: Any) -> Any: ...
    class Mode:
        one: int
''', encoding="utf-8")
    output = root / "api"
    metadata = build(stubs, output, root)
    module = (output / "Part/index.md").read_text(encoding="utf-8")
    shape = (output / "Part/Shape.md").read_text(encoding="utf-8")
    assert "length: float, /, *, option: bool=..." in module
    assert "Alias = Vector" in module and "Vector as Vector" in module
    assert "Build a box." in module and "Typing limit" in module
    assert shape.count("@overload") == 2 and shape.count("## `Part.Shape.copy`") == 1
    assert "getter and setter declared" in shape and "@value.setter" in shape
    assert "Attribute documentation." in shape and "runtime writability" in shape
    assert "class Shape(Base):" in shape and "Purpose/behavior undocumented" in shape
    assert (output / "Part/Shape.Mode.md").is_file() and "Shape.Mode" in shape
    assert "original checkout revision/version unverified" in metadata["stub_provenance"]
    outside = root / "keep.md"
    outside.write_text("keep", encoding="utf-8")
    stale = output / "stale.md"
    stale.write_text("obsolete", encoding="utf-8")
    metadata["pages"] += ["stale.md", "../keep.md"]
    (output / "manifest.json").write_text(json.dumps(metadata), encoding="utf-8")
    build(stubs, output, root)
    assert not stale.exists() and outside.read_text(encoding="utf-8") == "keep"
    for page in output.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
            if target.endswith(".md") and target != "../modeling-api.md":
                assert (page.parent / target).is_file(), (page, target)
    assert metadata["modules"] == 1 and metadata["classes"] == 2
print("Reference rendering check passed.")
