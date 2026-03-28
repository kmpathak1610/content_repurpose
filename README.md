# Video Repurposing Studio

A local-first AI video repurposing system with 3 core engines:

1. **Content Understanding (AI brain)** - Whisper transcription + LLM analysis
2. **Clip Extraction (viral moment detection)** - AI-powered clip detection
3. **Editing + Export (reels + transcript editor)** - Descript-like editor

## Features

### Core Features
- 📥 **Video Input**: Load local files or download from YouTube URLs
- 📝 **Transcription**: Whisper-based local speech-to-text with timestamps
- 🎯 **Viral Clip Detection**: AI-powered detection of engaging moments
- 📱 **Multi-Platform Export**: Reels, Shorts, TikTok, Landscape, Square formats
- 💬 **Subtitle Generation**: Auto-generated subtitles with styling options

### AI Features
- Hook detection and scoring
- Emotion analysis
- Topic segmentation
- LLM-powered clip suggestions (optional)
- Viral intelligence layer

### Desktop Features
- Video preview with playback controls
- Transcript editor (Descript-like)
- Clip management and organization
- Progress tracking

## Installation

### 1. Install FFmpeg
FFmpeg is required for video processing. Download from [ffmpeg.org](https://ffmpeg.org/download.html) or install via:
- Windows: `winget install ffmpeg` or download from gyan.dev
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) AI Setup
For enhanced clip detection with LLM:
- **OpenAI**: Set `OPENAI_API_KEY` environment variable
- **Anthropic**: Set `ANTHROPIC_API_KEY` environment variable
- **Ollama**: Run locally (`ollama serve`)

## Usage

```bash
python main.py
```

### Quick Start
1. Click **Open** to load a local video file, or **From URL** to download from YouTube
2. Click **Transcribe** to generate transcript
3. Click **Detect Clips** to find viral moments
4. Select a clip and click **Export** to create formatted output

### Export Formats
- **Instagram Reels**: 9:16, 90 seconds max
- **YouTube Shorts**: 9:16, 60 seconds max
- **TikTok**: 9:16, 3 minutes max
- **Landscape**: 16:9, standard video
- **Square**: 1:1, Instagram feed

## Project Structure

```
video_repurpose_app/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── config/                # Configuration
│
├── core/                  # Core processing modules
│   ├── config.py         # Settings and constants
│   ├── downloader.py     # Video downloading (yt-dlp)
│   ├── transcriber.py    # Whisper transcription
│   ├── clip_detector.py  # Viral clip detection
│   ├── editor_engine.py  # Transcript editor
│   └── renderer.py       # Video rendering/export
│
├── ai/                    # AI modules
│   └── llm_interface.py  # LLM providers (OpenAI, Anthropic, Ollama)
│
└── ui/                    # PySide6 UI
    ├── main_window.py    # Main application window
    └── dialogs.py        # Custom dialogs
```

## Configuration

Edit `core/config.py` to customize:
- Whisper model size (tiny/base/small/medium/large)
- Clip detection parameters
- Export presets
- UI settings

## Tech Stack

- **UI**: PySide6 (Qt) - Modern, fast Python desktop UI
- **Video Processing**: FFmpeg, moviepy
- **Audio**: pydub
- **AI**: Whisper (OpenAI), LLM integration
- **Download**: yt-dlp

## Performance Tips

1. Use GPU acceleration for Whisper (CUDA-enabled PyTorch)
2. For faster processing, use smaller Whisper models (tiny/base)
3. Enable async processing for batch operations

## License

MIT

## Contributing

Contributions welcome! Please submit issues and pull requests.