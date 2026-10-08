# `FreeCADGui.Command`

[Module](index.md)

```python
class Command:
```

FreeCAD Python wrapper of Command functions

Author: Werner Mayer (wmayer[at]users.sourceforge.net)
Licence: LGPL

Evidence: public stub `FreeCADGui/__init__.pyi` line 1627. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCADGui.Command.get`

```python
@staticmethod
def get(name: str, /) -> Optional['Command']:
```

Get a given command by name or None if it doesn't exist.

name : str
    Command name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1636.

## `FreeCADGui.Command.update`

```python
@staticmethod
def update() -> None:
```

Update active status of all commands.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1646.

## `FreeCADGui.Command.listAll`

```python
@staticmethod
def listAll() -> List[str]:
```

Returns the name of all commands.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1653.

## `FreeCADGui.Command.listByShortcut`

```python
@staticmethod
def listByShortcut(string: str, useRegExp: bool=False, /) -> List[str]:
```

Returns a list of all commands, filtered by shortcut.
Shortcuts are converted to uppercase and spaces removed
prior to comparison.

string :  str
    Shortcut to be searched.
useRegExp : bool
    Filter using regular expression.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1660.

## `FreeCADGui.Command.run`

```python
def run(self, item: int=0, /) -> None:
```

Runs the given command.

item : int
    Item to be run.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1673.

## `FreeCADGui.Command.isActive`

```python
def isActive(self) -> bool:
```

Returns True if the command is active, False otherwise.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1682.

## `FreeCADGui.Command.getShortcut`

```python
def getShortcut(self) -> str:
```

Returns string representing shortcut key accelerator for command.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1688.

## `FreeCADGui.Command.setShortcut`

```python
def setShortcut(self, string: str, /) -> bool:
```

Sets shortcut for given command, returns True for success.

string : str
    Shortcut to be set.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1694.

## `FreeCADGui.Command.resetShortcut`

```python
def resetShortcut(self) -> bool:
```

Resets shortcut for given command back to the default, returns True for success.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1703.

## `FreeCADGui.Command.getInfo`

```python
def getInfo(self) -> Dict[Any, Any]:
```

Return information about this command.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1709.

## `FreeCADGui.Command.getAction`

```python
def getAction(self) -> List[Any]:
```

Return the associated QAction object.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1715.

## `FreeCADGui.Command.createCustomCommand`

```python
@staticmethod
def createCustomCommand(macroFile: str, menuText: Optional[str]=None, toolTip: Optional[str]=None, whatsThis: Optional[str]=None, statusTip: Optional[str]=None, pixmap: Optional[str]=None, shortcut: Optional[str]=None) -> str:
```

Create a custom command for a macro. Returns name of the created command.

macroFile : str
    Macro file.
menuText : str
    Menu text. Optional.
toolTip : str
    Tool tip text. Optional.
whatsThis : str
    `What's this?` text. Optional.
statusTip : str
    Status tip text. Optional.
pixmap : str
    Pixmap name. Optional.
shortcut : str
    Shortcut key sequence. Optional.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1722.

## `FreeCADGui.Command.removeCustomCommand`

```python
@staticmethod
def removeCustomCommand(name: str, /) -> bool:
```

Remove the custom command if it exists.
Given the name of a custom command, this removes that command.
It is not an error to remove a non-existent command, the function
simply does nothing in that case.
Returns True if something was removed, or False if not.

name : str
    Command name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1744.

## `FreeCADGui.Command.findCustomCommand`

```python
@staticmethod
def findCustomCommand(name: str, /) -> Optional[str]:
```

Given the name of a macro, return the name of the custom command for that macro
or None if there is no command matching that macro script name.

name : str
    Macro name.

Evidence: public stub `FreeCADGui/__init__.pyi` line(s) 1758.

