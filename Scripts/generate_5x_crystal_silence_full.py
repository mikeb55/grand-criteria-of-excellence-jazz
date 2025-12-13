"""
5x-Crystal Silence — Full Pipeline Generation
==============================================

ECM Ballad Style (Ralph Towner / Egberto Gismonti / Metheny solo)

Generates:
- 4 Lead Sheets (A-D) as MusicXML + Notes.md
- 5 Exercise directories with studies
- README.md
- HTML Play-Along

Key: A Major | Tempo: 80 BPM | Time: 4/4 | 16 bars
Technique: Campanella, sustain, open strings, drone
Dynamics: Never louder than mp
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ============================================================================
# CONSTANTS
# ============================================================================

NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "E#": 5, "Fb": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7,
    "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11, "Cb": 11
}

MIDI_TO_NOTE_SHARP = {
    0: ("C", 0), 1: ("C", 1), 2: ("D", 0), 3: ("D", 1),
    4: ("E", 0), 5: ("F", 0), 6: ("F", 1), 7: ("G", 0),
    8: ("G", 1), 9: ("A", 0), 10: ("A", 1), 11: ("B", 0)
}

# 4/4 time: 64 divisions per bar (16 per quarter * 4 quarters)
DIVISIONS = 16
BAR = 64

WHOLE = 64
DOTTED_HALF = 48
HALF = 32
DOTTED_QUARTER = 24
QUARTER = 16
DOTTED_EIGHTH = 12
EIGHTH = 8
SIXTEENTH = 4


@dataclass
class Note:
    pitch: int
    duration: int
    is_rest: bool = False
    
    def get_xml_pitch(self) -> Tuple[str, int, int]:
        if self.is_rest:
            return ("C", 4, 0)
        octave = (self.pitch // 12) - 1
        pc = self.pitch % 12
        step, alter = MIDI_TO_NOTE_SHARP[pc]
        return (step, octave, alter)


def p(note: str, octave: int) -> int:
    """Octave lowered for guitar range."""
    return NOTE_TO_MIDI[note] + octave * 12  # Removed +1 to lower by octave

def n(note: str, octave: int, duration: int) -> Note:
    return Note(p(note, octave), duration)

def r(duration: int) -> Note:
    return Note(0, duration, is_rest=True)

def verify_bar(items: List[Note], bar_num: int, section: str) -> bool:
    total = sum(item.duration for item in items)
    ok = "[OK]" if total == BAR else "[FAIL]"
    print(f"  {ok} {section} Bar {bar_num}: {total}/64")
    return total == BAR


# ============================================================================
# VERSION A: LYRICAL SUSTAIN
# ============================================================================

def generate_version_a() -> List[List[Note]]:
    """Lyrical Sustain: Long breathing phrases, whole/half notes."""
    bars = []
    
    # Bar 1: Amaj9 - Open with sustained 3rd
    bar1 = [n("C#", 5, WHOLE)]
    verify_bar(bar1, 1, "A")
    bars.append(bar1)
    
    # Bar 2: F#m11 - Descend to minor color
    bar2 = [n("A", 4, HALF), n("F#", 4, HALF)]
    verify_bar(bar2, 2, "A")
    bars.append(bar2)
    
    # Bar 3: Dmaj9 - Bright neighbor, rise
    bar3 = [n("E", 5, DOTTED_HALF), r(QUARTER)]
    verify_bar(bar3, 3, "A")
    bars.append(bar3)
    
    # Bar 4: E/A - Suspension, open
    bar4 = [n("B", 4, WHOLE)]
    verify_bar(bar4, 4, "A")
    bars.append(bar4)
    
    # Bar 5: Amaj9 - Descending release begins
    bar5 = [n("G#", 5, HALF), n("E", 5, HALF)]
    verify_bar(bar5, 5, "A")
    bars.append(bar5)
    
    # Bar 6: C#m7 - Minor 3rd
    bar6 = [n("E", 5, DOTTED_HALF), n("C#", 5, QUARTER)]
    verify_bar(bar6, 6, "A")
    bars.append(bar6)
    
    # Bar 7: Bm9 - Dorian color
    bar7 = [n("D", 5, HALF), n("A", 4, HALF)]
    verify_bar(bar7, 7, "A")
    bars.append(bar7)
    
    # Bar 8: Esus4 E7 - Tension, space
    bar8 = [n("B", 4, HALF), r(HALF)]
    verify_bar(bar8, 8, "A")
    bars.append(bar8)
    
    # Bar 9: Fmaj7 - Distant color (borrowed)
    bar9 = [n("A", 4, WHOLE)]
    verify_bar(bar9, 9, "A")
    bars.append(bar9)
    
    # Bar 10: Gmaj7 - Chromatic approach
    bar10 = [n("B", 4, HALF), n("D", 5, HALF)]
    verify_bar(bar10, 10, "A")
    bars.append(bar10)
    
    # Bar 11: Amaj9 - Return home
    bar11 = [n("C#", 5, DOTTED_HALF), r(QUARTER)]
    verify_bar(bar11, 11, "A")
    bars.append(bar11)
    
    # Bar 12: Dmaj7 - Bright IV
    bar12 = [n("F#", 5, WHOLE)]
    verify_bar(bar12, 12, "A")
    bars.append(bar12)
    
    # Bar 13: Bm11 - Return begins fading
    bar13 = [n("D", 5, HALF), n("B", 4, HALF)]
    verify_bar(bar13, 13, "A")
    bars.append(bar13)
    
    # Bar 14: E7sus4 - Suspension
    bar14 = [n("A", 4, DOTTED_HALF), r(QUARTER)]
    verify_bar(bar14, 14, "A")
    bars.append(bar14)
    
    # Bar 15: Amaj9 - Home, fading
    bar15 = [n("E", 5, HALF), n("C#", 5, HALF)]
    verify_bar(bar15, 15, "A")
    bars.append(bar15)
    
    # Bar 16: Amaj9 - Final sustain, fade to silence
    bar16 = [n("A", 4, WHOLE)]
    verify_bar(bar16, 16, "A")
    bars.append(bar16)
    
    return bars


# ============================================================================
# VERSION B: CAMPANELLA ARPEGGIOS
# ============================================================================

def generate_version_b() -> List[List[Note]]:
    """Campanella Arpeggios: Harp-like, notes ring into each other."""
    bars = []
    
    # Bar 1: Amaj9 - Open string arpeggio
    bar1 = [
        n("A", 3, EIGHTH), n("E", 4, EIGHTH), n("C#", 5, EIGHTH), n("B", 4, EIGHTH),
        n("E", 5, EIGHTH), n("A", 4, EIGHTH), n("C#", 5, EIGHTH), n("E", 4, EIGHTH)
    ]
    verify_bar(bar1, 1, "B")
    bars.append(bar1)
    
    # Bar 2: F#m11 - Minor arpeggio with suspension
    bar2 = [
        n("F#", 3, EIGHTH), n("A", 4, EIGHTH), n("E", 4, EIGHTH), n("B", 4, EIGHTH),
        n("C#", 5, EIGHTH), n("F#", 4, EIGHTH), n("A", 4, EIGHTH), n("E", 5, EIGHTH)
    ]
    verify_bar(bar2, 2, "B")
    bars.append(bar2)
    
    # Bar 3: Dmaj9 - Bright Lydian arpeggio
    bar3 = [
        n("D", 4, EIGHTH), n("A", 4, EIGHTH), n("F#", 4, EIGHTH), n("E", 5, EIGHTH),
        n("C#", 5, EIGHTH), n("D", 5, EIGHTH), n("A", 4, EIGHTH), n("F#", 5, EIGHTH)
    ]
    verify_bar(bar3, 3, "B")
    bars.append(bar3)
    
    # Bar 4: E/A - E over A arpeggio
    bar4 = [
        n("A", 3, EIGHTH), n("E", 4, EIGHTH), n("G#", 4, EIGHTH), n("B", 4, EIGHTH),
        n("E", 5, EIGHTH), n("G#", 4, EIGHTH), n("B", 4, EIGHTH), n("E", 4, EIGHTH)
    ]
    verify_bar(bar4, 4, "B")
    bars.append(bar4)
    
    # Bar 5: Amaj9 - Descending campanella
    bar5 = [
        n("E", 5, EIGHTH), n("C#", 5, EIGHTH), n("B", 4, EIGHTH), n("A", 4, EIGHTH),
        n("G#", 4, EIGHTH), n("E", 4, EIGHTH), n("C#", 4, EIGHTH), n("A", 3, EIGHTH)
    ]
    verify_bar(bar5, 5, "B")
    bars.append(bar5)
    
    # Bar 6: C#m7 - Minor cascade
    bar6 = [
        n("C#", 4, EIGHTH), n("E", 4, EIGHTH), n("G#", 4, EIGHTH), n("B", 4, EIGHTH),
        n("C#", 5, EIGHTH), n("E", 5, EIGHTH), n("G#", 4, EIGHTH), n("B", 4, EIGHTH)
    ]
    verify_bar(bar6, 6, "B")
    bars.append(bar6)
    
    # Bar 7: Bm9 - Dorian arpeggio
    bar7 = [
        n("B", 3, EIGHTH), n("D", 4, EIGHTH), n("F#", 4, EIGHTH), n("A", 4, EIGHTH),
        n("C#", 5, EIGHTH), n("D", 5, EIGHTH), n("F#", 4, EIGHTH), n("B", 4, EIGHTH)
    ]
    verify_bar(bar7, 7, "B")
    bars.append(bar7)
    
    # Bar 8: Esus4 E7 - Suspension arpeggio, space
    bar8 = [
        n("E", 4, EIGHTH), n("A", 4, EIGHTH), n("B", 4, EIGHTH), n("E", 5, EIGHTH),
        r(QUARTER), n("G#", 4, QUARTER)
    ]
    verify_bar(bar8, 8, "B")
    bars.append(bar8)
    
    # Bar 9: Fmaj7 - Borrowed color
    bar9 = [
        n("F", 4, EIGHTH), n("A", 4, EIGHTH), n("C", 5, EIGHTH), n("E", 5, EIGHTH),
        n("F", 5, EIGHTH), n("C", 5, EIGHTH), n("A", 4, EIGHTH), n("E", 4, EIGHTH)
    ]
    verify_bar(bar9, 9, "B")
    bars.append(bar9)
    
    # Bar 10: Gmaj7 - Chromatic neighbor
    bar10 = [
        n("G", 4, EIGHTH), n("B", 4, EIGHTH), n("D", 5, EIGHTH), n("F#", 5, EIGHTH),
        n("G", 5, EIGHTH), n("D", 5, EIGHTH), n("B", 4, EIGHTH), n("G", 4, EIGHTH)
    ]
    verify_bar(bar10, 10, "B")
    bars.append(bar10)
    
    # Bar 11: Amaj9 - Return, ascending
    bar11 = [
        n("A", 3, EIGHTH), n("C#", 4, EIGHTH), n("E", 4, EIGHTH), n("G#", 4, EIGHTH),
        n("B", 4, EIGHTH), n("C#", 5, EIGHTH), n("E", 5, EIGHTH), n("A", 4, EIGHTH)
    ]
    verify_bar(bar11, 11, "B")
    bars.append(bar11)
    
    # Bar 12: Dmaj7 - Bright IV
    bar12 = [
        n("D", 4, EIGHTH), n("F#", 4, EIGHTH), n("A", 4, EIGHTH), n("C#", 5, EIGHTH),
        n("D", 5, EIGHTH), n("F#", 5, EIGHTH), n("A", 4, EIGHTH), n("D", 5, EIGHTH)
    ]
    verify_bar(bar12, 12, "B")
    bars.append(bar12)
    
    # Bar 13: Bm11 - Settling
    bar13 = [
        n("B", 3, EIGHTH), n("D", 4, EIGHTH), n("E", 4, EIGHTH), n("F#", 4, EIGHTH),
        n("A", 4, EIGHTH), n("B", 4, EIGHTH), n("D", 5, EIGHTH), n("E", 5, EIGHTH)
    ]
    verify_bar(bar13, 13, "B")
    bars.append(bar13)
    
    # Bar 14: E7sus4 - Tension then space
    bar14 = [
        n("E", 4, EIGHTH), n("A", 4, EIGHTH), n("B", 4, EIGHTH), n("D", 5, EIGHTH),
        n("E", 5, QUARTER), r(QUARTER)
    ]
    verify_bar(bar14, 14, "B")
    bars.append(bar14)
    
    # Bar 15: Amaj9 - Fading cascade
    bar15 = [
        n("E", 5, EIGHTH), n("C#", 5, EIGHTH), n("B", 4, EIGHTH), n("A", 4, EIGHTH),
        n("E", 4, EIGHTH), n("C#", 4, QUARTER), r(EIGHTH)
    ]
    verify_bar(bar15, 15, "B")
    bars.append(bar15)
    
    # Bar 16: Amaj9 - Final shimmer
    bar16 = [
        n("A", 3, QUARTER), n("E", 4, QUARTER), n("C#", 5, QUARTER), n("A", 4, QUARTER)
    ]
    verify_bar(bar16, 16, "B")
    bars.append(bar16)
    
    return bars


# ============================================================================
# VERSION C: HIGH POSITION + DRONE
# ============================================================================

def generate_version_c() -> List[List[Note]]:
    """High Position + Drone: Melody in high register over low drone."""
    bars = []
    
    # Drone is open A (A3), melody in high position (octave 4-5)
    
    # Bar 1: Amaj9 - Drone + high melody
    bar1 = [
        (n("A", 3, WHOLE), n("C#", 5, HALF)),  # Drone + high melody
        (None, n("E", 5, HALF))
    ]
    bars.append(("drone", bar1))
    
    # Bar 2: F#m11
    bar2 = [
        (n("A", 3, WHOLE), n("F#", 4, HALF)),
        (None, n("A", 4, HALF))
    ]
    bars.append(("drone", bar2))
    
    # Bar 3: Dmaj9
    bar3 = [
        (n("A", 3, WHOLE), n("F#", 5, DOTTED_HALF)),
        (None, r(QUARTER))
    ]
    bars.append(("drone", bar3))
    
    # Bar 4: E/A
    bar4 = [
        (n("A", 3, WHOLE), n("G#", 4, HALF)),
        (None, n("B", 4, HALF))
    ]
    bars.append(("drone", bar4))
    
    # Bar 5: Amaj9
    bar5 = [
        (n("A", 3, WHOLE), n("E", 5, HALF)),
        (None, n("C#", 5, HALF))
    ]
    bars.append(("drone", bar5))
    
    # Bar 6: C#m7
    bar6 = [
        (n("A", 3, WHOLE), n("C#", 5, WHOLE))
    ]
    bars.append(("drone", bar6))
    
    # Bar 7: Bm9
    bar7 = [
        (n("A", 3, WHOLE), n("D", 5, HALF)),
        (None, n("B", 4, HALF))
    ]
    bars.append(("drone", bar7))
    
    # Bar 8: Esus4 E7 - Drone continues, melody pauses
    bar8 = [
        (n("E", 3, WHOLE), n("B", 4, HALF)),
        (None, r(HALF))
    ]
    bars.append(("drone", bar8))
    
    # Bar 9: Fmaj7 - Distant color, E drone (melody in high position)
    bar9 = [
        (n("E", 3, WHOLE), n("A", 4, HALF)),
        (None, n("C", 5, HALF))
    ]
    bars.append(("drone", bar9))
    
    # Bar 10: Gmaj7
    bar10 = [
        (n("E", 3, WHOLE), n("B", 4, HALF)),
        (None, n("D", 5, HALF))
    ]
    bars.append(("drone", bar10))
    
    # Bar 11: Amaj9 - Return to A drone
    bar11 = [
        (n("A", 3, WHOLE), n("C#", 5, DOTTED_HALF)),
        (None, r(QUARTER))
    ]
    bars.append(("drone", bar11))
    
    # Bar 12: Dmaj7
    bar12 = [
        (n("A", 3, WHOLE), n("F#", 5, HALF)),
        (None, n("D", 5, HALF))
    ]
    bars.append(("drone", bar12))
    
    # Bar 13: Bm11
    bar13 = [
        (n("A", 3, WHOLE), n("D", 5, HALF)),
        (None, n("B", 4, HALF))
    ]
    bars.append(("drone", bar13))
    
    # Bar 14: E7sus4
    bar14 = [
        (n("E", 3, WHOLE), n("A", 4, WHOLE))
    ]
    bars.append(("drone", bar14))
    
    # Bar 15: Amaj9
    bar15 = [
        (n("A", 3, WHOLE), n("E", 5, HALF)),
        (None, n("C#", 5, HALF))
    ]
    bars.append(("drone", bar15))
    
    # Bar 16: Amaj9 - Final drone fade (high melody)
    bar16 = [
        (n("A", 3, WHOLE), n("A", 4, WHOLE))
    ]
    bars.append(("drone", bar16))
    
    return bars


# ============================================================================
# VERSION D: HYBRID
# ============================================================================

def generate_version_d() -> List[List]:
    """Hybrid: Combines lyrical, campanella, and drone textures."""
    bars = []
    
    # Bars 1-4: LYRICAL (from A)
    bar1 = [n("C#", 5, WHOLE)]
    verify_bar(bar1, 1, "D")
    bars.append(("lyrical", bar1))
    
    bar2 = [n("A", 4, HALF), n("F#", 4, HALF)]
    verify_bar(bar2, 2, "D")
    bars.append(("lyrical", bar2))
    
    bar3 = [n("E", 5, DOTTED_HALF), r(QUARTER)]
    verify_bar(bar3, 3, "D")
    bars.append(("lyrical", bar3))
    
    bar4 = [n("B", 4, WHOLE)]
    verify_bar(bar4, 4, "D")
    bars.append(("lyrical", bar4))
    
    # Bars 5-8: CAMPANELLA (from B)
    bar5 = [
        n("E", 5, EIGHTH), n("C#", 5, EIGHTH), n("B", 4, EIGHTH), n("A", 4, EIGHTH),
        n("G#", 4, EIGHTH), n("E", 4, EIGHTH), n("C#", 4, EIGHTH), n("A", 3, EIGHTH)
    ]
    verify_bar(bar5, 5, "D")
    bars.append(("campanella", bar5))
    
    bar6 = [
        n("C#", 4, EIGHTH), n("E", 4, EIGHTH), n("G#", 4, EIGHTH), n("B", 4, EIGHTH),
        n("C#", 5, EIGHTH), n("E", 5, EIGHTH), n("G#", 4, EIGHTH), n("B", 4, EIGHTH)
    ]
    verify_bar(bar6, 6, "D")
    bars.append(("campanella", bar6))
    
    bar7 = [
        n("B", 3, EIGHTH), n("D", 4, EIGHTH), n("F#", 4, EIGHTH), n("A", 4, EIGHTH),
        n("C#", 5, EIGHTH), n("D", 5, EIGHTH), n("F#", 4, EIGHTH), n("B", 4, EIGHTH)
    ]
    verify_bar(bar7, 7, "D")
    bars.append(("campanella", bar7))
    
    bar8 = [
        n("E", 4, EIGHTH), n("A", 4, EIGHTH), n("B", 4, EIGHTH), n("E", 5, EIGHTH),
        r(QUARTER), n("G#", 4, QUARTER)
    ]
    verify_bar(bar8, 8, "D")
    bars.append(("campanella", bar8))
    
    # Bars 9-12: DRONE + high melody (from C, melody in high position)
    bar9 = [
        (n("E", 3, WHOLE), n("A", 4, HALF)),
        (None, n("C", 5, HALF))
    ]
    bars.append(("drone", bar9))
    
    bar10 = [
        (n("E", 3, WHOLE), n("B", 4, HALF)),
        (None, n("D", 5, HALF))
    ]
    bars.append(("drone", bar10))
    
    bar11 = [
        (n("A", 3, WHOLE), n("C#", 5, DOTTED_HALF)),
        (None, r(QUARTER))
    ]
    bars.append(("drone", bar11))
    
    bar12 = [
        (n("A", 3, WHOLE), n("F#", 5, HALF)),
        (None, n("D", 5, HALF))
    ]
    bars.append(("drone", bar12))
    
    # Bars 13-16: LYRICAL FADE (from A)
    bar13 = [n("D", 5, HALF), n("B", 4, HALF)]
    verify_bar(bar13, 13, "D")
    bars.append(("lyrical", bar13))
    
    bar14 = [n("A", 4, DOTTED_HALF), r(QUARTER)]
    verify_bar(bar14, 14, "D")
    bars.append(("lyrical", bar14))
    
    bar15 = [n("E", 5, HALF), n("C#", 5, HALF)]
    verify_bar(bar15, 15, "D")
    bars.append(("lyrical", bar15))
    
    bar16 = [n("A", 4, WHOLE)]
    verify_bar(bar16, 16, "D")
    bars.append(("lyrical", bar16))
    
    return bars


# ============================================================================
# MUSICXML GENERATION
# ============================================================================

class CrystalSilenceMusicXMLGenerator:
    def __init__(self, version: str, title_suffix: str):
        self.version = version
        self.title = f"Crystal Silence ({version}) - {title_suffix}"
        self.divisions = DIVISIONS
        
    def get_duration_type(self, dur: int) -> Tuple[str, bool]:
        if dur == WHOLE:
            return ("whole", False)
        elif dur == DOTTED_HALF:
            return ("half", True)
        elif dur == HALF:
            return ("half", False)
        elif dur == DOTTED_QUARTER:
            return ("quarter", True)
        elif dur == QUARTER:
            return ("quarter", False)
        elif dur == DOTTED_EIGHTH:
            return ("eighth", True)
        elif dur == EIGHTH:
            return ("eighth", False)
        elif dur == SIXTEENTH:
            return ("16th", False)
        else:
            return ("quarter", False)
    
    def add_note_element(self, measure: ET.Element, note: Note, is_chord: bool = False, voice: int = 1):
        note_elem = ET.SubElement(measure, "note")
        
        if is_chord:
            ET.SubElement(note_elem, "chord")
        
        if note.is_rest:
            ET.SubElement(note_elem, "rest")
        else:
            pitch = ET.SubElement(note_elem, "pitch")
            step, octave, alter = note.get_xml_pitch()
            ET.SubElement(pitch, "step").text = step
            if alter != 0:
                ET.SubElement(pitch, "alter").text = str(alter)
            ET.SubElement(pitch, "octave").text = str(octave)
        
        ET.SubElement(note_elem, "duration").text = str(note.duration)
        
        dur_type, is_dotted = self.get_duration_type(note.duration)
        ET.SubElement(note_elem, "type").text = dur_type
        if is_dotted:
            ET.SubElement(note_elem, "dot")
        
        ET.SubElement(note_elem, "voice").text = str(voice)
        
        # Add dynamics marking for first note (pp)
        if not is_chord and not note.is_rest:
            notations = ET.SubElement(note_elem, "notations")
            dynamics = ET.SubElement(notations, "dynamics")
            ET.SubElement(dynamics, "pp")
    
    def create_part(self, part_elem: ET.Element, bars: List):
        for bar_num, bar_data in enumerate(bars, 1):
            measure = ET.SubElement(part_elem, "measure")
            measure.set("number", str(bar_num))
            
            if bar_num == 1:
                attrs = ET.SubElement(measure, "attributes")
                ET.SubElement(attrs, "divisions").text = str(self.divisions)
                
                key = ET.SubElement(attrs, "key")
                ET.SubElement(key, "fifths").text = "3"  # A major (3 sharps)
                ET.SubElement(key, "mode").text = "major"
                
                time = ET.SubElement(attrs, "time")
                ET.SubElement(time, "beats").text = "4"
                ET.SubElement(time, "beat-type").text = "4"
                
                clef = ET.SubElement(attrs, "clef")
                ET.SubElement(clef, "sign").text = "G"
                ET.SubElement(clef, "line").text = "2"
                ET.SubElement(clef, "clef-octave-change").text = "-1"
                
                direction = ET.SubElement(measure, "direction")
                direction.set("placement", "above")
                dir_type = ET.SubElement(direction, "direction-type")
                metro = ET.SubElement(dir_type, "metronome")
                ET.SubElement(metro, "beat-unit").text = "quarter"
                ET.SubElement(metro, "per-minute").text = "80"
                sound = ET.SubElement(direction, "sound")
                sound.set("tempo", "80")
            
            # Handle different bar formats
            if isinstance(bar_data, tuple):
                mode, notes = bar_data
                if mode == "drone":
                    # Two voices - drone and melody
                    for pair in notes:
                        if isinstance(pair, tuple):
                            drone, melody = pair
                            if drone:
                                self.add_note_element(measure, drone, voice=2)
                            if melody:
                                self.add_note_element(measure, melody, is_chord=bool(drone), voice=1)
                elif mode in ("lyrical", "campanella"):
                    for note in notes:
                        self.add_note_element(measure, note)
            else:
                # Simple note list
                for note in bar_data:
                    self.add_note_element(measure, note)
    
    def generate(self, bars: List) -> str:
        root = ET.Element("score-partwise")
        root.set("version", "4.0")
        
        work = ET.SubElement(root, "work")
        ET.SubElement(work, "work-title").text = self.title
        
        ident = ET.SubElement(root, "identification")
        creator = ET.SubElement(ident, "creator")
        creator.set("type", "composer")
        creator.text = "GCE (ECM Ballad Style)"
        
        part_list = ET.SubElement(root, "part-list")
        score_part = ET.SubElement(part_list, "score-part")
        score_part.set("id", "P1")
        ET.SubElement(score_part, "part-name").text = "Guitar"
        
        part = ET.SubElement(root, "part")
        part.set("id", "P1")
        self.create_part(part, bars)
        
        xml_str = ET.tostring(root, encoding="unicode")
        parsed = minidom.parseString(xml_str)
        return '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n' + parsed.toprettyxml(indent="  ")[23:]


def generate_notes_md(version: str, title: str, description: str, technique: str, listening_cues: List[str], practice_focus: str) -> str:
    return f"""# Crystal Silence ({version}) - {title}

## Intent
{description}

## Campanella / Drone Technique
{technique}

## What to Listen For
1. {listening_cues[0]}
2. {listening_cues[1]}
3. {listening_cues[2]}

## Practice Focus
{practice_focus}

## Version Comparison
| Version | Role | Character |
|---------|------|-----------|
| A - Lyrical Sustain | The tune itself | Long tones, breathing phrases |
| B - Campanella Arpeggios | Harp-like resonance | Notes ring into each other |
| C - High Position + Drone | Sitar texture | Melody floats over pedal |
| D - Hybrid | Integration model | Combines all textures |

---
*Generated for GCE Jazz - Trio Tunes Project*
*Style: ECM Ballad (Ralph Towner / Egberto Gismonti)*
"""


def generate_html_playalong() -> str:
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crystal Silence - Play Along</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e8e8e8;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #a8d8ea;
            text-shadow: 0 0 20px rgba(168, 216, 234, 0.3);
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-style: italic;
        }
        .controls {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        button {
            background: linear-gradient(145deg, #3a506b, #1c2541);
            color: #e8e8e8;
            border: 1px solid #5c6b7a;
            padding: 12px 30px;
            font-size: 1.1em;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        button:hover {
            background: linear-gradient(145deg, #5c6b7a, #3a506b);
            box-shadow: 0 0 15px rgba(168, 216, 234, 0.3);
        }
        button.active {
            background: linear-gradient(145deg, #a8d8ea, #88c0d0);
            color: #1a1a2e;
        }
        .tempo-control {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        input[type="range"] {
            width: 150px;
            accent-color: #a8d8ea;
        }
        .bar-display {
            font-size: 4em;
            text-align: center;
            color: #a8d8ea;
            margin: 30px 0;
            font-weight: bold;
        }
        .form-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 30px;
        }
        .bar-block {
            background: linear-gradient(145deg, #2a3a4a, #1c2541);
            border: 2px solid #3a506b;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            transition: all 0.2s ease;
        }
        .bar-block.current {
            background: linear-gradient(145deg, #a8d8ea, #88c0d0);
            color: #1a1a2e;
            border-color: #a8d8ea;
            box-shadow: 0 0 20px rgba(168, 216, 234, 0.5);
            transform: scale(1.05);
        }
        .bar-block .bar-num { font-size: 1.5em; font-weight: bold; }
        .bar-block .chord { font-size: 0.9em; color: #888; margin-top: 5px; }
        .bar-block.current .chord { color: #1a1a2e; }
        .section-label {
            grid-column: span 4;
            text-align: center;
            color: #a8d8ea;
            font-size: 0.9em;
            margin: 10px 0;
        }
        .loop-buttons { margin-bottom: 20px; text-align: center; }
        .loop-buttons button { margin: 5px; padding: 8px 20px; font-size: 0.9em; }
        @media print {
            body { background: white; color: black; }
            .controls, .loop-buttons { display: none; }
            .bar-block { border: 1px solid #333; }
            h1 { color: #333; text-shadow: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Crystal Silence</h1>
        <p class="subtitle">ECM Ballad | A Major | 80 BPM | 4/4</p>
        
        <div class="controls">
            <button id="startBtn" onclick="togglePlay()">Start</button>
            <div class="tempo-control">
                <span>Tempo:</span>
                <input type="range" id="tempoSlider" min="40" max="120" value="80" onchange="updateTempo()">
                <span id="tempoValue">80</span>
            </div>
        </div>
        
        <div class="loop-buttons">
            <button onclick="setLoop(1,8)">A Section (1-8)</button>
            <button onclick="setLoop(9,16)">B Section (9-16)</button>
            <button onclick="setLoop(1,16)">Full Form</button>
        </div>
        
        <div class="bar-display">Bar: <span id="currentBar">1</span></div>
        
        <div class="form-grid">
            <div class="section-label">Section A</div>
            <div class="bar-block" data-bar="1"><div class="bar-num">1</div><div class="chord">Amaj9</div></div>
            <div class="bar-block" data-bar="2"><div class="bar-num">2</div><div class="chord">F#m11</div></div>
            <div class="bar-block" data-bar="3"><div class="bar-num">3</div><div class="chord">Dmaj9</div></div>
            <div class="bar-block" data-bar="4"><div class="bar-num">4</div><div class="chord">E/A</div></div>
            <div class="bar-block" data-bar="5"><div class="bar-num">5</div><div class="chord">Amaj9</div></div>
            <div class="bar-block" data-bar="6"><div class="bar-num">6</div><div class="chord">C#m7</div></div>
            <div class="bar-block" data-bar="7"><div class="bar-num">7</div><div class="chord">Bm9</div></div>
            <div class="bar-block" data-bar="8"><div class="bar-num">8</div><div class="chord">Esus E7</div></div>
            
            <div class="section-label">Section B</div>
            <div class="bar-block" data-bar="9"><div class="bar-num">9</div><div class="chord">Fmaj7</div></div>
            <div class="bar-block" data-bar="10"><div class="bar-num">10</div><div class="chord">Gmaj7</div></div>
            <div class="bar-block" data-bar="11"><div class="bar-num">11</div><div class="chord">Amaj9</div></div>
            <div class="bar-block" data-bar="12"><div class="bar-num">12</div><div class="chord">Dmaj7</div></div>
            <div class="bar-block" data-bar="13"><div class="bar-num">13</div><div class="chord">Bm11</div></div>
            <div class="bar-block" data-bar="14"><div class="bar-num">14</div><div class="chord">E7sus</div></div>
            <div class="bar-block" data-bar="15"><div class="bar-num">15</div><div class="chord">Amaj9</div></div>
            <div class="bar-block" data-bar="16"><div class="bar-num">16</div><div class="chord">Amaj9</div></div>
        </div>
    </div>
    
    <script>
        let isPlaying = false;
        let currentBar = 1;
        let tempo = 80;
        let loopStart = 1;
        let loopEnd = 16;
        let intervalId = null;
        let audioCtx = null;
        
        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
        }
        
        function playClick() {
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.frequency.value = currentBar === loopStart ? 880 : 440;
            gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
            osc.start(audioCtx.currentTime);
            osc.stop(audioCtx.currentTime + 0.1);
        }
        
        function updateDisplay() {
            document.getElementById('currentBar').textContent = currentBar;
            document.querySelectorAll('.bar-block').forEach(block => {
                block.classList.remove('current');
                if (parseInt(block.dataset.bar) === currentBar) {
                    block.classList.add('current');
                }
            });
        }
        
        function tick() {
            playClick();
            updateDisplay();
            currentBar++;
            if (currentBar > loopEnd) currentBar = loopStart;
        }
        
        function togglePlay() {
            initAudio();
            isPlaying = !isPlaying;
            const btn = document.getElementById('startBtn');
            if (isPlaying) {
                btn.textContent = 'Stop';
                btn.classList.add('active');
                const msPerBar = (60000 / tempo) * 4;
                tick();
                intervalId = setInterval(tick, msPerBar);
            } else {
                btn.textContent = 'Start';
                btn.classList.remove('active');
                clearInterval(intervalId);
            }
        }
        
        function updateTempo() {
            tempo = parseInt(document.getElementById('tempoSlider').value);
            document.getElementById('tempoValue').textContent = tempo;
            if (isPlaying) {
                clearInterval(intervalId);
                const msPerBar = (60000 / tempo) * 4;
                intervalId = setInterval(tick, msPerBar);
            }
        }
        
        function setLoop(start, end) {
            loopStart = start;
            loopEnd = end;
            currentBar = start;
            updateDisplay();
        }
        
        updateDisplay();
    </script>
</body>
</html>
'''


def generate_readme() -> str:
    return '''# Crystal Silence - Complete Lead Sheet Package

## Overview
ECM-style ballad featuring campanella technique, open strings, and sustained textures.

**Key:** A Major | **Tempo:** 80 BPM | **Time:** 4/4 | **Length:** 16 bars

## Directory Structure

```
Tune11_Crystal_Silence/
├── LeadSheet/
│   ├── A/                    # Lyrical Sustain
│   │   ├── Crystal_Silence-A-LeadSheet.musicxml
│   │   └── Crystal_Silence-A-Notes.md
│   ├── B/                    # Campanella Arpeggios
│   │   ├── Crystal_Silence-B-LeadSheet.musicxml
│   │   └── Crystal_Silence-B-Notes.md
│   ├── C/                    # High Position + Drone
│   │   ├── Crystal_Silence-C-LeadSheet.musicxml
│   │   └── Crystal_Silence-C-Notes.md
│   └── D/                    # Hybrid
│       ├── Crystal_Silence-D-LeadSheet.musicxml
│       └── Crystal_Silence-D-Notes.md
├── Practice/
│   ├── 01_Lyrical_Sustain_Studies/
│   ├── 02_Campanella_Arpeggio_Studies/
│   ├── 03_Drone_and_HighRegister_Studies/
│   ├── 04_Hybrid_Integration_Studies/
│   └── 05_Space_Silence_Dynamics/
├── Crystal_Silence_PlayAlong.html
├── export_pdfs.ps1
└── README.md
```

## Version Descriptions

### A - Lyrical Sustain
The tune itself. Long breathing phrases, whole and half notes, maximum sustain.
Use open strings wherever possible.

### B - Campanella Arpeggios
Harp-like resonance. Notes ring into each other using different strings.
Focus on shimmering sustain, not speed.

### C - High Position + Drone
Sitar-like texture. Low drone (open A or E) with high melody (frets 9-14).
The drone never stops; melody floats above.

### D - Hybrid
Integration model. Combines all three textures across the 16-bar form.
Seamless, unannounced transitions.

## How to Export PDFs

### Option 1: MuseScore CLI (Recommended)
Run the PowerShell script:
```powershell
.\\export_pdfs.ps1
```

### Option 2: Guitar Pro 8
Open each .musicxml file in Guitar Pro and export to PDF manually.

### Option 3: Manual MuseScore
Open MuseScore > File > Open > [select .musicxml] > File > Export > PDF

## Listening References
1. Ralph Towner - Solstice
2. Egberto Gismonti - Sol Do Meio Dia
3. Pat Metheny - One Quiet Night
4. Bill Frisell - Good Dog, Happy Man

## Practice Tips
- Dynamics: Never louder than mp (mezzo-piano)
- Sustain: Let strings ring (don't dampen)
- Campanella: Use different strings for adjacent notes
- Space: The silence between notes is part of the music

---
*GCE Jazz - Trio Tunes Project*
'''


def generate_export_script() -> str:
    return '''# export_pdfs.ps1 - Crystal Silence PDF Export Script
# Attempts to use MuseScore CLI to convert MusicXML to PDF

$ErrorActionPreference = "Continue"

# Common MuseScore installation paths
$musescorePaths = @(
    "C:\\Program Files\\MuseScore 4\\bin\\MuseScore4.exe",
    "C:\\Program Files\\MuseScore 3\\bin\\MuseScore3.exe",
    "C:\\Program Files (x86)\\MuseScore 4\\bin\\MuseScore4.exe",
    "C:\\Program Files (x86)\\MuseScore 3\\bin\\MuseScore3.exe",
    "$env:LOCALAPPDATA\\Programs\\MuseScore 4\\bin\\MuseScore4.exe"
)

$musescore = $null
foreach ($path in $musescorePaths) {
    if (Test-Path $path) {
        $musescore = $path
        break
    }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($musescore) {
    Write-Host "Found MuseScore at: $musescore" -ForegroundColor Green
    Write-Host "Converting MusicXML files to PDF..." -ForegroundColor Cyan
    
    # Find all .musicxml files
    $xmlFiles = Get-ChildItem -Path $scriptDir -Recurse -Filter "*.musicxml"
    
    foreach ($file in $xmlFiles) {
        $pdfPath = $file.FullName -replace "\\.musicxml$", ".pdf"
        Write-Host "Converting: $($file.Name)"
        
        try {
            & $musescore -o $pdfPath $file.FullName 2>$null
            if (Test-Path $pdfPath) {
                Write-Host "  [OK] Created: $pdfPath" -ForegroundColor Green
            }
        } catch {
            Write-Host "  [WARN] Could not convert $($file.Name)" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`nConversion complete!" -ForegroundColor Green
} else {
    Write-Host "MuseScore not found in common installation paths." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To export PDFs manually:" -ForegroundColor Cyan
    Write-Host "1. Download MuseScore from https://musescore.org/download"
    Write-Host "2. Install and rerun this script"
    Write-Host ""
    Write-Host "Or use Guitar Pro 8:" -ForegroundColor Cyan
    Write-Host "1. Open each .musicxml file in Guitar Pro 8"
    Write-Host "2. File > Export > PDF"
    Write-Host ""
    Write-Host "MusicXML files are located at:"
    Get-ChildItem -Path $scriptDir -Recurse -Filter "*.musicxml" | ForEach-Object {
        Write-Host "  $($_.FullName)"
    }
}
'''


# ============================================================================
# EXERCISE GENERATION
# ============================================================================

def generate_exercise_study(name: str, description: str, technique: str) -> Tuple[str, str]:
    """Generate a simple exercise study MusicXML and MD."""
    # Simplified 8-bar exercise based on A section
    generator = CrystalSilenceMusicXMLGenerator("Study", name)
    
    # Simple 8-bar pattern
    bars = []
    if "Lyrical" in name:
        bars = [
            [n("A", 4, WHOLE)],
            [n("C#", 5, HALF), n("E", 5, HALF)],
            [n("F#", 5, DOTTED_HALF), r(QUARTER)],
            [n("E", 5, WHOLE)],
            [n("D", 5, HALF), n("B", 4, HALF)],
            [n("A", 4, DOTTED_HALF), r(QUARTER)],
            [n("G#", 4, HALF), n("E", 4, HALF)],
            [n("A", 4, WHOLE)]
        ]
    elif "Campanella" in name:
        bars = [
            [n("A", 3, EIGHTH), n("E", 4, EIGHTH), n("C#", 5, EIGHTH), n("A", 4, EIGHTH),
             n("E", 5, EIGHTH), n("C#", 5, EIGHTH), n("A", 4, EIGHTH), n("E", 4, EIGHTH)],
            [n("F#", 4, EIGHTH), n("A", 4, EIGHTH), n("C#", 5, EIGHTH), n("E", 5, EIGHTH),
             n("F#", 5, EIGHTH), n("E", 5, EIGHTH), n("C#", 5, EIGHTH), n("A", 4, EIGHTH)],
            [n("D", 4, EIGHTH), n("F#", 4, EIGHTH), n("A", 4, EIGHTH), n("D", 5, EIGHTH),
             n("F#", 5, EIGHTH), n("A", 4, EIGHTH), n("D", 5, EIGHTH), n("F#", 4, EIGHTH)],
            [n("E", 4, EIGHTH), n("G#", 4, EIGHTH), n("B", 4, EIGHTH), n("E", 5, EIGHTH),
             n("G#", 4, QUARTER), r(QUARTER)],
            [n("A", 3, EIGHTH), n("C#", 4, EIGHTH), n("E", 4, EIGHTH), n("A", 4, EIGHTH),
             n("C#", 5, EIGHTH), n("E", 5, EIGHTH), n("A", 4, EIGHTH), n("E", 4, EIGHTH)],
            [n("B", 3, EIGHTH), n("D", 4, EIGHTH), n("F#", 4, EIGHTH), n("A", 4, EIGHTH),
             n("B", 4, EIGHTH), n("D", 5, EIGHTH), n("F#", 4, EIGHTH), n("D", 4, EIGHTH)],
            [n("E", 4, EIGHTH), n("A", 4, EIGHTH), n("B", 4, EIGHTH), n("E", 5, EIGHTH),
             n("B", 4, QUARTER), r(QUARTER)],
            [n("A", 3, QUARTER), n("E", 4, QUARTER), n("C#", 5, QUARTER), n("A", 4, QUARTER)]
        ]
    elif "Drone" in name:
        bars = [
            [n("A", 3, WHOLE)],
            [n("A", 3, WHOLE)],
            [n("A", 3, WHOLE)],
            [n("A", 3, WHOLE)],
            [n("E", 3, WHOLE)],
            [n("E", 3, WHOLE)],
            [n("A", 3, WHOLE)],
            [n("A", 3, WHOLE)]
        ]
    else:  # Hybrid or Space
        bars = [
            [n("A", 4, WHOLE)],
            [n("E", 5, HALF), r(HALF)],
            [n("C#", 5, QUARTER), n("A", 4, QUARTER), r(HALF)],
            [r(WHOLE)],
            [n("F#", 5, HALF), n("D", 5, HALF)],
            [r(HALF), n("B", 4, HALF)],
            [n("A", 4, DOTTED_HALF), r(QUARTER)],
            [r(WHOLE)]
        ]
    
    # Truncate to 8 bars
    bars = bars[:8]
    
    xml_content = generator.generate(bars)
    
    md_content = f"""# {name}

## Description
{description}

## Technique Focus
{technique}

## Practice Instructions
1. Play at 60 BPM first, focusing on sustain
2. Let all notes ring their full duration
3. Gradually increase to 80 BPM
4. Record yourself and listen for ringing quality

## Tips
- Never louder than mp
- Use open strings when possible
- Let strings ring into each other

---
*Crystal Silence Exercise Study*
"""
    
    return xml_content, md_content


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("CRYSTAL SILENCE - FULL PIPELINE GENERATION")
    print("ECM Ballad | A Major | 80 BPM | 4/4")
    print("=" * 70)
    
    base_path = Path(__file__).parent.parent / "Trio Tunes" / "Tune11_Crystal_Silence"
    leadsheet_path = base_path / "LeadSheet"
    alt_path = Path(__file__).parent.parent / "Trio Tunes" / "Alternative_LeadSheets" / "CrystalSilence_ECM"
    
    # Create directories
    alt_path.mkdir(parents=True, exist_ok=True)
    
    # =========================================================================
    # TASK A: Generate 4 Lead Sheets
    # =========================================================================
    print("\n" + "=" * 50)
    print("TASK A: Generating Lead Sheets A-D")
    print("=" * 50)
    
    versions = {
        "A": {
            "title": "Lyrical Sustain",
            "generator": generate_version_a,
            "description": "The tune itself. Long breathing phrases with maximum sustain. Whole and half notes predominate.",
            "technique": "Standard sustained playing with open strings ringing freely.",
            "listening_cues": [
                "The arc of the phrase across 4-bar groups",
                "How silence contributes to the music",
                "The color shift at bars 9-10 (Fmaj7, Gmaj7)"
            ],
            "practice_focus": "Focus on letting every note ring its full duration. No dampening."
        },
        "B": {
            "title": "Campanella Arpeggios",
            "generator": generate_version_b,
            "description": "Harp-like arpeggiated lines where notes ring into each other.",
            "technique": "Campanella: Use different strings for adjacent notes so they overlap and sustain together.",
            "listening_cues": [
                "The shimmering quality as notes sustain into each other",
                "How register changes create variety",
                "The difference between ascending and descending patterns"
            ],
            "practice_focus": "Play slowly and listen for overlapping sustain. Speed is not the goal."
        },
        "C": {
            "title": "High Position + Drone",
            "generator": generate_version_c,
            "description": "Sitar-like texture with low drone and high melody.",
            "technique": "The open A or E string provides a continuous drone while melody floats in the high register.",
            "listening_cues": [
                "The hypnotic quality of the continuous drone",
                "How the high melody creates tension against the drone",
                "The meditative, trance-like effect"
            ],
            "practice_focus": "Keep the drone ringing throughout. The melody should never overpower it."
        },
        "D": {
            "title": "Hybrid",
            "generator": generate_version_d,
            "description": "Integration model combining lyrical, campanella, and drone textures.",
            "technique": "Seamlessly transitions between all three textures within the 16-bar form.",
            "listening_cues": [
                "How the texture shifts at bars 5, 9, and 13",
                "The unannounced transitions between styles",
                "How each section complements the others"
            ],
            "practice_focus": "Practice each 4-bar section separately, then connect them smoothly."
        }
    }
    
    for version_key, version_data in versions.items():
        print(f"\n--- Generating Version {version_key}: {version_data['title']} ---")
        
        bars = version_data["generator"]()
        
        generator = CrystalSilenceMusicXMLGenerator(version_key, version_data["title"])
        xml_content = generator.generate(bars)
        
        # Save to LeadSheet directory
        version_dir = leadsheet_path / version_key
        version_dir.mkdir(parents=True, exist_ok=True)
        
        xml_path = version_dir / f"Crystal_Silence-{version_key}-LeadSheet.musicxml"
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print(f"  [OK] Saved: {xml_path}")
        
        # Save notes MD
        md_content = generate_notes_md(
            version_key, version_data["title"], version_data["description"],
            version_data["technique"], version_data["listening_cues"],
            version_data["practice_focus"]
        )
        md_path = version_dir / f"Crystal_Silence-{version_key}-Notes.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"  [OK] Saved: {md_path}")
        
        # Also save to Alternative_LeadSheets
        alt_xml_path = alt_path / f"Crystal_Silence-{version_key}-LeadSheet.musicxml"
        with open(alt_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print(f"  [OK] Saved: {alt_xml_path}")
    
    # =========================================================================
    # TASK B: Generate Exercise Directories
    # =========================================================================
    print("\n" + "=" * 50)
    print("TASK B: Generating Exercise Directories")
    print("=" * 50)
    
    practice_path = base_path / "Practice"
    
    exercises = [
        ("01_Lyrical_Sustain_Studies", "CS_01_Lyrical_Sustain_Study",
         "Sustained long-tone practice derived from Version A",
         "Focus on whole notes and half notes with maximum sustain"),
        ("02_Campanella_Arpeggio_Studies", "CS_02_Campanella_Arpeggio_Study",
         "Harp-like arpeggio patterns derived from Version B",
         "Practice using different strings for adjacent notes"),
        ("03_Drone_and_HighRegister_Studies", "CS_03_Drone_Study",
         "Drone pedal practice derived from Version C",
         "Maintain continuous open string drone throughout"),
        ("04_Hybrid_Integration_Studies", "CS_04_Hybrid_Integration_Study",
         "Texture transition practice derived from Version D",
         "Practice seamless shifts between lyrical, campanella, and drone"),
        ("05_Space_Silence_Dynamics", "CS_05_Space_Dynamics_Study",
         "Space and silence as musical elements",
         "Focus on the rests and dynamic control (never exceed mp)")
    ]
    
    for folder, file_prefix, description, technique in exercises:
        print(f"\n--- Creating {folder} ---")
        exercise_dir = practice_path / folder
        exercise_dir.mkdir(parents=True, exist_ok=True)
        
        xml_content, md_content = generate_exercise_study(file_prefix, description, technique)
        
        xml_path = exercise_dir / f"{file_prefix}.musicxml"
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print(f"  [OK] Saved: {xml_path}")
        
        md_path = exercise_dir / f"{file_prefix}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"  [OK] Saved: {md_path}")
    
    # =========================================================================
    # TASK C: Generate Export Script
    # =========================================================================
    print("\n" + "=" * 50)
    print("TASK C: Generating PDF Export Script")
    print("=" * 50)
    
    export_script = generate_export_script()
    export_path = base_path / "export_pdfs.ps1"
    with open(export_path, "w", encoding="utf-8") as f:
        f.write(export_script)
    print(f"  [OK] Saved: {export_path}")
    
    # =========================================================================
    # TASK D: Generate HTML Play-Along
    # =========================================================================
    print("\n" + "=" * 50)
    print("TASK D: Generating HTML Play-Along")
    print("=" * 50)
    
    html_content = generate_html_playalong()
    html_path = base_path / "Crystal_Silence_PlayAlong.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  [OK] Saved: {html_path}")
    
    # =========================================================================
    # Generate README
    # =========================================================================
    print("\n" + "=" * 50)
    print("Generating README")
    print("=" * 50)
    
    readme_content = generate_readme()
    readme_path = base_path / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"  [OK] Saved: {readme_path}")
    
    # =========================================================================
    # COMPLETE
    # =========================================================================
    print("\n" + "=" * 70)
    print("CRYSTAL SILENCE FULL PIPELINE COMPLETE!")
    print("=" * 70)
    print(f"\nPrimary location: {base_path}")
    print(f"Alternative location: {alt_path}")
    print("\nGenerated:")
    print("  - 4 Lead Sheets (A-D) with MusicXML + Notes.md")
    print("  - 5 Exercise directories with studies")
    print("  - export_pdfs.ps1 (PDF export automation)")
    print("  - Crystal_Silence_PlayAlong.html")
    print("  - README.md")


if __name__ == "__main__":
    main()

