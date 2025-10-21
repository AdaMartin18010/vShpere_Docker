# CSI存储概述

> **返回**: [容器存储目录](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 文档元信息

| 属性 | 值 |
|------|-----|
| **文档版本** | v2.0 (2025改进版) |
| **更新日期** | 2025-10-21 |
| **CSI版本** | v1.9.0, v1.8.x |
| **兼容版本** | v1.5.0+ |
| **标准对齐** | CNCF CSI Spec, Kubernetes Storage |
| **状态** | 生产就绪 |

> **版本锚点**: 本文档严格对齐CSI v1.9.0规范与Kubernetes 1.30存储模型。

---

## 📋 目录

- [CSI存储概述](#csi存储概述)
  - [文档元信息](#文档元信息)
  - [📋 目录](#-目录)
  - [1. CSI简介](#1-csi简介)
  - [2. CSI架构](#2-csi架构)
  - [3. 存储类型](#3-存储类型)
  - [4. 主流CSI驱动对比](#4-主流csi驱动对比)
  - [5. 存储选型指南](#5-存储选型指南)
  - [6. PV/PVC基础](#6-pvpvc基础)
  - [7. StorageClass配置](#7-storageclass配置)
  - [8. 存储快照](#8-存储快照)
  - [9. 存储扩容](#9-存储扩容)
  - [10. 最佳实践](#10-最佳实践)
  - [相关文档](#相关文档)

---

## 1. CSI简介

```yaml
CSI_Overview:
  全称: Container Storage Interface (容器存储接口)
  
  定义:
    - CNCF项目
    - 容器存储标准规范
    - 插件化架构
    - 容器编排系统和存储系统之间的接口
  
  目标:
    - 简化存储集成
    - 统一存储接口
    - 与编排系统解耦
    - 支持多种存储方案
  
  发展历史:
    2017: CSI规范v0.1发布
    2018: Kubernetes 1.13 CSI正式GA
    2019: CSI v1.0.0发布
    2020: 添加快照和克隆支持
    2023: 广泛应用于容器平台
  
  核心功能:
    - 卷的创建和删除
    - 卷的挂载和卸载
    - 卷的快照和克隆
    - 卷的扩容
    - 拓扑感知
```

---

## 2. CSI架构

```yaml
CSI_Architecture:
  组件结构:
    Controller Plugin:
      作用: 控制平面操作
      功能:
        - 创建/删除卷
        - 挂载/卸载卷
        - 创建快照
        - 扩容卷
      部署: StatefulSet/Deployment
      
    Node Plugin:
      作用: 节点级操作
      功能:
        - 挂载卷到节点
        - 格式化卷
        - 卸载卷
      部署: DaemonSet (每节点)
    
    CSI Sidecar容器:
      External Provisioner:
        - 监听PVC创建
        - 调用CSI创建卷
        - 创建PV
      
      External Attacher:
        - 监听VolumeAttachment
        - 调用CSI挂载卷
        - 更新状态
      
      External Resizer:
        - 监听PVC扩容
        - 调用CSI扩容卷
        - 更新容量
      
      External Snapshotter:
        - 监听快照请求
        - 调用CSI创建快照
        - 创建快照对象
      
      Node Driver Registrar:
        - 注册CSI驱动
        - 与Kubelet通信
        - 更新节点信息
      
      Liveness Probe:
        - 健康检查
        - 监控CSI驱动
  
  接口规范:
    Identity Service:
      - GetPluginInfo: 获取插件信息
      - GetPluginCapabilities: 获取插件能力
      - Probe: 健康检查
    
    Controller Service:
      - CreateVolume: 创建卷
      - DeleteVolume: 删除卷
      - ControllerPublishVolume: 挂载卷到节点
      - ControllerUnpublishVolume: 从节点卸载卷
      - ValidateVolumeCapabilities: 验证卷能力
      - ListVolumes: 列出卷
      - GetCapacity: 获取容量
      - CreateSnapshot: 创建快照
      - DeleteSnapshot: 删除快照
      - ControllerExpandVolume: 扩容卷
    
    Node Service:
      - NodeStageVolume: 暂存卷 (格式化)
      - NodeUnstageVolume: 取消暂存
      - NodePublishVolume: 发布卷 (挂载)
      - NodeUnpublishVolume: 取消发布
      - NodeGetCapabilities: 获取节点能力
      - NodeGetInfo: 获取节点信息
      - NodeExpandVolume: 节点扩容
```

**CSI架构图**:

```text
┌───────────────────────────────────────────┐
│        Kubernetes API Server              │
└─────────────┬─────────────────────────────┘
              │
      ┌───────┴──────────┐
      │                  │
┌─────▼──────────┐ ┌─────▼───────────┐
│   Controller   │ │    Node         │
│   Plugin       │ │    Plugin       │
│ ┌────────────┐ │ │ ┌─────────────┐ │
│ │External    │ │ │ │Node Driver  │ │
│ │Provisioner │ │ │ │Registrar    │ │
│ └────────────┘ │ │ └─────────────┘ │
│ ┌────────────┐ │ │ ┌─────────────┐ │
│ │External    │ │ │ │CSI Node     │ │
│ │Attacher    │ │ │ │Service      │ │
│ └────────────┘ │ │ └─────────────┘ │
│ ┌────────────┐ │ │                 │
│ │External    │ │ │  (每个节点)     │
│ │Resizer     │ │ │                 │
│ └────────────┘ │ └─────────────────┘
│ ┌────────────┐ │
│ │External    │ │
│ │Snapshotter │ │
│ └────────────┘ │
│ ┌────────────┐ │
│ │CSI         │ │
│ │Controller  │ │
│ │Service     │ │
│ └────────────┘ │
└────────────────┘
        │
        ▼
┌───────────────────┐
│  Storage Backend  │
│  (Ceph/NFS/iSCSI) │
└───────────────────┘
```

---

## 3. 存储类型

```yaml
Storage_Types:
  本地存储:
    类型:
      - Local PV: 本地磁盘
      - HostPath: 主机路径
      - EmptyDir: 临时存储
    
    特点:
      - 高性能
      - 低延迟
      - 节点亲和性
      - 无法迁移
    
    适用场景:
      - 高性能数据库
      - 缓存
      - 临时数据
  
  块存储 (Block):
    类型:
      - iSCSI
      - FC (Fiber Channel)
      - AWS EBS
      - GCE PD
      - Azure Disk
    
    特点:
      - 高性能
      - 单节点挂载 (RWO)
      - 直接访问
      - 需要格式化
    
    适用场景:
      - 数据库
      - 应用数据
      - 需要高IOPS
  
  文件存储 (File):
    类型:
      - NFS
      - CephFS
      - GlusterFS
      - AWS EFS
      - Azure Files
    
    特点:
      - 多节点共享 (RWX)
      - POSIX兼容
      - 易于使用
      - 性能一般
    
    适用场景:
      - 共享配置
      - 日志收集
      - 多Pod读写
  
  对象存储 (Object):
    类型:
      - S3
      - MinIO
      - Ceph RGW
      - Azure Blob
    
    特点:
      - 无限扩展
      - HTTP访问
      - 不支持POSIX
      - 成本低
    
    适用场景:
      - 备份归档
      - 静态资源
      - 大文件存储
  
  分布式存储:
    类型:
      - Rook-Ceph
      - Longhorn
      - OpenEBS
      - Portworx
    
    特点:
      - 高可用
      - 数据复制
      - 自动恢复
      - 云原生
    
    适用场景:
      - 生产环境
      - 关键数据
      - 多集群
  
  访问模式:
    RWO (ReadWriteOnce):
      - 单节点读写
      - 块存储
      - 数据库
    
    ROX (ReadOnlyMany):
      - 多节点只读
      - 配置共享
      - 静态内容
    
    RWX (ReadWriteMany):
      - 多节点读写
      - 文件存储
      - 共享数据
    
    RWOP (ReadWriteOncePod):
      - 单Pod读写
      - Kubernetes 1.22+
      - 严格隔离
```

---

## 4. 主流CSI驱动对比

```yaml
CSI_Drivers_Comparison:
  Rook-Ceph:
    类型: 分布式存储
    访问模式: RWO, ROX, RWX
    存储类型: Block, File, Object
    
    特性:
      - 高可用
      - 数据副本
      - 自动修复
      - 企业级功能
    
    性能: ★★★★☆
    稳定性: ★★★★★
    易用性: ★★★☆☆
    
    适用场景:
      - 大规模生产环境
      - 需要RWX
      - 对象存储需求
      - 企业级应用
    
    部署规模: 大规模 (3+节点)
  
  Longhorn:
    类型: 云原生分布式存储
    访问模式: RWO, RWX
    存储类型: Block, File
    
    特性:
      - 轻量级
      - 易于使用
      - 快照备份
      - UI管理
    
    性能: ★★★★☆
    稳定性: ★★★★☆
    易用性: ★★★★★
    
    适用场景:
      - 中小规模集群
      - 快速部署
      - 边缘计算
      - 简单易用
    
    部署规模: 中小规模 (3+节点)
  
  OpenEBS:
    类型: 容器化存储
    访问模式: RWO, ROX, RWX
    存储类型: Block, File
    
    特性:
      - 多引擎
      - 灵活配置
      - Local PV支持
      - CAS架构
    
    性能: ★★★★★ (Local PV)
    稳定性: ★★★★☆
    易用性: ★★★☆☆
    
    适用场景:
      - 高性能需求
      - 灵活部署
      - 混合方案
    
    部署规模: 灵活
  
  Portworx:
    类型: 企业级存储
    访问模式: RWO, ROX, RWX
    存储类型: Block, File
    
    特性:
      - 企业级
      - 多云支持
      - 数据服务
      - 商业支持
    
    性能: ★★★★★
    稳定性: ★★★★★
    易用性: ★★★★☆
    
    适用场景:
      - 企业生产环境
      - 多云部署
      - 关键业务
    
    部署规模: 大规模
    费用: 商业授权
  
  NFS CSI:
    类型: NFS客户端
    访问模式: RWO, ROX, RWX
    存储类型: File
    
    特性:
      - 简单易用
      - 成熟稳定
      - 广泛支持
      - 依赖NFS服务器
    
    性能: ★★★☆☆
    稳定性: ★★★★★
    易用性: ★★★★★
    
    适用场景:
      - 已有NFS
      - 共享存储
      - 测试环境
    
    部署规模: 任意
  
  Local Path Provisioner:
    类型: 本地存储
    访问模式: RWO
    存储类型: Local
    
    特性:
      - 极高性能
      - 简单快速
      - 无需额外组件
      - 无法迁移
    
    性能: ★★★★★
    稳定性: ★★★★☆
    易用性: ★★★★★
    
    适用场景:
      - 开发测试
      - 高性能需求
      - 单机应用
    
    部署规模: 任意
  
  云厂商CSI:
    AWS EBS CSI:
      - AWS EBS卷
      - RWO
      - 高性能
      - AWS集成
    
    Azure Disk CSI:
      - Azure Managed Disk
      - RWO
      - 高性能
      - Azure集成
    
    GCE PD CSI:
      - Google Persistent Disk
      - RWO
      - 高性能
      - GCP集成
```

**存储方案对比表**:

| 存储方案 | 类型 | 访问模式 | 性能 | 高可用 | 成本 | 复杂度 |
|---------|------|----------|------|-------|------|--------|
| Rook-Ceph | 分布式 | RWO/RWX | 高 | ✅ | 低 | 高 |
| Longhorn | 分布式 | RWO/RWX | 高 | ✅ | 低 | 中 |
| OpenEBS | 容器化 | RWO/RWX | 极高 | ✅ | 低 | 高 |
| Portworx | 企业级 | RWO/RWX | 极高 | ✅ | 高 | 中 |
| NFS | 文件 | RWX | 中 | ❌ | 低 | 低 |
| Local PV | 本地 | RWO | 极高 | ❌ | 低 | 低 |
| AWS EBS | 块 | RWO | 高 | ✅ | 中 | 低 |
| Azure Disk | 块 | RWO | 高 | ✅ | 中 | 低 |

---

## 5. 存储选型指南

```yaml
Storage_Selection_Guide:
  选型因素:
    性能要求:
      高性能: Local PV, OpenEBS Local, Portworx
      中等性能: Rook-Ceph, Longhorn, 云厂商
      共享存储: NFS, CephFS
    
    访问模式:
      RWO需求: 大部分CSI都支持
      RWX需求: Rook-Ceph (CephFS), NFS, Longhorn
      高性能RWO: Local PV, OpenEBS Local
    
    高可用要求:
      需要HA: Rook-Ceph, Longhorn, Portworx
      单机可接受: Local PV, NFS
    
    规模:
      小规模 (<10节点): Longhorn, NFS, Local PV
      中规模 (10-100): Longhorn, Rook-Ceph
      大规模 (>100): Rook-Ceph, Portworx
    
    环境:
      公有云: 云厂商CSI (EBS, Azure Disk)
      私有云/IDC: Rook-Ceph, Longhorn, OpenEBS
      边缘计算: Longhorn, Local PV
    
    预算:
      开源方案: Rook-Ceph, Longhorn, OpenEBS, NFS
      商业方案: Portworx
    
    运维能力:
      简单易用: Longhorn, NFS, Local PV
      需要专业: Rook-Ceph, OpenEBS, Portworx
  
  推荐方案:
    通用生产环境:
      首选: Rook-Ceph
      备选: Longhorn
      理由: 功能全面、高可用、成熟稳定
    
    高性能场景:
      首选: OpenEBS Local PV
      备选: Local Path Provisioner
      理由: 极致性能、低延迟
    
    简单场景:
      首选: Longhorn
      备选: NFS CSI
      理由: 简单易用、快速部署
    
    RWX需求:
      首选: Rook-Ceph (CephFS)
      备选: NFS CSI
      理由: 多节点读写、高可用
    
    云环境:
      AWS: AWS EBS CSI
      Azure: Azure Disk CSI
      GCP: GCE PD CSI
      理由: 原生集成、最佳性能
    
    边缘计算:
      首选: Longhorn
      备选: Local PV
      理由: 轻量级、易管理
```

---

## 6. PV/PVC基础

```yaml
PV_PVC_Basics:
  PersistentVolume (PV):
    定义:
      - 集群级资源
      - 存储实体
      - 由管理员创建或动态供应
    
    生命周期:
      - Available: 可用
      - Bound: 已绑定
      - Released: 已释放
      - Failed: 失败
    
    回收策略:
      - Retain: 保留 (手动回收)
      - Delete: 删除 (自动删除)
      - Recycle: 回收 (已废弃)
  
  PersistentVolumeClaim (PVC):
    定义:
      - 命名空间级资源
      - 存储请求
      - 由用户创建
    
    绑定:
      - 静态绑定: 手动创建PV
      - 动态绑定: StorageClass自动创建
  
  工作流程:
    静态供应:
      1. 管理员创建PV
      2. 用户创建PVC
      3. Kubernetes匹配PV和PVC
      4. 绑定成功
      5. Pod挂载PVC
    
    动态供应:
      1. 用户创建PVC (指定StorageClass)
      2. CSI Provisioner监听
      3. 调用CSI创建卷
      4. 创建PV
      5. 绑定PV和PVC
      6. Pod挂载PVC
```

**PV/PVC示例**:

```yaml
# ========================================
# PersistentVolume (静态)
# ========================================
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 10Gi
  volumeMode: Filesystem
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  nfs:
    server: 192.168.1.100
    path: /data/pv001

---
# ========================================
# PersistentVolumeClaim
# ========================================
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
  namespace: default
spec:
  storageClassName: manual
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
# ========================================
# Pod使用PVC
# ========================================
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: my-pvc
```

---

## 7. StorageClass配置

```yaml
# ========================================
# Rook-Ceph StorageClass (RBD)
# ========================================
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-ceph-block
provisioner: rook-ceph.rbd.csi.ceph.com
parameters:
  clusterID: rook-ceph
  pool: replicapool
  imageFormat: "2"
  imageFeatures: layering
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/controller-expand-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/controller-expand-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-rbd-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
  csi.storage.k8s.io/fstype: ext4
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: Immediate

---
# ========================================
# Longhorn StorageClass
# ========================================
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn
provisioner: driver.longhorn.io
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: Immediate
parameters:
  numberOfReplicas: "3"
  staleReplicaTimeout: "30"
  fromBackup: ""
  fsType: "ext4"

---
# ========================================
# NFS StorageClass
# ========================================
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-client
provisioner: nfs.csi.k8s.io
parameters:
  server: 192.168.1.100
  share: /data/nfs
  mountOptions: "vers=4.1"
reclaimPolicy: Delete
volumeBindingMode: Immediate
```

---

## 8. 存储快照

```yaml
# VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapshot-class
driver: rook-ceph.rbd.csi.ceph.com
deletionPolicy: Delete
parameters:
  clusterID: rook-ceph
  csi.storage.k8s.io/snapshotter-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/snapshotter-secret-namespace: rook-ceph

---
# VolumeSnapshot
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-snapshot
spec:
  volumeSnapshotClassName: csi-snapshot-class
  source:
    persistentVolumeClaimName: my-pvc

---
# 从快照恢复
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: restored-pvc
spec:
  storageClassName: rook-ceph-block
  dataSource:
    name: my-snapshot
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

---

## 9. 存储扩容

```bash
# ========================================
# 在线扩容PVC
# ========================================

# 1. 确保StorageClass允许扩容
kubectl get sc <storage-class> -o yaml | grep allowVolumeExpansion

# 2. 修改PVC容量
kubectl patch pvc <pvc-name> -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# 3. 查看扩容状态
kubectl describe pvc <pvc-name>

# 4. 等待扩容完成
kubectl get pvc <pvc-name> -w
```

---

## 10. 最佳实践

```yaml
Best_Practices:
  存储规划:
    ✅ 评估存储需求
    ✅ 选择合适的存储类型
    ✅ 规划存储容量
    ✅ 考虑数据增长
  
  StorageClass设计:
    ✅ 创建多个StorageClass
    ✅ 标记默认StorageClass
    ✅ 启用卷扩容
    ✅ 合理设置回收策略
  
  高可用:
    ✅ 使用副本存储
    ✅ 跨节点分布
    ✅ 定期备份
    ✅ 测试恢复
  
  性能优化:
    ✅ 选择高性能存储
    ✅ 使用SSD
    ✅ 优化副本数
    ✅ 启用缓存
  
  监控:
    ✅ 监控存储容量
    ✅ 监控IOPS
    ✅ 监控延迟
    ✅ 配置告警
  
  安全:
    ✅ 加密存储数据
    ✅ 访问控制
    ✅ 快照备份
    ✅ 审计日志
  
  运维:
    ✅ 自动化部署
    ✅ 定期维护
    ✅ 容量规划
    ✅ 故障演练
```

---

## 相关文档

- [Rook-Ceph存储](02_Rook_Ceph存储.md)
- [Longhorn存储](03_Longhorn存储.md)
- [StorageClass最佳实践](04_StorageClass最佳实践.md)
- [Kubernetes存储故障排查](../02_Kubernetes部署/05_故障排查.md#4-存储故障排查)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪
