"""
Melodic Pattern Engine for Etude Generator
===========================================

Stitches melodic patterns into bar-length phrases using the
Open Triad Engine's pattern generator.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
from enum import Enum
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from open_triad_engine import Note, Triad
from open_triad_engine.output_shapes import (
    MelodicPatternGenerator, MelodicPattern, ArpeggioPattern,
    ContourSignature, ContourType
)

from .inputs import EtudeConfig, EtudeType, Difficulty
from .harmonic import HarmonicCell, HarmonicMaterial


class PatternType(Enum):
    """Types of melodic patterns."""
    ARPEGGIO_UP = "arpeggio_up"
    ARPEGGIO_DOWN = "arpeggio_down"
    ARPEGGIO_UP_DOWN = "arpeggio_up_down"
    ROTATION_132 = "rotation_1-3-2"
    ROTATION_312 = "rotation_3-1-2"
    ROTATION_213 = "rotation_2-1-3"
    WAVE = "wave"
    PENDULUM = "pendulum"
    SKIP_2 = "skip_2"
    SKIP_3 = "skip_3"


# Pattern difficulty mappings
DIFFICULTY_PATTERNS = {
    Difficulty.BEGINNER: [
        PatternType.ARPEGGIO_UP,
        PatternType.ARPEGGIO_DOWN,
    ],
    Difficulty.INTERMEDIATE: [
        PatternType.ARPEGGIO_UP,
        PatternType.ARPEGGIO_DOWN,
        PatternType.ARPEGGIO_UP_DOWN,
        PatternType.ROTATION_132,
        PatternType.ROTATION_312,
    ],
    Difficulty.ADVANCED: [
        PatternType.ARPEGGIO_UP,
        PatternType.ARPEGGIO_DOWN,
        PatternType.ARPEGGIO_UP_DOWN,
        PatternType.ROTATION_132,
        PatternType.ROTATION_312,
        PatternType.ROTATION_213,
        PatternType.WAVE,
        PatternType.PENDULUM,
        PatternType.SKIP_2,
        PatternType.SKIP_3,
    ],
}


@dataclass
class NoteEvent:
    """
    A single note event with timing information.
    
    Attributes:
        note: The pitch
        beat: Beat position in the bar (0-indexed)
        duration: Duration in beats
        string: Guitar string (1-6, optional)
        fret: Fret number (optional)
        fingering: Suggested fingering (optional)
    """
    note: Note
    beat: float
    duration: float
    string: Optional[int] = None
    fret: Optional[int] = None
    fingering: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return {
            'pitch': str(self.note),
            'beat': self.beat,
            'duration': self.duration,
            'string': self.string,
            'fret': self.fret,
            'fingering': self.fingering,
        }


@dataclass
class BarContent:
    """
    Content of a single bar.
    
    Attributes:
        bar_number: Bar number (1-indexed)
        notes: List of note events
        harmony: The harmonic cell for this bar
        pattern_type: Pattern used
        time_signature: Time signature (beats, beat_type)
    """
    bar_number: int
    notes: List[NoteEvent]
    harmony: HarmonicCell
    pattern_type: str
    time_signature: Tuple[int, int] = (4, 4)
    
    @property
    def beats_per_bar(self) -> int:
        return self.time_signature[0]
    
    def to_dict(self) -> Dict:
        return {
            'bar_number': self.bar_number,
            'notes': [n.to_dict() for n in self.notes],
            'harmony': self.harmony.to_dict(),
            'pattern_type': self.pattern_type,
            'time_signature': list(self.time_signature),
        }


@dataclass
class EtudePhrase:
    """
    A phrase containing multiple bars.
    
    Attributes:
        bars: List of bar contents
        phrase_number: Phrase number
        contour: Overall contour of the phrase
    """
    bars: List[BarContent]
    phrase_number: int = 1
    contour: Optional[ContourSignature] = None
    
    @property
    def all_notes(self) -> List[Note]:
        """Get all notes in the phrase."""
        return [event.note for bar in self.bars for event in bar.notes]
    
    def to_dict(self) -> Dict:
        return {
            'phrase_number': self.phrase_number,
            'bars': [bar.to_dict() for bar in self.bars],
            'contour': self.contour.to_dict() if self.contour else None,
        }


class PatternStitcher:
    """
    Stitches melodic patterns into bar-length phrases.
    
    Uses the Open Triad Engine's pattern generator and combines
    patterns with harmonic material to create complete etude phrases.
    """
    
    def __init__(self, config: EtudeConfig):
        """
        Initialize the pattern stitcher.
        
        Args:
            config: Etude configuration
        """
        self.config = config
        self.pattern_gen = MelodicPatternGenerator()
        
        # Get allowed patterns for difficulty
        self.allowed_patterns = DIFFICULTY_PATTERNS.get(
            config._difficulty_enum, DIFFICULTY_PATTERNS[Difficulty.INTERMEDIATE]
        )
    
    def stitch(self, harmonic_material: HarmonicMaterial) -> List[EtudePhrase]:
        """
        Stitch patterns with harmonic material to create phrases.
        
        Args:
            harmonic_material: Harmonic cells to use
            
        Returns:
            List of EtudePhrase objects
        """
        phrases = []
        bars = []
        
        for i, cell in enumerate(harmonic_material.cells):
            bar = self._create_bar(cell, i + 1)
            bars.append(bar)
            
            # Create phrase every 4 bars or at end
            if len(bars) >= 4 or i == len(harmonic_material.cells) - 1:
                phrase = EtudePhrase(
                    bars=bars.copy(),
                    phrase_number=len(phrases) + 1,
                    contour=self._calculate_phrase_contour(bars)
                )
                phrases.append(phrase)
                bars = []
        
        return phrases
    
    def _create_bar(self, cell: HarmonicCell, bar_number: int) -> BarContent:
        """Create a bar from a harmonic cell."""
        # Select pattern based on etude type and position
        pattern_type = self._select_pattern(bar_number)
        
        # Generate pattern using engine
        pattern = self._generate_pattern(cell.triad, pattern_type)
        
        # Convert to note events
        notes = self._pattern_to_events(pattern, bar_number)
        
        return BarContent(
            bar_number=bar_number,
            notes=notes,
            harmony=cell,
            pattern_type=pattern_type.value,
            time_signature=self.config.time_signature
        )
    
    def _select_pattern(self, bar_number: int) -> PatternType:
        """Select a pattern based on bar position and etude type."""
        etude_type = self.config._etude_type_enum
        
        if etude_type == EtudeType.MELODIC:
            # Alternate between up and down arpeggios
            if bar_number % 2 == 1:
                return PatternType.ARPEGGIO_UP
            else:
                return PatternType.ARPEGGIO_DOWN
        
        elif etude_type == EtudeType.INTERVALLIC:
            # Use wider interval patterns
            patterns = [PatternType.SKIP_2, PatternType.WAVE, PatternType.PENDULUM]
            return patterns[(bar_number - 1) % len(patterns)]
        
        elif etude_type == EtudeType.INVERSION_CYCLE:
            # Cycle through different rotation patterns
            patterns = [
                PatternType.ARPEGGIO_UP,
                PatternType.ROTATION_132,
                PatternType.ROTATION_312,
            ]
            return patterns[(bar_number - 1) % len(patterns)]
        
        else:
            # Default: cycle through allowed patterns
            idx = (bar_number - 1) % len(self.allowed_patterns)
            return self.allowed_patterns[idx]
    
    def _generate_pattern(self, triad: Triad, pattern_type: PatternType) -> MelodicPattern:
        """Generate a melodic pattern from a triad."""
        if pattern_type == PatternType.ARPEGGIO_UP:
            return self.pattern_gen.arpeggio(triad, ArpeggioPattern.UP)
        
        elif pattern_type == PatternType.ARPEGGIO_DOWN:
            return self.pattern_gen.arpeggio(triad, ArpeggioPattern.DOWN)
        
        elif pattern_type == PatternType.ARPEGGIO_UP_DOWN:
            return self.pattern_gen.arpeggio(triad, ArpeggioPattern.UP_DOWN)
        
        elif pattern_type == PatternType.ROTATION_132:
            return self.pattern_gen.rotation(triad, (1, 3, 2))
        
        elif pattern_type == PatternType.ROTATION_312:
            return self.pattern_gen.rotation(triad, (3, 1, 2))
        
        elif pattern_type == PatternType.ROTATION_213:
            return self.pattern_gen.rotation(triad, (2, 1, 3))
        
        elif pattern_type == PatternType.WAVE:
            return self.pattern_gen.wave(triad)
        
        elif pattern_type == PatternType.PENDULUM:
            return self.pattern_gen.pendulum(triad)
        
        elif pattern_type == PatternType.SKIP_2:
            return self.pattern_gen.intervallic_skip(triad, 2)
        
        elif pattern_type == PatternType.SKIP_3:
            return self.pattern_gen.intervallic_skip(triad, 3)
        
        else:
            return self.pattern_gen.arpeggio(triad, ArpeggioPattern.UP)
    
    def _pattern_to_events(self, pattern: MelodicPattern, bar_number: int) -> List[NoteEvent]:
        """Convert a melodic pattern to note events."""
        events = []
        beats_per_bar = self.config.time_signature[0]
        
        # Calculate note duration based on number of notes and time signature
        num_notes = len(pattern.notes)
        if num_notes == 0:
            return events
        
        # Distribute notes evenly across the bar
        duration = beats_per_bar / num_notes
        
        for i, note in enumerate(pattern.notes):
            beat = i * duration
            
            event = NoteEvent(
                note=note,
                beat=beat,
                duration=duration
            )
            events.append(event)
        
        return events
    
    def _calculate_phrase_contour(self, bars: List[BarContent]) -> ContourSignature:
        """Calculate the contour signature for a phrase."""
        all_notes = []
        for bar in bars:
            all_notes.extend([event.note for event in bar.notes])
        
        if not all_notes:
            return ContourSignature(
                type=ContourType.FLAT,
                intervals=[],
                directions=[],
                range=0
            )
        
        return ContourSignature.from_notes(all_notes)
    
    def add_rhythm(self, phrases: List[EtudePhrase], rhythm_events: List[Dict]) -> List[EtudePhrase]:
        """
        Apply rhythm events to phrases.
        
        Args:
            phrases: Phrases to modify
            rhythm_events: Rhythm timing information
            
        Returns:
            Modified phrases
        """
        # This will be implemented in conjunction with the rhythm module
        return phrases
    
    def add_guitar_positions(self, phrases: List[EtudePhrase]) -> List[EtudePhrase]:
        """
        Add guitar string/fret positions to note events.
        
        Args:
            phrases: Phrases to modify
            
        Returns:
            Phrases with guitar positions
        """
        for phrase in phrases:
            for bar in phrase.bars:
                for event in bar.notes:
                    string, fret = self._calculate_guitar_position(event.note)
                    event.string = string
                    event.fret = fret
        
        return phrases
    
    def _calculate_guitar_position(self, note: Note) -> Tuple[int, int]:
        """
        Calculate guitar string and fret for a note.
        
        Returns:
            Tuple of (string, fret)
        """
        # Standard tuning: E2, A2, D3, G3, B3, E4
        # MIDI: 40, 45, 50, 55, 59, 64
        string_tunings = [40, 45, 50, 55, 59, 64]  # String 6 to 1
        
        midi = note.midi_number
        
        # Handle string set preference
        string_set = self.config._string_set_enum
        
        if string_set.value == "6-4":
            preferred_strings = [0, 1, 2]  # Strings 6, 5, 4
        elif string_set.value == "5-3":
            preferred_strings = [1, 2, 3]  # Strings 5, 4, 3
        elif string_set.value == "4-2":
            preferred_strings = [2, 3, 4]  # Strings 4, 3, 2
        else:
            preferred_strings = list(range(6))  # All strings
        
        # Find best string/fret combination
        best_string = 6
        best_fret = 0
        best_score = float('inf')
        
        for string_idx in preferred_strings:
            open_pitch = string_tunings[string_idx]
            fret = midi - open_pitch
            
            if 0 <= fret <= 12:  # Playable range
                # Prefer lower positions for beginners
                score = fret
                if self.config._difficulty_enum == Difficulty.BEGINNER:
                    score = fret * 2  # Heavy penalty for high frets
                
                if score < best_score:
                    best_score = score
                    best_string = 6 - string_idx  # Convert to 1-6 numbering
                    best_fret = fret
        
        return (best_string, best_fret)


def stitch_patterns(config: EtudeConfig, harmonic_material: HarmonicMaterial) -> List[EtudePhrase]:
    """
    Convenience function to stitch patterns.
    
    Args:
        config: Etude configuration
        harmonic_material: Harmonic material to use
        
    Returns:
        List of EtudePhrase objects
    """
    stitcher = PatternStitcher(config)
    phrases = stitcher.stitch(harmonic_material)
    return stitcher.add_guitar_positions(phrases)

