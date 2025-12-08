"""
Chord-Melody Engine (Open Triad Edition)
=========================================

A generator that takes a melody and produces modern chord-melody arrangements
using open triads from Open Triad Engine v1.0.

Features:
- Multiple harmonisation modes (diatonic, reharm, UST, functional, modal)
- Melody always preserved as top voice
- VL-SM integration for smooth voice-leading
- Optional counterpoint in lower voices
- Guitar-playable voicings with TAB
- MusicXML and PDF export
"""

from .inputs import ChordMelodyConfig, HarmonisationStyle, Texture, RhythmAlignment
from .melody import MelodyNote, MelodyParser, Melody
from .harmonisation import HarmonisationEngine, HarmonisedMoment
from .voicing import VoicingGenerator, ChordMelodyVoicing
from .counterpoint import CounterpointGenerator
from .rhythm import RhythmRealiser
from .output import ChordMelodyOutput
from .engine import ChordMelodyEngine

__version__ = "1.0.0"
__all__ = [
    "ChordMelodyEngine",
    "ChordMelodyConfig",
    "HarmonisationStyle",
    "Texture",
    "RhythmAlignment",
    "MelodyNote",
    "MelodyParser",
    "Melody",
    "HarmonisationEngine",
    "HarmonisedMoment",
    "VoicingGenerator",
    "ChordMelodyVoicing",
    "CounterpointGenerator",
    "RhythmRealiser",
    "ChordMelodyOutput",
]

