import os
import re
import yt_dlp
import imageio_ffmpeg
import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from PIL import Image
from io import BytesIO
import ui

REGEX_SPECIAL_CHARS = r'[\/:*?"<>|\"\'\:\|\!\?\=\$\%\(\)\{\}\[\];,.]'
CHOICE_VO, CHOICE_AO, CHOICE_VA = 1, 2, 3
MB_IN_BYTES = 1048576
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()


def my_progress_hook(d: dict):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            progress = downloaded / total * 100
            ui.progress_bar(progress, downloaded / MB_IN_BYTES, 1)


def prompt_metadata(audio: EasyID3, title: str):
    if "-" in title:
        artist, track_title = title.split(" - ", 1)
        while True:
            ui.print_music_detected([artist, track_title])
            choice = input(ui.Fore.LIGHTCYAN_EX + "Výběr: " + ui.Fore.WHITE).lower()
            if choice == "a":
                break
            elif choice == "n":
                audio["artist"], audio["title"] = artist, track_title
                break
    if not audio.get("artist"):
        ui.print_music_not_detected(title)
        audio["artist"] = input(ui.Fore.LIGHTCYAN_EX + "Umělec: " + ui.Fore.WHITE)
        audio["title"] = input(ui.Fore.LIGHTCYAN_EX + "Název: " + ui.Fore.WHITE)


def download_thumbnail(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
        with Image.open(BytesIO(response.content)) as image:
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.getchannel('A'))
                image = background
            else:
                image = image.convert('RGB')
            buffer = BytesIO()
            image.save(buffer, format='JPEG')
            return buffer.getvalue()
    except (RequestException, HTTPError, ConnectionError):
        pass  # potlačíme chybový výpis
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
            audio_id3.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=jpeg_data
            ))
    audio_id3.save()


def build_ydl_opts(path: str, choice: int) -> dict:
    opts = {
        'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
        'progress_hooks': [my_progress_hook],
        'ffmpeg_location': ffmpeg_path
    }
    if choice == CHOICE_VO:
        opts['format'] = 'bestvideo+bestaudio/best'
    else:
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    return opts


def download_by_choice(download_path: str, download_choice: int):
    url_accepted, bad_url, e_msg = False, False, ""
    info = None

    while not url_accepted:
        ui.print_download_screen(download_type=download_choice, error=e_msg)
        prompt = "Zadejte URL: " if not bad_url else "Neplatná URL, zadejte znovu: "
        url = input(ui.Fore.LIGHTCYAN_EX + prompt + ui.Fore.WHITE)

        try:
            ydl_opts = build_ydl_opts(download_path, download_choice)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if download_choice in (CHOICE_AO, CHOICE_VA):
                    file_path = os.path.splitext(file_path)[0] + '.mp3'
            url_accepted = True
        except yt_dlp.utils.DownloadError as e:
            bad_url, e_msg = True, ui.Fore.RED + "Chyba: " + ui.Fore.WHITE + str(e)
        except Exception as e:
            bad_url, e_msg = True, ui.Fore.RED + "Chyba: " + ui.Fore.WHITE + "Neznámá chyba: " + str(e)

    title = info.get('title', 'Unknown Title')

    while True:
        ui.print_name(title)
        choice = input(ui.Fore.LIGHTCYAN_EX + "Výběr: " + ui.Fore.WHITE).lower()
        if choice == "a":
            new_title = input(ui.Fore.LIGHTCYAN_EX + "Nový název: " + ui.Fore.WHITE)
            clean_title = re.sub(REGEX_SPECIAL_CHARS, "", new_title) + os.path.splitext(file_path)[1]
            new_path = os.path.join(download_path, clean_title)
            os.rename(file_path, new_path)
            file_path = new_path
            break
        elif choice == "n":
            break

    ui.print_success_download(file_path)

    if download_choice in (CHOICE_AO, CHOICE_VA):
        mp3_metadata_change(file_path, title, info.get('thumbnail'))
