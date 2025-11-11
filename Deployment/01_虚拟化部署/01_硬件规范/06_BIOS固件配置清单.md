# BIOS/固件配置清单

> **返回**: [硬件规范目录](README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [BIOS/固件配置清单](#bios固件配置清单)
  - [📋 目录](#-目录)
  - [核心虚拟化配置](#核心虚拟化配置)
    - [必须启用的虚拟化功能](#必须启用的虚拟化功能)
  - [性能优化配置](#性能优化配置)
    - [电源管理配置](#电源管理配置)
    - [CPU特性配置](#cpu特性配置)
  - [内存与NUMA配置](#内存与numa配置)
    - [内存配置](#内存配置)
  - [启动与安全配置](#启动与安全配置)
    - [启动配置](#启动配置)
    - [安全配置](#安全配置)
  - [品牌服务器配置路径](#品牌服务器配置路径)
    - [Dell服务器 (PowerEdge)](#dell服务器-poweredge)
    - [HPE服务器 (ProLiant)](#hpe服务器-proliant)
    - [Lenovo服务器 (ThinkSystem)](#lenovo服务器-thinksystem)
    - [华为服务器 (FusionServer)](#华为服务器-fusionserver)
    - [浪潮服务器 (Inspur)](#浪潮服务器-inspur)
  - [配置验证清单](#配置验证清单)
    - [部署前检查清单](#部署前检查清单)
    - [配置导出备份](#配置导出备份)
  - [注意事项](#注意事项)
    - [⚠️ 重要提示](#️-重要提示)
    - [📌 常见问题](#-常见问题)
  - [相关文档](#相关文档)

---

## 核心虚拟化配置

### 必须启用的虚拟化功能

```yaml
Intel平台:
  Intel VT-x (Intel Virtualization Technology):
    功能: 硬件辅助虚拟化
    状态: ✅ Enabled (必须)
    位置: Advanced → CPU Configuration
    说明: 不启用将无法运行虚拟机
    验证:
      - Linux: grep -E 'vmx' /proc/cpuinfo
      - Windows: systeminfo | findstr /C:"虚拟化"

  Intel VT-d (Intel Virtualization Technology for Directed I/O):
    功能: 设备直通 (PCI Passthrough)
    状态: ✅ Enabled (强烈推荐)
    位置: Advanced → CPU Configuration
    用途:
      - GPU直通
      - 网卡SR-IOV
      - 存储控制器直通
      - 提升I/O性能
    验证:
      - Linux: dmesg | grep -e DMAR -e IOMMU

  Intel EPT (Extended Page Tables):
    功能: 扩展页表，加速内存虚拟化
    状态: ✅ Enabled (通常自动)
    位置: 通常跟随VT-x自动启用
    优势: 大幅提升虚拟机内存性能

AMD平台:
  AMD-V (AMD Virtualization):
    功能: 硬件辅助虚拟化
    状态: ✅ Enabled (必须)
    位置: Advanced → CPU Configuration → SVM Mode
    说明: AMD的VT-x等价物
    验证:
      - Linux: grep -E 'svm' /proc/cpuinfo

  AMD-Vi (AMD I/O Virtualization):
    功能: 设备直通 (IOMMU)
    状态: ✅ Enabled (强烈推荐)
    位置: Advanced → CPU Configuration → IOMMU
    用途: 同Intel VT-d
    验证:
      - Linux: dmesg | grep AMD-Vi

  AMD RVI (Rapid Virtualization Indexing):
    功能: 嵌套页表 (NPT)
    状态: ✅ Enabled (通常自动)
    位置: 通常跟随AMD-V自动启用
    优势: 等同Intel EPT

国产CPU (海光/鲲鹏):
  海光 (Hygon):
    虚拟化技术: 基于AMD平台
    配置: 同AMD-V/AMD-Vi
    支持: 完整虚拟化扩展

  鲲鹏 (Kunpeng):
    虚拟化技术: ARM Virtualization Extensions
    配置: 通常默认启用
    支持: KVM、Docker、Kubernetes

配置验证脚本:
  Linux验证:
    ```bash
    #!/bin/bash
    echo "=== 虚拟化支持检测 ==="

    # 检测CPU虚拟化支持
    if grep -qE 'vmx|svm' /proc/cpuinfo; then
      echo "✅ CPU支持虚拟化"
      if grep -q vmx /proc/cpuinfo; then
        echo "  平台: Intel VT-x"
      elif grep -q svm /proc/cpuinfo; then
        echo "  平台: AMD-V"
      fi
    else
      echo "❌ CPU不支持虚拟化或未启用"
      exit 1
    fi

    # 检测IOMMU
    if dmesg | grep -qE 'DMAR|AMD-Vi'; then
      echo "✅ IOMMU已启用"
    else
      echo "⚠️  IOMMU未启用 (VT-d/AMD-Vi)"
    fi

    # 检测KVM模块
    if lsmod | grep -q kvm; then
      echo "✅ KVM模块已加载"
    else
      echo "❌ KVM模块未加载"
    fi
    ```

  ESXi验证:
    ```bash
    # 检查硬件虚拟化
    esxcli hardware cpu global get | grep -i virtualization

    # 检查IOMMU
    esxcli system settings kernel list -o iommuEnabled
    ```
```

---

## 性能优化配置

### 电源管理配置

```yaml
Power Management (电源管理):
  Performance模式配置:
    目标: 最大性能，禁用节能
    适用: 生产虚拟化环境

    配置项:
      Power Profile / Power Policy:
        设置: Maximum Performance / High Performance
        位置: Advanced → Power Management
        说明: 禁用CPU降频

      C-States (CPU空闲状态):
        设置: ❌ Disabled
        位置: Advanced → CPU Configuration → CPU Power Management
        原因: 避免CPU进入睡眠降低延迟
        影响: 增加功耗约5-10%，降低延迟50%+

      C1E (Enhanced Halt State):
        设置: ❌ Disabled
        位置: Advanced → CPU Configuration
        原因: 防止CPU降频

      Intel Turbo Boost / AMD Turbo Core:
        设置: ✅ Enabled
        位置: Advanced → CPU Configuration
        原因: 单核性能提升，短暂高负载加速
        提升: 单核性能提升10-40%

      Intel SpeedStep / AMD Cool'n'Quiet:
        设置: ❌ Disabled (性能优先)
        设置: ✅ Enabled (节能优先)
        位置: Advanced → CPU Configuration
        说明: 生产环境建议禁用

  Balanced模式配置:
    目标: 性能与节能平衡
    适用: 开发测试环境、负载不高场景

    配置项:
      Power Profile: Balanced
      C-States: ✅ Enabled (C1/C3)
      Turbo Boost: ✅ Enabled
      SpeedStep: ✅ Enabled

性能对比:
  Maximum Performance:
    延迟: 最低
    功耗: 最高
    适用: 生产环境

  Balanced:
    延迟: 适中
    功耗: 适中
    适用: 测试环境

  Power Saving:
    延迟: 最高
    功耗: 最低
    适用: ❌ 不推荐虚拟化
```

### CPU特性配置

```yaml
Hyper-Threading / SMT:
  功能: 超线程技术
  设置: ✅ Enabled (强烈推荐)
  位置: Advanced → CPU Configuration
  优势:
    - 逻辑核心翻倍
    - 提升多任务性能20-30%
    - 虚拟机密度提升
  注意:
    - 某些安全敏感场景可能禁用
    - 核心授权按物理核心计算

NUMA (Non-Uniform Memory Access):
  功能: 内存访问优化
  设置: ✅ Enabled (必须)
  位置: Advanced → Memory Configuration
  优势:
    - 降低内存访问延迟
    - 提升多路CPU性能
  ESXi NUMA优化:
    - 虚拟机vCPU不超过单NUMA节点
    - 例: 2路CPU，每路24核 → 虚拟机最大24vCPU

Hardware Prefetcher:
  功能: 硬件预取器
  设置: ✅ Enabled
  位置: Advanced → CPU Configuration
  优势: 提升缓存命中率

Adjacent Cache Line Prefetch:
  功能: 相邻缓存行预取
  设置: ✅ Enabled
  位置: Advanced → CPU Configuration
  优势: 顺序读取性能提升

Intel AES-NI:
  功能: 硬件AES加密加速
  设置: ✅ Enabled
  位置: Advanced → CPU Configuration
  优势: 加密性能提升10倍+
  用途: 全盘加密、VPN、TLS/SSL
```

---

## 内存与NUMA配置

### 内存配置

```yaml
Memory Configuration:
  ECC (Error Correcting Code):
    功能: 错误校验与纠正
    设置: ✅ Enabled (自动，使用ECC内存)
    说明: 生产环境必须使用ECC内存

  Memory Frequency:
    设置: Auto (自动最高频率)
    或: 手动设定 (3200MHz / 2933MHz)
    说明: 除非稳定性问题，否则使用Auto

  Memory Interleaving (内存交错):
    Node Interleaving:
      设置: ❌ Disabled (虚拟化推荐)
      位置: Advanced → Memory Configuration
      原因: 保持NUMA特性，优化性能

    Channel Interleaving:
      设置: ✅ Enabled
      位置: Advanced → Memory Configuration
      原因: 提升单NUMA节点内带宽

  Memory Patrol Scrubbing:
    功能: 内存巡检
    设置: ✅ Enabled
    频率: 24 hours
    说明: 定期扫描内存错误

NUMA优化:
  NUMA Nodes per Socket:
    设置: 根据CPU选择
    说明:
      - 单路CPU: 1个NUMA节点
      - 双路CPU: 2个NUMA节点
      - 某些EPYC: 每CPU多个NUMA节点

  Memory RAS:
    功能: 可靠性、可用性、可维护性
    设置: ✅ Enabled
    包括:
      - Demand/Patrol Scrub
      - SDDC (Single Device Data Correction)
```

---

## 启动与安全配置

### 启动配置

```yaml
Boot Configuration:
  Boot Mode:
    设置: UEFI (推荐)
    备选: Legacy BIOS (老系统)
    位置: Boot → Boot Mode
    优势:
      ✅ 支持>2TB磁盘
      ✅ 更快启动
      ✅ 更好安全性

  Secure Boot:
    设置: ❌ Disabled (虚拟化通常禁用)
    位置: Boot → Secure Boot
    原因:
      - ESXi定制镜像可能不支持
      - 第三方驱动签名问题
    注意: 高安全场景可考虑启用

  Boot Device Order:
    推荐顺序:
      1. Local HDD/SSD (系统盘)
      2. Network (PXE Boot, 批量部署用)
      3. USB/Virtual Media

PCIe配置:
  SR-IOV (Single Root I/O Virtualization):
    设置: ✅ Enabled
    位置: Advanced → PCIe Configuration
    用途:
      - 网卡虚拟化
      - 直接分配虚拟网卡给VM
      - 接近原生性能
    要求: 网卡支持SR-IOV

  ACS (Access Control Services):
    设置: ✅ Enabled
    位置: Advanced → PCIe Configuration
    用途: 隔离PCIe设备，支持直通

网络配置:
  Integrated NIC 1/2:
    设置: ✅ Enabled
    用途: 管理网络

  PXE Boot:
    设置: Enabled (需要批量部署)
    设置: Disabled (单机部署)
```

### 安全配置

```yaml
Security Settings:
  Intel TXT (Trusted Execution Technology):
    设置: 根据需求
    用途: 可信计算

  TPM (Trusted Platform Module):
    设置: ✅ Enabled (推荐)
    版本: TPM 2.0
    用途:
      - 全盘加密
      - vTPM for VM

  BIOS/Administrator Password:
    设置: ✅ 必须设置
    强度: 复杂密码

  Boot Guard:
    设置: ✅ Enabled (支持的话)
    功能: 启动安全验证
```

---

## 品牌服务器配置路径

### Dell服务器 (PowerEdge)

```yaml
进入BIOS:
  方法: 开机时按 F2
  iDRAC: 按 F10 (远程管理)

关键配置路径:
  1. System Setup → System BIOS → Processor Settings
     操作:
       - Intel Virtualization Technology: ✅ Enabled
       - Intel VT for Directed I/O: ✅ Enabled
       - Logical Processor (Hyper-Threading): ✅ Enabled

  2. System Setup → System BIOS → System Profile Settings
     操作:
       - System Profile: Performance (性能优先)
       - System Profile: Performance Per Watt (DAPC) (节能)

  3. System Setup → System BIOS → Memory Settings
     操作:
       - Node Interleaving: ❌ Disabled
       - System Memory Testing: Enabled

  4. System Setup → Device Settings → Network Devices
     操作:
       - 配置网卡，启用PXE (如需)

  5. iDRAC Settings → Network
     操作:
       - 配置远程管理IP
       - 启用IPMI

快捷配置:
  System Profile预设:
    - Performance: 最大性能
    - Performance Per Watt (DAPC): 动态节能
    - Performance Per Watt (OS): 操作系统控制
    - 推荐: Performance (生产虚拟化)
```

### HPE服务器 (ProLiant)

```yaml
进入BIOS:
  方法: 开机时按 F9
  iLO: 按 F8 (远程管理)

关键配置路径:
  1. System Options → Processor Options
     操作:
       - Intel Virtualization Technology: ✅ Enabled
       - Intel VT-d: ✅ Enabled
       - Intel Hyper-Threading: ✅ Enabled

  2. System Options → BIOS/Platform Configuration (RBSU)
     操作:
       - Workload Profile: Virtualization - Max Performance
       - 或: General Power Efficient (节能)

  3. Power Management → Advanced Power Options
     操作:
       - Power Regulator: HP Static High Performance Mode
       - 或: HP Dynamic Power Savings Mode (节能)

  4. System Options → Memory Options
     操作:
       - Node Interleaving: ❌ Disabled
       - Channel Interleaving: ✅ Enabled

  5. Network Options → Network Boot Options
     操作:
       - 配置PXE启动顺序

Workload Profile推荐:
  生产虚拟化:
    - Virtualization - Max Performance

  混合负载:
    - General Peak Frequency Compute

  节能:
    - General Power Efficient
```

### Lenovo服务器 (ThinkSystem)

```yaml
进入BIOS:
  方法: 开机时按 F1
  XCC: 通过Web访问 (远程管理)

关键配置路径:
  1. System Settings → Processors
     操作:
       - Intel Virtualization Technology: ✅ Enabled
       - Intel VT-d: ✅ Enabled
       - Hyper-Threading: ✅ Enabled

  2. System Settings → Power
     操作:
       - Operating Mode: Maximum Performance
       - 或: Custom Mode (自定义)

  3. System Settings → Memory
     操作:
       - Memory Interleaving: Auto

  4. System Settings → Devices and I/O Ports
     操作:
       - SR-IOV Support: ✅ Enabled

Operating Mode推荐:
  - Maximum Performance: 最大性能
  - Efficiency: 节能模式
  - Custom: 自定义 (建议选Maximum Performance)
```

### 华为服务器 (FusionServer)

```yaml
进入BIOS:
  方法: 开机时按 Delete
  iBMC: 通过Web访问 (远程管理)

关键配置路径:
  1. Advanced → Processor Configuration
     操作:
       - Intel Virtualization Technology: ✅ Enabled
       - Intel VT-d: ✅ Enabled
       - Hyper-Threading: ✅ Enabled

  2. Advanced → Power Configuration
     操作:
       - Power Policy: Performance
       - 或: Custom (自定义)

  3. Advanced → Memory Configuration
     操作:
       - Node Interleaving: ❌ Disabled

  4. Advanced → PCIe Configuration
     操作:
       - SR-IOV Support: ✅ Enabled

Power Policy推荐:
  - Performance: 最大性能 (生产推荐)
  - Balanced: 平衡模式
  - Power Saving: 节能模式
```

### 浪潮服务器 (Inspur)

```yaml
进入BIOS:
  方法: 开机时按 Delete 或 F2
  BMC: 通过Web访问

关键配置路径:
  1. Advanced → CPU Configuration
     操作:
       - Intel Virtualization Technology: ✅ Enabled
       - VT-d: ✅ Enabled
       - Hyper-Threading: ✅ Enabled

  2. Advanced → Power & Performance
     操作:
       - CPU Power Mode: Performance Mode

  3. Advanced → Chipset Configuration → Memory Configuration
     操作:
       - NUMA: ✅ Enabled
```

---

## 配置验证清单

### 部署前检查清单

```yaml
虚拟化必备:
  ☐ Intel VT-x / AMD-V: Enabled
  ☐ Intel VT-d / AMD-Vi: Enabled
  ☐ Hyper-Threading: Enabled
  ☐ NUMA: Enabled

性能优化:
  ☐ Power Policy: Maximum Performance
  ☐ C-States: Disabled
  ☐ Turbo Boost: Enabled
  ☐ SpeedStep/Cool'n'Quiet: Disabled

内存:
  ☐ ECC: Enabled (使用ECC内存)
  ☐ Node Interleaving: Disabled
  ☐ Channel Interleaving: Enabled

启动:
  ☐ Boot Mode: UEFI
  ☐ Secure Boot: Disabled (或根据需求)
  ☐ SR-IOV: Enabled

安全:
  ☐ BIOS Password: 已设置
  ☐ TPM: Enabled (推荐)

远程管理:
  ☐ iDRAC/iLO/XCC/iBMC: 已配置IP
  ☐ 远程管理网络: 已连接
```

### 配置导出备份

```yaml
Dell:
  方法: iDRAC → System Setup → Export System Configuration
  格式: XML文件

HPE:
  方法: iLO → System Information → Export Configuration
  格式: JSON文件

Lenovo:
  方法: XCC → Configuration → Export Configuration
  格式: XML文件

华为:
  方法: iBMC → Configuration → Export Configuration
  格式: XML文件

建议:
  ✅ 部署后立即导出配置
  ✅ 版本控制保存
  ✅ 批量部署时导入配置
```

---

## 注意事项

### ⚠️ 重要提示

1. **虚拟化必须启用**: VT-x/AMD-V和VT-d/AMD-Vi必须启用
2. **性能优先**: 生产环境选择Maximum Performance模式
3. **NUMA优化**: 禁用Node Interleaving以保持NUMA特性
4. **UEFI首选**: 新部署优先选择UEFI启动
5. **配置备份**: 配置完成后务必导出备份
6. **固件升级**: 部署前升级到最新稳定BIOS/固件

### 📌 常见问题

**Q: Secure Boot要不要启用？**
A: 虚拟化环境通常禁用，避免兼容性问题

**Q: C-States一定要禁用吗？**
A: 生产环境建议禁用，测试环境可启用节能

**Q: NUMA怎么配置？**
A: 启用NUMA，禁用Node Interleaving

**Q: SR-IOV是什么？**
A: 网卡虚拟化技术，提升网络性能，必须启用

---

## 相关文档

- [CPU处理器选型](01_CPU处理器选型.md)
- [内存选型指南](02_内存选型.md)
- [硬件兼容性清单](07_硬件兼容性清单.md)
- [ESXi安装配置](../02_软件安装/02_VMware_ESXi安装与配置.md)

---

**更新时间**: 2025-10-19
**文档版本**: v3.0
**状态**: ✅ 生产就绪
