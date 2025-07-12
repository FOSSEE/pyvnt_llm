"""
ask_question: Handles user queries and generates OpenFOAM case files using the LLM pipeline.
"""

from pathlib import Path
import time
from typing import Optional
from .config import FoamGenConfig
from .spinner import LoadingSpinner
from app.rag_llm import run_rag_pipeline

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

    spinner = LoadingSpinner("Generating OpenFOAM case files")

    try:
        spinner.start("🔄 Connecting to AI model")
        time.sleep(0.5)
        spinner.stop()
        spinner.start("🧠 Analyzing your requirements")
        time.sleep(0.8)
        spinner.stop()
        spinner.start("⚙️  Generating case files")

        response, docs = run_rag_pipeline(question, api_key, selected_model)

        spinner.stop("Case files generated successfully!")

        print("\n📋 Generated OpenFOAM Case:")
        print("=" * 60)
        print(response)
        print("=" * 60)

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            response_file = output_path / "generated_case.txt"
            with open(response_file, 'w') as f:
                f.write(f"Question: {question}\n")
                f.write(f"Model: {selected_model}\n")
                f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n")
                f.write(f"Response:\n{response}\n")
            print(f"💾 Response saved to: {response_file}")

        if docs:
            print(f"📚 Retrieved {len(docs)} relevant documents from knowledge base")

    except KeyboardInterrupt:
        spinner.stop("❌ Operation cancelled by user")
        print("\nOperation cancelled.")
    except Exception as e:
        spinner.stop("❌ Error occurred")
        print(f"❌ Error generating response: {e}")
        print("Please check your API key and internet connection.")