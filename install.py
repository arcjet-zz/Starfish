#!/usr/bin/env python3
"""
Installation script for Starfish Python GUI
This script helps set up the environment and dependencies
"""

import sys
import subprocess
import os
from pathlib import Path
import platform

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Starfish Python GUI requires Python 3.7 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_java():
    """Check if Java is available"""
    print("\nChecking Java installation...")
    
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Java version is in stderr for some reason
            version_info = result.stderr.split('\n')[0]
            print(f"✅ Java found: {version_info}")
            return True
        else:
            print("❌ Java not found or not working")
            return False
    except FileNotFoundError:
        print("❌ Java not found in PATH")
        print("   Please install Java Runtime Environment (JRE) 8 or higher")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        # Upgrade pip first
        print("Upgrading pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True)
        
        # Install requirements
        print("Installing dependencies from requirements.txt...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                      check=True)
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_vtk_installation():
    """Test VTK installation"""
    print("\nTesting VTK installation...")
    
    try:
        import vtk
        print(f"✅ VTK {vtk.vtkVersion.GetVTKVersion()} imported successfully")
        
        # Test VTK rendering capability
        render_window = vtk.vtkRenderWindow()
        render_window.SetOffScreenRendering(1)  # Don't show window
        renderer = vtk.vtkRenderer()
        render_window.AddRenderer(renderer)
        
        # Create a simple sphere to test rendering
        sphere = vtk.vtkSphereSource()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        renderer.AddActor(actor)
        
        render_window.Render()
        print("✅ VTK rendering test passed")
        return True
        
    except ImportError:
        print("❌ VTK import failed")
        return False
    except Exception as e:
        print(f"❌ VTK test failed: {e}")
        return False

def test_pyqt_installation():
    """Test PyQt5 installation"""
    print("\nTesting PyQt5 installation...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        # Create a minimal application to test
        app = QApplication([])
        print("✅ PyQt5 imported and application created successfully")
        app.quit()
        return True
        
    except ImportError as e:
        print(f"❌ PyQt5 import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ PyQt5 test failed: {e}")
        return False

def find_starfish_jar():
    """Find Starfish CLI jar file"""
    print("\nLooking for Starfish CLI jar file...")
    
    current_dir = Path.cwd()
    possible_locations = [
        current_dir / "StarfishCLI.jar",
        current_dir / "build" / "StarfishCLI.jar",
        current_dir / "dist" / "StarfishCLI.jar",
        current_dir / "target" / "StarfishCLI.jar",
        current_dir / "Starfish.jar"  # Full GUI version
    ]
    
    found_jars = []
    for jar_path in possible_locations:
        if jar_path.exists():
            found_jars.append(jar_path)
            print(f"✅ Found: {jar_path}")
    
    if not found_jars:
        print("⚠️  No Starfish jar files found")
        print("   You'll need to download StarfishCLI.jar from:")
        print("   https://github.com/particleincell/Starfish/releases")
        return False
    
    return True

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only for now)"""
    if platform.system() != "Windows":
        return True
    
    print("\nCreating desktop shortcut...")
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "Starfish Python GUI.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = str(Path(__file__).parent / "main.py")
        shortcut.WorkingDirectory = str(Path(__file__).parent)
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print(f"✅ Desktop shortcut created: {shortcut_path}")
        return True
        
    except ImportError:
        print("⚠️  Could not create desktop shortcut (winshell not available)")
        return True
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {e}")
        return True

def run_test_suite():
    """Run the test suite"""
    print("\nRunning test suite...")
    
    try:
        test_script = Path(__file__).parent / "test_gui.py"
        result = subprocess.run([sys.executable, str(test_script)], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False

def main():
    """Main installation process"""
    print("Starfish Python GUI Installation")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        return 1
    
    java_available = check_java()
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Test installations
    vtk_ok = test_vtk_installation()
    pyqt_ok = test_pyqt_installation()
    
    if not (vtk_ok and pyqt_ok):
        print("\n❌ Some dependencies failed to install correctly")
        return 1
    
    # Check for Starfish jar
    jar_found = find_starfish_jar()
    
    # Create shortcut
    create_desktop_shortcut()
    
    # Run tests
    tests_passed = run_test_suite()
    
    # Summary
    print("\n" + "=" * 50)
    print("Installation Summary:")
    print(f"✅ Python: Compatible")
    print(f"{'✅' if java_available else '⚠️ '} Java: {'Available' if java_available else 'Not found'}")
    print(f"✅ Dependencies: Installed")
    print(f"✅ VTK: Working")
    print(f"✅ PyQt5: Working")
    print(f"{'✅' if jar_found else '⚠️ '} Starfish JAR: {'Found' if jar_found else 'Not found'}")
    print(f"{'✅' if tests_passed else '❌'} Tests: {'Passed' if tests_passed else 'Failed'}")
    
    if tests_passed and (java_available or jar_found):
        print("\n🎉 Installation completed successfully!")
        print("\nTo start the GUI, run:")
        print("   python main.py")
        
        if not java_available:
            print("\n⚠️  Note: Java not found. You'll need to install Java to run simulations.")
        
        if not jar_found:
            print("\n⚠️  Note: Starfish JAR not found. Download from:")
            print("   https://github.com/particleincell/Starfish/releases")
        
        return 0
    else:
        print("\n❌ Installation completed with issues.")
        print("Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
