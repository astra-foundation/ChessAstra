#!/usr/bin/env python3
"""
ChessAstra 60,000-Game Live Monitor Dashboard.
Parses live gauntlet log and PGN to display real-time statistics,
win rates, Elo progression, and pentanomial distribution.
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path

PGN_FILE = Path(__file__).resolve().parent / "matches" / "gauntlet_60000_games.pgn"
LOG_FILE = Path(__file__).resolve().parent / "matches" / "gauntlet_60k.log"

def get_process_status():
    res = subprocess.run("ps aux | grep fastchess | grep -v grep", shell=True, stdout=subprocess.PIPE, text=True)
    return bool(res.stdout.strip())

def main():
    if not LOG_FILE.exists():
        print("Gauntlet log file not found. Run run_60k_gauntlet.py first.")
        return

    is_running = get_process_status()
    pgn_size = PGN_FILE.stat().st_size / 1024 if PGN_FILE.exists() else 0

    # Count games in PGN
    games_count = 0
    if PGN_FILE.exists():
        with open(PGN_FILE, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("[Event "):
                    games_count += 1

    # Extract latest stats block
    latest_stats = "No rating block reported yet."
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
        stats_lines = []
        capture = False
        for line in lines:
            if "Results of ChessAstra" in line:
                stats_lines = [line]
                capture = True
            elif capture:
                stats_lines.append(line)
                if "--------------------------------------------------" in line:
                    capture = False
        if stats_lines:
            latest_stats = "".join(stats_lines).strip()

    print("=" * 70)
    print(" ♚ CHESSASTRA 60,000-GAME GAUNTLET LIVE STATUS")
    print("=" * 70)
    print(f"Status           : {'🟢 RUNNING (10 threads)' if is_running else '🔴 STOPPED'}")
    print(f"Target Games     : 60,000")
    print(f"Completed Games  : {games_count:,} ({games_count/600:.2f}% of 60k)")
    print(f"PGN File         : {PGN_FILE}")
    print(f"PGN File Size    : {pgn_size:.2f} KB")
    print("-" * 70)
    print("Latest Pentanomial / Rating Update:")
    print(latest_stats)
    print("=" * 70)

if __name__ == "__main__":
    main()
