"""Story scripts: load, validate, and time the scenes.

A story is JSON:

{
  "title": "the corner three",
  "scenes": [
    {"text": "on-screen text for the scene",
     "narration": "optional spoken text (defaults to text)",
     "duration": 4.5,                       // optional seconds
     "bg": "#101018", "accent": "#e8722a"}  // optional colors
  ]
}
"""

import json

DEFAULT_BG = "#101018"
DEFAULT_ACCENT = "#e8722a"
WORDS_PER_SECOND = 2.4      # calm narration pace
MIN_SCENE_SECONDS = 2.0
PAD_SECONDS = 0.8


class Scene:
    def __init__(self, text, narration=None, duration=None,
                 bg=DEFAULT_BG, accent=DEFAULT_ACCENT):
        if not text or not text.strip():
            raise ValueError("scene text must not be empty")
        self.text = text.strip()
        self.narration = (narration or text).strip()
        self.duration = duration
        self.bg = bg
        self.accent = accent

    def resolved_duration(self):
        """Explicit duration, or an estimate from the narration length."""
        if self.duration is not None:
            if self.duration <= 0:
                raise ValueError("scene duration must be positive")
            return float(self.duration)
        words = len(self.narration.split())
        return max(MIN_SCENE_SECONDS, words / WORDS_PER_SECOND + PAD_SECONDS)


class Story:
    def __init__(self, title, scenes):
        if not title or not title.strip():
            raise ValueError("story title must not be empty")
        if not scenes:
            raise ValueError("a story needs at least one scene")
        self.title = title.strip()
        self.scenes = scenes

    def total_seconds(self):
        return sum(s.resolved_duration() for s in self.scenes)


def load_story(path):
    with open(path) as f:
        raw = json.load(f)
    scenes = [
        Scene(
            text=s["text"],
            narration=s.get("narration"),
            duration=s.get("duration"),
            bg=s.get("bg", DEFAULT_BG),
            accent=s.get("accent", DEFAULT_ACCENT),
        )
        for s in raw["scenes"]
    ]
    return Story(title=raw["title"], scenes=scenes)
