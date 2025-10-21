# Istio 部署与配置

> **返回**: [服务网格首页](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 文档元信息

| 属性 | 值 |
|------|-----|
| **文档版本** | v2.0 (2025改进版) |
| **更新日期** | 2025-10-21 |
| **Istio版本** | v1.20 (Latest), v1.19 |
| **Envoy版本** | v1.29 |
| **兼容版本** | Kubernetes v1.25+ |
| **标准对齐** | CNCF Istio, Envoy Proxy, Gateway API v1.0 |
| **状态** | 生产就绪 |

> **版本锚点**: 本文档严格对齐Istio v1.20与Ambient模式最新特性。

---

## 📋 目录

- [Istio 部署与配置](#istio-部署与配置)
  - [文档元信息](#文档元信息)
  - [📋 目录](#-目录)
  - [1. Istio 概述](#1-istio-概述)
  - [2. Istio 架构](#2-istio-架构)
    - [2.1 整体架构](#21-整体架构)
    - [2.2 核心组件](#22-核心组件)
      - [Istiod (控制平面)](#istiod-控制平面)
      - [Envoy Proxy (数据平面)](#envoy-proxy-数据平面)
  - [3. 安装部署](#3-安装部署)
    - [3.1 环境准备](#31-环境准备)
    - [3.2 istioctl 安装 (推荐)](#32-istioctl-安装-推荐)
      - [3.2.1 默认安装](#321-默认安装)
      - [3.2.2 生产安装](#322-生产安装)
    - [3.3 Helm 安装](#33-helm-安装)
    - [3.4 启用 Sidecar 自动注入](#34-启用-sidecar-自动注入)
    - [3.5 验证安装](#35-验证安装)
  - [4. 流量管理](#4-流量管理)
    - [4.1 核心资源](#41-核心资源)
    - [4.2 VirtualService (路由规则)](#42-virtualservice-路由规则)
      - [4.2.1 基础路由](#421-基础路由)
      - [4.2.2 金丝雀发布 (按权重)](#422-金丝雀发布-按权重)
      - [4.2.3 基于请求头路由](#423-基于请求头路由)
      - [4.2.4 超时与重试](#424-超时与重试)
      - [4.2.5 故障注入](#425-故障注入)
    - [4.3 DestinationRule (目标策略)](#43-destinationrule-目标策略)
      - [4.3.1 定义 Subset](#431-定义-subset)
      - [4.3.2 负载均衡策略](#432-负载均衡策略)
      - [4.3.3 熔断配置](#433-熔断配置)
    - [4.4 Gateway (入口网关)](#44-gateway-入口网关)
      - [4.4.1 HTTP Gateway](#441-http-gateway)
      - [4.4.2 HTTPS Gateway (TLS)](#442-https-gateway-tls)
    - [4.5 ServiceEntry (外部服务)](#45-serviceentry-外部服务)
  - [5. 安全](#5-安全)
    - [5.1 mTLS (双向 TLS)](#51-mtls-双向-tls)
      - [5.1.1 全局启用 mTLS](#511-全局启用-mtls)
      - [5.1.2 命名空间级别 mTLS](#512-命名空间级别-mtls)
      - [5.1.3 服务级别 mTLS](#513-服务级别-mtls)
    - [5.2 授权策略](#52-授权策略)
      - [5.2.1 默认拒绝策略](#521-默认拒绝策略)
      - [5.2.2 基于服务账户授权](#522-基于服务账户授权)
      - [5.2.3 基于 JWT 授权](#523-基于-jwt-授权)
  - [6. 可观测性](#6-可观测性)
    - [6.1 Prometheus 集成](#61-prometheus-集成)
    - [6.2 Grafana 仪表板](#62-grafana-仪表板)
    - [6.3 Jaeger 分布式追踪](#63-jaeger-分布式追踪)
    - [6.4 Kiali 拓扑可视化](#64-kiali-拓扑可视化)
  - [7. 故障排查](#7-故障排查)
    - [7.1 常见问题](#71-常见问题)
      - [7.1.1 Sidecar 未注入](#711-sidecar-未注入)
      - [7.1.2 流量路由不生效](#712-流量路由不生效)
      - [7.1.3 mTLS 连接失败](#713-mtls-连接失败)
    - [7.2 诊断命令](#72-诊断命令)
  - [8. 性能优化](#8-性能优化)
    - [8.1 Sidecar 资源限制](#81-sidecar-资源限制)
    - [8.2 减少指标基数](#82-减少指标基数)
  - [9. 最佳实践](#9-最佳实践)
    - [9.1 生产部署检查清单](#91-生产部署检查清单)
    - [9.2 版本升级](#92-版本升级)

---

## 1. Istio 概述

**Istio** 是目前最流行的开源服务网格平台，由 Google、IBM 和 Lyft 联合开发。

**核心特性**:

- ✅ 流量管理：智能路由、负载均衡、金丝雀发布
- ✅ 安全：mTLS、授权策略、证书管理
- ✅ 可观测性：指标、日志、分布式追踪
- ✅ 多集群：跨集群服务发现和流量管理

**版本信息**:

- 当前稳定版本：v1.20.0 (2024)
- 最低 Kubernetes 版本：v1.25+

---

## 2. Istio 架构

### 2.1 整体架构

```text
┌─────────────────────────────────────────────────────────────┐
│                    Istiod (Control Plane)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Pilot     │  │   Citadel    │  │   Galley     │       │
│  │  (流量管理)   │  │   (证书)     │  │  (配置)      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────┬────────────────────────────────────────────────┘
             │ (xDS API)
    ┌────────┴────────┬────────────┬────────────┐
    │                 │            │            │
┌───▼─────────┐  ┌────▼────────┐  ┌────▼────────┐  ┌──────────┐
│  Pod 1      │  │  Pod 2      │  │  Pod 3      │  │  Ingress │
│ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │  │  Gateway │
│ │   App   │ │  │ │   App   │ │  │ │   App   │ │  │          │
│ └────┬────┘ │  │ └────┬────┘ │  │ └────┬────┘ │  └──────────┘
│      │      │  │      │      │  │      │      │
│ ┌────▼────┐ │  │ ┌────▼────┐ │  │ ┌────▼────┐ │
│ │ Envoy   │◄┼──┼─┤ Envoy   │◄─┼──┼─┤ Envoy   │ │
│ │ Proxy   │ │  │ │ Proxy   │  │  │ │ Proxy   │ │
│ └─────────┘ │  │ └─────────┘  │  │ └─────────┘ │
└─────────────┘  └──────────────┘  └──────────────┘
```

### 2.2 核心组件

#### Istiod (控制平面)

**功能**:

- **Pilot**: 服务发现、流量管理
- **Citadel**: 证书签发和轮换
- **Galley**: 配置验证和分发

**资源要求**:

```yaml
resources:
  requests:
    cpu: 500m
    memory: 2Gi
  limits:
    cpu: 2
    memory: 4Gi
```

#### Envoy Proxy (数据平面)

**功能**:

- L7 代理
- 动态配置 (xDS API)
- 指标收集

**资源要求 (每 Pod)**:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 2
    memory: 1Gi
```

---

## 3. 安装部署

### 3.1 环境准备

**系统要求**:

- Kubernetes: v1.25+
- kubectl已配置
- 集群资源充足 (至少4核8GB可用)

**安装 istioctl**:

```bash
# 下载 Istio
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.20.0 sh -

# 进入目录
cd istio-1.20.0

# 添加到 PATH
export PATH=$PWD/bin:$PATH

# 验证
istioctl version
```

---

### 3.2 istioctl 安装 (推荐)

#### 3.2.1 默认安装

```bash
# 安装 demo 配置 (适合测试)
istioctl install --set profile=demo -y

# 验证安装
kubectl get pods -n istio-system

# 预期输出
NAME                                    READY   STATUS    RESTARTS   AGE
istiod-xxxxx                            1/1     Running   0          2m
istio-ingressgateway-xxxxx              1/1     Running   0          2m
istio-egressgateway-xxxxx               1/1     Running   0          2m
```

#### 3.2.2 生产安装

```bash
# 安装 minimal 配置 (生产推荐)
istioctl install --set profile=minimal -y

# 或自定义配置
istioctl install --set values.global.proxy.resources.requests.cpu=100m \
  --set values.global.proxy.resources.requests.memory=128Mi \
  --set values.pilot.resources.requests.cpu=500m \
  --set values.pilot.resources.requests.memory=2Gi -y
```

**配置文件 (IstioOperator)**:

```yaml
# istio-config.yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: istio-controlplane
spec:
  profile: default
  components:
    pilot:
      k8s:
        resources:
          requests:
            cpu: 500m
            memory: 2Gi
          limits:
            cpu: 2
            memory: 4Gi
    ingressGateways:
    - name: istio-ingressgateway
      enabled: true
      k8s:
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
        hpaSpec:
          minReplicas: 2
          maxReplicas: 5
  values:
    global:
      proxy:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 2
            memory: 1Gi
      tracer:
        zipkin:
          address: jaeger-collector.observability:9411
```

```bash
# 应用配置
istioctl install -f istio-config.yaml -y
```

---

### 3.3 Helm 安装

```bash
# 添加 Helm 仓库
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update

# 安装 Istio Base (CRD)
helm install istio-base istio/base -n istio-system --create-namespace

# 安装 Istiod
helm install istiod istio/istiod -n istio-system --wait

# 安装 Ingress Gateway
helm install istio-ingressgateway istio/gateway -n istio-system
```

---

### 3.4 启用 Sidecar 自动注入

**方法1: 命名空间级别 (推荐)**:

```bash
# 为命名空间打标签
kubectl label namespace default istio-injection=enabled

# 验证
kubectl get namespace -L istio-injection

# 部署测试应用
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml

# 检查 Sidecar 注入
kubectl get pods
# 每个 Pod 应有 2/2 容器 (App + Envoy)
```

**方法2: 手动注入**:

```bash
# 手动注入 Sidecar
istioctl kube-inject -f deployment.yaml | kubectl apply -f -

# 或使用文件
istioctl kube-inject -f deployment.yaml > deployment-injected.yaml
kubectl apply -f deployment-injected.yaml
```

---

### 3.5 验证安装

```bash
# 检查 Istiod 健康状态
istioctl verify-install

# 检查代理状态
istioctl proxy-status

# 查看配置同步
istioctl proxy-config cluster <pod-name>.<namespace>

# 部署示例应用
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml

# 获取 Ingress Gateway 地址
export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')
export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT

# 访问测试
curl http://$GATEWAY_URL/productpage
```

---

## 4. 流量管理

### 4.1 核心资源

| 资源 | 说明 |
|-----|------|
| **VirtualService** | 定义路由规则 (如何路由到哪个服务) |
| **DestinationRule** | 定义目标策略 (负载均衡、熔断、TLS) |
| **Gateway** | 入口/出口网关配置 |
| **ServiceEntry** | 注册外部服务 |

---

### 4.2 VirtualService (路由规则)

#### 4.2.1 基础路由

```yaml
# 将所有流量路由到 v1
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
```

#### 4.2.2 金丝雀发布 (按权重)

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 90  # 90% 流量
    - destination:
        host: reviews
        subset: v2
      weight: 10  # 10% 流量 (金丝雀)
```

#### 4.2.3 基于请求头路由

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        user:
          exact: "vip"
    route:
    - destination:
        host: reviews
        subset: v2  # VIP 用户访问 v2
  - route:
    - destination:
        host: reviews
        subset: v1  # 默认访问 v1
```

#### 4.2.4 超时与重试

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - timeout: 10s  # 请求超时 10 秒
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure
    route:
    - destination:
        host: reviews
        subset: v1
```

#### 4.2.5 故障注入

```yaml
# 注入延迟
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - fault:
      delay:
        percentage:
          value: 10  # 10% 请求延迟
        fixedDelay: 5s  # 延迟 5 秒
    route:
    - destination:
        host: reviews
---
# 注入错误
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - fault:
      abort:
        percentage:
          value: 10  # 10% 请求返回错误
        httpStatus: 500  # 返回 500 错误
    route:
    - destination:
        host: reviews
```

---

### 4.3 DestinationRule (目标策略)

#### 4.3.1 定义 Subset

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
  - name: v3
    labels:
      version: v3
```

#### 4.3.2 负载均衡策略

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  trafficPolicy:
    loadBalancer:
      simple: LEAST_REQUEST  # 最少请求数
    # 或一致性哈希
    # loadBalancer:
    #   consistentHash:
    #     httpHeaderName: "user-id"
```

#### 4.3.3 熔断配置

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100  # 最大连接数
      http:
        http1MaxPendingRequests: 10  # 最大挂起请求
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutive5xxErrors: 5  # 连续 5 次 5xx 错误
      interval: 30s
      baseEjectionTime: 30s    # 驱逐 30 秒
      maxEjectionPercent: 50   # 最多驱逐 50% 实例
      minHealthPercent: 10     # 最少保留 10% 健康实例
```

---

### 4.4 Gateway (入口网关)

#### 4.4.1 HTTP Gateway

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: bookinfo-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "bookinfo.example.com"
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: bookinfo
spec:
  hosts:
  - "bookinfo.example.com"
  gateways:
  - bookinfo-gateway
  http:
  - match:
    - uri:
        exact: /productpage
    route:
    - destination:
        host: productpage
        port:
          number: 9080
```

#### 4.4.2 HTTPS Gateway (TLS)

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: bookinfo-gateway-tls
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: bookinfo-credential  # Secret 名称
    hosts:
    - "bookinfo.example.com"
```

**创建 TLS Secret**:

```bash
kubectl create -n istio-system secret tls bookinfo-credential \
  --key=tls.key \
  --cert=tls.crt
```

---

### 4.5 ServiceEntry (外部服务)

```yaml
# 注册外部 HTTP 服务
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-api
spec:
  hosts:
  - api.external.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  location: MESH_EXTERNAL
  resolution: DNS
---
# 路由到外部服务
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: external-api
spec:
  hosts:
  - api.external.com
  http:
  - timeout: 10s
    route:
    - destination:
        host: api.external.com
```

---

## 5. 安全

### 5.1 mTLS (双向 TLS)

#### 5.1.1 全局启用 mTLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT  # 强制 mTLS
```

#### 5.1.2 命名空间级别 mTLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

#### 5.1.3 服务级别 mTLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: reviews
  namespace: default
spec:
  selector:
    matchLabels:
      app: reviews
  mtls:
    mode: STRICT
  portLevelMtls:
    9080:
      mode: PERMISSIVE  # 9080 端口允许非 mTLS
```

---

### 5.2 授权策略

#### 5.2.1 默认拒绝策略

```yaml
# 拒绝所有流量 (零信任起点)
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: default
spec:
  {}  # 空规则 = 拒绝所有
```

#### 5.2.2 基于服务账户授权

```yaml
# 仅允许 frontend 访问 backend
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: default
spec:
  selector:
    matchLabels:
      app: backend
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
```

#### 5.2.3 基于 JWT 授权

```yaml
# 要求 JWT 令牌
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: default
spec:
  selector:
    matchLabels:
      app: reviews
  jwtRules:
  - issuer: "https://accounts.google.com"
    jwksUri: "https://www.googleapis.com/oauth2/v3/certs"
---
# 授权策略
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: require-jwt
  namespace: default
spec:
  selector:
    matchLabels:
      app: reviews
  action: ALLOW
  rules:
  - from:
    - source:
        requestPrincipals: ["*"]  # 必须有有效 JWT
```

---

## 6. 可观测性

### 6.1 Prometheus 集成

**安装 Prometheus**:

```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/prometheus.yaml
```

**关键指标**:

```promql
# 请求总数
istio_requests_total

# 请求延迟
histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (le))

# 错误率
sum(rate(istio_requests_total{response_code=~"5.."}[5m])) 
/ 
sum(rate(istio_requests_total[5m]))
```

---

### 6.2 Grafana 仪表板

**安装 Grafana**:

```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/grafana.yaml

# 端口转发
kubectl -n istio-system port-forward svc/grafana 3000:3000

# 访问: http://localhost:3000
```

**内置仪表板**:

- Istio Mesh Dashboard
- Istio Service Dashboard
- Istio Workload Dashboard
- Istio Performance Dashboard

---

### 6.3 Jaeger 分布式追踪

**安装 Jaeger**:

```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/jaeger.yaml

# 端口转发
kubectl -n istio-system port-forward svc/jaeger-query 16686:16686

# 访问: http://localhost:16686
```

**配置采样率**:

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    defaultConfig:
      tracing:
        sampling: 100.0  # 100% 采样 (生产建议 1-10%)
        zipkin:
          address: jaeger-collector.istio-system:9411
```

---

### 6.4 Kiali 拓扑可视化

**安装 Kiali**:

```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/kiali.yaml

# 端口转发
kubectl -n istio-system port-forward svc/kiali 20001:20001

# 访问: http://localhost:20001
```

**功能**:

- 服务拓扑图
- 流量监控
- 配置验证
- 健康检查

---

## 7. 故障排查

### 7.1 常见问题

#### 7.1.1 Sidecar 未注入

**排查步骤**:

```bash
# 检查命名空间标签
kubectl get namespace default -o yaml | grep istio-injection

# 检查 Pod 注解
kubectl get pod <pod-name> -o jsonpath='{.metadata.annotations.sidecar\.istio\.io/inject}'

# 查看 Istiod 日志
kubectl logs -n istio-system deployment/istiod

# 手动注入测试
istioctl kube-inject -f deployment.yaml > deployment-injected.yaml
```

---

#### 7.1.2 流量路由不生效

**排查步骤**:

```bash
# 检查 VirtualService 配置
istioctl analyze

# 查看 Envoy 配置
istioctl proxy-config routes <pod-name>.<namespace>

# 查看 Pilot 日志
kubectl logs -n istio-system deployment/istiod -c discovery
```

---

#### 7.1.3 mTLS 连接失败

**排查步骤**:

```bash
# 检查 mTLS 状态
istioctl authn tls-check <pod-name>.<namespace>

# 查看证书
istioctl proxy-config secret <pod-name>.<namespace>

# 检查 PeerAuthentication
kubectl get peerauthentication -A
```

---

### 7.2 诊断命令

```bash
# 代理状态
istioctl proxy-status

# 分析配置
istioctl analyze -A

# 查看 Envoy 配置
istioctl proxy-config cluster <pod-name>.<namespace>
istioctl proxy-config listener <pod-name>.<namespace>
istioctl proxy-config route <pod-name>.<namespace>

# 查看日志
kubectl logs <pod-name> -c istio-proxy --tail=100

# 启用调试日志
istioctl proxy-config log <pod-name>.<namespace> --level debug
```

---

## 8. 性能优化

### 8.1 Sidecar 资源限制

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  values:
    global:
      proxy:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 2
            memory: 1Gi
```

### 8.2 减少指标基数

```yaml
meshConfig:
  defaultConfig:
    proxyStatsMatcher:
      inclusionPrefixes:
      - "cluster.outbound"
      - "cluster.inbound"
      inclusionRegexps:
      - ".*"
```

---

## 9. 最佳实践

### 9.1 生产部署检查清单

- [ ] 使用 `minimal` 或 `default` profile (避免 `demo`)
- [ ] 配置 Sidecar 资源限制
- [ ] 启用 HPA (Horizontal Pod Autoscaler)
- [ ] 配置 PodDisruptionBudget
- [ ] 启用 mTLS STRICT 模式
- [ ] 配置合理的追踪采样率 (1-10%)
- [ ] 部署多副本 Istiod (至少 2 个)
- [ ] 监控告警配置完成
- [ ] 测试故障注入和熔断

### 9.2 版本升级

**金丝雀升级**:

```bash
# 1. 安装新版本控制平面
istioctl install --set revision=1-20-0 -y

# 2. 更新命名空间标签
kubectl label namespace production istio.io/rev=1-20-0 --overwrite

# 3. 滚动重启 Pod
kubectl rollout restart deployment -n production

# 4. 验证新版本
istioctl proxy-status

# 5. 清理旧版本
istioctl uninstall --revision=1-19-0 -y
```

---

**相关文档**:

- [服务网格概述](01_服务网格概述.md)
- [Linkerd部署与配置](03_Linkerd部署与配置.md)
- [服务网格流量管理](04_服务网格流量管理.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**Istio 版本**: v1.20.0
