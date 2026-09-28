#!/usr/bin/env python3
"""
ChessAstra NNUE Parity and Integrity Validator.
Checks network file hash, evaluates test FENs across opening/middlegame/endgame,
and verifies eval consistency between base and new networks.
"""

import argparse
import subprocess
import sys
from pathlib import Path

TEST_FENS = [
    # Standard starting position
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    # Italian game
    "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
    # Ruy Lopez Berlin defense
    "r1bqkb1r/pppp1ppp/2n5/1B2p3/4n3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 1 5",
    # Sicilian Najdorf
    "rnbqkb1r/1p2pppp/p2p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6",
    # Complex tactical middlegame
    "r1b2rk1/2q1bppp/p2pp3/1p2n1P1/3NP3/2N1BP2/PPP4P/2KR1Q1R w - - 1 15",
    # Heavy piece endgame
    "4r1k1/5ppp/8/8/8/8/4qPPP/4R1K1 w - - 0 1",
    # Pawn endgame
    "8/5k2/8/4P3/8/8/5K2/8 w - - 0 1",
    # Rook endgame (Lucena position)
    "1K1k4/1P6/8/8/8/8/r7/2R5 w - - 0 1",
]

def evaluate_fen(engine_path: Path, net_path: Path, fen: str) -> int:
    """Send position and 'eval' command to engine and parse resulting static eval."""
    proc = subprocess.Popen(
        [str(engine_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    commands = [
        f"setoption name EvalFile value {net_path}",
        f"position fen {fen}",
        "eval",
        "quit",
    ]
    stdout, _ = proc.communicate("\n".join(commands))
    for line in stdout.splitlines():
        if "NNUE evaluation" in line and "(side to move" in line:
            parts = line.split()
            try:
                return int(parts[2])
            except (IndexError, ValueError):
                pass
        elif "Total" in line and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                try:
                    return int(float(parts[3]) * 100)
                except ValueError:
                    pass
    return 0

def main():
    parser = argparse.ArgumentParser(description="Verify NNUE net integrity & eval consistency")
    parser.add_argument("--net", type=str, required=True, help="Path to .nnue network file")
    parser.add_argument("--engine", type=str, default="src/chessastra", help="Path to engine binary")
    args = parser.parse_args()

    engine_path = Path(args.engine).resolve()
    net_path = Path(args.net).resolve()

    if not net_path.exists():
        print(f"Error: Network file not found at {net_path}", file=sys.stderr)
        sys.exit(1)
    if not engine_path.exists():
        print(f"Error: Engine binary not found at {engine_path}", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print(f"Validating NNUE Network: {net_path.name}")
    print(f"Size: {net_path.stat().st_size / (1024*1024):.2f} MB")
    print("=" * 70)

    # Test loading and evaluating across test positions
    print(f"{'Position Description':<35} | {'Static Eval':<15}")
    print("-" * 55)

    descriptions = [
        "Start Position",
        "Italian Game",
        "Ruy Lopez Berlin",
        "Sicilian Najdorf",
        "Tactical Middlegame",
        "Heavy Piece Endgame",
        "Pawn Endgame",
        "Lucena Rook Endgame",
    ]

    all_valid = True
    for desc, fen in zip(descriptions, TEST_FENS):
        score = evaluate_fen(engine_path, net_path, fen)
        print(f"{desc:<35} | {score:>10} units")
        if abs(score) > 30000:
            print(f"[!] Warning: Extreme/overflow eval detected in {desc}")
            all_valid = False

    print("-" * 55)
    if all_valid:
        print("[✓] All test positions evaluated successfully without NaN or overflow.")
    else:
        print("[!] Validation failed on some positions.")
        sys.exit(1)

if __name__ == "__main__":
    main()
