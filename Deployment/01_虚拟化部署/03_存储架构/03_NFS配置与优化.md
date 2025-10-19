# NFS配置与优化

> **返回**: [存储架构目录](README.md) | [虚拟化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [NFS配置与优化](#nfs配置与优化)
  - [📋 目录](#-目录)
  - [NFS概述](#nfs概述)
    - [NFS架构](#nfs架构)
    - [NFS版本对比](#nfs版本对比)
    - [适用场景](#适用场景)
  - [NFS服务器配置](#nfs服务器配置)
    - [Linux NFS服务器 (NFSv3)](#linux-nfs服务器-nfsv3)
    - [Linux NFS服务器 (NFSv4)](#linux-nfs服务器-nfsv4)
    - [FreeNAS/TrueNAS NFS](#freenastruenas-nfs)
  - [VMware ESXi NFS配置](#vmware-esxi-nfs配置)
    - [挂载NFS数据存储](#挂载nfs数据存储)
    - [NFSv4.1会话中继](#nfsv41会话中继)
  - [Linux NFS客户端配置](#linux-nfs客户端配置)
  - [Windows NFS客户端配置](#windows-nfs客户端配置)
  - [网络优化](#网络优化)
  - [性能优化](#性能优化)
  - [安全配置](#安全配置)
  - [监控与故障排查](#监控与故障排查)
  - [相关文档](#相关文档)

---

## NFS概述

### NFS架构

```yaml
NFS (Network File System):
  定义:
    网络文件系统
    文件级别的共享存储
    基于RPC (Remote Procedure Call)
  
  核心组件:
    NFS Server (服务器):
      角色: 导出共享目录
      服务: nfsd, mountd, rpcbind
      端口:
        - NFSv3: 2049 (TCP/UDP), 111 (rpcbind)
        - NFSv4: 2049 (TCP only)
      配置: /etc/exports
    
    NFS Client (客户端):
      角色: 挂载远程共享
      命令: mount, showmount
      配置: /etc/fstab
    
    RPC服务:
      rpcbind (portmapper):
        作用: 端口映射
        端口: 111
        仅NFSv3需要
      
      mountd:
        作用: 处理挂载请求
        端口: 动态 (NFSv3)
        NFSv4不需要
      
      nfsd:
        作用: NFS核心服务
        端口: 2049
      
      statd (可选):
        作用: 文件锁管理
        用途: NFSv3
      
      lockd (可选):
        作用: 文件锁
        用途: NFSv3

  工作流程:
    1. Client发起mount请求
    2. Server验证权限 (/etc/exports)
    3. 建立NFS连接
    4. Client访问远程文件 (透明)
    5. Server处理I/O请求
    6. 返回数据给Client

  存储模式:
    - 文件级存储
    - 共享文件系统
    - 多客户端同时访问
    - POSIX兼容
```

### NFS版本对比

```yaml
NFSv3:
  发布: 1995年
  协议: TCP/UDP
  特点:
    ✅ 成熟稳定
    ✅ 广泛支持
    ✅ 简单配置
    ⚠️ 无状态协议
    ⚠️ 安全性较低
    ⚠️ 依赖多个RPC服务
  
  端口需求:
    - 2049 (nfs)
    - 111 (rpcbind)
    - 动态端口 (mountd, statd, lockd)
  
  适用场景:
    ✅ 传统环境
    ✅ VMware ESXi (推荐)
    ✅ 简单共享
  
  性能:
    良好，成熟优化

NFSv4:
  发布: 2000年 (v4.0)
  协议: TCP only
  特点:
    ✅ 有状态协议
    ✅ 单端口 (2049)
    ✅ 内置安全 (Kerberos)
    ✅ 更好性能
    ✅ 支持ACL
    ✅ 复合操作
    ⚠️ 配置较复杂
  
  子版本:
    v4.0 (2000):
      基础NFSv4功能
    
    v4.1 (2010):
      ✅ pNFS (并行NFS)
      ✅ 会话管理
      ✅ 更好性能
      VMware支持: vSphere 6.0+
    
    v4.2 (2016):
      ✅ 服务器端复制
      ✅ 稀疏文件
      ✅ 应用数据块
  
  端口需求:
    - 2049 only
  
  适用场景:
    ✅ 现代环境
    ✅ 安全需求高
    ✅ Linux to Linux
    ⚠️ ESXi支持有限
  
  性能:
    优秀，尤其是v4.1+

版本对比表:
  特性          | NFSv3  | NFSv4.0 | NFSv4.1
  -------------|--------|---------|--------
  发布年份      | 1995   | 2000    | 2010
  协议         | TCP/UDP| TCP     | TCP
  端口数量      | 多个   | 单个    | 单个
  状态         | 无状态  | 有状态  | 有状态
  Kerberos     | 可选   | 内置    | 内置
  ACL          | ❌     | ✅      | ✅
  pNFS         | ❌     | ❌      | ✅
  复合操作      | ❌     | ✅      | ✅
  性能         | 良好   | 良好    | 优秀
  ESXi推荐     | ✅     | ⚠️      | ✅ (6.0+)

推荐选择:
  VMware ESXi:
    推荐: NFSv3
    可选: NFSv4.1 (vSphere 6.0+)
    原因: 成熟稳定，广泛测试
  
  Linux环境:
    推荐: NFSv4.1
    原因: 更好性能和安全性
  
  混合环境:
    推荐: NFSv3
    原因: 兼容性最好
```

### 适用场景

```yaml
推荐场景:
  虚拟机存储:
    ✅ VMware ESXi虚拟机存储
    ✅ KVM虚拟机存储
    ✅ 模板和ISO库
    优势: 共享存储，支持vMotion
  
  文件共享:
    ✅ 团队共享目录
    ✅ 项目文件
    ✅ 媒体文件
    优势: POSIX兼容，权限管理
  
  容器存储:
    ✅ Kubernetes持久卷 (NFS CSI)
    ✅ Docker卷
    优势: 简单，易于配置
  
  备份存储:
    ✅ 备份目标
    ✅ 归档存储
    优势: 容量大，成本低
  
  开发环境:
    ✅ 代码共享
    ✅ 构建产物
    优势: 灵活，易于管理

不推荐场景:
  ❌ 高IOPS数据库 (>50K IOPS)
    原因: 文件级开销
    替代: iSCSI块存储
  
  ❌ 极低延迟要求 (<1ms)
    原因: 网络和协议开销
    替代: 本地SSD
  
  ❌ Windows主要环境
    原因: SMB/CIFS更原生
    替代: SMB 3.0
  
  ❌ 高并发写入
    原因: 文件锁竞争
    替代: 对象存储

性能预期:
  网络: 10GbE
  IOPS: 10,000-30,000
  延迟: 1-5ms
  带宽: 500MB/s-1GB/s
  
  对比iSCSI:
    IOPS: iSCSI > NFS
    延迟: iSCSI < NFS
    易用性: NFS > iSCSI
    文件操作: NFS > iSCSI
```

---

## NFS服务器配置

### Linux NFS服务器 (NFSv3)

```bash
#!/bin/bash
# NFS服务器配置脚本 - NFSv3
# 适用于: Ubuntu 22.04 / Rocky Linux 9

set -e

echo "========================================="
echo "  NFS服务器配置 (NFSv3)"
echo "========================================="
echo ""

# 1. 安装NFS服务器
echo "步骤1: 安装NFS服务器..."

if command -v apt &> /dev/null; then
    # Ubuntu/Debian
    apt update
    apt install -y nfs-kernel-server
elif command -v dnf &> /dev/null; then
    # CentOS/RHEL/Rocky Linux
    dnf install -y nfs-utils
fi

# 2. 创建NFS导出目录
echo ""
echo "步骤2: 创建导出目录..."

mkdir -p /export/vmware
mkdir -p /export/iso
mkdir -p /export/backup

# 设置权限
chown -R nobody:nogroup /export  # Ubuntu
# chown -R nfsnobody:nfsnobody /export  # CentOS

chmod -R 755 /export

echo "导出目录已创建:"
echo "  /export/vmware  - 虚拟机存储"
echo "  /export/iso     - ISO镜像库"
echo "  /export/backup  - 备份存储"

# 3. 配置NFS导出
echo ""
echo "步骤3: 配置NFS导出..."

cat > /etc/exports <<'EOF'
# NFS导出配置文件
# 格式: <导出路径> <客户端>(选项)

# 虚拟机存储 - 允许特定网段，读写，同步
/export/vmware 192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)

# ISO镜像库 - 只读，所有客户端
/export/iso *(ro,sync,no_subtree_check)

# 备份存储 - 允许特定主机，读写
/export/backup 192.168.1.100(rw,sync,no_subtree_check,no_root_squash) 192.168.1.101(rw,sync,no_subtree_check,no_root_squash)

# 选项说明:
# rw: 读写权限
# ro: 只读权限
# sync: 同步写入 (数据安全，性能略低)
# async: 异步写入 (性能高，数据风险)
# no_subtree_check: 禁用子树检查 (提升性能)
# no_root_squash: root用户不映射为nobody (谨慎使用)
# root_squash: root用户映射为nobody (默认，推荐)
# all_squash: 所有用户映射为nobody
# anonuid/anongid: 匿名用户映射的UID/GID

# 多个客户端示例:
# /export/data 192.168.1.0/24(rw) 10.0.0.0/8(ro)

# 单个主机示例:
# /export/data 192.168.1.100(rw,no_root_squash)

# 所有客户端示例 (不推荐生产环境):
# /export/public *(ro,all_squash)
EOF

echo "NFS导出配置已创建"

# 4. 应用NFS配置
echo ""
echo "步骤4: 应用配置..."

exportfs -ra  # 重新导出所有目录
exportfs -v   # 验证导出

# 5. 配置防火墙
echo ""
echo "步骤5: 配置防火墙..."

if command -v ufw &> /dev/null; then
    # Ubuntu UFW
    ufw allow from 192.168.1.0/24 to any port nfs
    ufw allow from 192.168.1.0/24 to any port 111
    ufw allow from 192.168.1.0/24 to any port 2049
    ufw status
elif command -v firewall-cmd &> /dev/null; then
    # CentOS/RHEL firewalld
    firewall-cmd --permanent --add-service=nfs
    firewall-cmd --permanent --add-service=rpc-bind
    firewall-cmd --permanent --add-service=mountd
    firewall-cmd --reload
    firewall-cmd --list-all
fi

# 6. 启动NFS服务
echo ""
echo "步骤6: 启动NFS服务..."

if command -v systemctl &> /dev/null; then
    systemctl enable nfs-server
    systemctl start nfs-server
    systemctl status nfs-server --no-pager
    
    # 启动RPC服务
    systemctl enable rpcbind
    systemctl start rpcbind
fi

# 7. 验证配置
echo ""
echo "========================================="
echo "  配置完成 - 验证"
echo "========================================="
echo ""

echo "NFS导出列表:"
showmount -e localhost

echo ""
echo "RPC服务状态:"
rpcinfo -p localhost | grep nfs

echo ""
echo "监听端口:"
ss -tlnp | grep -E '(2049|111)'

echo ""
echo "========================================="
echo "  完成"
echo "========================================="
echo ""
echo "客户端挂载命令:"
echo "  mount -t nfs 192.168.1.X:/export/vmware /mnt/vmware"
echo ""
echo "查看导出:"
echo "  showmount -e 192.168.1.X"
```

**NFS导出选项详解**:

```yaml
常用选项:
  访问权限:
    rw: 读写 (read-write)
    ro: 只读 (read-only)
  
  同步模式:
    sync: 
      同步写入磁盘
      数据安全
      性能较低
      推荐: 生产环境
    
    async:
      异步写入，先写缓存
      性能高
      数据风险 (断电可能丢失)
      推荐: 非关键数据
  
  用户映射:
    root_squash (默认):
      root用户映射为nobody
      安全
      推荐: 大多数场景
    
    no_root_squash:
      root用户保持root权限
      危险
      仅在需要时使用 (如VMware)
    
    all_squash:
      所有用户映射为nobody
      最安全
      用途: 公共只读共享
    
    anonuid=UID:
      匿名用户映射的UID
      配合all_squash使用
    
    anongid=GID:
      匿名用户映射的GID
  
  性能优化:
    no_subtree_check:
      禁用子树检查
      提升性能
      推荐: 导出整个文件系统
    
    subtree_check (默认):
      启用子树检查
      安全
      性能开销
  
  其他选项:
    no_wdelay:
      禁用写延迟
      提升小文件性能
      需要sync
    
    nohide:
      显示子挂载点
      用途: 导出嵌套文件系统
    
    crossmnt:
      允许跨挂载点
      NFSv4
    
    secure (默认):
      限制端口 <1024
    
    insecure:
      允许任意端口
      用于NFS客户端非root

配置示例:
  高性能虚拟化存储:
    /export/vmware 192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash,no_wdelay)
  
  只读ISO库:
    /export/iso *(ro,sync,no_subtree_check,all_squash)
  
  备份存储:
    /export/backup 192.168.1.0/24(rw,async,no_subtree_check)
  
  开发共享:
    /export/dev 192.168.1.0/24(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000)
```

### Linux NFS服务器 (NFSv4)

```bash
#!/bin/bash
# NFS服务器配置脚本 - NFSv4
# 适用于: Ubuntu 22.04 / Rocky Linux 9

set -e

echo "========================================="
echo "  NFS服务器配置 (NFSv4)"
echo "========================================="
echo ""

# 1. 安装NFS服务器
echo "步骤1: 安装NFS服务器..."

if command -v apt &> /dev/null; then
    apt update
    apt install -y nfs-kernel-server
elif command -v dnf &> /dev/null; then
    dnf install -y nfs-utils
fi

# 2. 创建NFSv4根目录
echo ""
echo "步骤2: 创建NFSv4根目录..."

# NFSv4使用伪根文件系统
NFS4_ROOT="/srv/nfs4"
mkdir -p $NFS4_ROOT

# 创建实际存储目录
mkdir -p /export/vmware
mkdir -p /export/iso

# 绑定挂载到NFSv4根
mkdir -p $NFS4_ROOT/vmware
mkdir -p $NFS4_ROOT/iso

# 方法1: 使用绑定挂载
mount --bind /export/vmware $NFS4_ROOT/vmware
mount --bind /export/iso $NFS4_ROOT/iso

# 方法2: 使用符号链接 (不推荐)
# ln -s /export/vmware $NFS4_ROOT/vmware

# 永久化绑定挂载
cat >> /etc/fstab <<EOF
# NFSv4绑定挂载
/export/vmware $NFS4_ROOT/vmware none bind 0 0
/export/iso $NFS4_ROOT/iso none bind 0 0
EOF

# 3. 配置NFSv4导出
echo ""
echo "步骤3: 配置NFSv4导出..."

cat > /etc/exports <<EOF
# NFSv4导出配置

# NFSv4根目录 (fsid=0必须)
$NFS4_ROOT 192.168.1.0/24(rw,sync,fsid=0,no_subtree_check,crossmnt)

# 子目录 (NFSv4会自动包含在根下)
$NFS4_ROOT/vmware 192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)
$NFS4_ROOT/iso 192.168.1.0/24(ro,sync,no_subtree_check)

# NFSv4选项说明:
# fsid=0: 标记为NFSv4根文件系统
# crossmnt: 允许跨挂载点
EOF

# 4. 配置NFSv4特定设置
echo ""
echo "步骤4: 配置NFSv4设置..."

# 编辑 /etc/nfs.conf (如果存在)
if [ -f /etc/nfs.conf ]; then
    cat >> /etc/nfs.conf <<EOF

[nfsd]
# 强制NFSv4
vers4=y
vers4.0=y
vers4.1=y
vers4.2=y

# 禁用NFSv3 (可选)
# vers3=n

# 线程数 (根据CPU核心数调整)
threads=16
EOF
fi

# Ubuntu使用 /etc/default/nfs-kernel-server
if [ -f /etc/default/nfs-kernel-server ]; then
    sed -i 's/^RPCNFSDCOUNT=.*/RPCNFSDCOUNT=16/' /etc/default/nfs-kernel-server
fi

# 5. 应用配置
echo ""
echo "步骤5: 应用配置..."

exportfs -ra
exportfs -v

# 6. 配置防火墙 (NFSv4只需2049)
echo ""
echo "步骤6: 配置防火墙..."

if command -v ufw &> /dev/null; then
    ufw allow from 192.168.1.0/24 to any port 2049
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=nfs
    firewall-cmd --reload
fi

# 7. 启动服务
echo ""
echo "步骤7: 启动NFS服务..."

systemctl enable nfs-server
systemctl restart nfs-server
systemctl status nfs-server --no-pager

# 8. 验证
echo ""
echo "========================================="
echo "  配置完成 - 验证"
echo "========================================="
echo ""

echo "NFSv4导出:"
exportfs -v

echo ""
echo "监听端口 (应仅有2049):"
ss -tlnp | grep 2049

echo ""
echo "========================================="
echo "  完成"
echo "========================================="
echo ""
echo "客户端挂载命令 (NFSv4):"
echo "  mount -t nfs4 192.168.1.X:/ /mnt"
echo "  mount -t nfs4 192.168.1.X:/vmware /mnt/vmware"
echo ""
echo "注意: NFSv4使用伪文件系统，根目录为 /"
```

### FreeNAS/TrueNAS NFS

```yaml
TrueNAS NFS配置 (Web界面):
  步骤1: 创建数据集
    导航: Storage → Pools
    操作:
      1. 选择存储池
      2. 点击 "Add Dataset"
      3. 名称: nfs_vmware
      4. 共享类型: Generic
      5. 保存
  
  步骤2: 创建NFS共享
    导航: Sharing → Unix Shares (NFS)
    操作:
      1. 点击 "Add"
      2. 路径: 选择刚创建的数据集
      3. 描述: VMware NFS Storage
      4. 保存
  
  步骤3: 配置NFS共享
    编辑NFS共享:
      基本选项:
        Path: /mnt/pool/nfs_vmware
        Description: VMware NFS Storage
        Enabled: ✓
      
      访问控制:
        Authorized Networks: 192.168.1.0/24
        Authorized Hosts: (留空允许网段内所有)
      
      高级选项:
        Maproot User: root (VMware需要)
        Maproot Group: wheel
        或: Mapall User/Group (所有用户映射)
      
      NFSv4选项:
        NFSv4: ✓ (启用)
        NFSv3 ownership model: ✓ (兼容性)
  
  步骤4: 配置NFS服务
    导航: Services → NFS
    点击配置图标:
      
      General Options:
        Number of servers: 16
        Bind IP Addresses: (所有或特定IP)
        Enable NFSv4: ✓
        NFSv3 ownership model: ✓
        Require Kerberos: ☐ (除非需要)
      
      NFSv4 Options:
        Support NFSv4: ✓
        NFSv4 v4_krb_enabled: ☐
        NFSv4 v4_domain: (留空或DNS域名)
      
      保存
  
  步骤5: 启动NFS服务
    导航: Services
    操作:
      1. 找到 "NFS"
      2. 点击开关启用
      3. 勾选 "Start Automatically"
  
  验证:
    从客户端测试:
      showmount -e <TrueNAS-IP>
    
    应显示:
      /mnt/pool/nfs_vmware 192.168.1.0/24

性能优化:
  启用异步写入 (可选):
    在共享高级选项中:
      - 勾选 "Async"
      - 提升性能，但数据风险
  
  调整块大小:
    系统 → 调优:
      - vfs.nfsd.async: 1
      - vfs.nfsrv.async: 1
      - vfs.nfsrv.io_maxbsize: 131072
```

---

## VMware ESXi NFS配置

### 挂载NFS数据存储

```bash
#!/bin/bash
# ESXi NFS数据存储挂载脚本

ESXi_HOST="192.168.1.101"
NFS_SERVER="192.168.1.10"
NFS_PATH="/export/vmware"
DATASTORE_NAME="nfs-vmware01"

echo "========================================="
echo "  ESXi NFS数据存储挂载"
echo "========================================="
echo ""

# 方法1: 使用esxcli命令行

# NFSv3挂载
echo "挂载NFSv3数据存储..."
esxcli storage nfs add \
  --host=$NFS_SERVER \
  --share=$NFS_PATH \
  --volume-name=$DATASTORE_NAME

# NFSv4.1挂载 (ESXi 6.0+)
echo "挂载NFSv4.1数据存储..."
esxcli storage nfs41 add \
  --host=$NFS_SERVER \
  --share=$NFS_PATH \
  --volume-name=$DATASTORE_NAME

# 查看NFS数据存储
echo ""
echo "NFS数据存储列表:"
esxcli storage nfs list
esxcli storage nfs41 list

# 卸载NFS数据存储
# esxcli storage nfs remove --volume-name=$DATASTORE_NAME
# esxcli storage nfs41 remove --volume-name=$DATASTORE_NAME

echo ""
echo "========================================="
echo "  完成"
echo "========================================="
```

**ESXi GUI配置步骤**:

```yaml
通过vSphere Client配置:
  步骤1: 导航到存储
    1. 登录vSphere Client
    2. 选择ESXi主机
    3. 配置 → 存储 → 数据存储
  
  步骤2: 新建数据存储
    1. 点击 "新建数据存储"
    2. 类型: 选择 "挂载NFS数据存储"
    3. 点击 "下一步"
  
  步骤3: 选择NFS版本
    选择:
      - NFS 3 (推荐)
      - NFS 4.1 (ESXi 6.0+)
    
    点击 "下一步"
  
  步骤4: 提供NFS挂载详细信息
    NFS 3配置:
      名称: nfs-vmware01
      NFS服务器: 192.168.1.10
      NFS共享: /export/vmware
      访问模式: 读写 (默认)
    
    NFS 4.1配置:
      名称: nfs41-vmware01
      服务器: 192.168.1.10
      NFS共享: /vmware (NFSv4路径)
      访问模式: 读写
      Kerberos认证: 无 (默认)
    
    点击 "下一步"
  
  步骤5: 主机可访问性
    选择可以访问此数据存储的主机
    勾选需要挂载的主机
    点击 "下一步"
  
  步骤6: 即将完成
    审核配置
    点击 "完成"
  
  验证:
    1. 数据存储列表应显示新NFS存储
    2. 状态: 正常
    3. 类型: NFS或NFS 4.1
    4. 容量: 显示可用空间

NFS数据存储特点:
  - 文件系统: 服务器端文件系统 (如ext4)
  - 不创建VMFS
  - 支持精简置备
  - 支持vMotion
  - 不支持原始设备映射 (RDM)
```

### NFSv4.1会话中继

```yaml
NFSv4.1会话中继 (ESXi 6.5+):
  定义:
    多路径NFS
    使用多个网络路径访问NFS
    类似于iSCSI多路径
  
  优势:
    ✅ 负载均衡
    ✅ 故障切换
    ✅ 提升带宽
    ✅ 降低延迟
  
  要求:
    - ESXi 6.5 U1+
    - NFSv4.1
    - 多个VMkernel端口
    - NFS服务器多网卡
  
  配置步骤:
    1. 创建多个VMkernel端口
       vmk1: 192.168.20.101
       vmk2: 192.168.20.102
    
    2. NFS服务器配置多IP
       eth0: 192.168.20.10
       eth1: 192.168.20.11
    
    3. 挂载NFSv4.1数据存储时
       ESXi自动检测多路径
       自动配置会话中继
    
    4. 验证
       esxcli storage nfs41 list
       查看 "IPs" 字段应显示多个IP
  
  注意事项:
    - 仅NFSv4.1支持
    - NFSv3不支持多路径
    - 需要网络支持 (VLAN/路由)
```

---

## Linux NFS客户端配置

```bash
#!/bin/bash
# Linux NFS客户端挂载脚本

NFS_SERVER="192.168.1.10"
NFS_PATH="/export/vmware"
MOUNT_POINT="/mnt/nfs_vmware"

echo "========================================="
echo "  Linux NFS客户端配置"
echo "========================================="
echo ""

# 1. 安装NFS客户端
echo "步骤1: 安装NFS客户端..."

if command -v apt &> /dev/null; then
    apt update
    apt install -y nfs-common
elif command -v dnf &> /dev/null; then
    dnf install -y nfs-utils
fi

# 2. 查看NFS服务器导出
echo ""
echo "步骤2: 查看NFS导出..."
showmount -e $NFS_SERVER

# 3. 创建挂载点
echo ""
echo "步骤3: 创建挂载点..."
mkdir -p $MOUNT_POINT

# 4. 临时挂载 (NFSv3)
echo ""
echo "步骤4: 临时挂载NFSv3..."
mount -t nfs \
  -o rw,hard,intr,rsize=131072,wsize=131072,tcp \
  $NFS_SERVER:$NFS_PATH $MOUNT_POINT

# 或挂载NFSv4
# mount -t nfs4 \
#   -o rw,hard,intr,rsize=131072,wsize=131072 \
#   $NFS_SERVER:/vmware $MOUNT_POINT

# 5. 验证挂载
echo ""
echo "步骤5: 验证挂载..."
df -h $MOUNT_POINT
mount | grep nfs

# 6. 性能测试
echo ""
echo "步骤6: 性能测试..."
dd if=/dev/zero of=$MOUNT_POINT/test.dat bs=1M count=1024 2>&1 | grep MB/s
rm -f $MOUNT_POINT/test.dat

# 7. 永久挂载 (/etc/fstab)
echo ""
echo "步骤7: 配置永久挂载..."

# 备份fstab
cp /etc/fstab /etc/fstab.bak

# 添加NFS挂载
cat >> /etc/fstab <<EOF

# NFS挂载 - VMware存储
$NFS_SERVER:$NFS_PATH $MOUNT_POINT nfs rw,hard,intr,rsize=131072,wsize=131072,tcp,_netdev 0 0

# 或NFSv4
# $NFS_SERVER:/vmware $MOUNT_POINT nfs4 rw,hard,intr,rsize=131072,wsize=131072,_netdev 0 0
EOF

# 测试fstab
mount -a

echo ""
echo "========================================="
echo "  配置完成"
echo "========================================="
echo ""
echo "挂载点: $MOUNT_POINT"
echo "验证: df -h $MOUNT_POINT"
```

**NFS挂载选项详解**:

```yaml
基本选项:
  版本:
    nfs: 自动检测 (通常NFSv3)
    nfs4: 强制NFSv4
    vers=3: 强制NFSv3
    vers=4.1: 强制NFSv4.1
  
  访问模式:
    rw: 读写 (默认)
    ro: 只读
  
  错误处理:
    hard (推荐):
      NFS请求失败时无限重试
      适用: 生产环境，防止数据损坏
    
    soft:
      NFS请求失败后返回错误
      适用: 非关键数据
      风险: 数据可能损坏
  
    intr:
      允许中断NFS请求
      推荐: 配合hard使用
    
    timeo=600:
      超时时间 (0.1秒单位)
      默认: 600 (60秒)
    
    retrans=2:
      重传次数
      默认: 3

性能选项:
  传输大小:
    rsize=131072:
      读取块大小 (128KB)
      推荐: 131072 或 262144
      影响: 读性能
    
    wsize=131072:
      写入块大小 (128KB)
      推荐: 131072 或 262144
      影响: 写性能
  
  协议:
    tcp (推荐):
      使用TCP协议
      稳定
    
    udp:
      使用UDP协议
      仅NFSv3
      不推荐
  
  缓存:
    ac (默认):
      启用属性缓存
      提升性能
    
    noac:
      禁用属性缓存
      实时性
      性能下降
    
    actimeo=60:
      属性缓存超时 (秒)
      默认: 3-60秒动态
  
  锁:
    lock:
      启用文件锁 (默认)
    
    nolock:
      禁用文件锁
      提升性能
      适用: 单客户端

系统选项:
  _netdev:
    网络文件系统标记
    系统启动时等待网络
    推荐: 永久挂载必须
  
  bg:
    后台挂载
    挂载失败时重试
    适用: 启动时挂载
  
  nofail:
    挂载失败不报错
    系统启动继续
  
  x-systemd.automount:
    systemd自动挂载
    按需挂载
    提升启动速度

推荐配置:
  生产虚拟化:
    $SERVER:$PATH $MOUNT nfs rw,hard,intr,rsize=131072,wsize=131072,tcp,timeo=600,_netdev 0 0
  
  高性能:
    $SERVER:$PATH $MOUNT nfs4 rw,hard,intr,rsize=262144,wsize=262144,_netdev 0 0
  
  备份存储:
    $SERVER:$PATH $MOUNT nfs rw,soft,intr,rsize=131072,wsize=131072,tcp,_netdev 0 0
  
  开发环境:
    $SERVER:$PATH $MOUNT nfs rw,hard,intr,nolock,_netdev 0 0
```

---

## Windows NFS客户端配置

```powershell
# PowerShell脚本 - Windows NFS客户端配置

# 检查管理员权限
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "需要管理员权限运行此脚本" -ForegroundColor Red
    exit 1
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Windows NFS客户端配置" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$NFSServer = "192.168.1.10"
$NFSPath = "/export/vmware"
$DriveLetter = "Z:"

# 1. 安装NFS客户端
Write-Host "步骤1: 安装NFS客户端..." -ForegroundColor Green

# Windows 10/11 Pro
$nfsFeature = Get-WindowsOptionalFeature -Online -FeatureName ServicesForNFS-ClientOnly

if ($nfsFeature.State -ne "Enabled") {
    Write-Host "正在安装NFS客户端..." -ForegroundColor Yellow
    Enable-WindowsOptionalFeature -Online -FeatureName ServicesForNFS-ClientOnly -All -NoRestart
    Write-Host "NFS客户端已安装" -ForegroundColor Green
} else {
    Write-Host "NFS客户端已安装" -ForegroundColor Green
}

# Windows Server
# Install-WindowsFeature NFS-Client

# 2. 启动NFS客户端服务
Write-Host ""
Write-Host "步骤2: 启动NFS客户端服务..." -ForegroundColor Green
Start-Service -Name NfsClnt -ErrorAction SilentlyContinue
Set-Service -Name NfsClnt -StartupType Automatic

# 3. 配置NFS客户端设置
Write-Host ""
Write-Host "步骤3: 配置NFS客户端..." -ForegroundColor Green

# 配置UID/GID (避免权限问题)
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\ClientForNFS\CurrentVersion\Default" `
    -Name "AnonymousUid" -Value 0
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\ClientForNFS\CurrentVersion\Default" `
    -Name "AnonymousGid" -Value 0

# 重启NFS服务
Restart-Service -Name NfsClnt

# 4. 查看NFS导出
Write-Host ""
Write-Host "步骤4: 查看NFS导出..." -ForegroundColor Green
showmount -e $NFSServer

# 5. 挂载NFS共享
Write-Host ""
Write-Host "步骤5: 挂载NFS共享..." -ForegroundColor Green

$MountPath = "${NFSServer}:${NFSPath}"

# 临时挂载
mount -o anon $MountPath $DriveLetter

# 或永久挂载 (开机自动)
# mount -o anon,persistent $MountPath $DriveLetter

# 或使用mtype和nolock选项
# mount -o mtype=hard,anon,nolock $MountPath $DriveLetter

# 6. 验证挂载
Write-Host ""
Write-Host "步骤6: 验证挂载..." -ForegroundColor Green
Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Name -eq $DriveLetter.TrimEnd(':')}

# 列出所有NFS挂载
mount

# 7. 测试访问
Write-Host ""
Write-Host "步骤7: 测试访问..." -ForegroundColor Green
Test-Path "$DriveLetter\"

# 8. 卸载NFS共享 (可选)
# umount $DriveLetter
# 或
# umount -f $DriveLetter  # 强制卸载

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  配置完成" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NFS共享已挂载到: $DriveLetter" -ForegroundColor Green
Write-Host ""
Write-Host "管理命令:" -ForegroundColor Yellow
Write-Host "  查看挂载: mount" -ForegroundColor White
Write-Host "  卸载: umount $DriveLetter" -ForegroundColor White
```

**GUI配置步骤**:

```yaml
Windows资源管理器挂载:
  方法1: 通过映射网络驱动器
    1. 打开资源管理器
    2. 右键 "此电脑"
    3. 映射网络驱动器
    4. 驱动器: Z:
    5. 文件夹: \\192.168.1.10\export\vmware
    6. 注意: Windows将NFS路径解释为SMB路径
       需要使用命令行mount
  
  方法2: 使用命令行 (推荐)
    以管理员运行CMD或PowerShell:
      mount -o anon \\192.168.1.10\export\vmware Z:
    
    或指定用户:
      mount -o mtype=hard,anon \\192.168.1.10\export\vmware Z:

常见选项:
  anon:
    使用匿名访问
    推荐: 大多数场景
  
  mtype=hard:
    硬挂载，失败时重试
    推荐: 生产环境
  
  persistent:
    永久挂载，重启后保留
    语法: mount -o persistent ...
  
  nolock:
    禁用文件锁
    提升性能
  
  rsize=131072:
    读取块大小
  
  wsize=131072:
    写入块大小

故障排查:
  问题: 拒绝访问
    解决:
      1. 设置UID/GID为0 (root)
      2. NFS服务器使用no_root_squash
      3. 检查防火墙
  
  问题: 无法看到文件
    解决:
      1. 检查NFS导出权限
      2. 确认客户端IP在允许列表
      3. 重启NFS服务
```

---

## 网络优化

```yaml
网络配置最佳实践:
  专用VLAN:
    VLAN ID: 20 (示例)
    IP段: 192.168.20.0/24
    用途: NFS存储流量
    隔离: 与业务网络分离
  
  Jumbo Frame:
    MTU: 9000
    要求:
      ✅ NFS服务器: MTU 9000
      ✅ NFS客户端: MTU 9000
      ✅ 交换机: 启用Jumbo Frame
    
    优势:
      ✅ 减少CPU开销 (20-30%)
      ✅ 提升吞吐量 (10-20%)
      ✅ 降低延迟
    
    配置:
      Linux服务器:
        ip link set eth1 mtu 9000
      
      ESXi VMkernel:
        esxcli network ip interface set -i vmk1 -m 9000
      
      验证:
        ping -M do -s 8972 192.168.20.10
        # 8972 = 9000 - 28 (IP+ICMP header)
  
  链路聚合 (不推荐用于NFS):
    说明: NFS难以有效利用LACP
    原因: 单个NFS连接通常走单路径
    替代: 使用多个NFS挂载点
  
  QoS:
    优先级: 高
    DSCP: EF (46)
    CoS: 5-7
    目的: 保证NFS流量优先

网络测试:
  延迟测试:
    ping -c 100 192.168.20.10
    # 应 <1ms (同交换机)
  
  带宽测试:
    iperf3 -c 192.168.20.10 -t 60
    # 10GbE应接近9Gbps
  
  NFS性能测试:
    dd if=/dev/zero of=/mnt/nfs/test bs=1M count=10240
    # 测试写入带宽
```

---

## 性能优化

```yaml
服务器端优化:
  NFS线程数:
    查看:
      cat /proc/fs/nfsd/threads
    
    设置 (临时):
      echo 16 > /proc/fs/nfsd/threads
    
    永久配置:
      # Ubuntu: /etc/default/nfs-kernel-server
      RPCNFSDCOUNT=16
      
      # CentOS: /etc/nfs.conf
      [nfsd]
      threads=16
    
    推荐: 2-4个线程/CPU核心
    计算: 16核 × 2 = 32线程
  
  异步写入 (谨慎):
    /etc/exports:
      /export/data *(rw,async,no_subtree_check)
    
    优势: 提升写性能50-100%
    风险: 断电可能数据丢失
    推荐: 仅非关键数据
  
  读写缓存:
    增加内核缓存:
      # /etc/sysctl.conf
      vm.dirty_ratio = 15
      vm.dirty_background_ratio = 5
      vm.vfs_cache_pressure = 50
      
      sysctl -p
  
  文件系统优化:
    XFS (推荐NFS):
      mkfs.xfs -i size=512 /dev/sdb1
      mount -o noatime,nodiratime /dev/sdb1 /export
    
    ext4:
      mkfs.ext4 -E lazy_itable_init=0 /dev/sdb1
      mount -o noatime,data=writeback /dev/sdb1 /export
    
    挂载选项:
      noatime: 不更新访问时间 (提升性能)
      nodiratime: 不更新目录访问时间

客户端优化:
  挂载选项:
    rsize/wsize:
      推荐: 131072 (128KB) 或 262144 (256KB)
      测试: 逐步增加，观察性能
    
    缓存:
      ac: 启用属性缓存 (默认)
      actimeo=60: 缓存60秒
    
    错误处理:
      hard,intr,timeo=600
    
    完整示例:
      mount -t nfs \
        -o rw,hard,intr,rsize=262144,wsize=262144,tcp,timeo=600 \
        192.168.1.10:/export/vmware /mnt/vmware
  
  预读:
    查看:
      blockdev --getra /dev/sdb
    
    设置 (KB):
      blockdev --setra 4096 /dev/sdb  # 2MB

ESXi优化:
  高级设置:
    NFS.MaxVolumes: 256
    NFS.MaxQueueDepth: 128
    NFS.SendBufferSize: 262144
    NFS.ReceiveBufferSize: 262144
  
  配置方法:
    esxcli system settings advanced set \
      -o /NFS/MaxQueueDepth -i 128

性能监控:
  Linux nfsstat:
    nfsstat -c  # 客户端统计
    nfsstat -s  # 服务器统计
    nfsstat -m  # 挂载统计
    
    watch -n 1 nfsstat -c
  
  观察指标:
    retrans: 重传 (应接近0)
    timeouts: 超时 (应为0)
    rpc ops/s: RPC操作/秒
    read/write MB/s: 吞吐量
```

---

## 安全配置

```yaml
访问控制:
  IP限制:
    /etc/exports:
      # 单个IP
      /export/data 192.168.1.100(rw)
      
      # 子网
      /export/data 192.168.1.0/24(rw)
      
      # 多个网段
      /export/data 192.168.1.0/24(rw) 10.0.0.0/8(ro)
      
      # 主机名 (需DNS)
      /export/data client.example.com(rw)
  
  用户映射:
    root_squash (默认):
      安全，推荐大多数场景
    
    no_root_squash:
      危险，仅在需要时使用
      用途: VMware, 容器
    
    all_squash:
      最安全
      所有用户映射为nobody
      用途: 公共只读共享

防火墙配置:
  UFW (Ubuntu):
    # NFSv3
    ufw allow from 192.168.1.0/24 to any port nfs
    ufw allow from 192.168.1.0/24 to any port 111
    
    # NFSv4
    ufw allow from 192.168.1.0/24 to any port 2049
  
  firewalld (CentOS):
    # NFSv3
    firewall-cmd --permanent --add-service=nfs
    firewall-cmd --permanent --add-service=rpc-bind
    firewall-cmd --permanent --add-service=mountd
    
    # 或仅NFSv4
    firewall-cmd --permanent --add-port=2049/tcp
    
    firewall-cmd --reload
  
  iptables:
    # NFSv4
    iptables -A INPUT -p tcp --dport 2049 -s 192.168.1.0/24 -j ACCEPT
    iptables -A INPUT -p tcp --dport 2049 -j DROP

Kerberos认证 (NFSv4):
  说明: 企业级安全认证
  配置复杂度: 高
  适用: 高安全需求
  
  基本步骤:
    1. 配置Kerberos KDC
    2. 创建NFS服务主体
    3. 配置/etc/krb5.conf
    4. 启用sec=krb5
  
  挂载示例:
    mount -t nfs4 -o sec=krb5p server:/path /mnt
  
  安全级别:
    sec=sys: 基于UID/GID (默认)
    sec=krb5: Kerberos认证
    sec=krb5i: 认证+完整性
    sec=krb5p: 认证+完整性+加密

审计:
  启用审计日志:
    # /etc/audit/rules.d/nfs.rules
    -w /etc/exports -p wa -k nfs_exports
    -w /export -p wa -k nfs_data
    
    service auditd restart
  
  查看日志:
    ausearch -k nfs_exports
    ausearch -k nfs_data

最佳实践:
  ✅ 使用专用VLAN隔离NFS流量
  ✅ 限制客户端IP范围
  ✅ 使用root_squash (除非必需)
  ✅ 启用防火墙
  ✅ 定期更新NFS软件
  ✅ 监控NFS访问日志
  ✅ 考虑使用NFSv4 + Kerberos (高安全)
  ❌ 不要将NFS暴露到公网
  ❌ 不要使用 *(all hosts) 在生产环境
  ❌ 避免使用async (关键数据)
```

---

## 监控与故障排查

```bash
#!/bin/bash
# NFS监控和诊断脚本

echo "========================================="
echo "  NFS监控和诊断"
echo "========================================="
echo ""

# 服务器端诊断
if command -v nfsstat &> /dev/null && [ -d /etc/exports.d ]; then
    echo "=== NFS服务器状态 ==="
    
    # NFS导出
    echo "NFS导出:"
    exportfs -v
    
    echo ""
    echo "NFS统计:"
    nfsstat -s
    
    echo ""
    echo "RPC信息:"
    rpcinfo -p localhost
    
    echo ""
    echo "活动连接:"
    ss -tn | grep :2049
fi

# 客户端诊断
if command -v nfsstat &> /dev/null && mount | grep -q nfs; then
    echo "=== NFS客户端状态 ==="
    
    # NFS挂载
    echo "NFS挂载点:"
    mount | grep nfs
    
    echo ""
    echo "NFS统计:"
    nfsstat -c
    
    echo ""
    echo "挂载详情:"
    nfsstat -m
    
    echo ""
    echo "RPC统计:"
    nfsstat -r
fi

# 性能测试
NFS_MOUNT=$(mount | grep " nfs" | head -1 | awk '{print $3}')
if [ -n "$NFS_MOUNT" ] && [ -w "$NFS_MOUNT" ]; then
    echo "=== NFS性能测试 ==="
    
    echo "写入测试 (100MB):"
    dd if=/dev/zero of=$NFS_MOUNT/test_write.dat bs=1M count=100 2>&1 | grep MB/s
    
    echo ""
    echo "读取测试 (100MB):"
    dd if=$NFS_MOUNT/test_write.dat of=/dev/null bs=1M 2>&1 | grep MB/s
    
    rm -f $NFS_MOUNT/test_write.dat
fi

# 网络诊断
NFS_SERVER=$(mount | grep " nfs" | head -1 | awk -F: '{print $1}')
if [ -n "$NFS_SERVER" ]; then
    echo ""
    echo "=== 网络诊断 ==="
    
    echo "Ping测试:"
    ping -c 4 $NFS_SERVER
    
    echo ""
    echo "MTU测试:"
    ping -M do -s 8972 -c 2 $NFS_SERVER 2>&1 | tail -3
    
    echo ""
    echo "端口连通性:"
    nc -zv $NFS_SERVER 2049 2>&1
fi

echo ""
echo "========================================="
echo "  诊断完成"
echo "========================================="
```

**常见问题和解决方案**:

```yaml
问题1: 挂载超时 (mount.nfs: Connection timed out)
  原因:
    - 网络不通
    - 防火墙阻止
    - NFS服务未启动
  
  排查:
    1. Ping NFS服务器
    2. 检查端口: nc -zv <server> 2049
    3. 查看服务: systemctl status nfs-server
    4. 检查防火墙: firewall-cmd --list-all
  
  解决:
    - 启动NFS服务
    - 开放防火墙端口
    - 检查网络配置

问题2: 权限拒绝 (Permission denied)
  原因:
    - 客户端IP不在允许列表
    - 用户映射问题
    - 文件系统权限
  
  排查:
    1. 检查/etc/exports
    2. exportfs -v
    3. ls -ld /export/path
  
  解决:
    - 添加客户端IP到exports
    - 使用no_root_squash (谨慎)
    - 调整文件系统权限

问题3: 性能差
  原因:
    - 网络延迟高
    - rsize/wsize太小
    - 未启用Jumbo Frame
    - 服务器I/O瓶颈
  
  排查:
    1. ping测试延迟
    2. nfsstat查看重传
    3. iostat查看磁盘
    4. iftop查看带宽
  
  解决:
    - 增加rsize/wsize
    - 启用Jumbo Frame (MTU 9000)
    - 增加NFS线程数
    - 升级到SSD存储

问题4: Stale file handle
  原因:
    - NFS服务器重启
    - 导出配置变更
    - 文件系统卸载
  
  解决:
    - 卸载并重新挂载
      umount -f /mnt/nfs
      mount /mnt/nfs
    
    - 或强制卸载
      umount -l /mnt/nfs  # 懒卸载

问题5: 文件锁问题
  症状:
    - 文件无法打开
    - "Resource temporarily unavailable"
  
  原因:
    - NFSv3锁机制问题
    - statd/lockd服务
  
  解决:
    - 重启锁服务:
      systemctl restart nfs-lock
    
    - 或使用nolock挂载:
      mount -o nolock ...
    
    - 升级到NFSv4 (更好的锁)

日志位置:
  服务器端:
    /var/log/syslog  # Ubuntu
    /var/log/messages  # CentOS
    
    实时监控:
      tail -f /var/log/syslog | grep nfs
  
  客户端:
    dmesg | grep nfs
    journalctl -u nfs-client.target
```

---

## 相关文档

- [存储类型与选型标准](01_存储类型与选型标准.md)
- [iSCSI配置与优化](02_iSCSI配置与优化.md)
- [存储性能优化](06_存储性能优化.md)
- [存储容灾与备份](07_存储容灾与备份.md)
- [网络架构配置](../04_网络架构/)

---

**更新时间**: 2025-10-19  
**文档版本**: v3.0  
**状态**: ✅ 生产就绪
