"""
Open Triad Engine v1.0 - Complete Demo
======================================

Demonstrates all engine modes and features with example outputs.
"""

import sys
from pathlib import Path
import json

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from open_triad_engine import (
    OpenTriadEngine, create_engine, EngineConfig,
    Note, Triad, TriadType, Inversion
)


def demo_melodic_mode():
    """Demo: Melodic Mode - Open triads for melodic lines."""
    print("\n" + "=" * 60)
    print("MELODIC MODE DEMO")
    print("=" * 60)
    
    engine = create_engine(
        mode='melodic',
        priority='smooth',
        triad_type='major'
    )
    
    # Generate open triads across C major scale
    result = engine.generate_scale_triads('C', 'ionian')
    
    print("\nC Major Scale - Open Triads:")
    for i, triad in enumerate(result.data):
        voices = ', '.join(str(v) for v in sorted(triad.voices, key=lambda n: n.midi_number))
        print(f"  Degree {i+1}: {triad.symbol:6} -> [{voices}]")
    
    # Generate melodic patterns
    print("\nMelodic Patterns from C Major triad:")
    patterns = engine.generate_patterns(result.data[0])[:5]
    for pattern in patterns:
        notes = ' -> '.join(str(n) for n in pattern.notes)
        print(f"  {pattern.pattern_type:20}: {notes}")


def demo_harmonic_mode():
    """Demo: Harmonic Mode - Voice-led progressions."""
    print("\n" + "=" * 60)
    print("HARMONIC MODE DEMO")
    print("=" * 60)
    
    engine = create_engine(mode='harmonic', priority='smooth')
    
    # Voice lead a ii-V-I progression
    print("\nVoice-Led ii-V-I in C Major:")
    result = engine.voice_lead_progression(['Dm', 'G', 'C'])
    
    for i, triad in enumerate(result.data['triads']):
        voices = ', '.join(str(v) for v in sorted(triad.voices, key=lambda n: n.midi_number))
        print(f"  {triad.symbol:6} -> [{voices}]")
    
    print("\nVoice Leading Analysis:")
    for vl in result.data['voice_leading']:
        print(f"  {vl.source.symbol} -> {vl.target.symbol}: {vl.narrative[:60]}...")
    
    # Generate ii-V-I with special engine
    print("\nii-V-I in all 12 keys (first 4):")
    keys = ['C', 'F', 'Bb', 'Eb']
    for key in keys:
        result_251 = engine.generate_two_five_one(key)
        print(f"  {key}: {result_251.ii.symbol} -> {result_251.V.symbol} -> {result_251.I.symbol}")


def demo_chord_melody_mode():
    """Demo: Chord-Melody Mode - Melody with triad support."""
    print("\n" + "=" * 60)
    print("CHORD-MELODY MODE DEMO")
    print("=" * 60)
    
    engine = create_engine(mode='chord_melody')
    
    # Create a simple melody
    melody = [
        Note('E', 5), Note('D', 5), Note('C', 5), Note('D', 5),
        Note('E', 5), Note('E', 5), Note('E', 5)
    ]
    
    print("\nMelody: Mary Had a Little Lamb (first phrase)")
    melody_str = ' -> '.join(str(n) for n in melody)
    print(f"  {melody_str}")
    
    # Harmonize with open triads
    print("\nChord-Melody Voicings (melody on top):")
    voicings = engine.create_chord_melody(melody)
    
    for i, voicing in enumerate(voicings):
        voices = ', '.join(str(v) for v in voicing.full_voicing)
        print(f"  Note {i+1}: [{voices}] (melody: {voicing.melody_note})")


def demo_counterpoint_mode():
    """Demo: Counterpoint Mode - Three independent lines."""
    print("\n" + "=" * 60)
    print("COUNTERPOINT MODE DEMO")
    print("=" * 60)
    
    engine = create_engine(mode='counterpoint')
    
    # Create a chord progression
    progression = ['C', 'Am', 'F', 'G', 'C']
    result = engine.parse_progression(progression)
    
    print(f"\nProgression: {' -> '.join(progression)}")
    
    # Generate counterpoint
    cp_result = engine.generate_counterpoint(result.data)
    
    print("\nThree-Voice Counterpoint:")
    print("  Soprano:", ' -> '.join(str(n) for n in cp_result.soprano.notes))
    print("  Alto:   ", ' -> '.join(str(n) for n in cp_result.alto.notes))
    print("  Bass:   ", ' -> '.join(str(n) for n in cp_result.bass.notes))


def demo_orchestration_mode():
    """Demo: Orchestration Mode - Instrument assignments."""
    print("\n" + "=" * 60)
    print("ORCHESTRATION MODE DEMO")
    print("=" * 60)
    
    engine = create_engine(
        mode='orchestration',
        instruments={
            'top': 'violin',
            'middle': 'viola',
            'bottom': 'cello'
        }
    )
    
    # Generate triads
    result = engine.generate_scale_triads('G', 'ionian')
    
    print("\nG Major Scale - Orchestrated for String Trio:")
    orchestrations = engine.orchestrate(result.data)
    
    for i, orch in enumerate(orchestrations[:4]):  # First 4
        print(f"\n  Chord {i+1}: {orch.triad.symbol}")
        for pos, inst in orch.assignments.items():
            info = orch.register_info[pos]
            status = "✓" if info['in_preferred'] else "⚠"
            print(f"    {pos:8} -> {inst:8} ({info['note']}) {status}")


def demo_two_five_one():
    """Demo: ii-V-I Engine with APVL and TRAM."""
    print("\n" + "=" * 60)
    print("ii-V-I ENGINE DEMO")
    print("=" * 60)
    
    engine = create_engine()
    
    print("\nii-V-I Progressions with Optimal Voice Leading:")
    
    for key in ['C', 'G', 'D', 'A']:
        result = engine.generate_two_five_one(key)
        
        ii_voices = ', '.join(str(v) for v in sorted(result.ii.voices, key=lambda n: n.midi_number))
        V_voices = ', '.join(str(v) for v in sorted(result.V.voices, key=lambda n: n.midi_number))
        I_voices = ', '.join(str(v) for v in sorted(result.I.voices, key=lambda n: n.midi_number))
        
        print(f"\n  Key of {key}:")
        print(f"    ii:  {result.ii.symbol:4} [{ii_voices}]")
        print(f"    V:   {result.V.symbol:4} [{V_voices}]")
        print(f"    I:   {result.I.symbol:4} [{I_voices}]")


def demo_triad_pairs():
    """Demo: Open Triad Pair Engine."""
    print("\n" + "=" * 60)
    print("TRIAD PAIR ENGINE DEMO")
    print("=" * 60)
    
    engine = create_engine()
    
    print("\nKlemons-Style Triad Pairs (whole step apart):")
    for root in ['C', 'G', 'D']:
        pair = engine.create_triad_pair(root, 'klemons')
        
        t1_notes = ', '.join(str(v) for v in sorted(pair.triad1.voices, key=lambda n: n.midi_number))
        t2_notes = ', '.join(str(v) for v in sorted(pair.triad2.voices, key=lambda n: n.midi_number))
        
        print(f"\n  Root: {root}")
        print(f"    Triad 1: {pair.triad1.symbol} [{t1_notes}]")
        print(f"    Triad 2: {pair.triad2.symbol} [{t2_notes}]")
        print(f"    Combined pitch classes: {pair.combined_pitch_classes}")


def demo_shape_bundles():
    """Demo: Shape Bundles for practice."""
    print("\n" + "=" * 60)
    print("SHAPE BUNDLES DEMO")
    print("=" * 60)
    
    engine = create_engine()
    
    # Generate triads and bundles
    result = engine.generate_scale_triads('C', 'ionian')
    bundles = engine.get_shape_bundles(result.data)
    
    print("\nC Major - All Open Triad Shapes:")
    for bundle in bundles[:3]:  # First 3 chords
        print(f"\n  {bundle.root_triad.symbol}:")
        
        shapes = bundle.get_all_shapes()
        for name, shape in shapes.items():
            voices = ', '.join(str(v) for v in sorted(shape.voices, key=lambda n: n.midi_number))
            print(f"    {name:12}: [{voices}]")
        
        print(f"    Contour: {bundle.root_contour.type.value}")


def demo_modal_sequence():
    """Demo: Modal sequence example."""
    print("\n" + "=" * 60)
    print("MODAL SEQUENCE DEMO")
    print("=" * 60)
    
    engine = create_engine(mode='harmonic')
    
    # Lydian mode sequence
    print("\nLydian Mode Triads (D Lydian):")
    result = engine.generate_scale_triads('D', 'lydian')
    
    for i, triad in enumerate(result.data):
        voices = ', '.join(str(v) for v in sorted(triad.voices, key=lambda n: n.midi_number))
        print(f"  Degree {i+1}: {triad.symbol:6} [{voices}]")
    
    # Voice lead a modal progression
    print("\nModal Chord Progression (Voice-Led):")
    modal_prog = ['Dmaj7', 'Emaj7', 'F#m7', 'Gmaj7#11']
    result = engine.voice_lead_progression(['D', 'E', 'F#m', 'G'])
    
    for triad in result.data['triads']:
        voices = ', '.join(str(v) for v in sorted(triad.voices, key=lambda n: n.midi_number))
        print(f"  {triad.symbol:6} [{voices}]")


def demo_exports():
    """Demo: Export functionality."""
    print("\n" + "=" * 60)
    print("EXPORT DEMO")
    print("=" * 60)
    
    engine = create_engine()
    
    # Generate some triads
    result = engine.generate_scale_triads('C', 'ionian')
    triads = result.data[:4]
    
    # Export to JSON
    print("\nJSON Export (preview):")
    json_preview = {
        'triads': [t.to_dict() for t in triads[:2]],
        'count': len(triads)
    }
    print(json.dumps(json_preview, indent=2)[:500] + "...")
    
    print("\nAvailable Export Formats:")
    print("  - MusicXML (.xml)  - Standard notation interchange")
    print("  - JSON (.json)     - Data interchange")
    print("  - TAB (.txt)       - Guitar tablature")
    print("  - HTML Etude       - Print-ready practice sheet")


def main():
    """Run all demos."""
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "  OPEN TRIAD ENGINE v1.0 - COMPLETE DEMO  ".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    # Run all demos
    demo_melodic_mode()
    demo_harmonic_mode()
    demo_chord_melody_mode()
    demo_counterpoint_mode()
    demo_orchestration_mode()
    demo_two_five_one()
    demo_triad_pairs()
    demo_shape_bundles()
    demo_modal_sequence()
    demo_exports()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nThe Open Triad Engine is ready for integration with:")
    print("  - EtudeGen")
    print("  - MAMS (Music Analysis and Manipulation System)")
    print("  - TriadPair Engine")
    print("  - Counterpoint Companion")
    print("  - Quartet Engine")
    print("  - And more...")
    print("\nSee README.md for full documentation.")


if __name__ == '__main__':
    main()

