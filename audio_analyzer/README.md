# Распознавание речи с CrisperWhisper 2.0

Скрипт принимает аудиозапись и сохраняет дословную расшифровку с временными метками. Используется CrisperWhisper 2.0 в режиме `verbatim`: модель старается записать повторы, запинки, заполнители пауз и звуки вроде `[lipsmack]`, которые обычное распознавание часто пропускает.

Результат состоит из двух файлов: **TXT для чтения** и **JSON для анализа**. Текстовый эталон или API-ключ для запуска не нужны.

## Что понадобится

- 64-битный Python **3.10 или 3.11**. Установщик: [python.org](https://www.python.org/downloads/).
- Интернет для установки пакетов и первого скачивания модели с Hugging Face.
- Несколько гигабайт свободного места под окружение и веса. Файл весов `small` занимает примерно 484 МБ.

Проект проверен на Mac с Apple Silicon и Python 3.10.10. Закреплённая сборка PyTorch требует на таком Mac **macOS 14 или новее**. Для Intel Mac этот набор зависимостей не подходит. Ниже также приведены команды для Windows и Linux; на этих системах запуск пока не проверялся.

Видеокарта не обязательна. На CPU длинные записи могут обрабатываться несколько минут.

## Установка

### macOS и Linux

Откройте Terminal. Скачайте ветку и перейдите в папку распознавателя:

```bash
git clone --branch voice-recognition --single-branch https://github.com/lmnotavailable/voice-generator-and-recognition.git
cd voice-generator-and-recognition/audio_analyzer
```

Создайте отдельное окружение и установите зависимости:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

Перед созданием окружения убедитесь, что `python3 --version` показывает 3.10.x или 3.11.x. Если нужная версия установлена как `python3.11`, используйте `python3.11 -m venv .venv`. В некоторых дистрибутивах Linux предварительно нужен пакет `python3-venv` для выбранной версии Python.

После активации перед приглашением Terminal появится `(.venv)`. Успешный `pip check` выводит `No broken requirements found`.

### Windows — PowerShell

Установите Python 3.11, затем выполните:

```powershell
git clone --branch voice-recognition --single-branch https://github.com/lmnotavailable/voice-generator-and-recognition.git
cd voice-generator-and-recognition/audio_analyzer
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Здесь Python окружения вызывается напрямую, поэтому активация и изменение настроек PowerShell не нужны.

Если Git не установлен, на GitHub выберите ветку `voice-recognition`, нажмите **Code → Download ZIP** и распакуйте архив. Откройте терминал в папке `audio_analyzer` и выполните команды установки, начиная с создания `.venv`.

У распознавателя и генератора Qwen отдельные окружения. В этой папке нужен только её `requirements.txt`; устанавливать зависимости генератора для распознавания не требуется.

## Первый запуск

Через Finder или Проводник скопируйте запись в папку `audio_analyzer` рядом с `analyze.py`. В примерах она называется `audio.wav` — замените это имя на своё. Для первого запуска рекомендуется **WAV**; переименование расширения не конвертирует запись.

**macOS / Linux:**

```bash
source .venv/bin/activate
python analyze.py "audio.wav" --language ru --model small --mode verbatim --device cpu --compute-type float32 --output outputs/result.json
```

**Windows:**

```powershell
.\.venv\Scripts\python.exe analyze.py "audio.wav" --language ru --model small --mode verbatim --device cpu --compute-type float32 --output outputs/result.json
```

В этих командах указан CPU и `float32` для совместимости. На проверенном Mac также работал `float16`; его можно выбрать параметром `--compute-type float16`.

При первом запуске автоматически скачивается модель `nyralabs/CrisperWhisper2.0_small`. После загрузки весов программа приступает к распознаванию. Дождитесь строк:

```text
Saved transcript and ... timed tokens to .../outputs/result.json
Saved readable transcript to .../outputs/result.txt
```

## Где лежит результат

Папка `outputs` создаётся внутри `audio_analyzer` автоматически:

| Файл | Содержимое |
|---|---|
| `outputs/result.txt` | Расшифровка обычным текстом, включая распознанные повторы и метки звуков. |
| `outputs/result.json` | Текст, длительность, язык, название модели и временные метки слов/событий. |

Для каждой новой записи можно задать своё имя, например `--output outputs/interview.json`. Рядом появится `interview.txt`. Если повторно указать то же имя, **оба файла будут перезаписаны**.

В JSON поле `transcript` содержит полный текст, а `events` — его временную разметку. Пример одного элемента, с условными значениями:

```json
{
  "type": "token",
  "text": "[lipsmack]",
  "start": 12.34,
  "end": 12.48,
  "confidence": 0.58
}
```

`start` и `end` отсчитываются в секундах от начала записи. `confidence` — оценка модели, а не гарантия правильности. Метки `[UH]`, `[lipsmack]` и другие входят в саму расшифровку.

## Следующие запуски

Снова откройте терминал в папке `audio_analyzer`. На macOS/Linux активируйте `.venv`, затем повторите команду распознавания с новым именем записи и результата. На Windows вызывайте `.\.venv\Scripts\python.exe`, как в примере выше.

Устанавливать библиотеки заново не нужно. Веса сохраняются в кеше Hugging Face, обычно `~/.cache/huggingface/hub`. Если они полностью скачаны, можно отключить сетевые проверки перед запуском:

```bash
# macOS / Linux
export HF_HUB_OFFLINE=1
```

```powershell
# Windows
$env:HF_HUB_OFFLINE="1"
```

Чтобы скачать другую модель, отключите этот режим: `unset HF_HUB_OFFLINE` в macOS/Linux или `Remove-Item Env:HF_HUB_OFFLINE` в PowerShell.

## Настройки

| Параметр | Значение |
|---|---|
| `--language ru` | Русская речь. `auto` — автоматическое определение языка. |
| `--model small` | Размер модели. Доступны также `medium`, `large`, `turbo`; их веса скачиваются отдельно. |
| `--mode verbatim` | Дословная расшифровка. `intended` — очищенный текст. |
| `--output outputs/result.json` | Путь к JSON. TXT сохраняется рядом автоматически. |
| `--device auto` | Выбор CUDA при наличии, иначе CPU. Можно указать `cpu` или `cuda`. |
| `--compute-type float16` | Точность вычислений по умолчанию. Для CPU в примерах используется `float32`. |
| `--no-word-confidence` | Отключает оценки слов **и временные метки**. Для анализа событий не используйте. |

Полная справка: `python analyze.py --help`. На Windows замените `python` на `.\.venv\Scripts\python.exe`.

## Если возникла ошибка

| Сообщение | Что проверить |
|---|---|
| `audio file not found` | Имя записи и текущую папку. Список файлов покажет `ls` или `dir`. Пути с пробелами заключайте в кавычки. |
| `ModuleNotFoundError: crisperwhisper` | Активировано ли нужное `.venv` и выполнена ли установка из `audio_analyzer/requirements.txt`. |
| `No matching distribution found` | Версию Python и поддержку платформы. Прочитайте строки выше ошибки: причиной также бывает отсутствие сети. |
| Ошибка доступа к PyPI или Hugging Face | Соединение с интернетом. Первый запуск без загрузки весов не сработает. |
| `Operation not permitted` на Mac | Разрешите Terminal доступ к папке с записью либо перенесите файл через Finder в `audio_analyzer`. |
| Ошибка чтения аудио | Экспортируйте запись в WAV. Для WAV отдельная установка FFmpeg не нужна. |
| Ошибка FP16 на CPU | Укажите `--device cpu --compute-type float32`. |
| Недостаточно памяти | Выберите `small` и закройте другие тяжёлые программы. |

Предупреждения Transformers могут появляться и при успешном запуске. Результат считается сохранённым после строк `Saved...`; при сбое скрипт пишет `Transcription failed...`.

## Проверка и ограничения

На русской записи длиной 144,4 секунды модель `small` выдала 257 фрагментов с временными метками, сохранила повтор «я я» и добавила `[lipsmack]` и `[UH]`. Дополнительно проверен запуск на коротком WAV в режиме CPU/float32 с сохранением JSON и TXT. Для закреплённых зависимостей выполнена проверка разрешения пакетов с PyPI без использования уже установленных библиотек.

Эти результаты не заменяют сравнение с эталоном: модель может пропускать или добавлять слова и звуки. Отдельные интервалы тишины скрипт не размечает. Промежуток между временными метками слов не обязательно является паузой.

## Модель и лицензия

Стандартные веса CrisperWhisper 2.0 опубликованы под **Nyra Health Non-Commercial Research License**. У кода библиотеки и модельных весов разные лицензии; Pro-модели имеют отдельные условия.

- [CrisperWhisper: репозиторий](https://github.com/nyrahealth/CrisperWhisper)
- [Документация API](https://github.com/nyrahealth/CrisperWhisper/blob/main/DOCS.md)
- [Карточка модели small](https://huggingface.co/nyralabs/CrisperWhisper2.0_small)
