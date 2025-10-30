
# Teraz stwórzmy demonstrację działania tych narzędzi

print("="*70)
print("DEMONSTRACJA DZIAŁANIA NARZĘDZI CLI")
print("="*70)

# Test 1: Kodowanie i dekodowanie z prostą wiadomością
print("\n📝 TEST 1: Prosta wiadomość tekstowa")
print("-" * 70)

import subprocess
import os

# Zakoduj wiadomość
test_message = "To jest tajna wiadomość!"
print(f"Tajna wiadomość: '{test_message}'")

result = subprocess.run(
    ['python', 'encode.py', '-c', 'cover.txt', '-s', test_message, '-o', 'test_stego.txt', '-v'],
    capture_output=True,
    text=True
)

print(result.stdout)

# Sprawdź czy plik został utworzony
if os.path.exists('test_stego.txt'):
    with open('test_stego.txt', 'r', encoding='utf-8') as f:
        stego_content = f.read()
    
    print(f"\n📄 Stego-tekst (pierwsze 100 znaków):")
    print(f"   {stego_content[:100]}...")
    
    # Dekoduj
    print("\n🔓 Dekodowanie...")
    result = subprocess.run(
        ['python', 'decode.py', '-i', 'test_stego.txt', '-v'],
        capture_output=True,
        text=True
    )
    print(result.stdout)

# Test 2: Z pliku
print("\n" + "="*70)
print("📝 TEST 2: Wiadomość z pliku")
print("-" * 70)

# Utwórz plik z tajną wiadomością
secret_file_content = "Spotkanie jutro o 15:00\nMiejsce: Kawiarnia Central\nKod: ALFA-123"
with open('test_secret.txt', 'w', encoding='utf-8') as f:
    f.write(secret_file_content)

print(f"Plik test_secret.txt zawiera:\n{secret_file_content}\n")

# Zakoduj z pliku
result = subprocess.run(
    ['python', 'encode.py', '-c', 'cover.txt', '-sf', 'test_secret.txt', '-o', 'test_stego2.txt'],
    capture_output=True,
    text=True
)
print(result.stdout)

# Dekoduj do pliku
result = subprocess.run(
    ['python', 'decode.py', '-i', 'test_stego2.txt', '-o', 'test_decoded.txt'],
    capture_output=True,
    text=True
)
print(result.stdout)

# Sprawdź wynik
if os.path.exists('test_decoded.txt'):
    with open('test_decoded.txt', 'r', encoding='utf-8') as f:
        decoded = f.read()
    print(f"\n✅ Odkodowana wiadomość z test_decoded.txt:\n{decoded}")

# Test 3: Porównanie metod
print("\n" + "="*70)
print("📝 TEST 3: Porównanie metod steganografii")
print("-" * 70)

message = "TEST"

# Zero-width
result1 = subprocess.run(
    ['python', 'encode.py', '-c', 'cover.txt', '-s', message, '-o', 'stego_zw.txt', '-m', 'zero-width'],
    capture_output=True,
    text=True
)

# Feature-coding
result2 = subprocess.run(
    ['python', 'encode.py', '-c', 'cover.txt', '-s', message, '-o', 'stego_fc.txt', '-m', 'feature-coding'],
    capture_output=True,
    text=True
)

# Porównaj rozmiary
with open('cover.txt', 'r', encoding='utf-8') as f:
    cover_size = len(f.read())

with open('stego_zw.txt', 'r', encoding='utf-8') as f:
    zw_content = f.read()
    zw_size = len(zw_content)

with open('stego_fc.txt', 'r', encoding='utf-8') as f:
    fc_content = f.read()
    fc_size = len(fc_content)

print("\nPorównanie wyników:")
print(f"  Oryginalny tekst:  {cover_size} znaków")
print(f"  Zero-width:        {zw_size} znaków (+{zw_size - cover_size})")
print(f"  Feature-coding:    {fc_size} znaków (+{fc_size - cover_size})")

print("\n  Zero-width (pierwsze 80 znaków):")
print(f"  {zw_content[:80]}...")

print("\n  Feature-coding (pierwsze 80 znaków, zauważ UPPERCASE):")
print(f"  {fc_content[:80]}...")

# Dekoduj obie metody
print("\n🔓 Dekodowanie automatyczne (auto):")

result = subprocess.run(
    ['python', 'decode.py', '-i', 'stego_zw.txt', '-m', 'auto'],
    capture_output=True,
    text=True
)
print(f"  Zero-width: {result.stdout.strip()}")

result = subprocess.run(
    ['python', 'decode.py', '-i', 'stego_fc.txt', '-m', 'auto'],
    capture_output=True,
    text=True
)
print(f"  Feature-coding: {result.stdout.strip()}")

# Stwórz quick reference guide
print("\n" + "="*70)
print("📋 QUICK REFERENCE CARD")
print("="*70)

quick_ref = """
┌──────────────────────────────────────────────────────────────────┐
│                    STEGANOGRAFIA CLI                             │
│                 Szybki Przewodnik Użycia                         │
└──────────────────────────────────────────────────────────────────┘

🔧 KODOWANIE (Ukrywanie)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Podstawowe:
    python encode.py -c cover.txt -s "Wiadomość" -o stego.txt

  Z pliku:
    python encode.py -c cover.txt -sf secret.txt -o stego.txt

  Metody:
    -m zero-width       → Niewidoczne (domyślne)
    -m feature-coding   → Transformacja znaków

  Szczegóły:
    -v                  → Pokaż statystyki

🔓 DEKODOWANIE (Wydobywanie)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Na ekran:
    python decode.py -i stego.txt

  Do pliku:
    python decode.py -i stego.txt -o odkodowana.txt

  Auto-wykrywanie:
    python decode.py -i stego.txt -m auto

  Szczegóły:
    -v                  → Pokaż informacje o metodzie

📋 TYPOWY WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Przygotuj tekst przykrywający (cover.txt)
  2. python encode.py -c cover.txt -s "Tajne" -o stego.txt
  3. Wyślij stego.txt do odbiorcy
  4. python decode.py -i stego.txt

⚠️ BEZPIECZEŃSTWO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ Zaszyfruj wiadomość przed ukryciem (AES, GPG)
  ✓ Używaj naturalnego tekstu jako przykrycia
  ✓ Krótsze wiadomości = bezpieczniejsze
  ✗ To NIE jest szyfrowanie!

🆘 POMOC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    python encode.py --help
    python decode.py --help

📖 Pełna dokumentacja: CLI_README.md
"""

print(quick_ref)

# Zapisz quick reference
with open('QUICK_REFERENCE.txt', 'w', encoding='utf-8') as f:
    f.write(quick_ref)

print("\n✅ Zapisano quick reference do: QUICK_REFERENCE.txt")

# Podsumowanie
print("\n" + "="*70)
print("✅ WSZYSTKO GOTOWE!")
print("="*70)

print("""
Utworzono kompletny zestaw narzędzi CLI:

📦 Pliki główne:
   • encode.py - Kodowanie (ukrywanie)
   • decode.py - Dekodowanie (wydobywanie)

📚 Dokumentacja:
   • CLI_README.md - Pełna dokumentacja
   • QUICK_REFERENCE.txt - Szybka ściągawka

📄 Przykłady:
   • cover.txt - Przykładowy tekst
   • test_stego.txt, test_stego2.txt - Przykłady stego-tekstów

🚀 Zacznij teraz:
   python encode.py -c cover.txt -s "Cześć!" -o stego.txt
   python decode.py -i stego.txt
""")

print("="*70)

# Wyczyść pliki testowe
import os
for f in ['test_stego.txt', 'test_stego2.txt', 'test_secret.txt', 
          'test_decoded.txt', 'stego_zw.txt', 'stego_fc.txt']:
    if os.path.exists(f):
        os.remove(f)
        
print("\n🧹 Pliki testowe wyczyszczone")
