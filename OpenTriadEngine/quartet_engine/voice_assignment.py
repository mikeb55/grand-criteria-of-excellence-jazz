"""
Voice Assignment Module for Quartet Engine
============================================

Distributes open-triad voices across the quartet instruments.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

try:
    from .instruments import InstrumentType, QuartetInstruments, Instrument
    from .inputs import QuartetConfig, RegisterProfile
except ImportError:
    from instruments import InstrumentType, QuartetInstruments, Instrument
    from inputs import QuartetConfig, RegisterProfile


class VoiceDistributionMode(Enum):
    """Modes for distributing triad voices."""
    CLASSIC_TRIO = "classic_trio"      # Violins + Viola = triad, Cello = bass
    ROTATING = "rotating"               # Rotate voices across instruments
    EXPANDED = "expanded"               # Add 4th voice (7th, 9th, pedal)
    DOUBLED = "doubled"                 # Double one voice


@dataclass
class VoiceAssignment:
    """
    A single voice assignment for an instrument.
    
    Attributes:
        instrument: Target instrument
        pitch: MIDI pitch
        voice_role: Role in the voicing (top, middle, bottom, bass, extension)
        source_triad_voice: Which triad voice this came from (1=root, 2=3rd, 3=5th)
        is_doubled: Whether this is a doubling
    """
    instrument: InstrumentType
    pitch: int
    voice_role: str
    source_triad_voice: int = 0
    is_doubled: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "instrument": self.instrument.value,
            "pitch": self.pitch,
            "voice_role": self.voice_role,
            "source_triad_voice": self.source_triad_voice,
            "is_doubled": self.is_doubled
        }


@dataclass
class VoiceDistribution:
    """
    Complete voice distribution for a quartet moment.
    
    Attributes:
        assignments: List of voice assignments
        chord_symbol: Optional chord symbol
        bar: Bar number
        beat: Beat position
        analysis: Analysis of the distribution
    """
    assignments: List[VoiceAssignment]
    chord_symbol: Optional[str] = None
    bar: int = 1
    beat: float = 1.0
    analysis: str = ""
    
    def get_pitch_for_instrument(
        self, 
        instrument: InstrumentType
    ) -> Optional[int]:
        """Get the pitch assigned to an instrument."""
        for a in self.assignments:
            if a.instrument == instrument:
                return a.pitch
        return None
    
    def get_all_pitches(self) -> Dict[InstrumentType, int]:
        """Get all pitches as a dictionary."""
        return {a.instrument: a.pitch for a in self.assignments}
    
    def to_dict(self) -> Dict:
        return {
            "assignments": [a.to_dict() for a in self.assignments],
            "chord_symbol": self.chord_symbol,
            "bar": self.bar,
            "beat": self.beat,
            "analysis": self.analysis
        }


class VoiceAssigner:
    """
    Assigns open-triad voices to quartet instruments.
    """
    
    MIDI_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    def __init__(self, config: QuartetConfig):
        """
        Initialize the voice assigner.
        
        Args:
            config: Quartet configuration
        """
        self.config = config
        self.instruments = QuartetInstruments.get_all()
        self.register_ranges = QuartetInstruments.get_register_adjusted_ranges(
            config.register_profile.value
        )
    
    def _midi_to_name(self, midi: int) -> str:
        """Convert MIDI to note name."""
        octave = (midi // 12) - 1
        note = self.MIDI_TO_NOTE[midi % 12]
        return f"{note}{octave}"
    
    def _adjust_to_register(
        self,
        pitch: int,
        instrument: InstrumentType
    ) -> int:
        """Adjust a pitch to fit instrument register."""
        low, high = self.register_ranges[instrument]
        
        while pitch < low:
            pitch += 12
        while pitch > high:
            pitch -= 12
        
        return pitch
    
    def assign_classic_trio(
        self,
        triad_pitches: List[int],
        bass_pitch: Optional[int] = None,
        bar: int = 1,
        beat: float = 1.0,
        chord_symbol: str = None
    ) -> VoiceDistribution:
        """
        Assign using classic trio + cello bass pattern.
        
        Violin I: top voice
        Violin II: middle voice
        Viola: lower middle (or 3rd if triad)
        Cello: bass/pedal
        
        Args:
            triad_pitches: Open triad pitches [low, mid, high]
            bass_pitch: Optional bass pitch for cello
            bar: Bar number
            beat: Beat position
            chord_symbol: Optional chord symbol
        
        Returns:
            VoiceDistribution
        """
        assignments = []
        
        # Sort pitches from low to high
        sorted_pitches = sorted(triad_pitches)
        
        if len(sorted_pitches) >= 3:
            # Violin I gets highest
            vln1_pitch = self._adjust_to_register(
                sorted_pitches[2], InstrumentType.VIOLIN_I
            )
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLIN_I,
                pitch=vln1_pitch,
                voice_role="top",
                source_triad_voice=3
            ))
            
            # Violin II gets middle
            vln2_pitch = self._adjust_to_register(
                sorted_pitches[1], InstrumentType.VIOLIN_II
            )
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLIN_II,
                pitch=vln2_pitch,
                voice_role="middle",
                source_triad_voice=2
            ))
            
            # Viola gets lowest triad pitch
            vla_pitch = self._adjust_to_register(
                sorted_pitches[0], InstrumentType.VIOLA
            )
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLA,
                pitch=vla_pitch,
                voice_role="lower_middle",
                source_triad_voice=1
            ))
        elif len(sorted_pitches) == 2:
            # Two notes - distribute to Vln I and II
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLIN_I,
                pitch=self._adjust_to_register(sorted_pitches[1], InstrumentType.VIOLIN_I),
                voice_role="top",
                source_triad_voice=2
            ))
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLIN_II,
                pitch=self._adjust_to_register(sorted_pitches[0], InstrumentType.VIOLIN_II),
                voice_role="middle",
                source_triad_voice=1
            ))
        
        # Cello gets bass
        if bass_pitch is not None:
            cello_pitch = self._adjust_to_register(
                bass_pitch, InstrumentType.CELLO
            )
        else:
            # Use lowest triad pitch, down an octave
            cello_pitch = self._adjust_to_register(
                sorted_pitches[0] - 12 if sorted_pitches else 48,
                InstrumentType.CELLO
            )
        
        assignments.append(VoiceAssignment(
            instrument=InstrumentType.CELLO,
            pitch=cello_pitch,
            voice_role="bass",
            source_triad_voice=0
        ))
        
        return VoiceDistribution(
            assignments=assignments,
            chord_symbol=chord_symbol,
            bar=bar,
            beat=beat,
            analysis="Classic trio + bass distribution"
        )
    
    def assign_rotating(
        self,
        triad_pitches: List[int],
        rotation: int = 0,
        bar: int = 1,
        beat: float = 1.0,
        chord_symbol: str = None
    ) -> VoiceDistribution:
        """
        Assign using rotating voicing system.
        
        Rotates which instrument gets which triad voice
        to create timbral variation.
        
        Args:
            triad_pitches: Open triad pitches
            rotation: Rotation amount (0, 1, 2, 3)
            bar: Bar number
            beat: Beat position
            chord_symbol: Optional chord symbol
        
        Returns:
            VoiceDistribution
        """
        assignments = []
        sorted_pitches = sorted(triad_pitches, reverse=True)
        
        # Rotation patterns
        rotation_patterns = [
            [InstrumentType.VIOLIN_I, InstrumentType.VIOLIN_II, InstrumentType.VIOLA, InstrumentType.CELLO],
            [InstrumentType.VIOLIN_II, InstrumentType.VIOLA, InstrumentType.CELLO, InstrumentType.VIOLIN_I],
            [InstrumentType.VIOLA, InstrumentType.CELLO, InstrumentType.VIOLIN_I, InstrumentType.VIOLIN_II],
            [InstrumentType.CELLO, InstrumentType.VIOLIN_I, InstrumentType.VIOLIN_II, InstrumentType.VIOLA],
        ]
        
        pattern = rotation_patterns[rotation % 4]
        voice_roles = ["top", "middle", "lower_middle", "bass"]
        
        for i, (inst, role) in enumerate(zip(pattern, voice_roles)):
            if i < len(sorted_pitches):
                pitch = sorted_pitches[i]
            else:
                # Double the bass or create pedal
                pitch = sorted_pitches[-1] - 12 if sorted_pitches else 48
            
            adjusted_pitch = self._adjust_to_register(pitch, inst)
            
            assignments.append(VoiceAssignment(
                instrument=inst,
                pitch=adjusted_pitch,
                voice_role=role,
                source_triad_voice=i + 1 if i < len(sorted_pitches) else 0
            ))
        
        return VoiceDistribution(
            assignments=assignments,
            chord_symbol=chord_symbol,
            bar=bar,
            beat=beat,
            analysis=f"Rotating distribution (rotation {rotation})"
        )
    
    def assign_expanded(
        self,
        triad_pitches: List[int],
        extension_pitch: Optional[int] = None,
        bar: int = 1,
        beat: float = 1.0,
        chord_symbol: str = None
    ) -> VoiceDistribution:
        """
        Assign using expanded 4-voice voicing.
        
        Adds a fourth voice (7th, 9th, or pedal tone).
        
        Args:
            triad_pitches: Open triad pitches
            extension_pitch: Optional extension (7th, 9th, etc.)
            bar: Bar number
            beat: Beat position
            chord_symbol: Optional chord symbol
        
        Returns:
            VoiceDistribution
        """
        assignments = []
        sorted_pitches = sorted(triad_pitches, reverse=True)
        
        # Violin I: highest pitch
        if sorted_pitches:
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLIN_I,
                pitch=self._adjust_to_register(sorted_pitches[0], InstrumentType.VIOLIN_I),
                voice_role="top",
                source_triad_voice=3
            ))
        
        # Violin II: extension or second highest
        if extension_pitch:
            vln2_pitch = self._adjust_to_register(extension_pitch, InstrumentType.VIOLIN_II)
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLIN_II,
                pitch=vln2_pitch,
                voice_role="extension",
                source_triad_voice=0
            ))
        elif len(sorted_pitches) > 1:
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLIN_II,
                pitch=self._adjust_to_register(sorted_pitches[1], InstrumentType.VIOLIN_II),
                voice_role="middle",
                source_triad_voice=2
            ))
        
        # Viola: middle/lower
        if len(sorted_pitches) > 2:
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLA,
                pitch=self._adjust_to_register(sorted_pitches[2], InstrumentType.VIOLA),
                voice_role="lower_middle",
                source_triad_voice=1
            ))
        elif len(sorted_pitches) > 1:
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLA,
                pitch=self._adjust_to_register(sorted_pitches[-1], InstrumentType.VIOLA),
                voice_role="lower_middle",
                source_triad_voice=1
            ))
        
        # Cello: bass
        bass = sorted_pitches[-1] - 12 if sorted_pitches else 48
        assignments.append(VoiceAssignment(
            instrument=InstrumentType.CELLO,
            pitch=self._adjust_to_register(bass, InstrumentType.CELLO),
            voice_role="bass",
            source_triad_voice=0
        ))
        
        return VoiceDistribution(
            assignments=assignments,
            chord_symbol=chord_symbol,
            bar=bar,
            beat=beat,
            analysis="Expanded 4-voice distribution"
        )
    
    def check_voice_crossing(
        self,
        distribution: VoiceDistribution
    ) -> Tuple[bool, List[str]]:
        """
        Check for voice crossing in a distribution.
        
        Returns:
            Tuple of (has_crossing, list of crossings)
        """
        pitches = distribution.get_all_pitches()
        return QuartetInstruments.validate_voicing(pitches)
    
    def fix_voice_crossing(
        self,
        distribution: VoiceDistribution
    ) -> VoiceDistribution:
        """
        Attempt to fix voice crossing by octave displacement.
        
        Args:
            distribution: Distribution to fix
        
        Returns:
            Fixed VoiceDistribution
        """
        # Get current assignments sorted by expected register
        instrument_order = [
            InstrumentType.VIOLIN_I,
            InstrumentType.VIOLIN_II,
            InstrumentType.VIOLA,
            InstrumentType.CELLO
        ]
        
        pitches = {}
        for a in distribution.assignments:
            pitches[a.instrument] = a.pitch
        
        # Ensure pitches descend from Vln I to Cello
        fixed = []
        prev_pitch = float('inf')
        
        for inst in instrument_order:
            if inst in pitches:
                pitch = pitches[inst]
                
                # Adjust if crossing
                while pitch >= prev_pitch and pitch > 36:
                    pitch -= 12
                
                # Find original assignment
                for a in distribution.assignments:
                    if a.instrument == inst:
                        fixed.append(VoiceAssignment(
                            instrument=inst,
                            pitch=pitch,
                            voice_role=a.voice_role,
                            source_triad_voice=a.source_triad_voice,
                            is_doubled=a.is_doubled
                        ))
                        prev_pitch = pitch
                        break
        
        return VoiceDistribution(
            assignments=fixed,
            chord_symbol=distribution.chord_symbol,
            bar=distribution.bar,
            beat=distribution.beat,
            analysis=distribution.analysis + " (voice crossing fixed)"
        )

