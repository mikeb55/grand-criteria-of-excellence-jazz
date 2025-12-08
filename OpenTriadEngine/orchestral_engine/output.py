"""
Output Module for Orchestral Engine
====================================

Handles export formats: JSON, MusicXML, HTML/PDF.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from xml.etree import ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import json
from datetime import datetime
import html

from .inputs import OrchestraConfig
from .instruments import InstrumentType, ORCHESTRA_INSTRUMENTS, OrchestraInstruments
from .textures import OrchestraTexture, OrchestraMoment


@dataclass
class OrchestraScore:
    """Complete orchestral score data."""
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


class OrchestraOutput:
    """Handles orchestral score output in multiple formats."""
    
    MIDI_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # Key signature fifths
    KEY_TO_FIFTHS = {
        "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F#": 6,
        "Gb": -6, "Db": -5, "Ab": -4, "Eb": -3, "Bb": -2, "F": -1
    }
    
    # Instrument order in score
    SCORE_ORDER = [
        InstrumentType.FLUTE,
        InstrumentType.CLARINET,
        InstrumentType.FLUGELHORN,
        InstrumentType.VIOLIN_I,
        InstrumentType.VIOLIN_II,
        InstrumentType.VIOLA,
        InstrumentType.CELLO,
        InstrumentType.BASS,
        InstrumentType.PIANO,
        InstrumentType.PERCUSSION,
    ]
    
    def __init__(self, config: OrchestraConfig):
        """Initialize the output handler."""
        self.config = config
    
    def _midi_to_note_name(self, midi: int) -> tuple:
        """Convert MIDI to (step, octave, alter)."""
        octave = (midi // 12) - 1
        pc = midi % 12
        
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
        texture: OrchestraTexture,
        title: str = "Orchestra",
        composer: str = "Orchestral Engine"
    ) -> OrchestraScore:
        """Convert an OrchestraTexture to OrchestraScore."""
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
        
        return OrchestraScore(
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
    
    def to_json(self, score: OrchestraScore) -> Dict:
        """Convert score to JSON."""
        return {
            "orchestral_engine_version": "1.0.0",
            "generated": datetime.now().isoformat(),
            "score": score.to_dict()
        }
    
    def save_json(self, score: OrchestraScore, filepath: str):
        """Save score as JSON file."""
        data = self.to_json(score)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def to_musicxml(self, score: OrchestraScore) -> str:
        """Convert score to MusicXML."""
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
        software.text = "Orchestral Engine v1.0"
        encoding_date = ET.SubElement(encoding, "encoding-date")
        encoding_date.text = datetime.now().strftime("%Y-%m-%d")
        
        # Part list
        part_list = ET.SubElement(root, "part-list")
        
        active_instruments = []
        for inst in self.SCORE_ORDER:
            if inst in score.voices and score.voices[inst]:
                active_instruments.append(inst)
                inst_def = ORCHESTRA_INSTRUMENTS[inst]
                part_id = f"P{len(active_instruments)}"
                
                score_part = ET.SubElement(part_list, "score-part", id=part_id)
                part_name = ET.SubElement(score_part, "part-name")
                part_name.text = inst_def.name
        
        # Parts
        for idx, inst in enumerate(active_instruments):
            part_id = f"P{idx + 1}"
            part = ET.SubElement(root, "part", id=part_id)
            inst_def = ORCHESTRA_INSTRUMENTS[inst]
            
            # Group notes by measure
            notes_by_bar = {}
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
                    
                    # Clef
                    clef = ET.SubElement(attributes, "clef")
                    sign = ET.SubElement(clef, "sign")
                    line = ET.SubElement(clef, "line")
                    clef_sign, clef_line = OrchestraInstruments.get_clef(inst)
                    sign.text = clef_sign
                    line.text = str(clef_line)
                    
                    # Transposition for Bb instruments
                    if inst_def.transposition != 0:
                        transpose = ET.SubElement(attributes, "transpose")
                        diatonic = ET.SubElement(transpose, "diatonic")
                        diatonic.text = str(-1 if inst_def.transposition == -2 else 0)
                        chromatic = ET.SubElement(transpose, "chromatic")
                        chromatic.text = str(inst_def.transposition)
                
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
    
    def save_musicxml(self, score: OrchestraScore, filepath: str):
        """Save score as MusicXML file."""
        xml = self.to_musicxml(score)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml)
    
    def to_html(self, score: OrchestraScore) -> str:
        """Generate HTML score sheet (for PDF)."""
        voices_html = ""
        for inst in self.SCORE_ORDER:
            if inst in score.voices and score.voices[inst]:
                notes = score.voices[inst]
                notes_str = " ".join([
                    f"({n['bar']}:{n['beat']}) {n['step']}{n['octave']}"
                    for n in notes[:15]
                ])
                voices_html += f"""
                <div class="voice">
                    <h3>{ORCHESTRA_INSTRUMENTS[inst].name}</h3>
                    <p class="notes">{html.escape(notes_str)}{'...' if len(notes) > 15 else ''}</p>
                </div>
                """
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(score.title)}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;700&family=JetBrains+Mono&display=swap');
        
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --accent: #f59e0b;
            --accent2: #10b981;
            --text: #f1f5f9;
            --muted: #94a3b8;
        }}
        
        body {{
            font-family: 'Crimson Pro', Georgia, serif;
            background: linear-gradient(135deg, var(--bg) 0%, #1a1a2e 100%);
            color: var(--text);
            padding: 2rem;
            margin: 0;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: var(--surface);
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
        
        h1 {{
            color: var(--accent);
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 3px solid var(--accent);
            padding-bottom: 0.5rem;
        }}
        
        .composer {{
            color: var(--muted);
            font-style: italic;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }}
        
        .metadata {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
        }}
        
        .meta-item {{
            text-align: center;
        }}
        
        .meta-label {{
            font-size: 0.75rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        .meta-value {{
            font-size: 1.3rem;
            color: var(--accent);
            font-weight: bold;
        }}
        
        h2 {{
            color: var(--accent2);
            margin-top: 2rem;
            font-size: 1.5rem;
        }}
        
        .voice {{
            background: rgba(0,0,0,0.2);
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 0.75rem;
            border-left: 4px solid var(--accent);
        }}
        
        .voice h3 {{
            color: var(--accent);
            margin: 0 0 0.5rem 0;
            font-size: 1.1rem;
        }}
        
        .notes {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: var(--muted);
            word-wrap: break-word;
            margin: 0;
        }}
        
        .analysis {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(16, 185, 129, 0.1));
            border-left: 4px solid var(--accent2);
            padding: 1.5rem;
            margin-top: 2rem;
            border-radius: 8px;
        }}
        
        footer {{
            text-align: center;
            color: var(--muted);
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎼 {html.escape(score.title)}</h1>
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
                <div class="meta-value">{score.tempo}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Bars</div>
                <div class="meta-value">{score.bars}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Texture</div>
                <div class="meta-value">{html.escape(score.texture)}</div>
            </div>
        </div>
        
        <h2>Instrumentation</h2>
        {voices_html}
        
        <div class="analysis">
            <h2>Analysis</h2>
            <p>{html.escape(score.analysis)}</p>
        </div>
        
        <footer>
            Generated by Orchestral Engine v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </footer>
    </div>
</body>
</html>"""
        
        return html_content
    
    def save_html(self, score: OrchestraScore, filepath: str):
        """Save score as HTML file."""
        html_content = self.to_html(score)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def export_all(
        self,
        score: OrchestraScore,
        output_dir: str,
        base_name: str = "orchestra"
    ) -> Dict[str, str]:
        """Export to all formats."""
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

