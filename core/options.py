"""
Options class for handling command line arguments and configuration
Equivalent to the Java Options class
"""

import os
from enum import Enum
from pathlib import Path


class RunMode(Enum):
    """Simulation run modes"""
    CONSOLE = "console"
    GUI = "gui"
    GUI_RUN = "gui_run"


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Options:
    """Configuration options for Starfish simulation"""
    
    def __init__(self, args=None):
        # Default values
        self.working_directory = Path.cwd()
        self.simulation_file = None
        self.run_mode = RunMode.GUI
        self.randomize = True
        self.log_level = LogLevel.INFO
        self.max_cores = os.cpu_count() or 1
        
        if args:
            self._parse_args(args)
    
    def _parse_args(self, args):
        """Parse command line arguments"""
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg.startswith('-'):
                # Handle flags
                if arg == '-wd' and i + 1 < len(args):
                    self.working_directory = Path(args[i + 1])
                    i += 1
                elif arg == '-gui':
                    if i + 1 < len(args) and args[i + 1] in ['on', 'off', 'run']:
                        gui_mode = args[i + 1]
                        if gui_mode == 'off':
                            self.run_mode = RunMode.CONSOLE
                        elif gui_mode == 'run':
                            self.run_mode = RunMode.GUI_RUN
                        else:
                            self.run_mode = RunMode.GUI
                        i += 1
                    else:
                        self.run_mode = RunMode.GUI
                elif arg == '-nr':
                    self.randomize = False
                elif arg == '-serial':
                    self.max_cores = 1
                elif arg == '-cores' and i + 1 < len(args):
                    try:
                        self.max_cores = int(args[i + 1])
                    except ValueError:
                        print(f"Invalid core count: {args[i + 1]}")
                    i += 1
                elif arg == '-log' and i + 1 < len(args):
                    try:
                        self.log_level = LogLevel(args[i + 1].lower())
                    except ValueError:
                        print(f"Invalid log level: {args[i + 1]}")
                    i += 1
                else:
                    print(f"Unknown argument: {arg}")
            else:
                # Assume it's a simulation file
                if not self.simulation_file:
                    self.simulation_file = Path(arg)
            
            i += 1
    
    def clone(self):
        """Create a copy of this options object"""
        new_options = Options()
        new_options.working_directory = self.working_directory
        new_options.simulation_file = self.simulation_file
        new_options.run_mode = self.run_mode
        new_options.randomize = self.randomize
        new_options.log_level = self.log_level
        new_options.max_cores = self.max_cores
        return new_options
    
    def __str__(self):
        return (f"Options(wd={self.working_directory}, "
                f"sim_file={self.simulation_file}, "
                f"run_mode={self.run_mode}, "
                f"randomize={self.randomize}, "
                f"log_level={self.log_level}, "
                f"max_cores={self.max_cores})")
