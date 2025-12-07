# ═══════════════════════════════════════════════════════════════════════════════
#  TRIO TUNES - AUTOMATED MUSICXML → A4 PDF ENGRAVING SYSTEM
#  Converts all MusicXML files to professional A4 lead sheet PDFs
#  using MuseScore 4 CLI
# ═══════════════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Continue"

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Detect MuseScore CLI
# ─────────────────────────────────────────────────────────────────────────────

$MUSESCORE = $null

$paths = @(
    "C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
    "C:\Program Files\MuseScore 3\bin\MuseScore3.exe",
    "C:\Program Files (x86)\MuseScore 4\bin\MuseScore4.exe",
    "C:\Program Files (x86)\MuseScore 3\bin\MuseScore3.exe"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        $MUSESCORE = $path
        break
    }
}

if (-not $MUSESCORE) {
    Write-Host "ERROR: No MuseScore installation found!" -ForegroundColor Red
    Write-Host "Please install MuseScore 4 from: https://musescore.org/download"
    exit 1
}

Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TRIO TUNES XML → PDF CONVERTER" -ForegroundColor Cyan
Write-Host "  Using: $MUSESCORE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Find all MusicXML files
# ─────────────────────────────────────────────────────────────────────────────

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$xmlFiles = Get-ChildItem -Path $scriptDir -Recurse -Include "*.musicxml", "*.xml" | Where-Object { $_.Name -notmatch "^[A-Z]:" }

$totalFiles = $xmlFiles.Count
$converted = 0
$failed = 0

Write-Host "Found $totalFiles MusicXML files to convert" -ForegroundColor Yellow
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Convert each file
# ─────────────────────────────────────────────────────────────────────────────

foreach ($xmlFile in $xmlFiles) {
    $pdfFile = [System.IO.Path]::ChangeExtension($xmlFile.FullName, ".pdf")
    $relativePath = $xmlFile.FullName.Replace($scriptDir, "").TrimStart("\")
    
    Write-Host "[$($converted + $failed + 1)/$totalFiles] Converting: $relativePath" -ForegroundColor White
    
    try {
        # Run MuseScore in CLI mode to export PDF
        $process = Start-Process -FilePath $MUSESCORE -ArgumentList @(
            "-o", "`"$pdfFile`"",
            "`"$($xmlFile.FullName)`""
        ) -Wait -PassThru -NoNewWindow -ErrorAction Stop
        
        if ($process.ExitCode -eq 0 -and (Test-Path $pdfFile)) {
            Write-Host "  ✓ Created: $([System.IO.Path]::GetFileName($pdfFile))" -ForegroundColor Green
            $converted++
        } else {
            Write-Host "  ✗ Failed (exit code: $($process.ExitCode))" -ForegroundColor Red
            $failed++
        }
    }
    catch {
        Write-Host "  ✗ Error: $_" -ForegroundColor Red
        $failed++
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Summary
# ─────────────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  CONVERSION COMPLETE" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✓ Converted: $converted files" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "  ✗ Failed: $failed files" -ForegroundColor Red
}
Write-Host ""
Write-Host "PDFs are saved alongside their source MusicXML files."
Write-Host ""

