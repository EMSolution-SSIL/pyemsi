"""Render portable API references from FreeCAD's existing public stub generator.

Run from any directory with --root pointing at a FreeCAD checkout. No FreeCAD
runtime or third-party Python packages are imported.
"""

from __future__ import annotations

import argparse
import ast
import copy
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import sys
import uuid


SKILL = Path(__file__).resolve().parents[1]
MAX_PAGE_CHARS = 24000


@contextmanager
def temporary_workspace():
    # Normal mkdir permissions work with Windows workspace sandboxes; Python's
    # tempfile mode-0700 directories can be inaccessible in those environments.
    parent = SKILL / "scripts"
    path = parent / ("freecad-reference-temp-" + uuid.uuid4().hex)
    if not path.resolve().is_relative_to(parent.resolve()):
        raise ValueError("Temporary path escaped the owned scripts directory")
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def flatten(body):
    """The public generator can retain typing-only conditional declarations."""
    for node in body:
        if isinstance(node, ast.If):
            if ast.unparse(node.test) not in {"TYPE_CHECKING", "typing.TYPE_CHECKING"}:
                raise ValueError(f"Unsupported conditional at stub line {node.lineno}: {ast.unparse(node.test)}")
            yield from flatten(node.body)
            yield from flatten(node.orelse)
        else:
            yield node


def classes(body, prefix=""):
    for node in flatten(body):
        if isinstance(node, ast.ClassDef):
            name = prefix + node.name
            yield name, node
            yield from classes(node.body, name + ".")


def declaration(node):
    result = copy.deepcopy(node)
    if isinstance(result, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        result.body = [ast.Expr(ast.Constant(Ellipsis))]
    text = ast.unparse(result)
    if isinstance(result, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        text = text.rsplit("\n", 1)[0]
    return text


def symbol_name(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name
    if isinstance(node, ast.AnnAssign):
        return ast.unparse(node.target)
    if isinstance(node, ast.Assign):
        return ", ".join(ast.unparse(target) for target in node.targets)
    return None


def entries(body, owner, stub):
    """Keep overloads and getter/setter pairs together, with adjacent field docs."""
    nodes = list(flatten(body))
    groups = {}
    for i, node in enumerate(nodes):
        name = symbol_name(node)
        if name is None or isinstance(node, ast.ClassDef):
            continue
        doc = ast.get_docstring(node) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else None
        if doc is None and i + 1 < len(nodes):
            following = nodes[i + 1]
            if isinstance(following, ast.Expr) and isinstance(following.value, ast.Constant) and isinstance(following.value.value, str):
                doc = following.value.value
        groups.setdefault(name, []).append((node, doc))
    rendered = []
    for name, group in groups.items():
        code = "\n\n".join(declaration(node) for node, _ in group)
        docs = list(dict.fromkeys(doc for _, doc in group if doc))
        text = f"## `{owner}.{name}`\n\n```python\n{code}\n```\n\n"
        if docs:
            text += "\n\n".join(docs) + "\n\n"
        else:
            text += "Purpose/behavior undocumented in this stub; consult the implementation before relying on it.\n\n"
        decorators = [ast.unparse(d) for node, _ in group for d in getattr(node, "decorator_list", [])]
        if "property" in decorators:
            access = "getter and setter declared" if any(d.endswith(".setter") for d in decorators) else "getter only declared"
            text += f"Access: {access} in the stub.\n\n"
        elif any(isinstance(node, ast.AnnAssign) for node, _ in group):
            text += "Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.\n\n"
        if any(isinstance(item, ast.Name) and item.id == "Any" for node, _ in group for item in ast.walk(node)):
            text += "Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.\n\n"
        if any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.args.defaults + [d for d in node.args.kw_defaults if d] for node, _ in group):
            if "..." in code:
                text += "A default shown as `...` is unspecified by the stub; it is not a value to pass.\n\n"
        text += f"Evidence: public stub `{stub}` line(s) {', '.join(str(node.lineno) for node, _ in group)}.\n\n"
        rendered.append(text)
    return rendered


def chunks(sections, header):
    pages = []
    current = header
    for section in sections:
        if len(current) + len(section) > MAX_PAGE_CHARS and current != header:
            pages.append(current)
            current = header
        current += section
    pages.append(current)
    return pages


def write_pages(directory, stem, sections, header, links):
    pages = chunks(sections, header)
    paths = []
    for i, content in enumerate(pages, 1):
        filename = f"{stem}.md" if i == 1 else f"{stem}-{i}.md"
        path = directory / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        if len(pages) > 1:
            navigation = " | ".join(f"[part {n}]({stem + ('-' + str(n) if n > 1 else '')}.md)" for n in range(1, len(pages) + 1))
            content = header + navigation + "\n\n" + content[len(header):]
        path.write_text(content, encoding="utf-8")
        links.append(path)
        paths.append(path)
    return paths


def module_name(path):
    parts = list(path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def build(stubs, out, root, fresh=False):
    """Write only the script-owned catalogue; supplied stubs remain read-only."""
    paths = sorted(stubs.rglob("*.pyi"))
    if not paths:
        raise ValueError("No .pyi files in --stubs-dir")
    digest = hashlib.sha256()
    links = []
    module_links = []
    class_links = []
    for path in paths:
        relative = path.relative_to(stubs)
        data = path.read_bytes()
        digest.update(relative.as_posix().encode() + b"\0" + data)
        tree = ast.parse(data.decode("utf-8-sig"), filename=relative.as_posix())
        module = module_name(relative)
        directory = out / Path(*module.split("."))
        body = list(flatten(tree.body))
        imports = [ast.unparse(node) for node in body if isinstance(node, (ast.Import, ast.ImportFrom))]
        header = f"# `{module}`\n\n[Catalogue index]({'../' * len(module.split('.'))}index.md)\n\n"
        header += f"Evidence: import-shaped public stub `{relative.as_posix()}`; generated binding/typing declarations, runtime unverified.\n\n"
        if ast.get_docstring(tree):
            header += ast.get_docstring(tree) + "\n\n"
        class_nodes = [node for node in body if isinstance(node, ast.ClassDef)]
        overview = "## Classes\n\n" + "".join(f"- [{module}.{node.name}]({node.name}.md)\n" for node in class_nodes) + "\n" if class_nodes else ""
        import_section = "## Imports and aliases\n\nThese preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.\n\n```python\n" + "\n".join(imports) + "\n```\n\n" if imports else ""
        written = write_pages(directory, "index", [overview, import_section] + entries(body, module, relative.as_posix()), header, links)
        module_links.append((module, written))
        for local_name, node in classes(body):
            name = f"{module}.{local_name}"
            class_header = f"# `{name}`\n\n[Module](index.md)\n\n```python\n{declaration(node)}\n```\n\n"
            class_header += (ast.get_docstring(node) or "Class purpose undocumented in this stub.") + "\n\n"
            class_header += f"Evidence: public stub `{relative.as_posix()}` line {node.lineno}. Inherited members are on the named base's reference; aliases keep their imported identity.\n\n"
            if node.name.startswith("_"):
                class_header += "Underscored typing/support name: verify runtime exposure and support status before using it.\n\n"
            nested = "".join(f"- [{name}.{child.name}]({local_name}.{child.name}.md)\n" for child in flatten(node.body) if isinstance(child, ast.ClassDef))
            sections = (["## Nested classes\n\n" + nested + "\n"] if nested else []) + entries(node.body, name, relative.as_posix())
            written = write_pages(directory, local_name, sections, class_header, links)
            class_links.append((name, written))
    try:
        revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        revision = "unavailable"
    version = json.loads((root / "version.json").read_text(encoding="utf-8"))
    release = ".".join(str(version[f"version_{key}"]) for key in ("major", "minor", "patch"))
    if version.get("version_suffix"):
        release += "-" + version["version_suffix"]
    provenance = "Fresh stubs generated from this checkout in this run." if fresh else "Supplied stubs: original checkout revision/version unverified. The checkout metadata below does not prove that these stubs match it."
    index = f"# Generated API catalogue\n\n{provenance}\n\nCheckout HEAD: `{revision}`. Checkout version: `{release}`. Local source changes are not represented by the HEAD identifier.\n\nStub content SHA-256: `{digest.hexdigest()}`. Inputs: {len(paths)} `.pyi` files; rendered {len(module_links)} modules and {len(class_links)} classes.\n\n"
    index += "## Reading limits\n\n- Public module names here are stub-emitted/source-discovered, not verified imports in an installed FreeCAD. Optional builds can differ.\n- Signatures, decorators, documentation, inheritance and aliases are copied from stubs. Source-to-symbol implementation mappings are not inferred. Evidence locations refer to the stub input tree.\n- `Any`, undocumented entries, typing-only helpers and unspecified defaults require implementation/runtime checks. No exception, unit, side-effect or writable-property contract is inferred when absent.\n- Dynamic document properties omitted by the existing generator and pure Python workbench packages require source inspection. See [modeling guidance](../modeling-api.md).\n- Generated docs preserve upstream descriptions, including limitations and legacy syntax. Examples and runtime behavior have not been exercised by this renderer.\n\n"
    index += "## Maintenance\n\nFrom the checkout root (Python 3.10+):\n\n```sh\npython -B contrib/skills/freecad-addon-api/scripts/build_references.py --root .\n# Reuse an import-shaped stubs directory, without changing it:\npython -B contrib/skills/freecad-addon-api/scripts/build_references.py --root . --stubs-dir path/to/stubs\npython -B contrib/skills/freecad-addon-api/scripts/test_build_references.py\n```\n\nFresh generation invokes `src/Tools/typing/generate_stubs.py` in a temporary directory. Only the catalogue under `references/api/` is maintained by this script.\n\n"
    for title, catalogue in (("Modules", module_links), ("Classes", class_links)):
        index += f"## {title}\n\n"
        for name, pages in catalogue:
            index += f"- `{name}`: " + ", ".join(f"[{'reference' if i == 0 else 'part ' + str(i + 1)}]({page.relative_to(out).as_posix()})" for i, page in enumerate(pages)) + "\n"
        index += "\n"
    (out / "index.md").write_text(index, encoding="utf-8")
    links.append(out / "index.md")
    manifest_path = out / "manifest.json"
    previous = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    current = {path.relative_to(out).as_posix() for path in links}
    # Remove only previously listed Markdown pages inside the fixed owned output.
    for obsolete in set(previous.get("pages", [])) - current:
        target = (out / obsolete).resolve()
        if target.is_relative_to(out.resolve()) and target.suffix == ".md" and target.is_file():
            target.unlink()
    metadata = {"checkout_revision": revision, "checkout_version": release, "stub_provenance": provenance, "stub_sha256": digest.hexdigest(), "stub_files": len(paths), "modules": len(module_links), "classes": len(class_links), "pages": sorted(current)}
    manifest_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--stubs-dir", type=Path, help="Existing import-shaped public stub tree; remains read-only")
    args = parser.parse_args()
    root = args.root.resolve()
    output = SKILL / "references" / "api"
    # No arbitrary output/cleanup argument. Refuse links redirecting the owned tree.
    if output.resolve() != output or output.is_symlink():
        parser.error("references/api must be an ordinary directory inside this skill")
    if args.stubs_dir:
        stubs = args.stubs_dir if args.stubs_dir.is_absolute() else root / args.stubs_dir
        result = build(stubs.resolve(), output, root)
    else:
        with temporary_workspace() as temporary:
            generated = temporary / "generated"
            subprocess.run([sys.executable, "-B", str(root / "src/Tools/typing/generate_stubs.py"), "--root", str(root), "--out-dir", str(generated)], check=True)
            result = build(generated / "stubs", output, root, fresh=True)
    print(f"Rendered {result['modules']} modules, {result['classes']} classes, {len(result['pages'])} Markdown pages.")


if __name__ == "__main__":
    main()
