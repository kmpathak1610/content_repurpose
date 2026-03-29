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
    "twitter": {
        "width": 1280,
        "height": 720,
        "aspect_ratio": "16:9",
        "fps": 30,
        "max_duration": 140,
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

# Caption style presets (similar to Descript/CapCut style panel)
CAPTION_PRESETS = {
    "no_captions": {
        "name": "No Captions",
        "icon": "\u2298",  # no entry symbol
        "font": "Arial",
        "font_size": 42,
        "font_color": "#FFFFFF",
        "font_weight": "bold",
        "outline_width": 0,
        "outline_color": "#000000",
        "bg_color": None,
        "bg_opacity": 0.0,
        "highlight_color": "#00FF00",
        "shadow_offset": 0,
        "shadow_color": "#000000",
        "position": "bottom",
        "word_highlight": False,
        "enabled": False,
    },
    "karaoke": {
        "name": "Karaoke",
        "icon": "\u25b6",  # play symbol
        "font": "Arial",
        "font_size": 42,
        "font_color": "#FFFFFF",
        "font_weight": "bold",
        "outline_width": 2,
        "outline_color": "#000000",
        "bg_color": None,
        "bg_opacity": 0.0,
        "highlight_color": "#00FF00",
        "shadow_offset": 2,
        "shadow_color": "#000000",
        "position": "bottom",
        "word_highlight": True,
        "enabled": True,
    },
    "beasty": {
        "name": "Beasty",
        "icon": "B",
        "font": "Impact",
        "font_size": 48,
        "font_color": "#FFFFFF",
        "font_weight": "bold",
        "outline_width": 4,
        "outline_color": "#000000",
        "bg_color": None,
        "bg_opacity": 0.0,
        "highlight_color": "#00FF00",
        "shadow_offset": 3,
        "shadow_color": "#000000",
        "position": "bottom",
        "word_highlight": True,
        "enabled": True,
    },
    "deep_diver": {
        "name": "Deep Diver",
        "icon": "D",
        "font": "Helvetica",
        "font_size": 32,
        "font_color": "#FFFFFF",
        "font_weight": "normal",
        "outline_width": 1,
        "outline_color": "#000000",
        "bg_color": "#000000",
        "bg_opacity": 0.6,
        "highlight_color": "#FFFFFF",
        "shadow_offset": 0,
        "shadow_color": "#000000",
        "position": "bottom",
        "word_highlight": False,
        "enabled": True,
    },
    "pod_p": {
        "name": "Pod P",
        "icon": "P",
        "font": "Arial",
        "font_size": 44,
        "font_color": "#FF69B4",
        "font_weight": "bold",
        "outline_width": 2,
        "outline_color": "#000000",
        "bg_color": None,
        "bg_opacity": 0.0,
        "highlight_color": "#FF1493",
        "shadow_offset": 2,
        "shadow_color": "#000000",
        "position": "bottom",
        "word_highlight": True,
        "enabled": True,
    },
    "youshaei": {
        "name": "Youshaei",
        "icon": "Y",
        "font": "Arial",
        "font_size": 42,
        "font_color": "#FFFFFF",
        "font_weight": "bold",
        "outline_width": 3,
        "outline_color": "#000000",
        "bg_color": "#00BFFF",
        "bg_opacity": 0.7,
        "highlight_color": "#00FF00",
        "shadow_offset": 2,
        "shadow_color": "#000000",
        "position": "bottom",
        "word_highlight": True,
        "enabled": True,
    },
    "mozi": {
        "name": "Mozi",
        "icon": "M",
        "font": "Georgia",
        "font_size": 40,
        "font_color": "#FFFFFF",
        "font_weight": "bold",
        "outline_width": 2,
        "outline_color": "#333333",
        "bg_color": "#FFD700",
        "bg_opacity": 0.8,
        "highlight_color": "#FFD700",
        "shadow_offset": 2,
        "shadow_color": "#000000",
        "position": "bottom",
        "word_highlight": True,
        "enabled": True,
    },
    "neon": {
        "name": "Neon",
        "icon": "N",
        "font": "Arial",
        "font_size": 44,
        "font_color": "#00FFFF",
        "font_weight": "bold",
        "outline_width": 0,
        "outline_color": "#000000",
        "bg_color": None,
        "bg_opacity": 0.0,
        "highlight_color": "#FF00FF",
        "shadow_offset": 4,
        "shadow_color": "#00FFFF",
        "position": "bottom",
        "word_highlight": True,
        "enabled": True,
    },
    "minimal": {
        "name": "Minimal",
        "icon": "-",
        "font": "Helvetica",
        "font_size": 28,
        "font_color": "#FFFFFF",
        "font_weight": "normal",
        "outline_width": 0,
        "outline_color": "#000000",
        "bg_color": "#000000",
        "bg_opacity": 0.5,
        "highlight_color": "#FFFFFF",
        "shadow_offset": 0,
        "shadow_color": "#000000",
        "position": "bottom",
        "word_highlight": False,
        "enabled": True,
    },
}

DEFAULT_CAPTION_PRESET = "beasty"

# Logo settings
LOGO_DEFAULTS = {
    "position": "bottom_left",  # bottom_left, bottom_right, top_left, top_right
    "width": 150,  # pixels
    "opacity": 0.8,
    "margin": 20,  # pixels from edge
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
