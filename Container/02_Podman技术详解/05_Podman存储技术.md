# Podman存储技术

> 版本锚点（新增）：本文档基于 Podman 5.0+ 和 containers/storage 1.51+ 版本编写，版本信息统一参考《2025年技术标准最终对齐报告.md》。

## 目录

- [Podman存储技术](#podman存储技术)
  - [目录](#目录)
  - [1. containers/storage 驱动](#1-containersstorage-驱动)
    - [1.1 存储驱动概述](#11-存储驱动概述)
    - [1.2 overlay2 驱动](#12-overlay2-驱动)
    - [1.3 btrfs 驱动](#13-btrfs-驱动)
    - [1.4 zfs 驱动](#14-zfs-驱动)
    - [1.5 vfs 驱动](#15-vfs-驱动)
    - [1.6 存储驱动选择](#16-存储驱动选择)
  - [2. 数据卷与绑定挂载](#2-数据卷与绑定挂载)
    - [2.1 数据卷管理](#21-数据卷管理)
    - [2.2 绑定挂载](#22-绑定挂载)
    - [2.3 SELinux 标签](#23-selinux-标签)
    - [2.4 tmpfs 挂载](#24-tmpfs-挂载)
    - [2.5 挂载选项](#25-挂载选项)
  - [3. 性能与一致性](#3-性能与一致性)
    - [3.1 文件系统语义](#31-文件系统语义)
    - [3.2 IO 限制](#32-io-限制)
    - [3.3 Cgroups 集成](#33-cgroups-集成)
    - [3.4 性能调优](#34-性能调优)
  - [4. 备份与迁移](#4-备份与迁移)
    - [4.1 卷备份](#41-卷备份)
    - [4.2 镜像备份](#42-镜像备份)
    - [4.3 离线迁移](#43-离线迁移)
    - [4.4 在线迁移](#44-在线迁移)
  - [5. 故障与恢复](#5-故障与恢复)
    - [5.1 权限问题](#51-权限问题)
    - [5.2 层损坏恢复](#52-层损坏恢复)
    - [5.3 空间清理](#53-空间清理)
  - [6. 实操示例](#6-实操示例)
    - [6.1 卷管理示例](#61-卷管理示例)
    - [6.2 数据备份示例](#62-数据备份示例)
    - [6.3 存储迁移示例](#63-存储迁移示例)
  - [7. 故障清单与排查](#7-故障清单与排查)
  - [8. FAQ](#8-faq)
  - [9. 基线模板（建议）](#9-基线模板建议)

## 1. containers/storage 驱动

### 1.1 存储驱动概述

Podman 使用 `containers/storage` 库管理镜像和容器的存储，支持多种存储驱动。

**支持的存储驱动**：

| 驱动 | 成熟度 | 性能 | 特性 | 推荐场景 |
|------|--------|------|------|----------|
| **overlay2** | 稳定 | 高 | 写时复制，节省空间 | **生产环境推荐** |
| **btrfs** | 稳定 | 高 | 快照，压缩 | Btrfs 文件系统 |
| **zfs** | 稳定 | 高 | 快照，压缩，去重 | ZFS 文件系统 |
| **vfs** | 简单 | 低 | 完全复制，兼容性好 | 测试/兼容性 |

**查看当前存储驱动**：

```bash
# 查看存储信息
podman info | grep -A 10 "store:"

# 输出示例
store:
  graphDriverName: overlay
  graphRoot: /var/lib/containers/storage
  imageStore:
    number: 15
  runRoot: /run/containers/storage

# 查看详细的存储配置
podman info --format json | jq '.store'
```

**存储配置文件**：

```bash
# 系统级配置
/etc/containers/storage.conf

# 用户级配置（rootless）
$HOME/.config/containers/storage.conf

# 查看配置
cat /etc/containers/storage.conf
```

**示例配置文件**：

```toml
# /etc/containers/storage.conf
[storage]
# 存储驱动
driver = "overlay"

# 存储根目录
graphroot = "/var/lib/containers/storage"

# 运行时目录
runroot = "/run/containers/storage"

# 存储选项
[storage.options]
# overlay 特定选项
mountopt = "nodev"
size = "120G"

# 忽略 chown 错误
ignore_chown_errors = "false"

# 自动 userns UID/GID 映射
auto_userns_min_size = 1024
auto_userns_max_size = 65536
```

### 1.2 overlay2 驱动

Overlay2 是最推荐的存储驱动，提供良好的性能和空间效率。

**特点**：

- ✅ **写时复制（CoW）**：节省磁盘空间
- ✅ **高性能**：接近原生文件系统性能
- ✅ **内核支持好**：Linux 4.0+
- ✅ **节省 inode**：不会耗尽 inode
- ❌ **限制**：需要 ext4/xfs 底层文件系统

**配置 overlay2**：

```toml
# /etc/containers/storage.conf
[storage]
driver = "overlay"

[storage.options]
# 挂载选项
mountopt = "nodev"

# 忽略chown错误（rootless模式可能需要）
ignore_chown_errors = "true"

# overlay 层数限制（默认128）
mount_program = "/usr/bin/fuse-overlayfs"

[storage.options.overlay]
# 使用 native overlay（而不是 fuse-overlayfs）
# force_mask = "0000"
```

**overlay2 目录结构**：

```bash
# 存储根目录
/var/lib/containers/storage/
├── overlay/              # 层数据
│   ├── <layer-id>/
│   │   ├── diff/        # 层内容
│   │   ├── link         # 短链接名
│   │   └── work/        # 工作目录
├── overlay-images/       # 镜像元数据
│   └── images.json
├── overlay-layers/       # 层元数据
│   └── layers.json
└── overlay-containers/   # 容器元数据
    └── containers.json

# rootless 存储位置
$HOME/.local/share/containers/storage/
```

**检查 overlay 支持**：

```bash
# 检查内核版本
uname -r

# 检查 overlay 模块
lsmod | grep overlay

# 检查文件系统
df -T /var/lib/containers/storage

# 测试 overlay 挂载
mkdir -p /tmp/overlay-test/{lower,upper,work,merged}
mount -t overlay overlay \
  -o lowerdir=/tmp/overlay-test/lower,upperdir=/tmp/overlay-test/upper,workdir=/tmp/overlay-test/work \
  /tmp/overlay-test/merged
umount /tmp/overlay-test/merged
```

**fuse-overlayfs（rootless 替代方案）**：

```bash
# 安装 fuse-overlayfs
sudo dnf install fuse-overlayfs  # Fedora/RHEL
sudo apt-get install fuse-overlayfs  # Ubuntu/Debian

# rootless 配置自动使用 fuse-overlayfs
# ~/.config/containers/storage.conf
[storage]
driver = "overlay"

[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"
```

### 1.3 btrfs 驱动

Btrfs 驱动利用 Btrfs 文件系统的高级特性。

**特点**：

- ✅ **快照支持**：原生快照功能
- ✅ **压缩**：自动数据压缩
- ✅ **写时复制**：高效的 CoW
- ✅ **去重**：数据去重
- ❌ **限制**：需要 Btrfs 文件系统

**配置 btrfs**：

```bash
# 创建 Btrfs 文件系统
sudo mkfs.btrfs /dev/sdb1
sudo mount /dev/sdb1 /var/lib/containers/storage

# 配置
# /etc/containers/storage.conf
[storage]
driver = "btrfs"
graphroot = "/var/lib/containers/storage"
```

**btrfs 特性**：

```bash
# 启用压缩
sudo mount -o remount,compress=zstd /var/lib/containers/storage

# 查看 Btrfs 使用情况
sudo btrfs filesystem usage /var/lib/containers/storage

# 查看子卷
sudo btrfs subvolume list /var/lib/containers/storage

# 快照卷
sudo btrfs subvolume snapshot /var/lib/containers/storage/volume1 \
  /var/lib/containers/storage/volume1-snapshot
```

### 1.4 zfs 驱动

ZFS 驱动提供企业级存储特性。

**特点**：

- ✅ **快照和克隆**：瞬时快照
- ✅ **压缩**：多种压缩算法
- ✅ **去重**：块级去重
- ✅ **数据完整性**：校验和保护
- ❌ **限制**：需要 ZFS 内核模块

**配置 zfs**：

```bash
# 安装 ZFS
sudo dnf install zfs  # Fedora
sudo apt-get install zfsutils-linux  # Ubuntu

# 创建 ZFS 池和数据集
sudo zpool create tank /dev/sdb
sudo zfs create -o mountpoint=/var/lib/containers/storage tank/podman

# 配置
# /etc/containers/storage.conf
[storage]
driver = "zfs"
graphroot = "/var/lib/containers/storage"

[storage.options.zfs]
# ZFS 文件系统名称
fsname = "tank/podman"
```

**zfs 管理**：

```bash
# 查看 ZFS 文件系统
sudo zfs list

# 查看池状态
sudo zpool status

# 创建快照
sudo zfs snapshot tank/podman@snapshot1

# 克隆
sudo zfs clone tank/podman@snapshot1 tank/podman-clone

# 压缩
sudo zfs set compression=lz4 tank/podman

# 去重（消耗内存）
sudo zfs set dedup=on tank/podman
```

### 1.5 vfs 驱动

VFS 驱动是最简单但最低效的驱动。

**特点**：

- ✅ **兼容性好**：支持所有文件系统
- ✅ **简单**：无特殊要求
- ❌ **性能差**：完全复制每一层
- ❌ **空间浪费**：无共享，空间占用大

**适用场景**：

- 测试和开发
- 不支持其他驱动的文件系统
- 临时环境

**配置 vfs**：

```toml
# /etc/containers/storage.conf
[storage]
driver = "vfs"
```

**警告**：

```bash
# ⚠️ 不推荐在生产环境使用 vfs
# 每个容器层都完全复制，非常耗费空间

# 示例：同一个基础镜像运行3个容器
podman pull nginx:alpine  # ~23MB
podman run -d --name c1 nginx:alpine
podman run -d --name c2 nginx:alpine
podman run -d --name c3 nginx:alpine

# overlay: ~23MB * 1 = 23MB
# vfs: ~23MB * 3 = 69MB (每个容器完整复制)
```

### 1.6 存储驱动选择

**选择决策树**：

```text
有 ZFS 吗？
  ├─ 是 → 使用 zfs（企业级特性）
  └─ 否 ↓

有 Btrfs 吗？
  ├─ 是 → 使用 btrfs（高级特性）
  └─ 否 ↓

内核 >= 4.0 且文件系统是 ext4/xfs？
  ├─ 是 → 使用 overlay（推荐）
  └─ 否 ↓

Rootless 模式？
  ├─ 是 → 使用 overlay + fuse-overlayfs
  └─ 否 → 使用 vfs（最后选择）
```

**性能对比**：

| 驱动 | 镜像构建 | 容器启动 | 磁盘使用 | 推荐度 |
|------|---------|----------|----------|--------|
| **overlay2** | 快 | 快 | 低 | ⭐⭐⭐⭐⭐ |
| **btrfs** | 快 | 快 | 中 | ⭐⭐⭐⭐ |
| **zfs** | 中 | 快 | 中 | ⭐⭐⭐⭐ |
| **vfs** | 慢 | 慢 | 高 | ⭐⭐ |

**切换存储驱动**：

```bash
# ⚠️ 警告：切换驱动会丢失现有数据！

# 1. 导出重要容器和镜像
podman save -o images.tar image1 image2
podman export container1 > container1.tar

# 2. 停止所有容器
podman stop -a

# 3. 重置存储
podman system reset --force

# 4. 修改配置
sudo vim /etc/containers/storage.conf
# 修改 driver = "overlay"

# 5. 重新导入
podman load -i images.tar
```

## 2. 数据卷与绑定挂载

### 2.1 数据卷管理

Podman 卷提供持久化存储，独立于容器生命周期。

**创建和管理卷**：

```bash
# 创建卷
podman volume create myvolume

# 列出卷
podman volume ls

# 查看卷详情
podman volume inspect myvolume

# 使用卷
podman run -d --name web -v myvolume:/usr/share/nginx/html nginx:alpine

# 删除卷
podman volume rm myvolume

# 删除所有未使用的卷
podman volume prune

# 删除所有卷（包括正在使用的）
podman volume rm -a -f
```

**卷位置**：

```bash
# Rootful 模式
/var/lib/containers/storage/volumes/

# Rootless 模式
$HOME/.local/share/containers/storage/volumes/

# 查看卷实际路径
podman volume inspect myvolume | jq '.[0].Mountpoint'
```

**卷驱动和选项**：

```bash
# 创建带选项的卷
podman volume create \
  --driver local \
  --opt type=tmpfs \
  --opt device=tmpfs \
  --opt o=size=100m \
  tmpvolume

# 创建 NFS 卷
podman volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=nfs-server.example.com,vers=4 \
  --opt device=:/path/on/server \
  nfsvolume

# 创建带标签的卷
podman volume create --label env=production --label tier=database dbvolume
```

**卷使用模式**：

```bash
# 只读卷
podman run -d -v myvolume:/data:ro nginx:alpine

# 读写卷
podman run -d -v myvolume:/data:rw nginx:alpine

# 卷权限（rootless 模式重要）
podman run -d -v myvolume:/data:rw,U nginx:alpine  # U: 自动chown
```

### 2.2 绑定挂载

绑定挂载直接挂载主机目录到容器。

**基本绑定挂载**：

```bash
# 挂载主机目录
podman run -d -v /host/path:/container/path nginx:alpine

# 只读挂载
podman run -d -v /host/path:/container/path:ro nginx:alpine

# 使用 --mount 语法（更明确）
podman run -d \
  --mount type=bind,source=/host/path,target=/container/path \
  nginx:alpine

# 挂载单个文件
podman run -d -v /host/config.conf:/etc/app/config.conf:ro nginx:alpine
```

**绑定挂载选项**：

```bash
# 递归绑定
podman run -d \
  --mount type=bind,source=/host,target=/data,bind-recursive=enabled \
  nginx:alpine

# 传播模式
podman run -d \
  --mount type=bind,source=/host,target=/data,bind-propagation=shared \
  nginx:alpine

# 传播模式选项：
# - shared: 双向传播
# - slave: 单向传播（主机→容器）
# - private: 无传播（默认）
# - rshared, rslave, rprivate: 递归版本
```

**相对路径和当前目录**：

```bash
# 使用相对路径
podman run -d -v ./data:/data nginx:alpine

# 使用 $PWD
podman run -d -v $PWD:/app nginx:alpine

# 使用 $(pwd)
podman run -d -v $(pwd):/workspace nginx:alpine
```

### 2.3 SELinux 标签

在启用 SELinux 的系统上（如 RHEL/Fedora），需要正确设置 SELinux 标签。

**SELinux 标签选项**：

```bash
# :z - 共享标签（多个容器可访问）
podman run -d -v /host/data:/data:z nginx:alpine

# :Z - 私有标签（仅此容器可访问）
podman run -d -v /host/data:/data:Z nginx:alpine

# 对比：
# :z → svirt_sandbox_file_t:s0:c100,c200 (共享)
# :Z → svirt_sandbox_file_t:s0:c300,c400 (唯一)
```

**检查 SELinux 标签**：

```bash
# 查看文件SELinux上下文
ls -Z /host/data

# 检查容器内的标签
podman exec container ls -Z /data

# 手动设置 SELinux 标签（不推荐，使用 :z/:Z 更好）
sudo chcon -Rt svirt_sandbox_file_t /host/data
```

**SELinux 故障排查**：

```bash
# 症状：Permission denied (即使 Unix 权限正确)

# 检查 SELinux 状态
getenforce

# 查看 SELinux 拒绝日志
sudo ausearch -m AVC -ts recent | grep podman

# 临时禁用 SELinux（仅测试用）
sudo setenforce 0

# 永久禁用（不推荐）
sudo sed -i 's/SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config

# 正确做法：使用 :z 或 :Z 标签
podman run -d -v /host/data:/data:Z nginx:alpine
```

### 2.4 tmpfs 挂载

Tmpfs 挂载创建内存中的文件系统，适合临时数据。

**创建 tmpfs 挂载**：

```bash
# 基本 tmpfs
podman run -d --tmpfs /tmp nginx:alpine

# 指定大小
podman run -d --tmpfs /tmp:size=100m nginx:alpine

# 多个选项
podman run -d --tmpfs /tmp:rw,noexec,nosuid,size=100m nginx:alpine

# 使用 --mount 语法
podman run -d \
  --mount type=tmpfs,destination=/tmp,tmpfs-size=100m,tmpfs-mode=1777 \
  nginx:alpine
```

**tmpfs 用途**：

1. **临时文件**：缓存、临时处理文件
2. **安全**：敏感数据不落盘
3. **性能**：内存速度

**示例：只读根文件系统 + tmpfs**：

```bash
# 安全配置：只读根 + tmpfs 写入点
podman run -d \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --tmpfs /var/run:rw,noexec,nosuid,size=32m \
  nginx:alpine
```

### 2.5 挂载选项

**完整的挂载选项表**：

| 选项 | 说明 | 示例 |
|------|------|------|
| `ro` | 只读 | `-v /data:/data:ro` |
| `rw` | 读写（默认） | `-v /data:/data:rw` |
| `z` | SELinux 共享标签 | `-v /data:/data:z` |
| `Z` | SELinux 私有标签 | `-v /data:/data:Z` |
| `U` | chown 到容器用户 | `-v /data:/data:U` |
| `noexec` | 禁止执行 | `--tmpfs /tmp:noexec` |
| `nosuid` | 禁止 SUID | `--tmpfs /tmp:nosuid` |
| `nodev` | 禁止设备文件 | `--tmpfs /tmp:nodev` |

**高级挂载示例**：

```bash
# 组合多个选项
podman run -d -v /app:/app:ro,z,U nginx:alpine

# 完整的 --mount 语法
podman run -d \
  --mount type=bind,source=/host/data,target=/data,readonly=true,relabel=shared \
  nginx:alpine

# 多个挂载点
podman run -d \
  -v /data1:/data1:ro \
  -v /data2:/data2:rw,Z \
  --tmpfs /tmp:size=100m \
  nginx:alpine
```

## 3. 性能与一致性

### 3.1 文件系统语义

不同存储驱动的文件系统行为略有差异。

**写时复制（CoW）行为**：

```bash
# overlay/btrfs/zfs 使用 CoW
# 首次写入时复制数据到容器层

# 测试 CoW
podman run --rm -it alpine sh
# 在容器内
dd if=/dev/zero of=/bigfile bs=1M count=1000
# 观察主机存储使用
df -h /var/lib/containers/storage
```

**文件一致性**：

```bash
# 默认：最终一致性（性能优先）
podman run -d -v /data:/data nginx:alpine

# 强一致性：使用 sync 挂载
podman run -d \
  --mount type=bind,source=/data,target=/data,bind-propagation=rsync \
  nginx:alpine

# 对于关键数据，考虑使用 sync
podman run -d -v /data:/data:sync nginx:alpine
```

**文件系统限制**：

```bash
# 某些文件系统特性可能不支持

# 测试文件系统功能
podman run --rm -v /data:/data alpine sh -c '
  # 测试硬链接
  touch /data/test
  ln /data/test /data/test-link
  
  # 测试文件锁
  flock /data/test echo "locked"
  
  # 测试 inotify
  inotifywait /data
'
```

### 3.2 IO 限制

使用 cgroups 限制容器的 IO。

**限制 IO 带宽**：

```bash
# 限制读取速度（字节/秒）
podman run -d \
  --device-read-bps /dev/sda:1mb \
  nginx:alpine

# 限制写入速度
podman run -d \
  --device-write-bps /dev/sda:1mb \
  nginx:alpine

# 限制 IOPS
podman run -d \
  --device-read-iops /dev/sda:100 \
  --device-write-iops /dev/sda:100 \
  nginx:alpine

# 组合限制
podman run -d \
  --device-read-bps /dev/sda:10mb \
  --device-write-bps /dev/sda:10mb \
  --device-read-iops /dev/sda:1000 \
  --device-write-iops /dev/sda:1000 \
  nginx:alpine
```

**blkio 权重**：

```bash
# 设置 IO 权重（默认 500，范围 10-1000）
podman run -d --blkio-weight 300 nginx:alpine
podman run -d --blkio-weight 700 postgres:alpine

# 针对特定设备设置权重
podman run -d \
  --blkio-weight-device /dev/sda:300 \
  nginx:alpine
```

**监控 IO**：

```bash
# 使用 podman stats
podman stats --format "table {{.Name}}\t{{.BlockInput}}\t{{.BlockOutput}}"

# 使用 iostat
iostat -x 1

# 使用 iotop（需要安装）
sudo iotop -o

# 检查 cgroup IO 统计
cat /sys/fs/cgroup/system.slice/system-podman.slice/*/io.stat
```

### 3.3 Cgroups 集成

存储与 cgroups 的交互。

**Cgroups v2 IO 控制**：

```bash
# 检查 cgroups 版本
mount | grep cgroup

# cgroups v2 (推荐)
/sys/fs/cgroup cgroup2

# 设置 IO 限制（cgroups v2）
podman run -d \
  --cpu-shares 512 \
  --memory 512m \
  --device-write-bps /dev/sda:10mb \
  nginx:alpine

# 查看 cgroup 配置
podman inspect container | jq '.[0].HostConfig.Resources'
```

**IO 优先级**：

```bash
# 设置 IO nice (ionice)
# 0: 无优先级, 1: 实时, 2: 尽力而为, 3: 空闲
podman run -d \
  --ulimit nofile=1024:2048 \
  nginx:alpine

# 在容器内设置 ionice
podman exec container ionice -c 2 -n 7 process_name
```

### 3.4 性能调优

**overlay 性能调优**：

```bash
# 使用 native overlay（而非 fuse-overlayfs）
# /etc/containers/storage.conf
[storage.options.overlay]
mount_program = ""  # 空字符串表示使用原生

# 调整 inode 缓存
echo 100000 | sudo tee /proc/sys/fs/inotify/max_user_watches

# 禁用 atime 更新
sudo mount -o remount,noatime /var/lib/containers/storage
```

**文件系统调优**：

```bash
# ext4 调优
sudo tune2fs -O dir_index /dev/sda1
sudo tune2fs -o journal_data_writeback /dev/sda1

# xfs 调优
sudo mount -o remount,noatime,nodiratime /var/lib/containers/storage

# 增加文件描述符限制
ulimit -n 65536
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
```

**减少层数**：

```dockerfile
# ❌ 不好：多层
FROM alpine
RUN apk add package1
RUN apk add package2
RUN apk add package3

# ✅ 好：合并层
FROM alpine
RUN apk add --no-cache package1 package2 package3

# ✅ 更好：多阶段构建
FROM golang:1.22-alpine AS builder
RUN go build -o app .

FROM alpine:3.20
COPY --from=builder /go/app /usr/local/bin/
```

**存储清理**：

```bash
# 定期清理未使用的资源
podman system prune -a -f

# 清理构建缓存
podman builder prune -a -f

# 清理卷
podman volume prune -f

# 清理所有
podman system prune -a --volumes -f

# 自动化清理（cron）
0 2 * * * podman system prune -a -f > /dev/null 2>&1
```

## 4. 备份与迁移

### 4.1 卷备份

**备份卷数据**：

```bash
# 方法1：使用 tar
podman run --rm \
  -v myvolume:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/myvolume-backup.tar.gz -C /data .

# 方法2：使用 rsync
podman run --rm \
  -v myvolume:/data \
  -v /backup:/backup \
  alpine sh -c "apk add rsync && rsync -av /data/ /backup/"

# 方法3：直接复制（rootful）
sudo cp -a /var/lib/containers/storage/volumes/myvolume/_data /backup/
```

**恢复卷数据**：

```bash
# 创建新卷
podman volume create myvolume-restored

# 恢复数据
podman run --rm \
  -v myvolume-restored:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/myvolume-backup.tar.gz -C /data

# 验证
podman run --rm -v myvolume-restored:/data alpine ls -la /data
```

**增量备份**：

```bash
#!/bin/bash
# incremental-backup.sh

VOLUME="myvolume"
BACKUP_DIR="/backup/volumes"
DATE=$(date +%Y%m%d-%H%M%S)

# 完整备份（每周日）
if [ $(date +%u) -eq 7 ]; then
  podman run --rm \
    -v $VOLUME:/data:ro \
    -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/$VOLUME-full-$DATE.tar.gz -C /data .
else
  # 增量备份（其他天）
  podman run --rm \
    -v $VOLUME:/data:ro \
    -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/$VOLUME-inc-$DATE.tar.gz \
      --newer-mtime="$(date -d '1 day ago' +%Y-%m-%d)" \
      -C /data .
fi
```

### 4.2 镜像备份

**导出镜像**：

```bash
# 导出单个镜像
podman save -o nginx.tar nginx:alpine

# 导出多个镜像
podman save -o images.tar nginx:alpine redis:alpine postgres:alpine

# 压缩导出
podman save nginx:alpine | gzip > nginx.tar.gz

# 导出所有镜像
podman save -o all-images.tar $(podman images -q)
```

**导入镜像**：

```bash
# 导入镜像
podman load -i nginx.tar

# 导入压缩镜像
gunzip -c nginx.tar.gz | podman load

# 从标准输入导入
cat nginx.tar | podman load
```

**镜像仓库同步**（使用 skopeo）：

```bash
# 同步镜像到另一个仓库
skopeo copy \
  docker://docker.io/library/nginx:alpine \
  docker://registry.local/nginx:alpine

# 批量同步
for image in nginx:alpine redis:alpine postgres:alpine; do
  skopeo copy docker://docker.io/library/$image docker://registry.local/$image
done
```

### 4.3 离线迁移

**完整系统迁移**：

```bash
#!/bin/bash
# export-system.sh - 在源系统运行

BACKUP_DIR="/backup/podman-migration"
mkdir -p $BACKUP_DIR

# 1. 导出所有镜像
echo "导出镜像..."
podman save -o $BACKUP_DIR/images.tar $(podman images -q)

# 2. 导出所有卷
echo "导出卷..."
for volume in $(podman volume ls -q); do
  podman run --rm \
    -v $volume:/data:ro \
    -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/volume-$volume.tar.gz -C /data .
done

# 3. 导出容器配置
echo "导出容器配置..."
podman ps -a --format json > $BACKUP_DIR/containers.json

# 4. 导出网络配置
echo "导出网络配置..."
podman network ls --format json > $BACKUP_DIR/networks.json

# 5. 打包
echo "打包..."
tar czf podman-backup-$(date +%Y%m%d).tar.gz -C /backup podman-migration/

echo "备份完成！"
```

**导入到新系统**：

```bash
#!/bin/bash
# import-system.sh - 在目标系统运行

BACKUP_FILE="podman-backup-20250118.tar.gz"
WORK_DIR="/tmp/podman-import"

# 1. 解压
mkdir -p $WORK_DIR
tar xzf $BACKUP_FILE -C $WORK_DIR

# 2. 导入镜像
echo "导入镜像..."
podman load -i $WORK_DIR/podman-migration/images.tar

# 3. 创建并恢复卷
echo "恢复卷..."
for volume_tar in $WORK_DIR/podman-migration/volume-*.tar.gz; do
  volume_name=$(basename $volume_tar | sed 's/volume-//;s/.tar.gz//')
  echo "恢复卷: $volume_name"
  
  podman volume create $volume_name
  podman run --rm \
    -v $volume_name:/data \
    -v $WORK_DIR/podman-migration:/backup \
    alpine tar xzf /backup/$(basename $volume_tar) -C /data
done

# 4. 重建网络
echo "重建网络..."
# 根据 networks.json 手动重建网络配置

# 5. 重建容器
echo "重建容器..."
# 根据 containers.json 手动重建容器

echo "导入完成！请手动验证并启动容器。"
```

### 4.4 在线迁移

使用 `podman migrate` 或实时同步：

```bash
# 使用 rsync 实时同步卷数据
# 在源系统
rsync -avz -e ssh /var/lib/containers/storage/volumes/ \
  user@target-host:/var/lib/containers/storage/volumes/

# 使用 podman save/load 通过 SSH
podman save nginx:alpine | ssh target-host podman load

# 使用镜像仓库中转
podman tag myapp:latest registry.local/myapp:latest
podman push registry.local/myapp:latest

# 在目标系统
podman pull registry.local/myapp:latest
```

## 5. 故障与恢复

### 5.1 权限问题

**常见权限问题**：

```bash
# 问题1：Permission denied (rootless 模式)

# 诊断
podman run --rm -v /host/data:/data alpine ls -la /data
# 错误：Permission denied

# 原因：UID/GID 映射不匹配

# 解决方案1：使用 :U 标签（自动 chown）
podman run --rm -v /host/data:/data:U alpine ls -la /data

# 解决方案2：使用 podman unshare
podman unshare chown -R 0:0 /host/data

# 解决方案3：调整 subuid/subgid
cat /etc/subuid
cat /etc/subgid
# 确保用户有足够的 UID/GID 范围

# 问题2：SELinux 阻止访问

# 诊断
sudo ausearch -m AVC -ts recent | grep podman

# 解决：使用 :z 或 :Z
podman run --rm -v /host/data:/data:Z alpine ls -la /data
```

**修复权限**：

```bash
# rootless 模式下修复卷权限
podman unshare chown -R $(id -u):$(id -g) \
  $HOME/.local/share/containers/storage/volumes/myvolume/_data

# rootful 模式
sudo chown -R root:root /var/lib/containers/storage/volumes/myvolume/_data

# 修复 SELinux 标签
sudo chcon -Rt svirt_sandbox_file_t /var/lib/containers/storage
```

### 5.2 层损坏恢复

**检测层损坏**：

```bash
# 症状：容器启动失败，镜像损坏

# 检查存储完整性
podman system check

# 查看存储状态
podman info --format json | jq '.store'

# 检查特定镜像
podman inspect image:tag
```

**恢复步骤**：

```bash
# 1. 停止所有容器
podman stop -a

# 2. 备份当前存储
sudo cp -a /var/lib/containers/storage /var/lib/containers/storage.backup

# 3. 尝试修复
podman system reset --force

# 4. 重新导入镜像
podman load -i images-backup.tar

# 5. 如果单个镜像损坏，重新拉取
podman rmi -f image:tag
podman pull image:tag
```

**预防措施**：

```bash
# 1. 定期备份
0 2 * * * podman save -o /backup/images-$(date +\%Y\%m\%d).tar $(podman images -q)

# 2. 使用只读根文件系统
podman run --read-only --tmpfs /tmp myapp:latest

# 3. 监控存储健康
df -h /var/lib/containers/storage
sudo btrfs device stats /var/lib/containers/storage  # 如果使用 btrfs
```

### 5.3 空间清理

**磁盘空间不足**：

```bash
# 查看存储使用
podman system df

# 详细信息
podman system df -v

# 清理未使用的镜像
podman image prune -a

# 清理未使用的容器
podman container prune

# 清理未使用的卷
podman volume prune

# 清理所有未使用的资源
podman system prune -a --volumes

# 强制清理（不询问）
podman system prune -a --volumes -f
```

**自动清理策略**：

```bash
# 创建清理脚本
cat > /usr/local/bin/podman-cleanup.sh <<'EOF'
#!/bin/bash
# 保留最近7天的镜像，清理其他
CUTOFF_DATE=$(date -d '7 days ago' +%s)

podman images --format "{{.ID}} {{.Created}}" | while read id created; do
  created_timestamp=$(date -d "$created" +%s 2>/dev/null || echo 0)
  if [ $created_timestamp -lt $CUTOFF_DATE ]; then
    echo "删除镜像: $id (created: $created)"
    podman rmi -f $id 2>/dev/null || true
  fi
done

# 清理卷和容器
podman container prune -f
podman volume prune -f
EOF

chmod +x /usr/local/bin/podman-cleanup.sh

# 添加到 cron
0 3 * * * /usr/local/bin/podman-cleanup.sh > /var/log/podman-cleanup.log 2>&1
```

**配额管理**：

```bash
# 设置存储大小限制（需要文件系统支持）
# /etc/containers/storage.conf
[storage.options]
size = "120G"

# 使用 XFS 配额
sudo xfs_quota -x -c 'limit bsoft=100g bhard=120g podman' /var/lib/containers

# 监控配额
sudo xfs_quota -x -c 'report -h' /var/lib/containers
```

## 6. 实操示例

### 6.1 卷管理示例

```bash
#!/bin/bash
# volume-demo.sh - 卷管理演示

# 1. 创建应用卷
echo "创建应用卷..."
podman volume create app-data
podman volume create app-logs
podman volume create app-config

# 2. 使用卷运行应用
echo "启动应用..."
podman run -d \
  --name myapp \
  -v app-data:/app/data \
  -v app-logs:/app/logs \
  -v app-config:/app/config:ro \
  myapp:latest

# 3. 备份卷
echo "备份卷..."
for vol in app-data app-logs app-config; do
  podman run --rm \
    -v $vol:/source:ro \
    -v $(pwd)/backup:/backup \
    alpine tar czf /backup/$vol-$(date +%Y%m%d).tar.gz -C /source .
done

# 4. 检查卷使用
echo "卷使用情况..."
podman system df -v | grep app-

# 5. 清理（小心！）
# podman stop myapp
# podman rm myapp
# podman volume rm app-data app-logs app-config
```

### 6.2 数据备份示例

```bash
#!/bin/bash
# backup-containers.sh - 完整备份脚本

BACKUP_ROOT="/backup/podman"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$DATE"

mkdir -p $BACKUP_DIR

echo "=== Podman 备份开始: $DATE ==="

# 1. 备份镜像
echo "备份镜像..."
podman save -o $BACKUP_DIR/images.tar $(podman images -q)
echo "镜像备份完成: $(du -h $BACKUP_DIR/images.tar | cut -f1)"

# 2. 备份卷
echo "备份卷..."
mkdir -p $BACKUP_DIR/volumes
for volume in $(podman volume ls -q); do
  echo "  备份卷: $volume"
  podman run --rm \
    -v $volume:/data:ro \
    -v $BACKUP_DIR/volumes:/backup \
    alpine tar czf /backup/$volume.tar.gz -C /data .
done

# 3. 导出容器配置
echo"备份容器配置..."
podman ps -a --format json > $BACKUP_DIR/containers.json
podman network ls --format json > $BACKUP_DIR/networks.json

# 4. 备份配置文件
echo "备份配置文件..."
sudo cp -a /etc/containers $BACKUP_DIR/etc-containers

# 5. 创建备份清单
echo "创建备份清单..."
cat > $BACKUP_DIR/manifest.txt <<EOF
Backup Date: $DATE
Images: $(podman images -q | wc -l)
Containers: $(podman ps -a -q | wc -l)
Volumes: $(podman volume ls -q | wc -l)
Networks: $(podman network ls -q | wc -l)
Total Size: $(du -sh $BACKUP_DIR | cut -f1)
EOF

# 6. 压缩备份
echo "压缩备份..."
tar czf $BACKUP_ROOT/podman-backup-$DATE.tar.gz -C $BACKUP_ROOT $DATE

# 7. 清理旧备份（保留最近7天）
echo "清理旧备份..."
find $BACKUP_ROOT -name "podman-backup-*.tar.gz" -mtime +7 -delete

echo "=== 备份完成！==="
echo "备份文件: $BACKUP_ROOT/podman-backup-$DATE.tar.gz"
ls -lh $BACKUP_ROOT/podman-backup-$DATE.tar.gz
```

### 6.3 存储迁移示例

```bash
#!/bin/bash
# migrate-storage.sh - 迁移存储驱动

OLD_DRIVER="vfs"
NEW_DRIVER="overlay"

echo "=== 迁移存储驱动: $OLD_DRIVER → $NEW_DRIVER ==="

# 1. 备份数据
echo "1. 备份现有数据..."
BACKUP_DIR="/backup/storage-migration-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

podman save -o $BACKUP_DIR/images.tar $(podman images -q)
for vol in $(podman volume ls -q); do
  podman run --rm -v $vol:/data:ro -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/volume-$vol.tar.gz -C /data .
done

# 2. 停止所有容器
echo "2. 停止所有容器..."
podman stop -a

# 3. 重置存储
echo "3. 重置存储..."
podman system reset --force

# 4. 更改存储驱动
echo "4. 更新配置文件..."
sudo sed -i "s/driver = \"$OLD_DRIVER\"/driver = \"$NEW_DRIVER\"/" \
  /etc/containers/storage.conf

# 5. 恢复数据
echo "5. 恢复镜像..."
podman load -i $BACKUP_DIR/images.tar

echo "6. 恢复卷..."
for vol_tar in $BACKUP_DIR/volume-*.tar.gz; do
  vol_name=$(basename $vol_tar | sed 's/volume-//;s/.tar.gz//')
  echo "  恢复卷: $vol_name"
  podman volume create $vol_name
  podman run --rm -v $vol_name:/data -v $BACKUP_DIR:/backup \
    alpine tar xzf /backup/$(basename $vol_tar) -C /data
done

# 7. 验证
echo "7. 验证迁移..."
echo "存储驱动: $(podman info | grep graphDriverName)"
echo "镜像数量: $(podman images -q | wc -l)"
echo "卷数量: $(podman volume ls -q | wc -l)"

echo "=== 迁移完成！请手动重启容器。==="
```

## 7. 故障清单与排查

**问题1：权限拒绝（Permission denied）**:

```bash
# 症状
podman run -v /host/data:/data alpine ls /data
# Error: open /data: permission denied

# 排查
# 1. 检查 SELinux
getenforce
ls -Z /host/data

# 2. 检查 Unix 权限
ls -la /host/data

# 3. 检查 UID 映射（rootless）
podman unshare cat /proc/self/uid_map

# 解决方案
# A. 使用 SELinux 标签
podman run -v /host/data:/data:Z alpine ls /data

# B. 使用 :U 自动 chown
podman run -v /host/data:/data:U alpine ls /data

# C. 手动修复权限
podman unshare chown -R 0:0 /host/data
```

**问题2：Overlay 报错**:

```bash
# 症状
Error: overlay: invalid argument

# 排查
# 1. 检查内核版本
uname -r  # 需要 >= 4.0

# 2. 检查文件系统
df -T /var/lib/containers/storage  # 应该是 ext4 或 xfs

# 3. 检查 overlay 模块
lsmod | grep overlay

# 4. 检查 dmesg
sudo dmesg | grep -i overlay

# 解决方案
# A. 加载 overlay 模块
sudo modprobe overlay

# B. 切换到 fuse-overlayfs（rootless）
# ~/.config/containers/storage.conf
[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"

# C. 切换文件系统或存储驱动
```

**问题3：性能异常**:

```bash
# 症状：容器 IO 缓慢

# 排查
# 1. 检查磁盘性能
iostat -x 1

# 2. 检查存储驱动
podman info | grep graphDriverName

# 3. 检查磁盘使用
df -h /var/lib/containers/storage
podman system df

# 4. 检查 IO 限制
podman inspect container | jq '.[0].HostConfig.BlkioDeviceReadBps'

# 解决方案
# A. 清理空间
podman system prune -a --volumes -f

# B. 优化存储驱动
# 切换到 overlay2/btrfs/zfs

# C. 调整 IO 限制
podman run --device-write-bps /dev/sda:100mb ...

# D. 优化文件系统挂载
sudo mount -o remount,noatime /var/lib/containers/storage
```

**问题4：磁盘空间不足**:

```bash
# 症状
Error: No space left on device

# 排查
df -h /var/lib/containers/storage
podman system df

# 解决方案
# 1. 清理未使用资源
podman system prune -a --volumes -f

# 2. 删除旧镜像
podman images | grep '<none>' | awk '{print $3}' | xargs podman rmi

# 3. 清理构建缓存
podman builder prune -a -f

# 4. 扩展磁盘/分区
```

**问题5：卷数据丢失**:

```bash
# 症状：容器重启后数据丢失

# 排查
# 1. 检查卷是否正确挂载
podman inspect container | jq '.[0].Mounts'

# 2. 检查卷是否存在
podman volume ls
podman volume inspect volume_name

# 原因
# - 使用匿名卷（未命名）
# - 使用 tmpfs
# - 容器被删除（--rm）

# 解决方案
# A. 使用命名卷
podman run -v my-named-volume:/data ...

# B. 不使用 --rm 标志（或备份数据）
podman run --name persistent-container ...

# C. 定期备份
```

## 8. FAQ

**Q1: rootless 卷在哪里？**

A: Rootless 模式下，卷位于：

```bash
$HOME/.local/share/containers/storage/volumes/

# 查看具体位置
podman volume inspect myvolume | jq '.[0].Mountpoint'
```

**Q2: 如何在 rootless 和 rootful 之间共享卷？**

A: 不能直接共享，但可以通过容器中转：

```bash
# 从 rootless 导出
podman run --rm -v myvolume:/data -v $(pwd):/backup alpine \
  tar czf /backup/data.tar.gz -C /data .

# 导入到 rootful
sudo podman volume create myvolume
sudo podman run --rm -v myvolume:/data -v $(pwd):/backup alpine \
  tar xzf /backup/data.tar.gz -C /data
```

**Q3: overlay vs btrfs vs zfs？**

A: 选择建议：

- **overlay**: 默认推荐，适合大多数场景
- **btrfs**: 如果已使用 Btrfs 文件系统
- **zfs**: 需要企业级特性（快照、去重）
- **vfs**: 仅用于测试/兼容性

**Q4: 如何限制容器的磁盘使用？**

A: 方法：

1. **存储驱动配额**（XFS/ZFS）
2. **容器配额**（仅部分驱动支持）
3. **卷大小限制**

```bash
# 使用 tmpfs 限制
podman run --tmpfs /tmp:size=100m alpine

# 使用存储配置限制
# /etc/containers/storage.conf
[storage.options]
size = "10G"
```

**Q5: SELinux `:z` 和 `:Z` 的区别？**

A:

- **`:z`** - 共享标签，多个容器可访问同一目录
- **`:Z`** - 私有标签，仅当前容器独占

```bash
# :z - 多容器共享
podman run -v /shared:/data:z container1
podman run -v /shared:/data:z container2  # OK

# :Z - 独占
podman run -v /private:/data:Z container1
podman run -v /private:/data:Z container2  # 权限错误！
```

**Q6: 如何备份 Podman 的所有数据？**

A: 完整备份包括：

1. 镜像：`podman save`
2. 卷：`tar` 备份
3. 配置：`/etc/containers/`
4. 容器定义：`podman inspect`

参考"6.2 数据备份示例"中的完整脚本。

**Q7: 如何迁移到不同的存储驱动？**

A: 步骤：

1. 备份数据（`podman save`, 卷备份）
2. 重置存储（`podman system reset`）
3. 修改配置文件（`/etc/containers/storage.conf`）
4. 恢复数据（`podman load`, 卷恢复）

参考"6.3 存储迁移示例"。

**Q8: 卷和绑定挂载的区别？**

A:

- **卷（Volume）**：Podman 管理，更安全，跨平台
- **绑定挂载（Bind Mount）**：直接挂载主机目录，更灵活

```bash
# 卷
podman volume create myvolume
podman run -v myvolume:/data alpine

# 绑定挂载
podman run -v /host/path:/data alpine
```

推荐生产环境使用卷。

**Q9: 如何检查存储健康状态？**

A:

```bash
# 1. 基本检查
podman system df
podman info

# 2. 文件系统检查
df -h /var/lib/containers/storage
df -i /var/lib/containers/storage  # inode 使用

# 3. 特定文件系统
sudo btrfs device stats /var/lib/containers/storage  # Btrfs
sudo zpool status  # ZFS

# 4. 检查层完整性
podman system check
```

**Q10: 如何处理 "no space left on device" 错误？**

A: 步骤：

1. 清理未使用资源：`podman system prune -a --volumes -f`
2. 检查 inode：`df -i`
3. 清理旧镜像和层
4. 扩展存储空间
5. 调整配额

详见"5.3 空间清理"部分。

## 9. 基线模板（建议）

**生产环境推荐配置**：

```toml
# /etc/containers/storage.conf
[storage]
# 使用 overlay2 驱动
driver = "overlay"

# 存储路径
graphroot = "/var/lib/containers/storage"
runroot = "/run/containers/storage"

[storage.options]
# 挂载选项
mountopt = "nodev"

# 大小限制（如果文件系统支持）
size = "120G"

# 忽略 chown 错误（rootless 需要）
ignore_chown_errors = "false"

[storage.options.overlay]
# 使用原生 overlay（性能更好）
mount_program = ""

# 镜像存储
[storage.options.aufs]
mountopt = "rw"

[storage.options.thinpool]
autoextend_percent = "20"
autoextend_threshold = "80"
```

**Rootless 推荐配置**：

```toml
# ~/.config/containers/storage.conf
[storage]
driver = "overlay"

runroot = "$HOME/.local/share/containers/storage/tmp"
graphroot = "$HOME/.local/share/containers/storage"

[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"
mountopt = "nodev"

[storage.options.overlay]
ignore_chown_errors = "true"
```

**监控和告警建议**：

```bash
#!/bin/bash
# storage-monitor.sh - 存储监控脚本

# 磁盘使用告警阈值
DISK_WARN=80
DISK_CRIT=90

# 检查磁盘使用
DISK_USAGE=$(df -h /var/lib/containers/storage | tail -1 | awk '{print $5}' | sed 's/%//')

if [ $DISK_USAGE -ge $DISK_CRIT ]; then
  echo "CRITICAL: 存储使用率 ${DISK_USAGE}%"
  # 发送告警...
elif [ $DISK_USAGE -ge $DISK_WARN ]; then
  echo "WARNING: 存储使用率 ${DISK_USAGE}%"
  # 发送警告...
fi

# 检查 inode 使用
INODE_USAGE=$(df -i /var/lib/containers/storage | tail -1 | awk '{print $5}' | sed 's/%//')

if [ $INODE_USAGE -ge $DISK_CRIT ]; then
  echo "CRITICAL: inode 使用率 ${INODE_USAGE}%"
fi

# 自动清理
if [ $DISK_USAGE -ge $DISK_WARN ]; then
  echo "执行自动清理..."
  podman system prune -a -f
fi
```

**备份策略建议**：

1. **每日增量备份**：卷数据
2. **每周完整备份**：镜像 + 卷 + 配置
3. **每月验证恢复**：测试备份可用性
4. **异地备份**：关键数据异地存储

**最佳实践清单**：

- ✅ 使用 overlay2 驱动（生产环境）
- ✅ 使用命名卷而不是绑定挂载
- ✅ 正确使用 SELinux 标签（`:z`/`:Z`）
- ✅ 定期清理未使用资源
- ✅ 监控磁盘和 inode 使用
- ✅ 定期备份卷数据
- ✅ Rootless 模式使用 fuse-overlayfs
- ✅ 文件系统使用 noatime 挂载
- ✅ 设置存储配额限制
- ✅ 定期检查存储健康状态

---

**相关资源**：

- [containers/storage GitHub](https://github.com/containers/storage)
- [Podman 存储文档](https://docs.podman.io/en/latest/markdown/podman-storage.1.html)
- [OCI 镜像规范](https://github.com/opencontainers/image-spec)
- [Linux overlay 文件系统](https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html)
- [Btrfs 文档](https://btrfs.wiki.kernel.org/)
- [ZFS on Linux](https://openzfs.github.io/openzfs-docs/)
