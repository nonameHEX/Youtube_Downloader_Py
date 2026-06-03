# AGENTS.md

## Project Overview

This is a small Python CLI application for downloading YouTube video/audio.
It uses `yt-dlp` for downloads, `imageio-ffmpeg`/FFmpeg for conversion, `mutagen`
for MP3 metadata, `Pillow`/`requests` for cover thumbnails, and `colorama` for
colored console output.

Main files:

- `main.py` is the application entry point. It parses the optional output
  directory argument, creates the default `YTDownload` directory when needed,
  sizes the console, and runs the interactive menu loop.
- `ui.py` owns terminal rendering: frames, menus, progress display, success
  screens, metadata prompts, and interruption/exit messages.
- `yt_downloader.py` owns download behavior: yt-dlp options, progress hooks,
  batch URL parsing, parallel downloads, MP3 conversion, metadata prompts,
  thumbnail embedding, and optional file renaming.
- `thumbnail_adder.py` is a standalone utility for copying APIC cover-art data
  from one MP3 file to another.
- `requirements.txt` contains pinned runtime dependencies.

Generated downloads go to `YTDownload/` by default. That directory is ignored by
git and should not be committed.

## Setup And Run

Use Python 3.10 or newer; the code uses modern type syntax such as
`bytes | None`.

Recommended local setup:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the app:

```powershell
python main.py
python main.py C:\path\to\existing\output
python main.py --help
```

Run the thumbnail utility:

```powershell
python thumbnail_adder.py -i input.mp3 -o output.mp3
```

The default output path `YTDownload` is created automatically. A custom output
directory must already exist.

## Current Behavior Notes

- Interactive menu choices in the current code are `V`/`v` for video,
  `A`/`a` for audio, `O`/`o` for both video and audio, and `U`/`u` to exit.
  The README still mentions `B`/`b` for both; treat the code as the current
  source of truth unless updating the README too.
- URL input accepts one URL per line. A blank line starts the download.
  Comma-separated URLs are also split by `_parse_batch_urls`.
- Duplicate URLs in one batch are skipped and counted.
- `MAX_PARALLEL_DOWNLOADS` is currently `2`.
- Audio metadata is edited after downloads complete. The app tries to infer
  artist/title from the YouTube title before asking the user.
- Cover art is downloaded from the thumbnail URL and embedded as JPEG APIC data
  when available.
- Custom file renames strip characters matching `REGEX_SPECIAL_CHARS`.

## Development Guidance

- Keep changes scoped to the existing small-module structure unless a refactor
  is explicitly requested.
- Prefer updating helpers such as `build_ydl_opts`, `_parse_batch_urls`, and
  `_detect_artist_title_from_video_title` instead of duplicating logic.
- Preserve the interactive CLI flow and the mostly Czech user-facing wording.
  Verify text encoding carefully before editing visible strings.
- Be careful with the current import coupling between `main.py`, `ui.py`, and
  `yt_downloader.py`. Avoid adding new import-time side effects.
- Do not edit or commit `venv/`, `__pycache__/`, `.idea/`, `.vscode/`, or
  generated media/download output unless the user asks for it.
- For automated tests, start with pure helpers and mock network/download/media
  operations. Avoid real YouTube downloads in routine tests.
- For download behavior changes, keep yt-dlp configuration centralized through
  `build_ydl_opts`.

## Validation

There is no dedicated test suite in the current project. Useful checks:

```powershell
python -m compileall main.py ui.py yt_downloader.py thumbnail_adder.py
python main.py --help
```

For changes that affect downloads or conversion, do a manual smoke test with a
small sample URL only when network access and media downloads are appropriate.
