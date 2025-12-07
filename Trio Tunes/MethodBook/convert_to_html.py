#!/usr/bin/env python3
"""
Convert Method Book Markdown chapters to styled HTML
With clickable Table of Contents and navigation
Printer-friendly format
"""

import os
import re
import markdown

print("=" * 50)
print("  Method Book HTML Converter")
print("  GCE Jazz - Trio Tunes Collection")
print("  (With Table of Contents & Navigation)")
print("=" * 50)

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
chapters_dir = os.path.join(script_dir, "Chapters")
html_output_dir = os.path.join(script_dir, "HTML")

# Create output directory
os.makedirs(html_output_dir, exist_ok=True)

# Chapter metadata for TOC
chapters_info = [
    ("00_Introduction", "Introduction", ["How to Use This Book", "Core Concepts", "The 15 Tunes at a Glance"]),
    ("01_Blue_Cycle", "Blue Cycle", ["The Form", "Scale Palette", "Triad Pairs", "The Three Choruses"]),
    ("02_Orbit", "Orbit", ["The Form", "Scale Palette", "The Three Choruses", "The 3/4 Feel"]),
    ("03_Rust_And_Chrome", "Rust & Chrome", ["The Form", "Scale Palette", "The Three Choruses", "Legato Slides"]),
    ("04_Sao_Paulo_Rain", "Sao Paulo Rain", ["The Form", "The Bossa Rhythm", "The Three Choruses", "The Bossa Touch"]),
    ("05_The_Mirror", "The Mirror", ["The Form", "Wide Intervals", "The Three Choruses", "Volume Swells"]),
    ("06_Bright_Size_Life_2", "Bright Size Life 2", ["The Form", "Scale Palette", "The Three Choruses", "The Metheny Touch"]),
    ("07_Monks_Dream", "Monk's Dream", ["The Form", "Whole-Tone Scale", "The Three Choruses", "Rhythmic Displacement"]),
    ("08_Nefertitis_Shadow", "Nefertiti's Shadow", ["The Form", "Lydian as Default", "The Three Choruses", "Playing at 180 BPM"]),
    ("09_Greezy", "Greezy", ["The Form", "The 12/8 Feel", "The Three Choruses", "The Shuffle Feel"]),
    ("10_Hexagon", "Hexagon", ["Understanding 5/4", "Hexatonic Scales", "The Three Choruses", "Odd Meter Tips"]),
    ("11_Crystal_Silence", "Crystal Silence", ["The Form", "Campanella Technique", "The Three Choruses", "ECM Sound"]),
    ("12_Angular_Motion", "Angular Motion", ["The Form", "Bebop Scales", "The Three Choruses", "Economy Picking"]),
    ("13_The_Void", "The Void", ["The Concept", "Extended Techniques", "The Framework", "Listening Strategies"]),
    ("14_Solar_Flare", "Solar Flare", ["Understanding 7/8", "Scale Palette", "The Three Choruses", "Speed Building"]),
    ("15_Final_Departure", "Final Departure", ["The Form", "Drop-2 Voicings", "The Three Choruses", "Rubato Playing"]),
    ("16_Conclusion", "Conclusion", ["What You've Learned", "Where to Go From Here", "Core Principles"]),
]

# PRINTER-FRIENDLY CSS with TOC styles
css = '''
<style>
@page {
    size: letter;
    margin: 0.75in 0.75in 1in 0.75in;
}

@media print {
    body { font-size: 11pt; }
    .page-break { page-break-before: always; }
    pre, table { page-break-inside: avoid; }
    h1, h2, h3 { page-break-after: avoid; }
    .no-print { display: none; }
    .back-to-toc { display: none; }
    a { text-decoration: none; color: #222; }
}

* { box-sizing: border-box; }

body {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 12pt;
    line-height: 1.6;
    color: #222;
    max-width: 850px;
    margin: 0 auto;
    padding: 40px 20px;
    background: #fff;
}

/* TABLE OF CONTENTS STYLES */
.toc-container {
    border: 2px solid #333;
    padding: 30px 40px;
    margin: 30px 0 50px 0;
    background: #fafafa;
}

.toc-container h2 {
    text-align: center;
    border-bottom: 2px solid #333;
    padding-bottom: 15px;
    margin-top: 0;
    font-size: 22pt;
}

.toc-chapter {
    margin: 20px 0;
    padding: 10px 0;
    border-bottom: 1px dotted #999;
}

.toc-chapter:last-child {
    border-bottom: none;
}

.toc-chapter-title {
    font-size: 14pt;
    font-weight: bold;
    margin-bottom: 8px;
}

.toc-chapter-title a {
    color: #1a1a2e;
    text-decoration: none;
}

.toc-chapter-title a:hover {
    text-decoration: underline;
}

.toc-chapter-num {
    color: #666;
    font-weight: normal;
}

.toc-subheadings {
    margin-left: 25px;
    font-size: 11pt;
    color: #444;
}

.toc-subheadings a {
    color: #444;
    text-decoration: none;
    margin-right: 15px;
}

.toc-subheadings a:hover {
    text-decoration: underline;
}

/* BACK TO TOC LINK */
.back-to-toc {
    display: inline-block;
    margin-top: 20px;
    padding: 8px 15px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 10pt;
    color: #333;
    text-decoration: none;
}

.back-to-toc:hover {
    background: #e0e0e0;
}

/* HEADINGS */
h1 {
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 26pt;
    color: #1a1a2e;
    border-bottom: 3px solid #333;
    padding-bottom: 10px;
    margin-top: 40px;
    margin-bottom: 20px;
}

h2 {
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 16pt;
    color: #222;
    margin-top: 30px;
    border-bottom: 1px solid #999;
    padding-bottom: 5px;
}

h3 {
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13pt;
    color: #333;
    margin-top: 20px;
}

h4 {
    font-size: 12pt;
    font-weight: bold;
    color: #222;
    margin-top: 15px;
}

p { margin-bottom: 12px; text-align: justify; }

ul, ol { margin-left: 25px; margin-bottom: 12px; }

li { margin-bottom: 6px; }

/* TABLES - Printer friendly */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 10pt;
    border: 1px solid #333;
}

th {
    background-color: #f0f0f0;
    color: #222;
    padding: 10px 12px;
    text-align: left;
    font-weight: bold;
    border: 1px solid #333;
}

td {
    padding: 8px 12px;
    border: 1px solid #ccc;
}

tr:nth-child(even) { background-color: #fafafa; }

/* CODE - Printer friendly */
code {
    font-family: 'Consolas', 'Courier New', monospace;
    background-color: #f5f5f5;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10pt;
    border: 1px solid #ddd;
}

pre {
    background-color: #f8f8f8;
    color: #222;
    padding: 15px 20px;
    border-radius: 5px;
    border: 1px solid #ccc;
    overflow-x: auto;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
    line-height: 1.4;
}

pre code {
    background-color: transparent;
    padding: 0;
    border: none;
    color: #222;
}

blockquote {
    border-left: 3px solid #666;
    margin: 20px 0;
    padding: 10px 20px;
    background-color: #fafafa;
    font-style: italic;
}

hr {
    border: none;
    border-top: 2px solid #333;
    margin: 35px 0;
}

strong { color: #111; }
em { color: #333; }
a { color: #333; }

/* Header banner */
.header-banner {
    border: 2px solid #333;
    padding: 25px 30px;
    margin: 0 0 40px 0;
    text-align: center;
    background-color: #fafafa;
}

.header-banner h1 {
    color: #111;
    border: none;
    margin: 0 0 10px 0;
    padding: 0;
    font-size: 28pt;
}

.header-banner p {
    color: #444;
    margin: 5px 0;
    text-align: center;
    font-size: 12pt;
}

.footer {
    margin-top: 60px;
    padding-top: 20px;
    border-top: 1px solid #ccc;
    text-align: center;
    color: #666;
    font-size: 10pt;
}

.chapter-divider {
    border-top: 3px double #333;
    margin: 50px 0 30px 0;
    padding-top: 20px;
}

.print-instructions {
    background-color: #fffde7;
    border: 1px solid #ffd54f;
    padding: 15px 20px;
    margin-bottom: 30px;
    border-radius: 5px;
}

@media print {
    .print-instructions { display: none; }
    .header-banner { margin-top: 0; }
}
</style>
'''

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

def add_ids_to_headings(html_content, chapter_slug):
    """Add anchor IDs to h2 headings for navigation"""
    def replace_h2(match):
        heading_text = match.group(1)
        heading_id = f"{chapter_slug}-{slugify(heading_text)}"
        return f'<h2 id="{heading_id}">{heading_text}</h2>'
    
    return re.sub(r'<h2>([^<]+)</h2>', replace_h2, html_content)

def generate_toc_html():
    """Generate the Table of Contents HTML"""
    toc_html = '''
<div class="toc-container" id="table-of-contents">
    <h2>📖 TABLE OF CONTENTS</h2>
'''
    for i, (filename, title, subheadings) in enumerate(chapters_info):
        chapter_slug = slugify(filename)
        chapter_num = filename.split('_')[0]
        
        toc_html += f'''
    <div class="toc-chapter">
        <div class="toc-chapter-title">
            <span class="toc-chapter-num">{chapter_num}.</span>
            <a href="#{chapter_slug}">{title}</a>
        </div>
        <div class="toc-subheadings">
'''
        for subheading in subheadings[:4]:  # Limit to 4 subheadings
            sub_slug = f"{chapter_slug}-{slugify(subheading)}"
            toc_html += f'            <a href="#{sub_slug}">• {subheading}</a>\n'
        
        toc_html += '        </div>\n    </div>\n'
    
    toc_html += '</div>\n'
    return toc_html

# Get all markdown files sorted
md_files = sorted([f for f in os.listdir(chapters_dir) if f.endswith('.md')])

print(f"\nFound {len(md_files)} chapters to convert\n")

# Convert individual files
converted = 0
for md_file in md_files:
    md_path = os.path.join(chapters_dir, md_file)
    html_name = md_file.replace('.md', '.html')
    html_path = os.path.join(html_output_dir, html_name)
    
    print(f"  Converting: {md_file}")
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
        
        title = md_file.replace('.md', '').replace('_', ' ')
        full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} - Trio Tunes Method Book</title>
    {css}
</head>
<body>
    {html_content}
    <div class="footer">
        <p>GCE Jazz - Trio Tunes Method Book © 2025</p>
    </div>
</body>
</html>
'''
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"    -> Created: {html_name}")
        converted += 1
        
    except Exception as e:
        print(f"    -> FAILED: {e}")

# Create combined HTML with TOC
print("\n  Creating complete Method Book with Table of Contents...")
try:
    combined_html_parts = []
    
    # Add TOC first
    toc_html = generate_toc_html()
    
    for i, md_file in enumerate(md_files):
        md_path = os.path.join(chapters_dir, md_file)
        filename = md_file.replace('.md', '')
        chapter_slug = slugify(filename)
        
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
        
        # Add anchor ID to chapter and IDs to subheadings
        html_content = f'<div id="{chapter_slug}">\n' + html_content
        html_content = add_ids_to_headings(html_content, chapter_slug)
        
        # Add "Back to TOC" link
        html_content += '\n<a href="#table-of-contents" class="back-to-toc">↑ Back to Table of Contents</a>\n</div>'
        
        # Add chapter divider (except first)
        if i > 0:
            combined_html_parts.append('<div class="chapter-divider page-break"></div>')
        
        combined_html_parts.append(html_content)
    
    combined_content = "\n".join(combined_html_parts)
    
    full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Trio Tunes Method Book - Complete</title>
    {css}
</head>
<body>
    <div class="print-instructions no-print">
        <strong>📄 PRINTER-FRIENDLY with NAVIGATION</strong><br>
        • Click any chapter or section in the Table of Contents to jump there<br>
        • Click "Back to Table of Contents" to return<br>
        • To save as PDF: Press <strong>Ctrl+P</strong> → Select <strong>"Save as PDF"</strong> → Click <strong>Save</strong>
    </div>
    
    <div class="header-banner">
        <h1>TRIO TUNES METHOD BOOK</h1>
        <p><strong>A Comprehensive Guide to Jazz Guitar Etudes</strong></p>
        <p>Grand Criteria of Excellence (GCE) Jazz Collection</p>
        <p><em>15 Original Tunes • 17 Chapters • Complete Practice Guide</em></p>
    </div>
    
    {toc_html}
    
    {combined_content}
    
    <div class="footer">
        <p>GCE Jazz - Trio Tunes Method Book © 2025</p>
        <p><em>Grand Criteria of Excellence</em></p>
    </div>
</body>
</html>
'''
    
    combined_html_path = os.path.join(html_output_dir, "MethodBook_Complete.html")
    with open(combined_html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"    -> Created: MethodBook_Complete.html")
    converted += 1
    
except Exception as e:
    print(f"    -> FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print(f"  Complete! Created: {converted} files")
print("=" * 50)
print("\n✅ FEATURES:")
print("   • Clickable Table of Contents")
print("   • Links to chapters AND key subheadings")
print("   • 'Back to TOC' links after each chapter")
print("   • Printer-friendly (no dark backgrounds)")
print("\n📁 Output: Trio Tunes/MethodBook/HTML/MethodBook_Complete.html")
