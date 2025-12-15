"""
Level 2 Shell Voicing Map Generator
====================================
Generates LilyPond source files for shell voicing maps.
Output: Standard notation + TAB, matching System2_Shell_Voicing_Map-1.png style.

Usage:
    python generate_shell_voicing_maps.py

Output:
    - Trio Tunes/Alternative_LeadSheets/The_Mirror_Level2_ShellVoicingMap.ly
    - Trio Tunes/Alternative_LeadSheets/Crystal_Silence_Level2_ShellVoicingMap.ly
    - Trio Tunes/Alternative_LeadSheets/Orbit_Level2_ShellVoicingMap.ly

To convert to PNG:
    lilypond --png -dresolution=300 <filename>.ly
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Guitar standard tuning (MIDI pitch for open strings)
# String 1 (high E) = 64, String 2 (B) = 59, String 3 (G) = 55
# String 4 (D) = 50, String 5 (A) = 45, String 6 (low E) = 40
GUITAR_TUNING = {1: 64, 2: 59, 3: 55, 4: 50, 5: 45, 6: 40}

# Note names for LilyPond (using flats where appropriate)
MIDI_TO_LILY = {
    0: "c", 1: "cis", 2: "d", 3: "ees", 4: "e", 5: "f",
    6: "fis", 7: "g", 8: "aes", 9: "a", 10: "bes", 11: "b"
}

# Alternate spellings for specific contexts
MIDI_TO_LILY_SHARP = {
    0: "c", 1: "cis", 2: "d", 3: "dis", 4: "e", 5: "f",
    6: "fis", 7: "g", 8: "gis", 9: "a", 10: "ais", 11: "b"
}


@dataclass
class ShellVoicing:
    """A shell voicing with chord name and TAB data."""
    chord_name: str
    strings: Tuple[int, int, int]  # e.g., (5, 4, 3) for A-D-G strings
    frets: Tuple[int, int, int]    # e.g., (6, 5, 8) for fret positions
    bar_number: int
    beat_position: float = 1.0    # 1.0 = beat 1, 3.0 = beat 3, etc.
    duration: str = "1"           # LilyPond duration: 1=whole, 2=half, etc.


def string_fret_to_midi(string: int, fret: int) -> int:
    """Convert string/fret to MIDI pitch."""
    return GUITAR_TUNING[string] + fret


def midi_to_lilypond(midi_pitch: int, prefer_sharp: bool = False) -> str:
    """Convert MIDI pitch to LilyPond note name with octave."""
    octave = (midi_pitch // 12) - 4  # LilyPond c' = MIDI 60 = octave 0
    pitch_class = midi_pitch % 12
    
    if prefer_sharp:
        note = MIDI_TO_LILY_SHARP[pitch_class]
    else:
        note = MIDI_TO_LILY[pitch_class]
    
    # Add octave marks
    if octave > 0:
        note += "'" * octave
    elif octave < 0:
        note += "," * abs(octave)
    
    return note


def voicing_to_lilypond_chord(voicing: ShellVoicing, prefer_sharp: bool = False) -> str:
    """Convert a shell voicing to LilyPond chord notation."""
    notes = []
    for string, fret in zip(voicing.strings, voicing.frets):
        midi = string_fret_to_midi(string, fret)
        note = midi_to_lilypond(midi, prefer_sharp)
        notes.append(note)
    
    # Sort by pitch (lowest first for LilyPond)
    midi_notes = [(string_fret_to_midi(s, f), midi_to_lilypond(string_fret_to_midi(s, f), prefer_sharp)) 
                  for s, f in zip(voicing.strings, voicing.frets)]
    midi_notes.sort(key=lambda x: x[0])
    sorted_notes = [n[1] for n in midi_notes]
    
    return f"<{' '.join(sorted_notes)}>{voicing.duration}"


def voicing_to_tab(voicing: ShellVoicing) -> str:
    """Convert a shell voicing to LilyPond TAB notation."""
    tab_notes = []
    for string, fret in zip(voicing.strings, voicing.frets):
        midi = string_fret_to_midi(string, fret)
        note = midi_to_lilypond(midi)
        # TAB uses \N for string number
        tab_notes.append(f"{note}\\{string}")
    
    # Sort by pitch
    midi_tab = [(string_fret_to_midi(s, f), f"{midi_to_lilypond(string_fret_to_midi(s, f))}\\{s}") 
                for s, f in zip(voicing.strings, voicing.frets)]
    midi_tab.sort(key=lambda x: x[0])
    sorted_tab = [n[1] for n in midi_tab]
    
    return f"<{' '.join(sorted_tab)}>{voicing.duration}"


def chord_to_lilypond(chord_name: str, duration: str = "1") -> str:
    """Convert chord name to LilyPond chordmode format."""
    # Handle special chord names
    chord = chord_name.replace("#11", "").replace("#5", "").replace("/A", "")
    
    # Extract root
    if len(chord) > 1 and chord[1] in 'b#':
        root = chord[0:2]
        quality = chord[2:]
    else:
        root = chord[0]
        quality = chord[1:]
    
    # Map root to LilyPond (Bb -> bes, C# -> cis, etc.)
    lily_root = root[0].lower()
    if len(root) > 1:
        if root[1] == 'b':
            lily_root += "es"
        elif root[1] == '#':
            lily_root += "is"
    
    # Map quality
    if 'maj7' in quality or 'maj9' in quality:
        lily_quality = ":maj7"
    elif 'm7' in quality or 'm9' in quality or 'm11' in quality:
        lily_quality = ":m7"
    elif quality == 'm':
        lily_quality = ":m"
    elif 'sus4' in quality:
        lily_quality = ":sus4"
    elif '7' in quality:
        lily_quality = ":7"
    else:
        lily_quality = ":maj7"
    
    return f"{lily_root}{duration}{lily_quality}"


def generate_lilypond_file(
    title: str,
    composer: str,
    voicings: List[ShellVoicing],
    key_signature: str,
    time_signature: str,
    section_markers: dict,  # {bar_number: "A", "B", "A'"}
    output_path: Path
) -> None:
    """Generate a complete LilyPond file with notation and TAB."""
    
    # Group voicings by bar
    bars = {}
    for v in voicings:
        if v.bar_number not in bars:
            bars[v.bar_number] = []
        bars[v.bar_number].append(v)
    
    # Build the complete LilyPond file
    lily_content = f'''\\version "2.24.0"

\\header {{
  title = "{title}"
  composer = "{composer}"
  tagline = ##f
}}

\\paper {{
  #(set-paper-size "a4")
  top-margin = 15\\mm
  bottom-margin = 15\\mm
  left-margin = 15\\mm
  right-margin = 15\\mm
  system-system-spacing.basic-distance = #18
  indent = 0
}}

% Chord names
chordNames = \\chordmode {{
'''
    
    # Add chord names
    for bar_num in sorted(bars.keys()):
        for v in bars[bar_num]:
            lily_content += f"  {chord_to_lilypond(v.chord_name, v.duration)}\n"
    
    lily_content += '''  }

% Main notation
notation = \\relative c' {
  \\clef "treble_8"
  \\key ''' + key_signature + '''
  \\time ''' + time_signature + '''
  
'''
    
    # Add notation with section markers
    for bar_num in sorted(bars.keys()):
        if bar_num in section_markers:
            marker = section_markers[bar_num]
            lily_content += f'  \\mark \\markup {{ \\box "{marker}" }}\n'
        
        for v in bars[bar_num]:
            lily_content += f'  {voicing_to_lilypond_chord(v)}\n'
        
        # System break after bar 8
        if bar_num == 8:
            lily_content += '  \\break\n'
    
    lily_content += '''  \\bar "|."
}

% TAB notation  
tabNotation = \\relative c {
  \\clef "moderntab"
  \\key ''' + key_signature + '''
  \\time ''' + time_signature + '''
  
'''
    
    # Add TAB
    for bar_num in sorted(bars.keys()):
        for v in bars[bar_num]:
            lily_content += f'  {voicing_to_tab(v)}\n'
        
        if bar_num == 8:
            lily_content += '  \\break\n'
    
    lily_content += '''  \\bar "|."
}

\\score {
  <<
    \\new ChordNames { \\chordNames }
    \\new Staff { \\notation }
    \\new TabStaff {
      \\set TabStaff.stringTunings = \\stringTuning <e, a, d g b e'>
      \\tabNotation
    }
  >>
  \\layout {
    \\context {
      \\Score
      \\override SpacingSpanner.common-shortest-duration = #(ly:make-moment 1/1)
    }
  }
}
'''
    
    output_path.write_text(lily_content, encoding='utf-8')
    print(f"Generated: {output_path}")


# =============================================================================
# SONG DATA
# =============================================================================

def get_the_mirror_voicings() -> List[ShellVoicing]:
    """The Mirror 5X - validated shell voicings from System2_Shell_Voicing_Chart.txt"""
    return [
        ShellVoicing("Abmaj7", (4, 3, 2), (6, 5, 8), 1),
        ShellVoicing("Fm7", (5, 4, 3), (8, 6, 8), 2),
        ShellVoicing("Dbmaj7", (3, 2, 1), (5, 6, 9), 3),
        ShellVoicing("Ebsus4", (5, 4, 3), (6, 6, 6), 4, duration="2"),
        ShellVoicing("Eb7", (5, 4, 3), (6, 5, 6), 4, beat_position=3.0, duration="2"),
        ShellVoicing("Abmaj7", (4, 3, 2), (6, 5, 8), 5),
        ShellVoicing("Bbm7", (4, 3, 2), (8, 6, 9), 6),
        ShellVoicing("Gbmaj7", (5, 4, 3), (8, 8, 6), 7),
        ShellVoicing("Cm7", (5, 4, 3), (6, 8, 5), 8, duration="2"),
        ShellVoicing("Fm7", (5, 4, 3), (8, 6, 8), 8, beat_position=3.0, duration="2"),
        ShellVoicing("Bmaj7", (5, 4, 3), (6, 8, 8), 9),
        ShellVoicing("Emaj7", (5, 4, 3), (7, 6, 8), 10),
        ShellVoicing("Bbm7", (4, 3, 2), (8, 6, 9), 11),
        ShellVoicing("Eb7", (5, 4, 3), (6, 5, 6), 12),
        ShellVoicing("Abmaj7", (4, 3, 2), (6, 5, 8), 13),
        ShellVoicing("Fm7", (5, 4, 3), (8, 6, 8), 14),
        ShellVoicing("Dbmaj7", (3, 2, 1), (5, 6, 9), 15, duration="2"),
        ShellVoicing("Dbm", (5, 4, 3), (7, 6, 6), 15, beat_position=3.0, duration="2"),
        ShellVoicing("Abmaj7", (4, 3, 2), (6, 5, 8), 16),
    ]


def get_crystal_silence_voicings() -> List[ShellVoicing]:
    """Crystal Silence - shell voicings calculated for frets 5-9"""
    return [
        ShellVoicing("Amaj9", (5, 4, 3), (5, 6, 6), 1),
        ShellVoicing("F#m11", (4, 3, 2), (9, 7, 9), 2),
        ShellVoicing("Dmaj9", (4, 3, 2), (5, 7, 6), 3),
        ShellVoicing("E/A", (5, 4, 3), (7, 6, 7), 4),
        ShellVoicing("Amaj9", (5, 4, 3), (5, 6, 6), 5),
        ShellVoicing("C#m7", (4, 3, 2), (9, 9, 7), 6),
        ShellVoicing("Bm9", (4, 3, 2), (7, 7, 5), 7),
        ShellVoicing("Esus4", (5, 4, 3), (7, 7, 7), 8, duration="2"),
        ShellVoicing("E7", (5, 4, 3), (7, 6, 7), 8, beat_position=3.0, duration="2"),
        ShellVoicing("Fmaj7", (5, 4, 3), (8, 7, 9), 9),
        ShellVoicing("Gmaj7", (4, 3, 2), (5, 4, 7), 10),
        ShellVoicing("Amaj9", (5, 4, 3), (5, 6, 6), 11),
        ShellVoicing("Dmaj7", (4, 3, 2), (5, 7, 6), 12),
        ShellVoicing("Bm11", (4, 3, 2), (7, 7, 5), 13),
        ShellVoicing("E7sus4", (5, 4, 3), (7, 7, 7), 14),
        ShellVoicing("Amaj9", (5, 4, 3), (5, 6, 6), 15),
        ShellVoicing("Amaj9", (5, 4, 3), (5, 6, 6), 16),
    ]


def get_orbit_voicings() -> List[ShellVoicing]:
    """Orbit - shell voicings calculated for frets 5-9 (3/4 waltz)"""
    return [
        ShellVoicing("Fmaj7", (5, 4, 3), (8, 7, 9), 1),
        ShellVoicing("Ebmaj7", (5, 4, 3), (6, 5, 7), 2),
        ShellVoicing("Dbmaj7", (4, 3, 2), (5, 6, 9), 3),
        ShellVoicing("Bmaj7", (5, 4, 3), (6, 8, 8), 4),
        ShellVoicing("Bbm9", (4, 3, 2), (8, 6, 9), 5),
        ShellVoicing("Abmaj7", (4, 3, 2), (6, 5, 8), 6),
        ShellVoicing("Gbmaj7", (5, 4, 3), (8, 8, 6), 7),
        ShellVoicing("Emaj7", (5, 4, 3), (7, 6, 8), 8),
        ShellVoicing("Fmaj7", (5, 4, 3), (8, 7, 9), 9),
        ShellVoicing("Dbmaj7", (4, 3, 2), (5, 6, 9), 10),
        ShellVoicing("Amaj7", (5, 4, 3), (5, 6, 6), 11),
        ShellVoicing("Gmaj7", (4, 3, 2), (5, 4, 7), 12),
        ShellVoicing("Fmaj7", (5, 4, 3), (8, 7, 9), 13),
        ShellVoicing("Ebm9", (4, 3, 2), (6, 4, 9), 14),
        ShellVoicing("Dbmaj7", (4, 3, 2), (5, 6, 9), 15),
        ShellVoicing("Fmaj7", (5, 4, 3), (8, 7, 9), 16),
    ]


def generate_musicxml_file(
    title: str,
    composer: str,
    voicings: List[ShellVoicing],
    key_fifths: int,
    time_num: int,
    time_denom: int,
    section_markers: dict,
    output_path: Path
) -> None:
    """Generate MusicXML file with single guitar staff (notation + TAB combined)."""
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    
    # Group voicings by bar
    bars = {}
    for v in voicings:
        if v.bar_number not in bars:
            bars[v.bar_number] = []
        bars[v.bar_number].append(v)
    
    # Create score
    score = ET.Element("score-partwise", version="4.0")
    
    # Work info
    work = ET.SubElement(score, "work")
    ET.SubElement(work, "work-title").text = title
    
    ident = ET.SubElement(score, "identification")
    creator = ET.SubElement(ident, "creator", type="composer")
    creator.text = composer
    
    # Part list - single guitar part with 2 staves
    part_list = ET.SubElement(score, "part-list")
    
    sp1 = ET.SubElement(part_list, "score-part", id="P1")
    ET.SubElement(sp1, "part-name").text = "Guitar"
    
    divisions = 4  # Divisions per quarter note
    
    # Helper to convert pitch to MusicXML
    def midi_to_xml_pitch(midi_pitch):
        STEP_MAP = ["C", "C", "D", "E", "E", "F", "F", "G", "G", "A", "B", "B"]
        ALTER_MAP = [0, 1, 0, -1, 0, 0, 1, 0, 1, 0, -1, 0]
        octave = (midi_pitch // 12) - 1
        pc = midi_pitch % 12
        return STEP_MAP[pc], ALTER_MAP[pc], octave
    
    # Create guitar part with 2 staves
    guitar_part = ET.SubElement(score, "part", id="P1")
    
    for bar_num in sorted(bars.keys()):
        measure = ET.SubElement(guitar_part, "measure", number=str(bar_num))
        
        # First measure attributes
        if bar_num == 1:
            attr = ET.SubElement(measure, "attributes")
            ET.SubElement(attr, "divisions").text = str(divisions)
            key = ET.SubElement(attr, "key")
            ET.SubElement(key, "fifths").text = str(key_fifths)
            time = ET.SubElement(attr, "time")
            ET.SubElement(time, "beats").text = str(time_num)
            ET.SubElement(time, "beat-type").text = str(time_denom)
            ET.SubElement(attr, "staves").text = "2"
            
            # Staff 1: Standard notation
            clef1 = ET.SubElement(attr, "clef", number="1")
            ET.SubElement(clef1, "sign").text = "G"
            ET.SubElement(clef1, "line").text = "2"
            ET.SubElement(clef1, "clef-octave-change").text = "-1"
            
            # Staff 2: TAB
            clef2 = ET.SubElement(attr, "clef", number="2")
            ET.SubElement(clef2, "sign").text = "TAB"
            ET.SubElement(clef2, "line").text = "5"
            
            # Staff details for TAB (staff 2)
            staff_details = ET.SubElement(attr, "staff-details", number="2")
            ET.SubElement(staff_details, "staff-lines").text = "6"
            # Tuning: strings 1-6 from high to low (E4, B3, G3, D3, A2, E2)
            tuning_data = [(1, 64), (2, 59), (3, 55), (4, 50), (5, 45), (6, 40)]
            for string_num, tuning_pitch in tuning_data:
                tuning = ET.SubElement(staff_details, "staff-tuning", line=str(string_num))
                step, alt, octave = midi_to_xml_pitch(tuning_pitch)
                ET.SubElement(tuning, "tuning-step").text = step
                if alt != 0:
                    ET.SubElement(tuning, "tuning-alter").text = str(alt)
                ET.SubElement(tuning, "tuning-octave").text = str(octave)
        
        # Section marker
        if bar_num in section_markers:
            direction = ET.SubElement(measure, "direction", placement="above")
            dt = ET.SubElement(direction, "direction-type")
            ET.SubElement(dt, "rehearsal", enclosure="rectangle").text = section_markers[bar_num]
            ET.SubElement(direction, "staff").text = "1"
        
        # Add chord symbol and notes for this bar
        for v in bars[bar_num]:
            # Chord symbol
            harmony = ET.SubElement(measure, "harmony")
            root_elem = ET.SubElement(harmony, "root")
            
            chord = v.chord_name.replace("#11", "").replace("#5", "").replace("/A", "")
            if len(chord) > 1 and chord[1] in 'b#':
                root_name = chord[0]
                alter = 1 if chord[1] == '#' else -1
                quality = chord[2:]
            else:
                root_name = chord[0]
                alter = 0
                quality = chord[1:]
            
            ET.SubElement(root_elem, "root-step").text = root_name
            if alter != 0:
                ET.SubElement(root_elem, "root-alter").text = str(alter)
            
            # Chord kind
            if 'maj7' in quality or 'maj9' in quality:
                kind = "major-seventh"
            elif 'm7' in quality or 'm9' in quality or 'm11' in quality:
                kind = "minor-seventh"
            elif quality == 'm':
                kind = "minor"
            elif 'sus4' in quality:
                kind = "suspended-fourth"
            elif '7' in quality:
                kind = "dominant"
            else:
                kind = "major-seventh"
            ET.SubElement(harmony, "kind").text = kind
            
            # Calculate duration
            dur_map = {"1": divisions * 4, "2": divisions * 2, "4": divisions}
            duration = dur_map.get(v.duration, divisions * 4)
            
            # Notes in the chord - sorted by pitch
            midi_notes = []
            for string, fret in zip(v.strings, v.frets):
                midi = string_fret_to_midi(string, fret)
                midi_notes.append((midi, string, fret))
            midi_notes.sort(key=lambda x: x[0])
            
            # Write notes for Staff 1 (notation)
            for i, (midi, string, fret) in enumerate(midi_notes):
                note_elem = ET.SubElement(measure, "note")
                if i > 0:
                    ET.SubElement(note_elem, "chord")
                
                pitch = ET.SubElement(note_elem, "pitch")
                step, alt, octave = midi_to_xml_pitch(midi)
                ET.SubElement(pitch, "step").text = step
                if alt != 0:
                    ET.SubElement(pitch, "alter").text = str(alt)
                ET.SubElement(pitch, "octave").text = str(octave)
                
                ET.SubElement(note_elem, "duration").text = str(duration)
                
                if v.duration == "1":
                    ET.SubElement(note_elem, "type").text = "whole"
                elif v.duration == "2":
                    ET.SubElement(note_elem, "type").text = "half"
                else:
                    ET.SubElement(note_elem, "type").text = "quarter"
                
                ET.SubElement(note_elem, "staff").text = "1"
                
                # Add technical notation with string/fret for proper TAB
                notations = ET.SubElement(note_elem, "notations")
                technical = ET.SubElement(notations, "technical")
                ET.SubElement(technical, "string").text = str(string)
                ET.SubElement(technical, "fret").text = str(fret)
            
            # Write backup to go back to start of measure for staff 2
            backup = ET.SubElement(measure, "backup")
            ET.SubElement(backup, "duration").text = str(duration)
            
            # Write notes for Staff 2 (TAB) with explicit string/fret
            for i, (midi, string, fret) in enumerate(midi_notes):
                note_elem = ET.SubElement(measure, "note")
                if i > 0:
                    ET.SubElement(note_elem, "chord")
                
                pitch = ET.SubElement(note_elem, "pitch")
                step, alt, octave = midi_to_xml_pitch(midi)
                ET.SubElement(pitch, "step").text = step
                if alt != 0:
                    ET.SubElement(pitch, "alter").text = str(alt)
                ET.SubElement(pitch, "octave").text = str(octave)
                
                ET.SubElement(note_elem, "duration").text = str(duration)
                
                if v.duration == "1":
                    ET.SubElement(note_elem, "type").text = "whole"
                elif v.duration == "2":
                    ET.SubElement(note_elem, "type").text = "half"
                else:
                    ET.SubElement(note_elem, "type").text = "quarter"
                
                ET.SubElement(note_elem, "staff").text = "2"
                
                # Explicit TAB notation
                notations = ET.SubElement(note_elem, "notations")
                technical = ET.SubElement(notations, "technical")
                ET.SubElement(technical, "string").text = str(string)
                ET.SubElement(technical, "fret").text = str(fret)
    
    # Write to file
    rough = ET.tostring(score, encoding="unicode")
    dom = minidom.parseString(rough)
    pretty = dom.toprettyxml(indent="  ")
    
    # Add DOCTYPE
    lines = pretty.split('\n')
    lines.insert(1, '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">')
    
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Generated: {output_path}")


def main():
    """Generate all three shell voicing map files."""
    output_dir = Path(__file__).parent.parent / "Trio Tunes" / "Alternative_LeadSheets"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    songs = [
        {
            "title": "The Mirror 5X - Shell Voicing Map",
            "composer": "Mike Bryant",
            "voicings": get_the_mirror_voicings(),
            "key_lily": "aes \\major",
            "key_fifths": -4,  # Ab major
            "time_signature": "4/4",
            "time_num": 4,
            "time_denom": 4,
            "section_markers": {1: "A", 9: "B", 13: "A'"},
            "base_name": "The_Mirror_Level2_ShellVoicingMap"
        },
        {
            "title": "Crystal Silence - Shell Voicing Map",
            "composer": "Mike Bryant",
            "voicings": get_crystal_silence_voicings(),
            "key_lily": "a \\major",
            "key_fifths": 3,  # A major
            "time_signature": "4/4",
            "time_num": 4,
            "time_denom": 4,
            "section_markers": {1: "A", 9: "B", 13: "A'"},
            "base_name": "Crystal_Silence_Level2_ShellVoicingMap"
        },
        {
            "title": "Orbit - Shell Voicing Map",
            "composer": "Mike Bryant",
            "voicings": get_orbit_voicings(),
            "key_lily": "f \\major",
            "key_fifths": -1,  # F major
            "time_signature": "3/4",
            "time_num": 3,
            "time_denom": 4,
            "section_markers": {1: "A", 9: "B", 13: "A'"},
            "base_name": "Orbit_Level2_ShellVoicingMap"
        }
    ]
    
    for song in songs:
        # Generate LilyPond file
        generate_lilypond_file(
            title=song["title"],
            composer=song["composer"],
            voicings=song["voicings"],
            key_signature=song["key_lily"],
            time_signature=song["time_signature"],
            section_markers=song["section_markers"],
            output_path=output_dir / f"{song['base_name']}.ly"
        )
        
        # Generate MusicXML file
        generate_musicxml_file(
            title=song["title"],
            composer=song["composer"],
            voicings=song["voicings"],
            key_fifths=song["key_fifths"],
            time_num=song["time_num"],
            time_denom=song["time_denom"],
            section_markers=song["section_markers"],
            output_path=output_dir / f"{song['base_name']}.musicxml"
        )
    
    print("\n" + "="*60)
    print("Files generated successfully!")
    print("="*60)
    print("\nLilyPond files (.ly):")
    print("  To convert to PNG: lilypond --png -dresolution=300 <filename>.ly")
    print("  Or use: https://www.hacklily.org/")
    print("\nMusicXML files (.musicxml):")
    print("  Open in MuseScore (free): https://musescore.org/")
    print("  File > Export > PNG")


if __name__ == "__main__":
    main()


