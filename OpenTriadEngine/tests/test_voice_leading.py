"""
Unit Tests for Voice Leading Module
===================================

Tests for VL-SM modes, APVL, TRAM, SISM algorithms.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from open_triad_engine.core import Note, Triad, TriadType
from open_triad_engine.voice_leading import (
    VoiceLeadingSmartModule, VLMode, VoiceLeadingResult,
    APVL, TRAM, SISM, voice_lead
)
from open_triad_engine.transformations import InversionEngine


class TestAPVL:
    """Tests for Axis-Preserving Voice Leading."""
    
    def test_find_common_tones(self):
        """Test finding common tones between triads."""
        c_major = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        a_minor = Triad(root=Note('A', 4), triad_type=TriadType.MINOR)
        
        common = APVL.find_common_tones(c_major, a_minor)
        
        # C major (C, E, G) and A minor (A, C, E) share C and E
        assert len(common) >= 1
    
    def test_apply_preserves_common_tone(self):
        """Test that APVL preserves common tones when possible."""
        c_major = InversionEngine.open_root(
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        )
        
        result = APVL.apply(c_major, Note('G', 4), TriadType.MAJOR)
        
        # G major should share G with C major
        common = APVL.find_common_tones(c_major, result)
        assert len(common) >= 1


class TestTRAM:
    """Tests for Tension/Release Alternating Motion."""
    
    def test_alternating_tension(self):
        """Test that tension alternates."""
        tram = TRAM()
        
        first = tram.get_next_tension_state()
        second = tram.get_next_tension_state()
        third = tram.get_next_tension_state()
        
        assert first != second
        assert second != third
        assert first == third


class TestSISM:
    """Tests for Sum-Interval Stability Mapping."""
    
    def test_stability_calculation(self):
        """Test stability score calculation."""
        triad = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        score = SISM.calculate_stability(triad)
        
        assert isinstance(score, float)
        assert score >= 0
    
    def test_rank_by_stability(self):
        """Test ranking triads by stability."""
        triads = [
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR),
            Triad(root=Note('C', 4), triad_type=TriadType.DIMINISHED),
            Triad(root=Note('C', 4), triad_type=TriadType.AUGMENTED),
        ]
        
        ranked = SISM.rank_by_stability(triads)
        
        assert len(ranked) == 3
        # First should be most stable (lowest score)
        assert ranked[0][1] <= ranked[1][1] <= ranked[2][1]


class TestVoiceLeadingSmartModule:
    """Tests for the main VL-SM."""
    
    def test_functional_mode(self):
        """Test functional voice leading mode."""
        vlsm = VoiceLeadingSmartModule(mode=VLMode.FUNCTIONAL)
        
        source = InversionEngine.open_root(
            Triad(root=Note('D', 4), triad_type=TriadType.MINOR)
        )
        target = Triad(root=Note('G', 4), triad_type=TriadType.MAJOR)
        
        result = vlsm.voice_lead(source, target)
        
        assert isinstance(result, VoiceLeadingResult)
        assert result.mode == VLMode.FUNCTIONAL
        assert len(result.motions) == 3
    
    def test_modal_mode(self):
        """Test modal voice leading mode."""
        vlsm = VoiceLeadingSmartModule(mode=VLMode.MODAL)
        
        source = InversionEngine.open_root(
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        )
        target = Triad(root=Note('Db', 4), triad_type=TriadType.MAJOR)
        
        result = vlsm.voice_lead(source, target)
        
        assert result.mode == VLMode.MODAL
    
    def test_counterpoint_mode(self):
        """Test counterpoint voice leading mode."""
        vlsm = VoiceLeadingSmartModule(mode=VLMode.COUNTERPOINT)
        
        source = InversionEngine.open_root(
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        )
        target = Triad(root=Note('F', 4), triad_type=TriadType.MAJOR)
        
        result = vlsm.voice_lead(source, target)
        
        assert result.mode == VLMode.COUNTERPOINT
        assert 'motion' in result.narrative.lower()
    
    def test_orchestration_mode(self):
        """Test orchestration voice leading mode."""
        vlsm = VoiceLeadingSmartModule(
            mode=VLMode.ORCHESTRATION,
            instruments={'top': 'violin', 'middle': 'viola', 'bottom': 'cello'}
        )
        
        source = InversionEngine.open_root(
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        )
        target = Triad(root=Note('G', 4), triad_type=TriadType.MAJOR)
        
        result = vlsm.voice_lead(source, target)
        
        assert result.mode == VLMode.ORCHESTRATION
    
    def test_progression_voice_leading(self):
        """Test voice leading an entire progression."""
        vlsm = VoiceLeadingSmartModule(mode=VLMode.FUNCTIONAL)
        
        triads = [
            InversionEngine.open_root(Triad(root=Note('D', 4), triad_type=TriadType.MINOR)),
            Triad(root=Note('G', 4), triad_type=TriadType.MAJOR),
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR),
        ]
        
        results = vlsm.voice_lead_progression(triads)
        
        assert len(results) == 2  # Two transitions
    
    def test_parallel_fifth_avoidance(self):
        """Test that parallel fifths can be avoided."""
        vlsm = VoiceLeadingSmartModule(
            mode=VLMode.FUNCTIONAL,
            allow_parallel_fifths=False
        )
        
        # This is a configuration test - the module should be configured correctly
        assert not vlsm.allow_parallel_fifths
    
    def test_max_voice_leap_constraint(self):
        """Test maximum voice leap constraint."""
        vlsm = VoiceLeadingSmartModule(max_voice_leap=7)
        
        assert vlsm.max_voice_leap == 7


class TestVoiceLeadConvenienceFunction:
    """Tests for the voice_lead convenience function."""
    
    def test_basic_voice_lead(self):
        """Test basic voice leading with convenience function."""
        source = InversionEngine.open_root(
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        )
        target = Triad(root=Note('F', 4), triad_type=TriadType.MAJOR)
        
        result = voice_lead(source, target, mode='functional')
        
        assert isinstance(result, VoiceLeadingResult)
    
    def test_voice_lead_with_mode_override(self):
        """Test voice leading with mode override."""
        source = InversionEngine.open_root(
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        )
        target = Triad(root=Note('F', 4), triad_type=TriadType.MAJOR)
        
        result = voice_lead(source, target, mode='modal')
        
        assert result.mode == VLMode.MODAL


class TestVoiceLeadingResult:
    """Tests for VoiceLeadingResult."""
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        vlsm = VoiceLeadingSmartModule()
        
        source = InversionEngine.open_root(
            Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        )
        target = Triad(root=Note('G', 4), triad_type=TriadType.MAJOR)
        
        result = vlsm.voice_lead(source, target)
        data = result.to_dict()
        
        assert 'source' in data
        assert 'target' in data
        assert 'motions' in data
        assert 'narrative' in data
        assert 'score' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

