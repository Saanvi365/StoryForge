import json
import os
import shutil
import subprocess
import tempfile
import unittest

from storyforge.render import render_scene, render_title_card, wrap_text
from storyforge.script import Scene, Story, load_story
from storyforge.narrate import available_voice, narrate


STORY_JSON = {
    "title": "test story",
    "scenes": [
        {"text": "a short opening line"},
        {"text": "a scene with explicit duration", "duration": 3.0},
        {"text": "on screen words", "narration": "different spoken words"},
    ],
}


def _write_story(tmpdir, data=None):
    path = os.path.join(tmpdir, "story.json")
    with open(path, "w") as f:
        json.dump(data or STORY_JSON, f)
    return path


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_load_story(self):
        story = load_story(_write_story(self.tmp))
        self.assertEqual(story.title, "test story")
        self.assertEqual(len(story.scenes), 3)

    def test_narration_defaults_to_text(self):
        s = Scene("same words")
        self.assertEqual(s.narration, "same words")

    def test_explicit_duration_wins(self):
        s = Scene("text", duration=3.0)
        self.assertEqual(s.resolved_duration(), 3.0)

    def test_estimated_duration_scales_with_words(self):
        short = Scene("two words").resolved_duration()
        long = Scene("word " * 30).resolved_duration()
        self.assertGreater(long, short)

    def test_estimated_duration_has_floor(self):
        self.assertGreaterEqual(Scene("hi").resolved_duration(), 2.0)

    def test_empty_scene_rejected(self):
        with self.assertRaises(ValueError):
            Scene("   ")

    def test_empty_story_rejected(self):
        with self.assertRaises(ValueError):
            Story("title", [])

    def test_bad_duration_rejected(self):
        with self.assertRaises(ValueError):
            Scene("text", duration=0).resolved_duration()


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_wrap_text(self):
        lines = wrap_text("word " * 50, width=20)
        self.assertTrue(all(len(l) <= 21 for l in lines))
        self.assertGreater(len(lines), 1)

    def test_render_scene_png(self):
        out = os.path.join(self.tmp, "s.png")
        render_scene(Scene("hello there"), out, index=1, total=2)
        self.assertGreater(os.path.getsize(out), 1000)

    def test_render_title_card(self):
        out = os.path.join(self.tmp, "t.png")
        render_title_card(Story("my title", [Scene("x")]), out)
        self.assertGreater(os.path.getsize(out), 1000)


class NarrateTests(unittest.TestCase):
    def test_no_voice_returns_false(self):
        self.assertFalse(narrate("hello", "/tmp/x.wav", voice=None)
                         if available_voice() is None else False)


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg not installed")
class EndToEndTests(unittest.TestCase):
    def test_full_build_produces_playable_video(self):
        from storyforge.cli import main

        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        story_path = _write_story(tmp)
        out_dir = os.path.join(tmp, "out")

        rc = main(["build", story_path, "--out-dir", out_dir, "--silent"])
        self.assertEqual(rc, 0)

        mp4 = os.path.join(out_dir, "story.mp4")
        self.assertTrue(os.path.exists(mp4))
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "csv=p=0", mp4],
            capture_output=True, text=True, check=True,
        )
        duration = float(probe.stdout.strip())
        # title card (2.5s) + 3 scenes, each >= 2s
        self.assertGreaterEqual(duration, 8.0)


if __name__ == "__main__":
    unittest.main()
