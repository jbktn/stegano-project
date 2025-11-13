import sys
import math
import os

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
    """
    Znajdź zestaw emotikonów, do którego należy dana emotikona.
    Zwraca: (set_name, index, n_bits) lub (None, None, None)
    """
    for set_name, emoticon_list in EMOTICON_SETS.items():
        if emoticon in emoticon_list:
            index = emoticon_list.index(emoticon)
            N = len(emoticon_list)
            n = math.floor(math.log2(N))
            return set_name, index, n
    return None, None, None

def extract_bits_from_sentence(stego_sentence):
    """
    Wyciągnij ukryte bity z zdania stego.
    Zwraca: (extracted_bits, emoticon, set_name) lub None
    """
    # Znajdź wszystkie emotikony w zdaniu
    emoticons_found = []
    for emoticon_set in EMOTICON_SETS.values():
        for emoticon in emoticon_set:
            if emoticon in stego_sentence:
                emoticons_found.append(emoticon)

    if not emoticons_found:
        return None

    # Przetwórz pierwszą znalezioną emotikonę
    emoticon = emoticons_found[0]

    # Znajdź info o emotikonie
    set_name, index, n = find_emoticon_info(emoticon)

    if set_name is None:
        return None

    # Wyciągnij n bitów z pozycji emotikony w secie
    emoticon_bits = decimal_to_bits(index, n)

    # Wyciągnij bit pozycji (0=start, 1=end)
    if stego_sentence.strip().startswith(emoticon):
        position_bit = '0'
    else:
        position_bit = '1'

    # Wyciągnij bit interpunkcji (0=with comma, 1=without)
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
    # Upewnij się że długość jest wielokrotnością 8
    padding = len(binary_string) % 8
    if padding != 0:
        binary_string = binary_string[:len(binary_string) - padding]

    text = ''
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i+8]
        if len(byte) == 8:
            char_code = int(byte, 2)
            if 32 <= char_code <= 126:  # Drukowane ASCII
                text += chr(char_code)

    return text

def decode_messages(stego_sentences):
    """
    Zdekoduj wszystkie stego zdania i wyciągnij ukrytą wiadomość.
    """
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
            print(f"  Emoticon: {emoticon} (from '{set_name}' set)")
            print(f"  Extracted bits: {bits} ({len(bits)} bits)")
        else:
            print(f"\nMessage {i}: {sentence}")
            print(f"  No emoticon found!")

    print(f"\n{'=' * 60}")
    print(f"Total bits extracted: {len(all_bits)}")
    print(f"Binary: {all_bits}")
    print(f"{'=' * 60}\n")

    # Konwertuj na tekst
    decoded_text = binary_to_text(all_bits)

    return decoded_text, all_bits

def main():
    # Parametry
    if len(sys.argv) >= 2:
        stego_file = sys.argv[1]
    else:
        stego_file = 'stego_output.txt'

    # Wczytaj stego sentences
    if not os.path.exists(stego_file):
        print(f"Error: Stego file '{stego_file}' not found!")
        print(f"\nUsage: python decode.py [stego_file]")
        print(f"Default: python decode.py (uses stego_output.txt)")
        sys.exit(1)

    with open(stego_file, 'r', encoding='utf-8') as f:
        stego_sentences = [line.strip() for line in f if line.strip()]

    print(f"\n{'=' * 60}")
    print("STEGANOGRAPHY DECODER (Batch-optimized)")
    print(f"{'=' * 60}")
    print(f"\nReading from file: {stego_file}")
    print(f"Received {len(stego_sentences)} stego sentence(s)")
    print(f"Emoticon sets: 4 categories × 16 emoticons each = 64 total")

    # Dekoduj wiadomości
    decoded_text, all_bits = decode_messages(stego_sentences)

    print("=" * 60)
    print("DECODED SECRET MESSAGE:")
    print("=" * 60)
    print(f"Text: {decoded_text}")
    print(f"Binary: {all_bits}")
    print("=" * 60)

if __name__ == "__main__":
    main()
