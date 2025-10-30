# encode.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import re
import sys
import textwrap # <-- DODANE

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
    
    # --- START POPRAWKI PIONOWEJ ---
    left_margin = 50
    top_margin = 50
    bottom_margin = 50
    
    font_name = "Courier"
    font_size = 12
    # Odstęp między liniami (np. 120% rozmiaru czcionki)
    line_height = font_size * 1.2 

    # Zacznij pisać tekst od góry
    text_object = c.beginText(left_margin, height - top_margin)
    text_object.setFont(font_name, font_size)
    
    # Śledź aktualną pozycję Y (pionową)
    current_y = height - top_margin

    for line in text.splitlines():
        # Sprawdź, czy kolejna linia zmieści się na stronie
        if current_y < bottom_margin:
            # Jeśli nie, narysuj dotychczasowy tekst
            c.drawText(text_object)
            # I zacznij nową stronę
            c.showPage()
            
            # Zresetuj obiekt tekstowy na górze nowej strony
            text_object = c.beginText(left_margin, height - top_margin)
            text_object.setFont(font_name, font_size)
            current_y = height - top_margin
        
        # Dodaj linię do obiektu tekstowego
        text_object.textLine(line)
        # Ręcznie przesuń pozycję Y o wysokość linii
        current_y -= line_height
    
    # Narysuj pozostały tekst na ostatniej stronie
    c.drawText(text_object)
    # --- KONIEC POPRAWKI ---
    
    c.save() # Zapisz plik

if __name__ == "__main__":
    # ---- konfiguracja ----
    COVER_FILE = "cover.txt"
    OUTPUT_PDF = "stego.pdf"
    SECRET = "To jest tajna wiadomość ukryta w PDF."

    # ---- wczytaj cover text ----
    with open(COVER_FILE, "r", encoding="utf-8") as f:
        original_cover_text = f.read()

    # --- START POPRAWKI: Formatuj tekst PRZED kodowaniem ---
    
    # Najpierw zwiń cały tekst do jednej linii, usuwając oryginalne złamania
    single_line_text = " ".join(original_cover_text.split())
    
    # Oblicz bezpieczną szerokość łamania w znakach dla Courier 12 na A4
    usable_width_points = A4[0] - 50 - 50 # A4[0] to szerokość
    char_width = 12 * 0.6 # Szerokość znaku Courier 12pt
    wrap_width_chars = int(usable_width_points / char_width) # ok. 68

    wrapper = textwrap.TextWrapper(
        width=wrap_width_chars, 
        break_long_words=False,
        replace_whitespace=True # To jest bezpieczne, bo robimy to PRZED kodowaniem
    )
    
    # Stwórz nowy cover_text z poprawnymi złamaniami linii
    cover_text = "\n".join(wrapper.wrap(single_line_text))
    # --- KONIEC POPRAWKI ---

    # ---- zakoduj sekret ----
    # Użyj nowego, sformatowanego tekstu
    stego_text = encode(SECRET, cover_text)

    # ---- zapisz do PDF ----
    # Użyj poprawionej funkcji write_pdf
    write_pdf(stego_text, OUTPUT_PDF)

    print(f"[OK] Ukryto wiadomość w {OUTPUT_PDF}")
