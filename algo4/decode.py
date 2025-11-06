def sum_of_squares_of_digits(r: int) -> int:
    return sum((int(d)**2) for d in str(r))

def decipher_one_time_pad(ciphertext: bytes, key: bytes) -> bytes:
    if len(ciphertext) != len(key):
        raise ValueError("Ciphertext and key lengths differ.")
    plain = []
    for e, r in zip(ciphertext, key):
        s = sum_of_squares_of_digits(r)
        x = s // 10
        y = s % 10
        n = (e - r + (x*y)) % 256
        plain.append(n)
    return bytes(plain)

if __name__ == "__main__":
    # Load files
    with open("stego_text.txt", "r", encoding="utf-8") as f:
        stego_text = f.read()
    with open("key.bin", "rb") as f:
        data = f.read()

    otp_len = int.from_bytes(data[:4], "big")
    otp_key = data[4:4+otp_len]
    cipher = data[4+otp_len:]

    # Decrypt
    plaintext_bytes = decipher_one_time_pad(cipher, otp_key)
    try:
        message = plaintext_bytes.decode("utf-8")
    except UnicodeDecodeError:
        message = plaintext_bytes.decode("utf-8", errors="replace")

    print("\n✅ Message successfully recovered!")
    print("📜 UTF-8 decoded text:\n")
    print(message)
