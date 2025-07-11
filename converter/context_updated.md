# pyvnt: Class Structure and Example Usage Context

## Core Class Structure

### 1. ValueProperty (Abstract)
- Parent for all property classes (e.g., `Int_P`, `Flt_P`, `Enm_P`).
- Enforces interface for value properties used in Key_C.

### 2. Int_P, Flt_P, Str_P, Enm_P
- Store typed values with constraints (e.g., min/max/default for ints/floats, set of choices for enums).
- Example: `Enm_P('val1', items={'PCG', 'PBiCG', 'PBiCGStab'}, default='PCG')`

### 3. Key_C
- Represents a dictionary-like node holding multiple ValueProperty instances.
- Enforces encapsulation: attributes are only set via constructor or methods.
- Example: `Key_C('solver', prop1, prop2)`
- Methods: `replaceVal`, `delVal`, `giveVal`, etc.

### 4. Node_C
- Tree node class (inherits from anytree's NodeMixin).
- Holds a name, parent, children, and a list of Key_C objects as data.
- Methods: `addChild`, `setParent`, `add_data`, `removeData`, `getChild`, etc.

### 5. show_tree
- Utility to print the tree structure and Key_C at each node.

## Example: Creating and Displaying a Tree

```python
from pyvnt import *

# Define properties
prop1 = Enm_P('val1', items={'PCG', 'PBiCG', 'PBiCGStab'}, default='PCG')
prop2 = Enm_P('val2', items={'PCG', 'PBiCG', 'PBiCGStab'}, default='PBiCG')

# Create Key_C
key1 = Key_C('solver', prop1, prop2)

# Build tree
head = Node_C("test_head", None, None)
child1 = Node_C('test_child', head, None)
child2 = Node_C('test_child2', child1, None, key1)
child3 = Node_C('test_child3', child1, None, key1)

# Display tree
show_tree(head)
```

## Example Output (Tree Structure)
```
test_head
|--test_child
|   |--test_child2
|   |   {
|   |      solver : PCG, PBiCG,
|   |   }
|   |--test_child3
|   |   {
|   |      solver : PCG, PBiCG,
|   |   }
```

## Complete Example:

```python
from pyvnt import *

head = Node_C('fvSolutions')
sl = Node_C('solvers', parent = head)

s = Key_C('solver', Enm_P('val1', items={'PCG', 'PBiCG', 'PBiCGStab'}, default='PCG'))
pc = Key_C('preconditioner', Enm_P('val1', items={'DIC', 'DILU', 'FDIC'}, default='DIC'))
tol = Key_C('tolerance', Flt_P('val1', minimum=0, maximum=1000, default=1e-06))
rt = Key_C('relTol', Flt_P('val1', minimum=0, maximum=100, default=0.05))

p = Node_C('p', sl, None, pc, s, tol, rt)
relTol2 = Key_C('relTol', Flt_P('val1', minimum=0, maximum=100, default=0))
pf = Node_C('pFinal', sl, None, relTol2)

sol2 = Key_C('solver', Enm_P('val1', items={'smoothSolver'}, default='smoothSolver'))
sm = Key_C('smoother', Enm_P('val1', items={'symGaussSeidel', 'gaussSeidel'}, default = 'symGaussSeidel'))
tol2 = Key_C('tolerance', Flt_P('val1', minimum=0, maximum=1000, default=1e-05))
relTol3 = Key_C('relTol', Flt_P('val1', minimum=0, maximum=100, default=0))

u = Node_C('U', sl, None, sol2, sm, tol2, relTol3)

ncorr = Key_C('nCorrectors', Int_P('int_prop_1', minimum=0, maximum=100, default=2))
nnoc = Key_C('nNonOrthogonalCorrectors', Int_P('int_prop_2', minimum=0, maximum=100, default=0))
prc = Key_C('pRefCell', Int_P('int_prop_3', minimum=0, maximum=100, default=0))
prv = Key_C('pRefValue', Int_P('int_prop_4', minimum=0, maximum=100, default=0))

piso = Node_C('PISO', head, None, ncorr, nnoc, prc, prv)

show_tree(head)
```

### Output
```
fvSolutions
├── solvers
│   ├── p
│   │   { 
│   │      preconditioner : DIC, 
│   │      solver : PCG, 
│   │      tolerance : 1e-06, 
│   │      relTol : 0.05, 
│   │   }
│   ├── pFinal
│   │   { 
│   │      relTol : 0, 
│   │   }
│   └── U
│       { 
│          solver : smoothSolver, 
│          smoother : symGaussSeidel, 
│          tolerance : 1e-05, 
│          relTol : 0, 
│       }
└── PISO
    { 
       nCorrectors : 2, 
       nNonOrthogonalCorrectors : 0, 
       pRefCell : 0, 
       pRefValue : 0, 
    }
```

## Important Note on Node_C Construction and Leaf Node Errors

**Common mistake:**  
The way you call the `Node_C` constructor determines whether a node is treated as a leaf (cannot have children) or not.

### Example from `testfile.py` (Correct)
```python
p = Node_C('p', sl, None, pc, s, tol, rt)
```
- `'p'` is the node name.
- `sl` is the parent node.
- `None` is explicitly passed as the third argument (children).
- The rest (`pc, s, tol, rt`) are data objects.

**Why this works:**  
Passing `None` for the children argument tells the `Node_C` class that this node is **not a leaf** and can have children added later. The remaining arguments are treated as data.

---

### Example from `main.py` (Potential Issue)
```python
solvers_node = Node_C("solvers", parent=fv_solution_root)
```
- Here, only the `parent` is specified using a keyword argument.
- If the constructor does not receive the children argument (or receives it as something other than `None` or a list), it may **default to making the node a leaf**.

---

### Why the difference?
- The `Node_C` constructor likely checks if the third argument (children) is `None` or a list.
    - If `None`, the node can have children added later.
    - If omitted or passed incorrectly, it might default to a leaf node.
- This is why in `testfile.py`, the node is not a leaf, but in `main.py`, it may be.

---

### Recommendation

**Always pass `None` as the third argument to the `Node_C` constructor if you want the node to be able to have children later.**  
This matches the intended usage and avoids the `LeafNodeError`.

**Example fix for main.py:**
```python
solvers_node = Node_C("solvers", fv_solution_root, None)
```

**IMPORTANT**
add_data() only takes 3 positional arguments, never give more than 3.

## Class Name Mapping (Old vs New Syntax)

| Old Syntax | New Syntax |
|------------|------------|
| `Foam` | `Node_C` |
| `KeyData` | `Key_C` |
| `PropertyInt` | `Int_P` |
| `PropertyFloat` | `Flt_P` |
| `PropertyString` | `Str_P` |
| `EnumProp` | `Enm_P` |
| `showTree` | `show_tree` |

**Summary:**  
- In `testfile.py`, passing `None` for children tells `Node_C` the node is not a leaf.
- In `main.py`, omitting the children argument may cause the node to be a leaf.
- **Check the `Node_C` class constructor signature and always follow the correct argument order and usage.**