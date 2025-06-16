"""
About dialog for Starfish GUI
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont


class AboutDialog(QDialog):
    """About dialog showing application information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("About Starfish")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Starfish")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 0.22-Python")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        description = QTextEdit()
        description.setReadOnly(True)
        description.setHtml("""
        <h3>2D Plasma/Fluid Simulation Software</h3>
        <p><b>Starfish</b> is a 2D (Cartesian or axisymmetric) code for simulating 
        a wide range of plasma and gas problems. It implements the electrostatic 
        Particle-in-Cell (ES-PIC) method along with several fluid solvers.</p>
        
        <p><b>Features:</b></p>
        <ul>
        <li>Electrostatic Particle-in-Cell (ES-PIC) method</li>
        <li>Multiple fluid solvers</li>
        <li>Material interactions through MCC or DSMC collisions</li>
        <li>Chemical reactions support</li>
        <li>Multi-domain rectilinear or body-fitted meshes</li>
        <li>Linear/cubic spline surface geometry</li>
        <li>Plugin architecture for extensibility</li>
        </ul>
        
        <p><b>Copyright:</b> © 2012-2019, Particle In Cell Consulting LLC</p>
        <p><b>License:</b> Simplified BSD (Modified for Non-Commercial Use)</p>
        <p><b>Website:</b> <a href="https://www.particleincell.com/starfish">
        https://www.particleincell.com/starfish</a></p>
        
        <hr>
        <p><i>This Python GUI implementation maintains full compatibility with 
        the original Java version while eliminating VTK compilation issues.</i></p>
        """)
        layout.addWidget(description)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
