# Podman网络技术

> 版本锚点（新增）：本文档基于 Podman 5.0+、Netavark 1.9+ 和 Aardvark-DNS 1.9+ 版本编写，版本信息统一参考《2025年技术标准最终对齐报告.md》。

## 目录

- [Podman网络技术](#podman网络技术)
  - [目录](#目录)
  - [1. 网络后端与模式](#1-网络后端与模式)
    - [1.1 网络模式概述](#11-网络模式概述)
    - [1.2 Bridge 模式](#12-bridge-模式)
    - [1.3 Host 模式](#13-host-模式)
    - [1.4 None 模式](#14-none-模式)
    - [1.5 Pod 网络](#15-pod-网络)
    - [1.6 与 Docker 差异](#16-与-docker-差异)
  - [2. netavark/aardvark-dns](#2-netavarkaardvark-dns)
    - [2.1 Netavark 架构](#21-netavark-架构)
    - [2.2 Aardvark-DNS 服务](#22-aardvark-dns-服务)
    - [2.3 与 CNI 对比](#23-与-cni-对比)
    - [2.4 网络配置](#24-网络配置)
  - [3. rootless 网络：slirp4netns/pasta](#3-rootless-网络slirp4netnspasta)
    - [3.1 Rootless 网络架构](#31-rootless-网络架构)
    - [3.2 slirp4netns](#32-slirp4netns)
    - [3.3 pasta (Passt)](#33-pasta-passt)
    - [3.4 性能对比与选择](#34-性能对比与选择)
  - [4. IPv6 与高级特性](#4-ipv6-与高级特性)
    - [4.1 IPv6 配置](#41-ipv6-配置)
    - [4.2 双栈网络](#42-双栈网络)
    - [4.3 macvlan 和 ipvlan](#43-macvlan-和-ipvlan)
    - [4.4 VLAN 网络](#44-vlan-网络)
    - [4.5 网络策略](#45-网络策略)
  - [5. 故障诊断与调优](#5-故障诊断与调优)
    - [5.1 网络诊断工具](#51-网络诊断工具)
    - [5.2 防火墙配置](#52-防火墙配置)
    - [5.3 性能调优](#53-性能调优)
  - [6. 实操示例](#6-实操示例)
    - [6.1 创建自定义网络](#61-创建自定义网络)
    - [6.2 多网络配置](#62-多网络配置)
    - [6.3 网络隔离](#63-网络隔离)
  - [7. 故障清单与排查](#7-故障清单与排查)
  - [8. FAQ](#8-faq)

## 1. 网络后端与模式

### 1.1 网络模式概述

Podman 支持多种网络模式，每种模式适用于不同的场景：

| 网络模式 | 特点 | 适用场景 | 性能 |
|---------|------|----------|------|
| **bridge** | 默认，网络隔离 | 常规容器通信 | 中等 |
| **host** | 共享主机网络栈 | 高性能需求 | 最高 |
| **none** | 无网络 | 安全隔离 | N/A |
| **pod** | Pod 内共享网络 | Kubernetes风格 | 高 |
| **macvlan** | 独立 MAC 地址 | 容器直连物理网络 | 高 |
| **pasta/slirp4netns** | rootless 专用 | 非特权网络 | 中等 |

**查看网络列表**：

```bash
# 列出所有网络
podman network ls

# 输出示例
NETWORK ID    NAME         DRIVER
2f259bab93aa  podman       bridge

# 查看网络详情
podman network inspect podman
```

### 1.2 Bridge 模式

Bridge 是 Podman 的默认网络模式，为容器提供隔离的网络环境。

**创建 Bridge 网络**：

```bash
# 创建基本 bridge 网络
podman network create mynetwork

# 指定子网和网关
podman network create \
  --subnet 172.20.0.0/16 \
  --gateway 172.20.0.1 \
  --ip-range 172.20.100.0/24 \
  app-network

# 指定驱动和选项
podman network create \
  --driver bridge \
  --opt com.docker.network.bridge.name=br-custom \
  --opt com.docker.network.driver.mtu=9000 \
  custom-bridge
```

**使用 Bridge 网络**：

```bash
# 连接到自定义网络
podman run -d --name nginx --network mynetwork nginx:alpine

# 连接到多个网络
podman run -d --name app \
  --network mynetwork \
  --network another-network \
  alpine

# 指定 IP 地址
podman run -d --name web --network mynetwork --ip 172.20.0.10 nginx:alpine
```

**Bridge 网络配置文件**：

```bash
# 查看网络配置文件位置
ls /etc/containers/networks/

# 配置示例 (mynetwork.json)
{
  "name": "mynetwork",
  "id": "abcdef123456",
  "driver": "bridge",
  "network_interface": "podman1",
  "created": "2025-01-01T00:00:00Z",
  "subnets": [
    {
      "subnet": "172.20.0.0/16",
      "gateway": "172.20.0.1"
    }
  ],
  "ipv6_enabled": false,
  "internal": false,
  "dns_enabled": true,
  "ipam_options": {
    "driver": "host-local"
  }
}
```

### 1.3 Host 模式

Host 模式让容器直接使用主机的网络栈，性能最高但安全性较低。

```bash
# 使用 host 网络
podman run -d --network host nginx:alpine

# 注意：host 模式下不需要端口映射
# ❌ 错误
podman run -d --network host -p 8080:80 nginx

# ✅ 正确：容器端口直接绑定到主机
podman run -d --network host nginx  # 直接使用 80 端口

# 查看网络信息
podman inspect container_name | jq '.[0].NetworkSettings'
```

**Host 模式特点**：

- ✅ **优点**：
  - 最高网络性能
  - 无需端口映射
  - 可直接绑定低端口（如果有权限）
  
- ❌ **缺点**：
  - 无网络隔离
  - 端口冲突风险高
  - 安全性较低

### 1.4 None 模式

None 模式完全禁用网络，适用于需要高度隔离的场景。

```bash
# 创建无网络容器
podman run -d --network none alpine sleep infinity

# 验证网络隔离
podman exec container_name ip addr
# 只有 lo (loopback) 接口

# 使用场景：数据处理、批处理任务
podman run --rm --network none \
  -v /data:/data:z \
  alpine sh -c "process_data.sh /data"
```

### 1.5 Pod 网络

Pod 是 Podman 的特色功能，多个容器共享同一个网络命名空间。

**创建和使用 Pod**：

```bash
# 创建 Pod
podman pod create --name mypod -p 8080:80

# 查看 Pod
podman pod ls

# 在 Pod 中运行容器
podman run -d --pod mypod --name nginx nginx:alpine
podman run -d --pod mypod --name sidecar busybox sleep infinity

# Pod 内容器共享网络
# 可以通过 localhost 相互访问
podman exec nginx curl localhost:80
```

**Pod 网络配置**：

```bash
# 创建带有自定义网络的 Pod
podman pod create \
  --name webapp \
  --network mynetwork \
  --ip 172.20.0.50 \
  -p 8080:80 \
  -p 8443:443

# 添加多个网络
podman pod create \
  --name multi-net-pod \
  --network frontend \
  --network backend \
  -p 3000:3000
```

**Pod 网络特性**：

1. **Infra 容器**：每个 Pod 有一个 infra 容器管理网络
2. **共享网络栈**：Pod 内容器共享 IP、端口空间
3. **localhost 通信**：容器间通过 localhost 通信
4. **Kubernetes 兼容**：与 K8s Pod 网络模型一致

```bash
# 查看 Pod 的 infra 容器
podman pod inspect mypod | jq '.InfraContainerID'

# 查看 infra 容器详情
podman inspect <infra-container-id>
```

### 1.6 与 Docker 差异

**主要差异**：

| 特性 | Podman | Docker |
|------|--------|--------|
| 默认网络栈 | Netavark (4.0+) | Docker bridge |
| DNS 服务 | Aardvark-DNS | Docker embedded DNS |
| IPv6 支持 | 原生更好 | 需要额外配置 |
| Rootless 网络 | slirp4netns/pasta | 不完善 |
| Pod 概念 | 原生支持 | 不支持 |
| 网络隔离 | 更严格 | 相对宽松 |

**配置文件位置差异**：

```bash
# Podman
# 系统级
/etc/containers/networks/
/etc/containers/containers.conf

# 用户级
$HOME/.config/containers/networks/
$HOME/.config/containers/containers.conf

# Docker
/etc/docker/daemon.json
/var/lib/docker/network/
```

**命令差异**：

```bash
# Podman 特有的网络命令
podman network reload <container>  # 重新加载容器网络
podman network exists <network>    # 检查网络是否存在

# Docker 特有的命令
docker network connect --alias myalias <network> <container>
docker network disconnect -f <network> <container>
```

## 2. netavark/aardvark-dns

### 2.1 Netavark 架构

Netavark 是 Podman 4.0+ 的新一代网络栈，替代了 CNI 插件。

**Netavark 特点**：

1. **原生 Rust 实现**：性能和内存安全
2. **简化架构**：无需多个二进制文件
3. **更好的 IPv6 支持**
4. **集成 DNS 服务**：与 Aardvark-DNS 配合
5. **nftables 支持**：现代防火墙规则

**Netavark 配置**：

```bash
# 查看 Netavark 版本
netavark --version

# 配置文件位置
/etc/containers/containers.conf

# 示例配置
[network]
network_backend = "netavark"
dns_bind_port = 53

# 检查当前网络后端
podman info | grep -i network
```

**Netavark 网络创建流程**：

```text
容器启动
    ↓
Podman 调用 Netavark
    ↓
创建网络命名空间
    ↓
创建 veth pair
    ↓
配置 IP 地址
    ↓
设置路由和防火墙规则
    ↓
启动 Aardvark-DNS
    ↓
完成
```

**Netavark 命令**：

```bash
# Netavark 是底层工具，通常不直接调用
# 但可以用于调试

# 查看网络信息
sudo netavark list

# 设置网络
sudo netavark setup <network-config.json>

# 清理网络
sudo netavark teardown <network-config.json>
```

### 2.2 Aardvark-DNS 服务

Aardvark-DNS 是 Netavark 的配套 DNS 服务器，提供容器名称解析。

**功能特性**：

1. **容器名称解析**：自动解析容器名到 IP
2. **网络别名**：支持多个别名
3. **服务发现**：动态更新 DNS 记录
4. **支持 IPv4/IPv6**：双栈 DNS 解析
5. **自定义上游 DNS**：配置外部 DNS 服务器

**DNS 配置**：

```bash
# 查看容器 DNS 配置
podman exec container_name cat /etc/resolv.conf

# 输出示例
nameserver 10.88.0.1    # Aardvark-DNS 地址
search dns.podman

# 自定义 DNS 服务器
podman run -d --dns 8.8.8.8 --dns 1.1.1.1 nginx:alpine

# 添加 DNS 搜索域
podman run -d --dns-search example.com nginx:alpine

# 添加 hosts 条目
podman run -d --add-host myhost:10.0.0.1 nginx:alpine
```

**容器名称解析**：

```bash
# 在同一网络中的容器可以通过名称相互访问
podman network create mynet

podman run -d --name web --network mynet nginx:alpine
podman run -d --name app --network mynet alpine sleep infinity

# 从 app 容器访问 web
podman exec app ping web  # 成功！
podman exec app wget -O- http://web/

# 使用网络别名
podman run -d --name db --network mynet --network-alias database postgres:alpine
podman exec app ping database  # 通过别名访问
```

**Aardvark-DNS 配置**：

```toml
# /etc/containers/containers.conf
[network]
dns_bind_port = 53

# 用户级配置
# $HOME/.config/containers/containers.conf
[network]
# 自定义 DNS 端口（rootless 模式）
dns_bind_port = 5353
```

**DNS 工作流程**：

```text
容器发起 DNS 查询
    ↓
查询发送到 Aardvark-DNS (10.88.0.1)
    ↓
Aardvark 检查本地记录
    ↓
找到？ ——是——> 返回容器 IP
    |
    否
    ↓
转发到上游 DNS (如 8.8.8.8)
    ↓
返回结果
```

### 2.3 与 CNI 对比

**CNI (Container Network Interface) vs Netavark**：

| 特性 | CNI | Netavark |
|------|-----|----------|
| **语言** | Go (多个插件) | Rust (单一二进制) |
| **性能** | 中等 | 更高 |
| **IPv6** | 需要配置 | 原生支持 |
| **DNS** | 需要 dnsmasq | 集成 Aardvark |
| **nftables** | 部分支持 | 完全支持 |
| **配置** | 多个 JSON 文件 | 统一配置 |
| **维护** | 多个项目 | 单一项目 |

**迁移到 Netavark**：

```bash
# Podman 4.0+ 默认使用 Netavark
# 查看当前后端
podman info | grep networkBackend

# 如果需要切换回 CNI（不推荐）
# /etc/containers/containers.conf
[network]
network_backend = "cni"

# 重启 Podman 系统服务
podman system reset --force  # ⚠️ 警告：删除所有容器和网络
```

**Netavark 优势**：

1. **简化部署**：单一二进制，无需多个插件
2. **更好的 IPv6**：无需额外配置
3. **统一配置**：一个配置文件
4. **现代化**：使用 nftables 替代 iptables
5. **性能提升**：Rust 实现，更高效

### 2.4 网络配置

**全局网络配置**：

```toml
# /etc/containers/containers.conf
[network]
# 网络后端
network_backend = "netavark"

# 默认网络
default_network = "podman"

# DNS 配置
dns_bind_port = 53

# 默认子网
default_subnet = "10.88.0.0/16"

# 默认子网池
default_subnet_pools = [
  {"base" = "10.89.0.0/16", "size" = 24},
  {"base" = "10.90.0.0/16", "size" = 24},
]

# 网络配置目录
network_config_dir = "/etc/containers/networks"

# 防火墙驱动
firewall_driver = "nftables"  # 或 "iptables"
```

**每个网络的配置**：

```json
{
  "name": "mynetwork",
  "id": "abc123",
  "driver": "bridge",
  "network_interface": "podman1",
  "created": "2025-01-01T00:00:00Z",
  "subnets": [
    {
      "subnet": "172.20.0.0/16",
      "gateway": "172.20.0.1",
      "lease_range": {
        "start_ip": "172.20.1.0",
        "end_ip": "172.20.255.255"
      }
    }
  ],
  "ipv6_enabled": true,
  "internal": false,
  "dns_enabled": true,
  "ipam_options": {
    "driver": "host-local"
  },
  "options": {
    "mtu": "1500",
    "vlan": "100"
  }
}
```

## 3. rootless 网络：slirp4netns/pasta

### 3.1 Rootless 网络架构

Rootless Podman 无法直接创建网络设备，需要特殊的网络方案。

**Rootless 网络选项**：

| 方案 | 性能 | 功能 | 复杂度 | 推荐度 |
|------|------|------|--------|--------|
| **slirp4netns** | 低 | 完整 | 低 | 兼容性 |
| **pasta** | 高 | 完整 | 低 | **推荐** |
| **tap** | 最高 | 完整 | 高 | 高级用户 |

**架构对比**：

```text
# Rootful (有 root 权限)
Container → veth → bridge → 主机网络

# Rootless - slirp4netns
Container → slirp4netns (用户空间网络栈) → 主机网络

# Rootless - pasta
Container → pasta (优化的用户空间网络) → 主机网络
```

### 3.2 slirp4netns

Slirp4netns 是早期的 rootless 网络方案，基于 QEMU 的 slirp 代码。

**安装 slirp4netns**：

```bash
# Fedora/RHEL
sudo dnf install slirp4netns

# Ubuntu/Debian
sudo apt-get install slirp4netns

# 验证安装
slirp4netns --version
```

**使用 slirp4netns**：

```bash
# Podman 默认在 rootless 模式下使用 slirp4netns
podman run -d --name web -p 8080:80 nginx:alpine

# 明确指定 slirp4netns
podman run -d --network slirp4netns nginx:alpine

# 配置 slirp4netns 选项
podman run -d \
  --network slirp4netns:port_handler=slirp4netns \
  --network slirp4netns:cidr=10.0.2.0/24 \
  nginx:alpine
```

**slirp4netns 特点**：

✅ **优点**：

- 无需特权
- 兼容性好
- 配置简单

❌ **缺点**：

- 性能较低（用户空间实现）
- 无法绑定 < 1024 端口
- 网络吞吐量有限

**性能优化**：

```bash
# 启用 seccomp 加速
podman run -d \
  --network slirp4netns:enable_seccomp=true \
  nginx:alpine

# 调整 MTU
podman run -d \
  --network slirp4netns:mtu=9000 \
  nginx:alpine

# 使用多队列
podman run -d \
  --network slirp4netns:enable_ipv6=true,outbound_addr=slirp4netns \
  nginx:alpine
```

### 3.3 pasta (Passt)

Pasta (Passt) 是新一代 rootless 网络方案，性能接近原生网络。

**安装 pasta**：

```bash
# Fedora 37+
sudo dnf install passt

# Ubuntu 22.04+
sudo apt-get install passt

# 验证安装
pasta --version
```

**使用 pasta**：

```bash
# Podman 5.0+ 可以使用 pasta
podman run -d --network pasta --name web -p 8080:80 nginx:alpine

# pasta 作为默认 rootless 网络
# /etc/containers/containers.conf 或 ~/.config/containers/containers.conf
[network]
default_rootless_network_cmd = "pasta"

# 重启容器后生效
podman stop web && podman start web
```

**pasta 配置选项**：

```bash
# 指定 pasta 选项
podman run -d \
  --network pasta:--map-gw,--no-map-gw \
  nginx:alpine

# 端口转发
podman run -d \
  --network pasta:-t,8080:80,-u,5353:53 \
  nginx:alpine
```

**pasta 特点**：

✅ **优点**：

- 高性能（接近原生）
- 自动端口映射
- 更好的 IPv6 支持
- 低 CPU 开销

❌ **缺点**：

- 需要较新的内核 (5.10+)
- 相对较新，生态系统在完善中

### 3.4 性能对比与选择

**性能测试对比**：

```bash
# 测试脚本
#!/bin/bash
# network-perf-test.sh

test_network() {
  local mode=$1
  echo "测试 $mode 网络..."
  
  # 启动服务器容器
  podman run -d --name server-$mode --network $mode nginx:alpine
  sleep 2
  
  # 测试吞吐量
  time podman run --rm --network $mode alpine \
    wget -O /dev/null http://server-$mode/
  
  # 清理
  podman rm -f server-$mode
}

# 测试不同模式
test_network "host"          # 基准
test_network "bridge"        # rootful bridge
test_network "slirp4netns"   # rootless slirp4netns
test_network "pasta"         # rootless pasta
```

**性能对比（相对 host 模式）**：

| 网络模式 | 吞吐量 | 延迟 | CPU 使用 | 内存使用 |
|---------|--------|------|----------|----------|
| **host** | 100% | 1x | 最低 | 最低 |
| **bridge (rootful)** | 95% | 1.05x | 低 | 低 |
| **pasta (rootless)** | 85-90% | 1.15x | 中 | 中 |
| **slirp4netns** | 50-60% | 2x | 高 | 高 |

**选择建议**：

```text
使用场景           →  推荐方案
─────────────────────────────────
生产环境 + rootful   →  bridge
生产环境 + rootless  →  pasta
开发环境 + rootless  →  pasta 或 slirp4netns
高性能需求          →  host 或 macvlan
需要兼容性          →  slirp4netns
需要网络隔离        →  bridge
```

**配置示例**：

```toml
# ~/.config/containers/containers.conf
[network]
# Rootless 默认使用 pasta
default_rootless_network_cmd = "pasta"

# 如果 pasta 不可用，回退到 slirp4netns
# (自动处理)

[engine]
# 启用 pasta 的实验性功能
# experimental = true
```

## 4. IPv6 与高级特性

### 4.1 IPv6 配置

Podman 对 IPv6 有原生支持，配置比 Docker 更简单。

**启用 IPv6**：

```bash
# 创建支持 IPv6 的网络
podman network create \
  --ipv6 \
  --subnet 2001:db8::/64 \
  --gateway 2001:db8::1 \
  ipv6-network

# 创建双栈网络
podman network create \
  --subnet 172.20.0.0/16 \
  --gateway 172.20.0.1 \
  --ipv6 \
  --subnet 2001:db8::/64 \
  --gateway 2001:db8::1 \
  dualstack-network

# 使用 IPv6 网络
podman run -d --network ipv6-network --name web nginx:alpine

# 指定 IPv6 地址
podman run -d \
  --network ipv6-network \
  --ip6 2001:db8::100 \
  --name web \
  nginx:alpine
```

**验证 IPv6**：

```bash
# 检查容器 IPv6 地址
podman exec web ip -6 addr

# 测试 IPv6 连接
podman exec web ping6 google.com
podman exec web curl -6 https://ipv6.google.com

# 从另一个容器访问
podman run --rm --network ipv6-network alpine \
  ping6 2001:db8::100
```

**IPv6 端口映射**：

```bash
# IPv6 端口映射
podman run -d \
  --network dualstack-network \
  -p '[::]:8080:80' \
  --name web \
  nginx:alpine

# 验证监听
ss -tlnp | grep 8080
# 应该显示 :::8080
```

### 4.2 双栈网络

双栈网络同时支持 IPv4 和 IPv6。

**创建双栈网络**：

```bash
# 完整的双栈网络配置
podman network create \
  --driver bridge \
  --subnet 10.100.0.0/24 \
  --gateway 10.100.0.1 \
  --ip-range 10.100.0.128/25 \
  --ipv6 \
  --subnet fd00:abcd::/64 \
  --gateway fd00:abcd::1 \
  --opt com.docker.network.bridge.name=br-dualstack \
  --opt com.docker.network.driver.mtu=1500 \
  dualstack-net

# 查看配置
podman network inspect dualstack-net
```

**使用双栈网络**：

```bash
# 运行容器
podman run -d \
  --name web \
  --network dualstack-net \
  --ip 10.100.0.10 \
  --ip6 fd00:abcd::10 \
  nginx:alpine

# 验证双栈配置
podman exec web ip addr show eth0

# 测试 IPv4
podman exec web wget -O- http://ipv4.google.com

# 测试 IPv6
podman exec web wget -O- http://ipv6.google.com
```

### 4.3 macvlan 和 ipvlan

Macvlan 和 IPvlan 允许容器直接连接到物理网络。

**创建 macvlan 网络**：

```bash
# 创建 macvlan 网络（需要 root）
sudo podman network create \
  --driver macvlan \
  --subnet 192.168.1.0/24 \
  --gateway 192.168.1.1 \
  --ip-range 192.168.1.100/28 \
  -o parent=eth0 \
  macvlan-net

# 使用 macvlan
sudo podman run -d \
  --network macvlan-net \
  --ip 192.168.1.101 \
  --name web \
  nginx:alpine

# 容器直接在物理网络上可见
# 可以从物理网络的其他设备访问 192.168.1.101
```

**创建 ipvlan 网络**：

```bash
# IPvlan L2 模式
sudo podman network create \
  --driver ipvlan \
  --subnet 192.168.1.0/24 \
  --gateway 192.168.1.1 \
  -o parent=eth0 \
  -o ipvlan_mode=l2 \
  ipvlan-l2

# IPvlan L3 模式（路由模式）
sudo podman network create \
  --driver ipvlan \
  --subnet 10.200.0.0/24 \
  -o parent=eth0 \
  -o ipvlan_mode=l3 \
  ipvlan-l3

# 使用 ipvlan
sudo podman run -d \
  --network ipvlan-l2 \
  --name web \
  nginx:alpine
```

**macvlan vs ipvlan**：

| 特性 | macvlan | ipvlan |
|------|---------|--------|
| **MAC 地址** | 每个容器独立 MAC | 共享 MAC |
| **交换机兼容** | 可能有限制 | 更好 |
| **性能** | 高 | 更高 |
| **L2/L3** | L2 only | L2 和 L3 |

### 4.4 VLAN 网络

VLAN 网络用于网络隔离和多租户环境。

**创建 VLAN 网络**：

```bash
# 创建 VLAN 100 网络
sudo podman network create \
  --driver macvlan \
  --subnet 10.100.0.0/24 \
  --gateway 10.100.0.1 \
  -o parent=eth0.100 \
  vlan100-net

# 如果 VLAN 接口不存在，先创建
sudo ip link add link eth0 name eth0.100 type vlan id 100
sudo ip link set eth0.100 up

# 使用 VLAN 网络
sudo podman run -d \
  --network vlan100-net \
  --name app1 \
  myapp:latest

# 创建多个 VLAN
sudo podman network create --driver macvlan \
  --subnet 10.200.0.0/24 -o parent=eth0.200 vlan200-net
```

### 4.5 网络策略

虽然 Podman 不像 Kubernetes 有内置的 NetworkPolicy，但可以通过防火墙实现。

**使用 nftables 实现网络策略**：

```bash
# 阻止容器间通信（除非明确允许）
sudo nft add table ip podman-isolation
sudo nft add chain ip podman-isolation forward { type filter hook forward priority 0\; policy drop\; }

# 允许特定网络间通信
sudo nft add rule ip podman-isolation forward \
  ip saddr 172.20.0.0/16 ip daddr 172.21.0.0/16 accept

# 允许容器访问外网
sudo nft add rule ip podman-isolation forward \
  ip saddr 172.20.0.0/16 oifname "eth0" accept
sudo nft add rule ip podman-isolation forward \
  ip daddr 172.20.0.0/16 iifname "eth0" ct state established,related accept
```

**使用 iptables（传统方式）**：

```bash
# 创建隔离链
sudo iptables -N PODMAN-ISOLATION

# 默认拒绝
sudo iptables -A PODMAN-ISOLATION -j DROP

# 允许特定通信
sudo iptables -I PODMAN-ISOLATION 1 \
  -s 172.20.0.0/16 -d 172.21.0.0/16 -j ACCEPT
```

## 5. 故障诊断与调优

### 5.1 网络诊断工具

**基本诊断命令**：

```bash
# 查看网络列表
podman network ls

# 检查网络详情
podman network inspect <network-name>

# 查看容器网络配置
podman inspect <container> | jq '.[0].NetworkSettings'

# 检查容器网络接口
podman exec <container> ip addr
podman exec <container> ip route

# 测试网络连接
podman exec <container> ping -c 3 google.com
podman exec <container> curl -v https://example.com

# 检查 DNS 解析
podman exec <container> nslookup google.com
podman exec <container> dig google.com
```

**高级诊断**：

```bash
# 追踪路由
podman exec <container> traceroute google.com

# 检查端口
podman exec <container> netstat -tulpn
podman exec <container> ss -tulpn

# 抓包分析
sudo tcpdump -i podman0 -w capture.pcap
# 在另一个终端触发网络活动
wireshark capture.pcap

# 检查防火墙规则
sudo nft list ruleset | grep -A 20 podman
sudo iptables-save | grep -i podman

# 检查网络命名空间
sudo ip netns list
podman inspect <container> | jq '.[0].NetworkSettings.SandboxKey'
```

**网络性能测试**：

```bash
# 使用 iperf3 测试
# 服务器容器
podman run -d --name iperf-server --network mynet \
  networkstatic/iperf3 -s

# 客户端容器
podman run --rm --network mynet \
  networkstatic/iperf3 -c iperf-server

# 测试延迟
podman run --rm --network mynet alpine \
  ping -c 100 iperf-server | tail -1

# 测试带宽
podman run --rm --network mynet alpine \
  wget -O /dev/null http://iperf-server/bigfile
```

### 5.2 防火墙配置

**nftables 配置（推荐）**：

```bash
# 查看 Podman 的 nftables 规则
sudo nft list ruleset | grep -A 30 podman

# 示例规则
table ip podman {
    chain PODMAN {
        type filter hook forward priority 0; policy accept;
        iifname "podman0" oifname != "podman0" accept
        oifname "podman0" ct state related,established accept
    }
}

# 添加自定义规则
sudo nft add rule ip podman PODMAN \
  ip saddr 172.20.0.0/16 ip daddr 10.0.0.0/8 drop
```

**iptables 配置（传统）**：

```bash
# 查看 Podman 的 iptables 规则
sudo iptables -L -n -v | grep -i podman
sudo iptables -t nat -L -n -v | grep -i podman

# 允许特定流量
sudo iptables -I PODMAN-ISOLATION 1 \
  -s 172.20.0.0/16 -p tcp --dport 80 -j ACCEPT

# 端口转发
sudo iptables -t nat -A PODMAN-DNAT \
  -p tcp --dport 8080 -j DNAT --to-destination 172.20.0.10:80
```

**firewalld 集成**：

```bash
# 查看 firewalld 区域
sudo firewall-cmd --get-active-zones

# 将 Podman 网络添加到信任区域
sudo firewall-cmd --permanent --zone=trusted \
  --add-source=172.20.0.0/16
sudo firewall-cmd --reload

# 添加端口转发
sudo firewall-cmd --permanent \
  --add-forward-port=port=8080:proto=tcp:toport=80:toaddr=172.20.0.10
sudo firewall-cmd --reload
```

### 5.3 性能调优

**MTU 优化**：

```bash
# 创建自定义 MTU 网络
podman network create \
  --opt com.docker.network.driver.mtu=9000 \
  jumbo-network

# 验证 MTU
podman run --rm --network jumbo-network alpine \
  ip link show eth0

# 测试最佳 MTU
for mtu in 1500 4000 9000; do
  echo "测试 MTU $mtu"
  podman network create --opt mtu=$mtu test-$mtu
  # 运行性能测试...
  podman network rm test-$mtu
done
```

**TCP 优化**：

```bash
# 在容器内优化 TCP
podman run -d --name optimized \
  --sysctl net.ipv4.tcp_fastopen=3 \
  --sysctl net.core.somaxconn=4096 \
  --sysctl net.ipv4.tcp_max_syn_backlog=8192 \
  nginx:alpine

# 或通过 Dockerfile
# RUN echo "net.ipv4.tcp_fastopen=3" >> /etc/sysctl.conf
```

**网络隔离优化**：

```bash
# 禁用容器间通信（提高安全性和性能）
podman network create \
  --opt com.docker.network.bridge.enable_icc=false \
  isolated-network

# 使用 internal 网络（无外网访问）
podman network create --internal internal-net

# 容器只能相互通信，无法访问外网
podman run -d --network internal-net --name db postgres:alpine
podman run -d --network internal-net --name app myapp:latest
```

## 6. 实操示例

### 6.1 创建自定义网络

```bash
#!/bin/bash
# create-custom-network.sh

# 1. 创建前端网络
podman network create \
  --subnet 172.21.0.0/16 \
  --gateway 172.21.0.1 \
  --ip-range 172.21.10.0/24 \
  --opt com.docker.network.bridge.name=br-frontend \
  --label env=production \
  --label tier=frontend \
  frontend-net

# 2. 创建后端网络
podman network create \
  --subnet 172.22.0.0/16 \
  --gateway 172.22.0.1 \
  --internal \
  --label env=production \
  --label tier=backend \
  backend-net

# 3. 创建 IPv6 双栈网络
podman network create \
  --subnet 172.23.0.0/16 \
  --ipv6 \
  --subnet fd00:cafe::/64 \
  --label env=production \
  --label tier=dmz \
  dmz-net

echo "网络创建完成！"
podman network ls
```

### 6.2 多网络配置

```bash
#!/bin/bash
# multi-network-app.sh

# 1. 创建网络
podman network create frontend
podman network create backend
podman network create database

# 2. 启动数据库（仅后端网络）
podman run -d \
  --name postgres \
  --network database \
  -e POSTGRES_PASSWORD=secret \
  postgres:15-alpine

# 3. 启动应用（前端+后端网络）
podman run -d \
  --name app \
  --network frontend \
  --network backend \
  -e DB_HOST=postgres \
  myapp:latest

# 将应用也连接到数据库网络
podman network connect database app

# 4. 启动 Web 服务器（仅前端网络）
podman run -d \
  --name nginx \
  --network frontend \
  -p 8080:80 \
  nginx:alpine

# 验证网络隔离
echo "验证网络连接..."
podman exec app ping -c 1 postgres  # 应该成功
podman exec nginx ping -c 1 postgres  # 应该失败（没有连接到 database 网络）
```

### 6.3 网络隔离

```bash
#!/bin/bash
# network-isolation-demo.sh

# 场景：创建多租户隔离环境

# 租户 A
podman network create --internal tenant-a-network
podman pod create --name tenant-a --network tenant-a-network -p 8081:80

podman run -d --pod tenant-a --name tenant-a-web nginx:alpine
podman run -d --pod tenant-a --name tenant-a-db postgres:alpine

# 租户 B
podman network create --internal tenant-b-network
podman pod create --name tenant-b --network tenant-b-network -p 8082:80

podman run -d --pod tenant-b --name tenant-b-web nginx:alpine
podman run -d --pod tenant-b --name tenant-b-db postgres:alpine

# 验证隔离
echo "验证网络隔离..."
podman exec tenant-a-web ping -c 1 -W 1 tenant-b-web && echo "隔离失败！" || echo "隔离成功！"

# 访问测试
curl http://localhost:8081  # 租户 A
curl http://localhost:8082  # 租户 B
```

## 7. 故障清单与排查

**问题1：端口未通（Rootless 模式）**:

```bash
# 症状：无法访问容器端口

# 排查：
# 1. 检查端口映射
podman ps --format "{{.Names}} {{.Ports}}"

# 2. 确认 rootless 低端口限制
# rootless 不能直接绑定 < 1024 端口

# 3. 检查防火墙
sudo firewall-cmd --list-all

# 解决方案：
# - 使用高端口映射
podman run -p 8080:80 nginx  # 而不是 -p 80:80

# - 或使用 rootful 模式
sudo podman run -p 80:80 nginx

# - 或配置 sysctl
echo 'net.ipv4.ip_unprivileged_port_start=80' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

**问题2：IPv6 未生效**:

```bash
# 症状：IPv6 地址无法访问

# 排查：
# 1. 检查系统 IPv6 是否启用
cat /proc/sys/net/ipv6/conf/all/disable_ipv6  # 应该是 0

# 2. 检查 Netavark 版本
netavark --version  # 应该 >= 1.4.0

# 3. 验证网络配置
podman network inspect mynet | jq '.ipv6_enabled'

# 解决方案：
# - 启用系统 IPv6
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=0

# - 重新创建网络
podman network rm mynet
podman network create --ipv6 --subnet fd00::/64 mynet

# - 检查容器 IPv6 地址
podman exec container ip -6 addr
```

**问题3：容器间无法通信**:

```bash
# 症状：同一网络的容器无法互相访问

# 排查：
# 1. 检查容器是否在同一网络
podman inspect container1 | jq '.[0].NetworkSettings.Networks'
podman inspect container2 | jq '.[0].NetworkSettings.Networks'

# 2. 检查 Aardvark-DNS
podman exec container1 cat /etc/resolv.conf
podman exec container1 nslookup container2

# 3. 检查防火墙规则
sudo nft list ruleset | grep -i podman

# 解决方案：
# - 确保容器在同一网络
podman network connect mynetwork container2

# - 重启 Aardvark-DNS
podman network reload container1
podman network reload container2

# - 检查网络隔离设置
podman network inspect mynet | jq '.internal'
```

**问题4：性能问题（Rootless slirp4netns）**:

```bash
# 症状：网络延迟高，吞吐量低

# 排查：
# 1. 确认使用的网络后端
podman info | grep -i networkBackend

# 2. 检查是否使用 slirp4netns
podman inspect container | jq '.[0].HostConfig.NetworkMode'

# 解决方案：
# - 升级到 pasta
sudo dnf install passt  # Fedora
sudo apt install passt  # Ubuntu

# 配置 Podman 使用 pasta
# ~/.config/containers/containers.conf
[network]
default_rootless_network_cmd = "pasta"

# - 或使用 rootful 模式（如果可以）
sudo podman run ...

# - 或使用 host 网络（无隔离）
podman run --network host ...
```

**问题5：DNS 解析失败**:

```bash
# 症状：容器无法解析域名

# 排查：
# 1. 检查 DNS 配置
podman exec container cat /etc/resolv.conf

# 2. 测试 DNS 解析
podman exec container nslookup google.com
podman exec container dig @8.8.8.8 google.com

# 3. 检查 Aardvark-DNS
podman exec container ping $(podman network inspect mynet | jq -r '.[0].plugins[0].ipam.ranges[0][0].gateway')

# 解决方案：
# - 指定 DNS 服务器
podman run --dns 8.8.8.8 --dns 1.1.1.1 ...

# - 重启网络
podman network reload container

# - 检查主机 DNS
cat /etc/resolv.conf
ping google.com  # 主机能否解析？

# - 禁用 SELinux（临时测试）
sudo setenforce 0
```

## 8. FAQ

**Q1: Podman 的 bridge 与 Docker 的 bridge 有何差异？**

A: 主要差异：

- **网络栈**：Podman 4.0+ 使用 Netavark，Docker 使用自己的 bridge
- **DNS**：Podman 使用 Aardvark-DNS，Docker 使用 embedded DNS
- **IPv6**：Podman 原生支持更好，无需额外配置
- **配置**：Podman 配置更标准化（OCI 兼容）

**Q2: Rootless 模式下如何绑定低端口？**

A: 三种方法：

1. **端口映射**：`podman run -p 8080:80`（推荐）
2. **配置 sysctl**：

   ```bash
   echo 'net.ipv4.ip_unprivileged_port_start=80' | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```

3. **使用 rootful 模式**：`sudo podman run -p 80:80`

**Q3: 如何提高 rootless 网络性能？**

A:

1. 使用 **pasta** 而不是 slirp4netns
2. 使用 **host 网络**（无隔离）
3. 升级内核到 5.10+
4. 考虑使用 **rootful 模式**（如果安全要求允许）

**Q4: 如何实现容器间网络隔离？**

A:

1. **使用不同网络**：不同租户使用不同网络
2. **internal 网络**：禁止访问外网
3. **防火墙规则**：使用 nftables/iptables 限制流量
4. **Pod 隔离**：将容器组织成 Pod，限制 Pod 间通信

**Q5: Pod 网络与 Docker Compose 网络有何区别？**

A:

- **Pod**：多个容器共享同一网络栈，通过 localhost 通信
- **Compose**：容器有独立网络栈，通过容器名通信
- **性能**：Pod 性能更高（无需经过 bridge）
- **隔离**：Compose 隔离性更好

**Q6: 如何调试网络问题？**

A: 步骤：

1. 使用 `podman network inspect` 检查配置
2. 使用 `podman exec container ip addr` 查看接口
3. 测试 DNS：`podman exec container nslookup google.com`
4. 测试连接：`podman exec container ping 8.8.8.8`
5. 检查防火墙：`sudo nft list ruleset | grep podman`
6. 抓包分析：`sudo tcpdump -i podman0`

**Q7: 能否在同一容器上使用多个网络？**

A: 可以！

```bash
podman run -d --name multi-net \
  --network net1 \
  --network net2 \
  --network net3 \
  myapp:latest

# 或动态连接
podman network connect net4 multi-net
```

**Q8: 如何实现跨主机容器通信？**

A: 方法：

1. **Overlay 网络**（需要 etcd/consul）
2. **Macvlan**：容器直接在物理网络上
3. **VPN/Wireguard**：主机间建立 VPN
4. **Kubernetes**：使用 CNI 插件（Calico、Flannel 等）

**Q9: Netavark 能否与 CNI 共存？**

A: 不推荐，但技术上可以：

```toml
# /etc/containers/containers.conf
[network]
network_backend = "netavark"  # 或 "cni"
```

选择一个并坚持使用。

**Q10: 如何实现网络 QoS？**

A: 使用 tc (traffic control)：

```bash
# 在宿主机上限制容器网络
sudo tc qdisc add dev veth123 root tbf rate 1mbit burst 32kbit latency 400ms

# 或在创建网络时指定
podman network create \
  --opt com.docker.network.driver.mtu=1500 \
  --opt com.docker.network.bridge.name=br-qos \
  qos-network
```

---

**相关资源**：

- [Podman 网络文档](https://docs.podman.io/en/latest/markdown/podman-network.1.html)
- [Netavark GitHub](https://github.com/containers/netavark)
- [Aardvark-DNS GitHub](https://github.com/containers/aardvark-dns)
- [Pasta/Passt 项目](https://passt.top/)
- [slirp4netns 文档](https://github.com/rootless-containers/slirp4netns)
- [OCI 运行时规范](https://github.com/opencontainers/runtime-spec)
