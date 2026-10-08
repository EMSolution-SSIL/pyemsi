# `Part.PreviewExtension`

[Module](index.md)

```python
class PreviewExtension(DocumentObjectExtension):
```

Computes the shape shown as a semi-transparent 3D preview of an upcoming
geometry change.

Evidence: public stub `Part/__init__.pyi` line 3260. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Part.PreviewExtension.updatePreview`

```python
def updatePreview(self) -> None:
```

Recompute the preview shape if it is stale.

Does nothing while the preview is fresh. Pair with invalidatePreview()
to force a recompute.

Evidence: public stub `Part/__init__.pyi` line(s) 3266.

## `Part.PreviewExtension.invalidatePreview`

```python
def invalidatePreview(self) -> None:
```

Mark the preview stale so the next updatePreview() recomputes it.

Evidence: public stub `Part/__init__.pyi` line(s) 3275.

## `Part.PreviewExtension.isPreviewFresh`

```python
def isPreviewFresh(self) -> bool:
```

Returns whether the preview shape is up to date with the object's inputs.

Evidence: public stub `Part/__init__.pyi` line(s) 3281.

