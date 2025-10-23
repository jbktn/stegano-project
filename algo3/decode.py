# decode.py
import re
from PyPDF2 import PdfReader

SPACE_BETWEEN_WORDS_REGEX = re.compile(r'(?<=\S) (?=\S)')

def bits_to_int(bits: str) -> int:
    return int(bits, 2) if bits else 0

def decode_bits(bit_str: str) -> str:
    length_bits = bit_str[:32]
    secret_len = bits_to_int(length_bits)
    needed_bits = secret_len * 8
    data_bits = bit_str[32:32 + needed_bits]
    chars = [data_bits[i:i+8] for i in range(0, len(data_bits), 8)]
    return ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)

def extract_text_from_pdf(filename: str) -> str:
    reader = PdfReader(filename)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def decode_from_text(stego_text: str) -> str:
    bits = []
    for m in SPACE_BETWEEN_WORDS_REGEX.finditer(stego_text):
        # policz liczbę spacji od tej pozycji
        start = m.start()
        cnt = 0
        while start + cnt < len(stego_text) and stego_text[start + cnt] == ' ':
            cnt += 1
        bits.append('1' if cnt > 1 else '0')
    bit_str = ''.join(bits)
    return decode_bits(bit_str)

if __name__ == "__main__":
    INPUT_PDF = "stego.pdf"

    text = extract_text_from_pdf(INPUT_PDF)
    secret = decode_from_text(text)

    print(f"Odczytany sekret:\n{secret}")
