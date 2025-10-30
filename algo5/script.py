
# Utworzę dwa proste skrypty CLI: encode.py i decode.py

# ==================== ENCODE.PY ====================
encode_script = '''#!/usr/bin/env python3
"""
encode.py - Ukryj tajną wiadomość w pliku tekstowym

Użycie:
    python encode.py -c cover.txt -s "Tajna wiadomość" -o stego.txt
    python encode.py -c cover.txt -sf secret.txt -o stego.txt
"""

import sys
import argparse
from pathlib import Path


class ZeroWidthSteganography:
    """Steganografia używająca znaków zerowej szerokości Unicode."""
    
    ZWSP = '\\u200B'  # Zero-width space (0)
    ZWNJ = '\\u200C'  # Zero-width non-joiner (1)
    ZWJ = '\\u200D'   # Zero-width joiner (separator)
    
    def encode(self, cover_text, secret_text):
        """Ukryj secret_text w cover_text."""
        # Konwertuj na binarny
        binary = ''.join(format(ord(c), '08b') for c in secret_text)
        
        # Zakoduj jako znaki zerowej szerokości
        zw_message = ""
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            for bit in byte:
                zw_message += self.ZWSP if bit == '0' else self.ZWNJ
            zw_message += self.ZWJ
        
        # Wstaw po pierwszym słowie
        words = cover_text.split(' ', 1)
        if len(words) > 1:
            return words[0] + zw_message + ' ' + words[1]
        return cover_text + zw_message


class FeatureCodingSteganography:
    """Steganografia oparta na kodowaniu cech."""
    
    def __init__(self):
        self.categories = {
            'CF1': list('aeiouąęóAEIOU'),
            'CF2': list('bcdfghjklmnpqrstvwxyzćłńśźżBCDFGHJKLMNPQRSTVWXYZĆŁŃŚŹŻ'),
        }
        
        self.char_to_category = {}
        for category, chars in self.categories.items():
            for char in chars:
                self.char_to_category[char] = category
    
    def text_to_binary(self, text):
        """Konwertuj tekst na binarny."""
        return ''.join(format(ord(c), '08b') for c in text)
    
    def encode(self, cover_text, secret_text):
        """Ukryj secret_text w cover_text używając FSM."""
        secret_binary = self.text_to_binary(secret_text)
        
        # Znajdź transformowalne znaki
        transformable = []
        for i, char in enumerate(cover_text):
            if char in self.char_to_category:
                transformable.append((i, char, self.char_to_category[char]))
        
        if len(transformable) == 0:
            raise ValueError("Tekst przykrywający nie zawiera transformowalnych znaków!")
        
        if len(secret_binary) >= len(transformable):
            raise ValueError(
                f"Wiadomość za długa! Potrzeba {len(secret_binary)} znaków, "
                f"dostępne: {len(transformable)}"
            )
        
        # FSM encoding
        current_category = transformable[0][2]
        transform_positions = [transformable[0][0]]
        used_indices = [0]
        
        for bit in secret_binary:
            found = False
            for search_idx in range(used_indices[-1] + 1, len(transformable)):
                _, _, symbol_category = transformable[search_idx]
                
                if bit == '0' and symbol_category == current_category:
                    transform_positions.append(transformable[search_idx][0])
                    used_indices.append(search_idx)
                    found = True
                    break
                elif bit == '1' and symbol_category != current_category:
                    transform_positions.append(transformable[search_idx][0])
                    used_indices.append(search_idx)
                    current_category = symbol_category
                    found = True
                    break
            
            if not found:
                raise ValueError("Za mało odpowiednich znaków w tekście!")
        
        # Transformuj (uppercase)
        stego_chars = list(cover_text)
        for pos in transform_positions:
            stego_chars[pos] = stego_chars[pos].upper()
        
        return ''.join(stego_chars)


def main():
    parser = argparse.ArgumentParser(
        description='Ukryj tajną wiadomość w pliku tekstowym',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  # Metoda zero-width (uniwersalna, niewidoczna)
  python encode.py -c cover.txt -s "Tajne" -o stego.txt
  python encode.py -c cover.txt -sf secret.txt -o stego.txt -m zero-width
  
  # Metoda feature-coding (dla tekstu z odpowiednimi znakami)
  python encode.py -c cover.txt -s "Hi" -o stego.txt -m feature-coding

Metody:
  zero-width    - Używa niewidocznych znaków Unicode (działa z każdym tekstem)
  feature-coding - Używa transformacji znaków (wymaga odpowiednich znaków)
        """
    )
    
    parser.add_argument('-c', '--cover', required=True,
                       help='Plik z tekstem przykrywającym')
    parser.add_argument('-s', '--secret', 
                       help='Tajna wiadomość (tekst)')
    parser.add_argument('-sf', '--secret-file',
                       help='Plik z tajną wiadomością')
    parser.add_argument('-o', '--output', required=True,
                       help='Plik wyjściowy ze stego-tekstem')
    parser.add_argument('-m', '--method', 
                       choices=['zero-width', 'feature-coding'],
                       default='zero-width',
                       help='Metoda steganografii (domyślnie: zero-width)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Pokaż szczegółowe informacje')
    
    args = parser.parse_args()
    
    # Walidacja
    if not args.secret and not args.secret_file:
        parser.error("Musisz podać -s WIADOMOŚĆ lub -sf PLIK")
    
    if args.secret and args.secret_file:
        parser.error("Podaj tylko -s lub -sf, nie oba")
    
    try:
        # Wczytaj tekst przykrywający
        cover_path = Path(args.cover)
        if not cover_path.exists():
            print(f"❌ Błąd: Plik '{args.cover}' nie istnieje!", file=sys.stderr)
            sys.exit(1)
        
        with open(cover_path, 'r', encoding='utf-8') as f:
            cover_text = f.read().strip()
        
        if not cover_text:
            print("❌ Błąd: Plik przykrywający jest pusty!", file=sys.stderr)
            sys.exit(1)
        
        # Wczytaj tajną wiadomość
        if args.secret:
            secret_text = args.secret
        else:
            secret_path = Path(args.secret_file)
            if not secret_path.exists():
                print(f"❌ Błąd: Plik '{args.secret_file}' nie istnieje!", file=sys.stderr)
                sys.exit(1)
            
            with open(secret_path, 'r', encoding='utf-8') as f:
                secret_text = f.read().strip()
        
        if not secret_text:
            print("❌ Błąd: Tajna wiadomość jest pusta!", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"📄 Tekst przykrywający: {len(cover_text)} znaków")
            print(f"🔒 Tajna wiadomość: {len(secret_text)} znaków")
            print(f"🔧 Metoda: {args.method}")
        
        # Kodowanie
        if args.method == 'zero-width':
            stego_system = ZeroWidthSteganography()
            stego_text = stego_system.encode(cover_text, secret_text)
        else:  # feature-coding
            stego_system = FeatureCodingSteganography()
            stego_text = stego_system.encode(cover_text, secret_text)
        
        # Zapisz wynik
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stego_text)
        
        if args.verbose:
            print(f"\\n✅ Sukces!")
            print(f"📁 Zapisano stego-tekst do: {args.output}")
            print(f"📊 Długość: {len(stego_text)} znaków")
            print(f"   Różnica: +{len(stego_text) - len(cover_text)} znaków")
        else:
            print(f"✅ Zakodowano wiadomość do pliku: {args.output}")
        
    except ValueError as e:
        print(f"❌ Błąd: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
'''

# Zapisz encode.py
with open('encode.py', 'w', encoding='utf-8') as f:
    f.write(encode_script)

print("✅ Utworzono: encode.py")

# ==================== DECODE.PY ====================
decode_script = '''#!/usr/bin/env python3
"""
decode.py - Wydobądź ukrytą wiadomość z pliku tekstowego

Użycie:
    python decode.py -i stego.txt
    python decode.py -i stego.txt -o secret.txt
"""

import sys
import argparse
from pathlib import Path


class ZeroWidthSteganography:
    """Steganografia używająca znaków zerowej szerokości Unicode."""
    
    ZWSP = '\\u200B'  # Zero-width space (0)
    ZWNJ = '\\u200C'  # Zero-width non-joiner (1)
    ZWJ = '\\u200D'   # Zero-width joiner (separator)
    
    def decode(self, stego_text):
        """Wydobądź ukrytą wiadomość."""
        # Wyciągnij znaki zerowej szerokości
        zw_chars = ''.join(c for c in stego_text 
                          if c in [self.ZWSP, self.ZWNJ, self.ZWJ])
        
        if not zw_chars:
            return None
        
        # Konwertuj na binarny
        binary = ''.join('0' if c == self.ZWSP else '1' if c == self.ZWNJ else ''
                        for c in zw_chars)
        
        # Konwertuj binarny na tekst
        text = ""
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        
        return text if text else None


class FeatureCodingSteganography:
    """Steganografia oparta na kodowaniu cech."""
    
    def __init__(self):
        self.categories = {
            'CF1': list('aeiouąęóAEIOU'),
            'CF2': list('bcdfghjklmnpqrstvwxyzćłńśźżBCDFGHJKLMNPQRSTVWXYZĆŁŃŚŹŻ'),
        }
        
        self.char_to_category = {}
        for category, chars in self.categories.items():
            for char in chars:
                self.char_to_category[char] = category
    
    def decode(self, stego_text):
        """Wydobądź ukrytą wiadomość."""
        # Znajdź transformowane znaki (uppercase)
        transformed = []
        for i, char in enumerate(stego_text):
            char_lower = char.lower()
            if (char.isupper() and char_lower in self.char_to_category):
                transformed.append((i, char_lower, self.char_to_category[char_lower]))
        
        if len(transformed) < 2:
            return None
        
        # Dekoduj przez porównanie kategorii
        current_category = transformed[0][2]
        binary = []
        
        for i in range(1, len(transformed)):
            next_category = transformed[i][2]
            if next_category == current_category:
                binary.append('0')
            else:
                binary.append('1')
                current_category = next_category
        
        # Konwertuj binarny na tekst
        binary_str = ''.join(binary)
        text = ""
        for i in range(0, len(binary_str), 8):
            byte = binary_str[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        
        return text if text else None


def main():
    parser = argparse.ArgumentParser(
        description='Wydobądź ukrytą wiadomość z pliku tekstowego',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  # Wyświetl wiadomość na ekranie
  python decode.py -i stego.txt
  
  # Zapisz wiadomość do pliku
  python decode.py -i stego.txt -o secret.txt
  
  # Spróbuj obu metod automatycznie
  python decode.py -i stego.txt -m auto

Metody:
  auto          - Automatycznie wykryj metodę (domyślnie)
  zero-width    - Dekoduj znaki zerowej szerokości
  feature-coding - Dekoduj transformacje znaków
        """
    )
    
    parser.add_argument('-i', '--input', required=True,
                       help='Plik ze stego-tekstem')
    parser.add_argument('-o', '--output',
                       help='Plik wyjściowy dla odkodowanej wiadomości')
    parser.add_argument('-m', '--method',
                       choices=['auto', 'zero-width', 'feature-coding'],
                       default='auto',
                       help='Metoda dekodowania (domyślnie: auto)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Pokaż szczegółowe informacje')
    
    args = parser.parse_args()
    
    try:
        # Wczytaj stego-tekst
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ Błąd: Plik '{args.input}' nie istnieje!", file=sys.stderr)
            sys.exit(1)
        
        with open(input_path, 'r', encoding='utf-8') as f:
            stego_text = f.read()
        
        if not stego_text:
            print("❌ Błąd: Plik jest pusty!", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"📄 Wczytano: {len(stego_text)} znaków")
            print(f"🔍 Metoda: {args.method}")
        
        # Dekodowanie
        secret_text = None
        method_used = None
        
        if args.method == 'auto':
            # Spróbuj zero-width najpierw
            zw_system = ZeroWidthSteganography()
            secret_text = zw_system.decode(stego_text)
            if secret_text:
                method_used = 'zero-width'
            else:
                # Spróbuj feature-coding
                fc_system = FeatureCodingSteganography()
                secret_text = fc_system.decode(stego_text)
                if secret_text:
                    method_used = 'feature-coding'
        
        elif args.method == 'zero-width':
            zw_system = ZeroWidthSteganography()
            secret_text = zw_system.decode(stego_text)
            method_used = 'zero-width'
        
        else:  # feature-coding
            fc_system = FeatureCodingSteganography()
            secret_text = fc_system.decode(stego_text)
            method_used = 'feature-coding'
        
        if not secret_text:
            print("❌ Nie znaleziono ukrytej wiadomości!", file=sys.stderr)
            print("   Sprawdź czy plik zawiera zakodowaną wiadomość.", file=sys.stderr)
            sys.exit(1)
        
        # Wynik
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(secret_text)
            
            if args.verbose:
                print(f"\\n✅ Sukces!")
                print(f"🔓 Odkodowano metodą: {method_used}")
                print(f"📝 Długość wiadomości: {len(secret_text)} znaków")
                print(f"💾 Zapisano do: {args.output}")
            else:
                print(f"✅ Odkodowano wiadomość do pliku: {args.output}")
        else:
            if args.verbose:
                print(f"\\n✅ Sukces!")
                print(f"🔓 Odkodowano metodą: {method_used}")
                print(f"📝 Długość wiadomości: {len(secret_text)} znaków")
                print(f"\\n{'='*60}")
                print("ODKODOWANA WIADOMOŚĆ:")
                print('='*60)
            
            print(secret_text)
            
            if args.verbose:
                print('='*60)
        
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
'''

# Zapisz decode.py
with open('decode.py', 'w', encoding='utf-8') as f:
    f.write(decode_script)

print("✅ Utworzono: decode.py")

# ==================== PRZYKŁADOWY PLIK COVER ====================
cover_example = """Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod 
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim 
veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 
commodo consequat. Duis aute irure dolor in reprehenderit in voluptate 
velit esse cillum dolore eu fugiat nulla pariatur.

Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia 
deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste 
natus error sit voluptatem accusantium doloremque laudantium totam rem 
aperiam eaque ipsa quae ab illo inventore veritatis et quasi architecto 
beatae vitae dicta sunt explicabo."""

with open('cover.txt', 'w', encoding='utf-8') as f:
    f.write(cover_example)

print("✅ Utworzono: cover.txt (przykładowy tekst)")

# ==================== README DLA CLI ====================
cli_readme = """# Steganografia - Narzędzia CLI

Proste narzędzia wiersza poleceń do ukrywania i wydobywania tajnych wiadomości w plikach tekstowych.

## Instalacja

Nie wymaga instalacji dodatkowych bibliotek. Wymagany Python 3.6+

```bash
python --version  # Sprawdź wersję
```

## Użycie

### 1. Kodowanie (ukrywanie wiadomości)

**Podstawowe użycie:**
```bash
python encode.py -c cover.txt -s "Tajna wiadomość" -o stego.txt
```

**Z pliku:**
```bash
python encode.py -c cover.txt -sf secret.txt -o stego.txt
```

**Z wyborem metody:**
```bash
# Zero-width (niewidoczne, uniwersalne)
python encode.py -c cover.txt -s "Tajne" -o stego.txt -m zero-width

# Feature coding (transformacja znaków)
python encode.py -c cover.txt -s "Hi" -o stego.txt -m feature-coding
```

**Tryb szczegółowy:**
```bash
python encode.py -c cover.txt -s "Test" -o stego.txt -v
```

### 2. Dekodowanie (wydobywanie wiadomości)

**Wyświetl na ekranie:**
```bash
python decode.py -i stego.txt
```

**Zapisz do pliku:**
```bash
python decode.py -i stego.txt -o odkodowana.txt
```

**Automatyczne wykrywanie metody:**
```bash
python decode.py -i stego.txt -m auto
```

**Tryb szczegółowy:**
```bash
python decode.py -i stego.txt -v
```

## Metody Steganografii

### Zero-Width (Domyślna)
- ✅ Działa z **każdym** tekstem
- ✅ Całkowicie **niewidoczna**
- ✅ Prosta w użyciu
- ⚠️ Można wykryć szukając znaków Unicode

**Jak działa:**
Używa niewidocznych znaków Unicode (zero-width space, zero-width non-joiner) do reprezentacji bitów:
- `\\u200B` (zero-width space) = bit 0
- `\\u200C` (zero-width non-joiner) = bit 1

### Feature Coding
- ✅ Rozproszony w tekście
- ✅ Trudniejszy do wykrycia
- ⚠️ Wymaga tekstu z odpowiednimi znakami (samogłoski + spółgłoski)
- ⚠️ Może zmieniać wygląd (uppercase)

**Jak działa:**
Wykorzystuje automat skończony (FSM) i transformacje znaków:
- Bit 0 = ten sam typ znaku (samogłoska→samogłoska)
- Bit 1 = inny typ znaku (samogłoska→spółgłoska)

## Kompletny Przykład

```bash
# 1. Utwórz plik z tajną wiadomością
echo "To jest tajna wiadomość!" > secret.txt

# 2. Zakoduj w pliku przykrywającym
python encode.py -c cover.txt -sf secret.txt -o stego.txt -v

# 3. Dekoduj z powrotem
python decode.py -i stego.txt -v

# 4. Lub zapisz do pliku
python decode.py -i stego.txt -o odkodowana.txt
```

## Parametry

### encode.py

```
-c, --cover FILE      Plik z tekstem przykrywającym (wymagany)
-s, --secret TEXT     Tajna wiadomość jako tekst
-sf, --secret-file    Plik z tajną wiadomością
-o, --output FILE     Plik wyjściowy (wymagany)
-m, --method METHOD   Metoda: zero-width|feature-coding (domyślnie: zero-width)
-v, --verbose         Pokaż szczegóły
```

### decode.py

```
-i, --input FILE      Plik ze stego-tekstem (wymagany)
-o, --output FILE     Plik wyjściowy dla odkodowanej wiadomości
-m, --method METHOD   Metoda: auto|zero-width|feature-coding (domyślnie: auto)
-v, --verbose         Pokaż szczegóły
```

## Przykłady Zastosowań

### 1. Bezpieczna komunikacja
```bash
# Alice koduje
python encode.py -c public_message.txt -s "Spotkanie o 15:00" -o message.txt

# Bob dekoduje
python decode.py -i message.txt
```

### 2. Wodoznaki w dokumentach
```bash
python encode.py -c document.txt -s "Copyright 2025" -o marked_doc.txt
```

### 3. Śledzenie wycieków
```bash
# Unikalne ID dla każdego odbiorcy
python encode.py -c report.txt -s "RECIPIENT-123" -o report_copy.txt
```

## Bezpieczeństwo

⚠️ **WAŻNE:**
1. **Szyfruj przed ukryciem**: Zawsze zaszyfruj wiadomość przed steganografią
2. **Długość**: Krótsze wiadomości są bezpieczniejsze
3. **Tekst przykrywający**: Używaj naturalnego, nieprzetworzonego tekstu
4. **Nie polegaj tylko na steganografii**: To nie jest szyfrowanie!

### Przykład z szyfrowaniem:

```bash
# 1. Zaszyfruj wiadomość (np. OpenSSL)
echo "Tajna wiadomość" | openssl enc -aes-256-cbc -base64 > encrypted.txt

# 2. Ukryj zaszyfrowaną wiadomość
python encode.py -c cover.txt -sf encrypted.txt -o stego.txt

# 3. Dekoduj
python decode.py -i stego.txt -o encrypted_out.txt

# 4. Odszyfruj
cat encrypted_out.txt | openssl enc -d -aes-256-cbc -base64
```

## Rozwiązywanie Problemów

### "Wiadomość za długa!"
- Użyj dłuższego tekstu przykrywającego
- Skróć tajną wiadomość
- Dla feature-coding: użyj tekstu z więcej samogłoskami/spółgłoskami

### "Nie znaleziono ukrytej wiadomości!"
- Sprawdź czy używasz prawidłowej metody dekodowania
- Użyj `-m auto` do automatycznego wykrywania
- Sprawdź czy plik nie został przypadkowo zmodyfikowany

### "Brak transformowalnych znaków!"
- Dla feature-coding: użyj tekstu z literami (nie tylko liczby/znaki specjalne)
- Alternatywnie użyj metody zero-width: `-m zero-width`

## Pliki

- `encode.py` - Skrypt kodujący
- `decode.py` - Skrypt dekodujący  
- `cover.txt` - Przykładowy tekst przykrywający
- `CLI_README.md` - Ta dokumentacja

## Licencja

Do użytku edukacyjnego i badawczego.
"""

with open('CLI_README.md', 'w', encoding='utf-8') as f:
    f.write(cli_readme)

print("✅ Utworzono: CLI_README.md")

print("\n" + "="*70)
print("PODSUMOWANIE - Utworzono narzędzia CLI")
print("="*70)

summary = """
📦 Utworzone pliki:
  
  🔧 encode.py          - Narzędzie do kodowania (ukrywania wiadomości)
  🔓 decode.py          - Narzędzie do dekodowania (wydobywania wiadomości)
  📄 cover.txt          - Przykładowy tekst przykrywający
  📖 CLI_README.md      - Pełna dokumentacja narzędzi

🎯 Szybki start:

  1. KODOWANIE (ukryj wiadomość):
     python encode.py -c cover.txt -s "Tajne!" -o stego.txt
  
  2. DEKODOWANIE (wydobądź wiadomość):
     python decode.py -i stego.txt

💡 Przykłady użycia:

  # Z pliku tekstowego
  echo "Moja tajna wiadomość" > secret.txt
  python encode.py -c cover.txt -sf secret.txt -o stego.txt
  python decode.py -i stego.txt -o odkodowana.txt
  
  # Tryb szczegółowy
  python encode.py -c cover.txt -s "Test" -o stego.txt -v
  python decode.py -i stego.txt -v
  
  # Wybór metody
  python encode.py -c cover.txt -s "Hi" -o stego.txt -m zero-width
  python encode.py -c cover.txt -s "Hi" -o stego.txt -m feature-coding

🔧 Dostępne metody:

  • zero-width (domyślna)
    - Niewidoczne znaki Unicode
    - Działa z każdym tekstem
    - Najprostsza w użyciu
  
  • feature-coding
    - Transformacje znaków (FSM)
    - Wymaga liter w tekście
    - Bardziej zaawansowana

📋 Parametry:

  encode.py:
    -c FILE    Tekst przykrywający (wymagany)
    -s TEXT    Tajna wiadomość
    -sf FILE   Tajna wiadomość z pliku
    -o FILE    Plik wyjściowy (wymagany)
    -m METHOD  Metoda: zero-width|feature-coding
    -v         Tryb szczegółowy
  
  decode.py:
    -i FILE    Plik wejściowy (wymagany)
    -o FILE    Zapisz do pliku
    -m METHOD  Metoda: auto|zero-width|feature-coding
    -v         Tryb szczegółowy
"""

print(summary)

print("="*70)
print("✅ Narzędzia CLI gotowe do użycia!")
print("="*70)
