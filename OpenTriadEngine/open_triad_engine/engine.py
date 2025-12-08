"""
Open Triad Engine v1.0 - Main Engine Interface
===============================================

The primary interface for the Open Triad Engine, designed to be
called by other generators (EtudeGen, MAMS, TriadPair Engine,
Counterpoint Companion, Quartet Engine, etc.).

Provides a clean, unified API for all engine functionality.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

from .core import Note, Triad, TriadType, Inversion, VoicingType, create_triad
from .inputs import EngineConfig, EngineMode, VoiceLeadingPriority, RegisterLimits
from .transformations import (
    ClosedToOpenConverter, InversionEngine, ScaleMapper, DropVoicing
)
from .voice_leading import (
    VoiceLeadingSmartModule, VLMode, VoiceLeadingResult, APVL, TRAM, SISM
)
from .output_shapes import (
    ShapeBundle, MelodicPatternGenerator, RhythmicTemplate, 
    MelodicPattern, ContourSignature, ArpeggioPattern
)
from .special_engines import (
    ChordMelodyEngine, TwoFiveOneEngine, OpenTriadPairEngine,
    CounterpointCompanion, OrchestrationMapper, TwoFiveOneResult
)
from .exports import (
    MusicXMLExporter, PDFEtudeBuilder, TABExporter, NotationExporter,
    ExportOptions
)
from .tonality_vault import TonalityVault, Scale


@dataclass
class EngineResult:
    """
    Standard result container for engine operations.
    
    Provides a consistent interface for all engine outputs.
    """
    success: bool
    operation: str
    data: Any
    message: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'operation': self.operation,
            'message': self.message,
            'metadata': self.metadata,
            'data': self._serialize_data()
        }
    
    def _serialize_data(self) -> Any:
        """Serialize data to JSON-compatible format."""
        if isinstance(self.data, list):
            return [self._serialize_item(item) for item in self.data]
        return self._serialize_item(self.data)
    
    def _serialize_item(self, item: Any) -> Any:
        """Serialize a single item."""
        if hasattr(item, 'to_dict'):
            return item.to_dict()
        return item


class OpenTriadEngine:
    """
    The main Open Triad Engine class.
    
    Provides a unified interface for all open triad operations,
    designed to be easily integrated with other music generators.
    
    Example Usage:
        # Create engine with config
        engine = OpenTriadEngine(EngineConfig(
            triad_type='major',
            mode='melodic',
            priority='smooth'
        ))
        
        # Generate open triads across a scale
        result = engine.generate_scale_triads('C', 'ionian')
        
        # Get shape bundles for practice
        bundles = engine.get_shape_bundles(result.data)
        
        # Voice lead a progression
        vl_result = engine.voice_lead_progression(['Dm', 'G', 'C'])
        
        # Export to MusicXML
        engine.export_musicxml(result.data, 'output.xml')
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Optional[EngineConfig] = None):
        """
        Initialize the engine with configuration.
        
        Args:
            config: Engine configuration (uses defaults if not provided)
        """
        self.config = config or EngineConfig()
        
        # Initialize sub-modules
        self._init_modules()
    
    def _init_modules(self):
        """Initialize all engine modules."""
        # Core transformation modules
        self.converter = ClosedToOpenConverter()
        self.inversion_engine = InversionEngine()
        self.scale_mapper = ScaleMapper()
        self.tonality_vault = TonalityVault()
        
        # Voice leading module
        vl_mode = self._get_vl_mode()
        self.voice_leading = VoiceLeadingSmartModule(
            mode=vl_mode,
            allow_parallel_fifths=self.config.allow_parallel_fifths,
            allow_parallel_octaves=self.config.allow_parallel_octaves,
            prefer_contrary_motion=self.config.prefer_contrary_motion,
            max_voice_leap=self.config.max_voice_leap,
            register_limits=self.config.get_register_limits_obj(),
            instruments=self.config.instruments
        )
        
        # Special engines
        self.chord_melody = ChordMelodyEngine()
        self.two_five_one = TwoFiveOneEngine()
        self.triad_pair = OpenTriadPairEngine()
        self.counterpoint = CounterpointCompanion()
        self.orchestration = OrchestrationMapper()
        
        # Pattern generator
        self.pattern_gen = MelodicPatternGenerator()
    
    def _get_vl_mode(self) -> VLMode:
        """Get VL mode from config."""
        mode_map = {
            'melodic': VLMode.FUNCTIONAL,
            'harmonic': VLMode.FUNCTIONAL,
            'chord_melody': VLMode.FUNCTIONAL,
            'counterpoint': VLMode.COUNTERPOINT,
            'orchestration': VLMode.ORCHESTRATION
        }
        return mode_map.get(self.config.mode, VLMode.FUNCTIONAL)
    
    # =========================================================================
    # Core Triad Operations
    # =========================================================================
    
    def create_triad(
        self,
        root: str,
        triad_type: str = 'major',
        octave: int = 4
    ) -> Triad:
        """
        Create a closed triad.
        
        Args:
            root: Root note name (e.g., 'C', 'F#', 'Bb')
            triad_type: 'major', 'minor', 'dim', 'aug', 'sus2', 'sus4'
            octave: Octave for root note
            
        Returns:
            Triad in closed position
        """
        return create_triad(root, triad_type, octave)
    
    def to_open_voicing(
        self,
        triad: Triad,
        voicing: str = 'drop2'
    ) -> Triad:
        """
        Convert a closed triad to open voicing.
        
        Args:
            triad: Source triad
            voicing: 'drop2', 'drop3', or 'super_open'
            
        Returns:
            Triad in open voicing
        """
        voicing_map = {
            'drop2': DropVoicing.DROP2,
            'drop3': DropVoicing.DROP3,
            'super_open': DropVoicing.SUPER_OPEN
        }
        dv = voicing_map.get(voicing, DropVoicing.DROP2)
        return self.converter.convert(triad, dv)
    
    def get_all_inversions(
        self,
        triad: Triad,
        open_voicing: bool = True
    ) -> Dict[str, Triad]:
        """
        Get all inversions of a triad.
        
        Args:
            triad: Source triad
            open_voicing: If True, return open-position inversions
            
        Returns:
            Dictionary mapping inversion names to triads
        """
        if open_voicing:
            return self.inversion_engine.all_inversions(triad)
        
        return {
            'root': triad.set_inversion(Inversion.ROOT),
            'first': triad.set_inversion(Inversion.FIRST),
            'second': triad.set_inversion(Inversion.SECOND)
        }
    
    # =========================================================================
    # Scale and Progression Operations
    # =========================================================================
    
    def generate_scale_triads(
        self,
        root: str = 'C',
        scale_name: str = 'ionian',
        open_voicing: bool = True
    ) -> EngineResult:
        """
        Generate triads for all degrees of a scale.
        
        Args:
            root: Root of the scale
            scale_name: Scale name (e.g., 'ionian', 'dorian', 'melodic_minor')
            open_voicing: If True, return open-position triads
            
        Returns:
            EngineResult containing list of triads
        """
        self.scale_mapper = ScaleMapper(root)
        triads = self.scale_mapper.get_diatonic_triads(scale_name)
        
        if open_voicing:
            triads = [self.inversion_engine.open_root(t) for t in triads]
        
        return EngineResult(
            success=True,
            operation='generate_scale_triads',
            data=triads,
            message=f"Generated {len(triads)} triads in {root} {scale_name}",
            metadata={
                'root': root,
                'scale': scale_name,
                'count': len(triads)
            }
        )
    
    def parse_progression(
        self,
        chord_symbols: List[str],
        octave: int = 4
    ) -> EngineResult:
        """
        Parse a chord progression into triads.
        
        Args:
            chord_symbols: List of chord symbols (e.g., ['Dm', 'G', 'C'])
            octave: Base octave
            
        Returns:
            EngineResult containing list of triads
        """
        triads = self.scale_mapper.get_triads_from_progression(chord_symbols, octave)
        
        return EngineResult(
            success=True,
            operation='parse_progression',
            data=triads,
            message=f"Parsed {len(triads)} chords",
            metadata={'symbols': chord_symbols}
        )
    
    # =========================================================================
    # Voice Leading Operations
    # =========================================================================
    
    def voice_lead(
        self,
        source: Triad,
        target: Triad,
        mode: Optional[str] = None
    ) -> VoiceLeadingResult:
        """
        Voice lead between two triads.
        
        Args:
            source: Starting triad
            target: Target triad
            mode: Optional mode override ('functional', 'modal', 'counterpoint', 'orchestration')
            
        Returns:
            VoiceLeadingResult with optimal voicing
        """
        mode_override = None
        if mode:
            mode_map = {
                'functional': VLMode.FUNCTIONAL,
                'modal': VLMode.MODAL,
                'counterpoint': VLMode.COUNTERPOINT,
                'orchestration': VLMode.ORCHESTRATION
            }
            mode_override = mode_map.get(mode)
        
        return self.voice_leading.voice_lead(source, target, mode_override)
    
    def voice_lead_progression(
        self,
        chord_symbols: List[str],
        open_voicing: bool = True,
        mode: Optional[str] = None
    ) -> EngineResult:
        """
        Voice lead an entire chord progression.
        
        Args:
            chord_symbols: List of chord symbols
            open_voicing: Start with open voicings
            mode: Voice leading mode
            
        Returns:
            EngineResult with voice-led triads and analysis
        """
        triads = self.scale_mapper.get_triads_from_progression(chord_symbols)
        
        if open_voicing:
            triads[0] = self.inversion_engine.open_root(triads[0])
        
        mode_override = None
        if mode:
            mode_map = {
                'functional': VLMode.FUNCTIONAL,
                'modal': VLMode.MODAL,
                'counterpoint': VLMode.COUNTERPOINT,
                'orchestration': VLMode.ORCHESTRATION
            }
            mode_override = mode_map.get(mode)
        
        results = self.voice_leading.voice_lead_progression(triads, mode_override)
        
        # Collect final voiced triads
        voiced_triads = [triads[0]] + [r.target for r in results]
        
        return EngineResult(
            success=True,
            operation='voice_lead_progression',
            data={
                'triads': voiced_triads,
                'voice_leading': results
            },
            message=f"Voice led {len(chord_symbols)} chords",
            metadata={
                'symbols': chord_symbols,
                'mode': mode or self.config.mode
            }
        )
    
    # =========================================================================
    # Shape Bundles and Patterns
    # =========================================================================
    
    def get_shape_bundles(
        self,
        triads: List[Triad]
    ) -> List[ShapeBundle]:
        """
        Create shape bundles for a list of triads.
        
        Args:
            triads: List of triads
            
        Returns:
            List of ShapeBundle objects
        """
        return [ShapeBundle.from_triad(t) for t in triads]
    
    def generate_patterns(
        self,
        triad: Triad,
        pattern_types: Optional[List[str]] = None
    ) -> List[MelodicPattern]:
        """
        Generate melodic patterns from a triad.
        
        Args:
            triad: Source triad
            pattern_types: Optional list of pattern types to generate
            
        Returns:
            List of MelodicPattern objects
        """
        if pattern_types is None:
            return self.pattern_gen.all_patterns(triad)
        
        patterns = []
        for pt in pattern_types:
            if pt.startswith('arpeggio'):
                # Parse arpeggio type
                arp_type = pt.split('_')[1] if '_' in pt else 'up'
                arp_map = {
                    'up': ArpeggioPattern.UP,
                    'down': ArpeggioPattern.DOWN,
                    'up_down': ArpeggioPattern.UP_DOWN,
                    'down_up': ArpeggioPattern.DOWN_UP
                }
                patterns.append(self.pattern_gen.arpeggio(
                    triad, arp_map.get(arp_type, ArpeggioPattern.UP)
                ))
            elif pt == 'wave':
                patterns.append(self.pattern_gen.wave(triad))
            elif pt == 'pendulum':
                patterns.append(self.pattern_gen.pendulum(triad))
        
        return patterns
    
    # =========================================================================
    # Special Engines
    # =========================================================================
    
    def generate_two_five_one(
        self,
        key: str = 'C',
        minor: bool = False
    ) -> TwoFiveOneResult:
        """
        Generate a ii-V-I progression with optimal voice leading.
        
        Args:
            key: Target key
            minor: If True, generate ii-V-i
            
        Returns:
            TwoFiveOneResult with voiced triads
        """
        return self.two_five_one.generate(key, minor=minor)
    
    def create_chord_melody(
        self,
        melody: List[Note],
        chord_symbols: Optional[List[str]] = None
    ):
        """
        Create chord-melody voicings for a melody.
        
        Args:
            melody: List of melody notes
            chord_symbols: Optional chord symbols
            
        Returns:
            List of ChordMelodyVoicing objects
        """
        return self.chord_melody.harmonize_melody(melody, chord_symbols)
    
    def create_triad_pair(
        self,
        root: str,
        pair_type: str = 'klemons'
    ):
        """
        Create a triad pair for improvisation.
        
        Args:
            root: Root note
            pair_type: 'klemons', 'diatonic', or 'ust'
            
        Returns:
            TriadPair object
        """
        if pair_type == 'klemons':
            return self.triad_pair.create_klemons_pair(root)
        # Add other pair types as needed
        return self.triad_pair.create_klemons_pair(root)
    
    def generate_counterpoint(
        self,
        triads: List[Triad]
    ):
        """
        Generate three-voice counterpoint from triads.
        
        Args:
            triads: List of triads
            
        Returns:
            CounterpointResult with three voice lines
        """
        return self.counterpoint.generate_counterpoint(triads)
    
    def orchestrate(
        self,
        triads: List[Triad],
        instruments: Optional[Dict[str, str]] = None
    ):
        """
        Orchestrate triads for instruments.
        
        Args:
            triads: List of triads
            instruments: Optional instrument assignments
            
        Returns:
            List of OrchestrationVoicing objects
        """
        return self.orchestration.orchestrate_progression(triads, instruments)
    
    # =========================================================================
    # Export Operations
    # =========================================================================
    
    def export_musicxml(
        self,
        triads: List[Triad],
        filename: str,
        title: str = "Open Triad Study"
    ) -> str:
        """
        Export triads to MusicXML format.
        
        Args:
            triads: Triads to export
            filename: Output filename
            title: Title for the score
            
        Returns:
            Path to created file
        """
        exporter = MusicXMLExporter(ExportOptions(title=title))
        return exporter.export_triads(triads, filename)
    
    def export_tab(
        self,
        triads: List[Triad],
        filename: str
    ) -> str:
        """
        Export triads to guitar TAB format.
        
        Args:
            triads: Triads to export
            filename: Output filename
            
        Returns:
            Path to created file
        """
        exporter = TABExporter()
        return exporter.export_triads(triads, filename)
    
    def export_json(
        self,
        triads: List[Triad],
        filename: str
    ) -> str:
        """
        Export triads to JSON format.
        
        Args:
            triads: Triads to export
            filename: Output filename
            
        Returns:
            Path to created file
        """
        return NotationExporter.to_json(triads, filename)
    
    def export_etude(
        self,
        title: str,
        key: str,
        triads: List[Triad],
        filename: str,
        include_patterns: bool = True
    ) -> str:
        """
        Export a complete practice etude.
        
        Args:
            title: Etude title
            key: Key/scale
            triads: Triads to include
            filename: Output filename
            include_patterns: Include melodic patterns
            
        Returns:
            Path to created file
        """
        bundles = self.get_shape_bundles(triads)
        
        patterns = None
        if include_patterns and triads:
            patterns = self.generate_patterns(triads[0])[:5]  # First 5 patterns
        
        builder = PDFEtudeBuilder()
        return builder.export_etude(
            title=title,
            scale_key=key,
            shapes=bundles,
            filename=filename,
            patterns=patterns
        )
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_scale(self, name: str) -> Optional[Scale]:
        """Get a scale definition from the tonality vault."""
        return self.tonality_vault.get_scale(name)
    
    def list_scales(self, category: Optional[str] = None) -> List[str]:
        """List available scale names."""
        from .tonality_vault import ScaleCategory
        
        if category:
            cat_map = {
                'diatonic': ScaleCategory.DIATONIC,
                'melodic_minor': ScaleCategory.MELODIC_MINOR,
                'harmonic_minor': ScaleCategory.HARMONIC_MINOR,
                'symmetric': ScaleCategory.SYMMETRIC,
                'pentatonic': ScaleCategory.PENTATONIC,
                'bebop': ScaleCategory.BEBOP,
                'exotic': ScaleCategory.EXOTIC
            }
            cat = cat_map.get(category)
            return self.tonality_vault.list_scales(cat)
        
        return self.tonality_vault.list_scales()
    
    def set_config(self, **kwargs):
        """Update engine configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Reinitialize modules with new config
        self._init_modules()
    
    def get_version(self) -> str:
        """Get engine version."""
        return self.VERSION
    
    def __repr__(self) -> str:
        return f"OpenTriadEngine(v{self.VERSION}, mode={self.config.mode})"


# =========================================================================
# Module-Level Functions for External Generators
# =========================================================================

def quick_open_triads(
    root: str,
    scale: str = 'ionian'
) -> List[Triad]:
    """
    Quick function to generate open triads for a scale.
    
    Designed for easy integration with other generators.
    
    Args:
        root: Root note
        scale: Scale name
        
    Returns:
        List of open-position triads
    """
    engine = OpenTriadEngine()
    result = engine.generate_scale_triads(root, scale, open_voicing=True)
    return result.data


def quick_voice_lead(
    chord_symbols: List[str]
) -> List[Triad]:
    """
    Quick function to voice lead a progression.
    
    Args:
        chord_symbols: List of chord symbols
        
    Returns:
        List of voice-led open triads
    """
    engine = OpenTriadEngine()
    result = engine.voice_lead_progression(chord_symbols)
    return result.data['triads']


def quick_two_five_one(key: str = 'C') -> List[Triad]:
    """
    Quick function to generate a ii-V-I in open triads.
    
    Args:
        key: Target key
        
    Returns:
        List of [ii, V, I] triads
    """
    engine = OpenTriadEngine()
    result = engine.generate_two_five_one(key)
    return [result.ii, result.V, result.I]

