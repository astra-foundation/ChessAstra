#!/usr/bin/env python3
"""
ChessAstra Kaggle Remote Trainer Orchestrator.
Uses Kaggle CLI to trigger GPU training sessions, monitor progress,
and automatically retrieve trained .nnue model weights.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

KAGGLE_DIR = Path(__file__).resolve().parent
NETWORKS_DIR = Path(__file__).resolve().parent.parent.parent / "networks"
KERNEL_SLUG = "hemeshchesskas/chessastra-nnue-trainer"

def run_cmd(cmd: str) -> Tuple[int, str]:
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return res.returncode, res.stdout

def push_kernel():
    print(f"[*] Pushing Kaggle GPU Kernel from {KAGGLE_DIR}...")
    code, out = run_cmd(f"kaggle kernels push -p {KAGGLE_DIR}")
    print(out)
    if code != 0:
        print("[!] Error pushing kernel to Kaggle.", file=sys.stderr)
        return False
    return True

def monitor_kernel(poll_interval: int = 30):
    print(f"[*] Monitoring kernel status for {KERNEL_SLUG}...")
    while True:
        code, out = run_cmd(f"kaggle kernels status {KERNEL_SLUG}")
        print(f"[{time.strftime('%H:%M:%S')}] {out.strip()}")
        if "complete" in out.lower():
            print("[✓] Kaggle GPU training finished successfully!")
            return True
        elif "error" in out.lower() or "cancel" in out.lower():
            print(f"[!] Kernel failed or canceled:\n{out}", file=sys.stderr)
            return False
        time.sleep(poll_interval)

def download_output():
    NETWORKS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[*] Downloading output artifacts to {NETWORKS_DIR}...")
    code, out = run_cmd(f"kaggle kernels output {KERNEL_SLUG} -p {NETWORKS_DIR}")
    print(out)
    return code == 0

def main():
    parser = argparse.ArgumentParser(description="Manage Kaggle GPU NNUE training for ChessAstra")
    parser.add_argument("--push", action="store_true", help="Push kernel and start training")
    parser.add_argument("--status", action="store_true", help="Check current kernel status")
    parser.add_argument("--download", action="store_true", help="Download output model")
    parser.add_argument("--all", action="store_true", help="Push, monitor, and download in one run")
    args = parser.parse_args()

    if args.all or args.push:
        if not push_kernel():
            sys.exit(1)

    if args.all or (not args.status and not args.download and not args.push):
        if not monitor_kernel():
            sys.exit(1)
        download_output()
    elif args.status:
        code, out = run_cmd(f"kaggle kernels status {KERNEL_SLUG}")
        print(out)
    elif args.download:
        download_output()

if __name__ == "__main__":
    main()
