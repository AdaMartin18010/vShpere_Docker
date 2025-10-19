# VMware ESXi安装与配置

> **返回**: [软件安装目录](README.md) | [虚拟化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [VMware ESXi安装与配置](#vmware-esxi安装与配置)
  - [📋 目录](#-目录)
  - [ESXi安装准备](#esxi安装准备)
    - [下载ESXi镜像](#下载esxi镜像)
    - [制作启动U盘](#制作启动u盘)
    - [服务器准备清单](#服务器准备清单)
    - [自动化安装配置 (Kickstart)](#自动化安装配置-kickstart)
  - [ESXi交互式安装](#esxi交互式安装)
    - [安装流程](#安装流程)
    - [安装后首次配置](#安装后首次配置)
    - [Web界面访问](#web界面访问)
  - [ESXi存储配置](#esxi存储配置)
    - [创建VMFS数据存储](#创建vmfs数据存储)
    - [挂载NFS数据存储](#挂载nfs数据存储)
    - [存储最佳实践](#存储最佳实践)
  - [ESXi网络配置](#esxi网络配置)
    - [创建标准交换机 (vSwitch)](#创建标准交换机-vswitch)
    - [创建端口组](#创建端口组)
    - [网络最佳实践](#网络最佳实践)
  - [vCenter Server部署](#vcenter-server部署)
    - [VCSA部署方式](#vcsa部署方式)
    - [VCSA部署步骤](#vcsa部署步骤)
    - [首次登录配置](#首次登录配置)
  - [创建数据中心和集群](#创建数据中心和集群)
    - [创建数据中心](#创建数据中心)
    - [创建集群](#创建集群)
    - [配置资源池](#配置资源池)
  - [相关文档](#相关文档)

---

## ESXi安装准备

### 下载ESXi镜像

```yaml
版本选择:
  ESXi 8.0 U2:
    状态: 最新稳定版 (推荐)
    发布日期: 2024年
    支持周期: 至2027年
    文件名: VMware-VMvisor-Installer-8.0U2-xxxxxxx.iso
    大小: ~500MB
  
  ESXi 7.0 U3:
    状态: 长期支持版
    发布日期: 2023年
    支持周期: 至2027年
    文件名: VMware-VMvisor-Installer-7.0U3-xxxxxxx.iso
    说明: 适合老硬件

下载地址:
  官方网站: https://my.vmware.com
  步骤:
    1. 注册VMware账号 (免费)
    2. 登录 My VMware
    3. 导航到: Products and Accounts → All Products
    4. 选择: VMware vSphere
    5. 选择版本: 8.0 U2
    6. 选择: ESXi ISO image (Includes VMware Tools)
    7. 下载ISO文件

许可证类型:
  免费版 (vSphere Hypervisor):
    功能:
      ✅ 基础虚拟化
      ✅ vSphere Web Client
      ✅ VMFS数据存储
      ❌ vCenter集中管理
      ❌ vMotion在线迁移
      ❌ HA高可用
    适用: 小型环境、学习测试
    获取: 免费，需注册许可证密钥
  
  标准版 (vSphere Standard):
    功能:
      ✅ 包含免费版所有功能
      ✅ vCenter管理
      ✅ vMotion在线迁移
      ❌ DRS自动负载均衡
      ❌ HA高可用
    适用: 中小型生产环境
  
  企业版 (vSphere Enterprise Plus):
    功能:
      ✅ 包含标准版所有功能
      ✅ DRS自动负载均衡
      ✅ HA高可用
      ✅ 分布式交换机
      ✅ Storage DRS
      ✅ vSAN (需单独许可)
    适用: 大型生产环境
```

### 制作启动U盘

```yaml
Windows方法:
  工具: Rufus 3.20+
  下载: https://rufus.ie
  
  步骤:
    1. 准备U盘:
       - 容量: 8GB+ (推荐16GB)
       - 格式: 将被格式化，请备份数据
    
    2. 启动Rufus:
       - 插入U盘
       - 打开Rufus软件
       - 自动检测U盘
    
    3. 配置参数:
       - 设备: 选择你的U盘
       - 引导类型选择: 选择 "磁盘或ISO镜像"
       - 点击 "选择" 按钮，选择ESXi ISO文件
       - 分区类型: GPT
       - 目标系统: UEFI (非CSM)
       - 文件系统: FAT32 (默认)
       - 簇大小: 默认
    
    4. 开始制作:
       - 点击 "开始" 按钮
       - 警告：将清除U盘所有数据
       - 点击 "确定" 确认
       - 等待完成 (约5-10分钟)
    
    5. 完成:
       - 显示 "准备就绪"
       - 关闭Rufus
       - 安全移除U盘

Linux/Mac方法:
  工具: dd命令
  
  步骤:
    1. 查找U盘设备:
       Linux:
         lsblk
         # 假设U盘是 /dev/sdb
       
       Mac:
         diskutil list
         # 假设U盘是 /dev/disk2
    
    2. 卸载U盘 (不要拔出):
       Linux:
         sudo umount /dev/sdb*
       
       Mac:
         diskutil unmountDisk /dev/disk2
    
    3. 写入ISO:
       Linux:
         sudo dd if=VMware-VMvisor-Installer-8.0U2.iso of=/dev/sdb bs=4M status=progress
         sudo sync
       
       Mac:
         sudo dd if=VMware-VMvisor-Installer-8.0U2.iso of=/dev/rdisk2 bs=1m
         # 注意: Mac使用 /dev/rdisk2 (raw disk) 更快
       
       ⚠️ 警告: 确保of=后的设备路径正确，否则会损坏其他磁盘！
    
    4. 完成:
       等待命令完成 (约5-10分钟)
       安全移除U盘

验证U盘:
  1. 重新插入U盘
  2. 检查文件:
     - 应包含: EFI/ 目录
     - 应包含: BOOT.CFG 文件
     - 应包含: BOOTX64.EFI 文件
  3. U盘标签应为: ESXi-8.0U2-xxx
```

### 服务器准备清单

```yaml
硬件准备:
  BIOS配置:
    ☐ 已启用虚拟化功能 (VT-x/AMD-V)
    ☐ 已启用VT-d/AMD-Vi
    ☐ 已启用超线程 (Hyper-Threading)
    ☐ 已配置电源模式为 Performance
    ☐ 启动模式设置为 UEFI
    参考: [BIOS配置清单](../01_硬件规范/06_BIOS固件配置清单.md)
  
  RAID配置:
    ☐ 系统盘已配置为 RAID1 (推荐)
    ☐ RAID卡缓存已启用
    ☐ RAID卡BBU/FBWC已安装
    ☐ RAID配置已保存
  
  网络准备:
    ☐ 网线已连接到管理网口 (通常是第一个网口)
    ☐ 交换机端口已配置 (如需VLAN)
    ☐ 已分配静态IP地址
    ☐ 已记录网络配置信息
  
  远程管理:
    ☐ iDRAC/iLO/iBMC已配置 (可选，推荐)
    ☐ 远程管理IP已设置
    ☐ 远程管理网线已连接
    ☐ 可通过远程控制台操作

信息记录:
  服务器信息:
    序列号: __________________
    服务型号: __________________
    资产编号: __________________
  
  网络配置:
    管理IP: __________________
    子网掩码: __________________
    默认网关: __________________
    DNS服务器: __________________
    主机名: __________________
  
  凭证信息:
    ESXi Root密码: __________________
    iDRAC/iLO密码: __________________
```

### 自动化安装配置 (Kickstart)

```bash
# ESXi Kickstart配置文件 (ks.cfg)
# 用于无人值守批量部署

# 接受最终用户许可协议
vmaccepteula

# 清除数据存储: 0表示清除所有内容
clearpart --alldrives --overwritevmfs

# 安装到第一块硬盘
install --firstdisk --overwritevmfs

# 设置Root密码
rootpw VMware@2025

# 网络配置
network --bootproto=static --device=vmnic0 --ip=192.168.1.101 --netmask=255.255.255.0 --gateway=192.168.1.1 --nameserver=8.8.8.8,8.8.4.4 --hostname=esxi-01.domain.local --vlanid=0

# 安装后重启
reboot

# 安装后执行的脚本
%firstboot --interpreter=busybox

# 启用SSH和ESXi Shell
vim-cmd hostsvc/enable_ssh
vim-cmd hostsvc/start_ssh
vim-cmd hostsvc/enable_esx_shell
vim-cmd hostsvc/start_esx_shell

# 配置NTP
esxcli system ntp set --server=ntp.aliyun.com
esxcli system ntp set --server=ntp1.aliyun.com
esxcli system ntp set --enabled=yes

# 配置防火墙允许NTP
esxcli network firewall ruleset set --ruleset-id=ntpClient --enabled=yes

# 设置主机名
esxcli system hostname set --fqdn=esxi-01.domain.local

# 禁用IPv6 (可选)
esxcli network ip set --ipv6-enabled=false

# 创建本地数据存储 (如有第二块磁盘)
# esxcli storage filesystem automount

# 配置高级系统设置
esxcli system settings advanced set -o /UserVars/SuppressShellWarning -i 1
esxcli system settings advanced set -o /UserVars/ESXiShellTimeOut -i 0

# 重启管理服务
/etc/init.d/hostd restart
/etc/init.d/vpxa restart

# 输出完成信息
echo "ESXi 自动化配置完成" > /tmp/kickstart_complete.log

%end

# 使用方法:
# 1. 将此文件保存为 ks.cfg
# 2. 放置到Web服务器 (如 http://192.168.1.100/ks.cfg)
# 3. 启动ESXi安装，在引导菜单按 Shift+O
# 4. 输入: ks=http://192.168.1.100/ks.cfg
# 5. 按回车开始自动安装
```

---

## ESXi交互式安装

### 安装流程

```yaml
步骤1: 启动安装程序
  操作:
    1. 插入U盘到服务器USB接口
    2. 开机，进入BIOS启动菜单:
       - Dell: F11
       - HP: F9
       - Lenovo: F12
       - Cisco: F6
       - 浪潮: F11
    3. 选择U盘启动设备
    4. 等待加载ESXi安装程序 (约30秒)
    5. 看到欢迎界面: "Welcome to VMware ESXi 8.0.2 Installation"
  
  故障排除:
    无法从U盘启动:
      - 检查BIOS启动模式是否为UEFI
      - 检查U盘是否正确制作
      - 尝试不同的USB接口
    
    启动后黑屏:
      - 等待更长时间（某些服务器较慢）
      - 检查显示器连接

步骤2: 接受许可协议
  操作:
    1. 按 Enter 继续
    2. 按 F11 接受EULA许可协议
  
  说明:
    - 必须接受才能继续
    - 许可协议为VMware最终用户许可协议

步骤3: 选择安装磁盘
  界面显示:
    列出所有可用存储设备
    显示: 设备名称、容量、类型、状态
  
  操作:
    1. 使用方向键 ↑↓ 选择目标磁盘
    2. 按 Enter 确认
  
  ⚠️ 警告:
    选择的磁盘上所有数据将被清除！
    请确保选择正确的磁盘！
  
  推荐选择:
    ✅ RAID1镜像盘 (生产环境首选)
    ✅ 本地SSD (性能优先)
    ✅ USB/SD卡 (小型环境，需16GB+)
    ❌ 避免选择数据盘
  
  设备标识:
    t10.xxx: SATA/SAS磁盘
    naa.xxx: FC/iSCSI LUN
    mpx.xxx: 多路径设备
    eui.xxx: NVMe设备

步骤4: 选择键盘布局
  操作:
    1. 默认: US Default (美式键盘)
    2. 可选择其他布局（如需）
    3. 按 Enter 继续
  
  说明:
    中文环境通常使用US Default即可

步骤5: 设置Root密码
  操作:
    1. 输入密码
    2. 再次输入确认密码
    3. 按 Enter 继续
  
  密码策略:
    要求:
      ✅ 至少7个字符
      ✅ 包含大小写字母
      ✅ 包含数字
      ✅ 包含特殊字符 (推荐)
    
    示例:
      VMware@2025
      ESXi@Admin123
      P@ssw0rd2025
    
    ⚠️ 注意:
      - 密码不会显示在屏幕上
      - 请牢记此密码
      - 建议使用密码管理器记录

步骤6: 扫描升级信息
  操作:
    自动扫描，无需操作
    等待完成（约5-10秒）
  
  说明:
    检查是否有现有ESXi安装

步骤7: 确认安装
  界面显示:
    安装摘要:
      - 安装磁盘: /dev/disks/xxx (XX GB)
      - 键盘布局: US Default
  
  操作:
    1. 检查安装摘要
    2. 按 F11 开始安装
    3. 等待安装过程（约5-10分钟）
  
  安装进度:
    显示进度条: [=====>    ] 50%
    显示状态: Installing ESXi
  
  ⚠️ 最后确认:
    按F11后将开始安装！
    所选磁盘数据将被清除！

步骤8: 安装完成
  操作:
    1. 显示: "Installation Complete"
    2. 移除安装U盘
    3. 按 Enter 重启服务器
  
  说明:
    - 必须移除U盘，避免再次进入安装程序
    - 如果忘记移除，再次启动安装程序时按 Esc 退出
```

### 安装后首次配置

```yaml
步骤1: 进入DCUI控制台
  操作:
    1. 服务器重启后自动进入DCUI
    2. 显示ESXi版本和IP信息
    3. 按 F2 进入系统定制
    4. 输入root密码登录
  
  界面说明:
    DCUI = Direct Console User Interface
    黄色背景界面，显示基本信息

步骤2: 配置管理网络
  操作:
    1. 选择 "Configure Management Network"
    2. 按 Enter 进入
  
  子菜单说明:
    Network Adapters: 选择管理网卡
    VLAN (optional): 配置VLAN
    IPv4 Configuration: 配置IPv4地址
    IPv6 Configuration: 配置IPv6地址 (可选)
    DNS Configuration: 配置DNS和主机名
    Custom DNS Suffixes: 配置DNS后缀 (可选)

  配置管理网卡:
    1. 选择 "Network Adapters"
    2. 列出所有物理网卡:
       - vmnic0: Intel I350 1Gbps
       - vmnic1: Intel I350 1Gbps
       - ...
    3. 使用空格键选中 vmnic0
    4. 按 Enter 确认
    
    推荐:
      ✅ 仅选择1个网卡作为管理网络
      ✅ 选择第一个网口 (vmnic0)
      ✅ 预留其他网卡给VM网络
  
  配置VLAN (可选):
    1. 选择 "VLAN (optional)"
    2. 如果管理网络在特定VLAN:
       - 输入VLAN ID (如: 100)
    3. 如果不需要VLAN:
       - 留空或输入0
    4. 按 Enter 确认
  
  配置IPv4地址:
    1. 选择 "IPv4 Configuration"
    2. 选择配置方式:
       - Set static IPv4 address and network configuration (推荐)
       - Use DHCP (仅测试环境)
    3. 如果选择静态IP，输入:
       - IPv4 Address: 192.168.1.101
       - Subnet Mask: 255.255.255.0
       - Default Gateway: 192.168.1.1
    4. 按 Enter 确认
    
    IP地址规划建议:
      ESXi-01: 192.168.1.101
      ESXi-02: 192.168.1.102
      ESXi-03: 192.168.1.103
      vCenter: 192.168.1.10
  
  配置DNS:
    1. 选择 "DNS Configuration"
    2. 配置:
       - Primary DNS Server: 8.8.8.8
       - Alternate DNS Server: 8.8.4.4
       - Hostname: esxi-01
       - Domain: domain.local
    3. 按 Enter 确认
    
    完整FQDN:
      esxi-01.domain.local
  
  保存配置:
    1. 按 Esc 返回主菜单
    2. 提示: "Apply changes and restart management network?"
    3. 按 Y 确认
    4. 等待网络重启（约5秒）

步骤3: 测试管理网络
  操作:
    1. 返回主菜单
    2. 选择 "Test Management Network"
    3. 按 Enter 开始测试
    4. 等待测试完成（约10秒）
  
  测试项目:
    ✅ Ping default gateway (192.168.1.1): OK
    ✅ Ping primary DNS server (8.8.8.8): OK
    ✅ Ping alternate DNS server (8.8.4.4): OK
    ✅ Resolve hostname (esxi-01.domain.local): OK
  
  故障排除:
    Ping网关失败:
      - 检查网线连接
      - 检查交换机端口状态
      - 检查网卡指示灯
    
    Ping DNS失败:
      - 检查网关配置
      - 检查DNS服务器地址
      - 检查防火墙规则

步骤4: 启用SSH和ESXi Shell
  操作:
    1. 返回主菜单
    2. 选择 "Troubleshooting Options"
    3. 启用服务:
       - Enable ESXi Shell: 按 Enter 启用
       - Enable SSH: 按 Enter 启用
    4. 按 Esc 返回
  
  说明:
    SSH: 允许远程命令行访问
    ESXi Shell: 本地命令行界面
  
  ⚠️ 安全提示:
    生产环境中SSH应在配置完成后禁用
    或配置SSH密钥认证，禁用密码登录

步骤5: 查看系统信息
  操作:
    按 F12 查看系统日志和信息
  
  显示内容:
    - 系统版本
    - 硬件信息
    - 网络状态
    - 系统日志
```

### Web界面访问

```yaml
访问ESXi Host Client:
  URL:
    https://192.168.1.101
    或: https://esxi-01.domain.local
  
  登录凭证:
    用户名: root
    密码: 安装时设置的Root密码
  
  浏览器要求:
    支持: Chrome, Firefox, Edge (最新版本)
    不支持: IE (已弃用)
  
  SSL证书警告:
    首次访问会显示证书警告
    原因: ESXi使用自签名证书
    操作:
      Chrome: 点击 "高级" → "继续访问"
      Firefox: 点击 "高级" → "接受风险并继续"

主界面导航:
  左侧菜单:
    导航器:
      - 主机: 查看主机概要信息
      - 虚拟机: 管理虚拟机
      - 存储: 管理数据存储
      - 网络: 管理网络
      - 监控: 性能监控
    
    清单:
      - 虚拟机列表
      - 数据存储列表
      - 网络列表
  
  主面板:
    主机概要:
      - CPU使用率
      - 内存使用率
      - 存储使用率
      - 正在运行的VM数量
    
    选项卡:
      - 监控: 性能图表
      - 配置: 系统配置
      - 虚拟机: VM列表
      - 存储: 数据存储
      - 网络: 网络拓扑
      - 许可: 许可证管理

基础配置任务:
  配置许可证:
    步骤:
      1. 导航到: 主机 → 管理 → 许可
      2. 点击 "分配许可证"
      3. 输入许可证密钥
      4. 或选择 "评估模式" (60天)
      5. 点击 "确定"
    
    说明:
      免费版: 需从VMware获取免费许可证密钥
      评估版: 自动激活60天全功能
  
  配置时间同步:
    步骤:
      1. 导航到: 主机 → 管理 → 时间和日期
      2. 点击 "编辑设置"
      3. 选择: "使用网络时间协议 (启用NTP客户端)"
      4. NTP服务器:
         - ntp.aliyun.com
         - ntp1.aliyun.com
      5. NTP服务策略: "随主机一起启动并停止"
      6. 点击 "保存"
  
  配置防火墙:
    步骤:
      1. 导航到: 主机 → 管理 → 安全配置文件
      2. 编辑防火墙规则
      3. 允许服务:
         ✅ SSH (端口22)
         ✅ NTP Client (端口123)
         ✅ vSphere Web Client (端口443)
         ✅ iSCSI (端口3260) - 如需
      4. 点击 "确定"
  
  配置高级设置:
    步骤:
      1. 导航到: 主机 → 管理 → 高级设置
      2. 常用设置:
         - UserVars.SuppressShellWarning: 1 (禁用Shell警告)
         - UserVars.ESXiShellTimeOut: 0 (禁用Shell超时)
         - UserVars.DcuiTimeOut: 600 (DCUI超时时间)
      3. 修改后点击 "保存"
```

---

## ESXi存储配置

### 创建VMFS数据存储

```yaml
VMFS数据存储说明:
  VMFS: Virtual Machine File System
  版本: VMFS6 (ESXi 6.5+)
  用途: 存储虚拟机文件、ISO镜像等
  优势:
    ✅ 集群文件系统
    ✅ 支持大文件
    ✅ 支持快照
    ✅ 支持精简置备

创建步骤:
  1. 导航到存储:
     左侧菜单 → 存储 → 数据存储
  
  2. 新建数据存储:
     点击 "新建数据存储" 按钮
  
  3. 选择类型:
     选择: "创建新VMFS数据存储"
     点击 "下一步"
  
  4. 命名数据存储:
     名称: datastore1
     或更具描述性的名称:
       - local-ssd-esxi01
       - nvme-datastore1
     点击 "下一步"
  
  5. 选择设备:
     显示: 所有可用存储设备
     列出: 设备名称、容量、类型
     
     选择未使用的磁盘或RAID卷
     
     设备标识:
       naa.xxx: SAN LUN
       t10.xxx: 本地磁盘
       eui.xxx: NVMe SSD
     
     点击 "下一步"
  
  6. 选择VMFS版本:
     选择: VMFS 6 (推荐)
     说明: VMFS 6是最新版本，支持所有新特性
     点击 "下一步"
  
  7. 分区配置:
     选项:
       - 使用全部可用空间 (推荐)
       - 自定义分区大小
     
     如果自定义:
       输入大小 (GB)
     
     点击 "下一步"
  
  8. 准备完成:
     审核配置:
       - 数据存储名称
       - 设备
       - VMFS版本
       - 容量
     
     点击 "完成"
  
  9. 等待创建:
     格式化磁盘
     创建VMFS文件系统
     挂载数据存储
     完成 (约10-30秒)

验证数据存储:
  1. 刷新数据存储列表
  2. 确认新数据存储出现
  3. 检查容量和可用空间
  4. 右键点击 → "浏览" 查看内容
```

### 挂载NFS数据存储

```yaml
NFS数据存储说明:
  NFS: Network File System
  版本: NFS 3 (推荐), NFS 4.1 (ESXi 6.0+)
  用途: 共享存储，多主机访问
  优势:
    ✅ 共享数据存储
    ✅ 支持vMotion
    ✅ 易于管理和扩展
    ✅ 无需专用存储控制器

前提条件:
  NFS服务器要求:
    ✅ 已安装NFS服务
    ✅ 已创建NFS导出目录
    ✅ 已配置导出权限
    ✅ ESXi主机能访问NFS服务器
  
  网络要求:
    ✅ ESXi和NFS服务器在同一网络
    ✅ 网络延迟低 (<1ms 推荐)
    ✅ 足够带宽 (10GbE 推荐)
    ✅ 防火墙允许NFS流量 (端口2049)

NFS服务器配置示例:
  Linux NFS服务器:
    ```bash
    # 安装NFS服务
    apt install nfs-kernel-server  # Ubuntu
    dnf install nfs-utils          # Rocky Linux
    
    # 创建导出目录
    mkdir -p /export/vmware
    chown -R nobody:nogroup /export/vmware
    chmod 777 /export/vmware
    
    # 配置导出
    cat >> /etc/exports <<EOF
    /export/vmware 192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)
    EOF
    
    # 应用配置
    exportfs -ra
    
    # 启动NFS服务
    systemctl enable nfs-server
    systemctl start nfs-server
    
    # 验证导出
    showmount -e localhost
    ```

挂载步骤:
  1. 导航到存储:
     左侧菜单 → 存储 → 数据存储
  
  2. 新建数据存储:
     点击 "新建数据存储" 按钮
  
  3. 选择类型:
     选择: "挂载NFS数据存储"
     点击 "下一步"
  
  4. 配置NFS:
     名称: nfs-datastore1
     
     NFS服务器: 192.168.2.10
     
     NFS共享: /export/vmware
     
     NFS版本: NFS 3 (推荐)
     或: NFS 4.1 (需服务器支持)
     
     访问模式: 读写 (默认)
     或: 只读 (特殊场景)
     
     点击 "下一步"
  
  5. 准备完成:
     审核配置
     点击 "完成"
  
  6. 等待挂载:
     连接NFS服务器
     挂载共享目录
     完成 (约5-10秒)

验证NFS数据存储:
  1. 刷新数据存储列表
  2. 确认NFS数据存储出现
  3. 类型显示为: NFS
  4. 容量应与NFS服务器一致
  5. 右键点击 → "浏览" 测试访问

故障排除:
  无法挂载NFS:
    ☐ 检查NFS服务器是否运行
    ☐ 检查网络连接 (ping NFS服务器)
    ☐ 检查防火墙规则
    ☐ 检查NFS导出权限
    ☐ 检查ESXi防火墙 (允许NFS客户端)
  
  性能问题:
    ☐ 使用10GbE网络
    ☐ 启用Jumbo Frame (MTU 9000)
    ☐ 使用NFS 4.1 (更好性能)
    ☐ 优化NFS服务器配置
```

### 存储最佳实践

```yaml
命名规范:
  本地存储:
    - local-esxi01
    - local-ssd-node1
    - local-nvme-host1
  
  SSD存储:
    - ssd-datastore1
    - ssd-high-performance
  
  NFS存储:
    - nfs-storage1
    - nfs-shared-prod
  
  iSCSI存储:
    - iscsi-lun01
    - iscsi-san-storage

性能优化:
  系统分配:
    ESXi系统盘: 使用RAID1 SSD
    VM系统盘: 使用NVMe或SSD
    VM数据盘: 根据需求选择
    ISO镜像: 可使用HDD或NFS
  
  VMFS设置:
    块大小: 1MB (默认，适合大多数场景)
    精简置备: 根据需求启用
    预留空间: 建议预留10-20%
  
  硬件加速:
    ✅ 启用VAAI (vSphere Storage APIs for Array Integration)
    ✅ 启用VASA (vSphere APIs for Storage Awareness)
    作用: 卸载存储操作到阵列，提升性能

存储分层:
  Tier 0 (最高性能):
    介质: NVMe SSD
    用途: 数据库、关键业务
    RAID: RAID10
  
  Tier 1 (高性能):
    介质: SATA/SAS SSD
    用途: 生产虚拟机
    RAID: RAID10
  
  Tier 2 (标准):
    介质: HDD
    用途: 归档、备份
    RAID: RAID6

容量规划:
  虚拟机存储:
    - 每个VM平均: 100GB
    - 50个VM: 5TB
    - 加20%余量: 6TB
  
  快照存储:
    - 预留10-20%用于快照
    - 避免长期保留快照
  
  ISO/模板存储:
    - 100-500GB独立数据存储
    - 可使用NFS共享

多路径配置 (仅SAN):
  策略:
    - VMW_PSP_RR: 轮询 (推荐，负载均衡)
    - VMW_PSP_MRU: 最近使用 (默认)
    - VMW_PSP_FIXED: 固定路径
  
  配置:
    esxcli storage nmp device set --device naa.xxx --psp VMW_PSP_RR
```

---

## ESXi网络配置

### 创建标准交换机 (vSwitch)

```yaml
虚拟交换机说明:
  标准交换机 (vSS):
    - vSphere Standard Switch
    - 每台ESXi主机独立配置
    - 免费，包含在vSphere中
    - 适合中小型环境
  
  分布式交换机 (vDS):
    - vSphere Distributed Switch
    - 集中管理，需vCenter
    - 需Enterprise Plus许可
    - 适合大型环境

创建标准交换机:
  1. 导航到网络:
     左侧菜单 → 网络 → 虚拟交换机
  
  2. 添加交换机:
     点击 "添加标准虚拟交换机"
  
  3. 配置基本设置:
     名称: vSwitch1
     
     MTU: 
       - 1500 (标准以太网)
       - 9000 (Jumbo Frame，推荐用于存储网络)
     
     上行链路数: 2 (推荐，冗余)
  
  4. 选择上行链路:
     可用网卡:
       vmnic0: Intel I350 1Gbps (已用于管理)
       vmnic1: Intel I350 1Gbps (可用)
       vmnic2: Intel X710 10Gbps (可用)
       vmnic3: Intel X710 10Gbps (可用)
     
     选择:
       上行链路1: vmnic2
       上行链路2: vmnic3
     
     说明: 选择高速网卡用于业务网络
  
  5. 安全策略:
     混杂模式: 拒绝 (推荐)
     MAC地址更改: 接受
     伪传输: 接受
  
  6. NIC组合:
     负载均衡:
       - Route based on originating virtual port (默认)
       - Route based on IP hash (需要交换机支持)
       - Route based on physical NIC load (负载均衡)
     
     网络故障切换检测:
       - Link status only (推荐)
       - Beacon probing (需要)
     
     通知交换机: 是 (推荐)
     
     故障切换: 是 (推荐)
  
  7. 完成创建:
     点击 "添加"
     新交换机出现在列表中

编辑现有交换机:
  1. 点击交换机名称
  2. 查看拓扑图:
     - 显示上行链路
     - 显示端口组
     - 显示连接的VM
  
  3. 编辑设置:
     点击 "编辑设置"
     修改配置后保存
```

### 创建端口组

```yaml
端口组说明:
  作用: 定义网络策略和VLAN
  用途:
    - VM业务网络
    - vMotion网络
    - 存储网络 (iSCSI/NFS)
    - 管理网络

创建VM业务网络端口组:
  1. 导航到端口组:
     网络 → 端口组
  
  2. 添加端口组:
     点击 "添加端口组"
  
  3. 配置:
     名称: VM-Network-VLAN10
     
     VLAN ID: 10
     说明: 0=不使用VLAN, 1-4094=VLAN ID, 4095=trunk
     
     虚拟交换机: vSwitch1
     
     安全策略: 继承自vSwitch (推荐)
  
  4. 完成创建:
     点击 "添加"

创建存储网络端口组:
  配置:
    名称: Storage-Network-VLAN20
    VLAN ID: 20
    虚拟交换机: vSwitch0
    
    用途: iSCSI, NFS存储流量
    
    优化:
      - MTU: 9000 (Jumbo Frame)
      - 流量整形: 可选
  
  iSCSI绑定:
    1. 创建VMkernel端口
    2. 启用iSCSI流量
    3. 绑定到iSCSI适配器

创建vMotion网络端口组:
  配置:
    名称: vMotion-Network-VLAN30
    VLAN ID: 30
    虚拟交换机: vSwitch0
    
    用途: vMotion实时迁移
  
  VMkernel端口:
    1. 创建VMkernel网络适配器
    2. 启用vMotion服务
    3. 配置IP地址:
       - IP: 192.168.30.101
       - 掩码: 255.255.255.0
    4. MTU: 9000 (推荐)

创建管理网络端口组:
  说明:
    管理网络通常在安装时已创建
    默认名称: Management Network
    默认交换机: vSwitch0
  
  如需修改:
    1. 点击 "Management Network"
    2. 编辑设置
    3. 修改VLAN ID或其他参数
    4. 保存

端口组优先级:
  高优先级 (独立交换机):
    - 管理网络
    - vMotion网络
    - 存储网络
  
  标准优先级:
    - VM业务网络
```

### 网络最佳实践

```yaml
物理网卡分配:
  小型环境 (4个网口):
    vmnic0: 管理网络 (1GbE)
    vmnic1: 管理网络备份 (1GbE)
    vmnic2: VM业务网络 (10GbE)
    vmnic3: VM业务网络 (10GbE)
  
  中型环境 (6个网口):
    vmnic0: 管理网络 (1GbE)
    vmnic1: vMotion网络 (10GbE)
    vmnic2-3: 存储网络 (10GbE, 绑定)
    vmnic4-5: VM业务网络 (10GbE, 绑定)
  
  大型环境 (8+个网口):
    vmnic0: 管理网络 (1GbE)
    vmnic1: vMotion网络 (10/25GbE)
    vmnic2-3: 存储网络 (10/25GbE, LACP)
    vmnic4-5: VM业务网络1 (10/25GbE, LACP)
    vmnic6-7: VM业务网络2 (10/25GbE, LACP)

链路聚合配置:
  支持的策略:
    Route based on originating virtual port:
      - 默认策略
      - 简单，无需交换机配置
      - 单个VM流量不跨多个上行链路
    
    Route based on IP hash:
      - 需要交换机支持LACP/802.3ad
      - 真正的负载均衡
      - 单个VM可使用多个上行链路
      - 推荐用于生产环境
    
    Route based on physical NIC load:
      - ESXi 6.7+
      - 自动负载均衡
      - 无需交换机配置
  
  配置LACP (IP Hash):
    1. 交换机端配置LACP
    2. ESXi端选择 "Route based on IP hash"
    3. 确保上行链路在同一LACP组

故障切换配置:
  Active-Active (推荐):
    - 所有上行链路同时使用
    - 负载均衡
    - 高带宽利用率
  
  Active-Standby:
    - 一个上行链路active
    - 其他standby备用
    - 故障时自动切换
    - 适合管理网络

网络隔离:
  VLAN规划:
    VLAN 1: 默认/原生VLAN (不使用)
    VLAN 10: 管理网络
    VLAN 20: 存储网络
    VLAN 30: vMotion网络
    VLAN 100-199: VM业务网络
  
  物理隔离:
    管理/vMotion: 独立交换机
    存储: 独立交换机或VLAN
    业务: 独立交换机或VLAN

性能优化:
  Jumbo Frame:
    用途: 存储和vMotion网络
    MTU: 9000
    要求: 整条链路支持 (ESXi, 交换机, 存储)
    
    配置:
      1. 交换机启用Jumbo Frame
      2. ESXi vSwitch MTU设为9000
      3. VMkernel端口MTU设为9000
      4. 存储设备MTU设为9000
    
    验证:
      vmkping -d -s 8972 192.168.20.10
      # 8972 = 9000 - 28 (IP+ICMP header)
  
  TSO/LRO:
    自动启用，无需配置
    作用: 降低CPU使用率

安全配置:
  混杂模式: 拒绝 (除非有特殊需求)
  MAC地址更改: 接受 (正常VM操作需要)
  伪传输: 接受 (正常VM操作需要)
```

---

## vCenter Server部署

### VCSA部署方式

```yaml
vCenter Server Appliance (VCSA):
  说明:
    - 基于Photon OS (Linux)
    - 内置PostgreSQL数据库
    - OVF/OVA格式部署
    - 免费，包含在vSphere许可中
  
  优点:
    ✅ 部署简单，向导式安装
    ✅ 资源占用低
    ✅ 无需Windows许可
    ✅ 内置数据库，无需外部DB
    ✅ 支持本机HA
  
  缺点:
    ⚠️ 仅支持内置PostgreSQL
    ⚠️ 备份较复杂（需专用工具）

Windows vCenter Server:
  说明:
    从vSphere 7.0开始已弃用
    不推荐新部署
  
  如果必须使用:
    - 需要Windows Server许可
    - 需要外部SQL Server数据库
    - 资源占用更高

VCSA硬件要求:
  最小配置 (Tiny):
    vCPU: 2核
    内存: 12GB
    磁盘: 250GB
    适用: <10台主机, <100虚拟机
  
  小型配置 (Small):
    vCPU: 4核
    内存: 16GB
    磁盘: 300GB
    适用: 10-100台主机, 100-1000虚拟机
  
  中型配置 (Medium):
    vCPU: 8核
    内存: 24GB
    磁盘: 500GB
    适用: 100-400台主机, 1000-4000虚拟机
  
  大型配置 (Large):
    vCPU: 16核
    内存: 32GB
    磁盘: 750GB
    适用: 400-1000台主机, 4000-10000虚拟机
  
  超大型配置 (X-Large):
    vCPU: 24核
    内存: 48GB
    磁盘: 1TB
    适用: >1000台主机, >10000虚拟机
```

### VCSA部署步骤

```yaml
阶段1: 部署VCSA OVF到ESXi

步骤1: 挂载VCSA ISO
  Windows:
    - 双击ISO文件自动挂载
    - 或右键 → 挂载
  
  Linux:
    mount -o loop VMware-VCSA-all-8.0.2-xxx.iso /mnt
  
  Mac:
    - 双击ISO文件自动挂载

步骤2: 运行安装程序
  Windows:
    vcsa-ui-installer\win32\installer.exe
  
  Linux:
    vcsa-ui-installer/lin64/installer
  
  Mac:
    vcsa-ui-installer/mac/Installer.app

步骤3: 欢迎界面
  选择: "安装"
  说明: 
    - 安装: 新部署vCenter
    - 升级: 从旧版本升级
    - 迁移: 从Windows vCenter迁移
    - 还原: 从备份还原

步骤4: 接受许可协议
  勾选: "我接受许可协议的条款"
  点击: "下一步"

步骤5: vCenter Server部署目标
  ESXi主机或vCenter Server名称或IP地址:
    192.168.1.101
  
  HTTPS端口:
    443 (默认)
  
  用户名:
    root
  
  密码:
    (ESXi的root密码)
  
  点击: "下一步"
  
  证书警告:
    显示: ESXi使用自签名证书
    勾选: "接受"
    点击: "是"

步骤6: 设置vCenter Server虚拟机
  虚拟机名称:
    vcenter-01
  
  设置root密码:
    输入: VMware@2025
    确认: VMware@2025
  
  说明:
    - 这是vCenter Appliance的root密码
    - 不是vCenter管理员密码（后面配置）
  
  点击: "下一步"

步骤7: 选择部署规模
  部署规模选项:
    - Tiny (最小): <10主机, <100VM
      CPU: 2核, 内存: 12GB, 存储: 250GB
    
    - Small (小型): <100主机, <1000VM
      CPU: 4核, 内存: 16GB, 存储: 300GB
    
    - Medium (中型): <400主机, <4000VM
      CPU: 8核, 内存: 24GB, 存储: 500GB
    
    - Large (大型): <1000主机, <10000VM
      CPU: 16核, 内存: 32GB, 存储: 750GB
    
    - X-Large (超大型): >1000主机, >10000VM
      CPU: 24核, 内存: 48GB, 存储: 1TB
  
  存储规模:
    - Default (默认)
    - Large (大型) - 用于增强的Logging和Events
  
  选择合适的规模
  点击: "下一步"

步骤8: 选择数据存储
  数据存储:
    选择: datastore1 (或其他可用数据存储)
  
  启用精简磁盘模式:
    勾选 (推荐，节省空间)
    不勾选 (性能优先)
  
  点击: "下一步"

步骤9: 配置网络设置
  网络:
    选择: VM Network (或其他业务网络)
  
  IP版本:
    选择: IPv4
  
  IP分配:
    选择: 静态
  
  系统名称 (FQDN):
    vcenter-01.domain.local
    或: vcenter.company.com
  
  IP地址:
    192.168.1.10
  
  子网掩码或前缀长度:
    255.255.255.0
    或: 24
  
  默认网关:
    192.168.1.1
  
  DNS服务器:
    8.8.8.8
    或多个: 8.8.8.8,8.8.4.4
  
  点击: "下一步"

步骤10: 即将完成阶段1
  审核所有设置:
    - vCenter Server名称
    - 部署规模
    - 数据存储
    - 网络配置
  
  点击: "完成"
  
  部署进度:
    阶段1: 部署OVF模板
    显示进度条
    时间: 约10-15分钟
    
    状态:
      - 传输OVF文件
      - 创建虚拟机
      - 配置虚拟机
      - 启动虚拟机
      - 初始化服务
  
  完成提示:
    "阶段1已成功完成"
    点击: "继续" 进入阶段2

阶段2: 设置vCenter Server

步骤1: 开始阶段2
  显示: vCenter Server设置
  点击: "下一步"

步骤2: vCenter Server配置
  时间同步模式:
    选项:
      - 与ESXi主机同步 (推荐，简单)
      - 与NTP服务器同步 (推荐，准确)
    
    如果选择NTP:
      NTP服务器:
        ntp.aliyun.com
        ntp1.aliyun.com
  
  SSH访问:
    启用SSH: 否 (推荐，安全)
    或: 是 (调试需要)
  
  点击: "下一步"

步骤3: SSO配置
  Single Sign-On配置:
    选择: "创建新的SSO域"
    (如果有现有vCenter，可选择加入)
  
  Single Sign-On域名:
    vsphere.local (默认，推荐)
    说明: 不要使用实际DNS域名
  
  Single Sign-On用户名:
    administrator (默认，不可更改)
    完整用户名: administrator@vsphere.local
  
  Single Sign-On密码:
    输入: VMware@2025
    确认: VMware@2025
    
    要求:
      - 至少8个字符
      - 包含大小写字母
      - 包含数字
      - 包含特殊字符
  
  站点名称:
    Default-Site (默认)
    或自定义: Beijing-Site
  
  点击: "下一步"

步骤4: 加入CEIP
  客户体验改进计划:
    选项:
      - 加入VMware CEIP (发送使用数据)
      - 不加入 (推荐，隐私)
    
    根据需要选择
  
  点击: "下一步"

步骤5: 即将完成
  审核配置:
    - vCenter Server URL
    - SSO域
    - 管理员账号
  
  点击: "完成"
  
  配置进度:
    阶段2: 配置vCenter Server
    显示进度条
    时间: 约5-10分钟
    
    状态:
      - 配置SSO
      - 配置vCenter Server
      - 启动服务
      - 初始化数据库
  
  完成提示:
    "设置成功"
    显示vCenter Server信息:
      - vCenter Server: https://192.168.1.10:443
      - Getting Started URL: https://192.168.1.10/ui
  
  点击: "确定"
```

### 首次登录配置

```yaml
访问vCenter:
  URL:
    https://192.168.1.10/ui
    或: https://vcenter-01.domain.local/ui
  
  浏览器:
    推荐: Chrome, Firefox, Edge (最新版本)
  
  SSL证书:
    首次访问显示证书警告
    原因: 自签名证书
    操作: 接受并继续

登录凭证:
  vSphere Client:
    用户名: administrator@vsphere.local
    密码: VMware@2025 (SSO密码)
  
  Appliance Management:
    URL: https://192.168.1.10:5480
    用户名: root
    密码: VMware@2025 (Appliance root密码)

首次登录向导:
  1. 语言选择:
     选择: 简体中文 或 English
  
  2. 许可证配置:
     导航到: 菜单 → 管理 → 许可
     
     操作:
       - 点击 "许可证"
       - 点击 "添加新许可证"
       - 输入vCenter Server许可证密钥
       - 点击 "添加新许可证"
       - 输入vSphere许可证密钥
       - 点击 "确定"
     
     分配许可证:
       - 选择vCenter Server
       - 点击 "分配许可证"
       - 选择vCenter许可证
       - 点击 "确定"
  
  3. 证书配置 (可选):
     导航到: 管理 → 证书 → 证书管理
     
     选项:
       - 使用自签名证书 (默认)
       - 替换为CA签名证书 (推荐生产环境)
       - 配置证书自动续订
  
  4. 身份源配置 (可选):
     导航到: 管理 → Single Sign On → 配置 → 身份源
     
     选项:
       - 本地用户 (默认，vsphere.local)
       - Active Directory (企业环境推荐)
       - LDAP (可选)
     
     添加AD:
       - 域: company.com
       - 用户名: administrator@company.com
       - 密码: (AD管理员密码)
  
  5. 权限配置:
     导航到: 管理 → 访问控制 → 全局权限
     
     添加管理员:
       - 点击 "添加权限"
       - 选择用户/组
       - 分配角色: Administrator
       - 勾选 "传播到子对象"
       - 点击 "确定"

验证vCenter:
  检查服务:
    1. 导航到: 菜单 → 管理 → 系统配置 → 服务
    2. 确认所有服务状态为: "正在运行"
    3. 关键服务:
       ✅ VMware vCenter Server
       ✅ VMware vSphere Web Client
       ✅ VMware vAPI Endpoint
       ✅ VMware vSphere Profile-Driven Storage
  
  检查健康状况:
    1. 导航到: 菜单 → 主机和集群
    2. 选择: vCenter Server实例
    3. 选项卡: 监控 → vCenter Server健康状况
    4. 检查:
       ✅ 存储器: 绿色
       ✅ CPU: 绿色
       ✅ 内存: 绿色
       ✅ 数据库: 绿色
```

---

## 创建数据中心和集群

### 创建数据中心

```yaml
数据中心概念:
  说明:
    数据中心是vCenter中的逻辑容器
    用于组织主机、集群、网络、存储
    一个vCenter可包含多个数据中心
  
  用途:
    ✅ 逻辑隔离 (如: 生产/测试)
    ✅ 地理位置分组 (如: 北京/上海)
    ✅ 部门隔离 (如: IT/财务)

创建步骤:
  1. 登录vCenter:
     https://192.168.1.10/ui
     用户: administrator@vsphere.local
  
  2. 导航到清单:
     菜单 → 主机和集群
  
  3. 创建数据中心:
     右键点击vCenter Server名称
     选择: "新建数据中心"
  
  4. 配置:
     数据中心名称: DC-Beijing
     或其他有意义的名称:
       - DC-Production
       - DC-Test
       - DC-Shanghai
  
  5. 完成:
     点击: "确定"
     数据中心出现在清单中

添加主机到数据中心:
  方式1: 直接添加
    1. 右键点击数据中心
    2. 选择: "添加主机"
    3. 输入主机信息:
       - 名称或IP地址: 192.168.1.101
       - 用户名: root
       - 密码: (ESXi密码)
    4. 证书警告: 点击 "是"
    5. 主机摘要: 查看主机信息
    6. 分配许可证: 选择vSphere许可证
    7. 锁定模式: 已禁用 (首次配置)
    8. VM位置: 选择数据中心
    9. 完成: 点击 "完成"
  
  方式2: 创建集群后添加 (推荐)
    先创建集群，然后将主机添加到集群
```

### 创建集群

```yaml
集群概念:
  说明:
    集群是一组ESXi主机的集合
    共享资源和策略
    提供高可用和负载均衡
  
  功能:
    ✅ vSphere HA: 高可用性
    ✅ vSphere DRS: 分布式资源调度
    ✅ vSphere vMotion: 在线迁移
    ✅ vSphere EVC: CPU兼容性
    ✅ vSAN: 软件定义存储 (可选)

创建集群:
  1. 导航到数据中心:
     主机和集群 → DC-Beijing
  
  2. 创建集群:
     右键点击数据中心
     选择: "新建集群"
  
  3. 集群名称:
     名称: Cluster-Production
     或其他名称:
       - Cluster-Web
       - Cluster-Database
       - Cluster-Test
  
  4. 功能配置:
     
     vSphere DRS (分布式资源调度):
       ☑ 启用vSphere DRS
       
       DRS自动化级别:
         - 手动: 仅提供建议
         - 部分自动化: 自动放置新VM
         - 全自动化: 自动负载均衡 (推荐)
       
       迁移阈值:
         保守 (1) <---> 激进 (5)
         推荐: 3 (中等)
       
       预测性DRS (仅vSphere 7.0+):
         ☑ 启用预测性DRS
         使用vRealize Operations预测负载
     
     vSphere HA (高可用性):
       ☑ 启用vSphere HA
       
       故障条件和VM响应:
         主机故障响应:
           - 重启VM (推荐)
           - 关闭VM电源
           - 已禁用
         
         主机隔离响应:
           - 关闭VM电源并重启 (推荐)
           - 关闭VM电源
           - 保持VM开机状态
         
         APD响应 (全路径不通):
           - 关闭VM电源并重启 (保守)
           - 禁用
         
         PDL响应 (永久设备丢失):
           - 关闭VM电源并重启 (激进)
       
       准入控制:
         ☑ 启用准入控制
         
         策略:
           - 集群资源百分比 (推荐)
             故障主机: 25%
             CPU: 25%
             内存: 25%
           
           - 插槽策略
             固定插槽大小
           
           - 专用故障切换主机
             指定主机作为备用
       
       心跳数据存储:
         ☑ 使用指定的数据存储
         选择: 所有共享数据存储
         目的: 网络隔离时检测主机状态
     
     vSAN:
       ☑ 启用vSAN (仅当有3+主机和适当硬件)
       
       要求:
         - 至少3台主机
         - 每台主机至少1个SSD (缓存)
         - 每台主机至少1个HDD/SSD (容量)
       
       服务:
         ☑ 重复数据删除和压缩 (需全闪存)
         ☑ 加密 (vSphere 6.6+)
     
     vSphere EVC (增强的vMotion兼容性):
       ☐ 禁用EVC (默认)
       ☑ 启用EVC (混合CPU代际时)
       
       EVC模式:
         Intel:
           - "Skylake" (Intel Xeon Gen 6+)
           - "Cascade Lake" (Intel Xeon Gen 2)
           - "Ice Lake" (Intel Xeon Gen 3)
         
         AMD:
           - "AMD EPYC Rome" (EPYC 7002)
           - "AMD EPYC Milan" (EPYC 7003)
       
       说明:
         限制CPU特性到最低公共集
         允许不同代际CPU主机间vMotion
  
  5. vSphere Lifecycle Manager:
     基线管理: 默认
     镜像管理: vSphere 7.0+ (可选)
  
  6. 完成创建:
     审核设置
     点击: "完成"
     集群创建完成

添加主机到集群:
  方式1: 拖拽
    将已有主机拖拽到集群
  
  方式2: 添加主机
    1. 右键点击集群
    2. 选择: "添加主机"
    3. 输入主机信息:
       - 名称或IP: 192.168.1.101
       - 用户名: root
       - 密码: (ESXi密码)
    4. 证书警告: 接受
    5. 主机摘要: 查看
    6. 分配许可证: 选择vSphere许可证
    7. 锁定模式: 已禁用
    8. 完成: 点击 "完成"
  
  添加多台主机:
    重复上述步骤
    推荐至少3台主机以实现HA

验证集群:
  1. 选择集群
  2. 选项卡: 监控
  3. 检查:
     vSphere HA: 绿色 (受保护)
     vSphere DRS: 绿色 (正常)
  4. 选项卡: 主机
  5. 确认所有主机已连接
```

### 配置资源池

```yaml
资源池概念:
  说明:
    资源池用于分配和管理计算资源
    可嵌套，形成资源层次结构
    支持预留、限制、份额
  
  用途:
    ✅ 部门资源隔离
    ✅ 应用优先级管理
    ✅ 资源超配控制
    ✅ 计费和核算

创建资源池:
  1. 导航到集群:
     主机和集群 → Cluster-Production
  
  2. 创建资源池:
     右键点击集群
     选择: "新建资源池"
  
  3. 配置:
     名称: Production-Pool
     
     CPU资源:
       预留:
         - 值: 8000 MHz (8GHz)
         - 说明: 保证的最小CPU
       
       限制:
         - ☐ 无限制 (推荐)
         - ☑ 限制为: 16000 MHz (特殊场景)
       
       份额:
         - 低: 低优先级
         - 正常: 默认优先级 (推荐)
         - 高: 高优先级
         - 自定义: 指定份额值
       
       可扩展预留:
         ☑ 启用 (推荐)
         说明: 允许借用父对象的未使用预留
     
     内存资源:
       预留:
         - 值: 32 GB
         - 说明: 保证的最小内存
       
       限制:
         - ☐ 无限制 (推荐)
         - ☑ 限制为: 64 GB (特殊场景)
       
       份额:
         - 低/正常/高/自定义
         - 推荐: 正常
       
       可扩展预留:
         ☑ 启用 (推荐)
  
  4. 完成:
     点击: "确定"
     资源池创建完成

使用资源池:
  创建VM时选择资源池:
    1. 新建虚拟机
    2. 选择计算资源
    3. 选择: Production-Pool
    4. 继续配置
  
  移动VM到资源池:
    1. 右键点击VM
    2. 选择: "移动到"
    3. 选择: 目标资源池
    4. 确定

资源池最佳实践:
  组织结构:
    Cluster-Production/
      ├── Production-Pool/
      │   ├── Web-Servers
      │   └── App-Servers
      └── Dev-Pool/
          └── Test-VMs
  
  预留配置:
    生产资源池: 较高预留
    开发资源池: 较低预留
    测试资源池: 无预留
  
  份额配置:
    关键业务: 高份额
    一般业务: 正常份额
    测试开发: 低份额
```

---

## 相关文档

- [操作系统与内核优化](01_操作系统与内核优化.md)
- [KVM安装与配置](03_KVM安装与配置.md)
- [Hyper-V安装与配置](04_Hyper-V安装与配置.md)
- [BIOS/固件配置清单](../01_硬件规范/06_BIOS固件配置清单.md)
- [硬件兼容性清单](../01_硬件规范/07_硬件兼容性清单.md)
- [存储架构配置](../03_存储架构/)
- [网络架构配置](../04_网络架构/)
- [高可用与容灾](../05_高可用容灾/)

---

**更新时间**: 2025-10-19  
**文档版本**: v3.0  
**状态**: ✅ 生产就绪
