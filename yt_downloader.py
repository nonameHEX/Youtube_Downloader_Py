import os
from time import sleep
import re
import logging
import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError
import threading

from pytube import YouTube, exceptions
from moviepy.editor import *
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

import ui

REGEX_SPECIAL_CHARS = '[\/:*?"<>|\"\'\:\|\!\?\=\$\%\(\)\{\}\[\];,.]'
CHOICE_VO = 1   # Video Only
CHOICE_AO = 2   # Audio Only
CHOICE_VA = 3   # Video and Audio
MB_IN_BYTES = 1048576 # MB value in bytes
logging.basicConfig(level=logging.CRITICAL)

def on_progress(video_object, chunk, bytes_remaining):
    # video_object by měl být stream obsažen v my_video_object, obsahuje informace o velikosti souboru
    # chunk obsahuje data v bytech, která ještě nejsou uložená na disk - zbytečný, ale musí být ve funkci
    # bytes_remaining je int hodnota zbylých bytů co se musí ještě stáhnout

    # Výpočet pro už stažený data v %
    progress_in_percentage = round(100 - (bytes_remaining / video_object.filesize * 100), 1)
    # Výpočet už stažených dat v MB
    progress_in_mb = round((video_object.filesize - bytes_remaining) / MB_IN_BYTES, 2)
    
    #logging.info(progress_in_mb + " - " + progress_in_percentage + " %") # Vypisuje progress -> poté předělat na nějaký progressbar v ui
    ui.progress_bar(progress_in_percentage, progress_in_mb, 1) # Výpis progressu stahování, 1 znamená download

def hide_moviepy_output_thread(video_clip: AudioFileClip, converted_video_pathway):
    # Proměnná video_clip se konvertuje na .mp3 soubor (celá cesta, kde se vytvoří i s názvem), logger schová veškery moviepy output když je None
    video_clip.write_audiofile(filename = converted_video_pathway, logger = None)

def is_possible_music(yt_title):
    # Nejzákladnější pokus o rozeznání hudbního klipu, většinou bývá název videa "umělec - název skladby"
    if "-" in yt_title:
        return True
    else:
        return False

def mp3_metadata_change(audio_pathway, yt_title, yt_thumbnail_url):
    # Změna metadat názvu a umělce v souboru, použito EasyID3 pro jednoduchou práci s tagy
    audio = EasyID3(audio_pathway)
    if is_possible_music(yt_title):
        audio_tags = yt_title.split(" - ")
        # Možná zavádějící název proměnné, ale hlídá pouze zda je na vstupu A/a N/n
        choice_default_metadata = False
        while not choice_default_metadata:
            ui.print_music_detected(audio_tags)
            choice = input(ui.Fore.LIGHTCYAN_EX + "Výběr: " + ui.Fore.WHITE)
            if choice.lower() == "a":
                choice_default_metadata = True
            if choice.lower() == "n":
                audio["artist"] = audio_tags[0]
                audio["title"] = audio_tags[1]
                choice_default_metadata = True

    # Pokud se nenajdou tagy (stačí umělec, protože buď budou oba nebo žádný), tak se vloží detekovaná metadata
    if not audio.get("artist"):
        ui.print_music_not_detected(yt_title)
        artist = input(ui.Fore.LIGHTCYAN_EX + "Umělec: " + ui.Fore.WHITE)
        audio["artist"] = artist
        title = input(ui.Fore.LIGHTCYAN_EX + "Název: " + ui.Fore.WHITE)
        audio["title"] = title

    audio.save()

    # Třída ID3 je vylepšená pro práci s audio tagy (EasyID3 nelze použít na přidání obrázku do metadat),
    # ale zbytečně složitá na jednoduché věci jako změna názvu autora
    audio = ID3(audio_pathway)
    try:
        thumb_data = requests.get(yt_thumbnail_url).content
        # Vytvoření instance třídy APIC pro nastavení thumbnailu
        thumbnail = APIC(
            data=thumb_data,
            mime='image/jpeg',
            desc='thumbnail'
        )
        audio.add(thumbnail) # Přidání APIC tagu do audia
    except RequestException:
        print("Thumbnail Error - Chyba při požadavku")
    except HTTPError:
        print("Thumbnail Error - HTTP chyba")
    except ConnectionError:
        print("Thumbnail Error - Chyba připojení")

    audio.save()

def download_by_choice(download_pathway, download_choice):
    url_accepted = False
    bad_url = False
    e_msg = ""
    while not url_accepted:
        ui.print_download_screen(download_type=download_choice, error=e_msg)
        try:
            if not bad_url:
                my_url = input(ui.Fore.LIGHTCYAN_EX + "Zadejte URL: " + ui.Fore.WHITE)
            else:
                my_url = input(ui.Fore.LIGHTCYAN_EX + "Neplatná URL, zadejte znovu: " + ui.Fore.WHITE)
            my_video_object = YouTube(url = my_url, on_progress_callback = on_progress)
            # Video bude obsahovat celou cestu s názvem k souboru jako string -> download_pathway\nazev.mp4
            if download_choice == CHOICE_VO or download_choice == CHOICE_VA:
                video = my_video_object.streams.get_highest_resolution().download(output_path = download_pathway)
            elif download_choice == CHOICE_AO:
                video = my_video_object.streams.get_audio_only().download(output_path = download_pathway)
            url_accepted = True
        except exceptions.RegexMatchError:
            bad_url = True
            e_msg = ui.Fore.RED + "Chyba: " + ui.Fore.WHITE + "Neplatná URL adresa"
        except exceptions.AgeRestrictedError as e:
            bad_url = True
            e_msg = ui.Fore.RED + "Chyba: " + ui.Fore.WHITE + "Video s adresou " + e.video_id + " je věkově omezené"
        except exceptions.VideoUnavailable as e:
            bad_url = True
            e_msg = ui.Fore.RED + "Chyba: " + ui.Fore.WHITE + "Video s adresou " + e.video_id + " neexistuje"
        except Exception:
            bad_url = True
            e_msg = ui.Fore.RED + "Chyba: " + ui.Fore.WHITE + "Vyskytla se neznámá chyba"

    logging.debug(my_video_object)

    # Možná zavádějící název proměnné, ale hlídá pouze zda je na vstupu A/a N/n
    choice_rename_accepted = False
    while not choice_rename_accepted:
        ui.print_name(my_video_object.title)
        choice = input(ui.Fore.LIGHTCYAN_EX + "Výběr: " + ui.Fore.WHITE)
        if choice.lower() == "a":
            new_title = input(ui.Fore.LIGHTCYAN_EX + "Nový název: " + ui.Fore.WHITE)
            logging.debug(new_title)
            # Odstranění speciálních znaků z názvu (OS by mohl mít problém, kdyby tam zůstaly)
            clean_title = re.sub(REGEX_SPECIAL_CHARS, "", new_title) + ".mp4"
            logging.debug(clean_title)
            new_video = os.path.join(download_pathway, clean_title)
            logging.debug(new_video)
            # Přejmenování souboru na nový název a uložení cesty do proměnné video
            os.rename(video, new_video)
            video = new_video
            choice_rename_accepted = True
        elif choice.lower() == "n":
            choice_rename_accepted = True

    if download_choice == CHOICE_VO:
        ui.print_success_download(video)
    elif download_choice == CHOICE_AO or download_choice == CHOICE_VA:
        converted_video_pathway = re.sub(".mp4", ".mp3", video)
        # Vytvoření objektu AudioClip do proměnné video_clip, proměnná má název video_clip, protože to stále je .mp4 soubor
        video_clip = AudioFileClip(video)

        # Potřebujeme zjistit celkový počet chunků, které se budou během iterací/s konvertovat
        # chunksize=2000 je dáno proto, protože write_audiofile funkce moviepy má jako základní hodnotu biffersize=2000 
        # (u některých videí to hodilo IndexError, při větším chunksize)
        chunks = len(list(video_clip.iter_chunks(chunksize=2000)))
        logging.debug("Chunks: " + str(chunks))

        # Potřebujeme velikost videa a převedeme na MB pro výpis
        if download_choice == CHOICE_AO:
            itag = my_video_object.streams.get_audio_only().itag
        else:
            itag = my_video_object.streams.get_highest_resolution().itag
        total_size = my_video_object.streams.get_by_itag(itag).filesize / MB_IN_BYTES

        # Přesměrování moviepy na jiný thread aby se mohl udělat custom loading bar zároveň s konverzí
        moviepy_thread = threading.Thread(target=hide_moviepy_output_thread, args=(video_clip, converted_video_pathway))
        moviepy_thread.start()

        # Fake konverze pro výpis custom loading baru +/- odpovídá realitě od 1 do 100 %
        for i in range(100+1):
            progress_mb = (total_size / 100) * (i)
            ui.progress_bar(float(i), round(progress_mb, 2), 2) # Výpis progressu stahování, 2 znamená fake konvert
            # Aby 1% odpovídalo reálné konverzi chunků, doba je nastavena lehce pod průměr konverze moviepy za normálního stavu
            sleep((chunks / 1300) / 100)

        moviepy_thread.join()

        if download_choice == CHOICE_AO:
            # Odstranění .mp4 souboru, pokud chceme pouze audio
            os.remove(video)
            ui.print_success_download(converted_video_pathway)
        if download_choice == CHOICE_VA:
            ui.print_success_download(path1=video, path2=converted_video_pathway)

        # Změna metadat u MP3 souboru
        mp3_metadata_change(converted_video_pathway, my_video_object.title, my_video_object.thumbnail_url)