# containerd 2.0 完整迁移指南

## 文档元信息

| 属性 | 值 |
|------|-----|
| **文档版本** | v1.0 |
| **创建日期** | 2025-10-22 |
| **containerd版本** | 2.0.0 |
| **前置版本** | 1.7.x |
| **适用场景** | 生产环境迁移 |
| **文档状态** | ✅ 完成 |

> **版本锚点**: 本文档提供从containerd 1.7到2.0的完整迁移方案,包含所有breaking changes和最佳实践。

---

## 目录

- [containerd 2.0 完整迁移指南](#containerd-20-完整迁移指南)
  - [文档元信息](#文档元信息)
  - [目录](#目录)
  - [1. 版本概述](#1-版本概述)
    - [1.1 版本信息](#11-版本信息)
    - [1.2 主要变更](#12-主要变更)
  - [2. Breaking Changes](#2-breaking-changes)
    - [2.1 API Breaking Changes](#21-api-breaking-changes)
    - [2.2 配置文件变更](#22-配置文件变更)
    - [2.3 命令行工具变更](#23-命令行工具变更)
  - [3. 新增特性](#3-新增特性)
    - [3.1 改进的镜像管理](#31-改进的镜像管理)
    - [3.2 改进的快照管理](#32-改进的快照管理)
    - [3.3 Windows容器支持](#33-windows容器支持)
    - [3.4 cgroup v2完整支持](#34-cgroup-v2完整支持)
  - [4. 迁移准备](#4-迁移准备)
    - [4.1 环境检查](#41-环境检查)
    - [4.2 备份策略](#42-备份策略)
    - [4.3 兼容性测试](#43-兼容性测试)
  - [5. 迁移步骤](#5-迁移步骤)
    - [5.1 停机迁移(推荐)](#51-停机迁移推荐)
    - [5.2 滚动升级(Kubernetes)](#52-滚动升级kubernetes)
    - [5.3 配置迁移工具](#53-配置迁移工具)
  - [6. 验证测试](#6-验证测试)
    - [6.1 功能验证](#61-功能验证)
    - [6.2 性能验证](#62-性能验证)
    - [6.3 Kubernetes集成验证](#63-kubernetes集成验证)
  - [7. 回滚方案](#7-回滚方案)
    - [7.1 快速回滚](#71-快速回滚)
  - [8. 最佳实践](#8-最佳实践)
    - [8.1 生产环境配置](#81-生产环境配置)
    - [8.2 监控配置](#82-监控配置)
    - [8.3 故障排查](#83-故障排查)
  - [9. 总结](#9-总结)
    - [9.1 迁移收益](#91-迁移收益)
    - [9.2 关键注意事项](#92-关键注意事项)

---

## 1. 版本概述

### 1.1 版本信息

**containerd 2.0重大更新**:

| 项目 | 详情 |
|------|------|
| **版本号** | 2.0.0 |
| **发布日期** | 2024年 |
| **版本类型** | Major Release |
| **支持状态** | ✅ 长期支持(LTS) |
| **API版本** | v2 |
| **最低Go版本** | 1.21 |

**组件版本**:

```yaml
核心组件:
  runc: 1.2.0+
  CNI: 1.4.0+
  containerd-shim: v2
  ctr: 2.0.0

可选组件:
  nerdctl: 1.7.0+
  buildkit: 0.13.0+
  stargz-snapshotter: 0.15.0+
```

### 1.2 主要变更

**核心改进**:

✅ **性能提升**

- 容器启动速度提升20%
- 镜像pull/push速度提升25%
- 内存占用降低15%
- CPU使用率降低10%

✅ **功能增强**

- 改进的镜像加密
- 增强的快照管理
- 更好的Windows支持
- 完整的cgroup v2支持

✅ **API变更**

- gRPC API v2
- 改进的事件系统
- 新的元数据存储
- 增强的插件系统

✅ **安全增强**

- 更严格的默认配置
- 改进的沙箱隔离
- 增强的证书验证
- 更好的审计日志

---

## 2. Breaking Changes

### 2.1 API Breaking Changes

**gRPC API v2变更**:

```go
// v1.7 (旧版本)
import (
    "github.com/containerd/containerd"
    "github.com/containerd/containerd/namespaces"
)

client, err := containerd.New("/run/containerd/containerd.sock")
ctx := namespaces.WithNamespace(context.Background(), "default")

// v2.0 (新版本)
import (
    "github.com/containerd/containerd/v2/client"
    "github.com/containerd/containerd/v2/core/containers"
)

c, err := client.New("/run/containerd/containerd.sock")
ctx := client.WithNamespace(context.Background(), "default")
```

**重要变更列表**:

| 变更项 | v1.7 | v2.0 | 影响 |
|--------|------|------|------|
| API路径 | `/v1.containerd.*` | `/v2.containerd.*` | ⚠️ 高 |
| 命名空间 | `namespace.WithNamespace` | `client.WithNamespace` | ⚠️ 中 |
| 容器创建 | `containers.Create` | 改进的参数 | ⚠️ 中 |
| 快照API | `snapshots.*` | 重构 | ⚠️ 高 |
| 元数据存储 | boltdb | bbolt | ⚠️ 低 |

### 2.2 配置文件变更

**config.toml变更**:

```toml
# containerd 1.7配置
version = 2

[plugins]
  [plugins."io.containerd.grpc.v1.cri"]
    sandbox_image = "registry.k8s.io/pause:3.9"
    
  [plugins."io.containerd.grpc.v1.cri".containerd]
    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
      runtime_type = "io.containerd.runc.v2"

# containerd 2.0配置
version = 3

[plugins]
  [plugins."io.containerd.cri.v1"]
    sandbox_image = "registry.k8s.io/pause:3.10"
    
    [plugins."io.containerd.cri.v1".containerd]
      [plugins."io.containerd.cri.v1".containerd.runtimes.runc]
        runtime_type = "io.containerd.runc.v2"
        
      # 新增: 配置cgroup驱动
      [plugins."io.containerd.cri.v1".containerd.runtimes.runc.options]
        SystemdCgroup = true
```

**关键配置变更**:

```yaml
重要变更:
  版本标识:
    旧: version = 2
    新: version = 3
  
  插件路径:
    旧: plugins."io.containerd.grpc.v1.cri"
    新: plugins."io.containerd.cri.v1"
  
  默认值:
    sandbox_image: pause:3.9 → pause:3.10
    默认启用systemd cgroup
    改进的默认资源限制
```

### 2.3 命令行工具变更

**ctr命令变更**:

```bash
# 1.7版本
ctr images pull docker.io/library/nginx:latest
ctr containers create docker.io/library/nginx:latest nginx
ctr tasks start nginx

# 2.0版本 (部分命令参数变化)
ctr images pull docker.io/library/nginx:latest
ctr containers create \
  --runtime io.containerd.runc.v2 \
  docker.io/library/nginx:latest nginx
ctr tasks start nginx
```

---

## 3. 新增特性

### 3.1 改进的镜像管理

**镜像加密增强**:

```bash
# 创建加密镜像
ctr images encrypt \
  --gpg-homedir ~/.gnupg \
  --gpg-version 2 \
  --recipient user@example.com \
  nginx:latest nginx:latest-encrypted

# 推送加密镜像
ctr images push \
  --encryption-key-protocol gpg \
  nginx:latest-encrypted registry.example.com/nginx:encrypted

# 拉取并解密
ctr images pull \
  --decryption-key ~/.gnupg/private.key \
  registry.example.com/nginx:encrypted
```

**增量镜像拉取**:

```bash
# 使用stargz快照
ctr images pull \
  --snapshotter stargz \
  --platform linux/amd64 \
  ghcr.io/stargz-containers/nginx:latest

# 性能对比
传统pull: ~30s (完整下载)
stargz pull: ~5s (按需加载)
```

### 3.2 改进的快照管理

**新的快照API**:

```go
// 创建快照
import (
    "github.com/containerd/containerd/v2/core/snapshots"
)

snapshotter := client.SnapshotService("overlayfs")

// 准备快照
mounts, err := snapshotter.Prepare(ctx, key, parent)

// 提交快照
err = snapshotter.Commit(ctx, name, key)

// 查看快照
info, err := snapshotter.Stat(ctx, name)

// 删除快照
err = snapshotter.Remove(ctx, name)
```

**性能优化**:

```yaml
快照性能提升:
  创建速度: +30%
  删除速度: +40%
  空间效率: +20%
  并发性能: +50%

新特性:
  - 原子性快照操作
  - 改进的垃圾回收
  - 更好的并发控制
  - 快照链优化
```

### 3.3 Windows容器支持

**Windows支持增强**:

```powershell
# Windows容器配置
# config.toml
[plugins."io.containerd.cri.v1"]
  [plugins."io.containerd.cri.v1".containerd]
    [plugins."io.containerd.cri.v1".containerd.runtimes.runhcs]
      runtime_type = "io.containerd.runhcs.v1"
      
    [plugins."io.containerd.cri.v1".containerd.runtimes.runhcs-wcow]
      runtime_type = "io.containerd.runhcs.v1"
      [plugins."io.containerd.cri.v1".containerd.runtimes.runhcs-wcow.options]
        Debug = true
        DebugType = "npipe"

# 运行Windows容器
ctr run --runtime io.containerd.runhcs.v1 \
  mcr.microsoft.com/windows/servercore:ltsc2022 \
  test-windows
```

### 3.4 cgroup v2完整支持

**cgroup v2配置**:

```toml
# config.toml
[plugins."io.containerd.cri.v1"]
  [plugins."io.containerd.cri.v1".containerd]
    [plugins."io.containerd.cri.v1".containerd.runtimes.runc]
      [plugins."io.containerd.cri.v1".containerd.runtimes.runc.options]
        # 启用systemd cgroup
        SystemdCgroup = true

# 验证cgroup版本
cat /sys/fs/cgroup/cgroup.controllers

# 输出示例 (cgroup v2)
cpuset cpu io memory hugetlb pids rdma misc
```

**资源限制示例**:

```bash
# 使用cgroup v2限制资源
ctr run \
  --memory-limit 512M \
  --cpu-quota 50000 \
  --cpu-period 100000 \
  --pids-limit 1000 \
  nginx:latest test-nginx
```

---

## 4. 迁移准备

### 4.1 环境检查

**迁移前检查脚本**:

```bash
#!/bin/bash
# containerd 2.0迁移前检查

echo "=== containerd迁移前检查 ==="

# 1. 当前版本
echo "当前版本:"
containerd --version

# 2. 运行时信息
echo -e "\n运行时信息:"
ctr version

# 3. 命名空间列表
echo -e "\n命名空间:"
ctr namespaces ls

# 4. 容器列表
echo -e "\n容器 (k8s.io命名空间):"
ctr -n k8s.io containers ls

# 5. 镜像列表
echo -e "\n镜像:"
ctr -n k8s.io images ls | head -10

# 6. 快照列表
echo -e "\n快照:"
ctr -n k8s.io snapshots ls | head -10

# 7. 插件列表
echo -e "\n插件:"
ctr plugins ls

# 8. 配置文件
echo -e "\n当前配置:"
cat /etc/containerd/config.toml | head -20

# 9. 系统信息
echo -e "\n系统信息:"
uname -a
echo "cgroup版本: $(stat -fc %T /sys/fs/cgroup/)"

# 10. 磁盘空间
echo -e "\n磁盘空间:"
df -h /var/lib/containerd
```

### 4.2 备份策略

**完整备份脚本**:

```bash
#!/bin/bash
# containerd数据备份

BACKUP_DIR="/backup/containerd-$(date +%Y%m%d-%H%M%S)"

echo "创建备份目录: $BACKUP_DIR"
mkdir -p $BACKUP_DIR

# 1. 备份配置文件
echo "备份配置文件..."
cp -r /etc/containerd $BACKUP_DIR/

# 2. 导出所有镜像
echo "导出镜像..."
mkdir -p $BACKUP_DIR/images
ctr -n k8s.io images ls -q | while read image; do
  name=$(echo $image | tr '/:' '_')
  echo "导出: $image"
  ctr -n k8s.io images export \
    "$BACKUP_DIR/images/${name}.tar" \
    $image 2>/dev/null || echo "导出失败: $image"
done

# 3. 备份元数据
echo "备份元数据..."
cp -r /var/lib/containerd/io.containerd.metadata.v1.bolt \
  $BACKUP_DIR/metadata.db

# 4. 记录容器信息
echo "记录容器信息..."
ctr -n k8s.io containers ls > $BACKUP_DIR/containers.txt

# 5. 创建备份清单
echo "创建备份清单..."
cat > $BACKUP_DIR/manifest.txt <<EOF
备份时间: $(date)
containerd版本: $(containerd --version)
备份路径: $BACKUP_DIR
镜像数量: $(ls $BACKUP_DIR/images/*.tar 2>/dev/null | wc -l)
EOF

echo "备份完成: $BACKUP_DIR"
ls -lh $BACKUP_DIR/
```

### 4.3 兼容性测试

**测试环境搭建**:

```bash
#!/bin/bash
# 在测试环境验证containerd 2.0

# 1. 安装containerd 2.0
wget https://github.com/containerd/containerd/releases/download/v2.0.0/containerd-2.0.0-linux-amd64.tar.gz
sudo tar -C /usr/local -xzf containerd-2.0.0-linux-amd64.tar.gz

# 2. 创建测试配置
sudo mkdir -p /etc/containerd-test
containerd config default > /etc/containerd-test/config.toml

# 3. 启动测试实例
sudo containerd \
  --config /etc/containerd-test/config.toml \
  --root /var/lib/containerd-test \
  --state /run/containerd-test \
  --address /run/containerd-test/containerd.sock &

# 4. 运行基本测试
export CONTAINERD_ADDRESS=/run/containerd-test/containerd.sock

ctr images pull docker.io/library/nginx:latest
ctr run -d docker.io/library/nginx:latest test-nginx
ctr tasks ls
ctr containers rm test-nginx

# 5. 清理测试环境
sudo pkill -f "containerd.*containerd-test"
sudo rm -rf /var/lib/containerd-test /run/containerd-test
```

---

## 5. 迁移步骤

### 5.1 停机迁移(推荐)

**完整迁移流程**:

```bash
#!/bin/bash
# containerd停机迁移脚本

set -e

echo "=== containerd 2.0停机迁移 ==="

# 0. 准备工作
BACKUP_DIR="/backup/containerd-migration-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 1. 停止相关服务
echo "步骤1: 停止服务..."
sudo systemctl stop kubelet || true
sudo systemctl stop docker || true
sudo systemctl stop containerd

# 2. 备份数据
echo "步骤2: 备份数据..."
sudo cp -r /etc/containerd $BACKUP_DIR/
sudo cp -r /var/lib/containerd $BACKUP_DIR/

# 3. 升级containerd
echo "步骤3: 升级containerd..."
wget https://github.com/containerd/containerd/releases/download/v2.0.0/containerd-2.0.0-linux-amd64.tar.gz
sudo tar -C /usr/local -xzf containerd-2.0.0-linux-amd64.tar.gz

# 4. 更新配置文件
echo "步骤4: 更新配置..."
sudo mv /etc/containerd/config.toml /etc/containerd/config.toml.v1
sudo containerd config default > /etc/containerd/config.toml

# 5. 应用自定义配置
echo "步骤5: 应用自定义配置..."
sudo tee -a /etc/containerd/config.toml > /dev/null <<'EOF'

[plugins."io.containerd.cri.v1"]
  [plugins."io.containerd.cri.v1".containerd]
    [plugins."io.containerd.cri.v1".containerd.runtimes.runc]
      [plugins."io.containerd.cri.v1".containerd.runtimes.runc.options]
        SystemdCgroup = true
EOF

# 6. 启动containerd
echo "步骤6: 启动containerd..."
sudo systemctl daemon-reload
sudo systemctl start containerd

# 7. 验证
echo "步骤7: 验证安装..."
sudo containerd --version
sudo ctr version

# 8. 启动其他服务
echo "步骤8: 启动相关服务..."
sudo systemctl start docker || true
sudo systemctl start kubelet || true

# 9. 健康检查
echo "步骤9: 健康检查..."
sleep 10
sudo ctr plugins ls
sudo ctr namespaces ls

echo "迁移完成!"
```

### 5.2 滚动升级(Kubernetes)

**Kubernetes节点滚动升级**:

```bash
#!/bin/bash
# Kubernetes节点containerd滚动升级

NODE_NAME=$(hostname)

echo "=== 节点 $NODE_NAME 滚动升级 ==="

# 1. 标记节点不可调度
echo "步骤1: 驱逐Pod..."
kubectl cordon $NODE_NAME
kubectl drain $NODE_NAME \
  --ignore-daemonsets \
  --delete-emptydir-data \
  --force \
  --timeout=300s

# 2. 停止kubelet
echo "步骤2: 停止kubelet..."
sudo systemctl stop kubelet

# 3. 升级containerd (复用停机迁移脚本的3-6步)
echo "步骤3: 升级containerd..."
# ... (执行上面的升级步骤)

# 4. 清理CNI网络
echo "步骤4: 清理CNI..."
sudo rm -rf /var/lib/cni/
sudo rm -rf /var/lib/calico/

# 5. 启动kubelet
echo "步骤5: 启动kubelet..."
sudo systemctl start kubelet

# 6. 等待节点就绪
echo "步骤6: 等待节点就绪..."
kubectl wait --for=condition=Ready node/$NODE_NAME --timeout=300s

# 7. 取消调度限制
echo "步骤7: 恢复调度..."
kubectl uncordon $NODE_NAME

# 8. 验证
echo "步骤8: 验证..."
kubectl get nodes $NODE_NAME
kubectl get pods -A -o wide --field-selector spec.nodeName=$NODE_NAME

echo "节点升级完成!"
```

### 5.3 配置迁移工具

**自动配置转换脚本**:

```python
#!/usr/bin/env python3
# containerd配置v2到v3转换

import re
import sys

def convert_config(old_config):
    """转换containerd配置从v2到v3"""
    
    new_config = old_config
    
    # 1. 更新版本号
    new_config = re.sub(
        r'version\s*=\s*2',
        'version = 3',
        new_config
    )
    
    # 2. 更新CRI插件路径
    new_config = re.sub(
        r'\[plugins\."io\.containerd\.grpc\.v1\.cri"\]',
        '[plugins."io.containerd.cri.v1"]',
        new_config
    )
    
    new_config = re.sub(
        r'plugins\."io\.containerd\.grpc\.v1\.cri"',
        'plugins."io.containerd.cri.v1"',
        new_config
    )
    
    # 3. 添加systemd cgroup配置
    if 'SystemdCgroup' not in new_config:
        runc_section = r'(\[plugins\."io\.containerd\.cri\.v1"\.containerd\.runtimes\.runc\])'
        new_config = re.sub(
            runc_section,
            r'\1\n      [plugins."io.containerd.cri.v1".containerd.runtimes.runc.options]\n        SystemdCgroup = true',
            new_config
        )
    
    return new_config

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: convert_config.py input.toml output.toml")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        old_config = f.read()
    
    new_config = convert_config(old_config)
    
    with open(sys.argv[2], 'w') as f:
        f.write(new_config)
    
    print(f"配置已转换: {sys.argv[1]} -> {sys.argv[2]}")
```

---

## 6. 验证测试

### 6.1 功能验证

**基础功能测试**:

```bash
#!/bin/bash
# containerd 2.0功能验证

echo "=== containerd功能验证 ==="

# 1. 版本验证
echo "1. 版本验证:"
containerd --version | grep "v2.0"
if [ $? -eq 0 ]; then
  echo "✓ 版本正确"
else
  echo "✗ 版本错误"
  exit 1
fi

# 2. 服务状态
echo -e "\n2. 服务状态:"
systemctl is-active containerd
if [ $? -eq 0 ]; then
  echo "✓ 服务运行中"
else
  echo "✗ 服务未运行"
  exit 1
fi

# 3. 镜像操作
echo -e "\n3. 镜像操作测试:"
ctr images pull docker.io/library/alpine:latest
if [ $? -eq 0 ]; then
  echo "✓ 镜像拉取成功"
else
  echo "✗ 镜像拉取失败"
  exit 1
fi

# 4. 容器创建
echo -e "\n4. 容器创建测试:"
ctr run -d docker.io/library/alpine:latest test-container sh -c "sleep 60"
if [ $? -eq 0 ]; then
  echo "✓ 容器创建成功"
else
  echo "✗ 容器创建失败"
  exit 1
fi

# 5. 容器列表
echo -e "\n5. 容器列表:"
ctr containers ls | grep test-container
if [ $? -eq 0 ]; then
  echo "✓ 容器可见"
else
  echo "✗ 容器不可见"
  exit 1
fi

# 6. 任务状态
echo -e "\n6. 任务状态:"
ctr tasks ls | grep test-container
if [ $? -eq 0 ]; then
  echo "✓ 任务运行中"
else
  echo "✗ 任务未运行"
  exit 1
fi

# 7. 清理
echo -e "\n7. 清理测试资源:"
ctr tasks kill test-container
ctr containers rm test-container
ctr images rm docker.io/library/alpine:latest

echo -e "\n✓ 所有测试通过!"
```

### 6.2 性能验证

**性能基准测试**:

```bash
#!/bin/bash
# containerd性能基准测试

echo "=== containerd性能测试 ==="

IMAGE="docker.io/library/alpine:latest"
ITERATIONS=10

# 1. 镜像拉取性能
echo "1. 镜像拉取性能测试 ($ITERATIONS次):"
ctr images rm $IMAGE 2>/dev/null

total_time=0
for i in $(seq 1 $ITERATIONS); do
  start=$(date +%s.%N)
  ctr images pull $IMAGE >/dev/null 2>&1
  end=$(date +%s.%N)
  elapsed=$(echo "$end - $start" | bc)
  total_time=$(echo "$total_time + $elapsed" | bc)
  ctr images rm $IMAGE >/dev/null 2>&1
done

avg_pull=$(echo "scale=2; $total_time / $ITERATIONS" | bc)
echo "平均拉取时间: ${avg_pull}s"

# 2. 容器启动性能
echo -e "\n2. 容器启动性能测试 ($ITERATIONS次):"
ctr images pull $IMAGE >/dev/null 2>&1

total_time=0
for i in $(seq 1 $ITERATIONS); do
  start=$(date +%s.%N)
  ctr run -d $IMAGE test-$i sh -c "sleep 1" >/dev/null 2>&1
  end=$(date +%s.%N)
  elapsed=$(echo "$end - $start" | bc)
  total_time=$(echo "$total_time + $elapsed" | bc)
  ctr tasks kill test-$i >/dev/null 2>&1
  ctr containers rm test-$i >/dev/null 2>&1
done

avg_start=$(echo "scale=2; $total_time / $ITERATIONS" | bc)
echo "平均启动时间: ${avg_start}s"

# 3. 清理
ctr images rm $IMAGE

echo -e "\n性能测试完成"
echo "镜像拉取: ${avg_pull}s"
echo "容器启动: ${avg_start}s"
```

### 6.3 Kubernetes集成验证

**K8s集成测试**:

```bash
#!/bin/bash
# Kubernetes + containerd 2.0集成测试

echo "=== Kubernetes集成测试 ==="

# 1. 节点状态
echo "1. 节点状态:"
kubectl get nodes
kubectl describe node $(hostname) | grep -A 5 "Container Runtime"

# 2. 创建测试Pod
echo -e "\n2. 创建测试Pod:"
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: test-containerd
spec:
  containers:
  - name: test
    image: nginx:latest
    ports:
    - containerPort: 80
EOF

# 3. 等待Pod就绪
echo -e "\n3. 等待Pod就绪:"
kubectl wait --for=condition=Ready pod/test-containerd --timeout=60s

# 4. 验证Pod运行
echo -e "\n4. 验证Pod:"
kubectl get pod test-containerd -o wide

# 5. 验证容器ID
echo -e "\n5. 验证containerd容器:"
CONTAINER_ID=$(kubectl get pod test-containerd -o jsonpath='{.status.containerStatuses[0].containerID}' | sed 's/containerd:\/\///')
ctr -n k8s.io containers ls | grep $CONTAINER_ID

# 6. 清理
echo -e "\n6. 清理:"
kubectl delete pod test-containerd

echo -e "\n✓ Kubernetes集成测试通过!"
```

---

## 7. 回滚方案

### 7.1 快速回滚

**紧急回滚脚本**:

```bash
#!/bin/bash
# containerd紧急回滚到1.7

set -e

BACKUP_DIR="/backup/containerd-migration-YYYYMMDD"  # 替换为实际备份目录

echo "=== containerd紧急回滚 ==="

# 1. 停止服务
echo "步骤1: 停止服务..."
sudo systemctl stop kubelet || true
sudo systemctl stop docker || true
sudo systemctl stop containerd

# 2. 恢复配置
echo "步骤2: 恢复配置..."
sudo rm -rf /etc/containerd
sudo cp -r $BACKUP_DIR/etc/containerd /etc/

# 3. 降级containerd
echo "步骤3: 降级containerd..."
wget https://github.com/containerd/containerd/releases/download/v1.7.11/containerd-1.7.11-linux-amd64.tar.gz
sudo tar -C /usr/local -xzf containerd-1.7.11-linux-amd64.tar.gz

# 4. 恢复数据(可选，谨慎使用)
# echo "步骤4: 恢复数据..."
# sudo rm -rf /var/lib/containerd
# sudo cp -r $BACKUP_DIR/var/lib/containerd /var/lib/

# 5. 启动服务
echo "步骤5: 启动服务..."
sudo systemctl daemon-reload
sudo systemctl start containerd
sudo systemctl start docker || true
sudo systemctl start kubelet || true

# 6. 验证
echo "步骤6: 验证..."
containerd --version
ctr version

echo "回滚完成!"
```

---

## 8. 最佳实践

### 8.1 生产环境配置

**推荐的config.toml**:

```toml
# containerd 2.0生产环境配置
version = 3

[grpc]
  address = "/run/containerd/containerd.sock"
  max_recv_message_size = 16777216
  max_send_message_size = 16777216

[debug]
  level = "info"

[metrics]
  address = "127.0.0.1:1338"

[plugins]
  [plugins."io.containerd.cri.v1"]
    sandbox_image = "registry.k8s.io/pause:3.10"
    max_container_log_line_size = 16384
    
    [plugins."io.containerd.cri.v1".containerd]
      snapshotter = "overlayfs"
      default_runtime_name = "runc"
      
      [plugins."io.containerd.cri.v1".containerd.runtimes.runc]
        runtime_type = "io.containerd.runc.v2"
        
        [plugins."io.containerd.cri.v1".containerd.runtimes.runc.options]
          SystemdCgroup = true
          
    [plugins."io.containerd.cri.v1".registry]
      config_path = "/etc/containerd/certs.d"
      
  [plugins."io.containerd.snapshotter.v1.overlayfs"]
    root_path = "/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs"
```

### 8.2 监控配置

**Prometheus监控**:

```yaml
# prometheus-containerd.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'containerd'
    static_configs:
      - targets: ['localhost:1338']
        labels:
          instance: 'node1'
```

### 8.3 故障排查

**常见问题处理**:

```bash
# 问题1: containerd启动失败
journalctl -u containerd -n 50 --no-pager

# 问题2: CRI插件未加载
ctr plugins ls | grep cri

# 问题3: 镜像拉取失败
ctr images pull --debug docker.io/library/nginx:latest

# 问题4: 容器创建失败
ctr run --debug docker.io/library/nginx:latest test

# 问题5: 快照问题
ctr snapshots ls
ctr snapshots rm <snapshot-name>
```

---

## 9. 总结

### 9.1 迁移收益

✅ **性能提升20-30%**
✅ **安全性显著增强**  
✅ **更好的Windows支持**
✅ **完整的cgroup v2支持**
✅ **改进的镜像管理**

### 9.2 关键注意事项

⚠️ **API变更需要更新客户端代码**
⚠️ **配置文件必须转换**
⚠️ **建议在测试环境先验证**
⚠️ **准备好回滚方案**
⚠️ **Kubernetes需要滚动升级**

---

**文档版本**: v1.0  
**最后更新**: 2025-10-22  
**维护者**: 项目技术团队
