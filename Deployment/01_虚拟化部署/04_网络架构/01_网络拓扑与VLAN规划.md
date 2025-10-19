# 网络拓扑与VLAN规划

> **返回**: [网络架构目录](README.md) | [虚拟化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [网络拓扑与VLAN规划](#网络拓扑与vlan规划)
  - [📋 目录](#-目录)
  - [网络架构概述](#网络架构概述)
  - [网络拓扑设计](#网络拓扑设计)
  - [VLAN规划](#vlan规划)
  - [IP地址规划](#ip地址规划)
  - [子网划分](#子网划分)
  - [路由设计](#路由设计)
  - [典型架构方案](#典型架构方案)
    - [小型企业方案 (\<50台服务器)](#小型企业方案-50台服务器)
    - [中型企业方案 (50-200台服务器)](#中型企业方案-50-200台服务器)
    - [大型企业/云服务商方案 (\>200台服务器)](#大型企业云服务商方案-200台服务器)
  - [网络设备选型](#网络设备选型)
  - [部署实施](#部署实施)
  - [最佳实践](#最佳实践)
  - [相关文档](#相关文档)

---

## 网络架构概述

```yaml
网络架构层次:
  物理层 (Layer 1):
    作用: 物理连接
    组件:
      - 网线 (Cat5e/Cat6/Cat6a/光纤)
      - 配线架
      - 光模块 (SFP/SFP+/QSFP)
      - 机柜布线
  
  数据链路层 (Layer 2):
    作用: 局域网交换
    组件:
      - 接入层交换机
      - 汇聚层交换机
      - VLAN
      - 链路聚合 (LACP)
    
    技术:
      ✅ MAC地址学习
      ✅ 生成树协议 (STP/RSTP/MSTP)
      ✅ VLAN隔离
      ✅ Trunk链路
  
  网络层 (Layer 3):
    作用: 路由转发
    组件:
      - 核心交换机 (L3)
      - 路由器
      - 防火墙
    
    技术:
      ✅ 静态路由
      ✅ 动态路由 (OSPF/BGP)
      ✅ VLAN间路由
      ✅ NAT
  
  应用层 (Layer 4-7):
    作用: 负载均衡、安全
    组件:
      - 负载均衡器
      - 应用防火墙 (WAF)
      - VPN网关
    
    技术:
      ✅ 负载均衡算法
      ✅ SSL卸载
      ✅ 应用层过滤

虚拟化网络组件:
  VMware vSphere:
    标准交换机 (vSS):
      特点: 单主机管理
      适用: 小型环境
    
    分布式交换机 (vDS):
      特点: 集中管理
      适用: 企业环境
      功能:
        ✅ 统一配置
        ✅ 流量监控 (NetFlow)
        ✅ 端口镜像
        ✅ LACP支持
        ✅ 流量整形
    
    NSX:
      类型: 网络虚拟化平台
      功能:
        ✅ 软件定义网络 (SDN)
        ✅ 微分段
        ✅ 分布式防火墙
        ✅ 负载均衡
        ✅ VPN
  
  Linux Bridge:
    特点: Linux原生虚拟交换机
    用途: KVM虚拟化
    命令: brctl, ip link
  
  Open vSwitch (OVS):
    特点: 高级虚拟交换机
    功能:
      ✅ OpenFlow支持
      ✅ VLAN
      ✅ QoS
      ✅ 流量镜像
      ✅ GRE/VXLAN隧道
    
    用途:
      - OpenStack
      - Kubernetes (Flannel/Calico后端)
      - 企业虚拟化

容器网络模型:
  CNI (Container Network Interface):
    标准: Kubernetes网络插件标准
    
    主流插件:
      Flannel:
        类型: 简单overlay网络
        后端: VXLAN/host-gw
        适用: 小规模集群
      
      Calico:
        类型: BGP网络
        特点:
          ✅ 高性能
          ✅ 网络策略
          ✅ 不需要overlay
        适用: 大规模生产环境
      
      Cilium:
        类型: eBPF网络
        特点:
          ✅ 极高性能
          ✅ 安全策略
          ✅ 7层可观测
        适用: 高性能场景
      
      Weave Net:
        类型: Mesh网络
        特点: 自动发现
        适用: 简单部署
```

---

## 网络拓扑设计

```yaml
经典三层架构:
  接入层 (Access Layer):
    作用: 连接终端设备
    设备:
      - 接入交换机 (24/48口)
      - ToR交换机 (Top of Rack)
    
    特点:
      ✅ 端口密度高
      ✅ PoE供电 (可选)
      ✅ L2功能
      ✅ 基础QoS
    
    配置:
      端口模式: Access
      VLAN: 单VLAN
      STP: PortFast
      安全: Port Security
  
  汇聚层 (Distribution Layer):
    作用: 流量汇聚、路由
    设备:
      - 汇聚交换机 (L3)
      - 中等端口密度
    
    特点:
      ✅ L2/L3交换
      ✅ VLAN间路由
      ✅ 策略路由
      ✅ QoS
      ✅ 冗余设计
    
    配置:
      端口模式: Trunk
      路由: OSPF/静态
      冗余: HSRP/VRRP
      链路聚合: LACP
  
  核心层 (Core Layer):
    作用: 高速转发
    设备:
      - 核心交换机 (高性能L3)
      - 路由器
    
    特点:
      ✅ 超高带宽
      ✅ 低延迟
      ✅ 高可用
      ✅ 模块化
    
    配置:
      路由协议: OSPF/BGP
      冗余: 双核心
      链路: 40G/100G
      优先级: 最高

Spine-Leaf架构 (现代数据中心):
  Spine层 (脊柱):
    作用: 核心交换
    特点:
      ✅ 所有Leaf互联
      ✅ 无阻塞
      ✅ 东西流量优化
    
    设备: 高性能L3交换机
    数量: 2-4台
    带宽: 100G/400G
  
  Leaf层 (叶子):
    作用: 接入服务器
    特点:
      ✅ 连接所有Spine
      ✅ L3到服务器
      ✅ VTEP (VXLAN)
    
    设备: ToR交换机
    数量: 根据机柜数
    带宽: 25G/100G上行
  
  优势:
    ✅ 可预测的延迟
    ✅ 易于扩展
    ✅ 高带宽
    ✅ 无阻塞
    ✅ 容错性强
  
  适用: 云计算、大规模虚拟化

虚拟化网络拓扑:
  VMware标准架构:
    管理网络:
      vSwitch: vSwitch0
      用途: ESXi管理、vCenter
      VLAN: VLAN 10
      上行链路: 2x 1GbE (主备)
    
    vMotion网络:
      vSwitch: vSwitch1
      用途: 虚拟机迁移
      VLAN: VLAN 20
      上行链路: 2x 10GbE (LACP)
    
    存储网络:
      vSwitch: vSwitch2
      用途: iSCSI/NFS
      VLAN: VLAN 30/31 (多路径)
      上行链路: 2x 10GbE (独立)
    
    虚拟机网络:
      vSwitch: vDS (分布式交换机)
      用途: VM业务流量
      VLAN: VLAN 40-49 (多个)
      上行链路: 4x 10GbE (LACP)
  
  KVM标准架构:
    管理网络:
      接口: eth0
      Bridge: br-mgmt
      用途: 宿主机管理
    
    虚拟机网络:
      接口: eth1-eth2
      Bridge: br-vm
      VLAN: 通过OVS/Linux VLAN
      绑定: bond0 (LACP)
    
    存储网络:
      接口: eth3-eth4
      Bridge: 无 (直连iSCSI)
      VLAN: 专用

容器网络拓扑:
  Kubernetes网络平面:
    主机网络 (Host Network):
      用途: 节点间通信
      实现: 物理网络
    
    Pod网络 (Pod Network):
      用途: Pod间通信
      实现: CNI插件
      CIDR: 10.244.0.0/16 (示例)
    
    Service网络 (Service Network):
      用途: 服务发现与负载均衡
      实现: kube-proxy
      CIDR: 10.96.0.0/12 (示例)
    
    Ingress网络:
      用途: 外部访问
      实现: Ingress Controller
```

**网络拓扑图示例**:

```text
三层架构:

┌─────────────────────────────────────────────────┐
│                   核心层                         │
│  ┌──────────┐              ┌──────────┐         │
│  │ Core-SW1 │◄────────────►│ Core-SW2 │         │
│  └────┬─────┘              └─────┬────┘         │
└───────┼───────────────────────────┼──────────────┘
        │                           │
        │         汇聚层             │
┌───────┼───────────────────────────┼──────────────┐
│   ┌───▼────┐              ┌───────▼───┐          │
│   │ Dist-SW1│◄────────────►│ Dist-SW2 │          │
│   └───┬────┘              └───────┬───┘          │
└───────┼───────────────────────────┼──────────────┘
        │                           │
        │         接入层             │
┌───────┼───────────────────────────┼──────────────┐
│   ┌───▼────┐  ┌────────┐  ┌───────▼───┐          │
│   │Access-1│  │Access-2│  │ Access-3  │          │
│   └───┬────┘  └────┬───┘  └───────┬───┘          │
└───────┼────────────┼──────────────┼──────────────┘
        │            │              │
    ┌───▼──┐    ┌───▼──┐      ┌────▼──┐
    │Server│    │Server│      │Server │
    └──────┘    └──────┘      └───────┘

Spine-Leaf架构:

┌─────────────────────────────────────────────────┐
│                   Spine层                        │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │Spine1│  │Spine2│  │Spine3│  │Spine4│         │
│  └───┬──┘  └───┬──┘  └───┬──┘  └───┬──┘         │
└──────┼─────────┼─────────┼─────────┼────────────┘
    ╱  │  ╲   ╱  │  ╲   ╱  │  ╲   ╱  │  ╲
   ╱   │   ╲ ╱   │   ╲ ╱   │   ╲ ╱   │   ╲
┌─────────────────────────────────────────────────┐
│                   Leaf层                         │
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐       │
│ │Leaf│ │Leaf│ │Leaf│ │Leaf│ │Leaf│ │Leaf│       │
│ │ 1  │ │ 2  │ │ 3  │ │ 4  │ │ 5  │ │ 6  │       │
│ └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘       │
└───┼──────┼──────┼──────┼──────┼──────┼──────────┘
    │      │      │      │      │      │
  ┌─▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐
  │Rack│ │Rack│ │Rack│ │Rack│ │Rack│ │Rack│
  │ 1  │ │ 2  │ │ 3  │ │ 4  │ │ 5  │ │ 6  │
  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘
```

---

## VLAN规划

```yaml
VLAN基础概念:
  定义: Virtual Local Area Network (虚拟局域网)
  作用:
    ✅ 逻辑隔离
    ✅ 安全分段
    ✅ 广播域控制
    ✅ 简化管理
  
  范围:
    VLAN 1: 默认VLAN (不推荐使用)
    VLAN 2-1001: 标准VLAN
    VLAN 1002-1005: 保留 (令牌环、FDDI)
    VLAN 1006-4094: 扩展VLAN

企业VLAN规划标准:
  管理VLAN (10-19):
    VLAN 10: 网络设备管理
      - 交换机管理IP
      - 路由器管理IP
      - 防火墙管理IP
    
    VLAN 11: 虚拟化管理
      - ESXi/KVM宿主机管理
      - vCenter Server
      - 管理工作站
    
    VLAN 12: 存储管理
      - 存储设备管理接口
      - 存储阵列管理
    
    VLAN 15: 带外管理 (IPMI/iLO/iDRAC)
      - 服务器BMC接口
      - 远程控制台
  
  基础设施VLAN (20-39):
    VLAN 20: vMotion/迁移网络
      - VMware vMotion
      - Hyper-V Live Migration
      - KVM迁移
    
    VLAN 21: 容错网络
      - VMware Fault Tolerance
    
    VLAN 30: iSCSI存储 (路径A)
      - iSCSI流量
      - 隔离存储网络
    
    VLAN 31: iSCSI存储 (路径B)
      - 多路径冗余
    
    VLAN 35: NFS存储
      - NFS数据存储
    
    VLAN 36: 备份网络
      - 备份流量隔离
      - 避免影响生产
  
  生产业务VLAN (40-99):
    VLAN 40: Web前端
      - Web服务器
      - 负载均衡器
    
    VLAN 41: 应用层
      - 应用服务器
      - 中间件
    
    VLAN 42: 数据库
      - 数据库服务器
      - 缓存服务器
    
    VLAN 45: 容器Pod网络
      - Kubernetes Pod
      - Docker容器
    
    VLAN 50: 开发环境
      - 开发服务器
      - 测试环境
    
    VLAN 60: UAT环境
      - 用户验收测试
    
    VLAN 70: 生产环境
      - 生产业务系统
  
  用户接入VLAN (100-199):
    VLAN 100: 办公网络
      - 员工PC
      - 打印机
    
    VLAN 110: 会议室
      - 会议室设备
      - 访客Wi-Fi
    
    VLAN 120: 研发网络
      - 研发人员
      - 开发工具
  
  专用VLAN (200-299):
    VLAN 200: DMZ外网区
      - 对外服务
      - 公网接口
    
    VLAN 210: 监控网络
      - 监控系统
      - 摄像头
    
    VLAN 220: 语音网络
      - IP电话
      - 视频会议
  
  预留VLAN (900-999):
    VLAN 999: 隔离VLAN
      - 未使用端口
      - 黑洞VLAN

VLAN配置示例:
```

```cisco
! Cisco交换机VLAN配置

! 1. 创建VLAN
vlan 10
 name MGMT-Network
vlan 11
 name VMware-Management
vlan 20
 name vMotion-Network
vlan 30
 name iSCSI-Storage-A
vlan 31
 name iSCSI-Storage-B
vlan 40
 name Web-Tier
vlan 41
 name App-Tier
vlan 42
 name Database-Tier
vlan 100
 name Office-Network

! 2. 配置Access端口 (连接服务器)
interface GigabitEthernet1/0/1
 description ESXi-Host-1-MGMT
 switchport mode access
 switchport access vlan 11
 spanning-tree portfast
 spanning-tree bpduguard enable

! 3. 配置Trunk端口 (上行链路)
interface GigabitEthernet1/0/48
 description Uplink-to-Core
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,11,20,30,31,40-42,100
 switchport trunk native vlan 999
 channel-group 1 mode active

! 4. 配置VLAN接口 (L3交换机)
interface Vlan10
 description MGMT-Network-Gateway
 ip address 192.168.10.1 255.255.255.0
 no shutdown

interface Vlan11
 description VMware-MGMT-Gateway
 ip address 192.168.11.1 255.255.255.0
 ip helper-address 192.168.10.10
 no shutdown
```

```yaml
VLAN最佳实践:
  设计原则:
    ✅ 按功能划分: 管理/存储/业务分离
    ✅ 按安全级别: 生产/开发/测试隔离
    ✅ 按性能要求: 高流量单独VLAN
    ✅ 预留扩展空间: 保留未来增长
  
  命名规范:
    格式: VLAN<ID>-<用途>-<位置>
    示例:
      - VLAN10-MGMT-DC1
      - VLAN40-WEB-PROD
      - VLAN100-OFFICE-BJ
  
  文档管理:
    必须记录:
      - VLAN ID
      - VLAN名称
      - 用途描述
      - IP子网
      - 网关地址
      - DHCP服务器
      - 使用设备列表
  
  安全考虑:
    ✅ 不使用VLAN 1
    ✅ Native VLAN设置为未使用ID
    ✅ 关闭DTP (Dynamic Trunking Protocol)
    ✅ 未使用端口分配到隔离VLAN
    ✅ 启用Private VLAN (如需要)
```

---

## IP地址规划

```yaml
IPv4地址规划:
  RFC1918私有地址段:
    10.0.0.0/8:
      范围: 10.0.0.0 - 10.255.255.255
      主机数: 16,777,216
      适用: 大型企业、运营商
    
    172.16.0.0/12:
      范围: 172.16.0.0 - 172.31.255.255
      主机数: 1,048,576
      适用: 中型企业
    
    192.168.0.0/16:
      范围: 192.168.0.0 - 192.168.255.255
      主机数: 65,536
      适用: 小型企业、家庭

企业IP地址分配:
  数据中心 (10.0.0.0/8):
    管理网段 (10.10.0.0/16):
      10.10.10.0/24: 网络设备管理
      10.10.11.0/24: VMware管理
      10.10.15.0/24: IPMI带外管理
    
    基础设施网段 (10.20.0.0/16):
      10.20.20.0/24: vMotion网络
      10.20.30.0/24: iSCSI存储A
      10.20.31.0/24: iSCSI存储B
      10.20.35.0/24: NFS存储
      10.20.36.0/24: 备份网络
    
    生产业务网段 (10.100.0.0/16):
      10.100.40.0/24: Web层
      10.100.41.0/24: 应用层
      10.100.42.0/24: 数据库层
    
    容器网段 (10.244.0.0/16):
      10.244.0.0/16: Kubernetes Pod CIDR
      10.96.0.0/12: Kubernetes Service CIDR
    
    开发测试 (10.150.0.0/16):
      10.150.50.0/24: 开发环境
      10.150.60.0/24: UAT环境
  
  办公网络 (192.168.0.0/16):
    192.168.100.0/24: 办公区域A
    192.168.101.0/24: 办公区域B
    192.168.110.0/24: 会议室
    192.168.120.0/24: 研发网络
  
  DMZ区域 (172.16.0.0/16):
    172.16.200.0/24: 公网服务器

子网规划示例:
```

| 网段 | CIDR | 可用主机数 | 网关 | DHCP范围 | 用途 |
|------|------|-----------|------|---------|------|
| 10.10.10.0/24 | /24 | 254 | 10.10.10.1 | 10.10.10.100-200 | 网络设备管理 |
| 10.10.11.0/24 | /24 | 254 | 10.10.11.1 | 静态分配 | VMware管理 |
| 10.20.20.0/24 | /24 | 254 | 无 | 静态分配 | vMotion (L2) |
| 10.20.30.0/24 | /24 | 254 | 无 | 静态分配 | iSCSI存储A |
| 10.20.31.0/24 | /24 | 254 | 无 | 静态分配 | iSCSI存储B |
| 10.100.40.0/24 | /24 | 254 | 10.100.40.1 | 10.100.40.100-200 | Web层 |
| 10.100.41.0/22 | /22 | 1022 | 10.100.41.1 | 10.100.42.1-10.100.43.254 | 应用层 (大量主机) |
| 10.100.42.0/25 | /25 | 126 | 10.100.42.1 | 静态分配 | 数据库层 |
| 192.168.100.0/23 | /23 | 510 | 192.168.100.1 | 192.168.100.100-192.168.101.254 | 办公网络 |

```yaml
IP地址分配策略:
  静态分配:
    设备类型:
      - 网络设备 (交换机、路由器)
      - 服务器 (物理/虚拟)
      - 存储设备
      - 负载均衡器
      - 数据库服务器
    
    分配范围:
      网关: .1
      网络设备: .2-.9
      服务器: .10-.99
      预留: .250-.254
  
  DHCP动态分配:
    设备类型:
      - 办公PC
      - 打印机
      - 临时设备
    
    分配范围:
      一般: .100-.200
      大范围: .100-.250

IPv6规划 (可选):
  地址段: fd00::/8 (Unique Local Address)
  
  示例:
    管理网络: fd00:10:11::/64
    Pod网络: fd00:244::/48
    Service网络: fd00:96::/108
  
  优势:
    ✅ 海量地址空间
    ✅ 无需NAT
    ✅ 简化路由
    ✅ 更好的安全性
```

---

## 子网划分

```yaml
子网掩码计算:
  CIDR记法:
    /24: 255.255.255.0 (254主机)
    /23: 255.255.254.0 (510主机)
    /22: 255.255.252.0 (1022主机)
    /25: 255.255.255.128 (126主机)
    /26: 255.255.255.192 (62主机)
    /27: 255.255.255.224 (30主机)
    /28: 255.255.255.240 (14主机)
    /29: 255.255.255.248 (6主机)
    /30: 255.255.255.252 (2主机, 点对点)

VLSM (可变长子网掩码):
  原则: 根据实际需求分配合适大小的子网
  
  示例: 从10.100.0.0/16分配
    Web层 (100台主机):
      需求: /25 (126主机)
      分配: 10.100.40.0/25
    
    应用层 (500台主机):
      需求: /22 (1022主机)
      分配: 10.100.44.0/22
    
    数据库 (30台主机):
      需求: /26 (62主机)
      分配: 10.100.48.0/26
    
    点对点链路 (2台主机):
      需求: /30 (2主机)
      分配: 10.100.48.64/30

子网汇总 (Route Summarization):
  目的: 减少路由表条目
  
  示例:
    原始路由:
      10.100.40.0/24
      10.100.41.0/24
      10.100.42.0/24
      10.100.43.0/24
    
    汇总后:
      10.100.40.0/22 (包含上述4个/24网段)
  
  计算方法:
    1. 找到共同前缀
    2. 确定汇总掩码长度
    3. 验证是否覆盖所有子网

子网划分工具:
  命令行工具:
    ipcalc:
      安装: apt install ipcalc
      使用: ipcalc 10.100.40.0/24
    
    sipcalc:
      功能: 更强大的IP计算器
      使用: sipcalc 10.100.0.0/16 -s 24
  
  在线工具:
    - ip-calculator.net
    - subnet-calculator.com
    - calculator.net/ip-subnet-calculator.html
```

---

## 路由设计

```yaml
静态路由:
  适用场景:
    - 小型网络
    - 简单拓扑
    - 明确路径
  
  配置示例 (Cisco):
```

```cisco
! 默认路由
ip route 0.0.0.0 0.0.0.0 192.168.1.1

! 到特定网段的路由
ip route 10.100.0.0 255.255.0.0 10.10.10.2

! 备份路由 (管理距离120)
ip route 10.100.0.0 255.255.0.0 10.10.10.3 120
```

```yaml
动态路由协议:
  OSPF (Open Shortest Path First):
    类型: 链路状态协议
    特点:
      ✅ 快速收敛
      ✅ 无环路
      ✅ 支持VLSM
      ✅ 区域划分
    
    适用: 企业内部网络
    
    配置示例 (Cisco):
```

```cisco
! 启用OSPF
router ospf 1
 router-id 10.10.10.1
 network 10.10.10.0 0.0.0.255 area 0
 network 10.100.0.0 0.0.255.255 area 1
 passive-interface default
 no passive-interface GigabitEthernet1/0/48

! 区域划分
! Area 0: 骨干区域 (管理网络)
! Area 1: 普通区域 (业务网络)
! Area 2: 普通区域 (办公网络)
```

```yaml
  BGP (Border Gateway Protocol):
    类型: 路径向量协议
    特点:
      ✅ 策略路由
      ✅ 大规模网络
      ✅ AS间路由
    
    适用: 数据中心互联、多出口
    
    配置示例 (Cisco):
```

```cisco
! BGP配置
router bgp 65001
 bgp router-id 10.10.10.1
 neighbor 10.10.10.2 remote-as 65001
 neighbor 203.0.113.1 remote-as 65002
 !
 address-family ipv4
  network 10.100.0.0 mask 255.255.0.0
  neighbor 10.10.10.2 activate
  neighbor 203.0.113.1 activate
 exit-address-family
```

```yaml
VLAN间路由:
  方法1: 单臂路由 (Router-on-a-Stick)
    特点:
      - 路由器单接口
      - 子接口对应VLAN
      - 性能瓶颈
    
    适用: 小型网络
    
    配置 (Cisco路由器):
```

```cisco
interface GigabitEthernet0/0
 no shutdown

interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.10.10.1 255.255.255.0

interface GigabitEthernet0/0.40
 encapsulation dot1Q 40
 ip address 10.100.40.1 255.255.255.0
```

```yaml
  方法2: L3交换机 (SVI)
    特点:
      - 硬件转发
      - 高性能
      - 主流方案
    
    配置 (Cisco L3交换机):
```

```cisco
! 启用IP路由
ip routing

! 创建SVI
interface Vlan10
 ip address 10.10.10.1 255.255.255.0
 no shutdown

interface Vlan40
 ip address 10.100.40.1 255.255.255.0
 no shutdown

! 端口配置
interface GigabitEthernet1/0/1
 switchport access vlan 10

interface GigabitEthernet1/0/2
 switchport access vlan 40
```

```yaml
高可用路由:
  HSRP (Hot Standby Router Protocol):
    厂商: Cisco私有
    虚拟IP: 共享
    优先级: 可配置
    
    配置:
```

```cisco
! 主路由器
interface Vlan10
 ip address 10.10.10.2 255.255.255.0
 standby 1 ip 10.10.10.1
 standby 1 priority 110
 standby 1 preempt

! 备份路由器
interface Vlan10
 ip address 10.10.10.3 255.255.255.0
 standby 1 ip 10.10.10.1
 standby 1 priority 100
```

```yaml
  VRRP (Virtual Router Redundancy Protocol):
    厂商: 标准协议
    虚拟IP: 共享
    
    配置 (Linux):
```

```bash
# 安装keepalived
apt install keepalived

# /etc/keepalived/keepalived.conf
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1234
    }
    virtual_ipaddress {
        10.10.10.1/24
    }
}
```

---

## 典型架构方案

### 小型企业方案 (<50台服务器)

```yaml
拓扑: 简化两层架构
设备清单:
  核心交换机: 2台L3交换机 (48口)
  接入交换机: 3-5台L2交换机 (24口)
  防火墙: 1台 (可选)

VLAN规划:
  VLAN 10: 管理网络
  VLAN 20: 服务器网络
  VLAN 100: 办公网络

IP规划:
  192.168.10.0/24: 管理
  192.168.20.0/24: 服务器
  192.168.100.0/24: 办公

带宽:
  核心上行: 10GbE
  接入上行: 1GbE聚合
  服务器: 1GbE双网卡

成本: ¥50,000-100,000
```

### 中型企业方案 (50-200台服务器)

```yaml
拓扑: 标准三层架构
设备清单:
  核心交换机: 2台模块化L3交换机
  汇聚交换机: 4台L3交换机
  接入交换机: 10-20台L2/L3交换机
  防火墙: 2台 (主备)
  负载均衡器: 2台

VLAN规划:
  管理VLAN: 10-19
  基础设施VLAN: 20-39
  业务VLAN: 40-99
  办公VLAN: 100-199

IP规划:
  10.10.0.0/16: 数据中心
  192.168.0.0/16: 办公网络
  172.16.0.0/24: DMZ

带宽:
  核心: 40G/100G
  汇聚: 10G/25G
  接入: 10G上行
  服务器: 10G双网卡

成本: ¥500,000-1,000,000
```

### 大型企业/云服务商方案 (>200台服务器)

```yaml
拓扑: Spine-Leaf架构
设备清单:
  Spine交换机: 4-8台 (100G/400G)
  Leaf交换机: 20-100台 (25G/100G)
  防火墙集群: 4-8台
  负载均衡器集群: 4-8台

VLAN规划:
  使用VXLAN overlay网络
  L3到服务器
  EVPN控制平面

IP规划:
  Underlay: 10.0.0.0/8 (物理网络)
  Overlay: 172.16.0.0/12 (租户网络)
  管理: 192.168.0.0/16

带宽:
  Spine: 400G
  Leaf: 100G上行, 25G下行
  服务器: 25G双网卡

SDN:
  VMware NSX / Cisco ACI / OpenStack Neutron

成本: ¥5,000,000+
```

---

## 网络设备选型

```yaml
交换机选型:
  接入层:
    Cisco Catalyst 9200:
      端口: 24/48口
      上行: 4x 10G SFP+
      功能: L2/L3, PoE+
      价格: ¥15,000-30,000
    
    HPE Aruba 6200F:
      端口: 24/48口
      上行: 4x 10G SFP+
      功能: L2/L3, PoE
      价格: ¥12,000-25,000
    
    华为S5735:
      端口: 24/48口
      上行: 4x 10G SFP+
      国产化: 支持
      价格: ¥10,000-20,000
  
  汇聚层:
    Cisco Catalyst 9300/9400:
      端口: 24-48口 10G
      上行: 40G/100G
      功能: 全L3, 冗余电源
      价格: ¥80,000-200,000
    
    HPE Aruba 8360:
      端口: 48口 10G/25G
      上行: 100G
      VSF: 支持
      价格: ¥100,000-150,000
  
  核心层:
    Cisco Nexus 9000:
      端口: 32-64口 100G
      架构: Spine-Leaf ready
      SDN: ACI支持
      价格: ¥500,000-2,000,000
    
    Arista 7050X3:
      端口: 32口 100G
      延迟: Ultra-low (<1μs)
      用途: 金融交易
      价格: ¥800,000+
    
    Mellanox Spectrum:
      端口: 32口 100G
      RDMA: 支持
      用途: HPC, AI
      价格: ¥600,000+

路由器选型:
  边界路由器:
    Cisco ASR 1000:
      吞吐: 5-100 Gbps
      功能: 企业边界
      价格: ¥200,000-1,000,000
    
    Juniper MX系列:
      吞吐: 10-400 Gbps
      用途: 运营商级
      价格: ¥500,000+
```

---

## 部署实施

```bash
#!/bin/bash
# 网络配置自动化脚本

set -e

LOG_FILE="/var/log/network_deploy_$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "  网络配置部署脚本"
log "========================================="

# 1. 配置网络接口
log "--- 配置网络接口 ---"

# 管理接口
cat > /etc/netplan/01-mgmt.yaml <<EOF
network:
  version: 2
  ethernets:
    ens192:
      addresses:
        - 10.10.11.10/24
      gateway4: 10.10.11.1
      nameservers:
        addresses:
          - 10.10.10.10
          - 8.8.8.8
EOF

# 存储接口 (iSCSI)
cat > /etc/netplan/02-iscsi.yaml <<EOF
network:
  version: 2
  ethernets:
    ens224:
      addresses:
        - 10.20.30.10/24
      mtu: 9000
    ens256:
      addresses:
        - 10.20.31.10/24
      mtu: 9000
EOF

# 应用配置
netplan apply

log "网络接口配置完成"

# 2. 配置VLAN接口 (如果需要)
if [ -n "$CONFIGURE_VLAN" ]; then
    log "--- 配置VLAN接口 ---"
    
    cat > /etc/netplan/03-vlan.yaml <<EOF
network:
  version: 2
  vlans:
    vlan40:
      id: 40
      link: ens160
      addresses:
        - 10.100.40.10/24
    vlan41:
      id: 41
      link: ens160
      addresses:
        - 10.100.41.10/24
EOF
    
    netplan apply
    log "VLAN接口配置完成"
fi

# 3. 配置网桥 (用于KVM)
if [ -n "$CONFIGURE_BRIDGE" ]; then
    log "--- 配置网桥 ---"
    
    cat > /etc/netplan/04-bridge.yaml <<EOF
network:
  version: 2
  bridges:
    br0:
      interfaces:
        - ens160
      addresses:
        - 10.100.40.10/24
      gateway4: 10.100.40.1
      parameters:
        stp: true
        forward-delay: 4
EOF
    
    netplan apply
    log "网桥配置完成"
fi

# 4. 配置路由
log "--- 配置静态路由 ---"

# 添加静态路由
ip route add 172.16.0.0/16 via 10.10.11.254

# 永久化路由
cat >> /etc/netplan/01-mgmt.yaml <<EOF
      routes:
        - to: 172.16.0.0/16
          via: 10.10.11.254
EOF

netplan apply

log "路由配置完成"

# 5. 网络性能优化
log "--- 网络性能优化 ---"

cat >> /etc/sysctl.conf <<EOF

# 网络性能优化
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq
net.ipv4.tcp_mtu_probing = 1

# 连接数优化
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.core.somaxconn = 32768
EOF

sysctl -p

log "性能优化完成"

# 6. 验证网络配置
log "--- 验证网络配置 ---"

log "接口状态:"
ip addr show | tee -a "$LOG_FILE"

log "路由表:"
ip route show | tee -a "$LOG_FILE"

log "连通性测试:"
ping -c 3 10.10.11.1 && log "✓ 网关可达" || log "✗ 网关不可达"
ping -c 3 8.8.8.8 && log "✓ 外网可达" || log "✗ 外网不可达"

log "========================================="
log "  网络配置部署完成"
log "========================================="
log "日志文件: $LOG_FILE"
```

---

## 最佳实践

```yaml
网络设计原则:
  1. 冗余设计:
     ✅ 核心/汇聚双设备
     ✅ 双上行链路
     ✅ LACP链路聚合
     ✅ HSRP/VRRP网关冗余
  
  2. 性能优化:
     ✅ Jumbo Frame (MTU 9000)
     ✅ QoS策略
     ✅ 合理的VLAN划分
     ✅ 避免广播风暴
  
  3. 安全加固:
     ✅ 网络分段隔离
     ✅ ACL访问控制
     ✅ 端口安全
     ✅ DHCP Snooping
     ✅ ARP检查
  
  4. 可扩展性:
     ✅ 预留VLAN
     ✅ 预留IP段
     ✅ 模块化设计
     ✅ Spine-Leaf架构
  
  5. 可管理性:
     ✅ 一致的命名规范
     ✅ 完整的文档
     ✅ SNMP监控
     ✅ 日志集中收集

常见错误:
  ❌ VLAN 1用于生产
  ❌ 单点故障
  ❌ 未文档化配置
  ❌ 过度复杂设计
  ❌ 忽略安全
  ❌ 未预留扩展
  ❌ 广播域过大
  ❌ 未测试故障切换

配置检查清单:
  部署前:
    □ 网络拓扑图完成
    □ VLAN规划文档
    □ IP地址分配表
    □ 设备清单与配置
    □ 布线方案
    □ 测试计划
  
  部署中:
    □ 物理连接正确
    □ VLAN配置正确
    □ IP地址配置正确
    □ 路由配置正确
    □ 冗余机制工作
    □ 性能达标
  
  部署后:
    □ 连通性测试
    □ 故障切换测试
    □ 性能测试
    □ 安全审计
    □ 文档更新
    □ 培训交接
```

---

## 相关文档

- [交换机配置与优化](02_交换机配置与优化.md)
- [负载均衡与高可用](03_负载均衡与高可用.md)
- [网络安全策略](04_网络安全策略.md)
- [网络监控与故障排查](05_网络监控与故障排查.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v3.0  
**状态**: ✅ 生产就绪
