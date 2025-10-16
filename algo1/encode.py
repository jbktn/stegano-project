def to_bits(data: bytes) -> str:
    return ''.join(f'{b:08b}' for b in data)

def int_to_32bits(n: int) -> str:
    return f'{n:032b}'

def encode_html(output_html: str, cover_lines, message: str):
    msg_bytes = message.encode('utf-8')
    length_bits = int_to_32bits(len(msg_bytes))
    payload_bits = length_bits + to_bits(msg_bytes)

    if len(cover_lines) < len(payload_bits):
        raise ValueError(f"Potrzeba co najmniej {len(payload_bits)} linii w coverze.")

    html_lines = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'><title>Stego HTML</title></head><body style='font-family: monospace; line-height: 1.5;'>"
    ]

    shift_amount = 4  # przesunięcie dla bitu 1

    for i, line in enumerate(cover_lines):
        bit = payload_bits[i] if i < len(payload_bits) else '0'
        top_shift = shift_amount if bit == '1' else 0
        html_lines.append(f"<div style='position: relative; top: {top_shift}px;'>{line}</div>")

    html_lines.append("</body></html>")

    with open(output_html, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"Zapisano HTML: {output_html}")
    print(f"Ukryta wiadomość: {message!r}")
    print(f"Użyto {len(payload_bits)} linii.")

if __name__ == "__main__":
    lines = [f"Line {i+1}" for i in range(2000)]
    secret = "Ukryta wiadomosc w html"
    encode_html("stego.html", lines, secret)
