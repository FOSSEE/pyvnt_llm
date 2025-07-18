from pyvnt.DictionaryElement.foamDS import Foam
from pyvnt.DictionaryElement.keyData import KeyData
from pyvnt.DictionaryElement.showTree import showTree
from pyvnt.Reference.basic import PropertyString, PropertyInt, PropertyFloat
from together import Together
import ast

# Initialize the Together client with your API key
client = Together(api_key="97eb242cb120beb901b23eff5a2811de094d3b7377d2269fa1d80e545bf7e877")

def get_completion(prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional OpenFOAM expert with deep Python experience.\n"
                "Convert the given OpenFOAM dictionary content into PyVnt Python code that constructs a node tree.\n\n"
                "Use these imports:\n"
                "from pyvnt.DictionaryElement.foamDS import Foam\n"
                "from pyvnt.DictionaryElement.keyData import KeyData\n"
                "from pyvnt.DictionaryElement.showTree import showTree\n"
                "from pyvnt.Reference.basic import PropertyString, PropertyInt, PropertyFloat\n\n"
                "Structure:\n"
                "1. Create root: head = Foam('dictName')\n"
                "2. Create properties: prop = PropertyString('key', 'value') or PropertyFloat('key', 1.0) or PropertyInt('key', 1)\n"
                "3. Create KeyData: key = KeyData('keyName', prop)\n"
                "4. Add to node: head.data = [key1, key2, ...]\n"
                "5. For nested dictionaries, create child Foam nodes\n"
                "6. End with: showTree(head)\n\n"
                "Return ONLY valid Python code. No explanations, no comments, no markdown formatting."
            )
        },
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages,
        temperature=0,
    )


    code = response.choices[0].message.content.strip()
    
    
    if code.startswith("```python"):
        code = code[9:]  
    elif code.startswith("```"):
        code = code[3:]  
    if code.endswith("```"):
        code = code[:-3]  
    
    return code.strip()

def main():
    print("📄 OpenFOAM to PyVnt Converter")
    print("=" * 40)
    print("Paste your OpenFOAM dictionary content below.")
    print("On Windows: Press Ctrl+Z then Enter to finish input")
    print("On Linux/macOS: Press Ctrl+D to finish input")
    print("-" * 40)
    
    user_input = ""
    try:
        while True:
            line = input()
            user_input += line + "\n"
    except EOFError:
        pass
    
    if not user_input.strip():
        print("❌ No input provided. Exiting.")
        return

    print("\n🤖 Generating PyVnt tree...")
    try:
        pyvnt_code = get_completion(user_input)
        
        print("\n✅ Generated Code:\n")
        print("-" * 50)
        print(pyvnt_code)
        print("-" * 50)

        print("\n🚀 Executing...\n")
        
     
        import ast
        try:
            ast.parse(pyvnt_code)  
            print("✅ Syntax validation passed")
        except SyntaxError as e:
            print(f"❌ Syntax error in generated code: {e}")
            return
            
     
        exec(pyvnt_code, globals())
        print("\n✅ Execution completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
