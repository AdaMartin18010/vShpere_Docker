# Podman安全机制

> 版本锚点（新增）：本文档基于 Podman 5.0+、crun 1.14+ 和 Linux 内核 6.1+ 版本编写，版本信息统一参考《2025年技术标准最终对齐报告.md》。

## 目录

- [Podman安全机制](#podman安全机制)
  - [目录](#目录)
  - [1. Rootless 与权限模型](#1-rootless-与权限模型)
    - [1.1 Rootless 容器概述](#11-rootless-容器概述)
    - [1.2 User Namespace (userns)](#12-user-namespace-userns)
    - [1.3 subuid/subgid 配置](#13-subuidsubgid-配置)
    - [1.4 Linux Capabilities](#14-linux-capabilities)
    - [1.5 Seccomp 安全过滤](#15-seccomp-安全过滤)
    - [1.6 SELinux/AppArmor](#16-selinuxapparmor)
  - [2. 策略与供应链安全](#2-策略与供应链安全)
    - [2.1 policy.json 配置](#21-policyjson-配置)
    - [2.2 镜像签名与验证](#22-镜像签名与验证)
    - [2.3 SBOM（软件物料清单）](#23-sbom软件物料清单)
    - [2.4 漏洞扫描](#24-漏洞扫描)
    - [2.5 镜像来源控制](#25-镜像来源控制)
  - [3. 运行时与网络安全](#3-运行时与网络安全)
    - [3.1 只读根文件系统](#31-只读根文件系统)
    - [3.2 最小权限原则](#32-最小权限原则)
    - [3.3 端口暴露控制](#33-端口暴露控制)
    - [3.4 网络隔离与策略](#34-网络隔离与策略)
    - [3.5 资源限制](#35-资源限制)
  - [4. 沙箱运行时与隔离增强](#4-沙箱运行时与隔离增强)
    - [4.1 容器运行时选择](#41-容器运行时选择)
    - [4.2 Kata Containers](#42-kata-containers)
    - [4.3 gVisor](#43-gvisor)
    - [4.4 性能与安全权衡](#44-性能与安全权衡)
  - [5. 安全基线与合规](#5-安全基线与合规)
    - [5.1 容器加固清单](#51-容器加固清单)
    - [5.2 日志与审计](#52-日志与审计)
    - [5.3 秘密管理](#53-秘密管理)
    - [5.4 合规性检查](#54-合规性检查)
  - [6. 故障与应急响应](#6-故障与应急响应)
    - [6.1 容器逃逸检测](#61-容器逃逸检测)
    - [6.2 事件响应流程](#62-事件响应流程)
    - [6.3 取证与分析](#63-取证与分析)
    - [6.4 镜像回滚](#64-镜像回滚)
  - [7. 实操示例](#7-实操示例)
    - [7.1 安全容器配置](#71-安全容器配置)
    - [7.2 镜像签名流程](#72-镜像签名流程)
    - [7.3 漏洞扫描集成](#73-漏洞扫描集成)
  - [8. 故障清单与排查](#8-故障清单与排查)
  - [9. FAQ](#9-faq)
  - [10. 基线模板（建议）](#10-基线模板建议)

## 1. Rootless 与权限模型

### 1.1 Rootless 容器概述

Podman 的 rootless 模式允许非特权用户运行容器，无需 root 权限或 setuid 二进制文件。

**Rootless 的优势**：

- ✅ **安全性**：容器逃逸仅影响用户空间
- ✅ **多租户**：多用户独立运行容器
- ✅ **零特权**：无需 root 或 sudo
- ✅ **减少攻击面**：容器内 root 映射到主机非特权用户

**Rootless vs Rootful**：

| 特性 | Rootless | Rootful |
|------|----------|---------|
| 运行权限 | 普通用户 | root |
| 低端口绑定 | 需要 CAP_NET_BIND_SERVICE | 直接支持 |
| 网络性能 | 稍慢（slirp4netns） | 最优 |
| 存储位置 | `~/.local/share/containers` | `/var/lib/containers` |
| 安全性 | 高（隔离更强） | 中 |
| 推荐场景 | 开发、测试、多租户 | 生产、性能敏感 |

**启用 Rootless 模式**：

```bash
# 检查 Rootless 支持
podman system info | grep rootless
# rootless: true

# 安装必需包
sudo dnf install -y podman slirp4netns fuse-overlayfs  # Fedora/RHEL
sudo apt-get install -y podman slirp4netns fuse-overlayfs  # Ubuntu/Debian

# 配置 subuid/subgid (自动完成)
cat /etc/subuid
cat /etc/subgid

# 测试 rootless 容器
podman run --rm alpine id
# uid=0(root) gid=0(root) groups=0(root)  <- 容器内
# 实际是主机上的非特权用户
```

**Rootless 原理**：

```text
主机:
├── 用户 alice (UID 1000)
│   └── Podman rootless 进程
│       └── User Namespace
│           ├── 容器内 UID 0 (root) → 主机 UID 1000 (alice)
│           ├── 容器内 UID 1 → 主机 UID 100000
│           ├── 容器内 UID 2 → 主机 UID 100001
│           └── ...

User Namespace 映射:
容器内 UID/GID → 主机 UID/GID (非特权范围)
```

### 1.2 User Namespace (userns)

User Namespace 是 rootless 容器的核心技术。

**User Namespace 隔离**：

```bash
# 查看当前 User Namespace
ls -l /proc/self/ns/user

# 查看容器的 User Namespace
podman run --rm alpine ls -l /proc/self/ns/user

# 查看 UID 映射
podman unshare cat /proc/self/uid_map
# 0       1000          1
# 1     100000      65536

# 格式：容器内ID  主机ID  范围
# 容器内UID 0 → 主机UID 1000
# 容器内UID 1-65536 → 主机UID 100000-165536
```

**手动创建 User Namespace**：

```bash
# 使用 unshare 创建 User Namespace
unshare --user --map-root-user /bin/bash

# 在新 namespace 中
id
# uid=0(root) gid=0(root) groups=0(root)

# 但在主机上看是普通用户
ps aux | grep bash
```

**Podman unshare**：

```bash
# 进入 Podman 的 User Namespace
podman unshare

# 在此环境中操作文件会使用映射后的 UID
touch /tmp/test
ls -l /tmp/test
# -rw-r--r-- 1 root root 0 Jan 18 10:00 /tmp/test

# 退出后在主机查看
exit
ls -l /tmp/test
# -rw-r--r-- 1 alice alice 0 Jan 18 10:00 /tmp/test
```

**User Namespace 安全性**：

```bash
# 容器内即使是 root，也无法提权主机
podman run --rm alpine sh -c '
  id
  # uid=0(root) 但权限受限
  
  # 尝试访问主机资源（失败）
  mount /dev/sda1 /mnt 2>&1
  # mount: /mnt: permission denied
'
```

### 1.3 subuid/subgid 配置

`subuid` 和 `subgid` 定义用户可以使用的从属 UID/GID 范围。

**查看配置**：

```bash
# 查看 subuid 配置
cat /etc/subuid
# alice:100000:65536
# bob:200000:65536

# 查看 subgid 配置
cat /etc/subgid
# alice:100000:65536
# bob:200000:65536

# 格式：用户名:起始ID:数量
```

**添加/修改 subuid/subgid**：

```bash
# 为用户添加从属 UID/GID
sudo usermod --add-subuids 100000-165535 alice
sudo usermod --add-subgids 100000-165535 alice

# 或手动编辑
sudo vim /etc/subuid
sudo vim /etc/subgid

# 验证
grep alice /etc/subuid /etc/subgid
```

**调整范围大小**：

```bash
# 默认 65536 个 UID/GID 通常足够
# 如果需要更多（不常见）:

# /etc/subuid
alice:100000:131072  # 翻倍

# ⚠️ 修改后需要重置 Podman 存储
podman system reset --force
```

**多用户配置**：

```bash
# 确保不同用户的范围不重叠
cat /etc/subuid
alice:100000:65536    # 100000-165535
bob:200000:65536      # 200000-265535
carol:300000:65536    # 300000-365535
```

**故障排查**：

```bash
# 问题：rootless 容器无法启动
# Error: cannot set up namespace using newuidmap

# 检查 subuid/subgid
cat /etc/subuid | grep $USER
cat /etc/subgid | grep $USER

# 如果缺失，添加
sudo usermod --add-subuids 100000-165535 $USER
sudo usermod --add-subgids 100000-165535 $USER

# 重新登录
exit
# 重新登录后测试
podman run --rm alpine id
```

### 1.4 Linux Capabilities

Capabilities 将 root 权限细分为独立的能力。

**Capability 概述**：

```bash
# 查看所有 capabilities
capsh --print

# Podman 默认 capabilities (rootful)
podman run --rm alpine sh -c 'apk add libcap && capsh --print'

# 默认启用的 capabilities:
# CAP_CHOWN, CAP_DAC_OVERRIDE, CAP_FOWNER, CAP_FSETID,
# CAP_KILL, CAP_NET_BIND_SERVICE, CAP_SETFCAP, CAP_SETGID,
# CAP_SETPCAP, CAP_SETUID, CAP_SYS_CHROOT, CAP_AUDIT_WRITE
```

**常用 Capabilities**：

| Capability | 说明 | 风险 |
|------------|------|------|
| `CAP_NET_BIND_SERVICE` | 绑定低端口 (<1024) | 低 |
| `CAP_SYS_ADMIN` | 系统管理操作 | 🔴 高 |
| `CAP_SYS_PTRACE` | 进程跟踪 | 🟡 中 |
| `CAP_SYS_MODULE` | 加载内核模块 | 🔴 高 |
| `CAP_NET_RAW` | 原始网络包 | 🟡 中 |
| `CAP_DAC_OVERRIDE` | 绕过文件权限检查 | 🟡 中 |
| `CAP_CHOWN` | 更改文件所有权 | 低 |

**添加/移除 Capabilities**：

```bash
# 移除所有 capabilities（最安全）
podman run --rm --cap-drop=ALL alpine sh -c 'capsh --print'

# 移除特定 capability
podman run --rm --cap-drop=NET_RAW alpine ping 8.8.8.8
# ping: socket: Operation not permitted

# 添加特定 capability
podman run --rm --cap-drop=ALL --cap-add=NET_BIND_SERVICE alpine sh

# 添加危险 capability（谨慎！）
podman run --rm --cap-add=SYS_ADMIN alpine sh

# 查看容器的 capabilities
podman run --rm alpine sh -c '
  cat /proc/self/status | grep Cap
'
```

**最小权限实践**：

```bash
# 示例：Web 服务器只需 NET_BIND_SERVICE
podman run -d \
  --name web \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --cap-add=CHOWN \
  --cap-add=SETUID \
  --cap-add=SETGID \
  -p 80:80 \
  nginx:alpine

# 数据库容器
podman run -d \
  --name db \
  --cap-drop=ALL \
  --cap-add=CHOWN \
  --cap-add=SETUID \
  --cap-add=SETGID \
  postgres:alpine
```

**Rootless 模式的 Capabilities**：

```bash
# Rootless 模式下，容器内的 capabilities 更受限
podman run --rm alpine sh -c 'capsh --print | grep Current'

# 即使指定 --cap-add=SYS_ADMIN，也会被忽略（安全保护）
podman run --rm --cap-add=SYS_ADMIN alpine sh -c 'capsh --print'
```

### 1.5 Seccomp 安全过滤

Seccomp (Secure Computing Mode) 限制容器可以执行的系统调用。

**Seccomp 概述**：

```bash
# 检查 Seccomp 支持
grep CONFIG_SECCOMP /boot/config-$(uname -r)
# CONFIG_SECCOMP=y

# Podman 默认启用 Seccomp
podman run --rm alpine grep Seccomp /proc/self/status
# Seccomp: 2  (2 = 已过滤)
```

**默认 Seccomp 配置**：

```bash
# Podman 使用默认 Seccomp 配置
# 阻止危险的系统调用，如:
# - clone, unshare (创建新 namespace)
# - mount, umount (挂载操作)
# - reboot, swapon (系统操作)
# - ptrace (进程跟踪)
# - 内核模块加载

# 测试被阻止的系统调用
podman run --rm alpine unshare -r /bin/sh
# unshare: unshare failed: Operation not permitted
```

**自定义 Seccomp 配置**：

```bash
# 禁用 Seccomp（不推荐，仅测试用）
podman run --rm --security-opt seccomp=unconfined alpine unshare -r /bin/sh
# 成功

# 使用自定义 Seccomp 配置文件
cat > seccomp-custom.json <<'EOF'
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "defaultErrnoRet": 1,
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_AARCH64"
  ],
  "syscalls": [
    {
      "names": [
        "read", "write", "open", "close", "stat", "fstat",
        "lseek", "mmap", "mprotect", "munmap", "brk",
        "rt_sigaction", "rt_sigprocmask", "ioctl", "access",
        "exit", "exit_group", "wait4", "kill", "fcntl"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
EOF

podman run --rm --security-opt seccomp=seccomp-custom.json alpine ls
```

**审计 Seccomp 事件**：

```bash
# 启用审计模式（记录但不阻止）
cat > seccomp-audit.json <<'EOF'
{
  "defaultAction": "SCMP_ACT_LOG",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": []
}
EOF

# 运行容器并审计系统调用
podman run --rm --security-opt seccomp=seccomp-audit.json alpine sh -c 'ls /tmp'

# 查看审计日志
sudo ausearch -m SECCOMP -ts recent
```

**常见应用的 Seccomp 需求**：

```bash
# 示例：允许 strace（需要 ptrace 系统调用）
cat > seccomp-strace.json <<'EOF'
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "syscalls": [
    {
      "names": ["ptrace"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
EOF

podman run --rm --security-opt seccomp=seccomp-strace.json alpine strace ls
```

### 1.6 SELinux/AppArmor

强制访问控制 (MAC) 系统为容器提供额外的安全层。

**SELinux（RHEL/Fedora）**：

```bash
# 检查 SELinux 状态
getenforce
# Enforcing

# Podman 自动为容器分配 SELinux 标签
podman run --rm alpine cat /proc/self/attr/current
# system_u:system_r:container_t:s0:c123,c456

# container_t: 容器类型
# s0:c123,c456: MCS (Multi-Category Security) 标签，隔离容器

# 查看文件 SELinux 标签
podman run --rm -v /tmp/test:/data:Z alpine ls -Z /data
# container_file_t:s0:c123,c456
```

**SELinux 标签选项**：

```bash
# :z - 共享标签（多容器共享）
podman run -v /host/data:/data:z alpine ls /data

# :Z - 私有标签（仅此容器）
podman run -v /host/data:/data:Z alpine ls /data

# 自定义 SELinux 标签
podman run --security-opt label=level:s0:c100,c200 alpine cat /proc/self/attr/current

# 禁用 SELinux（不推荐）
podman run --security-opt label=disable alpine cat /proc/self/attr/current
```

**SELinux 故障排查**：

```bash
# 症状：Permission denied (但 Unix 权限正确)

# 1. 检查 SELinux 是否启用
getenforce

# 2. 查看 SELinux 拒绝日志
sudo ausearch -m AVC -ts recent | grep podman

# 3. 临时禁用 SELinux（测试用）
sudo setenforce 0
# 重新测试

# 4. 如果是 SELinux 问题，使用正确的标签
podman run -v /host/data:/data:Z alpine ls /data

# 5. 恢复 SELinux
sudo setenforce 1
```

**AppArmor（Ubuntu/Debian）**：

```bash
# 检查 AppArmor 状态
sudo aa-status

# Podman 默认 AppArmor 配置
# /etc/apparmor.d/containers/podman-default

# 查看容器的 AppArmor 配置
podman run --rm alpine cat /proc/self/attr/current
# podman-default (enforce)

# 使用自定义 AppArmor 配置
podman run --security-opt apparmor=my-profile alpine sh

# 禁用 AppArmor（不推荐）
podman run --security-opt apparmor=unconfined alpine sh
```

**创建自定义 AppArmor 配置**：

```bash
# /etc/apparmor.d/podman-custom
cat > /etc/apparmor.d/podman-custom <<'EOF'
#include <tunables/global>

profile podman-custom flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  
  # 允许网络
  network inet stream,
  network inet6 stream,
  
  # 允许读取 /etc
  /etc/** r,
  
  # 允许写入 /tmp
  /tmp/** rw,
  
  # 拒绝其他一切
  deny /** wx,
}
EOF

# 加载配置
sudo apparmor_parser -r /etc/apparmor.d/podman-custom

# 使用
podman run --security-opt apparmor=podman-custom alpine sh
```

**SELinux vs AppArmor 对比**：

| 特性 | SELinux | AppArmor |
|------|---------|----------|
| 发行版 | RHEL, Fedora, CentOS | Ubuntu, Debian, SUSE |
| 配置方式 | 类型和标签 | 路径规则 |
| 复杂度 | 高 | 中 |
| 细粒度 | 高 | 中 |
| 学习曲线 | 陡峭 | 平缓 |

## 2. 策略与供应链安全

### 2.1 policy.json 配置

`policy.json` 控制哪些镜像可以被拉取和运行。

**policy.json 位置**：

```bash
# 系统级策略
/etc/containers/policy.json

# 用户级策略（rootless）
$HOME/.config/containers/policy.json

# 查看当前策略
cat /etc/containers/policy.json
```

**策略类型**：

```json
{
  "default": [
    {
      "type": "insecureAcceptAnything"
    }
  ],
  "transports": {
    "docker": {
      "docker.io": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
        }
      ],
      "registry.access.redhat.com": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
        }
      ],
      "registry.local": [
        {
          "type": "insecureAcceptAnything"
        }
      ]
    }
  }
}
```

**策略类型说明**：

| 类型 | 说明 | 安全性 |
|------|------|--------|
| `insecureAcceptAnything` | 接受任何镜像（默认） | ❌ 低 |
| `reject` | 拒绝所有镜像 | ✅ 高（太严格） |
| `signedBy` | 要求镜像签名 | ✅ 高 |
| `sigstoreSigned` | Sigstore/Cosign 签名 | ✅ 高 |

**实用策略配置**：

```json
{
  "default": [
    {
      "type": "reject"
    }
  ],
  "transports": {
    "docker": {
      "docker.io/library": [
        {
          "type": "insecureAcceptAnything"
        }
      ],
      "quay.io/myorg": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/containers/myorg.gpg"
        }
      ],
      "registry.local": [
        {
          "type": "insecureAcceptAnything"
        }
      ]
    },
    "dir": [
      {
        "type": "insecureAcceptAnything"
      }
    ]
  }
}
```

**测试策略**：

```bash
# 配置严格策略
cat > /tmp/policy.json <<'EOF'
{
  "default": [{"type": "reject"}],
  "transports": {
    "docker": {
      "docker.io/library/alpine": [
        {"type": "insecureAcceptAnything"}
      ]
    }
  }
}
EOF

# 测试（使用自定义策略文件需要 root 权限或配置）
sudo podman pull --policy /tmp/policy.json alpine:latest
# 成功

sudo podman pull --policy /tmp/policy.json nginx:latest
# Error: Source image rejected: Running image docker://nginx:latest is rejected by policy.
```

### 2.2 镜像签名与验证

使用 GPG 或 Sigstore 签名镜像以确保完整性。

**GPG 签名（传统方法）**：

```bash
# 1. 生成 GPG 密钥
gpg --full-generate-key
# 选择 RSA, 4096 bits

# 2. 导出公钥
gpg --armor --export your-email@example.com > mykey.gpg

# 3. 配置签名 (需要 registry 支持)
# 编辑 /etc/containers/registries.d/registry.yaml
cat > /etc/containers/registries.d/myregistry.yaml <<'EOF'
docker:
  registry.local:
    sigstore: file:///var/lib/containers/sigstore
    sigstore-staging: file:///var/lib/containers/sigstore
EOF

# 4. 推送并签名镜像
podman push --sign-by your-email@example.com \
  localhost/myapp:1.0 \
  docker://registry.local/myapp:1.0

# 5. 验证镜像
podman pull --signature-policy /etc/containers/policy.json \
  docker://registry.local/myapp:1.0
```

**Sigstore/Cosign 签名（现代方法）**：

```bash
# 1. 安装 Cosign
# https://github.com/sigstore/cosign
curl -O -L https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign

# 2. 生成密钥对
cosign generate-key-pair
# 生成 cosign.key 和 cosign.pub

# 3. 签名镜像
cosign sign --key cosign.key registry.local/myapp:1.0

# 4. 验证镜像
cosign verify --key cosign.pub registry.local/myapp:1.0
```

**配置 policy.json 使用 Sigstore**：

```json
{
  "default": [{"type": "reject"}],
  "transports": {
    "docker": {
      "registry.local": [
        {
          "type": "sigstoreSigned",
          "keyPath": "/etc/containers/cosign.pub",
          "signedIdentity": {
            "type": "matchRepository"
          }
        }
      ]
    }
  }
}
```

**自动化签名流程（CI/CD）**：

```yaml
# GitLab CI 示例
sign-and-push:
  stage: deploy
  script:
    - podman build -t registry.local/myapp:${CI_COMMIT_SHA} .
    - podman push registry.local/myapp:${CI_COMMIT_SHA}
    - cosign sign --key ${COSIGN_KEY} registry.local/myapp:${CI_COMMIT_SHA}
  only:
    - main
```

### 2.3 SBOM（软件物料清单）

SBOM 记录镜像中的所有软件组件，便于追踪漏洞。

**生成 SBOM（使用 Syft）**：

```bash
# 安装 Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# 生成 SBOM
syft packages docker://nginx:alpine -o spdx-json > nginx-sbom.json

# 生成多种格式
syft packages docker://myapp:1.0 -o cyclonedx-json > sbom-cyclonedx.json
syft packages docker://myapp:1.0 -o spdx-json > sbom-spdx.json
syft packages docker://myapp:1.0 -o table

# 输出示例
NAME                VERSION      TYPE
nginx               1.24.0       apk
alpine-baselayout   3.4.3        apk
busybox             1.36.1       apk
...
```

**将 SBOM 附加到镜像（使用 Cosign）**：

```bash
# 生成 SBOM
syft packages docker://myapp:1.0 -o spdx-json > sbom.json

# 附加到镜像
cosign attach sbom --sbom sbom.json myapp:1.0

# 验证并下载 SBOM
cosign verify-attestation --key cosign.pub myapp:1.0
```

**集成到 CI/CD**：

```yaml
# GitHub Actions 示例
- name: Generate SBOM
  run: |
    syft packages docker://myapp:${{ github.sha }} -o spdx-json > sbom.json

- name: Upload SBOM
  uses: actions/upload-artifact@v3
  with:
    name: sbom
    path: sbom.json

- name: Attach SBOM to image
  run: |
    cosign attach sbom --sbom sbom.json myapp:${{ github.sha }}
```

### 2.4 漏洞扫描

定期扫描镜像以发现已知漏洞。

**使用 Trivy 扫描**：

```bash
# 安装 Trivy
sudo dnf install trivy  # Fedora
sudo apt-get install trivy  # Ubuntu

# 扫描镜像
trivy image nginx:alpine

# 输出示例
nginx:alpine (alpine 3.19.1)
===========================
Total: 0 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0)

# 仅显示高危和严重漏洞
trivy image --severity HIGH,CRITICAL nginx:alpine

# 输出 JSON 格式
trivy image -f json -o trivy-report.json nginx:alpine

# 扫描本地镜像
trivy image myapp:latest

# 扫描文件系统
trivy fs /path/to/project
```

**漏洞严重性分级**：

| 级别 | 说明 | 处理建议 |
|------|------|----------|
| CRITICAL | 严重漏洞 | 🔴 立即修复 |
| HIGH | 高危漏洞 | 🟠 优先修复 |
| MEDIUM | 中危漏洞 | 🟡 计划修复 |
| LOW | 低危漏洞 | ⚪ 可选修复 |
| UNKNOWN | 未知 | 评估后决定 |

**CI/CD 集成**：

```yaml
# GitLab CI 示例
security-scan:
  stage: test
  image: aquasec/trivy:latest
  script:
    - trivy image --exit-code 1 --severity CRITICAL,HIGH myapp:${CI_COMMIT_SHA}
  allow_failure: false  # 有高危漏洞则失败
```

**使用 Grype 扫描**：

```bash
# 安装 Grype (Anchore)
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# 扫描镜像
grype docker://nginx:alpine

# 仅严重漏洞
grype docker://nginx:alpine --fail-on critical

# 输出 JSON
grype docker://nginx:alpine -o json > grype-report.json
```

**持续监控**：

```bash
# 定期扫描运行中的容器
#!/bin/bash
# scan-running-containers.sh

for image in $(podman ps --format '{{.Image}}' | sort -u); do
  echo "扫描: $image"
  trivy image --severity HIGH,CRITICAL "$image"
done
```

### 2.5 镜像来源控制

限制可以拉取镜像的仓库。

**配置可信仓库**：

```bash
# /etc/containers/registries.conf
cat > /etc/containers/registries.conf <<'EOF'
[registries.search]
registries = ["docker.io", "quay.io", "registry.local"]

[registries.insecure]
registries = ["registry.local"]

[registries.block]
registries = ["untrusted-registry.example.com"]

[[registry]]
location = "docker.io"
blocked = false

[[registry]]
location = "docker.io/library"
blocked = false

[[registry]]
location = "quay.io/myorg"
blocked = false

[[registry.mirror]]
location = "mirror.local/docker.io"
insecure = false
EOF
```

**镜像仓库镜像/代理**：

```bash
# 配置镜像加速
# /etc/containers/registries.conf
[[registry]]
prefix = "docker.io"
location = "docker.io"

[[registry.mirror]]
location = "mirror.example.com"
insecure = false

# 测试
podman pull nginx:alpine
# 实际从 mirror.example.com 拉取
```

**私有仓库认证**：

```bash
# 登录私有仓库
podman login registry.local
# Username: admin
# Password: ********

# 凭证存储在
cat ~/.config/containers/auth.json
# 或 /run/user/1000/containers/auth.json

# 退出登录
podman logout registry.local
```

## 3. 运行时与网络安全

### 3.1 只读根文件系统

只读根文件系统防止容器内的恶意修改。

**启用只读根文件系统**：

```bash
# 基本只读根
podman run --rm --read-only alpine touch /test
# touch: /test: Read-only file system

# 只读根 + tmpfs 写入点
podman run --rm \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --tmpfs /var/run:rw,noexec,nosuid,size=32m \
  alpine sh -c '
    touch /tmp/test && echo "Success"
    touch /var/run/test && echo "Success"
    touch /etc/test  # 失败
  '
```

**应用示例**：

```bash
# Nginx 只读根
podman run -d \
  --name nginx-secure \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --tmpfs /var/run:rw,noexec,nosuid,size=32m \
  --tmpfs /var/cache/nginx:rw,noexec,nosuid,size=128m \
  -p 8080:80 \
  nginx:alpine

# 应用容器只读根
podman run -d \
  --name app \
  --read-only \
  --tmpfs /tmp:size=100m \
  -v app-data:/app/data:rw \
  myapp:latest
```

**检测可写路径**：

```bash
# 列出容器内的可写路径
podman exec container mount | grep -v "ro,"

# 或
podman exec container df -h | grep -v "ro"
```

### 3.2 最小权限原则

以非 root 用户运行容器进程。

**使用非 root 用户**：

```dockerfile
# Dockerfile
FROM alpine:3.20

# 创建非 root 用户
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# 切换用户
USER appuser

# 应用代码
WORKDIR /app
COPY --chown=appuser:appuser . /app

CMD ["./myapp"]
```

**运行时指定用户**：

```bash
# 指定 UID
podman run --user 1000:1000 alpine id
# uid=1000 gid=1000

# 指定用户名（如果镜像中存在）
podman run --user appuser alpine id

# Rootless 模式下的 UID 映射
podman unshare cat /proc/self/uid_map
# 容器内 UID 1000 → 主机 UID 101000
```

**限制进程**：

```bash
# 限制 CPU
podman run --cpus=0.5 alpine sh

# 限制内存
podman run --memory=256m alpine sh

# 限制 PIDs（防止 fork 炸弹）
podman run --pids-limit=100 alpine sh

# 组合限制
podman run \
  --cpus=0.5 \
  --memory=256m \
  --pids-limit=100 \
  --read-only \
  --user 1000:1000 \
  alpine sh
```

### 3.3 端口暴露控制

最小化暴露的端口和服务。

**仅暴露必要端口**：

```bash
# ❌ 不好：暴露所有端口
podman run -P nginx:alpine

# ✅ 好：仅暴露必要端口
podman run -p 127.0.0.1:8080:80 nginx:alpine

# ✅ 更好：指定协议
podman run -p 127.0.0.1:8080:80/tcp nginx:alpine
```

**端口扫描防护**：

```bash
# 检查容器暴露的端口
podman port container

# 使用防火墙限制
sudo firewall-cmd --add-rich-rule='
  rule family="ipv4"
  source address="10.0.0.0/8"
  port port="8080" protocol="tcp" accept
'
```

**使用反向代理**：

```bash
# 不直接暴露应用端口，通过反向代理
podman run -d --name app --network backend-net myapp:latest
podman run -d --name proxy \
  --network backend-net \
  --network frontend-net \
  -p 443:443 \
  nginx-proxy:latest
```

### 3.4 网络隔离与策略

隔离容器网络以减少攻击面。

**创建隔离网络**：

```bash
# 创建内部网络（无外网访问）
podman network create \
  --internal \
  --subnet 10.89.0.0/24 \
  backend-net

# 运行容器
podman run -d --network backend-net postgres:alpine
podman run -d --network backend-net redis:alpine

# 这些容器之间可以通信，但无法访问外网
```

**多网络架构**：

```bash
# 前端网络（外网可访问）
podman network create frontend-net

# 后端网络（内部）
podman network create --internal backend-net

# 数据库网络（内部）
podman network create --internal db-net

# Web 服务器：连接前端和后端网络
podman run -d \
  --name web \
  --network frontend-net \
  --network backend-net \
  -p 443:443 \
  nginx:alpine

# 应用服务器：连接后端和数据库网络
podman run -d \
  --name app \
  --network backend-net \
  --network db-net \
  myapp:latest

# 数据库：仅连接数据库网络
podman run -d \
  --name db \
  --network db-net \
  postgres:alpine
```

**使用 Pod 隔离**：

```bash
# 创建 Pod（内部共享网络）
podman pod create --name myapp-pod -p 8080:80

# 添加容器到 Pod
podman run -d --pod myapp-pod --name web nginx:alpine
podman run -d --pod myapp-pod --name app myapp:latest

# Pod 内容器共享 localhost
podman exec web curl localhost:3000  # 访问 app 容器
```

**网络策略（使用 nftables/iptables）**：

```bash
# 限制容器出站流量
sudo nft add table ip podman_filter
sudo nft add chain ip podman_filter output '{ type filter hook output priority 0; }'
sudo nft add rule ip podman_filter output meta skuid 100000-165536 ip daddr != { 10.0.0.0/8, 172.16.0.0/12 } drop
```

### 3.5 资源限制

防止资源耗尽攻击。

**CPU 限制**：

```bash
# 限制 CPU 配额
podman run --cpus=0.5 alpine sh  # 最多使用 50% CPU

# CPU 共享权重
podman run --cpu-shares=512 alpine sh  # 默认 1024

# 指定 CPU 核心
podman run --cpuset-cpus=0,1 alpine sh  # 仅使用 CPU 0 和 1
```

**内存限制**：

```bash
# 限制内存
podman run --memory=256m alpine sh

# 内存 + Swap
podman run --memory=256m --memory-swap=512m alpine sh

# 禁用 Swap
podman run --memory=256m --memory-swap=256m alpine sh

# 内存预留
podman run --memory=512m --memory-reservation=256m alpine sh
```

**磁盘 IO 限制**：

```bash
# 限制读写速度
podman run --device-read-bps /dev/sda:10mb alpine sh
podman run --device-write-bps /dev/sda:10mb alpine sh

# 限制 IOPS
podman run --device-read-iops /dev/sda:100 alpine sh
```

**进程数限制**：

```bash
# 限制进程数（防止 fork 炸弹）
podman run --pids-limit=50 alpine sh

# 测试 fork 炸弹防护
podman run --pids-limit=10 alpine sh -c ':(){:|:&};:'
# 达到限制后无法创建新进程
```

## 4. 沙箱运行时与隔离增强

### 4.1 容器运行时选择

Podman 支持多种 OCI 运行时。

**可用运行时**：

| 运行时 | 类型 | 隔离级别 | 性能 | 推荐场景 |
|--------|------|----------|------|----------|
| **crun** | 原生 | Linux namespace | 最快 | 默认推荐 |
| **runc** | 原生 | Linux namespace | 快 | 兼容性 |
| **kata-runtime** | VM 沙箱 | 虚拟机 | 中 | 多租户 |
| **runsc** (gVisor) | 用户空间内核 | 用户空间 | 慢 | 不可信代码 |

**查看和切换运行时**：

```bash
# 查看默认运行时
podman info | grep -A 5 "runtime:"

# 列出可用运行时
podman info | grep -A 10 "runtimes:"

# 使用特定运行时
podman run --runtime=crun alpine sh
podman run --runtime=runc alpine sh

# 配置默认运行时
# ~/.config/containers/containers.conf
[engine]
runtime = "crun"
```

**crun vs runc**：

```bash
# 性能对比
time podman run --runtime=crun --rm alpine echo "test"
# real    0m0.123s

time podman run --runtime=runc --rm alpine echo "test"
# real    0m0.156s

# crun 优势:
# - 更快的启动时间
# - 更好的 cgroups v2 支持
# - 更小的内存占用
# - C 语言实现（vs runc 的 Go）
```

### 4.2 Kata Containers

Kata Containers 使用轻量级虚拟机提供强隔离。

**安装 Kata Containers**：

```bash
# Fedora/RHEL
sudo dnf install kata-runtime kata-containers

# Ubuntu
sudo apt-get install kata-runtime

# 验证安装
kata-runtime --version
```

**配置 Podman 使用 Kata**：

```bash
# ~/.config/containers/containers.conf
[engine.runtimes]
kata = [
  "/usr/bin/kata-runtime"
]

# 测试
podman run --runtime=kata alpine uname -r
# 显示 Kata VM 内核版本（不同于主机）
```

**Kata 特性**：

```bash
# 每个容器运行在独立的轻量级 VM 中
podman run --runtime=kata alpine sh

# 查看 Kata VM 进程
ps aux | grep qemu

# Kata 提供：
# - 独立的内核
# - 硬件虚拟化隔离
# - 更强的安全边界
```

**适用场景**：

- ✅ 多租户环境
- ✅ 运行不可信代码
- ✅ 需要内核级隔离
- ❌ 性能敏感应用
- ❌ 需要主机设备访问

### 4.3 gVisor

gVisor 实现用户空间内核，拦截系统调用。

**安装 gVisor**：

```bash
# 下载 runsc
curl -fsSL https://storage.googleapis.com/gvisor/releases/release/latest/x86_64/runsc -o runsc
curl -fsSL https://storage.googleapis.com/gvisor/releases/release/latest/x86_64/runsc.sha512 -o runsc.sha512
sha512sum -c runsc.sha512

# 安装
chmod +x runsc
sudo mv runsc /usr/local/bin/

# 配置 Podman
# ~/.config/containers/containers.conf
[engine.runtimes]
runsc = [
  "/usr/local/bin/runsc",
  "--platform=ptrace"
]
```

**使用 gVisor**：

```bash
# 运行容器
podman run --runtime=runsc alpine sh

# gVisor 拦截系统调用
podman run --runtime=runsc alpine strace ls
# 会看到 gVisor 的系统调用拦截
```

**gVisor 特性**：

```bash
# 用户空间内核
# - 拦截所有系统调用
# - 仅有限的系统调用直接到主机内核
# - 减少攻击面

# 查看支持的系统调用
runsc help syscalls

# 限制：
# - 不支持所有 Linux 特性
# - 性能开销较大
# - 某些应用可能不兼容
```

### 4.4 性能与安全权衡

**性能对比**：

| 运行时 | 启动时间 | 运行时开销 | 内存占用 | 安全性 |
|--------|----------|------------|----------|--------|
| crun/runc | 最快 (~100ms) | 几乎无 | 最小 | 中 |
| Kata | 慢 (~500ms) | 中等 | 高 (~100MB/VM) | 高 |
| gVisor | 中 (~200ms) | 高 (~20-30%) | 中 | 高 |

**选择决策树**：

```text
需要最强隔离（内核级）？
  ├─ 是 → Kata Containers
  └─ 否 ↓

运行不可信代码？
  ├─ 是 → gVisor
  └─ 否 ↓

需要最佳性能？
  ├─ 是 → crun/runc + rootless + seccomp + SELinux
  └─ 否 → crun (默认)
```

**混合使用**：

```bash
# 不同安全级别的容器使用不同运行时

# 普通应用：crun
podman run --runtime=crun webapp:latest

# 用户提交的代码：gVisor
podman run --runtime=runsc user-code:latest

# 多租户环境：Kata
podman run --runtime=kata tenant-app:latest
```

## 5. 安全基线与合规

### 5.1 容器加固清单

**镜像构建安全**：

- ✅ 使用最小基础镜像（alpine, distroless）
- ✅ 多阶段构建，仅保留运行时依赖
- ✅ 定期更新基础镜像
- ✅ 扫描镜像漏洞
- ✅ 不在镜像中包含秘密
- ✅ 使用非 root 用户
- ✅ 移除不必要的工具（shell, curl, wget）

**容器运行安全**：

- ✅ Rootless 模式
- ✅ 只读根文件系统
- ✅ 最小 capabilities
- ✅ Seccomp/SELinux/AppArmor
- ✅ 资源限制
- ✅ 网络隔离
- ✅ 禁用特权模式

**安全配置示例**：

```bash
# 安全加固的容器
podman run -d \
  --name secure-app \
  --read-only \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt no-new-privileges=true \
  --user 1000:1000 \
  --cpus=0.5 \
  --memory=256m \
  --pids-limit=100 \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --network isolated-net \
  -p 127.0.0.1:8080:8080 \
  myapp:latest
```

### 5.2 日志与审计

**启用日志**：

```bash
# 查看容器日志
podman logs container

# 实时跟踪
podman logs -f container

# 查看最近 100 行
podman logs --tail 100 container

# 配置日志驱动
podman run -d \
  --log-driver=journald \
  --log-opt tag="myapp" \
  myapp:latest

# 查看 journald 日志
journalctl CONTAINER_NAME=myapp
```

**系统审计**：

```bash
# 启用 auditd
sudo systemctl enable --now auditd

# 添加 Podman 审计规则
sudo auditctl -w /usr/bin/podman -p x -k podman_exec
sudo auditctl -w /etc/containers/ -p wa -k containers_config

# 查看审计日志
sudo ausearch -k podman_exec
sudo ausearch -k containers_config

# 持久化规则
echo "-w /usr/bin/podman -p x -k podman_exec" | \
  sudo tee -a /etc/audit/rules.d/podman.rules
```

**集中日志收集**：

```bash
# 使用 Fluentd/Fluentbit
podman run -d \
  --name fluentbit \
  -v /var/log/containers:/var/log/containers:ro \
  -v /etc/fluent-bit:/fluent-bit/etc \
  fluent/fluent-bit:latest

# 配置 fluent-bit.conf
[INPUT]
    Name tail
    Path /var/log/containers/*.log
    Parser json

[OUTPUT]
    Name es
    Match *
    Host elasticsearch.local
    Port 9200
```

### 5.3 秘密管理

**避免硬编码秘密**：

```bash
# ❌ 不好：硬编码
podman run -e DB_PASSWORD=mysecret postgres:alpine

# ✅ 好：使用环境文件
cat > secrets.env <<'EOF'
DB_PASSWORD=mysecret
API_KEY=abcd1234
EOF
chmod 600 secrets.env

podman run --env-file secrets.env postgres:alpine

# ✅ 更好：使用 Podman secrets
podman secret create db_password -
# 输入密码后按 Ctrl+D

podman run -d \
  --secret db_password,type=env,target=DB_PASSWORD \
  postgres:alpine
```

**Kubernetes Secrets（Podman play kube）**：

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: bXlzZWNyZXQ=  # base64编码
---
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
```

```bash
# 使用
podman play kube secrets.yaml
```

**外部秘密管理**：

```bash
# 集成 Vault
vault kv get -field=password secret/db | \
  podman secret create db_password -

# 或使用 --env
podman run -d \
  -e DB_PASSWORD=$(vault kv get -field=password secret/db) \
  postgres:alpine
```

### 5.4 合规性检查

**CIS Docker Benchmark**：

```bash
# 安装 Docker Bench Security
git clone https://github.com/docker/docker-bench-security.git
cd docker-bench-security

# 运行（需要适配 Podman）
sudo sh docker-bench-security.sh
```

**使用 OpenSCAP**：

```bash
# 安装 OpenSCAP
sudo dnf install openscap-scanner scap-security-guide

# 扫描容器镜像
oscap-podman image nginx:alpine cve \
  --format=html \
  --output=report.html

# 扫描运行中的容器
oscap-podman container mycontainer cve \
  --format=html \
  --output=container-report.html
```

## 6. 故障与应急响应

### 6.1 容器逃逸检测

**监控逃逸迹象**：

```bash
# 检查异常进程
ps aux | grep -E "runc|crun|podman" | grep -v grep

# 检查可疑文件访问
sudo ausearch -m path -ts recent | grep /var/lib/containers

# 检查网络连接
ss -tulpn | grep podman

# 使用 Falco 检测
# https://falco.org/
```

**常见逃逸迹象**：

1. 容器内出现主机进程
2. 容器内访问主机文件系统
3. 容器内加载内核模块
4. 容器内修改 cgroup 配置
5. 异常的 setuid/setgid 调用

**检测脚本**：

```bash
#!/bin/bash
# detect-escape.sh

# 检查容器是否可以访问主机进程
podman exec container ps aux | grep -v "^root.*[podman]" | wc -l

# 检查挂载点
podman exec container mount | grep -E "/(proc|sys|dev)$"

# 检查 capabilities
podman exec container sh -c 'cat /proc/self/status | grep Cap'

# 检查 Seccomp
podman exec container sh -c 'cat /proc/self/status | grep Seccomp'
# Seccomp: 0 = 已禁用 (危险!)
# Seccomp: 2 = 已过滤 (安全)
```

### 6.2 事件响应流程

**响应步骤**：

1. **检测** - 发现异常
2. **隔离** - 暂停/停止容器
3. **分析** - 取证和根因分析
4. **清除** - 移除威胁
5. **恢复** - 从已知良好状态恢复
6. **总结** - 事后分析和改进

**隔离容器**：

```bash
# 暂停容器（冻结所有进程）
podman pause suspicious-container

# 断开网络
podman network disconnect bridge suspicious-container

# 停止容器
podman stop suspicious-container

# 如果严重，直接 kill
podman kill suspicious-container
```

### 6.3 取证与分析

**保存容器状态**：

```bash
# 导出容器文件系统
podman export suspicious-container > container-forensics.tar

# 保存容器日志
podman logs suspicious-container > container.log 2>&1

# 保存容器配置
podman inspect suspicious-container > container-inspect.json

# 提交为镜像（保留状态）
podman commit suspicious-container evidence:$(date +%Y%m%d-%H%M%S)
```

**分析工具**：

```bash
# 分析文件系统
tar -tf container-forensics.tar | grep -E "\.(sh|py|elf)$"

# 检查最近修改的文件
podman diff suspicious-container

# 检查进程
podman top suspicious-container

# 检查网络连接
podman exec suspicious-container netstat -tulpn
```

### 6.4 镜像回滚

**回滚到已知良好版本**：

```bash
# 停止受影响的容器
podman stop myapp

# 拉取已知良好版本
podman pull myapp:1.0-known-good

# 重新标记
podman tag myapp:1.0-known-good myapp:latest

# 重新部署
podman run -d --name myapp myapp:latest

# 或使用之前的镜像ID
podman images myapp
# 找到良好版本的 IMAGE ID

podman run -d --name myapp <good-image-id>
```

**预防性备份**：

```bash
# 定期标记稳定版本
podman tag myapp:latest myapp:stable-$(date +%Y%m%d)

# 定期导出镜像
podman save myapp:stable-20250118 | gzip > myapp-stable-20250118.tar.gz

# 保存到安全位置
rsync -av myapp-stable-*.tar.gz backup-server:/backups/
```

## 7. 实操示例

### 7.1 安全容器配置

**生产级安全配置**：

```bash
#!/bin/bash
# secure-container.sh - 安全容器启动脚本

podman run -d \
  --name secure-webapp \
  \
  `# 基础安全` \
  --read-only \
  --user 1000:1000 \
  --security-opt no-new-privileges=true \
  \
  `# Capabilities` \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --cap-add=CHOWN \
  --cap-add=SETUID \
  --cap-add=SETGID \
  \
  `# Seccomp/SELinux` \
  --security-opt seccomp=seccomp-profile.json \
  --security-opt label=type:container_webapp_t \
  \
  `# 资源限制` \
  --cpus=1.0 \
  --memory=512m \
  --memory-swap=512m \
  --pids-limit=100 \
  \
  `# tmpfs 写入点` \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --tmpfs /var/run:rw,noexec,nosuid,size=50m \
  \
  `# 数据卷` \
  -v webapp-data:/app/data:rw,Z \
  -v webapp-logs:/app/logs:rw,Z \
  \
  `# 网络` \
  --network isolated-net \
  -p 127.0.0.1:8080:8080 \
  \
  `# 日志` \
  --log-driver=journald \
  --log-opt tag="webapp" \
  \
  `# 镜像` \
  webapp:1.0-secure
```

### 7.2 镜像签名流程

**完整签名工作流**：

```bash
#!/bin/bash
# sign-and-push.sh

IMAGE="registry.local/myapp"
TAG="1.0"
FULL_IMAGE="$IMAGE:$TAG"

# 1. 构建镜像
echo "构建镜像..."
podman build -t $FULL_IMAGE .

# 2. 扫描漏洞
echo "扫描漏洞..."
trivy image --exit-code 1 --severity CRITICAL,HIGH $FULL_IMAGE
if [ $? -ne 0 ]; then
  echo "发现高危漏洞，中止发布"
  exit 1
fi

# 3. 生成 SBOM
echo "生成 SBOM..."
syft packages $FULL_IMAGE -o spdx-json > sbom.json

# 4. 推送镜像
echo "推送镜像..."
podman push $FULL_IMAGE

# 5. 签名镜像
echo "签名镜像..."
cosign sign --key cosign.key $FULL_IMAGE

# 6. 附加 SBOM
echo "附加 SBOM..."
cosign attach sbom --sbom sbom.json $FULL_IMAGE

# 7. 签名 SBOM
echo "签名 SBOM..."
cosign sign --key cosign.key --attachment sbom $FULL_IMAGE

echo "完成！镜像已签名并发布：$FULL_IMAGE"
```

### 7.3 漏洞扫描集成

**CI/CD 集成示例**：

```yaml
# .gitlab-ci.yml
stages:
  - build
  - scan
  - sign
  - deploy

build:
  stage: build
  script:
    - podman build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - podman push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

security-scan:
  stage: scan
  image: aquasec/trivy:latest
  script:
    - trivy image --exit-code 0 --severity LOW,MEDIUM $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - trivy image --exit-code 1 --severity HIGH,CRITICAL $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  artifacts:
    reports:
      container_scanning: trivy-report.json

sign-image:
  stage: sign
  script:
    - cosign sign --key $COSIGN_KEY $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main

deploy-production:
  stage: deploy
  script:
    - cosign verify --key $COSIGN_PUB $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - podman pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - podman tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - # 部署到生产环境...
  only:
    - main
  when: manual
```

## 8. 故障清单与排查

**问题1：策略拒绝（Policy denied）**:

```bash
# 症状
podman pull nginx:latest
# Error: Source image rejected: Running image is rejected by policy

# 排查
# 1. 检查策略配置
cat /etc/containers/policy.json

# 2. 检查镜像签名
skopeo inspect --raw docker://nginx:latest | jq .

# 3. 检查签名验证
podman pull --signature-policy=/tmp/test-policy.json nginx:latest

# 解决方案
# A. 修改策略允许该镜像
# B. 对镜像进行签名
# C. 使用 insecureAcceptAnything (不推荐生产环境)
```

**问题2：Rootless 权限异常**:

```bash
# 症状
Error: cannot set up namespace using newuidmap

# 排查
# 1. 检查 subuid/subgid
cat /etc/subuid | grep $USER
cat /etc/subgid | grep $USER

# 2. 检查 /etc/subuid 权限
ls -l /etc/subuid /etc/subgid

# 3. 检查 newuidmap/newgidmap
which newuidmap newgidmap
ls -l /usr/bin/newuidmap /usr/bin/newgidmap
# 应该有 setuid 位

# 解决方案
# A. 添加 subuid/subgid
sudo usermod --add-subuids 100000-165535 $USER
sudo usermod --add-subgids 100000-165535 $USER

# B. 重新登录
exit
```

**问题3：SELinux 阻止**:

```bash
# 症状
Permission denied (但 Unix 权限正确)

# 排查
# 1. 检查 SELinux 状态
getenforce

# 2. 查看 AVC 拒绝
sudo ausearch -m AVC -ts recent | grep podman

# 3. 查看文件标签
ls -Z /host/path

# 解决方案
# A. 使用正确的标签
podman run -v /host/path:/data:Z alpine ls /data

# B. 临时禁用SELinux测试
sudo setenforce 0  # 仅测试！

# C. 创建自定义 SELinux 策略
sudo audit2allow -a -M mypolicy
sudo semodule -i mypolicy.pp
```

**问题4：容器无法绑定低端口（Rootless）**:

```bash
# 症状
Error: cannot listen on privileged port 80

# 解决方案
# A. 使用高端口映射
podman run -p 8080:80 nginx:alpine
# 外部访问 8080，容器内监听 80

# B. 使用 CAP_NET_BIND_SERVICE
podman run --cap-add=NET_BIND_SERVICE -p 80:80 nginx:alpine

# C. 配置 sysctl (需要 root)
sudo sysctl net.ipv4.ip_unprivileged_port_start=80

# D. 使用反向代理
# Rootful nginx 监听 80 → Rootless 容器
```

**问题5：镜像扫描发现漏洞**:

```bash
# 症状
trivy image myapp:latest
# CRITICAL: CVE-2024-xxxxx

# 排查与解决
# 1. 更新基础镜像
FROM alpine:3.19  →  FROM alpine:3.20

# 2. 更新依赖包
RUN apk upgrade --no-cache

# 3. 使用 distroless 镜像
FROM gcr.io/distroless/static-debian12

# 4. 如果无法修复，评估风险并记录
echo "CVE-2024-xxxxx: 已评估，不影响我们的使用场景" > security-notes.txt
```

## 9. FAQ

**Q1: rootless 和 rootful 如何选择？**

A:

- **Rootless**: 开发、测试、多租户、不可信代码
- **Rootful**: 生产环境、性能敏感、需要特权操作

**Q2: 如何让 rootless 容器绑定低端口？**

A: 三种方法：

1. 使用端口映射 (`-p 8080:80`)
2. 添加 `CAP_NET_BIND_SERVICE` capability
3. 配置 `net.ipv4.ip_unprivileged_port_start`

**Q3: crun vs runc，如何选择？**

A:

- **crun**: 默认推荐，更快，更好的 cgroups v2 支持
- **runc**: 更成熟，更广泛的测试

大多数情况选 crun。

**Q4: 何时使用 Kata/gVisor？**

A:

- **Kata**: 多租户、需要内核级隔离、安全优先
- **gVisor**: 运行不可信代码、需要系统调用过滤

普通应用使用 crun/runc + rootless + seccomp 已足够安全。

**Q5: 如何检测容器是否被入侵？**

A: 监控：

1. 异常的系统调用（ausearch）
2. 意外的文件修改（podman diff）
3. 异常网络连接（netstat）
4. 高资源使用（podman stats）
5. 使用 Falco 等安全工具

**Q6: policy.json 的 insecureAcceptAnything 安全吗？**

A:
❌ **不安全**！仅用于开发/测试。

生产环境应使用 `signedBy` 或 `sigstoreSigned`。

**Q7: 如何保护容器中的秘密？**

A:

1. 使用 `podman secret`
2. 使用外部秘密管理（Vault, AWS Secrets Manager）
3. 不在镜像中包含秘密
4. 使用环境变量（但不要记录）
5. 挂载秘密文件（只读，限制权限）

**Q8: SELinux vs AppArmor？**

A: 取决于发行版：

- **RHEL/Fedora/CentOS**: SELinux（默认）
- **Ubuntu/Debian**: AppArmor（默认）

都能提供有效的 MAC，使用系统默认的即可。

**Q9: 如何审计容器操作？**

A:

1. 启用 `auditd`
2. 添加审计规则监控 `/usr/bin/podman`
3. 启用容器日志（journald/syslog）
4. 使用集中日志收集（Fluentd, Elasticsearch）
5. 监控 `/etc/containers/` 配置变更

**Q10: 最小权限的容器应该是什么样？**

A:

```bash
podman run -d \
  --read-only \                      # 只读根
  --cap-drop=ALL \                   # 移除所有 capabilities
  --security-opt no-new-privileges \ # 禁止提权
  --user 1000:1000 \                 # 非 root 用户
  --cpus=0.5 --memory=256m \         # 资源限制
  --pids-limit=50 \                  # 进程限制
  --tmpfs /tmp:noexec,nosuid \       # 临时文件
  --network none \                   # 无网络（如不需要）
  myapp:latest
```

## 10. 基线模板（建议）

**生产环境安全基线**：

```bash
# /etc/containers/containers.conf
[containers]
# 默认 capabilities
default_capabilities = [
  "CHOWN",
  "DAC_OVERRIDE",
  "FOWNER",
  "FSETID",
  "KILL",
  "NET_BIND_SERVICE",
  "SETFCAP",
  "SETGID",
  "SETPCAP",
  "SETUID",
  "SYS_CHROOT"
]

# 禁止特权容器
default_sysctls = []

# 默认 ulimit
default_ulimits = [
  "nofile=1024:2048",
  "nproc=1024:2048"
]

# 默认 seccomp
seccomp_profile = "/usr/share/containers/seccomp.json"

# PID 限制
pids_limit = 2048

# 日志
log_driver = "journald"

[engine]
# 运行时
runtime = "crun"

# Rootless
rootless_networking = "slirp4netns"

[engine.runtimes]
crun = [
  "/usr/bin/crun"
]

kata = [
  "/usr/bin/kata-runtime"
]

runsc = [
  "/usr/local/bin/runsc"
]
```

**安全策略模板**：

```json
{
  "default": [
    {
      "type": "reject"
    }
  ],
  "transports": {
    "docker": {
      "docker.io/library": [
        {
          "type": "insecureAcceptAnything"
        }
      ],
      "quay.io/organization": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/containers/org.gpg"
        }
      ],
      "registry.local": [
        {
          "type": "sigstoreSigned",
          "keyPath": "/etc/containers/cosign.pub"
        }
      ]
    }
  }
}
```

**部署检查清单**：

容器镜像:

- [ ] 使用最小基础镜像
- [ ] 多阶段构建
- [ ] 非 root 用户
- [ ] 无秘密信息
- [ ] 已签名
- [ ] 已扫描漏洞
- [ ] 生成 SBOM

容器运行:

- [ ] Rootless 模式（或有明确理由使用 rootful）
- [ ] 只读根文件系统
- [ ] 最小 capabilities
- [ ] Seccomp 启用
- [ ] SELinux/AppArmor 启用
- [ ] 资源限制（CPU/内存/PIDs）
- [ ] 网络隔离
- [ ] 端口最小化
- [ ] no-new-privileges

监控与审计:

- [ ] 日志收集
- [ ] 审计规则
- [ ] 漏洞扫描
- [ ] 合规检查
- [ ] 事件响应流程
- [ ] 定期安全评估

**自动化安全检查脚本**：

```bash
#!/bin/bash
# security-check.sh - 容器安全检查

CONTAINER=$1

echo "=== 安全检查: $CONTAINER ==="

# 1. 检查运行用户
USER=$(podman inspect $CONTAINER | jq -r '.[0].Config.User')
if [ "$USER" = "root" ] || [ -z "$USER" ]; then
  echo "❌ 以 root 用户运行"
else
  echo "✅ 非 root 用户: $USER"
fi

# 2. 检查只读根
READONLY=$(podman inspect $CONTAINER | jq -r '.[0].HostConfig.ReadonlyRootfs')
if [ "$READONLY" = "true" ]; then
  echo "✅ 只读根文件系统"
else
  echo "❌ 可写根文件系统"
fi

# 3. 检查 Capabilities
CAPS=$(podman inspect $CONTAINER | jq -r '.[0].EffectiveCaps[]' | wc -l)
echo "⚠️  Capabilities: $CAPS (越少越好)"

# 4. 检查特权模式
PRIVILEGED=$(podman inspect $CONTAINER | jq -r '.[0].HostConfig.Privileged')
if [ "$PRIVILEGED" = "true" ]; then
  echo "🔴 特权模式（危险！）"
else
  echo "✅ 非特权模式"
fi

# 5. 检查 Seccomp
SECCOMP=$(podman exec $CONTAINER grep Seccomp /proc/self/status | awk '{print $2}')
if [ "$SECCOMP" = "2" ]; then
  echo "✅ Seccomp 已启用"
else
  echo "❌ Seccomp 未启用"
fi

# 6. 检查资源限制
MEMORY=$(podman inspect $CONTAINER | jq -r '.[0].HostConfig.Memory')
CPU=$(podman inspect $CONTAINER | jq -r '.[0].HostConfig.NanoCpus')
if [ "$MEMORY" != "0" ] && [ "$CPU" != "0" ]; then
  echo "✅ 资源限制已设置"
else
  echo "⚠️  未设置资源限制"
fi

echo "=== 检查完成 ==="
```

---

**相关资源**：

- [Podman 安全文档](https://docs.podman.io/en/latest/markdown/podman-security.html)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST Application Container Security Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
- [Sigstore](https://www.sigstore.dev/)
- [Trivy](https://github.com/aquasecurity/trivy)
- [Falco](https://falco.org/)
- [Kata Containers](https://katacontainers.io/)
- [gVisor](https://gvisor.dev/)
