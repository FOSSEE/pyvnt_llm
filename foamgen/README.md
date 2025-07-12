# FoamGen

**FoamGen** is an AI-powered command-line tool that streamlines the generation of [OpenFOAM](https://www.openfoam.com/) case files through natural language processing. By leveraging state-of-the-art Large Language Models (LLMs), FoamGen enables engineers and researchers to create complex computational fluid dynamics (CFD) simulations through conversational interfaces.

## Overview

FoamGen bridges the gap between domain expertise and technical implementation by translating natural language descriptions into properly structured OpenFOAM case configurations. The application supports multiple LLM backends and provides both interactive and batch processing modes for maximum flexibility.

## Key Features

- **Intelligent Case Generation**: Convert natural language descriptions into complete OpenFOAM case structures
- **Multi-Model Support**: Compatible with various LLM providers including Meta-Llama and Mistral models
- **Interactive Terminal Interface**: Real-time conversation mode for iterative case development
- **Batch Processing**: Generate multiple cases from command-line queries
- **Configurable Output**: Customizable output directories and model selection
- **API Integration**: Seamless integration with Together AI's model ecosystem

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenFOAM installation (recommended for case validation)
- Together AI API key

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/foamgen.git
   cd foamgen
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### API Key Setup

FoamGen requires a Together AI API key for LLM access. Follow these steps to obtain and configure your API key:

#### Step 1: Create a Together AI Account

1. Navigate to [https://www.together.ai/](https://www.together.ai/)
2. Click **"Sign Up"** in the top right corner
3. Choose your preferred registration method:
   - **Email**: Enter your email address and create a password
   - **Google**: Sign up using your Google account
   - **GitHub**: Sign up using your GitHub account
4. Verify your email address if required
5. Complete your profile setup

#### Step 2: Access Your API Key

1. Once logged in, navigate to your **Dashboard**
2. Click on **"API Keys"** in the left sidebar menu
3. Click **"Create new key"** or **"+ New API Key"**
4. Provide a descriptive name for your key (e.g., "FoamGen Development")
5. Click **"Create"** to generate your API key
6. **Important**: Copy your API key immediately and store it securely - it will only be displayed once

#### Step 3: Configure FoamGen

Choose one of the following methods to configure your API key:

**Method 1: Command-line configuration (Recommended)**
```bash
python3 main.py set-key <your_together_api_key>
```

**Method 2: Environment variable**
```bash
export TOGETHER_API_KEY=<your_together_api_key>
```

**Method 3: Add to your shell profile (Persistent)**
```bash
echo 'export TOGETHER_API_KEY=<your_together_api_key>' >> ~/.bashrc
source ~/.bashrc
```

> **Security Note**: Never commit your API key to version control. Keep it secure and rotate it periodically.

### Model Configuration

List available models:
```bash
python3 main.py list-models
```

Set default model:
```bash
python3 main.py set-model <model_name>
```

## Usage

### Command-Line Interface

**Basic case generation:**
```bash
python3 main.py ask-q "Create a lid-driven cavity case with Reynolds number 1000"
```

**Specify model and output directory:**
```bash
python3 main.py ask-q "Generate a heat transfer case" \
  --model meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo \
  --output ./simulation_cases/heat_transfer
```

### Interactive Mode

Launch the interactive shell for conversational case development:
```bash
python3 main.py interactive
```

The interactive mode allows for iterative refinement of case parameters through natural language dialogue.

## Architecture

### System Components

```
foamgen/
├── main.py                 # Entry point and CLI interface
├── requirements.txt        # Python dependencies
├── app/
│   └── rag_llm.py         # LLM integration and processing logic
├── openfoam_vectorstore/   # Knowledge base and embeddings
│   ├── index.faiss        # Vector search index
│   └── index.pkl          # Serialized metadata
└── README.md              # Documentation
```

### Technical Stack

- **Language Models**: Together AI API integration
- **Vector Storage**: FAISS for efficient similarity search
- **Framework**: LangChain for LLM orchestration
- **Interface**: Command-line interface with argparse

## System Requirements

- **Python**: 3.8+ (3.9+ recommended)
- **Memory**: Minimum 4GB RAM for vector operations
- **Storage**: 500MB for dependencies and vector store
- **Network**: Internet connection for API access

## Contributing

We welcome contributions to FoamGen. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Implement changes with appropriate tests
4. Submit a pull request with detailed description

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support and Documentation

For technical support, bug reports, or feature requests, please visit our [GitHub Issues](https://github.com/<your-username>/foamgen/issues) page.

## Acknowledgments

FoamGen builds upon the excellent work of several open-source projects:

- [OpenFOAM Foundation](https://www.openfoam.com/) - The open-source CFD toolbox
- [Together AI](https://www.together.ai/) - LLM infrastructure and API services
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework
- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search library

---

**Accelerate your OpenFOAM workflow with intelligent case generation.**