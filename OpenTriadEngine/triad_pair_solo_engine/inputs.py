"""
Input Module for Triad Pair Solo Engine
========================================

Handles input validation with fallbacks for all configuration parameters.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class TriadPairType(Enum):
    """Types of triad pairs available."""
    DIATONIC = "diatonic"
    KLEMONIC = "klemonic"
    UST = "ust"  # Upper Structure Triads
    ALTERED_DOMINANT = "altered_dominant_pairs"


class SoloMode(Enum):
    """Solo generation modes."""
    FUNCTIONAL = "functional"
    MODAL = "modal"
    INTERVALLIC = "intervallic"
    HYBRID = "hybrid"


class RhythmicStyle(Enum):
    """Rhythmic style options."""
    STRAIGHT = "straight"
    SWING = "swing"
    TRIPLET = "triplet"
    SYNCOPATED = "syncopated"
    POLYRHYTHMIC = "polyrhythmic"


class ContourType(Enum):
    """Melodic contour options."""
    ASCENDING = "ascending"
    DESCENDING = "descending"
    WAVE = "wave"
    ZIGZAG = "zigzag"
    RANDOM_SEEDED = "random_seeded"


class SoloDifficulty(Enum):
    """Difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# Valid keys
VALID_KEYS = [
    "C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", 
    "G", "G#", "Ab", "A", "A#", "Bb", "B"
]

# Valid scales
VALID_SCALES = [
    "major", "minor", "dorian", "phrygian", "lydian", "mixolydian",
    "aeolian", "locrian", "melodic_minor", "harmonic_minor",
    "whole_tone", "diminished", "altered", "lydian_dominant",
    "half_whole_dim", "whole_half_dim", "bebop_dominant",
    "bebop_major", "pentatonic_major", "pentatonic_minor",
    "blues", "chromatic"
]

# Valid string sets for guitar
VALID_STRING_SETS = ["6-4", "5-3", "4-2", "auto"]


@dataclass
class SoloEngineConfig:
    """
    Configuration for the Triad Pair Solo Engine.
    
    Attributes:
        key: Root key (e.g., "C", "F#", "Bb")
        scale: Scale type (e.g., "major", "dorian", "altered")
        progression: Optional chord progression (e.g., ["Dm7", "G7", "Cmaj7"])
        triad_pair_type: Type of triad pairs to use
        mode: Solo generation mode
        string_set: Guitar string set (optional)
        rhythmic_style: Rhythmic feel
        phrase_length: Length in bars or beats
        contour: Melodic contour shape
        difficulty: Difficulty level
        seed: Optional random seed for reproducibility
    """
    key: str = "C"
    scale: str = "major"
    progression: Optional[List[str]] = None
    triad_pair_type: TriadPairType = TriadPairType.DIATONIC
    mode: SoloMode = SoloMode.INTERVALLIC
    string_set: str = "auto"
    rhythmic_style: RhythmicStyle = RhythmicStyle.SWING
    phrase_length: int = 4  # bars
    contour: ContourType = ContourType.WAVE
    difficulty: SoloDifficulty = SoloDifficulty.INTERMEDIATE
    seed: Optional[int] = None
    
    def __post_init__(self):
        """Validate and apply fallbacks for all inputs."""
        self._validate_key()
        self._validate_scale()
        self._validate_progression()
        self._validate_triad_pair_type()
        self._validate_mode()
        self._validate_string_set()
        self._validate_rhythmic_style()
        self._validate_phrase_length()
        self._validate_contour()
        self._validate_difficulty()
    
    def _validate_key(self):
        """Validate key with fallback to C."""
        if self.key not in VALID_KEYS:
            print(f"Warning: Invalid key '{self.key}', falling back to 'C'")
            self.key = "C"
    
    def _validate_scale(self):
        """Validate scale with fallback to major."""
        if self.scale.lower() not in VALID_SCALES:
            print(f"Warning: Invalid scale '{self.scale}', falling back to 'major'")
            self.scale = "major"
        else:
            self.scale = self.scale.lower()
    
    def _validate_progression(self):
        """Validate progression format."""
        if self.progression is not None:
            if not isinstance(self.progression, list):
                print("Warning: Progression must be a list, setting to None")
                self.progression = None
            elif len(self.progression) == 0:
                self.progression = None
    
    def _validate_triad_pair_type(self):
        """Validate triad pair type."""
        if isinstance(self.triad_pair_type, str):
            try:
                self.triad_pair_type = TriadPairType(self.triad_pair_type)
            except ValueError:
                print(f"Warning: Invalid triad_pair_type '{self.triad_pair_type}', "
                      "falling back to DIATONIC")
                self.triad_pair_type = TriadPairType.DIATONIC
    
    def _validate_mode(self):
        """Validate solo mode."""
        if isinstance(self.mode, str):
            try:
                self.mode = SoloMode(self.mode)
            except ValueError:
                print(f"Warning: Invalid mode '{self.mode}', falling back to INTERVALLIC")
                self.mode = SoloMode.INTERVALLIC
    
    def _validate_string_set(self):
        """Validate string set."""
        if self.string_set not in VALID_STRING_SETS:
            print(f"Warning: Invalid string_set '{self.string_set}', falling back to 'auto'")
            self.string_set = "auto"
    
    def _validate_rhythmic_style(self):
        """Validate rhythmic style."""
        if isinstance(self.rhythmic_style, str):
            try:
                self.rhythmic_style = RhythmicStyle(self.rhythmic_style)
            except ValueError:
                print(f"Warning: Invalid rhythmic_style '{self.rhythmic_style}', "
                      "falling back to SWING")
                self.rhythmic_style = RhythmicStyle.SWING
    
    def _validate_phrase_length(self):
        """Validate phrase length (1-32 bars)."""
        if not isinstance(self.phrase_length, int) or self.phrase_length < 1:
            print("Warning: Invalid phrase_length, falling back to 4 bars")
            self.phrase_length = 4
        elif self.phrase_length > 32:
            print("Warning: phrase_length too long, capping at 32 bars")
            self.phrase_length = 32
    
    def _validate_contour(self):
        """Validate contour type."""
        if isinstance(self.contour, str):
            try:
                self.contour = ContourType(self.contour)
            except ValueError:
                print(f"Warning: Invalid contour '{self.contour}', falling back to WAVE")
                self.contour = ContourType.WAVE
    
    def _validate_difficulty(self):
        """Validate difficulty level."""
        if isinstance(self.difficulty, str):
            try:
                self.difficulty = SoloDifficulty(self.difficulty)
            except ValueError:
                print(f"Warning: Invalid difficulty '{self.difficulty}', "
                      "falling back to INTERMEDIATE")
                self.difficulty = SoloDifficulty.INTERMEDIATE
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "key": self.key,
            "scale": self.scale,
            "progression": self.progression,
            "triad_pair_type": self.triad_pair_type.value,
            "mode": self.mode.value,
            "string_set": self.string_set,
            "rhythmic_style": self.rhythmic_style.value,
            "phrase_length": self.phrase_length,
            "contour": self.contour.value,
            "difficulty": self.difficulty.value,
            "seed": self.seed
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SoloEngineConfig":
        """Create config from dictionary."""
        return cls(
            key=data.get("key", "C"),
            scale=data.get("scale", "major"),
            progression=data.get("progression"),
            triad_pair_type=data.get("triad_pair_type", "diatonic"),
            mode=data.get("mode", "intervallic"),
            string_set=data.get("string_set", "auto"),
            rhythmic_style=data.get("rhythmic_style", "swing"),
            phrase_length=data.get("phrase_length", 4),
            contour=data.get("contour", "wave"),
            difficulty=data.get("difficulty", "intermediate"),
            seed=data.get("seed")
        )

