#!/usr/bin/env python3
"""
FoamGen - OpenFOAM Case File Generator
Main entry point for the CLI application.
"""

import argparse
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.banner import print_banner
from core.ask import ask_question
from core.models import list_models, set_default_model
from core.config import FoamGenConfig
from core.interactive import interactive_mode

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

if __name__ == "__main__":
    main()