# Conversion gap audit

[Catalogue index](index.md)

Upstream metadata has 43 unresolved property occurrences. The audit below preserves every occurrence and reviews exact native property families; it does not modify the core metadata or infer contracts through unrelated overrides. Getter and setter results are separately traced. Reviews are source behavior, not runtime tests.

The evidence snapshot is in [source-review.json](source-review.json). Its source hashes are checked on regeneration; changed/missing sources invalidate affected manual reviews. Iterable and Sequence are standard Python typing concepts. Base refers to FreeCAD.Base.

## `App::PropertyBoolList`

Status: source-reviewed.

Getter: tuple[bool, ...].

Setter: bool | int | Iterable[bool | int] | dict[int, bool | int] | str.

Getter builds a tuple. Setter accepts binary-digit strings via dynamic_bitset; other inputs follow PropertyListsT conversion. A single bool/int replaces with one item, iterables replace contents, and integer-key dictionaries update/append indexed items. Index -1 or current length appends.

Evidence: `src/App/PropertyStandard.cpp:2440`, `src/App/Property.cpp:389`, `src/App/Property.h:1077`.

Affected occurrences:

- [App::FeatureTest.BoolList](App/FeatureTest.md): `src/App/FeatureTest.cpp:81`.
- [Fem::ConstraintContact.ReversedMaster](Fem/ConstraintContact.md): `src/Mod/Fem/App/FemConstraintContact.cpp:81`.
- [Fem::ConstraintContact.ReversedSlave](Fem/ConstraintContact.md): `src/Mod/Fem/App/FemConstraintContact.cpp:88`.
- [Gui::ViewProviderLink.OverrideMaterialList](Gui/ViewProviderLink.md): `src/Gui/ViewProviderLink.cpp:1968`.
- [Surface::GeomFillSurface.ReversedList](Surface/GeomFillSurface.md): `src/Mod/Surface/App/FeatureGeomFillSurface.cpp:137`.

## `App::PropertyColorList`

Status: source-reviewed.

Getter: list[tuple[float, float, float, float]].

Setter: _ColorInput | Iterable[_ColorInput] | dict[int, _ColorInput].

Getter builds RGBA tuples. Each setter item is converted by PropertyColor::setPyObject; inherited PropertyListsT also accepts a single color, iterables, and indexed dictionaries. _ColorInput is defined in conversion-aliases.md.

Evidence: `src/App/PropertyStandard.cpp:2722`, `src/App/PropertyStandard.cpp:2744`, `src/App/PropertyStandard.h:1102`, `src/App/Property.cpp:389`, `src/App/Property.h:1077`.

Affected occurrences:

- [App::FeatureTest.ColourList](App/FeatureTest.md): `src/App/FeatureTest.cpp:96`.
- [FemGui::ViewProviderFemMesh.ElementColorArray](FemGui/ViewProviderFemMesh.md): `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:217`.
- [FemGui::ViewProviderFemMesh.NodeColorArray](FemGui/ViewProviderFemMesh.md): `src/Mod/Fem/Gui/ViewProviderFemMesh.cpp:210`.
- [Gui::ViewProviderFeature.ColourList](Gui/ViewProviderFeature.md): `src/Gui/ViewProviderFeature.cpp:37`.
- [Gui::ViewProviderLink.OverrideColorList](Gui/ViewProviderLink.md): `src/Gui/ViewProviderLink.cpp:1969`.
- [Gui::ViewProviderPart.OverrideColorList](Gui/ViewProviderPart.md): `src/Gui/ViewProviderPart.cpp:59`.
- [PartGui::ViewProviderPartExt.LineColorArray](PartGui/ViewProviderPartExt.md): `src/Mod/Part/Gui/ViewProviderExt.cpp:181`.
- [PartGui::ViewProviderPartExt.PointColorArray](PartGui/ViewProviderPartExt.md): `src/Mod/Part/Gui/ViewProviderExt.cpp:174`.

## `App::PropertyIntegerSet`

Status: source-reviewed.

Getter: set[int].

Setter: int | Sequence[int].

Getter returns a set; setter accepts a scalar integer or PySequence_Check sequence of integers. A Python set is not accepted merely because it is the getter result; assign list(result) when round-tripping.

Evidence: `src/App/PropertyStandard.cpp:1049`.

Affected occurrences:

- [Fem::FemSetElementNodesObject.Elements](Fem/FemSetElementNodesObject.md): `src/Mod/Fem/App/FemSetElementNodesObject.cpp:39`.
- [Fem::FemSetNodesObject.Nodes](Fem/FemSetNodesObject.md): `src/Mod/Fem/App/FemSetNodesObject.cpp:39`.

## `App::PropertyMaterial`

Status: source-reviewed.

Getter: FreeCAD.Material.

Setter: FreeCAD.Material | _ColorInput.

Getter creates a material copy. Setter accepts legacy App MaterialPy or MaterialPy::toColor inputs: packed integer or homogeneous integer/float RGB/RGBA tuple. FreeCAD.Material is distinct from the modern Materials.Material API.

Evidence: `src/App/PropertyStandard.cpp:2987`, `src/App/MaterialPyImp.cpp:35`, `src/App/Application.cpp:489`.

Affected occurrences:

- [App::FeatureTest.Material](App/FeatureTest.md): `src/App/FeatureTest.cpp:97`.
- [MeshGui::ViewProviderMeshCurvature.TextureMaterial](MeshGui/ViewProviderMeshCurvature.md): `src/Mod/Mesh/Gui/ViewProviderCurvature.cpp:123`.
- [PartGui::ViewProviderPartExt.LineMaterial](PartGui/ViewProviderPartExt.md): `src/Mod/Part/Gui/ViewProviderExt.cpp:170`.
- [PartGui::ViewProviderPartExt.PointMaterial](PartGui/ViewProviderPartExt.md): `src/Mod/Part/Gui/ViewProviderExt.cpp:171`.

## `App::PropertyMaterialList`

Status: source-reviewed.

Getter: tuple[FreeCAD.Material, ...].

Setter: FreeCAD.Material | Iterable[FreeCAD.Material] | dict[int, FreeCAD.Material].

Getter builds a tuple of material copies. Inherited PropertyListsT handles scalar, iterable, and indexed updates; getPyValue accepts only MaterialPy, unlike PropertyMaterial's color shortcut. The native class maintains a minimum list size of one.

Evidence: `src/App/PropertyStandard.cpp:3099`, `src/App/PropertyStandard.cpp:3547`, `src/App/PropertyStandard.h:1221`, `src/App/Property.cpp:389`, `src/App/Property.h:1077`, `src/App/Application.cpp:489`.

Affected occurrences:

- [App::FeatureTest.MaterialList](App/FeatureTest.md): `src/App/FeatureTest.cpp:98`.
- [Gui::ViewProviderGeometryObject.ShapeAppearance](Gui/ViewProviderGeometryObject.md): `src/Gui/ViewProviderGeometryObject.cpp:77`.
- [Gui::ViewProviderLink.MaterialList](Gui/ViewProviderLink.md): `src/Gui/ViewProviderLink.cpp:1965`.
- [Gui::ViewProviderLink.ShapeAppearance](Gui/ViewProviderLink.md): `src/Gui/ViewProviderLink.cpp:1949`.

## `App::PropertyMatrix`

Status: source-reviewed.

Getter: Base.Matrix.

Setter: Base.Matrix | tuple[float | int, ...].

Getter copies the matrix. Tuple setter requires exactly 16 numbers and fills cMatrix[x][y] from tuple[x + y*4]; do not assume row-major ordering or accept lists.

Evidence: `src/App/PropertyGeo.cpp:421`.

Affected occurrences:

- [App::FeatureTest.Matrix](App/FeatureTest.md): `src/App/FeatureTest.cpp:113`.
- [Mesh::Transform.Position](Mesh/Transform.md): `src/Mod/Mesh/App/FeatureMeshTransform.cpp:40`.

## `App::PropertyPath`

Status: source-reviewed.

Getter: str.

Setter: str.

Filesystem path conversion uses a UTF-8 Python string. This is distinct from CAM's Path::PropertyPath toolpath.

Evidence: `src/App/PropertyStandard.cpp:210`.

Affected occurrences:

- [App::FeatureTest.Path](App/FeatureTest.md): `src/App/FeatureTest.cpp:83`.

## `App::PropertyPythonObject`

Status: source-reviewed.

Getter: object.

Setter: object.

Getter returns a new reference to the stored arbitrary Python object, not a copy. Setter stores that object with native change notification. This conversion does not establish that every object is persistable.

Evidence: `src/App/PropertyPythonObject.cpp:225`.

Affected occurrences:

- [App::FeatureTestAttribute.Object](App/FeatureTestAttribute.md): `src/App/FeatureTest.cpp:347`.
- [SketcherGui::ViewProviderSketch.TempoVis](SketcherGui/ViewProviderSketch.md): `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:611`.

## `App::PropertyRotation`

Status: source-reviewed.

Getter: Base.Rotation.

Setter: Base.Rotation | Base.Matrix.

Getter constructs a copy; Matrix assignment extracts rotation and Rotation assignment copies its value.

Evidence: `src/App/PropertyGeo.cpp:1220`.

Affected occurrences:

- [Fem::ConstraintRigidBody.Rotation](Fem/ConstraintRigidBody.md): `src/Mod/Fem/App/FemConstraintRigidBody.cpp:51`.
- [Fem::ConstraintTransform.Rotation](Fem/ConstraintTransform.md): `src/Mod/Fem/App/FemConstraintTransform.cpp:41`.

## `App::PropertyXLinkSubList`

Status: source-reviewed.

Getter: list[tuple[FreeCAD.DocumentObject, tuple[str, ...]]].

Setter: PropertyLinkSub input or list/tuple of PropertyLinkSub inputs.

Getter skips absent/detached linked objects. Setter first tries PropertyLinkSub syntax with external links allowed, then a tuple/list of such inputs; it groups subnames by object. PropertyLinkSub input includes an object, None, or object/subname pair. Cross-document and runtime attachment state remain relevant.

Evidence: `src/App/PropertyLinks.cpp:5100`, `src/App/PropertyLinks.cpp:5123`, `src/App/PropertyLinks.cpp:1500`.

Affected occurrences:

- [PartDesign::SubShapeBinder.Support](PartDesign/SubShapeBinder.md): `src/Mod/PartDesign/App/ShapeBinder.cpp:350`.

## `Fem::PropertyFemMesh`

Status: source-reviewed.

Getter: Fem.FemMesh.

Setter: Fem.FemMesh | Base.Placement.

Getter wraps the stored mesh and calls setConst. A mesh setter copies the mesh; a Placement setter transforms existing mesh geometry, rather than storing placement as the property value.

Evidence: `src/Mod/Fem/App/FemMeshProperty.cpp:96`, `src/Mod/Fem/App/AppFem.cpp:132`.

Affected occurrences:

- [Fem::FemMeshObject.FemMesh](Fem/FemMeshObject.md): `src/Mod/Fem/App/FemMeshObject.cpp:42`.

## `Fem::PropertyPostDataObject`

Status: conditional.

Getter: VTK Python data-object wrapper when FC_USE_VTK_PYTHON is enabled.

Setter: VTK Python object convertible to vtkDataObject when FC_USE_VTK_PYTHON is enabled.

Getter wraps a deep-copied dataset; setter checks vtkDataObject and deep-copies it. Without FC_USE_VTK_PYTHON, both directions signal NotImplementedError. Actual VTK Python class and supported concrete dataset subtype depend on the build/value; they are intentionally not flattened into one unconditional Python signature.

Evidence: `src/Mod/Fem/App/PropertyPostDataObject.cpp:172`.

Affected occurrences:

- [Fem::FemPostObject.Data](Fem/FemPostObject.md): `src/Mod/Fem/App/FemPostObject.cpp:44`.

## `Inspection::PropertyDistanceList`

Status: source-reviewed.

Getter: list[float].

Setter: float | list[float].

This setter checks PyList/PyFloat explicitly; integer entries and general iterable/tuple inputs are not accepted by this implementation.

Evidence: `src/Mod/Inspection/App/InspectionFeature.cpp:592`.

Affected occurrences:

- [Inspection::Feature.Distances](Inspection/Feature.md): `src/Mod/Inspection/App/InspectionFeature.cpp:772`.

## `Mesh::PropertyCurvatureList`

Status: source-reviewed.

Getter: list[tuple[float, float, tuple[float, float, float], tuple[float, float, float]]].

Setter: raises AttributeError.

Each entry is maximum curvature, minimum curvature, maximum direction xyz, minimum direction xyz. Setter unconditionally raises a read-only AttributeError.

Evidence: `src/Mod/Mesh/App/MeshProperties.cpp:365`.

Affected occurrences:

- [Mesh::Curvature.CurvInfo](Mesh/Curvature.md): `src/Mod/Mesh/App/FeatureMeshCurvature.cpp:40`.

## `Part::PropertyFilletEdges`

Status: source-reviewed.

Getter: list[tuple[int, float, float]].

Setter: Sequence[tuple[int, float, float]].

Canonical setter form is a sequence of edge-id, first-radius, second-radius tuples. C++ PyCXX conversion reads tuple items 0..2; this describes the supported form without promising exact rejection/coercion behavior for every malformed input.

Evidence: `src/Mod/Part/App/PropertyTopoShape.cpp:979`.

Affected occurrences:

- [Part::FilletBase.Edges](Part/FilletBase.md): `src/Mod/Part/App/PartFeature.cpp:2033`.

## `Part::PropertyShapeHistory`

Status: source-reviewed.

Getter: None.

Setter: object (ignored).

Getter always returns None and setter is empty. Python assignment does not alter the native history; this property is not an exposed shape-history editing API.

Evidence: `src/Mod/Part/App/PropertyTopoShape.cpp:920`.

Affected occurrences:

- [Part::Boolean.History](Part/Boolean.md): `src/Mod/Part/App/FeaturePartBoolean.cpp:82`.
- [Part::MultiCommon.History](Part/MultiCommon.md): `src/Mod/Part/App/FeaturePartCommon.cpp:73`.
- [Part::MultiFuse.History](Part/MultiFuse.md): `src/Mod/Part/App/FeaturePartFuse.cpp:76`.

## `Path::PropertyPath`

Status: source-reviewed.

Getter: Path.Path.

Setter: Path.Path.

Getter copies the toolpath into PathPy; setter accepts PathPy and copies its Toolpath. Module initialization exports the wrapper as Path.Path.

Evidence: `src/Mod/CAM/App/PropertyPath.cpp:59`, `src/Mod/CAM/App/AppPath.cpp:72`.

Affected occurrences:

- [Path::Feature.Path](Path/Feature.md): `src/Mod/CAM/App/FeaturePath.cpp:37`.

## `Points::PropertyPointKernel`

Status: source-reviewed.

Getter: Points.Points.

Setter: Points.Points.

Getter wraps the stored point kernel and calls setConst; setter copies an accepted PointsPy kernel. Reassign a separately constructed Points.Points value for edits.

Evidence: `src/Mod/Points/App/PropertyPointKernel.cpp:78`, `src/Mod/Points/App/AppPoints.cpp:49`.

Affected occurrences:

- [Points::Feature.Points](Points/Feature.md): `src/Mod/Points/App/PointsFeature.cpp:42`.

## `Robot::PropertyTrajectory`

Status: source-reviewed.

Getter: Robot.Trajectory.

Setter: Robot.Trajectory.

Getter copies the trajectory into TrajectoryPy; setter accepts that wrapper and copies the value. Module initialization exports Robot.Trajectory.

Evidence: `src/Mod/Robot/App/PropertyTrajectory.cpp:84`, `src/Mod/Robot/App/AppRobot.cpp:122`.

Affected occurrences:

- [Robot::TrajectoryObject.Trajectory](Robot/TrajectoryObject.md): `src/Mod/Robot/App/TrajectoryObject.cpp:42`.

## `SketcherGui::PropertyVisualLayerList`

Status: unsupported.

Getter: raises NotImplementedError.

Setter: nonempty values raise NotImplementedError; no supported Python counterpart.

getPyObject and per-item getPyValue explicitly throw because there is no Python counterpart. Inherited empty-list operations may avoid per-item conversion, but are not a supported visual-layer editing contract. Use the documented Sketcher/view-provider methods instead of inventing a Python VisualLayer value.

Evidence: `src/Mod/Sketcher/Gui/PropertyVisualLayerList.cpp:52`, `src/Mod/Sketcher/Gui/PropertyVisualLayerList.h`, `src/App/Property.h:1077`.

Affected occurrences:

- [SketcherGui::ViewProviderSketch.VisualLayerList](SketcherGui/ViewProviderSketch.md): `src/Mod/Sketcher/Gui/ViewProviderSketch.cpp:658`.

