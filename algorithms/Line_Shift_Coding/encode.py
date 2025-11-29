import argparse
import sys

def tobits(data: bytes) -> str:
    return ''.join(f"{b:08b}" for b in data)

def intto32bits(n: int) -> str:
    return f"{n:032b}"

def encodehtml(outputhtml: str, coverlines, message: str):
    msgbytes = message.encode("utf-8")
    lengthbits = intto32bits(len(msgbytes))
    payloadbits = lengthbits + tobits(msgbytes)
    if len(coverlines) < len(payloadbits):
        raise ValueError(f"Potrzeba co najmniej {len(payloadbits)} linii w coverze.")
    htmllines = ['<!DOCTYPE html>', '<html><head><meta charset="utf-8"><title>Stego HTML</title></head><body style="font-family: monospace; line-height: 1.5;">']
    shiftamount = 4  # przesunięcie dla bitu 1
    for i, line in enumerate(coverlines):
        bit = int(payloadbits[i]) if i < len(payloadbits) else 0
        topshift = shiftamount if bit == 1 else 0
        htmllines.append(f'<div style="position:relative;top:{topshift}px;">{line.rstrip()}</div>')
    htmllines.append('</body></html>')
    with open(outputhtml, "w", encoding="utf-8") as f:
        f.write('\n'.join(htmllines))
    print(f"Zapisano HTML {outputhtml}")
    print(f"Ukryta wiadomość: {message!r}")
    print(f"Użyto {len(payloadbits)} linii.")

def read_cover_lines(args):
    if args.ic:
        # Zamień \n na przejścia linii jeśli podano jeden string z wejścia
        return args.ic.split("\\n") if "\\n" in args.ic else args.ic.split("\n")
    if args.fc:
        with open(args.fc, "r", encoding="utf-8") as f: return f.readlines()
    raise ValueError("Podaj źródło covera przez -ic lub -fc")

def read_secret(args):
    if args.is_: return args.is_
    if args.fs:
        with open(args.fs, "r", encoding="utf-8") as f: return f.read().strip()
    raise ValueError("Podaj secret przez -is lub -fs")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group_cover = parser.add_mutually_exclusive_group(required=True)
    group_cover.add_argument('-ic', type=str, help="Cover text (input)")
    group_cover.add_argument('-fc', type=str, help="Cover file")
    group_secret = parser.add_mutually_exclusive_group(required=True)
    group_secret.add_argument('-is', dest='is_', type=str, help="Secret message (input)")
    group_secret.add_argument('-fs', type=str, help="Secret file")
    parser.add_argument('-o', type=str, default="stego.html", help="Output HTML file")
    args = parser.parse_args()
    cover_lines = read_cover_lines(args)
    secret = read_secret(args)
    encodehtml(args.o, cover_lines, secret)

