# `Web`

[Catalogue index](../index.md)

Evidence: import-shaped public stub `Web/__init__.pyi`; generated binding/typing declarations, runtime unverified.

## Imports and aliases

These preserve stub type context and reexports. Imported typing helpers and underscored names are not a promise of supported runtime API.

```python
from __future__ import annotations
from typing import Any
from collections.abc import Callable
from typing import TypeAlias
```

## `Web._ServerAddress`

```python
_ServerAddress: TypeAlias = tuple[str, int]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Web/__init__.pyi` line(s) 8.

## `Web._ServerFirewall`

```python
_ServerFirewall: TypeAlias = Callable[[str], bool]
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `Web/__init__.pyi` line(s) 9.

## `Web.startServer`

```python
def startServer(address: str='127.0.0.1', port: int=0, /) -> _ServerAddress:
```

Start one listening server and return its bound address and port.

Evidence: public stub `Web/__init__.pyi` line(s) 11.

## `Web.waitForConnection`

```python
def waitForConnection(address: str='127.0.0.1', port: int=0, timeout: int=0, /) -> bool:
```

Listen for one connection and report whether a client connected before timeout.

Evidence: public stub `Web/__init__.pyi` line(s) 15.

## `Web.registerServerFirewall`

```python
def registerServerFirewall(firewall: _ServerFirewall | None, /) -> None:
```

Register or clear the callback that filters incoming server requests.

Evidence: public stub `Web/__init__.pyi` line(s) 19.

