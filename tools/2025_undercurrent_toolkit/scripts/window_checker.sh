#!/bin/bash

# ===================================================================
# 抢跑窗口检查器
# ===================================================================

set -euo pipefail

# ============ 颜色 ============
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============ 计算剩余天数 ============
days_until() {
    local target_date=$1
    local current_date=$(date +%s)
    local target_timestamp=$(date -d "$target_date" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$target_date" "+%s")
    local diff=$(( (target_timestamp - current_date) / 86400 ))
    echo "$diff"
}

# ============ 状态图标 ============
status_icon() {
    local days=$1
    if [ "$days" -lt 0 ]; then
        echo "❌"
    elif [ "$days" -lt 30 ]; then
        echo "⚠️ "
    else
        echo "✅"
    fi
}

# ============ 主函数 ============
main() {
    echo ""
    echo "=========================================="
    echo "抢跑窗口检查"
    echo "=========================================="
    echo "当前日期: $(date +%Y-%m-%d)"
    echo ""
    
    # 关键截止日期
    local dates=(
        "2026-01-01:跨云签名生效日:⑦ 跨云签名"
        "2026-01-01:Docker Hub限速:③ Rootless"
        "2025-12-31:K8s 1.32 GA (预计):⑤ AI调度"
        "2026-06-30:标准冻结窗口:② 多运行时"
        "2026-03-31:WasmEdge 1.0 (预计):⑥ WASM GPU"
        "2026-06-30:边缘FPGA上市:⑧ 边缘FPGA"
    )
    
    echo "关键时间点:"
    echo ""
    
    local urgent_count=0
    
    for entry in "${dates[@]}"; do
        IFS=':' read -r date event action <<< "$entry"
        local days
        days=$(days_until "$date")
        local icon
        icon=$(status_icon "$days")
        
        echo -e "$icon $event ($action)"
        
        if [ "$days" -lt 0 ]; then
            echo -e "   ${RED}已过期 (${days#-}天前)${NC}"
        elif [ "$days" -lt 30 ]; then
            echo -e "   ${YELLOW}剩余 $days 天${NC}"
            ((urgent_count++))
        else
            echo -e "   ${GREEN}剩余 $days 天${NC}"
        fi
        echo ""
    done
    
    echo "=========================================="
    
    # 紧急行动提示
    if [ "$urgent_count" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  有 $urgent_count 个紧急时间点！${NC}"
        echo "请立即查看行动清单:"
        echo "  tools/2025_undercurrent_toolkit/checklist/2025_Q4_actions.md"
    else
        echo -e "${GREEN}✅ 时间窗口充足${NC}"
    fi
    
    echo "=========================================="
    echo ""
}

main

