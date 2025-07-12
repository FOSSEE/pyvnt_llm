# OpenFOAM ↔ pyvnt Bidirectional Converter

An AI-powered tool for seamless conversion between OpenFOAM case files and pyvnt Python code structures. This converter uses Google's Gemini AI to intelligently translate between these two formats with high accuracy and proper formatting.

## Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [File Structure](#-file-structure)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## Features

- **🔄 Bidirectional Conversion**: Convert OpenFOAM case files to pyvnt Python code and vice versa
- **🤖 AI-Powered**: Uses Google Gemini 2.0 Flash for intelligent, context-aware conversions
- **📁 Organized Output**: Automatically saves Python files to `pyvnt_package/` directory
- **💻 Interactive CLI**: User-friendly command-line interface with animated loading indicators
- **🎯 Context-Aware**: Supports external context files for improved conversion accuracy
- **🛡️ Error Handling**: Comprehensive error handling with graceful fallbacks
- **📝 Automatic Formatting**: Proper code formatting and structure validation

## Prerequisites

Before running the converter, ensure you have:

1. **Python 3.7+** installed
2. **Google Gemini API Key** (free tier available)
3. **Required Python packages**:
   ```bash
   pip install google-generativeai pathlib
   ```

## Installation

1. **Download the converter script**:
   ```bash
   # Save the script as converter.py
   ```

2. **Install required dependencies**:
   ```bash
   pip install google-generativeai
   ```

3. **Set up your Gemini API key**:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

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

- `context_case_to_trees.md` - For OpenFOAM → pyvnt conversion
- `context_trees_to_case.md` - For pyvnt → OpenFOAM conversion

Place these files in the same directory as the converter script.

## Usage

### Running the Converter

```bash
python3 converter.py
```

### Interactive Menu

The converter will present you with three options:

```
🚀 BIDIRECTIONAL CONVERTER: OpenFOAM ↔ pyvnt (AI-Powered)
======================================================================

Select conversion mode:
1. 📄 OpenFOAM Case Files → 🐍 pyvnt Python Code
2. 🐍 pyvnt Python Code → 📄 OpenFOAM Case Files
3. 🚪 Exit
```

### Step-by-Step Process

#### Option 1: OpenFOAM → pyvnt

1. **Select Option 1**
2. **Paste your OpenFOAM case file content** when prompted
3. **Type 'END'** on a new line to finish input
4. **Wait for AI processing** (animated loading indicator will show)
5. **Review the generated pyvnt code**
6. **Choose to save** the result to a file
7. **Provide a filename** or use the default timestamp-based name
8. **File saved** to `pyvnt_package/` directory

#### Option 2: pyvnt → OpenFOAM

1. **Select Option 2**
2. **Paste your pyvnt Python code** when prompted
3. **Type 'END'** on a new line to finish input
4. **Wait for AI processing**
5. **Review the generated OpenFOAM case file**
6. **Choose to save** the result to a file
7. **File saved** to `generated_text_files/` directory

### Input Methods

You can provide input in two ways:

1. **Interactive paste**: Copy and paste your content, then type 'END'
2. **EOF signal**: Use Ctrl+D (Linux/Mac) or Ctrl+Z+Enter (Windows) to finish

## File Structure

After running the converter, your directory structure will look like:

```
your_project/
├── converter.py                    # Main converter script
├── context_case_to_trees.md       # Optional context file
├── context_trees_to_case.md       # Optional context file
├── pyvnt_package/                 # Generated Python files
│   ├── pyvnt_code_20240115_143022.py
│   └── custom_filename.py
└── generated_text_files/          # Generated OpenFOAM files
    ├── openfoam_case_20240115_143155.txt
    └── custom_case.txt
```

## Examples

### OpenFOAM Case File Example

**Input:**
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
```

**Generated pyvnt Code:**
```python
from pyvnt import Node_C, Key_C, Int_P, Flt_P, Str_P, Enm_P, show_tree

# Root node
root = Node_C('root', None, None)

# Solvers node
solvers = Node_C('solvers', root, None)

# Pressure solver configuration
p = Node_C('p', solvers, None,
    Key_C('solver', Enm_P('solver', items={'PCG', 'PBiCG', 'PBiCGStab'}, default='PCG')),
    Key_C('preconditioner', Enm_P('preconditioner', items={'DIC', 'DILU', 'diagonal'}, default='DIC')),
    Key_C('tolerance', Flt_P('tolerance', min_val=1e-12, max_val=1e-1, default=1e-06)),
    Key_C('relTol', Flt_P('relTol', min_val=0.0, max_val=1.0, default=0.05))
)

# Velocity solver configuration
U = Node_C('U', solvers, None,
    Key_C('solver', Enm_P('solver', items={'smoothSolver', 'PBiCG', 'PBiCGStab'}, default='smoothSolver')),
    Key_C('smoother', Enm_P('smoother', items={'symGaussSeidel', 'GaussSeidel', 'DIC'}, default='symGaussSeidel')),
    Key_C('tolerance', Flt_P('tolerance', min_val=1e-12, max_val=1e-1, default=1e-05)),
    Key_C('relTol', Flt_P('relTol', min_val=0.0, max_val=1.0, default=0.1))
)

# Display the tree structure
show_tree(root)
```

### pyvnt to OpenFOAM Conversion

The above pyvnt code would convert back to properly formatted OpenFOAM case file format.

## 🔧 Troubleshooting

### Common Issues

#### 1. API Key Error
```
Error: GEMINI_API_KEY environment variable not set
```
**Solution**: Set your Gemini API key as an environment variable.

#### 2. Network/API Errors
```
❌ Error generating code: [API Error]
```
**Solution**: 
- Check your internet connection
- Verify your API key is valid
- Ensure you haven't exceeded API rate limits

#### 3. Directory Creation Errors
```
❌ Error creating directory: [Permission Error]
```
**Solution**: 
- Ensure you have write permissions in the current directory
- Run the script from a directory where you have full access

#### 4. Invalid Input Format
**Solution**: 
- Ensure your OpenFOAM case file has proper syntax
- For pyvnt code, verify it follows the correct class structure

### Getting Help

If you encounter issues:

1. **Check the error message** - most issues are clearly indicated
2. **Verify your API key** - ensure it's correctly set and valid
3. **Check file permissions** - ensure you can write to the current directory
4. **Validate input format** - ensure your input follows the expected structure

## 📋 Tips for Best Results

### For OpenFOAM → pyvnt Conversion

- **Use complete case file sections** rather than fragments
- **Include proper OpenFOAM dictionary syntax** with braces and semicolons
- **Ensure proper indentation** in your input

### For pyvnt → OpenFOAM Conversion

- **Use complete pyvnt tree structures** with proper Node_C hierarchy
- **Include all necessary imports** at the top of your code
- **Follow pyvnt naming conventions** and class structure

## 🤝 Contributing

This converter is designed to be extensible. You can:

1. **Add custom context files** for domain-specific conversions
2. **Modify the embedded contexts** for better conversion accuracy
3. **Extend the property types** supported by the converter
4. **Add new output formats** or directory structures

## 📄 License

This tool is provided as-is for educational and research purposes. Please ensure you comply with Google's Gemini API terms of service when using this converter.

---
