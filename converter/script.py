#!/usr/bin/env python3
"""
Improved Bidirectional Converter: Case Files ↔ pyvnt Python Code
Both directions now use Gemini LLM for reliable conversion!
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

def load_context(mode):
    """Load the appropriate context based on conversion mode"""
    if mode == ConversionMode.CASE_TO_PYVNT:
        context_file = Path("context_updated.md")
        fallback_context = get_case_to_pyvnt_context()
    else:
        # Use your specific context file name
        context_file = Path("context_pyvnt_to_trees.md")
        fallback_context = get_pyvnt_to_openfoam_context()
    
    if not context_file.exists():
        print(f"Warning: {context_file} not found. Using embedded context.")
        return fallback_context
    
    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            context_content = f.read()
            print(f"✓ Loaded context from {context_file}")
            return context_content
    except Exception as e:
        print(f"Error reading {context_file}: {e}")
        return fallback_context

def get_case_to_pyvnt_context():
    """Embedded context for case file to pyvnt conversion"""
    return """
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

### 4. Node_C
- Tree node class (inherits from anytree's NodeMixin).
- Holds a name, parent, children, and a list of Key_C objects as data.
- Always pass `None` as the third argument for non-leaf nodes.
- Example: `Node_C('nodeName', parent, None, data1, data2)`

### 5. show_tree
- Utility to print the tree structure and Key_C at each node.
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
    Key_C('tolerance', Flt_P('val1', default=1e-06))
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

def get_conversion_mode():
    """Get conversion mode from user"""
    print("=" * 70)
    print("🚀 BIDIRECTIONAL CONVERTER: OpenFOAM ↔ pyvnt (AI-Powered)")
    print("=" * 70)
    print("\nSelect conversion mode:")
    print("1. 📄 OpenFOAM Case Files → 🐍 pyvnt Python Code")
    print("2. 🐍 pyvnt Python Code → 📄 OpenFOAM Case Files")
    print("3. 🚪 Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice == "1":
                return ConversionMode.CASE_TO_PYVNT
            elif choice == "2":
                return ConversionMode.PYVNT_TO_CASE
            elif choice == "3":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\n⚠️ Operation cancelled.")
            sys.exit(0)
        except EOFError:
            print("\n\n⚠️ Operation cancelled.")
            sys.exit(0)

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

def create_case_to_pyvnt_prompt(context, case_file_content):
    """Create prompt for case file to pyvnt conversion"""
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
4. Set reasonable constraints (min/max values) and defaults based on typical OpenFOAM values
5. Always pass `None` as the third argument to Node_C constructor for non-leaf nodes
6. Include the final `show_tree()` call to display the structure
7. Add appropriate comments explaining the structure

Return ONLY the Python code, no explanations or markdown formatting.
"""

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

def case_to_pyvnt_conversion(model, context, case_file_content):
    """Convert OpenFOAM case file to pyvnt code using Gemini"""
    prompt = create_case_to_pyvnt_prompt(context, case_file_content)
    
    print("\n" + "=" * 60)
    print("AI-POWERED CONVERSION IN PROGRESS")
    print("=" * 60)
    
    # Start loading indicator
    loader = LoadingIndicator("🔄 Generating pyvnt code")
    loader.start()
    
    try:
        response = model.generate_content(prompt)
        loader.stop()
        print("✅ pyvnt code generated successfully!")
        return response.text
    except Exception as e:
        loader.stop()
        print(f"❌ Error generating code: {e}")
        return None

def pyvnt_to_case_conversion(model, context, pyvnt_code):
    """Convert pyvnt Python code to OpenFOAM case file format using Gemini"""
    prompt = create_pyvnt_to_case_prompt(context, pyvnt_code)
    
    print("\n" + "=" * 60)
    print("AI-POWERED CONVERSION IN PROGRESS")
    print("=" * 60)
    
    # Start loading indicator
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

def save_output(content, filename, mode):
    """Save the generated content to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ Generated content saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

def main():
    """Main function"""
    # Setup Gemini (needed for both conversion modes now)
    print("🤖 Initializing AI converter...")
    model = setup_gemini()
    print("✅ AI converter ready!")
    
    # Get conversion mode
    mode = get_conversion_mode()
    
    # Load appropriate context
    print(f"\n📚 Loading conversion context...")
    context = load_context(mode)
    
    # Get input content
    input_content = get_input_content(mode)
    
    if not input_content.strip():
        print("❌ No content provided. Exiting.")
        sys.exit(1)
    
    # Perform conversion based on mode (both now use Gemini!)
    if mode == ConversionMode.CASE_TO_PYVNT:
        result = case_to_pyvnt_conversion(model, context, input_content)
        default_filename = "generated_pyvnt_code.py"
    else:
        result = pyvnt_to_case_conversion(model, context, input_content)
        default_filename = "generated_case_file.txt"
    
    if result:
        # Clean up the result (remove any markdown formatting if present)
        result = result.strip()
        if result.startswith('```'):
            lines = result.split('\n')
            # Remove first line if it's markdown formatting
            if lines[0].startswith('```'):
                lines = lines[1:]
            # Remove last line if it's markdown formatting
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            result = '\n'.join(lines)
        
        print("\n" + "=" * 60)
        print("🎉 CONVERSION RESULT:")
        print("=" * 60)
        print(result)
        
        # Ask if user wants to save
        save_choice = input("\n💾 Save this result to a file? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes', '']:
            filename = input(f"📁 Enter filename (default: {default_filename}): ").strip()
            if not filename:
                filename = default_filename
            save_output(result, filename, mode)
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