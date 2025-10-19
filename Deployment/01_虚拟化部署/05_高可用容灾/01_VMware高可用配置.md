# VMware高可用配置

> **返回**: [高可用容灾目录](README.md) | [虚拟化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [VMware高可用配置](#vmware高可用配置)
  - [📋 目录](#-目录)
  - [1. VMware HA概述](#1-vmware-ha概述)
  - [2. VMware HA配置](#2-vmware-ha配置)
    - [2.1 启用HA集群](#21-启用ha集群)
    - [2.2 PowerCLI配置HA](#22-powercli配置ha)
    - [2.3 HA准入控制详细配置](#23-ha准入控制详细配置)
  - [3. VMware Fault Tolerance (FT)](#3-vmware-fault-tolerance-ft)
    - [3.1 启用FT](#31-启用ft)
    - [3.2 FT测试](#32-ft测试)
  - [4. VMware DRS配置](#4-vmware-drs配置)
    - [4.1 配置DRS](#41-配置drs)
  - [5. vMotion与Storage vMotion](#5-vmotion与storage-vmotion)
    - [5.1 配置vMotion网络](#51-配置vmotion网络)
    - [5.2 执行vMotion](#52-执行vmotion)
  - [6. 高可用网络配置](#6-高可用网络配置)
  - [7. 监控与故障排查](#7-监控与故障排查)
    - [7.1 HA监控](#71-ha监控)
    - [7.2 常见问题排查](#72-常见问题排查)
  - [8. 最佳实践](#8-最佳实践)
  - [相关文档](#相关文档)

---

## 1. VMware HA概述

```yaml
VMware_HA_Overview:
  全称: VMware High Availability
  功能: 自动重启失败主机上的虚拟机
  
  工作原理:
    1. 集群内ESXi主机互相监控心跳
    2. 检测到主机故障时
    3. 自动在其他主机上重启受影响的VM
    4. RTO: 通常2-5分钟
  
  关键组件:
    Master主机:
      - 集群中选举一台作为Master
      - 负责监控从主机和VM
      - 协调VM重启
    
    Slave从主机:
      - 向Master报告状态
      - 接收Master指令
      - 执行VM重启
    
    数据存储心跳:
      - 当网络心跳失败时
      - 通过共享存储交换心跳
      - 防止脑裂
  
  故障类型:
    主机故障:
      - 硬件故障
      - ESXi崩溃
      - 断电
      结果: VM在其他主机重启
    
    隔离响应:
      - 主机网络隔离
      - 无法访问管理网络
      策略: 关闭VM/保持开启/无操作
    
    分区情况:
      - 网络分区导致多个Master
      - 使用数据存储心跳仲裁
      结果: 少数派分区的VM被关闭

准入控制:
  目的: 确保有足够资源进行故障切换
  
  策略:
    主机故障集群容忍:
      - 定义可容忍的主机故障数
      - 预留对应资源
      - 推荐: 容忍1-2台主机故障
    
    百分比预留:
      - CPU/内存预留百分比
      - 灵活性更高
      - 推荐: 25%-50%
    
    专用故障切换主机:
      - 指定特定主机用于故障切换
      - 平时不运行VM
      - 适用: 关键业务场景

VM重启优先级:
  High (高):
    - 关键业务VM
    - 优先分配资源
    - 首先重启
  
  Medium (中):
    - 普通业务VM
    - 默认优先级
  
  Low (低):
    - 测试/开发VM
    - 最后重启
  
  Disabled (禁用):
    - 不自动重启
    - 手动干预
```

---

## 2. VMware HA配置

### 2.1 启用HA集群

```yaml
# ========================================
# 通过vSphere Client配置HA
# ========================================

步骤:
  1. 创建集群:
     - 导航到: Datacenter → 右键 → New Cluster
     - 名称: Production-Cluster
     - 勾选: "Turn ON vSphere HA"
  
  2. 配置HA选项:
     导航到: Cluster → Configure → vSphere Availability → Edit
     
     故障和响应:
       主机监控: 已启用 ✅
       主机失败响应: 重启虚拟机 ✅
       主机隔离响应: 关闭虚拟机电源并重启 ✅
       
       数据存储心跳:
         - 使用集群中的数据存储
         - 自动选择
         - 数量: 2-4个
     
     准入控制:
       策略: 主机故障集群容忍
       失败主机数量: 1
       性能降级: ✅ 允许VM开机
     
     心跳数据存储:
       - 自动选择
       - 确保至少2个数据存储
  
  3. 添加主机到集群:
     - 拖拽ESXi主机到集群
     - 或右键集群 → Add Hosts
  
  4. 验证:
     - Cluster → Monitor → vSphere HA
     - 状态: Protected (已保护)
     - Master主机: 已选举
```

### 2.2 PowerCLI配置HA

```powershell
# ========================================
# PowerCLI自动化配置HA
# ========================================

# 连接vCenter
Connect-VIServer -Server vcenter.example.com

# 创建集群并启用HA
$cluster = New-Cluster -Name "Production-Cluster" `
    -Location (Get-Datacenter "DC1") `
    -HAEnabled:$true `
    -HAAdmissionControlEnabled:$true

# 配置HA设置
Set-Cluster -Cluster $cluster `
    -HAIsolationResponse "PowerOff" `
    -HARestartPriority "Medium" `
    -HAFailoverLevel 1 `
    -Confirm:$false

# 配置高级选项
$cluster = Get-Cluster "Production-Cluster"

# 主机监控敏感度 (默认: 中等)
New-AdvancedSetting -Entity $cluster `
    -Name "das.failuredetectiontime" `
    -Value 15 `
    -Confirm:$false

# 心跳数据存储数量
New-AdvancedSetting -Entity $cluster `
    -Name "das.heartbeatDsPerHost" `
    -Value 3 `
    -Confirm:$false

# VM监控 (每30秒检查一次)
New-AdvancedSetting -Entity $cluster `
    -Name "das.vmmonitoring" `
    -Value "vmMonitoringOnly" `
    -Confirm:$false

# 添加主机到集群
Get-VMHost "esxi-01.example.com","esxi-02.example.com","esxi-03.example.com" | 
    Move-VMHost -Destination $cluster

# 配置VM重启优先级
Get-VM -Location $cluster | Where-Object {$_.Name -like "*prod*"} |
    Set-VM -HARestartPriority "High" -Confirm:$false

# 验证HA状态
Get-Cluster $cluster | Select Name, HAEnabled, HAFailoverLevel

# 查看Master主机
$haStatus = Get-View -ViewType ClusterComputeResource -Filter @{"Name"="Production-Cluster"}
$haStatus.ConfigurationEx.DasConfig.HBDatastoreCandidatePolicy
```

### 2.3 HA准入控制详细配置

```yaml
准入控制策略对比:

策略1: 主机故障集群容忍 (推荐):
  配置:
    失败主机数量: 1-2
    性能降级: 允许
  
  计算方式:
    可用槽位 = (总CPU槽位 - 预留CPU槽位) + (总内存槽位 - 预留内存槽位)
    CPU槽位大小 = 集群中最大VM的CPU预留
    内存槽位大小 = 集群中最大VM的内存预留 + VM开销
  
  适用场景:
    - VM资源需求相对均匀
    - 中小型集群 (3-10台主机)
  
  示例:
    5台主机集群, 容忍1台主机故障
    每台主机: 32 vCPU, 256GB RAM
    最大VM: 4 vCPU, 16GB RAM
    
    槽位大小: 4 vCPU, 16GB RAM
    每台主机槽位: 8个 (32/4) 或 16个 (256/16), 取较小值 = 8
    总槽位: 5 x 8 = 40
    预留: 1台主机 = 8槽位
    可用: 40 - 8 = 32槽位

策略2: 百分比预留:
  配置:
    CPU预留: 25%
    内存预留: 25%
  
  计算方式:
    预留CPU = 集群总CPU × 25%
    预留内存 = 集群总内存 × 25%
  
  适用场景:
    - VM资源需求差异大
    - 大型集群
    - 需要灵活性
  
  示例:
    5台主机, 每台32 vCPU, 256GB RAM
    总资源: 160 vCPU, 1280GB RAM
    25%预留: 40 vCPU, 320GB RAM
    可用: 120 vCPU, 960GB RAM

策略3: 专用故障切换主机:
  配置:
    指定1-2台主机作为故障切换主机
    这些主机平时空闲
  
  适用场景:
    - 关键业务
    - 需要快速故障切换
    - 资源充足
  
  示例:
    7台主机集群
    指定2台作为故障切换主机
    5台运行生产VM
    故障时VM迁移到2台故障切换主机
```

---

## 3. VMware Fault Tolerance (FT)

```yaml
FT_Overview:
  全称: Fault Tolerance
  功能: 零停机时间保护
  
  工作原理:
    - 创建VM的实时副本 (Secondary VM)
    - Primary和Secondary VM同步运行
    - Primary故障时，Secondary立即接管
    - RTO: 0秒 (无停机)
    - RPO: 0 (无数据丢失)
  
  要求:
    vSphere版本: 6.0+
    
    硬件:
      - CPU支持硬件虚拟化 (VT-x/AMD-V)
      - 主机至少2台
      - 共享存储
      - 10Gbps网络 (FT日志流量)
    
    VM限制:
      - vCPU: 最多8个 (vSphere 6.5+)
      - 内存: 最多128GB
      - 磁盘: 只能使用Thick Provisioned磁盘
      - 不支持快照
  
  网络要求:
    FT日志网络:
      - 专用10Gbps网络
      - 低延迟 (<5ms)
      - 高带宽
      - 推荐Jumbo Frame
```

### 3.1 启用FT

```yaml
# ========================================
# 通过vSphere Client启用FT
# ========================================

前提条件:
  1. VM满足FT要求
  2. 配置FT日志网络:
     每台ESXi主机:
       - VMkernel网卡标记"Fault Tolerance logging"
       - 10Gbps网络
       - 推荐VLAN隔离

步骤:
  1. 配置FT日志网络:
     ESXi → Configure → Networking → VMkernel adapters → Add
     
     设置:
       - 端口组: FT-Logging (VLAN 50)
       - IP: 192.168.50.x/24
       - 服务: ✅ Fault Tolerance logging
       - MTU: 9000 (Jumbo Frame)
  
  2. 启用FT:
     VM → 右键 → Fault Tolerance → Turn On Fault Tolerance
     
     向导:
       - Secondary VM主机: 选择另一台主机
       - Secondary VM数据存储: 选择共享存储
       - 网络: 选择FT日志网络
  
  3. 验证:
     VM → Summary
     状态: "Fault Tolerance: Protected"
     
     Primary VM: 在主机A
     Secondary VM: 在主机B (自动创建)

注意事项:
  - FT会消耗额外资源 (双倍CPU/内存)
  - 仅用于关键业务VM
  - 不能与DRS完全自动化同时使用
```

### 3.2 FT测试

```yaml
FT故障切换测试:
  测试1: 主机断电测试
    步骤:
      1. 记录Primary VM所在主机
      2. 断开该主机电源
      3. 观察Secondary VM立即接管
      4. 验证VM无中断
    
    预期结果:
      - Secondary VM成为新的Primary
      - 自动创建新的Secondary VM
      - 业务无感知
      - 故障切换时间: <1秒
  
  测试2: 网络隔离测试
    步骤:
      1. 禁用Primary VM主机的管理网络
      2. 观察FT切换
      3. 验证VM继续运行
    
    预期结果:
      - Secondary VM接管
      - 网络连接无中断
  
  测试3: FT日志网络故障
    步骤:
      1. 禁用FT日志网络
      2. 观察告警
      3. VM进入不受保护状态
    
    预期结果:
      - VM继续运行但不受FT保护
      - 生成告警
      - 修复网络后自动恢复FT
```

---

## 4. VMware DRS配置

```yaml
DRS_Overview:
  全称: Distributed Resource Scheduler
  功能: 自动负载均衡
  
  工作原理:
    - 监控集群资源使用情况
    - 使用vMotion迁移VM
    - 平衡主机负载
    - 优化资源利用率
  
  自动化级别:
    Manual (手动):
      - DRS提供建议
      - 管理员手动执行
      - 适用: 高度管控环境
    
    Partially Automated (部分自动):
      - VM初始放置自动
      - 迁移建议手动执行
      - 适用: 测试环境
    
    Fully Automated (完全自动) ✅:
      - 初始放置自动
      - 负载均衡自动
      - 推荐: 生产环境
  
  迁移阈值:
    Conservative (保守):
      - 优先级1建议
      - 最小化vMotion
      - 适用: 稳定优先
    
    Moderate (适中):
      - 优先级1-2建议
      - 平衡
      - 推荐: 默认设置
    
    Aggressive (激进):
      - 优先级1-3建议
      - 频繁vMotion
      - 适用: 性能优先

DRS亲和性规则:
  VM-VM亲和性:
    Keep VMs Together:
      - 强制VM在同一主机
      - 例: Web服务器和缓存服务器
    
    Separate VMs:
      - 强制VM在不同主机
      - 例: 主数据库和备份数据库
  
  VM-Host亲和性:
    Must run on:
      - VM必须在指定主机组
      - 例: 许可证限制
    
    Should run on:
      - VM优先在指定主机组
      - 软规则, 可违反
    
    Must not run on:
      - VM禁止在指定主机
      - 例: 硬件兼容性
```

### 4.1 配置DRS

```powershell
# ========================================
# PowerCLI配置DRS
# ========================================

# 启用DRS
$cluster = Get-Cluster "Production-Cluster"
Set-Cluster -Cluster $cluster `
    -DrsEnabled:$true `
    -DrsAutomationLevel "FullyAutomated" `
    -DrsMode "FullyAutomated" `
    -Confirm:$false

# 设置DRS迁移阈值 (1-5, 5最激进)
Set-Cluster -Cluster $cluster `
    -DrsAutomationLevel "FullyAutomated" `
    -Confirm:$false

New-AdvancedSetting -Entity $cluster `
    -Name "TryBalanceVmsPerHost" `
    -Value 5 `
    -Confirm:$false

# 创建VM-VM亲和性规则 (保持在一起)
New-DrsRule -Cluster $cluster `
    -Name "Keep-Web-Cache-Together" `
    -KeepTogether $true `
    -VM (Get-VM "web-01","cache-01") `
    -Enabled $true

# 创建VM-VM反亲和性规则 (分开)
New-DrsRule -Cluster $cluster `
    -Name "Separate-DB-Primary-Standby" `
    -KeepTogether $false `
    -VM (Get-VM "db-primary","db-standby") `
    -Enabled $true

# 创建主机组
New-DrsClusterGroup -Cluster $cluster `
    -Name "HostGroup-HighEnd" `
    -VMHost (Get-VMHost "esxi-01","esxi-02")

New-DrsClusterGroup -Cluster $cluster `
    -Name "HostGroup-Standard" `
    -VMHost (Get-VMHost "esxi-03","esxi-04")

# 创建VM组
New-DrsClusterGroup -Cluster $cluster `
    -Name "VMGroup-Production" `
    -VM (Get-VM -Location $cluster | Where-Object {$_.Name -like "*prod*"})

# 创建VM-Host亲和性规则 (应该运行在)
New-DrsVMHostRule -Cluster $cluster `
    -Name "Prod-VMs-on-HighEnd-Hosts" `
    -VMGroup "VMGroup-Production" `
    -VMHostGroup "HostGroup-HighEnd" `
    -Type "ShouldRunOn" `
    -Enabled $true

# 查看DRS建议
Get-DrsRecommendation -Cluster $cluster | 
    Select-Object VM, Reason, RecommendedHost |
    Format-Table -AutoSize

# 应用DRS建议
Get-DrsRecommendation -Cluster $cluster -Priority 1 | 
    Apply-DrsRecommendation -RunAsync
```

---

## 5. vMotion与Storage vMotion

```yaml
vMotion_Overview:
  功能: 在线迁移虚拟机
  
  类型:
    vMotion:
      - 迁移VM到不同主机
      - 保持存储位置不变
      - 实时迁移, 无停机
    
    Storage vMotion:
      - 迁移VM磁盘到不同存储
      - 保持主机不变
      - 实时迁移, 无停机
    
    vMotion + Storage vMotion:
      - 同时迁移主机和存储
      - Cross vCenter vMotion
      - 长距离vMotion

要求:
  vMotion网络:
    - 专用千兆以上网络
    - 推荐10Gbps
    - VMkernel网卡标记"vMotion"
    - 低延迟
  
  共享存储:
    - vMotion需要共享存储
    - 或使用vSAN
  
  兼容性:
    - CPU兼容 (EVC模式)
    - 虚拟机硬件版本
    - 网络配置

Enhanced vMotion Compatibility (EVC):
  目的: 确保CPU兼容性
  
  原理:
    - 屏蔽新CPU特性
    - 向下兼容
    - 允许不同CPU代际主机间vMotion
  
  EVC模式:
    Intel:
      - Merom (Core 2)
      - Penryn (Core 2)
      - Nehalem (Core i7)
      - Westmere
      - Sandy Bridge
      - Ivy Bridge
      - Haswell
      - Broadwell
      - Skylake
      - Cascade Lake
    
    AMD:
      - AMD Opteron Gen 1
      - AMD Opteron Gen 2 (Barcelona)
      - AMD Opteron Gen 3 (Bulldozer)
      - AMD EPYC (Zen)
  
  配置建议:
    - 集群创建时启用EVC
    - 选择集群中最老CPU的EVC模式
    - 允许未来添加更新硬件
```

### 5.1 配置vMotion网络

```bash
# ========================================
# ESXi配置vMotion (CLI)
# ========================================

# 1. 创建vMotion VMkernel接口
esxcli network vswitch standard portgroup add \
    --portgroup-name="vMotion" \
    --vswitch-name=vSwitch0

esxcli network vswitch standard portgroup set \
    --portgroup-name="vMotion" \
    --vlan-id=20

esxcli network ip interface add \
    --interface-name=vmk1 \
    --portgroup-name="vMotion"

esxcli network ip interface ipv4 set \
    --interface-name=vmk1 \
    --ipv4=192.168.20.10 \
    --netmask=255.255.255.0 \
    --type=static

# 2. 启用vMotion服务
esxcli network ip interface tag add \
    --interface-name=vmk1 \
    --tagname=VMotion

# 3. 配置MTU (可选, Jumbo Frame)
esxcli network ip interface set \
    --interface-name=vmk1 \
    --mtu=9000

# 4. 验证
esxcli network ip interface list
esxcli network ip interface ipv4 get --interface-name=vmk1
```

### 5.2 执行vMotion

```powershell
# ========================================
# PowerCLI执行vMotion
# ========================================

# vMotion (只迁移计算)
Move-VM -VM "web-01" `
    -Destination (Get-VMHost "esxi-02.example.com") `
    -Confirm:$false

# Storage vMotion (只迁移存储)
Move-VM -VM "db-01" `
    -Datastore (Get-Datastore "iSCSI-Datastore-02") `
    -Confirm:$false

# vMotion + Storage vMotion (同时迁移)
Move-VM -VM "app-01" `
    -Destination (Get-VMHost "esxi-03.example.com") `
    -Datastore (Get-Datastore "NFS-Datastore-01") `
    -Confirm:$false

# 批量vMotion
Get-VM -Location (Get-VMHost "esxi-01") | 
    Where-Object {$_.PowerState -eq "PoweredOn"} |
    Move-VM -Destination (Get-VMHost "esxi-02") -RunAsync

# Cross vCenter vMotion (vSphere 6.0+)
$sourceVC = Connect-VIServer -Server vcenter1.example.com
$targetVC = Connect-VIServer -Server vcenter2.example.com

$vm = Get-VM -Name "critical-vm" -Server $sourceVC
$targetHost = Get-VMHost -Name "esxi-10" -Server $targetVC
$targetDatastore = Get-Datastore -Name "Datastore-B" -Server $targetVC

Move-VM -VM $vm `
    -Destination $targetHost `
    -Datastore $targetDatastore `
    -InventoryLocation (Get-Folder "Production" -Server $targetVC) `
    -Confirm:$false
```

---

## 6. 高可用网络配置

```yaml
HA网络最佳实践:
  管理网络冗余:
    - 至少2个物理网卡
    - 不同网卡连接不同交换机
    - 负载均衡: Route based on originating port ID
    - 故障切换: Explicit Failover Order
  
  vMotion网络:
    - 专用网络, VLAN隔离
    - 10Gbps+
    - Jumbo Frame (MTU 9000)
    - 多条vMotion网络 (vSphere 6.0+)
  
  FT日志网络:
    - 专用网络
    - 10Gbps
    - 极低延迟
    - Jumbo Frame
  
  存储网络:
    - iSCSI: 专用网络, Jumbo Frame
    - NFS: 专用网络, Jumbo Frame
    - 多路径配置

网络冗余配置:
  标准交换机 (vSS):
    上行链路:
      - 至少2个物理网卡
      - 主动/主动或主动/备用
    
    负载均衡策略:
      Route based on originating port ID: 默认
      Route based on IP hash: 需要EtherChannel
      Route based on source MAC: 简单
      Use explicit failover order: 主备模式
    
    故障切换:
      - 链路状态检测
      - 信标探测 (可选)
  
  分布式交换机 (vDS):
    上行链路:
      - LACP支持
      - 负载均衡增强
      - Network I/O Control
    
    高级功能:
      - Port Mirroring
      - NetFlow
      - LACP
      - Private VLAN
```

---

## 7. 监控与故障排查

### 7.1 HA监控

```powershell
# ========================================
# PowerCLI监控HA状态
# ========================================

# 获取集群HA状态
$cluster = Get-Cluster "Production-Cluster"
$cluster | Select-Object Name, HAEnabled, HAAdmissionControlEnabled, HAFailoverLevel

# 获取HA保护的VM
Get-VM -Location $cluster | 
    Select-Object Name, HARestartPriority, HAIsolationResponse |
    Format-Table -AutoSize

# 检查Master主机
$clusterView = Get-View -ViewType ClusterComputeResource -Filter @{"Name"=$cluster.Name}
$haConfig = $clusterView.RetrieveDasAdvancedRuntimeInfo()
$haConfig.DasHostInfo.Config | 
    Select-Object HostName, IsMaster |
    Format-Table -AutoSize

# 检查HA心跳数据存储
$clusterView.ConfigurationEx.DasConfig.HBDatastoreCandidatePolicy

# 查看HA事件
Get-VIEvent -Entity $cluster -MaxSamples 100 |
    Where-Object {$_.FullFormattedMessage -like "*HA*"} |
    Select-Object CreatedTime, FullFormattedMessage |
    Format-Table -AutoSize -Wrap

# 监控vMotion活动
Get-VIEvent -Entity $cluster -MaxSamples 100 -Types Info |
    Where-Object {$_.FullFormattedMessage -like "*vMotion*"} |
    Select-Object CreatedTime, VM, FullFormattedMessage |
    Format-Table -AutoSize
```

### 7.2 常见问题排查

```yaml
问题1: HA无法启用
  症状: 启用HA时报错
  
  可能原因:
    1. 主机没有共享存储
    2. 管理网络配置不正确
    3. 主机DNS解析问题
    4. 防火墙阻止HA通信
  
  排查步骤:
    1. 验证共享存储:
       - 所有主机能访问至少一个共享数据存储
       - esxcli storage vmfs extent list
    
    2. 检查管理网络:
       - 所有主机管理网络互通
       - ping其他主机管理IP
    
    3. DNS解析:
       - 主机FQDN能正确解析
       - nslookup esxi-01.example.com
    
    4. 防火墙:
       - 确保FDM端口8182开放
       - esxcli network firewall ruleset list | grep fdm

问题2: VM未受HA保护
  症状: VM状态显示"Not Protected"
  
  可能原因:
    1. HA准入控制资源不足
    2. VM位于本地数据存储
    3. VM重启优先级设为Disabled
  
  解决方案:
    1. 增加集群资源或调整准入控制
    2. 迁移VM到共享存储
    3. 修改VM重启优先级

问题3: vMotion失败
  症状: vMotion报错或速度慢
  
  可能原因:
    1. vMotion网络带宽不足
    2. CPU不兼容
    3. VM有不兼容设备
  
  排查:
    1. 检查vMotion网络:
       - esxcli network ip interface list
       - iperf测试带宽
    
    2. 检查CPU兼容性:
       - 启用EVC模式
    
    3. 检查VM配置:
       - 移除CD-ROM, USB设备
       - 断开ISO

问题4: FT无法启用
  症状: 启用FT时报错
  
  可能原因:
    1. VM不满足FT要求
    2. FT日志网络未配置
    3. 主机不足
  
  解决方案:
    1. 检查VM:
       - vCPU ≤ 8
       - 内存 ≤ 128GB
       - Thick磁盘
    
    2. 配置FT日志网络:
       - 10Gbps网络
       - 专用VMkernel适配器
    
    3. 至少2台主机
```

---

## 8. 最佳实践

```yaml
HA最佳实践:
  集群设计:
    ✅ 集群主机数量: 3-32台 (最佳: 8-16台)
    ✅ 主机硬件尽量一致
    ✅ 启用EVC确保CPU兼容
    ✅ 配置N+1或N+2冗余
    ✅ 准入控制: 容忍1-2台主机故障
  
  网络配置:
    ✅ 管理网络: 至少2个网卡, 冗余
    ✅ vMotion网络: 10Gbps+, 专用VLAN
    ✅ 存储网络: 多路径, 冗余
    ✅ 所有网络启用Jumbo Frame
    ✅ 使用vDS而非vSS (大型环境)
  
  存储配置:
    ✅ 使用共享存储 (iSCSI/NFS/FC/vSAN)
    ✅ 配置多路径
    ✅ 至少2-3个心跳数据存储
    ✅ 数据存储不要过载 (< 80% 容量)
  
  VM配置:
    ✅ 关键VM: High重启优先级
    ✅ 关键VM: 考虑使用FT (vCPU ≤ 8)
    ✅ 配置VM-VM反亲和性规则
    ✅ 使用Thick磁盘 (FT要求)
    ✅ 定期测试VM重启时间
  
  DRS配置:
    ✅ 生产环境使用完全自动化
    ✅ 迁移阈值: Moderate (平衡)
    ✅ 配置合理的亲和性规则
    ✅ 避免过多规则导致冲突
  
  监控和维护:
    ✅ 监控HA/DRS事件
    ✅ 定期查看HA建议
    ✅ 监控vMotion性能
    ✅ 定期测试故障切换
    ✅ 文档化HA配置
    ✅ 定期审查和优化规则

性能调优:
  vMotion优化:
    - 增加vMotion网络带宽
    - 启用Jumbo Frame
    - 多个vMotion VMkernel (vSphere 6.0+)
    - 同时vMotion数量限制 (默认4)
  
  DRS优化:
    - 调整迁移阈值
    - 监控DRS建议应用率
    - 优化亲和性规则
    - 避免资源碎片化
  
  HA优化:
    - 调整主机监控敏感度
    - 增加心跳数据存储数量
    - 优化VM重启顺序
    - 配置VM监控 (应用级HA)

容量规划:
  计算资源:
    公式: (N - X) × Host_Capacity
    N = 主机总数
    X = 容忍故障主机数
    
    示例:
      5台主机, 每台100 vCPU, 512GB RAM
      容忍1台故障
      可用: (5-1) × 100 vCPU = 400 vCPU
      可用: (5-1) × 512GB = 2048GB
      
      建议使用率: 70-80%
      推荐分配: 280-320 vCPU, 1434-1638GB
  
  存储容量:
    公式: Total_Storage × 0.8
    预留20%空间用于:
      - 快照
      - vMotion临时空间
      - 膨胀开销
  
  网络带宽:
    管理网络: 1Gbps (最小)
    vMotion: 10Gbps (推荐)
    存储: 10Gbps (iSCSI/NFS)
    业务: 根据需求

故障测试清单:
  测试1: 主机故障
    操作: 断开ESXi主机电源
    预期: VM在其他主机重启
    验证: VM运行时间, 业务中断时间
  
  测试2: 网络隔离
    操作: 禁用主机管理网络
    预期: HA触发隔离响应
    验证: VM被关闭或保持运行
  
  测试3: 存储故障
    操作: 断开存储连接
    预期: VM进入All Paths Down (APD)
    验证: HA重启超时VM
  
  测试4: vMotion
    操作: 迁移运行中的VM
    预期: 无业务中断, <2秒
    验证: 应用连接不中断
  
  测试5: DRS自动均衡
    操作: 在一台主机启动多个VM
    预期: DRS自动迁移VM平衡负载
    验证: 负载均匀分布
  
  测试6: FT切换
    操作: 断开Primary VM主机电源
    预期: Secondary立即接管
    验证: 业务完全无中断
```

---

## 相关文档

- [Kubernetes高可用架构](02_Kubernetes高可用架构.md)
- [备份恢复方案](03_备份恢复方案.md)
- [容灾演练流程](04_容灾演练流程.md)
- [存储容灾与备份](../03_存储架构/07_存储容灾与备份.md)
- [网络高可用](../04_网络架构/03_负载均衡与高可用.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪
