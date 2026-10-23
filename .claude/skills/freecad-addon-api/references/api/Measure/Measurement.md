# `Measure.Measurement`

[Module](index.md)

```python
class Measurement(BaseClass):
```

Make a measurement

Author: Luke Parry (l.parry@warwick.ac.uk)
License: LGPL-2.1-or-later

Evidence: public stub `Measure/__init__.pyi` line 41. Inherited members are on the named base's reference; aliases keep their imported identity.

## `Measure.Measurement.addReference3D`

```python
def addReference3D(self, object_name: str, sub_name: str, /) -> None:
```

add a geometric reference to a subelement of a named object in the active document

Evidence: public stub `Measure/__init__.pyi` line(s) 49.

## `Measure.Measurement.has3DReferences`

```python
def has3DReferences(self) -> Any:
```

does Measurement have links to 3D geometry

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 53.

## `Measure.Measurement.clear`

```python
def clear(self) -> Any:
```

clear all references and reset the measurement

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 57.

## `Measure.Measurement.delta`

```python
def delta(self) -> Any:
```

measure the difference between references to obtain resultant vector

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 61.

## `Measure.Measurement.length`

```python
def length(self) -> Any:
```

measure the length of the references

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 65.

## `Measure.Measurement.volume`

```python
def volume(self) -> Any:
```

measure the volume of the references

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 69.

## `Measure.Measurement.area`

```python
def area(self) -> Any:
```

measure the area of the references

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 73.

## `Measure.Measurement.lineLineDistance`

```python
def lineLineDistance(self) -> Any:
```

measure the line-Line Distance of the references. Returns 0 if references are not 2 lines.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 77.

## `Measure.Measurement.planePlaneDistance`

```python
def planePlaneDistance(self) -> Any:
```

measure the plane-plane distance of the references. Returns 0 if references are not 2 planes.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 81.

## `Measure.Measurement.angle`

```python
def angle(self) -> Any:
```

measure the angle between two edges

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 85.

## `Measure.Measurement.radius`

```python
def radius(self) -> Any:
```

measure the radius of an arc or circle edge

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 89.

## `Measure.Measurement.com`

```python
def com(self) -> Any:
```

measure the center of mass for selected volumes

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `Measure/__init__.pyi` line(s) 93.

