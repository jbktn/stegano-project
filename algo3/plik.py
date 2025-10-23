import textwrap

class WhiteSteg:
    """
    Implementacja algorytmu WhiteSteg:
    ukrywanie informacji poprzez manipulację białymi znakami między słowami i akapitami.
    """

    def __init__(self):
        self.cover_sources = [
            "Twinkle twinkle little star how I wonder what you are",
            "Baa baa black sheep have you any wool",
            "Mary had a little lamb whose fleece was white as snow",
            "Jack and Jill went up the hill to fetch a pail of water",
        ]

    def _generate_cover_text(self, secret_len_bytes: int) -> str:
        """Generuje przykładowy cover-text zgodnie z tabelą z artykułu."""
        capacity_map = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
        for cap in capacity_map:
            if secret_len_bytes < cap:
                chosen_len = cap
                break
        base_text = " ".join(self.cover_sources)
        repeat_factor = (chosen_len * 2) // len(base_text.split()) + 1
        cover = (" ".join(self.cover_sources) + " ") * repeat_factor
        return cover.strip()

    def _text_to_bits(self, text: str) -> str:
        """Konwertuje tekst na binarny ciąg (8 bitów na znak)."""
        return ''.join(format(ord(c), '08b') for c in text)

    def _bits_to_text(self, bits: str) -> str:
        """Konwertuje ciąg bitów na tekst."""
        chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
        return ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)

    def encode(self, secret_text: str, cover_text: str = None) -> str:
        """Ukrywa wiadomość w białych znakach."""
        if not cover_text:
            cover_text = self._generate_cover_text(len(secret_text))

        bits = self._text_to_bits(secret_text)
        words = cover_text.split(" ")

        if len(words) - 1 < len(bits):
            raise ValueError("Cover text is too short to hide this message.")

        stego_words = []
        for i, word in enumerate(words[:-1]):
            stego_words.append(word)
            if i < len(bits):
                stego_words.append(" " if bits[i] == '0' else "  ")
            else:
                stego_words.append(" ")
        stego_words.append(words[-1])

        stego_text = "".join(stego_words)
        return stego_text

    def decode(self, stego_text: str) -> str:
        """Odczytuje ukrytą wiadomość z tekstu."""
        bits = []
        segments = stego_text.split(" ")
        i = 0
        while i < len(segments) - 1:
            space_count = 0
            while i + 1 < len(segments) and segments[i + 1] == "":
                space_count += 1
                i += 1
            if space_count == 0:
                bits.append('0')
            elif space_count == 1:
                bits.append('1')
            i += 1

        bit_str = ''.join(bits)
        text = self._bits_to_text(bit_str)
        return text.strip("\x00")  # usuń ewentualne puste bajty

if __name__ == "__main__":
    steg = WhiteSteg()
    secret = "Siema"
    cover = "Mary had a little lamb whose fleece was white as snowMary had a little lamb whose fleece was white as snowMary had a little lamb whose fleece was white as snowMary had a little lamb whose fleece was white as snowMary had a little lamb whose fleece was white as snowMary had a little lamb whose fleece was white as snowMary had a little lamb whose fleece was white as snowMary had a little lamb whose fleece was white as snowMary had a little lamb whose fleece was white as snow"

    stego = steg.encode(secret, cover)
    print("Stego-text:")
    print(repr(stego))  # Użyj repr(), żeby zobaczyć spacje

    decoded = steg.decode(stego)
    print("\nDecoded secret:", decoded)
