"""
5x-Orbit Lead Sheets A/B/C/D — Wayne Shorter Style
====================================================

MASTER GENERATION: Four distinct 16-bar lead sheet realisations
- A: Lyrical (the tune itself)
- B: Modern Triad Pairs (architectural)
- C: Counterpoint (linear independence)
- D: Hybrid (integration model)

Key: F Major | Tempo: 160 BPM | Time: 3/4
Style: Wayne Shorter (post-1965, non-functional, melodic-first)

NO chord symbols printed. NO tab. Prioritise space, sustain, wide intervals.
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

MIDI_TO_NOTE_FLAT = {
    0: ("C", 0), 1: ("D", -1), 2: ("D", 0), 3: ("E", -1),
    4: ("E", 0), 5: ("F", 0), 6: ("G", -1), 7: ("G", 0),
    8: ("A", -1), 9: ("A", 0), 10: ("B", -1), 11: ("B", 0)
}

# 3/4 time: 48 divisions per bar (16 per quarter * 3 quarters)
DIVISIONS = 16
BAR = 48  # 3/4 time

DOTTED_HALF = 48
HALF = 32
DOTTED_QUARTER = 24
QUARTER = 16
DOTTED_EIGHTH = 12
EIGHTH = 8
SIXTEENTH = 4


@dataclass
class Note:
    pitch: int  # MIDI pitch
    duration: int
    is_rest: bool = False
    tied_start: bool = False
    tied_stop: bool = False

    def get_xml_pitch(self, use_flats: bool = True) -> Tuple[str, int, int]:
        if self.is_rest:
            return ("C", 4, 0)
        octave = (self.pitch // 12) - 1
        pc = self.pitch % 12
        lookup = MIDI_TO_NOTE_FLAT if use_flats else MIDI_TO_NOTE_SHARP
        step, alter = lookup[pc]
        return (step, octave, alter)


def p(note: str, octave: int) -> int:
    """Convert note name and octave to MIDI pitch. Octave lowered for guitar range."""
    return NOTE_TO_MIDI[note] + octave * 12  # Removed +1 to lower by octave


def n(note: str, octave: int, duration: int) -> Note:
    """Create a note."""
    return Note(p(note, octave), duration)


def r(duration: int) -> Note:
    """Create a rest."""
    return Note(0, duration, is_rest=True)


def tie_start(note: str, octave: int, duration: int) -> Note:
    """Create a note that starts a tie."""
    return Note(p(note, octave), duration, tied_start=True)


def tie_stop(note: str, octave: int, duration: int) -> Note:
    """Create a note that stops a tie."""
    return Note(p(note, octave), duration, tied_stop=True)


def verify_bar(items: List[Note], bar_num: int, section: str) -> bool:
    """Verify bar sums to 48 divisions (3/4 time)."""
    total = sum(item.duration for item in items)
    ok = "[OK]" if total == BAR else "[FAIL]"
    print(f"  {ok} {section} Bar {bar_num}: {total}/48")
    return total == BAR


# ============================================================================
# VERSION A: LYRICAL — The tune itself
# ============================================================================

def generate_version_a() -> List[List[Note]]:
    """
    Lyrical: Sparse, singing melody. Long tones, ties across barlines.
    Emphasis on intervallic contour (6ths, 7ths, 9ths). Frequent space.
    """
    bars = []
    
    # Bar 1: Fmaj7#11 - Open with space, ascending 6th
    bar1 = [n("A", 4, HALF), r(QUARTER), n("F", 5, QUARTER)]  # 32+16=48? No, need to fix
    # Actually: half=32, quarter=16 → 32+16+16=64 too much. 
    # For 3/4: we need 48. half=32, quarter=16 → 32+16=48 ✓
    bar1 = [n("A", 4, HALF), n("F", 5, QUARTER)]  # Rising 6th, let it breathe
    verify_bar(bar1, 1, "A")
    bars.append(bar1)
    
    # Bar 2: Ebmaj7#5 - Sustain into silence
    bar2 = [n("G", 5, DOTTED_HALF)]  # Hold the maj7
    verify_bar(bar2, 2, "A")
    bars.append(bar2)
    
    # Bar 3: Dbmaj7 - Descending, wide interval
    bar3 = [r(QUARTER), n("Ab", 5, QUARTER), n("C", 5, QUARTER)]  # Space, then drop
    verify_bar(bar3, 3, "A")
    bars.append(bar3)
    
    # Bar 4: Bmaj7 - Lydian color
    bar4 = [n("D#", 5, HALF), r(QUARTER)]  # #11 of B, then breathe
    verify_bar(bar4, 4, "A")
    bars.append(bar4)
    
    # Bar 5: Bbm9 - Minor color, sustained
    bar5 = [n("C", 5, DOTTED_QUARTER), n("Db", 5, DOTTED_QUARTER)]  # 9th to b3
    verify_bar(bar5, 5, "A")
    bars.append(bar5)
    
    # Bar 6: Abmaj7 - Wide leap up
    bar6 = [n("Eb", 4, QUARTER), r(QUARTER), n("G", 5, QUARTER)]  # Low to high
    verify_bar(bar6, 6, "A")
    bars.append(bar6)
    
    # Bar 7: Gbmaj7 - Sustain the float
    bar7 = [n("F", 5, DOTTED_HALF)]  # Maj7 of Gb
    verify_bar(bar7, 7, "A")
    bars.append(bar7)
    
    # Bar 8: Emaj7 - Resolve to 5th
    bar8 = [n("B", 4, HALF), n("G#", 4, QUARTER)]  # 5th down to 3rd
    verify_bar(bar8, 8, "A")
    bars.append(bar8)
    
    # Bar 9: Fmaj7#11 - Return, restate motif
    bar9 = [r(QUARTER), n("E", 5, HALF)]  # Maj7, space first
    verify_bar(bar9, 9, "A")
    bars.append(bar9)
    
    # Bar 10: Dbmaj7 - Continue floating
    bar10 = [n("C", 5, QUARTER), n("Ab", 4, HALF)]  # 7th down to 5th
    verify_bar(bar10, 10, "A")
    bars.append(bar10)
    
    # Bar 11: Amaj7 - Bright Lydian
    bar11 = [n("G#", 5, DOTTED_QUARTER), r(DOTTED_QUARTER)]  # Maj7, then space
    verify_bar(bar11, 11, "A")
    bars.append(bar11)
    
    # Bar 12: Gmaj7 - Descend
    bar12 = [n("F#", 5, QUARTER), n("D", 5, QUARTER), n("B", 4, QUARTER)]  # 7-5-3
    verify_bar(bar12, 12, "A")
    bars.append(bar12)
    
    # Bar 13: Fmaj7#11 - Home, opening gesture
    bar13 = [n("A", 4, HALF), n("E", 5, QUARTER)]  # 3rd to 7th
    verify_bar(bar13, 13, "A")
    bars.append(bar13)
    
    # Bar 14: Ebm9 - Minor shift, contrast
    bar14 = [n("F", 5, DOTTED_HALF)]  # 9th of Eb minor
    verify_bar(bar14, 14, "A")
    bars.append(bar14)
    
    # Bar 15: Dbmaj7 - Penultimate, tension
    bar15 = [n("C", 5, QUARTER), r(QUARTER), n("Ab", 5, QUARTER)]
    verify_bar(bar15, 15, "A")
    bars.append(bar15)
    
    # Bar 16: Fmaj7 - Home, final sustain
    bar16 = [n("A", 5, DOTTED_HALF)]  # End on 3rd, singing
    verify_bar(bar16, 16, "A")
    bars.append(bar16)
    
    return bars


# ============================================================================
# VERSION B: MODERN TRIAD PAIRS — Architectural
# ============================================================================

def generate_version_b() -> List[List[Note]]:
    """
    Modern Triad Pairs: Continuous or near-continuous 8ths.
    Strict triad-pair logic. Angular, non-scalar, non-bebop.
    Momentum without cadence.
    """
    bars = []
    
    # Bar 1: Fmaj7#11 - F/G triad pair (Lydian)
    # F-A-C / G-B-D arpeggiated
    bar1 = [
        n("F", 4, EIGHTH), n("A", 4, EIGHTH), n("C", 5, EIGHTH),
        n("G", 4, EIGHTH), n("B", 4, EIGHTH), n("D", 5, EIGHTH)
    ]
    verify_bar(bar1, 1, "B")
    bars.append(bar1)
    
    # Bar 2: Ebmaj7#5 - Eb aug / Bb triad pair
    bar2 = [
        n("Eb", 4, EIGHTH), n("G", 4, EIGHTH), n("B", 4, EIGHTH),
        n("Bb", 4, EIGHTH), n("D", 5, EIGHTH), n("F", 5, EIGHTH)
    ]
    verify_bar(bar2, 2, "B")
    bars.append(bar2)
    
    # Bar 3: Dbmaj7 - Db/Eb triad pair
    bar3 = [
        n("Db", 4, EIGHTH), n("F", 4, EIGHTH), n("Ab", 4, EIGHTH),
        n("Eb", 4, EIGHTH), n("G", 4, EIGHTH), n("Bb", 4, EIGHTH)
    ]
    verify_bar(bar3, 3, "B")
    bars.append(bar3)
    
    # Bar 4: Bmaj7 - B/C# triad pair
    bar4 = [
        n("B", 3, EIGHTH), n("D#", 4, EIGHTH), n("F#", 4, EIGHTH),
        n("C#", 4, EIGHTH), n("F", 4, EIGHTH), n("G#", 4, EIGHTH)  # E# = F enharmonic
    ]
    verify_bar(bar4, 4, "B")
    bars.append(bar4)
    
    # Bar 5: Bbm9 - Db/Ab triad pair (Dorian)
    bar5 = [
        n("Db", 4, EIGHTH), n("F", 4, EIGHTH), n("Ab", 4, EIGHTH),
        n("Ab", 3, EIGHTH), n("C", 4, EIGHTH), n("Eb", 4, EIGHTH)
    ]
    verify_bar(bar5, 5, "B")
    bars.append(bar5)
    
    # Bar 6: Abmaj7 - Ab/Bb triad pair
    bar6 = [
        n("Ab", 4, EIGHTH), n("C", 5, EIGHTH), n("Eb", 5, EIGHTH),
        n("Bb", 4, EIGHTH), n("D", 5, EIGHTH), n("F", 5, EIGHTH)
    ]
    verify_bar(bar6, 6, "B")
    bars.append(bar6)
    
    # Bar 7: Gbmaj7 - Gb/Ab triad pair
    bar7 = [
        n("Gb", 4, EIGHTH), n("Bb", 4, EIGHTH), n("Db", 5, EIGHTH),
        n("Ab", 4, EIGHTH), n("C", 5, EIGHTH), n("Eb", 5, EIGHTH)
    ]
    verify_bar(bar7, 7, "B")
    bars.append(bar7)
    
    # Bar 8: Emaj7 - E/F# triad pair
    bar8 = [
        n("E", 4, EIGHTH), n("G#", 4, EIGHTH), n("B", 4, EIGHTH),
        n("F#", 4, EIGHTH), n("A#", 4, EIGHTH), n("C#", 5, EIGHTH)
    ]
    verify_bar(bar8, 8, "B")
    bars.append(bar8)
    
    # Bar 9: Fmaj7#11 - Ascending through F/G
    bar9 = [
        n("G", 4, EIGHTH), n("B", 4, EIGHTH), n("D", 5, EIGHTH),
        n("F", 5, EIGHTH), n("A", 5, EIGHTH), n("C", 6, EIGHTH)
    ]
    verify_bar(bar9, 9, "B")
    bars.append(bar9)
    
    # Bar 10: Dbmaj7 - Descending Db/Eb
    bar10 = [
        n("Bb", 5, EIGHTH), n("G", 5, EIGHTH), n("Eb", 5, EIGHTH),
        n("Ab", 5, EIGHTH), n("F", 5, EIGHTH), n("Db", 5, EIGHTH)
    ]
    verify_bar(bar10, 10, "B")
    bars.append(bar10)
    
    # Bar 11: Amaj7 - A/B triad pair
    bar11 = [
        n("A", 4, EIGHTH), n("C#", 5, EIGHTH), n("E", 5, EIGHTH),
        n("B", 4, EIGHTH), n("D#", 5, EIGHTH), n("F#", 5, EIGHTH)
    ]
    verify_bar(bar11, 11, "B")
    bars.append(bar11)
    
    # Bar 12: Gmaj7 - G/A triad pair
    bar12 = [
        n("G", 4, EIGHTH), n("B", 4, EIGHTH), n("D", 5, EIGHTH),
        n("A", 4, EIGHTH), n("C#", 5, EIGHTH), n("E", 5, EIGHTH)
    ]
    verify_bar(bar12, 12, "B")
    bars.append(bar12)
    
    # Bar 13: Fmaj7#11 - Angular return
    bar13 = [
        n("B", 4, EIGHTH), n("F", 5, EIGHTH), n("A", 4, EIGHTH),
        n("D", 5, EIGHTH), n("G", 4, EIGHTH), n("C", 5, EIGHTH)
    ]
    verify_bar(bar13, 13, "B")
    bars.append(bar13)
    
    # Bar 14: Ebm9 - Gb/Db triad pair (Dorian)
    bar14 = [
        n("Gb", 4, EIGHTH), n("Bb", 4, EIGHTH), n("Db", 5, EIGHTH),
        n("Db", 4, EIGHTH), n("F", 4, EIGHTH), n("Ab", 4, EIGHTH)
    ]
    verify_bar(bar14, 14, "B")
    bars.append(bar14)
    
    # Bar 15: Dbmaj7 - Building to end
    bar15 = [
        n("Db", 5, EIGHTH), n("F", 5, EIGHTH), n("Ab", 5, EIGHTH),
        n("Eb", 5, EIGHTH), n("G", 5, EIGHTH), n("Bb", 5, EIGHTH)
    ]
    verify_bar(bar15, 15, "B")
    bars.append(bar15)
    
    # Bar 16: Fmaj7 - Final angular gesture
    bar16 = [
        n("C", 5, EIGHTH), n("F", 5, EIGHTH), n("A", 5, EIGHTH),
        n("E", 5, EIGHTH), n("B", 4, EIGHTH), n("G", 4, EIGHTH)
    ]
    verify_bar(bar16, 16, "B")
    bars.append(bar16)
    
    return bars


# ============================================================================
# VERSION C: COUNTERPOINT — Linear Independence
# ============================================================================

def generate_version_c() -> List[List[Tuple[Note, Optional[Note]]]]:
    """
    Counterpoint: Two independent melodic voices.
    Contrary or oblique motion preferred. Clear registral separation.
    Returns list of bars, each containing (top_voice, bottom_voice) tuples.
    """
    bars = []
    
    # Bar 1: Fmaj7#11 - Contrary motion
    bar1 = [
        (n("A", 5, QUARTER), n("C", 4, QUARTER)),  # Top up, bottom stays
        (n("B", 5, QUARTER), n("A", 3, QUARTER)),  # Top up, bottom down
        (n("C", 6, QUARTER), n("F", 3, QUARTER)),  # Wide spread
    ]
    bars.append(bar1)
    
    # Bar 2: Ebmaj7#5 - Oblique motion
    bar2 = [
        (n("G", 5, HALF), n("Eb", 4, QUARTER)),  # Top holds
        (None, n("G", 4, QUARTER)),  # Top continues, bottom moves
    ]
    bars.append(bar2)
    
    # Bar 3: Dbmaj7 - Contrary
    bar3 = [
        (n("F", 5, QUARTER), n("Ab", 4, QUARTER)),
        (n("Eb", 5, QUARTER), n("Bb", 4, QUARTER)),  # Top down, bottom up
        (n("C", 5, QUARTER), n("Db", 5, QUARTER)),  # Converge
    ]
    bars.append(bar3)
    
    # Bar 4: Bmaj7 - Wide separation
    bar4 = [
        (n("D#", 6, DOTTED_QUARTER), n("B", 3, DOTTED_QUARTER)),
        (n("F#", 5, DOTTED_QUARTER), n("G#", 3, DOTTED_QUARTER)),
    ]
    bars.append(bar4)
    
    # Bar 5: Bbm9 - Minor color, contrary
    bar5 = [
        (n("Db", 5, QUARTER), n("Bb", 4, QUARTER)),
        (n("C", 5, QUARTER), n("C", 4, QUARTER)),  # Octave
        (n("Bb", 4, QUARTER), n("Db", 4, QUARTER)),  # Cross
    ]
    bars.append(bar5)
    
    # Bar 6: Abmaj7 - Oblique
    bar6 = [
        (n("Eb", 5, HALF), n("Ab", 3, QUARTER)),
        (None, n("C", 4, QUARTER)),
    ]
    bars.append(bar6)
    
    # Bar 7: Gbmaj7 - Wide spread, sustained
    bar7 = [
        (n("F", 5, DOTTED_HALF), n("Gb", 3, DOTTED_HALF)),
    ]
    bars.append(bar7)
    
    # Bar 8: Emaj7 - Contrary resolution
    bar8 = [
        (n("G#", 5, QUARTER), n("E", 4, QUARTER)),
        (n("F#", 5, QUARTER), n("G#", 4, QUARTER)),  # Top down, bottom up
        (n("E", 5, QUARTER), n("B", 4, QUARTER)),
    ]
    bars.append(bar8)
    
    # Bar 9: Fmaj7#11 - Return
    bar9 = [
        (n("E", 5, HALF), n("F", 4, HALF)),
        (n("F", 5, QUARTER), n("A", 4, QUARTER)),
    ]
    bars.append(bar9)
    
    # Bar 10: Dbmaj7 - Contrary motion
    bar10 = [
        (n("C", 6, QUARTER), n("Db", 4, QUARTER)),
        (n("Ab", 5, QUARTER), n("F", 4, QUARTER)),  # Both down/up
        (n("F", 5, QUARTER), n("Ab", 4, QUARTER)),
    ]
    bars.append(bar10)
    
    # Bar 11: Amaj7 - Oblique
    bar11 = [
        (n("G#", 5, DOTTED_HALF), n("A", 4, QUARTER)),
        (None, n("E", 4, QUARTER)),
        (None, n("C#", 4, QUARTER)),
    ]
    bars.append(bar11)
    
    # Bar 12: Gmaj7 - Parallel 5ths (medieval touch)
    bar12 = [
        (n("D", 5, QUARTER), n("G", 4, QUARTER)),  # P5
        (n("E", 5, QUARTER), n("A", 4, QUARTER)),  # P5
        (n("F#", 5, QUARTER), n("B", 4, QUARTER)),  # P5
    ]
    bars.append(bar12)
    
    # Bar 13: Fmaj7#11 - Wide return
    bar13 = [
        (n("B", 5, HALF), n("F", 3, HALF)),  # Tritone spread
        (n("A", 5, QUARTER), n("A", 3, QUARTER)),  # Octave
    ]
    bars.append(bar13)
    
    # Bar 14: Ebm9 - Minor, contrary
    bar14 = [
        (n("Gb", 5, QUARTER), n("Eb", 4, QUARTER)),
        (n("F", 5, QUARTER), n("Gb", 4, QUARTER)),
        (n("Eb", 5, QUARTER), n("Bb", 4, QUARTER)),
    ]
    bars.append(bar14)
    
    # Bar 15: Dbmaj7 - Building
    bar15 = [
        (n("Ab", 5, QUARTER), n("Db", 4, QUARTER)),
        (n("Bb", 5, QUARTER), n("C", 4, QUARTER)),
        (n("C", 6, QUARTER), n("Db", 4, QUARTER)),
    ]
    bars.append(bar15)
    
    # Bar 16: Fmaj7 - Final convergence
    bar16 = [
        (n("A", 5, DOTTED_HALF), n("F", 4, DOTTED_HALF)),  # 3rd and root
    ]
    bars.append(bar16)
    
    return bars


# ============================================================================
# VERSION D: HYBRID — Integration Model
# ============================================================================

def generate_version_d() -> List[List]:
    """
    Hybrid: Combines lyrical fragments, triad-pair passages, and counterpoint.
    Texture shifts within the 16 bars. Seamless transitions.
    """
    bars = []
    
    # Bars 1-4: LYRICAL opening
    # Bar 1: Fmaj7#11
    bar1 = [n("A", 4, HALF), n("E", 5, QUARTER)]
    verify_bar(bar1, 1, "D")
    bars.append(("lyrical", bar1))
    
    # Bar 2: Ebmaj7#5
    bar2 = [n("G", 5, DOTTED_HALF)]
    verify_bar(bar2, 2, "D")
    bars.append(("lyrical", bar2))
    
    # Bar 3: Dbmaj7
    bar3 = [r(QUARTER), n("C", 5, HALF)]
    verify_bar(bar3, 3, "D")
    bars.append(("lyrical", bar3))
    
    # Bar 4: Bmaj7 - transition
    bar4 = [n("D#", 5, QUARTER), n("F#", 5, QUARTER), n("B", 4, QUARTER)]
    verify_bar(bar4, 4, "D")
    bars.append(("lyrical", bar4))
    
    # Bars 5-8: TRIAD PAIRS (architectural)
    # Bar 5: Bbm9
    bar5 = [
        n("Db", 4, EIGHTH), n("F", 4, EIGHTH), n("Ab", 4, EIGHTH),
        n("Bb", 4, EIGHTH), n("Db", 5, EIGHTH), n("F", 5, EIGHTH)
    ]
    verify_bar(bar5, 5, "D")
    bars.append(("triads", bar5))
    
    # Bar 6: Abmaj7
    bar6 = [
        n("Ab", 4, EIGHTH), n("C", 5, EIGHTH), n("Eb", 5, EIGHTH),
        n("Bb", 4, EIGHTH), n("D", 5, EIGHTH), n("F", 5, EIGHTH)
    ]
    verify_bar(bar6, 6, "D")
    bars.append(("triads", bar6))
    
    # Bar 7: Gbmaj7
    bar7 = [
        n("Gb", 4, EIGHTH), n("Bb", 4, EIGHTH), n("Db", 5, EIGHTH),
        n("Ab", 4, EIGHTH), n("C", 5, EIGHTH), n("Eb", 5, EIGHTH)
    ]
    verify_bar(bar7, 7, "D")
    bars.append(("triads", bar7))
    
    # Bar 8: Emaj7 - transitioning out
    bar8 = [
        n("E", 4, EIGHTH), n("G#", 4, EIGHTH), n("B", 4, EIGHTH),
        n("G#", 4, QUARTER), r(EIGHTH)
    ]
    verify_bar(bar8, 8, "D")
    bars.append(("triads", bar8))
    
    # Bars 9-12: COUNTERPOINT (two voices)
    # Bar 9: Fmaj7#11
    bar9 = [
        (n("E", 5, HALF), n("F", 4, HALF)),
        (n("A", 5, QUARTER), n("C", 4, QUARTER)),
    ]
    bars.append(("counterpoint", bar9))
    
    # Bar 10: Dbmaj7
    bar10 = [
        (n("Ab", 5, QUARTER), n("Db", 4, QUARTER)),
        (n("F", 5, QUARTER), n("F", 4, QUARTER)),
        (n("C", 5, QUARTER), n("Ab", 4, QUARTER)),
    ]
    bars.append(("counterpoint", bar10))
    
    # Bar 11: Amaj7
    bar11 = [
        (n("G#", 5, QUARTER), n("A", 4, QUARTER)),
        (n("E", 5, QUARTER), n("C#", 4, QUARTER)),
        (n("C#", 5, QUARTER), n("E", 4, QUARTER)),
    ]
    bars.append(("counterpoint", bar11))
    
    # Bar 12: Gmaj7 - parallel 5ths ending
    bar12 = [
        (n("D", 5, QUARTER), n("G", 4, QUARTER)),
        (n("B", 4, HALF), n("E", 4, HALF)),
    ]
    bars.append(("counterpoint", bar12))
    
    # Bars 13-16: LYRICAL return with embellishment
    # Bar 13: Fmaj7#11
    bar13 = [n("A", 4, DOTTED_QUARTER), n("B", 4, EIGHTH), n("A", 5, QUARTER)]
    verify_bar(bar13, 13, "D")
    bars.append(("lyrical", bar13))
    
    # Bar 14: Ebm9
    bar14 = [n("Gb", 5, HALF), n("F", 5, QUARTER)]
    verify_bar(bar14, 14, "D")
    bars.append(("lyrical", bar14))
    
    # Bar 15: Dbmaj7
    bar15 = [n("Eb", 5, QUARTER), r(QUARTER), n("Ab", 5, QUARTER)]
    verify_bar(bar15, 15, "D")
    bars.append(("lyrical", bar15))
    
    # Bar 16: Fmaj7 - final sustain
    bar16 = [n("A", 5, DOTTED_HALF)]
    verify_bar(bar16, 16, "D")
    bars.append(("lyrical", bar16))
    
    return bars


# ============================================================================
# MUSICXML GENERATION
# ============================================================================

class OrbitMusicXMLGenerator:
    def __init__(self, version: str, title_suffix: str):
        self.version = version
        self.title = f"Orbit ({version}) – {title_suffix}"
        self.divisions = DIVISIONS
        
    def get_duration_type(self, dur: int) -> Tuple[str, bool]:
        """Return (type_name, is_dotted)."""
        if dur == DOTTED_HALF:
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
        """Add a note element to a measure."""
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
        
        if note.tied_start:
            tie = ET.SubElement(note_elem, "tie")
            tie.set("type", "start")
        if note.tied_stop:
            tie = ET.SubElement(note_elem, "tie")
            tie.set("type", "stop")
    
    def create_part(self, part_elem: ET.Element, bars: List):
        """Create part content from bars."""
        for bar_num, bar_data in enumerate(bars, 1):
            measure = ET.SubElement(part_elem, "measure")
            measure.set("number", str(bar_num))
            
            # Add attributes for first measure
            if bar_num == 1:
                attrs = ET.SubElement(measure, "attributes")
                ET.SubElement(attrs, "divisions").text = str(self.divisions)
                
                key = ET.SubElement(attrs, "key")
                ET.SubElement(key, "fifths").text = "-1"  # F major (1 flat)
                ET.SubElement(key, "mode").text = "major"
                
                time = ET.SubElement(attrs, "time")
                ET.SubElement(time, "beats").text = "3"
                ET.SubElement(time, "beat-type").text = "4"
                
                clef = ET.SubElement(attrs, "clef")
                ET.SubElement(clef, "sign").text = "G"
                ET.SubElement(clef, "line").text = "2"
                ET.SubElement(clef, "clef-octave-change").text = "-1"  # Guitar octave down
                
                # Add tempo
                direction = ET.SubElement(measure, "direction")
                direction.set("placement", "above")
                dir_type = ET.SubElement(direction, "direction-type")
                metro = ET.SubElement(dir_type, "metronome")
                ET.SubElement(metro, "beat-unit").text = "quarter"
                ET.SubElement(metro, "per-minute").text = "160"
                sound = ET.SubElement(direction, "sound")
                sound.set("tempo", "160")
            
            # Handle different bar formats
            if isinstance(bar_data, tuple) and bar_data[0] in ("lyrical", "triads", "counterpoint"):
                # Version D hybrid format
                mode, notes = bar_data
                if mode == "counterpoint":
                    # Two voices
                    for pair in notes:
                        if isinstance(pair, tuple):
                            top, bottom = pair
                            if top:
                                self.add_note_element(measure, top, voice=1)
                            if bottom:
                                self.add_note_element(measure, bottom, is_chord=bool(top), voice=2)
                else:
                    # Single voice
                    for note in notes:
                        self.add_note_element(measure, note)
            elif isinstance(bar_data, list) and len(bar_data) > 0:
                if isinstance(bar_data[0], tuple):
                    # Version C counterpoint format
                    for pair in bar_data:
                        if isinstance(pair, tuple):
                            top, bottom = pair
                            if top:
                                self.add_note_element(measure, top, voice=1)
                            if bottom:
                                self.add_note_element(measure, bottom, is_chord=bool(top), voice=2)
                else:
                    # Regular notes (A or B)
                    for note in bar_data:
                        self.add_note_element(measure, note)
    
    def generate(self, bars: List) -> str:
        """Generate complete MusicXML document."""
        root = ET.Element("score-partwise")
        root.set("version", "4.0")
        
        # Work info
        work = ET.SubElement(root, "work")
        ET.SubElement(work, "work-title").text = self.title
        
        # Identification
        ident = ET.SubElement(root, "identification")
        creator = ET.SubElement(ident, "creator")
        creator.set("type", "composer")
        creator.text = "GCE (Wayne Shorter Style)"
        
        # Part list
        part_list = ET.SubElement(root, "part-list")
        score_part = ET.SubElement(part_list, "score-part")
        score_part.set("id", "P1")
        ET.SubElement(score_part, "part-name").text = "Guitar"
        
        # Part content
        part = ET.SubElement(root, "part")
        part.set("id", "P1")
        self.create_part(part, bars)
        
        # Format output
        xml_str = ET.tostring(root, encoding="unicode")
        parsed = minidom.parseString(xml_str)
        return '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n' + parsed.toprettyxml(indent="  ")[23:]


def generate_notes_md(version: str, title: str, description: str) -> str:
    """Generate pedagogical notes markdown."""
    return f"""# Orbit ({version}) – {title}

## Intent
{description}

## What to Listen For
- How does this version create its own sense of forward motion?
- Where are the moments of tension and release?
- How does the melodic contour serve the overall aesthetic?

## How It Differs from Other Versions
| Version | Role | Character |
|---------|------|-----------|
| A – Lyrical | The tune itself | Sparse, singing, space |
| B – Modern Triad Pairs | Tonality Vault | Continuous, architectural |
| C – Counterpoint | Linear independence | Two voices, contrary motion |
| D – Hybrid | Integration model | Combines all textures |

## Practice Suggestions
1. Play through slowly, focusing on tone and sustain
2. Analyze the intervallic content
3. Compare with other versions to understand textural contrasts
4. Use as a springboard for your own improvisations

---
*Generated for GCE Jazz – Trio Tunes Project*
*Style: Wayne Shorter (post-1965, non-functional, melodic-first)*
"""


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("5x-ORBIT LEAD SHEETS A/B/C/D — Wayne Shorter Style")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent / "Trio Tunes" / "Tune02_Orbit" / "LeadSheet"
    alt_path = Path(__file__).parent.parent / "Trio Tunes" / "Alternative_LeadSheets" / "Orbit_WayneShorter"
    
    versions = {
        "A": {
            "title": "Lyrical",
            "generator": generate_version_a,
            "description": "The tune itself. Sparse, singing melody with long tones and ties across barlines. Emphasis on intervallic contour (6ths, 7ths, 9ths). Frequent space and silence. Should sound complete alone with just a metronome."
        },
        "B": {
            "title": "Modern Triad Pairs",
            "generator": generate_version_b,
            "description": "Tonality Vault / modern linear motion. Continuous or near-continuous 8ths with strict triad-pair logic derived from the Lydian scale palette. Angular, non-scalar, non-bebop. Momentum without cadence. Abstract and architectural."
        },
        "C": {
            "title": "Counterpoint",
            "generator": generate_version_c,
            "description": "Linear independence. Two independent melodic voices on one guitar staff. Contrary or oblique motion preferred. Clear registral separation with no voice doubling. Horizontal logic dominates. Reads like linear composition, not 'changes.'"
        },
        "D": {
            "title": "Hybrid",
            "generator": generate_version_d,
            "description": "Integration model. Combines lyrical fragments, triad-pair passages, and brief counterpoint moments. Texture shifts within the 16 bars with seamless transitions. Represents how a real modern soloist actually moves between concepts."
        }
    }
    
    for version_key, version_data in versions.items():
        print(f"\n--- Generating Version {version_key}: {version_data['title']} ---")
        
        # Generate bars
        bars = version_data["generator"]()
        
        # Create MusicXML
        generator = OrbitMusicXMLGenerator(version_key, version_data["title"])
        xml_content = generator.generate(bars)
        
        # Save to LeadSheet directory
        version_dir = base_path / version_key
        version_dir.mkdir(parents=True, exist_ok=True)
        
        xml_path = version_dir / f"5x-Orbit_{version_key}_{version_data['title'].replace(' ', '_')}.musicxml"
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print(f"  [OK] Saved: {xml_path}")
        
        # Save notes MD
        md_content = generate_notes_md(version_key, version_data["title"], version_data["description"])
        md_path = version_dir / f"5x-Orbit_{version_key}_Notes.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"  [OK] Saved: {md_path}")
        
        # Also save to Alternative_LeadSheets/Orbit_WayneShorter
        alt_path.mkdir(parents=True, exist_ok=True)
        alt_xml_path = alt_path / f"5x-Orbit_{version_key}_{version_data['title'].replace(' ', '_')}.musicxml"
        with open(alt_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print(f"  [OK] Saved: {alt_xml_path}")
    
    print("\n" + "=" * 60)
    print("ALL 4 VERSIONS GENERATED!")
    print("=" * 60)
    print(f"\nLeadSheet location: {base_path}")
    print(f"Alternative location: {alt_path}")


if __name__ == "__main__":
    main()

