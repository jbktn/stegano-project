import sys
import math
import os

# Optimized 4-category emoticon sets - EXACTLY 16 emoticons each
EMOTICON_SETS = {
    'happy': [
        '😊', '😀', '😃', '😄', '😁', '🙂', '😍', '🥰',
        '😘', '😇', '🤗', '😌', '☺️', '🥳', '💖', '❤️'
    ],
    'sad': [
        '😢', '😭', '😔', '😞', '😟', '🙁', '☹️', '😕',
        '😥', '😰', '😓', '😪', '😫', '🥺', '💔', '😿'
    ],
    'funny': [
        '😂', '🤣', '😆', '😅', '😹', '😸', '🤪', '😜',
        '😝', '😛', '🙃', '😋', '🤭', '🤡', '👻', '🤠'
    ],
    'angry': [
        '😠', '😡', '🤬', '😤', '👿', '😾', '💢', '😖',
        '😣', '😩', '😫', '🤯', '😒', '🙄', '😑', '😬'
    ]
}

def bits_to_decimal(bits):
    return int(bits, 2)

def text_to_binary(text):
    binary = ''
    for char in text:
        binary += format(ord(char), '08b')
    return binary

def batch_sentiment_labels_with_llm(cover_sentences):
    try:
        import ollama

        # Przygotuj chat z wszystkimi liniami
        chat_text = '\n'.join(cover_sentences)

        # Prompt batch - przesyła całą konwersację naraz
        batch_prompt = f"""You are a sentiment annotation assistant.
Label the EMOTION category for each line in the following chat.
Available categories: happy, sad, funny, angry.

INSTRUCTIONS:
- Return ONLY a list of labels, one label per line
- Labels MUST be in the same order as the chat
- DO NOT add any commentary, headers, or explanations
- Response format: one label per line (happy, sad, funny, or angry)

CRITICAL RULES:
- Insults, curse words, hostility → angry
- Questions or sentences with negative words (idiot, stupid, etc.) → angry
- "Why" questions with criticism → angry
- Passive-aggressive tone → angry or sad
- Positive, joyful emotions → happy
- Sorrowful, disappointed emotions → sad
- Humorous, playful emotions → funny

Chat:
{chat_text}

Labels (one per line, matching chat order above):"""

        response = ollama.chat(
            model='llama3.1',
            messages=[{
                'role': 'user',
                'content': batch_prompt
            }]
        )

        # Parsuj odpowiedź - każda linia to jedna etykieta
        response_text = response['message']['content'].strip()
        lines = response_text.lower().split('\n')

        # Czyść whitespace
        labels = [line.strip() for line in lines if line.strip()]

        # Walidacja
        if len(labels) != len(cover_sentences):
            print(f"Warning: Got {len(labels)} labels but expected {len(cover_sentences)}")
            print(f"Response from LLM:\n{response_text}")
            # Dopełnij lub obetnij jeśli liczby się nie zgadzają
            if len(labels) < len(cover_sentences):
                labels.extend(['happy'] * (len(cover_sentences) - len(labels)))
            else:
                labels = labels[:len(cover_sentences)]

        # Waliduj każdą etykietę
        valid_sentiments = {'happy', 'sad', 'funny', 'angry'}
        for i, label in enumerate(labels):
            if label not in valid_sentiments:
                # Spróbuj znaleźć sentiment w odpowiedzi
                found = False
                for valid in valid_sentiments:
                    if valid in label:
                        labels[i] = valid
                        found = True
                        break
                if not found:
                    print(f"Warning: Line {i} has invalid label '{label}', defaulting to 'happy'")
                    labels[i] = 'happy'

        # Pokaż wyniki
        for i, (sentence, label) in enumerate(zip(cover_sentences, labels), 1):
            print(f"Line {i}: '{sentence[:45]}...' -> {label.upper()}")
        print("=" * 60)

        return labels

    except ImportError:
        print("Error: ollama library not installed!")
        print("Install with: pip install ollama")
        sys.exit(1)
    except Exception as e:
        print(f"Error: llama3.1 batch analysis failed: {e}")
        print("\nFalling back to keyword-based analysis...")
        return fallback_sentiment_batch(cover_sentences)

def fallback_sentiment_batch(cover_sentences):
    """
    Fallback: Simple keyword-based sentiment analysis for all sentences.
    """
    happy_words = ['good', 'great', 'love', 'happy', 'excellent', 'wonderful', 'nice', 
                   'glad', 'joy', 'thank', 'amazing', 'fantastic', 'perfect', 'best']
    sad_words = ['bad', 'sad', 'sorry', 'unfortunately', 'terrible', 'awful', 
                 'disappointed', 'upset', 'worried', 'afraid', 'miss', 'lost', 'fail']
    funny_words = ['haha', 'lol', 'funny', 'joke', 'hilarious', 'laugh', 'amusing',
                   'rofl', 'lmao', 'comedy', 'humor']
    angry_words = ['angry', 'mad', 'hate', 'annoyed', 'frustrated', 'furious', 
                   'irritated', 'idiot', 'stupid', 'ridiculous', 'hell', 'damn',
                   'wtf', 'bullshit', 'shit', 'pissed', 'fuck', 'asshole']

    labels = []
    for sentence in cover_sentences:
        text_lower = sentence.lower()

        # Sprawdź insulty w pytaniach
        insult_patterns = ['idiot', 'stupid', 'moron', 'dumb', 'fool', 'jerk']
        if any(insult in text_lower for insult in insult_patterns):
            if 'why' in text_lower or 'what' in text_lower or '?' in sentence:
                labels.append('angry')
                continue

        scores = {
            'happy': sum(1 for word in happy_words if word in text_lower),
            'sad': sum(1 for word in sad_words if word in text_lower),
            'funny': sum(1 for word in funny_words if word in text_lower),
            'angry': sum(1 for word in angry_words if word in text_lower)
        }

        max_score = max(scores.values())
        if max_score == 0:
            labels.append('happy')
        else:
            labels.append(max(scores, key=scores.get))

    return labels

def create_stego_sentences(cover_sentences, secret_bits, sentiment_labels):
    """
    Koduje bity używając wstępnie przeanalizowanych etykiet sentymentu.
    sentiment_labels: lista etykiet ('happy', 'sad', 'funny', 'angry') dla każdej linii
    """
    results = []
    bit_index = 0
    cover_index = 0

    while bit_index < len(secret_bits):
        # Pobierz aktualną linię cover text
        current_cover = cover_sentences[cover_index % len(cover_sentences)]

        # Pobierz etykietę sentymentu dla tej linii
        emoticon_set_name = sentiment_labels[cover_index % len(cover_sentences)]

        emoticon_set = EMOTICON_SETS[emoticon_set_name]
        N = len(emoticon_set)
        n = math.floor(math.log2(N))

        # Sprawdź czy mamy wystarczająco bitów
        bits_needed = n + 2

        if bit_index + bits_needed > len(secret_bits):
            remaining = secret_bits[bit_index:]
            secret_bits += '0' * (bits_needed - len(remaining))

        # Wyciągnij bity
        emoticon_bits = secret_bits[bit_index:bit_index+n]
        position_bit = secret_bits[bit_index+n] if bit_index+n < len(secret_bits) else '0'
        punct_bit = secret_bits[bit_index+n+1] if bit_index+n+1 < len(secret_bits) else '0'

        # Wybierz emotikonę
        d = bits_to_decimal(emoticon_bits)
        if d >= N:
            d = N - 1
        emoticon = emoticon_set[d]

        # Pozycja (0=start, 1=end)
        position = 'end' if position_bit == '1' else 'start'

        # Interpunkcja (0=with comma, 1=without)
        punctuation = '' if punct_bit == '1' else ','

        # Zbuduj stego zdanie
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
        cover_index += 1

    return results

def main():
    # Parametry
    if len(sys.argv) >= 3:
        cover_file = sys.argv[1]
        secret_file = sys.argv[2]
    else:
        cover_file = 'cover.txt'
        secret_file = 'secret.txt'

    # Wczytaj cover sentences
    if not os.path.exists(cover_file):
        print(f"Error: Cover file '{cover_file}' not found!")
        sys.exit(1)

    with open(cover_file, 'r', encoding='utf-8') as f:
        cover_sentences = [line.strip() for line in f if line.strip()]

    if not cover_sentences:
        print(f"Error: Cover file '{cover_file}' is empty!")
        sys.exit(1)

    # Wczytaj secret message
    if not os.path.exists(secret_file):
        print(f"Error: Secret file '{secret_file}' not found!")
        sys.exit(1)

    with open(secret_file, 'r', encoding='utf-8') as f:
        secret_message = f.read().strip()

    # Konwertuj na binarny
    secret_bits = text_to_binary(secret_message)

    print(f"\n{'=' * 60}")
    print("STEGANOGRAPHY WITH BATCH SENTIMENT ANALYSIS")
    print(f"{'=' * 60}")
    print(f"\nCover sentences (from {cover_file}): {len(cover_sentences)} messages")
    print(f"Secret message (from {secret_file}): {secret_message}")
    print(f"Secret in binary: {secret_bits}")
    print(f"Total bits to embed: {len(secret_bits)}")
    print(f"\nEmoticon sets: 4 categories × 16 emoticons each = 64 total")
    print(f"Bits per emoticon: 4 (log2(16) = 4)")
    print(f"\nUsing: llama3.1")

    sentiment_labels = batch_sentiment_labels_with_llm(cover_sentences)

    # Koduj wiadomość
    print(f"\n{'=' * 60}")
    print("ENCODING MESSAGE")
    print(f"{'=' * 60}")
    results = create_stego_sentences(cover_sentences, secret_bits, sentiment_labels)

    print(f"\n{'=' * 60}")
    print("STEGO SENTENCES (CHAT MESSAGES):")
    print(f"{'=' * 60}")

    with open('stego_output.txt', 'w', encoding='utf-8') as f:
        for i, result in enumerate(results, 1):
            print(f"\nMessage {i}:")
            print(f"  Original: {result['cover_used']}")
            print(f"  Stego: {result['sentence']}")
            print(f"  Emoticon: {result['emoticon']} (from '{result['set']}' set)")
            print(f"  Bits: {result['bits_embedded']} ({result['bits_count']} bits)")
            f.write(result['sentence'] + '\n')

    print(f"\n{'=' * 60}")
    print(f"Total messages created: {len(results)}")
    print(f"Stego sentences saved to: stego_output.txt")

if __name__ == "__main__":
    main()
