# Steganografia - Narzędzia CLI

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
- `\u200B` (zero-width space) = bit 0
- `\u200C` (zero-width non-joiner) = bit 1

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
