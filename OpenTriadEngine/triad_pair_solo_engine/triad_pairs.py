"""
Triad Pair Selection Engine
============================

Implements logic for selecting triad pairs:
- Diatonic pairs (adjacent and non-adjacent scale-degree triads)
- Klemonic pairs (stable + tension triads per Jordan Klemons)
- UST pairs (Upper Structure Triads for altered dominants, etc.)
- Altered Dominant pairs (7b9, 7alt, dim whole-tone derived)
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum
import sys
import os

# Add parent directory for Open Triad Engine imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from open_triad_engine.core import Note, Triad, TriadQuality
    from open_triad_engine.transformations import ClosedToOpenConverter, InversionEngine
except ImportError:
    # Fallback definitions if Open Triad Engine not available
    class TriadQuality(Enum):
        MAJOR = "major"
        MINOR = "minor"
        DIMINISHED = "dim"
        AUGMENTED = "aug"


# Scale degree triads for various scales
MAJOR_SCALE_TRIADS = [
    ("I", "major"), ("ii", "minor"), ("iii", "minor"), ("IV", "major"),
    ("V", "major"), ("vi", "minor"), ("vii°", "dim")
]

MINOR_SCALE_TRIADS = [
    ("i", "minor"), ("ii°", "dim"), ("III", "major"), ("iv", "minor"),
    ("v", "minor"), ("VI", "major"), ("VII", "major")
]

MELODIC_MINOR_TRIADS = [
    ("i", "minor"), ("ii", "minor"), ("III+", "aug"), ("IV", "major"),
    ("V", "major"), ("vi°", "dim"), ("vii°", "dim")
]

DORIAN_TRIADS = [
    ("i", "minor"), ("ii", "minor"), ("III", "major"), ("IV", "major"),
    ("v", "minor"), ("vi°", "dim"), ("VII", "major")
]


@dataclass
class TriadPair:
    """
    Represents a pair of triads for intervallic soloing.
    
    Attributes:
        triad_a: First triad (root, quality)
        triad_b: Second triad (root, quality)
        relationship: Description of the pair relationship
        tension_level: 0.0 (consonant) to 1.0 (maximum tension)
        source_scale: The scale these triads derive from
        chord_context: Optional chord this pair is designed for
    """
    triad_a: Tuple[str, str]  # (root, quality)
    triad_b: Tuple[str, str]
    relationship: str = "diatonic"
    tension_level: float = 0.5
    source_scale: str = "major"
    chord_context: Optional[str] = None
    
    def __repr__(self):
        return (f"TriadPair({self.triad_a[0]}{self.triad_a[1]} + "
                f"{self.triad_b[0]}{self.triad_b[1]}, {self.relationship})")
    
    def get_interval(self) -> int:
        """Get the interval in semitones between the two roots."""
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        enharmonics = {"Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#", 
                       "Ab": "G#", "Bb": "A#", "Cb": "B"}
        
        root_a = enharmonics.get(self.triad_a[0], self.triad_a[0])
        root_b = enharmonics.get(self.triad_b[0], self.triad_b[0])
        
        try:
            idx_a = notes.index(root_a)
            idx_b = notes.index(root_b)
            return (idx_b - idx_a) % 12
        except ValueError:
            return 0


class TriadPairSelector:
    """
    Selects triad pairs based on harmonic context and pair type.
    """
    
    CHROMATIC_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # Scale interval patterns (in semitones)
    SCALE_PATTERNS = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "aeolian": [0, 2, 3, 5, 7, 8, 10],
        "locrian": [0, 1, 3, 5, 6, 8, 10],
        "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
        "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
        "whole_tone": [0, 2, 4, 6, 8, 10],
        "diminished": [0, 2, 3, 5, 6, 8, 9, 11],  # whole-half
        "altered": [0, 1, 3, 4, 6, 8, 10],
        "lydian_dominant": [0, 2, 4, 6, 7, 9, 10],
    }
    
    # Triad qualities for scale degrees (in major/minor contexts)
    SCALE_DEGREE_QUALITIES = {
        "major": ["major", "minor", "minor", "major", "major", "minor", "dim"],
        "minor": ["minor", "dim", "major", "minor", "minor", "major", "major"],
        "dorian": ["minor", "minor", "major", "major", "minor", "dim", "major"],
        "melodic_minor": ["minor", "minor", "aug", "major", "major", "dim", "dim"],
        "lydian": ["major", "major", "minor", "dim", "major", "minor", "minor"],
        "mixolydian": ["major", "minor", "dim", "major", "minor", "minor", "major"],
        "altered": ["dim", "dim", "minor", "minor", "major", "major", "minor"],
    }
    
    # Klemonic pairs: (chord quality) -> [(stable_interval, stable_quality, tension_interval, tension_quality)]
    KLEMONIC_PAIRS = {
        "maj7": [
            (0, "major", 2, "minor"),   # I + ii (sweet tension)
            (0, "major", 7, "minor"),   # I + vii (leading tone tension)
            (4, "minor", 7, "minor"),   # iii + vii
        ],
        "m7": [
            (0, "minor", 2, "minor"),   # i + ii
            (0, "minor", 5, "minor"),   # i + v
            (3, "major", 5, "minor"),   # III + v
        ],
        "7": [
            (0, "major", 2, "minor"),   # I + ii (creates 9th tension)
            (0, "major", 6, "dim"),     # I + vii dim (tritone)
            (4, "minor", 6, "dim"),     # iii + vii dim
        ],
        "m7b5": [
            (0, "dim", 3, "minor"),     # i dim + bIII
            (0, "dim", 5, "major"),     # i dim + bVI
        ],
        "dim7": [
            (0, "dim", 3, "dim"),       # stacked dim (symmetric)
            (0, "dim", 6, "dim"),       # tritone dim pair
        ],
    }
    
    # UST (Upper Structure Triad) pairs for specific chord types
    UST_PAIRS = {
        "7alt": [
            ("Eb", "major", "F#", "major"),   # bVI + #IV over G7alt
            ("Db", "major", "E", "major"),    # b5 + 6 triads
            ("Ab", "minor", "B", "minor"),    # altered extensions
        ],
        "7#11": [
            ("D", "major", "F#", "dim"),      # II + #IV dim over C7#11
            ("A", "minor", "D", "major"),     # Lydian color
        ],
        "7b9": [
            ("Ab", "major", "B", "dim"),      # b9 + dim structure
            ("Db", "major", "E", "dim"),      # tritone sub colors
        ],
        "m(maj7)": [
            ("Eb", "major", "B", "major"),    # bIII + VII over Cm(maj7)
            ("G", "minor", "B", "major"),     # i + VII
        ],
        "maj7#5": [
            ("E", "major", "Ab", "major"),    # #5 pair
            ("C", "major", "E", "aug"),       # augmented tension
        ],
    }
    
    # Altered dominant pairs (derived from diminished whole-tone / altered scale)
    ALTERED_DOMINANT_PAIRS = {
        "7b9": [
            (1, "major", 4, "major"),   # b9 triad + 3 triad
            (1, "minor", 7, "dim"),
        ],
        "7#9": [
            (3, "minor", 7, "major"),   # #9 minor + 7 major
            (3, "major", 6, "dim"),
        ],
        "7alt": [
            (1, "major", 6, "major"),   # b9 + b13
            (3, "minor", 6, "dim"),     # #9 minor + b13 dim
            (4, "major", 8, "major"),   # 3 + #5
        ],
        "7#5": [
            (0, "aug", 4, "major"),     # augmented root + major 3rd
            (4, "major", 8, "major"),   # whole tone pair
        ],
    }
    
    def __init__(self, key: str = "C", scale: str = "major"):
        """
        Initialize the selector.
        
        Args:
            key: Root key
            scale: Scale type
        """
        self.key = key
        self.scale = scale.lower()
        self.scale_notes = self._build_scale_notes()
    
    def _get_note_index(self, note: str) -> int:
        """Get chromatic index for a note."""
        enharmonics = {"Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#",
                       "Ab": "G#", "Bb": "A#", "Cb": "B"}
        note = enharmonics.get(note, note)
        return self.CHROMATIC_NOTES.index(note)
    
    def _get_note_at_interval(self, root: str, semitones: int) -> str:
        """Get note at interval from root."""
        root_idx = self._get_note_index(root)
        target_idx = (root_idx + semitones) % 12
        return self.CHROMATIC_NOTES[target_idx]
    
    def _build_scale_notes(self) -> List[str]:
        """Build the scale notes for the current key."""
        pattern = self.SCALE_PATTERNS.get(self.scale, self.SCALE_PATTERNS["major"])
        return [self._get_note_at_interval(self.key, interval) for interval in pattern]
    
    def get_diatonic_pairs(self, adjacent_only: bool = False) -> List[TriadPair]:
        """
        Get diatonic triad pairs from the scale.
        
        Args:
            adjacent_only: If True, only return adjacent pairs (I-II, II-III, etc.)
        
        Returns:
            List of TriadPair objects
        """
        pairs = []
        qualities = self.SCALE_DEGREE_QUALITIES.get(
            self.scale, self.SCALE_DEGREE_QUALITIES["major"]
        )
        
        # Ensure we have enough qualities for the scale
        while len(qualities) < len(self.scale_notes):
            qualities = qualities + qualities
        qualities = qualities[:len(self.scale_notes)]
        
        if adjacent_only:
            # Adjacent pairs only
            for i in range(len(self.scale_notes)):
                next_i = (i + 1) % len(self.scale_notes)
                pairs.append(TriadPair(
                    triad_a=(self.scale_notes[i], qualities[i]),
                    triad_b=(self.scale_notes[next_i], qualities[next_i]),
                    relationship=f"diatonic_adjacent_{i+1}_{next_i+1}",
                    tension_level=0.3,
                    source_scale=f"{self.key}_{self.scale}"
                ))
        else:
            # All combinations
            for i in range(len(self.scale_notes)):
                for j in range(i + 1, len(self.scale_notes)):
                    # Calculate tension based on interval
                    interval = (j - i) % len(self.scale_notes)
                    tension = self._calculate_diatonic_tension(interval)
                    
                    pairs.append(TriadPair(
                        triad_a=(self.scale_notes[i], qualities[i]),
                        triad_b=(self.scale_notes[j], qualities[j]),
                        relationship=f"diatonic_{i+1}_{j+1}",
                        tension_level=tension,
                        source_scale=f"{self.key}_{self.scale}"
                    ))
        
        return pairs
    
    def _calculate_diatonic_tension(self, scale_interval: int) -> float:
        """Calculate tension level for diatonic interval."""
        # Tension mapping: 2nds and 7ths = high, 3rds/6ths = low, 4ths/5ths = medium
        tension_map = {
            1: 0.7,  # 2nd - high tension
            2: 0.4,  # 3rd - lower
            3: 0.5,  # 4th - medium
            4: 0.3,  # 5th - stable
            5: 0.4,  # 6th - lower
            6: 0.8,  # 7th - high tension
        }
        return tension_map.get(scale_interval, 0.5)
    
    def get_klemonic_pairs(self, chord_quality: str = "maj7") -> List[TriadPair]:
        """
        Get Klemonic triad pairs (stable + tension) per Jordan Klemons principles.
        
        Args:
            chord_quality: The chord quality (maj7, m7, 7, m7b5, dim7)
        
        Returns:
            List of TriadPair objects
        """
        pairs = []
        pair_definitions = self.KLEMONIC_PAIRS.get(chord_quality, self.KLEMONIC_PAIRS["maj7"])
        
        for stable_interval, stable_qual, tension_interval, tension_qual in pair_definitions:
            stable_root = self._get_note_at_interval(self.key, stable_interval)
            tension_root = self._get_note_at_interval(self.key, tension_interval)
            
            pairs.append(TriadPair(
                triad_a=(stable_root, stable_qual),
                triad_b=(tension_root, tension_qual),
                relationship="klemonic",
                tension_level=0.6,
                source_scale=f"{self.key}_{self.scale}",
                chord_context=f"{self.key}{chord_quality}"
            ))
        
        return pairs
    
    def get_ust_pairs(self, chord_type: str = "7alt") -> List[TriadPair]:
        """
        Get Upper Structure Triad pairs for altered dominants, Lydian, etc.
        
        Args:
            chord_type: The chord type (7alt, 7#11, 7b9, m(maj7), maj7#5)
        
        Returns:
            List of TriadPair objects
        """
        pairs = []
        pair_definitions = self.UST_PAIRS.get(chord_type, self.UST_PAIRS["7alt"])
        
        for pair_def in pair_definitions:
            # UST pairs are defined with absolute note names, transpose to key
            root_offset = self._get_note_index(self.key)
            
            # For simplicity, we'll transpose the generic pairs
            triad_a_root = self._get_note_at_interval("C", 
                self._get_note_index(pair_def[0]) + root_offset)
            triad_b_root = self._get_note_at_interval("C",
                self._get_note_index(pair_def[2]) + root_offset)
            
            pairs.append(TriadPair(
                triad_a=(triad_a_root, pair_def[1]),
                triad_b=(triad_b_root, pair_def[3]),
                relationship="ust",
                tension_level=0.8,
                source_scale=f"{self.key}_{chord_type}",
                chord_context=f"{self.key}{chord_type}"
            ))
        
        return pairs
    
    def get_altered_dominant_pairs(self, alt_type: str = "7alt") -> List[TriadPair]:
        """
        Get altered dominant triad pairs derived from 7b9, 7alt, dim whole-tone.
        
        Args:
            alt_type: The altered type (7b9, 7#9, 7alt, 7#5)
        
        Returns:
            List of TriadPair objects
        """
        pairs = []
        pair_definitions = self.ALTERED_DOMINANT_PAIRS.get(
            alt_type, self.ALTERED_DOMINANT_PAIRS["7alt"]
        )
        
        for interval_a, qual_a, interval_b, qual_b in pair_definitions:
            root_a = self._get_note_at_interval(self.key, interval_a)
            root_b = self._get_note_at_interval(self.key, interval_b)
            
            pairs.append(TriadPair(
                triad_a=(root_a, qual_a),
                triad_b=(root_b, qual_b),
                relationship="altered_dominant",
                tension_level=0.9,
                source_scale=f"{self.key}_altered",
                chord_context=f"{self.key}{alt_type}"
            ))
        
        return pairs
    
    def get_pairs_for_progression(
        self, 
        progression: List[str], 
        pair_type: str = "diatonic"
    ) -> Dict[str, List[TriadPair]]:
        """
        Get triad pairs for each chord in a progression.
        
        Args:
            progression: List of chord symbols
            pair_type: Type of pairs to generate
        
        Returns:
            Dict mapping chord symbols to their triad pairs
        """
        result = {}
        
        for chord in progression:
            # Parse chord root and quality
            root, quality = self._parse_chord(chord)
            
            # Create a new selector for this chord's context
            local_selector = TriadPairSelector(key=root, scale=self.scale)
            
            if pair_type == "diatonic":
                result[chord] = local_selector.get_diatonic_pairs()
            elif pair_type == "klemonic":
                result[chord] = local_selector.get_klemonic_pairs(quality)
            elif pair_type == "ust":
                # Determine UST type based on quality
                ust_type = self._quality_to_ust_type(quality)
                result[chord] = local_selector.get_ust_pairs(ust_type)
            elif pair_type == "altered_dominant":
                alt_type = self._quality_to_alt_type(quality)
                result[chord] = local_selector.get_altered_dominant_pairs(alt_type)
            else:
                result[chord] = local_selector.get_diatonic_pairs()
        
        return result
    
    def _parse_chord(self, chord: str) -> Tuple[str, str]:
        """Parse a chord symbol into root and quality."""
        # Handle sharps and flats in root
        if len(chord) > 1 and chord[1] in ['#', 'b']:
            root = chord[:2]
            quality = chord[2:] if len(chord) > 2 else "maj7"
        else:
            root = chord[0]
            quality = chord[1:] if len(chord) > 1 else "maj7"
        
        # Normalize quality
        quality_map = {
            "": "maj7", "maj7": "maj7", "M7": "maj7", "Δ": "maj7", "Δ7": "maj7",
            "m7": "m7", "-7": "m7", "min7": "m7",
            "7": "7", "dom7": "7",
            "m7b5": "m7b5", "-7b5": "m7b5", "ø": "m7b5", "ø7": "m7b5",
            "dim7": "dim7", "°7": "dim7", "o7": "dim7",
            "7alt": "7alt", "alt": "7alt",
            "7#11": "7#11", "7#9": "7#9", "7b9": "7b9",
        }
        quality = quality_map.get(quality, "maj7")
        
        return root, quality
    
    def _quality_to_ust_type(self, quality: str) -> str:
        """Map chord quality to UST type."""
        mapping = {
            "7alt": "7alt", "alt": "7alt",
            "7#11": "7#11",
            "7b9": "7b9",
            "m(maj7)": "m(maj7)",
            "maj7#5": "maj7#5",
        }
        return mapping.get(quality, "7alt")
    
    def _quality_to_alt_type(self, quality: str) -> str:
        """Map chord quality to altered dominant type."""
        mapping = {
            "7b9": "7b9",
            "7#9": "7#9",
            "7alt": "7alt",
            "7#5": "7#5",
        }
        return mapping.get(quality, "7alt")

