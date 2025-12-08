"""
Pattern Engine for Quartet Engine
===================================

Generates musical patterns adapted for string quartet:
- Open-triad inversion sweeps
- Triad-pair intervallic gestures
- Contrapuntal canons
- Staggered entrances
- Hocketed triad tones
- Rhythmic cells
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random

try:
    from .instruments import InstrumentType, QuartetInstruments
    from .inputs import QuartetConfig, PatternType
    from .counterpoint import VoiceLine, VoiceNote
except ImportError:
    from instruments import InstrumentType, QuartetInstruments
    from inputs import QuartetConfig, PatternType
    from counterpoint import VoiceLine, VoiceNote


@dataclass
class PatternCell:
    """
    A single pattern cell.
    
    Attributes:
        instrument: Target instrument
        pitches: List of pitches in the cell
        durations: List of durations
        start_bar: Starting bar
        start_beat: Starting beat
    """
    instrument: InstrumentType
    pitches: List[int]
    durations: List[float]
    start_bar: int
    start_beat: float
    
    def total_duration(self) -> float:
        return sum(self.durations)


@dataclass
class QuartetPattern:
    """
    A complete pattern for the quartet.
    
    Attributes:
        cells: Dict mapping instrument to list of PatternCells
        pattern_type: Type of pattern
        bars: Number of bars
        analysis: Pattern analysis
    """
    cells: Dict[InstrumentType, List[PatternCell]]
    pattern_type: PatternType
    bars: int
    analysis: str = ""
    
    def get_voice_line(self, instrument: InstrumentType) -> VoiceLine:
        """Convert cells to a VoiceLine."""
        notes = []
        if instrument in self.cells:
            for cell in self.cells[instrument]:
                for i, (pitch, dur) in enumerate(zip(cell.pitches, cell.durations)):
                    beat = cell.start_beat
                    for j in range(i):
                        beat += cell.durations[j]
                    
                    notes.append(VoiceNote(
                        pitch=pitch,
                        duration=dur,
                        bar=cell.start_bar,
                        beat=beat
                    ))
        
        return VoiceLine(
            instrument=instrument,
            notes=notes,
            contour="pattern"
        )


class PatternEngine:
    """
    Generates quartet-adapted musical patterns.
    """
    
    NOTE_TO_MIDI = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
        "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
    }
    
    SCALE_PATTERNS = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
    }
    
    TRIAD_INTERVALS = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "dim": [0, 3, 6],
    }
    
    def __init__(self, config: QuartetConfig, seed: Optional[int] = None):
        """
        Initialize the pattern engine.
        
        Args:
            config: Quartet configuration
            seed: Random seed
        """
        self.config = config
        self.key_midi = self.NOTE_TO_MIDI.get(config.key, 0)
        self.scale_pattern = self.SCALE_PATTERNS.get(config.scale, self.SCALE_PATTERNS["major"])
        
        if seed is not None:
            random.seed(seed)
    
    def _build_triad(self, root_pc: int, quality: str, octave: int) -> List[int]:
        """Build triad pitches."""
        root_midi = root_pc + (octave + 1) * 12
        intervals = self.TRIAD_INTERVALS.get(quality, [0, 4, 7])
        return [root_midi + i for i in intervals]
    
    def _get_inversions(self, triad: List[int]) -> List[List[int]]:
        """Get all inversions of a triad."""
        inversions = [triad]
        
        # First inversion
        inv1 = [triad[1], triad[2], triad[0] + 12]
        inversions.append(inv1)
        
        # Second inversion
        inv2 = [triad[2], triad[0] + 12, triad[1] + 12]
        inversions.append(inv2)
        
        return inversions
    
    def generate_inversion_sweep(
        self,
        bars: int,
        root_pc: int = None,
        quality: str = "major"
    ) -> QuartetPattern:
        """
        Generate open-triad inversion sweeps across the quartet.
        
        Args:
            bars: Number of bars
            root_pc: Root pitch class
            quality: Triad quality
        
        Returns:
            QuartetPattern
        """
        root_pc = root_pc if root_pc is not None else self.key_midi
        cells = {inst: [] for inst in InstrumentType}
        
        base_triad = self._build_triad(root_pc, quality, octave=3)
        inversions = self._get_inversions(base_triad)
        
        beats_per_bar = self.config.time_signature[0]
        duration = beats_per_bar / 2  # Half-bar per inversion
        
        for bar in range(1, bars + 1):
            for half in range(2):
                beat = 1.0 + (half * duration)
                inv_idx = ((bar - 1) * 2 + half) % 3
                inv = inversions[inv_idx]
                
                # Distribute inversion across quartet
                instruments = [
                    InstrumentType.CELLO,
                    InstrumentType.VIOLA,
                    InstrumentType.VIOLIN_II,
                    InstrumentType.VIOLIN_I
                ]
                
                for i, inst in enumerate(instruments):
                    inst_def = QuartetInstruments.get_by_type(inst)
                    
                    if i < len(inv):
                        pitch = inv[i]
                    else:
                        # Add bass
                        pitch = inv[0] - 12
                    
                    # Adjust to register
                    while pitch < inst_def.range.low:
                        pitch += 12
                    while pitch > inst_def.range.high:
                        pitch -= 12
                    
                    cells[inst].append(PatternCell(
                        instrument=inst,
                        pitches=[pitch],
                        durations=[duration],
                        start_bar=bar,
                        start_beat=beat
                    ))
        
        return QuartetPattern(
            cells=cells,
            pattern_type=PatternType.INVERSION_CYCLES,
            bars=bars,
            analysis=f"Inversion sweep: {quality} triad cycling through inversions"
        )
    
    def generate_triad_pair_gesture(
        self,
        bars: int,
        pair: Tuple[Tuple[int, str], Tuple[int, str]] = None
    ) -> QuartetPattern:
        """
        Generate triad-pair intervallic gestures.
        
        Args:
            bars: Number of bars
            pair: Tuple of ((root1, quality1), (root2, quality2))
        
        Returns:
            QuartetPattern
        """
        # Default pair: I and ii
        if pair is None:
            pair = (
                (self.key_midi, "major"),
                ((self.key_midi + 2) % 12, "minor")
            )
        
        cells = {inst: [] for inst in InstrumentType}
        
        triad_a = self._build_triad(pair[0][0], pair[0][1], octave=4)
        triad_b = self._build_triad(pair[1][0], pair[1][1], octave=4)
        
        beats_per_bar = self.config.time_signature[0]
        
        for bar in range(1, bars + 1):
            # Alternate between triads each beat
            for beat_idx in range(beats_per_bar):
                beat = 1.0 + beat_idx
                triad = triad_a if beat_idx % 2 == 0 else triad_b
                
                # Arpeggiate across instruments
                instruments = [
                    InstrumentType.CELLO,
                    InstrumentType.VIOLA,
                    InstrumentType.VIOLIN_II,
                    InstrumentType.VIOLIN_I
                ]
                
                for i, inst in enumerate(instruments):
                    if i < len(triad):
                        pitch = triad[i]
                    else:
                        pitch = triad[-1] + 12
                    
                    inst_def = QuartetInstruments.get_by_type(inst)
                    while pitch < inst_def.range.low:
                        pitch += 12
                    while pitch > inst_def.range.high:
                        pitch -= 12
                    
                    cells[inst].append(PatternCell(
                        instrument=inst,
                        pitches=[pitch],
                        durations=[1.0],
                        start_bar=bar,
                        start_beat=beat
                    ))
        
        return QuartetPattern(
            cells=cells,
            pattern_type=PatternType.TRIAD_PAIRS,
            bars=bars,
            analysis="Triad-pair intervallic gesture"
        )
    
    def generate_staggered_entrance(
        self,
        bars: int,
        offset_beats: float = 1.0
    ) -> QuartetPattern:
        """
        Generate staggered entrance pattern.
        
        Each instrument enters one after another.
        
        Args:
            bars: Number of bars
            offset_beats: Beat offset between entrances
        
        Returns:
            QuartetPattern
        """
        cells = {inst: [] for inst in InstrumentType}
        
        instruments = [
            InstrumentType.CELLO,
            InstrumentType.VIOLA,
            InstrumentType.VIOLIN_II,
            InstrumentType.VIOLIN_I
        ]
        
        base_triad = self._build_triad(self.key_midi, "major", octave=3)
        beats_per_bar = self.config.time_signature[0]
        
        for i, inst in enumerate(instruments):
            entry_offset = i * offset_beats
            entry_bar = 1 + int(entry_offset // beats_per_bar)
            entry_beat = 1.0 + (entry_offset % beats_per_bar)
            
            inst_def = QuartetInstruments.get_by_type(inst)
            
            # Each instrument plays from its entry point
            current_bar = entry_bar
            current_beat = entry_beat
            
            while current_bar <= bars:
                pitch = base_triad[i % len(base_triad)]
                while pitch < inst_def.range.low:
                    pitch += 12
                while pitch > inst_def.range.high:
                    pitch -= 12
                
                remaining_in_bar = beats_per_bar - current_beat + 1
                duration = min(2.0, remaining_in_bar)
                
                cells[inst].append(PatternCell(
                    instrument=inst,
                    pitches=[pitch],
                    durations=[duration],
                    start_bar=current_bar,
                    start_beat=current_beat
                ))
                
                current_beat += duration
                if current_beat > beats_per_bar:
                    current_bar += 1
                    current_beat = 1.0
        
        return QuartetPattern(
            cells=cells,
            pattern_type=PatternType.CONTRAPUNTAL_CELLS,
            bars=bars,
            analysis=f"Staggered entrances with {offset_beats} beat offset"
        )
    
    def generate_hocket(
        self,
        bars: int
    ) -> QuartetPattern:
        """
        Generate hocketed triad tones across instruments.
        
        Triad tones are distributed rhythmically across the quartet.
        
        Args:
            bars: Number of bars
        
        Returns:
            QuartetPattern
        """
        cells = {inst: [] for inst in InstrumentType}
        
        triad = self._build_triad(self.key_midi, "major", octave=4)
        instruments = [
            InstrumentType.VIOLIN_I,
            InstrumentType.VIOLIN_II,
            InstrumentType.VIOLA,
            InstrumentType.CELLO
        ]
        
        beats_per_bar = self.config.time_signature[0]
        
        for bar in range(1, bars + 1):
            for eighth_idx in range(beats_per_bar * 2):
                beat = 1.0 + (eighth_idx * 0.5)
                
                # Each eighth note goes to a different instrument
                inst_idx = eighth_idx % 4
                inst = instruments[inst_idx]
                
                # Each instrument gets a different triad tone
                pitch_idx = inst_idx % 3
                pitch = triad[pitch_idx]
                
                inst_def = QuartetInstruments.get_by_type(inst)
                while pitch < inst_def.range.low:
                    pitch += 12
                while pitch > inst_def.range.high:
                    pitch -= 12
                
                cells[inst].append(PatternCell(
                    instrument=inst,
                    pitches=[pitch],
                    durations=[0.5],
                    start_bar=bar,
                    start_beat=beat
                ))
        
        return QuartetPattern(
            cells=cells,
            pattern_type=PatternType.CONTRAPUNTAL_CELLS,
            bars=bars,
            analysis="Hocketed triad tones across quartet"
        )
    
    def generate_open_triad_arpeggiation(
        self,
        bars: int
    ) -> QuartetPattern:
        """
        Generate open-triad arpeggiation spread across all parts.
        
        Args:
            bars: Number of bars
        
        Returns:
            QuartetPattern
        """
        cells = {inst: [] for inst in InstrumentType}
        
        # Open triad spacing
        root = self.key_midi + 36  # C2
        open_triad = [
            root,           # Cello
            root + 12 + 4,  # Viola (M3 + octave)
            root + 24 + 7,  # Vln II (P5 + 2 octaves)
            root + 36,      # Vln I (3 octaves)
        ]
        
        beats_per_bar = self.config.time_signature[0]
        
        instruments = [
            InstrumentType.CELLO,
            InstrumentType.VIOLA,
            InstrumentType.VIOLIN_II,
            InstrumentType.VIOLIN_I
        ]
        
        for bar in range(1, bars + 1):
            for beat_idx in range(beats_per_bar):
                beat = 1.0 + beat_idx
                
                # Arpeggio upward then downward
                if beat_idx < 4:
                    inst_idx = beat_idx % 4
                else:
                    inst_idx = (beats_per_bar - 1 - beat_idx) % 4
                
                inst = instruments[inst_idx]
                pitch = open_triad[inst_idx]
                
                inst_def = QuartetInstruments.get_by_type(inst)
                while pitch < inst_def.range.low:
                    pitch += 12
                while pitch > inst_def.range.high:
                    pitch -= 12
                
                cells[inst].append(PatternCell(
                    instrument=inst,
                    pitches=[pitch],
                    durations=[1.0],
                    start_bar=bar,
                    start_beat=beat
                ))
        
        return QuartetPattern(
            cells=cells,
            pattern_type=PatternType.OPEN_TRIAD_LOOPS,
            bars=bars,
            analysis="Open-triad arpeggiation across quartet"
        )
    
    def generate_rhythmic_cells(
        self,
        bars: int,
        cell_pattern: str = "3:2"
    ) -> QuartetPattern:
        """
        Generate rhythmic cell patterns (polyrhythm, hemiola).
        
        Args:
            bars: Number of bars
            cell_pattern: Pattern type ("3:2", "3:4", "hemiola")
        
        Returns:
            QuartetPattern
        """
        cells = {inst: [] for inst in InstrumentType}
        
        triad = self._build_triad(self.key_midi, "major", octave=4)
        beats_per_bar = self.config.time_signature[0]
        
        for bar in range(1, bars + 1):
            if cell_pattern == "3:2":
                # Violins play 3 notes, lower strings play 2
                # Violins: dotted rhythm
                for vln in [InstrumentType.VIOLIN_I, InstrumentType.VIOLIN_II]:
                    inst_def = QuartetInstruments.get_by_type(vln)
                    pitch = triad[2 if vln == InstrumentType.VIOLIN_I else 1]
                    
                    while pitch < inst_def.range.low:
                        pitch += 12
                    
                    cells[vln].append(PatternCell(
                        instrument=vln,
                        pitches=[pitch, pitch, pitch],
                        durations=[1.33, 1.33, 1.34],
                        start_bar=bar,
                        start_beat=1.0
                    ))
                
                # Lower strings: half notes
                for lower in [InstrumentType.VIOLA, InstrumentType.CELLO]:
                    inst_def = QuartetInstruments.get_by_type(lower)
                    pitch = triad[0] if lower == InstrumentType.CELLO else triad[1]
                    
                    while pitch < inst_def.range.low:
                        pitch += 12
                    while pitch > inst_def.range.high:
                        pitch -= 12
                    
                    cells[lower].append(PatternCell(
                        instrument=lower,
                        pitches=[pitch, pitch],
                        durations=[2.0, 2.0],
                        start_bar=bar,
                        start_beat=1.0
                    ))
            
            elif cell_pattern == "hemiola":
                # Create 2 bars of 3/4 feel in 4/4
                for inst in InstrumentType:
                    inst_def = QuartetInstruments.get_by_type(inst)
                    idx = list(InstrumentType).index(inst)
                    pitch = triad[idx % 3]
                    
                    while pitch < inst_def.range.low:
                        pitch += 12
                    while pitch > inst_def.range.high:
                        pitch -= 12
                    
                    cells[inst].append(PatternCell(
                        instrument=inst,
                        pitches=[pitch, pitch, pitch],
                        durations=[1.33, 1.33, 1.34],
                        start_bar=bar,
                        start_beat=1.0
                    ))
        
        return QuartetPattern(
            cells=cells,
            pattern_type=PatternType.CONTRAPUNTAL_CELLS,
            bars=bars,
            analysis=f"Rhythmic cells: {cell_pattern} pattern"
        )
    
    def generate_pattern(
        self,
        bars: int = None,
        pattern_type: PatternType = None
    ) -> QuartetPattern:
        """
        Generate pattern based on configuration.
        
        Args:
            bars: Number of bars
            pattern_type: Pattern type
        
        Returns:
            QuartetPattern
        """
        bars = bars or self.config.length
        pattern_type = pattern_type or self.config.pattern_type
        
        if pattern_type == PatternType.INVERSION_CYCLES:
            return self.generate_inversion_sweep(bars)
        elif pattern_type == PatternType.OPEN_TRIAD_LOOPS:
            return self.generate_open_triad_arpeggiation(bars)
        elif pattern_type == PatternType.TRIAD_PAIRS:
            return self.generate_triad_pair_gesture(bars)
        elif pattern_type == PatternType.CONTRAPUNTAL_CELLS:
            return self.generate_hocket(bars)
        else:
            return self.generate_inversion_sweep(bars)

