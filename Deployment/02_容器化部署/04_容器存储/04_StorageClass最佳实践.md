# StorageClass 最佳实践

> **返回**: [容器存储首页](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [StorageClass 最佳实践](#storageclass-最佳实践)
  - [📋 目录](#-目录)
  - [1. StorageClass 概述](#1-storageclass-概述)
    - [1.1 什么是 StorageClass](#11-什么是-storageclass)
    - [1.2 核心概念](#12-核心概念)
    - [1.3 工作原理](#13-工作原理)
    - [1.4 使用场景](#14-使用场景)
  - [2. StorageClass 配置](#2-storageclass-配置)
    - [2.1 基础配置](#21-基础配置)
    - [2.2 参数详解](#22-参数详解)
      - [2.2.1 核心参数](#221-核心参数)
      - [2.2.2 Provisioner Parameters (Longhorn)](#222-provisioner-parameters-longhorn)
      - [2.2.3 Provisioner Parameters (Rook-Ceph RBD)](#223-provisioner-parameters-rook-ceph-rbd)
    - [2.3 常用 Provisioner](#23-常用-provisioner)
    - [2.4 绑定模式](#24-绑定模式)
      - [2.4.1 Immediate (立即绑定)](#241-immediate-立即绑定)
      - [2.4.2 WaitForFirstConsumer (延迟绑定)](#242-waitforfirstconsumer-延迟绑定)
  - [3. 动态供应 (Dynamic Provisioning)](#3-动态供应-dynamic-provisioning)
    - [3.1 动态供应原理](#31-动态供应原理)
    - [3.2 配置示例](#32-配置示例)
    - [3.3 PVC 请求规范](#33-pvc-请求规范)
    - [3.4 常见问题](#34-常见问题)
      - [3.4.1 PVC 一直 Pending](#341-pvc-一直-pending)
      - [3.4.2 默认 StorageClass 未生效](#342-默认-storageclass-未生效)
  - [4. 卷快照 (VolumeSnapshot)](#4-卷快照-volumesnapshot)
    - [4.1 快照功能概述](#41-快照功能概述)
    - [4.2 VolumeSnapshotClass](#42-volumesnapshotclass)
    - [4.3 创建快照](#43-创建快照)
    - [4.4 从快照恢复](#44-从快照恢复)
    - [4.5 快照策略](#45-快照策略)
  - [5. 卷克隆 (Volume Cloning)](#5-卷克隆-volume-cloning)
    - [5.1 克隆原理](#51-克隆原理)
    - [5.2 克隆操作](#52-克隆操作)
    - [5.3 应用场景](#53-应用场景)
    - [5.4 克隆 vs 快照](#54-克隆-vs-快照)
  - [6. 卷扩容 (Volume Expansion)](#6-卷扩容-volume-expansion)
    - [6.1 扩容原理](#61-扩容原理)
    - [6.2 在线扩容](#62-在线扩容)
    - [6.3 离线扩容](#63-离线扩容)
    - [6.4 扩容限制](#64-扩容限制)
  - [7. 回收策略 (Reclaim Policy)](#7-回收策略-reclaim-policy)
    - [7.1 策略类型](#71-策略类型)
    - [7.2 选择建议](#72-选择建议)
    - [7.3 手动回收](#73-手动回收)
    - [7.4 策略变更](#74-策略变更)
  - [8. 访问模式 (Access Modes)](#8-访问模式-access-modes)
    - [8.1 访问模式类型](#81-访问模式类型)
    - [8.2 存储方案支持度](#82-存储方案支持度)
    - [8.3 应用选择](#83-应用选择)
    - [8.4 跨节点访问](#84-跨节点访问)
  - [9. 性能优化](#9-性能优化)
    - [9.1 存储类型选择](#91-存储类型选择)
    - [9.2 IOPS 优化](#92-iops-优化)
    - [9.3 吞吐量优化](#93-吞吐量优化)
    - [9.4 性能测试](#94-性能测试)
  - [10. 多租户隔离](#10-多租户隔离)
    - [10.1 命名空间隔离](#101-命名空间隔离)
    - [10.2 ResourceQuota](#102-resourcequota)
    - [10.3 LimitRange](#103-limitrange)
    - [10.4 RBAC 权限控制](#104-rbac-权限控制)
  - [11. 监控与审计](#11-监控与审计)
    - [11.1 存储指标](#111-存储指标)
    - [11.2 Prometheus 监控](#112-prometheus-监控)
    - [11.3 Grafana 仪表板](#113-grafana-仪表板)
    - [11.4 审计日志](#114-审计日志)
  - [12. 故障排查](#12-故障排查)
    - [12.1 常见问题](#121-常见问题)
      - [12.1.1 PVC 一直 Pending](#1211-pvc-一直-pending)
      - [12.1.2 Pod 无法挂载 PVC](#1212-pod-无法挂载-pvc)
    - [12.2 诊断命令](#122-诊断命令)
    - [12.3 日志分析](#123-日志分析)
    - [12.4 恢复流程](#124-恢复流程)
  - [13. 最佳实践](#13-最佳实践)
    - [13.1 StorageClass 设计原则](#131-storageclass-设计原则)
    - [13.2 命名规范](#132-命名规范)
    - [13.3 标签管理](#133-标签管理)
    - [13.4 安全加固](#134-安全加固)
    - [13.5 部署检查清单](#135-部署检查清单)
  - [总结](#总结)

---

## 1. StorageClass 概述

### 1.1 什么是 StorageClass

**StorageClass** 是 Kubernetes 中用于定义**存储类别**的 API 对象，它描述了如何动态创建 PersistentVolume (PV)。

**核心功能**:

- **动态供应**: 自动创建 PV，无需手动预创建
- **存储抽象**: 屏蔽底层存储差异，提供统一接口
- **参数化配置**: 通过参数定义存储特性 (性能、副本、加密等)
- **多租户支持**: 不同租户使用不同存储类

**工作流程**:

```text
1. 管理员创建 StorageClass
        ↓
2. 用户创建 PVC，指定 storageClassName
        ↓
3. CSI Provisioner 监听到 PVC 事件
        ↓
4. Provisioner 调用 CSI Driver API 创建卷
        ↓
5. 创建 PV 并绑定到 PVC
        ↓
6. Pod 挂载 PVC
```

---

### 1.2 核心概念

| 概念 | 说明 |
|-----|------|
| **Provisioner** | 存储后端驱动 (如 `driver.longhorn.io`, `rook-ceph.rbd.csi.ceph.com`) |
| **Parameters** | 传递给 Provisioner 的参数 (如副本数、IOPS) |
| **ReclaimPolicy** | PVC 删除后 PV 的处理方式 (Delete/Retain) |
| **VolumeBindingMode** | PV 绑定时机 (Immediate/WaitForFirstConsumer) |
| **AllowVolumeExpansion** | 是否允许卷扩容 |
| **MountOptions** | 挂载选项 (如 NFS 的 `vers=4.1`) |

---

### 1.3 工作原理

**架构示意**:

```text
┌──────────────────────────────────────────────────────────────┐
│                    Kubernetes 集群                           │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────┐    ┌────────────┐    ┌────────────┐          │
│  │    Pod     │───▶│    PVC     │───▶│     PV     │         │
│  └────────────┘    └──────┬─────┘    └──────┬─────┘          │
│                            │                  │               │
│                            │                  │               │
│                     ┌──────▼──────────────────▼─────┐        │
│                     │     StorageClass             │        │
│                     │  ┌────────────────────────┐  │        │
│                     │  │  Provisioner           │  │        │
│                     │  │  Parameters            │  │        │
│                     │  │  ReclaimPolicy         │  │        │
│                     │  └────────────────────────┘  │        │
│                     └──────────┬────────────────────┘        │
│                                │                              │
│                                ▼                              │
│                     ┌────────────────────┐                   │
│                     │   CSI Driver       │                   │
│                     └─────────┬──────────┘                   │
└───────────────────────────────┼──────────────────────────────┘
                                │
                                ▼
                    ┌────────────────────┐
                    │  存储后端 (Ceph/   │
                    │  Longhorn/NFS/等)  │
                    └────────────────────┘
```

---

### 1.4 使用场景

| 场景 | StorageClass 配置 |
|-----|------------------|
| **数据库 (MySQL/PostgreSQL)** | 高 IOPS, 3 副本, RWO |
| **文件共享 (NFS)** | 中等性能, RWX, 允许扩容 |
| **日志存储 (Elasticsearch)** | 大容量, 低成本, 2 副本 |
| **CI/CD 缓存** | 高性能, 1 副本, Delete 策略 |
| **备份归档** | 低成本, 冷存储, Retain 策略 |

---

## 2. StorageClass 配置

### 2.1 基础配置

**最小化配置**:

```yaml
# storageclass-basic.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: Immediate
```

**完整配置示例**:

```yaml
# storageclass-full.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"  # 设为默认
  labels:
    storage-type: ssd
    performance: high
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "3"
  dataLocality: "best-effort"
  diskSelector: "ssd"
  fsType: "ext4"
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
mountOptions:
  - discard
  - noatime
```

---

### 2.2 参数详解

#### 2.2.1 核心参数

| 参数 | 必填 | 说明 | 示例值 |
|-----|------|------|--------|
| `provisioner` | ✅ | CSI Driver 名称 | `driver.longhorn.io` |
| `parameters` | ❌ | 传递给 Provisioner 的参数 | 见下表 |
| `reclaimPolicy` | ❌ | 回收策略 | `Delete` / `Retain` |
| `volumeBindingMode` | ❌ | 绑定模式 | `Immediate` / `WaitForFirstConsumer` |
| `allowVolumeExpansion` | ❌ | 是否允许扩容 | `true` / `false` |
| `mountOptions` | ❌ | 挂载选项 | `["noatime", "discard"]` |

---

#### 2.2.2 Provisioner Parameters (Longhorn)

| 参数 | 说明 | 默认值 |
|-----|------|--------|
| `numberOfReplicas` | 副本数 | `3` |
| `dataLocality` | 数据局部性 | `disabled` |
| `diskSelector` | 磁盘选择器 | `` (所有磁盘) |
| `nodeSelector` | 节点选择器 | `` (所有节点) |
| `fsType` | 文件系统类型 | `ext4` |
| `staleReplicaTimeout` | 过期副本超时 (分钟) | `2880` (48小时) |
| `recurringJobSelector` | 定时任务选择器 | `[]` |

---

#### 2.2.3 Provisioner Parameters (Rook-Ceph RBD)

| 参数 | 说明 | 示例值 |
|-----|------|--------|
| `clusterID` | Ceph 集群 ID | `rook-ceph` |
| `pool` | Ceph 存储池 | `replicapool` |
| `imageFormat` | 镜像格式 | `2` |
| `imageFeatures` | 镜像特性 | `layering` |
| `csi.storage.k8s.io/provisioner-secret-name` | CSI Secret 名称 | `rook-csi-rbd-provisioner` |
| `csi.storage.k8s.io/node-stage-secret-name` | Node Secret 名称 | `rook-csi-rbd-node` |

---

### 2.3 常用 Provisioner

| Provisioner | 说明 | 适用场景 |
|------------|------|---------|
| `driver.longhorn.io` | Longhorn 分布式块存储 | 中小型集群 |
| `rook-ceph.rbd.csi.ceph.com` | Rook-Ceph RBD | 大型生产环境 |
| `rook-ceph.cephfs.csi.ceph.com` | Rook-Ceph CephFS | 共享文件存储 |
| `nfs.csi.k8s.io` | NFS CSI Driver | 遗留 NFS 存储 |
| `ebs.csi.aws.com` | AWS EBS | AWS 云环境 |
| `disk.csi.azure.com` | Azure Disk | Azure 云环境 |
| `pd.csi.storage.gke.io` | Google Persistent Disk | GCP 云环境 |

---

### 2.4 绑定模式

#### 2.4.1 Immediate (立即绑定)

**特点**:

- PVC 创建后立即绑定 PV
- 不考虑 Pod 调度位置
- 可能导致 Pod 无法调度 (PV 所在节点无可用资源)

**适用场景**:

- 网络存储 (SAN/NFS/Ceph)
- 多节点可访问的存储

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ceph-rbd
volumeBindingMode: Immediate  # 立即绑定
```

---

#### 2.4.2 WaitForFirstConsumer (延迟绑定)

**特点**:

- 等待 Pod 创建时才绑定 PV
- 确保 PV 创建在 Pod 所在节点
- 避免跨节点数据传输

**适用场景**:

- 本地存储 (Local PV)
- 云厂商存储 (EBS/Azure Disk)
- Longhorn (数据局部性优化)

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-local
volumeBindingMode: WaitForFirstConsumer  # 延迟绑定
```

---

## 3. 动态供应 (Dynamic Provisioning)

### 3.1 动态供应原理

**传统静态供应 vs 动态供应**:

| 对比项 | 静态供应 | 动态供应 |
|-------|---------|---------|
| **PV 创建** | 管理员手动创建 | 自动创建 |
| **灵活性** | 低 (需预创建) | 高 (按需创建) |
| **资源利用率** | 低 (可能浪费) | 高 (精确匹配) |
| **维护成本** | 高 | 低 |
| **适用场景** | 小规模、遗留系统 | 大规模、云原生 |

---

### 3.2 配置示例

**创建 StorageClass**:

```yaml
# storageclass-dynamic.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-storage
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "3"
  dataLocality: "best-effort"
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
```

**创建 PVC**:

```yaml
# pvc-dynamic.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-storage  # 指定 StorageClass
  resources:
    requests:
      storage: 10Gi
```

**验证**:

```bash
# 创建 PVC
kubectl apply -f pvc-dynamic.yaml

# 查看 PVC (应为 Pending，等待 Pod 调度)
kubectl get pvc app-data
# NAME       STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS
# app-data   Pending                                      fast-storage

# 创建 Pod 挂载 PVC
kubectl apply -f pod-with-pvc.yaml

# 再次查看 PVC (应为 Bound)
kubectl get pvc app-data
# NAME       STATUS   VOLUME                                     CAPACITY
# app-data   Bound    pvc-12345678-1234-1234-1234-123456789012   10Gi
```

---

### 3.3 PVC 请求规范

**标准 PVC 配置**:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-data
  namespace: production
  labels:
    app: mysql
    env: production
  annotations:
    volume.beta.kubernetes.io/storage-class: "fast-storage"  # 旧版写法
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-storage  # 推荐写法
  resources:
    requests:
      storage: 100Gi
  selector:  # 可选: 选择特定标签的 PV
    matchLabels:
      tier: gold
```

**访问模式选择**:

```yaml
# 数据库 (单节点读写)
accessModes:
  - ReadWriteOnce

# 文件共享 (多节点读写)
accessModes:
  - ReadWriteMany

# 静态内容 (多节点只读)
accessModes:
  - ReadOnlyMany
```

---

### 3.4 常见问题

#### 3.4.1 PVC 一直 Pending

**排查步骤**:

```bash
# 1. 查看 PVC 事件
kubectl describe pvc app-data

# 常见错误:
# - StorageClass 不存在
# - CSI Driver 未安装
# - 节点存储空间不足
# - Provisioner Pod 未就绪

# 2. 检查 StorageClass
kubectl get storageclass

# 3. 检查 CSI Driver Pods
kubectl get pods -n kube-system | grep csi

# 4. 检查 Provisioner 日志
kubectl logs -n kube-system <csi-provisioner-pod>
```

---

#### 3.4.2 默认 StorageClass 未生效

**解决方法**:

```bash
# 1. 取消所有 StorageClass 的默认标记
kubectl patch storageclass <old-default> \
  -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'

# 2. 设置新的默认 StorageClass
kubectl patch storageclass fast-storage \
  -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# 3. 验证
kubectl get storageclass
# NAME                    PROVISIONER            ...
# fast-storage (default)  driver.longhorn.io     ...
```

---

## 4. 卷快照 (VolumeSnapshot)

### 4.1 快照功能概述

**VolumeSnapshot** 是 Kubernetes 提供的卷快照功能，允许在不停止应用的情况下创建数据副本。

**核心优势**:

- ✅ **时间点恢复**: 恢复到特定时间点
- ✅ **快速克隆**: 基于快照快速创建新卷
- ✅ **备份策略**: 定时快照作为备份
- ✅ **测试环境**: 复制生产数据到测试环境

---

### 4.2 VolumeSnapshotClass

**创建 VolumeSnapshotClass**:

```yaml
# volumesnapshotclass-longhorn.yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: longhorn-snapshot
driver: driver.longhorn.io
deletionPolicy: Delete  # 或 Retain
parameters:
  type: snap  # Provisioner 特定参数
```

**Rook-Ceph 示例**:

```yaml
# volumesnapshotclass-ceph.yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: ceph-rbd-snapshot
driver: rook-ceph.rbd.csi.ceph.com
deletionPolicy: Delete
parameters:
  clusterID: rook-ceph
  csi.storage.k8s.io/snapshotter-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/snapshotter-secret-namespace: rook-ceph
```

---

### 4.3 创建快照

**手动创建快照**:

```yaml
# volumesnapshot.yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: mysql-snapshot-20251019
  namespace: production
spec:
  volumeSnapshotClassName: longhorn-snapshot
  source:
    persistentVolumeClaimName: mysql-data
```

**验证快照**:

```bash
# 创建快照
kubectl apply -f volumesnapshot.yaml

# 查看快照状态
kubectl get volumesnapshot -n production
# NAME                       READYTOUSE   SOURCEPVC    RESTORESIZE   ...
# mysql-snapshot-20251019    true         mysql-data   100Gi         ...

# 查看快照详情
kubectl describe volumesnapshot mysql-snapshot-20251019 -n production
```

---

### 4.4 从快照恢复

**恢复到新 PVC**:

```yaml
# pvc-from-snapshot.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-data-restored
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-storage
  dataSource:
    name: mysql-snapshot-20251019
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  resources:
    requests:
      storage: 100Gi  # 必须 ≥ 快照大小
```

**验证恢复**:

```bash
kubectl apply -f pvc-from-snapshot.yaml
kubectl get pvc mysql-data-restored -n production

# 挂载到测试 Pod 验证数据
kubectl apply -f test-pod-with-restored-pvc.yaml
kubectl exec -it test-pod -n production -- ls -lh /data
```

---

### 4.5 快照策略

**定时快照 (CronJob)**:

```yaml
# snapshot-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mysql-daily-snapshot
  namespace: production
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: snapshot-creator
          containers:
          - name: snapshot
            image: bitnami/kubectl:latest
            command:
            - /bin/sh
            - -c
            - |
              SNAPSHOT_NAME="mysql-snapshot-$(date +%Y%m%d-%H%M%S)"
              cat <<EOF | kubectl apply -f -
              apiVersion: snapshot.storage.k8s.io/v1
              kind: VolumeSnapshot
              metadata:
                name: $SNAPSHOT_NAME
                namespace: production
              spec:
                volumeSnapshotClassName: longhorn-snapshot
                source:
                  persistentVolumeClaimName: mysql-data
              EOF
          restartPolicy: OnFailure
```

**RBAC 权限**:

```yaml
# snapshot-rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: snapshot-creator
  namespace: production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: snapshot-creator
  namespace: production
rules:
- apiGroups: ["snapshot.storage.k8s.io"]
  resources: ["volumesnapshots"]
  verbs: ["create", "get", "list", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: snapshot-creator
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: snapshot-creator
subjects:
- kind: ServiceAccount
  name: snapshot-creator
  namespace: production
```

---

## 5. 卷克隆 (Volume Cloning)

### 5.1 克隆原理

**卷克隆 vs 快照恢复**:

| 对比项 | 卷克隆 | 快照恢复 |
|-------|-------|---------|
| **速度** | 快 (COW) | 中等 |
| **资源占用** | 低 (初始) | 高 (完整复制) |
| **独立性** | 依赖源卷 (部分实现) | 完全独立 |
| **适用场景** | 快速测试、临时环境 | 生产恢复、长期保存 |

---

### 5.2 克隆操作

**克隆 PVC**:

```yaml
# pvc-clone.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-data-clone
  namespace: testing
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-storage
  dataSource:
    name: mysql-data            # 源 PVC 名称
    kind: PersistentVolumeClaim  # 注意: 不是 VolumeSnapshot
    apiGroup: ""
  resources:
    requests:
      storage: 100Gi
```

**验证克隆**:

```bash
kubectl apply -f pvc-clone.yaml
kubectl get pvc mysql-data-clone -n testing

# 挂载到 Pod
kubectl apply -f test-pod-with-clone.yaml

# 验证数据
kubectl exec -it test-pod -n testing -- mysql -u root -p -e "SHOW DATABASES;"
```

---

### 5.3 应用场景

**场景 1: 数据库测试**:

```yaml
# 克隆生产数据库到测试环境
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-test-data
  namespace: testing
spec:
  dataSource:
    name: mysql-prod-data
    kind: PersistentVolumeClaim
  # ... 其他配置
```

**场景 2: A/B 测试**:

```yaml
# 克隆应用数据到 A/B 测试环境
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data-variant-b
  namespace: ab-test
spec:
  dataSource:
    name: app-data-variant-a
    kind: PersistentVolumeClaim
  # ... 其他配置
```

---

### 5.4 克隆 vs 快照

**何时使用克隆**:

- ✅ 快速复制到测试环境
- ✅ 临时数据分析
- ✅ 数据集开发

**何时使用快照**:

- ✅ 长期备份保留
- ✅ 灾难恢复
- ✅ 合规审计

---

## 6. 卷扩容 (Volume Expansion)

### 6.1 扩容原理

**CSI 扩容流程**:

```text
1. 用户修改 PVC.spec.resources.requests.storage
        ↓
2. PVC Controller 检测到变更
        ↓
3. 调用 CSI Driver ControllerExpandVolume()
        ↓
4. 存储后端扩容卷
        ↓
5. Kubelet 调用 CSI Driver NodeExpandVolume()
        ↓
6. 扩展文件系统 (ext4/xfs)
        ↓
7. PVC 状态更新为新容量
```

---

### 6.2 在线扩容

**支持在线扩容的 StorageClass**:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expandable-storage
provisioner: driver.longhorn.io
allowVolumeExpansion: true  # 启用扩容
```

**扩容操作**:

```bash
# 1. 编辑 PVC
kubectl edit pvc mysql-data -n production

# 修改 spec.resources.requests.storage
spec:
  resources:
    requests:
      storage: 200Gi  # 从 100Gi 扩容到 200Gi

# 2. 等待扩容完成
kubectl get pvc mysql-data -n production -w

# 3. 验证新容量
kubectl exec -it mysql-pod -n production -- df -h /var/lib/mysql
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/longhorn/pvc-xxx  197G   50G  147G  26% /var/lib/mysql
```

**注意事项**:

- ✅ 支持在线扩容 (无需重启 Pod)
- ❌ 不支持缩容
- ⚠️ 文件系统必须支持扩容 (ext4/xfs 支持，ext3 不支持)

---

### 6.3 离线扩容

**不支持在线扩容时的步骤**:

```bash
# 1. 删除 Pod (保留 PVC)
kubectl delete pod mysql-pod -n production

# 2. 扩容 PVC
kubectl patch pvc mysql-data -n production \
  -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'

# 3. 等待扩容完成
kubectl get pvc mysql-data -n production

# 4. 重建 Pod
kubectl apply -f mysql-pod.yaml
```

---

### 6.4 扩容限制

| 存储类型 | 在线扩容 | 离线扩容 | 缩容 |
|---------|---------|---------|------|
| **Longhorn** | ✅ | ✅ | ❌ |
| **Rook-Ceph RBD** | ✅ | ✅ | ❌ |
| **AWS EBS** | ✅ | ✅ | ❌ |
| **Azure Disk** | ✅ | ✅ | ❌ |
| **GCE PD** | ✅ | ✅ | ❌ |
| **NFS** | ⚠️ (取决于后端) | ✅ | ❌ |

---

## 7. 回收策略 (Reclaim Policy)

### 7.1 策略类型

| 策略 | 说明 | PVC 删除后 PV 状态 | 数据保留 |
|-----|------|------------------|---------|
| **Delete** | 自动删除 PV 和底层存储 | PV 被删除 | ❌ 数据丢失 |
| **Retain** | 保留 PV 和数据 | PV 变为 Released | ✅ 数据保留 |
| **Recycle** | 清空数据后重用 (已废弃) | PV 变为 Available | ❌ 数据清空 |

---

### 7.2 选择建议

**Delete 策略** (默认):

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: temp-storage
reclaimPolicy: Delete
# 适用场景:
# - 开发测试环境
# - 临时缓存数据
# - CI/CD 临时卷
```

**Retain 策略**:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: prod-storage
reclaimPolicy: Retain
# 适用场景:
# - 生产数据库
# - 关键业务数据
# - 需要手动审计后删除
```

---

### 7.3 手动回收

**Retain 策略下的回收流程**:

```bash
# 1. 删除 PVC (PV 变为 Released)
kubectl delete pvc mysql-data -n production

# 2. 查看 PV 状态
kubectl get pv
# NAME                                       CAPACITY   STATUS      CLAIM
# pvc-12345678-1234-1234-1234-123456789012   100Gi      Released    production/mysql-data

# 3. 备份数据 (可选)
kubectl exec -it backup-pod -- \
  rsync -av /mnt/pv-xxx/ /backup/mysql-20251019/

# 4. 删除 PV
kubectl delete pv pvc-12345678-1234-1234-1234-123456789012

# 5. 底层存储手动清理 (取决于存储类型)
# Longhorn: 通过 UI 删除卷
# Ceph: ceph rbd rm pool/image-xxx
```

---

### 7.4 策略变更

**修改现有 PV 的回收策略**:

```bash
# 查看当前策略
kubectl get pv pvc-xxx -o yaml | grep persistentVolumeReclaimPolicy

# 修改为 Retain (保护数据)
kubectl patch pv pvc-xxx \
  -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'

# 验证
kubectl get pv pvc-xxx -o jsonpath='{.spec.persistentVolumeReclaimPolicy}'
```

---

## 8. 访问模式 (Access Modes)

### 8.1 访问模式类型

| 访问模式 | 缩写 | 说明 | 典型应用 |
|---------|------|------|---------|
| **ReadWriteOnce** | RWO | 单节点读写 | MySQL, PostgreSQL, MongoDB |
| **ReadOnlyMany** | ROX | 多节点只读 | 静态资源 (图片/视频) |
| **ReadWriteMany** | RWX | 多节点读写 | NFS, CephFS, 文件共享 |
| **ReadWriteOncePod** | RWOP | 单 Pod 读写 (K8s 1.22+) | 严格单实例应用 |

---

### 8.2 存储方案支持度

| 存储方案 | RWO | ROX | RWX | RWOP |
|---------|-----|-----|-----|------|
| **Longhorn** | ✅ | ✅ | ❌ | ✅ |
| **Rook-Ceph RBD** | ✅ | ✅ | ❌ | ✅ |
| **Rook-Ceph CephFS** | ✅ | ✅ | ✅ | ✅ |
| **NFS CSI** | ✅ | ✅ | ✅ | ✅ |
| **AWS EBS** | ✅ | ❌ | ❌ | ✅ |
| **Azure Disk** | ✅ | ❌ | ❌ | ✅ |
| **Google PD** | ✅ | ❌ | ❌ | ✅ |
| **Local PV** | ✅ | ❌ | ❌ | ✅ |

---

### 8.3 应用选择

**数据库 (RWO)**:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-data
spec:
  accessModes:
    - ReadWriteOnce  # 单节点读写
  storageClassName: fast-storage
  resources:
    requests:
      storage: 100Gi
```

**文件共享 (RWX)**:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shared-files
spec:
  accessModes:
    - ReadWriteMany  # 多节点读写
  storageClassName: cephfs-storage
  resources:
    requests:
      storage: 500Gi
```

---

### 8.4 跨节点访问

**RWO 卷跨节点迁移**:

```bash
# 场景: Pod 从 node1 调度到 node2

# 1. Kubelet 在 node1 上卸载卷
# 2. CSI Driver 在存储后端 Detach 卷
# 3. CSI Driver 在存储后端 Attach 卷到 node2
# 4. Kubelet 在 node2 上挂载卷
# 5. Pod 在 node2 上启动

# 迁移时间: 30 秒 - 2 分钟 (取决于存储类型)
```

---

## 9. 性能优化

### 9.1 存储类型选择

| 存储类型 | IOPS | 吞吐量 | 延迟 | 成本 | 适用场景 |
|---------|------|--------|------|------|---------|
| **NVMe SSD** | 100k+ | 3000+ MB/s | <1ms | 高 | 数据库、高并发 |
| **SATA SSD** | 10k-50k | 500 MB/s | 1-5ms | 中 | Web应用、缓存 |
| **HDD** | 100-200 | 100 MB/s | 10-20ms | 低 | 归档、备份 |

**配置示例**:

```yaml
# 高性能 SSD StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nvme-storage
provisioner: driver.longhorn.io
parameters:
  diskSelector: "nvme"
  numberOfReplicas: "2"  # 减少副本数提升性能
  dataLocality: "best-effort"
```

---

### 9.2 IOPS 优化

**文件系统选择**:

| 文件系统 | IOPS | 特点 |
|---------|------|------|
| **ext4** | 中等 | 稳定、成熟 |
| **xfs** | 高 | 大文件性能好 |
| **btrfs** | 中等 | 支持快照 (实验性) |

**挂载选项优化**:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: high-iops
mountOptions:
  - noatime      # 禁用访问时间更新
  - nodiratime   # 禁用目录访问时间更新
  - discard      # 启用 TRIM (SSD)
  - nobarrier    # 禁用写屏障 (提升性能，降低安全性)
```

---

### 9.3 吞吐量优化

**块大小调优**:

```yaml
# 大文件场景 (视频/备份)
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    volumeMounts:
    - name: data
      mountPath: /data
      mountPropagation: HostToContainer
    # 在应用层设置大块 I/O
    command: ["dd", "if=/dev/zero", "of=/data/test", "bs=1M", "count=1000"]
```

---

### 9.4 性能测试

**fio 基准测试**:

```yaml
# fio-benchmark.yaml
apiVersion: v1
kind: Pod
metadata:
  name: fio-benchmark
spec:
  containers:
  - name: fio
    image: dmonakhov/alpine-fio
    command: ["/bin/sh", "-c"]
    args:
      - |
        echo "=== 随机写 IOPS 测试 ==="
        fio --name=randwrite --ioengine=libaio --iodepth=16 \
            --rw=randwrite --bs=4k --direct=1 --size=1G \
            --numjobs=4 --runtime=60 --group_reporting \
            --filename=/data/test

        echo "=== 顺序读吞吐量测试 ==="
        fio --name=seqread --ioengine=libaio --iodepth=16 \
            --rw=read --bs=1M --direct=1 --size=1G \
            --numjobs=1 --runtime=60 --group_reporting \
            --filename=/data/test
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: test-pvc
```

**预期性能指标** (参考):

| 存储方案 | 随机写 IOPS | 顺序读带宽 |
|---------|-----------|-----------|
| **Longhorn (NVMe)** | 20k-50k | 1000-2000 MB/s |
| **Rook-Ceph (NVMe)** | 50k-100k | 2000-3000 MB/s |
| **AWS EBS gp3** | 16k | 1000 MB/s |
| **Azure Premium SSD** | 20k | 900 MB/s |

---

## 10. 多租户隔离

### 10.1 命名空间隔离

**租户命名空间设计**:

```bash
# 创建租户命名空间
kubectl create namespace tenant-a
kubectl create namespace tenant-b

# 为每个租户创建专用 StorageClass
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: tenant-a-storage
  labels:
    tenant: tenant-a
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "3"
  nodeSelector: "tenant=tenant-a"  # 租户专用节点
EOF
```

---

### 10.2 ResourceQuota

**限制租户存储配额**:

```yaml
# resourcequota-tenant-a.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: storage-quota
  namespace: tenant-a
spec:
  hard:
    requests.storage: "1Ti"                    # 总存储限制
    persistentvolumeclaims: "50"              # PVC 数量限制
    tenant-a-storage.storageclass.storage.k8s.io/requests.storage: "1Ti"  # 特定 StorageClass 限制
```

**验证配额**:

```bash
kubectl apply -f resourcequota-tenant-a.yaml

# 查看配额使用情况
kubectl get resourcequota -n tenant-a
# NAME            REQUESTS.STORAGE   PERSISTENTVOLUMECLAIMS
# storage-quota   500Gi/1Ti          25/50
```

---

### 10.3 LimitRange

**限制单个 PVC 大小**:

```yaml
# limitrange-tenant-a.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: pvc-limit
  namespace: tenant-a
spec:
  limits:
  - type: PersistentVolumeClaim
    max:
      storage: 500Gi  # 单个 PVC 最大 500 GB
    min:
      storage: 1Gi    # 单个 PVC 最小 1 GB
```

---

### 10.4 RBAC 权限控制

**只允许租户访问自己的 StorageClass**:

```yaml
# rbac-tenant-a.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: storageclass-user
  namespace: tenant-a
rules:
- apiGroups: [""]
  resources: ["persistentvolumeclaims"]
  verbs: ["create", "get", "list", "delete"]
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses"]
  verbs: ["get", "list"]
  resourceNames: ["tenant-a-storage"]  # 仅允许使用特定 StorageClass
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: storageclass-user
  namespace: tenant-a
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: storageclass-user
subjects:
- kind: ServiceAccount
  name: tenant-a-sa
  namespace: tenant-a
```

---

## 11. 监控与审计

### 11.1 存储指标

**关键监控指标**:

| 指标类型 | 指标名称 | 说明 |
|---------|---------|------|
| **容量** | `kubelet_volume_stats_capacity_bytes` | PVC 总容量 |
| **使用量** | `kubelet_volume_stats_used_bytes` | PVC 已用容量 |
| **可用量** | `kubelet_volume_stats_available_bytes` | PVC 可用容量 |
| **Inodes** | `kubelet_volume_stats_inodes` | 总 inode 数 |
| **Inodes 使用** | `kubelet_volume_stats_inodes_used` | 已用 inode 数 |

---

### 11.2 Prometheus 监控

**抓取 Kubelet 指标**:

```yaml
# servicemonitor-kubelet.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kubelet
  namespace: kube-system
spec:
  endpoints:
  - port: https-metrics
    scheme: https
    tlsConfig:
      caFile: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      insecureSkipVerify: true
    bearerTokenFile: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabelings:
    - action: labelmap
      regex: __meta_kubernetes_node_label_(.+)
  selector:
    matchLabels:
      k8s-app: kubelet
```

---

### 11.3 Grafana 仪表板

**导入官方仪表板**:

- **Kubernetes / Persistent Volumes**: Grafana ID `13646`
- **Kubernetes / Storage**: Grafana ID `11454`

**自定义告警**:

```yaml
# prometheusrule-storage.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: storage-alerts
  namespace: monitoring
spec:
  groups:
  - name: storage.rules
    interval: 30s
    rules:
    # PVC 使用率 > 85%
    - alert: PVCHighUsage
      expr: |
        (kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes) > 0.85
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "PVC {{ $labels.persistentvolumeclaim }} usage > 85%"
        description: "Namespace: {{ $labels.namespace }}, Usage: {{ $value | humanizePercentage }}"
    
    # PVC Inodes 不足
    - alert: PVCInodesFull
      expr: |
        (kubelet_volume_stats_inodes_used / kubelet_volume_stats_inodes) > 0.90
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "PVC {{ $labels.persistentvolumeclaim }} inodes > 90%"
    
    # PVC 挂载失败
    - alert: PVCMountFailed
      expr: |
        kube_persistentvolumeclaim_status_phase{phase="Pending"} > 0
      for: 15m
      labels:
        severity: warning
      annotations:
        summary: "PVC {{ $labels.persistentvolumeclaim }} pending for 15 minutes"
```

---

### 11.4 审计日志

**启用 PVC 审计**:

```yaml
# audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# 记录所有 PVC/PV 操作
- level: RequestResponse
  resources:
  - group: ""
    resources: ["persistentvolumeclaims", "persistentvolumes"]
  verbs: ["create", "delete", "patch"]

# 记录 StorageClass 变更
- level: RequestResponse
  resources:
  - group: "storage.k8s.io"
    resources: ["storageclasses"]
  verbs: ["create", "delete", "patch"]
```

**查询审计日志**:

```bash
# 查看 PVC 创建事件
kubectl logs kube-apiserver-xxx -n kube-system | \
  grep 'persistentvolumeclaims' | \
  grep 'create' | \
  jq '.responseObject.metadata.name'
```

---

## 12. 故障排查

### 12.1 常见问题

#### 12.1.1 PVC 一直 Pending

**现象**:

```bash
kubectl get pvc
# NAME       STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS
# app-data   Pending                                       fast-storage
```

**排查步骤**:

```bash
# 1. 查看 PVC 事件
kubectl describe pvc app-data

# 常见错误:
# - "waiting for a volume to be created"
# - "no nodes available to schedule pods"
# - "storageclass not found"

# 2. 检查 StorageClass
kubectl get storageclass fast-storage

# 3. 检查 CSI Provisioner
kubectl get pods -n kube-system | grep csi-provisioner

# 4. 查看 Provisioner 日志
kubectl logs -n kube-system csi-provisioner-xxx

# 5. 检查节点存储空间
kubectl describe node | grep -A 5 "Allocated resources"
```

---

#### 12.1.2 Pod 无法挂载 PVC

**现象**:

```bash
kubectl get pods
# NAME      READY   STATUS              RESTARTS   AGE
# app-pod   0/1     ContainerCreating   0          5m
```

**排查步骤**:

```bash
# 1. 查看 Pod 事件
kubectl describe pod app-pod

# 常见错误:
# - "MountVolume.MountDevice failed"
# - "Unable to attach or mount volumes"

# 2. 检查 PVC 状态
kubectl get pvc
# 确保 PVC 状态为 Bound

# 3. 检查 CSI Node Plugin
kubectl get pods -n kube-system | grep csi-plugin

# 4. 查看 Node Plugin 日志
kubectl logs -n kube-system longhorn-csi-plugin-xxx -c longhorn-csi-plugin

# 5. 检查节点 iSCSI 服务 (Longhorn)
kubectl exec -it longhorn-csi-plugin-xxx -n kube-system -- \
  iscsiadm -m session
```

---

### 12.2 诊断命令

**查看存储资源**:

```bash
# 查看所有 StorageClass
kubectl get storageclass

# 查看所有 PVC
kubectl get pvc -A

# 查看所有 PV
kubectl get pv

# 查看 PVC 详情
kubectl describe pvc app-data -n production

# 查看 PV 详情
kubectl describe pv pvc-xxx
```

**查看 CSI 组件**:

```bash
# 查看 CSI Driver
kubectl get csidrivers

# 查看 CSI Node
kubectl get csinodes

# 查看 Provisioner Pods
kubectl get pods -n kube-system | grep csi-provisioner

# 查看 Attacher Pods
kubectl get pods -n kube-system | grep csi-attacher
```

---

### 12.3 日志分析

**CSI Provisioner 日志**:

```bash
kubectl logs -n kube-system deployment/csi-provisioner | grep ERROR

# 常见错误:
# - "failed to provision volume": 存储后端故障
# - "timeout waiting for volume": 网络/存储性能问题
# - "quota exceeded": 配额超限
```

**CSI Attacher 日志**:

```bash
kubectl logs -n kube-system deployment/csi-attacher | grep ERROR

# 常见错误:
# - "failed to attach volume": 存储后端无法附加卷
# - "volume already attached": 卷重复附加
```

---

### 12.4 恢复流程

**PVC 挂起恢复**:

```bash
# 1. 强制删除 Pod (保留 PVC)
kubectl delete pod app-pod --force --grace-period=0

# 2. 检查 PVC 是否正常
kubectl get pvc

# 3. 重建 Pod
kubectl apply -f app-pod.yaml

# 4. 如果仍失败,删除并重建 PVC
kubectl delete pvc app-data
kubectl apply -f app-pvc.yaml
```

---

## 13. 最佳实践

### 13.1 StorageClass 设计原则

**1. 分层设计**:

```yaml
# 高性能层
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gold
parameters:
  diskSelector: "nvme"
  numberOfReplicas: "3"
---
# 标准层
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: silver
parameters:
  diskSelector: "ssd"
  numberOfReplicas: "2"
---
# 归档层
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: bronze
parameters:
  diskSelector: "hdd"
  numberOfReplicas: "2"
```

**2. 按应用分类**:

```yaml
# 数据库专用
- name: db-storage
  parameters:
    fsType: ext4
    dataLocality: best-effort
    
# 日志专用
- name: log-storage
  parameters:
    fsType: xfs
    numberOfReplicas: "2"
    
# 缓存专用
- name: cache-storage
  parameters:
    numberOfReplicas: "1"
    reclaimPolicy: Delete
```

---

### 13.2 命名规范

**推荐命名格式**:

```text
<性能等级>-<应用场景>-<存储类型>

示例:
- fast-db-rbd          (高性能数据库 RBD)
- standard-app-rbd     (标准应用 RBD)
- archive-backup-cephfs (归档备份 CephFS)
```

**标签规范**:

```yaml
metadata:
  labels:
    tier: gold              # 性能等级
    type: block             # 存储类型
    backup-enabled: "true"  # 功能标签
    cost-center: "eng"      # 成本中心
```

---

### 13.3 标签管理

**标准标签集合**:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: prod-storage
  labels:
    # 性能分层
    storage.k8s.io/tier: gold
    
    # 存储类型
    storage.k8s.io/type: block
    
    # 环境标识
    environment: production
    
    # 功能特性
    features.storage.k8s.io/backup: enabled
    features.storage.k8s.io/encryption: enabled
    features.storage.k8s.io/snapshot: enabled
    
    # 成本管理
    cost-center: engineering
    cost-tier: standard
```

---

### 13.4 安全加固

**1. 加密存储**:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: encrypted-storage
parameters:
  encrypted: "true"
  kms-key-id: "arn:aws:kms:us-east-1:123456789012:key/xxx"
```

**2. RBAC 最小权限**:

```yaml
# 仅允许特定命名空间使用特定 StorageClass
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: storage-user
  namespace: production
rules:
- apiGroups: [""]
  resources: ["persistentvolumeclaims"]
  verbs: ["create", "get", "list", "delete"]
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses"]
  verbs: ["get"]
  resourceNames: ["prod-storage"]  # 仅允许使用此 StorageClass
```

---

### 13.5 部署检查清单

**StorageClass 配置检查**:

- [ ] `provisioner` 正确且 CSI Driver 已安装
- [ ] `parameters` 符合存储后端要求
- [ ] `reclaimPolicy` 根据数据重要性选择 (Retain/Delete)
- [ ] `volumeBindingMode` 根据存储类型选择 (Immediate/WaitForFirstConsumer)
- [ ] `allowVolumeExpansion` 根据需求启用
- [ ] `mountOptions` 针对性能优化设置

**PVC 配置检查**:

- [ ] `accessModes` 符合应用需求
- [ ] `storageClassName` 正确且存在
- [ ] `resources.requests.storage` 合理评估
- [ ] `dataSource` (如需克隆/快照恢复) 正确配置

**监控告警检查**:

- [ ] Prometheus 抓取 Kubelet 指标
- [ ] Grafana 仪表板已导入
- [ ] 告警规则已配置 (容量/Inodes/挂载失败)
- [ ] 告警通道已测试 (邮件/Slack/PagerDuty)

**权限检查**:

- [ ] ServiceAccount 具有创建 PVC 权限
- [ ] ResourceQuota 配置合理
- [ ] LimitRange 避免单个 PVC 过大
- [ ] NetworkPolicy 限制存储网络访问

---

## 总结

**StorageClass 核心价值**:

- ✅ **简化运维**: 自动化 PV 创建,无需手动预创建
- ✅ **灵活配置**: 通过参数定制存储特性
- ✅ **多租户支持**: 不同租户使用不同存储类
- ✅ **成本优化**: 分层存储,按需分配

**关键功能**:

- 动态供应 (Dynamic Provisioning)
- 卷快照 (VolumeSnapshot)
- 卷克隆 (Volume Cloning)
- 卷扩容 (Volume Expansion)

**生产环境建议**:

- 创建多层级 StorageClass (Gold/Silver/Bronze)
- 为关键数据使用 Retain 策略
- 启用卷扩容 (allowVolumeExpansion)
- 配置监控告警 (容量/Inodes/挂载失败)
- 定期审计存储使用情况

---

**相关文档**:

- [CSI存储概述](01_CSI存储概述.md)
- [Rook-Ceph存储](02_Rook_Ceph存储.md)
- [Longhorn存储](03_Longhorn存储.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**Kubernetes 版本**: v1.21+
