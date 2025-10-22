#!/bin/bash

# ===================================================================
# 签名验证脚本
# ===================================================================

set -euo pipefail

COSIGN_PUB="${COSIGN_PUB:-cosign.pub}"

echo "========================================"
echo "验证镜像签名"
echo "========================================"

for image in "$@"; do
    echo ""
    echo "验证: $image"
    if cosign verify --key "$COSIGN_PUB" "$image"; then
        echo "✅ 签名有效"
    else
        echo "❌ 签名无效或未签名"
    fi
done

