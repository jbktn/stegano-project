import textwrap
import re
from pathlib import Path

# ------------------------------------------------------------
# Pomocnicze funkcje konwersji
# ------------------------------------------------------------

def text_to_binary(secret_text: str) -> str:
    """Konwertuje tekst na ciąg bitów (ASCII -> binarny)."""
    return ''.join(format(ord(c), '08b') for c in secret_text)

def pad_bits(bits: str) -> str:
    """Zapewnia parzystą liczbę bitów."""
    return bits if len(bits) % 2 == 0 else '0' + bits

def bits_to_blocks(bits: str) -> list[str]:
    """Dzieli bity na bloki po 2."""
    return textwrap.wrap(bits, 2)

def binary_to_text(bits: str) -> str:
    """Konwertuje ciąg bitów z powrotem na tekst."""
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)

# ------------------------------------------------------------
# Główne funkcje steganografii (zgodne z sekcją 4 pracy)
# ------------------------------------------------------------

def encode_steganography(cover_text: str, secret_text: str) -> str:
    """Implementacja algorytmu z sekcji 4 pracy Roy & Manasmita (2011)."""
    lines = cover_text.split('\n')
    bits = pad_bits(text_to_binary(secret_text))
    blocks = bits_to_blocks(bits)
    
    stego_lines = []
    c = 0  # licznik linii

    for block in blocks:
        if c >= len(lines):
            break  # brak więcej linii w coverze
        
        line = lines[c]

        # --- Implementacja kroków ze specyfikacji ---
        if block == '00':  # Shrink line
            line += ' [SHRINK]'
        elif block == '11':  # Expand line
            line += ' [EXPAND]'
        elif block == '01':  # Addspace()
            words = line.split(' ')
            if len(words) > 1:
                words.insert(1, '')  # podwójna spacja
                line = ' '.join(words)
            else:
                line += '  '
        elif block == '10':  # Addspecial()
            specials = [',', '.', '!', '?', ';', ':']
            found = False
            for s in specials:
                if s in line:
                    line = line.replace(s, ' ' + s, 1)
                    found = True
                    break
            if not found:
                line += ' *'
        stego_lines.append(line)
        c += 1

    # dopisz pozostałe niezmienione linie jeśli zostały
    stego_lines.extend(lines[c:])
    return '\n'.join(stego_lines)


def decode_steganography(stego_text: str) -> str:
    """Dekodowanie zgodnie z sekcją 4.2 pracy Roy & Manasmita (2011)."""
    lines = stego_text.split('\n')
    extracted_bits = ''

    for line in lines:
        if '[SHRINK]' in line:
            extracted_bits += '00'
        elif '[EXPAND]' in line:
            extracted_bits += '11'
        elif '  ' in line and not '[EXPAND]' in line and not '[SHRINK]' in line:
            extracted_bits += '01'
        elif any(re.search(r'\s' + re.escape(s), line) for s in [',', '.', '!', '?', ';', ':', '*']):
            extracted_bits += '10'

    return binary_to_text(extracted_bits)

# ------------------------------------------------------------
# Operacje na plikach
# ------------------------------------------------------------

def encode_file(cover_path: str, secret_path: str, stego_path: str):
    """Koduje sekretną wiadomość z pliku w cover.txt i zapisuje wynik w stego.txt"""
    cover_text = Path(cover_path).read_text(encoding='utf-8')
    secret_text = Path(secret_path).read_text(encoding='utf-8')

    stego_text = encode_steganography(cover_text, secret_text)
    Path(stego_path).write_text(stego_text, encoding='utf-8')
    print(f"[+] Zapisano stego tekst do pliku: {stego_path}")

def decode_file(stego_path: str, output_path: str):
    """Odczytuje sekretną wiadomość z pliku stego.txt i zapisuje do pliku."""
    stego_text = Path(stego_path).read_text(encoding='utf-8')
    decoded_secret = decode_steganography(stego_text)
    Path(output_path).write_text(decoded_secret, encoding='utf-8')
    print(f"[+] Odczytano wiadomość i zapisano do pliku: {output_path}")

# ------------------------------------------------------------
# Uruchomienie przykładowe (można usunąć w wersji produkcyjnej)
# ------------------------------------------------------------

if __name__ == "__main__":
    # przykładowe pliki wejściowe
    encode_file("cover.txt", "secret.txt", "stego.txt")
    decode_file("stego.txt", "decoded.txt")
