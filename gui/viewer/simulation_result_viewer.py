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
        self.reader = None  # Store the VTK reader
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
        
    def load_vts_file(self, file_path, selected_field=None):
        """Load a VTS (VTK Structured Grid) file"""
        try:
            file_ext = Path(file_path).suffix.lower()

            # Choose appropriate reader based on file extension
            if file_ext == '.vts':
                self.reader = vtk.vtkXMLStructuredGridReader()
            elif file_ext == '.vtr':
                self.reader = vtk.vtkXMLRectilinearGridReader()
            elif file_ext == '.vtp':
                self.reader = vtk.vtkXMLPolyDataReader()
            elif file_ext == '.vtk':
                self.reader = vtk.vtkDataSetReader()
            else:
                print(f"Unsupported file format: {file_ext}")
                return False

            self.reader.SetFileName(str(file_path))
            self.reader.Update()

            # Get data
            data = self.reader.GetOutput()

            if data.GetNumberOfPoints() == 0:
                print("Warning: No data points found in file")
                return False

            # Print available arrays for debugging
            point_data = data.GetPointData()
            print(f"Available arrays: {[point_data.GetArrayName(i) for i in range(point_data.GetNumberOfArrays())]}")

            # Clear previous actors
            self.renderer.RemoveAllViewProps()

            # Set the active scalar field (like Java version)
            if selected_field and point_data.GetArray(selected_field):
                point_data.SetActiveScalars(selected_field)
                print(f"Set active scalar to: {selected_field}")
            elif point_data.GetNumberOfArrays() > 0:
                # Use the first available array
                first_array_name = point_data.GetArrayName(0)
                point_data.SetActiveScalars(first_array_name)
                print(f"Set active scalar to first array: {first_array_name}")

            # Force update the data
            data.Modified()

            # Use the same approach as Java version - simple DataSetMapper
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputData(data)

            # Enable scalar visibility and set scalar mode (like Java version)
            mapper.SetScalarVisibility(1)  # Use 1 instead of True for compatibility
            mapper.SetScalarModeToUsePointData()
            mapper.SetColorModeToMapScalars()

            # Set scalar range if data has scalars
            if point_data.GetNumberOfArrays() > 0:
                active_array = point_data.GetScalars()
                if active_array:
                    scalar_range = active_array.GetRange()
                    mapper.SetScalarRange(scalar_range)
                    print(f"Scalar range: {scalar_range}")
                    print(f"Active scalar array name: {active_array.GetName()}")
                    print(f"Mapper scalar visibility: {mapper.GetScalarVisibility()}")
                    print(f"Mapper scalar mode: {mapper.GetScalarMode()}")
                else:
                    print("Warning: No active scalar array found!")
            else:
                print("Warning: No point data arrays found!")

            # Create and configure lookup table (like Java version)
            lut = vtk.vtkLookupTable()
            lut.SetHueRange(0.667, 0.0)  # Blue to red
            lut.SetSaturationRange(1.0, 1.0)
            lut.SetValueRange(1.0, 1.0)
            lut.SetNumberOfColors(256)

            # Set the table range to match the data range
            if point_data.GetNumberOfArrays() > 0:
                active_array = point_data.GetScalars()
                if active_array:
                    scalar_range = active_array.GetRange()
                    lut.SetTableRange(scalar_range)
                    print(f"Set lookup table range to: {scalar_range}")

            lut.Build()

            mapper.SetLookupTable(lut)
            # Don't use SetUseLookupTableScalarRange, let mapper handle the range
            # mapper.SetUseLookupTableScalarRange(1)

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            # Add to renderer
            self.renderer.AddActor(actor)

            # Add scalar bar for color legend (like Java version)
            scalar_bar = vtk.vtkScalarBarActor()
            scalar_bar.SetLookupTable(lut)
            scalar_bar.SetTitle(selected_field if selected_field else "Value")
            scalar_bar.SetNumberOfLabels(4)  # Use 4 like Java version
            scalar_bar.SetPosition(0.85, 0.1)
            scalar_bar.SetWidth(0.1)
            scalar_bar.SetHeight(0.8)
            self.renderer.AddActor2D(scalar_bar)

            # Set up proper camera for 2D data
            self.setup_optimal_camera(data)

            # Set background color like Java version
            self.renderer.SetBackground(0.5, 0.5, 0.5)  # Gray background like Java

            # Render
            self.render_window.Render()

            print(f"Successfully loaded {file_path} with {data.GetNumberOfPoints()} points")
            return True

        except Exception as e:
            print(f"Error loading VTK file: {e}")
            return False
            
    def setup_optimal_camera(self, data):
        """Setup optimal camera view for the data"""
        try:
            bounds = data.GetBounds()
            dims = [data.GetDimensions()[i] for i in range(3)]  # Avoid deprecation warning

            # Calculate data properties
            x_range = bounds[1] - bounds[0]
            y_range = bounds[3] - bounds[2]
            z_range = bounds[5] - bounds[4]

            center = [
                (bounds[0] + bounds[1]) / 2,
                (bounds[2] + bounds[3]) / 2,
                (bounds[4] + bounds[5]) / 2
            ]

            print(f"Data bounds: X[{bounds[0]:.3f}, {bounds[1]:.3f}], Y[{bounds[2]:.3f}, {bounds[3]:.3f}], Z[{bounds[4]:.3f}, {bounds[5]:.3f}]")
            print(f"Data ranges: X={x_range:.3f}, Y={y_range:.3f}, Z={z_range:.3f}")
            print(f"Data center: [{center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f}]")

            camera = self.camera

            # Check if this is 2D data (Z dimension = 1 or Z range very small)
            is_2d = dims[2] == 1 or z_range < 1e-6

            if is_2d:
                print("Setting up 2D camera view")

                # For 2D data, position camera above looking down
                max_range = max(x_range, y_range)

                # Position camera above the center, looking down
                camera_distance = max_range * 2  # Ensure we're far enough
                camera_pos = [center[0], center[1], center[2] + camera_distance]

                camera.SetPosition(camera_pos)
                camera.SetFocalPoint(center)
                camera.SetViewUp(0, 1, 0)  # Y-axis points up

                # Use parallel projection for 2D (no perspective distortion)
                camera.ParallelProjectionOn()

                # Set parallel scale to show the entire data with some margin
                margin_factor = 1.1  # 10% margin
                parallel_scale = max_range * margin_factor / 2
                camera.SetParallelScale(parallel_scale)

                print(f"2D camera setup: position={camera_pos}, parallel_scale={parallel_scale:.3f}")

            else:
                print("Setting up 3D camera view")

                # For 3D data, use perspective projection and reset camera
                camera.ParallelProjectionOff()
                self.renderer.ResetCamera()

                # Adjust the camera to show all data with some margin
                camera.Zoom(0.8)  # Zoom out a bit to add margin

            print(f"Final camera: position={camera.GetPosition()}, focal_point={camera.GetFocalPoint()}")
            print(f"Camera distance: {camera.GetDistance():.3f}")
            if camera.GetParallelProjection():
                print(f"Parallel scale: {camera.GetParallelScale():.3f}")
            else:
                print(f"View angle: {camera.GetViewAngle():.1f} degrees")

        except Exception as e:
            print(f"Error setting up camera: {e}")
            # Fallback to default
            self.renderer.ResetCamera()

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
            self.load_and_update_everything(file_path)
            self.setWindowTitle(f"Result Viewer - {Path(file_path).name}")
                
    def show_current_simulation(self):
        """Show results from the currently running simulation"""
        if not self.simulation_runner or not self.simulation_runner.is_running():
            QMessageBox.information(self, "No Simulation",
                                    "No simulation is currently running.")
            return

        # Try to find the most recent output files from the simulation
        try:
            output_files = self.find_simulation_output_files()
            if output_files:
                # Load the most recent file
                latest_file = max(output_files, key=lambda f: f.stat().st_mtime)
                self.load_and_update_everything(str(latest_file))

                # Enable auto-refresh if not already enabled
                if not self.auto_refresh_action.isChecked():
                    self.auto_refresh_action.setChecked(True)
                    self.toggle_auto_refresh(True)

                QMessageBox.information(self, "Live Viewing",
                                        f"Now viewing: {latest_file.name}\n"
                                        "Auto-refresh is enabled to show updates.")
            else:
                QMessageBox.information(self, "No Output Files",
                                        "No VTS output files found from the current simulation.\n"
                                        "Make sure your simulation is configured to output VTK files.")
        except Exception as e:
            QMessageBox.warning(self, "Error",
                                f"Failed to load simulation output: {str(e)}")

    def find_simulation_output_files(self):
        """Find VTS files from the current simulation"""
        output_files = []

        # Get the current simulation's working directory
        if hasattr(self.simulation_runner, 'current_worker') and self.simulation_runner.current_worker:
            # Get the directory where the simulation is running
            sim_file = self.simulation_runner.current_worker.simulation_file
            sim_dir = sim_file.parent

            # Look for VTS files in common output directories
            search_dirs = [
                sim_dir,
                sim_dir / "results",
                sim_dir / "output",
                sim_dir / "vtk"
            ]

            for search_dir in search_dirs:
                if search_dir.exists():
                    # Find all VTS files
                    vts_files = list(search_dir.glob("*.vts"))
                    output_files.extend(vts_files)

                    # Also look for numbered VTS files (animation frames)
                    numbered_vts = list(search_dir.glob("*_[0-9]*.vts"))
                    output_files.extend(numbered_vts)

        return output_files

    def load_and_update_everything(self, file_path):
        """Load a VTS file and update the visualization"""
        try:
            # Store the current file (ensure it's a string)
            self.current_file = str(file_path)

            # Update the settings based on the loaded file first
            self.update_field_choices()

            # Get the selected field
            selected_field = self.settings_widget.field_combo.currentText()

            # Load the file into VTK with the selected field
            self.vtk_widget.load_vts_file(self.current_file, selected_field)

            # Apply current settings
            self.on_settings_changed()

        except Exception as e:
            QMessageBox.warning(self, "Load Error",
                                f"Failed to load file {file_path}:\n{str(e)}")

    def update_field_choices(self):
        """Update the field choices in the settings panel based on loaded data"""
        try:
            # Get available fields from the VTK data
            if hasattr(self.vtk_widget, 'reader') and self.vtk_widget.reader:
                reader = self.vtk_widget.reader
                reader.Update()

                # Get point data arrays
                point_data = reader.GetOutput().GetPointData()
                num_arrays = point_data.GetNumberOfArrays()

                field_names = []
                for i in range(num_arrays):
                    array_name = point_data.GetArrayName(i)
                    if array_name:
                        field_names.append(array_name)

                # Update the field combo box
                current_field = self.settings_widget.field_combo.currentText()
                self.settings_widget.field_combo.clear()
                self.settings_widget.field_combo.addItems(field_names)

                # Try to restore the previous selection
                if current_field in field_names:
                    self.settings_widget.field_combo.setCurrentText(current_field)
                elif field_names:
                    self.settings_widget.field_combo.setCurrentIndex(0)

        except Exception as e:
            print(f"Warning: Could not update field choices: {e}")

    def toggle_auto_refresh(self, enabled):
        """Toggle auto refresh"""
        if enabled:
            self.auto_refresh_timer.start(2000)  # Refresh every 2 seconds
        else:
            self.auto_refresh_timer.stop()
            
    def refresh_view(self):
        """Refresh the current view"""
        if self.current_file:
            current_path = Path(self.current_file) if isinstance(self.current_file, str) else self.current_file
            if current_path.exists():
                # Get the currently selected field
                selected_field = self.settings_widget.field_combo.currentText()
                self.vtk_widget.load_vts_file(str(current_path), selected_field)
            
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
            # Reload the file with the selected field
            self.vtk_widget.load_vts_file(self.current_file, field)

            # Apply opacity
            actors = self.vtk_widget.renderer.GetActors()
            actors.InitTraversal()
            actor = actors.GetNextItem()
            while actor:
                if hasattr(actor, 'GetProperty'):  # Check if it's a 3D actor
                    actor.GetProperty().SetOpacity(opacity)
                actor = actors.GetNextItem()

            # Apply colormap
            self.apply_colormap(colormap)

            # Render with new settings
            self.vtk_widget.render_window.Render()

        except Exception as e:
            print(f"Error applying settings: {e}")

    def apply_colormap(self, colormap_name):
        """Apply the selected colormap"""
        try:
            # Get the mapper from the current actor
            actors = self.vtk_widget.renderer.GetActors()
            actors.InitTraversal()
            actor = actors.GetNextItem()

            if actor and hasattr(actor, 'GetMapper'):
                mapper = actor.GetMapper()
                if mapper:
                    # Create lookup table based on colormap selection
                    lut = vtk.vtkLookupTable()
                    lut.SetNumberOfColors(256)

                    if colormap_name == 'viridis':
                        lut.SetHueRange(0.667, 0.0)  # Blue to red
                    elif colormap_name == 'plasma':
                        lut.SetHueRange(0.8, 0.0)   # Purple to yellow
                    elif colormap_name == 'jet':
                        lut.SetHueRange(0.667, 0.0) # Blue to red (classic jet)
                    elif colormap_name == 'rainbow':
                        lut.SetHueRange(0.0, 0.667) # Red to blue
                    else:  # Default to viridis
                        lut.SetHueRange(0.667, 0.0)

                    lut.SetSaturationRange(1.0, 1.0)
                    lut.SetValueRange(1.0, 1.0)
                    lut.Build()

                    mapper.SetLookupTable(lut)

        except Exception as e:
            print(f"Error applying colormap: {e}")

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
