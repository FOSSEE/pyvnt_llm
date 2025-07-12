# pyvnt to OpenFOAM Case File Converter Context

## Overview
This context describes how to convert pyvnt tree structures back to OpenFOAM case file format. The conversion process involves traversing the Node_C tree structure and generating properly formatted OpenFOAM dictionary syntax.

## OpenFOAM Dictionary Format Rules

### 1. Basic Structure
```
dictionaryName
{
    key1    value1;
    key2    value2;
    
    subDict1
    {
        nestedKey1    nestedValue1;
        nestedKey2    nestedValue2;
    }
    
    subDict2
    {
        // more nested content
    }
}
```

### 2. Formatting Rules
- Dictionary names are followed by opening brace `{` on the same line or next line
- Key-value pairs are separated by whitespace and terminated with semicolon `;`
- Nested dictionaries follow the same pattern
- Proper indentation (typically 4 spaces per level)
- Comments can be added with `//` or `/* */`

### 3. Value Types in OpenFOAM
- **Strings**: Can be quoted or unquoted (e.g., `PCG` or `"PCG"`)
- **Numbers**: Integer or floating point (e.g., `1`, `1.0`, `1e-06`)
- **Booleans**: `true`, `false`, `yes`, `no`, `on`, `off`
- **Lists**: `(value1 value2 value3)` or `[value1 value2 value3]`
- **Vectors**: `(x y z)`

## pyvnt to OpenFOAM Conversion Logic

### 1. Tree Traversal
- Start from root Node_C
- Recursively traverse all children
- Convert each Node_C to OpenFOAM dictionary format

### 2. Node_C Conversion
Each Node_C becomes an OpenFOAM dictionary:
```python
# pyvnt Node_C with name "solvers"
solvers_node = Node_C("solvers", parent, None, key1, key2)

# Converts to OpenFOAM:
solvers
{
    key1_name    key1_value;
    key2_name    key2_value;
}
```

### 3. Key_C Conversion
Each Key_C becomes a key-value pair:
```python
# pyvnt Key_C
tolerance = Key_C('tolerance', Flt_P('val1', minimum=0, maximum=1000, default=1e-06))

# Converts to OpenFOAM:
tolerance    1e-06;
```

### 4. Property Value Extraction
- **Int_P**: Extract integer value
- **Flt_P**: Extract float value (format appropriately, e.g., scientific notation)
- **Str_P**: Extract string value
- **Enm_P**: Extract selected enum value

## Example Conversion

### Input pyvnt Tree:
```python
from pyvnt import *

head = Node_C('fvSolutions')
sl = Node_C('solvers', parent=head)

s = Key_C('solver', Enm_P('val1', items={'PCG', 'PBiCG', 'PBiCGStab'}, default='PCG'))
tol = Key_C('tolerance', Flt_P('val1', minimum=0, maximum=1000, default=1e-06))
p = Node_C('p', sl, None, s, tol)

ncorr = Key_C('nCorrectors', Int_P('int_prop_1', minimum=0, maximum=100, default=2))
piso = Node_C('PISO', head, None, ncorr)
```

### Output OpenFOAM Format:
```
fvSolutions
{
    solvers
    {
        p
        {
            solver       PCG;
            tolerance    1e-06;
        }
    }
    
    PISO
    {
        nCorrectors    2;
    }
}
```

## Implementation Guidelines

### 1. Recursive Tree Traversal
```python
def convert_node_to_openfoam(node, indent_level=0):
    indent = "    " * indent_level
    lines = []
    
    # Add node name and opening brace
    lines.append(f"{indent}{node.name}")
    lines.append(f"{indent}{{")
    
    # Convert Key_C objects to key-value pairs
    for key_data in node.data:
        key_line = convert_key_to_openfoam(key_data, indent_level + 1)
        lines.append(key_line)
    
    # Recursively convert children
    for child in node.children:
        child_lines = convert_node_to_openfoam(child, indent_level + 1)
        lines.extend(child_lines)
    
    # Add closing brace
    lines.append(f"{indent}}}")
    
    return lines
```

### 2. Key_C to OpenFOAM Conversion
```python
def convert_key_to_openfoam(key_data, indent_level=0):
    indent = "    " * indent_level
    
    # Extract value from the ValueProperty
    value = extract_property_value(key_data)
    
    # Format based on value type
    formatted_value = format_openfoam_value(value)
    
    return f"{indent}{key_data.name}    {formatted_value};"
```

### 3. Value Formatting
```python
def format_openfoam_value(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        if value == 0:
            return "0"
        elif abs(value) < 1e-4 or abs(value) > 1e4:
            return f"{value:.6e}"
        else:
            return str(value)
    else:
        return str(value)
```

## Error Handling and Edge Cases

### 1. Empty Nodes
- Nodes with no data and no children should still generate dictionary structure
- Add comment indicating empty dictionary if needed

### 2. Special Characters
- Handle special characters in names and values
- Quote strings if they contain spaces or special characters

### 3. File Headers
- Add appropriate OpenFOAM file headers (FoamFile dictionary)
- Include version, format, class, object, etc.

### 4. Value Validation
- Ensure extracted values are valid OpenFOAM syntax
- Handle edge cases like infinity, NaN, etc.

## Complete Example Function Structure

```python
def pyvnt_to_openfoam(root_node, add_foam_header=True):
    """
    Convert pyvnt tree to OpenFOAM case file format
    
    Args:
        root_node: Root Node_C of the pyvnt tree
        add_foam_header: Whether to add FoamFile header
    
    Returns:
        str: OpenFOAM formatted case file content
    """
    lines = []
    
    if add_foam_header:
        lines.extend(generate_foam_header(root_node.name))
    
    # Convert the tree
    tree_lines = convert_node_to_openfoam(root_node)
    lines.extend(tree_lines)
    
    return '\n'.join(lines)
```

## Usage Notes

### 1. Accessing Node Data
- Use `node.data` to access list of Key_C objects
- Use `node.children` to access child nodes
- Use `node.name` for the dictionary name

### 2. Extracting Property Values
- Each Key_C contains ValueProperty objects
- Use appropriate methods to extract current values
- Handle default values appropriately

### 3. Indentation and Formatting
- Maintain consistent 4-space indentation
- Align values for readability
- Add blank lines between major sections

This context provides the foundation for implementing the pyvnt to OpenFOAM conversion functionality.