# Video Repurposing Studio - Task Tracker

## Completed (this session)

### Bug Fixes
- [x] Fix YouTube download format selection (invalid yt-dlp format strings)
- [x] Update yt-dlp from 2024.10.07 to 2026.3.17 (YouTube API changes)
- [x] Fix Hindi transcription -- add language parameter to Whisper, set CPU device
- [x] Implement EditClipDialog for clip editing (title, timing, hook, notes)
- [x] Fix ffmpeg export error -- two-pass approach with subprocess
- [x] Fix SRT file not found when using YouTube subtitles (empty transcriber.current_transcript)
- [x] Fix SRT timestamps not matching clip timeline (add offset parameter)
- [x] Fix Windows ffmpeg subtitle path issues (drive letter colon, backslashes)
- [x] Fix OpenAI "model does not support image input" error (gpt-4 -> gpt-4o, strip image URLs)
- [x] Add graceful LLM failure fallback in clip detection
- [x] Set USE_GPU = False in config.py for CPU-only systems

### New Features
- [x] YouTube subtitle download and parsing (SRT format)
- [x] SRT file scanning when loading local videos (finds .srt files next to video)
- [x] Language-agnostic clip detection scoring (works for Hindi, Arabic, etc.)
- [x] Duration-based clip fallback (always produces clips even when scoring fails)
- [x] Language selector dropdown in toolbar (18 languages)
- [x] Clip segment filtering by clip range for SRT export
- [x] Debug logging for transcription and export
- [x] CPU-aware Whisper documentation and settings hints

### Documentation
- [x] Create plan.md -- comprehensive app architecture and CPU-optimized design
- [x] Create todo.md -- task tracking (this file)

## In Progress

- [ ] Test export with Hindi subtitles end-to-end on CPU
- [ ] Verify subtitle sync accuracy in exported clips

## Pending (known issues)

### High Priority
- [ ] Add async processing for Whisper transcription (UI freezes during long videos -- critical on CPU)
- [ ] Fix duplicate export preset definitions (config.py vs renderer.py)
- [ ] Add tests (pytest is in requirements but no test files)

### Medium Priority
- [ ] Implement smart crop using face detection (opencv is installed but unused)
- [ ] Fix LLM clip score hard-coding (all LLM clips score 0.8 regardless of quality)
- [ ] Add soft subtitle support (sidecar file instead of burned-in)
- [ ] Add transcription progress callback (show % complete during Whisper on CPU)

### Low Priority
- [ ] Clean up unused dependencies (moviepy, pydub)
- [ ] Fix SettingsDialog Whisper model list to match config.py
- [ ] Add keyboard shortcuts for common actions
- [ ] Add batch export (export all clips at once)
- [ ] Add export format preview (show dimensions/aspect ratio before export)

## Future Enhancements

### Features
- [ ] Cloud subtitle service integration (Google Speech-to-Text, AWS Transcribe)
- [ ] Auto-caption styling (font, size, color, position presets)
- [ ] Multi-language transcript comparison (side-by-side)
- [ ] Clip preview with timeline scrubbing
- [ ] Undo/redo in clip editing (TranscriptEditor has it, UI doesn't wire it)
- [ ] Save/load project state (open recent projects)
- [ ] Keyboard shortcut customization
- [ ] Plugin system for custom export formats

### CPU-Specific Optimizations
- [ ] Add Whisper model caching (avoid reloading on repeated transcriptions)
- [ ] Add segment-level caching (transcribe once, reuse for multiple clips)
- [ ] Add estimated time remaining during Whisper transcription
- [ ] Add "fast mode" toggle (auto-selects tiny model, skips LLM)
- [ ] Consider faster-whisper as alternative backend (2-4x faster on CPU)

### AI Enhancements
- [ ] Sentiment analysis per segment (positive/negative/neutral)
- [ ] Named entity extraction for topic detection (Hindi, English)
- [ ] Auto-title generation for clips using LLM
- [ ] Trend-based clip scoring (compare against viral content patterns)
- [ ] Face detection for smart crop (using opencv)

### Technical
- [ ] Migrate to PySide6 multimedia with Qt6 video pipeline
- [ ] Add GPU acceleration for ffmpeg operations (if GPU added later)
- [ ] Implement proper undo/redo with history stack
- [ ] Add logging framework (replace print statements)
- [ ] Package as standalone executable (PyInstaller/Nuitka)
