"""
Counterpoint Engine for Quartet Engine
=======================================

Generates independent four-voice contrapuntal lines with:
- Movement rules (contrary, oblique, parallel)
- VL-SM integration (APVL, TRAM, SISM)
- Voice independence and interaction
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random

try:
    from .instruments import InstrumentType, QuartetInstruments
    from .inputs import QuartetConfig, MotionType
except ImportError:
    from instruments import InstrumentType, QuartetInstruments
    from inputs import QuartetConfig, MotionType


class MotionRelation(Enum):
    """Types of motion between voices."""
    CONTRARY = "contrary"
    OBLIQUE = "oblique"
    PARALLEL = "parallel"
    SIMILAR = "similar"


@dataclass
class VoiceNote:
    """
    A single note in a voice line.
    
    Attributes:
        pitch: MIDI pitch
        duration: Duration in beats
        bar: Bar number
        beat: Beat position
        articulation: Optional articulation
        dynamic: Optional dynamic marking
    """
    pitch: int
    duration: float
    bar: int
    beat: float
    articulation: Optional[str] = None
    dynamic: Optional[str] = None
    
    @property
    def pitch_class(self) -> int:
        return self.pitch % 12


@dataclass
class VoiceLine:
    """
    A complete voice line for one instrument.
    
    Attributes:
        instrument: The instrument
        notes: List of notes
        contour: Contour description
    """
    instrument: InstrumentType
    notes: List[VoiceNote]
    contour: str = "neutral"
    
    def get_pitches(self) -> List[int]:
        return [n.pitch for n in self.notes]
    
    def get_range(self) -> Tuple[int, int]:
        pitches = self.get_pitches()
        return (min(pitches), max(pitches)) if pitches else (60, 60)
    
    def total_duration(self) -> float:
        return sum(n.duration for n in self.notes)


@dataclass
class CounterpointMoment:
    """
    A vertical slice of all four voices at one moment.
    
    Attributes:
        bar: Bar number
        beat: Beat position
        pitches: Dict mapping instrument to pitch
        motion_analysis: Analysis of motion from previous moment
    """
    bar: int
    beat: float
    pitches: Dict[InstrumentType, int]
    motion_analysis: str = ""


class CounterpointEngine:
    """
    Generates contrapuntal voice lines for string quartet.
    """
    
    MIDI_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # Scale patterns
    SCALE_PATTERNS = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    }
    
    # Interval classifications
    CONSONANT = [0, 3, 4, 7, 8, 9, 12]  # P1, m3, M3, P5, m6, M6, P8
    DISSONANT = [1, 2, 5, 6, 10, 11]     # m2, M2, P4, tritone, m7, M7
    
    def __init__(
        self,
        config: QuartetConfig,
        seed: Optional[int] = None
    ):
        """
        Initialize the counterpoint engine.
        
        Args:
            config: Quartet configuration
            seed: Random seed for reproducibility
        """
        self.config = config
        self.key = config.key
        self.scale = config.scale
        self.motion_type = config.motion_type
        
        if seed is not None:
            random.seed(seed)
        
        self.key_midi = self._get_key_midi()
        self.scale_notes = self._build_scale()
    
    def _get_key_midi(self) -> int:
        """Get MIDI pitch class for key."""
        note_to_midi = {
            "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
            "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
            "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
        }
        return note_to_midi.get(self.key, 0)
    
    def _build_scale(self) -> List[int]:
        """Build scale pitch classes."""
        pattern = self.SCALE_PATTERNS.get(self.scale, self.SCALE_PATTERNS["major"])
        return [(self.key_midi + interval) % 12 for interval in pattern]
    
    def _is_scale_tone(self, pitch: int) -> bool:
        """Check if pitch is a scale tone."""
        return (pitch % 12) in self.scale_notes
    
    def _get_nearest_scale_tone(self, pitch: int, direction: int = 0) -> int:
        """Get nearest scale tone to a pitch."""
        pc = pitch % 12
        
        if pc in self.scale_notes:
            return pitch
        
        # Search up and down
        for offset in range(1, 7):
            if direction >= 0 and ((pc + offset) % 12) in self.scale_notes:
                return pitch + offset
            if direction <= 0 and ((pc - offset) % 12) in self.scale_notes:
                return pitch - offset
        
        return pitch
    
    def _analyze_motion(
        self,
        prev_pitches: Dict[InstrumentType, int],
        curr_pitches: Dict[InstrumentType, int]
    ) -> Dict[Tuple[InstrumentType, InstrumentType], MotionRelation]:
        """
        Analyze motion between two moments for all voice pairs.
        """
        motions = {}
        instruments = list(prev_pitches.keys())
        
        for i, inst1 in enumerate(instruments):
            for inst2 in instruments[i + 1:]:
                if inst1 in prev_pitches and inst1 in curr_pitches:
                    if inst2 in prev_pitches and inst2 in curr_pitches:
                        motion1 = curr_pitches[inst1] - prev_pitches[inst1]
                        motion2 = curr_pitches[inst2] - prev_pitches[inst2]
                        
                        if motion1 == 0 and motion2 == 0:
                            relation = MotionRelation.OBLIQUE
                        elif motion1 == 0 or motion2 == 0:
                            relation = MotionRelation.OBLIQUE
                        elif (motion1 > 0 and motion2 < 0) or (motion1 < 0 and motion2 > 0):
                            relation = MotionRelation.CONTRARY
                        elif motion1 == motion2:
                            relation = MotionRelation.PARALLEL
                        else:
                            relation = MotionRelation.SIMILAR
                        
                        motions[(inst1, inst2)] = relation
        
        return motions
    
    def _check_parallel_fifths_octaves(
        self,
        prev_pitches: Dict[InstrumentType, int],
        curr_pitches: Dict[InstrumentType, int]
    ) -> List[str]:
        """Check for parallel fifths and octaves."""
        issues = []
        instruments = list(prev_pitches.keys())
        
        for i, inst1 in enumerate(instruments):
            for inst2 in instruments[i + 1:]:
                if all(inst in prev_pitches and inst in curr_pitches 
                       for inst in [inst1, inst2]):
                    
                    prev_interval = abs(prev_pitches[inst1] - prev_pitches[inst2]) % 12
                    curr_interval = abs(curr_pitches[inst1] - curr_pitches[inst2]) % 12
                    
                    prev_motion = curr_pitches[inst1] - prev_pitches[inst1]
                    
                    # Parallel fifths
                    if prev_interval == 7 and curr_interval == 7 and prev_motion != 0:
                        issues.append(f"Parallel 5ths: {inst1.value}-{inst2.value}")
                    
                    # Parallel octaves
                    if prev_interval == 0 and curr_interval == 0 and prev_motion != 0:
                        issues.append(f"Parallel 8ves: {inst1.value}-{inst2.value}")
        
        return issues
    
    def generate_line(
        self,
        instrument: InstrumentType,
        bars: int,
        start_pitch: int,
        contour: str = "wave",
        beats_per_bar: int = 4
    ) -> VoiceLine:
        """
        Generate a single voice line.
        
        Args:
            instrument: Target instrument
            bars: Number of bars
            start_pitch: Starting pitch
            contour: Contour type (ascending, descending, wave, static)
            beats_per_bar: Time signature beats
        
        Returns:
            VoiceLine
        """
        inst_def = QuartetInstruments.get_by_type(instrument)
        notes = []
        
        current_pitch = self._get_nearest_scale_tone(start_pitch)
        current_beat = 1.0
        
        for bar in range(1, bars + 1):
            # Generate notes for this bar
            bar_beats = 0.0
            
            while bar_beats < beats_per_bar:
                # Determine note duration
                remaining = beats_per_bar - bar_beats
                duration = min(random.choice([0.5, 1.0, 1.5, 2.0]), remaining)
                
                # Determine pitch movement based on contour
                if contour == "ascending":
                    direction = random.choice([1, 1, 1, 0])
                elif contour == "descending":
                    direction = random.choice([-1, -1, -1, 0])
                elif contour == "static":
                    direction = 0
                else:  # wave
                    direction = random.choice([-1, 0, 1])
                
                # Calculate step size
                step = direction * random.choice([1, 2, 3])
                
                # Apply step
                new_pitch = current_pitch + step
                
                # Constrain to scale
                new_pitch = self._get_nearest_scale_tone(new_pitch, direction)
                
                # Constrain to instrument range
                new_pitch = max(inst_def.range.low, 
                               min(inst_def.range.high, new_pitch))
                
                # Check leap safety
                if not inst_def.is_leap_safe(new_pitch - current_pitch):
                    # Reduce the leap
                    if new_pitch > current_pitch:
                        new_pitch = current_pitch + inst_def.constraints.max_safe_leap
                    else:
                        new_pitch = current_pitch - inst_def.constraints.max_safe_leap
                    new_pitch = self._get_nearest_scale_tone(new_pitch)
                
                notes.append(VoiceNote(
                    pitch=new_pitch,
                    duration=duration,
                    bar=bar,
                    beat=current_beat
                ))
                
                current_pitch = new_pitch
                bar_beats += duration
                current_beat += duration
                
                if current_beat > beats_per_bar:
                    current_beat = 1.0
            
            current_beat = 1.0
        
        return VoiceLine(
            instrument=instrument,
            notes=notes,
            contour=contour
        )
    
    def generate_four_voices(
        self,
        bars: int,
        start_chord: List[int] = None,
        prefer_contrary: bool = True
    ) -> Dict[InstrumentType, VoiceLine]:
        """
        Generate all four voices with contrapuntal interaction.
        
        Args:
            bars: Number of bars
            start_chord: Starting pitches [cello, viola, vln2, vln1]
            prefer_contrary: Prefer contrary motion
        
        Returns:
            Dict of instrument to VoiceLine
        """
        # Default starting chord
        if start_chord is None:
            root = self.key_midi + 48  # C3
            start_chord = [
                root,           # Cello
                root + 7,       # Viola (5th)
                root + 12,      # Vln II (octave)
                root + 16,      # Vln I (major 3rd above)
            ]
        
        # Generate lines with complementary contours
        contours = {
            InstrumentType.VIOLIN_I: "wave",
            InstrumentType.VIOLIN_II: "descending" if prefer_contrary else "wave",
            InstrumentType.VIOLA: "ascending" if prefer_contrary else "wave",
            InstrumentType.CELLO: "static" if self.motion_type == MotionType.STATIC_PEDAL else "wave",
        }
        
        voices = {}
        for i, inst in enumerate([InstrumentType.CELLO, InstrumentType.VIOLA,
                                   InstrumentType.VIOLIN_II, InstrumentType.VIOLIN_I]):
            voices[inst] = self.generate_line(
                instrument=inst,
                bars=bars,
                start_pitch=start_chord[i],
                contour=contours[inst]
            )
        
        # Post-process to avoid parallel 5ths/8ves
        if prefer_contrary:
            voices = self._fix_parallels(voices)
        
        return voices
    
    def _fix_parallels(
        self,
        voices: Dict[InstrumentType, VoiceLine]
    ) -> Dict[InstrumentType, VoiceLine]:
        """
        Attempt to fix parallel 5ths and octaves.
        """
        # Get all moments
        instruments = list(voices.keys())
        max_notes = max(len(v.notes) for v in voices.values())
        
        for i in range(1, max_notes):
            prev_pitches = {}
            curr_pitches = {}
            
            for inst in instruments:
                if i - 1 < len(voices[inst].notes):
                    prev_pitches[inst] = voices[inst].notes[i - 1].pitch
                if i < len(voices[inst].notes):
                    curr_pitches[inst] = voices[inst].notes[i].pitch
            
            issues = self._check_parallel_fifths_octaves(prev_pitches, curr_pitches)
            
            if issues:
                # Try to fix by adjusting inner voices
                for inst in [InstrumentType.VIOLIN_II, InstrumentType.VIOLA]:
                    if inst in curr_pitches and i < len(voices[inst].notes):
                        # Shift by a step
                        voices[inst].notes[i].pitch += random.choice([-1, 1, 2])
                        voices[inst].notes[i].pitch = self._get_nearest_scale_tone(
                            voices[inst].notes[i].pitch
                        )
        
        return voices
    
    def apply_vl_sm(
        self,
        voices: Dict[InstrumentType, VoiceLine],
        mode: str = "functional"
    ) -> Dict[InstrumentType, VoiceLine]:
        """
        Apply VL-SM (Voice-Leading Smart Module) principles.
        
        Args:
            voices: Voice lines to process
            mode: VL-SM mode (functional, modal, intervallic)
        
        Returns:
            Processed voice lines
        """
        if mode == "functional":
            # APVL: Preserve axis (common tones)
            # TRAM: Tension expansion → release contraction
            return self._apply_functional_vl(voices)
        elif mode == "modal":
            # Emphasize color tones
            return self._apply_modal_vl(voices)
        elif mode == "intervallic":
            # SISM: Wide spacing for tension
            return self._apply_intervallic_vl(voices)
        
        return voices
    
    def _apply_functional_vl(
        self,
        voices: Dict[InstrumentType, VoiceLine]
    ) -> Dict[InstrumentType, VoiceLine]:
        """Apply functional voice-leading (APVL, TRAM)."""
        # Ensure smooth outer voice motion
        for inst in [InstrumentType.VIOLIN_I, InstrumentType.CELLO]:
            if inst in voices:
                line = voices[inst]
                for i in range(1, len(line.notes)):
                    leap = abs(line.notes[i].pitch - line.notes[i-1].pitch)
                    if leap > 4:  # Larger than major 3rd
                        # Smooth it
                        direction = 1 if line.notes[i].pitch > line.notes[i-1].pitch else -1
                        line.notes[i].pitch = line.notes[i-1].pitch + (direction * 2)
                        line.notes[i].pitch = self._get_nearest_scale_tone(line.notes[i].pitch)
        
        return voices
    
    def _apply_modal_vl(
        self,
        voices: Dict[InstrumentType, VoiceLine]
    ) -> Dict[InstrumentType, VoiceLine]:
        """Apply modal voice-leading."""
        # Add characteristic scale tones
        return voices
    
    def _apply_intervallic_vl(
        self,
        voices: Dict[InstrumentType, VoiceLine]
    ) -> Dict[InstrumentType, VoiceLine]:
        """Apply intervallic voice-leading (SISM spacing)."""
        # Widen spacing for tension
        if InstrumentType.VIOLIN_I in voices:
            for note in voices[InstrumentType.VIOLIN_I].notes:
                note.pitch += 2  # Shift up for wider spacing
        
        return voices
    
    def generate_canon(
        self,
        leader: InstrumentType,
        followers: List[InstrumentType],
        bars: int,
        offset_bars: int = 1,
        interval: int = 0
    ) -> Dict[InstrumentType, VoiceLine]:
        """
        Generate a canon pattern.
        
        Args:
            leader: Lead voice instrument
            followers: Following voices
            bars: Number of bars
            offset_bars: Bar offset for canon entry
            interval: Transposition interval for followers
        
        Returns:
            Dict of voice lines
        """
        # Generate leader
        leader_def = QuartetInstruments.get_by_type(leader)
        start_pitch = (leader_def.range.low + leader_def.range.high) // 2
        
        leader_line = self.generate_line(
            instrument=leader,
            bars=bars + (offset_bars * len(followers)),
            start_pitch=start_pitch,
            contour="wave"
        )
        
        voices = {leader: leader_line}
        
        # Generate followers as transposed/offset copies
        for i, follower in enumerate(followers):
            follower_def = QuartetInstruments.get_by_type(follower)
            offset_beats = (i + 1) * offset_bars * self.config.time_signature[0]
            
            follower_notes = []
            for j, note in enumerate(leader_line.notes):
                if note.bar > offset_bars * (i + 1):
                    transposed_pitch = note.pitch + interval - (12 * (i + 1))
                    
                    # Fit to register
                    while transposed_pitch < follower_def.range.low:
                        transposed_pitch += 12
                    while transposed_pitch > follower_def.range.high:
                        transposed_pitch -= 12
                    
                    follower_notes.append(VoiceNote(
                        pitch=transposed_pitch,
                        duration=note.duration,
                        bar=note.bar - offset_bars * (i + 1),
                        beat=note.beat
                    ))
            
            voices[follower] = VoiceLine(
                instrument=follower,
                notes=follower_notes,
                contour="canon"
            )
        
        return voices

