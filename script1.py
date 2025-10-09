from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import Color

def char_to_shade(c):
    """
    Map character to subtle black shade using its ASCII code.
    Only for characters with codes from 1 to 255.
    """
    ascii_val = ord(c)
    # Clamp to 1-255
    if ascii_val < 1:
        ascii_val = 1
    elif ascii_val > 255:
        ascii_val = 255
    # Each color channel gets the same value
    return Color(ascii_val / 255, ascii_val / 255, ascii_val / 255)

def embed_hidden_message(pdf_path, visible_text, hidden_message):
    """
    Generates a PDF with text that looks black but encodes a hidden message
    in the color hex values of each character.
    """
    c = canvas.Canvas(pdf_path, pagesize=LETTER)
    width, height = LETTER

    x = 50
    y = height - 100

    # Only use as many letters of visible_text as hidden_message
    if len(visible_text) < len(hidden_message):
        raise ValueError("Visible text must be at least as long as hidden message")

    for i, ch in enumerate(hidden_message):
        shade = char_to_shade(ch)
        c.setFillColor(shade)
        c.drawString(x, y, visible_text[i])
        x += 10  # Move right for next character

    # Add any remaining visible text in true black
    c.setFillColor(Color(0, 0, 0))
    for ch in visible_text[len(hidden_message):]:
        c.drawString(x, y, ch)
        x += 10

    c.save()
    print(f"PDF saved as {pdf_path}")

# Example usage
visible_text = "This is just a normal line of text that looks black."
hidden_message = "secret"

embed_hidden_message("hidden_message.pdf", visible_text, hidden_message)
