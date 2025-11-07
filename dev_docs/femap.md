# FEMAP Neutral File Format
This document describes the **FEMAP Neutral File Format**.

This information is not required unless you are going to write your own interfaces to read or write Neutral Files.

## **File Structure**

FEMAP Neutral files follow a very structured format that makes them relatively easy to read and write.

All data is contained in **“data blocks”**.

Each data block begins with a “`-1`” and an ID, and also ends with a “`-1`”.

In a formatted Neutral file it looks like the following:

| **Description** | **File Contains** |
| --- | --- |
| Start of Data Block |    `   -1` |
| Data Block ID |    `100` |
| All of the data for this data block. This is usually multiple records. | `Data` |
| End of Data Block |    `   -1` |

Any number of data blocks can be in the file, and they can appear in any order.

Data blocks of the same type can even be repeated, when necessary.

## **Formatted Neutral Files**

Formatted Neutral Files contain **free-format, record-oriented data blocks**.

You will notice that each value is separated by a comma, and there are even trailing commas at the end of each record (line).

These commas are not required, but values must be separated by at least one or more spaces.

The only fixed field requirements are for the “`   -1`” start and end of block indicators —

they must always be preceded by **3 spaces** and start in the **fourth column**.

All other records should start in the first column.

### **Integer Values**

Integer values are all subject to the limitations for the corresponding numbers in FEMAP.

In no case can an ID ever exceed the range **1 to 99999999**.

Other limitations are described in the formats shown below.

### **Real Values**

Real numbers can be written in either floating point or exponential format.

Any reasonable number of significant digits can be included, but the total length of any line can not exceed **255 characters**.

### **Character Strings**

Titles and other text items are simply written as a series of characters.

In a formatted file, they are always the only item in the record, so the end of the line terminates them.

If the character string is really empty (has no characters), FEMAP will write the special string **“<NULL>”**.

If you are reading a Neutral file, you should interpret this as a blank string.


# **Data Block 100 – Neutral File Header**

| **Line** | **Field** | **Description** | **Size** |
| --- | --- | --- | --- |
| **1** | Title | Database title | Character string |
| **2** | Version | The version of FEMAP used to create this file.  Currently should be **4.41** | 8 byte, double precision |

Sample:
```
   -1
   100
<NULL>
4.41,
   -1
```

# **Data Block 403 – Nodes**

| **Line** | **Field** | **Description** | **Size** |
| --- | --- | --- | --- |
| **1** | ID | ID of node | 4 byte, long integers |
|  | define_sys | ID of definition coordinate system (0 here) |  |
|  | output_sys | ID of output coordinate system (0 here) |  |
|  | layer | ID of layer (1 here) |  |
|  | color | ID of color (46 here) |  |
|  | pembc[0..5] | The six permanent constraints (0 = free, 1 = fixed) (0,0,0,0,0,0, here) | 2 byte, boolean |
|  | x | X-coordinate of node in Global Rectangular coordinate system | 8 byte, double precision |
|  | y | Y-coordinate of node in Global Rectangular coordinate system | 8 byte, double precision |
|  | z | Z-coordinate of node in Global Rectangular coordinate system | 8 byte, double precision |

template:
```
ID,define_sys,output_sys,layer,color,pembc[0],pembc[1],pembc[2],pembc[3],pembc[4],pembc[5],x,y,z,
```

in this project:
```
ID,0,0,1,46,0,0,0,0,0,0,x,y,z,
```

sample:
```
   -1
   403
1,0,0,1,46,0,0,0,0,0,0,  0.00000e+00,  0.00000e+00,  0.00000e+00,
2,0,0,1,46,0,0,0,0,0,0,  1.00000e-02,  0.00000e+00,  0.00000e+00,
   -1
```

# **Data Block 404 – Elements**

| **Line** | **Field** | **Description** | **Size** |
| --- | --- | --- | --- |
| **1** | ID | ID of element | 4 byte, long integers |
|  | color | ID of color (124 here) |  |
|  | propID | ID of property |  |
|  | type | Element Type (refer to property tables for values) |  |
|  | topology | **Element Shape:**  0=Line2, 2=Tri3, 3=Tri6, 4=Quad4, 5=Quad8, 6=Tetra4, 7=Wedge6, 8=Brick8, 9=Point, 10=Tetra10, 11=Wedge15, 12=Brick20, 13=Rigid, 15=MultiList, 16=Contact, 17=Weld | 4 byte, long integers |
|  | layer | ID of layer |  |
|  | orientID | Third node for bar/beam (0 here) |  |
|  | matl_orflag | Material orientation flag (0 if not set, 1 if set) (0 here) | 2 byte, boolean |
| **2** | node[0..9] | Nodes referenced by element |  |
| **3** | node[10..19] |  |  |
| **4** | orient[0..2] | Element orientation vector for bar/beam. [0] contains material orientation angle for planar elements. | 8 byte, double precision (0.,0.,0., here) |
| **5** | offset1[0..2] | Offsets at end1 of bar/beam (0.,0.,0., here) |  |
| **6** | offset2[0..2] | Offsets at end2 of bar/beam (0.,0.,0., here) |  |
| **7** | list[0..15] | (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, here) | 2 byte, boolean |

template:
```
ID,color,propID,type,topology,layer,orientID,matl_orflag,
node[0],node[1],node[2],node[3],node[4],node[5],node[6],node[7],node[8],node[9],
node[10],node[11],node[12],node[13],node[14],node[15],node[16],node[17],node[18],node[19],
orient[0],orient[1],orient[2],
offset1[0],offset1[1],offset1[2],
offset2[0],offset2[1],offset2[2],
list[0],list[1],list[2],list[3],list[4],list[5],list[6],list[7],list[8],list[9],list[10],list[11],list[12],list[13],list[14],list[15],
``` 

in this project:
```
ID,124,propID,type,topology,layer,0,0,
node[0],node[1],node[2],node[3],node[4],node[5],node[6],node[7],node[8],node[9],
node[10],node[11],node[12],node[13],node[14],node[15],node[16],node[17],node[18],node[19],
0.,0.,0.,
0.,0.,0.,
0.,0.,0.,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
```

sample:
```
   -1
   404
225,124,1,25,8,1,0,0,
1,2,4,3,1001,1002,1004,1003,0,0,
0,0,0,0,0,0,0,0,0,0,
0.,0.,0.,
0.,0.,0.,
0.,0.,0.,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
226,124,1,25,8,1,0,0,
2,5,7,4,1002,1005,1007,1004,0,0,
0,0,0,0,0,0,0,0,0,0,
0.,0.,0.,
0.,0.,0.,
0.,0.,0.,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    -1
```

### **Record for Each Node Plus Final**

| **Field** | **Description** | **Size** |
| --- | --- | --- |
| nodeID | ID of node referenced by element. This must be 1 to end the list. | 4 byte, long integers |
| faceID | Element face ID |  |
| weight | Weighting factor for interpolation elements | 8 byte, double precision |
| dof[1..6] | Flags indicating active degrees of freedom for interpolation | 4 byte, long integers |

---

### **Node Reference Entries for Elements**

| **Topology** | **Array Entries** |
| --- | --- |
| Point | 0 |
| Line2 | 0,1 |
| Line3 | 0,1,2 |
| Tri3 | 0,1,2 |
| Tri6 | 0,1,2,(3,4,5) |
| Quad4 | 0,1,2,3 |
| Quad8 | 0,1,2,3,(4,5,6,7) |
| Tetra4 | 0,1,2,3 |
| Tetra10 | 0,1,2,3,(4,5,6,7,8,9) |
| Wedge6 | 0,1,2,3,4,5 |
| Wedge15 | 0,1,2,3,4,5,(6,7,8,9,10,11,12,13,14) |
| Brick8 | 0,1,2,3,4,5,6,7 |
| Brick20 | 0,1,2,3,4,5,6,7,(8,9,10,11,12,13,14,15,16,17,18,19) |
| RigidList | 0=Independent, Dependent Nodes use Element Lists, not Array Entries |
| RigidListID | REID-0=Independent, 1=Dependent, Nodes use Element Lists, not Array Entries |
| MultiList | Uses Element Lists, not Array Entries |
| Contact | References contact segments, not nodes |
| Weld | Weld Axis=0 SegA=4,5,6,(7,8,9,10,11) SegB=12,13,14,(15,16,17,18,19) |


# **Data Block 402 – Properties**

| **Line** | **Field** | **Description** | **Size** |
| ---------- | --------- | --------------- | -------- |
| **1**      | ID        | ID of property | 4 byte, long integers |
|   | color     | ID of color (here 24) | |
|   | matlID    | ID of material (here 1) | |
|   | type      | Type of property (here 25) | |
|   | layer     | ID of layer (here 1) | |
|   | refCS     | Reference coordinate system (here 0) | |
| **2**      | title     | Property Title (max 79 characters) (here Solid) | character string |
| **3**      | flag[0..3]| Property flags (0,0,0,0, here)| 4 byte, long integers |
| **4**      | num_lam   | Max material lamina (here 8)  | |
| **5**   | list[0..7] | (here 0,0,0,0,0,0,0,0,) | |
| **6**      | int | (here 5) | |
| **7**      | real[0..4]| (here 0.,0.,0.,0.,0.,) | |

template:
```
ID,color,matlID,type,layer,refCS,
title,
flag[0],flag[1],flag[2],flag[3],
num_lam,
list[0],list[1],list[2],list[3],list[4],list[5],list[6],list[7],
int,
real[0],real[1],real[2],real[3],real[4],
``` 
in this project:
```
ID,24,1,25,1,0,
Solid,
0,0,0,0,
8,
0,0,0,0,0,0,0,0,
5,
0.,0.,0.,0.,0.,
```
example:
```
   -1
   402
1,24,1,25,1,0,
Solid
0,0,0,0,
8,
0,0,0,0,0,0,0,0,
5,
0.,0.,0.,0.,0.,
3,24,1,25,1,0,
Solid
0,0,0,0,
8,
0,0,0,0,0,0,0,0,
5,
0.,0.,0.,0.,0.,
4,24,1,25,1,0,
Solid
0,0,0,0,
8,
0,0,0,0,0,0,0,0,
5,
0.,0.,0.,0.,0.,
   -1
```
# **Data Block 601 – Materials**

always:
```
   -1
   601
1,-601,55,0,0,1,0,
<NULL>
10,
0,0,0,0,0,0,0,0,0,0,
25,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,
200,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,,
50,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
70,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
   -1
```

Here’s your **Data Block 450 – Output Sets** section converted into clean and properly structured **Markdown format**:

---

## **Data Block 450 – Output Sets**

| **Record**     | **Field**     | **Description** | **Size** |
| -------------- | ------------- | --------------- | -------- |
| **1** | ID   | ID of output set  | 4 byte, long integers |
| **2** | title| Output Set title (max 79 characters) | character string|
| **3** | from_prog     | always 0 |        |
|       | ProcessType   | always 3 | 4 byte, long integers    |
| **4** | value| Time or Frequency value for this case. 0.0 for static analysis.  | 8 byte, double precision |
| **5** | nlines        | always 1   | 4 byte, long integers    |
| **6** | notes| always <NULL>  | character string|

template:
```
ID,
title,
0,3,
value,
1,
<NULL>,
```

sample:
```
   -1
   450
6,
STEP:6 Time: 6.00000e-02
0,3,
 6.00000e-02,
1,
<NULL>
   -1
```

Here’s your **Data Block 1051 – Output Data Vectors** converted into clean, structured **Markdown format** for documentation:

---

# **Data Block 1051 – Output Data Vectors**

| **Line** | **Field** | **Description** | **Size** |
| ---------- | --------- | --------------- | -------- |
| **1** | setID    | ID of output set     | 4 byte, long integers    |
|       | vecID    | ID of output vector, must be unique in each output set (always 60011)   | 4 byte, long integers    |
|       | 1        | Always 1    | 2 byte, boolean |
| **2** | title    | Output Vector title (max 79 characters)| character string|
| **3** | min_val  | Minimum value in vector (always 0.) | 8 byte, double precision |
|       | max_val  | Maximum value in vector. <br>If `max_val < min_val`, FEMAP will search the output for the max, min, and abs_max values. (always -1.) | 8 byte, double precision |
|       | abs_max  | Maximum absolute value in vector (always 0.) | 8 byte, double precision |
| **4** | comp[0..9]        | Component vectors. Either zero, or the IDs of the X, Y, Z components, or the IDs of the corresponding elemental corner output. (always 60011,0,0,0,0,0,0,0,0,0,)   | 4 byte, long integers    |
| **5** | comp[10..19]      | Continuation of component vectors (always 0,0,0,0,0,0,0,0,0,0,)      | 4 byte, long integers    |
| **6** | id_min   | ID of entity where minimum value occurs (0 if FEMAP will recalc max/min) (always 0)  | 4 byte, long integers    |
|       | id_max   | ID of entity where maximum value occurs (0 if FEMAP will recalc max/min) (always 0)  | 4 byte, long integers    |
|       | out_type | Type of output <br>(0=Any, 1=Disp, 2=Accel, 3=Force, 4=Stress, 5=Strain, 6=Temp, others=User) (always 3)|        |
|       | ent_type | Either nodal (7) or elemental (8) output        |        |
| **7** | calc_warn| If 1, cannot linearly combine this output (always 0)       | 2 byte, boolean |
|       | comp_dir | If 1, comp[0..2] are X,Y,Z component values. <br>If 2, data at end of beams. <br>If 3, reverse data at second end of beam. (always 1)      | 4 byte, long integers    |
|       | cent_total        | If 1, vector has centroidal or nodal output (always 1)    | 2 byte, boolean |


### **Result Records**

Repeated records exist for all result values in one of two formats, depending on entity numbering in the model.
When reading the file, FEMAP reads a record and if there are only two fields, it assumes **Format 1**;
if there are more fields, then it must be **Format 2**.

#### **Format 1**

| **Field** | **Description**| **Size**        |
| --------- | ----------------------------------------- | ------------------------ |
| entityID  | ID of the single node/element for results | 4 byte, long integers    |
| value     | Result value   | 8 byte, double precision |

#### **Format 2**

| **Field**      | **Description**| **Size**     |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| start_entityID | First ID       | 4 byte, long integers |
| end_entityID   | Final ID       | 4 byte, long integers |
| values[0..n]   | Values for each entity from start_entityID to end_entityID. Results for all IDs in this range are included (no holes). <br>Values are written so there are a total of 10 fields on each line — first line has 2 IDs and 8 values; remaining lines have 10 values (last line may have fewer). |     |

template:
```
setID,vecID,1,
title,
min_val,max_val,abs_max,
comp[0],comp[1],comp[2],comp[3],comp[4],comp[5],comp[6],comp[7],comp[8],comp[9],
comp[10],comp[11],comp[12],comp[13],comp[14],comp[15],comp[16],comp[17],comp[18],comp[19],
id_min,id_max,out_type,ent_type,
calc_warn,comp_dir,cent_total,
<result records in Format 1 or Format 2>
```

in this project:
```
6,60011,1,
DISPLACEMENTS,
0.,-1.,0.,
60011,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,3,7,
0,1,1,
<result records in Format 1 or Format 2>
```