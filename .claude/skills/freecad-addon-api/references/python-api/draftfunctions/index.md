# Python source module `draftfunctions`

[Python catalogue](../index.md)

Evidence: `src/Mod/Draft/draftfunctions/__init__.py`. Import path is source-routed; installed availability is unverified.

Modules that contain functions for use with scripted objects and commands.

These functions provide support for dealing with the custom objects
defined within the workbench.
The functions are meant to be used in the creation step of the objects,
by the functions in the `draftmake` package, but also by the graphical
GuiCommands in the `draftguitools` and `drafttaskpanels` packages.

These functions should deal with the internal shapes of the objects,
and their special properties. They should not be very generic;
if they are very generic then they are more appropriate to be included
in the `draftutils` package.

These functions, together with those defined in the `draftmake` package,
represent the public application programming interface (API)
of the Draft Workbench, and should be made available in the `Draft`
namespace by importing them in the `Draft` module.

Literal `__all__`: not available; source names do not imply supported public API.

