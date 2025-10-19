# KVM安装与配置

> **返回**: [软件安装目录](README.md) | [虚拟化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [KVM安装与配置](#kvm安装与配置)
  - [📋 目录](#-目录)
  - [KVM概述](#kvm概述)
    - [KVM架构](#kvm架构)
    - [KVM优势](#kvm优势)
    - [适用场景](#适用场景)
  - [环境准备](#环境准备)
    - [硬件要求](#硬件要求)
    - [系统要求](#系统要求)
    - [检查虚拟化支持](#检查虚拟化支持)
  - [KVM安装](#kvm安装)
    - [Ubuntu安装](#ubuntu安装)
    - [Rocky Linux安装](#rocky-linux安装)
    - [验证安装](#验证安装)
  - [网络配置](#网络配置)
    - [桥接网络 (Bridge)](#桥接网络-bridge)
    - [NAT网络](#nat网络)
    - [网络管理](#网络管理)
  - [存储配置](#存储配置)
    - [存储池管理](#存储池管理)
    - [存储卷管理](#存储卷管理)
    - [存储类型](#存储类型)
  - [虚拟机管理](#虚拟机管理)
    - [使用virt-install创建](#使用virt-install创建)
    - [使用virsh管理](#使用virsh管理)
    - [使用virt-manager (GUI)](#使用virt-manager-gui)
  - [虚拟机模板](#虚拟机模板)
    - [创建模板](#创建模板)
    - [克隆虚拟机](#克隆虚拟机)
    - [Cloud-init配置](#cloud-init配置)
  - [性能优化](#性能优化)
  - [相关文档](#相关文档)

---

## KVM概述

### KVM架构

```yaml
KVM (Kernel-based Virtual Machine):
  说明:
    - 基于Linux内核的虚拟化技术
    - 将Linux转换为Type-1 Hypervisor
    - 内核模块提供虚拟化支持
    - 开源免费
  
  核心组件:
    KVM内核模块:
      - kvm.ko: KVM核心模块
      - kvm-intel.ko: Intel CPU支持
      - kvm-amd.ko: AMD CPU支持
      功能: 提供CPU和内存虚拟化
    
    QEMU:
      版本: 6.2+ (推荐7.0+)
      功能: 
        - 设备模拟
        - I/O虚拟化
        - VM进程管理
    
    libvirt:
      版本: 8.0+
      功能:
        - 虚拟化管理API
        - 统一管理接口
        - 支持多种Hypervisor
      组件:
        - libvirtd: 后台服务
        - virsh: 命令行工具
        - virt-manager: 图形界面
  
  架构图:
    用户空间:
      [virt-manager] [virsh] [OpenStack]
            ↓           ↓         ↓
         [libvirt API]
            ↓
      [QEMU进程1] [QEMU进程2] ...
            ↓           ↓
    内核空间:
      [KVM模块 (kvm.ko, kvm-intel.ko)]
            ↓
      [Linux Kernel]
            ↓
    硬件层:
      [CPU (VT-x/AMD-V)] [内存] [存储] [网络]
```

### KVM优势

```yaml
优势:
  开源免费:
    ✅ 完全开源 (GPL许可)
    ✅ 无许可费用
    ✅ 社区支持活跃
    ✅ 企业级发行版支持 (RHEL)
  
  性能优秀:
    ✅ 接近裸机性能
    ✅ 内核级虚拟化
    ✅ 硬件辅助虚拟化
    ✅ 优化的I/O性能
  
  灵活性高:
    ✅ 支持多种操作系统
    ✅ 支持多种存储后端
    ✅ 支持多种网络模式
    ✅ 可与OpenStack集成
  
  管理便捷:
    ✅ 统一的libvirt API
    ✅ 丰富的管理工具
    ✅ 支持自动化脚本
    ✅ 云平台集成良好

劣势:
  ⚠️ 管理界面不如VMware友好
  ⚠️ 需要Linux知识
  ⚠️ 企业级功能需要额外工具
  ⚠️ 文档相对分散

对比VMware:
  性能: KVM ≈ VMware (相当)
  功能: VMware > KVM (VMware功能更丰富)
  易用性: VMware > KVM (VMware界面更友好)
  成本: KVM > VMware (KVM免费)
  开源: KVM > VMware (KVM开源)
```

### 适用场景

```yaml
推荐场景:
  开发测试环境:
    ✅ 成本敏感
    ✅ 灵活性要求高
    ✅ 需要快速部署
  
  私有云平台:
    ✅ OpenStack底层
    ✅ 大规模部署
    ✅ 自动化需求
  
  容器宿主机:
    ✅ Kubernetes节点
    ✅ 容器化环境
    ✅ CI/CD平台
  
  中小型生产环境:
    ✅ 预算有限
    ✅ 有Linux运维能力
    ✅ 不需要高级功能

不推荐场景:
  ❌ 对管理界面要求高
  ❌ 缺乏Linux运维经验
  ❌ 需要企业级支持（除非购买RHEV）
  ❌ 需要复杂的虚拟化功能
```

---

## 环境准备

### 硬件要求

```yaml
最低配置:
  CPU:
    核心: 2核心 (4线程推荐)
    频率: 2.0 GHz+
    要求: 支持VT-x (Intel) 或 AMD-V (AMD)
  
  内存:
    最小: 4GB
    推荐: 8GB+
    说明: 宿主机2GB + 每个VM 1-2GB
  
  存储:
    系统盘: 50GB+
    VM磁盘: 根据需求
    推荐: SSD (提升VM性能)
  
  网络:
    最小: 1Gbps
    推荐: 10Gbps (生产环境)

推荐配置:
  CPU: 
    Intel Xeon E5 / Gold系列
    AMD EPYC系列
    核心: 16核心+
  
  内存: 64GB+
  
  存储:
    系统: 500GB SSD
    VM存储: 2TB+ NVMe SSD
  
  网络: 10Gbps x2 (双上行)

支持的CPU:
  Intel:
    ✅ 支持VT-x (虚拟化技术)
    ✅ 支持VT-d (I/O虚拟化)
    ✅ 支持EPT (扩展页表)
  
  AMD:
    ✅ 支持AMD-V (虚拟化技术)
    ✅ 支持AMD-Vi (I/O虚拟化)
    ✅ 支持RVI (快速虚拟化索引)
```

### 系统要求

```yaml
支持的Linux发行版:
  Ubuntu Server:
    推荐版本: 22.04 LTS, 20.04 LTS
    内核: 5.15+, 5.4+
    包管理: apt
    支持周期: 5年
  
  Red Hat Enterprise Linux (RHEL):
    推荐版本: 9.3, 8.9
    内核: 5.14+, 4.18+
    包管理: dnf
    支持周期: 10年
    说明: 商业支持，需订阅
  
  Rocky Linux:
    推荐版本: 9.3, 8.9
    内核: 5.14+, 4.18+
    包管理: dnf
    说明: RHEL兼容，免费
  
  CentOS Stream:
    推荐版本: 9
    内核: 5.14+
    包管理: dnf
    说明: 滚动更新
  
  Debian:
    推荐版本: 12 (Bookworm)
    内核: 6.1
    包管理: apt
    说明: 极度稳定
  
  openEuler (国产):
    推荐版本: 22.03 LTS SP3
    内核: 5.10+
    包管理: dnf
    说明: 华为支持

内核要求:
  最低内核: 5.4 (Ubuntu 20.04)
  推荐内核: 5.15+ (Ubuntu 22.04)
  最新内核: 6.1+ (Debian 12)
  
  必须特性:
    ✅ KVM支持
    ✅ TUN/TAP支持
    ✅ Bridge支持
    ✅ vhost-net支持
```

### 检查虚拟化支持

```bash
#!/bin/bash
# 检查系统是否支持KVM虚拟化

echo "========================================="
echo "  KVM虚拟化支持检测"
echo "========================================="

# 1. 检查CPU虚拟化支持
echo ""
echo "1. 检查CPU虚拟化支持..."
if grep -E '(vmx|svm)' /proc/cpuinfo > /dev/null 2>&1; then
    if grep -q vmx /proc/cpuinfo; then
        echo "✅ CPU支持硬件虚拟化 (Intel VT-x)"
    elif grep -q svm /proc/cpuinfo; then
        echo "✅ CPU支持硬件虚拟化 (AMD-V)"
    fi
else
    echo "❌ CPU不支持硬件虚拟化"
    echo "   请检查BIOS设置，启用 Intel VT-x 或 AMD-V"
    exit 1
fi

# 2. 检查内核版本
echo ""
echo "2. 检查内核版本..."
KERNEL_VERSION=$(uname -r)
KERNEL_MAJOR=$(echo $KERNEL_VERSION | cut -d. -f1)
KERNEL_MINOR=$(echo $KERNEL_VERSION | cut -d. -f2)
echo "   当前内核: $KERNEL_VERSION"

if [ $KERNEL_MAJOR -ge 5 ] && [ $KERNEL_MINOR -ge 4 ]; then
    echo "✅ 内核版本满足要求 (>=5.4)"
else
    echo "⚠️  内核版本偏低，推荐升级到5.15+"
fi

# 3. 检查KVM模块
echo ""
echo "3. 检查KVM内核模块..."
if lsmod | grep -q kvm; then
    echo "✅ KVM模块已加载"
    lsmod | grep kvm
else
    echo "⚠️  KVM模块未加载"
    echo "   尝试加载模块..."
    
    if grep -q vmx /proc/cpuinfo; then
        modprobe kvm
        modprobe kvm_intel
    elif grep -q svm /proc/cpuinfo; then
        modprobe kvm
        modprobe kvm_amd
    fi
    
    if lsmod | grep -q kvm; then
        echo "✅ KVM模块加载成功"
    else
        echo "❌ KVM模块加载失败"
        exit 1
    fi
fi

# 4. 检查KVM设备
echo ""
echo "4. 检查KVM设备文件..."
if [ -e /dev/kvm ]; then
    echo "✅ /dev/kvm 存在"
    ls -l /dev/kvm
else
    echo "❌ /dev/kvm 不存在"
    exit 1
fi

# 5. 检查CPU标志
echo ""
echo "5. 检查CPU特性标志..."
CPU_FLAGS=$(cat /proc/cpuinfo | grep flags | head -n 1)
echo "   检查重要标志:"

if echo "$CPU_FLAGS" | grep -q vmx; then
    echo "   ✅ vmx (Intel VT-x)"
fi

if echo "$CPU_FLAGS" | grep -q svm; then
    echo "   ✅ svm (AMD-V)"
fi

if echo "$CPU_FLAGS" | grep -q ept; then
    echo "   ✅ ept (扩展页表)"
fi

if echo "$CPU_FLAGS" | grep -q vpid; then
    echo "   ✅ vpid (虚拟处理器ID)"
fi

# 6. 检查可用内存
echo ""
echo "6. 检查系统内存..."
TOTAL_MEM=$(free -g | grep Mem: | awk '{print $2}')
AVAIL_MEM=$(free -g | grep Mem: | awk '{print $7}')
echo "   总内存: ${TOTAL_MEM}GB"
echo "   可用内存: ${AVAIL_MEM}GB"

if [ $TOTAL_MEM -ge 8 ]; then
    echo "✅ 内存充足 (>=8GB)"
elif [ $TOTAL_MEM -ge 4 ]; then
    echo "⚠️  内存较少 (4-8GB)，建议升级"
else
    echo "❌ 内存不足 (<4GB)"
fi

# 总结
echo ""
echo "========================================="
echo "  检测完成"
echo "========================================="
echo "系统支持KVM虚拟化！"
```

---

## KVM安装

### Ubuntu安装

```bash
#!/bin/bash
# KVM完整安装脚本 - Ubuntu 22.04

set -e

echo "========================================="
echo "  KVM安装脚本 - Ubuntu 22.04"
echo "========================================="

# 1. 更新系统
echo ""
echo "步骤1: 更新系统..."
apt update
apt upgrade -y

# 2. 检查虚拟化支持
echo ""
echo "步骤2: 检查虚拟化支持..."
if grep -E '(vmx|svm)' /proc/cpuinfo > /dev/null; then
    echo "✅ CPU支持硬件虚拟化"
else
    echo "❌ CPU不支持硬件虚拟化"
    echo "请在BIOS中启用 Intel VT-x 或 AMD-V"
    exit 1
fi

# 3. 安装KVM和相关软件包
echo ""
echo "步骤3: 安装KVM软件包..."
apt install -y \
    qemu-kvm \
    libvirt-daemon-system \
    libvirt-clients \
    libvirt-daemon \
    bridge-utils \
    virtinst \
    virt-manager \
    virt-viewer \
    cpu-checker \
    libguestfs-tools \
    libosinfo-bin \
    genisoimage

# 软件包说明:
# qemu-kvm: QEMU虚拟机模拟器 + KVM加速
# libvirt-daemon-system: libvirt守护进程
# libvirt-clients: virsh等客户端工具
# bridge-utils: 网桥管理工具
# virtinst: virt-install虚拟机安装工具
# virt-manager: 图形化管理界面
# virt-viewer: VNC/SPICE查看器
# cpu-checker: CPU虚拟化检查工具 (kvm-ok)
# libguestfs-tools: 虚拟机磁盘工具 (virt-sysprep等)
# libosinfo-bin: OS信息数据库 (osinfo-query)
# genisoimage: ISO镜像创建工具

# 4. 验证安装
echo ""
echo "步骤4: 验证KVM安装..."
kvm-ok

# 5. 启动libvirt服务
echo ""
echo "步骤5: 启动libvirt服务..."
systemctl enable libvirtd
systemctl start libvirtd
systemctl status libvirtd --no-pager

# 6. 将当前用户添加到libvirt和kvm组
echo ""
echo "步骤6: 配置用户权限..."
CURRENT_USER=${SUDO_USER:-$USER}
usermod -aG libvirt $CURRENT_USER
usermod -aG kvm $CURRENT_USER
echo "✅ 用户 $CURRENT_USER 已添加到 libvirt 和 kvm 组"
echo "⚠️  请注销并重新登录以使组权限生效"

# 7. 验证libvirt
echo ""
echo "步骤7: 验证libvirt..."
virsh version
virsh list --all

# 8. 检查默认网络
echo ""
echo "步骤8: 检查默认网络..."
virsh net-list --all

# 如果default网络不存在或未启动，启动它
if ! virsh net-list --all | grep -q "default.*active"; then
    echo "启动默认网络..."
    virsh net-start default 2>/dev/null || true
    virsh net-autostart default 2>/dev/null || true
fi

# 9. 创建虚拟机存储目录
echo ""
echo "步骤9: 创建存储目录..."
mkdir -p /var/lib/libvirt/images
mkdir -p /var/lib/libvirt/iso
chmod 755 /var/lib/libvirt/images
chmod 755 /var/lib/libvirt/iso
echo "✅ 存储目录已创建:"
echo "   VM磁盘: /var/lib/libvirt/images"
echo "   ISO镜像: /var/lib/libvirt/iso"

# 10. 显示系统信息
echo ""
echo "步骤10: 系统信息..."
echo "内核版本: $(uname -r)"
echo "QEMU版本: $(qemu-system-x86_64 --version | head -n 1)"
echo "libvirt版本: $(virsh version | grep 'libvirt' | awk '{print $3}')"

# 完成
echo ""
echo "========================================="
echo "  ✅ KVM安装完成！"
echo "========================================="
echo ""
echo "下一步操作:"
echo "  1. 注销并重新登录 (使组权限生效)"
echo "  2. 运行: virsh list --all (测试virsh命令)"
echo "  3. 运行: virt-manager (启动图形界面)"
echo "  4. 下载ISO镜像到: /var/lib/libvirt/iso/"
echo "  5. 创建虚拟机"
echo ""
```

### Rocky Linux安装

```bash
#!/bin/bash
# KVM完整安装脚本 - Rocky Linux 9

set -e

echo "========================================="
echo "  KVM安装脚本 - Rocky Linux 9"
echo "========================================="

# 1. 更新系统
echo ""
echo "步骤1: 更新系统..."
dnf update -y

# 2. 检查虚拟化支持
echo ""
echo "步骤2: 检查虚拟化支持..."
if grep -E '(vmx|svm)' /proc/cpuinfo > /dev/null; then
    echo "✅ CPU支持硬件虚拟化"
else
    echo "❌ CPU不支持硬件虚拟化"
    exit 1
fi

# 3. 安装虚拟化组
echo ""
echo "步骤3: 安装虚拟化软件组..."
dnf groupinstall -y "Virtualization Host"
dnf install -y \
    virt-install \
    virt-viewer \
    libguestfs-tools

# 4. 启动libvirtd
echo ""
echo "步骤4: 启动libvirt服务..."
systemctl enable libvirtd
systemctl start libvirtd
systemctl status libvirtd --no-pager

# 5. 配置用户权限
echo ""
echo "步骤5: 配置用户权限..."
CURRENT_USER=${SUDO_USER:-$USER}
usermod -aG libvirt $CURRENT_USER
echo "✅ 用户 $CURRENT_USER 已添加到 libvirt 组"

# 6. 验证安装
echo ""
echo "步骤6: 验证安装..."
virsh version
virsh list --all

# 7. 配置防火墙
echo ""
echo "步骤7: 配置防火墙..."
firewall-cmd --permanent --add-service=libvirt
firewall-cmd --reload
echo "✅ 防火墙规则已添加"

# 8. 创建存储目录
echo ""
echo "步骤8: 创建存储目录..."
mkdir -p /var/lib/libvirt/images
mkdir -p /var/lib/libvirt/iso
chmod 755 /var/lib/libvirt/images
chmod 755 /var/lib/libvirt/iso

# 完成
echo ""
echo "========================================="
echo "  ✅ KVM安装完成！"
echo "========================================="
```

### 验证安装

```bash
# 验证KVM安装和配置

# 1. 检查KVM模块
echo "=== KVM模块状态 ==="
lsmod | grep kvm
# 应显示: kvm, kvm_intel 或 kvm_amd

# 2. 检查libvirt服务
echo "=== libvirt服务状态 ==="
systemctl status libvirtd

# 3. 检查virsh版本
echo "=== virsh版本 ==="
virsh version

# 4. 列出虚拟机
echo "=== 虚拟机列表 ==="
virsh list --all

# 5. 列出网络
echo "=== 网络列表 ==="
virsh net-list --all

# 6. 列出存储池
echo "=== 存储池列表 ==="
virsh pool-list --all

# 7. 检查QEMU版本
echo "=== QEMU版本 ==="
qemu-system-x86_64 --version

# 8. 测试权限
echo "=== 测试用户权限 ==="
groups
# 应包含: libvirt, kvm

# 9. 检查/dev/kvm
echo "=== KVM设备 ==="
ls -l /dev/kvm

# 10. 查看主机信息
echo "=== 主机虚拟化能力 ==="
virsh capabilities | grep -A 5 '<guest>'
```

---

## 网络配置

### 桥接网络 (Bridge)

```yaml
桥接网络说明:
  用途: VM直接连接到物理网络
  优势:
    ✅ VM获得与宿主机同一网段IP
    ✅ VM可被外部网络直接访问
    ✅ 性能接近物理网络
  
  劣势:
    ⚠️ 需要额外IP地址
    ⚠️ 需要修改宿主机网络配置
```

**Ubuntu配置桥接网络 (Netplan)**:

```bash
#!/bin/bash
# Ubuntu 22.04 桥接网络配置

# 1. 备份原配置
cp /etc/netplan/00-installer-config.yaml /etc/netplan/00-installer-config.yaml.bak

# 2. 创建新配置
cat > /etc/netplan/01-netcfg.yaml <<EOF
network:
  version: 2
  renderer: networkd
  
  ethernets:
    eno1:                    # 物理网卡名称，使用 ip a 查看
      dhcp4: false
      dhcp6: false
  
  bridges:
    br0:
      interfaces: [eno1]
      addresses:
        - 192.168.1.150/24    # 宿主机IP
      routes:
        - to: default
          via: 192.168.1.1    # 网关
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
      parameters:
        stp: false            # 禁用生成树协议
        forward-delay: 0      # 禁用转发延迟
      dhcp4: false
      dhcp6: false
EOF

# 3. 测试配置
netplan try

# 4. 应用配置 (如果测试成功)
netplan apply

# 5. 验证
ip addr show br0
brctl show

# 6. 创建libvirt网络定义
cat > /tmp/br0.xml <<EOF
<network>
  <name>br0</name>
  <forward mode='bridge'/>
  <bridge name='br0'/>
</network>
EOF

# 7. 定义并启动网络
virsh net-define /tmp/br0.xml
virsh net-start br0
virsh net-autostart br0

# 8. 验证
virsh net-list --all

echo "✅ 桥接网络配置完成"
echo "网桥名称: br0"
echo "宿主机IP: 192.168.1.150"
```

**Rocky Linux配置桥接网络 (NetworkManager)**:

```bash
#!/bin/bash
# Rocky Linux 9 桥接网络配置

PHYSICAL_IF="eno1"        # 物理网卡
BRIDGE_NAME="br0"
HOST_IP="192.168.1.150"
GATEWAY="192.168.1.1"

# 1. 创建网桥
nmcli connection add type bridge \
    con-name $BRIDGE_NAME \
    ifname $BRIDGE_NAME \
    ipv4.addresses ${HOST_IP}/24 \
    ipv4.gateway $GATEWAY \
    ipv4.dns "8.8.8.8 8.8.4.4" \
    ipv4.method manual

# 2. 将物理网卡添加到网桥
nmcli connection add type ethernet \
    con-name ${BRIDGE_NAME}-slave \
    ifname $PHYSICAL_IF \
    master $BRIDGE_NAME

# 3. 启动网桥
nmcli connection up $BRIDGE_NAME
nmcli connection up ${BRIDGE_NAME}-slave

# 4. 禁用原物理网卡连接
nmcli connection down $PHYSICAL_IF

# 5. 验证
ip addr show $BRIDGE_NAME
bridge link

# 6. 创建libvirt网络
cat > /tmp/br0.xml <<EOF
<network>
  <name>br0</name>
  <forward mode='bridge'/>
  <bridge name='br0'/>
</network>
EOF

virsh net-define /tmp/br0.xml
virsh net-start br0
virsh net-autostart br0

echo "✅ 桥接网络配置完成"
```

### NAT网络

```yaml
NAT网络说明:
  用途: VM通过宿主机NAT访问外网
  优势:
    ✅ 无需额外IP地址
    ✅ VM自动分配IP (DHCP)
    ✅ 配置简单
  
  劣势:
    ⚠️ 外部网络无法直接访问VM
    ⚠️ 需要端口转发才能从外部访问

默认NAT网络:
  libvirt自动创建default网络
  网络名称: default
  网络类型: NAT
  IP范围: 192.168.122.0/24
  DHCP范围: 192.168.122.2 - 192.168.122.254
  网关: 192.168.122.1 (宿主机)
```

**查看和管理默认网络**:

```bash
# 查看网络列表
virsh net-list --all

# 查看default网络详细信息
virsh net-dumpxml default

# 启动default网络
virsh net-start default

# 设置开机自启
virsh net-autostart default

# 查看DHCP租约
virsh net-dhcp-leases default
```

**创建自定义NAT网络**:

```bash
# 创建自定义NAT网络配置
cat > /tmp/nat-network.xml <<EOF
<network>
  <name>custom-nat</name>
  <forward mode='nat'>
    <nat>
      <port start='1024' end='65535'/>
    </nat>
  </forward>
  <bridge name='virbr1' stp='on' delay='0'/>
  <ip address='192.168.100.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.100.100' end='192.168.100.200'/>
    </dhcp>
  </ip>
</network>
EOF

# 定义网络
virsh net-define /tmp/nat-network.xml

# 启动网络
virsh net-start custom-nat

# 设置开机自启
virsh net-autostart custom-nat

# 验证
virsh net-list --all
```

### 网络管理

```bash
# 网络管理常用命令

# 列出所有网络
virsh net-list --all

# 查看网络详细信息
virsh net-info default
virsh net-dumpxml default

# 启动/停止网络
virsh net-start default
virsh net-destroy default

# 删除网络
virsh net-undefine custom-nat

# 查看DHCP租约
virsh net-dhcp-leases default

# 编辑网络配置
virsh net-edit default

# 查看网络接口
virsh domiflist vm-name

# 查看网桥
brctl show
ip link show type bridge
```

---

## 存储配置

### 存储池管理

```yaml
存储池类型:
  dir (目录):
    说明: 使用本地目录存储
    路径: /var/lib/libvirt/images (默认)
    格式: qcow2, raw
    用途: 最常用，简单直接
  
  lvm (LVM):
    说明: 使用LVM逻辑卷
    优势: 快照支持，性能好
    用途: 生产环境
  
  nfs:
    说明: NFS网络存储
    优势: 共享存储，支持迁移
    用途: 多主机环境
  
  iscsi:
    说明: iSCSI存储
    优势: 块级存储，高性能
    用途: 企业环境
```

**创建目录存储池**:

```bash
#!/bin/bash
# 创建目录存储池

POOL_NAME="vm-storage"
POOL_PATH="/data/kvm/vms"

# 1. 创建目录
mkdir -p $POOL_PATH

# 2. 定义存储池
virsh pool-define-as $POOL_NAME dir - - - - $POOL_PATH

# 3. 构建存储池
virsh pool-build $POOL_NAME

# 4. 启动存储池
virsh pool-start $POOL_NAME

# 5. 设置开机自启
virsh pool-autostart $POOL_NAME

# 6. 验证
virsh pool-list --all
virsh pool-info $POOL_NAME

echo "✅ 存储池创建完成: $POOL_NAME"
```

**创建NFS存储池**:

```bash
#!/bin/bash
# 创建NFS存储池

POOL_NAME="nfs-storage"
NFS_SERVER="192.168.2.10"
NFS_PATH="/export/vms"
MOUNT_PATH="/mnt/nfs-vms"

# 1. 安装NFS客户端
apt install -y nfs-common  # Ubuntu
# dnf install -y nfs-utils  # Rocky Linux

# 2. 创建挂载点
mkdir -p $MOUNT_PATH

# 3. 测试挂载
mount -t nfs ${NFS_SERVER}:${NFS_PATH} $MOUNT_PATH
df -h $MOUNT_PATH

# 4. 卸载 (libvirt会自动挂载)
umount $MOUNT_PATH

# 5. 定义NFS存储池
virsh pool-define-as $POOL_NAME netfs \
    --source-host $NFS_SERVER \
    --source-path $NFS_PATH \
    --target $MOUNT_PATH

# 6. 启动存储池
virsh pool-start $POOL_NAME
virsh pool-autostart $POOL_NAME

# 7. 验证
virsh pool-info $POOL_NAME

echo "✅ NFS存储池创建完成"
```

**存储池管理命令**:

```bash
# 列出存储池
virsh pool-list --all

# 查看存储池信息
virsh pool-info default

# 查看存储池详细配置
virsh pool-dumpxml default

# 刷新存储池 (扫描新卷)
virsh pool-refresh default

# 删除存储池
virsh pool-destroy pool-name
virsh pool-undefine pool-name

# 查看存储池路径
virsh pool-dumpxml default | grep '<path>'
```

### 存储卷管理

```bash
# 创建存储卷 (虚拟磁盘)

# 方法1: 使用virsh
virsh vol-create-as default \
    vm01-disk1.qcow2 \
    20G \
    --format qcow2

# 方法2: 使用qemu-img (更灵活)
qemu-img create -f qcow2 \
    /var/lib/libvirt/images/vm01-disk1.qcow2 \
    20G

# 创建预分配磁盘 (性能更好)
qemu-img create -f qcow2 \
    -o preallocation=metadata \
    /var/lib/libvirt/images/vm01-disk2.qcow2 \
    50G

# 列出存储卷
virsh vol-list default

# 查看存储卷信息
virsh vol-info --pool default vm01-disk1.qcow2
qemu-img info /var/lib/libvirt/images/vm01-disk1.qcow2

# 删除存储卷
virsh vol-delete --pool default vm01-disk1.qcow2

# 克隆存储卷
virsh vol-clone --pool default \
    source-disk.qcow2 \
    clone-disk.qcow2

# 调整存储卷大小
qemu-img resize /var/lib/libvirt/images/vm01-disk1.qcow2 +10G
```

### 存储类型

```yaml
qcow2 (QEMU Copy-On-Write v2):
  优势:
    ✅ 支持快照
    ✅ 支持精简置备
    ✅ 支持压缩
    ✅ 支持加密
  劣势:
    ⚠️ 性能略低于raw
  用途: 推荐用于大多数场景

raw (原始格式):
  优势:
    ✅ 性能最佳
    ✅ 兼容性最好
    ✅ 可直接挂载
  劣势:
    ⚠️ 不支持快照
    ⚠️ 占用全部空间
  用途: 性能敏感场景

性能对比:
  随机读写: raw > qcow2 (约5-10%)
  顺序读写: raw ≈ qcow2
  空间效率: qcow2 > raw
  推荐: qcow2 (性能损失可接受，功能丰富)
```

---

## 虚拟机管理

### 使用virt-install创建

```bash
#!/bin/bash
# 使用virt-install创建虚拟机

VM_NAME="ubuntu-vm01"
VCPUS=2
MEMORY=2048  # MB
DISK_SIZE=20  # GB
ISO_PATH="/var/lib/libvirt/iso/ubuntu-22.04-server.iso"
DISK_PATH="/var/lib/libvirt/images/${VM_NAME}.qcow2"
NETWORK="bridge=br0"  # 或 network=default

# 创建磁盘
qemu-img create -f qcow2 $DISK_PATH ${DISK_SIZE}G

# 创建虚拟机
virt-install \
    --name $VM_NAME \
    --ram $MEMORY \
    --vcpus $VCPUS \
    --disk path=$DISK_PATH,format=qcow2,bus=virtio \
    --network $NETWORK,model=virtio \
    --graphics vnc,listen=0.0.0.0,port=5901 \
    --cdrom $ISO_PATH \
    --os-variant ubuntu22.04 \
    --boot uefi \
    --noautoconsole

echo "✅ 虚拟机创建完成: $VM_NAME"
echo "VNC连接: <host-ip>:5901"
echo "使用virt-viewer连接: virt-viewer --connect qemu:///system $VM_NAME"

# 参数说明:
# --name: 虚拟机名称
# --ram: 内存大小(MB)
# --vcpus: CPU核心数
# --disk: 磁盘配置
#   - path: 磁盘路径
#   - format: 磁盘格式(qcow2/raw)
#   - bus: 总线类型(virtio/scsi/sata)
# --network: 网络配置
#   - bridge: 桥接网络
#   - network: NAT网络
#   - model: 网卡型号(virtio推荐)
# --graphics: 图形配置
#   - vnc: VNC协议
#   - spice: SPICE协议(更好性能)
# --cdrom: ISO镜像路径
# --os-variant: 操作系统类型(osinfo-query os)
# --boot: 启动方式(uefi/bios)
# --noautoconsole: 不自动打开控制台
```

**常用os-variant查询**:

```bash
# 列出所有支持的OS
osinfo-query os

# 搜索特定OS
osinfo-query os | grep -i ubuntu
osinfo-query os | grep -i centos

# 常用os-variant:
# ubuntu22.04, ubuntu20.04
# rhel9.0, rhel8.6
# centos-stream9
# debian12
# win10, win11, win2k22
```

### 使用virsh管理

```bash
# 虚拟机生命周期管理

# 列出所有虚拟机
virsh list --all

# 启动虚拟机
virsh start vm-name

# 关闭虚拟机 (优雅关机)
virsh shutdown vm-name

# 强制关闭虚拟机
virsh destroy vm-name

# 重启虚拟机
virsh reboot vm-name

# 暂停虚拟机
virsh suspend vm-name

# 恢复虚拟机
virsh resume vm-name

# 删除虚拟机定义
virsh undefine vm-name

# 删除虚拟机及磁盘
virsh undefine vm-name --remove-all-storage

# 查看虚拟机信息
virsh dominfo vm-name

# 查看虚拟机配置
virsh dumpxml vm-name

# 编辑虚拟机配置
virsh edit vm-name

# 连接虚拟机控制台
virsh console vm-name

# 查看虚拟机VNC端口
virsh vncdisplay vm-name

# 虚拟机自动启动
virsh autostart vm-name
virsh autostart --disable vm-name

# 查看虚拟机资源使用
virsh domstats vm-name

# CPU管理
virsh vcpuinfo vm-name
virsh setvcpus vm-name 4 --live  # 动态调整CPU

# 内存管理
virsh dommemstat vm-name
virsh setmem vm-name 4G --live  # 动态调整内存

# 磁盘管理
virsh domblklist vm-name  # 列出磁盘
virsh attach-disk vm-name /path/to/disk.qcow2 vdb --live  # 热插拔磁盘
virsh detach-disk vm-name vdb --live  # 热拔出磁盘

# 网络管理
virsh domiflist vm-name  # 列出网卡
virsh attach-interface vm-name bridge br0 --model virtio --live  # 热插拔网卡
virsh detach-interface vm-name bridge --mac 52:54:00:xx:xx:xx --live  # 热拔出网卡

# 快照管理
virsh snapshot-create-as vm-name snap1 "First snapshot"  # 创建快照
virsh snapshot-list vm-name  # 列出快照
virsh snapshot-revert vm-name snap1  # 恢复快照
virsh snapshot-delete vm-name snap1  # 删除快照
```

### 使用virt-manager (GUI)

```yaml
virt-manager图形界面:
  安装:
    Ubuntu: apt install virt-manager
    Rocky: dnf install virt-manager
  
  启动:
    命令: virt-manager
    或从应用菜单启动
  
  功能:
    ✅ 创建虚拟机向导
    ✅ 虚拟机控制 (启动/停止/重启)
    ✅ VNC/SPICE图形控制台
    ✅ 资源监控
    ✅ 网络和存储管理
    ✅ 快照管理
  
  适用场景:
    - 学习和测试
    - 小型环境管理
    - 单机虚拟化
  
  不适用:
    - 大规模部署 (使用命令行/自动化)
    - 远程管理 (需要X11转发)
    - 生产自动化

远程连接:
  SSH隧道:
    virt-manager -c 'qemu+ssh://user@remote-host/system'
  
  TCP连接 (不安全，仅内网):
    virt-manager -c 'qemu+tcp://remote-host/system'
```

---

## 虚拟机模板

### 创建模板

```bash
#!/bin/bash
# 创建KVM虚拟机模板

TEMPLATE_NAME="ubuntu-22.04-template"
VM_NAME="ubuntu-22.04-base"

echo "=== 准备创建模板 ==="

# 1. 关闭虚拟机
echo "步骤1: 关闭虚拟机..."
virsh shutdown $VM_NAME
sleep 30

# 2. 清理虚拟机 (使用virt-sysprep)
echo "步骤2: 清理虚拟机系统..."
virt-sysprep -d $VM_NAME \
    --operations defaults \
    --enable customize \
    --hostname template

# virt-sysprep清理项:
# - SSH主机密钥
# - 网络配置 (udev规则, MAC地址)
# - 日志文件
# - 临时文件
# - 用户历史记录
# - Machine ID

# 3. 导出虚拟机配置
echo "步骤3: 导出配置..."
virsh dumpxml $VM_NAME > /tmp/${TEMPLATE_NAME}.xml

# 4. 修改配置 (移除UUID和MAC地址)
sed -i '/<uuid>/d' /tmp/${TEMPLATE_NAME}.xml
sed -i '/<mac address/d' /tmp/${TEMPLATE_NAME}.xml

# 5. 复制磁盘作为模板
echo "步骤4: 复制磁盘..."
DISK_PATH=$(virsh domblklist $VM_NAME | grep vda | awk '{print $2}')
TEMPLATE_DISK="/var/lib/libvirt/images/${TEMPLATE_NAME}.qcow2"
cp $DISK_PATH $TEMPLATE_DISK

# 6. 取消定义原虚拟机 (保留磁盘)
virsh undefine $VM_NAME

echo "✅ 模板创建完成"
echo "模板磁盘: $TEMPLATE_DISK"
echo "模板配置: /tmp/${TEMPLATE_NAME}.xml"
```

### 克隆虚拟机

```bash
#!/bin/bash
# 从模板克隆虚拟机

TEMPLATE_NAME="ubuntu-22.04-template"
NEW_VM_NAME="web-server-01"
TEMPLATE_DISK="/var/lib/libvirt/images/${TEMPLATE_NAME}.qcow2"
NEW_DISK="/var/lib/libvirt/images/${NEW_VM_NAME}.qcow2"

echo "=== 从模板克隆虚拟机 ==="

# 方法1: 使用virt-clone (推荐)
echo "方法1: 使用virt-clone..."
virt-clone \
    --original-xml /tmp/${TEMPLATE_NAME}.xml \
    --name $NEW_VM_NAME \
    --file $NEW_DISK

# 方法2: 手动克隆
echo "方法2: 手动克隆磁盘..."
# 克隆磁盘
qemu-img create -f qcow2 \
    -b $TEMPLATE_DISK \
    -F qcow2 \
    $NEW_DISK

# 定义虚拟机
virsh define /tmp/${TEMPLATE_NAME}.xml

# 启动虚拟机
virsh start $NEW_VM_NAME

echo "✅ 虚拟机克隆完成: $NEW_VM_NAME"
```

### Cloud-init配置

```yaml
Cloud-init说明:
  用途: 虚拟机首次启动自动配置
  支持: Ubuntu, CentOS, Debian等
  功能:
    - 主机名配置
    - 网络配置
    - 用户创建
    - SSH密钥注入
    - 软件包安装
    - 脚本执行
```

**创建Cloud-init镜像**:

```bash
#!/bin/bash
# 创建Cloud-init配置ISO

VM_NAME="web-server-01"
HOSTNAME="web-01.example.com"
IP_ADDRESS="192.168.1.201/24"
GATEWAY="192.168.1.1"
DNS="8.8.8.8"
SSH_PUBLIC_KEY="ssh-rsa AAAA... user@host"

# 1. 创建meta-data
cat > meta-data <<EOF
instance-id: ${VM_NAME}
local-hostname: ${HOSTNAME}
EOF

# 2. 创建user-data
cat > user-data <<EOF
#cloud-config

# 主机名
hostname: ${HOSTNAME}
fqdn: ${HOSTNAME}
manage_etc_hosts: true

# 用户
users:
  - name: admin
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: sudo
    shell: /bin/bash
    ssh_authorized_keys:
      - ${SSH_PUBLIC_KEY}

# 密码 (生产环境建议使用SSH密钥)
chpasswd:
  list: |
    admin:P@ssw0rd
  expire: false

# 网络配置
network:
  version: 2
  ethernets:
    eth0:
      addresses:
        - ${IP_ADDRESS}
      gateway4: ${GATEWAY}
      nameservers:
        addresses:
          - ${DNS}

# 软件包
packages:
  - curl
  - wget
  - vim
  - htop

# 运行命令
runcmd:
  - echo "System initialized" > /var/log/cloudinit.log
  - systemctl restart sshd

# 完成后重启
power_state:
  mode: reboot
  timeout: 30
  condition: True
EOF

# 3. 创建network-config (可选)
cat > network-config <<EOF
version: 2
ethernets:
  eth0:
    addresses:
      - ${IP_ADDRESS}
    gateway4: ${GATEWAY}
    nameservers:
      addresses:
        - ${DNS}
EOF

# 4. 生成ISO
genisoimage \
    -output ${VM_NAME}-cidata.iso \
    -volid cidata \
    -joliet \
    -rock \
    user-data meta-data network-config

# 5. 移动ISO到libvirt目录
mv ${VM_NAME}-cidata.iso /var/lib/libvirt/images/

# 6. 挂载ISO到虚拟机
virsh attach-disk $VM_NAME \
    /var/lib/libvirt/images/${VM_NAME}-cidata.iso \
    hdc \
    --type cdrom \
    --mode readonly \
    --config

echo "✅ Cloud-init ISO创建完成"
echo "启动虚拟机后将自动配置"
```

---

## 性能优化

```yaml
CPU优化:
  CPU模式:
    host-passthrough:
      特性: 直接透传CPU特性
      性能: 最佳
      迁移: 不支持跨CPU型号
      用途: 性能优先，单主机
    
    host-model:
      特性: 模拟相似CPU
      性能: 良好
      迁移: 支持相似CPU迁移
      用途: 推荐，平衡性能和兼容性
    
    custom:
      特性: 指定CPU型号
      性能: 一般
      迁移: 支持跨代迁移
      用途: 兼容性优先
  
  配置示例:
    ```xml
    <cpu mode='host-passthrough'/>
    ```

内存优化:
  大页内存 (Huge Pages):
    优势: 减少TLB miss，提升性能
    适用: 内存密集型应用
    配置:
      ```bash
      # 配置大页
      echo 1024 > /proc/sys/vm/nr_hugepages
      
      # 永久配置
      echo "vm.nr_hugepages = 1024" >> /etc/sysctl.conf
      
      # 虚拟机使用大页
      virsh edit vm-name
      # 添加:
      <memoryBacking>
        <hugepages/>
      </memoryBacking>
      ```
  
  NUMA绑定:
    优势: 减少跨NUMA访问，提升性能
    查看NUMA: numactl --hardware
    配置:
      ```xml
      <numatune>
        <memory mode='strict' nodeset='0'/>
      </numatune>
      ```

磁盘优化:
  缓存模式:
    writeback: 最快，数据可能丢失
    writethrough: 平衡
    none: 最安全，性能较低
    directsync: 最安全，最慢
  
  I/O调度:
    native (Linux AIO): 推荐
    threads: 默认
  
  配置:
    ```xml
    <driver name='qemu' type='qcow2' cache='writeback' io='native'/>
    ```

网络优化:
  virtio驱动: 必须使用
  vhost-net: 内核级加速
  多队列: 提升多核性能
  
  配置:
    ```xml
    <interface type='bridge'>
      <model type='virtio'/>
      <driver name='vhost' queues='4'/>
    </interface>
    ```
```

---

## 相关文档

- [操作系统与内核优化](01_操作系统与内核优化.md)
- [VMware ESXi安装与配置](02_VMware_ESXi安装与配置.md)
- [Hyper-V安装与配置](04_Hyper-V安装与配置.md)
- [BIOS/固件配置清单](../01_硬件规范/06_BIOS固件配置清单.md)
- [硬件兼容性清单](../01_硬件规范/07_硬件兼容性清单.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v3.0  
**状态**: ✅ 生产就绪
