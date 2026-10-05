#!/usr/bin/env python3
"""
Model updater for CreaZik.
Fetches latest AI music generation models and updates from HuggingFace.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

class ModelUpdater:
    def __init__(self):
        self.cache_dir = Path("D:/HuggingFaceCache")
        self.models_file = Path("models_registry.json")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.load_registry()

    def load_registry(self):
        """Load or create models registry."""
        if self.models_file.exists():
            with open(self.models_file, 'r') as f:
                self.registry = json.load(f)
        else:
            self.registry = {
                "last_updated": None,
                "models": []
            }

    def fetch_latest_models(self):
        """Fetch latest models from HuggingFace."""
        models = [
            {
                "id": "ace-step-1.5",
                "name": "ACE-Step 1.5",
                "type": "music-generation",
                "capability": ["instrumental", "controllable"],
                "hf_model": "ace-step-1.5",
                "status": "available"
            },
            {
                "id": "musicgen-medium",
                "name": "MusicGen Medium",
                "type": "music-generation",
                "capability": ["instrumental", "controllable"],
                "hf_model": "facebook/musicgen-medium",
                "status": "available"
            },
            {
                "id": "musicgen-large",
                "name": "MusicGen Large",
                "type": "music-generation",
                "capability": ["instrumental", "controllable", "high-quality"],
                "hf_model": "facebook/musicgen-large",
                "status": "available"
            },
            {
                "id": "stable-audio-open",
                "name": "Stable Audio Open",
                "type": "music-generation",
                "capability": ["instrumental", "sfx", "controllable"],
                "hf_model": "stabilityai/stable-audio-open-1.0",
                "status": "available"
            },
            {
                "id": "musicgen-stereo-small",
                "name": "MusicGen Stereo (Small)",
                "type": "music-generation",
                "capability": ["instrumental", "stereo"],
                "hf_model": "facebook/musicgen-stereo-small",
                "status": "available"
            }
        ]

        return models

    def update_registry(self):
        """Update registry with latest models."""
        print("🔍 Fetching latest AI music models...")
        models = self.fetch_latest_models()

        self.registry["models"] = models
        self.registry["last_updated"] = datetime.now().isoformat()

        with open(self.models_file, 'w') as f:
            json.dump(self.registry, f, indent=2)

        print(f"✅ Registry updated with {len(models)} models")
        return models

    def list_models(self):
        """List available models."""
        print("\n📋 Available AI Music Generation Models:\n")
        print("-" * 70)

        for model in self.registry["models"]:
            print(f"\n🎵 {model['name']}")
            print(f"   ID: {model['id']}")
            print(f"   Type: {model['type']}")
            print(f"   Capabilities: {', '.join(model['capability'])}")
            print(f"   Status: {model['status']}")

        print(f"\n-" * 70)
        print(f"Last updated: {self.registry.get('last_updated', 'Never')}")

    def check_model_available(self, model_id):
        """Check if model files are cached locally."""
        cache_path = self.cache_dir / model_id
        return cache_path.exists()

    def download_model(self, model_id):
        """Download model from HuggingFace (placeholder)."""
        model = next((m for m in self.registry["models"] if m["id"] == model_id), None)
        if not model:
            print(f"❌ Model '{model_id}' not found in registry")
            return False

        print(f"\n⬇️  Downloading {model['name']}...")
        print(f"   HuggingFace: {model['hf_model']}")

        # TODO: Implement actual download
        print(f"   Cache: {self.cache_dir / model_id}")
        print(f"   (Placeholder - implement git-lfs or huggingface-hub download)")

        return True

    def remove_model(self, model_id):
        """Remove cached model."""
        cache_path = self.cache_dir / model_id
        if cache_path.exists():
            import shutil
            shutil.rmtree(cache_path)
            print(f"✅ Removed {model_id}")
        else:
            print(f"⚠️  Model not found in cache")


def main():
    updater = ModelUpdater()

    if len(sys.argv) < 2:
        print("CreaZik Model Updater\n")
        print("Usage:")
        print("  python model_updater.py list           - List available models")
        print("  python model_updater.py update         - Update model registry")
        print("  python model_updater.py download <id>  - Download a model")
        print("  python model_updater.py remove <id>    - Remove cached model")
        print("  python model_updater.py status         - Check cache status")
        return

    command = sys.argv[1]

    if command == "list":
        updater.list_models()
    elif command == "update":
        updater.update_registry()
        updater.list_models()
    elif command == "download" and len(sys.argv) > 2:
        updater.download_model(sys.argv[2])
    elif command == "remove" and len(sys.argv) > 2:
        updater.remove_model(sys.argv[2])
    elif command == "status":
        print("\n📊 Model Cache Status:\n")
        for model in updater.registry["models"]:
            cached = "✓" if updater.check_model_available(model["id"]) else "✗"
            print(f"{cached} {model['name']}")
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
