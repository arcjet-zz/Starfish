"""
Simulation File Builder
Equivalent to the Java SimulationFileBuilder class
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QScrollArea,
                             QToolBar, QAction, QFileDialog, QMessageBox,
                             QFormLayout, QLineEdit, QComboBox, QSpinBox,
                             QDoubleSpinBox, QCheckBox, QTextEdit, QPushButton,
                             QGroupBox, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

import xml.etree.ElementTree as ET
from pathlib import Path


class SimulationFileBuilder(QWidget):
    """GUI for building Starfish simulation XML files"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.simulation_tree = None
        self.init_ui()
        self.create_default_simulation()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create toolbar
        self.create_toolbar()
        layout.addWidget(self.toolbar)
        
        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Tree view
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Simulation Structure")
        self.tree_widget.setMinimumWidth(200)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        splitter.addWidget(self.tree_widget)
        
        # Right side: Property editor
        self.property_scroll = QScrollArea()
        self.property_scroll.setWidgetResizable(True)
        self.property_scroll.setMinimumWidth(300)
        splitter.addWidget(self.property_scroll)
        
        # Set splitter proportions
        splitter.setSizes([200, 500])
        
        layout.addWidget(splitter)
        
    def create_toolbar(self):
        """Create the toolbar"""
        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # New file
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        self.toolbar.addAction(new_action)
        
        # Open file
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        self.toolbar.addAction(open_action)
        
        # Save file
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        self.toolbar.addAction(save_action)
        
        # Save as
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        self.toolbar.addAction(save_as_action)
        
        self.toolbar.addSeparator()
        
        # Add section
        add_action = QAction("Add Section", self)
        add_action.triggered.connect(self.add_section)
        self.toolbar.addAction(add_action)
        
        # Remove section
        remove_action = QAction("Remove Section", self)
        remove_action.triggered.connect(self.remove_section)
        self.toolbar.addAction(remove_action)

        self.toolbar.addSeparator()

        # Templates
        template_action = QAction("Load Template", self)
        template_action.triggered.connect(self.load_template)
        self.toolbar.addAction(template_action)
        
    def create_default_simulation(self):
        """Create a default simulation structure"""
        self.simulation_tree = ET.Element("simulation")
        
        # Add basic structure
        note = ET.SubElement(self.simulation_tree, "note")
        note.text = "New Starfish Simulation"
        
        log = ET.SubElement(self.simulation_tree, "log")
        log.set("level", "info")
        
        time = ET.SubElement(self.simulation_tree, "time")
        num_it = ET.SubElement(time, "num_it")
        num_it.text = "1000"
        dt = ET.SubElement(time, "dt")
        dt.text = "1e-6"
        
        # Update tree view
        self.update_tree_view()
        
    def update_tree_view(self):
        """Update the tree widget from the XML structure"""
        self.tree_widget.clear()
        
        if self.simulation_tree is not None:
            root_item = QTreeWidgetItem(self.tree_widget)
            root_item.setText(0, "simulation")
            root_item.setData(0, Qt.UserRole, self.simulation_tree)
            
            self.add_xml_children(self.simulation_tree, root_item)
            
            self.tree_widget.expandAll()
            
    def add_xml_children(self, xml_element, tree_item):
        """Recursively add XML children to tree"""
        for child in xml_element:
            child_item = QTreeWidgetItem(tree_item)
            child_item.setText(0, child.tag)
            child_item.setData(0, Qt.UserRole, child)
            
            # Add text content if present
            if child.text and child.text.strip():
                text_item = QTreeWidgetItem(child_item)
                text_item.setText(0, f"Text: {child.text.strip()}")
                text_item.setData(0, Qt.UserRole, ("text", child))
            
            # Add attributes
            for attr_name, attr_value in child.attrib.items():
                attr_item = QTreeWidgetItem(child_item)
                attr_item.setText(0, f"{attr_name}: {attr_value}")
                attr_item.setData(0, Qt.UserRole, ("attr", child, attr_name))
            
            # Recursively add children
            self.add_xml_children(child, child_item)
            
    def on_tree_item_clicked(self, item, column):
        """Handle tree item selection"""
        data = item.data(0, Qt.UserRole)
        
        if isinstance(data, ET.Element):
            self.show_element_properties(data)
        elif isinstance(data, tuple) and len(data) >= 2:
            if data[0] == "text":
                self.show_text_properties(data[1])
            elif data[0] == "attr":
                self.show_attribute_properties(data[1], data[2])
                
    def show_element_properties(self, element):
        """Show properties for an XML element"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Element name (read-only)
        name_edit = QLineEdit(element.tag)
        name_edit.setReadOnly(True)
        layout.addRow("Element:", name_edit)
        
        # Text content
        self.text_editor = QTextEdit()
        self.text_editor.setPlainText(element.text.strip() if element.text else "")
        self.text_editor.setMaximumHeight(100)
        self.text_editor.textChanged.connect(lambda elem=element: self.update_text_content(elem))
        layout.addRow("Text:", self.text_editor)
        
        # Attributes
        self.attribute_editors = {}
        for attr_name, attr_value in element.attrib.items():
            attr_edit = QLineEdit(attr_value)
            attr_edit.textChanged.connect(lambda text, elem=element, attr=attr_name: self.update_attribute(elem, attr, text))
            self.attribute_editors[attr_name] = attr_edit
            layout.addRow(f"{attr_name}:", attr_edit)
        
        # Add common buttons
        button_layout = QHBoxLayout()

        add_attr_btn = QPushButton("Add Attribute")
        add_attr_btn.clicked.connect(lambda: self.add_attribute(element))

        add_child_btn = QPushButton("Add Child Element")
        add_child_btn.clicked.connect(lambda: self.add_child_element(element))

        button_layout.addWidget(add_attr_btn)
        button_layout.addWidget(add_child_btn)
        button_layout.addStretch()

        layout.addRow(button_layout)
        
        self.property_scroll.setWidget(widget)
        
    def show_text_properties(self, element):
        """Show properties for text content"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(element.text.strip() if element.text else "")
        layout.addRow("Text Content:", text_edit)
        
        self.property_scroll.setWidget(widget)
        
    def show_attribute_properties(self, element, attr_name):
        """Show properties for an attribute"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        name_edit = QLineEdit(attr_name)
        name_edit.setReadOnly(True)
        layout.addRow("Attribute Name:", name_edit)
        
        value_edit = QLineEdit(element.get(attr_name, ""))
        layout.addRow("Value:", value_edit)
        
        self.property_scroll.setWidget(widget)
        
    def new_file(self):
        """Create a new simulation file"""
        if self.check_unsaved_changes():
            self.current_file = None
            self.create_default_simulation()
            
    def open_file(self):
        """Open an existing simulation file"""
        if not self.check_unsaved_changes():
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Simulation File", "", 
            "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            try:
                self.simulation_tree = ET.parse(file_path).getroot()
                self.current_file = Path(file_path)
                self.update_tree_view()
            except ET.ParseError as e:
                QMessageBox.critical(self, "Error", f"Failed to parse XML file:\n{e}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")
                
    def save_file(self):
        """Save the current simulation file"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Save the simulation file with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Simulation File", "", 
            "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            self.current_file = Path(file_path)
            self.save_to_file(self.current_file)
            
    def save_to_file(self, file_path):
        """Save the simulation tree to a file"""
        try:
            # Create pretty-printed XML
            self.indent_xml(self.simulation_tree)
            tree = ET.ElementTree(self.simulation_tree)
            tree.write(str(file_path), encoding='utf-8', xml_declaration=True)
            
            QMessageBox.information(self, "Success", f"File saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")
            
    def indent_xml(self, elem, level=0):
        """Add pretty-printing indentation to XML"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent_xml(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
                
    def add_section(self):
        """Add a new section to the simulation"""
        from PyQt5.QtWidgets import QInputDialog

        # Get available section types
        section_types = [
            "domain", "mesh", "species", "material", "boundary",
            "solver", "output", "source", "interaction"
        ]

        section_type, ok = QInputDialog.getItem(
            self, "Add Section", "Select section type:",
            section_types, 0, False
        )

        if ok and section_type:
            # Add new element to the simulation tree
            new_element = ET.SubElement(self.simulation_tree, section_type)

            # Add some default attributes based on type
            if section_type == "domain":
                new_element.set("type", "rect")
            elif section_type == "mesh":
                new_element.set("type", "uniform")
            elif section_type == "species":
                new_element.set("name", "new_species")
            elif section_type == "output":
                new_element.set("type", "2D")
                new_element.set("file_name", "output.vts")

            self.update_tree_view()

    def remove_section(self):
        """Remove the selected section"""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select an item to remove.")
            return

        data = current_item.data(0, Qt.UserRole)
        if isinstance(data, ET.Element):
            # Confirm deletion
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete the '{data.tag}' element?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Find parent and remove element
                parent = self.simulation_tree
                for elem in self.simulation_tree.iter():
                    if data in elem:
                        elem.remove(data)
                        break

                self.update_tree_view()
        else:
            QMessageBox.information(self, "Cannot Delete", "Selected item cannot be deleted.")
            
    def add_attribute(self, element):
        """Add a new attribute to an element"""
        from PyQt5.QtWidgets import QInputDialog

        attr_name, ok1 = QInputDialog.getText(self, "Add Attribute", "Attribute name:")
        if ok1 and attr_name:
            attr_value, ok2 = QInputDialog.getText(self, "Add Attribute", "Attribute value:")
            if ok2:
                element.set(attr_name, attr_value)
                self.update_tree_view()
                self.show_element_properties(element)

    def add_child_element(self, parent_element):
        """Add a new child element"""
        from PyQt5.QtWidgets import QInputDialog

        child_name, ok = QInputDialog.getText(self, "Add Child Element", "Element name:")
        if ok and child_name:
            child = ET.SubElement(parent_element, child_name)
            self.update_tree_view()
            self.show_element_properties(child)

    def update_attribute(self, element, attr_name, new_value):
        """Update an attribute value"""
        element.set(attr_name, new_value)
        self.update_tree_view()

    def update_text_content(self, element):
        """Update text content of an element"""
        if hasattr(self, 'text_editor'):
            element.text = self.text_editor.toPlainText()
            self.update_tree_view()

    def load_template(self):
        """Load a simulation template"""
        from PyQt5.QtWidgets import QInputDialog

        templates = {
            "Basic Plasma": self.create_basic_plasma_template,
            "Ion Beam": self.create_ion_beam_template,
            "Discharge": self.create_discharge_template,
            "Empty": self.create_default_simulation
        }

        template_name, ok = QInputDialog.getItem(
            self, "Load Template", "Select template:",
            list(templates.keys()), 0, False
        )

        if ok and template_name:
            if self.check_unsaved_changes():
                templates[template_name]()

    def create_basic_plasma_template(self):
        """Create a basic plasma simulation template"""
        self.simulation_tree = ET.Element("simulation")

        # Basic structure
        note = ET.SubElement(self.simulation_tree, "note")
        note.text = "Basic Plasma Simulation"

        log = ET.SubElement(self.simulation_tree, "log")
        log.set("level", "info")

        # Time settings
        time = ET.SubElement(self.simulation_tree, "time")
        num_it = ET.SubElement(time, "num_it")
        num_it.text = "5000"
        dt = ET.SubElement(time, "dt")
        dt.text = "1e-6"

        # Domain
        domain = ET.SubElement(self.simulation_tree, "domain")
        domain.set("type", "rect")
        x0 = ET.SubElement(domain, "x0")
        x0.text = "0.0"
        x1 = ET.SubElement(domain, "x1")
        x1.text = "0.1"
        y0 = ET.SubElement(domain, "y0")
        y0.text = "0.0"
        y1 = ET.SubElement(domain, "y1")
        y1.text = "0.1"

        # Mesh
        mesh = ET.SubElement(self.simulation_tree, "mesh")
        mesh.set("type", "uniform")
        ni = ET.SubElement(mesh, "ni")
        ni.text = "50"
        nj = ET.SubElement(mesh, "nj")
        nj.text = "50"

        # Species
        species = ET.SubElement(self.simulation_tree, "species")
        species.set("name", "O+")
        species.set("type", "kinetic")
        mass = ET.SubElement(species, "mass")
        mass.text = "16"
        charge = ET.SubElement(species, "charge")
        charge.text = "1"

        # Starfish
        ET.SubElement(self.simulation_tree, "starfish")

        # Output
        output = ET.SubElement(self.simulation_tree, "output")
        output.set("type", "2D")
        output.set("file_name", "plasma.vts")
        output.set("format", "vtk")
        scalars = ET.SubElement(output, "scalars")
        scalars.text = "phi, rho"

        self.update_tree_view()

    def create_ion_beam_template(self):
        """Create an ion beam simulation template"""
        self.create_basic_plasma_template()

        # Add ion beam source
        source = ET.SubElement(self.simulation_tree, "source")
        source.set("type", "beam")
        source.set("species", "O+")

        # Beam parameters
        energy = ET.SubElement(source, "energy")
        energy.text = "100"  # eV

        current = ET.SubElement(source, "current")
        current.text = "1e-3"  # A

        self.update_tree_view()

    def create_discharge_template(self):
        """Create a discharge simulation template"""
        self.create_basic_plasma_template()

        # Add electrode boundaries
        boundaries = ET.SubElement(self.simulation_tree, "boundaries")

        # Cathode
        cathode = ET.SubElement(boundaries, "boundary")
        cathode.set("name", "cathode")
        cathode.set("type", "dirichlet")
        cathode.set("value", "-100")  # V

        # Anode
        anode = ET.SubElement(boundaries, "boundary")
        anode.set("name", "anode")
        anode.set("type", "dirichlet")
        anode.set("value", "0")  # V

        self.update_tree_view()

    def check_unsaved_changes(self):
        """Check if there are unsaved changes"""
        # For now, always return True
        # In a full implementation, this would track modifications
        return True
