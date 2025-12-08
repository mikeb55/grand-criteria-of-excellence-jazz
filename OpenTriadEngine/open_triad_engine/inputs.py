"""
Inputs Module for Open Triad Engine
====================================

Handles input validation, configuration, and fallbacks for all engine parameters.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
import json


class TriadSource(Enum):
    """Source for generating triads."""
    DIATONIC = "diatonic"
    CHROMATIC = "chromatic"
    PROGRESSION = "progression"
    USER_DEFINED = "user_defined"
    TONALITY_VAULT = "tonality_vault"


class StringSet(Enum):
    """Guitar string sets for voicings."""
    HIGH = "6-4"      # Strings 6, 5, 4 (low E, A, D)
    MIDDLE = "5-3"    # Strings 5, 4, 3 (A, D, G)
    LOW = "4-2"       # Strings 4, 3, 2 (D, G, B)
    AUTO = "auto"     # Engine decides based on register


class EngineMode(Enum):
    """Operating modes for the engine."""
    MELODIC = "melodic"
    HARMONIC = "harmonic"
    CHORD_MELODY = "chord_melody"
    COUNTERPOINT = "counterpoint"
    ORCHESTRATION = "orchestration"


class VoiceLeadingPriority(Enum):
    """Priority for voice leading decisions."""
    SMOOTH = "smooth"        # Minimize motion, prefer steps
    INTERVALLIC = "intervallic"  # Allow wider intervals for color
    MIXED = "mixed"          # Balance between smooth and intervallic


class TriadTypeInput(Enum):
    """Valid triad type inputs."""
    MAJOR = "major"
    MINOR = "minor"
    DIM = "dim"
    AUG = "aug"
    SUS = "sus"
    SUS2 = "sus2"
    SUS4 = "sus4"
    HYBRID = "hybrid"


@dataclass
class RegisterLimits:
    """
    Defines the pitch range limits for the engine.
    
    Attributes:
        low: Lowest allowed pitch (MIDI number or note string)
        high: Highest allowed pitch (MIDI number or note string)
    """
    low: Union[int, str] = 36   # C2 (cello low)
    high: Union[int, str] = 84  # C6 (violin high)
    
    def __post_init__(self):
        # Convert note strings to MIDI numbers
        if isinstance(self.low, str):
            self.low = self._note_to_midi(self.low)
        if isinstance(self.high, str):
            self.high = self._note_to_midi(self.high)
        
        # Validate range
        if self.low >= self.high:
            raise ValueError(f"Low register ({self.low}) must be less than high ({self.high})")
    
    @staticmethod
    def _note_to_midi(note_str: str) -> int:
        """Convert note string to MIDI number."""
        from .core import Note
        note = Note.from_string(note_str)
        return note.midi_number
    
    def contains(self, midi_number: int) -> bool:
        """Check if a MIDI number is within the register limits."""
        return self.low <= midi_number <= self.high
    
    def clamp(self, midi_number: int) -> int:
        """Clamp a MIDI number to the register limits."""
        return max(self.low, min(self.high, midi_number))
    
    @property
    def range(self) -> int:
        """Return the range in semitones."""
        return self.high - self.low


@dataclass
class InstrumentRegister:
    """Register definitions for orchestration."""
    name: str
    low: int   # MIDI number
    high: int  # MIDI number
    preferred_low: int = None  # Comfortable low
    preferred_high: int = None # Comfortable high
    
    def __post_init__(self):
        if self.preferred_low is None:
            self.preferred_low = self.low + 5
        if self.preferred_high is None:
            self.preferred_high = self.high - 5


# Common instrument registers
INSTRUMENT_REGISTERS = {
    'violin': InstrumentRegister('violin', 55, 103, 60, 96),      # G3 to G7
    'viola': InstrumentRegister('viola', 48, 91, 53, 84),         # C3 to G6
    'cello': InstrumentRegister('cello', 36, 76, 41, 72),         # C2 to E5
    'bass': InstrumentRegister('bass', 28, 60, 33, 55),           # E1 to C4
    'flute': InstrumentRegister('flute', 60, 96, 65, 91),         # C4 to C7
    'clarinet': InstrumentRegister('clarinet', 50, 94, 55, 89),   # D3 to Bb6
    'guitar': InstrumentRegister('guitar', 40, 88, 45, 81),       # E2 to E6
    'piano': InstrumentRegister('piano', 21, 108, 36, 96),        # A0 to C8
}


@dataclass
class EngineConfig:
    """
    Complete configuration for the Open Triad Engine.
    
    All parameters are validated upon initialization with fallbacks
    for invalid or missing values.
    """
    # Triad configuration
    triad_type: str = "major"
    source: str = "diatonic"
    
    # Instrument/voicing configuration
    string_set: str = "auto"
    
    # Engine mode
    mode: str = "melodic"
    
    # Voice leading
    priority: str = "smooth"
    
    # Scale mapping
    scale_map: List[str] = field(default_factory=lambda: ["ionian"])
    
    # Register limits
    register_limits: Dict[str, Any] = field(default_factory=lambda: {"low": 36, "high": 84})
    
    # Advanced options
    allow_parallel_fifths: bool = False
    allow_parallel_octaves: bool = False
    prefer_contrary_motion: bool = True
    max_voice_leap: int = 12  # Maximum semitones for a single voice
    
    # Instrument assignment (for orchestration mode)
    instruments: Dict[str, str] = field(default_factory=lambda: {
        "top": "violin",
        "middle": "viola", 
        "bottom": "cello"
    })
    
    # Validated/normalized values (set after validation)
    _validated: bool = field(default=False, repr=False)
    
    def __post_init__(self):
        self._validate_and_normalize()
    
    def _validate_and_normalize(self):
        """Validate all inputs and apply fallbacks."""
        self.triad_type = self._validate_triad_type(self.triad_type)
        self.source = self._validate_source(self.source)
        self.string_set = self._validate_string_set(self.string_set)
        self.mode = self._validate_mode(self.mode)
        self.priority = self._validate_priority(self.priority)
        self.scale_map = self._validate_scale_map(self.scale_map)
        self.register_limits = self._validate_register_limits(self.register_limits)
        self._validated = True
    
    @staticmethod
    def _validate_triad_type(value: str) -> str:
        """Validate triad type with fallback to 'major'."""
        valid = {'major', 'minor', 'dim', 'aug', 'sus', 'sus2', 'sus4', 'hybrid'}
        normalized = value.lower().strip()
        if normalized not in valid:
            print(f"Warning: Invalid triad_type '{value}', falling back to 'major'")
            return 'major'
        # Normalize 'sus' to 'sus4'
        if normalized == 'sus':
            return 'sus4'
        return normalized
    
    @staticmethod
    def _validate_source(value: str) -> str:
        """Validate source with fallback to 'diatonic'."""
        valid = {'diatonic', 'chromatic', 'progression', 'user_defined', 'tonality_vault'}
        normalized = value.lower().strip()
        if normalized not in valid:
            print(f"Warning: Invalid source '{value}', falling back to 'diatonic'")
            return 'diatonic'
        return normalized
    
    @staticmethod
    def _validate_string_set(value: str) -> str:
        """Validate string set with fallback to 'auto'."""
        valid = {'6-4', '5-3', '4-2', 'auto'}
        normalized = value.lower().strip()
        if normalized not in valid:
            print(f"Warning: Invalid string_set '{value}', falling back to 'auto'")
            return 'auto'
        return normalized
    
    @staticmethod
    def _validate_mode(value: str) -> str:
        """Validate mode with fallback to 'melodic'."""
        valid = {'melodic', 'harmonic', 'chord_melody', 'counterpoint', 'orchestration'}
        normalized = value.lower().strip()
        if normalized not in valid:
            print(f"Warning: Invalid mode '{value}', falling back to 'melodic'")
            return 'melodic'
        return normalized
    
    @staticmethod
    def _validate_priority(value: str) -> str:
        """Validate priority with fallback to 'smooth'."""
        valid = {'smooth', 'intervallic', 'mixed'}
        normalized = value.lower().strip()
        if normalized not in valid:
            print(f"Warning: Invalid priority '{value}', falling back to 'smooth'")
            return 'smooth'
        return normalized
    
    @staticmethod
    def _validate_scale_map(value: List[str]) -> List[str]:
        """Validate scale map with fallback to ['ionian']."""
        if not value or not isinstance(value, list):
            print("Warning: Invalid scale_map, falling back to ['ionian']")
            return ['ionian']
        return [s.lower().strip() for s in value]
    
    @staticmethod
    def _validate_register_limits(value: Dict[str, Any]) -> Dict[str, Any]:
        """Validate register limits with fallbacks."""
        default = {"low": 36, "high": 84}
        
        if not isinstance(value, dict):
            print("Warning: Invalid register_limits, falling back to defaults")
            return default
        
        result = {}
        result['low'] = value.get('low', default['low'])
        result['high'] = value.get('high', default['high'])
        
        # Ensure low < high
        if result['low'] >= result['high']:
            print("Warning: register_limits low >= high, using defaults")
            return default
        
        return result
    
    def get_register_limits_obj(self) -> RegisterLimits:
        """Return a RegisterLimits object from the config."""
        return RegisterLimits(
            low=self.register_limits['low'],
            high=self.register_limits['high']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'triad_type': self.triad_type,
            'source': self.source,
            'string_set': self.string_set,
            'mode': self.mode,
            'priority': self.priority,
            'scale_map': self.scale_map,
            'register_limits': self.register_limits,
            'allow_parallel_fifths': self.allow_parallel_fifths,
            'allow_parallel_octaves': self.allow_parallel_octaves,
            'prefer_contrary_motion': self.prefer_contrary_motion,
            'max_voice_leap': self.max_voice_leap,
            'instruments': self.instruments,
        }
    
    def to_json(self) -> str:
        """Convert config to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EngineConfig':
        """Create config from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EngineConfig':
        """Create config from JSON string."""
        return cls.from_dict(json.loads(json_str))


class InputValidator:
    """
    Utility class for validating individual inputs.
    Provides static methods for common validations.
    """
    
    # Valid scale names recognized by the engine
    VALID_SCALES = {
        # Major modes
        'ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian',
        # Melodic minor modes
        'melodic_minor', 'dorian_b2', 'lydian_augmented', 'lydian_dominant',
        'mixolydian_b6', 'locrian_nat2', 'altered', 'super_locrian',
        # Harmonic minor modes
        'harmonic_minor', 'locrian_nat6', 'ionian_augmented', 'dorian_sharp4',
        'phrygian_dominant', 'lydian_sharp2', 'ultra_locrian',
        # Symmetric scales
        'whole_tone', 'diminished', 'octatonic', 'half_whole', 'whole_half',
        'augmented',
        # Pentatonics and blues
        'major_pentatonic', 'minor_pentatonic', 'blues', 'blues_major',
        # Other scales
        'chromatic', 'bebop_dominant', 'bebop_major', 'bebop_minor',
    }
    
    @classmethod
    def validate_scale_name(cls, scale: str) -> bool:
        """Check if a scale name is valid."""
        return scale.lower().strip().replace(' ', '_') in cls.VALID_SCALES
    
    @classmethod
    def normalize_scale_name(cls, scale: str) -> str:
        """Normalize a scale name to standard format."""
        normalized = scale.lower().strip().replace(' ', '_')
        if normalized in cls.VALID_SCALES:
            return normalized
        # Try common aliases
        aliases = {
            'major': 'ionian',
            'minor': 'aeolian',
            'natural_minor': 'aeolian',
            'jazz_minor': 'melodic_minor',
            'dom_bebop': 'bebop_dominant',
            'diminished_half_whole': 'half_whole',
            'diminished_whole_half': 'whole_half',
            'super_locrian': 'altered',
        }
        return aliases.get(normalized, 'ionian')
    
    @staticmethod
    def validate_chord_progression(progression: List[str]) -> bool:
        """
        Validate a chord progression input.
        
        Args:
            progression: List of chord symbols (e.g., ['Dm7', 'G7', 'Cmaj7'])
            
        Returns:
            True if all chord symbols are parseable
        """
        import re
        # Basic chord symbol pattern
        pattern = r'^[A-G][#b]?(m|maj|min|dim|aug|sus[24]?|\+|°|ø)?[0-9]*.*$'
        
        for chord in progression:
            if not re.match(pattern, chord.strip(), re.IGNORECASE):
                return False
        return True
    
    @staticmethod
    def validate_midi_range(low: int, high: int) -> bool:
        """Validate MIDI number range (0-127)."""
        return 0 <= low < high <= 127
    
    @staticmethod
    def parse_note_or_midi(value: Union[str, int]) -> int:
        """
        Parse a note string or MIDI number to MIDI number.
        
        Args:
            value: Note string (e.g., 'C4') or MIDI number
            
        Returns:
            MIDI note number
        """
        if isinstance(value, int):
            return max(0, min(127, value))
        
        from .core import Note
        note = Note.from_string(str(value))
        return note.midi_number


def create_config(**kwargs) -> EngineConfig:
    """
    Factory function to create an EngineConfig with validation.
    
    All invalid inputs are replaced with sensible defaults.
    """
    return EngineConfig(**kwargs)


def validate_inputs(**kwargs) -> Dict[str, Any]:
    """
    Validate inputs and return a dictionary of validated values.
    
    Useful for checking inputs before creating a full config.
    """
    config = EngineConfig(**kwargs)
    return config.to_dict()

