"""Check native property preservation, inherited links, and bounded cleanup."""

import json
from pathlib import Path
import re

from build_object_types import CHECKOUT, build, source_review
from build_references import temporary_workspace


with temporary_workspace() as temporary:
    output = Path(temporary) / "object-types"
    metadata = build(CHECKOUT, output)
    box = (output / "Part/Box.md").read_text(encoding="utf-8")
    assert "Part::Box" in box and "../Part/Primitive.md" in box
    assert all(f"`{name}`" in box for name in ("Length", "Width", "Height"))
    assert "App::PropertyLength" in box and "Base.Quantity" in box
    assert "unresolved direct binding association" in box
    assert "`Shape`" in (output / "Part/Feature.md").read_text(encoding="utf-8")
    assert metadata["properties"] > 1000 and metadata["document_types"] > 100
    assert metadata["unresolved_property_conversions"] == 43
    assert metadata["source_reviewed_property_conversions"] == 43
    assert metadata["remaining_unreviewed_property_conversions"] == 0
    assert metadata["build_conditional_property_conversions"] == 1
    assert metadata["unsupported_python_property_conversions"] == 1
    assert not metadata["changed_review_evidence"]
    audit = (output / "conversion-review.md").read_text(encoding="utf-8")
    assert "object (ignored)" in audit and "raises NotImplementedError" in audit
    assert "PrimitivePy" in box and "Closest discovered ancestor binding" in box
    property_rows = sum(line.startswith("| `") for page in output.rglob("*.md") for line in page.read_text(encoding="utf-8").splitlines())
    assert property_rows == metadata["properties"]
    wrapper_rows = sum(line.startswith("| [") for page in output.glob("*/wrapper-review.md") for line in page.read_text(encoding="utf-8").splitlines())
    assert wrapper_rows == metadata["owners_without_direct_binding"]
    missing_root = Path(temporary) / "missing-evidence-root"
    missing_root.mkdir()
    _, withheld, changed = source_review(missing_root)
    assert changed and not withheld["property_contracts"] and not withheld["wrapper_implementations"]
    outside = Path(temporary) / "keep.md"
    outside.write_text("keep", encoding="utf-8")
    stale = output / "stale.md"
    stale.write_text("stale", encoding="utf-8")
    metadata["pages"] += ["stale.md", "../keep.md"]
    (output / "manifest.json").write_text(json.dumps(metadata), encoding="utf-8")
    build(CHECKOUT, output)
    assert not stale.exists() and outside.read_text(encoding="utf-8") == "keep"
    for page in output.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
            if target in {"../object-types.md", "../core-api.md", "../runtime-validation.md"}:
                continue  # Curated guides are outside this isolated output.
            assert (page.parent / target).is_file(), (page, target)
print("Native object/property catalogue check passed.")
