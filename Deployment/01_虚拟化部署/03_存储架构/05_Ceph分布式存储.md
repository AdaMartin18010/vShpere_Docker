# Ceph分布式存储

> **返回**: [存储架构目录](README.md) | [虚拟化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Ceph分布式存储](#ceph分布式存储)
  - [📋 目录](#-目录)
  - [Ceph概述](#ceph概述)
  - [Ceph架构与组件](#ceph架构与组件)
  - [Ceph硬件要求](#ceph硬件要求)
  - [Ceph集群部署](#ceph集群部署)
  - [存储池与数据管理](#存储池与数据管理)
  - [RBD块存储](#rbd块存储)
  - [CephFS文件系统](#cephfs文件系统)
  - [对象存储网关](#对象存储网关)
  - [Ceph性能优化](#ceph性能优化)
  - [监控与运维](#监控与运维)
  - [故障排查](#故障排查)
  - [相关文档](#相关文档)

---

## Ceph概述

```yaml
Ceph简介:
  定义:
    开源分布式存储系统
    统一存储平台 (块/文件/对象)
    软件定义存储 (SDS)
    CRUSH算法驱动
  
  核心特性:
    ✅ 统一存储接口
    ✅ 高可用性 (无单点故障)
    ✅ 自动数据分布与平衡
    ✅ 自我修复
    ✅ 横向扩展 (Scale-Out)
    ✅ 开源免费 (Apache 2.0)
  
  版本历史:
    Pacific (16.x):
      发布: 2021年
      状态: 稳定 LTS
      特性: cephadm部署, 改进监控
    
    Quincy (17.x):
      发布: 2022年
      状态: 当前 LTS
      特性: 性能提升, RBD镜像改进
    
    Reef (18.x):
      发布: 2023年
      状态: 最新稳定
      特性: 简化管理, 增强安全
  
  存储接口:
    块存储 (RBD - RADOS Block Device):
      协议: Kernel RBD, librbd
      用途: 虚拟机磁盘, Kubernetes PV
      性能: 优秀 (低延迟)
      客户端: Linux内核, QEMU/KVM, OpenStack
    
    文件存储 (CephFS):
      协议: POSIX兼容
      用途: 共享文件系统
      性能: 良好
      客户端: Linux内核, FUSE, Windows (Samba)
    
    对象存储 (RGW - RADOS Gateway):
      协议: S3, Swift
      用途: 对象存储, 云存储
      性能: 良好
      客户端: S3 API客户端

  适用场景:
    ✅ 云平台存储 (OpenStack, CloudStack)
    ✅ Kubernetes持久卷
    ✅ 虚拟化存储 (Proxmox, oVirt)
    ✅ 大数据存储
    ✅ 备份归档
    ✅ 对象存储服务
  
  不适用场景:
    ⚠️ 极低延迟 (<0.5ms)
    ⚠️ 小型环境 (<3节点)
    ⚠️ 事务型数据库 (OLTP)
    ⚠️ 资源受限环境

  优势:
    ✅ 开源免费
    ✅ 统一存储平台
    ✅ 无单点故障
    ✅ 横向扩展
    ✅ 自动修复
    ✅ 社区活跃
  
  劣势:
    ❌ 学习曲线陡峭
    ❌ 硬件资源消耗高
    ❌ 小集群性能一般
    ❌ 运维复杂度高
```

---

## Ceph架构与组件

```yaml
Ceph核心组件:
  Monitor (MON):
    角色: 集群状态管理
    功能:
      - 维护集群映射 (cluster map)
      - 提供认证服务
      - 管理配置变更
      - 监控集群健康
    
    数量: 
      最少: 1 (测试)
      推荐: 3 (生产)
      大型: 5-7 (高可用)
    
    配置:
      CPU: 2-4核心
      内存: 2-4GB
      存储: 50GB SSD (存储集群映射)
      网络: 1GbE+
    
    注意: Monitor不存储用户数据
  
  OSD (Object Storage Daemon):
    角色: 数据存储与管理
    功能:
      - 存储对象数据
      - 数据复制
      - 数据修复
      - 数据平衡
      - 提供容量
    
    数量:
      最少: 3 OSD
      推荐: 每节点3-10 OSD
      大型: 数百到数千 OSD
    
    配置:
      1 OSD = 1 磁盘 (推荐)
      CPU: 0.5-2核心/OSD
      内存: 4-8GB/OSD (取决于数据量)
      存储: HDD或SSD
      网络: 10GbE+ (专用后端网络)
    
    类型:
      BlueStore (默认):
        直接管理裸设备
        性能优秀
        推荐: Ceph 12.2+
      
      FileStore (已弃用):
        基于文件系统 (XFS)
        Ceph 14+已移除
  
  Manager (MGR):
    角色: 管理与监控
    功能:
      - Dashboard Web界面
      - RESTful API
      - 监控指标收集
      - 插件系统 (Prometheus, Zabbix)
    
    数量:
      最少: 1
      推荐: 2 (主备)
    
    配置:
      CPU: 2-4核心
      内存: 2-4GB
  
  MDS (Metadata Server):
    角色: CephFS元数据管理
    功能:
      - 管理文件系统元数据
      - 文件/目录结构
      - 权限管理
    
    数量:
      CephFS需要: 至少1个
      高可用: 2+ (主备)
    
    配置:
      CPU: 4-8核心
      内存: 2-32GB (取决于文件数量)
    
    注意: 仅CephFS需要MDS

  RGW (RADOS Gateway):
    角色: 对象存储接口
    功能:
      - S3 API
      - Swift API
      - 用户管理
      - 多租户
    
    数量:
      可选: 按需部署
      高可用: 2+ (负载均衡)
    
    配置:
      CPU: 2-4核心
      内存: 4-8GB

Ceph数据分布:
  CRUSH算法:
    定义: Controlled Replication Under Scalable Hashing
    作用: 伪随机数据分布
    特点:
      - 确定性 (给定输入，输出唯一)
      - 去中心化 (客户端直接计算)
      - 自动平衡
      - 支持多层次拓扑
  
  CRUSH Map:
    定义: 集群物理拓扑
    层次: root → datacenter → rack → host → osd
    规则: 定义数据放置策略
  
  数据流:
    1. 客户端写入数据到Pool
    2. Pool映射到PG (Placement Group)
    3. CRUSH算法计算PG → OSD映射
    4. 数据写入到主OSD
    5. 主OSD复制到副本OSD
    6. 全部OSD确认后返回成功

  存储池 (Pool):
    定义: 逻辑存储分区
    类型:
      副本池 (Replicated):
        数据完整复制
        副本数: 2-3
        空间效率: 33-50%
      
      纠删码池 (Erasure Coded):
        数据分片+校验
        配置: k+m (如4+2)
        空间效率: 67-80%
        性能: 写性能较低
  
  PG (Placement Group):
    定义: 对象到OSD的中间层
    作用: 简化数据管理
    数量计算:
      PG数 = (OSD总数 × 100) / 副本数
      向上取2的幂次
    
    示例:
      30 OSD, 3副本: (30 × 100) / 3 = 1000 → 1024 PG
```

---

## Ceph硬件要求

```yaml
最小集群配置 (测试):
  节点数: 3
  每节点:
    CPU: 4核心
    内存: 8GB
    系统盘: 50GB SSD
    OSD盘: 2x 1TB HDD
    网络: 1GbE
  
  集群总计:
    12核心, 24GB内存, 6 OSD
    容量: 6TB原始 (2TB可用, 3副本)

生产集群配置 (小型):
  节点数: 3-5
  每节点:
    CPU: 16核心
    内存: 64GB
    系统盘: 240GB SSD (RAID1)
    OSD盘: 10x 4TB HDD
    日志/DB盘: 1x 800GB SSD (共享)
    网络: 2x 10GbE (前端+后端)
  
  集群总计 (5节点):
    80核心, 320GB内存, 50 OSD
    容量: 200TB原始 (66TB可用, 3副本)

生产集群配置 (中型全闪存):
  节点数: 5-7
  每节点:
    CPU: 32核心
    内存: 128GB
    系统盘: 480GB SSD (RAID1)
    OSD盘: 12x 3.84TB NVMe SSD
    网络: 2x 25GbE (前端+后端)
  
  集群总计 (7节点):
    224核心, 896GB内存, 84 OSD
    容量: 323TB原始 (107TB可用, 3副本)
    性能: IOPS >500K

硬件选型建议:
  CPU:
    推荐: Intel Xeon或AMD EPYC
    核心数: 1-2核心/OSD + 基础开销
    示例: 10 OSD → 16核心
  
  内存:
    公式: 4-8GB/OSD (BlueStore)
    基础: MON/MGR 4GB
    示例:
      10 OSD → 64GB (4GB×10 + 24GB系统)
      MDS (CephFS) → 额外8-32GB
  
  存储:
    OSD磁盘:
      HDD:
        容量: 4TB-12TB
        转速: 7.2K (经济) 或 10K (性能)
        接口: SATA/SAS
        适用: 大容量场景
      
      SSD:
        容量: 1.92TB-7.68TB
        接口: SATA/SAS/NVMe
        耐久性: 1+ DWPD
        适用: 高性能场景
      
      NVMe:
        容量: 1.92TB-15.36TB
        接口: PCIe 3.0/4.0
        耐久性: 3+ DWPD
        适用: 极高性能
    
    BlueStore DB/WAL盘:
      类型: SSD或NVMe
      大小:
        DB: OSD容量的4% (HDD后端)
        WAL: 512MB-2GB
      共享: 1个SSD可服务4-6个HDD OSD
    
    系统盘:
      容量: 240GB+ SSD
      RAID: RAID1 (可选)
  
  网络:
    前端网络 (Public Network):
      用途: 客户端访问
      带宽: 10GbE+
      VLAN: 独立VLAN
    
    后端网络 (Cluster Network):
      用途: OSD间复制
      带宽: 10/25GbE
      VLAN: 独立VLAN (与前端隔离)
      推荐: 2x NIC (冗余)
    
    拓扑:
      小型: 单10GbE (前后端共享)
      中型: 前端10GbE + 后端10GbE
      大型: 前端25GbE + 后端25GbE
  
  控制器:
    推荐: HBA直通模式
    型号: LSI 9300/9400系列
    避免: RAID控制器 (除非JBOD)

存储规划:
  副本池 (3副本):
    原始容量 → 可用容量 ≈ 原始 × 0.33 × 0.7
    # 0.33=1/3, 0.7=预留30%
  
  纠删码池 (4+2):
    原始容量 → 可用容量 ≈ 原始 × 0.67 × 0.7
  
  示例:
    60 OSD × 4TB HDD, 3副本:
      原始: 240TB
      可用: 240TB × 0.33 × 0.7 ≈ 55TB
```

---

## Ceph集群部署

```yaml
部署方法对比:
  cephadm (推荐):
    版本: Ceph 15.2+ (Octopus)
    工具: 容器化部署
    优点:
      ✅ 官方推荐
      ✅ 简化部署
      ✅ 容器隔离
      ✅ 自动化管理
    
    适用: 新集群
  
  ceph-ansible:
    工具: Ansible playbook
    优点:
      ✅ 灵活
      ✅ 适合大规模
      ✅ 可定制
    
    缺点:
      ⚠️ 需要Ansible经验
      ⚠️ 维护复杂
  
  手动部署:
    适用: 学习/小型测试
    不推荐: 生产环境

部署前准备:
  操作系统:
    推荐:
      ✅ Ubuntu 20.04/22.04 LTS
      ✅ Rocky Linux 8/9
      ✅ CentOS Stream 9
    
    内核: 5.4+
  
  时间同步:
    要求: 所有节点时间一致
    配置: NTP或Chrony
    验证: timedatectl
  
  主机名与DNS:
    要求: 解析正确
    配置: /etc/hosts或DNS
    验证: ping 主机名
  
  防火墙:
    选择:
      关闭防火墙 (测试)
      配置防火墙规则 (生产)
    
    端口:
      MON: 3300, 6789
      MGR: 6800-7300, 8443 (Dashboard)
      OSD: 6800-7300
      MDS: 6800
      RGW: 7480, 8080
  
  SSH免密:
    管理节点 → 所有节点
    配置: ssh-keygen + ssh-copy-id

使用cephadm部署:
  环境: 3节点集群
    node1: 192.168.30.11 (MON, MGR, OSD)
    node2: 192.168.30.12 (MON, OSD)
    node3: 192.168.30.13 (MON, OSD)
```

```bash
#!/bin/bash
# Ceph集群部署脚本 - cephadm方式
# 在node1执行

set -e

echo "========================================="
echo "  Ceph集群部署 (cephadm)"
echo "========================================="
echo ""

# 1. 安装依赖
echo "步骤1: 安装依赖..."
if command -v apt &> /dev/null; then
    apt update
    apt install -y python3 python3-pip lvm2 podman
elif command -v dnf &> /dev/null; then
    dnf install -y python3 python3-pip lvm2 podman
fi

# 2. 下载cephadm
echo ""
echo "步骤2: 下载cephadm..."
curl --silent --remote-name --location https://github.com/ceph/ceph/raw/quincy/src/cephadm/cephadm
chmod +x cephadm

# 3. 添加Ceph仓库
echo ""
echo "步骤3: 添加Ceph仓库..."
./cephadm add-repo --release quincy
./cephadm install

# 4. Bootstrap引导集群
echo ""
echo "步骤4: Bootstrap引导集群..."
cephadm bootstrap \
  --mon-ip 192.168.30.11 \
  --cluster-network 192.168.30.0/24 \
  --initial-dashboard-user admin \
  --initial-dashboard-password 'AdminP@ssw0rd!' \
  --allow-fqdn-hostname \
  --skip-monitoring-stack

# 输出信息
echo ""
echo "========================================="
echo "  Bootstrap完成"
echo "========================================="
echo ""
echo "Dashboard URL: https://192.168.30.11:8443"
echo "Username: admin"
echo "Password: AdminP@ssw0rd!"
echo ""
echo "查看集群状态:"
echo "  ceph -s"
echo ""

# 5. 添加Ceph CLI别名
echo "步骤5: 配置CLI..."
cephadm shell -- ceph -v
alias ceph='cephadm shell -- ceph'

# 6. 安装ceph-common (可选)
echo ""
echo "步骤6: 安装ceph-common..."
cephadm install ceph-common

# 7. 添加其他主机
echo ""
echo "步骤7: 添加其他主机..."

# 复制SSH密钥到其他节点
ssh-copy-id -f -i /etc/ceph/ceph.pub root@192.168.30.12
ssh-copy-id -f -i /etc/ceph/ceph.pub root@192.168.30.13

# 添加主机
ceph orch host add node2 192.168.30.12
ceph orch host add node3 192.168.30.13

# 8. 部署MON守护进程
echo ""
echo "步骤8: 部署Monitor..."
ceph orch apply mon 3  # 部署3个MON

# 9. 部署MGR守护进程
echo ""
echo "步骤9: 部署Manager..."
ceph orch apply mgr 2  # 部署2个MGR

# 10. 部署OSD
echo ""
echo "步骤10: 部署OSD..."

# 方法1: 自动发现并部署所有可用磁盘
ceph orch apply osd --all-available-devices

# 方法2: 手动指定磁盘 (推荐)
# ceph orch daemon add osd node1:/dev/sdb
# ceph orch daemon add osd node1:/dev/sdc
# ceph orch daemon add osd node2:/dev/sdb
# ceph orch daemon add osd node2:/dev/sdc
# ceph orch daemon add osd node3:/dev/sdb
# ceph orch daemon add osd node3:/dev/sdc

echo ""
echo "等待OSD创建完成..."
sleep 30

# 11. 验证集群
echo ""
echo "========================================="
echo "  集群验证"
echo "========================================="
echo ""

echo "集群状态:"
ceph -s

echo ""
echo "集群拓扑:"
ceph orch ps

echo ""
echo "OSD列表:"
ceph osd tree

echo ""
echo "存储池:"
ceph osd lspools

echo ""
echo "========================================="
echo "  部署完成"
echo "========================================="
echo ""
echo "下一步:"
echo "  1. 访问Dashboard: https://192.168.30.11:8443"
echo "  2. 创建存储池: ceph osd pool create <pool-name> <pg-num>"
echo "  3. 配置客户端访问"
```

**手动配置OSD（带单独DB/WAL盘）**:

```bash
# 场景: 10个HDD OSD + 1个SSD作为DB/WAL盘

# 1. 创建逻辑卷 (在SSD上)
SSD_DEV="/dev/nvme0n1"
for i in {1..10}; do
    lvcreate -L 40G -n db$i ceph-db $SSD_DEV
    lvcreate -L 2G -n wal$i ceph-wal $SSD_DEV
done

# 2. 创建OSD
for i in {1..10}; do
    HDD_DEV="/dev/sd${i}"
    ceph-volume lvm create \
      --data $HDD_DEV \
      --block.db ceph-db/db$i \
      --block.wal ceph-wal/wal$i
done
```

---

## 存储池与数据管理

```yaml
存储池管理:
  创建副本池:
    命令:
      ceph osd pool create <pool-name> <pg-num> <pgp-num> replicated
    
    示例:
      # 创建RBD池, 3副本, 128 PG
      ceph osd pool create rbd 128 128 replicated
      ceph osd pool set rbd size 3
      ceph osd pool set rbd min_size 2
      
      # 初始化RBD池
      rbd pool init rbd
  
  创建纠删码池:
    命令:
      # 先创建纠删码profile
      ceph osd erasure-code-profile set <profile-name> k=4 m=2
      
      # 创建池
      ceph osd pool create <pool-name> <pg-num> <pgp-num> erasure <profile-name>
    
    示例:
      # 4+2纠删码池
      ceph osd erasure-code-profile set ec42 k=4 m=2
      ceph osd pool create ec-pool 128 128 erasure ec42
  
  常用池配置:
    副本数:
      ceph osd pool set <pool> size 3
      ceph osd pool set <pool> min_size 2
    
    PG数调整:
      ceph osd pool set <pool> pg_num 256
      ceph osd pool set <pool> pgp_num 256
    
    应用类型:
      ceph osd pool application enable <pool> rbd
      # 类型: rbd, cephfs, rgw
  
  删除池:
    # 需要先允许删除
    ceph tell mon.* injectargs '--mon-allow-pool-delete=true'
    ceph osd pool delete <pool> <pool> --yes-i-really-really-mean-it

PG数量计算:
  公式:
    PG总数 = (OSD总数 × 100) / 最大副本数
    每个池PG数 = PG总数 / 池数量
    结果向上取2的幂次
  
  示例:
    30 OSD, 3副本, 3个池:
      PG总数 = (30 × 100) / 3 = 1000
      每池PG数 = 1000 / 3 ≈ 333 → 512 (2的幂次)
  
  工具:
    在线计算器:
      https://ceph.io/pgcalc/

快照管理:
  池快照:
    创建: ceph osd pool mksnap <pool> <snap-name>
    删除: ceph osd pool rmsnap <pool> <snap-name>
    列表: rados -p <pool> lssnap
  
  RBD快照:
    创建: rbd snap create <pool>/<image>@<snap>
    保护: rbd snap protect <pool>/<image>@<snap>
    克隆: rbd clone <pool>/<image>@<snap> <pool>/<new-image>
    删除: rbd snap rm <pool>/<image>@<snap>

配额管理:
  设置池配额:
    # 最大对象数
    ceph osd pool set-quota <pool> max_objects 10000
    
    # 最大容量
    ceph osd pool set-quota <pool> max_bytes $((100 * 1024**3))  # 100GB
  
  查看配额:
    ceph osd pool get-quota <pool>
```

---

## RBD块存储

```yaml
RBD概述:
  定义: RADOS Block Device
  功能: 块设备接口
  特点:
    ✅ 精简置备
    ✅ 快照
    ✅ 克隆
    ✅ 镜像 (灾备)
    ✅ 加密
  
  客户端:
    Kernel RBD: Linux内核模块
    librbd: 用户空间库 (QEMU/KVM)
```

```bash
#!/bin/bash
# RBD块存储配置脚本

echo "========================================="
echo "  RBD块存储配置"
echo "========================================="
echo ""

# 1. 创建RBD存储池
echo "步骤1: 创建RBD池..."
ceph osd pool create rbd 128 128 replicated
ceph osd pool set rbd size 3
ceph osd pool set rbd min_size 2
ceph osd pool application enable rbd rbd
rbd pool init rbd

# 2. 创建RBD镜像
echo ""
echo "步骤2: 创建RBD镜像..."

# 创建10GB镜像
rbd create --size 10240 rbd/disk01
rbd create --size 10240 rbd/disk02

# 启用特性
rbd feature enable rbd/disk01 object-map fast-diff
rbd feature enable rbd/disk02 object-map fast-diff

# 查看镜像
echo ""
echo "RBD镜像列表:"
rbd ls rbd
rbd info rbd/disk01

# 3. 映射RBD到本地 (Linux客户端)
echo ""
echo "步骤3: 映射RBD设备..."

# 映射
rbd map rbd/disk01

# 查看映射
rbd showmapped

# 格式化并挂载
DEV=$(rbd showmapped | grep disk01 | awk '{print $5}')
mkfs.ext4 $DEV
mkdir -p /mnt/rbd-disk01
mount $DEV /mnt/rbd-disk01

echo ""
echo "RBD设备已挂载到: /mnt/rbd-disk01"

# 4. 快照管理
echo ""
echo "步骤4: 快照管理..."

# 创建快照
rbd snap create rbd/disk01@snap1

# 保护快照 (用于克隆)
rbd snap protect rbd/disk01@snap1

# 从快照克隆
rbd clone rbd/disk01@snap1 rbd/disk01-clone

# 列出快照
rbd snap ls rbd/disk01

# 5. 性能测试
echo ""
echo "步骤5: 性能测试..."
rbd bench --io-type write rbd/disk01 --io-size 4096 --io-threads 16 --io-total 1G

echo ""
echo "========================================="
echo "  配置完成"
echo "========================================="
```

**Kubernetes集成（RBD）**:

```yaml
# StorageClass配置
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rbd-sc
provisioner: rbd.csi.ceph.com
parameters:
  clusterID: <ceph-cluster-id>
  pool: kubernetes
  imageFeatures: layering
  csi.storage.k8s.io/provisioner-secret-name: csi-rbd-secret
  csi.storage.k8s.io/provisioner-secret-namespace: default
  csi.storage.k8s.io/controller-expand-secret-name: csi-rbd-secret
  csi.storage.k8s.io/controller-expand-secret-namespace: default
  csi.storage.k8s.io/node-stage-secret-name: csi-rbd-secret
  csi.storage.k8s.io/node-stage-secret-namespace: default
  csi.storage.k8s.io/fstype: ext4
reclaimPolicy: Delete
allowVolumeExpansion: true
mountOptions:
  - discard
```

```yaml
# PVC示例
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rbd-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: rbd-sc
  resources:
    requests:
      storage: 10Gi
```

---

## CephFS文件系统

```yaml
CephFS概述:
  定义: Ceph文件系统
  协议: POSIX兼容
  架构: 元数据(MDS) + 数据(OSD)
  特点:
    ✅ 共享访问 (多客户端)
    ✅ 目录快照
    ✅ 配额管理
    ✅ 高可用MDS
```

```bash
#!/bin/bash
# CephFS部署脚本

echo "========================================="
echo "  CephFS部署"
echo "========================================="
echo ""

# 1. 创建存储池
echo "步骤1: 创建CephFS存储池..."

# 元数据池 (小, SSD)
ceph osd pool create cephfs_metadata 64 64 replicated
ceph osd pool set cephfs_metadata size 3

# 数据池 (大)
ceph osd pool create cephfs_data 256 256 replicated
ceph osd pool set cephfs_data size 3

# 2. 创建文件系统
echo ""
echo "步骤2: 创建CephFS..."
ceph fs new cephfs cephfs_metadata cephfs_data

# 3. 部署MDS
echo ""
echo "步骤3: 部署MDS..."
ceph orch apply mds cephfs --placement="3"

# 等待MDS启动
sleep 10

# 查看MDS状态
ceph fs status cephfs

# 4. 挂载CephFS (Kernel driver)
echo ""
echo "步骤4: 挂载CephFS..."

# 创建挂载点
mkdir -p /mnt/cephfs

# 获取密钥
KEY=$(ceph auth get-key client.admin)

# 挂载
mount -t ceph 192.168.30.11:6789:/ /mnt/cephfs \
  -o name=admin,secret=$KEY

echo ""
echo "CephFS已挂载到: /mnt/cephfs"

# 5. 永久挂载 (/etc/fstab)
cat >> /etc/fstab <<EOF
192.168.30.11:6789:/  /mnt/cephfs  ceph  name=admin,secretfile=/etc/ceph/admin.secret,noatime,_netdev  0  0
EOF

echo $KEY > /etc/ceph/admin.secret
chmod 600 /etc/ceph/admin.secret

# 6. 配置配额
echo ""
echo "步骤6: 配置配额..."

# 创建目录
mkdir -p /mnt/cephfs/projects/project1

# 设置配额
setfattr -n ceph.quota.max_bytes -v 107374182400 /mnt/cephfs/projects/project1  # 100GB
setfattr -n ceph.quota.max_files -v 1000000 /mnt/cephfs/projects/project1

# 查看配额
getfattr -n ceph.quota.max_bytes /mnt/cephfs/projects/project1

echo ""
echo "========================================="
echo "  部署完成"
echo "========================================="
```

**Kubernetes集成（CephFS）**:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: cephfs-sc
provisioner: cephfs.csi.ceph.com
parameters:
  clusterID: <ceph-cluster-id>
  fsName: cephfs
  pool: cephfs_data
  csi.storage.k8s.io/provisioner-secret-name: csi-cephfs-secret
  csi.storage.k8s.io/provisioner-secret-namespace: default
  csi.storage.k8s.io/controller-expand-secret-name: csi-cephfs-secret
  csi.storage.k8s.io/controller-expand-secret-namespace: default
  csi.storage.k8s.io/node-stage-secret-name: csi-cephfs-secret
  csi.storage.k8s.io/node-stage-secret-namespace: default
reclaimPolicy: Delete
allowVolumeExpansion: true
mountOptions:
  - debug
```

---

## 对象存储网关

```yaml
RGW概述:
  定义: RADOS Gateway
  协议: S3, Swift
  用途: 对象存储API
  特点:
    ✅ S3兼容
    ✅ 多租户
    ✅ 用户管理
    ✅ 配额
```

```bash
#!/bin/bash
# RGW部署脚本

echo "========================================="
echo "  RADOS Gateway部署"
echo "========================================="
echo ""

# 1. 部署RGW
echo "步骤1: 部署RGW..."
ceph orch apply rgw myrgw --placement="2 node1 node2" --port=8080

# 等待启动
sleep 15

# 2. 创建用户
echo ""
echo "步骤2: 创建S3用户..."
radosgw-admin user create \
  --uid=testuser \
  --display-name="Test User" \
  --email=test@example.com \
  --access-key=TESTKEY123 \
  --secret-key=TESTSECRET456

# 3. 创建存储桶
echo ""
echo "步骤3: 创建存储桶..."

# 安装s3cmd
pip3 install s3cmd

# 配置s3cmd
cat > ~/.s3cfg <<EOF
[default]
access_key = TESTKEY123
secret_key = TESTSECRET456
host_base = 192.168.30.11:8080
host_bucket = 192.168.30.11:8080
use_https = False
EOF

# 创建bucket
s3cmd mb s3://mybucket

# 上传文件
echo "Hello Ceph RGW" > test.txt
s3cmd put test.txt s3://mybucket/

# 列出对象
s3cmd ls s3://mybucket/

echo ""
echo "========================================="
echo "  RGW部署完成"
echo "========================================="
echo ""
echo "S3 Endpoint: http://192.168.30.11:8080"
echo "Access Key: TESTKEY123"
echo "Secret Key: TESTSECRET456"
```

---

## Ceph性能优化

```yaml
OSD性能优化:
  BlueStore配置:
    # ceph.conf或覆盖
    [osd]
    osd_op_num_threads_per_shard = 2
    osd_op_num_shards = 8
    bluestore_cache_size = 4GB  # HDD
    bluestore_cache_size = 8GB  # SSD
  
  网络优化:
    [global]
    ms_async_op_threads = 5
    ms_async_max_op_threads = 10
  
  日志优化:
    [osd]
    osd_max_write_size = 512
    osd_client_message_size_cap = 2147483648
    osd_deep_scrub_stride = 131072

客户端优化:
  RBD缓存:
    [client]
    rbd_cache = true
    rbd_cache_size = 33554432  # 32MB
    rbd_cache_max_dirty = 25165824
    rbd_cache_target_dirty = 16777216
  
  内核RBD:
    echo 4096 > /sys/module/rbd/parameters/single_major

PG优化:
  自动调整:
    ceph osd pool set <pool> pg_autoscale_mode on
  
  手动调整:
    ceph osd pool set <pool> pg_num 256
    ceph osd pool set <pool> pgp_num 256

SSD优化:
  # 调度器
  echo none > /sys/block/sdb/queue/scheduler
  
  # 关闭机械盘优化
  echo 0 > /sys/block/sdb/queue/rotational
  
  # 队列深度
  echo 1024 > /sys/block/sdb/queue/nr_requests

性能测试:
  RADOS Bench:
    # 写测试
    rados bench -p rbd 10 write --no-cleanup
    
    # 顺序读
    rados bench -p rbd 10 seq
    
    # 随机读
    rados bench -p rbd 10 rand
  
  RBD Bench:
    rbd bench --io-type write rbd/image1 --io-size 4096 --io-threads 16 --io-total 10G
  
  FIO:
    fio --name=rbd-test --ioengine=rbd --pool=rbd --rbdname=fio-test --rw=randwrite --bs=4k --size=10G --runtime=60 --time_based
```

---

## 监控与运维

```yaml
集群监控:
  Dashboard:
    URL: https://<mon-ip>:8443
    功能:
      - 集群状态
      - 性能图表
      - OSD管理
      - 池管理
      - RBD/CephFS管理
  
  Prometheus:
    启用:
      ceph mgr module enable prometheus
      ceph mgr module enable alerts
    
    Endpoint: http://<mgr-ip>:9283/metrics
  
  命令行监控:
    实时状态:
      ceph -w
    
    集群状态:
      ceph -s
      ceph health detail
    
    OSD状态:
      ceph osd stat
      ceph osd tree
      ceph osd df
    
    性能:
      ceph osd perf
      ceph osd pool stats

日志管理:
  查看日志:
    # Cephadm容器日志
    cephadm logs --name <daemon>
    
    # 示例
    cephadm logs --name osd.0
    cephadm logs --name mon.node1
  
  调整日志级别:
    ceph tell osd.* config set debug_osd 10/10
    ceph tell mon.* config set debug_mon 10/10

容量管理:
  扩容:
    添加OSD:
      ceph orch daemon add osd node4:/dev/sdb
    
    添加节点:
      ceph orch host add node4 192.168.30.14
  
  缩容:
    移除OSD:
      ceph orch osd rm <osd-id>
      # 等待数据迁移
      ceph osd purge <osd-id> --yes-i-really-mean-it
    
    移除节点:
      ceph orch host drain node4
      ceph orch host rm node4

备份策略:
  配置备份:
    ceph config-key dump > ceph-config-backup.json
    ceph osd getcrushmap -o crushmap-backup
  
  数据备份:
    RBD: rbd export <pool>/<image> <file>
    CephFS: rsync/tar备份
    RGW: s3cmd sync

升级:
  cephadm方式:
    # 检查更新
    ceph orch upgrade check <version>
    
    # 开始升级
    ceph orch upgrade start --image <image>
    
    # 监控升级
    ceph orch upgrade status
```

---

## 故障排查

```yaml
常见问题:
  问题1: OSD Down
    现象:
      ceph -s显示OSD down
    
    排查:
      1. 检查OSD进程
         systemctl status ceph-osd@<id>
      
      2. 查看OSD日志
         cephadm logs --name osd.<id>
      
      3. 检查磁盘健康
         smartctl -a /dev/sdX
      
      4. 检查网络
         ping <osd-host>
    
    解决:
      - 重启OSD: systemctl restart ceph-osd@<id>
      - 更换故障磁盘
      - 修复网络
  
  问题2: PG Inactive
    现象:
      ceph -s显示PG not active+clean
    
    排查:
      ceph pg dump | grep -v active+clean
      ceph pg <pg-id> query
    
    解决:
      - 等待PG恢复
      - 检查OSD状态
      - 重启相关OSD
  
  问题3: MON Quorum Lost
    现象:
      无法连接集群
    
    排查:
      ceph mon stat
      ceph quorum_status --format json-pretty
    
    解决:
      - 恢复多数MON
      - 紧急: 提取并重建MON
  
  问题4: 性能差
    现象:
      IOPS低, 延迟高
    
    排查:
      1. 检查PG分布
         ceph pg dump_stuck
      
      2. 检查OSD负载
         ceph osd perf
      
      3. 检查网络
         iperf3测试
      
      4. 检查磁盘
         iostat -x 1
    
    解决:
      - 调整PG数量
      - 平衡数据分布
      - 升级网络
      - 更换慢盘
  
  问题5: 容量不平衡
    现象:
      部分OSD使用率高
    
    排查:
      ceph osd df tree
    
    解决:
      # 调整权重
      ceph osd reweight <osd-id> 0.95
      
      # 或使用自动平衡
      ceph balancer on
      ceph balancer mode upmap

诊断命令:
  集群健康:
    ceph health detail
    ceph -s
  
  PG状态:
    ceph pg stat
    ceph pg dump_stuck
    ceph pg <pg-id> query
  
  OSD诊断:
    ceph osd tree
    ceph osd df
    ceph tell osd.* version
  
  日志:
    cephadm logs --name <daemon>
    journalctl -u ceph-osd@<id>

紧急恢复:
  OSD丢失 (少于min_size):
    # 临时降低min_size
    ceph osd pool set <pool> min_size 1
    
    # 恢复数据后改回
    ceph osd pool set <pool> min_size 2
  
  MON数据损坏:
    # 从健康MON提取
    ceph-mon --extract-monmap <file>
    
    # 重建MON
    ceph-mon --mkfs -i <new-mon> --monmap <file>
```

---

## 相关文档

- [存储类型与选型标准](01_存储类型与选型标准.md)
- [iSCSI配置与优化](02_iSCSI配置与优化.md)
- [NFS配置与优化](03_NFS配置与优化.md)
- [VMware vSAN配置](04_VMware_vSAN配置.md)
- [存储性能优化](06_存储性能优化.md)
- [存储容灾与备份](07_存储容灾与备份.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v3.0  
**状态**: ✅ 生产就绪
