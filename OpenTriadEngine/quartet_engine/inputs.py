"""
Input Module for Quartet Engine
================================

Handles configuration and validation for quartet generation.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import Enum


class QuartetMode(Enum):
    """Quartet writing modes."""
    HOMOPHONIC = "homophonic"
    CONTRAPUNTAL = "contrapuntal"
    HYBRID = "hybrid"
    HARMONIC_FIELD = "harmonic_field"
    RHYTHMIC_CELLS = "rhythmic_cells"


class TextureDensity(Enum):
    """Texture density levels."""
    SPARSE = "sparse"
    MEDIUM = "medium"
    DENSE = "dense"


class MotionType(Enum):
    """Harmonic motion types."""
    FUNCTIONAL = "functional"
    MODAL = "modal"
    INTERVALLIC = "intervallic"
    STATIC_PEDAL = "static_pedal"


class PatternType(Enum):
    """Pattern types for quartet."""
    INVERSION_CYCLES = "inversion_cycles"
    OPEN_TRIAD_LOOPS = "open_triad_loops"
    TRIAD_PAIRS = "triad_pairs"
    CONTRAPUNTAL_CELLS = "contrapuntal_cells"


class RegisterProfile(Enum):
    """Register profiles for quartet texture."""
    STANDARD = "standard"
    HIGH_LIFT = "high_lift"      # Lighter, brighter
    DARK_LOW = "dark_low"        # Heavier, darker


class RhythmicStyle(Enum):
    """Rhythmic style options."""
    STRAIGHT = "straight"
    SYNCOPATED = "syncopated"
    MIXED = "mixed"
    OSTINATO = "ostinato"


# Valid keys and scales
VALID_KEYS = [
    "C", "C#", "Db", "D", "D#", "Eb", "E", "F",
    "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"
]

VALID_SCALES = [
    "major", "minor", "dorian", "phrygian", "lydian", "mixolydian",
    "aeolian", "locrian", "melodic_minor", "harmonic_minor",
    "whole_tone", "diminished", "altered", "lydian_dominant"
]


@dataclass
class VoiceRangeOverride:
    """Override for a voice's range."""
    instrument: str
    low: int   # MIDI pitch
    high: int  # MIDI pitch


@dataclass
class QuartetConfig:
    """
    Configuration for the Quartet Engine.
    
    Attributes:
        key: Musical key
        scale: Scale type
        progression: Optional chord progression
        quartet_mode: Writing mode
        texture_density: Texture density
        motion_type: Harmonic motion type
        length: Length in bars
        pattern_type: Pattern type to use
        register_profile: Register profile
        voice_ranges: Optional voice range overrides
        rhythmic_style: Rhythmic style
        allow_voice_crossing: Whether to allow voice crossing
        enable_counterpoint: Enable contrapuntal behavior
        tempo: Tempo in BPM
        time_signature: Time signature as (beats, beat_value)
    """
    key: str = "C"
    scale: str = "major"
    progression: Optional[List[str]] = None
    quartet_mode: QuartetMode = QuartetMode.HOMOPHONIC
    texture_density: TextureDensity = TextureDensity.MEDIUM
    motion_type: MotionType = MotionType.MODAL
    length: int = 8  # bars
    pattern_type: PatternType = PatternType.OPEN_TRIAD_LOOPS
    register_profile: RegisterProfile = RegisterProfile.STANDARD
    voice_ranges: Optional[List[VoiceRangeOverride]] = None
    rhythmic_style: RhythmicStyle = RhythmicStyle.STRAIGHT
    allow_voice_crossing: bool = False
    enable_counterpoint: bool = True
    tempo: int = 80
    time_signature: Tuple[int, int] = (4, 4)
    
    def __post_init__(self):
        """Validate configuration."""
        self._validate_key()
        self._validate_scale()
        self._validate_length()
        self._validate_enums()
    
    def _validate_key(self):
        """Validate key."""
        if self.key not in VALID_KEYS:
            print(f"Warning: Invalid key '{self.key}', using 'C'")
            self.key = "C"
    
    def _validate_scale(self):
        """Validate scale."""
        if self.scale.lower() not in VALID_SCALES:
            print(f"Warning: Invalid scale '{self.scale}', using 'major'")
            self.scale = "major"
        else:
            self.scale = self.scale.lower()
    
    def _validate_length(self):
        """Validate length."""
        if self.length < 1:
            self.length = 1
        elif self.length > 128:
            self.length = 128
    
    def _validate_enums(self):
        """Convert string values to enums."""
        if isinstance(self.quartet_mode, str):
            try:
                self.quartet_mode = QuartetMode(self.quartet_mode)
            except ValueError:
                self.quartet_mode = QuartetMode.HOMOPHONIC
        
        if isinstance(self.texture_density, str):
            try:
                self.texture_density = TextureDensity(self.texture_density)
            except ValueError:
                self.texture_density = TextureDensity.MEDIUM
        
        if isinstance(self.motion_type, str):
            try:
                self.motion_type = MotionType(self.motion_type)
            except ValueError:
                self.motion_type = MotionType.MODAL
        
        if isinstance(self.pattern_type, str):
            try:
                self.pattern_type = PatternType(self.pattern_type)
            except ValueError:
                self.pattern_type = PatternType.OPEN_TRIAD_LOOPS
        
        if isinstance(self.register_profile, str):
            try:
                self.register_profile = RegisterProfile(self.register_profile)
            except ValueError:
                self.register_profile = RegisterProfile.STANDARD
        
        if isinstance(self.rhythmic_style, str):
            try:
                self.rhythmic_style = RhythmicStyle(self.rhythmic_style)
            except ValueError:
                self.rhythmic_style = RhythmicStyle.STRAIGHT
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "scale": self.scale,
            "progression": self.progression,
            "quartet_mode": self.quartet_mode.value,
            "texture_density": self.texture_density.value,
            "motion_type": self.motion_type.value,
            "length": self.length,
            "pattern_type": self.pattern_type.value,
            "register_profile": self.register_profile.value,
            "rhythmic_style": self.rhythmic_style.value,
            "allow_voice_crossing": self.allow_voice_crossing,
            "enable_counterpoint": self.enable_counterpoint,
            "tempo": self.tempo,
            "time_signature": self.time_signature,
        }

