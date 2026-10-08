# `FreeCAD.Console`

[Catalogue index](../../index.md)

Evidence: import-shaped public stub `FreeCAD/Console.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any, overload
from typing import Literal, TypeAlias
from Base.Metadata import module
```

## `FreeCAD.Console._MessageType`

```python
_MessageType: TypeAlias = Literal['Log', 'Wrn', 'Msg', 'Err', 'Critical', 'Notification']
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 8.

## `FreeCAD.Console.GetObservers`

```python
def GetObservers() -> list[str]:
```

Return the observer names registered with the console singleton.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 10.

## `FreeCAD.Console.GetStatus`

```python
def GetStatus(observer: str, type: _MessageType, /) -> bool | None:
```

Return one message-category state, or None if the observer is unknown.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 14.

## `FreeCAD.Console.PrintCritical`

```python
@overload
def PrintCritical(message: object, /) -> None:

@overload
def PrintCritical(notifier: object, message: object, /) -> None:
```

Print a critical message using the default empty notifier.

Print a critical message with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 19, 24.

## `FreeCAD.Console.PrintDeveloperError`

```python
@overload
def PrintDeveloperError(message: object, /) -> None:

@overload
def PrintDeveloperError(notifier: object, message: object, /) -> None:
```

Print a developer-only error using the default empty notifier.

Print a developer-only error with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 29, 34.

## `FreeCAD.Console.PrintDeveloperWarning`

```python
@overload
def PrintDeveloperWarning(message: object, /) -> None:

@overload
def PrintDeveloperWarning(notifier: object, message: object, /) -> None:
```

Print a developer-only warning using the default empty notifier.

Print a developer-only warning with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 39, 44.

## `FreeCAD.Console.PrintError`

```python
@overload
def PrintError(message: object, /) -> None:

@overload
def PrintError(notifier: object, message: object, /) -> None:
```

Print an error using the default empty notifier.

Print an error with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 49, 54.

## `FreeCAD.Console.PrintLog`

```python
@overload
def PrintLog(message: object, /) -> None:

@overload
def PrintLog(notifier: object, message: object, /) -> None:
```

Print a log message using the default empty notifier.

Print a log message with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 59, 64.

## `FreeCAD.Console.PrintMessage`

```python
@overload
def PrintMessage(message: object, /) -> None:

@overload
def PrintMessage(notifier: object, message: object, /) -> None:
```

Print a plain message using the default empty notifier.

Print a plain message with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 69, 74.

## `FreeCAD.Console.PrintNotification`

```python
@overload
def PrintNotification(message: object, /) -> None:

@overload
def PrintNotification(notifier: object, message: object, /) -> None:
```

Print a notification using the default empty notifier.

Print a notification with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 79, 84.

## `FreeCAD.Console.PrintTranslatedNotification`

```python
@overload
def PrintTranslatedNotification(message: object, /) -> None:

@overload
def PrintTranslatedNotification(notifier: object, message: object, /) -> None:
```

Print a translated notification using the default empty notifier.

Print a translated notification with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 89, 94.

## `FreeCAD.Console.PrintTranslatedUserError`

```python
@overload
def PrintTranslatedUserError(message: object, /) -> None:

@overload
def PrintTranslatedUserError(notifier: object, message: object, /) -> None:
```

Print a translated user-facing error using the default empty notifier.

Print a translated user-facing error with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 99, 104.

## `FreeCAD.Console.PrintTranslatedUserWarning`

```python
@overload
def PrintTranslatedUserWarning(message: object, /) -> None:

@overload
def PrintTranslatedUserWarning(notifier: object, message: object, /) -> None:
```

Print a translated user-facing warning using the default empty notifier.

Print a translated user-facing warning with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 109, 114.

## `FreeCAD.Console.PrintUserError`

```python
@overload
def PrintUserError(message: object, /) -> None:

@overload
def PrintUserError(notifier: object, message: object, /) -> None:
```

Print a user-facing error using the default empty notifier.

Print a user-facing error with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 119, 124.

## `FreeCAD.Console.PrintUserWarning`

```python
@overload
def PrintUserWarning(message: object, /) -> None:

@overload
def PrintUserWarning(notifier: object, message: object, /) -> None:
```

Print a user-facing warning using the default empty notifier.

Print a user-facing warning with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 129, 134.

## `FreeCAD.Console.PrintWarning`

```python
@overload
def PrintWarning(message: object, /) -> None:

@overload
def PrintWarning(notifier: object, message: object, /) -> None:
```

Print a warning using the default empty notifier.

Print a warning with an explicit notifier prefix.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 139, 144.

## `FreeCAD.Console.SetStatus`

```python
def SetStatus(observer: str, type: _MessageType, status: bool, /) -> None:
```

Enable or disable one message category for a registered console observer.

Evidence: public stub `FreeCAD/Console.pyi` line(s) 148.

