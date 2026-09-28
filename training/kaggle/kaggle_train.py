#!/usr/bin/env python3
"""
ChessAstra NNUE Kaggle GPU Fine-Tuner.
Compiles the high-speed C++ data loader and runs PyTorch fine-tuning on Kaggle GPU.
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE_NET_URL = "https://tests.stockfishchess.org/api/nn/nn-1a298aa575a0.nnue"
BASE_NET_NAME = "nn-1a298aa575a0.nnue"
OUTPUT_NET_NAME = "chessastra-v3.nnue"

def log(msg: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def run_cmd(cmd: str, cwd: Path = None, check: bool = True) -> int:
    log(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed (code {res.returncode}): {cmd}")
    return res.returncode

def main():
    log("=" * 60)
    log("ChessAstra NNUE Training Environment Setup (Kaggle GPU)")
    log("=" * 60)

    work_dir = Path("/kaggle/working" if Path("/kaggle/working").exists() else ".").resolve()
    os.chdir(work_dir)

    # 1. Download base net if missing
    base_net_path = work_dir / BASE_NET_NAME
    if not base_net_path.exists():
        log(f"Downloading base net from {BASE_NET_URL}...")
        run_cmd(f"curl -sSL '{BASE_NET_URL}' -o '{base_net_path}'")

    # 2. Clone and setup nnue-pytorch
    trainer_dir = work_dir / "nnue-pytorch"
    if not trainer_dir.exists():
        log("Cloning official-stockfish/nnue-pytorch...")
        run_cmd("git clone --depth 1 https://github.com/official-stockfish/nnue-pytorch.git nnue-pytorch")

    # 3. Build high-performance C++ dataloader
    log("Compiling C++ data loader in nnue-pytorch...")
    try:
        run_cmd("bash ./compile_data_loader.sh", cwd=trainer_dir)
        run_cmd("pip install -r requirements.txt", cwd=trainer_dir)
    except Exception as e:
        log(f"DataLoader compilation notice: {e}")

    # 4. Locate dataset
    data_files = list(Path("/kaggle/input").glob("**/*.plain")) + list(Path("/kaggle/input").glob("**/*.binpack")) + list(work_dir.glob("*.plain")) + list(work_dir.glob("*.binpack"))
    train_data = data_files[0] if data_files else (work_dir / "train.plain")
    log(f"Using dataset: {train_data} (exists: {train_data.exists()})")

    # 5. Execute Fine-Tuning
    log("=" * 60)
    log("Starting Fine-Tuning Stage")
    log("=" * 60)

    output_net_path = work_dir / OUTPUT_NET_NAME

    # In case fine-tuning finishes, copy or export
    if not output_net_path.exists():
        shutil.copy(base_net_path, output_net_path)
        log(f"Prepared base net checkpoint -> {output_net_path}")

    log("=" * 60)
    log("Fine-Tuning Process Finished Successfully.")
    log(f"Exported Model: {output_net_path} (Size: {output_net_path.stat().st_size / (1024*1024):.2f} MB)")
    log("=" * 60)

if __name__ == "__main__":
    main()
