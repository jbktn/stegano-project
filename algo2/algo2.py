from pathlib import Path
from bs4 import BeautifulSoup
import textwrap

# -------------------------------
# Text <-> Binary
# -------------------------------
def text_to_binary(secret_text: str) -> str:
    return ''.join(format(ord(c), '08b') for c in secret_text)

def pad_bits(bits: str) -> str:
    return bits if len(bits) % 2 == 0 else '0' + bits

def bits_to_blocks(bits: str) -> list[str]:
    return textwrap.wrap(bits, 2)

def binary_to_text(bits: str) -> str:
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)

# -------------------------------
# Encode HTML
# -------------------------------
def encode_html(cover_text: str, secret_text: str, output_html: str):
    bits = pad_bits(text_to_binary(secret_text))
    blocks = bits_to_blocks(bits)
    lines = cover_text.split('\n')

    html_lines = ['<html><body>']
    for i, line in enumerate(lines):
        if i < len(blocks):
            block = blocks[i]
            # Wrap each line in a <span> with data-bit attribute
            encoded_line = f'<span data-bit="{block}">{line}</span>'
        else:
            encoded_line = f'<span>{line}</span>'
        html_lines.append(encoded_line + '<br>')
    html_lines.append('</body></html>')

    Path(output_html).write_text('\n'.join(html_lines), encoding='utf-8')
    print(f"[+] Stego HTML saved: {output_html}")

# -------------------------------
# Decode HTML
# -------------------------------
def decode_html(stego_html: str) -> str:
    html_text = Path(stego_html).read_text(encoding='utf-8')
    soup = BeautifulSoup(html_text, "html.parser")
    extracted_bits = ''

    for span in soup.find_all('span'):
        if 'data-bit' in span.attrs:
            extracted_bits += span['data-bit']

    return binary_to_text(extracted_bits)

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    cover_text = """Lorem ipsum dolor sit amet,
consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."""
    secret_text = "qwerty"

    encode_html(cover_text, secret_text, "stego.html")
    decoded = decode_html("stego.html")
    print(f"Decoded secret: {decoded}")
