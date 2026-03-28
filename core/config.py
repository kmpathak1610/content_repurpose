"""
Configuration module for Video Repurposing Application
Centralized settings and defaults
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
EXPORTS_DIR = BASE_DIR / "exports"
CACHE_DIR = BASE_DIR / "cache"

# Ensure directories exist
ASSETS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# Video settings
DEFAULT_VIDEO_CODEC = "libx264"
DEFAULT_AUDIO_CODEC = "aac"
DEFAULT_FORMAT = "mp4"

# Export presets
EXPORT_PRESETS = {
    "reels": {
        "width": 1080,
        "height": 1920,
        "aspect_ratio": "9:16",
        "fps": 30,
        "max_duration": 90,  # 90 seconds for Instagram Reels
    },
    "shorts": {
        "width": 1080,
        "height": 1920,
        "aspect_ratio": "9:16",
        "fps": 30,
        "max_duration": 60,  # 60 seconds for YouTube Shorts
    },
    "tiktok": {
        "width": 1080,
        "height": 1920,
        "aspect_ratio": "9:16",
        "fps": 30,
        "max_duration": 180,  # 3 minutes for TikTok
    },
    "landscape": {
        "width": 1920,
        "height": 1080,
        "aspect_ratio": "16:9",
        "fps": 30,
        "max_duration": 600,
    },
}

# AI Settings
WHISPER_MODELS = {
    "tiny": {"size": "39M", "speed": "fastest", "accuracy": "lowest"},
    "base": {"size": "74M", "speed": "fast", "accuracy": "basic"},
    "small": {"size": "244M", "speed": "medium", "accuracy": "good"},
    "medium": {"size": "769M", "speed": "slow", "accuracy": "better"},
    "large": {"size": "1550M", "speed": "slowest", "accuracy": "best"},
}
DEFAULT_WHISPER_MODEL = "small"

# Clip detection settings
CLIP_DETECTION = {
    "min_clip_duration": 20,
    "max_clip_duration": 60,
    "default_num_clips": 5,
    "hook_detection": {
        "keywords": [
            "shocking",
            "truth",
            "secret",
            "actually",
            "real",
            "listen",
            "wait",
            "believe",
            "never",
            "always",
            "warning",
            "happened",
            "mistake",
            "wrong",
            "right",
        ],
        "max_hook_duration": 3.0,
    },
    "scoring_weights": {
        "hook": 0.3,
        "emotion": 0.2,
        "length": 0.1,
        "topic_shift": 0.2,
        "pauses": 0.2,
    },
}

# Subtitle settings
SUBTITLE_STYLES = {
    "burned": {
        "font": "Arial",
        "font_size": 24,
        "font_color": "white",
        "background": "black",
    },
    "styled": {
        "font": "Arial",
        "font_size": 32,
        "font_color": "white",
        "outline": 2,
        "outline_color": "black",
    },
}

# LLM Settings
LLM_PROVIDERS = ["openai", "anthropic", "ollama", "llama.cpp"]
DEFAULT_LLM_PROVIDER = "openai"

# UI Settings
WINDOW_MIN_SIZE = (1200, 800)
DEFAULT_LAYOUT = "horizontal"  # or "vertical"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance
USE_GPU = True
CACHE_TRANSCRIPTS = True
ASYNC_PROCESSING = True
