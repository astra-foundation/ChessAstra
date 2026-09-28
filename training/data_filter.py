#!/usr/bin/env python3
"""
ChessAstra Dataset Filtering & Clean-up Pipeline.
Filters noisy, in-check, tactical-in-flight, and duplicate positions.
Prepares clean datasets for NNUE training.
"""

import argparse
import sys
from pathlib import Path
from typing import Set

import chess

def parse_args():
    parser = argparse.ArgumentParser(description="Filter and clean ChessAstra training datasets")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input raw .plain dataset file")
    parser.add_argument("--train-out", type=str, default="training/data/train.plain", help="Clean train output")
    parser.add_argument("--val-out", type=str, default="training/data/val.plain", help="Clean val output")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Validation split ratio")
    parser.add_argument("--max-eval", type=int, default=1500, help="Max absolute eval cp cutoff")
    return parser.parse_args()

def is_valid_quiet_position(board: chess.Board, eval_cp: int) -> bool:
    """Check if position is clean, non-tactical, and suitable for NNUE static evaluation."""
    # 1. King in check is rejected
    if board.is_check():
        return False

    # 2. Extreme eval (overwhelming tactical blowout or impending mate)
    if abs(eval_cp) > 1500:
        return False

    # 3. Game over state (stalemate / checkmate)
    if board.is_game_over():
        return False

    # 4. Check if the position has sufficient piece material (at least 3 pieces)
    if len(board.piece_map()) < 3:
        return False

    return True

def get_canonical_fen(fen: str) -> str:
    """Return FEN without halfmove clock and fullmove number for deduplication."""
    parts = fen.strip().split()
    if len(parts) >= 4:
        return " ".join(parts[:4])
    return fen.strip()

def main():
    args = parse_args()
    input_path = Path(args.input).resolve()

    if not input_path.exists():
        print(f"Error: Input file {input_path} not found.", file=sys.stderr)
        sys.exit(1)

    train_path = Path(args.train_out).resolve()
    val_path = Path(args.val_out).resolve()
    train_path.parent.mkdir(parents=True, exist_ok=True)
    val_path.parent.mkdir(parents=True, exist_ok=True)

    seen_fens: Set[str] = set()
    valid_records = []

    total_lines = 0
    filtered_checks = 0
    filtered_eval = 0
    filtered_dups = 0

    print(f"[*] Processing dataset from {input_path}...")

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "|" not in line:
                continue
            total_lines += 1

            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 3:
                continue

            fen, score_str, wdl_str = parts[0], parts[1], parts[2]
            try:
                score_cp = int(float(score_str))
                wdl = float(wdl_str)
            except ValueError:
                continue

            # Check deduplication
            canon_fen = get_canonical_fen(fen)
            if canon_fen in seen_fens:
                filtered_dups += 1
                continue

            try:
                board = chess.Board(fen)
            except ValueError:
                continue

            if board.is_check():
                filtered_checks += 1
                continue

            if not is_valid_quiet_position(board, score_cp):
                filtered_eval += 1
                continue

            seen_fens.add(canon_fen)
            valid_records.append((fen, score_cp, wdl))

    print(f"[+] Total read: {total_lines}")
    print(f"[-] Filtered duplicates: {filtered_dups}")
    print(f"[-] Filtered in-check: {filtered_checks}")
    print(f"[-] Filtered extreme eval / tactical: {filtered_eval}")
    print(f"[✓] Retained high-quality positions: {len(valid_records)}")

    # Split into train and val
    val_count = int(len(valid_records) * args.val_ratio)
    train_count = len(valid_records) - val_count

    train_data = valid_records[:train_count]
    val_data = valid_records[train_count:]

    with open(train_path, "w", encoding="utf-8") as f_train:
        for fen, score, wdl in train_data:
            f_train.write(f"{fen} | {score} | {wdl:.4f}\n")

    with open(val_path, "w", encoding="utf-8") as f_val:
        for fen, score, wdl in val_data:
            f_val.write(f"{fen} | {score} | {wdl:.4f}\n")

    print(f"[✓] Train dataset ({len(train_data)} positions) -> {train_path}")
    print(f"[✓] Validation dataset ({len(val_data)} positions) -> {val_path}")

if __name__ == "__main__":
    main()
