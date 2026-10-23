# `FreeCAD.Base.Matrix`

[Module](index.md)

```python
class Matrix:
```

Base.Matrix class.

A 4x4 Matrix.
In particular, this matrix can represent an affine transformation, that is,
given a 3D vector `x`, apply the transformation y = M*x + b, where the matrix
`M` is a linear map and the vector `b` is a translation.
`y` can be obtained using a linear transformation represented by the 4x4 matrix
`A` conformed by the augmented 3x4 matrix (M|b), augmented by row with
(0,0,0,1), therefore: (y, 1) = A*(x, 1).

The following constructors are supported:

Matrix()
Empty constructor.

Matrix(matrix)
Copy constructor.
matrix : Base.Matrix.

Matrix(*coef)
Define from 16 coefficients of the 4x4 matrix.
coef : sequence of float
    The sequence can have up to 16 elements which complete the matrix by rows.

Matrix(vector1, vector2, vector3, vector4)
Define from four 3D vectors which represent the columns of the 3x4 submatrix,
useful to represent an affine transformation. The fourth row is made up by
(0,0,0,1).
vector1 : Base.Vector
vector2 : Base.Vector
vector3 : Base.Vector
vector4 : Base.Vector
    Default to (0,0,0). Optional.

Author: Juergen Riegel (FreeCAD@juergen-riegel.net)
Licence: LGPL

Evidence: public stub `FreeCAD/Base.pyi` line 521. Inherited members are on the named base's reference; aliases keep their imported identity.

## `FreeCAD.Base.Matrix.A11`

```python
A11: float = 0.0
```

The (1,1) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 560.

## `FreeCAD.Base.Matrix.A12`

```python
A12: float = 0.0
```

The (1,2) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 562.

## `FreeCAD.Base.Matrix.A13`

```python
A13: float = 0.0
```

The (1,3) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 564.

## `FreeCAD.Base.Matrix.A14`

```python
A14: float = 0.0
```

The (1,4) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 566.

## `FreeCAD.Base.Matrix.A21`

```python
A21: float = 0.0
```

The (2,1) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 568.

## `FreeCAD.Base.Matrix.A22`

```python
A22: float = 0.0
```

The (2,2) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 570.

## `FreeCAD.Base.Matrix.A23`

```python
A23: float = 0.0
```

The (2,3) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 572.

## `FreeCAD.Base.Matrix.A24`

```python
A24: float = 0.0
```

The (2,4) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 574.

## `FreeCAD.Base.Matrix.A31`

```python
A31: float = 0.0
```

The (3,1) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 576.

## `FreeCAD.Base.Matrix.A32`

```python
A32: float = 0.0
```

The (3,2) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 578.

## `FreeCAD.Base.Matrix.A33`

```python
A33: float = 0.0
```

The (3,3) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 580.

## `FreeCAD.Base.Matrix.A34`

```python
A34: float = 0.0
```

The (3,4) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 582.

## `FreeCAD.Base.Matrix.A41`

```python
A41: float = 0.0
```

The (4,1) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 584.

## `FreeCAD.Base.Matrix.A42`

```python
A42: float = 0.0
```

The (4,2) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 586.

## `FreeCAD.Base.Matrix.A43`

```python
A43: float = 0.0
```

The (4,3) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 588.

## `FreeCAD.Base.Matrix.A44`

```python
A44: float = 0.0
```

The (4,4) matrix element.

Access: attribute declaration; `Final` constrains typing, but does not independently verify runtime writability.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 590.

## `FreeCAD.Base.Matrix.A`

```python
@property
def A(self) -> tuple[float, ...]:

@A.setter
def A(self, value: Sequence[float]) -> None:
```

The matrix elements.

Access: getter and setter declared in the stub.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 594, 599.

## `FreeCAD.Base.Matrix.move`

```python
@overload
def move(self, vector: Vector | tuple[float, float, float], /) -> None:

@overload
def move(self, x: float, y: float, z: float, /) -> None:

def move(self, *args) -> None:
```

Move the matrix along a vector, equivalent to left multiply the matrix
by a pure translation transformation.

vector : Base.Vector, tuple
x : float
    `x` translation.
y : float
    `y` translation.
z : float
    `z` translation.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 603, 607, 610.

## `FreeCAD.Base.Matrix.scale`

```python
@overload
def scale(self, vector: Vector | tuple[float, float, float], /) -> None:

@overload
def scale(self, x: float, y: float, z: float, /) -> None:

@overload
def scale(self, factor: float, /) -> None:

def scale(self, *args) -> None:
```

Scale the first three rows of the matrix.

vector : Base.Vector
x : float
    First row factor scale.
y : float
    Second row factor scale.
z : float
    Third row factor scale.
factor : float
    global factor scale.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 626, 630, 634, 637.

## `FreeCAD.Base.Matrix.hasScale`

```python
def hasScale(self, tol: float=0, /) -> ScaleType:
```

Return an enum value of ScaleType. Possible values are:
Uniform, NonUniformLeft, NonUniformRight, NoScaling or Other
if it's not a scale matrix.

tol : float

Evidence: public stub `FreeCAD/Base.pyi` line(s) 653.

## `FreeCAD.Base.Matrix.decompose`

```python
def decompose(self) -> Tuple['Matrix', 'Matrix', 'Matrix', 'Matrix']:
```

Return a tuple of matrices representing shear, scale, rotation and move.
So that matrix = move * rotation * scale * shear.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 663.

## `FreeCAD.Base.Matrix.nullify`

```python
def nullify(self) -> None:
```

Make this the null matrix.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 670.

## `FreeCAD.Base.Matrix.isNull`

```python
def isNull(self) -> bool:
```

Check if this is the null matrix.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 676.

## `FreeCAD.Base.Matrix.unity`

```python
def unity(self) -> None:
```

Make this matrix to unity (4D identity matrix).

Evidence: public stub `FreeCAD/Base.pyi` line(s) 682.

## `FreeCAD.Base.Matrix.isUnity`

```python
def isUnity(self, tol: float=0.0, /) -> bool:
```

Check if this is the unit matrix (4D identity matrix).

Evidence: public stub `FreeCAD/Base.pyi` line(s) 688.

## `FreeCAD.Base.Matrix.transform`

```python
def transform(self, vector: Vector, matrix2: 'Matrix', /) -> None:
```

Transform the matrix around a given point.
Equivalent to left multiply the matrix by T*M*T_inv, where M is `matrix2`, T the
translation generated by `vector` and T_inv the inverse translation.
For example, if `matrix2` is a rotation, the result is the transformation generated
by the current matrix followed by a rotation around the point represented by `vector`.

vector : Base.Vector
matrix2 : Base.Matrix

Evidence: public stub `FreeCAD/Base.pyi` line(s) 694.

## `FreeCAD.Base.Matrix.col`

```python
def col(self, index: int, /) -> Vector:
```

Return the vector of a column, that is, the vector generated by the three
first elements of the specified column.

index : int
    Required column index.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 707.

## `FreeCAD.Base.Matrix.setCol`

```python
def setCol(self, index: int, vector: Vector, /) -> None:
```

Set the vector of a column, that is, the three first elements of the specified
column by index.

index : int
    Required column index.
vector : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 717.

## `FreeCAD.Base.Matrix.row`

```python
def row(self, index: int, /) -> Vector:
```

Return the vector of a row, that is, the vector generated by the three
first elements of the specified row.

index : int
    Required row index.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 728.

## `FreeCAD.Base.Matrix.setRow`

```python
def setRow(self, index: int, vector: Vector, /) -> None:
```

Set the vector of a row, that is, the three first elements of the specified
row by index.

index : int
    Required row index.
vector : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 738.

## `FreeCAD.Base.Matrix.diagonal`

```python
def diagonal(self) -> Vector:
```

Return the diagonal of the 3x3 leading principal submatrix as vector.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 749.

## `FreeCAD.Base.Matrix.setDiagonal`

```python
def setDiagonal(self, vector: Vector, /) -> None:
```

Set the diagonal of the 3x3 leading principal submatrix.

vector : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 755.

## `FreeCAD.Base.Matrix.rotateX`

```python
def rotateX(self, angle: float | Quantity, /) -> None:
```

Rotate around X axis.

angle : float
    Angle in radians.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 763.

## `FreeCAD.Base.Matrix.rotateY`

```python
def rotateY(self, angle: float | Quantity, /) -> None:
```

Rotate around Y axis.

angle : float
    Angle in radians.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 772.

## `FreeCAD.Base.Matrix.rotateZ`

```python
def rotateZ(self, angle: float | Quantity, /) -> None:
```

Rotate around Z axis.

angle : float
    Angle in radians.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 781.

## `FreeCAD.Base.Matrix.multiply`

```python
@overload
def multiply(self, matrix: 'Matrix', /) -> 'Matrix':

@overload
def multiply(self, vector: Vector, /) -> Vector:

def multiply(self, obj: Union['Matrix', Vector], /) -> Union['Matrix', Vector]:
```

Right multiply the matrix by the given object.
If the argument is a vector, this is augmented to the 4D vector (`vector`, 1).

matrix : Base.Matrix
vector : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 791, 795, 798.

## `FreeCAD.Base.Matrix.multVec`

```python
def multVec(self, vector: Vector, /) -> Vector:
```

Compute the transformed vector using the matrix.

vector : Base.Vector

Evidence: public stub `FreeCAD/Base.pyi` line(s) 808.

## `FreeCAD.Base.Matrix.invert`

```python
def invert(self) -> None:
```

Compute the inverse matrix in-place, if possible.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 816.

## `FreeCAD.Base.Matrix.inverse`

```python
def inverse(self) -> 'Matrix':
```

Compute the inverse matrix, if possible.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 822.

## `FreeCAD.Base.Matrix.transpose`

```python
def transpose(self) -> None:
```

Transpose the matrix in-place.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 828.

## `FreeCAD.Base.Matrix.transposed`

```python
def transposed(self) -> 'Matrix':
```

Returns a transposed copy of this matrix.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 834.

## `FreeCAD.Base.Matrix.determinant`

```python
def determinant(self) -> float:
```

Compute the determinant of the matrix.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 840.

## `FreeCAD.Base.Matrix.isOrthogonal`

```python
def isOrthogonal(self, tol: float=1e-06, /) -> float:
```

Checks if the matrix is orthogonal, i.e. M * M^T = k*I and returns
the multiple of the identity matrix. If it's not orthogonal 0 is returned.

tol : float
    Tolerance used to check orthogonality.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 846.

## `FreeCAD.Base.Matrix.submatrix`

```python
def submatrix(self, dim: int, /) -> 'Matrix':
```

Get the leading principal submatrix of the given dimension.
The (4 - `dim`) remaining dimensions are completed with the
corresponding identity matrix.

dim : int
    Dimension parameter must be in the range [1,4].

Evidence: public stub `FreeCAD/Base.pyi` line(s) 856.

## `FreeCAD.Base.Matrix.analyze`

```python
def analyze(self) -> str:
```

Analyzes the type of transformation.

Evidence: public stub `FreeCAD/Base.pyi` line(s) 867.

