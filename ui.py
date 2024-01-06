import re
import os

from colorama import Fore, Back, Style, init
from time import sleep

from yt_downloader import CHOICE_VO, CHOICE_AO, CHOICE_VA
from main import COLS

ESCAPE_REGEX = '\x1b\[.*?m'
init(autoreset=True) # inicializace knihovny colorama, aby se vynulovala předchozí nastavení barev

def _clear_console():
    if os.name == 'nt':  # Windows
        os.system("cls")
    else:  # Linux or macOS
        os.system("clear")

def set_console_size(rows, columns):
    # kontrola platformy
    if os.name == 'nt':  # Windows
        os.system(f'mode con: cols={columns} lines={rows} && cls')
    else:  # Linux or macOS
        os.system(f'printf "\033[8;{rows};{columns}t" && clear')

def _get_visible_length(text: str):
    escape_pattern = re.compile(ESCAPE_REGEX)
    visible_text = escape_pattern.sub('', text)
    return len(visible_text)

def _downloader_logo():
    print_centered(f"█"*34)
    print_centered( f"█{Back.WHITE}{Fore.BLACK}You{Fore.RED}Tube {Fore.BLUE}V{Fore.BLACK}ideo " +
                    f"& {Fore.GREEN}A{Fore.BLACK}udio {Fore.YELLOW}D{Fore.BLACK}ownloader{Style.RESET_ALL}█")
    print_centered(f"█"*34)

def print_basic_menu():
    _clear_console()
    up_frame()

    print_centered("Jaký obsah chcete stáhnout?")
    print_centered( f"({Fore.BLUE}V{Fore.WHITE})ideo | " +
                    f"({Fore.GREEN}A{Fore.WHITE})udio | " +
                    f"({Fore.YELLOW}O{Fore.WHITE})bojí | " +
                    f"({Fore.RED}U{Fore.WHITE})končit")
    
    down_frame(7)

def print_download_screen(download_type, error: str):
    _clear_console()
    up_frame()

    if download_type == CHOICE_VO:
        print_centered(f"Stahujete pouze {Fore.BLUE}VIDEO{Fore.WHITE}")
    elif download_type == CHOICE_AO:
        print_centered(f"Stahujete pouze {Fore.GREEN}AUDIO{Fore.WHITE}")
    elif download_type == CHOICE_VA:
        print_centered(f"Stahujete {Fore.YELLOW}VIDEO {Fore.WHITE}i {Fore.YELLOW}AUDIO{Fore.WHITE}")

    if error != "":
        print_centered("")
        print_centered(error)
        down_frame(6)
    else:
        down_frame(8)

def print_music_detected(audio_tags: list):
    _clear_console()
    up_frame()

    print_centered("! Název YouTube videa detekován jako skladba !")
    print_centered(f"{Fore.YELLOW}Umělec: {Fore.WHITE}{audio_tags[0]}")
    print_centered(f"{Fore.YELLOW}Název: {Fore.WHITE}{audio_tags[1]}")
    print_centered("")
    print_centered("Chcete nastavit metadata podle sebe?")
    print_centered(f"({Fore.GREEN}A{Fore.WHITE})no | ({Fore.RED}N{Fore.WHITE})e")

    down_frame(3)

def print_music_not_detected(name: str):
    _clear_console()
    up_frame()

    print_centered(f"{Fore.YELLOW}Název videa: {Fore.WHITE}{name}")
    print_centered("")
    print_centered("Nastavujete metadata")

    down_frame(6)

def print_closing_screen():
    _clear_console()
    up_frame()

    print_centered(f"{Fore.RED}Exiting download script{Fore.WHITE}")

    down_frame(8)

    print(Style.RESET_ALL)
    sleep(1)
    _clear_console()

def print_name(name: str):
    _clear_console()
    up_frame()

    print_centered(f"{Fore.YELLOW}Název videa: {Fore.WHITE}{name}")
    print_centered("")
    print_centered("Chcete soubor přejmenovat podle sebe? Všechny nepovolené znaky budou nahrazeny.")
    print_centered(f"({Fore.GREEN}A{Fore.WHITE})no | ({Fore.RED}N{Fore.WHITE})e")

    down_frame(5)

def print_success_download(path1: str, path2=""):
    _clear_console()
    up_frame()

    print_centered(f"{Fore.GREEN}Soubor uložen: {Fore.WHITE}")
    print_centered(path1)
    if path2 != "":
        print_centered(f"{Fore.GREEN}Soubor uložen: {Fore.WHITE}")
        print_centered(path2)
        down_frame(5)
    else:
        down_frame(7)

    sleep(3)

def print_interupt():
    _clear_console()
    print(Style.RESET_ALL + "Přerušení z klávesnice - program se ukončil")

#progress bar - porovnává hodnoty progress a aktualizuje loading bar na konzoli
def progress_bar(progress, progress_mb, t_type):
    progress_int = int(progress)  # Převedení hodnoty progress na celočíselnou hodnotu
    if progress_int < 33:
        color = Fore.RED  # Červená barva
    elif progress_int < 67:
        color = Fore.YELLOW  # Oranžová barva
    else:
        color = Fore.GREEN  # Zelená barva

    bar = "█" * (progress_int // 2)  # Vytvoření loading baru s použitím znaku "█"
    bar += " " * (50 - progress_int // 2)  # Doplnění zbylého místa mezerami

    if t_type == 1:
        text = "Stahuji soubor z YouTube"
    if t_type == 2:
        text = "Konvertuji soubor do MP3"
    # Výpis na konzoli s použitím barev a escape sekvence \r pro návrat na začátek řádku
    print_centered(f"{text} - {Fore.YELLOW}Progress{Fore.WHITE}: {progress_mb:.2f} MB [{color}{bar}{Fore.WHITE}] {progress:.1f}%", no_frame=True)

def print_centered(text: str, no_frame = False):
    width = COLS
    padding = width - _get_visible_length(text) - 2
    left_padding = padding // 2
    right_padding = padding - left_padding
    if no_frame:
        centered_text = " " * left_padding + text
        print(centered_text, end="\r")
    else:
        centered_text = "█" + " " * left_padding + text + " " * right_padding + "█"
        print(centered_text)

def print_frame():
    frame = f"{Back.BLACK}{Fore.WHITE}█" * COLS
    print(frame)

def up_frame():
    print_frame()
    for i in range(3):
        print_centered("")
    _downloader_logo()
    print_centered("")

def down_frame(space: int):
    for i in range(space):
        print_centered("")
    print_frame()