# Convert_MusicXML_to_PDF.ps1
# Converts all MusicXML files in Trio Tunes to PDF using MuseScore
#
# Usage: Right-click and "Run with PowerShell" OR run from terminal:
#        .\Convert_MusicXML_to_PDF.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MusicXML to PDF Converter" -ForegroundColor Cyan
Write-Host "  GCE Jazz - Trio Tunes Collection" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find MuseScore installation
$musescorePaths = @(
    "${env:ProgramFiles}\MuseScore 4\bin\MuseScore4.exe",
    "${env:ProgramFiles}\MuseScore 3\bin\MuseScore3.exe",
    "${env:ProgramFiles(x86)}\MuseScore 4\bin\MuseScore4.exe",
    "${env:ProgramFiles(x86)}\MuseScore 3\bin\MuseScore3.exe",
    "$env:LOCALAPPDATA\Programs\MuseScore 4\bin\MuseScore4.exe",
    "$env:LOCALAPPDATA\Programs\MuseScore 3\bin\MuseScore3.exe"
)

$musescore = $null
foreach ($path in $musescorePaths) {
    if (Test-Path $path) {
        $musescore = $path
        Write-Host "Found MuseScore: $path" -ForegroundColor Green
        break
    }
}

if (-not $musescore) {
    Write-Host "ERROR: MuseScore not found!" -ForegroundColor Red
    Write-Host "Please install MuseScore 3 or 4 from https://musescore.org" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Get script directory (where this script is located)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $scriptDir) {
    $scriptDir = Get-Location
}

Write-Host "Working directory: $scriptDir" -ForegroundColor Gray
Write-Host ""

# Find all MusicXML files
$xmlFiles = Get-ChildItem -Path $scriptDir -Recurse -Include "*.musicxml", "*.mxl" | 
    Where-Object { $_.FullName -match "LeadSheet" }

if ($xmlFiles.Count -eq 0) {
    Write-Host "No MusicXML files found in LeadSheet folders!" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($xmlFiles.Count) MusicXML files to convert" -ForegroundColor Cyan
Write-Host ""

$converted = 0
$skipped = 0
$failed = 0

foreach ($xmlFile in $xmlFiles) {
    $pdfPath = [System.IO.Path]::ChangeExtension($xmlFile.FullName, ".pdf")
    $relativePath = $xmlFile.FullName.Replace("$scriptDir\", "")
    
    # Check if PDF already exists and is newer than XML
    if ((Test-Path $pdfPath) -and ((Get-Item $pdfPath).LastWriteTime -gt $xmlFile.LastWriteTime)) {
        Write-Host "  SKIP: $relativePath (PDF is up to date)" -ForegroundColor DarkGray
        $skipped++
        continue
    }
    
    Write-Host "  Converting: $relativePath" -ForegroundColor White
    
    try {
        # Run MuseScore to convert
        $process = Start-Process -FilePath $musescore -ArgumentList "-o", "`"$pdfPath`"", "`"$($xmlFile.FullName)`"" -Wait -PassThru -NoNewWindow -RedirectStandardError "NUL"
        
        if ($process.ExitCode -eq 0 -and (Test-Path $pdfPath)) {
            Write-Host "    -> Created PDF" -ForegroundColor Green
            $converted++
        } else {
            Write-Host "    -> FAILED (exit code: $($process.ExitCode))" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host "    -> ERROR: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Conversion Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Converted: $converted" -ForegroundColor Green
Write-Host "  Skipped:   $skipped" -ForegroundColor DarkGray
Write-Host "  Failed:    $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Gray" })
Write-Host ""

if ($converted -gt 0) {
    Write-Host "PDF files created alongside MusicXML source files." -ForegroundColor Yellow
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


