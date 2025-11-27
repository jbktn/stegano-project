import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QComboBox, QRadioButton,
    QButtonGroup, QFileDialog, QTextEdit, QMessageBox, QGroupBox, QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

class AlgorithmFrame(QWidget):
    """Base class dla encode/decode frames"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.algorithms = self.load_algorithms()
    
    def load_algorithms(self):
        """Wczytaj algorytmy z folderów"""
        algorithms_dir = Path(__file__).parent / "algorithms"
        
        print(f"🔍 Szukam algorytmów w: {algorithms_dir}")
        print(f"   Folder istnieje: {algorithms_dir.exists()}")
        
        algos = {}
        
        if not algorithms_dir.exists():
            print(f"⚠️  Folder 'algorithms' nie istnieje!")
            print(f"   Utwórz strukturę:")
            print(f"   {Path(__file__).parent}/")
            print(f"   └── algorithms/")
            print(f"       ├── shift_position/")
            print(f"       │   ├── encode.py")
            print(f"       │   └── decode.py")
            print(f"       ├── formatting_spaces/")
            print(f"       ├── one_time_pad/")
            print(f"       ├── feature_coding/")
            print(f"       └── pdf_color/")
            return algos
        
        for algo_folder in algorithms_dir.iterdir():
            if algo_folder.is_dir():
                encode_path = algo_folder / "encode.py"
                decode_path = algo_folder / "decode.py"
                
                folder_name = algo_folder.name
                encode_exists = encode_path.exists()
                decode_exists = decode_path.exists()
                
                print(f"📁 {folder_name}:")
                print(f"   encode.py: {encode_exists}")
                print(f"   decode.py: {decode_exists}")
                
                if encode_exists and decode_exists:
                    algo_name = folder_name.replace("_", " ").title()
                    algos[algo_name] = {
                        'encode': str(encode_path),
                        'decode': str(decode_path),
                        'folder': str(algo_folder)
                    }
                    print(f"   ✅ Załadowano jako: {algo_name}")
                else:
                    print(f"   ❌ Brakuje pliku(ów)")
        
        print(f"\n✅ Załadowano {len(algos)} algorytmów: {list(algos.keys())}\n")
        return algos

class EncodeFrame(QWidget):
    """Zakładka do enkodowania"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.algorithms = self.load_algorithms()
        self.cover_content = ""
        self.secret_content = ""
        self.init_ui()
    
    def load_algorithms(self):
        """Wczytaj algorytmy z folderów"""
        algorithms_dir = Path(__file__).parent / "algorithms"
        algos = {}
        
        if algorithms_dir.exists():
            for algo_folder in algorithms_dir.iterdir():
                if algo_folder.is_dir():
                    encode_path = algo_folder / "encode.py"
                    decode_path = algo_folder / "decode.py"
                    
                    if encode_path.exists() and decode_path.exists():
                        algo_name = algo_folder.name.replace("_", " ").title()
                        algos[algo_name] = {
                            'encode': str(encode_path),
                            'decode': str(decode_path),
                            'folder': str(algo_folder)
                        }
        
        return algos
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Algorytm
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Algorithm:"))
        self.algo_combo = QComboBox()
        
        if self.algorithms:
            self.algo_combo.addItems(sorted(self.algorithms.keys()))
        else:
            self.algo_combo.addItem("No algorithms found")
        
        algo_layout.addWidget(self.algo_combo)
        layout.addLayout(algo_layout)
        
        layout.addSpacing(10)
        
        # Cover source
        layout.addWidget(QLabel("Cover Source:"))
        cover_source_layout = QHBoxLayout()
        self.cover_file_radio = QRadioButton("File")
        self.cover_input_radio = QRadioButton("Input")
        self.cover_file_radio.setChecked(True)
        self.cover_group = QButtonGroup()
        self.cover_group.addButton(self.cover_file_radio, 0)
        self.cover_group.addButton(self.cover_input_radio, 1)
        cover_source_layout.addWidget(self.cover_file_radio)
        cover_source_layout.addWidget(self.cover_input_radio)
        layout.addLayout(cover_source_layout)
        
        # Cover input
        self.cover_file_edit = QLineEdit()
        self.cover_file_edit.setPlaceholderText("Select cover file...")
        self.cover_file_btn = QPushButton("Browse")
        self.cover_file_btn.clicked.connect(self.browse_cover_file)
        cover_file_layout = QHBoxLayout()
        cover_file_layout.addWidget(self.cover_file_edit)
        cover_file_layout.addWidget(self.cover_file_btn)
        layout.addLayout(cover_file_layout)
        
        self.cover_text_edit = QTextEdit()
        self.cover_text_edit.setPlaceholderText("Enter cover text here...")
        self.cover_text_edit.setVisible(False)
        self.cover_text_edit.setMaximumHeight(80)
        layout.addWidget(self.cover_text_edit)
        
        self.cover_file_radio.toggled.connect(self.toggle_cover_source)
        
        layout.addSpacing(10)
        
        # Secret source
        layout.addWidget(QLabel("Secret Source:"))
        secret_source_layout = QHBoxLayout()
        self.secret_file_radio = QRadioButton("File")
        self.secret_input_radio = QRadioButton("Input")
        self.secret_file_radio.setChecked(True)
        self.secret_group = QButtonGroup()
        self.secret_group.addButton(self.secret_file_radio, 0)
        self.secret_group.addButton(self.secret_input_radio, 1)
        secret_source_layout.addWidget(self.secret_file_radio)
        secret_source_layout.addWidget(self.secret_input_radio)
        layout.addLayout(secret_source_layout)
        
        # Secret input
        self.secret_file_edit = QLineEdit()
        self.secret_file_edit.setPlaceholderText("Select secret file...")
        self.secret_file_btn = QPushButton("Browse")
        self.secret_file_btn.clicked.connect(self.browse_secret_file)
        secret_file_layout = QHBoxLayout()
        secret_file_layout.addWidget(self.secret_file_edit)
        secret_file_layout.addWidget(self.secret_file_btn)
        layout.addLayout(secret_file_layout)
        
        self.secret_text_edit = QTextEdit()
        self.secret_text_edit.setPlaceholderText("Enter secret message here...")
        self.secret_text_edit.setVisible(False)
        self.secret_text_edit.setMaximumHeight(80)
        layout.addWidget(self.secret_text_edit)
        
        self.secret_file_radio.toggled.connect(self.toggle_secret_source)
        
        layout.addSpacing(10)
        
        # Output file
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output file:"))
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("stego_output")
        output_layout.addWidget(self.output_edit)
        layout.addLayout(output_layout)
        
        layout.addSpacing(15)
        
        # Encode button
        self.encode_btn = QPushButton("ENCODE")
        self.encode_btn.setMinimumHeight(40)
        self.encode_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.encode_btn.clicked.connect(self.encode)
        layout.addWidget(self.encode_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def toggle_cover_source(self):
        is_file = self.cover_file_radio.isChecked()
        self.cover_file_edit.setVisible(is_file)
        self.cover_file_btn.setVisible(is_file)
        self.cover_text_edit.setVisible(not is_file)
    
    def toggle_secret_source(self):
        is_file = self.secret_file_radio.isChecked()
        self.secret_file_edit.setVisible(is_file)
        self.secret_file_btn.setVisible(is_file)
        self.secret_text_edit.setVisible(not is_file)
    
    def browse_cover_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select cover file", "", "Text Files (*.txt);;All Files (*)")
        if file:
            self.cover_file_edit.setText(file)
    
    def browse_secret_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select secret file", "", "Text Files (*.txt);;All Files (*)")
        if file:
            self.secret_file_edit.setText(file)
    
    def encode(self):
        if not self.algorithms:
            QMessageBox.warning(self, "Error", "❌ No algorithms found!\n\nUtwórz folder 'algorithms' obok app.py")
            return
        
        algo_name = self.algo_combo.currentText()
        if algo_name not in self.algorithms:
            QMessageBox.warning(self, "Error", f"❌ Select valid algorithm")
            return
        
        # Get cover source
        if self.cover_file_radio.isChecked():
            if not self.cover_file_edit.text():
                QMessageBox.warning(self, "Error", "❌ Select cover file")
                return
            cover_args = ["-fc", self.cover_file_edit.text()]
        else:
            if not self.cover_text_edit.toPlainText():
                QMessageBox.warning(self, "Error", "❌ Enter cover text")
                return
            cover_args = ["-ic", self.cover_text_edit.toPlainText()]
        
        # Get secret source
        if self.secret_file_radio.isChecked():
            if not self.secret_file_edit.text():
                QMessageBox.warning(self, "Error", "❌ Select secret file")
                return
            secret_args = ["-fs", self.secret_file_edit.text()]
        else:
            if not self.secret_text_edit.toPlainText():
                QMessageBox.warning(self, "Error", "❌ Enter secret message")
                return
            secret_args = ["-is", self.secret_text_edit.toPlainText()]
        
        # Output file
        output = self.output_edit.text() or "stego_output"
        output_args = ["-o", output]
        
        # Run encode
        try:
            encode_script = self.algorithms[algo_name]['encode']
            cmd = [sys.executable, encode_script] + cover_args + secret_args + output_args
            
            print(f"🔄 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                QMessageBox.information(self, "Success", f"✅ Encoded successfully!\nOutput: {output}")
            else:
                QMessageBox.critical(self, "Error", f"❌ Encoding failed:\n{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Error: {str(e)}")

class DecodeFrame(QWidget):
    """Zakładka do dekodowania"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.algorithms = self.load_algorithms()
        self.init_ui()
    
    def load_algorithms(self):
        """Wczytaj algorytmy z folderów"""
        algorithms_dir = Path(__file__).parent / "algorithms"
        algos = {}
        
        if algorithms_dir.exists():
            for algo_folder in algorithms_dir.iterdir():
                if algo_folder.is_dir():
                    encode_path = algo_folder / "encode.py"
                    decode_path = algo_folder / "decode.py"
                    
                    if encode_path.exists() and decode_path.exists():
                        algo_name = algo_folder.name.replace("_", " ").title()
                        algos[algo_name] = {
                            'encode': str(encode_path),
                            'decode': str(decode_path),
                            'folder': str(algo_folder)
                        }
        
        return algos
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Algorytm
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Algorithm:"))
        self.algo_combo = QComboBox()
        
        if self.algorithms:
            self.algo_combo.addItems(sorted(self.algorithms.keys()))
        else:
            self.algo_combo.addItem("No algorithms found")
        
        algo_layout.addWidget(self.algo_combo)
        layout.addLayout(algo_layout)
        
        layout.addSpacing(10)
        
        # Input file
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input file:"))
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Select encoded file...")
        input_btn = QPushButton("Browse")
        input_btn.clicked.connect(self.browse_input_file)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)
        
        layout.addSpacing(10)
        
        # Output file (optional)
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output file (optional):"))
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Leave empty to display in window")
        output_layout.addWidget(self.output_edit)
        layout.addLayout(output_layout)
        
        layout.addSpacing(15)
        
        # Result display
        layout.addWidget(QLabel("Decoded message:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(150)
        layout.addWidget(self.result_text)
        
        layout.addSpacing(15)
        
        # Decode button
        self.decode_btn = QPushButton("DECODE")
        self.decode_btn.setMinimumHeight(40)
        self.decode_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.decode_btn.clicked.connect(self.decode)
        layout.addWidget(self.decode_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def browse_input_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select encoded file", "")
        if file:
            self.input_edit.setText(file)
    
    def decode(self):
        if not self.algorithms:
            QMessageBox.warning(self, "Error", "❌ No algorithms found!\n\nUtwórz folder 'algorithms' obok app.py")
            return
        
        algo_name = self.algo_combo.currentText()
        if algo_name not in self.algorithms:
            QMessageBox.warning(self, "Error", "❌ Select valid algorithm")
            return
        
        if not self.input_edit.text():
            QMessageBox.warning(self, "Error", "❌ Select input file")
            return
        
        try:
            decode_script = self.algorithms[algo_name]['decode']
            
            # Algorytm PDF wymaga -i, inne zwykle mają jako pozycyjny argument
            if "pdf" in algo_name.lower():
                cmd = [sys.executable, decode_script, "-i", self.input_edit.text()]
            else:
                cmd = [sys.executable, decode_script, self.input_edit.text()]
            
            if self.output_edit.text():
                cmd.extend(["-o", self.output_edit.text()])
            
            print(f"🔄 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                message = result.stdout.strip()
                self.result_text.setText(message)
                
                if self.output_edit.text():
                    QMessageBox.information(self, "Success", f"✅ Decoded successfully!\nSaved to: {self.output_edit.text()}")
                else:
                    QMessageBox.information(self, "Success", "✅ Decoded successfully!")
            else:
                QMessageBox.critical(self, "Error", f"❌ Decoding failed:\n{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Error: {str(e)}")

class HelpWindow(QMessageBox):
    """Okno pomocy"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.setIcon(QMessageBox.Icon.Information)
        
        help_text = """
<b>STEGANOGRAPHY GUI - Pomoc</b>

<b>Co to jest?</b>
Aplikacja do ukrywania tajnych wiadomości w plikach przy użyciu różnych algorytmów steganograficznych.

<b>Jak korzystać?</b>

<u>Zakładka ENCODE:</u>
1. Wybierz algorytm z listy
2. Wybierz źródło COVER TEXT:
   - File: załaduj plik .txt (zalecane)
   - Input: wpisz tekst bezpośrednio
3. Wybierz źródło SECRET MESSAGE:
   - File: załaduj plik .txt
   - Input: wpisz wiadomość bezpośrednio
4. Wpisz nazwę pliku wyjściowego
5. Kliknij ENCODE

<u>Zakładka DECODE:</u>
1. Wybierz algorytm (ten sam co przy encodowaniu!)
2. Załaduj plik zakodowany (stego_output)
3. Opcjonalnie: wskaż plik do zapisu wyniku
4. Kliknij DECODE

<b>Obsługiwane algorytmy:</b>
- Shift Position: przesunięcie pozycji tekstu
- Formatting Spaces: formatowanie spacji
- One Time Pad: szyfrowanie one-time pad
- Feature Coding: kodowanie cech znaków
- PDF Color: kodowanie w kolorach liter PDF

<b>Porady:</b>
- Zawsze używaj tego samego algorytmu do encode i decode
- Cover text musi być dłuższy niż secret message
- Dla PDF upewnij się, że masz zainstalowany: pip install PyMuPDF reportlab
- Wiadomości są bezpiecznie ukryte - okiem zwykłej osoby niewidoczne

<b>Błędy?</b>
- Sprawdź czy pliki istnieją
- Sprawdź czy wybrałeś algorytm
- Sprawdź czy cover text jest wystarczająco długi
"""
        
        self.setText(help_text)
        self.setMinimumWidth(600)

class MainWindow(QMainWindow):
    """Główne okno aplikacji"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steganography Tool")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Header
        title = QLabel("Steganography Application")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Tabs
        self.tabs = QTabWidget()
        self.encode_frame = EncodeFrame()
        self.decode_frame = DecodeFrame()
        self.tabs.addTab(self.encode_frame, "Encode")
        self.tabs.addTab(self.decode_frame, "Decode")
        layout.addWidget(self.tabs)
        
        # Help button (corner)
        help_layout = QHBoxLayout()
        help_layout.addStretch()
        help_btn = QPushButton("? Help")
        help_btn.setMaximumWidth(100)
        help_btn.clicked.connect(self.show_help)
        help_layout.addWidget(help_btn)
        layout.addLayout(help_layout)
        
        central_widget.setLayout(layout)
    
    def show_help(self):
        HelpWindow(self).exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

