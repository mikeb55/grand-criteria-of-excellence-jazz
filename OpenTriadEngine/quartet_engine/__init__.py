"""
Quartet Engine (Open Triad Edition)
====================================

A four-voice generative system for string quartet writing using the 
harmonic logic of Open Triad Engine v1.0.

Features:
- Open-triad voicing distribution across Violin I, II, Viola, Cello
- Contrapuntal voice behaviour with VL-SM integration
- Functional and modal harmonic movement
- Multiple texture modes (homophonic, contrapuntal, hybrid, etc.)
- Adaptive voice-leading
- MusicXML and PDF score output
"""

from .inputs import QuartetConfig, QuartetMode, TextureDensity, MotionType
from .instruments import Instrument, QuartetInstruments, VoiceRange
from .voice_assignment import VoiceAssignment, VoiceDistribution
from .counterpoint import CounterpointEngine, VoiceLine
from .textures import TextureGenerator, QuartetTexture
from .patterns import PatternEngine, QuartetPattern
from .rhythm import RhythmEngine, QuartetRhythm
from .output import QuartetOutput, QuartetScore
from .engine import QuartetEngine

__version__ = "1.0.0"
__all__ = [
    "QuartetEngine",
    "QuartetConfig",
    "QuartetMode",
    "TextureDensity",
    "MotionType",
    "Instrument",
    "QuartetInstruments",
    "VoiceRange",
    "VoiceAssignment",
    "VoiceDistribution",
    "CounterpointEngine",
    "VoiceLine",
    "TextureGenerator",
    "QuartetTexture",
    "PatternEngine",
    "QuartetPattern",
    "RhythmEngine",
    "QuartetRhythm",
    "QuartetOutput",
    "QuartetScore",
]

