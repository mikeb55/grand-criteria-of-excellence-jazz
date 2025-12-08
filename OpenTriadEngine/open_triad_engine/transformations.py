"""
Transformation Modules for Open Triad Engine
=============================================

Implements:
1. Closed → Open Triad Conversion (drop2, drop3, super_open)
2. Inversion Engine (open_root, open_first, open_second)
3. Scale/Key Mapping
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from .core import Note, Triad, TriadType, Inversion, VoicingType, CHROMATIC_NOTES
from .tonality_vault import TonalityVault, Scale


class DropVoicing(Enum):
    """Types of drop voicings."""
    DROP2 = "drop2"
    DROP3 = "drop3"
    SUPER_OPEN = "super_open"


@dataclass
class TransformationResult:
    """
    Result of a transformation operation.
    
    Attributes:
        original: The original triad
        transformed: The transformed triad
        operation: Name of the transformation applied
        description: Human-readable description
    """
    original: Triad
    transformed: Triad
    operation: str
    description: str


class ClosedToOpenConverter:
    """
    Converts closed-position triads to open-position voicings.
    
    Supports three transformations:
    - open_drop2: Drop the 2nd voice from the top down an octave
    - open_drop3: Drop the 3rd voice from the top down an octave  
    - super_open: Flip multiple voices up an octave for widest spacing
    """
    
    @staticmethod
    def open_drop2(triad: Triad) -> Triad:
        """
        Convert to drop-2 voicing.
        
        Takes the second voice from the top and drops it down an octave.
        Result: Wide interval at bottom, close interval at top.
        
        For a closed [R-3-5], drop2 creates [3-R-5] with the 3rd down.
        """
        result = triad.copy()
        sorted_voices = sorted(result.voices, key=lambda n: n.midi_number)
        
        if len(sorted_voices) < 3:
            return result
        
        # Get voices in order: bottom, middle, top
        bottom, middle, top = sorted_voices[0], sorted_voices[1], sorted_voices[2]
        
        # Drop the middle voice down an octave
        new_middle = middle.transpose(-12)
        
        # New ordering: dropped middle (now bass), original bottom, original top
        result.voices = sorted([new_middle, bottom, top], key=lambda n: n.midi_number)
        result.voicing_type = VoicingType.OPEN_DROP2
        
        return result
    
    @staticmethod
    def open_drop3(triad: Triad) -> Triad:
        """
        Convert to drop-3 voicing.
        
        Takes the third voice from the top (the bass) and drops it down an octave.
        Result: Very wide spacing at bottom.
        """
        result = triad.copy()
        sorted_voices = sorted(result.voices, key=lambda n: n.midi_number)
        
        if len(sorted_voices) < 3:
            return result
        
        bottom, middle, top = sorted_voices[0], sorted_voices[1], sorted_voices[2]
        
        # Drop the bottom voice down an octave
        new_bottom = bottom.transpose(-12)
        
        result.voices = sorted([new_bottom, middle, top], key=lambda n: n.midi_number)
        result.voicing_type = VoicingType.OPEN_DROP3
        
        return result
    
    @staticmethod
    def super_open(triad: Triad) -> Triad:
        """
        Convert to super-open voicing.
        
        Spreads voices maximally by raising top voice up an octave
        and lowering bottom voice down an octave.
        """
        result = triad.copy()
        sorted_voices = sorted(result.voices, key=lambda n: n.midi_number)
        
        if len(sorted_voices) < 3:
            return result
        
        bottom, middle, top = sorted_voices[0], sorted_voices[1], sorted_voices[2]
        
        # Lower bottom, raise top
        new_bottom = bottom.transpose(-12)
        new_top = top.transpose(12)
        
        result.voices = sorted([new_bottom, middle, new_top], key=lambda n: n.midi_number)
        result.voicing_type = VoicingType.SUPER_OPEN
        
        return result
    
    @classmethod
    def convert(cls, triad: Triad, voicing: DropVoicing) -> Triad:
        """
        Convert a triad to the specified open voicing.
        
        Args:
            triad: The source triad (any voicing)
            voicing: Target voicing type
            
        Returns:
            New triad with open voicing
        """
        # First normalize to closed root position
        closed = Triad(
            root=Note(triad.root.name, triad.root.octave),
            triad_type=triad.triad_type,
            inversion=Inversion.ROOT,
            voicing_type=VoicingType.CLOSED
        )
        
        if voicing == DropVoicing.DROP2:
            return cls.open_drop2(closed)
        elif voicing == DropVoicing.DROP3:
            return cls.open_drop3(closed)
        elif voicing == DropVoicing.SUPER_OPEN:
            return cls.super_open(closed)
        
        return closed
    
    @classmethod
    def all_open_voicings(cls, triad: Triad) -> Dict[str, Triad]:
        """
        Generate all open voicings for a triad.
        
        Returns:
            Dictionary mapping voicing names to triads
        """
        return {
            'drop2': cls.open_drop2(triad),
            'drop3': cls.open_drop3(triad),
            'super_open': cls.super_open(triad),
        }


class InversionEngine:
    """
    Generates open-triad inversions.
    
    Creates three open positions:
    - open_root: Root in bass, open spacing above
    - open_first: Third in bass, open spacing above
    - open_second: Fifth in bass, open spacing above
    """
    
    @staticmethod
    def open_root(triad: Triad) -> Triad:
        """
        Create open-position root inversion.
        
        Root in bass, with open spacing (5th raised an octave).
        """
        # Get interval pattern for this triad type
        intervals = triad.TRIAD_INTERVALS[triad.triad_type]
        
        root = Note(triad.root.name, triad.root.octave)
        third = root.transpose(intervals[0])
        fifth = root.transpose(intervals[1] + 12)  # Raise 5th an octave
        
        result = triad.copy()
        result.voices = [root, third, fifth]
        result.inversion = Inversion.ROOT
        result.voicing_type = VoicingType.OPEN_ROOT
        
        return result
    
    @staticmethod
    def open_first(triad: Triad) -> Triad:
        """
        Create open-position first inversion.
        
        Third in bass, with open spacing.
        """
        intervals = triad.TRIAD_INTERVALS[triad.triad_type]
        
        root = Note(triad.root.name, triad.root.octave)
        third = root.transpose(intervals[0])
        fifth = root.transpose(intervals[1])
        
        # Third in bass, fifth above, root raised an octave
        bass_third = Note(third.name, root.octave)
        mid_fifth = bass_third.transpose((intervals[1] - intervals[0]) % 12)
        top_root = root.transpose(12)
        
        result = triad.copy()
        result.voices = sorted([bass_third, mid_fifth, top_root], key=lambda n: n.midi_number)
        result.inversion = Inversion.FIRST
        result.voicing_type = VoicingType.OPEN_FIRST
        
        return result
    
    @staticmethod
    def open_second(triad: Triad) -> Triad:
        """
        Create open-position second inversion.
        
        Fifth in bass, with open spacing.
        """
        intervals = triad.TRIAD_INTERVALS[triad.triad_type]
        
        root = Note(triad.root.name, triad.root.octave)
        fifth = root.transpose(intervals[1])
        
        # Fifth in bass at original octave, raise root and third
        bass_fifth = Note(fifth.name, root.octave - 1)  # Fifth as bass
        mid_root = root  # Root in middle
        top_third = root.transpose(intervals[0] + 12)  # Third on top, raised
        
        result = triad.copy()
        result.voices = sorted([bass_fifth, mid_root, top_third], key=lambda n: n.midi_number)
        result.inversion = Inversion.SECOND
        result.voicing_type = VoicingType.OPEN_SECOND
        
        return result
    
    @classmethod
    def get_inversion(cls, triad: Triad, inversion: Inversion) -> Triad:
        """
        Get the specified open inversion.
        
        Args:
            triad: Source triad
            inversion: Target inversion
            
        Returns:
            Triad in open position with specified inversion
        """
        if inversion == Inversion.ROOT:
            return cls.open_root(triad)
        elif inversion == Inversion.FIRST:
            return cls.open_first(triad)
        elif inversion == Inversion.SECOND:
            return cls.open_second(triad)
        return triad.copy()
    
    @classmethod
    def all_inversions(cls, triad: Triad) -> Dict[str, Triad]:
        """
        Generate all open inversions for a triad.
        
        Returns:
            Dictionary mapping inversion names to triads
        """
        return {
            'open_root': cls.open_root(triad),
            'open_first': cls.open_first(triad),
            'open_second': cls.open_second(triad),
        }
    
    @classmethod
    def cycle_inversions(cls, triad: Triad, ascending: bool = True) -> List[Triad]:
        """
        Generate a cycling sequence of inversions.
        
        Args:
            triad: Source triad
            ascending: If True, cycle 1st→2nd→root; if False, root→2nd→1st
            
        Returns:
            List of triads in cycling order
        """
        if ascending:
            return [
                cls.open_first(triad),
                cls.open_second(triad),
                cls.open_root(triad),
            ]
        else:
            return [
                cls.open_root(triad),
                cls.open_second(triad),
                cls.open_first(triad),
            ]


class ScaleMapper:
    """
    Maps open triads across scales and modes.
    
    Supports:
    - Diatonic modes (Ionian through Locrian)
    - Melodic minor modes
    - Whole-tone, diminished/octatonic
    - Altered scale
    - Tonality Vault scale sets
    """
    
    # Scale degree intervals from root (in semitones)
    SCALE_FORMULAS = {
        # Major modes
        'ionian': [0, 2, 4, 5, 7, 9, 11],
        'dorian': [0, 2, 3, 5, 7, 9, 10],
        'phrygian': [0, 1, 3, 5, 7, 8, 10],
        'lydian': [0, 2, 4, 6, 7, 9, 11],
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],
        'aeolian': [0, 2, 3, 5, 7, 8, 10],
        'locrian': [0, 1, 3, 5, 6, 8, 10],
        
        # Melodic minor modes
        'melodic_minor': [0, 2, 3, 5, 7, 9, 11],
        'dorian_b2': [0, 1, 3, 5, 7, 9, 10],
        'lydian_augmented': [0, 2, 4, 6, 8, 9, 11],
        'lydian_dominant': [0, 2, 4, 6, 7, 9, 10],
        'mixolydian_b6': [0, 2, 4, 5, 7, 8, 10],
        'locrian_nat2': [0, 2, 3, 5, 6, 8, 10],
        'altered': [0, 1, 3, 4, 6, 8, 10],
        
        # Harmonic minor modes
        'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
        'phrygian_dominant': [0, 1, 4, 5, 7, 8, 10],
        
        # Symmetric scales
        'whole_tone': [0, 2, 4, 6, 8, 10],
        'half_whole': [0, 1, 3, 4, 6, 7, 9, 10],  # Diminished
        'whole_half': [0, 2, 3, 5, 6, 8, 9, 11],  # Diminished
        'augmented': [0, 3, 4, 7, 8, 11],          # Augmented hexatonic
        
        # Pentatonics
        'major_pentatonic': [0, 2, 4, 7, 9],
        'minor_pentatonic': [0, 3, 5, 7, 10],
        'blues': [0, 3, 5, 6, 7, 10],
    }
    
    # Triad types naturally occurring on each scale degree
    DIATONIC_TRIADS = {
        'ionian': ['major', 'minor', 'minor', 'major', 'major', 'minor', 'dim'],
        'dorian': ['minor', 'minor', 'major', 'major', 'minor', 'dim', 'major'],
        'phrygian': ['minor', 'major', 'major', 'minor', 'dim', 'major', 'minor'],
        'lydian': ['major', 'major', 'minor', 'dim', 'major', 'minor', 'minor'],
        'mixolydian': ['major', 'minor', 'dim', 'major', 'minor', 'minor', 'major'],
        'aeolian': ['minor', 'dim', 'major', 'minor', 'minor', 'major', 'major'],
        'locrian': ['dim', 'major', 'minor', 'minor', 'major', 'major', 'minor'],
    }
    
    def __init__(self, root: str = 'C'):
        """
        Initialize mapper with a root note.
        
        Args:
            root: Root note name (e.g., 'C', 'Bb', 'F#')
        """
        self.root = root
        self.root_pc = CHROMATIC_NOTES.index(root) if root in CHROMATIC_NOTES else 0
        self.vault = TonalityVault()
    
    def get_scale_notes(self, scale_name: str) -> List[str]:
        """
        Get the note names for a scale.
        
        Args:
            scale_name: Name of the scale
            
        Returns:
            List of note names in the scale
        """
        formula = self.SCALE_FORMULAS.get(scale_name.lower())
        if not formula:
            # Try tonality vault
            scale = self.vault.get_scale(scale_name)
            if scale:
                formula = scale.intervals
            else:
                formula = self.SCALE_FORMULAS['ionian']  # Fallback
        
        notes = []
        for interval in formula:
            pc = (self.root_pc + interval) % 12
            notes.append(CHROMATIC_NOTES[pc])
        
        return notes
    
    def get_diatonic_triads(self, scale_name: str, octave: int = 4) -> List[Triad]:
        """
        Generate all diatonic triads in a scale.
        
        Args:
            scale_name: Name of the scale
            octave: Starting octave
            
        Returns:
            List of triads built on each scale degree
        """
        scale_notes = self.get_scale_notes(scale_name)
        triad_types = self.DIATONIC_TRIADS.get(scale_name.lower(), ['major'] * 7)
        
        triads = []
        for i, note_name in enumerate(scale_notes):
            if i < len(triad_types):
                tt_str = triad_types[i]
                tt_map = {
                    'major': TriadType.MAJOR,
                    'minor': TriadType.MINOR,
                    'dim': TriadType.DIMINISHED,
                    'aug': TriadType.AUGMENTED,
                }
                tt = tt_map.get(tt_str, TriadType.MAJOR)
                
                triad = Triad(
                    root=Note(note_name, octave),
                    triad_type=tt
                )
                triads.append(triad)
        
        return triads
    
    def map_triad_across_scale(
        self, 
        triad: Triad, 
        scale_name: str,
        preserve_shape: bool = True
    ) -> List[Triad]:
        """
        Map a triad shape across all degrees of a scale.
        
        Args:
            triad: Source triad (shape to replicate)
            scale_name: Scale to map across
            preserve_shape: If True, keep triad type constant; if False, use diatonic types
            
        Returns:
            List of triads, one for each scale degree
        """
        scale_notes = self.get_scale_notes(scale_name)
        result = []
        
        for i, note_name in enumerate(scale_notes):
            new_triad = triad.copy()
            
            # Calculate transposition
            original_pc = triad.root.pitch_class
            new_pc = CHROMATIC_NOTES.index(note_name)
            transpose_amt = (new_pc - original_pc) % 12
            
            new_triad = triad.transpose(transpose_amt)
            new_triad.root = Note(note_name, triad.root.octave)
            
            if not preserve_shape:
                # Use diatonic triad type
                triad_types = self.DIATONIC_TRIADS.get(scale_name.lower(), ['major'] * 7)
                if i < len(triad_types):
                    tt_map = {
                        'major': TriadType.MAJOR,
                        'minor': TriadType.MINOR,
                        'dim': TriadType.DIMINISHED,
                        'aug': TriadType.AUGMENTED,
                    }
                    new_triad = Triad(
                        root=Note(note_name, triad.root.octave),
                        triad_type=tt_map.get(triad_types[i], TriadType.MAJOR),
                        voicing_type=triad.voicing_type
                    )
            
            result.append(new_triad)
        
        return result
    
    def get_triads_from_progression(
        self, 
        chord_symbols: List[str],
        octave: int = 4
    ) -> List[Triad]:
        """
        Convert a chord progression to triads.
        
        Args:
            chord_symbols: List of chord symbols (e.g., ['Dm7', 'G7', 'Cmaj7'])
            octave: Base octave
            
        Returns:
            List of triads
        """
        triads = []
        for symbol in chord_symbols:
            triad = Triad.from_symbol(symbol, octave)
            triads.append(triad)
        return triads
    
    def chromatic_triads(
        self, 
        triad_type: TriadType = TriadType.MAJOR,
        octave: int = 4
    ) -> List[Triad]:
        """
        Generate all 12 chromatic triads of a given type.
        
        Args:
            triad_type: Type of triads to generate
            octave: Base octave
            
        Returns:
            List of 12 triads, one for each chromatic note
        """
        return [
            Triad(root=Note(note, octave), triad_type=triad_type)
            for note in CHROMATIC_NOTES
        ]


def closed_to_open(triad: Triad, voicing: str = 'drop2') -> Triad:
    """
    Convenience function to convert closed to open voicing.
    
    Args:
        triad: Source triad
        voicing: 'drop2', 'drop3', or 'super_open'
        
    Returns:
        Open-voiced triad
    """
    converter = ClosedToOpenConverter()
    
    voicing_map = {
        'drop2': DropVoicing.DROP2,
        'drop3': DropVoicing.DROP3,
        'super_open': DropVoicing.SUPER_OPEN,
    }
    
    dv = voicing_map.get(voicing.lower(), DropVoicing.DROP2)
    return converter.convert(triad, dv)


def map_triads_to_scale(
    triad_type: str,
    scale_name: str,
    root: str = 'C',
    octave: int = 4
) -> List[Triad]:
    """
    Convenience function to map triads across a scale.
    
    Args:
        triad_type: Type of triad ('major', 'minor', etc.)
        scale_name: Scale to map across
        root: Root note of the scale
        octave: Base octave
        
    Returns:
        List of triads across the scale
    """
    mapper = ScaleMapper(root)
    
    tt_map = {
        'major': TriadType.MAJOR,
        'minor': TriadType.MINOR,
        'dim': TriadType.DIMINISHED,
        'aug': TriadType.AUGMENTED,
        'sus2': TriadType.SUSPENDED_2,
        'sus4': TriadType.SUSPENDED_4,
    }
    
    tt = tt_map.get(triad_type.lower(), TriadType.MAJOR)
    source_triad = Triad(root=Note(root, octave), triad_type=tt)
    
    return mapper.map_triad_across_scale(source_triad, scale_name)

