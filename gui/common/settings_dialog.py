"""
Settings dialog for Starfish GUI
Equivalent to the Java GUISettings class
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QCheckBox, QComboBox,
                             QPushButton, QSpinBox, QFormLayout, QDialogButtonBox,
                             QFileDialog, QGroupBox)
from PyQt5.QtCore import Qt

from core.options import LogLevel


class SettingsDialog(QDialog):
    """Settings configuration dialog"""
    
    def __init__(self, options, parent=None):
        super().__init__(parent)
        self.options = options.clone()  # Work with a copy
        self.original_options = options
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_general_tab()
        self.create_builder_tab()
        self.create_runner_tab()
        self.create_viewer_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Create button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        
        layout.addWidget(button_box)
        
    def create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Working directory
        self.working_dir_edit = QLineEdit()
        wd_layout = QHBoxLayout()
        wd_layout.addWidget(self.working_dir_edit)
        
        browse_wd_btn = QPushButton("Browse...")
        browse_wd_btn.clicked.connect(self.browse_working_directory)
        wd_layout.addWidget(browse_wd_btn)
        
        layout.addRow("Working Directory:", wd_layout)
        
        # Max cores
        self.max_cores_spin = QSpinBox()
        self.max_cores_spin.setMinimum(1)
        self.max_cores_spin.setMaximum(64)
        layout.addRow("Max CPU Cores:", self.max_cores_spin)
        
        # Log level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems([level.value.title() for level in LogLevel])
        layout.addRow("Log Level:", self.log_level_combo)
        
        # Randomize
        self.randomize_check = QCheckBox("Enable randomization")
        layout.addRow(self.randomize_check)
        
        self.tab_widget.addTab(tab, "General")
        
    def create_builder_tab(self):
        """Create simulation builder settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Builder-specific settings would go here
        group = QGroupBox("Simulation File Builder")
        group_layout = QFormLayout(group)
        
        # Default template directory
        self.template_dir_edit = QLineEdit()
        template_layout = QHBoxLayout()
        template_layout.addWidget(self.template_dir_edit)
        
        browse_template_btn = QPushButton("Browse...")
        browse_template_btn.clicked.connect(self.browse_template_directory)
        template_layout.addWidget(browse_template_btn)
        
        group_layout.addRow("Template Directory:", template_layout)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Builder")
        
    def create_runner_tab(self):
        """Create simulation runner settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Runner-specific settings
        group = QGroupBox("Simulation Runner")
        group_layout = QFormLayout(group)
        
        # Auto-save interval
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setMinimum(0)
        self.autosave_spin.setMaximum(3600)
        self.autosave_spin.setSuffix(" seconds")
        group_layout.addRow("Auto-save Interval:", self.autosave_spin)
        
        # Show progress in title
        self.progress_title_check = QCheckBox("Show progress in window title")
        group_layout.addRow(self.progress_title_check)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Runner")
        
    def create_viewer_tab(self):
        """Create result viewer settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Viewer-specific settings
        group = QGroupBox("Result Viewer")
        group_layout = QFormLayout(group)
        
        # Default colormap
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(['viridis', 'plasma', 'inferno', 'magma', 'jet', 'rainbow'])
        group_layout.addRow("Default Colormap:", self.colormap_combo)
        
        # Auto-refresh
        self.auto_refresh_check = QCheckBox("Auto-refresh during simulation")
        group_layout.addRow(self.auto_refresh_check)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Viewer")
        
    def load_settings(self):
        """Load current settings into the dialog"""
        self.working_dir_edit.setText(str(self.options.working_directory))
        self.max_cores_spin.setValue(self.options.max_cores)
        
        # Set log level
        log_level_index = list(LogLevel).index(self.options.log_level)
        self.log_level_combo.setCurrentIndex(log_level_index)
        
        self.randomize_check.setChecked(self.options.randomize)
        
        # Set default values for other settings
        self.template_dir_edit.setText("")
        self.autosave_spin.setValue(60)
        self.progress_title_check.setChecked(True)
        self.colormap_combo.setCurrentText('viridis')
        self.auto_refresh_check.setChecked(True)
        
    def browse_working_directory(self):
        """Browse for working directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Working Directory", 
            str(self.options.working_directory)
        )
        if directory:
            self.working_dir_edit.setText(directory)
            
    def browse_template_directory(self):
        """Browse for template directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Template Directory", 
            self.template_dir_edit.text()
        )
        if directory:
            self.template_dir_edit.setText(directory)
            
    def apply_settings(self):
        """Apply settings without closing dialog"""
        self.save_settings()
        
    def accept_settings(self):
        """Accept and apply settings"""
        self.save_settings()
        self.accept()
        
    def save_settings(self):
        """Save settings from dialog to options"""
        from pathlib import Path
        
        # Update options
        self.options.working_directory = Path(self.working_dir_edit.text())
        self.options.max_cores = self.max_cores_spin.value()
        self.options.log_level = list(LogLevel)[self.log_level_combo.currentIndex()]
        self.options.randomize = self.randomize_check.isChecked()
        
        # Copy back to original options
        self.original_options.working_directory = self.options.working_directory
        self.original_options.max_cores = self.options.max_cores
        self.original_options.log_level = self.options.log_level
        self.original_options.randomize = self.options.randomize
