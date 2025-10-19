# Rook-Ceph存储

> **返回**: [容器存储目录](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Rook-Ceph存储](#rook-ceph存储)
  - [📋 目录](#-目录)
  - [1. Rook-Ceph简介](#1-rook-ceph简介)
  - [2. Ceph架构](#2-ceph架构)
  - [3. Rook架构](#3-rook架构)
  - [4. Rook-Ceph部署](#4-rook-ceph部署)
    - [前置要求](#前置要求)
    - [安装步骤](#安装步骤)
  - [5. RBD块存储](#5-rbd块存储)
  - [6. CephFS文件存储](#6-cephfs文件存储)
  - [7. RGW对象存储](#7-rgw对象存储)
  - [8. 存储管理](#8-存储管理)
  - [9. 监控与运维](#9-监控与运维)
  - [10. 最佳实践](#10-最佳实践)
  - [相关文档](#相关文档)

---

## 1. Rook-Ceph简介

```yaml
Rook_Ceph_Overview:
  Rook:
    定义:
      - CNCF毕业项目
      - 云原生存储编排器
      - Kubernetes Operator
      - 自动化存储管理
    
    支持存储:
      - Ceph (主要)
      - NFS
      - Cassandra (已废弃)
      - EdgeFS (已废弃)
  
  Ceph:
    定义:
      - 开源分布式存储
      - 统一存储平台
      - 高可用高扩展
      - 企业级功能
    
    存储类型:
      - RBD: 块存储
      - CephFS: 文件存储
      - RGW: 对象存储
  
  Rook-Ceph优势:
    - 云原生设计
    - Operator自动化
    - 简化部署
    - 自我修复
    - 滚动升级
    - 多集群管理
  
  适用场景:
    - 生产环境存储
    - 多Pod共享存储
    - 对象存储需求
    - 企业级应用
    - 大规模集群
```

---

## 2. Ceph架构

```yaml
Ceph_Architecture:
  核心组件:
    Monitor (MON):
      作用: 集群监控
      功能:
        - 维护集群状态
        - 管理集群拓扑
        - 认证授权
        - 故障检测
      推荐数量: 3个或5个 (奇数)
    
    OSD (Object Storage Daemon):
      作用: 存储数据
      功能:
        - 存储对象
        - 数据复制
        - 数据恢复
        - 数据平衡
      推荐: 每块磁盘一个OSD
    
    Manager (MGR):
      作用: 管理服务
      功能:
        - 监控指标
        - Dashboard
        - REST API
        - 模块管理
      推荐数量: 2个 (主备)
    
    MDS (Metadata Server):
      作用: CephFS元数据
      功能:
        - 文件系统元数据
        - 目录结构
        - 权限管理
      需求: 仅CephFS需要
      推荐数量: 2个 (主备)
    
    RGW (RADOS Gateway):
      作用: 对象存储网关
      功能:
        - S3 API
        - Swift API
        - 对象存储
        - 多租户
      需求: 仅对象存储需要
  
  数据组织:
    Object:
      - 最小存储单元
      - 默认4MB
      - 包含数据和元数据
    
    PG (Placement Group):
      - 对象逻辑分组
      - CRUSH算法映射
      - 数据分布
      - 推荐: 100-200 PG/OSD
    
    Pool:
      - PG集合
      - 存储策略
      - 副本数/纠删码
      - 访问控制
  
  CRUSH算法:
    - Controlled Replication Under Scalable Hashing
    - 伪随机数据分布
    - 无需中心元数据
    - 拓扑感知
    - 故障域隔离
```

**Ceph架构图**:

```text
┌─────────────────────────────────────────────┐
│            Client Applications               │
│     (RBD / CephFS / RGW)                    │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┴──────┐
        │   librados  │  (Ceph客户端库)
        └──────┬──────┘
               │
┌──────────────▼──────────────────────────────┐
│            RADOS (可靠自主分布式对象存储)      │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌──▼────┐
│ MON   │  │  MGR  │  │  MDS  │
│ (监控) │  │(管理) │  │(元数据)│
└───────┘  └───────┘  └───────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌──▼────┐
│ OSD-1 │  │ OSD-2 │  │ OSD-3 │
│ Disk1 │  │ Disk2 │  │ Disk3 │
└───────┘  └───────┘  └───────┘
```

---

## 3. Rook架构

```yaml
Rook_Architecture:
  组件:
    Rook Operator:
      - 核心控制器
      - 监听CRD
      - 管理Ceph集群
      - 自动化运维
    
    Rook Agent:
      - 节点代理 (已废弃)
      - 使用CSI替代
    
    Rook Discover:
      - 磁盘发现
      - 节点标记
      - 自动化准备
    
    CSI Driver:
      - RBD CSI
      - CephFS CSI
      - 卷管理
      - 动态供应
  
  CRD资源:
    CephCluster:
      - 定义Ceph集群
      - 配置MON/OSD/MGR
      - 集群级别设置
    
    CephBlockPool:
      - 定义存储池
      - RBD使用
      - 副本配置
    
    CephFilesystem:
      - 定义文件系统
      - CephFS使用
      - MDS配置
    
    CephObjectStore:
      - 定义对象存储
      - RGW配置
      - S3 API
    
    CephNFS:
      - NFS服务
      - Ganesha配置
```

---

## 4. Rook-Ceph部署

### 前置要求

```yaml
Prerequisites:
  硬件要求:
    节点数量: >=3 (生产环境)
    CPU: 每OSD 1核
    内存: 每OSD 2-4GB
    存储:
      - 原始块设备 (推荐)
      - 未格式化
      - 未挂载
      - GPT分区清除
  
  软件要求:
    Kubernetes: >=1.21
    内核: >=4.17 (RBD), >=4.17 (CephFS)
    工具: lvm2
```

### 安装步骤

```bash
# ========================================
# 1. 部署Rook Operator
# ========================================

# 克隆Rook仓库
git clone --single-branch --branch v1.12.0 https://github.com/rook/rook.git
cd rook/deploy/examples

# 部署CRD和Operator
kubectl create -f crds.yaml
kubectl create -f common.yaml
kubectl create -f operator.yaml

# 验证Operator
kubectl get pods -n rook-ceph

# ========================================
# 2. 创建Ceph集群
# ========================================

# 编辑cluster.yaml (根据需要)
cat <<EOF > cluster.yaml
apiVersion: ceph.rook.io/v1
kind: CephCluster
metadata:
  name: rook-ceph
  namespace: rook-ceph
spec:
  cephVersion:
    image: quay.io/ceph/ceph:v17.2.6
    allowUnsupported: false
  
  dataDirHostPath: /var/lib/rook
  
  mon:
    count: 3
    allowMultiplePerNode: false
  
  mgr:
    count: 2
    allowMultiplePerNode: false
  
  dashboard:
    enabled: true
    ssl: true
  
  monitoring:
    enabled: true
  
  storage:
    useAllNodes: true
    useAllDevices: true
    # 或指定设备
    # config:
    #   osdsPerDevice: "1"
  
  priorityClassNames:
    mon: system-node-critical
    osd: system-node-critical
    mgr: system-cluster-critical
EOF

# 部署集群
kubectl create -f cluster.yaml

# 查看集群状态
kubectl get cephcluster -n rook-ceph
kubectl get pods -n rook-ceph -w

# ========================================
# 3. 安装Rook工具箱
# ========================================

kubectl create -f toolbox.yaml

# 进入工具箱
kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- bash

# 查看Ceph状态
ceph status
ceph osd status
ceph df
ceph health detail

# ========================================
# 4. 访问Dashboard
# ========================================

# 获取Dashboard地址
kubectl get svc -n rook-ceph | grep dashboard

# 端口转发
kubectl port-forward -n rook-ceph svc/rook-ceph-mgr-dashboard 8443:8443

# 获取admin密码
kubectl -n rook-ceph get secret rook-ceph-dashboard-password -o jsonpath="{['data']['password']}" | base64 --decode

# 浏览器访问: https://localhost:8443
# 用户名: admin
```

---

## 5. RBD块存储

```yaml
# ========================================
# 1. 创建Block Pool
# ========================================
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: replicapool
  namespace: rook-ceph
spec:
  failureDomain: host
  replicated:
    size: 3  # 副本数
    requireSafeReplicaSize: true
  deviceClass: ssd  # 可选: hdd/ssd/nvme

---
# ========================================
# 2. 创建StorageClass
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
# 3. 创建PVC
# ========================================
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rbd-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: rook-ceph-block

---
# ========================================
# 4. 使用PVC
# ========================================
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: rbd-pvc
```

**RBD管理命令**:

```bash
# 在工具箱中执行
kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- bash

# 查看RBD池
ceph osd pool ls

# 查看RBD镜像
rbd ls -p replicapool

# 查看镜像详情
rbd info replicapool/<image-name>

# 查看镜像使用
rbd du -p replicapool

# 删除镜像
rbd rm replicapool/<image-name>
```

---

## 6. CephFS文件存储

```yaml
# ========================================
# 1. 创建文件系统
# ========================================
apiVersion: ceph.rook.io/v1
kind: CephFilesystem
metadata:
  name: myfs
  namespace: rook-ceph
spec:
  metadataPool:
    replicated:
      size: 3
  dataPools:
  - name: replicated
    replicated:
      size: 3
  
  preserveFilesystemOnDelete: false
  
  metadataServer:
    activeCount: 1
    activeStandby: true

---
# ========================================
# 2. 创建StorageClass
# ========================================
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-cephfs
provisioner: rook-ceph.cephfs.csi.ceph.com
parameters:
  clusterID: rook-ceph
  fsName: myfs
  pool: myfs-replicated
  
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/controller-expand-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/controller-expand-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-cephfs-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: Immediate

---
# ========================================
# 3. 创建RWX PVC
# ========================================
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cephfs-pvc
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: rook-cephfs

---
# ========================================
# 4. 多Pod共享
# ========================================
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx
        volumeMounts:
        - name: shared-data
          mountPath: /usr/share/nginx/html
      volumes:
      - name: shared-data
        persistentVolumeClaim:
          claimName: cephfs-pvc
```

---

## 7. RGW对象存储

```yaml
# ========================================
# 1. 创建对象存储
# ========================================
apiVersion: ceph.rook.io/v1
kind: CephObjectStore
metadata:
  name: my-store
  namespace: rook-ceph
spec:
  metadataPool:
    replicated:
      size: 3
  dataPool:
    replicated:
      size: 3
  preservePoolsOnDelete: false
  
  gateway:
    port: 80
    instances: 2
    priorityClassName: system-cluster-critical

---
# ========================================
# 2. 创建StorageClass
# ========================================
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-ceph-bucket
provisioner: rook-ceph.ceph.rook.io/bucket
reclaimPolicy: Delete
parameters:
  objectStoreName: my-store
  objectStoreNamespace: rook-ceph

---
# ========================================
# 3. 创建Object Bucket Claim
# ========================================
apiVersion: objectbucket.io/v1alpha1
kind: ObjectBucketClaim
metadata:
  name: my-bucket
spec:
  generateBucketName: my-bucket
  storageClassName: rook-ceph-bucket

---
# ========================================
# 4. 访问对象存储
# ========================================
# 获取访问凭证
kubectl get secret my-bucket -o yaml

# 使用S3 API访问
# Endpoint: http://rook-ceph-rgw-my-store.rook-ceph:80
# Access Key: 从secret获取
# Secret Key: 从secret获取
```

**S3客户端使用**:

```bash
# 安装AWS CLI
pip install awscli

# 配置
export AWS_ACCESS_KEY_ID=<access-key>
export AWS_SECRET_ACCESS_KEY=<secret-key>
export AWS_ENDPOINT=http://rook-ceph-rgw-my-store.rook-ceph:80

# 列出bucket
aws s3 ls --endpoint-url $AWS_ENDPOINT

# 上传文件
aws s3 cp file.txt s3://my-bucket/ --endpoint-url $AWS_ENDPOINT

# 下载文件
aws s3 cp s3://my-bucket/file.txt . --endpoint-url $AWS_ENDPOINT
```

---

## 8. 存储管理

```bash
# ========================================
# OSD管理
# ========================================

# 查看OSD
ceph osd tree
ceph osd status

# OSD out (维护前)
ceph osd out osd.0

# OSD in
ceph osd in osd.0

# 移除OSD
ceph osd crush remove osd.0
ceph auth del osd.0
ceph osd rm osd.0

# ========================================
# 存储池管理
# ========================================

# 查看池
ceph osd pool ls detail

# 创建池
ceph osd pool create mypool 128 128

# 设置副本数
ceph osd pool set mypool size 3

# 设置PG数
ceph osd pool set mypool pg_num 256

# 删除池
ceph osd pool delete mypool mypool --yes-i-really-really-mean-it

# ========================================
# PG管理
# ========================================

# 查看PG
ceph pg stat
ceph pg dump

# 查看PG状态
ceph pg <pgid> query

# 修复PG
ceph pg repair <pgid>

# ========================================
# 集群维护
# ========================================

# 查看集群健康
ceph health detail

# 查看集群状态
ceph status

# 查看IO统计
ceph osd perf

# 查看空间使用
ceph df

#停止自动平衡 (维护时)
ceph osd set noout
ceph osd set norebalance

# 恢复
ceph osd unset noout
ceph osd unset norebalance
```

---

## 9. 监控与运维

```yaml
# ========================================
# Prometheus监控
# ========================================
# Rook自动部署Ceph exporter

# 查看Service Monitor
kubectl get servicemonitor -n rook-ceph

# Grafana Dashboard
# 导入Ceph Dashboard: ID 2842

# ========================================
# 告警规则
# ========================================
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ceph-alerts
  namespace: rook-ceph
spec:
  groups:
  - name: ceph
    rules:
    - alert: CephHealthWarning
      expr: ceph_health_status{job="rook-ceph-mgr"} == 1
      for: 5m
      annotations:
        summary: "Ceph health warning"
    
    - alert: CephOSDDown
      expr: ceph_osd_up < 1
      for: 5m
      annotations:
        summary: "Ceph OSD down"
```

---

## 10. 最佳实践

```yaml
Best_Practices:
  部署规划:
    ✅ 至少3个节点
    ✅ 使用SSD作为OSD
    ✅ 独立的网络 (10GbE+)
    ✅ 预留足够空间
  
  配置优化:
    ✅ MON数量: 3或5个 (奇数)
    ✅ OSD副本数: 3 (生产)
    ✅ PG数量: 100-200/OSD
    ✅ 启用Dashboard
  
  性能优化:
    ✅ 使用NVMe SSD
    ✅ 分离MON和OSD
    ✅ 优化PG数量
    ✅ 启用BlueStore
  
  高可用:
    ✅ 多副本
    ✅ 跨主机/机架
    ✅ 故障域隔离
    ✅ 定期备份
  
  监控:
    ✅ Prometheus + Grafana
    ✅ Ceph Dashboard
    ✅ 告警规则
    ✅ 容量规划
  
  运维:
    ✅ 定期巡检
    ✅ 升级计划
    ✅ 故障演练
    ✅ 文档维护
```

---

## 相关文档

- [CSI存储概述](01_CSI存储概述.md)
- [Longhorn存储](03_Longhorn存储.md)
- [StorageClass最佳实践](04_StorageClass最佳实践.md)
- [Kubernetes存储故障排查](../02_Kubernetes部署/05_故障排查.md#4-存储故障排查)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪
