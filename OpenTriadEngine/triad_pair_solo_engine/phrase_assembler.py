"""
Phrase Assembler for Triad Pair Solo Engine
=============================================

Builds complete solo phrases by assembling:
- Open-triad melodic cells
- Triad-pair alternation
- Rhythmic contour
- VL-SM transitions
- Optional chromatic approach tones
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum

try:
    from .inputs import SoloEngineConfig, ContourType, SoloMode, RhythmicStyle
    from .triad_pairs import TriadPair, TriadPairSelector
    from .patterns import PatternNote, MelodicCell, SoloPatternGenerator, PatternType
    from .rhythm import SoloRhythmEngine, RhythmicTemplate
    from .voice_leading import SoloVoiceLeadingEngine, VoiceLeadingResult
except ImportError:
    from inputs import SoloEngineConfig, ContourType, SoloMode, RhythmicStyle
    from triad_pairs import TriadPair, TriadPairSelector
    from patterns import PatternNote, MelodicCell, SoloPatternGenerator, PatternType
    from rhythm import SoloRhythmEngine, RhythmicTemplate
    from voice_leading import SoloVoiceLeadingEngine, VoiceLeadingResult


class PhraseStructure(Enum):
    """Types of phrase structures."""
    MOTIF_1BAR = "motif_1bar"
    CALL_2BAR = "call_2bar"
    RESPONSE_2BAR = "response_2bar"
    STRUCTURED_4BAR = "structured_4bar"
    STRUCTURED_8BAR = "structured_8bar"


@dataclass
class SoloPhrase:
    """
    A complete solo phrase.
    
    Attributes:
        notes: All notes in the phrase
        cells: Component melodic cells
        structure: Phrase structure type
        triad_pairs: Triad pairs used
        bar_count: Number of bars
        rhythmic_style: Applied rhythmic style
        voice_leading_analysis: VL-SM analysis results
        metadata: Additional phrase metadata
    """
    notes: List[PatternNote]
    cells: List[MelodicCell]
    structure: PhraseStructure
    triad_pairs: List[TriadPair]
    bar_count: int
    rhythmic_style: RhythmicStyle
    voice_leading_analysis: List[VoiceLeadingResult] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def total_duration(self) -> float:
        """Get total duration in beats."""
        return sum(n.duration for n in self.notes)
    
    def get_pitches(self) -> List[int]:
        """Get list of all MIDI pitches."""
        return [n.pitch for n in self.notes]
    
    def get_pitch_range(self) -> Tuple[int, int]:
        """Get lowest and highest pitches."""
        pitches = self.get_pitches()
        return (min(pitches), max(pitches)) if pitches else (60, 60)


class PhraseAssembler:
    """
    Assembles complete solo phrases from components.
    """
    
    def __init__(self, config: SoloEngineConfig):
        """
        Initialize the phrase assembler.
        
        Args:
            config: Solo engine configuration
        """
        self.config = config
        self.pattern_generator = SoloPatternGenerator(
            base_octave=4,
            seed=config.seed,
            difficulty=config.difficulty
        )
        self.rhythm_engine = SoloRhythmEngine(
            default_style=config.rhythmic_style,
            difficulty=config.difficulty,
            seed=config.seed
        )
        self.vl_engine = SoloVoiceLeadingEngine(mode=config.mode)
    
    def build_phrase(
        self,
        triad_pairs: List[TriadPair],
        structure: PhraseStructure = PhraseStructure.STRUCTURED_4BAR
    ) -> SoloPhrase:
        """
        Build a complete solo phrase.
        
        Args:
            triad_pairs: Triad pairs to use
            structure: Desired phrase structure
        
        Returns:
            Complete SoloPhrase
        """
        if structure == PhraseStructure.MOTIF_1BAR:
            return self._build_1bar_motif(triad_pairs)
        elif structure == PhraseStructure.CALL_2BAR:
            return self._build_2bar_call(triad_pairs)
        elif structure == PhraseStructure.RESPONSE_2BAR:
            return self._build_2bar_response(triad_pairs)
        elif structure == PhraseStructure.STRUCTURED_4BAR:
            return self._build_4bar_phrase(triad_pairs)
        else:  # 8-bar
            return self._build_8bar_phrase(triad_pairs)
    
    def _build_1bar_motif(self, triad_pairs: List[TriadPair]) -> SoloPhrase:
        """Build a 1-bar motif."""
        if not triad_pairs:
            triad_pairs = [self._default_triad_pair()]
        
        pair = triad_pairs[0]
        
        # Generate pattern based on contour
        cell = self.pattern_generator.generate_for_contour(
            pair, self.config.contour, duration=0.5, string_set=self.config.string_set
        )
        
        # Apply rhythm
        template = self.rhythm_engine.get_template(self.config.rhythmic_style, 4.0)
        rhythmized_cell = self.rhythm_engine.apply_rhythm_to_cell(cell, template)
        
        # Fit to 1 bar
        notes = self.pattern_generator.stitch_cells_to_bar([rhythmized_cell], 4.0)
        
        return SoloPhrase(
            notes=notes,
            cells=[rhythmized_cell],
            structure=PhraseStructure.MOTIF_1BAR,
            triad_pairs=[pair],
            bar_count=1,
            rhythmic_style=self.config.rhythmic_style,
            metadata={"motif_type": rhythmized_cell.pattern_type.value}
        )
    
    def _build_2bar_call(self, triad_pairs: List[TriadPair]) -> SoloPhrase:
        """Build a 2-bar 'call' phrase (ascending, opening)."""
        pairs = triad_pairs[:2] if len(triad_pairs) >= 2 else [triad_pairs[0]] * 2
        
        cells = []
        vl_analysis = []
        
        # Bar 1: Ascending arpeggio
        cell1 = self.pattern_generator.generate_up_arpeggio(
            pairs[0], duration=0.5, string_set=self.config.string_set
        )
        cells.append(cell1)
        
        # Bar 2: Wave or continuation
        if len(pairs) > 1:
            cell2 = self.pattern_generator.generate_wave(
                pairs[1], duration=0.5, string_set=self.config.string_set
            )
            
            # Analyze voice-leading between bars
            vl = self.vl_engine.analyze_transition(
                pairs[0].triad_b, pairs[1].triad_a
            )
            vl_analysis.append(vl)
        else:
            cell2 = self.pattern_generator.generate_rotation(
                pairs[0], "132", duration=0.5, string_set=self.config.string_set
            )
        cells.append(cell2)
        
        # Apply rhythm
        templates = self.rhythm_engine.generate_phrase_rhythm(2, self.config.rhythmic_style)
        rhythmized_cells = [
            self.rhythm_engine.apply_rhythm_to_cell(cell, template)
            for cell, template in zip(cells, templates)
        ]
        
        # Assemble notes
        all_notes = []
        for cell in rhythmized_cells:
            all_notes.extend(cell.notes)
        
        return SoloPhrase(
            notes=all_notes,
            cells=rhythmized_cells,
            structure=PhraseStructure.CALL_2BAR,
            triad_pairs=pairs,
            bar_count=2,
            rhythmic_style=self.config.rhythmic_style,
            voice_leading_analysis=vl_analysis,
            metadata={"phrase_type": "call", "direction": "ascending"}
        )
    
    def _build_2bar_response(self, triad_pairs: List[TriadPair]) -> SoloPhrase:
        """Build a 2-bar 'response' phrase (descending, closing)."""
        pairs = triad_pairs[:2] if len(triad_pairs) >= 2 else [triad_pairs[0]] * 2
        
        cells = []
        vl_analysis = []
        
        # Bar 1: Descending or interval skip
        cell1 = self.pattern_generator.generate_down_arpeggio(
            pairs[0], duration=0.5, string_set=self.config.string_set
        )
        cells.append(cell1)
        
        # Bar 2: Resolution pattern
        if len(pairs) > 1:
            cell2 = self.pattern_generator.generate_pivot_tone(
                pairs[1], pivot_voice=1, duration=0.5, string_set=self.config.string_set
            )
            
            vl = self.vl_engine.analyze_transition(
                pairs[0].triad_b, pairs[1].triad_a
            )
            vl_analysis.append(vl)
        else:
            cell2 = self.pattern_generator.generate_rotation(
                pairs[0], "321", duration=0.5, string_set=self.config.string_set
            )
        cells.append(cell2)
        
        # Apply rhythm
        templates = self.rhythm_engine.generate_phrase_rhythm(2, self.config.rhythmic_style)
        rhythmized_cells = [
            self.rhythm_engine.apply_rhythm_to_cell(cell, template)
            for cell, template in zip(cells, templates)
        ]
        
        all_notes = []
        for cell in rhythmized_cells:
            all_notes.extend(cell.notes)
        
        return SoloPhrase(
            notes=all_notes,
            cells=rhythmized_cells,
            structure=PhraseStructure.RESPONSE_2BAR,
            triad_pairs=pairs,
            bar_count=2,
            rhythmic_style=self.config.rhythmic_style,
            voice_leading_analysis=vl_analysis,
            metadata={"phrase_type": "response", "direction": "descending"}
        )
    
    def _build_4bar_phrase(self, triad_pairs: List[TriadPair]) -> SoloPhrase:
        """Build a 4-bar structured phrase (AABA or similar)."""
        # Ensure we have enough pairs
        while len(triad_pairs) < 4:
            triad_pairs = triad_pairs + triad_pairs
        pairs = triad_pairs[:4]
        
        cells = []
        vl_analysis = []
        
        # Bar 1: Opening (ascending)
        cells.append(self.pattern_generator.generate_up_arpeggio(
            pairs[0], duration=0.5, string_set=self.config.string_set
        ))
        
        # Bar 2: Development (alternating)
        cells.append(self.pattern_generator.generate_alternating(
            pairs[1], duration=0.5, repetitions=1, string_set=self.config.string_set
        ))
        vl = self.vl_engine.analyze_transition(pairs[0].triad_b, pairs[1].triad_a)
        vl_analysis.append(vl)
        
        # Bar 3: Contrast (wave or skip)
        cells.append(self.pattern_generator.generate_interval_skip(
            pairs[2], skip_size=2, duration=0.5, string_set=self.config.string_set
        ))
        vl = self.vl_engine.analyze_transition(pairs[1].triad_b, pairs[2].triad_a)
        vl_analysis.append(vl)
        
        # Bar 4: Resolution (descending)
        cells.append(self.pattern_generator.generate_down_arpeggio(
            pairs[3], duration=0.5, string_set=self.config.string_set
        ))
        vl = self.vl_engine.analyze_transition(pairs[2].triad_b, pairs[3].triad_a)
        vl_analysis.append(vl)
        
        # Apply voice-leading adjustments based on mode
        if self.config.mode == SoloMode.INTERVALLIC:
            # Apply SISM spacing for tension
            cells = [self.vl_engine.apply_sism_spacing(cell, 0.7) for cell in cells]
        
        # Apply rhythm
        templates = self.rhythm_engine.generate_phrase_rhythm(
            4, self.config.rhythmic_style, with_variations=True
        )
        rhythmized_cells = [
            self.rhythm_engine.apply_rhythm_to_cell(cell, template)
            for cell, template in zip(cells, templates)
        ]
        
        # Optional chromatic approaches for advanced difficulty
        all_notes = []
        for cell in rhythmized_cells:
            if self.config.difficulty.value == "advanced":
                enhanced_notes = self.vl_engine.apply_chromatic_approach(cell.notes, 0.2)
                all_notes.extend(enhanced_notes)
            else:
                all_notes.extend(cell.notes)
        
        return SoloPhrase(
            notes=all_notes,
            cells=rhythmized_cells,
            structure=PhraseStructure.STRUCTURED_4BAR,
            triad_pairs=pairs,
            bar_count=4,
            rhythmic_style=self.config.rhythmic_style,
            voice_leading_analysis=vl_analysis,
            metadata={
                "phrase_type": "structured",
                "form": "ABCD",
                "mode": self.config.mode.value
            }
        )
    
    def _build_8bar_phrase(self, triad_pairs: List[TriadPair]) -> SoloPhrase:
        """Build an 8-bar structured phrase."""
        # Build two 4-bar phrases
        while len(triad_pairs) < 8:
            triad_pairs = triad_pairs + triad_pairs
        pairs = triad_pairs[:8]
        
        # First 4 bars: Call
        call_phrase = self._build_4bar_phrase(pairs[:4])
        
        # Second 4 bars: Response/development
        response_pairs = pairs[4:8]
        cells = []
        vl_analysis = list(call_phrase.voice_leading_analysis)
        
        # Bar 5: Echo of bar 1 (up arpeggio)
        cells.append(self.pattern_generator.generate_up_arpeggio(
            response_pairs[0], duration=0.5, string_set=self.config.string_set
        ))
        
        # Bar 6: Variation
        cells.append(self.pattern_generator.generate_rotation(
            response_pairs[1], "312", duration=0.5, string_set=self.config.string_set
        ))
        
        # Bar 7: Climax (wave with high tension)
        climax_cell = self.pattern_generator.generate_wave(
            response_pairs[2], duration=0.5, string_set=self.config.string_set
        )
        cells.append(self.vl_engine.apply_sism_spacing(climax_cell, 0.9))
        
        # Bar 8: Resolution
        cells.append(self.pattern_generator.generate_pivot_tone(
            response_pairs[3], duration=0.5, string_set=self.config.string_set
        ))
        
        # Apply rhythm
        templates = self.rhythm_engine.generate_phrase_rhythm(
            4, self.config.rhythmic_style, with_variations=True
        )
        rhythmized_cells = [
            self.rhythm_engine.apply_rhythm_to_cell(cell, template)
            for cell, template in zip(cells, templates)
        ]
        
        # Combine with first 4 bars
        all_notes = list(call_phrase.notes)
        for cell in rhythmized_cells:
            all_notes.extend(cell.notes)
        
        all_cells = list(call_phrase.cells) + rhythmized_cells
        
        return SoloPhrase(
            notes=all_notes,
            cells=all_cells,
            structure=PhraseStructure.STRUCTURED_8BAR,
            triad_pairs=pairs,
            bar_count=8,
            rhythmic_style=self.config.rhythmic_style,
            voice_leading_analysis=vl_analysis,
            metadata={
                "phrase_type": "structured",
                "form": "ABCD-ABCD'",
                "mode": self.config.mode.value,
                "climax_bar": 7
            }
        )
    
    def build_call_and_response(
        self,
        triad_pairs: List[TriadPair]
    ) -> Tuple[SoloPhrase, SoloPhrase]:
        """
        Build a call-and-response phrase pair.
        
        Args:
            triad_pairs: Triad pairs to use
        
        Returns:
            Tuple of (call_phrase, response_phrase)
        """
        call = self._build_2bar_call(triad_pairs[:len(triad_pairs)//2])
        response = self._build_2bar_response(triad_pairs[len(triad_pairs)//2:])
        return call, response
    
    def _default_triad_pair(self) -> TriadPair:
        """Create a default triad pair."""
        return TriadPair(
            triad_a=(self.config.key, "major"),
            triad_b=(self._get_note_at_interval(self.config.key, 2), "minor"),
            relationship="diatonic",
            source_scale=f"{self.config.key}_{self.config.scale}"
        )
    
    def _get_note_at_interval(self, root: str, semitones: int) -> str:
        """Get note at interval from root."""
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        enharmonics = {"Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#",
                       "Ab": "G#", "Bb": "A#", "Cb": "B"}
        root = enharmonics.get(root, root)
        try:
            root_idx = notes.index(root)
            return notes[(root_idx + semitones) % 12]
        except ValueError:
            return "C"
    
    def assemble_from_cells(
        self,
        cells: List[MelodicCell],
        apply_rhythm: bool = True
    ) -> SoloPhrase:
        """
        Assemble a phrase from pre-generated melodic cells.
        
        Args:
            cells: List of MelodicCell objects
            apply_rhythm: Whether to apply rhythmic templates
        
        Returns:
            Assembled SoloPhrase
        """
        if apply_rhythm:
            templates = self.rhythm_engine.generate_phrase_rhythm(
                len(cells), self.config.rhythmic_style
            )
            rhythmized_cells = [
                self.rhythm_engine.apply_rhythm_to_cell(cell, template)
                for cell, template in zip(cells, templates)
            ]
        else:
            rhythmized_cells = cells
        
        all_notes = []
        triad_pairs = []
        for cell in rhythmized_cells:
            all_notes.extend(cell.notes)
            if cell.triad_pair:
                triad_pairs.append(cell.triad_pair)
        
        # Determine structure based on length
        if len(cells) <= 1:
            structure = PhraseStructure.MOTIF_1BAR
        elif len(cells) <= 2:
            structure = PhraseStructure.CALL_2BAR
        elif len(cells) <= 4:
            structure = PhraseStructure.STRUCTURED_4BAR
        else:
            structure = PhraseStructure.STRUCTURED_8BAR
        
        return SoloPhrase(
            notes=all_notes,
            cells=rhythmized_cells,
            structure=structure,
            triad_pairs=triad_pairs,
            bar_count=len(cells),
            rhythmic_style=self.config.rhythmic_style
        )

