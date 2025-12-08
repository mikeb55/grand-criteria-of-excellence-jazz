"""
Orchestral Engine (Small Orchestra Edition) v1.0
=================================================

A small-orchestra generative system using open triads from the Open Triad Engine v1.0.

Instruments:
- Flute, Clarinet in Bb, Flugelhorn/Trumpet
- Violin I, Violin II, Viola, Cello, Bass
- Piano
- Light Percussion (optional)
"""

from .inputs import (
    OrchestraConfig, TextureMode, OrchestrationProfile,
    RegisterProfile, MotionType, RhythmicStyle, Density
)
from .instruments import InstrumentType, OrchestraInstruments
from .engine import OrchestralEngine

__all__ = [
    "OrchestralEngine",
    "OrchestraConfig",
    "TextureMode",
    "OrchestrationProfile",
    "RegisterProfile",
    "MotionType",
    "RhythmicStyle",
    "Density",
    "InstrumentType",
    "OrchestraInstruments",
]

__version__ = "1.0.0"

