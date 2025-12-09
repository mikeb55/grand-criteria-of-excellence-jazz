"""
First Light - Pat Metheny Style
================================

Lyrical, soaring, beautiful composition with:
- Singable major-key melody
- Brazilian/ECM influence
- Warm, optimistic harmony
- Gentle 16th-note syncopation

Key: G Major
Tempo: 96 BPM (flowing, gentle)
Time: 4/4

Form:
  1. Intro Melody (8 bars) - Beautiful, singable theme
  2. Triad Pair Solo (8 bars) - Lyrical triads, Metheny warmth
  3. Chord Melody (8 bars) - Lush maj9, 6/9 voicings
  4. Outro (8 bars) - Modified melody, gentle resolution

RHYTHM: Each bar = 64 divisions (triple-checked)
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
    pitches: List[int]
    duration: int


@dataclass 
class Chord:
    root: str
    quality: str
    
    def to_musicxml_harmony(self) -> Tuple[str, str]:
        kind_map = {
            "maj7": "major-seventh", "maj9": "major-ninth", 
            "6/9": "major-sixth", "6": "major-sixth", "add9": "major",
            "": "major", "m7": "minor-seventh", "m9": "minor-ninth",
            "7": "dominant", "sus4": "suspended-fourth",
            "m": "minor", "dim": "diminished",
        }
        return (self.root, kind_map.get(self.quality, "major-seventh"))


def verify(items: List, bar_num: int, section: str) -> int:
    total = sum(item.duration for item in items)
    status = "✓" if total == BAR else "✗"
    print(f"  {status} {section} Bar {bar_num}: {total}")
    return total


class FirstLight:
    """Pat Metheny-inspired lyrical composition."""
    
    def __init__(self):
        self.title = "First Light"
        self.composer = "GCE (Metheny Style)"
        self.tempo = 96
        self.divisions = 16
        self.key_fifths = 1  # G major
        
    def p(self, note: str, octave: int) -> int:
        return NOTE_TO_MIDI[note] + (octave + 1) * 12
    
    def n(self, note: str, octave: int, dur: int) -> Note:
        return Note(self.p(note, octave), dur)
    
    def r(self, dur: int) -> Note:
        return Note(0, dur, is_rest=True)
    
    def chord(self, notes: List[Tuple[str, int]], dur: int) -> ChordVoicing:
        return ChordVoicing([self.p(n, o) for n, o in notes], dur)
    
    # =========================================================================
    # SECTION 1: INTRO - Beautiful, singable melody
    # =========================================================================
    
    def intro_melody(self) -> List:
        """Lyrical Metheny-style melody - warm, soaring, singable."""
        items = []
        
        # Bar 1: Gmaj9 - Gentle opening, like sunrise
        # 8+8+16+32 = 64 ✓
        bar1 = [
            self.n("D", 4, EIGHTH),      # Pickup feel
            self.n("E", 4, EIGHTH),      # Rising
            self.n("G", 4, QUARTER),     # Root - gentle
            self.n("A", 4, HALF),        # 9th - warm color
        ]
        verify(bar1, 1, "Intro")
        items.extend(bar1)
        
        # Bar 2: Continue rising - hope building
        # 8+8+24+24 = 64 ✓
        bar2 = [
            self.n("B", 4, EIGHTH),      # 3rd
            self.n("D", 5, EIGHTH),      # 5th
            self.n("E", 5, DOTTED_QUARTER),  # 6th - soaring!
            self.n("D", 5, DOTTED_QUARTER),  # Step back gently
        ]
        verify(bar2, 2, "Intro")
        items.extend(bar2)
        
        # Bar 3: Cmaj9 - Sweet IV chord color
        # 16+16+16+16 = 64 ✓
        bar3 = [
            self.n("E", 5, QUARTER),     # 3rd of C
            self.n("D", 5, QUARTER),     # 9th
            self.n("C", 5, QUARTER),     # Root
            self.n("B", 4, QUARTER),     # maj7
        ]
        verify(bar3, 3, "Intro")
        items.extend(bar3)
        
        # Bar 4: D7sus4 -> D7 - Gentle dominant
        # 32+16+16 = 64 ✓
        bar4 = [
            self.n("A", 4, HALF),        # 5th - sus4 feel
            self.n("G", 4, QUARTER),     # 4th resolving
            self.n("F#", 4, QUARTER),    # 3rd - resolution
        ]
        verify(bar4, 4, "Intro")
        items.extend(bar4)
        
        # Bar 5: Em9 - Relative minor, deepening
        # 8+8+16+16+16 = 64 ✓
        bar5 = [
            self.n("E", 4, EIGHTH),      # Root
            self.n("G", 4, EIGHTH),      # b3
            self.n("B", 4, QUARTER),     # 5th
            self.n("D", 5, QUARTER),     # 7th
            self.n("F#", 5, QUARTER),    # 9th - beautiful
        ]
        verify(bar5, 5, "Intro")
        items.extend(bar5)
        
        # Bar 6: Am9 - Circle of 4ths
        # 24+8+16+16 = 64 ✓
        bar6 = [
            self.n("E", 5, DOTTED_QUARTER),  # 5th
            self.n("D", 5, EIGHTH),          # 4th
            self.n("C", 5, QUARTER),         # b3
            self.n("B", 4, QUARTER),         # 9th
        ]
        verify(bar6, 6, "Intro")
        items.extend(bar6)
        
        # Bar 7: D9 - Building to resolution
        # 16+16+16+16 = 64 ✓
        bar7 = [
            self.n("F#", 4, QUARTER),    # 3rd
            self.n("A", 4, QUARTER),     # 5th
            self.n("C", 5, QUARTER),     # 7th
            self.n("E", 5, QUARTER),     # 9th
        ]
        verify(bar7, 7, "Intro")
        items.extend(bar7)
        
        # Bar 8: Gmaj7 - Home, warmth
        # 32+32 = 64 ✓
        bar8 = [
            self.n("D", 5, HALF),        # 5th - hold
            self.n("B", 4, HALF),        # 3rd - warm ending
        ]
        verify(bar8, 8, "Intro")
        items.extend(bar8)
        
        return items
    
    def intro_bass(self) -> List[Note]:
        notes = []
        # Bar 1: G pedal
        notes.extend([self.n("G", 2, HALF), self.n("D", 3, HALF)])
        # Bar 2
        notes.extend([self.n("G", 2, HALF), self.n("B", 2, HALF)])
        # Bar 3: C
        notes.extend([self.n("C", 2, HALF), self.n("E", 2, HALF)])
        # Bar 4: D
        notes.extend([self.n("D", 2, WHOLE)])
        # Bar 5: Em
        notes.extend([self.n("E", 2, HALF), self.n("G", 2, HALF)])
        # Bar 6: Am
        notes.extend([self.n("A", 2, HALF), self.n("E", 2, HALF)])
        # Bar 7: D
        notes.extend([self.n("D", 2, HALF), self.n("F#", 2, HALF)])
        # Bar 8: G
        notes.extend([self.n("G", 2, WHOLE)])
        return notes
    
    def intro_chords(self) -> List[Chord]:
        return [
            Chord("G", "maj9"), Chord("G", "maj9"),
            Chord("C", "maj9"), Chord("D", "7sus4"),
            Chord("E", "m9"), Chord("A", "m9"),
            Chord("D", "9"), Chord("G", "maj7"),
        ]
    
    # =========================================================================
    # SECTION 2: TRIAD PAIR SOLO - Arpeggiated with gentle syncopation
    # =========================================================================
    
    def triad_solo(self) -> List:
        """Arpeggiated triads with Metheny's lyrical rhythmic feel."""
        items = []
        
        # Bar 1: G + Am arpeggios - gentle syncopation
        # 8+8+8+8+8+8+16 = 64 ✓
        bar1 = [
            self.n("G", 4, EIGHTH),      # G triad arp
            self.n("B", 4, EIGHTH),      
            self.n("D", 5, EIGHTH),      
            self.n("A", 4, EIGHTH),      # Am triad arp
            self.n("C", 5, EIGHTH),      
            self.n("E", 5, EIGHTH),      
            self.n("D", 5, QUARTER),     # Land gently
        ]
        verify(bar1, 1, "TriadSolo")
        items.extend(bar1)
        
        # Bar 2: Bm + C arpeggios - pickup feel
        # 8+8+8+8+8+8+8+8 = 64 ✓
        bar2 = [
            self.n("B", 4, EIGHTH),      # Bm arp
            self.n("D", 5, EIGHTH),      
            self.n("F#", 5, EIGHTH),     
            self.n("G", 5, EIGHTH),      # C arp begins
            self.n("C", 5, EIGHTH),      
            self.n("E", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      
            self.n("E", 5, EIGHTH),      # Echo
        ]
        verify(bar2, 2, "TriadSolo")
        items.extend(bar2)
        
        # Bar 3: D + Em with rhythmic push (dotted rhythm)
        # 12+4+8+8+8+8+16 = 64 ✓
        bar3 = [
            self.n("D", 5, DOTTED_EIGHTH),  # D arp with push
            self.n("F#", 5, SIXTEENTH),     
            self.n("A", 5, EIGHTH),         
            self.n("E", 5, EIGHTH),         # Em arp
            self.n("G", 5, EIGHTH),         
            self.n("B", 5, EIGHTH),         
            self.n("A", 5, QUARTER),        # Soaring hold
        ]
        verify(bar3, 3, "TriadSolo")
        items.extend(bar3)
        
        # Bar 4: G resolution - soaring arpeggio
        # 8+8+8+8+32 = 64 ✓
        bar4 = [
            self.n("G", 4, EIGHTH),      # Low G
            self.n("B", 4, EIGHTH),      
            self.n("D", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      # Octave
            self.n("B", 5, HALF),        # Hold - soaring!
        ]
        verify(bar4, 4, "TriadSolo")
        items.extend(bar4)
        
        # Bar 5: C + D with gentle displacement
        # 8+8+8+8+8+8+8+8 = 64 ✓
        bar5 = [
            self.r(EIGHTH),              # Gentle breath
            self.n("C", 5, EIGHTH),      # C arp
            self.n("E", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      
            self.n("D", 5, EIGHTH),      # D arp
            self.n("F#", 5, EIGHTH),     
            self.n("A", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      # Smooth landing
        ]
        verify(bar5, 5, "TriadSolo")
        items.extend(bar5)
        
        # Bar 6: Em + F#dim - color change
        # 8+8+8+16+8+8+8 = 64 ✓
        bar6 = [
            self.n("E", 5, EIGHTH),      # Em arp
            self.n("G", 5, EIGHTH),      
            self.n("B", 5, EIGHTH),      
            self.n("A", 5, QUARTER),     # Slight pause
            self.n("F#", 5, EIGHTH),     # F#dim arp (tension)
            self.n("A", 5, EIGHTH),      
            self.n("C", 5, EIGHTH),      
        ]
        verify(bar6, 6, "TriadSolo")
        items.extend(bar6)
        
        # Bar 7: Am + D - building to resolution
        # 8+8+8+8+8+8+16 = 64 ✓
        bar7 = [
            self.n("A", 4, EIGHTH),      # Am arp
            self.n("C", 5, EIGHTH),      
            self.n("E", 5, EIGHTH),      
            self.n("D", 5, EIGHTH),      # D arp
            self.n("F#", 5, EIGHTH),     
            self.n("A", 5, EIGHTH),      
            self.n("F#", 5, QUARTER),    # Leading tone held
        ]
        verify(bar7, 7, "TriadSolo")
        items.extend(bar7)
        
        # Bar 8: G final arpeggio - warm resolution
        # 8+8+8+8+32 = 64 ✓
        bar8 = [
            self.n("G", 4, EIGHTH),      # G arp from root
            self.n("D", 5, EIGHTH),      
            self.n("B", 4, EIGHTH),      
            self.n("G", 4, EIGHTH),      
            self.n("D", 5, HALF),        # Warm 5th hold
        ]
        verify(bar8, 8, "TriadSolo")
        items.extend(bar8)
        
        return items
    
    def triad_solo_bass(self) -> List[Note]:
        notes = []
        notes.extend([self.n("G", 2, HALF), self.n("A", 2, HALF)])
        notes.extend([self.n("B", 2, HALF), self.n("C", 2, HALF)])
        notes.extend([self.n("D", 2, HALF), self.n("E", 2, HALF)])
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("C", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("E", 2, HALF), self.n("F#", 2, HALF)])
        notes.extend([self.n("A", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("G", 2, WHOLE)])
        return notes
    
    def triad_solo_chords(self) -> List[Chord]:
        return [
            Chord("G", "maj7"), Chord("B", "m7"),
            Chord("D", ""), Chord("G", "maj7"),
            Chord("C", "maj7"), Chord("E", "m7"),
            Chord("A", "m7"), Chord("G", "maj7"),
        ]
    
    # =========================================================================
    # SECTION 3: CHORD MELODY - Lush Metheny voicings
    # =========================================================================
    
    def chord_melody(self) -> List:
        """Lush chord melody with maj9, 6/9 voicings."""
        items = []
        
        # Bar 1: Gmaj9 voicing
        # 32+32 = 64 ✓
        bar1 = [
            self.chord([("A", 5), ("F#", 5), ("D", 5), ("B", 4)], HALF),  # Gmaj9
            self.chord([("B", 5), ("G", 5), ("D", 5), ("B", 4)], HALF),   # G6
        ]
        verify(bar1, 1, "ChordMel")
        items.extend(bar1)
        
        # Bar 2: Moving to Em9
        # 32+32 = 64 ✓
        bar2 = [
            self.chord([("F#", 5), ("D", 5), ("B", 4), ("G", 4)], HALF),  # Em9
            self.chord([("E", 5), ("D", 5), ("B", 4), ("G", 4)], HALF),   # Em
        ]
        verify(bar2, 2, "ChordMel")
        items.extend(bar2)
        
        # Bar 3: Cmaj9 - Sweet
        # 32+32 = 64 ✓
        bar3 = [
            self.chord([("D", 6), ("B", 5), ("G", 5), ("E", 5)], HALF),   # Cmaj9
            self.chord([("E", 6), ("C", 6), ("G", 5), ("E", 5)], HALF),   # C6/9
        ]
        verify(bar3, 3, "ChordMel")
        items.extend(bar3)
        
        # Bar 4: D9 resolution
        # 64 = 64 ✓
        bar4 = [
            self.chord([("E", 6), ("C", 6), ("A", 5), ("F#", 5)], WHOLE), # D9
        ]
        verify(bar4, 4, "ChordMel")
        items.extend(bar4)
        
        # Bar 5: Am9 - Circle continues
        # 32+32 = 64 ✓
        bar5 = [
            self.chord([("B", 5), ("G", 5), ("E", 5), ("C", 5)], HALF),   # Am9
            self.chord([("A", 5), ("G", 5), ("E", 5), ("C", 5)], HALF),   # Am7
        ]
        verify(bar5, 5, "ChordMel")
        items.extend(bar5)
        
        # Bar 6: Bm7 - Em7
        # 32+32 = 64 ✓
        bar6 = [
            self.chord([("A", 5), ("F#", 5), ("D", 5), ("B", 4)], HALF),  # Bm7
            self.chord([("D", 5), ("B", 4), ("G", 4), ("E", 4)], HALF),   # Em7
        ]
        verify(bar6, 6, "ChordMel")
        items.extend(bar6)
        
        # Bar 7: Am7 - D7
        # 32+32 = 64 ✓
        bar7 = [
            self.chord([("G", 5), ("E", 5), ("C", 5), ("A", 4)], HALF),   # Am7
            self.chord([("F#", 5), ("C", 5), ("A", 4), ("D", 4)], HALF),  # D7
        ]
        verify(bar7, 7, "ChordMel")
        items.extend(bar7)
        
        # Bar 8: Gmaj9 final
        # 64 = 64 ✓
        bar8 = [
            self.chord([("A", 5), ("F#", 5), ("D", 5), ("G", 4)], WHOLE), # Gmaj9 - warm
        ]
        verify(bar8, 8, "ChordMel")
        items.extend(bar8)
        
        return items
    
    def chord_melody_bass(self) -> List[Note]:
        notes = []
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("E", 2, WHOLE)])
        notes.extend([self.n("C", 2, HALF), self.n("C", 2, HALF)])
        notes.extend([self.n("D", 2, WHOLE)])
        notes.extend([self.n("A", 2, WHOLE)])
        notes.extend([self.n("B", 2, HALF), self.n("E", 2, HALF)])
        notes.extend([self.n("A", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("G", 2, WHOLE)])
        return notes
    
    def chord_melody_chords(self) -> List[Chord]:
        return [
            Chord("G", "maj9"), Chord("E", "m9"),
            Chord("C", "maj9"), Chord("D", "9"),
            Chord("A", "m9"), Chord("B", "m7"),
            Chord("A", "m7"), Chord("G", "maj9"),
        ]
    
    # =========================================================================
    # SECTION 4: OUTRO - Modified melody, gentle resolution
    # =========================================================================
    
    def outro_melody(self) -> List:
        """Modified theme with peaceful resolution."""
        items = []
        
        # Bar 1: Higher, more soaring version
        # 8+8+16+32 = 64 ✓
        bar1 = [
            self.n("G", 4, EIGHTH),
            self.n("A", 4, EIGHTH),
            self.n("B", 4, QUARTER),
            self.n("D", 5, HALF),        # Higher start
        ]
        verify(bar1, 1, "Outro")
        items.extend(bar1)
        
        # Bar 2: Soaring to peak
        # 8+8+24+24 = 64 ✓
        bar2 = [
            self.n("E", 5, EIGHTH),
            self.n("G", 5, EIGHTH),
            self.n("A", 5, DOTTED_QUARTER),  # Peak!
            self.n("G", 5, DOTTED_QUARTER),  # Gentle descent
        ]
        verify(bar2, 2, "Outro")
        items.extend(bar2)
        
        # Bar 3: C color - peaceful
        # 16+16+16+16 = 64 ✓
        bar3 = [
            self.n("E", 5, QUARTER),
            self.n("D", 5, QUARTER),
            self.n("C", 5, QUARTER),
            self.n("B", 4, QUARTER),
        ]
        verify(bar3, 3, "Outro")
        items.extend(bar3)
        
        # Bar 4: D resolution preparation
        # 32+16+16 = 64 ✓
        bar4 = [
            self.n("A", 4, HALF),
            self.n("G", 4, QUARTER),
            self.n("F#", 4, QUARTER),
        ]
        verify(bar4, 4, "Outro")
        items.extend(bar4)
        
        # Bar 5: Em - gentle minor touch
        # 8+8+16+16+16 = 64 ✓
        bar5 = [
            self.n("E", 4, EIGHTH),
            self.n("G", 4, EIGHTH),
            self.n("B", 4, QUARTER),
            self.n("D", 5, QUARTER),
            self.n("E", 5, QUARTER),
        ]
        verify(bar5, 5, "Outro")
        items.extend(bar5)
        
        # Bar 6: Am - descending with grace
        # 24+8+16+16 = 64 ✓
        bar6 = [
            self.n("C", 5, DOTTED_QUARTER),
            self.n("B", 4, EIGHTH),
            self.n("A", 4, QUARTER),
            self.n("G", 4, QUARTER),
        ]
        verify(bar6, 6, "Outro")
        items.extend(bar6)
        
        # Bar 7: D - final approach
        # 16+16+16+16 = 64 ✓
        bar7 = [
            self.n("F#", 4, QUARTER),
            self.n("A", 4, QUARTER),
            self.n("D", 5, QUARTER),
            self.n("B", 4, QUARTER),
        ]
        verify(bar7, 7, "Outro")
        items.extend(bar7)
        
        # Bar 8: G final chord - warm resolution
        # 64 = 64 ✓
        bar8 = [
            self.chord([("D", 5), ("B", 4), ("G", 4), ("D", 4)], WHOLE),  # G warm
        ]
        verify(bar8, 8, "Outro")
        items.extend(bar8)
        
        return items
    
    def outro_bass(self) -> List[Note]:
        notes = []
        notes.extend([self.n("G", 2, HALF), self.n("D", 3, HALF)])
        notes.extend([self.n("G", 2, HALF), self.n("B", 2, HALF)])
        notes.extend([self.n("C", 2, HALF), self.n("E", 2, HALF)])
        notes.extend([self.n("D", 2, WHOLE)])
        notes.extend([self.n("E", 2, HALF), self.n("G", 2, HALF)])
        notes.extend([self.n("A", 2, HALF), self.n("E", 2, HALF)])
        notes.extend([self.n("D", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("G", 1, WHOLE)])
        return notes
    
    def outro_chords(self) -> List[Chord]:
        return [
            Chord("G", "maj9"), Chord("G", "6/9"),
            Chord("C", "maj9"), Chord("D", "7sus4"),
            Chord("E", "m9"), Chord("A", "m9"),
            Chord("D", "9"), Chord("G", "maj9"),
        ]
    
    # =========================================================================
    # MusicXML Export
    # =========================================================================
    
    def create_musicxml(self) -> str:
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
                _, kind = c.to_musicxml_harmony()
                ET.SubElement(harmony, "kind").text = kind
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
                    note_elem = ET.SubElement(measure, "note")
                    if item.is_rest:
                        ET.SubElement(note_elem, "rest")
                    else:
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
    print("FIRST LIGHT - Pat Metheny Style")
    print("=" * 60)
    
    out = Path(__file__).parent.parent / "Trio Tunes" / "Alternative_LeadSheets" / "Pat Metheny - First Light"
    out.mkdir(parents=True, exist_ok=True)
    
    comp = FirstLight()
    path = out / "First_Light.musicxml"
    comp.save(str(path))
    
    print(f"\nSaved: {path}")
    print("\nMETHENY CHARACTERISTICS:")
    print("  ✓ Lyrical, singable melody")
    print("  ✓ G major warmth and optimism")
    print("  ✓ maj9, 6/9 voicings")
    print("  ✓ Gentle chord progressions (I-IV-V-vi)")
    print("  ✓ Soaring melodic peaks")
    print("  ✓ All bars = 64 divisions (triple-checked)")
    print("=" * 60)


if __name__ == "__main__":
    main()

