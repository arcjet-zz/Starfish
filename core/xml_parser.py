"""
XML Parser for Starfish simulation files
Equivalent to the Java InputParser class
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union, Optional, List, Dict, Any


class XMLParser:
    """Parser for Starfish XML simulation files"""
    
    def __init__(self, file_path: Union[str, Path], working_directory: Union[str, Path] = None):
        self.file_path = Path(file_path)
        self.working_directory = Path(working_directory) if working_directory else self.file_path.parent
        self.root = None
        self.load_file()
        
    def load_file(self):
        """Load and parse the XML file"""
        try:
            tree = ET.parse(self.file_path)
            self.root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML file {self.file_path}: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"XML file not found: {self.file_path}")
            
    def get_elements(self, tag_name: str) -> List[ET.Element]:
        """Get all elements with the specified tag name"""
        if self.root is None:
            return []
        return self.root.findall(tag_name)
        
    def get_element(self, tag_name: str) -> Optional[ET.Element]:
        """Get the first element with the specified tag name"""
        if self.root is None:
            return None
        return self.root.find(tag_name)
        
    @staticmethod
    def get_string(attribute_name: str, element: ET.Element, default_value: str = "") -> str:
        """Get string attribute value"""
        return element.get(attribute_name, default_value)
        
    @staticmethod
    def get_int(attribute_name: str, element: ET.Element, default_value: int = 0) -> int:
        """Get integer attribute value"""
        value = element.get(attribute_name)
        if value is None:
            return default_value
        try:
            return int(value)
        except ValueError:
            return default_value
            
    @staticmethod
    def get_double(attribute_name: str, element: ET.Element, default_value: float = 0.0) -> float:
        """Get double/float attribute value"""
        value = element.get(attribute_name)
        if value is None:
            return default_value
        try:
            return float(value)
        except ValueError:
            return default_value
            
    @staticmethod
    def get_boolean(attribute_name: str, element: ET.Element, default_value: bool = False) -> bool:
        """Get boolean attribute value"""
        value = element.get(attribute_name)
        if value is None:
            return default_value
        return value.lower() in ('true', '1', 'yes', 'on')
        
    @staticmethod
    def get_text(element: ET.Element, default_value: str = "") -> str:
        """Get element text content"""
        return element.text.strip() if element.text else default_value
        
    def get_child_elements(self, parent_element: ET.Element) -> List[ET.Element]:
        """Get all child elements of a parent element"""
        return list(parent_element)
        
    def validate_simulation_file(self) -> Dict[str, Any]:
        """Validate the simulation file structure"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        if self.root is None:
            validation_result['valid'] = False
            validation_result['errors'].append("No root element found")
            return validation_result
            
        # Check root element
        if self.root.tag != 'simulation':
            validation_result['warnings'].append(
                f"Root element is '{self.root.tag}', expected 'simulation'"
            )
            
        # Check for required elements
        required_elements = ['time', 'starfish']
        for req_elem in required_elements:
            if self.get_element(req_elem) is None:
                validation_result['errors'].append(f"Missing required element: {req_elem}")
                validation_result['valid'] = False
                
        # Check time element
        time_elem = self.get_element('time')
        if time_elem is not None:
            num_it = self.get_int('num_it', time_elem, -1)
            dt = self.get_double('dt', time_elem, -1.0)
            
            if num_it < 0:
                validation_result['warnings'].append("num_it not specified in time element")
            if dt <= 0:
                validation_result['warnings'].append("dt not specified or invalid in time element")
                
        # Collect information
        validation_result['info']['elements'] = [elem.tag for elem in self.root]
        validation_result['info']['has_domain'] = self.get_element('domain') is not None
        validation_result['info']['has_materials'] = self.get_element('materials') is not None
        validation_result['info']['has_boundaries'] = self.get_element('boundaries') is not None
        validation_result['info']['has_sources'] = self.get_element('sources') is not None
        validation_result['info']['has_solver'] = self.get_element('solver') is not None
        validation_result['info']['has_output'] = len(self.get_elements('output')) > 0
        
        return validation_result
        
    def extract_simulation_parameters(self) -> Dict[str, Any]:
        """Extract key simulation parameters"""
        params = {}
        
        # Time parameters
        time_elem = self.get_element('time')
        if time_elem is not None:
            params['num_iterations'] = self.get_int('num_it', time_elem, 1000)
            params['time_step'] = self.get_double('dt', time_elem, 1e-6)
            
        # Solver parameters
        solver_elem = self.get_element('solver')
        if solver_elem is not None:
            params['solver_type'] = self.get_string('type', solver_elem, 'poisson')
            params['solver_method'] = self.get_text(solver_elem.find('method') or ET.Element('method'), 'gs')
            
        # Domain information
        domain_elem = self.get_element('domain')
        if domain_elem is not None:
            params['has_domain'] = True
        else:
            params['has_domain'] = False
            
        # Output information
        output_elements = self.get_elements('output')
        params['output_files'] = []
        for output_elem in output_elements:
            output_info = {
                'type': self.get_string('type', output_elem),
                'file_name': self.get_string('file_name', output_elem),
                'format': self.get_string('format', output_elem, 'vtk')
            }
            params['output_files'].append(output_info)
            
        return params
        
    def get_load_files(self) -> List[Path]:
        """Get list of files to be loaded"""
        load_files = []
        load_elements = self.get_elements('load')
        
        for load_elem in load_elements:
            file_name = self.get_text(load_elem)
            if file_name:
                file_path = self.working_directory / file_name
                load_files.append(file_path)
                
        return load_files
        
    def __iter__(self):
        """Iterator over root element children"""
        if self.root is not None:
            return iter(self.root)
        return iter([])
        
    def __str__(self):
        """String representation"""
        return f"XMLParser({self.file_path})"
