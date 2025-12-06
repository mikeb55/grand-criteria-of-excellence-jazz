"""
GCE Jazz Guitar Collection - Workbook PDF Generator
Combines all tune analysis files into a printable PDF workbook.
"""

from fpdf import FPDF
from pathlib import Path
import re

# Paths
BASE_DIR = Path(__file__).parent.parent
MD_DIR = BASE_DIR / "Trio Tunes" / "MD"
OUTPUT_PDF = BASE_DIR / "GCE_Jazz_Guitar_Workbook.pdf"

# Tune files in order
TUNE_FILES = [
    "Tune_1_Blue_Cycle.md",
    "Tune_2_Orbit.md",
    "Tune_3_Rust_and_Chrome.md",
    "Tune_4_Sao_Paulo_Rain.md",
    "Tune_5_The_Mirror.md",
    "Tune_6_Bright_Size_Life_2.md",
    "Tune_7_Monks_Dream.md",
    "Tune_8_Nefertitis_Shadow.md",
    "Tune_9_Greezy.md",
    "Tune_10_Hexagon.md",
    "Tune_11_Crystal_Silence.md",
    "Tune_12_Angular_Motion.md",
    "Tune_13_The_Void.md",
    "Tune_14_Solar_Flare.md",
    "Tune_15_Final_Departure.md",
    "Tune_16_Bop_Burner.md",
    "Tune_17_Blue_Minor.md",
    "Tune_18_Epistrophy_2.md",
]

# Tune metadata for TOC
TUNE_DATA = [
    ("1", "Blue Cycle", "Blues (Cycle)", "Bb", "4/4"),
    ("2", "Orbit", "Wayne Shorter", "F", "3/4"),
    ("3", "Rust & Chrome", "Scofield Funk", "E", "4/4"),
    ("4", "Sao Paulo Rain", "Bossa Nova", "D", "4/4"),
    ("5", "The Mirror", "Scofield Ballad", "Ab", "4/4"),
    ("6", "Bright Size Life 2", "Pat Metheny", "D", "4/4"),
    ("7", "Monk's Dream", "Experimental", "C", "4/4"),
    ("8", "Nefertiti's Shadow", "Wayne Shorter", "Eb", "4/4"),
    ("9", "Greezy", "Blues Shuffle", "G", "12/8"),
    ("10", "Hexagon", "Odd Meter", "B", "5/4"),
    ("11", "Crystal Silence", "ECM Ballad", "A", "4/4"),
    ("12", "Angular Motion", "Bebop Etude", "Gb", "4/4"),
    ("13", "The Void", "Free", "Free", "Free"),
    ("14", "Solar Flare", "Fusion", "C#", "7/8"),
    ("15", "Final Departure", "Ballad", "Db", "4/4"),
    ("16", "Bop Burner", "Bebop", "F", "4/4"),
    ("17", "Blue Minor", "Minor Bebop", "Cm", "4/4"),
    ("18", "Epistrophy 2", "Monk-Style", "Db", "4/4"),
]


class GCEWorkbookPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        if self.page_no() > 2:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 8, 'GCE Jazz Guitar Workbook', align='C')
            self.ln(10)
    
    def footer(self):
        if self.page_no() > 1:
            self.set_y(-12)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, str(self.page_no()), align='C')
    
    def safe_text(self, text):
        """Convert text to latin-1 safe characters."""
        replacements = {
            '—': '-', '–': '-', '"': '"', '"': '"', 
            ''': "'", ''': "'", '→': '->', '←': '<-',
            '♮': 'nat', '♯': '#', '♭': 'b', '°': 'dim',
            '•': '*', '…': '...', '×': 'x',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        try:
            text = text.encode('latin-1', errors='replace').decode('latin-1')
        except:
            text = text.encode('ascii', errors='replace').decode('ascii')
        return text.strip()
    
    def cover_page(self):
        self.add_page()
        self.ln(70)
        self.set_font('Helvetica', 'B', 40)
        self.set_text_color(40, 60, 80)
        self.cell(0, 15, 'GCE JAZZ GUITAR', align='C')
        self.ln(20)
        self.set_font('Helvetica', 'B', 32)
        self.set_text_color(50, 150, 220)
        self.cell(0, 15, 'WORKBOOK', align='C')
        self.ln(30)
        self.set_font('Helvetica', '', 14)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, 'Grand Criteria of Excellence Collection', align='C')
        self.ln(15)
        self.set_font('Helvetica', '', 12)
        self.cell(0, 8, '18 Tunes - Standard Analysis - Practice Etudes', align='C')
        self.ln(40)
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(160, 160, 160)
        self.cell(0, 8, 'Blues | Shorter | Scofield | Metheny | Bossa | Bebop', align='C')
    
    def table_of_contents(self):
        self.add_page()
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(40, 60, 80)
        self.cell(0, 12, 'TABLE OF CONTENTS', align='C')
        self.ln(15)
        
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(50, 150, 220)
        self.set_text_color(255, 255, 255)
        self.cell(15, 7, '#', border=1, fill=True, align='C')
        self.cell(45, 7, 'Title', border=1, fill=True, align='C')
        self.cell(50, 7, 'Style', border=1, fill=True, align='C')
        self.cell(20, 7, 'Key', border=1, fill=True, align='C')
        self.cell(20, 7, 'Time', border=1, fill=True, align='C')
        self.ln()
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(0, 0, 0)
        for i, (num, title, style, key, time) in enumerate(TUNE_DATA):
            self.set_fill_color(248, 248, 248) if i % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.cell(15, 6, num, border=1, fill=True, align='C')
            self.cell(45, 6, title, border=1, fill=True)
            self.cell(50, 6, style, border=1, fill=True)
            self.cell(20, 6, key, border=1, fill=True, align='C')
            self.cell(20, 6, time, border=1, fill=True, align='C')
            self.ln()
    
    def add_tune(self, content):
        """Process a tune's markdown content."""
        lines = content.split('\n')
        in_code = False
        in_table = False
        table_rows = []
        
        for line in lines:
            line = line.rstrip()
            
            # Code blocks
            if line.startswith('```'):
                in_code = not in_code
                if not in_code and line != '```':
                    pass
                continue
            
            if in_code:
                self.set_font('Courier', '', 8)
                self.set_text_color(100, 100, 100)
                self.set_x(15)
                text = self.safe_text(line) if line.strip() else ' '
                self.cell(180, 4, text[:90], ln=True)
                self.set_text_color(0, 0, 0)
                continue
            
            # Tables
            if '|' in line and line.count('|') >= 2:
                parts = line.split('|')
                cells = [p.strip() for p in parts if p.strip()]
                if cells and not all(set(c) <= set('-:| ') for c in cells):
                    if not in_table:
                        in_table = True
                        table_rows = []
                    table_rows.append(cells)
                continue
            else:
                if in_table and table_rows:
                    self.add_table(table_rows)
                    table_rows = []
                    in_table = False
            
            # Headers
            if line.startswith('# '):
                self.add_page()
                self.set_font('Helvetica', 'B', 16)
                self.set_text_color(40, 60, 80)
                self.set_x(10)
                text = self.safe_text(line[2:].replace('#', ''))
                self.cell(190, 10, text, ln=True)
                self.set_draw_color(50, 150, 220)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(6)
                
            elif line.startswith('## '):
                self.ln(4)
                self.set_font('Helvetica', 'B', 11)
                self.set_text_color(50, 70, 90)
                self.set_x(10)
                text = self.safe_text(line[3:].replace('#', ''))
                self.cell(190, 7, text, ln=True)
                self.ln(2)
                
            elif line.startswith('### '):
                self.ln(2)
                self.set_font('Helvetica', 'B', 10)
                self.set_text_color(100, 100, 100)
                self.set_x(10)
                text = self.safe_text(line[4:].replace('#', ''))
                self.cell(190, 6, text, ln=True)
                
            elif line.startswith('---'):
                self.ln(2)
                self.set_draw_color(200, 200, 200)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(4)
                
            elif line.startswith('> '):
                self.set_font('Helvetica', 'I', 9)
                self.set_text_color(80, 80, 80)
                self.set_x(15)
                text = self.safe_text(line[2:])
                self.multi_cell(180, 5, text)
                
            elif line.startswith('* ') or line.startswith('- '):
                self.set_font('Helvetica', '', 9)
                self.set_text_color(30, 30, 30)
                self.set_x(15)
                text = '- ' + self.safe_text(line[2:])
                self.multi_cell(180, 5, text)
                
            elif line.strip():
                self.set_font('Helvetica', '', 9)
                self.set_text_color(30, 30, 30)
                self.set_x(10)
                text = self.safe_text(line)
                if text:
                    self.multi_cell(190, 5, text)
            else:
                self.ln(2)
        
        if in_table and table_rows:
            self.add_table(table_rows)
    
    def add_table(self, rows):
        if not rows:
            return
        
        self.ln(2)
        num_cols = max(len(r) for r in rows)
        col_w = min(30, 180 / num_cols)
        
        # Header
        self.set_font('Helvetica', 'B', 7)
        self.set_fill_color(50, 150, 220)
        self.set_text_color(255, 255, 255)
        self.set_x(10)
        for i, cell in enumerate(rows[0]):
            if i < num_cols:
                self.cell(col_w, 5, self.safe_text(cell)[:15], border=1, fill=True, align='C')
        self.ln()
        
        # Data
        self.set_font('Helvetica', '', 7)
        self.set_text_color(0, 0, 0)
        for idx, row in enumerate(rows[1:]):
            self.set_fill_color(248, 248, 248) if idx % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.set_x(10)
            for i in range(num_cols):
                cell = row[i] if i < len(row) else ''
                self.cell(col_w, 4, self.safe_text(cell)[:15], border=1, fill=True)
            self.ln()
        self.ln(2)


def main():
    print("GCE Jazz Guitar Workbook Generator")
    print("=" * 40)
    
    pdf = GCEWorkbookPDF()
    pdf.set_title("GCE Jazz Guitar Workbook")
    pdf.set_author("GCE")
    
    print("  Creating cover...")
    pdf.cover_page()
    
    print("  Creating TOC...")
    pdf.table_of_contents()
    
    for filename in TUNE_FILES:
        filepath = MD_DIR / filename
        if filepath.exists():
            print(f"  Adding: {filename}")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            pdf.add_tune(content)
        else:
            print(f"  MISSING: {filename}")
    
    print("\nSaving PDF...")
    pdf.output(str(OUTPUT_PDF))
    
    size_kb = OUTPUT_PDF.stat().st_size / 1024
    print(f"\nDone! Created: {OUTPUT_PDF.name}")
    print(f"Size: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
