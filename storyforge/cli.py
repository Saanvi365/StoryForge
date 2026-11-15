"""Command line interface for StoryForge."""

import argparse
import os
import sys

from .assemble import build_video
from .narrate import available_voice, narrate
from .render import render_scene, render_title_card
from .script import load_story


def cmd_build(args):
    story = load_story(args.story)
    voice = None if args.silent else available_voice()

    workdir = os.path.join(args.out_dir, "frames")
    os.makedirs(workdir, exist_ok=True)

    if voice:
        print(f"narration voice: {voice}")
    elif not args.silent:
        print("no tts engine found (espeak / say) - building a silent video")

    pieces = []
    title_card = os.path.join(workdir, "title.png")
    render_title_card(story, title_card)
    pieces.append((title_card, args.title_seconds, None))

    total = len(story.scenes)
    for i, scene in enumerate(story.scenes, 1):
        frame = os.path.join(workdir, f"scene_{i:03d}.png")
        render_scene(scene, frame, index=i, total=total)

        audio = None
        if voice:
            wav = os.path.join(workdir, f"scene_{i:03d}.wav")
            if narrate(scene.narration, wav, voice):
                audio = wav
        seconds = scene.resolved_duration()
        pieces.append((frame, seconds, audio))
        print(f"scene {i}/{total}: {seconds:.1f}s"
              + (" (narrated)" if audio else ""))

    out_path = os.path.join(args.out_dir, args.out)
    build_video(pieces, out_path, workdir=os.path.join(args.out_dir, "clips"))
    print(f"\n{story.title!r}: {total} scenes, "
          f"~{story.total_seconds() + args.title_seconds:.0f}s -> {out_path}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="storyforge",
        description="Turn a written story into a narrated video.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build", help="build a video from a story JSON file")
    p.add_argument("story", help="path to story JSON")
    p.add_argument("--out", default="story.mp4", help="output filename")
    p.add_argument("--out-dir", default="out", help="output directory")
    p.add_argument("--title-seconds", type=float, default=2.5)
    p.add_argument("--silent", action="store_true",
                   help="skip narration even if a voice is available")
    p.set_defaults(func=cmd_build)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
