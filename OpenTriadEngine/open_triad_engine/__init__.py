"""
Open Triad Engine v1.0
======================

A modular generative engine that converts closed triads into open triads,
cycles inversions, performs adaptive voice-leading, maps shapes across scales
or progressions, and outputs melodic/harmonic/chord-melody/counterpoint/
orchestration material.

Designed to be installable as a standalone module but callable by other
generators (EtudeGen, MAMS, TriadPair Engine, Counterpoint Companion, 
Quartet Engine, etc.).

Author: GCE-Jazz Project
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "GCE-Jazz Project"

# Core music theory classes
from .core import (
    Note,
    Interval,
    Triad,
    TriadType,
    Inversion,
    VoicingType,
    CHROMATIC_NOTES,
    ENHARMONIC_MAP
)

# Input handling and validation
from .inputs import (
    EngineConfig,
    InputValidator,
    StringSet,
    EngineMode,
    VoiceLeadingPriority,
    TriadSource
)

# Transformation modules
from .transformations import (
    ClosedToOpenConverter,
    InversionEngine,
    ScaleMapper,
    DropVoicing
)

# Voice-leading smart module
from .voice_leading import (
    VoiceLeadingSmartModule,
    VLMode,
    VoiceLeadingResult,
    APVL,
    TRAM,
    SISM
)

# Output shape modules
from .output_shapes import (
    ShapeBundle,
    MelodicPatternGenerator,
    RhythmicTemplate,
    ContourSignature
)

# Special use-case engines
from .special_engines import (
    ChordMelodyEngine,
    TwoFiveOneEngine,
    OpenTriadPairEngine,
    CounterpointCompanion,
    OrchestrationMapper
)

# Export modules
from .exports import (
    MusicXMLExporter,
    PDFEtudeBuilder,
    TABExporter,
    NotationExporter
)

# Convenience factory function
from .engine import OpenTriadEngine


def create_engine(**kwargs) -> 'OpenTriadEngine':
    """
    Factory function to create an OpenTriadEngine instance with configuration.
    
    Args:
        triad_type: major | minor | dim | aug | sus | hybrid
        source: diatonic | chromatic | progression | user_defined | tonality_vault
        string_set: "6-4" | "5-3" | "4-2" | auto
        mode: melodic | harmonic | chord_melody | counterpoint | orchestration
        priority: smooth | intervallic | mixed
        scale_map: array of scale names
        register_limits: dict with 'low' and 'high' pitch definitions
        
    Returns:
        Configured OpenTriadEngine instance
    """
    config = EngineConfig(**kwargs)
    return OpenTriadEngine(config)


__all__ = [
    # Version info
    '__version__',
    '__author__',
    
    # Core
    'Note',
    'Interval', 
    'Triad',
    'TriadType',
    'Inversion',
    'VoicingType',
    'CHROMATIC_NOTES',
    'ENHARMONIC_MAP',
    
    # Inputs
    'EngineConfig',
    'InputValidator',
    'StringSet',
    'EngineMode',
    'VoiceLeadingPriority',
    'TriadSource',
    
    # Transformations
    'ClosedToOpenConverter',
    'InversionEngine',
    'ScaleMapper',
    'DropVoicing',
    
    # Voice Leading
    'VoiceLeadingSmartModule',
    'VLMode',
    'VoiceLeadingResult',
    'APVL',
    'TRAM',
    'SISM',
    
    # Output Shapes
    'ShapeBundle',
    'MelodicPatternGenerator',
    'RhythmicTemplate',
    'ContourSignature',
    
    # Special Engines
    'ChordMelodyEngine',
    'TwoFiveOneEngine',
    'OpenTriadPairEngine',
    'CounterpointCompanion',
    'OrchestrationMapper',
    
    # Exports
    'MusicXMLExporter',
    'PDFEtudeBuilder',
    'TABExporter',
    'NotationExporter',
    
    # Main Engine
    'OpenTriadEngine',
    'create_engine',
]

