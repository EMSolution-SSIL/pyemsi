# `PathApp.Command`

[Module](index.md)

```python
class Command(Persistence):
```

Command([name],[parameters],[annotations]): Represents a basic Gcode command
name (optional) is the name of the command, ex. G1
parameters (optional) is a dictionary containing string:number
pairs, or a placement, or a vector
annotations (optional) is a dictionary containing string:string or string:number pairs

Evidence: public stub `PathApp/__init__.pyi` line 163. Inherited members are on the named base's reference; aliases keep their imported identity.

## `PathApp.Command.toGCode`

```python
def toGCode(self) -> str:
```

returns a GCode representation of the command

Evidence: public stub `PathApp/__init__.pyi` line(s) 172.

## `PathApp.Command.setFromGCode`

```python
def setFromGCode(self, gcode: str, /) -> None:
```

sets the path from the contents of the given GCode string

Evidence: public stub `PathApp/__init__.pyi` line(s) 176.

## `PathApp.Command.transform`

```python
def transform(self, placement: 'PathApp.Placement', /) -> Command:
```

returns a copy of this command transformed by the given placement

Evidence: public stub `PathApp/__init__.pyi` line(s) 180.

## `PathApp.Command.addAnnotations`

```python
def addAnnotations(self, annotations, /) -> 'Command':
```

addAnnotations(annotations): adds annotations from dictionary or string and returns self for chaining

Evidence: public stub `PathApp/__init__.pyi` line(s) 184.

## `PathApp.Command.Name`

```python
Name: str
```

The name of the command

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 187.

## `PathApp.Command.Parameters`

```python
Parameters: dict[str, float]
```

The parameters of the command.

    Assigning a dictionary replaces the whole parameter set: keys that are not
    in the assigned dictionary are removed. To change a single parameter, copy
    the dictionary, modify it, and assign it back.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 189.

## `PathApp.Command.Annotations`

```python
Annotations: dict[str, str]
```

The annotations of the command

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 191.

## `PathApp.Command.Placement`

```python
Placement: 'PathApp.Placement'
```

The coordinates of the endpoint of the command

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `PathApp/__init__.pyi` line(s) 193.

