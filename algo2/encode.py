import argparse
import textwrap
import re
from pathlib import Path

def text_to_binary(secret_text: str) -> str:
    return ''.join(format(b, '08b') for b in secret_text.encode('utf-8'))

def pad_bits(bits: str) -> str:
    return bits if len(bits) % 2 == 0 else '0' + bits

def bits_to_blocks(bits: str) -> list:
    return textwrap.wrap(bits, 2)

def encode_html_with_formatting(cover_text: str, secret_text: str, output_html: str):
    """Enkoduje tajną wiadomość w tekście coveru poprzez formatowanie."""
    bits = pad_bits(text_to_binary(secret_text))
    blocks = bits_to_blocks(bits)
    lines = cover_text.split('\n')
    
    if len(blocks) > len(lines):
        print(f"⚠️  COVER TEXT ma {len(lines)} linii, ale potrzeba {len(blocks)} linii.")
        print(f"   Wiadomość zostanie skrócona.")
        blocks = blocks[:len(lines)]
    
    html_lines = ['<!DOCTYPE html>', '<html><head><meta charset="utf-8"><title>Stego Text</title></head><body><pre style="font-family: monospace; line-height: 1.8;">']
    block_index = 0
    
    for line in lines:
        if block_index < len(blocks):
            block = blocks[block_index]
            encoded_line = ""
            
            if block == '00':      # brak dodatkowej spacji
                encoded_line = f'{line}'
            elif block == '11':    # dwie spacje na koniec
                encoded_line = f'{line}  '
            elif block == '01':    # spacja między słowami
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    encoded_line = f'{parts[0]}  {parts[1]}'
                else:
                    encoded_line = f'{line}'
            elif block == '10':    # spacja przed znakiem specjalnym
                match = re.search(r'([,.!;?])', line)
                if match:
                    idx = match.start()
                    encoded_line = f'{line[:idx]} {line[idx:]}'
                else:
                    encoded_line = f'{line}'
            
            html_lines.append(encoded_line)
            block_index += 1
    
    html_lines.extend(['</pre></body></html>'])
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines))
    
    print(f"✓ Zapisano HTML: {output_html}")
    print(f"✓ Ukryta wiadomość: {secret_text!r}")
    print(f"✓ Użyto {len(blocks)} bloków (linii).")

def read_cover(args):
    if args.ic:
        return args.ic.replace("\\n", "\n")
    if args.fc:
        try:
            return Path(args.fc).read_text(encoding='utf-8')
        except FileNotFoundError:
            print(f"❌ Błąd: plik coveru nie znaleziony: {args.fc}")
            exit(1)
    print("❌ Podaj źródło covera: -ic (tekst) lub -fc (plik)")
    exit(1)

def read_secret(args):
    if args.is_:
        return args.is_
    if args.fs:
        try:
            return Path(args.fs).read_text(encoding='utf-8').strip()
        except FileNotFoundError:
            print(f"❌ Błąd: plik secretu nie znaleziony: {args.fs}")
            exit(1)
    print("❌ Podaj źródło secretu: -is (tekst) lub -fs (plik)")
    exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enkoduj tajną wiadomość w tekście coveru")
    
    group_cover = parser.add_mutually_exclusive_group(required=True)
    group_cover.add_argument('-ic', type=str, help="Cover text bezpośrednio z linii komend")
    group_cover.add_argument('-fc', type=str, help="Plik z cover textem")
    
    group_secret = parser.add_mutually_exclusive_group(required=True)
    group_secret.add_argument('-is', dest='is_', type=str, help="Secret message bezpośrednio z linii komend")
    group_secret.add_argument('-fs', type=str, help="Plik z secret message")
    
    parser.add_argument('-o', type=str, default="stego.html", help="Plik wyjściowy HTML (domyślnie: stego.html)")
    
    args = parser.parse_args()
    
    cover = read_cover(args)
    secret = read_secret(args)
    encode_html_with_formatting(cover, secret, args.o)
