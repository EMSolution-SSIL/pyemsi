# `FreeCAD.Metadata`

[Module](index.md)

```python
class Metadata:
```

App.Metadata class.

A Metadata object reads an XML-formatted package metadata file and provides
read and write access to its contents.

The following constructors are supported:

Metadata()
Empty constructor.

Metadata(metadata)
Copy constructor.
metadata : App.Metadata

Metadata(file)
Reads the XML file and provides access to the metadata it specifies.
file : str
    XML file name.

Metadata(bytes)
Treats the bytes as UTF-8-encoded XML data and provides access to the metadata it specifies.
bytes : bytes
    Python bytes-like object.

Author: Chris Hennes (chennes@pioneerlibrarysystem.org)
Licence: LGPL
DeveloperDocu: Metadata

Evidence: public stub `FreeCAD/__init__.pyi` line 2509. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Metadata.__init__`

```python
@overload
def __init__(self) -> None:

@overload
def __init__(self, metadata: 'Metadata') -> None:

@overload
def __init__(self, file: str) -> None:

@overload
def __init__(self, bytes: bytes) -> None:
```

Purpose/behavior undocumented in this stub; consult the implementation before relying on it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2541, 2545, 2549, 2553.

## `FreeCAD.Metadata.Name`

```python
Name: str = ''
```

String representing the name of this item.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2555.

## `FreeCAD.Metadata.Version`

```python
Version: str = ''
```

String representing the version of this item in semantic triplet format.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2557.

## `FreeCAD.Metadata.Date`

```python
Date: str = ''
```

String representing the date of this item in YYYY-MM-DD format (format not currently programmatically enforced)

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2559.

## `FreeCAD.Metadata.Type`

```python
Type: str = ''
```

String representing the type of this item (text only, no markup allowed).

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2561.

## `FreeCAD.Metadata.Description`

```python
Description: str = ''
```

String representing the description of this item (text only, no markup allowed).

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2563.

## `FreeCAD.Metadata.Maintainer`

```python
Maintainer: List[Any] = []
```

List of maintainer objects with 'name' and 'email' string attributes.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2565.

## `FreeCAD.Metadata.License`

```python
License: List[Any] = []
```

List of applicable licenses as objects with 'name' and 'file' string attributes.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2567.

## `FreeCAD.Metadata.Urls`

```python
Urls: List[Any] = []
```


    List of URLs as objects with 'location' and 'type' string attributes, where type
    is one of:
    * website
    * repository
    * bugtracker
    * readme
    * documentation
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2569.

## `FreeCAD.Metadata.Author`

```python
Author: List[Any] = []
```


    List of author objects, each with a 'name' and a (potentially empty) 'email'
    string attribute.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2571.

## `FreeCAD.Metadata.Depend`

```python
Depend: List[Any] = []
```


    List of dependencies, as objects with the following attributes:
    * package
        Required. Must exactly match the contents of the 'name' element in the
        referenced package's package.xml file.
    * version_lt
        Optional. The dependency to the package is restricted to versions less than
        the stated version number.
    * version_lte
        Optional. The dependency to the package is restricted to versions less or
        equal than the stated version number.
    * version_eq
        Optional. The dependency to the package is restricted to a version equal
        than the stated version number.
    * version_gte
        Optional. The dependency to the package is restricted to versions greater
        or equal than the stated version number.
    * version_gt
        Optional. The dependency to the package is restricted to versions greater
        than the stated version number.
    * condition
        Optional. Conditional expression as documented in REP149.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2573.

## `FreeCAD.Metadata.Conflict`

```python
Conflict: List[Any] = []
```

List of conflicts, format identical to dependencies.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2575.

## `FreeCAD.Metadata.Replace`

```python
Replace: List[Any] = []
```


    List of things this item is considered by its author to replace. The format is
    identical to dependencies.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2577.

## `FreeCAD.Metadata.Tag`

```python
Tag: List[str] = []
```

List of strings.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2579.

## `FreeCAD.Metadata.Icon`

```python
Icon: str = ''
```

Relative path to an icon file.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2581.

## `FreeCAD.Metadata.Classname`

```python
Classname: str = ''
```


    String representing the name of the main Python class this item
    creates/represents.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2583.

## `FreeCAD.Metadata.Subdirectory`

```python
Subdirectory: str = ''
```


    String representing the name of the subdirectory this content item is located in.
    If empty, the item is in a directory named the same as the content item.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2585.

## `FreeCAD.Metadata.File`

```python
File: List[Any] = []
```


    List of files associated with this item.
    The meaning of each file is implementation-defined.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2587.

## `FreeCAD.Metadata.Content`

```python
Content: Dict[str, List['Metadata']] = {}
```


    Dictionary of lists of content items: defined recursively, each item is itself
    a Metadata object.
    See package.xml file format documentation for details.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2589.

## `FreeCAD.Metadata.FreeCADMin`

```python
FreeCADMin: str = ''
```


    String representing the minimum version of FreeCAD needed for this item.
    If unset it will be 0.0.0.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2591.

## `FreeCAD.Metadata.FreeCADMax`

```python
FreeCADMax: str = ''
```


    String representing the maximum version of FreeCAD needed for this item.
    If unset it will be 0.0.0.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2593.

## `FreeCAD.Metadata.PythonMin`

```python
PythonMin: str = ''
```


    String representing the minimum version of Python needed for this item.
    If unset it will be 0.0.0.
    

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2595.

## `FreeCAD.Metadata.getLastSupportedFreeCADVersion`

```python
def getLastSupportedFreeCADVersion(self) -> Optional[str]:
```

Search through all content package items, and determine if a maximum supported
version of FreeCAD is set.
Returns None if no maximum version is set, or if *any* content item fails to
provide a maximum version (implying that that content item will work with all
known versions).

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2598.

## `FreeCAD.Metadata.getFirstSupportedFreeCADVersion`

```python
def getFirstSupportedFreeCADVersion(self) -> Optional[str]:
```

Search through all content package items, and determine if a minimum supported
version of FreeCAD is set.
Returns 0.0 if no minimum version is set, or if *any* content item fails to
provide a minimum version (implying that that content item will work with all
known versions. Technically limited to 0.20 as the lowest known version since
the metadata standard was added then).

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2608.

## `FreeCAD.Metadata.supportsCurrentFreeCAD`

```python
def supportsCurrentFreeCAD(self) -> bool:
```

Returns False if this metadata object directly indicates that it does not
support the current version of FreeCAD, or True if it makes no indication, or
specifically indicates that it does support the current version. Does not
recurse into Content items.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2619.

## `FreeCAD.Metadata.getGenericMetadata`

```python
def getGenericMetadata(self, name: str, /) -> List[Any]:
```

Get the list of GenericMetadata objects with key 'name'.
Generic metadata objects are Python objects with a string 'contents' and a
dictionary of strings, 'attributes'. They represent unrecognized simple XML tags
in the metadata file.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2628.

## `FreeCAD.Metadata.addContentItem`

```python
def addContentItem(self, content_type: str, metadata: 'Metadata', /) -> None:
```

Add a new content item of type 'content_type' with metadata 'metadata'.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2637.

## `FreeCAD.Metadata.removeContentItem`

```python
def removeContentItem(self, content_type: str, name: str, /) -> None:
```

Remove the content item of type 'content_type' with name 'name'.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2643.

## `FreeCAD.Metadata.addMaintainer`

```python
def addMaintainer(self, name: str, email: str, /) -> None:
```

Add a new Maintainer.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2649.

## `FreeCAD.Metadata.removeMaintainer`

```python
def removeMaintainer(self, name: str, email: str, /) -> None:
```

Remove the Maintainer.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2655.

## `FreeCAD.Metadata.addLicense`

```python
def addLicense(self, short_code: str, path: str, /) -> None:
```

Add a new License.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2661.

## `FreeCAD.Metadata.removeLicense`

```python
def removeLicense(self, short_code: str, path: str, /) -> None:
```

Remove the License.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2667.

## `FreeCAD.Metadata.addUrl`

```python
def addUrl(self, url_type: str, url: str, branch: str=..., /) -> None:
```

Add a new Url or type 'url_type' (which should be one of 'repository', 'readme',

'bugtracker', 'documentation', or 'webpage') If type is 'repository' you

must also specify the 'branch' parameter.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2673.

## `FreeCAD.Metadata.removeUrl`

```python
def removeUrl(self, url_type: str, url: str, branch: str=..., /) -> None:
```

Remove the Url.

A default shown as `...` is unspecified by the stub; it is not a value to pass.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2683.

## `FreeCAD.Metadata.addAuthor`

```python
def addAuthor(self, name: str, email: str, /) -> None:
```

Add a new Author with name 'name', and optionally email 'email'.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2689.

## `FreeCAD.Metadata.removeAuthor`

```python
def removeAuthor(self, name: str, email: str, /) -> None:
```

Remove the Author.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2695.

## `FreeCAD.Metadata.addDepend`

```python
def addDepend(self, dependency: dict[str, Any], /) -> None:
```

Add a new Dependency described by the given dictionary.

See the `Depend` attribute for the recognized keys.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2701.

## `FreeCAD.Metadata.removeDepend`

```python
def removeDepend(self, dependency: dict[str, Any], /) -> None:
```

Remove the Dependency described by the given dictionary.

See the `Depend` attribute for the recognized keys.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2709.

## `FreeCAD.Metadata.addConflict`

```python
def addConflict(self, dependency: dict[str, Any], /) -> None:
```

Add a new Conflict. See documentation for addDepend().

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2717.

## `FreeCAD.Metadata.removeConflict`

```python
def removeConflict(self, dependency: dict[str, Any], /) -> None:
```

Remove the Conflict. See documentation for removeDepend().

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2723.

## `FreeCAD.Metadata.addReplace`

```python
def addReplace(self, dependency: dict[str, Any], /) -> None:
```

Add a new Replace.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2729.

## `FreeCAD.Metadata.removeReplace`

```python
def removeReplace(self, dependency: dict[str, Any], /) -> None:
```

Remove the Replace.

Typing limit: `Any` leaves this contract partially unspecified; do not infer accepted types from it.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2735.

## `FreeCAD.Metadata.addTag`

```python
def addTag(self, tag: str, /) -> None:
```

Add a new Tag.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2741.

## `FreeCAD.Metadata.removeTag`

```python
def removeTag(self, tag: str, /) -> None:
```

Remove the Tag.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2747.

## `FreeCAD.Metadata.addFile`

```python
def addFile(self, filename: str, /) -> None:
```

Add a new File.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2753.

## `FreeCAD.Metadata.removeFile`

```python
def removeFile(self, filename: str, /) -> None:
```

Remove the File.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2759.

## `FreeCAD.Metadata.write`

```python
def write(self, filename: str, /) -> None:
```

Write the metadata to the given file as XML data.

Evidence: public stub `FreeCAD/__init__.pyi` line(s) 2765.

