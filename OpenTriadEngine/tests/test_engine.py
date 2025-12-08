"""
Unit Tests for Main Engine
==========================

Tests for OpenTriadEngine and special use-case engines.
"""

import pytest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from open_triad_engine.engine import (
    OpenTriadEngine, EngineResult,
    quick_open_triads, quick_voice_lead, quick_two_five_one
)
from open_triad_engine.inputs import EngineConfig
from open_triad_engine.core import Note, Triad, TriadType
from open_triad_engine.special_engines import (
    ChordMelodyEngine, TwoFiveOneEngine, OpenTriadPairEngine,
    CounterpointCompanion, OrchestrationMapper
)


class TestOpenTriadEngine:
    """Tests for the main engine class."""
    
    def test_engine_creation(self):
        """Test basic engine creation."""
        engine = OpenTriadEngine()
        assert engine.VERSION == "1.0.0"
    
    def test_engine_with_config(self):
        """Test engine creation with config."""
        config = EngineConfig(
            triad_type='minor',
            mode='melodic',
            priority='smooth'
        )
        engine = OpenTriadEngine(config)
        
        assert engine.config.triad_type == 'minor'
        assert engine.config.mode == 'melodic'
    
    def test_create_triad(self):
        """Test triad creation through engine."""
        engine = OpenTriadEngine()
        triad = engine.create_triad('C', 'major', 4)
        
        assert triad.root.name == 'C'
        assert triad.triad_type == TriadType.MAJOR
    
    def test_to_open_voicing(self):
        """Test open voicing conversion."""
        engine = OpenTriadEngine()
        closed = engine.create_triad('G', 'minor')
        open_triad = engine.to_open_voicing(closed, 'drop2')
        
        assert open_triad.is_open
    
    def test_get_all_inversions(self):
        """Test getting all inversions."""
        engine = OpenTriadEngine()
        triad = engine.create_triad('D', 'major')
        inversions = engine.get_all_inversions(triad)
        
        assert 'open_root' in inversions
        assert 'open_first' in inversions
        assert 'open_second' in inversions
    
    def test_generate_scale_triads(self):
        """Test scale triad generation."""
        engine = OpenTriadEngine()
        result = engine.generate_scale_triads('C', 'ionian')
        
        assert isinstance(result, EngineResult)
        assert result.success
        assert len(result.data) == 7
    
    def test_parse_progression(self):
        """Test chord progression parsing."""
        engine = OpenTriadEngine()
        result = engine.parse_progression(['Dm7', 'G7', 'Cmaj7'])
        
        assert result.success
        assert len(result.data) == 3
    
    def test_voice_lead(self):
        """Test voice leading between two triads."""
        engine = OpenTriadEngine()
        source = engine.create_triad('C', 'major')
        source = engine.to_open_voicing(source, 'drop2')
        target = engine.create_triad('G', 'major')
        
        result = engine.voice_lead(source, target)
        
        assert len(result.motions) == 3
    
    def test_voice_lead_progression(self):
        """Test voice leading a progression."""
        engine = OpenTriadEngine()
        result = engine.voice_lead_progression(['Dm', 'G', 'C'])
        
        assert result.success
        assert 'triads' in result.data
        assert 'voice_leading' in result.data
    
    def test_get_shape_bundles(self):
        """Test shape bundle creation."""
        engine = OpenTriadEngine()
        result = engine.generate_scale_triads('C', 'ionian')
        bundles = engine.get_shape_bundles(result.data)
        
        assert len(bundles) == 7
        for bundle in bundles:
            assert bundle.open_root is not None
            assert bundle.open_first is not None
            assert bundle.open_second is not None
    
    def test_generate_patterns(self):
        """Test pattern generation."""
        engine = OpenTriadEngine()
        triad = engine.create_triad('C', 'major')
        patterns = engine.generate_patterns(triad)
        
        assert len(patterns) > 0
    
    def test_generate_two_five_one(self):
        """Test ii-V-I generation."""
        engine = OpenTriadEngine()
        result = engine.generate_two_five_one('C')
        
        assert result.ii is not None
        assert result.V is not None
        assert result.I is not None
    
    def test_list_scales(self):
        """Test listing available scales."""
        engine = OpenTriadEngine()
        scales = engine.list_scales()
        
        assert 'ionian' in scales
        assert 'dorian' in scales
        assert 'altered' in scales
    
    def test_export_json(self):
        """Test JSON export."""
        engine = OpenTriadEngine()
        result = engine.generate_scale_triads('C', 'ionian')
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = engine.export_json(result.data, f.name)
            assert Path(path).exists()


class TestChordMelodyEngine:
    """Tests for chord-melody engine."""
    
    def test_harmonize_note(self):
        """Test harmonizing a single note."""
        engine = ChordMelodyEngine()
        melody_note = Note('E', 5)
        
        voicing = engine.harmonize_note(melody_note)
        
        # Melody should be on top
        assert voicing.top_note.pitch_class == melody_note.pitch_class
    
    def test_harmonize_note_with_chord(self):
        """Test harmonizing with specific chord."""
        engine = ChordMelodyEngine()
        melody_note = Note('G', 5)
        
        voicing = engine.harmonize_note(melody_note, 'C')
        
        assert voicing.triad.root.name == 'C'
    
    def test_harmonize_melody(self):
        """Test harmonizing a melody line."""
        engine = ChordMelodyEngine()
        melody = [Note('C', 5), Note('E', 5), Note('G', 5)]
        
        voicings = engine.harmonize_melody(melody)
        
        assert len(voicings) == 3
        for i, v in enumerate(voicings):
            assert v.top_note.pitch_class == melody[i].pitch_class


class TestTwoFiveOneEngine:
    """Tests for ii-V-I engine."""
    
    def test_generate_major(self):
        """Test generating major ii-V-I."""
        engine = TwoFiveOneEngine()
        result = engine.generate('C')
        
        assert result.ii.root.name == 'D'
        assert result.ii.triad_type == TriadType.MINOR
        assert result.V.root.name == 'G'
        assert result.I.root.name == 'C'
        assert result.I.triad_type == TriadType.MAJOR
    
    def test_generate_minor(self):
        """Test generating minor ii-V-i."""
        engine = TwoFiveOneEngine()
        result = engine.generate('C', minor=True)
        
        assert result.I.triad_type == TriadType.MINOR
    
    def test_generate_all_keys(self):
        """Test generating in all keys."""
        engine = TwoFiveOneEngine()
        results = engine.generate_all_keys()
        
        assert len(results) == 12


class TestOpenTriadPairEngine:
    """Tests for triad pair engine."""
    
    def test_create_klemons_pair(self):
        """Test creating Klemons-style pair."""
        engine = OpenTriadPairEngine()
        pair = engine.create_klemons_pair('C')
        
        # Klemons pairs are whole step apart
        interval = (pair.triad2.root.pitch_class - pair.triad1.root.pitch_class) % 12
        assert interval == 2
    
    def test_create_diatonic_pair(self):
        """Test creating diatonic pair."""
        engine = OpenTriadPairEngine()
        pair = engine.create_diatonic_pair('ionian', 'C', 1, 4)
        
        # Degrees 1 and 4 in C major = C and F
        assert pair.triad1.root.name == 'C'
        assert pair.triad2.root.name == 'F'
    
    def test_generate_melodic_line(self):
        """Test generating melodic line from pair."""
        engine = OpenTriadPairEngine()
        pair = engine.create_klemons_pair('G')
        
        line = engine.generate_melodic_line(pair, length=8)
        
        assert len(line) == 8


class TestCounterpointCompanion:
    """Tests for counterpoint engine."""
    
    def test_generate_counterpoint(self):
        """Test generating counterpoint."""
        engine = CounterpointCompanion()
        
        triads = [
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR),
            Triad(root=Note('G', 4), triad_type=TriadType.MAJOR),
            Triad(root=Note('A', 4), triad_type=TriadType.MINOR),
            Triad(root=Note('F', 4), triad_type=TriadType.MAJOR),
        ]
        
        result = engine.generate_counterpoint(triads)
        
        assert len(result.soprano.notes) == 4
        assert len(result.alto.notes) == 4
        assert len(result.bass.notes) == 4
    
    def test_analyze_motion(self):
        """Test motion analysis."""
        engine = CounterpointCompanion()
        
        triads = [
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR),
            Triad(root=Note('F', 4), triad_type=TriadType.MAJOR),
        ]
        
        result = engine.generate_counterpoint(triads)
        analysis = engine.analyze_motion(result)
        
        assert 'soprano' in analysis
        assert 'alto' in analysis
        assert 'bass' in analysis


class TestOrchestrationMapper:
    """Tests for orchestration mapper."""
    
    def test_assign_instruments(self):
        """Test instrument assignment."""
        mapper = OrchestrationMapper()
        triad = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        
        voicing = mapper.assign_instruments(triad)
        
        assert 'top' in voicing.assignments
        assert 'middle' in voicing.assignments
        assert 'bottom' in voicing.assignments
    
    def test_custom_instruments(self):
        """Test with custom instruments."""
        mapper = OrchestrationMapper(
            top_instruments=['flute'],
            middle_instruments=['clarinet'],
            bottom_instruments=['bassoon']
        )
        
        triad = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        voicing = mapper.assign_instruments(triad)
        
        # Should use custom instruments
        assert voicing.assignments['top'] == 'flute'


class TestQuickFunctions:
    """Tests for module-level quick functions."""
    
    def test_quick_open_triads(self):
        """Test quick_open_triads function."""
        triads = quick_open_triads('C', 'dorian')
        
        assert len(triads) == 7
        for triad in triads:
            assert triad.is_open
    
    def test_quick_voice_lead(self):
        """Test quick_voice_lead function."""
        triads = quick_voice_lead(['Am', 'D', 'G', 'C'])
        
        assert len(triads) == 4
    
    def test_quick_two_five_one(self):
        """Test quick_two_five_one function."""
        triads = quick_two_five_one('Bb')
        
        assert len(triads) == 3


class TestEngineResult:
    """Tests for EngineResult."""
    
    def test_to_dict(self):
        """Test serialization."""
        result = EngineResult(
            success=True,
            operation='test',
            data={'key': 'value'},
            message='Test message'
        )
        
        data = result.to_dict()
        
        assert data['success'] == True
        assert data['operation'] == 'test'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

