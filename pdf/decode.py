import fitz  # PyMuPDF

def rgb_to_char(r, g, b):
    """
    Convert RGB values back to character based on the distributed encoding scheme.
    Now matches the encoding scheme from encode.py
    """
    # Convert back to the original values used in encoding
    r_val = round(r * 25)
    g_val = round(g * 25) 
    b_val = round(b * 25)
    
    # Reconstruct ASCII value using the same formula as encoding
    ascii_val = r_val * 36 + g_val * 6 + b_val
    
    if 1 <= ascii_val <= 255:
        return chr(ascii_val)
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
                        # Check if this is one of our encoded colors (not pure black)
                        if (r > 0 or g > 0 or b > 0) and not (r == 0 and g == 0 and b == 0):
                            char = rgb_to_char(r, g, b)
                            if char:
                                hidden_message += char
    doc.close()
    return hidden_message

# Example usage
pdf_path = "hidden_message.pdf"
message = extract_hidden_message(pdf_path)
print("Hidden message:", message)
