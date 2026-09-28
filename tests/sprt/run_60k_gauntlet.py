#!/usr/bin/env python3
"""
ChessAstra 60,000-Game Gauntlet Runner
Orchestrates massive validation matches vs official Stockfish 19 with:
- Balanced Lichess UHO Opening Suite (2.6M+ positions)
- Pentanomial model analysis and Live Elo Error Bars
- Automated checkpointing, crash recovery, and PGN export
"""

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_ENGINE1 = Path(__file__).resolve().parent.parent.parent / "src" / "chessastra"
DEFAULT_ENGINE2 = Path(__file__).resolve().parent.parent / "baseline" / "stockfish-19-official"
DEFAULT_FASTCHESS = Path(__file__).resolve().parent.parent / "bin" / "fastchess"
DEFAULT_BOOK = Path(__file__).resolve().parent.parent / "books" / "UHO_Lichess_4852_v1.epd"
MATCHES_DIR = Path(__file__).resolve().parent / "matches"

TC_PRESETS = {
    "STC": {"tc": "10+0.1", "hash": 16},
    "LTC": {"tc": "60+0.6", "hash": 64},
    "VLTC": {"tc": "120+1.2", "hash": 128},
    "ULTRAFAST": {"tc": "5+0.05", "hash": 16},
}

def parse_args():
    parser = argparse.ArgumentParser(description="Run 60,000-game match gauntlet for ChessAstra")
    parser.add_argument("--games", type=int, default=60000, help="Total games to play (default: 60000)")
    parser.add_argument("--tc", type=str, default="ULTRAFAST", help="Time control preset or raw string")
    parser.add_argument("--hash", type=int, default=16, help="Hash size in MB")
    parser.add_argument("--threads", type=int, default=1, help="Threads per engine")
    parser.add_argument("--concurrency", type=int, default=max(1, (os.cpu_count() or 4) - 2), help="Concurrent games")
    parser.add_argument("--net1", type=str, default=None, help="Custom NNUE net for ChessAstra")
    parser.add_argument("--pgn", type=str, default=None, help="PGN output path")
    parser.add_argument("--batch-size", type=int, default=1000, help="Checkpoint autosave batch size")
    return parser.parse_args()

def main():
    args = parse_args()
    engine1 = Path(args.engine1 if hasattr(args, "engine1") else DEFAULT_ENGINE1).resolve()
    engine2 = Path(args.engine2 if hasattr(args, "engine2") else DEFAULT_ENGINE2).resolve()
    fastchess = Path(DEFAULT_FASTCHESS).resolve()
    book = Path(DEFAULT_BOOK).resolve()

    if not engine1.exists():
        print(f"Error: Engine 1 binary not found at {engine1}", file=sys.stderr)
        sys.exit(1)
    if not engine2.exists():
        print(f"Error: Engine 2 binary not found at {engine2}", file=sys.stderr)
        sys.exit(1)

    MATCHES_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pgn_path = Path(args.pgn) if args.pgn else MATCHES_DIR / f"gauntlet_60k_{timestamp}.pgn"

    rounds = args.games // 2  # 2 games per round (repeat swapped colors)

    eng1_args = [f"cmd={engine1}", "name=ChessAstra"]
    if args.net1:
        eng1_args.append(f"option.EvalFile={Path(args.net1).resolve()}")

    if args.tc.upper() in TC_PRESETS:
        tc_str = TC_PRESETS[args.tc.upper()]["tc"]
        hash_size = args.hash if args.hash != 16 else TC_PRESETS[args.tc.upper()]["hash"]
    else:
        tc_str = args.tc
        hash_size = args.hash

    cmd = [
        str(fastchess),
        "-engine", *eng1_args,
        "-engine", f"cmd={engine2}", "name=Stockfish-19-Official",
        "-each", f"tc={tc_str}", f"option.Hash={hash_size}", f"option.Threads={args.threads}",
        "-rounds", str(rounds),
        "-repeat",
        "-concurrency", str(args.concurrency),
        "-openings", f"file={book}", "format=epd", "order=random",
        "-draw", "movenumber=34", "movecount=8", "score=20",
        "-resign", "movecount=3", "score=600",
        "-report", "penta=true",
        "-ratinginterval", "20",
        "-autosaveinterval", str(args.batch_size),
        "-recover",
        "-pgnout", f"file={pgn_path}", "notation=san", "nodes=true",
    ]

    print("=" * 70)
    print("ChessAstra 60,000-Game Validation Gauntlet")
    print("=" * 70)
    print(f"Engine 1 (Dev)     : ChessAstra ({engine1})")
    print(f"Engine 2 (Base)    : Stockfish 19 Official ({engine2})")
    print(f"Target Games       : {args.games} ({rounds} pairs)")
    print(f"Time Control       : {args.tc}")
    print(f"Concurrency        : {args.concurrency} worker threads")
    print(f"Opening Suite      : {book.name}")
    print(f"PGN Destination    : {pgn_path}")
    print("=" * 70)
    sys.stdout.flush()

    try:
        proc = subprocess.run(cmd)
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        print("\n[!] Gauntlet paused by user. Progress saved to PGN.")
        sys.exit(0)

if __name__ == "__main__":
    main()
