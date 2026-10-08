# Python source module `draftmake`

[Python catalogue](../index.md)

Evidence: `src/Mod/Draft/draftmake/__init__.py`. Import path is source-routed; installed availability is unverified.

Modules that contain functions to create custom scripted objects.

These functions represent the basic application programming interface (API)
of the Draft Workbench to create custom objects.

These functions first create a simple, extensible object defined in C++,
for example, `Part::FeaturePython` or `Part::Part2DObjectPython`,
and then assign a custom proxy class to define its data properties,
and a custom viewprovider class to define its visual properties.

The proxy class is imported from `draftobjects` and the corresponding
viewprovider from `draftviewproviders`.

::

    import FreeCAD as App
    import draftobjects.my_obj as my_obj
    import draftviewproviders.view_my_obj as view_my_obj

    def make_function(input_data):
        doc = App.ActiveDocument
        new_obj = doc.addObject("Part::Part2DObjectPython",
                                "New_obj")
        my_obj.Obj(new_obj)

        if App.GuiUp:
            view_my_obj.ViewProviderObj(new_obj.ViewObject)

        return new_obj

Assigning the viewprovider class is only possible if the graphical interface
is available. In a terminal-only session the viewproviders are not accessible
because the `ViewObject` attribute does not exist.

If an object is created and saved in a console-only session,
the object will not have the custom viewprovider when the file is opened
in the GUI version of the program; it will only have a basic viewprovider
associated to the base C++ object.

If needed, the custom viewprovider can be assigned after opening
the GUI version of the program; then the object will have access
to additional visual properties.

::

    import Draft
    Draft.ViewProviderDraft(new_obj.ViewObject)

Most Draft objects are based on two base `Part` objects
that are able to handle a `Part::TopoShape`.

- `Part::Part2DObjectPython` if they should handle only 2D shapes, and
- `Part::FeaturePython` if they should handle any type of shape (2D or 3D).

Generic objects that don't need to handle shapes but which
can have other properties like `App::PropertyPlacement`,
or which can interact with the 3D view through Coin,
can be based on the simple `App::FeaturePython` object.

Literal `__all__`: not available; source names do not imply supported public API.

