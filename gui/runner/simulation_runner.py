"""
Simulation Runner
Equivalent to the Java GUISimulationRunner class
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QProgressBar, QListWidget, QListWidgetItem,
                             QSplitter, QTextEdit, QFileDialog, QMessageBox,
                             QLabel, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor

import subprocess
import sys
import os
from pathlib import Path
import threading
import time


class SimulationWorker(QThread):
    """Worker thread for running simulations"""
    
    progress_updated = pyqtSignal(int)
    output_received = pyqtSignal(str)
    simulation_finished = pyqtSignal(int)  # exit code
    
    def __init__(self, simulation_file, options):
        super().__init__()
        self.simulation_file = simulation_file
        self.options = options
        self.process = None
        self.should_stop = False
        
    def run(self):
        """Run the simulation"""
        try:
            # Find the Java CLI jar file
            jar_file = self.find_starfish_jar()
            if not jar_file:
                error_msg = ("Error: StarfishCLI.jar not found!\n"
                           "Please ensure StarfishCLI.jar is in one of these locations:\n"
                           "- Current directory\n"
                           "- build/ directory\n"
                           "- dist/ directory\n"
                           "- target/ directory\n"
                           "- Working directory\n")
                self.output_received.emit(error_msg)
                self.simulation_finished.emit(-1)
                return

            # 确定工作目录和仿真文件
            sim_file_path = Path(self.simulation_file)
            if sim_file_path.is_absolute():
                working_dir = sim_file_path.parent
                sim_file_name = sim_file_path.name
            else:
                working_dir = self.options.working_directory
                sim_file_name = str(sim_file_path)

            # 构建命令 - 只传递仿真文件名（相对路径）
            cmd = ['java', '-jar', str(jar_file), sim_file_name]

            self.output_received.emit(f"Starting simulation: {' '.join(cmd)}\n")
            self.output_received.emit(f"Working directory: {working_dir}\n")
            self.output_received.emit(f"Simulation file: {sim_file_name}\n")

            # Start process in the correct working directory
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                cwd=str(working_dir)  # 设置工作目录
            )
            
            # Read output
            while True:
                if self.should_stop:
                    self.process.terminate()
                    break
                    
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                    
                if output:
                    self.output_received.emit(output)
                    
                    # Try to extract progress information
                    if "it:" in output:
                        try:
                            # Parse iteration info for progress
                            # Format: "it: 1234   Ar+: 0"
                            if "it:" in output:
                                parts = output.split()
                                for i, part in enumerate(parts):
                                    if part == "it:":
                                        current_it = int(parts[i + 1])
                                        # Estimate progress based on iteration count
                                        # Assume typical simulation runs 1000-5000 iterations
                                        if current_it <= 1000:
                                            progress = min(100, current_it // 10)
                                        elif current_it <= 5000:
                                            progress = min(100, 10 + (current_it - 1000) // 40)
                                        else:
                                            progress = min(100, 90 + (current_it - 5000) // 500)
                                        self.progress_updated.emit(progress)
                                        break
                        except:
                            pass
            
            # Get exit code
            exit_code = self.process.poll()
            self.simulation_finished.emit(exit_code or 0)
            
        except Exception as e:
            self.output_received.emit(f"Error running simulation: {e}\n")
            self.simulation_finished.emit(-1)
            
    def stop(self):
        """Stop the simulation"""
        self.should_stop = True
        if self.process:
            self.process.terminate()
            
    def find_starfish_jar(self):
        """Find the Starfish CLI jar file"""
        # Look in common locations
        possible_paths = [
            Path.cwd() / "StarfishCLI.jar",
            Path.cwd() / "build" / "StarfishCLI.jar",
            Path.cwd() / "dist" / "StarfishCLI.jar",
            Path.cwd() / "target" / "StarfishCLI.jar",
            Path.cwd().parent / "StarfishCLI.jar",  # Parent directory
            Path.cwd() / "lib" / "StarfishCLI.jar",  # Lib directory
        ]

        # Also check if it's in the working directory
        if hasattr(self.options, 'working_directory'):
            wd = Path(self.options.working_directory)
            possible_paths.extend([
                wd / "StarfishCLI.jar",
                wd / "build" / "StarfishCLI.jar",
                wd / "dist" / "StarfishCLI.jar",
            ])

        for path in possible_paths:
            if path.exists():
                return path

        # If not found, try to find any jar file that might be Starfish
        for jar_file in Path.cwd().glob("*.jar"):
            if "starfish" in jar_file.name.lower():
                return jar_file

        return None


class SimulationQueue(QListWidget):
    """Queue widget for managing simulation files"""
    
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(150)
        
    def add_simulation(self, file_path):
        """Add a simulation file to the queue"""
        item = QListWidgetItem(str(file_path))
        item.setData(Qt.UserRole, file_path)
        self.addItem(item)
        
    def get_next_simulation(self):
        """Get the next simulation from the queue"""
        if self.count() > 0:
            item = self.takeItem(0)
            return item.data(Qt.UserRole)
        return None
        
    def clear_queue(self):
        """Clear all items from the queue"""
        self.clear()


class SimulationRunner(QWidget):
    """Main simulation runner widget"""
    
    def __init__(self, options):
        super().__init__()
        self.options = options
        self.current_worker = None
        self.is_running_simulation = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Create main content area
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Queue and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right side: Console output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 9))
        self.console.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        splitter.addWidget(self.console)
        
        # Set splitter proportions
        splitter.setSizes([250, 550])
        
        layout.addWidget(splitter)
        
    def create_control_panel(self):
        """Create the main control panel"""
        group = QGroupBox("Simulation Control")
        layout = QHBoxLayout(group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(QLabel("Progress:"))
        layout.addWidget(self.progress_bar, 1)
        
        # Control buttons
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_simulation)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_simulation)
        self.pause_button.setEnabled(False)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        
        layout.addWidget(self.start_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)
        
        return group
        
    def create_left_panel(self):
        """Create the left control panel"""
        widget = QWidget()
        widget.setMaximumWidth(250)
        layout = QVBoxLayout(widget)
        
        # File management
        file_group = QGroupBox("Simulation Files")
        file_layout = QVBoxLayout(file_group)
        
        add_file_button = QPushButton("Add File to Queue")
        add_file_button.clicked.connect(self.add_file_to_queue)
        file_layout.addWidget(add_file_button)
        
        clear_queue_button = QPushButton("Clear Queue")
        clear_queue_button.clicked.connect(self.clear_queue)
        file_layout.addWidget(clear_queue_button)
        
        layout.addWidget(file_group)
        
        # Simulation queue
        queue_group = QGroupBox("Simulation Queue")
        queue_layout = QVBoxLayout(queue_group)
        
        self.simulation_queue = SimulationQueue()
        queue_layout.addWidget(self.simulation_queue)
        
        layout.addWidget(queue_group)
        
        # Status
        status_group = QGroupBox("Status")
        status_layout = QFormLayout(status_group)
        
        self.status_label = QLabel("Ready")
        self.current_file_label = QLabel("None")
        
        status_layout.addRow("Status:", self.status_label)
        status_layout.addRow("Current File:", self.current_file_label)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
        
        return widget
        
    def add_file_to_queue(self):
        """Add a simulation file to the queue"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Simulation File", 
            str(self.options.working_directory),
            "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            self.simulation_queue.add_simulation(Path(file_path))
            self.append_to_console(f"Added to queue: {file_path}\n")
            
    def clear_queue(self):
        """Clear the simulation queue"""
        self.simulation_queue.clear_queue()
        self.append_to_console("Queue cleared\n")
        
    def start_simulation(self):
        """Start running simulations from the queue"""
        if self.is_running_simulation:
            return
            
        next_sim = self.simulation_queue.get_next_simulation()
        if not next_sim:
            QMessageBox.information(self, "No Simulations", 
                                    "Please add simulation files to the queue first.")
            return
            
        self.is_running_simulation = True
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        self.status_label.setText("Running")
        self.current_file_label.setText(next_sim.name)
        
        # Clear console
        self.console.clear()
        
        # Start worker thread
        self.current_worker = SimulationWorker(next_sim, self.options)
        self.current_worker.progress_updated.connect(self.update_progress)
        self.current_worker.output_received.connect(self.append_to_console)
        self.current_worker.simulation_finished.connect(self.on_simulation_finished)
        self.current_worker.start()
        
    def pause_simulation(self):
        """Pause the current simulation"""
        # Note: True pausing is not easily implemented with subprocess
        # Instead, we'll provide a warning and suggest stopping
        reply = QMessageBox.question(
            self, "Pause Simulation",
            "Pausing is not supported for CLI simulations.\n"
            "Would you like to stop the simulation instead?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.stop_simulation()
        else:
            self.append_to_console("Note: Pause functionality not available for CLI simulations\n")
        
    def stop_simulation(self):
        """Stop the current simulation"""
        if self.current_worker:
            self.current_worker.stop()
            self.current_worker.wait()
            
        self.on_simulation_finished(-1)
        
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
        
    def append_to_console(self, text):
        """Append text to the console"""
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(text)
        self.console.moveCursor(QTextCursor.End)
        
    def on_simulation_finished(self, exit_code):
        """Handle simulation completion"""
        self.is_running_simulation = False
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        # Handle different exit codes
        # Note: Windows can return large unsigned values for negative exit codes
        if exit_code == 0:
            self.status_label.setText("Completed")
            self.append_to_console("\nSimulation completed successfully\n")
        elif exit_code == 4294967295:  # This is -1 as unsigned 32-bit
            self.status_label.setText("Completed with warnings")
            self.append_to_console("\nSimulation completed with warnings (output errors)\n")
        else:
            self.status_label.setText("Failed")
            self.append_to_console(f"\nSimulation failed with exit code {exit_code}\n")

        self.current_file_label.setText("None")
        self.progress_bar.setValue(100)  # Show completion

        # Check if there are more simulations in queue
        if self.simulation_queue.count() > 0:
            reply = QMessageBox.question(
                self, "Continue Queue",
                "There are more simulations in the queue. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                QTimer.singleShot(1000, self.start_simulation)  # Start next after 1 second
                
    def is_running(self):
        """Check if a simulation is currently running"""
        return self.is_running_simulation
