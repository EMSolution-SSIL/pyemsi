# `App::FeaturePython`

[Namespace index](index.md) | [Catalogue index](../index.md)

Category: DocumentObject descendant. Registration: `src/App/FeaturePython.cpp:756`. Abstract macro: no.

Native parent: [App::DocumentObject](../App/DocumentObject.md). Read the parent record for inherited properties.

Python wrapper: unresolved direct binding association. An ancestor wrapper may be used or a handwritten getPyObject override may supply another; inspect implementation/runtime rather than invent a Python class.

[Wrapper association audit](wrapper-review.md).

Closest discovered ancestor binding: `App::DocumentObject` -> `FreeCAD.DocumentObject`. This routes base API lookup; it does not establish this descendant's concrete returned wrapper.

Reviewed implementation context at `App::FeaturePython`: Explicit specialization constructs FeaturePythonPyT<DocumentObjectPy>. A proxy object is distinct from this returned native wrapper; no standalone FreeCAD.FeaturePython import is promised. Evidence: `src/App/FeaturePython.cpp:763`, `src/App/FeaturePythonPyImp.h`, `src/App/FeaturePythonPyImp.inl`. Descendant getPyObject overrides and PythonObject replacement can change the returned value.

## Properties registered for this owner

No direct properties discovered. This does not mean there are no inherited, extension, runtime-added, or unparsed properties.

