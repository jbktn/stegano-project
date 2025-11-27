import textwrap
import re
from pathlib import Path
from bs4 import BeautifulSoup

COVER_FILE = "cover.txt"
OUTPUT_FILE = "stego_subtelny.html"
SECRET_TEXT = "Ukryta wiadomosc TEST 123000321!!!"

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
        return "BLAD DEKODOWANIA"

# ukrywanie
def encode_html_with_formatting(cover_file: str, secret_text: str, output_html: str):
    
    try:
        cover_text = Path(cover_file).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"BRAK PLIKU COVER TEXT: {cover_file}")
        return

    bits = pad_bits(text_to_binary(secret_text))
    blocks = bits_to_blocks(bits)
    lines = cover_text.split('\n')

    if len(blocks) > len(lines):
        print(f"!!!COVER TEXT ma {len(lines)} linii, ")
        print(f"ale potrzeba {len(blocks)} linii, wiadomosc zostanie skrocona.")
        blocks = blocks[:len(lines)]

    html_lines = ['<html><head><style>',
                  'body { font-family: "Times New Roman", serif; }',
                  '.end-00::after { content: "\\00a0"; }',         # 1 spacja na końcu
                  '.end-11::after { content: "\\00a0\\00a0"; }',   # 2 spacje na końcu
                  '.space-01 { word-spacing: 0.15em; }',      # lekkie zwiększenie odstępu
                  '.space-10::before { content: "\\00a0"; }', # spacja przed znakiem spec.
                  '</style></head><body>']

    block_index = 0
    for line in lines:
        if block_index < len(blocks):
            block = blocks[block_index]
            encoded_line = ""
            
            if block == '00':
                # jedna spasja
                encoded_line = f'<span class="end-00">{line}</span>'
            elif block == '11':
		# dwie spacje na koniec
                encoded_line = f'<span class="end-11">{line}</span>'
            elif block == '01':
                # spacja między slowami 
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    encoded_line = f'<span>{parts[0]}<span class="space-01">&nbsp;</span>{parts[1]}</span>'
                else:
                    encoded_line = f'<span>{line}</span>'
            elif block == '10':
                # spacja przed 1. znakiem specjalnym 
                match = re.search(r'([,.!;?])', line)
                if match:
                    idx = match.start()
                    encoded_line = f'<span>{line[:idx]}<span class="space-10"></span>{line[idx:]}</span>'
                else:
                    encoded_line = f'<span>{line}</span>'

            html_lines.append(encoded_line + '<br>')
            block_index += 1
        else:
            html_lines.append(f'<span>{line}</span><br>')

    html_lines.append('</body></html>')
    Path(output_html).write_text('\n'.join(html_lines), encoding='utf-8')
    print(f"+++Plik zapisany: {output_html}")

def decode_html_with_formatting(stego_html: str) -> str: 
    try:
        html_text = Path(stego_html).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"!!!BRAK PLIKU: {stego_html}")
        return ""
        
    soup = BeautifulSoup(html_text, "lxml")
    extracted_bits = ''

    for element in soup.body.find_all('span', recursive=False):
        if not element:
            continue
            
        block_found = False
        
        # Sprawdzanie klas '00' i '11'
        classes = element.get('class', [])
        if 'end-00' in classes:
            extracted_bits += '00'
            block_found = True
        elif 'end-11' in classes:
            extracted_bits += '11'
            block_found = True

        # Sprawdz spany '01', '10'
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
                
        if block_found and ('end-00' in classes or 'end-11' in classes):
             if len(extracted_bits) > 2:
                pass

    return binary_to_text(extracted_bits)

if __name__ == "__main__":
    
    print("----------------------------------------------------")
    print("Algorytm zaczyna dzialanie!")
    print("----------------------------------------------------")

    encode_html_with_formatting(COVER_FILE, SECRET_TEXT, OUTPUT_FILE)
    
    decoded = decode_html_with_formatting(OUTPUT_FILE)
    print(f"Zdekodowano: {decoded}")

    if decoded == SECRET_TEXT:
        print("+++Odkodowano poprawnie.")
    else:
        print("---Zle odczytano.")
