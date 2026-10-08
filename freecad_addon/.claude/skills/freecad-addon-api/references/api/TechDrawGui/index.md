# `TechDrawGui`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `TechDrawGui/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Classes

- [TechDrawGui.QGSPage](QGSPage.md)
- [TechDrawGui._MDIViewPage](_MDIViewPage.md)

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from collections.abc import Sequence
from TechDraw import DrawPage, DrawView
from typing import Any
```

## `TechDrawGui.export`

```python
def export(objects: Sequence[DrawPage], filename: str, /) -> None:
```

Export one or more selected TechDraw pages through the GUI export hook.

Evidence: public stub `TechDrawGui/__init__.pyi` line(s) 12.

## `TechDrawGui.exportPageAsPdf`

```python
def exportPageAsPdf(page: DrawPage, filename: str, /) -> None:
```

Export one TechDraw page as one PDF file.

Evidence: public stub `TechDrawGui/__init__.pyi` line(s) 16.

## `TechDrawGui.exportPageAsSvg`

```python
def exportPageAsSvg(page: DrawPage, filename: str, /) -> None:
```

Export one TechDraw page as one SVG file.

Evidence: public stub `TechDrawGui/__init__.pyi` line(s) 20.

## `TechDrawGui.addQGIToView`

```python
def addQGIToView(view: DrawView, item: object, /) -> None:
```

Insert one Qt graphics item into a TechDraw view's graphics item tree.

Evidence: public stub `TechDrawGui/__init__.pyi` line(s) 24.

## `TechDrawGui.addQGObjToView`

```python
def addQGObjToView(view: DrawView, item: object, /) -> None:
```

Insert one Qt graphics object into a TechDraw view's graphics item tree.

Evidence: public stub `TechDrawGui/__init__.pyi` line(s) 28.

## `TechDrawGui.addQGIToScene`

```python
def addQGIToScene(page: DrawPage, item: object, /) -> None:
```

Insert one Qt graphics item directly into a TechDraw page scene.

Evidence: public stub `TechDrawGui/__init__.pyi` line(s) 32.

## `TechDrawGui.addQGObjToScene`

```python
def addQGObjToScene(page: DrawPage, item: object, /) -> None:
```

Insert one Qt graphics object directly into a TechDraw page scene.

Evidence: public stub `TechDrawGui/__init__.pyi` line(s) 36.

## `TechDrawGui.getSceneForPage`

```python
def getSceneForPage(page: DrawPage, /) -> QGSPage | None:
```

Return the scene wrapper associated with one TechDraw page.

Evidence: public stub `TechDrawGui/__init__.pyi` line(s) 40.

