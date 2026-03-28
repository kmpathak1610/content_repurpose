"""
Editor Engine Module
Descript-like transcript editor - editing text = editing video
Maps transcript changes to video segments
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import copy
import json


@dataclass
class EditOperation:
    """Represents an edit operation on the transcript"""
    operation_type: str  # "delete", "split", "merge", "keep"
    segment_id: int
    start_time: float
    end_time: float
    text: str
    original_index: int


class TranscriptEditor:
    """
    Descript-style editor that maps text editing to video editing
    - Click on transcript text -> jump to video position
    - Delete text -> remove segment from video
    - Edit text -> update segment
    """
    
    def __init__(self, transcript: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize editor with transcript
        
        Args:
            transcript: List of transcript segments with timestamps
        """
        self.original_transcript: List[Dict[str, Any]] = []
        self.edited_transcript: List[Dict[str, Any]] = []
        self.edit_history: List[List[Dict[str, Any]]] = []
        self.current_position: int = 0
        
        if transcript:
            self.load_transcript(transcript)
    
    def load_transcript(self, transcript: List[Dict[str, Any]]) -> None:
        """Load and initialize transcript"""
        
        # Deep copy to preserve original
        self.original_transcript = copy.deepcopy(transcript)
        self.edited_transcript = copy.deepcopy(transcript)
        self.edit_history = [copy.deepcopy(transcript)]
        self.current_position = 0
    
    def get_segments(self) -> List[Dict[str, Any]]:
        """Get current edited segments"""
        return self.edited_transcript
    
    def get_segment_at_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get segment at index"""
        
        if 0 <= index < len(self.edited_transcript):
            return self.edited_transcript[index]
        return None
    
    def get_segment_at_time(self, time: float) -> Optional[Tuple[int, Dict[str, Any]]]:
        """Get segment at specific time"""
        
        for i, seg in enumerate(self.edited_transcript):
            if seg["start"] <= time <= seg["end"]:
                return i, seg
        return None
    
    def get_time_for_index(self, index: int) -> float:
        """Get start time for segment at index"""
        
        if 0 <= index < len(self.edited_transcript):
            return self.edited_transcript[index]["start"]
        return 0.0
    
    def delete_segment(self, index: int) -> bool:
        """
        Delete a segment from the transcript (removes from video)
        
        Args:
            index: Segment index to delete
            
        Returns:
            True if successful
        """
        if 0 <= index < len(self.edited_transcript):
            deleted_segment = self.edited_transcript.pop(index)
            self._save_edit_state(f"Deleted: {deleted_segment['text'][:30]}...")
            return True
        return False
    
    def delete_range(self, start_index: int, end_index: int) -> bool:
        """
        Delete a range of segments
        
        Args:
            start_index: Start index
            end_index: End index (exclusive)
            
        Returns:
            True if successful
        """
        if 0 <= start_index < end_index <= len(self.edited_transcript):
            self.edited_transcript = (
                self.edited_transcript[:start_index] + 
                self.edited_transcript[end_index:]
            )
            self._save_edit_state(f"Deleted range: {start_index} to {end_index}")
            return True
        return False
    
    def keep_only(self, indices: List[int]) -> bool:
        """
        Keep only specific segments, delete all others
        
        Args:
            indices: List of segment indices to keep
            
        Returns:
            True if successful
        """
        if not indices:
            return False
        
        kept_segments = []
        for i in indices:
            if 0 <= i < len(self.edited_transcript):
                kept_segments.append(self.edited_transcript[i])
        
        if kept_segments:
            self.edited_transcript = kept_segments
            self._save_edit_state(f"Kept {len(kept_segments)} segments")
            return True
        return False
    
    def update_text(self, index: int, new_text: str) -> bool:
        """
        Update segment text (doesn't affect video, just changes subtitle)
        
        Args:
            index: Segment index
            new_text: New text
            
        Returns:
            True if successful
        """
        if 0 <= index < len(self.edited_transcript):
            self.edited_transcript[index]["text"] = new_text
            self._save_edit_state(f"Updated segment {index}")
            return True
        return False
    
    def split_segment(self, index: int, split_time: float) -> Tuple[bool, int]:
        """
        Split a segment at a specific time
        
        Args:
            index: Segment index to split
            split_time: Time to split at
            
        Returns:
            Tuple of (success, new_segment_index)
        """
        if 0 <= index < len(self.edited_transcript):
            segment = self.edited_transcript[index]
            
            if segment["start"] < split_time < segment["end"]:
                # Create two new segments
                first_half = copy.deepcopy(segment)
                second_half = copy.deepcopy(segment)
                
                first_half["end"] = split_time
                second_half["start"] = split_time
                
                # Adjust text (simple split by words)
                words = segment["text"].split()
                mid_point = len(words) // 2
                first_half["text"] = " ".join(words[:mid_point])
                second_half["text"] = " ".join(words[mid_point:])
                
                # Replace original with two new segments
                self.edited_transcript[index] = first_half
                self.edited_transcript.insert(index + 1, second_half)
                
                self._save_edit_state(f"Split segment {index}")
                return True, index + 1
        
        return False, -1
    
    def merge_segments(self, start_index: int, end_index: int) -> bool:
        """
        Merge consecutive segments
        
        Args:
            start_index: Start index
            end_index: End index (exclusive)
            
        Returns:
            True if successful
        """
        if start_index < end_index <= len(self.edited_transcript):
            segments_to_merge = self.edited_transcript[start_index:end_index]
            
            # Create merged segment
            merged = copy.deepcopy(segments_to_merge[0])
            merged["end"] = segments_to_merge[-1]["end"]
            merged["text"] = " ".join(seg["text"] for seg in segments_to_merge)
            
            # Replace range with merged segment
            self.edited_transcript = (
                self.edited_transcript[:start_index] + 
                [merged] + 
                self.edited_transcript[end_index:]
            )
            
            self._save_edit_state(f"Merged {end_index - start_index} segments")
            return True
        
        return False
    
    def undo(self) -> bool:
        """Undo last edit operation"""
        
        if len(self.edit_history) > 1:
            self.edit_history.pop()  # Remove current state
            self.edited_transcript = copy.deepcopy(self.edit_history[-1])
            return True
        return False
    
    def redo(self) -> bool:
        """Redo last undone operation (if available in history)"""
        # Simplified - could implement full redo stack
        return False
    
    def _save_edit_state(self, description: str = "") -> None:
        """Save current state to edit history"""
        
        # Limit history size
        if len(self.edit_history) > 50:
            self.edit_history = self.edit_history[-49:]
        
        self.edit_history.append(copy.deepcopy(self.edited_transcript))
    
    def get_timeline_segments(self) -> List[Dict[str, Any]]:
        """
        Get segments formatted for timeline display
        
        Returns:
            List of segments with timeline-friendly format
        """
        timeline = []
        
        for i, seg in enumerate(self.edited_transcript):
            timeline.append({
                "index": i,
                "text": seg["text"],
                "start": seg["start"],
                "end": seg["end"],
                "duration": seg["end"] - seg["start"],
                "start_formatted": self._format_time(seg["start"]),
                "end_formatted": self._format_time(seg["end"]),
                "duration_formatted": self._format_time(seg["end"] - seg["start"])
            })
        
        return timeline
    
    def get_total_duration(self) -> float:
        """Get total duration of edited video"""
        
        if not self.edited_transcript:
            return 0.0
        
        return self.edited_transcript[-1]["end"] - self.edited_transcript[0]["start"]
    
    def export_edl(self, output_path: Path) -> str:
        """
        Export edit decision list (EDL) for video editing
        
        Args:
            output_path: Path to save EDL
            
        Returns:
            Path to exported file
        """
        edl_content = []
        
        for i, seg in enumerate(self.edited_transcript, 1):
            edl_content.append(
                f"{i:03d}  01 V     C        {self._format_time(seg['start'])} {self._format_time(seg['end'])} "
                f"{self._format_time(seg['start'])} {self._format_time(seg['end'])}"
            )
            edl_content.append(f"* FROM CLIP NAME: {seg['text'][:30]}...")
            edl_content.append("")
        
        with open(output_path, "w") as f:
            f.write("\n".join(edl_content))
        
        return str(output_path)
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds to timecode (HH:MM:SS:FF)"""
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        frames = int((seconds % 1) * 30)  # Assuming 30fps
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"
    
    def get_original_text(self, index: int) -> Optional[str]:
        """Get original text for a segment"""
        
        if 0 <= index < len(self.original_transcript):
            return self.original_transcript[index]["text"]
        return None
    
    def reset_edits(self) -> None:
        """Reset to original transcript"""
        
        self.edited_transcript = copy.deepcopy(self.original_transcript)
        self.edit_history = [copy.deepcopy(self.original_transcript)]
    
    def get_changed_indices(self) -> List[int]:
        """Get indices of segments that have been edited/deleted"""
        
        changed = []
        
        # Compare current with original
        current_texts = [seg["text"] for seg in self.edited_transcript]
        original_texts = [seg["text"] for seg in self.original_transcript]
        
        # Find deleted segments
        for i, text in enumerate(original_texts):
            if text not in current_texts:
                changed.append(i)  # Deleted
        
        # Find modified segments
        min_len = min(len(current_texts), len(original_texts))
        for i in range(min_len):
            if current_texts[i] != original_texts[i]:
                changed.append(i)
        
        return changed


class ClipCollection:
    """
    Manages a collection of clips (for the clip generator)
    """
    
    def __init__(self):
        self.clips: List[Dict[str, Any]] = []
        self.current_clip_index: int = -1
    
    def add_clip(self, clip_data: Dict[str, Any]) -> None:
        """Add a clip to the collection"""
        
        self.clips.append({
            **clip_data,
            "id": len(self.clips),
            "selected": False
        })
    
    def remove_clip(self, clip_id: int) -> bool:
        """Remove a clip by ID"""
        
        for i, clip in enumerate(self.clips):
            if clip["id"] == clip_id:
                self.clips.pop(i)
                return True
        return False
    
    def get_clip(self, clip_id: int) -> Optional[Dict[str, Any]]:
        """Get clip by ID"""
        
        for clip in self.clips:
            if clip["id"] == clip_id:
                return clip
        return None
    
    def select_clip(self, clip_id: int) -> None:
        """Select a clip"""
        
        for clip in self.clips:
            clip["selected"] = (clip["id"] == clip_id)
        
        self.current_clip_index = clip_id
    
    def get_selected_clip(self) -> Optional[Dict[str, Any]]:
        """Get currently selected clip"""
        
        for clip in self.clips:
            if clip.get("selected"):
                return clip
        return None
    
    def update_clip(self, clip_id: int, updates: Dict[str, Any]) -> bool:
        """Update clip properties"""
        
        for clip in self.clips:
            if clip["id"] == clip_id:
                clip.update(updates)
                return True
        return False
    
    def get_all_clips(self) -> List[Dict[str, Any]]:
        """Get all clips"""
        return self.clips
    
    def export_clips(self, output_path: Path) -> str:
        """Export clip list to JSON"""
        
        with open(output_path, "w") as f:
            json.dump(self.clips, f, indent=2)
        
        return str(output_path)


# Convenience functions

def create_editor(transcript: List[Dict[str, Any]]) -> TranscriptEditor:
    """Create a new transcript editor"""
    return TranscriptEditor(transcript)


def create_clip_collection() -> ClipCollection:
    """Create a new clip collection"""
    return ClipCollection()


if __name__ == "__main__":
    # Test
    editor = TranscriptEditor()
    print("TranscriptEditor module loaded successfully")
    print("Editor supports: delete, split, merge, undo operations")