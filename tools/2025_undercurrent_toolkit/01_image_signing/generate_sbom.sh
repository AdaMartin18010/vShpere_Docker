#!/bin/bash

# ===================================================================
# SBOM生成脚本
# ===================================================================

set -euo pipefail

IMAGE=$1
FORMAT=${2:-spdx}  # spdx or cyclonedx

if [ "$FORMAT" = "spdx" ]; then
    syft "$IMAGE" -o spdx-json
else
    syft "$IMAGE" -o cyclonedx-json
fi

