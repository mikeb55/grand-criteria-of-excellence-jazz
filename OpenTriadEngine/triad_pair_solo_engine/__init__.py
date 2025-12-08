"""
Triad Pair Solo Engine (Open Triad Edition)
============================================

An improvisation-focused generator that produces intervallic, modern jazz 
solo lines using triad pairs transformed into open triads.

Depends on Open Triad Engine v1.0 for triad generation, inversion logic,
voice-leading (VL-SM), scale mapping, and pattern generation.
"""

from .inputs import SoloEngineConfig, TriadPairType, ContourType, SoloDifficulty
from .triad_pairs import TriadPairSelector, TriadPair
from .patterns import SoloPatternGenerator
from .rhythm import SoloRhythmEngine
from .phrase_assembler import PhraseAssembler, SoloPhrase
from .output import SoloOutputFormatter
from .engine import TriadPairSoloEngine

__version__ = "1.0.0"
__all__ = [
    "TriadPairSoloEngine",
    "SoloEngineConfig",
    "TriadPairType",
    "ContourType",
    "SoloDifficulty",
    "TriadPairSelector",
    "TriadPair",
    "SoloPatternGenerator",
    "SoloRhythmEngine",
    "PhraseAssembler",
    "SoloPhrase",
    "SoloOutputFormatter",
]

