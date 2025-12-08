"""
Voice Expansion Module for Orchestral Engine
=============================================

Expands open triads into 4-8 instrument voicings.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

from .inputs import OrchestraConfig, Density, OrchestrationProfile, RegisterProfile
from .instruments import InstrumentType, ORCHESTRA_INSTRUMENTS, OrchestraInstruments


@dataclass
class VoiceAssignment:
    """Assignment of a pitch to an instrument."""
    instrument: InstrumentType
    pitch: int
    duration: float
    role: str  # "melody", "harmony", "bass", "doubling", "counterpoint"
    dynamic: str = "mf"


@dataclass 
class OrchestraVoicing:
    """A complete orchestral voicing for one moment."""
    bar: int
    beat: float
    assignments: List[VoiceAssignment]
    chord_symbol: Optional[str] = None
    analysis: str = ""


class VoiceExpander:
    """
    Expands open triads into full orchestral voicings.
    """
    
    # Instrument groupings for different profiles
    BRIGHT_INSTRUMENTS = [
        InstrumentType.FLUTE, InstrumentType.VIOLIN_I, InstrumentType.VIOLIN_II,
        InstrumentType.FLUGELHORN
    ]
    
    WARM_INSTRUMENTS = [
        InstrumentType.CLARINET, InstrumentType.VIOLA, InstrumentType.VIOLIN_II,
        InstrumentType.FLUGELHORN, InstrumentType.CELLO
    ]
    
    DARK_INSTRUMENTS = [
        InstrumentType.CLARINET, InstrumentType.VIOLA, InstrumentType.CELLO,
        InstrumentType.BASS, InstrumentType.PIANO
    ]
    
    TRANSPARENT_INSTRUMENTS = [
        InstrumentType.FLUTE, InstrumentType.VIOLIN_I, InstrumentType.PIANO
    ]
    
    def __init__(self, config: OrchestraConfig):
        """Initialize the voice expander."""
        self.config = config
    
    def get_active_instruments(self) -> List[InstrumentType]:
        """Get active instruments based on profile and density."""
        profile = self.config.orchestration_profile
        density = self.config.density
        
        # Start with profile-based instruments
        if profile == OrchestrationProfile.BRIGHT:
            base = list(self.BRIGHT_INSTRUMENTS)
        elif profile == OrchestrationProfile.WARM:
            base = list(self.WARM_INSTRUMENTS)
        elif profile == OrchestrationProfile.DARK:
            base = list(self.DARK_INSTRUMENTS)
        else:  # TRANSPARENT
            base = list(self.TRANSPARENT_INSTRUMENTS)
        
        # Add core instruments
        if InstrumentType.CELLO not in base:
            base.append(InstrumentType.CELLO)
        if InstrumentType.BASS not in base:
            base.append(InstrumentType.BASS)
        
        # Adjust for density
        if density == Density.SPARSE:
            # Remove some instruments
            return base[:4]
        elif density == Density.DENSE:
            # Add all instruments
            return list(InstrumentType)
        else:  # MEDIUM
            return base
    
    def expand_triad(
        self,
        triad: List[int],
        bar: int,
        beat: float,
        duration: float,
        chord_symbol: str = ""
    ) -> OrchestraVoicing:
        """
        Expand a triad into full orchestral voicing.
        
        Args:
            triad: List of 3 MIDI pitches (root, third, fifth)
            bar: Bar number
            beat: Beat position
            duration: Duration in beats
            chord_symbol: Chord symbol
        
        Returns:
            OrchestraVoicing with all assignments
        """
        assignments = []
        active = self.get_active_instruments()
        
        if len(triad) < 3:
            return OrchestraVoicing(bar=bar, beat=beat, assignments=[], chord_symbol=chord_symbol)
        
        root, third, fifth = triad[0], triad[1], triad[2]
        
        # Register adjustment based on profile
        register_offset = 0
        if self.config.register_profile == RegisterProfile.HIGH:
            register_offset = 12
        elif self.config.register_profile == RegisterProfile.LOW:
            register_offset = -12
        
        # Assign bass
        if InstrumentType.BASS in active:
            bass_pitch = OrchestraInstruments.clamp_to_range(InstrumentType.BASS, root - 24)
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.BASS,
                pitch=bass_pitch,
                duration=duration,
                role="bass"
            ))
        
        # Assign cello
        if InstrumentType.CELLO in active:
            cello_pitch = OrchestraInstruments.clamp_to_range(InstrumentType.CELLO, root - 12)
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.CELLO,
                pitch=cello_pitch,
                duration=duration,
                role="harmony"
            ))
        
        # Assign viola
        if InstrumentType.VIOLA in active:
            viola_pitch = OrchestraInstruments.clamp_to_range(InstrumentType.VIOLA, third)
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLA,
                pitch=viola_pitch,
                duration=duration,
                role="harmony"
            ))
        
        # Assign violin II
        if InstrumentType.VIOLIN_II in active:
            v2_pitch = OrchestraInstruments.clamp_to_range(InstrumentType.VIOLIN_II, fifth + register_offset)
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLIN_II,
                pitch=v2_pitch,
                duration=duration,
                role="harmony"
            ))
        
        # Assign violin I (top voice)
        if InstrumentType.VIOLIN_I in active:
            v1_pitch = OrchestraInstruments.clamp_to_range(
                InstrumentType.VIOLIN_I, 
                root + 12 + register_offset
            )
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.VIOLIN_I,
                pitch=v1_pitch,
                duration=duration,
                role="melody"
            ))
        
        # Assign winds (color tones)
        if InstrumentType.FLUTE in active:
            flute_pitch = OrchestraInstruments.clamp_to_range(
                InstrumentType.FLUTE,
                fifth + 12 + register_offset
            )
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.FLUTE,
                pitch=flute_pitch,
                duration=duration,
                role="harmony"
            ))
        
        if InstrumentType.CLARINET in active:
            clar_pitch = OrchestraInstruments.clamp_to_range(
                InstrumentType.CLARINET,
                third + register_offset
            )
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.CLARINET,
                pitch=clar_pitch,
                duration=duration,
                role="harmony"
            ))
        
        if InstrumentType.FLUGELHORN in active:
            flugel_pitch = OrchestraInstruments.clamp_to_range(
                InstrumentType.FLUGELHORN,
                fifth + register_offset
            )
            assignments.append(VoiceAssignment(
                instrument=InstrumentType.FLUGELHORN,
                pitch=flugel_pitch,
                duration=duration,
                role="harmony"
            ))
        
        # Piano (optional reinforcement)
        if InstrumentType.PIANO in active and self.config.density != Density.SPARSE:
            # Piano plays chord in comfortable range
            piano_pitches = [root - 12, third, fifth]
            for i, p in enumerate(piano_pitches):
                assignments.append(VoiceAssignment(
                    instrument=InstrumentType.PIANO,
                    pitch=p,
                    duration=duration,
                    role="harmony" if i > 0 else "bass"
                ))
        
        analysis = f"Triad expanded to {len(assignments)} voices, profile: {self.config.orchestration_profile.value}"
        
        return OrchestraVoicing(
            bar=bar,
            beat=beat,
            assignments=assignments,
            chord_symbol=chord_symbol,
            analysis=analysis
        )
    
    def expand_with_doubling(
        self,
        triad: List[int],
        bar: int,
        beat: float,
        duration: float,
        doubling_rules: Dict[InstrumentType, InstrumentType] = None
    ) -> OrchestraVoicing:
        """
        Expand triad with specific doubling rules.
        
        Args:
            triad: Triad pitches
            bar: Bar number
            beat: Beat position
            duration: Duration
            doubling_rules: Dict mapping source instrument to doubling instrument
        
        Returns:
            OrchestraVoicing
        """
        voicing = self.expand_triad(triad, bar, beat, duration)
        
        if doubling_rules:
            new_assignments = []
            for assign in voicing.assignments:
                new_assignments.append(assign)
                if assign.instrument in doubling_rules:
                    doubling_inst = doubling_rules[assign.instrument]
                    doubled_pitch = OrchestraInstruments.clamp_to_range(
                        doubling_inst, 
                        assign.pitch
                    )
                    new_assignments.append(VoiceAssignment(
                        instrument=doubling_inst,
                        pitch=doubled_pitch,
                        duration=assign.duration,
                        role="doubling"
                    ))
            voicing.assignments = new_assignments
        
        return voicing

