"""
Texture Module for Orchestral Engine
=====================================

Implements orchestral texture modes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random

from .inputs import OrchestraConfig, TextureMode, Density, MotionType, RegisterProfile
from .instruments import InstrumentType, ORCHESTRA_INSTRUMENTS, OrchestraInstruments
from .voice_expansion import VoiceExpander, OrchestraVoicing, VoiceAssignment


@dataclass
class OrchestraMoment:
    """Single moment in orchestral texture."""
    bar: int
    beat: float
    voices: Dict[InstrumentType, tuple]  # (pitch, duration)
    articulation: str = None
    dynamic: str = "mf"


@dataclass
class OrchestraTexture:
    """Complete orchestral texture."""
    moments: List[OrchestraMoment] = field(default_factory=list)
    texture_type: TextureMode = TextureMode.HOMOPHONIC
    bars: int = 8
    analysis: str = ""


# Scale definitions (MIDI intervals from root)
SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
}

KEY_TO_MIDI = {
    "C": 60, "C#": 61, "Db": 61, "D": 62, "D#": 63, "Eb": 63,
    "E": 64, "F": 65, "F#": 66, "Gb": 66, "G": 67, "G#": 68,
    "Ab": 68, "A": 69, "A#": 70, "Bb": 70, "B": 71
}


class TextureGenerator:
    """
    Generates orchestral textures in various modes.
    """
    
    def __init__(self, config: OrchestraConfig, seed: int = None):
        """Initialize the texture generator."""
        self.config = config
        self.expander = VoiceExpander(config)
        self.rng = random.Random(seed)
        
        # Get root note MIDI value
        self.root = KEY_TO_MIDI.get(config.key, 60)
        self.scale_intervals = SCALE_INTERVALS.get(config.scale, SCALE_INTERVALS["major"])
    
    def get_scale_notes(self, octave_offset: int = 0) -> List[int]:
        """Get scale notes with octave offset."""
        base = self.root + (octave_offset * 12)
        return [base + interval for interval in self.scale_intervals]
    
    def build_triad(self, scale_degree: int) -> List[int]:
        """Build triad on scale degree."""
        scale = self.get_scale_notes()
        
        root = scale[scale_degree % len(scale)]
        third = scale[(scale_degree + 2) % len(scale)]
        fifth = scale[(scale_degree + 4) % len(scale)]
        
        # Ensure proper stacking
        while third < root:
            third += 12
        while fifth < third:
            fifth += 12
        
        return [root, third, fifth]
    
    def generate_texture(
        self,
        bars: int = None,
        mode: TextureMode = None
    ) -> OrchestraTexture:
        """Generate orchestral texture."""
        bars = bars or self.config.length
        mode = mode or self.config.texture_mode
        
        if mode == TextureMode.HOMOPHONIC:
            return self.generate_homophonic(bars)
        elif mode == TextureMode.CONTRAPUNTAL:
            return self.generate_contrapuntal(bars)
        elif mode == TextureMode.HYBRID:
            return self.generate_hybrid(bars)
        elif mode == TextureMode.HARMONIC_FIELD:
            return self.generate_harmonic_field(bars)
        elif mode == TextureMode.OSTINATO:
            return self.generate_ostinato(bars)
        else:
            return self.generate_orchestral_pads(bars)
    
    def generate_homophonic(self, bars: int = 8) -> OrchestraTexture:
        """Generate homophonic (block chord) texture."""
        moments = []
        beats_per_bar = self.config.time_signature[0]
        
        for bar in range(1, bars + 1):
            # Choose scale degree
            degree = (bar - 1) % len(self.scale_intervals)
            triad = self.build_triad(degree)
            
            # Expand to orchestra
            voicing = self.expander.expand_triad(
                triad, bar, 1.0, float(beats_per_bar),
                chord_symbol=f"{self.config.key} degree {degree + 1}"
            )
            
            # Convert to moment
            voices = {}
            for assign in voicing.assignments:
                voices[assign.instrument] = (assign.pitch, assign.duration)
            
            moments.append(OrchestraMoment(
                bar=bar,
                beat=1.0,
                voices=voices,
                dynamic="mf"
            ))
        
        return OrchestraTexture(
            moments=moments,
            texture_type=TextureMode.HOMOPHONIC,
            bars=bars,
            analysis=f"Homophonic texture with {len(moments)} block chords"
        )
    
    def generate_contrapuntal(self, bars: int = 8) -> OrchestraTexture:
        """Generate contrapuntal texture with independent lines."""
        moments = []
        beats_per_bar = self.config.time_signature[0]
        scale = self.get_scale_notes()
        
        # Define voice starting pitches
        voice_starts = {
            InstrumentType.FLUTE: scale[4] + 12,
            InstrumentType.VIOLIN_I: scale[4] + 12,
            InstrumentType.CLARINET: scale[2],
            InstrumentType.VIOLIN_II: scale[2],
            InstrumentType.VIOLA: scale[0],
            InstrumentType.CELLO: scale[0] - 12,
            InstrumentType.BASS: scale[0] - 24,
        }
        
        current_pitches = dict(voice_starts)
        
        for bar in range(1, bars + 1):
            # Multiple moments per bar for counterpoint
            for beat in range(1, beats_per_bar + 1):
                voices = {}
                
                for inst, pitch in current_pitches.items():
                    # Move each voice independently
                    motion = self.rng.choice([-2, -1, 0, 1, 2])
                    new_pitch = pitch + motion
                    
                    # Clamp to range
                    new_pitch = OrchestraInstruments.clamp_to_range(inst, new_pitch)
                    current_pitches[inst] = new_pitch
                    
                    voices[inst] = (new_pitch, 1.0)
                
                moments.append(OrchestraMoment(
                    bar=bar,
                    beat=float(beat),
                    voices=voices
                ))
        
        return OrchestraTexture(
            moments=moments,
            texture_type=TextureMode.CONTRAPUNTAL,
            bars=bars,
            analysis=f"Contrapuntal texture with {len(current_pitches)} independent voices"
        )
    
    def generate_hybrid(self, bars: int = 8) -> OrchestraTexture:
        """Generate hybrid texture (melody + harmony + bass)."""
        moments = []
        beats_per_bar = self.config.time_signature[0]
        scale = self.get_scale_notes()
        
        melody_line = []
        melody_pitch = scale[4] + 12  # Start on 5th degree
        
        for bar in range(1, bars + 1):
            # Melody rhythm
            for beat_idx, beat in enumerate(range(1, beats_per_bar + 1)):
                voices = {}
                
                # Flute carries melody
                if beat_idx % 2 == 0:  # Change melody every 2 beats
                    motion = self.rng.choice([-2, -1, 1, 2])
                    melody_pitch = OrchestraInstruments.clamp_to_range(
                        InstrumentType.FLUTE,
                        melody_pitch + motion
                    )
                
                voices[InstrumentType.FLUTE] = (melody_pitch, 1.0)
                
                # Inner voices (counter-motion)
                degree = (bar - 1) % len(self.scale_intervals)
                triad = self.build_triad(degree)
                
                voices[InstrumentType.CLARINET] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.CLARINET, triad[1]),
                    1.0
                )
                voices[InstrumentType.VIOLIN_II] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.VIOLIN_II, triad[2]),
                    1.0
                )
                voices[InstrumentType.VIOLA] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.VIOLA, triad[0]),
                    1.0
                )
                
                # Violin I harmonic extensions
                voices[InstrumentType.VIOLIN_I] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.VIOLIN_I, triad[2] + 12),
                    1.0
                )
                
                # Cello stepwise bass
                cello_pitch = triad[0] - 12
                voices[InstrumentType.CELLO] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.CELLO, cello_pitch),
                    1.0
                )
                
                # Bass pedal
                voices[InstrumentType.BASS] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.BASS, scale[0] - 24),
                    float(beats_per_bar)
                )
                
                # Piano comping
                if beat == 1 or beat == 3:
                    voices[InstrumentType.PIANO] = (triad[0], 2.0)
                
                moments.append(OrchestraMoment(
                    bar=bar,
                    beat=float(beat),
                    voices=voices
                ))
        
        return OrchestraTexture(
            moments=moments,
            texture_type=TextureMode.HYBRID,
            bars=bars,
            analysis="Hybrid texture: Flute melody, inner countermotion, cello bass"
        )
    
    def generate_harmonic_field(self, bars: int = 8) -> OrchestraTexture:
        """Generate harmonic field with rotating open triads."""
        moments = []
        beats_per_bar = self.config.time_signature[0]
        
        for bar in range(1, bars + 1):
            # Rotate through triads
            for beat_idx in range(2):  # Two chords per bar
                degree = ((bar - 1) * 2 + beat_idx) % len(self.scale_intervals)
                triad = self.build_triad(degree)
                beat = 1.0 + beat_idx * 2
                
                voices = {}
                
                # Winds carry color tones
                voices[InstrumentType.FLUTE] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.FLUTE, triad[2] + 12),
                    2.0
                )
                voices[InstrumentType.CLARINET] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.CLARINET, triad[1]),
                    2.0
                )
                
                # Strings provide pads
                voices[InstrumentType.VIOLIN_I] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.VIOLIN_I, triad[2]),
                    2.0
                )
                voices[InstrumentType.VIOLIN_II] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.VIOLIN_II, triad[1]),
                    2.0
                )
                voices[InstrumentType.VIOLA] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.VIOLA, triad[0]),
                    2.0
                )
                voices[InstrumentType.CELLO] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.CELLO, triad[0] - 12),
                    2.0
                )
                voices[InstrumentType.BASS] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.BASS, triad[0] - 24),
                    2.0
                )
                
                # Piano reinforcement
                voices[InstrumentType.PIANO] = (triad[0] - 12, 2.0)
                
                moments.append(OrchestraMoment(
                    bar=bar,
                    beat=beat,
                    voices=voices
                ))
        
        return OrchestraTexture(
            moments=moments,
            texture_type=TextureMode.HARMONIC_FIELD,
            bars=bars,
            analysis="Harmonic field: rotating open-triad loops with wind colors"
        )
    
    def generate_ostinato(self, bars: int = 8) -> OrchestraTexture:
        """Generate ostinato pattern with pads and punctuations."""
        moments = []
        beats_per_bar = self.config.time_signature[0]
        scale = self.get_scale_notes()
        
        # Ostinato pattern (3:2 polyrhythm)
        ostinato_pattern = [0, 2, 4]  # Scale degrees
        
        for bar in range(1, bars + 1):
            degree = (bar - 1) % len(self.scale_intervals)
            triad = self.build_triad(degree)
            
            # Cello + Bass ostinato
            for ost_idx, beat in enumerate([1.0, 2.33, 3.67]):
                if beat <= beats_per_bar:
                    ost_degree = ostinato_pattern[ost_idx % len(ostinato_pattern)]
                    ost_pitch = scale[ost_degree] - 12
                    
                    voices = {}
                    voices[InstrumentType.CELLO] = (
                        OrchestraInstruments.clamp_to_range(InstrumentType.CELLO, ost_pitch),
                        0.67
                    )
                    voices[InstrumentType.BASS] = (
                        OrchestraInstruments.clamp_to_range(InstrumentType.BASS, ost_pitch - 12),
                        0.67
                    )
                    
                    moments.append(OrchestraMoment(bar=bar, beat=beat, voices=voices))
            
            # String pads (whole bar)
            pad_voices = {}
            pad_voices[InstrumentType.VIOLIN_I] = (
                OrchestraInstruments.clamp_to_range(InstrumentType.VIOLIN_I, triad[2] + 12),
                float(beats_per_bar)
            )
            pad_voices[InstrumentType.VIOLIN_II] = (
                OrchestraInstruments.clamp_to_range(InstrumentType.VIOLIN_II, triad[1]),
                float(beats_per_bar)
            )
            pad_voices[InstrumentType.VIOLA] = (
                OrchestraInstruments.clamp_to_range(InstrumentType.VIOLA, triad[0]),
                float(beats_per_bar)
            )
            
            moments.append(OrchestraMoment(bar=bar, beat=1.0, voices=pad_voices))
            
            # Wind punctuations (sparse)
            if bar % 2 == 1:
                wind_voices = {}
                wind_voices[InstrumentType.FLUTE] = (
                    OrchestraInstruments.clamp_to_range(InstrumentType.FLUTE, triad[2] + 12),
                    1.0
                )
                moments.append(OrchestraMoment(bar=bar, beat=1.0, voices=wind_voices))
        
        return OrchestraTexture(
            moments=moments,
            texture_type=TextureMode.OSTINATO,
            bars=bars,
            analysis="Ostinato texture: cello/bass 3:2 pattern, string pads, wind punctuations"
        )
    
    def generate_orchestral_pads(self, bars: int = 8) -> OrchestraTexture:
        """Generate sustained orchestral pads."""
        moments = []
        beats_per_bar = self.config.time_signature[0]
        
        for bar in range(1, bars + 1):
            degree = (bar - 1) % len(self.scale_intervals)
            triad = self.build_triad(degree)
            
            voices = {}
            
            # All strings sustain
            voices[InstrumentType.VIOLIN_I] = (
                OrchestraInstruments.clamp_to_range(InstrumentType.VIOLIN_I, triad[2] + 12),
                float(beats_per_bar)
            )
            voices[InstrumentType.VIOLIN_II] = (
                OrchestraInstruments.clamp_to_range(InstrumentType.VIOLIN_II, triad[1] + 12),
                float(beats_per_bar)
            )
            voices[InstrumentType.VIOLA] = (
                OrchestraInstruments.clamp_to_range(InstrumentType.VIOLA, triad[0]),
                float(beats_per_bar)
            )
            voices[InstrumentType.CELLO] = (
                OrchestraInstruments.clamp_to_range(InstrumentType.CELLO, triad[0] - 12),
                float(beats_per_bar)
            )
            voices[InstrumentType.BASS] = (
                OrchestraInstruments.clamp_to_range(InstrumentType.BASS, triad[0] - 24),
                float(beats_per_bar)
            )
            
            # Winds sustain softly
            voices[InstrumentType.FLUTE] = (
                OrchestraInstruments.clamp_to_range(InstrumentType.FLUTE, triad[2]),
                float(beats_per_bar)
            )
            voices[InstrumentType.CLARINET] = (
                OrchestraInstruments.clamp_to_range(InstrumentType.CLARINET, triad[1]),
                float(beats_per_bar)
            )
            
            moments.append(OrchestraMoment(
                bar=bar,
                beat=1.0,
                voices=voices,
                dynamic="p"
            ))
        
        return OrchestraTexture(
            moments=moments,
            texture_type=TextureMode.ORCHESTRAL_PADS,
            bars=bars,
            analysis="Orchestral pads: sustained strings and winds"
        )

