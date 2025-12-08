"""
Output Module for Quartet Engine
==================================

Handles export formats:
- JSON score structure
- MusicXML (4 staves with correct clefs)
- PDF Score
- MIDI export (optional)
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from xml.etree import ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import json
from datetime import datetime
import html

try:
    from .instruments import InstrumentType, QuartetInstruments
    from .inputs import QuartetConfig
    from .textures import QuartetTexture, QuartetMoment
    from .counterpoint import VoiceLine, VoiceNote
except ImportError:
    from instruments import InstrumentType, QuartetInstruments
    from inputs import QuartetConfig
    from textures import QuartetTexture, QuartetMoment
    from counterpoint import VoiceLine, VoiceNote


@dataclass
class QuartetScore:
    """
    Complete quartet score data.
    
    Attributes:
        title: Score title
        composer: Composer name
        key: Key signature
        time_signature: Time signature
        tempo: Tempo
        bars: Number of bars
        voices: Dict mapping instrument to voice data
        texture: Texture information
        analysis: Harmonic/voice-leading analysis
    """
    title: str
    composer: str
    key: str
    time_signature: tuple
    tempo: int
    bars: int
    voices: Dict[InstrumentType, List[Dict]]
    texture: str
    analysis: str
    metadata: Dict = None
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "composer": self.composer,
            "key": self.key,
            "time_signature": self.time_signature,
            "tempo": self.tempo,
            "bars": self.bars,
            "voices": {k.value: v for k, v in self.voices.items()},
            "texture": self.texture,
            "analysis": self.analysis,
            "metadata": self.metadata or {}
        }


class QuartetOutput:
    """
    Handles quartet score output in multiple formats.
    """
    
    MIDI_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # Clef definitions
    CLEFS = {
        InstrumentType.VIOLIN_I: ("G", 2),
        InstrumentType.VIOLIN_II: ("G", 2),
        InstrumentType.VIOLA: ("C", 3),  # Alto clef
        InstrumentType.CELLO: ("F", 4),  # Bass clef
    }
    
    # Key signature fifths
    KEY_TO_FIFTHS = {
        "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F#": 6,
        "Gb": -6, "Db": -5, "Ab": -4, "Eb": -3, "Bb": -2, "F": -1
    }
    
    def __init__(self, config: QuartetConfig):
        """
        Initialize the output handler.
        
        Args:
            config: Quartet configuration
        """
        self.config = config
    
    def _midi_to_note_name(self, midi: int) -> tuple:
        """Convert MIDI to (step, octave, alter)."""
        octave = (midi // 12) - 1
        pc = midi % 12
        
        # Map to step and alter
        step_map = {
            0: ("C", 0), 1: ("C", 1), 2: ("D", 0), 3: ("D", 1),
            4: ("E", 0), 5: ("F", 0), 6: ("F", 1), 7: ("G", 0),
            8: ("G", 1), 9: ("A", 0), 10: ("A", 1), 11: ("B", 0)
        }
        step, alter = step_map[pc]
        return step, octave, alter
    
    def _duration_to_type(self, duration: float) -> tuple:
        """Convert duration to (type, dots)."""
        if duration >= 4.0:
            return "whole", 0
        elif duration >= 3.0:
            return "half", 1
        elif duration >= 2.0:
            return "half", 0
        elif duration >= 1.5:
            return "quarter", 1
        elif duration >= 1.0:
            return "quarter", 0
        elif duration >= 0.75:
            return "eighth", 1
        elif duration >= 0.5:
            return "eighth", 0
        elif duration >= 0.25:
            return "16th", 0
        else:
            return "32nd", 0
    
    def texture_to_score(
        self,
        texture: QuartetTexture,
        title: str = "Quartet",
        composer: str = "Quartet Engine"
    ) -> QuartetScore:
        """
        Convert a QuartetTexture to QuartetScore.
        
        Args:
            texture: The texture to convert
            title: Score title
            composer: Composer name
        
        Returns:
            QuartetScore
        """
        voices = {inst: [] for inst in InstrumentType}
        
        for moment in texture.moments:
            for inst, (pitch, duration) in moment.voices.items():
                step, octave, alter = self._midi_to_note_name(pitch)
                voices[inst].append({
                    "bar": moment.bar,
                    "beat": moment.beat,
                    "pitch": pitch,
                    "step": step,
                    "octave": octave,
                    "alter": alter,
                    "duration": duration,
                    "articulation": moment.articulation,
                    "dynamic": moment.dynamic
                })
        
        return QuartetScore(
            title=title,
            composer=composer,
            key=self.config.key,
            time_signature=self.config.time_signature,
            tempo=self.config.tempo,
            bars=texture.bars,
            voices=voices,
            texture=texture.texture_type.value,
            analysis=texture.analysis
        )
    
    def to_json(self, score: QuartetScore) -> Dict:
        """
        Convert score to JSON.
        
        Args:
            score: QuartetScore object
        
        Returns:
            JSON-serializable dictionary
        """
        return {
            "quartet_engine_version": "1.0.0",
            "generated": datetime.now().isoformat(),
            "score": score.to_dict()
        }
    
    def save_json(self, score: QuartetScore, filepath: str):
        """Save score as JSON file."""
        data = self.to_json(score)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def to_musicxml(self, score: QuartetScore) -> str:
        """
        Convert score to MusicXML.
        
        Args:
            score: QuartetScore object
        
        Returns:
            MusicXML string
        """
        root = ET.Element("score-partwise", version="4.0")
        
        # Work
        work = ET.SubElement(root, "work")
        work_title = ET.SubElement(work, "work-title")
        work_title.text = score.title
        
        # Identification
        identification = ET.SubElement(root, "identification")
        creator = ET.SubElement(identification, "creator", type="composer")
        creator.text = score.composer
        
        encoding = ET.SubElement(identification, "encoding")
        software = ET.SubElement(encoding, "software")
        software.text = "Quartet Engine v1.0"
        encoding_date = ET.SubElement(encoding, "encoding-date")
        encoding_date.text = datetime.now().strftime("%Y-%m-%d")
        
        # Part list
        part_list = ET.SubElement(root, "part-list")
        
        instruments = [
            (InstrumentType.VIOLIN_I, "P1", "Violin I"),
            (InstrumentType.VIOLIN_II, "P2", "Violin II"),
            (InstrumentType.VIOLA, "P3", "Viola"),
            (InstrumentType.CELLO, "P4", "Cello"),
        ]
        
        for inst, part_id, name in instruments:
            score_part = ET.SubElement(part_list, "score-part", id=part_id)
            part_name = ET.SubElement(score_part, "part-name")
            part_name.text = name
        
        # Parts
        for inst, part_id, name in instruments:
            part = ET.SubElement(root, "part", id=part_id)
            
            # Group notes by measure
            notes_by_bar = {}
            if inst in score.voices:
                for note_data in score.voices[inst]:
                    bar = note_data["bar"]
                    if bar not in notes_by_bar:
                        notes_by_bar[bar] = []
                    notes_by_bar[bar].append(note_data)
            
            for bar_num in range(1, score.bars + 1):
                measure = ET.SubElement(part, "measure", number=str(bar_num))
                
                # Attributes for first measure
                if bar_num == 1:
                    attributes = ET.SubElement(measure, "attributes")
                    
                    divisions = ET.SubElement(attributes, "divisions")
                    divisions.text = "4"
                    
                    key_elem = ET.SubElement(attributes, "key")
                    fifths = ET.SubElement(key_elem, "fifths")
                    fifths.text = str(self.KEY_TO_FIFTHS.get(score.key, 0))
                    
                    time = ET.SubElement(attributes, "time")
                    beats = ET.SubElement(time, "beats")
                    beats.text = str(score.time_signature[0])
                    beat_type = ET.SubElement(time, "beat-type")
                    beat_type.text = str(score.time_signature[1])
                    
                    clef = ET.SubElement(attributes, "clef")
                    sign = ET.SubElement(clef, "sign")
                    line = ET.SubElement(clef, "line")
                    clef_info = self.CLEFS[inst]
                    sign.text = clef_info[0]
                    line.text = str(clef_info[1])
                
                # Add notes
                if bar_num in notes_by_bar:
                    for note_data in notes_by_bar[bar_num]:
                        note_elem = ET.SubElement(measure, "note")
                        
                        pitch = ET.SubElement(note_elem, "pitch")
                        step = ET.SubElement(pitch, "step")
                        step.text = note_data["step"]
                        
                        if note_data["alter"] != 0:
                            alter = ET.SubElement(pitch, "alter")
                            alter.text = str(note_data["alter"])
                        
                        octave = ET.SubElement(pitch, "octave")
                        octave.text = str(note_data["octave"])
                        
                        duration = ET.SubElement(note_elem, "duration")
                        duration.text = str(int(note_data["duration"] * 4))
                        
                        note_type, dots = self._duration_to_type(note_data["duration"])
                        type_elem = ET.SubElement(note_elem, "type")
                        type_elem.text = note_type
                        
                        for _ in range(dots):
                            ET.SubElement(note_elem, "dot")
                else:
                    # Add rest for empty measure
                    note_elem = ET.SubElement(measure, "note")
                    ET.SubElement(note_elem, "rest")
                    duration = ET.SubElement(note_elem, "duration")
                    duration.text = str(score.time_signature[0] * 4)
                    type_elem = ET.SubElement(note_elem, "type")
                    type_elem.text = "whole"
        
        # Pretty print
        xml_string = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")
    
    def save_musicxml(self, score: QuartetScore, filepath: str):
        """Save score as MusicXML file."""
        xml = self.to_musicxml(score)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml)
    
    def to_html(self, score: QuartetScore) -> str:
        """
        Generate HTML score sheet (for PDF).
        
        Args:
            score: QuartetScore object
        
        Returns:
            HTML string (printer-friendly: dark text on light background)
        """
        # Build voice tables
        voices_html = ""
        for inst in InstrumentType:
            if inst in score.voices and score.voices[inst]:
                notes = score.voices[inst]
                notes_str = " ".join([
                    f"({n['bar']}:{n['beat']}) {n['step']}{n['octave']}"
                    for n in notes[:20]  # Limit display
                ])
                voices_html += f"""
                <div class="voice">
                    <h3>{inst.value}</h3>
                    <p class="notes">{html.escape(notes_str)}{'...' if len(notes) > 20 else ''}</p>
                </div>
                """
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(score.title)}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Source+Code+Pro&display=swap');
        
        :root {{
            --bg: #ffffff;
            --surface: #f8f9fa;
            --accent: #1e3a5f;
            --accent2: #3d5a80;
            --text: #333333;
            --muted: #666666;
            --border: #dee2e6;
        }}
        
        body {{
            font-family: 'Merriweather', Georgia, serif;
            background: var(--bg);
            color: var(--text);
            padding: 2rem;
            margin: 0;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: var(--accent);
            font-size: 2rem;
            margin-bottom: 0.5rem;
            border-bottom: 3px solid var(--accent);
            padding-bottom: 0.5rem;
        }}
        
        .composer {{
            color: var(--muted);
            font-style: italic;
            margin-bottom: 2rem;
        }}
        
        .metadata {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
            padding: 1rem;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
        }}
        
        .meta-item {{
            text-align: center;
        }}
        
        .meta-label {{
            font-size: 0.8rem;
            color: var(--muted);
            text-transform: uppercase;
        }}
        
        .meta-value {{
            font-size: 1.2rem;
            color: var(--accent);
            font-weight: bold;
        }}
        
        h2 {{
            color: var(--accent);
            margin-top: 2rem;
            font-size: 1.3rem;
        }}
        
        .voice {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-left: 4px solid var(--accent);
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
        }}
        
        .voice h3 {{
            color: var(--accent);
            margin: 0 0 0.5rem 0;
        }}
        
        .notes {{
            font-family: 'Source Code Pro', monospace;
            font-size: 0.85rem;
            color: var(--muted);
            word-wrap: break-word;
        }}
        
        .analysis {{
            background: var(--surface);
            border-left: 4px solid var(--accent2);
            padding: 1rem;
            margin-top: 2rem;
        }}
        
        footer {{
            text-align: center;
            color: var(--muted);
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
            font-size: 0.9rem;
        }}
        
        @media print {{
            body {{ padding: 0.5rem; }}
            .metadata {{ padding: 0.5rem; }}
            .voice {{ padding: 0.5rem; margin-bottom: 0.5rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{html.escape(score.title)}</h1>
        <p class="composer">by {html.escape(score.composer)}</p>
        
        <div class="metadata">
            <div class="meta-item">
                <div class="meta-label">Key</div>
                <div class="meta-value">{html.escape(score.key)}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Time</div>
                <div class="meta-value">{score.time_signature[0]}/{score.time_signature[1]}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Tempo</div>
                <div class="meta-value">{score.tempo} BPM</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Bars</div>
                <div class="meta-value">{score.bars}</div>
            </div>
        </div>
        
        <h2>Texture: {html.escape(score.texture)}</h2>
        
        <h2>Voices</h2>
        {voices_html}
        
        <div class="analysis">
            <h2>Analysis</h2>
            <p>{html.escape(score.analysis)}</p>
        </div>
        
        <footer>
            Generated by Quartet Engine v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </footer>
    </div>
</body>
</html>"""
        
        return html_content
    
    def save_html(self, score: QuartetScore, filepath: str):
        """Save score as HTML file."""
        html_content = self.to_html(score)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def export_all(
        self,
        score: QuartetScore,
        output_dir: str,
        base_name: str = "quartet"
    ) -> Dict[str, str]:
        """
        Export to all formats.
        
        Args:
            score: QuartetScore object
            output_dir: Output directory
            base_name: Base filename
        
        Returns:
            Dict of format -> filepath
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # JSON
        json_path = output_path / f"{base_name}.json"
        self.save_json(score, str(json_path))
        files["json"] = str(json_path)
        
        # MusicXML
        xml_path = output_path / f"{base_name}.musicxml"
        self.save_musicxml(score, str(xml_path))
        files["musicxml"] = str(xml_path)
        
        # HTML
        html_path = output_path / f"{base_name}.html"
        self.save_html(score, str(html_path))
        files["html"] = str(html_path)
        
        return files

