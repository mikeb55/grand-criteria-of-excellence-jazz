"""
Quartal Engine Python Wrapper
==============================

This module provides a Python interface to the Node.js Quartal Engine
located at: C:\\Users\\mike\\Documents\\Cursor AI Projects\\gml-workspace\\quartal-engine

The Quartal Engine generates quartal harmony (chords built in 4ths) for guitar
and outputs MusicXML files that can be integrated into 3-chorus solos.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class QuartalParams:
    """Parameters for quartal generation."""
    root: str  # e.g., "C", "D", "F#"
    scale: str  # e.g., "major", "dorian", "lydian", "minor"
    bars: int
    stack_type: str = "3-note"  # "3-note" or "4-note"
    duration: str = "quarter"  # "half", "quarter", "eighth", "sixteenth"
    tempo: Optional[int] = None  # BPM (default: 108)
    string_set: Optional[List[int]] = None  # e.g., [3, 2, 1] for strings 3-2-1


@dataclass
class MultiScaleSegment:
    """A segment in a multi-scale progression."""
    root: str
    scale: str
    start_bar: int
    end_bar: int


@dataclass
class MultiScaleParams:
    """Parameters for multi-scale quartal generation."""
    segments: List[MultiScaleSegment]
    stack_type: str = "3-note"
    duration: str = "quarter"
    tempo: Optional[int] = None


class QuartalEngine:
    """
    Python wrapper for the Node.js Quartal Engine.
    
    Usage:
        engine = QuartalEngine()
        xml_path = engine.generate(
            root="D",
            scale="dorian",
            bars=8,
            duration="quarter"
        )
    """
    
    def __init__(self, engine_path: Optional[str] = None):
        """
        Initialize the Quartal Engine wrapper.
        
        Args:
            engine_path: Path to quartal-engine directory. If None, uses default location.
        """
        if engine_path is None:
            # Default path to cloned repository
            base_path = Path(r"C:\Users\mike\Documents\Cursor AI Projects\gml-workspace\quartal-engine")
        else:
            base_path = Path(engine_path)
        
        self.engine_path = base_path
        self.cli_path = base_path / "quartal-cli.js"
        self.output_dir = base_path / "output" / "generated"
        
        # Verify engine exists
        if not self.cli_path.exists():
            raise FileNotFoundError(
                f"Quartal Engine not found at {self.cli_path}. "
                f"Please ensure the repository is cloned."
            )
    
    def _build_command(self, params: QuartalParams) -> str:
        """
        Build a natural language command for the quartal engine.
        
        Args:
            params: Quartal generation parameters
            
        Returns:
            Command string
        """
        # Build duration string
        duration_map = {
            "half": "half notes",
            "quarter": "quarter notes",
            "eighth": "eighth notes",
            "sixteenth": "sixteenth notes"
        }
        duration_str = duration_map.get(params.duration, "quarter notes")
        
        # Build stack type string
        if params.stack_type == "4-note":
            stack_str = "4-note quartals"
        else:
            stack_str = "quartals"
        
        # Build command
        if params.bars == 7:
            # Full scale harmonization
            command = f"Generate a musicxml of the {params.root} {params.scale} scale harmonised as {stack_str}"
        else:
            command = f"Generate {params.root} {params.scale} {stack_str}, {params.bars} bars, {duration_str}"
        
        # Add tempo if specified
        if params.tempo:
            command += f", {params.tempo} bpm"
        
        return command
    
    def _build_multiscale_command(self, params: MultiScaleParams) -> str:
        """
        Build a multi-scale command.
        
        Args:
            params: Multi-scale parameters
            
        Returns:
            Command string
        """
        duration_map = {
            "half": "half notes",
            "quarter": "quarter notes",
            "eighth": "eighth notes",
            "sixteenth": "sixteenth notes"
        }
        duration_str = duration_map.get(params.duration, "quarter notes")
        
        stack_str = "4-note quartals" if params.stack_type == "4-note" else "quartals"
        
        # Build segments
        segments = []
        for seg in params.segments:
            segments.append(f"{seg.root} {seg.scale} bars {seg.start_bar}-{seg.end_bar}")
        
        command = f"Generate {', '.join(segments)}, {stack_str}, {duration_str}"
        
        if params.tempo:
            command += f", {params.tempo} bpm"
        
        return command
    
    def generate(
        self,
        root: str,
        scale: str,
        bars: int,
        stack_type: str = "3-note",
        duration: str = "quarter",
        tempo: Optional[int] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate quartal harmony and return path to MusicXML file.
        
        Args:
            root: Root note (e.g., "C", "D", "F#")
            scale: Scale/mode (e.g., "major", "dorian", "lydian")
            bars: Number of bars
            stack_type: "3-note" or "4-note"
            duration: "half", "quarter", "eighth", "sixteenth"
            tempo: Optional BPM
            output_path: Optional custom output path (if None, uses engine's output dir)
            
        Returns:
            Path to generated MusicXML file
        """
        params = QuartalParams(
            root=root,
            scale=scale,
            bars=bars,
            stack_type=stack_type,
            duration=duration,
            tempo=tempo
        )
        
        command = self._build_command(params)
        return self._execute_command(command, output_path)
    
    def generate_multiscale(
        self,
        segments: List[Tuple[str, str, int, int]],  # (root, scale, start_bar, end_bar)
        stack_type: str = "3-note",
        duration: str = "quarter",
        tempo: Optional[int] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate multi-scale quartal progression.
        
        Args:
            segments: List of (root, scale, start_bar, end_bar) tuples
            stack_type: "3-note" or "4-note"
            duration: Note duration
            tempo: Optional BPM
            output_path: Optional custom output path
            
        Returns:
            Path to generated MusicXML file
        """
        multiseg = MultiScaleParams(
            segments=[
                MultiScaleSegment(root=r, scale=s, start_bar=start, end_bar=end)
                for r, s, start, end in segments
            ],
            stack_type=stack_type,
            duration=duration,
            tempo=tempo
        )
        
        command = self._build_multiscale_command(multiseg)
        return self._execute_command(command, output_path)
    
    def parse_semicolon_commands(self, command_string: str) -> List[Tuple[str, str, int, int]]:
        """
        Parse semicolon-separated commands into segments with bar ranges.
        
        Example input:
            "Generate G mixolydian quartals, 6 bars, half notes; Generate G# locrian quartals, 1 bars, half notes"
        
        Returns:
            List of (root, scale, start_bar, end_bar) tuples
        """
        import re
        
        # Split by semicolon
        commands = [c.strip() for c in command_string.split(';') if c.strip()]
        
        segments = []
        current_bar = 1
        
        for cmd in commands:
            # Extract root and scale: "G mixolydian" or "G# locrian"
            key_match = re.search(r'Generate\s+([A-G][#b]?)\s+(\w+)', cmd, re.IGNORECASE)
            if not key_match:
                continue
            
            root = key_match.group(1)
            scale = key_match.group(2).lower()
            
            # Extract bar count: "6 bars" or "1 bars"
            bar_match = re.search(r'(\d+)\s+bar', cmd, re.IGNORECASE)
            if not bar_match:
                continue
            
            bar_count = int(bar_match.group(1))
            start_bar = current_bar
            end_bar = current_bar + bar_count - 1
            
            segments.append((root, scale, start_bar, end_bar))
            current_bar = end_bar + 1
        
        return segments
    
    def generate_from_semicolon_commands(
        self,
        command_string: str,
        stack_type: str = "3-note",
        duration: str = "quarter",
        tempo: Optional[int] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate quartals from semicolon-separated commands.
        
        This method parses commands like:
            "Generate G mixolydian quartals, 6 bars, half notes; Generate G# locrian quartals, 1 bars, half notes"
        
        And converts them to the proper multi-scale format with explicit bar ranges.
        
        Args:
            command_string: Semicolon-separated command string
            stack_type: "3-note" or "4-note"
            duration: Note duration (extracted from command if present, otherwise uses this param)
            tempo: Optional BPM
            output_path: Optional custom output path
            
        Returns:
            Path to generated MusicXML file
        """
        # Extract duration from command if present
        import re
        duration_match = re.search(r'(half|quarter|eighth|sixteenth)\s+notes?', command_string, re.IGNORECASE)
        if duration_match:
            duration = duration_match.group(1).lower()
        
        # Parse segments
        segments = self.parse_semicolon_commands(command_string)
        
        if not segments:
            raise ValueError(f"Could not parse any segments from command: {command_string}")
        
        # Generate using multiscale method
        return self.generate_multiscale(segments, stack_type, duration, tempo, output_path)
    
    def _execute_command(self, command: str, output_path: Optional[str] = None) -> str:
        """
        Execute a quartal engine command and return the output file path.
        
        Args:
            command: Natural language command string
            output_path: Optional custom output path
            
        Returns:
            Path to generated MusicXML file
        """
        # Change to engine directory
        original_dir = os.getcwd()
        try:
            os.chdir(self.engine_path)
            
            # Run the command via Node.js
            process = subprocess.Popen(
                ["node", "quartal-cli.js"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            stdout, stderr = process.communicate(input=command + "\nexit\n", timeout=30)
            
            if process.returncode != 0:
                raise RuntimeError(f"Quartal Engine error: {stderr or 'Unknown error'}")
            
            # Parse output to find generated file
            # The engine outputs the file path
            if stdout is None:
                stdout = ""
            lines = stdout.split('\n')
            generated_file = None
            
            for line in lines:
                if '.musicxml' in line.lower() or 'generated' in line.lower():
                    # Try to extract file path
                    if 'output' in line or 'generated' in line:
                        # Look for file path pattern
                        parts = line.split()
                        for part in parts:
                            if '.musicxml' in part.lower():
                                generated_file = part.strip()
                                break
            
            # If we couldn't parse it, look for the most recent file in output directory
            if generated_file is None or not os.path.exists(generated_file):
                if self.output_dir.exists():
                    musicxml_files = list(self.output_dir.glob("*.musicxml"))
                    if musicxml_files:
                        # Get most recent
                        generated_file = max(musicxml_files, key=os.path.getctime)
                        generated_file = str(generated_file)
            
            if generated_file is None or not os.path.exists(generated_file):
                raise FileNotFoundError(
                    f"Could not find generated MusicXML file. "
                    f"Command: {command}\nOutput: {stdout}\nError: {stderr}"
                )
            
            # If custom output path specified, copy file
            if output_path:
                import shutil
                shutil.copy2(generated_file, output_path)
                return output_path
            
            return generated_file
            
        finally:
            os.chdir(original_dir)
    
    def generate_3_chorus_quartal(
        self,
        root: str,
        scale: str,
        bars_per_chorus: int,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate quartal material for a 3-chorus solo.
        
        Chorus 1: Half notes (establishment)
        Chorus 2: Quarter notes (development)
        Chorus 3: Eighth notes (climax)
        
        Args:
            root: Root note
            scale: Scale/mode
            bars_per_chorus: Number of bars per chorus
            output_dir: Optional output directory (default: uses engine output dir)
            
        Returns:
            Dictionary with keys 'chorus1', 'chorus2', 'chorus3' mapping to file paths
        """
        results = {}
        
        # Chorus 1: Establishment (half notes, 3-note quartals)
        results['chorus1'] = self.generate(
            root=root,
            scale=scale,
            bars=bars_per_chorus,
            stack_type="3-note",
            duration="half",
            output_path=output_dir
        )
        
        # Chorus 2: Development (quarter notes, 3-note quartals)
        results['chorus2'] = self.generate(
            root=root,
            scale=scale,
            bars=bars_per_chorus,
            stack_type="3-note",
            duration="quarter",
            output_path=output_dir
        )
        
        # Chorus 3: Climax (eighth notes, 3-note quartals)
        results['chorus3'] = self.generate(
            root=root,
            scale=scale,
            bars=bars_per_chorus,
            stack_type="3-note",
            duration="eighth",
            output_path=output_dir
        )
        
        return results


# Convenience function for quick generation
def generate_quartal(
    root: str,
    scale: str,
    bars: int,
    stack_type: str = "3-note",
    duration: str = "quarter"
) -> str:
    """
    Quick function to generate quartal harmony.
    
    Args:
        root: Root note
        scale: Scale/mode
        bars: Number of bars
        stack_type: "3-note" or "4-note"
        duration: "half", "quarter", "eighth", "sixteenth"
        
    Returns:
        Path to generated MusicXML file
    """
    engine = QuartalEngine()
    return engine.generate(root, scale, bars, stack_type, duration)


if __name__ == "__main__":
    # Test the wrapper
    print("Testing Quartal Engine Wrapper...")
    
    engine = QuartalEngine()
    
    # Test single generation
    print("\n1. Generating D dorian quartals, 4 bars, quarter notes...")
    result = engine.generate("D", "dorian", 4, "3-note", "quarter")
    print(f"   Generated: {result}")
    
    # Test 3-chorus generation
    print("\n2. Generating 3-chorus quartal solo (D dorian, 8 bars each)...")
    chorus_results = engine.generate_3_chorus_quartal("D", "dorian", 8)
    print(f"   Chorus 1: {chorus_results['chorus1']}")
    print(f"   Chorus 2: {chorus_results['chorus2']}")
    print(f"   Chorus 3: {chorus_results['chorus3']}")
    
    print("\n✓ Quartal Engine wrapper is working!")


