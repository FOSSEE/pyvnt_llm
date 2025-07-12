---

## FoamGen

FoamGen is a command-line tool that lets you generate OpenFOAM case files simply by describing your simulation in natural language. Powered by large language models (LLMs) via the Together AI API, FoamGen can answer OpenFOAM-related questions, generate case files, and help automate CFD workflows. It supports interactive and batch modes, multiple LLM models, and easy API key management.

- **Example usage:**
  ```bash
  cd foamgen
  python3 main.py ask-q "Create a lid-driven cavity case with Reynolds number 1000"
  ```

- **Features:**
  - Natural language to OpenFOAM case file generation
  - Multi-model support (Meta-Llama, Mistral, etc.)
  - Interactive and batch CLI
  - API key management and model configuration

- **Full documentation:**  
  [FoamGen README](https://github.com/FOSSEE/pyvnt_llm/blob/main/foamgen/README.md)

---

## OpenFOAM ↔ pyvnt Converter

The converter is an AI-powered tool for seamless conversion between OpenFOAM case files and pyvnt Python code structures. Using Google Gemini AI, it can translate in both directions with high accuracy and proper formatting. The converter features an interactive CLI, context file support, and organized output directories.

- **Example usage:**
  ```bash
  cd converter
  python3 converter.py
  ```

- **Features:**
  - Bidirectional conversion: OpenFOAM case files ↔ pyvnt Python code
  - Uses Google Gemini AI for intelligent, context-aware conversions
  - Interactive CLI with animated loading indicators
  - Context file support for improved accuracy
  - Organized output directories

- **Full documentation:**  
  [Converter README](https://github.com/FOSSEE/pyvnt_llm/blob/main/converter/README.md)

---

Both tools are designed to accelerate and simplify CFD workflows by leveraging the latest in AI technology.
