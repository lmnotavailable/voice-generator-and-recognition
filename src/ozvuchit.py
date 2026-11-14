#!/usr/bin/env python3
"""Generate Russian speech from a UTF-8 text file with a local Qwen3-TTS model."""

from __future__ import annotations

import argparse
import os
import shlex
from pathlib import Path
import sys

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

DEFAULT_STYLE = (
    "Speak Russian at a brisk, lively conversational pace, slightly faster than ordinary narration, "
    "but keep every word clear. Sound spontaneous and informal, as if telling a friend a story. "
    "Use natural connected phrasing, varied intonation, occasional hesitation, and short conversational pauses. "
    "Avoid a slow, solemn audiobook narrator style."
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Озвучить русский .txt-файл локальной моделью Qwen3-TTS.")
    parser.add_argument("text_file", nargs="?", help="Путь к текстовому файлу UTF-8")
    parser.add_argument("-o", "--output", help="Путь для WAV; по умолчанию рядом с исходным текстом")
    parser.add_argument("--model", help="Путь к папке Qwen3-TTS VoiceDesign; можно задать QWEN_TTS_MODEL")
    parser.add_argument("--style", default=DEFAULT_STYLE, help="Описание желаемой манеры речи")
    args = parser.parse_args()

    input_value = args.text_file
    if not input_value:
        raw_value = input("Путь к .txt-файлу (можно перетащить файл сюда): ").strip()
        if raw_value:
            try:
                paths = shlex.split(raw_value)
            except ValueError as exc:
                parser.error(f"Не удалось прочитать путь: {exc}")
            if len(paths) != 1:
                parser.error("Укажите один файл. Путь с пробелами заключите в кавычки.")
            input_value = paths[0]
    if not input_value:
        parser.error("Не указан текстовый файл")

    input_path = Path(input_value).expanduser()
    if not input_path.is_file():
        parser.error(f"Файл не найден: {input_path}")
    if input_path.suffix.lower() != ".txt":
        parser.error("Ожидается файл с расширением .txt")

    try:
        text = input_path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        parser.error("Файл должен быть сохранён в кодировке UTF-8")
    if not text:
        parser.error("Текстовый файл пуст")

    model_value = args.model or os.environ.get("QWEN_TTS_MODEL")
    if not model_value:
        model_value = str(Path.home() / "qwen-models" / "Qwen3-TTS-12Hz-1.7B-VoiceDesign")
    model_dir = Path(model_value).expanduser()
    if not model_dir.is_dir():
        parser.error(f"Не найдена папка модели: {model_dir}")

    output_path = Path(args.output).expanduser() if args.output else input_path.with_name(f"{input_path.stem}_озвучка.wav")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Модель: {model_dir}")
    print(f"Текст:  {input_path}")
    print(f"WAV:    {output_path}")
    print("Загружаю модель и начинаю синтез. На CPU длинный текст может обрабатываться несколько минут.")

    model = Qwen3TTSModel.from_pretrained(
        str(model_dir),
        device_map="cpu",
        dtype=torch.float32,
    )
    waveforms, sample_rate = model.generate_voice_design(
        text=text,
        language="Russian",
        instruct=args.style,
    )
    sf.write(str(output_path), waveforms[0], sample_rate)
    print(f"Готово: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
