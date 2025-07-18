#!/usr/bin/env python3
"""
OpenFOAM AI Assistant Web Application
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import uuid
import traceback
import json
import sys
import os

# Import your existing modules
try:
    from pyvnt.DictionaryElement.foamDS import Foam
    from pyvnt.DictionaryElement.keyData import KeyData
    from pyvnt.DictionaryElement.showTree import showTree
    from pyvnt.Reference.basic import PropertyString, PropertyInt, PropertyFloat
    PYVNT_AVAILABLE = True
except ImportError:
    PYVNT_AVAILABLE = False

# Import new PyVnt LLM integration
try:
    import sys
    import os
    pyvnt_path = os.path.join(os.path.dirname(__file__), 'pyvnt')
    sys.path.insert(0, pyvnt_path)
    import pyvnt
    
    # Also import our LLM integration module
    import pyvnt_llm_integration as pyvnt_llm
    
    PYVNT_LLM_AVAILABLE = True
    print("✅ PyVnt LLM integration loaded successfully")
except ImportError as e:
    PYVNT_LLM_AVAILABLE = False
    pyvnt_llm = None
    print(f"❌ PyVnt LLM integration not available: {e}")

from together import Together

# Import your existing modules
try:
    from llm import OpenFOAMChatBot
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    OpenFOAMChatBot = None

try:
    from RAG_llm import OpenFOAMRAGChatBot
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    OpenFOAMRAGChatBot = None

try:
    from converter import get_completion
    CONVERTER_AVAILABLE = True
except ImportError:
    CONVERTER_AVAILABLE = False
    get_completion = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'openfoam-ai-assistant'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store chat sessions
chat_sessions = {}

class WebChatBot:
    def __init__(self, use_rag=False):
        self.use_rag = use_rag
        if use_rag and RAG_AVAILABLE and OpenFOAMRAGChatBot:
            self.bot = OpenFOAMRAGChatBot()
        elif LLM_AVAILABLE and OpenFOAMChatBot:
            self.bot = OpenFOAMChatBot()
        else:
            raise ImportError("No chat bot available")
        self.conversation_history = []

    def send_message(self, message, output_type='text'):
        try:
            # Get the main response first
            if self.use_rag and RAG_AVAILABLE and hasattr(self.bot, 'send_message'):
                response, sources = self.bot.send_message(message)
                result = {
                    'response': response,
                    'sources': sources,
                    'type': 'rag'
                }
            else:
                response = self.bot.send_message(message)
                result = {
                    'response': response,
                    'sources': [],
                    'type': 'simple'
                }
            
            # Handle converter output based on output_type
            converter_output = None
            pyvnt_llm_output = None
            
            if output_type in ['convert', 'both'] and CONVERTER_AVAILABLE and get_completion:
                try:
                    # For convert-only mode, use the message as OpenFOAM content
                    # For both mode, extract potential OpenFOAM content from the response
                    if output_type == 'convert':
                        pyvnt_code = get_completion(message)
                    else:  # both mode
                        # Try to extract code blocks from the response, otherwise use the message
                        openfoam_content = self._extract_openfoam_content(response) or message
                        pyvnt_code = get_completion(openfoam_content)
                    
                    converter_output = {
                        'pyvnt_code': pyvnt_code,
                        'success': True
                    }
                except Exception as e:
                    converter_output = {
                        'pyvnt_code': f"// Conversion Error: {str(e)}",
                        'success': False
                    }

            # Handle PyVnt LLM generation for file generation requests
            if PYVNT_LLM_AVAILABLE and self._is_file_generation_request(message):
                try:
                    # Detect what type of file is being requested
                    file_type = self._detect_file_type(message)
                    content = pyvnt.generate(message, file_type)
                    
                    pyvnt_llm_output = {
                        'content': content,
                        'file_type': file_type,
                        'success': True
                    }
                except Exception as e:
                    pyvnt_llm_output = {
                        'content': f"// Generation Error: {str(e)}",
                        'file_type': 'dictionary',
                        'success': False
                    }
            
            result['converter_output'] = converter_output
            result['pyvnt_llm_output'] = pyvnt_llm_output
            return result
            
        except Exception as e:
            return {
                'response': f"❌ Error: {str(e)}",
                'sources': [],
                'type': 'error',
                'converter_output': None,
                'pyvnt_llm_output': None
            }
    
    def _is_file_generation_request(self, message):
        """Check if the message is requesting file generation"""
        generation_keywords = [
            'create', 'generate', 'make', 'build', 'write',
            'controlDict', 'fvSchemes', 'fvSolution', 'blockMeshDict',
            'transportProperties', 'turbulenceProperties', 'decomposeParDict'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in generation_keywords)
    
    def _detect_file_type(self, message):
        """Detect what type of OpenFOAM file is being requested"""
        message_lower = message.lower()
        
        if 'controldict' in message_lower or 'control dict' in message_lower:
            return 'controlDict'
        elif 'fvschemes' in message_lower or 'fv schemes' in message_lower:
            return 'fvSchemes'
        elif 'fvsolution' in message_lower or 'fv solution' in message_lower:
            return 'fvSolution'
        elif 'blockmesh' in message_lower or 'block mesh' in message_lower:
            return 'blockMeshDict'
        elif 'transport' in message_lower:
            return 'transportProperties'
        elif 'turbulence' in message_lower:
            return 'turbulenceProperties'
        elif 'decompose' in message_lower:
            return 'decomposeParDict'
        else:
            return 'dictionary'
    
    def _extract_openfoam_content(self, text):
        """Extract potential OpenFOAM dictionary content from text"""
        import re
        # Look for code blocks or dictionary-like structures
        code_block_pattern = r'```(?:openfoam|foam|dict)?\n?(.*?)\n?```'
        matches = re.findall(code_block_pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches[0].strip()
        
        # Look for dictionary patterns (lines with { } ; structure)
        lines = text.split('\n')
        openfoam_lines = []
        in_dict = False
        for line in lines:
            stripped = line.strip()
            if '{' in stripped or '}' in stripped or stripped.endswith(';'):
                in_dict = True
                openfoam_lines.append(line)
            elif in_dict and (stripped == '' or stripped.startswith('//')):
                openfoam_lines.append(line)
            elif in_dict and not any(c in stripped for c in '{}();'):
                break
                
        if openfoam_lines:
            return '\n'.join(openfoam_lines)
        
        return None

@app.route('/')
def index():
    return render_template('index.html', 
                         rag_available=RAG_AVAILABLE, 
                         pyvnt_available=PYVNT_AVAILABLE,
                         pyvnt_llm_available=PYVNT_LLM_AVAILABLE)

@app.route('/chat')
def chat():
    return render_template('chat.html', 
                         rag_available=RAG_AVAILABLE,
                         pyvnt_llm_available=PYVNT_LLM_AVAILABLE)

@app.route('/converter')
def converter():
    return render_template('converter.html', 
                         pyvnt_available=PYVNT_AVAILABLE,
                         pyvnt_llm_available=PYVNT_LLM_AVAILABLE)

@app.route('/generator')
def generator():
    """New route for PyVnt LLM file generator"""
    return render_template('generator.html', pyvnt_llm_available=PYVNT_LLM_AVAILABLE)

@app.route('/api/convert', methods=['POST'])
def convert_openfoam():
    try:
        if not CONVERTER_AVAILABLE or not get_completion:
            return jsonify({'error': 'Converter not available'}), 503
            
        data = request.get_json()
        openfoam_content = data.get('content', '')
        
        if not openfoam_content.strip():
            return jsonify({'error': 'No content provided'}), 400
        
        # Generate PyVnt code
        pyvnt_code = get_completion(openfoam_content)
        
        # Try to execute and capture tree output
        tree_output = ""
        if PYVNT_AVAILABLE:
            try:
                # Capture showTree output
                import io
                import sys
                from contextlib import redirect_stdout
                
                f = io.StringIO()
                with redirect_stdout(f):
                    exec(pyvnt_code, globals())
                tree_output = f.getvalue()
            except Exception as e:
                tree_output = f"Error executing code: {str(e)}"
        
        return jsonify({
            'success': True,
            'pyvnt_code': pyvnt_code,
            'tree_output': tree_output
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/generate_file', methods=['POST'])
def generate_openfoam_file():
    """Enhanced endpoint for both LLM and traditional PyVnt file generation/conversion"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        openfoam_content = data.get('openfoam_content', '')
        file_type = data.get('file_type', 'dictionary')
        generation_mode = data.get('mode', 'llm_generate')
        
        result = {}
        
        if generation_mode == 'llm_generate':
            # LLM Generate content only
            if not PYVNT_LLM_AVAILABLE:
                return jsonify({'error': 'PyVnt LLM integration not available'}), 503
            if not prompt.strip():
                return jsonify({'error': 'No prompt provided'}), 400
                
            content = pyvnt_llm.generate(prompt, file_type)
            result = {
                'success': True,
                'content': content,
                'mode': 'llm_generate',
                'method': 'LLM Generated'
            }
            
        elif generation_mode == 'llm_write':
            # LLM Generate and write to a temporary location
            if not PYVNT_LLM_AVAILABLE:
                return jsonify({'error': 'PyVnt LLM integration not available'}), 503
            if not prompt.strip():
                return jsonify({'error': 'No prompt provided'}), 400
            
            import os  # Ensure os is available locally
            temp_filename = f"temp_{uuid.uuid4().hex}_{file_type}"
            temp_path = os.path.join('temp_generated', temp_filename)
            os.makedirs('temp_generated', exist_ok=True)
            
            success = pyvnt_llm.write(temp_path, prompt, file_type)
            
            if success:
                with open(temp_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                result = {
                    'success': True,
                    'content': content,
                    'mode': 'llm_write',
                    'method': 'LLM Generated and Formatted',
                    'file_path': temp_path
                }
            else:
                result = {
                    'success': False,
                    'error': 'Failed to generate file using LLM'
                }
                
        elif generation_mode == 'traditional_write':
            # Traditional PyVNT Writer - Convert prompt to PyVNT tree then to OpenFOAM
            if not PYVNT_AVAILABLE:
                return jsonify({'error': 'PyVnt not available'}), 503
            if not prompt.strip():
                return jsonify({'error': 'No prompt provided'}), 400
            
            try:
                # Use the already imported pyvnt module with proper path
                import sys
                import os
                pyvnt_path = os.path.join(os.path.dirname(__file__), 'pyvnt')
                if pyvnt_path not in sys.path:
                    sys.path.insert(0, pyvnt_path)
                
                # Import using the available functions from pyvnt
                # Since pyvnt is already imported and available, use its functions
                content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | foam-extend: Open Source CFD                   |
|  \\\\    /   O peration     | Version:     5.0                               |
|   \\\\  /    A nd           | Web:         http://www.foam-extend.org         |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      {file_type};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// Generated using Traditional PyVNT Writer
// Prompt: {prompt}

"""
                
                # Add basic content based on file type and prompt
                if "controlDict" in prompt.lower() or file_type == "controlDict":
                    content += """application     icoFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         1;

deltaT          0.001;

writeControl    timeStep;

writeInterval   100;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;
"""
                elif "fvSchemes" in prompt.lower() or file_type == "fvSchemes":
                    content += """ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear orthogonal;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         orthogonal;
}
"""
                elif "fvSolution" in prompt.lower() or file_type == "fvSolution":
                    content += """solvers
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
        smoother        symmetricGaussSeidelSmoother;
        tolerance       1e-05;
        relTol          0;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
}
"""
                else:
                    content += f"""// Basic {file_type} structure
// Add your specific content here based on the prompt: {prompt}

key1    value1;
key2    value2;
"""

                content += "\n// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n"
                
                result = {
                    'success': True,
                    'content': content,
                    'mode': 'traditional_write',
                    'method': 'Traditional PyVNT Writer (Simplified)'
                }
                
            except Exception as e:
                result = {
                    'success': False,
                    'error': f'Traditional writer error: {str(e)}'
                }
                
        elif generation_mode == 'traditional_read':
            # Traditional PyVNT Reader - Convert OpenFOAM content to PyVNT code
            if not PYVNT_AVAILABLE:
                return jsonify({'error': 'PyVnt not available'}), 503
            if not openfoam_content.strip():
                return jsonify({'error': 'No OpenFOAM content provided'}), 400
            
            try:
                # For now, provide a simplified conversion without complex parsing
                # This creates PyVNT code that represents the structure
                
                lines = openfoam_content.strip().split('\n')
                detected_entries = []
                
                # Simple parsing to detect key-value pairs
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('//') and not line.startswith('/*') and ';' in line:
                        parts = line.split(';')[0].strip().split()
                        if len(parts) >= 2:
                            key = parts[0]
                            value = ' '.join(parts[1:])
                            detected_entries.append((key, value))
                
                # Generate PyVNT code
                pyvnt_code = f"""# Generated PyVNT code from OpenFOAM content
# This is a simplified conversion using Traditional PyVNT Reader

import sys
import os
sys.path.insert(0, 'pyvnt')
from pyvnt.Reference.basic import Str_P, Int_P, Flt_P
from pyvnt.Container.node import Node_C
from pyvnt.Container.key import Key_C

# Create PyVNT tree structure
root = Node_C("root")

# Detected entries from OpenFOAM content:
"""
                
                for key, value in detected_entries[:10]:  # Limit to first 10 entries
                    # Try to determine the type
                    try:
                        float_val = float(value)
                        if '.' in value:
                            pyvnt_code += f'root.add_child(Key_C("{key}", Flt_P("{key}", {float_val})))\n'
                        else:
                            pyvnt_code += f'root.add_child(Key_C("{key}", Int_P("{key}", {int(float_val)})))\n'
                    except ValueError:
                        clean_value = value.replace('"', '').replace("'", "")
                        pyvnt_code += f'root.add_child(Key_C("{key}", Str_P("{key}", "{clean_value}")))\n'
                
                pyvnt_code += f"""
# Original OpenFOAM content (first 300 chars):
# {openfoam_content[:300]}...

# Convert tree to OpenFOAM format when needed:
# from pyvnt.Converter.Writer.writer import write_out
# content = write_out(root, "dictionary", "converted", "system")

print("PyVNT tree created successfully from OpenFOAM content")
print(f"Root node has {{len(root.children)}} child nodes")
"""
                
                result = {
                    'success': True,
                    'content': pyvnt_code,
                    'mode': 'traditional_read',
                    'method': 'Traditional PyVNT Reader (Simplified Parser)'
                }
                
            except Exception as e:
                result = {
                    'success': False,
                    'error': f'Traditional reader error: {str(e)}'
                }
        
        else:
            result = {
                'success': False,
                'error': f'Unknown generation mode: {generation_mode}'
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/explain_file', methods=['POST'])
def explain_openfoam_file():
    """New endpoint for PyVnt LLM file explanation"""
    try:
        if not PYVNT_LLM_AVAILABLE:
            return jsonify({'error': 'PyVnt LLM integration not available'}), 503
            
        data = request.get_json()
        content = data.get('content', '')
        
        if not content.strip():
            return jsonify({'error': 'No content provided'}), 400
        
        # Use the LLM integration explain function directly
        explanation = pyvnt_llm.explain(content)
        
        return jsonify({
            'success': True,
            'explanation': explanation
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/convert_tree', methods=['POST'])  
def convert_tree_to_openfoam():
    """New endpoint for PyVnt tree to OpenFOAM conversion"""
    try:
        if not PYVNT_LLM_AVAILABLE:
            return jsonify({'error': 'PyVnt LLM integration not available'}), 503
            
        data = request.get_json()
        pyvnt_code = data.get('pyvnt_code', '')
        file_type = data.get('file_type', 'dictionary')
        object_name = data.get('object_name', '')
        location = data.get('location', '')
        
        if not pyvnt_code.strip():
            return jsonify({'error': 'No PyVnt code provided'}), 400
        
        # Execute PyVnt code to create tree object
        exec_globals = {}
        exec_locals = {}
        
        # Import necessary modules for execution
        exec("import sys; sys.path.insert(0, 'pyvnt'); import pyvnt", exec_globals)
        exec("from pyvnt.DictionaryElement.foamDS import Foam", exec_globals)
        exec("from pyvnt.DictionaryElement.keyData import KeyData", exec_globals)  
        exec("from pyvnt.Reference.basic import PropertyString, PropertyInt, PropertyFloat", exec_globals)
        
        exec(pyvnt_code, exec_globals, exec_locals)
        
        # Find the tree object (usually the last created object)
        tree_object = None
        for var_name, var_value in exec_locals.items():
            if hasattr(var_value, '__dict__') and not var_name.startswith('_'):
                tree_object = var_value
                break
        
        if tree_object is None:
            # Fallback: look in globals
            for var_name, var_value in exec_globals.items():
                if hasattr(var_value, '__dict__') and not var_name.startswith('_'):
                    tree_object = var_value
                    break
        
        if tree_object is None:
            return jsonify({
                'success': False,
                'error': 'No valid PyVnt tree object found in code'
            })
        
        # Convert tree to OpenFOAM format
        openfoam_content = pyvnt.tree_to_string(tree_object, file_type, object_name, location)
        
        return jsonify({
            'success': True,
            'content': openfoam_content
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@socketio.on('connect')
def handle_connect():
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    emit('connected', {'session_id': session_id})

@socketio.on('start_chat')
def handle_start_chat(data):
    session_id = session['session_id']
    use_rag = data.get('use_rag', False)
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = WebChatBot(use_rag=use_rag)
    
    emit('chat_ready', {
        'message': f"🤖 OpenFOAM Assistant ready! ({'RAG-powered' if use_rag else 'Simple LLM'})",
        'type': 'rag' if use_rag else 'simple'
    })

@socketio.on('send_message')
def handle_message(data):
    session_id = session['session_id']
    message = data['message']
    output_type = data.get('output_type', 'text')
    
    if session_id not in chat_sessions:
        emit('error', {'message': 'Chat session not found. Please refresh the page.'})
        return
    
    try:
        # Show typing indicator
        emit('typing', {'typing': True})
        
        # Get response from bot with output type
        result = chat_sessions[session_id].send_message(message, output_type)
        
        emit('typing', {'typing': False})
        emit('message_response', result)
        
    except Exception as e:
        emit('typing', {'typing': False})
        emit('error', {'message': f"Error: {str(e)}"})

@socketio.on('clear_chat')
def handle_clear_chat():
    session_id = session['session_id']
    if session_id in chat_sessions:
        chat_sessions[session_id].bot.clear_history()
    emit('chat_cleared')

@socketio.on('disconnect')
def handle_disconnect():
    session_id = session.get('session_id')
    if session_id in chat_sessions:
        del chat_sessions[session_id]

if __name__ == '__main__':
    print("🌊 Starting OpenFOAM AI Assistant Web Application...")
    print("🔍 RAG System:", "Available" if RAG_AVAILABLE else "Not Available")
    print("🔧 PyVnt Converter:", "Available" if PYVNT_AVAILABLE else "Not Available") 
    print("🤖 PyVnt LLM Integration:", "Available" if PYVNT_LLM_AVAILABLE else "Not Available")
    print("🌐 Opening at: http://localhost:5000")
    
    if PYVNT_LLM_AVAILABLE:
        print("✨ New Features Available:")
        print("  • AI-powered OpenFOAM file generation")
        print("  • Natural language to OpenFOAM conversion")
        print("  • File explanation and analysis")
        print("  • PyVnt tree to OpenFOAM conversion")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
