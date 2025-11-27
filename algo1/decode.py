import argparse
from pathlib import Path
from bs4 import BeautifulSoup

def bits_to_bytes(bitstring: str) -> bytes:
    return bytes(int(bitstring[i:i+8], 2) for i in range(0, len(bitstring), 8))

def decode_html(input_html: str, threshold=2.0):
    """Dekoduje tajną wiadomość z HTML (przesunięcie pozycji)."""
    try:
        with open(input_html, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except FileNotFoundError:
        print(f"❌ Błąd: plik nie znaleziony: {input_html}")
        exit(1)
    
    divs = soup.find_all("div")
    bits = []
    
    for div in divs:
        style = div.get("style", "")
        top_val = 0
        if "top:" in style:
            try:
                top_val = float(style.split("top:")[1].split("px")[0])
            except Exception:
                pass
        bit = '1' if top_val > threshold else '0'
        bits.append(bit)
    
    bitstring = ''.join(bits)
    length_bits = bitstring[:32]
    msg_len = int(length_bits, 2)
    total_bits = 32 + msg_len * 8
    msg_bits = bitstring[32:total_bits]
    msg_bytes = bits_to_bytes(msg_bits)
    message = msg_bytes.decode('utf-8', errors='replace')
    
    print(f"✓ Odkodowana wiadomość: {message!r}")
    return message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dekoduj tajną wiadomość z HTML (algorytm 1 - shift)")
    parser.add_argument('input_html', type=str, help="Ścieżka do pliku HTML do dekodowania")
    parser.add_argument('-o', dest='out_file', type=str, default=None, help="Plik wyjściowy (opcjonalnie)")
    
    args = parser.parse_args()
    
    message = decode_html(args.input_html)
    
    if args.out_file:
        Path(args.out_file).write_text(message, encoding='utf-8')
        print(f"✓ Zapisano do pliku: {args.out_file}")

