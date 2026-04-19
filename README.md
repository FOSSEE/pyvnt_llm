# OpenFOAM AI Assistant (PyVNT + LLM)

A Flask-based OpenFOAM assistant that combines:
- LLM chat for OpenFOAM questions and file generation
- RAG-based retrieval over OpenFOAM case files
- OpenFOAM dictionary to PyVNT conversion
- PyVNT-assisted OpenFOAM file generation and explanation

This project includes both a web UI and CLI scripts.

## What This Project Does

- Chat with an OpenFOAM-focused assistant from the browser
- Optionally run in RAG mode using a local FAISS vector store
- Convert OpenFOAM dictionary-style text into generated PyVNT Python code
- Generate OpenFOAM files (for example `controlDict`, `fvSchemes`, `fvSolution`, `blockMeshDict`) from natural-language prompts
- Explain OpenFOAM file content with an LLM

## Main Components

- `app.py`: Flask + Socket.IO web app (main entry point)
- `llm.py`: CLI chat assistant (non-RAG)
- `RAG_llm.py`: CLI chat assistant with retrieval from FAISS vector store
- `converter.py`: CLI converter from OpenFOAM content to PyVNT code
- `parser.py`: Builds FAISS vector store from `.txt` case files
- `pyvnt_llm_integration.py`: LLM wrappers for generate/write/explain workflows
- `templates/`: Web pages (`index.html`, `chat.html`, `converter.html`, `generator.html`)
- `static/`: CSS and analysis images
- `data/`: OpenFOAM text corpus used for retrieval
- `openfoam_vectorstore/`: Saved FAISS index used by RAG mode
- `pyvnt/`: Local PyVNT library source

## Prerequisites

- Python 3.10+ recommended
- Internet access for Together AI API calls
- A Together AI API key

## Quick Start

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install Python dependencies from this repository.

```powershell
pip install -r requirements.txt
```

3. Install web/runtime packages used by the app (if not already present).

```powershell
pip install flask flask-socketio together python-dotenv langchain-community langchain-huggingface faiss-cpu
```

4. Install local PyVNT package (editable mode).

```powershell
pip install -e .\pyvnt
```

5. Set your Together API key.

```powershell
$env:TOGETHER_API_KEY="your_api_key_here"
```

6. Start the web app.

```powershell
python app.py
```

7. Open:

- http://localhost:5000

## Web App Routes

- `/`: Home page
- `/chat`: Chat UI (simple or RAG mode, plus converter output options)
- `/converter`: OpenFOAM to PyVNT conversion page
- `/generator`: AI file generation page

## API Endpoints

- `POST /api/convert`
  - Input: `{ "content": "...openfoam text..." }`
  - Output: generated `pyvnt_code` and optional `tree_output`

- `POST /api/generate_file`
  - Input fields include `prompt`, `file_type`, `mode`, optional `openfoam_content`
  - Modes:
    - `llm_generate`
    - `llm_write`
    - `traditional_write`
    - `traditional_read`

- `POST /api/explain_file`
  - Input: `{ "content": "...openfoam file content..." }`
  - Output: natural-language explanation

- `POST /api/convert_tree`
  - Input: PyVNT code and file metadata
  - Output: generated OpenFOAM dictionary content

## Socket Events (Chat)

- Client emits:
  - `start_chat` with `{ use_rag: boolean }`
  - `send_message` with `{ message: string, output_type: "text"|"convert"|"both" }`
  - `clear_chat`

- Server emits:
  - `connected`, `chat_ready`, `typing`, `message_response`, `chat_cleared`, `error`

## Using RAG Mode

`RAG_llm.py` and web RAG chat require `openfoam_vectorstore/`.

If you need to rebuild embeddings:

1. Ensure your OpenFOAM corpus `.txt` files are in a directory you want to index.
2. Update `DATA_DIR` in `parser.py` to the correct local path.
3. Run:

```powershell
python parser.py
```

This writes a FAISS index to `openfoam_vectorstore/`.

## CLI Usage

Run non-web scripts directly:

```powershell
python llm.py
python RAG_llm.py
python converter.py
```

## Known Caveats

- `requirements.txt` does not currently include all web/runtime dependencies used by `app.py`.
- Several scripts currently contain hardcoded Together API keys (`llm.py`, `RAG_llm.py`, `converter.py`).
- `pyvnt_llm_integration.py` uses `TOGETHER_API_KEY` from environment, which is preferred.
- `parser.py` currently has a machine-specific `DATA_DIR` path and should be adjusted per environment.

## Security Recommendation

Move all API keys to environment variables and remove hardcoded secrets from source files before sharing or deploying.

## Suggested Next Improvements

- Consolidate all dependencies into a single verified `requirements.txt`
- Remove hardcoded keys and load all secrets from `.env`
- Add automated tests for API endpoints
- Add Docker support for reproducible setup

## License

No license file is currently defined in this repository. Add one before distribution if needed.
