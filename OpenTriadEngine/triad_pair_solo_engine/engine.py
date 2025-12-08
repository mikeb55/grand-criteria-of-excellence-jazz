"""
Main Triad Pair Solo Engine
============================

The primary interface for generating intervallic, modern jazz solo lines
using triad pairs transformed into open triads.
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path

try:
    from .inputs import (
        SoloEngineConfig, TriadPairType, SoloMode, RhythmicStyle,
        ContourType, SoloDifficulty
    )
    from .triad_pairs import TriadPair, TriadPairSelector
    from .patterns import SoloPatternGenerator, MelodicCell, PatternType
    from .rhythm import SoloRhythmEngine
    from .voice_leading import SoloVoiceLeadingEngine, VoiceLeadingResult
    from .phrase_assembler import PhraseAssembler, SoloPhrase, PhraseStructure
    from .output import SoloOutputFormatter
except ImportError:
    from inputs import (
        SoloEngineConfig, TriadPairType, SoloMode, RhythmicStyle,
        ContourType, SoloDifficulty
    )
    from triad_pairs import TriadPair, TriadPairSelector
    from patterns import SoloPatternGenerator, MelodicCell, PatternType
    from rhythm import SoloRhythmEngine
    from voice_leading import SoloVoiceLeadingEngine, VoiceLeadingResult
    from phrase_assembler import PhraseAssembler, SoloPhrase, PhraseStructure
    from output import SoloOutputFormatter


class TriadPairSoloEngine:
    """
    Main engine for generating triad pair-based solo phrases.
    
    This engine integrates with Open Triad Engine v1.0 for:
    - Triad generation and transformation
    - Inversion logic
    - Voice-leading (VL-SM)
    - Scale mapping
    - Pattern generation
    
    Example usage:
        >>> engine = TriadPairSoloEngine(key="C", scale="dorian")
        >>> phrase = engine.generate_phrase(bars=4)
        >>> engine.export(phrase, "output/my_solo")
    """
    
    def __init__(
        self,
        key: str = "C",
        scale: str = "major",
        progression: Optional[List[str]] = None,
        triad_pair_type: str = "diatonic",
        mode: str = "intervallic",
        string_set: str = "auto",
        rhythmic_style: str = "swing",
        phrase_length: int = 4,
        contour: str = "wave",
        difficulty: str = "intermediate",
        seed: Optional[int] = None
    ):
        """
        Initialize the Triad Pair Solo Engine.
        
        Args:
            key: Root key (e.g., "C", "F#", "Bb")
            scale: Scale type (e.g., "major", "dorian", "altered")
            progression: Optional chord progression
            triad_pair_type: Type of triad pairs ("diatonic", "klemonic", "ust", "altered_dominant_pairs")
            mode: Solo mode ("functional", "modal", "intervallic", "hybrid")
            string_set: Guitar string set ("6-4", "5-3", "4-2", "auto")
            rhythmic_style: Rhythmic style ("straight", "swing", "triplet", "syncopated", "polyrhythmic")
            phrase_length: Default phrase length in bars
            contour: Melodic contour ("ascending", "descending", "wave", "zigzag", "random_seeded")
            difficulty: Difficulty level ("beginner", "intermediate", "advanced")
            seed: Random seed for reproducibility
        """
        self.config = SoloEngineConfig(
            key=key,
            scale=scale,
            progression=progression,
            triad_pair_type=triad_pair_type,
            mode=mode,
            string_set=string_set,
            rhythmic_style=rhythmic_style,
            phrase_length=phrase_length,
            contour=contour,
            difficulty=difficulty,
            seed=seed
        )
        
        # Initialize components
        self.triad_selector = TriadPairSelector(key=key, scale=scale)
        self.pattern_generator = SoloPatternGenerator(
            seed=seed, difficulty=self.config.difficulty
        )
        self.rhythm_engine = SoloRhythmEngine(
            default_style=self.config.rhythmic_style,
            difficulty=self.config.difficulty,
            seed=seed
        )
        self.vl_engine = SoloVoiceLeadingEngine(mode=self.config.mode)
        self.phrase_assembler = PhraseAssembler(self.config)
        self.output_formatter = SoloOutputFormatter(self.config)
    
    # =========================================================================
    # TRIAD PAIR SELECTION
    # =========================================================================
    
    def get_triad_pairs(
        self,
        count: int = 4,
        pair_type: TriadPairType = None
    ) -> List[TriadPair]:
        """
        Get triad pairs for solo generation.
        
        Args:
            count: Number of pairs to generate
            pair_type: Type of pairs (uses config default if None)
        
        Returns:
            List of TriadPair objects
        """
        pair_type = pair_type or self.config.triad_pair_type
        
        if pair_type == TriadPairType.DIATONIC:
            pairs = self.triad_selector.get_diatonic_pairs()
        elif pair_type == TriadPairType.KLEMONIC:
            pairs = self.triad_selector.get_klemonic_pairs()
        elif pair_type == TriadPairType.UST:
            pairs = self.triad_selector.get_ust_pairs()
        elif pair_type == TriadPairType.ALTERED_DOMINANT:
            pairs = self.triad_selector.get_altered_dominant_pairs()
        else:
            pairs = self.triad_selector.get_diatonic_pairs()
        
        # Return requested count (cycling if needed)
        result = []
        while len(result) < count:
            result.extend(pairs)
        return result[:count]
    
    def get_pairs_for_progression(self) -> Dict[str, List[TriadPair]]:
        """
        Get triad pairs for each chord in the configured progression.
        
        Returns:
            Dictionary mapping chord symbols to triad pairs
        """
        if not self.config.progression:
            return {}
        
        return self.triad_selector.get_pairs_for_progression(
            self.config.progression,
            self.config.triad_pair_type.value
        )
    
    # =========================================================================
    # PHRASE GENERATION
    # =========================================================================
    
    def generate_phrase(
        self,
        bars: int = None,
        structure: PhraseStructure = None,
        triad_pairs: List[TriadPair] = None
    ) -> SoloPhrase:
        """
        Generate a complete solo phrase.
        
        Args:
            bars: Number of bars (overrides structure if provided)
            structure: Phrase structure type
            triad_pairs: Specific triad pairs to use (auto-generated if None)
        
        Returns:
            Complete SoloPhrase
        """
        bars = bars or self.config.phrase_length
        
        # Determine structure from bars if not specified
        if structure is None:
            if bars <= 1:
                structure = PhraseStructure.MOTIF_1BAR
            elif bars <= 2:
                structure = PhraseStructure.CALL_2BAR
            elif bars <= 4:
                structure = PhraseStructure.STRUCTURED_4BAR
            else:
                structure = PhraseStructure.STRUCTURED_8BAR
        
        # Get triad pairs
        if triad_pairs is None:
            triad_pairs = self.get_triad_pairs(count=bars)
        
        # Build the phrase
        phrase = self.phrase_assembler.build_phrase(triad_pairs, structure)
        
        return phrase
    
    def generate_call_response(
        self,
        triad_pairs: List[TriadPair] = None
    ) -> Tuple[SoloPhrase, SoloPhrase]:
        """
        Generate a call-and-response phrase pair.
        
        Args:
            triad_pairs: Specific triad pairs to use
        
        Returns:
            Tuple of (call_phrase, response_phrase)
        """
        if triad_pairs is None:
            triad_pairs = self.get_triad_pairs(count=4)
        
        return self.phrase_assembler.build_call_and_response(triad_pairs)
    
    def generate_over_progression(self) -> Dict[str, SoloPhrase]:
        """
        Generate phrases for each chord in the progression.
        
        Returns:
            Dictionary mapping chord symbols to SoloPhrase objects
        """
        if not self.config.progression:
            raise ValueError("No progression configured")
        
        pairs_by_chord = self.get_pairs_for_progression()
        phrases = {}
        
        for chord, pairs in pairs_by_chord.items():
            phrase = self.phrase_assembler.build_phrase(
                pairs[:2], PhraseStructure.MOTIF_1BAR
            )
            phrases[chord] = phrase
        
        return phrases
    
    # =========================================================================
    # PATTERN GENERATION
    # =========================================================================
    
    def generate_pattern(
        self,
        triad_pair: TriadPair,
        pattern_type: PatternType = PatternType.UP_ARPEGGIO
    ) -> MelodicCell:
        """
        Generate a single melodic pattern from a triad pair.
        
        Args:
            triad_pair: Triad pair to use
            pattern_type: Type of pattern to generate
        
        Returns:
            MelodicCell with the pattern
        """
        if pattern_type == PatternType.UP_ARPEGGIO:
            return self.pattern_generator.generate_up_arpeggio(
                triad_pair, string_set=self.config.string_set
            )
        elif pattern_type == PatternType.DOWN_ARPEGGIO:
            return self.pattern_generator.generate_down_arpeggio(
                triad_pair, string_set=self.config.string_set
            )
        elif pattern_type == PatternType.ALTERNATING:
            return self.pattern_generator.generate_alternating(
                triad_pair, string_set=self.config.string_set
            )
        elif pattern_type == PatternType.WAVE:
            return self.pattern_generator.generate_wave(
                triad_pair, string_set=self.config.string_set
            )
        elif pattern_type == PatternType.INTERVAL_SKIP:
            return self.pattern_generator.generate_interval_skip(
                triad_pair, string_set=self.config.string_set
            )
        elif pattern_type == PatternType.PIVOT_TONE:
            return self.pattern_generator.generate_pivot_tone(
                triad_pair, string_set=self.config.string_set
            )
        elif pattern_type in [PatternType.ROTATION_132, PatternType.ROTATION_312,
                              PatternType.ROTATION_213, PatternType.ROTATION_321]:
            rotation = pattern_type.value.split("_")[1]
            return self.pattern_generator.generate_rotation(
                triad_pair, rotation, string_set=self.config.string_set
            )
        else:
            return self.pattern_generator.generate_up_arpeggio(
                triad_pair, string_set=self.config.string_set
            )
    
    def generate_sequence(
        self,
        pattern_type: PatternType = PatternType.UP_ARPEGGIO,
        count: int = 4
    ) -> List[MelodicCell]:
        """
        Generate a sequence of patterns through multiple triad pairs.
        
        Args:
            pattern_type: Type of pattern for each cell
            count: Number of cells to generate
        
        Returns:
            List of MelodicCell objects
        """
        pairs = self.get_triad_pairs(count=count)
        return self.pattern_generator.generate_sequence(
            pairs, pattern_type, string_set=self.config.string_set
        )
    
    # =========================================================================
    # VOICE-LEADING
    # =========================================================================
    
    def analyze_voice_leading(
        self,
        from_pair: TriadPair,
        to_pair: TriadPair
    ) -> VoiceLeadingResult:
        """
        Analyze voice-leading between two triad pairs.
        
        Args:
            from_pair: Starting triad pair
            to_pair: Target triad pair
        
        Returns:
            VoiceLeadingResult with analysis
        """
        # Analyze transition from last triad of first pair to first triad of second
        return self.vl_engine.analyze_transition(
            from_pair.triad_b, to_pair.triad_a
        )
    
    def get_optimal_inversions(
        self,
        from_pair: TriadPair,
        to_pair: TriadPair,
        direction: str = "ascending"
    ) -> Dict[str, Tuple[int, int]]:
        """
        Get optimal inversions for smooth voice-leading.
        
        Args:
            from_pair: Starting triad pair
            to_pair: Target triad pair
            direction: "ascending" or "descending"
        
        Returns:
            Dictionary with recommended inversions
        """
        return {
            "from_inversion": self.vl_engine.optimize_inversion(
                from_pair.triad_a, from_pair.triad_b, direction
            ),
            "to_inversion": self.vl_engine.optimize_inversion(
                to_pair.triad_a, to_pair.triad_b, direction
            )
        }
    
    def generate_tram_analysis(
        self,
        triad_pairs: List[TriadPair] = None
    ) -> List[Dict]:
        """
        Generate TRAM (Tension/Release Alternating Motion) analysis.
        
        Args:
            triad_pairs: Pairs to analyze (auto-generated if None)
        
        Returns:
            List of TRAM analysis dictionaries
        """
        if triad_pairs is None:
            triad_pairs = self.get_triad_pairs(count=4)
        
        return self.vl_engine.generate_tram_sequence(triad_pairs)
    
    # =========================================================================
    # EXPORT
    # =========================================================================
    
    def export(
        self,
        phrase: SoloPhrase,
        output_path: str,
        formats: List[str] = None
    ) -> Dict[str, str]:
        """
        Export phrase to specified formats.
        
        Args:
            phrase: SoloPhrase to export
            output_path: Base output path (without extension)
            formats: List of formats ("json", "musicxml", "html") or None for all
        
        Returns:
            Dictionary mapping format -> filepath
        """
        output_dir = Path(output_path).parent
        base_name = Path(output_path).stem
        
        if formats is None:
            return self.output_formatter.export_all(phrase, str(output_dir), base_name)
        
        files = {}
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if "json" in formats:
            json_path = output_dir / f"{base_name}.json"
            self.output_formatter.save_json(phrase, str(json_path))
            files["json"] = str(json_path)
        
        if "musicxml" in formats:
            xml_path = output_dir / f"{base_name}.musicxml"
            self.output_formatter.save_musicxml(phrase, str(xml_path))
            files["musicxml"] = str(xml_path)
        
        if "html" in formats:
            html_path = output_dir / f"{base_name}.html"
            self.output_formatter.save_html(phrase, str(html_path))
            files["html"] = str(html_path)
        
        return files
    
    def to_json(self, phrase: SoloPhrase) -> Dict:
        """
        Convert phrase to JSON dictionary.
        
        Args:
            phrase: SoloPhrase to convert
        
        Returns:
            JSON-serializable dictionary
        """
        return self.output_formatter.to_json(phrase)
    
    def to_musicxml(self, phrase: SoloPhrase, title: str = None) -> str:
        """
        Convert phrase to MusicXML string.
        
        Args:
            phrase: SoloPhrase to convert
            title: Score title
        
        Returns:
            MusicXML string
        """
        return self.output_formatter.to_musicxml(
            phrase, title or f"Solo in {self.config.key} {self.config.scale}"
        )
    
    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    
    def reconfigure(self, **kwargs):
        """
        Update engine configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Reinitialize components with new config
        self.triad_selector = TriadPairSelector(
            key=self.config.key, scale=self.config.scale
        )
        self.vl_engine = SoloVoiceLeadingEngine(mode=self.config.mode)
        self.phrase_assembler = PhraseAssembler(self.config)
        self.output_formatter = SoloOutputFormatter(self.config)
    
    def get_config(self) -> Dict:
        """Get current configuration as dictionary."""
        return self.config.to_dict()
    
    # =========================================================================
    # DEMO / EXAMPLES
    # =========================================================================
    
    def demo_intervallic_modal(self) -> SoloPhrase:
        """Generate demo: Intervallic modal open-triad pair line."""
        self.reconfigure(
            mode="intervallic",
            triad_pair_type="diatonic",
            rhythmic_style="swing",
            contour="wave"
        )
        pairs = self.get_triad_pairs(count=4)
        return self.generate_phrase(bars=4, triad_pairs=pairs)
    
    def demo_altered_dominant(self) -> SoloPhrase:
        """Generate demo: Altered-dominant open-triad pair over V7alt."""
        self.reconfigure(
            mode="intervallic",
            triad_pair_type="altered_dominant_pairs",
            scale="altered",
            rhythmic_style="swing"
        )
        pairs = self.get_triad_pairs(count=2)
        return self.generate_phrase(bars=2, triad_pairs=pairs)
    
    def demo_functional_251(self) -> SoloPhrase:
        """Generate demo: Functional ii-V-I phrase using APVL + TRAM."""
        self.reconfigure(
            mode="functional",
            triad_pair_type="diatonic",
            progression=["Dm7", "G7", "Cmaj7"],
            rhythmic_style="swing"
        )
        pairs = self.get_triad_pairs(count=4)
        return self.generate_phrase(bars=4, triad_pairs=pairs)
    
    def demo_large_leap(self) -> SoloPhrase:
        """Generate demo: Large-leap modern-jazz phrase using SISM spacing."""
        self.reconfigure(
            mode="intervallic",
            triad_pair_type="ust",
            rhythmic_style="syncopated",
            difficulty="advanced"
        )
        pairs = self.get_triad_pairs(count=4)
        phrase = self.generate_phrase(bars=4, triad_pairs=pairs)
        
        # Apply additional SISM spacing
        for i, cell in enumerate(phrase.cells):
            phrase.cells[i] = self.vl_engine.apply_sism_spacing(cell, 0.85)
        
        return phrase

