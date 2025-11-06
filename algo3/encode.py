#!/usr/bin/env python3
"""
Emoticon-based Text Steganography - Encoding
Based on Wang et al. (2009) algorithm
Reads cover text from cover.txt (multiple lines) and secret message from secret.txt
Each line in cover.txt is treated as a separate chat message
"""

import sys
import math
import os

# Pre-defined emoticon sets (can be customized)
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

def bits_to_decimal(bits):
    """Convert binary string to decimal"""
    return int(bits, 2)

def text_to_binary(text):
    """Convert text to binary representation"""
    binary = ''
    for char in text:
        binary += format(ord(char), '08b')
    return binary

def create_stego_sentences(cover_sentences, secret_bits):
    """
    Create steganographic sentences with embedded emoticons
    Uses different cover sentences from the list

    Args:
        cover_sentences: List of cover sentences (chat messages)
        secret_bits: Binary string to embed

    Returns:
        List of stego sentences with emoticons
    """
    emoticon_set_names = list(EMOTICON_SETS.keys())

    results = []
    bit_index = 0
    cover_index = 0

    while bit_index < len(secret_bits):
        # Get current cover sentence (cycle through if we run out)
        current_cover = cover_sentences[cover_index % len(cover_sentences)]
        cover_index += 1

        # Determine which set to use (rotate through sets)
        set_idx = (bit_index // 4) % len(emoticon_set_names)
        emoticon_set_name = emoticon_set_names[set_idx]

        emoticon_set = EMOTICON_SETS[emoticon_set_name]
        N = len(emoticon_set)
        n = math.floor(math.log2(N))

        # Check if we have enough bits left
        bits_needed = n + 2  # n bits for emoticon, 1 for position, 1 for punctuation
        if bit_index + bits_needed > len(secret_bits):
            # Pad with zeros if needed
            remaining = secret_bits[bit_index:]
            secret_bits += '0' * (bits_needed - len(remaining))

        # Extract bits
        emoticon_bits = secret_bits[bit_index:bit_index+n]
        position_bit = secret_bits[bit_index+n] if bit_index+n < len(secret_bits) else '0'
        punct_bit = secret_bits[bit_index+n+1] if bit_index+n+1 < len(secret_bits) else '0'

        # Select emoticon
        d = bits_to_decimal(emoticon_bits)
        if d >= N:
            d = N - 1
        emoticon = emoticon_set[d]

        # Determine position (0=start, 1=end)
        position = 'end' if position_bit == '1' else 'start'

        # Determine punctuation (0=with comma, 1=without)
        punctuation = '' if punct_bit == '1' else ','

        # Build stego sentence
        if position == 'start':
            stego = f"{emoticon}{punctuation} {current_cover}"
        else:
            stego = f"{current_cover} {punctuation}{emoticon}"

        results.append({
            'sentence': stego,
            'bits_embedded': emoticon_bits + position_bit + punct_bit,
            'bits_count': len(emoticon_bits + position_bit + punct_bit),
            'emoticon': emoticon,
            'set': emoticon_set_name,
            'cover_used': current_cover
        })

        bit_index += bits_needed

    return results

def main():
    # Check if files are provided as arguments
    if len(sys.argv) >= 3:
        cover_file = sys.argv[1]
        secret_file = sys.argv[2]
    else:
        # Default file names
        cover_file = 'cover.txt'
        secret_file = 'secret.txt'

    # Read cover sentences from file (one per line)
    if not os.path.exists(cover_file):
        print(f"Error: Cover file '{cover_file}' not found!")
        print(f"\nUsage: python encode.py [cover_file] [secret_file]")
        print(f"Default: python encode.py (uses cover.txt and secret.txt)")
        sys.exit(1)

    with open(cover_file, 'r', encoding='utf-8') as f:
        cover_sentences = [line.strip() for line in f if line.strip()]

    if not cover_sentences:
        print(f"Error: Cover file '{cover_file}' is empty!")
        sys.exit(1)

    # Read secret message from file
    if not os.path.exists(secret_file):
        print(f"Error: Secret file '{secret_file}' not found!")
        print(f"\nUsage: python encode.py [cover_file] [secret_file]")
        print(f"Default: python encode.py (uses cover.txt and secret.txt)")
        sys.exit(1)

    with open(secret_file, 'r', encoding='utf-8') as f:
        secret_message = f.read().strip()

    # Convert secret message to binary
    secret_bits = text_to_binary(secret_message)

    print(f"\nCover sentences (from {cover_file}): {len(cover_sentences)} messages")
    for i, sentence in enumerate(cover_sentences, 1):
        print(f"  {i}. {sentence}")
    print(f"\nSecret message (from {secret_file}): {secret_message}")
    print(f"Secret in binary: {secret_bits}")
    print(f"Total bits to embed: {len(secret_bits)}\n")

    # Create stego sentences
    results = create_stego_sentences(cover_sentences, secret_bits)

    print("=" * 60)
    print("STEGO SENTENCES (CHAT MESSAGES):")
    print("=" * 60)

    # Save stego sentences to output file
    with open('stego_output.txt', 'w', encoding='utf-8') as f:
        for i, result in enumerate(results, 1):
            print(f"\nMessage {i}:")
            print(f"  Original: {result['cover_used']}")
            print(f"  Stego:    {result['sentence']}")
            print(f"  Emoticon: {result['emoticon']} (from '{result['set']}' set)")
            print(f"  Bits:     {result['bits_embedded']} ({result['bits_count']} bits)")

            # Write to file
            f.write(result['sentence'] + '\n')

    print(f"\n{'=' * 60}")
    print(f"Total messages created: {len(results)}")
    print(f"Stego sentences saved to: stego_output.txt")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
