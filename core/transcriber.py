"""
Transcription Engine Module
Uses Whisper for local speech-to-text transcription with timestamps
"""

import whisper
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import os


class TranscriptionEngine:
    """
    Handles video/audio transcription using OpenAI Whisper
    Supports local-only processing for privacy
    """

    def __init__(self, model_name: str = "base", device: Optional[str] = None):
        """
        Initialize transcription engine

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: Device to use (cuda, cpu). Auto-detects if None
        """
        self.model_name = model_name

        # Auto-detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.model = None
        self.current_transcript: List[Dict[str, Any]] = []

        print(f"Using device: {self.device}")

    def load_model(self) -> None:
        """Load Whisper model (lazy loading)"""
        if self.model is None:
            print(f"Loading Whisper model: {self.model_name}...")
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"Model loaded successfully!")

    def transcribe(
        self, audio_path: str, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en'). Auto-detects if None

        Returns:
            List of transcript segments with timestamps
        """
        self.load_model()

        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"Transcribing: {audio_path.name} (language={language})...")

        transcribe_kwargs = {
            "word_timestamps": True,
            "verbose": False,
        }
        if language:
            transcribe_kwargs["language"] = language
            transcribe_kwargs["task"] = "transcribe"

        result = self.model.transcribe(str(audio_path), **transcribe_kwargs)

        detected_lang = result.get("language", "unknown")
        print(f"Whisper detected language: {detected_lang}")

        # Process and store transcript
        self.current_transcript = self._process_segments(result["segments"])

        if self.current_transcript:
            print(f"First segment: {self.current_transcript[0]['text'][:80]}")

        print(f"Transcription complete! {len(self.current_transcript)} segments")

        return self.current_transcript

    def transcribe_video(
        self, video_path: str, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Transcribe directly from video file (extracts audio internally)

        Args:
            video_path: Path to video file
            language: Language code

        Returns:
            List of transcript segments
        """
        self.load_model()

        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        print(f"Transcribing video: {video_path.name} (language={language})...")

        transcribe_kwargs = {
            "word_timestamps": True,
            "verbose": False,
        }
        if language:
            transcribe_kwargs["language"] = language
            transcribe_kwargs["task"] = "transcribe"

        result = self.model.transcribe(str(video_path), **transcribe_kwargs)

        detected_lang = result.get("language", "unknown")
        print(f"Whisper detected language: {detected_lang}")

        self.current_transcript = self._process_segments(result["segments"])

        if self.current_transcript:
            print(f"First segment: {self.current_transcript[0]['text'][:80]}")

        print(f"Transcription complete! {len(self.current_transcript)} segments")

        return self.current_transcript

    def _process_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw Whisper segments into cleaner format"""

        processed = []
        for i, seg in enumerate(segments):
            processed.append(
                {
                    "id": i,
                    "text": seg["text"].strip(),
                    "start": seg["start"],
                    "end": seg["end"],
                    "words": seg.get("words", []),
                    "confidence": seg.get("avg_logprob", 0),
                }
            )

        return processed

    def get_transcript_text(
        self, segments: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Get full transcript as plain text"""

        segments = segments or self.current_transcript
        return " ".join(seg["text"] for seg in segments)

    def export_srt(
        self,
        segments: Optional[List[Dict[str, Any]]] = None,
        output_path: Optional[Path] = None,
        offset: float = 0.0,
    ) -> str:
        """Export transcript as SRT subtitle file

        Args:
            segments: Transcript segments
            output_path: Where to write the SRT
            offset: Subtract this from all timestamps (use for clip exports
                    where the clip starts partway through the video)
        """

        segments = segments or self.current_transcript

        if output_path is None:
            output_path = Path("transcript.srt")

        srt_content = self._generate_srt(segments, offset=offset)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        return str(output_path)

    def _generate_srt(self, segments: List[Dict[str, Any]], offset: float = 0.0) -> str:
        """Generate SRT format from segments"""

        srt_lines = []
        for i, seg in enumerate(segments, 1):
            start_time = self._format_srt_time(max(0, seg["start"] - offset))
            end_time = self._format_srt_time(max(0, seg["end"] - offset))
            text = seg["text"]

            srt_lines.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")

        return "\n".join(srt_lines)

    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def export_json(
        self,
        segments: Optional[List[Dict[str, Any]]] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        """Export transcript as JSON"""

        segments = segments or self.current_transcript

        if output_path is None:
            output_path = Path("transcript.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, indent=2, ensure_ascii=False)

        return str(output_path)

    def get_segment_at_time(self, time: float) -> Optional[Dict[str, Any]]:
        """Get transcript segment at a specific time"""

        for seg in self.current_transcript:
            if seg["start"] <= time <= seg["end"]:
                return seg
        return None

    def search_transcript(
        self, query: str, case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """Search transcript for text"""

        results = []
        query = query if case_sensitive else query.lower()

        for seg in self.current_transcript:
            text = seg["text"] if case_sensitive else seg["text"].lower()
            if query in text:
                results.append(seg)

        return results

    def get_current_transcript(self) -> List[Dict[str, Any]]:
        """Get the current transcript"""
        return self.current_transcript

    def clear_transcript(self):
        """Clear current transcript"""
        self.current_transcript = []


def transcribe_video(video_path: str, model: str = "base") -> List[Dict[str, Any]]:
    """
    Convenience function to transcribe a video file

    Args:
        video_path: Path to video file
        model: Whisper model size

    Returns:
        List of transcript segments
    """
    engine = TranscriptionEngine(model_name=model)
    return engine.transcribe_video(video_path)


if __name__ == "__main__":
    # Test
    engine = TranscriptionEngine("base")
    print("TranscriptionEngine module loaded successfully")
    print(f"Available models: tiny, base, small, medium, large")
