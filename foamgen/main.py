#!/usr/bin/env python3
"""
FoamGen - OpenFOAM Case File Generator
A terminal-based application for generating OpenFOAM case files using LLMs
"""

import argparse
import os
import sys
from pathlib import Path
import json
import time
import threading
from typing import Optional

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rag_llm import run_rag_pipeline

class LoadingSpinner:
    """A beautiful loading spinner for terminal"""
    
    def __init__(self, message="Loading"):
        self.message = message
        self.spinning = False
        self.thread = None
        # Different spinner styles
        self.spinners = {
            'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'bars': ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▂'],
            'arrows': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
            'clock': ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛'],
            'brain': ['🧠', '💭', '💡', '⚡', '🔥', '✨'],
            'gears': ['⚙️ ', '🔧', '⚡', '💻', '🤖', '🎯']
        }
        self.current_spinner = self.spinners['gears']
    
    def _spin(self):
        """Internal spinning method"""
        idx = 0
        while self.spinning:
            spinner_char = self.current_spinner[idx % len(self.current_spinner)]
            # Clear line and print spinner
            print(f'\r{spinner_char} {self.message}...', end='', flush=True)
            time.sleep(0.2)
            idx += 1
    
    def start(self, message=None):
        """Start the spinner"""
        if message:
            self.message = message
        self.spinning = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, final_message=None):
        """Stop the spinner"""
        self.spinning = False
        if self.thread:
            self.thread.join()
        # Clear the line
        print('\r' + ' ' * 80, end='')
        print('\r', end='')
        if final_message:
            print(f'✅ {final_message}')

class FoamGenConfig:
    """Configuration management for FoamGen"""
    
    def __init__(self):
        self.config_file = Path.home() / ".foamgen_config.json"
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        return {
            "api_key": "",
            "default_model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "models": [
                "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
                "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "mistralai/Mistral-7B-Instruct-v0.1"
            ]
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_api_key(self) -> str:
        """Get API key from config or environment"""
        api_key = self.config.get("api_key")
        if not api_key:
            api_key = os.getenv("TOGETHER_API_KEY")
        return api_key or ""
    
    def set_api_key(self, api_key: str):
        """Set API key in config"""
        self.config["api_key"] = api_key
        self.save_config()

def print_banner():
    """Print FoamGen banner"""
    banner = """
    ███████╗ ██████╗  █████╗ ███╗   ███╗ ██████╗ ███████╗███╗   ██╗
    ██╔════╝██╔═══██╗██╔══██╗████╗ ████║██╔════╝ ██╔════╝████╗  ██║
    █████╗  ██║   ██║███████║██╔████╔██║██║  ███╗█████╗  ██╔██╗ ██║
    ██╔══╝  ██║   ██║██╔══██║██║╚██╔╝██║██║   ██║██╔══╝  ██║╚██╗██║
    ██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║╚██████╔╝███████╗██║ ╚████║
    ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝
    
    OpenFOAM Case File Generator powered by LLMs
    """
    print(banner)

def ask_question(question: str, model: Optional[str] = None, output_dir: Optional[str] = None):
    """Ask a question and generate OpenFOAM case files"""
    config = FoamGenConfig()
    
    # Get API key
    api_key = config.get_api_key()
    if not api_key:
        print("❌ Error: No API key found!")
        print("Please set your Together API key using:")
        print("  python3 main.py set-key <your_api_key>")
        print("Or set the TOGETHER_API_KEY environment variable")
        return
    
    # Use provided model or default
    selected_model = model or config.config["default_model"]
    
    print(f"🤖 Using model: {selected_model}")
    print(f"❓ Question: {question}")
    print("-" * 60)
    
    # Create and start the loading spinner
    spinner = LoadingSpinner("Generating OpenFOAM case files")
    
    try:
        # Start the spinner
        spinner.start("🔄 Connecting to AI model")
        time.sleep(0.5)  # Brief pause for visual effect
        
        spinner.stop()
        spinner.start("🧠 Analyzing your requirements")
        time.sleep(0.8)
        
        spinner.stop()
        spinner.start("⚙️  Generating case files")
        
        # Run the RAG pipeline
        response, docs = run_rag_pipeline(question, api_key, selected_model)
        
        # Stop spinner with success message
        spinner.stop("Case files generated successfully!")
        
        print("\n📋 Generated OpenFOAM Case:")
        print("=" * 60)
        print(response)
        print("=" * 60)
        
        # If output directory is specified, save the response
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save the response
            response_file = output_path / "generated_case.txt"
            with open(response_file, 'w') as f:
                f.write(f"Question: {question}\n")
                f.write(f"Model: {selected_model}\n")
                f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n")
                f.write(f"Response:\n{response}\n")
            
            print(f"💾 Response saved to: {response_file}")
        
        # Show retrieved documents info if available
        if docs:
            print(f"📚 Retrieved {len(docs)} relevant documents from knowledge base")
        
    except KeyboardInterrupt:
        spinner.stop("❌ Operation cancelled by user")
        print("\nOperation cancelled.")
    except Exception as e:
        spinner.stop("❌ Error occurred")
        print(f"❌ Error generating response: {e}")
        print("Please check your API key and internet connection.")

def list_models():
    """List available models"""
    config = FoamGenConfig()
    print("Available models:")
    for i, model in enumerate(config.config["models"], 1):
        default_marker = " (default)" if model == config.config["default_model"] else ""
        print(f"  {i}. {model}{default_marker}")

def set_default_model(model: str):
    """Set default model"""
    config = FoamGenConfig()
    if model in config.config["models"]:
        config.config["default_model"] = model
        config.save_config()
        print(f"✅ Default model set to: {model}")
    else:
        print(f"❌ Model '{model}' not found in available models")
        print("Available models:")
        for m in config.config["models"]:
            print(f"  - {m}")

def set_api_key(api_key: str):
    """Set API key"""
    config = FoamGenConfig()
    config.set_api_key(api_key)
    print("✅ API key saved successfully")

def main():
    parser = argparse.ArgumentParser(
        description="FoamGen - OpenFOAM Case File Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py ask-q "Create a lid-driven cavity case with Reynolds number 1000"
  python3 main.py ask-q "Generate a heat transfer case" --model meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
  python3 main.py ask-q "Create a turbulent flow case" --output ./my_case
  python3 main.py list-models
  python3 main.py set-key your_together_api_key_here
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ask question command
    ask_parser = subparsers.add_parser('ask-q', help='Ask a question to generate OpenFOAM case files')
    ask_parser.add_argument('question', help='Question about OpenFOAM case to generate')
    ask_parser.add_argument('--model', '-m', help='Model to use for generation')
    ask_parser.add_argument('--output', '-o', help='Output directory to save generated files')
    
    # List models command
    subparsers.add_parser('list-models', help='List available models')
    
    # Set default model command
    set_model_parser = subparsers.add_parser('set-model', help='Set default model')
    set_model_parser.add_argument('model', help='Model name to set as default')
    
    # Set API key command
    set_key_parser = subparsers.add_parser('set-key', help='Set Together API key')
    set_key_parser.add_argument('api_key', help='Your Together API key')
    
    # Interactive mode command
    subparsers.add_parser('interactive', help='Start interactive mode')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    if args.command == 'ask-q':
        ask_question(args.question, args.model, args.output)
    elif args.command == 'list-models':
        list_models()
    elif args.command == 'set-model':
        set_default_model(args.model)
    elif args.command == 'set-key':
        set_api_key(args.api_key)
    elif args.command == 'interactive':
        interactive_mode()
    else:
        parser.print_help()

def interactive_mode():
    """Interactive mode for asking multiple questions"""
    print_banner()
    print("🔄 Starting interactive mode...")
    print("Type 'exit' or 'quit' to stop, 'help' for commands")
    print("=" * 60)
    
    config = FoamGenConfig()
    
    while True:
        try:
            user_input = input("\n🚀 FoamGen> ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("👋 Thanks for using FoamGen! Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("\n📖 Available commands:")
                print("  ask <question>     - Ask a question")
                print("  model <model_name> - Switch model")
                print("  models             - List available models")
                print("  clear              - Clear screen")
                print("  exit/quit          - Exit interactive mode")
                continue
            elif user_input.lower() == 'models':
                list_models()
                continue
            elif user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                print_banner()
                continue
            elif user_input.lower().startswith('model '):
                model_name = user_input[6:].strip()
                set_default_model(model_name)
                continue
            elif user_input.lower().startswith('ask '):
                question = user_input[4:].strip()
                if question:
                    ask_question(question)
                else:
                    print("❓ Please provide a question after 'ask'")
                continue
            elif user_input:
                # Treat any other input as a question
                ask_question(user_input)
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for using FoamGen! Goodbye!")
            break
        except EOFError:
            print("\n👋 Thanks for using FoamGen! Goodbye!")
            break

if __name__ == "__main__":
    main()