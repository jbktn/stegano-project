# Nazwa pliku: pdf_paper_algo_v2.py
# Wersja z wczytywaniem pliku i subtelnymi metodami (spacje na końcu linii)
# Wymaga: pip install beautifulsoup4 lxml

import textwrap
import re
from pathlib import Path
from bs4 import BeautifulSoup

# -------------------------------
# Stałe
# -------------------------------
COVER_FILE = "cover.txt"        # Plik z tekstem okrywkowym
OUTPUT_FILE = "stego_subtelny.html" # Wynikowy plik stego
SECRET_TEXT = "ToJestBardzoTajnaWiadomosc123!"

# -------------------------------
# Konwersja Tekst <-> Bity
# -------------------------------
def text_to_binary(secret_text: str) -> str:
    return ''.join(format(b, '08b') for b in secret_text.encode('utf-8'))

def pad_bits(bits: str) -> str:
    return bits if len(bits) % 2 == 0 else '0' + bits

def bits_to_blocks(bits: str) -> list[str]:
    return textwrap.wrap(bits, 2)

def binary_to_text(bits: str) -> str:
    bit_len = (len(bits) // 8) * 8
    bits = bits[:bit_len]
    b_array = bytearray()
    for i in range(0, len(bits), 8):
        byte_str = bits[i:i+8]
        if len(byte_str) == 8:
            b_array.append(int(byte_str, 2))
    try:
        return b_array.decode('utf-8')
    except UnicodeDecodeError:
        return "Błąd dekodowania"

# -------------------------------
# KODOWANIE (Metody subtelne)
# -------------------------------
def encode_html_with_formatting(cover_file: str, secret_text: str, output_html: str):
    
    try:
        cover_text = Path(cover_file).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"[!] Błąd: Nie znaleziono pliku okrywkowego: {cover_file}")
        return

    bits = pad_bits(text_to_binary(secret_text))
    blocks = bits_to_blocks(bits)
    lines = cover_text.split('\n')

    if len(blocks) > len(lines):
        print(f"[!] Ostrzeżenie: Tekst okrywkowy ma {len(lines)} linii, ")
        print(f"    ale potrzeba {len(blocks)} linii. Wiadomość zostanie obcięta.")
        blocks = blocks[:len(lines)]

    # Używamy CSS do wstawiania niewidocznych spacji (spacje niełamliwe)
    # jako pseudo-elementy, co utrudnia wykrycie.
    html_lines = ['<html><head><style>',
                  'body { font-family: "Times New Roman", serif; }',
                  '.end-00::after { content: "\\00a0"; }',         # Jedna spacja na końcu
                  '.end-11::after { content: "\\00a0\\00a0"; }',   # Dwie spacje na końcu
                  '.space-01 { word-spacing: 0.15em; }',      # Lekkie zwiększenie odstępu
                  '.space-10::before { content: "\\00a0"; }', # Spacja przed znakiem spec.
                  '</style></head><body>']

    block_index = 0
    for line in lines:
        if block_index < len(blocks):
            block = blocks[block_index]
            encoded_line = ""
            
            if block == '00':
                # Metoda '00': Dodaj jedną spację na końcu linii
                encoded_line = f'<span class="end-00">{line}</span>'
            elif block == '11':
                # Metoda '11': Dodaj dwie spacje na końcu linii
                encoded_line = f'<span class="end-11">{line}</span>'
            elif block == '01':
                # Metoda '01': Dodaj spację między słowami 
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    encoded_line = f'<span>{parts[0]}<span class="space-01">&nbsp;</span>{parts[1]}</span>'
                else:
                    encoded_line = f'<span>{line}</span>' # Pomiń
            elif block == '10':
                # Metoda '10': Dodaj spację przed znakiem specjalnym 
                match = re.search(r'([,.!;?])', line)
                if match:
                    idx = match.start()
                    encoded_line = f'<span>{line[:idx]}<span class="space-10"></span>{line[idx:]}</span>'
                else:
                    encoded_line = f'<span>{line}</span>' # Pomiń (lub dodaj znak)

            html_lines.append(encoded_line + '<br>')
            block_index += 1
        else:
            html_lines.append(f'<span>{line}</span><br>')

    html_lines.append('</body></html>')
    Path(output_html).write_text('\n'.join(html_lines), encoding='utf-8')
    print(f"[+] Plik stego (metoda subtelna) zapisany: {output_html}")

# -------------------------------
# DEKODOWANIE (dopasowane do metod subtelnych)
# -------------------------------
def decode_html_with_formatting(stego_html: str) -> str:
    
    try:
        html_text = Path(stego_html).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"[!] Błąd: Nie znaleziono pliku stego: {stego_html}")
        return ""
        
    soup = BeautifulSoup(html_text, "lxml")
    extracted_bits = ''

    for element in soup.body.find_all('span', recursive=False):
        if not element:
            continue
            
        block_found = False
        
        # Sprawdź główne klasy (dla '00' i '11')
        classes = element.get('class', [])
        if 'end-00' in classes:
            extracted_bits += '00'
            block_found = True
        elif 'end-11' in classes:
            extracted_bits += '11'
            block_found = True

        # Sprawdź zagnieżdżone tagi dla '01' i '10'
        inner_spans = element.find_all('span', recursive=True)
        for span in inner_spans:
            inner_classes = span.get('class', [])
            if 'space-01' in inner_classes:
                extracted_bits += '01'
                block_found = True
                break
            if 'space-10' in inner_classes:
                extracted_bits += '10'
                block_found = True
                break
                
        # To zapobiega błędom, jeśli linia nie miała kodowania
        # (np. span był tylko dla '01'/'10')
        if block_found and ('end-00' in classes or 'end-11' in classes):
             if len(extracted_bits) > 2:
                # Usunęliśmy podwójne zliczenie, jeśli '01'/'10' było WEWNĄTRZ '00'/'11'
                # To się nie powinno zdarzyć przy obecnej logice kodowania, 
                # ale zabezpiecza dekoder.
                pass

    return binary_to_text(extracted_bits)

# -------------------------------
# Przykład użycia
# -------------------------------
if __name__ == "__main__":
    
    print("--- Testowanie subtelnej implementacji algorytmu z PDF ---")
    
    # 1. Kodowanie
    encode_html_with_formatting(COVER_FILE, SECRET_TEXT, OUTPUT_FILE)
    
    # 2. Dekodowanie
    decoded = decode_html_with_formatting(OUTPUT_FILE)
    print(f"Zdekodowano: {decoded}")

    if decoded == SECRET_TEXT:
        print("Sukces: Dane zgodne.")
    else:
        print("Błąd: Dane niezgodne.")
