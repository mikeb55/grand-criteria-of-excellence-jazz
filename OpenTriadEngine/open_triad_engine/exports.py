"""
Export Modules for Open Triad Engine
=====================================

Implements:
1. MusicXML Export - standard notation interchange format
2. PDF Etude Builder - print-ready practice materials
3. TAB Export - guitar tablature
4. Notation Export - generic notation export utilities
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import html

from .core import Note, Triad, CHROMATIC_NOTES
from .output_shapes import MelodicPattern, RhythmicNote, ShapeBundle


@dataclass
class ExportOptions:
    """
    Options for export operations.
    
    Attributes:
        title: Title of the piece
        composer: Composer name
        tempo: BPM for playback
        time_signature: Time signature as tuple (beats, beat_type)
        key: Key signature
        clef: Clef to use (treble, bass, alto)
        include_fingerings: Include fingering suggestions
        include_analysis: Include harmonic analysis
    """
    title: str = "Open Triad Study"
    composer: str = "Open Triad Engine"
    tempo: int = 120
    time_signature: Tuple[int, int] = (4, 4)
    key: str = "C"
    clef: str = "treble"
    include_fingerings: bool = False
    include_analysis: bool = True


class MusicXMLExporter:
    """
    Exports triads and patterns to MusicXML format.
    
    MusicXML is the standard interchange format for notation software.
    """
    
    # MIDI to MusicXML pitch mapping
    STEP_ALTER = {
        0: ('C', 0), 1: ('C', 1), 2: ('D', 0), 3: ('D', 1),
        4: ('E', 0), 5: ('F', 0), 6: ('F', 1), 7: ('G', 0),
        8: ('G', 1), 9: ('A', 0), 10: ('A', 1), 11: ('B', 0)
    }
    
    def __init__(self, options: Optional[ExportOptions] = None):
        self.options = options or ExportOptions()
    
    def create_score(self) -> ET.Element:
        """Create the root score-partwise element."""
        score = ET.Element('score-partwise', version="4.0")
        
        # Work info
        work = ET.SubElement(score, 'work')
        work_title = ET.SubElement(work, 'work-title')
        work_title.text = self.options.title
        
        # Identification
        identification = ET.SubElement(score, 'identification')
        creator = ET.SubElement(identification, 'creator', type="composer")
        creator.text = self.options.composer
        
        # Part list
        part_list = ET.SubElement(score, 'part-list')
        score_part = ET.SubElement(part_list, 'score-part', id="P1")
        part_name = ET.SubElement(score_part, 'part-name')
        part_name.text = "Open Triads"
        
        return score
    
    def create_measure(
        self,
        number: int,
        notes: List[Note],
        is_first: bool = False,
        is_chord: bool = False
    ) -> ET.Element:
        """Create a measure element with notes."""
        measure = ET.Element('measure', number=str(number))
        
        if is_first:
            # Add attributes (clef, time signature, etc.)
            attributes = ET.SubElement(measure, 'attributes')
            
            divisions = ET.SubElement(attributes, 'divisions')
            divisions.text = "4"  # Quarter note = 4 divisions
            
            # Time signature
            time = ET.SubElement(attributes, 'time')
            beats = ET.SubElement(time, 'beats')
            beats.text = str(self.options.time_signature[0])
            beat_type = ET.SubElement(time, 'beat-type')
            beat_type.text = str(self.options.time_signature[1])
            
            # Clef
            clef = ET.SubElement(attributes, 'clef')
            sign = ET.SubElement(clef, 'sign')
            line = ET.SubElement(clef, 'line')
            
            if self.options.clef == 'treble':
                sign.text = 'G'
                line.text = '2'
            elif self.options.clef == 'bass':
                sign.text = 'F'
                line.text = '4'
            else:
                sign.text = 'C'
                line.text = '3'
        
        # Add notes
        for i, note in enumerate(notes):
            note_elem = self._create_note_element(
                note,
                duration=4,
                is_chord=(is_chord and i > 0)
            )
            measure.append(note_elem)
        
        return measure
    
    def _create_note_element(
        self,
        note: Note,
        duration: int = 4,
        note_type: str = "quarter",
        is_chord: bool = False
    ) -> ET.Element:
        """Create a note element."""
        note_elem = ET.Element('note')
        
        if is_chord:
            ET.SubElement(note_elem, 'chord')
        
        # Pitch
        pitch = ET.SubElement(note_elem, 'pitch')
        
        step, alter = self.STEP_ALTER[note.pitch_class]
        step_elem = ET.SubElement(pitch, 'step')
        step_elem.text = step
        
        if alter != 0:
            alter_elem = ET.SubElement(pitch, 'alter')
            alter_elem.text = str(alter)
        
        octave_elem = ET.SubElement(pitch, 'octave')
        octave_elem.text = str(note.octave)
        
        # Duration
        duration_elem = ET.SubElement(note_elem, 'duration')
        duration_elem.text = str(duration)
        
        # Type
        type_elem = ET.SubElement(note_elem, 'type')
        type_elem.text = note_type
        
        return note_elem
    
    def export_triads(
        self,
        triads: List[Triad],
        filename: str
    ) -> str:
        """
        Export a list of triads to MusicXML.
        
        Args:
            triads: List of triads to export
            filename: Output filename
            
        Returns:
            Path to the created file
        """
        score = self.create_score()
        part = ET.SubElement(score, 'part', id="P1")
        
        for i, triad in enumerate(triads):
            # Sort voices for proper notation order
            sorted_voices = sorted(triad.voices, key=lambda n: n.midi_number)
            measure = self.create_measure(
                number=i + 1,
                notes=sorted_voices,
                is_first=(i == 0),
                is_chord=True
            )
            part.append(measure)
        
        # Write file
        tree = ET.ElementTree(score)
        xml_str = ET.tostring(score, encoding='unicode')
        
        # Pretty print
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Add doctype
        lines = pretty_xml.split('\n')
        lines.insert(1, '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">')
        
        output = '\n'.join(lines)
        
        path = Path(filename)
        path.write_text(output, encoding='utf-8')
        
        return str(path.absolute())
    
    def export_pattern(
        self,
        pattern: MelodicPattern,
        filename: str
    ) -> str:
        """Export a melodic pattern to MusicXML."""
        score = self.create_score()
        part = ET.SubElement(score, 'part', id="P1")
        
        # Create measures, 4 notes per measure
        notes_per_measure = self.options.time_signature[0]
        measure_num = 1
        current_notes = []
        
        for note in pattern.notes:
            current_notes.append(note)
            
            if len(current_notes) >= notes_per_measure:
                measure = self.create_measure(
                    number=measure_num,
                    notes=current_notes,
                    is_first=(measure_num == 1),
                    is_chord=False
                )
                part.append(measure)
                measure_num += 1
                current_notes = []
        
        # Handle remaining notes
        if current_notes:
            measure = self.create_measure(
                number=measure_num,
                notes=current_notes,
                is_first=(measure_num == 1),
                is_chord=False
            )
            part.append(measure)
        
        # Write file
        xml_str = ET.tostring(score, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        lines = pretty_xml.split('\n')
        lines.insert(1, '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">')
        
        output = '\n'.join(lines)
        
        path = Path(filename)
        path.write_text(output, encoding='utf-8')
        
        return str(path.absolute())


class TABExporter:
    """
    Exports triads and patterns to guitar tablature format.
    """
    
    # Standard guitar tuning (low to high string)
    STANDARD_TUNING = [40, 45, 50, 55, 59, 64]  # E A D G B E
    
    def __init__(
        self,
        tuning: Optional[List[int]] = None,
        fret_range: Tuple[int, int] = (0, 12)
    ):
        self.tuning = tuning or self.STANDARD_TUNING
        self.fret_range = fret_range
    
    def note_to_fret(self, note: Note) -> Optional[Tuple[int, int]]:
        """
        Convert a note to (string, fret) position.
        
        Returns:
            Tuple of (string_number, fret) or None if unplayable
        """
        midi = note.midi_number
        
        # Try each string
        for string_num, open_pitch in enumerate(self.tuning):
            fret = midi - open_pitch
            if self.fret_range[0] <= fret <= self.fret_range[1]:
                return (string_num, fret)
        
        return None
    
    def triad_to_tab(self, triad: Triad) -> List[Optional[int]]:
        """
        Convert a triad to TAB format.
        
        Returns:
            List of fret numbers for each string (None = not played)
        """
        tab = [None] * len(self.tuning)
        
        sorted_voices = sorted(triad.voices, key=lambda n: n.midi_number)
        
        for note in sorted_voices:
            pos = self.note_to_fret(note)
            if pos:
                string_num, fret = pos
                tab[string_num] = fret
        
        return tab
    
    def format_tab_line(self, tabs: List[List[Optional[int]]]) -> str:
        """Format TAB data as ASCII tab."""
        lines = []
        string_names = ['e', 'B', 'G', 'D', 'A', 'E']
        
        for string_idx in range(len(self.tuning) - 1, -1, -1):
            line = f"{string_names[string_idx]}|"
            
            for tab in tabs:
                if tab[string_idx] is not None:
                    fret = str(tab[string_idx])
                    line += f"-{fret:>2}-|"
                else:
                    line += "----"
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    def export_triads(
        self,
        triads: List[Triad],
        filename: str
    ) -> str:
        """Export triads as TAB to a text file."""
        tabs = [self.triad_to_tab(t) for t in triads]
        
        content = []
        content.append(f"{'=' * 50}")
        content.append("OPEN TRIAD TABLATURE")
        content.append(f"{'=' * 50}")
        content.append("")
        
        # Add chord names
        chord_line = "    " + "  ".join(f"{t.symbol:^5}" for t in triads)
        content.append(chord_line)
        content.append("")
        
        # Add TAB
        content.append(self.format_tab_line(tabs))
        
        path = Path(filename)
        path.write_text('\n'.join(content), encoding='utf-8')
        
        return str(path.absolute())


class PDFEtudeBuilder:
    """
    Builds print-ready PDF etudes from triads and patterns.
    
    Creates HTML first, then can be converted to PDF using external tools.
    """
    
    def __init__(self, options: Optional[ExportOptions] = None):
        self.options = options or ExportOptions()
    
    def build_etude_html(
        self,
        title: str,
        scale_key: str,
        shapes: List[ShapeBundle],
        patterns: Optional[List[MelodicPattern]] = None,
        fingerings: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Build an HTML etude document.
        
        Args:
            title: Etude title
            scale_key: Scale/key for the etude
            shapes: Open triad shape bundles
            patterns: Optional melodic patterns
            fingerings: Optional fingering suggestions
            
        Returns:
            HTML string
        """
        html_parts = []
        
        # HTML header
        html_parts.append('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@400;600&display=swap');
        
        body {{
            font-family: 'Source Sans Pro', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            background: #fafafa;
            color: #333;
        }}
        
        h1 {{
            font-family: 'Playfair Display', serif;
            font-size: 2.5em;
            color: #1a1a2e;
            border-bottom: 3px solid #16213e;
            padding-bottom: 10px;
        }}
        
        h2 {{
            font-family: 'Playfair Display', serif;
            color: #16213e;
            margin-top: 30px;
        }}
        
        .meta {{
            color: #666;
            font-style: italic;
            margin-bottom: 30px;
        }}
        
        .chord-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .chord-box {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .chord-name {{
            font-weight: 700;
            font-size: 1.3em;
            color: #0f3460;
            margin-bottom: 10px;
        }}
        
        .voicing {{
            font-family: monospace;
            background: #f5f5f5;
            padding: 8px;
            border-radius: 4px;
            margin: 5px 0;
        }}
        
        .contour {{
            font-size: 0.85em;
            color: #666;
        }}
        
        .pattern {{
            background: white;
            border-left: 4px solid #e94560;
            padding: 15px;
            margin: 15px 0;
        }}
        
        .fingering {{
            color: #e94560;
            font-weight: 600;
        }}
        
        .notes {{
            font-family: monospace;
            letter-spacing: 2px;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 20px;
            }}
            .chord-box {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
'''.format(title=html.escape(title)))
        
        # Title and meta
        html_parts.append(f'<h1>{html.escape(title)}</h1>')
        html_parts.append(f'<p class="meta">Key: {html.escape(scale_key)} | Generated by Open Triad Engine</p>')
        
        # Shapes section
        html_parts.append('<h2>Open Triad Shapes</h2>')
        html_parts.append('<div class="chord-grid">')
        
        for bundle in shapes:
            html_parts.append('<div class="chord-box">')
            html_parts.append(f'<div class="chord-name">{html.escape(bundle.root_triad.symbol)}</div>')
            
            for name, shape in bundle.get_all_shapes().items():
                voices = ', '.join(str(v) for v in sorted(shape.voices, key=lambda n: n.midi_number))
                html_parts.append(f'<div class="voicing"><strong>{name}:</strong> {voices}</div>')
            
            html_parts.append(f'<div class="contour">Contour: {bundle.root_contour.type.value}</div>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        # Patterns section
        if patterns:
            html_parts.append('<h2>Practice Patterns</h2>')
            
            for i, pattern in enumerate(patterns):
                notes_str = ' - '.join(str(n) for n in pattern.notes)
                html_parts.append(f'''
                <div class="pattern">
                    <strong>Pattern {i + 1}</strong> ({pattern.pattern_type})<br>
                    <span class="notes">{notes_str}</span><br>
                    <span class="contour">Contour: {pattern.contour.type.value}, Range: {pattern.contour.range} semitones</span>
                </div>
                ''')
        
        # Fingerings section
        if fingerings:
            html_parts.append('<h2>Suggested Fingerings</h2>')
            for shape, fing in fingerings.items():
                html_parts.append(f'<p><strong>{shape}:</strong> <span class="fingering">{fing}</span></p>')
        
        # Footer
        html_parts.append('''
</body>
</html>
''')
        
        return ''.join(html_parts)
    
    def export_etude(
        self,
        title: str,
        scale_key: str,
        shapes: List[ShapeBundle],
        filename: str,
        patterns: Optional[List[MelodicPattern]] = None,
        fingerings: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Export a complete etude to HTML file.
        
        Args:
            title: Etude title
            scale_key: Scale/key
            shapes: Shape bundles to include
            filename: Output filename
            patterns: Optional patterns
            fingerings: Optional fingerings
            
        Returns:
            Path to created file
        """
        html_content = self.build_etude_html(
            title=title,
            scale_key=scale_key,
            shapes=shapes,
            patterns=patterns,
            fingerings=fingerings
        )
        
        path = Path(filename)
        path.write_text(html_content, encoding='utf-8')
        
        return str(path.absolute())


class NotationExporter:
    """
    Generic notation export utilities.
    """
    
    @staticmethod
    def to_json(
        triads: List[Triad],
        filename: str,
        include_analysis: bool = True
    ) -> str:
        """Export triads to JSON format."""
        data = {
            'version': '1.0',
            'engine': 'Open Triad Engine',
            'triads': [t.to_dict() for t in triads]
        }
        
        if include_analysis:
            data['analysis'] = {
                'total_triads': len(triads),
                'unique_roots': list(set(t.root.name for t in triads)),
                'voicing_types': list(set(t.voicing_type.value for t in triads))
            }
        
        path = Path(filename)
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        
        return str(path.absolute())
    
    @staticmethod
    def to_lilypond(triads: List[Triad]) -> str:
        """Generate LilyPond notation code for triads."""
        # LilyPond note conversion
        ly_notes = {
            'C': 'c', 'C#': 'cis', 'D': 'd', 'D#': 'dis',
            'E': 'e', 'F': 'f', 'F#': 'fis', 'G': 'g',
            'G#': 'gis', 'A': 'a', 'A#': 'ais', 'B': 'b'
        }
        
        def note_to_ly(note: Note) -> str:
            ly_pitch = ly_notes.get(note.name, 'c')
            octave = note.octave - 4  # LilyPond middle C is c'
            
            if octave > 0:
                ly_pitch += "'" * octave
            elif octave < 0:
                ly_pitch += "," * abs(octave)
            
            return ly_pitch
        
        lines = []
        lines.append("\\version \"2.24.0\"")
        lines.append("\\header { title = \"Open Triad Study\" }")
        lines.append("{")
        
        for triad in triads:
            sorted_voices = sorted(triad.voices, key=lambda n: n.midi_number)
            chord_notes = ' '.join(note_to_ly(n) for n in sorted_voices)
            lines.append(f"  <{chord_notes}>1")
        
        lines.append("}")
        
        return '\n'.join(lines)


# Convenience functions
def export_to_musicxml(
    triads: List[Triad],
    filename: str,
    title: str = "Open Triad Study"
) -> str:
    """Quick export to MusicXML."""
    exporter = MusicXMLExporter(ExportOptions(title=title))
    return exporter.export_triads(triads, filename)


def export_to_tab(triads: List[Triad], filename: str) -> str:
    """Quick export to TAB."""
    exporter = TABExporter()
    return exporter.export_triads(triads, filename)


def export_to_json(triads: List[Triad], filename: str) -> str:
    """Quick export to JSON."""
    return NotationExporter.to_json(triads, filename)

