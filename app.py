import tkinter as tk
from tkinter import ttk
import os

window = tk.Tk()
window.title("Drop-down w oknie")
window.geometry("350x250")

label_select = tk.Label(window, text="Wybierz folder:")
label_select.pack(pady=10)

current_dir = os.getcwd()
options = [f for f in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, f))]

combo = ttk.Combobox(window, values=options, state="readonly")
combo.pack(pady=5)

label_msg = tk.Label(window, text="Podaj wiadomość do ukrycia:")
label_msg.pack(pady=5)

entry = tk.Entry(window, width=35)
entry.pack(pady=5)

result_label = tk.Label(window, text="", fg="blue")
result_label.pack(pady=10)

def on_submit():
    message = entry.get().strip()
    selected = combo.get()
    if not selected:
        result_label.config(text="⚠️ Nie wybrano folderu!")
    elif not message:
        result_label.config(text="⚠️ Wpisz wiadomość!")
    else:
        result_label.config(text=f"📁 {selected}\n💬 {message}")

submit_button = tk.Button(window, text="Zatwierdź", command=on_submit)
submit_button.pack(pady=5)

window.mainloop()
