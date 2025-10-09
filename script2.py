import fitz  # PyMuPDF

def rgb_to_char(r, g, b):
    """
    Convert RGB (0.0 - 1.0) grayscale value to character.
    Assumes the text color is in the format (x, x, x) and x * 255 = ASCII.
    """
    # Since it's grayscale, any channel works
    val = round(r * 255)
    if 1 <= val <= 255:
        return chr(val)
    return ''

def extract_hidden_message(pdf_path):
    doc = fitz.open(pdf_path)
    hidden_message = ""

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    color = span.get("color")
                    if color is not None:
                        r, g, b = span["color"]
                        # Colors in PyMuPDF are 0-1 floats
                        if r == g == b and 0 < r < 1:
                            char = rgb_to_char(r, g, b)
                            if char:
                                hidden_message += char
    doc.close()
    return hidden_message

# Example usage
pdf_path = "hidden_message.pdf"
message = extract_hidden_message(pdf_path)
print("Hidden message:", message)
