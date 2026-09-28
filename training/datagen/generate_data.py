#!/usr/bin/env python3
"""
ChessAstra Self-Play & Endgame Data Generator.
Generates high-quality position records (FEN + Search Eval + WDL Outcome)
with randomized search limits and balanced opening books.
"""

import argparse
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

DEFAULT_ENGINE = Path(__file__).resolve().parent.parent.parent / "src" / "chessastra"
DEFAULT_FASTCHESS = Path(__file__).resolve().parent.parent.parent / "tests" / "bin" / "fastchess"
DEFAULT_BOOK = Path(__file__).resolve().parent.parent.parent / "tests" / "books" / "UHO_Lichess_4852_v1.epd"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def parse_args():
    parser = argparse.ArgumentParser(description="Generate training self-play data for ChessAstra")
    parser.add_argument("--engine", type=str, default=str(DEFAULT_ENGINE), help="Engine binary path")
    parser.add_argument("--book", type=str, default=str(DEFAULT_BOOK), help="Opening book (.epd)")
    parser.add_argument("--fastchess", type=str, default=str(DEFAULT_FASTCHESS), help="fastchess binary")
    parser.add_argument("--rounds", type=int, default=500, help="Number of game pairs (rounds)")
    parser.add_argument("--concurrency", type=int, default=max(1, (os.cpu_count() or 4) - 2), help="Concurrency")
    parser.add_argument("--nodes-min", type=int, default=8000, help="Min nodes per move")
    parser.add_argument("--nodes-max", type=int, default=35000, help="Max nodes per move")
    parser.add_argument("--output", type=str, default=None, help="Output plain text data file")
    return parser.parse_args()

def run_selfplay_batch(engine: Path, book: Path, fastchess: Path, rounds: int, concurrency: int,
                       nodes: int, pgn_out: Path) -> bool:
    """Run a batch of self-play games using fastchess with node limit and PGN export."""
    cmd = [
        str(fastchess),
        "-engine", f"cmd={engine}", "name=ChessAstraA", f"nodes={nodes}",
        "-engine", f"cmd={engine}", "name=ChessAstraB", f"nodes={nodes}",
        "-each", "tc=inf", "option.Hash=16", "option.Threads=1",
        "-rounds", str(rounds),
        "-repeat",
        "-concurrency", str(concurrency),
        "-openings", f"file={book}", "format=epd", "order=random",
        "-draw", "movenumber=34", "movecount=8", "score=20",
        "-resign", "movecount=3", "score=600",
        "-pgnout", f"file={pgn_out}", "notation=san", "nodes=true", "seldepth=true",
    ]
    print(f"[*] Starting batch: {rounds*2} games @ {nodes} nodes/move (concurrency={concurrency})...")
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    return res.returncode == 0

def parse_pgn_to_positions(pgn_path: Path) -> List[Tuple[str, int, float]]:
    """
    Parses PGN comments containing eval and move numbers to extract
    (FEN, eval_cp, wdl_score).
    """
    import chess
    import chess.pgn

    records = []
    if not pgn_path.exists():
        return records

    with open(pgn_path, "r", encoding="utf-8", errors="replace") as f:
        while True:
            try:
                game = chess.pgn.read_game(f)
            except Exception:
                break
            if game is None:
                break

            result_str = game.headers.get("Result", "*")
            if result_str == "1-0":
                result = 1.0
            elif result_str == "0-1":
                result = 0.0
            elif result_str == "1/2-1/2":
                result = 0.5
            else:
                continue

            board = game.board()
            ply = 0
            for node in game.mainline():
                move = node.move
                # Skip opening book moves (first 8 plies)
                if ply >= 8 and not board.is_check():
                    comment = node.comment
                    # Extract eval e.g. eval=+0.23 or eval=-1.45 or score cp
                    eval_cp = None
                    m = re.search(r"eval=([+-]?\d+\.?\d*)", comment)
                    if m:
                        try:
                            eval_cp = int(float(m.group(1)) * 100)
                        except ValueError:
                            pass
                    else:
                        m2 = re.search(r"([+-]?\d+\.?\d*)/", comment)
                        if m2:
                            try:
                                eval_cp = int(float(m2.group(1)) * 100)
                            except ValueError:
                                pass

                    if eval_cp is not None and abs(eval_cp) < 2000:
                        # Normalize eval relative to side to move
                        fen = board.fen()
                        # wdl score for side to move
                        side_result = result if board.turn == chess.WHITE else (1.0 - result)
                        records.append((fen, eval_cp, side_result))

                board.push(move)
                ply += 1

    return records

def main():
    args = parse_args()
    engine_path = Path(args.engine).resolve()
    fastchess_path = Path(args.fastchess).resolve()
    book_path = Path(args.book).resolve()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    pgn_file = DATA_DIR / f"selfplay_{timestamp}.pgn"
    out_file = Path(args.output).resolve() if args.output else DATA_DIR / f"dataset_{timestamp}.plain"

    # Split rounds across 3 node levels for variety
    rounds_per_batch = max(10, args.rounds // 3)
    node_levels = [args.nodes_min, (args.nodes_min + args.nodes_max) // 2, args.nodes_max]

    for nodes in node_levels:
        run_selfplay_batch(
            engine=engine_path,
            book=book_path,
            fastchess=fastchess_path,
            rounds=rounds_per_batch,
            concurrency=args.concurrency,
            nodes=nodes,
            pgn_out=pgn_file,
        )

    print(f"[*] Parsing PGN results from {pgn_file}...")
    positions = parse_pgn_to_positions(pgn_file)
    print(f"[+] Extracted {len(positions)} raw training positions.")

    with open(out_file, "w", encoding="utf-8") as out:
        for fen, score, wdl in positions:
            out.write(f"{fen} | {score} | {wdl:.2f}\n")

    print(f"[✓] Saved training dataset to {out_file}")

if __name__ == "__main__":
    main()
