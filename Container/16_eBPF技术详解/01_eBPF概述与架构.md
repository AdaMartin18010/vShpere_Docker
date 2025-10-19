# eBPF技术详解

## 📋 目录

- [eBPF技术详解](#ebpf技术详解)
  - [📋 目录](#-目录)
  - [概述](#概述)
    - [什么是eBPF](#什么是ebpf)
    - [核心价值](#核心价值)
    - [版本历史](#版本历史)
  - [核心概念](#核心概念)
    - [eBPF架构](#ebpf架构)
    - [BPF程序类型](#bpf程序类型)
    - [BPF Maps](#bpf-maps)
    - [XDP (eXpress Data Path)](#xdp-express-data-path)
  - [Cilium网络方案](#cilium网络方案)
    - [Cilium概述](#cilium概述)
    - [Cilium架构](#cilium架构)
    - [Cilium部署](#cilium部署)
    - [Cilium网络策略](#cilium网络策略)
    - [Service Mesh无Sidecar](#service-mesh无sidecar)
  - [Hubble可观测性](#hubble可观测性)
    - [Hubble概述](#hubble概述)
    - [Hubble架构](#hubble架构)
    - [使用Hubble CLI](#使用hubble-cli)
    - [Hubble指标](#hubble指标)
  - [Falco安全审计](#falco安全审计)
    - [Falco概述](#falco概述)
    - [Falco架构](#falco架构)
    - [Falco部署](#falco部署)
    - [Falco规则](#falco规则)
    - [Falco集成](#falco集成)
  - [应用场景](#应用场景)
    - [高性能网络](#高性能网络)
    - [零信任网络](#零信任网络)
    - [性能分析](#性能分析)
  - [最佳实践](#最佳实践)
    - [Cilium生产部署](#cilium生产部署)
    - [Falco生产部署](#falco生产部署)
    - [监控告警](#监控告警)
  - [参考资料](#参考资料)
    - [官方文档](#官方文档)
    - [学习资源](#学习资源)
    - [社区](#社区)

---

## 概述

### 什么是eBPF

**Extended Berkeley Packet Filter** (eBPF) 是Linux内核中的革命性技术，允许在内核中运行沙箱程序，无需修改内核源代码或加载内核模块。

### 核心价值

**技术优势**:

- 🚀 高性能: 内核空间执行，零拷贝
- 🛡️ 安全性: 验证器确保程序安全
- 🔧 灵活性: 动态加载和卸载
- 📊 可观测性: 深度系统洞察
- 🌐 网络加速: 绕过内核网络栈

**应用领域**:

```text
网络:
  - 负载均衡
  - 流量过滤
  - 服务网格

安全:
  - 运行时安全
  - 威胁检测
  - 审计日志

可观测性:
  - 性能分析
  - 追踪跟踪
  - 指标收集

性能优化:
  - 网络加速
  - 存储优化
  - CPU调度
```

### 版本历史

| 内核版本 | 时间 | 重要特性 |
|---------|------|---------|
| 3.18 | 2014 | BPF系统调用引入 |
| 4.1 | 2015 | BPF maps支持 |
| 4.8 | 2016 | XDP (eXpress Data Path) |
| 4.16 | 2018 | BTF (BPF Type Format) |
| 5.2 | 2019 | BPF迭代器 |
| 5.13 | 2021 | BPF定时器 |
| **6.1** | 2022 | BPF链接支持 |
| **6.8** | 2024 | 增强的BPF验证器 |

---

## 核心概念

### eBPF架构

```text
┌─────────────────────────────────────────┐
│        用户空间应用                      │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Cilium   │  │ Falco    │  │ Custom │ │
│  └──────────┘  └──────────┘  └────────┘ │
├─────────────────────────────────────────┤
│        libbpf / BPF系统调用              │
├─────────────────────────────────────────┤
│             Linux Kernel                │
│  ┌───────────────────────────────────┐  │
│  │     BPF Verifier (验证器)          │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │     BPF JIT Compiler              │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │     Hook Points (挂载点)           │  │
│  │  - XDP  - TC  - cgroup            │  │
│  │  - kprobe  - tracepoint           │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │     BPF Maps (数据共享)            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### BPF程序类型

**常用程序类型**:

```c
BPF_PROG_TYPE_XDP            // XDP网络处理
BPF_PROG_TYPE_SOCKET_FILTER  // Socket过滤
BPF_PROG_TYPE_KPROBE         // 内核探针
BPF_PROG_TYPE_TRACEPOINT     // 跟踪点
BPF_PROG_TYPE_CGROUP_SKB     // cgroup网络
BPF_PROG_TYPE_CGROUP_SOCK    // cgroup socket
BPF_PROG_TYPE_PERF_EVENT     // 性能事件
BPF_PROG_TYPE_LSM            // 安全模块
```

**简单示例**:

```c
// XDP丢弃特定端口的数据包
SEC("xdp")
int xdp_drop_port(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;
    
    if (eth->h_proto != htons(ETH_P_IP))
        return XDP_PASS;
    
    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end)
        return XDP_PASS;
    
    if (ip->protocol != IPPROTO_TCP)
        return XDP_PASS;
    
    struct tcphdr *tcp = (void *)(ip + 1);
    if ((void *)(tcp + 1) > data_end)
        return XDP_PASS;
    
    // 丢弃目标端口为22的包
    if (tcp->dest == htons(22))
        return XDP_DROP;
    
    return XDP_PASS;
}
```

### BPF Maps

**Map类型**:

```yaml
Hash Maps:
  - BPF_MAP_TYPE_HASH: 通用哈希表
  - BPF_MAP_TYPE_LRU_HASH: LRU哈希表
  - BPF_MAP_TYPE_PERCPU_HASH: 每CPU哈希表

Array Maps:
  - BPF_MAP_TYPE_ARRAY: 固定大小数组
  - BPF_MAP_TYPE_PERCPU_ARRAY: 每CPU数组
  - BPF_MAP_TYPE_PROG_ARRAY: 程序数组(尾调用)

Special Maps:
  - BPF_MAP_TYPE_RING福: 环形缓冲区
  - BPF_MAP_TYPE_QUEUE: 队列
  - BPF_MAP_TYPE_STACK: 栈
  - BPF_MAP_TYPE_LPM_TRIE: 最长前缀匹配树
```

**Map使用示例**:

```c
// 定义Map
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, __u32);    // IP地址
    __type(value, __u64);  // 包计数
} packet_count SEC(".maps");

// BPF程序中使用
SEC("xdp")
int count_packets(struct xdp_md *ctx) {
    __u32 ip_src = ...;  // 提取源IP
    __u64 *count, initial = 1;
    
    count = bpf_map_lookup_elem(&packet_count, &ip_src);
    if (count) {
        __sync_fetch_and_add(count, 1);
    } else {
        bpf_map_update_elem(&packet_count, &ip_src, &initial, BPF_ANY);
    }
    
    return XDP_PASS;
}

// 用户空间读取
int fd = bpf_obj_get("/sys/fs/bpf/packet_count");
__u32 key;
__u64 value;
while (bpf_map_get_next_key(fd, &key, &key) == 0) {
    bpf_map_lookup_elem(fd, &key, &value);
    printf("IP: %u, Count: %llu\n", key, value);
}
```

### XDP (eXpress Data Path)

**XDP模式**:

```yaml
Native XDP (推荐):
  位置: 网卡驱动
  性能: 最高 (14-24 Mpps)
  要求: 驱动支持
  使用: ip link set dev eth0 xdp obj program.o

Offloaded XDP:
  位置: 网卡硬件
  性能: 极高 (100+ Mpps)
  要求: SmartNIC (Netronome, Mellanox)
  使用: ip link set dev eth0 xdpoffload obj program.o

Generic XDP:
  位置: 内核网络栈
  性能: 较低 (5-10 Mpps)
  要求: 无特殊要求
  使用: ip link set dev eth0 xdpgeneric obj program.o
```

**XDP动作**:

```c
XDP_DROP    // 丢弃数据包 (DDoS防护)
XDP_PASS    // 传递到网络栈
XDP_TX      // 从同一网卡发回
XDP_REDIRECT  // 重定向到其他网卡
XDP_ABORTED // 异常终止
```

**XDP性能**:

```yaml
测试环境:
  CPU: Intel Xeon Gold 6258R @ 2.7GHz
  NIC: Mellanox ConnectX-6 DX (100GbE)
  Packet Size: 64 bytes
  Kernel: 6.1

性能数据:
  XDP_DROP (Native):
    - 单核: 24 Mpps
    - 多核: 95 Mpps
    - 延迟: < 10 μs
  
  传统iptables DROP:
    - 单核: 1.5 Mpps
    - 多核: 6 Mpps
    - 延迟: 50-100 μs
  
  性能提升: **16倍**
```

---

## Cilium网络方案

### Cilium概述

**项目信息**:

- 创建时间: 2016年
- CNCF状态: 毕业项目 (2021年10月)
- 最新版本: **v1.16** (2024年10月)
- GitHub Star: 19k+

**核心特性**:

- 🌐 eBPF原生CNI
- 🔒 网络策略执行
- 🔍 深度网络可观测性
- 🚀 服务网格 (无Sidecar)
- 🛡️ 透明加密
- 🌍 多集群连接

### Cilium架构

```text
┌──────────────────────────────────────────────┐
│           Kubernetes集群                      │
│  ┌────────────────────────────────────────┐  │
│  │  Pod                  Pod              │  │
│  │  ┌─────────┐          ┌─────────┐      │  │
│  │  │Container│          │Container│      │  │
│  │  └────┬────┘          └────┬────┘      │  │
│  │       │veth                 │veth      │  │
│  └───────┼─────────────────────┼──────────┘  │
├───────────┼────────────────────┼─────────────┤
│           ↓                     ↓            │
│  ┌─────────────────────────────────────────┐ │
│  │  Cilium Agent (每节点)                   │ │
│  │  ┌─────────────────────────────────┐    │ │
│  │  │  eBPF Datapath                  │    │ │
│  │  │  - tc (Traffic Control)         │    │ │
│  │  │  - XDP                          │    │ │
│  │  │  - Socket operations            │    │ │
│  │  │  - Network Policy               │    │ │
│  │  └─────────────────────────────────┘    │ │
│  │  ┌─────────────────────────────────┐    │ │
│  │  │  Identity Management            │    │ │
│  │  └─────────────────────────────────┘    │ │
│  └─────────────────────────────────────────┘ │
├──────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐ │
│  │  Cilium Operator (集群级别)              │ │
│  │  - IPAM                                 │ │
│  │  - CRD管理                               │ │
│  │  - Cluster Mesh                         │ │
│  └─────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

### Cilium部署

**Helm安装**:

```bash
# 添加Helm仓库
helm repo add cilium https://helm.cilium.io/
helm repo update

# 安装Cilium 1.16
helm install cilium cilium/cilium \
  --version 1.16.0 \
  --namespace kube-system \
  --set kubeProxyReplacement=true \
  --set k8sServiceHost=API_SERVER_IP \
  --set k8sServicePort=API_SERVER_PORT \
  --set operator.replicas=1 \
  --set ipam.mode=kubernetes \
  --set encryption.enabled=true \
  --set encryption.type=wireguard \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true

# 验证安装
cilium status --wait
```

**高级配置**:

```yaml
# values.yaml
# Cilium 1.16 生产配置

# 基础配置
kubeProxyReplacement: "true"  # 完全替换kube-proxy
k8sServiceHost: "10.0.0.1"
k8sServicePort: "6443"

# IPAM配置
ipam:
  mode: kubernetes  # 或 cluster-pool, azure, aws-eni
  operator:
    clusterPoolIPv4PodCIDRList: ["10.244.0.0/16"]
    clusterPoolIPv4MaskSize: 24

# 数据平面
bpf:
  masquerade: true
  hostRouting: true
  tproxy: true
  monitorAggregation: medium
  clockProbe: true
  
# XDP加速
xdp:
  enabled: true
  mode: native  # native, offload, generic

# 网络策略
policyEnforcementMode: default  # default, always, never
policyAuditMode: false

# 加密
encryption:
  enabled: true
  type: wireguard  # wireguard 或 ipsec
  nodeEncryption: true

# 服务网格 (无Sidecar)
serviceTopology: true
socketLB:
  enabled: true
  hostNamespaceOnly: false

# Hubble可观测性
hubble:
  enabled: true
  relay:
    enabled: true
    replicas: 2
  ui:
    enabled: true
    replicas: 2
  metrics:
    enabled:
      - dns
      - drop
      - tcp
      - flow
      - icmp
      - http

# BGP (高级路由)
bgpControlPlane:
  enabled: true

# 多集群
clusterName: cluster1
clusterID: 1
cluster:
  name: cluster1
  id: 1

# 性能调优
bpfMapDynamicSizeRatio: 0.0025
tunnelProtocol: vxlan  # vxlan, geneve, disabled
autoDirectNodeRoutes: true

# 监控
prometheus:
  enabled: true
  serviceMonitor:
    enabled: true

# 资源limits
operator:
  replicas: 2
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 100m
      memory: 128Mi

agent:
  resources:
    limits:
      cpu: 4000m
      memory: 4Gi
    requests:
      cpu: 100m
      memory: 512Mi
```

### Cilium网络策略

**L3/L4策略**:

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: l3-l4-policy
spec:
  endpointSelector:
    matchLabels:
      app: backend
  
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: frontend
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
  
  egress:
  - toEndpoints:
    - matchLabels:
        app: database
    toPorts:
    - ports:
      - port: "5432"
        protocol: TCP
  
  - toFQDNs:
    - matchName: "api.example.com"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
```

**L7策略 (HTTP)**:

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: l7-http-policy
spec:
  endpointSelector:
    matchLabels:
      app: api-gateway
  
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: web-frontend
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/api/v1/users"
        - method: "POST"
          path: "/api/v1/users"
          headers:
          - "Content-Type: application/json"
```

**DNS策略**:

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: dns-policy
spec:
  endpointSelector:
    matchLabels:
      app: app
  
  egress:
  # 允许访问特定域名
  - toFQDNs:
    - matchName: "*.example.com"
    - matchPattern: "*.cdn.cloudflare.net"
  
  # 允许DNS查询
  - toEndpoints:
    - matchLabels:
        "k8s:io.kubernetes.pod.namespace": kube-system
        "k8s:k8s-app": kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
      rules:
        dns:
        - matchPattern: "*"
```

### Service Mesh无Sidecar

**传统Sidecar vs Cilium**:

```yaml
传统服务网格 (Istio):
┌─────────────────┐
│  Pod            │
│  ┌──────────┐   │
│  │ App      │   │
│  └────┬─────┘   │
│       ↓         │
│  ┌──────────┐   │
│  │ Envoy    │   │  ← Sidecar容器
│  │ (代理)   │   │    (额外资源消耗)
│  └────┬─────┘   │
└───────┼─────────┘
        ↓
   网络栈

Cilium eBPF:
┌─────────────────┐
│  Pod            │
│  ┌──────────┐   │
│  │ App      │   │  ← 无Sidecar
│  └────┬─────┘   │
└───────┼─────────┘
        ↓
  ┌──────────┐
  │ eBPF     │       ← 内核空间
  │ 数据平面  │         (零额外资源)
  └──────────┘
```

**启用服务网格**:

```yaml
# Cilium配置
socketLB:
  enabled: true
  hostNamespaceOnly: false

# 自动L7负载均衡
loadBalancer:
  algorithm: random  # random, maglev
  mode: dsr  # dsr, snat, hybrid
  
# mTLS (Cilium 1.16+)
authentication:
  mode: required
  mutual:
    spire:
      enabled: true
      install:
        enabled: true
```

**性能对比**:

```yaml
测试场景: HTTP请求延迟 (P99)

Istio with Envoy:
  Latency: 12ms
  CPU: 300m (sidecar)
  Memory: 150Mi (sidecar)

Cilium eBPF:
  Latency: 2ms
  CPU: 50m (agent)
  Memory: 100Mi (agent)

性能提升:
  延迟: ↓ 83%
  CPU: ↓ 83%
  内存: ↓ 33%
```

---

## Hubble可观测性

### Hubble概述

**Hubble**是Cilium的网络可观测性组件，提供:

- 🔍 网络流量可视化
- 📊 服务依赖图
- 🚨 网络问题诊断
- 📈 性能指标

### Hubble架构

```text
┌──────────────────────────────────────────┐
│  Hubble UI (Web界面)                      │
└────────────────┬─────────────────────────┘
                 ↓
┌──────────────────────────────────────────┐
│  Hubble Relay (聚合层)                    │
└────────────────┬─────────────────────────┘
                 ↓
     ┌───────────┴───────────┐
     ↓                       ↓
┌─────────────┐       ┌─────────────┐
│ Hubble      │       │ Hubble      │
│ (Node 1)    │       │ (Node 2)    │
│             │       │             │
│ eBPF events │       │ eBPF events │
└─────────────┘       └─────────────┘
```

### 使用Hubble CLI

**安装**:

```bash
# 安装Hubble CLI
HUBBLE_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/hubble/master/stable.txt)
curl -L --fail --remote-name-all \
  https://github.com/cilium/hubble/releases/download/$HUBBLE_VERSION/hubble-linux-amd64.tar.gz{,.sha256sum}
sha256sum --check hubble-linux-amd64.tar.gz.sha256sum
sudo tar xzvfC hubble-linux-amd64.tar.gz /usr/local/bin
rm hubble-linux-amd64.tar.gz{,.sha256sum}

# 端口转发
kubectl port-forward -n kube-system svc/hubble-relay 4245:80 &
```

**查看流量**:

```bash
# 实时观察所有流量
hubble observe

# 查看特定namespace
hubble observe --namespace default

# 查看特定Pod
hubble observe --pod default/nginx-xxx

# 查看被拒绝的流量
hubble observe --verdict DROPPED

# 查看HTTP流量
hubble observe --protocol http

# 查看DNS查询
hubble observe --protocol dns

# 过滤源/目标
hubble observe --from-pod default/app --to-pod default/db
```

**服务依赖图**:

```bash
# 生成服务地图
hubble observe --since 1h | hubble observe --output json \
  | jq -r '.flow | "\(.source.namespace)/\(.source.pod_name) -> \(.destination.namespace)/\(.destination.pod_name)"' \
  | sort | uniq

# 使用Hubble UI
kubectl port-forward -n kube-system svc/hubble-ui 12000:80
# 访问 http://localhost:12000
```

### Hubble指标

**Prometheus指标**:

```yaml
hubble:
  metrics:
    enabled:
    # 网络流量
    - flow:
        - source_namespace
        - destination_namespace
        - verdict
    
    # DNS查询
    - dns:
        - query
        - rcode
        - source_namespace
    
    # HTTP请求
    - http:
        - method
        - status
        - source_namespace
        - destination_namespace
    
    # TCP连接
    - tcp:
        - family
        - source_namespace
        - destination_namespace
    
    # 丢包
    - drop:
        - reason
        - protocol
        - source_namespace
    
    # ICMP
    - icmp:
        - family
        - type
```

**Grafana仪表板**:

```yaml
# 导入Cilium官方仪表板
仪表板ID:
  - Cilium Metrics: 16611
  - Cilium Operator: 16612
  - Hubble Metrics: 16613
  - Hubble L7: 16614

# 自定义PromQL查询
queries:
  # 每秒请求数
  rate(hubble_http_requests_total[5m])
  
  # HTTP错误率
  rate(hubble_http_requests_total{status=~"5.."}[5m]) 
  / rate(hubble_http_requests_total[5m])
  
  # 丢包率
  rate(hubble_drop_total[5m])
  
  # DNS查询延迟
  histogram_quantile(0.99, 
    rate(hubble_dns_query_duration_seconds_bucket[5m]))
```

---

## Falco安全审计

### Falco概述

**项目信息**:

- 创建者: Sysdig
- CNCF状态: 毕业项目 (2024年1月)
- 最新版本: **v0.37** (2024年3月)
- GitHub Star: 7k+

**核心功能**:

- 🔒 运行时安全监控
- 🚨 威胁检测
- 📝 审计日志
- 🔍 异常行为识别

### Falco架构

```text
┌──────────────────────────────────────────┐
│  Falco                                    │
│  ┌────────────────────────────────────┐  │
│  │  Rules Engine                      │  │
│  │  - 加载规则                        │  │
│  │  - 匹配事件                        │  │
│  │  - 生成告警                        │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  Outputs                           │  │
│  │  - stdout  - syslog               │  │
│  │  - file    - HTTP                 │  │
│  └────────────────────────────────────┘  │
└───────────────┬──────────────────────────┘
                ↓
┌───────────────────────────────────────────┐
│  Event Sources                            │
│  ┌─────────────┐  ┌──────────────────┐   │
│  │ Syscalls    │  │  Kubernetes      │   │
│  │ (eBPF/mod)  │  │  Audit Events    │   │
│  └─────────────┘  └──────────────────┘   │
└───────────────────────────────────────────┘
                ↓
┌───────────────────────────────────────────┐
│  Linux Kernel                             │
│  - eBPF probes                            │
│  - Kernel module (legacy)                 │
│  - Syscall hooks                          │
└───────────────────────────────────────────┘
```

### Falco部署

**Helm安装**:

```bash
# 添加仓库
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

# 安装Falco with eBPF
helm install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace \
  --set driver.kind=ebpf \
  --set falco.grpc.enabled=true \
  --set falco.grpcOutput.enabled=true \
  --set falcosidekick.enabled=true \
  --set falcosidekick.webui.enabled=true

# 验证
kubectl logs -n falco -l app.kubernetes.io/name=falco
```

**配置文件**:

```yaml
# falco-config.yaml
falco:
  rules_file:
    - /etc/falco/falco_rules.yaml
    - /etc/falco/k8s_audit_rules.yaml
    - /etc/falco/rules.d
  
  json_output: true
  json_include_output_property: true
  
  priority: debug
  
  buffered_outputs: true
  
  outputs:
    rate: 1
    max_burst: 1000
  
  syslog_output:
    enabled: false
  
  file_output:
    enabled: true
    keep_alive: false
    filename: /var/log/falco/events.log
  
  stdout_output:
    enabled: true
  
  grpc:
    enabled: true
    bind_address: "0.0.0.0:5060"
    threadiness: 8
  
  grpc_output:
    enabled: true

# eBPF配置
ebpf:
  probe: ""  # 使用内置probe
  
  # 性能调优
  buf_size_preset: 4
  drop_failed_exit: false
```

### Falco规则

**默认规则示例**:

```yaml
# 检测Shell在容器中运行
- rule: Terminal shell in container
  desc: A shell was used in a container
  condition: >
    spawned_process and 
    container and
    proc.name in (bash, sh, zsh, csh, ksh, fish)
  output: >
    Shell spawned in container
    (user=%user.name container_id=%container.id 
    container_name=%container.name image=%container.image.repository 
    command=%proc.cmdline)
  priority: WARNING
  tags: [container, shell, mitre_execution]

# 检测敏感文件读取
- rule: Read sensitive file untrusted
  desc: Detect读取敏感文件
  condition: >
    open_read and 
    sensitive_files and 
    not trusted_containers
  output: >
    Sensitive file read
    (user=%user.name command=%proc.cmdline 
    file=%fd.name parent=%proc.pname 
    container_id=%container.id image=%container.image.repository)
  priority: WARNING
  tags: [filesystem, mitre_credential_access]

# 检测容器特权升级
- rule: Create files below /dev
  desc: Detect创建设备文件
  condition: >
    open_write and 
    container and 
    fd.name startswith /dev/ and 
    not proc.name in (docker, dockerd, containerd)
  output: >
    File created below /dev in container
    (user=%user.name command=%proc.cmdline 
    file=%fd.name container_id=%container.id)
  priority: ERROR
  tags: [filesystem, mitre_persistence]

# 检测网络活动
- rule: Outbound Connection to C2 Servers
  desc: Detect出站连接到C2服务器
  condition: >
    outbound and 
    container and 
    fd.sip in (known_c2_ips)
  output: >
    Outbound connection to known C2 server
    (user=%user.name connection=%fd.name 
    container_id=%container.id image=%container.image.repository)
  priority: CRITICAL
  tags: [network, mitre_command_and_control]
```

**自定义规则**:

```yaml
# custom_rules.yaml
- macro: custom_app_container
  condition: container.image.repository contains "myapp"

- rule: Unexpected Process in App Container
  desc: Detect意外进程
  condition: >
    spawned_process and 
    custom_app_container and 
    not proc.name in (app, helper, monitor)
  output: >
    Unexpected process in application container
    (user=%user.name process=%proc.name command=%proc.cmdline 
    container_id=%container.id image=%container.image.repository)
  priority: WARNING
  tags: [container, process]

- rule: Cryptocurrency Mining Activity
  desc: Detect加密货币挖矿
  condition: >
    spawned_process and 
    container and 
    proc.name in (xmrig, minerd, cpuminer) or 
    proc.cmdline contains "stratum+tcp"
  output: >
    Cryptocurrency mining detected
    (user=%user.name process=%proc.name command=%proc.cmdline 
    container_id=%container.id image=%container.image.repository)
  priority: CRITICAL
  tags: [container, malware, mitre_impact]
```

### Falco集成

**与Falcosidekick集成**:

```yaml
# Falcosidekick配置
falcosidekick:
  config:
    # Slack通知
    slack:
      webhookurl: "https://hooks.slack.com/services/XXX"
      minimumpriority: "warning"
      messageformat: "Alert: {{.Rule}} - {{.Output}}"
    
    # Microsoft Teams
    teams:
      webhookurl: "https://outlook.office.com/webhook/XXX"
      minimumpriority: "error"
    
    # Elasticsearch
    elasticsearch:
      hostport: "http://elasticsearch:9200"
      index: "falco"
      type: "_doc"
      minimumpriority: "debug"
    
    # Prometheus
    prometheus:
      extralabels: "cluster:prod"
    
    # Webhook
    webhook:
      address: "http://webhook-receiver:8080/falco"
      minimumpriority: "warning"
```

---

## 应用场景

### 高性能网络

**DDoS防护**:

```c
// XDP DDoS防护
SEC("xdp")
int xdp_ddos_filter(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    
    // 解析以太网头
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;
    
    // 只处理IPv4
    if (eth->h_proto != htons(ETH_P_IP))
        return XDP_PASS;
    
    // 解析IP头
    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end)
        return XDP_PASS;
    
    // 获取源IP的包速率
    __u32 src_ip = ip->saddr;
    __u64 *rate = bpf_map_lookup_elem(&rate_limit_map, &src_ip);
    
    __u64 now = bpf_ktime_get_ns();
    if (rate) {
        // 检查速率限制 (100 Mbps)
        if ((*rate + (data_end - data)) > 100 * 1024 * 1024) {
            // 超过限制，丢弃
            __sync_fetch_and_add(&dropped_packets, 1);
            return XDP_DROP;
        }
        __sync_fetch_and_add(rate, data_end - data);
    } else {
        __u64 initial = data_end - data;
        bpf_map_update_elem(&rate_limit_map, &src_ip, &initial, BPF_ANY);
    }
    
    return XDP_PASS;
}
```

### 零信任网络

**实现微分段**:

```yaml
# Cilium实现零信任
---
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: zero-trust-frontend
spec:
  endpointSelector:
    matchLabels:
      tier: frontend
  
  # 默认拒绝所有入站
  ingress: []
  
  # 只允许特定出站
  egress:
  - toEndpoints:
    - matchLabels:
        tier: backend
        app: api
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "GET|POST"
          path: "/api/v1/.*"
          headers:
          - "Authorization: Bearer .*"

---
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: deny-all-default
spec:
  endpointSelector: {}
  ingress:
  - {}
  egress:
  - {}
```

### 性能分析

**CPU Profiling**:

```bash
# 使用bpftrace分析CPU热点
bpftrace -e 'profile:hz:99 { @[kstack] = count(); }'

# 分析特定进程
bpftrace -e 'profile:hz:99 /pid == 1234/ { @[ustack] = count(); }'

# 生成火焰图
bpftrace -e 'profile:hz:99 { @[kstack] = count(); }' > stacks.txt
flamegraph.pl stacks.txt > flamegraph.svg
```

**网络延迟追踪**:

```bash
# 追踪TCP连接延迟
bpftrace -e '
  kprobe:tcp_v4_connect { @start[tid] = nsecs; }
  kretprobe:tcp_v4_connect /@start[tid]/ {
    $duration = (nsecs - @start[tid]) / 1000;
    printf("TCP connect latency: %d μs\n", $duration);
    @latency = hist($duration);
    delete(@start[tid]);
  }
'
```

---

## 最佳实践

### Cilium生产部署

**集群规划**:

```yaml
小型集群 (< 50节点):
  - kube-proxy替换: 推荐
  - IPAM: kubernetes
  - 隧道: vxlan
  - 加密: wireguard

中型集群 (50-500节点):
  - kube-proxy替换: 推荐
  - IPAM: cluster-pool
  - 隧道: 禁用 (直接路由)
  - 加密: wireguard
  - BGP: 启用

大型集群 (> 500节点):
  - kube-proxy替换: 推荐
  - IPAM: cloud provider (AWS ENI/Azure IPAM)
  - 隧道: 禁用
  - 加密: IPsec (offload)
  - BGP: 启用
  - Cluster Mesh: 多集群
```

**性能调优**:

```yaml
# 网卡优化
ethtool -G eth0 rx 4096 tx 4096  # 增大环形缓冲
ethtool -K eth0 gro on gso on tso on  # 启用offload
ethtool -C eth0 adaptive-rx on adaptive-tx on  # 自适应合并

# 系统调优
sysctl -w net.core.netdev_max_backlog=5000
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"

# eBPF map大小
bpfMapDynamicSizeRatio: 0.0025  # 根据节点规模调整

# CPU亲和性
agent:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: node-role.kubernetes.io/control-plane
            operator: DoesNotExist
```

### Falco生产部署

**规则管理**:

```yaml
规则优先级:
  - EMERGENCY: 立即响应
  - ALERT: 15分钟内响应
  - CRITICAL: 1小时内响应
  - ERROR: 4小时内响应
  - WARNING: 24小时内响应
  - NOTICE/INFO/DEBUG: 记录但不告警

规则调优:
  1. 从默认规则开始
  2. 观察1-2周，记录误报
  3. 创建例外规则或调整条件
  4. 逐步启用更严格的规则
  5. 定期审查和更新
```

**性能优化**:

```yaml
# 减少CPU使用
falco:
  syscall_event_drops:
    threshold: .1  # 允许10%丢弃
    actions:
      - log
      - alert
  
  # 限制事件速率
  outputs:
    rate: 5  # 每秒最多5个告警
    max_burst: 100

  # 只监控关键syscalls
  base_syscalls:
    custom_set:
      - open
      - openat
      - execve
      - connect
      - accept

# 使用eBPF而非内核模块
driver:
  kind: ebpf  # 更低性能影响
```

### 监控告警

**关键指标**:

```yaml
Cilium:
  - cilium_endpoint_state: Endpoint健康状态
  - cilium_policy_enforcement_duration: 策略执行延迟
  - cilium_datapath_conntrack_gc_duration: 连接跟踪GC时间
  - cilium_bpf_map_ops_total: BPF map操作数
  
Hubble:
  - hubble_drop_total: 丢包数
  - hubble_tcp_flags_total: TCP标志统计
  - hubble_http_requests_total: HTTP请求数
  - hubble_dns_responses_total: DNS响应数

Falco:
  - falco_events_total: 事件总数
  - falco_drops_total: 丢弃事件数
  - falco_outputs_total: 输出数
  - falco_alerts_total: 告警数
```

**告警规则**:

```yaml
# Prometheus告警规则
groups:
- name: cilium
  rules:
  - alert: CiliumAgentDown
    expr: up{job="cilium-agent"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Cilium agent is down"
  
  - alert: HighPacketDrop
    expr: rate(cilium_drop_count_total[5m]) > 100
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High packet drop rate"
  
  - alert: PolicyEnforcementSlow
    expr: histogram_quantile(0.99, rate(cilium_policy_enforcement_duration_seconds_bucket[5m])) > 1
    for: 15m
    labels:
      severity: warning
    annotations:
      summary: "Policy enforcement is slow"

- name: falco
  rules:
  - alert: FalcoCriticalAlert
    expr: increase(falco_alerts_total{priority="Critical"}[5m]) > 0
    labels:
      severity: critical
    annotations:
      summary: "Falco critical security alert"
  
  - alert: FalcoHighDropRate
    expr: rate(falco_drops_total[5m]) / rate(falco_events_total[5m]) > 0.05
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Falco is dropping events"
```

---

## 参考资料

### 官方文档

**eBPF**:

- [eBPF Official](https://ebpf.io/)
- [Kernel BPF Documentation](https://www.kernel.org/doc/html/latest/bpf/)
- [libbpf GitHub](https://github.com/libbpf/libbpf)
- [BPF CO-RE](https://nakryiko.com/posts/bpf-portability-and-co-re/)

**Cilium**:

- [Cilium Documentation](https://docs.cilium.io/)
- [Cilium GitHub](https://github.com/cilium/cilium)
- [eBPF Datapath](https://docs.cilium.io/en/latest/concepts/ebpf/intro/)
- [Cilium Service Mesh](https://docs.cilium.io/en/latest/network/servicemesh/)

**Hubble**:

- [Hubble Documentation](https://docs.cilium.io/en/latest/gettingstarted/hubble/)
- [Hubble GitHub](https://github.com/cilium/hubble)
- [Hubble CLI Reference](https://docs.cilium.io/en/latest/gettingstarted/hubble_cli/)

**Falco**:

- [Falco Documentation](https://falco.org/docs/)
- [Falco GitHub](https://github.com/falcosecurity/falco)
- [Falco Rules](https://github.com/falcosecurity/rules)
- [Falcosidekick](https://github.com/falcosecurity/falcosidekick)

### 学习资源

**书籍**:

- "Linux Observability with BPF" - David Calavera, Lorenzo Fontana
- "BPF Performance Tools" - Brendan Gregg
- "Learning eBPF" - Liz Rice

**课程**:

- [eBPF Summit](https://ebpf.io/summit/)
- [Cilium Learning Platform](https://learn.cilium.io/)
- [Isovalent Academy](https://academy.isovalent.com/)

**博客**:

- [Cilium Blog](https://cilium.io/blog/)
- [Brendan Gregg's Blog](http://www.brendangregg.com/blog/)
- [Falco Blog](https://falco.org/blog/)

### 社区

- [eBPF Slack](https://ebpf.io/slack)
- [Cilium Slack](https://cilium.io/slack)
- [Falco Community](https://falco.org/community/)
- [CNCF eBPF SIG](https://github.com/cncf/tag-runtime)

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19  
**维护者**: 虚拟化容器化技术知识库项目组

**下一步阅读**:

- [02_eBPF编程实践](./02_eBPF编程实践.md)
- [03_Cilium高级特性](./03_Cilium高级特性.md)
- [04_Falco规则定制](./04_Falco规则定制.md)
