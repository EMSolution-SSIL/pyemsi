"""Render native TypeIds and C++ properties using FreeCAD's existing discovery.

The command writes only references/object-types beside this script. It does not
import a FreeCAD runtime or implement another C++ scanner.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import sys


SKILL = Path(__file__).resolve().parents[1]
CHECKOUT = SKILL.parents[2]


@lru_cache(maxsize=1)
def discover(root):
    sys.path.insert(0, str(root / "src/Tools/typing"))
    from stubgen.cpp_properties import discover_cpp_properties
    from stubgen.discovery import collect_type_registrations
    from stubgen.document_object_types import direct_python_types
    from stubgen.parsing import load_source_files
    from stubgen.property_contracts import load_property_catalog, property_contract
    from stubgen.source_inputs import collect_binding_classes
    from stubgen.type_hierarchy import discover_type_hierarchy

    hierarchy = discover_type_hierarchy(root)
    diagnostics = []
    properties = discover_cpp_properties(root, hierarchy, diagnostics)
    registrations = collect_type_registrations(root, load_source_files(root, root / "src"))
    classes = collect_binding_classes(root, root / "src", registrations)
    # Only direct source binding associations: do not guess inherited wrappers.
    selected = {native for native in hierarchy.nodes if hierarchy.is_derived_from(native, "App::DocumentObject")}
    selected.update(prop.owner_type_id for prop in properties)
    selected.update(issue.owner_type_id for issue in diagnostics if issue.owner_type_id in hierarchy.nodes)
    wrappers = direct_python_types(classes, type_ids=selected)
    catalog = load_property_catalog(root)
    contracts = {}
    for native in {prop.property_type_id for prop in properties}:
        try:
            contracts[native] = property_contract(native, hierarchy, catalog)
        except KeyError:
            contracts[native] = None
    return hierarchy, properties, diagnostics, wrappers, contracts, catalog


def type_path(native):
    parts = native.split("::")
    return Path(parts[0] if len(parts) > 1 else "unqualified", ".".join(parts[1:] or parts) + ".md")


def md_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


@lru_cache(maxsize=1)
def source_review(root):
    """Apply exact-TypeId manual reviews only while their evidence still matches."""
    review = json.loads((SKILL / "references/object-types/source-review.json").read_text(encoding="utf-8"))
    changed = set()
    for source, expected in review["source_hashes"].items():
        path = (root / source).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            changed.add(source)
    valid = {}
    for section in ("property_contracts", "wrapper_implementations"):
        valid[section] = {native: item for native, item in review[section].items() if not any(source.split(":")[0] in changed for source in item["sources"])}
    return review, valid, changed


def write(out, relative, content, pages):
    path = out / relative
    if path.resolve() != path.absolute():
        raise ValueError(f"Refusing redirected output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    pages.add(Path(relative).as_posix())


def build(root, out):
    hierarchy, properties, diagnostics, wrappers, contracts, catalog = discover(root)
    review, valid, changed = source_review(root)
    write(out, "source-review.json", json.dumps(review, indent=2) + "\n", set())
    reviewed = valid["property_contracts"]
    implementations = valid["wrapper_implementations"]
    by_owner = defaultdict(list)
    for prop in properties:
        by_owner[prop.owner_type_id].append(prop)
    issues_by_owner = defaultdict(list)
    for issue in diagnostics:
        issues_by_owner[issue.owner_type_id].append(issue)
    documents = {native for native in hierarchy.nodes if hierarchy.is_derived_from(native, "App::DocumentObject")}
    selected = documents | set(by_owner) | (set(issues_by_owner) & set(hierarchy.nodes))
    namespaces = defaultdict(list)
    wrapper_gaps = defaultdict(list)
    pages = set()
    for native in sorted(selected):
        node = hierarchy.nodes[native]
        relative = type_path(native)
        namespace = relative.parts[0]
        namespaces[namespace].append(native)
        text = f"# `{native}`\n\n[Namespace index](index.md) | [Catalogue index](../index.md)\n\n"
        category = "DocumentObject descendant" if native in documents else "Other native property owner; not a Document.addObject type"
        text += f"Category: {category}. Registration: `{node.source}:{node.line}`. Abstract macro: {'yes' if node.is_abstract else 'no'}.\n\n"
        if node.parent:
            parent = type_path(node.parent)
            target = f"../{parent.as_posix()}"
            text += f"Native parent: [{node.parent}]({target}). Read the parent record for inherited properties.\n\n" if node.parent in selected else f"Native parent: `{node.parent}` (outside this document/property-owner inventory).\n\n"
        wrapper = wrappers.get(native)
        text += f"Direct binding association: `{wrapper.qualified_name}`. This is a source binding name, not a runtime wrapper check.\n\n" if wrapper else "Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.\n\n"
        if wrapper is None:
            chain = hierarchy.chain(native)
            ancestor = next((item for item in chain[1:] if item in wrappers), None)
            implementation = next((item for item in chain if item in implementations), None)
            text += "[Wrapper association audit](wrapper-review.md).\n\n"
            if ancestor:
                text += f"Closest discovered ancestor binding: `{ancestor}` -> `{wrappers[ancestor].qualified_name}`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.\n\n"
            if implementation:
                evidence = implementations[implementation]
                text += f"Reviewed implementation context at `{implementation}`: {evidence['note']} Evidence: " + ", ".join(f"`{source}`" for source in evidence["sources"]) + ". Descendant getPyObject overrides and PythonObject replacement can change the returned value.\n\n"
            else:
                text += "No manually verified getPyObject implementation context in this native chain; inspect its declaration/implementation or target runtime.\n\n"
            wrapper_gaps[namespace].append((native, ancestor, implementation))
        text += "## Properties registered for this owner\n\n"
        direct = sorted(by_owner[native], key=lambda prop: prop.property_name)
        if direct:
            text += "| Name | Native property TypeId | Getter contract | Setter contract | Documentation | Source |\n| --- | --- | --- | --- | --- | --- |\n"
            for prop in direct:
                contract = contracts[prop.property_type_id]
                getter = f"`{contract.getter}`" if contract else "Unresolved conversion"
                setter = f"`{contract.setter}`" if contract and contract.setter else "No setter declared" if contract else "Unresolved conversion"
                if contract is None and prop.property_type_id in reviewed:
                    item = reviewed[prop.property_type_id]
                    getter = item["getter"] + " (source review)"
                    setter = item["setter"] + " (source review)"
                row = [f"`{prop.property_name}`", f"`{prop.property_type_id}`", getter, setter, prop.documentation or "Not documented by registration", f"`{prop.source}:{prop.line}`"]
                text += "| " + " | ".join(md_cell(cell) for cell in row) + " |\n"
            text += "\nGetter/setter metadata is resolved through native property inheritance; it is not runtime validation. Omitted setters do not independently prove immutable Python access.\n\n"
            if any(contracts[prop.property_type_id] is None for prop in direct):
                text += "Conversion metadata gaps have exact-TypeId, direction-specific [source reviews](../conversion-review.md), with build conditions and unsupported operations preserved. These reviews do not change upstream generator metadata and are never inherited across a different conversion implementation.\n\n"
        else:
            text += "No direct properties discovered. This does not mean there are no inherited, extension, runtime-added, or unparsed properties.\n\n"
        if issues_by_owner[native]:
            text += "## Discovery diagnostics\n\n"
            text += "\n".join(f"- `{issue.format()}`" for issue in issues_by_owner[native]) + "\n\n"
        write(out, relative, text, pages)
    for namespace, natives in sorted(namespaces.items()):
        text = f"# Native namespace `{namespace}`\n\n[Catalogue index](../index.md)\n\n"
        text += "Native prefixes identify source registrations; they are not necessarily public Python modules. Runtime availability depends on build/module initialization.\n\n"
        if wrapper_gaps[namespace]:
            text += "[Wrapper association audit](wrapper-review.md) lists every owner in this namespace without a direct association.\n\n"
        for native in natives:
            kind = "document" if native in documents else "other property owner"
            text += f"- [{native}]({type_path(native).name}): {kind}; {len(by_owner[native])} directly discovered properties.\n"
        write(out, Path(namespace) / "index.md", text, pages)
    for namespace, gaps in sorted(wrapper_gaps.items()):
        if not gaps:
            continue
        text = f"# `{namespace}` wrapper association audit\n\n[Namespace index](index.md) | [Audit overview](../wrapper-review.md)\n\n"
        text += "Every listed owner has no direct binding association in existing discovery. Native inheritance and closest verified implementation context are routing evidence, not automatic public Python class declarations. Exact descendant overrides, conditional compilation, initialization, cached PythonObject replacement, and target-version behavior remain unverified unless the linked type record supplies an explicit review.\n\n"
        text += "| Native owner | Closest discovered ancestor binding | Reviewed implementation context | Registration evidence |\n| --- | --- | --- | --- |\n"
        for native, ancestor, implementation in gaps:
            base = f"{ancestor} -> {wrappers[ancestor].qualified_name}" if ancestor else "None discovered; inspect native implementation"
            context = implementation or "None reviewed; exact wrapper unresolved"
            node = hierarchy.nodes[native]
            text += f"| [{native}]({type_path(native).name}) | {md_cell(base)} | {md_cell(context)} | `{node.source}:{node.line}` |\n"
        write(out, Path(namespace) / "wrapper-review.md", text, pages)
    text = "# Wrapper association audit\n\n[Catalogue index](index.md)\n\nThe direct-association gap is retained; nearest ancestor bindings are not silently promoted into concrete wrapper identities. Each namespace audit records every affected native owner, source registration, closest discovered binding ancestor, and available verified implementation context. Type records contain the detailed evidence. Runtime availability and actual returned Python classes remain target-version checks.\n\n"
    text += "\n".join(f"- [{namespace}]({namespace}/wrapper-review.md): {len(gaps)} owners without a direct association" for namespace, gaps in sorted(wrapper_gaps.items()) if gaps) + "\n\n"
    text += "Reviewed implementations are recorded with source hashes in [review evidence](source-review.json). If evidence changes, those manual contexts are withheld until rereviewed. An ancestor context intentionally does not assert that a descendant lacks an overriding factory.\n"
    write(out, "wrapper-review.md", text, pages)
    gaps = [prop for prop in properties if contracts[prop.property_type_id] is None]
    text = f"# Conversion gap audit\n\n[Catalogue index](index.md)\n\nUpstream metadata has {len(gaps)} unresolved property occurrences. The audit below preserves every occurrence and reviews exact native property families; it does not modify the core metadata or infer contracts through unrelated overrides. Getter and setter results are separately traced. Reviews are source behavior, not runtime tests.\n\n"
    text += "The evidence snapshot is in [source-review.json](source-review.json). Its source hashes are checked on regeneration; changed/missing sources invalidate affected manual reviews. Iterable and Sequence are standard Python typing concepts. Base refers to FreeCAD.Base.\n\n"
    for native in sorted({prop.property_type_id for prop in gaps}):
        item = reviewed.get(native)
        text += f"## `{native}`\n\n"
        if item:
            text += f"Status: {item['status']}.\n\nGetter: {item['getter']}.\n\nSetter: {item['setter']}.\n\n{item['note']}\n\nEvidence: " + ", ".join(f"`{source}`" for source in item["sources"]) + ".\n\n"
        else:
            text += "Unresolved: no current manual review, or its evidence changed. Inspect native getPyObject/setPyObject and module registration; no contract is invented.\n\n"
        text += "Affected occurrences:\n\n"
        for prop in sorted((prop for prop in gaps if prop.property_type_id == native), key=lambda prop: (prop.owner_type_id, prop.property_name)):
            text += f"- [{prop.owner_type_id}.{prop.property_name}]({type_path(prop.owner_type_id).as_posix()}): `{prop.source}:{prop.line}`.\n"
        text += "\n"
    if changed:
        text += "## Changed review evidence\n\n" + "\n".join(f"- `{source}`: source absent or content hash changed; affected reviews withheld." for source in sorted(changed)) + "\n"
    write(out, "conversion-review.md", text, pages)
    try:
        revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        revision = "unavailable"
    unresolved = sum(contracts[prop.property_type_id] is None for prop in properties)
    diagnostics_counts = dict(sorted(Counter(issue.kind for issue in diagnostics).items()))
    version = json.loads((root / "version.json").read_text(encoding="utf-8"))
    release = ".".join(str(version[f"version_{key}"]) for key in ("major", "minor", "patch"))
    if version.get("version_suffix"):
        release += "-" + version["version_suffix"]
    metadata = {"checkout_revision": revision, "checkout_version": release, "native_registrations": len(hierarchy.nodes), "document_types": len(documents), "catalogued_owners": len(selected), "namespaces": len(namespaces), "properties": len(properties), "unresolved_property_conversions": unresolved, "owners_without_direct_binding": sum(native not in wrappers for native in selected), "discovery_diagnostics": diagnostics_counts}
    metadata.update(source_reviewed_property_conversions=sum(prop.property_type_id in reviewed for prop in gaps), remaining_unreviewed_property_conversions=sum(prop.property_type_id not in reviewed for prop in gaps), build_conditional_property_conversions=sum(reviewed.get(prop.property_type_id, {}).get("status") == "conditional" for prop in gaps), unsupported_python_property_conversions=sum(reviewed.get(prop.property_type_id, {}).get("status") == "unsupported" for prop in gaps), wrapper_owners_with_implementation_context=sum(implementation is not None for items in wrapper_gaps.values() for _, _, implementation in items), wrapper_owners_without_implementation_context=sum(implementation is None for items in wrapper_gaps.values() for _, _, implementation in items), review_evidence_revision=review["review_revision"], changed_review_evidence=sorted(changed))
    text = f"# Native object and property catalogue\n\nGenerated from checkout HEAD `{revision}`, version `{release}`, using current local source. HEAD alone does not identify uncommitted source changes. This full inventory is not runtime-verified; separate smoke checks are recorded in [runtime validation](../runtime-validation.md).\n\n"
    text += f"Discovery: {len(hierarchy.nodes)} native registrations, {len(documents)} DocumentObject descendants (including abstract types), {len(properties)} C++ registered properties across {len(selected)} catalogued owners. {unresolved} properties have unresolved conversion metadata; {metadata['owners_without_direct_binding']} owners lack a direct source binding association.\n\n"
    text += f"[Conversion gap audit](conversion-review.md): {metadata['source_reviewed_property_conversions']} occurrences have current source reviews; {metadata['remaining_unreviewed_property_conversions']} remain unaudited/stale. {metadata['build_conditional_property_conversions']} depend on optional build support and {metadata['unsupported_python_property_conversions']} have no supported Python counterpart. Upstream missing-metadata count is preserved. [Wrapper audit](wrapper-review.md) records all direct-association gaps with conservative ancestor/implementation context; {metadata['wrapper_owners_without_implementation_context']} have no manually verified implementation context.\n\n"
    text += "## Limits and use\n\n- Follow namespace/type records and native parent links for inherited properties. This inventory also retains properties on non-document owners (such as extensions and view providers), marked accordingly.\n- Abstract registration and available source are not promises of constructibility in a running build. Native TypeIds are not Python import paths.\n- Discovery reuses `src/Tools/typing/stubgen/type_hierarchy.py` and `cpp_properties.py`. All properties returned by that helper are retained, including those omitted from public stubs for unresolved wrapper ownership. Its diagnostics retain skipped/unscoped registrations.\n- Extension attachment and instance-specific Python addProperty calls are not flattened into this static catalogue. Zero discovered direct properties does not establish zero available properties.\n- Public associations come from existing binding discovery. Manual handwritten implementations and nearest discovered ancestors are separate evidence, not automatic descendant type claims.\n- Conversion expressions normally come from PropertyPythonContracts.pyi metadata and native inheritance; source-review exceptions are marked per row. Nested helper aliases are defined in [conversion aliases](conversion-aliases.md). Metadata may omit valid runtime inputs; registration descriptions are source text.\n- See [object discovery guidance](../object-types.md) and [core property guidance](../core-api.md) for safe runtime inspection, copies, units, and editor status.\n\n"
    text += "## Namespaces\n\n" + "\n".join(f"- [{namespace}]({namespace}/index.md): {len(natives)} owners" for namespace, natives in sorted(namespaces.items())) + "\n\n"
    text += "## Discovery diagnostics\n\n" + ("\n".join(f"- {kind}: {count}" for kind, count in diagnostics_counts.items()) or "No discovery diagnostics.") + "\n\nDiagnostics appear on the corresponding owner records; unresolved conversion counts are separate.\n\n"
    unregistered = [issue for issue in diagnostics if issue.owner_type_id not in hierarchy.nodes]
    if unregistered:
        text += "### Diagnostics without a registered owner\n\n" + "\n".join(f"- `{issue.format()}`" for issue in unregistered) + "\n\n"
    text += "## Regenerate\n\n```sh\npython -B contrib/skills/freecad-addon-api/scripts/build_object_types.py --root .\npython -B contrib/skills/freecad-addon-api/scripts/test_build_object_types.py\n```\n\nIn the repository layout, `--root` defaults to this script's checkout. When copying/installing the skill elsewhere, pass `--root /path/to/FreeCAD` explicitly. Output is fixed to this skill's references/object-types directory; only obsolete previously listed Markdown pages are removed. No FreeCAD runtime or third-party dependencies are required.\n"
    write(out, "index.md", text, pages)
    aliases = "# Conversion aliases\n\n[Catalogue index](index.md)\n\nTyping expressions from the existing property metadata; these are not runtime imports. Unqualified Base and DocumentObject refer to FreeCAD.Base and FreeCAD.DocumentObject.\n\n```python\n" + "\n".join(f"{alias.name} = {alias.expression}" for alias in catalog.aliases) + "\n```\n"
    write(out, "conversion-aliases.md", aliases, pages)
    manifest = out / "manifest.json"
    if manifest.resolve() != manifest.absolute():
        raise ValueError("Refusing redirected manifest")
    previous = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {}
    for obsolete in set(previous.get("pages", [])) - pages:
        target = out / obsolete
        resolved = target.resolve()
        if resolved.is_relative_to(out.resolve()) and resolved == target.absolute() and target.suffix == ".md" and target.is_file():
            target.unlink()
    metadata["pages"] = sorted(pages)
    manifest.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=CHECKOUT)
    args = parser.parse_args()
    result = build(args.root.resolve(), SKILL / "references/object-types")
    print(f"Rendered {result['document_types']} native document types, {result['properties']} properties, {len(result['pages'])} pages; {result['unresolved_property_conversions']} conversion gaps.")


if __name__ == "__main__":
    main()
