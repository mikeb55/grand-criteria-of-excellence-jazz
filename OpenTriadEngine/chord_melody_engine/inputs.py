"""
Input Module for Chord-Melody Engine
=====================================

Handles input validation for melody, configuration, and constraints.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Union


class HarmonisationStyle(Enum):
    """Harmonisation approach modes."""
    DIATONIC = "diatonic"
    REHARM = "reharm"
    UST = "ust"
    FUNCTIONAL = "functional"
    MODAL = "modal"


class Texture(Enum):
    """Voicing density/texture levels."""
    SPARSE = "sparse"
    MEDIUM = "medium"
    DENSE = "dense"


class RhythmAlignment(Enum):
    """How chords align with melody."""
    EVERY_NOTE = "chord_on_every_note"
    PHRASE_BASED = "phrase_based"
    HARMONIC_RHYTHM = "harmonic_rhythm"
    STRONG_BEATS = "strong_beats"
    ARPEGGIATED = "arpeggiated"


class VoicingDensity(Enum):
    """Number of notes in voicings."""
    TWO_NOTE = "2-note"
    THREE_NOTE = "3-note"
    FOUR_NOTE = "4-note"


class Difficulty(Enum):
    """Difficulty levels for voicings."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# Valid configuration values
VALID_KEYS = [
    "C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb",
    "G", "G#", "Ab", "A", "A#", "Bb", "B"
]

VALID_SCALES = [
    "major", "minor", "dorian", "phrygian", "lydian", "mixolydian",
    "aeolian", "locrian", "melodic_minor", "harmonic_minor",
    "whole_tone", "diminished", "altered", "lydian_dominant",
    "pentatonic_major", "pentatonic_minor", "blues"
]

VALID_STRING_SETS = ["6-4", "5-3", "4-2", "auto"]

# Guitar register limits (MIDI)
GUITAR_LOW = 40   # E2
GUITAR_HIGH = 84  # C6


@dataclass
class ChordMelodyConfig:
    """
    Configuration for the Chord-Melody Engine.
    
    Attributes:
        key: Root key (e.g., "C", "F#", "Bb")
        scale: Scale type
        progression: Optional chord progression for context
        harmonisation_style: Harmonisation approach
        texture: Voicing density level
        string_set: Guitar string set preference
        voicing_density: Number of notes per voicing
        rhythm_alignment: How chords align with melody
        difficulty: Difficulty level
        allow_modal_interchange: Allow borrowing from parallel modes
        counterpoint_enabled: Generate counterpoint in lower voices
        register_low: Lowest playable pitch (MIDI)
        register_high: Highest playable pitch (MIDI)
    """
    key: str = "C"
    scale: str = "major"
    progression: Optional[List[str]] = None
    harmonisation_style: HarmonisationStyle = HarmonisationStyle.DIATONIC
    texture: Texture = Texture.MEDIUM
    string_set: str = "auto"
    voicing_density: VoicingDensity = VoicingDensity.THREE_NOTE
    rhythm_alignment: RhythmAlignment = RhythmAlignment.EVERY_NOTE
    difficulty: Difficulty = Difficulty.INTERMEDIATE
    allow_modal_interchange: bool = True
    counterpoint_enabled: bool = False
    register_low: int = GUITAR_LOW
    register_high: int = GUITAR_HIGH
    
    def __post_init__(self):
        """Validate all inputs."""
        self._validate_key()
        self._validate_scale()
        self._validate_string_set()
        self._validate_enums()
        self._validate_registers()
    
    def _validate_key(self):
        """Validate key."""
        if self.key not in VALID_KEYS:
            print(f"Warning: Invalid key '{self.key}', falling back to 'C'")
            self.key = "C"
    
    def _validate_scale(self):
        """Validate scale."""
        if self.scale.lower() not in VALID_SCALES:
            print(f"Warning: Invalid scale '{self.scale}', falling back to 'major'")
            self.scale = "major"
        else:
            self.scale = self.scale.lower()
    
    def _validate_string_set(self):
        """Validate string set."""
        if self.string_set not in VALID_STRING_SETS:
            print(f"Warning: Invalid string_set '{self.string_set}', falling back to 'auto'")
            self.string_set = "auto"
    
    def _validate_enums(self):
        """Convert string values to enums if needed."""
        if isinstance(self.harmonisation_style, str):
            try:
                self.harmonisation_style = HarmonisationStyle(self.harmonisation_style)
            except ValueError:
                self.harmonisation_style = HarmonisationStyle.DIATONIC
        
        if isinstance(self.texture, str):
            try:
                self.texture = Texture(self.texture)
            except ValueError:
                self.texture = Texture.MEDIUM
        
        if isinstance(self.rhythm_alignment, str):
            try:
                self.rhythm_alignment = RhythmAlignment(self.rhythm_alignment)
            except ValueError:
                self.rhythm_alignment = RhythmAlignment.EVERY_NOTE
        
        if isinstance(self.voicing_density, str):
            try:
                self.voicing_density = VoicingDensity(self.voicing_density)
            except ValueError:
                self.voicing_density = VoicingDensity.THREE_NOTE
        
        if isinstance(self.difficulty, str):
            try:
                self.difficulty = Difficulty(self.difficulty)
            except ValueError:
                self.difficulty = Difficulty.INTERMEDIATE
    
    def _validate_registers(self):
        """Validate register limits."""
        if self.register_low < 20 or self.register_low > 100:
            self.register_low = GUITAR_LOW
        if self.register_high < 40 or self.register_high > 120:
            self.register_high = GUITAR_HIGH
        if self.register_low >= self.register_high:
            self.register_low = GUITAR_LOW
            self.register_high = GUITAR_HIGH
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "key": self.key,
            "scale": self.scale,
            "progression": self.progression,
            "harmonisation_style": self.harmonisation_style.value,
            "texture": self.texture.value,
            "string_set": self.string_set,
            "voicing_density": self.voicing_density.value,
            "rhythm_alignment": self.rhythm_alignment.value,
            "difficulty": self.difficulty.value,
            "allow_modal_interchange": self.allow_modal_interchange,
            "counterpoint_enabled": self.counterpoint_enabled,
            "register_low": self.register_low,
            "register_high": self.register_high,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ChordMelodyConfig":
        """Create config from dictionary."""
        return cls(**data)


def validate_melody_in_register(
    melody_pitches: List[int],
    register_low: int = GUITAR_LOW,
    register_high: int = GUITAR_HIGH
) -> bool:
    """
    Check if all melody pitches are within the playable register.
    
    Args:
        melody_pitches: List of MIDI pitch numbers
        register_low: Lowest acceptable pitch
        register_high: Highest acceptable pitch
    
    Returns:
        True if all pitches are playable
    """
    return all(register_low <= p <= register_high for p in melody_pitches)


def validate_melody_as_top_voice(
    melody_pitch: int,
    harmony_pitches: List[int]
) -> bool:
    """
    Check if melody pitch can be the top voice of the harmony.
    
    Args:
        melody_pitch: The melody note (MIDI)
        harmony_pitches: The harmony notes below
    
    Returns:
        True if melody is highest pitch
    """
    if not harmony_pitches:
        return True
    return melody_pitch >= max(harmony_pitches)

