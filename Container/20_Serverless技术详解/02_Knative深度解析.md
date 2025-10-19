# 02 - Knative深度解析

**作者**: 云原生专家团队  
**创建日期**: 2025-10-19  
**最后更新**: 2025-10-19  
**版本**: v1.0

---

## 📋 本章导航

- [02 - Knative深度解析](#02---knative深度解析)
  - [📋 本章导航](#-本章导航)
  - [1. Knative概述](#1-knative概述)
    - [1.1 什么是Knative](#11-什么是knative)
    - [1.2 发展历史](#12-发展历史)
    - [1.3 核心组件](#13-核心组件)
    - [1.4 架构原理](#14-架构原理)
  - [2. Knative Serving](#2-knative-serving)
    - [2.1 核心概念](#21-核心概念)
    - [2.2 自动扩缩容](#22-自动扩缩容)
    - [2.3 流量管理](#23-流量管理)
    - [2.4 版本管理](#24-版本管理)
  - [3. Knative Eventing](#3-knative-eventing)
    - [3.1 事件驱动架构](#31-事件驱动架构)
    - [3.2 事件源](#32-事件源)
    - [3.3 事件代理](#33-事件代理)
    - [3.4 事件订阅](#34-事件订阅)
  - [4. Knative部署实践](#4-knative部署实践)
    - [4.1 环境准备](#41-环境准备)
    - [4.2 安装Knative Serving](#42-安装knative-serving)
    - [4.3 安装Knative Eventing](#43-安装knative-eventing)
    - [4.4 验证安装](#44-验证安装)
  - [5. 实战示例](#5-实战示例)
    - [5.1 Hello World服务](#51-hello-world服务)
    - [5.2 灰度发布](#52-灰度发布)
    - [5.3 事件驱动应用](#53-事件驱动应用)
    - [5.4 自动扩缩容演示](#54-自动扩缩容演示)
  - [6. 最佳实践](#6-最佳实践)
    - [6.1 性能优化](#61-性能优化)
    - [6.2 成本优化](#62-成本优化)
    - [6.3 安全加固](#63-安全加固)
    - [6.4 监控告警](#64-监控告警)
  - [7. 总结](#7-总结)

---

## 1. Knative概述

### 1.1 什么是Knative

**Knative** 是一个基于Kubernetes的开源Serverless平台，由Google、IBM、Red Hat等公司联合发起。

```yaml
Knative定位:
  - Kubernetes原生Serverless平台
  - CNCF孵化项目 (2024年3月进入)
  - 企业级生产就绪

核心价值:
  ✅ 简化Serverless开发
  ✅ 自动扩缩容 (0-N)
  ✅ 事件驱动架构
  ✅ 流量管理与灰度发布
  ✅ 避免厂商锁定
  ✅ 标准化 (CloudEvents)

适用场景:
  - 无服务器应用
  - 事件驱动架构
  - 微服务
  - API后端
  - 数据处理

优势:
  ✅ Kubernetes原生
  ✅ 强大灵活
  ✅ 企业级
  ✅ 开源免费
  ✅ 多云支持

劣势:
  ❌ 复杂度高 (需要K8s)
  ❌ 学习曲线陡
  ❌ 运维负担
```

---

### 1.2 发展历史

```yaml
Knative发展历程:

2018年7月:
  - Google I/O发布
  - 版本: v0.1.0
  - 初始组件: Serving + Build + Eventing

2019年:
  - Build组件分离 → Tekton
  - 专注于Serving + Eventing
  - v0.8.0: 稳定性提升

2020年:
  - v0.18.0: 性能优化
  - 冷启动优化
  - 企业采用增加

2021年:
  - v1.0.0发布 (Serving)
  - API稳定
  - 生产就绪

2022年:
  - Eventing成熟
  - CloudEvents 1.0支持
  - 多集群支持

2023年:
  - v1.10+
  - 性能持续优化
  - 边缘计算支持

2024年3月:
  - 加入CNCF (孵化项目)
  - 企业级采用广泛
  - 生态成熟

2025年:
  - v1.15+ (当前)
  - AI/ML工作负载优化
  - WebAssembly支持增强
```

---

### 1.3 核心组件

**Knative架构**:

```yaml
Knative核心组件:

1. Knative Serving:
   功能:
     - 无服务器容器运行
     - 自动扩缩容 (0-N)
     - 流量管理
     - 灰度发布
     - 版本管理
   
   核心资源:
     - Service: 服务定义
     - Route: 路由规则
     - Configuration: 配置
     - Revision: 版本快照

2. Knative Eventing:
   功能:
     - 事件驱动架构
     - 事件源管理
     - 事件路由
     - 事件订阅
   
   核心资源:
     - Source: 事件源
     - Broker: 事件代理
     - Trigger: 触发器
     - Channel: 事件通道
     - Subscription: 订阅

3. Knative Functions (可选):
   功能:
     - 函数开发框架
     - 多语言支持
     - 本地开发
     - 快速部署
   
   CLI:
     - func create
     - func deploy
     - func run
```

**架构图**:

```
┌────────────────────────────────────────────────────────────────┐
│                         Knative                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────┐      ┌─────────────────────┐        │
│  │  Knative Serving    │      │  Knative Eventing   │        │
│  ├─────────────────────┤      ├─────────────────────┤        │
│  │ - Service           │      │ - Source            │        │
│  │ - Route             │      │ - Broker            │        │
│  │ - Configuration     │      │ - Trigger           │        │
│  │ - Revision          │      │ - Channel           │        │
│  │ - Autoscaling       │      │ - Subscription      │        │
│  └─────────────────────┘      └─────────────────────┘        │
│           │                             │                     │
├───────────┼─────────────────────────────┼─────────────────────┤
│           ↓                             ↓                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Kubernetes (K8s)                          │  │
│  │  - Deployment  - Service  - HPA  - Ingress           │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

### 1.4 架构原理

**Knative Serving架构**:

```yaml
Serving组件:

Controller (控制器):
  - knative-serving-controller
  - 监听Service/Route/Configuration资源
  - 创建/更新Revision
  - 管理流量分配

Autoscaler (自动扩缩容器):
  - knative-serving-autoscaler
  - 监控并发数/请求数
  - 计算副本数
  - 扩缩容决策
  - 支持Scale to Zero

Activator (激活器):
  - knative-serving-activator
  - 接收冷启动请求
  - 唤醒Pod
  - 缓冲请求
  - 转发到Pod

Webhook (准入控制):
  - knative-serving-webhook
  - 资源验证
  - 默认值填充
  - CRD转换

数据流:
  用户请求
      ↓
  Ingress Gateway (Istio/Kourier/Contour)
      ↓
  Route (流量分配)
      ↓
  Revision (版本)
      ↓
  Pod (如果存在) → 处理请求
      或
  Activator (如果Scale to Zero) → 唤醒Pod → 转发请求
```

**Knative Eventing架构**:

```yaml
Eventing组件:

Controller (控制器):
  - knative-eventing-controller
  - 管理事件资源
  - 创建订阅关系

Webhook (准入控制):
  - knative-eventing-webhook
  - 资源验证

Broker (事件代理):
  - 接收事件
  - 路由到Trigger
  - 支持多后端 (MT-Channel-Broker/Kafka/RabbitMQ)

Channel (事件通道):
  - InMemoryChannel (内存)
  - KafkaChannel (Kafka)
  - NATSChannel (NATS)

Source (事件源):
  - PingSource (定时)
  - ApiServerSource (K8s API事件)
  - KafkaSource (Kafka)
  - 自定义Source

数据流:
  Event Source (事件源)
      ↓
  Broker (事件代理)
      ↓
  Trigger (触发器, 过滤)
      ↓
  Subscriber (订阅者, Knative Service)
```

---

## 2. Knative Serving

### 2.1 核心概念

**Service (服务)**:

```yaml
Knative Service:
  定义:
    - 最高层抽象
    - 包含Configuration + Route
    - 自动管理版本
  
  特点:
    - 声明式
    - 自动扩缩容
    - 流量管理
    - 版本快照

示例:
```

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: hello
  namespace: default
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "0"
        autoscaling.knative.dev/max-scale: "10"
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go
        ports:
        - containerPort: 8080
        env:
        - name: TARGET
          value: "World"
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "1000m"
            memory: "512Mi"
```

**Configuration (配置)**:

```yaml
Configuration:
  定义:
    - 定义Service的期望状态
    - 包含容器镜像、环境变量、资源限制
  
  特点:
    - 每次更新创建新Revision
    - 不可变
    - 版本化

示例:
```

```yaml
apiVersion: serving.knative.dev/v1
kind: Configuration
metadata:
  name: hello-config
spec:
  template:
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go:v1
        ports:
        - containerPort: 8080
```

**Revision (版本)**:

```yaml
Revision:
  定义:
    - Configuration的不可变快照
    - 每次Configuration更新自动创建
    - 代表应用的特定版本
  
  特点:
    - 不可变
    - 永久保留 (除非手动删除)
    - 可回滚
    - 可流量分割

命名:
  - hello-00001
  - hello-00002
  - hello-xyz12 (随机后缀)

查看:
  kubectl get revisions
  kubectl describe revision hello-00001
```

**Route (路由)**:

```yaml
Route:
  定义:
    - 管理流量分配
    - 将流量路由到不同Revision
    - 支持灰度发布
  
  特点:
    - 动态流量分割
    - 蓝绿部署
    - 金丝雀发布
    - 多版本共存

示例:
```

```yaml
apiVersion: serving.knative.dev/v1
kind: Route
metadata:
  name: hello-route
spec:
  traffic:
  - revisionName: hello-00001
    percent: 90
    tag: stable
  - revisionName: hello-00002
    percent: 10
    tag: canary
  - latestRevision: true
    percent: 0
    tag: latest
```

---

### 2.2 自动扩缩容

**扩缩容策略**:

```yaml
Knative Autoscaling:

指标:
  1. Concurrency (并发数):
     - 默认指标
     - 每Pod并发请求数
     - target: 100 (默认)
  
  2. RPS (请求数/秒):
     - 可选指标
     - 每秒请求数
     - target-utilization-percentage: 70%

算法:
  - KPA (Knative Pod Autoscaler, 默认)
  - HPA (Kubernetes Horizontal Pod Autoscaler)

公式 (KPA):
  desiredPods = ceil(
    当前并发数 / target并发数
  )

示例:
  当前并发: 500
  target: 100
  desiredPods = 500 / 100 = 5个Pod
```

**扩缩容配置**:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: autoscale-demo
spec:
  template:
    metadata:
      annotations:
        # 扩缩容类别
        autoscaling.knative.dev/class: "kpa.autoscaling.knative.dev"
        # 或使用HPA: "hpa.autoscaling.knative.dev"
        
        # 指标类型
        autoscaling.knative.dev/metric: "concurrency"
        # 或: "rps" (requests per second)
        
        # 目标值
        autoscaling.knative.dev/target: "50"
        # concurrency: 并发数, rps: 请求数
        
        # 利用率
        autoscaling.knative.dev/target-utilization-percentage: "70"
        # 仅用于RPS指标
        
        # 最小副本数
        autoscaling.knative.dev/min-scale: "0"
        # 0表示支持Scale to Zero
        
        # 最大副本数
        autoscaling.knative.dev/max-scale: "10"
        
        # 初始副本数
        autoscaling.knative.dev/initial-scale: "1"
        
        # Scale to Zero配置
        autoscaling.knative.dev/scale-to-zero-pod-retention-period: "10m"
        # Pod保留时间
        
        # 扩缩容窗口
        autoscaling.knative.dev/window: "60s"
        # 评估窗口
        
        # Panic模式 (快速扩容)
        autoscaling.knative.dev/panic-window-percentage: "10.0"
        autoscaling.knative.dev/panic-threshold-percentage: "200.0"
    spec:
      containers:
      - image: gcr.io/knative-samples/autoscale-go:latest
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "1000m"
            memory: "512Mi"
```

**Scale to Zero (零扩展)**:

```yaml
Scale to Zero机制:

触发条件:
  - 无请求流量
  - 空闲时间超过阈值 (默认60秒)

流程:
  1. 请求停止
  2. 等待retention period (10分钟默认)
  3. 缩容到0
  4. Pod删除

冷启动流程:
  1. 新请求到达
  2. Activator接收请求
  3. Activator通知Autoscaler
  4. 创建Pod (冷启动延迟)
  5. Pod就绪
  6. Activator转发请求到Pod
  7. 后续请求直达Pod (热启动)

配置:
```

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-autoscaler
  namespace: knative-serving
data:
  # 是否启用Scale to Zero
  enable-scale-to-zero: "true"
  
  # 缩容到0的宽限期
  scale-to-zero-grace-period: "30s"
  
  # Pod保留时间
  scale-to-zero-pod-retention-period: "0s"
  
  # Stable窗口 (稳定窗口)
  stable-window: "60s"
  
  # Panic窗口 (快速扩容窗口)
  panic-window-percentage: "10.0"
  
  # Panic阈值
  panic-threshold-percentage: "200.0"
```

**快速扩容 (Panic Mode)**:

```yaml
Panic Mode:
  触发:
    - 并发数超过target的2倍 (默认200%)
    - 在panic-window内 (6秒, 默认stable-window的10%)
  
  行为:
    - 快速扩容
    - 不等待stable-window
    - 立即增加副本
  
  目的:
    - 应对流量突增
    - 避免请求堆积
    - 提升用户体验

示例:
  target: 100
  panic-threshold: 200% → 200并发
  
  当前并发: 250
  触发Panic Mode
  立即扩容到 ceil(250 / 100) = 3个Pod
```

---

### 2.3 流量管理

**流量分割**:

```yaml
# 蓝绿部署 (Blue/Green Deployment)
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: blue-green-demo
spec:
  template:
    metadata:
      name: blue-green-demo-v2  # 新版本
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go:v2
  traffic:
  - revisionName: blue-green-demo-v1
    percent: 100
    tag: blue
  - revisionName: blue-green-demo-v2
    percent: 0
    tag: green
  # 切换流量: 将v1的100%改为0%, v2的0%改为100%

---
# 金丝雀发布 (Canary Release)
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: canary-demo
spec:
  template:
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go:v3
  traffic:
  - revisionName: canary-demo-v2
    percent: 90
    tag: stable
  - latestRevision: true  # v3
    percent: 10
    tag: canary

---
# A/B测试
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ab-test-demo
spec:
  template:
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go:latest
  traffic:
  - revisionName: ab-test-demo-v1
    percent: 50
    tag: version-a
  - revisionName: ab-test-demo-v2
    percent: 50
    tag: version-b
```

**流量标签 (Tag)**:

```yaml
流量标签作用:
  - 为Revision创建子域名
  - 独立访问特定版本
  - 不影响主流量分配

示例:
  Service: hello
  Tag: canary
  
  主域名:
    https://hello.default.example.com
    (按traffic.percent分配)
  
  标签域名:
    https://canary-hello.default.example.com
    (100%流量到canary标签的Revision)

配置:
```

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: hello-tags
spec:
  template:
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go:latest
  traffic:
  - latestRevision: false
    revisionName: hello-tags-v1
    percent: 80
    tag: stable
  - latestRevision: true
    percent: 20
    tag: canary
  - latestRevision: false
    revisionName: hello-tags-v1
    percent: 0
    tag: previous

# 访问方式:
# https://hello-tags.default.example.com       (80% v1, 20% latest)
# https://stable-hello-tags.default.example.com  (100% v1)
# https://canary-hello-tags.default.example.com  (100% latest)
# https://previous-hello-tags.default.example.com (100% v1, 仅测试)
```

---

### 2.4 版本管理

**Revision管理**:

```yaml
# 查看Revisions
kubectl get revisions

# 输出示例:
# NAME              SERVICE   READY   REASON
# hello-00001       hello     True    
# hello-00002       hello     True    
# hello-00003       hello     True    

# 查看详情
kubectl describe revision hello-00001

# 查看流量分配
kubectl get ksvc hello -o yaml | grep -A 10 traffic:

# 回滚到指定版本
kubectl patch ksvc hello -p '{"spec":{"traffic":[{"revisionName":"hello-00001","percent":100}]}}'

# 删除旧版本 (不在使用的)
kubectl delete revision hello-00001
```

**版本保留策略**:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-gc
  namespace: knative-serving
data:
  # 保留最近N个Revision
  retain-since-create-time: "48h"
  
  # 保留最近使用的N个Revision
  retain-since-last-active-time: "15h"
  
  # 最少保留N个Revision
  min-non-active-revisions: "2"
  
  # 最多保留N个Revision
  max-non-active-revisions: "1000"

# 手动清理
kubectl delete revision -l serving.knative.dev/service=hello \
  --field-selector=status.conditions[?(@.type=="Active")].status=False
```

---

## 3. Knative Eventing

### 3.1 事件驱动架构

**CloudEvents标准**:

```yaml
CloudEvents 1.0:
  定义:
    - CNCF标准
    - 统一事件格式
    - 跨平台互操作
  
  核心属性:
    - id: 事件唯一标识
    - source: 事件源
    - specversion: CloudEvents版本
    - type: 事件类型
    - datacontenttype: 数据格式
    - data: 事件数据

示例:
```

```json
{
  "specversion": "1.0",
  "id": "uuid-1234-5678",
  "source": "https://github.com/example/repo",
  "type": "com.github.pull_request.opened",
  "datacontenttype": "application/json",
  "time": "2025-10-19T12:00:00Z",
  "data": {
    "repository": "example/repo",
    "number": 123,
    "title": "Fix bug"
  }
}
```

**Eventing架构模式**:

```yaml
1. Source to Sink (简单模式):
   Event Source → Knative Service
   
   优点:
     - 简单直接
     - 低延迟
   
   缺点:
     - 紧耦合
     - 难以扩展

2. Broker/Trigger (推荐模式):
   Event Source → Broker → Trigger → Knative Service
   
   优点:
     - 解耦
     - 灵活过滤
     - 多订阅者
   
   缺点:
     - 略微增加延迟

3. Channel/Subscription:
   Event Source → Channel → Subscription → Knative Service
   
   优点:
     - 持久化
     - 支持多后端 (Kafka/NATS)
   
   缺点:
     - 配置复杂
```

---

### 3.2 事件源

**内置事件源**:

```yaml
# PingSource (定时事件)
apiVersion: sources.knative.dev/v1
kind: PingSource
metadata:
  name: ping-source
spec:
  schedule: "*/1 * * * *"  # Cron表达式, 每分钟
  contentType: "application/json"
  data: '{"message": "Hello from PingSource"}'
  sink:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: event-display

---
# ApiServerSource (K8s API事件)
apiVersion: sources.knative.dev/v1
kind: ApiServerSource
metadata:
  name: api-server-source
spec:
  serviceAccountName: api-server-source-sa
  mode: Resource
  resources:
  - apiVersion: v1
    kind: Pod
  - apiVersion: apps/v1
    kind: Deployment
  sink:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: event-display

---
# SinkBinding (容器绑定)
apiVersion: sources.knative.dev/v1
kind: SinkBinding
metadata:
  name: sink-binding
spec:
  subject:
    apiVersion: batch/v1
    kind: Job
    name: my-job
  sink:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: event-display

---
# ContainerSource (自定义容器)
apiVersion: sources.knative.dev/v1
kind: ContainerSource
metadata:
  name: container-source
spec:
  template:
    spec:
      containers:
      - image: gcr.io/knative-samples/event-source:latest
        env:
        - name: EVENT_TYPE
          value: "com.example.custom"
  sink:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: event-display
```

**第三方事件源**:

```yaml
# KafkaSource
apiVersion: sources.knative.dev/v1beta1
kind: KafkaSource
metadata:
  name: kafka-source
spec:
  consumerGroup: knative-group
  bootstrapServers:
  - kafka-broker:9092
  topics:
  - my-topic
  sink:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: event-display

---
# GitHubSource
apiVersion: sources.knative.dev/v1alpha1
kind: GitHubSource
metadata:
  name: github-source
spec:
  eventTypes:
  - pull_request
  - push
  ownerAndRepository: example/repo
  accessToken:
    secretKeyRef:
      name: github-secret
      key: token
  sink:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: github-event-handler
```

---

### 3.3 事件代理

**Broker (事件代理)**:

```yaml
# 创建Broker
apiVersion: eventing.knative.dev/v1
kind: Broker
metadata:
  name: default
  namespace: default
  annotations:
    eventing.knative.dev/broker.class: MTChannelBasedBroker
    # 或: Kafka, RabbitMQ
spec:
  config:
    apiVersion: v1
    kind: ConfigMap
    name: config-br-default-channel
    namespace: knative-eventing

---
# 简化创建 (使用默认Broker)
kubectl label namespace default knative-eventing-injection=enabled

# 查看Broker
kubectl get broker

# 输出:
# NAME      URL                                                   AGE   READY
# default   http://broker-ingress.knative-eventing.svc.cluster.local/default/default   1m    True
```

**发送事件到Broker**:

```bash
# 方法1: curl直接发送
curl -v "http://broker-ingress.knative-eventing.svc.cluster.local/default/default" \
  -X POST \
  -H "Ce-Id: 12345" \
  -H "Ce-Specversion: 1.0" \
  -H "Ce-Type: com.example.test" \
  -H "Ce-Source: curl-command" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Knative Eventing"}'

# 方法2: 从Pod内发送
kubectl run curl --image=curlimages/curl --rm -it --restart=Never -- \
  curl -X POST \
  -H "Ce-Id: 12345" \
  -H "Ce-Specversion: 1.0" \
  -H "Ce-Type: com.example.test" \
  -H "Ce-Source: test-pod" \
  -H "Content-Type: application/json" \
  -d '{"data":"test"}' \
  http://broker-ingress.knative-eventing.svc.cluster.local/default/default
```

---

### 3.4 事件订阅

**Trigger (触发器)**:

```yaml
# 基础Trigger (接收所有事件)
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: all-events-trigger
spec:
  broker: default
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: event-display

---
# 过滤Trigger (type过滤)
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: type-filter-trigger
spec:
  broker: default
  filter:
    attributes:
      type: com.github.pull_request.opened
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: pr-handler

---
# 多属性过滤
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: multi-filter-trigger
spec:
  broker: default
  filter:
    attributes:
      type: com.example.order
      source: https://example.com/api
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: order-processor

---
# Dead Letter Sink (死信队列)
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: dlq-trigger
spec:
  broker: default
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: order-processor
  delivery:
    deadLetterSink:
      ref:
        apiVersion: serving.knative.dev/v1
        kind: Service
        name: dlq-handler
    retry: 5
    backoffPolicy: exponential
    backoffDelay: "PT1S"  # ISO 8601: 1秒
```

**Channel (事件通道)**:

```yaml
# InMemoryChannel (内存通道)
apiVersion: messaging.knative.dev/v1
kind: InMemoryChannel
metadata:
  name: in-memory-channel
spec: {}

---
# KafkaChannel (Kafka通道)
apiVersion: messaging.knative.dev/v1beta1
kind: KafkaChannel
metadata:
  name: kafka-channel
spec:
  numPartitions: 3
  replicationFactor: 2

---
# Subscription (订阅)
apiVersion: messaging.knative.dev/v1
kind: Subscription
metadata:
  name: my-subscription
spec:
  channel:
    apiVersion: messaging.knative.dev/v1
    kind: InMemoryChannel
    name: in-memory-channel
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: event-consumer
  reply:
    ref:
      apiVersion: messaging.knative.dev/v1
      kind: InMemoryChannel
      name: reply-channel
```

---

## 4. Knative部署实践

### 4.1 环境准备

**前置条件**:

```bash
# Kubernetes集群
# - 版本: 1.28+
# - 节点: 2+ (建议)
# - CPU: 4+ cores
# - 内存: 8+ GB

# 方式1: Minikube
minikube start --cpus=4 --memory=8192 --kubernetes-version=v1.28.0

# 方式2: Kind
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
EOF

# 验证集群
kubectl cluster-info
kubectl get nodes
```

---

### 4.2 安装Knative Serving

**安装步骤**:

```bash
# 1. 安装Knative Serving CRDs
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.15.0/serving-crds.yaml

# 2. 安装Knative Serving Core
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.15.0/serving-core.yaml

# 3. 验证安装
kubectl get pods -n knative-serving

# 输出 (等待所有Pod Running):
# NAME                                     READY   STATUS    RESTARTS   AGE
# activator-xxx                            1/1     Running   0          1m
# autoscaler-xxx                           1/1     Running   0          1m
# controller-xxx                           1/1     Running   0          1m
# webhook-xxx                              1/1     Running   0          1m
```

**安装网络层**:

```yaml
选项:
  - Kourier (推荐, 轻量)
  - Istio (功能丰富)
  - Contour (企业级)
```

```bash
# 方式1: Kourier (推荐)
kubectl apply -f https://github.com/knative/net-kourier/releases/download/knative-v1.15.0/kourier.yaml

# 配置Kourier为默认网络层
kubectl patch configmap/config-network \
  --namespace knative-serving \
  --type merge \
  --patch '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'

# 获取Kourier External IP
kubectl get svc kourier -n kourier-system

# 配置DNS (用于本地测试)
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.15.0/serving-default-domain.yaml

# 或手动配置Magic DNS (sslip.io)
kubectl patch configmap/config-domain \
  --namespace knative-serving \
  --type merge \
  --patch '{"data":{"<External-IP>.sslip.io":""}}'
```

```bash
# 方式2: Istio
# 安装Istio
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.20.0 sh -
cd istio-1.20.0
./bin/istioctl install -y

# 安装Knative Istio Controller
kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.15.0/net-istio.yaml

# 验证
kubectl get pods -n istio-system
```

---

### 4.3 安装Knative Eventing

```bash
# 1. 安装Eventing CRDs
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.15.0/eventing-crds.yaml

# 2. 安装Eventing Core
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.15.0/eventing-core.yaml

# 3. 验证安装
kubectl get pods -n knative-eventing

# 输出:
# NAME                                  READY   STATUS    RESTARTS   AGE
# eventing-controller-xxx               1/1     Running   0          1m
# eventing-webhook-xxx                  1/1     Running   0          1m

# 4. 安装In-Memory Channel (默认)
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.15.0/in-memory-channel.yaml

# 5. 安装MT-Channel-Broker (默认Broker实现)
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.15.0/mt-channel-broker.yaml

# 6. (可选) 安装Kafka支持
kubectl apply -f https://github.com/knative-extensions/eventing-kafka-broker/releases/download/knative-v1.15.0/eventing-kafka-controller.yaml
kubectl apply -f https://github.com/knative-extensions/eventing-kafka-broker/releases/download/knative-v1.15.0/eventing-kafka-broker.yaml
```

---

### 4.4 验证安装

```bash
# 验证Serving
kubectl get pods -n knative-serving

# 验证Eventing
kubectl get pods -n knative-eventing

# 部署测试Service
kubectl apply -f - <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: hello
spec:
  template:
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go
        env:
        - name: TARGET
          value: "Knative"
EOF

# 等待就绪
kubectl wait ksvc hello --for=condition=Ready --timeout=300s

# 获取URL
kubectl get ksvc hello

# 输出:
# NAME    URL                                        LATESTCREATED   LATESTREADY     READY
# hello   http://hello.default.<External-IP>.sslip.io   hello-00001     hello-00001     True

# 测试访问
curl http://hello.default.<External-IP>.sslip.io

# 输出:
# Hello Knative!
```

---

## 5. 实战示例

### 5.1 Hello World服务

```bash
# 创建Hello World Service
kubectl apply -f - <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: hello-world
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "1"
        autoscaling.knative.dev/max-scale: "5"
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go
        ports:
        - containerPort: 8080
        env:
        - name: TARGET
          value: "World"
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
EOF

# 等待就绪
kubectl wait ksvc hello-world --for=condition=Ready

# 获取URL
export SERVICE_URL=$(kubectl get ksvc hello-world -o jsonpath='{.status.url}')
echo $SERVICE_URL

# 测试
curl $SERVICE_URL

# 输出:
# Hello World!
```

**Go语言Hello World源码**:

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "os"
)

func main() {
    target := os.Getenv("TARGET")
    if target == "" {
        target = "World"
    }

    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello %s!\n", target)
        log.Printf("Request received: %s %s", r.Method, r.URL.Path)
    })

    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    log.Printf("Server starting on port %s", port)
    log.Fatal(http.ListenAndServe(":"+port, nil))
}
```

---

### 5.2 灰度发布

```bash
# 步骤1: 部署v1版本
kubectl apply -f - <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: canary-demo
spec:
  template:
    metadata:
      name: canary-demo-v1
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go
        env:
        - name: TARGET
          value: "Version 1"
EOF

# 步骤2: 部署v2版本 (10%流量)
kubectl apply -f - <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: canary-demo
spec:
  template:
    metadata:
      name: canary-demo-v2
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go
        env:
        - name: TARGET
          value: "Version 2"
  traffic:
  - revisionName: canary-demo-v1
    percent: 90
    tag: stable
  - revisionName: canary-demo-v2
    percent: 10
    tag: canary
EOF

# 步骤3: 测试流量分配
for i in {1..100}; do
  curl -s $(kubectl get ksvc canary-demo -o jsonpath='{.status.url}')
done | sort | uniq -c

# 输出 (约90/10分布):
#   90 Hello Version 1!
#   10 Hello Version 2!

# 步骤4: 逐步增加v2流量
kubectl apply -f - <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: canary-demo
spec:
  template:
    metadata:
      name: canary-demo-v2
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go
        env:
        - name: TARGET
          value: "Version 2"
  traffic:
  - revisionName: canary-demo-v1
    percent: 50
  - revisionName: canary-demo-v2
    percent: 50
EOF

# 步骤5: 完全切换到v2
kubectl apply -f - <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: canary-demo
spec:
  template:
    metadata:
      name: canary-demo-v2
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go
        env:
        - name: TARGET
          value: "Version 2"
  traffic:
  - latestRevision: true
    percent: 100
EOF
```

---

### 5.3 事件驱动应用

```bash
# 步骤1: 创建事件显示Service
kubectl apply -f - <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: event-display
spec:
  template:
    spec:
      containers:
      - image: gcr.io/knative-releases/knative.dev/eventing/cmd/event_display
EOF

# 步骤2: 创建Broker
kubectl label namespace default knative-eventing-injection=enabled

# 验证Broker
kubectl get broker

# 步骤3: 创建PingSource (定时事件)
kubectl apply -f - <<EOF
apiVersion: sources.knative.dev/v1
kind: PingSource
metadata:
  name: ping-source-demo
spec:
  schedule: "*/1 * * * *"  # 每分钟
  contentType: "application/json"
  data: '{"message": "Ping at minute boundary"}'
  sink:
    ref:
      apiVersion: eventing.knative.dev/v1
      kind: Broker
      name: default
EOF

# 步骤4: 创建Trigger
kubectl apply -f - <<EOF
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: ping-trigger
spec:
  broker: default
  filter:
    attributes:
      type: dev.knative.sources.ping
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: event-display
EOF

# 步骤5: 查看事件
kubectl logs -l serving.knative.dev/service=event-display -c user-container --tail=50 -f

# 输出 (每分钟):
# ☁️  cloudevents.Event
# Context Attributes,
#   specversion: 1.0
#   type: dev.knative.sources.ping
#   source: /apis/v1/namespaces/default/pingsources/ping-source-demo
#   id: xxx
#   time: 2025-10-19T12:00:00Z
#   datacontenttype: application/json
# Data,
#   {
#     "message": "Ping at minute boundary"
#   }
```

---

### 5.4 自动扩缩容演示

```bash
# 部署自动扩缩容示例
kubectl apply -f - <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: autoscale-demo
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "0"
        autoscaling.knative.dev/max-scale: "10"
        autoscaling.knative.dev/target: "10"  # 每Pod 10个并发
    spec:
      containers:
      - image: gcr.io/knative-samples/autoscale-go
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
EOF

# 获取URL
export SERVICE_URL=$(kubectl get ksvc autoscale-demo -o jsonpath='{.status.url}')

# 观察Pod数量
watch kubectl get pods -l serving.knative.dev/service=autoscale-demo

# 终端2: 生成负载
hey -z 60s -c 50 $SERVICE_URL
# -z 60s: 持续60秒
# -c 50: 50个并发

# 观察扩容:
# 初始: 0个Pod (Scale to Zero)
# 5秒: 1个Pod (冷启动)
# 10秒: 5个Pod (扩容)
# 20秒: 10个Pod (达到max-scale)
# 负载停止后: 逐步缩容
# 10分钟后: 0个Pod (Scale to Zero)
```

**负载生成脚本**:

```bash
#!/bin/bash
# autoscale-test.sh

SERVICE_URL=$1
DURATION=${2:-60}
CONCURRENCY=${3:-50}

echo "Target: $SERVICE_URL"
echo "Duration: ${DURATION}s"
echo "Concurrency: $CONCURRENCY"

# 安装hey (如果未安装)
if ! command -v hey &> /dev/null; then
    echo "Installing hey..."
    go install github.com/rakyll/hey@latest
fi

# 生成负载
hey -z ${DURATION}s -c $CONCURRENCY $SERVICE_URL

# 使用:
# chmod +x autoscale-test.sh
# ./autoscale-test.sh http://autoscale-demo.default.example.com 60 50
```

---

## 6. 最佳实践

### 6.1 性能优化

```yaml
1. 资源配置优化:
   requests:
     cpu: "100m"    # 最小CPU
     memory: "128Mi"  # 最小内存
   limits:
     cpu: "1000m"   # 最大CPU (影响扩缩容)
     memory: "512Mi"  # 最大内存

2. 扩缩容参数调优:
   autoscaling.knative.dev/target: "100"
   # 根据应用调整:
   # - 计算密集型: 50-100
   # - I/O密集型: 100-200
   # - 简单API: 200-500

3. 冷启动优化:
   - 镜像优化 (多阶段构建)
   - 使用轻量基础镜像 (alpine/distroless)
   - 预热: min-scale: "1"

4. 预留实例 (关键服务):
   autoscaling.knative.dev/min-scale: "2"
   # 避免冷启动
   # 提升可用性

5. 容器优化:
   - 减少镜像大小
   - 优化启动时间
   - 使用健康检查
```

**镜像优化示例**:

```dockerfile
# 多阶段构建 (Go示例)
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
CMD ["./main"]

# 结果: 镜像从800MB → 15MB
```

---

### 6.2 成本优化

```yaml
1. Scale to Zero (低流量服务):
   autoscaling.knative.dev/min-scale: "0"
   # 空闲时0成本

2. 合理设置max-scale:
   autoscaling.knative.dev/max-scale: "10"
   # 防止资源爆炸
   # 结合QPS预估

3. 资源请求优化:
   requests:
     cpu: "50m"     # 最小化请求
     memory: "64Mi"
   # 提升节点利用率

4. 使用Spot实例 (公有云):
   nodeSelector:
     kubernetes.io/lifecycle: spot
   # 成本降低70%

5. 定期清理旧Revision:
   kubectl delete revision -l serving.knative.dev/service=xxx \
     --field-selector=status.conditions[?(@.type=="Active")].status=False
```

---

### 6.3 安全加固

```yaml
# 1. 使用非root用户
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: secure-service
spec:
  template:
    spec:
      containers:
      - image: myapp:latest
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true

---
# 2. 网络策略 (限制流量)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: knative-service-policy
spec:
  podSelector:
    matchLabels:
      serving.knative.dev/service: secure-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          knative.dev/ingress: "true"
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443

---
# 3. Secret管理
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: secret-demo
spec:
  template:
    spec:
      containers:
      - image: myapp:latest
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secret
              key: key

---
# 4. RBAC权限控制
apiVersion: v1
kind: ServiceAccount
metadata:
  name: knative-app-sa

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: knative-app-role
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: knative-app-rolebinding
subjects:
- kind: ServiceAccount
  name: knative-app-sa
roleRef:
  kind: Role
  name: knative-app-role
  apiGroup: rbac.authorization.k8s.io
```

---

### 6.4 监控告警

```yaml
# 1. Prometheus监控 (Knative内置)
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.15.0/monitoring-metrics-prometheus.yaml

# 核心指标:
# - autoscaler_actual_pods: 实际Pod数
# - autoscaler_desired_pods: 期望Pod数
# - revision_request_count: 请求总数
# - revision_request_latencies: 请求延迟
# - activator_request_concurrency: Activator并发数

---
# 2. Grafana Dashboard
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.15.0/monitoring-logs-elasticsearch.yaml

# 导入Dashboard:
# - Knative Serving - Revision
# - Knative Serving - Autoscaler
# - Knative Eventing

---
# 3. 告警规则 (PrometheusRule)
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: knative-alerts
spec:
  groups:
  - name: knative_serving
    rules:
    - alert: KnativeServiceDown
      expr: |
        kn_service_ready{} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Knative Service {{ $labels.service }} is down"
    
    - alert: KnativeHighLatency
      expr: |
        histogram_quantile(0.99, revision_request_latencies_bucket) > 1000
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High latency on {{ $labels.service }}"
    
    - alert: KnativeScalingIssue
      expr: |
        abs(autoscaler_actual_pods - autoscaler_desired_pods) > 2
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "Scaling issue on {{ $labels.service }}"
```

---

## 7. 总结

```yaml
本章要点:
  ✅ Knative概述 (定义/历史/架构)
  ✅ Knative Serving (Service/扩缩容/流量管理)
  ✅ Knative Eventing (事件驱动/Source/Broker/Trigger)
  ✅ 完整部署实践 (安装/验证)
  ✅ 实战示例 (Hello World/灰度/事件/扩缩容)
  ✅ 最佳实践 (性能/成本/安全/监控)

Knative核心价值:
  - Kubernetes原生Serverless
  - 自动扩缩容 (0-N)
  - 事件驱动架构
  - 流量管理强大
  - 避免厂商锁定

适用场景:
  ✅ 企业级Serverless
  ✅ 事件驱动应用
  ✅ 微服务架构
  ✅ API后端
  ✅ 数据处理
  ✅ 混合云/多云

关键特性:
  ⭐ Scale to Zero
  ⭐ 流量分割 (蓝绿/金丝雀)
  ⭐ CloudEvents标准
  ⭐ 灵活扩展
  ⭐ 生产就绪

技术对比:
  vs AWS Lambda: 无厂商锁定
  vs OpenFaaS: 功能更丰富
  vs Fission: 生态更成熟
```

---

**下一章预告**:

**03 - OpenFaaS实战**:

- OpenFaaS架构与特点
- 快速部署与开发
- 多语言函数开发
- CI/CD集成
- 监控与日志

---

**完成日期**: 2025-10-19  
**版本**: v1.0  
**作者**: 云原生专家团队

**Tags**: `#Knative` `#Serving` `#Eventing` `#Serverless` `#Kubernetes`

