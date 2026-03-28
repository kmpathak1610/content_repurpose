"""
AI Module
LLM interface for advanced clip detection and content analysis
Supports multiple providers: OpenAI, Anthropic, Ollama, llama.cpp
"""

import json
import os
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import re


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from prompt"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.is_available():
            raise RuntimeError("OpenAI API key not available")

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            # Strip any image URLs/paths from prompt to avoid "model does not support image input"
            clean_prompt = re.sub(
                r"https?://\S+\.(png|jpg|jpeg|gif|webp|bmp)", "[image removed]", prompt
            )
            clean_prompt = re.sub(
                r"[A-Z]:\\[^\n]+\.(png|jpg|jpeg|gif|webp|bmp)",
                "[image removed]",
                clean_prompt,
            )

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": clean_prompt})

            response = client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7
            )

            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.is_available():
            raise RuntimeError("Anthropic API key not available")

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": full_prompt}],
            )

            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model

    def is_available(self) -> bool:
        try:
            import requests

            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            import requests

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full_prompt, "stream": False},
                timeout=120,
            )

            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                raise RuntimeError(f"Ollama error: {response.status_code}")
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}")


class LLMInterface:
    """
    Unified interface for LLM providers
    Handles provider selection and fallback
    """

    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider_name = provider
        self.provider = self._create_provider(provider, api_key, model)
        self.system_prompt = self._get_default_system_prompt()

    def _create_provider(
        self, provider: str, api_key: Optional[str], model: Optional[str]
    ) -> LLMProvider:
        """Create LLM provider instance"""

        if provider == "openai":
            return OpenAIProvider(api_key, model or "gpt-4o")
        elif provider == "anthropic":
            return AnthropicProvider(api_key, model or "claude-3-opus-20240229")
        elif provider == "ollama":
            return OllamaProvider(model=model or "llama2")
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for video analysis"""

        return """You are an expert video content analyst specializing in identifying viral, engaging moments from long-form video content.

Your expertise includes:
- Understanding what makes content go viral on social media
- Identifying strong hooks and attention-grabbing moments
- Analyzing emotional and controversial content
- Recognizing standalone moments that work without context

When analyzing transcripts, consider:
1. First 3 seconds hook strength
2. Emotional intensity and controversy
3. Standalone clarity (can it be understood without full context?)
4. Engagement potential (questions, surprises, reveals)
5. Pacing and rhythm of speech

Return your analysis in clean JSON format."""

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from LLM"""

        if not self.provider.is_available():
            raise RuntimeError(f"LLM provider {self.provider_name} is not available")

        return self.provider.generate(prompt, system_prompt or self.system_prompt)

    def is_available(self) -> bool:
        """Check if current provider is available"""
        return self.provider.is_available()

    def detect_clips(
        self,
        transcript: str,
        num_clips: int = 5,
        min_duration: int = 20,
        max_duration: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to detect viral clips from transcript

        Args:
            transcript: Full transcript text with timestamps
            num_clips: Number of clips to detect
            min_duration: Minimum clip duration
            max_duration: Maximum clip duration

        Returns:
            List of clip dicts
        """
        prompt = self._build_clip_detection_prompt(
            transcript, num_clips, min_duration, max_duration
        )

        response = self.generate(prompt)

        return self._parse_clip_response(response)

    def _build_clip_detection_prompt(
        self, transcript: str, num_clips: int, min_duration: int, max_duration: int
    ) -> str:
        """Build prompt for clip detection"""

        return f"""Analyze the following video transcript and identify the {num_clips} best viral short-form video clips.

Requirements:
- Each clip must be {min_duration}-{max_duration} seconds
- Strong hook in first 3 seconds
- Content that can stand alone without full context
- High emotional or controversial content
- Questions, reveals, or surprising statements

Transcript (with timestamps):
{transcript}

Return ONLY a JSON array of clip objects with this exact format (no other text):
[
  {{
    "start_time": 123.45,
    "end_time": 180.90,
    "title": "Short engaging title",
    "hook": "The hook/attention grabber from first 3 seconds",
    "reason": "Why this clip will go viral"
  }}
]"""

    def _parse_clip_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into clip dicts"""

        try:
            # Try to extract JSON
            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                clips = json.loads(json_match.group())
                return clips
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")

        return []

    def generate_title(self, transcript_segment: str) -> str:
        """Generate engaging title for a clip"""

        prompt = f"""Generate a short, engaging title (max 60 characters) for this video segment:

"{transcript_segment}"

Return ONLY the title, no explanation."""

        return self.generate(prompt).strip().strip('"')

    def generate_description(self, transcript_segment: str) -> str:
        """Generate description for a clip"""

        prompt = f"""Generate a short description (max 200 characters) for this video segment:

"{transcript_segment}"

Return ONLY the description, no explanation."""

        return self.generate(prompt).strip().strip('"')

    def analyze_content(self, transcript: str) -> Dict[str, Any]:
        """Analyze overall content for insights"""

        prompt = f"""Analyze this video transcript and provide insights:

{transcript}

Return ONLY a JSON object with this structure:
{{
  "main_topics": ["topic1", "topic2"],
  "emotional_tone": "neutral/positive/negative/mixed",
  "target_audience": "description of likely audience",
  "key_moments": ["moment1", "moment2"],
  "engagement_score": 0-10
}}"""

        try:
            response = self.generate(prompt)
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {}


class ViralIntelligence:
    """
    Advanced viral intelligence layer
    Provides engagement scoring, hook optimization, and clip ranking
    """

    def __init__(self, llm: Optional[LLMInterface] = None):
        self.llm = llm

    def score_clip(
        self, text: str, start_time: float, end_time: float
    ) -> Dict[str, Any]:
        """
        Score a clip for viral potential

        Returns:
            Dict with scores and recommendations
        """
        scores = {}

        # Hook score (first 3 seconds)
        hook_text = text[:200] if len(text) > 200 else text
        scores["hook_score"] = self._score_hook(hook_text)

        # Emotion score
        scores["emotion_score"] = self._score_emotion(text)

        # Controversy score
        scores["controversy_score"] = self._score_controversy(text)

        # Clarity score
        scores["clarity_score"] = self._score_clarity(text)

        # Duration penalty
        duration = end_time - start_time
        if duration > 60:
            scores["duration_score"] = 0.5
        elif duration < 20:
            scores["duration_score"] = 0.6
        else:
            scores["duration_score"] = 1.0

        # Overall score
        weights = {
            "hook_score": 0.3,
            "emotion_score": 0.2,
            "controversy_score": 0.2,
            "clarity_score": 0.2,
            "duration_score": 0.1,
        }

        overall = sum(scores[k] * weights[k] for k in weights)
        scores["overall_score"] = round(overall, 2)

        # Recommendations
        scores["recommendations"] = self._get_recommendations(scores)

        return scores

    def _score_hook(self, text: str) -> float:
        """Score the hook strength"""

        hook_words = [
            "wait",
            "listen",
            "actually",
            "really",
            "truth",
            "shocking",
            "secret",
            "believe",
            "never",
            "always",
            "here's",
            "actually",
            "surprising",
            "unexpected",
            "reveal",
            "answer",
            "question",
            "why",
            "how",
        ]

        text_lower = text.lower()
        hook_count = sum(1 for w in hook_words if w in text_lower)

        # Start with base score
        score = 0.3 + min(hook_count * 0.15, 0.5)

        # Question at start = higher score
        if text.strip().startswith("?"):
            score += 0.2

        return min(score, 1.0)

    def _score_emotion(self, text: str) -> float:
        """Score emotional content"""

        emotion_words = {
            "high": [
                "!",
                "amazing",
                "incredible",
                "love",
                "excited",
                "brilliant",
                "fantastic",
            ],
            "medium": ["important", "interesting", "really", "actually"],
            "low": ["okay", "so", "basically", "basically"],
        }

        text_lower = text.lower()

        high_count = sum(1 for w in emotion_words["high"] if w in text_lower)
        medium_count = sum(1 for w in emotion_words["medium"] if w in text_lower)

        score = 0.2 + high_count * 0.2 + medium_count * 0.1

        return min(score, 1.0)

    def _score_controversy(self, text: str) -> float:
        """Score controversial content"""

        controversy_words = [
            "wrong",
            "mistake",
            "lie",
            "fake",
            "scam",
            "actually",
            "really",
            "belief",
            "disagree",
            "controversial",
            "debate",
            "argument",
        ]

        text_lower = text.lower()
        count = sum(1 for w in controversy_words if w in text_lower)

        return min(0.3 + count * 0.15, 1.0)

    def _score_clarity(self, text: str) -> float:
        """Score clarity of content"""

        # Short sentences = clearer
        sentences = text.split(".")
        avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

        if avg_length < 15:
            return 1.0
        elif avg_length < 25:
            return 0.8
        else:
            return 0.5

    def _get_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Get improvement recommendations"""

        recommendations = []

        if scores.get("hook_score", 0) < 0.5:
            recommendations.append("Add a stronger hook in first 3 seconds")

        if scores.get("emotion_score", 0) < 0.4:
            recommendations.append("Add more emotional language")

        if scores.get("clarity_score", 0) < 0.7:
            recommendations.append("Simplify sentences for better clarity")

        if not recommendations:
            recommendations.append("Clip looks good! Consider adding captions")

        return recommendations

    def rank_clips(self, clips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank clips by viral potential"""

        scored_clips = []

        for clip in clips:
            text = clip.get("text", clip.get("hook", ""))
            scores = self.score_clip(
                text, clip.get("start_time", 0), clip.get("end_time", 0)
            )

            scored_clips.append(
                {**clip, "viral_scores": scores, "rank_score": scores["overall_score"]}
            )

        # Sort by rank score
        scored_clips.sort(key=lambda x: x["rank_score"], reverse=True)

        return scored_clips


# Convenience functions


def create_llm_interface(
    provider: str = "openai", api_key: Optional[str] = None, model: Optional[str] = None
) -> LLMInterface:
    """Create LLM interface"""
    return LLMInterface(provider, api_key, model)


def create_viral_intelligence(llm: Optional[LLMInterface] = None) -> ViralIntelligence:
    """Create viral intelligence engine"""
    return ViralIntelligence(llm)


if __name__ == "__main__":
    # Test
    interface = LLMInterface("openai")
    print(f"LLM Interface loaded")
    print(f"Provider available: {interface.is_available()}")

    viral = ViralIntelligence()
    print("ViralIntelligence loaded")
