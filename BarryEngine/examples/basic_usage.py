"""
Basic Usage Examples for Barry Engine
=====================================

Demonstrates how to use Barry for analysis and transformation.
"""

from barry_engine import (
    GMLPhrase, GMLProgression, GMLSection, GMLForm, PhraseRole,
    BarryEngine,
    note_from_midi, note_from_name, phrase_from_pitches,
    score_phrase_movement, score_phrase_bebop_idiom,
    improve_line_movement, add_bebop_enclosures, strengthen_cadence
)


def example_1_basic_analysis():
    """Example 1: Basic phrase analysis."""
    print("=" * 60)
    print("Example 1: Basic Phrase Analysis")
    print("=" * 60)
    
    # Create a simple phrase (C major scale)
    notes = [
        note_from_midi(60, duration=0.5, onset=0.0),   # C4
        note_from_midi(62, duration=0.5, onset=0.5),   # D4
        note_from_midi(64, duration=0.5, onset=1.0),   # E4
        note_from_midi(65, duration=0.5, onset=1.5),   # F4
        note_from_midi(67, duration=0.5, onset=2.0),   # G4
    ]
    
    phrase = GMLPhrase(
        notes=notes,
        bar_start=1,
        bar_end=1,
        key="C"
    )
    
    # Create a progression
    progression = GMLProgression(
        chords=["Cmaj7", "Am7", "Dm7", "G7"],
        key="C"
    )
    
    # Analyze
    engine = BarryEngine()
    result = engine.analyze_phrase(phrase, progression)
    
    print(f"\nOverall Score: {result.overall:.2f}")
    print(f"\nMovement Analysis:")
    print(f"  Stepwise ratio: {result.movement.stepwise_ratio:.2f}")
    print(f"  Guide tone score: {result.movement.guide_tone_score:.2f}")
    print(f"  Voice-leading score: {result.movement.voice_leading_score:.2f}")
    print(f"  Leap penalty: {result.movement.leap_penalty:.2f}")
    print(f"  Overall: {result.movement.overall:.2f}")
    
    print(f"\nBebop Analysis:")
    print(f"  8th-note ratio: {result.bebop.eighth_note_ratio:.2f}")
    print(f"  Chord tone targeting: {result.bebop.chord_tone_targeting:.2f}")
    print(f"  Approach tone usage: {result.bebop.approach_tone_usage:.2f}")
    print(f"  Overall: {result.bebop.overall:.2f}")
    
    print(f"\nTags:")
    for tag in result.tags[:5]:
        print(f"  - {tag}")


def example_2_movement_improvement():
    """Example 2: Improving movement in a phrase."""
    print("\n" + "=" * 60)
    print("Example 2: Improving Movement")
    print("=" * 60)
    
    # Create a phrase with a large leap
    notes = [
        note_from_midi(60, duration=1.0, onset=0.0),   # C4
        note_from_midi(72, duration=1.0, onset=1.0),   # C5 (octave leap)
        note_from_midi(64, duration=1.0, onset=2.0),   # E4
    ]
    
    phrase = GMLPhrase(notes=notes, key="C")
    
    # Analyze before
    engine = BarryEngine()
    before = engine.analyze_phrase(phrase)
    print(f"\nBefore improvement:")
    print(f"  Movement score: {before.movement.overall:.2f}")
    print(f"  Leap penalty: {before.movement.leap_penalty:.2f}")
    
    # Improve
    result = improve_line_movement(phrase)
    
    print(f"\nAfter improvement:")
    print(f"  Changes made: {len(result.changes_made)}")
    for change in result.changes_made:
        print(f"    - {change}")
    
    after = engine.analyze_phrase(result.phrase)
    print(f"  Movement score: {after.movement.overall:.2f}")
    print(f"  Leap penalty: {after.movement.leap_penalty:.2f}")


def example_3_bebop_enclosures():
    """Example 3: Adding bebop enclosures."""
    print("\n" + "=" * 60)
    print("Example 3: Adding Bebop Enclosures")
    print("=" * 60)
    
    # Create a phrase with chord tones
    notes = [
        note_from_midi(60, duration=0.5, onset=0.0),   # C4
        note_from_midi(64, duration=0.5, onset=0.5),   # E4
        note_from_midi(67, duration=0.5, onset=1.0),   # G4
    ]
    
    phrase = GMLPhrase(
        notes=notes,
        harmonic_progression=["Cmaj7"],
        key="C"
    )
    
    # Add enclosures
    result = add_bebop_enclosures(phrase)
    
    print(f"\nOriginal phrase: {len(phrase.notes)} notes")
    print(f"With enclosures: {len(result.phrase.notes)} notes")
    print(f"\nChanges made:")
    for change in result.changes_made:
        print(f"  - {change}")


def example_4_section_analysis():
    """Example 4: Analyzing a section."""
    print("\n" + "=" * 60)
    print("Example 4: Section Analysis")
    print("=" * 60)
    
    # Create multiple phrases
    phrase1 = phrase_from_pitches(
        [60, 62, 64, 65],
        durations=[0.5, 0.5, 0.5, 0.5],
        key="C",
        bar_start=1
    )
    phrase1.role = PhraseRole.OPENING
    
    phrase2 = phrase_from_pitches(
        [67, 69, 71, 72],
        durations=[0.5, 0.5, 0.5, 0.5],
        key="C",
        bar_start=5
    )
    phrase2.role = PhraseRole.CONTINUATION
    
    phrase3 = phrase_from_pitches(
        [72, 71, 69, 67],
        durations=[0.5, 0.5, 0.5, 1.0],
        key="C",
        bar_start=9
    )
    phrase3.role = PhraseRole.CADENTIAL
    
    # Create section
    section = GMLSection(
        phrases=[phrase1, phrase2, phrase3],
        label="A",
        form=GMLForm.AABA,
        key="C"
    )
    
    # Analyze
    engine = BarryEngine()
    result = engine.analyze_section(section)
    
    print(f"\nSection Analysis:")
    print(f"  Overall score: {result.overall:.2f}")
    print(f"\nGCE Scores:")
    print(f"  Tension-release: {result.gce.tension_release:.2f}")
    print(f"  Motivic development: {result.gce.motivic_development:.2f}")
    print(f"  Form alignment: {result.gce.form_alignment:.2f}")
    print(f"  Idiomaticity: {result.gce.idiomaticity:.2f}")
    print(f"  Playability: {result.gce.playability:.2f}")
    
    print(f"\nTags:")
    for tag in result.tags[:5]:
        print(f"  - {tag}")


def example_5_candidate_evaluation():
    """Example 5: Evaluating multiple candidates."""
    print("\n" + "=" * 60)
    print("Example 5: Candidate Evaluation")
    print("=" * 60)
    
    from barry_engine import evaluate_phrase_bundle, suggest_best_candidate_line
    
    # Create three candidate phrases
    candidate1 = phrase_from_pitches(
        [60, 62, 64, 65],
        durations=[0.5, 0.5, 0.5, 0.5],
        key="C"
    )
    
    candidate2 = phrase_from_pitches(
        [60, 64, 67, 72],  # More leaps
        durations=[0.5, 0.5, 0.5, 0.5],
        key="C"
    )
    
    candidate3 = phrase_from_pitches(
        [60, 61, 62, 64],  # Stepwise
        durations=[0.5, 0.5, 0.5, 0.5],
        key="C"
    )
    
    candidates = [candidate1, candidate2, candidate3]
    
    # Evaluate all
    results = evaluate_phrase_bundle(candidates)
    
    print(f"\nCandidate Scores:")
    for i, result in enumerate(results, 1):
        print(f"  Candidate {i}: {result.overall:.2f}")
        print(f"    Movement: {result.movement.overall:.2f}")
        print(f"    Bebop: {result.bebop.overall:.2f}")
    
    # Suggest best
    best_phrase, best_result = suggest_best_candidate_line(candidates)
    print(f"\nBest candidate: Score {best_result.overall:.2f}")


if __name__ == "__main__":
    example_1_basic_analysis()
    example_2_movement_improvement()
    example_3_bebop_enclosures()
    example_4_section_analysis()
    example_5_candidate_evaluation()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)

