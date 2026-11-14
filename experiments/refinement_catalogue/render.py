"""Pictures of the catalogue's meshes with gmsh offscreen: 1000 x 800, parts coloured, a 3D mesh cut at a plane.

Gmsh crashes when it is initialized again after its graphics were, so a process draws one picture: picture() runs
this file in a new Python.
Run alone: pixi run -e addon python experiments/refinement_catalogue/render.py <msh>[|<msh>] <png> <dim> [hints as JSON]"""

import json
import os
import subprocess
import sys

import gmsh

WIDTH, HEIGHT = 1000, 800
NORMALS = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}
LOOK = {"x": (-90, 0, -90), "y": (-90, 0, 0), "z": (0, 0, 0)}  # General.RotationX/Y/Z that face the cut


def render(msh_paths, png_path, dim, clip=None, zoom=None, at=0.0):
    """Write a picture of the mesh files msh_paths (one path or a list: a sliding Study's fixed and moving meshes) to
    png_path. dim 2 or 3; clip "x", "y" or "z": 3D only, the slice of elements that
    cross the plane axis = at, seen face on; zoom (u0, v0, u1, v1): the box of the view's plane to show, (x, y) for a
    2D drawing or a z cut, (x, z) for a y cut, (y, z) for an x cut. Without zoom the whole model fills the picture."""
    gmsh.initialize()
    try:
        opt = gmsh.option.setNumber
        opt("General.Terminal", 0)
        paths = [msh_paths] if isinstance(msh_paths, str) else list(msh_paths)
        gmsh.open(paths[0])
        for path in paths[1:]:
            gmsh.merge(path)
        opt("General.GraphicsWidth", WIDTH)
        opt("General.GraphicsHeight", HEIGHT)
        opt("Print.Width", WIDTH)  # the size of the PNG; the window may be smaller on screen
        opt("Print.Height", HEIGHT)
        opt("General.SmallAxes", 0)
        opt("Mesh.ColorCarousel", 2)  # by part: by entity (1) gave touching parts the same colour (RN-03)
        opt("Mesh.Points", 0)
        opt("Mesh.Lines", 0)
        if dim == 3:
            opt("Mesh.SurfaceFaces", 0)
            opt("Mesh.SurfaceEdges", 0)
            opt("Mesh.VolumeFaces", 1)
            opt("Mesh.VolumeEdges", 1)
        else:
            opt("Mesh.SurfaceFaces", 1)
            opt("Mesh.SurfaceEdges", 1)
        axis = clip or "z"
        if dim == 3 and clip:
            a, b, c = NORMALS[clip]
            for name, value in zip("ABCD", (a, b, c, -at)):
                opt(f"General.Clip0{name}", value)
            opt("Mesh.Clip", 1)
            opt("General.ClipWholeElements", 1)
            opt("General.ClipOnlyDrawIntersectingVolume", 1)
        opt("General.Trackball", 0)
        for name, value in zip("XYZ", LOOK[axis]):
            opt(f"General.Rotation{name}", value)
        gmsh.fltk.initialize()
        gmsh.fltk.update()
        gmsh.write(png_path)  # gmsh's own fit: measured to find its pixels per mm
        _zoom(png_path, zoom, axis)
        gmsh.fltk.update()
        gmsh.write(png_path)
    finally:
        gmsh.finalize()


def _zoom(png_path, box, axis):
    """Scale and move the view so the box (u0, v0, u1, v1) of the view's plane fills it (default: the model's box).
    Gmsh's own fit is measured on the first picture: the width of what it drew against the model's width. Translation
    is in mm of the screen's axes; gmsh centres the model's box."""
    from PIL import Image
    import numpy as np

    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)
    lo = {"z": (xmin, ymin), "y": (xmin, zmin), "x": (ymin, zmin)}[axis]
    hi = {"z": (xmax, ymax), "y": (xmax, zmax), "x": (ymax, zmax)}[axis]
    drawn = np.asarray(Image.open(png_path).convert("L")) < 250
    cols = np.where(drawn.any(axis=0))[0]
    per_mm = (cols.max() - cols.min()) / (hi[0] - lo[0])
    u0, v0, u1, v1 = box or (*lo, *hi)
    scale = 0.96 * min(WIDTH / (u1 - u0), HEIGHT / (v1 - v0)) / per_mm
    for name in "XYZ":
        gmsh.option.setNumber(f"General.Scale{name}", scale)
    gmsh.option.setNumber("General.TranslationX", (lo[0] + hi[0]) / 2 - (u0 + u1) / 2)
    gmsh.option.setNumber("General.TranslationY", (lo[1] + hi[1]) / 2 - (v0 + v1) / 2)


def picture(msh_paths, png_path, dim, **hints):
    """render() in a new process; raises when it fails or writes no picture."""
    paths = [msh_paths] if isinstance(msh_paths, str) else list(msh_paths)
    args = [sys.executable, os.path.abspath(__file__), "|".join(paths), png_path, str(dim), json.dumps(hints)]
    r = subprocess.run(args, capture_output=True, encoding="utf-8", errors="replace", timeout=300)
    if r.returncode or not os.path.exists(png_path):
        raise RuntimeError(f"render failed ({r.returncode}): {r.stderr.strip()[-500:]}")


if __name__ == "__main__":
    msh, png, d = sys.argv[1:4]
    render(msh.split("|"), png, int(d), **(json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}))
