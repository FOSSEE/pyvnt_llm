"""
interactive_mode: Provides an interactive shell for FoamGen.
"""

import os
from .banner import print_banner
from .config import FoamGenConfig
from .ask import ask_question
from .models import list_models, set_default_model

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
                ask_question(user_input)

        except KeyboardInterrupt:
            print("\n👋 Thanks for using FoamGen! Goodbye!")
            break
        except EOFError:
            print("\n👋 Thanks for using FoamGen! Goodbye!")
            break