"""
Unit Tests for Etude Generator
==============================

Tests for all etude generator modules.
"""

import pytest
import sys
import tempfile
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from inputs import (
    EtudeConfig, EtudeType, Difficulty, RhythmicStyle, EtudeMode,
    StringSet, PositionConstraints, validate_config, create_config
)
from harmonic import HarmonicGenerator, HarmonicMaterial, HarmonicCell
from patterns import PatternStitcher, EtudePhrase, BarContent, NoteEvent, PatternType
from rhythm import RhythmGenerator, RhythmicPhrase, apply_rhythm
from templates import (
    get_template, ScalarOpenTriadEtude, InversionCycleEtude,
    TwoFiveOneEtude, ChordMelodyMiniEtude, IntervallicEtude
)
from output import EtudeOutput, GuitarTabGenerator, EtudeMusicXMLExporter, EtudePDFBuilder
from generator import EtudeGenerator, GeneratedEtude, generate_etude, quick_etude


class TestEtudeConfig:
    """Tests for EtudeConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = EtudeConfig()
        assert config.key == 'C'
        assert config.scale == 'ionian'
        assert config._etude_type_enum == EtudeType.MELODIC
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = EtudeConfig(
            key='G',
            scale='dorian',
            etude_type='intervallic',
            difficulty='advanced'
        )
        assert config.key == 'G'
        assert config.scale == 'dorian'
        assert config._etude_type_enum == EtudeType.INTERVALLIC
        assert config._difficulty_enum == Difficulty.ADVANCED
    
    def test_key_validation(self):
        """Test key validation with fallback."""
        config = EtudeConfig(key='invalid')
        assert config.key == 'C'  # Should fall back to C
    
    def test_scale_validation(self):
        """Test scale name normalization."""
        config = EtudeConfig(scale='major')
        assert config.scale == 'ionian'  # major -> ionian
    
    def test_difficulty_constraints(self):
        """Test difficulty-based constraints."""
        beginner = EtudeConfig(difficulty='beginner', tempo=200)
        assert beginner.tempo <= 80  # Should be capped
        
        advanced = EtudeConfig(difficulty='advanced', length=50)
        assert advanced.length <= 32  # Should be capped
    
    def test_title_generation(self):
        """Test automatic title generation."""
        config = EtudeConfig(key='D', scale='mixolydian', etude_type='harmonic')
        assert 'D' in config.title
        assert 'Mixolydian' in config.title
    
    def test_to_dict(self):
        """Test serialization."""
        config = EtudeConfig()
        data = config.to_dict()
        assert 'key' in data
        assert 'scale' in data
        assert 'etude_type' in data


class TestPositionConstraints:
    """Tests for PositionConstraints."""
    
    def test_from_position(self):
        """Test creating constraints from position."""
        constraints = PositionConstraints.from_position(5, 4)
        assert constraints.min_fret == 5
        assert constraints.max_fret == 9
        assert constraints.contains(7)
        assert not constraints.contains(3)
    
    def test_contains(self):
        """Test fret containment check."""
        constraints = PositionConstraints(min_fret=3, max_fret=7)
        assert constraints.contains(5)
        assert not constraints.contains(10)


class TestHarmonicGenerator:
    """Tests for HarmonicGenerator."""
    
    def test_generate_diatonic(self):
        """Test diatonic triad generation."""
        config = EtudeConfig(key='C', scale='ionian')
        gen = HarmonicGenerator(config)
        material = gen._generate_diatonic()
        
        assert len(material.cells) == 7  # 7 scale degrees
        assert material.key == 'C'
    
    def test_generate_two_five_one(self):
        """Test ii-V-I generation."""
        config = EtudeConfig(key='G', etude_type='ii_v_i', length=6)
        gen = HarmonicGenerator(config)
        material = gen._generate_two_five_one()
        
        # Should have at least ii, V, I
        assert len(material.cells) >= 3
    
    def test_generate_scalar(self):
        """Test scalar material generation."""
        config = EtudeConfig(key='F', scale='lydian', length=8)
        gen = HarmonicGenerator(config)
        material = gen._generate_scalar()
        
        assert len(material.cells) <= config.length
    
    def test_harmonic_cell_to_dict(self):
        """Test HarmonicCell serialization."""
        from open_triad_engine import Triad, Note, TriadType
        
        triad = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        cell = HarmonicCell(triad=triad, scale_degree=1, function='tonic')
        
        data = cell.to_dict()
        assert data['symbol'] == 'C'
        assert data['scale_degree'] == 1


class TestPatternStitcher:
    """Tests for PatternStitcher."""
    
    def test_stitch_phrases(self):
        """Test pattern stitching."""
        config = EtudeConfig(key='C', length=4)
        gen = HarmonicGenerator(config)
        material = gen._generate_diatonic()
        
        stitcher = PatternStitcher(config)
        phrases = stitcher.stitch(material)
        
        assert len(phrases) >= 1
        assert all(isinstance(p, EtudePhrase) for p in phrases)
    
    def test_guitar_positions(self):
        """Test guitar position calculation."""
        config = EtudeConfig(string_set='5-3')
        gen = HarmonicGenerator(config)
        material = gen._generate_diatonic()
        
        stitcher = PatternStitcher(config)
        phrases = stitcher.stitch(material)
        phrases = stitcher.add_guitar_positions(phrases)
        
        # Check that positions are assigned
        for phrase in phrases:
            for bar in phrase.bars:
                for event in bar.notes:
                    assert event.string is not None
                    assert event.fret is not None
    
    def test_pattern_selection(self):
        """Test pattern selection based on etude type."""
        config = EtudeConfig(etude_type='melodic')
        stitcher = PatternStitcher(config)
        
        pattern = stitcher._select_pattern(1)
        assert pattern in [PatternType.ARPEGGIO_UP, PatternType.ARPEGGIO_DOWN]


class TestRhythmGenerator:
    """Tests for RhythmGenerator."""
    
    def test_generate_bar_rhythm(self):
        """Test bar rhythm generation."""
        config = EtudeConfig(rhythmic_style='straight')
        gen = RhythmGenerator(config)
        
        rhythm = gen.generate_bar_rhythm(1, 4)
        
        assert isinstance(rhythm, RhythmicPhrase)
        assert len(rhythm.events) == 4
    
    def test_rhythm_styles(self):
        """Test different rhythm styles."""
        for style in ['straight', 'syncopated', 'triplet']:
            config = EtudeConfig(
                rhythmic_style=style,
                difficulty='advanced'  # Allow all styles
            )
            gen = RhythmGenerator(config)
            rhythm = gen.generate_bar_rhythm(1, 4)
            assert rhythm.style.value == style
    
    def test_apply_rhythm_to_phrases(self):
        """Test applying rhythm to phrases."""
        config = EtudeConfig()
        gen = HarmonicGenerator(config)
        material = gen._generate_diatonic()
        
        stitcher = PatternStitcher(config)
        phrases = stitcher.stitch(material)
        
        rhythm_gen = RhythmGenerator(config)
        phrases = rhythm_gen.apply_rhythm_to_phrases(phrases)
        
        # Check that rhythm was applied
        for phrase in phrases:
            for bar in phrase.bars:
                for event in bar.notes:
                    assert event.duration > 0


class TestTemplates:
    """Tests for etude templates."""
    
    def test_get_template(self):
        """Test template retrieval."""
        config = EtudeConfig(etude_type='scalar')
        template = get_template(config)
        
        assert isinstance(template, ScalarOpenTriadEtude)
    
    def test_scalar_template(self):
        """Test scalar etude template."""
        config = EtudeConfig(key='C', etude_type='scalar', length=8)
        template = ScalarOpenTriadEtude(config)
        
        phrases = template.generate()
        assert len(phrases) >= 1
    
    def test_inversion_cycle_template(self):
        """Test inversion cycle template."""
        config = EtudeConfig(key='G', etude_type='inversion_cycle', length=9)
        template = InversionCycleEtude(config)
        
        phrases = template.generate()
        assert len(phrases) >= 1
    
    def test_two_five_one_template(self):
        """Test ii-V-I template."""
        config = EtudeConfig(key='Bb', etude_type='ii_v_i', length=6)
        template = TwoFiveOneEtude(config)
        
        phrases = template.generate()
        description = template.get_description()
        
        assert len(phrases) >= 1
        assert 'ii-V-I' in description
    
    def test_template_metadata(self):
        """Test template metadata."""
        config = EtudeConfig()
        template = ScalarOpenTriadEtude(config)
        
        metadata = template.get_metadata()
        assert 'template_name' in metadata
        assert 'description' in metadata


class TestOutput:
    """Tests for output modules."""
    
    def test_guitar_tab_generation(self):
        """Test TAB generation."""
        config = EtudeConfig()
        gen = HarmonicGenerator(config)
        material = gen._generate_diatonic()
        
        stitcher = PatternStitcher(config)
        phrases = stitcher.stitch(material)
        phrases = stitcher.add_guitar_positions(phrases)
        
        tab_gen = GuitarTabGenerator(config)
        tab = tab_gen.generate_tab(phrases)
        
        assert 'e|' in tab  # High E string
        assert 'E|' in tab  # Low E string
    
    def test_musicxml_export(self):
        """Test MusicXML export."""
        config = EtudeConfig()
        gen = HarmonicGenerator(config)
        material = gen._generate_diatonic()
        
        stitcher = PatternStitcher(config)
        phrases = stitcher.stitch(material)
        
        exporter = EtudeMusicXMLExporter(config)
        
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as f:
            path = exporter.export(phrases, f.name)
            assert Path(path).exists()
            
            # Check file content
            content = Path(path).read_text()
            assert 'score-partwise' in content
            assert 'measure' in content
    
    def test_html_export(self):
        """Test HTML/PDF export."""
        config = EtudeConfig(title='Test Etude')
        gen = HarmonicGenerator(config)
        material = gen._generate_diatonic()
        
        stitcher = PatternStitcher(config)
        phrases = stitcher.stitch(material)
        
        builder = EtudePDFBuilder(config)
        html = builder.build_html(phrases, "Test description")
        
        assert 'Test Etude' in html
        assert 'Test description' in html
    
    def test_etude_output_statistics(self):
        """Test EtudeOutput statistics."""
        config = EtudeConfig()
        gen = HarmonicGenerator(config)
        material = gen._generate_diatonic()
        
        stitcher = PatternStitcher(config)
        phrases = stitcher.stitch(material)
        
        output = EtudeOutput(config=config, phrases=phrases)
        stats = output._get_statistics()
        
        assert 'total_notes' in stats
        assert 'total_bars' in stats


class TestEtudeGenerator:
    """Tests for main EtudeGenerator."""
    
    def test_generate_etude(self):
        """Test complete etude generation."""
        config = EtudeConfig(key='D', scale='dorian', etude_type='melodic', length=4)
        generator = EtudeGenerator(config)
        
        etude = generator.generate()
        
        assert isinstance(etude, GeneratedEtude)
        assert etude.total_bars >= 1
        assert etude.total_notes >= 1
    
    def test_quick_generate(self):
        """Test quick generation."""
        etude = EtudeGenerator.quick_generate(
            key='A',
            etude_type='scalar',
            difficulty='beginner'
        )
        
        assert etude.config.key == 'A'
        assert etude.config._difficulty_enum == Difficulty.BEGINNER
    
    def test_generate_etude_function(self):
        """Test convenience function."""
        etude = generate_etude(key='E', scale='mixolydian', length=4)
        
        assert etude.config.key == 'E'
        assert etude.config.scale == 'mixolydian'
    
    def test_quick_etude_function(self):
        """Test quick etude function."""
        etude = quick_etude(key='F', etude_type='harmonic')
        
        assert etude.config.key == 'F'
    
    def test_export_all(self):
        """Test exporting to all formats."""
        etude = quick_etude(key='C', etude_type='melodic')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            base = str(Path(tmpdir) / 'test_etude')
            results = etude.export_all(base)
            
            assert 'json' in results
            assert 'tab' in results
            assert 'musicxml' in results
            assert 'html' in results
            
            # Verify files exist
            for format_name, path in results.items():
                assert Path(path).exists()
    
    def test_etude_warnings(self):
        """Test that warnings are captured."""
        config = EtudeConfig(
            difficulty='beginner',
            rhythmic_style='polyrhythmic'  # Not allowed for beginner
        )
        generator = EtudeGenerator(config)
        
        assert len(generator.warnings) > 0
    
    def test_etude_to_dict(self):
        """Test etude serialization."""
        etude = quick_etude()
        data = etude.to_dict()
        
        assert 'title' in data
        assert 'config' in data
        assert 'phrases' in data
        assert 'statistics' in data


class TestVoiceLeadingIntegration:
    """Tests for voice-leading integration with VL-SM."""
    
    def test_functional_mode_voice_leading(self):
        """Test functional mode voice leading."""
        config = EtudeConfig(key='C', mode='functional', etude_type='ii_v_i')
        gen = HarmonicGenerator(config)
        material = gen._generate_two_five_one()
        
        # Check voice leading info is present
        has_vl_info = any(
            cell.voice_leading_from is not None 
            for cell in material.cells
        )
        assert has_vl_info
    
    def test_modal_mode_voice_leading(self):
        """Test modal mode voice leading."""
        config = EtudeConfig(key='D', mode='modal', etude_type='melodic')
        gen = HarmonicGenerator(config)
        material = gen._generate_diatonic()
        
        # Should have generated material
        assert len(material.cells) >= 1


class TestStringSetPlayability:
    """Tests for string-set playability constraints."""
    
    def test_string_set_constraint(self):
        """Test that string set constraints are applied."""
        for string_set in ['6-4', '5-3', '4-2']:
            config = EtudeConfig(string_set=string_set, etude_type='string_set')
            gen = HarmonicGenerator(config)
            material = gen._generate_diatonic()
            
            stitcher = PatternStitcher(config)
            phrases = stitcher.stitch(material)
            phrases = stitcher.add_guitar_positions(phrases)
            
            # Check string constraints
            expected_strings = {
                '6-4': {6, 5, 4},
                '5-3': {5, 4, 3},
                '4-2': {4, 3, 2},
            }[string_set]
            
            for phrase in phrases:
                for bar in phrase.bars:
                    for event in bar.notes:
                        if event.string is not None:
                            assert event.string in expected_strings or event.fret is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

