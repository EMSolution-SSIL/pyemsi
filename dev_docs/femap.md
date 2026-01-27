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
| **1** | Title | always <NULL> | Character string |
| **2** | Version | always 4.41 | 8 byte, double precision |

template:
```
   -1
   100
Title,
Version,
   -1
```


# **Data Block 403 – Nodes**

| **Line** | **Field** | **Description** | **Size** |
| --- | --- | --- | --- |
| **1** | ID | ID of node | 4 byte, long integers |
|  | define_sys | always 0 |  |
|  | output_sys | always 0 |  |
|  | layer | always 1 |  |
|  | color | always 46 |  |
|  | pembc[0..5] | always 0,0,0,0,0,0, | 2 byte, boolean |
|  | x | X-coordinate of node in Global Rectangular coordinate system | 8 byte, double precision |
|  | y | Y-coordinate of node in Global Rectangular coordinate system | 8 byte, double precision |
|  | z | Z-coordinate of node in Global Rectangular coordinate system | 8 byte, double precision |

template:
```
   -1
   403
ID,0,0,1,46,0,0,0,0,0,0,x,y,z,
...
   -1
```

# **Data Block 404 – Elements**

| **Line** | **Field** | **Description** | **Size** |
| --- | --- | --- | --- |
| **1** | ID | ID of element | 4 byte, long integers |
|  | color | always 124 |  |
|  | propID | ID of property |  |
|  | type | always 25 |  |
|  | topology | **Element Shape:**  0=Line2, 2=Tri3, 3=Tri6, 4=Quad4, 5=Quad8, 6=Tetra4, 7=Wedge6, 8=Brick8, 9=Point, 10=Tetra10, 11=Wedge15, 12=Brick20, 13=Rigid, 15=MultiList, 16=Contact, 17=Weld | 4 byte, long integers |
|  | layer | always 1 |  |
|  | orientID | always 0 |  |
|  | matl_orflag | always 0 | 2 byte, boolean |
| **2** | node[0..9] | Nodes referenced by element |  |
| **3** | node[10..19] |  |  |
| **4** | orient[0..2] | always 0.,0.,0., |
| **5** | offset1[0..2] | always 0.,0.,0., |  |
| **6** | offset2[0..2] | always 0.,0.,0., |  |
| **7** | list[0..15] | always 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, | 2 byte, boolean |

template:
```
    -1
    404
ID,124,propID,25,topology,1,0,0,
node[0],node[1],node[2],node[3],node[4],node[5],node[6],node[7],node[8],node[9],
node[10],node[11],node[12],node[13],node[14],node[15],node[16],node[17],node[18],node[19],
0.,0.,0.,
0.,0.,0.,
0.,0.,0.,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
...
    -1
```

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
|   | color     | always 24 | |
|   | matlID    | always 1 | |
|   | type      | always 25 | |
|   | layer     | always 1 | |
|   | refCS     | always 0 | |
| **2**      | title     | always Solid | character string |
| **3**      | flag[0..3]| always 0,0,0,0, | 4 byte, long integers |
| **4**      | num_lam   | always 8  | |
| **5**   | list[0..7] | always 0,0,0,0,0,0,0,0, | |
| **6**      | int | always 5 | |
| **7**      | real[0..4]| always 0.,0.,0.,0.,0., | |

template:
```
   -1
   402
ID,24,1,25,1,0,
Solid,
0,0,0,0,
8,
0,0,0,0,0,0,0,0,
5,
0.,0.,0.,0.,0.,
...
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
   -1
   450
ID,
title,
0,3,
value,
1,
<NULL>,
...
   -1
```

# **Data Block 1051 – Output Data Vectors**

| **Line** | **Field** | **Description** | **Size** |
| ---------- | --------- | --------------- | -------- |
| **1** | setID    | ID of output set     | 4 byte, long integers    |
|       | vecID    | ID of output vector, must be unique in each output set (always 60011)   | 4 byte, long integers    |
|       | 1        | always 1    | 2 byte, boolean |
| **2** | title    | Output Vector title (max 79 characters)| character string|
| **3** | min_val  | always 0. | 8 byte, double precision |
|       | max_val  | always -1. | 8 byte, double precision |
|       | abs_max  | always 0. | 8 byte, double precision |
| **4** | comp[0..9] | always 0,0,0,0,0,0,0,0,0,0, | 4 byte, long integers    |
| **5** | comp[10..19] | always 0,0,0,0,0,0,0,0,0,0, | 4 byte, long integers    |
| **6** | id_min   | always 0 | 4 byte, long integers    |
|       | id_max   | always 0 | 4 byte, long integers    |
|       | out_type | always 3 |        |
|       | ent_type | Either nodal (7) or elemental (8) output |        |
| **7** | calc_warn| always 0 | 2 byte, boolean |
|       | comp_dir | always 1 | 4 byte, long integers |
|       | cent_total | always 1 | 2 byte, boolean |


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

| **Field** | **Description** | **Size** |
| --------- | --------------- | -------- |
| start_entityID | First ID       | 4 byte, long integers |
| end_entityID   | Final ID       | 4 byte, long integers |
| values[0..n]   | Values for each entity from start_entityID to end_entityID. Results for all IDs in this range are included (no holes). <br>Values are written so there are a total of 10 fields on each line — first line has 2 IDs and 8 values; remaining lines have 10 values (last line may have fewer). |     |

template:
```
   -1
   1051
setID1,vecID1,1,
title1,
0.,-1.,0.,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,3,ent_type1,
0,1,1,
<result records in Format 1 or Format 2>
-1,0.,
setID2,vecID2,1,
title2,
0.,-1.,0.,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,3,ent_type2,
0,1,1,
<result records in Format 1 or Format 2>
-1,0.,
...
   -1
```