# Longhorn 存储

> **返回**: [容器存储首页](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 文档元信息

| 属性 | 值 |
|------|-----|
| **文档版本** | v2.0 (2025改进版) |
| **更新日期** | 2025-10-21 |
| **Longhorn版本** | v1.6 (Latest), v1.5 |
| **兼容版本** | Kubernetes v1.21+ |
| **标准对齐** | CNCF Sandbox Project, CSI v1.9.0 |
| **状态** | 生产就绪 |

> **版本锚点**: 本文档严格对齐Longhorn v1.6与CSI v1.9.0规范。

---

## 📋 目录

- [Longhorn 存储](#longhorn-存储)
  - [文档元信息](#文档元信息)
  - [📋 目录](#-目录)
  - [1. Longhorn 概述](#1-longhorn-概述)
    - [1.1 什么是 Longhorn](#11-什么是-longhorn)
    - [1.2 核心特性](#12-核心特性)
    - [1.3 适用场景](#13-适用场景)
    - [1.4 与其他存储方案对比](#14-与其他存储方案对比)
  - [2. Longhorn 架构](#2-longhorn-架构)
    - [2.1 整体架构](#21-整体架构)
    - [2.2 核心组件](#22-核心组件)
      - [2.2.1 Longhorn Manager](#221-longhorn-manager)
      - [2.2.2 Longhorn Engine](#222-longhorn-engine)
      - [2.2.3 CSI Driver](#223-csi-driver)
      - [2.2.4 UI (Web Console)](#224-ui-web-console)
    - [2.3 数据路径](#23-数据路径)
    - [2.4 工作原理](#24-工作原理)
      - [2.4.1 卷创建流程](#241-卷创建流程)
      - [2.4.2 副本同步机制](#242-副本同步机制)
  - [3. Longhorn 安装部署](#3-longhorn-安装部署)
    - [3.1 环境准备](#31-环境准备)
      - [3.1.1 系统要求](#311-系统要求)
      - [3.1.2 依赖检查](#312-依赖检查)
      - [3.1.3 环境检查脚本](#313-环境检查脚本)
    - [3.2 Helm 安装](#32-helm-安装)
      - [3.2.1 添加 Helm 仓库](#321-添加-helm-仓库)
      - [3.2.2 自定义配置](#322-自定义配置)
      - [3.2.3 安装 Longhorn](#323-安装-longhorn)
    - [3.3 kubectl 安装](#33-kubectl-安装)
    - [3.4 Rancher 集成安装](#34-rancher-集成安装)
    - [3.5 验证安装](#35-验证安装)
      - [3.5.1 检查 Pod 状态](#351-检查-pod-状态)
      - [3.5.2 检查 StorageClass](#352-检查-storageclass)
      - [3.5.3 访问 Web UI](#353-访问-web-ui)
      - [3.5.4 创建测试卷](#354-创建测试卷)
  - [4. 卷管理](#4-卷管理)
    - [4.1 创建 StorageClass](#41-创建-storageclass)
      - [4.1.1 基础 StorageClass](#411-基础-storageclass)
      - [4.1.2 高性能 StorageClass](#412-高性能-storageclass)
      - [4.1.3 高可用 StorageClass](#413-高可用-storageclass)
    - [4.2 动态卷供应](#42-动态卷供应)
    - [4.3 卷克隆](#43-卷克隆)
    - [4.4 卷快照](#44-卷快照)
      - [4.4.1 创建 VolumeSnapshotClass](#441-创建-volumesnapshotclass)
      - [4.4.2 创建快照](#442-创建快照)
      - [4.4.3 从快照恢复](#443-从快照恢复)
    - [4.5 卷扩容](#45-卷扩容)
    - [4.6 卷迁移](#46-卷迁移)
  - [5. 备份与恢复](#5-备份与恢复)
    - [5.1 备份目标配置](#51-备份目标配置)
      - [5.1.1 S3 备份目标](#511-s3-备份目标)
      - [5.1.2 NFS 备份目标](#512-nfs-备份目标)
    - [5.2 手动备份](#52-手动备份)
    - [5.3 定时备份](#53-定时备份)
    - [5.4 跨集群备份](#54-跨集群备份)
    - [5.5 灾难恢复](#55-灾难恢复)
      - [5.5.1 完整集群恢复流程](#551-完整集群恢复流程)
      - [5.5.2 RPO/RTO 指标](#552-rporto-指标)
  - [6. 高可用配置](#6-高可用配置)
    - [6.1 副本策略](#61-副本策略)
    - [6.2 节点故障恢复](#62-节点故障恢复)
    - [6.3 数据局部性](#63-数据局部性)
    - [6.4 反亲和性](#64-反亲和性)
  - [7. 监控与告警](#7-监控与告警)
    - [7.1 Prometheus 集成](#71-prometheus-集成)
    - [7.2 Grafana 仪表板](#72-grafana-仪表板)
    - [7.3 告警规则](#73-告警规则)
    - [7.4 日志收集](#74-日志收集)
  - [8. 故障排查](#8-故障排查)
    - [8.1 常见问题](#81-常见问题)
      - [8.1.1 Pod 无法启动: `MountVolume.MountDevice failed`](#811-pod-无法启动-mountvolumemountdevice-failed)
      - [8.1.2 卷降级 (Degraded)](#812-卷降级-degraded)
      - [8.1.3 备份失败](#813-备份失败)
    - [8.2 诊断命令](#82-诊断命令)
    - [8.3 日志分析](#83-日志分析)
    - [8.4 故障恢复流程](#84-故障恢复流程)
  - [9. 性能优化](#9-性能优化)
    - [9.1 存储性能调优](#91-存储性能调优)
      - [9.1.1 使用 SSD 磁盘](#911-使用-ssd-磁盘)
      - [9.1.2 优化副本数](#912-优化副本数)
      - [9.1.3 启用数据局部性](#913-启用数据局部性)
    - [9.2 网络性能优化](#92-网络性能优化)
    - [9.3 资源限制](#93-资源限制)
    - [9.4 性能测试](#94-性能测试)
  - [10. 最佳实践](#10-最佳实践)
    - [10.1 生产环境部署](#101-生产环境部署)
    - [10.2 容量规划](#102-容量规划)
    - [10.3 安全加固](#103-安全加固)
    - [10.4 升级策略](#104-升级策略)
    - [10.5 部署前检查清单](#105-部署前检查清单)
  - [总结](#总结)

---

## 1. Longhorn 概述

### 1.1 什么是 Longhorn

**Longhorn** 是由 Rancher Labs（现为SUSE子公司）开发的**轻量级、可靠的分布式块存储系统**，专为 Kubernetes 设计。

**核心理念**:

- **简单易用**: 一键安装，通过 Web UI 管理
- **云原生**: 完全基于 Kubernetes CRD 实现
- **企业级功能**: 快照、备份、灾备、高可用
- **开源免费**: Apache 2.0 许可证，CNCF 沙箱项目

**技术特点**:

```text
┌─────────────────────────────────────────────┐
│           Longhorn 存储架构                  │
├─────────────────────────────────────────────┤
│  应用层: Pod (通过 PVC 挂载存储)             │
├─────────────────────────────────────────────┤
│  编排层: Kubernetes (CSI Driver)            │
├─────────────────────────────────────────────┤
│  存储层: Longhorn Manager + Engine          │
├─────────────────────────────────────────────┤
│  数据层: 本地磁盘 (每个节点)                  │
└─────────────────────────────────────────────┘
```

---

### 1.2 核心特性

| 特性类别 | 功能说明 |
|---------|---------|
| **卷管理** | 动态供应、卷克隆、卷快照、在线扩容 |
| **备份恢复** | 增量备份到 NFS/S3、定时备份、跨集群恢复 |
| **高可用** | 多副本同步、自动故障转移、节点容错 |
| **数据保护** | 快照策略、备份策略、数据校验 |
| **可观测性** | Prometheus 指标、Web UI、日志审计 |
| **性能优化** | 数据局部性、读缓存、SSD 优化 |

---

### 1.3 适用场景

✅ **推荐场景**:

- **中小型 Kubernetes 集群** (3-50 节点)
- **边缘计算环境** (K3s/K8s)
- **开发测试环境** (快速部署、易管理)
- **无共享存储场景** (利用本地磁盘构建分布式存储)
- **需要简单备份方案** (内置 S3/NFS 备份)

❌ **不推荐场景**:

- **超大规模集群** (>100 节点，考虑 Ceph)
- **极高 IOPS 要求** (>100k IOPS，考虑企业 SAN)
- **文件存储需求** (Longhorn 仅支持块存储，考虑 CephFS)
- **对象存储需求** (考虑 MinIO/Ceph RGW)

---

### 1.4 与其他存储方案对比

| 对比项 | Longhorn | Rook-Ceph | OpenEBS | Portworx |
|-------|---------|----------|---------|---------|
| **复杂度** | ⭐⭐ (简单) | ⭐⭐⭐⭐ (复杂) | ⭐⭐⭐ (中等) | ⭐⭐⭐ (中等) |
| **存储类型** | 块存储 | 块/文件/对象 | 块存储 | 块/文件 |
| **性能** | 中等 | 高 | 中高 | 高 |
| **资源占用** | 低 | 高 | 中 | 中 |
| **备份恢复** | ⭐⭐⭐⭐ (优秀) | ⭐⭐⭐ (良好) | ⭐⭐ (基础) | ⭐⭐⭐⭐ (优秀) |
| **Web UI** | ✅ (友好) | ⚠️ (需安装 Dashboard) | ❌ | ✅ (商业版) |
| **社区支持** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ (商业) |
| **最小节点数** | 3 | 3 | 1 | 3 |
| **开源许可** | Apache 2.0 | Apache 2.0 | Apache 2.0 | 商业许可 |

**选型建议**:

- **Longhorn**: 中小型集群、边缘计算、快速上手
- **Rook-Ceph**: 大型生产环境、需要文件/对象存储
- **OpenEBS**: 本地存储优化、高性能块存储
- **Portworx**: 企业级功能、商业支持

---

## 2. Longhorn 架构

### 2.1 整体架构

```text
┌──────────────────────────────────────────────────────────────────┐
│                      Kubernetes 集群                              │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐│
│  │  Node 1         │   │  Node 2         │   │  Node 3         ││
│  │  ┌───────────┐  │   │  ┌───────────┐  │   │  ┌───────────┐  ││
│  │  │ Longhorn  │  │   │  │ Longhorn  │  │   │  │ Longhorn  │  ││
│  │  │ Manager   │◄─┼───┼─►│ Manager   │◄─┼───┼─►│ Manager   │  ││
│  │  └─────┬─────┘  │   │  └─────┬─────┘  │   │  └─────┬─────┘  ││
│  │        │        │   │        │        │   │        │        ││
│  │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  ││
│  │  │ Engine    │  │   │  │ Engine    │  │   │  │ Engine    │  ││
│  │  │ (Primary) │  │   │  │ (Replica) │  │   │  │ (Replica) │  ││
│  │  └─────┬─────┘  │   │  └─────┬─────┘  │   │  └─────┬─────┘  ││
│  │        │        │   │        │        │   │        │        ││
│  │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  │   │  ┌─────▼─────┐  ││
│  │  │ Replica   │  │   │  │ Replica   │  │   │  │ Replica   │  ││
│  │  │ (Local    │  │   │  │ (Local    │  │   │  │ (Local    │  ││
│  │  │ Disk)     │  │   │  │ Disk)     │  │   │  │ Disk)     │  ││
│  │  └───────────┘  │   │  └───────────┘  │   │  └───────────┘  ││
│  └─────────────────┘   └─────────────────┘   └─────────────────┘│
└──────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    ┌─────────┴──────────┐
                    │  Backup Target     │
                    │  (S3/NFS)          │
                    └────────────────────┘
```

---

### 2.2 核心组件

#### 2.2.1 Longhorn Manager

**职责**:

- **卷生命周期管理**: 创建、删除、附加、分离卷
- **副本调度**: 决定副本在哪些节点上创建
- **监控与健康检查**: 监控卷和副本状态
- **API 服务**: 提供 REST API 和 Web UI

**部署形式**:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: longhorn-manager
  namespace: longhorn-system
spec:
  selector:
    matchLabels:
      app: longhorn-manager
  template:
    spec:
      containers:
      - name: longhorn-manager
        image: longhornio/longhorn-manager:v1.6.0
        ports:
        - containerPort: 9500  # API 端口
```

---

#### 2.2.2 Longhorn Engine

**职责**:

- **I/O 处理**: 处理来自 Pod 的读写请求
- **数据复制**: 将数据同步到多个副本
- **快照管理**: 创建和管理快照
- **备份协调**: 将数据备份到远程存储

**工作模式**:

- **主副本 (Primary Replica)**: 处理写请求
- **从副本 (Secondary Replicas)**: 接收同步数据

**架构示意**:

```text
Pod (iSCSI Client)
        │
        ▼
┌───────────────────┐
│ Longhorn Engine   │
│   (Primary)       │
├───────────────────┤
│  ┌─────────────┐  │
│  │   Replica   │  │ ◄── 本地副本
│  └─────────────┘  │
└────────┬──────────┘
         │ (gRPC 同步)
         ├────────────────────┐
         ▼                    ▼
┌───────────────────┐  ┌───────────────────┐
│ Longhorn Engine   │  │ Longhorn Engine   │
│   (Replica)       │  │   (Replica)       │
├───────────────────┤  ├───────────────────┤
│  ┌─────────────┐  │  │  ┌─────────────┐  │
│  │   Replica   │  │  │  │   Replica   │  │
│  └─────────────┘  │  │  └─────────────┘  │
└───────────────────┘  └───────────────────┘
```

---

#### 2.2.3 CSI Driver

**职责**:

- **卷附加/分离**: 将 Longhorn 卷附加到 Pod 所在节点
- **卷挂载**: 挂载块设备到 Pod 容器
- **卷扩容**: 在线扩容 PVC

**组件**:

```yaml
# CSI Plugin (DaemonSet)
- longhorn-csi-plugin

# CSI Attacher (Deployment)
- csi-attacher

# CSI Provisioner (Deployment)
- csi-provisioner

# CSI Resizer (Deployment)
- csi-resizer

# CSI Snapshotter (Deployment)
- csi-snapshotter
```

---

#### 2.2.4 UI (Web Console)

**功能**:

- 卷管理 (创建、删除、附加、分离)
- 快照管理
- 备份管理
- 节点管理
- 监控仪表板

**访问地址**:

```bash
# 暴露 UI 服务
kubectl -n longhorn-system port-forward svc/longhorn-frontend 8080:80

# 浏览器访问
http://localhost:8080
```

---

### 2.3 数据路径

**写入路径**:

```text
1. Pod 发起 write() 系统调用
        ↓
2. iSCSI 驱动转发到 Longhorn Engine
        ↓
3. Engine 写入本地 Replica (主副本)
        ↓
4. Engine 通过 gRPC 同步到其他节点的 Replica
        ↓
5. 所有副本确认写入成功后，返回 Pod
```

**读取路径**:

```text
1. Pod 发起 read() 系统调用
        ↓
2. iSCSI 驱动转发到 Longhorn Engine
        ↓
3. Engine 从本地 Replica 读取数据 (优先读本地)
        ↓
4. 返回数据给 Pod
```

---

### 2.4 工作原理

#### 2.4.1 卷创建流程

```text
1. 用户创建 PVC
        ↓
2. CSI Provisioner 监听到 PVC 事件
        ↓
3. 调用 Longhorn Manager API 创建 Volume CRD
        ↓
4. Longhorn Manager 选择节点创建 Replica
        ↓
5. 在每个节点上启动 Engine 容器和 Replica 容器
        ↓
6. 返回 PV 信息给 Kubernetes
```

#### 2.4.2 副本同步机制

**同步复制 (Synchronous Replication)**:

- 写入操作必须在**所有副本**写入成功后才返回
- 保证数据强一致性
- 性能略低于异步复制

**副本状态**:

- **Healthy**: 副本正常，数据同步
- **Degraded**: 副本异常，正在重建
- **Faulted**: 副本故障，已移除

---

## 3. Longhorn 安装部署

### 3.1 环境准备

#### 3.1.1 系统要求

**Kubernetes 版本**:

- Kubernetes: v1.21+
- K3s: v1.21+
- RKE/RKE2: v1.21+

**节点要求**:

- CPU: 2 核心+
- 内存: 4 GB+
- 磁盘: 每个节点至少 10 GB 可用空间

---

#### 3.1.2 依赖检查

**安装 `open-iscsi`** (必须):

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y open-iscsi

# CentOS/RHEL
sudo yum install -y iscsi-initiator-utils

# 启动 iSCSI 服务
sudo systemctl enable iscsid --now
sudo systemctl status iscsid
```

**安装 `nfs-common`** (可选，用于备份到 NFS):

```bash
# Ubuntu/Debian
sudo apt-get install -y nfs-common

# CentOS/RHEL
sudo yum install -y nfs-utils
```

**安装 `util-linux`** (必须):

```bash
# Ubuntu/Debian
sudo apt-get install -y util-linux

# CentOS/RHEL
sudo yum install -y util-linux
```

---

#### 3.1.3 环境检查脚本

```bash
#!/bin/bash
# 下载官方检查脚本
curl -sSfL https://raw.githubusercontent.com/longhorn/longhorn/v1.6.0/scripts/environment_check.sh | bash

# 预期输出
✅ iscsi_initiator installed
✅ nfs-common installed
✅ multipathd not running
✅ Kernel supports cgroup v2
```

---

### 3.2 Helm 安装

#### 3.2.1 添加 Helm 仓库

```bash
helm repo add longhorn https://charts.longhorn.io
helm repo update
```

---

#### 3.2.2 自定义配置

**创建 `values.yaml`**:

```yaml
# values.yaml
defaultSettings:
  # 默认副本数
  defaultReplicaCount: 3
  
  # 备份目标 (S3)
  backupTarget: s3://longhorn-backup@us-east-1/
  backupTargetCredentialSecret: aws-secret
  
  # 存储最小可用空间 (%)
  storageMinimalAvailablePercentage: 10
  
  # 数据局部性 (优先使用本地副本)
  defaultDataLocality: best-effort

# 持久化存储路径
persistence:
  defaultClass: true
  defaultClassReplicaCount: 3
  
# 资源限制
longhornManager:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 1
      memory: 512Mi

longhornDriver:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 1
      memory: 512Mi

# UI 服务类型
service:
  ui:
    type: NodePort  # 或 LoadBalancer
    nodePort: 30080

# Ingress 配置
ingress:
  enabled: true
  host: longhorn.example.com
  tls: true
  tlsSecret: longhorn-tls-secret
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
```

---

#### 3.2.3 安装 Longhorn

```bash
# 创建命名空间
kubectl create namespace longhorn-system

# 安装 Longhorn
helm install longhorn longhorn/longhorn \
  --namespace longhorn-system \
  --values values.yaml \
  --version 1.6.0

# 查看安装状态
kubectl -n longhorn-system get pods -w
```

---

### 3.3 kubectl 安装

**适用场景**: 不使用 Helm 的环境

```bash
# 下载安装清单
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.6.0/deploy/longhorn.yaml

# 查看安装进度
kubectl -n longhorn-system get pods
```

---

### 3.4 Rancher 集成安装

**适用场景**: 已部署 Rancher 管理平台

**安装步骤**:

1. 登录 Rancher UI
2. 进入目标集群
3. 点击 **Apps & Marketplace**
4. 搜索 **Longhorn**
5. 点击 **Install**
6. 配置参数 (副本数、备份目标等)
7. 点击 **Install** 开始部署

---

### 3.5 验证安装

#### 3.5.1 检查 Pod 状态

```bash
kubectl -n longhorn-system get pods

# 预期输出 (所有 Pod 应为 Running)
NAME                                           READY   STATUS    RESTARTS   AGE
longhorn-manager-xxxxx                         1/1     Running   0          5m
longhorn-driver-deployer-xxxxx                 1/1     Running   0          5m
longhorn-csi-plugin-xxxxx                      2/2     Running   0          5m
csi-attacher-xxxxx                             1/1     Running   0          5m
csi-provisioner-xxxxx                          1/1     Running   0          5m
csi-resizer-xxxxx                              1/1     Running   0          5m
csi-snapshotter-xxxxx                          1/1     Running   0          5m
longhorn-ui-xxxxx                              1/1     Running   0          5m
```

---

#### 3.5.2 检查 StorageClass

```bash
kubectl get storageclass

# 预期输出
NAME                 PROVISIONER          RECLAIMPOLICY   VOLUMEBINDINGMODE
longhorn (default)   driver.longhorn.io   Delete          Immediate
```

---

#### 3.5.3 访问 Web UI

```bash
# 获取 UI 访问地址
kubectl -n longhorn-system get svc longhorn-frontend

# NodePort 方式访问
http://<NODE_IP>:30080

# 或端口转发
kubectl -n longhorn-system port-forward svc/longhorn-frontend 8080:80
# 访问 http://localhost:8080
```

---

#### 3.5.4 创建测试卷

```yaml
# test-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: test
    image: nginx:latest
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: test-pvc
```

**部署测试**:

```bash
kubectl apply -f test-pvc.yaml

# 检查 PVC 状态
kubectl get pvc test-pvc
# 应显示 Bound

# 检查 Pod 状态
kubectl get pod test-pod
# 应显示 Running

# 写入测试数据
kubectl exec -it test-pod -- sh -c "echo 'Longhorn Test' > /data/test.txt"

# 读取验证
kubectl exec -it test-pod -- cat /data/test.txt
# 输出: Longhorn Test

# 清理测试资源
kubectl delete -f test-pvc.yaml
```

---

## 4. 卷管理

### 4.1 创建 StorageClass

#### 4.1.1 基础 StorageClass

```yaml
# storageclass-basic.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-basic
provisioner: driver.longhorn.io
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: Immediate
parameters:
  numberOfReplicas: "3"
  staleReplicaTimeout: "2880"  # 48 小时
  dataLocality: "disabled"
```

---

#### 4.1.2 高性能 StorageClass

```yaml
# storageclass-fast.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-fast
provisioner: driver.longhorn.io
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: Immediate
parameters:
  numberOfReplicas: "2"         # 减少副本数提升性能
  dataLocality: "best-effort"   # 启用数据局部性
  diskSelector: "ssd"           # 仅使用 SSD 节点
  nodeSelector: "storage-node"  # 仅使用特定节点
```

---

#### 4.1.3 高可用 StorageClass

```yaml
# storageclass-ha.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-ha
provisioner: driver.longhorn.io
allowVolumeExpansion: true
reclaimPolicy: Retain  # 保留策略
volumeBindingMode: WaitForFirstConsumer
parameters:
  numberOfReplicas: "5"         # 5 个副本
  dataLocality: "disabled"
  replicaAutoBalance: "best-effort"
```

---

### 4.2 动态卷供应

**创建 PVC**:

```yaml
# pvc-app.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn-fast
  resources:
    requests:
      storage: 50Gi
```

**挂载到 StatefulSet**:

```yaml
# statefulset-mysql.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
  namespace: production
spec:
  serviceName: mysql
  replicas: 3
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
          value: "MySecretPassword"
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: longhorn-fast
      resources:
        requests:
          storage: 50Gi
```

---

### 4.3 卷克隆

**使用场景**: 快速复制生产数据到测试环境

```yaml
# pvc-clone.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data-clone
  namespace: testing
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn-fast
  dataSource:
    name: app-data            # 源 PVC 名称
    kind: PersistentVolumeClaim
    apiGroup: ""
  resources:
    requests:
      storage: 50Gi
```

---

### 4.4 卷快照

#### 4.4.1 创建 VolumeSnapshotClass

```yaml
# volumesnapshotclass.yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: longhorn-snapshot
driver: driver.longhorn.io
deletionPolicy: Delete
```

---

#### 4.4.2 创建快照

```yaml
# volumesnapshot.yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: app-data-snapshot-20251019
  namespace: production
spec:
  volumeSnapshotClassName: longhorn-snapshot
  source:
    persistentVolumeClaimName: app-data
```

**验证快照**:

```bash
kubectl get volumesnapshot -n production

# 查看快照详情
kubectl describe volumesnapshot app-data-snapshot-20251019 -n production
```

---

#### 4.4.3 从快照恢复

```yaml
# pvc-from-snapshot.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data-restored
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn-fast
  dataSource:
    name: app-data-snapshot-20251019
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  resources:
    requests:
      storage: 50Gi
```

---

### 4.5 卷扩容

**在线扩容 (无需停止 Pod)**:

```bash
# 1. 编辑 PVC
kubectl edit pvc app-data -n production

# 修改 spec.resources.requests.storage
spec:
  resources:
    requests:
      storage: 100Gi  # 从 50Gi 扩容到 100Gi

# 2. 查看扩容状态
kubectl get pvc app-data -n production -w

# 3. 验证新容量
kubectl exec -it <pod-name> -n production -- df -h /data
```

**注意事项**:

- ✅ 支持在线扩容 (无需重启 Pod)
- ❌ 不支持缩容
- ⚠️ 文件系统需支持扩容 (ext4/xfs 支持)

---

### 4.6 卷迁移

**场景**: 将卷从节点 A 迁移到节点 B

**方法 1: 通过 Longhorn UI**：

1. 登录 Longhorn UI
2. 选择目标卷
3. 点击 **Detach**
4. 修改 **Node Selector**
5. 点击 **Attach to Node**

**方法 2: 通过命令行**：

```bash
# 获取卷名称
kubectl get volume -n longhorn-system

# 编辑卷 CRD
kubectl edit volume <volume-name> -n longhorn-system

# 修改 spec.nodeID 字段
spec:
  nodeID: node-2  # 目标节点

# Pod 会自动重启并挂载到新节点
```

---

## 5. 备份与恢复

### 5.1 备份目标配置

#### 5.1.1 S3 备份目标

**创建 S3 凭证 Secret**:

```yaml
# s3-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: aws-secret
  namespace: longhorn-system
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: AKIAIOSFODNN7EXAMPLE
  AWS_SECRET_ACCESS_KEY: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  AWS_ENDPOINTS: https://s3.amazonaws.com
```

**配置备份目标**:

```bash
# 通过 UI 配置
# Settings → General → Backup Target
s3://longhorn-backup@us-east-1/
# Backup Target Credential Secret
aws-secret

# 或通过 kubectl 配置
kubectl -n longhorn-system patch settings.longhorn.io backup-target \
  -p '{"value":"s3://longhorn-backup@us-east-1/"}'

kubectl -n longhorn-system patch settings.longhorn.io backup-target-credential-secret \
  -p '{"value":"aws-secret"}'
```

---

#### 5.1.2 NFS 备份目标

**部署 NFS 服务器** (参考):

```bash
# NFS 服务器端 (Ubuntu)
sudo apt-get install -y nfs-kernel-server
sudo mkdir -p /mnt/longhorn-backup
sudo chown nobody:nogroup /mnt/longhorn-backup
sudo chmod 777 /mnt/longhorn-backup

# 配置导出
sudo tee -a /etc/exports <<EOF
/mnt/longhorn-backup *(rw,sync,no_subtree_check,no_root_squash)
EOF

sudo exportfs -ra
sudo systemctl restart nfs-kernel-server
```

**配置 Longhorn**:

```bash
# NFS 备份目标格式
nfs://192.168.1.100:/mnt/longhorn-backup

# 通过 UI 或命令行配置
kubectl -n longhorn-system patch settings.longhorn.io backup-target \
  -p '{"value":"nfs://192.168.1.100:/mnt/longhorn-backup"}'
```

---

### 5.2 手动备份

**通过 Longhorn UI**:

1. 进入 **Volume** 页面
2. 选择目标卷
3. 点击 **Create Backup**
4. 输入备份名称 (可选)
5. 点击 **OK**

**通过 kubectl**:

```yaml
# backup-manual.yaml
apiVersion: longhorn.io/v1beta2
kind: Backup
metadata:
  name: app-data-backup-20251019
  namespace: longhorn-system
spec:
  snapshotName: manual-snapshot-20251019
  labels:
    type: manual
```

```bash
kubectl apply -f backup-manual.yaml

# 查看备份状态
kubectl get backup -n longhorn-system
```

---

### 5.3 定时备份

**通过 Longhorn UI**:

1. 进入 **RecurringJob** 页面
2. 点击 **Create Recurring Job**
3. 配置:
   - **Name**: `daily-backup`
   - **Task**: `backup`
   - **Cron**: `0 2 * * *` (每天凌晨2点)
   - **Retain**: `7` (保留7个备份)
   - **Concurrency**: `2`
4. 点击 **OK**

**通过 kubectl**:

```yaml
# recurring-backup.yaml
apiVersion: longhorn.io/v1beta2
kind: RecurringJob
metadata:
  name: daily-backup
  namespace: longhorn-system
spec:
  cron: "0 2 * * *"            # 每天凌晨2点
  task: "backup"
  groups:
    - default
  retain: 7                    # 保留7个备份
  concurrency: 2
  labels:
    schedule: daily
```

```bash
kubectl apply -f recurring-backup.yaml

# 绑定到卷
kubectl -n longhorn-system patch volume app-data \
  --type='json' \
  -p='[{"op":"add","path":"/spec/recurringJobs","value":[{"name":"daily-backup","isGroup":false}]}]'
```

---

### 5.4 跨集群备份

**场景**: 将集群 A 的卷恢复到集群 B

**步骤**:

1. **集群 A**: 配置相同的备份目标 (S3/NFS)
2. **集群 A**: 创建备份
3. **集群 B**: 配置相同的备份目标
4. **集群 B**: 在 Longhorn UI 中点击 **Backup** 页面
5. **集群 B**: 点击 **Restore** 选择备份
6. **集群 B**: 创建新 PVC 挂载恢复的卷

**示例 (集群 B)**:

```yaml
# pvc-restore.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data-restored
  namespace: production
  annotations:
    longhorn.io/volume-restore: "s3://longhorn-backup@us-east-1/?backup=backup-xxxxx&volume=app-data"
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn-fast
  resources:
    requests:
      storage: 50Gi
```

---

### 5.5 灾难恢复

#### 5.5.1 完整集群恢复流程

**准备工作**:

- ✅ 备份目标可访问 (S3/NFS)
- ✅ 新集群已安装 Longhorn
- ✅ 配置相同的备份目标

**恢复步骤**:

```bash
# 1. 列出所有备份
kubectl get backupvolume -n longhorn-system

# 2. 批量恢复卷
for backup in $(kubectl get backupvolume -n longhorn-system -o jsonpath='{.items[*].metadata.name}'); do
  kubectl -n longhorn-system patch backupvolume $backup \
    --type='json' \
    -p='[{"op":"replace","path":"/spec/restoreOnceIfCreated","value":true}]'
done

# 3. 重建 PVC
kubectl get pv -o yaml | \
  sed 's/storageClassName: longhorn/storageClassName: longhorn-fast/' | \
  kubectl apply -f -

# 4. 重新部署应用
kubectl apply -f production-apps/
```

---

#### 5.5.2 RPO/RTO 指标

| 场景 | RPO | RTO | 说明 |
|-----|-----|-----|------|
| **手动备份** | 根据备份频率 | 5-10 分钟 | 取决于数据量 |
| **定时备份** | 1-24 小时 | 5-10 分钟 | 推荐每天备份 |
| **实时快照** | 近乎为 0 | 1-3 分钟 | 集群内恢复 |
| **跨集群备份** | 1-24 小时 | 10-30 分钟 | 包含网络传输时间 |

---

## 6. 高可用配置

### 6.1 副本策略

**副本数建议**:

| 集群规模 | 副本数 | 故障容忍 |
|---------|-------|---------|
| 3 节点 | 3 | 1 节点 |
| 5 节点 | 3 | 1 节点 |
| 7 节点 | 5 | 2 节点 |
| 10+ 节点 | 3 | 1 节点 |

**配置副本数**:

```yaml
# 全局默认副本数
kubectl -n longhorn-system patch settings.longhorn.io default-replica-count \
  -p '{"value":"3"}'

# 单个卷副本数
kubectl -n longhorn-system patch volume app-data \
  -p '{"spec":{"numberOfReplicas":5}}'
```

---

### 6.2 节点故障恢复

**自动恢复流程**:

```text
1. Longhorn Manager 检测到节点故障 (心跳超时)
        ↓
2. 标记节点上的副本为 Faulted
        ↓
3. 在其他健康节点上创建新副本
        ↓
4. 从主副本同步数据到新副本
        ↓
5. 新副本变为 Healthy 状态
        ↓
6. 删除 Faulted 副本
```

**配置恢复参数**:

```bash
# 副本自动平衡 (避免副本集中在少数节点)
kubectl -n longhorn-system patch settings.longhorn.io replica-auto-balance \
  -p '{"value":"best-effort"}'

# 副本重建并发数
kubectl -n longhorn-system patch settings.longhorn.io concurrent-replica-rebuild-per-node-limit \
  -p '{"value":"2"}'
```

---

### 6.3 数据局部性

**数据局部性模式**:

| 模式 | 说明 | 性能 | 适用场景 |
|-----|------|------|---------|
| **disabled** | 所有副本随机分布 | 中等 | 默认模式 |
| **best-effort** | 优先使用本地副本 | 高 | 读密集型应用 |
| **strict-local** | 强制本地副本 (实验性) | 最高 | 单节点应用 |

**配置示例**:

```yaml
# 全局配置
kubectl -n longhorn-system patch settings.longhorn.io default-data-locality \
  -p '{"value":"best-effort"}'

# 单个 StorageClass 配置
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-local
parameters:
  dataLocality: "best-effort"
```

---

### 6.4 反亲和性

**节点反亲和**: 确保副本不会分布在同一节点

```yaml
# Longhorn 默认启用节点反亲和
# 副本调度规则
spec:
  replicaAutoBalance: "best-effort"
  replicaSoftAntiAffinity: "true"   # 软反亲和 (尽力而为)
  replicaZoneSoftAntiAffinity: "true"  # 跨可用区反亲和
```

**磁盘反亲和**: 确保副本不会分布在同一磁盘

```yaml
# 节点标签
kubectl label node node1 topology.kubernetes.io/zone=zone-a
kubectl label node node2 topology.kubernetes.io/zone=zone-b
kubectl label node node3 topology.kubernetes.io/zone=zone-c
```

---

## 7. 监控与告警

### 7.1 Prometheus 集成

**安装 ServiceMonitor**:

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: longhorn-prometheus-servicemonitor
  namespace: longhorn-system
  labels:
    app: longhorn
spec:
  selector:
    matchLabels:
      app: longhorn-manager
  endpoints:
  - port: manager
    path: /metrics
```

**验证指标抓取**:

```bash
# Prometheus UI 查询
curl http://prometheus:9090/api/v1/query?query=longhorn_volume_actual_size_bytes

# 或通过 kubectl
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# 访问 http://localhost:9090/graph
```

---

### 7.2 Grafana 仪表板

**导入官方仪表板**:

1. 登录 Grafana
2. 点击 **Dashboards → Import**
3. 输入仪表板 ID: **13032** (官方 Longhorn 仪表板)
4. 选择 Prometheus 数据源
5. 点击 **Import**

**关键指标**:

- **卷状态**: Attached/Detached/Degraded
- **副本健康**: Healthy/Rebuilding/Faulted
- **磁盘使用率**: 每个节点磁盘空间
- **IOPS/带宽**: 读写性能
- **备份状态**: 成功/失败/进行中

---

### 7.3 告警规则

**创建 PrometheusRule**:

```yaml
# prometheusrule.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: longhorn-alerts
  namespace: longhorn-system
spec:
  groups:
  - name: longhorn.rules
    interval: 30s
    rules:
    # 卷降级告警
    - alert: LonghornVolumeDegraded
      expr: longhorn_volume_robustness == 2
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Longhorn volume {{ $labels.volume }} is degraded"
        description: "Volume has {{ $value }} replicas in Degraded state"
    
    # 磁盘空间不足
    - alert: LonghornDiskSpaceLow
      expr: (longhorn_node_storage_usage_bytes / longhorn_node_storage_capacity_bytes) > 0.85
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "Longhorn disk space low on node {{ $labels.node }}"
        description: "Disk usage is {{ $value | humanizePercentage }}"
    
    # 备份失败
    - alert: LonghornBackupFailed
      expr: increase(longhorn_backup_state{state="Error"}[1h]) > 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Longhorn backup failed for volume {{ $labels.volume }}"
    
    # 副本重建慢
    - alert: LonghornReplicaRebuildSlow
      expr: longhorn_replica_actual_size_bytes{state="rebuilding"} > 0
      for: 30m
      labels:
        severity: warning
      annotations:
        summary: "Replica rebuild taking too long on node {{ $labels.node }}"
```

---

### 7.4 日志收集

**查看 Longhorn Manager 日志**:

```bash
# 实时日志
kubectl logs -f deployment/longhorn-manager -n longhorn-system

# 查询特定关键词
kubectl logs deployment/longhorn-manager -n longhorn-system | grep ERROR

# 导出日志到文件
kubectl logs deployment/longhorn-manager -n longhorn-system > longhorn-manager.log
```

**集成 EFK/Loki**:

```yaml
# fluentbit-configmap.yaml (示例)
[INPUT]
    Name              tail
    Path              /var/log/containers/*longhorn*.log
    Parser            docker
    Tag               longhorn.*

[OUTPUT]
    Name              es
    Match             longhorn.*
    Host              elasticsearch.logging.svc.cluster.local
    Port              9200
    Index             longhorn
```

---

## 8. 故障排查

### 8.1 常见问题

#### 8.1.1 Pod 无法启动: `MountVolume.MountDevice failed`

**原因**:

- iSCSI 服务未启动
- 节点防火墙阻止 iSCSI 端口 (3260)

**解决方法**:

```bash
# 检查 iSCSI 服务
sudo systemctl status iscsid

# 启动 iSCSI 服务
sudo systemctl enable iscsid --now

# 检查防火墙规则 (CentOS/RHEL)
sudo firewall-cmd --add-port=3260/tcp --permanent
sudo firewall-cmd --reload

# 重启 Longhorn Engine
kubectl rollout restart deployment/longhorn-manager -n longhorn-system
```

---

#### 8.1.2 卷降级 (Degraded)

**原因**:

- 节点故障导致副本不可用
- 磁盘空间不足

**解决方法**:

```bash
# 查看卷状态
kubectl get volume -n longhorn-system app-data

# 通过 UI 查看副本状态
# Longhorn UI → Volumes → app-data → Replicas

# 手动重建副本
kubectl -n longhorn-system patch volume app-data \
  -p '{"spec":{"numberOfReplicas":3}}'

# 等待副本重建完成
kubectl get volume -n longhorn-system app-data -w
```

---

#### 8.1.3 备份失败

**原因**:

- S3 凭证错误
- 网络不通
- 备份目标空间不足

**解决方法**:

```bash
# 测试 S3 连接
kubectl -n longhorn-system create job test-s3 --image=amazon/aws-cli \
  -- s3 ls s3://longhorn-backup --region us-east-1

# 检查 Secret
kubectl get secret aws-secret -n longhorn-system -o yaml

# 验证备份目标
kubectl -n longhorn-system get settings.longhorn.io backup-target -o yaml
```

---

### 8.2 诊断命令

**检查集群状态**:

```bash
# 查看所有 Longhorn 资源
kubectl get all -n longhorn-system

# 查看卷状态
kubectl get volume -n longhorn-system

# 查看副本状态
kubectl get replica -n longhorn-system

# 查看引擎状态
kubectl get engine -n longhorn-system

# 查看节点状态
kubectl get node.longhorn.io -n longhorn-system
```

**查看事件**:

```bash
# Longhorn 事件
kubectl get events -n longhorn-system --sort-by='.lastTimestamp'

# 卷相关事件
kubectl describe volume app-data -n longhorn-system
```

---

### 8.3 日志分析

**关键错误日志**:

```bash
# Engine 日志
kubectl logs -n longhorn-system -l app=longhorn-engine

# Manager 日志 (过滤错误)
kubectl logs -n longhorn-system deployment/longhorn-manager | grep -i error

# CSI Plugin 日志
kubectl logs -n longhorn-system daemonset/longhorn-csi-plugin -c longhorn-csi-plugin
```

---

### 8.4 故障恢复流程

**标准恢复流程**:

```text
1. 识别问题
   ├─ 查看 Longhorn UI 告警
   ├─ 检查 Pod 事件 (kubectl describe pod)
   └─ 查看 Prometheus 告警

2. 收集信息
   ├─ 导出 Longhorn 日志
   ├─ 检查节点状态 (kubectl get node)
   └─ 检查磁盘空间 (df -h)

3. 诊断根因
   ├─ 节点故障 → 检查节点网络/资源
   ├─ 磁盘故障 → 更换磁盘
   ├─ 配置错误 → 修正配置
   └─ Bug → 升级 Longhorn 版本

4. 执行恢复
   ├─ 重启相关组件
   ├─ 手动重建副本
   ├─ 从备份恢复
   └─ 迁移卷到其他节点

5. 验证恢复
   ├─ 检查卷状态 (Healthy)
   ├─ 测试应用读写
   └─ 验证备份功能
```

---

## 9. 性能优化

### 9.1 存储性能调优

#### 9.1.1 使用 SSD 磁盘

```bash
# 给节点打标签
kubectl label node node1 disk-type=ssd
kubectl label node node2 disk-type=ssd
kubectl label node node3 disk-type=ssd

# 创建 SSD StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-ssd
parameters:
  diskSelector: "ssd"
  dataLocality: "best-effort"
```

---

#### 9.1.2 优化副本数

**原则**: 副本数越少,写入性能越高

| 场景 | 推荐副本数 | 理由 |
|-----|-----------|------|
| 开发环境 | 1 | 无需高可用 |
| 测试环境 | 2 | 平衡性能与可用性 |
| 生产环境 | 3 | 标准高可用 |
| 核心业务 | 5 | 极高可用要求 |

---

#### 9.1.3 启用数据局部性

```yaml
# 性能提升约 30-50%
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-fast
parameters:
  dataLocality: "best-effort"  # 优先读本地副本
```

---

### 9.2 网络性能优化

**启用 Jumbo Frames** (需交换机支持):

```bash
# 所有节点设置 MTU 9000
sudo ip link set eth0 mtu 9000

# 验证
ip link show eth0 | grep mtu
```

**优化 iSCSI 超时**:

```bash
# 减少 iSCSI 超时时间
sudo iscsiadm -m node -o update -n node.session.timeo.replacement_timeout -v 30
```

---

### 9.3 资源限制

**Longhorn Manager 资源优化**:

```yaml
# helm values.yaml
longhornManager:
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 2
      memory: 1Gi
```

**Engine 资源限制**:

```yaml
# 全局配置
kubectl -n longhorn-system patch settings.longhorn.io guaranteed-engine-manager-cpu \
  -p '{"value":"0.25"}'

kubectl -n longhorn-system patch settings.longhorn.io guaranteed-replica-manager-cpu \
  -p '{"value":"0.25"}'
```

---

### 9.4 性能测试

**使用 fio 测试**:

```yaml
# fio-test.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fio-test-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn-fast
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: fio-test
spec:
  containers:
  - name: fio
    image: dmonakhov/alpine-fio
    command: ["/bin/sh"]
    args:
      - -c
      - |
        fio --name=randwrite --ioengine=libaio --iodepth=16 \
            --rw=randwrite --bs=4k --direct=1 --size=1G \
            --numjobs=4 --runtime=60 --group_reporting \
            --filename=/data/test
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: fio-test-pvc
```

**执行测试**:

```bash
kubectl apply -f fio-test.yaml
kubectl logs -f fio-test

# 预期输出 (示例)
WRITE: bw=100MiB/s (105MB/s), iops=25.6k
```

---

## 10. 最佳实践

### 10.1 生产环境部署

**硬件要求**:

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 2 核心 | 4 核心+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | SSD 100 GB | NVMe SSD 500 GB+ |
| 网络 | 1 GbE | 10 GbE |

**节点规划**:

- ✅ 至少 3 个存储节点 (支持副本数为 3)
- ✅ 存储节点使用 SSD 或 NVMe
- ✅ 网络带宽 ≥ 10 GbE
- ✅ 磁盘预留 20% 空闲空间

---

### 10.2 容量规划

**存储容量计算**:

```text
可用容量 = (单节点磁盘容量 × 节点数) / 副本数

示例:
- 5 个节点, 每节点 1 TB SSD
- 副本数 = 3
- 可用容量 = (1 TB × 5) / 3 ≈ 1.67 TB
```

**增长预估**:

- 预留 30% 空间用于未来增长
- 每季度评估存储使用率
- 磁盘使用率超过 70% 时扩容

---

### 10.3 安全加固

**网络隔离**:

```yaml
# NetworkPolicy: 仅允许 Longhorn 组件通信
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: longhorn-allow
  namespace: longhorn-system
spec:
  podSelector:
    matchLabels:
      app: longhorn-manager
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: longhorn-system
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: longhorn-system
```

**RBAC 最小权限**:

```bash
# 创建只读用户
kubectl create serviceaccount longhorn-readonly -n longhorn-system
kubectl create clusterrolebinding longhorn-readonly \
  --clusterrole=view \
  --serviceaccount=longhorn-system:longhorn-readonly
```

---

### 10.4 升级策略

**升级前准备**:

- ✅ 阅读升级说明: https://longhorn.io/docs/latest/deploy/upgrade/
- ✅ 备份所有关键卷
- ✅ 测试环境先升级
- ✅ 选择低峰时段升级

**升级步骤**:

```bash
# 1. 备份 Longhorn CRD
kubectl get crd -o yaml | grep longhorn > longhorn-crd-backup.yaml

# 2. 升级 Helm Chart
helm repo update
helm upgrade longhorn longhorn/longhorn \
  --namespace longhorn-system \
  --version 1.7.0 \
  --reuse-values

# 3. 等待所有 Pod 就绪
kubectl -n longhorn-system rollout status daemonset/longhorn-manager

# 4. 验证卷状态
kubectl get volume -n longhorn-system
```

---

### 10.5 部署前检查清单

**基础环境**:

- [ ] Kubernetes 版本 ≥ v1.21
- [ ] 所有节点已安装 `open-iscsi`
- [ ] 所有节点已安装 `nfs-common` (可选)
- [ ] 所有节点已安装 `util-linux`

**存储规划**:

- [ ] 每个存储节点至少 10 GB 可用空间
- [ ] 存储节点已打标签 (diskSelector)
- [ ] 确定副本数 (默认 3)
- [ ] 确定备份目标 (S3/NFS)

**网络配置**:

- [ ] 节点间 iSCSI 端口 (3260) 互通
- [ ] 备份目标网络可达
- [ ] (可选) 启用 Jumbo Frames

**监控告警**:

- [ ] Prometheus 已安装
- [ ] Grafana 已安装
- [ ] 导入 Longhorn 仪表板
- [ ] 配置告警规则

**安全加固**:

- [ ] 配置 NetworkPolicy
- [ ] 配置 RBAC 权限
- [ ] 启用 TLS (Ingress)

---

## 总结

**Longhorn 适用场景**:

- ✅ 中小型 Kubernetes 集群
- ✅ 边缘计算 (K3s)
- ✅ 无共享存储的环境
- ✅ 需要简单易用的存储方案

**核心优势**:

- 简单易部署 (一键安装)
- Web UI 友好
- 内置备份恢复
- 良好的社区支持

**注意事项**:

- 仅支持块存储 (RWO)
- 性能略低于 Ceph/Portworx
- 不适合超大规模集群 (>100 节点)

---

**相关文档**:

- [CSI存储概述](01_CSI存储概述.md)
- [Rook-Ceph存储](02_Rook_Ceph存储.md)
- [StorageClass最佳实践](04_StorageClass最佳实践.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**Longhorn 版本**: v1.6.0
