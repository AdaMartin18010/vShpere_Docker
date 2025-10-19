# Linkerd 部署与配置

> **返回**: [服务网格首页](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Linkerd 部署与配置](#linkerd-部署与配置)
  - [📋 目录](#-目录)
  - [1. Linkerd 概述](#1-linkerd-概述)
    - [1.1 什么是 Linkerd](#11-什么是-linkerd)
    - [1.2 核心特性](#12-核心特性)
    - [1.3 Linkerd vs Istio](#13-linkerd-vs-istio)
  - [2. Linkerd 架构](#2-linkerd-架构)
    - [2.1 整体架构](#21-整体架构)
    - [2.2 核心组件](#22-核心组件)
      - [2.2.1 Control Plane (控制平面)](#221-control-plane-控制平面)
      - [2.2.2 Data Plane (数据平面)](#222-data-plane-数据平面)
    - [2.3 工作原理](#23-工作原理)
  - [3. 安装部署](#3-安装部署)
    - [3.1 环境准备](#31-环境准备)
    - [3.2 CLI 安装](#32-cli-安装)
      - [3.2.1 安装 Linkerd CLI](#321-安装-linkerd-cli)
      - [3.2.2 预检查](#322-预检查)
      - [3.2.3 安装 Linkerd CRD](#323-安装-linkerd-crd)
      - [3.2.4 安装 Linkerd 控制平面](#324-安装-linkerd-控制平面)
      - [3.2.5 安装 Linkerd Viz (可观测性扩展)](#325-安装-linkerd-viz-可观测性扩展)
    - [3.3 Helm 安装](#33-helm-安装)
    - [3.4 验证安装](#34-验证安装)
      - [3.4.1 检查控制平面](#341-检查控制平面)
      - [3.4.2 部署示例应用](#342-部署示例应用)
      - [3.4.3 验证 mTLS](#343-验证-mtls)
  - [4. mTLS 配置](#4-mtls-配置)
    - [4.1 自动 mTLS](#41-自动-mtls)
    - [4.2 证书管理](#42-证书管理)
      - [4.2.1 生成根证书](#421-生成根证书)
      - [4.2.2 安装时指定证书](#422-安装时指定证书)
      - [4.2.3 证书轮换](#423-证书轮换)
    - [4.3 外部 CA 集成](#43-外部-ca-集成)
  - [5. 流量管理](#5-流量管理)
    - [5.1 TrafficSplit (金丝雀发布)](#51-trafficsplit-金丝雀发布)
    - [5.2 HTTPRoute (Gateway API)](#52-httproute-gateway-api)
    - [5.3 超时与重试](#53-超时与重试)
    - [5.4 熔断](#54-熔断)
  - [6. 可观测性](#6-可观测性)
    - [6.1 Linkerd Viz](#61-linkerd-viz)
    - [6.2 Prometheus 集成](#62-prometheus-集成)
    - [6.3 Grafana 仪表板](#63-grafana-仪表板)
    - [6.4 分布式追踪](#64-分布式追踪)
  - [7. 多集群](#7-多集群)
    - [7.1 Linkerd Multicluster](#71-linkerd-multicluster)
    - [7.2 跨集群服务](#72-跨集群服务)
  - [8. 故障排查](#8-故障排查)
    - [8.1 常见问题](#81-常见问题)
      - [8.1.1 Sidecar 未注入](#811-sidecar-未注入)
      - [8.1.2 mTLS 连接失败](#812-mtls-连接失败)
      - [8.1.3 流量路由不生效](#813-流量路由不生效)
    - [8.2 诊断命令](#82-诊断命令)
    - [8.3 日志分析](#83-日志分析)
  - [9. 性能优化](#9-性能优化)
    - [9.1 资源限制](#91-资源限制)
    - [9.2 高可用配置](#92-高可用配置)
  - [10. 最佳实践](#10-最佳实践)
    - [10.1 生产部署](#101-生产部署)
    - [10.2 安全加固](#102-安全加固)
    - [10.3 升级策略](#103-升级策略)
    - [10.4 部署检查清单](#104-部署检查清单)
  - [总结](#总结)

---

## 1. Linkerd 概述

### 1.1 什么是 Linkerd

**Linkerd** 是一个轻量级、易用的服务网格，专注于**简单性、性能和安全性**。由 Buoyant 公司开发并开源，是 CNCF 毕业项目。

**核心理念**:

- **Simple**: 简单易用，5 分钟快速上手
- **Fast**: 基于 Rust 编写的 linkerd2-proxy，性能优秀
- **Secure**: 自动 mTLS，零配置加密

**版本信息**:

- 当前稳定版本: v2.14.x (2024)
- 最低 Kubernetes 版本: v1.21+

---

### 1.2 核心特性

| 特性 | 说明 |
|-----|------|
| **自动 mTLS** | 零配置服务间加密 |
| **轻量级代理** | linkerd2-proxy (Rust) 资源占用极低 |
| **流量管理** | 金丝雀发布、流量分割、重试、超时 |
| **可观测性** | 实时指标、拓扑图、Tap (实时流量查看) |
| **多集群** | Linkerd Multicluster 扩展 |
| **简单易用** | CLI 友好，5 分钟完成部署 |

---

### 1.3 Linkerd vs Istio

| 对比项 | Linkerd | Istio |
|-------|---------|-------|
| **复杂度** | ⭐⭐ (低) | ⭐⭐⭐⭐⭐ (高) |
| **性能** | ⭐⭐⭐⭐⭐ (极佳) | ⭐⭐⭐ (良好) |
| **资源开销** | 极低 (20-50MB/Pod) | 高 (50-100MB/Pod) |
| **功能丰富度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **学习曲线** | 平缓 | 陡峭 |
| **多集群支持** | ⭐⭐ (有限) | ⭐⭐⭐⭐⭐ (强大) |
| **社区活跃度** | 高 | 极高 |

**选择建议**:

- **Linkerd**: 中小型团队、注重性能和稳定性、快速上手
- **Istio**: 大型企业、多集群/多云、需要高级功能

---

## 2. Linkerd 架构

### 2.1 整体架构

```text
┌──────────────────────────────────────────────────────────────┐
│              Linkerd Control Plane                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Destination  │  │  Identity    │  │  Proxy       │       │
│  │ (服务发现)    │  │  (证书管理)   │  │  Injector    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬────────────┬────────────┐
    │                 │            │            │
┌───▼─────────┐  ┌────▼────────┐  ┌────▼────────┐  
│  Pod 1      │  │  Pod 2      │  │  Pod 3      │  
│ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │  
│ │   App   │ │  │ │   App   │ │  │ │   App   │ │  
│ └────┬────┘ │  │ └────┬────┘ │  │ └────┬────┘ │  
│      │      │  │      │      │  │      │      │  
│ ┌────▼────┐ │  │ ┌────▼────┐ │  │ ┌────▼────┐ │  
│ │linkerd2-│◄┼──┼─┤linkerd2-│◄─┼──┼─┤linkerd2-│ │  
│ │ proxy   │ │  │ │ proxy   │  │  │ │ proxy   │ │  
│ └─────────┘ │  │ └─────────┘  │  │ └─────────┘ │  
└─────────────┘  └──────────────┘  └──────────────┘
```

---

### 2.2 核心组件

#### 2.2.1 Control Plane (控制平面)

**Destination (服务发现)**:

- 提供服务端点信息
- 支持权重路由
- 服务拓扑信息

**Identity (证书管理)**:

- 自动签发 TLS 证书
- 证书轮换 (默认 24 小时)
- 基于 Kubernetes ServiceAccount 的身份

**Proxy Injector (Sidecar 注入)**:

- 自动注入 linkerd2-proxy
- 配置代理参数

---

#### 2.2.2 Data Plane (数据平面)

**linkerd2-proxy**:

- 基于 Rust 编写
- 极低资源占用 (20-50MB 内存)
- 原生支持 gRPC/HTTP/2
- 自动 mTLS

**资源要求 (每 Pod)**:

```yaml
resources:
  requests:
    cpu: 20m
    memory: 20Mi
  limits:
    cpu: 1
    memory: 250Mi
```

---

### 2.3 工作原理

**请求流程**:

```text
1. Service A Pod 发起请求
        ↓
2. linkerd2-proxy (Service A) 拦截请求
        ↓
3. 查询 Destination 获取 Service B 端点
        ↓
4. 建立 mTLS 连接到 Service B 的 linkerd2-proxy
        ↓
5. Service B 的 linkerd2-proxy 转发请求到应用容器
        ↓
6. 响应沿原路返回
```

---

## 3. 安装部署

### 3.1 环境准备

**系统要求**:

- Kubernetes: v1.21+
- kubectl已配置
- 集群资源充足 (至少2核4GB可用)

**网络要求**:

- 允许 Pod 间通信
- 允许访问控制平面服务 (linkerd-destination:8086, linkerd-identity:8080)

---

### 3.2 CLI 安装

#### 3.2.1 安装 Linkerd CLI

```bash
# 下载最新版本
curl --proto '=https' --tlsv1.2 -sSfL https://run.linkerd.io/install | sh

# 添加到 PATH
export PATH=$HOME/.linkerd2/bin:$PATH

# 验证
linkerd version
```

---

#### 3.2.2 预检查

```bash
# 检查集群兼容性
linkerd check --pre

# 预期输出
✔ can initialize the client
✔ can query the Kubernetes API
✔ is running the minimum Kubernetes API version
✔ is running the minimum kubectl version
...
```

---

#### 3.2.3 安装 Linkerd CRD

```bash
# 安装 CRD
linkerd install --crds | kubectl apply -f -
```

---

#### 3.2.4 安装 Linkerd 控制平面

```bash
# 安装控制平面
linkerd install | kubectl apply -f -

# 等待就绪
linkerd check

# 预期输出
✔ control plane is running
✔ control plane self-check
✔ control plane pods are ready
...
```

---

#### 3.2.5 安装 Linkerd Viz (可观测性扩展)

```bash
# 安装 Viz 扩展
linkerd viz install | kubectl apply -f -

# 检查 Viz
linkerd viz check

# 启动仪表板
linkerd viz dashboard
# 自动打开浏览器访问 http://localhost:50750
```

---

### 3.3 Helm 安装

```bash
# 添加 Helm 仓库
helm repo add linkerd https://helm.linkerd.io/stable
helm repo update

# 安装 CRD
helm install linkerd-crds linkerd/linkerd-crds -n linkerd --create-namespace

# 安装控制平面
helm install linkerd-control-plane linkerd/linkerd-control-plane \
  -n linkerd \
  --set-file identityTrustAnchorsPEM=ca.crt \
  --set-file identity.issuer.tls.crtPEM=issuer.crt \
  --set-file identity.issuer.tls.keyPEM=issuer.key

# 安装 Viz
helm install linkerd-viz linkerd/linkerd-viz -n linkerd-viz --create-namespace
```

---

### 3.4 验证安装

#### 3.4.1 检查控制平面

```bash
# 检查所有组件
linkerd check

# 查看控制平面 Pods
kubectl get pods -n linkerd

# 预期输出
NAME                                      READY   STATUS    RESTARTS   AGE
linkerd-destination-xxxxx                 2/2     Running   0          2m
linkerd-identity-xxxxx                    2/2     Running   0          2m
linkerd-proxy-injector-xxxxx              2/2     Running   0          2m
```

---

#### 3.4.2 部署示例应用

```bash
# 部署 emojivoto 示例应用
curl --proto '=https' --tlsv1.2 -sSfL https://run.linkerd.io/emojivoto.yml \
  | kubectl apply -f -

# 注入 Linkerd Sidecar
kubectl get deploy -n emojivoto -o yaml \
  | linkerd inject - \
  | kubectl apply -f -

# 查看 Pod (应有 2/2 容器)
kubectl get pods -n emojivoto
```

---

#### 3.4.3 验证 mTLS

```bash
# 查看 mTLS 状态
linkerd viz edges deployment -n emojivoto

# 预期输出 (SRC 列应显示 "✓")
SRC                      DST                      SRC_NS       DST_NS       SECURED
emoji                    voting-svc               emojivoto    emojivoto    ✓
web                      emoji-svc                emojivoto    emojivoto    ✓
```

---

## 4. mTLS 配置

### 4.1 自动 mTLS

**Linkerd 默认启用 mTLS**，无需额外配置。

**工作流程**:

```text
1. Pod 启动时，linkerd2-proxy 向 Identity 服务请求证书
        ↓
2. Identity 服务验证 Pod 的 ServiceAccount
        ↓
3. 签发短期证书 (默认 24 小时有效期)
        ↓
4. linkerd2-proxy 使用证书建立 mTLS 连接
        ↓
5. 证书到期前自动轮换
```

---

### 4.2 证书管理

#### 4.2.1 生成根证书

```bash
# 生成信任锚点 (Trust Anchor)
step certificate create root.linkerd.cluster.local ca.crt ca.key \
  --profile root-ca --no-password --insecure

# 生成 Issuer 证书
step certificate create identity.linkerd.cluster.local issuer.crt issuer.key \
  --profile intermediate-ca --not-after 8760h --no-password --insecure \
  --ca ca.crt --ca-key ca.key
```

---

#### 4.2.2 安装时指定证书

```bash
linkerd install \
  --identity-trust-anchors-file ca.crt \
  --identity-issuer-certificate-file issuer.crt \
  --identity-issuer-key-file issuer.key \
  | kubectl apply -f -
```

---

#### 4.2.3 证书轮换

**Issuer 证书过期前轮换**:

```bash
# 1. 生成新的 Issuer 证书
step certificate create identity.linkerd.cluster.local issuer-new.crt issuer-new.key \
  --profile intermediate-ca --not-after 8760h --no-password --insecure \
  --ca ca.crt --ca-key ca.key

# 2. 更新 Secret
kubectl create secret tls linkerd-identity-issuer \
  --cert=issuer-new.crt \
  --key=issuer-new.key \
  --namespace=linkerd \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. 重启 Identity Pod
kubectl rollout restart deployment/linkerd-identity -n linkerd
```

---

### 4.3 外部 CA 集成

**使用 cert-manager 管理证书**:

```yaml
# cert-manager Issuer
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: linkerd-trust-anchor
  namespace: linkerd
spec:
  ca:
    secretName: linkerd-trust-anchor
---
# 自动轮换 Issuer 证书
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: linkerd-identity-issuer
  namespace: linkerd
spec:
  secretName: linkerd-identity-issuer
  duration: 48h
  renewBefore: 25h
  issuerRef:
    name: linkerd-trust-anchor
    kind: Issuer
  commonName: identity.linkerd.cluster.local
  dnsNames:
  - identity.linkerd.cluster.local
  isCA: true
  privateKey:
    algorithm: ECDSA
  usages:
  - cert sign
  - crl sign
  - server auth
  - client auth
```

---

## 5. 流量管理

### 5.1 TrafficSplit (金丝雀发布)

**使用 SMI TrafficSplit**:

```yaml
# 创建两个版本的 Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: v1
  template:
    metadata:
      labels:
        app: myapp
        version: v1
    spec:
      containers:
      - name: app
        image: myapp:v1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      version: v2
  template:
    metadata:
      labels:
        app: myapp
        version: v2
    spec:
      containers:
      - name: app
        image: myapp:v2
---
# 主服务 (稳定版本)
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
    version: v1
  ports:
  - port: 80
    targetPort: 8080
---
# v1 服务
apiVersion: v1
kind: Service
metadata:
  name: myapp-v1
spec:
  selector:
    app: myapp
    version: v1
  ports:
  - port: 80
    targetPort: 8080
---
# v2 服务
apiVersion: v1
kind: Service
metadata:
  name: myapp-v2
spec:
  selector:
    app: myapp
    version: v2
  ports:
  - port: 80
    targetPort: 8080
---
# TrafficSplit: 90% v1, 10% v2 (金丝雀)
apiVersion: split.smi-spec.io/v1alpha1
kind: TrafficSplit
metadata:
  name: myapp-canary
spec:
  service: myapp
  backends:
  - service: myapp-v1
    weight: 900  # 90%
  - service: myapp-v2
    weight: 100  # 10%
```

**验证流量分割**:

```bash
linkerd viz stat trafficsplit -n default

# 输出
NAME            APEX     LEAF        WEIGHT   SUCCESS      RPS
myapp-canary    myapp    myapp-v1      900m   100.00%   10.0rps
                         myapp-v2      100m   100.00%    1.1rps
```

---

### 5.2 HTTPRoute (Gateway API)

**安装 Gateway API CRD**:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v0.8.0/standard-install.yaml
```

**配置 HTTPRoute**:

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: HTTPRoute
metadata:
  name: myapp-route
spec:
  parentRefs:
  - name: myapp
    kind: Service
    group: core
    port: 80
  rules:
  - matches:
    - headers:
      - name: "user"
        value: "vip"
    backendRefs:
    - name: myapp-v2
      port: 80
  - backendRefs:
    - name: myapp-v1
      port: 80
```

---

### 5.3 超时与重试

**ServiceProfile (超时/重试)**:

```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: myapp.default.svc.cluster.local
  namespace: default
spec:
  routes:
  - name: GET /api
    condition:
      method: GET
      pathRegex: /api/.*
    timeout: 10s
    retryBudget:
      retryRatio: 0.2  # 最多重试 20% 请求
      minRetriesPerSecond: 10
      ttl: 10s
    isRetryable: true
```

---

### 5.4 熔断

**OutboundPolicy (熔断)**:

```yaml
apiVersion: policy.linkerd.io/v1alpha1
kind: Server
metadata:
  name: myapp-server
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: myapp
  port: 8080
  proxyProtocol: HTTP/2
---
apiVersion: policy.linkerd.io/v1beta1
kind: HTTPRoute
metadata:
  name: myapp-route
  namespace: default
spec:
  parentRefs:
  - name: myapp-server
    kind: Server
    group: policy.linkerd.io
  rules:
  - backendRefs:
    - name: myapp
      port: 80
    timeouts:
      request: 10s
    retry:
      codes: [503]
      maxRetries: 3
```

---

## 6. 可观测性

### 6.1 Linkerd Viz

**实时指标查看**:

```bash
# 查看命名空间统计
linkerd viz stat namespaces

# 查看 Deployment 统计
linkerd viz stat deploy -n default

# 查看 Pod 统计
linkerd viz stat pod -n default

# 输出示例
NAME           MESHED   SUCCESS      RPS   LATENCY_P50   LATENCY_P95   LATENCY_P99
myapp-v1-xxx     1/1   100.00%   10.0rps           5ms          10ms          15ms
```

**实时流量查看 (Tap)**:

```bash
# 查看 Deployment 的实时流量
linkerd viz tap deploy/myapp -n default

# 输出 (实时流更新)
req id=0:0 proxy=in  src=10.1.2.3:45678 dst=10.1.2.4:8080 tls=true :method=GET :authority=myapp:80 :path=/api
rsp id=0:0 proxy=in  src=10.1.2.3:45678 dst=10.1.2.4:8080 tls=true :status=200 latency=5ms
end id=0:0 proxy=in  src=10.1.2.3:45678 dst=10.1.2.4:8080 tls=true duration=5ms response-length=1234B
```

**Top 命令**:

```bash
# 查看最频繁的路由
linkerd viz top deploy/myapp -n default

# 输出
SOURCE           PATH           COUNT
frontend-xxx     GET /api         123
```

---

### 6.2 Prometheus 集成

**Linkerd Viz 内置 Prometheus**，但也可以集成外部 Prometheus。

**外部 Prometheus 配置**:

```yaml
# prometheus-additional-scrape-configs.yaml
- job_name: 'linkerd-controller'
  kubernetes_sd_configs:
  - role: pod
    namespaces:
      names:
      - linkerd
      - linkerd-viz
  relabel_configs:
  - source_labels:
    - __meta_kubernetes_pod_container_port_name
    action: keep
    regex: admin-http
  - source_labels: [__meta_kubernetes_pod_container_name]
    action: replace
    target_label: component

- job_name: 'linkerd-proxy'
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  - source_labels:
    - __meta_kubernetes_pod_container_name
    - __meta_kubernetes_pod_container_port_name
    action: keep
    regex: ^linkerd-proxy;linkerd-admin$
  - source_labels: [__meta_kubernetes_namespace]
    action: replace
    target_label: namespace
  - source_labels: [__meta_kubernetes_pod_name]
    action: replace
    target_label: pod
```

---

### 6.3 Grafana 仪表板

**导入 Linkerd 官方仪表板**:

- **Linkerd Top Line**: 全局概览
- **Linkerd Deployment**: Deployment 详情
- **Linkerd Pod**: Pod 详情
- **Linkerd Authority**: 按服务聚合

**导入方式**:

```bash
# 下载仪表板 JSON
curl -sL https://grafana.com/api/dashboards/15474/revisions/1/download > linkerd-top-line.json

# 在 Grafana UI 中导入
# Dashboards → Import → 上传 JSON
```

---

### 6.4 分布式追踪

**配置 Jaeger/Zipkin**:

```yaml
# 配置 Linkerd 代理发送追踪数据
apiVersion: v1
kind: ConfigMap
metadata:
  name: linkerd-config
  namespace: linkerd
data:
  config: |
    tracing:
      collector_svc_addr: jaeger-collector.observability:55678
      collector_svc_name: jaeger-collector
```

**应用层传递 Trace Headers**:

```go
// 应用需传递以下 Headers
headers := []string{
    "x-request-id",
    "x-b3-traceid",
    "x-b3-spanid",
    "x-b3-parentspanid",
    "x-b3-sampled",
    "x-b3-flags",
}
```

---

## 7. 多集群

### 7.1 Linkerd Multicluster

**安装 Multicluster 扩展**:

```bash
# 在两个集群都安装 Linkerd

# 集群 1
kubectl config use-context cluster1
linkerd multicluster install | kubectl apply -f -

# 集群 2
kubectl config use-context cluster2
linkerd multicluster install | kubectl apply -f -
```

---

### 7.2 跨集群服务

**链接两个集群**:

```bash
# 从集群 1 链接到集群 2
kubectl config use-context cluster1
linkerd multicluster link --cluster-name cluster2 \
  | kubectl apply -f -

# 验证
linkerd multicluster gateways

# 输出
CLUSTER    ALIVE    NUM_SVC    LATENCY
cluster2   True     5          10ms
```

**导出服务**:

```bash
# 在集群 2 导出服务
kubectl config use-context cluster2
kubectl label svc myapp mirror.linkerd.io/exported=true

# 在集群 1 访问跨集群服务
kubectl config use-context cluster1
curl myapp-cluster2.default.svc.cluster.local
```

---

## 8. 故障排查

### 8.1 常见问题

#### 8.1.1 Sidecar 未注入

**排查步骤**:

```bash
# 检查命名空间标签
kubectl get namespace default -o yaml | grep linkerd.io/inject

# 检查 Pod 注解
kubectl get pod <pod-name> -o jsonpath='{.metadata.annotations.linkerd\.io/inject}'

# 手动注入
kubectl get deploy <deployment-name> -o yaml \
  | linkerd inject - \
  | kubectl apply -f -
```

---

#### 8.1.2 mTLS 连接失败

**排查步骤**:

```bash
# 检查 mTLS 状态
linkerd viz edges pod -n default

# 检查证书
linkerd identity <pod-name> -n default

# 检查 Identity Pod 日志
kubectl logs -n linkerd deployment/linkerd-identity
```

---

#### 8.1.3 流量路由不生效

**排查步骤**:

```bash
# 检查 TrafficSplit
kubectl describe trafficsplit <name> -n default

# 查看实时流量
linkerd viz tap deploy/<deployment-name> -n default

# 检查 ServiceProfile
kubectl get serviceprofiles -A
```

---

### 8.2 诊断命令

```bash
# 全面检查
linkerd check
linkerd viz check

# 查看代理日志
kubectl logs <pod-name> -c linkerd-proxy -n default

# 查看控制平面日志
kubectl logs -n linkerd deployment/linkerd-destination
kubectl logs -n linkerd deployment/linkerd-identity

# 查看服务拓扑
linkerd viz edges deployment -n default

# 实时流量
linkerd viz tap deploy/<name> -n default

# 诊断特定 Pod
linkerd viz endpoints <pod-name> -n default
```

---

### 8.3 日志分析

**启用调试日志**:

```bash
# 重启 Pod 并启用调试日志
kubectl get pod <pod-name> -o yaml | \
  linkerd inject --proxy-log-level=debug - | \
  kubectl apply -f -

# 查看调试日志
kubectl logs <pod-name> -c linkerd-proxy --tail=100
```

---

## 9. 性能优化

### 9.1 资源限制

**调整 Sidecar 资源**:

```yaml
# ConfigMap: linkerd-config
apiVersion: v1
kind: ConfigMap
metadata:
  name: linkerd-config
  namespace: linkerd
data:
  proxy_resources: |
    requests:
      cpu: 20m
      memory: 20Mi
    limits:
      cpu: 1
      memory: 250Mi
```

**或使用注解**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    config.linkerd.io/proxy-cpu-request: "50m"
    config.linkerd.io/proxy-memory-request: "50Mi"
    config.linkerd.io/proxy-cpu-limit: "2"
    config.linkerd.io/proxy-memory-limit: "500Mi"
```

---

### 9.2 高可用配置

**控制平面高可用**:

```bash
# 使用 HA 配置安装
linkerd install --ha | kubectl apply -f -

# 默认配置
# - Destination: 3 副本
# - Identity: 3 副本
# - Proxy Injector: 3 副本
```

**网关高可用**:

```yaml
# 多副本 Gateway
apiVersion: apps/v1
kind: Deployment
metadata:
  name: linkerd-gateway
spec:
  replicas: 3  # 3 个副本
  selector:
    matchLabels:
      app: linkerd-gateway
  template:
    metadata:
      labels:
        app: linkerd-gateway
    spec:
      containers:
      - name: nginx
        image: nginx:latest
```

---

## 10. 最佳实践

### 10.1 生产部署

**资源规划**:

| 组件 | CPU | 内存 | 副本数 |
|-----|-----|------|--------|
| **Destination** | 100m | 100Mi | 3 |
| **Identity** | 100m | 100Mi | 3 |
| **Proxy Injector** | 100m | 100Mi | 3 |
| **Sidecar** | 20m | 20Mi | N (每 Pod) |

**控制平面配置**:

```yaml
apiVersion: install.linkerd.io/v1alpha1
kind: Linkerd
metadata:
  name: linkerd-control-plane
spec:
  global:
    highAvailability: true
    proxy:
      resources:
        requests:
          cpu: 20m
          memory: 20Mi
        limits:
          cpu: 1
          memory: 250Mi
```

---

### 10.2 安全加固

**禁用未授权的 Tap**:

```yaml
# 删除默认 ClusterRoleBinding
kubectl delete clusterrolebinding linkerd-linkerd-tap-auth-delegator

# 创建限制性 RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: linkerd-tap-admin
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: linkerd-linkerd-tap-admin
subjects:
- kind: User
  name: admin@example.com
```

**限制 Sidecar 权限**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    config.linkerd.io/skip-inbound-ports: "3306,6379"  # 跳过数据库端口
    config.linkerd.io/skip-outbound-ports: "443"       # 跳过 HTTPS 出站
```

---

### 10.3 升级策略

**升级步骤**:

```bash
# 1. 升级 CLI
curl --proto '=https' --tlsv1.2 -sSfL https://run.linkerd.io/install | sh

# 2. 检查兼容性
linkerd check --pre

# 3. 升级 CRD
linkerd upgrade --crds | kubectl apply -f -

# 4. 升级控制平面
linkerd upgrade | kubectl apply -f -

# 5. 验证升级
linkerd check

# 6. 滚动重启应用 (注入新版本 Sidecar)
kubectl rollout restart deployment -n default
```

---

### 10.4 部署检查清单

**安装前**:

- [ ] Kubernetes 版本 ≥ v1.21
- [ ] 集群资源充足 (2核4GB+)
- [ ] 网络策略允许 Pod 间通信
- [ ] 已备份现有证书 (如有)

**安装后**:

- [ ] `linkerd check` 全部通过
- [ ] `linkerd viz check` 全部通过
- [ ] mTLS 自动启用 (`linkerd viz edges`)
- [ ] 测试应用部署成功
- [ ] Grafana 仪表板正常显示

**生产环境**:

- [ ] 使用 HA 配置 (`--ha`)
- [ ] 配置 Sidecar 资源限制
- [ ] 配置 PodDisruptionBudget
- [ ] 集成外部 Prometheus/Grafana
- [ ] 配置告警规则
- [ ] 证书自动轮换 (cert-manager)

---

## 总结

**Linkerd 核心优势**:

- ✅ **轻量级**: 资源占用极低 (20-50MB/Pod)
- ✅ **简单易用**: 5 分钟快速上手
- ✅ **性能优秀**: Rust 代理,延迟 <1ms
- ✅ **自动 mTLS**: 零配置服务间加密

**适用场景**:

- 中小型 Kubernetes 集群
- 注重性能和稳定性
- 需要快速上手服务网格
- 简单微服务架构

**不适用场景**:

- 多集群/多云复杂架构 (考虑 Istio)
- 需要高级流量管理功能 (流量镜像/Egress 网关)
- 虚拟机混合部署

---

**相关文档**:

- [服务网格概述](01_服务网格概述.md)
- [Istio部署与配置](02_Istio部署与配置.md)
- [服务网格流量管理](04_服务网格流量管理.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**Linkerd 版本**: v2.14.x
