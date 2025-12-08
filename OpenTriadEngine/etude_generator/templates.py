"""
Structural Etude Templates
==========================

Implements 7 etude template types:
1. Scalar Open-Triad Etude
2. Inversion Cycle Etude
3. Intervallic Etude
4. Position-Locked Etude
5. String-Set Etude
6. ii-V-I Etude
7. Chord-Melody Mini-Etude
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Type
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from open_triad_engine import Note, Triad
from open_triad_engine.transformations import InversionEngine

from .inputs import EtudeConfig, EtudeType, Difficulty, PositionConstraints
from .harmonic import HarmonicGenerator, HarmonicMaterial, HarmonicCell
from .patterns import PatternStitcher, EtudePhrase, BarContent


class EtudeTemplate(ABC):
    """
    Abstract base class for etude templates.
    
    Each template defines:
    - How to generate harmonic material
    - Which patterns to use
    - Structural constraints
    """
    
    name: str = "Base Template"
    description: str = "Base etude template"
    
    def __init__(self, config: EtudeConfig):
        """
        Initialize the template.
        
        Args:
            config: Etude configuration
        """
        self.config = config
        self.harmonic_gen = HarmonicGenerator(config)
        self.pattern_stitcher = PatternStitcher(config)
        self.inversion_engine = InversionEngine()
    
    @abstractmethod
    def generate(self) -> List[EtudePhrase]:
        """Generate the etude content."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get a description of this etude type."""
        pass
    
    def get_metadata(self) -> Dict:
        """Get metadata about the template."""
        return {
            'template_name': self.name,
            'description': self.description,
            'config': self.config.to_dict(),
        }


class ScalarOpenTriadEtude(EtudeTemplate):
    """
    Scalar Open-Triad Etude
    
    Runs all open inversions through the scale degrees.
    Good for learning scale shapes in open voicings.
    """
    
    name = "Scalar Open-Triad Etude"
    description = "Runs through all scale degrees with open triad voicings"
    
    def generate(self) -> List[EtudePhrase]:
        """Generate scalar etude content."""
        # Generate scalar harmonic material
        material = self.harmonic_gen._generate_scalar()
        
        # Stitch patterns
        phrases = self.pattern_stitcher.stitch(material)
        
        # Add guitar positions
        phrases = self.pattern_stitcher.add_guitar_positions(phrases)
        
        return phrases
    
    def get_description(self) -> str:
        return f"""
        Scalar Open-Triad Etude in {self.config.key} {self.config.scale}
        
        This etude runs through all seven scale degrees using open triad voicings.
        Each degree is presented in root position, first inversion, and second inversion
        before moving to the next degree.
        
        Practice tips:
        - Focus on smooth position shifts between inversions
        - Listen for the scale sound emerging from the arpeggiated triads
        - Pay attention to which notes are common between adjacent chords
        """


class InversionCycleEtude(EtudeTemplate):
    """
    Inversion Cycle Etude
    
    Cycles through inversions: open_root → open_first → open_second
    across different positions on the fretboard.
    """
    
    name = "Inversion Cycle Etude"
    description = "Cycles through all three inversions systematically"
    
    def generate(self) -> List[EtudePhrase]:
        """Generate inversion cycle content."""
        material = self.harmonic_gen._generate_inversion_cycle()
        phrases = self.pattern_stitcher.stitch(material)
        phrases = self.pattern_stitcher.add_guitar_positions(phrases)
        return phrases
    
    def get_description(self) -> str:
        return f"""
        Inversion Cycle Etude in {self.config.key} {self.config.scale}
        
        This etude systematically cycles through all three inversions of each chord:
        1. Root position (open_root)
        2. First inversion (open_first)  
        3. Second inversion (open_second)
        
        Practice tips:
        - Notice how the bass note changes with each inversion
        - Feel the different "weight" of each inversion
        - Practice connecting inversions smoothly
        """


class IntervallicEtude(EtudeTemplate):
    """
    Intervallic Etude
    
    Wide-interval open-triad lines with voice-led connections.
    Uses triad pairs for maximum intervallic variety.
    """
    
    name = "Intervallic Etude"
    description = "Wide-interval lines using open triads and triad pairs"
    
    def generate(self) -> List[EtudePhrase]:
        """Generate intervallic content."""
        material = self.harmonic_gen._generate_intervallic()
        
        # Use wider interval patterns
        self.pattern_stitcher.allowed_patterns = [
            p for p in self.pattern_stitcher.allowed_patterns
            if 'skip' in p.value.lower() or 'wave' in p.value.lower() or 'pendulum' in p.value.lower()
        ]
        
        # If no wide patterns available, use all
        if not self.pattern_stitcher.allowed_patterns:
            self.pattern_stitcher = PatternStitcher(self.config)
        
        phrases = self.pattern_stitcher.stitch(material)
        phrases = self.pattern_stitcher.add_guitar_positions(phrases)
        return phrases
    
    def get_description(self) -> str:
        return f"""
        Intervallic Etude in {self.config.key} {self.config.scale}
        
        This etude emphasizes wide intervals and angular melodic motion.
        Uses triad pairs and skip patterns to create modern, intervallic lines.
        
        Practice tips:
        - Focus on accuracy with the larger leaps
        - Maintain a steady pulse despite the wide intervals
        - Listen for the harmonic connection between triad pairs
        """


class PositionLockedEtude(EtudeTemplate):
    """
    Position-Locked Etude
    
    All material stays within one fretboard position/area.
    Great for developing position awareness.
    """
    
    name = "Position-Locked Etude"
    description = "All notes stay within a single fretboard position"
    
    def generate(self) -> List[EtudePhrase]:
        """Generate position-locked content."""
        # Get position constraints
        constraints = self.config.get_position_constraints()
        if constraints is None:
            constraints = PositionConstraints.from_position(5, 4)  # Default: 5th position
        
        material = self.harmonic_gen._generate_diatonic()
        phrases = self.pattern_stitcher.stitch(material)
        
        # Add guitar positions with constraints
        for phrase in phrases:
            for bar in phrase.bars:
                for event in bar.notes:
                    string, fret = self._find_position_in_constraints(
                        event.note, constraints
                    )
                    event.string = string
                    event.fret = fret
        
        return phrases
    
    def _find_position_in_constraints(
        self, 
        note: Note, 
        constraints: PositionConstraints
    ) -> tuple:
        """Find a string/fret combination within position constraints."""
        string_tunings = [40, 45, 50, 55, 59, 64]  # E A D G B e
        midi = note.midi_number
        
        best_string = 6
        best_fret = constraints.min_fret
        
        for string_idx, open_pitch in enumerate(string_tunings):
            fret = midi - open_pitch
            if constraints.contains(fret):
                best_string = 6 - string_idx
                best_fret = fret
                break
        
        return (best_string, best_fret)
    
    def get_description(self) -> str:
        constraints = self.config.get_position_constraints()
        pos_name = constraints.position_name if constraints else "5th position"
        
        return f"""
        Position-Locked Etude in {self.config.key} {self.config.scale}
        
        All notes in this etude stay within {pos_name} on the fretboard.
        This develops position awareness and efficient fingering.
        
        Practice tips:
        - Keep your hand in position - no shifting!
        - Notice which scale degrees fall on each string
        - Focus on finger independence within the position
        """


class StringSetEtude(EtudeTemplate):
    """
    String-Set Etude
    
    All voicings use a specific string set (6-4, 5-3, or 4-2).
    Develops comfort with specific string groupings.
    """
    
    name = "String-Set Etude"
    description = "All triads voiced on a specific string set"
    
    def generate(self) -> List[EtudePhrase]:
        """Generate string-set specific content."""
        material = self.harmonic_gen._generate_diatonic()
        phrases = self.pattern_stitcher.stitch(material)
        
        # Force all notes to target string set
        string_set = self.config._string_set_enum
        phrases = self._apply_string_set(phrases, string_set.value)
        
        return phrases
    
    def _apply_string_set(
        self, 
        phrases: List[EtudePhrase], 
        string_set: str
    ) -> List[EtudePhrase]:
        """Apply string set constraints to all notes."""
        # String sets: 6-4 means strings 6,5,4; 5-3 means 5,4,3; etc.
        set_map = {
            "6-4": [6, 5, 4],
            "5-3": [5, 4, 3],
            "4-2": [4, 3, 2],
            "auto": [6, 5, 4, 3, 2, 1],
        }
        
        allowed_strings = set_map.get(string_set, [6, 5, 4, 3, 2, 1])
        string_tunings = {
            6: 40, 5: 45, 4: 50, 3: 55, 2: 59, 1: 64
        }
        
        for phrase in phrases:
            for bar in phrase.bars:
                for event in bar.notes:
                    midi = event.note.midi_number
                    
                    # Find best string in allowed set
                    best_string = allowed_strings[0]
                    best_fret = 0
                    
                    for s in allowed_strings:
                        fret = midi - string_tunings[s]
                        if 0 <= fret <= 12:
                            best_string = s
                            best_fret = fret
                            break
                    
                    event.string = best_string
                    event.fret = best_fret
        
        return phrases
    
    def get_description(self) -> str:
        string_set = self.config.string_set
        
        return f"""
        String-Set Etude in {self.config.key} {self.config.scale}
        
        All voicings in this etude use the {string_set} string set.
        This develops facility with specific string groupings commonly
        used for chord voicings and arpeggios.
        
        Practice tips:
        - Focus on clean execution on the target strings
        - Notice the tonal quality of this string set
        - Experiment with different picking patterns
        """


class TwoFiveOneEtude(EtudeTemplate):
    """
    ii-V-I Etude
    
    Functional voice-leading with APVL + TRAM.
    The classic jazz progression in open triad voicings.
    """
    
    name = "ii-V-I Etude"
    description = "Functional ii-V-I progressions with optimal voice leading"
    
    def generate(self) -> List[EtudePhrase]:
        """Generate ii-V-I content."""
        material = self.harmonic_gen._generate_two_five_one()
        phrases = self.pattern_stitcher.stitch(material)
        phrases = self.pattern_stitcher.add_guitar_positions(phrases)
        return phrases
    
    def get_description(self) -> str:
        return f"""
        ii-V-I Etude in {self.config.key}
        
        This etude works through the fundamental ii-V-I progression using
        open triad voicings with optimal voice leading.
        
        The voice leading uses:
        - APVL (Axis-Preserving Voice Leading) for common tone retention
        - TRAM (Tension/Release Alternating Motion) for musical phrasing
        
        Practice tips:
        - Listen for the common tones between chords
        - Notice how the voice leading creates smooth motion
        - Feel the tension (ii-V) and resolution (I)
        """


class ChordMelodyMiniEtude(EtudeTemplate):
    """
    Chord-Melody Mini-Etude
    
    Melody note fixed on top with open triad harmonizations underneath.
    Introduces chord-melody concepts in a simple context.
    """
    
    name = "Chord-Melody Mini-Etude"
    description = "Melody on top with open triad support underneath"
    
    def generate(self) -> List[EtudePhrase]:
        """Generate chord-melody content."""
        material = self.harmonic_gen._generate_chord_melody()
        
        # For chord-melody, we need to ensure melody is on top
        for cell in material.cells:
            # Adjust voicing so highest note is the melody
            sorted_voices = sorted(cell.triad.voices, key=lambda n: n.midi_number)
            cell.triad.voices = sorted_voices  # Ensure proper ordering
        
        phrases = self.pattern_stitcher.stitch(material)
        phrases = self.pattern_stitcher.add_guitar_positions(phrases)
        
        return phrases
    
    def get_description(self) -> str:
        return f"""
        Chord-Melody Mini-Etude in {self.config.key} {self.config.scale}
        
        This etude introduces chord-melody technique using open triads.
        The melody (highest note) stays on top while the triad provides
        harmonic support underneath.
        
        Practice tips:
        - Bring out the top voice (melody) dynamically
        - Keep the lower voices balanced but softer
        - Think of playing two things: melody AND accompaniment
        """


# Template registry
TEMPLATE_REGISTRY: Dict[EtudeType, Type[EtudeTemplate]] = {
    EtudeType.SCALAR: ScalarOpenTriadEtude,
    EtudeType.INVERSION_CYCLE: InversionCycleEtude,
    EtudeType.INTERVALLIC: IntervallicEtude,
    EtudeType.POSITION: PositionLockedEtude,
    EtudeType.STRING_SET: StringSetEtude,
    EtudeType.TWO_FIVE_ONE: TwoFiveOneEtude,
    EtudeType.CHORD_MELODY: ChordMelodyMiniEtude,
    EtudeType.MELODIC: ScalarOpenTriadEtude,  # Default to scalar for melodic
    EtudeType.HARMONIC: TwoFiveOneEtude,      # Default to ii-V-I for harmonic
}


def get_template(config: EtudeConfig) -> EtudeTemplate:
    """
    Get the appropriate template for a configuration.
    
    Args:
        config: Etude configuration
        
    Returns:
        Instantiated EtudeTemplate
    """
    template_class = TEMPLATE_REGISTRY.get(
        config._etude_type_enum, 
        ScalarOpenTriadEtude
    )
    return template_class(config)


def list_templates() -> List[str]:
    """List all available template names."""
    return [t.name for t in TEMPLATE_REGISTRY.values()]

