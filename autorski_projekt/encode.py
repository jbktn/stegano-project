from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def char_to_shade(c):
    """
    Map character to subtle black shade using its ASCII code.
    Distribute ASCII value across RGB channels for smaller color fluctuations.
    """
    ascii_val = ord(c)
    sense = 128
    # Clamp to 1-255
    ascii_val = max(1, min(ascii_val, 255))
    # Spread bits across RGB channels
    r = int(ascii_val/36)
    g = int(ascii_val/6 - r*6)
    b = int(ascii_val%6)
    return Color(float(r/sense), float(g/sense), float(b/sense))

def embed_hidden_message(pdf_path, visible_text, hidden_message):
    """
    Generates a PDF with text that looks black but encodes a hidden message
    in the color hex values of each character.
    """
    c = canvas.Canvas(pdf_path, pagesize=LETTER)
    width, height = LETTER
    
    # Set font and size
    c.setFont("Helvetica", 12)
    
    x = 50
    y = height - 100

    if len(visible_text) < len(hidden_message):
        raise ValueError("Visible text must be at least as long as hidden message")

    # Create text object for better spacing control
    text = c.beginText(x, y)
    
    # Process hidden message characters
    for i, ch in enumerate(hidden_message):
        shade = char_to_shade(ch)
        text.setFillColor(shade)
        text.textOut(visible_text[i])
    
    # Add remaining visible text in true black
    text.setFillColor(Color(0, 0, 0))
    text.textOut(visible_text[len(hidden_message):])
    
    c.drawText(text)
    c.save()
    print(f"PDF saved as {pdf_path}")

# Example usage
visible_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"
hidden_message = "nie dziala na razie"

embed_hidden_message("hidden_message.pdf", visible_text, hidden_message)
