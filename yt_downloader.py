import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

import imageio_ffmpeg
import requests
import yt_dlp
from requests.exceptions import RequestException, HTTPError, ConnectionError
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from PIL import Image

import ui

REGEX_SPECIAL_CHARS = r'[\/:*?"<>|\"\'\:\|\!\?\=\$\%\(\)\{\}\[\];,.]'
CHOICE_VO, CHOICE_AO, CHOICE_VA = 1, 2, 3
MB_IN_BYTES = 1048576
MAX_PARALLEL_DOWNLOADS = 2

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

TITLE_NOISE_REGEX = r'\s*(\[(official|lyrics?|audio|video)[^\]]*\]|\((official|lyrics?|audio|video)[^)]*\))\s*$'
TITLE_SEPARATORS = [" - ", " – ", " — ", " | ", " : "]


def my_progress_hook(d: dict):
    if d.get("status") == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
        downloaded = d.get("downloaded_bytes", 0)
        if total:
            progress = downloaded / total * 100
            ui.progress_bar(progress, downloaded / MB_IN_BYTES, 1)


def _clean_title_for_metadata(title: str) -> str:
    cleaned = re.sub(TITLE_NOISE_REGEX, "", title, flags=re.IGNORECASE).strip()
    return cleaned or title


def _looks_like_artist(part: str) -> bool:
    p = part.strip().lower()
    if not p:
        return False
    if any(x in p for x in ["official", "lyrics", "video", "audio"]):
        return False
    # jednoduchá heuristika: autor bývá kratší část
    return len(p.split()) <= 5


def _detect_artist_title_from_video_title(title: str):
    cleaned = _clean_title_for_metadata(title)

    for sep in TITLE_SEPARATORS:
        if sep not in cleaned:
            continue

        left, right = [x.strip() for x in cleaned.split(sep, 1)]
        if not left or not right:
            continue

        left_artist = _looks_like_artist(left)
        right_artist = _looks_like_artist(right)

        # author - title
        if left_artist and not right_artist:
            return left, right

        # title - author
        if right_artist and not left_artist:
            return right, left

        # fallback
        return left, right

    return None, None


def prompt_metadata(audio: EasyID3, title: str):
    auto_artist, auto_title = _detect_artist_title_from_video_title(title)

    if auto_artist and auto_title:
        ui.print_music_detected([auto_artist, auto_title])
        choice = input(ui.Fore.LIGHTCYAN_EX + "Výběr: " + ui.Fore.WHITE).lower().strip()

        # A = použít auto, N = upravit ručně
        if choice in ("a", ""):
            audio["artist"] = auto_artist
            audio["title"] = auto_title
            return

        artist_input = input(ui.Fore.LIGHTCYAN_EX + f"Umělec [{auto_artist}]: " + ui.Fore.WHITE).strip()
        title_input = input(ui.Fore.LIGHTCYAN_EX + f"Název [{auto_title}]: " + ui.Fore.WHITE).strip()
        audio["artist"] = artist_input or auto_artist
        audio["title"] = title_input or auto_title
        return

    ui.print_music_not_detected(title)
    audio["artist"] = input(ui.Fore.LIGHTCYAN_EX + "Umělec: " + ui.Fore.WHITE)
    audio["title"] = input(ui.Fore.LIGHTCYAN_EX + "Název: " + ui.Fore.WHITE)


def download_thumbnail(url: str) -> bytes | None:
    try:
        response = requests.get(url, timeout=12)
        response.raise_for_status()
        with Image.open(BytesIO(response.content)) as image:
            if image.mode in ("RGBA", "LA"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.getchannel("A"))
                image = background
            else:
                image = image.convert("RGB")
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            return buffer.getvalue()
    except (RequestException, HTTPError, ConnectionError):
        pass
    except Exception:
        pass
    return None


def mp3_metadata_change(audio_path: str, title: str, thumbnail_url: str | None):
    audio = EasyID3(audio_path)
    prompt_metadata(audio, title)
    audio.save()

    audio_id3 = ID3(audio_path)
    if thumbnail_url:
        jpeg_data = download_thumbnail(thumbnail_url)
        if jpeg_data:
            audio_id3.delall("APIC")
            audio_id3.add(APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=jpeg_data
            ))
    audio_id3.save()


def build_ydl_opts(path: str, choice: int, allow_playlist: bool = True) -> dict:
    opts = {
        "outtmpl": os.path.join(path, "%(title)s [%(id)s].%(ext)s"),
        "progress_hooks": [my_progress_hook],
        "ffmpeg_location": ffmpeg_path,
        "noplaylist": not allow_playlist
    }

    if choice == CHOICE_VO:
        opts["format"] = "bestvideo+bestaudio/best"
    elif choice == CHOICE_AO:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    else:  # CHOICE_VA
        opts["format"] = "bestvideo+bestaudio/best"
        opts["keepvideo"] = True
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]

    return opts


def _parse_batch_urls(raw_lines: list[str]):
    cleaned = []
    seen = set()
    skipped = 0

    for line in raw_lines:
        for part in line.replace(",", "\n").splitlines():
            url = part.strip()
            if not url:
                continue
            if url in seen:
                skipped += 1
                continue
            seen.add(url)
            cleaned.append(url)

    return cleaned, skipped


def _download_url_items(url: str, download_path: str, download_choice: int):
    ydl_opts = build_ydl_opts(download_path, download_choice, allow_playlist=True)

    downloaded = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        entries = info.get("entries") if isinstance(info, dict) else None
        entries = [e for e in entries if e] if entries else [info]

        for entry in entries:
            file_path = ydl.prepare_filename(entry)
            if download_choice in (CHOICE_AO, CHOICE_VA):
                file_path = os.path.splitext(file_path)[0] + ".mp3"

            downloaded.append({
                "file_path": file_path,
                "title": entry.get("title", "Unknown Title"),
                "thumbnail": entry.get("thumbnail"),
                "is_audio": download_choice in (CHOICE_AO, CHOICE_VA)
            })

    return downloaded


def download_by_choice(download_path: str, download_choice: int):
    ui.print_download_screen(download_type=download_choice, error="")
    print(ui.Fore.LIGHTCYAN_EX + "Zadejte URL (1 URL na řádek, prázdný řádek = start):" + ui.Fore.WHITE)

    raw_lines = []
    while True:
        line = input().strip()
        if not line:
            break
        raw_lines.append(line)

    urls, skipped_dupes = _parse_batch_urls(raw_lines)
    if not urls:
        print(ui.Fore.RED + "Nebyla zadána žádná URL." + ui.Fore.WHITE)
        return

    if skipped_dupes:
        print(ui.Fore.YELLOW + f"Přeskočeno duplicitních URL: {skipped_dupes}" + ui.Fore.WHITE)

    all_items = []
    errors = []

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_DOWNLOADS) as executor:
        futures = {executor.submit(_download_url_items, url, download_path, download_choice): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                items = future.result()
                all_items.extend(items)
                print(ui.Fore.GREEN + f"Staženo: {url}" + ui.Fore.WHITE)
            except yt_dlp.utils.DownloadError as e:
                errors.append((url, str(e)))
                print(ui.Fore.RED + f"Chyba URL: {url}\n{e}" + ui.Fore.WHITE)
            except Exception as e:
                errors.append((url, "Neznámá chyba: " + str(e)))
                print(ui.Fore.RED + f"Chyba URL: {url}\nNeznámá chyba: {e}" + ui.Fore.WHITE)

    # Metadata fáze až po dokončení všech downloadů
    if download_choice in (CHOICE_AO, CHOICE_VA):
        for item in all_items:
            if item["is_audio"] and os.path.exists(item["file_path"]):
                mp3_metadata_change(item["file_path"], item["title"], item["thumbnail"])

    # Volitelné přejmenování každého souboru
    for item in all_items:
        file_path = item["file_path"]
        if not os.path.exists(file_path):
            continue

        title = item["title"]
        while True:
            ui.print_name(title)
            choice = input(ui.Fore.LIGHTCYAN_EX + "Výběr: " + ui.Fore.WHITE).lower().strip()
            if choice == "a":
                new_title = input(ui.Fore.LIGHTCYAN_EX + "Nový název: " + ui.Fore.WHITE).strip()
                if not new_title:
                    break
                ext = os.path.splitext(file_path)[1]
                clean_title = re.sub(REGEX_SPECIAL_CHARS, "", new_title)
                new_path = os.path.join(download_path, clean_title + ext)
                if not os.path.exists(new_path):
                    os.rename(file_path, new_path)
                    item["file_path"] = new_path
                break
            elif choice == "n":
                break

        ui.print_success_download(item["file_path"])

    print(ui.Fore.GREEN + f"Hotovo. Staženo položek: {len(all_items)} | Chyb URL: {len(errors)}" + ui.Fore.WHITE)
