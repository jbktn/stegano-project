import argparse
import sys
from pathlib import Path

def sum_of_squares_of_digits(r: int) -> int:
    return sum((int(d)**2) for d in str(r))

def decipher_one_time_pad(ciphertext: bytes, key: bytes) -> bytes:
    if len(ciphertext) != len(key):
        raise ValueError("Ciphertext and key lengths differ.")
    
    plain = []
    for e, r in zip(ciphertext, key):
        s = sum_of_squares_of_digits(r)
        x = s // 10
        y = s % 10
        
        n = (e - r + (x*y)) % 256
        plain.append(n)
    
    return bytes(plain)

def extract_missing_letters(stego_text: str) -> bytes:
    """Wyciągnij pozycje znaków '?' z tekstu stego."""
    words = stego_text.split()
    positions = []
    
    for word in words:
        if '?' in word:
            pos = word.index('?')
            positions.append(pos)
    
    return bytes(positions)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dekoduj tajną wiadomość z One-Time Pad + Missing Letter Hide")
    parser.add_argument('stego_file', type=str, help="Ścieżka do pliku stego_text.txt")
    parser.add_argument('-k', dest='key_file', type=str, default="key.bin", help="Plik z kluczem (domyślnie: key.bin)")
    parser.add_argument('-o', dest='out_file', type=str, default=None, help="Plik wyjściowy (opcjonalnie)")
    
    args = parser.parse_args()
    
    # Walidacja pliku stego
    if not Path(args.stego_file).exists():
        print(f"❌ Błąd: plik stego nie znaleziony: {args.stego_file}")
        sys.exit(1)
    
    # Walidacja pliku klucza
    if not Path(args.key_file).exists():
        print(f"❌ Błąd: plik klucza nie znaleziony: {args.key_file}")
        sys.exit(1)
    
    # Wczytaj stego text
    with open(args.stego_file, "r", encoding="utf-8") as f:
        stego_text = f.read()
    
    # Wyciągnij pozycje '?'
    positions = extract_missing_letters(stego_text)
    
    # Wczytaj klucz i ciphertext
    with open(args.key_file, "rb") as f:
        data = f.read()
    
    otp_len = int.from_bytes(data[:4], "big")
    otp_key = data[4:4+otp_len]
    cipher = data[4+otp_len:]
    
    # Dekryptuj
    
    try:
        plaintext_bytes = decipher_one_time_pad(cipher, otp_key)
        
        message = plaintext_bytes.decode("utf-8", errors="replace")
        
        print(message)

        if args.out_file:
            Path(args.out_file).write_text(message, encoding='utf-8')
            print(f"✓ Saved to: {args.out_file}")
        
    except Exception as e:
        print(f"❌ Błąd dekodowania: {e}")
        sys.exit(1)

