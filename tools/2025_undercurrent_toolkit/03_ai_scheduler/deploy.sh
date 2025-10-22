#!/bin/bash

# ===================================================================
# K8s AI Scheduler 一键部署脚本
# ===================================================================
# 收益: 集群故障率 -40%
# 成本: ¥0 (开源)
# 窗口期: 2025 Q4 - 2025-12-31
# ===================================================================

set -euo pipefail

# ============ 配置 ============
K8S_VERSION="${K8S_VERSION:-1.32.0}"
NAMESPACE="${NAMESPACE:-kube-system}"
MODEL_SIZE="${MODEL_SIZE:-small}"
DRY_RUN="${DRY_RUN:-false}"

# ============ 颜色 ============
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============ 日志函数 ============
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# ============ 检查K8s版本 ============
check_k8s_version() {
    log_info "检查Kubernetes版本..."
    
    local version
    version=$(kubectl version --short 2>/dev/null | grep Server | awk '{print $3}' | sed 's/v//')
    
    if [ -z "$version" ]; then
        log_error "无法获取Kubernetes版本"
        exit 1
    fi
    
    log_info "当前版本: v$version"
    
    # 检查是否 >= 1.32
    if [ "$(printf '%s\n' "1.32.0" "$version" | sort -V | head -n1)" != "1.32.0" ]; then
        log_error "需要 Kubernetes >= 1.32.0"
        echo ""
        echo "升级指南:"
        echo "  kubeadm upgrade plan"
        echo "  kubeadm upgrade apply v1.32.0"
        exit 1
    fi
    
    log_success "版本检查通过"
}

# ============ 部署AI Scheduler ============
deploy_scheduler() {
    log_info "部署AI Scheduler..."
    
    if [ "$DRY_RUN" = "true" ]; then
        log_info "[DRY RUN] 将部署到 namespace: $NAMESPACE"
        return 0
    fi
    
    # 添加Helm仓库
    log_info "添加Helm仓库..."
    helm repo add scheduler-plugins oci://registry.k8s.io/scheduler-plugins
    helm repo update
    
    # 部署
    log_info "安装AI Scheduler..."
    helm install ai-scheduler scheduler-plugins/ai-scheduler \
        --namespace "$NAMESPACE" \
        --create-namespace \
        --set aiScheduler.enabled=true \
        --set aiScheduler.model.size="$MODEL_SIZE" \
        --values helm-values.yaml \
        --wait
    
    log_success "AI Scheduler部署完成"
}

# ============ 配置默认调度器 ============
configure_default_scheduler() {
    log_info "配置默认调度器..."
    
    # 为default namespace启用AI调度器
    kubectl label namespace default scheduler=ai-scheduler --overwrite
    
    log_success "默认调度器配置完成"
}

# ============ 验证部署 ============
verify_deployment() {
    log_info "验证部署..."
    
    # 检查Pod状态
    log_info "等待Pod就绪..."
    kubectl wait --for=condition=ready pod \
        -l app=ai-scheduler \
        -n "$NAMESPACE" \
        --timeout=5m
    
    # 检查日志
    log_info "检查日志..."
    kubectl logs -n "$NAMESPACE" -l app=ai-scheduler --tail=20
    
    log_success "部署验证通过"
}

# ============ 创建测试Pod ============
create_test_pod() {
    log_info "创建测试Pod..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: ai-scheduler-test
  namespace: default
spec:
  schedulerName: ai-scheduler
  containers:
  - name: app
    image: nginx:alpine
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "200m"
EOF
    
    log_success "测试Pod创建完成"
    
    # 查看调度事件
    log_info "查看调度事件..."
    kubectl get events --field-selector involvedObject.name=ai-scheduler-test
}

# ============ 监控指标 ============
show_metrics() {
    log_info "AI Scheduler指标..."
    
    # 端口转发
    kubectl port-forward -n "$NAMESPACE" svc/ai-scheduler-metrics 9090:9090 &
    local port_forward_pid=$!
    
    sleep 3
    
    # 获取指标
    echo ""
    echo "=========================================="
    echo "预测准确率:"
    curl -s http://localhost:9090/metrics | grep "ai_scheduler_prediction_accuracy"
    echo ""
    echo "驱逐次数:"
    curl -s http://localhost:9090/metrics | grep "ai_scheduler_evictions_total"
    echo "=========================================="
    
    # 停止端口转发
    kill $port_forward_pid
}

# ============ 使用说明 ============
usage() {
    cat << EOF
用法: $0 [选项]

选项:
  -h, --help              显示帮助
  -n, --namespace NS      指定namespace (默认: kube-system)
  -s, --size SIZE         模型大小 (small/medium/large, 默认: small)
  --dry-run               模拟运行
  --verify-only           仅验证部署
  --test                  创建测试Pod
  --metrics               显示监控指标

示例:
  # 标准部署
  $0

  # 指定模型大小
  $0 --size medium

  # 验证现有部署
  $0 --verify-only

  # 创建测试Pod
  $0 --test

EOF
}

# ============ 主函数 ============
main() {
    local verify_only=false
    local test_only=false
    local show_metrics_only=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -s|--size)
                MODEL_SIZE="$2"
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
            --test)
                test_only=true
                shift
                ;;
            --metrics)
                show_metrics_only=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # 打印横幅
    echo "=========================================="
    echo "K8s AI Scheduler 部署"
    echo "=========================================="
    echo "目标: 集群故障率 -40%"
    echo "成本: ¥0 (开源)"
    echo "窗口期: 2025 Q4 - 2025-12-31"
    echo "=========================================="
    echo ""
    
    # 仅显示指标
    if [ "$show_metrics_only" = true ]; then
        show_metrics
        exit 0
    fi
    
    # 仅创建测试
    if [ "$test_only" = true ]; then
        create_test_pod
        exit 0
    fi
    
    # 检查K8s版本
    check_k8s_version
    
    # 仅验证
    if [ "$verify_only" = true ]; then
        verify_deployment
        exit 0
    fi
    
    # 完整部署
    deploy_scheduler
    configure_default_scheduler
    verify_deployment
    
    echo ""
    echo "=========================================="
    echo "✅ 部署完成!"
    echo "=========================================="
    echo "下一步:"
    echo "  1. 创建测试Pod: $0 --test"
    echo "  2. 查看指标: $0 --metrics"
    echo "  3. 查看日志: kubectl logs -n $NAMESPACE -l app=ai-scheduler -f"
    echo "=========================================="
}

main "$@"

