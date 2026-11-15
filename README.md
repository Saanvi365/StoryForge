# StoryForge

Turn a written story into a narrated video. Write a story as JSON scenes, and
StoryForge renders each scene as a cinematic title card, generates voiceover
for it, and stitches everything into one mp4.

## how it works

```
story.json ──> script.py ──> render.py ──> narrate.py ──> assemble.py ──> story.mp4
             (load/validate  (Pillow       (espeak/say    (ffmpeg
              + time scenes)  frames)       voiceover)     stitching)
```

1. **script.py** loads the story and gives every scene a duration - explicit
   if you set one, otherwise estimated from the narration length at a calm
   speaking pace.
2. **render.py** draws each scene as a 1280x720 frame with Pillow: wrapped
   text, an accent spine, scene numbering, plus a title card to open.
3. **narrate.py** synthesizes voiceover per scene with whatever offline TTS
   the machine has - `espeak` on Linux, `say` on macOS. No voice installed?
   The pipeline still works; the video just carries the story on screen.
4. **assemble.py** loops each frame for its duration with ffmpeg, muxes in
   the voiceover, and concatenates the clips into one mp4.

## quick start

```bash
pip3 install -r requirements.txt
brew install ffmpeg        # or: sudo apt install ffmpeg espeak

python3 -m storyforge.cli build examples/corner_three.json --out-dir out
# -> out/story.mp4
```

Use `--silent` to skip narration even when a voice is available.

## the story format

```json
{
  "title": "the corner three",
  "scenes": [
    {
      "text": "the gym is empty except for one ball and one kid",
      "narration": "optional: different words for the voiceover",
      "duration": 4.0,
      "bg": "#101018",
      "accent": "#e8722a"
    }
  ]
}
```

Only `text` is required. `narration` defaults to `text`; `duration` is
estimated from word count when omitted; `bg` and `accent` have defaults.

## tests

```bash
python3 -m unittest discover -s tests -v
```

Pure-logic tests cover script loading, validation, and duration estimates;
render tests verify the PNG frames; with ffmpeg installed, an end-to-end
test builds a real video and probes its duration with ffprobe.

## project structure

```
storyforge/
  __init__.py
  script.py     # story loading, validation, scene timing
  render.py     # Pillow frame + title-card rendering
  narrate.py    # optional offline TTS voiceover
  assemble.py   # ffmpeg clip building and concatenation
  cli.py        # `python3 -m storyforge.cli build ...`
examples/
  corner_three.json
tests/
  test_storyforge.py
```
