from codecs import utf_16_encode
from time import sleep
from colorama import Fore, Back, Style
import subprocess
import re
from pytube import YouTube
from mutagen.mp3 import EasyMP3
from mutagen.id3 import ID3, APIC
dl_pathway = "/mnt/d/Stažené soubory/DL/"
ffmpeg_pathway = "/mnt/d/Stažené\ soubory/DL/"

def on_complete(stream, filepath):
    print(filepath)
    print("COMPLETE!  --> " + filepath)

def on_progress(stream, chunk, bytes_remaining):
    str = f'{round(100 - (bytes_remaining / stream.filesize * 100), 2)}%'
    str2 = f'{round((stream.filesize - bytes_remaining) / 1048576, 2)} MB'
    print(Fore.YELLOW + "Progress      " + Fore.WHITE  + ": " + str2 + " - " + str)

#ffmpeg -i /mnt/d/Stažené\ soubory/DL/song_name.mp4 /mnt/d/Stažené\ soubory/DL/song_name.mp3     --> Convert to MP3
#rm -rf /mnt/d/Stažené soubory/DL/song_name.mp4                                                  --> Remove MP4 if needed
def dl_proc(choice):
    mp4_s = "'%s.mp4'" % name
    mp3_s = "'%s.mp3'" % name
    mp3_sa = dl_pathway + name + ".mp3"
    ffmpeg = ("ffmpeg -i %s%s %s%s" % (ffmpeg_pathway, mp4_s, ffmpeg_pathway, mp3_s))
    subprocess.call(ffmpeg, shell=True)

#If Audio only remove mp4 file
    if(choice == "A" or choice == "a"):
        rmf = ("rm -rf '%s'" % video)
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
    audio.tags["ARTIST"] = input("Artist : ")
    audio.tags["TITLE"] = input("Title   : ")
    audio.save()

#Logo always on top
def dl_logo():
    print(Fore.RED + "You" + Fore.WHITE + "Tube Downloader Script" + Back.RESET)

def dl_init():
    print(Back.RESET)
    subprocess.call("clear", shell=True)

dl_init()
dl_logo()

name = None
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
    conv_n = re.sub("[\/:*?\"<>|]", "", conv_n).replace(".", "").replace("\'", "")
#Switching between pre download info and post
    dl_info(0)

#/home/codex/Stažené/DL                                                                        --> Path to download folder
#Video only download
    if(choice == "V" or choice == "v"):
        video = myvideo.streams.get_highest_resolution().download(output_path = dl_pathway)
        name = re.sub(dl_pathway, "", video)
        name = re.sub(".mp4", "", name)
        dl_info(1)
#Audio only download
    if(choice == "A" or choice == "a"):
        video = myvideo.streams.get_audio_only().download(output_path = dl_pathway)
        print(video)
        name = re.sub(dl_pathway, "", video)
        name = re.sub(".mp4", "", name)
        dl_proc(choice)
        dl_info(1)
#Video and audio download
    if(choice == "B" or choice == "b"):
        video = myvideo.streams.get_highest_resolution().download(output_path = dl_pathway)
        name = re.sub(dl_pathway, "", video)
        name = re.sub(".mp4", "", name)
        dl_proc(choice)
        dl_info(1)