import argparse
import sys
from pathlib import Path

class FeatureCodingSteganography:
    def __init__(self):
        self.categories = {
            'CF1': list('aeiou'),
            'CF2': list('bcdfghjklmnpqrstvwxyz'),
        }
        
        self.char_to_category = {}
        for cat_name, chars in self.categories.items():
            for char in chars:
                self.char_to_category[char] = cat_name
    
    def find_transformable(self, text):
        transformable = []
        for i, char in enumerate(text):
            if char.lower() in self.char_to_category:
                category = self.char_to_category[char.lower()]
                transformable.append((i, char, category))
        return transformable
    
    def encode(self, cover_text, secret_binary):
        transformable = self.find_transformable(cover_text)
        
        if len(transformable) == 0:
            raise ValueError("No transformable characters in cover text!")
        
        if len(secret_binary) >= len(transformable):
            raise ValueError(
                f"Secret too long! Need {len(secret_binary)} chars, "
                f"only {len(transformable)} available"
            )
        
        current_state = transformable[0][2]
        positions_to_transform = [transformable[0][0]]
        used_indices = [0]
        
        for bit in secret_binary:
            found = False
            for search_idx in range(used_indices[-1] + 1, len(transformable)):
                pos, char, category = transformable[search_idx]
                
                if bit == '0' and category == current_state:
                    positions_to_transform.append(pos)
                    used_indices.append(search_idx)
                    found = True
                    break
                elif bit == '1' and category != current_state:
                    positions_to_transform.append(pos)
                    used_indices.append(search_idx)
                    current_state = category
                    found = True
                    break
            
            if not found:
                raise ValueError(f"Cannot encode bit. Not enough suitable characters.")
        
        stego_chars = list(cover_text)
        for pos in positions_to_transform:
            stego_chars[pos] = stego_chars[pos].upper()
        
        return ''.join(stego_chars)

def text_to_binary(text):
    return ''.join(format(ord(c), '08b') for c in text)

def read_cover(args):
    if args.ic:
        return args.ic.replace("\\n", "\n")
    if args.fc:
        try:
            return Path(args.fc).read_text(encoding='utf-8').strip()
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
    parser = argparse.ArgumentParser(description='Feature Coding Steganography - Encoder')
    
    group_cover = parser.add_mutually_exclusive_group(required=True)
    group_cover.add_argument('-ic', type=str, help='Cover text bezpośrednio z linii komend')
    group_cover.add_argument('-fc', type=str, help='Plik z cover textem')
    
    group_secret = parser.add_mutually_exclusive_group(required=True)
    group_secret.add_argument('-is', dest='is_', type=str, help='Secret message bezpośrednio z linii komend')
    group_secret.add_argument('-fs', type=str, help='Plik z secret message')
    
    parser.add_argument('-o', type=str, default='stego.txt', help='Plik wyjściowy (domyślnie: stego.txt)')
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
        
        if args.verbose:
            print(f"\n{'=' * 60}")
            print("FEATURE CODING STEGANOGRAPHY - ENCODER")
            print(f"{'=' * 60}")
            print(f"\nCover text: {len(cover_text)} chars")
            print(f"Secret: '{secret_text}' ({len(secret_text)} chars)")
        
        stego = FeatureCodingSteganography()
        secret_binary = text_to_binary(secret_text)
        
        if args.verbose:
            print(f"Binary: {len(secret_binary)} bits")
            transformable = stego.find_transformable(cover_text)
            print(f"Transformable chars: {len(transformable)}")
        
        stego_text = stego.encode(cover_text, secret_binary)
        
        output_path = Path(args.o)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stego_text)
        
        if args.verbose:
            print(f"\n✅ Encoded successfully!")
            print(f"✓ Output: {args.o}")
            print(f"{'=' * 60}\n")
        else:
            print(f"✓ Encoded to: {args.o}")
    
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

