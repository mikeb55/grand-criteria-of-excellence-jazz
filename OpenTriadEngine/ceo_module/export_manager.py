"""
Export Manager for CEO Module
==============================

Unifies export formats across all engines:
- JSON with metadata
- MusicXML
- PDF
- Combined multi-engine outputs
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from xml.etree import ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import html


@dataclass
class ExportResult:
    """
    Result of an export operation.
    
    Attributes:
        format: Export format (json, musicxml, pdf, tab)
        filepath: Path to exported file (if saved)
        content: Raw content (string or bytes)
        success: Whether export succeeded
        error: Error message if failed
    """
    format: str
    filepath: Optional[str] = None
    content: Optional[Any] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class CEOExportPackage:
    """
    Complete export package from CEO.
    
    Attributes:
        exports: List of ExportResult objects
        metadata: Overall metadata
        engines_used: List of engines that contributed
        timestamp: When the export was created
    """
    exports: List[ExportResult]
    metadata: Dict
    engines_used: List[str]
    timestamp: str


class ExportManager:
    """
    Manages unified exports across all CEO engines.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the export manager.
        
        Args:
            output_dir: Default output directory
        """
        self.output_dir = Path(output_dir) if output_dir else Path("./exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_json(
        self,
        data: Dict,
        metadata: Dict = None,
        filepath: str = None
    ) -> ExportResult:
        """
        Export data as JSON.
        
        Args:
            data: Data to export
            metadata: Additional metadata to include
            filepath: Optional file path
        
        Returns:
            ExportResult
        """
        try:
            output = {
                "ceo_version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
                "data": data
            }
            
            content = json.dumps(output, indent=2, default=str)
            
            if filepath:
                path = Path(filepath)
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return ExportResult(
                format="json",
                filepath=str(filepath) if filepath else None,
                content=content,
                success=True
            )
        except Exception as e:
            return ExportResult(
                format="json",
                success=False,
                error=str(e)
            )
    
    def export_musicxml(
        self,
        musicxml_content: str,
        title: str = "CEO Output",
        filepath: str = None
    ) -> ExportResult:
        """
        Export or merge MusicXML content.
        
        Args:
            musicxml_content: MusicXML string
            title: Score title
            filepath: Optional file path
        
        Returns:
            ExportResult
        """
        try:
            # If content is already valid MusicXML, use it
            if musicxml_content and musicxml_content.strip().startswith("<?xml"):
                content = musicxml_content
            else:
                # Generate basic MusicXML wrapper
                content = self._generate_musicxml_wrapper(title)
            
            if filepath:
                path = Path(filepath)
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return ExportResult(
                format="musicxml",
                filepath=str(filepath) if filepath else None,
                content=content,
                success=True
            )
        except Exception as e:
            return ExportResult(
                format="musicxml",
                success=False,
                error=str(e)
            )
    
    def _generate_musicxml_wrapper(self, title: str) -> str:
        """Generate a basic MusicXML document."""
        root = ET.Element("score-partwise", version="4.0")
        
        work = ET.SubElement(root, "work")
        work_title = ET.SubElement(work, "work-title")
        work_title.text = title
        
        identification = ET.SubElement(root, "identification")
        creator = ET.SubElement(identification, "creator", type="composer")
        creator.text = "CEO Module"
        
        encoding = ET.SubElement(identification, "encoding")
        software = ET.SubElement(encoding, "software")
        software.text = "Combined Engine Orchestrator v1.0"
        
        part_list = ET.SubElement(root, "part-list")
        score_part = ET.SubElement(part_list, "score-part", id="P1")
        part_name = ET.SubElement(score_part, "part-name")
        part_name.text = "Part 1"
        
        part = ET.SubElement(root, "part", id="P1")
        measure = ET.SubElement(part, "measure", number="1")
        
        attributes = ET.SubElement(measure, "attributes")
        divisions = ET.SubElement(attributes, "divisions")
        divisions.text = "1"
        
        xml_string = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")
    
    def export_html(
        self,
        data: Dict,
        title: str = "CEO Output",
        filepath: str = None
    ) -> ExportResult:
        """
        Export as HTML (for PDF conversion).
        
        Args:
            data: Data to render
            title: Document title
            filepath: Optional file path
        
        Returns:
            ExportResult
        """
        try:
            content = self._generate_html(data, title)
            
            if filepath:
                path = Path(filepath)
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return ExportResult(
                format="html",
                filepath=str(filepath) if filepath else None,
                content=content,
                success=True
            )
        except Exception as e:
            return ExportResult(
                format="html",
                success=False,
                error=str(e)
            )
    
    def _generate_html(self, data: Dict, title: str) -> str:
        """Generate HTML document from data."""
        engines_used = data.get("engines_used", [])
        outputs = data.get("outputs", [])
        metadata = data.get("metadata", {})
        
        outputs_html = ""
        for i, output in enumerate(outputs):
            engine = output.get("engine", "unknown")
            engine_data = output.get("data", {})
            
            outputs_html += f"""
            <div class="engine-output">
                <h2>Output from {html.escape(engine)}</h2>
                <pre><code>{html.escape(json.dumps(engine_data, indent=2, default=str)[:2000])}</code></pre>
            </div>
            """
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono&display=swap');
        
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --accent: #58a6ff;
            --accent-bright: #79c0ff;
            --text: #c9d1d9;
            --text-muted: #8b949e;
            --border: #30363d;
            --success: #3fb950;
            --warning: #d29922;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Space Grotesk', sans-serif;
            background: var(--bg-primary);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent-bright);
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: var(--text-muted);
            font-size: 1.1rem;
        }}
        
        .engines-badge {{
            display: inline-flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        
        .badge {{
            background: var(--bg-secondary);
            border: 1px solid var(--accent);
            color: var(--accent);
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        
        h2 {{
            font-size: 1.5rem;
            color: var(--accent);
            margin: 2rem 0 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }}
        
        .engine-output {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        
        .engine-output h2 {{
            margin-top: 0;
            border: none;
            padding-bottom: 0;
        }}
        
        pre {{
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 1rem;
            overflow-x: auto;
            margin-top: 1rem;
        }}
        
        code {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: var(--text);
        }}
        
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }}
        
        .meta-item {{
            background: var(--bg-secondary);
            padding: 1rem;
            border-radius: 6px;
            border: 1px solid var(--border);
        }}
        
        .meta-label {{
            color: var(--text-muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .meta-value {{
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--accent-bright);
        }}
        
        footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        
        @media print {{
            body {{
                background: white;
                color: black;
            }}
            .container {{
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{html.escape(title)}</h1>
            <p class="subtitle">Generated by Combined Engine Orchestrator</p>
            <div class="engines-badge">
                {"".join(f'<span class="badge">{html.escape(e)}</span>' for e in engines_used)}
            </div>
        </header>
        
        <section class="metadata">
            <div class="meta-item">
                <div class="meta-label">Key</div>
                <div class="meta-value">{html.escape(str(metadata.get('key', 'C')))}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Scale</div>
                <div class="meta-value">{html.escape(str(metadata.get('scale', 'major')))}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Mode</div>
                <div class="meta-value">{html.escape(str(metadata.get('mode', 'modal')))}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Bars</div>
                <div class="meta-value">{metadata.get('bars', 4)}</div>
            </div>
        </section>
        
        {outputs_html}
        
        <footer>
            <p>Combined Engine Orchestrator v1.0 | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html_content
    
    def merge_musicxml(
        self,
        musicxml_list: List[str],
        title: str = "Combined Score"
    ) -> str:
        """
        Merge multiple MusicXML documents.
        
        Args:
            musicxml_list: List of MusicXML strings
            title: Title for merged document
        
        Returns:
            Merged MusicXML string
        """
        if not musicxml_list:
            return self._generate_musicxml_wrapper(title)
        
        if len(musicxml_list) == 1:
            return musicxml_list[0]
        
        # For now, return the first valid MusicXML
        # A full implementation would merge the parts
        for xml in musicxml_list:
            if xml and xml.strip().startswith("<?xml"):
                return xml
        
        return self._generate_musicxml_wrapper(title)
    
    def create_export_package(
        self,
        workflow_result: Any,
        request: Any,
        output_dir: str = None,
        base_name: str = "ceo_output"
    ) -> CEOExportPackage:
        """
        Create a complete export package from a workflow result.
        
        Args:
            workflow_result: Result from the router
            request: Original CEORequest
            output_dir: Output directory
            base_name: Base filename
        
        Returns:
            CEOExportPackage with all exports
        """
        output_dir = Path(output_dir) if output_dir else self.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exports = []
        engines_used = []
        
        # Collect data from all engine results
        combined_data = {
            "workflow": "ceo_export",
            "engines_used": [],
            "outputs": [],
            "metadata": {
                "key": request.key,
                "scale": request.scale,
                "mode": request.mode,
                "bars": request.bars,
            }
        }
        
        musicxml_parts = []
        
        for result in workflow_result.engine_results:
            if result.success:
                engines_used.append(result.engine.value)
                combined_data["engines_used"].append(result.engine.value)
                
                if result.json_output:
                    combined_data["outputs"].append({
                        "engine": result.engine.value,
                        "data": result.json_output,
                        "metadata": result.metadata
                    })
                
                if result.musicxml_output:
                    musicxml_parts.append(result.musicxml_output)
        
        # Export JSON
        if "json" in request.output_formats:
            json_result = self.export_json(
                combined_data,
                combined_data["metadata"],
                str(output_dir / f"{base_name}.json")
            )
            exports.append(json_result)
        
        # Export MusicXML
        if "musicxml" in request.output_formats:
            merged_xml = self.merge_musicxml(musicxml_parts, base_name)
            xml_result = self.export_musicxml(
                merged_xml,
                base_name,
                str(output_dir / f"{base_name}.musicxml")
            )
            exports.append(xml_result)
        
        # Export HTML/PDF
        if "pdf" in request.output_formats or "html" in request.output_formats:
            html_result = self.export_html(
                combined_data,
                base_name.replace("_", " ").title(),
                str(output_dir / f"{base_name}.html")
            )
            exports.append(html_result)
        
        return CEOExportPackage(
            exports=exports,
            metadata=combined_data["metadata"],
            engines_used=engines_used,
            timestamp=datetime.now().isoformat()
        )

