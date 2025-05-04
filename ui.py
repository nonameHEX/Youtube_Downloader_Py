import os
import re
from time import sleep
from colorama import Fore, Back, Style, init
from yt_downloader import CHOICE_VO, CHOICE_AO, CHOICE_VA
from main import COLS

ESCAPE_REGEX = r'\x1b\[.*?m'
init(autoreset=True)


def _clear_console():
    os.system("cls" if os.name == 'nt' else "clear")


def set_console_size(rows: int, columns: int):
    command = f"mode con: cols={columns} lines={rows} && cls" if os.name == 'nt' else f'printf "\033[8;{rows};{columns}t" && clear'
    os.system(command)


def _get_visible_length(text: str) -> int:
    return len(re.sub(ESCAPE_REGEX, '', text))


def _downloader_logo():
    print_centered("█" * 34)
    print_centered(
        f"█{Back.WHITE}{Fore.BLACK}You{Fore.RED}Tube {Fore.BLUE}V{Fore.BLACK}ideo "
        f"& {Fore.GREEN}A{Fore.BLACK}udio {Fore.YELLOW}D{Fore.BLACK}ownloader{Style.RESET_ALL}█"
    )
    print_centered("█" * 34)


def print_basic_menu():
    _clear_console()
    _up_frame()
    print_centered("Jaký obsah chcete stáhnout?")
    print_centered(
        f"({Fore.BLUE}V{Fore.WHITE})ideo | "
        f"({Fore.GREEN}A{Fore.WHITE})udio | "
        f"({Fore.YELLOW}O{Fore.WHITE})bojí | "
        f"({Fore.RED}U{Fore.WHITE})končit"
    )
    _down_frame(7)


def print_download_screen(download_type: int, error: str):
    _clear_console()
    _up_frame()
    messages = {
        CHOICE_VO: f"Stahujete pouze {Fore.BLUE}VIDEO{Fore.WHITE}",
        CHOICE_AO: f"Stahujete pouze {Fore.GREEN}AUDIO{Fore.WHITE}",
        CHOICE_VA: f"Stahujete {Fore.YELLOW}VIDEO {Fore.WHITE}i {Fore.YELLOW}AUDIO{Fore.WHITE}"
    }
    print_centered(messages.get(download_type, "Neznámý typ stahování"))
    if error:
        print_centered("")
        print_centered(error)
        _down_frame(6)
    else:
        _down_frame(8)


def _print_metadata_screen(title: str, is_detected: bool):
    _clear_console()
    _up_frame()
    if is_detected:
        print_centered("! Název YouTube videa detekován jako skladba !")
        print_centered(f"{Fore.YELLOW}Umělec: {Fore.WHITE}")
        print_centered(f"{Fore.YELLOW}Název: {Fore.WHITE}")
        print_centered("")
        print_centered("Chcete nastavit metadata podle sebe?")
        print_centered(f"({Fore.GREEN}A{Fore.WHITE})no | ({Fore.RED}N{Fore.WHITE})e")
        _down_frame(3)
    else:
        print_centered(f"{Fore.YELLOW}Název videa: {Fore.WHITE}{title}")
        print_centered("")
        print_centered("Nastavujete metadata")
        _down_frame(6)


def print_music_detected(audio_tags: list):
    _print_metadata_screen("", is_detected=True)


def print_music_not_detected(name: str):
    _print_metadata_screen(name, is_detected=False)


def print_closing_screen():
    _clear_console()
    _up_frame()
    print_centered(f"{Fore.RED}Exiting download script{Fore.WHITE}")
    _down_frame(8)
    print(Style.RESET_ALL)
    _clear_console()


def print_name(name: str):
    _clear_console()
    _up_frame()
    print_centered(f"{Fore.YELLOW}Název videa: {Fore.WHITE}{name}")
    print_centered("")
    print_centered("Chcete soubor přejmenovat podle sebe? Všechny nepovolené znaky budou nahrazeny.")
    print_centered(f"({Fore.GREEN}A{Fore.WHITE})no | ({Fore.RED}N{Fore.WHITE})e")
    _down_frame(5)


def print_success_download(path1: str, path2: str = ""):
    _clear_console()
    _up_frame()
    print_centered(f"{Fore.GREEN}Soubor uložen: {Fore.WHITE}")
    print_centered(path1)
    if path2:
        print_centered(f"{Fore.GREEN}Soubor uložen: {Fore.WHITE}")
        print_centered(path2)
        _down_frame(5)
    else:
        _down_frame(7)


def print_interupt():
    _clear_console()
    print(Style.RESET_ALL + "Přerušení z klávesnice - program se ukončil")


# progress bar - porovnává hodnoty progress a aktualizuje loading bar na konzoli
def progress_bar(progress: float, progress_mb: float, t_type: int):
    color = Fore.RED if progress < 33 else Fore.YELLOW if progress < 67 else Fore.GREEN
    bar_length = progress_int = int(progress)
    bar = "█" * (bar_length // 2) + " " * (50 - bar_length // 2)
    text = "Stahuji soubor z YouTube" if t_type == 1 else "Konvertuji soubor do MP3"
    print_centered(
        f"{text} - {Fore.YELLOW}Progress{Fore.WHITE}: {progress_mb:.2f} MB [{color}{bar}{Fore.WHITE}] {progress:.1f}%",
        no_frame=True
    )


def print_centered(text: str, no_frame: bool = False):
    width = COLS
    padding = width - _get_visible_length(text) - 2
    left = padding // 2
    right = padding - left
    line = f"{' ' * left}{text}{' ' * right}" if no_frame else f"█{' ' * left}{text}{' ' * right}█"
    print(line, end="\r" if no_frame else "\n")


def print_frame():
    print(f"{Back.BLACK}{Fore.WHITE}█" * COLS)


def _up_frame():
    print_frame()
    for _ in range(3):
        print_centered("")
    _downloader_logo()
    print_centered("")


def _down_frame(space: int):
    for _ in range(space):
        print_centered("")
    print_frame()
