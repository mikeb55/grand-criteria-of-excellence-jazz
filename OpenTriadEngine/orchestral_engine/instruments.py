"""
Instrument Definitions for Orchestral Engine
==============================================

Defines instrument types, ranges, transpositions, and characteristics.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional


class InstrumentType(Enum):
    """Orchestral instrument types."""
    FLUTE = "flute"
    CLARINET = "clarinet"
    FLUGELHORN = "flugelhorn"
    VIOLIN_I = "violin_1"
    VIOLIN_II = "violin_2"
    VIOLA = "viola"
    CELLO = "cello"
    BASS = "bass"
    PIANO = "piano"
    PERCUSSION = "percussion"


class InstrumentSection(Enum):
    """Instrument sections."""
    WINDS = "winds"
    BRASS = "brass"
    STRINGS = "strings"
    KEYBOARD = "keyboard"
    PERCUSSION = "percussion"


@dataclass
class Instrument:
    """
    Instrument definition.
    
    Attributes:
        name: Instrument name
        inst_type: Instrument type enum
        section: Instrument section
        range_low: Lowest playable MIDI note
        range_high: Highest playable MIDI note
        sweet_low: Low end of comfortable range
        sweet_high: High end of comfortable range
        transposition: Transposition in semitones (0 for concert pitch)
        clef: Clef type (treble, alto, bass)
        safe_leap: Maximum comfortable leap in semitones
        doubling_priority: Priority for doubling (higher = prefer)
    """
    name: str
    inst_type: InstrumentType
    section: InstrumentSection
    range_low: int
    range_high: int
    sweet_low: int
    sweet_high: int
    transposition: int = 0
    clef: str = "treble"
    safe_leap: int = 12
    doubling_priority: int = 5


# Define all orchestra instruments
ORCHESTRA_INSTRUMENTS: Dict[InstrumentType, Instrument] = {
    InstrumentType.FLUTE: Instrument(
        name="Flute",
        inst_type=InstrumentType.FLUTE,
        section=InstrumentSection.WINDS,
        range_low=60,   # C4
        range_high=96,  # C7
        sweet_low=67,   # G4
        sweet_high=91,  # G6
        transposition=0,
        clef="treble",
        safe_leap=12,
        doubling_priority=7
    ),
    InstrumentType.CLARINET: Instrument(
        name="Clarinet in Bb",
        inst_type=InstrumentType.CLARINET,
        section=InstrumentSection.WINDS,
        range_low=50,   # D3 (concert pitch)
        range_high=93,  # A6 (concert pitch)
        sweet_low=55,   # G3
        sweet_high=86,  # D6
        transposition=-2,  # Bb instrument (written note sounds M2 lower)
        clef="treble",
        safe_leap=12,
        doubling_priority=6
    ),
    InstrumentType.FLUGELHORN: Instrument(
        name="Flugelhorn/Trumpet",
        inst_type=InstrumentType.FLUGELHORN,
        section=InstrumentSection.BRASS,
        range_low=54,   # F#3 (concert pitch)
        range_high=86,  # D6 (concert pitch)
        sweet_low=58,   # Bb3
        sweet_high=79,  # G5
        transposition=-2,  # Bb instrument
        clef="treble",
        safe_leap=10,
        doubling_priority=5
    ),
    InstrumentType.VIOLIN_I: Instrument(
        name="Violin I",
        inst_type=InstrumentType.VIOLIN_I,
        section=InstrumentSection.STRINGS,
        range_low=55,   # G3
        range_high=100, # E7
        sweet_low=60,   # C4
        sweet_high=88,  # E6
        transposition=0,
        clef="treble",
        safe_leap=12,
        doubling_priority=8
    ),
    InstrumentType.VIOLIN_II: Instrument(
        name="Violin II",
        inst_type=InstrumentType.VIOLIN_II,
        section=InstrumentSection.STRINGS,
        range_low=55,   # G3
        range_high=86,  # D6
        sweet_low=55,   # G3
        sweet_high=79,  # G5
        transposition=0,
        clef="treble",
        safe_leap=12,
        doubling_priority=7
    ),
    InstrumentType.VIOLA: Instrument(
        name="Viola",
        inst_type=InstrumentType.VIOLA,
        section=InstrumentSection.STRINGS,
        range_low=48,   # C3
        range_high=81,  # A5
        sweet_low=48,   # C3
        sweet_high=72,  # C5
        transposition=0,
        clef="alto",
        safe_leap=10,
        doubling_priority=6
    ),
    InstrumentType.CELLO: Instrument(
        name="Cello",
        inst_type=InstrumentType.CELLO,
        section=InstrumentSection.STRINGS,
        range_low=36,   # C2
        range_high=76,  # E5
        sweet_low=36,   # C2
        sweet_high=67,  # G4
        transposition=0,
        clef="bass",
        safe_leap=12,
        doubling_priority=7
    ),
    InstrumentType.BASS: Instrument(
        name="Double Bass",
        inst_type=InstrumentType.BASS,
        section=InstrumentSection.STRINGS,
        range_low=28,   # E1 (sounds octave lower than written)
        range_high=60,  # C4
        sweet_low=28,   # E1
        sweet_high=55,  # G3
        transposition=-12,  # Sounds octave lower
        clef="bass",
        safe_leap=12,
        doubling_priority=8
    ),
    InstrumentType.PIANO: Instrument(
        name="Piano",
        inst_type=InstrumentType.PIANO,
        section=InstrumentSection.KEYBOARD,
        range_low=21,   # A0
        range_high=108, # C8
        sweet_low=36,   # C2
        sweet_high=96,  # C7
        transposition=0,
        clef="treble",  # Uses grand staff
        safe_leap=24,
        doubling_priority=5
    ),
    InstrumentType.PERCUSSION: Instrument(
        name="Percussion",
        inst_type=InstrumentType.PERCUSSION,
        section=InstrumentSection.PERCUSSION,
        range_low=36,   # Variable
        range_high=84,
        sweet_low=48,
        sweet_high=72,
        transposition=0,
        clef="percussion",
        safe_leap=24,
        doubling_priority=3
    ),
}


class OrchestraInstruments:
    """Utility class for orchestral instrument operations."""
    
    @staticmethod
    def get_instrument(inst_type: InstrumentType) -> Instrument:
        """Get instrument definition by type."""
        return ORCHESTRA_INSTRUMENTS[inst_type]
    
    @staticmethod
    def is_in_range(inst_type: InstrumentType, pitch: int) -> bool:
        """Check if pitch is within instrument range."""
        inst = ORCHESTRA_INSTRUMENTS[inst_type]
        return inst.range_low <= pitch <= inst.range_high
    
    @staticmethod
    def is_in_sweet_spot(inst_type: InstrumentType, pitch: int) -> bool:
        """Check if pitch is within comfortable range."""
        inst = ORCHESTRA_INSTRUMENTS[inst_type]
        return inst.sweet_low <= pitch <= inst.sweet_high
    
    @staticmethod
    def get_by_section(section: InstrumentSection) -> list:
        """Get all instruments in a section."""
        return [inst for inst in ORCHESTRA_INSTRUMENTS.values() 
                if inst.section == section]
    
    @staticmethod
    def get_winds() -> list:
        """Get all wind instruments."""
        return OrchestraInstruments.get_by_section(InstrumentSection.WINDS)
    
    @staticmethod
    def get_brass() -> list:
        """Get all brass instruments."""
        return OrchestraInstruments.get_by_section(InstrumentSection.BRASS)
    
    @staticmethod
    def get_strings() -> list:
        """Get all string instruments."""
        return OrchestraInstruments.get_by_section(InstrumentSection.STRINGS)
    
    @staticmethod
    def clamp_to_range(inst_type: InstrumentType, pitch: int) -> int:
        """Clamp pitch to instrument range with octave adjustment."""
        inst = ORCHESTRA_INSTRUMENTS[inst_type]
        
        while pitch < inst.range_low:
            pitch += 12
        while pitch > inst.range_high:
            pitch -= 12
        
        return pitch
    
    @staticmethod
    def get_clef(inst_type: InstrumentType) -> Tuple[str, int]:
        """Get clef sign and line for instrument."""
        inst = ORCHESTRA_INSTRUMENTS[inst_type]
        
        clef_mapping = {
            "treble": ("G", 2),
            "alto": ("C", 3),
            "bass": ("F", 4),
            "percussion": ("percussion", 2)
        }
        
        return clef_mapping.get(inst.clef, ("G", 2))

