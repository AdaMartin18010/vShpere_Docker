#!/bin/bash

# ===================================================================
# 2025技术暗流 - 镜像签名自动化脚本
# ===================================================================
# 功能: 自动签名Docker镜像 + 生成SBOM
# 收益: ¥600/年 (2026起免跨云流量费)
# 窗口期: 2025 Q4 - 2026-01-01
# ===================================================================

set -euo pipefail

# ============ 配置 ============
COSIGN_KEY="${COSIGN_KEY:-cosign.key}"
COSIGN_PUB="${COSIGN_PUB:-cosign.pub}"
SBOM_FORMAT="${SBOM_FORMAT:-spdx}"  # spdx or cyclonedx
REGISTRY="${REGISTRY:-}"
DRY_RUN="${DRY_RUN:-false}"

# ============ 颜色 ============
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============ 日志函数 ============
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# ============ 检查依赖 ============
check_dependencies() {
    log_info "检查依赖工具..."
    
    local missing_deps=()
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v cosign &> /dev/null; then
        missing_deps+=("cosign")
    fi
    
    if ! command -v syft &> /dev/null; then
        missing_deps+=("syft")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "缺少依赖: ${missing_deps[*]}"
        echo ""
        echo "安装指南:"
        echo "  cosign: curl -LO https://github.com/sigstore/cosign/releases/download/v2.2.0/cosign-linux-amd64"
        echo "  syft:   curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# ============ 生成密钥对 ============
generate_keypair() {
    if [ ! -f "$COSIGN_KEY" ]; then
        log_info "生成cosign密钥对..."
        cosign generate-key-pair
        log_success "密钥对已生成: $COSIGN_KEY, $COSIGN_PUB"
    else
        log_info "使用现有密钥: $COSIGN_KEY"
    fi
}

# ============ 生成SBOM ============
generate_sbom() {
    local image=$1
    local sbom_file="${image//\//_}_sbom.json"
    
    log_info "生成SBOM: $image"
    
    if [ "$SBOM_FORMAT" = "spdx" ]; then
        syft "$image" -o spdx-json > "$sbom_file"
    else
        syft "$image" -o cyclonedx-json > "$sbom_file"
    fi
    
    log_success "SBOM已生成: $sbom_file"
    echo "$sbom_file"
}

# ============ 签名镜像 ============
sign_image() {
    local image=$1
    local sbom_file=$2
    
    log_info "签名镜像: $image"
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warn "[DRY RUN] 将签名: $image"
        return 0
    fi
    
    # 签名镜像 + 附加SBOM
    cosign sign --key "$COSIGN_KEY" \
        --attachment sbom \
        --sbom "$sbom_file" \
        "$image" \
        --yes
    
    log_success "签名完成: $image"
}

# ============ 验证签名 ============
verify_signature() {
    local image=$1
    
    log_info "验证签名: $image"
    
    if cosign verify --key "$COSIGN_PUB" "$image" &> /dev/null; then
        log_success "签名验证成功: $image"
        return 0
    else
        log_error "签名验证失败: $image"
        return 1
    fi
}

# ============ 处理单个镜像 ============
process_image() {
    local image=$1
    
    echo ""
    echo "=========================================="
    echo "处理镜像: $image"
    echo "=========================================="
    
    # 1. 拉取镜像
    log_info "拉取镜像..."
    if ! docker pull "$image"; then
        log_error "拉取失败: $image"
        return 1
    fi
    
    # 2. 生成SBOM
    local sbom_file
    sbom_file=$(generate_sbom "$image")
    
    # 3. 签名
    sign_image "$image" "$sbom_file"
    
    # 4. 验证
    verify_signature "$image"
    
    # 5. 清理临时文件
    rm -f "$sbom_file"
    
    log_success "处理完成: $image"
}

# ============ 批量处理 ============
process_all_images() {
    local registry=$1
    
    log_info "扫描仓库: $registry"
    
    # 获取所有镜像 (需要registry API或docker命令)
    local images
    images=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "$registry" || true)
    
    if [ -z "$images" ]; then
        log_warn "未找到镜像: $registry"
        return 0
    fi
    
    local total=0
    local success=0
    local failed=0
    
    while IFS= read -r image; do
        ((total++))
        if process_image "$image"; then
            ((success++))
        else
            ((failed++))
        fi
    done <<< "$images"
    
    echo ""
    echo "=========================================="
    echo "批量处理完成"
    echo "=========================================="
    echo "总计: $total"
    echo "成功: $success"
    echo "失败: $failed"
    echo "=========================================="
}

# ============ 统计信息 ============
print_stats() {
    echo ""
    echo "=========================================="
    echo "抢跑收益统计"
    echo "=========================================="
    echo "✅ 签名镜像数: $1"
    echo "✅ 预计年收益: ¥600 (免跨云流量费)"
    echo "✅ 窗口期剩余: $(days_until 2026-01-01)天"
    echo "=========================================="
}

# ============ 计算剩余天数 ============
days_until() {
    local target_date=$1
    local current_date=$(date +%s)
    local target_timestamp=$(date -d "$target_date" +%s)
    local diff=$(( (target_timestamp - current_date) / 86400 ))
    echo "$diff"
}

# ============ 使用说明 ============
usage() {
    cat << EOF
用法: $0 [选项] [镜像...]

选项:
  -h, --help              显示帮助
  -a, --all               批量处理所有镜像
  -r, --registry REGISTRY 指定仓库
  -k, --key KEY           指定cosign私钥 (默认: cosign.key)
  -f, --format FORMAT     SBOM格式 (spdx/cyclonedx, 默认: spdx)
  --dry-run               模拟运行，不实际签名
  --verify-only           仅验证签名

示例:
  # 签名单个镜像
  $0 myapp:v1.0

  # 批量签名
  $0 --all --registry myregistry.io

  # 验证签名
  $0 --verify-only myapp:v1.0

  # 模拟运行
  $0 --dry-run myapp:v1.0

环境变量:
  COSIGN_KEY      cosign私钥路径
  COSIGN_PUB      cosign公钥路径
  SBOM_FORMAT     SBOM格式 (spdx/cyclonedx)
  REGISTRY        仓库地址
  DRY_RUN         模拟运行 (true/false)

EOF
}

# ============ 主函数 ============
main() {
    local images=()
    local batch_mode=false
    local verify_only=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -a|--all)
                batch_mode=true
                shift
                ;;
            -r|--registry)
                REGISTRY="$2"
                shift 2
                ;;
            -k|--key)
                COSIGN_KEY="$2"
                COSIGN_PUB="${2}.pub"
                shift 2
                ;;
            -f|--format)
                SBOM_FORMAT="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verify-only)
                verify_only=true
                shift
                ;;
            *)
                images+=("$1")
                shift
                ;;
        esac
    done
    
    # 打印横幅
    echo "=========================================="
    echo "2025技术暗流 - 镜像签名自动化"
    echo "=========================================="
    echo "目标: 免跨云流量费 ¥600/年"
    echo "窗口期: 2025 Q4 - 2026-01-01"
    echo "=========================================="
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 仅验证模式
    if [ "$verify_only" = true ]; then
        for image in "${images[@]}"; do
            verify_signature "$image"
        done
        exit 0
    fi
    
    # 生成密钥对
    generate_keypair
    
    # 批量模式
    if [ "$batch_mode" = true ]; then
        if [ -z "$REGISTRY" ]; then
            log_error "批量模式需要指定 --registry"
            exit 1
        fi
        process_all_images "$REGISTRY"
        exit 0
    fi
    
    # 处理指定镜像
    if [ ${#images[@]} -eq 0 ]; then
        log_error "请指定镜像或使用 --all"
        usage
        exit 1
    fi
    
    local signed_count=0
    for image in "${images[@]}"; do
        if process_image "$image"; then
            ((signed_count++))
        fi
    done
    
    # 打印统计
    print_stats "$signed_count"
}

main "$@"

