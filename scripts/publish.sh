#!/usr/bin/env bash
# ChessAstra Release Packaging and GitHub Publisher
# Astra Foundation (https://github.com/astra-foundation/ChessAstra)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${REPO_ROOT}/dist"
VERSION="${1:-v1.0.0}"
TAG_NAME="${VERSION}"
TARGET_REPO="astra-foundation/ChessAstra"

echo "======================================================"
echo "Publishing ChessAstra Release: ${VERSION}"
echo "Target: ${TARGET_REPO}"
echo "======================================================"

mkdir -p "${DIST_DIR}"
rm -rf "${DIST_DIR}/*"

# 1. Compile Optimized Binary
echo "[*] Compiling optimized ChessAstra binary..."
cd "${REPO_ROOT}/src"
make -j"$(nproc)" ARCH=x86-64-avx2 COMP=gcc build

# 2. Package Binary Release
echo "[*] Packaging release tarballs..."
cp "${REPO_ROOT}/src/chessastra" "${DIST_DIR}/chessastra-linux-x86-64-avx2"
cp "${REPO_ROOT}/networks/chessastra-v3.nnue" "${DIST_DIR}/chessastra-v3.nnue"
cp "${REPO_ROOT}/LICENSE" "${DIST_DIR}/"
cp "${REPO_ROOT}/NOTICE" "${DIST_DIR}/"
cp "${REPO_ROOT}/README.md" "${DIST_DIR}/"

cd "${DIST_DIR}"
tar -czvf "chessastra-${VERSION}-linux-x86-64-avx2.tar.gz" \
    chessastra-linux-x86-64-avx2 chessastra-v3.nnue LICENSE NOTICE README.md

# 3. Generate SHA256 Checksums
echo "[*] Generating SHA256 checksums..."
sha256sum "chessastra-${VERSION}-linux-x86-64-avx2.tar.gz" "chessastra-v3.nnue" > "SHA256SUMS.txt"
cat "SHA256SUMS.txt"

echo "======================================================"
echo "[✓] Release artifacts prepared in ${DIST_DIR}:"
ls -lh "${DIST_DIR}"
echo "======================================================"

# 4. Publish via GitHub CLI (if authenticated and repo exists)
if command -v gh >/dev/null 2>&1; then
    echo "[*] Checking GitHub CLI credentials..."
    if gh auth status >/dev/null 2>&1; then
        echo "[*] Publishing release ${TAG_NAME} to GitHub..."
        gh release create "${TAG_NAME}" \
            "chessastra-${VERSION}-linux-x86-64-avx2.tar.gz" \
            "chessastra-v3.nnue" \
            "SHA256SUMS.txt" \
            --repo "${TARGET_REPO}" \
            --title "ChessAstra ${VERSION} Release" \
            --notes "Official release of ChessAstra ${VERSION} by Astra Foundation. Derivative work of Stockfish 19 under GPLv3. Features fine-tuned SFNNv16 NNUE network chessastra-v3.nnue with verified gains on Lichess UHO suite." \
            || echo "[!] Notice: GitHub release push requires write permissions on ${TARGET_REPO}."
    else
        echo "[!] GitHub CLI is not logged in. Run 'gh auth login' to publish automatically."
    fi
fi

echo "[✓] Release packaging complete."
