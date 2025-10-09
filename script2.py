import fitz  # PyMuPDF

def rgb_to_char(r, g, b):
    val = round(r * 255)
    if 1 <= val <= 255:
        return chr(val)
    return ''

def int_to_rgb(color_int):
    r = (color_int >> 16) & 255
    g = (color_int >> 8) & 255
    b = color_int & 255
    return r / 255, g / 255, b / 255

def extract_hidden_message(pdf_path):
    doc = fitz.open(pdf_path)
    hidden_message = ""

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    color_int = span.get("color")
                    if color_int is not None:
                        r, g, b = int_to_rgb(color_int)
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
