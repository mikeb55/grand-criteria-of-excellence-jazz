"""
Rhythm Generation Module for Etude Generator
=============================================

Generates rhythmic patterns and applies them to melodic phrases.
Uses the Open Triad Engine's rhythmic templates.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from open_triad_engine.output_shapes import RhythmicTemplate, RhythmType, RhythmLibrary

from .inputs import EtudeConfig, RhythmicStyle, Difficulty
from .patterns import EtudePhrase, BarContent, NoteEvent


@dataclass
class RhythmEvent:
    """
    A single rhythm event.
    
    Attributes:
        beat: Beat position (0-indexed)
        duration: Duration in beats
        accent: Whether this beat is accented
        subdivision: Subdivision type (1=quarter, 2=eighth, 3=triplet, 4=sixteenth)
    """
    beat: float
    duration: float
    accent: bool = False
    subdivision: int = 2
    
    def to_dict(self) -> Dict:
        return {
            'beat': self.beat,
            'duration': self.duration,
            'accent': self.accent,
            'subdivision': self.subdivision,
        }


@dataclass
class RhythmicPhrase:
    """
    A rhythmic phrase for a bar.
    
    Attributes:
        events: List of rhythm events
        style: Rhythmic style used
        time_signature: Time signature
    """
    events: List[RhythmEvent]
    style: RhythmicStyle
    time_signature: Tuple[int, int] = (4, 4)
    
    @property
    def total_beats(self) -> float:
        return sum(e.duration for e in self.events)
    
    def to_dict(self) -> Dict:
        return {
            'events': [e.to_dict() for e in self.events],
            'style': self.style.value,
            'time_signature': list(self.time_signature),
        }


class RhythmGenerator:
    """
    Generates rhythmic patterns for etudes.
    
    Supports:
    - Straight eighths
    - Syncopated patterns
    - Triplet/jazz phrasing
    - Polyrhythm (advanced)
    """
    
    # Base rhythm patterns for different styles
    RHYTHM_PATTERNS = {
        RhythmicStyle.STRAIGHT: [
            # Straight eighths
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            # Straight quarters
            [1.0, 1.0, 1.0, 1.0],
            # Mixed
            [1.0, 0.5, 0.5, 1.0, 1.0],
        ],
        RhythmicStyle.SYNCOPATED: [
            # Basic syncopation
            [0.75, 0.25, 0.5, 0.5, 0.75, 0.25, 0.5, 0.5],
            # Anticipation
            [0.5, 0.5, 0.5, 0.5, 0.25, 0.75, 0.5, 0.5],
            # Off-beat accents
            [0.5, 1.0, 0.5, 0.5, 1.0, 0.5],
        ],
        RhythmicStyle.TRIPLET: [
            # Triplet eighths
            [1/3, 1/3, 1/3, 1/3, 1/3, 1/3, 1/3, 1/3, 1/3, 1/3, 1/3, 1/3],
            # Mixed triplet/duple
            [1/3, 1/3, 1/3, 0.5, 0.5, 1/3, 1/3, 1/3, 1.0],
            # Quarter-note triplets
            [2/3, 2/3, 2/3, 2/3, 2/3, 2/3],
        ],
        RhythmicStyle.SWING: [
            # Swing eighths (long-short)
            [2/3, 1/3, 2/3, 1/3, 2/3, 1/3, 2/3, 1/3],
            # Swing with held notes
            [2/3, 1/3, 1.0, 2/3, 1/3, 1.0],
        ],
        RhythmicStyle.POLYRHYTHMIC: [
            # 3 over 4
            [4/3, 4/3, 4/3],
            # 5 over 4
            [4/5, 4/5, 4/5, 4/5, 4/5],
            # Mixed polyrhythm
            [1.0, 4/3, 4/3, 4/3 - 1.0 + 4],  # This needs adjustment
        ],
    }
    
    # Accent patterns for different styles
    ACCENT_PATTERNS = {
        RhythmicStyle.STRAIGHT: [0, 4],           # Beat 1 and 3
        RhythmicStyle.SYNCOPATED: [0, 2, 5],      # Off-beats
        RhythmicStyle.TRIPLET: [0, 3, 6, 9],      # Every third note
        RhythmicStyle.SWING: [0, 2, 4, 6],        # Downbeats
        RhythmicStyle.POLYRHYTHMIC: [0],          # Just the first
    }
    
    def __init__(self, config: EtudeConfig):
        """
        Initialize the rhythm generator.
        
        Args:
            config: Etude configuration
        """
        self.config = config
        self.style = config._rhythmic_style_enum
        self.time_sig = config.time_signature
        
        # Get appropriate patterns for difficulty
        self._filter_patterns_for_difficulty()
    
    def _filter_patterns_for_difficulty(self):
        """Filter rhythm patterns based on difficulty."""
        difficulty = self.config._difficulty_enum
        
        if difficulty == Difficulty.BEGINNER:
            # Only use straight rhythms for beginners
            self.available_patterns = self.RHYTHM_PATTERNS[RhythmicStyle.STRAIGHT][:2]
        elif difficulty == Difficulty.INTERMEDIATE:
            # Use current style's patterns
            self.available_patterns = self.RHYTHM_PATTERNS.get(
                self.style, self.RHYTHM_PATTERNS[RhythmicStyle.STRAIGHT]
            )
        else:
            # Advanced: all patterns for the style
            self.available_patterns = self.RHYTHM_PATTERNS.get(
                self.style, self.RHYTHM_PATTERNS[RhythmicStyle.STRAIGHT]
            )
    
    def generate_bar_rhythm(self, bar_number: int, num_notes: int) -> RhythmicPhrase:
        """
        Generate rhythm for a single bar.
        
        Args:
            bar_number: Bar number (for variation)
            num_notes: Number of notes to fit
            
        Returns:
            RhythmicPhrase for the bar
        """
        beats_per_bar = self.time_sig[0]
        
        # Select a pattern
        pattern_idx = (bar_number - 1) % len(self.available_patterns)
        base_pattern = self.available_patterns[pattern_idx]
        
        # Adjust pattern length to match num_notes
        rhythm = self._adjust_pattern_length(base_pattern, num_notes, beats_per_bar)
        
        # Create events
        events = []
        current_beat = 0.0
        accent_positions = self.ACCENT_PATTERNS.get(self.style, [0])
        
        for i, duration in enumerate(rhythm):
            events.append(RhythmEvent(
                beat=current_beat,
                duration=duration,
                accent=(i in accent_positions),
                subdivision=self._get_subdivision(duration)
            ))
            current_beat += duration
        
        return RhythmicPhrase(
            events=events,
            style=self.style,
            time_signature=self.time_sig
        )
    
    def _adjust_pattern_length(
        self, 
        pattern: List[float], 
        target_notes: int,
        beats_per_bar: float
    ) -> List[float]:
        """Adjust a rhythm pattern to fit a specific number of notes."""
        if len(pattern) == target_notes:
            return pattern
        
        if target_notes <= 0:
            return [beats_per_bar]
        
        # Calculate even distribution
        duration = beats_per_bar / target_notes
        return [duration] * target_notes
    
    def _get_subdivision(self, duration: float) -> int:
        """Get the subdivision type for a duration."""
        if abs(duration - 1.0) < 0.1:
            return 1  # Quarter
        elif abs(duration - 0.5) < 0.1:
            return 2  # Eighth
        elif abs(duration - 1/3) < 0.05:
            return 3  # Triplet
        elif abs(duration - 0.25) < 0.05:
            return 4  # Sixteenth
        else:
            return 2  # Default to eighth
    
    def apply_rhythm_to_phrase(self, phrase: EtudePhrase) -> EtudePhrase:
        """
        Apply rhythmic patterns to an etude phrase.
        
        Args:
            phrase: The phrase to modify
            
        Returns:
            Modified phrase with rhythm applied
        """
        for bar in phrase.bars:
            rhythm = self.generate_bar_rhythm(bar.bar_number, len(bar.notes))
            
            # Apply rhythm events to notes
            for i, (note_event, rhythm_event) in enumerate(zip(bar.notes, rhythm.events)):
                note_event.beat = rhythm_event.beat
                note_event.duration = rhythm_event.duration
        
        return phrase
    
    def apply_rhythm_to_phrases(self, phrases: List[EtudePhrase]) -> List[EtudePhrase]:
        """Apply rhythm to multiple phrases."""
        return [self.apply_rhythm_to_phrase(p) for p in phrases]
    
    def generate_count_in(self, bars: int = 1) -> List[RhythmEvent]:
        """Generate a count-in rhythm."""
        events = []
        beats_per_bar = self.time_sig[0]
        
        for i in range(bars * beats_per_bar):
            events.append(RhythmEvent(
                beat=float(i),
                duration=1.0,
                accent=(i % beats_per_bar == 0)
            ))
        
        return events


def apply_rhythm(config: EtudeConfig, phrases: List[EtudePhrase]) -> List[EtudePhrase]:
    """
    Convenience function to apply rhythm to phrases.
    
    Args:
        config: Etude configuration
        phrases: Phrases to modify
        
    Returns:
        Phrases with rhythm applied
    """
    generator = RhythmGenerator(config)
    return generator.apply_rhythm_to_phrases(phrases)

