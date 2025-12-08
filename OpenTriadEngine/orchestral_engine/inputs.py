"""
Input Module for Orchestral Engine
===================================

Handles input validation and configuration.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum


class TextureMode(Enum):
    """Texture modes for orchestral writing."""
    HOMOPHONIC = "homophonic"
    CONTRAPUNTAL = "contrapuntal"
    HYBRID = "hybrid"
    HARMONIC_FIELD = "harmonic_field"
    OSTINATO = "ostinato"
    ORCHESTRAL_PADS = "orchestral_pads"


class Density(Enum):
    """Orchestral density levels."""
    SPARSE = "sparse"
    MEDIUM = "medium"
    DENSE = "dense"


class MotionType(Enum):
    """Harmonic motion types."""
    FUNCTIONAL = "functional"
    MODAL = "modal"
    INTERVALLIC = "intervallic"
    CINEMATIC = "cinematic"


class OrchestrationProfile(Enum):
    """Orchestration timbral profiles."""
    BRIGHT = "bright"
    WARM = "warm"
    DARK = "dark"
    TRANSPARENT = "transparent"


class RegisterProfile(Enum):
    """Register profiles for orchestration."""
    HIGH = "high"
    MID = "mid"
    LOW = "low"
    MIXED = "mixed"


class RhythmicStyle(Enum):
    """Rhythmic styles."""
    STRAIGHT = "straight"
    SYNCOPATED = "syncopated"
    TRIPLET = "triplet"
    POLYRHYTHMIC = "polyrhythmic"


# Valid scales
VALID_SCALES = [
    "major", "minor", "dorian", "phrygian", "lydian", "mixolydian",
    "aeolian", "locrian", "harmonic_minor", "melodic_minor",
    "whole_tone", "diminished", "pentatonic", "blues"
]


@dataclass
class OrchestraConfig:
    """
    Configuration for the Orchestral Engine.
    
    Attributes:
        key: Musical key (C, D, E, etc.)
        scale: Scale type
        progression: Optional chord progression
        texture_mode: Texture mode for orchestral writing
        density: Orchestral density
        motion_type: Type of harmonic motion
        length: Number of bars
        orchestration_profile: Timbral profile
        register_profile: Register profile
        rhythmic_style: Rhythmic style
        tempo: Tempo in BPM
        time_signature: Time signature tuple
    """
    key: str = "C"
    scale: str = "major"
    progression: Optional[List[str]] = None
    texture_mode: TextureMode = TextureMode.HOMOPHONIC
    density: Density = Density.MEDIUM
    motion_type: MotionType = MotionType.MODAL
    length: int = 8
    orchestration_profile: OrchestrationProfile = OrchestrationProfile.WARM
    register_profile: RegisterProfile = RegisterProfile.MIXED
    rhythmic_style: RhythmicStyle = RhythmicStyle.STRAIGHT
    tempo: int = 80
    time_signature: Tuple[int, int] = (4, 4)
    
    def __post_init__(self):
        """Validate and normalize inputs."""
        # Normalize key
        self.key = self.key.upper() if len(self.key) == 1 else self.key.capitalize()
        
        # Normalize scale
        self.scale = self.scale.lower().replace(" ", "_")
        if self.scale not in VALID_SCALES:
            self.scale = "major"
        
        # Convert string enums
        if isinstance(self.texture_mode, str):
            self.texture_mode = TextureMode(self.texture_mode)
        if isinstance(self.density, str):
            self.density = Density(self.density)
        if isinstance(self.motion_type, str):
            self.motion_type = MotionType(self.motion_type)
        if isinstance(self.orchestration_profile, str):
            self.orchestration_profile = OrchestrationProfile(self.orchestration_profile)
        if isinstance(self.register_profile, str):
            self.register_profile = RegisterProfile(self.register_profile)
        if isinstance(self.rhythmic_style, str):
            self.rhythmic_style = RhythmicStyle(self.rhythmic_style)
        
        # Validate length
        if self.length < 1:
            self.length = 8
        if self.length > 64:
            self.length = 64
        
        # Validate tempo
        if self.tempo < 40:
            self.tempo = 40
        if self.tempo > 240:
            self.tempo = 240
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "key": self.key,
            "scale": self.scale,
            "progression": self.progression,
            "texture_mode": self.texture_mode.value,
            "density": self.density.value,
            "motion_type": self.motion_type.value,
            "length": self.length,
            "orchestration_profile": self.orchestration_profile.value,
            "register_profile": self.register_profile.value,
            "rhythmic_style": self.rhythmic_style.value,
            "tempo": self.tempo,
            "time_signature": self.time_signature
        }

