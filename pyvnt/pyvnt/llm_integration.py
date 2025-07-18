# """
# PyVNT LLM Integration Module

# This module provides LLM-powered OpenFOAM file generation capabilities
# and tree-to-OpenFOAM file conversion functionality.
# """

# import os
# import sys
# from typing import Union, Optional
# from pyvnt.Container.node import Node_C
# from pyvnt.Converter.Writer.writer import writeTo, write_out

# # Import LLM functionality from the main CFD directory
# LLM_AVAILABLE = False
# OpenFOAMChatBot = None

# try:
#     # Add the main CFD directory to path to access LLM modules
#     main_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     if main_dir not in sys.path:
#         sys.path.insert(0, main_dir)
    
#     from llm import OpenFOAMChatBot
#     LLM_AVAILABLE = True
# except ImportError:
#     pass
# except Exception:
#     pass


# class PyVntLLM:
#     """LLM integration class for PyVNT OpenFOAM file generation."""
    
#     def __init__(self, api_key: Optional[str] = None):
#         """
#         Initialize the PyVNT LLM integration.
        
#         Args:
#             api_key: Optional API key for the LLM service
#         """
#         self.llm_available = LLM_AVAILABLE
#         self.chatbot = None
        
#         if self.llm_available and OpenFOAMChatBot:
#             try:
#                 self.chatbot = OpenFOAMChatBot()
#                 print("✅ PyVNT LLM integration initialized successfully")
#             except Exception as e:
#                 print(f"❌ Failed to initialize LLM: {e}")
#                 self.llm_available = False
    
#     def generate_openfoam_content(self, prompt: str) -> str:
#         """
#         Generate OpenFOAM content using LLM.
        
#         Args:
#             prompt: Description of what OpenFOAM content to generate
            
#         Returns:
#             Generated OpenFOAM content as string
#         """
#         if not self.llm_available or not self.chatbot:
#             raise RuntimeError("LLM is not available. Cannot generate content.")
        
#         try:
#             response = self.chatbot.chat(prompt)
#             return response
#         except Exception as e:
#             raise RuntimeError(f"Failed to generate OpenFOAM content: {e}")


# def tree_to_openfoam_string(tree: Node_C) -> str:
#     """
#     Convert a PyVNT tree to OpenFOAM format string.
    
#     Args:
#         tree: PyVNT Node_C tree object
        
#     Returns:
#         OpenFOAM formatted string
#     """
#     if not isinstance(tree, Node_C):
#         raise TypeError("Input must be a PyVNT Node_C object")
    
#     # Create a string buffer to capture the output
#     from io import StringIO
#     string_buffer = StringIO()
    
#     # Write the tree to the string buffer
#     for child in tree.get_ordered_items():
#         write_out(child, string_buffer)
#         string_buffer.write("\n")
    
#     content = string_buffer.getvalue()
#     string_buffer.close()
    
#     return content


# def write_openfoam_file(filepath: str, tree: Node_C, file_class: str = "dictionary", 
#                        object_name: str = "", location: str = ""):
#     """
#     Write a PyVNT tree to an OpenFOAM file with proper header.
    
#     Args:
#         filepath: Path where to write the file
#         tree: PyVNT Node_C tree object
#         file_class: OpenFOAM file class (default: "dictionary")
#         object_name: OpenFOAM object name
#         location: OpenFOAM location
#     """
#     if not isinstance(tree, Node_C):
#         raise TypeError("Tree must be a PyVNT Node_C object")
    
#     # Ensure directory exists
#     os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
#     # Generate OpenFOAM header
#     header = f'''/*--------------------------------*- C++ -*----------------------------------*\\
#   =========                 |
#   \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
#    \\\\    /   O peration     | Website:  https://openfoam.org
#     \\\\  /    A nd           | Version:  12
#      \\\\/     M anipulation  |
# \\*---------------------------------------------------------------------------*/
# FoamFile
# {{
#     format      ascii;
#     class       {file_class};
#     object      {object_name or os.path.basename(filepath)};
#     location    "{location}";
# }}
# // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

# '''
    
#     # Convert tree to OpenFOAM content
#     content = tree_to_openfoam_string(tree)
    
#     # Write to file
#     with open(filepath, 'w') as f:
#         f.write(header)
#         f.write(content)
#         f.write('\n// ************************************************************************* //\n')


# def write(filepath: str, content: Union[str, Node_C], **kwargs) -> bool:
#     """
#     Main write function for PyVNT - handles both LLM generation and tree conversion.
    
#     Args:
#         filepath: Path where to write the OpenFOAM file
#         content: Either a string prompt for LLM generation or a PyVNT Node_C tree
#         **kwargs: Additional arguments for file generation
        
#     Returns:
#         True if successful, False otherwise
#     """
#     try:
#         if isinstance(content, str):
#             # LLM generation mode
#             llm = PyVntLLM()
#             if not llm.llm_available:
#                 print("❌ LLM not available for content generation")
#                 return False
            
#             print(f"🤖 Generating OpenFOAM content for: {filepath}")
#             openfoam_content = llm.generate_openfoam_content(content)
            
#             # Ensure directory exists
#             os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
#             # Write the generated content to file
#             with open(filepath, 'w') as f:
#                 f.write(openfoam_content)
            
#             print(f"✅ Generated and wrote file: {filepath}")
#             return True
            
#         elif isinstance(content, Node_C):
#             # Tree conversion mode
#             print(f"🔄 Converting PyVNT tree to OpenFOAM file: {filepath}")
#             write_openfoam_file(
#                 filepath, 
#                 content,
#                 kwargs.get('file_class', 'dictionary'),
#                 kwargs.get('object_name', ''),
#                 kwargs.get('location', '')
#             )
#             print(f"✅ Converted and wrote file: {filepath}")
#             return True
            
#         else:
#             raise TypeError("Content must be either a string prompt or PyVNT Node_C tree")
            
#     except Exception as e:
#         print(f"❌ Error writing file {filepath}: {e}")
#         return False


# def generate(prompt: str) -> str:
#     """
#     Generate OpenFOAM content using LLM without writing to file.
    
#     Args:
#         prompt: Description of what OpenFOAM content to generate
        
#     Returns:
#         Generated OpenFOAM content as string
#     """
#     llm = PyVntLLM()
#     return llm.generate_openfoam_content(prompt)


# def explain(openfoam_content: str) -> str:
#     """
#     Explain OpenFOAM content using LLM.
    
#     Args:
#         openfoam_content: OpenFOAM content to explain
        
#     Returns:
#         Explanation of the OpenFOAM content
#     """
#     llm = PyVntLLM()
#     prompt = f"Please explain this OpenFOAM content:\n\n{openfoam_content}"
#     return llm.generate_openfoam_content(prompt)


# # Make functions available at module level
# __all__ = ['write', 'generate', 'explain', 'tree_to_openfoam_string', 'write_openfoam_file', 'PyVntLLM']
