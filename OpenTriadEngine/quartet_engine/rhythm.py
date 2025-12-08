"""
Rhythmic Engine for Quartet Engine
====================================

Supports:
- Unified rhythm across voices
- Staggered rhythm (offset voices)
- Ostinatos
- Polyrhythm (3:2, 3:4)
- Sustained pads vs active lines
- Articulation (pizz/arco/staccato)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random

try:
    from .instruments import InstrumentType
    from .inputs import QuartetConfig, RhythmicStyle
except ImportError:
    from instruments import InstrumentType
    from inputs import QuartetConfig, RhythmicStyle


class Articulation(Enum):
    """String articulations."""
    ARCO = "arco"
    PIZZ = "pizzicato"
    STACCATO = "staccato"
    LEGATO = "legato"
    TENUTO = "tenuto"
    ACCENT = "accent"
    TREMOLO = "tremolo"


@dataclass
class RhythmicEvent:
    """
    A rhythmic event (onset + duration).
    
    Attributes:
        onset: Beat position (1.0 = downbeat)
        duration: Duration in beats
        accent: Accent strength (0.0-1.0)
        articulation: Optional articulation
    """
    onset: float
    duration: float
    accent: float = 0.5
    articulation: Optional[Articulation] = None


@dataclass
class RhythmicPattern:
    """
    A rhythmic pattern for one instrument.
    
    Attributes:
        instrument: Target instrument
        events: List of RhythmicEvent objects
        bar_length: Length in beats
    """
    instrument: InstrumentType
    events: List[RhythmicEvent]
    bar_length: float = 4.0
    
    def get_onsets(self) -> List[float]:
        return [e.onset for e in self.events]
    
    def get_durations(self) -> List[float]:
        return [e.duration for e in self.events]


@dataclass
class QuartetRhythm:
    """
    Complete rhythmic structure for the quartet.
    
    Attributes:
        patterns: Dict mapping instrument to RhythmicPattern
        bars: Number of bars
        style: Rhythmic style
    """
    patterns: Dict[InstrumentType, RhythmicPattern]
    bars: int
    style: RhythmicStyle


class RhythmEngine:
    """
    Generates rhythmic patterns for string quartet.
    """
    
    # Predefined rhythmic cells
    QUARTER_NOTES = [(0.0, 1.0), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0)]
    HALF_NOTES = [(0.0, 2.0), (2.0, 2.0)]
    WHOLE_NOTE = [(0.0, 4.0)]
    EIGHTH_NOTES = [
        (0.0, 0.5), (0.5, 0.5), (1.0, 0.5), (1.5, 0.5),
        (2.0, 0.5), (2.5, 0.5), (3.0, 0.5), (3.5, 0.5)
    ]
    
    SYNCOPATED_1 = [(0.0, 1.5), (1.5, 1.0), (2.5, 1.5)]
    SYNCOPATED_2 = [(0.5, 1.0), (1.5, 1.0), (2.5, 1.0), (3.5, 0.5)]
    
    DOTTED = [(0.0, 1.5), (1.5, 0.5), (2.0, 1.5), (3.5, 0.5)]
    
    TRIPLET_QUARTER = [(0.0, 1.33), (1.33, 1.33), (2.66, 1.34)]
    
    OSTINATO_BASS = [(0.0, 0.5), (0.5, 0.5), (1.0, 0.5), (1.5, 0.5),
                     (2.0, 0.5), (2.5, 0.5), (3.0, 0.5), (3.5, 0.5)]
    
    def __init__(self, config: QuartetConfig, seed: Optional[int] = None):
        """
        Initialize the rhythm engine.
        
        Args:
            config: Quartet configuration
            seed: Random seed
        """
        self.config = config
        self.beats_per_bar = config.time_signature[0]
        
        if seed is not None:
            random.seed(seed)
    
    def _create_events(
        self,
        rhythm_data: List[Tuple[float, float]],
        articulation: Articulation = None
    ) -> List[RhythmicEvent]:
        """Create RhythmicEvent list from onset/duration tuples."""
        events = []
        for onset, duration in rhythm_data:
            events.append(RhythmicEvent(
                onset=onset,
                duration=duration,
                accent=0.8 if onset == 0.0 else 0.4,
                articulation=articulation
            ))
        return events
    
    def generate_unified(
        self,
        bars: int
    ) -> QuartetRhythm:
        """
        Generate unified rhythm - all instruments align.
        
        Args:
            bars: Number of bars
        
        Returns:
            QuartetRhythm
        """
        # Choose a basic rhythm pattern
        base_rhythm = self.HALF_NOTES
        
        patterns = {}
        for inst in InstrumentType:
            all_events = []
            for bar in range(bars):
                bar_offset = bar * self.beats_per_bar
                events = self._create_events(base_rhythm)
                for e in events:
                    e.onset += bar_offset
                all_events.extend(events)
            
            patterns[inst] = RhythmicPattern(
                instrument=inst,
                events=all_events,
                bar_length=self.beats_per_bar
            )
        
        return QuartetRhythm(
            patterns=patterns,
            bars=bars,
            style=RhythmicStyle.STRAIGHT
        )
    
    def generate_staggered(
        self,
        bars: int,
        offset: float = 0.5
    ) -> QuartetRhythm:
        """
        Generate staggered rhythm - voices offset.
        
        Args:
            bars: Number of bars
            offset: Beat offset between voices
        
        Returns:
            QuartetRhythm
        """
        patterns = {}
        instruments = list(InstrumentType)
        
        for i, inst in enumerate(instruments):
            all_events = []
            inst_offset = i * offset
            
            for bar in range(bars):
                bar_offset = bar * self.beats_per_bar
                
                # Each instrument gets quarter notes, staggered
                for beat in range(int(self.beats_per_bar)):
                    onset = bar_offset + beat + inst_offset
                    onset = onset % (bars * self.beats_per_bar)
                    
                    all_events.append(RhythmicEvent(
                        onset=onset,
                        duration=1.0 - offset if offset > 0 else 1.0,
                        accent=0.7 if beat == 0 else 0.4
                    ))
            
            patterns[inst] = RhythmicPattern(
                instrument=inst,
                events=sorted(all_events, key=lambda e: e.onset),
                bar_length=self.beats_per_bar
            )
        
        return QuartetRhythm(
            patterns=patterns,
            bars=bars,
            style=RhythmicStyle.MIXED
        )
    
    def generate_ostinato(
        self,
        bars: int,
        ostinato_instruments: List[InstrumentType] = None
    ) -> QuartetRhythm:
        """
        Generate ostinato pattern.
        
        Args:
            bars: Number of bars
            ostinato_instruments: Instruments playing ostinato
        
        Returns:
            QuartetRhythm
        """
        if ostinato_instruments is None:
            ostinato_instruments = [InstrumentType.CELLO, InstrumentType.VIOLA]
        
        patterns = {}
        
        for inst in InstrumentType:
            all_events = []
            
            if inst in ostinato_instruments:
                # Ostinato pattern (steady eighth notes)
                for bar in range(bars):
                    bar_offset = bar * self.beats_per_bar
                    events = self._create_events(self.OSTINATO_BASS)
                    for e in events:
                        e.onset += bar_offset
                    all_events.extend(events)
            else:
                # Long notes for melody instruments
                for bar in range(bars):
                    bar_offset = bar * self.beats_per_bar
                    all_events.append(RhythmicEvent(
                        onset=bar_offset,
                        duration=self.beats_per_bar,
                        accent=0.6
                    ))
            
            patterns[inst] = RhythmicPattern(
                instrument=inst,
                events=all_events,
                bar_length=self.beats_per_bar
            )
        
        return QuartetRhythm(
            patterns=patterns,
            bars=bars,
            style=RhythmicStyle.OSTINATO
        )
    
    def generate_polyrhythm(
        self,
        bars: int,
        pattern: str = "3:2"
    ) -> QuartetRhythm:
        """
        Generate polyrhythmic pattern.
        
        Args:
            bars: Number of bars
            pattern: Polyrhythm pattern ("3:2", "3:4")
        
        Returns:
            QuartetRhythm
        """
        patterns = {}
        
        if pattern == "3:2":
            # Upper strings: 3 notes
            # Lower strings: 2 notes
            upper_rhythm = self.TRIPLET_QUARTER
            lower_rhythm = self.HALF_NOTES
            
            upper_insts = [InstrumentType.VIOLIN_I, InstrumentType.VIOLIN_II]
            lower_insts = [InstrumentType.VIOLA, InstrumentType.CELLO]
        
        else:  # 3:4
            upper_rhythm = self.TRIPLET_QUARTER
            lower_rhythm = self.QUARTER_NOTES
            
            upper_insts = [InstrumentType.VIOLIN_I]
            lower_insts = [InstrumentType.VIOLIN_II, InstrumentType.VIOLA, InstrumentType.CELLO]
        
        for inst in InstrumentType:
            all_events = []
            
            if inst in upper_insts:
                rhythm = upper_rhythm
            else:
                rhythm = lower_rhythm
            
            for bar in range(bars):
                bar_offset = bar * self.beats_per_bar
                events = self._create_events(rhythm)
                for e in events:
                    e.onset += bar_offset
                all_events.extend(events)
            
            patterns[inst] = RhythmicPattern(
                instrument=inst,
                events=all_events,
                bar_length=self.beats_per_bar
            )
        
        return QuartetRhythm(
            patterns=patterns,
            bars=bars,
            style=RhythmicStyle.MIXED
        )
    
    def generate_syncopated(
        self,
        bars: int
    ) -> QuartetRhythm:
        """
        Generate syncopated rhythm.
        
        Args:
            bars: Number of bars
        
        Returns:
            QuartetRhythm
        """
        patterns = {}
        
        synco_patterns = [
            self.SYNCOPATED_1,
            self.SYNCOPATED_2,
            self.DOTTED,
        ]
        
        for i, inst in enumerate(InstrumentType):
            all_events = []
            rhythm = synco_patterns[i % len(synco_patterns)]
            
            for bar in range(bars):
                bar_offset = bar * self.beats_per_bar
                events = self._create_events(rhythm)
                for e in events:
                    e.onset += bar_offset
                all_events.extend(events)
            
            patterns[inst] = RhythmicPattern(
                instrument=inst,
                events=all_events,
                bar_length=self.beats_per_bar
            )
        
        return QuartetRhythm(
            patterns=patterns,
            bars=bars,
            style=RhythmicStyle.SYNCOPATED
        )
    
    def generate_pads_vs_active(
        self,
        bars: int,
        active_instruments: List[InstrumentType] = None
    ) -> QuartetRhythm:
        """
        Generate sustained pads vs active melodic lines.
        
        Args:
            bars: Number of bars
            active_instruments: Instruments with active rhythm
        
        Returns:
            QuartetRhythm
        """
        if active_instruments is None:
            active_instruments = [InstrumentType.VIOLIN_I]
        
        patterns = {}
        
        for inst in InstrumentType:
            all_events = []
            
            if inst in active_instruments:
                # Active: eighth note or quarter note motion
                for bar in range(bars):
                    bar_offset = bar * self.beats_per_bar
                    events = self._create_events(self.QUARTER_NOTES)
                    for e in events:
                        e.onset += bar_offset
                    all_events.extend(events)
            else:
                # Pad: whole notes
                for bar in range(bars):
                    bar_offset = bar * self.beats_per_bar
                    all_events.append(RhythmicEvent(
                        onset=bar_offset,
                        duration=self.beats_per_bar,
                        accent=0.4,
                        articulation=Articulation.LEGATO
                    ))
            
            patterns[inst] = RhythmicPattern(
                instrument=inst,
                events=all_events,
                bar_length=self.beats_per_bar
            )
        
        return QuartetRhythm(
            patterns=patterns,
            bars=bars,
            style=RhythmicStyle.STRAIGHT
        )
    
    def add_articulations(
        self,
        rhythm: QuartetRhythm,
        articulation_map: Dict[InstrumentType, Articulation] = None
    ) -> QuartetRhythm:
        """
        Add articulation markings to a rhythm.
        
        Args:
            rhythm: QuartetRhythm to modify
            articulation_map: Articulation per instrument
        
        Returns:
            Modified QuartetRhythm
        """
        if articulation_map is None:
            articulation_map = {
                InstrumentType.VIOLIN_I: Articulation.LEGATO,
                InstrumentType.VIOLIN_II: Articulation.LEGATO,
                InstrumentType.VIOLA: Articulation.ARCO,
                InstrumentType.CELLO: Articulation.ARCO,
            }
        
        for inst, pattern in rhythm.patterns.items():
            art = articulation_map.get(inst, Articulation.ARCO)
            for event in pattern.events:
                event.articulation = art
        
        return rhythm
    
    def generate_rhythm(
        self,
        bars: int = None,
        style: RhythmicStyle = None
    ) -> QuartetRhythm:
        """
        Generate rhythm based on configuration.
        
        Args:
            bars: Number of bars
            style: Rhythmic style
        
        Returns:
            QuartetRhythm
        """
        bars = bars or self.config.length
        style = style or self.config.rhythmic_style
        
        if style == RhythmicStyle.STRAIGHT:
            return self.generate_unified(bars)
        elif style == RhythmicStyle.SYNCOPATED:
            return self.generate_syncopated(bars)
        elif style == RhythmicStyle.MIXED:
            return self.generate_staggered(bars)
        elif style == RhythmicStyle.OSTINATO:
            return self.generate_ostinato(bars)
        else:
            return self.generate_unified(bars)

