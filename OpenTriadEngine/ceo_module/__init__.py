"""
Combined Engine Orchestrator (CEO Module)
==========================================

A top-level orchestration layer providing a single, unified interface for:
1. Open Triad Engine v1.0
2. Etude Generator Add-On
3. Triad Pair Solo Engine
4. Chord-Melody Engine (Open Triad Edition)

Features:
- Natural language request parsing
- Automatic engine routing
- Shared parameter normalization
- Unified export (JSON, MusicXML, PDF)
- Comprehensive error handling
"""

from .parser import RequestParser, CEORequest, EngineType
from .router import EngineRouter
from .normalizer import ParameterNormalizer
from .export_manager import ExportManager
from .error_handler import CEOErrorHandler, CEOError
from .shared import SharedSubsystems
from .orchestrator import CombinedEngineOrchestrator

__version__ = "1.0.0"
__all__ = [
    "CombinedEngineOrchestrator",
    "RequestParser",
    "CEORequest",
    "EngineType",
    "EngineRouter",
    "ParameterNormalizer",
    "ExportManager",
    "CEOErrorHandler",
    "CEOError",
    "SharedSubsystems",
]

