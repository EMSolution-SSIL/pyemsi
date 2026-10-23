# Python source module `draftviewproviders.view_dimension`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py`. Import path is source-routed; installed availability is unverified.

Provides the viewprovider code for the Dimension objects.

These include linear dimensions, including radius and diameter,
as well as angular dimensions.
They inherit their behavior from the base Annotation viewprovider.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import math

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.math` -> `math`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:39`.

### import pivy.coin as coin

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.coin` -> `pivy.coin`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:40`.

### import lazy_loader.lazy_loader as lz

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.lz` -> `lazy_loader.lazy_loader`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:41`.

### from PySide.QtCore import QT_TRANSLATE_NOOP

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.QT_TRANSLATE_NOOP` -> `PySide.QtCore.QT_TRANSLATE_NOOP`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:42`.

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:44`.

### import DraftVecUtils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.DraftVecUtils` -> `DraftVecUtils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:45`.

### from draftgeoutils import edges as geo_edges

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.geo_edges` -> `draftgeoutils.edges`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:46`.

### from draftgeoutils import general as geo_general

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.geo_general` -> `draftgeoutils.general`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:47`.

### from draftgeoutils import geometry as geo_geometry

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.geo_geometry` -> `draftgeoutils.geometry`.

[Source module `draftgeoutils`](../../draftgeoutils/index.md).

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:48`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:49`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:50`.

### from draftutils import units

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.units` -> `draftutils.units`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:51`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:52`.

### from draftviewproviders.view_draft_annotation import ViewProviderDraftAnnotation

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftviewproviders.view_dimension.ViewProviderDraftAnnotation` -> `draftviewproviders.view_draft_annotation.ViewProviderDraftAnnotation`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftviewproviders/view_dimension.py:53`.

## Classes

- [draftviewproviders.view_dimension.ViewProviderDimensionBase](ViewProviderDimensionBase.md)
- [draftviewproviders.view_dimension.ViewProviderLinearDimension](ViewProviderLinearDimension.md)
- [draftviewproviders.view_dimension.ViewProviderAngularDimension](ViewProviderAngularDimension.md)

## Internal definitions not expanded

`draftviewproviders.view_dimension._ViewProviderDimension`, `draftviewproviders.view_dimension._ViewProviderAngularDimension`. These are source internals unless an explicit export establishes otherwise.

