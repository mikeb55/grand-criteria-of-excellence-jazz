"""Automated test suite for quartal engine progressions."""
import os
import sys
from pathlib import Path
from quartal_engine_wrapper import QuartalEngine
from datetime import datetime

# Test cases - various progressions
TEST_CASES = [
    {
        "name": "Test 1: Blues Progression (Greezy-style)",
        "command": (
            "Generate G mixolydian quartals, 6 bars, half notes; "
            "Generate G# locrian quartals, 1 bars, half notes; "
            "Generate C mixolydian quartals, 2 bars, half notes; "
            "Generate C# locrian quartals, 1 bars, half notes; "
            "Generate G mixolydian quartals, 2 bars, half notes; "
            "Generate E mixolydian quartals, 2 bars, half notes; "
            "Generate A dorian quartals, 2 bars, half notes; "
            "Generate D mixolydian quartals, 2 bars, half notes"
        ),
        "expected_bars": 18,
        "expected_segments": 8
    },
    {
        "name": "Test 2: ii-V-I in D",
        "command": (
            "Generate E dorian quartals, 2 bars, quarter notes; "
            "Generate A mixolydian quartals, 2 bars, quarter notes; "
            "Generate D major quartals, 4 bars, quarter notes"
        ),
        "expected_bars": 8,
        "expected_segments": 3
    },
    {
        "name": "Test 3: Modal Interchange (C major/minor)",
        "command": (
            "Generate C major quartals, 4 bars, half notes; "
            "Generate C dorian quartals, 2 bars, half notes; "
            "Generate C mixolydian quartals, 2 bars, half notes"
        ),
        "expected_bars": 8,
        "expected_segments": 3
    },
    {
        "name": "Test 4: Chromatic Movement",
        "command": (
            "Generate C mixolydian quartals, 2 bars, quarter notes; "
            "Generate C# locrian quartals, 1 bars, quarter notes; "
            "Generate D dorian quartals, 2 bars, quarter notes; "
            "Generate D# locrian quartals, 1 bars, quarter notes; "
            "Generate E mixolydian quartals, 2 bars, quarter notes"
        ),
        "expected_bars": 8,
        "expected_segments": 5
    },
    {
        "name": "Test 5: Extended Form (16 bars)",
        "command": (
            "Generate F mixolydian quartals, 4 bars, half notes; "
            "Generate Bb mixolydian quartals, 4 bars, half notes; "
            "Generate F mixolydian quartals, 4 bars, half notes; "
            "Generate C mixolydian quartals, 4 bars, half notes"
        ),
        "expected_bars": 16,
        "expected_segments": 4
    }
]

def evaluate_result(test_case, result_path, segments_parsed):
    """Evaluate a test result."""
    issues = []
    successes = []
    
    # Check if file exists
    if not result_path or not os.path.exists(result_path):
        issues.append("[ERROR] Generated file not found")
        return {"status": "FAILED", "issues": issues, "successes": []}
    
    # Check file size
    file_size = os.path.getsize(result_path)
    if file_size < 1000:
        issues.append(f"[WARN] File suspiciously small ({file_size} bytes)")
    else:
        successes.append(f"[OK] File generated ({file_size:,} bytes)")
    
    # Check parsing
    if len(segments_parsed) != test_case["expected_segments"]:
        issues.append(f"[ERROR] Expected {test_case['expected_segments']} segments, got {len(segments_parsed)}")
    else:
        successes.append(f"[OK] Correct number of segments ({len(segments_parsed)})")
    
    # Check total bars
    if segments_parsed:
        total_bars = segments_parsed[-1][3]  # end_bar of last segment
        if total_bars != test_case["expected_bars"]:
            issues.append(f"[ERROR] Expected {test_case['expected_bars']} bars, got {total_bars}")
        else:
            successes.append(f"[OK] Correct total bars ({total_bars})")
    
    # Check bar ranges are sequential
    if segments_parsed:
        prev_end = 0
        for i, (root, scale, start, end) in enumerate(segments_parsed, 1):
            if start != prev_end + 1:
                issues.append(f"[ERROR] Segment {i} starts at bar {start}, expected {prev_end + 1}")
            prev_end = end
    
    if not issues:
        status = "PASSED"
    elif len(issues) < len(successes):
        status = "PARTIAL"
    else:
        status = "FAILED"
    
    return {"status": status, "issues": issues, "successes": successes}

def main():
    """Run automated test suite."""
    print("="*70)
    print("QUARTAL ENGINE AUTOMATED TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    engine = QuartalEngine()
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'='*70}")
        print(f"{test_case['name']}")
        print(f"{'='*70}")
        print(f"Command: {test_case['command'][:80]}...")
        
        try:
            # Parse segments first
            segments = engine.parse_semicolon_commands(test_case['command'])
            print(f"\nParsed {len(segments)} segments:")
            for j, (root, scale, start, end) in enumerate(segments, 1):
                print(f"  {j}. {root} {scale}: bars {start}-{end}")
            
            # Generate
            print("\nGenerating...")
            result_path = engine.generate_from_semicolon_commands(
                test_case['command'],
                stack_type="3-note"
            )
            
            print(f"[OK] Generated: {result_path}")
            
            # Evaluate
            evaluation = evaluate_result(test_case, result_path, segments)
            results.append({
                "test": test_case['name'],
                "result_path": result_path,
                "evaluation": evaluation,
                "segments": segments
            })
            
            # Print evaluation
            print(f"\nStatus: {evaluation['status']}")
            if evaluation['successes']:
                for success in evaluation['successes']:
                    print(f"  {success}")
            if evaluation['issues']:
                for issue in evaluation['issues']:
                    print(f"  {issue}")
                    
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            results.append({
                "test": test_case['name'],
                "result_path": None,
                "evaluation": {"status": "ERROR", "issues": [f"Exception: {str(e)}"], "successes": []},
                "segments": []
            })
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results if r['evaluation']['status'] == "PASSED")
    partial = sum(1 for r in results if r['evaluation']['status'] == "PARTIAL")
    failed = sum(1 for r in results if r['evaluation']['status'] in ["FAILED", "ERROR"])
    
    print(f"\nTotal tests: {len(TEST_CASES)}")
    print(f"  [PASS] Passed: {passed}")
    print(f"  [PARTIAL] Partial: {partial}")
    print(f"  [FAIL] Failed: {failed}")
    
    print("\nDetailed Results:")
    for i, result in enumerate(results, 1):
        status_icon = {
            "PASSED": "[PASS]",
            "PARTIAL": "[PARTIAL]",
            "FAILED": "[FAIL]",
            "ERROR": "[ERROR]"
        }.get(result['evaluation']['status'], "[?]")
        
        print(f"\n{i}. {status_icon} {result['test']}")
        if result['result_path']:
            print(f"   File: {result['result_path']}")
        if result['segments']:
            total_bars = result['segments'][-1][3]
            print(f"   Bars: {total_bars} ({len(result['segments'])} segments)")
    
    print("\n" + "="*70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    return results

if __name__ == "__main__":
    results = main()

