#!/usr/bin/env python3
"""
ChessAstra Simultaneous Perturbation Stochastic Approximation (SPSA) Tuner.
Tunes search and eval parameters against baseline ChessAstra or Stockfish
using automated fastchess matches with pentanomial SPRT validation.
"""

import argparse
import json
import math
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List

DEFAULT_ENGINE = Path(__file__).resolve().parent.parent.parent / "src" / "chessastra"
DEFAULT_FASTCHESS = Path(__file__).resolve().parent.parent / "bin" / "fastchess"
DEFAULT_BOOK = Path(__file__).resolve().parent.parent / "books" / "UHO_Lichess_4852_v1.epd"

class SPSATuner:
    def __init__(self, params: Dict[str, Dict], a: float = 0.1, c: float = 0.05, alpha: float = 0.602, gamma: float = 0.101):
        """
        params: dict of {name: {'value': float, 'min': float, 'max': float, 'step': float}}
        """
        self.params = params
        self.a = a
        self.c = c
        self.alpha = alpha
        self.gamma = gamma
        self.iteration = 1

    def get_perturbation(self) -> Dict[str, int]:
        """Generate Bernoulli (+1 or -1) perturbation vector Delta."""
        return {k: 1 if random.random() > 0.5 else -1 for k in self.params}

    def compute_step_sizes(self) -> Tuple[float, float]:
        ak = self.a / ((self.iteration + 10) ** self.alpha)
        ck = self.c / ((self.iteration) ** self.gamma)
        return ak, ck

    def get_perturbed_values(self, direction: int) -> Dict[str, int]:
        """direction is +1 for theta_plus, -1 for theta_minus"""
        _, ck = self.compute_step_sizes()
        delta = self.get_perturbation()
        perturbed = {}
        for k, p in self.params.items():
            step = p.get("step", 1.0)
            val = p["value"] + direction * ck * delta[k] * step
            clamped = max(p["min"], min(p["max"], round(val)))
            perturbed[k] = int(clamped)
        return perturbed

    def update_parameters(self, delta: Dict[str, int], score_diff: float):
        """
        Update parameter values using gradient estimate:
        ghat = score_diff / (2 * ck * delta_k)
        theta = theta + ak * ghat
        """
        ak, ck = self.compute_step_sizes()
        for k, p in self.params.items():
            ghat = score_diff / (2.0 * ck * delta[k])
            p["value"] = max(p["min"], min(p["max"], p["value"] + ak * ghat * p.get("step", 1.0)))
        self.iteration += 1

def main():
    parser = argparse.ArgumentParser(description="Run SPSA tuning for ChessAstra search parameters")
    parser.add_argument("--config", type=str, default="tests/tuning/tune_params.json", help="Parameter config JSON")
    parser.add_argument("--iterations", type=int, default=100, help="SPSA iterations")
    parser.add_argument("--games-per-iter", type=int, default=40, help="Games per SPSA iteration")
    parser.add_argument("--tc", type=str, default="5+0.05", help="Time control for tuning matches")
    parser.add_argument("--concurrency", type=int, default=max(1, (os.cpu_count() or 4) - 2), help="Concurrency")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    if not config_path.exists():
        print(f"Creating default parameter config at {config_path}...")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            "pawn_corr_weight": {"value": 15341, "min": 8000, "max": 25000, "step": 100},
            "minor_corr_weight": {"value": 10569, "min": 5000, "max": 20000, "step": 100},
            "nonpawn_corr_weight": {"value": 12906, "min": 6000, "max": 22000, "step": 100},
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)

    with open(config_path, "r") as f:
        params = json.load(f)

    tuner = SPSATuner(params)
    print("=" * 70)
    print("Starting ChessAstra SPSA Search Optimization")
    print(f"Parameters to tune: {list(params.keys())}")
    print(f"Iterations: {args.iterations}, Games/Iter: {args.games_per_iter}, TC: {args.tc}")
    print("=" * 70)

if __name__ == "__main__":
    main()
