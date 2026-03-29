# Video Repurposing Studio - Project Plan

## Overview

A local-first CPU-optimized desktop application that automates repurposing long-form
video content into short-form clips optimized for social media platforms (Instagram
Reels, YouTube Shorts, TikTok, Twitter/X). Built with PySide6 (Qt), Whisper for
transcription (CPU mode), ffmpeg for video processing, optional LLM integration for
enhanced clip detection, and social media posting capabilities.

## Architecture

```
main.py (entry point)
  └── ui/main_window.py (MainWindow - orchestrates all modules)
        ├── core/downloader.py     -- VideoDownloader (YouTube, Twitter/X, local)
        ├── core/transcriber.py    -- TranscriptionEngine (Whisper CPU + SRT parsing)
        ├── core/clip_detector.py  -- ClipDetector (rule-based + LLM fallback)
        ├── core/editor_engine.py  -- TranscriptEditor (Descript-like editing)
        ├── core/renderer.py       -- VideoRenderer (ffmpeg clip + subtitle export)
        ├── core/config.py         -- Configuration (presets, models, settings)
        ├── core/poster.py         -- SocialMediaPoster (Twitter/X API posting)
        ├── ai/llm_interface.py    -- LLMInterface (OpenAI, Anthropic, Ollama)
        └── ui/dialogs.py          -- URLDialog, ExportDialog, EditClipDialog,
                                      LogoDialog, SubtitleStyleDialog, PostDialog
```

## User Workflow

1. **Load Video** -- Open local file, download from YouTube, or download from Twitter/X
2. **Transcribe** -- Whisper speech-to-text (CPU) OR YouTube subtitle download (SRT)
3. **Detect Clips** -- Rule-based scoring + optional LLM analysis + duration fallback
4. **Edit Clips** -- Adjust title, timing, hook; set logo overlay; customize subtitle style
5. **Export** -- Two-pass ffmpeg: extract clip -> burn subtitles + logo (platform presets)
6. **Post** -- Direct upload to Twitter/X with title, description, hashtags

## Core Components

### Video Input (`core/downloader.py`)
- YouTube download with yt-dlp (format fallback chain)
- Twitter/X video download with yt-dlp (handles tweet URLs, short URLs)
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
- Two-pass approach: extract clip -> burn subtitles + logo overlay
- Custom logo overlay (position, size, opacity configurable)
- Subtitle styling: background color, font size, font color, position presets
- SRT timestamp offset (relative to clip start, not absolute)
- Windows-safe path handling (forward slashes, no drive letter colons in subtitle filter)
- Platform presets: Reels (1080x1920, 90s), Shorts (1080x1920, 60s),
  TikTok (1080x1920, 180s), Twitter/X (1280x720, 140s), Landscape (1920x1080), Square (1080x1080)

### AI Integration (`ai/llm_interface.py`)
- OpenAI (gpt-4o), Anthropic (Claude 3), Ollama (local) providers
- Clip detection prompt with JSON response parsing
- Image URL stripping from prompts (avoids "model does not support image input" error)
- ViralIntelligence scoring engine (no LLM required)

### Social Media Posting (`core/poster.py`)
- Twitter/X API v2 integration (OAuth2 user authentication)
- Video upload via Twitter media endpoint
- Configurable tweet text: title, description, hashtags, custom message
- Post with optional video thumbnail preview
- Rate limit handling and retry logic

### UI (`ui/main_window.py`, `ui/dialogs.py`)
- PySide6/QMediaPlayer video preview with playback controls
- Toolbar: Open, From URL, Language selector, Transcribe, Detect Clips, Export, Post
- Transcript tab (timestamped list) + Detected Clips tab (score, title, time range)
- Export format selector + subtitle checkbox + logo checkbox
- Custom dialogs: URLDialog, ExportDialog, SettingsDialog, EditClipDialog,
  LogoDialog (upload/select logo, position/size), SubtitleStyleDialog (background color,
  font color, font size, position), PostDialog (tweet text, hashtags, preview)

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
| Video Download | yt-dlp (YouTube, Twitter/X) |
| Social Media API | tweepy (Twitter/X API v2) |
| LLM Providers | OpenAI API, Anthropic API, Ollama (local) |
| Python | 3.10+ |

## Key Design Decisions

- **Local-first**: All processing on user's machine, no cloud dependency
- **CPU-optimized**: Default Whisper model "small" balances speed/accuracy on CPU
- **LLM-optional**: App works fully with rule-based clip detection
- **Subprocess over ffmpeg-python for subtitles**: Avoids Windows path escaping bugs
- **Two-pass export**: Extract clip first, then burn subtitles + logo (avoids filter chain issues)
- **SRT timestamp offset**: Subtitles relative to clip start (not absolute video time)
- **YouTube subtitle priority**: When SRT files exist, skip Whisper entirely
- **Branding overlay**: Logo burned into video at export time (not at edit time) for flexibility
- **OAuth2 for Twitter/X**: User authenticates via browser, token stored locally

## Social Media Integration

### Supported Platforms (Current & Planned)

| Platform | Download | Post | Status |
|----------|----------|------|--------|
| YouTube | Yes (yt-dlp) | No | Implemented |
| Twitter/X | Yes (yt-dlp) | Yes (tweepy) | Planned |
| Instagram | No | Planned | Future |
| TikTok | No | Planned | Future |
| Facebook | No | Planned | Future |

### Posting Flow
1. User exports clip with logo and subtitle styling
2. Click "Post" button -> PostDialog opens
3. User enters tweet text, hashtags, description
4. Video uploaded to Twitter media endpoint
5. Tweet created with video attached
6. Success confirmation with tweet URL

## Current Limitations

- No async processing (UI freezes during Whisper transcription -- even more impactful on CPU)
- No face-detection smart crop (uses center crop)
- No tests written (pytest in requirements but no test files)
- moviepy/pydub/opencv declared but unused
- Duplicate export preset definitions (config.py vs renderer.py)
- LLM clip scores hard-coded to 0.8 (less nuanced than rule-based)
