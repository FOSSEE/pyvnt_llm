# OpenFOAM pyvnt Bidirectional Converter

An AI-powered tool for seamless conversion between OpenFOAM case files and pyvnt Python code structures. This converter uses Google's Gemini AI to intelligently translate between these two formats with high accuracy and proper formatting.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [File Structure](#file-structure)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

- **Bidirectional Conversion**: Convert OpenFOAM case files to pyvnt Python code and vice versa
- **AI-Powered**: Uses Google Gemini 2.0 Flash for intelligent, context-aware conversions
- **Programmatic API**: `read()` function for direct integration into Python scripts
- **Module Management**: Save and load converted structures as reusable Python modules
- **Organized Output**: Automatically creates structured directory hierarchy
- **Interactive CLI**: User-friendly command-line interface with animated loading indicators
- **Context-Aware**: Supports external context files for improved conversion accuracy
- **Code Validation**: Automatic syntax and structure validation of generated code
- **Direct Execution**: Execute generated code directly in isolated namespace

## Prerequisites

Before running the converter, ensure you have:

1. **Python 3.7+** installed
2. **Google Gemini API Key** (free tier available)
3. **Required Python packages**:
   ```bash
   pip install google-generativeai pathlib
   ```
4. **pyvnt library** installed and accessible

## Installation

1. **Install required dependencies**:
   ```bash
   pip install google-generativeai
   ```

2. **Set up your Gemini API key**:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

3. **Ensure pyvnt is available** in your Python environment

## Configuration

### Getting Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and set it as an environment variable:

   **Linux/Mac:**
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

   **Windows:**
   ```cmd
   set GEMINI_API_KEY=your_api_key_here
   ```

### Optional Context Files

For enhanced conversion accuracy, you can create context files:

- `context_case_to_trees.md` - For OpenFOAM to pyvnt conversion
- `context_trees_to_case.md` - For pyvnt to OpenFOAM conversion

Place these files in the same directory as the converter script.

## Usage

### Interactive Mode

```bash
python3 converter.py
```

The converter presents four options:

1. **OpenFOAM Case Files to pyvnt Python Code**
2. **pyvnt Python Code to OpenFOAM Case Files**
3. **Use read() function (programmatic demonstration)**
4. **Exit**

### Programmatic Usage

#### Basic File Conversion

```python
from converter import read

# Convert OpenFOAM case file to pyvnt tree
root_tree = read('path/to/your/case_file.txt')

# The root_tree is now a pyvnt Node_C object ready for use
print(f"Root node: {root_tree.name}")
```

#### Advanced Options

```python
# Convert with module saving
root_tree = read(
    'fvSolution', 
    save_module=True,
    module_name='my_custom_solver_config',
    verbose=True,
    use_tree_modules=True
)

# Load a previously saved module
from converter import load_saved_module
root_tree = load_saved_module('my_custom_solver_config', from_tree_modules=True)

# List available saved modules
from converter import list_saved_modules
modules = list_saved_modules(from_tree_modules=True)
print("Available modules:", modules)
```

## API Reference

### read(file_path, save_module=True, module_name=None, verbose=False, use_tree_modules=True)

Convert an OpenFOAM case file to a pyvnt tree structure.

**Parameters:**
- `file_path` (str): Path to the OpenFOAM case file
- `save_module` (bool): Whether to save the generated code as a reusable module
- `module_name` (str): Custom name for the saved module (optional)
- `verbose` (bool): Whether to print detailed progress information
- `use_tree_modules` (bool): Whether to save modules in tree_modules/ directory

**Returns:**
- `Node_C`: The root node of the constructed pyvnt tree

**Raises:**
- `FileNotFoundError`: If the input file doesn't exist
- `RuntimeError`: If conversion or execution fails

### load_saved_module(module_name, from_tree_modules=True, verbose=False)

Load a previously saved module and return its root tree.

**Parameters:**
- `module_name` (str): Name of the module to load (without .py extension)
- `from_tree_modules` (bool): Whether to load from tree_modules/ or pyvnt_package/
- `verbose` (bool): Whether to print progress information

**Returns:**
- `Node_C`: The root node of the loaded pyvnt tree

### list_saved_modules(from_tree_modules=True)

List all saved modules in the specified directory.

**Parameters:**
- `from_tree_modules` (bool): Whether to list from tree_modules/ or pyvnt_package/

**Returns:**
- `list`: List of module names (without .py extension)

## File Structure

After running the converter, your directory structure will be:

```
converter/pyvnt_package/
├── converter.py                           # Main converter script
├── context_case_to_trees.md              # Optional context file
├── context_trees_to_case.md              # Optional context file
└── converter/                             # Generated output directory
    ├── generated_text_files/              # Generated OpenFOAM files
    │   ├── openfoam_case_20240115_143155.txt
    │   └── custom_case.txt
    └── pyvnt_package/                     # Generated Python files
        ├── pyvnt_code_20240115_143022.py
        ├── custom_filename.py
        └── tree_modules/                  # Saved module directory
            ├── converted_fvSolution_20240115_143022.py
            └── my_custom_solver_config.py
```

## Examples

### Basic Programmatic Usage

```python
from converter import read

# Convert a simple case file
try:
    root = read('system/fvSolution', verbose=True)
    print(f"Successfully converted! Root node: {root.name}")
    
    # Access the tree structure
    for child in root.children:
        print(f"Child node: {child.name}")
        
except FileNotFoundError:
    print("File not found")
except RuntimeError as e:
    print(f"Conversion failed: {e}")
```

### Working with Saved Modules

```python
from converter import read, load_saved_module, list_saved_modules

# Save a conversion as a reusable module
root = read('controlDict', 
           save_module=True,
           module_name='control_dict_config',
           use_tree_modules=True)

# Later, load the saved module
loaded_root = load_saved_module('control_dict_config')

# List all available modules
available = list_saved_modules()
print("Saved modules:", available)
```

### OpenFOAM Case File Example

**Input (fvSolution):**
```
solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0.05;
    }
    
    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

PISO
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}
```

**Generated pyvnt Code:**
```python
from pyvnt import *

# Create root node
root = Node_C('root', None, None)

# Solvers configuration
solvers = Node_C('solvers', root, None)

# Pressure solver
p = Node_C('p', solvers, None,
    Key_C('solver', Enm_P('solver', items={'PCG', 'PBiCG', 'PBiCGStab'}, default='PCG')),
    Key_C('preconditioner', Enm_P('preconditioner', items={'DIC', 'DILU', 'diagonal'}, default='DIC')),
    Key_C('tolerance', Flt_P('tolerance', min_val=1e-12, max_val=1e-1, default=1e-06)),
    Key_C('relTol', Flt_P('relTol', min_val=0.0, max_val=1.0, default=0.05))
)

# Velocity solver
U = Node_C('U', solvers, None,
    Key_C('solver', Enm_P('solver', items={'smoothSolver', 'PBiCG'}, default='smoothSolver')),
    Key_C('smoother', Enm_P('smoother', items={'symGaussSeidel', 'GaussSeidel'}, default='symGaussSeidel')),
    Key_C('tolerance', Flt_P('tolerance', min_val=1e-12, max_val=1e-1, default=1e-05)),
    Key_C('relTol', Flt_P('relTol', min_val=0.0, max_val=1.0, default=0.1))
)

# PISO algorithm settings
PISO = Node_C('PISO', root, None,
    Key_C('nCorrectors', Int_P('nCorrectors', min_val=1, max_val=10, default=2)),
    Key_C('nNonOrthogonalCorrectors', Int_P('nNonOrthogonalCorrectors', min_val=0, max_val=5, default=0)),
    Key_C('pRefCell', Int_P('pRefCell', min_val=0, default=0)),
    Key_C('pRefValue', Flt_P('pRefValue', default=0.0))
)

# Display the tree
show_tree(root)
```

## Troubleshooting

### Common Issues

#### API Key Error
```
Error: GEMINI_API_KEY environment variable not set
```
**Solution**: Set your Gemini API key as an environment variable.

#### File Not Found
```
FileNotFoundError: File not found: path/to/file
```
**Solution**: Verify the file path exists and is accessible.

#### Conversion Failures
```
RuntimeError: Failed to execute generated code
```
**Solution**: 
- Ensure pyvnt library is properly installed
- Check that the input OpenFOAM file has valid syntax
- Try with verbose=True to see detailed error information

#### Module Loading Issues
```
ModuleNotFoundError: No module named 'pyvnt'
```
**Solution**: 
- Ensure pyvnt is installed in your Python environment
- Check that the pyvnt_package directory is in the correct location

### Code Validation

The converter includes automatic validation:
- Syntax checking of generated Python code
- Verification of required imports and function calls
- Structure validation for pyvnt compatibility

### Getting Help

If you encounter issues:

1. **Use verbose mode**: Set `verbose=True` to see detailed progress
2. **Check file permissions**: Ensure you can read input files and write to output directories
3. **Validate input format**: Ensure your OpenFOAM files follow proper dictionary syntax
4. **Verify API connectivity**: Check your internet connection and API key validity

## Tips for Best Results

### For OpenFOAM to pyvnt Conversion

- Use complete case file sections rather than fragments
- Ensure proper OpenFOAM dictionary syntax with braces and semicolons
- Include proper indentation in your input files
- Use standard OpenFOAM keywords and values when possible

### For pyvnt to OpenFOAM Conversion

- Use complete pyvnt tree structures with proper Node_C hierarchy
- Include all necessary imports at the top of your code
- Follow pyvnt naming conventions and class structure
- Ensure all Key_C objects contain valid ValueProperty instances

### Module Management

- Use descriptive names for saved modules
- Organize modules in the tree_modules directory for better structure
- Regularly clean up unused modules to maintain organization
- Use the list_saved_modules() function to track available conversions

## Contributing

This converter is designed to be extensible. You can:

1. **Add custom context files** for domain-specific conversions
2. **Modify the embedded contexts** for better conversion accuracy
3. **Extend the property types** supported by the converter
4. **Add new output formats** or directory structures
5. **Enhance the module management system**
6. **Improve error handling and validation**

## License

This tool is provided as-is for educational and research purposes. Please ensure you comply with Google's Gemini API terms of service when using this converter.