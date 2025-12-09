"""
Harmolodic Sketch - Bill Frisell Style (V3 - PROPERLY FIXED)
=============================================================

FIXES:
1. Chord-writing bug FIXED - all chord tones now written correctly
2. More melodic interest with actual movement
3. REAL triads that actually stack in notation
4. REAL chord melody voicings
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, 
    "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

MIDI_TO_NOTE = {
    0: ("C", 0), 1: ("C", 1), 2: ("D", 0), 3: ("E", -1),
    4: ("E", 0), 5: ("F", 0), 6: ("F", 1), 7: ("G", 0),
    8: ("G", 1), 9: ("A", 0), 10: ("B", -1), 11: ("B", 0)
}

WHOLE = 64
DOTTED_HALF = 48
HALF = 32
DOTTED_QUARTER = 24
QUARTER = 16
DOTTED_EIGHTH = 12
EIGHTH = 8
SIXTEENTH = 4
BAR = 64


@dataclass
class Note:
    pitch: int
    duration: int
    is_rest: bool = False
    
    def get_step_octave_alter(self) -> Tuple[str, int, int]:
        if self.is_rest:
            return ("C", 4, 0)
        octave = (self.pitch // 12) - 1
        pc = self.pitch % 12
        step, alter = MIDI_TO_NOTE[pc]
        return (step, octave, alter)


@dataclass
class ChordVoicing:
    """A chord = multiple notes played simultaneously."""
    pitches: List[int]  # All pitches in the chord (highest first = melody)
    duration: int


@dataclass 
class Chord:
    root: str
    quality: str
    
    def to_musicxml_harmony(self) -> Tuple[str, str]:
        kind_map = {
            "maj7": "major-seventh", "maj9": "major-ninth", "6": "major-sixth",
            "": "major", "7": "dominant", "m7": "minor-seventh", "m": "minor",
            "sus4": "suspended-fourth", "dim": "diminished",
        }
        return (self.root, kind_map.get(self.quality, "major"))


class HarmolodicSketchV3:
    
    def __init__(self):
        self.title = "Harmolodic Sketch"
        self.composer = "GCE (Frisell Style)"
        self.tempo = 88
        self.divisions = 16
        self.key_fifths = 1
        
    def p(self, note: str, octave: int) -> int:
        return NOTE_TO_MIDI[note] + (octave + 1) * 12
    
    def note(self, n: str, o: int, dur: int) -> Note:
        return Note(self.p(n, o), dur)
    
    def rest(self, dur: int) -> Note:
        return Note(0, dur, is_rest=True)
    
    def chord(self, notes: List[Tuple[str, int]], dur: int) -> ChordVoicing:
        """Create chord voicing. Notes listed high to low (melody first)."""
        pitches = [self.p(n, o) for n, o in notes]
        return ChordVoicing(pitches, dur)
    
    # =========================================================================
    # INTRO - Actual melodic content!
    # =========================================================================
    
    def intro_guitar(self) -> List:
        """Returns mix of Notes and ChordVoicings."""
        items = []
        
        # Bar 1: Gmaj7 - Rising phrase
        items.append(self.note("D", 4, EIGHTH))
        items.append(self.note("E", 4, EIGHTH))
        items.append(self.note("G", 4, EIGHTH))
        items.append(self.note("A", 4, EIGHTH))
        items.append(self.note("B", 4, QUARTER))
        items.append(self.note("D", 5, QUARTER))
        
        # Bar 2: Continue rising, then fall
        items.append(self.note("E", 5, DOTTED_QUARTER))
        items.append(self.note("D", 5, EIGHTH))
        items.append(self.note("B", 4, QUARTER))
        items.append(self.note("G", 4, QUARTER))
        
        # Bar 3: Cmaj9 - Gentle answer
        items.append(self.note("E", 5, QUARTER))
        items.append(self.note("D", 5, QUARTER))
        items.append(self.note("C", 5, QUARTER))
        items.append(self.note("B", 4, QUARTER))
        
        # Bar 4: D7sus4 - Tension
        items.append(self.note("A", 4, QUARTER))
        items.append(self.note("G", 4, EIGHTH))
        items.append(self.note("A", 4, EIGHTH))
        items.append(self.note("D", 5, HALF))
        
        # Bar 5: Em7 - Minor color
        items.append(self.note("E", 4, EIGHTH))
        items.append(self.note("G", 4, EIGHTH))
        items.append(self.note("B", 4, QUARTER))
        items.append(self.note("D", 5, QUARTER))
        items.append(self.note("E", 5, QUARTER))
        
        # Bar 6: Am9 - Deepening
        items.append(self.note("C", 5, QUARTER))
        items.append(self.note("B", 4, EIGHTH))
        items.append(self.note("A", 4, EIGHTH))
        items.append(self.note("G", 4, QUARTER))
        items.append(self.note("E", 4, QUARTER))
        
        # Bar 7: D9 - Anticipation
        items.append(self.note("F#", 4, QUARTER))
        items.append(self.note("A", 4, QUARTER))
        items.append(self.note("D", 5, QUARTER))
        items.append(self.note("E", 5, QUARTER))
        
        # Bar 8: Gmaj7 - Home
        items.append(self.note("D", 5, QUARTER))
        items.append(self.note("B", 4, QUARTER))
        items.append(self.note("G", 4, HALF))
        
        return items
    
    def intro_bass(self) -> List[Note]:
        notes = []
        # Bar 1
        notes.extend([self.note("G", 2, HALF), self.note("D", 3, HALF)])
        # Bar 2
        notes.extend([self.note("G", 2, HALF), self.note("F#", 2, HALF)])
        # Bar 3
        notes.extend([self.note("C", 2, HALF), self.note("E", 2, HALF)])
        # Bar 4
        notes.extend([self.note("D", 2, WHOLE)])
        # Bar 5
        notes.extend([self.note("E", 2, HALF), self.note("G", 2, HALF)])
        # Bar 6
        notes.extend([self.note("A", 2, HALF), self.note("G", 2, HALF)])
        # Bar 7
        notes.extend([self.note("D", 2, HALF), self.note("C", 2, HALF)])
        # Bar 8
        notes.extend([self.note("G", 2, WHOLE)])
        return notes
    
    def intro_chords(self) -> List[Chord]:
        return [
            Chord("G", "maj7"), Chord("G", "maj7"),
            Chord("C", "maj9"), Chord("D", "7sus4"),
            Chord("E", "m7"), Chord("A", "m7"),
            Chord("D", "7"), Chord("G", "maj7"),
        ]
    
    # =========================================================================
    # OPEN TRIAD SOLO - REAL TRIADS!
    # =========================================================================
    
    def triad_solo_guitar(self) -> List:
        items = []
        
        # Bar 1: G major triad -> A minor triad (both as REAL chords)
        items.append(self.chord([("B", 4), ("G", 4), ("D", 4)], HALF))  # G triad
        items.append(self.chord([("C", 5), ("A", 4), ("E", 4)], HALF))  # Am triad
        
        # Bar 2: Continue with triads
        items.append(self.chord([("D", 5), ("B", 4), ("G", 4)], HALF))  # G high
        items.append(self.chord([("E", 5), ("C", 5), ("A", 4)], HALF))  # Am high
        
        # Bar 3: C major -> D major
        items.append(self.chord([("E", 5), ("C", 5), ("G", 4)], HALF))  # C triad
        items.append(self.chord([("F#", 5), ("D", 5), ("A", 4)], HALF))  # D triad
        
        # Bar 4: G resolution
        items.append(self.chord([("G", 5), ("D", 5), ("B", 4)], WHOLE))  # G spread
        
        # Bar 5: Em -> F#dim
        items.append(self.chord([("G", 5), ("E", 5), ("B", 4)], HALF))  # Em
        items.append(self.chord([("A", 5), ("F#", 5), ("C", 5)], HALF))  # F#dim
        
        # Bar 6: Am -> Bm
        items.append(self.chord([("E", 5), ("C", 5), ("A", 4)], HALF))  # Am
        items.append(self.chord([("F#", 5), ("D", 5), ("B", 4)], HALF))  # Bm
        
        # Bar 7: D spread
        items.append(self.chord([("A", 5), ("F#", 5), ("D", 5)], DOTTED_HALF))
        items.append(self.note("D", 5, QUARTER))
        
        # Bar 8: G final
        items.append(self.chord([("B", 5), ("G", 5), ("D", 5)], WHOLE))
        
        return items
    
    def triad_solo_bass(self) -> List[Note]:
        notes = []
        notes.extend([self.note("G", 2, HALF), self.note("A", 2, HALF)])
        notes.extend([self.note("G", 2, HALF), self.note("A", 2, HALF)])
        notes.extend([self.note("C", 2, HALF), self.note("D", 2, HALF)])
        notes.extend([self.note("G", 2, WHOLE)])
        notes.extend([self.note("E", 2, HALF), self.note("F#", 2, HALF)])
        notes.extend([self.note("A", 2, HALF), self.note("B", 2, HALF)])
        notes.extend([self.note("D", 2, WHOLE)])
        notes.extend([self.note("G", 2, WHOLE)])
        return notes
    
    def triad_solo_chords(self) -> List[Chord]:
        return [
            Chord("G", ""), Chord("G", ""),
            Chord("C", ""), Chord("G", ""),
            Chord("E", "m"), Chord("A", "m"),
            Chord("D", ""), Chord("G", ""),
        ]
    
    # =========================================================================
    # CHORD MELODY - REAL 4-VOICE VOICINGS!
    # =========================================================================
    
    def chord_melody_guitar(self) -> List:
        items = []
        
        # Bar 1: Gmaj9 voicings
        items.append(self.chord([("A", 5), ("D", 5), ("B", 4), ("G", 4)], HALF))
        items.append(self.chord([("G", 5), ("D", 5), ("B", 4), ("G", 4)], HALF))
        
        # Bar 2: Em9
        items.append(self.chord([("F#", 5), ("D", 5), ("B", 4), ("E", 4)], HALF))
        items.append(self.chord([("E", 5), ("D", 5), ("B", 4), ("G", 4)], HALF))
        
        # Bar 3: Cmaj7 -> Cm6 (borrowed!)
        items.append(self.chord([("B", 5), ("G", 5), ("E", 5), ("C", 5)], HALF))
        items.append(self.chord([("A", 5), ("G", 5), ("Eb", 5), ("C", 5)], HALF))  # Cm6!
        
        # Bar 4: Dsus4 -> D
        items.append(self.chord([("G", 5), ("D", 5), ("A", 4), ("D", 4)], HALF))
        items.append(self.chord([("F#", 5), ("D", 5), ("A", 4), ("D", 4)], HALF))
        
        # Bar 5: Bm7
        items.append(self.chord([("A", 5), ("F#", 5), ("D", 5), ("B", 4)], HALF))
        items.append(self.chord([("F#", 5), ("D", 5), ("B", 4), ("F#", 4)], HALF))
        
        # Bar 6: Em7 -> Am9
        items.append(self.chord([("D", 5), ("B", 4), ("G", 4), ("E", 4)], HALF))
        items.append(self.chord([("B", 5), ("E", 5), ("C", 5), ("A", 4)], HALF))
        
        # Bar 7: D7sus4
        items.append(self.chord([("C", 5), ("A", 4), ("G", 4), ("D", 4)], HALF))
        items.append(self.chord([("D", 5), ("A", 4), ("G", 4), ("D", 4)], HALF))
        
        # Bar 8: Gmaj7 final
        items.append(self.chord([("F#", 5), ("D", 5), ("B", 4), ("G", 4)], QUARTER))
        items.append(self.chord([("G", 5), ("D", 5), ("B", 4), ("G", 4)], DOTTED_HALF))
        
        return items
    
    def chord_melody_bass(self) -> List[Note]:
        notes = []
        notes.extend([self.note("G", 2, WHOLE)])
        notes.extend([self.note("E", 2, WHOLE)])
        notes.extend([self.note("C", 2, HALF), self.note("C", 2, HALF)])
        notes.extend([self.note("D", 2, WHOLE)])
        notes.extend([self.note("B", 1, WHOLE)])
        notes.extend([self.note("E", 2, HALF), self.note("A", 2, HALF)])
        notes.extend([self.note("D", 2, WHOLE)])
        notes.extend([self.note("G", 2, WHOLE)])
        return notes
    
    def chord_melody_chords(self) -> List[Chord]:
        return [
            Chord("G", "maj9"), Chord("E", "m7"),
            Chord("C", "maj7"), Chord("D", "sus4"),
            Chord("B", "m7"), Chord("A", "m7"),
            Chord("D", "7"), Chord("G", "maj7"),
        ]
    
    # =========================================================================
    # OUTRO - Melody variation
    # =========================================================================
    
    def outro_guitar(self) -> List:
        items = []
        
        # Bar 1: Higher version of theme
        items.append(self.note("G", 5, EIGHTH))
        items.append(self.note("A", 5, EIGHTH))
        items.append(self.note("B", 5, QUARTER))
        items.append(self.note("D", 6, HALF))
        
        # Bar 2: Descending
        items.append(self.note("E", 6, QUARTER))
        items.append(self.note("D", 6, EIGHTH))
        items.append(self.note("B", 5, EIGHTH))
        items.append(self.note("A", 5, QUARTER))
        items.append(self.note("G", 5, QUARTER))
        
        # Bar 3: C color
        items.append(self.note("E", 5, QUARTER))
        items.append(self.note("D", 5, QUARTER))
        items.append(self.note("C", 5, HALF))
        
        # Bar 4: D suspended
        items.append(self.note("A", 4, HALF))
        items.append(self.note("D", 5, HALF))
        
        # Bar 5: Em
        items.append(self.note("E", 4, QUARTER))
        items.append(self.note("G", 4, QUARTER))
        items.append(self.note("B", 4, QUARTER))
        items.append(self.note("E", 5, QUARTER))
        
        # Bar 6: Am resolution
        items.append(self.note("C", 5, QUARTER))
        items.append(self.note("B", 4, QUARTER))
        items.append(self.note("A", 4, HALF))
        
        # Bar 7: D to G
        items.append(self.note("D", 5, QUARTER))
        items.append(self.note("B", 4, QUARTER))
        items.append(self.note("A", 4, QUARTER))
        items.append(self.note("G", 4, QUARTER))
        
        # Bar 8: Final G chord
        items.append(self.chord([("G", 5), ("D", 5), ("B", 4), ("G", 4)], WHOLE))
        
        return items
    
    def outro_bass(self) -> List[Note]:
        notes = []
        notes.extend([self.note("G", 2, WHOLE)])
        notes.extend([self.note("G", 2, HALF), self.note("F#", 2, HALF)])
        notes.extend([self.note("C", 2, WHOLE)])
        notes.extend([self.note("D", 2, WHOLE)])
        notes.extend([self.note("E", 2, WHOLE)])
        notes.extend([self.note("A", 2, WHOLE)])
        notes.extend([self.note("D", 2, HALF), self.note("G", 2, HALF)])
        notes.extend([self.note("G", 1, WHOLE)])
        return notes
    
    def outro_chords(self) -> List[Chord]:
        return [
            Chord("G", "maj7"), Chord("G", ""),
            Chord("C", "maj7"), Chord("D", "sus4"),
            Chord("E", "m7"), Chord("A", "m7"),
            Chord("D", ""), Chord("G", ""),
        ]
    
    # =========================================================================
    # MusicXML Export - FIXED chord writing!
    # =========================================================================
    
    def create_musicxml(self) -> str:
        score = ET.Element("score-partwise", version="4.0")
        
        work = ET.SubElement(score, "work")
        ET.SubElement(work, "work-title").text = self.title
        
        ident = ET.SubElement(score, "identification")
        creator = ET.SubElement(ident, "creator", type="composer")
        creator.text = self.composer
        
        part_list = ET.SubElement(score, "part-list")
        ET.SubElement(ET.SubElement(part_list, "score-part", id="P1"), "part-name").text = "Guitar"
        ET.SubElement(ET.SubElement(part_list, "score-part", id="P2"), "part-name").text = "Bass"
        
        # Collect sections
        sections = [
            ("1 - Intro", self.intro_guitar(), self.intro_bass(), self.intro_chords()),
            ("2 - Open Triad Solo", self.triad_solo_guitar(), self.triad_solo_bass(), self.triad_solo_chords()),
            ("3 - Chord Melody", self.chord_melody_guitar(), self.chord_melody_bass(), self.chord_melody_chords()),
            ("4 - Outro", self.outro_guitar(), self.outro_bass(), self.outro_chords()),
        ]
        
        all_guitar = []
        all_bass = []
        all_chords = []
        markers = []
        
        bar_count = 0
        for name, gtr, bass, chds in sections:
            markers.append((bar_count, name))
            all_guitar.extend(gtr)
            all_bass.extend(bass)
            all_chords.extend(chds)
            bar_count += 8
        
        guitar = ET.SubElement(score, "part", id="P1")
        self._write_guitar_part(guitar, all_guitar, all_chords, markers)
        
        bass_part = ET.SubElement(score, "part", id="P2")
        self._write_bass_part(bass_part, all_bass)
        
        rough = ET.tostring(score, encoding="unicode")
        return minidom.parseString(rough).toprettyxml(indent="  ")
    
    def _write_guitar_part(self, part_elem, items, chords, markers):
        """Write guitar part with proper chord handling."""
        marker_dict = {m: name for m, name in markers}
        
        measure_num = 1
        item_idx = 0
        chord_idx = 0
        
        while item_idx < len(items):
            measure = ET.SubElement(part_elem, "measure", number=str(measure_num))
            
            # First measure setup
            if measure_num == 1:
                attr = ET.SubElement(measure, "attributes")
                ET.SubElement(attr, "divisions").text = str(self.divisions)
                key = ET.SubElement(attr, "key")
                ET.SubElement(key, "fifths").text = str(self.key_fifths)
                ET.SubElement(key, "mode").text = "major"
                time = ET.SubElement(attr, "time")
                ET.SubElement(time, "beats").text = "4"
                ET.SubElement(time, "beat-type").text = "4"
                clef = ET.SubElement(attr, "clef")
                ET.SubElement(clef, "sign").text = "G"
                ET.SubElement(clef, "line").text = "2"
                
                direction = ET.SubElement(measure, "direction", placement="above")
                dt = ET.SubElement(direction, "direction-type")
                met = ET.SubElement(dt, "metronome")
                ET.SubElement(met, "beat-unit").text = "quarter"
                ET.SubElement(met, "per-minute").text = str(self.tempo)
            
            # Section marker
            if (measure_num - 1) in marker_dict:
                direction = ET.SubElement(measure, "direction", placement="above")
                dt = ET.SubElement(direction, "direction-type")
                ET.SubElement(dt, "rehearsal").text = marker_dict[measure_num - 1]
            
            # Chord symbol
            if chord_idx < len(chords):
                c = chords[chord_idx]
                harmony = ET.SubElement(measure, "harmony")
                root = ET.SubElement(harmony, "root")
                if len(c.root) > 1 and c.root[1] in '#b':
                    ET.SubElement(root, "root-step").text = c.root[0]
                    ET.SubElement(root, "root-alter").text = "1" if c.root[1] == '#' else "-1"
                else:
                    ET.SubElement(root, "root-step").text = c.root
                _, kind = c.to_musicxml_harmony()
                ET.SubElement(harmony, "kind").text = kind
                chord_idx += 1
            
            # Write notes/chords for this measure
            dur_in_bar = 0
            while item_idx < len(items) and dur_in_bar < BAR:
                item = items[item_idx]
                
                if isinstance(item, ChordVoicing):
                    # Write ALL notes of the chord
                    for i, pitch in enumerate(item.pitches):
                        note_elem = ET.SubElement(measure, "note")
                        if i > 0:  # Not the first note = chord tone
                            ET.SubElement(note_elem, "chord")
                        
                        p = ET.SubElement(note_elem, "pitch")
                        step, octave, alter = self._pitch_to_xml(pitch)
                        ET.SubElement(p, "step").text = step
                        if alter != 0:
                            ET.SubElement(p, "alter").text = str(alter)
                        ET.SubElement(p, "octave").text = str(octave)
                        
                        ET.SubElement(note_elem, "duration").text = str(item.duration)
                        t, dot = self._dur_to_type(item.duration)
                        ET.SubElement(note_elem, "type").text = t
                        if dot:
                            ET.SubElement(note_elem, "dot")
                    
                    dur_in_bar += item.duration
                    item_idx += 1
                    
                elif isinstance(item, Note):
                    if item.is_rest:
                        note_elem = ET.SubElement(measure, "note")
                        ET.SubElement(note_elem, "rest")
                        ET.SubElement(note_elem, "duration").text = str(item.duration)
                        t, dot = self._dur_to_type(item.duration)
                        ET.SubElement(note_elem, "type").text = t
                        if dot:
                            ET.SubElement(note_elem, "dot")
                    else:
                        note_elem = ET.SubElement(measure, "note")
                        p = ET.SubElement(note_elem, "pitch")
                        step, octave, alter = self._pitch_to_xml(item.pitch)
                        ET.SubElement(p, "step").text = step
                        if alter != 0:
                            ET.SubElement(p, "alter").text = str(alter)
                        ET.SubElement(p, "octave").text = str(octave)
                        ET.SubElement(note_elem, "duration").text = str(item.duration)
                        t, dot = self._dur_to_type(item.duration)
                        ET.SubElement(note_elem, "type").text = t
                        if dot:
                            ET.SubElement(note_elem, "dot")
                    
                    dur_in_bar += item.duration
                    item_idx += 1
            
            measure_num += 1
    
    def _write_bass_part(self, part_elem, notes):
        """Write bass part."""
        measure_num = 1
        note_idx = 0
        
        while note_idx < len(notes):
            measure = ET.SubElement(part_elem, "measure", number=str(measure_num))
            
            if measure_num == 1:
                attr = ET.SubElement(measure, "attributes")
                ET.SubElement(attr, "divisions").text = str(self.divisions)
                key = ET.SubElement(attr, "key")
                ET.SubElement(key, "fifths").text = str(self.key_fifths)
                ET.SubElement(key, "mode").text = "major"
                time = ET.SubElement(attr, "time")
                ET.SubElement(time, "beats").text = "4"
                ET.SubElement(time, "beat-type").text = "4"
                clef = ET.SubElement(attr, "clef")
                ET.SubElement(clef, "sign").text = "F"
                ET.SubElement(clef, "line").text = "4"
            
            dur_in_bar = 0
            while note_idx < len(notes) and dur_in_bar < BAR:
                n = notes[note_idx]
                note_elem = ET.SubElement(measure, "note")
                
                if n.is_rest:
                    ET.SubElement(note_elem, "rest")
                else:
                    p = ET.SubElement(note_elem, "pitch")
                    step, octave, alter = self._pitch_to_xml(n.pitch)
                    ET.SubElement(p, "step").text = step
                    if alter != 0:
                        ET.SubElement(p, "alter").text = str(alter)
                    ET.SubElement(p, "octave").text = str(octave)
                
                ET.SubElement(note_elem, "duration").text = str(n.duration)
                t, dot = self._dur_to_type(n.duration)
                ET.SubElement(note_elem, "type").text = t
                if dot:
                    ET.SubElement(note_elem, "dot")
                
                dur_in_bar += n.duration
                note_idx += 1
            
            measure_num += 1
    
    def _pitch_to_xml(self, midi_pitch: int) -> Tuple[str, int, int]:
        octave = (midi_pitch // 12) - 1
        pc = midi_pitch % 12
        step, alter = MIDI_TO_NOTE[pc]
        return (step, octave, alter)
    
    def _dur_to_type(self, dur: int) -> Tuple[str, bool]:
        if dur == DOTTED_HALF:
            return ("half", True)
        if dur == DOTTED_QUARTER:
            return ("quarter", True)
        if dur == DOTTED_EIGHTH:
            return ("eighth", True)
        
        mapping = {
            WHOLE: "whole", HALF: "half", QUARTER: "quarter",
            EIGHTH: "eighth", SIXTEENTH: "16th"
        }
        return (mapping.get(dur, "quarter"), False)
    
    def save(self, path: str):
        xml = self.create_musicxml()
        lines = xml.split('\n')
        if lines[0].startswith('<?xml'):
            lines = lines[1:]
        
        content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        content += '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
        content += '"http://www.musicxml.org/dtds/partwise.dtd">\n'
        content += '\n'.join(lines)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path


def main():
    print("=" * 60)
    print("HARMOLODIC SKETCH v3.0 - PROPERLY FIXED!")
    print("=" * 60)
    
    out = Path(__file__).parent.parent / "Trio Tunes" / "Alternative_LeadSheets" / "Bill Frisell - Harmolodic Sketch"
    out.mkdir(parents=True, exist_ok=True)
    
    comp = HarmolodicSketchV3()
    path = out / "Harmolodic_Sketch.musicxml"
    comp.save(str(path))
    
    print(f"\nSaved: {path}")
    print("\nFIXES IN V3:")
    print("  ✓ Chord-writing bug FIXED")
    print("  ✓ REAL triads (3 notes stacked)")
    print("  ✓ REAL chord melody (4-voice voicings)")
    print("  ✓ More melodic content with movement")
    print("  ✓ Eighth note rhythms for interest")
    print("=" * 60)


if __name__ == "__main__":
    main()
