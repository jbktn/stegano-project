import argparse
import sys
import math
import os
from pathlib import Path

# Optimized 4-category emoticon sets - EXACTLY 16 emoticons each (must match encoder)
EMOTICON_SETS = {
    'happy': [
        '😊', '😀', '😃', '😄', '😁', '🙂', '😍', '🥰',
        '😘', '😇', '🤗', '😌', '☺️', '🥳', '💖', '❤️'
    ],
    'sad': [
        '😢', '😭', '😔', '😞', '😟', '🙁', '☹️', '😕',
        '😥', '😰', '😓', '😪', '😫', '🥺', '💔', '😿'
    ],
    'funny': [
        '😂', '🤣', '😆', '😅', '😹', '😸', '🤪', '😜',
        '😝', '😛', '🙃', '😋', '🤭', '🤡', '👻', '🤠'
    ],
    'angry': [
        '😠', '😡', '🤬', '😤', '👿', '😾', '💢', '😖',
        '😣', '😩', '😫', '🤯', '😒', '🙄', '😑', '😬'
    ]
}

def decimal_to_bits(d, n):
    """Konwertuj liczbę na binarny string o długości n."""
    return format(d, f'0{n}b')

def find_emoticon_info(emoticon):
    """Znajdź zestaw emotikonów, do którego należy dana emotikona."""
    for set_name, emoticon_list in EMOTICON_SETS.items():
        if emoticon in emoticon_list:
            index = emoticon_list.index(emoticon)
            N = len(emoticon_list)
            n = math.floor(math.log2(N))
            return set_name, index, n
    return None, None, None

def extract_bits_from_sentence(stego_sentence):
    """Wyciągnij ukryte bity z zdania stego."""
    emoticons_found = []
    for emoticon_set in EMOTICON_SETS.values():
        for emoticon in emoticon_set:
            if emoticon in stego_sentence:
                emoticons_found.append(emoticon)

    if not emoticons_found:
        return None

    emoticon = emoticons_found[0]
    set_name, index, n = find_emoticon_info(emoticon)

    if set_name is None:
        return None

    emoticon_bits = decimal_to_bits(index, n)

    if stego_sentence.strip().startswith(emoticon):
        position_bit = '0'
    else:
        position_bit = '1'

    if ',' in stego_sentence:
        if f'{emoticon},' in stego_sentence or f',{emoticon}' in stego_sentence or \
           f', {emoticon}' in stego_sentence or f'{emoticon} ,' in stego_sentence:
            punct_bit = '0'
        else:
            punct_bit = '1'
    else:
        punct_bit = '1'

    extracted_bits = emoticon_bits + position_bit + punct_bit
    return extracted_bits, emoticon, set_name

def binary_to_text(binary_string):
    """Konwertuj binary string na tekst (ASCII)."""
    padding = len(binary_string) % 8
    if padding != 0:
        binary_string = binary_string[:len(binary_string) - padding]

    text = ''
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i+8]
        if len(byte) == 8:
            char_code = int(byte, 2)
            if 32 <= char_code <= 126:
                text += chr(char_code)

    return text

def decode_messages(stego_sentences):
    """Zdekoduj wszystkie stego zdania i wyciągnij ukrytą wiadomość."""
    all_bits = ""

    print("\n" + "=" * 60)
    print("EXTRACTING BITS FROM STEGO SENTENCES:")
    print("=" * 60)

    for i, sentence in enumerate(stego_sentences, 1):
        result = extract_bits_from_sentence(sentence)
        if result:
            bits, emoticon, set_name = result
            all_bits += bits
            print(f"\nMessage {i}: {sentence}")
            print(f" Emoticon: {emoticon} (from '{set_name}' set)")
            print(f" Extracted bits: {bits} ({len(bits)} bits)")
        else:
            print(f"\nMessage {i}: {sentence}")
            print(f" No emoticon found!")

    print(f"\n{'=' * 60}")
    print(f"Total bits extracted: {len(all_bits)}")
    print(f"Binary: {all_bits}")
    print(f"{'=' * 60}\n")

    decoded_text = binary_to_text(all_bits)
    return decoded_text, all_bits

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dekoduj tajną wiadomość z stego pliku")
    parser.add_argument('input_file', type=str, help="Ścieżka do pliku stego")
    parser.add_argument('-o', dest='out_file', type=str, default=None, help="Plik wyjściowy (opcjonalnie)")

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"❌ Błąd: plik nie znaleziony: {args.input_file}")
        sys.exit(1)

    with open(args.input_file, 'r', encoding='utf-8') as f:
        stego_sentences = [line.strip() for line in f if line.strip()]

    print(f"\n{'=' * 60}")
    print("STEGANOGRAPHY DECODER (Batch-optimized)")
    print(f"{'=' * 60}")
    print(f"\nReading from file: {args.input_file}")
    print(f"Received {len(stego_sentences)} stego sentence(s)")
    print(f"Emoticon sets: 4 categories × 16 emoticons each = 64 total")

    decoded_text, all_bits = decode_messages(stego_sentences)

    print("=" * 60)
    print("DECODED SECRET MESSAGE:")
    print("=" * 60)
    print(f"Text: {decoded_text}")
    print(f"Binary: {all_bits}")
    print("=" * 60)

    if args.out_file:
        Path(args.out_file).write_text(decoded_text, encoding='utf-8')
        print(f"✓ Zapisano do pliku: {args.out_file}")

