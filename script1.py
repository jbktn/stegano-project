from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
visible_text = "This is just a normal line of text that looks black."
hidden_message = "qwertyuiop"

embed_hidden_message("hidden_message.pdf", visible_text, hidden_message)
