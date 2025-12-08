"""
Harmonic Material Generation Module
====================================

Uses the Open Triad Engine to generate harmonic material for etudes.
Handles closed→open conversion, inversions, and scale mapping.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import sys
from pathlib import Path

# Add parent to path for engine imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from open_triad_engine import (
    OpenTriadEngine, create_engine,
    Note, Triad, TriadType, Inversion, VoicingType
)
from open_triad_engine.transformations import InversionEngine, ScaleMapper, ClosedToOpenConverter
from open_triad_engine.voice_leading import VoiceLeadingSmartModule, VLMode
from open_triad_engine.special_engines import TwoFiveOneEngine, ChordMelodyEngine, OpenTriadPairEngine

from .inputs import EtudeConfig, EtudeType, EtudeMode, StringSet


@dataclass
class HarmonicCell:
    """
    A single harmonic cell containing a triad with metadata.
    
    Attributes:
        triad: The open triad
        scale_degree: Degree in the scale (1-7)
        function: Harmonic function (tonic, subdominant, dominant)
        inversion_name: Name of the inversion used
        voice_leading_from: Voice leading info from previous cell
    """
    triad: Triad
    scale_degree: Optional[int] = None
    function: Optional[str] = None
    inversion_name: str = "root"
    voice_leading_from: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.triad.symbol,
            'voices': [str(v) for v in self.triad.voices],
            'scale_degree': self.scale_degree,
            'function': self.function,
            'inversion': self.inversion_name,
            'voicing_type': self.triad.voicing_type.value,
        }


@dataclass
class HarmonicMaterial:
    """
    Complete harmonic material for an etude.
    
    Attributes:
        cells: List of harmonic cells
        key: Key center
        scale: Scale used
        mode: Voice-leading mode used
    """
    cells: List[HarmonicCell]
    key: str
    scale: str
    mode: str
    
    @property
    def triads(self) -> List[Triad]:
        """Get all triads from cells."""
        return [cell.triad for cell in self.cells]
    
    def get_cell(self, index: int) -> Optional[HarmonicCell]:
        """Get a cell by index."""
        if 0 <= index < len(self.cells):
            return self.cells[index]
        return None
    
    def to_dict(self) -> Dict:
        return {
            'key': self.key,
            'scale': self.scale,
            'mode': self.mode,
            'cells': [cell.to_dict() for cell in self.cells]
        }


class HarmonicGenerator:
    """
    Generates harmonic material using the Open Triad Engine.
    
    Handles:
    - Closed → open triad conversion
    - Inversion set creation
    - Scale/progression mapping
    - Engine mode selection
    """
    
    # Harmonic function mapping for diatonic chords
    DIATONIC_FUNCTIONS = {
        1: 'tonic',
        2: 'subdominant',
        3: 'tonic',      # iii is tonic substitute
        4: 'subdominant',
        5: 'dominant',
        6: 'tonic',      # vi is tonic substitute
        7: 'dominant',   # vii° is dominant function
    }
    
    def __init__(self, config: EtudeConfig):
        """
        Initialize the harmonic generator.
        
        Args:
            config: Etude configuration
        """
        self.config = config
        
        # Initialize the Open Triad Engine
        self.engine = self._create_engine()
        
        # Initialize sub-engines
        self.scale_mapper = ScaleMapper(config.key)
        self.inversion_engine = InversionEngine()
        self.converter = ClosedToOpenConverter()
        
        # Voice-leading module
        vl_mode = self._get_vl_mode()
        self.voice_leading = VoiceLeadingSmartModule(mode=vl_mode)
        
        # Special engines
        self.two_five_one = TwoFiveOneEngine()
        self.chord_melody = ChordMelodyEngine(config.scale, config.key)
        self.triad_pair = OpenTriadPairEngine()
    
    def _create_engine(self) -> OpenTriadEngine:
        """Create configured Open Triad Engine."""
        mode_map = {
            EtudeMode.FUNCTIONAL: 'harmonic',
            EtudeMode.MODAL: 'melodic',
            EtudeMode.INTERVALLIC: 'melodic',
        }
        
        engine_mode = mode_map.get(self.config._mode_enum, 'melodic')
        
        return create_engine(
            mode=engine_mode,
            priority='smooth' if self.config._mode_enum == EtudeMode.FUNCTIONAL else 'intervallic'
        )
    
    def _get_vl_mode(self) -> VLMode:
        """Get voice-leading mode from config."""
        mode_map = {
            EtudeMode.FUNCTIONAL: VLMode.FUNCTIONAL,
            EtudeMode.MODAL: VLMode.MODAL,
            EtudeMode.INTERVALLIC: VLMode.MODAL,  # Use modal for intervallic freedom
        }
        return mode_map.get(self.config._mode_enum, VLMode.FUNCTIONAL)
    
    def generate(self) -> HarmonicMaterial:
        """
        Generate harmonic material based on configuration.
        
        Returns:
            HarmonicMaterial with all cells
        """
        etude_type = self.config._etude_type_enum
        
        if etude_type == EtudeType.TWO_FIVE_ONE:
            return self._generate_two_five_one()
        elif etude_type == EtudeType.CHORD_MELODY:
            return self._generate_chord_melody()
        elif etude_type == EtudeType.SCALAR:
            return self._generate_scalar()
        elif etude_type == EtudeType.INVERSION_CYCLE:
            return self._generate_inversion_cycle()
        elif etude_type == EtudeType.INTERVALLIC:
            return self._generate_intervallic()
        else:
            return self._generate_diatonic()
    
    def _generate_diatonic(self) -> HarmonicMaterial:
        """Generate diatonic triads with voice leading."""
        # Get diatonic triads from scale
        result = self.engine.generate_scale_triads(self.config.key, self.config.scale)
        
        cells = []
        prev_triad = None
        
        for i, triad in enumerate(result.data):
            degree = i + 1
            
            # Apply voice leading from previous
            vl_info = None
            if prev_triad is not None:
                vl_result = self.voice_leading.voice_lead(prev_triad, triad)
                triad = vl_result.target
                vl_info = {
                    'narrative': vl_result.narrative,
                    'score': vl_result.score,
                }
            
            cell = HarmonicCell(
                triad=triad,
                scale_degree=degree,
                function=self.DIATONIC_FUNCTIONS.get(degree),
                inversion_name=self._get_inversion_name(triad),
                voice_leading_from=vl_info
            )
            cells.append(cell)
            prev_triad = triad
        
        return HarmonicMaterial(
            cells=cells,
            key=self.config.key,
            scale=self.config.scale,
            mode=self.config.mode
        )
    
    def _generate_scalar(self) -> HarmonicMaterial:
        """Generate scalar etude with all inversions through scale."""
        result = self.engine.generate_scale_triads(self.config.key, self.config.scale)
        
        cells = []
        inversions = ['open_root', 'open_first', 'open_second']
        
        for cycle in range(self.config.length // 7 + 1):
            for i, triad in enumerate(result.data):
                if len(cells) >= self.config.length:
                    break
                
                # Cycle through inversions
                inv_name = inversions[cycle % 3]
                
                if inv_name == 'open_root':
                    voiced = self.inversion_engine.open_root(triad)
                elif inv_name == 'open_first':
                    voiced = self.inversion_engine.open_first(triad)
                else:
                    voiced = self.inversion_engine.open_second(triad)
                
                cell = HarmonicCell(
                    triad=voiced,
                    scale_degree=i + 1,
                    function=self.DIATONIC_FUNCTIONS.get(i + 1),
                    inversion_name=inv_name
                )
                cells.append(cell)
        
        return HarmonicMaterial(
            cells=cells[:self.config.length],
            key=self.config.key,
            scale=self.config.scale,
            mode=self.config.mode
        )
    
    def _generate_inversion_cycle(self) -> HarmonicMaterial:
        """Generate inversion cycle etude."""
        # Use first few chords of scale
        result = self.engine.generate_scale_triads(self.config.key, self.config.scale)
        base_triads = result.data[:4]  # I, ii, iii, IV
        
        cells = []
        inversions = ['open_root', 'open_first', 'open_second']
        
        for triad in base_triads:
            for inv_name in inversions:
                if len(cells) >= self.config.length:
                    break
                
                if inv_name == 'open_root':
                    voiced = self.inversion_engine.open_root(triad)
                elif inv_name == 'open_first':
                    voiced = self.inversion_engine.open_first(triad)
                else:
                    voiced = self.inversion_engine.open_second(triad)
                
                cell = HarmonicCell(
                    triad=voiced,
                    inversion_name=inv_name
                )
                cells.append(cell)
        
        return HarmonicMaterial(
            cells=cells,
            key=self.config.key,
            scale=self.config.scale,
            mode=self.config.mode
        )
    
    def _generate_two_five_one(self) -> HarmonicMaterial:
        """Generate ii-V-I etude with functional voice leading."""
        cells = []
        
        # Generate ii-V-I for the number of bars needed
        num_progressions = self.config.length // 3 + 1
        
        for _ in range(num_progressions):
            if len(cells) >= self.config.length:
                break
            
            result = self.two_five_one.generate(self.config.key)
            
            # Add ii
            cells.append(HarmonicCell(
                triad=result.ii,
                scale_degree=2,
                function='subdominant',
                inversion_name=self._get_inversion_name(result.ii),
                voice_leading_from=None
            ))
            
            if len(cells) >= self.config.length:
                break
            
            # Add V with voice leading info
            cells.append(HarmonicCell(
                triad=result.V,
                scale_degree=5,
                function='dominant',
                inversion_name=self._get_inversion_name(result.V),
                voice_leading_from={
                    'narrative': result.vl_ii_to_V.narrative,
                    'score': result.vl_ii_to_V.score,
                }
            ))
            
            if len(cells) >= self.config.length:
                break
            
            # Add I with voice leading info
            cells.append(HarmonicCell(
                triad=result.I,
                scale_degree=1,
                function='tonic',
                inversion_name=self._get_inversion_name(result.I),
                voice_leading_from={
                    'narrative': result.vl_V_to_I.narrative,
                    'score': result.vl_V_to_I.score,
                }
            ))
        
        return HarmonicMaterial(
            cells=cells[:self.config.length],
            key=self.config.key,
            scale=self.config.scale,
            mode='functional'
        )
    
    def _generate_chord_melody(self) -> HarmonicMaterial:
        """Generate chord-melody material."""
        # Generate diatonic material first
        diatonic = self._generate_diatonic()
        
        # For chord-melody, we keep the same harmonic structure
        # but will add melody notes in the pattern module
        return diatonic
    
    def _generate_intervallic(self) -> HarmonicMaterial:
        """Generate intervallic etude with triad pairs."""
        cells = []
        
        # Create triad pairs for each scale degree
        result = self.engine.generate_scale_triads(self.config.key, self.config.scale)
        
        for i in range(0, len(result.data) - 1, 2):
            if len(cells) >= self.config.length:
                break
            
            triad1 = result.data[i]
            triad2 = result.data[i + 1] if i + 1 < len(result.data) else result.data[0]
            
            # Create triad pair using engine
            pair = self.triad_pair.create_diatonic_pair(
                self.config.scale, self.config.key, i + 1, i + 2
            )
            
            cells.append(HarmonicCell(
                triad=pair.triad1,
                scale_degree=i + 1,
                inversion_name='open_root'
            ))
            
            if len(cells) < self.config.length:
                cells.append(HarmonicCell(
                    triad=pair.triad2,
                    scale_degree=i + 2,
                    inversion_name='open_root'
                ))
        
        return HarmonicMaterial(
            cells=cells,
            key=self.config.key,
            scale=self.config.scale,
            mode='intervallic'
        )
    
    def _get_inversion_name(self, triad: Triad) -> str:
        """Get the inversion name from a triad."""
        inv_map = {
            Inversion.ROOT: 'open_root',
            Inversion.FIRST: 'open_first',
            Inversion.SECOND: 'open_second',
        }
        return inv_map.get(triad.inversion, 'open_root')
    
    def get_all_inversions(self, triad: Triad) -> Dict[str, Triad]:
        """Get all open inversions for a triad."""
        return self.inversion_engine.all_inversions(triad)
    
    def voice_lead_cells(self, cells: List[HarmonicCell]) -> List[HarmonicCell]:
        """Apply voice leading between cells."""
        if len(cells) < 2:
            return cells
        
        result = [cells[0]]
        
        for i in range(1, len(cells)):
            prev = result[-1]
            curr = cells[i]
            
            # Apply voice leading
            vl_result = self.voice_leading.voice_lead(prev.triad, curr.triad)
            
            # Update cell with voiced triad
            new_cell = HarmonicCell(
                triad=vl_result.target,
                scale_degree=curr.scale_degree,
                function=curr.function,
                inversion_name=self._get_inversion_name(vl_result.target),
                voice_leading_from={
                    'narrative': vl_result.narrative,
                    'score': vl_result.score,
                }
            )
            result.append(new_cell)
        
        return result


def generate_harmonic_material(config: EtudeConfig) -> HarmonicMaterial:
    """
    Convenience function to generate harmonic material.
    
    Args:
        config: Etude configuration
        
    Returns:
        HarmonicMaterial
    """
    generator = HarmonicGenerator(config)
    return generator.generate()

