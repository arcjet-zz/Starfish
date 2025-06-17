# Starfish - 2D Plasma/Gas Simulation Code

![Starfish logo](resources/starfish-100.png)

[Starfish](https://www.particleincell.com/starfish) is a 2D (Cartesian or axisymmetric) code for simulating a wide range of plasma and gas problems.
It implements the electrostatic Particle-in-Cell (ES-PIC) method along with several fluid solvers. Material interactions are included through
MCC or DSMC collisions, or via chemical reactions. The computational domain can be divided into multiple rectilinear or body-fitted meshes, and linear/cubic
splines represent the surface geometry.

## 🚀 Quick Start

### Python GUI (Recommended)
```bash
# 1. Install dependencies
python install.py

# 2. Start GUI
python main.py
```

### Command Line
```bash
java -jar StarfishCLI.jar simulation_file.xml
```

## 📋 System Requirements

- **Python**: 3.7+ (for GUI)
- **Java**: JRE 8+ (for simulation engine)
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

## 🔧 Installation

### Option 1: One-Click Setup (Recommended)
```bash
# Windows
start_gui.bat

# Linux/macOS
./start_gui.sh
```

### Option 2: Manual Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python main.py
```

### Option 3: Build from Source
See [Building StarfishCLI.jar](#building-starfishclijar) section below.

## 🎯 Python GUI Features

### 🔧 Simulation File Builder
- Interactive XML simulation file creation
- Tree-based structure editor with real-time validation
- Built-in templates (plasma, ion beam, discharge)
- Form-based parameter input

### 🚀 Simulation Runner
- Queue-based simulation management
- Real-time progress monitoring and console output
- Multi-core execution support
- Pause/resume/stop controls

### 📊 Result Viewer
- VTK-based 3D visualization with proper 2D camera setup
- Multiple field display (phi, rho, nd.O+, efi, etc.)
- Live simulation viewing with "Show Current Sim" feature
- Customizable colormaps and animation support
- Auto-refresh during simulation with optimal view bounds

## 📁 File Types Guide

### ✅ Runnable Simulation Files
- `starfish.xml` - Main simulation configuration files

### ⚠️ Configuration Fragments (Not Runnable)
- `interactions.xml` - Material interaction configs
- `materials.xml` - Material definition configs
- `boundaries.xml` - Boundary condition configs
- `domain.xml` - Domain geometry configs

## 🛠 Troubleshooting

### Common Issues

#### "PyQt5 not found"
```bash
pip install PyQt5
```

#### "VTK import error"
```bash
pip install vtk
```

#### "Java not found"
- Install Java JRE 8+ and ensure `java` is in PATH
- Verify: `java -version`

#### "StarfishCLI.jar not found"
- Download from [Releases](https://github.com/particleincell/Starfish/releases)
- Or build from source using `buildHeadless.bat` (Windows) or `buildHeadless.sh` (Linux/macOS)

#### "jar command not found" (Windows)
- Install Java JDK (not just JRE) from [Oracle](https://www.oracle.com/java/technologies/downloads/)
- The build script will automatically locate jar.exe in common installation paths
- Alternatively, set JAVA_HOME environment variable

#### "javac not found"
- Install Java JDK (Development Kit), not just JRE (Runtime Environment)
- Verify installation: `javac -version`

#### Simulation Ends Immediately
- Use recommended test files: `dat/examples/tutorial/step1/starfish.xml`
- Avoid `interactions.xml` and other config fragments
- Check for `particle_trace` configuration errors
- Ensure you're running from the correct directory with all required XML files

## 🏗 Building StarfishCLI.jar

### Prerequisites
- Java Development Kit (JDK) 8 or higher
- All source files in `src/` directory

### Windows (Recommended)
Use the automated build script:
```batch
.\buildHeadless.bat
```

This script will:
- ✅ Check Java installation (JDK required)
- ✅ Automatically find jar.exe even if not in PATH
- ✅ Remove GUI components for headless operation
- ✅ Compile all Java sources
- ✅ Create optimized JAR file (~1.4MB)
- ✅ Provide detailed error messages and troubleshooting

### Linux/macOS
```bash
./buildHeadless.sh
```

### Manual Build Steps
```bash
# 1. Create build directory
mkdir build
cd build

# 2. Compile Java sources
javac -cp . -d . ../src/starfish/**/*.java

# 3. Copy manifest
cp ../src/META-INF/MANIFEST.MF .

# 4. Create JAR file
jar cfm StarfishCLI.jar MANIFEST.MF starfish/

# 5. Move to project root
mv StarfishCLI.jar ../
```

### Alternative: Using IDE
1. Import `src/` as Java project in your IDE
2. Set main class to `starfish.MainHeadless`
3. Build JAR with dependencies
4. Ensure manifest specifies `Main-Class: starfish.MainHeadless`

### Verification
```bash
java -jar starfish.jar
# Should display Starfish version and usage information

# Test with example simulation
cd dat/examples/tutorial/step1
java -jar ../../../../starfish.jar starfish.xml
```

## 📖 Examples

Recommended test files (located in `dat/examples/`):

| File | Description | Status |
|------|-------------|--------|
| `tutorial/step1/starfish.xml` | Basic plasma simulation | ✅ Fast, reliable |
| `tutorial/step2/starfish.xml` | Ion beam simulation | ✅ Normal runtime |
| `multi-domain/starfish.xml` | Multi-domain flow | ⚠️ Fixed particle_trace |

## 📞 Support & Contact

- **Documentation**: See `doc/Starfish-UG.pdf` for detailed user guide
- **Tutorials**: [ES-PIC](https://www.particleincell.com/2012/starfish-tutorial-part1/) and [DSMC](https://www.particleincell.com/2017/starfish-tutorial-dsmc/)
- **Website**: [particleincell.com](https://www.particleincell.com/contact/)
- **Issues**: Submit bug reports for any problems

## 📄 License

Simplified BSD (Modified for Non-Commercial Use Only)
Copyright © 2012-2024 Particle In Cell Consulting LLC

## 🔄 Recent Updates

- **v0.27.1**: Fixed Windows build script (`buildHeadless.bat`) - automatic jar.exe detection, improved error handling, and resolved NullPointerException in Options class
- **v0.27**: Fixed VTK visualization issues - proper color mapping, live simulation viewing, and adaptive camera for different domain sizes
- **v0.25**: Python GUI implementation with VTK visualization
- **v0.24**: Magnetostatic and Geng generalized Ohm's law solver
- **v0.22**: Multi-mesh support, command line arguments, trace rewrite
- **v0.21**: Chemical reaction rate sigmas support

