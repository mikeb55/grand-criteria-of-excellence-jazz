"""
Main Etude Generator Module
============================

The main entry point for generating etudes.
Coordinates all sub-modules to produce complete, playable etudes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from .inputs import EtudeConfig, EtudeType, create_config, validate_config
from .harmonic import HarmonicGenerator, HarmonicMaterial
from .patterns import PatternStitcher, EtudePhrase
from .rhythm import RhythmGenerator, apply_rhythm
from .templates import get_template, EtudeTemplate, TEMPLATE_REGISTRY
from .output import EtudeOutput, EtudeExporter


@dataclass
class GeneratedEtude:
    """
    A complete generated etude with all data and export capabilities.
    
    Attributes:
        config: Configuration used
        phrases: Generated phrases
        harmonic_material: Harmonic content
        template: Template used
        metadata: Additional metadata
        warnings: Any warnings generated
    """
    config: EtudeConfig
    phrases: List[EtudePhrase]
    harmonic_material: HarmonicMaterial
    template: EtudeTemplate
    metadata: Dict = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self._exporter = EtudeExporter(self.config)
    
    @property
    def title(self) -> str:
        return self.config.title
    
    @property
    def description(self) -> str:
        return self.template.get_description()
    
    @property
    def total_bars(self) -> int:
        return sum(len(p.bars) for p in self.phrases)
    
    @property
    def total_notes(self) -> int:
        return sum(
            len(bar.notes) 
            for phrase in self.phrases 
            for bar in phrase.bars
        )
    
    def get_output(self) -> EtudeOutput:
        """Get the EtudeOutput object."""
        return EtudeOutput(
            config=self.config,
            phrases=self.phrases,
            metadata=self.metadata
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'config': self.config.to_dict(),
            'description': self.description,
            'statistics': {
                'total_bars': self.total_bars,
                'total_notes': self.total_notes,
                'total_phrases': len(self.phrases),
            },
            'harmonic_material': self.harmonic_material.to_dict(),
            'phrases': [p.to_dict() for p in self.phrases],
            'warnings': self.warnings,
        }
    
    # Export methods
    def export_json(self, filename: str) -> str:
        """Export to JSON format."""
        return self._exporter.export_json(self.get_output(), filename)
    
    def export_tab(self, filename: str) -> str:
        """Export to guitar TAB format."""
        return self._exporter.export_tab(self.phrases, filename)
    
    def export_musicxml(self, filename: str) -> str:
        """Export to MusicXML format."""
        return self._exporter.export_musicxml(self.phrases, filename)
    
    def export_pdf(self, filename: str) -> str:
        """Export to HTML/PDF format."""
        return self._exporter.export_pdf(self.phrases, filename, self.description)
    
    def export_all(self, base_filename: str) -> Dict[str, str]:
        """Export to all formats."""
        return self._exporter.export_all(
            self.get_output(), 
            base_filename, 
            self.description
        )
    
    def print_summary(self):
        """Print a summary of the generated etude."""
        print(f"\n{'='*60}")
        print(f"  {self.title}")
        print(f"{'='*60}")
        print(f"  Key: {self.config.key} {self.config.scale}")
        print(f"  Type: {self.config.etude_type}")
        print(f"  Difficulty: {self.config.difficulty}")
        print(f"  Tempo: {self.config.tempo} BPM")
        print(f"  Length: {self.total_bars} bars, {self.total_notes} notes")
        print(f"  Phrases: {len(self.phrases)}")
        
        if self.warnings:
            print(f"\n  Warnings:")
            for w in self.warnings:
                print(f"    - {w}")
        
        print(f"{'='*60}\n")


class EtudeGenerator:
    """
    Main etude generator class.
    
    Coordinates all modules to produce complete etudes:
    1. Validates configuration
    2. Generates harmonic material
    3. Stitches patterns
    4. Applies rhythm
    5. Adds guitar positions
    6. Prepares output
    """
    
    def __init__(self, config: EtudeConfig):
        """
        Initialize the generator.
        
        Args:
            config: Etude configuration
        """
        self.config = config
        self.warnings = validate_config(config)
        
        # Get the appropriate template
        self.template = get_template(config)
        
        # Initialize generators
        self.harmonic_gen = HarmonicGenerator(config)
        self.pattern_stitcher = PatternStitcher(config)
        self.rhythm_gen = RhythmGenerator(config)
    
    def generate(self) -> GeneratedEtude:
        """
        Generate a complete etude.
        
        Returns:
            GeneratedEtude with all content
        """
        # Step 1: Generate harmonic material
        harmonic_material = self.harmonic_gen.generate()
        
        # Step 2: Generate phrases using template
        phrases = self.template.generate()
        
        # Step 3: Apply rhythm
        phrases = self.rhythm_gen.apply_rhythm_to_phrases(phrases)
        
        # Step 4: Ensure guitar positions are set
        phrases = self.pattern_stitcher.add_guitar_positions(phrases)
        
        # Step 5: Build metadata
        metadata = {
            'template': self.template.name,
            'engine_version': '1.0.0',
            'generator': 'Etude Generator',
        }
        
        return GeneratedEtude(
            config=self.config,
            phrases=phrases,
            harmonic_material=harmonic_material,
            template=self.template,
            metadata=metadata,
            warnings=self.warnings
        )
    
    @classmethod
    def quick_generate(
        cls,
        key: str = 'C',
        scale: str = 'ionian',
        etude_type: str = 'melodic',
        difficulty: str = 'intermediate',
        length: int = 8
    ) -> GeneratedEtude:
        """
        Quick generate an etude with minimal configuration.
        
        Args:
            key: Key center
            scale: Scale name
            etude_type: Type of etude
            difficulty: Difficulty level
            length: Number of bars
            
        Returns:
            GeneratedEtude
        """
        config = create_config(
            key=key,
            scale=scale,
            etude_type=etude_type,
            difficulty=difficulty,
            length=length
        )
        generator = cls(config)
        return generator.generate()


def generate_etude(**kwargs) -> GeneratedEtude:
    """
    Convenience function to generate an etude.
    
    Args:
        **kwargs: Configuration options
        
    Returns:
        GeneratedEtude
    """
    config = create_config(**kwargs)
    generator = EtudeGenerator(config)
    return generator.generate()


def quick_etude(
    key: str = 'C',
    etude_type: str = 'melodic',
    difficulty: str = 'intermediate'
) -> GeneratedEtude:
    """
    Generate an etude with minimal configuration.
    
    Args:
        key: Key center
        etude_type: Type of etude
        difficulty: Difficulty level
        
    Returns:
        GeneratedEtude
    """
    return EtudeGenerator.quick_generate(
        key=key,
        etude_type=etude_type,
        difficulty=difficulty
    )


def list_etude_types() -> List[str]:
    """List all available etude types."""
    return [et.value for et in EtudeType]


def list_templates() -> Dict[str, str]:
    """List all templates with descriptions."""
    result = {}
    for et, template_class in TEMPLATE_REGISTRY.items():
        result[et.value] = template_class.description
    return result

