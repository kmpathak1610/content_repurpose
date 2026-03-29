# Video Repurposing Studio - Project Plan

## Overview

A local-first CPU-optimized desktop application that automates repurposing long-form
video content into short-form clips optimized for social media platforms (Instagram
Reels, YouTube Shorts, TikTok). Built with PySide6 (Qt), Whisper for transcription
(CPU mode), ffmpeg for video processing, and optional LLM integration for enhanced
clip detection.

## Architecture

```
main.py (entry point)
  └── ui/main_window.py (MainWindow - orchestrates all modules)
        ├── core/downloader.py     -- VideoDownloader (YouTube + local)
        ├── core/transcriber.py    -- TranscriptionEngine (Whisper CPU + SRT parsing)
        ├── core/clip_detector.py  -- ClipDetector (rule-based + LLM fallback)
        ├── core/editor_engine.py  -- TranscriptEditor (Descript-like editing)
        ├── core/renderer.py       -- VideoRenderer (ffmpeg clip + subtitle export)
        ├── core/config.py         -- Configuration (presets, models, settings)
        ├── ai/llm_interface.py    -- LLMInterface (OpenAI, Anthropic, Ollama)
        └── ui/dialogs.py          -- URLDialog, ExportDialog, EditClipDialog
```

## User Workflow

1. **Load Video** -- Open local file or download from YouTube (yt-dlp)
2. **Transcribe** -- Whisper speech-to-text (CPU) OR YouTube subtitle download (SRT)
3. **Detect Clips** -- Rule-based scoring + optional LLM analysis + duration fallback
4. **Edit Clips** -- Adjust title, timing, hook via EditClipDialog
5. **Export** -- Two-pass ffmpeg: extract clip -> burn subtitles (platform presets)

## Core Components

### Video Input (`core/downloader.py`)
- YouTube download with yt-dlp (format fallback chain)
- Local file loading via ffmpeg probe
- YouTube subtitle download (manual + auto-generated)
- SRT parsing into Whisper-compatible segment format

### Transcription (`core/transcriber.py`)
- Whisper model running on CPU (default: small, ~244MB)
- Language parameter support for accurate non-English transcription
- SRT file parsing with offset for clip exports
- Word-level timestamps
- Language selector: 18 languages including Hindi (Devanagari)
- **CPU Note**: Use "tiny" or "base" model for faster transcription; "small" for
  better accuracy; "medium" only if time is not a concern

### Clip Detection (`core/clip_detector.py`)
- Rule-based scoring: hook keywords, emotion, questions, exclamation,
  topic shifts, dramatic pauses, opening sections, numbers/dates
- Language-agnostic signals for non-English content
- LLM-enhanced detection (OpenAI, Anthropic, Ollama) with graceful fallback
- Duration-based fallback when scoring yields zero clips
- Clip merging, ranking, and selection

### Export (`core/renderer.py`)
- Two-pass approach: extract clip -> burn subtitles
- SRT timestamp offset (relative to clip start, not absolute)
- Windows-safe path handling (forward slashes, no drive letter colons in subtitle filter)
- Platform presets: Reels (1080x1920, 90s), Shorts (1080x1920, 60s),
  TikTok (1080x1920, 180s), Landscape (1920x1080), Square (1080x1080)

### AI Integration (`ai/llm_interface.py`)
- OpenAI (gpt-4o), Anthropic (Claude 3), Ollama (local) providers
- Clip detection prompt with JSON response parsing
- Image URL stripping from prompts (avoids "model does not support image input" error)
- ViralIntelligence scoring engine (no LLM required)

### UI (`ui/main_window.py`, `ui/dialogs.py`)
- PySide6/QMediaPlayer video preview with playback controls
- Toolbar: Open, From URL, Language selector, Transcribe, Detect Clips, Export
- Transcript tab (timestamped list) + Detected Clips tab (score, title, time range)
- Export format selector + subtitle checkbox
- Custom dialogs: URLDialog, ExportDialog, SettingsDialog, EditClipDialog

## CPU Performance Considerations

| Whisper Model | Parameters | CPU Time (5-min video) | Accuracy | Recommendation |
|--------------|-----------|----------------------|----------|----------------|
| tiny | 39M | ~30s | Low | Quick drafts only |
| base | 74M | ~60s | Basic | Short English videos |
| **small** | **244M** | **~3min** | **Good** | **Default - best balance** |
| medium | 769M | ~10min | Better | Hindi/non-English (if time permits) |
| large | 1550M | ~20min | Best | Not recommended on CPU |

**Tips for CPU users:**
- Default to "small" model - good accuracy, reasonable speed
- For Hindi/non-English, "small" is usually sufficient; "medium" if quality matters more
- Consider using YouTube subtitle download instead of Whisper when available (instant)
- Export speed depends on ffmpeg, which is generally fast even on CPU

## Tech Stack

| Category | Technology |
|----------|-----------|
| UI Framework | PySide6 (Qt) |
| Video Processing | ffmpeg (subprocess) + ffmpeg-python (probe) |
| Speech-to-Text | openai-whisper (CPU mode) |
| Video Download | yt-dlp |
| LLM Providers | OpenAI API, Anthropic API, Ollama (local) |
| Python | 3.10+ |

## Key Design Decisions

- **Local-first**: All processing on user's machine, no cloud dependency
- **CPU-optimized**: Default Whisper model "small" balances speed/accuracy on CPU
- **LLM-optional**: App works fully with rule-based clip detection
- **Subprocess over ffmpeg-python for subtitles**: Avoids Windows path escaping bugs
- **Two-pass export**: Extract clip first, then burn subtitles (avoids filter chain issues)
- **SRT timestamp offset**: Subtitles relative to clip start (not absolute video time)
- **YouTube subtitle priority**: When SRT files exist, skip Whisper entirely

## Current Limitations

- No async processing (UI freezes during Whisper transcription -- even more impactful on CPU)
- No face-detection smart crop (uses center crop)
- No tests written (pytest in requirements but no test files)
- moviepy/pydub/opencv declared but unused
- Duplicate export preset definitions (config.py vs renderer.py)
- LLM clip scores hard-coded to 0.8 (less nuanced than rule-based)
