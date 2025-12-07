# Merge_LeadSheets_to_PDF.ps1
# Combines A/B/C/D lead sheets into single PDFs per tune
# Original individual files are NOT deleted
#
# Requires: PDFtk or a PDF merging tool
# Usage: .\Merge_LeadSheets_to_PDF.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lead Sheet PDF Merger" -ForegroundColor Cyan
Write-Host "  GCE Jazz - Trio Tunes Collection" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $scriptDir) { $scriptDir = Get-Location }

$outputDir = Join-Path $scriptDir "PDF"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "Created output directory: $outputDir" -ForegroundColor Green
}

# Find PDFtk
$pdftkPaths = @(
    "C:\Program Files\PDFtk Server\bin\pdftk.exe",
    "C:\Program Files (x86)\PDFtk Server\bin\pdftk.exe",
    "C:\Program Files\PDFtk\bin\pdftk.exe",
    "$env:LOCALAPPDATA\Programs\PDFtk\bin\pdftk.exe"
)

$pdftk = $null
foreach ($path in $pdftkPaths) {
    if (Test-Path $path) {
        $pdftk = $path
        Write-Host "Found PDFtk: $path" -ForegroundColor Green
        break
    }
}

if (-not $pdftk) {
    Write-Host "WARNING: PDFtk not found!" -ForegroundColor Yellow
    Write-Host "Please install PDFtk Server from: https://www.pdflabs.com/tools/pdftk-server/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Using PyPDF2 Python fallback..." -ForegroundColor Cyan
    
    # Create Python fallback script
    $pythonScript = @"
import os
import sys
from pathlib import Path

try:
    from PyPDF2 import PdfMerger
except ImportError:
    print("Installing PyPDF2...")
    os.system("pip install PyPDF2")
    from PyPDF2 import PdfMerger

script_dir = Path(r"$scriptDir")
output_dir = script_dir / "PDF"
output_dir.mkdir(exist_ok=True)

# Tune mappings
tunes = [
    ("01", "Blue_Cycle"),
    ("02", "Orbit"),
    ("03", "Rust_And_Chrome"),
    ("04", "Sao_Paulo_Rain"),
    ("05", "The_Mirror"),
    ("06", "Bright_Size_Life_2"),
    ("07", "Monks_Dream"),
    ("08", "Nefertitis_Shadow"),
    ("09", "Greezy"),
    ("10", "Hexagon"),
    ("11", "Crystal_Silence"),
    ("12", "Angular_Motion"),
    ("13", "The_Void"),
    ("14", "Solar_Flare"),
    ("15", "Final_Departure"),
]

merged = 0
skipped = 0

for num, name in tunes:
    tune_dir = script_dir / f"Tune{num}_{name}" / "LeadSheet"
    if not tune_dir.exists():
        print(f"  SKIP: Tune{num}_{name} (folder not found)")
        skipped += 1
        continue
    
    # Collect A, B, C, D PDFs
    pdfs = []
    for version in ["A", "B", "C", "D"]:
        version_dir = tune_dir / version
        if version_dir.exists():
            pdf_files = list(version_dir.glob("*.pdf"))
            if pdf_files:
                pdfs.append(pdf_files[0])
    
    if len(pdfs) < 4:
        print(f"  SKIP: {name} (only {len(pdfs)}/4 PDFs found)")
        skipped += 1
        continue
    
    output_file = output_dir / f"{num}_{name}_Complete.pdf"
    
    try:
        merger = PdfMerger()
        for pdf in pdfs:
            merger.append(str(pdf))
        merger.write(str(output_file))
        merger.close()
        print(f"  MERGED: {num}_{name}_Complete.pdf ({len(pdfs)} files)")
        merged += 1
    except Exception as e:
        print(f"  ERROR: {name} - {e}")

print(f"\nComplete! Merged: {merged}, Skipped: {skipped}")
print(f"Output folder: {output_dir}")
"@
    
    $pythonScript | Out-File -FilePath (Join-Path $scriptDir "merge_pdfs.py") -Encoding UTF8
    
    Write-Host "Running Python merge script..." -ForegroundColor Cyan
    python (Join-Path $scriptDir "merge_pdfs.py")
    
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# PDFtk merge logic
$tunes = @(
    @{Num="01"; Name="Blue_Cycle"},
    @{Num="02"; Name="Orbit"},
    @{Num="03"; Name="Rust_And_Chrome"},
    @{Num="04"; Name="Sao_Paulo_Rain"},
    @{Num="05"; Name="The_Mirror"},
    @{Num="06"; Name="Bright_Size_Life_2"},
    @{Num="07"; Name="Monks_Dream"},
    @{Num="08"; Name="Nefertitis_Shadow"},
    @{Num="09"; Name="Greezy"},
    @{Num="10"; Name="Hexagon"},
    @{Num="11"; Name="Crystal_Silence"},
    @{Num="12"; Name="Angular_Motion"},
    @{Num="13"; Name="The_Void"},
    @{Num="14"; Name="Solar_Flare"},
    @{Num="15"; Name="Final_Departure"}
)

$merged = 0
$skipped = 0

foreach ($tune in $tunes) {
    $tuneDir = Join-Path $scriptDir "Tune$($tune.Num)_$($tune.Name)" "LeadSheet"
    
    if (-not (Test-Path $tuneDir)) {
        Write-Host "  SKIP: Tune$($tune.Num)_$($tune.Name) (folder not found)" -ForegroundColor DarkGray
        $skipped++
        continue
    }
    
    $pdfs = @()
    foreach ($version in @("A", "B", "C", "D")) {
        $versionDir = Join-Path $tuneDir $version
        if (Test-Path $versionDir) {
            $pdfFile = Get-ChildItem -Path $versionDir -Filter "*.pdf" | Select-Object -First 1
            if ($pdfFile) {
                $pdfs += $pdfFile.FullName
            }
        }
    }
    
    if ($pdfs.Count -lt 4) {
        Write-Host "  SKIP: $($tune.Name) (only $($pdfs.Count)/4 PDFs found)" -ForegroundColor Yellow
        $skipped++
        continue
    }
    
    $outputFile = Join-Path $outputDir "$($tune.Num)_$($tune.Name)_Complete.pdf"
    
    try {
        & $pdftk $pdfs cat output $outputFile
        Write-Host "  MERGED: $($tune.Num)_$($tune.Name)_Complete.pdf" -ForegroundColor Green
        $merged++
    } catch {
        Write-Host "  ERROR: $($tune.Name) - $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Merge Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Merged: $merged" -ForegroundColor Green
Write-Host "  Skipped: $skipped" -ForegroundColor $(if ($skipped -gt 0) { "Yellow" } else { "Gray" })
Write-Host ""
Write-Host "Output folder: $outputDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "NOTE: Original A/B/C/D files were NOT deleted." -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

