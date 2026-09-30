"""Catalogue selected Python addon APIs without executing workbench code.

Selection is explicit: useful entry points and source reexports, not all GUI,
test or implementation modules. Uses the binding renderer's shared formatting.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess

from build_references import SKILL, declaration, module_name, symbol_name, write_pages


# Import paths are relative to each workbench's Python search directory.
SEEDS = {
    "Draft": ["Draft.py", "DraftGeomUtils.py", "DraftVecUtils.py", "WorkingPlane.py", "draftmake/*.py", "draftfunctions/*.py", "draftgeoutils/*.py"],
    "BIM": ["Arch.py"],
    "Part": ["BasicShapes/*.py", "BOPTools/*.py", "CompoundTools/*.py"],
    "Fem": ["ObjectsFem.py", "femtools/femutils.py", "femtools/membertools.py", "femtools/objecttools.py", "femtools/geomtools.py", "femmesh/meshtools.py", "femmesh/femmesh2mesh.py", "femresult/resulttools.py"],
    "TechDraw": ["TechDrawTools/*.py"],
    "Sketcher": ["ProfileLib/*.py"],
    "CAM": ["Path/__init__.py", "Path/Geom.py", "Path/Log.py", "Path/Base/Util.py", "Path/Main/Job.py", "Path/Main/Stock.py", "Path/Op/Util.py", "Path/Tool/Controller.py"],
}
FACADES = {"Draft", "DraftGeomUtils", "Arch"}
METHOD_DUNDERS = {"__init__", "__call__", "__iter__", "__next__", "__getitem__", "__setitem__", "__len__", "__enter__", "__exit__", "__getstate__", "__setstate__"}


def scoped(body, guards=()):
    """Visit declarations in module/class scopes while retaining branch guards."""
    for node in body:
        if isinstance(node, ast.If):
            condition = ast.unparse(node.test)
            yield from scoped(node.body, guards + (f"if {condition}",))
            yield from scoped(node.orelse, guards + (f"else of ({condition})",))
        elif isinstance(node, (ast.Try, getattr(ast, "TryStar", ast.Try))):
            yield from scoped(node.body, guards + (f"try block at line {node.lineno}",))
            for handler in node.handlers:
                condition = ast.unparse(handler.type) if handler.type else "any exception"
                yield from scoped(handler.body, guards + (f"except {condition} at line {handler.lineno}",))
            yield from scoped(node.orelse, guards + (f"try-success else at line {node.lineno}",))
            yield from scoped(node.finalbody, guards + (f"finally at line {node.lineno}",))
        elif isinstance(node, (ast.With, ast.For, ast.While)):
            yield from scoped(node.body, guards + (f"dynamic {type(node).__name__} block at line {node.lineno}",))
            yield from scoped(getattr(node, "orelse", []), guards + (f"dynamic block else at line {node.lineno}",))
        else:
            yield node, guards


def exports(tree):
    declarations = list(scoped(tree.body))
    assignments = [(node, guards) for node, guards in declarations if symbol_name(node) == "__all__"]
    if len(assignments) != 1 or assignments[0][1]:
        return None
    for node, _ in declarations:
        if isinstance(node, ast.AugAssign) and ast.unparse(node.target) == "__all__":
            return None
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and ast.unparse(node.value.func.value) == "__all__":
            return None
    names = []
    for node, _ in assignments:
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            return None
        if not isinstance(value, (list, tuple)) or not all(isinstance(item, str) for item in value):
            return None
        names.extend(value)
    return set(names)


def import_target(module, node, is_package=False):
    if not node.level:
        return node.module or ""
    package = module.split(".") if is_package else module.split(".")[:-1]
    return ".".join(package[:len(package) - node.level + 1] + ([node.module] if node.module else []))


def source_inventory(root):
    candidates = {}
    selected = {}
    for workbench in (root / "src/Mod").iterdir():
        if not workbench.is_dir():
            continue
        for path in workbench.rglob("*.py"):
            name = module_name(path.relative_to(workbench))
            candidates.setdefault(name, []).append(path)
        for pattern in SEEDS.get(workbench.name, []):
            for path in workbench.glob(pattern):
                selected[module_name(path.relative_to(workbench))] = path
    for path in (root / "src/Ext/freecad").glob("*.py"):
        name = "freecad." + path.stem
        candidates.setdefault(name, []).append(path)
        selected[name] = path
    template = root / "src/Ext/freecad/__init__.py.template"
    selected["freecad"] = template
    candidates["freecad"] = [template]
    known = {name: values[0] for name, values in candidates.items() if len(values) == 1}
    # Facades intentionally reexport functions/classes. Follow their source module
    # declarations once; do not recursively pull ordinary dependency imports.
    for module in FACADES:
        path = selected.get(module)
        if not path:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node, _ in scoped(tree.body):
            if isinstance(node, ast.ImportFrom):
                target = import_target(module, node)
                if target in known:
                    selected.setdefault(target, known[target])
    return selected


def notes(guards):
    return "Conditions: " + "; ".join(f"`{guard}`" for guard in guards) + ".\n\n" if guards else ""


def entries(body, owner, source, all_names=None, class_scope=False):
    nodes = list(scoped(body))
    sections = []
    private = []
    count = 0
    for i, (node, guards) in enumerate(nodes):
        name = symbol_name(node)
        if not name or isinstance(node, ast.ClassDef):
            continue
        if name.startswith("_") and name not in (all_names or ()) and not (class_scope and name in METHOD_DUNDERS):
            private.append(name)
            continue
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.AnnAssign, ast.Assign)):
            continue
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and not isinstance(getattr(node, "value", None), (ast.Name, ast.Attribute, ast.Constant, ast.Tuple, ast.List, type(None))) and not class_scope:
            # Keep explicit aliases and constants; large computed runtime state is
            # source evidence, not an inferred exported API contract.
            continue
        code = declaration(node)
        if len(code) > 1600:
            code = code[:1600] + "\n# Remaining expression omitted; inspect source."
        doc = ast.get_docstring(node) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else None
        if not doc and i + 1 < len(nodes):
            following = nodes[i + 1][0]
            if isinstance(following, ast.Expr) and isinstance(following.value, ast.Constant) and isinstance(following.value.value, str):
                doc = following.value.value
        status = "listed in literal __all__" if name in (all_names or ()) else "source-defined name; no independently verified stability/export guarantee"
        section = f"## `{owner}.{name}`\n\nStatus: {status}.\n\n" + notes(guards)
        section += f"```python\n{code}\n```\n\n" + (doc or "No source docstring; inspect implementation and callers for purpose, return values and side effects.") + "\n\n"
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            count += 1
            if node.returns is None or any(arg.annotation is None for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs if arg.arg not in {"self", "cls"}):
                section += "Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.\n\n"
        section += f"Evidence: `{source}:{node.lineno}`. Decorators are copied as source expressions and have not been executed.\n\n"
        sections.append(section)
    if private:
        sections.append("## Internal definitions not expanded\n\n" + ", ".join(f"`{owner}.{name}`" for name in dict.fromkeys(private)) + ". These are source internals unless an explicit export establishes otherwise.\n\n")
    return sections, count


def relative_link(directory, target):
    return Path(os.path.relpath(target, directory)).as_posix()


def build(root, out, selected=None):
    selected = source_inventory(root) if selected is None else selected
    links = []
    listing = []
    digest = hashlib.sha256()
    functions = classes_count = import_count = 0
    sources = {}
    for module, path in sorted(selected.items()):
        source = path.relative_to(root).as_posix()
        data = path.read_bytes()
        digest.update(source.encode() + b"\0" + data)
        tree = ast.parse(data.decode("utf-8-sig"), filename=source)
        all_names = exports(tree)
        directory = out / Path(*module.split("."))
        header = f"# Python source module `{module}`\n\n[Python catalogue]({relative_link(directory, out / 'index.md')})\n\nEvidence: `{source}`. Import path is source-routed; installed availability is unverified.\n\n"
        if ast.get_docstring(tree):
            header += ast.get_docstring(tree) + "\n\n"
        header += "Literal `__all__`: " + (", ".join(f"`{name}`" for name in sorted(all_names)) if all_names is not None else "not available; source names do not imply supported public API") + ".\n\n"
        imports = []
        for node, guards in scoped(tree.body):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            import_count += len(node.names)
            target = import_target(module, node, path.name.startswith("__init__.py")) if isinstance(node, ast.ImportFrom) else ""
            support_import = target.startswith(("typing", "freecad.deprecation", "FreeCAD", "PySide", "collections"))
            status = "Facade reexport declaration" if module in FACADES and isinstance(node, ast.ImportFrom) and not support_import else "Module-scope import; may be a dependency rather than supported addon API"
            text = "### " + ast.unparse(node).replace("\n", " ") + "\n\n" + status + ".\n\n" + notes(guards)
            for alias in node.names:
                if alias.name == "*":
                    continue
                if isinstance(node, ast.ImportFrom):
                    local = alias.asname or alias.name
                    origin = target + "." + alias.name
                else:
                    local = alias.asname or alias.name.split(".")[0]
                    origin = alias.name
                export_note = " Listed in literal __all__." if local in (all_names or ()) else ""
                text += f"Bound source name `{module}.{local}` -> `{origin}`.{export_note}\n\n"
            if target in selected:
                target_path = out / Path(*target.split(".")) / "index.md"
                text += f"[Source module `{target}`]({relative_link(directory, target_path)}).\n\n"
            else:
                text += "Target not expanded in this selected Python catalogue; check the binding catalogue or source.\n\n"
            if any(alias.name == "*" for alias in node.names):
                text += "Wildcard export is retained as a wildcard. Its full runtime member set is not inferred; inspect the target's export declarations and initialization.\n\n"
            text += f"Evidence: `{source}:{node.lineno}`.\n\n"
            imports.append(text)
        definitions, count = entries(tree.body, module, source, all_names)
        functions += count
        sections = (["## Imports, aliases and conditional reexports\n\n"] + imports if imports else [])
        for node, guards in scoped(tree.body):
            export_statement = symbol_name(node) == "__all__"
            export_statement |= isinstance(node, ast.AugAssign) and ast.unparse(node.target) == "__all__"
            export_statement |= isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and ast.unparse(node.value.func.value) == "__all__"
            if export_statement:
                sections.append("## Export declaration evidence\n\n" + notes(guards) + f"```python\n{ast.unparse(node)}\n```\n\nEvidence: `{source}:{node.lineno}`. Conditional/dynamic alternatives have not been evaluated.\n\n")
        class_sections = []
        for node, guards in scoped(tree.body):
            if not isinstance(node, ast.ClassDef):
                continue
            if node.name.startswith("_") and node.name not in (all_names or ()):
                class_sections.append(f"Internal class `{module}.{node.name}` at `{source}:{node.lineno}` is not expanded.\n\n")
                continue
            classes_count += 1
            name = module + "." + node.name
            class_header = f"# `{name}`\n\n[Source module](index.md)\n\n" + notes(guards) + f"```python\n{declaration(node)}\n```\n\n" + (ast.get_docstring(node) or "No class source docstring.") + "\n\n"
            class_header += f"Evidence: `{source}:{node.lineno}`. Source-defined class; runtime behavior and support status unverified.\n\n"
            members, count = entries(node.body, name, source, class_scope=True)
            functions += count
            written = write_pages(directory, node.name, members, class_header, links)
            class_sections.append(f"- [{name}]({written[0].name})\n")
        sections += (["## Classes\n\n" + "".join(class_sections) + "\n"] if class_sections else []) + definitions
        written = write_pages(directory, "index", sections, header, links)
        listing.append((module, source, written))
        sources[module] = source
    revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip() if (root / ".git").exists() else "unavailable"
    index = f"# Python-defined addon API catalogue\n\nCheckout HEAD: `{revision}`; local source changes are not encoded in that identifier. Selected-source SHA-256: `{digest.hexdigest()}`.\n\n{len(selected)} source modules; {classes_count} expanded classes; {functions} function/method declarations; {import_count} module-scope import/alias declarations.\n\n"
    index += "## Scope and limits\n\nThis source-only catalogue supplements the [binding catalogue](../api/index.md). [Selection and usage guide](../python-api-guide.md). It does not import FreeCAD, run decorators, resolve dynamic/conditional `__all__`, expand wildcard imports, or verify installed paths. Signatures, docstrings, guards, aliases and lifecycle decorators are copied from source. Facade reexports, literal export lists, other source-defined names and private internals are distinguished. Imported dependencies and public-looking source names are not automatically supported API.\n\nSelection: Draft facades/factories/operations/geometry plus their direct reexport source modules; all `src/Ext/freecad` modules including the namespace initializer template; Arch facade and direct star-import sources; selected Part shape, FEM creation/geometry/mesh/result, TechDraw, Sketcher profile and CAM Path helpers. Unrelated GUI/test internals and arbitrary transitive dependencies are omitted. Included GUI command modules/reexports still require appropriate GUI availability. Nested classes, function-local definitions, dynamically attached APIs and dynamic runtime property contracts are not inventoried. Unannotated arguments/returns remain unspecified.\n\n## Maintenance\n\n```sh\npython -B contrib/skills/freecad-addon-api/scripts/build_python_api.py --root .\npython -B contrib/skills/freecad-addon-api/scripts/test_build_python_api.py\n```\n\nOnly this script's generated `references/python-api/` pages listed in its manifest are cleaned up. Improve Python source documentation before regenerating; retain curated usage guidance outside the generated tree.\n\n## Modules\n\n"
    for module, source, pages in listing:
        index += f"- `{module}` ({source}): " + ", ".join(f"[part {i + 1}]({page.relative_to(out).as_posix()})" for i, page in enumerate(pages)) + "\n"
    (out / "index.md").write_text(index, encoding="utf-8")
    links.append(out / "index.md")
    manifest_path = out / "manifest.json"
    previous = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    current = {path.relative_to(out).as_posix() for path in links}
    for obsolete in set(previous.get("pages", [])) - current:
        target = (out / obsolete).resolve()
        if target.is_relative_to(out.resolve()) and target.suffix == ".md" and target.is_file():
            target.unlink()
    result = {"revision": revision, "source_sha256": digest.hexdigest(), "modules": len(selected), "classes": classes_count, "function_declarations": functions, "import_alias_declarations": import_count, "sources": sources, "pages": sorted(current)}
    manifest_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    out = SKILL / "references/python-api"
    if out.resolve() != out or out.is_symlink():
        parser.error("references/python-api must be an ordinary directory inside this skill")
    result = build(args.root.resolve(), out)
    print(f"Python catalogue: {result['modules']} modules, {result['classes']} classes, {result['function_declarations']} functions/methods, {len(result['pages'])} pages.")


if __name__ == "__main__":
    main()
