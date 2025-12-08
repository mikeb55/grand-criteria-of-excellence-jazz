"""
Tonality Vault Module
=====================

A comprehensive collection of scales, modes, and harmonic systems
for the Open Triad Engine.

Includes:
- Standard diatonic modes
- Melodic and harmonic minor modes
- Symmetric scales (whole-tone, diminished, augmented)
- Exotic and world scales
- Custom scale definitions
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ScaleCategory(Enum):
    """Categories of scales."""
    DIATONIC = "diatonic"
    MELODIC_MINOR = "melodic_minor"
    HARMONIC_MINOR = "harmonic_minor"
    SYMMETRIC = "symmetric"
    PENTATONIC = "pentatonic"
    BEBOP = "bebop"
    EXOTIC = "exotic"
    CUSTOM = "custom"


@dataclass
class Scale:
    """
    Represents a musical scale.
    
    Attributes:
        name: Scale name
        intervals: Semitone intervals from root
        category: Scale category
        description: Brief description
        parent_scale: Parent scale (for modes)
        mode_degree: Which degree of parent this mode is built on
        triad_types: Triad types for each degree
    """
    name: str
    intervals: List[int]
    category: ScaleCategory = ScaleCategory.DIATONIC
    description: str = ""
    parent_scale: Optional[str] = None
    mode_degree: int = 1
    triad_types: List[str] = field(default_factory=list)
    
    @property
    def num_notes(self) -> int:
        """Number of notes in the scale."""
        return len(self.intervals)
    
    @property
    def interval_pattern(self) -> List[int]:
        """Return the pattern of intervals between adjacent notes."""
        pattern = []
        for i in range(len(self.intervals)):
            next_i = (i + 1) % len(self.intervals)
            if next_i == 0:
                interval = 12 - self.intervals[i]
            else:
                interval = self.intervals[next_i] - self.intervals[i]
            pattern.append(interval)
        return pattern
    
    def contains_interval(self, interval: int) -> bool:
        """Check if the scale contains a specific interval from root."""
        return (interval % 12) in self.intervals
    
    def get_notes(self, root: str) -> List[str]:
        """Get note names for this scale from a given root."""
        from .core import CHROMATIC_NOTES
        root_pc = CHROMATIC_NOTES.index(root) if root in CHROMATIC_NOTES else 0
        return [CHROMATIC_NOTES[(root_pc + iv) % 12] for iv in self.intervals]


class TonalityVault:
    """
    Repository of all scales and harmonic systems.
    
    Provides access to standard and exotic scales, with methods
    for querying and generating scale-based material.
    """
    
    def __init__(self):
        """Initialize the vault with all scale definitions."""
        self._scales: Dict[str, Scale] = {}
        self._load_diatonic_modes()
        self._load_melodic_minor_modes()
        self._load_harmonic_minor_modes()
        self._load_symmetric_scales()
        self._load_pentatonic_scales()
        self._load_bebop_scales()
        self._load_exotic_scales()
    
    def _load_diatonic_modes(self):
        """Load the seven diatonic modes."""
        modes = [
            Scale(
                name="ionian",
                intervals=[0, 2, 4, 5, 7, 9, 11],
                category=ScaleCategory.DIATONIC,
                description="Major scale - bright, resolved",
                triad_types=['major', 'minor', 'minor', 'major', 'major', 'minor', 'dim']
            ),
            Scale(
                name="dorian",
                intervals=[0, 2, 3, 5, 7, 9, 10],
                category=ScaleCategory.DIATONIC,
                description="Minor with raised 6th - jazzy minor",
                parent_scale="ionian", mode_degree=2,
                triad_types=['minor', 'minor', 'major', 'major', 'minor', 'dim', 'major']
            ),
            Scale(
                name="phrygian",
                intervals=[0, 1, 3, 5, 7, 8, 10],
                category=ScaleCategory.DIATONIC,
                description="Minor with b2 - Spanish/flamenco feel",
                parent_scale="ionian", mode_degree=3,
                triad_types=['minor', 'major', 'major', 'minor', 'dim', 'major', 'minor']
            ),
            Scale(
                name="lydian",
                intervals=[0, 2, 4, 6, 7, 9, 11],
                category=ScaleCategory.DIATONIC,
                description="Major with #4 - dreamy, floating",
                parent_scale="ionian", mode_degree=4,
                triad_types=['major', 'major', 'minor', 'dim', 'major', 'minor', 'minor']
            ),
            Scale(
                name="mixolydian",
                intervals=[0, 2, 4, 5, 7, 9, 10],
                category=ScaleCategory.DIATONIC,
                description="Major with b7 - dominant, bluesy",
                parent_scale="ionian", mode_degree=5,
                triad_types=['major', 'minor', 'dim', 'major', 'minor', 'minor', 'major']
            ),
            Scale(
                name="aeolian",
                intervals=[0, 2, 3, 5, 7, 8, 10],
                category=ScaleCategory.DIATONIC,
                description="Natural minor - sad, reflective",
                parent_scale="ionian", mode_degree=6,
                triad_types=['minor', 'dim', 'major', 'minor', 'minor', 'major', 'major']
            ),
            Scale(
                name="locrian",
                intervals=[0, 1, 3, 5, 6, 8, 10],
                category=ScaleCategory.DIATONIC,
                description="Diminished tonic - unstable, dark",
                parent_scale="ionian", mode_degree=7,
                triad_types=['dim', 'major', 'minor', 'minor', 'major', 'major', 'minor']
            ),
        ]
        for scale in modes:
            self._scales[scale.name] = scale
    
    def _load_melodic_minor_modes(self):
        """Load the seven melodic minor modes."""
        modes = [
            Scale(
                name="melodic_minor",
                intervals=[0, 2, 3, 5, 7, 9, 11],
                category=ScaleCategory.MELODIC_MINOR,
                description="Minor with raised 6th and 7th - jazz minor"
            ),
            Scale(
                name="dorian_b2",
                intervals=[0, 1, 3, 5, 7, 9, 10],
                category=ScaleCategory.MELODIC_MINOR,
                description="Phrygian with natural 6th",
                parent_scale="melodic_minor", mode_degree=2
            ),
            Scale(
                name="lydian_augmented",
                intervals=[0, 2, 4, 6, 8, 9, 11],
                category=ScaleCategory.MELODIC_MINOR,
                description="Lydian with #5 - very bright",
                parent_scale="melodic_minor", mode_degree=3
            ),
            Scale(
                name="lydian_dominant",
                intervals=[0, 2, 4, 6, 7, 9, 10],
                category=ScaleCategory.MELODIC_MINOR,
                description="Lydian with b7 - dominant with tension",
                parent_scale="melodic_minor", mode_degree=4
            ),
            Scale(
                name="mixolydian_b6",
                intervals=[0, 2, 4, 5, 7, 8, 10],
                category=ScaleCategory.MELODIC_MINOR,
                description="Mixolydian with b6 - Hindu scale",
                parent_scale="melodic_minor", mode_degree=5
            ),
            Scale(
                name="locrian_nat2",
                intervals=[0, 2, 3, 5, 6, 8, 10],
                category=ScaleCategory.MELODIC_MINOR,
                description="Locrian with natural 2nd - half-diminished",
                parent_scale="melodic_minor", mode_degree=6
            ),
            Scale(
                name="altered",
                intervals=[0, 1, 3, 4, 6, 8, 10],
                category=ScaleCategory.MELODIC_MINOR,
                description="Super locrian - all alterations for V7alt",
                parent_scale="melodic_minor", mode_degree=7
            ),
        ]
        for scale in modes:
            self._scales[scale.name] = scale
    
    def _load_harmonic_minor_modes(self):
        """Load harmonic minor and its common modes."""
        modes = [
            Scale(
                name="harmonic_minor",
                intervals=[0, 2, 3, 5, 7, 8, 11],
                category=ScaleCategory.HARMONIC_MINOR,
                description="Minor with raised 7th - classical minor"
            ),
            Scale(
                name="locrian_nat6",
                intervals=[0, 1, 3, 5, 6, 9, 10],
                category=ScaleCategory.HARMONIC_MINOR,
                description="Locrian with natural 6th",
                parent_scale="harmonic_minor", mode_degree=2
            ),
            Scale(
                name="ionian_augmented",
                intervals=[0, 2, 4, 5, 8, 9, 11],
                category=ScaleCategory.HARMONIC_MINOR,
                description="Major with #5",
                parent_scale="harmonic_minor", mode_degree=3
            ),
            Scale(
                name="dorian_sharp4",
                intervals=[0, 2, 3, 6, 7, 9, 10],
                category=ScaleCategory.HARMONIC_MINOR,
                description="Dorian with #4 - Romanian/Ukrainian",
                parent_scale="harmonic_minor", mode_degree=4
            ),
            Scale(
                name="phrygian_dominant",
                intervals=[0, 1, 4, 5, 7, 8, 10],
                category=ScaleCategory.HARMONIC_MINOR,
                description="Phrygian with major 3rd - Spanish/Jewish",
                parent_scale="harmonic_minor", mode_degree=5
            ),
            Scale(
                name="lydian_sharp2",
                intervals=[0, 3, 4, 6, 7, 9, 11],
                category=ScaleCategory.HARMONIC_MINOR,
                description="Lydian with #2",
                parent_scale="harmonic_minor", mode_degree=6
            ),
            Scale(
                name="ultra_locrian",
                intervals=[0, 1, 3, 4, 6, 8, 9],
                category=ScaleCategory.HARMONIC_MINOR,
                description="Super locrian with bb7",
                parent_scale="harmonic_minor", mode_degree=7
            ),
        ]
        for scale in modes:
            self._scales[scale.name] = scale
    
    def _load_symmetric_scales(self):
        """Load symmetric scales."""
        scales = [
            Scale(
                name="whole_tone",
                intervals=[0, 2, 4, 6, 8, 10],
                category=ScaleCategory.SYMMETRIC,
                description="All whole steps - augmented, dreamlike"
            ),
            Scale(
                name="half_whole",
                intervals=[0, 1, 3, 4, 6, 7, 9, 10],
                category=ScaleCategory.SYMMETRIC,
                description="Diminished (H-W) - for diminished chords"
            ),
            Scale(
                name="whole_half",
                intervals=[0, 2, 3, 5, 6, 8, 9, 11],
                category=ScaleCategory.SYMMETRIC,
                description="Diminished (W-H) - for dominant 7b9 chords"
            ),
            Scale(
                name="augmented",
                intervals=[0, 3, 4, 7, 8, 11],
                category=ScaleCategory.SYMMETRIC,
                description="Augmented hexatonic - Coltrane changes"
            ),
            Scale(
                name="chromatic",
                intervals=list(range(12)),
                category=ScaleCategory.SYMMETRIC,
                description="All 12 notes"
            ),
        ]
        for scale in scales:
            self._scales[scale.name] = scale
    
    def _load_pentatonic_scales(self):
        """Load pentatonic scales."""
        scales = [
            Scale(
                name="major_pentatonic",
                intervals=[0, 2, 4, 7, 9],
                category=ScaleCategory.PENTATONIC,
                description="Major without 4th and 7th - universal"
            ),
            Scale(
                name="minor_pentatonic",
                intervals=[0, 3, 5, 7, 10],
                category=ScaleCategory.PENTATONIC,
                description="Minor without 2nd and 6th - blues/rock"
            ),
            Scale(
                name="blues",
                intervals=[0, 3, 5, 6, 7, 10],
                category=ScaleCategory.PENTATONIC,
                description="Minor pentatonic with b5 - blues essential"
            ),
            Scale(
                name="blues_major",
                intervals=[0, 2, 3, 4, 7, 9],
                category=ScaleCategory.PENTATONIC,
                description="Major pentatonic with b3 - major blues"
            ),
        ]
        for scale in scales:
            self._scales[scale.name] = scale
    
    def _load_bebop_scales(self):
        """Load bebop scales."""
        scales = [
            Scale(
                name="bebop_dominant",
                intervals=[0, 2, 4, 5, 7, 9, 10, 11],
                category=ScaleCategory.BEBOP,
                description="Mixolydian + natural 7 - chromatic passing"
            ),
            Scale(
                name="bebop_major",
                intervals=[0, 2, 4, 5, 7, 8, 9, 11],
                category=ScaleCategory.BEBOP,
                description="Major + b6 - chromatic passing"
            ),
            Scale(
                name="bebop_minor",
                intervals=[0, 2, 3, 5, 7, 8, 9, 10],
                category=ScaleCategory.BEBOP,
                description="Dorian + natural 7 - chromatic passing"
            ),
            Scale(
                name="bebop_locrian",
                intervals=[0, 1, 3, 5, 6, 7, 8, 10],
                category=ScaleCategory.BEBOP,
                description="Locrian + natural 5 - chromatic passing"
            ),
        ]
        for scale in scales:
            self._scales[scale.name] = scale
    
    def _load_exotic_scales(self):
        """Load exotic and world scales."""
        scales = [
            Scale(
                name="hirajoshi",
                intervals=[0, 2, 3, 7, 8],
                category=ScaleCategory.EXOTIC,
                description="Japanese pentatonic - haunting"
            ),
            Scale(
                name="in_sen",
                intervals=[0, 1, 5, 7, 10],
                category=ScaleCategory.EXOTIC,
                description="Japanese mode - mysterious"
            ),
            Scale(
                name="iwato",
                intervals=[0, 1, 5, 6, 10],
                category=ScaleCategory.EXOTIC,
                description="Japanese - dark, temple bells"
            ),
            Scale(
                name="kumoi",
                intervals=[0, 2, 3, 7, 9],
                category=ScaleCategory.EXOTIC,
                description="Japanese - melancholic"
            ),
            Scale(
                name="hungarian_minor",
                intervals=[0, 2, 3, 6, 7, 8, 11],
                category=ScaleCategory.EXOTIC,
                description="Double harmonic minor - gypsy"
            ),
            Scale(
                name="double_harmonic",
                intervals=[0, 1, 4, 5, 7, 8, 11],
                category=ScaleCategory.EXOTIC,
                description="Byzantine/Arabic - very exotic"
            ),
            Scale(
                name="persian",
                intervals=[0, 1, 4, 5, 6, 8, 11],
                category=ScaleCategory.EXOTIC,
                description="Persian traditional"
            ),
            Scale(
                name="neapolitan_major",
                intervals=[0, 1, 3, 5, 7, 9, 11],
                category=ScaleCategory.EXOTIC,
                description="Major with b2"
            ),
            Scale(
                name="neapolitan_minor",
                intervals=[0, 1, 3, 5, 7, 8, 11],
                category=ScaleCategory.EXOTIC,
                description="Harmonic minor with b2"
            ),
            Scale(
                name="enigmatic",
                intervals=[0, 1, 4, 6, 8, 10, 11],
                category=ScaleCategory.EXOTIC,
                description="Verdi's scale - mysterious"
            ),
        ]
        for scale in scales:
            self._scales[scale.name] = scale
    
    def get_scale(self, name: str) -> Optional[Scale]:
        """Get a scale by name."""
        return self._scales.get(name.lower().replace(' ', '_'))
    
    def list_scales(self, category: Optional[ScaleCategory] = None) -> List[str]:
        """List all scale names, optionally filtered by category."""
        if category is None:
            return list(self._scales.keys())
        return [name for name, scale in self._scales.items() 
                if scale.category == category]
    
    def get_scales_by_category(self, category: ScaleCategory) -> List[Scale]:
        """Get all scales in a category."""
        return [scale for scale in self._scales.values() 
                if scale.category == category]
    
    def search_scales(self, interval: int) -> List[Scale]:
        """Find scales containing a specific interval."""
        return [scale for scale in self._scales.values() 
                if scale.contains_interval(interval)]
    
    def add_custom_scale(
        self, 
        name: str, 
        intervals: List[int],
        description: str = ""
    ) -> Scale:
        """
        Add a custom scale to the vault.
        
        Args:
            name: Unique name for the scale
            intervals: Semitone intervals from root
            description: Optional description
            
        Returns:
            The created Scale object
        """
        scale = Scale(
            name=name,
            intervals=intervals,
            category=ScaleCategory.CUSTOM,
            description=description
        )
        self._scales[name.lower().replace(' ', '_')] = scale
        return scale
    
    def get_related_scales(self, scale_name: str) -> List[Scale]:
        """Get scales related to the given scale (modes of same parent)."""
        scale = self.get_scale(scale_name)
        if not scale:
            return []
        
        parent = scale.parent_scale or scale.name
        return [s for s in self._scales.values() 
                if s.parent_scale == parent or s.name == parent]
    
    def get_triad_pair_scales(self) -> List[Scale]:
        """Get scales commonly used for triad pairs."""
        # Scales with good triad pair potential
        triad_pair_names = [
            'lydian', 'lydian_augmented', 'lydian_dominant',
            'whole_tone', 'augmented', 'altered',
            'half_whole', 'whole_half'
        ]
        return [self._scales[name] for name in triad_pair_names 
                if name in self._scales]


# Convenience function
def get_scale(name: str) -> Optional[Scale]:
    """Get a scale from the global vault."""
    vault = TonalityVault()
    return vault.get_scale(name)

