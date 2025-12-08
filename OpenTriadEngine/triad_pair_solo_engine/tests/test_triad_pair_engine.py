"""
Unit Tests for Triad Pair Solo Engine
======================================

Tests for:
- Triad pair mapping correctness
- Open-triad transformation
- Inversion cycling in intervallic mode
- VL-SM intervallic behaviour
- Rhythmic alignment rules
- MusicXML schema validity
"""

import pytest
import sys
import os
from xml.etree import ElementTree as ET

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inputs import (
    SoloEngineConfig, TriadPairType, SoloMode, RhythmicStyle,
    ContourType, SoloDifficulty
)
from triad_pairs import TriadPair, TriadPairSelector
from patterns import SoloPatternGenerator, PatternType, MelodicCell
from rhythm import SoloRhythmEngine, RhythmicTemplate
from voice_leading import SoloVoiceLeadingEngine, VoiceLeadingResult
from phrase_assembler import PhraseAssembler, SoloPhrase, PhraseStructure
from output import SoloOutputFormatter
from engine import TriadPairSoloEngine


class TestInputValidation:
    """Test input validation and fallbacks."""
    
    def test_valid_key(self):
        """Test valid key is accepted."""
        config = SoloEngineConfig(key="F#")
        assert config.key == "F#"
    
    def test_invalid_key_fallback(self):
        """Test invalid key falls back to C."""
        config = SoloEngineConfig(key="Z")
        assert config.key == "C"
    
    def test_valid_scale(self):
        """Test valid scale is accepted."""
        config = SoloEngineConfig(scale="dorian")
        assert config.scale == "dorian"
    
    def test_phrase_length_validation(self):
        """Test phrase length bounds."""
        config = SoloEngineConfig(phrase_length=50)
        assert config.phrase_length == 32  # Capped at 32
        
        config2 = SoloEngineConfig(phrase_length=0)
        assert config2.phrase_length == 4  # Fallback to 4
    
    def test_enum_string_conversion(self):
        """Test string to enum conversion."""
        config = SoloEngineConfig(
            triad_pair_type="klemonic",
            mode="functional",
            rhythmic_style="triplet"
        )
        assert config.triad_pair_type == TriadPairType.KLEMONIC
        assert config.mode == SoloMode.FUNCTIONAL
        assert config.rhythmic_style == RhythmicStyle.TRIPLET


class TestTriadPairSelection:
    """Test triad pair selection engine."""
    
    def test_diatonic_pairs_count(self):
        """Test diatonic pairs returns correct count."""
        selector = TriadPairSelector(key="C", scale="major")
        pairs = selector.get_diatonic_pairs()
        # Should return combinations of 7 scale degrees
        assert len(pairs) > 0
        assert all(isinstance(p, TriadPair) for p in pairs)
    
    def test_diatonic_pairs_adjacent(self):
        """Test adjacent-only diatonic pairs."""
        selector = TriadPairSelector(key="C", scale="major")
        pairs = selector.get_diatonic_pairs(adjacent_only=True)
        assert len(pairs) == 7  # 7 adjacent pairs in diatonic scale
    
    def test_klemonic_pairs(self):
        """Test Klemonic pair generation."""
        selector = TriadPairSelector(key="G", scale="major")
        pairs = selector.get_klemonic_pairs(chord_quality="maj7")
        assert len(pairs) > 0
        assert all(p.relationship == "klemonic" for p in pairs)
    
    def test_ust_pairs(self):
        """Test UST pair generation."""
        selector = TriadPairSelector(key="G", scale="altered")
        pairs = selector.get_ust_pairs(chord_type="7alt")
        assert len(pairs) > 0
        assert all(p.relationship == "ust" for p in pairs)
    
    def test_altered_dominant_pairs(self):
        """Test altered dominant pair generation."""
        selector = TriadPairSelector(key="G", scale="altered")
        pairs = selector.get_altered_dominant_pairs(alt_type="7alt")
        assert len(pairs) > 0
        assert all(p.tension_level == 0.9 for p in pairs)
    
    def test_triad_pair_interval(self):
        """Test interval calculation between pair roots."""
        pair = TriadPair(
            triad_a=("C", "major"),
            triad_b=("G", "major"),
            relationship="test"
        )
        assert pair.get_interval() == 7  # Perfect fifth = 7 semitones


class TestPatternGeneration:
    """Test pattern generation module."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SoloPatternGenerator(base_octave=4, seed=42)
        self.test_pair = TriadPair(
            triad_a=("C", "major"),
            triad_b=("D", "minor"),
            relationship="diatonic"
        )
    
    def test_up_arpeggio(self):
        """Test ascending arpeggio pattern."""
        cell = self.generator.generate_up_arpeggio(self.test_pair)
        pitches = cell.get_pitches()
        
        # Should be generally ascending
        assert len(pitches) == 6  # 3 notes per triad
        assert cell.contour == "ascending"
    
    def test_down_arpeggio(self):
        """Test descending arpeggio pattern."""
        cell = self.generator.generate_down_arpeggio(self.test_pair)
        
        assert cell.contour == "descending"
        assert len(cell.notes) == 6
    
    def test_alternating_pattern(self):
        """Test alternating triad pattern."""
        cell = self.generator.generate_alternating(self.test_pair, repetitions=2)
        
        # Should alternate between A and B triads
        sources = [n.triad_source for n in cell.notes]
        assert "A" in sources and "B" in sources
    
    def test_rotation_pattern(self):
        """Test rotation patterns."""
        for rotation in ["132", "312", "213", "321"]:
            cell = self.generator.generate_rotation(self.test_pair, rotation)
            assert len(cell.notes) == 6  # 3 from each triad
    
    def test_wave_pattern(self):
        """Test wave pattern generation."""
        cell = self.generator.generate_wave(self.test_pair)
        assert cell.contour == "wave"
    
    def test_guitar_position(self):
        """Test guitar string/fret calculation."""
        cell = self.generator.generate_up_arpeggio(
            self.test_pair, string_set="5-3"
        )
        
        # All notes should have string/fret info
        for note in cell.notes:
            assert note.string is not None
            assert note.fret is not None
            assert 1 <= note.string <= 6
    
    def test_stitch_to_bar(self):
        """Test stitching cells to bar length."""
        cells = [
            self.generator.generate_up_arpeggio(self.test_pair, duration=0.5)
            for _ in range(3)
        ]
        
        bar_notes = self.generator.stitch_cells_to_bar(cells, bar_length=4.0)
        total_duration = sum(n.duration for n in bar_notes)
        
        assert total_duration <= 4.0


class TestRhythmEngine:
    """Test rhythm engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SoloRhythmEngine(seed=42)
    
    def test_straight_template(self):
        """Test straight 8ths template."""
        template = self.engine.get_template(RhythmicStyle.STRAIGHT)
        assert template.style == RhythmicStyle.STRAIGHT
        assert len(template.events) == 8  # 8 eighth notes per bar
    
    def test_swing_template(self):
        """Test swing template."""
        template = self.engine.get_template(RhythmicStyle.SWING)
        assert template.style == RhythmicStyle.SWING
    
    def test_triplet_template(self):
        """Test triplet template."""
        template = self.engine.get_template(RhythmicStyle.TRIPLET)
        assert template.style == RhythmicStyle.TRIPLET
        # Should have 12 events (4 beats × 3 triplets)
        assert len(template.events) == 12
    
    def test_apply_swing(self):
        """Test swing application."""
        template = self.engine.get_template(RhythmicStyle.STRAIGHT)
        swung = self.engine.apply_swing(template.events, swing_amount=0.33)
        
        # Some events should have swing offset
        swing_offsets = [e.swing_offset for e in swung]
        assert any(offset > 0 for offset in swing_offsets)
    
    def test_phrase_rhythm_generation(self):
        """Test multi-bar rhythm generation."""
        templates = self.engine.generate_phrase_rhythm(4, RhythmicStyle.SWING)
        assert len(templates) == 4


class TestVoiceLeading:
    """Test voice-leading engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.vl_intervallic = SoloVoiceLeadingEngine(mode=SoloMode.INTERVALLIC)
        self.vl_functional = SoloVoiceLeadingEngine(mode=SoloMode.FUNCTIONAL)
    
    def test_transition_analysis(self):
        """Test transition analysis."""
        result = self.vl_intervallic.analyze_transition(
            ("C", "major"), ("D", "minor")
        )
        
        assert isinstance(result, VoiceLeadingResult)
        assert len(result.motion_intervals) == 3
        assert result.narrative is not None
    
    def test_motion_types(self):
        """Test motion type classification."""
        # Same triad should have common tones
        result = self.vl_intervallic.analyze_transition(
            ("C", "major"), ("C", "major")
        )
        assert all(mt == "common_tone" for mt in result.motion_types)
    
    def test_intervallic_tension(self):
        """Test intervallic mode tension calculation."""
        result = self.vl_intervallic.analyze_transition(
            ("C", "major"), ("F#", "major")  # Tritone apart
        )
        # Large motion should be interesting in intervallic mode
        assert result.tension_level > 0.5
    
    def test_functional_smoothness(self):
        """Test functional mode prefers smooth motion."""
        result = self.vl_functional.analyze_transition(
            ("C", "major"), ("G", "major")  # Related keys
        )
        # Should have lower tension for smooth motion
        assert result.tension_level <= 0.8
    
    def test_optimal_inversions(self):
        """Test inversion optimization."""
        inversions = self.vl_intervallic.optimize_inversion(
            ("C", "major"), ("D", "minor"), "ascending"
        )
        assert 0 <= inversions[0] <= 2
        assert 0 <= inversions[1] <= 2
    
    def test_sism_spacing(self):
        """Test SISM spacing application."""
        generator = SoloPatternGenerator(seed=42)
        pair = TriadPair(("C", "major"), ("D", "minor"), "test")
        cell = generator.generate_up_arpeggio(pair)
        
        adjusted = self.vl_intervallic.apply_sism_spacing(cell, target_tension=0.8)
        
        # Pitches should be adjusted for high tension
        original_pitches = cell.get_pitches()
        adjusted_pitches = adjusted.get_pitches()
        assert original_pitches != adjusted_pitches or len(cell.notes) < 2


class TestPhraseAssembler:
    """Test phrase assembler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = SoloEngineConfig(key="C", scale="major")
        self.assembler = PhraseAssembler(self.config)
        self.test_pairs = [
            TriadPair(("C", "major"), ("D", "minor"), "diatonic"),
            TriadPair(("E", "minor"), ("F", "major"), "diatonic"),
        ]
    
    def test_1bar_motif(self):
        """Test 1-bar motif generation."""
        phrase = self.assembler.build_phrase(
            self.test_pairs, PhraseStructure.MOTIF_1BAR
        )
        assert phrase.bar_count == 1
        assert phrase.structure == PhraseStructure.MOTIF_1BAR
    
    def test_2bar_call(self):
        """Test 2-bar call phrase."""
        phrase = self.assembler.build_phrase(
            self.test_pairs, PhraseStructure.CALL_2BAR
        )
        assert phrase.bar_count == 2
        assert phrase.metadata.get("phrase_type") == "call"
    
    def test_4bar_phrase(self):
        """Test 4-bar structured phrase."""
        phrase = self.assembler.build_phrase(
            self.test_pairs * 2, PhraseStructure.STRUCTURED_4BAR
        )
        assert phrase.bar_count == 4
        assert len(phrase.cells) == 4
    
    def test_call_and_response(self):
        """Test call-and-response generation."""
        call, response = self.assembler.build_call_and_response(self.test_pairs * 2)
        
        assert call.metadata.get("direction") == "ascending"
        assert response.metadata.get("direction") == "descending"


class TestOutputFormatter:
    """Test output formatting."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = SoloEngineConfig(key="C", scale="major")
        self.formatter = SoloOutputFormatter(self.config)
        self.assembler = PhraseAssembler(self.config)
        
        pairs = [
            TriadPair(("C", "major"), ("D", "minor"), "diatonic"),
            TriadPair(("E", "minor"), ("F", "major"), "diatonic"),
        ]
        self.phrase = self.assembler.build_phrase(pairs, PhraseStructure.CALL_2BAR)
    
    def test_json_output(self):
        """Test JSON output structure."""
        json_data = self.formatter.to_json(self.phrase)
        
        assert "phrase" in json_data
        assert "notes" in json_data
        assert "triad_pairs" in json_data
        assert json_data["phrase"]["bar_count"] == 2
    
    def test_musicxml_validity(self):
        """Test MusicXML output is valid XML."""
        xml_string = self.formatter.to_musicxml(self.phrase, "Test Solo")
        
        # Should parse without error
        root = ET.fromstring(xml_string)
        
        # Check basic structure
        assert root.tag == "score-partwise"
        assert root.find(".//part") is not None
        assert root.find(".//measure") is not None
    
    def test_musicxml_notes(self):
        """Test MusicXML contains notes."""
        xml_string = self.formatter.to_musicxml(self.phrase)
        root = ET.fromstring(xml_string)
        
        notes = root.findall(".//note")
        assert len(notes) > 0
    
    def test_html_output(self):
        """Test HTML phrase sheet generation."""
        html = self.formatter.to_html_phrase_sheet(self.phrase, "Test")
        
        assert "<!DOCTYPE html>" in html
        assert "Test" in html
        assert "Triad Pairs Used" in html


class TestMainEngine:
    """Test main TriadPairSoloEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TriadPairSoloEngine(
            key="C", scale="dorian", seed=42
        )
    
    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        assert self.engine.config.key == "C"
        assert self.engine.config.scale == "dorian"
    
    def test_get_triad_pairs(self):
        """Test triad pair retrieval."""
        pairs = self.engine.get_triad_pairs(count=4)
        assert len(pairs) == 4
        assert all(isinstance(p, TriadPair) for p in pairs)
    
    def test_generate_phrase(self):
        """Test phrase generation."""
        phrase = self.engine.generate_phrase(bars=4)
        
        assert isinstance(phrase, SoloPhrase)
        assert phrase.bar_count == 4
        assert len(phrase.notes) > 0
    
    def test_generate_pattern(self):
        """Test single pattern generation."""
        pairs = self.engine.get_triad_pairs(count=1)
        cell = self.engine.generate_pattern(pairs[0], PatternType.WAVE)
        
        assert isinstance(cell, MelodicCell)
        assert cell.pattern_type == PatternType.WAVE
    
    def test_demo_methods(self):
        """Test demo phrase generation methods."""
        demos = [
            self.engine.demo_intervallic_modal,
            self.engine.demo_altered_dominant,
            self.engine.demo_functional_251,
            self.engine.demo_large_leap,
        ]
        
        for demo_fn in demos:
            phrase = demo_fn()
            assert isinstance(phrase, SoloPhrase)
            assert len(phrase.notes) > 0
    
    def test_reconfigure(self):
        """Test engine reconfiguration."""
        self.engine.reconfigure(key="G", mode="functional")
        
        assert self.engine.config.key == "G"
        assert self.engine.config.mode == SoloMode.FUNCTIONAL
    
    def test_export_json(self):
        """Test JSON export from engine."""
        phrase = self.engine.generate_phrase(bars=2)
        json_data = self.engine.to_json(phrase)
        
        assert isinstance(json_data, dict)
        assert "notes" in json_data


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_workflow_diatonic(self):
        """Test complete diatonic workflow."""
        engine = TriadPairSoloEngine(
            key="C", scale="major",
            triad_pair_type="diatonic",
            mode="intervallic",
            rhythmic_style="swing",
            seed=42
        )
        
        # Generate pairs
        pairs = engine.get_triad_pairs(count=4)
        assert len(pairs) == 4
        
        # Generate phrase
        phrase = engine.generate_phrase(bars=4, triad_pairs=pairs)
        assert phrase.bar_count == 4
        
        # Export to JSON
        json_data = engine.to_json(phrase)
        assert len(json_data["notes"]) > 0
        
        # Export to MusicXML
        xml = engine.to_musicxml(phrase)
        root = ET.fromstring(xml)
        assert root.tag == "score-partwise"
    
    def test_full_workflow_altered(self):
        """Test complete altered dominant workflow."""
        engine = TriadPairSoloEngine(
            key="G", scale="altered",
            triad_pair_type="altered_dominant_pairs",
            mode="intervallic",
            difficulty="advanced",
            seed=42
        )
        
        phrase = engine.generate_phrase(bars=2)
        
        assert phrase.bar_count == 2
        assert len(phrase.notes) > 0
    
    def test_call_response_workflow(self):
        """Test call and response workflow."""
        engine = TriadPairSoloEngine(key="F", scale="dorian", seed=42)
        
        call, response = engine.generate_call_response()
        
        assert call.bar_count == 2
        assert response.bar_count == 2
        assert call.metadata.get("direction") == "ascending"
        assert response.metadata.get("direction") == "descending"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

