# Kubernetes GPU集成详解

## 目录

- [Kubernetes GPU集成详解](#kubernetes-gpu集成详解)
  - [目录](#目录)
  - [文档信息](#文档信息)
  - [1. 引言](#1-引言)
    - [1.1 Kubernetes GPU集成概述](#11-kubernetes-gpu集成概述)
    - [1.2 GPU集成的重要性](#12-gpu集成的重要性)
  - [2. Kubernetes GPU架构](#2-kubernetes-gpu架构)
    - [2.1 Device Plugin机制](#21-device-plugin机制)
      - [2.1.1 Device Plugin原理](#211-device-plugin原理)
      - [2.1.2 Device Plugin实现](#212-device-plugin实现)
    - [2.2 GPU Operator](#22-gpu-operator)
      - [2.2.1 GPU Operator概述](#221-gpu-operator概述)
      - [2.2.2 GPU Operator安装](#222-gpu-operator安装)
  - [3. GPU资源管理](#3-gpu资源管理)
    - [3.1 GPU资源定义](#31-gpu资源定义)
      - [3.1.1 资源类型](#311-资源类型)
      - [3.1.2 Pod资源请求](#312-pod资源请求)
    - [3.2 GPU资源配额](#32-gpu资源配额)
      - [3.2.1 Namespace配额](#321-namespace配额)
      - [3.2.2 LimitRange配置](#322-limitrange配置)
  - [4. GPU调度策略](#4-gpu调度策略)
    - [4.1 节点选择](#41-节点选择)
      - [4.1.1 节点标签](#411-节点标签)
      - [4.1.2 节点亲和性](#412-节点亲和性)
    - [4.2 调度器配置](#42-调度器配置)
      - [4.2.1 默认调度器](#421-默认调度器)
      - [4.2.2 自定义调度器](#422-自定义调度器)
  - [5. GPU监控和运维](#5-gpu监控和运维)
    - [5.1 GPU监控](#51-gpu监控)
      - [5.1.1 DCGM Exporter](#511-dcgm-exporter)
      - [5.1.2 Prometheus集成](#512-prometheus集成)
    - [5.2 GPU运维](#52-gpu运维)
      - [5.2.1 健康检查](#521-健康检查)
      - [5.2.2 日志管理](#522-日志管理)
  - [6. GPU应用部署](#6-gpu应用部署)
    - [6.1 单GPU部署](#61-单gpu部署)
      - [6.1.1 基础部署](#611-基础部署)
      - [6.1.2 多容器共享GPU](#612-多容器共享gpu)
    - [6.2 多GPU部署](#62-多gpu部署)
      - [6.2.1 数据并行训练](#621-数据并行训练)
      - [6.2.2 分布式训练](#622-分布式训练)
  - [7. GPU故障处理](#7-gpu故障处理)
    - [7.1 常见问题](#71-常见问题)
      - [7.1.1 GPU不可用](#711-gpu不可用)
      - [7.1.2 Pod调度失败](#712-pod调度失败)
    - [7.2 故障恢复](#72-故障恢复)
      - [7.2.1 自动恢复](#721-自动恢复)
      - [7.2.2 手动恢复](#722-手动恢复)
  - [8. 总结](#8-总结)
    - [8.1 Kubernetes GPU集成总结](#81-kubernetes-gpu集成总结)
    - [8.2 集成方案选择](#82-集成方案选择)
    - [8.3 未来展望](#83-未来展望)
  - [9. 附录](#9-附录)
    - [9.1 参考文档](#91-参考文档)
    - [9.2 相关工具](#92-相关工具)
    - [9.3 更新记录](#93-更新记录)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

## 文档信息

- **版本**: v2.0
- **创建日期**: 2025-10-17
- **更新日期**: 2025-12-05
- **状态**: ✅ 已完成
- **更新人**: AI Assistant

## 1. 引言

### 1.1 Kubernetes GPU集成概述

Kubernetes GPU集成是在Kubernetes集群中集成GPU资源，支持GPU容器调度、资源管理和监控的技术。
Kubernetes GPU集成通过Device Plugin机制、GPU Operator等工具，实现GPU资源的自动化管理和调度。

### 1.2 GPU集成的重要性

```yaml
集成重要性:
  云原生:
    - 容器化部署
    - Kubernetes编排
    - 自动化运维
    - 弹性伸缩

  资源管理:
    - 资源调度
    - 资源隔离
    - 资源监控
    - 资源优化

  多租户:
    - 多租户支持
    - 资源共享
    - 公平调度
    - 成本优化

  开发效率:
    - 简化部署
    - 自动化管理
    - 快速迭代
    - 易于维护
```

## 2. Kubernetes GPU架构

### 2.1 Device Plugin机制

#### 2.1.1 Device Plugin原理

```yaml
Device Plugin:
  工作原理:
    - GPU设备注册
    - 资源上报
    - 设备分配
    - 健康检查

  架构组件:
    - Device Plugin Manager
    - Device Plugin Server
    - Device Plugin Client
    - Kubelet集成

  工作流程:
    1. Device Plugin注册
    2. 资源发现
    3. 资源上报
    4. Pod调度
    5. 设备分配
    6. 健康检查
```

#### 2.1.2 Device Plugin实现

```go
// Device Plugin实现示例
package main

import (
    "context"
    "log"
    "net"
    "os"
    "path/filepath"
    "time"

    "google.golang.org/grpc"
    pluginapi "k8s.io/kubelet/pkg/apis/deviceplugin/v1beta1"
)

type GPUServer struct {
    pluginapi.UnimplementedDevicePluginServer
}

func (s *GPUServer) ListAndWatch(e *pluginapi.Empty, stream pluginapi.DevicePlugin_ListAndWatchServer) error {
    devices := []*pluginapi.Device{
        {ID: "GPU0", Health: pluginapi.Healthy},
        {ID: "GPU1", Health: pluginapi.Healthy},
    }

    for {
        if err := stream.Send(&pluginapi.ListAndWatchResponse{Devices: devices}); err != nil {
            return err
        }
        time.Sleep(5 * time.Second)
    }
}

func (s *GPUServer) Allocate(ctx context.Context, req *pluginapi.AllocateRequest) (*pluginapi.AllocateResponse, error) {
    var responses pluginapi.AllocateResponse

    for _, containerReq := range req.ContainerRequests {
        response := pluginapi.ContainerAllocateResponse{
            Devices: []*pluginapi.DeviceSpec{
                {ContainerPath: "/dev/nvidia0", HostPath: "/dev/nvidia0", Permissions: "rw"},
            },
            Envs: map[string]string{
                "CUDA_VISIBLE_DEVICES": "0",
            },
        }
        responses.ContainerResponses = append(responses.ContainerResponses, &response)
    }

    return &responses, nil
}

func main() {
    server := &GPUServer{}

    lis, err := net.Listen("unix", "/var/lib/kubelet/device-plugins/nvidia-gpu.sock")
    if err != nil {
        log.Fatal(err)
    }

    s := grpc.NewServer()
    pluginapi.RegisterDevicePluginServer(s, server)

    if err := s.Serve(lis); err != nil {
        log.Fatal(err)
    }
}
```

### 2.2 GPU Operator

#### 2.2.1 GPU Operator概述

```yaml
GPU Operator:
  定义:
    - NVIDIA GPU Operator
    - Kubernetes GPU管理
    - 自动化部署
    - 生命周期管理

  核心组件:
    - GPU Operator
    - NVIDIA Driver
    - NVIDIA Container Toolkit
    - NVIDIA Device Plugin
    - NVIDIA DCGM Exporter

  功能特性:
    - 自动部署
    - 版本管理
    - 健康检查
    - 自动升级
```

#### 2.2.2 GPU Operator安装

```bash
# 安装GPU Operator
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# 安装GPU Operator
helm install --wait gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --create-namespace

# 验证安装
kubectl get pods -n gpu-operator

# 检查GPU节点
kubectl get nodes -o json | jq '.items[] | select(.status.capacity."nvidia.com/gpu")'
```

## 3. GPU资源管理

### 3.1 GPU资源定义

#### 3.1.1 资源类型

```yaml
资源类型:
  nvidia.com/gpu:
    - GPU设备数量
    - 整数类型
    - 示例: 1, 2, 4

  nvidia.com/mig-1g.10gb:
    - MIG 1/7 GPU
    - 10GB显存
    - MIG实例

  nvidia.com/mig-2g.20gb:
    - MIG 1/3 GPU
    - 20GB显存
    - MIG实例

  nvidia.com/mig-3g.40gb:
    - MIG 1/2 GPU
    - 40GB显存
    - MIG实例
```

#### 3.1.2 Pod资源请求

```yaml
资源请求:
  apiVersion: v1
  kind: Pod
  metadata:
    name: gpu-pod
  spec:
    containers:
    - name: cuda-container
      image: nvidia/cuda:11.0-base
      resources:
        limits:
          nvidia.com/gpu: 1
        requests:
          nvidia.com/gpu: 1
      command: ["sleep", "infinity"]
```

### 3.2 GPU资源配额

#### 3.2.1 Namespace配额

```yaml
资源配额:
  apiVersion: v1
  kind: ResourceQuota
  metadata:
    name: gpu-quota
    namespace: production
  spec:
    hard:
      requests.nvidia.com/gpu: "10"
      limits.nvidia.com/gpu: "10"
```

#### 3.2.2 LimitRange配置

```yaml
限制范围:
  apiVersion: v1
  kind: LimitRange
  metadata:
    name: gpu-limit-range
    namespace: production
  spec:
    limits:
    - default:
        nvidia.com/gpu: "1"
      defaultRequest:
        nvidia.com/gpu: "1"
      type: Container
```

## 4. GPU调度策略

### 4.1 节点选择

#### 4.1.1 节点标签

```yaml
节点标签:
  添加标签:
    kubectl label nodes <node-name> accelerator=nvidia-tesla-k80

  查询标签:
    kubectl get nodes -l accelerator=nvidia-tesla-k80

  使用标签:
    apiVersion: v1
    kind: Pod
    spec:
      nodeSelector:
        accelerator: nvidia-tesla-k80
```

#### 4.1.2 节点亲和性

```yaml
节点亲和性:
  apiVersion: v1
  kind: Pod
  spec:
    affinity:
      nodeAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
          - matchExpressions:
            - key: accelerator
              operator: In
              values:
              - nvidia-tesla-k80
              - nvidia-tesla-v100
```

### 4.2 调度器配置

#### 4.2.1 默认调度器

```yaml
调度器配置:
  apiVersion: v1
  kind: ConfigMap
  metadata:
    name: kube-scheduler-config
    namespace: kube-system
  data:
    kube-scheduler.conf: |
      apiVersion: kubescheduler.config.k8s.io/v1beta3
      kind: KubeSchedulerConfiguration
      profiles:
      - schedulerName: default-scheduler
        plugins:
          filter:
            enabled:
            - name: NodeResourcesFit
          score:
            enabled:
            - name: NodeResourcesFit
              weight: 1
```

#### 4.2.2 自定义调度器

```yaml
自定义调度器:
  apiVersion: v1
  kind: Pod
  metadata:
    name: gpu-pod
  spec:
    schedulerName: gpu-scheduler
    containers:
    - name: cuda-container
      image: nvidia/cuda:11.0-base
      resources:
        limits:
          nvidia.com/gpu: 1
```

## 5. GPU监控和运维

### 5.1 GPU监控

#### 5.1.1 DCGM Exporter

```yaml
DCGM Exporter:
  功能:
    - GPU指标收集
    - Prometheus集成
    - 性能监控
    - 健康检查

  安装:
    kubectl apply -f https://raw.githubusercontent.com/NVIDIA/dcgm-exporter/main/deployments/kubernetes/dcgm-exporter.yaml

  配置:
    apiVersion: v1
    kind: Service
    metadata:
      name: dcgm-exporter
    spec:
      selector:
        app: dcgm-exporter
      ports:
      - port: 9400
        targetPort: 9400
```

#### 5.1.2 Prometheus集成

```yaml
Prometheus配置:
  apiVersion: v1
  kind: ServiceMonitor
  metadata:
    name: dcgm-exporter
  spec:
    selector:
      matchLabels:
        app: dcgm-exporter
    endpoints:
    - port: metrics
      interval: 30s
```

### 5.2 GPU运维

#### 5.2.1 健康检查

```yaml
健康检查:
  apiVersion: v1
  kind: Pod
  metadata:
    name: gpu-pod
  spec:
    containers:
    - name: cuda-container
      image: nvidia/cuda:11.0-base
      livenessProbe:
        exec:
          command:
          - nvidia-smi
        initialDelaySeconds: 30
        periodSeconds: 10
      readinessProbe:
        exec:
          command:
          - nvidia-smi
        initialDelaySeconds: 10
        periodSeconds: 5
```

#### 5.2.2 日志管理

```yaml
日志配置:
  apiVersion: v1
  kind: Pod
  metadata:
    name: gpu-pod
  spec:
    containers:
    - name: cuda-container
      image: nvidia/cuda:11.0-base
      volumeMounts:
      - name: log-volume
        mountPath: /var/log
    volumes:
    - name: log-volume
      emptyDir: {}
```

## 6. GPU应用部署

### 6.1 单GPU部署

#### 6.1.1 基础部署

```yaml
单GPU Pod:
  apiVersion: v1
  kind: Pod
  metadata:
    name: gpu-training-pod
  spec:
    containers:
    - name: training-container
      image: tensorflow/tensorflow:2.8.0-gpu
      resources:
        limits:
          nvidia.com/gpu: 1
        requests:
          nvidia.com/gpu: 1
      command:
      - python
      - train.py
```

#### 6.1.2 多容器共享GPU

```yaml
多容器共享:
  apiVersion: v1
  kind: Pod
  metadata:
    name: gpu-multi-pod
  spec:
    containers:
    - name: inference-container-1
      image: nvidia/cuda:11.0-base
      resources:
        limits:
          nvidia.com/gpu: 1
    - name: inference-container-2
      image: nvidia/cuda:11.0-base
      resources:
        limits:
          nvidia.com/gpu: 1
```

### 6.2 多GPU部署

#### 6.2.1 数据并行训练

```yaml
多GPU部署:
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: gpu-training-deployment
  spec:
    replicas: 4
    selector:
      matchLabels:
        app: gpu-training
    template:
      metadata:
        labels:
          app: gpu-training
      spec:
        containers:
        - name: training-container
          image: tensorflow/tensorflow:2.8.0-gpu
          resources:
            limits:
              nvidia.com/gpu: 1
            requests:
              nvidia.com/gpu: 1
          command:
          - python
          - train.py
```

#### 6.2.2 分布式训练

```yaml
分布式训练:
  apiVersion: batch/v1
  kind: Job
  metadata:
    name: distributed-training-job
  spec:
    completions: 4
    parallelism: 4
    template:
      spec:
        containers:
        - name: training-container
          image: tensorflow/tensorflow:2.8.0-gpu
          resources:
            limits:
              nvidia.com/gpu: 1
            requests:
              nvidia.com/gpu: 1
          command:
          - python
          - distributed_train.py
        restartPolicy: OnFailure
```

## 7. GPU故障处理

### 7.1 常见问题

#### 7.1.1 GPU不可用

```yaml
问题诊断:
  检查步骤:
    1. 检查GPU节点状态
       kubectl get nodes -o wide

    2. 检查GPU资源
       kubectl describe node <node-name>

    3. 检查Device Plugin
       kubectl get pods -n kube-system | grep nvidia

    4. 检查GPU驱动
       kubectl logs -n kube-system <device-plugin-pod>

  解决方案:
    - 重启Device Plugin
    - 更新GPU驱动
    - 检查硬件连接
    - 联系技术支持
```

#### 7.1.2 Pod调度失败

```yaml
问题诊断:
  检查步骤:
    1. 检查Pod事件
       kubectl describe pod <pod-name>

    2. 检查资源配额
       kubectl describe quota -n <namespace>

    3. 检查节点资源
       kubectl describe node <node-name>

    4. 检查调度器日志
       kubectl logs -n kube-system <scheduler-pod>

  解决方案:
    - 增加资源配额
    - 添加GPU节点
    - 调整资源请求
    - 检查调度器配置
```

### 7.2 故障恢复

#### 7.2.1 自动恢复

```yaml
自动恢复:
  Pod重启:
    restartPolicy: Always
    livenessProbe:
      exec:
        command:
        - nvidia-smi
      initialDelaySeconds: 30
      periodSeconds: 10
      failureThreshold: 3

  Node重启:
    - 节点自动恢复
    - Pod自动迁移
    - 资源自动释放
    - 服务自动恢复
```

#### 7.2.2 手动恢复

```yaml
手动恢复:
  步骤:
    1. 诊断问题
       kubectl describe pod <pod-name>

    2. 检查日志
       kubectl logs <pod-name>

    3. 重启Pod
       kubectl delete pod <pod-name>

    4. 检查状态
       kubectl get pods
```

## 8. 总结

### 8.1 Kubernetes GPU集成总结

Kubernetes GPU集成通过Device Plugin机制、GPU Operator等工具，实现了GPU资源的自动化管理和调度，为云原生AI/ML应用提供了强大的GPU支持。

### 8.2 集成方案选择

```yaml
方案选择:
  简单场景:
    - 推荐: Device Plugin
    - 原因: 简单易用
    - 配置: 基础配置
    - 适用: 小规模部署

  生产环境:
    - 推荐: GPU Operator
    - 原因: 自动化管理
    - 配置: 完整配置
    - 适用: 大规模部署

  高性能场景:
    - 推荐: 自定义调度器
    - 原因: 灵活调度
    - 配置: 高级配置
    - 适用: 高性能需求
```

### 8.3 未来展望

```yaml
未来展望:
  技术优化:
    - 更好的集成
    - 自动化运维
    - 性能优化
    - 易用性提升

  功能增强:
    - 更多GPU支持
    - 更好的调度
    - 更强的监控
    - 更快的故障恢复

  应用扩展:
    - 更多应用场景
    - 更好的性能
    - 更低的成本
    - 更易管理
```

## 9. 附录

### 9.1 参考文档

- Kubernetes GPU Support: <https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/>
- NVIDIA GPU Operator: <https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/>
- NVIDIA Device Plugin: <https://github.com/NVIDIA/k8s-device-plugin>

### 9.2 相关工具

- GPU Operator: GPU自动化管理
- Device Plugin: GPU设备插件
- DCGM Exporter: GPU监控
- Prometheus: 指标收集

### 9.3 更新记录

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|----------|--------|
| v1.0 | 2025-10-17 | 初始版本创建 | 技术团队 |

---

**文档状态**: 已完成
**下一步行动**: 创建GPU虚拟化最佳实践文档

---

## 相关文档

### 本模块相关

- [GPU虚拟化概述](./01_GPU虚拟化概述.md) - GPU虚拟化概述
- [NVIDIA MIG技术](./02_NVIDIA_MIG技术.md) - NVIDIA MIG技术详解
- [Alibaba cGPU技术](./03_Alibaba_cGPU技术.md) - Alibaba cGPU技术详解
- [GPU容器调度](./04_GPU容器调度.md) - GPU容器调度详解
- [GPU性能优化](./05_GPU性能优化.md) - GPU性能优化详解
- [GPU安全隔离](./06_GPU安全隔离.md) - GPU安全隔离详解
- [GPU虚拟化最佳实践](./08_GPU虚拟化最佳实践.md) - GPU虚拟化最佳实践

### 其他模块相关

- [Kubernetes技术详解](../03_Kubernetes技术详解/README.md) - Kubernetes技术体系
- [Kubernetes架构原理](../03_Kubernetes技术详解/01_Kubernetes架构原理.md) - Kubernetes架构原理
- [容器编排技术](../04_容器编排技术/README.md) - 容器编排技术

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新
