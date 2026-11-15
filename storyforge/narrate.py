"""Narration: turn scene narration into wav audio, when a voice is available.

Uses whatever offline TTS the machine has - espeak/espeak-ng on Linux,
say(1) on macOS. With no voice available the pipeline still works: scenes
just render silent, and the video carries the story on screen.
"""

import shutil
import subprocess
import tempfile


def available_voice():
    """Name of the usable TTS engine, or None."""
    for tool in ("espeak-ng", "espeak", "say"):
        if shutil.which(tool):
            return tool
    return None


def narrate(text, out_wav, voice=None):
    """Synthesize text to out_wav. Returns True on success, False if no voice."""
    voice = voice or available_voice()
    if voice is None:
        return False
    try:
        if voice == "say":
            # say writes aiff; convert happens at assembly (ffmpeg reads aiff)
            subprocess.run(
                ["say", "-o", out_wav, "--data-format=LEI16@22050", text],
                check=True, capture_output=True, timeout=60,
            )
        else:
            subprocess.run(
                [voice, "-w", out_wav, text],
                check=True, capture_output=True, timeout=60,
            )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False
    return True
