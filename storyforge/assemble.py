"""Assembly: frames (+ optional narration) -> one mp4, via ffmpeg."""

import os
import subprocess


def _scene_clip(image_path, seconds, out_path, audio_path=None):
    """One scene: loop a still image for `seconds`, optional voiceover."""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
    ]
    if audio_path:
        cmd += ["-i", audio_path]
    cmd += [
        "-t", f"{seconds:.2f}",
        "-vf", "scale=1280:720,fps=24,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast",
    ]
    if audio_path:
        cmd += ["-c:a", "aac", "-shortest"]
    else:
        cmd += ["-an"]
    cmd += [out_path]
    subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    return out_path


def build_video(pieces, out_path, workdir):
    """pieces: [(image_path, seconds, audio_path_or_None)] in order."""
    os.makedirs(workdir, exist_ok=True)
    clips = []
    for i, (image, seconds, audio) in enumerate(pieces):
        clip = os.path.join(workdir, f"clip_{i:03d}.mp4")
        _scene_clip(image, seconds, clip, audio)
        clips.append(clip)

    manifest = os.path.join(workdir, "concat.txt")
    with open(manifest, "w") as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", manifest, "-c", "copy", out_path],
        check=True, capture_output=True, timeout=180,
    )
    return out_path
