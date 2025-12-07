#!/usr/bin/env python3
"""
Convert Method Book Markdown chapters to PDF
Uses markdown + weasyprint
"""

import os
import markdown
from weasyprint import HTML, CSS

print("=" * 50)
print("  Method Book PDF Converter")
print("  GCE Jazz - Trio Tunes Collection")
print("=" * 50)

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
chapters_dir = os.path.join(script_dir, "Chapters")
pdf_output_dir = os.path.join(script_dir, "PDF")

# Create output directory
os.makedirs(pdf_output_dir, exist_ok=True)

# CSS for beautiful PDF output
css = CSS(string='''
@page {
    size: letter;
    margin: 1in 0.75in;
    @bottom-center {
        content: "GCE Jazz - Trio Tunes Method Book";
        font-size: 9pt;
        color: #666;
    }
    @bottom-right {
        content: counter(page);
        font-size: 9pt;
        color: #666;
    }
}

body {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #222;
}

h1 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 24pt;
    color: #1a1a2e;
    border-bottom: 3px solid #4a4e69;
    padding-bottom: 10px;
    margin-top: 0;
}

h2 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 16pt;
    color: #22223b;
    margin-top: 30px;
    border-bottom: 1px solid #9a8c98;
    padding-bottom: 5px;
}

h3 {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 13pt;
    color: #4a4e69;
    margin-top: 20px;
}

h4 {
    font-size: 11pt;
    font-weight: bold;
    color: #22223b;
}

p {
    margin-bottom: 12px;
    text-align: justify;
}

ul, ol {
    margin-left: 20px;
    margin-bottom: 12px;
}

li {
    margin-bottom: 4px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 10pt;
}

th {
    background-color: #22223b;
    color: white;
    padding: 8px 10px;
    text-align: left;
    font-weight: bold;
}

td {
    padding: 6px 10px;
    border-bottom: 1px solid #ddd;
}

tr:nth-child(even) {
    background-color: #f8f8f8;
}

code {
    font-family: 'Consolas', 'Monaco', monospace;
    background-color: #f4f4f4;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 10pt;
}

pre {
    background-color: #2d2d2d;
    color: #f8f8f2;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 9pt;
    line-height: 1.4;
}

pre code {
    background-color: transparent;
    padding: 0;
    color: #f8f8f2;
}

blockquote {
    border-left: 4px solid #4a4e69;
    margin: 15px 0;
    padding: 10px 20px;
    background-color: #f9f9f9;
    font-style: italic;
}

hr {
    border: none;
    border-top: 2px solid #4a4e69;
    margin: 30px 0;
}

strong {
    color: #22223b;
}

em {
    color: #4a4e69;
}

a {
    color: #4a4e69;
    text-decoration: none;
}
''')

# Get all markdown files sorted
md_files = sorted([f for f in os.listdir(chapters_dir) if f.endswith('.md')])

print(f"\nFound {len(md_files)} chapters to convert\n")

# Convert each file
converted = 0
failed = 0

for md_file in md_files:
    md_path = os.path.join(chapters_dir, md_file)
    pdf_name = md_file.replace('.md', '.pdf')
    pdf_path = os.path.join(pdf_output_dir, pdf_name)
    
    print(f"  Converting: {md_file}")
    
    try:
        # Read markdown
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert to HTML
        html_content = markdown.markdown(
            md_content, 
            extensions=['tables', 'fenced_code', 'codehilite', 'toc']
        )
        
        # Wrap in HTML document
        full_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{md_file.replace('.md', '').replace('_', ' ')}</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        '''
        
        # Convert to PDF
        HTML(string=full_html).write_pdf(pdf_path, stylesheets=[css])
        print(f"    -> Created: {pdf_name}")
        converted += 1
        
    except Exception as e:
        print(f"    -> FAILED: {e}")
        failed += 1

# Also create a combined PDF
print("\n  Creating combined Method Book PDF...")
try:
    combined_md = ""
    for md_file in md_files:
        md_path = os.path.join(chapters_dir, md_file)
        with open(md_path, 'r', encoding='utf-8') as f:
            combined_md += f.read() + "\n\n---\n\n"
    
    html_content = markdown.markdown(
        combined_md,
        extensions=['tables', 'fenced_code', 'codehilite', 'toc']
    )
    
    full_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Trio Tunes Method Book - Complete</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    '''
    
    combined_pdf_path = os.path.join(pdf_output_dir, "MethodBook_Complete.pdf")
    HTML(string=full_html).write_pdf(combined_pdf_path, stylesheets=[css])
    print(f"    -> Created: MethodBook_Complete.pdf")
    converted += 1
    
except Exception as e:
    print(f"    -> FAILED: {e}")
    failed += 1

print("\n" + "=" * 50)
print(f"  Complete! Converted: {converted}, Failed: {failed}")
print("=" * 50)
print(f"\nPDFs saved to: {pdf_output_dir}")


