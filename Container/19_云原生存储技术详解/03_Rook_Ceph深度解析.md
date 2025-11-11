# 03 - Rook/Ceph深度解析

**作者**: 云原生存储专家团队
**创建日期**: 2025-10-19
**最后更新**: 2025-10-19
**版本**: v1.0

---

## 📋 本章导航

- [03 - Rook/Ceph深度解析](#03---rookceph深度解析)
  - [📋 本章导航](#-本章导航)
  - [1. Ceph架构与原理](#1-ceph架构与原理)
    - [1.1 Ceph核心组件](#11-ceph核心组件)
    - [1.2 CRUSH算法](#12-crush算法)
    - [1.3 数据分布与副本](#13-数据分布与副本)
    - [1.4 Pool管理](#14-pool管理)
  - [2. Rook Operator](#2-rook-operator)
    - [2.1 Rook架构](#21-rook架构)
    - [2.2 CRD详解](#22-crd详解)
    - [2.3 Operator部署](#23-operator部署)
    - [2.4 集群管理](#24-集群管理)
  - [3. 块存储 (RBD)](#3-块存储-rbd)
    - [3.1 RBD概述与StorageClass](#31-rbd概述与storageclass)
  - [4. 文件存储 (CephFS)](#4-文件存储-cephfs)
    - [4.1 CephFS部署](#41-cephfs部署)
  - [5. 对象存储 (RGW)](#5-对象存储-rgw)
    - [5.1 RGW部署](#51-rgw部署)
  - [6. 监控与告警](#6-监控与告警)
    - [6.1 Prometheus集成](#61-prometheus集成)
  - [7. 生产级调优](#7-生产级调优)
    - [7.1 OSD调优](#71-osd调优)
  - [8. 总结](#8-总结)
    - [8.1 本章要点](#81-本章要点)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 1. Ceph架构与原理

### 1.1 Ceph核心组件

**Ceph架构概览**:

```text
Ceph分布式存储架构:

                    ┌─────────────────────────────────────┐
                    │         Client Applications         │
                    │  (RBD, CephFS, RGW, librados)       │
                    └──────────────┬──────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
    ┌────▼────┐              ┌────▼────┐              ┌────▼────┐
    │   RBD   │              │ CephFS  │              │   RGW   │
    │  块存储  │              │ 文件存储 │              │ 对象存储 │
    └────┬────┘              └────┬────┘              └────┬────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │         RADOS               │
                    │  (Reliable Autonomic        │
                    │   Distributed Object Store) │
                    └──────────────┬──────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
    ┌────▼────┐              ┌────▼────┐              ┌────▼────┐
    │   MON   │              │   OSD   │              │   MGR   │
    │  监控    │              │  存储   │              │  管理   │
    └─────────┘              └─────────┘              └─────────┘
```

**核心组件详解**:

```yaml
1. MON (Monitor):
   功能:
     - 维护集群状态 (cluster map)
     - 管理认证 (cephx)
     - 提供集群信息
     - 仲裁服务 (Paxos)

   部署要求:
     - 推荐奇数个 (3/5/7)
     - 最少3个保证高可用
     - 低延迟网络
     - 独立磁盘 (SSD推荐)

   核心Map:
     - Monitor Map: MON拓扑
     - OSD Map: OSD状态
     - PG Map: PG分布
     - CRUSH Map: 数据放置规则
     - MDS Map: MDS状态 (CephFS)

2. OSD (Object Storage Daemon):
   功能:
     - 存储数据 (对象)
     - 数据复制
     - 数据恢复
     - 数据再平衡
     - 心跳检查

   部署要求:
     - 每块磁盘一个OSD
     - 最少3个OSD (3副本)
     - SSD/NVMe推荐
     - 10Gb+网络

   存储引擎:
     - BlueStore (推荐): 直接管理裸设备
       - RocksDB元数据
       - 无需文件系统
       - 更高性能
     - FileStore (废弃): 基于文件系统
       - XFS推荐
       - 双写开销

3. MGR (Manager):
   功能:
     - 集群监控
     - 指标收集
     - 管理面板 (Dashboard)
     - REST API
     - 插件框架

   部署要求:
     - 至少1个 (推荐2个)
     - 自动failover
     - 低资源消耗

   常用模块:
     - dashboard: Web UI
     - prometheus: 监控导出
     - restful: REST API
     - balancer: 数据均衡
     - alerts: 告警

4. MDS (Metadata Server) - CephFS专用:
   功能:
     - 管理文件元数据
     - 目录树
     - 文件属性
     - 访问控制

   部署要求:
     - 至少1个active
     - 可配置standby
     - 大内存需求 (64GB+)
     - 高性能CPU

   工作模式:
     - Active: 服务元数据请求
     - Standby: 热备
     - Standby-replay: 实时replay日志

5. RGW (RADOS Gateway) - 对象存储专用:
   功能:
     - S3 API兼容
     - Swift API兼容
     - 多租户
     - Multi-site复制

   部署要求:
     - 无状态，可水平扩展
     - 负载均衡 (HAProxy/Nginx)
     - SSL/TLS支持

   特性:
     - Bucket管理
     - IAM权限
     - 生命周期策略
     - 版本控制
     - 跨域资源共享 (CORS)
```

**组件通信**:

```yaml
通信协议:
  MON <-> MON: Paxos (仲裁)
  Client <-> MON: librados (获取cluster map)
  Client <-> OSD: librados (数据I/O)
  OSD <-> OSD: 数据复制, 心跳
  MGR <-> MON: 获取集群状态
  MDS <-> OSD: 元数据存储

端口:
  MON: 6789 (v1), 3300 (v2)
  OSD: 6800-7300
  MGR: 8443 (Dashboard), 9283 (Prometheus)
  MDS: 6800+
  RGW: 7480 (HTTP), 7481 (HTTPS)

网络要求:
  公共网络 (public network):
    - Client访问
    - MON通信
    - 10Gb+推荐

  集群网络 (cluster network):
    - OSD间复制
    - 数据恢复
    - 10Gb+必须
    - 与公共网络分离 (推荐)
```

---

### 1.2 CRUSH算法

**CRUSH (Controlled Replication Under Scalable Hashing)** 是Ceph的核心数据分布算法。

**CRUSH特点**:

```yaml
核心特性:
  ✅ 伪随机分布
  ✅ 确定性 (输入相同输出相同)
  ✅ 可控副本放置
  ✅ 故障域隔离
  ✅ 动态再平衡

优势:
  ✅ 无中心元数据
  ✅ 高性能 (O(log n))
  ✅ 可扩展 (PB级)
  ✅ 故障自愈
  ✅ 支持复杂拓扑
```

**CRUSH Map层次结构**:

```text
CRUSH Map示例:

root default
├── datacenter dc1
│   ├── room room1
│   │   ├── row row1
│   │   │   ├── rack rack1
│   │   │   │   ├── host node1
│   │   │   │   │   ├── osd.0 (weight: 1.82TiB)
│   │   │   │   │   ├── osd.1 (weight: 1.82TiB)
│   │   │   │   │   └── osd.2 (weight: 1.82TiB)
│   │   │   │   └── host node2
│   │   │   │       ├── osd.3 (weight: 1.82TiB)
│   │   │   │       ├── osd.4 (weight: 1.82TiB)
│   │   │   │       └── osd.5 (weight: 1.82TiB)
│   │   │   └── rack rack2
│   │   │       ├── host node3
│   │   │       │   ├── osd.6 (weight: 1.82TiB)
│   │   │       │   ├── osd.7 (weight: 1.82TiB)
│   │   │       │   └── osd.8 (weight: 1.82TiB)
│   │   │       └── host node4
│   │   │           ├── osd.9 (weight: 1.82TiB)
│   │   │           ├── osd.10 (weight: 1.82TiB)
│   │   │           └── osd.11 (weight: 1.82TiB)
│   │   └── row row2
│   │       └── ... (更多机架和主机)
│   └── room room2
│       └── ... (更多机架和主机)
└── datacenter dc2
    └── ... (更多数据中心)

故障域层级:
  - osd: 单个OSD故障
  - host: 主机故障
  - rack: 机架故障 (电源/网络)
  - row: 行故障
  - room: 机房故障
  - datacenter: 数据中心故障
```

**CRUSH规则示例**:

```yaml
# 副本放置规则 (3副本, 跨机架)
rule replicated_rule {
  id 0
  type replicated
  min_size 1
  max_size 10
  step take default            # 从root开始
  step chooseleaf firstn 0 type rack  # 选择3个不同rack
  step emit                    # 输出结果
}

# 纠删码放置规则 (4+2, 跨主机)
rule erasure_rule {
  id 1
  type erasure
  min_size 3
  max_size 6
  step set_chooseleaf_tries 5
  step set_choose_tries 100
  step take default
  step chooseleaf indep 0 type host  # 选择6个不同host
  step emit
}

参数说明:
  type:
    - replicated: 副本模式
    - erasure: 纠删码模式

  chooseleaf:
    - firstn: 选择前N个 (副本)
    - indep: 独立选择 (纠删码)

  type:
    - osd: 按OSD隔离
    - host: 按主机隔离
    - rack: 按机架隔离
    - datacenter: 按数据中心隔离
```

**数据定位流程**:

```yaml
数据定位步骤:

1. Object -> PG映射:
   PG = hash(object_name + pool_id) % pg_num

   示例:
     object: "image1.raw"
     pool_id: 1
     pg_num: 128
     hash("image1.raw" + 1) = 0xABCD1234
     PG = 0xABCD1234 % 128 = 52
     结果: PG 1.52

2. PG -> OSD映射 (CRUSH):
   CRUSH(PG, cluster_map, rule) -> [primary_osd, replica_osd...]

   输入:
     - PG: 1.52
     - cluster_map: 当前集群状态
     - rule: replicated_rule

   输出:
     - [osd.3, osd.7, osd.11] (3副本)

   保证:
     ✅ 3个OSD在不同rack
     ✅ 确定性 (每次计算结果相同)
     ✅ 均匀分布

3. Client直接访问Primary OSD:
   Client -> osd.3 (primary)
     osd.3 -> osd.7 (replica)
     osd.3 -> osd.11 (replica)

   优势:
     ✅ 无中心瓶颈
     ✅ 高性能
     ✅ 自动failover
```

**查看CRUSH Map**:

```bash
# 获取CRUSH Map (二进制)
ceph osd getcrushmap -o /tmp/crushmap.bin

# 反编译为文本
crushtool -d /tmp/crushmap.bin -o /tmp/crushmap.txt

# 查看CRUSH Map
cat /tmp/crushmap.txt

# 查看CRUSH树
ceph osd tree

# 输出示例:
ID  CLASS  WEIGHT   TYPE NAME         STATUS  REWEIGHT  PRI-AFF
-1         10.92188  root default
-3          5.46094      host node1
 0    ssd   1.82031          osd.0     up   1.00000  1.00000
 1    ssd   1.82031          osd.1     up   1.00000  1.00000
 2    ssd   1.82031          osd.2     up   1.00000  1.00000
-5          5.46094      host node2
 3    ssd   1.82031          osd.3     up   1.00000  1.00000
 4    ssd   1.82031          osd.4     up   1.00000  1.00000
 5    ssd   1.82031          osd.5     up   1.00000  1.00000

# 查看CRUSH规则
ceph osd crush rule ls
ceph osd crush rule dump replicated_rule
```

**修改CRUSH Map**:

```bash
# 添加新OSD到指定位置
ceph osd crush add osd.12 1.82 host=node4 rack=rack2 room=room1 datacenter=dc1

# 调整OSD权重 (影响数据分布)
ceph osd crush reweight osd.0 1.50

# 移除OSD
ceph osd crush remove osd.0

# 创建新规则 (跨机架3副本)
ceph osd crush rule create-replicated my-rule default rack

# 修改Pool的CRUSH规则
ceph osd pool set my-pool crush_rule my-rule
```

---

### 1.3 数据分布与副本

**副本模式 vs 纠删码**:

```yaml
副本模式 (Replication):
  原理:
    - 每个对象完整复制N份
    - 典型: 3副本
    - 存储开销: 3x

  优势:
    ✅ 高性能 (无需编解码)
    ✅ 低延迟
    ✅ 故障恢复快
    ✅ 支持部分写入

  劣势:
    ❌ 存储效率低 (3x)
    ❌ 成本高

  适用场景:
    ✅ 数据库 (高IOPS)
    ✅ 虚拟机磁盘
    ✅ 热数据
    ✅ 小文件

纠删码 (Erasure Coding):
  原理:
    - 将对象分成K个数据块
    - 生成M个校验块
    - 总共K+M个块
    - 可容忍M个块丢失
    - 典型: 4+2 (可丢2块)

  存储开销:
    4+2: 1.5x (vs 3x副本)
    8+3: 1.375x
    8+4: 1.5x

  优势:
    ✅ 存储效率高 (1.5x vs 3x)
    ✅ 节省成本 (50%)
    ✅ 更高可靠性 (可丢更多块)

  劣势:
    ❌ 性能较低 (编解码开销)
    ❌ 延迟较高
    ❌ 恢复慢
    ❌ 不支持部分写入

  适用场景:
    ✅ 对象存储 (冷数据)
    ✅ 备份归档
    ✅ 大文件
    ✅ 低成本需求

对比表格:
| 特性 | 3副本 | 4+2 EC | 8+3 EC |
|------|-------|--------|--------|
| 存储开销 | 3x | 1.5x | 1.375x |
| 可容忍故障 | 2 | 2 | 3 |
| 读性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 写性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 恢复速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 成本 | 高 | 中 | 低 |
| 适用场景 | 热数据/数据库 | 温数据 | 冷数据/归档 |
```

**PG (Placement Group)**:

```yaml
PG概念:
  定义:
    - 逻辑分组
    - 对象集合
    - CRUSH的最小单位
    - 一个Pool包含多个PG
    - 一个PG映射到多个OSD

  作用:
    ✅ 简化数据管理
    ✅ 加速恢复
    ✅ 负载均衡
    ✅ 减少元数据

PG数量计算:
  公式:
    Total PGs = (OSDs × 100) / replicas

  示例:
    12 OSDs, 3副本:
      PGs = (12 × 100) / 3 = 400
      取最接近的2的幂: 512

  推荐:
    < 5 OSDs: 128 PGs
    5-10 OSDs: 512 PGs
    10-50 OSDs: 1024 PGs
    > 50 OSDs: 2048+ PGs

  注意:
    ⚠️ PG过少: 负载不均
    ⚠️ PG过多: 元数据开销大
    ✅ 平衡: 每个OSD约100个PG

PG状态:
  active: 正常服务
  clean: 所有副本正常
  degraded: 副本不足
  recovering: 数据恢复中
  backfilling: 数据回填中
  remapped: 重新映射
  peering: 副本间同步状态
  incomplete: PG不完整
  stale: PG通信中断
```

**示例: 创建不同类型的Pool**:

```bash
# 1. 创建3副本Pool
ceph osd pool create rbd-pool 128 128 replicated
ceph osd pool set rbd-pool size 3
ceph osd pool set rbd-pool min_size 2  # 最少2副本可写

# 2. 创建纠删码Profile
ceph osd erasure-code-profile set ec-profile-4-2 \
  k=4 \
  m=2 \
  crush-failure-domain=host \
  crush-device-class=ssd

# 查看EC Profile
ceph osd erasure-code-profile get ec-profile-4-2

# 3. 创建纠删码Pool
ceph osd pool create ec-pool 128 128 erasure ec-profile-4-2

# 4. 创建CephFS需要的Pool (数据+元数据)
ceph osd pool create cephfs-data 128
ceph osd pool create cephfs-metadata 64

# 5. 查看Pool
ceph osd pool ls detail

# 6. 查看PG分布
ceph pg dump
ceph pg stat

# 7. 查看Pool使用情况
ceph df
rados df

# 8. 调整PG数量 (谨慎操作)
ceph osd pool set rbd-pool pg_num 256
ceph osd pool set rbd-pool pgp_num 256
```

---

### 1.4 Pool管理

**Pool参数配置**:

```bash
# 创建Pool
ceph osd pool create my-pool <pg_num> <pgp_num> <type>

# 常用参数设置
ceph osd pool set my-pool size 3              # 副本数
ceph osd pool set my-pool min_size 2          # 最少副本
ceph osd pool set my-pool crush_rule replicated_rule  # CRUSH规则
ceph osd pool set my-pool compression_mode aggressive  # 压缩
ceph osd pool set my-pool compression_algorithm snappy # 压缩算法

# 配额设置
ceph osd pool set-quota my-pool max_objects 10000  # 最大对象数
ceph osd pool set-quota my-pool max_bytes 1099511627776  # 最大容量(1TB)

# Pool重命名
ceph osd pool rename old-name new-name

# 删除Pool (需要确认)
ceph osd pool delete my-pool my-pool --yes-i-really-really-mean-it

# 启用Pool应用
ceph osd pool application enable my-pool rbd  # RBD
ceph osd pool application enable my-pool cephfs  # CephFS
ceph osd pool application enable my-pool rgw  # RGW
```

**Pool压缩**:

```yaml
压缩模式:
  none: 不压缩
  passive: 客户端hint压缩
  aggressive: 所有数据压缩
  force: 强制压缩

压缩算法:
  snappy: 快速, 低压缩比 (推荐通用)
  zlib: 中等, 中压缩比
  zstd: 可调, 高压缩比 (推荐冷数据)
  lz4: 最快, 最低压缩比

配置示例:
  # 启用压缩
  ceph osd pool set my-pool compression_mode aggressive
  ceph osd pool set my-pool compression_algorithm snappy
  ceph osd pool set my-pool compression_required_ratio 0.875  # 压缩比阈值

  # 压缩统计
  ceph osd pool stats my-pool
```

## 2. Rook Operator

### 2.1 Rook架构

**Rook概述**:

```yaml
Rook特点:
  ✅ Kubernetes原生
  ✅ Operator模式
  ✅ 自动化管理
  ✅ 声明式配置
  ✅ 自愈能力
  ✅ 多存储后端 (Ceph, Cassandra, NFS)

Rook vs 传统Ceph:
  传统Ceph:
    - 手动部署
    - 配置复杂
    - 难以扩展
    - 运维负担重

  Rook:
    ✅ 一键部署
    ✅ CRD声明式
    ✅ 自动扩展
    ✅ 自动运维
```

**Rook架构图**:

```text
Rook-Ceph架构:

┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Rook Operator (Deployment)                 │ │
│  │  - Watch CRDs                                           │ │
│  │  - Reconcile Ceph Cluster                              │ │
│  │  - Manage Ceph Components                              │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                           │
│         ┌─────────┼──────────┬──────────┬──────────┐        │
│         │         │          │          │          │         │
│    ┌────▼────┐┌───▼─────┐┌───▼─────┐┌───▼─────┐┌───▼────┐  │
│    │CephCluster││CephBlock││CephFile││CephObject││CephNFS │  │
│    │   (CRD)   ││Pool(CRD)││System   ││Store(CRD)││(CRD)   │  │
│    └───────────┘└─────────┘│ (CRD)  │└──────────┘└────────┘  │
│                             └─────────┘                       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Ceph Components                      │ │
│  │                                                         │ │
│  │  ┌──────┐ ┌──────┐ ┌──────┐  ┌──────────┐             │ │
│  │  │ MON  │ │ MON  │ │ MON  │  │   MGR    │             │ │
│  │  │ Pod  │ │ Pod  │ │ Pod  │  │   Pod    │             │ │
│  │  └──────┘ └──────┘ └──────┘  └──────────┘             │ │
│  │                                                         │ │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                 │ │
│  │  │ OSD  │ │ OSD  │ │ OSD  │ │ OSD  │  ...            │ │
│  │  │ Pod  │ │ Pod  │ │ Pod  │ │ Pod  │                 │ │
│  │  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘                 │ │
│  │     │        │        │        │                      │ │
│  │  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐                 │ │
│  │  │/dev/│  │/dev/│  │/dev/│  │/dev/│                 │ │
│  │  │ sdb │  │ sdc │  │ sdd │  │ sde │                 │ │
│  │  └─────┘  └─────┘  └─────┘  └─────┘                 │ │
│  │                                                         │ │
│  │  ┌──────┐ ┌──────┐           ┌──────┐                │ │
│  │  │ MDS  │ │ MDS  │           │ RGW  │                │ │
│  │  │ Pod  │ │ Pod  │           │ Pod  │                │ │
│  │  └──────┘ └──────┘           └──────┘                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               CSI Drivers (DaemonSet)                   │ │
│  │  - RBD CSI Plugin                                       │ │
│  │  - CephFS CSI Plugin                                    │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

### 2.2 CRD详解

**Rook核心CRD**:

```yaml
1. CephCluster:
   作用: 定义Ceph集群

   示例:
     apiVersion: ceph.rook.io/v1
     kind: CephCluster
     metadata:
       name: rook-ceph
       namespace: rook-ceph
     spec:
       dataDirHostPath: /var/lib/rook
       mon:
         count: 3
         allowMultiplePerNode: false
       mgr:
         count: 2
       storage:
         useAllNodes: true
         useAllDevices: true

2. CephBlockPool:
   作用: 定义RBD存储池

   示例:
     apiVersion: ceph.rook.io/v1
     kind: CephBlockPool
     metadata:
       name: replicapool
       namespace: rook-ceph
     spec:
       replicated:
         size: 3
         requireSafeReplicaSize: true

3. CephFilesystem:
   作用: 定义CephFS文件系统

   示例:
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
       - replicated:
           size: 3
       metadataServer:
         activeCount: 1
         activeStandby: true

4. CephObjectStore:
   作用: 定义RGW对象存储

   示例:
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
       gateway:
         instances: 2
         port: 80

5. CephNFS:
   作用: 定义NFS Gateway

   示例:
     apiVersion: ceph.rook.io/v1
     kind: CephNFS
     metadata:
       name: my-nfs
       namespace: rook-ceph
     spec:
       rados:
         pool: myfs-data0
         namespace: nfs-ns
       server:
         active: 2
```

---

### 2.3 Operator部署

**完整部署流程**:

```bash
# 1. 下载Rook仓库
git clone --single-branch --branch v1.12.0 https://github.com/rook/rook.git
cd rook/deploy/examples

# 2. 部署Rook Operator
kubectl create -f crds.yaml
kubectl create -f common.yaml
kubectl create -f operator.yaml

# 3. 验证Operator
kubectl -n rook-ceph get pod
# NAME                                  READY   STATUS    AGE
# rook-ceph-operator-xxx                1/1     Running   30s
# rook-discover-xxx                     1/1     Running   30s
# rook-discover-yyy                     1/1     Running   30s

# 4. 准备节点磁盘 (每个节点)
# 列出可用磁盘
lsblk -f

# 清理磁盘 (如果之前使用过)
sudo sgdisk --zap-all /dev/sdb
sudo dd if=/dev/zero of=/dev/sdb bs=1M count=100 oflag=direct,dsync
sudo blkdiscard /dev/sdb

# 5. 创建Ceph集群
kubectl create -f cluster.yaml

# 6. 等待集群就绪
kubectl -n rook-ceph get cephcluster
# NAME        DATADIRHOSTPATH   MONCOUNT   AGE   PHASE   MESSAGE   HEALTH
# rook-ceph   /var/lib/rook     3          60s   Ready             HEALTH_OK

# 7. 查看Ceph Pods
kubectl -n rook-ceph get pod
# NAME                                     READY   STATUS      AGE
# csi-cephfsplugin-provisioner-xxx         6/6     Running     3m
# csi-cephfsplugin-xxx                     3/3     Running     3m
# csi-rbdplugin-provisioner-xxx            6/6     Running     3m
# csi-rbdplugin-xxx                        3/3     Running     3m
# rook-ceph-crashcollector-node1-xxx       1/1     Running     2m
# rook-ceph-mgr-a-xxx                      1/1     Running     2m
# rook-ceph-mon-a-xxx                      1/1     Running     3m
# rook-ceph-mon-b-xxx                      1/1     Running     3m
# rook-ceph-mon-c-xxx                      1/1     Running     3m
# rook-ceph-operator-xxx                   1/1     Running     10m
# rook-ceph-osd-0-xxx                      1/1     Running     2m
# rook-ceph-osd-1-xxx                      1/1     Running     2m
# rook-ceph-osd-2-xxx                      1/1     Running     2m
# rook-ceph-osd-prepare-node1-xxx          0/1     Completed   2m
# rook-ceph-osd-prepare-node2-xxx          0/1     Completed   2m
# rook-ceph-osd-prepare-node3-xxx          0/1     Completed   2m

# 8. 部署Toolbox (管理工具)
kubectl create -f toolbox.yaml

# 9. 使用Toolbox执行Ceph命令
kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- bash
# 在toolbox中:
ceph status
ceph osd status
ceph osd tree
ceph df
rados df
```

**完整cluster.yaml示例**:

```yaml
apiVersion: ceph.rook.io/v1
kind: CephCluster
metadata:
  name: rook-ceph
  namespace: rook-ceph
spec:
  cephVersion:
    image: quay.io/ceph/ceph:v17.2.6  # Ceph Quincy
    allowUnsupported: false

  dataDirHostPath: /var/lib/rook

  # 跳过OSD设备升级确认
  skipUpgradeChecks: false

  # 持续健康检查
  continueUpgradeAfterChecksEvenIfNotHealthy: false

  # MON配置
  mon:
    count: 3  # 奇数个
    allowMultiplePerNode: false
    volumeClaimTemplate:
      spec:
        storageClassName: local-storage
        resources:
          requests:
            storage: 10Gi

  # MGR配置
  mgr:
    count: 2  # 高可用
    allowMultiplePerNode: false
    modules:
    - name: pg_autoscaler
      enabled: true
    - name: rook
      enabled: true

  # Dashboard
  dashboard:
    enabled: true
    ssl: true
    port: 8443

  # Prometheus监控
  monitoring:
    enabled: true
    createPrometheusRules: true

  # 网络配置
  network:
    provider: host  # host或multus
    connections:
      encryption:
        enabled: false
      compression:
        enabled: false

    # 双网络配置 (可选)
    # hostNetwork: true
    # provider: multus
    # selectors:
    #   public: public-network
    #   cluster: cluster-network

  # Crash收集器
  crashCollector:
    disable: false

  # 日志收集器
  logCollector:
    enabled: true
    periodicity: daily
    maxLogSize: 500M

  # 清理策略
  cleanupPolicy:
    confirmation: ""  # yes-really-destroy-data (删除集群时清理数据)
    sanitizeDisks:
      method: quick  # quick或complete
      dataSource: zero  # zero或random
      iteration: 1
    allowUninstallWithVolumes: false

  # OSD存储配置
  storage:
    useAllNodes: true
    useAllDevices: false  # 不自动使用所有设备

    # 设备选择
    deviceFilter: "^sd[b-z]"  # 正则匹配设备名
    devicePathFilter: "^/dev/disk/by-path/.*-ssd.*"  # 路径过滤

    # 节点配置
    nodes:
    - name: "node1"
      devices:
      - name: "/dev/sdb"
      - name: "/dev/sdc"
    - name: "node2"
      devices:
      - name: "/dev/sdb"
      - name: "/dev/sdc"
    - name: "node3"
      devices:
      - name: "/dev/sdb"
      - name: "/dev/sdc"

    # OSD配置
    config:
      osdsPerDevice: "1"  # 每个设备1个OSD
      encryptedDevice: "false"  # 加密
      metadataDevice: ""  # 元数据设备 (SSD)
      databaseSizeMB: "1024"  # RocksDB大小
      walSizeMB: "576"  # WAL大小
      journalSizeMB: "5120"  # Journal大小

    # StorageClass设备分类
    storageClassDeviceSets:
    - name: set1
      count: 3  # 创建3个OSD
      portable: true
      tuneDeviceClass: true
      encrypted: false
      placement:
        tolerations:
        - effect: NoSchedule
          key: storage-node
          operator: Exists
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - rook-ceph-osd
            topologyKey: kubernetes.io/hostname
      resources:
        limits:
          cpu: "2"
          memory: "4Gi"
        requests:
          cpu: "1"
          memory: "2Gi"
      volumeClaimTemplates:
      - metadata:
          name: data
        spec:
          accessModes: [ "ReadWriteOnce" ]
          resources:
            requests:
              storage: 100Gi
          storageClassName: local-storage
          volumeMode: Block

  # 资源限制
  resources:
    mgr:
      limits:
        cpu: "1"
        memory: "2Gi"
      requests:
        cpu: "500m"
        memory: "1Gi"
    mon:
      limits:
        cpu: "2"
        memory: "4Gi"
      requests:
        cpu: "1"
        memory: "2Gi"
    osd:
      limits:
        cpu: "2"
        memory: "4Gi"
      requests:
        cpu: "1"
        memory: "2Gi"
    prepareosd:
      limits:
        cpu: "1"
        memory: "1Gi"
      requests:
        cpu: "500m"
        memory: "500Mi"
    crashcollector:
      limits:
        cpu: "100m"
        memory: "60Mi"
      requests:
        cpu: "50m"
        memory: "60Mi"

  # 优先级
  priorityClassNames:
    mgr: system-cluster-critical
    mon: system-cluster-critical
    osd: system-node-critical

  # 健康检查
  healthCheck:
    daemonHealth:
      mon:
        disabled: false
        interval: 45s
      osd:
        disabled: false
        interval: 60s
      status:
        disabled: false
        interval: 60s
    livenessProbe:
      mon:
        disabled: false
      mgr:
        disabled: false
      osd:
        disabled: false
```

---

### 2.4 集群管理

**常用管理命令**:

```bash
# 进入Toolbox
kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- bash

# === 集群状态 ===
ceph status
ceph health detail

# === OSD管理 ===
ceph osd status
ceph osd tree
ceph osd df

# === Pool管理 ===
ceph osd pool ls detail
ceph df
```

---

## 3. 块存储 (RBD)

### 3.1 RBD概述与StorageClass

**创建RBD StorageClass**:

```yaml
# 1. CephBlockPool
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: replicapool
  namespace: rook-ceph
spec:
  replicated:
    size: 3
---
# 2. StorageClass
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
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-rbd-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
  csi.storage.k8s.io/fstype: ext4
reclaimPolicy: Delete
allowVolumeExpansion: true
```

---

## 4. 文件存储 (CephFS)

### 4.1 CephFS部署

```yaml
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
  - replicated:
      size: 3
  metadataServer:
    activeCount: 1
    activeStandby: true
```

---

## 5. 对象存储 (RGW)

### 5.1 RGW部署

```yaml
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
  gateway:
    instances: 2
```

---

## 6. 监控与告警

### 6.1 Prometheus集成

```yaml
monitoring:
  enabled: true
  createPrometheusRules: true
```

---

## 7. 生产级调优

### 7.1 OSD调优

```yaml
# BlueStore配置
osd_memory_target: 4294967296  # 4GB
bluestore_cache_size_ssd: 3221225472  # 3GB
```

---

## 8. 总结

### 8.1 本章要点

```yaml
核心知识:
  ✅ Ceph架构 (MON/OSD/MGR/MDS/RGW)
  ✅ CRUSH算法
  ✅ Rook Operator部署
  ✅ 块/文件/对象存储
  ✅ 监控调优
```

---

**完成日期**: 2025-10-19
**版本**: v1.0
**作者**: 云原生存储专家团队

**Tags**: `#RookCeph` `#Ceph` `#DistributedStorage` `#CloudNativeStorage`

---

## 相关文档

### 本模块相关

- [云原生存储概述与架构](./01_云原生存储概述与架构.md) - 云原生存储概述与架构
- [Kubernetes存储基础](./02_Kubernetes存储基础.md) - Kubernetes存储基础
- [Velero备份恢复](./04_Velero备份恢复.md) - Velero备份恢复
- [CSI驱动详解](./05_CSI驱动详解.md) - CSI驱动详解
- [存储性能优化](./06_存储性能优化.md) - 存储性能优化
- [多云存储](./07_多云存储.md) - 多云存储
- [存储安全](./08_存储安全.md) - 存储安全
- [实战案例](./09_实战案例.md) - 实战案例
- [最佳实践](./10_最佳实践.md) - 最佳实践
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [容器存储技术](../05_容器存储技术/README.md) - 容器存储技术
- [高级存储技术](../05_容器存储技术/02_高级存储技术.md) - 高级存储技术
- [Kubernetes存储管理](../03_Kubernetes技术详解/04_存储管理技术.md) - K8s存储管理
- [容器编排技术](../04_容器编排技术/README.md) - 容器编排技术

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新
