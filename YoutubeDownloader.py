from asyncore import write
from codecs import utf_16_encode
from time import sleep
from webbrowser import get
from colorama import init, Fore, Back, Style
import os
import subprocess
import re
from pytube import YouTube
import mutagen
from mutagen.mp3 import EasyMP3
#import requests
#from mutagen.id3 import ID3, APIC
dl_pathway = '/mnt/d/Stažené soubory/DL/'

def on_complete(stream, filepath):
    print("COMPLETE!  --> " + filepath)

def on_progress(stream, chunk, bytes_remaining):
    str = f'{round(100 - (bytes_remaining / stream.filesize * 100), 2)}%'
    str2 = f'{round((stream.filesize - bytes_remaining) / 1048576, 2)} MB'
    print(Fore.YELLOW + "Progress      " + Fore.WHITE  + ": " + str2 + " - " + str)

#ffmpeg -i /mnt/d/Stažené\ soubory/DL/song_name.mp4 /mnt/d/Stažené\ soubory/DL/song_name.mp3     --> Convert to MP3
#rm -rf /mnt/d/Stažené\ soubory/DL/song_name.mp4                                                 --> Remove MP4 if needed
def dl_proc(choice):
    mp4_s = "'%s.mp4'" % conv_n
    mp3_s = "'%s.mp3'" % conv_n
    mp3_sa = dl_pathway + conv_n + ".mp3"

    ffmpeg = ('ffmpeg -i %s%s %s%s' % (dl_pathway, mp4_s, dl_pathway, mp3_s))
    subprocess.call(ffmpeg, shell=True)

#If Audio only remove mp4 file
    if(choice == "A" or choice == "a"):
        rmf = ('rm -rf %s%s' % (dl_pathway, mp4_s))
        subprocess.call(rmf, shell=True)

    change_meta(mp3_sa)

#Download info for pre and post download
def dl_info(inf_c):
    if(inf_c == 1):
        subprocess.call("clear", shell=True)
        dl_logo()
        print(Fore.GREEN + "Download complete!")

    print(Fore.BLUE + "YT Name       " + Fore.WHITE + ": " + myvideo.title)
    print(Fore.BLUE + "Thumbnail URL " + Fore.WHITE + ": " + myvideo.thumbnail_url)
    
    if(inf_c == 1):
        print(Fore.BLUE + "Pathfile      " + Fore.WHITE + ": " + dl_pathway)

#For mp3 Changing metadata for artist and title so it can be sorted in mobile etc.
def change_meta(mp3_sample):
    subprocess.call("clear", shell=True)
    dl_logo()
    dl_info(0)
    audio = EasyMP3(mp3_sample)
    print("Metadata change")
    audio.tags['ARTIST'] = input("Artist: ")
    audio.tags['TITLE'] = input("Title: ")
    """
    #Downloading thumbnail
    thumb = requests.get(myvideo.thumbnail_url)
    print(thumb.status_code)
    with open ("/mnt/d/Stažené soubory/DL/thumbnail.jpg", "wb") as imgs:
        imgs.write(thumb.content)
    with open ("/mnt/d/Stažené soubory/DL/thumbnail.jpg", "rb") as thmb:
        audio.tags(
            APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',
                type=3,  # 3 is for album art
                desc='Cover',
                data=thmb.read()  # Reads and adds album art
            )
        )
    #Deleting thumbnail
    rmf = ('rm -rf /mnt/d/Stažené\ soubory/DL/thumbnail.jpg')
    subprocess.call(rmf, shell=True)
    """
    audio.save()

#Logo always on top
def dl_logo():
    print(Fore.RED + "You" + Fore.WHITE + "Tube Downloader Script" + Back.RESET)

def dl_init():
    print(Back.RESET)
    subprocess.call("clear", shell=True)

dl_init()
dl_logo()
while True:
    print(Style.BRIGHT + Fore.CYAN + "What content would you like to download?" + Style.NORMAL)
    print(Fore.RED + "(V)" + Fore.WHITE + "ideo only | " + Fore.RED +  "(A)" + Fore.WHITE + "udio only | " + Fore.RED +  "(B)" + Fore.WHITE + "oth | " + Fore.RED +  "(E)" + Fore.WHITE + "xit")
    choice = input("Choice: ")

#Exiting script 
    if(choice == "E" or choice == "e"):
        print(Fore.RED + "Exiting download script")
        sleep(1)
        print(Style.RESET_ALL)
        subprocess.call("clear", shell=True)
        exit(0)

    url = input(Fore.RED + "URL: " + Fore.WHITE)
    myvideo = YouTube(url, on_complete_callback = on_complete, on_progress_callback = on_progress)
    
    conv_n = myvideo.title
#Removing forbidden symbols in name \/:*?"<>|()
    conv_n = re.sub("[\/:*?\"<>|]", "", conv_n).replace(".", "")

#Switching between pre download info and post
    dl_info(0)

#/home/codex/Stažené/DL                                                                        --> Path to download folder
#Video only download
    if(choice == "V" or choice == "v"):
        video = myvideo.streams.get_highest_resolution().download(output_path = dl_pathway)
        dl_info(1)
#Audio only download
    if(choice == "A" or choice == "a"):
        video = myvideo.streams.get_audio_only().download(output_path = dl_pathway)
        dl_proc(choice)
        dl_info(1)
#Video and audio download
    if(choice == "B" or choice == "b"):
        video = myvideo.streams.get_highest_resolution().download(output_path = dl_pathway)
        dl_proc(choice)
        dl_info(1)