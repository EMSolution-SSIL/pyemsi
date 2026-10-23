"""Geometry sources and setup validation. No GUI or mesh generation here."""

import FreeCAD as App

from . import objects


def global_shape(obj):
    """Shape where the user sees it, including the placements of containing Parts."""
    shape = obj.getPropertyOfGeometry().transformed(App.Placement().Matrix)
    shape.Placement = obj.getGlobalPlacement()
    return shape


def is_container(obj):
    return not objects.is_study_object(obj) and (
        obj.isDerivedFrom("App::Part") or obj.isDerivedFrom("App::DocumentObjectGroup")
    )


def is_source(obj):
    """A source cannot contain Study objects: linking it would create a dependency cycle."""
    return is_container(obj) and not any(objects.is_study_object(o) for o in obj.OutListRecursive)


PLANE_TOL = 1e-6


def plane_of(face):
    """ "XY" for a face in the plane z = 0, "ZX" for a face in the plane y = 0, else None."""
    box = face.BoundBox
    if max(abs(box.ZMin), abs(box.ZMax)) < PLANE_TOL:
        return "XY"
    if max(abs(box.YMin), abs(box.YMax)) < PLANE_TOL:
        return "ZX"
    return None


def collect(roots, dimension):
    """Return final geometry objects and diagnostics, in source order.

    Bodies are atomic. A Part result consumes its dependencies, so a Boolean and
    its operands do not become three overlapping regions. Visibility is irrelevant.
    """
    candidates, errors, visited = [], [], set()

    def visit(obj):
        key = (obj.Document.Name, obj.Name)
        if key in visited:
            return
        visited.add(key)
        if objects.is_study_object(obj) or obj.isDerivedFrom("Fem::FemMeshObject"):
            errors.append(f"{obj.Label}: study objects and mesh results are not geometry.")
        elif is_container(obj):
            for child in obj.Group:
                visit(child)
        elif obj.isDerivedFrom("App::Origin") or obj.isDerivedFrom("App::OriginFeature"):
            return
        elif obj.isDerivedFrom("Sketcher::SketchObject"):
            return  # sketches are construction inputs; this phase does not fill wires
        elif obj.isDerivedFrom("Part::Feature") and not obj.isDerivedFrom("App::Link"):
            candidates.append(obj)
        else:
            errors.append(f"{obj.Label}: unsupported geometry object ({obj.TypeId}).")

    for obj in roots:
        visit(obj)
    consumed = {dep.Name for obj in candidates for dep in obj.OutListRecursive if dep.Document == obj.Document}
    result, plane = [], None
    for obj in candidates:
        if obj.Name in consumed:
            continue
        shape = global_shape(obj)
        if dimension == "3D":
            if not shape.Solids:
                errors.append(f"{obj.Label}: 3D geometry must contain at least one solid.")
                continue
        else:
            if shape.Solids or not shape.Faces:
                errors.append(f"{obj.Label}: 2D geometry must contain filled planar faces without solids.")
                continue
            valid = True
            for face in shape.Faces:
                if not face.Surface.isPlanar():
                    errors.append(f"{obj.Label}: 2D faces must be planar.")
                    valid = False
                    break
                found = plane_of(face)
                if found is None:
                    errors.append(f"{obj.Label}: 2D faces must lie in the XY plane (z = 0) or the ZX plane (y = 0).")
                    valid = False
                    break
                if plane is None:
                    plane = found
                elif found != plane:
                    errors.append(f"{obj.Label}: 2D faces must share one plane.")
                    valid = False
                    break
            if not valid:
                continue
        result.append(obj)
    return result, errors


def region(study, name):
    """Resolve a live source; a deleted container never falls back to the document."""
    mode = getattr(study, name + "Mode")
    if mode == "Container":
        source = getattr(study, name + "Source")
        if source is None:
            return [], ["Selected container is missing. Choose a Part or Group."]
        if source.Document != study.Document or not is_source(source):
            return [], [f"{source.Label}: choose a Part or Group in this document without Study objects."]
        roots = [source]
    elif mode == "Manual":
        roots = list(getattr(study, name + "Objects"))
    else:
        roots = []
    resolved, errors = collect(roots, study.Dimension)
    if not resolved and not errors:
        errors.append(
            "No geometry chosen. Select the Study and pick a Part or Group, or add bodies to Manual selection."
        )
    return resolved, errors


def setup(study):
    """Resolve enabled regions and validate a common plane and disjoint assignments."""
    main, errors = region(study, "Main")
    errors = ["Main geometry: " + e for e in errors]
    moving = []
    if study.Movement == "Sliding motion":
        moving, other_errors = region(study, "Moving")
        errors += ["Moving geometry: " + e for e in other_errors]
        duplicates = {o.Name for o in main} & {o.Name for o in moving}
        if duplicates:
            errors.append(
                "Assigned to both fixed and moving geometry: "
                + ", ".join(o.Label for o in main if o.Name in duplicates)
            )
        if study.Dimension == "2D":
            _, plane_errors = collect(main + moving, "2D")
            errors += plane_errors
    return main, moving, list(dict.fromkeys(errors))


def export_unavailable(study):
    """Why the Study cannot be meshed at all, or "". Nothing blocks it now; kept for the callers that ask."""
    return ""
