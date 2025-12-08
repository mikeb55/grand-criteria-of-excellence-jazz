"""
Core Music Theory Classes for Open Triad Engine
================================================

Fundamental building blocks: Note, Interval, Triad, and related enums.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import copy


# Chromatic note names (sharps preferred)
CHROMATIC_NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Enharmonic equivalents
ENHARMONIC_MAP = {
    'Db': 'C#', 'Eb': 'D#', 'Fb': 'E', 'Gb': 'F#', 'Ab': 'G#', 
    'Bb': 'A#', 'Cb': 'B', 'E#': 'F', 'B#': 'C',
    'C##': 'D', 'D##': 'E', 'F##': 'G', 'G##': 'A', 'A##': 'B'
}

# Interval names
INTERVAL_NAMES = {
    0: 'P1', 1: 'm2', 2: 'M2', 3: 'm3', 4: 'M3', 5: 'P4',
    6: 'TT', 7: 'P5', 8: 'm6', 9: 'M6', 10: 'm7', 11: 'M7', 12: 'P8'
}


class TriadType(Enum):
    """Types of triads supported by the engine."""
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "dim"
    AUGMENTED = "aug"
    SUSPENDED_2 = "sus2"
    SUSPENDED_4 = "sus4"
    HYBRID = "hybrid"  # For non-standard constructions


class Inversion(Enum):
    """Triad inversions."""
    ROOT = 0
    FIRST = 1
    SECOND = 2


class VoicingType(Enum):
    """Types of voicings."""
    CLOSED = "closed"
    OPEN_DROP2 = "open_drop2"
    OPEN_DROP3 = "open_drop3"
    SUPER_OPEN = "super_open"
    OPEN_ROOT = "open_root"
    OPEN_FIRST = "open_first"
    OPEN_SECOND = "open_second"


@dataclass
class Note:
    """
    Represents a musical note with pitch class and octave.
    
    Attributes:
        name: Note name (e.g., 'C', 'F#', 'Bb')
        octave: Octave number (middle C = C4)
    """
    name: str
    octave: int = 4
    
    def __post_init__(self):
        # Normalize enharmonics
        if self.name in ENHARMONIC_MAP:
            self.name = ENHARMONIC_MAP[self.name]
    
    @property
    def pitch_class(self) -> int:
        """Return pitch class (0-11) for the note."""
        return CHROMATIC_NOTES.index(self.name) if self.name in CHROMATIC_NOTES else -1
    
    @property
    def midi_number(self) -> int:
        """Return MIDI note number."""
        return (self.octave + 1) * 12 + self.pitch_class
    
    @property
    def frequency(self) -> float:
        """Return frequency in Hz (A4 = 440Hz)."""
        return 440.0 * (2 ** ((self.midi_number - 69) / 12))
    
    def transpose(self, semitones: int) -> 'Note':
        """Return a new Note transposed by the given semitones."""
        new_midi = self.midi_number + semitones
        new_octave = (new_midi // 12) - 1
        new_pc = new_midi % 12
        return Note(CHROMATIC_NOTES[new_pc], new_octave)
    
    def interval_to(self, other: 'Note') -> int:
        """Return the interval in semitones to another note."""
        return other.midi_number - self.midi_number
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Note):
            return False
        return self.midi_number == other.midi_number
    
    def __lt__(self, other: 'Note') -> bool:
        return self.midi_number < other.midi_number
    
    def __hash__(self) -> int:
        return hash(self.midi_number)
    
    def __repr__(self) -> str:
        return f"{self.name}{self.octave}"
    
    def __str__(self) -> str:
        return f"{self.name}{self.octave}"
    
    @classmethod
    def from_midi(cls, midi_number: int) -> 'Note':
        """Create a Note from a MIDI number."""
        octave = (midi_number // 12) - 1
        pc = midi_number % 12
        return cls(CHROMATIC_NOTES[pc], octave)
    
    @classmethod
    def from_string(cls, note_str: str) -> 'Note':
        """Parse a note string like 'C4', 'F#3', 'Bb5'."""
        # Handle flats/sharps in name
        if len(note_str) >= 2 and note_str[1] in '#b':
            if len(note_str) >= 3 and note_str[2] in '#b':
                name = note_str[:3]
                octave_str = note_str[3:]
            else:
                name = note_str[:2]
                octave_str = note_str[2:]
        else:
            name = note_str[0]
            octave_str = note_str[1:]
        
        octave = int(octave_str) if octave_str else 4
        return cls(name, octave)


@dataclass
class Interval:
    """
    Represents a musical interval.
    
    Attributes:
        semitones: Number of semitones
        quality: Interval quality name (e.g., 'M3', 'm7')
    """
    semitones: int
    
    @property
    def quality(self) -> str:
        """Return the interval quality name."""
        normalized = self.semitones % 12
        return INTERVAL_NAMES.get(normalized, f'{self.semitones}st')
    
    @property
    def is_consonant(self) -> bool:
        """Check if interval is consonant."""
        consonants = {0, 3, 4, 5, 7, 8, 9, 12}  # P1, m3, M3, P4, P5, m6, M6, P8
        return (self.semitones % 12) in consonants
    
    @property
    def is_step(self) -> bool:
        """Check if interval is a step (m2 or M2)."""
        return abs(self.semitones) in {1, 2}
    
    @property
    def direction(self) -> int:
        """Return direction: 1 for up, -1 for down, 0 for unison."""
        if self.semitones > 0:
            return 1
        elif self.semitones < 0:
            return -1
        return 0
    
    def __repr__(self) -> str:
        return f"Interval({self.quality}, {self.semitones}st)"


@dataclass
class Triad:
    """
    Represents a triad with root, third, and fifth.
    
    Supports closed and open voicings, inversions, and transformations.
    
    Attributes:
        root: The root note of the triad
        triad_type: Type of triad (major, minor, dim, aug, sus)
        inversion: Current inversion (root, first, second)
        voicing_type: Current voicing (closed, open_drop2, etc.)
        voices: List of notes in current voicing [bottom, middle, top]
    """
    root: Note
    triad_type: TriadType = TriadType.MAJOR
    inversion: Inversion = Inversion.ROOT
    voicing_type: VoicingType = VoicingType.CLOSED
    voices: List[Note] = field(default_factory=list)
    
    # Interval patterns for each triad type (from root)
    TRIAD_INTERVALS: Dict[TriadType, Tuple[int, int]] = field(default=None, repr=False)
    
    def __post_init__(self):
        # Define intervals for each triad type
        self.TRIAD_INTERVALS = {
            TriadType.MAJOR: (4, 7),        # M3, P5
            TriadType.MINOR: (3, 7),        # m3, P5
            TriadType.DIMINISHED: (3, 6),   # m3, d5
            TriadType.AUGMENTED: (4, 8),    # M3, A5
            TriadType.SUSPENDED_2: (2, 7),  # M2, P5
            TriadType.SUSPENDED_4: (5, 7),  # P4, P5
            TriadType.HYBRID: (4, 7),       # Default to major
        }
        
        # Build voices if not provided
        if not self.voices:
            self._build_closed_voicing()
    
    def _build_closed_voicing(self):
        """Build a closed position voicing based on triad type and inversion."""
        intervals = self.TRIAD_INTERVALS[self.triad_type]
        
        # Build root position notes
        root = self.root
        third = self.root.transpose(intervals[0])
        fifth = self.root.transpose(intervals[1])
        
        # Apply inversion
        if self.inversion == Inversion.ROOT:
            self.voices = [root, third, fifth]
        elif self.inversion == Inversion.FIRST:
            # Third in bass, root up an octave
            self.voices = [third, fifth, root.transpose(12)]
        elif self.inversion == Inversion.SECOND:
            # Fifth in bass, root and third up an octave
            self.voices = [fifth, root.transpose(12), third.transpose(12)]
        
        self.voicing_type = VoicingType.CLOSED
    
    @property
    def bass_note(self) -> Note:
        """Return the lowest note."""
        return min(self.voices)
    
    @property
    def top_note(self) -> Note:
        """Return the highest note."""
        return max(self.voices)
    
    @property
    def middle_note(self) -> Note:
        """Return the middle note."""
        sorted_voices = sorted(self.voices)
        return sorted_voices[1] if len(sorted_voices) >= 3 else sorted_voices[0]
    
    @property
    def outer_interval(self) -> int:
        """Return the interval between bass and top in semitones."""
        return self.top_note.midi_number - self.bass_note.midi_number
    
    @property
    def intervals(self) -> List[int]:
        """Return list of intervals between adjacent voices."""
        sorted_voices = sorted(self.voices)
        return [sorted_voices[i+1].midi_number - sorted_voices[i].midi_number 
                for i in range(len(sorted_voices) - 1)]
    
    @property
    def symbol(self) -> str:
        """Return chord symbol (e.g., 'Cmaj', 'Dm', 'Fdim')."""
        type_symbols = {
            TriadType.MAJOR: '',
            TriadType.MINOR: 'm',
            TriadType.DIMINISHED: 'dim',
            TriadType.AUGMENTED: 'aug',
            TriadType.SUSPENDED_2: 'sus2',
            TriadType.SUSPENDED_4: 'sus4',
            TriadType.HYBRID: 'hybrid',
        }
        return f"{self.root.name}{type_symbols[self.triad_type]}"
    
    @property
    def is_open(self) -> bool:
        """Check if voicing is open (spans more than an octave)."""
        return self.outer_interval > 12
    
    @property
    def contour(self) -> str:
        """Return contour signature based on interval directions."""
        intervals = self.intervals
        if len(intervals) < 2:
            return "flat"
        
        directions = []
        for iv in intervals:
            if iv > 7:
                directions.append('W')  # Wide
            elif iv > 4:
                directions.append('M')  # Medium
            else:
                directions.append('N')  # Narrow
        return '-'.join(directions)
    
    def copy(self) -> 'Triad':
        """Return a deep copy of the triad."""
        return Triad(
            root=Note(self.root.name, self.root.octave),
            triad_type=self.triad_type,
            inversion=self.inversion,
            voicing_type=self.voicing_type,
            voices=[Note(n.name, n.octave) for n in self.voices]
        )
    
    def transpose(self, semitones: int) -> 'Triad':
        """Return a new Triad transposed by the given semitones."""
        new_triad = self.copy()
        new_triad.root = self.root.transpose(semitones)
        new_triad.voices = [v.transpose(semitones) for v in self.voices]
        return new_triad
    
    def set_inversion(self, inversion: Inversion) -> 'Triad':
        """Return a new Triad with the specified inversion."""
        new_triad = Triad(
            root=Note(self.root.name, self.root.octave),
            triad_type=self.triad_type,
            inversion=inversion,
            voicing_type=VoicingType.CLOSED
        )
        return new_triad
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'root': str(self.root),
            'triad_type': self.triad_type.value,
            'inversion': self.inversion.value,
            'voicing_type': self.voicing_type.value,
            'voices': [str(v) for v in self.voices],
            'symbol': self.symbol,
            'intervals': self.intervals,
            'contour': self.contour,
            'is_open': self.is_open
        }
    
    @classmethod
    def from_symbol(cls, symbol: str, octave: int = 4) -> 'Triad':
        """
        Create a Triad from a chord symbol.
        
        Examples: 'C', 'Dm', 'F#dim', 'Gbaug', 'Asus4'
        """
        # Parse root note
        if len(symbol) >= 2 and symbol[1] in '#b':
            root_name = symbol[:2]
            quality_str = symbol[2:]
        else:
            root_name = symbol[0]
            quality_str = symbol[1:]
        
        # Determine triad type
        quality_str = quality_str.lower()
        if quality_str.startswith('dim') or quality_str.startswith('°'):
            triad_type = TriadType.DIMINISHED
        elif quality_str.startswith('aug') or quality_str.startswith('+'):
            triad_type = TriadType.AUGMENTED
        elif quality_str.startswith('sus4'):
            triad_type = TriadType.SUSPENDED_4
        elif quality_str.startswith('sus2'):
            triad_type = TriadType.SUSPENDED_2
        elif quality_str.startswith('m') or quality_str.startswith('-'):
            triad_type = TriadType.MINOR
        else:
            triad_type = TriadType.MAJOR
        
        root = Note(root_name, octave)
        return cls(root=root, triad_type=triad_type)
    
    def __repr__(self) -> str:
        voices_str = ', '.join(str(v) for v in self.voices)
        return f"Triad({self.symbol}, {self.voicing_type.value}, [{voices_str}])"
    
    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class VoiceMotion:
    """
    Describes the motion of a single voice between two triads.
    
    Attributes:
        voice_name: 'bass', 'middle', or 'top'
        from_note: Starting note
        to_note: Ending note
        interval: Semitone distance (positive = up, negative = down)
        motion_type: 'step', 'skip', 'leap', 'common_tone'
    """
    voice_name: str
    from_note: Note
    to_note: Note
    interval: int
    
    @property
    def motion_type(self) -> str:
        """Categorize the motion."""
        abs_interval = abs(self.interval)
        if abs_interval == 0:
            return 'common_tone'
        elif abs_interval <= 2:
            return 'step'
        elif abs_interval <= 4:
            return 'skip'
        else:
            return 'leap'
    
    @property
    def direction(self) -> str:
        """Return direction as string."""
        if self.interval > 0:
            return 'ascending'
        elif self.interval < 0:
            return 'descending'
        return 'static'
    
    def __repr__(self) -> str:
        return f"VoiceMotion({self.voice_name}: {self.from_note} → {self.to_note}, {self.motion_type})"


# Factory functions for common operations
def create_triad(root: str, triad_type: str = 'major', octave: int = 4) -> Triad:
    """
    Convenience function to create a triad.
    
    Args:
        root: Root note name (e.g., 'C', 'F#', 'Bb')
        triad_type: 'major', 'minor', 'dim', 'aug', 'sus2', 'sus4'
        octave: Octave for the root note
        
    Returns:
        A new Triad instance
    """
    type_map = {
        'major': TriadType.MAJOR, 'maj': TriadType.MAJOR,
        'minor': TriadType.MINOR, 'min': TriadType.MINOR, 'm': TriadType.MINOR,
        'dim': TriadType.DIMINISHED, 'diminished': TriadType.DIMINISHED,
        'aug': TriadType.AUGMENTED, 'augmented': TriadType.AUGMENTED,
        'sus2': TriadType.SUSPENDED_2,
        'sus4': TriadType.SUSPENDED_4, 'sus': TriadType.SUSPENDED_4,
    }
    
    tt = type_map.get(triad_type.lower(), TriadType.MAJOR)
    return Triad(root=Note(root, octave), triad_type=tt)


def interval_between(note1: Note, note2: Note) -> Interval:
    """Calculate the interval between two notes."""
    semitones = note2.midi_number - note1.midi_number
    return Interval(semitones)

