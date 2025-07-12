"""
Model utilities: List and set available LLM models for FoamGen.
"""

from .config import FoamGenConfig

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