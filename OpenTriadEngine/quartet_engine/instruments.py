"""
Instrument Definitions for Quartet Engine
==========================================

Defines voice registers, safe leaps, and playing constraints for:
- Violin I
- Violin II
- Viola
- Cello
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum


class InstrumentType(Enum):
    """String quartet instruments."""
    VIOLIN_I = "violin_1"
    VIOLIN_II = "violin_2"
    VIOLA = "viola"
    CELLO = "cello"


@dataclass
class VoiceRange:
    """
    Range definition for an instrument.
    
    Attributes:
        low: Lowest playable pitch (MIDI)
        high: Highest comfortable pitch (MIDI)
        extended_high: Extended technique high (MIDI)
        sweet_spot: Most resonant range (low, high)
    """
    low: int
    high: int
    extended_high: int
    sweet_spot: Tuple[int, int]


@dataclass
class PlayingConstraints:
    """
    Playing constraints for an instrument.
    
    Attributes:
        max_safe_leap: Maximum comfortable melodic leap (semitones)
        max_leap: Maximum possible leap (semitones)
        preferred_motion: Preferred motion type (step, leap)
        double_stop_intervals: Allowed double-stop intervals
        pizz_range: Range for pizzicato (low, high)
        legato_max_leap: Maximum leap for legato passages
    """
    max_safe_leap: int
    max_leap: int
    preferred_motion: str
    double_stop_intervals: List[int]
    pizz_range: Tuple[int, int]
    legato_max_leap: int


@dataclass
class Instrument:
    """
    Complete instrument definition.
    
    Attributes:
        instrument_type: Type of instrument
        name: Display name
        clef: Music notation clef
        range: Voice range
        constraints: Playing constraints
        transposition: Transposition (0 for concert pitch)
    """
    instrument_type: InstrumentType
    name: str
    clef: str
    range: VoiceRange
    constraints: PlayingConstraints
    transposition: int = 0
    
    def is_pitch_playable(self, pitch: int, extended: bool = False) -> bool:
        """Check if a pitch is playable."""
        high = self.range.extended_high if extended else self.range.high
        return self.range.low <= pitch <= high
    
    def is_in_sweet_spot(self, pitch: int) -> bool:
        """Check if pitch is in the sweet spot."""
        return self.range.sweet_spot[0] <= pitch <= self.range.sweet_spot[1]
    
    def is_leap_safe(self, interval: int) -> bool:
        """Check if a melodic leap is safe."""
        return abs(interval) <= self.constraints.max_safe_leap
    
    def is_leap_possible(self, interval: int) -> bool:
        """Check if a leap is possible (may be difficult)."""
        return abs(interval) <= self.constraints.max_leap


class QuartetInstruments:
    """
    Provides standard quartet instrument definitions.
    """
    
    # MIDI note reference: C4 = 60
    # G3 = 55, C3 = 48, C2 = 36
    
    VIOLIN_I = Instrument(
        instrument_type=InstrumentType.VIOLIN_I,
        name="Violin I",
        clef="treble",
        range=VoiceRange(
            low=55,    # G3
            high=88,   # E6
            extended_high=100,  # E7
            sweet_spot=(60, 84)  # C4 to C6
        ),
        constraints=PlayingConstraints(
            max_safe_leap=12,     # Octave
            max_leap=19,          # Octave + fifth
            preferred_motion="step",
            double_stop_intervals=[3, 4, 5, 7, 8, 12],  # 3rds, 4ths, 5ths, 6ths, octaves
            pizz_range=(55, 79),  # G3 to G5
            legato_max_leap=7     # Fifth
        )
    )
    
    VIOLIN_II = Instrument(
        instrument_type=InstrumentType.VIOLIN_II,
        name="Violin II",
        clef="treble",
        range=VoiceRange(
            low=55,    # G3
            high=86,   # D6
            extended_high=93,  # A6
            sweet_spot=(55, 79)  # G3 to G5
        ),
        constraints=PlayingConstraints(
            max_safe_leap=12,
            max_leap=17,
            preferred_motion="step",
            double_stop_intervals=[3, 4, 5, 7, 8, 12],
            pizz_range=(55, 77),
            legato_max_leap=7
        )
    )
    
    VIOLA = Instrument(
        instrument_type=InstrumentType.VIOLA,
        name="Viola",
        clef="alto",
        range=VoiceRange(
            low=48,    # C3
            high=81,   # A5
            extended_high=88,  # E6
            sweet_spot=(48, 72)  # C3 to C5
        ),
        constraints=PlayingConstraints(
            max_safe_leap=12,
            max_leap=15,
            preferred_motion="step",
            double_stop_intervals=[3, 4, 5, 7, 8, 12],
            pizz_range=(48, 72),
            legato_max_leap=7
        )
    )
    
    CELLO = Instrument(
        instrument_type=InstrumentType.CELLO,
        name="Cello",
        clef="bass",
        range=VoiceRange(
            low=36,    # C2
            high=76,   # E5
            extended_high=84,  # C6
            sweet_spot=(36, 67)  # C2 to G4
        ),
        constraints=PlayingConstraints(
            max_safe_leap=14,     # Major 9th (bass lines leap more)
            max_leap=19,
            preferred_motion="step",
            double_stop_intervals=[3, 4, 5, 7, 8, 12],
            pizz_range=(36, 67),
            legato_max_leap=9     # Major 6th
        )
    )
    
    @classmethod
    def get_all(cls) -> List[Instrument]:
        """Get all quartet instruments in score order."""
        return [cls.VIOLIN_I, cls.VIOLIN_II, cls.VIOLA, cls.CELLO]
    
    @classmethod
    def get_by_type(cls, instrument_type: InstrumentType) -> Instrument:
        """Get instrument by type."""
        mapping = {
            InstrumentType.VIOLIN_I: cls.VIOLIN_I,
            InstrumentType.VIOLIN_II: cls.VIOLIN_II,
            InstrumentType.VIOLA: cls.VIOLA,
            InstrumentType.CELLO: cls.CELLO,
        }
        return mapping.get(instrument_type, cls.VIOLIN_I)
    
    @classmethod
    def validate_voicing(
        cls,
        pitches: Dict[InstrumentType, int]
    ) -> Tuple[bool, List[str]]:
        """
        Validate a voicing across the quartet.
        
        Args:
            pitches: Dict mapping instrument to MIDI pitch
        
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        for inst_type, pitch in pitches.items():
            inst = cls.get_by_type(inst_type)
            if not inst.is_pitch_playable(pitch):
                issues.append(
                    f"{inst.name}: pitch {pitch} out of range "
                    f"({inst.range.low}-{inst.range.high})"
                )
        
        # Check voice crossing
        ordered_pitches = [
            (InstrumentType.VIOLIN_I, pitches.get(InstrumentType.VIOLIN_I, 0)),
            (InstrumentType.VIOLIN_II, pitches.get(InstrumentType.VIOLIN_II, 0)),
            (InstrumentType.VIOLA, pitches.get(InstrumentType.VIOLA, 0)),
            (InstrumentType.CELLO, pitches.get(InstrumentType.CELLO, 0)),
        ]
        
        for i in range(len(ordered_pitches) - 1):
            upper_pitch = ordered_pitches[i][1]
            lower_pitch = ordered_pitches[i + 1][1]
            if upper_pitch > 0 and lower_pitch > 0 and upper_pitch < lower_pitch:
                issues.append(
                    f"Voice crossing: {ordered_pitches[i][0].value} "
                    f"below {ordered_pitches[i + 1][0].value}"
                )
        
        return len(issues) == 0, issues
    
    @classmethod
    def get_register_adjusted_ranges(
        cls,
        profile: str = "standard"
    ) -> Dict[InstrumentType, Tuple[int, int]]:
        """
        Get adjusted ranges based on register profile.
        
        Args:
            profile: "standard", "high_lift", or "dark_low"
        
        Returns:
            Dict of instrument to (low, high) range
        """
        base_ranges = {
            InstrumentType.VIOLIN_I: (55, 88),
            InstrumentType.VIOLIN_II: (55, 86),
            InstrumentType.VIOLA: (48, 81),
            InstrumentType.CELLO: (36, 76),
        }
        
        if profile == "high_lift":
            # Shift everything up, use upper ranges
            return {
                InstrumentType.VIOLIN_I: (67, 88),   # G4-E6
                InstrumentType.VIOLIN_II: (62, 81),  # D4-A5
                InstrumentType.VIOLA: (55, 76),      # G3-E5
                InstrumentType.CELLO: (43, 67),      # G2-G4
            }
        
        elif profile == "dark_low":
            # Shift everything down, use lower ranges
            return {
                InstrumentType.VIOLIN_I: (55, 76),   # G3-E5
                InstrumentType.VIOLIN_II: (55, 72),  # G3-C5
                InstrumentType.VIOLA: (48, 67),      # C3-G4
                InstrumentType.CELLO: (36, 55),      # C2-G3
            }
        
        else:  # standard
            return base_ranges

