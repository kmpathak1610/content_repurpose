"""
Video Renderer Module
Handles video rendering, format conversion, and export
Supports Reels, Shorts, TikTok formats with auto-cropping
"""

import ffmpeg
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import subprocess
import json


class VideoRenderer:
    """
    Handles all video rendering operations:
    - Clip extraction
    - Format conversion (vertical/horizontal)
    - Subtitle burning
    - Export presets
    """

    # Export presets
    PRESETS = {
        "reels": {
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "video_bitrate": "2000k",
            "audio_bitrate": "128k",
            "max_duration": 90,
            "aspect": "9:16",
        },
        "shorts": {
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "video_bitrate": "2000k",
            "audio_bitrate": "128k",
            "max_duration": 60,
            "aspect": "9:16",
        },
        "tiktok": {
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "video_bitrate": "2000k",
            "audio_bitrate": "128k",
            "max_duration": 180,
            "aspect": "9:16",
        },
        "landscape": {
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "video_bitrate": "4000k",
            "audio_bitrate": "192k",
            "max_duration": 600,
            "aspect": "16:9",
        },
        "square": {
            "width": 1080,
            "height": 1080,
            "fps": 30,
            "video_bitrate": "2000k",
            "audio_bitrate": "128k",
            "max_duration": 300,
            "aspect": "1:1",
        },
    }

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize renderer

        Args:
            output_dir: Output directory for rendered videos
        """
        self.output_dir = output_dir or Path("exports")
        self.output_dir.mkdir(exist_ok=True)
        self.last_output: Optional[Path] = None

    def extract_clip(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_path: Optional[Path] = None,
        codec: str = "copy",
    ) -> Path:
        """
        Extract a clip from video using ffmpeg

        Args:
            video_path: Source video path
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Output path (auto-generated if None)
            codec: Video codec ('copy' for fast, 'libx264' for quality)

        Returns:
            Path to extracted clip
        """
        video_path = Path(video_path)

        if output_path is None:
            output_path = self.output_dir / f"clip_{start_time:.0f}_{end_time:.0f}.mp4"

        # Use -ss before -i for faster seeking
        stream = ffmpeg.input(str(video_path), ss=start_time, to=end_time)

        if codec == "copy":
            stream = ffmpeg.output(
                stream, str(output_path), c="copy", **{"avoid_negative_ts": "make_zero"}
            )
        else:
            stream = ffmpeg.output(
                stream, str(output_path), c="libx264", preset="fast", crf=23
            )

        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        self.last_output = output_path
        return output_path

    def convert_to_vertical(
        self,
        video_path: str,
        output_path: Optional[Path] = None,
        crop_mode: str = "center",
        preset: str = "reels",
    ) -> Path:
        """
        Convert video to vertical format (9:16 aspect ratio)

        Args:
            video_path: Source video path
            output_path: Output path
            crop_mode: 'center', 'smart' (face detection), or 'custom'
            preset: Export preset name

        Returns:
            Path to converted video
        """
        video_path = Path(video_path)
        preset_config = self.PRESETS.get(preset, self.PRESETS["reels"])

        if output_path is None:
            output_path = video_path.with_name(f"{video_path.stem}_vertical.mp4")

        # Get video info
        probe = ffmpeg.probe(str(video_path))
        video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
        original_width = int(video_info["width"])
        original_height = int(video_info["height"])

        # Calculate crop dimensions for 9:16
        target_width = preset_config["width"]
        target_height = preset_config["height"]

        if crop_mode == "center":
            # Center crop
            crop_width = original_height * 9 // 16
            crop_height = original_height
            crop_x = (original_width - crop_width) // 2
            crop_y = 0
        elif crop_mode == "smart":
            # Smart crop - would need face detection
            # For now, use center
            crop_width = original_height * 9 // 16
            crop_height = original_height
            crop_x = (original_width - crop_width) // 2
            crop_y = 0
        else:
            # Default center
            crop_width = original_height * 9 // 16
            crop_height = original_height
            crop_x = (original_width - crop_width) // 2
            crop_y = 0

        # Build filter chain
        filter_chain = f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y},scale={target_width}:{target_height}"

        stream = ffmpeg.input(str(video_path))
        stream = ffmpeg.filter(stream, "scale", target_width, target_height)
        stream = ffmpeg.output(
            stream,
            str(output_path),
            vcodec="libx264",
            preset="fast",
            crf=23,
            r=preset_config["fps"],
            video_bitrate=preset_config["video_bitrate"],
            acodec="aac",
            audio_bitrate=preset_config["audio_bitrate"],
        )

        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        self.last_output = output_path
        return output_path

    def add_subtitles(
        self,
        video_path: str,
        srt_path: str,
        output_path: Optional[Path] = None,
        style: str = "burned",
    ) -> Path:
        """
        Add subtitles to video

        Args:
            video_path: Source video path
            srt_path: SRT subtitle file path
            output_path: Output path
            style: 'burned' (hardcoded) or 'soft' (sidecar)

        Returns:
            Path to video with subtitles
        """
        video_path = Path(video_path)
        srt_path = Path(srt_path)

        if output_path is None:
            output_path = video_path.with_name(f"{video_path.stem}_subtitled.mp4")

        if style == "burned":
            # Escape SRT path for ffmpeg subtitles filter (Windows-safe)
            escaped_srt = self._escape_ffmpeg_path(srt_path)

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-vf",
                f"subtitles='{escaped_srt}'",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "23",
                "-c:a",
                "copy",
                str(output_path),
            ]
        else:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-c:v",
                "copy",
                "-c:a",
                "copy",
                "-c:s",
                "srt",
                "-metadata:s:s:0",
                "language=eng",
                str(output_path),
            ]

        self._run_ffmpeg_cmd(cmd)

        self.last_output = output_path
        return output_path

    def create_clip_with_subtitles(
        self,
        video_path: str,
        srt_path: str,
        start_time: float,
        end_time: float,
        output_path: Optional[Path] = None,
        vertical: bool = False,
        preset: str = "reels",
    ) -> Path:
        """
        Create a clip with subtitles in one operation

        Args:
            video_path: Source video
            srt_path: SRT subtitle file
            start_time: Start time
            end_time: End time
            output_path: Output path
            vertical: Convert to vertical
            preset: Export preset

        Returns:
            Path to final video
        """
        video_path = Path(video_path)

        if output_path is None:
            suffix = "_vertical" if vertical else ""
            output_path = self.output_dir / f"clip_{start_time:.0f}{suffix}.mp4"

        preset_config = self.PRESETS.get(preset, self.PRESETS["reels"])

        # Build filter chain as a single -vf string
        vf_parts = []

        if vertical:
            probe = ffmpeg.probe(str(video_path))
            video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
            original_width = int(video_info["width"])
            original_height = int(video_info["height"])
            crop_width = original_height * 9 // 16
            crop_x = (original_width - crop_width) // 2
            vf_parts.append(f"crop={crop_width}:{original_height}:{crop_x}:0")
            vf_parts.append(f"scale={preset_config['width']}:{preset_config['height']}")

        if srt_path:
            escaped_srt = self._escape_ffmpeg_path(Path(srt_path))
            vf_parts.append(f"subtitles={escaped_srt}")

        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_time),
            "-i",
            str(video_path),
            "-to",
            str(end_time - start_time),
        ]

        if vf_parts:
            cmd += ["-vf", ",".join(vf_parts)]

        cmd += [
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-r",
            str(preset_config["fps"]),
            "-c:a",
            "aac",
            str(output_path),
        ]

        self._run_ffmpeg_cmd(cmd)

        self.last_output = output_path
        return output_path

    def _escape_ffmpeg_path(self, path: Path) -> str:
        """
        Escape a file path for use in ffmpeg subtitles filter.
        Windows paths like D:/path need the colon escaped as D\\:/path
        because ffmpeg uses ':' as filter parameter separator.
        """
        p = str(path).replace("\\", "/")
        # Escape the colon after drive letter: D:/ -> D\:/  (Windows only)
        if len(p) >= 2 and p[1] == ":":
            p = p[0] + "\\:" + p[2:]
        return p

    def _run_ffmpeg_cmd(self, cmd: list):
        """Run an ffmpeg command via subprocess with proper error capture"""
        import subprocess

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                # Trim stderr to last 10 lines for readability
                stderr_lines = result.stderr.strip().splitlines()
                stderr_tail = "\n".join(stderr_lines[-10:])
                raise RuntimeError(f"ffmpeg failed:\n{stderr_tail}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("ffmpeg timed out after 600 seconds")

    def batch_export_clips(
        self,
        video_path: str,
        clips: List[Dict[str, Any]],
        output_dir: Optional[Path] = None,
        preset: str = "reels",
        add_subtitles: bool = True,
    ) -> List[Path]:
        """
        Export multiple clips at once

        Args:
            video_path: Source video path
            clips: List of clip dicts with start_time, end_time, title
            output_dir: Output directory
            preset: Export preset
            add_subtitles: Whether to add subtitles

        Returns:
            List of output paths
        """
        output_dir = output_dir or self.output_dir
        output_dir.mkdir(exist_ok=True)

        outputs = []

        for i, clip in enumerate(clips):
            output_path = (
                output_dir
                / f"{clip.get('title', f'clip_{i}').replace(' ', '_')[:30]}.mp4"
            )

            try:
                output = self.extract_clip(
                    video_path, clip["start_time"], clip["end_time"], output_path
                )
                outputs.append(output)
            except Exception as e:
                print(f"Failed to export clip {i}: {e}")
                continue

        return outputs

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video information"""

        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            audio_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "audio"), None
            )

            return {
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "duration": float(probe["format"].get("duration", 0)),
                "fps": self._parse_fps(video_stream.get("r_frame_rate", "0/1")),
                "codec": video_stream.get("codec_name", "unknown"),
                "audio_codec": audio_stream.get("codec_name", "unknown")
                if audio_stream
                else "none",
                "bitrate": int(probe["format"].get("bit_rate", 0)),
            }
        except Exception as e:
            return {"error": str(e)}

    def _parse_fps(self, fps_string: str) -> float:
        """Parse FPS from fraction string"""
        try:
            if "/" in fps_string:
                num, denom = fps_string.split("/")
                return float(num) / float(denom)
            return float(fps_string)
        except:
            return 0.0

    def get_last_output(self) -> Optional[Path]:
        """Get last output path"""
        return self.last_output

    def estimate_render_time(self, duration: float, preset: str = "reels") -> float:
        """Estimate render time in seconds (rough estimate)"""
        # Assuming ~10x realtime for fast encoding
        return duration * 10


# Convenience functions


def extract_clip(video_path: str, start: float, end: float, output: str = None) -> str:
    """Convenience function to extract a clip"""
    renderer = VideoRenderer()
    result = renderer.extract_clip(
        video_path, start, end, Path(output) if output else None
    )
    return str(result)


def convert_to_vertical(
    video_path: str, output: str = None, preset: str = "reels"
) -> str:
    """Convenience function to convert to vertical"""
    renderer = VideoRenderer()
    result = renderer.convert_to_vertical(
        video_path, Path(output) if output else None, preset=preset
    )
    return str(result)


if __name__ == "__main__":
    renderer = VideoRenderer()
    print("VideoRenderer module loaded successfully")
    print(f"Available presets: {', '.join(renderer.PRESETS.keys())}")
