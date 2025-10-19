# VMware vSAN配置与管理

> **返回**: [存储架构目录](README.md) | [虚拟化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [VMware vSAN配置与管理](#vmware-vsan配置与管理)
  - [📋 目录](#-目录)
  - [vSAN概述](#vsan概述)
  - [vSAN架构与组件](#vsan架构与组件)
  - [vSAN硬件要求](#vsan硬件要求)
  - [vSAN网络配置](#vsan网络配置)
  - [vSAN集群部署](#vsan集群部署)
  - [存储策略配置](#存储策略配置)
  - [vSAN性能优化](#vsan性能优化)
  - [vSAN监控与维护](#vsan监控与维护)
  - [故障排查](#故障排查)
  - [相关文档](#相关文档)

---

## vSAN概述

```yaml
VMware vSAN简介:
  定义:
    软件定义存储 (SDS)
    超融合基础架构 (HCI)核心组件
    虚拟化本地存储，聚合为共享存储池
  
  核心特点:
    ✅ 分布式存储架构
    ✅ 策略驱动管理
    ✅ 无需外部SAN/NAS
    ✅ 与vSphere深度集成
    ✅ 线性扩展性能
    ✅ 数据弹性（冗余）
  
  架构类型:
    原始vSAN (vSAN Original):
      存储类型: 混合或全闪存
      架构: 基于主机本地磁盘
      适用: 通用工作负载
    
    vSAN HCI网格 (vSAN HCI Mesh):
      功能: 跨集群共享vSAN存储
      版本: vSphere 8.0+
      用途: 资源池化
    
    vSAN Express Storage Architecture (ESA):
      版本: vSAN 8.0+
      特点: 全新架构，性能提升2-3倍
      要求: 全NVMe
  
  版本对比:
    vSAN Standard:
      - 基础功能
      - 混合/全闪存
      - RAID-1, RAID-5, RAID-6
    
    vSAN Advanced:
      + 重复数据删除和压缩
      + 纠删码 (RAID-5/6)
      + 加密
    
    vSAN Enterprise:
      + 延伸集群
      + iSCSI目标服务
      + 文件服务
    
    vSAN Enterprise Plus (ESA):
      + Express Storage Architecture
      + 更高性能
      + 简化管理

  适用场景:
    ✅ 虚拟桌面基础架构 (VDI)
    ✅ 通用虚拟化工作负载
    ✅ 数据库和应用服务器
    ✅ 远程办公/分支机构 (ROBO)
    ✅ 边缘计算
    ✅ Kubernetes持久卷
  
  不适用场景:
    ⚠️ 极高IOPS需求 (>500K)
    ⚠️ 极低延迟要求 (<0.1ms)
    ⚠️ 预算极度有限 (硬件成本较高)

  优势:
    ✅ 简化架构，无需外部存储
    ✅ 降低TCO (总拥有成本)
    ✅ 线性扩展 (横向扩展)
    ✅ 策略驱动自动化
    ✅ 与vSphere原生集成
    ✅ 支持混合云 (VMware Cloud)
  
  劣势:
    ❌ 硬件要求严格 (HCL)
    ❌ 初期投入较高
    ❌ 学习曲线
    ❌ 许可证成本
```

---

## vSAN架构与组件

```yaml
vSAN存储架构:
  磁盘组 (Disk Group):
    定义: 1个缓存盘 + 1-7个容量盘
    缓存盘 (Cache Tier):
      类型: SSD或NVMe
      用途: 读缓存 + 写缓冲
      大小: 建议容量盘总容量的10%
      数量: 每主机1-5个磁盘组
    
    容量盘 (Capacity Tier):
      混合架构:
        类型: HDD机械硬盘
        用途: 数据持久化
        最小: 1个/磁盘组
        最大: 7个/磁盘组
      
      全闪存架构:
        类型: SSD
        用途: 数据持久化
        最小: 1个/磁盘组
        最大: 7个/磁盘组
      
      vSAN ESA (8.0+):
        类型: 仅NVMe
        架构: 单层存储池
        无磁盘组概念
  
  存储对象:
    虚拟机磁盘 (VMDK)
    虚拟机快照
    虚拟机交换文件
    命名空间 (Kubernetes)
  
  容错方法 (FTT - Failures To Tolerate):
    RAID-1 (镜像):
      FTT=1: 2副本，容忍1个故障
      FTT=2: 3副本，容忍2个故障
      FTT=3: 4副本，容忍3个故障
      空间效率: 50% (FTT=1)
      性能: 写2x, 读1x
      最少主机: FTT+1
    
    RAID-5 (纠删码):
      FTT=1: 1副本+奇偶校验
      空间效率: 75% (4+1)
      性能: 优于RAID-1
      最少主机: 4
      要求: 全闪存 + Advanced许可
    
    RAID-6 (双重奇偶校验):
      FTT=2: 1副本+双奇偶
      空间效率: 67% (4+2)
      性能: 优于RAID-1
      最少主机: 6
      要求: 全闪存 + Advanced许可

  见证主机 (Witness):
    用途: 延伸集群/2节点vSAN
    作用: 仲裁，防止脑裂
    配置: 轻量级虚拟设备
    要求: 不存储用户数据
  
  vSAN集群最小配置:
    标准集群:
      最少主机: 3台
      每主机最少: 1个缓存盘 + 1个容量盘
      网络: 10GbE (最低1GbE)
    
    2节点vSAN:
      主机: 2台 + 1台见证主机
      用途: ROBO, 小型站点
      限制: 仅RAID-1
    
    单节点vSAN:
      主机: 1台
      用途: 边缘, 开发测试
      限制: 无容错

vSAN网络架构:
  VMkernel网络:
    类型: VMkernel (vmk)
    用途: vSAN数据传输
    要求: 专用VMkernel端口
    IP: 独立IP地址
    VLAN: 建议专用VLAN
  
  网络拓扑:
    单网络 (Single NIC):
      配置: 1x 10GbE
      适用: 小型环境
      风险: 单点故障
    
    冗余网络 (推荐):
      配置: 2x 10GbE (主备或负载均衡)
      容错: ✅
      性能: ✅ (LACP或多路径)
    
    专用网络 (最佳):
      管理网络: 1GbE VLAN 10
      vSAN网络: 10/25GbE VLAN 20
      vMotion网络: 10GbE VLAN 30
      VM网络: 10GbE VLAN 40
```

---

## vSAN硬件要求

```yaml
vSAN Ready Node认证:
  定义:
    厂商预配置的vSAN认证服务器
    硬件组合已通过VMware测试
  
  主流厂商:
    ✅ Dell EMC VxRail (深度集成)
    ✅ HPE SimpliVity
    ✅ Cisco HyperFlex
    ✅ 联想ThinkAgile VX
    ✅ 浪潮InCloudRail
    ✅ 华为FusionCube
  
  查询HCL:
    URL: https://www.vmware.com/resources/compatibility/search.php?deviceCategory=vsan
    筛选: 服务器型号、控制器、磁盘

服务器配置要求:
  CPU:
    最低: 2个CPU核心
    推荐: 8-16核/CPU
    型号: Intel Xeon或AMD EPYC
  
  内存:
    最低: 16GB
    推荐: 每TB vSAN容量 32GB+
    计算: 基础12GB + 容量盘开销
    示例:
      - 10TB容量 = 32GB RAM
      - 50TB容量 = 64GB RAM
      - 100TB容量 = 128GB RAM
  
  网络:
    最低: 1GbE (仅测试)
    推荐: 10GbE
    高性能: 25GbE
    最佳: 2x 25GbE (冗余)
  
  存储控制器:
    要求:
      - 直通模式 (Pass-through/HBA)
      - 或RAID-0逐盘配置
      - vSAN管理磁盘，不使用RAID
    
    推荐型号:
      ✅ LSI 9300/9400系列 (HBA)
      ✅ Dell PERC H730P/H740P (RAID-0模式)
      ✅ HPE Smart Array (HBA模式)
    
    不推荐:
      ❌ 软RAID
      ❌ 不支持直通的RAID控制器

磁盘配置:
  混合架构 (Hybrid):
    缓存层:
      类型: SSD
      容量: 600GB-1.6TB
      用途: 70%读缓存 + 30%写缓冲
      接口: SATA/SAS
      数量: 1-5个/主机
    
    容量层:
      类型: HDD
      容量: 4TB-12TB
      接口: SATA/SAS, 7.2K或10K RPM
      数量: 1-7个/磁盘组
    
    配置示例:
      小型 (3主机):
        每主机: 1x 480GB SSD + 4x 4TB HDD
        总容量: ~48TB原始 (~24TB可用, FTT=1)
      
      中型 (4主机):
        每主机: 2x 800GB SSD + 8x 8TB HDD
        总容量: ~256TB原始 (~192TB可用, RAID-5)
  
  全闪存架构 (All-Flash):
    缓存层:
      类型: NVMe SSD或高性能SAS SSD
      容量: 800GB-1.6TB
      写入耐久性: 高 (3+ DWPD)
      数量: 1-5个/主机
    
    容量层:
      类型: SSD
      容量: 1.92TB-7.68TB
      写入耐久性: 中等 (1-3 DWPD)
      接口: SATA/SAS/NVMe
      数量: 1-7个/磁盘组
    
    配置示例:
      高性能 (4主机):
        每主机: 2x 800GB NVMe (缓存) + 6x 3.84TB SSD (容量)
        总容量: ~92TB原始 (~69TB可用, RAID-5)
      
      超高性能 (6主机):
        每主机: 2x 1.6TB NVMe (缓存) + 8x 7.68TB NVMe (容量)
        总容量: ~368TB原始 (~307TB可用, RAID-6)
  
  vSAN ESA (8.0+, 全NVMe):
    存储池:
      类型: 仅NVMe
      容量: 1.92TB-15.36TB
      数量: 无限制
      架构: 单层，无缓存/容量区分
    
    配置示例:
      ESA集群 (4主机):
        每主机: 8x 7.68TB NVMe
        总容量: ~245TB原始 (~184TB可用, RAID-5)
        性能: IOPS > 1M

容量规划:
  原始容量计算:
    容量盘总容量 = 主机数 × 每主机容量盘容量
  
  可用容量计算:
    RAID-1 (FTT=1):
      可用容量 = 原始容量 × 0.5 × 0.7
      # 0.5=镜像开销, 0.7=预留30%空间
    
    RAID-5 (FTT=1):
      可用容量 = 原始容量 × 0.75 × 0.7
    
    RAID-6 (FTT=2):
      可用容量 = 原始容量 × 0.67 × 0.7
  
  示例:
    4主机, 每主机8x 4TB HDD, RAID-5:
      原始: 4 × 8 × 4TB = 128TB
      可用: 128TB × 0.75 × 0.7 ≈ 67TB
```

---

## vSAN网络配置

```yaml
VMkernel端口配置:
  创建vSAN VMkernel:
    步骤1: 创建分布式交换机 (推荐)
      1. vCenter → 网络 → 新建分布式交换机
      2. 名称: vDS-vSAN
      3. 版本: 7.0或8.0
      4. 上行链路数: 2 (冗余)
    
    步骤2: 创建端口组
      1. vDS-vSAN → 新建分布式端口组
      2. 名称: vSAN-PG
      3. VLAN: 20 (专用VLAN)
      4. 负载均衡: 基于源虚拟端口
    
    步骤3: 添加主机上行链路
      1. vDS-vSAN → 添加和管理主机
      2. 选择ESXi主机
      3. 分配物理适配器: vmnic2, vmnic3
    
    步骤4: 创建VMkernel适配器
      1. 主机 → 配置 → VMkernel适配器
      2. 添加网络 → VMkernel网络适配器
      3. 分布式端口组: vSAN-PG
      4. IPv4: 192.168.20.101
      5. 子网: 255.255.255.0
      6. 服务: ✅ vSAN
      7. 完成
    
    步骤5: 验证
      esxcli vsan network list
      # 应显示vmk接口启用vSAN

  IP地址规划:
    示例 (4主机):
      ESXi-01: vmk1 = 192.168.20.101
      ESXi-02: vmk1 = 192.168.20.102
      ESXi-03: vmk1 = 192.168.20.103
      ESXi-04: vmk1 = 192.168.20.104
    
    要求:
      - 同一子网
      - 低延迟 (<1ms)
      - 大带宽 (10GbE+)
      - 无路由跳跃

网络冗余配置:
  主备模式 (Active-Standby):
    配置:
      vmnic2: Active
      vmnic3: Standby
    
    优点: 简单
    缺点: 未利用全部带宽
  
  负载均衡 (Active-Active):
    方法1: 基于源虚拟端口
      配置: vDS负载均衡策略
      效果: 不同对象走不同上行链路
      推荐: ✅
    
    方法2: 基于IP哈希 (需LACP)
      配置: 交换机LACP + vDS LACP
      效果: 单对象可用多链路
      性能: 最佳
      复杂度: 高

  配置示例 (LACP):
    交换机端 (Cisco):
      interface Port-channel10
        description vSAN-LACP
        switchport mode trunk
        switchport trunk allowed vlan 20
      
      interface range GigabitEthernet1/0/1-2
        description ESXi-01-vSAN
        channel-group 10 mode active
        switchport mode trunk
        switchport trunk allowed vlan 20
    
    vDS端:
      1. vDS → LACP → 新建
      2. 名称: vSAN-LAG
      3. 模式: Active
      4. 上行链路数: 2
      5. 负载均衡: 基于IP哈希
      6. 分配物理NIC: vmnic2, vmnic3

Jumbo Frame配置:
  优势:
    ✅ 减少CPU开销
    ✅ 提升吞吐量 10-20%
    ✅ 降低延迟
  
  配置MTU 9000:
    vDS:
      1. vDS → 设置 → 高级 → MTU
      2. 设置: 9000
    
    VMkernel:
      esxcli network ip interface set -i vmk1 -m 9000
    
    物理交换机:
      interface range GigabitEthernet1/0/1-8
        mtu 9216  # 交换机通常需要9216
  
  验证:
    # 从ESXi主机测试
    vmkping ++netstack=vsan -d -s 8972 192.168.20.102
    # 8972 = 9000 - 28 (IP+ICMP)
    # 应显示: 0% packet loss

流量整形 (可选):
  vSAN流量QoS:
    vDS端口组:
      1. vSAN-PG → 编辑设置
      2. 流量整形 → 启用
      3. 平均带宽: 8,000,000 Kbps (1GbE)
      4. 峰值带宽: 10,000,000 Kbps
      5. 突发大小: 102,400 KB
```

---

## vSAN集群部署

```yaml
部署前检查清单:
  硬件:
    ✅ 所有服务器在VMware HCL中
    ✅ 控制器配置为直通模式
    ✅ 磁盘已安装并识别
    ✅ 网络适配器正常
  
  网络:
    ✅ vSAN VMkernel端口已创建
    ✅ IP地址已分配
    ✅ VLAN配置正确
    ✅ Jumbo Frame已启用 (可选)
    ✅ 网络连通性测试通过
  
  软件:
    ✅ ESXi版本一致
    ✅ vCenter已部署
    ✅ vSAN许可证已准备
    ✅ 时间同步 (NTP)

启用vSAN集群 (Web界面):
  步骤1: 创建集群
    1. vCenter → 清单 → 数据中心
    2. 右键 → 新建集群
    3. 名称: Cluster-vSAN
    4. vSAN: ✅ 开启vSAN
    5. 不要勾选 "单主机" (标准集群)
  
  步骤2: 添加主机
    1. Cluster-vSAN → 添加主机
    2. 选择ESXi主机: 192.168.1.101-104
    3. 验证主机兼容性
    4. 添加
  
  步骤3: 配置vSAN
    1. Cluster-vSAN → 配置 → vSAN → 服务
    2. 磁盘管理: 手动
    3. 重复数据删除和压缩: 启用 (全闪存+Advanced许可)
    4. 加密: 启用 (可选)
  
  步骤4: 声明磁盘
    1. 配置 → vSAN → 磁盘管理
    2. 每台主机:
       a. 声明未使用的磁盘
       b. 选择缓存盘: SSD/NVMe
       c. 选择容量盘: HDD/SSD
       d. 创建磁盘组
    
    示例 (每主机):
      磁盘组1:
        缓存: 1x 800GB NVMe
        容量: 4x 3.84TB SSD
  
  步骤5: 验证vSAN
    1. 配置 → vSAN → 健康检查
    2. 运行所有测试
    3. 确保全绿
  
  步骤6: 查看容量
    1. 监控 → vSAN → 容量
    2. 查看可用容量

使用PowerCLI部署:
  脚本示例:
    # PowerCLI脚本 - 启用vSAN集群
    
    # 连接vCenter
    Connect-VIServer -Server vcenter.example.com -User administrator@vsphere.local -Password 'P@ssw0rd'
    
    # 创建集群并启用vSAN
    $cluster = New-Cluster -Name "Cluster-vSAN" -Location (Get-Datacenter "DC01")
    Set-Cluster -Cluster $cluster -VsanEnabled:$true -Confirm:$false
    
    # 添加主机到集群
    Add-VMHost -Name "192.168.1.101" -Location $cluster -User root -Password 'ESXiP@ss' -Force
    Add-VMHost -Name "192.168.1.102" -Location $cluster -User root -Password 'ESXiP@ss' -Force
    Add-VMHost -Name "192.168.1.103" -Location $cluster -User root -Password 'ESXiP@ss' -Force
    Add-VMHost -Name "192.168.1.104" -Location $cluster -User root -Password 'ESXiP@ss' -Force
    
    # 声明磁盘 (自动模式)
    Get-Cluster $cluster | Set-VsanClusterConfiguration -VsanDiskClaimMode Automatic
    
    # 启用重复数据删除和压缩 (全闪存)
    Get-VsanClusterConfiguration -Cluster $cluster | Set-VsanClusterConfiguration -SpaceEfficiencyEnabled $true
    
    # 验证vSAN
    Test-VsanClusterHealth -Cluster $cluster

CLI部署 (esxcli):
  在每台ESXi主机上:
    # 1. 查看可用磁盘
    esxcli storage core device list
    
    # 2. 创建磁盘组
    esxcli vsan storage add -d naa.xxx (容量盘) -s naa.yyy (缓存盘)
    
    # 3. 验证磁盘组
    esxcli vsan storage list
    
    # 4. 查看vSAN集群状态
    esxcli vsan cluster get
```

---

## 存储策略配置

```yaml
存储策略概述:
  定义:
    基于策略的管理 (SPBM)
    定义VM存储需求
    vSAN自动应用策略
  
  核心参数:
    容错方法 (FTM):
      RAID-1 (镜像)
      RAID-5 (纠删码)
      RAID-6 (双重奇偶)
    
    容错级别 (FTT):
      0: 无容错 (单节点vSAN)
      1: 容忍1个故障
      2: 容忍2个故障
      3: 容忍3个故障
    
    磁盘条带数 (SFTT):
      1-12条带
      提升性能
      增加容量开销
    
    对象空间预留:
      0%: 精简置备
      100%: 厚置备
      默认: 0%
    
    闪存读缓存预留:
      0-100%
      保证缓存配额

默认存储策略:
  vSAN Default Storage Policy:
    容错方法: RAID-1
    FTT: 1
    磁盘条带: 1
    对象空间预留: 0%
    适用: 通用工作负载

创建自定义策略:
  步骤 (Web界面):
    1. 菜单 → 策略和配置文件 → VM存储策略
    2. 创建
    3. 名称: vSAN-Critical
    4. 规则:
       - 站点灾难容错: 无
       - 容错方法: RAID-1
       - 容错级别: 2 (3副本)
       - 磁盘条带数: 2
       - 对象空间预留: 50%
       - 闪存读缓存: 100%
    5. 保存
  
  应用策略:
    新虚拟机:
      创建VM → 自定义 → 选择存储策略: vSAN-Critical
    
    现有虚拟机:
      VM → 编辑设置 → VM选项 → VM存储策略: vSAN-Critical

策略示例:
  关键业务 (数据库):
    名称: vSAN-Database
    容错方法: RAID-1
    FTT: 2
    磁盘条带: 4
    对象空间预留: 100%
    闪存读缓存: 100%
    用途: SQL Server, Oracle
  
  高性能 (全闪存+RAID-5):
    名称: vSAN-Performance
    容错方法: RAID-5
    FTT: 1
    磁盘条带: 4
    对象空间预留: 0%
    用途: Web服务器, 应用服务器
  
  大容量 (RAID-6):
    名称: vSAN-Capacity
    容错方法: RAID-6
    FTT: 2
    磁盘条带: 1
    对象空间预留: 0%
    用途: 归档, 备份
  
  开发测试:
    名称: vSAN-Dev
    容错方法: RAID-1
    FTT: 1
    磁盘条带: 1
    对象空间预留: 0%
    用途: 开发, 测试环境

策略变更:
  修改现有VM策略:
    影响: vSAN自动重新平衡对象
    时间: 取决于数据量
    建议: 维护窗口执行
  
  PowerCLI示例:
    # 批量应用策略
    Get-VM -Location "Cluster-vSAN" | Where {$_.Name -like "DB-*"} | Set-SpbmEntityConfiguration -StoragePolicy "vSAN-Database"
```

---

## vSAN性能优化

```yaml
硬件优化:
  磁盘性能:
    缓存层:
      优先: NVMe > SAS SSD > SATA SSD
      建议: 企业级SSD, 高DWPD
    
    容量层:
      全闪存: SSD
      混合: 10K RPM HDD优于7.2K
    
    控制器:
      队列深度: 越高越好
      缓存: 不依赖RAID缓存
  
  网络性能:
    带宽:
      最低: 10GbE
      推荐: 25GbE
      高性能: 2x 25GbE (50GbE聚合)
    
    延迟:
      目标: <1ms (同机架)
      检测: vmkping ++netstack=vsan
    
    Jumbo Frame:
      MTU: 9000
      提升: 10-20%

配置优化:
  存储策略优化:
    磁盘条带数:
      默认: 1
      大文件顺序I/O: 增加到4-8
      注意: 增加容量开销
    
    对象空间预留:
      精简: 0% (默认)
      厚置备: 100% (性能最佳)
      折中: 50%
  
  读缓存预留:
    默认: 0% (按需)
    关键VM: 100% (保证缓存)
  
  重复数据删除和压缩:
    适用: 全闪存
    效果: 节省50-70%容量
    开销: 10-15% CPU和内存
    建议: VDI, 虚拟服务器

  ESXi高级选项:
    VSAN.ClomRepairDelay: 60分钟
      说明: 主机离线后重建延迟
      默认: 60
      建议: 维护时增加到120-180
    
    VSAN.DomOwnerForceWarmCache: 1
      说明: 强制DOM所有者热缓存
      提升: 缓存命中率
    
    VSAN.ObjectScrubsPerYear: 1
      说明: 年度对象校验次数
      用途: 数据完整性

  vSAN resync throttle:
    限制重建带宽，避免影响业务
    配置: 集群 → 配置 → vSAN → 常规
    设置: 重新同步流量限制 = 40-60 IOPS

监控与调优:
  性能指标:
    延迟:
      优秀: <5ms
      良好: 5-10ms
      警告: >10ms
    
    IOPS:
      混合vSAN: 5K-20K
      全闪存: 50K-200K+
    
    吞吐量:
      混合: 500MB/s-2GB/s
      全闪存: 2GB/s-10GB/s+
  
  监控工具:
    vCenter性能图表:
      vSAN → 性能 → 后端
      指标: 延迟, IOPS, 吞吐量
    
    vSAN观察器 (vSAN Observer):
      实时性能监控
      采样: 60秒-24小时
      用途: 性能分析
    
    esxtop:
      命令: esxtop → v (vSAN视图)
      指标: GAVG, DAVG, 队列深度
```

---

## vSAN监控与维护

```yaml
健康检查:
  vSAN Health Service:
    访问: 集群 → 监控 → vSAN → 健康
    类别:
      ✅ 硬件兼容性
      ✅ 网络连通性
      ✅ 物理磁盘健康
      ✅ 限制与配置
      ✅ 存储策略
      ✅ 集群性能
    
    频率: 每日检查
    警报: 配置自动告警

  关键健康项:
    ✅ 所有主机已连接
    ✅ 网络延迟 <1ms
    ✅ 磁盘健康正常
    ✅ 存储策略合规
    ✅ 容量预警阈值 >20%
    ✅ 对象无重建

容量管理:
  监控容量:
    位置: 监控 → vSAN → 容量
    指标:
      - 总容量
      - 已用容量
      - 可用容量
      - Slack空间 (30%预留)
  
  容量阈值:
    80%: 警告，计划扩容
    85%: 严重，立即扩容
    90%: 紧急，性能下降
  
  扩容方法:
    横向扩展 (Scale-Out):
      添加新主机
      优点: 增加容量+性能
      成本: 高
    
    纵向扩展 (Scale-Up):
      向现有主机添加磁盘
      优点: 成本低
      限制: 最多7容量盘/磁盘组

日常维护:
  固件更新:
    顺序:
      1. 更新存储控制器固件
      2. 更新磁盘固件
      3. 重启主机
    
    注意: 进入维护模式前确保vSAN健康
  
  磁盘更换:
    步骤:
      1. 识别故障磁盘
      2. 移除磁盘组 (如果缓存盘故障)
      3. 等待数据重建完成
      4. 物理更换磁盘
      5. 重新声明磁盘
  
  主机维护:
    维护模式选项:
      确保可访问性:
        vSAN迁移数据到其他主机
        时间长
        推荐: 计划维护
      
      快速模式:
        不迁移数据
        主机离线后60分钟开始重建
        推荐: 快速重启
      
      无数据迁移:
        不迁移，不重建
        用途: 紧急维护

备份策略:
  VM级备份:
    工具:
      ✅ Veeam Backup & Replication
      ✅ VMware vSphere Data Protection
      ✅ Commvault
      ✅ Dell EMC Avamar
    
    备份目标: 外部存储 (NFS/iSCSI)
  
  配置备份:
    vCenter配置备份:
      计划: 每日
      保留: 7天
    
    vSAN配置导出:
      PowerCLI:
        Get-VsanClusterConfiguration -Cluster "Cluster-vSAN" | Export-Clixml "vsan-config.xml"
```

---

## 故障排查

```yaml
常见问题:
  问题1: vSAN数据存储未显示
    原因:
      - vSAN未启用
      - 磁盘组未创建
      - 网络故障
    
    排查:
      1. 检查vSAN是否启用
      2. 验证磁盘组: esxcli vsan storage list
      3. 测试vSAN网络: vmkping ++netstack=vsan
      4. 查看vSAN健康检查
  
  问题2: 性能差 (延迟高)
    原因:
      - 网络延迟
      - 磁盘性能瓶颈
      - 容量不足 (<20%)
      - 重建活动
    
    排查:
      1. 检查网络延迟: vmkping
      2. 查看磁盘IOPS: esxtop → d
      3. 查看vSAN容量
      4. 检查重建任务: vSAN → 重新同步对象
    
    解决:
      - 升级网络到25GbE
      - 更换更快磁盘
      - 扩容vSAN
      - 限制重建速率
  
  问题3: 对象不合规
    原因:
      - 主机数量不足
      - 容量不足
      - 存储策略无法满足
    
    排查:
      1. 监控 → vSAN → 虚拟对象
      2. 查看不合规对象
      3. 检查存储策略
    
    解决:
      - 添加主机
      - 扩容
      - 调整存储策略 (降低FTT)
  
  问题4: 磁盘故障
    症状:
      - vSAN健康检查警告
      - 磁盘离线
    
    处理:
      1. 确认故障磁盘: 配置 → vSAN → 磁盘管理
      2. 移除磁盘组 (如果缓存盘故障)
      3. 等待重建完成
      4. 更换物理磁盘
      5. 重新添加磁盘
  
  问题5: 网络分区 (Network Partition)
    症状:
      - vSAN健康检查错误
      - VM无法访问存储
    
    原因:
      - 交换机故障
      - 网络配置错误
      - VLAN配置
    
    排查:
      1. 测试主机间连通性
      2. 检查交换机日志
      3. 验证VLAN配置
      4. 检查物理链路
  
  问题6: 主机离线后数据重建
    现象:
      主机维护后返回，vSAN自动重建数据
    
    原因:
      超过ClomRepairDelay时间 (默认60分钟)
    
    避免:
      1. 维护前增加延迟:
         esxcli system settings advanced set -o /VSAN/ClomRepairDelay -i 180
      
      2. 使用快速维护模式
      
      3. 维护窗口内完成

日志位置:
  ESXi主机:
    /var/log/vmkernel.log: vSAN核心日志
    /var/log/vmware.log: 虚拟机日志
  
  vCenter:
    /var/log/vmware/vpxd/: vCenter日志
  
  查看vSAN日志:
    tail -f /var/log/vmkernel.log | grep -i vsan

诊断命令:
  # vSAN集群信息
  esxcli vsan cluster get
  
  # 磁盘组列表
  esxcli vsan storage list
  
  # vSAN网络配置
  esxcli vsan network list
  
  # vSAN健康检查 (CLI)
  esxcli vsan health cluster list
  
  # vSAN对象列表
  esxcli vsan debug object list
  
  # vSAN性能统计
  vsantop
  
  # 查看vSAN版本
  esxcli software vib list | grep vsan
```

---

## 相关文档

- [存储类型与选型标准](01_存储类型与选型标准.md)
- [iSCSI配置与优化](02_iSCSI配置与优化.md)
- [NFS配置与优化](03_NFS配置与优化.md)
- [Ceph分布式存储](05_Ceph分布式存储.md)
- [存储性能优化](06_存储性能优化.md)
- [存储容灾与备份](07_存储容灾与备份.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v3.0  
**状态**: ✅ 生产就绪
