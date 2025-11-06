#!/usr/bin/env python3
"""
Emoticon-based Text Steganography - Decoding
Based on Wang et al. (2009) algorithm
Reads stego sentences from stego_output.txt or specified file
"""

import sys
import math
import os

# Pre-defined emoticon sets (must match encoder)
EMOTICON_SETS = {
    'smile': ['😊', '😀', '🙂', '😄', '😁', '😃', '😆', '😅'],
    'laugh': ['😂', '🤣', '😹', '😸'],
    'cry': ['😢', '😭', '😿', '😥', '😰', '😓', '😪', '😫'],
    'love': ['😍', '😘', '😻', '💖', '💕', '💓', '❤️', '💗'],
    'angry': ['😠', '😡', '👿', '😤'],
    'sad': ['😔', '😞', '😟', '🙁', '☹️', '😕'],
    'surprise': ['😮', '😲', '😯', '😦', '😧', '😨'],
    'cool': ['😎', '🕶️', '😏', '🤓']
}

def decimal_to_bits(d, n):
    """Convert decimal to binary string of length n"""
    return format(d, f'0{n}b')

def find_emoticon_info(emoticon):
    """
    Find emoticon in sets and return its info

    Returns:
        (set_name, index, bits_capacity) or (None, None, None)
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
    Extract secret bits from a stego sentence

    Args:
        stego_sentence: Sentence with embedded emoticon

    Returns:
        Binary string of extracted bits
    """
    # Find all emoticons in the sentence
    emoticons_found = []
    for emoticon_set in EMOTICON_SETS.values():
        for emoticon in emoticon_set:
            if emoticon in stego_sentence:
                emoticons_found.append(emoticon)

    if not emoticons_found:
        return None

    # For simplicity, process first emoticon found
    emoticon = emoticons_found[0]

    # Find emoticon info
    set_name, index, n = find_emoticon_info(emoticon)

    if set_name is None:
        return None

    # Extract n bits from emoticon position in set
    emoticon_bits = decimal_to_bits(index, n)

    # Extract position bit (0=start, 1=end)
    if stego_sentence.strip().startswith(emoticon):
        position_bit = '0'
    else:
        position_bit = '1'

    # Extract punctuation bit (0=with comma, 1=without)
    # Check if there's a comma near the emoticon
    if ',' in stego_sentence:
        # Check if comma is adjacent to emoticon
        if f'{emoticon},' in stego_sentence or f',{emoticon}' in stego_sentence or f', {emoticon}' in stego_sentence or f'{emoticon} ,' in stego_sentence:
            punct_bit = '0'
        else:
            punct_bit = '1'
    else:
        punct_bit = '1'

    extracted_bits = emoticon_bits + position_bit + punct_bit

    return extracted_bits, emoticon, set_name

def binary_to_text(binary_string):
    """Convert binary string to text"""
    # Ensure length is multiple of 8
    padding = len(binary_string) % 8
    if padding != 0:
        binary_string = binary_string[:len(binary_string) - padding]

    text = ''
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i+8]
        if len(byte) == 8:
            char_code = int(byte, 2)
            if 32 <= char_code <= 126:  # Printable ASCII
                text += chr(char_code)

    return text

def decode_messages(stego_sentences):
    """
    Decode multiple stego sentences

    Args:
        stego_sentences: List of stego sentences

    Returns:
        Decoded secret message
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

    # Convert to text
    decoded_text = binary_to_text(all_bits)

    return decoded_text, all_bits

def main():
    # Check if file is provided as argument
    if len(sys.argv) >= 2:
        stego_file = sys.argv[1]
    else:
        # Default file name
        stego_file = 'stego_output.txt'

    # Read stego sentences from file
    if not os.path.exists(stego_file):
        print(f"Error: Stego file '{stego_file}' not found!")
        print(f"\nUsage: python decode.py [stego_file]")
        print(f"Default: python decode.py (uses stego_output.txt)")
        sys.exit(1)

    with open(stego_file, 'r', encoding='utf-8') as f:
        stego_sentences = [line.strip() for line in f if line.strip()]

    print(f"\nReading from file: {stego_file}")
    print(f"Received {len(stego_sentences)} stego sentence(s)")

    # Decode messages
    decoded_text, all_bits = decode_messages(stego_sentences)

    print("=" * 60)
    print("DECODED SECRET MESSAGE:")
    print("=" * 60)
    print(f"Text: {decoded_text}")
    print(f"Binary: {all_bits}")
    print("=" * 60)

if __name__ == "__main__":
    main()
