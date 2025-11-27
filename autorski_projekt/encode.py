import argparse
import sys
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics

def char_to_shade(c):
    """
    Map character to subtle black shade using its ASCII code.
    Distribute ASCII value across RGB channels for smaller color fluctuations.
    """
    ascii_val = ord(c)
    sense = 128
    ascii_val = max(1, min(ascii_val, 255))
    
    r = int(ascii_val / 36)
    g = int(ascii_val / 6 - r * 6)
    b = int(ascii_val % 6)
    
    return Color(float(r / sense), float(g / sense), float(b / sense))

def embed_hidden_message(pdf_path, visible_text, hidden_message,
                        pagesize=LETTER, font_name="Helvetica", font_size=12,
                        left_margin=50, top_margin=100, bottom_margin=50, leading=None):
    """
    Generates a PDF with text that looks black but encodes a hidden message
    in the color of each character. Text is wrapped into lines and across pages.
    Ignores newline characters.
    """
    if len(visible_text) < len(hidden_message):
        raise ValueError("Visible text must be at least as long as hidden message")
    
    c = canvas.Canvas(pdf_path, pagesize=pagesize)
    width, height = pagesize
    c.setFont(font_name, font_size)
    
    if leading is None:
        leading = int(font_size * 1.2)
    
    max_width = width - 2 * left_margin
    x = left_margin
    y = height - top_margin
    
    hidden_idx = 0  # Index dla hidden message
    
    for i, ch in enumerate(visible_text):
        # Pomij entery
        if ch == '\n':
            x = left_margin
            y -= leading
            if y < bottom_margin + leading:
                c.showPage()
                c.setFont(font_name, font_size)
                x = left_margin
                y = height - top_margin
            continue
        
        if y < bottom_margin + leading:
            c.showPage()
            c.setFont(font_name, font_size)
            x = left_margin
            y = height - top_margin
        
        ch_width = pdfmetrics.stringWidth(ch, font_name, font_size)
        
        if (x - left_margin) + ch_width > max_width:
            x = left_margin
            y -= leading
        
        if y < bottom_margin + leading:
            c.showPage()
            c.setFont(font_name, font_size)
            x = left_margin
            y = height - top_margin
        
        # Koduj tylko jeśli mamy jeszcze tajną wiadomość
        if hidden_idx < len(hidden_message):
            shade = char_to_shade(hidden_message[hidden_idx])
            hidden_idx += 1
            c.setFillColor(shade)
        else:
            c.setFillColor(Color(0, 0, 0))
        
        c.drawString(x, y, ch)
        x += ch_width
    
    c.save()

def read_cover(args):
    if args.ic:
        return args.ic.replace("\\n", "\n")
    if args.fc:
        try:
            return Path(args.fc).read_text(encoding='utf-8')
        except FileNotFoundError:
            print(f"❌ Błąd: plik coveru nie znaleziony: {args.fc}", file=sys.stderr)
            sys.exit(1)
    print("❌ Podaj źródło covera: -ic (tekst) lub -fc (plik)", file=sys.stderr)
    sys.exit(1)

def read_secret(args):
    if args.is_:
        return args.is_
    if args.fs:
        try:
            return Path(args.fs).read_text(encoding='utf-8').strip()
        except FileNotFoundError:
            print(f"❌ Błąd: plik secretu nie znaleziony: {args.fs}", file=sys.stderr)
            sys.exit(1)
    print("❌ Podaj źródło secretu: -is (tekst) lub -fs (plik)", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PDF Color Steganography - Encoder')
    
    group_cover = parser.add_mutually_exclusive_group(required=True)
    group_cover.add_argument('-ic', type=str, help='Cover text bezpośrednio z linii komend')
    group_cover.add_argument('-fc', type=str, help='Plik z cover textem')
    
    group_secret = parser.add_mutually_exclusive_group(required=True)
    group_secret.add_argument('-is', dest='is_', type=str, help='Secret message bezpośrednio z linii komend')
    group_secret.add_argument('-fs', type=str, help='Plik z secret message')
    
    parser.add_argument('-o', type=str, default='hidden_message.pdf', help='Plik wyjściowy PDF (domyślnie: hidden_message.pdf)')
    parser.add_argument('--font-size', type=int, default=12, help='Font size (domyślnie: 12)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        cover_text = read_cover(args)
        secret_text = read_secret(args)
        
        if not cover_text:
            print("❌ Błąd: cover text jest pusty!", file=sys.stderr)
            sys.exit(1)
        
        if not secret_text:
            print("❌ Błąd: secret message jest pusty!", file=sys.stderr)
            sys.exit(1)
        
        # Policz znaki bez enterów
        cover_without_newlines = len([c for c in cover_text if c != '\n'])
        if cover_without_newlines < len(secret_text):
            print(f"❌ Błąd: cover text ({cover_without_newlines} znaków bez enterów) jest za krótki dla secret ({len(secret_text)} znaków)", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"\n{'=' * 60}")
            print("PDF COLOR STEGANOGRAPHY - ENCODER")
            print(f"{'=' * 60}")
            print(f"\nCover text: {cover_without_newlines} chars (bez enterów)")
            print(f"Secret: '{secret_text}' ({len(secret_text)} chars)")
            print(f"Output PDF: {args.o}")
            print(f"Font size: {args.font_size}")
        
        embed_hidden_message(args.o, cover_text, secret_text, font_size=args.font_size)
        
        if args.verbose:
            print(f"\n✅ Encoded successfully!")
            print(f"✓ PDF saved as: {args.o}")
            print(f"{'=' * 60}\n")
        else:
            print(f"✓ Encoded to: {args.o}")
    
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

