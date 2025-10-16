import tkinter as tk
from tkinter import ttk, filedialog
import os
from src.encode import embed_hidden_message

class SteganographyApp:
    def __init__(self, window):
        self.window = window
        self.window.title("PDF Steganography Tool")
        self.window.geometry("400x300")
        
        # Visible text input
        self.visible_label = tk.Label(window, text="Visible text:")
        self.visible_label.pack(pady=5)
        
        self.visible_text = tk.Text(window, height=4, width=40)
        self.visible_text.pack(pady=5)
        
        # Hidden message input
        self.hidden_label = tk.Label(window, text="Hidden message:")
        self.hidden_label.pack(pady=5)
        
        self.hidden_entry = tk.Entry(window, width=40)
        self.hidden_entry.pack(pady=5)
        
        # Output file selection
        self.output_button = tk.Button(window, text="Select Output PDF", command=self.select_output)
        self.output_button.pack(pady=10)
        
        self.output_label = tk.Label(window, text="No file selected")
        self.output_label.pack(pady=5)
        
        # Generate PDF button
        self.generate_button = tk.Button(window, text="Generate PDF", command=self.generate_pdf)
        self.generate_button.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(window, text="")
        self.status_label.pack(pady=10)
        
        self.output_path = None

    def select_output(self):
        self.output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if self.output_path:
            self.output_label.config(text=os.path.basename(self.output_path))

    def generate_pdf(self):
        if not self.output_path:
            self.status_label.config(text="Please select output file location", fg="red")
            return
            
        visible_text = self.visible_text.get("1.0", tk.END).strip()
        hidden_message = self.hidden_entry.get().strip()
        
        if not visible_text or not hidden_message:
            self.status_label.config(text="Please fill in both text fields", fg="red")
            return
            
        if len(visible_text) < len(hidden_message):
            self.status_label.config(
                text="Visible text must be longer than hidden message", 
                fg="red"
            )
            return
            
        try:
            embed_hidden_message(self.output_path, visible_text, hidden_message)
            self.status_label.config(
                text=f"PDF generated successfully: {os.path.basename(self.output_path)}", 
                fg="green"
            )
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()