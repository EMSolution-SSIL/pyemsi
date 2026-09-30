# `FreeCAD.Base.Precision`

[Module](index.md)

```python
class Precision:
```

This is the Precision class

Author: Werner Mayer (wmayer@users.sourceforge.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 1150. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.Precision.angular`

```python
@staticmethod
def angular() -> float:
```

Returns the recommended precision value when checking the equality of two angles (given in radians)

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1159.

## `FreeCAD.Base.Precision.confusion`

```python
@staticmethod
def confusion() -> float:
```

Returns the recommended precision value when checking coincidence of two points in real space

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1166.

## `FreeCAD.Base.Precision.squareConfusion`

```python
@staticmethod
def squareConfusion() -> float:
```

Returns square of confusion

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1173.

## `FreeCAD.Base.Precision.intersection`

```python
@staticmethod
def intersection() -> float:
```

Returns the precision value in real space, frequently used by intersection algorithms

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1180.

## `FreeCAD.Base.Precision.approximation`

```python
@staticmethod
def approximation() -> float:
```

Returns the precision value in real space, frequently used by approximation algorithms

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1187.

## `FreeCAD.Base.Precision.parametric`

```python
@staticmethod
def parametric(p: float, t: float=..., /) -> float:
```

Convert a real space precision to a parametric space precision

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1194.

## `FreeCAD.Base.Precision.isInfinite`

```python
@staticmethod
def isInfinite(value: float, /) -> bool:
```

Returns True if R may be considered as an infinite number

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1201.

## `FreeCAD.Base.Precision.isPositiveInfinite`

```python
@staticmethod
def isPositiveInfinite(value: float, /) -> bool:
```

Returns True if R may  be considered as a positive infinite number

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1208.

## `FreeCAD.Base.Precision.isNegativeInfinite`

```python
@staticmethod
def isNegativeInfinite(value: float, /) -> bool:
```

Returns True if R may  be considered as a negative infinite number

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1215.

## `FreeCAD.Base.Precision.infinite`

```python
@staticmethod
def infinite() -> float:
```

Returns a  big number that  can  be  considered as infinite

Evidence: public stub `FreeCAD/Base.pyi` line(s) 1222.

