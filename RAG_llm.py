from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.retrieval_qa.base import RetrievalQA
from together import Together
import sys
import time

class OpenFOAMRAGChatBot:
    def __init__(self):
        print("🔄 Initializing OpenFOAM RAG Assistant...")
        print("   Loading embeddings model...")
        self.embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
        
        print("   Loading vector store...")
        self.vectorstore = FAISS.load_local("openfoam_vectorstore", self.embedding, allow_dangerous_deserialization=True)
        
        print("   Setting up retriever...")
        self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        
        print("   Connecting to Together AI...")
        self.client = Together(api_key="97eb242cb120beb901b23eff5a2811de094d3b7377d2269fa1d80e545bf7e877")
        
        self.conversation_history = []
        self.system_prompt_template = """You are a highly experienced OpenFOAM practitioner with decades of expertise in CFD simulations and OpenFOAM case files. 

You have access to a comprehensive database of 800+ real OpenFOAM configuration files covering various solvers, applications, and scenarios.

Based on the provided context from actual OpenFOAM cases, provide accurate, practical, and detailed responses. When generating configuration files, use proper OpenFOAM syntax and include helpful comments.

Context from OpenFOAM database:
{context}

Always reference which specific case files or examples you're drawing from when possible."""

        print("✅ RAG Assistant initialized successfully!\n")
    
    def print_welcome_message(self):
        print("=" * 70)
        print("🧠 OpenFOAM RAG (Retrieval-Augmented Generation) Assistant")
        print("=" * 70)
        print("Welcome! I'm your enhanced OpenFOAM assistant with access to 800+ configuration files.")
        print("\n🔍 What makes me special:")
        print("  • Access to real OpenFOAM case database (800+ files)")
        print("  • Context-aware responses based on actual configurations")
        print("  • References to specific source files")
        print("  • Best practices from diverse OpenFOAM applications")
        print("\n📚 I can help with:")
        print("  • Generate configuration files based on real examples")
        print("  • Find similar cases in the database")
        print("  • Explain configurations with context")
        print("  • Suggest best practices from the knowledge base")
        print("\n⌨️  Commands:")
        print("  • Type 'exit' or 'quit' to end the chat")
        print("  • Type 'clear' to clear conversation history")
        print("  • Type 'help' to see example questions")
        print("  • Type 'sources' to see sources from last query")
        print("-" * 70)
    
    def print_help(self):
        print("\n📚 OpenFOAM RAG Assistant - Example Questions:")
        print("\n🔧 Configuration Generation:")
        print("  • Generate a blockMeshDict for flow around a cylinder")
        print("  • Create controlDict for LES turbulence simulation")
        print("  • Show me fvSchemes for compressible flow")
        print("  • Generate fvSolution for multiphase simulation")
        print("\n🔍 Case-based Queries:")
        print("  • Find examples of combustion cases in the database")
        print("  • Show me how pitzDaily case is configured")
        print("  • What boundary conditions are used in cavity cases?")
        print("  • How is turbulence handled in motorBike case?")
        print("\n🎯 Specific Applications:")
        print("  • Heat transfer setup for heated duct")
        print("  • Multiphase configuration for dam break")
        print("  • Combustion setup for engine simulation")
        print("  • Mesh generation for complex geometries")
        print()
    
    def get_user_input(self):
        try:
            return input("\n🤖 You: ").strip()
        except KeyboardInterrupt:
            print("\n\nThank you for using OpenFOAM RAG Assistant! 👋")
            sys.exit(0)
    
    def retrieve_context(self, query):
        """Retrieve relevant documents from the vector store"""
        try:
            docs = self.retriever.invoke(query)  # Updated method
            context = "\n".join([doc.page_content for doc in docs])
            sources = [doc.metadata.get("source", "Unknown") for doc in docs]
            return context, sources, docs
        except Exception as e:
            print(f"⚠️  Warning: Could not retrieve context - {str(e)}")
            return "", [], []
    
    def get_completion(self, query, context):
        """Get completion from Together AI with context"""
        system_prompt = self.system_prompt_template.format(context=context)
        
        # Prepare messages including conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history (keep last 10 exchanges)
        recent_history = self.conversation_history[-20:]
        messages.extend(recent_history)
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=messages,
                temperature=0.1,  # Lower temperature for more consistent responses
                max_tokens=1500
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Error getting AI response: {str(e)}"
    
    def send_message(self, user_message):
        # Show retrieval process
        print("\n🔍 Searching knowledge base...")
        context, sources, docs = self.retrieve_context(user_message)
        
        if context:
            print(f"📚 Found {len(docs)} relevant documents")
        
        print("🤖 Generating response...")
        
        # Get AI response with context
        assistant_response = self.get_completion(user_message, context)
        
        # Store in conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        # Store sources for later reference
        self.last_sources = sources
        
        return assistant_response, sources
    
    def clear_history(self):
        self.conversation_history = []
        self.last_sources = []
        print("✅ Conversation history cleared!")
    
    def show_sources(self):
        if hasattr(self, 'last_sources') and self.last_sources:
            print("\n📄 Sources from last query:")
            for i, source in enumerate(self.last_sources, 1):
                print(f"   {i}. {source}")
        else:
            print("No sources available. Ask a question first!")
    
    def run_chat(self):
        self.print_welcome_message()
        
        while True:
            user_input = self.get_user_input()
            
            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Thank you for using OpenFOAM RAG Assistant. Goodbye!")
                break
            
            elif user_input.lower() == 'clear':
                self.clear_history()
                continue
            
            elif user_input.lower() == 'help':
                self.print_help()
                continue
            
            elif user_input.lower() == 'sources':
                self.show_sources()
                continue
            
            elif not user_input:
                print("Please enter a question or command.")
                continue
            
            # Get RAG response
            response, sources = self.send_message(user_input)
            
            # Print response with formatting
            print("\n🧠 OpenFOAM RAG Assistant:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            
            # Show sources
            if sources:
                print(f"\n📚 Based on {len(sources)} reference files:")
                for i, source in enumerate(sources[:3], 1):  # Show first 3 sources
                    print(f"   {i}. {source}")
                if len(sources) > 3:
                    print(f"   ... and {len(sources) - 3} more (type 'sources' to see all)")

def main():
    """Main function to run the RAG chat interface"""
    try:
        chatbot = OpenFOAMRAGChatBot()
        chatbot.run_chat()
    except FileNotFoundError:
        print("❌ Error: Vector store not found!")
        print("Please run 'parser.py' first to create the vector store.")
    except Exception as e:
        print(f"❌ Error initializing RAG system: {str(e)}")

if __name__ == "__main__":
    main()
