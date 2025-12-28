"""
Barry Engine - Rule-Based Jazz Analysis and Improvement System
================================================================

Barry is an abstract, rule-based jazz engine built on General Musical Language (GML),
inspired by Barry Harris-style concepts of movement, bebop language, and clear criteria
of excellence.

Barry is instrument-agnostic: it analyzes GML phrases, progressions, and sections,
scores them against explicit jazz criteria, and suggests improvements.

Core API:
    - Analysis functions: score_phrase_movement, score_phrase_bebop_idiom, etc.
    - Transformation functions: improve_line_movement, add_bebop_enclosures, etc.
    - Orchestration: evaluate_phrase_bundle, suggest_best_candidate_line
"""

from .gml import (
    GMLNote,
    GMLPhrase,
    GMLProgression,
    GMLSection,
    GMLForm,
    PhraseRole,
    HarmonicFunction
)

from .barry import (
    BarryEngine,
    AnalysisResult,
    TransformationResult,
    evaluate_phrase_bundle,
    suggest_best_candidate_line
)

# Import convenience functions directly from their modules
from .movement import score_phrase_movement
from .bebop import score_phrase_bebop_idiom
from .gce_scoring import score_section_form_alignment
from .transformations import (
    improve_line_movement,
    add_bebop_enclosures,
    strengthen_cadence
)

__version__ = "1.0.0"
__all__ = [
    # GML Structures
    "GMLNote",
    "GMLPhrase",
    "GMLProgression",
    "GMLSection",
    "GMLForm",
    "PhraseRole",
    "HarmonicFunction",
    # Main Engine
    "BarryEngine",
    "AnalysisResult",
    "TransformationResult",
    # Analysis Functions
    "score_phrase_movement",
    "score_phrase_bebop_idiom",
    "score_section_form_alignment",
    # Transformation Functions
    "improve_line_movement",
    "add_bebop_enclosures",
    "strengthen_cadence",
    # Orchestration
    "evaluate_phrase_bundle",
    "suggest_best_candidate_line",
]

