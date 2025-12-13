# export_pdfs.ps1 - Crystal Silence PDF Export Script
# Attempts to use MuseScore CLI to convert MusicXML to PDF

$ErrorActionPreference = "Continue"

# Common MuseScore installation paths
$musescorePaths = @(
    "C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
    "C:\Program Files\MuseScore 3\bin\MuseScore3.exe",
    "C:\Program Files (x86)\MuseScore 4\bin\MuseScore4.exe",
    "C:\Program Files (x86)\MuseScore 3\bin\MuseScore3.exe",
    "$env:LOCALAPPDATA\Programs\MuseScore 4\bin\MuseScore4.exe"
)

$musescore = $null
foreach ($path in $musescorePaths) {
    if (Test-Path $path) {
        $musescore = $path
        break
    }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($musescore) {
    Write-Host "Found MuseScore at: $musescore" -ForegroundColor Green
    Write-Host "Converting MusicXML files to PDF..." -ForegroundColor Cyan
    
    # Find all .musicxml files
    $xmlFiles = Get-ChildItem -Path $scriptDir -Recurse -Filter "*.musicxml"
    
    foreach ($file in $xmlFiles) {
        $pdfPath = $file.FullName -replace "\.musicxml$", ".pdf"
        Write-Host "Converting: $($file.Name)"
        
        try {
            & $musescore -o $pdfPath $file.FullName 2>$null
            if (Test-Path $pdfPath) {
                Write-Host "  [OK] Created: $pdfPath" -ForegroundColor Green
            }
        } catch {
            Write-Host "  [WARN] Could not convert $($file.Name)" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`nConversion complete!" -ForegroundColor Green
} else {
    Write-Host "MuseScore not found in common installation paths." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To export PDFs manually:" -ForegroundColor Cyan
    Write-Host "1. Download MuseScore from https://musescore.org/download"
    Write-Host "2. Install and rerun this script"
    Write-Host ""
    Write-Host "Or use Guitar Pro 8:" -ForegroundColor Cyan
    Write-Host "1. Open each .musicxml file in Guitar Pro 8"
    Write-Host "2. File > Export > PDF"
    Write-Host ""
    Write-Host "MusicXML files are located at:"
    Get-ChildItem -Path $scriptDir -Recurse -Filter "*.musicxml" | ForEach-Object {
        Write-Host "  $($_.FullName)"
    }
}
