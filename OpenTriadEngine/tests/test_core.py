"""
Unit Tests for Core Module
==========================

Tests for Note, Interval, Triad, and related core classes.
"""

import pytest
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from open_triad_engine.core import (
    Note, Interval, Triad, TriadType, Inversion, VoicingType,
    CHROMATIC_NOTES, create_triad, interval_between
)


class TestNote:
    """Tests for Note class."""
    
    def test_note_creation(self):
        """Test basic note creation."""
        note = Note('C', 4)
        assert note.name == 'C'
        assert note.octave == 4
    
    def test_pitch_class(self):
        """Test pitch class calculation."""
        assert Note('C', 4).pitch_class == 0
        assert Note('G', 4).pitch_class == 7
        assert Note('B', 3).pitch_class == 11
    
    def test_midi_number(self):
        """Test MIDI number conversion."""
        assert Note('C', 4).midi_number == 60  # Middle C
        assert Note('A', 4).midi_number == 69  # A440
        assert Note('C', 5).midi_number == 72
    
    def test_enharmonic_normalization(self):
        """Test that enharmonics are normalized."""
        note = Note('Db', 4)
        assert note.name == 'C#'
    
    def test_transpose(self):
        """Test note transposition."""
        c4 = Note('C', 4)
        g4 = c4.transpose(7)
        assert g4.name == 'G'
        assert g4.octave == 4
        
        c5 = c4.transpose(12)
        assert c5.name == 'C'
        assert c5.octave == 5
    
    def test_interval_to(self):
        """Test interval calculation between notes."""
        c4 = Note('C', 4)
        g4 = Note('G', 4)
        assert c4.interval_to(g4) == 7
    
    def test_from_midi(self):
        """Test creating note from MIDI number."""
        note = Note.from_midi(60)
        assert note.name == 'C'
        assert note.octave == 4
    
    def test_from_string(self):
        """Test parsing note from string."""
        note = Note.from_string('F#5')
        assert note.name == 'F#'
        assert note.octave == 5
    
    def test_comparison(self):
        """Test note comparison."""
        c4 = Note('C', 4)
        d4 = Note('D', 4)
        c5 = Note('C', 5)
        
        assert c4 < d4
        assert c4 < c5
        assert d4 < c5


class TestInterval:
    """Tests for Interval class."""
    
    def test_interval_quality(self):
        """Test interval quality names."""
        assert Interval(0).quality == 'P1'
        assert Interval(7).quality == 'P5'
        assert Interval(4).quality == 'M3'
    
    def test_consonance(self):
        """Test consonance detection."""
        assert Interval(7).is_consonant  # P5
        assert Interval(4).is_consonant  # M3
        assert not Interval(1).is_consonant  # m2
        assert not Interval(6).is_consonant  # TT
    
    def test_step_detection(self):
        """Test step detection."""
        assert Interval(1).is_step
        assert Interval(2).is_step
        assert not Interval(3).is_step


class TestTriad:
    """Tests for Triad class."""
    
    def test_major_triad(self):
        """Test major triad creation."""
        triad = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        
        assert len(triad.voices) == 3
        pitches = sorted([v.pitch_class for v in triad.voices])
        assert pitches == [0, 4, 7]  # C, E, G
    
    def test_minor_triad(self):
        """Test minor triad creation."""
        triad = Triad(root=Note('A', 4), triad_type=TriadType.MINOR)
        
        pitches = sorted([v.pitch_class for v in triad.voices])
        assert pitches == [0, 4, 9]  # A, C, E
    
    def test_diminished_triad(self):
        """Test diminished triad creation."""
        triad = Triad(root=Note('B', 4), triad_type=TriadType.DIMINISHED)
        
        pitches = sorted([v.pitch_class for v in triad.voices])
        assert pitches == [2, 5, 11]  # B, D, F
    
    def test_augmented_triad(self):
        """Test augmented triad creation."""
        triad = Triad(root=Note('C', 4), triad_type=TriadType.AUGMENTED)
        
        pitches = sorted([v.pitch_class for v in triad.voices])
        assert pitches == [0, 4, 8]  # C, E, G#
    
    def test_inversions(self):
        """Test triad inversions."""
        triad_root = Triad(
            root=Note('C', 4),
            triad_type=TriadType.MAJOR,
            inversion=Inversion.ROOT
        )
        assert triad_root.bass_note.name == 'C'
        
        triad_first = Triad(
            root=Note('C', 4),
            triad_type=TriadType.MAJOR,
            inversion=Inversion.FIRST
        )
        assert triad_first.bass_note.name == 'E'
        
        triad_second = Triad(
            root=Note('C', 4),
            triad_type=TriadType.MAJOR,
            inversion=Inversion.SECOND
        )
        assert triad_second.bass_note.name == 'G'
    
    def test_transpose(self):
        """Test triad transposition."""
        c_major = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        d_major = c_major.transpose(2)
        
        assert d_major.root.name == 'D'
    
    def test_symbol(self):
        """Test chord symbol generation."""
        assert Triad(root=Note('C', 4), triad_type=TriadType.MAJOR).symbol == 'C'
        assert Triad(root=Note('A', 4), triad_type=TriadType.MINOR).symbol == 'Am'
        assert Triad(root=Note('B', 4), triad_type=TriadType.DIMINISHED).symbol == 'Bdim'
    
    def test_from_symbol(self):
        """Test creating triad from symbol."""
        triad = Triad.from_symbol('Dm')
        assert triad.root.name == 'D'
        assert triad.triad_type == TriadType.MINOR
        
        triad = Triad.from_symbol('F#dim')
        assert triad.root.name == 'F#'
        assert triad.triad_type == TriadType.DIMINISHED
    
    def test_is_open(self):
        """Test open voicing detection."""
        closed = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        assert not closed.is_open  # Closed voicing spans less than octave
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        triad = Triad(root=Note('C', 4), triad_type=TriadType.MAJOR)
        data = triad.to_dict()
        
        assert 'root' in data
        assert 'triad_type' in data
        assert 'voices' in data
        assert 'symbol' in data


class TestFactoryFunctions:
    """Tests for factory functions."""
    
    def test_create_triad(self):
        """Test create_triad convenience function."""
        triad = create_triad('G', 'minor', 4)
        assert triad.root.name == 'G'
        assert triad.triad_type == TriadType.MINOR
    
    def test_interval_between(self):
        """Test interval_between function."""
        c4 = Note('C', 4)
        e4 = Note('E', 4)
        interval = interval_between(c4, e4)
        assert interval.semitones == 4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

