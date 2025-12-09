"""
Harmolodic Sketch x5 - Bill Frisell Style (5-STAR VERSION)
==========================================================

UPGRADES FOR 5-STAR:
- Distinctive Frisell melody: SPACE, unexpected intervals, folk-like simplicity
- Arpeggiated triad solo with rhythmic displacement
- More Americana flavor with major/minor ambiguity
- Silences and breathing room (Frisell signature)

Key: G Major (Americana)
Tempo: 88 BPM (slow, spacious)
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
    8: ("A", -1), 9: ("A", 0), 10: ("B", -1), 11: ("B", 0)
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
    
    def get_xml(self) -> Tuple[str, int, int]:
        if self.is_rest:
            return ("C", 4, 0)
        octave = (self.pitch // 12) - 1
        pc = self.pitch % 12
        step, alter = MIDI_TO_NOTE[pc]
        return (step, octave, alter)


@dataclass
class ChordVoicing:
    pitches: List[int]
    duration: int


@dataclass 
class Chord:
    root: str
    quality: str
    
    def to_kind(self) -> str:
        kinds = {
            "maj7": "major-seventh", "maj9": "major-ninth",
            "m7": "minor-seventh", "m9": "minor-ninth",
            "7": "dominant", "7sus4": "suspended-fourth",
            "m7b5": "half-diminished", "dim7": "diminished-seventh",
            "6": "major-sixth", "m6": "minor-sixth",
            "": "major", "m": "minor",
        }
        return kinds.get(self.quality, "major-seventh")


def verify(items, bar_num, section):
    total = sum(i.duration for i in items)
    ok = "✓" if total == BAR else "✗"
    print(f"  {ok} {section} Bar {bar_num}: {total}")
    return total == BAR


class HarmolodicSketchX5:
    """5-star Bill Frisell inspired composition."""
    
    def __init__(self):
        self.title = "Harmolodic Sketch x5"
        self.composer = "GCE (Bill Frisell Style)"
        self.tempo = 88
        self.divisions = 16
        self.key_fifths = 1  # G major
        
    def p(self, n, o):
        return NOTE_TO_MIDI[n] + (o + 1) * 12
    
    def n(self, note, oct, dur):
        return Note(self.p(note, oct), dur)
    
    def r(self, dur):
        return Note(0, dur, is_rest=True)
    
    def chord(self, notes, dur):
        return ChordVoicing([self.p(n, o) for n, o in notes], dur)
    
    # =========================================================================
    # INTRO: Frisell signature - SPACE, folk-like, unexpected turns
    # =========================================================================
    
    def intro_melody(self):
        items = []
        
        # Bar 1: Simple folk-like opening with SPACE
        # 32+8+8+16 = 64 ✓
        bar1 = [
            self.n("G", 4, HALF),        # Long G - SPACE
            self.n("B", 4, EIGHTH),      
            self.n("D", 5, EIGHTH),      
            self.n("E", 5, QUARTER),     # Unexpected 6th!
        ]
        verify(bar1, 1, "Intro")
        items.extend(bar1)
        
        # Bar 2: Bend-like phrase (Frisell loves bends)
        # 8+8+32+16 = 64 ✓
        bar2 = [
            self.n("D", 5, EIGHTH),      
            self.n("Eb", 5, EIGHTH),     # Blue note!
            self.n("D", 5, HALF),        # Long resolve
            self.n("B", 4, QUARTER),     
        ]
        verify(bar2, 2, "Intro")
        items.extend(bar2)
        
        # Bar 3: Cmaj7 - Wide leap then settle
        # 16+16+32 = 64 ✓
        bar3 = [
            self.n("E", 5, QUARTER),     # 3rd of C
            self.n("C", 4, QUARTER),     # Wide leap DOWN!
            self.n("G", 4, HALF),        # Settle on 5th
        ]
        verify(bar3, 3, "Intro")
        items.extend(bar3)
        
        # Bar 4: Breathing space
        # 16+16+32 = 64 ✓
        bar4 = [
            self.r(QUARTER),             # SILENCE (Frisell!)
            self.n("A", 4, QUARTER),     
            self.n("D", 5, HALF),        
        ]
        verify(bar4, 4, "Intro")
        items.extend(bar4)
        
        # Bar 5: Em - Plaintive minor color
        # 8+8+16+32 = 64 ✓
        bar5 = [
            self.n("E", 4, EIGHTH),      
            self.n("G", 4, EIGHTH),      
            self.n("B", 4, QUARTER),     
            self.n("E", 5, HALF),        # Hold - expressive
        ]
        verify(bar5, 5, "Intro")
        items.extend(bar5)
        
        # Bar 6: Am - Deeper, more space
        # 32+16+16 = 64 ✓
        bar6 = [
            self.n("C", 5, HALF),        # Long 3rd
            self.n("A", 4, QUARTER),     
            self.n("G", 4, QUARTER),     # Natural 7th descent
        ]
        verify(bar6, 6, "Intro")
        items.extend(bar6)
        
        # Bar 7: D7 - Anticipation with Frisell "wrong note"
        # 8+8+16+16+16 = 64 ✓
        bar7 = [
            self.n("F#", 4, EIGHTH),     
            self.n("A", 4, EIGHTH),      
            self.n("C", 5, QUARTER),     # b7
            self.n("Eb", 5, QUARTER),    # "Wrong" note! Tension
            self.n("D", 5, QUARTER),     # Resolve
        ]
        verify(bar7, 7, "Intro")
        items.extend(bar7)
        
        # Bar 8: G - Home with echo
        # 16+16+32 = 64 ✓
        bar8 = [
            self.n("D", 5, QUARTER),     
            self.n("B", 4, QUARTER),     
            self.n("G", 4, HALF),        # Home - rest
        ]
        verify(bar8, 8, "Intro")
        items.extend(bar8)
        
        return items
    
    def intro_bass(self):
        notes = []
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("G", 2, HALF), self.n("F#", 2, HALF)])
        notes.extend([self.n("C", 2, WHOLE)])
        notes.extend([self.n("D", 2, WHOLE)])
        notes.extend([self.n("E", 2, WHOLE)])
        notes.extend([self.n("A", 2, HALF), self.n("G", 2, HALF)])
        notes.extend([self.n("D", 2, WHOLE)])
        notes.extend([self.n("G", 2, WHOLE)])
        return notes
    
    def intro_chords(self):
        return [
            Chord("G", "maj7"), Chord("G", "maj7"),
            Chord("C", "maj7"), Chord("D", "7sus4"),
            Chord("E", "m7"), Chord("A", "m7"),
            Chord("D", "7"), Chord("G", "maj7"),
        ]
    
    # =========================================================================
    # TRIAD SOLO: Arpeggiated with Frisell's gentle syncopation
    # =========================================================================
    
    def triad_solo(self):
        items = []
        
        # Bar 1: G + Am arps with space
        # 8+8+8+8+8+8+16 = 64 ✓
        bar1 = [
            self.n("G", 4, EIGHTH),      # G arp
            self.n("B", 4, EIGHTH),      
            self.n("D", 5, EIGHTH),      
            self.r(EIGHTH),              # Breath!
            self.n("A", 4, EIGHTH),      # Am arp
            self.n("C", 5, EIGHTH),      
            self.n("E", 5, QUARTER),     # Land
        ]
        verify(bar1, 1, "TriadSolo")
        items.extend(bar1)
        
        # Bar 2: G + Am higher with pull
        # 8+8+8+8+8+8+8+8 = 64 ✓
        bar2 = [
            self.n("D", 5, EIGHTH),      # G arp high
            self.n("G", 5, EIGHTH),      
            self.n("B", 4, EIGHTH),      # Drop back down
            self.n("C", 5, EIGHTH),      # Am starts
            self.n("E", 5, EIGHTH),      
            self.n("A", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      
            self.n("E", 5, EIGHTH),      # Descending echo
        ]
        verify(bar2, 2, "TriadSolo")
        items.extend(bar2)
        
        # Bar 3: C + D with rhythmic push
        # 8+8+16+8+8+16 = 64 ✓
        bar3 = [
            self.n("C", 5, EIGHTH),      # C arp
            self.n("E", 5, EIGHTH),      
            self.n("G", 5, QUARTER),     # Hold
            self.n("D", 5, EIGHTH),      # D arp
            self.n("F#", 5, EIGHTH),     
            self.n("A", 5, QUARTER),     # Hold
        ]
        verify(bar3, 3, "TriadSolo")
        items.extend(bar3)
        
        # Bar 4: G resolution with space
        # 8+8+16+32 = 64 ✓
        bar4 = [
            self.n("G", 4, EIGHTH),      
            self.n("B", 4, EIGHTH),      
            self.n("D", 5, QUARTER),     
            self.n("G", 5, HALF),        # Soaring hold
        ]
        verify(bar4, 4, "TriadSolo")
        items.extend(bar4)
        
        # Bar 5: Em + F#dim (darker)
        # 8+8+8+8+8+8+16 = 64 ✓
        bar5 = [
            self.n("E", 4, EIGHTH),      # Em arp
            self.n("G", 4, EIGHTH),      
            self.n("B", 4, EIGHTH),      
            self.n("F#", 4, EIGHTH),     # F#dim arp
            self.n("A", 4, EIGHTH),      
            self.n("C", 5, EIGHTH),      
            self.n("B", 4, QUARTER),     # Resolve tension
        ]
        verify(bar5, 5, "TriadSolo")
        items.extend(bar5)
        
        # Bar 6: Am + Bm
        # 8+8+8+8+8+8+8+8 = 64 ✓
        bar6 = [
            self.n("A", 4, EIGHTH),      # Am arp
            self.n("C", 5, EIGHTH),      
            self.n("E", 5, EIGHTH),      
            self.n("D", 5, EIGHTH),      # Passing
            self.n("B", 4, EIGHTH),      # Bm arp
            self.n("D", 5, EIGHTH),      
            self.n("F#", 5, EIGHTH),     
            self.n("E", 5, EIGHTH),      # Echo
        ]
        verify(bar6, 6, "TriadSolo")
        items.extend(bar6)
        
        # Bar 7: D with sustain
        # 8+8+8+8+32 = 64 ✓
        bar7 = [
            self.n("D", 5, EIGHTH),      # D arp
            self.n("F#", 5, EIGHTH),     
            self.n("A", 5, EIGHTH),      
            self.n("D", 6, EIGHTH),      # High octave
            self.n("A", 5, HALF),        # Sustain
        ]
        verify(bar7, 7, "TriadSolo")
        items.extend(bar7)
        
        # Bar 8: G final - gentle landing
        # 8+8+8+8+32 = 64 ✓
        bar8 = [
            self.n("G", 4, EIGHTH),      
            self.n("D", 5, EIGHTH),      
            self.n("B", 4, EIGHTH),      
            self.n("G", 4, EIGHTH),      
            self.n("D", 5, HALF),        # Warm 5th
        ]
        verify(bar8, 8, "TriadSolo")
        items.extend(bar8)
        
        return items
    
    def triad_solo_bass(self):
        notes = []
        notes.extend([self.n("G", 2, HALF), self.n("A", 2, HALF)])
        notes.extend([self.n("G", 2, HALF), self.n("A", 2, HALF)])
        notes.extend([self.n("C", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("E", 2, HALF), self.n("F#", 2, HALF)])
        notes.extend([self.n("A", 2, HALF), self.n("B", 2, HALF)])
        notes.extend([self.n("D", 2, WHOLE)])
        notes.extend([self.n("G", 2, WHOLE)])
        return notes
    
    def triad_solo_chords(self):
        return [
            Chord("G", ""), Chord("G", ""),
            Chord("C", ""), Chord("G", ""),
            Chord("E", "m"), Chord("A", "m"),
            Chord("D", ""), Chord("G", ""),
        ]
    
    # =========================================================================
    # CHORD MELODY: Frisell's hybrid voicings with color
    # =========================================================================
    
    def chord_melody(self):
        items = []
        
        # Bar 1: Gmaj9 - open, spacious voicing
        bar1 = [
            self.chord([("A", 5), ("D", 5), ("B", 4), ("G", 4)], HALF),
            self.chord([("B", 5), ("D", 5), ("G", 4)], HALF),  # 3-note for variety
        ]
        verify(bar1, 1, "ChordMel")
        items.extend(bar1)
        
        # Bar 2: Em7 with melody motion
        bar2 = [
            self.chord([("D", 5), ("B", 4), ("G", 4), ("E", 4)], HALF),
            self.chord([("E", 5), ("B", 4), ("G", 4), ("E", 4)], HALF),
        ]
        verify(bar2, 2, "ChordMel")
        items.extend(bar2)
        
        # Bar 3: Cmaj7 - open string feel
        bar3 = [
            self.chord([("D", 5), ("G", 4), ("E", 4), ("C", 4)], HALF),
            self.chord([("E", 5), ("G", 4), ("C", 5), ("C", 4)], HALF),
        ]
        verify(bar3, 3, "ChordMel")
        items.extend(bar3)
        
        # Bar 4: Am7add13
        bar4 = [
            self.chord([("F#", 5), ("E", 5), ("C", 5), ("A", 4)], WHOLE),
        ]
        verify(bar4, 4, "ChordMel")
        items.extend(bar4)
        
        # Bar 5: D9 - dominant color
        bar5 = [
            self.chord([("E", 5), ("C", 5), ("A", 4), ("D", 4)], HALF),
            self.chord([("F#", 5), ("C", 5), ("A", 4), ("D", 4)], HALF),
        ]
        verify(bar5, 5, "ChordMel")
        items.extend(bar5)
        
        # Bar 6: Bm7 -> Em
        bar6 = [
            self.chord([("A", 5), ("F#", 5), ("D", 5), ("B", 4)], HALF),
            self.chord([("G", 5), ("E", 5), ("B", 4), ("E", 4)], HALF),
        ]
        verify(bar6, 6, "ChordMel")
        items.extend(bar6)
        
        # Bar 7: Am7 -> D7
        bar7 = [
            self.chord([("G", 5), ("E", 5), ("C", 5), ("A", 4)], HALF),
            self.chord([("F#", 5), ("C", 5), ("A", 4), ("D", 4)], HALF),
        ]
        verify(bar7, 7, "ChordMel")
        items.extend(bar7)
        
        # Bar 8: Gmaj7 final
        bar8 = [
            self.chord([("A", 5), ("D", 5), ("B", 4), ("G", 4)], WHOLE),
        ]
        verify(bar8, 8, "ChordMel")
        items.extend(bar8)
        
        return items
    
    def chord_melody_bass(self):
        notes = []
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("E", 2, WHOLE)])
        notes.extend([self.n("C", 2, WHOLE)])
        notes.extend([self.n("A", 2, WHOLE)])
        notes.extend([self.n("D", 2, WHOLE)])
        notes.extend([self.n("B", 2, HALF), self.n("E", 2, HALF)])
        notes.extend([self.n("A", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("G", 2, WHOLE)])
        return notes
    
    def chord_melody_chords(self):
        return [
            Chord("G", "maj7"), Chord("E", "m7"),
            Chord("C", "maj7"), Chord("A", "m7"),
            Chord("D", "7"), Chord("B", "m7"),
            Chord("A", "m7"), Chord("G", "maj7"),
        ]
    
    # =========================================================================
    # OUTRO: Melody variation - higher, more resolved
    # =========================================================================
    
    def outro_melody(self):
        items = []
        
        # Bar 1: Higher restatement
        bar1 = [
            self.n("G", 5, HALF),        # High G
            self.n("B", 5, EIGHTH),      
            self.n("D", 6, EIGHTH),      # Soaring
            self.n("E", 6, QUARTER),     
        ]
        verify(bar1, 1, "Outro")
        items.extend(bar1)
        
        # Bar 2: Gentle descent
        bar2 = [
            self.n("D", 6, DOTTED_QUARTER),
            self.n("B", 5, EIGHTH),      
            self.n("G", 5, HALF),        
        ]
        verify(bar2, 2, "Outro")
        items.extend(bar2)
        
        # Bar 3: C color
        bar3 = [
            self.n("E", 5, QUARTER),     
            self.n("C", 5, QUARTER),     
            self.r(QUARTER),             # Space!
            self.n("G", 4, QUARTER),     
        ]
        verify(bar3, 3, "Outro")
        items.extend(bar3)
        
        # Bar 4: D tension
        bar4 = [
            self.n("A", 4, QUARTER),     
            self.n("D", 5, HALF),        
            self.n("F#", 5, QUARTER),    
        ]
        verify(bar4, 4, "Outro")
        items.extend(bar4)
        
        # Bar 5: Em recall
        bar5 = [
            self.n("E", 5, HALF),        
            self.n("G", 5, QUARTER),     
            self.n("B", 5, QUARTER),     
        ]
        verify(bar5, 5, "Outro")
        items.extend(bar5)
        
        # Bar 6: Am - penultimate
        bar6 = [
            self.n("C", 5, QUARTER),     
            self.n("A", 4, QUARTER),     
            self.n("E", 4, HALF),        
        ]
        verify(bar6, 6, "Outro")
        items.extend(bar6)
        
        # Bar 7: D7 - final approach
        bar7 = [
            self.n("F#", 4, QUARTER),    
            self.n("A", 4, QUARTER),     
            self.n("D", 5, QUARTER),     
            self.n("C", 5, QUARTER),     # b7 color
        ]
        verify(bar7, 7, "Outro")
        items.extend(bar7)
        
        # Bar 8: G final chord
        bar8 = [
            self.chord([("D", 5), ("B", 4), ("G", 4)], WHOLE),
        ]
        verify(bar8, 8, "Outro")
        items.extend(bar8)
        
        return items
    
    def outro_bass(self):
        notes = []
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("C", 2, WHOLE)])
        notes.extend([self.n("D", 2, WHOLE)])
        notes.extend([self.n("E", 2, WHOLE)])
        notes.extend([self.n("A", 2, WHOLE)])
        notes.extend([self.n("D", 2, WHOLE)])
        notes.extend([self.n("G", 1, WHOLE)])
        return notes
    
    def outro_chords(self):
        return [
            Chord("G", "maj7"), Chord("G", "maj7"),
            Chord("C", "maj7"), Chord("D", "7"),
            Chord("E", "m7"), Chord("A", "m7"),
            Chord("D", "7"), Chord("G", "maj7"),
        ]
    
    # =========================================================================
    # MusicXML Export
    # =========================================================================
    
    def create_musicxml(self):
        score = ET.Element("score-partwise", version="4.0")
        
        work = ET.SubElement(score, "work")
        ET.SubElement(work, "work-title").text = self.title
        
        ident = ET.SubElement(score, "identification")
        creator = ET.SubElement(ident, "creator", type="composer")
        creator.text = self.composer
        
        part_list = ET.SubElement(score, "part-list")
        gtr = ET.SubElement(part_list, "score-part", id="P1")
        ET.SubElement(gtr, "part-name").text = "Guitar"
        bass = ET.SubElement(part_list, "score-part", id="P2")
        ET.SubElement(bass, "part-name").text = "Bass"
        
        print("\nVerifying all bars...")
        sections = [
            ("1 - Intro", self.intro_melody(), self.intro_bass(), self.intro_chords()),
            ("2 - Triad Solo", self.triad_solo(), self.triad_solo_bass(), self.triad_solo_chords()),
            ("3 - Chord Melody", self.chord_melody(), self.chord_melody_bass(), self.chord_melody_chords()),
            ("4 - Outro", self.outro_melody(), self.outro_bass(), self.outro_chords()),
        ]
        
        all_guitar = []
        all_bass = []
        all_chords = []
        markers = []
        
        bar_count = 0
        for name, g, b, c in sections:
            markers.append((bar_count, name))
            all_guitar.extend(g)
            all_bass.extend(b)
            all_chords.extend(c)
            bar_count += 8
        
        guitar_part = ET.SubElement(score, "part", id="P1")
        self._write_part(guitar_part, all_guitar, all_chords, markers, True)
        
        bass_part = ET.SubElement(score, "part", id="P2")
        self._write_part(bass_part, all_bass, [], [], False)
        
        rough = ET.tostring(score, encoding="unicode")
        return minidom.parseString(rough).toprettyxml(indent="  ")
    
    def _write_part(self, part, items, chords, markers, is_guitar):
        marker_dict = {m: name for m, name in markers}
        measure_num = 1
        item_idx = 0
        chord_idx = 0
        
        while item_idx < len(items):
            measure = ET.SubElement(part, "measure", number=str(measure_num))
            
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
                ET.SubElement(clef, "sign").text = "G" if is_guitar else "F"
                ET.SubElement(clef, "line").text = "2" if is_guitar else "4"
                
                if is_guitar:
                    direction = ET.SubElement(measure, "direction", placement="above")
                    dt = ET.SubElement(direction, "direction-type")
                    met = ET.SubElement(dt, "metronome")
                    ET.SubElement(met, "beat-unit").text = "quarter"
                    ET.SubElement(met, "per-minute").text = str(self.tempo)
            
            if is_guitar and (measure_num - 1) in marker_dict:
                direction = ET.SubElement(measure, "direction", placement="above")
                dt = ET.SubElement(direction, "direction-type")
                ET.SubElement(dt, "rehearsal").text = marker_dict[measure_num - 1]
            
            if is_guitar and chord_idx < len(chords):
                c = chords[chord_idx]
                harmony = ET.SubElement(measure, "harmony")
                root = ET.SubElement(harmony, "root")
                if len(c.root) > 1 and c.root[1] in '#b':
                    ET.SubElement(root, "root-step").text = c.root[0]
                    ET.SubElement(root, "root-alter").text = "1" if c.root[1] == '#' else "-1"
                else:
                    ET.SubElement(root, "root-step").text = c.root
                ET.SubElement(harmony, "kind").text = c.to_kind()
                chord_idx += 1
            
            dur_in_bar = 0
            while item_idx < len(items) and dur_in_bar < BAR:
                item = items[item_idx]
                
                if isinstance(item, ChordVoicing):
                    for i, pitch in enumerate(item.pitches):
                        note_elem = ET.SubElement(measure, "note")
                        if i > 0:
                            ET.SubElement(note_elem, "chord")
                        p = ET.SubElement(note_elem, "pitch")
                        step, octave, alter = self._pitch_xml(pitch)
                        ET.SubElement(p, "step").text = step
                        if alter != 0:
                            ET.SubElement(p, "alter").text = str(alter)
                        ET.SubElement(p, "octave").text = str(octave)
                        ET.SubElement(note_elem, "duration").text = str(item.duration)
                        t, dot = self._dur_type(item.duration)
                        ET.SubElement(note_elem, "type").text = t
                        if dot:
                            ET.SubElement(note_elem, "dot")
                    dur_in_bar += item.duration
                    item_idx += 1
                    
                elif isinstance(item, Note):
                    note_elem = ET.SubElement(measure, "note")
                    if item.is_rest:
                        ET.SubElement(note_elem, "rest")
                    else:
                        p = ET.SubElement(note_elem, "pitch")
                        step, octave, alter = self._pitch_xml(item.pitch)
                        ET.SubElement(p, "step").text = step
                        if alter != 0:
                            ET.SubElement(p, "alter").text = str(alter)
                        ET.SubElement(p, "octave").text = str(octave)
                    ET.SubElement(note_elem, "duration").text = str(item.duration)
                    t, dot = self._dur_type(item.duration)
                    ET.SubElement(note_elem, "type").text = t
                    if dot:
                        ET.SubElement(note_elem, "dot")
                    dur_in_bar += item.duration
                    item_idx += 1
            
            measure_num += 1
    
    def _pitch_xml(self, midi):
        octave = (midi // 12) - 1
        pc = midi % 12
        step, alter = MIDI_TO_NOTE[pc]
        return (step, octave, alter)
    
    def _dur_type(self, dur):
        if dur == DOTTED_HALF:
            return ("half", True)
        if dur == DOTTED_QUARTER:
            return ("quarter", True)
        if dur == DOTTED_EIGHTH:
            return ("eighth", True)
        mapping = {WHOLE: "whole", HALF: "half", QUARTER: "quarter",
                   EIGHTH: "eighth", SIXTEENTH: "16th"}
        return (mapping.get(dur, "quarter"), False)
    
    def save(self, path):
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
    print("HARMOLODIC SKETCH x5 - 5-STAR VERSION")
    print("Bill Frisell Style - UPGRADED")
    print("=" * 60)
    
    out = Path(__file__).parent.parent / "Trio Tunes" / "Alternative_LeadSheets" / "Bill Frisell - Harmolodic Sketch"
    out.mkdir(parents=True, exist_ok=True)
    
    comp = HarmolodicSketchX5()
    path = out / "Harmolodic_Sketch_x5.musicxml"
    comp.save(str(path))
    
    print(f"\nSaved: {path}")
    print("\n5-STAR UPGRADES:")
    print("  ✓ Distinctive melody with SPACE (Frisell signature)")
    print("  ✓ Blue notes and 'wrong' notes for color")
    print("  ✓ Arpeggiated triad solo with breathing room")
    print("  ✓ Hybrid voicings in chord melody")
    print("  ✓ Americana folk-like simplicity")
    print("=" * 60)


if __name__ == "__main__":
    main()

