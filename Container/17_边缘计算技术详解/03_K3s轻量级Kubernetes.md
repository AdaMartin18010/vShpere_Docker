# K3s轻量级Kubernetes

## 📋 目录

- [K3s轻量级Kubernetes](#k3s轻量级kubernetes)
  - [📋 目录](#-目录)
  - [项目概述](#项目概述)
    - [K3s简介](#k3s简介)
    - [核心特性](#核心特性)
    - [版本历史](#版本历史)
    - [与K8s的关系](#与k8s的关系)
  - [核心架构](#核心架构)
    - [整体架构](#整体架构)
    - [组件对比](#组件对比)
    - [数据存储](#数据存储)
  - [快速部署](#快速部署)
    - [单节点部署](#单节点部署)
    - [多节点集群](#多节点集群)
    - [高可用部署](#高可用部署)
  - [存储集成](#存储集成)
    - [Local Path Provisioner](#local-path-provisioner)
    - [Longhorn分布式存储](#longhorn分布式存储)
  - [网络配置](#网络配置)
    - [Flannel网络](#flannel网络)
    - [Traefik Ingress](#traefik-ingress)
    - [Service Load Balancer](#service-load-balancer)
  - [ARM与边缘设备](#arm与边缘设备)
    - [ARM64支持](#arm64支持)
    - [树莓派部署](#树莓派部署)
    - [NVIDIA Jetson](#nvidia-jetson)
  - [生产部署](#生产部署)
    - [系统要求](#系统要求)
    - [安全加固](#安全加固)
    - [性能优化](#性能优化)
  - [监控运维](#监控运维)
    - [监控方案](#监控方案)
    - [日志管理](#日志管理)
    - [备份恢复](#备份恢复)
  - [应用场景](#应用场景)
    - [边缘计算](#边缘计算)
    - [IoT网关](#iot网关)
    - [CI/CD环境](#cicd环境)
  - [最佳实践](#最佳实践)
    - [1. 资源规划](#1-资源规划)
    - [2. 网络优化](#2-网络优化)
    - [3. 安全建议](#3-安全建议)
  - [与Kubernetes对比](#与kubernetes对比)
    - [功能对比](#功能对比)
    - [性能对比](#性能对比)
    - [选型建议](#选型建议)
  - [参考资料](#参考资料)
    - [官方资源](#官方资源)
    - [社区资源](#社区资源)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 项目概述

### K3s简介

**K3s** 是由Rancher Labs（现为SUSE旗下）开发的轻量级Kubernetes发行版，专为资源受限的环境和边缘计算场景设计。K3s是经过CNCF认证的Kubernetes发行版，完全兼容Kubernetes API。

**名字由来**: "K3s"代表"5 less than K8s"（比K8s少5个），寓意比Kubernetes更轻量。

**项目信息**:

```yaml
开发者: Rancher Labs (SUSE)
开源时间: 2019年2月
CNCF认证: ✅ Certified Kubernetes
最新版本: v1.30.5+k3s1 (2024年10月)
GitHub: github.com/k3s-io/k3s
Stars: 27K+ (2024年)
License: Apache 2.0

关键特点:
  - 二进制大小: <70MB
  - 内存占用: 最低512MB
  - 安装时间: <30秒
  - 单进程架构: 简化运维
```

### 核心特性

**1. 极致轻量**:

```yaml
尺寸对比:
  K8s:
    二进制: ~1.5GB
    依赖: etcd, kubelet, kube-proxy等多个组件
    镜像: 10+个

  K3s:
    二进制: <70MB (所有组件打包)
    依赖: 内置etcd/SQLite
    镜像: 单一镜像

内存占用:
  K8s: 至少2-4GB
  K3s: 最低512MB (推荐1GB)
```

**2. 简化部署**:

```bash
# K3s安装 - 单条命令
curl -sfL https://get.k3s.io | sh -

# K8s安装 - 需要多个步骤
# - 安装容器运行时
# - 配置kubelet
# - 初始化集群
# - 安装CNI插件
# - ...（10+步骤）
```

**3. 边缘优化**:

```yaml
优化方向:
  启动速度:
    - 单二进制启动
    - 无需复杂依赖
    - 秒级启动完成

  资源使用:
    - 内存占用小
    - CPU开销低
    - 磁盘空间少

  网络容错:
    - 自动断线重连
    - 内置代理
    - 支持间歇性网络

  ARM支持:
    - 原生ARM64支持
    - 树莓派优化
    - IoT设备友好
```

**4. 生产就绪**:

```yaml
企业特性:
  - CNCF认证Kubernetes
  - 100%兼容K8s API
  - 自动TLS证书管理
  - 内置负载均衡器
  - 支持Helm
  - 支持所有K8s资源

内置组件:
  - 容器运行时: containerd
  - 网络插件: Flannel
  - Ingress控制器: Traefik
  - 存储: Local Path Provisioner
  - DNS: CoreDNS
  - 负载均衡: ServiceLB
```

### 版本历史

| 版本 | 发布时间 | Kubernetes版本 | 主要特性 |
|------|---------|---------------|---------|
| **v1.30** | 2024-10 | K8s 1.30 | 增强安全、性能优化 |
| **v1.29** | 2024-06 | K8s 1.29 | 嵌入式镜像支持 |
| **v1.28** | 2024-03 | K8s 1.28 | 支持外部数据库 |
| **v1.27** | 2023-12 | K8s 1.27 | 改进的HA支持 |
| **v1.26** | 2023-09 | K8s 1.26 | 增强的ARM支持 |
| **v1.25** | 2023-06 | K8s 1.25 | Dual-stack IPv4/IPv6 |
| **v1.24** | 2023-03 | K8s 1.24 | 移除Dockershim |
| **v1.0** | 2020-02 | K8s 1.17 | 首个GA版本 |

### 与K8s的关系

```text
┌────────────────────────────────────────┐
│          K3s                           │
│  ┌──────────────────────────────────┐  │
│  │  Kubernetes API (100%兼容)       │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  简化的组件                       │  │
│  │  - 单二进制                      │  │
│  │  - 内置数据库(SQLite/etcd)       │  │
│  │  - 简化的控制平面                │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  内置附加组件                     │  │
│  │  - Traefik Ingress              │  │
│  │  - Local Storage                │  │
│  │  - ServiceLB                    │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

特点:
  ✅ 100% K8s API兼容
  ✅ 通过CNCF认证
  ✅ kubectl完全可用
  ✅ Helm charts兼容
  ✅ K8s应用无需修改
```

---

## 核心架构

### 整体架构

```text
┌────────────────────────────────────────────────────────┐
│                K3s Server Node                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  K3s Server (单进程)                             │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  API Server                                │  │  │
│  │  │  - 提供Kubernetes API                      │  │  │
│  │  │  - 处理REST请求                           │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Controller Manager                        │  │  │
│  │  │  - 节点控制器                             │  │  │
│  │  │  - 副本控制器                             │  │  │
│  │  │  - 端点控制器                             │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Scheduler                                 │  │  │
│  │  │  - Pod调度                                │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Cloud Controller (可选)                   │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  内置数据库                                       │  │
│  │  - SQLite (单节点) 或                           │  │
│  │  - Embedded etcd (多节点)                       │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Containerd (容器运行时)                         │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Kubelet (Pod管理)                              │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Kube-proxy (网络代理)                          │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────┐
│                K3s Agent Node                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  K3s Agent (单进程)                              │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Kubelet                                   │  │  │
│  │  │  - Pod生命周期管理                         │  │  │
│  │  │  - 资源监控                                │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Kube-proxy                                │  │  │
│  │  │  - Service路由                            │  │  │
│  │  │  - 负载均衡                                │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Flannel (CNI)                            │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Containerd                                      │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### 组件对比

**K3s vs K8s组件差异**:

| 组件 | Kubernetes | K3s |
|------|-----------|-----|
| **控制平面** | 多个独立进程 | 单进程 |
| **数据存储** | 外部etcd集群 | 内置SQLite/etcd |
| **容器运行时** | 需单独安装 | 内置containerd |
| **网络插件** | 需单独安装 | 内置Flannel |
| **DNS** | 需单独部署 | 内置CoreDNS |
| **Ingress** | 需单独部署 | 内置Traefik |
| **存储** | 需单独配置 | 内置Local Path |
| **负载均衡** | 需云提供商 | 内置ServiceLB |
| **证书管理** | 手动或cert-manager | 自动管理 |

### 数据存储

**支持的数据库**:

```yaml
1. SQLite (默认):
   适用场景: 单节点、开发测试
   优势:
     - 无需配置
     - 零依赖
     - 自动备份
   劣势:
     - 不支持HA
     - 性能有限

2. Embedded etcd:
   适用场景: 多节点HA集群
   优势:
     - 自动集群
     - 高可用
     - 一致性保证
   劣势:
     - 内存占用高(+512MB)

3. 外部etcd:
   适用场景: 大规模生产集群
   优势:
     - 灵活配置
     - 独立扩展
     - 专用备份

4. PostgreSQL/MySQL:
   适用场景: 复用现有数据库
   优势:
     - 统一数据库管理
     - 成熟的备份方案
```

---

## 快速部署

### 单节点部署

**最简单的部署** (1分钟内完成):

```bash
# 1. 安装K3s (自动启动)
curl -sfL https://get.k3s.io | sh -

# 2. 验证安装
sudo k3s kubectl get nodes

# 输出:
# NAME   STATUS   ROLES                  AGE   VERSION
# node1  Ready    control-plane,master   30s   v1.30.5+k3s1

# 3. 部署应用
sudo k3s kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
EOF

# 4. 访问应用
# K3s会自动分配外部端口
sudo k3s kubectl get svc nginx
```

**配置kubectl**:

```bash
# 方法1: 使用k3s kubectl
sudo k3s kubectl get pods

# 方法2: 配置标准kubectl
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# 现在可以直接使用kubectl
kubectl get pods
```

**自定义安装选项**:

```bash
# 禁用Traefik
curl -sfL https://get.k3s.io | sh -s - --disable traefik

# 禁用ServiceLB
curl -sfL https://get.k3s.io | sh -s - --disable servicelb

# 指定数据目录
curl -sfL https://get.k3s.io | sh -s - --data-dir /data/k3s

# 指定node-ip (多网卡环境)
curl -sfL https://get.k3s.io | sh -s - --node-ip 192.168.1.100

# 禁用默认CNI (使用自定义网络)
curl -sfL https://get.k3s.io | sh -s - --flannel-backend=none

# 完整示例
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.30.5+k3s1 sh -s - \
  --write-kubeconfig-mode 644 \
  --disable traefik \
  --node-name k3s-master \
  --node-ip 192.168.1.100 \
  --data-dir /data/k3s
```

### 多节点集群

**部署架构**:

```text
┌─────────────┐
│  Server 1   │  (Master)
│ 192.168.1.10│
└──────┬──────┘
       │
       ├─────────┬─────────┐
       │         │         │
┌──────▼──────┐ ┌─▼───────┐ ┌─▼───────┐
│   Agent 1   │ │ Agent 2 │ │ Agent 3 │
│192.168.1.11 │ │.1.12    │ │.1.13    │
└─────────────┘ └─────────┘ └─────────┘
```

**步骤1: 部署Server节点**:

```bash
# 在Server节点 (192.168.1.10)
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --node-ip 192.168.1.10 \
  --node-name k3s-server-1

# 获取node-token (用于Agent加入)
sudo cat /var/lib/rancher/k3s/server/node-token
```

**步骤2: 加入Agent节点**:

```bash
# 在Agent节点1 (192.168.1.11)
curl -sfL https://get.k3s.io | K3S_URL=https://192.168.1.10:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -s - agent \
  --node-ip 192.168.1.11 \
  --node-name k3s-agent-1

# 在Agent节点2 (192.168.1.12)
curl -sfL https://get.k3s.io | K3S_URL=https://192.168.1.10:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -s - agent \
  --node-ip 192.168.1.12 \
  --node-name k3s-agent-2

# 在Agent节点3 (192.168.1.13)
curl -sfL https://get.k3s.io | K3S_URL=https://192.168.1.10:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -s - agent \
  --node-ip 192.168.1.13 \
  --node-name k3s-agent-3
```

**步骤3: 验证集群**:

```bash
# 在Server节点查看所有节点
kubectl get nodes

# 输出:
# NAME           STATUS   ROLES                  AGE   VERSION
# k3s-server-1   Ready    control-plane,master   5m    v1.30.5+k3s1
# k3s-agent-1    Ready    <none>                 2m    v1.30.5+k3s1
# k3s-agent-2    Ready    <none>                 2m    v1.30.5+k3s1
# k3s-agent-3    Ready    <none>                 2m    v1.30.5+k3s1

# 查看集群信息
kubectl cluster-info
```

### 高可用部署

**架构** (3个Server节点 + 3个Agent节点):

```text
┌───────────────────────────────────────┐
│        LoadBalancer / HAProxy         │
│         192.168.1.100:6443            │
└───────────────┬───────────────────────┘
                │
     ┌──────────┼──────────┐
     │          │          │
┌────▼────┐ ┌──▼─────┐ ┌──▼─────┐
│Server 1 │ │Server 2│ │Server 3│  (Embedded etcd quorum)
│  .1.11  │ │  .1.12 │ │  .1.13 │
└─────────┘ └────────┘ └────────┘
     │          │          │
     └──────────┼──────────┘
                │
     ┌──────────┼──────────┐
     │          │          │
┌────▼────┐ ┌──▼─────┐ ┌──▼─────┐
│Agent 1  │ │Agent 2 │ │Agent 3 │
│  .1.21  │ │  .1.22 │ │  .1.23 │
└─────────┘ └────────┘ └────────┘
```

**步骤1: 部署第一个Server** (初始化集群):

```bash
# Server 1 (192.168.1.11)
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --node-ip 192.168.1.11 \
  --node-name k3s-server-1 \
  --tls-san 192.168.1.100 \
  --tls-san k3s-cluster.local

# 获取token
sudo cat /var/lib/rancher/k3s/server/node-token
```

**步骤2: 加入其他Server节点**:

```bash
# Server 2 (192.168.1.12)
curl -sfL https://get.k3s.io | sh -s - server \
  --server https://192.168.1.11:6443 \
  --token <NODE_TOKEN> \
  --node-ip 192.168.1.12 \
  --node-name k3s-server-2 \
  --tls-san 192.168.1.100 \
  --tls-san k3s-cluster.local

# Server 3 (192.168.1.13)
curl -sfL https://get.k3s.io | sh -s - server \
  --server https://192.168.1.11:6443 \
  --token <NODE_TOKEN> \
  --node-ip 192.168.1.13 \
  --node-name k3s-server-3 \
  --tls-san 192.168.1.100 \
  --tls-san k3s-cluster.local
```

**步骤3: 配置HAProxy** (192.168.1.100):

```bash
# 安装HAProxy
sudo apt-get install haproxy

# 配置HAProxy
sudo tee /etc/haproxy/haproxy.cfg <<EOF
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

defaults
    log     global
    mode    tcp
    option  tcplog
    option  dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000

frontend k3s_api
    bind *:6443
    mode tcp
    default_backend k3s_servers

backend k3s_servers
    mode tcp
    balance roundrobin
    option tcp-check
    server k3s-server-1 192.168.1.11:6443 check
    server k3s-server-2 192.168.1.12:6443 check
    server k3s-server-3 192.168.1.13:6443 check

frontend stats
    bind *:8404
    mode http
    stats enable
    stats uri /stats
    stats refresh 10s
EOF

# 重启HAProxy
sudo systemctl restart haproxy
sudo systemctl enable haproxy
```

**步骤4: 加入Agent节点** (通过HAProxy):

```bash
# Agent 1 (192.168.1.21)
curl -sfL https://get.k3s.io | K3S_URL=https://192.168.1.100:6443 \
  K3S_TOKEN=<NODE_TOKEN> sh -s - agent \
  --node-ip 192.168.1.21 \
  --node-name k3s-agent-1

# Agent 2, 3类似...
```

**步骤5: 验证HA集群**:

```bash
# 查看所有节点
kubectl get nodes

# 输出:
# NAME           STATUS   ROLES                  AGE   VERSION
# k3s-server-1   Ready    control-plane,master   10m   v1.30.5+k3s1
# k3s-server-2   Ready    control-plane,master   8m    v1.30.5+k3s1
# k3s-server-3   Ready    control-plane,master   8m    v1.30.5+k3s1
# k3s-agent-1    Ready    <none>                 5m    v1.30.5+k3s1
# k3s-agent-2    Ready    <none>                 5m    v1.30.5+k3s1
# k3s-agent-3    Ready    <none>                 5m    v1.30.5+k3s1

# 测试HA: 停止一个Server节点
sudo systemctl stop k3s
# 集群应该继续正常工作

# 查看etcd状态
sudo k3s etcd-snapshot ls
```

---

## 存储集成

### Local Path Provisioner

**K3s默认存储** (开箱即用):

```yaml
# 查看StorageClass
kubectl get sc

# 输出:
# NAME                   PROVISIONER             RECLAIMPOLICY
# local-path (default)   rancher.io/local-path   Delete

# 默认存储路径: /var/lib/rancher/k3s/storage
```

**使用示例**:

```yaml
# PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 10Gi
---
# Deployment使用PVC
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "password"
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-data
        persistentVolumeClaim:
          claimName: mysql-pvc
```

**自定义存储路径**:

```bash
# 修改local-path配置
kubectl edit configmap local-path-config -n kube-system

# 修改paths字段:
# data:
#   config.json: |-
#     {
#       "nodePathMap":[
#       {
#         "node":"DEFAULT_PATH_FOR_NON_LISTED_NODES",
#         "paths":["/data/k3s-storage"]
#       }
#       ]
#     }
```

### Longhorn分布式存储

**Longhorn** (Rancher的企业级分布式存储):

```bash
# 前置条件
# 每个节点需要:
# - open-iscsi
# - util-linux
# - 至少10GB空闲磁盘空间

# 安装依赖
sudo apt-get install open-iscsi nfs-common -y

# 安装Longhorn
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.6.0/deploy/longhorn.yaml

# 等待所有Pod运行
kubectl get pods -n longhorn-system -w

# 验证安装
kubectl get sc

# 输出应该包含:
# NAME       PROVISIONER          RECLAIMPOLICY
# longhorn   driver.longhorn.io   Delete
```

**使用Longhorn**:

```yaml
# 创建PVC (自动使用Longhorn)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: longhorn-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 10Gi
```

**访问Longhorn UI**:

```bash
# 方法1: Port Forward
kubectl port-forward -n longhorn-system svc/longhorn-frontend 8080:80

# 访问: http://localhost:8080

# 方法2: Ingress (如果启用了Traefik)
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: longhorn-ingress
  namespace: longhorn-system
spec:
  rules:
  - host: longhorn.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: longhorn-frontend
            port:
              number: 80
EOF
```

---

## 网络配置

### Flannel网络

**K3s默认CNI** (VXLAN模式):

```yaml
网络信息:
  Pod CIDR: 10.42.0.0/16
  Service CIDR: 10.43.0.0/16

后端选项:
  - vxlan (默认): 适用于大多数环境
  - host-gw: 性能好，要求L2网络
  - wireguard: 加密隧道，安全性高
  - ipsec: 加密隧道，兼容性好
```

**自定义Flannel后端**:

```bash
# host-gw模式 (性能最好)
curl -sfL https://get.k3s.io | sh -s - --flannel-backend=host-gw

# WireGuard模式 (加密)
# 需要先安装WireGuard
sudo apt-get install wireguard -y
curl -sfL https://get.k3s.io | sh -s - --flannel-backend=wireguard

# IPSec模式 (加密)
curl -sfL https://get.k3s.io | sh -s - --flannel-backend=ipsec
```

**禁用Flannel (使用其他CNI)**:

```bash
# 安装K3s时禁用Flannel
curl -sfL https://get.k3s.io | sh -s - --flannel-backend=none

# 然后安装Calico
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# 或安装Cilium
helm install cilium cilium/cilium --version 1.14.5 \
  --namespace kube-system
```

### Traefik Ingress

**K3s默认Ingress控制器**:

```yaml
# 查看Traefik
kubectl get pods -n kube-system | grep traefik

# 查看Traefik Service
kubectl get svc -n kube-system traefik
```

**基础Ingress示例**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: whoami
spec:
  replicas: 2
  selector:
    matchLabels:
      app: whoami
  template:
    metadata:
      labels:
        app: whoami
    spec:
      containers:
      - name: whoami
        image: traefik/whoami
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: whoami
spec:
  selector:
    app: whoami
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: whoami
spec:
  rules:
  - host: whoami.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: whoami
            port:
              number: 80
```

**TLS支持**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: whoami-tls
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: whoami-tls
spec:
  tls:
  - hosts:
    - whoami.example.com
    secretName: whoami-tls
  rules:
  - host: whoami.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: whoami
            port:
              number: 80
```

**替换为Nginx Ingress**:

```bash
# 1. 禁用Traefik
curl -sfL https://get.k3s.io | sh -s - --disable traefik

# 2. 安装Nginx Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/baremetal/deploy.yaml
```

### Service Load Balancer

**K3s内置LoadBalancer** (ServiceLB/Klipper-LB):

```yaml
# 创建LoadBalancer类型Service
apiVersion: v1
kind: Service
metadata:
  name: nginx-lb
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80

# K3s会自动:
# 1. 创建DaemonSet (klipper-lb-xxxx)
# 2. 分配节点IP作为EXTERNAL-IP
# 3. 配置iptables规则
```

**查看LoadBalancer**:

```bash
# 查看Service
kubectl get svc

# 输出:
# NAME       TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)
# nginx-lb   LoadBalancer   10.43.100.50    192.168.1.11    80:30080/TCP

# 查看klipper-lb Pod
kubectl get pods -n kube-system | grep klipper-lb

# 访问服务
curl http://192.168.1.11
```

**使用MetalLB (更强大)**:

```bash
# 1. 禁用ServiceLB
curl -sfL https://get.k3s.io | sh -s - --disable servicelb

# 2. 安装MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.3/config/manifests/metallb-native.yaml

# 3. 配置IP池
kubectl apply -f - <<EOF
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.200-192.168.1.250
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default
  namespace: metallb-system
spec:
  ipAddressPools:
  - default-pool
EOF
```

---

继续编写剩余章节...

## ARM与边缘设备

### ARM64支持

**K3s原生支持ARM**:

```yaml
支持的架构:
  - amd64 (x86_64)
  - arm64 (aarch64)
  - armhf (ARMv7)

镜像:
  - 官方镜像自动适配
  - 多架构镜像支持
  - 无需手动选择架构
```

**在ARM设备上安装**:

```bash
# 树莓派/ARM服务器安装
curl -sfL https://get.k3s.io | sh -

# 验证架构
kubectl get nodes -o wide

# 输出:
# NAME   STATUS   ROLES   AGE   VERSION   ARCH
# rpi4   Ready    master  1m    v1.30.5   arm64
```

### 树莓派部署

**硬件要求**:

```yaml
推荐配置:
  型号: 树莓派4B / 5
  RAM: 4GB+ (最低2GB)
  存储: 32GB+ SD卡 (推荐SSD)
  网络: 千兆以太网

操作系统:
  - Raspberry Pi OS Lite (64-bit)
  - Ubuntu Server 22.04 ARM64
```

**系统准备**:

```bash
# 1. 启用cgroup (必需)
sudo nano /boot/cmdline.txt
# 添加: cgroup_memory=1 cgroup_enable=memory

# 或使用sed命令
sudo sed -i '$ s/$/ cgroup_memory=1 cgroup_enable=memory/' /boot/cmdline.txt

# 2. 重启
sudo reboot

# 3. 验证cgroup
cat /proc/cgroups | grep memory

# 4. 安装K3s
curl -sfL https://get.k3s.io | sh -

# 5. 验证
sudo k3s kubectl get nodes
```

**树莓派集群示例**:

```text
┌────────────┐
│   树莓派1  │  (Server)
│   4GB RAM  │
│   主节点   │
└─────┬──────┘
      │
      ├─────────┬─────────┐
      │         │         │
┌─────▼──┐ ┌───▼────┐ ┌──▼─────┐
│树莓派2 │ │树莓派3 │ │树莓派4 │  (Agent)
│2GB RAM │ │2GB RAM │ │2GB RAM │
│工作节点│ │工作节点│ │工作节点│
└────────┘ └────────┘ └────────┘
```

**性能优化**:

```bash
# 使用SSD而非SD卡
# 1. USB SSD启动
# 2. 修改boot配置

# 限制资源使用
curl -sfL https://get.k3s.io | sh -s - server \
  --kubelet-arg="eviction-hard=memory.available<200Mi" \
  --kubelet-arg="eviction-soft=memory.available<300Mi" \
  --kubelet-arg="eviction-soft-grace-period=memory.available=1m" \
  --kubelet-arg="system-reserved=cpu=200m,memory=200Mi"
```

### NVIDIA Jetson

**Jetson平台支持**:

```yaml
支持设备:
  - Jetson Nano
  - Jetson Xavier NX
  - Jetson AGX Xavier
  - Jetson Orin

特性:
  - GPU加速
  - CUDA支持
  - TensorRT推理
  - 边缘AI工作负载
```

**安装步骤**:

```bash
# 1. 安装JetPack SDK
# (从NVIDIA官网下载并安装)

# 2. 安装Docker (如果未安装)
sudo apt-get install docker.io -y

# 3. 安装NVIDIA Container Runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-runtime

# 4. 配置Docker使用NVIDIA runtime
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<EOF
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
EOF

sudo systemctl restart docker

# 5. 安装K3s (使用Docker作为运行时)
curl -sfL https://get.k3s.io | sh -s - --docker

# 6. 安装NVIDIA Device Plugin
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml

# 7. 验证GPU
kubectl get nodes -o json | jq '.items[].status.allocatable'
# 应该看到 "nvidia.com/gpu": "1"
```

**GPU工作负载示例**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cuda-test
spec:
  restartPolicy: OnFailure
  containers:
  - name: cuda-container
    image: nvcr.io/nvidia/cuda:11.8.0-base-ubuntu22.04
    command: ["nvidia-smi"]
    resources:
      limits:
        nvidia.com/gpu: 1  # 请求1个GPU
```

---

## 生产部署

### 系统要求

**最低要求**:

```yaml
Server节点:
  CPU: 1核
  RAM: 512MB
  磁盘: 10GB

Agent节点:
  CPU: 1核
  RAM: 512MB
  磁盘: 5GB

推荐配置:
  Server节点:
    CPU: 2核+
    RAM: 2GB+
    磁盘: 20GB+ SSD

  Agent节点:
    CPU: 2核+
    RAM: 2GB+
    磁盘: 20GB+ SSD

网络:
  - 所有节点互通
  - Server节点: 6443 (API), 10250 (Kubelet)
  - Agent节点: 10250 (Kubelet)
  - Flannel: 8472 (VXLAN), 51820 (WireGuard)
```

**操作系统**:

```yaml
支持的Linux发行版:
  - Ubuntu 20.04/22.04/24.04
  - Debian 11/12
  - RHEL/CentOS 8/9
  - Rocky Linux 8/9
  - openSUSE Leap 15.x
  - Raspberry Pi OS

内核要求:
  - 最低: 3.10
  - 推荐: 5.x+

必需模块:
  - br_netfilter
  - overlay
  - iptables
```

### 安全加固

**1. 禁用默认ServiceAccount自动挂载**:

```bash
# Server配置
curl -sfL https://get.k3s.io | sh -s - server \
  --kube-apiserver-arg="enable-admission-plugins=NamespaceLifecycle,LimitRanger,ServiceAccount,TaintNodesByCondition,Priority,DefaultTolerationSeconds,DefaultStorageClass,PersistentVolumeClaimResize,MutatingAdmissionWebhook,ValidatingAdmissionWebhook,ResourceQuota,NodeRestriction,PodSecurityPolicy"
```

**2. 限制API Server访问**:

```bash
# 只监听内网IP
curl -sfL https://get.k3s.io | sh -s - server \
  --bind-address 192.168.1.10 \
  --advertise-address 192.168.1.10
```

**3. 启用审计日志**:

```yaml
# 审计策略
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
- level: Request
  verbs: ["create", "update", "patch", "delete"]
```

```bash
# 启动时指定审计配置
curl -sfL https://get.k3s.io | sh -s - server \
  --kube-apiserver-arg="audit-log-path=/var/log/k3s-audit.log" \
  --kube-apiserver-arg="audit-log-maxage=30" \
  --kube-apiserver-arg="audit-log-maxbackup=10" \
  --kube-apiserver-arg="audit-log-maxsize=100" \
  --kube-apiserver-arg="audit-policy-file=/etc/k3s/audit-policy.yaml"
```

**4. Network Policy**:

```yaml
# 默认拒绝所有入站流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
---
# 只允许特定流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-nginx
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: nginx
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 80
```

**5. Pod Security Standards**:

```yaml
# Namespace级别限制
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 性能优化

**1. Server节点优化**:

```bash
curl -sfL https://get.k3s.io | sh -s - server \
  --kube-apiserver-arg="max-requests-inflight=400" \
  --kube-apiserver-arg="max-mutating-requests-inflight=200" \
  --kube-controller-manager-arg="node-monitor-period=10s" \
  --kube-controller-manager-arg="node-monitor-grace-period=20s" \
  --kube-controller-manager-arg="pod-eviction-timeout=30s"
```

**2. Agent节点优化**:

```bash
curl -sfL https://get.k3s.io | K3S_URL=https://server:6443 \
  K3S_TOKEN=xxx sh -s - agent \
  --kubelet-arg="max-pods=110" \
  --kubelet-arg="pod-max-pids=4096" \
  --kubelet-arg="image-gc-high-threshold=85" \
  --kubelet-arg="image-gc-low-threshold=80"
```

**3. 数据库优化 (外部etcd)**:

```bash
# 使用SSD
# 调整etcd参数
curl -sfL https://get.k3s.io | sh -s - server \
  --datastore-endpoint="https://etcd1:2379,https://etcd2:2379,https://etcd3:2379" \
  --datastore-cafile=/etc/etcd/ca.pem \
  --datastore-certfile=/etc/etcd/server.pem \
  --datastore-keyfile=/etc/etcd/server-key.pem \
  --etcd-arg="heartbeat-interval=200" \
  --etcd-arg="election-timeout=2000" \
  --etcd-arg="snapshot-count=10000"
```

**4. 网络优化**:

```bash
# 使用host-gw模式 (L2网络)
curl -sfL https://get.k3s.io | sh -s - --flannel-backend=host-gw

# 或启用WireGuard加密
curl -sfL https://get.k3s.io | sh -s - --flannel-backend=wireguard
```

---

## 监控运维

### 监控方案

**方案1: K3s内置指标**:

```bash
# 查看节点资源
kubectl top nodes

# 查看Pod资源
kubectl top pods -A

# 查看特定Pod
kubectl top pod nginx-xxx
```

**方案2: Prometheus + Grafana**:

```bash
# 安装kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 安装 (针对K3s优化)
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set prometheus.prometheusSpec.retention=7d \
  --set prometheus.prometheusSpec.resources.requests.memory=400Mi \
  --set grafana.persistence.enabled=true \
  --set grafana.persistence.size=5Gi

# 访问Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# 默认账号: admin / prom-operator
```

**方案3: K9s (终端UI)**:

```bash
# 安装K9s
wget https://github.com/derailed/k9s/releases/download/v0.31.0/k9s_Linux_amd64.tar.gz
tar -xzf k9s_Linux_amd64.tar.gz
sudo mv k9s /usr/local/bin/

# 运行
k9s

# 常用快捷键:
# :pods    - 查看Pods
# :nodes   - 查看Nodes
# :deploy  - 查看Deployments
# :svc     - 查看Services
# l        - 查看日志
# d        - 描述资源
# e        - 编辑资源
```

### 日志管理

**方案1: 查看原始日志**:

```bash
# K3s Server日志
sudo journalctl -u k3s -f

# K3s Agent日志
sudo journalctl -u k3s-agent -f

# Pod日志
kubectl logs <pod-name> -f

# 多容器Pod
kubectl logs <pod-name> -c <container-name> -f

# 所有副本日志
kubectl logs -l app=nginx --all-containers=true -f
```

**方案2: Loki + Grafana**:

```bash
# 安装Loki Stack
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install loki grafana/loki-stack \
  --namespace logging --create-namespace \
  --set grafana.enabled=true \
  --set prometheus.enabled=true \
  --set promtail.enabled=true

# 访问Grafana
kubectl port-forward -n logging svc/loki-grafana 3000:80

# 添加Loki数据源: http://loki:3100
```

### 备份恢复

**1. 备份K3s集群数据**:

```bash
# SQLite备份 (单节点)
sudo k3s etcd-snapshot save --name backup-$(date +%Y%m%d-%H%M%S)

# 查看备份
sudo k3s etcd-snapshot ls

# 输出:
# Name: backup-20241019-103000
# Location: /var/lib/rancher/k3s/server/db/snapshots
# Size: 5.2MB

# 定时备份 (cron)
sudo crontab -e
# 添加: 0 2 * * * /usr/local/bin/k3s etcd-snapshot save --name backup-$(date +\%Y\%m\%d-\%H\%M\%S)
```

**2. 从备份恢复**:

```bash
# 停止K3s
sudo systemctl stop k3s

# 恢复快照
sudo k3s server \
  --cluster-reset \
  --cluster-reset-restore-path=/var/lib/rancher/k3s/server/db/snapshots/backup-20241019-103000

# 启动K3s
sudo systemctl start k3s

# 验证
kubectl get nodes
```

**3. 备份到S3**:

```bash
# 配置S3访问
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx

# 备份到S3
sudo k3s etcd-snapshot save \
  --name backup-$(date +%Y%m%d-%H%M%S) \
  --s3 \
  --s3-bucket=k3s-backups \
  --s3-region=us-west-2 \
  --s3-endpoint=s3.amazonaws.com

# 从S3恢复
sudo k3s server \
  --cluster-reset \
  --cluster-reset-restore-path=s3://k3s-backups/backup-20241019-103000
```

**4. 应用数据备份 (Velero)**:

```bash
# 安装Velero CLI
wget https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/velero-v1.12.0-linux-amd64.tar.gz
tar -xzf velero-v1.12.0-linux-amd64.tar.gz
sudo mv velero-v1.12.0-linux-amd64/velero /usr/local/bin/

# 安装Velero (使用Minio)
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket k3s-backups \
  --secret-file ./credentials-velero \
  --use-volume-snapshots=false \
  --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://minio.default.svc:9000

# 备份namespace
velero backup create production-backup --include-namespaces production

# 恢复
velero restore create --from-backup production-backup
```

---

## 应用场景

### 边缘计算

**场景**: 工业IoT边缘网关

```yaml
架构:
  ┌──────────────────┐
  │   Cloud (K8s)    │  集中管理
  └────────┬─────────┘
           │
    ┌──────┴──────┬──────────┐
    │             │          │
  ┌─▼──┐       ┌──▼─┐     ┌─▼──┐
  │K3s │       │K3s │     │K3s │  边缘网关
  │工厂A│       │工厂B│     │工厂C│  (Jetson/ARM)
  └─┬──┘       └──┬─┘     └─┬──┘
    │             │          │
  [设备]        [设备]     [设备]  传感器/PLC

部署清单:
  - MQTT Broker: 设备数据采集
  - Node-RED: 数据处理
  - InfluxDB: 时序数据存储
  - Grafana: 本地可视化
  - AI推理: TensorFlow Lite
```

**示例配置**:

```yaml
# MQTT Broker
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mosquitto
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mosquitto
  template:
    metadata:
      labels:
        app: mosquitto
    spec:
      containers:
      - name: mosquitto
        image: eclipse-mosquitto:2.0
        ports:
        - containerPort: 1883
        - containerPort: 9001
        volumeMounts:
        - name: config
          mountPath: /mosquitto/config
        - name: data
          mountPath: /mosquitto/data
      volumes:
      - name: config
        configMap:
          name: mosquitto-config
      - name: data
        persistentVolumeClaim:
          claimName: mosquitto-data
---
# Node-RED
apiVersion: apps/v1
kind: Deployment
metadata:
  name: node-red
spec:
  replicas: 1
  selector:
    matchLabels:
      app: node-red
  template:
    metadata:
      labels:
        app: node-red
    spec:
      containers:
      - name: node-red
        image: nodered/node-red:latest
        ports:
        - containerPort: 1880
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: node-red-data
```

### IoT网关

**场景**: 智能家居边缘控制器

```yaml
硬件:
  - 树莓派4 (4GB)
  - Zigbee/Z-Wave USB适配器
  - UPS电源

软件栈:
  - K3s: 容器编排
  - Home Assistant: 智能家居中枢
  - Zigbee2MQTT: Zigbee设备桥接
  - Node-RED: 自动化规则
  - InfluxDB: 数据存储
  - Grafana: 监控面板
```

### CI/CD环境

**场景**: 轻量级开发测试集群

```yaml
用途:
  - GitLab Runner
  - Jenkins Agent
  - 应用测试环境
  - 多租户开发环境

优势:
  - 快速启动 (<30秒)
  - 资源占用小
  - 易于重置
  - 接近生产K8s环境
```

**GitLab Runner示例**:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: gitlab-runner-config
data:
  config.toml: |
    concurrent = 4
    check_interval = 3
    [[runners]]
      name = "k3s-runner"
      url = "https://gitlab.com/"
      token = "YOUR_TOKEN"
      executor = "kubernetes"
      [runners.kubernetes]
        namespace = "gitlab"
        privileged = true
        image = "alpine:latest"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gitlab-runner
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gitlab-runner
  template:
    metadata:
      labels:
        app: gitlab-runner
    spec:
      serviceAccountName: gitlab-runner
      containers:
      - name: gitlab-runner
        image: gitlab/gitlab-runner:latest
        volumeMounts:
        - name: config
          mountPath: /etc/gitlab-runner
      volumes:
      - name: config
        configMap:
          name: gitlab-runner-config
```

---

## 最佳实践

### 1. 资源规划

```yaml
节点规划:
  小型部署 (1-10节点):
    - 1-3个Server节点
    - SQLite或Embedded etcd
    - 单一数据中心

  中型部署 (10-50节点):
    - 3个Server节点 (HA)
    - Embedded etcd
    - 考虑外部存储

  大型部署 (50+节点):
    - 3-5个Server节点
    - 外部etcd集群
    - 分区/多集群架构

资源预留:
  Server节点:
    - CPU: 预留20%
    - Memory: 预留30%
    - Disk: 预留40%

  Agent节点:
    - CPU: 预留10%
    - Memory: 预留20%
    - Disk: 预留30%
```

### 2. 网络优化

```yaml
选择合适的CNI:
  - Flannel VXLAN: 通用，兼容性好
  - Flannel host-gw: 性能好，需L2网络
  - Flannel WireGuard: 加密，安全性高
  - Calico: 高级策略，大规模
  - Cilium: eBPF，高性能

优化参数:
  # 增加连接跟踪
  net.netfilter.nf_conntrack_max=1000000

  # 优化TCP
  net.ipv4.tcp_tw_reuse=1
  net.ipv4.tcp_fin_timeout=30
  net.core.netdev_max_backlog=5000
```

### 3. 安全建议

```yaml
1. 最小权限原则:
   - 使用RBAC限制权限
   - 禁用默认ServiceAccount
   - 启用Pod Security Standards

2. 网络隔离:
   - 使用NetworkPolicy
   - 分离管理网络和数据网络
   - 限制API Server访问

3. 定期更新:
   - 及时更新K3s版本
   - 扫描镜像漏洞
   - 审计集群配置

4. 数据保护:
   - 定期备份
   - 加密存储
   - 访问审计

5. 供应链安全:
   - 使用签名镜像
   - 私有镜像仓库
   - 镜像扫描
```

---

## 与Kubernetes对比

### 功能对比

| 特性 | Kubernetes | K3s | 说明 |
|------|-----------|-----|------|
| **API兼容性** | 100% | 100% | K3s是认证的K8s发行版 |
| **二进制大小** | ~1.5GB | <70MB | K3s极致精简 |
| **内存占用** | 2-4GB+ | 512MB+ | K3s资源消耗低 |
| **安装时间** | 30-60分钟 | <30秒 | K3s一键安装 |
| **控制平面** | 多进程 | 单进程 | K3s简化架构 |
| **数据存储** | 需外部etcd | 内置SQLite/etcd | K3s开箱即用 |
| **CNI插件** | 需单独安装 | 内置Flannel | K3s预集成 |
| **Ingress** | 需单独安装 | 内置Traefik | K3s预集成 |
| **存储** | 需配置 | 内置Local Path | K3s预集成 |
| **LoadBalancer** | 需云提供商 | 内置ServiceLB | K3s自带 |
| **ARM支持** | 需手动适配 | 原生支持 | K3s优化 |
| **边缘场景** | 需优化 | 开箱即用 | K3s专为边缘设计 |

### 性能对比

```yaml
启动时间:
  K8s: 3-5分钟
  K3s: 10-30秒

内存基线:
  K8s: 2GB+
  K3s: 512MB

API响应延迟:
  K8s: 50-100ms
  K3s: 30-80ms

Pod启动时间:
  K8s: 5-15秒
  K3s: 3-10秒
```

### 选型建议

```yaml
选择K8s的场景:
  - 大规模生产环境 (100+节点)
  - 需要高级特性 (alpha/beta features)
  - 多租户隔离要求高
  - 已有K8s运维团队
  - 云上托管服务 (EKS/GKE/AKS)

选择K3s的场景:
  ✅ 边缘计算
  ✅ IoT网关
  ✅ 资源受限环境
  ✅ ARM设备 (树莓派/Jetson)
  ✅ CI/CD环境
  ✅ 开发测试
  ✅ 快速原型
  ✅ 单节点或小规模集群 (<50节点)
  ✅ 需要快速部署
  ✅ 简化运维
```

---

## 参考资料

### 官方资源

- [K3s Official Site](https://k3s.io/)
- [K3s GitHub](https://github.com/k3s-io/k3s)
- [K3s Documentation](https://docs.k3s.io/)
- [Rancher Official Site](https://www.rancher.com/)

### 社区资源

- [K3s Slack](https://slack.rancher.io/)
- [K3s中文社区](https://github.com/kingsd041/k3s-tutorial)
- [Awesome K3s](https://github.com/k3s-io/awesome-k3s)

**相关项目**:

- [K3d](https://k3d.io/) - K3s in Docker (本地开发)
- [K3sup](https://github.com/alexellis/k3sup) - K3s自动化部署工具
- [Longhorn](https://longhorn.io/) - 分布式存储
- [Rancher](https://www.rancher.com/) - 多集群管理

---

**文档版本**: v1.0
**最后更新**: 2025-10-19
**维护者**: 虚拟化容器化技术知识库项目组

**下一步阅读**:

- [01_边缘计算概述与架构](./01_边缘计算概述与架构.md)
- [02_KubeEdge技术详解](./02_KubeEdge技术详解.md)
- [04_5G边缘计算(MEC)](./04_5G边缘计算MEC.md)
- [05_边缘存储与数据管理](./05_边缘存储与数据管理.md)

---

## 相关文档

### 本模块相关

- [边缘计算概述与架构](./01_边缘计算概述与架构.md) - 边缘计算概述与架构
- [KubeEdge技术详解](./02_KubeEdge技术详解.md) - KubeEdge技术详解
- [5G边缘计算MEC](./04_5G边缘计算MEC.md) - 5G边缘计算MEC详解
- [边缘存储与数据管理](./05_边缘存储与数据管理.md) - 边缘存储与数据管理
- [边缘AI与推理优化](./06_边缘AI与推理优化.md) - 边缘AI与推理优化
- [边缘网络与通信](./07_边缘网络与通信.md) - 边缘网络与通信
- [边缘安全与运维](./08_边缘安全与运维.md) - 边缘安全与运维
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [Kubernetes技术详解](../03_Kubernetes技术详解/README.md) - Kubernetes技术体系
- [容器编排技术](../04_容器编排技术/README.md) - 容器编排技术
- [容器存储技术](../05_容器存储技术/README.md) - 容器存储技术
- [容器监控与运维](../06_容器监控与运维/README.md) - 容器监控运维

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新
