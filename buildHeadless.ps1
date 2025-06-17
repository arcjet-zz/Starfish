# This will build a JAR file that starts at starfish.MainHeadless
# Starfish is dependent on the VTK library for the GUI only, which
# many users may not need if they are exclusively using the CLI.
# This script builds a JAR file without the GUI components such that
# users don't need to have the VTK library installed on their computer.

param(
    [string]$JarFile = "starfish.jar",
    [string]$SourceDir = "src",
    [string]$MainClass = "starfish.MainHeadless",
    [string]$TmpDir = "tmp"
)

Write-Host "Building Starfish CLI JAR file..." -ForegroundColor Green
Write-Host ""

# Check if Java is available
try {
    $javaVersion = java -version 2>&1
    Write-Host "Java found: $($javaVersion[0])" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Java is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Java JDK 8 or higher and ensure 'java' and 'javac' are in PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    $javacVersion = javac -version 2>&1
    Write-Host "Java compiler found: $javacVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Java compiler (javac) is not available" -ForegroundColor Red
    Write-Host "Please install Java JDK (not just JRE) and ensure 'javac' is in PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Clean up and create temporary directory
if (Test-Path $TmpDir) {
    Remove-Item $TmpDir -Recurse -Force
}
New-Item -ItemType Directory -Path $TmpDir | Out-Null

Write-Host "Copying Java source files (excluding GUI components)..." -ForegroundColor Cyan

# Get all Java files
$allJavaFiles = Get-ChildItem -Path $SourceDir -Filter "*.java" -Recurse

$copiedFiles = 0
foreach ($file in $allJavaFiles) {
    $relativePath = $file.FullName.Substring((Get-Location).Path.Length + $SourceDir.Length + 2)
    
    # Skip GUI folder and Main.java
    if ($relativePath -notmatch "starfish[\\\/]gui[\\\/]" -and $relativePath -notmatch "starfish[\\\/]Main\.java$") {
        # Create directory structure in tmp
        $targetDir = Join-Path $TmpDir (Split-Path $relativePath -Parent)
        if (!(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        # Copy file
        $targetFile = Join-Path $TmpDir $relativePath
        Copy-Item $file.FullName $targetFile
        $copiedFiles++
    }
}

Write-Host "Copied $copiedFiles Java source files" -ForegroundColor Green

# Copy and modify META-INF
$metaInfSource = Join-Path $SourceDir "META-INF"
if (Test-Path $metaInfSource) {
    $metaInfTarget = Join-Path $TmpDir "META-INF"
    New-Item -ItemType Directory -Path $metaInfTarget | Out-Null
    
    # Create modified MANIFEST.MF for headless main class
    $manifestContent = @"
Manifest-Version: 1.0
Main-Class: $MainClass

"@
    Set-Content -Path (Join-Path $metaInfTarget "MANIFEST.MF") -Value $manifestContent
    Write-Host "Created MANIFEST.MF with Main-Class: $MainClass" -ForegroundColor Green
}

Write-Host ""
Write-Host "Compiling Java sources..." -ForegroundColor Cyan

# Find all Java files in tmp directory
$javaFiles = Get-ChildItem -Path $TmpDir -Filter "*.java" -Recurse
$javaFileList = $javaFiles | ForEach-Object { "`"$($_.FullName)`"" }

# Compile all Java files
$compileCommand = "javac -d `"$TmpDir`" -sourcepath `"$TmpDir`" $($javaFileList -join ' ')"
Write-Host "Running: javac with $($javaFiles.Count) source files" -ForegroundColor Yellow

try {
    Invoke-Expression $compileCommand
    if ($LASTEXITCODE -ne 0) {
        throw "Compilation failed with exit code $LASTEXITCODE"
    }
    Write-Host "Compilation successful!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Compilation failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Remove-Item $TmpDir -Recurse -Force
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Creating JAR file..." -ForegroundColor Cyan

# Create JAR file with manifest
$manifestPath = Join-Path $TmpDir "META-INF\MANIFEST.MF"
try {
    if (Test-Path $manifestPath) {
        jar cfm $JarFile $manifestPath -C $TmpDir .
    } else {
        jar cfe $JarFile $MainClass -C $TmpDir .
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "JAR creation failed with exit code $LASTEXITCODE"
    }
    Write-Host "JAR file created successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: JAR creation failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Remove-Item $TmpDir -Recurse -Force
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean up
Remove-Item $TmpDir -Recurse -Force

Write-Host ""
Write-Host "SUCCESS: $JarFile created successfully!" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host ""
Write-Host "To test the JAR file, run:" -ForegroundColor Yellow
Write-Host "  java -jar $JarFile" -ForegroundColor White
Write-Host ""
Write-Host "To run a simulation:" -ForegroundColor Yellow
Write-Host "  java -jar $JarFile path\to\simulation.xml" -ForegroundColor White
Write-Host ""

# Get file size
$jarInfo = Get-Item $JarFile
Write-Host "JAR file size: $([math]::Round($jarInfo.Length / 1MB, 2)) MB" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
