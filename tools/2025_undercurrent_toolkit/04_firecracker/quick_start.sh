#!/bin/bash

# ===================================================================
# Firecracker MicroVM 快速启动脚本
# ===================================================================
# 功能: 125ms冷启动 + Container支持
# 成本: ¥18/月
# 窗口期: 2025 Q4 - 2026 Q2
# ===================================================================

set -euo pipefail

# ============ 配置 ============
IMAGE="${IMAGE:-alpine:latest}"
MEMORY="${MEMORY:-512}"  # MB
VCPUS="${VCPUS:-2}"
ROOTFS="${ROOTFS:-rootfs.ext4}"
KERNEL="${KERNEL:-vmlinux.bin}"

# ============ 颜色 ============
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============ 日志 ============
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

# ============ 下载Firecracker ============
download_firecracker() {
    if [ -f "./firecracker" ]; then
        log_info "Firecracker已存在"
        return 0
    fi
    
    log_info "下载Firecracker v1.8.0..."
    wget -q https://github.com/firecracker-microvm/firecracker/releases/download/v1.8.0/firecracker-v1.8.0-x86_64.tgz
    tar xzf firecracker-v1.8.0-x86_64.tgz
    chmod +x firecracker
    rm firecracker-v1.8.0-x86_64.tgz
    log_success "Firecracker下载完成"
}

# ============ 下载内核 ============
download_kernel() {
    if [ -f "$KERNEL" ]; then
        log_info "内核已存在"
        return 0
    fi
    
    log_info "下载MicroVM内核..."
    wget -q https://s3.amazonaws.com/spec.ccfc.min/img/quickstart_guide/x86_64/kernels/vmlinux.bin
    log_success "内核下载完成"
}

# ============ 创建rootfs ============
create_rootfs() {
    if [ -f "$ROOTFS" ]; then
        log_info "Rootfs已存在"
        return 0
    fi
    
    log_info "创建rootfs from Docker image: $IMAGE"
    
    # 导出Docker镜像为tar
    local container_id
    container_id=$(docker create "$IMAGE")
    docker export "$container_id" > rootfs.tar
    docker rm "$container_id" > /dev/null
    
    # 创建ext4文件系统
    dd if=/dev/zero of="$ROOTFS" bs=1M count=512
    mkfs.ext4 "$ROOTFS"
    
    # 挂载并解压
    local mount_point="/tmp/firecracker_rootfs_$$"
    mkdir -p "$mount_point"
    sudo mount "$ROOTFS" "$mount_point"
    sudo tar xf rootfs.tar -C "$mount_point"
    sudo umount "$mount_point"
    rmdir "$mount_point"
    rm rootfs.tar
    
    log_success "Rootfs创建完成"
}

# ============ 生成配置 ============
generate_config() {
    log_info "生成MicroVM配置..."
    
    cat > vm_config.json <<EOF
{
  "boot-source": {
    "kernel_image_path": "$KERNEL",
    "boot_args": "console=ttyS0 reboot=k panic=1 pci=off"
  },
  "drives": [{
    "drive_id": "rootfs",
    "path_on_host": "$ROOTFS",
    "is_root_device": true,
    "is_read_only": false
  }],
  "machine-config": {
    "vcpu_count": $VCPUS,
    "mem_size_mib": $MEMORY,
    "ht_enabled": false
  },
  "network-interfaces": [{
    "iface_id": "eth0",
    "guest_mac": "AA:FC:00:00:00:01",
    "host_dev_name": "tap0"
  }]
}
EOF
    
    log_success "配置生成完成: vm_config.json"
}

# ============ 启动MicroVM ============
start_microvm() {
    log_info "启动MicroVM..."
    
    # 设置网络
    sudo ip tuntap add tap0 mode tap
    sudo ip addr add 172.16.0.1/24 dev tap0
    sudo ip link set tap0 up
    
    # 启动Firecracker
    rm -f /tmp/firecracker.sock
    ./firecracker --api-sock /tmp/firecracker.sock --config-file vm_config.json &
    local firecracker_pid=$!
    
    log_success "MicroVM启动完成 (PID: $firecracker_pid)"
    
    echo ""
    echo "=========================================="
    echo "✅ Firecracker MicroVM运行中"
    echo "=========================================="
    echo "内存: ${MEMORY}MB"
    echo "vCPUs: $VCPUS"
    echo "镜像: $IMAGE"
    echo "=========================================="
    echo ""
    echo "管理命令:"
    echo "  查看状态: curl --unix-socket /tmp/firecracker.sock http://localhost/machine-config"
    echo "  停止VM: kill $firecracker_pid"
    echo "=========================================="
    
    # 等待用户停止
    wait $firecracker_pid
}

# ============ 主函数 ============
main() {
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --image)
                IMAGE="$2"
                shift 2
                ;;
            --memory)
                MEMORY="$2"
                shift 2
                ;;
            --vcpus)
                VCPUS="$2"
                shift 2
                ;;
            *)
                echo "未知选项: $1"
                exit 1
                ;;
        esac
    done
    
    echo "=========================================="
    echo "Firecracker MicroVM 快速启动"
    echo "=========================================="
    echo "目标: 125ms冷启动"
    echo "成本: ¥18/月"
    echo "=========================================="
    echo ""
    
    download_firecracker
    download_kernel
    create_rootfs
    generate_config
    start_microvm
}

main "$@"

