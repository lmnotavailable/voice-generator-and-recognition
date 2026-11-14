#!/usr/bin/env python3
"""Verbatim transcription with CrisperWhisper 2 and word timestamps."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path, help="audio file (WAV/FLAC recommended)")
    parser.add_argument("--output", type=Path, default=Path("result-verbatim.json"))
    parser.add_argument("--language", default="ru", help="language code, e.g. ru; use auto to detect")
    parser.add_argument("--model", choices=["small", "medium", "large", "turbo"], default="small")
    parser.add_argument("--mode", choices=["verbatim", "intended"], default="verbatim")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--compute-type", choices=["float16", "float32"], default="float16")
    parser.add_argument("--no-word-confidence", action="store_true",
                        help="omit token confidence and word timestamps")
    args = parser.parse_args()

    if not args.audio.is_file():
        parser.error(f"audio file not found: {args.audio}")
    if args.output.suffix.lower() != ".json":
        parser.error("--output must end with .json (a companion .txt is saved automatically)")
    if args.audio.resolve() in {args.output.resolve(), args.output.with_suffix(".txt").resolve()}:
        parser.error("output must not overwrite the input audio")

    try:
        from crisperwhisper import CrisperWhisperModel

        # The Transformers backend supports macOS/Apple Silicon and CPU inference.
        print(f"Loading CrisperWhisper 2.0 {args.model}; first run downloads model weights.", flush=True)
        model = CrisperWhisperModel(args.model, backend="transformers",
                                   device=args.device, compute_type=args.compute_type)
        print(f"Transcribing {args.audio} in {args.mode} mode...", flush=True)
        language = None if args.language.lower() == "auto" else args.language
        result = model.transcribe(
            str(args.audio),
            language=language,
            mode=args.mode,
            word_confidence=not args.no_word_confidence,
        )
        mode = args.mode

        events = []
        words = getattr(result, "words", None) or []
        for word in words:
            item = {
                "type": "token",
                "text": word.word,
                "start": round(float(word.start), 3),
                "end": round(float(word.end), 3),
            }
            probability = getattr(word, "probability", None)
            if probability is not None:
                item["confidence"] = round(float(probability), 4)
            events.append(item)

        payload = {
            "audio": str(args.audio),
            "duration": round(float(getattr(result, "duration", 0.0) or 0.0), 3),
            "language": getattr(result, "language", language),
            "mode": mode,
            "transcript": result.text,
            "events": events,
            "model": f"CrisperWhisper 2.0 {args.model} (Transformers)",
            "notes": [
                "Verbatim mode aims to retain fillers, repetitions, false starts, stutters and vocal events.",
                "Word confidence is a model score, not a calibrated probability of correctness.",
                "The transcript's event labels are model output and may omit or misclassify sounds; validate against audio.",
            ],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        text_output = args.output.with_suffix(".txt")
        text_output.write_text(result.text.strip() + "\n", encoding="utf-8")
        print(f"Saved transcript and {len(events)} timed tokens to {args.output.resolve()}")
        print(f"Saved readable transcript to {text_output.resolve()}")
        return 0
    except KeyboardInterrupt:
        print("Transcription cancelled.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Transcription failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
