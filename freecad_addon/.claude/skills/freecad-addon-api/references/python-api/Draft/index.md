# Python source module `Draft`

[Python catalogue](../index.md)

Evidence: `src/Mod/Draft/Draft.py`. Import path is source-routed; installed availability is unverified.

Provide the Draft Workbench public programming interface.

The Draft module offers tools to create and manipulate 2D objects.
The functions in this file must be usable without requiring the
graphical user interface.
These functions can be used as the backend for the graphical commands
defined in `DraftTools.py`.

Literal `__all__`: not available; source names do not imply supported public API.

[part 1](index.md) | [part 2](index-2.md)

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `Draft.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/Draft.py:37`.

### import Draft_rc

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `Draft.Draft_rc` -> `Draft_rc`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/Draft.py:40`.

### from draftutils.utils import ARROW_TYPES as arrowtypes

Facade reexport declaration.

Bound source name `Draft.arrowtypes` -> `draftutils.utils.ARROW_TYPES`.

[Source module `draftutils.utils`](../draftutils/utils/index.md).

Evidence: `src/Mod/Draft/Draft.py:57`.

### from draftutils.utils import type_check, typecheck, precision, tolerance

Facade reexport declaration.

Bound source name `Draft.type_check` -> `draftutils.utils.type_check`.

Bound source name `Draft.typecheck` -> `draftutils.utils.typecheck`.

Bound source name `Draft.precision` -> `draftutils.utils.precision`.

Bound source name `Draft.tolerance` -> `draftutils.utils.tolerance`.

[Source module `draftutils.utils`](../draftutils/utils/index.md).

Evidence: `src/Mod/Draft/Draft.py:59`.

### from draftutils.utils import get_real_name, getRealName, get_type, getType, get_objects_of_type, getObjectsOfType, is_clone, isClone, get_clone_base, getCloneBase, print_shape, printShape, compare_objects, compareObjects, shapify, is_closed_edge

Facade reexport declaration.

Bound source name `Draft.get_real_name` -> `draftutils.utils.get_real_name`.

Bound source name `Draft.getRealName` -> `draftutils.utils.getRealName`.

Bound source name `Draft.get_type` -> `draftutils.utils.get_type`.

Bound source name `Draft.getType` -> `draftutils.utils.getType`.

Bound source name `Draft.get_objects_of_type` -> `draftutils.utils.get_objects_of_type`.

Bound source name `Draft.getObjectsOfType` -> `draftutils.utils.getObjectsOfType`.

Bound source name `Draft.is_clone` -> `draftutils.utils.is_clone`.

Bound source name `Draft.isClone` -> `draftutils.utils.isClone`.

Bound source name `Draft.get_clone_base` -> `draftutils.utils.get_clone_base`.

Bound source name `Draft.getCloneBase` -> `draftutils.utils.getCloneBase`.

Bound source name `Draft.print_shape` -> `draftutils.utils.print_shape`.

Bound source name `Draft.printShape` -> `draftutils.utils.printShape`.

Bound source name `Draft.compare_objects` -> `draftutils.utils.compare_objects`.

Bound source name `Draft.compareObjects` -> `draftutils.utils.compareObjects`.

Bound source name `Draft.shapify` -> `draftutils.utils.shapify`.

Bound source name `Draft.is_closed_edge` -> `draftutils.utils.is_closed_edge`.

[Source module `draftutils.utils`](../draftutils/utils/index.md).

Evidence: `src/Mod/Draft/Draft.py:61`.

### from draftutils.utils import string_encode_coin, stringencodecoin, load_svg_patterns, loadSvgPatterns, svg_patterns, svgpatterns, get_rgb, getrgb, argb_to_rgba, rgba_to_argb, get_rgba_tuple

Facade reexport declaration.

Bound source name `Draft.string_encode_coin` -> `draftutils.utils.string_encode_coin`.

Bound source name `Draft.stringencodecoin` -> `draftutils.utils.stringencodecoin`.

Bound source name `Draft.load_svg_patterns` -> `draftutils.utils.load_svg_patterns`.

Bound source name `Draft.loadSvgPatterns` -> `draftutils.utils.loadSvgPatterns`.

Bound source name `Draft.svg_patterns` -> `draftutils.utils.svg_patterns`.

Bound source name `Draft.svgpatterns` -> `draftutils.utils.svgpatterns`.

Bound source name `Draft.get_rgb` -> `draftutils.utils.get_rgb`.

Bound source name `Draft.getrgb` -> `draftutils.utils.getrgb`.

Bound source name `Draft.argb_to_rgba` -> `draftutils.utils.argb_to_rgba`.

Bound source name `Draft.rgba_to_argb` -> `draftutils.utils.rgba_to_argb`.

Bound source name `Draft.get_rgba_tuple` -> `draftutils.utils.get_rgba_tuple`.

[Source module `draftutils.utils`](../draftutils/utils/index.md).

Evidence: `src/Mod/Draft/Draft.py:80`.

### from draftfunctions.svg import get_svg, getSVG

Facade reexport declaration.

Bound source name `Draft.get_svg` -> `draftfunctions.svg.get_svg`.

Bound source name `Draft.getSVG` -> `draftfunctions.svg.getSVG`.

[Source module `draftfunctions.svg`](../draftfunctions/svg/index.md).

Evidence: `src/Mod/Draft/Draft.py:94`.

### from draftfunctions.dxf import get_dxf, getDXF

Facade reexport declaration.

Bound source name `Draft.get_dxf` -> `draftfunctions.dxf.get_dxf`.

Bound source name `Draft.getDXF` -> `draftfunctions.dxf.getDXF`.

[Source module `draftfunctions.dxf`](../draftfunctions/dxf/index.md).

Evidence: `src/Mod/Draft/Draft.py:96`.

### from draftutils.gui_utils import get3DView, get_3d_view, autogroup, removeHidden, remove_hidden, get_diffuse_color, apply_current_style, restore_view_object, formatObject, format_object, getSelection, get_selection, getSelectionEx, get_selection_ex, select, loadTexture, load_texture, get_bbox, end_all_events

Facade reexport declaration.

Bound source name `Draft.get3DView` -> `draftutils.gui_utils.get3DView`.

Bound source name `Draft.get_3d_view` -> `draftutils.gui_utils.get_3d_view`.

Bound source name `Draft.autogroup` -> `draftutils.gui_utils.autogroup`.

Bound source name `Draft.removeHidden` -> `draftutils.gui_utils.removeHidden`.

Bound source name `Draft.remove_hidden` -> `draftutils.gui_utils.remove_hidden`.

Bound source name `Draft.get_diffuse_color` -> `draftutils.gui_utils.get_diffuse_color`.

Bound source name `Draft.apply_current_style` -> `draftutils.gui_utils.apply_current_style`.

Bound source name `Draft.restore_view_object` -> `draftutils.gui_utils.restore_view_object`.

Bound source name `Draft.formatObject` -> `draftutils.gui_utils.formatObject`.

Bound source name `Draft.format_object` -> `draftutils.gui_utils.format_object`.

Bound source name `Draft.getSelection` -> `draftutils.gui_utils.getSelection`.

Bound source name `Draft.get_selection` -> `draftutils.gui_utils.get_selection`.

Bound source name `Draft.getSelectionEx` -> `draftutils.gui_utils.getSelectionEx`.

Bound source name `Draft.get_selection_ex` -> `draftutils.gui_utils.get_selection_ex`.

Bound source name `Draft.select` -> `draftutils.gui_utils.select`.

Bound source name `Draft.loadTexture` -> `draftutils.gui_utils.loadTexture`.

Bound source name `Draft.load_texture` -> `draftutils.gui_utils.load_texture`.

Bound source name `Draft.get_bbox` -> `draftutils.gui_utils.get_bbox`.

Bound source name `Draft.end_all_events` -> `draftutils.gui_utils.end_all_events`.

[Source module `draftutils.gui_utils`](../draftutils/gui_utils/index.md).

Evidence: `src/Mod/Draft/Draft.py:98`.

### from draftutils.gui_utils import dim_symbol, dimSymbol, dim_dash, dimDash

Facade reexport declaration.

Bound source name `Draft.dim_symbol` -> `draftutils.gui_utils.dim_symbol`.

Bound source name `Draft.dimSymbol` -> `draftutils.gui_utils.dimSymbol`.

Bound source name `Draft.dim_dash` -> `draftutils.gui_utils.dim_dash`.

Bound source name `Draft.dimDash` -> `draftutils.gui_utils.dimDash`.

[Source module `draftutils.gui_utils`](../draftutils/gui_utils/index.md).

Evidence: `src/Mod/Draft/Draft.py:120`.

### from draftutils.groups import is_group, get_group_names, getGroupNames, ungroup, get_windows, get_group_contents, getGroupContents, get_movable_children, getMovableChildren

Facade reexport declaration.

Bound source name `Draft.is_group` -> `draftutils.groups.is_group`.

Bound source name `Draft.get_group_names` -> `draftutils.groups.get_group_names`.

Bound source name `Draft.getGroupNames` -> `draftutils.groups.getGroupNames`.

Bound source name `Draft.ungroup` -> `draftutils.groups.ungroup`.

Bound source name `Draft.get_windows` -> `draftutils.groups.get_windows`.

Bound source name `Draft.get_group_contents` -> `draftutils.groups.get_group_contents`.

Bound source name `Draft.getGroupContents` -> `draftutils.groups.getGroupContents`.

Bound source name `Draft.get_movable_children` -> `draftutils.groups.get_movable_children`.

Bound source name `Draft.getMovableChildren` -> `draftutils.groups.getMovableChildren`.

[Source module `draftutils.groups`](../draftutils/groups/index.md).

Evidence: `src/Mod/Draft/Draft.py:122`.

### from draftfunctions.array import array

Facade reexport declaration.

Bound source name `Draft.array` -> `draftfunctions.array.array`.

[Source module `draftfunctions.array`](../draftfunctions/array/index.md).

Evidence: `src/Mod/Draft/Draft.py:137`.

### from draftfunctions.cut import cut

Facade reexport declaration.

Bound source name `Draft.cut` -> `draftfunctions.cut.cut`.

[Source module `draftfunctions.cut`](../draftfunctions/cut/index.md).

Evidence: `src/Mod/Draft/Draft.py:139`.

### from draftfunctions.downgrade import downgrade

Facade reexport declaration.

Bound source name `Draft.downgrade` -> `draftfunctions.downgrade.downgrade`.

[Source module `draftfunctions.downgrade`](../draftfunctions/downgrade/index.md).

Evidence: `src/Mod/Draft/Draft.py:141`.

### from draftfunctions.draftify import draftify

Facade reexport declaration.

Bound source name `Draft.draftify` -> `draftfunctions.draftify.draftify`.

[Source module `draftfunctions.draftify`](../draftfunctions/draftify/index.md).

Evidence: `src/Mod/Draft/Draft.py:143`.

### from draftfunctions.extrude import extrude

Facade reexport declaration.

Bound source name `Draft.extrude` -> `draftfunctions.extrude.extrude`.

[Source module `draftfunctions.extrude`](../draftfunctions/extrude/index.md).

Evidence: `src/Mod/Draft/Draft.py:145`.

### from draftfunctions.fuse import fuse

Facade reexport declaration.

Bound source name `Draft.fuse` -> `draftfunctions.fuse.fuse`.

[Source module `draftfunctions.fuse`](../draftfunctions/fuse/index.md).

Evidence: `src/Mod/Draft/Draft.py:147`.

### from draftfunctions.heal import heal

Facade reexport declaration.

Bound source name `Draft.heal` -> `draftfunctions.heal.heal`.

[Source module `draftfunctions.heal`](../draftfunctions/heal/index.md).

Evidence: `src/Mod/Draft/Draft.py:149`.

### from draftfunctions.move import move, move_vertex, move_edge, copy_moved_edge

Facade reexport declaration.

Bound source name `Draft.move` -> `draftfunctions.move.move`.

Bound source name `Draft.move_vertex` -> `draftfunctions.move.move_vertex`.

Bound source name `Draft.move_edge` -> `draftfunctions.move.move_edge`.

Bound source name `Draft.copy_moved_edge` -> `draftfunctions.move.copy_moved_edge`.

[Source module `draftfunctions.move`](../draftfunctions/move/index.md).

Evidence: `src/Mod/Draft/Draft.py:151`.

### from draftfunctions.rotate import rotate, rotate_vertex, rotate_edge, copy_rotated_edge

Facade reexport declaration.

Bound source name `Draft.rotate` -> `draftfunctions.rotate.rotate`.

Bound source name `Draft.rotate_vertex` -> `draftfunctions.rotate.rotate_vertex`.

Bound source name `Draft.rotate_edge` -> `draftfunctions.rotate.rotate_edge`.

Bound source name `Draft.copy_rotated_edge` -> `draftfunctions.rotate.copy_rotated_edge`.

[Source module `draftfunctions.rotate`](../draftfunctions/rotate/index.md).

Evidence: `src/Mod/Draft/Draft.py:153`.

### from draftfunctions.scale import scale, scale_vertex, scale_edge, copy_scaled_edge

Facade reexport declaration.

Bound source name `Draft.scale` -> `draftfunctions.scale.scale`.

Bound source name `Draft.scale_vertex` -> `draftfunctions.scale.scale_vertex`.

Bound source name `Draft.scale_edge` -> `draftfunctions.scale.scale_edge`.

Bound source name `Draft.copy_scaled_edge` -> `draftfunctions.scale.copy_scaled_edge`.

[Source module `draftfunctions.scale`](../draftfunctions/scale/index.md).

Evidence: `src/Mod/Draft/Draft.py:155`.

### from draftfunctions.join import join_wires, joinWires, join_two_wires, joinTwoWires

Facade reexport declaration.

Bound source name `Draft.join_wires` -> `draftfunctions.join.join_wires`.

Bound source name `Draft.joinWires` -> `draftfunctions.join.joinWires`.

Bound source name `Draft.join_two_wires` -> `draftfunctions.join.join_two_wires`.

Bound source name `Draft.joinTwoWires` -> `draftfunctions.join.joinTwoWires`.

[Source module `draftfunctions.join`](../draftfunctions/join/index.md).

Evidence: `src/Mod/Draft/Draft.py:157`.

### from draftfunctions.split import split

Facade reexport declaration.

Bound source name `Draft.split` -> `draftfunctions.split.split`.

[Source module `draftfunctions.split`](../draftfunctions/split/index.md).

Evidence: `src/Mod/Draft/Draft.py:159`.

### from draftfunctions.offset import offset

Facade reexport declaration.

Bound source name `Draft.offset` -> `draftfunctions.offset.offset`.

[Source module `draftfunctions.offset`](../draftfunctions/offset/index.md).

Evidence: `src/Mod/Draft/Draft.py:161`.

### from draftfunctions.mirror import mirror

Facade reexport declaration.

Bound source name `Draft.mirror` -> `draftfunctions.mirror.mirror`.

[Source module `draftfunctions.mirror`](../draftfunctions/mirror/index.md).

Evidence: `src/Mod/Draft/Draft.py:163`.

### from draftfunctions.upgrade import upgrade

Facade reexport declaration.

Bound source name `Draft.upgrade` -> `draftfunctions.upgrade.upgrade`.

[Source module `draftfunctions.upgrade`](../draftfunctions/upgrade/index.md).

Evidence: `src/Mod/Draft/Draft.py:165`.

### from draftobjects.base import DraftObject, _DraftObject

Facade reexport declaration.

Bound source name `Draft.DraftObject` -> `draftobjects.base.DraftObject`.

Bound source name `Draft._DraftObject` -> `draftobjects.base._DraftObject`.

[Source module `draftobjects.base`](../draftobjects/base/index.md).

Evidence: `src/Mod/Draft/Draft.py:172`.

### from draftviewproviders.view_base import ViewProviderDraft, _ViewProviderDraft, ViewProviderDraftAlt, _ViewProviderDraftAlt, ViewProviderDraftPart, _ViewProviderDraftPart

Facade reexport declaration.

Bound source name `Draft.ViewProviderDraft` -> `draftviewproviders.view_base.ViewProviderDraft`.

Bound source name `Draft._ViewProviderDraft` -> `draftviewproviders.view_base._ViewProviderDraft`.

Bound source name `Draft.ViewProviderDraftAlt` -> `draftviewproviders.view_base.ViewProviderDraftAlt`.

Bound source name `Draft._ViewProviderDraftAlt` -> `draftviewproviders.view_base._ViewProviderDraftAlt`.

Bound source name `Draft.ViewProviderDraftPart` -> `draftviewproviders.view_base.ViewProviderDraftPart`.

Bound source name `Draft._ViewProviderDraftPart` -> `draftviewproviders.view_base._ViewProviderDraftPart`.

[Source module `draftviewproviders.view_base`](../draftviewproviders/view_base/index.md).

Evidence: `src/Mod/Draft/Draft.py:175`.

### from draftobjects.draftlink import DraftLink, _DraftLink

Facade reexport declaration.

Bound source name `Draft.DraftLink` -> `draftobjects.draftlink.DraftLink`.

Bound source name `Draft._DraftLink` -> `draftobjects.draftlink._DraftLink`.

[Source module `draftobjects.draftlink`](../draftobjects/draftlink/index.md).

Evidence: `src/Mod/Draft/Draft.py:185`.

### from draftviewproviders.view_draftlink import ViewProviderDraftLink, _ViewProviderDraftLink

Facade reexport declaration.

Bound source name `Draft.ViewProviderDraftLink` -> `draftviewproviders.view_draftlink.ViewProviderDraftLink`.

Bound source name `Draft._ViewProviderDraftLink` -> `draftviewproviders.view_draftlink._ViewProviderDraftLink`.

[Source module `draftviewproviders.view_draftlink`](../draftviewproviders/view_draftlink/index.md).

Evidence: `src/Mod/Draft/Draft.py:186`.

### from draftobjects.circle import Circle, _Circle

Facade reexport declaration.

Bound source name `Draft.Circle` -> `draftobjects.circle.Circle`.

Bound source name `Draft._Circle` -> `draftobjects.circle._Circle`.

[Source module `draftobjects.circle`](../draftobjects/circle/index.md).

Evidence: `src/Mod/Draft/Draft.py:189`.

### from draftmake.make_circle import make_circle, makeCircle

Facade reexport declaration.

Bound source name `Draft.make_circle` -> `draftmake.make_circle.make_circle`.

Bound source name `Draft.makeCircle` -> `draftmake.make_circle.makeCircle`.

[Source module `draftmake.make_circle`](../draftmake/make_circle/index.md).

Evidence: `src/Mod/Draft/Draft.py:190`.

### from draftmake.make_arc_3points import make_arc_3_points, make_arc_3points

Facade reexport declaration.

Bound source name `Draft.make_arc_3_points` -> `draftmake.make_arc_3points.make_arc_3_points`.

Bound source name `Draft.make_arc_3points` -> `draftmake.make_arc_3points.make_arc_3points`.

[Source module `draftmake.make_arc_3points`](../draftmake/make_arc_3points/index.md).

Evidence: `src/Mod/Draft/Draft.py:193`.

### from draftobjects.ellipse import Ellipse, _Ellipse

Facade reexport declaration.

Bound source name `Draft.Ellipse` -> `draftobjects.ellipse.Ellipse`.

Bound source name `Draft._Ellipse` -> `draftobjects.ellipse._Ellipse`.

[Source module `draftobjects.ellipse`](../draftobjects/ellipse/index.md).

Evidence: `src/Mod/Draft/Draft.py:196`.

### from draftmake.make_ellipse import make_ellipse, makeEllipse

Facade reexport declaration.

Bound source name `Draft.make_ellipse` -> `draftmake.make_ellipse.make_ellipse`.

Bound source name `Draft.makeEllipse` -> `draftmake.make_ellipse.makeEllipse`.

[Source module `draftmake.make_ellipse`](../draftmake/make_ellipse/index.md).

Evidence: `src/Mod/Draft/Draft.py:197`.

### from draftobjects.rectangle import Rectangle, _Rectangle

Facade reexport declaration.

Bound source name `Draft.Rectangle` -> `draftobjects.rectangle.Rectangle`.

Bound source name `Draft._Rectangle` -> `draftobjects.rectangle._Rectangle`.

[Source module `draftobjects.rectangle`](../draftobjects/rectangle/index.md).

Evidence: `src/Mod/Draft/Draft.py:200`.

### from draftmake.make_rectangle import make_rectangle, makeRectangle

Facade reexport declaration.

Bound source name `Draft.make_rectangle` -> `draftmake.make_rectangle.make_rectangle`.

Bound source name `Draft.makeRectangle` -> `draftmake.make_rectangle.makeRectangle`.

[Source module `draftmake.make_rectangle`](../draftmake/make_rectangle/index.md).

Evidence: `src/Mod/Draft/Draft.py:201`.

### from draftviewproviders.view_rectangle import ViewProviderRectangle, _ViewProviderRectangle

Facade reexport declaration.

Conditions: `if App.GuiUp`.

Bound source name `Draft.ViewProviderRectangle` -> `draftviewproviders.view_rectangle.ViewProviderRectangle`.

Bound source name `Draft._ViewProviderRectangle` -> `draftviewproviders.view_rectangle._ViewProviderRectangle`.

[Source module `draftviewproviders.view_rectangle`](../draftviewproviders/view_rectangle/index.md).

Evidence: `src/Mod/Draft/Draft.py:204`.

### from draftobjects.polygon import Polygon, _Polygon

Facade reexport declaration.

Bound source name `Draft.Polygon` -> `draftobjects.polygon.Polygon`.

Bound source name `Draft._Polygon` -> `draftobjects.polygon._Polygon`.

[Source module `draftobjects.polygon`](../draftobjects/polygon/index.md).

Evidence: `src/Mod/Draft/Draft.py:207`.

### from draftmake.make_polygon import make_polygon, makePolygon

Facade reexport declaration.

Bound source name `Draft.make_polygon` -> `draftmake.make_polygon.make_polygon`.

Bound source name `Draft.makePolygon` -> `draftmake.make_polygon.makePolygon`.

[Source module `draftmake.make_polygon`](../draftmake/make_polygon/index.md).

Evidence: `src/Mod/Draft/Draft.py:208`.

### from draftobjects.wire import Wire, _Wire

Facade reexport declaration.

Bound source name `Draft.Wire` -> `draftobjects.wire.Wire`.

Bound source name `Draft._Wire` -> `draftobjects.wire._Wire`.

[Source module `draftobjects.wire`](../draftobjects/wire/index.md).

Evidence: `src/Mod/Draft/Draft.py:211`.

### from draftmake.make_line import make_line, makeLine

Facade reexport declaration.

Bound source name `Draft.make_line` -> `draftmake.make_line.make_line`.

Bound source name `Draft.makeLine` -> `draftmake.make_line.makeLine`.

[Source module `draftmake.make_line`](../draftmake/make_line/index.md).

Evidence: `src/Mod/Draft/Draft.py:213`.

### from draftmake.make_wire import make_wire, makeWire

Facade reexport declaration.

Bound source name `Draft.make_wire` -> `draftmake.make_wire.make_wire`.

Bound source name `Draft.makeWire` -> `draftmake.make_wire.makeWire`.

[Source module `draftmake.make_wire`](../draftmake/make_wire/index.md).

Evidence: `src/Mod/Draft/Draft.py:214`.

### from draftviewproviders.view_wire import ViewProviderWire, _ViewProviderWire

Facade reexport declaration.

Conditions: `if App.GuiUp`.

Bound source name `Draft.ViewProviderWire` -> `draftviewproviders.view_wire.ViewProviderWire`.

Bound source name `Draft._ViewProviderWire` -> `draftviewproviders.view_wire._ViewProviderWire`.

[Source module `draftviewproviders.view_wire`](../draftviewproviders/view_wire/index.md).

Evidence: `src/Mod/Draft/Draft.py:217`.

### from draftobjects.bspline import BSpline, _BSpline

Facade reexport declaration.

Bound source name `Draft.BSpline` -> `draftobjects.bspline.BSpline`.

Bound source name `Draft._BSpline` -> `draftobjects.bspline._BSpline`.

[Source module `draftobjects.bspline`](../draftobjects/bspline/index.md).

Evidence: `src/Mod/Draft/Draft.py:220`.

### from draftmake.make_bspline import make_bspline, makeBSpline

Facade reexport declaration.

Bound source name `Draft.make_bspline` -> `draftmake.make_bspline.make_bspline`.

Bound source name `Draft.makeBSpline` -> `draftmake.make_bspline.makeBSpline`.

[Source module `draftmake.make_bspline`](../draftmake/make_bspline/index.md).

Evidence: `src/Mod/Draft/Draft.py:221`.

### from draftviewproviders.view_bspline import ViewProviderBSpline, _ViewProviderBSpline

Facade reexport declaration.

Conditions: `if App.GuiUp`.

Bound source name `Draft.ViewProviderBSpline` -> `draftviewproviders.view_bspline.ViewProviderBSpline`.

Bound source name `Draft._ViewProviderBSpline` -> `draftviewproviders.view_bspline._ViewProviderBSpline`.

[Source module `draftviewproviders.view_bspline`](../draftviewproviders/view_bspline/index.md).

Evidence: `src/Mod/Draft/Draft.py:224`.

### from draftobjects.bezcurve import BezCurve, _BezCurve

Facade reexport declaration.

Bound source name `Draft.BezCurve` -> `draftobjects.bezcurve.BezCurve`.

Bound source name `Draft._BezCurve` -> `draftobjects.bezcurve._BezCurve`.

[Source module `draftobjects.bezcurve`](../draftobjects/bezcurve/index.md).

Evidence: `src/Mod/Draft/Draft.py:227`.

### from draftmake.make_bezcurve import make_bez_curve, make_bezcurve, makeBezCurve

Facade reexport declaration.

Bound source name `Draft.make_bez_curve` -> `draftmake.make_bezcurve.make_bez_curve`.

Bound source name `Draft.make_bezcurve` -> `draftmake.make_bezcurve.make_bezcurve`.

Bound source name `Draft.makeBezCurve` -> `draftmake.make_bezcurve.makeBezCurve`.

[Source module `draftmake.make_bezcurve`](../draftmake/make_bezcurve/index.md).

Evidence: `src/Mod/Draft/Draft.py:228`.

