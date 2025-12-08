"""
Texture Generator for Quartet Engine
======================================

Implements multiple quartet texture modes:
- Homophonic
- Contrapuntal
- Hybrid
- Harmonic Field
- Rhythmic Cell-Based
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

try:
    from .instruments import InstrumentType, QuartetInstruments
    from .inputs import QuartetConfig, QuartetMode, TextureDensity
    from .voice_assignment import VoiceDistribution, VoiceAssignment, VoiceAssigner
    from .counterpoint import CounterpointEngine, VoiceLine
except ImportError:
    from instruments import InstrumentType, QuartetInstruments
    from inputs import QuartetConfig, QuartetMode, TextureDensity
    from voice_assignment import VoiceDistribution, VoiceAssignment, VoiceAssigner
    from counterpoint import CounterpointEngine, VoiceLine


@dataclass
class QuartetMoment:
    """
    A vertical slice of the quartet at one moment.
    
    Attributes:
        bar: Bar number
        beat: Beat position
        voices: Dict mapping instrument to (pitch, duration)
        articulation: Shared articulation
        dynamic: Dynamic marking
    """
    bar: int
    beat: float
    voices: Dict[InstrumentType, Tuple[int, float]]
    articulation: Optional[str] = None
    dynamic: Optional[str] = None


@dataclass
class QuartetTexture:
    """
    A complete textural passage for quartet.
    
    Attributes:
        moments: List of QuartetMoment objects
        texture_type: Type of texture
        bars: Number of bars
        analysis: Textural analysis
    """
    moments: List[QuartetMoment]
    texture_type: QuartetMode
    bars: int
    analysis: str = ""
    
    def get_voice_line(self, instrument: InstrumentType) -> List[Tuple[int, int, float, float]]:
        """Extract a voice line as (bar, beat, pitch, duration) tuples."""
        line = []
        for m in self.moments:
            if instrument in m.voices:
                pitch, duration = m.voices[instrument]
                line.append((m.bar, m.beat, pitch, duration))
        return line


class TextureGenerator:
    """
    Generates various quartet textures.
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
        "aug": [0, 4, 8],
    }
    
    def __init__(self, config: QuartetConfig):
        """
        Initialize the texture generator.
        
        Args:
            config: Quartet configuration
        """
        self.config = config
        self.voice_assigner = VoiceAssigner(config)
        self.counterpoint = CounterpointEngine(config)
        
        self.key_midi = self.NOTE_TO_MIDI.get(config.key, 0)
        self.scale_pattern = self.SCALE_PATTERNS.get(config.scale, self.SCALE_PATTERNS["major"])
    
    def _build_triad(self, root_pc: int, quality: str = "major", octave: int = 4) -> List[int]:
        """Build triad pitches."""
        root_midi = root_pc + (octave + 1) * 12
        intervals = self.TRIAD_INTERVALS.get(quality, self.TRIAD_INTERVALS["major"])
        return [root_midi + i for i in intervals]
    
    def _get_scale_degree_triad(self, degree: int) -> Tuple[int, str]:
        """Get triad root and quality for a scale degree."""
        root_pc = (self.key_midi + self.scale_pattern[degree % 7]) % 12
        
        # Determine quality based on scale degree (major scale)
        major_qualities = ["major", "minor", "minor", "major", "major", "minor", "dim"]
        quality = major_qualities[degree % 7]
        
        return root_pc, quality
    
    def generate_homophonic(
        self,
        bars: int,
        triads_per_bar: int = 1
    ) -> QuartetTexture:
        """
        Generate homophonic texture - all instruments align harmonically.
        
        Args:
            bars: Number of bars
            triads_per_bar: Triads per bar (1, 2, or 4)
        
        Returns:
            QuartetTexture
        """
        moments = []
        beats_per_bar = self.config.time_signature[0]
        duration = beats_per_bar / triads_per_bar
        
        for bar in range(1, bars + 1):
            for triad_idx in range(triads_per_bar):
                beat = 1.0 + (triad_idx * duration)
                
                # Choose triad (cycle through scale degrees)
                degree = ((bar - 1) * triads_per_bar + triad_idx) % 7
                root_pc, quality = self._get_scale_degree_triad(degree)
                
                # Build triad
                triad_pitches = self._build_triad(root_pc, quality, octave=4)
                
                # Distribute across quartet
                distribution = self.voice_assigner.assign_classic_trio(
                    triad_pitches,
                    bass_pitch=triad_pitches[0] - 12,
                    bar=bar,
                    beat=beat
                )
                
                # Create moment
                voices = {}
                for a in distribution.assignments:
                    voices[a.instrument] = (a.pitch, duration)
                
                moments.append(QuartetMoment(
                    bar=bar,
                    beat=beat,
                    voices=voices
                ))
        
        return QuartetTexture(
            moments=moments,
            texture_type=QuartetMode.HOMOPHONIC,
            bars=bars,
            analysis=f"Homophonic texture with {triads_per_bar} chord(s) per bar"
        )
    
    def generate_contrapuntal(
        self,
        bars: int
    ) -> QuartetTexture:
        """
        Generate contrapuntal texture - independent voices with triad targets.
        
        Args:
            bars: Number of bars
        
        Returns:
            QuartetTexture
        """
        # Generate independent voice lines
        voice_lines = self.counterpoint.generate_four_voices(
            bars=bars,
            prefer_contrary=True
        )
        
        # Apply VL-SM
        voice_lines = self.counterpoint.apply_vl_sm(
            voice_lines,
            mode=self.config.motion_type.value
        )
        
        # Convert to moments
        moments = []
        
        # Find the maximum note count
        max_notes = max(len(vl.notes) for vl in voice_lines.values())
        
        for i in range(max_notes):
            voices = {}
            bar = 1
            beat = 1.0
            
            for inst, line in voice_lines.items():
                if i < len(line.notes):
                    note = line.notes[i]
                    voices[inst] = (note.pitch, note.duration)
                    bar = note.bar
                    beat = note.beat
            
            if voices:
                moments.append(QuartetMoment(
                    bar=bar,
                    beat=beat,
                    voices=voices
                ))
        
        return QuartetTexture(
            moments=moments,
            texture_type=QuartetMode.CONTRAPUNTAL,
            bars=bars,
            analysis="Contrapuntal texture with independent voice motion"
        )
    
    def generate_hybrid(
        self,
        bars: int,
        melody_instrument: InstrumentType = InstrumentType.VIOLIN_I
    ) -> QuartetTexture:
        """
        Generate hybrid texture - melody + harmony + inner counterlines.
        
        Args:
            bars: Number of bars
            melody_instrument: Which instrument carries melody
        
        Returns:
            QuartetTexture
        """
        moments = []
        beats_per_bar = self.config.time_signature[0]
        
        # Generate melody line
        melody_def = QuartetInstruments.get_by_type(melody_instrument)
        melody_start = (melody_def.range.low + melody_def.range.high) // 2
        
        melody_line = self.counterpoint.generate_line(
            instrument=melody_instrument,
            bars=bars,
            start_pitch=melody_start,
            contour="wave"
        )
        
        # For each melody note, create harmony
        for note in melody_line.notes:
            # Find a triad containing the melody note
            melody_pc = note.pitch % 12
            
            # Try to harmonize with a scale-degree triad
            best_degree = 0
            for degree in range(7):
                root_pc, quality = self._get_scale_degree_triad(degree)
                triad_pcs = [(root_pc + i) % 12 for i in self.TRIAD_INTERVALS[quality]]
                if melody_pc in triad_pcs:
                    best_degree = degree
                    break
            
            root_pc, quality = self._get_scale_degree_triad(best_degree)
            triad_pitches = self._build_triad(root_pc, quality, octave=3)
            
            # Assign voices
            voices = {}
            voices[melody_instrument] = (note.pitch, note.duration)
            
            # Other voices get harmony
            other_instruments = [
                InstrumentType.VIOLIN_II,
                InstrumentType.VIOLA,
                InstrumentType.CELLO
            ]
            
            if melody_instrument != InstrumentType.VIOLIN_I:
                other_instruments.insert(0, InstrumentType.VIOLIN_I)
                other_instruments.remove(melody_instrument)
            
            for i, inst in enumerate(other_instruments):
                if i < len(triad_pitches):
                    pitch = triad_pitches[len(triad_pitches) - 1 - i]
                    
                    # Adjust to register
                    inst_def = QuartetInstruments.get_by_type(inst)
                    while pitch < inst_def.range.low:
                        pitch += 12
                    while pitch > inst_def.range.high:
                        pitch -= 12
                    
                    voices[inst] = (pitch, note.duration)
            
            moments.append(QuartetMoment(
                bar=note.bar,
                beat=note.beat,
                voices=voices
            ))
        
        return QuartetTexture(
            moments=moments,
            texture_type=QuartetMode.HYBRID,
            bars=bars,
            analysis=f"Hybrid texture with melody in {melody_instrument.value}"
        )
    
    def generate_harmonic_field(
        self,
        bars: int,
        root_pc: int = None
    ) -> QuartetTexture:
        """
        Generate harmonic field texture - rotating triads for atmosphere.
        
        Args:
            bars: Number of bars
            root_pc: Root pitch class (uses key if None)
        
        Returns:
            QuartetTexture
        """
        moments = []
        root_pc = root_pc if root_pc is not None else self.key_midi
        beats_per_bar = self.config.time_signature[0]
        
        # Create a pool of related triads
        triad_pool = []
        for degree in [0, 2, 4, 5]:  # I, iii, V, vi
            deg_root, quality = self._get_scale_degree_triad(degree)
            triad_pool.append((deg_root, quality))
        
        for bar in range(1, bars + 1):
            for beat_offset in range(0, beats_per_bar, 2):
                beat = 1.0 + beat_offset
                
                # Rotate through triads
                triad_idx = ((bar - 1) * (beats_per_bar // 2) + beat_offset // 2) % len(triad_pool)
                triad_root, quality = triad_pool[triad_idx]
                triad_pitches = self._build_triad(triad_root, quality, octave=4)
                
                # Use rotating distribution
                rotation = (bar - 1) % 4
                distribution = self.voice_assigner.assign_rotating(
                    triad_pitches,
                    rotation=rotation,
                    bar=bar,
                    beat=beat
                )
                
                voices = {}
                for a in distribution.assignments:
                    voices[a.instrument] = (a.pitch, 2.0)
                
                moments.append(QuartetMoment(
                    bar=bar,
                    beat=beat,
                    voices=voices,
                    dynamic="pp" if self.config.texture_density == TextureDensity.SPARSE else "mp"
                ))
        
        return QuartetTexture(
            moments=moments,
            texture_type=QuartetMode.HARMONIC_FIELD,
            bars=bars,
            analysis="Harmonic field texture with rotating open triads"
        )
    
    def generate_rhythmic_cells(
        self,
        bars: int
    ) -> QuartetTexture:
        """
        Generate rhythmic cell-based texture.
        
        Ostinatos in Cello/Viola, syncopated punctuations in violins.
        
        Args:
            bars: Number of bars
        
        Returns:
            QuartetTexture
        """
        moments = []
        beats_per_bar = self.config.time_signature[0]
        
        # Cello ostinato pattern (root pedal)
        cello_def = QuartetInstruments.get_by_type(InstrumentType.CELLO)
        cello_pitch = self.key_midi + 36  # Low root
        
        # Viola pattern (5th)
        viola_pitch = cello_pitch + 7 + 12  # Fifth, octave up
        
        for bar in range(1, bars + 1):
            # Cello: steady quarter notes
            for beat_offset in range(beats_per_bar):
                beat = 1.0 + beat_offset
                
                moments.append(QuartetMoment(
                    bar=bar,
                    beat=beat,
                    voices={
                        InstrumentType.CELLO: (cello_pitch, 1.0),
                    }
                ))
            
            # Viola: syncopated pattern (off beats)
            for beat_offset in [0.5, 2.5]:
                if beat_offset < beats_per_bar:
                    moments.append(QuartetMoment(
                        bar=bar,
                        beat=1.0 + beat_offset,
                        voices={
                            InstrumentType.VIOLA: (viola_pitch, 0.5),
                        }
                    ))
            
            # Violins: punctuating chords on beats 1 and 3
            for beat_offset in [0, 2]:
                if beat_offset < beats_per_bar:
                    degree = (bar - 1 + beat_offset // 2) % 7
                    root_pc, quality = self._get_scale_degree_triad(degree)
                    triad = self._build_triad(root_pc, quality, octave=4)
                    
                    moments.append(QuartetMoment(
                        bar=bar,
                        beat=1.0 + beat_offset,
                        voices={
                            InstrumentType.VIOLIN_I: (triad[2], 0.5),
                            InstrumentType.VIOLIN_II: (triad[1], 0.5),
                        },
                        articulation="staccato"
                    ))
        
        # Sort moments by bar and beat
        moments.sort(key=lambda m: (m.bar, m.beat))
        
        return QuartetTexture(
            moments=moments,
            texture_type=QuartetMode.RHYTHMIC_CELLS,
            bars=bars,
            analysis="Rhythmic cell texture with ostinato and syncopation"
        )
    
    def generate_texture(
        self,
        bars: int = None,
        mode: QuartetMode = None
    ) -> QuartetTexture:
        """
        Generate texture based on configuration.
        
        Args:
            bars: Number of bars (uses config if None)
            mode: Texture mode (uses config if None)
        
        Returns:
            QuartetTexture
        """
        bars = bars or self.config.length
        mode = mode or self.config.quartet_mode
        
        if mode == QuartetMode.HOMOPHONIC:
            return self.generate_homophonic(bars)
        elif mode == QuartetMode.CONTRAPUNTAL:
            return self.generate_contrapuntal(bars)
        elif mode == QuartetMode.HYBRID:
            return self.generate_hybrid(bars)
        elif mode == QuartetMode.HARMONIC_FIELD:
            return self.generate_harmonic_field(bars)
        elif mode == QuartetMode.RHYTHMIC_CELLS:
            return self.generate_rhythmic_cells(bars)
        else:
            return self.generate_homophonic(bars)

