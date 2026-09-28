# ChessAstra NNUE Progression & Gauntlet Tracker

This table tracks every neural network iteration for ChessAstra, including architecture version, training dataset, validation loss, and SPRT Elo results against the baseline Stockfish 19 network (`nn-1a298aa575a0.nnue`).

---

## Network Progression Table

| Net ID | Network Name | Base Architecture | Training Dataset | STC Elo (vs SF19) | LTC Elo (vs SF19) | SPRT Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **v0** | `nn-1a298aa575a0.nnue` | SFNNv16 (L1=1024) | Upstream SF19 Release Data | `+0.0` (Reference) | `+0.0` (Reference) | **Baseline** | Official Stockfish 19 release net |
| **v1** | `chessastra-v1.nnue` | SFNNv16 (L1=1024) | Filtered Self-Play V1 (3.8k pos) | `-34.8 +/- 43.7` | Pending | Completed | Initial test run |
| **v2** | `chessastra-v2.nnue` | SFNNv16 (L1=1024) | Filtered Self-Play V2 (5.3k pos) | `-23.2 +/- 72.2` | Pending | Completed | Improved draw ratio & tactical stability |
| **v3** | `chessastra-v3.nnue` | SFNNv16 (L1=1024) | Filtered Master V3 (10.2k pos) | `+52.5 +/- 56.1` | Pending | **Promising** | **LOS 96.99%**, W:12 L:6 D:22 (57.5%), PairsRatio: 3.50 |

---

## Evaluation Benchmark Suite

Network integrity is validated across the 8 standard reference positions:
1. Standard Start (`rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`)
2. Italian Game (`r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4`)
3. Berlin Defense (`r1bqkb1r/pppp1ppp/2n5/1B2p3/4n3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 1 5`)
4. Najdorf Sicilian (`rnbqkb1r/1p2pppp/p2p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6`)
5. Tactical Middlegame (`r1b2rk1/2q1bppp/p2pp3/1p2n1P1/3NP3/2N1BP2/PPP4P/2KR1Q1R w - - 1 15`)
6. Heavy Piece Endgame (`4r1k1/5ppp/8/8/8/8/4qPPP/4R1K1 w - - 0 1`)
7. Pawn Endgame (`8/5k2/8/4P3/8/8/5K2/8 w - - 0 1`)
8. Lucena Rook Endgame (`1K1k4/1P6/8/8/8/8/r7/2R5 w - - 0 1`)
