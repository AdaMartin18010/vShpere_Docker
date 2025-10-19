# iSCSI配置与优化

> **返回**: [存储架构目录](README.md) | [虚拟化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [iSCSI配置与优化](#iscsi配置与优化)
  - [📋 目录](#-目录)
  - [iSCSI概述](#iscsi概述)
    - [iSCSI架构](#iscsi架构)
    - [iSCSI优势与劣势](#iscsi优势与劣势)
    - [适用场景](#适用场景)
  - [iSCSI Target配置](#iscsi-target配置)
    - [Linux iSCSI Target (TGT)](#linux-iscsi-target-tgt)
    - [Linux iSCSI Target (LIO)](#linux-iscsi-target-lio)
    - [FreeNAS/TrueNAS iSCSI](#freenastruenas-iscsi)
  - [VMware ESXi iSCSI配置](#vmware-esxi-iscsi配置)
    - [软件iSCSI适配器](#软件iscsi适配器)
    - [硬件iSCSI适配器](#硬件iscsi适配器)
    - [iSCSI网络绑定](#iscsi网络绑定)
  - [Linux iSCSI Initiator配置](#linux-iscsi-initiator配置)
  - [Windows iSCSI Initiator配置](#windows-iscsi-initiator配置)
  - [多路径配置](#多路径配置)
    - [ESXi多路径](#esxi多路径)
    - [Linux多路径](#linux多路径)
  - [网络优化](#网络优化)
  - [性能优化](#性能优化)
  - [监控与故障排查](#监控与故障排查)
  - [相关文档](#相关文档)

---

## iSCSI概述

### iSCSI架构

```yaml
iSCSI (Internet Small Computer Systems Interface):
  定义:
    基于TCP/IP的存储协议
    将SCSI命令封装在IP包中
    通过以太网传输块级存储
  
  核心组件:
    iSCSI Target (目标):
      定义: 存储服务器端
      作用: 提供存储资源
      组件:
        - Portal: IP地址和端口 (默认3260)
        - Target IQN: 全局唯一标识符
        - LUN: 逻辑单元号
      示例:
        IQN: iqn.2025-01.com.example:storage01
        Portal: 192.168.20.10:3260
        LUN: 0, 1, 2...
    
    iSCSI Initiator (发起者):
      定义: 客户端
      作用: 连接到Target并使用存储
      类型:
        - 软件Initiator: 使用CPU处理
        - 硬件Initiator: 专用HBA卡
      示例:
        IQN: iqn.2025-01.com.example:esxi01
    
    iSCSI Portal:
      定义: Target的网络访问点
      格式: IP地址:端口号
      示例: 192.168.20.10:3260
    
    IQN (iSCSI Qualified Name):
      格式: iqn.yyyy-mm.naming-authority:unique-name
      示例: iqn.2025-01.com.example:storage.target01
      说明: 全球唯一标识符

  工作流程:
    1. Discovery (发现):
       Initiator扫描Target
       获取可用Target列表
    
    2. Login (登录):
       Initiator连接到Target
       建立iSCSI会话
    
    3. Authentication (认证):
       CHAP认证 (可选)
       确保安全连接
    
    4. Data Transfer (数据传输):
       读写数据
       SCSI命令封装在TCP/IP中
    
    5. Logout (注销):
       断开iSCSI会话
```

### iSCSI优势与劣势

```yaml
优势:
  成本效益:
    ✅ 使用以太网 (无需专用FC设备)
    ✅ 标准服务器硬件
    ✅ 软件实现成本低
    ✅ 现有网络基础设施
  
  灵活性:
    ✅ 支持远程存储
    ✅ 跨数据中心存储
    ✅ 易于扩展
    ✅ 支持虚拟化
  
  兼容性:
    ✅ 跨平台支持 (Linux/Windows/ESXi)
    ✅ 标准协议
    ✅ 广泛的厂商支持

劣势:
  性能:
    ⚠️ 延迟高于FC SAN (1-3ms vs <0.5ms)
    ⚠️ CPU开销 (软件Initiator)
    ⚠️ 受网络质量影响
  
  复杂性:
    ⚠️ 网络配置要求高
    ⚠️ 多路径配置复杂
    ⚠️ 需要专用网络
  
  可靠性:
    ⚠️ 单点故障风险 (单Target)
    ⚠️ 网络故障影响存储

对比FC SAN:
  性能: FC SAN > iSCSI
  成本: iSCSI > FC SAN (iSCSI更低)
  复杂度: FC SAN > iSCSI (FC更复杂)
  灵活性: iSCSI > FC SAN
  推荐: 
    - 预算有限: iSCSI
    - 性能优先: FC SAN
    - 中小型环境: iSCSI
```

### 适用场景

```yaml
推荐场景:
  虚拟化环境:
    ✅ VMware vSphere
    ✅ Hyper-V
    ✅ KVM
    用途: VM数据存储、共享存储
  
  数据库服务器:
    ✅ MySQL/PostgreSQL
    ✅ SQL Server
    ⚠️ 非关键业务数据库
    要求: 10GbE以上网络
  
  文件服务器:
    ✅ Windows文件服务器
    ✅ Linux文件服务器
    用途: 共享存储池
  
  备份系统:
    ✅ 备份目标存储
    ✅ 归档存储
    优势: 成本低、容量大

不推荐场景:
  ❌ 高IOPS需求 (>100K IOPS)
  ❌ 极低延迟要求 (<0.5ms)
  ❌ 关键业务数据库 (考虑FC SAN)
  ❌ 网络环境不佳
```

---

## iSCSI Target配置

### Linux iSCSI Target (TGT)

```bash
#!/bin/bash
# TGT (SCSI Target Daemon) 配置脚本
# 适用于: Ubuntu/Debian

# 1. 安装TGT
echo "=== 安装TGT ==="
apt update
apt install -y tgt

# 2. 启动TGT服务
systemctl enable tgt
systemctl start tgt
systemctl status tgt

# 3. 创建后端存储 (块设备)
echo "=== 创建存储设备 ==="

# 方法1: 使用LVM卷 (推荐)
# 假设已有VG: vg_storage
lvcreate -L 100G -n lv_iscsi_lun0 vg_storage
lvcreate -L 100G -n lv_iscsi_lun1 vg_storage

# 方法2: 使用文件作为后端
# mkdir -p /storage/iscsi
# dd if=/dev/zero of=/storage/iscsi/lun0.img bs=1M count=102400  # 100GB
# dd if=/dev/zero of=/storage/iscsi/lun1.img bs=1M count=102400

# 4. 配置iSCSI Target
echo "=== 配置iSCSI Target ==="

cat > /etc/tgt/conf.d/iscsi-target.conf <<'EOF'
# iSCSI Target配置

# Target 1
<target iqn.2025-01.com.example:storage.target01>
    # 后端存储
    backing-store /dev/vg_storage/lv_iscsi_lun0
    
    # 或使用文件
    # backing-store /storage/iscsi/lun0.img
    
    # LUN ID (自动分配从1开始，0是控制器)
    lun 1
    
    # Initiator访问控制 (可选)
    # 允许所有Initiator
    initiator-address ALL
    
    # 或仅允许特定IP段
    # initiator-address 192.168.20.0/24
    
    # 或仅允许特定IQN
    # initiator-name iqn.2025-01.com.example:esxi01
    
    # CHAP认证 (推荐)
    incominguser iscsi-user SecurePassword123
    
    # 双向CHAP (可选)
    # outgoinguser target-user TargetPassword456
    
    # 供应商信息
    vendor_id "Example"
    product_id "Storage01"
    product_rev "1.0"
</target>

# Target 2 (多个Target示例)
<target iqn.2025-01.com.example:storage.target02>
    backing-store /dev/vg_storage/lv_iscsi_lun1
    lun 1
    initiator-address 192.168.20.0/24
    incominguser iscsi-user2 SecurePassword456
</target>
EOF

# 5. 重新加载配置
tgt-admin --update ALL

# 6. 验证配置
echo "=== 验证iSCSI Target ==="
tgtadm --mode target --op show

# 显示所有Target
tgt-admin --show

# 7. 防火墙配置
echo "=== 配置防火墙 ==="
ufw allow 3260/tcp

# 完成
echo ""
echo "========================================="
echo "  iSCSI Target配置完成"
echo "========================================="
echo ""
echo "Target信息:"
echo "  IQN: iqn.2025-01.com.example:storage.target01"
echo "  Portal: $(hostname -I | awk '{print $1}'):3260"
echo "  用户名: iscsi-user"
echo "  密码: SecurePassword123"
echo ""
echo "测试连接:"
echo "  iscsiadm -m discovery -t st -p $(hostname -I | awk '{print $1}')"
```

### Linux iSCSI Target (LIO)

```bash
#!/bin/bash
# LIO (Linux IO Target) 配置脚本
# 适用于: CentOS/RHEL/Rocky Linux
# LIO是内核集成的iSCSI Target，性能优于TGT

# 1. 安装targetcli
echo "=== 安装targetcli ==="
dnf install -y targetcli

# 2. 启动target服务
systemctl enable target
systemctl start target

# 3. 使用targetcli配置 (交互式)
echo "=== 配置iSCSI Target (targetcli) ==="

# 方法1: 交互式配置
# targetcli

# 方法2: 命令行配置 (自动化)
cat > /tmp/targetcli-setup.sh <<'TCLI'
#!/bin/bash

# 进入targetcli
targetcli <<EOF
# 创建后端存储 (Block)
/backstores/block create lun0 /dev/vg_storage/lv_iscsi_lun0

# 或使用文件后端 (Fileio)
# /backstores/fileio create lun0 /storage/iscsi/lun0.img 100G

# 创建iSCSI Target
/iscsi create iqn.2025-01.com.example:storage.target01

# 创建LUN
/iscsi/iqn.2025-01.com.example:storage.target01/tpg1/luns create /backstores/block/lun0

# 配置Portal (监听地址)
/iscsi/iqn.2025-01.com.example:storage.target01/tpg1/portals create 192.168.20.10 3260

# 配置ACL (访问控制)
/iscsi/iqn.2025-01.com.example:storage.target01/tpg1/acls create iqn.2025-01.com.example:esxi01

# 配置CHAP认证
/iscsi/iqn.2025-01.com.example:storage.target01/tpg1/acls/iqn.2025-01.com.example:esxi01 set auth userid=iscsi-user
/iscsi/iqn.2025-01.com.example:storage.target01/tpg1/acls/iqn.2025-01.com.example:esxi01 set auth password=SecurePassword123

# 或配置全局认证
# /iscsi/iqn.2025-01.com.example:storage.target01/tpg1 set attribute authentication=1
# /iscsi/iqn.2025-01.com.example:storage.target01/tpg1 set auth userid=iscsi-user
# /iscsi/iqn.2025-01.com.example:storage.target01/tpg1 set auth password=SecurePassword123

# 禁用demo mode (生产环境)
/iscsi/iqn.2025-01.com.example:storage.target01/tpg1 set attribute generate_node_acls=0
/iscsi/iqn.2025-01.com.example:storage.target01/tpg1 set attribute demo_mode_write_protect=0

# 保存配置
saveconfig
exit
EOF
TCLI

chmod +x /tmp/targetcli-setup.sh
/tmp/targetcli-setup.sh

# 4. 验证配置
echo "=== 验证配置 ==="
targetcli ls

# 5. 防火墙配置
echo "=== 配置防火墙 ==="
firewall-cmd --permanent --add-service=iscsi-target
firewall-cmd --reload

# 完成
echo ""
echo "========================================="
echo "  iSCSI Target (LIO) 配置完成"
echo "========================================="
echo ""
echo "查看配置:"
echo "  targetcli ls"
echo ""
echo "Target信息:"
echo "  IQN: iqn.2025-01.com.example:storage.target01"
echo "  Portal: 192.168.20.10:3260"
```

**targetcli常用命令**:

```bash
# 进入targetcli
targetcli

# 查看配置树
ls

# 查看后端存储
/backstores ls

# 查看iSCSI Target
/iscsi ls

# 查看会话
sessions

# 删除Target
/iscsi delete iqn.xxx

# 保存配置
saveconfig

# 退出
exit

# 命令行直接查看
targetcli ls

# 导出配置
targetcli saveconfig /tmp/target-backup.json

# 恢复配置
targetcli restoreconfig /tmp/target-backup.json
```

### FreeNAS/TrueNAS iSCSI

```yaml
TrueNAS iSCSI配置 (Web界面):
  步骤1: 创建数据集
    导航: Storage → Pools
    操作:
      1. 选择存储池
      2. 点击 "Add Dataset"
      3. 名称: iscsi
      4. 保存
  
  步骤2: 创建Portal
    导航: Sharing → Block (iSCSI) → Portals
    操作:
      1. 点击 "Add"
      2. Discovery Authentication Method: None (或CHAP)
      3. IP Address: 0.0.0.0 (所有IP) 或指定IP
      4. Port: 3260
      5. 保存
  
  步骤3: 创建Initiator
    导航: Sharing → Block (iSCSI) → Initiators
    操作:
      1. 点击 "Add"
      2. Initiators: 留空 (允许所有) 或指定IQN
      3. Authorized Network: 192.168.20.0/24
      4. 保存
  
  步骤4: 创建Extent (存储范围)
    导航: Sharing → Block (iSCSI) → Extents
    操作:
      1. 点击 "Add"
      2. Name: extent01
      3. Type: Device (或File)
      4. Device: 选择zvol
         或 File: 指定路径和大小
      5. Logical Block Size: 512 (默认)
      6. 保存
  
  步骤5: 创建Target
    导航: Sharing → Block (iSCSI) → Targets
    操作:
      1. 点击 "Add"
      2. Target Name: target01
      3. Target Alias: Storage Target 01
      4. Portal Group: 选择之前创建的Portal
      5. Initiator Group: 选择之前创建的Initiator
      6. Authentication Method: None (或CHAP)
      7. 保存
  
  步骤6: 关联Target和Extent
    导航: Sharing → Block (iSCSI) → Associated Targets
    操作:
      1. 点击 "Add"
      2. Target: 选择target01
      3. LUN ID: 0
      4. Extent: 选择extent01
      5. 保存
  
  步骤7: 启用iSCSI服务
    导航: Services
    操作:
      1. 找到 "iSCSI"
      2. 点击开关启用
      3. 勾选 "Start Automatically"
  
  验证:
    从Initiator扫描:
      iscsiadm -m discovery -t st -p <TrueNAS-IP>
    
    应显示:
      <TrueNAS-IP>:3260,1 iqn.2005-10.org.freenas.ctl:target01
```

---

## VMware ESXi iSCSI配置

### 软件iSCSI适配器

```bash
#!/bin/bash
# ESXi软件iSCSI适配器配置脚本

echo "========================================="
echo "  ESXi软件iSCSI适配器配置"
echo "========================================="
echo ""

ESXi_HOST="192.168.1.101"
ISCSI_TARGET_IP="192.168.20.10"
ISCSI_IQN="iqn.2025-01.com.example:storage.target01"
VMKERNEL_IP="192.168.20.101"

echo "配置主机: $ESXi_HOST"
echo "iSCSI Target: $ISCSI_TARGET_IP"
echo "VMkernel IP: $VMKERNEL_IP"
echo ""

# 1. 启用软件iSCSI适配器
echo "步骤1: 启用软件iSCSI适配器..."
esxcli iscsi software set --enabled=true

# 2. 获取iSCSI适配器名称
ISCSI_HBA=$(esxcli iscsi adapter list | grep "iscsi_vmk" | awk '{print $1}')
echo "iSCSI适配器: $ISCSI_HBA"

# 3. 创建VMkernel端口 (用于iSCSI)
echo ""
echo "步骤2: 配置VMkernel端口..."

# 假设已有vSwitch0和iSCSI-PG端口组
esxcli network ip interface add \
  --interface-name=vmk1 \
  --portgroup-name="iSCSI-PG"

# 配置静态IP
esxcli network ip interface ipv4 set \
  --interface-name=vmk1 \
  --type=static \
  --ipv4=$VMKERNEL_IP \
  --netmask=255.255.255.0

# 设置MTU为9000 (Jumbo Frame)
esxcli network ip interface set \
  --interface-name=vmk1 \
  --mtu=9000

# 4. 绑定VMkernel端口到iSCSI适配器
echo ""
echo "步骤3: 绑定VMkernel端口..."
esxcli iscsi networkportal add \
  --adapter=$ISCSI_HBA \
  --nic=vmk1

# 5. 配置CHAP认证 (如果Target需要)
echo ""
echo "步骤4: 配置CHAP认证..."
esxcli iscsi adapter auth chap set \
  --adapter=$ISCSI_HBA \
  --authname="iscsi-user" \
  --secret="SecurePassword123" \
  --level=discouraged

# 6. 添加动态发现地址
echo ""
echo "步骤5: 添加iSCSI Target..."
esxcli iscsi adapter discovery sendtarget add \
  --adapter=$ISCSI_HBA \
  --address=$ISCSI_TARGET_IP:3260

# 7. 重新扫描适配器
echo ""
echo "步骤6: 扫描存储设备..."
esxcli storage core adapter rescan --adapter=$ISCSI_HBA

# 8. 验证
echo ""
echo "========================================="
echo "  配置完成 - 验证"
echo "========================================="
echo ""

echo "iSCSI适配器状态:"
esxcli iscsi adapter list

echo ""
echo "iSCSI会话:"
esxcli iscsi session list

echo ""
echo "发现的设备:"
esxcli storage core device list | grep -A 5 "naa."

echo ""
echo "========================================="
echo "  完成"
echo "========================================="
```

**ESXi GUI配置步骤**:

```yaml
通过vSphere Client配置:
  步骤1: 启用iSCSI
    1. 登录vSphere Client
    2. 选择ESXi主机
    3. 配置 → 存储适配器
    4. 点击 "添加软件适配器"
    5. 选择 "软件iSCSI适配器"
    6. 确定
  
  步骤2: 配置网络绑定
    1. 选择iSCSI适配器 (vmhba##)
    2. 网络端口绑定 → 添加
    3. 选择VMkernel端口 (vmk1)
    4. 确定
  
  步骤3: 配置动态发现
    1. 动态发现 → 添加
    2. iSCSI服务器: 192.168.20.10
    3. 端口: 3260
    4. CHAP认证 (可选):
       - 名称: iscsi-user
       - 密码: SecurePassword123
    5. 确定
  
  步骤4: 重新扫描
    1. 点击 "重新扫描存储"
    2. 等待完成
  
  步骤5: 创建VMFS数据存储
    1. 导航到: 存储 → 数据存储
    2. 新建数据存储 → VMFS
    3. 选择iSCSI设备
    4. 配置并创建
```

### 硬件iSCSI适配器

```yaml
硬件iSCSI HBA卡:
  优势:
    ✅ 无CPU开销 (专用处理器)
    ✅ 更高性能
    ✅ 更低延迟
    ✅ TOE (TCP Offload Engine)
  
  推荐型号:
    QLogic QLE4062:
      速率: 双口1Gbps
      价格: ~¥2,000
    
    QLogic QLE8362:
      速率: 双口10Gbps
      价格: ~¥5,000
    
    Broadcom 57810S:
      速率: 双口10Gbps
      价格: ~¥3,500
      说明: 融合网卡 (支持iSCSI和FCoE)

配置步骤:
  1. 安装HBA卡到服务器
  2. 更新HBA固件 (如需)
  3. 在ESXi中自动识别
  4. 配置与软件iSCSI类似
  5. 无需VMkernel绑定 (使用HBA自身网络)
```

### iSCSI网络绑定

```bash
# ESXi iSCSI网络端口绑定 (多路径)

# 创建第二个VMkernel端口
esxcli network ip interface add \
  --interface-name=vmk2 \
  --portgroup-name="iSCSI-PG2"

esxcli network ip interface ipv4 set \
  --interface-name=vmk2 \
  --type=static \
  --ipv4=192.168.20.102 \
  --netmask=255.255.255.0

esxcli network ip interface set \
  --interface-name=vmk2 \
  --mtu=9000

# 绑定第二个端口
esxcli iscsi networkportal add \
  --adapter=$ISCSI_HBA \
  --nic=vmk2

# 验证绑定
esxcli iscsi networkportal list

# 配置端口绑定策略
esxcli iscsi adapter param set \
  --adapter=$ISCSI_HBA \
  --key=DelayedAck \
  --value=false

# 查看所有参数
esxcli iscsi adapter param get --adapter=$ISCSI_HBA
```

---

## Linux iSCSI Initiator配置

```bash
#!/bin/bash
# Linux iSCSI Initiator配置脚本

echo "========================================="
echo "  Linux iSCSI Initiator配置"
echo "========================================="
echo ""

ISCSI_TARGET_IP="192.168.20.10"
ISCSI_IQN="iqn.2025-01.com.example:storage.target01"

# 1. 安装iSCSI Initiator
echo "步骤1: 安装iSCSI工具..."

# Ubuntu/Debian
if command -v apt &> /dev/null; then
    apt update
    apt install -y open-iscsi
    systemctl enable open-iscsi
    systemctl start open-iscsi
fi

# CentOS/RHEL/Rocky
if command -v dnf &> /dev/null; then
    dnf install -y iscsi-initiator-utils
    systemctl enable iscsi
    systemctl start iscsi
fi

# 2. 配置Initiator IQN (可选，使用默认或自定义)
echo ""
echo "步骤2: 配置Initiator IQN..."

# 查看当前IQN
INITIATOR_IQN=$(cat /etc/iscsi/initiatorname.iscsi | grep "InitiatorName=" | cut -d'=' -f2)
echo "当前Initiator IQN: $INITIATOR_IQN"

# 或设置自定义IQN
# echo "InitiatorName=iqn.2025-01.com.example:initiator01" > /etc/iscsi/initiatorname.iscsi

# 3. 配置CHAP认证 (如果Target需要)
echo ""
echo "步骤3: 配置CHAP认证..."

cat >> /etc/iscsi/iscsid.conf <<EOF

# CHAP认证配置
node.session.auth.authmethod = CHAP
node.session.auth.username = iscsi-user
node.session.auth.password = SecurePassword123

# 或配置双向CHAP
# node.session.auth.username_in = target-user
# node.session.auth.password_in = TargetPassword456

# 自动登录
node.startup = automatic
EOF

# 重启服务
systemctl restart iscsid

# 4. 发现iSCSI Target
echo ""
echo "步骤4: 发现iSCSI Target..."
iscsiadm -m discovery -t sendtargets -p $ISCSI_TARGET_IP

# 5. 登录到Target
echo ""
echo "步骤5: 登录到iSCSI Target..."
iscsiadm -m node --targetname $ISCSI_IQN --portal $ISCSI_TARGET_IP:3260 --login

# 6. 验证
echo ""
echo "========================================="
echo "  配置完成 - 验证"
echo "========================================="
echo ""

echo "iSCSI会话:"
iscsiadm -m session

echo ""
echo "发现的磁盘:"
lsblk | grep -E "sd[b-z]"

echo ""
echo "iSCSI设备详情:"
ls -l /dev/disk/by-path/ | grep iscsi

echo ""
echo "========================================="
echo "  完成"
echo "========================================="
echo ""
echo "下一步: 创建文件系统并挂载"
echo "  mkfs.ext4 /dev/sdb"
echo "  mount /dev/sdb /mnt/iscsi"
```

**Linux iSCSI常用命令**:

```bash
# 发现Target
iscsiadm -m discovery -t st -p 192.168.20.10

# 登录到所有发现的Target
iscsiadm -m node --login

# 登录到特定Target
iscsiadm -m node --targetname iqn.xxx --portal 192.168.20.10:3260 --login

# 注销
iscsiadm -m node --logout

# 查看会话
iscsiadm -m session

# 查看会话详情
iscsiadm -m session -P 3

# 删除Target记录
iscsiadm -m node --targetname iqn.xxx --portal 192.168.20.10:3260 --op delete

# 查看所有记录的Target
iscsiadm -m node

# 修改Target设置
iscsiadm -m node --targetname iqn.xxx --op update -n node.startup -v automatic

# 重新扫描设备大小
iscsiadm -m node --rescan

# 或使用rescan-scsi-bus
rescan-scsi-bus.sh --forcerescan
```

---

## Windows iSCSI Initiator配置

```powershell
# PowerShell脚本 - Windows iSCSI Initiator配置

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Windows iSCSI Initiator配置" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$TargetPortal = "192.168.20.10"
$TargetIQN = "iqn.2025-01.com.example:storage.target01"

# 1. 启动iSCSI服务
Write-Host "步骤1: 启动iSCSI服务..." -ForegroundColor Green
Start-Service MSiSCSI
Set-Service MSiSCSI -StartupType Automatic

# 2. 配置iSCSI Initiator IQN (可选)
Write-Host ""
Write-Host "步骤2: 查看Initiator IQN..." -ForegroundColor Green
$InitiatorIQN = (Get-InitiatorPort).NodeAddress
Write-Host "Initiator IQN: $InitiatorIQN" -ForegroundColor White

# 3. 添加Target Portal
Write-Host ""
Write-Host "步骤3: 添加Target Portal..." -ForegroundColor Green
New-IscsiTargetPortal -TargetPortalAddress $TargetPortal

# 4. 发现Target
Write-Host ""
Write-Host "步骤4: 发现Target..." -ForegroundColor Green
Get-IscsiTarget

# 5. 连接到Target
Write-Host ""
Write-Host "步骤5: 连接到Target..." -ForegroundColor Green
Connect-IscsiTarget -NodeAddress $TargetIQN `
    -IsPersistent $true `
    -IsMultipathEnabled $false

# 如果需要CHAP认证
# Connect-IscsiTarget -NodeAddress $TargetIQN `
#     -IsPersistent $true `
#     -AuthenticationType ONEWAYCHAP `
#     -ChapUsername "iscsi-user" `
#     -ChapSecret "SecurePassword123"

# 6. 初始化磁盘 (首次)
Write-Host ""
Write-Host "步骤6: 初始化新磁盘..." -ForegroundColor Green

# 查找未初始化的磁盘
$newDisks = Get-Disk | Where-Object {$_.PartitionStyle -eq 'RAW'}

foreach ($disk in $newDisks) {
    Write-Host "初始化磁盘 $($disk.Number)..." -ForegroundColor Cyan
    
    # 初始化为GPT
    Initialize-Disk -Number $disk.Number -PartitionStyle GPT
    
    # 创建分区
    $partition = New-Partition -DiskNumber $disk.Number -UseMaximumSize -AssignDriveLetter
    
    # 格式化
    Format-Volume -DriveLetter $partition.DriveLetter `
        -FileSystem NTFS `
        -NewFileSystemLabel "iSCSI-Volume" `
        -Confirm:$false
    
    Write-Host "磁盘 $($disk.Number) 已格式化为 $($partition.DriveLetter):\" -ForegroundColor Green
}

# 7. 验证
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  配置完成 - 验证" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "iSCSI会话:" -ForegroundColor Yellow
Get-IscsiSession | Format-Table

Write-Host ""
Write-Host "iSCSI连接:" -ForegroundColor Yellow
Get-IscsiConnection | Format-Table

Write-Host ""
Write-Host "磁盘列表:" -ForegroundColor Yellow
Get-Disk | Format-Table Number, FriendlyName, Size, PartitionStyle

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  完成" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
```

**GUI配置步骤**:

```yaml
Windows iSCSI Initiator (GUI):
  打开iSCSI Initiator:
    路径: 控制面板 → 管理工具 → iSCSI Initiator
    或: 运行 → iscsicpl.exe
  
  步骤1: 配置Tab (可选)
    查看Initiator IQN
    修改CHAP凭据 (如需)
  
  步骤2: 发现Tab
    1. 点击 "发现门户"
    2. IP地址: 192.168.20.10
    3. 端口: 3260
    4. 高级 (可选): 配置CHAP
    5. 确定
  
  步骤3: 目标Tab
    1. 点击 "刷新"
    2. 看到Target列表
    3. 选择Target
    4. 点击 "连接"
    5. 勾选 "将此连接添加到收藏目标列表"
    6. (可选) 高级设置:
       - 本地适配器
       - CHAP认证
       - 多路径
    7. 确定
  
  步骤4: 卷和设备Tab
    点击 "自动配置"
    查看连接的卷
  
  步骤5: 初始化磁盘
    1. 打开: 磁盘管理 (diskmgmt.msc)
    2. 看到新磁盘
    3. 初始化磁盘 (GPT)
    4. 新建简单卷
    5. 格式化 (NTFS)
    6. 分配驱动器号
```

---

## 多路径配置

### ESXi多路径

```bash
# ESXi多路径配置

# 1. 查看存储设备和路径
esxcli storage core device list
esxcli storage core path list

# 2. 查看多路径策略
esxcli storage nmp device list

# 3. 设置多路径策略为Round Robin (推荐)
DEVICE_NAA="naa.xxx"  # 替换为实际设备NAA

esxcli storage nmp device set \
  --device $DEVICE_NAA \
  --psp VMW_PSP_RR

# 4. 设置Round Robin的IOPS限制
esxcli storage nmp psp roundrobin deviceconfig set \
  --device $DEVICE_NAA \
  --type=iops \
  --iops=1

# 5. 查看配置
esxcli storage nmp device list -d $DEVICE_NAA

# 6. 查看路径状态
esxcli storage core path list -d $DEVICE_NAA

# 多路径策略说明:
# VMW_PSP_FIXED: 固定路径，故障时切换
# VMW_PSP_MRU: 最近使用路径
# VMW_PSP_RR: 轮询，负载均衡 (推荐)

# 查看所有iSCSI设备的多路径
for device in $(esxcli storage core device list | grep "iSCSI" | awk '{print $1}'); do
    echo "Device: $device"
    esxcli storage nmp device list -d $device | grep "Path Selection Policy"
    echo ""
done
```

### Linux多路径

```bash
#!/bin/bash
# Linux多路径 (multipath-tools) 配置

# 1. 安装multipath-tools
apt install -y multipath-tools  # Ubuntu
# dnf install -y device-mapper-multipath  # CentOS

# 2. 启动multipathd服务
systemctl enable multipathd
systemctl start multipathd

# 3. 生成配置文件
mpathconf --enable --with_multipathd y

# 4. 配置multipath.conf
cat > /etc/multipath.conf <<'EOF'
# multipath.conf

defaults {
    user_friendly_names yes
    path_grouping_policy multibus
    path_selector "round-robin 0"
    failback immediate
    rr_min_io 100
    no_path_retry queue
}

blacklist {
    devnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"
    devnode "^hd[a-z]"
    devnode "^sda$"  # 排除本地磁盘
}

# 设备特定配置 (可选)
devices {
    device {
        vendor "LIO-ORG"
        product ".*"
        path_grouping_policy multibus
        path_selector "round-robin 0"
        hardware_handler "1 alua"
        prio alua
        failback immediate
        rr_weight priorities
        no_path_retry 30
    }
}

multipaths {
    # 可选：为特定设备配置别名
    # multipath {
    #     wwid "36001405xxx"
    #     alias iscsi_vol01
    # }
}
EOF

# 5. 重新加载配置
systemctl reload multipathd

# 6. 重新扫描设备
multipath -r

# 7. 查看多路径设备
multipath -ll

# 8. 查看详细信息
multipath -v3 -ll

# 9. 查看multipath映射
ls -l /dev/mapper/

# 10. 使用多路径设备
# mkfs.ext4 /dev/mapper/mpatha
# mount /dev/mapper/mpatha /mnt/iscsi

echo ""
echo "多路径配置完成"
echo "查看多路径设备: multipath -ll"
```

**multipath常用命令**:

```bash
# 查看多路径设备
multipath -ll

# 重新加载配置
systemctl reload multipathd

# 重新扫描多路径
multipath -r

# 刷新多路径
multipath -F

# 查看路径状态
multipath -t

# 查看设备WWID
/lib/udev/scsi_id -g -u -d /dev/sdb

# 手动添加路径
multipath -a /dev/sdb

# 手动删除路径
multipath -d mpatha
```

---

## 网络优化

```yaml
网络配置最佳实践:
  专用VLAN:
    原因: 隔离存储流量
    配置:
      VLAN ID: 20 (示例)
      IP段: 192.168.20.0/24
      MTU: 9000
  
  Jumbo Frame (MTU 9000):
    优势:
      ✅ 减少CPU开销
      ✅ 提升吞吐量 (10-30%)
      ✅ 降低延迟
    
    配置:
      交换机: 启用Jumbo Frame
      ESXi: MTU 9000 (VMkernel)
      Linux: ip link set eth1 mtu 9000
      Target: MTU 9000
    
    验证:
      # Linux/ESXi
      ping -M do -s 8972 192.168.20.10
      # 8972 = 9000 - 28 (IP+ICMP header)
  
  链路聚合 (LACP):
    优势:
      ✅ 带宽聚合
      ✅ 冗余
      ✅ 负载均衡
    
    配置:
      交换机: 配置LACP
      ESXi: IP Hash负载均衡
      Linux: bonding mode=802.3ad
  
  QoS (服务质量):
    目的: 保证存储流量优先级
    
    配置:
      交换机: 
        - CoS: 5-7 (存储流量)
        - DSCP: EF (46)
      
      ESXi:
        - 存储流量自动高优先级
      
      Linux:
        iptables -t mangle -A OUTPUT \
          -p tcp --dport 3260 \
          -j DSCP --set-dscp 46

交换机配置示例 (Cisco):

  ```cisco
  ! 创建存储VLAN
  vlan 20
   name Storage-Network
  
  ! 配置Trunk端口
  interface GigabitEthernet0/1
   switchport mode trunk
   switchport trunk allowed vlan 20
   mtu 9000
  
  ! 配置访问端口
  interface GigabitEthernet0/10
   switchport mode access
   switchport access vlan 20
   mtu 9000
   spanning-tree portfast
  
  ! QoS配置
  mls qos
  class-map match-all ISCSI-TRAFFIC
   match access-group name ISCSI
  policy-map STORAGE-QOS
   class ISCSI-TRAFFIC
    set dscp ef
    priority percent 50
  interface GigabitEthernet0/10
   service-policy output STORAGE-QOS
  
  ! 访问控制列表
  ip access-list extended ISCSI
   permit tcp any any eq 3260
  ```

---

## 性能优化

```yaml
存储性能优化:
  队列深度:
    ESXi:
      # 查看队列深度
      esxcli storage core device list -d naa.xxx
      
      # 调整队列深度
      esxcli storage core device set \
        -d naa.xxx \
        --queue-full-sample-size 32 \
        --queue-full-threshold 8
    
    Linux:
      # 查看队列深度
      cat /sys/block/sdb/device/queue_depth
      
      # 调整队列深度
      echo 128 > /sys/block/sdb/device/queue_depth
  
  I/O调度器:
    Linux:
      # 查看当前调度器
      cat /sys/block/sdb/queue/scheduler
      
      # 设置为noop (推荐用于iSCSI)
      echo noop > /sys/block/sdb/queue/scheduler
      
      # 或设置为deadline
      echo deadline > /sys/block/sdb/queue/scheduler
      
      # 永久配置 (/etc/default/grub)
      GRUB_CMDLINE_LINUX="elevator=noop"
  
  TCP参数调优:
    Linux:
      ```bash
      # /etc/sysctl.conf
      
      # TCP窗口大小
      net.core.rmem_max = 134217728
      net.core.wmem_max = 134217728
      net.ipv4.tcp_rmem = 4096 87380 67108864
      net.ipv4.tcp_wmem = 4096 65536 67108864
      
      # TCP连接
      net.ipv4.tcp_no_metrics_save = 1
      net.ipv4.tcp_moderate_rcvbuf = 1
      
      # 应用配置
      sysctl -p
      ```
  
  DelayedAck禁用:
    ESXi:
      ```bash
      esxcli iscsi adapter param set \
        --adapter=vmhba33 \
        --key=DelayedAck \
        --value=false
      ```
    
    说明: 提升小I/O性能
  
  预读 (Read-ahead):
    Linux:
      ```bash
      # 查看预读大小 (扇区数)
      blockdev --getra /dev/sdb
      
      # 设置预读为4096扇区 (2MB)
      blockdev --setra 4096 /dev/sdb
      
      # 永久配置 (udev规则)
      echo 'ACTION=="add|change", KERNEL=="sd[b-z]", ATTR{bdi/read_ahead_kb}="2048"' > /etc/udev/rules.d/60-iscsi-readahead.rules
      ```

Target端优化:
  LIO Target:
    ```bash
    # 增加队列深度
    targetcli /iscsi/iqn.xxx/tpg1 set attribute \
      default_cmdsn_depth=128
    
    # 启用数据摘要 (可选，增加安全但降低性能)
    targetcli /iscsi/iqn.xxx/tpg1 set attribute \
      DataDigest=None \
      HeaderDigest=None
    ```
  
  TGT Target:
    ```bash
    # /etc/tgt/conf.d/iscsi-target.conf
    
    <target iqn.xxx>
        backing-store /dev/vg/lv
        
        # 直接I/O (绕过缓存)
        direct-store yes
        
        # 块大小
        bs-type aio
        
        # 队列深度
        queue-depth 128
    </target>
    ```
```

---

## 监控与故障排查

```bash
#!/bin/bash
# iSCSI监控和故障排查脚本

echo "========================================="
echo "  iSCSI监控和诊断"
echo "========================================="
echo ""

# ESXi监控
if command -v esxcli &> /dev/null; then
    echo "=== ESXi iSCSI状态 ==="
    
    # iSCSI适配器
    echo "iSCSI适配器:"
    esxcli iscsi adapter list
    
    echo ""
    echo "iSCSI会话:"
    esxcli iscsi session list
    
    echo ""
    echo "iSCSI连接统计:"
    esxcli iscsi session connection list
    
    echo ""
    echo "存储设备:"
    esxcli storage core device list | grep -A 5 "naa."
    
    echo ""
    echo "路径状态:"
    esxcli storage core path list | grep -E "(Device|State|Path)"
fi

# Linux监控
if command -v iscsiadm &> /dev/null; then
    echo "=== Linux iSCSI状态 ==="
    
    # iSCSI会话
    echo "iSCSI会话:"
    iscsiadm -m session
    
    echo ""
    echo "会话详情:"
    iscsiadm -m session -P 3
    
    echo ""
    echo "iSCSI设备:"
    ls -l /dev/disk/by-path/ | grep iscsi
    
    echo ""
    echo "块设备统计:"
    iostat -x 1 3
    
    echo ""
    echo "多路径状态:"
    if command -v multipath &> /dev/null; then
        multipath -ll
    fi
fi

# 网络诊断
echo ""
echo "=== 网络诊断 ==="

TARGET_IP="192.168.20.10"

echo "Ping测试:"
ping -c 4 $TARGET_IP

echo ""
echo "MTU测试 (Jumbo Frame):"
ping -M do -s 8972 -c 4 $TARGET_IP 2>&1 | tail -5

echo ""
echo "端口连通性:"
nc -zv $TARGET_IP 3260 2>&1

echo ""
echo "TCP连接统计:"
netstat -anp | grep 3260

# 性能测试
echo ""
echo "=== 性能测试 ==="

ISCSI_DEVICE="/dev/sdb"  # 修改为实际设备

if [ -b "$ISCSI_DEVICE" ]; then
    echo "顺序读测试 (1GB):"
    dd if=$ISCSI_DEVICE of=/dev/null bs=1M count=1024 2>&1 | grep "MB/s"
    
    echo ""
    echo "顺序写测试 (100MB, 危险!):"
    echo "# dd if=/dev/zero of=$ISCSI_DEVICE bs=1M count=100"
    echo "# (已注释，避免数据丢失)"
fi

# 日志检查
echo ""
echo "=== 日志检查 ==="

if [ -f "/var/log/messages" ]; then
    echo "最近的iSCSI日志:"
    tail -50 /var/log/messages | grep -i iscsi
fi

if [ -f "/var/log/syslog" ]; then
    echo "最近的iSCSI日志:"
    tail -50 /var/log/syslog | grep -i iscsi
fi

echo ""
echo "========================================="
echo "  诊断完成"
echo "========================================="
```

**常见问题和解决方案**:

```yaml
问题1: 无法发现Target
  症状:
    iscsiadm discovery返回空
  
  排查:
    1. 检查网络连通性:
       ping <target-ip>
       nc -zv <target-ip> 3260
    
    2. 检查Target服务状态:
       systemctl status target  # LIO
       systemctl status tgt     # TGT
    
    3. 检查防火墙:
       firewall-cmd --list-all
       ufw status
    
    4. 检查Target配置:
       targetcli ls
       tgtadm --mode target --op show
  
  解决:
    - 确保Target服务运行
    - 开放端口3260
    - 检查ACL配置

问题2: 登录失败 (认证错误)
  症状:
    Login failed: Authorization failed
  
  排查:
    1. 检查CHAP凭据
    2. 查看Target日志
    3. 验证Initiator IQN在ACL中
  
  解决:
    - 更正CHAP用户名/密码
    - 添加Initiator IQN到ACL
    - 禁用CHAP测试 (不推荐生产)

问题3: 性能差
  症状:
    IOPS低、延迟高
  
  排查:
    1. 检查网络:
       - MTU是否为9000
       - 网络延迟 (ping)
       - 丢包率
    
    2. 检查多路径:
       - 策略是否为Round Robin
       - 所有路径是否Active
    
    3. 检查存储:
       - Target端磁盘性能
       - iostat查看
    
    4. 检查队列深度
  
  解决:
    - 启用Jumbo Frame
    - 配置多路径Round Robin
    - 禁用DelayedAck
    - 增加队列深度
    - 使用SSD存储

问题4: 会话断开
  症状:
    iSCSI session lost
  
  排查:
    1. 检查网络稳定性
    2. 检查Target服务状态
    3. 查看系统日志
  
  解决:
    - 配置会话超时:
      /etc/iscsi/iscsid.conf
      node.session.timeo.replacement_timeout = 120
    
    - 启用自动重连:
      node.startup = automatic
    
    - 检查网络设备 (交换机)
```

---

## 相关文档

- [存储类型与选型标准](01_存储类型与选型标准.md)
- [NFS配置与优化](03_NFS配置与优化.md)
- [存储性能优化](06_存储性能优化.md)
- [存储容灾与备份](07_存储容灾与备份.md)
- [网络架构配置](../04_网络架构/)

---

**更新时间**: 2025-10-19  
**文档版本**: v3.0  
**状态**: ✅ 生产就绪
