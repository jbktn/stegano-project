import sys
import argparse
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
            if char in self.char_to_category:
                category = self.char_to_category[char]
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


def main():
    parser = argparse.ArgumentParser(description='Feature Coding Steganography - Encoder')

    parser.add_argument('-c', '--cover', required=True, help='Cover text file')
    parser.add_argument('-s', '--secret', help='Secret message (text)')
    parser.add_argument('-sf', '--secret-file', help='Secret message file')
    parser.add_argument('-o', '--output', required=True, help='Output stego file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not args.secret and not args.secret_file:
        parser.error("Provide -s SECRET or -sf FILE")

    if args.secret and args.secret_file:
        parser.error("Provide only -s or -sf, not both")

    try:
        cover_path = Path(args.cover)
        if not cover_path.exists():
            print(f"Error: File '{args.cover}' not found!", file=sys.stderr)
            sys.exit(1)

        with open(cover_path, 'r', encoding='utf-8') as f:
            cover_text = f.read().strip()

        if not cover_text:
            print("Error: Cover file is empty!", file=sys.stderr)
            sys.exit(1)

        if args.secret:
            secret_text = args.secret
        else:
            secret_path = Path(args.secret_file)
            if not secret_path.exists():
                print(f"Error: File '{args.secret_file}' not found!", file=sys.stderr)
                sys.exit(1)

            with open(secret_path, 'r', encoding='utf-8') as f:
                secret_text = f.read().strip()

        if not secret_text:
            print("Error: Secret message is empty!", file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(f"Cover text: {len(cover_text)} chars")
            print(f"Secret: '{secret_text}' ({len(secret_text)} chars)")

        stego = FeatureCodingSteganography()
        secret_binary = text_to_binary(secret_text)

        if args.verbose:
            print(f"Binary: {len(secret_binary)} bits")
            transformable = stego.find_transformable(cover_text)
            print(f"Transformable chars: {len(transformable)}")

        stego_text = stego.encode(cover_text, secret_binary)

        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stego_text)

        if args.verbose:
            print(f"\nEncoded successfully!")
            print(f"Output: {args.output}")
        else:
            print(f"Encoded to: {args.output}")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
