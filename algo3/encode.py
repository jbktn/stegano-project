# encode.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import re
import sys

def text_to_bits(text: str) -> str:
    return ''.join(format(ord(c), '08b') for c in text)

def int_to_bits(n: int, width: int) -> str:
    return format(n, '0{}b'.format(width))

SPACE_BETWEEN_WORDS_REGEX = re.compile(r'(?<=\S) (?=\S)')

def encode(secret: str, cover_text: str) -> str:
    secret_bytes_len = len(secret.encode('utf-8'))
    length_bits = int_to_bits(secret_bytes_len, 32)
    data_bits = ''.join(format(b, '08b') for b in secret.encode('utf-8'))
    bits = length_bits + data_bits

    matches = list(SPACE_BETWEEN_WORDS_REGEX.finditer(cover_text))
    if len(matches) < len(bits):
        raise ValueError("Cover text too short for secret message")

    out_parts = []
    last_end = 0
    used = 0
    for m in matches:
        out_parts.append(cover_text[last_end:m.start()])
        if used < len(bits):
            bit = bits[used]
            out_parts.append('  ' if bit == '1' else ' ')
        else:
            out_parts.append(' ')
        last_end = m.end()
        used += 1
    out_parts.append(cover_text[last_end:])
    return ''.join(out_parts)

def write_pdf(text: str, filename: str):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    text_object = c.beginText(50, height - 50)
    text_object.setFont("Courier", 12)
    for line in text.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)
    c.save()

if __name__ == "__main__":
    # ---- konfiguracja ----
    COVER_FILE = "cover.txt"
    OUTPUT_PDF = "stego.pdf"
    SECRET = "To jest tajna wiadomość ukryta w PDF."  # hardcoded

    # ---- wczytaj cover text ----
    with open(COVER_FILE, "r", encoding="utf-8") as f:
        cover_text = f.read()

    # ---- zakoduj sekret ----
    stego_text = encode(SECRET, cover_text)

    # ---- zapisz do PDF ----
    write_pdf(stego_text, OUTPUT_PDF)

    print(f"[OK] Ukryto wiadomość w {OUTPUT_PDF}")
