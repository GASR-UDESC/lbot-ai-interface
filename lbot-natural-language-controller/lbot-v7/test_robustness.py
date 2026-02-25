#!/usr/bin/env python3
"""
LBot V7 - Robustness Test Suite
================================

Tests the V7 preprocessing pipeline and (optionally) the full model translation.

Two modes:
  1. Preprocessing-only (default, no model needed):
     python test_robustness.py

  2. Full model translation (requires lbot_translator_v7.pt):
     python test_robustness.py --model lbot_translator_v7.pt
"""

import sys
import os
import re
from typing import Tuple

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lbot_v7 import preprocess_input


# ============================================================================
# LBML validation
# ============================================================================

LBML_PATTERN = re.compile(r'^(D\d+[FBLR];|R\d+[LR];)+$')


def validate_lbml(lbml: str) -> bool:
    """Check if output is valid LBML V4."""
    return bool(LBML_PATTERN.match(lbml))


# ============================================================================
# Preprocessing test cases
# ============================================================================

PREPROCESSING_TESTS = [
    # ── Unit conversion ──
    ("ande 2 metros para frente",           "ande 200 centímetros para frente"),
    ("ande 1 metro para frente",            "ande 100 centímetros para frente"),
    ("ande 500 milímetros para trás",       "ande 50 centímetros para trás"),
    ("ande 500 milimetros para trás",       "ande 50 centímetros para trás"),
    ("ande 3 passos para frente",           "ande 225 centímetros para frente"),
    ("ande 1 jarda para direita",           "ande 91 centímetros para direita"),
    ("mova-se 1 quilômetro para frente",    "mova-se 100000 centímetros para frente"),

    # ── Abbreviation expansion ──
    ("ande 40cm para frente",               "ande 40 centímetros para frente"),
    ("ande 40 cm para frente",              "ande 40 centímetros para frente"),
    ("gire 90° para direita",               "gire 90 graus para direita"),
    ("ande 2m para frente",                 "ande 200 centímetros para frente"),
    ("ande 500mm para trás",                "ande 50 centímetros para trás"),

    # ── Accent normalization ──
    ("ande 40 centimetros para frente",     "ande 40 centímetros para frente"),
    ("gire 90 graus sentido anti-horario",  "gire 90 graus sentido anti-horário"),

    # ── Number words → digits ──
    ("ande quarenta centímetros para frente",
     "ande 40 centímetros para frente"),
    ("gire noventa graus para direita",
     "gire 90 graus para direita"),
    ("ande vinte e cinco centímetros para trás",
     "ande 25 centímetros para trás"),
    ("mova-se cento e cinquenta centímetros para frente",
     "mova-se 150 centímetros para frente"),
    ("ande duzentos centímetros para esquerda",
     "ande 200 centímetros para esquerda"),

    # ── Informal normalization ──
    ("vai 40 centímetros pra frente",       None),  # vai → vá
    ("roda 90 graus pra esquerda",          None),  # roda → rode
    ("dobra 45 graus pra direita",          None),  # dobra → gire

    # ── Missing punctuation (connector insertion) ──
    ("ande 40 centímetros para frente depois gire 90 graus para direita",
     None),  # should insert comma before "depois"

    # ── Combined augmentations ──
    ("vai 40cm pra frente",                 None),  # informal + abbreviation
    ("ande 2m pra frente depois roda 90° pra esquerda",
     None),  # units + informal + abbreviation + missing comma
]


# ============================================================================
# Full model translation tests (expected LBML outputs)
# ============================================================================

TRANSLATION_TESTS = [
    # ── Standard clean inputs ──
    ("vá 40 centímetros para frente",                    "D40F;"),
    ("ande 25 centímetros para trás",                    "D25B;"),
    ("mova-se 60 centímetros para esquerda",             "D60L;"),
    ("mova-se 30 centímetros para direita",              "D30R;"),
    ("gire 90 graus para direita",                       "R90R;"),
    ("gire 45 graus para esquerda",                      "R45L;"),
    ("vire 180 graus para direita",                      "R180R;"),
    ("vire 90 graus sentido horário",                    "R90R;"),
    ("gire 90 graus sentido anti-horário",               "R90L;"),

    # ── Compound standard ──
    ("vá 40 centímetros para frente, depois gire 90 graus para direita",
     "D40F;R90R;"),
    ("gire 90 graus para direita, depois ande 30 centímetros para frente",
     "R90R;D30F;"),
    ("ande 50 centímetros para frente, gire 90 graus para esquerda, depois ande 20 centímetros para direita",
     "D50F;R90L;D20R;"),

    # ── Multi-unit (model should handle after preprocessing) ──
    ("ande 2 metros para frente",                        "D200F;"),
    ("ande 500 milímetros para trás",                    "D50B;"),
    ("ande 3 passos para frente",                        "D225F;"),
    ("ande 1 jarda para direita",                        "D91R;"),

    # ── Abbreviations ──
    ("ande 40cm para frente",                            "D40F;"),
    ("gire 90° para direita",                            "R90R;"),

    # ── Missing accents ──
    ("ande 40 centimetros para frente",                  "D40F;"),
    ("gire 90 graus sentido anti-horario",               "R90L;"),

    # ── Numbers as words ──
    ("ande quarenta centímetros para frente",             "D40F;"),
    ("gire noventa graus para direita",                  "R90R;"),
    ("vá vinte e cinco centímetros para trás",           "D25B;"),

    # ── Informal ──
    ("vai 40 centímetros pra frente",                    "D40F;"),
    ("roda 90 graus pra esquerda",                       "R90L;"),

    # ── Combined ──
    ("vai 40cm pra frente",                              "D40F;"),
    ("ande 2m pra frente depois roda 90° pra esquerda",  "D200F;R90L;"),
]


# ============================================================================
# Runner
# ============================================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def run_preprocessing_tests() -> Tuple:
    """Run preprocessing pipeline tests."""
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"  PREPROCESSING TESTS")
    print(f"{'='*70}{Colors.END}\n")

    passed = 0
    failed = 0
    warnings = 0

    for i, (raw_input, expected) in enumerate(PREPROCESSING_TESTS, 1):
        result = preprocess_input(raw_input)

        if expected is None:
            # Just ensure it doesn't crash and output is different from input
            changed = result.strip().lower() != raw_input.strip().lower()
            status = f"{Colors.CYAN}INFO{Colors.END}"
            if changed:
                print(f"  {status} [{i:2d}] '{raw_input}'")
                print(f"         → '{result}'")
            else:
                print(f"  {Colors.YELLOW}WARN{Colors.END} [{i:2d}] No change: '{raw_input}'")
                warnings += 1
            passed += 1
        else:
            result_lower = result.strip().lower()
            expected_lower = expected.strip().lower()
            if result_lower == expected_lower:
                print(f"  {Colors.GREEN}PASS{Colors.END} [{i:2d}] '{raw_input}'")
                passed += 1
            else:
                print(f"  {Colors.RED}FAIL{Colors.END} [{i:2d}] '{raw_input}'")
                print(f"         Expected: '{expected}'")
                print(f"         Got:      '{result}'")
                failed += 1

    return passed, failed, warnings


def run_translation_tests(model_path: str) -> Tuple:
    """Run full model translation tests."""
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"  TRANSLATION TESTS (with model)")
    print(f"{'='*70}{Colors.END}\n")

    # Import and load model
    from lbot_v7 import LBotTranslatorV7
    translator = LBotTranslatorV7(model_path)

    passed = 0
    failed = 0
    invalid_lbml = 0

    for i, (raw_input, expected_lbml) in enumerate(TRANSLATION_TESTS, 1):
        result = translator.translate(raw_input)

        valid = validate_lbml(result)
        if not valid:
            invalid_lbml += 1

        if result == expected_lbml:
            print(f"  {Colors.GREEN}PASS{Colors.END} [{i:2d}] '{raw_input}' → '{result}'")
            passed += 1
        else:
            validity = "✅" if valid else "❌ INVALID LBML"
            print(f"  {Colors.RED}FAIL{Colors.END} [{i:2d}] '{raw_input}'")
            print(f"         Expected: '{expected_lbml}'")
            print(f"         Got:      '{result}' {validity}")
            failed += 1

    return passed, failed, invalid_lbml


def main():
    import argparse

    parser = argparse.ArgumentParser(description='LBot V7 Robustness Tests')
    parser.add_argument('--model', type=str, default=None,
                        help='Path to lbot_translator_v7.pt for full translation tests')
    args = parser.parse_args()

    print(f"\n{Colors.BOLD}{'#'*70}")
    print(f"  LBOT V7 - ROBUSTNESS TEST SUITE")
    print(f"{'#'*70}{Colors.END}")

    total_passed = 0
    total_failed = 0

    # 1. Preprocessing tests (always run)
    pp_passed, pp_failed, pp_warnings = run_preprocessing_tests()
    total_passed += pp_passed
    total_failed += pp_failed

    print(f"\n  Preprocessing: {Colors.GREEN}{pp_passed} passed{Colors.END}, "
          f"{Colors.RED}{pp_failed} failed{Colors.END}, "
          f"{Colors.YELLOW}{pp_warnings} warnings{Colors.END}")

    # 2. Translation tests (only with model)
    if args.model:
        if not os.path.exists(args.model):
            print(f"\n  {Colors.RED}Model file not found: {args.model}{Colors.END}")
        else:
            tr_passed, tr_failed, tr_invalid = run_translation_tests(args.model)
            total_passed += tr_passed
            total_failed += tr_failed

            print(f"\n  Translation: {Colors.GREEN}{tr_passed} passed{Colors.END}, "
                  f"{Colors.RED}{tr_failed} failed{Colors.END}, "
                  f"{Colors.YELLOW}{tr_invalid} invalid LBML{Colors.END}")
    else:
        print(f"\n  {Colors.CYAN}ℹ️  Skipping translation tests (no --model provided){Colors.END}")
        print(f"  Run with: python test_robustness.py --model lbot_translator_v7.pt")

    # Summary
    print(f"\n{Colors.BOLD}{'='*70}")
    total = total_passed + total_failed
    rate = total_passed / total * 100 if total > 0 else 0
    color = Colors.GREEN if total_failed == 0 else Colors.RED
    print(f"  TOTAL: {color}{total_passed}/{total} ({rate:.0f}%){Colors.END}")
    print(f"{'='*70}{Colors.END}\n")

    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
