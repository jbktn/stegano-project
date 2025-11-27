import argparse
import sys
import io
from pathlib import Path
from bs4 import BeautifulSoup
import re

def binary_to_text(bits: str) -> str:
    """Konwertuje ciąg bitów z powrotem na tekst."""
    if not bits:
        return ""
    
    bit_len = (len(bits) // 8) * 8
    if bit_len == 0:
        return ""
    
    bits = bits[:bit_len]
    b_array = bytearray()
    
    for i in range(0, len(bits), 8):
        byte_str = bits[i:i+8]
        if len(byte_str) == 8:
            b_array.append(int(byte_str, 2))
    
    try:
        return b_array.decode('utf-8')
    except UnicodeDecodeError:
        return "❌ BŁĄD DEKODOWANIA"

def decode_html_with_formatting(input_html: str):
    """Dekoduje tajną wiadomość z formatowanego HTML (algorytm 2 - spacje)."""
    try:
        html_content = Path(input_html).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ Błąd: plik HTML nie znaleziony: {input_html}", file=sys.stderr)
        sys.exit(1)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    pre_tag = soup.find('pre')
    
    if not pre_tag:
        print("❌ Błąd: nie znaleziono tagu <pre> w HTML", file=sys.stderr)
        sys.exit(1)
    
    lines = pre_tag.get_text().split('\n')
    bits = ""
    
    for line in lines:
        # Pomij puste linie
        if not line.strip():
            continue
        
        # Sprawdzaj formaty spacji - DOKŁADNY PORZĄDEK!
        if line.endswith('  '):           # dwie spacje na koniec -> '11'
            bits += '11'
        elif line.endswith(' '):          # JEDNA spacja na koniec
            bits += '00'
        elif '  ' in line:                # dwie spacje w środku -> '01'
            bits += '01'
        elif re.search(r'\s[,.!;?]', line):  # spacja przed znakiem specjalnym -> '10'
            bits += '10'
        else:                             # brak dodatkowych spacji -> '00'
            bits += '00'
    
    message = binary_to_text(bits)
    return message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dekoduj tajną wiadomość z HTML (algorytm 2 - formatowanie)')
    parser.add_argument('input_html', type=str, help='Ścieżka do pliku HTML do dekodowania')
    parser.add_argument('-o', dest='out_file', type=str, default=None, help='Plik wyjściowy (opcjonalnie)')
    
    args = parser.parse_args()
    
    try:
        message = decode_html_with_formatting(args.input_html)
        
        # Wypisz do stdout (czyta aplikacja)
        sys.stdout.write(message)
        sys.stdout.flush()  # WAŻNE - flush buffera!
        
        if args.out_file:
            Path(args.out_file).write_text(message, encoding='utf-8')
    
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

