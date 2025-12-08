"""
Etude Generator Demo - 4 Example Etudes
========================================

Generates demonstration etudes showcasing the Etude Generator capabilities:
1. Modal open-triad melodic etude
2. Intervallic triad-pair open-triad line
3. ii-V-I functional etude
4. Chord-melody open-triad miniature
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from generator import generate_etude, quick_etude
from inputs import EtudeConfig


def demo_modal_melodic_etude():
    """
    Demo 1: Modal Open-Triad Melodic Etude
    
    D Dorian scale with melodic patterns for developing
    modal vocabulary using open triad voicings.
    """
    print("\n" + "=" * 60)
    print("  DEMO 1: Modal Open-Triad Melodic Etude")
    print("=" * 60)
    
    etude = generate_etude(
        key='D',
        scale='dorian',
        etude_type='melodic',
        difficulty='intermediate',
        mode='modal',
        rhythmic_style='straight',
        tempo=100,
        length=8,
        title='D Dorian Modal Melodic Etude'
    )
    
    etude.print_summary()
    
    # Export
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    results = etude.export_all(str(output_dir / 'demo_1_modal_melodic'))
    
    print("  Exported files:")
    for fmt, path in results.items():
        print(f"    {fmt}: {path}")
    
    return etude


def demo_intervallic_triad_pair_etude():
    """
    Demo 2: Intervallic Triad-Pair Etude
    
    G Lydian with wide intervals and triad pairs
    for developing modern, angular vocabulary.
    """
    print("\n" + "=" * 60)
    print("  DEMO 2: Intervallic Triad-Pair Etude")
    print("=" * 60)
    
    etude = generate_etude(
        key='G',
        scale='lydian',
        etude_type='intervallic',
        difficulty='advanced',
        mode='intervallic',
        rhythmic_style='syncopated',
        tempo=120,
        length=8,
        title='G Lydian Intervallic Triad-Pair Etude'
    )
    
    etude.print_summary()
    
    # Export
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    results = etude.export_all(str(output_dir / 'demo_2_intervallic'))
    
    print("  Exported files:")
    for fmt, path in results.items():
        print(f"    {fmt}: {path}")
    
    return etude


def demo_two_five_one_etude():
    """
    Demo 3: ii-V-I Functional Etude
    
    Classic jazz progression in Bb with functional
    voice leading using APVL and TRAM.
    """
    print("\n" + "=" * 60)
    print("  DEMO 3: ii-V-I Functional Etude")
    print("=" * 60)
    
    etude = generate_etude(
        key='Bb',
        scale='ionian',
        etude_type='ii_v_i',
        difficulty='intermediate',
        mode='functional',
        rhythmic_style='swing',
        tempo=120,
        length=12,
        title='Bb ii-V-I Functional Voice-Leading Etude'
    )
    
    etude.print_summary()
    
    # Export
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    results = etude.export_all(str(output_dir / 'demo_3_two_five_one'))
    
    print("  Exported files:")
    for fmt, path in results.items():
        print(f"    {fmt}: {path}")
    
    return etude


def demo_chord_melody_miniature():
    """
    Demo 4: Chord-Melody Open-Triad Miniature
    
    C major chord-melody piece with melody on top
    and open triad harmonization underneath.
    """
    print("\n" + "=" * 60)
    print("  DEMO 4: Chord-Melody Open-Triad Miniature")
    print("=" * 60)
    
    etude = generate_etude(
        key='C',
        scale='ionian',
        etude_type='chord_melody',
        difficulty='advanced',
        mode='functional',
        rhythmic_style='straight',
        tempo=80,
        length=8,
        string_set='4-2',  # Higher strings for chord-melody
        title='C Major Chord-Melody Miniature'
    )
    
    etude.print_summary()
    
    # Export
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    results = etude.export_all(str(output_dir / 'demo_4_chord_melody'))
    
    print("  Exported files:")
    for fmt, path in results.items():
        print(f"    {fmt}: {path}")
    
    return etude


def run_all_demos():
    """Run all demonstration etudes."""
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + "  ETUDE GENERATOR - DEMONSTRATION SUITE  ".center(68) + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    
    etudes = []
    
    # Generate all demos
    etudes.append(demo_modal_melodic_etude())
    etudes.append(demo_intervallic_triad_pair_etude())
    etudes.append(demo_two_five_one_etude())
    etudes.append(demo_chord_melody_miniature())
    
    # Summary
    print("\n" + "=" * 70)
    print("  DEMO SUMMARY")
    print("=" * 70)
    
    total_bars = sum(e.total_bars for e in etudes)
    total_notes = sum(e.total_notes for e in etudes)
    
    print(f"\n  Generated 4 demonstration etudes:")
    for i, e in enumerate(etudes, 1):
        print(f"    {i}. {e.title}")
        print(f"       {e.total_bars} bars, {e.total_notes} notes")
    
    print(f"\n  Total: {total_bars} bars, {total_notes} notes")
    
    output_dir = Path(__file__).parent / 'output'
    print(f"\n  All files exported to: {output_dir}")
    
    print("\n  Available formats:")
    print("    - JSON: Complete etude data")
    print("    - TAB: ASCII guitar tablature")
    print("    - MusicXML: Notation interchange (open in MuseScore, Finale, etc.)")
    print("    - HTML: Print-ready etude sheet (print to PDF)")
    
    print("\n" + "=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70 + "\n")
    
    return etudes


if __name__ == '__main__':
    run_all_demos()

