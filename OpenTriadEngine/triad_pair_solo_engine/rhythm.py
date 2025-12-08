"""
Rhythm Engine for Triad Pair Solo Engine
==========================================

Implements rhythmic options:
- Straight 8ths
- Triplet-based jazz phrasing
- Swing-feel grid
- Syncopation templates
- Polyrhythmic cells (3 over 4, 5 over 4)
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum
import random

try:
    from .inputs import RhythmicStyle, SoloDifficulty
    from .patterns import PatternNote, MelodicCell
except ImportError:
    from inputs import RhythmicStyle, SoloDifficulty
    from patterns import PatternNote, MelodicCell


@dataclass
class RhythmicEvent:
    """
    A rhythmic event (note onset with duration).
    
    Attributes:
        onset: Beat position (0.0 = downbeat)
        duration: Duration in beats
        accent: Whether this is an accented beat
        swing_offset: Swing displacement amount
    """
    onset: float
    duration: float
    accent: bool = False
    swing_offset: float = 0.0


@dataclass
class RhythmicTemplate:
    """
    A rhythmic template for a bar or phrase.
    
    Attributes:
        events: List of RhythmicEvents
        name: Template name
        style: Rhythmic style
        bar_length: Length in beats
    """
    events: List[RhythmicEvent]
    name: str
    style: RhythmicStyle
    bar_length: float = 4.0
    
    def get_durations(self) -> List[float]:
        """Get list of durations."""
        return [e.duration for e in self.events]
    
    def get_onsets(self) -> List[float]:
        """Get list of onset times."""
        return [e.onset for e in self.events]


class SoloRhythmEngine:
    """
    Generates and applies rhythmic templates for jazz soloing.
    """
    
    # Predefined rhythmic patterns (onset, duration, accent)
    STRAIGHT_8THS = [
        (0.0, 0.5, True), (0.5, 0.5, False),
        (1.0, 0.5, True), (1.5, 0.5, False),
        (2.0, 0.5, True), (2.5, 0.5, False),
        (3.0, 0.5, True), (3.5, 0.5, False),
    ]
    
    SWING_8THS = [
        (0.0, 0.67, True), (0.67, 0.33, False),
        (1.0, 0.67, True), (1.67, 0.33, False),
        (2.0, 0.67, True), (2.67, 0.33, False),
        (3.0, 0.67, True), (3.67, 0.33, False),
    ]
    
    TRIPLET_FEEL = [
        (0.0, 0.33, True), (0.33, 0.33, False), (0.67, 0.33, False),
        (1.0, 0.33, True), (1.33, 0.33, False), (1.67, 0.33, False),
        (2.0, 0.33, True), (2.33, 0.33, False), (2.67, 0.33, False),
        (3.0, 0.33, True), (3.33, 0.33, False), (3.67, 0.33, False),
    ]
    
    SYNCOPATED_PATTERNS = [
        # Pattern 1: Anticipations
        [(0.0, 0.5, True), (0.5, 1.0, True), (1.5, 0.5, False),
         (2.0, 0.5, True), (2.5, 1.0, True), (3.5, 0.5, False)],
        # Pattern 2: Offbeat emphasis
        [(0.5, 0.5, True), (1.0, 0.5, False), (1.5, 0.5, True),
         (2.5, 0.5, True), (3.0, 0.5, False), (3.5, 0.5, True)],
        # Pattern 3: Charleston-like
        [(0.0, 0.75, True), (1.5, 0.75, True), (2.25, 0.75, False), (3.5, 0.5, True)],
        # Pattern 4: Clave-inspired
        [(0.0, 0.5, True), (0.75, 0.5, True), (1.5, 0.5, True),
         (2.5, 0.5, True), (3.25, 0.5, True)],
    ]
    
    POLYRHYTHMIC_3_OVER_4 = [
        (0.0, 1.33, True), (1.33, 1.33, False), (2.67, 1.33, True),
    ]
    
    POLYRHYTHMIC_5_OVER_4 = [
        (0.0, 0.8, True), (0.8, 0.8, False), (1.6, 0.8, True),
        (2.4, 0.8, False), (3.2, 0.8, True),
    ]
    
    def __init__(
        self, 
        default_style: RhythmicStyle = RhythmicStyle.SWING,
        difficulty: SoloDifficulty = SoloDifficulty.INTERMEDIATE,
        seed: Optional[int] = None
    ):
        """
        Initialize the rhythm engine.
        
        Args:
            default_style: Default rhythmic style
            difficulty: Affects rhythmic complexity
            seed: Random seed for reproducibility
        """
        self.default_style = default_style
        self.difficulty = difficulty
        if seed is not None:
            random.seed(seed)
    
    def get_template(
        self, 
        style: RhythmicStyle = None,
        bar_length: float = 4.0
    ) -> RhythmicTemplate:
        """
        Get a rhythmic template for the specified style.
        
        Args:
            style: Rhythmic style (uses default if None)
            bar_length: Bar length in beats
        
        Returns:
            RhythmicTemplate object
        """
        style = style or self.default_style
        
        if style == RhythmicStyle.STRAIGHT:
            events = self._events_from_pattern(self.STRAIGHT_8THS, bar_length)
            name = "Straight 8ths"
        elif style == RhythmicStyle.SWING:
            events = self._events_from_pattern(self.SWING_8THS, bar_length)
            name = "Swing 8ths"
        elif style == RhythmicStyle.TRIPLET:
            events = self._events_from_pattern(self.TRIPLET_FEEL, bar_length)
            name = "Triplet Feel"
        elif style == RhythmicStyle.SYNCOPATED:
            pattern = random.choice(self.SYNCOPATED_PATTERNS)
            events = self._events_from_pattern(pattern, bar_length)
            name = "Syncopated"
        elif style == RhythmicStyle.POLYRHYTHMIC:
            if random.random() > 0.5:
                events = self._events_from_pattern(self.POLYRHYTHMIC_3_OVER_4, bar_length)
                name = "3 over 4"
            else:
                events = self._events_from_pattern(self.POLYRHYTHMIC_5_OVER_4, bar_length)
                name = "5 over 4"
        else:
            events = self._events_from_pattern(self.SWING_8THS, bar_length)
            name = "Swing 8ths"
        
        return RhythmicTemplate(
            events=events,
            name=name,
            style=style,
            bar_length=bar_length
        )
    
    def _events_from_pattern(
        self, 
        pattern: List[Tuple[float, float, bool]],
        bar_length: float
    ) -> List[RhythmicEvent]:
        """Convert pattern tuples to RhythmicEvent objects."""
        events = []
        for onset, duration, accent in pattern:
            if onset < bar_length:
                # Clip duration if it exceeds bar
                clipped_duration = min(duration, bar_length - onset)
                events.append(RhythmicEvent(
                    onset=onset,
                    duration=clipped_duration,
                    accent=accent
                ))
        return events
    
    def apply_swing(
        self, 
        events: List[RhythmicEvent],
        swing_amount: float = 0.33
    ) -> List[RhythmicEvent]:
        """
        Apply swing feel to a list of rhythmic events.
        
        Args:
            events: Input events
            swing_amount: Amount of swing (0.0 = straight, 0.5 = max)
        
        Returns:
            Events with swing applied
        """
        swung_events = []
        for event in events:
            # Apply swing to offbeats (8th note offbeats)
            beat_fraction = event.onset % 1.0
            if 0.4 < beat_fraction < 0.6:  # Offbeat 8th
                new_onset = event.onset + swing_amount
            else:
                new_onset = event.onset
            
            swung_events.append(RhythmicEvent(
                onset=new_onset,
                duration=event.duration,
                accent=event.accent,
                swing_offset=swing_amount if 0.4 < beat_fraction < 0.6 else 0.0
            ))
        
        return swung_events
    
    def generate_variation(
        self, 
        template: RhythmicTemplate,
        variation_amount: float = 0.3
    ) -> RhythmicTemplate:
        """
        Generate a variation of a rhythmic template.
        
        Args:
            template: Base template
            variation_amount: How much to vary (0.0-1.0)
        
        Returns:
            New varied RhythmicTemplate
        """
        new_events = []
        
        for event in template.events:
            # Randomly vary duration and accent
            if random.random() < variation_amount:
                # Tie to next note (longer duration)
                new_duration = event.duration * (1.0 + random.uniform(0, 0.5))
            elif random.random() < variation_amount:
                # Shorten
                new_duration = event.duration * random.uniform(0.5, 1.0)
            else:
                new_duration = event.duration
            
            # Random accent changes
            new_accent = event.accent
            if random.random() < variation_amount * 0.5:
                new_accent = not new_accent
            
            new_events.append(RhythmicEvent(
                onset=event.onset,
                duration=new_duration,
                accent=new_accent,
                swing_offset=event.swing_offset
            ))
        
        return RhythmicTemplate(
            events=new_events,
            name=f"{template.name} (varied)",
            style=template.style,
            bar_length=template.bar_length
        )
    
    def apply_rhythm_to_notes(
        self,
        notes: List[PatternNote],
        template: RhythmicTemplate
    ) -> List[PatternNote]:
        """
        Apply a rhythmic template to a list of notes.
        
        Args:
            notes: Input pattern notes
            template: Rhythmic template to apply
        
        Returns:
            Notes with adjusted durations
        """
        if not notes or not template.events:
            return notes
        
        rhythmized = []
        template_events = template.events
        
        for i, note in enumerate(notes):
            # Cycle through template events
            event = template_events[i % len(template_events)]
            
            rhythmized.append(PatternNote(
                pitch=note.pitch,
                pitch_name=note.pitch_name,
                duration=event.duration,
                triad_source=note.triad_source,
                voice=note.voice,
                string=note.string,
                fret=note.fret,
                articulation="accent" if event.accent else note.articulation
            ))
        
        return rhythmized
    
    def apply_rhythm_to_cell(
        self,
        cell: MelodicCell,
        template: RhythmicTemplate
    ) -> MelodicCell:
        """
        Apply a rhythmic template to a melodic cell.
        
        Args:
            cell: Input melodic cell
            template: Rhythmic template to apply
        
        Returns:
            New MelodicCell with rhythmized notes
        """
        rhythmized_notes = self.apply_rhythm_to_notes(cell.notes, template)
        
        return MelodicCell(
            notes=rhythmized_notes,
            pattern_type=cell.pattern_type,
            triad_pair=cell.triad_pair,
            contour=cell.contour
        )
    
    def generate_phrase_rhythm(
        self,
        num_bars: int,
        style: RhythmicStyle = None,
        with_variations: bool = True
    ) -> List[RhythmicTemplate]:
        """
        Generate rhythmic templates for a multi-bar phrase.
        
        Args:
            num_bars: Number of bars
            style: Rhythmic style
            with_variations: Whether to vary rhythms across bars
        
        Returns:
            List of RhythmicTemplate objects (one per bar)
        """
        templates = []
        base_template = self.get_template(style or self.default_style)
        
        for i in range(num_bars):
            if with_variations and i > 0:
                # Vary the base template
                variation_amount = 0.2 + (self.difficulty.value == "advanced") * 0.2
                templates.append(self.generate_variation(base_template, variation_amount))
            else:
                templates.append(base_template)
        
        return templates
    
    def get_beat_accents(
        self, 
        style: RhythmicStyle,
        bar_length: float = 4.0
    ) -> List[Tuple[float, float]]:
        """
        Get beat accent positions and strengths for a style.
        
        Args:
            style: Rhythmic style
            bar_length: Bar length in beats
        
        Returns:
            List of (beat_position, accent_strength) tuples
        """
        if style == RhythmicStyle.STRAIGHT:
            # Equal emphasis on all downbeats
            return [(0.0, 1.0), (1.0, 0.7), (2.0, 0.9), (3.0, 0.7)]
        elif style == RhythmicStyle.SWING:
            # Jazz: 2 and 4 emphasis
            return [(0.0, 0.6), (1.0, 0.9), (2.0, 0.6), (3.0, 0.9)]
        elif style == RhythmicStyle.TRIPLET:
            # First of each triplet
            return [(0.0, 1.0), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0)]
        elif style == RhythmicStyle.SYNCOPATED:
            # Offbeat emphasis
            return [(0.5, 0.9), (1.5, 0.7), (2.5, 0.9), (3.5, 0.7)]
        else:
            return [(0.0, 1.0), (1.0, 0.7), (2.0, 0.9), (3.0, 0.7)]
    
    def create_rest_pattern(
        self,
        total_beats: float,
        rest_probability: float = 0.2
    ) -> List[bool]:
        """
        Create a pattern indicating which rhythmic positions should be rests.
        
        Args:
            total_beats: Total number of beats
            rest_probability: Probability of each position being a rest
        
        Returns:
            List of booleans (True = note, False = rest)
        """
        # Discretize into 8th notes
        num_positions = int(total_beats * 2)
        pattern = []
        
        for i in range(num_positions):
            # Never rest on strong beats (positions 0, 4, 8, etc.)
            if i % 4 == 0:
                pattern.append(True)
            elif random.random() > rest_probability:
                pattern.append(True)
            else:
                pattern.append(False)
        
        return pattern

