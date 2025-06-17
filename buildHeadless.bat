@echo off
setlocal enabledelayedexpansion

REM ========================================
REM Windows Build Script for Starfish CLI JAR
REM ========================================
REM This script builds a headless version of Starfish that doesn't require VTK
REM and can run simulations from the command line without GUI components.
REM
REM Requirements:
REM - Java JDK 8 or higher (with javac and jar commands)
REM - Windows command prompt or PowerShell
REM
REM Usage:
REM   buildHeadless_windows.bat
REM
REM Output:
REM   starfish.jar - Headless CLI version of Starfish
REM
REM Test the JAR:
REM   java -jar starfish.jar
REM   java -jar starfish.jar path\to\simulation.xml
REM ========================================

echo ========================================
echo Building Starfish CLI JAR file...
echo ========================================

REM Configuration
set JAR_FILE=starfish.jar
set SOURCE_DIR=src
set MAIN_CLASS=starfish.MainHeadless
set TMP_DIR=tmp

echo Checking Java installation...
java -version >nul 2>&1 && echo Java runtime found || goto :java_error
javac -version >nul 2>&1 && echo Java compiler found || goto :javac_error

echo.
echo Setting up build directory...
if exist "%TMP_DIR%" (
    echo Cleaning existing build directory...
    rmdir /s /q "%TMP_DIR%"
)
mkdir "%TMP_DIR%"

echo.
echo Copying source files (excluding GUI components)...
if not exist "%SOURCE_DIR%" (
    echo ERROR: Source directory '%SOURCE_DIR%' not found
    echo Make sure you're running this script from the Starfish root directory
    pause
    exit /b 1
)

xcopy "%SOURCE_DIR%" "%TMP_DIR%" /S /I /Y >nul
if errorlevel 1 (
    echo ERROR: Failed to copy source files
    pause
    exit /b 1
)

echo Removing GUI components...
if exist "%TMP_DIR%\starfish\gui" (
    rmdir /s /q "%TMP_DIR%\starfish\gui"
    echo Removed GUI directory
)
if exist "%TMP_DIR%\starfish\Main.java" (
    del "%TMP_DIR%\starfish\Main.java"
    echo Removed Main.java (GUI version)
)

echo.
echo Creating MANIFEST.MF for headless version...
if exist "%TMP_DIR%\META-INF" (
    echo Manifest-Version: 1.0 > "%TMP_DIR%\META-INF\MANIFEST.MF"
    echo Main-Class: %MAIN_CLASS% >> "%TMP_DIR%\META-INF\MANIFEST.MF"
    echo. >> "%TMP_DIR%\META-INF\MANIFEST.MF"
    echo MANIFEST.MF updated
)

echo.
echo Compiling Java sources...
dir /s /b "%TMP_DIR%\*.java" > java_files.txt 2>nul
if not exist java_files.txt (
    echo ERROR: No Java files found to compile
    rmdir /s /q "%TMP_DIR%"
    pause
    exit /b 1
)

REM Check if we have any files to compile
for /f %%i in (java_files.txt) do set HAVE_FILES=1
if not defined HAVE_FILES (
    echo ERROR: No Java files found in source directory
    del java_files.txt
    rmdir /s /q "%TMP_DIR%"
    pause
    exit /b 1
)

javac -d "%TMP_DIR%" -sourcepath "%TMP_DIR%" @java_files.txt
set COMPILE_RESULT=%errorlevel%
del java_files.txt

if %COMPILE_RESULT% neq 0 (
    echo ERROR: Compilation failed with exit code %COMPILE_RESULT%
    rmdir /s /q "%TMP_DIR%"
    pause
    exit /b 1
)
echo Compilation successful!

echo.
echo Creating JAR file...
REM Try to find jar command
set JAR_CMD=jar
jar >nul 2>&1
if errorlevel 9009 (
    echo jar not in PATH, searching for it...
    REM Try common Java installation paths
    if exist "C:\Program Files\Java\jdk-24\bin\jar.exe" (
        set JAR_CMD="C:\Program Files\Java\jdk-24\bin\jar.exe"
    ) else if exist "C:\Program Files\Java\jdk-11\bin\jar.exe" (
        set JAR_CMD="C:\Program Files\Java\jdk-11\bin\jar.exe"
    ) else if exist "C:\Program Files\Java\jdk1.8.0_*\bin\jar.exe" (
        set JAR_CMD="C:\Program Files\Java\jdk1.8.0_*\bin\jar.exe"
    ) else (
        echo ERROR: jar.exe not found
        echo Please ensure Java JDK is installed and jar.exe is accessible
        rmdir /s /q "%TMP_DIR%"
        pause
        exit /b 1
    )
    echo Found jar command
)

%JAR_CMD% cfe "%JAR_FILE%" "%MAIN_CLASS%" -C "%TMP_DIR%" .
if errorlevel 1 (
    echo ERROR: JAR creation failed
    rmdir /s /q "%TMP_DIR%"
    pause
    exit /b 1
)

echo Cleaning up temporary files...
rmdir /s /q "%TMP_DIR%"

echo.
echo ========================================
echo SUCCESS: %JAR_FILE% created successfully!
echo ========================================
echo.
echo File information:
dir "%JAR_FILE%" | find "%JAR_FILE%"
echo.
echo Usage examples:
echo   java -jar %JAR_FILE%
echo   java -jar %JAR_FILE% path\to\simulation.xml
echo   java -jar %JAR_FILE% dat\examples\tutorial\step1\starfish.xml
echo.
echo To run a simulation, navigate to the directory containing the simulation
echo files and run:
echo   java -jar path\to\%JAR_FILE% simulation.xml
echo.
echo Example:
echo   cd dat\examples\tutorial\step1
echo   java -jar ..\..\..\..\%JAR_FILE% starfish.xml
echo.
goto :end

:java_error
echo ERROR: Java not found in PATH
echo Please install Java JDK 8 or higher
pause
exit /b 1

:javac_error
echo ERROR: javac not found in PATH
echo Please install Java JDK (not just JRE)
pause
exit /b 1

:end
pause
