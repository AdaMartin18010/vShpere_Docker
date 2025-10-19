# Calico网络配置

> **返回**: [容器网络目录](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Calico网络配置](#calico网络配置)
  - [📋 目录](#-目录)
  - [1. Calico架构](#1-calico架构)
  - [2. Calico安装部署](#2-calico安装部署)
    - [使用Operator安装 (推荐)](#使用operator安装-推荐)
    - [使用Manifest安装](#使用manifest安装)
    - [安装calicoctl工具](#安装calicoctl工具)
  - [3. 网络模式配置](#3-网络模式配置)
  - [4. IP地址管理 (IPAM)](#4-ip地址管理-ipam)
  - [5. BGP配置](#5-bgp配置)
  - [6. NetworkPolicy](#6-networkpolicy)
  - [7. 运维管理](#7-运维管理)
  - [8. 故障排查](#8-故障排查)
  - [9. 性能优化](#9-性能优化)
  - [10. 最佳实践](#10-最佳实践)
  - [相关文档](#相关文档)

---

## 1. Calico架构

```yaml
Calico_Architecture:
  核心组件:
    Felix:
      作用: 节点代理
      功能:
        - 配置路由和ACL
        - 报告状态
        - 编程内核路由表
        - 配置iptables规则
      部署: 每节点一个DaemonSet Pod
    
    BIRD:
      作用: BGP客户端
      功能:
        - 分发路由信息
        - 与其他节点交换路由
        - 与物理路由器对等
      部署: 与Felix在同一Pod
    
    Typha:
      作用: 缓存和扇出代理
      功能:
        - 减轻etcd/Kubernetes API压力
        - 聚合数据变更
        - 扇出到Felix
      部署: 大规模集群（>50节点）必需
    
    Kube-controllers:
      作用: Kubernetes控制器
      功能:
        - 监听Kubernetes事件
        - 转换为Calico资源
        - 垃圾回收
      部署: 单个Deployment
    
    CNI插件:
      作用: 容器网络接口
      功能:
        - Pod网络配置
        - IP分配
        - 路由设置
      部署: 节点二进制文件
  
  数据存储:
    - Kubernetes API (推荐)
    - etcd v3 (独立部署)
  
  网络模型:
    - 纯三层网络
    - BGP路由协议
    - 无Overlay封装 (BGP模式)
    - 可选IPIP/VXLAN封装
```

**Calico架构图**:

```text
┌─────────────────────────────────────────┐
│           Kubernetes API Server          │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│ Kube-        │  │   Typha     │
│ controllers  │  │ (可选)       │
└──────────────┘  └──────┬──────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼──────────┐ ┌───▼────────────┐
│ Node 1         │ │ Node 2        │ │ Node 3         │
│ ┌────────────┐ │ │ ┌───────────┐ │ │ ┌────────────┐ │
│ │Felix + BIRD│ │ │ │Felix+BIRD │ │ │ │Felix + BIRD│ │
│ └────────────┘ │ │ └───────────┘ │ │ └────────────┘ │
│ ┌────────────┐ │ │ ┌───────────┐ │ │ ┌────────────┐ │
│ │  Pods      │ │ │ │  Pods     │ │ │ │  Pods      │ │
│ └────────────┘ │ │ └───────────┘ │ │ └────────────┘ │
└────────────────┘ └───────────────┘ └────────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                    BGP Routing
```

---

## 2. Calico安装部署

### 使用Operator安装 (推荐)

```bash
# ========================================
# 1. 安装Tigera Operator
# ========================================

kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/tigera-operator.yaml

# 查看Operator状态
kubectl get pods -n tigera-operator

# ========================================
# 2. 安装Calico
# ========================================

# 创建Installation资源
cat <<EOF | kubectl apply -f -
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  # Calico版本
  variant: Calico
  
  # 网络配置
  calicoNetwork:
    # IP池配置
    ipPools:
    - name: default-ipv4-ippool
      blockSize: 26
      cidr: 10.244.0.0/16
      encapsulation: IPIP
      natOutgoing: Enabled
      nodeSelector: all()
    
    # IPv6配置 (可选)
    # - name: default-ipv6-ippool
    #   blockSize: 122
    #   cidr: fd00:10:244::/48
    #   encapsulation: None
    #   natOutgoing: Enabled
    
    # BGP配置
    bgp: Enabled
    
    # MTU
    mtu: 1440
    
    # 节点地址自动检测
    nodeAddressAutodetectionV4:
      interface: "eth0"
EOF

# 查看Installation状态
kubectl get installation default -o yaml

# ========================================
# 3. 验证安装
# ========================================

# 查看Calico Pods
kubectl get pods -n calico-system

# 查看节点状态
calicoctl node status

# 查看IP池
calicoctl get ippool -o wide
```

### 使用Manifest安装

```bash
# ========================================
# 直接安装Calico
# ========================================

# 下载manifest
curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/calico.yaml -O

# 修改Pod CIDR (如需要)
sed -i 's/192.168.0.0\/16/10.244.0.0\/16/g' calico.yaml

# 应用
kubectl apply -f calico.yaml

# 验证
kubectl get pods -n kube-system -l k8s-app=calico-node
kubectl get pods -n kube-system -l k8s-app=calico-kube-controllers
```

### 安装calicoctl工具

```bash
# ========================================
# 安装calicoctl CLI
# ========================================

# 下载二进制
curl -L https://github.com/projectcalico/calico/releases/download/v3.26.1/calicoctl-linux-amd64 -o calicoctl
chmod +x calicoctl
sudo mv calicoctl /usr/local/bin/

# 配置calicoctl
mkdir -p /etc/calico
cat <<EOF > /etc/calico/calicoctl.cfg
apiVersion: projectcalico.org/v3
kind: CalicoAPIConfig
metadata:
spec:
  datastoreType: "kubernetes"
  kubeconfig: "/root/.kube/config"
EOF

# 验证
calicoctl version
calicoctl get nodes
```

---

## 3. 网络模式配置

```yaml
Calico_Network_Modes:
  BGP模式 (推荐):
    特点:
      - 无封装
      - 高性能
      - 原生路由
      - 需要网络支持
    
    配置:
      encapsulation: None
      bgp: Enabled
    
    适用场景:
      - 私有云/IDC
      - 底层网络可控
      - 性能要求高
  
  IPIP模式:
    特点:
      - IP-in-IP封装
      - 跨子网通信
      - 无需网络配置
      - 有性能开销
    
    配置:
      encapsulation: IPIP
      ipipMode: Always | CrossSubnet
    
    适用场景:
      - 公有云环境
      - 网络不互通
      - 快速部署
  
  VXLAN模式:
    特点:
      - VXLAN封装
      - 不依赖BGP
      - 兼容性好
      - 性能中等
    
    配置:
      encapsulation: VXLAN
      vxlanMode: Always | CrossSubnet
    
    适用场景:
      - BGP不可用
      - 混合云环境
      - 安全隔离需求
```

**网络模式配置示例**:

```yaml
# ========================================
# BGP模式 (无封装)
# ========================================
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  calicoNetwork:
    bgp: Enabled
    ipPools:
    - cidr: 10.244.0.0/16
      encapsulation: None
      natOutgoing: Enabled

---
# ========================================
# IPIP模式 (CrossSubnet)
# ========================================
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  calicoNetwork:
    bgp: Enabled
    ipPools:
    - cidr: 10.244.0.0/16
      encapsulation: IPIP
      ipipMode: CrossSubnet
      natOutgoing: Enabled

---
# ========================================
# VXLAN模式
# ========================================
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  calicoNetwork:
    bgp: Disabled
    ipPools:
    - cidr: 10.244.0.0/16
      encapsulation: VXLAN
      natOutgoing: Enabled
```

---

## 4. IP地址管理 (IPAM)

```yaml
Calico_IPAM:
  IP池管理:
    blockSize:
      - /26: 64个IP (默认)
      - /28: 16个IP (小集群)
      - /24: 256个IP (大Pod数)
    
    分配策略:
      - 节点级别分配Block
      - Block内分配IP
      - 自动扩展和回收
  
  IP池配置:
    default-ipv4-ippool:
      cidr: 10.244.0.0/16
      blockSize: 26
      allowedUses: ["Workload", "Tunnel"]
      disableBGPExport: false
      natOutgoing: true
```

**IP池操作**:

```bash
# ========================================
# 查看IP池
# ========================================

calicoctl get ippool -o wide

# 详细信息
calicoctl get ippool default-ipv4-ippool -o yaml

# ========================================
# 创建新IP池
# ========================================

cat <<EOF | calicoctl apply -f -
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: new-pool
spec:
  cidr: 10.245.0.0/16
  blockSize: 26
  ipipMode: CrossSubnet
  natOutgoing: true
  nodeSelector: "!all()"  # 不自动分配
EOF

# ========================================
# 修改IP池
# ========================================

# 禁用IP池
calicoctl patch ippool default-ipv4-ippool -p '{"spec":{"disabled":true}}'

# 修改NAT
calicoctl patch ippool default-ipv4-ippool -p '{"spec":{"natOutgoing":false}}'

# ========================================
# IP地址分配查看
# ========================================

# 查看IPAM配置
calicoctl get ipamconfig default -o yaml

# 查看Block分配
calicoctl ipam show

# 查看节点Block
calicoctl ipam show --show-blocks

# 释放IP
calicoctl ipam release --ip=10.244.1.5
```

---

## 5. BGP配置

```yaml
BGP_Configuration:
  BGP模式:
    Full-mesh (默认):
      - 所有节点互联
      - 适合小规模 (<100节点)
      - 配置简单
    
    Route Reflector:
      - 分层BGP
      - 适合大规模 (>100节点)
      - RR作为集中点
    
    ToR (Top-of-Rack):
      - 与物理路由器对等
      - 与数据中心集成
      - 高可用
  
  BGP参数:
    ASN: 自治系统号
    Router ID: BGP路由器ID
    Listen Port: 179 (BGP标准)
    Hold Time: 保持时间
    Keep Alive: 心跳间隔
```

**BGP配置示例**:

```yaml
# ========================================
# 1. 全网格BGP (默认)
# ========================================

# 查看BGP配置
calicoctl get bgpconfig default -o yaml

# 修改AS号
apiVersion: projectcalico.org/v3
kind: BGPConfiguration
metadata:
  name: default
spec:
  logSeverityScreen: Info
  nodeToNodeMeshEnabled: true
  asNumber: 64512

---
# ========================================
# 2. Route Reflector配置
# ========================================

# 禁用全网格
calicoctl patch bgpconfig default -p '{"spec":{"nodeToNodeMeshEnabled":false}}'

# 标记RR节点
kubectl label node rr-node01 route-reflector=true
kubectl label node rr-node02 route-reflector=true

# 配置RR
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: rr-node01
spec:
  peerIP: 192.168.1.10
  asNumber: 64512
  nodeSelector: !route-reflector

---
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: rr-node02
spec:
  peerIP: 192.168.1.11
  asNumber: 64512
  nodeSelector: !route-reflector

# 配置节点为RR客户端
calicoctl apply -f - <<EOF
apiVersion: projectcalico.org/v3
kind: Node
metadata:
  name: rr-node01
spec:
  bgp:
    routeReflectorClusterID: 224.0.0.1
EOF

---
# ========================================
# 3. 外部BGP对等
# ========================================

# 与ToR路由器对等
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: tor-switch
spec:
  peerIP: 192.168.1.1
  asNumber: 65000
  nodeSelector: rack == 'rack-1'

---
# 多个ToR
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: tor-switch-01
spec:
  peerIP: 192.168.1.1
  asNumber: 65000
---
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: tor-switch-02
spec:
  peerIP: 192.168.1.2
  asNumber: 65000
```

**BGP管理命令**:

```bash
# 查看BGP状态
calicoctl node status

# 查看BGP对等体
calicoctl get bgppeer

# 查看BGP配置
calicoctl get bgpconfig

# 查看节点BGP
calicoctl get node <node-name> -o yaml | grep -A 10 bgp

# BIRD状态 (在Calico Node Pod内)
kubectl exec -n calico-system <calico-node-pod> -c calico-node -- birdcl show protocols
kubectl exec -n calico-system <calico-node-pod> -c calico-node -- birdcl show route
```

---

## 6. NetworkPolicy

```yaml
# ========================================
# 默认拒绝所有入站
# ========================================
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  selector: all()
  types:
  - Ingress
  order: 1000

---
# ========================================
# 允许特定Pod访问
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080

---
# ========================================
# Calico GlobalNetworkPolicy
# ========================================
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: allow-cluster-internal
spec:
  selector: has(kubernetes.io/hostname)
  types:
  - Ingress
  ingress:
  - action: Allow
    source:
      nets:
      - 10.244.0.0/16  # Pod CIDR
      - 10.96.0.0/12   # Service CIDR
  order: 100
```

详细NetworkPolicy配置见：[NetworkPolicy策略文档](04_NetworkPolicy策略.md)

---

## 7. 运维管理

```bash
# ========================================
# 节点管理
# ========================================

# 查看Calico节点
calicoctl get nodes

# 节点详情
calicoctl get node <node-name> -o yaml

# 删除节点
calicoctl delete node <node-name>

# ========================================
# 工作负载管理
# ========================================

# 查看工作负载
calicoctl get workloadendpoint

# 特定命名空间
calicoctl get workloadendpoint -n production

# 工作负载详情
calicoctl get workloadendpoint <endpoint-name> -n <namespace> -o yaml

# ========================================
# 诊断信息收集
# ========================================

# 收集诊断信息
kubectl exec -n calico-system <calico-node-pod> -- calico-node -felix-dump

# 导出配置
calicoctl get nodes -o yaml > nodes-backup.yaml
calicoctl get ippool -o yaml > ippool-backup.yaml
calicoctl get bgpconfig -o yaml > bgpconfig-backup.yaml
calicoctl get bgppeer -o yaml > bgppeer-backup.yaml

# ========================================
# 升级Calico
# ========================================

# 查看当前版本
calicoctl version

# 使用Operator升级
kubectl set image -n tigera-operator deployment/tigera-operator \
  tigera-operator=quay.io/tigera/operator:v1.30.0

# 查看升级状态
kubectl get tigerastatus

# ========================================
# 监控指标
# ========================================

# Prometheus指标
curl http://<calico-node-ip>:9091/metrics

# 常用指标:
# - felix_active_local_endpoints
# - felix_active_local_policies
# - felix_int_dataplane_failures
# - felix_ipset_errors
```

---

## 8. 故障排查

```bash
# ========================================
# 基本检查
# ========================================

# Calico Pod状态
kubectl get pods -n calico-system

# 查看日志
kubectl logs -n calico-system <calico-node-pod> -c calico-node
kubectl logs -n calico-system <calico-kube-controllers-pod>

# ========================================
# BGP故障排查
# ========================================

# BGP状态
calicoctl node status

# 如果BGP down:
# 1. 检查Felix日志
kubectl logs -n calico-system <calico-node-pod> -c calico-node | grep -i bgp

# 2. 检查BIRD状态
kubectl exec -n calico-system <calico-node-pod> -c calico-node -- birdcl show protocols

# 3. 检查路由
ip route show

# 4. 检查防火墙
iptables -L -n -v | grep 179

# ========================================
# 网络连通性排查
# ========================================

# Pod到Pod不通:
# 1. 检查路由
kubectl exec <pod> -- ip route

# 2. 检查NetworkPolicy
calicoctl get networkpolicy -n <namespace>
calicoctl get globalnetworkpolicy

# 3. 测试连通性
kubectl exec <pod1> -- ping <pod2-ip>
kubectl exec <pod1> -- traceroute <pod2-ip>

# 4. 检查iptables
iptables -L -n -v | grep <pod-ip>

# ========================================
# IPAM问题排查
# ========================================

# IP地址耗尽:
# 1. 查看IP使用
calicoctl ipam show --show-blocks

# 2. 查看IP池
calicoctl get ippool -o wide

# 3. 释放未使用IP
calicoctl ipam check

# ========================================
# 性能问题排查
# ========================================

# 1. 检查CPU使用
kubectl top pod -n calico-system

# 2. 检查iptables规则数
iptables -L -n | wc -l

# 3. 检查路由表大小
ip route show | wc -l

# 4. 检查conntrack
cat /proc/sys/net/netfilter/nf_conntrack_count
cat /proc/sys/net/netfilter/nf_conntrack_max
```

---

## 9. 性能优化

```yaml
Performance_Optimization:
  网络模式:
    最佳: BGP (无封装)
    次选: IPIP CrossSubnet
    避免: IPIP Always
  
  BGP优化:
    大规模集群:
      - 使用Route Reflector
      - 禁用Full-mesh
      - 合理划分AS
    
    路由聚合:
      - 启用CIDR aggregation
      - 减少路由表大小
  
  iptables优化:
    - 启用iptables-legacy (如性能差)
    - 考虑ipvs模式
    - 定期清理规则
  
  Felix配置优化:
    # Felix配置
    apiVersion: projectcalico.org/v3
    kind: FelixConfiguration
    metadata:
      name: default
    spec:
      # 日志级别
      logSeverityScreen: Warning
      
      # 报告间隔
      reportingInterval: 0s
      
      # 健康检查
      healthEnabled: true
      healthPort: 9099
      
      # iptables优化
      iptablesRefreshInterval: 60s
      iptablesPostWriteCheckInterval: 1s
      
      # 路由优化
      routeRefreshInterval: 60s
      
      # BPF加速 (需内核支持)
      bpfEnabled: true
      bpfExternalServiceMode: DSR
  
  MTU优化:
    标准网络: 1500
    IPIP: 1480 (减去20字节)
    VXLAN: 1450 (减去50字节)
```

---

## 10. 最佳实践

```yaml
Best_Practices:
  网络规划:
    ✅ 提前规划Pod CIDR
    ✅ 预留足够IP地址
    ✅ 考虑IPv6支持
    ✅ 规划BGP AS号
  
  部署配置:
    ✅ 使用Operator部署
    ✅ 生产环境BGP模式
    ✅ 大集群启用Route Reflector
    ✅ 配置Typha (>50节点)
  
  安全:
    ✅ 启用NetworkPolicy
    ✅ 默认拒绝策略
    ✅ 最小权限原则
    ✅ 定期审计规则
  
  监控:
    ✅ 监控Felix和BIRD状态
    ✅ 监控BGP对等体
    ✅ 监控IPAM使用率
    ✅ 配置告警规则
  
  运维:
    ✅ 定期备份配置
    ✅ 测试故障恢复
    ✅ 建立运维手册
    ✅ 培训团队成员
  
  升级:
    ✅ 先升级测试环境
    ✅ 灰度升级节点
    ✅ 验证网络连通性
    ✅ 保留回滚方案
```

---

## 相关文档

- [CNI网络概述](01_CNI网络概述.md)
- [Cilium eBPF网络](03_Cilium_eBPF网络.md)
- [NetworkPolicy策略](04_NetworkPolicy策略.md)
- [Kubernetes网络故障排查](../02_Kubernetes部署/05_故障排查.md#3-网络故障排查)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪
