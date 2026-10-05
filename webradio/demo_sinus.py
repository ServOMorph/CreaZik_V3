#!/usr/bin/env python3
"""
Demo mode - Génère des fichiers WAV de test pour explorer l'UI.
Utile pour tester le explorateur de playlists sans ACE-Step réel.
"""

import json
import os
import sys
import struct
import wave
from pathlib import Path
from datetime import datetime
import random

class DemoPlaylistRunner:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.output_dir = Path(self.config["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "config_file": config_path,
            "mode": "demo",
            "note": "Fichiers WAV de test générés pour démonstration UI",
            "generations": []
        }

    def run(self):
        """Execute demo playlist generation."""
        print(f"🎵 Starting CreaZik Playlist (DEMO MODE)")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Test cases: {len(self.config['test_cases'])}")
        print("-" * 60)

        for i, test_case in enumerate(self.config["test_cases"], 1):
            print(f"\n[{i}/{len(self.config['test_cases'])}] Generating: {test_case['name']}")
            self._generate_demo_track(test_case)

        self._save_results()
        print(f"\n✅ Demo playlist complete!")
        print(f"📂 Results saved to: {self.output_dir}")
        print(f"🌐 Open ui.html to explore results\n")

    def _save_results(self):
        """Save playlist results metadata."""
        results_file = self.output_dir / "playlist_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        # Also create a summary
        summary_file = self.output_dir / "PLAYLIST.md"
        with open(summary_file, 'w') as f:
            f.write("# CreaZik Playlist Results (DEMO)\n\n")
            f.write(f"**Timestamp:** {self.results['timestamp']}\n")
            f.write(f"**Mode:** {self.results['mode']}\n\n")
            f.write("## Generated Tracks\n\n")
            for gen in self.results["generations"]:
                f.write(f"- **{gen['name']}** ({gen['status']})\n")
                f.write(f"  - Prompt: {gen['prompt']}\n")
                f.write(f"  - File: {gen['output_file']}\n\n")

    def _generate_demo_track(self, test_case):
        """Generate a dummy WAV file for testing UI."""
        track_id = int(test_case['id'])
        output_file = self.output_dir / f"{track_id:02d}_{test_case['name'].replace(' ', '_')}.wav"
        duration = test_case.get('duration', 30)

        result = {
            "test_case_id": test_case["id"],
            "name": test_case["name"],
            "prompt": test_case["prompt"],
            "type": test_case["type"],
            "duration": duration,
            "output_file": str(output_file),
            "status": "generated",
            "generated_at": datetime.now().isoformat()
        }

        try:
            self._create_demo_wav(str(output_file), duration, test_case["id"])
            print(f"  ✓ Generated: {output_file.name}")
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"  ✗ Failed: {e}")

        self.results["generations"].append(result)

    def _create_demo_wav(self, filepath, duration_seconds=30, track_id=1):
        """Create a simple WAV file for testing."""
        sample_rate = 44100
        num_samples = sample_rate * duration_seconds

        # Vary frequency slightly by track for audio difference
        base_freq = 440 + (int(track_id) * 50)  # A4 + variation

        # Create simple sine wave
        frames = []
        for i in range(num_samples):
            # Mix two frequencies for variation
            freq1 = base_freq
            freq2 = base_freq * 1.5

            sample = 0.3 * (
                math.sin(2 * math.pi * freq1 * i / sample_rate) * 0.7 +
                math.sin(2 * math.pi * freq2 * i / sample_rate) * 0.3
            )

            # Fade in/out
            if i < sample_rate * 0.5:
                sample *= (i / (sample_rate * 0.5))
            elif i > num_samples - sample_rate * 0.5:
                sample *= ((num_samples - i) / (sample_rate * 0.5))

            # Convert to 16-bit PCM
            value = int(sample * 32767)
            frames.append(struct.pack('<h', value))

        # Write WAV file
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(frames))


if __name__ == "__main__":
    # Need to import math for demo
    import math

    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    runner = DemoPlaylistRunner(config_file)
    runner.run()
