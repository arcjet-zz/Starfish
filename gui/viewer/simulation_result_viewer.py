"""
Simulation Result Viewer
Equivalent to the Java SimulationResultViewer class
Uses VTK for 3D visualization
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QToolBar, QAction, QFileDialog, QMessageBox,
                             QGroupBox, QFormLayout, QComboBox, QCheckBox,
                             QSlider, QLabel, QPushButton, QSpinBox,
                             QDoubleSpinBox, QColorDialog, QTabWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET


class VTKVisualizationWidget(QWidget):
    """Widget containing VTK visualization"""
    
    def __init__(self):
        super().__init__()
        self.init_vtk()
        
    def init_vtk(self):
        """Initialize VTK components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget)
        
        # Create renderer
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.1, 0.1, 0.2)  # Dark blue background
        
        # Create render window
        self.render_window = self.vtk_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        
        # Create interactor
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        
        # Set up camera
        self.camera = self.renderer.GetActiveCamera()
        self.camera.SetPosition(0, 0, 10)
        self.camera.SetFocalPoint(0, 0, 0)
        self.camera.SetViewUp(0, 1, 0)
        
        # Initialize interactor
        self.interactor.Initialize()
        self.interactor.Start()
        
    def load_vts_file(self, file_path):
        """Load a VTS (VTK Structured Grid) file"""
        try:
            file_ext = Path(file_path).suffix.lower()

            # Choose appropriate reader based on file extension
            if file_ext == '.vts':
                reader = vtk.vtkXMLStructuredGridReader()
            elif file_ext == '.vtr':
                reader = vtk.vtkXMLRectilinearGridReader()
            elif file_ext == '.vtp':
                reader = vtk.vtkXMLPolyDataReader()
            elif file_ext == '.vtk':
                reader = vtk.vtkDataSetReader()
            else:
                print(f"Unsupported file format: {file_ext}")
                return False

            reader.SetFileName(str(file_path))
            reader.Update()

            # Get data
            data = reader.GetOutput()

            if data.GetNumberOfPoints() == 0:
                print("Warning: No data points found in file")
                return False

            # Clear previous actors
            self.renderer.RemoveAllViewProps()

            # Create mapper and actor
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputData(data)

            # Set scalar range if data has scalars
            if data.GetPointData().GetNumberOfArrays() > 0:
                scalar_range = data.GetPointData().GetArray(0).GetRange()
                mapper.SetScalarRange(scalar_range)

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            # Add to renderer
            self.renderer.AddActor(actor)

            # Reset camera
            self.renderer.ResetCamera()

            # Render
            self.render_window.Render()

            print(f"Successfully loaded {file_path} with {data.GetNumberOfPoints()} points")
            return True

        except Exception as e:
            print(f"Error loading VTK file: {e}")
            return False
            
    def clear_visualization(self):
        """Clear the visualization"""
        self.renderer.RemoveAllViewProps()
        self.render_window.Render()


class ViewerSettings(QWidget):
    """Settings panel for the viewer"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setMaximumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Create tabs
        tab_widget = QTabWidget()
        
        # Display tab
        display_tab = self.create_display_tab()
        tab_widget.addTab(display_tab, "Display")
        
        # Colormap tab
        colormap_tab = self.create_colormap_tab()
        tab_widget.addTab(colormap_tab, "Colormap")
        
        # Animation tab
        animation_tab = self.create_animation_tab()
        tab_widget.addTab(animation_tab, "Animation")
        
        layout.addWidget(tab_widget)
        layout.addStretch()
        
    def create_display_tab(self):
        """Create display settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Field selection
        self.field_combo = QComboBox()
        self.field_combo.addItems(['phi', 'rho', 'nd.O+', 'efi', 'efj'])
        self.field_combo.currentTextChanged.connect(self.settings_changed.emit)
        layout.addRow("Field:", self.field_combo)
        
        # Show mesh
        self.show_mesh_check = QCheckBox()
        self.show_mesh_check.toggled.connect(self.settings_changed.emit)
        layout.addRow("Show Mesh:", self.show_mesh_check)
        
        # Show boundaries
        self.show_boundaries_check = QCheckBox()
        self.show_boundaries_check.setChecked(True)
        self.show_boundaries_check.toggled.connect(self.settings_changed.emit)
        layout.addRow("Show Boundaries:", self.show_boundaries_check)
        
        # Opacity
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.settings_changed.emit)
        layout.addRow("Opacity:", self.opacity_slider)
        
        return widget
        
    def create_colormap_tab(self):
        """Create colormap settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Colormap selection
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(['viridis', 'plasma', 'inferno', 'magma', 'jet', 'rainbow'])
        self.colormap_combo.currentTextChanged.connect(self.settings_changed.emit)
        layout.addRow("Colormap:", self.colormap_combo)
        
        # Auto range
        self.auto_range_check = QCheckBox()
        self.auto_range_check.setChecked(True)
        self.auto_range_check.toggled.connect(self.settings_changed.emit)
        layout.addRow("Auto Range:", self.auto_range_check)
        
        # Min value
        self.min_value_spin = QDoubleSpinBox()
        self.min_value_spin.setMinimum(-1e10)
        self.min_value_spin.setMaximum(1e10)
        self.min_value_spin.valueChanged.connect(self.settings_changed.emit)
        layout.addRow("Min Value:", self.min_value_spin)
        
        # Max value
        self.max_value_spin = QDoubleSpinBox()
        self.max_value_spin.setMinimum(-1e10)
        self.max_value_spin.setMaximum(1e10)
        self.max_value_spin.setValue(1.0)
        self.max_value_spin.valueChanged.connect(self.settings_changed.emit)
        layout.addRow("Max Value:", self.max_value_spin)
        
        return widget
        
    def create_animation_tab(self):
        """Create animation settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Animation controls
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        
        layout.addRow("Controls:", button_layout)
        
        # Frame rate
        self.frame_rate_spin = QSpinBox()
        self.frame_rate_spin.setMinimum(1)
        self.frame_rate_spin.setMaximum(60)
        self.frame_rate_spin.setValue(10)
        layout.addRow("Frame Rate (fps):", self.frame_rate_spin)
        
        # Current frame
        self.current_frame_spin = QSpinBox()
        self.current_frame_spin.setMinimum(0)
        self.current_frame_spin.setMaximum(1000)
        layout.addRow("Current Frame:", self.current_frame_spin)
        
        return widget


class SimulationResultViewer(QWidget):
    """Main result viewer widget"""
    
    def __init__(self, simulation_runner=None):
        super().__init__()
        self.simulation_runner = simulation_runner
        self.current_file = None
        self.auto_refresh_timer = QTimer()
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create toolbar
        self.create_toolbar()
        layout.addWidget(self.toolbar)
        
        # Create main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: VTK visualization
        self.vtk_widget = VTKVisualizationWidget()
        splitter.addWidget(self.vtk_widget)
        
        # Right side: Settings
        self.settings_widget = ViewerSettings()
        splitter.addWidget(self.settings_widget)
        
        # Set splitter proportions
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
        
    def create_toolbar(self):
        """Create the toolbar"""
        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Load file
        load_action = QAction("Load File", self)
        load_action.triggered.connect(self.load_file)
        self.toolbar.addAction(load_action)
        
        # Show current simulation
        show_current_action = QAction("Show Current Sim", self)
        show_current_action.triggered.connect(self.show_current_simulation)
        self.toolbar.addAction(show_current_action)
        
        self.toolbar.addSeparator()
        
        # Auto refresh
        self.auto_refresh_action = QAction("Auto Refresh", self)
        self.auto_refresh_action.setCheckable(True)
        self.auto_refresh_action.toggled.connect(self.toggle_auto_refresh)
        self.toolbar.addAction(self.auto_refresh_action)
        
        # Refresh
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_view)
        self.toolbar.addAction(refresh_action)

        self.toolbar.addSeparator()

        # Generate test data
        test_data_action = QAction("Generate Test Data", self)
        test_data_action.triggered.connect(self.generate_test_data)
        self.toolbar.addAction(test_data_action)
        
    def setup_connections(self):
        """Setup signal-slot connections"""
        self.settings_widget.settings_changed.connect(self.on_settings_changed)
        self.auto_refresh_timer.timeout.connect(self.refresh_view)
        
    def load_file(self):
        """Load a result file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Result File", "",
            "VTK Files (*.vts *.vtr *.vtp);;All Files (*)"
        )
        
        if file_path:
            self.current_file = Path(file_path)
            success = self.vtk_widget.load_vts_file(self.current_file)
            
            if success:
                self.setWindowTitle(f"Result Viewer - {self.current_file.name}")
            else:
                QMessageBox.critical(self, "Error", 
                                     f"Failed to load file: {self.current_file}")
                
    def show_current_simulation(self):
        """Show results from the currently running simulation"""
        if not self.simulation_runner or not self.simulation_runner.is_running():
            QMessageBox.information(self, "No Simulation", 
                                    "No simulation is currently running.")
            return
            
        # This would need to interface with the actual simulation
        # to get the current output files
        QMessageBox.information(self, "Not Implemented", 
                                "Live simulation viewing not yet implemented.")
        
    def toggle_auto_refresh(self, enabled):
        """Toggle auto refresh"""
        if enabled:
            self.auto_refresh_timer.start(2000)  # Refresh every 2 seconds
        else:
            self.auto_refresh_timer.stop()
            
    def refresh_view(self):
        """Refresh the current view"""
        if self.current_file and self.current_file.exists():
            self.vtk_widget.load_vts_file(self.current_file)
            
    def on_settings_changed(self):
        """Handle settings changes"""
        if not self.current_file:
            return

        # Get current settings
        field = self.settings_widget.field_combo.currentText()
        show_mesh = self.settings_widget.show_mesh_check.isChecked()
        show_boundaries = self.settings_widget.show_boundaries_check.isChecked()
        opacity = self.settings_widget.opacity_slider.value() / 100.0
        colormap = self.settings_widget.colormap_combo.currentText()

        # Apply settings to visualization
        try:
            # Reload the file with new settings
            self.vtk_widget.load_vts_file(self.current_file)

            # Apply opacity
            actors = self.vtk_widget.renderer.GetActors()
            actors.InitTraversal()
            actor = actors.GetNextItem()
            while actor:
                actor.GetProperty().SetOpacity(opacity)
                actor = actors.GetNextItem()

            # Render with new settings
            self.vtk_widget.render_window.Render()

        except Exception as e:
            print(f"Error applying settings: {e}")

    def generate_test_data(self):
        """Generate test VTK data for demonstration"""
        try:
            # Create a simple structured grid with test data
            grid = vtk.vtkStructuredGrid()

            # Create points
            points = vtk.vtkPoints()
            nx, ny, nz = 20, 20, 1

            for k in range(nz):
                for j in range(ny):
                    for i in range(nx):
                        x = i * 0.1
                        y = j * 0.1
                        z = k * 0.1
                        points.InsertNextPoint(x, y, z)

            grid.SetDimensions(nx, ny, nz)
            grid.SetPoints(points)

            # Create scalar data (potential field)
            phi_array = vtk.vtkFloatArray()
            phi_array.SetName("phi")
            phi_array.SetNumberOfComponents(1)

            # Create density data
            rho_array = vtk.vtkFloatArray()
            rho_array.SetName("rho")
            rho_array.SetNumberOfComponents(1)

            # Generate test data
            import math
            for k in range(nz):
                for j in range(ny):
                    for i in range(nx):
                        x = i * 0.1
                        y = j * 0.1

                        # Potential: simple quadratic
                        phi = -(x*x + y*y) * 10
                        phi_array.InsertNextValue(phi)

                        # Density: Gaussian distribution
                        r2 = (x-1.0)**2 + (y-1.0)**2
                        rho = math.exp(-r2/0.2) * 1e12
                        rho_array.InsertNextValue(rho)

            # Add arrays to grid
            grid.GetPointData().AddArray(phi_array)
            grid.GetPointData().AddArray(rho_array)
            grid.GetPointData().SetActiveScalars("phi")

            # Clear previous actors
            self.vtk_widget.renderer.RemoveAllViewProps()

            # Create mapper and actor
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputData(grid)
            mapper.SetScalarRange(phi_array.GetRange())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            # Add to renderer
            self.vtk_widget.renderer.AddActor(actor)

            # Reset camera
            self.vtk_widget.renderer.ResetCamera()

            # Render
            self.vtk_widget.render_window.Render()

            QMessageBox.information(self, "Test Data Generated",
                                    "Test plasma data has been generated and displayed.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate test data: {e}")
            print(f"Error generating test data: {e}")
