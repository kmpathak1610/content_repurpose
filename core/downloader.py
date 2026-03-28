"""
Video Downloader Module
Handles downloading videos from YouTube URLs or loading local video files
Also handles YouTube subtitle downloading and SRT parsing
"""

import os
import re
import ffmpeg
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
import yt_dlp


class VideoDownloader:
    """
    Handles video input from various sources:
    - YouTube URLs
    - Local video files
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("exports")
        self.output_dir.mkdir(exist_ok=True)
        self.current_video_path: Optional[Path] = None
        self.video_info: Dict[str, Any] = {}

    def is_youtube_url(self, source: str) -> bool:
        """Check if the source is a YouTube URL"""
        youtube_domains = [
            "youtube.com",
            "youtu.be",
            "youtube.co.uk",
            "youtube.co.in",
            "y2u.be",
            "m.youtube.com",
        ]
        return any(domain in source.lower() for domain in youtube_domains)

    def fetch_video_info(self, source: str) -> Dict[str, Any]:
        """Get video metadata without downloading"""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source, download=False)
            return {
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown"),
                "upload_date": info.get("upload_date", ""),
                "description": info.get("description", ""),
                "thumbnail": info.get("thumbnail", ""),
                "url": source,
            }

    def download(
        self, source: str, quality: str = "best"
    ) -> Tuple[Path, Dict[str, Any]]:
        """
        Download video from URL or load local file

        Args:
            source: YouTube URL or local file path
            quality: Video quality preference (best, worst, bestvideo+bestaudio)

        Returns:
            Tuple of (video_path, video_info)
        """
        if self.is_youtube_url(source):
            return self._download_youtube(source, quality)
        else:
            return self._load_local(source)

    def _download_youtube(self, url: str, quality: str) -> Tuple[Path, Dict[str, Any]]:
        """Download video from YouTube using yt-dlp"""

        # Get video info first
        self.video_info = self.fetch_video_info(url)

        # Sanitize filename
        safe_title = "".join(
            c for c in self.video_info["title"] if c.isalnum() or c in " -_"
        ).strip()[:50]
        output_filename = f"{safe_title}.mp4"
        output_path = self.output_dir / output_filename

        # Valid yt-dlp format strings, ordered from most to least preferred
        format_options = [
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "bestvideo+bestaudio/best",
            "best",
            "worstvideo+bestaudio/worst",
            "worst",
        ]

        last_error = None
        success = False

        for fmt in format_options:
            try:
                ydl_opts = {
                    "format": fmt,
                    "outtmpl": str(self.output_dir / f"{safe_title}.%(ext)s"),
                    "merge_output_format": "mp4",
                    "progress_hooks": [self._progress_hook],
                }

                print(f"Trying format: {fmt}")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                success = True
                break

            except Exception as e:
                last_error = str(e)
                print(f"Format {fmt} failed: {last_error}")
                continue

        if not success:
            raise RuntimeError(f"Failed to download: {last_error}")

        # Find the downloaded file
        downloaded_files = list(self.output_dir.glob(f"{safe_title}.*"))
        if not downloaded_files:
            raise FileNotFoundError(f"Failed to download video: {url}")

        self.current_video_path = downloaded_files[0]
        return self.current_video_path, self.video_info

    def _load_local(self, file_path: str) -> Tuple[Path, Dict[str, Any]]:
        """Load a local video file"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")

        # Get video info using ffmpeg
        probe = ffmpeg.probe(str(path))
        video_stream = next(
            (s for s in probe["streams"] if s["codec_type"] == "video"), None
        )

        self.current_video_path = path
        self.video_info = {
            "title": path.stem,
            "duration": float(probe["format"].get("duration", 0)),
            "size": probe["format"].get("size", 0),
            "format": probe["format"].get("format_name", "unknown"),
            "width": int(video_stream.get("width", 0)) if video_stream else 0,
            "height": int(video_stream.get("height", 0)) if video_stream else 0,
            "fps": self._parse_fps(video_stream.get("r_frame_rate", "0/1"))
            if video_stream
            else 0,
        }

        return self.current_video_path, self.video_info

    def _parse_fps(self, fps_string: str) -> float:
        """Parse FPS from fraction string like '30000/1001'"""
        try:
            if "/" in fps_string:
                num, denom = fps_string.split("/")
                return float(num) / float(denom)
            return float(fps_string)
        except:
            return 0.0

    def _progress_hook(self, d: Dict[str, Any]):
        """Progress callback for yt-dlp"""
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%")
            speed = d.get("_speed_str", "0")
            print(f"\rDownloading: {percent} at {speed}", end="")
        elif d["status"] == "finished":
            print(f"\nDownload complete!")

    def extract_audio(
        self, video_path: Optional[Path] = None, output_format: str = "mp3"
    ) -> Path:
        """
        Extract audio from video

        Args:
            video_path: Path to video file (uses current if not provided)
            output_format: Output audio format (mp3, wav, m4a)

        Returns:
            Path to extracted audio file
        """
        video_path = video_path or self.current_video_path
        if not video_path:
            raise ValueError("No video loaded")

        audio_path = video_path.with_suffix(f".{output_format}")

        try:
            stream = ffmpeg.input(str(video_path))
            stream = ffmpeg.output(
                stream,
                str(audio_path),
                **{"acodec": "libmp3lame" if output_format == "mp3" else output_format},
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to extract audio: {e}")

        return audio_path

    def get_video_path(self) -> Optional[Path]:
        """Get the current video path"""
        return self.current_video_path

    def get_current_video_info(self) -> Dict[str, Any]:
        """Get current video information"""
        return self.video_info

    # ==================== Subtitle Methods ====================

    def fetch_available_subtitles(self, url: str) -> Dict[str, List[str]]:
        """
        List available subtitle languages for a YouTube video.

        Returns:
            Dict with 'manual' and 'auto' keys, each containing a list of language codes.
        """
        ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": False}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        manual = list((info.get("subtitles") or {}).keys())
        auto = list((info.get("automatic_captions") or {}).keys())

        # yt-dlp includes a ton of auto-generated translation languages
        # Filter to just the original auto-generated ones (no ".en" translations)
        auto_original = [lang for lang in auto if "." not in lang]

        return {"manual": manual, "auto": auto_original}

    def download_subtitles(
        self, url: str, lang: str = "hi", prefer_manual: bool = True
    ) -> Optional[Path]:
        """
        Download subtitles from YouTube as SRT.

        Args:
            url: YouTube video URL
            lang: Language code (e.g. 'hi', 'en')
            prefer_manual: Prefer manual subs over auto-generated

        Returns:
            Path to downloaded SRT file, or None if not available.
        """
        safe_title = "".join(
            c
            for c in self.video_info.get("title", "video")
            if c.isalnum() or c in " -_"
        ).strip()[:50]

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "writesubtitles": prefer_manual,
            "writeautomaticsub": not prefer_manual,
            "subtitleslangs": [lang],
            "subtitlesformat": "srt",
            "outtmpl": str(self.output_dir / f"{safe_title}"),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"Subtitle download failed: {e}")
            return None

        # Find the downloaded SRT file
        # yt-dlp names them like: title.lang.srt or title.lang.auto.srt
        candidates = list(self.output_dir.glob(f"{safe_title}*{lang}*.srt"))
        if candidates:
            print(f"Downloaded subtitles: {candidates[0]}")
            return candidates[0]

        # If manual preferred but not found, try auto
        if prefer_manual:
            print(f"No manual subs found for '{lang}', trying auto-generated...")
            return self.download_subtitles(url, lang, prefer_manual=False)

        print(f"No subtitles found for language: {lang}")
        return None

    def parse_srt(self, srt_path: Path) -> List[Dict[str, Any]]:
        """
        Parse an SRT file into the same segment format Whisper produces:
        [{"id": 0, "text": "...", "start": 0.0, "end": 2.5, "words": [], "confidence": 0}, ...]
        """
        segments = []

        with open(srt_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Split into blocks separated by blank lines
        blocks = re.split(r"\n\s*\n", content.strip())

        for block in blocks:
            lines = block.strip().splitlines()
            if len(lines) < 3:
                continue

            # Line 0: index number (skip)
            # Line 1: timestamp "00:00:01,000 --> 00:00:04,000"
            # Line 2+: subtitle text
            time_match = re.match(
                r"(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})",
                lines[1],
            )
            if not time_match:
                continue

            start = self._srt_time_to_seconds(time_match.group(1))
            end = self._srt_time_to_seconds(time_match.group(2))

            # Join remaining lines as text, strip HTML-like tags
            text = " ".join(lines[2:])
            text = re.sub(r"<[^>]+>", "", text)  # remove <b>, <i>, etc.
            text = re.sub(r"\{[^}]+\}", "", text)  # remove {\an8} positioning
            text = text.strip()

            if text:
                segments.append(
                    {
                        "id": len(segments),
                        "text": text,
                        "start": start,
                        "end": end,
                        "words": [],
                        "confidence": 0,
                    }
                )

        print(f"Parsed {len(segments)} segments from SRT")
        return segments

    @staticmethod
    def _srt_time_to_seconds(time_str: str) -> float:
        """Convert SRT timestamp (00:01:23,456) to seconds"""
        time_str = time_str.replace(",", ".")
        parts = time_str.split(":")
        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds


def download_video(url: str, output_dir: str = "exports") -> Tuple[str, Dict[str, Any]]:
    """
    Convenience function to download a video

    Args:
        url: YouTube URL or local file path
        output_dir: Output directory

    Returns:
        Tuple of (video_path, video_info)
    """
    downloader = VideoDownloader(Path(output_dir))
    return downloader.download(url)


if __name__ == "__main__":
    # Test
    downloader = VideoDownloader()
    # Test with YouTube URL (would need actual URL)
    # path, info = downloader.download("https://www.youtube.com/watch?v=example")
    print("VideoDownloader module loaded successfully")
