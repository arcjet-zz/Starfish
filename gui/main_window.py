"""
Main window for Starfish GUI
Equivalent to the Java GUI.java class
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QButtonGroup, QStackedWidget, 
                             QSplitter, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

from .builder.simulation_file_builder import SimulationFileBuilder
from .runner.simulation_runner import SimulationRunner
from .viewer.simulation_result_viewer import SimulationResultViewer
from .common.settings_dialog import SettingsDialog
from .common.about_dialog import AboutDialog


class StarfishMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, options):
        super().__init__()
        self.options = options
        self.settings_dialog = None
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Starfish 0.22-Python")
        self.setMinimumSize(800, 600)
        self.resize(1024, 768)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create side panel
        self.side_panel = self.create_side_panel()
        
        # Create main content area
        self.content_stack = QStackedWidget()
        
        # Create the three main panels
        self.simulation_builder = SimulationFileBuilder()
        self.simulation_runner = SimulationRunner(self.options)
        self.result_viewer = SimulationResultViewer(self.simulation_runner)
        
        # Add panels to stack
        self.content_stack.addWidget(self.simulation_builder)
        self.content_stack.addWidget(self.simulation_runner)
        self.content_stack.addWidget(self.result_viewer)
        
        # Add to main layout
        main_layout.addWidget(self.side_panel)
        main_layout.addWidget(self.content_stack, 1)  # Give content area more space
        
        # Show simulation builder by default
        self.show_simulation_builder()
        
    def create_side_panel(self):
        """Create the side navigation panel"""
        side_widget = QWidget()
        side_widget.setFixedWidth(200)  # 增加宽度从150到200
        side_widget.setStyleSheet("background-color: #f0f0f0;")

        layout = QVBoxLayout(side_widget)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create button group for exclusive selection
        self.nav_button_group = QButtonGroup()
        
        # Navigation buttons
        self.build_button = QPushButton("Build Sim File")
        self.build_button.setCheckable(True)
        self.build_button.setMinimumHeight(50)  # 增加高度
        self.build_button.setMinimumWidth(180)  # 设置最小宽度

        self.run_button = QPushButton("Run Simulation")
        self.run_button.setCheckable(True)
        self.run_button.setMinimumHeight(50)
        self.run_button.setMinimumWidth(180)

        self.view_button = QPushButton("View Results")
        self.view_button.setCheckable(True)
        self.view_button.setMinimumHeight(50)
        self.view_button.setMinimumWidth(180)
        
        # Add buttons to group
        self.nav_button_group.addButton(self.build_button, 0)
        self.nav_button_group.addButton(self.run_button, 1)
        self.nav_button_group.addButton(self.view_button, 2)
        
        # Add buttons to layout
        layout.addWidget(self.build_button)
        layout.addWidget(self.run_button)
        layout.addWidget(self.view_button)
        
        # Add spacer
        layout.addStretch()
        
        # Settings and About buttons
        self.settings_button = QPushButton("Settings")
        self.settings_button.setMinimumHeight(50)
        self.settings_button.setMinimumWidth(180)

        self.about_button = QPushButton("About")
        self.about_button.setMinimumHeight(50)
        self.about_button.setMinimumWidth(180)
        
        layout.addWidget(self.settings_button)
        layout.addWidget(self.about_button)
        
        return side_widget
        
    def setup_connections(self):
        """Setup signal-slot connections"""
        self.nav_button_group.buttonClicked.connect(self.on_nav_button_clicked)
        self.settings_button.clicked.connect(self.show_settings)
        self.about_button.clicked.connect(self.show_about)

        # Set default selection
        self.build_button.setChecked(True)
        self.content_stack.setCurrentIndex(0)

    def on_nav_button_clicked(self, button):
        """Handle navigation button clicks"""
        button_id = self.nav_button_group.id(button)
        self.content_stack.setCurrentIndex(button_id)

        # Update window title based on current panel
        panel_names = ["Build Simulation File", "Run Simulation", "View Results"]
        if 0 <= button_id < len(panel_names):
            self.setWindowTitle(f"Starfish 0.22-Python - {panel_names[button_id]}")
        
    def show_simulation_builder(self):
        """Show the simulation file builder"""
        self.build_button.setChecked(True)
        self.content_stack.setCurrentIndex(0)
        
    def show_simulation_runner(self):
        """Show the simulation runner"""
        self.run_button.setChecked(True)
        self.content_stack.setCurrentIndex(1)
        
    def show_result_viewer(self):
        """Show the result viewer"""
        self.view_button.setChecked(True)
        self.content_stack.setCurrentIndex(2)
        
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.options, self)
        if dialog.exec_() == QDialog.Accepted:
            # Settings were applied, update components if needed
            self.simulation_runner.options = self.options
            self.statusBar().showMessage("Settings updated", 2000)
        
    def show_about(self):
        """Show about dialog"""
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Check if simulation is running
        if hasattr(self.simulation_runner, 'is_running') and self.simulation_runner.is_running():
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                'A simulation is currently running. Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.simulation_runner.stop_simulation()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
