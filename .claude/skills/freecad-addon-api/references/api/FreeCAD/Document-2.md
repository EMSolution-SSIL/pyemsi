# `FreeCAD.Document`

[Module](index.md)

```python
class Document(PropertyContainer):
```

This is the Document class.

Evidence: public stub `FreeCAD/__init__.pyi` line 945. Inherited members are on the named base's reference; aliases keep their imported identity.

[part 1](Document.md) | [part 2](Document-2.md) | [part 3](Document-3.md)

## `FreeCAD.Document.addObject`

```python
@overload
def addObject(self, type: Literal['Assembly::AssemblyLink'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Assembly.AssemblyLink:

@overload
def addObject(self, type: Literal['Assembly::AssemblyObject'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Assembly.AssemblyObject:

@overload
def addObject(self, type: Literal['Assembly::BomGroup'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Assembly.BomGroup:

@overload
def addObject(self, type: Literal['Assembly::BomObject'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Assembly.BomObject:

@overload
def addObject(self, type: Literal['Assembly::JointGroup'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Assembly.JointGroup:

@overload
def addObject(self, type: Literal['Assembly::SimulationGroup'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Assembly.SimulationGroup:

@overload
def addObject(self, type: Literal['Assembly::SnapshotGroup'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Assembly.SnapshotGroup:

@overload
def addObject(self, type: Literal['Assembly::ViewGroup'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Assembly.ViewGroup:

@overload
def addObject(self, type: Literal['Path::FeatureArea', 'Path::FeatureAreaPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _CAM.FeatureArea:

@overload
def addObject(self, type: Literal['Fem::FemPostBranchFilter'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Fem.FemPostBranchFilter:

@overload
def addObject(self, type: Literal['Fem::FemPostCalculatorFilter', 'Fem::FemPostClipFilter', 'Fem::FemPostContoursFilter', 'Fem::FemPostCutFilter', 'Fem::FemPostDataAlongLineFilter', 'Fem::FemPostDataAtPointFilter', 'Fem::FemPostFilter', 'Fem::FemPostScalarClipFilter', 'Fem::FemPostWarpVectorFilter', 'Fem::PostFilterPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Fem.FemPostFilter:

@overload
def addObject(self, type: Literal['Fem::FemPostObject'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Fem.FemPostObject:

@overload
def addObject(self, type: Literal['Fem::FemPostPipeline'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Fem.FemPostPipeline:

@overload
def addObject(self, type: Literal['App::Annotation', 'App::AnnotationLabel', 'App::DocumentObject', 'App::DocumentObjectFileIncluded', 'App::FeaturePython', 'App::FeatureTest', 'App::FeatureTestAbsAddress', 'App::FeatureTestAsyncBlocker', 'App::FeatureTestAttribute', 'App::FeatureTestColumn', 'App::FeatureTestException', 'App::FeatureTestPlacement', 'App::FeatureTestRow', 'App::Link', 'App::LinkElement', 'App::LinkElementPython', 'App::LinkGroup', 'App::LinkGroupPython', 'App::LinkPython', 'App::MaterialObject', 'App::MaterialObjectPython', 'App::TextDocument', 'App::VarSet', 'Fem::Constraint', 'Fem::ConstraintBearing', 'Fem::ConstraintContact', 'Fem::ConstraintDisplacement', 'Fem::ConstraintFixed', 'Fem::ConstraintFluidBoundary', 'Fem::ConstraintForce', 'Fem::ConstraintGear', 'Fem::ConstraintHeatflux', 'Fem::ConstraintInitialTemperature', 'Fem::ConstraintPlaneRotation', 'Fem::ConstraintPressure', 'Fem::ConstraintPulley', 'Fem::ConstraintPython', 'Fem::ConstraintRigidBody', 'Fem::ConstraintSpring', 'Fem::ConstraintTemperature', 'Fem::ConstraintTransform', 'Fem::FeaturePython', 'Fem::FemPostBoxFunction', 'Fem::FemPostCylinderFunction', 'Fem::FemPostFunction', 'Fem::FemPostFunctionProvider', 'Fem::FemPostPlaneFunction', 'Fem::FemPostSphereFunction', 'Fem::FemResultObject', 'Fem::FemResultObjectPython', 'Fem::FemSetElementNodesObject', 'Fem::FemSetElementsObject', 'Fem::FemSetFacesObject', 'Fem::FemSetGeometryObject', 'Fem::FemSetNodesObject', 'Fem::FemSetObject', 'Fem::FemSolverObject', 'Fem::FemSolverObjectPython', 'Inspection::Feature', 'Measure::Result', 'Mesh::Curvature', 'Mesh::Export', 'Part::LinkArray', 'Part::LinkArrayCircular', 'Part::LinkArrayLinear', 'Part::LinkArrayPath', 'Part::LinkArrayPoint', 'Part::LinkArrayPolar'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> DocumentObject:

@overload
def addObject(self, type: Literal['App::DocumentObjectGroup', 'App::DocumentObjectGroupPython', 'Fem::FemAnalysis', 'Fem::FemAnalysisPython', 'Inspection::Group'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> DocumentObjectGroup:

@overload
def addObject(self, type: Literal['App::DatumElement', 'App::GeoFeature', 'App::GeometryPython', 'App::InventorObject', 'App::Line', 'App::LocalCoordinateSystem', 'App::Origin', 'App::Placement', 'App::PlacementPython', 'App::Plane', 'App::Point', 'App::VRMLObject', 'Fem::FemMeshObject', 'Fem::FemMeshObjectPython', 'Fem::FemMeshShapeBaseObject', 'Fem::FemMeshShapeBaseObjectPython', 'Fem::FemMeshShapeNetgenObject', 'Fem::FemMeshShapeObject', 'Image::ImagePlane', 'Part::DatumLine', 'Part::DatumPlane', 'Part::DatumPoint', 'Part::FeatureReference', 'Part::LocalCoordinateSystem', 'Path::Feature', 'Path::FeatureCompound', 'Path::FeatureCompoundPython', 'Path::FeaturePython', 'Path::FeatureShape', 'Path::FeatureShapePython', 'Points::Feature', 'Points::FeatureCustom', 'Points::FeaturePython', 'Points::Structured', 'Points::StructuredCustom', 'Robot::Edge2TracObject', 'Robot::TrajectoryCompound', 'Robot::TrajectoryDressUpObject', 'Robot::TrajectoryObject'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> GeoFeature:

@overload
def addObject(self, type: Literal['App::Part'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> Part:

@overload
def addObject(self, type: Literal['Measure::MeasureAngle', 'Measure::MeasureArea', 'Measure::MeasureBase', 'Measure::MeasureCOM', 'Measure::MeasureDiameter', 'Measure::MeasureDistance', 'Measure::MeasureDistanceDetached', 'Measure::MeasureLength', 'Measure::MeasurePosition', 'Measure::MeasurePython', 'Measure::MeasureRadius'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Measure.MeasureBase:

@overload
def addObject(self, type: Literal['Mesh::Cone', 'Mesh::Cube', 'Mesh::Cylinder', 'Mesh::Ellipsoid', 'Mesh::Feature', 'Mesh::FeatureCustom', 'Mesh::FeaturePython', 'Mesh::FillHoles', 'Mesh::FixDefects', 'Mesh::FixDeformations', 'Mesh::FixDegenerations', 'Mesh::FixDuplicatedFaces', 'Mesh::FixDuplicatedPoints', 'Mesh::FixIndices', 'Mesh::FixNonManifolds', 'Mesh::FlipNormals', 'Mesh::HarmonizeNormals', 'Mesh::Import', 'Mesh::RemoveComponents', 'Mesh::SegmentByMesh', 'Mesh::SetOperations', 'Mesh::Sphere', 'Mesh::Torus', 'Mesh::Transform', 'Mesh::TransformDemolding'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Mesh.Feature:

@overload
def addObject(self, type: Literal['Part::BodyBase'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Part.BodyBase:

@overload
def addObject(self, type: Literal['Part::Box', 'Part::Chamfer', 'Part::Circle', 'Part::Common', 'Part::Compound', 'Part::Compound2', 'Part::Cone', 'Part::CurveNet', 'Part::CustomFeature', 'Part::CustomFeaturePython', 'Part::Cut', 'Part::Cylinder', 'Part::Ellipse', 'Part::Ellipsoid', 'Part::Extrusion', 'Part::Face', 'Part::Feature', 'Part::FeatureExt', 'Part::FeatureGeometrySet', 'Part::FeaturePython', 'Part::Fillet', 'Part::FilletBase', 'Part::Fuse', 'Part::Helix', 'Part::ImportBrep', 'Part::ImportIges', 'Part::ImportStep', 'Part::Line', 'Part::Loft', 'Part::Mirroring', 'Part::MultiCommon', 'Part::MultiFuse', 'Part::Offset', 'Part::Offset2D', 'Part::Plane', 'Part::Polygon', 'Part::Prism', 'Part::ProjectOnSurface', 'Part::Refine', 'Part::RegularPolygon', 'Part::Reverse', 'Part::Revolution', 'Part::RuledSurface', 'Part::Scale', 'Part::Section', 'Part::Sphere', 'Part::Spiral', 'Part::Spline', 'Part::Sweep', 'Part::Thickness', 'Part::Torus', 'Part::Vertex', 'Part::Wedge', 'PartDesign::CoordinateSystem', 'PartDesign::Line', 'PartDesign::Plane', 'PartDesign::Point', 'PartDesign::ShapeBinder', 'PartDesign::SubShapeBinder', 'PartDesign::SubShapeBinderPython', 'Path::FeatureAreaView', 'Path::FeatureAreaViewPython', 'Surface::Cut', 'Surface::Extend', 'Surface::FeatureBlendCurve', 'Surface::Filling', 'Surface::GeomFillSurface', 'Surface::Sections', 'Surface::Sewing', 'TechDraw::FeatureProjection'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Part.Feature:

@overload
def addObject(self, type: Literal['Part::Part2DObject', 'Part::Part2DObjectPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Part.Part2DObject:

@overload
def addObject(self, type: Literal['PartDesign::Body'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _PartDesign.Body:

@overload
def addObject(self, type: Literal['PartDesign::AdditiveBox', 'PartDesign::AdditiveCone', 'PartDesign::AdditiveCylinder', 'PartDesign::AdditiveEllipsoid', 'PartDesign::AdditiveHelix', 'PartDesign::AdditiveLoft', 'PartDesign::AdditivePipe', 'PartDesign::AdditivePrism', 'PartDesign::AdditiveSphere', 'PartDesign::AdditiveTorus', 'PartDesign::AdditiveWedge', 'PartDesign::Boolean', 'PartDesign::Box', 'PartDesign::Chamfer', 'PartDesign::CircularPattern', 'PartDesign::Cone', 'PartDesign::Cylinder', 'PartDesign::Defeaturing', 'PartDesign::Draft', 'PartDesign::DressUp', 'PartDesign::Ellipsoid', 'PartDesign::Feature', 'PartDesign::FeatureAddSub', 'PartDesign::FeatureAddSubPython', 'PartDesign::FeatureAdditivePython', 'PartDesign::FeatureBase', 'PartDesign::FeatureExtrude', 'PartDesign::FeaturePrimitive', 'PartDesign::FeaturePython', 'PartDesign::FeatureRefine', 'PartDesign::FeatureRefinePython', 'PartDesign::FeatureSubtractivePython', 'PartDesign::Fillet', 'PartDesign::Groove', 'PartDesign::Helix', 'PartDesign::Hole', 'PartDesign::LinearPattern', 'PartDesign::Loft', 'PartDesign::Mirrored', 'PartDesign::MultiTransform', 'PartDesign::Pad', 'PartDesign::PathPattern', 'PartDesign::Pipe', 'PartDesign::Pocket', 'PartDesign::PointPattern', 'PartDesign::PolarPattern', 'PartDesign::Prism', 'PartDesign::ProfileBased', 'PartDesign::Revolution', 'PartDesign::Scaled', 'PartDesign::Solid', 'PartDesign::Sphere', 'PartDesign::SubtractiveBox', 'PartDesign::SubtractiveCone', 'PartDesign::SubtractiveCylinder', 'PartDesign::SubtractiveEllipsoid', 'PartDesign::SubtractiveHelix', 'PartDesign::SubtractiveLoft', 'PartDesign::SubtractivePipe', 'PartDesign::SubtractivePrism', 'PartDesign::SubtractiveSphere', 'PartDesign::SubtractiveTorus', 'PartDesign::SubtractiveWedge', 'PartDesign::Thickness', 'PartDesign::Torus', 'PartDesign::Transformed', 'PartDesign::Wedge'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _PartDesign.Feature:

@overload
def addObject(self, type: Literal['Robot::RobotObject'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Robot.RobotObject:

@overload
def addObject(self, type: Literal['Sketcher::SketchObject', 'Sketcher::SketchObjectPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Sketcher.SketchObject:

@overload
def addObject(self, type: Literal['Sketcher::SketchObjectSF'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Sketcher.SketchObjectSF:

@overload
def addObject(self, type: Literal['Spreadsheet::Sheet', 'Spreadsheet::SheetPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _Spreadsheet.Sheet:

@overload
def addObject(self, type: Literal['TechDraw::DrawBrokenView', 'TechDraw::DrawBrokenViewPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawBrokenView:

@overload
def addObject(self, type: Literal['TechDraw::DrawGeomHatch', 'TechDraw::DrawGeomHatchPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawGeomHatch:

@overload
def addObject(self, type: Literal['TechDraw::DrawHatch', 'TechDraw::DrawHatchPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawHatch:

@overload
def addObject(self, type: Literal['TechDraw::DrawLeaderLine', 'TechDraw::DrawLeaderLinePython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawLeaderLine:

@overload
def addObject(self, type: Literal['TechDraw::DrawPage', 'TechDraw::DrawPagePython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawPage:

@overload
def addObject(self, type: Literal['TechDraw::DrawParametricTemplate', 'TechDraw::DrawParametricTemplatePython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawParametricTemplate:

@overload
def addObject(self, type: Literal['TechDraw::DrawProjGroup'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawProjGroup:

@overload
def addObject(self, type: Literal['TechDraw::DrawProjGroupItem'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawProjGroupItem:

@overload
def addObject(self, type: Literal['TechDraw::DrawRichAnno', 'TechDraw::DrawRichAnnoPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawRichAnno:

@overload
def addObject(self, type: Literal['TechDraw::DrawSVGTemplate', 'TechDraw::DrawSVGTemplatePython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawSVGTemplate:

@overload
def addObject(self, type: Literal['TechDraw::DrawTemplate', 'TechDraw::DrawTemplatePython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawTemplate:

@overload
def addObject(self, type: Literal['TechDraw::DrawTile', 'TechDraw::DrawTilePython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawTile:

@overload
def addObject(self, type: Literal['TechDraw::DrawTileWeld', 'TechDraw::DrawTileWeldPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawTileWeld:

@overload
def addObject(self, type: Literal['TechDraw::DrawView', 'TechDraw::DrawViewBalloon', 'TechDraw::DrawViewImage', 'TechDraw::DrawViewImagePython', 'TechDraw::DrawViewPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawView:

@overload
def addObject(self, type: Literal['TechDraw::DrawViewAnnotation', 'TechDraw::DrawViewAnnotationPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawViewAnnotation:

@overload
def addObject(self, type: Literal['TechDraw::DrawViewClip', 'TechDraw::DrawViewClipPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawViewClip:

@overload
def addObject(self, type: Literal['TechDraw::DrawViewCollection'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawViewCollection:

@overload
def addObject(self, type: Literal['TechDraw::DrawViewDimExtent'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawViewDimExtent:

@overload
def addObject(self, type: Literal['TechDraw::DrawViewDimension', 'TechDraw::LandmarkDimension'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawViewDimension:

@overload
def addObject(self, type: Literal['TechDraw::DrawComplexSection', 'TechDraw::DrawComplexSectionPython', 'TechDraw::DrawViewDetail', 'TechDraw::DrawViewDetailPython', 'TechDraw::DrawViewMulti', 'TechDraw::DrawViewMultiPython', 'TechDraw::DrawViewPart', 'TechDraw::DrawViewPartPython', 'TechDraw::DrawViewSection', 'TechDraw::DrawViewSectionPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawViewPart:

@overload
def addObject(self, type: Literal['TechDraw::DrawViewArch', 'TechDraw::DrawViewDraft', 'TechDraw::DrawViewDraftPython', 'TechDraw::DrawViewSpreadsheet', 'TechDraw::DrawViewSpreadsheetPython', 'TechDraw::DrawViewSymbol', 'TechDraw::DrawViewSymbolPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawViewSymbol:

@overload
def addObject(self, type: Literal['TechDraw::DrawWeldSymbol', 'TechDraw::DrawWeldSymbolPython'], name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> _TechDraw.DrawWeldSymbol:

@overload
def addObject(self, type: str, name: str=..., objProxy: object | None=None, viewProxy: object | None=None, attach: bool=False, viewType: str=...) -> DocumentObject:
```

Add an object to document.

Args:
    type: the type of the document object to create.
          Call method supportedTypes() to get a list of possible values.
    name: the optional name of the new object.
    objProxy: the Python binding object to attach to the new document object.
    viewProxy: the Python binding object to attach the view provider of this object.
    attach: if True, then bind the document object first before adding to the document
            to allow Python code to override view provider type. Once bound, and before adding to
            the document, it will try to call Python binding object's attach(obj) method.
    viewType: override the view provider type directly, only effective when attach is False.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1296, 1300, 1304, 1308, 1312, 1316, 1320, 1324, 1328, 1332, 1336, 1340, 1344, 1348, 1352, 1356, 1360, 1364, 1368, 1372, 1376, 1380, 1384, 1388, 1392, 1396, 1400, 1404, 1408, 1412, 1416, 1420, 1424, 1428, 1432, 1436, 1440, 1444, 1448, 1452, 1456, 1460, 1464, 1468, 1472, 1476, 1480, 1484, 1488, 1492, 1496.

## `FreeCAD.Document.addProperty`

```python
def addProperty(self, type: str, name: str, group: str='', doc: str='', attr: int=0, read_only: bool=False, hidden: bool=False, locked: bool=False, enum_vals: list[str] | None=None) -> Document:
```

Add a generic property.

Args:
    type: The type of the property to add.
    name: The name of the property.
    group: The group to which the property belongs. Defaults to "".
    doc: The documentation string for the property. Defaults to "".
    attr: Attribute flags for the property. Defaults to 0.
    read_only: Whether the property is read-only. Defaults to False.
    hidden: Whether the property is hidden. Defaults to False.
    locked: Whether the property is locked. Defaults to False.

Returns:
    The document instance with the added property.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1513.

## `FreeCAD.Document.removeProperty`

```python
def removeProperty(self, name: str, /) -> bool:
```

Remove a generic property.

Note, you can only remove user-defined properties but not built-in ones.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1532.

## `FreeCAD.Document.removeObject`

```python
def removeObject(self, object: str | DocumentObject, /) -> None:
```

Remove an object from the document.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1540.

## `FreeCAD.Document.copyObject`

```python
@overload
def copyObject(self, object: Sequence[DocumentObject], recursive: bool=False, return_all: bool=False) -> tuple[DocumentObject, ...]:

@overload
def copyObject(self, object: DocumentObject, recursive: bool=False, return_all: Literal[False]=False) -> DocumentObject:

@overload
def copyObject(self, object: DocumentObject, recursive: bool=False, return_all: Literal[True]=True) -> DocumentObject | tuple[DocumentObject, ...]:

def copyObject(self, object: DocumentObject | Sequence[DocumentObject], recursive: bool=False, return_all: bool=False) -> DocumentObject | tuple[DocumentObject, ...]:
```

Copy an object or objects from another document to this document.

Args:
    object: can either be a single object or sequence of objects
    recursive: if True, also recursively copies internal objects
    return_all: if True, returns all copied objects, or else return only the copied
                object corresponding to the input objects.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1547, 1551, 1555, 1558.

## `FreeCAD.Document.moveObject`

```python
def moveObject(self, object: DocumentObject, with_dependencies: bool=False, /) -> DocumentObject:
```

Transfers an object from another document to this document.

Args:
    object: can either a single object or sequence of objects
    with_dependencies: if True, all internal dependent objects are copied too.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1570.

## `FreeCAD.Document.importLinks`

```python
def importLinks(self, source: DocumentObject | Sequence[DocumentObject] | None=None, /) -> tuple[DocumentObject, ...]:
```

Import any externally linked object given a list of objects in
this document.  Any link type properties of the input objects
will be automatically reassigned to the imported object

If no object is given as input, it import all externally linked
object of this document.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 1580.

