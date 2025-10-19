# Hyper-V安装与配置

> **返回**: [软件安装目录](README.md) | [虚拟化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Hyper-V安装与配置](#hyper-v安装与配置)
  - [📋 目录](#-目录)
  - [Hyper-V概述](#hyper-v概述)
    - [Hyper-V架构](#hyper-v架构)
    - [Hyper-V优势](#hyper-v优势)
    - [适用场景](#适用场景)
  - [环境准备](#环境准备)
    - [硬件要求](#硬件要求)
    - [系统要求](#系统要求)
    - [检查虚拟化支持](#检查虚拟化支持)
  - [Hyper-V安装](#hyper-v安装)
    - [Windows Server安装](#windows-server安装)
    - [Windows 10/11安装](#windows-1011安装)
    - [PowerShell自动化安装](#powershell自动化安装)
  - [网络配置](#网络配置)
    - [虚拟交换机类型](#虚拟交换机类型)
    - [创建虚拟交换机](#创建虚拟交换机)
    - [网络最佳实践](#网络最佳实践)
  - [存储配置](#存储配置)
    - [存储位置](#存储位置)
    - [存储类型](#存储类型)
    - [存储管理](#存储管理)
  - [虚拟机管理](#虚拟机管理)
    - [使用GUI创建虚拟机](#使用gui创建虚拟机)
    - [使用PowerShell创建虚拟机](#使用powershell创建虚拟机)
    - [虚拟机管理命令](#虚拟机管理命令)
  - [高级功能](#高级功能)
    - [Live Migration](#live-migration)
    - [Replica容灾](#replica容灾)
    - [Shielded VMs](#shielded-vms)
  - [性能优化](#性能优化)
  - [相关文档](#相关文档)

---

## Hyper-V概述

### Hyper-V架构

```yaml
Hyper-V (Windows Hypervisor):
  说明:
    - Microsoft的Type-1 Hypervisor
    - 内置于Windows Server和Windows 10/11 Pro
    - 企业级虚拟化平台
    - 深度集成Windows生态
  
  核心组件:
    Hypervisor层:
      - Windows Hypervisor (hvix64.exe)
      - 微内核架构
      - 直接运行在硬件上
      - 权限级别: Ring -1
    
    父分区 (Parent Partition):
      - Windows Server/Windows 10/11
      - 运行Hyper-V管理服务
      - 提供虚拟化管理接口
      - 驱动模型 (设备访问)
    
    子分区 (Child Partition):
      - 虚拟机 (VM)
      - 隔离的执行环境
      - 通过VMBus与父分区通信
    
    管理工具:
      - Hyper-V管理器 (GUI)
      - PowerShell模块 (Hyper-V)
      - Windows Admin Center (Web)
      - System Center Virtual Machine Manager (SCVMM)
  
  架构图:
    应用层:
      [Hyper-V管理器] [PowerShell] [SCVMM]
            ↓               ↓          ↓
    父分区 (Root Partition):
      [管理OS: Windows Server]
      [虚拟化服务提供者 (VSP)]
      [设备驱动程序]
            ↓
    Hypervisor层:
      [Windows Hypervisor]
            ↓
    硬件层:
      [CPU (VT-x/AMD-V)] [内存] [存储] [网络]
            ↓
    子分区:
      [VM1] [VM2] [VM3] ...
      ↓
      [虚拟化服务客户端 (VSC)]
```

### Hyper-V优势

```yaml
优势:
  Windows生态集成:
    ✅ 深度集成Windows
    ✅ Active Directory集成
    ✅ System Center集成
    ✅ Azure集成
  
  企业级功能:
    ✅ Live Migration (在线迁移)
    ✅ Replica (容灾复制)
    ✅ Shielded VMs (加密虚拟机)
    ✅ 存储QoS
    ✅ 网络虚拟化
  
  性能优秀:
    ✅ Type-1 Hypervisor
    ✅ 接近裸机性能
    ✅ 动态内存
    ✅ SR-IOV网络
  
  管理便捷:
    ✅ 图形化界面友好
    ✅ PowerShell自动化
    ✅ Windows Admin Center
    ✅ 远程管理

劣势:
  ⚠️ 仅支持Windows宿主机
  ⚠️ Windows Server许可费用
  ⚠️ Linux VM支持不如VMware/KVM
  ⚠️ 开源生态支持较弱

对比VMware:
  功能: VMware ≈ Hyper-V (功能相当)
  性能: VMware ≈ Hyper-V (性能相当)
  易用性: VMware > Hyper-V (VMware稍好)
  成本: Hyper-V > VMware (Hyper-V含在Windows许可中)
  Windows集成: Hyper-V > VMware
  Linux支持: VMware > Hyper-V
```

### 适用场景

```yaml
推荐场景:
  Windows环境:
    ✅ Windows Server工作负载
    ✅ Active Directory环境
    ✅ .NET应用
    ✅ Microsoft SQL Server
  
  微软技术栈:
    ✅ Azure混合云
    ✅ System Center管理
    ✅ Microsoft 365集成
  
  中小型企业:
    ✅ 已有Windows Server许可
    ✅ IT团队熟悉Windows
    ✅ 预算有限
  
  开发测试:
    ✅ Windows 10/11 Pro内置
    ✅ 开发人员本地虚拟化
    ✅ 容器开发 (Docker Desktop)

不推荐场景:
  ❌ 纯Linux工作负载
  ❌ 开源优先策略
  ❌ 非Windows生态
  ❌ 需要高级Linux虚拟化特性
```

---

## 环境准备

### 硬件要求

```yaml
最低配置:
  CPU:
    核心: 2核心 (4线程推荐)
    频率: 1.4 GHz+
    要求: 
      - 64位处理器
      - 支持VT-x (Intel) 或 AMD-V (AMD)
      - 支持SLAT (Second Level Address Translation)
        Intel: EPT (Extended Page Tables)
        AMD: RVI (Rapid Virtualization Indexing)
  
  内存:
    Windows Server: 4GB (推荐8GB+)
    Windows 10/11: 4GB (推荐8GB+)
    每个VM: 512MB-2GB+
  
  存储:
    系统盘: 32GB+ (推荐100GB+)
    VM存储: 根据需求
    推荐: SSD (大幅提升VM性能)
  
  网络:
    最小: 1Gbps
    推荐: 10Gbps (生产环境)

推荐配置:
  CPU: 
    Intel Xeon E5 / Gold系列
    AMD EPYC系列
    核心: 8核心+
  
  内存: 32GB+ (Windows Server)
  
  存储:
    系统: 500GB SSD
    VM存储: 2TB+ NVMe SSD
  
  网络: 10Gbps x2 (双上行)

SLAT支持:
  检查方法:
    systeminfo | findstr /C:"Hyper-V Requirements"
  
  必须显示:
    ✅ A hypervisor has been detected
    ✅ VM Monitor Mode Extensions: Yes
    ✅ Virtualization Enabled In Firmware: Yes
    ✅ Second Level Address Translation: Yes
    ✅ Data Execution Prevention Available: Yes
```

### 系统要求

```yaml
Windows Server:
  支持版本:
    Windows Server 2022:
      版本: 21H2
      内核: NT 10.0
      支持: 至2031年
      推荐: ✅ 最新特性
    
    Windows Server 2019:
      版本: 1809
      内核: NT 10.0
      支持: 至2029年
      推荐: ✅ 长期支持
    
    Windows Server 2016:
      版本: 1607
      支持: 至2027年
      推荐: ⚠️ 考虑升级
  
  版本要求:
    Standard: 支持2个VM
    Datacenter: 无限VM (推荐生产环境)

Windows 10/11 (客户端):
  支持版本:
    Windows 11 Pro/Enterprise:
      版本: 21H2+
      推荐: ✅ 最新版本
    
    Windows 10 Pro/Enterprise:
      版本: 1809+
      推荐: ✅ 用于开发测试
  
  说明:
    ⚠️ Home版本不支持Hyper-V
    ⚠️ 客户端版本功能受限:
      - 无Live Migration
      - 无Replica
      - 无集群支持
  
  用途:
    ✅ 开发人员工作站
    ✅ 测试环境
    ✅ Docker Desktop后端
    ❌ 不推荐生产环境

功能对比:
  特性                    Server    Client
  基础虚拟化              ✅        ✅
  Live Migration         ✅        ❌
  Replica                ✅        ❌
  故障转移集群            ✅        ❌
  SR-IOV                 ✅        ✅
  嵌套虚拟化              ✅        ✅
  动态内存                ✅        ✅
```

### 检查虚拟化支持

```powershell
# PowerShell脚本 - 检查Hyper-V支持

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Hyper-V虚拟化支持检测" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查系统版本
Write-Host "1. 系统版本检查..." -ForegroundColor Green
$os = Get-CimInstance -ClassName Win32_OperatingSystem
Write-Host "   操作系统: $($os.Caption)" -ForegroundColor White
Write-Host "   版本: $($os.Version)" -ForegroundColor White
Write-Host "   架构: $($os.OSArchitecture)" -ForegroundColor White

if ($os.OSArchitecture -ne "64-bit") {
    Write-Host "   ❌ 需要64位操作系统" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ 系统版本满足要求" -ForegroundColor Green
Write-Host ""

# 2. 检查Hyper-V要求
Write-Host "2. Hyper-V硬件要求检查..." -ForegroundColor Green
$hvReqs = systeminfo | Select-String -Pattern "Hyper-V Requirements"
if ($hvReqs) {
    $hvReqs | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
} else {
    Write-Host "   ⚠️  无法获取Hyper-V要求信息" -ForegroundColor Yellow
}
Write-Host ""

# 3. 检查CPU虚拟化支持
Write-Host "3. CPU虚拟化支持检查..." -ForegroundColor Green
$proc = Get-CimInstance -ClassName Win32_Processor
Write-Host "   CPU: $($proc.Name)" -ForegroundColor White
Write-Host "   核心数: $($proc.NumberOfCores)" -ForegroundColor White
Write-Host "   逻辑处理器: $($proc.NumberOfLogicalProcessors)" -ForegroundColor White

# 使用systeminfo检查详细信息
$systemInfo = systeminfo
$vmExtensions = $systemInfo | Select-String "VM Monitor Mode Extensions"
$virtEnabled = $systemInfo | Select-String "Virtualization Enabled In Firmware"
$slat = $systemInfo | Select-String "Second Level Address Translation"

if ($vmExtensions -match "Yes") {
    Write-Host "   ✅ VM Monitor Mode Extensions: Yes" -ForegroundColor Green
} else {
    Write-Host "   ❌ VM Monitor Mode Extensions: No" -ForegroundColor Red
}

if ($virtEnabled -match "Yes") {
    Write-Host "   ✅ 固件中已启用虚拟化" -ForegroundColor Green
} else {
    Write-Host "   ❌ 固件中未启用虚拟化 - 请在BIOS中启用VT-x/AMD-V" -ForegroundColor Red
}

if ($slat -match "Yes") {
    Write-Host "   ✅ SLAT (Second Level Address Translation): Yes" -ForegroundColor Green
} else {
    Write-Host "   ❌ SLAT: No - CPU不支持EPT/RVI" -ForegroundColor Red
}
Write-Host ""

# 4. 检查内存
Write-Host "4. 内存检查..." -ForegroundColor Green
$memory = Get-CimInstance -ClassName Win32_PhysicalMemory
$totalMemoryGB = [math]::Round(($memory | Measure-Object -Property Capacity -Sum).Sum / 1GB, 2)
Write-Host "   总内存: ${totalMemoryGB}GB" -ForegroundColor White

if ($totalMemoryGB -ge 8) {
    Write-Host "   ✅ 内存充足 (>=8GB)" -ForegroundColor Green
} elseif ($totalMemoryGB -ge 4) {
    Write-Host "   ⚠️  内存较少 (4-8GB)" -ForegroundColor Yellow
} else {
    Write-Host "   ❌ 内存不足 (<4GB)" -ForegroundColor Red
}
Write-Host ""

# 5. 检查Hyper-V功能状态
Write-Host "5. Hyper-V功能状态..." -ForegroundColor Green
$hypervFeature = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -ErrorAction SilentlyContinue

if ($hypervFeature) {
    Write-Host "   Hyper-V功能状态: $($hypervFeature.State)" -ForegroundColor White
    if ($hypervFeature.State -eq "Enabled") {
        Write-Host "   ✅ Hyper-V已启用" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Hyper-V未启用" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  Hyper-V功能不可用" -ForegroundColor Yellow
}
Write-Host ""

# 总结
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  检测完成" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

if ($virtEnabled -match "Yes" -and $slat -match "Yes" -and $totalMemoryGB -ge 4) {
    Write-Host "✅ 系统支持Hyper-V虚拟化！" -ForegroundColor Green
} else {
    Write-Host "❌ 系统不满足Hyper-V要求" -ForegroundColor Red
}
```

---

## Hyper-V安装

### Windows Server安装

```powershell
# PowerShell脚本 - Windows Server Hyper-V安装

# 以管理员权限运行

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Hyper-V安装脚本 - Windows Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查系统
Write-Host "步骤1: 检查系统..." -ForegroundColor Green
$os = Get-CimInstance -ClassName Win32_OperatingSystem
Write-Host "   系统: $($os.Caption)" -ForegroundColor White
Write-Host ""

# 2. 检查Hyper-V功能
Write-Host "步骤2: 检查Hyper-V功能..." -ForegroundColor Green
$hypervInstalled = Get-WindowsFeature -Name Hyper-V
if ($hypervInstalled.Installed) {
    Write-Host "   ✅ Hyper-V已安装" -ForegroundColor Green
    Write-Host "   无需重新安装" -ForegroundColor Yellow
    exit 0
}
Write-Host ""

# 3. 安装Hyper-V角色
Write-Host "步骤3: 安装Hyper-V角色..." -ForegroundColor Green
Write-Host "   这将安装:" -ForegroundColor White
Write-Host "   - Hyper-V角色" -ForegroundColor White
Write-Host "   - Hyper-V PowerShell模块" -ForegroundColor White
Write-Host "   - Hyper-V管理工具" -ForegroundColor White
Write-Host ""

$confirmation = Read-Host "是否继续安装？(Y/N)"
if ($confirmation -ne 'Y') {
    Write-Host "安装已取消" -ForegroundColor Yellow
    exit 0
}

# 安装Hyper-V和管理工具
Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart

# 如果没有自动重启，手动提示
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Hyper-V安装完成" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  系统需要重启以完成安装" -ForegroundColor Yellow
Write-Host ""
$restart = Read-Host "是否现在重启？(Y/N)"
if ($restart -eq 'Y') {
    Restart-Computer -Force
}
```

### Windows 10/11安装

```powershell
# PowerShell脚本 - Windows 10/11 Hyper-V安装

# 以管理员权限运行

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Hyper-V安装脚本 - Windows 10/11" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查系统版本
Write-Host "步骤1: 检查系统版本..." -ForegroundColor Green
$os = Get-CimInstance -ClassName Win32_OperatingSystem
$osCaption = $os.Caption

Write-Host "   系统: $osCaption" -ForegroundColor White

# 检查是否为Pro/Enterprise版本
if ($osCaption -notmatch "Pro|Enterprise|Education") {
    Write-Host "   ❌ 不支持的Windows版本" -ForegroundColor Red
    Write-Host "   需要: Windows 10/11 Pro, Enterprise, 或 Education" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ 系统版本支持Hyper-V" -ForegroundColor Green
Write-Host ""

# 2. 检查Hyper-V功能
Write-Host "步骤2: 检查Hyper-V功能状态..." -ForegroundColor Green
$hypervFeature = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All

if ($hypervFeature.State -eq "Enabled") {
    Write-Host "   ✅ Hyper-V已启用" -ForegroundColor Green
    Write-Host "   无需重新安装" -ForegroundColor Yellow
    exit 0
}
Write-Host "   Hyper-V当前状态: $($hypervFeature.State)" -ForegroundColor White
Write-Host ""

# 3. 安装Hyper-V
Write-Host "步骤3: 安装Hyper-V..." -ForegroundColor Green
Write-Host "   这将启用:" -ForegroundColor White
Write-Host "   - Hyper-V平台" -ForegroundColor White
Write-Host "   - Hyper-V管理工具" -ForegroundColor White
Write-Host "   - Hyper-V PowerShell模块" -ForegroundColor White
Write-Host ""

$confirmation = Read-Host "是否继续安装？(Y/N)"
if ($confirmation -ne 'Y') {
    Write-Host "安装已取消" -ForegroundColor Yellow
    exit 0
}

# 启用Hyper-V功能
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All -NoRestart

# 启用Hyper-V管理工具
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-Tools-All -All -NoRestart

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Hyper-V安装完成" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  系统需要重启以完成安装" -ForegroundColor Yellow
Write-Host ""
$restart = Read-Host "是否现在重启？(Y/N)"
if ($restart -eq 'Y') {
    Restart-Computer -Force
}
```

### PowerShell自动化安装

```powershell
# 完整自动化安装和配置脚本

# 检查管理员权限
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ 需要管理员权限运行此脚本" -ForegroundColor Red
    exit 1
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Hyper-V自动化安装与配置" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检测系统类型
$osType = (Get-CimInstance -ClassName Win32_OperatingSystem).Caption
if ($osType -match "Server") {
    $isServer = $true
    Write-Host "检测到Windows Server系统" -ForegroundColor Green
} else {
    $isServer = $false
    Write-Host "检测到Windows客户端系统" -ForegroundColor Green
}
Write-Host ""

# 2. 安装Hyper-V
Write-Host "正在安装Hyper-V..." -ForegroundColor Green
if ($isServer) {
    # Windows Server
    Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart:$false
} else {
    # Windows 10/11
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All -NoRestart
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-Tools-All -All -NoRestart
}
Write-Host "✅ Hyper-V安装完成" -ForegroundColor Green
Write-Host ""

# 3. 配置默认虚拟机路径
Write-Host "配置默认路径..." -ForegroundColor Green
$vmPath = "C:\Hyper-V\VMs"
$vhdPath = "C:\Hyper-V\VHDs"

if (-not (Test-Path $vmPath)) {
    New-Item -Path $vmPath -ItemType Directory -Force | Out-Null
}
if (-not (Test-Path $vhdPath)) {
    New-Item -Path $vhdPath -ItemType Directory -Force | Out-Null
}

# 设置默认路径 (重启后生效)
# Set-VMHost -VirtualMachinePath $vmPath -VirtualHardDiskPath $vhdPath

Write-Host "✅ 默认路径已配置:" -ForegroundColor Green
Write-Host "   虚拟机: $vmPath" -ForegroundColor White
Write-Host "   虚拟磁盘: $vhdPath" -ForegroundColor White
Write-Host ""

# 4. 完成
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  安装完成" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "  1. 重启计算机" -ForegroundColor White
Write-Host "  2. 打开Hyper-V管理器" -ForegroundColor White
Write-Host "  3. 创建虚拟交换机" -ForegroundColor White
Write-Host "  4. 创建虚拟机" -ForegroundColor White
Write-Host ""

$restart = Read-Host "是否现在重启？(Y/N)"
if ($restart -eq 'Y') {
    Restart-Computer -Force
}
```

---

## 网络配置

### 虚拟交换机类型

```yaml
外部虚拟交换机 (External):
  说明:
    连接到物理网络适配器
    VM可访问外部网络
    VM可被外部访问
  
  用途:
    ✅ 生产VM
    ✅ 需要外部访问的服务器
    ✅ 连接到公司网络
  
  特点:
    - VM获得与宿主机同一网段IP
    - 可选择是否允许宿主机共享此适配器

内部虚拟交换机 (Internal):
  说明:
    仅连接宿主机和VM
    VM之间和宿主机可通信
    无法访问外部网络（除非配置NAT）
  
  用途:
    ✅ 宿主机与VM通信
    ✅ VM之间通信
    ✅ 开发测试环境
  
  特点:
    - 需要手动配置IP地址
    - 可配置NAT共享宿主机网络

专用虚拟交换机 (Private):
  说明:
    仅VM之间通信
    与宿主机隔离
    无法访问外部网络
  
  用途:
    ✅ VM之间隔离网络
    ✅ 安全测试环境
    ✅ 集群内部网络
  
  特点:
    - 完全隔离
    - 需要多个VM才有意义
```

### 创建虚拟交换机

**使用GUI创建**:

```yaml
打开Hyper-V管理器:
  路径: 开始菜单 → Windows管理工具 → Hyper-V管理器
  或: 运行 virtmgmt.msc

创建外部交换机:
  1. 右侧面板 → 虚拟交换机管理器
  2. 选择: 新建虚拟网络交换机
  3. 类型: 外部
  4. 点击: 创建虚拟交换机
  5. 配置:
     名称: External-Switch
     连接类型: 外部网络
     物理网卡: 选择物理网卡 (如 "Ethernet")
     ☑ 允许管理操作系统共享此网络适配器 (推荐)
  6. 点击: 应用
  7. 警告提示: 网络连接可能暂时中断
  8. 点击: 是
  9. 完成

创建内部交换机:
  配置:
    名称: Internal-Switch
    连接类型: 内部网络
  
  配置NAT (可选，允许VM访问外网):
    1. 打开PowerShell (管理员)
    2. 为内部交换机配置IP:
       New-NetIPAddress -IPAddress 192.168.100.1 `
         -PrefixLength 24 `
         -InterfaceAlias "vEthernet (Internal-Switch)"
    3. 创建NAT:
       New-NetNat -Name "Internal-NAT" `
         -InternalIPInterfaceAddressPrefix 192.168.100.0/24

创建专用交换机:
  配置:
    名称: Private-Switch
    连接类型: 专用网络
  
  无需额外配置
```

**使用PowerShell创建**:

```powershell
# 创建外部虚拟交换机

# 1. 列出物理网卡
Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Format-Table Name, InterfaceDescription

# 2. 创建外部交换机
$netAdapter = Get-NetAdapter -Name "Ethernet"
New-VMSwitch -Name "External-Switch" `
    -NetAdapterName $netAdapter.Name `
    -AllowManagementOS $true

# 创建内部虚拟交换机
New-VMSwitch -Name "Internal-Switch" -SwitchType Internal

# 配置内部交换机的NAT
$ifIndex = (Get-NetAdapter | Where-Object {$_.Name -like "*Internal-Switch*"}).ifIndex
New-NetIPAddress -IPAddress 192.168.100.1 `
    -PrefixLength 24 `
    -InterfaceIndex $ifIndex

New-NetNat -Name "Internal-NAT" `
    -InternalIPInterfaceAddressPrefix 192.168.100.0/24

# 创建专用虚拟交换机
New-VMSwitch -Name "Private-Switch" -SwitchType Private

# 查看虚拟交换机
Get-VMSwitch | Format-Table Name, SwitchType, NetAdapterInterfaceDescription
```

### 网络最佳实践

```yaml
物理网卡分配:
  小型环境 (2个网口):
    网卡1: External-Switch (管理+业务)
    网卡2: 备用或存储网络
  
  中型环境 (4个网口):
    网卡1: 管理网络
    网卡2-3: 业务网络 (NIC Teaming)
    网卡4: 存储网络 (iSCSI)
  
  大型环境 (6+个网口):
    网卡1-2: 管理网络 (NIC Teaming)
    网卡3-4: 业务网络 (NIC Teaming)
    网卡5-6: 存储网络 (NIC Teaming)

NIC Teaming (网卡绑定):
  配置PowerShell:
    ```powershell
    # 创建NIC Team
    New-NetLbfoTeam -Name "Team1" `
        -TeamMembers "Ethernet 2","Ethernet 3" `
        -TeamingMode SwitchIndependent `
        -LoadBalancingAlgorithm Dynamic
    
    # 创建虚拟交换机绑定到Team
    New-VMSwitch -Name "External-Teamed" `
        -NetAdapterName "Team1" `
        -AllowManagementOS $true
    ```
  
  优势:
    ✅ 带宽聚合
    ✅ 冗余和故障转移
    ✅ 提升可用性

VLAN配置:
  为VM配置VLAN:
    ```powershell
    # 为VM网卡配置VLAN
    Set-VMNetworkAdapterVlan -VMName "VM01" `
        -VlanId 10 `
        -Access
    
    # 配置trunk模式
    Set-VMNetworkAdapterVlan -VMName "VM01" `
        -Trunk `
        -AllowedVlanIdList "10,20,30"
    ```

QoS (服务质量):
  限制VM带宽:
    ```powershell
    # 设置最小和最大带宽
    Set-VMNetworkAdapter -VMName "VM01" `
        -MinimumBandwidthWeight 10 `
        -MaximumBandwidth 1000000000  # 1 Gbps
    ```
```

---

## 存储配置

### 存储位置

```powershell
# 配置默认虚拟机和虚拟硬盘路径

# 查看当前默认路径
Get-VMHost | Select-Object VirtualMachinePath, VirtualHardDiskPath

# 设置默认路径
Set-VMHost -VirtualMachinePath "D:\Hyper-V\VMs" `
    -VirtualHardDiskPath "D:\Hyper-V\VHDs"

# 为特定虚拟机指定路径
New-VM -Name "VM01" `
    -Path "E:\VMs\VM01" `
    -NewVHDPath "E:\VHDs\VM01.vhdx" `
    -NewVHDSizeBytes 40GB
```

### 存储类型

```yaml
VHDX (推荐):
  说明: Hyper-V虚拟硬盘格式 (第2代)
  最大容量: 64TB
  特性:
    ✅ 支持更大容量
    ✅ 防止数据损坏
    ✅ 性能优化
    ✅ 支持4K扇区
  用途: 所有新虚拟机 (推荐)

VHD:
  说明: 传统虚拟硬盘格式 (第1代)
  最大容量: 2TB
  特性:
    ⚠️ 兼容性好
    ⚠️ 容量限制
  用途: 仅兼容性需求

固定大小 (Fixed):
  特点:
    - 创建时分配全部空间
    - 性能最佳
    - 占用磁盘空间大
  用途:
    ✅ 生产环境
    ✅ 性能敏感应用
    ✅ I/O密集型

动态扩展 (Dynamic):
  特点:
    - 按需增长
    - 节省磁盘空间
    - 性能略低
  用途:
    ✅ 开发测试
    ✅ 磁盘空间有限
    ✅ 虚拟机较多

差异磁盘 (Differencing):
  特点:
    - 基于父磁盘
    - 仅存储变化
    - 节省空间
  用途:
    ✅ 虚拟机模板
    ✅ 快速部署
    ✅ 测试环境
```

### 存储管理

```powershell
# 创建虚拟硬盘

# 创建固定大小VHDX
New-VHD -Path "D:\VHDs\VM01-Fixed.vhdx" `
    -SizeBytes 40GB `
    -Fixed

# 创建动态扩展VHDX
New-VHD -Path "D:\VHDs\VM01-Dynamic.vhdx" `
    -SizeBytes 100GB `
    -Dynamic

# 创建差异磁盘
New-VHD -Path "D:\VHDs\VM01-Diff.vhdx" `
    -ParentPath "D:\VHDs\Template.vhdx" `
    -Differencing

# 转换磁盘格式
Convert-VHD -Path "D:\VHDs\Old.vhd" `
    -DestinationPath "D:\VHDs\New.vhdx" `
    -VHDType Dynamic

# 调整虚拟硬盘大小
Resize-VHD -Path "D:\VHDs\VM01.vhdx" `
    -SizeBytes 60GB

# 压缩虚拟硬盘 (回收未使用空间)
Optimize-VHD -Path "D:\VHDs\VM01.vhdx" `
    -Mode Full

# 挂载虚拟硬盘
Mount-VHD -Path "D:\VHDs\VM01.vhdx"

# 卸载虚拟硬盘
Dismount-VHD -Path "D:\VHDs\VM01.vhdx"

# 查看虚拟硬盘信息
Get-VHD -Path "D:\VHDs\VM01.vhdx" | Format-List

# 为虚拟机添加硬盘
Add-VMHardDiskDrive -VMName "VM01" `
    -Path "D:\VHDs\VM01-Data.vhdx"

# 移除硬盘
Remove-VMHardDiskDrive -VMName "VM01" `
    -ControllerType SCSI `
    -ControllerNumber 0 `
    -ControllerLocation 1
```

---

## 虚拟机管理

### 使用GUI创建虚拟机

```yaml
创建向导:
  1. 打开Hyper-V管理器
  2. 右键点击主机 → 新建 → 虚拟机
  3. 新建虚拟机向导:
     
     准备工作:
       - 点击: 下一步
     
     指定名称和位置:
       - 名称: Ubuntu-Server-01
       - ☑ 将虚拟机存储在其他位置
       - 位置: D:\Hyper-V\VMs
       - 点击: 下一步
     
     指定代:
       - 选择: 第2代 (推荐，支持UEFI)
       - 或: 第1代 (兼容性，支持传统BIOS)
       - 注意: Linux推荐第2代
       - 点击: 下一步
     
     分配内存:
       - 启动内存: 2048 MB
       - ☑ 为此虚拟机使用动态内存
       - 点击: 下一步
     
     配置网络:
       - 连接: External-Switch
       - 点击: 下一步
     
     连接虚拟硬盘:
       - 选择: 创建虚拟硬盘
       - 名称: Ubuntu-Server-01.vhdx
       - 位置: D:\Hyper-V\VHDs
       - 大小: 40 GB
       - 点击: 下一步
     
     安装选项:
       - 选择: 从可启动映像文件安装操作系统
       - 映像文件: 浏览到ISO文件
       - 点击: 下一步
     
     完成:
       - 检查摘要
       - 点击: 完成
  
  4. 配置虚拟机 (可选):
     右键虚拟机 → 设置
     - 处理器: 调整CPU数量
     - 内存: 调整内存大小
     - 网络适配器: 高级功能
     - 安全性: 安全启动设置

第2代vs第1代:
  第2代 (推荐):
    ✅ UEFI启动
    ✅ 安全启动
    ✅ 更快启动
    ✅ 支持64位
    ⚠️ 某些老系统不支持
  
  第1代:
    ✅ BIOS启动
    ✅ 兼容性最好
    ✅ 支持32位
    ⚠️ 功能较少
```

### 使用PowerShell创建虚拟机

```powershell
#!/usr/bin/env pwsh
# 创建Hyper-V虚拟机脚本

# 配置参数
$VMName = "Ubuntu-Server-01"
$VMPath = "D:\Hyper-V\VMs"
$VHDPath = "D:\Hyper-V\VHDs\$VMName.vhdx"
$VHDSize = 40GB
$Memory = 2GB
$CPUCount = 2
$SwitchName = "External-Switch"
$ISOPath = "D:\ISOs\ubuntu-22.04-server.iso"

Write-Host "创建虚拟机: $VMName" -ForegroundColor Green

# 1. 创建虚拟硬盘
Write-Host "创建虚拟硬盘..." -ForegroundColor Cyan
New-VHD -Path $VHDPath `
    -SizeBytes $VHDSize `
    -Dynamic

# 2. 创建虚拟机 (第2代)
Write-Host "创建虚拟机..." -ForegroundColor Cyan
New-VM -Name $VMName `
    -MemoryStartupBytes $Memory `
    -Generation 2 `
    -VHDPath $VHDPath `
    -Path $VMPath `
    -SwitchName $SwitchName

# 3. 配置虚拟机

# 配置处理器
Set-VMProcessor -VMName $VMName -Count $CPUCount

# 配置动态内存
Set-VMMemory -VMName $VMName `
    -DynamicMemoryEnabled $true `
    -MinimumBytes 512MB `
    -MaximumBytes 4GB `
    -Buffer 20

# 配置自动启动/停止
Set-VM -Name $VMName `
    -AutomaticStartAction Start `
    -AutomaticStopAction ShutDown

# 4. 挂载ISO
Write-Host "挂载ISO..." -ForegroundColor Cyan
Add-VMDvdDrive -VMName $VMName `
    -Path $ISOPath

# 配置启动顺序 (从DVD启动)
$dvd = Get-VMDvdDrive -VMName $VMName
Set-VMFirmware -VMName $VMName `
    -FirstBootDevice $dvd

# 5. 禁用安全启动 (Linux需要)
Set-VMFirmware -VMName $VMName `
    -EnableSecureBoot Off

# 6. 启动虚拟机
Write-Host "启动虚拟机..." -ForegroundColor Cyan
Start-VM -Name $VMName

# 7. 显示信息
Write-Host ""
Write-Host "✅ 虚拟机创建完成" -ForegroundColor Green
Write-Host "虚拟机名称: $VMName" -ForegroundColor White
Write-Host "内存: $($Memory/1GB)GB (动态)" -ForegroundColor White
Write-Host "CPU: $CPUCount 核" -ForegroundColor White
Write-Host "硬盘: $VHDPath" -ForegroundColor White
Write-Host "网络: $SwitchName" -ForegroundColor White
Write-Host ""
Write-Host "使用以下命令连接:" -ForegroundColor Yellow
Write-Host "vmconnect.exe localhost `"$VMName`"" -ForegroundColor White
```

### 虚拟机管理命令

```powershell
# Hyper-V虚拟机管理常用PowerShell命令

# === 生命周期管理 ===

# 列出所有虚拟机
Get-VM | Format-Table Name, State, CPUUsage, MemoryAssigned

# 启动虚拟机
Start-VM -Name "VM01"

# 关闭虚拟机 (优雅关机)
Stop-VM -Name "VM01"

# 强制关闭虚拟机
Stop-VM -Name "VM01" -Force

# 重启虚拟机
Restart-VM -Name "VM01"

# 暂停虚拟机
Suspend-VM -Name "VM01"

# 恢复虚拟机
Resume-VM -Name "VM01"

# 保存虚拟机状态
Save-VM -Name "VM01"

# 删除虚拟机
Remove-VM -Name "VM01"

# 删除虚拟机及虚拟硬盘
Remove-VM -Name "VM01" -Force
Remove-Item "D:\Hyper-V\VHDs\VM01.vhdx"

# === 配置管理 ===

# 查看虚拟机详细信息
Get-VM -Name "VM01" | Format-List

# 配置CPU
Set-VMProcessor -VMName "VM01" -Count 4

# 配置内存
Set-VMMemory -VMName "VM01" `
    -DynamicMemoryEnabled $true `
    -MinimumBytes 1GB `
    -MaximumBytes 8GB

# 配置静态内存
Set-VMMemory -VMName "VM01" `
    -DynamicMemoryEnabled $false `
    -StartupBytes 4GB

# 配置集成服务
Enable-VMIntegrationService -VMName "VM01" -Name "Guest Service Interface"

# 自动启动配置
Set-VM -Name "VM01" -AutomaticStartAction Start

# === 快照管理 ===

# 创建快照
Checkpoint-VM -Name "VM01" -SnapshotName "Before Update"

# 列出快照
Get-VMSnapshot -VMName "VM01"

# 恢复快照
Restore-VMSnapshot -VMName "VM01" -Name "Before Update" -Confirm:$false

# 删除快照
Remove-VMSnapshot -VMName "VM01" -Name "Before Update"

# 删除所有快照
Get-VMSnapshot -VMName "VM01" | Remove-VMSnapshot

# === 网络管理 ===

# 查看虚拟机网卡
Get-VMNetworkAdapter -VMName "VM01"

# 添加网卡
Add-VMNetworkAdapter -VMName "VM01" -SwitchName "Internal-Switch"

# 删除网卡
Remove-VMNetworkAdapter -VMName "VM01" -Name "Network Adapter 2"

# 配置VLAN
Set-VMNetworkAdapterVlan -VMName "VM01" -VlanId 10 -Access

# === 存储管理 ===

# 查看虚拟机硬盘
Get-VMHardDiskDrive -VMName "VM01"

# 添加硬盘
Add-VMHardDiskDrive -VMName "VM01" `
    -Path "D:\VHDs\VM01-Data.vhdx"

# 移除硬盘
Remove-VMHardDiskDrive -VMName "VM01" `
    -ControllerType SCSI `
    -ControllerNumber 0 `
    -ControllerLocation 1

# === 导入/导出 ===

# 导出虚拟机
Export-VM -Name "VM01" -Path "E:\VMExport"

# 导入虚拟机
Import-VM -Path "E:\VMExport\VM01\Virtual Machines\xxx.vmcx"

# === 连接虚拟机 ===

# 通过VMConnect连接
vmconnect.exe localhost "VM01"

# 使用PowerShell Direct (无需网络)
Enter-PSSession -VMName "VM01" -Credential (Get-Credential)
```

---

## 高级功能

### Live Migration

```yaml
Live Migration说明:
  功能: 在线迁移正在运行的虚拟机
  要求:
    - Windows Server (Datacenter或Standard)
    - 故障转移集群或独立主机
    - 共享存储或SMB 3.0文件共享
    - 相同或兼容的CPU

配置Live Migration:
  PowerShell配置:
    ```powershell
    # 启用Live Migration
    Enable-VMMigration
    
    # 配置认证类型
    Set-VMMigrationNetwork 192.168.10.0 -Priority 1
    
    # 设置同时迁移数量
    Set-VMHost -MaximumVirtualMachineMigrations 2
    
    # 执行Live Migration
    Move-VM -Name "VM01" `
        -DestinationHost "Host02" `
        -IncludeStorage `
        -DestinationStoragePath "D:\Hyper-V\VMs"
    ```

Storage Migration:
  功能: 迁移虚拟机存储
  无需停机:
    ```powershell
    Move-VMStorage -VMName "VM01" `
        -DestinationStoragePath "E:\NewStorage"
    ```
```

### Replica容灾

```yaml
Hyper-V Replica说明:
  功能: 异步复制虚拟机到灾备站点
  用途: 灾难恢复
  支持: 
    - 独立主机
    - 故障转移集群

配置Replica:
  启用Replica:
    ```powershell
    # 在灾备主机上启用Replica
    Set-VMReplicationServer -ReplicationEnabled $true `
        -AllowedAuthenticationType Kerberos `
        -ReplicationAllowedFromAnyServer $true
    
    # 配置虚拟机复制
    Enable-VMReplication -VMName "VM01" `
        -ReplicaServerName "DR-Host" `
        -ReplicaServerPort 80 `
        -AuthenticationType Kerberos `
        -CompressionEnabled $true
    
    # 开始初始复制
    Start-VMInitialReplication -VMName "VM01"
    
    # 查看复制状态
    Get-VMReplication -VMName "VM01"
    ```

故障转移:
  测试故障转移:
    不影响生产，测试灾备可用性
  
  计划内故障转移:
    优雅切换到灾备站点
  
  非计划内故障转移:
    生产站点故障，紧急切换
```

### Shielded VMs

```yaml
Shielded VMs (屏蔽虚拟机):
  功能: 加密虚拟机，防止未授权访问
  保护:
    - 虚拟机磁盘加密
    - 虚拟机状态加密
    - 防止恶意管理员访问
  
  要求:
    - Windows Server Datacenter
    - Host Guardian Service (HGS)
    - 第2代虚拟机
    - 支持TPM的宿主机

  适用场景:
    ✅ 金融行业
    ✅ 医疗行业
    ✅ 政府机构
    ✅ 高安全性要求
```

---

## 性能优化

```yaml
CPU优化:
  CPU类型:
    - 暴露虚拟化扩展 (嵌套虚拟化)
    - NUMA拓扑
  
  配置:
    ```powershell
    # 启用嵌套虚拟化
    Set-VMProcessor -VMName "VM01" `
        -ExposeVirtualizationExtensions $true
    
    # 配置NUMA
    Set-VMProcessor -VMName "VM01" `
        -Maximum 100 `
        -Reserve 10
    ```

内存优化:
  动态内存:
    优势: 自动调整内存分配
    适用: 大多数场景
  
  静态内存:
    优势: 性能更稳定
    适用: 数据库等关键应用
  
  配置:
    ```powershell
    # 动态内存
    Set-VMMemory -VMName "VM01" `
        -DynamicMemoryEnabled $true `
        -MinimumBytes 2GB `
        -MaximumBytes 8GB `
        -Buffer 20
    ```

存储优化:
  磁盘类型: 固定大小 > 动态扩展
  
  存储QoS:
    ```powershell
    # 设置最小/最大IOPS
    Set-VMHardDiskDrive -VMName "VM01" `
        -Path "D:\VHDs\VM01.vhdx" `
        -MinimumIOPS 100 `
        -MaximumIOPS 1000
    ```

网络优化:
  SR-IOV:
    功能: 直接网卡访问
    性能: 接近物理网卡
    
    配置:
      ```powershell
      # 启用SR-IOV (交换机)
      Set-VMSwitch -Name "External-Switch" `
          -EnableIov $true
      
      # 为VM启用SR-IOV
      Set-VMNetworkAdapter -VMName "VM01" `
          -IovWeight 100
      ```
  
  VMQ (虚拟机队列):
    功能: 多队列网络处理
    性能: 提升多核性能
```

---

## 相关文档

- [操作系统与内核优化](01_操作系统与内核优化.md)
- [VMware ESXi安装与配置](02_VMware_ESXi安装与配置.md)
- [KVM安装与配置](03_KVM安装与配置.md)
- [BIOS/固件配置清单](../01_硬件规范/06_BIOS固件配置清单.md)
- [硬件兼容性清单](../01_硬件规范/07_硬件兼容性清单.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v3.0  
**状态**: ✅ 生产就绪
