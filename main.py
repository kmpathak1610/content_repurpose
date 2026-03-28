"""
Video Repurposing Studio
========================
A local-first AI video repurposing system with 3 core engines:

1. Content Understanding (AI brain) - Whisper transcription + LLM analysis
2. Clip Extraction (viral moment detection) - AI-powered clip detection
3. Editing + Export (reels + transcript editor) - Descript-like editor

Usage:
    python main.py

Requirements:
    - FFmpeg installed and in PATH
    - Python packages from requirements.txt
    - For AI features: OpenAI API key or Ollama running locally
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import main UI
from ui.main_window import main

# Run the application
if __name__ == "__main__":
    main()