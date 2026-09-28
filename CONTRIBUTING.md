# Contributing to ChessAstra

Welcome to the **ChessAstra** project by the [**Astra Foundation**](https://github.com/astra-foundation)! We are excited to collaborate with engine developers, machine learning practitioners, and chess enthusiasts.

---

## Table of Contents
- [Project Philosophy](#project-philosophy)
- [Building ChessAstra](#building-chessastra)
- [Validation & SPRT Testing](#validation--sprt-testing)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Code Style & Formatting](#code-style--formatting)
- [Licensing](#licensing)

---

## Project Philosophy

ChessAstra is dedicated to advancing open-source computer chess through:
1. **Measurable Strength Gains:** Every search or NNUE change must be backed by rigorous SPRT testing ($H_0: \text{Elo}=0, H_1: \text{Elo}=+3$) on balanced opening books (e.g., Lichess UHO suites).
2. **Reproducible Pipelines:** Self-play generation, dataset filtering, and neural training scripts must remain transparent and reproducible under GPLv3.
3. **Clean, Modern C++20:** High-efficiency, zero-overhead modern C++ code conforming to project standards.

---

## Building ChessAstra

### Prerequisites
- C++20 compliant compiler (`g++ >= 11`, `clang++ >= 13`, or MSVC 2022)
- GNU Make

### Quick Build Commands
```bash
cd src

# Download or verify the default NNUE network
make net

# Build native binary
make -j ARCH=native build

# High-performance Profile-Guided Optimization (PGO) build
make -j ARCH=x86-64-avx2 profile-build
```

---

## Validation & SPRT Testing

### Functional Changes & Heuristics
Any patch that alters move generation, search pruning (LMR, futility, razoring, history tables), or evaluation scaling must undergo automated SPRT testing:

```bash
# Run Short Time Control (STC 10+0.1) SPRT vs Baseline
python3 tests/sprt/run_sprt.py --tc STC --concurrency 10

# Run Long Time Control (LTC 60+0.6) SPRT vs Baseline
python3 tests/sprt/run_sprt.py --tc LTC --concurrency 10

# Run 60,000-game Validation Gauntlet
python3 tests/sprt/run_60k_gauntlet.py --games 60000 --tc STC --concurrency 10
```

### Bench Parity Check
Verify determinism and node count across test positions:
```bash
./src/chessastra bench
```

---

## Submitting Pull Requests

1. **Fork and Branch:** Create a feature branch (e.g., `feat/lmr-tune` or `net/v4-finetune`).
2. **Include Test Results:** In the PR description, provide:
   - The hypothesis behind the modification.
   - Benchmark node count output (`./src/chessastra bench`).
   - SPRT match results (Elo, error bars, pentanomial distribution, and games played).
3. **Authors File:** First-time contributors, please add your name and handle to [`AUTHORS`](./AUTHORS).

---

## Code Style & Formatting

ChessAstra strictly conforms to the `.clang-format` definition. Before committing:
```bash
cd src
make format
```

---

## Licensing

ChessAstra is a derivative work based on Stockfish and its NNUE networks, licensed under the **GNU General Public License version 3 (GPLv3)**.
By contributing, you agree that your code and trained networks are licensed under GPLv3.
See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE) for full terms.
