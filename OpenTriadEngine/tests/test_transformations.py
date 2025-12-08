"""
Unit Tests for Transformation Modules
=====================================

Tests for closed→open conversions, inversions, and scale mapping.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from open_triad_engine.core import Note, Triad, TriadType, Inversion
from open_triad_engine.transformations import (
    ClosedToOpenConverter, InversionEngine, ScaleMapper,
    DropVoicing, closed_to_open, map_triads_to_scale
)


class TestClosedToOpenConverter:
    """Tests for closed to open triad conversion."""
    
    def test_drop2_conversion(self):
        """Test drop-2 voicing conversion."""
        closed = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        open_triad = ClosedToOpenConverter.open_drop2(closed)
        
        # Open voicing should span more than octave
        assert open_triad.outer_interval > 12
    
    def test_drop3_conversion(self):
        """Test drop-3 voicing conversion."""
        closed = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        open_triad = ClosedToOpenConverter.open_drop3(closed)
        
        assert open_triad.outer_interval > 12
    
    def test_super_open_conversion(self):
        """Test super-open voicing conversion."""
        closed = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        open_triad = ClosedToOpenConverter.super_open(closed)
        
        # Super open should span even wider
        assert open_triad.outer_interval > 20
    
    def test_convert_method(self):
        """Test the generic convert method."""
        closed = Triad(root=Note('G', 4), triad_type=TriadType.MINOR)
        
        drop2 = ClosedToOpenConverter.convert(closed, DropVoicing.DROP2)
        drop3 = ClosedToOpenConverter.convert(closed, DropVoicing.DROP3)
        
        assert drop2.is_open
        assert drop3.is_open
    
    def test_all_open_voicings(self):
        """Test generating all open voicings."""
        closed = Triad(root=Note('D', 4), triad_type=TriadType.MAJOR)
        voicings = ClosedToOpenConverter.all_open_voicings(closed)
        
        assert 'drop2' in voicings
        assert 'drop3' in voicings
        assert 'super_open' in voicings
        
        for name, voicing in voicings.items():
            assert voicing.is_open


class TestInversionEngine:
    """Tests for the inversion engine."""
    
    def test_open_root_inversion(self):
        """Test open root position."""
        triad = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        open_root = InversionEngine.open_root(triad)
        
        assert open_root.bass_note.name == 'C'
        assert open_root.is_open
    
    def test_open_first_inversion(self):
        """Test open first inversion."""
        triad = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        open_first = InversionEngine.open_first(triad)
        
        assert open_first.bass_note.name == 'E'
    
    def test_open_second_inversion(self):
        """Test open second inversion."""
        triad = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        open_second = InversionEngine.open_second(triad)
        
        assert open_second.bass_note.name == 'G'
    
    def test_all_inversions(self):
        """Test generating all inversions."""
        triad = Triad(root=Note('F', 4), triad_type=TriadType.MINOR)
        inversions = InversionEngine.all_inversions(triad)
        
        assert 'open_root' in inversions
        assert 'open_first' in inversions
        assert 'open_second' in inversions
    
    def test_cycle_inversions_ascending(self):
        """Test ascending inversion cycle."""
        triad = Triad(root=Note('A', 4), triad_type=TriadType.MAJOR)
        cycle = InversionEngine.cycle_inversions(triad, ascending=True)
        
        assert len(cycle) == 3
        # Ascending: 1st → 2nd → root
        assert cycle[0].inversion == Inversion.FIRST
        assert cycle[1].inversion == Inversion.SECOND
        assert cycle[2].inversion == Inversion.ROOT
    
    def test_cycle_inversions_descending(self):
        """Test descending inversion cycle."""
        triad = Triad(root=Note('A', 4), triad_type=TriadType.MAJOR)
        cycle = InversionEngine.cycle_inversions(triad, ascending=False)
        
        assert len(cycle) == 3
        # Descending: root → 2nd → 1st
        assert cycle[0].inversion == Inversion.ROOT


class TestScaleMapper:
    """Tests for scale mapping."""
    
    def test_get_scale_notes(self):
        """Test getting scale notes."""
        mapper = ScaleMapper('C')
        notes = mapper.get_scale_notes('ionian')
        
        assert notes == ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    
    def test_get_scale_notes_different_root(self):
        """Test scale notes with different root."""
        mapper = ScaleMapper('G')
        notes = mapper.get_scale_notes('ionian')
        
        assert notes[0] == 'G'
        assert len(notes) == 7
    
    def test_get_diatonic_triads(self):
        """Test getting diatonic triads."""
        mapper = ScaleMapper('C')
        triads = mapper.get_diatonic_triads('ionian')
        
        assert len(triads) == 7
        
        # C major scale: C, Dm, Em, F, G, Am, Bdim
        assert triads[0].triad_type == TriadType.MAJOR  # C
        assert triads[1].triad_type == TriadType.MINOR  # Dm
        assert triads[6].triad_type == TriadType.DIMINISHED  # Bdim
    
    def test_map_triad_across_scale(self):
        """Test mapping a triad shape across a scale."""
        mapper = ScaleMapper('C')
        source = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        
        mapped = mapper.map_triad_across_scale(source, 'ionian', preserve_shape=True)
        
        assert len(mapped) == 7
        # With preserve_shape=True, all should be major
        for triad in mapped:
            assert triad.triad_type == TriadType.MAJOR
    
    def test_chromatic_triads(self):
        """Test generating chromatic triads."""
        mapper = ScaleMapper('C')
        triads = mapper.chromatic_triads(TriadType.MINOR)
        
        assert len(triads) == 12
        for triad in triads:
            assert triad.triad_type == TriadType.MINOR
    
    def test_get_triads_from_progression(self):
        """Test parsing chord progression."""
        mapper = ScaleMapper('C')
        triads = mapper.get_triads_from_progression(['Dm', 'G', 'C'])
        
        assert len(triads) == 3
        assert triads[0].root.name == 'D'
        assert triads[0].triad_type == TriadType.MINOR
        assert triads[1].root.name == 'G'
        assert triads[2].root.name == 'C'


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_closed_to_open_function(self):
        """Test closed_to_open convenience function."""
        triad = Triad(root=Note('E', 4), triad_type=TriadType.MINOR)
        open_triad = closed_to_open(triad, 'drop2')
        
        assert open_triad.is_open
    
    def test_map_triads_to_scale_function(self):
        """Test map_triads_to_scale convenience function."""
        triads = map_triads_to_scale('major', 'dorian', 'D')
        
        assert len(triads) == 7


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

