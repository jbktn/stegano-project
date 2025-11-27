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
    
    def decode(self, stego_text):
        transformed = []
        for i, char in enumerate(stego_text):
            char_lower = char.lower()
            if char.isupper() and char_lower in self.char_to_category:
                category = self.char_to_category[char_lower]
                transformed.append((i, char_lower, category))
        
        if len(transformed) < 2:
            return None
        
        current_state = transformed[0][2]
        decoded_bits = []
        
        for i in range(1, len(transformed)):
            next_state = transformed[i][2]
            if next_state == current_state:
                decoded_bits.append('0')
            else:
                decoded_bits.append('1')
            current_state = next_state
        
        return ''.join(decoded_bits)

def binary_to_text(binary_str):
    if len(binary_str) % 8 != 0:
        binary_str = binary_str + '0' * (8 - len(binary_str) % 8)
    
    text = ""
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i+8]
        text += chr(int(byte, 2))
    
    return text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Feature Coding Steganography - Decoder')
    parser.add_argument('stego_file', type=str, help='Ścieżka do pliku stego')
    parser.add_argument('-o', type=str, default=None, help='Plik wyjściowy (opcjonalnie)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        stego_path = Path(args.stego_file)
        
        if not stego_path.exists():
            print(f"❌ Błąd: plik nie znaleziony: {args.stego_file}", file=sys.stderr)
            sys.exit(1)
        
        with open(stego_path, 'r', encoding='utf-8') as f:
            stego_text = f.read()
        
        if not stego_text:
            print("❌ Błąd: plik jest pusty!", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"\n{'=' * 60}")
            print("FEATURE CODING STEGANOGRAPHY - DECODER")
            print(f"{'=' * 60}")
            print(f"\nInput: {len(stego_text)} chars")
        
        stego = FeatureCodingSteganography()
        decoded_binary = stego.decode(stego_text)
        
        if not decoded_binary:
            print("❌ Błąd: nie znaleziono ukrytej wiadomości!", file=sys.stderr)
            sys.exit(1)
        
        secret_text = binary_to_text(decoded_binary)
        
        if args.verbose:
            print(f"Binary: {len(decoded_binary)} bits")
            print(f"Message: {len(secret_text)} chars")
        
        if args.o:
            output_path = Path(args.o)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(secret_text)
            if args.verbose:
                print(f"\n✓ Decoded: '{secret_text}'")
                print(f"✓ Saved to: {args.o}")
                print(f"{'=' * 60}\n")
            else:
                print(f"✓ Decoded to: {args.o}")
        else:
            if args.verbose:
                print(f"\n{'=' * 60}")
                print("DECODED MESSAGE:")
                print(f"{'=' * 60}\n")
            print(secret_text)
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

