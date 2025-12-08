"""
Engine Router for CEO Module
==============================

Routes requests to the correct engine(s) and handles multi-engine workflows.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .parser import CEORequest, EngineType, TaskType


@dataclass
class EngineResult:
    """
    Result from an engine execution.
    
    Attributes:
        engine: Which engine produced this result
        success: Whether execution succeeded
        data: The output data (phrases, voicings, etc.)
        json_output: JSON representation
        musicxml_output: MusicXML string (if applicable)
        error: Error message if failed
        metadata: Additional metadata
    """
    engine: EngineType
    success: bool
    data: Any = None
    json_output: Optional[Dict] = None
    musicxml_output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WorkflowResult:
    """
    Result from a complete workflow (possibly multi-engine).
    
    Attributes:
        success: Overall success
        engine_results: Results from each engine
        combined_output: Merged output from all engines
        errors: Any errors encountered
    """
    success: bool
    engine_results: List[EngineResult]
    combined_output: Optional[Dict] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class EngineRouter:
    """
    Routes requests to appropriate engines and manages multi-engine workflows.
    """
    
    def __init__(self):
        """Initialize the router with engine references."""
        self.engines = {}
        self.engine_available = {
            EngineType.OPEN_TRIAD: False,
            EngineType.ETUDE_GENERATOR: False,
            EngineType.TRIAD_PAIR_SOLO: False,
            EngineType.CHORD_MELODY: False,
        }
        self._load_engines()
    
    def _load_engines(self):
        """Attempt to load all available engines."""
        # Try to load Open Triad Engine
        try:
            from open_triad_engine.engine import OpenTriadEngine
            self.engines[EngineType.OPEN_TRIAD] = OpenTriadEngine
            self.engine_available[EngineType.OPEN_TRIAD] = True
        except ImportError:
            pass
        
        # Try to load Etude Generator
        try:
            from etude_generator.generator import EtudeGenerator
            self.engines[EngineType.ETUDE_GENERATOR] = EtudeGenerator
            self.engine_available[EngineType.ETUDE_GENERATOR] = True
        except ImportError:
            pass
        
        # Try to load Triad Pair Solo Engine
        try:
            from triad_pair_solo_engine.engine import TriadPairSoloEngine
            self.engines[EngineType.TRIAD_PAIR_SOLO] = TriadPairSoloEngine
            self.engine_available[EngineType.TRIAD_PAIR_SOLO] = True
        except ImportError:
            pass
        
        # Try to load Chord-Melody Engine
        try:
            from chord_melody_engine.engine import ChordMelodyEngine
            self.engines[EngineType.CHORD_MELODY] = ChordMelodyEngine
            self.engine_available[EngineType.CHORD_MELODY] = True
        except ImportError:
            pass
    
    def get_available_engines(self) -> List[EngineType]:
        """Get list of available engines."""
        return [e for e, available in self.engine_available.items() if available]
    
    def is_engine_available(self, engine_type: EngineType) -> bool:
        """Check if an engine is available."""
        return self.engine_available.get(engine_type, False)
    
    def route(self, request: CEORequest) -> WorkflowResult:
        """
        Route a request to the appropriate engine(s).
        
        Args:
            request: The parsed CEORequest
        
        Returns:
            WorkflowResult with all engine outputs
        """
        if request.engine == EngineType.MULTI:
            return self._execute_multi_engine(request)
        else:
            result = self._execute_single_engine(request)
            return WorkflowResult(
                success=result.success,
                engine_results=[result],
                combined_output=result.json_output,
                errors=[result.error] if result.error else []
            )
    
    def _execute_single_engine(self, request: CEORequest) -> EngineResult:
        """Execute a single engine."""
        engine_type = request.engine
        
        if not self.is_engine_available(engine_type):
            return EngineResult(
                engine=engine_type,
                success=False,
                error=f"Engine {engine_type.value} is not available"
            )
        
        try:
            if engine_type == EngineType.OPEN_TRIAD:
                return self._run_open_triad(request)
            elif engine_type == EngineType.ETUDE_GENERATOR:
                return self._run_etude_generator(request)
            elif engine_type == EngineType.TRIAD_PAIR_SOLO:
                return self._run_triad_pair_solo(request)
            elif engine_type == EngineType.CHORD_MELODY:
                return self._run_chord_melody(request)
            else:
                return EngineResult(
                    engine=engine_type,
                    success=False,
                    error=f"Unknown engine type: {engine_type}"
                )
        except Exception as e:
            return EngineResult(
                engine=engine_type,
                success=False,
                error=str(e)
            )
    
    def _execute_multi_engine(self, request: CEORequest) -> WorkflowResult:
        """Execute multiple engines in sequence."""
        results = []
        errors = []
        
        engines_to_run = request.engines_sequence or [EngineType.OPEN_TRIAD]
        
        for engine_type in engines_to_run:
            # Create a sub-request for this engine
            sub_request = CEORequest(
                engine=engine_type,
                task=request.task,
                key=request.key,
                scale=request.scale,
                progression=request.progression,
                melody=request.melody,
                bars=request.bars,
                mode=request.mode,
                style=request.style,
                string_set=request.string_set,
                difficulty=request.difficulty,
                rhythmic_style=request.rhythmic_style,
                texture=request.texture,
                output_formats=request.output_formats,
                additional_params=request.additional_params
            )
            
            result = self._execute_single_engine(sub_request)
            results.append(result)
            
            if not result.success:
                errors.append(result.error or f"Engine {engine_type.value} failed")
        
        # Combine outputs
        combined = self._combine_results(results)
        
        return WorkflowResult(
            success=all(r.success for r in results),
            engine_results=results,
            combined_output=combined,
            errors=errors
        )
    
    def _run_open_triad(self, request: CEORequest) -> EngineResult:
        """Run the Open Triad Engine."""
        try:
            from open_triad_engine.engine import OpenTriadEngine
            
            engine = OpenTriadEngine(
                key=request.key,
                scale=request.scale,
                mode=request.mode
            )
            
            # Generate based on task
            if request.task == TaskType.GENERATE_INVERSIONS:
                result = engine.generate_inversion_cycle()
            else:
                result = engine.generate_voicings()
            
            return EngineResult(
                engine=EngineType.OPEN_TRIAD,
                success=True,
                data=result,
                json_output=result if isinstance(result, dict) else {"data": str(result)},
                metadata={"key": request.key, "scale": request.scale}
            )
        except Exception as e:
            return EngineResult(
                engine=EngineType.OPEN_TRIAD,
                success=False,
                error=str(e)
            )
    
    def _run_etude_generator(self, request: CEORequest) -> EngineResult:
        """Run the Etude Generator."""
        try:
            from etude_generator.generator import EtudeGenerator
            
            generator = EtudeGenerator(
                key=request.key,
                scale=request.scale,
                string_set=request.string_set,
                difficulty=request.difficulty,
                rhythmic_style=request.rhythmic_style
            )
            
            etude = generator.generate_etude(
                bars=request.bars,
                etude_type=request.mode
            )
            
            json_output = generator.to_json(etude)
            musicxml = generator.to_musicxml(etude)
            
            return EngineResult(
                engine=EngineType.ETUDE_GENERATOR,
                success=True,
                data=etude,
                json_output=json_output,
                musicxml_output=musicxml,
                metadata={"bars": request.bars, "type": request.mode}
            )
        except Exception as e:
            return EngineResult(
                engine=EngineType.ETUDE_GENERATOR,
                success=False,
                error=str(e)
            )
    
    def _run_triad_pair_solo(self, request: CEORequest) -> EngineResult:
        """Run the Triad Pair Solo Engine."""
        try:
            from triad_pair_solo_engine.engine import TriadPairSoloEngine
            
            engine = TriadPairSoloEngine(
                key=request.key,
                scale=request.scale,
                mode=request.mode,
                string_set=request.string_set,
                rhythmic_style=request.rhythmic_style,
                difficulty=request.difficulty,
                contour=request.contour
            )
            
            phrase = engine.generate_phrase(bars=request.bars)
            
            json_output = engine.to_json(phrase)
            musicxml = engine.to_musicxml(phrase)
            
            return EngineResult(
                engine=EngineType.TRIAD_PAIR_SOLO,
                success=True,
                data=phrase,
                json_output=json_output,
                musicxml_output=musicxml,
                metadata={"bars": request.bars, "mode": request.mode}
            )
        except Exception as e:
            return EngineResult(
                engine=EngineType.TRIAD_PAIR_SOLO,
                success=False,
                error=str(e)
            )
    
    def _run_chord_melody(self, request: CEORequest) -> EngineResult:
        """Run the Chord-Melody Engine."""
        try:
            from chord_melody_engine.engine import ChordMelodyEngine
            
            engine = ChordMelodyEngine(
                key=request.key,
                scale=request.scale,
                harmonisation_style=request.style,
                texture=request.texture,
                string_set=request.string_set,
                difficulty=request.difficulty
            )
            
            # Melody is required
            if request.melody is None:
                return EngineResult(
                    engine=EngineType.CHORD_MELODY,
                    success=False,
                    error="Melody input is required for chord-melody generation"
                )
            
            arrangement = engine.harmonise(request.melody)
            
            json_output = engine.to_json(arrangement)
            musicxml = engine.to_musicxml(arrangement)
            
            return EngineResult(
                engine=EngineType.CHORD_MELODY,
                success=True,
                data=arrangement,
                json_output=json_output,
                musicxml_output=musicxml,
                metadata={"style": request.style}
            )
        except Exception as e:
            return EngineResult(
                engine=EngineType.CHORD_MELODY,
                success=False,
                error=str(e)
            )
    
    def _combine_results(self, results: List[EngineResult]) -> Dict:
        """Combine multiple engine results into one output."""
        combined = {
            "workflow": "multi-engine",
            "engines_used": [r.engine.value for r in results if r.success],
            "outputs": []
        }
        
        for result in results:
            if result.success and result.json_output:
                combined["outputs"].append({
                    "engine": result.engine.value,
                    "data": result.json_output,
                    "metadata": result.metadata
                })
        
        return combined
    
    def get_engine_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of each available engine."""
        capabilities = {}
        
        if self.engine_available[EngineType.OPEN_TRIAD]:
            capabilities["open_triad"] = [
                "closed_to_open_conversion",
                "inversion_cycling",
                "voice_leading",
                "scale_mapping"
            ]
        
        if self.engine_available[EngineType.ETUDE_GENERATOR]:
            capabilities["etude_generator"] = [
                "scalar_etudes",
                "inversion_cycle_etudes",
                "intervallic_etudes",
                "position_locked_etudes",
                "string_set_etudes",
                "ii_v_i_etudes",
                "chord_melody_etudes"
            ]
        
        if self.engine_available[EngineType.TRIAD_PAIR_SOLO]:
            capabilities["triad_pair_solo"] = [
                "diatonic_pairs",
                "klemonic_pairs",
                "ust_pairs",
                "altered_dominant_pairs",
                "intervallic_mode",
                "functional_mode",
                "modal_mode"
            ]
        
        if self.engine_available[EngineType.CHORD_MELODY]:
            capabilities["chord_melody"] = [
                "diatonic_harmonisation",
                "reharmonisation",
                "ust_harmonisation",
                "functional_harmonisation",
                "modal_harmonisation"
            ]
        
        return capabilities

