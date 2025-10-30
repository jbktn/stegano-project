import sys
import argparse
from pathlib import Path


class ZeroWidthSteganography:
    """Steganografia używająca znaków zerowej szerokości Unicode."""

    ZWSP = '\u200B'  # Zero-width space (0)
    ZWNJ = '\u200C'  # Zero-width non-joiner (1)
    ZWJ = '\u200D'   # Zero-width joiner (separator)

    def encode(self, cover_text, secret_text):
        """Ukryj secret_text w cover_text."""
        # Konwertuj na binarny
        binary = ''.join(format(ord(c), '08b') for c in secret_text)

        # Zakoduj jako znaki zerowej szerokości
        zw_message = ""
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            for bit in byte:
                zw_message += self.ZWSP if bit == '0' else self.ZWNJ
            zw_message += self.ZWJ

        # Wstaw po pierwszym słowie
        words = cover_text.split(' ', 1)
        if len(words) > 1:
            return words[0] + zw_message + ' ' + words[1]
        return cover_text + zw_message


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

    def text_to_binary(self, text):
        """Konwertuj tekst na binarny."""
        return ''.join(format(ord(c), '08b') for c in text)

    def encode(self, cover_text, secret_text):
        """Ukryj secret_text w cover_text używając FSM."""
        secret_binary = self.text_to_binary(secret_text)

        # Znajdź transformowalne znaki
        transformable = []
        for i, char in enumerate(cover_text):
            if char in self.char_to_category:
                transformable.append((i, char, self.char_to_category[char]))

        if len(transformable) == 0:
            raise ValueError("Tekst przykrywający nie zawiera transformowalnych znaków!")

        if len(secret_binary) >= len(transformable):
            raise ValueError(
                f"Wiadomość za długa! Potrzeba {len(secret_binary)} znaków, "
                f"dostępne: {len(transformable)}"
            )

        # FSM encoding
        current_category = transformable[0][2]
        transform_positions = [transformable[0][0]]
        used_indices = [0]

        for bit in secret_binary:
            found = False
            for search_idx in range(used_indices[-1] + 1, len(transformable)):
                _, _, symbol_category = transformable[search_idx]

                if bit == '0' and symbol_category == current_category:
                    transform_positions.append(transformable[search_idx][0])
                    used_indices.append(search_idx)
                    found = True
                    break
                elif bit == '1' and symbol_category != current_category:
                    transform_positions.append(transformable[search_idx][0])
                    used_indices.append(search_idx)
                    current_category = symbol_category
                    found = True
                    break

            if not found:
                raise ValueError("Za mało odpowiednich znaków w tekście!")

        # Transformuj (uppercase)
        stego_chars = list(cover_text)
        for pos in transform_positions:
            stego_chars[pos] = stego_chars[pos].upper()

        return ''.join(stego_chars)


def main():
    parser = argparse.ArgumentParser(
        description='Ukryj tajną wiadomość w pliku tekstowym',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  # Metoda zero-width (uniwersalna, niewidoczna)
  python encode.py -c cover.txt -s "Tajne" -o stego.txt
  python encode.py -c cover.txt -sf secret.txt -o stego.txt -m zero-width

  # Metoda feature-coding (dla tekstu z odpowiednimi znakami)
  python encode.py -c cover.txt -s "Hi" -o stego.txt -m feature-coding

Metody:
  zero-width    - Używa niewidocznych znaków Unicode (działa z każdym tekstem)
  feature-coding - Używa transformacji znaków (wymaga odpowiednich znaków)
        """
    )

    parser.add_argument('-o', '--output', required=True,
                       help='Plik wyjściowy ze stego-tekstem')
    parser.add_argument('-m', '--method', 
                       choices=['zero-width', 'feature-coding'],
                       default='zero-width',
                       help='Metoda steganografii (domyślnie: zero-width)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Pokaż szczegółowe informacje')

    args = parser.parse_args()

    try:
        cover_text = """Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod 
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim 
veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 
commodo consequat. Duis aute irure dolor in reprehenderit in voluptate 
velit esse cillum dolore eu fugiat nulla pariatur.

Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia 
deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste 
natus error sit voluptatem accusantium doloremque laudantium totam rem 
aperiam eaque ipsa quae ab illo inventore veritatis et quasi architecto 
beatae vitae dicta sunt explicabo."""

        secret_text = input("Podaj tajną wiadomość: ")
        
        print(f"📄 Tekst przykrywający: {len(cover_text)} znaków")
        print(f"🔒 Tajna wiadomość: {len(secret_text)} znaków")
        print(f"🔧 Metoda: {args.method}")

        # Kodowanie
        if args.method == 'zero-width':
            stego_system = ZeroWidthSteganography()
            stego_text = stego_system.encode(cover_text, secret_text)
        else:  # feature-coding
            stego_system = FeatureCodingSteganography()
            stego_text = stego_system.encode(cover_text, secret_text)

        # Zapisz wynik
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stego_text)

        if args.verbose:
            print(f"\n✅ Sukces!")
            print(f"📁 Zapisano stego-tekst do: {args.output}")
            print(f"📊 Długość: {len(stego_text)} znaków")
            print(f"   Różnica: +{len(stego_text) - len(cover_text)} znaków")
        else:
            print(f"✅ Zakodowano wiadomość do pliku: {args.output}")

    except ValueError as e:
        print(f"❌ Błąd: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
