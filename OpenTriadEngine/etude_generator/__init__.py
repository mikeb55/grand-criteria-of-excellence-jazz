"""
Etude Generator Add-on for Open Triad Engine v1.0
==================================================

A generator that produces playable guitar etudes using the Open Triad Engine.

Features:
- 7 structural etude templates
- Voice-leading integration (APVL, TRAM, SISM)
- Melodic pattern stitching
- Rhythm generation
- MusicXML, TAB, and PDF export

Author: GCE-Jazz Project
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "GCE-Jazz Project"

# Input configuration
from .inputs import (
    EtudeConfig,
    EtudeType,
    Difficulty,
    RhythmicStyle,
    EtudeMode,
    validate_config
)

# Harmonic generation
from .harmonic import (
    HarmonicGenerator,
    HarmonicMaterial
)

# Pattern generation
from .patterns import (
    PatternStitcher,
    EtudePhrase,
    BarContent
)

# Structural templates
from .templates import (
    EtudeTemplate,
    ScalarOpenTriadEtude,
    InversionCycleEtude,
    IntervallicEtude,
    PositionLockedEtude,
    StringSetEtude,
    TwoFiveOneEtude,
    ChordMelodyMiniEtude
)

# Rhythm generation
from .rhythm import (
    RhythmGenerator,
    RhythmicPhrase
)

# Output formats
from .output import (
    EtudeOutput,
    EtudeExporter,
    GuitarTabGenerator,
    EtudePDFBuilder
)

# Main generator
from .generator import (
    EtudeGenerator,
    GeneratedEtude,
    generate_etude
)


def create_etude(**kwargs) -> 'GeneratedEtude':
    """
    Factory function to create an etude with configuration.
    
    Args:
        key: Key or scale (e.g., 'C', 'G dorian')
        progression: Optional chord progression
        etude_type: melodic | harmonic | intervallic | chord_melody | position | string_set
        difficulty: beginner | intermediate | advanced
        string_set: "6-4" | "5-3" | "4-2" | auto
        mode: functional | modal | intervallic
        rhythmic_style: straight | syncopated | triplet | polyrhythmic
        length: Number of bars
        
    Returns:
        GeneratedEtude with notation, TAB, and export options
    """
    config = EtudeConfig(**kwargs)
    generator = EtudeGenerator(config)
    return generator.generate()


__all__ = [
    # Version info
    '__version__',
    '__author__',
    
    # Inputs
    'EtudeConfig',
    'EtudeType',
    'Difficulty',
    'RhythmicStyle',
    'EtudeMode',
    'validate_config',
    
    # Harmonic
    'HarmonicGenerator',
    'HarmonicMaterial',
    
    # Patterns
    'PatternStitcher',
    'EtudePhrase',
    'BarContent',
    
    # Templates
    'EtudeTemplate',
    'ScalarOpenTriadEtude',
    'InversionCycleEtude',
    'IntervallicEtude',
    'PositionLockedEtude',
    'StringSetEtude',
    'TwoFiveOneEtude',
    'ChordMelodyMiniEtude',
    
    # Rhythm
    'RhythmGenerator',
    'RhythmicPhrase',
    
    # Output
    'EtudeOutput',
    'EtudeExporter',
    'GuitarTabGenerator',
    'EtudePDFBuilder',
    
    # Generator
    'EtudeGenerator',
    'GeneratedEtude',
    'generate_etude',
    'create_etude',
]

