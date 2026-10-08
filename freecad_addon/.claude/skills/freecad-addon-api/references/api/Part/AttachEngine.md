# `Part.AttachEngine`

[Module](index.md)

```python
class AttachEngine(BaseClass):
```

AttachEngine abstract class - the functionality of AttachableObject, but outside of DocumentObject

Author: DeepSOIC (vv.titov@gmail.com)
Licence: LGPL
DeveloperDocu: AttachEngine abstract class

Evidence: public stub `Part/__init__.pyi` line 373. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.AttachEngine.AttacherType`

```python
AttacherType: Final[str] = ''
```

Type of engine: 3d, plane, line, or point.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 381.

## `Part.AttachEngine.Mode`

```python
Mode: str = ''
```

Current attachment mode.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 383.

## `Part.AttachEngine.References`

```python
References: object = ...
```

Current attachment mode.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 385.

## `Part.AttachEngine.AttachmentOffset`

```python
AttachmentOffset: object = ...
```

Current attachment mode.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 387.

## `Part.AttachEngine.Reverse`

```python
Reverse: bool = False
```

If True, Z axis of attached placement is flipped. X axis is flipped in addition (CS has to remain right-handed).

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 389.

## `Part.AttachEngine.Parameter`

```python
Parameter: float = 0.0
```

Value of parameter for some curve attachment modes. Range of 0..1 spans the length of the edge (parameter value can be outside of the range for curves that allow extrapolation.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 391.

## `Part.AttachEngine.CompleteModeList`

```python
CompleteModeList: Final[list] = []
```

List of all attachment modes of all AttachEngines. This is the list of modes in MapMode enum properties of AttachableObjects.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 393.

## `Part.AttachEngine.ImplementedModes`

```python
ImplementedModes: Final[list] = []
```

List of all attachment modes of all AttachEngines. This is the list of modes in MapMode enum properties of AttachableObjects.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 395.

## `Part.AttachEngine.CompleteRefTypeList`

```python
CompleteRefTypeList: Final[list] = []
```

List of all reference shape types recognized by AttachEngine.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Part/__init__.pyi` line(s) 397.

## `Part.AttachEngine.getModeInfo`

```python
def getModeInfo(self, mode: str, /) -> dict:
```

getModeInfo(mode): returns supported reference combinations, user-friendly name, and so on.

Evidence: public stub `Part/__init__.pyi` line(s) 400.

## `Part.AttachEngine.getRefTypeOfShape`

```python
def getRefTypeOfShape(self, shape: str, /) -> str:
```

getRefTypeOfShape(shape): returns shape type as interpreted by AttachEngine. Returns a string.

Evidence: public stub `Part/__init__.pyi` line(s) 406.

## `Part.AttachEngine.isFittingRefType`

```python
def isFittingRefType(self, type_shape: str, type_needed: str, /) -> bool:
```

isFittingRefType(type_shape, type_needed): tests if shape type, specified by type_shape (string), fits a type required by attachment mode type_needed (string). e.g. 'Circle' fits a requirement of 'Edge', and 'Curve' doesn't fit if a 'Circle' is required.

Evidence: public stub `Part/__init__.pyi` line(s) 412.

## `Part.AttachEngine.downgradeRefType`

```python
def downgradeRefType(self, type: str, /) -> str:
```

downgradeRefType(type): returns next more general type. E.g. downgradeType('Circle') yields 'Curve'.

Evidence: public stub `Part/__init__.pyi` line(s) 418.

## `Part.AttachEngine.getRefTypeInfo`

```python
def getRefTypeInfo(self, type: str, /) -> dict:
```

getRefTypeInfo(type): returns information (dict) on shape type. Keys:'UserFriendlyName', 'TypeIndex', 'Rank'. Rank is the number of times reftype can be downgraded, before it becomes 'Any'.

Evidence: public stub `Part/__init__.pyi` line(s) 424.

## `Part.AttachEngine.copy`

```python
def copy(self) -> 'AttachEngine':
```

copy(): returns a new instance of AttachEngine.

Evidence: public stub `Part/__init__.pyi` line(s) 430.

## `Part.AttachEngine.calculateAttachedPlacement`

```python
def calculateAttachedPlacement(self, orig_placement: Placement, /) -> Optional[Placement]:
```

calculateAttachedPlacement(orig_placement): returns result of attachment, based
on current Mode, References, etc. AttachmentOffset is included.

original_placement is the previous placement of the object being attached. It
is used to preserve orientation for Translate attachment mode. For other modes,
it is ignored.

Returns the new placement. If not attached, returns None. If attachment fails,
an exception is raised.

Evidence: public stub `Part/__init__.pyi` line(s) 436.

## `Part.AttachEngine.suggestModes`

```python
def suggestModes(self) -> dict:
```

suggestModes(): runs mode suggestion routine and returns a dictionary with
results and supplementary information.

Keys:
'allApplicableModes': list of modes that can accept current references. Note
that it is only a check by types, and does not guarantee the modes will
actually work.

'bestFitMode': mode that fits current references best. Note that the mode may
not be valid for the set of references; check for if 'message' is 'OK'.

'error': error message for when 'message' is 'UnexpectedError' or
'LinkBroken'.

'message': general result of suggestion. 'IncompatibleGeometry', 'NoModesFit':
no modes accept current set of references; 'OK': some modes do accept current
set of references (though it's not guarantted the modes will work - surrestor
only checks for correct types); 'UnexpectedError': should never happen.

'nextRefTypeHint': what more can be added to references to reach other modes
('reachableModes' provide more extended information on this)

'reachableModes': a dict, where key is mode, and value is a list of sequences
of references that can be added to fit that mode.

'references_Types': a list of types of geometry linked by references (that's
the input information for suggestor, actually).

Evidence: public stub `Part/__init__.pyi` line(s) 450.

## `Part.AttachEngine.readParametersFromFeature`

```python
def readParametersFromFeature(self, document_object: DocumentObject, /) -> None:
```

readParametersFromFeature(document_object): sets AttachEngine parameters (References, Mode, etc.) by reading out properties of AttachableObject-derived feature.

Evidence: public stub `Part/__init__.pyi` line(s) 482.

## `Part.AttachEngine.writeParametersToFeature`

```python
def writeParametersToFeature(self, document_object: DocumentObject, /) -> None:
```

writeParametersToFeature(document_object): updates properties of
AttachableObject-derived feature with current AttachEngine parameters
(References, Mode, etc.).

Warning: if a feature linked by AttachEngine.References was deleted, this method
will crash FreeCAD.

Evidence: public stub `Part/__init__.pyi` line(s) 488.

