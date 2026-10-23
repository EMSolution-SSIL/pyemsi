# `PartDesignGui.ViewProvider`

[Module](index.md)

```python
class ViewProvider(ViewProviderPartExt):
```

This is the father of all PartDesign ViewProvider classes

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `PartDesignGui/__init__.pyi` line 7. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PartDesignGui.ViewProvider.setBodyMode`

```python
def setBodyMode(self, mode: bool, /) -> None:
```

body mode means that the object is part of a body
and that the body is used to set the visual properties, not the features. Hence
setting body mode to true will hide most viewprovider properties.

Evidence: public stub `PartDesignGui/__init__.pyi` line(s) 15.

## `PartDesignGui.ViewProvider.makeTemporaryVisible`

```python
def makeTemporaryVisible(self, visible: bool, /) -> None:
```

makes this viewprovider visible in the
scene graph without changing any properties, not the visibility one and also not
the display mode. This can be used to show the shape of this viewprovider from
other viewproviders without doing anything to the document and properties.

Evidence: public stub `PartDesignGui/__init__.pyi` line(s) 23.

