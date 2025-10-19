# KubeEdge技术详解

## 📋 目录

- [KubeEdge技术详解](#kubeedge技术详解)
  - [📋 目录](#-目录)
  - [项目概述](#项目概述)
    - [KubeEdge简介](#kubeedge简介)
    - [核心优势](#核心优势)
    - [版本历史](#版本历史)
  - [核心架构](#核心架构)
    - [整体架构](#整体架构)
    - [组件说明](#组件说明)
    - [数据流](#数据流)
  - [CloudCore详解](#cloudcore详解)
    - [安装CloudCore](#安装cloudcore)
      - [前置条件](#前置条件)
      - [使用Keadm安装](#使用keadm安装)
      - [使用Helm安装](#使用helm安装)
    - [CloudCore配置](#cloudcore配置)
    - [CloudCore组件详解](#cloudcore组件详解)
      - [EdgeController](#edgecontroller)
      - [DeviceController](#devicecontroller)
      - [CloudHub](#cloudhub)
  - [EdgeCore详解](#edgecore详解)
    - [安装EdgeCore](#安装edgecore)
      - [使用Keadm安装](#使用keadm安装-1)
      - [高级安装选项](#高级安装选项)
    - [EdgeCore配置](#edgecore配置)
    - [EdgeCore组件详解](#edgecore组件详解)
      - [Edged（轻量级Kubelet）](#edged轻量级kubelet)
      - [EdgeHub（云边通信）](#edgehub云边通信)
      - [EventBus（MQTT总线）](#eventbusmqtt总线)
      - [DeviceTwin（设备孪生）](#devicetwin设备孪生)
  - [设备管理](#设备管理)
    - [设备接入](#设备接入)
      - [Modbus设备接入](#modbus设备接入)
      - [MQTT设备接入](#mqtt设备接入)
    - [自定义Mapper开发](#自定义mapper开发)
  - [应用部署](#应用部署)
    - [在边缘部署应用](#在边缘部署应用)
      - [基础应用部署](#基础应用部署)
      - [边缘应用组（NodeGroup）](#边缘应用组nodegroup)
    - [配置管理](#配置管理)
      - [ConfigMap和Secret](#configmap和secret)
    - [边缘存储](#边缘存储)
      - [Local Path Provisioner](#local-path-provisioner)
  - [云边协同](#云边协同)
    - [云边消息流](#云边消息流)
    - [云边通道类型](#云边通道类型)
      - [WebSocket (默认)](#websocket-默认)
      - [QUIC (推荐)](#quic-推荐)
    - [云边协同示例](#云边协同示例)
      - [动态配置更新](#动态配置更新)
  - [边缘自治](#边缘自治)
    - [离线能力](#离线能力)
    - [本地数据持久化](#本地数据持久化)
    - [边缘缓存策略](#边缘缓存策略)
  - [生产部署](#生产部署)
    - [高可用部署](#高可用部署)
      - [CloudCore高可用](#cloudcore高可用)
      - [边缘节点冗余](#边缘节点冗余)
    - [安全加固](#安全加固)
      - [TLS证书管理](#tls证书管理)
      - [RBAC权限控制](#rbac权限控制)
    - [性能优化](#性能优化)
  - [监控运维](#监控运维)
    - [Prometheus监控](#prometheus监控)
    - [日志收集](#日志收集)
  - [最佳实践](#最佳实践)
    - [1. 镜像管理](#1-镜像管理)
    - [2. 资源规划](#2-资源规划)
    - [3. 网络优化](#3-网络优化)
  - [参考资料](#参考资料)
    - [官方文档](#官方文档)
    - [技术文章](#技术文章)
    - [视频教程](#视频教程)

---

## 项目概述

### KubeEdge简介

**KubeEdge** 是华为开源的云原生边缘计算框架，旨在将容器化应用编排能力扩展到边缘侧。2019年加入CNCF，2022年晋升为CNCF孵化项目。

**核心特性**:

```yaml
技术定位:
  - Kubernetes原生: 100%兼容K8s API
  - 云边协同: 可靠的消息传递
  - 边缘自治: 离线运行能力
  - 设备管理: 内置设备孪生

项目信息:
  - 开源时间: 2018年11月
  - CNCF状态: 孵化项目 (Incubating)
  - 最新版本: v1.18.0 (2024年10月)
  - GitHub: github.com/kubeedge/kubeedge
  - Stars: 6.8K+ (2024年)
  - 贡献者: 500+

支持环境:
  - Kubernetes: 1.21+
  - 操作系统: Linux (x86_64, ARM64)
  - 容器运行时: Docker, containerd, CRI-O
  - 设备协议: MQTT, Modbus, OPC-UA, Bluetooth
```

### 核心优势

**1. Kubernetes原生**:

```yaml
完全兼容:
  - 使用标准K8s API
  - 支持kubectl命令
  - 兼容Helm charts
  - 无需学习新的API

优势:
  - 降低学习成本
  - 复用K8s生态
  - 平滑迁移应用
  - 统一管理体验
```

**2. 云边可靠协同**:

```text
┌─────────────────────────────────────┐
│          Cloud (K8s)                │
│  ┌──────────────────────────────┐   │
│  │  CloudCore                   │   │
│  │  - 云边消息路由              │   │
│  │  - 设备控制器                │   │
│  │  - 边缘节点管理              │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │ WebSocket/QUIC
               │ (可靠传输)
               ↓
┌─────────────────────────────────────┐
│          Edge Nodes                 │
│  ┌──────────────────────────────┐   │
│  │  EdgeCore                    │   │
│  │  - 本地数据缓存              │   │
│  │  - 离线自治                  │   │
│  │  - 设备管理                  │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

**3. 边缘自治**:

```yaml
离线能力:
  - 断网期间: 
    - Pod继续运行
    - 本地数据缓存生效
    - 设备管理正常
  
  - 重连后:
    - 自动同步状态
    - 增量更新
    - 无需手动干预

价值:
  - 高可用性: 不依赖云端连接
  - 低延迟: 本地处理
  - 节省带宽: 减少云边通信
```

**4. 设备管理**:

```yaml
设备支持:
  - 类型: 传感器、执行器、工业设备
  - 数量: 10K+ 设备/边缘节点
  - 协议: MQTT, Modbus, OPC-UA, 自定义

设备孪生:
  - 云端: 期望状态 (Desired State)
  - 边缘: 实际状态 (Reported State)
  - 自动同步: 双向更新

管理功能:
  - 设备注册
  - 属性上报
  - 命令下发
  - 状态监控
```

### 版本历史

| 版本 | 发布时间 | 主要特性 |
|------|---------|---------|
| **v1.18** | 2024-10 | Kubernetes 1.28支持、DMI v2改进 |
| **v1.17** | 2024-06 | 边缘应用自动扩缩容、增强安全 |
| **v1.16** | 2024-03 | Keadm安装优化、边缘Pod性能提升 |
| **v1.15** | 2023-12 | 支持Kubernetes 1.27、EdgeMesh 1.14 |
| **v1.14** | 2023-09 | 设备管理v2 API、云边消息优化 |
| **v1.13** | 2023-06 | 边缘节点组、MQTT 5.0支持 |
| **v1.12** | 2023-03 | QUIC协议、边缘存储增强 |

---

## 核心架构

### 整体架构

```text
┌───────────────────────────────────────────────────────────┐
│                    Cloud (Kubernetes)                      │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Kubernetes Master                                  │  │
│  │  - API Server                                       │  │
│  │  - Scheduler                                        │  │
│  │  - Controller Manager                               │  │
│  └─────────────────────────────────────────────────────┘  │
│                             ↓                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  CloudCore (KubeEdge Cloud Component)              │  │
│  │  ┌──────────────┐ ┌────────────┐ ┌──────────────┐ │  │
│  │  │EdgeController│ │DeviceCtrl  │ │   CloudHub   │ │  │
│  │  │(节点管理)     │ │(设备管理)  │ │(云边通信)    │ │  │
│  │  └──────────────┘ └────────────┘ └──────────────┘ │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────────────┬────────────────────────────────┘
                           │ WebSocket/QUIC/HTTPS
                           │ (Cloud-Edge Channel)
                           ↓
┌───────────────────────────────────────────────────────────┐
│                    Edge Nodes                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  EdgeCore (KubeEdge Edge Component)                │  │
│  │  ┌──────┐ ┌────────┐ ┌────────┐ ┌──────────────┐  │  │
│  │  │Edged │ │EdgeHub │ │EventBus│ │DeviceTwin    │  │  │
│  │  │(轻量 │ │(云边   │ │(MQTT   │ │(设备状态)    │  │  │
│  │  │Kubelet│ │消息)   │ │总线)   │ │              │  │  │
│  │  └──────┘ └────────┘ └────────┘ └──────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐│  │
│  │  │  MetaManager (本地元数据管理)                  ││  │
│  │  └────────────────────────────────────────────────┘│  │
│  └─────────────────────────────────────────────────────┘  │
│                             ↓                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Container Runtime (containerd/docker)              │  │
│  └─────────────────────────────────────────────────────┘  │
│                             ↓                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Mapper (设备驱动)                                  │  │
│  │  - MQTT Mapper                                      │  │
│  │  - Modbus Mapper                                    │  │
│  │  - OPC-UA Mapper                                    │  │
│  └─────────────────────────────────────────────────────┘  │
│                             ↓                              │
│  [IoT Devices] [Sensors] [Actuators] [Industrial Devices] │
└───────────────────────────────────────────────────────────┘
```

### 组件说明

**云端组件 (CloudCore)**:

| 组件 | 功能 | 端口 |
|------|------|------|
| **EdgeController** | 管理边缘节点、同步资源 | - |
| **DeviceController** | 管理设备、同步设备孪生 | - |
| **CloudHub** | 云边消息路由、协议转换 | 10000 (WebSocket)<br/>10001 (QUIC)<br/>10002 (HTTPS) |
| **DynamicController** | 动态配置管理 | - |
| **SyncController** | 云边状态同步 | - |

**边缘组件 (EdgeCore)**:

| 组件 | 功能 | 说明 |
|------|------|------|
| **Edged** | 轻量级Kubelet | Pod生命周期管理 |
| **EdgeHub** | 云边通信客户端 | 消息同步、断线重连 |
| **EventBus** | MQTT消息总线 | 设备事件路由 |
| **DeviceTwin** | 设备孪生 | 期望状态与实际状态同步 |
| **MetaManager** | 元数据管理 | 本地数据库、缓存 |
| **ServiceBus** | REST接口 | 应用访问设备 |
| **EdgeMesh** | 边缘服务网格 | 跨边缘通信、流量管理 |

### 数据流

**1. 应用下发流程**:

```text
1. kubectl apply -f deployment.yaml
   ↓
2. K8s API Server 接收请求
   ↓
3. EdgeController 监听到新的Deployment
   ↓
4. CloudHub 通过WebSocket/QUIC发送到边缘
   ↓
5. EdgeHub 接收消息
   ↓
6. MetaManager 更新本地数据库
   ↓
7. Edged 创建Pod
   ↓
8. Container Runtime 启动容器
   ↓
9. 状态回传: EdgeHub → CloudHub → K8s API Server
```

**2. 设备数据上报流程**:

```text
1. IoT设备通过MQTT/Modbus上报数据
   ↓
2. Mapper接收设备数据
   ↓
3. EventBus路由消息
   ↓
4. DeviceTwin更新实际状态(Reported)
   ↓
5. EdgeHub上报到CloudHub
   ↓
6. DeviceController更新云端设备孪生
   ↓
7. 应用可通过K8s API查询设备状态
```

---

## CloudCore详解

### 安装CloudCore

#### 前置条件

```yaml
环境要求:
  Kubernetes:
    版本: 1.21+
    组件: API Server, Controller Manager
  
  网络:
    云端IP: 可被边缘节点访问
    端口: 10000-10002需开放
  
  资源:
    CPU: 2核+
    内存: 2GB+
    磁盘: 10GB+
```

#### 使用Keadm安装

```bash
# 1. 下载keadm工具
wget https://github.com/kubeedge/kubeedge/releases/download/v1.18.0/keadm-v1.18.0-linux-amd64.tar.gz
tar -xvf keadm-v1.18.0-linux-amd64.tar.gz
chmod +x keadm && mv keadm /usr/local/bin/

# 2. 安装CloudCore
keadm init \
  --advertise-address="<CLOUD_IP>" \
  --kubeedge-version=v1.18.0 \
  --kube-config=/root/.kube/config

# 3. 验证安装
kubectl get pods -n kubeedge
# 应该看到cloudcore pod在运行

# 4. 获取token（用于边缘节点加入）
keadm gettoken

# 5. 查看CloudCore日志
kubectl logs -n kubeedge cloudcore-xxxxx -f
```

#### 使用Helm安装

```bash
# 1. 添加KubeEdge Helm仓库
helm repo add kubeedge https://raw.githubusercontent.com/kubeedge/kubeedge/master/build/helm
helm repo update

# 2. 创建命名空间
kubectl create namespace kubeedge

# 3. 安装CloudCore
helm install cloudcore kubeedge/cloudcore \
  --namespace kubeedge \
  --set cloudCore.cloudHub.advertiseAddress="{<CLOUD_IP>}" \
  --set cloudCore.cloudHub.nodeLimit=1000 \
  --set cloudCore.modules.cloudStream.enable=true

# 4. 验证安装
helm status cloudcore -n kubeedge
kubectl get all -n kubeedge
```

### CloudCore配置

**完整配置示例** (`cloudcore.yaml`):

```yaml
apiVersion: cloudcore.config.kubeedge.io/v1alpha1
kind: CloudCore
kubeAPIConfig:
  kubeConfig: /root/.kube/config
  master: ""
  qps: 100
  burst: 200
modules:
  cloudHub:
    advertiseAddress:
    - <CLOUD_IP>
    nodeLimit: 1000
    tlsCAFile: /etc/kubeedge/ca/rootCA.crt
    tlsCertFile: /etc/kubeedge/certs/server.crt
    tlsPrivateKeyFile: /etc/kubeedge/certs/server.key
    # WebSocket配置
    websocket:
      enable: true
      port: 10000
      maxConnections: 1000
    # QUIC配置 (更低延迟)
    quic:
      enable: true
      port: 10001
      maxIncomingStreams: 10000
    # HTTPS配置
    https:
      enable: true
      port: 10002
  
  cloudStream:
    enable: true
    tlsTunnelCAFile: /etc/kubeedge/ca/rootCA.crt
    tlsTunnelCertFile: /etc/kubeedge/certs/server.crt
    tlsTunnelPrivateKeyFile: /etc/kubeedge/certs/server.key
    tunnelPort: 10004
  
  dynamicController:
    enable: true
  
  router:
    enable: false
    restTimeout: 60
    port: 9443
```

### CloudCore组件详解

#### EdgeController

**功能**: 管理边缘节点、同步K8s资源到边缘

**工作原理**:

```text
┌─────────────────────────────────────┐
│     Kubernetes API Server           │
└──────────────┬──────────────────────┘
               │ Watch
               ↓
┌─────────────────────────────────────┐
│     EdgeController                  │
│  ┌─────────────────────────────┐    │
│  │  Downstream Controller      │    │
│  │  - Watch K8s资源            │    │
│  │  - 过滤属于边缘节点的资源   │    │
│  │  - 转换为边缘消息           │    │
│  └─────────────────────────────┘    │
│               ↓                      │
│  ┌─────────────────────────────┐    │
│  │  Upstream Controller        │    │
│  │  - 接收边缘上报             │    │
│  │  - 更新K8s资源状态          │    │
│  └─────────────────────────────┘    │
└──────────────┬──────────────────────┘
               ↓
          CloudHub → 边缘
```

**同步的资源类型**:

- Pod
- ConfigMap
- Secret
- Service
- Endpoints
- PersistentVolume
- PersistentVolumeClaim
- Node

#### DeviceController

**功能**: 管理设备孪生、同步设备状态

**设备CRD定义**:

```yaml
apiVersion: devices.kubeedge.io/v1beta1
kind: Device
metadata:
  name: temperature-sensor-01
  namespace: default
spec:
  deviceModelRef:
    name: temperature-model
  protocol:
    modbus:
      slaveID: 1
    common:
      com:
        serialPort: /dev/ttyUSB0
        baudRate: 115200
        dataBits: 8
        parity: even
        stopBits: 1
  nodeSelector:
    nodeSelectorTerms:
    - matchExpressions:
      - key: kubernetes.io/hostname
        operator: In
        values:
        - edge-node-1
  propertyVisitors:
  - propertyName: temperature
    modbus:
      register: holding
      offset: 2
      limit: 1
      scale: 0.01
      isSwap: false
    collectCycle: 5000  # ms
    reportCycle: 10000  # ms
status:
  twins:
  - propertyName: temperature
    desired:
      value: ""
      metadata:
        timestamp: "2024-10-19T10:00:00Z"
    reported:
      value: "25.6"
      metadata:
        timestamp: "2024-10-19T10:00:05Z"
```

**DeviceModel定义**:

```yaml
apiVersion: devices.kubeedge.io/v1beta1
kind: DeviceModel
metadata:
  name: temperature-model
  namespace: default
spec:
  properties:
  - name: temperature
    description: "Temperature in Celsius"
    type:
      double:
        accessMode: ReadOnly
        minimum: -50
        maximum: 100
        unit: "Celsius"
```

#### CloudHub

**功能**: 云边消息路由中心

**支持的协议**:

| 协议 | 端口 | 特点 | 适用场景 |
|------|------|------|---------|
| **WebSocket** | 10000 | 标准协议、易穿透 | 通用场景 |
| **QUIC** | 10001 | 低延迟、快速重连 | 弱网环境 |
| **HTTPS** | 10002 | 安全性高 | 高安全要求 |

**消息格式**:

```go
type Message struct {
    Header  MessageHeader `json:"header"`
    Router  MessageRoute  `json:"route"`
    Content interface{}   `json:"content"`
}

type MessageHeader struct {
    ID        string    `json:"id"`
    ParentID  string    `json:"parentid,omitempty"`
    Timestamp int64     `json:"timestamp"`
    Sync      bool      `json:"sync,omitempty"`
}

type MessageRoute struct {
    Source   string `json:"source"`
    Group    string `json:"group"`
    Operation string `json:"operation"`
    Resource  string `json:"resource"`
}
```

**消息流控**:

```yaml
流控配置:
  每节点最大连接: 10
  消息队列深度: 1024
  最大消息大小: 10MB
  心跳间隔: 30s
  重连延迟: 指数退避 (1s, 2s, 4s, 8s, 16s, 32s)
```

---

## EdgeCore详解

### 安装EdgeCore

#### 使用Keadm安装

```bash
# 1. 在云端获取token
TOKEN=$(keadm gettoken)

# 2. 在边缘节点安装EdgeCore
keadm join \
  --cloudcore-ipport=<CLOUD_IP>:10000 \
  --edgenode-name=edge-node-1 \
  --token=$TOKEN \
  --kubeedge-version=v1.18.0

# 3. 验证安装
systemctl status edgecore
journalctl -u edgecore -f

# 4. 在云端查看边缘节点
kubectl get nodes
# 应该看到edge-node-1节点
```

#### 高级安装选项

```bash
keadm join \
  --cloudcore-ipport=<CLOUD_IP>:10000 \
  --edgenode-name=edge-node-1 \
  --token=$TOKEN \
  --kubeedge-version=v1.18.0 \
  --runtimetype=containerd \  # 指定容器运行时
  --remote-runtime-endpoint=unix:///run/containerd/containerd.sock \
  --image-pull-policy=IfNotPresent \
  --cgroupdriver=systemd \
  --with-mqtt=true \  # 启用MQTT
  --mqtt-mode=internal  # 使用内置MQTT broker
```

### EdgeCore配置

**完整配置示例** (`edgecore.yaml`):

```yaml
apiVersion: edgecore.config.kubeedge.io/v1alpha2
kind: EdgeCore
database:
  dataSource: /var/lib/kubeedge/edgecore.db
modules:
  edged:
    enable: true
    cgroupDriver: systemd
    cgroupRoot: ""
    cgroupsPerQOS: true
    clusterDNS: ""
    clusterDomain: ""
    devicePluginEnabled: true
    dockerAddress: unix:///var/run/docker.sock
    gpuPluginEnabled: false
    imagePullProgressDeadline: 60
    maximumDeadContainersPerPod: 1
    nodeIP: ""  # 自动检测
    podSandboxImage: kubeedge/pause:3.6
    registerNode: true
    registerNodeNamespace: default
    remoteImageEndpoint: unix:///var/run/containerd/containerd.sock
    remoteRuntimeEndpoint: unix:///var/run/containerd/containerd.sock
    runtimeType: containerd
    nodeStatusUpdateFrequency: 10
    runtimeRequestTimeout: 2
    volumeStatsAggPeriod: 60000000000
    imageGCHighThreshold: 80
    imageGCLowThreshold: 40
    maximumDeadContainersPerContainer: 1
    hostnameOverride: edge-node-1
    registerSchedulable: true
  
  edgeHub:
    enable: true
    heartbeat: 15
    projectID: ""
    quic:
      handshakeTimeout: 30
      readDeadline: 15
      server: <CLOUD_IP>:10001
      writeDeadline: 15
    tlsCaFile: /etc/kubeedge/ca/rootCA.crt
    tlsCertFile: /etc/kubeedge/certs/server.crt
    tlsPrivateKeyFile: /etc/kubeedge/certs/server.key
    token: ""
    websocket:
      enable: true
      handshakeTimeout: 30
      readDeadline: 15
      server: <CLOUD_IP>:10000
      writeDeadline: 15
    httpServer: https://<CLOUD_IP>:10002
    rotateCertificates: true
  
  eventBus:
    enable: true
    mqttMode: internal  # external, internal, both
    mqttServerInternal: tcp://127.0.0.1:1883
    mqttServerExternal: tcp://<MQTT_BROKER>:1883
    mqttSubClientID: ""
    mqttPubClientID: ""
    mqttUsername: ""
    mqttPassword: ""
    mqttQOS: 0
    mqttRetain: false
    mqttSessionQueueSize: 100
  
  deviceTwin:
    enable: true
  
  metaManager:
    enable: true
    metaServer:
      enable: true
      server: 127.0.0.1:10550
    remoteQueryTimeout: 60
  
  serviceBus:
    enable: false
    port: 9060
    timeout: 60
```

### EdgeCore组件详解

#### Edged（轻量级Kubelet）

**功能**: Pod生命周期管理

**与Kubelet的区别**:

| 特性 | Kubelet | Edged |
|------|---------|-------|
| 资源占用 | ~300MB | ~70MB |
| 与API Server通信 | 直接连接 | 通过EdgeHub |
| 离线能力 | 无 | 完整支持 |
| 设备管理 | 无 | 内置支持 |
| CNI支持 | 全部 | 主流CNI |

**Pod管理流程**:

```text
1. EdgeHub接收Pod创建消息
   ↓
2. MetaManager更新本地数据库
   ↓
3. Edged从MetaManager读取Pod spec
   ↓
4. Edged调用容器运行时创建Pod
   ↓
5. 容器运行时拉取镜像、启动容器
   ↓
6. Edged监控Pod状态
   ↓
7. EdgeHub上报Pod状态到云端
```

#### EdgeHub（云边通信）

**功能**: 云边消息同步、断线重连

**连接管理**:

```go
// 连接状态机
type ConnectionState int

const (
    Connected    ConnectionState = iota  // 已连接
    Connecting                            // 连接中
    Disconnected                          // 已断开
)

// 重连策略
type ReconnectStrategy struct {
    InitialInterval time.Duration // 初始重连间隔: 1s
    Multiplier      float64       // 倍数: 2.0
    MaxInterval     time.Duration // 最大间隔: 32s
    MaxElapsedTime  time.Duration // 最大重连时间: 无限
}
```

**消息缓存**:

```yaml
缓存机制:
  断网期间:
    - 云端消息存储在EdgeHub内存队列
    - 边缘消息存储在MetaManager数据库
  
  重连后:
    - 按时间戳顺序发送缓存消息
    - 支持增量同步
    - 避免重复消息

缓存限制:
  内存队列: 1024条消息
  数据库: 10000条消息
  消息TTL: 24小时
```

#### EventBus（MQTT总线）

**功能**: 设备事件路由

**Topic设计**:

```text
$hw/events/device/{device_id}/twin/update         # 设备孪生更新
$hw/events/device/{device_id}/twin/update/result  # 更新结果
$hw/events/device/{device_id}/twin/get             # 获取设备孪生
$hw/events/device/{device_id}/twin/get/result      # 获取结果
$hw/events/device/{device_id}/state/update         # 设备状态更新
$hw/events/device/{device_id}/state/update/result  # 状态更新结果
$hw/events/node/{node_id}/membership/get           # 获取成员信息
$hw/events/node/{node_id}/membership/get/result    # 成员信息结果
```

**MQTT Broker选项**:

| 选项 | 说明 | 优势 | 劣势 |
|------|------|------|------|
| **internal** | 内置Broker | 简单、无需额外部署 | 功能有限 |
| **external** | 外部Broker (Mosquitto/EMQX) | 功能强大、高性能 | 需额外部署 |
| **both** | 内外结合 | 灵活 | 配置复杂 |

#### DeviceTwin（设备孪生）

**功能**: 设备状态同步

**孪生模型**:

```text
┌─────────────────────────────────────┐
│          Cloud (K8s)                │
│  ┌──────────────────────────────┐   │
│  │  Device CRD                  │   │
│  │  status:                     │   │
│  │    twins:                    │   │
│  │    - propertyName: temp      │   │
│  │      desired:                │   │
│  │        value: "30"  ←─────┐  │   │
│  │      reported:            │  │   │
│  │        value: "25.6" ←──┐ │  │   │
│  └──────────────────────────│─│──┘   │
└────────────────────────────│─│──────┘
                             │ │
                  CloudHub   │ │
                             ↓ ↑
┌────────────────────────────│─│──────┐
│          Edge               │ │      │
│  ┌──────────────────────────│─│──┐   │
│  │  DeviceTwin             │ │  │   │
│  │  - 存储期望状态(Desired)│ │  │   │
│  │  - 存储实际状态(Reported│ │  │   │
│  │  - 检测差异              │ │  │   │
│  └──────────────────────────│─│──┘   │
│               ↓ 应用期望     │ ↑      │
│               │              │ │上报   │
│  ┌──────────────────────────│─│──┐   │
│  │  Mapper                  │ │  │   │
│  │  - 协议转换              │ │  │   │
│  │  - 设备操作              │ │  │   │
│  └──────────────────────────│─│──┘   │
│                             ↓ ↑      │
│  [物理设备: 温度传感器 25.6°C]      │
└─────────────────────────────────────┘
```

**状态同步流程**:

```yaml
期望状态下发:
  1. 用户通过kubectl更新Device CRD的desired状态
  2. DeviceController检测到变化
  3. CloudHub发送到EdgeHub
  4. DeviceTwin接收并存储desired状态
  5. 检测到desired与reported差异
  6. 通过Mapper下发指令到设备
  7. 设备执行操作

实际状态上报:
  1. 设备通过Mapper上报数据
  2. Mapper发送到EventBus
  3. DeviceTwin接收并更新reported状态
  4. EdgeHub上报到CloudHub
  5. DeviceController更新Device CRD的reported状态
  6. 用户通过kubectl查看实际状态
```

---

## 设备管理

### 设备接入

#### Modbus设备接入

**1. 部署Modbus Mapper**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: modbus-mapper
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: modbus-mapper
  template:
    metadata:
      labels:
        app: modbus-mapper
    spec:
      nodeSelector:
        kubernetes.io/hostname: edge-node-1
      hostNetwork: true  # 访问/dev/ttyUSB0
      containers:
      - name: mapper
        image: kubeedge/modbus-mapper:v1.18.0
        imagePullPolicy: IfNotPresent
        securityContext:
          privileged: true  # 访问串口
        volumeMounts:
        - name: device
          mountPath: /dev/ttyUSB0
      volumes:
      - name: device
        hostPath:
          path: /dev/ttyUSB0
```

**2. 创建DeviceModel**:

```yaml
apiVersion: devices.kubeedge.io/v1beta1
kind: DeviceModel
metadata:
  name: modbus-温度传感器-model
spec:
  properties:
  - name: temperature
    description: "当前温度"
    type:
      double:
        accessMode: ReadOnly
        minimum: -50
        maximum: 100
        unit: "Celsius"
  - name: humidity
    description: "当前湿度"
    type:
      double:
        accessMode: ReadOnly
        minimum: 0
        maximum: 100
        unit: "%RH"
  - name: alarm_threshold
    description: "告警阈值"
    type:
      double:
        accessMode: ReadWrite
        minimum: 0
        maximum: 100
        unit: "Celsius"
```

**3. 创建Device**:

```yaml
apiVersion: devices.kubeedge.io/v1beta1
kind: Device
metadata:
  name: sensor-01
spec:
  deviceModelRef:
    name: modbus-温度传感器-model
  protocol:
    modbus:
      slaveID: 1
    common:
      com:
        serialPort: /dev/ttyUSB0
        baudRate: 9600
        dataBits: 8
        parity: none
        stopBits: 1
  nodeSelector:
    nodeSelectorTerms:
    - matchExpressions:
      - key: kubernetes.io/hostname
        operator: In
        values:
        - edge-node-1
  propertyVisitors:
  - propertyName: temperature
    modbus:
      register: holding
      offset: 0
      limit: 1
      scale: 0.1
      isSwap: false
      isRegisterSwap: false
    collectCycle: 5000   # 5秒采集一次
    reportCycle: 10000   # 10秒上报一次
  - propertyName: humidity
    modbus:
      register: holding
      offset: 1
      limit: 1
      scale: 0.1
      isSwap: false
    collectCycle: 5000
    reportCycle: 10000
  - propertyName: alarm_threshold
    modbus:
      register: holding
      offset: 10
      limit: 1
      scale: 0.1
      isSwap: false
    collectCycle: 60000  # 1分钟读取一次
```

**4. 查询设备状态**:

```bash
# 查看设备
kubectl get devices

# 查看设备详情
kubectl describe device sensor-01

# 查看设备孪生状态
kubectl get device sensor-01 -o jsonpath='{.status.twins}'

# 输出示例:
# [
#   {
#     "propertyName": "temperature",
#     "reported": {
#       "value": "25.6",
#       "metadata": {"timestamp": "2024-10-19T10:30:00Z"}
#     }
#   },
#   {
#     "propertyName": "humidity",
#     "reported": {
#       "value": "65.2",
#       "metadata": {"timestamp": "2024-10-19T10:30:00Z"}
#     }
#   }
# ]
```

**5. 更新设备期望状态**:

```bash
# 创建patch文件
cat <<EOF > device-patch.yaml
spec:
  properties:
  - name: alarm_threshold
    desired:
      value: "35.0"
      metadata:
        timestamp: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EOF

# 应用patch
kubectl patch device sensor-01 --type merge --patch "$(cat device-patch.yaml)"
```

#### MQTT设备接入

**1. 部署MQTT Mapper**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mqtt-mapper
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mqtt-mapper
  template:
    metadata:
      labels:
        app: mqtt-mapper
    spec:
      nodeSelector:
        kubernetes.io/hostname: edge-node-1
      containers:
      - name: mapper
        image: kubeedge/mqtt-mapper:v1.18.0
        env:
        - name: MQTT_BROKER_URL
          value: "tcp://127.0.0.1:1883"
```

**2. 创建MQTT Device**:

```yaml
apiVersion: devices.kubeedge.io/v1beta1
kind: Device
metadata:
  name: mqtt-device-01
spec:
  deviceModelRef:
    name: mqtt-device-model
  protocol:
    mqtt:
      brokerURL: tcp://127.0.0.1:1883
      clientID: mqtt-device-01
      username: ""
      password: ""
  propertyVisitors:
  - propertyName: temperature
    mqtt:
      topic: sensors/temperature
      qos: 1
      retained: false
    collectCycle: 5000
    reportCycle: 10000
```

### 自定义Mapper开发

**Mapper开发模板** (Go):

```go
package main

import (
    "github.com/kubeedge/kubeedge/cloud/pkg/devicecontroller/types"
    "github.com/kubeedge/mappers-go/mappers-common/pkg/common"
)

type CustomMapper struct {
    common.BaseMapper
}

func (m *CustomMapper) Initialize() error {
    // 初始化设备连接
    return nil
}

func (m *CustomMapper) GetDeviceData(visitor *types.PropertyVisitor) (interface{}, error) {
    // 从设备读取数据
    // 实现设备特定的协议
    return readFromDevice(visitor)
}

func (m *CustomMapper) SetDeviceData(visitor *types.PropertyVisitor, value string) error {
    // 向设备写入数据
    return writeToDevice(visitor, value)
}

func main() {
    mapper := &CustomMapper{}
    common.Run(mapper)
}
```

---

继续推进，现在文档已经达到约9,000字。让我继续编写剩余的重要章节...

## 应用部署

### 在边缘部署应用

#### 基础应用部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-edge
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      # 关键：指定边缘节点
      nodeSelector:
        node-role.kubernetes.io/edge: ""
      # 或指定具体节点
      # nodeSelector:
      #   kubernetes.io/hostname: edge-node-1
      
      containers:
      - name: nginx
        image: nginx:1.25-alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-edge
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: NodePort
```

**部署命令**:

```bash
# 部署应用
kubectl apply -f nginx-edge.yaml

# 查看Pod（注意NODE列显示为edge节点）
kubectl get pods -o wide

# 查看日志
kubectl logs nginx-edge-xxxxx

# 进入Pod
kubectl exec -it nginx-edge-xxxxx -- sh
```

#### 边缘应用组（NodeGroup）

**NodeGroup概念**: 将多个边缘节点分组管理，应用可以部署到整个组。

**1. 创建NodeGroup**:

```yaml
apiVersion: apps.kubeedge.io/v1alpha1
kind: NodeGroup
metadata:
  name: edge-group-zone-a
spec:
  nodes:
  - edge-node-1
  - edge-node-2
  - edge-node-3
  matchLabels:
    zone: "zone-a"
```

**2. 使用EdgeApplication部署**:

```yaml
apiVersion: apps.kubeedge.io/v1alpha1
kind: EdgeApplication
metadata:
  name: app-zone-a
spec:
  workloadTemplate:
    manifests:
    - apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: nginx
      spec:
        replicas: 1  # 每个节点1个副本
        selector:
          matchLabels:
            app: nginx
        template:
          metadata:
            labels:
              app: nginx
          spec:
            containers:
            - name: nginx
              image: nginx:1.25-alpine
  workloadScope:
    targetNodeGroups:
    - name: edge-group-zone-a
```

**效果**: 在zone-a的3个节点上各部署1个nginx Pod。

### 配置管理

#### ConfigMap和Secret

```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app.conf: |
    server {
        listen 80;
        server_name _;
        location / {
            root /usr/share/nginx/html;
        }
    }
---
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  username: YWRtaW4=  # base64: admin
  password: cGFzc3dvcmQ=  # base64: password
---
# 使用ConfigMap和Secret
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-config
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      nodeSelector:
        node-role.kubernetes.io/edge: ""
      containers:
      - name: app
        image: myapp:latest
        env:
        - name: USERNAME
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: username
        - name: PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: password
        volumeMounts:
        - name: config
          mountPath: /etc/nginx/conf.d
      volumes:
      - name: config
        configMap:
          name: app-config
```

### 边缘存储

#### Local Path Provisioner

```bash
# 1. 部署Local Path Provisioner
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml

# 2. 创建StorageClass
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-path
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: rancher.io/local-path
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
EOF

# 3. 使用PVC
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 10Gi
EOF
```

**在应用中使用**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-storage
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      nodeSelector:
        node-role.kubernetes.io/edge: ""
      containers:
      - name: app
        image: myapp:latest
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: data-pvc
```

---

## 云边协同

### 云边消息流

**下行消息（云→边）**:

```text
kubectl apply → K8s API Server → EdgeController → CloudHub → 
WebSocket/QUIC → EdgeHub → MetaManager → Edged → Container Runtime
```

**上行消息（边→云）**:

```text
Container Runtime → Edged → MetaManager → EdgeHub → 
WebSocket/QUIC → CloudHub → EdgeController → K8s API Server
```

### 云边通道类型

#### WebSocket (默认)

```yaml
优势:
  - 标准HTTP协议，易于穿透防火墙
  - 浏览器原生支持
  - 成熟稳定

劣势:
  - 延迟相对较高
  - 重连慢

适用:
  - 稳定网络环境
  - 需要穿透防火墙/代理
```

#### QUIC (推荐)

```yaml
优势:
  - 基于UDP，延迟低
  - 快速重连 (0-RTT)
  - 多路复用，无队头阻塞
  - 弱网环境表现好

劣势:
  - 相对新的协议
  - 部分网络可能阻止UDP

适用:
  - 弱网环境
  - 移动边缘节点
  - 对延迟敏感的场景
```

**启用QUIC**:

```bash
# CloudCore配置
keadm init --set cloudCore.modules.cloudHub.quic.enable=true

# EdgeCore配置
keadm join --with-quic=true
```

### 云边协同示例

#### 动态配置更新

**场景**: 运行时更新应用配置，无需重启Pod

```yaml
# 1. 更新ConfigMap
kubectl edit configmap app-config

# 2. ConfigMap自动同步到边缘（30秒内）

# 3. 应用通过inotify监听文件变化
# 或通过MetaServer API定期查询
```

**MetaServer API访问**:

```bash
# 在边缘Pod中访问MetaServer
curl http://127.0.0.1:10550/api/v1/namespaces/default/configmaps/app-config
```

---

## 边缘自治

### 离线能力

**断网场景处理**:

```yaml
EdgeCore离线模式:
  Pod管理:
    - 现有Pod继续运行
    - Pod重启后仍能启动（从本地缓存读取spec）
    - 可以kubectl exec进入Pod（EdgeStream功能）
  
  设备管理:
    - 设备数据继续采集
    - DeviceTwin本地存储
    - 设备控制正常工作
  
  限制:
    - 无法创建新Pod（需要镜像且镜像未缓存）
    - 无法删除Pod
    - 状态无法上报到云端

重连后:
  - 自动同步Pod状态
  - 上报设备数据
  - 执行pending的操作
  - 增量更新，不会全量同步
```

### 本地数据持久化

**MetaManager数据库**:

```bash
# 数据库位置
/var/lib/kubeedge/edgecore.db

# 查看数据库内容
sqlite3 /var/lib/kubeedge/edgecore.db
sqlite> .tables
# meta, device_twin, ...

sqlite> SELECT key, value FROM meta LIMIT 5;
```

### 边缘缓存策略

```yaml
资源缓存:
  Pod: 永久缓存
  ConfigMap: 永久缓存（Pod使用的）
  Secret: 永久缓存（Pod使用的）
  Service: 永久缓存
  Endpoints: 30分钟TTL

设备数据缓存:
  设备孪生: 永久缓存
  设备事件: 24小时TTL
  历史数据: 7天TTL（可配置）
```

---

## 生产部署

### 高可用部署

#### CloudCore高可用

```yaml
# 使用Deployment部署多副本CloudCore
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudcore
  namespace: kubeedge
spec:
  replicas: 3  # 3副本
  selector:
    matchLabels:
      app: cloudcore
  template:
    metadata:
      labels:
        app: cloudcore
    spec:
      affinity:
        podAntiAffinity:  # 反亲和，分散到不同节点
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: cloudcore
            topologyKey: kubernetes.io/hostname
      containers:
      - name: cloudcore
        image: kubeedge/cloudcore:v1.18.0
        ...
---
# LoadBalancer Service
apiVersion: v1
kind: Service
metadata:
  name: cloudcore-lb
  namespace: kubeedge
spec:
  type: LoadBalancer
  selector:
    app: cloudcore
  ports:
  - name: websocket
    port: 10000
    targetPort: 10000
  - name: quic
    port: 10001
    targetPort: 10001
  - name: https
    port: 10002
    targetPort: 10002
```

#### 边缘节点冗余

```yaml
应用部署策略:
  # 1. 多副本部署
  replicas: 3
  
  # 2. Pod反亲和（分散到不同边缘节点）
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: myapp
          topologyKey: kubernetes.io/hostname
  
  # 3. PodDisruptionBudget
  apiVersion: policy/v1
  kind: PodDisruptionBudget
  metadata:
    name: myapp-pdb
  spec:
    minAvailable: 1
    selector:
      matchLabels:
        app: myapp
```

### 安全加固

#### TLS证书管理

```bash
# 1. 生成CA证书
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -days 3650 -out ca.crt \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=KubeEdge/CN=kubeedge.io"

# 2. 生成服务端证书
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=KubeEdge/CN=cloudcore"

# 3. 签名证书
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt -days 365

# 4. 更新CloudCore证书
kubectl create secret generic cloudcore-certs \
  --from-file=ca.crt=ca.crt \
  --from-file=server.crt=server.crt \
  --from-file=server.key=server.key \
  -n kubeedge
```

#### RBAC权限控制

```yaml
# EdgeCore ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: edgecore
  namespace: kubeedge
---
# ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: edgecore
rules:
- apiGroups: [""]
  resources: ["nodes", "nodes/status"]
  verbs: ["get", "list", "watch", "update", "patch"]
- apiGroups: [""]
  resources: ["pods", "pods/status"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
---
# ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: edgecore
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: edgecore
subjects:
- kind: ServiceAccount
  name: edgecore
  namespace: kubeedge
```

### 性能优化

```yaml
CloudCore优化:
  资源限制:
    replicas: 3
    resources:
      requests:
        cpu: "1000m"
        memory: "1Gi"
      limits:
        cpu: "2000m"
        memory: "2Gi"
  
  参数调优:
    nodeLimit: 10000  # 最大边缘节点数
    messageCacheSize: 10000  # 消息缓存大小

EdgeCore优化:
  资源:
    nodeStatusUpdateFrequency: 10  # 节点状态上报频率(秒)
    imagePullProgressDeadline: 60  # 镜像拉取超时(秒)
  
  数据库:
    # 定期清理过期数据
    sqlite> DELETE FROM meta WHERE timestamp < datetime('now', '-7 days');
```

---

## 监控运维

### Prometheus监控

```yaml
# 监控指标
kubeedge_cloudcore_connected_nodes  # 已连接边缘节点数
kubeedge_cloudcore_message_send_total  # 发送消息总数
kubeedge_cloudcore_message_receive_total  # 接收消息总数
kubeedge_edgecore_pod_count  # 边缘Pod数量
kubeedge_edgecore_device_count  # 设备数量
```

### 日志收集

```bash
# CloudCore日志
kubectl logs -n kubeedge cloudcore-xxxxx -f

# EdgeCore日志
journalctl -u edgecore -f

# 日志级别调整
# 编辑/etc/kubeedge/config/edgecore.yaml
logLevel: "debug"  # debug, info, warn, error
```

---

## 最佳实践

### 1. 镜像管理

```yaml
推荐策略:
  - 边缘节点预拉取常用镜像
  - 使用私有镜像仓库（Harbor）
  - 镜像大小优化（Alpine base）
  - 启用镜像GC

命令:
  # 预拉取镜像
  crictl pull nginx:1.25-alpine
  
  # 配置私有仓库
  # /etc/containerd/config.toml
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
    endpoint = ["https://registry.example.com"]
```

### 2. 资源规划

```yaml
边缘节点分类:
  微型节点:
    CPU: 2核
    内存: 2GB
    应用: 轻量级服务（<5个Pod）
  
  小型节点:
    CPU: 4核
    内存: 8GB
    应用: 一般业务（<20个Pod）
  
  中型节点:
    CPU: 8核+
    内存: 16GB+
    应用: 复杂业务、AI推理
```

### 3. 网络优化

```yaml
协议选择:
  稳定网络: WebSocket
  弱网环境: QUIC
  高安全: HTTPS

参数调优:
  heartbeat: 15  # 心跳间隔（秒）
  messageQueueSize: 1024  # 消息队列大小
  writeDeadline: 15  # 写超时（秒）
```

---

## 参考资料

### 官方文档

- [KubeEdge Official Site](https://kubeedge.io/)
- [KubeEdge GitHub](https://github.com/kubeedge/kubeedge)
- [KubeEdge Documentation](https://kubeedge.io/docs/)
- [KubeEdge Blog](https://kubeedge.io/blog/)

### 技术文章

- [KubeEdge Architecture](https://kubeedge.io/docs/architecture/overview/)
- [Device Management](https://kubeedge.io/docs/developer/device_crd/)
- [EdgeMesh Service Mesh](https://edgemesh.netlify.app/)

### 视频教程

- [KubeEdge Introduction - YouTube](https://www.youtube.com/)
- [KubeEdge Workshop - KubeCon](https://www.youtube.com/)

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19  
**维护者**: 虚拟化容器化技术知识库项目组

**下一步阅读**:

- [03_K3s轻量级Kubernetes](./03_K3s轻量级Kubernetes.md)
- [04_5G边缘计算(MEC)](./04_5G边缘计算MEC.md)
- [05_边缘存储与数据管理](./05_边缘存储与数据管理.md)
