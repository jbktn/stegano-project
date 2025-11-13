from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# (Optional) register a TTF if you want a different font:
# pdfmetrics.registerFont(TTFont("DejaVuSans", "/path/to/DejaVuSans.ttf"))

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
    r = int(ascii_val / 36)
    g = int(ascii_val / 6 - r * 6)
    b = int(ascii_val % 6)
    return Color(float(r / sense), float(g / sense), float(b / sense))

def embed_hidden_message(pdf_path, visible_text, hidden_message,
                         pagesize=LETTER, font_name="Helvetica", font_size=12,
                         left_margin=50, top_margin=100, bottom_margin=50, leading=None):
    """
    Generates a PDF with text that looks black but encodes a hidden message
    in the color of each character. Text is wrapped into lines and across pages.
    """
    if len(visible_text) < len(hidden_message):
        raise ValueError("Visible text must be at least as long as hidden message")

    c = canvas.Canvas(pdf_path, pagesize=pagesize)
    width, height = pagesize

    c.setFont(font_name, font_size)
    if leading is None:
        leading = int(font_size * 1.2)  # default line spacing

    max_width = width - 2 * left_margin

    # Starting coordinates
    x = left_margin
    y = height - top_margin

    # We'll draw character-by-character. Use pdfmetrics to measure widths.
    for i, ch in enumerate(visible_text):
        # If current y would go below bottom margin, create new page and reset positions
        if y < bottom_margin + leading:  # leave space for one more line
            c.showPage()
            c.setFont(font_name, font_size)
            x = left_margin
            y = height - top_margin

        ch_width = pdfmetrics.stringWidth(ch, font_name, font_size)

        # Wrap if this character would overflow the max width
        if (x - left_margin) + ch_width > max_width:
            # move to next line
            x = left_margin
            y -= leading
            # check again for page break after wrapping
            if y < bottom_margin + leading:
                c.showPage()
                c.setFont(font_name, font_size)
                x = left_margin
                y = height - top_margin

        # Set color according to hidden message (or black if past hidden_message length)
        if i < len(hidden_message):
            shade = char_to_shade(hidden_message[i])
            c.setFillColor(shade)
        else:
            c.setFillColor(Color(0, 0, 0))

        # Draw the single character
        c.drawString(x, y, ch)

        # advance x
        x += ch_width

    # save page
    c.save()
    print(f"PDF saved as {pdf_path}")

# Example usage
if __name__ == "__main__":
    visible_text = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt "
                    "ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in "
                    "voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
                    "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum")
    hidden_message = "nie dziala na razie"
    embed_hidden_message("hidden_message.pdf", visible_text, hidden_message)
