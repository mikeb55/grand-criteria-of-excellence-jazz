"""
Demo Phrases for Triad Pair Solo Engine
=========================================

Generates example phrases demonstrating various capabilities:
1. Intervallic modal open-triad pair line
2. Altered-dominant open-triad pair over V7alt
3. Functional ii-V-I phrase using APVL + TRAM
4. Large-leap modern-jazz phrase using SISM spacing
"""

import sys
import os
from pathlib import Path

# Add parent directories to path for both module and direct execution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, grandparent_dir)

try:
    from triad_pair_solo_engine.engine import TriadPairSoloEngine
    from triad_pair_solo_engine.inputs import TriadPairType, SoloMode, RhythmicStyle
except ImportError:
    from engine import TriadPairSoloEngine
    from inputs import TriadPairType, SoloMode, RhythmicStyle

def generate_all_demos(output_dir: str = None):
    """
    Generate all demo phrases and export to files.
    
    Args:
        output_dir: Output directory (defaults to 'exports' subdirectory)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "exports"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("TRIAD PAIR SOLO ENGINE - DEMO PHRASES")
    print("=" * 60)
    
    # Demo 1: Intervallic Modal Line
    print("\n1. INTERVALLIC MODAL OPEN-TRIAD PAIR LINE")
    print("-" * 40)
    
    engine1 = TriadPairSoloEngine(
        key="D",
        scale="dorian",
        triad_pair_type="diatonic",
        mode="intervallic",
        rhythmic_style="swing",
        contour="wave",
        difficulty="intermediate",
        seed=42
    )
    
    phrase1 = engine1.demo_intervallic_modal()
    print(f"Generated {phrase1.bar_count} bars with {len(phrase1.notes)} notes")
    print(f"Triad pairs: {len(phrase1.triad_pairs)}")
    print(f"Pitch range: {phrase1.get_pitch_range()}")
    
    files1 = engine1.export(phrase1, str(output_dir / "demo_1_intervallic_modal"))
    print(f"Exported to: {list(files1.values())}")
    
    # Demo 2: Altered Dominant
    print("\n2. ALTERED-DOMINANT OPEN-TRIAD PAIR OVER V7alt")
    print("-" * 40)
    
    engine2 = TriadPairSoloEngine(
        key="G",
        scale="altered",
        triad_pair_type="altered_dominant_pairs",
        mode="intervallic",
        rhythmic_style="swing",
        difficulty="advanced",
        seed=42
    )
    
    phrase2 = engine2.demo_altered_dominant()
    print(f"Generated {phrase2.bar_count} bars with {len(phrase2.notes)} notes")
    print(f"Triad pairs used: {[str(tp) for tp in phrase2.triad_pairs]}")
    
    files2 = engine2.export(phrase2, str(output_dir / "demo_2_altered_dominant"))
    print(f"Exported to: {list(files2.values())}")
    
    # Demo 3: Functional ii-V-I
    print("\n3. FUNCTIONAL ii-V-I PHRASE (APVL + TRAM)")
    print("-" * 40)
    
    engine3 = TriadPairSoloEngine(
        key="C",
        scale="major",
        progression=["Dm7", "G7", "Cmaj7"],
        triad_pair_type="diatonic",
        mode="functional",
        rhythmic_style="swing",
        difficulty="intermediate",
        seed=42
    )
    
    phrase3 = engine3.demo_functional_251()
    print(f"Generated {phrase3.bar_count} bars with {len(phrase3.notes)} notes")
    print(f"Voice-leading analyses: {len(phrase3.voice_leading_analysis)}")
    
    for i, vl in enumerate(phrase3.voice_leading_analysis):
        print(f"  Transition {i+1}: {vl.narrative}")
    
    files3 = engine3.export(phrase3, str(output_dir / "demo_3_functional_251"))
    print(f"Exported to: {list(files3.values())}")
    
    # Demo 4: Large-Leap SISM
    print("\n4. LARGE-LEAP MODERN-JAZZ PHRASE (SISM SPACING)")
    print("-" * 40)
    
    engine4 = TriadPairSoloEngine(
        key="Eb",
        scale="lydian",
        triad_pair_type="ust",
        mode="intervallic",
        rhythmic_style="syncopated",
        difficulty="advanced",
        seed=42
    )
    
    phrase4 = engine4.demo_large_leap()
    print(f"Generated {phrase4.bar_count} bars with {len(phrase4.notes)} notes")
    
    # Calculate average leap size
    pitches = phrase4.get_pitches()
    if len(pitches) > 1:
        leaps = [abs(pitches[i+1] - pitches[i]) for i in range(len(pitches)-1)]
        avg_leap = sum(leaps) / len(leaps)
        max_leap = max(leaps)
        print(f"Average leap: {avg_leap:.1f} semitones, Max leap: {max_leap} semitones")
    
    files4 = engine4.export(phrase4, str(output_dir / "demo_4_large_leap_sism"))
    print(f"Exported to: {list(files4.values())}")
    
    return demos
    
    # Summary
    print("\n" + "=" * 60)
    print("DEMO GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nAll files saved to: {output_dir}")
    print("\nGenerated demos:")
    print("  1. demo_1_intervallic_modal - D Dorian intervallic line")
    print("  2. demo_2_altered_dominant - G7alt altered pairs")
    print("  3. demo_3_functional_251 - C major ii-V-I with APVL")
    print("  4. demo_4_large_leap_sism - Eb Lydian UST with wide spacing")
    
    return {
        "intervallic_modal": phrase1,
        "altered_dominant": phrase2,
        "functional_251": phrase3,
        "large_leap_sism": phrase4,
    }


def interactive_demo():
    """Run an interactive demo showing engine capabilities."""
    print("\n" + "=" * 60)
    print("INTERACTIVE TRIAD PAIR SOLO ENGINE DEMO")
    print("=" * 60)
    
    # Create engine
    engine = TriadPairSoloEngine(
        key="C",
        scale="major",
        mode="intervallic",
        seed=42
    )
    
    # Show available triad pairs
    print("\n--- DIATONIC TRIAD PAIRS ---")
    pairs = engine.get_triad_pairs(count=4)
    for i, pair in enumerate(pairs):
        print(f"Pair {i+1}: {pair}")
    
    # Generate a simple pattern
    print("\n--- PATTERN FROM FIRST PAIR ---")
    from patterns import PatternType
    cell = engine.generate_pattern(pairs[0], PatternType.UP_ARPEGGIO)
    print(f"Pattern: {cell.get_pitch_names()}")
    print(f"Contour: {cell.contour}")
    
    # Analyze voice-leading
    print("\n--- VOICE-LEADING ANALYSIS ---")
    if len(pairs) >= 2:
        vl = engine.analyze_voice_leading(pairs[0], pairs[1])
        print(f"Motion intervals: {vl.motion_intervals}")
        print(f"Motion types: {vl.motion_types}")
        print(f"Narrative: {vl.narrative}")
        print(f"Tension level: {vl.tension_level:.2f}")
    
    # Generate and display phrase
    print("\n--- GENERATED 4-BAR PHRASE ---")
    phrase = engine.generate_phrase(bars=4)
    print(f"Notes: {len(phrase.notes)}")
    print(f"Structure: {phrase.structure.value}")
    print(f"First 8 pitches: {[n.pitch_name for n in phrase.notes[:8]]}")
    
    # Show JSON preview
    print("\n--- JSON PREVIEW ---")
    json_data = engine.to_json(phrase)
    print(f"Keys: {list(json_data.keys())}")
    print(f"Note count in JSON: {len(json_data['notes'])}")
    
    return engine, phrase


demos = {}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Triad Pair Solo Engine Demos")
    parser.add_argument("--output", "-o", type=str, help="Output directory")
    parser.add_argument("--interactive", "-i", action="store_true", 
                        help="Run interactive demo")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_demo()
    else:
        generate_all_demos(args.output)

