import argparse
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ Błąd: PyMuPDF nie jest zainstalowany!", file=sys.stderr)
    print("Zainstaluj: pip install PyMuPDF", file=sys.stderr)
    sys.exit(1)

def rgb_to_char(r, g, b):
    """
    Convert RGB values back to character based on the distributed encoding scheme.
    """
    sense = 128
    r_val = round(r * sense)
    g_val = round(g * sense)
    b_val = round(b * sense)
    
    ascii_val = r_val * 36 + g_val * 6 + b_val
    
    if 1 <= ascii_val <= 255:
        return chr(ascii_val)
    return ''

def int_to_rgb(color_int):
    r = (color_int >> 16) & 255
    g = (color_int >> 8) & 255
    b = color_int & 255
    return r / 255, g / 255, b / 255

def extract_hidden_message(pdf_path):
    doc = fitz.open(pdf_path)
    hidden_message = ""
    
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    color_int = span.get("color")
                    span_text = span.get("text", "")
                    
                    # Pomij znaki nowego wiersza
                    if span_text == '\n' or not span_text:
                        continue
                    
                    if color_int is not None:
                        r, g, b_val = int_to_rgb(color_int)
                        
                        # Sprawdzaj każdy znak w span'ie, ale pomijaj entery
                        for char in span_text:
                            if char == '\n':
                                continue
                            
                            if (r > 0 or g > 0 or b_val > 0) and not (r == 0 and g == 0 and b_val == 0):
                                decoded_char = rgb_to_char(r, g, b_val)
                                if decoded_char:
                                    hidden_message += decoded_char
    
    doc.close()
    return hidden_message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PDF Color Steganography - Decoder')
    parser.add_argument('pdf_file', type=str, help='Ścieżka do pliku PDF')
    parser.add_argument('-o', type=str, default=None, help='Plik wyjściowy (opcjonalnie)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        pdf_path = Path(args.pdf_file)
        
        if not pdf_path.exists():
            print(f"❌ Błąd: plik PDF nie znaleziony: {args.pdf_file}", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"\n{'=' * 60}")
            print("PDF COLOR STEGANOGRAPHY - DECODER")
            print(f"{'=' * 60}")
            print(f"\nReading PDF: {args.pdf_file}")
        
        hidden_message = extract_hidden_message(str(pdf_path))
        
        if not hidden_message:
            print("⚠️  Brak ukrytej wiadomości w PDF lub wiadomość jest pusta")
        else:
            if args.verbose:
                print(f"✓ Extracted {len(hidden_message)} characters")
            
            if args.o:
                output_path = Path(args.o)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(hidden_message)
                if args.verbose:
                    print(f"✓ Decoded: '{hidden_message[:50]}{'...' if len(hidden_message) > 50 else ''}'")
                    print(f"✓ Saved to: {args.o}")
                    print(f"{'=' * 60}\n")
                else:
                    print(f"✓ Decoded to: {args.o}")
            else:
                if args.verbose:
                    print(f"\n{'=' * 60}")
                    print("DECODED MESSAGE:")
                    print(f"{'=' * 60}\n")
                print(hidden_message)
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

