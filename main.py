import os
import sys
import logging

import ui
from yt_downloader import download_by_choice, CHOICE_VO, CHOICE_AO, CHOICE_VA

DEFAULT_DOWNLOAD_PATH = "YTDownload"
ROWS = 24
COLS = 120

logging.basicConfig(level=logging.CRITICAL)

def parse_arguments():
    if "-h" in sys.argv or "--help" in sys.argv:
        # Bude volána funkce z ui na print help
        print("Program pro stahování videí/hudby z YouTube.")
        print("Použití: main.py [výstupní_adresář]")
        print("V případě, že nenapíšete žádný adresář, budou všechny soubory uloženy do výchozí složky YTDownload")
        sys.exit(0)
    
    if len(sys.argv) > 2:
        print("Chyba: Příliš mnoho argumentů.") # Bude volána funkce u ui na nějaký error list
        sys.exit(1)

    if len(sys.argv) == 2:
        # Pokud bude velikost vstupních argumentů rovna 2 a nebude tam přepínač pro nápovědu, tak si uložíme cestu
        output_dir = sys.argv[1]
    else:
        # Pokud bude program spuštěn bez argumentu, tak se bude ukládat do defaultní složky
        output_dir = DEFAULT_DOWNLOAD_PATH

    return output_dir

def main():
    # V případě, že nebudeme chtít nápovědu, tak se vrátí název složky/cesta ke složce, kam budeme chtít ukládat soubory
    output_dir = parse_arguments()
    logging.debug(f" {output_dir}")

    # Kontrola existence adresáře, kam chceme ukládat soubory
    if not output_dir is DEFAULT_DOWNLOAD_PATH and not os.path.exists(output_dir):
        print(f"Adresář '{output_dir}' neexistuje.")
        sys.exit(1)

    # Výchozí cesta pro uložení souborů
    output_dir = os.path.abspath(output_dir)

    # Pokud je cesta 'YTDownload', vytvoří se složka 'YTDownload' ve stejném adresáři jako spouštěný program
    if output_dir == os.path.abspath(DEFAULT_DOWNLOAD_PATH):
        output_dir = os.path.join(os.getcwd(), DEFAULT_DOWNLOAD_PATH)
        os.makedirs(output_dir, exist_ok=True)

    # Logika programu než se přejde do funkce z yt_downloader modulu
    ui.set_console_size(ROWS, COLS)
    end_program = False
    while not end_program:
        logging.debug(f" {output_dir}")

        ui.print_basic_menu()
        choice = input(ui.Fore.LIGHTCYAN_EX + "Výběr: " + ui.Fore.WHITE)

        if choice.lower() == "u":
            ui.print_closing_screen()
            end_program = True

        elif choice.lower() == "v":
            logging.debug(f"POUZE VIDEO MOŽNOST")
            download_by_choice(download_pathway = output_dir, download_choice = CHOICE_VO)

        elif choice.lower() == "a":
            logging.debug(f"POUZE AUDIO MOŽNOST")
            download_by_choice(download_pathway = output_dir, download_choice = CHOICE_AO)

        elif choice.lower() == "o":
            logging.debug(f"VIDEO A AUDIO MOŽNOST")
            download_by_choice(download_pathway = output_dir, download_choice = CHOICE_VA)

        #end_program = True # Pro debug, potom se smaže, potřebuji vidět výpis debugu při pouze jednom běhu

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ui.print_interupt()