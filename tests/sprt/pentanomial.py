"""
Pentanomial SPRT and Elo statistics calculator for ChessAstra.
Calculates Pentanomial distribution, Normalized Elo (nElo), Logistic Elo,
Log-Likelihood Ratio (LLR), and SPRT stopping conditions.
"""

import math
from typing import Dict, List, Tuple

class PentanomialSPRT:
    def __init__(self, elo0: float = 0.0, elo1: float = 3.0, alpha: float = 0.05, beta: float = 0.05):
        self.elo0 = elo0
        self.elo1 = elo1
        self.alpha = alpha
        self.beta = beta
        self.lower_bound = math.log(beta / (1.0 - alpha))
        self.upper_bound = math.log((1.0 - beta) / alpha)

    @staticmethod
    def elo_to_score(elo: float) -> float:
        """Convert logistic Elo difference to expected score."""
        return 1.0 / (1.0 + 10.0 ** (-elo / 400.0))

    @staticmethod
    def score_to_elo(score: float) -> float:
        """Convert score (0..1) to Elo difference."""
        if score <= 0.0:
            return -float("inf")
        if score >= 1.0:
            return float("inf")
        return -400.0 * math.log10(1.0 / score - 1.0)

    @staticmethod
    def calculate_stats(penta: List[int]) -> Dict[str, float]:
        """
        Calculate statistics from pentanomial counts [LL, LD, DD/WL, WD, WW]
        corresponding to game-pair scores: [0.0, 0.5, 1.0, 1.5, 2.0] / 2
        """
        assert len(penta) == 5
        N = sum(penta)
        if N == 0:
            return {"pairs": 0, "games": 0, "score": 0.5, "nelo": 0.0, "penta": penta}

        # Value per outcome (0, 0.25, 0.5, 0.75, 1.0)
        weights = [0.0, 0.25, 0.5, 0.75, 1.0]
        score_sum = sum(p * w for p, w in zip(penta, weights))
        mu = score_sum / N

        # Variance
        variance = sum(p * ((w - mu) ** 2) for p, w in zip(penta, weights)) / N
        stdev = math.sqrt(variance / N) if variance > 0 else 0.0

        # Normalized Elo (nElo) = (mu - 0.5) / (sqrt(2 * variance)) * (800 / ln(10))
        nelo_scale = 800.0 / math.log(10.0)
        nelo = (mu - 0.5) / math.sqrt(2.0 * variance) * nelo_scale if variance > 0 else 0.0
        nelo_error = (stdev / math.sqrt(2.0 * variance)) * nelo_scale if variance > 0 else 0.0

        # Logistic Elo
        elo = PentanomialSPRT.score_to_elo(mu)
        elo_lower = PentanomialSPRT.score_to_elo(max(1e-6, mu - 1.96 * stdev))
        elo_upper = PentanomialSPRT.score_to_elo(min(1.0 - 1e-6, mu + 1.96 * stdev))

        return {
            "pairs": N,
            "games": N * 2,
            "score": mu,
            "variance": variance,
            "stdev": stdev,
            "nelo": nelo,
            "nelo_error": 1.96 * nelo_error,
            "elo": elo,
            "elo_95_ci": (elo_lower, elo_upper),
            "penta": penta,
        }
