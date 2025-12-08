"""
Parameter Normalizer for CEO Module
====================================

Reconciles shared parameters so all engines operate consistently.
Normalizes scales, progressions, modes, string sets, etc.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re


@dataclass
class NormalizedParams:
    """
    Normalized parameters ready for any engine.
    
    Attributes:
        key: Normalized key name
        scale: Normalized scale name
        scale_intervals: Scale as interval list
        progression: Normalized chord progression
        mode: Normalized operating mode
        string_set: Normalized string set
        register_limits: Low/high register (MIDI)
        rhythmic_style: Normalized rhythm style
        triad_types: Available triad types for this scale
    """
    key: str
    scale: str
    scale_intervals: List[int]
    progression: Optional[List[Dict[str, str]]]
    mode: str
    string_set: str
    register_limits: Tuple[int, int]
    rhythmic_style: str
    triad_types: List[str]


class ParameterNormalizer:
    """
    Normalizes parameters for consistent cross-engine operation.
    """
    
    # Scale name mappings
    SCALE_ALIASES = {
        # Major/Ionian variants
        "maj": "major", "ionian": "major", "ion": "major",
        
        # Minor variants
        "min": "minor", "natural minor": "minor", "nat min": "minor",
        
        # Mode abbreviations
        "dor": "dorian", "phryg": "phrygian", "lyd": "lydian",
        "mixo": "mixolydian", "aeo": "aeolian", "loc": "locrian",
        
        # Melodic minor
        "mel min": "melodic_minor", "melodic minor": "melodic_minor",
        "jazz minor": "melodic_minor",
        
        # Harmonic minor
        "harm min": "harmonic_minor", "harmonic minor": "harmonic_minor",
        
        # Symmetric scales
        "whole tone": "whole_tone", "wholetone": "whole_tone", "wt": "whole_tone",
        "dim": "diminished", "octatonic": "diminished",
        "half whole": "diminished", "hw": "diminished",
        "whole half": "whole_half_dim", "wh": "whole_half_dim",
        
        # Altered
        "alt": "altered", "superlocrian": "altered", "super locrian": "altered",
        "diminished whole tone": "altered",
        
        # Lydian dominant
        "lyd dom": "lydian_dominant", "lydian dominant": "lydian_dominant",
        "mixo #11": "lydian_dominant", "overtone": "lydian_dominant",
        
        # Pentatonics
        "pent": "pentatonic_major", "pent maj": "pentatonic_major",
        "pentatonic": "pentatonic_major",
        "pent min": "pentatonic_minor", "minor pentatonic": "pentatonic_minor",
        
        # Blues
        "blues": "blues", "blues scale": "blues",
    }
    
    # Scale interval definitions
    SCALE_INTERVALS = {
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
        "diminished": [0, 2, 3, 5, 6, 8, 9, 11],
        "whole_half_dim": [0, 2, 3, 5, 6, 8, 9, 11],
        "altered": [0, 1, 3, 4, 6, 8, 10],
        "lydian_dominant": [0, 2, 4, 6, 7, 9, 10],
        "pentatonic_major": [0, 2, 4, 7, 9],
        "pentatonic_minor": [0, 3, 5, 7, 10],
        "blues": [0, 3, 5, 6, 7, 10],
    }
    
    # Mode mappings
    MODE_ALIASES = {
        "func": "functional", "tonal": "functional", "traditional": "functional",
        "mod": "modal", "static": "modal", "vamp": "modal",
        "int": "intervallic", "angular": "intervallic", "modern": "intervallic",
        "cm": "chord_melody", "chordal": "chord_melody",
        "cp": "counterpoint", "contrapuntal": "counterpoint",
        "orch": "orchestration",
    }
    
    # String set mappings
    STRING_SET_ALIASES = {
        "low": "6-4", "bass": "6-4", "bottom": "6-4",
        "mid": "5-3", "middle": "5-3",
        "high": "4-2", "treble": "4-2", "top": "4-2",
        "all": "auto", "any": "auto", "flexible": "auto",
    }
    
    # Rhythm style mappings
    RHYTHM_ALIASES = {
        "even": "straight", "straight eighths": "straight",
        "jazz": "swing", "swung": "swing",
        "3": "triplet", "triplets": "triplet", "ternary": "triplet",
        "synco": "syncopated", "off-beat": "syncopated",
        "poly": "polyrhythmic", "cross-rhythm": "polyrhythmic",
    }
    
    # Chord symbol patterns
    CHORD_PATTERNS = {
        r"([A-G][#b]?)maj7?": lambda m: {"root": m.group(1), "quality": "maj7"},
        r"([A-G][#b]?)m7": lambda m: {"root": m.group(1), "quality": "m7"},
        r"([A-G][#b]?)7": lambda m: {"root": m.group(1), "quality": "7"},
        r"([A-G][#b]?)m7b5": lambda m: {"root": m.group(1), "quality": "m7b5"},
        r"([A-G][#b]?)dim7?": lambda m: {"root": m.group(1), "quality": "dim7"},
        r"([A-G][#b]?)7alt": lambda m: {"root": m.group(1), "quality": "7alt"},
        r"([A-G][#b]?)7#11": lambda m: {"root": m.group(1), "quality": "7#11"},
        r"([A-G][#b]?)\+": lambda m: {"root": m.group(1), "quality": "aug"},
        r"([A-G][#b]?)sus4?": lambda m: {"root": m.group(1), "quality": "sus4"},
    }
    
    # Roman numeral to interval
    ROMAN_TO_INTERVAL = {
        "I": 0, "II": 2, "III": 4, "IV": 5, "V": 7, "VI": 9, "VII": 11,
        "i": 0, "ii": 2, "iii": 4, "iv": 5, "v": 7, "vi": 9, "vii": 11,
        "bII": 1, "bIII": 3, "bV": 6, "bVI": 8, "bVII": 10,
        "#IV": 6, "#iv": 6,
    }
    
    # Key to MIDI offset
    KEY_TO_MIDI = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
        "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
    }
    
    MIDI_TO_KEY = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    def __init__(self):
        """Initialize the normalizer."""
        pass
    
    def normalize_key(self, key: str) -> str:
        """Normalize a key name."""
        key = key.strip()
        if len(key) == 0:
            return "C"
        
        # Capitalize first letter
        normalized = key[0].upper()
        
        # Handle accidentals
        if len(key) > 1:
            if key[1] in ['#', 'b']:
                normalized += key[1]
        
        # Validate
        if normalized not in self.KEY_TO_MIDI:
            return "C"
        
        return normalized
    
    def normalize_scale(self, scale: str) -> str:
        """Normalize a scale name."""
        scale_lower = scale.lower().strip()
        
        # Check aliases
        if scale_lower in self.SCALE_ALIASES:
            return self.SCALE_ALIASES[scale_lower]
        
        # Check if already normalized
        if scale_lower in self.SCALE_INTERVALS:
            return scale_lower
        
        # Default
        return "major"
    
    def get_scale_intervals(self, scale: str) -> List[int]:
        """Get interval list for a scale."""
        normalized = self.normalize_scale(scale)
        return self.SCALE_INTERVALS.get(normalized, self.SCALE_INTERVALS["major"])
    
    def normalize_mode(self, mode: str) -> str:
        """Normalize an operating mode."""
        mode_lower = mode.lower().strip()
        
        if mode_lower in self.MODE_ALIASES:
            return self.MODE_ALIASES[mode_lower]
        
        valid_modes = ["functional", "modal", "intervallic", "chord_melody", 
                       "counterpoint", "orchestration"]
        if mode_lower in valid_modes:
            return mode_lower
        
        return "modal"
    
    def normalize_string_set(self, string_set: str) -> str:
        """Normalize a string set specification."""
        ss_lower = string_set.lower().strip()
        
        if ss_lower in self.STRING_SET_ALIASES:
            return self.STRING_SET_ALIASES[ss_lower]
        
        if ss_lower in ["6-4", "5-3", "4-2", "auto"]:
            return ss_lower
        
        return "auto"
    
    def normalize_rhythm(self, rhythm: str) -> str:
        """Normalize a rhythmic style."""
        rhythm_lower = rhythm.lower().strip()
        
        if rhythm_lower in self.RHYTHM_ALIASES:
            return self.RHYTHM_ALIASES[rhythm_lower]
        
        valid = ["straight", "swing", "triplet", "syncopated", "polyrhythmic"]
        if rhythm_lower in valid:
            return rhythm_lower
        
        return "swing"
    
    def normalize_progression(
        self, 
        progression: List[str],
        key: str = "C"
    ) -> List[Dict[str, str]]:
        """
        Normalize a chord progression.
        
        Handles:
        - Chord symbols (Dm7, G7, Cmaj7)
        - Roman numerals (ii, V, I)
        - Scale degrees (2m7, 5dom, 1maj7)
        
        Returns list of dicts with 'root' and 'quality'.
        """
        normalized = []
        key_offset = self.KEY_TO_MIDI.get(self.normalize_key(key), 0)
        
        for chord in progression:
            chord = chord.strip()
            parsed = None
            
            # Try Roman numerals first
            roman_match = re.match(r'([b#]?[IViv]+)(.*)', chord)
            if roman_match:
                roman = roman_match.group(1)
                suffix = roman_match.group(2)
                
                interval = self.ROMAN_TO_INTERVAL.get(roman, 0)
                root_midi = (key_offset + interval) % 12
                root = self.MIDI_TO_KEY[root_midi]
                
                # Determine quality from case and suffix
                if roman.islower():
                    quality = "m7"
                else:
                    quality = "maj7"
                
                if "7" in suffix and not "maj" in suffix.lower():
                    quality = "7"
                if "dim" in suffix.lower() or "o" in suffix:
                    quality = "dim7"
                if "m7b5" in suffix or "ø" in suffix:
                    quality = "m7b5"
                
                parsed = {"root": root, "quality": quality}
            
            # Try chord symbol patterns
            if parsed is None:
                for pattern, handler in self.CHORD_PATTERNS.items():
                    match = re.match(pattern, chord, re.IGNORECASE)
                    if match:
                        parsed = handler(match)
                        break
            
            # Fallback: treat as simple chord
            if parsed is None:
                root_match = re.match(r'([A-G][#b]?)', chord)
                if root_match:
                    parsed = {"root": root_match.group(1), "quality": "maj7"}
                else:
                    parsed = {"root": "C", "quality": "maj7"}
            
            normalized.append(parsed)
        
        return normalized
    
    def get_triad_types_for_scale(self, scale: str) -> List[str]:
        """Get available triad types for a scale."""
        normalized = self.normalize_scale(scale)
        
        # Major/Ionian family
        if normalized in ["major", "lydian", "mixolydian"]:
            return ["major", "minor", "dim"]
        
        # Minor family
        if normalized in ["minor", "aeolian", "dorian", "phrygian"]:
            return ["minor", "major", "dim"]
        
        # Locrian
        if normalized == "locrian":
            return ["dim", "minor", "major"]
        
        # Melodic minor
        if normalized == "melodic_minor":
            return ["minor", "major", "aug", "dim"]
        
        # Harmonic minor
        if normalized == "harmonic_minor":
            return ["minor", "major", "aug", "dim"]
        
        # Symmetric
        if normalized in ["whole_tone"]:
            return ["aug"]
        
        if normalized in ["diminished", "whole_half_dim"]:
            return ["dim", "minor", "major"]
        
        # Altered
        if normalized == "altered":
            return ["dim", "minor", "major"]
        
        # Default
        return ["major", "minor", "dim"]
    
    def get_register_limits(self, string_set: str) -> Tuple[int, int]:
        """Get register limits for a string set."""
        normalized = self.normalize_string_set(string_set)
        
        # Guitar tuning reference
        # E2=40, A2=45, D3=50, G3=55, B3=59, E4=64
        
        if normalized == "6-4":
            return (40, 62)   # Low E to D4 (strings 6, 5, 4)
        elif normalized == "5-3":
            return (45, 67)   # A2 to G4 (strings 5, 4, 3)
        elif normalized == "4-2":
            return (50, 76)   # D3 to E5 (strings 4, 3, 2)
        else:  # auto
            return (40, 84)   # Full guitar range
    
    def normalize_all(
        self,
        key: str = "C",
        scale: str = "major",
        progression: Optional[List[str]] = None,
        mode: str = "modal",
        string_set: str = "auto",
        rhythmic_style: str = "swing"
    ) -> NormalizedParams:
        """
        Normalize all parameters at once.
        
        Returns a NormalizedParams object ready for any engine.
        """
        norm_key = self.normalize_key(key)
        norm_scale = self.normalize_scale(scale)
        norm_mode = self.normalize_mode(mode)
        norm_string_set = self.normalize_string_set(string_set)
        norm_rhythm = self.normalize_rhythm(rhythmic_style)
        
        norm_progression = None
        if progression:
            norm_progression = self.normalize_progression(progression, norm_key)
        
        return NormalizedParams(
            key=norm_key,
            scale=norm_scale,
            scale_intervals=self.get_scale_intervals(norm_scale),
            progression=norm_progression,
            mode=norm_mode,
            string_set=norm_string_set,
            register_limits=self.get_register_limits(norm_string_set),
            rhythmic_style=norm_rhythm,
            triad_types=self.get_triad_types_for_scale(norm_scale)
        )
    
    def convert_params_for_engine(
        self,
        params: NormalizedParams,
        engine_type: str
    ) -> Dict[str, Any]:
        """
        Convert normalized params to engine-specific format.
        
        Args:
            params: NormalizedParams object
            engine_type: Target engine name
        
        Returns:
            Dictionary of parameters for that engine
        """
        base_params = {
            "key": params.key,
            "scale": params.scale,
            "string_set": params.string_set,
        }
        
        if engine_type == "open_triad":
            return {
                **base_params,
                "mode": params.mode,
                "triad_type": params.triad_types[0] if params.triad_types else "major",
                "register_limits": {
                    "low": params.register_limits[0],
                    "high": params.register_limits[1]
                }
            }
        
        elif engine_type == "etude_generator":
            return {
                **base_params,
                "mode": params.mode,
                "rhythmic_style": params.rhythmic_style,
                "difficulty": "intermediate",
            }
        
        elif engine_type == "triad_pair_solo":
            return {
                **base_params,
                "mode": params.mode,
                "rhythmic_style": params.rhythmic_style,
                "triad_pair_type": "diatonic",
                "contour": "wave",
            }
        
        elif engine_type == "chord_melody":
            return {
                **base_params,
                "harmonisation_style": params.mode if params.mode in 
                    ["diatonic", "reharm", "ust", "functional", "modal"] else "diatonic",
                "texture": "medium",
                "progression": params.progression,
            }
        
        return base_params

