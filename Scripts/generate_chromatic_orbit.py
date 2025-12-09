"""
Chromatic Orbit - John Scofield Style
======================================

Funky, blues-drenched, chromatic outside playing with:
- Syncopated, unpredictable rhythms
- Chromatic approach notes
- Quartal chord voicings
- Gritty urban energy

Key: Bb7 (dominant, bluesy Mixolydian)
Tempo: 108 BPM (medium funk groove)
Time: 4/4

Form:
  1. Intro Melody (8 bars) - Funky theme with chromatic approaches
  2. Triad Pair Solo (8 bars) - Angular triads, Scofield edge
  3. Chord Melody - Quartal (8 bars) - Voicings built in 4ths
  4. Outro (8 bars) - Modified melody, resolution

RHYTHM COUNTING (triple-checked!):
  - Quarter = 16 divisions
  - Half = 32
  - Whole = 64
  - Eighth = 8
  - Dotted quarter = 24
  - Dotted half = 48
  - 16th = 4
  - EACH BAR = 64 divisions
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

# Duration constants - TRIPLE CHECKED
WHOLE = 64        # 4 beats
DOTTED_HALF = 48  # 3 beats
HALF = 32         # 2 beats
DOTTED_QUARTER = 24  # 1.5 beats
QUARTER = 16      # 1 beat
DOTTED_EIGHTH = 12   # 0.75 beats
EIGHTH = 8        # 0.5 beats
SIXTEENTH = 4     # 0.25 beats
BAR = 64          # Total per bar in 4/4


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
    """Multiple notes played simultaneously."""
    pitches: List[int]
    duration: int


@dataclass 
class Chord:
    root: str
    quality: str
    
    def to_musicxml_harmony(self) -> Tuple[str, str]:
        kind_map = {
            "7": "dominant", "9": "dominant-ninth", "13": "dominant-13th",
            "7#9": "dominant", "7alt": "dominant", "7b9": "dominant",
            "m7": "minor-seventh", "m9": "minor-ninth",
            "maj7": "major-seventh", "6": "major-sixth",
            "sus4": "suspended-fourth", "": "major",
            "dim": "diminished", "m7b5": "half-diminished",
        }
        return (self.root, kind_map.get(self.quality, "dominant"))


def verify_bar(items: List, bar_num: int, section: str) -> int:
    """Verify bar duration and return total. Chord voicings count once."""
    total = 0
    for item in items:
        if isinstance(item, ChordVoicing):
            total += item.duration
        elif isinstance(item, Note):
            total += item.duration
    
    if total != BAR:
        print(f"ERROR: {section} Bar {bar_num}: {total} divisions (need {BAR})")
    else:
        print(f"  ✓ {section} Bar {bar_num}: {total} OK")
    return total


class ChromaticOrbit:
    """John Scofield-inspired funky jazz composition."""
    
    def __init__(self):
        self.title = "Chromatic Orbit"
        self.composer = "GCE (Scofield Style)"
        self.tempo = 108
        self.divisions = 16
        self.key_fifths = -2  # Bb
        
    def p(self, note: str, octave: int) -> int:
        """Pitch helper."""
        return NOTE_TO_MIDI[note] + (octave + 1) * 12
    
    def n(self, note: str, octave: int, dur: int) -> Note:
        """Note helper."""
        return Note(self.p(note, octave), dur)
    
    def r(self, dur: int) -> Note:
        """Rest helper."""
        return Note(0, dur, is_rest=True)
    
    def chord(self, notes: List[Tuple[str, int]], dur: int) -> ChordVoicing:
        """Chord helper. Notes listed high to low."""
        pitches = [self.p(n, o) for n, o in notes]
        return ChordVoicing(pitches, dur)
    
    # =========================================================================
    # SECTION 1: INTRO MELODY - Funky with chromatic approaches
    # =========================================================================
    
    def intro_melody(self) -> List:
        """Funky Scofield-style melody with chromatic approaches."""
        items = []
        
        # Bar 1: Bb7 - Funky opening riff
        # 8+8+8+8+16+16 = 64 ✓
        bar1 = [
            self.n("Bb", 4, EIGHTH),     # Root
            self.n("D", 5, EIGHTH),      # 3rd
            self.n("F", 5, EIGHTH),      # 5th
            self.n("Ab", 5, EIGHTH),     # b7
            self.n("G", 5, QUARTER),     # 6th - blues
            self.n("F", 5, QUARTER),     # 5th
        ]
        verify_bar(bar1, 1, "Intro")
        items.extend(bar1)
        
        # Bar 2: Chromatic approach!
        # 8+8+16+8+8+16 = 64 ✓
        bar2 = [
            self.n("E", 5, EIGHTH),      # Chromatic approach to F
            self.n("F", 5, EIGHTH),      # Target
            self.n("D", 5, QUARTER),     # 3rd
            self.n("Db", 5, EIGHTH),     # Chromatic!
            self.n("C", 5, EIGHTH),      # 9th
            self.n("Bb", 4, QUARTER),    # Root
        ]
        verify_bar(bar2, 2, "Intro")
        items.extend(bar2)
        
        # Bar 3: Eb7 (IV chord) - Answer phrase
        # 16+8+8+16+16 = 64 ✓
        bar3 = [
            self.n("Eb", 5, QUARTER),    # Root
            self.n("G", 5, EIGHTH),      # 3rd
            self.n("Bb", 5, EIGHTH),     # 5th
            self.n("Db", 6, QUARTER),    # b7 - high!
            self.n("C", 6, QUARTER),     # 6th
        ]
        verify_bar(bar3, 3, "Intro")
        items.extend(bar3)
        
        # Bar 4: F7 (V chord) - Tension
        # 8+8+8+8+32 = 64 ✓
        bar4 = [
            self.n("A", 5, EIGHTH),      # 3rd of F7
            self.n("Bb", 5, EIGHTH),     # Chromatic
            self.n("B", 5, EIGHTH),      # Chromatic!
            self.n("C", 6, EIGHTH),      # 5th
            self.n("Eb", 6, HALF),       # b7 - held tension
        ]
        verify_bar(bar4, 4, "Intro")
        items.extend(bar4)
        
        # Bar 5: Bb7 - Return, syncopated
        # 8+24+8+24 = 64 ✓
        bar5 = [
            self.r(EIGHTH),              # Rest - syncopation!
            self.n("Bb", 5, DOTTED_QUARTER),  # Root hit
            self.n("Ab", 5, EIGHTH),     # b7
            self.n("F", 5, DOTTED_QUARTER),   # 5th
        ]
        verify_bar(bar5, 5, "Intro")
        items.extend(bar5)
        
        # Bar 6: Chromatic line down
        # 8+8+8+8+8+8+16 = 64 ✓
        bar6 = [
            self.n("E", 5, EIGHTH),      # Chromatic
            self.n("Eb", 5, EIGHTH),     # Chromatic
            self.n("D", 5, EIGHTH),      # 3rd
            self.n("Db", 5, EIGHTH),     # Chromatic
            self.n("C", 5, EIGHTH),      # 9th
            self.n("B", 4, EIGHTH),      # Chromatic approach
            self.n("Bb", 4, QUARTER),    # Root landing
        ]
        verify_bar(bar6, 6, "Intro")
        items.extend(bar6)
        
        # Bar 7: Eb7 - F7 turnaround
        # 16+16+16+16 = 64 ✓
        bar7 = [
            self.n("G", 5, QUARTER),     # 3rd of Eb
            self.n("Ab", 5, QUARTER),    # 4th
            self.n("A", 5, QUARTER),     # 3rd of F7
            self.n("C", 6, QUARTER),     # 5th of F7
        ]
        verify_bar(bar7, 7, "Intro")
        items.extend(bar7)
        
        # Bar 8: Resolution to Bb
        # 32+32 = 64 ✓
        bar8 = [
            self.n("Bb", 5, HALF),       # Root
            self.n("D", 5, HALF),        # 3rd - bluesy end
        ]
        verify_bar(bar8, 8, "Intro")
        items.extend(bar8)
        
        return items
    
    def intro_bass(self) -> List[Note]:
        """Funky bass line."""
        notes = []
        # Bar 1: Bb groove
        notes.extend([self.n("Bb", 2, QUARTER), self.n("Bb", 2, EIGHTH), 
                      self.n("F", 2, EIGHTH), self.n("Ab", 2, QUARTER), 
                      self.n("Bb", 2, QUARTER)])
        # Bar 2
        notes.extend([self.n("Bb", 2, HALF), self.n("Ab", 2, QUARTER), 
                      self.n("G", 2, QUARTER)])
        # Bar 3: Eb
        notes.extend([self.n("Eb", 2, HALF), self.n("G", 2, QUARTER), 
                      self.n("Bb", 2, QUARTER)])
        # Bar 4: F
        notes.extend([self.n("F", 2, HALF), self.n("Eb", 2, HALF)])
        # Bar 5: Bb
        notes.extend([self.n("Bb", 2, QUARTER), self.n("D", 3, QUARTER), 
                      self.n("F", 3, QUARTER), self.n("Ab", 2, QUARTER)])
        # Bar 6
        notes.extend([self.n("Bb", 2, HALF), self.n("G", 2, HALF)])
        # Bar 7: Eb - F
        notes.extend([self.n("Eb", 2, HALF), self.n("F", 2, HALF)])
        # Bar 8: Bb
        notes.extend([self.n("Bb", 2, WHOLE)])
        return notes
    
    def intro_chords(self) -> List[Chord]:
        return [
            Chord("Bb", "7"), Chord("Bb", "7"),
            Chord("Eb", "7"), Chord("F", "7"),
            Chord("Bb", "7"), Chord("Bb", "7"),
            Chord("Eb", "7"), Chord("Bb", "7"),
        ]
    
    # =========================================================================
    # SECTION 2: TRIAD PAIR SOLO - Arpeggiated eighths with syncopation
    # =========================================================================
    
    def triad_solo(self) -> List:
        """Arpeggiated triad pairs with Scofield rhythmic displacement."""
        items = []
        
        # Bar 1: Bb triad + C triad ARPEGGIATED with syncopation
        # Rest(8) + Bb arp(24) + C arp(24) + note(8) = 8+24+24+8 = 64 ✓
        bar1 = [
            self.r(EIGHTH),              # Syncopated start!
            self.n("Bb", 4, EIGHTH),     # Bb triad arpeggio
            self.n("D", 5, EIGHTH),      
            self.n("F", 5, EIGHTH),      
            self.n("C", 5, EIGHTH),      # C triad arpeggio (outside!)
            self.n("E", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      
            self.n("F", 5, EIGHTH),      # Landing note
        ]
        verify_bar(bar1, 1, "TriadSolo")
        items.extend(bar1)
        
        # Bar 2: Db + Bb triads - displaced rhythm
        # 8+8+8+8+8+8+8+8 = 64 ✓
        bar2 = [
            self.n("Db", 5, EIGHTH),     # Db triad arp
            self.n("F", 5, EIGHTH),      
            self.n("Ab", 5, EIGHTH),     
            self.n("Bb", 5, EIGHTH),     # Bb triad arp
            self.n("D", 5, EIGHTH),      
            self.n("F", 5, EIGHTH),      
            self.n("Ab", 5, EIGHTH),     # Blue note
            self.n("G", 5, EIGHTH),      # Resolution
        ]
        verify_bar(bar2, 2, "TriadSolo")
        items.extend(bar2)
        
        # Bar 3: Eb + F triads with rhythmic push
        # 8+8+8+16+8+8+8 = 64 ✓ (quarter in middle = push)
        bar3 = [
            self.n("Eb", 5, EIGHTH),     # Eb triad
            self.n("G", 5, EIGHTH),      
            self.n("Bb", 5, EIGHTH),     
            self.n("C", 6, QUARTER),     # PUSH - longer note!
            self.n("A", 5, EIGHTH),      # F triad
            self.n("F", 5, EIGHTH),      
            self.n("C", 5, EIGHTH),      
        ]
        verify_bar(bar3, 3, "TriadSolo")
        items.extend(bar3)
        
        # Bar 4: Bb resolution arpeggio
        # 8+8+8+8+32 = 64 ✓
        bar4 = [
            self.n("Bb", 4, EIGHTH),     # Low Bb
            self.n("D", 5, EIGHTH),      
            self.n("F", 5, EIGHTH),      
            self.n("Bb", 5, EIGHTH),     # Octave
            self.n("D", 6, HALF),        # Hold high 3rd
        ]
        verify_bar(bar4, 4, "TriadSolo")
        items.extend(bar4)
        
        # Bar 5: Gm + Am arpeggios - syncopated
        # 8+8+8+8+8+8+16 = 64 ✓
        bar5 = [
            self.r(EIGHTH),              # Syncopation!
            self.n("G", 4, EIGHTH),      # Gm arp
            self.n("Bb", 4, EIGHTH),     
            self.n("D", 5, EIGHTH),      
            self.n("A", 4, EIGHTH),      # Am arp (outside!)
            self.n("C", 5, EIGHTH),      
            self.n("E", 5, QUARTER),     # Hold tension
        ]
        verify_bar(bar5, 5, "TriadSolo")
        items.extend(bar5)
        
        # Bar 6: Cm + Dm with displacement
        # 8+8+8+8+8+8+8+8 = 64 ✓
        bar6 = [
            self.n("C", 5, EIGHTH),      # Cm arp
            self.n("Eb", 5, EIGHTH),     
            self.n("G", 5, EIGHTH),      
            self.n("F", 5, EIGHTH),      # Chromatic passing
            self.n("D", 5, EIGHTH),      # Dm arp
            self.n("F", 5, EIGHTH),      
            self.n("A", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      # Landing
        ]
        verify_bar(bar6, 6, "TriadSolo")
        items.extend(bar6)
        
        # Bar 7: Gb + Ab triads - TENSION! Syncopated
        # 8+8+8+8+8+8+16 = 64 ✓
        bar7 = [
            self.n("Gb", 5, EIGHTH),     # Gb arp - outside!
            self.n("Bb", 5, EIGHTH),     
            self.n("Db", 6, EIGHTH),     
            self.r(EIGHTH),              # Breath/space
            self.n("Ab", 5, EIGHTH),     # Ab arp
            self.n("C", 6, EIGHTH),      
            self.n("Eb", 6, QUARTER),    # Hold high
        ]
        verify_bar(bar7, 7, "TriadSolo")
        items.extend(bar7)
        
        # Bar 8: Bb resolution - final arpeggio
        # 8+8+8+8+32 = 64 ✓
        bar8 = [
            self.n("F", 5, EIGHTH),      # Start on 5th
            self.n("D", 5, EIGHTH),      
            self.n("Bb", 4, EIGHTH),     
            self.n("F", 4, EIGHTH),      # Low 5th
            self.n("Bb", 4, HALF),       # Root - rest
        ]
        verify_bar(bar8, 8, "TriadSolo")
        items.extend(bar8)
        
        return items
    
    def triad_solo_bass(self) -> List[Note]:
        notes = []
        notes.extend([self.n("Bb", 2, HALF), self.n("C", 2, HALF)])
        notes.extend([self.n("Db", 2, HALF), self.n("Bb", 2, HALF)])
        notes.extend([self.n("Eb", 2, HALF), self.n("F", 2, HALF)])
        notes.extend([self.n("Bb", 2, WHOLE)])
        notes.extend([self.n("G", 2, HALF), self.n("A", 2, HALF)])
        notes.extend([self.n("C", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("Gb", 2, HALF), self.n("Ab", 2, HALF)])
        notes.extend([self.n("Bb", 2, WHOLE)])
        return notes
    
    def triad_solo_chords(self) -> List[Chord]:
        return [
            Chord("Bb", "7"), Chord("Bb", "7"),
            Chord("Eb", "7"), Chord("Bb", "7"),
            Chord("G", "m7"), Chord("C", "m7"),
            Chord("F", "7alt"), Chord("Bb", "7"),
        ]
    
    # =========================================================================
    # SECTION 3: CHORD MELODY - QUARTAL VOICINGS (built in 4ths!)
    # =========================================================================
    
    def chord_melody_quartal(self) -> List:
        """Chord melody using quartal voicings (stacked 4ths)."""
        items = []
        
        # Quartal voicings: stacked perfect 4ths (5 semitones each)
        # Example: Bb-Eb-Ab or F-Bb-Eb
        
        # Bar 1: Bb quartal voicings
        # 32+32 = 64 ✓
        bar1 = [
            self.chord([("Ab", 5), ("Eb", 5), ("Bb", 4)], HALF),  # Bb quartal
            self.chord([("Bb", 5), ("F", 5), ("C", 5)], HALF),    # C quartal
        ]
        verify_bar(bar1, 1, "Quartal")
        items.extend(bar1)
        
        # Bar 2: Moving quartal voicings
        # 32+32 = 64 ✓
        bar2 = [
            self.chord([("C", 6), ("G", 5), ("D", 5)], HALF),     # D quartal
            self.chord([("Bb", 5), ("F", 5), ("C", 5)], HALF),    # C quartal
        ]
        verify_bar(bar2, 2, "Quartal")
        items.extend(bar2)
        
        # Bar 3: Eb area quartals
        # 32+32 = 64 ✓
        bar3 = [
            self.chord([("Db", 6), ("Ab", 5), ("Eb", 5)], HALF),  # Eb quartal
            self.chord([("Eb", 6), ("Bb", 5), ("F", 5)], HALF),   # F quartal
        ]
        verify_bar(bar3, 3, "Quartal")
        items.extend(bar3)
        
        # Bar 4: Resolution quartals
        # 64 = 64 ✓
        bar4 = [
            self.chord([("F", 6), ("C", 6), ("G", 5), ("D", 5)], WHOLE),  # 4-note quartal!
        ]
        verify_bar(bar4, 4, "Quartal")
        items.extend(bar4)
        
        # Bar 5: Minor area quartals (Gm)
        # 32+32 = 64 ✓
        bar5 = [
            self.chord([("D", 6), ("A", 5), ("E", 5), ("B", 4)], HALF),  # E quartal
            self.chord([("C", 6), ("G", 5), ("D", 5), ("A", 4)], HALF),  # A quartal
        ]
        verify_bar(bar5, 5, "Quartal")
        items.extend(bar5)
        
        # Bar 6: Building tension
        # 32+32 = 64 ✓
        bar6 = [
            self.chord([("Eb", 6), ("Bb", 5), ("F", 5), ("C", 5)], HALF),  # C quartal ext
            self.chord([("Db", 6), ("Ab", 5), ("Eb", 5), ("Bb", 4)], HALF), # Bb quartal ext
        ]
        verify_bar(bar6, 6, "Quartal")
        items.extend(bar6)
        
        # Bar 7: F7 quartals
        # 32+32 = 64 ✓
        bar7 = [
            self.chord([("Eb", 6), ("Bb", 5), ("F", 5)], HALF),   # F quartal
            self.chord([("C", 6), ("G", 5), ("D", 5)], HALF),     # D quartal (leading)
        ]
        verify_bar(bar7, 7, "Quartal")
        items.extend(bar7)
        
        # Bar 8: Final Bb quartal
        # 64 = 64 ✓
        bar8 = [
            self.chord([("Ab", 5), ("Eb", 5), ("Bb", 4), ("F", 4)], WHOLE),  # Rich Bb quartal
        ]
        verify_bar(bar8, 8, "Quartal")
        items.extend(bar8)
        
        return items
    
    def chord_melody_bass(self) -> List[Note]:
        notes = []
        notes.extend([self.n("Bb", 2, WHOLE)])
        notes.extend([self.n("D", 2, HALF), self.n("C", 2, HALF)])
        notes.extend([self.n("Eb", 2, HALF), self.n("F", 2, HALF)])
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("E", 2, HALF), self.n("A", 2, HALF)])
        notes.extend([self.n("C", 2, HALF), self.n("Bb", 2, HALF)])
        notes.extend([self.n("F", 2, WHOLE)])
        notes.extend([self.n("Bb", 1, WHOLE)])
        return notes
    
    def chord_melody_chords(self) -> List[Chord]:
        return [
            Chord("Bb", "7"), Chord("Bb", "7"),
            Chord("Eb", "7"), Chord("G", "m7"),
            Chord("E", "m7b5"), Chord("C", "m7"),
            Chord("F", "7"), Chord("Bb", "7"),
        ]
    
    # =========================================================================
    # SECTION 4: OUTRO - Modified melody, resolution
    # =========================================================================
    
    def outro_melody(self) -> List:
        """Modified intro melody with resolution."""
        items = []
        
        # Bar 1: Higher energy version
        # 8+8+8+8+16+16 = 64 ✓
        bar1 = [
            self.n("Bb", 5, EIGHTH),
            self.n("D", 6, EIGHTH),
            self.n("F", 6, EIGHTH),
            self.n("Ab", 6, EIGHTH),
            self.n("G", 6, QUARTER),
            self.n("F", 6, QUARTER),
        ]
        verify_bar(bar1, 1, "Outro")
        items.extend(bar1)
        
        # Bar 2: Chromatic descent
        # 8+8+8+8+16+16 = 64 ✓
        bar2 = [
            self.n("E", 6, EIGHTH),
            self.n("Eb", 6, EIGHTH),
            self.n("D", 6, EIGHTH),
            self.n("Db", 6, EIGHTH),
            self.n("C", 6, QUARTER),
            self.n("Bb", 5, QUARTER),
        ]
        verify_bar(bar2, 2, "Outro")
        items.extend(bar2)
        
        # Bar 3: Eb answer
        # 16+16+16+16 = 64 ✓
        bar3 = [
            self.n("Eb", 5, QUARTER),
            self.n("G", 5, QUARTER),
            self.n("Bb", 5, QUARTER),
            self.n("Db", 6, QUARTER),
        ]
        verify_bar(bar3, 3, "Outro")
        items.extend(bar3)
        
        # Bar 4: F7 tension with chord
        # 64 = 64 ✓
        bar4 = [
            self.chord([("Eb", 6), ("C", 6), ("A", 5)], WHOLE),  # F7 voicing
        ]
        verify_bar(bar4, 4, "Outro")
        items.extend(bar4)
        
        # Bar 5: Back to Bb, syncopated
        # 8+24+16+16 = 64 ✓
        bar5 = [
            self.r(EIGHTH),
            self.n("Bb", 5, DOTTED_QUARTER),
            self.n("Ab", 5, QUARTER),
            self.n("F", 5, QUARTER),
        ]
        verify_bar(bar5, 5, "Outro")
        items.extend(bar5)
        
        # Bar 6: Final chromatic line
        # 8+8+8+8+16+16 = 64 ✓
        bar6 = [
            self.n("E", 5, EIGHTH),
            self.n("Eb", 5, EIGHTH),
            self.n("D", 5, EIGHTH),
            self.n("Db", 5, EIGHTH),
            self.n("C", 5, QUARTER),
            self.n("Bb", 4, QUARTER),
        ]
        verify_bar(bar6, 6, "Outro")
        items.extend(bar6)
        
        # Bar 7: Turnaround
        # 16+16+16+16 = 64 ✓
        bar7 = [
            self.n("G", 4, QUARTER),
            self.n("F", 4, QUARTER),
            self.n("Eb", 4, QUARTER),
            self.n("D", 4, QUARTER),
        ]
        verify_bar(bar7, 7, "Outro")
        items.extend(bar7)
        
        # Bar 8: Final Bb chord
        # 64 = 64 ✓
        bar8 = [
            self.chord([("Bb", 5), ("F", 5), ("D", 5), ("Bb", 4)], WHOLE),
        ]
        verify_bar(bar8, 8, "Outro")
        items.extend(bar8)
        
        return items
    
    def outro_bass(self) -> List[Note]:
        notes = []
        notes.extend([self.n("Bb", 2, QUARTER), self.n("Bb", 2, EIGHTH),
                      self.n("F", 2, EIGHTH), self.n("Ab", 2, QUARTER),
                      self.n("Bb", 2, QUARTER)])
        notes.extend([self.n("Bb", 2, HALF), self.n("Ab", 2, HALF)])
        notes.extend([self.n("Eb", 2, HALF), self.n("G", 2, HALF)])
        notes.extend([self.n("F", 2, WHOLE)])
        notes.extend([self.n("Bb", 2, HALF), self.n("G", 2, HALF)])
        notes.extend([self.n("Eb", 2, HALF), self.n("F", 2, HALF)])
        notes.extend([self.n("G", 2, QUARTER), self.n("F", 2, QUARTER),
                      self.n("Eb", 2, QUARTER), self.n("D", 2, QUARTER)])
        notes.extend([self.n("Bb", 1, WHOLE)])
        return notes
    
    def outro_chords(self) -> List[Chord]:
        return [
            Chord("Bb", "7"), Chord("Bb", "7"),
            Chord("Eb", "7"), Chord("F", "7"),
            Chord("Bb", "7"), Chord("Eb", "7"),
            Chord("G", "m7"), Chord("Bb", "7"),
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
        gtr_part = ET.SubElement(part_list, "score-part", id="P1")
        ET.SubElement(gtr_part, "part-name").text = "Guitar"
        bass_part = ET.SubElement(part_list, "score-part", id="P2")
        ET.SubElement(bass_part, "part-name").text = "Bass"
        
        # Collect all sections
        print("\nVerifying all bars...")
        sections = [
            ("1 - Intro", self.intro_melody(), self.intro_bass(), self.intro_chords()),
            ("2 - Triad Pair Solo", self.triad_solo(), self.triad_solo_bass(), self.triad_solo_chords()),
            ("3 - Quartal Chord Melody", self.chord_melody_quartal(), self.chord_melody_bass(), self.chord_melody_chords()),
            ("4 - Outro", self.outro_melody(), self.outro_bass(), self.outro_chords()),
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
        self._write_guitar(guitar, all_guitar, all_chords, markers)
        
        bass_elem = ET.SubElement(score, "part", id="P2")
        self._write_bass(bass_elem, all_bass)
        
        rough = ET.tostring(score, encoding="unicode")
        return minidom.parseString(rough).toprettyxml(indent="  ")
    
    def _write_guitar(self, part, items, chords, markers):
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
                ET.SubElement(clef, "sign").text = "G"
                ET.SubElement(clef, "line").text = "2"
                
                direction = ET.SubElement(measure, "direction", placement="above")
                dt = ET.SubElement(direction, "direction-type")
                met = ET.SubElement(dt, "metronome")
                ET.SubElement(met, "beat-unit").text = "quarter"
                ET.SubElement(met, "per-minute").text = str(self.tempo)
            
            if (measure_num - 1) in marker_dict:
                direction = ET.SubElement(measure, "direction", placement="above")
                dt = ET.SubElement(direction, "direction-type")
                ET.SubElement(dt, "rehearsal").text = marker_dict[measure_num - 1]
            
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
    
    def _write_bass(self, part, notes):
        measure_num = 1
        note_idx = 0
        
        while note_idx < len(notes):
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
    print("CHROMATIC ORBIT - John Scofield Style")
    print("=" * 60)
    
    out = Path(__file__).parent.parent / "Trio Tunes" / "Alternative_LeadSheets" / "John Scofield - Chromatic Orbit"
    out.mkdir(parents=True, exist_ok=True)
    
    comp = ChromaticOrbit()
    path = out / "Chromatic_Orbit.musicxml"
    comp.save(str(path))
    
    print(f"\nSaved: {path}")
    print("\nSCOFIELD CHARACTERISTICS:")
    print("  ✓ Funky Bb7 blues feel")
    print("  ✓ Chromatic approach notes")
    print("  ✓ Angular triad pairs (Bb+C, Gb+Ab)")
    print("  ✓ QUARTAL chord voicings (stacked 4ths)")
    print("  ✓ Syncopated rhythms")
    print("  ✓ All bars = 64 divisions (triple-checked)")
    print("=" * 60)


if __name__ == "__main__":
    main()

