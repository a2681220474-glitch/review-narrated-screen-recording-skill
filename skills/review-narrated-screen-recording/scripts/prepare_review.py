#!/usr/bin/env python3
"""Prepare timestamped audio, frames, contact sheets, and Whisper output for review."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        text=True,
        capture_output=capture,
    )


def require(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"Required command not found: {name}")
    return path


def probe(video: Path) -> dict:
    result = run(
        [
            require("ffprobe"),
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(video),
        ],
        capture=True,
    )
    return json.loads(result.stdout)


def duration_seconds(metadata: dict) -> float:
    value = metadata.get("format", {}).get("duration")
    if value is not None:
        return float(value)
    durations = [
        float(stream["duration"])
        for stream in metadata.get("streams", [])
        if stream.get("duration") is not None
    ]
    if not durations:
        raise RuntimeError("Could not determine video duration")
    return max(durations)


def timestamp(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def parse_srt_time(value: str) -> float:
    hours, minutes, rest = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)


def parse_srt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        return []
    segments: list[dict] = []
    pattern = re.compile(
        r"(?:^|\n\s*\n)(\d+)\s*\n"
        r"(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*"
        r"(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*\n"
        r"(.*?)(?=\n\s*\n|\Z)",
        re.S,
    )
    for match in pattern.finditer(text):
        start = parse_srt_time(match.group(2))
        end = parse_srt_time(match.group(3))
        segments.append(
            {
                "index": int(match.group(1)),
                "start": start,
                "end": end,
                "start_time": timestamp(start),
                "end_time": timestamp(end),
                "text": " ".join(match.group(4).split()),
            }
        )
    return segments


def nearest_frame(seconds: float, interval: float, frame_count: int) -> int:
    index = int(round(seconds / interval)) + 1
    return max(1, min(index, frame_count))


def drawtext_font_option() -> str:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return f"fontfile={candidate}:"
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--language", default="zh")
    parser.add_argument("--model", type=Path)
    parser.add_argument("--prompt", default="")
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--rows", type=int, default=3)
    parser.add_argument("--thumb-width", type=int, default=270)
    args = parser.parse_args()

    video = args.video.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not video.is_file():
        raise RuntimeError(f"Video not found: {video}")
    if args.interval <= 0:
        raise RuntimeError("--interval must be greater than zero")
    if args.columns <= 0 or args.rows <= 0:
        raise RuntimeError("--columns and --rows must be greater than zero")

    ffmpeg = require("ffmpeg")
    output.mkdir(parents=True, exist_ok=True)
    frames_dir = output / "frames"
    sheets_dir = output / "sheets"
    frames_dir.mkdir(exist_ok=True)
    sheets_dir.mkdir(exist_ok=True)
    for stale in frames_dir.glob("frame_*.jpg"):
        stale.unlink()
    for stale in sheets_dir.glob("sheet_*.jpg"):
        stale.unlink()

    metadata = probe(video)
    duration = duration_seconds(metadata)
    (output / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    audio = output / "audio-16k.wav"
    run(
        [
            ffmpeg,
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(audio),
        ]
    )

    fps_filter = f"fps=1/{args.interval}"
    run(
        [
            ffmpeg,
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-vf",
            fps_filter,
            "-q:v",
            "2",
            str(frames_dir / "frame_%06d.jpg"),
        ]
    )

    time_label = (
        f"drawtext={drawtext_font_option()}text='%{{pts\\:hms}}':x=8:y=8:fontsize=22:"
        "fontcolor=white:box=1:boxcolor=black@0.65"
    )
    tile_filter = (
        f"{fps_filter},scale={args.thumb_width}:-2,{time_label},"
        f"tile={args.columns}x{args.rows}:padding=8:margin=8:color=white"
    )
    run(
        [
            ffmpeg,
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-vf",
            tile_filter,
            "-fps_mode",
            "vfr",
            "-q:v",
            "3",
            str(sheets_dir / "sheet_%04d.jpg"),
        ]
    )

    frame_paths = sorted(frames_dir.glob("frame_*.jpg"))
    manifest = [
        {
            "index": index,
            "timestamp": min((index - 1) * args.interval, duration),
            "time": timestamp(min((index - 1) * args.interval, duration)),
            "path": str(path),
        }
        for index, path in enumerate(frame_paths, start=1)
    ]
    (output / "frame-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    transcript_state = {"status": "not_requested"}
    model = args.model or (Path(os.environ["WHISPER_MODEL"]) if os.getenv("WHISPER_MODEL") else None)
    if model:
        model = model.expanduser().resolve()
        if not model.is_file():
            raise RuntimeError(f"Whisper model not found: {model}")
        whisper = require("whisper-cli")
        transcript_base = output / "transcript"
        command = [
            whisper,
            "-ng",
            "-m",
            str(model),
            "-f",
            str(audio),
            "-l",
            args.language,
            "-osrt",
            "-otxt",
            "-ojf",
            "-of",
            str(transcript_base),
        ]
        if args.prompt:
            command.extend(["--prompt", args.prompt])
        run(command)
        transcript_state = {"status": "complete", "model": str(model)}

    (output / "transcription-status.json").write_text(
        json.dumps(transcript_state, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    srt = output / "transcript.srt"
    if srt.is_file():
        segments = parse_srt(srt)
        for segment in segments:
            midpoint = (segment["start"] + segment["end"]) / 2
            frame_index = nearest_frame(midpoint, args.interval, len(frame_paths))
            nearby = range(max(1, frame_index - 2), min(len(frame_paths), frame_index + 2) + 1)
            segment["nearest_frame"] = str(frames_dir / f"frame_{frame_index:06d}.jpg")
            segment["nearby_frames"] = [
                str(frames_dir / f"frame_{index:06d}.jpg") for index in nearby
            ]
        (output / "timeline.json").write_text(
            json.dumps(segments, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    summary = {
        "video": str(video),
        "duration_seconds": duration,
        "duration": timestamp(duration),
        "interval_seconds": args.interval,
        "frame_count": len(frame_paths),
        "sheet_count": len(list(sheets_dir.glob("sheet_*.jpg"))),
        "transcription": transcript_state,
        "output": str(output),
    }
    (output / "review-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
