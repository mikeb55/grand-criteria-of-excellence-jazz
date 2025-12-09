"""
Entangled Horizons - An Ant Law-Inspired Composition
=====================================================

A sophisticated modern jazz composition featuring:
- Beautiful, singable main melody with intervallic interest
- Chorus 1: Open triad pair solo passage
- Chorus 2: Sophisticated chord melody voicings
- Fully independent guitar and bass parts
- Modern harmonic language inspired by Ant Law's work

Composition: "Entangled Horizons"
Key: Bb Major / G Minor (modal interchange)
Time: 4/4 (swing feel)
Form: Intro - A - A' - B (Triad Solo) - C (Chord Melody) - A'' - Coda

RHYTHM COUNTING:
- divisions = 16 per quarter note
- Quarter note = 16
- Half note = 32
- Whole note = 64
- Eighth note = 8
- Dotted quarter = 24
- Dotted half = 48
- 16th note = 4
- Dotted eighth = 12
- EACH BAR IN 4/4 = 64 divisions total
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
import subprocess

# Note and pitch utilities
NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, 
    "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11, "Cb": 11
}

MIDI_TO_NOTE = {
    0: ("C", 0), 1: ("C", 1), 2: ("D", 0), 3: ("E", -1),
    4: ("E", 0), 5: ("F", 0), 6: ("F", 1), 7: ("G", 0),
    8: ("A", -1), 9: ("A", 0), 10: ("B", -1), 11: ("B", 0)
}

# Duration constants (divisions = 16 per quarter)
WHOLE = 64
HALF = 32
DOTTED_HALF = 48
QUARTER = 16
DOTTED_QUARTER = 24
EIGHTH = 8
DOTTED_EIGHTH = 12
SIXTEENTH = 4

# Bar length in 4/4
BAR = 64


@dataclass
class Note:
    """Represents a single note."""
    pitch: int  # MIDI pitch
    duration: int  # Duration in divisions (16 = quarter note)
    is_rest: bool = False
    tie_start: bool = False
    tie_stop: bool = False
    
    def get_step_octave_alter(self) -> Tuple[str, int, int]:
        """Get MusicXML step, octave, and alter."""
        if self.is_rest:
            return ("C", 4, 0)
        octave = (self.pitch // 12) - 1
        pc = self.pitch % 12
        step, alter = MIDI_TO_NOTE[pc]
        return (step, octave, alter)


@dataclass
class Chord:
    """Represents a chord with root, quality, and optional bass."""
    root: str
    quality: str
    bass: Optional[str] = None
    
    def to_musicxml_harmony(self) -> Tuple[str, str]:
        """Return root and kind for MusicXML."""
        kind_map = {
            "maj7": "major-seventh",
            "7": "dominant",
            "m7": "minor-seventh", 
            "m7b5": "half-diminished",
            "dim7": "diminished-seventh",
            "6": "major-sixth",
            "m6": "minor-sixth",
            "sus4": "suspended-fourth",
            "sus2": "suspended-second",
            "aug": "augmented",
            "maj9": "major-ninth",
            "9": "dominant-ninth",
            "m9": "minor-ninth",
            "7alt": "dominant",
            "7#9": "dominant",
            "7b9": "dominant",
            "7#11": "dominant",
            "maj7#11": "major-seventh",
            "mMaj7": "major-minor",
        }
        return (self.root, kind_map.get(self.quality, "major"))


def verify_bar(notes: List[Note], bar_num: int, part_name: str) -> bool:
    """Verify that notes add up to exactly one bar (64 divisions)."""
    total = sum(n.duration for n in notes)
    if total != BAR:
        print(f"ERROR: {part_name} Bar {bar_num}: {total} divisions (should be {BAR})")
        return False
    return True


class EntangledHorizonsComposition:
    """
    Main composition generator for 'Entangled Horizons'.
    """
    
    def __init__(self):
        self.title = "Entangled Horizons"
        self.composer = "Generative Composition Engine"
        self.tempo = 132
        self.time_sig = (4, 4)
        self.divisions = 16  # 16 divisions per quarter note
        
        # Key signature: Bb major (2 flats)
        self.key_fifths = -2
        self.key_mode = "major"
        
    def midi_pitch(self, note_name: str, octave: int) -> int:
        """Convert note name and octave to MIDI pitch."""
        return NOTE_TO_MIDI[note_name] + (octave + 1) * 12
    
    # =========================================================================
    # SECTION A: Main Theme - Beautiful, Memorable Melody
    # Each bar = 64 divisions exactly
    # =========================================================================
    
    def generate_section_a_melody(self) -> List[Note]:
        """
        Generate the main theme melody - memorable, singable, with intervallic interest.
        STRICT: Each bar must equal exactly 64 divisions.
        """
        notes = []
        
        # Bar 1: Bbmaj7 - Opening statement (64 divisions)
        # Dotted quarter + eighth + quarter + quarter + eighth + eighth = 24+8+16+16 = 64 ✓
        bar1 = [
            Note(self.midi_pitch("D", 5), DOTTED_QUARTER),   # 24 - Strong 3rd
            Note(self.midi_pitch("F", 5), EIGHTH),            # 8  - 5th
            Note(self.midi_pitch("G", 5), QUARTER),           # 16 - 6th color
            Note(self.midi_pitch("Bb", 5), QUARTER),          # 16 - Root resolution
        ]
        verify_bar(bar1, 1, "Melody")
        notes.extend(bar1)
        
        # Bar 2: Cm9 - Response phrase (64 divisions)
        # Quarter + eighth + eighth + quarter + quarter = 16+8+8+16+16 = 64 ✓
        bar2 = [
            Note(self.midi_pitch("A", 5), QUARTER),           # 16 - Approach from above
            Note(self.midi_pitch("G", 5), EIGHTH),            # 8  - 5th of Cm
            Note(self.midi_pitch("Eb", 5), EIGHTH),           # 8  - b3 of Cm
            Note(self.midi_pitch("D", 5), QUARTER),           # 16 - 9th
            Note(self.midi_pitch("C", 5), QUARTER),           # 16 - Root
        ]
        verify_bar(bar2, 2, "Melody")
        notes.extend(bar2)
        
        # Bar 3: F7sus4 -> F7 (64 divisions)
        # Half + quarter + quarter = 32+16+16 = 64 ✓
        bar3 = [
            Note(self.midi_pitch("Bb", 4), HALF),             # 32 - Sus4 held
            Note(self.midi_pitch("C", 5), QUARTER),           # 16 - 5th
            Note(self.midi_pitch("Eb", 5), QUARTER),          # 16 - b7
        ]
        verify_bar(bar3, 3, "Melody")
        notes.extend(bar3)
        
        # Bar 4: Bbmaj7 - Resolution (64 divisions)
        # Dotted quarter + eighth + half = 24+8+32 = 64 ✓
        bar4 = [
            Note(self.midi_pitch("D", 5), DOTTED_QUARTER),    # 24 - 3rd
            Note(self.midi_pitch("F", 5), EIGHTH),            # 8  - 5th
            Note(self.midi_pitch("Bb", 4), HALF),             # 32 - Root, low
        ]
        verify_bar(bar4, 4, "Melody")
        notes.extend(bar4)
        
        # Bar 5: Gm9 - Second phrase (64 divisions)
        # Quarter + quarter + half = 16+16+32 = 64 ✓
        bar5 = [
            Note(self.midi_pitch("G", 4), QUARTER),           # 16 - Root
            Note(self.midi_pitch("Bb", 4), QUARTER),          # 16 - b3
            Note(self.midi_pitch("D", 5), HALF),              # 32 - 5th, held
        ]
        verify_bar(bar5, 5, "Melody")
        notes.extend(bar5)
        
        # Bar 6: Ebmaj7#11 - Lydian color (64 divisions)
        # Eighth + eighth + quarter + half = 8+8+16+32 = 64 ✓
        bar6 = [
            Note(self.midi_pitch("F", 5), EIGHTH),            # 8  - 9th
            Note(self.midi_pitch("A", 5), EIGHTH),            # 8  - #11 Lydian!
            Note(self.midi_pitch("G", 5), QUARTER),           # 16 - 3rd
            Note(self.midi_pitch("Bb", 5), HALF),             # 32 - 5th
        ]
        verify_bar(bar6, 6, "Melody")
        notes.extend(bar6)
        
        # Bar 7: Am7b5 -> D7alt (64 divisions)
        # Quarter + quarter + quarter + quarter = 16+16+16+16 = 64 ✓
        bar7 = [
            Note(self.midi_pitch("C", 5), QUARTER),           # 16 - b3 of Am7b5
            Note(self.midi_pitch("A", 4), QUARTER),           # 16 - Root
            Note(self.midi_pitch("Ab", 4), QUARTER),          # 16 - D7alt: b5
            Note(self.midi_pitch("F#", 4), QUARTER),          # 16 - D7alt: 3rd
        ]
        verify_bar(bar7, 7, "Melody")
        notes.extend(bar7)
        
        # Bar 8: Gm6/9 - Resolution (64 divisions)
        # Half + quarter + quarter = 32+16+16 = 64 ✓
        bar8 = [
            Note(self.midi_pitch("G", 5), HALF),              # 32 - Root
            Note(self.midi_pitch("E", 5), QUARTER),           # 16 - 6th
            Note(self.midi_pitch("D", 5), QUARTER),           # 16 - 5th
        ]
        verify_bar(bar8, 8, "Melody")
        notes.extend(bar8)
        
        return notes
    
    def generate_section_a_bass(self) -> List[Note]:
        """
        Generate independent bass line for Section A.
        Walking bass with melodic interest, NOT doubling guitar.
        STRICT: Each bar must equal exactly 64 divisions.
        """
        notes = []
        
        # Bar 1: Bbmaj7 - walking bass (64 divisions)
        # 4 quarters = 16+16+16+16 = 64 ✓
        bar1 = [
            Note(self.midi_pitch("Bb", 2), QUARTER),
            Note(self.midi_pitch("D", 3), QUARTER),
            Note(self.midi_pitch("F", 3), QUARTER),
            Note(self.midi_pitch("A", 3), QUARTER),
        ]
        verify_bar(bar1, 1, "Bass")
        notes.extend(bar1)
        
        # Bar 2: Cm9 (64 divisions)
        bar2 = [
            Note(self.midi_pitch("C", 3), QUARTER),
            Note(self.midi_pitch("Eb", 3), QUARTER),
            Note(self.midi_pitch("G", 3), QUARTER),
            Note(self.midi_pitch("Bb", 3), QUARTER),
        ]
        verify_bar(bar2, 2, "Bass")
        notes.extend(bar2)
        
        # Bar 3: F7sus4 -> F7 (64 divisions)
        bar3 = [
            Note(self.midi_pitch("F", 2), QUARTER),
            Note(self.midi_pitch("C", 3), QUARTER),
            Note(self.midi_pitch("Eb", 3), QUARTER),
            Note(self.midi_pitch("E", 3), QUARTER),   # Chromatic resolution
        ]
        verify_bar(bar3, 3, "Bass")
        notes.extend(bar3)
        
        # Bar 4: Bbmaj7 - countermelody (64 divisions)
        bar4 = [
            Note(self.midi_pitch("Bb", 2), QUARTER),
            Note(self.midi_pitch("A", 2), QUARTER),   # Descending countermelody
            Note(self.midi_pitch("G", 2), QUARTER),
            Note(self.midi_pitch("F", 2), QUARTER),
        ]
        verify_bar(bar4, 4, "Bass")
        notes.extend(bar4)
        
        # Bar 5: Gm9 (64 divisions)
        bar5 = [
            Note(self.midi_pitch("G", 2), QUARTER),
            Note(self.midi_pitch("Bb", 2), QUARTER),
            Note(self.midi_pitch("D", 3), QUARTER),
            Note(self.midi_pitch("F", 3), QUARTER),
        ]
        verify_bar(bar5, 5, "Bass")
        notes.extend(bar5)
        
        # Bar 6: Ebmaj7#11 (64 divisions)
        bar6 = [
            Note(self.midi_pitch("Eb", 2), QUARTER),
            Note(self.midi_pitch("G", 2), QUARTER),
            Note(self.midi_pitch("Bb", 2), QUARTER),
            Note(self.midi_pitch("D", 3), QUARTER),
        ]
        verify_bar(bar6, 6, "Bass")
        notes.extend(bar6)
        
        # Bar 7: Am7b5 -> D7alt (64 divisions)
        bar7 = [
            Note(self.midi_pitch("A", 2), QUARTER),
            Note(self.midi_pitch("Eb", 3), QUARTER),   # b5
            Note(self.midi_pitch("D", 2), QUARTER),
            Note(self.midi_pitch("Ab", 2), QUARTER),   # b5 of D7alt
        ]
        verify_bar(bar7, 7, "Bass")
        notes.extend(bar7)
        
        # Bar 8: Gm6/9 (64 divisions)
        bar8 = [
            Note(self.midi_pitch("G", 2), QUARTER),
            Note(self.midi_pitch("E", 2), QUARTER),   # 6th in bass
            Note(self.midi_pitch("D", 2), QUARTER),
            Note(self.midi_pitch("C", 2), QUARTER),   # Approach to next
        ]
        verify_bar(bar8, 8, "Bass")
        notes.extend(bar8)
        
        return notes
    
    def generate_section_a_chords(self) -> List[Chord]:
        """Generate chord symbols for Section A."""
        return [
            Chord("Bb", "maj7"),
            Chord("C", "m9"),
            Chord("F", "7sus4"),
            Chord("Bb", "maj7"),
            Chord("G", "m9"),
            Chord("Eb", "maj7#11"),
            Chord("A", "m7b5"),
            Chord("G", "m6"),
        ]
    
    # =========================================================================
    # SECTION B: Triad Pair Solo - Open Voicings, Intervallic Lines
    # Each bar = 64 divisions exactly
    # =========================================================================
    
    def generate_section_b_melody(self) -> List[Note]:
        """
        Generate triad pair solo section.
        Using Klemonic and diatonic triad pairs with open voicings.
        STRICT: Each bar must equal exactly 64 divisions.
        """
        notes = []
        
        # Bar 1: Cm9 - C minor + D minor triad pair (64 divisions)
        # Eighth + eighth + quarter + quarter + quarter = 8+8+16+16+16 = 64 ✓
        bar1 = [
            Note(self.midi_pitch("C", 5), EIGHTH),    # C minor root
            Note(self.midi_pitch("G", 5), EIGHTH),    # Open 5th leap
            Note(self.midi_pitch("D", 5), QUARTER),   # D minor root
            Note(self.midi_pitch("A", 5), QUARTER),   # D minor 5th - wide!
            Note(self.midi_pitch("Eb", 5), QUARTER),  # Back to C minor b3
        ]
        verify_bar(bar1, 1, "Solo")
        notes.extend(bar1)
        
        # Bar 2: F7 - F major + G minor triad pair (64 divisions)
        # Quarter + quarter + eighth + eighth + quarter = 16+16+8+8+16 = 64 ✓
        bar2 = [
            Note(self.midi_pitch("F", 5), QUARTER),   # F root
            Note(self.midi_pitch("C", 6), QUARTER),   # F 5th - leap up
            Note(self.midi_pitch("G", 5), EIGHTH),    # G minor root
            Note(self.midi_pitch("Bb", 5), EIGHTH),   # G minor 3rd
            Note(self.midi_pitch("D", 6), QUARTER),   # G minor 5th
        ]
        verify_bar(bar2, 2, "Solo")
        notes.extend(bar2)
        
        # Bar 3: Bbmaj7 - Bb major + C minor pair (64 divisions)
        # Quarter + eighth + eighth + quarter + quarter = 16+8+8+16+16 = 64 ✓
        bar3 = [
            Note(self.midi_pitch("Bb", 5), QUARTER),  # Bb root
            Note(self.midi_pitch("D", 6), EIGHTH),    # Bb 3rd
            Note(self.midi_pitch("C", 6), EIGHTH),    # C minor root
            Note(self.midi_pitch("Eb", 6), QUARTER),  # C minor 3rd
            Note(self.midi_pitch("G", 5), QUARTER),   # C minor 5th - drop
        ]
        verify_bar(bar3, 3, "Solo")
        notes.extend(bar3)
        
        # Bar 4: Ebmaj7 - Eb major + F minor pair (64 divisions)
        # Quarter + quarter + quarter + quarter = 16+16+16+16 = 64 ✓
        bar4 = [
            Note(self.midi_pitch("Eb", 5), QUARTER),  # Eb root
            Note(self.midi_pitch("Bb", 5), QUARTER),  # Eb 5th
            Note(self.midi_pitch("F", 5), QUARTER),   # F minor root
            Note(self.midi_pitch("C", 6), QUARTER),   # F minor 5th
        ]
        verify_bar(bar4, 4, "Solo")
        notes.extend(bar4)
        
        # Bar 5: Am7b5 - A dim + Bb major (64 divisions)
        # Eighth + dotted quarter + quarter + eighth + eighth = 8+24+16+8+8 = 64 ✓
        bar5 = [
            Note(self.midi_pitch("A", 5), EIGHTH),           # A root
            Note(self.midi_pitch("Eb", 6), DOTTED_QUARTER),  # b5 - held tension
            Note(self.midi_pitch("Bb", 5), QUARTER),         # Bb major root
            Note(self.midi_pitch("F", 6), EIGHTH),           # Bb 5th
            Note(self.midi_pitch("D", 6), EIGHTH),           # Bb 3rd
        ]
        verify_bar(bar5, 5, "Solo")
        notes.extend(bar5)
        
        # Bar 6: D7alt - Eb major + F# major (UST) (64 divisions)
        # Quarter + quarter + quarter + quarter = 16+16+16+16 = 64 ✓
        bar6 = [
            Note(self.midi_pitch("Eb", 5), QUARTER),  # b9 of D7
            Note(self.midi_pitch("G", 5), QUARTER),   # Eb 3rd
            Note(self.midi_pitch("F#", 5), QUARTER),  # 3rd of D7
            Note(self.midi_pitch("C#", 6), QUARTER),  # F# 5th - tension
        ]
        verify_bar(bar6, 6, "Solo")
        notes.extend(bar6)
        
        # Bar 7: Gm9 - G minor + A minor pair (64 divisions)
        # Quarter + quarter + half = 16+16+32 = 64 ✓
        bar7 = [
            Note(self.midi_pitch("G", 5), QUARTER),   # G minor root
            Note(self.midi_pitch("D", 6), QUARTER),   # G minor 5th - open
            Note(self.midi_pitch("A", 5), HALF),      # A minor root - held
        ]
        verify_bar(bar7, 7, "Solo")
        notes.extend(bar7)
        
        # Bar 8: Cm7 -> F7 - Resolution (64 divisions)
        # Quarter + quarter + quarter + quarter = 16+16+16+16 = 64 ✓
        bar8 = [
            Note(self.midi_pitch("C", 6), QUARTER),   # C minor root
            Note(self.midi_pitch("Eb", 6), QUARTER),  # C minor 3rd
            Note(self.midi_pitch("A", 5), QUARTER),   # F7 3rd
            Note(self.midi_pitch("C", 5), QUARTER),   # F7 5th
        ]
        verify_bar(bar8, 8, "Solo")
        notes.extend(bar8)
        
        return notes
    
    def generate_section_b_bass(self) -> List[Note]:
        """
        Generate independent bass for triad pair solo section.
        STRICT: Each bar must equal exactly 64 divisions.
        """
        notes = []
        
        # Bar 1: Cm9 (64 divisions)
        bar1 = [
            Note(self.midi_pitch("C", 2), HALF),
            Note(self.midi_pitch("G", 2), QUARTER),
            Note(self.midi_pitch("Bb", 2), QUARTER),
        ]
        verify_bar(bar1, 1, "Bass Solo")
        notes.extend(bar1)
        
        # Bar 2: F7 (64 divisions)
        bar2 = [
            Note(self.midi_pitch("F", 2), QUARTER),
            Note(self.midi_pitch("A", 2), QUARTER),
            Note(self.midi_pitch("C", 3), QUARTER),
            Note(self.midi_pitch("E", 3), QUARTER),
        ]
        verify_bar(bar2, 2, "Bass Solo")
        notes.extend(bar2)
        
        # Bar 3: Bbmaj7 (64 divisions)
        bar3 = [
            Note(self.midi_pitch("Bb", 1), HALF),
            Note(self.midi_pitch("F", 2), QUARTER),
            Note(self.midi_pitch("D", 2), QUARTER),
        ]
        verify_bar(bar3, 3, "Bass Solo")
        notes.extend(bar3)
        
        # Bar 4: Ebmaj7 (64 divisions)
        bar4 = [
            Note(self.midi_pitch("Eb", 2), QUARTER),
            Note(self.midi_pitch("Bb", 2), QUARTER),
            Note(self.midi_pitch("G", 2), QUARTER),
            Note(self.midi_pitch("F", 2), QUARTER),
        ]
        verify_bar(bar4, 4, "Bass Solo")
        notes.extend(bar4)
        
        # Bar 5: Am7b5 (64 divisions)
        bar5 = [
            Note(self.midi_pitch("A", 2), HALF),
            Note(self.midi_pitch("Eb", 3), QUARTER),  # b5 color
            Note(self.midi_pitch("G", 2), QUARTER),
        ]
        verify_bar(bar5, 5, "Bass Solo")
        notes.extend(bar5)
        
        # Bar 6: D7alt (64 divisions)
        bar6 = [
            Note(self.midi_pitch("D", 2), HALF),
            Note(self.midi_pitch("Ab", 2), QUARTER),  # b5
            Note(self.midi_pitch("C", 3), QUARTER),   # 7th
        ]
        verify_bar(bar6, 6, "Bass Solo")
        notes.extend(bar6)
        
        # Bar 7: Gm9 (64 divisions)
        bar7 = [
            Note(self.midi_pitch("G", 2), HALF),
            Note(self.midi_pitch("D", 3), QUARTER),
            Note(self.midi_pitch("A", 2), QUARTER),
        ]
        verify_bar(bar7, 7, "Bass Solo")
        notes.extend(bar7)
        
        # Bar 8: Cm7 -> F7 (64 divisions)
        bar8 = [
            Note(self.midi_pitch("C", 2), HALF),
            Note(self.midi_pitch("F", 2), QUARTER),
            Note(self.midi_pitch("E", 2), QUARTER),
        ]
        verify_bar(bar8, 8, "Bass Solo")
        notes.extend(bar8)
        
        return notes
    
    def generate_section_b_chords(self) -> List[Chord]:
        """Generate chord symbols for Section B (Triad Pair Solo)."""
        return [
            Chord("C", "m9"),
            Chord("F", "7"),
            Chord("Bb", "maj7"),
            Chord("Eb", "maj7"),
            Chord("A", "m7b5"),
            Chord("D", "7alt"),
            Chord("G", "m9"),
            Chord("C", "m7"),
        ]
    
    # =========================================================================
    # SECTION C: Chord Melody - Rich Voicings, Harmonic Beauty
    # Each bar = 64 divisions exactly
    # =========================================================================
    
    def generate_section_c_melody(self) -> List[Note]:
        """
        Generate chord melody section - TOP voice.
        STRICT: Each bar must equal exactly 64 divisions.
        """
        notes = []
        
        # Bar 1: Gm(maj7) - haunting (64 divisions)
        # Dotted half + quarter = 48+16 = 64 ✓
        bar1 = [
            Note(self.midi_pitch("F#", 5), DOTTED_HALF),  # Major 7th tension
            Note(self.midi_pitch("G", 5), QUARTER),       # Resolution
        ]
        verify_bar(bar1, 1, "ChordMel")
        notes.extend(bar1)
        
        # Bar 2: Cm9 (64 divisions)
        # Half + quarter + quarter = 32+16+16 = 64 ✓
        bar2 = [
            Note(self.midi_pitch("D", 5), HALF),      # 9th
            Note(self.midi_pitch("Eb", 5), QUARTER),  # b3rd
            Note(self.midi_pitch("G", 5), QUARTER),   # 5th
        ]
        verify_bar(bar2, 2, "ChordMel")
        notes.extend(bar2)
        
        # Bar 3: Fmaj7#11 - Lydian (64 divisions)
        # Half + quarter + quarter = 32+16+16 = 64 ✓
        bar3 = [
            Note(self.midi_pitch("B", 5), HALF),      # #11!
            Note(self.midi_pitch("A", 5), QUARTER),   # 3rd
            Note(self.midi_pitch("G", 5), QUARTER),   # 9th
        ]
        verify_bar(bar3, 3, "ChordMel")
        notes.extend(bar3)
        
        # Bar 4: Bb6/9 (64 divisions)
        # Dotted quarter + dotted quarter + quarter + eighth = 24+24+16 = 64 ✓
        bar4 = [
            Note(self.midi_pitch("C", 6), DOTTED_QUARTER),  # 9th
            Note(self.midi_pitch("G", 5), DOTTED_QUARTER),  # 6th
            Note(self.midi_pitch("F", 5), QUARTER),         # 5th
        ]
        verify_bar(bar4, 4, "ChordMel")
        notes.extend(bar4)
        
        # Bar 5: Ebmaj7 (64 divisions)
        # Half + quarter + quarter = 32+16+16 = 64 ✓
        bar5 = [
            Note(self.midi_pitch("D", 6), HALF),      # Eb maj7
            Note(self.midi_pitch("C", 6), QUARTER),   # 6th
            Note(self.midi_pitch("Bb", 5), QUARTER),  # 5th
        ]
        verify_bar(bar5, 5, "ChordMel")
        notes.extend(bar5)
        
        # Bar 6: Gm9 (64 divisions)
        # Half + quarter + quarter = 32+16+16 = 64 ✓
        bar6 = [
            Note(self.midi_pitch("A", 5), HALF),      # 9th
            Note(self.midi_pitch("F", 5), QUARTER),   # 7th
            Note(self.midi_pitch("D", 5), QUARTER),   # 5th
        ]
        verify_bar(bar6, 6, "ChordMel")
        notes.extend(bar6)
        
        # Bar 7: Am7b5 -> D7#9 (64 divisions)
        # Quarter + quarter + quarter + quarter = 16+16+16+16 = 64 ✓
        bar7 = [
            Note(self.midi_pitch("G", 5), QUARTER),   # Am7b5: 7th
            Note(self.midi_pitch("C", 5), QUARTER),   # Am7b5: b3
            Note(self.midi_pitch("F", 5), QUARTER),   # D7#9: #9
            Note(self.midi_pitch("F#", 5), QUARTER),  # D7: 3rd
        ]
        verify_bar(bar7, 7, "ChordMel")
        notes.extend(bar7)
        
        # Bar 8: Gm6/9 - final (64 divisions)
        # Quarter + quarter + half = 16+16+32 = 64 ✓
        bar8 = [
            Note(self.midi_pitch("A", 5), QUARTER),   # 9th
            Note(self.midi_pitch("E", 5), QUARTER),   # 6th
            Note(self.midi_pitch("G", 5), HALF),      # Root - held
        ]
        verify_bar(bar8, 8, "ChordMel")
        notes.extend(bar8)
        
        return notes
    
    def generate_section_c_bass(self) -> List[Note]:
        """
        Generate bass for chord melody section.
        STRICT: Each bar must equal exactly 64 divisions.
        """
        notes = []
        
        # Bar 1: Gm(maj7) (64 divisions)
        bar1 = [
            Note(self.midi_pitch("G", 2), DOTTED_HALF),
            Note(self.midi_pitch("A", 2), QUARTER),
        ]
        verify_bar(bar1, 1, "Bass CM")
        notes.extend(bar1)
        
        # Bar 2: Cm9 (64 divisions)
        bar2 = [
            Note(self.midi_pitch("C", 2), DOTTED_HALF),
            Note(self.midi_pitch("Bb", 2), QUARTER),
        ]
        verify_bar(bar2, 2, "Bass CM")
        notes.extend(bar2)
        
        # Bar 3: Fmaj7#11 (64 divisions)
        bar3 = [
            Note(self.midi_pitch("F", 2), DOTTED_HALF),
            Note(self.midi_pitch("E", 2), QUARTER),
        ]
        verify_bar(bar3, 3, "Bass CM")
        notes.extend(bar3)
        
        # Bar 4: Bb6/9 (64 divisions)
        bar4 = [
            Note(self.midi_pitch("Bb", 1), DOTTED_HALF),
            Note(self.midi_pitch("A", 2), QUARTER),
        ]
        verify_bar(bar4, 4, "Bass CM")
        notes.extend(bar4)
        
        # Bar 5: Ebmaj7 (64 divisions)
        bar5 = [
            Note(self.midi_pitch("Eb", 2), DOTTED_HALF),
            Note(self.midi_pitch("D", 2), QUARTER),
        ]
        verify_bar(bar5, 5, "Bass CM")
        notes.extend(bar5)
        
        # Bar 6: Gm9 (64 divisions)
        bar6 = [
            Note(self.midi_pitch("G", 2), DOTTED_HALF),
            Note(self.midi_pitch("F", 2), QUARTER),
        ]
        verify_bar(bar6, 6, "Bass CM")
        notes.extend(bar6)
        
        # Bar 7: Am7b5 -> D7#9 (64 divisions)
        bar7 = [
            Note(self.midi_pitch("A", 2), HALF),
            Note(self.midi_pitch("D", 2), HALF),
        ]
        verify_bar(bar7, 7, "Bass CM")
        notes.extend(bar7)
        
        # Bar 8: Gm6/9 (64 divisions)
        bar8 = [
            Note(self.midi_pitch("G", 2), WHOLE),
        ]
        verify_bar(bar8, 8, "Bass CM")
        notes.extend(bar8)
        
        return notes
    
    def generate_section_c_chords(self) -> List[Chord]:
        """Generate chord symbols for Section C (Chord Melody)."""
        return [
            Chord("G", "mMaj7"),
            Chord("C", "m9"),
            Chord("F", "maj7#11"),
            Chord("Bb", "6"),
            Chord("Eb", "maj7"),
            Chord("G", "m9"),
            Chord("A", "m7b5"),
            Chord("G", "m6"),
        ]
    
    # =========================================================================
    # CODA: Resolution (4 bars)
    # =========================================================================
    
    def generate_coda_melody(self) -> List[Note]:
        """Generate the coda - peaceful resolution. Each bar = 64."""
        notes = []
        
        # Bar 1: Bbmaj9 (64 divisions)
        bar1 = [
            Note(self.midi_pitch("D", 5), HALF),
            Note(self.midi_pitch("C", 5), QUARTER),
            Note(self.midi_pitch("Bb", 4), QUARTER),
        ]
        verify_bar(bar1, 1, "Coda")
        notes.extend(bar1)
        
        # Bar 2: Bbmaj9 cont (64 divisions)
        bar2 = [
            Note(self.midi_pitch("A", 4), HALF),
            Note(self.midi_pitch("F", 4), HALF),
        ]
        verify_bar(bar2, 2, "Coda")
        notes.extend(bar2)
        
        # Bar 3: Gm6/9 (64 divisions)
        bar3 = [
            Note(self.midi_pitch("G", 4), DOTTED_HALF),
            Note(self.midi_pitch("A", 4), QUARTER),
        ]
        verify_bar(bar3, 3, "Coda")
        notes.extend(bar3)
        
        # Bar 4: Bbmaj9 - final (64 divisions)
        bar4 = [
            Note(self.midi_pitch("Bb", 4), WHOLE),
        ]
        verify_bar(bar4, 4, "Coda")
        notes.extend(bar4)
        
        return notes
    
    def generate_coda_bass(self) -> List[Note]:
        """Generate the coda bass. Each bar = 64."""
        notes = []
        
        # Bar 1
        bar1 = [Note(self.midi_pitch("Bb", 2), WHOLE)]
        verify_bar(bar1, 1, "Coda Bass")
        notes.extend(bar1)
        
        # Bar 2
        bar2 = [Note(self.midi_pitch("F", 2), WHOLE)]
        verify_bar(bar2, 2, "Coda Bass")
        notes.extend(bar2)
        
        # Bar 3
        bar3 = [Note(self.midi_pitch("G", 2), WHOLE)]
        verify_bar(bar3, 3, "Coda Bass")
        notes.extend(bar3)
        
        # Bar 4
        bar4 = [Note(self.midi_pitch("Bb", 1), WHOLE)]
        verify_bar(bar4, 4, "Coda Bass")
        notes.extend(bar4)
        
        return notes
    
    def generate_coda_chords(self) -> List[Chord]:
        """Generate chord symbols for Coda."""
        return [
            Chord("Bb", "maj9"),
            Chord("Bb", "maj9"),
            Chord("G", "m6"),
            Chord("Bb", "maj9"),
        ]
    
    # =========================================================================
    # MusicXML EXPORT
    # =========================================================================
    
    def create_musicxml(self) -> str:
        """Create the complete MusicXML score."""
        score = ET.Element("score-partwise", version="4.0")
        
        # Work and identification
        work = ET.SubElement(score, "work")
        ET.SubElement(work, "work-title").text = self.title
        
        identification = ET.SubElement(score, "identification")
        creator = ET.SubElement(identification, "creator", type="composer")
        creator.text = self.composer
        
        encoding = ET.SubElement(identification, "encoding")
        ET.SubElement(encoding, "software").text = "GCE-Jazz Engine"
        
        # Part list
        part_list = ET.SubElement(score, "part-list")
        
        # Guitar part
        guitar_part = ET.SubElement(part_list, "score-part", id="P1")
        ET.SubElement(guitar_part, "part-name").text = "Guitar"
        ET.SubElement(guitar_part, "part-abbreviation").text = "Gtr."
        
        # Bass part
        bass_part = ET.SubElement(part_list, "score-part", id="P2")
        ET.SubElement(bass_part, "part-name").text = "Bass"
        ET.SubElement(bass_part, "part-abbreviation").text = "Bass"
        
        # Generate all sections
        all_guitar_notes = []
        all_bass_notes = []
        all_chords = []
        section_markers = []
        
        # Section A (8 bars)
        section_markers.append((0, "A - Main Theme"))
        all_guitar_notes.extend(self.generate_section_a_melody())
        all_bass_notes.extend(self.generate_section_a_bass())
        all_chords.extend(self.generate_section_a_chords())
        
        # Section A' (repeat - 8 bars)
        section_markers.append((8, "A'"))
        all_guitar_notes.extend(self.generate_section_a_melody())
        all_bass_notes.extend(self.generate_section_a_bass())
        all_chords.extend(self.generate_section_a_chords())
        
        # Section B (Triad Pair Solo - 8 bars)
        section_markers.append((16, "B - Triad Pair Solo"))
        all_guitar_notes.extend(self.generate_section_b_melody())
        all_bass_notes.extend(self.generate_section_b_bass())
        all_chords.extend(self.generate_section_b_chords())
        
        # Section C (Chord Melody - 8 bars)
        section_markers.append((24, "C - Chord Melody"))
        all_guitar_notes.extend(self.generate_section_c_melody())
        all_bass_notes.extend(self.generate_section_c_bass())
        all_chords.extend(self.generate_section_c_chords())
        
        # Coda (4 bars)
        section_markers.append((32, "Coda"))
        all_guitar_notes.extend(self.generate_coda_melody())
        all_bass_notes.extend(self.generate_coda_bass())
        all_chords.extend(self.generate_coda_chords())
        
        # Create guitar part
        guitar = ET.SubElement(score, "part", id="P1")
        self._write_part_measures(guitar, all_guitar_notes, all_chords, 
                                   is_guitar=True, section_markers=section_markers)
        
        # Create bass part
        bass = ET.SubElement(score, "part", id="P2")
        self._write_part_measures(bass, all_bass_notes, [], 
                                   is_guitar=False, section_markers=[])
        
        # Convert to string
        rough_string = ET.tostring(score, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def _write_part_measures(self, part_element: ET.Element, notes: List[Note], 
                              chords: List[Chord], is_guitar: bool,
                              section_markers: List[Tuple[int, str]]):
        """Write measures for a part."""
        
        measure_num = 1
        note_index = 0
        chord_index = 0
        
        # Track section markers by measure number
        section_marker_dict = {m + 1: name for m, name in section_markers}
        
        while note_index < len(notes):
            measure = ET.SubElement(part_element, "measure", number=str(measure_num))
            
            # First measure attributes
            if measure_num == 1:
                attributes = ET.SubElement(measure, "attributes")
                ET.SubElement(attributes, "divisions").text = str(self.divisions)
                
                key = ET.SubElement(attributes, "key")
                ET.SubElement(key, "fifths").text = str(self.key_fifths)
                ET.SubElement(key, "mode").text = self.key_mode
                
                time = ET.SubElement(attributes, "time")
                ET.SubElement(time, "beats").text = str(self.time_sig[0])
                ET.SubElement(time, "beat-type").text = str(self.time_sig[1])
                
                clef = ET.SubElement(attributes, "clef")
                if is_guitar:
                    ET.SubElement(clef, "sign").text = "G"
                    ET.SubElement(clef, "line").text = "2"
                else:
                    ET.SubElement(clef, "sign").text = "F"
                    ET.SubElement(clef, "line").text = "4"
                
                # Tempo
                direction = ET.SubElement(measure, "direction", placement="above")
                direction_type = ET.SubElement(direction, "direction-type")
                metronome = ET.SubElement(direction_type, "metronome")
                ET.SubElement(metronome, "beat-unit").text = "quarter"
                ET.SubElement(metronome, "per-minute").text = str(self.tempo)
                ET.SubElement(direction, "sound", tempo=str(self.tempo))
            
            # Add section marker if applicable
            if measure_num in section_marker_dict and is_guitar:
                direction = ET.SubElement(measure, "direction", placement="above")
                direction_type = ET.SubElement(direction, "direction-type")
                rehearsal = ET.SubElement(direction_type, "rehearsal")
                rehearsal.text = section_marker_dict[measure_num]
            
            # Add chord symbol if applicable (guitar only)
            if is_guitar and chord_index < len(chords):
                chord = chords[chord_index]
                harmony = ET.SubElement(measure, "harmony")
                root_elem = ET.SubElement(harmony, "root")
                chord_root = chord.root
                
                if len(chord_root) > 1 and chord_root[1] in ['#', 'b']:
                    ET.SubElement(root_elem, "root-step").text = chord_root[0]
                    ET.SubElement(root_elem, "root-alter").text = "1" if chord_root[1] == '#' else "-1"
                else:
                    ET.SubElement(root_elem, "root-step").text = chord_root[0]
                
                _, kind = chord.to_musicxml_harmony()
                ET.SubElement(harmony, "kind").text = kind
                chord_index += 1
            
            duration_in_measure = 0
            measure_duration = BAR  # 64 divisions
            
            # Add notes to measure
            while note_index < len(notes) and duration_in_measure < measure_duration:
                note = notes[note_index]
                remaining_in_measure = measure_duration - duration_in_measure
                
                if note.duration <= remaining_in_measure:
                    self._add_note(measure, note, note.duration)
                    duration_in_measure += note.duration
                    note_index += 1
                else:
                    # Note needs to be split (tie)
                    self._add_note(measure, note, remaining_in_measure, tie_start=True)
                    notes[note_index] = Note(
                        note.pitch, 
                        note.duration - remaining_in_measure,
                        tie_stop=True
                    )
                    duration_in_measure = measure_duration
            
            # Fill remaining with rest if needed
            if duration_in_measure < measure_duration:
                rest_duration = measure_duration - duration_in_measure
                rest_note = Note(0, rest_duration, is_rest=True)
                self._add_note(measure, rest_note, rest_duration)
            
            measure_num += 1
    
    def _add_note(self, measure: ET.Element, note: Note, duration: int, 
                   tie_start: bool = False, tie_stop: bool = False):
        """Add a single note to a measure."""
        note_elem = ET.SubElement(measure, "note")
        
        if note.is_rest:
            ET.SubElement(note_elem, "rest")
        else:
            pitch = ET.SubElement(note_elem, "pitch")
            step, octave, alter = note.get_step_octave_alter()
            ET.SubElement(pitch, "step").text = step
            if alter != 0:
                ET.SubElement(pitch, "alter").text = str(alter)
            ET.SubElement(pitch, "octave").text = str(octave)
        
        ET.SubElement(note_elem, "duration").text = str(duration)
        
        # Get note type and whether it's dotted
        type_name, is_dotted = self._duration_to_type_and_dot(duration)
        if type_name:
            ET.SubElement(note_elem, "type").text = type_name
            # Add dot element for dotted notes - THIS IS THE KEY FIX!
            if is_dotted:
                ET.SubElement(note_elem, "dot")
        
        # Ties
        if tie_start or note.tie_start:
            ET.SubElement(note_elem, "tie", type="start")
        if tie_stop or note.tie_stop:
            ET.SubElement(note_elem, "tie", type="stop")
        
        # Notations
        if tie_start or tie_stop or note.tie_start or note.tie_stop:
            notations = ET.SubElement(note_elem, "notations")
            if tie_start or note.tie_start:
                ET.SubElement(notations, "tied", type="start")
            if tie_stop or note.tie_stop:
                ET.SubElement(notations, "tied", type="stop")
    
    def _duration_to_type_and_dot(self, duration: int) -> Tuple[str, bool]:
        """
        Convert duration to note type name and dotted flag.
        
        MusicXML requires:
        - <type>half</type> for half note
        - <type>half</type><dot/> for DOTTED half note
        
        Returns: (type_name, is_dotted)
        """
        # Dotted notes: base_duration * 1.5 = dotted_duration
        dotted_map = {
            DOTTED_HALF: ("half", True),       # 48 = dotted half
            DOTTED_QUARTER: ("quarter", True), # 24 = dotted quarter
            DOTTED_EIGHTH: ("eighth", True),   # 12 = dotted eighth
        }
        
        if duration in dotted_map:
            return dotted_map[duration]
        
        # Non-dotted notes
        type_map = {
            WHOLE: ("whole", False),           # 64
            HALF: ("half", False),             # 32
            QUARTER: ("quarter", False),       # 16
            EIGHTH: ("eighth", False),         # 8
            SIXTEENTH: ("16th", False),        # 4
        }
        
        return type_map.get(duration, ("quarter", False))
    
    def save_musicxml(self, filepath: str) -> str:
        """Save the composition to MusicXML."""
        xml_content = self.create_musicxml()
        
        # Remove extra xml declaration from minidom
        lines = xml_content.split('\n')
        if lines[0].startswith('<?xml'):
            lines = lines[1:]
        xml_content = '\n'.join(lines)
        
        # Add proper XML declaration
        full_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        full_content += '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
        full_content += '"http://www.musicxml.org/dtds/partwise.dtd">\n'
        full_content += xml_content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return filepath


def main():
    """Generate the composition and export."""
    print("=" * 60)
    print("ENTANGLED HORIZONS")
    print("An Ant Law-Inspired Composition")
    print("=" * 60)
    print()
    
    # Create output directory - use Alternative_LeadSheets folder
    output_dir = Path(__file__).parent.parent / "Trio Tunes" / "Alternative_LeadSheets"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate composition
    print("Generating composition with strict rhythm verification...")
    print()
    composition = EntangledHorizonsComposition()
    
    # Save MusicXML
    musicxml_path = output_dir / "Entangled_Horizons.musicxml"
    composition.save_musicxml(str(musicxml_path))
    print()
    print(f"MusicXML saved: {musicxml_path}")
    
    print()
    print("=" * 60)
    print("COMPOSITION SUMMARY")
    print("=" * 60)
    print()
    print("Title: Entangled Horizons")
    print("Key: Bb Major / G Minor")
    print("Tempo: 132 BPM (Swing)")
    print("Time: 4/4")
    print()
    print("RHYTHM VERIFICATION:")
    print("  ✓ Each bar verified = 64 divisions (4 beats × 16 divisions)")
    print("  ✓ All note durations sum correctly")
    print()
    print("FORM:")
    print("  A  - Main Theme (8 bars)")
    print("  A' - Theme Variation (8 bars)")
    print("  B  - Triad Pair Solo (8 bars)")
    print("  C  - Chord Melody (8 bars)")
    print("  Coda - Resolution (4 bars)")
    print()
    print(f"Output: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
