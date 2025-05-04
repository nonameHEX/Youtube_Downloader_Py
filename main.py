import os
import sys
import logging

import ui
from yt_downloader import download_by_choice, CHOICE_VO, CHOICE_AO, CHOICE_VA

DEFAULT_DOWNLOAD_PATH = "YTDownload"
ROWS, COLS = 24, 120

logging.basicConfig(level=logging.CRITICAL)


def parse_arguments() -> str:
    if "-h" in sys.argv or "--help" in sys.argv:
        print("Program pro stahování videí/hudby z YouTube.")
        print("Použití: main.py [výstupní_adresář]")
        print("Pokud nezadáte adresář, použije se výchozí složka YTDownload.")
        sys.exit(0)

    if len(sys.argv) > 2:
        print("Chyba: Příliš mnoho argumentů.")
        sys.exit(1)

    return sys.argv[1] if len(sys.argv) == 2 else DEFAULT_DOWNLOAD_PATH


def resolve_output_dir(directory: str) -> str:
    abs_default = os.path.abspath(DEFAULT_DOWNLOAD_PATH)
    abs_dir = os.path.abspath(directory)

    if directory != DEFAULT_DOWNLOAD_PATH and not os.path.exists(directory):
        print(f"Adresář '{directory}' neexistuje.")
        sys.exit(1)

    if abs_dir == abs_default:
        abs_dir = os.path.join(os.getcwd(), DEFAULT_DOWNLOAD_PATH)
        os.makedirs(abs_dir, exist_ok=True)

    return abs_dir


def handle_choice(choice: str, output_dir: str):
    actions = {
        "v": (CHOICE_VO, "POUZE VIDEO MOŽNOST"),
        "a": (CHOICE_AO, "POUZE AUDIO MOŽNOST"),
        "o": (CHOICE_VA, "VIDEO A AUDIO MOŽNOST"),
        "u": None
    }

    selected = actions.get(choice.lower())
    if selected:
        if choice.lower() == "u":
            ui.print_closing_screen()
            return False
        choice_type, log_msg = selected
        logging.debug(log_msg)
        download_by_choice(download_path=output_dir, download_choice=choice_type)
    return True


def main():
    output_dir = resolve_output_dir(parse_arguments())
    logging.debug(f"Výstupní adresář: {output_dir}")

    ui.set_console_size(ROWS, COLS)

    while True:
        ui.print_basic_menu()
        choice = input(ui.Fore.LIGHTCYAN_EX + "Výběr: " + ui.Fore.WHITE)
        if not handle_choice(choice, output_dir):
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ui.print_interupt()
