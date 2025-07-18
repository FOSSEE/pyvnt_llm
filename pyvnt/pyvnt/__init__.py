from pyvnt.Reference.basic import *
from pyvnt.Reference.vector import *
from pyvnt.Reference.tensor import *
from pyvnt.Reference.dimension_set import Dim_Set_P
from pyvnt.Container.node import *
from pyvnt.Container.key import *
from pyvnt.Container.list import *
from pyvnt.Converter.Writer.writer import *
from pyvnt.utils import *
from pyvnt.utils.show_tree import *

# from pyvnt.Converter.Reader import read
from pyvnt.Converter.PlyParser.Parser import *

# Initialize __all__ list
__all__ = []

# Import LLM integration functions
try:
    import sys
    import os
    # Get the parent directory (CFD) and import the LLM integration
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, parent_dir)
    
    from pyvnt_llm_integration import generate as _llm_generate, write as _llm_write, explain as _llm_explain
    
    # Make LLM functions available at package level
    def generate(prompt, file_type="dictionary"):
        return _llm_generate(prompt, file_type)
    
    def write(file_path, prompt, file_type="dictionary"):
        return _llm_write(file_path, prompt, file_type)
    
    def explain(content):
        return _llm_explain(content)
    
    __all__.extend(['generate', 'write', 'explain'])
    
except ImportError as e:
    print(f"Warning: LLM integration not available: {e}")
    
    # Provide placeholder functions
    def generate(prompt, file_type="dictionary"):
        return f"// LLM integration not available\n// Prompt: {prompt}\n// File type: {file_type}"
    
    def write(file_path, prompt, file_type="dictionary"):
        return False
    
    def explain(content):
        return "LLM integration not available for explanation"