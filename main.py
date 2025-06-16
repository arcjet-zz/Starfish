#!/usr/bin/env python3
"""
Starfish GUI - Python Implementation
A 2D plasma/fluid simulation GUI using PyQt5 and VTK

This is a Python reimplementation of the original Java Starfish GUI,
maintaining full feature compatibility while eliminating VTK compilation issues.
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import StarfishMainWindow
from core.options import Options


def main():
    """Main entry point for Starfish GUI"""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Starfish")
    app.setApplicationVersion("0.22-Python")
    app.setOrganizationName("Particle In Cell Consulting LLC")
    
    # Set application icon
    icon_path = project_root / "resources" / "starfish-100.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Parse command line options
    options = Options(sys.argv[1:])
    
    # Create and show main window
    main_window = StarfishMainWindow(options)
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
