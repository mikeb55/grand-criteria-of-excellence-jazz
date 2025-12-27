"""
Quartal 3-Chorus Solo Generator
==============================

This module generates 3-chorus solos using quartal harmony, integrating
with the Quartal Engine to create performance-ready material.

The 3-chorus structure follows jazz conventions:
- Chorus 1: Establish (space, motif, inside) - Half notes, 3-note quartals
- Chorus 2: Develop or Disrupt (controlled intensity) - Quarter notes, 3-note quartals
- Chorus 3: Peak and Resolve (earned intensity) - Eighth notes, 3-note quartals
"""

from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from quartal_engine_wrapper import QuartalEngine, QuartalParams


@dataclass
class ChorusConfig:
    """Configuration for a single chorus."""
    duration: str  # "half", "quarter", "eighth", "sixteenth"
    stack_type: str  # "3-note" or "4-note"
    tempo: Optional[int] = None
    description: str = ""


class Quartal3ChorusGenerator:
    """
    Generator for 3-chorus quartal solos.
    
    Usage:
        generator = Quartal3ChorusGenerator()
        results = generator.generate_solo(
            root="D",
            scale="dorian",
            bars_per_chorus=8,
            style="standard"  # or "intense", "lyrical"
        )
    """
    
    # Predefined chorus configurations
    CHORUS_STYLES = {
        "standard": [
            ChorusConfig("half", "3-note", description="Establishment - slow, sustained"),
            ChorusConfig("quarter", "3-note", description="Development - medium tempo"),
            ChorusConfig("eighth", "3-note", description="Climax - fast, intense")
        ],
        "intense": [
            ChorusConfig("quarter", "3-note", description="Quick establishment"),
            ChorusConfig("eighth", "3-note", description="Rapid development"),
            ChorusConfig("sixteenth", "3-note", description="Maximum intensity")
        ],
        "lyrical": [
            ChorusConfig("half", "3-note", description="Very slow, spacious"),
            ChorusConfig("half", "4-note", description="Rich harmony, still slow"),
            ChorusConfig("quarter", "3-note", description="Gentle build")
        ],
        "progressive": [
            ChorusConfig("half", "3-note", description="Start simple"),
            ChorusConfig("quarter", "4-note", description="Add richness"),
            ChorusConfig("eighth", "3-note", description="Build intensity")
        ]
    }
    
    def __init__(self, engine_path: Optional[str] = None):
        """
        Initialize the generator.
        
        Args:
            engine_path: Optional path to quartal-engine directory
        """
        self.engine = QuartalEngine(engine_path)
    
    def generate_solo(
        self,
        root: str,
        scale: str,
        bars_per_chorus: int,
        style: str = "standard",
        tempo: Optional[int] = None,
        output_dir: Optional[str] = None,
        custom_config: Optional[List[ChorusConfig]] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Generate a complete 3-chorus quartal solo.
        
        Args:
            root: Root note (e.g., "C", "D", "F#")
            scale: Scale/mode (e.g., "major", "dorian", "lydian")
            bars_per_chorus: Number of bars per chorus
            style: Predefined style ("standard", "intense", "lyrical", "progressive")
            tempo: Optional BPM (applied to all choruses)
            output_dir: Optional output directory
            custom_config: Optional custom chorus configurations
            
        Returns:
            Dictionary with structure:
            {
                'chorus1': {'file': path, 'config': ChorusConfig},
                'chorus2': {'file': path, 'config': ChorusConfig},
                'chorus3': {'file': path, 'config': ChorusConfig}
            }
        """
        # Get chorus configurations
        if custom_config:
            configs = custom_config
        elif style in self.CHORUS_STYLES:
            configs = self.CHORUS_STYLES[style]
        else:
            # Default to standard
            configs = self.CHORUS_STYLES["standard"]
        
        if len(configs) != 3:
            raise ValueError("Must provide exactly 3 chorus configurations")
        
        results = {}
        
        for i, config in enumerate(configs, 1):
            chorus_key = f"chorus{i}"
            
            # Generate this chorus
            file_path = self.engine.generate(
                root=root,
                scale=scale,
                bars=bars_per_chorus,
                stack_type=config.stack_type,
                duration=config.duration,
                tempo=tempo or config.tempo,
                output_path=output_dir
            )
            
            results[chorus_key] = {
                'file': file_path,
                'config': config,
                'description': config.description
            }
        
        return results
    
    def generate_multiscale_solo(
        self,
        segments: List[Tuple[str, str, int]],  # (root, scale, bars)
        style: str = "standard",
        tempo: Optional[int] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Generate a 3-chorus solo with different scales/modes per chorus.
        
        Args:
            segments: List of (root, scale, bars) tuples, one per chorus
            style: Predefined style
            tempo: Optional BPM
            output_dir: Optional output directory
            
        Returns:
            Dictionary with chorus results
        """
        if len(segments) != 3:
            raise ValueError("Must provide exactly 3 segments (one per chorus)")
        
        # Get configurations
        if style in self.CHORUS_STYLES:
            configs = self.CHORUS_STYLES[style]
        else:
            configs = self.CHORUS_STYLES["standard"]
        
        results = {}
        
        for i, ((root, scale, bars), config) in enumerate(zip(segments, configs), 1):
            chorus_key = f"chorus{i}"
            
            file_path = self.engine.generate(
                root=root,
                scale=scale,
                bars=bars,
                stack_type=config.stack_type,
                duration=config.duration,
                tempo=tempo or config.tempo,
                output_path=output_dir
            )
            
            results[chorus_key] = {
                'file': file_path,
                'config': config,
                'description': f"{root} {scale} - {config.description}",
                'root': root,
                'scale': scale
            }
        
        return results
    
    def generate_for_tune(
        self,
        tune_name: str,
        root: str,
        scale: str,
        form_bars: int,  # Total bars in the tune (e.g., 16, 32)
        style: str = "standard",
        tempo: Optional[int] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate a 3-chorus quartal solo for a specific tune.
        
        Args:
            tune_name: Name of the tune
            root: Root note
            scale: Scale/mode
            form_bars: Total bars in the tune form
            style: Predefined style
            tempo: Optional BPM
            output_dir: Optional output directory
            
        Returns:
            Complete solo information dictionary
        """
        results = self.generate_solo(
            root=root,
            scale=scale,
            bars_per_chorus=form_bars,
            style=style,
            tempo=tempo,
            output_dir=output_dir
        )
        
        return {
            'tune_name': tune_name,
            'root': root,
            'scale': scale,
            'form_bars': form_bars,
            'style': style,
            'choruses': results,
            'total_bars': form_bars * 3
        }


# Convenience functions
def generate_standard_3chorus(
    root: str,
    scale: str,
    bars_per_chorus: int = 8
) -> Dict[str, Dict[str, str]]:
    """Generate a standard 3-chorus quartal solo."""
    generator = Quartal3ChorusGenerator()
    return generator.generate_solo(root, scale, bars_per_chorus, style="standard")


def generate_intense_3chorus(
    root: str,
    scale: str,
    bars_per_chorus: int = 8
) -> Dict[str, Dict[str, str]]:
    """Generate an intense 3-chorus quartal solo."""
    generator = Quartal3ChorusGenerator()
    return generator.generate_solo(root, scale, bars_per_chorus, style="intense")


if __name__ == "__main__":
    # Test the generator
    print("Testing Quartal 3-Chorus Generator...")
    
    generator = Quartal3ChorusGenerator()
    
    # Test standard generation
    print("\n1. Generating standard 3-chorus solo (D dorian, 8 bars each)...")
    results = generator.generate_solo("D", "dorian", 8, style="standard")
    
    for chorus, data in results.items():
        print(f"   {chorus.upper()}: {data['description']}")
        print(f"      File: {data['file']}")
    
    # Test multiscale generation
    print("\n2. Generating multiscale 3-chorus solo...")
    multiscale_results = generator.generate_multiscale_solo(
        segments=[
            ("D", "dorian", 8),
            ("D", "minor", 8),
            ("D", "dorian", 8)
        ],
        style="progressive"
    )
    
    for chorus, data in multiscale_results.items():
        print(f"   {chorus.upper()}: {data['root']} {data['scale']} - {data['description']}")
        print(f"      File: {data['file']}")
    
    print("\n✓ Quartal 3-Chorus Generator is working!")




