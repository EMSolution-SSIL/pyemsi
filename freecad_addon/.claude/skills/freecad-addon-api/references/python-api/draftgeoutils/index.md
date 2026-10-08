# Python source module `draftgeoutils`

[Python catalogue](../index.md)

Evidence: `src/Mod/Draft/draftgeoutils/__init__.py`. Import path is source-routed; installed availability is unverified.

Modules that contain functions that use and manipulate shapes.

These functions provide support for dealing with the custom objects
defined within the workbench.
The functions are meant to be used in the creation step of the objects,
or to manipulate the created shapes, principally by the functions
in the `draftmake` package.

These functions should deal with the internal shapes of the objects,
and their special properties; they shouldn't be very generic.

These functions may be useful for other programmers in their own macros
or workbenches. These functions may not necessarily be exposed as
part of the Draft workbench programming interface yet.

These functions were previously defined in the big `DraftGeomUtils` module.

Literal `__all__`: not available; source names do not imply supported public API.

