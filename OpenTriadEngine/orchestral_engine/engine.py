"""
Main Orchestral Engine
=======================

The primary interface for generating small orchestra music using
open triads from the Open Triad Engine v1.0.
"""

from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

from .inputs import (
    OrchestraConfig, TextureMode, Density, MotionType,
    OrchestrationProfile, RegisterProfile, RhythmicStyle
)
from .instruments import InstrumentType, OrchestraInstruments, ORCHESTRA_INSTRUMENTS
from .voice_expansion import VoiceExpander, OrchestraVoicing
from .textures import TextureGenerator, OrchestraTexture
from .output import OrchestraOutput, OrchestraScore


class OrchestralEngine:
    """
    Main engine for generating small orchestra music.
    
    Instruments: Flute, Clarinet, Flugelhorn, Violins I/II, Viola, Cello, Bass, Piano
    
    Example:
        >>> engine = OrchestralEngine(key="C", scale="major")
        >>> texture = engine.generate(bars=8, mode="homophonic")
        >>> engine.export(texture, "output/orchestra")
    """
    
    def __init__(
        self,
        key: str = "C",
        scale: str = "major",
        progression: Optional[List[str]] = None,
        texture_mode: str = "homophonic",
        density: str = "medium",
        motion_type: str = "modal",
        orchestration_profile: str = "warm",
        register_profile: str = "mixed",
        rhythmic_style: str = "straight",
        tempo: int = 80,
        time_signature: Tuple[int, int] = (4, 4),
        seed: Optional[int] = None
    ):
        """
        Initialize the Orchestral Engine.
        
        Args:
            key: Musical key
            scale: Scale type
            progression: Optional chord progression
            texture_mode: Writing mode
            density: Orchestral density
            motion_type: Harmonic motion type
            orchestration_profile: Timbral profile
            register_profile: Register profile
            rhythmic_style: Rhythmic style
            tempo: Tempo in BPM
            time_signature: Time signature
            seed: Random seed
        """
        self.config = OrchestraConfig(
            key=key,
            scale=scale,
            progression=progression,
            texture_mode=texture_mode,
            density=density,
            motion_type=motion_type,
            orchestration_profile=orchestration_profile,
            register_profile=register_profile,
            rhythmic_style=rhythmic_style,
            tempo=tempo,
            time_signature=time_signature
        )
        
        self.seed = seed
        
        # Initialize components
        self.expander = VoiceExpander(self.config)
        self.texture_gen = TextureGenerator(self.config, seed=seed)
        self.output = OrchestraOutput(self.config)
    
    # =========================================================================
    # TEXTURE GENERATION
    # =========================================================================
    
    def generate(
        self,
        bars: int = None,
        mode: TextureMode = None
    ) -> OrchestraTexture:
        """
        Generate orchestral texture.
        
        Args:
            bars: Number of bars
            mode: Texture mode
        
        Returns:
            OrchestraTexture
        """
        bars = bars or self.config.length
        mode = mode or self.config.texture_mode
        
        if isinstance(mode, str):
            mode = TextureMode(mode)
        
        return self.texture_gen.generate_texture(bars, mode)
    
    def generate_homophonic(self, bars: int = 8) -> OrchestraTexture:
        """Generate homophonic texture."""
        return self.texture_gen.generate_homophonic(bars)
    
    def generate_contrapuntal(self, bars: int = 8) -> OrchestraTexture:
        """Generate contrapuntal texture."""
        return self.texture_gen.generate_contrapuntal(bars)
    
    def generate_hybrid(self, bars: int = 8) -> OrchestraTexture:
        """Generate hybrid texture."""
        return self.texture_gen.generate_hybrid(bars)
    
    def generate_harmonic_field(self, bars: int = 8) -> OrchestraTexture:
        """Generate harmonic field texture."""
        return self.texture_gen.generate_harmonic_field(bars)
    
    def generate_ostinato(self, bars: int = 8) -> OrchestraTexture:
        """Generate ostinato texture."""
        return self.texture_gen.generate_ostinato(bars)
    
    def generate_orchestral_pads(self, bars: int = 8) -> OrchestraTexture:
        """Generate orchestral pads texture."""
        return self.texture_gen.generate_orchestral_pads(bars)
    
    # =========================================================================
    # OUTPUT
    # =========================================================================
    
    def to_score(
        self,
        texture: OrchestraTexture,
        title: str = "Orchestra",
        composer: str = "Orchestral Engine"
    ) -> OrchestraScore:
        """Convert texture to score."""
        return self.output.texture_to_score(texture, title, composer)
    
    def to_json(self, score: OrchestraScore) -> Dict:
        """Convert score to JSON."""
        return self.output.to_json(score)
    
    def to_musicxml(self, score: OrchestraScore) -> str:
        """Convert score to MusicXML."""
        return self.output.to_musicxml(score)
    
    def export(
        self,
        texture: OrchestraTexture,
        output_path: str,
        title: str = "Orchestra",
        formats: List[str] = None
    ) -> Dict[str, str]:
        """
        Export texture to files.
        
        Args:
            texture: OrchestraTexture to export
            output_path: Base output path
            title: Score title
            formats: List of formats
        
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
        self.expander = VoiceExpander(self.config)
        self.texture_gen = TextureGenerator(self.config, seed=self.seed)
        self.output = OrchestraOutput(self.config)
    
    def get_config(self) -> Dict:
        """Get current configuration."""
        return self.config.to_dict()
    
    # =========================================================================
    # DIAGNOSTICS
    # =========================================================================
    
    def get_diagnostics(self, texture: OrchestraTexture) -> Dict:
        """
        Generate diagnostic information about a texture.
        
        Returns dict with spacing, register, VL-SM info.
        """
        diagnostics = {
            "bars": texture.bars,
            "texture_type": texture.texture_type.value,
            "instruments_used": [],
            "register_ranges": {},
            "spacing_analysis": {},
            "vl_sm_mode": self.config.motion_type.value,
            "orchestration_profile": self.config.orchestration_profile.value,
            "register_profile": self.config.register_profile.value
        }
        
        # Analyze instruments and ranges
        inst_pitches = {}
        for moment in texture.moments:
            for inst, (pitch, _) in moment.voices.items():
                if inst not in inst_pitches:
                    inst_pitches[inst] = []
                inst_pitches[inst].append(pitch)
        
        for inst, pitches in inst_pitches.items():
            inst_def = ORCHESTRA_INSTRUMENTS[inst]
            diagnostics["instruments_used"].append(inst.value)
            diagnostics["register_ranges"][inst.value] = {
                "min": min(pitches),
                "max": max(pitches),
                "instrument_range": [inst_def.range_low, inst_def.range_high],
                "in_range": all(inst_def.range_low <= p <= inst_def.range_high for p in pitches)
            }
        
        # Spacing analysis (intervals between adjacent voices)
        for moment in texture.moments:
            pitches = sorted([p for p, _ in moment.voices.values()])
            if len(pitches) >= 2:
                intervals = [pitches[i+1] - pitches[i] for i in range(len(pitches)-1)]
                diagnostics["spacing_analysis"][f"bar_{moment.bar}_beat_{moment.beat}"] = {
                    "intervals": intervals,
                    "max_gap": max(intervals),
                    "min_gap": min(intervals)
                }
        
        return diagnostics

