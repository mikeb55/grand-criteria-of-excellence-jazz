"""
Output Shape Modules for Open Triad Engine
==========================================

Implements:
1. Shape Bundles - grouped open triads with contour signatures
2. Melodic Pattern Generator - arpeggios, rotations, intervallic patterns
3. Rhythmic Templates - straight, syncopated, triplet, polyrhythmic
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
from enum import Enum
import itertools

from .core import Note, Triad, Inversion
from .transformations import InversionEngine, ClosedToOpenConverter, DropVoicing


class ContourType(Enum):
    """Types of melodic contour."""
    ASCENDING = "ascending"
    DESCENDING = "descending"
    ARCH = "arch"
    VALLEY = "valley"
    WAVE = "wave"
    FLAT = "flat"


class ArpeggioPattern(Enum):
    """Standard arpeggio patterns."""
    UP = "up"
    DOWN = "down"
    UP_DOWN = "up_down"
    DOWN_UP = "down_up"
    ALTERNATING = "alternating"


class RhythmType(Enum):
    """Types of rhythmic patterns."""
    STRAIGHT = "straight"
    SYNCOPATED = "syncopated"
    TRIPLET = "triplet"
    POLYRHYTHMIC = "polyrhythmic"
    SWING = "swing"


@dataclass
class ContourSignature:
    """
    Describes the melodic contour of a pattern.
    
    Attributes:
        type: Overall contour type
        intervals: List of interval sizes
        directions: List of directions (+1, -1, 0)
        range: Total range in semitones
    """
    type: ContourType
    intervals: List[int]
    directions: List[int]
    range: int
    
    @classmethod
    def from_notes(cls, notes: List[Note]) -> 'ContourSignature':
        """Create a contour signature from a list of notes."""
        if len(notes) < 2:
            return cls(
                type=ContourType.FLAT,
                intervals=[],
                directions=[],
                range=0
            )
        
        intervals = []
        directions = []
        
        for i in range(len(notes) - 1):
            interval = notes[i + 1].midi_number - notes[i].midi_number
            intervals.append(interval)
            if interval > 0:
                directions.append(1)
            elif interval < 0:
                directions.append(-1)
            else:
                directions.append(0)
        
        # Determine contour type
        contour_type = cls._determine_contour_type(directions)
        
        # Calculate range
        midi_nums = [n.midi_number for n in notes]
        note_range = max(midi_nums) - min(midi_nums)
        
        return cls(
            type=contour_type,
            intervals=intervals,
            directions=directions,
            range=note_range
        )
    
    @staticmethod
    def _determine_contour_type(directions: List[int]) -> ContourType:
        """Determine the overall contour type from directions."""
        if not directions:
            return ContourType.FLAT
        
        # All ascending
        if all(d >= 0 for d in directions) and any(d > 0 for d in directions):
            return ContourType.ASCENDING
        
        # All descending
        if all(d <= 0 for d in directions) and any(d < 0 for d in directions):
            return ContourType.DESCENDING
        
        # Arch: goes up then down
        peak_idx = None
        for i, d in enumerate(directions):
            if d < 0:
                peak_idx = i
                break
        
        if peak_idx and peak_idx > 0:
            if all(d >= 0 for d in directions[:peak_idx]):
                if all(d <= 0 for d in directions[peak_idx:]):
                    return ContourType.ARCH
        
        # Valley: goes down then up
        trough_idx = None
        for i, d in enumerate(directions):
            if d > 0 and i > 0:
                trough_idx = i
                break
        
        if trough_idx:
            if all(d <= 0 for d in directions[:trough_idx]):
                if all(d >= 0 for d in directions[trough_idx:]):
                    return ContourType.VALLEY
        
        # Wave: alternating
        changes = sum(1 for i in range(len(directions) - 1) 
                     if directions[i] * directions[i + 1] < 0)
        if changes >= 2:
            return ContourType.WAVE
        
        return ContourType.FLAT
    
    def to_dict(self) -> Dict:
        return {
            'type': self.type.value,
            'intervals': self.intervals,
            'directions': self.directions,
            'range': self.range
        }


@dataclass
class ShapeBundle:
    """
    A bundle of related open triad voicings for a single chord.
    
    Contains all three open inversions plus their contour signatures.
    """
    root_triad: Triad
    open_root: Triad
    open_first: Triad
    open_second: Triad
    
    # Contour signatures
    root_contour: ContourSignature = field(default=None)
    first_contour: ContourSignature = field(default=None)
    second_contour: ContourSignature = field(default=None)
    
    def __post_init__(self):
        # Calculate contours if not provided
        if self.root_contour is None:
            self.root_contour = ContourSignature.from_notes(
                sorted(self.open_root.voices, key=lambda n: n.midi_number)
            )
        if self.first_contour is None:
            self.first_contour = ContourSignature.from_notes(
                sorted(self.open_first.voices, key=lambda n: n.midi_number)
            )
        if self.second_contour is None:
            self.second_contour = ContourSignature.from_notes(
                sorted(self.open_second.voices, key=lambda n: n.midi_number)
            )
    
    @classmethod
    def from_triad(cls, triad: Triad) -> 'ShapeBundle':
        """Create a shape bundle from a closed triad."""
        return cls(
            root_triad=triad,
            open_root=InversionEngine.open_root(triad),
            open_first=InversionEngine.open_first(triad),
            open_second=InversionEngine.open_second(triad)
        )
    
    def get_all_shapes(self) -> Dict[str, Triad]:
        """Get all shapes in the bundle."""
        return {
            'open_root': self.open_root,
            'open_first': self.open_first,
            'open_second': self.open_second
        }
    
    def get_shape_by_contour(self, contour_type: ContourType) -> Optional[Triad]:
        """Get a shape matching a specific contour type."""
        if self.root_contour.type == contour_type:
            return self.open_root
        if self.first_contour.type == contour_type:
            return self.open_first
        if self.second_contour.type == contour_type:
            return self.open_second
        return None
    
    def to_dict(self) -> Dict:
        return {
            'chord': self.root_triad.symbol,
            'shapes': {
                'open_root': self.open_root.to_dict(),
                'open_first': self.open_first.to_dict(),
                'open_second': self.open_second.to_dict()
            },
            'contours': {
                'open_root': self.root_contour.to_dict(),
                'open_first': self.first_contour.to_dict(),
                'open_second': self.second_contour.to_dict()
            }
        }


@dataclass
class MelodicPattern:
    """
    A melodic pattern derived from a triad.
    
    Attributes:
        notes: List of notes in the pattern
        pattern_type: Type of pattern (arpeggio, rotation, etc.)
        contour: Contour signature of the pattern
    """
    notes: List[Note]
    pattern_type: str
    contour: ContourSignature = field(default=None)
    
    def __post_init__(self):
        if self.contour is None:
            self.contour = ContourSignature.from_notes(self.notes)
    
    def transpose(self, semitones: int) -> 'MelodicPattern':
        """Transpose the pattern."""
        new_notes = [n.transpose(semitones) for n in self.notes]
        return MelodicPattern(new_notes, self.pattern_type)
    
    def retrograde(self) -> 'MelodicPattern':
        """Get the retrograde (reversed) pattern."""
        return MelodicPattern(list(reversed(self.notes)), f"{self.pattern_type}_retrograde")
    
    def invert(self, axis: Optional[int] = None) -> 'MelodicPattern':
        """Invert the pattern around an axis."""
        if not self.notes:
            return self
        
        if axis is None:
            axis = self.notes[0].midi_number
        
        new_notes = []
        for note in self.notes:
            distance = note.midi_number - axis
            new_midi = axis - distance
            new_notes.append(Note.from_midi(new_midi))
        
        return MelodicPattern(new_notes, f"{self.pattern_type}_inverted")
    
    def to_dict(self) -> Dict:
        return {
            'notes': [str(n) for n in self.notes],
            'pattern_type': self.pattern_type,
            'contour': self.contour.to_dict()
        }


class MelodicPatternGenerator:
    """
    Generates melodic patterns from triads.
    
    Supports:
    - Arpeggios (up, down, up-down, down-up)
    - Rotations (1-3-2, 3-1-2, etc.)
    - Intervallic skips
    - Contour wave patterns
    """
    
    @staticmethod
    def arpeggio(triad: Triad, pattern: ArpeggioPattern = ArpeggioPattern.UP) -> MelodicPattern:
        """Generate an arpeggio pattern from a triad."""
        sorted_notes = sorted(triad.voices, key=lambda n: n.midi_number)
        
        if pattern == ArpeggioPattern.UP:
            notes = sorted_notes
        elif pattern == ArpeggioPattern.DOWN:
            notes = list(reversed(sorted_notes))
        elif pattern == ArpeggioPattern.UP_DOWN:
            notes = sorted_notes + list(reversed(sorted_notes[:-1]))
        elif pattern == ArpeggioPattern.DOWN_UP:
            notes = list(reversed(sorted_notes)) + sorted_notes[1:]
        elif pattern == ArpeggioPattern.ALTERNATING:
            # Low, high, middle
            notes = [sorted_notes[0], sorted_notes[2], sorted_notes[1]]
        else:
            notes = sorted_notes
        
        return MelodicPattern(notes, f"arpeggio_{pattern.value}")
    
    @staticmethod
    def rotation(triad: Triad, pattern: Tuple[int, ...] = (1, 3, 2)) -> MelodicPattern:
        """
        Generate a rotated pattern from a triad.
        
        Pattern tuple indicates order: (1, 3, 2) means root, 5th, 3rd.
        """
        sorted_notes = sorted(triad.voices, key=lambda n: n.midi_number)
        
        notes = []
        for idx in pattern:
            if 1 <= idx <= len(sorted_notes):
                notes.append(sorted_notes[idx - 1])
        
        pattern_str = '-'.join(str(i) for i in pattern)
        return MelodicPattern(notes, f"rotation_{pattern_str}")
    
    @staticmethod
    def intervallic_skip(triad: Triad, skip_size: int = 2) -> MelodicPattern:
        """
        Generate a pattern with intervallic skips.
        
        Args:
            triad: Source triad
            skip_size: Number of scale degrees to skip
        """
        sorted_notes = sorted(triad.voices, key=lambda n: n.midi_number)
        
        # Extend to include octave doublings
        extended = sorted_notes + [n.transpose(12) for n in sorted_notes]
        
        notes = []
        idx = 0
        while idx < len(extended) and len(notes) < 6:
            notes.append(extended[idx])
            idx += skip_size
        
        return MelodicPattern(notes, f"skip_{skip_size}")
    
    @staticmethod
    def wave(triad: Triad, amplitude: int = 1) -> MelodicPattern:
        """
        Generate a wave contour pattern.
        
        Alternates between ascending and descending.
        """
        sorted_notes = sorted(triad.voices, key=lambda n: n.midi_number)
        
        # Create wave: bottom, top, middle, bottom+8va, top-8va, middle
        notes = [
            sorted_notes[0],
            sorted_notes[2],
            sorted_notes[1],
            sorted_notes[0].transpose(12),
            sorted_notes[2],
            sorted_notes[1]
        ]
        
        return MelodicPattern(notes, "wave")
    
    @staticmethod
    def pendulum(triad: Triad) -> MelodicPattern:
        """Generate a pendulum pattern (alternating extreme notes)."""
        sorted_notes = sorted(triad.voices, key=lambda n: n.midi_number)
        
        low = sorted_notes[0]
        high = sorted_notes[2]
        mid = sorted_notes[1]
        
        notes = [low, high, low, mid, high, mid]
        return MelodicPattern(notes, "pendulum")
    
    @classmethod
    def all_patterns(cls, triad: Triad) -> List[MelodicPattern]:
        """Generate all standard patterns for a triad."""
        patterns = []
        
        # Arpeggios
        for arp in ArpeggioPattern:
            patterns.append(cls.arpeggio(triad, arp))
        
        # Rotations
        rotations = [
            (1, 2, 3), (1, 3, 2), (2, 1, 3),
            (2, 3, 1), (3, 1, 2), (3, 2, 1)
        ]
        for rot in rotations:
            patterns.append(cls.rotation(triad, rot))
        
        # Skips
        for skip in [2, 3]:
            patterns.append(cls.intervallic_skip(triad, skip))
        
        # Special patterns
        patterns.append(cls.wave(triad))
        patterns.append(cls.pendulum(triad))
        
        return patterns


@dataclass
class RhythmicNote:
    """
    A note with rhythmic information.
    
    Attributes:
        note: The pitch
        duration: Duration in beats
        offset: Offset from beat in fractions
        velocity: Dynamic level (0-127)
    """
    note: Note
    duration: float = 1.0
    offset: float = 0.0
    velocity: int = 100


@dataclass
class RhythmicTemplate:
    """
    A rhythmic template that can be applied to melodic patterns.
    
    Attributes:
        name: Template name
        type: Rhythm type (straight, syncopated, etc.)
        durations: List of durations in beats
        offsets: List of offsets from beat
        accents: List of accent positions
    """
    name: str
    type: RhythmType
    durations: List[float]
    offsets: List[float] = field(default_factory=list)
    accents: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.offsets:
            self.offsets = [0.0] * len(self.durations)
    
    def apply_to_pattern(
        self, 
        pattern: MelodicPattern,
        base_velocity: int = 100,
        accent_velocity: int = 120
    ) -> List[RhythmicNote]:
        """Apply this rhythm template to a melodic pattern."""
        notes = pattern.notes
        result = []
        
        for i, note in enumerate(notes):
            idx = i % len(self.durations)
            
            velocity = accent_velocity if i in self.accents else base_velocity
            
            rhythmic_note = RhythmicNote(
                note=note,
                duration=self.durations[idx],
                offset=self.offsets[idx],
                velocity=velocity
            )
            result.append(rhythmic_note)
        
        return result
    
    @classmethod
    def straight_quarters(cls) -> 'RhythmicTemplate':
        """Create a straight quarter note template."""
        return cls(
            name="Straight Quarters",
            type=RhythmType.STRAIGHT,
            durations=[1.0, 1.0, 1.0, 1.0],
            accents=[0]  # Accent first beat
        )
    
    @classmethod
    def straight_eighths(cls) -> 'RhythmicTemplate':
        """Create a straight eighth note template."""
        return cls(
            name="Straight Eighths",
            type=RhythmType.STRAIGHT,
            durations=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            accents=[0, 4]
        )
    
    @classmethod
    def syncopated(cls) -> 'RhythmicTemplate':
        """Create a syncopated template."""
        return cls(
            name="Syncopated",
            type=RhythmType.SYNCOPATED,
            durations=[0.75, 0.25, 0.5, 0.5, 0.75, 0.25, 0.5, 0.5],
            offsets=[0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.25, 0.0],
            accents=[0, 2, 4, 6]
        )
    
    @classmethod
    def triplet(cls) -> 'RhythmicTemplate':
        """Create a triplet template."""
        return cls(
            name="Triplet",
            type=RhythmType.TRIPLET,
            durations=[1/3, 1/3, 1/3, 1/3, 1/3, 1/3],
            accents=[0, 3]
        )
    
    @classmethod
    def swing_eighths(cls) -> 'RhythmicTemplate':
        """Create a swing eighths template."""
        return cls(
            name="Swing Eighths",
            type=RhythmType.SWING,
            durations=[2/3, 1/3, 2/3, 1/3, 2/3, 1/3, 2/3, 1/3],
            accents=[0, 2, 4, 6]
        )
    
    @classmethod
    def polyrhythmic_3_over_4(cls) -> 'RhythmicTemplate':
        """Create a 3-over-4 polyrhythmic template."""
        return cls(
            name="3 over 4",
            type=RhythmType.POLYRHYTHMIC,
            durations=[4/3, 4/3, 4/3],  # 3 notes over 4 beats
            accents=[0]
        )


class RhythmLibrary:
    """Collection of pre-built rhythmic templates."""
    
    TEMPLATES = {
        'straight_quarters': RhythmicTemplate.straight_quarters,
        'straight_eighths': RhythmicTemplate.straight_eighths,
        'syncopated': RhythmicTemplate.syncopated,
        'triplet': RhythmicTemplate.triplet,
        'swing': RhythmicTemplate.swing_eighths,
        '3_over_4': RhythmicTemplate.polyrhythmic_3_over_4,
    }
    
    @classmethod
    def get(cls, name: str) -> Optional[RhythmicTemplate]:
        """Get a template by name."""
        factory = cls.TEMPLATES.get(name)
        return factory() if factory else None
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List all available template names."""
        return list(cls.TEMPLATES.keys())


def create_shape_bundles(triads: List[Triad]) -> List[ShapeBundle]:
    """
    Create shape bundles for a list of triads.
    
    Args:
        triads: List of closed triads
        
    Returns:
        List of ShapeBundle objects
    """
    return [ShapeBundle.from_triad(t) for t in triads]


def generate_etude_patterns(
    triad: Triad,
    rhythm: str = 'straight_eighths'
) -> List[List[RhythmicNote]]:
    """
    Generate a set of etude patterns for practice.
    
    Args:
        triad: Source triad
        rhythm: Rhythm template name
        
    Returns:
        List of rhythmicized patterns
    """
    template = RhythmLibrary.get(rhythm) or RhythmicTemplate.straight_eighths()
    patterns = MelodicPatternGenerator.all_patterns(triad)
    
    return [template.apply_to_pattern(p) for p in patterns]

