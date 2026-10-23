# Python source module `draftmake.make_label`

[Python catalogue](../../index.md)

Evidence: `src/Mod/Draft/draftmake/make_label.py`. Import path is source-routed; installed availability is unverified.

Provides functions to create Label objects.

Literal `__all__`: not available; source names do not imply supported public API.

## Imports, aliases and conditional reexports

### import FreeCAD as App

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_label.App` -> `FreeCAD`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_label.py:35`.

### from draftobjects import label

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_label.label` -> `draftobjects.label`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_label.py:36`.

### from draftutils import gui_utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_label.gui_utils` -> `draftutils.gui_utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_label.py:37`.

### from draftutils import params

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_label.params` -> `draftutils.params`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_label.py:38`.

### from draftutils import utils

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_label.utils` -> `draftutils.utils`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_label.py:39`.

### from draftutils.messages import _err, _wrn

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_label._err` -> `draftutils.messages._err`.

Bound source name `draftmake.make_label._wrn` -> `draftutils.messages._wrn`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_label.py:40`.

### from draftutils.translate import translate

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_label.translate` -> `draftutils.translate.translate`.

Target not expanded in this selected Python catalogue; check the binding catalogue or source.

Evidence: `src/Mod/Draft/draftmake/make_label.py:41`.

### from freecad.deprecation import deprecated

Module-scope import; may be a dependency rather than supported addon API.

Bound source name `draftmake.make_label.deprecated` -> `freecad.deprecation.deprecated`.

[Source module `freecad.deprecation`](../../freecad/deprecation/index.md).

Evidence: `src/Mod/Draft/draftmake/make_label.py:42`.

### from draftviewproviders.view_label import ViewProviderLabel

Module-scope import; may be a dependency rather than supported addon API.

Conditions: `if App.GuiUp`.

Bound source name `draftmake.make_label.ViewProviderLabel` -> `draftviewproviders.view_label.ViewProviderLabel`.

[Source module `draftviewproviders.view_label`](../../draftviewproviders/view_label/index.md).

Evidence: `src/Mod/Draft/draftmake/make_label.py:45`.

## `draftmake.make_label.make_label`

Status: source-defined name; no independently verified stability/export guarantee.

```python
def make_label(target_point=App.Vector(0, 0, 0), placement=App.Vector(30, 30, 0), target_object=None, subelements=None, label_type='Custom', custom_text='Label', direction='Horizontal', distance=-10, points=None):
```

Create a Label object containing different types of information.

The current color and text height and font specified in preferences
are used.

Parameters
----------
target_point: Base::Vector3, optional
    It defaults to the origin `App.Vector(0, 0, 0)`.
    This is the point which is pointed to by the label's leader line.
    This point can be adorned with a marker like an arrow or circle.

placement: Base::Placement, Base::Vector3, or Base::Rotation, optional
    It defaults to `App.Vector(30, 30, 0)`.
    If it is provided, it defines the base point of the textual
    label.
    The input could be a full placement, just a vector indicating
    the translation, or just a rotation.

target_object: Part::Feature or str, optional
    It defaults to `None`.
    If it exists it should be an object which will be used to provide
    information to the label, as long as `label_type` is different
    from `'Custom'`.

    If it is a string, it must be the `Label` of that object.
    Since a `Label` is not guaranteed to be unique in a document,
    it will use the first object found with this `Label`.

subelements: str, optional
    It defaults to `None`.
    If `subelements` is provided, `target_object` should be provided
    as well, otherwise it is ignored.

    It should be a string indicating a subelement name, either
    `'VertexN'`, `'EdgeN'`, or `'FaceN'` which should exist
    within `target_object`.
    In this case `'N'` is an integer that indicates the specific number
    of vertex, edge, or face in `target_object`.

    Both `target_object` and `subelements` are used to link the label
    to a particular object, or to the particular vertex, edge, or face,
    and get information from them.
    ::
        make_label(..., target_object=App.ActiveDocument.Box)
        make_label(..., target_object="My box", subelements="Face3")

    These two parameters can be can be obtained from the `Gui::Selection`
    module.
    ::
        sel_object = Gui.Selection.getSelectionEx()[0]
        target_object = sel_object.Object
        subelements = sel_object.SubElementNames[0]

label_type: str, optional
    It defaults to `'Custom'`.
    It indicates the type of information that will be shown in the label.
    See the get_label_types function in label.py for supported types.

    Only `'Custom'` allows you to manually set the text
    by defining `custom_text`. The other types take their information
    from the object included in `target`.

    - `'Position'` will show the base position of the target object,
      or of the indicated `'VertexN'` in `target`.
    - `'Length'` will show the `Length` of the target object's `Shape`,
      or of the indicated `'EdgeN'` in `target`.
    - `'Area'` will show the `Area` of the target object's `Shape`,
      or of the indicated `'FaceN'` in `target`.

custom_text: str, or list of str, optional
    It defaults to `'Label'`.
    If it is a list, each element in the list represents a new text line.

    It is the text that will be displayed by the label when
    `label_type` is `'Custom'`.

direction: str, optional
    It defaults to `'Horizontal'`.
    It can be `'Horizontal'`, `'Vertical'`, or `'Custom'`.
    It indicates the direction of the straight segment of the leader line
    that ends up next to the textual label.

    If `'Custom'` is selected, the leader line can be manually drawn
    by specifying the value of `points`.
    Normally, the leader line has only three points, but with `'Custom'`
    you can specify as many points as needed.

distance: int, float, Base::Quantity, optional
    It defaults to -10.
    It indicates the length of the horizontal or vertical segment
    of the leader line.

    The leader line is composed of two segments, the first segment is
    inclined, while the second segment is either horizontal or vertical
    depending on the value of `direction`.
    ::
        T
        |
        |
        o------- L text

    The `oL` segment's length is defined by `distance`
    while the `oT` segment is automatically calculated depending
    on the values of `placement` (L) and `distance` (o).

    This `distance` is oriented, meaning that if it is positive
    the segment will be to the right and above of the textual
    label, depending on if `direction` is `'Horizontal'` or `'Vertical'`,
    respectively.
    If it is negative, the segment will be to the left
    and below of the text.

points: list of Base::Vector3, optional
    It defaults to `None`.
    It is a list of vectors defining the shape of the leader line;
    the list must have at least two points.
    This argument must be used together with `direction='Custom'`
    to display this custom leader.

    However, notice that if the Label's `StraightDirection` property
    is later changed to `'Horizontal'` or `'Vertical'`,
    the custom point list will be overwritten with a new,
    automatically calculated three-point list.

    For the object to use custom points, `StraightDirection`
    must remain `'Custom'`, and then the `Points` property
    can be overwritten by a suitable list of points.

Returns
-------
App::FeaturePython
    A scripted object of type `'Label'`.
    This object does not have a `Shape` attribute, as the text and lines
    are created on screen by Coin (pivy).

None
    If there is a problem it will return `None`.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_label.py:48`. Decorators are copied as source expressions and have not been executed.

## `draftmake.make_label.makeLabel`

Status: source-defined name; no independently verified stability/export guarantee.

```python
@deprecated(deprecated_in='26.3', removed_in='28.3', replacement='Draft.make_label()')
def makeLabel(targetpoint=None, target=None, direction=None, distance=None, labeltype=None, placement=None):
```

DEPRECATED. Use 'make_label'.

Typing limit: missing source annotations are unspecified; no inferred parameter/return types are supplied.

Evidence: `src/Mod/Draft/draftmake/make_label.py:379`. Decorators are copied as source expressions and have not been executed.

