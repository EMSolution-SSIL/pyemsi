# `PartGui.ViewProviderPreviewExtension`

[Module](index.md)

```python
class ViewProviderPreviewExtension(ViewProviderExtension):
```

Provides a 3D preview of an upcoming geometry change.

The view provider's Proxy may define three optional hooks:

- attachPreview(self, vext) and updatePreview(self, vext) run AFTER the
  C++ default and augment its result (add nodes, rewire the scene graph).
- getPreviewShape(self, vext) -> Part.Shape | None REPLACES the default
  shape when it returns one; returning None keeps the default.

A Coin node held in a Python attribute across calls - e.g. shared between
updatePreview() invocations - is not kept alive by that reference alone;
unlike Gui::CoinPtr on the C++ side, a SWIG pointer does not ref() the
underlying SoBase. Call node.ref() while retaining such a node, or it may be
freed the moment its last scene graph parent is removed, crashing on next
use, and pair that with node.unref() once it is no longer retained.

Evidence: public stub `PartGui/__init__.pyi` line 90. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PartGui.ViewProviderPreviewExtension.PreviewRootNode`

```python
PreviewRootNode: Final[Any] = ...
```


    Root of the preview scene graph, as a pivy SoSeparator.

    Children may be added, removed, or replaced wholesale from an
    attachPreview or updatePreview hook.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PartGui/__init__.pyi` line(s) 108.

## `PartGui.ViewProviderPreviewExtension.PreviewShapeNode`

```python
PreviewShapeNode: Final[Any] = ...
```


    The SoPreviewShape the default implementation feeds with the preview shape.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PartGui/__init__.pyi` line(s) 110.

## `PartGui.ViewProviderPreviewExtension.showPreview`

```python
def showPreview(self, enable: bool, /) -> None:
```

Show or hide the preview in the 3D view.

Evidence: public stub `PartGui/__init__.pyi` line(s) 113.

## `PartGui.ViewProviderPreviewExtension.isPreviewEnabled`

```python
def isPreviewEnabled(self) -> bool:
```

Returns if the preview is currently shown.

Evidence: public stub `PartGui/__init__.pyi` line(s) 119.

## `PartGui.ViewProviderPreviewExtension.updatePreview`

```python
def updatePreview(self) -> None:
```

Rebuild the preview scene graph.

Use when the preview arrangement depends on data other than PreviewShape,
which is the only property that triggers a rebuild automatically.

Never call this from inside an updatePreview hook - it dispatches back
into that hook and recurses.

Evidence: public stub `PartGui/__init__.pyi` line(s) 125.

## `PartGui.ViewProviderPreviewExtension.updatePreviewShape`

```python
def updatePreviewShape(self, shape: Any, node: Any, /) -> None:
```

Tessellate a Part.Shape into an SoPreviewShape node, honouring the view
provider's Deviation and AngularDeflection.

Raises TypeError if node is not an SoPreviewShape.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `PartGui/__init__.pyi` line(s) 137.

