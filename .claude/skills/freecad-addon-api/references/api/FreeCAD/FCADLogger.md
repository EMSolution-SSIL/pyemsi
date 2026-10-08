# `FreeCAD.FCADLogger`

[Module](index.md)

```python
class FCADLogger:
```

Convenient class for tagged logging.

Example usage:
    >>> logger = FreeCAD.Logger('MyModule')
    >>> logger.info('log test {}',1)
    24.36053 <MyModule> <input>(1): test log 1

The default output format is:
    <timestamp> <tag> <source file>(line number): message

The message is formatted using new style Python string formatting, e.g.
'test {}'.format(1). It is strongly recommended to not directly use
Python string formatting, but pass additional argument indirectly through
various logger print function, because the logger can skip string
evaluation in case the logging level is disabled. For more options,
please consult the docstring of __init__(), catch() and report().

To set/get logger level:
    >>> FreeCAD.setLogLevel('MyModule','Trace')
    >>> FreeCAD.getLogLevel('MyModule')
    4

There are five predefined logger level, each corresponding to an integer
value, as shown below together with the corresponding logger print
method,
    0: Error, Logger.error()
    1: Warning, Logger.warn()
    2: Message, Logger.msg() or info()
    3: Log, Logger.log() or debug()
    4: Trace, Logger.trace()

FreeCAD.setLogLevel() supports both text and integer value, which allows
you to define your own levels. The level set is persisted to user
configuration file.

By default any tag has a log level of 2 for release, and 3 for debug
build.

Evidence: public stub `FreeCAD/__init__.pyi` line 69. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.FCADLogger.printTag`

```python
printTag: bool
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 109.

## `FreeCAD.FCADLogger.noUpdateUI`

```python
noUpdateUI: bool
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 110.

## `FreeCAD.FCADLogger.timing`

```python
timing: bool
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 111.

## `FreeCAD.FCADLogger.lineno`

```python
lineno: bool
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 112.

## `FreeCAD.FCADLogger.parent`

```python
parent: 'FCADLogger | None'
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 113.

## `FreeCAD.FCADLogger.title`

```python
title: str
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 114.

## `FreeCAD.FCADLogger.tag`

```python
tag: str
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 115.

## `FreeCAD.FCADLogger.laststamp`

```python
laststamp: datetime
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 116.

## `FreeCAD.FCADLogger.__init__`

```python
def __init__(self, tag: str, **kwargs: object) -> None:
```

Construct a logger instance.

Supported arguments are their default values are,

* tag: a string tag for this logger. The log level of this logger can be
       accessed using FreeCAD.getLogLevel(tag)/setLogLevel(tag,level).
       All logger instance with the same tag shares the same level
       setting.

* printTag (True): whether to print tag

* noUpdateUI (True): whether to update GUI when printing. This is useful
                     to show log output on lengthy operations. Be
                     careful though, this may allow unexpected user
                     interaction when the application is busy, which may
                     lead to crash

* timing (True): whether to print time stamp

* lineno (True): whether to print source file and line number

* parent (None): provide a parent logger, so that the log printing will
                 check for parent's log level in addition of its own

* title ('FreeCAD'): message box title used by report()

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 118.

## `FreeCAD.FCADLogger.isEnabledFor`

```python
def isEnabledFor(self, level: int | str) -> bool:
```

To check for an integer or text log level.

* level: integer or text log level

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 148.

## `FreeCAD.FCADLogger.report`

```python
def report(self, msg: str, func: Callable[..., object], *args: object, **kwargs: object) -> object | None:
```

Catch any exception report it with a message box.

* msg: message string. Unlike log printer, this argument must not
        contain any string formatter.

* func: a callable object

* args: tuple of positional arguments to be passed to func.

* kwargs: dictionary of keyword arguments to be passed to func.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 156.

## `FreeCAD.FCADLogger.error`

```python
def error(self, msg: str, *args: object, **kwargs: object) -> None:
```

Log an error-level message.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 171.

## `FreeCAD.FCADLogger.warn`

```python
def warn(self, msg: str, *args: object, **kwargs: object) -> None:
```

Log a warning-level message.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 175.

## `FreeCAD.FCADLogger.msg`

```python
def msg(self, msg: str, *args: object, **kwargs: object) -> None:
```

Log a message-level message.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 179.

## `FreeCAD.FCADLogger.log`

```python
def log(self, msg: str, *args: object, **kwargs: object) -> None:
```

Log a log-level message.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 183.

## `FreeCAD.FCADLogger.trace`

```python
def trace(self, msg: str, *args: object, **kwargs: object) -> None:
```

Log a trace-level message.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 187.

## `FreeCAD.FCADLogger.info`

```python
def info(self, msg: str, *args: object, **kwargs: object) -> None:
```

Log an informational message.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 191.

## `FreeCAD.FCADLogger.debug`

```python
def debug(self, msg: str, *args: object, **kwargs: object) -> None:
```

Log a debug-level message.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 195.

## `FreeCAD.FCADLogger.catch`

```python
def catch(self, msg: str, func: Callable[..., object], *args: object, **kwargs: object) -> object | None:
```

Call *func* and catch exceptions at the error level.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 199.

## `FreeCAD.FCADLogger.catchWarn`

```python
def catchWarn(self, msg: str, func: Callable[..., object], *args: object, **kwargs: object) -> object | None:
```

Call *func* and catch exceptions at the warning level.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 203.

## `FreeCAD.FCADLogger.catchMsg`

```python
def catchMsg(self, msg: str, func: Callable[..., object], *args: object, **kwargs: object) -> object | None:
```

Call *func* and catch exceptions at the message level.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 207.

## `FreeCAD.FCADLogger.catchLog`

```python
def catchLog(self, msg: str, func: Callable[..., object], *args: object, **kwargs: object) -> object | None:
```

Call *func* and catch exceptions at the log level.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 211.

## `FreeCAD.FCADLogger.catchTrace`

```python
def catchTrace(self, msg: str, func: Callable[..., object], *args: object, **kwargs: object) -> object | None:
```

Call *func* and catch exceptions at the trace level.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 215.

## `FreeCAD.FCADLogger.catchInfo`

```python
def catchInfo(self, msg: str, func: Callable[..., object], *args: object, **kwargs: object) -> object | None:
```

Call *func* and catch exceptions at the message level.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 219.

## `FreeCAD.FCADLogger.catchDebug`

```python
def catchDebug(self, msg: str, func: Callable[..., object], *args: object, **kwargs: object) -> object | None:
```

Call *func* and catch exceptions at the log level.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 223.

