<p align="center">
  <img src="assets/chessastra_banner.svg" alt="ChessAstra Banner" width="100%">
</p>

<p align="center">
  <a href="https://github.com/astra-foundation/ChessAstra/actions/workflows/ci.yml"><img src="https://img.shields.io/badge/CI-Passing-00F2FE?style=for-the-badge&logo=githubactions&logoColor=white" alt="CI Status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPLv3-7F00FF?style=for-the-badge&logo=gnu&logoColor=white" alt="License: GPLv3"></a>
  <a href="https://github.com/astra-foundation"><img src="https://img.shields.io/badge/Organization-astra--foundation-4FACFE?style=for-the-badge&logo=github&logoColor=white" alt="Organization: astra-foundation"></a>
  <a href="docs/NETWORKS.md"><img src="https://img.shields.io/badge/NNUE-SFNNv16-00F2FE?style=for-the-badge" alt="NNUE: SFNNv16"></a>
</p>

---

ChessAstra is a high-performance open-source UCI chess engine derivative of Stockfish, maintained under the [**Astra Foundation**](https://github.com/astra-foundation). It is designed to measurably outperform baseline Stockfish 19 through refined NNUE fine-tuning, automated data filtering pipelines, and specialized search heuristics.

> **Derivative Work Notice:**
> ChessAstra is a derivative work based on Stockfish and its NNUE networks, licensed under GPLv3.
> Forked from official Stockfish 19 release tag `sf_19` (commit `edb0d9db6731067ec50ce619ff372b463bc4dd5d`).
> All code, training pipelines, and networks remain free and open source under GNU General Public License v3.

---

## Key Features & Unique Capabilities

- **Komodo-Style Adaptive Personalities:** Configurable playing styles directly through UCI options (`Default`, `Aggressive`, `Attacking`, `Positional`, `Dynamic`, and `Beginner` handicap modes).
- **Asymmetric Contempt & Dynamic Aggression:** Adjustable `Contempt` (-100 to +100 cp) and `Aggressiveness` (0–300%) sliders to avoid draw-heavy lines and force sharp, uncompromising attacking play.
- **State-of-the-Art NNUE Architecture:** SFNNv16 neural evaluation (`HalfKAv2_hm` + `FullThreats` + `PP_3Wide`, `L1=1024`, `L2=32`, `L3=32`, 8 layer stacks) with weights baked directly into the binary via `INCBIN`.
- **Reproducible Data & Training Infrastructure:** Turnkey self-play generation (`generate_data.py`), dataset filtering/deduplication (`data_filter.py`), and Kaggle GPU remote fine-tuning automation (`run_kaggle.py`).
- **Comprehensive Testing Harness:** Integrated `fastchess` 60,000-game gauntlet runner, automated SPRT framework with pentanomial model statistics, and dual opening book suites (Lichess UHO + Stockfish UHO).
- **Cross-Platform & Universal SIMD Targets:** CI builds supporting Linux, Windows, and macOS (Apple Silicon / AVX-512 / VNNI / AVX2 / SSE4.1-POPCNT).

---

## Repository Structure

```
ChessAstra/
├── src/                # Engine source code in C++20
│   ├── Makefile        # High-performance multi-target build system
│   ├── nnue/           # NNUE neural network forward pass implementation
│   ├── syzygy/         # Syzygy endgame tablebase probing
│   └── ...
├── networks/           # Trained and quantized .nnue neural network files
├── training/           # NNUE training configs, datasets, and scripts
│   ├── config.yaml     # Fine-tuning hyperparameters & LR schedule
│   └── data_filter.py  # Self-play and tactical filtering pipeline
├── tests/              # SPRT testing framework, opening books, gauntlets
│   ├── books/          # Balanced 8-move UHO opening books (EPD/PGN)
│   ├── sprt/           # Fastchess SPRT runner & pentanomial analyzer
│   └── signature.sh    # Bench determinism test
├── docs/               # Research notes, training logs, match results
├── AUTHORS             # Authors and contributors
├── Copying.txt         # GNU General Public License v3
├── LICENSE             # GPLv3 License
└── NOTICE              # Legal and derivative notice
```

---

## Building ChessAstra

### Prerequisites
- Modern C++ compiler supporting C++20 (`g++ >= 11`, `clang++ >= 13`, or MSVC 2022)
- GNU Make

### Quick Build (Native CPU Optimization)
```bash
cd src
make -j ARCH=native build
```

### Profile-Guided Optimization (PGO) Build (Highest Performance)
```bash
cd src
make -j ARCH=x86-64-avx2 profile-build
```

### Specific Architecture Targets
- **AVX-512 with VNNI:** `make -j ARCH=x86-64-vnni512 build`
- **AVX-512:** `make -j ARCH=x86-64-avx512 build`
- **AVX-2 / BMI2:** `make -j ARCH=x86-64-avx2 build`
- **SSE4.1 / POPCNT:** `make -j ARCH=x86-64-sse41-popcnt build`
- **ARM64 / Apple Silicon:** `make -j ARCH=armv8-dotprod build` or `ARCH=apple-silicon`

---

## Benchmarking & Verification

Verify engine integrity and node parity using the built-in benchmark:
```bash
./src/chessastra bench
```

Run automated SPRT testing against baseline Stockfish:
```bash
python3 tests/sprt/run_sprt.py --engine1 ./src/chessastra --engine2 ./baseline/stockfish --tc 10+0.1 --book tests/books/UHO_Lichess_4852_v1.epd
```

---

## License & Attribution

ChessAstra is free software licensed under the **GNU General Public License version 3** (GPLv3).
See [`Copying.txt`](Copying.txt) or [`LICENSE`](LICENSE) for complete license terms.

Original Stockfish copyright: Copyright (C) 2004-2026 The Stockfish developers.
ChessAstra modifications copyright: Copyright (C) 2026 ChessAstra developers.
