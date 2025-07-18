from together import Together
import sys
import time

class OpenFOAMChatBot:
    def __init__(self):
        # Initialize the Together client
        self.client = Together(api_key="97eb242cb120beb901b23eff5a2811de094d3b7377d2269fa1d80e545bf7e877")
        self.conversation_history = []
        self.system_prompt = """You are a highly knowledgeable OpenFOAM expert and CFD specialist. You help users with:
- Generating OpenFOAM configuration files (blockMeshDict, controlDict, fvSchemes, fvSolution)
- Explaining OpenFOAM concepts and solvers
- Troubleshooting simulation issues
- Best practices for CFD simulations
- Code examples and file structures

Provide clear, practical, and accurate responses. When generating files, include proper OpenFOAM syntax and comments."""
    
    def print_welcome_message(self):
        print("=" * 60)
        print("🌊 OpenFOAM AI Assistant Chat Interface")
        print("=" * 60)
        print("Welcome! I'm your OpenFOAM specialist assistant.")
        print("I can help you with:")
        print("  • Generate configuration files (blockMeshDict, controlDict, etc.)")
        print("  • Explain OpenFOAM concepts and solvers")
        print("  • Troubleshoot simulation issues")
        print("  • Provide CFD best practices")
        print("\nCommands:")
        print("  • Type 'exit' or 'quit' to end the chat")
        print("  • Type 'clear' to clear conversation history")
        print("  • Type 'help' to see this message again")
        print("-" * 60)
    
    def print_help(self):
        print("\n📚 OpenFOAM Assistant Help:")
        print("Example questions you can ask:")
        print("  • Generate a blockMeshDict for a cylinder flow simulation")
        print("  • Create a controlDict for turbulent flow analysis")
        print("  • Explain the difference between PISO and SIMPLE algorithms")
        print("  • How to set up boundary conditions for a pipe flow?")
        print("  • Generate fvSchemes for LES turbulence modeling")
        print("  • What solver should I use for multiphase flow?")
        print()
    
    def get_user_input(self):
        try:
            return input("\n🤖 You: ").strip()
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            sys.exit(0)
    
    def send_message(self, user_message):
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Prepare messages for API call
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history (keep last 10 exchanges to manage token limit)
        recent_history = self.conversation_history[-20:]  # Last 20 messages (10 exchanges)
        messages.extend(recent_history)
        
        try:
            print("\n🔄 Thinking...")
            
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=False
            )
            
            assistant_response = response.choices[0].message.content
            
            # Add assistant response to conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
        except Exception as e:
            return f"❌ Error: {str(e)}\nPlease try again or check your internet connection."
    
    def clear_history(self):
        self.conversation_history = []
        print("✅ Conversation history cleared!")
    
    def run_chat(self):
        self.print_welcome_message()
        
        while True:
            user_input = self.get_user_input()
            
            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Thank you for using OpenFOAM AI Assistant. Goodbye!")
                break
            
            elif user_input.lower() == 'clear':
                self.clear_history()
                continue
            
            elif user_input.lower() == 'help':
                self.print_help()
                continue
            
            elif not user_input:
                print("Please enter a question or command.")
                continue
            
            # Get AI response
            response = self.send_message(user_input)
            
            # Print response with formatting
            print("\n🤖 OpenFOAM Assistant:")
            print("-" * 40)
            print(response)
            print("-" * 40)

def main():
    """Main function to run the chat interface"""
    chatbot = OpenFOAMChatBot()
    chatbot.run_chat()

if __name__ == "__main__":
    main()
