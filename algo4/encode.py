import argparse
import random
import sys
from pathlib import Path

def sum_of_squares_of_digits(r: int) -> int:
    return sum((int(d)**2) for d in str(r))

def encipher_one_time_pad(plaintext: bytes, rng_seed=None):
    if rng_seed is not None:
        random.seed(rng_seed)
    
    A = [random.randrange(256) for _ in range(1000)]
    cipher, key = [], []
    
    for b in plaintext:
        i = random.randrange(len(A))
        r = A[i]
        key.append(r)
        A[i] = random.randrange(256)
        
        s = sum_of_squares_of_digits(r)
        x = s // 10
        y = s % 10
        
        e = (b - (x*y) + r) % 256
        cipher.append(e)
    
    return bytes(cipher), bytes(key)

def missing_letter_hide(ciphertext: bytes, cover_text: str, rng_seed=None):
    if rng_seed is not None:
        random.seed(rng_seed)
    
    words = cover_text.split()
    new_words = []
    w_index = 0
    
    # one '?' per ciphertext byte
    for b in ciphertext:
        if w_index >= len(words):
            raise ValueError(f"Not enough words in cover text. Need {len(ciphertext)} words, got {len(words)}")
        
        word = list(words[w_index])
        w_index += 1
        
        if not any(c.isalpha() for c in word):
            new_words.append("".join(word))
            continue
        
        pos = (b % len(word)) or 1
        word[pos - 1] = '?'
        new_words.append("".join(word))
    
    # append remaining words untouched
    new_words.extend(words[w_index:])
    
    return " ".join(new_words)

def read_cover(args):
    if args.ic:
        return args.ic.replace("\\n", "\n")
    if args.fc:
        try:
            return Path(args.fc).read_text(encoding='utf-8')
        except FileNotFoundError:
            print(f"❌ Błąd: plik coveru nie znaleziony: {args.fc}")
            sys.exit(1)
    print("❌ Podaj źródło covera: -ic (tekst) lub -fc (plik)")
    sys.exit(1)

def read_secret(args):
    if args.is_:
        return args.is_
    if args.fs:
        try:
            return Path(args.fs).read_text(encoding='utf-8').strip()
        except FileNotFoundError:
            print(f"❌ Błąd: plik secretu nie znaleziony: {args.fs}")
            sys.exit(1)
    print("❌ Podaj źródło secretu: -is (tekst) lub -fs (plik)")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enkoduj tajną wiadomość z One-Time Pad i Missing Letter Hide")
    
    group_cover = parser.add_mutually_exclusive_group(required=True)
    group_cover.add_argument('-ic', type=str, help="Cover text bezpośrednio z linii komend")
    group_cover.add_argument('-fc', type=str, help="Plik z cover textem")
    
    group_secret = parser.add_mutually_exclusive_group(required=True)
    group_secret.add_argument('-is', dest='is_', type=str, help="Secret message bezpośrednio z linii komend")
    group_secret.add_argument('-fs', type=str, help="Plik z secret message")
    
    parser.add_argument('-s', dest='seed', type=int, default=42, help="RNG seed dla One-Time Pad (domyślnie: 42)")
    parser.add_argument('-hs', dest='hide_seed', type=int, default=123, help="RNG seed dla hiding (domyślnie: 123)")
    parser.add_argument('-o', type=str, default="stego_text.txt", help="Plik wyjściowy stego (domyślnie: stego_text.txt)")
    parser.add_argument('-k', type=str, default="key.bin", help="Plik wyjściowy klucza (domyślnie: key.bin)")
    
    args = parser.parse_args()
    
    # Wczytaj cover i secret
    cover_text = read_cover(args)
    secret_message = read_secret(args)
    
    # Validacja
    cover_words = cover_text.split()
    if len(cover_words) < len(secret_message):
        print(f"❌ Błąd: cover text ma {len(cover_words)} słów, ale secret ma {len(secret_message)} bajtów")
        print("   Potrzeba co najmniej tyle samo słów co znaków w tajnej wiadomości")
        sys.exit(1)
    
    print(f"\n{'=' * 60}")
    print("STEGANOGRAPHY: One-Time Pad + Missing Letter Hide")
    print(f"{'=' * 60}")
    print(f"\nCover text: {len(cover_words)} słów")
    print(f"Secret message: {secret_message!r}")
    print(f"Message length: {len(secret_message)} bajtów")
    print(f"\nRNG seed (OTP): {args.seed}")
    print(f"RNG seed (hiding): {args.hide_seed}")
    
    # Enkoduj
    print(f"\n{'=' * 60}")
    print("ENCODING")
    print(f"{'=' * 60}")
    
    secret_bytes = secret_message.encode('utf-8')
    cipher, otp_key = encipher_one_time_pad(secret_bytes, rng_seed=args.seed)
    print(f"✓ Encrypted with One-Time Pad: {len(cipher)} bytes")
    
    stego_text = missing_letter_hide(cipher, cover_text, rng_seed=args.hide_seed)
    print(f"✓ Hidden in cover text with '?' characters")
    
    # Zapisz stego text
    with open(args.o, 'w', encoding='utf-8') as f:
        f.write(stego_text)
    print(f"✓ Saved stego text: {args.o}")
    
    # Zapisz klucz + ciphertext
    with open(args.k, 'wb') as f:
        f.write(len(otp_key).to_bytes(4, "big"))
        f.write(otp_key)
        f.write(cipher)
    print(f"✓ Saved key + cipher: {args.k}")
    
    print(f"\n{'=' * 60}")
    print("Preview (stego text):")
    print(f"{'=' * 60}")
    print(stego_text[:300] + ("..." if len(stego_text) > 300 else ""))
    print(f"\n✅ Encoding complete!")

