"""
Output Formatter for Triad Pair Solo Engine
=============================================

Handles output formats:
- JSON Phrase Data
- MusicXML Export
- PDF Phrase Sheet generation
"""

from dataclasses import asdict
from typing import List, Dict, Optional, Any
import json
from xml.etree import ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import html

try:
    from .inputs import SoloEngineConfig
    from .triad_pairs import TriadPair
    from .patterns import PatternNote, MelodicCell
    from .phrase_assembler import SoloPhrase, PhraseStructure
except ImportError:
    from inputs import SoloEngineConfig
    from triad_pairs import TriadPair
    from patterns import PatternNote, MelodicCell
    from phrase_assembler import SoloPhrase, PhraseStructure


class SoloOutputFormatter:
    """
    Formats solo phrases for various output formats.
    """
    
    def __init__(self, config: SoloEngineConfig):
        """
        Initialize the output formatter.
        
        Args:
            config: Solo engine configuration
        """
        self.config = config
    
    # =========================================================================
    # JSON OUTPUT
    # =========================================================================
    
    def to_json(
        self,
        phrase: SoloPhrase,
        include_metadata: bool = True
    ) -> Dict:
        """
        Convert a solo phrase to JSON-serializable dictionary.
        
        Args:
            phrase: SoloPhrase to convert
            include_metadata: Whether to include full metadata
        
        Returns:
            Dictionary ready for JSON serialization
        """
        result = {
            "phrase": {
                "structure": phrase.structure.value,
                "bar_count": phrase.bar_count,
                "rhythmic_style": phrase.rhythmic_style.value,
                "total_duration": phrase.total_duration(),
                "pitch_range": {
                    "low": phrase.get_pitch_range()[0],
                    "high": phrase.get_pitch_range()[1]
                }
            },
            "notes": [self._note_to_dict(n) for n in phrase.notes],
            "triad_pairs": [self._triad_pair_to_dict(tp) for tp in phrase.triad_pairs],
        }
        
        if include_metadata:
            result["config"] = self.config.to_dict()
            result["phrase"]["metadata"] = phrase.metadata
            result["voice_leading"] = [
                {
                    "from_voicing": vl.from_voicing,
                    "to_voicing": vl.to_voicing,
                    "motion_intervals": vl.motion_intervals,
                    "motion_types": vl.motion_types,
                    "narrative": vl.narrative,
                    "tension_level": vl.tension_level
                }
                for vl in phrase.voice_leading_analysis
            ]
        
        return result
    
    def _note_to_dict(self, note: PatternNote) -> Dict:
        """Convert a PatternNote to dictionary."""
        return {
            "pitch": note.pitch,
            "pitch_name": note.pitch_name,
            "duration": note.duration,
            "triad_source": note.triad_source,
            "voice": note.voice,
            "string": note.string,
            "fret": note.fret,
            "articulation": note.articulation
        }
    
    def _triad_pair_to_dict(self, tp: TriadPair) -> Dict:
        """Convert a TriadPair to dictionary."""
        return {
            "triad_a": {
                "root": tp.triad_a[0],
                "quality": tp.triad_a[1]
            },
            "triad_b": {
                "root": tp.triad_b[0],
                "quality": tp.triad_b[1]
            },
            "relationship": tp.relationship,
            "tension_level": tp.tension_level,
            "source_scale": tp.source_scale,
            "chord_context": tp.chord_context
        }
    
    def save_json(
        self,
        phrase: SoloPhrase,
        filepath: str,
        include_metadata: bool = True
    ):
        """
        Save phrase to JSON file.
        
        Args:
            phrase: SoloPhrase to save
            filepath: Output file path
            include_metadata: Whether to include metadata
        """
        data = self.to_json(phrase, include_metadata)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    # =========================================================================
    # MUSICXML OUTPUT
    # =========================================================================
    
    def to_musicxml(
        self,
        phrase: SoloPhrase,
        title: str = "Triad Pair Solo"
    ) -> str:
        """
        Convert a solo phrase to MusicXML format.
        
        Args:
            phrase: SoloPhrase to convert
            title: Title for the score
        
        Returns:
            MusicXML string
        """
        # Create root element
        root = ET.Element("score-partwise", version="4.0")
        
        # Work title
        work = ET.SubElement(root, "work")
        work_title = ET.SubElement(work, "work-title")
        work_title.text = title
        
        # Identification
        identification = ET.SubElement(root, "identification")
        creator = ET.SubElement(identification, "creator", type="composer")
        creator.text = "Triad Pair Solo Engine"
        
        encoding = ET.SubElement(identification, "encoding")
        software = ET.SubElement(encoding, "software")
        software.text = "Triad Pair Solo Engine v1.0"
        
        # Part list
        part_list = ET.SubElement(root, "part-list")
        score_part = ET.SubElement(part_list, "score-part", id="P1")
        part_name = ET.SubElement(score_part, "part-name")
        part_name.text = "Guitar"
        
        # Part content
        part = ET.SubElement(root, "part", id="P1")
        
        # Group notes into measures
        measures = self._group_notes_into_measures(phrase.notes)
        
        for measure_num, measure_notes in enumerate(measures, 1):
            measure = ET.SubElement(part, "measure", number=str(measure_num))
            
            # Attributes for first measure
            if measure_num == 1:
                attributes = ET.SubElement(measure, "attributes")
                
                divisions = ET.SubElement(attributes, "divisions")
                divisions.text = "4"  # 4 divisions per quarter note
                
                key = ET.SubElement(attributes, "key")
                fifths = ET.SubElement(key, "fifths")
                fifths.text = str(self._key_to_fifths(self.config.key))
                
                time = ET.SubElement(attributes, "time")
                beats = ET.SubElement(time, "beats")
                beats.text = "4"
                beat_type = ET.SubElement(time, "beat-type")
                beat_type.text = "4"
                
                clef = ET.SubElement(attributes, "clef")
                sign = ET.SubElement(clef, "sign")
                sign.text = "G"
                line = ET.SubElement(clef, "line")
                line.text = "2"
            
            # Add notes
            for note_data in measure_notes:
                note_elem = ET.SubElement(measure, "note")
                
                pitch_elem = ET.SubElement(note_elem, "pitch")
                step = ET.SubElement(pitch_elem, "step")
                step.text = note_data.pitch_name[0]
                
                # Handle sharps/flats
                if "#" in note_data.pitch_name:
                    alter = ET.SubElement(pitch_elem, "alter")
                    alter.text = "1"
                elif "b" in note_data.pitch_name:
                    alter = ET.SubElement(pitch_elem, "alter")
                    alter.text = "-1"
                
                octave = ET.SubElement(pitch_elem, "octave")
                octave.text = note_data.pitch_name[-1]
                
                # Duration
                duration = ET.SubElement(note_elem, "duration")
                duration.text = str(int(note_data.duration * 4))
                
                note_type = ET.SubElement(note_elem, "type")
                note_type.text = self._duration_to_type(note_data.duration)
                
                # Articulation
                if note_data.articulation:
                    notations = ET.SubElement(note_elem, "notations")
                    articulations = ET.SubElement(notations, "articulations")
                    if note_data.articulation == "accent":
                        ET.SubElement(articulations, "accent")
                    elif note_data.articulation == "ghost":
                        # Ghost note as parentheses
                        ornaments = ET.SubElement(notations, "ornaments")
                        ET.SubElement(ornaments, "parentheses")
        
        # Pretty print
        xml_string = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")
    
    def _group_notes_into_measures(
        self, 
        notes: List[PatternNote],
        beats_per_measure: float = 4.0
    ) -> List[List[PatternNote]]:
        """Group notes into measures based on duration."""
        measures = []
        current_measure = []
        current_beat = 0.0
        
        for note in notes:
            if current_beat + note.duration > beats_per_measure:
                # Start new measure
                measures.append(current_measure)
                current_measure = [note]
                current_beat = note.duration
            else:
                current_measure.append(note)
                current_beat += note.duration
        
        if current_measure:
            measures.append(current_measure)
        
        return measures if measures else [[]]
    
    def _key_to_fifths(self, key: str) -> int:
        """Convert key to circle of fifths position."""
        fifths_map = {
            "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F#": 6, "Gb": -6,
            "Db": -5, "Ab": -4, "Eb": -3, "Bb": -2, "F": -1, "C#": 7
        }
        return fifths_map.get(key, 0)
    
    def _duration_to_type(self, duration: float) -> str:
        """Convert duration in beats to note type."""
        if duration >= 4.0:
            return "whole"
        elif duration >= 2.0:
            return "half"
        elif duration >= 1.0:
            return "quarter"
        elif duration >= 0.5:
            return "eighth"
        elif duration >= 0.25:
            return "16th"
        else:
            return "32nd"
    
    def save_musicxml(
        self,
        phrase: SoloPhrase,
        filepath: str,
        title: str = "Triad Pair Solo"
    ):
        """
        Save phrase to MusicXML file.
        
        Args:
            phrase: SoloPhrase to save
            filepath: Output file path
            title: Score title
        """
        xml_content = self.to_musicxml(phrase, title)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
    
    # =========================================================================
    # PDF/HTML OUTPUT
    # =========================================================================
    
    def to_html_phrase_sheet(
        self,
        phrase: SoloPhrase,
        title: str = "Triad Pair Solo Phrase"
    ) -> str:
        """
        Generate HTML phrase sheet for PDF conversion.
        
        Args:
            phrase: SoloPhrase to format
            title: Sheet title
        
        Returns:
            HTML string
        """
        # Build triad pairs summary
        pairs_html = ""
        for i, tp in enumerate(phrase.triad_pairs):
            pairs_html += f"""
            <div class="triad-pair">
                <span class="pair-label">Pair {i+1}:</span>
                <span class="triad-a">{tp.triad_a[0]} {tp.triad_a[1]}</span>
                <span class="arrow">→</span>
                <span class="triad-b">{tp.triad_b[0]} {tp.triad_b[1]}</span>
                <span class="relationship">({tp.relationship})</span>
            </div>
            """
        
        # Build notation (simplified text representation)
        notation_html = self._generate_text_notation(phrase)
        
        # Build TAB
        tab_html = self._generate_tab_html(phrase)
        
        # Voice-leading analysis
        vl_html = ""
        for i, vl in enumerate(phrase.voice_leading_analysis):
            vl_html += f"""
            <div class="vl-analysis">
                <strong>Transition {i+1}:</strong> {vl.narrative}
                <span class="tension">(tension: {vl.tension_level:.2f})</span>
            </div>
            """
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600&family=JetBrains+Mono&display=swap');
        
        :root {{
            --primary: #1a1a2e;
            --accent: #e94560;
            --secondary: #16213e;
            --text: #eaeaea;
            --muted: #a0a0a0;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Crimson Pro', Georgia, serif;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(26, 26, 46, 0.9);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--accent);
            border-bottom: 2px solid var(--accent);
            padding-bottom: 0.5rem;
        }}
        
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }}
        
        .meta-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .meta-label {{
            font-size: 0.85rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        .meta-value {{
            font-size: 1.1rem;
            font-weight: 600;
        }}
        
        h2 {{
            font-size: 1.5rem;
            margin: 2rem 0 1rem;
            color: var(--accent);
        }}
        
        .triad-pairs {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        
        .triad-pair {{
            background: rgba(233, 69, 96, 0.1);
            border: 1px solid var(--accent);
            border-radius: 6px;
            padding: 0.75rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .pair-label {{
            font-weight: 600;
            color: var(--accent);
        }}
        
        .triad-a, .triad-b {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
        }}
        
        .arrow {{
            color: var(--muted);
        }}
        
        .relationship {{
            font-size: 0.85rem;
            color: var(--muted);
        }}
        
        .notation {{
            font-family: 'JetBrains Mono', monospace;
            background: rgba(0, 0, 0, 0.3);
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre;
            line-height: 1.8;
        }}
        
        .tab {{
            font-family: 'JetBrains Mono', monospace;
            background: rgba(0, 0, 0, 0.3);
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre;
            line-height: 1.4;
        }}
        
        .vl-analysis {{
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .tension {{
            color: var(--muted);
            font-size: 0.9rem;
        }}
        
        .footer {{
            margin-top: 2rem;
            text-align: center;
            color: var(--muted);
            font-size: 0.9rem;
        }}
        
        @media print {{
            body {{
                background: white;
                color: black;
            }}
            .container {{
                box-shadow: none;
                background: white;
            }}
            h1, h2, .pair-label {{
                color: #333;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{html.escape(title)}</h1>
        
        <div class="metadata">
            <div class="meta-item">
                <span class="meta-label">Key/Scale</span>
                <span class="meta-value">{self.config.key} {self.config.scale}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Structure</span>
                <span class="meta-value">{phrase.structure.value}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Bars</span>
                <span class="meta-value">{phrase.bar_count}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Rhythmic Style</span>
                <span class="meta-value">{phrase.rhythmic_style.value}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Mode</span>
                <span class="meta-value">{self.config.mode.value}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Triad Pair Type</span>
                <span class="meta-value">{self.config.triad_pair_type.value}</span>
            </div>
        </div>
        
        <h2>Triad Pairs Used</h2>
        <div class="triad-pairs">
            {pairs_html}
        </div>
        
        <h2>Notation</h2>
        <div class="notation">{notation_html}</div>
        
        <h2>TAB</h2>
        <div class="tab">{tab_html}</div>
        
        <h2>Voice-Leading Analysis</h2>
        <div class="vl-section">
            {vl_html if vl_html else "<p>No voice-leading transitions analyzed.</p>"}
        </div>
        
        <div class="footer">
            Generated by Triad Pair Solo Engine v1.0 | Open Triad Edition
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
    def _generate_text_notation(self, phrase: SoloPhrase) -> str:
        """Generate simplified text notation."""
        measures = self._group_notes_into_measures(phrase.notes)
        lines = []
        
        for i, measure_notes in enumerate(measures):
            notes_str = " ".join([n.pitch_name for n in measure_notes])
            lines.append(f"| {notes_str:<40} |")
        
        return "\n".join(lines)
    
    def _generate_tab_html(self, phrase: SoloPhrase) -> str:
        """Generate guitar TAB representation."""
        # Initialize 6 string lines
        strings = {
            1: [],  # High E
            2: [],  # B
            3: [],  # G
            4: [],  # D
            5: [],  # A
            6: [],  # Low E
        }
        
        for note in phrase.notes:
            string = note.string or 1
            fret = note.fret if note.fret is not None else 0
            
            # Add to the appropriate string, pad others
            max_len = max(len(s) for s in strings.values()) if any(strings.values()) else 0
            
            for s in range(1, 7):
                while len(strings[s]) < max_len:
                    strings[s].append("---")
                
                if s == string:
                    strings[s].append(f"-{fret:2d}")
                else:
                    strings[s].append("---")
        
        # Build TAB output
        string_labels = ["e|", "B|", "G|", "D|", "A|", "E|"]
        tab_lines = []
        
        for i, label in enumerate(string_labels, 1):
            line = label + "".join(strings[i]) + "-|"
            tab_lines.append(line)
        
        return "\n".join(tab_lines)
    
    def save_html(
        self,
        phrase: SoloPhrase,
        filepath: str,
        title: str = "Triad Pair Solo Phrase"
    ):
        """
        Save phrase as HTML file.
        
        Args:
            phrase: SoloPhrase to save
            filepath: Output file path
            title: Sheet title
        """
        html_content = self.to_html_phrase_sheet(phrase, title)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    # =========================================================================
    # BATCH OUTPUT
    # =========================================================================
    
    def export_all(
        self,
        phrase: SoloPhrase,
        output_dir: str,
        base_name: str = "triad_pair_solo"
    ) -> Dict[str, str]:
        """
        Export phrase to all formats.
        
        Args:
            phrase: SoloPhrase to export
            output_dir: Output directory
            base_name: Base filename (without extension)
        
        Returns:
            Dictionary of format -> filepath
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # JSON
        json_path = output_path / f"{base_name}.json"
        self.save_json(phrase, str(json_path))
        files["json"] = str(json_path)
        
        # MusicXML
        xml_path = output_path / f"{base_name}.musicxml"
        self.save_musicxml(phrase, str(xml_path), base_name.replace("_", " ").title())
        files["musicxml"] = str(xml_path)
        
        # HTML
        html_path = output_path / f"{base_name}.html"
        self.save_html(phrase, str(html_path), base_name.replace("_", " ").title())
        files["html"] = str(html_path)
        
        return files

