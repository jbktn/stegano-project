#!/usr/bin/env python3
"""
decode.py - Wydobądź ukrytą wiadomość z pliku tekstowego

Użycie:
    python decode.py -i stego.txt
    python decode.py -i stego.txt -o secret.txt
"""

import sys
import argparse
from pathlib import Path


class ZeroWidthSteganography:
    """Steganografia używająca znaków zerowej szerokości Unicode."""

    ZWSP = '\u200B'  # Zero-width space (0)
    ZWNJ = '\u200C'  # Zero-width non-joiner (1)
    ZWJ = '\u200D'   # Zero-width joiner (separator)

    def decode(self, stego_text):
        """Wydobądź ukrytą wiadomość."""
        # Wyciągnij znaki zerowej szerokości
        zw_chars = ''.join(c for c in stego_text 
                          if c in [self.ZWSP, self.ZWNJ, self.ZWJ])

        if not zw_chars:
            return None

        # Konwertuj na binarny
        binary = ''.join('0' if c == self.ZWSP else '1' if c == self.ZWNJ else ''
                        for c in zw_chars)

        # Konwertuj binarny na tekst
        text = ""
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))

        return text if text else None


class FeatureCodingSteganography:
    """Steganografia oparta na kodowaniu cech."""

    def __init__(self):
        self.categories = {
            'CF1': list('aeiouąęóAEIOU'),
            'CF2': list('bcdfghjklmnpqrstvwxyzćłńśźżBCDFGHJKLMNPQRSTVWXYZĆŁŃŚŹŻ'),
        }

        self.char_to_category = {}
        for category, chars in self.categories.items():
            for char in chars:
                self.char_to_category[char] = category

    def decode(self, stego_text):
        """Wydobądź ukrytą wiadomość."""
        # Znajdź transformowane znaki (uppercase)
        transformed = []
        for i, char in enumerate(stego_text):
            char_lower = char.lower()
            if (char.isupper() and char_lower in self.char_to_category):
                transformed.append((i, char_lower, self.char_to_category[char_lower]))

        if len(transformed) < 2:
            return None

        # Dekoduj przez porównanie kategorii
        current_category = transformed[0][2]
        binary = []

        for i in range(1, len(transformed)):
            next_category = transformed[i][2]
            if next_category == current_category:
                binary.append('0')
            else:
                binary.append('1')
                current_category = next_category

        # Konwertuj binarny na tekst
        binary_str = ''.join(binary)
        text = ""
        for i in range(0, len(binary_str), 8):
            byte = binary_str[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))

        return text if text else None


def main():
    parser = argparse.ArgumentParser(
        description='Wydobądź ukrytą wiadomość z pliku tekstowego',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  # Wyświetl wiadomość na ekranie
  python decode.py -i stego.txt

  # Zapisz wiadomość do pliku
  python decode.py -i stego.txt -o secret.txt

  # Spróbuj obu metod automatycznie
  python decode.py -i stego.txt -m auto

Metody:
  auto          - Automatycznie wykryj metodę (domyślnie)
  zero-width    - Dekoduj znaki zerowej szerokości
  feature-coding - Dekoduj transformacje znaków
        """
    )

    parser.add_argument('-i', '--input', required=True,
                       help='Plik ze stego-tekstem')
    parser.add_argument('-o', '--output',
                       help='Plik wyjściowy dla odkodowanej wiadomości')
    parser.add_argument('-m', '--method',
                       choices=['auto', 'zero-width', 'feature-coding'],
                       default='auto',
                       help='Metoda dekodowania (domyślnie: auto)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Pokaż szczegółowe informacje')

    args = parser.parse_args()

    try:
        # Wczytaj stego-tekst
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ Błąd: Plik '{args.input}' nie istnieje!", file=sys.stderr)
            sys.exit(1)

        with open(input_path, 'r', encoding='utf-8') as f:
            stego_text = f.read()

        if not stego_text:
            print("❌ Błąd: Plik jest pusty!", file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(f"📄 Wczytano: {len(stego_text)} znaków")
            print(f"🔍 Metoda: {args.method}")

        # Dekodowanie
        secret_text = None
        method_used = None

        if args.method == 'auto':
            # Spróbuj zero-width najpierw
            zw_system = ZeroWidthSteganography()
            secret_text = zw_system.decode(stego_text)
            if secret_text:
                method_used = 'zero-width'
            else:
                # Spróbuj feature-coding
                fc_system = FeatureCodingSteganography()
                secret_text = fc_system.decode(stego_text)
                if secret_text:
                    method_used = 'feature-coding'

        elif args.method == 'zero-width':
            zw_system = ZeroWidthSteganography()
            secret_text = zw_system.decode(stego_text)
            method_used = 'zero-width'

        else:  # feature-coding
            fc_system = FeatureCodingSteganography()
            secret_text = fc_system.decode(stego_text)
            method_used = 'feature-coding'

        if not secret_text:
            print("❌ Nie znaleziono ukrytej wiadomości!", file=sys.stderr)
            print("   Sprawdź czy plik zawiera zakodowaną wiadomość.", file=sys.stderr)
            sys.exit(1)

        # Wynik
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(secret_text)

            if args.verbose:
                print(f"\n✅ Sukces!")
                print(f"🔓 Odkodowano metodą: {method_used}")
                print(f"📝 Długość wiadomości: {len(secret_text)} znaków")
                print(f"💾 Zapisano do: {args.output}")
            else:
                print(f"✅ Odkodowano wiadomość do pliku: {args.output}")
        else:
            if args.verbose:
                print(f"\n✅ Sukces!")
                print(f"🔓 Odkodowano metodą: {method_used}")
                print(f"📝 Długość wiadomości: {len(secret_text)} znaków")
                print(f"\n{'='*60}")
                print("ODKODOWANA WIADOMOŚĆ:")
                print('='*60)

            print(secret_text)

            if args.verbose:
                print('='*60)

    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
