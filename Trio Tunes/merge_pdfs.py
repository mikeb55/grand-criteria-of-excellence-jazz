"""
Merge A/B/C/D Lead Sheet PDFs into Complete files
Original individual files are NOT deleted
"""
import os
import sys
from pathlib import Path

try:
    from PyPDF2 import PdfMerger
except ImportError:
    print("Installing PyPDF2...")
    os.system("py -m pip install PyPDF2 --quiet")
    from PyPDF2 import PdfMerger

script_dir = Path(__file__).parent.resolve()
output_dir = script_dir / "PDF"
output_dir.mkdir(exist_ok=True)

print("=" * 50)
print("  Lead Sheet PDF Merger")
print("  GCE Jazz - Trio Tunes Collection")
print("=" * 50)
print()

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

print()
print("=" * 50)
print(f"  Complete! Merged: {merged}, Skipped: {skipped}")
print("=" * 50)
print(f"Output folder: {output_dir}")
print()
print("NOTE: Original A/B/C/D files were NOT deleted.")


