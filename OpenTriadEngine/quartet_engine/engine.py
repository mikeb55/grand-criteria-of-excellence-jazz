"""
Main Quartet Engine
====================

The primary interface for generating string quartet music using
open triads from the Open Triad Engine v1.0.
"""

from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

try:
    from .inputs import (
        QuartetConfig, QuartetMode, TextureDensity, MotionType,
        PatternType, RegisterProfile, RhythmicStyle
    )
    from .instruments import InstrumentType, QuartetInstruments
    from .voice_assignment import VoiceAssigner, VoiceDistribution
    from .counterpoint import CounterpointEngine, VoiceLine
    from .textures import TextureGenerator, QuartetTexture
    from .patterns import PatternEngine, QuartetPattern
    from .rhythm import RhythmEngine, QuartetRhythm
    from .output import QuartetOutput, QuartetScore
except ImportError:
    from inputs import (
        QuartetConfig, QuartetMode, TextureDensity, MotionType,
        PatternType, RegisterProfile, RhythmicStyle
    )
    from instruments import InstrumentType, QuartetInstruments
    from voice_assignment import VoiceAssigner, VoiceDistribution
    from counterpoint import CounterpointEngine, VoiceLine
    from textures import TextureGenerator, QuartetTexture
    from patterns import PatternEngine, QuartetPattern
    from rhythm import RhythmEngine, QuartetRhythm
    from output import QuartetOutput, QuartetScore


class QuartetEngine:
    """
    Main engine for generating string quartet music.
    
    Integrates with Open Triad Engine v1.0 for:
    - Open-triad voicing generation
    - Inversion logic
    - VL-SM voice-leading modes
    - Scale mapping
    
    Example:
        >>> engine = QuartetEngine(key="C", scale="major")
        >>> texture = engine.generate(bars=8, mode="homophonic")
        >>> engine.export(texture, "output/quartet")
    """
    
    def __init__(
        self,
        key: str = "C",
        scale: str = "major",
        progression: Optional[List[str]] = None,
        quartet_mode: str = "homophonic",
        texture_density: str = "medium",
        motion_type: str = "modal",
        register_profile: str = "standard",
        rhythmic_style: str = "straight",
        tempo: int = 80,
        time_signature: Tuple[int, int] = (4, 4),
        seed: Optional[int] = None
    ):
        """
        Initialize the Quartet Engine.
        
        Args:
            key: Musical key
            scale: Scale type
            progression: Optional chord progression
            quartet_mode: Writing mode
            texture_density: Texture density
            motion_type: Harmonic motion type
            register_profile: Register profile
            rhythmic_style: Rhythmic style
            tempo: Tempo in BPM
            time_signature: Time signature
            seed: Random seed
        """
        self.config = QuartetConfig(
            key=key,
            scale=scale,
            progression=progression,
            quartet_mode=quartet_mode,
            texture_density=texture_density,
            motion_type=motion_type,
            register_profile=register_profile,
            rhythmic_style=rhythmic_style,
            tempo=tempo,
            time_signature=time_signature
        )
        
        self.seed = seed
        
        # Initialize components
        self.voice_assigner = VoiceAssigner(self.config)
        self.counterpoint = CounterpointEngine(self.config, seed=seed)
        self.texture_gen = TextureGenerator(self.config)
        self.pattern_gen = PatternEngine(self.config, seed=seed)
        self.rhythm_gen = RhythmEngine(self.config, seed=seed)
        self.output = QuartetOutput(self.config)
    
    # =========================================================================
    # TEXTURE GENERATION
    # =========================================================================
    
    def generate(
        self,
        bars: int = None,
        mode: QuartetMode = None
    ) -> QuartetTexture:
        """
        Generate quartet texture.
        
        Args:
            bars: Number of bars
            mode: Texture mode
        
        Returns:
            QuartetTexture
        """
        bars = bars or self.config.length
        mode = mode or self.config.quartet_mode
        
        if isinstance(mode, str):
            mode = QuartetMode(mode)
        
        return self.texture_gen.generate_texture(bars, mode)
    
    def generate_homophonic(self, bars: int = 8) -> QuartetTexture:
        """Generate homophonic texture."""
        return self.texture_gen.generate_homophonic(bars)
    
    def generate_contrapuntal(self, bars: int = 8) -> QuartetTexture:
        """Generate contrapuntal texture."""
        return self.texture_gen.generate_contrapuntal(bars)
    
    def generate_hybrid(
        self,
        bars: int = 8,
        melody_instrument: InstrumentType = InstrumentType.VIOLIN_I
    ) -> QuartetTexture:
        """Generate hybrid texture."""
        return self.texture_gen.generate_hybrid(bars, melody_instrument)
    
    def generate_harmonic_field(self, bars: int = 8) -> QuartetTexture:
        """Generate harmonic field texture."""
        return self.texture_gen.generate_harmonic_field(bars)
    
    def generate_rhythmic_cells(self, bars: int = 8) -> QuartetTexture:
        """Generate rhythmic cell texture."""
        return self.texture_gen.generate_rhythmic_cells(bars)
    
    # =========================================================================
    # PATTERN GENERATION
    # =========================================================================
    
    def generate_pattern(
        self,
        bars: int = None,
        pattern_type: PatternType = None
    ) -> QuartetPattern:
        """
        Generate quartet pattern.
        
        Args:
            bars: Number of bars
            pattern_type: Pattern type
        
        Returns:
            QuartetPattern
        """
        return self.pattern_gen.generate_pattern(bars, pattern_type)
    
    def generate_inversion_sweep(self, bars: int = 8) -> QuartetPattern:
        """Generate inversion sweep pattern."""
        return self.pattern_gen.generate_inversion_sweep(bars)
    
    def generate_triad_pair_gesture(
        self,
        bars: int = 8,
        pair: Tuple[Tuple[int, str], Tuple[int, str]] = None
    ) -> QuartetPattern:
        """Generate triad-pair gesture."""
        return self.pattern_gen.generate_triad_pair_gesture(bars, pair)
    
    def generate_staggered_entrance(
        self,
        bars: int = 8,
        offset_beats: float = 1.0
    ) -> QuartetPattern:
        """Generate staggered entrance pattern."""
        return self.pattern_gen.generate_staggered_entrance(bars, offset_beats)
    
    def generate_hocket(self, bars: int = 8) -> QuartetPattern:
        """Generate hocket pattern."""
        return self.pattern_gen.generate_hocket(bars)
    
    # =========================================================================
    # COUNTERPOINT GENERATION
    # =========================================================================
    
    def generate_counterpoint(
        self,
        bars: int = 8,
        prefer_contrary: bool = True
    ) -> Dict[InstrumentType, VoiceLine]:
        """
        Generate four independent contrapuntal voices.
        
        Args:
            bars: Number of bars
            prefer_contrary: Prefer contrary motion
        
        Returns:
            Dict of instrument to VoiceLine
        """
        voices = self.counterpoint.generate_four_voices(bars, prefer_contrary=prefer_contrary)
        return self.counterpoint.apply_vl_sm(voices, self.config.motion_type.value)
    
    def generate_canon(
        self,
        bars: int = 8,
        offset_bars: int = 1
    ) -> Dict[InstrumentType, VoiceLine]:
        """Generate a canon pattern."""
        return self.counterpoint.generate_canon(
            leader=InstrumentType.VIOLIN_I,
            followers=[InstrumentType.VIOLIN_II, InstrumentType.VIOLA, InstrumentType.CELLO],
            bars=bars,
            offset_bars=offset_bars
        )
    
    # =========================================================================
    # RHYTHM GENERATION
    # =========================================================================
    
    def generate_rhythm(
        self,
        bars: int = None,
        style: RhythmicStyle = None
    ) -> QuartetRhythm:
        """
        Generate rhythmic pattern.
        
        Args:
            bars: Number of bars
            style: Rhythmic style
        
        Returns:
            QuartetRhythm
        """
        return self.rhythm_gen.generate_rhythm(bars, style)
    
    # =========================================================================
    # OUTPUT
    # =========================================================================
    
    def to_score(
        self,
        texture: QuartetTexture,
        title: str = "Quartet",
        composer: str = "Quartet Engine"
    ) -> QuartetScore:
        """
        Convert texture to score.
        
        Args:
            texture: QuartetTexture object
            title: Score title
            composer: Composer name
        
        Returns:
            QuartetScore
        """
        return self.output.texture_to_score(texture, title, composer)
    
    def to_json(self, score: QuartetScore) -> Dict:
        """Convert score to JSON."""
        return self.output.to_json(score)
    
    def to_musicxml(self, score: QuartetScore) -> str:
        """Convert score to MusicXML."""
        return self.output.to_musicxml(score)
    
    def export(
        self,
        texture: QuartetTexture,
        output_path: str,
        title: str = "Quartet",
        formats: List[str] = None
    ) -> Dict[str, str]:
        """
        Export texture to files.
        
        Args:
            texture: QuartetTexture to export
            output_path: Base output path
            title: Score title
            formats: List of formats (json, musicxml, html)
        
        Returns:
            Dict of format -> filepath
        """
        score = self.to_score(texture, title)
        output_dir = Path(output_path).parent
        base_name = Path(output_path).stem
        
        return self.output.export_all(score, str(output_dir), base_name)
    
    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    
    def reconfigure(self, **kwargs):
        """Update configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Reinitialize components
        self.voice_assigner = VoiceAssigner(self.config)
        self.texture_gen = TextureGenerator(self.config)
        self.counterpoint = CounterpointEngine(self.config, seed=self.seed)
        self.pattern_gen = PatternEngine(self.config, seed=self.seed)
        self.rhythm_gen = RhythmEngine(self.config, seed=self.seed)
        self.output = QuartetOutput(self.config)
    
    def get_config(self) -> Dict:
        """Get current configuration."""
        return self.config.to_dict()
    
    # =========================================================================
    # DEMO METHODS
    # =========================================================================
    
    def demo_homophonic_c_major(self, bars: int = 8) -> QuartetTexture:
        """Demo: C major homophonic progression."""
        self.reconfigure(key="C", scale="major", quartet_mode="homophonic")
        return self.generate_homophonic(bars)
    
    def demo_functional_ii_v_i(self, bars: int = 4) -> QuartetTexture:
        """Demo: Functional ii-V-I in G major."""
        self.reconfigure(
            key="G", scale="major",
            quartet_mode="homophonic",
            motion_type="functional"
        )
        return self.generate_homophonic(bars)
    
    def demo_modal_dorian(self, bars: int = 6) -> QuartetTexture:
        """Demo: D Dorian modal texture."""
        self.reconfigure(
            key="D", scale="dorian",
            quartet_mode="harmonic_field",
            motion_type="modal"
        )
        return self.generate_harmonic_field(bars)
    
    def demo_contrapuntal_a_minor(self, bars: int = 4) -> QuartetTexture:
        """Demo: A minor counterpoint."""
        self.reconfigure(
            key="A", scale="minor",
            quartet_mode="contrapuntal",
            motion_type="intervallic"
        )
        return self.generate_contrapuntal(bars)
    
    def demo_hybrid_harmonic_minor(self, bars: int = 8) -> QuartetTexture:
        """Demo: A harmonic minor hybrid texture."""
        self.reconfigure(
            key="A", scale="harmonic_minor",
            quartet_mode="hybrid"
        )
        return self.generate_hybrid(bars)

