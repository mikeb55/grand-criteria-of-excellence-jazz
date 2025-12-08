"""
Output Module for Etude Generator
==================================

Handles export to multiple formats:
1. JSON - Complete etude data
2. MusicXML - Notation interchange
3. Guitar TAB - Tablature format
4. PDF/HTML - Print-ready etudes
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import html
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from open_triad_engine import Note
from open_triad_engine.exports import MusicXMLExporter, ExportOptions

from .inputs import EtudeConfig
from .patterns import EtudePhrase, BarContent, NoteEvent


@dataclass
class EtudeOutput:
    """
    Complete output data for an etude.
    
    Attributes:
        config: Original configuration
        phrases: Generated phrases
        metadata: Additional metadata
    """
    config: EtudeConfig
    phrases: List[EtudePhrase]
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'config': self.config.to_dict(),
            'metadata': self.metadata,
            'phrases': [p.to_dict() for p in self.phrases],
            'statistics': self._get_statistics(),
        }
    
    def _get_statistics(self) -> Dict:
        """Calculate statistics about the etude."""
        total_notes = sum(
            len(bar.notes) 
            for phrase in self.phrases 
            for bar in phrase.bars
        )
        total_bars = sum(len(phrase.bars) for phrase in self.phrases)
        
        return {
            'total_notes': total_notes,
            'total_bars': total_bars,
            'total_phrases': len(self.phrases),
        }


class GuitarTabGenerator:
    """
    Generates guitar tablature from etude phrases.
    """
    
    # Standard tuning note names
    STRING_NAMES = ['e', 'B', 'G', 'D', 'A', 'E']  # High to low
    
    def __init__(self, config: EtudeConfig):
        self.config = config
        self.beats_per_bar = config.time_signature[0]
    
    def generate_tab(self, phrases: List[EtudePhrase]) -> str:
        """
        Generate ASCII tablature.
        
        Args:
            phrases: Etude phrases
            
        Returns:
            ASCII TAB string
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append(f"  {self.config.title}")
        lines.append(f"  Key: {self.config.key} {self.config.scale}")
        lines.append(f"  Tempo: {self.config.tempo} BPM")
        lines.append("=" * 70)
        lines.append("")
        
        # Generate TAB for each phrase
        for phrase in phrases:
            lines.append(f"  Phrase {phrase.phrase_number}")
            lines.append("-" * 70)
            
            tab_lines = self._generate_phrase_tab(phrase)
            lines.extend(tab_lines)
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_phrase_tab(self, phrase: EtudePhrase) -> List[str]:
        """Generate TAB lines for a phrase."""
        # Initialize 6 string lines
        string_lines = {i: f"{self.STRING_NAMES[i-1]}|" for i in range(1, 7)}
        
        for bar in phrase.bars:
            # Add bar content
            bar_tabs = self._generate_bar_tab(bar)
            
            for string_num in range(1, 7):
                string_lines[string_num] += bar_tabs.get(string_num, "----")
            
            # Add bar line
            for string_num in range(1, 7):
                string_lines[string_num] += "|"
        
        # Return lines in order (high to low)
        return [string_lines[i] for i in range(1, 7)]
    
    def _generate_bar_tab(self, bar: BarContent) -> Dict[int, str]:
        """Generate TAB content for one bar."""
        # Calculate positions per beat
        chars_per_beat = 4
        total_chars = self.beats_per_bar * chars_per_beat
        
        # Initialize empty bar for each string
        bar_content = {i: ['-'] * total_chars for i in range(1, 7)}
        
        for event in bar.notes:
            if event.string and event.fret is not None:
                # Calculate position in the bar
                pos = int(event.beat * chars_per_beat)
                if 0 <= pos < total_chars:
                    fret_str = str(event.fret)
                    
                    # Place fret number
                    bar_content[event.string][pos] = fret_str[0]
                    if len(fret_str) > 1 and pos + 1 < total_chars:
                        bar_content[event.string][pos + 1] = fret_str[1]
        
        # Convert to strings
        return {k: ''.join(v) for k, v in bar_content.items()}
    
    def export(self, phrases: List[EtudePhrase], filename: str) -> str:
        """Export TAB to file."""
        tab_content = self.generate_tab(phrases)
        
        path = Path(filename)
        path.write_text(tab_content, encoding='utf-8')
        
        return str(path.absolute())


class EtudeMusicXMLExporter:
    """
    Exports etudes to MusicXML format.
    """
    
    # MIDI to MusicXML pitch mapping
    STEP_ALTER = {
        0: ('C', 0), 1: ('C', 1), 2: ('D', 0), 3: ('D', 1),
        4: ('E', 0), 5: ('F', 0), 6: ('F', 1), 7: ('G', 0),
        8: ('G', 1), 9: ('A', 0), 10: ('A', 1), 11: ('B', 0)
    }
    
    def __init__(self, config: EtudeConfig):
        self.config = config
        self.divisions = 4  # Divisions per quarter note
    
    def export(self, phrases: List[EtudePhrase], filename: str) -> str:
        """
        Export etude to MusicXML.
        
        Args:
            phrases: Etude phrases
            filename: Output filename
            
        Returns:
            Path to created file
        """
        score = self._create_score()
        part = ET.SubElement(score, 'part', id="P1")
        
        bar_number = 1
        for phrase in phrases:
            for bar in phrase.bars:
                measure = self._create_measure(bar, bar_number, bar_number == 1)
                part.append(measure)
                bar_number += 1
        
        # Write file
        xml_str = ET.tostring(score, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Add doctype
        lines = pretty_xml.split('\n')
        lines.insert(1, '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">')
        
        output = '\n'.join(lines)
        
        path = Path(filename)
        path.write_text(output, encoding='utf-8')
        
        return str(path.absolute())
    
    def _create_score(self) -> ET.Element:
        """Create the score-partwise root element."""
        score = ET.Element('score-partwise', version="4.0")
        
        # Work info
        work = ET.SubElement(score, 'work')
        work_title = ET.SubElement(work, 'work-title')
        work_title.text = self.config.title
        
        # Identification
        identification = ET.SubElement(score, 'identification')
        creator = ET.SubElement(identification, 'creator', type="composer")
        creator.text = "Etude Generator / Open Triad Engine"
        
        # Part list
        part_list = ET.SubElement(score, 'part-list')
        score_part = ET.SubElement(part_list, 'score-part', id="P1")
        part_name = ET.SubElement(score_part, 'part-name')
        part_name.text = "Guitar"
        
        return score
    
    def _create_measure(self, bar: BarContent, number: int, is_first: bool) -> ET.Element:
        """Create a measure element."""
        measure = ET.Element('measure', number=str(number))
        
        if is_first:
            # Attributes
            attributes = ET.SubElement(measure, 'attributes')
            
            divisions = ET.SubElement(attributes, 'divisions')
            divisions.text = str(self.divisions)
            
            # Time signature
            time = ET.SubElement(attributes, 'time')
            beats = ET.SubElement(time, 'beats')
            beats.text = str(self.config.time_signature[0])
            beat_type = ET.SubElement(time, 'beat-type')
            beat_type.text = str(self.config.time_signature[1])
            
            # Clef (treble with 8vb for guitar)
            clef = ET.SubElement(attributes, 'clef')
            sign = ET.SubElement(clef, 'sign')
            sign.text = 'G'
            line = ET.SubElement(clef, 'line')
            line.text = '2'
            clef_octave = ET.SubElement(clef, 'clef-octave-change')
            clef_octave.text = '-1'
            
            # Direction (tempo)
            direction = ET.SubElement(measure, 'direction', placement="above")
            direction_type = ET.SubElement(direction, 'direction-type')
            metronome = ET.SubElement(direction_type, 'metronome')
            beat_unit = ET.SubElement(metronome, 'beat-unit')
            beat_unit.text = 'quarter'
            per_minute = ET.SubElement(metronome, 'per-minute')
            per_minute.text = str(self.config.tempo)
        
        # Add notes
        for event in bar.notes:
            note_elem = self._create_note(event)
            measure.append(note_elem)
        
        return measure
    
    def _create_note(self, event: NoteEvent) -> ET.Element:
        """Create a note element."""
        note_elem = ET.Element('note')
        
        # Pitch
        pitch = ET.SubElement(note_elem, 'pitch')
        step, alter = self.STEP_ALTER[event.note.pitch_class]
        
        step_elem = ET.SubElement(pitch, 'step')
        step_elem.text = step
        
        if alter != 0:
            alter_elem = ET.SubElement(pitch, 'alter')
            alter_elem.text = str(alter)
        
        octave_elem = ET.SubElement(pitch, 'octave')
        octave_elem.text = str(event.note.octave)
        
        # Duration
        duration_elem = ET.SubElement(note_elem, 'duration')
        duration_elem.text = str(int(event.duration * self.divisions))
        
        # Type
        type_elem = ET.SubElement(note_elem, 'type')
        type_elem.text = self._get_note_type(event.duration)
        
        # Technical (TAB info)
        if event.string and event.fret is not None:
            notations = ET.SubElement(note_elem, 'notations')
            technical = ET.SubElement(notations, 'technical')
            
            string_elem = ET.SubElement(technical, 'string')
            string_elem.text = str(event.string)
            
            fret_elem = ET.SubElement(technical, 'fret')
            fret_elem.text = str(event.fret)
        
        return note_elem
    
    def _get_note_type(self, duration: float) -> str:
        """Get MusicXML note type from duration."""
        if duration >= 4.0:
            return 'whole'
        elif duration >= 2.0:
            return 'half'
        elif duration >= 1.0:
            return 'quarter'
        elif duration >= 0.5:
            return 'eighth'
        elif duration >= 0.25:
            return '16th'
        else:
            return '32nd'


class EtudePDFBuilder:
    """
    Builds print-ready HTML (for PDF conversion) from etude data.
    """
    
    def __init__(self, config: EtudeConfig):
        self.config = config
    
    def build_html(self, phrases: List[EtudePhrase], description: str = "") -> str:
        """
        Build HTML content for the etude.
        
        Args:
            phrases: Etude phrases
            description: Etude description text
            
        Returns:
            HTML string
        """
        # Generate TAB for inclusion
        tab_gen = GuitarTabGenerator(self.config)
        tab_content = tab_gen.generate_tab(phrases)
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(self.config.title)}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=JetBrains+Mono&display=swap');
        
        body {{
            font-family: 'Merriweather', serif;
            max-width: 850px;
            margin: 0 auto;
            padding: 40px;
            background: white;
            color: #333;
        }}
        
        h1 {{
            font-size: 2.2em;
            color: #1a1a2e;
            border-bottom: 3px solid #ee6c4d;
            padding-bottom: 15px;
            margin-bottom: 10px;
        }}
        
        .meta {{
            color: #666;
            font-size: 1.1em;
            margin-bottom: 30px;
        }}
        
        .meta span {{
            margin-right: 25px;
        }}
        
        .description {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            white-space: pre-wrap;
            line-height: 1.6;
        }}
        
        h2 {{
            color: #3d5a80;
            font-size: 1.5em;
            margin-top: 40px;
            border-left: 4px solid #ee6c4d;
            padding-left: 15px;
        }}
        
        .tab-container {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 25px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        .tab-content {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9em;
            line-height: 1.4;
            white-space: pre;
        }}
        
        .analysis {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px 20px;
            margin: 20px 0;
        }}
        
        .practice-tips {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px 20px;
            margin: 20px 0;
        }}
        
        .practice-tips ul {{
            margin: 10px 0 0 0;
            padding-left: 20px;
        }}
        
        .phrase-info {{
            color: #666;
            font-size: 0.9em;
            margin-top: 30px;
        }}
        
        @media print {{
            body {{
                padding: 20px;
            }}
            .tab-container {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <h1>{html.escape(self.config.title)}</h1>
    
    <div class="meta">
        <span><strong>Key:</strong> {html.escape(self.config.key)} {html.escape(self.config.scale)}</span>
        <span><strong>Tempo:</strong> {self.config.tempo} BPM</span>
        <span><strong>Difficulty:</strong> {html.escape(self.config.difficulty.capitalize())}</span>
    </div>
    
    <div class="description">{html.escape(description)}</div>
    
    <h2>Tablature</h2>
    <div class="tab-container">
        <div class="tab-content">{html.escape(tab_content)}</div>
    </div>
    
    <div class="practice-tips">
        <strong>Practice Tips:</strong>
        <ul>
            <li>Start slowly and focus on accuracy</li>
            <li>Use a metronome at {max(60, self.config.tempo - 40)} BPM to begin</li>
            <li>Listen for the chord tones connecting between positions</li>
            <li>Gradually increase tempo as comfort develops</li>
        </ul>
    </div>
    
    <div class="phrase-info">
        <p><strong>Structure:</strong> {len(phrases)} phrase(s), {sum(len(p.bars) for p in phrases)} bars total</p>
        <p><strong>Generated by:</strong> Etude Generator / Open Triad Engine v1.0</p>
    </div>
</body>
</html>'''
        
        return html_content
    
    def export(self, phrases: List[EtudePhrase], filename: str, description: str = "") -> str:
        """Export etude to HTML file."""
        html_content = self.build_html(phrases, description)
        
        path = Path(filename)
        path.write_text(html_content, encoding='utf-8')
        
        return str(path.absolute())


class EtudeExporter:
    """
    Main exporter class handling all output formats.
    """
    
    def __init__(self, config: EtudeConfig):
        self.config = config
        self.tab_generator = GuitarTabGenerator(config)
        self.musicxml_exporter = EtudeMusicXMLExporter(config)
        self.pdf_builder = EtudePDFBuilder(config)
    
    def export_json(self, output: EtudeOutput, filename: str) -> str:
        """Export to JSON."""
        data = output.to_dict()
        
        path = Path(filename)
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        
        return str(path.absolute())
    
    def export_tab(self, phrases: List[EtudePhrase], filename: str) -> str:
        """Export to TAB."""
        return self.tab_generator.export(phrases, filename)
    
    def export_musicxml(self, phrases: List[EtudePhrase], filename: str) -> str:
        """Export to MusicXML."""
        return self.musicxml_exporter.export(phrases, filename)
    
    def export_pdf(self, phrases: List[EtudePhrase], filename: str, description: str = "") -> str:
        """Export to HTML (for PDF conversion)."""
        return self.pdf_builder.export(phrases, filename, description)
    
    def export_all(
        self, 
        output: EtudeOutput, 
        base_filename: str,
        description: str = ""
    ) -> Dict[str, str]:
        """
        Export to all formats.
        
        Args:
            output: Complete etude output
            base_filename: Base filename (without extension)
            description: Etude description
            
        Returns:
            Dictionary of format -> filepath
        """
        results = {}
        
        # JSON
        results['json'] = self.export_json(output, f"{base_filename}.json")
        
        # TAB
        results['tab'] = self.export_tab(output.phrases, f"{base_filename}.tab.txt")
        
        # MusicXML
        results['musicxml'] = self.export_musicxml(output.phrases, f"{base_filename}.musicxml")
        
        # HTML/PDF
        results['html'] = self.export_pdf(output.phrases, f"{base_filename}.html", description)
        
        return results

