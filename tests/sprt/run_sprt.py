#!/usr/bin/env python3
"""
ChessAstra SPRT & Match Runner
Automates Sequential Probability Ratio Tests (SPRT) against baseline Stockfish.
"""

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_FASTCHESS = Path(__file__).resolve().parent.parent / "bin" / "fastchess"
DEFAULT_BOOK = Path(__file__).resolve().parent.parent / "books" / "UHO_Lichess_4852_v1.epd"
DEFAULT_ENGINE1 = Path(__file__).resolve().parent.parent.parent / "src" / "chessastra"
DEFAULT_ENGINE2 = Path(__file__).resolve().parent.parent / "baseline" / "stockfish-19-official"

TC_PRESETS = {
    "STC": {"tc": "10+0.1", "hash": 16},
    "LTC": {"tc": "60+0.6", "hash": 64},
    "VLTC": {"tc": "120+1.2", "hash": 128},
    "ULTRAFAST": {"tc": "5+0.05", "hash": 16},
}

def parse_args():
    parser = argparse.ArgumentParser(description="Run SPRT test for ChessAstra vs baseline")
    parser.add_argument("--engine1", type=str, default=str(DEFAULT_ENGINE1), help="Path to ChessAstra binary")
    parser.add_argument("--name1", type=str, default="ChessAstra", help="Display name for engine 1")
    parser.add_argument("--net1", type=str, default=None, help="Custom .nnue network for engine 1")
    parser.add_argument("--engine2", type=str, default=str(DEFAULT_ENGINE2), help="Path to Baseline Stockfish binary")
    parser.add_argument("--name2", type=str, default="Stockfish19-Baseline", help="Display name for engine 2")
    parser.add_argument("--net2", type=str, default=None, help="Custom .nnue network for engine 2")
    parser.add_argument("--tc", type=str, default="STC", help="Time control preset (STC, LTC, VLTC, ULTRAFAST) or raw string e.g. 10+0.1")
    parser.add_argument("--hash", type=int, default=None, help="Hash size in MB (defaults based on TC)")
    parser.add_argument("--threads", type=int, default=1, help="Threads per engine instance (default: 1)")
    parser.add_argument("--concurrency", type=int, default=max(1, (os.cpu_count() or 4) - 1), help="Concurrent games")
    parser.add_argument("--elo0", type=float, default=0.0, help="SPRT lower bound (default: 0.0)")
    parser.add_argument("--elo1", type=float, default=3.0, help="SPRT upper bound (default: 3.0)")
    parser.add_argument("--alpha", type=float, default=0.05, help="Type I error alpha (default: 0.05)")
    parser.add_argument("--beta", type=float, default=0.05, help="Type II error beta (default: 0.05)")
    parser.add_argument("--rounds", type=int, default=30000, help="Max game pairs (rounds)")
    parser.add_argument("--book", type=str, default=str(DEFAULT_BOOK), help="Opening book path (.epd or .pgn)")
    parser.add_argument("--fastchess", type=str, default=str(DEFAULT_FASTCHESS), help="Path to fastchess binary")
    parser.add_argument("--pgn", type=str, default=None, help="Output PGN file")
    parser.add_argument("--no-sprt", action="store_true", help="Run fixed rounds match without SPRT early exit")
    return parser.parse_args()

def main():
    args = parse_args()

    # Validate binaries
    engine1_path = Path(args.engine1).resolve()
    engine2_path = Path(args.engine2).resolve()
    fastchess_path = Path(args.fastchess).resolve()
    book_path = Path(args.book).resolve()

    if not engine1_path.exists():
        print(f"Error: Engine 1 binary not found at {engine1_path}", file=sys.stderr)
        sys.exit(1)
    if not engine2_path.exists():
        print(f"Error: Engine 2 binary not found at {engine2_path}", file=sys.stderr)
        sys.exit(1)
    if not fastchess_path.exists():
        print(f"Error: fastchess binary not found at {fastchess_path}", file=sys.stderr)
        sys.exit(1)
    if not book_path.exists():
        # Fallback to lichess book if 4060 does not exist
        alt_book = book_path.parent / "UHO_Lichess_4852_v1.epd"
        if alt_book.exists():
            book_path = alt_book
        else:
            print(f"Error: Opening book not found at {book_path}", file=sys.stderr)
            sys.exit(1)

    # Determine TC & Hash
    if args.tc.upper() in TC_PRESETS:
        tc_str = TC_PRESETS[args.tc.upper()]["tc"]
        hash_size = args.hash if args.hash is not None else TC_PRESETS[args.tc.upper()]["hash"]
    else:
        tc_str = args.tc
        hash_size = args.hash if args.hash is not None else 16

    # Output PGN setup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    match_dir = Path(__file__).resolve().parent / "matches"
    match_dir.mkdir(parents=True, exist_ok=True)
    pgn_file = args.pgn if args.pgn else str(match_dir / f"sprt_{args.name1}_vs_{args.name2}_{args.tc}_{timestamp}.pgn")

    eng1_opts = [f"cmd={engine1_path}", f"name={args.name1}"]
    if args.net1:
        eng1_opts.append(f"option.EvalFile={Path(args.net1).resolve()}")

    eng2_opts = [f"cmd={engine2_path}", f"name={args.name2}"]
    if args.net2:
        eng2_opts.append(f"option.EvalFile={Path(args.net2).resolve()}")

    cmd = [
        str(fastchess_path),
        "-engine", *eng1_opts,
        "-engine", *eng2_opts,
        "-each", f"tc={tc_str}", f"option.Hash={hash_size}", f"option.Threads={args.threads}",
        "-rounds", str(args.rounds),
        "-repeat",
        "-concurrency", str(args.concurrency),
        "-openings", f"file={book_path}", "format=epd", "order=random",
        "-draw", "movenumber=34", "movecount=8", "score=20",
        "-resign", "movecount=3", "score=600",
        "-report", "penta=true",
        "-pgnout", f"file={pgn_file}", "notation=san", "nodes=true",
    ]

    if not args.no_sprt:
        cmd.extend([
            "-sprt",
            f"elo0={args.elo0}",
            f"elo1={args.elo1}",
            f"alpha={args.alpha}",
            f"beta={args.beta}",
            "model=normalized",
        ])

    print("=" * 70)
    print("ChessAstra Automated SPRT Match Runner")
    print("=" * 70)
    print(f"Engine 1 (Dev)     : {args.name1} ({engine1_path})")
    print(f"Engine 2 (Base)    : {args.name2} ({engine2_path})")
    print(f"Time Control       : {tc_str} (Preset: {args.tc})")
    print(f"Hash / Threads     : {hash_size} MB / {args.threads} thread(s)")
    print(f"Concurrency        : {args.concurrency} concurrent games")
    print(f"Opening Book       : {book_path.name}")
    if not args.no_sprt:
        print(f"SPRT Bounds        : elo0={args.elo0}, elo1={args.elo1} (alpha={args.alpha}, beta={args.beta})")
    print(f"PGN Destination    : {pgn_file}")
    print("=" * 70)
    print("Executing command:")
    print(" ".join(cmd))
    print("=" * 70)
    sys.stdout.flush()

    try:
        proc = subprocess.run(cmd)
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
