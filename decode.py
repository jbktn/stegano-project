import fitz  # PyMuPDF

def rgb_to_char(r, g, b):
    """
    Convert RGB values back to character based on the distributed encoding scheme.
    """
    # Normalize values back to 0-15 for red, 0-3 for green and blue
    r_val = round((r - 0.9) / 0.1 * 15)
    g_val = round((g - 0.95) / 0.05 * 3)
    b_val = round((b - 0.95) / 0.05 * 3)
    
    # Reconstruct ASCII value
    ascii_val = (r_val << 4) | (g_val << 2) | b_val
    
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
                        # Check if color values are in the expected ranges
                        if (0.9 <= r <= 1.0 and 
                            0.95 <= g <= 1.0 and 
                            0.95 <= b <= 1.0):
                            char = rgb_to_char(r, g, b)
                            if char:
                                hidden_message += char
    doc.close()
    return hidden_message

# Example usage
pdf_path = "hidden_message.pdf"
message = extract_hidden_message(pdf_path)
print("Hidden message:", message)
