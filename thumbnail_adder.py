from mutagen.id3 import ID3, APIC
import os
import sys

def copy_apic_to_mp3(input_file_path, output_file_path):
    if not os.path.isfile(input_file_path) or not os.path.isfile(output_file_path):
        print("Vstupní/Výstupní soubor neexistuje!")
        return
    
    input_audio = ID3(input_file_path)
    output_audio = ID3(output_file_path)

    for tag_key, tag_value in input_audio.items():
        print(f"{tag_key}")
        if tag_key.startswith('APIC'):
            thumb_data = tag_value.data
            thumbnail = APIC(
                data=thumb_data,
                mime='image/jpeg',
                desc='thumbnail'
            )
            output_audio.add(thumbnail)

    output_audio.save()
    print("Kopírování APIC údajů dokončeno!")

# Získání správných cest k souborům ze vstupních parametrů programu
if len(sys.argv) < 5:
    print("Nebyly zadány dostatečné vstupní parametry!")
    print("Použití: python3 thumbnail_adder.py -i input_file.mp3 -o output_file.mp3")
else:
    input_mp3_file = ""
    output_mp3_file = ""
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-i" and i+1 < len(sys.argv):
            input_mp3_file = sys.argv[i+1]
        elif sys.argv[i] == "-o" and i+1 < len(sys.argv):
            output_mp3_file = sys.argv[i+1]

    if input_mp3_file == "" or output_mp3_file == "":
        print("Nebyly zadány dostatečné vstupní parametry!")
        print("Použití: python3 thumbnail_adder.py -i input_file.mp3 -o output_file.mp3")
    else:
        # Kopírování APIC údajů z vstupního MP3 souboru do výstupního MP3 souboru
        copy_apic_to_mp3(input_mp3_file, output_mp3_file)