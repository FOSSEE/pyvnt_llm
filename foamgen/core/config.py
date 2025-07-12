"""
FoamGenConfig: Handles configuration management for FoamGen, including API key storage and retrieval.
"""

import os
import json
from pathlib import Path

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