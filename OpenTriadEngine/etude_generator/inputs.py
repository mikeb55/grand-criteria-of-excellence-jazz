"""
Input Module for Etude Generator
=================================

Handles input configuration, validation, and fallback defaults
for etude generation.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
import json


class EtudeType(Enum):
    """Types of etudes that can be generated."""
    MELODIC = "melodic"
    HARMONIC = "harmonic"
    INTERVALLIC = "intervallic"
    CHORD_MELODY = "chord_melody"
    POSITION = "position"
    STRING_SET = "string_set"
    TWO_FIVE_ONE = "ii_v_i"
    INVERSION_CYCLE = "inversion_cycle"
    SCALAR = "scalar"


class Difficulty(Enum):
    """Difficulty levels for etudes."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class StringSet(Enum):
    """Guitar string sets for voicings."""
    HIGH = "6-4"      # Strings 6, 5, 4 (low E, A, D)
    MIDDLE = "5-3"    # Strings 5, 4, 3 (A, D, G)
    LOW = "4-2"       # Strings 4, 3, 2 (D, G, B)
    AUTO = "auto"     # Engine decides based on register


class EtudeMode(Enum):
    """Voice-leading modes for etude generation."""
    FUNCTIONAL = "functional"
    MODAL = "modal"
    INTERVALLIC = "intervallic"


class RhythmicStyle(Enum):
    """Rhythmic styles for etudes."""
    STRAIGHT = "straight"
    SYNCOPATED = "syncopated"
    TRIPLET = "triplet"
    POLYRHYTHMIC = "polyrhythmic"
    SWING = "swing"


@dataclass
class PositionConstraints:
    """
    Fretboard position constraints for position-locked etudes.
    
    Attributes:
        min_fret: Lowest fret allowed
        max_fret: Highest fret allowed
        position_name: Position name (e.g., "5th position")
    """
    min_fret: int = 0
    max_fret: int = 12
    position_name: str = "open position"
    
    def contains(self, fret: int) -> bool:
        """Check if a fret is within the position."""
        return self.min_fret <= fret <= self.max_fret
    
    @classmethod
    def from_position(cls, position: int, span: int = 4) -> 'PositionConstraints':
        """Create constraints from a position number."""
        return cls(
            min_fret=position,
            max_fret=position + span,
            position_name=f"{position}th position" if position > 0 else "open position"
        )


# Difficulty-based constraints
DIFFICULTY_SETTINGS = {
    Difficulty.BEGINNER: {
        'max_fret_span': 4,
        'max_tempo': 80,
        'avoid_stretches': True,
        'prefer_open_strings': True,
        'max_position_shifts': 0,
        'allowed_rhythms': ['straight'],
        'max_bars': 8,
    },
    Difficulty.INTERMEDIATE: {
        'max_fret_span': 5,
        'max_tempo': 120,
        'avoid_stretches': False,
        'prefer_open_strings': False,
        'max_position_shifts': 2,
        'allowed_rhythms': ['straight', 'syncopated', 'triplet'],
        'max_bars': 16,
    },
    Difficulty.ADVANCED: {
        'max_fret_span': 7,
        'max_tempo': 180,
        'avoid_stretches': False,
        'prefer_open_strings': False,
        'max_position_shifts': 5,
        'allowed_rhythms': ['straight', 'syncopated', 'triplet', 'polyrhythmic'],
        'max_bars': 32,
    },
}


@dataclass
class EtudeConfig:
    """
    Complete configuration for etude generation.
    
    All parameters are validated upon initialization with fallbacks
    for invalid or missing values.
    """
    # Basic parameters
    key: str = "C"
    scale: str = "ionian"
    progression: Optional[List[str]] = None
    
    # Etude type
    etude_type: str = "melodic"
    
    # Difficulty
    difficulty: str = "intermediate"
    
    # Guitar parameters
    string_set: str = "auto"
    position: Optional[int] = None  # For position-locked etudes
    
    # Voice-leading mode
    mode: str = "functional"
    
    # Rhythm
    rhythmic_style: str = "straight"
    tempo: int = 100
    
    # Structure
    length: int = 8  # bars
    time_signature: tuple = (4, 4)
    
    # Advanced options
    include_voice_leading_annotations: bool = True
    include_harmonic_analysis: bool = True
    include_fingerings: bool = True
    
    # Title (auto-generated if not provided)
    title: Optional[str] = None
    
    # Validated enums (set during validation)
    _etude_type_enum: EtudeType = field(default=None, repr=False)
    _difficulty_enum: Difficulty = field(default=None, repr=False)
    _string_set_enum: StringSet = field(default=None, repr=False)
    _mode_enum: EtudeMode = field(default=None, repr=False)
    _rhythmic_style_enum: RhythmicStyle = field(default=None, repr=False)
    _validated: bool = field(default=False, repr=False)
    
    def __post_init__(self):
        self._validate_and_normalize()
    
    def _validate_and_normalize(self):
        """Validate all inputs and apply fallbacks."""
        self.key = self._validate_key(self.key)
        self.scale = self._validate_scale(self.scale)
        self._etude_type_enum = self._validate_etude_type(self.etude_type)
        self._difficulty_enum = self._validate_difficulty(self.difficulty)
        self._string_set_enum = self._validate_string_set(self.string_set)
        self._mode_enum = self._validate_mode(self.mode)
        self._rhythmic_style_enum = self._validate_rhythmic_style(self.rhythmic_style)
        self.length = self._validate_length(self.length)
        self.tempo = self._validate_tempo(self.tempo)
        
        # Generate title if not provided
        if self.title is None:
            self.title = self._generate_title()
        
        self._validated = True
    
    @staticmethod
    def _validate_key(value: str) -> str:
        """Validate key with fallback to 'C'."""
        valid_keys = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 
                      'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        normalized = value.strip().capitalize()
        
        # Handle enharmonics
        if normalized in valid_keys:
            return normalized
        
        # Try to parse key from "C dorian" style
        parts = value.strip().split()
        if parts and parts[0].capitalize() in valid_keys:
            return parts[0].capitalize()
        
        print(f"Warning: Invalid key '{value}', falling back to 'C'")
        return 'C'
    
    @staticmethod
    def _validate_scale(value: str) -> str:
        """Validate scale name with fallback to 'ionian'."""
        valid_scales = {
            'ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian',
            'melodic_minor', 'harmonic_minor', 'altered', 'whole_tone', 'diminished',
            'major', 'minor', 'blues', 'pentatonic', 'bebop'
        }
        
        normalized = value.lower().strip().replace(' ', '_')
        
        # Handle common aliases
        aliases = {
            'major': 'ionian',
            'minor': 'aeolian',
            'natural_minor': 'aeolian',
        }
        
        if normalized in aliases:
            return aliases[normalized]
        
        if normalized in valid_scales:
            return normalized
        
        print(f"Warning: Invalid scale '{value}', falling back to 'ionian'")
        return 'ionian'
    
    @staticmethod
    def _validate_etude_type(value: str) -> EtudeType:
        """Validate etude type."""
        try:
            return EtudeType(value.lower().strip())
        except ValueError:
            # Try aliases
            aliases = {
                'melody': EtudeType.MELODIC,
                'harmony': EtudeType.HARMONIC,
                'intervals': EtudeType.INTERVALLIC,
                'chord-melody': EtudeType.CHORD_MELODY,
                'chordmelody': EtudeType.CHORD_MELODY,
                '251': EtudeType.TWO_FIVE_ONE,
                'ii-v-i': EtudeType.TWO_FIVE_ONE,
            }
            if value.lower() in aliases:
                return aliases[value.lower()]
            
            print(f"Warning: Invalid etude_type '{value}', falling back to 'melodic'")
            return EtudeType.MELODIC
    
    @staticmethod
    def _validate_difficulty(value: str) -> Difficulty:
        """Validate difficulty."""
        try:
            return Difficulty(value.lower().strip())
        except ValueError:
            # Try aliases
            aliases = {
                'easy': Difficulty.BEGINNER,
                'medium': Difficulty.INTERMEDIATE,
                'hard': Difficulty.ADVANCED,
            }
            if value.lower() in aliases:
                return aliases[value.lower()]
            
            print(f"Warning: Invalid difficulty '{value}', falling back to 'intermediate'")
            return Difficulty.INTERMEDIATE
    
    @staticmethod
    def _validate_string_set(value: str) -> StringSet:
        """Validate string set."""
        try:
            return StringSet(value.strip())
        except ValueError:
            print(f"Warning: Invalid string_set '{value}', falling back to 'auto'")
            return StringSet.AUTO
    
    @staticmethod
    def _validate_mode(value: str) -> EtudeMode:
        """Validate voice-leading mode."""
        try:
            return EtudeMode(value.lower().strip())
        except ValueError:
            print(f"Warning: Invalid mode '{value}', falling back to 'functional'")
            return EtudeMode.FUNCTIONAL
    
    @staticmethod
    def _validate_rhythmic_style(value: str) -> RhythmicStyle:
        """Validate rhythmic style."""
        try:
            return RhythmicStyle(value.lower().strip())
        except ValueError:
            aliases = {
                'jazz': RhythmicStyle.SWING,
                'swing eighths': RhythmicStyle.SWING,
            }
            if value.lower() in aliases:
                return aliases[value.lower()]
            
            print(f"Warning: Invalid rhythmic_style '{value}', falling back to 'straight'")
            return RhythmicStyle.STRAIGHT
    
    def _validate_length(self, value: int) -> int:
        """Validate bar length based on difficulty."""
        settings = DIFFICULTY_SETTINGS[self._difficulty_enum]
        max_bars = settings['max_bars']
        
        if value < 1:
            return 4
        if value > max_bars:
            print(f"Warning: Length {value} exceeds max for {self.difficulty}, capping at {max_bars}")
            return max_bars
        return value
    
    def _validate_tempo(self, value: int) -> int:
        """Validate tempo based on difficulty."""
        settings = DIFFICULTY_SETTINGS[self._difficulty_enum]
        max_tempo = settings['max_tempo']
        
        if value < 40:
            return 60
        if value > max_tempo:
            print(f"Warning: Tempo {value} exceeds max for {self.difficulty}, capping at {max_tempo}")
            return max_tempo
        return value
    
    def _generate_title(self) -> str:
        """Generate a title for the etude."""
        type_names = {
            EtudeType.MELODIC: "Melodic",
            EtudeType.HARMONIC: "Harmonic",
            EtudeType.INTERVALLIC: "Intervallic",
            EtudeType.CHORD_MELODY: "Chord-Melody",
            EtudeType.POSITION: "Position",
            EtudeType.STRING_SET: "String-Set",
            EtudeType.TWO_FIVE_ONE: "ii-V-I",
            EtudeType.INVERSION_CYCLE: "Inversion Cycle",
            EtudeType.SCALAR: "Scalar",
        }
        
        type_name = type_names.get(self._etude_type_enum, "Open Triad")
        return f"{self.key} {self.scale.capitalize()} {type_name} Etude"
    
    def get_difficulty_settings(self) -> Dict[str, Any]:
        """Get settings for the current difficulty level."""
        return DIFFICULTY_SETTINGS[self._difficulty_enum]
    
    def get_position_constraints(self) -> Optional[PositionConstraints]:
        """Get position constraints if position is specified."""
        if self.position is not None:
            settings = self.get_difficulty_settings()
            span = settings['max_fret_span']
            return PositionConstraints.from_position(self.position, span)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'key': self.key,
            'scale': self.scale,
            'progression': self.progression,
            'etude_type': self.etude_type,
            'difficulty': self.difficulty,
            'string_set': self.string_set,
            'position': self.position,
            'mode': self.mode,
            'rhythmic_style': self.rhythmic_style,
            'tempo': self.tempo,
            'length': self.length,
            'time_signature': self.time_signature,
            'title': self.title,
        }
    
    def to_json(self) -> str:
        """Convert config to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EtudeConfig':
        """Create config from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EtudeConfig':
        """Create config from JSON string."""
        return cls.from_dict(json.loads(json_str))


def validate_config(config: EtudeConfig) -> List[str]:
    """
    Validate a configuration and return any warnings.
    
    Args:
        config: EtudeConfig to validate
        
    Returns:
        List of warning messages (empty if valid)
    """
    warnings = []
    
    # Check rhythmic style is appropriate for difficulty
    settings = config.get_difficulty_settings()
    if config.rhythmic_style not in settings['allowed_rhythms']:
        warnings.append(
            f"Rhythmic style '{config.rhythmic_style}' may be challenging for {config.difficulty} level"
        )
    
    # Check progression is provided for ii-V-I etude
    if config._etude_type_enum == EtudeType.TWO_FIVE_ONE and not config.progression:
        warnings.append("ii-V-I etude type works best with a chord progression")
    
    # Check string set for chord-melody
    if config._etude_type_enum == EtudeType.CHORD_MELODY:
        if config._string_set_enum == StringSet.HIGH:
            warnings.append("String set 6-4 may be low for chord-melody voicings")
    
    return warnings


def create_config(**kwargs) -> EtudeConfig:
    """
    Factory function to create an EtudeConfig with validation.
    
    All invalid inputs are replaced with sensible defaults.
    """
    return EtudeConfig(**kwargs)

