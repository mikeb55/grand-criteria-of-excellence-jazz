"""
Convert Analysis Markdown files to print-friendly HTML (for PDF printing)
"""

import os
from pathlib import Path
import re

CSS_STYLE = """
<style>
    @page { size: letter; margin: 0.75in; }
    @media print { 
        body { font-size: 11pt; }
        pre, table { page-break-inside: avoid; }
        h1, h2, h3 { page-break-after: avoid; }
    }
    * { box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 12pt;
        line-height: 1.6;
        color: #222;
        max-width: 850px;
        margin: 0 auto;
        padding: 40px 20px;
        background: #fff;
    }
    h1 { font-size: 24pt; color: #1a1a2e; border-bottom: 3px solid #333; padding-bottom: 10px; margin-top: 0; }
    h2 { font-size: 16pt; color: #222; margin-top: 30px; border-bottom: 1px solid #999; padding-bottom: 5px; }
    h3 { font-size: 13pt; color: #333; margin-top: 20px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 10pt; }
    th { background-color: #f0f0f0; color: #222; padding: 10px; text-align: left; border: 1px solid #333; }
    td { padding: 8px; border: 1px solid #ccc; }
    tr:nth-child(even) { background-color: #fafafa; }
    code { font-family: Consolas, monospace; background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
    pre { background-color: #f8f8f8; padding: 15px; border-radius: 5px; border: 1px solid #ccc; overflow-x: auto; font-size: 10pt; }
    pre code { background: none; padding: 0; }
    hr { border: none; border-top: 2px solid #333; margin: 35px 0; }
    strong { color: #111; }
    blockquote { border-left: 3px solid #666; margin: 20px 0; padding: 10px 20px; background-color: #fafafa; }
</style>
"""

def markdown_to_html(md_content: str, title: str) -> str:
    """Simple markdown to HTML converter."""
    html = md_content
    
    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Code blocks
    html = re.sub(r'```([^`]+)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    
    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Bold
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    
    # Horizontal rules
    html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)
    
    # Tables (simple conversion)
    lines = html.split('\n')
    in_table = False
    new_lines = []
    for line in lines:
        if '|' in line and not line.strip().startswith('<'):
            if not in_table:
                new_lines.append('<table>')
                in_table = True
            if line.strip().startswith('|--') or line.strip().startswith('| --'):
                continue  # Skip separator row
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells:
                tag = 'th' if not any('<td>' in l for l in new_lines[-5:]) else 'td'
                row = '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>'
                new_lines.append(row)
        else:
            if in_table:
                new_lines.append('</table>')
                in_table = False
            new_lines.append(line)
    if in_table:
        new_lines.append('</table>')
    html = '\n'.join(new_lines)
    
    # Paragraphs (wrap remaining text)
    html = re.sub(r'\n\n+', '</p><p>', html)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    {CSS_STYLE}
</head>
<body>
{html}
</body>
</html>
"""

def main():
    print("Converting Analysis Markdown to HTML (for PDF printing)...")
    
    base_orbit = Path(r"C:\Users\mike\Documents\Cursor AI Projects\GCE-Jazz\Trio Tunes\Tune02_Orbit\Analysis")
    base_crystal = Path(r"C:\Users\mike\Documents\Cursor AI Projects\GCE-Jazz\Trio Tunes\Tune11_Crystal_Silence\Analysis")
    
    files = [
        (base_orbit / "Orbit_Harmonic_Analysis.md", "Orbit - Harmonic Analysis"),
        (base_orbit / "Orbit_Voice_Leading_Guide.md", "Orbit - Voice Leading Guide"),
        (base_crystal / "Crystal_Silence_Harmonic_Analysis.md", "Crystal Silence - Harmonic Analysis"),
        (base_crystal / "Crystal_Silence_Voice_Leading_Guide.md", "Crystal Silence - Voice Leading Guide"),
    ]
    
    for md_path, title in files:
        if md_path.exists():
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = markdown_to_html(md_content, title)
            html_path = md_path.with_suffix('.html')
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"[OK] Created: {html_path}")
    
    print("\nHTML files created! Open in browser and print to PDF.")
    print("\nTo print to PDF:")
    print("  1. Open each .html file in a browser")
    print("  2. Press Ctrl+P")
    print("  3. Select 'Save as PDF' as destination")
    print("  4. Save to the same Analysis folder")

if __name__ == "__main__":
    main()

