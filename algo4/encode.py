#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed Missing-Letter Steganography Encoder
Encodes actual ciphertext values in '?' pattern and saves combined key.
"""

import random

def sum_of_squares_of_digits(r: int) -> int:
    return sum((int(d)**2) for d in str(r))

def encipher_one_time_pad(plaintext: bytes, rng_seed=None):
    """Encrypt plaintext with one-time pad per the paper."""
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
    """Hide ciphertext bytes by replacing letters with '?'."""
    if rng_seed is not None:
        random.seed(rng_seed)
    words = cover_text.split()
    new_words = []
    w_index = 0

    # one '?' per ciphertext byte
    for b in ciphertext:
        if w_index >= len(words):
            raise ValueError("Not enough words in cover text.")
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

# --- Shakespeare text cover
SHAKESPEARE_SONNET_18 = """Shall I compare thee to a summer’s day?
Thou art more lovely and more temperate:
Rough winds do shake the darling buds of May,
And summer’s lease hath all too short a date:
Sometime too hot the eye of heaven shines,
And often is his gold complexion dimm'd;
And every fair from fair sometime declines,
By chance or nature’s changing course untrimm'd;
But thy eternal summer shall not fade,
Nor lose possession of that fair thou ow’st;
Nor shall Death brag thou wanderest in his shade,
When in eternal lines to time thou grow’st:
So long as men can breathe or eyes can see,
So long lives this, and this gives life to thee."""

if __name__ == "__main__":
    secret_message = input("Enter your secret message: ").encode("utf-8")

    cipher, otp_key = encipher_one_time_pad(secret_message, rng_seed=42)
    stego_text = missing_letter_hide(cipher, SHAKESPEARE_SONNET_18, rng_seed=123)

    # Save cover text
    with open("stego_text.txt", "w", encoding="utf-8") as f:
        f.write(stego_text)

    # Combine key + ciphertext into one file
    with open("key.bin", "wb") as f:
        f.write(len(otp_key).to_bytes(4, "big"))
        f.write(otp_key)
        f.write(cipher)

    print("\n✅ Saved 'stego_text.txt' and 'key.bin'")
    print("Preview:\n")
    print(stego_text[:400])
