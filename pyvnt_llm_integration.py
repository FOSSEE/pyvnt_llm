#!/usr/bin/env python3
"""
LLM Integration for PyVNT
Provides LLM-powered OpenFOAM file generation capabilities
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the pyvnt path
pyvnt_path = os.path.join(os.path.dirname(__file__), 'pyvnt')
sys.path.insert(0, pyvnt_path)

try:
    from together import Together
    TOGETHER_AVAILABLE = True
    
    # Initialize Together client with API key from environment
    API_KEY = os.getenv('TOGETHER_API_KEY')
    if API_KEY:
        together_client = Together(api_key=API_KEY)
        print("✅ Together AI client initialized successfully")
    else:
        together_client = None
        TOGETHER_AVAILABLE = False
        print("❌ TOGETHER_API_KEY not found in environment")
        
except ImportError:
    TOGETHER_AVAILABLE = False
    together_client = None
    print("❌ Together AI library not available")

def generate(prompt: str, file_type: str = "dictionary") -> str:
    """
    Generate OpenFOAM content using LLM
    
    Args:
        prompt: Description of what to generate
        file_type: Type of OpenFOAM file to generate
        
    Returns:
        Generated OpenFOAM content as string
    """
    if not TOGETHER_AVAILABLE or not together_client:
        return f"""// Error: Together AI not available or API key not set
// Prompt was: {prompt}
// File type: {file_type}

// This is a placeholder implementation
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      {file_type};
}}

// Generated based on prompt: {prompt}
// TODO: Set TOGETHER_API_KEY environment variable
"""

    try:
        # Create a detailed prompt for OpenFOAM generation
        system_prompt = f"""You are an expert in OpenFOAM CFD simulation software. 
Generate a complete, properly formatted OpenFOAM {file_type} file based on the user's description.
The output should be valid OpenFOAM syntax with proper FoamFile header.
Do not include any explanations, only the file content."""

        user_prompt = f"Create an OpenFOAM {file_type} file: {prompt}"
        
        response = together_client.chat.completions.create(
            model="meta-llama/Llama-3.2-3B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1024,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"""// Error generating content: {str(e)}
// Prompt was: {prompt}
// File type: {file_type}

FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      {file_type};
}}

// Generated based on prompt: {prompt}
// Error occurred during LLM generation
"""

def write(file_path: str, prompt: str, file_type: str = "dictionary") -> bool:
    """
    Generate OpenFOAM content and write to file
    
    Args:
        file_path: Path where to write the file
        prompt: Description of what to generate
        file_type: Type of OpenFOAM file to generate
        
    Returns:
        True if successful, False otherwise
    """
    try:
        content = generate(prompt, file_type)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return True
        
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
        return False

def explain(content: str) -> str:
    """
    Explain OpenFOAM content using LLM
    
    Args:
        content: OpenFOAM content to explain
        
    Returns:
        Explanation of the content
    """
    if not TOGETHER_AVAILABLE or not together_client:
        return f"Together AI not available or API key not set. Cannot explain content: {content[:100]}..."

    try:
        system_prompt = """You are an expert in OpenFOAM CFD simulation software.
Explain the given OpenFOAM file content in detail, including:
- What type of file it is
- What each section/parameter does
- How it fits into an OpenFOAM simulation
- Any important notes or best practices"""

        user_prompt = f"Explain this OpenFOAM content:\n\n{content}"
        
        response = together_client.chat.completions.create(
            model="meta-llama/Llama-3.2-3B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1024,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error explaining content: {str(e)}"

# Make functions available at module level
__all__ = ['generate', 'write', 'explain']
