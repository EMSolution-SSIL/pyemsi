"""Reads a mesh the add-on wrote and describes it in text. Gmsh API only: never import FreeCAD here."""

import json
import os

import gmsh


def groups(msh_path):
    """{MAT_ID: (name, element count)} of the physical groups of the highest dimension in the mesh file
    (volumes in 3D, surfaces in 2D); lower-dimension groups such as excitation surfaces are left out."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh_path)
        found = gmsh.model.getPhysicalGroups()
        if not found:
            return {}
        top = max(dim for dim, _ in found)
        out = {}
        for dim, tag in found:
            if dim != top:
                continue
            count = 0
            for entity in gmsh.model.getEntitiesForPhysicalGroup(dim, tag):
                count += sum(len(tags) for tags in gmsh.model.mesh.getElements(dim, entity)[1])
            out[tag] = (gmsh.model.getPhysicalName(dim, tag), count)
        return out
    finally:
        gmsh.finalize()


def _nodes(msh_path):
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(msh_path)
        return len(gmsh.model.mesh.getNodes()[0])
    finally:
        gmsh.finalize()


def checklist_text(checklist):
    return "\nCheck by hand:\n" + "".join(f"- {text}\n" for text in checklist) if checklist else ""


def report(case_dir, job, checklist=()):
    """The report of one case: the MAT_ID table, then the case's checklist.
    job is the path of the job.json the mesher ran. Raises if a body or the air of the job is missing or empty."""
    with open(job, encoding="utf-8") as fh:
        data = json.load(fh)
    expected = data.get("bodies") or data.get("volumes") or []
    expected = expected + ([data["air"]] if "air" in data else [])
    found = groups(data["mesh_file"])
    lines = [f"Case {os.path.basename(os.path.normpath(case_dir))}", f"Mesh {os.path.basename(data['mesh_file'])}"]
    lines.append(f"Nodes {_nodes(data['mesh_file'])}")
    lines.append("")
    lines.append("MAT_ID  name  elements")
    for item in expected:
        name, count = found.get(item["mat_id"], (item["name"], 0))
        if count == 0:
            raise RuntimeError(f"{item['name']} (MAT_ID {item['mat_id']}) has no elements in the mesh")
        lines.append(f"MAT_ID {item['mat_id']:>4}  {name}  {count}")
    return "\n".join(lines) + "\n" + checklist_text(checklist)
