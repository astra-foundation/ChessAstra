#!/usr/bin/env bash
# ChessAstra Opening Books Downloader
# Fetches balanced Lichess opening suites and official Stockfish opening books

set -euo pipefail

BOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "${BOOKS_DIR}"

BASE_URL="https://raw.githubusercontent.com/official-stockfish/books/master"

echo "======================================================"
echo "Downloading ChessAstra Opening Suites (Lichess + SF)"
echo "Target Directory: ${BOOKS_DIR}"
echo "======================================================"

download_zip() {
    local zipname="$1"
    local url="${BASE_URL}/${zipname}"

    echo "[*] Fetching ${zipname}..."
    if curl -sSL "${url}" -o "/tmp/${zipname}"; then
        unzip -o "/tmp/${zipname}" -d "${BOOKS_DIR}/" >/dev/null 2>&1 || true
        rm -f "/tmp/${zipname}"
        echo "[✓] Successfully downloaded: ${zipname}"
    else
        echo "[!] Failed downloading: ${zipname}"
    fi
}

# 1. Lichess Balanced UHO Suite
download_zip "UHO_Lichess_4852_v1.epd.zip"

# 2. Stockfish Standard & Unbalanced Suites
download_zip "UHO_4060_v3.epd.zip"
download_zip "UHO_4060_v4.epd.zip"
download_zip "noob_3moves.epd.zip"
download_zip "noob_4moves.epd.zip"
download_zip "8moves_v3.pgn.zip"
download_zip "8mvs_+90_+99.epd.zip"
download_zip "popularpos_lichess_v3.epd.zip"
download_zip "endgames.epd.zip"

echo "======================================================"
echo "Available Opening Suites in ${BOOKS_DIR}:"
ls -lh "${BOOKS_DIR}"
echo "======================================================"
