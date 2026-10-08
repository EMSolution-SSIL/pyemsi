# `FreeCAD.ParameterGrp`

[Module](index.md)

```python
class ParameterGrp:
```

Class purpose undocumented in this stub.

Evidence: public stub `FreeCAD/__init__.pyi` line 519. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.ParameterGrp.GetGroup`

```python
def GetGroup(self, name: str, /) -> ParameterGrp:
```

Return one child parameter group by name.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 521.

## `FreeCAD.ParameterGrp.GetGroupName`

```python
def GetGroupName(self) -> str:
```

Return this group's local name.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 525.

## `FreeCAD.ParameterGrp.GetGroups`

```python
def GetGroups(self) -> list[str]:
```

Return the child group names.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 529.

## `FreeCAD.ParameterGrp.RemGroup`

```python
def RemGroup(self, name: str, /) -> None:
```

Remove one child parameter group.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 533.

## `FreeCAD.ParameterGrp.HasGroup`

```python
def HasGroup(self, name: str, /) -> bool:
```

Return whether one child group exists.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 537.

## `FreeCAD.ParameterGrp.RenameGroup`

```python
def RenameGroup(self, old_name: str, new_name: str, /) -> bool:
```

Rename one child parameter group.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 541.

## `FreeCAD.ParameterGrp.CopyTo`

```python
def CopyTo(self, group: ParameterGrp, /) -> None:
```

Copy this group's contents into another parameter group.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 545.

## `FreeCAD.ParameterGrp.Manager`

```python
def Manager(self) -> ParameterGrp | None:
```

Return the manager group for this parameter group, if any.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 549.

## `FreeCAD.ParameterGrp.Parent`

```python
def Parent(self) -> ParameterGrp | None:
```

Return the parent group, if any.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 553.

## `FreeCAD.ParameterGrp.IsEmpty`

```python
def IsEmpty(self) -> bool:
```

Return whether the group has no stored values or child groups.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 557.

## `FreeCAD.ParameterGrp.Clear`

```python
def Clear(self) -> None:
```

Remove all stored values and child groups.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 561.

## `FreeCAD.ParameterGrp.Attach`

```python
def Attach(self, observer: _ParameterObserver, /) -> None:
```

Register one direct parameter observer.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 565.

## `FreeCAD.ParameterGrp.AttachManager`

```python
def AttachManager(self, observer: _ParameterManagerObserver, /) -> None:
```

Register one manager-level parameter observer.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 569.

## `FreeCAD.ParameterGrp.Detach`

```python
def Detach(self, observer: _ParameterObserver | _ParameterManagerObserver, /) -> None:
```

Unregister one direct or manager-level observer.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 573.

## `FreeCAD.ParameterGrp.Notify`

```python
def Notify(self, name: str, /) -> None:
```

Notify observers that one named entry changed.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 577.

## `FreeCAD.ParameterGrp.NotifyAll`

```python
def NotifyAll(self) -> None:
```

Notify observers that the whole group changed.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 581.

## `FreeCAD.ParameterGrp.SetBool`

```python
def SetBool(self, name: str, value: bool | int, /) -> None:
```

Store one boolean parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 585.

## `FreeCAD.ParameterGrp.GetBool`

```python
def GetBool(self, name: str, default: bool | int=False, /) -> bool:
```

Return one boolean parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 589.

## `FreeCAD.ParameterGrp.GetBools`

```python
def GetBools(self, filter: str='', /) -> list[str]:
```

Return the names of boolean parameters, optionally filtered.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 593.

## `FreeCAD.ParameterGrp.RemBool`

```python
def RemBool(self, name: str, /) -> None:
```

Remove one boolean parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 597.

## `FreeCAD.ParameterGrp.SetInt`

```python
def SetInt(self, name: str, value: int, /) -> None:
```

Store one integer parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 601.

## `FreeCAD.ParameterGrp.GetInt`

```python
def GetInt(self, name: str, default: int=0, /) -> int:
```

Return one integer parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 605.

## `FreeCAD.ParameterGrp.GetInts`

```python
def GetInts(self, filter: str='', /) -> list[str]:
```

Return the names of integer parameters, optionally filtered.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 609.

## `FreeCAD.ParameterGrp.RemInt`

```python
def RemInt(self, name: str, /) -> None:
```

Remove one integer parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 613.

## `FreeCAD.ParameterGrp.SetUnsigned`

```python
def SetUnsigned(self, name: str, value: int, /) -> None:
```

Store one unsigned integer parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 617.

## `FreeCAD.ParameterGrp.GetUnsigned`

```python
def GetUnsigned(self, name: str, default: int=0, /) -> int:
```

Return one unsigned integer parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 621.

## `FreeCAD.ParameterGrp.GetUnsigneds`

```python
def GetUnsigneds(self, filter: str='', /) -> list[str]:
```

Return the names of unsigned integer parameters, optionally filtered.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 625.

## `FreeCAD.ParameterGrp.RemUnsigned`

```python
def RemUnsigned(self, name: str, /) -> None:
```

Remove one unsigned integer parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 629.

## `FreeCAD.ParameterGrp.SetFloat`

```python
def SetFloat(self, name: str, value: float, /) -> None:
```

Store one floating-point parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 633.

## `FreeCAD.ParameterGrp.GetFloat`

```python
def GetFloat(self, name: str, default: float=0.0, /) -> float:
```

Return one floating-point parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 637.

## `FreeCAD.ParameterGrp.GetFloats`

```python
def GetFloats(self, filter: str='', /) -> list[str]:
```

Return the names of floating-point parameters, optionally filtered.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 641.

## `FreeCAD.ParameterGrp.RemFloat`

```python
def RemFloat(self, name: str, /) -> None:
```

Remove one floating-point parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 645.

## `FreeCAD.ParameterGrp.SetString`

```python
def SetString(self, name: str, value: str, /) -> None:
```

Store one string parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 649.

## `FreeCAD.ParameterGrp.GetString`

```python
def GetString(self, name: str, default: str='', /) -> str:
```

Return one string parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 653.

## `FreeCAD.ParameterGrp.GetStrings`

```python
def GetStrings(self, filter: str='', /) -> list[str]:
```

Return the names of string parameters, optionally filtered.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 657.

## `FreeCAD.ParameterGrp.RemString`

```python
def RemString(self, name: str, /) -> None:
```

Remove one string parameter value.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 661.

## `FreeCAD.ParameterGrp.Import`

```python
def Import(self, path: str, /) -> None:
```

Import parameter values from one external file.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 665.

## `FreeCAD.ParameterGrp.Insert`

```python
def Insert(self, path: str, /) -> None:
```

Insert parameter values from one external file.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 669.

## `FreeCAD.ParameterGrp.Export`

```python
def Export(self, path: str, /) -> None:
```

Export parameter values to one external file.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 673.

## `FreeCAD.ParameterGrp.GetContents`

```python
def GetContents(self) -> list[_ParameterContent] | None:
```

Return the stored parameter entries as tagged name-value tuples.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 677.

