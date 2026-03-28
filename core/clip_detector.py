"""
Viral Clip Detection Module
AI-powered detection of viral-worthy segments in video transcripts
Combines rule-based signals with LLM analysis
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class ClipSegment:
    """Represents a detected clip segment"""

    start_time: float
    end_time: float
    title: str
    hook: str
    score: float
    reason: str
    topics: List[str]


class ClipDetector:
    """
    Detects viral-worthy clips from transcript
    Uses hybrid approach: rule-based scoring + LLM analysis
    """

    # Hook keywords that indicate engaging content
    HOOK_KEYWORDS = [
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
        "surprising",
        "unexpected",
        "reveal",
        "breaking",
        "important",
        "critical",
        "essential",
        "key",
        "imagine",
        "think",
        "know",
        "guess",
        "guess what",
        "here's the thing",
        "the truth is",
        "let me tell you",
    ]

    # Controversial/emotional keywords
    EMOTION_KEYWORDS = [
        "angry",
        "furious",
        "love",
        "hate",
        "fear",
        "scared",
        "amazing",
        "incredible",
        "unbelievable",
        "insane",
        "crazy",
        "ridiculous",
        "absurd",
        "stupid",
        "idiotic",
        "brilliant",
        "genius",
        "smart",
        "dumb",
        "ignorant",
        "finally",
        "finally!",
        "answer",
        "explain",
        "why",
    ]

    def __init__(
        self,
        min_duration: int = 20,
        max_duration: int = 60,
        num_clips: int = 5,
        llm_provider: Optional[Any] = None,
    ):
        """
        Initialize clip detector

        Args:
            min_duration: Minimum clip duration in seconds
            max_duration: Maximum clip duration in seconds
            num_clips: Number of clips to generate
            llm_provider: LLM provider for advanced analysis
        """
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.num_clips = num_clips
        self.llm_provider = llm_provider

    def detect_clips(
        self, transcript: List[Dict[str, Any]], use_llm: bool = True
    ) -> List[ClipSegment]:
        """
        Main entry point to detect viral clips

        Args:
            transcript: List of transcript segments
            use_llm: Whether to use LLM for enhanced detection

        Returns:
            List of detected clip segments
        """
        if not transcript:
            return []

        # Step 1: Rule-based scoring
        scored_segments = self._rule_based_scoring(transcript)

        # Step 2: Merge adjacent high-scoring segments
        candidate_clips = self._merge_segments(scored_segments)

        # Step 3: If LLM available, use it for enhanced detection
        if use_llm and self.llm_provider:
            llm_clips = self._llm_detect_clips(transcript)
            # Merge LLM clips with rule-based
            candidate_clips = self._merge_llm_and_rule(llm_clips, candidate_clips)

        # Step 4: Fallback — if no clips found, create duration-based clips
        if not candidate_clips:
            candidate_clips = self._duration_based_clips(transcript)

        # Step 5: Rank and select top clips
        final_clips = self._rank_and_select(candidate_clips)

        return final_clips[: self.num_clips]

    def _rule_based_scoring(
        self, transcript: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply rule-based scoring to each segment — works for any language"""

        scored = []

        for i, seg in enumerate(transcript):
            text = seg["text"].lower()
            original_text = seg["text"]
            score = 0.0
            reasons = []

            # Hook detection (first 3 seconds = higher score)
            if seg["start"] < 3.0:
                score += 0.3
                reasons.append("early_hook")

            # Hook keywords (English — still useful for mixed content)
            hook_count = sum(1 for kw in self.HOOK_KEYWORDS if kw in text)
            if hook_count > 0:
                score += min(0.2 * hook_count, 0.4)
                reasons.append(f"hook_keywords({hook_count})")

            # Emotion keywords (English)
            emotion_count = sum(1 for kw in self.EMOTION_KEYWORDS if kw in text)
            if emotion_count > 0:
                score += min(0.15 * emotion_count, 0.3)
                reasons.append(f"emotion({emotion_count})")

            # --- Language-agnostic signals (work for Hindi, Arabic, etc.) ---

            # Question detection (universal engagement)
            if "?" in original_text:
                score += 0.25
                reasons.append("question")

            # Exclamation (high energy, universal)
            if "!" in original_text:
                score += 0.2
                reasons.append("exclamation")

            # Short punchy sentences (engaging in any language)
            word_count = len(text.split())
            if 3 <= word_count <= 15:
                score += 0.15
                reasons.append("punchy_length")

            # Longer substantive segments (topic introductions)
            if word_count > 20:
                score += 0.1
                reasons.append("substantive")

            # Numbers / dates / statistics (universal attention grabbers)
            if re.search(r"\d+", original_text):
                score += 0.1
                reasons.append("contains_numbers")

            # Topic shift detection (compare with previous)
            if i > 0:
                prev_text = transcript[i - 1]["text"].lower()
                if not self._similar_content(text, prev_text):
                    score += 0.2
                    reasons.append("topic_shift")

            # Pauses detection (based on segment gap)
            if i > 0:
                gap = seg["start"] - transcript[i - 1]["end"]
                if gap > 0.5:  # Significant pause
                    score += 0.15
                    reasons.append("dramatic_pause")

            # Very early in video (opening hook area: first 10% of video)
            total_duration = transcript[-1]["end"] if transcript else 0
            if total_duration > 0 and seg["start"] < total_duration * 0.1:
                score += 0.15
                reasons.append("opening_section")

            scored.append({"segment": seg, "score": score, "reasons": reasons})

        return scored

    def _similar_content(self, text1: str, text2: str, threshold: float = 0.5) -> bool:
        """Check if two texts are similar (basic word overlap)"""

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return False

        overlap = len(words1 & words2) / min(len(words1), len(words2))
        return overlap > threshold

    def _merge_segments(
        self, scored_segments: List[Dict[str, Any]]
    ) -> List[ClipSegment]:
        """Merge adjacent high-scoring segments into clips"""

        if not scored_segments:
            return []

        clips = []
        current_clip_start = None
        current_clip_end = None
        current_clip_score = 0.0
        current_clip_segments = []

        for item in scored_segments:
            seg = item["segment"]
            score = item["score"]

            # Start new clip if score is high enough (0.1 for any-language support)
            if score > 0.1:
                if current_clip_start is None:
                    current_clip_start = seg["start"]
                    current_clip_segments = [seg]
                else:
                    current_clip_segments.append(seg)

                current_clip_end = seg["end"]
                current_clip_score = max(current_clip_score, score)

            # End current clip if gap is too large or score drops
            elif current_clip_start is not None:
                clip_duration = current_clip_end - current_clip_start

                if self.min_duration <= clip_duration <= self.max_duration:
                    title = self._generate_title(current_clip_segments)
                    hook = self._extract_hook(current_clip_segments)

                    clips.append(
                        ClipSegment(
                            start_time=current_clip_start,
                            end_time=current_clip_end,
                            title=title,
                            hook=hook,
                            score=current_clip_score,
                            reason=", ".join(item["reasons"]),
                            topics=self._extract_topics(current_clip_segments),
                        )
                    )

                current_clip_start = None
                current_clip_end = None
                current_clip_score = 0.0
                current_clip_segments = []

        # Handle last clip
        if current_clip_start is not None:
            clip_duration = current_clip_end - current_clip_start
            if self.min_duration <= clip_duration <= self.max_duration:
                title = self._generate_title(current_clip_segments)
                hook = self._extract_hook(current_clip_segments)

                clips.append(
                    ClipSegment(
                        start_time=current_clip_start,
                        end_time=current_clip_end,
                        title=title,
                        hook=hook,
                        score=current_clip_score,
                        reason="auto_merged",
                        topics=self._extract_topics(current_clip_segments),
                    )
                )

        return clips

    def _generate_title(self, segments: List[Dict[str, Any]]) -> str:
        """Generate a title for the clip based on its content"""

        # Use first segment text as base
        if not segments:
            return "Untitled Clip"

        first_text = segments[0]["text"].strip()

        # Truncate if too long
        if len(first_text) > 50:
            first_text = first_text[:50].rsplit(" ", 1)[0] + "..."

        return first_text

    def _extract_hook(self, segments: List[Dict[str, Any]]) -> str:
        """Extract the hook from the clip (first engaging sentence)"""

        for seg in segments[:3]:  # Check first few segments
            text = seg["text"].strip()

            # Check for hook keywords
            if any(kw in text.lower() for kw in self.HOOK_KEYWORDS):
                return text[:100]  # Limit hook length

            # Use first segment if no hook found
            if seg == segments[0]:
                return text[:100]

        return segments[0]["text"][:100] if segments else ""

    def _extract_topics(self, segments: List[Dict[str, Any]]) -> List[str]:
        """Extract main topics from segments"""

        # Simple keyword-based topic extraction
        all_text = " ".join(seg["text"] for seg in segments).lower()

        topics = set()
        topic_keywords = {
            "politics": [
                "politics",
                "government",
                "president",
                "election",
                "policy",
                "vote",
            ],
            "business": ["business", "company", "market", "money", "economy", "stock"],
            "technology": ["tech", "ai", "software", "computer", "digital", "internet"],
            "science": ["science", "research", "study", "discovery", "scientist"],
            "health": ["health", "medical", "doctor", "disease", "treatment"],
            "sports": ["sport", "game", "team", "player", "match", "score"],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in all_text for kw in keywords):
                topics.add(topic)

        return list(topics)[:3]  # Max 3 topics

    def _llm_detect_clips(self, transcript: List[Dict[str, Any]]) -> List[ClipSegment]:
        """Use LLM to detect clips (if provider available)"""

        if not self.llm_provider:
            return []

        try:
            # Build transcript text with timestamps
            transcript_text = self._build_transcript_for_llm(transcript)

            # Create prompt for LLM
            prompt = self._build_clip_prompt(transcript_text)

            # Get LLM response
            response = self.llm_provider.generate(prompt)

            # Parse response to extract clips
            return self._parse_llm_response(response)
        except Exception as e:
            print(f"LLM clip detection failed: {e} — falling back to rule-based")
            return []

    def _build_transcript_for_llm(self, transcript: List[Dict[str, Any]]) -> str:
        """Build formatted transcript for LLM"""

        lines = []
        for seg in transcript:
            minutes = int(seg["start"] // 60)
            seconds = int(seg["start"] % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            lines.append(f"{timestamp} {seg['text']}")

        return "\n".join(lines)

    def _build_clip_prompt(self, transcript_text: str) -> str:
        """Build prompt for LLM clip detection"""

        return f"""Analyze the following video transcript and identify {self.num_clips} viral short-form video clips (20-60 seconds each).

For each clip, consider:
- Strong hook in first 3 seconds
- Controversial or emotional content
- Clear standalone meaning
- High engagement potential

Transcript:
{transcript_text}

Return your response as JSON array with this exact format:
[
  {{
    "start_time": 123.45,
    "end_time": 180.90,
    "title": "Clip title",
    "hook": "The hook/attention grabber"
  }}
]"""

    def _parse_llm_response(self, response: str) -> List[ClipSegment]:
        """Parse LLM response into ClipSegment objects"""

        try:
            # Try to extract JSON from response
            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                clips_data = json.loads(json_match.group())

                clips = []
                for item in clips_data:
                    duration = item.get("end_time", 0) - item.get("start_time", 0)
                    if self.min_duration <= duration <= self.max_duration:
                        clips.append(
                            ClipSegment(
                                start_time=item.get("start_time", 0),
                                end_time=item.get("end_time", 0),
                                title=item.get("title", "Untitled"),
                                hook=item.get("hook", ""),
                                score=0.8,  # LLM clips get high score
                                reason="llm_detected",
                                topics=[],
                            )
                        )

                return clips
        except Exception as e:
            print(f"Failed to parse LLM response: {e}")

        return []

    def _merge_llm_and_rule(
        self, llm_clips: List[ClipSegment], rule_clips: List[ClipSegment]
    ) -> List[ClipSegment]:
        """Merge LLM-detected clips with rule-based clips"""

        # Combine and deduplicate
        all_clips = llm_clips + rule_clips

        # Remove overlapping clips (keep higher scoring)
        merged = []
        for clip in all_clips:
            overlaps = False
            for existing in merged:
                if self._time_overlap(clip, existing):
                    overlaps = True
                    if clip.score > existing.score:
                        # Replace with higher scoring clip
                        merged.remove(existing)
                        merged.append(clip)
                    break

            if not overlaps:
                merged.append(clip)

        return merged

    def _time_overlap(self, clip1: ClipSegment, clip2: ClipSegment) -> bool:
        """Check if two clips overlap in time"""

        return not (
            clip1.end_time <= clip2.start_time or clip1.start_time >= clip2.end_time
        )

    def _rank_and_select(self, clips: List[ClipSegment]) -> List[ClipSegment]:
        """Rank clips by score and return top N"""

        # Sort by score descending
        ranked = sorted(clips, key=lambda x: x.score, reverse=True)

        return ranked

    def _duration_based_clips(
        self, transcript: List[Dict[str, Any]]
    ) -> List[ClipSegment]:
        """
        Fallback: create clips by dividing transcript into roughly equal
        chunks of max_duration. Guarantees output even when scoring yields nothing.
        """
        if not transcript:
            return []

        total_duration = transcript[-1]["end"]
        if total_duration <= 0:
            return []

        # Space out clip start times evenly across the video
        clip_duration = min(
            self.max_duration,
            max(self.min_duration, total_duration // (self.num_clips + 1)),
        )
        step = max(clip_duration, total_duration // self.num_clips)

        clips = []
        current_start = 0.0

        while (
            current_start + clip_duration <= total_duration
            and len(clips) < self.num_clips
        ):
            end = current_start + clip_duration

            # Find segments in this range
            segs = [
                s for s in transcript if s["start"] >= current_start and s["end"] <= end
            ]

            if not segs:
                # Find the nearest segments
                segs = [
                    s
                    for s in transcript
                    if s["end"] > current_start and s["start"] < end
                ]

            if segs:
                actual_start = segs[0]["start"]
                actual_end = segs[-1]["end"]
                title = self._generate_title(segs)

                clips.append(
                    ClipSegment(
                        start_time=actual_start,
                        end_time=actual_end,
                        title=title,
                        hook=segs[0]["text"][:100],
                        score=0.5,
                        reason="duration_fallback",
                        topics=[],
                    )
                )

            current_start += step

        return clips

    def format_clip_for_export(self, clip: ClipSegment) -> Dict[str, Any]:
        """Format clip for export"""

        return {
            "start_time": self._format_time(clip.start_time),
            "end_time": self._format_time(clip.end_time),
            "duration": clip.end_time - clip.start_time,
            "title": clip.title,
            "hook": clip.hook,
            "score": round(clip.score, 2),
            "reason": clip.reason,
            "topics": clip.topics,
        }

    def _format_time(self, seconds: float) -> str:
        """Format seconds to MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


def detect_viral_clips(
    transcript: List[Dict[str, Any]],
    min_duration: int = 20,
    max_duration: int = 60,
    num_clips: int = 5,
    llm_provider: Optional[Any] = None,
) -> List[ClipSegment]:
    """
    Convenience function to detect viral clips

    Args:
        transcript: List of transcript segments
        min_duration: Minimum clip duration
        max_duration: Maximum clip duration
        num_clips: Number of clips to generate
        llm_provider: Optional LLM provider

    Returns:
        List of detected clip segments
    """
    detector = ClipDetector(
        min_duration=min_duration,
        max_duration=max_duration,
        num_clips=num_clips,
        llm_provider=llm_provider,
    )
    return detector.detect_clips(transcript)


if __name__ == "__main__":
    # Test
    detector = ClipDetector()
    print("ClipDetector module loaded successfully")
    print(f"Min duration: {detector.min_duration}s, Max: {detector.max_duration}s")
