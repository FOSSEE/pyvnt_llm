#!/usr/bin/env python3
"""
Enhanced Bidirectional Converter: Case Files ↔ pyvnt Python Code
Now includes read() function for programmatic file conversion!
"""
import os
import sys
import ast
import traceback
import re
import threading
import time
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
import importlib.util
import types

class LoadingIndicator:
    """A simple loading indicator with animated dots"""
    def __init__(self, message="Loading"):
        self.message = message
        self.is_running = False
        self.thread = None
    
    def start(self):
        """Start the loading indicator"""
        self.is_running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the loading indicator"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        # Clear the line
        print("\r" + " " * (len(self.message) + 10), end="\r")
    
    def _animate(self):
        """Animate the loading dots"""
        dots = 0
        while self.is_running:
            dots_str = "." * (dots % 4)
            print(f"\r{self.message}{dots_str:<3}", end="", flush=True)
            time.sleep(0.5)
            dots += 1

class ConversionMode:
    CASE_TO_PYVNT = "case_to_pyvnt"
    PYVNT_TO_CASE = "pyvnt_to_case"

class RootNodeExtractor:
    """Extract root node variable from generated pyvnt code"""
    
    @staticmethod
    def find_root_variable(code_content):
        """
        Find the root node variable by analyzing the AST
        Root node is typically: Node_C('name', None, None, ...)
        """
        try:
            tree = ast.parse(code_content)
            root_candidates = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    # Look for assignments that create Node_C with parent=None
                    if isinstance(node.value, ast.Call):
                        if (hasattr(node.value.func, 'id') and 
                            node.value.func.id == 'Node_C' and
                            len(node.value.args) >= 2):
                            
                            # Check if second argument (parent) is None
                            second_arg = node.value.args[1]
                            if isinstance(second_arg, ast.Constant) and second_arg.value is None:
                                if node.targets and isinstance(node.targets[0], ast.Name):
                                    root_candidates.append(node.targets[0].id)
            
            # Return the first root candidate (there should typically be only one)
            return root_candidates[0] if root_candidates else None
            
        except Exception as e:
            print(f"Warning: Could not analyze code structure: {e}")
            return None
    
    @staticmethod
    def extract_from_show_tree(code_content):
        """
        Fallback method: extract root variable from show_tree() call
        """
        try:
            # Look for show_tree(variable_name) pattern
            pattern = r'show_tree\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)'
            matches = re.findall(pattern, code_content)
            return matches[0] if matches else None
        except Exception:
            return None

def create_output_directories():
    """Create output directories if they don't exist"""
    directories = {
        'python': Path("pyvnt_package"),
        'text': Path("generated_text_files"),
        'modules': Path("pyvnt_package")  # New directory for generated modules
    }
    
    for dir_type, directory in directories.items():
        try:
            directory.mkdir(exist_ok=True)
            if dir_type != 'modules':  # Don't print for internal modules directory
                print(f"✅ Directory ready: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")
            sys.exit(1)
    
    return directories

def setup_gemini():
    """Setup Gemini API client"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key: export GEMINI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    return model

def load_context(mode):
    """Load the appropriate context based on conversion mode"""
    if mode == ConversionMode.CASE_TO_PYVNT:
        context_file = Path("context_case_to_trees.md")
        fallback_context = get_case_to_pyvnt_context()
    else:
        context_file = Path("context_trees_to_case.md")
        fallback_context = get_pyvnt_to_openfoam_context()
    
    if not context_file.exists():
        return fallback_context
    
    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return fallback_context

def get_case_to_pyvnt_context():
    """Embedded context for case file to pyvnt conversion - ENFORCES root variable name"""
    return """
# pyvnt: Class Structure and Example Usage Context

## Core Class Structure

### 1. ValueProperty (Abstract)
- Parent for all property classes (e.g., `Int_P`, `Flt_P`, `Enm_P`).
- Enforces interface for value properties used in Key_C.

### 2. Int_P, Flt_P, Str_P, Enm_P
- Store typed values with constraints (e.g., minimum/maximum/default for ints/floats, set of choices for enums).
- Example: `Enm_P('val1', items={'PCG', 'PBiCG', 'PBiCGStab'}, default='PCG')`
- Example: `Flt_P('val1', minimum=1e-12, maximum=1.0, default=1e-8)`
- Example: `Int_P('val1', minimum=0, maximum=10, default=2)`

### 3. Key_C
- Represents a dictionary-like node holding multiple ValueProperty instances.
- Enforces encapsulation: attributes are only set via constructor or methods.
- Example: `Key_C('solver', prop1, prop2)`

### 4. Node_C
- Tree node class (inherits from anytree's NodeMixin).
- Holds a name, parent, children, and a list of Key_C objects as data.
- Always pass `None` as the third argument for non-leaf nodes.
- Example: `Node_C('nodeName', parent, None, data1, data2)`

### 5. show_tree
- Utility to print the tree structure and Key_C at each node.

## CRITICAL REQUIREMENTS:
- Always start with: `from pyvnt import *`
- MUST create root node with variable name 'root': `root = Node_C('name', None, None)`
- End with: `show_tree(root)`
- The root variable MUST be named 'root' - no other name is acceptable
- Use 'minimum' and 'maximum' parameters for Flt_P and Int_P, NOT 'min' and 'max'
"""

def get_pyvnt_to_openfoam_context():
    """Enhanced embedded context for pyvnt to OpenFOAM conversion"""
    return """
# pyvnt to OpenFOAM Case File Converter Context

You are an expert in converting pyvnt Python tree structures to OpenFOAM case file format.

## Key Conversion Rules:

1. **Node_C Structure**: Each Node_C represents a dictionary/subdictionary in OpenFOAM format
2. **Key_C to Properties**: Each Key_C contains ValueProperty instances that become key-value pairs
3. **Property Value Extraction**: Extract actual values from .value or .default attributes
4. **OpenFOAM Formatting**: Use proper dictionary syntax with braces, semicolons, and 4-space indentation

## Conversion Process:
1. Traverse the Node_C tree recursively
2. For each Node_C: create OpenFOAM dictionary with proper braces
3. For each Key_C in node.data: extract property values and format as key-value pairs
4. Maintain hierarchical structure through proper nesting

## Example:
```python
# pyvnt structure
p_node = Node_C('p', parent, None, 
    Key_C('solver', Enm_P('val1', default='PCG')),
    Key_C('tolerance', Flt_P('val1', minimum=1e-12, maximum=1.0, default=1e-06))
)

# OpenFOAM output
p
{
    solver       PCG;
    tolerance    1e-06;
}
```

Extract ALL property values from every Key_C object in the tree structure.
"""

def create_case_to_pyvnt_prompt(context, case_file_content):
    """Create prompt for case file to pyvnt conversion - ENFORCES root variable name"""
    return f"""
You are an expert in OpenFOAM case file structure and the pyvnt Python library. 

Here is the context about pyvnt library structure and usage:
{context}

Now, please convert the following OpenFOAM case file content into equivalent pyvnt Python code:

```
{case_file_content}
```

Requirements:
1. Generate clean, working Python code using the pyvnt library
2. Follow the exact patterns shown in the context examples
3. Use appropriate property types (Int_P, Flt_P, Str_P, Enm_P)
4. Set reasonable constraints (minimum/maximum values) and defaults based on typical OpenFOAM values
5. Always use 'minimum' and 'maximum' parameters for Flt_P and Int_P, NOT 'min' and 'max'
6. Always pass `None` as the third argument to Node_C constructor for non-leaf nodes
7. Include the final `show_tree(root)` call to display the structure
8. Add appropriate comments explaining the structure
9. MUST start with `from pyvnt import *`
10. CRITICAL: The root node variable MUST be named 'root' - example: `root = Node_C('fvSolutions', None, None)`

Return ONLY the Python code, no explanations or markdown formatting.
"""

def validate_generated_code(code_content):
    """
    Validate the generated pyvnt code before execution
    """
    try:
        # Try to parse the code
        ast.parse(code_content)
        
        # Check for required imports
        if 'from pyvnt import *' not in code_content and 'import pyvnt' not in code_content:
            return False, "Missing pyvnt import statement"
        
        # Check for Node_C usage
        if 'Node_C(' not in code_content:
            return False, "No Node_C objects found"
        
        # Check for show_tree call
        if 'show_tree(' not in code_content:
            return False, "Missing show_tree call"
        
        return True, "Code validation successful"
        
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"

def execute_pyvnt_code(code_content):
    """
    Execute pyvnt code in an isolated namespace and return the root node
    """
    try:
        # Create isolated namespace
        namespace = {}
        
        # Add necessary imports to namespace
        exec("from pyvnt import *", namespace)
        
        # Execute the generated code
        exec(code_content, namespace)
        
        # Extract root node variable
        root_var_name = RootNodeExtractor.find_root_variable(code_content)
        
        if not root_var_name:
            # Fallback: try to extract from show_tree call
            root_var_name = RootNodeExtractor.extract_from_show_tree(code_content)
        
        if not root_var_name:
            # Last resort: look for Node_C objects with parent=None
            for var_name, obj in namespace.items():
                if (hasattr(obj, 'parent') and obj.parent is None and 
                    hasattr(obj, 'name') and not var_name.startswith('_')):
                    root_var_name = var_name
                    break
        
        if root_var_name and root_var_name in namespace:
            return namespace[root_var_name], root_var_name
        else:
            raise ValueError("Could not identify root node variable")
            
    except Exception as e:
        raise RuntimeError(f"Failed to execute pyvnt code: {e}")

def save_as_module(code_content, module_name, directories):
    """
    Save the generated code as a reusable module
    """
    try:
        module_path = directories['modules'] / f"{module_name}.py"
        
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        
        return str(module_path)
    except Exception as e:
        print(f"Warning: Could not save module: {e}")
        return None

def case_to_pyvnt_conversion(model, context, case_file_content):
    """Convert OpenFOAM case file to pyvnt code using Gemini"""
    prompt = create_case_to_pyvnt_prompt(context, case_file_content)
    
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Clean up markdown formatting if present
        if result.startswith('```'):
            lines = result.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            result = '\n'.join(lines)
        
        return result
    except Exception as e:
        raise RuntimeError(f"AI conversion failed: {e}")
    
def execute_generated_code_directly(generated_code, pyvnt_package_path=None):
    """
    Execute the generated code directly and return the root variable
    """
    import sys
    from pathlib import Path
    
    # Add the pyvnt_package directory to Python path so it can find pyvnt
    if pyvnt_package_path is None:
        pyvnt_package_path = str(Path("pyvnt_package").absolute())
    
    path_added = False
    
    try:
        if pyvnt_package_path not in sys.path:
            sys.path.insert(0, pyvnt_package_path)
            path_added = True
        
        # Create a local namespace for execution
        local_namespace = {}
        global_namespace = globals().copy()
        
        # Execute the generated code
        exec(generated_code, global_namespace, local_namespace)
        
        # Get the root variable
        if 'root' in local_namespace:
            return local_namespace['root']
        else:
            raise AttributeError("Generated code does not create a 'root' variable")
            
    except Exception as e:
        raise RuntimeError(f"Failed to execute generated code: {e}")
    finally:
        # Clean up sys.path
        if path_added and pyvnt_package_path in sys.path:
            sys.path.remove(pyvnt_package_path)


def create_output_directories():
    """
    Create necessary output directories including tree_modules
    """
    from pathlib import Path
    
    directories = {
        'base': Path("converter"),
        'generated_files': Path("converter/generated_text_files"),
        'pyvnt_package': Path("converter/pyvnt_package"),
        'tree_modules': Path("converter/pyvnt_package/tree_modules"),  # Inside pyvnt_package
        'modules': Path("converter/pyvnt_package")  # Keep for backward compatibility
    }
    
    # Create all directories
    for dir_path in directories.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return directories


def read(file_path, save_module=True, module_name=None, verbose=False, use_tree_modules=True):
    """
    Read an OpenFOAM case file and convert it to a pyvnt tree structure.
    
    Args:
        file_path (str): Path to the OpenFOAM case file
        save_module (bool): Whether to save the generated code as a reusable module
        module_name (str): Custom name for the saved module (optional)
        verbose (bool): Whether to print detailed progress information
        use_tree_modules (bool): Whether to save modules in tree_modules/ directory
        
    Returns:
        Node_C: The root node of the constructed pyvnt tree
    
    Raises:
        FileNotFoundError: If the input file doesn't exist
        RuntimeError: If conversion or execution fails
    """
    
    # Validate input file
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if verbose:
        print(f"🔄 Reading file: {file_path}")
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            case_content = f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {e}")
    
    if not case_content.strip():
        raise ValueError("File is empty")
    
    # Setup components
    if verbose:
        print("🤖 Initializing AI converter...")
    
    model = setup_gemini()
    context = load_context(ConversionMode.CASE_TO_PYVNT)
    directories = create_output_directories()
    
    # Convert using AI
    if verbose:
        print("🔄 Converting to pyvnt code...")
        loader = LoadingIndicator("Converting")
        loader.start()
    
    try:
        generated_code = case_to_pyvnt_conversion(model, context, case_content)
        if verbose:
            loader.stop()
    except Exception as e:
        if verbose:
            loader.stop()
        raise e
    
    # Validate generated code
    is_valid, validation_msg = validate_generated_code(generated_code)
    if not is_valid:
        raise RuntimeError(f"Generated code validation failed: {validation_msg}")
    
    if verbose:
        print("✅ Code validation successful")
    
    # Execute the generated code directly
    if verbose:
        print("🔄 Executing generated code directly...")
    
    try:
        # Pass the pyvnt_package path to ensure the module can be found
        pyvnt_package_path = str(directories['pyvnt_package'].absolute())
        root_tree = execute_generated_code_directly(generated_code, pyvnt_package_path)
    except Exception as e:
        raise RuntimeError(f"Failed to execute generated code: {e}")
    
    # Optionally save the module file
    if save_module:
        # Generate module name if not provided
        if not module_name:
            module_name = f"converted_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Choose directory based on use_tree_modules flag
        if use_tree_modules:
            module_dir = directories['tree_modules']
            if verbose:
                print(f"📁 Saving to tree_modules/ directory...")
        else:
            module_dir = directories['modules']
            if verbose:
                print(f"📁 Saving to pyvnt_package/ directory...")
        
        module_path = module_dir / f"{module_name}.py"
        
        try:
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(generated_code)
            
            if verbose:
                print(f"💾 Module saved: {module_path}")
        except Exception as e:
            if verbose:
                print(f"⚠️ Failed to save module: {e}")
    
    if verbose:
        print(f"✅ Conversion completed! Root tree created successfully")
        print("🌳 Tree structure:")
        # Try to display the tree structure
        try:
            from pyvnt import show_tree
            show_tree(root_tree)
        except (ImportError, NameError):
            if verbose:
                print("show_tree function not available")
    
    return root_tree


def load_saved_module(module_name, from_tree_modules=True, verbose=False):
    """
    Load a previously saved module and return its root tree.
    
    Args:
        module_name (str): Name of the module to load (without .py extension)
        from_tree_modules (bool): Whether to load from tree_modules/ or pyvnt_package/
        verbose (bool): Whether to print progress information
        
    Returns:
        Node_C: The root node of the loaded pyvnt tree
    """
    from pathlib import Path
    import sys
    
    # Determine the correct directory
    if from_tree_modules:
        module_dir = Path("converter/pyvnt_package/tree_modules")
    else:
        module_dir = Path("converter/pyvnt_package")
    
    module_path = module_dir / f"{module_name}.py"
    
    if not module_path.exists():
        raise FileNotFoundError(f"Module not found: {module_path}")
    
    if verbose:
        print(f"📖 Loading module: {module_path}")
    
    # Read the module content
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            module_code = f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read module: {e}")
    
    # Execute the module code
    try:
        pyvnt_package_path = str(Path("converter/pyvnt_package").absolute())
        root_tree = execute_generated_code_directly(module_code, pyvnt_package_path)
        
        if verbose:
            print("✅ Module loaded successfully!")
        
        return root_tree
        
    except Exception as e:
        raise RuntimeError(f"Failed to execute module: {e}")


def list_saved_modules(from_tree_modules=True):
    """
    List all saved modules in the specified directory.
    
    Args:
        from_tree_modules (bool): Whether to list from tree_modules/ or pyvnt_package/
        
    Returns:
        list: List of module names (without .py extension)
    """
    from pathlib import Path
    
    if from_tree_modules:
        module_dir = Path("converter/pyvnt_package/tree_modules")
    else:
        module_dir = Path("converter/pyvnt_package")
    
    if not module_dir.exists():
        return []
    
    # Get all .py files that start with "converted_"
    modules = []
    for py_file in module_dir.glob("converted_*.py"):
        modules.append(py_file.stem)
    
    return sorted(modules)


# Legacy interactive functions (keeping for backward compatibility)

def get_conversion_mode():
    """Get conversion mode from user"""
    print("=" * 70)
    print("🚀 BIDIRECTIONAL CONVERTER: OpenFOAM ↔ pyvnt (AI-Powered)")
    print("=" * 70)
    print("\nSelect conversion mode:")
    print("1. 📄 OpenFOAM Case Files → 🐍 pyvnt Python Code")
    print("2. 🐍 pyvnt Python Code → 📄 OpenFOAM Case Files")
    print("3. 🔧 Use read() function (programmatic)")
    print("4. 🚪 Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            if choice == "1":
                return ConversionMode.CASE_TO_PYVNT
            elif choice == "2":
                return ConversionMode.PYVNT_TO_CASE
            elif choice == "3":
                return "PROGRAMMATIC"
            elif choice == "4":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1-4.")
        except KeyboardInterrupt:
            print("\n\n⚠️ Operation cancelled.")
            sys.exit(0)
        except EOFError:
            print("\n\n⚠️ Operation cancelled.")
            sys.exit(0)

def demonstrate_read_function():
    """Demonstrate the read() function usage"""
    print("\n" + "=" * 60)
    print("🔧 PROGRAMMATIC CONVERSION DEMO")
    print("=" * 60)
    
    file_path = input("Enter the path to your OpenFOAM case file: ").strip()
    
    try:
        print("\n🚀 Using read() function...")
        root_node, root_var_name = read(file_path, verbose=True)
        
        print(f"\n✅ Success! You can now use '{root_var_name}' as your pyvnt tree.")
        print(f"Root node type: {type(root_node)}")
        print(f"Root node name: {root_node.name}")
        
        # Show how to use it
        print(f"\n💡 Usage example:")
        print(f"   root_node, var_name = read('{file_path}')")
        print(f"   # Now you can use root_node in your code!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Keep other existing functions for backward compatibility
def get_input_content(mode):
    """Get input content based on conversion mode"""
    if mode == ConversionMode.CASE_TO_PYVNT:
        print("\n" + "=" * 60)
        print("📄 CASE FILE TO PYVNT CONVERTER")
        print("=" * 60)
        print("\n📝 Please paste your OpenFOAM case file content below.")
    else:
        print("\n" + "=" * 60)
        print("🐍 PYVNT TO CASE FILE CONVERTER")
        print("=" * 60)
        print("\n📝 Please paste your pyvnt Python code below.")
    
    print("Type 'END' on a new line when finished, or press Ctrl+D (Linux/Mac) / Ctrl+Z+Enter (Windows)")
    print("-" * 40)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except KeyboardInterrupt:
            print("\n\n⚠️ Operation cancelled.")
            sys.exit(0)
        except EOFError:
            break
    
    return '\n'.join(lines)

def get_output_filename(mode, custom_name=None):
    """Generate appropriate filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if custom_name:
        if mode == ConversionMode.CASE_TO_PYVNT:
            if not custom_name.endswith('.py'):
                custom_name += '.py'
        else:
            if not custom_name.endswith('.txt'):
                custom_name += '.txt'
        return custom_name
    
    if mode == ConversionMode.CASE_TO_PYVNT:
        return f"pyvnt_code_{timestamp}.py"
    else:
        return f"openfoam_case_{timestamp}.txt"

def create_pyvnt_to_case_prompt(context, pyvnt_code):
    """Create prompt for pyvnt to case file conversion"""
    return f"""
You are an expert in converting pyvnt Python tree structures to OpenFOAM case file format.

Here is the detailed context about the conversion process:

{context}

Now, please convert the following pyvnt Python code into equivalent OpenFOAM case file format:

```python
{pyvnt_code}
```

IMPORTANT INSTRUCTIONS:
1. **Analyze the complete pyvnt tree structure** - look at all Node_C objects and their relationships
2. **Extract ALL property values** from each Key_C object - each Key_C contains ValueProperty instances
3. **Follow the exact tree hierarchy** - maintain parent-child relationships as nested dictionaries
4. **Use proper OpenFOAM formatting**:
   - Dictionary names followed by opening brace
   - Key-value pairs with proper spacing and semicolons
   - 4-space indentation per level
   - Closing braces at appropriate indentation levels
5. **Handle all property types** correctly (Int_P, Flt_P, Str_P, Enm_P)
6. **Format values appropriately** for OpenFOAM (scientific notation, proper strings, etc.)

Return ONLY the OpenFOAM case file content with proper formatting. Do not include any explanations, code blocks, or markdown formatting.
"""

def pyvnt_to_case_conversion(model, context, pyvnt_code):
    """Convert pyvnt Python code to OpenFOAM case file format using Gemini"""
    prompt = create_pyvnt_to_case_prompt(context, pyvnt_code)
    
    print("\n" + "=" * 60)
    print("AI-POWERED CONVERSION IN PROGRESS")
    print("=" * 60)
    
    loader = LoadingIndicator("🔄 Generating OpenFOAM case file")
    loader.start()
    
    try:
        response = model.generate_content(prompt)
        loader.stop()
        print("✅ OpenFOAM case file generated successfully!")
        return response.text
    except Exception as e:
        loader.stop()
        print(f"❌ Error generating case file: {e}")
        return None

def save_output(content, filename, mode, directories):
    """Save the generated content to appropriate directory"""
    try:
        if mode == ConversionMode.CASE_TO_PYVNT:
            filepath = directories['python'] / filename
            print(f"\n📦 Saving Python file to pyvnt_package directory...")
        else:
            filepath = directories['text'] / filename
            print(f"\n📄 Saving text file to generated_text_files directory...")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Generated content saved to: {filepath}")
        return str(filepath)
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return None

def main():
    """Main function with enhanced options"""
    print("📁 Setting up output directories...")
    directories = create_output_directories()
    
    mode = get_conversion_mode()
    
    if mode == "PROGRAMMATIC":
        demonstrate_read_function()
        return
    
    print("\n🤖 Initializing AI converter...")
    model = setup_gemini()
    print("✅ AI converter ready!")
    
    print(f"\n📚 Loading conversion context...")
    context = load_context(mode)
    
    input_content = get_input_content(mode)
    
    if not input_content.strip():
        print("❌ No content provided. Exiting.")
        sys.exit(1)
    
    if mode == ConversionMode.CASE_TO_PYVNT:
        result = case_to_pyvnt_conversion(model, context, input_content)
    else:
        result = pyvnt_to_case_conversion(model, context, input_content)
    
    if result:
        result = result.strip()
        if result.startswith('```'):
            lines = result.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            result = '\n'.join(lines)
        
        print("\n" + "=" * 60)
        print("🎉 CONVERSION RESULT:")
        print("=" * 60)
        print(result)
        
        save_choice = input("\n💾 Save this result to a file? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes', '']:
            suggested_filename = get_output_filename(mode)
            filename = input(f"📁 Enter filename (default: {suggested_filename}): ").strip()
            if not filename:
                filename = suggested_filename
            else:
                filename = get_output_filename(mode, filename)
            
            saved_path = save_output(result, filename, mode, directories)
            if saved_path:
                print(f"📂 File location: {saved_path}")
                if mode == ConversionMode.CASE_TO_PYVNT:
                    print(f"\n✅ '{filename}' has been generated in the pyvnt_package directory.")
                    print(f"👉 Head over to the pyvnt_package directory to run the generated file:\n")
                    print(f"   cd pyvnt_package && python3 {filename}\n")
    else:
        print("❌ Conversion failed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)