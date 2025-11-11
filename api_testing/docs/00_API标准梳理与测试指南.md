# API标准梳理与测试指南

## 📚 文档目录

- [API标准梳理与测试指南](#api标准梳理与测试指南)
  - [📚 文档目录](#-文档目录)
  - [概述](#概述)
    - [什么是API标准？](#什么是api标准)
    - [为什么需要API测试？](#为什么需要api测试)
    - [本项目涵盖的API标准](#本项目涵盖的api标准)
  - [API标准解释](#api标准解释)
    - [1. RESTful API标准](#1-restful-api标准)
    - [2. gRPC API标准](#2-grpc-api标准)
    - [3. Unix Socket通信](#3-unix-socket通信)
  - [Docker API标准](#docker-api标准)
    - [API版本与兼容性](#api版本与兼容性)
    - [核心API分类](#核心api分类)
      - [1. 系统信息API](#1-系统信息api)
      - [2. 镜像管理API](#2-镜像管理api)
      - [3. 容器管理API](#3-容器管理api)
      - [4. 网络管理API](#4-网络管理api)
      - [5. 卷管理API](#5-卷管理api)
  - [Kubernetes API标准](#kubernetes-api标准)
    - [API架构](#api架构)
    - [核心资源API](#核心资源api)
      - [1. Pod API](#1-pod-api)
      - [2. Deployment API](#2-deployment-api)
      - [3. Service API](#3-service-api)
      - [4. ConfigMap \& Secret API](#4-configmap--secret-api)
  - [etcd API标准](#etcd-api标准)
    - [API架构](#api架构-1)
    - [核心API](#核心api)
      - [1. KV服务](#1-kv服务)
      - [2. Watch服务](#2-watch服务)
      - [3. Lease服务](#3-lease服务)
  - [测试场景梳理](#测试场景梳理)
    - [单元测试场景](#单元测试场景)
      - [Docker API测试场景](#docker-api测试场景)
      - [Kubernetes API测试场景](#kubernetes-api测试场景)
      - [etcd API测试场景](#etcd-api测试场景)
    - [集成测试场景](#集成测试场景)
  - [使用说明](#使用说明)
    - [快速开始](#快速开始)
      - [1. 环境准备](#1-环境准备)
      - [2. 运行测试](#2-运行测试)
      - [3. 查看结果](#3-查看结果)
    - [编写新测试](#编写新测试)
      - [示例: 添加Docker API测试](#示例-添加docker-api测试)
    - [调试技巧](#调试技巧)
  - [最佳实践](#最佳实践)
    - [1. 测试设计原则](#1-测试设计原则)
    - [2. 测试数据管理](#2-测试数据管理)
    - [3. 资源清理](#3-资源清理)
    - [4. 错误处理](#4-错误处理)
    - [5. 性能测试](#5-性能测试)
  - [总结](#总结)
    - [API标准覆盖](#api标准覆盖)
    - [测试价值](#测试价值)

---

## 概述

### 什么是API标准？

API标准是指规范化的应用程序接口规范，定义了：

- **接口格式**: RESTful、gRPC、WebSocket等
- **通信协议**: HTTP/HTTPS、TCP、Unix Socket等
- **数据格式**: JSON、Protobuf、YAML等
- **认证授权**: Token、TLS、ACL等
- **版本管理**: API版本控制策略

### 为什么需要API测试？

```yaml
业务价值:
  ✅ 确保API功能正确性
  ✅ 验证API性能指标
  ✅ 保证API向后兼容
  ✅ 提前发现集成问题
  ✅ 提高系统稳定性

技术价值:
  ✅ 文档即测试
  ✅ 自动化回归测试
  ✅ CI/CD集成
  ✅ 性能基准测试
  ✅ 安全性验证
```

### 本项目涵盖的API标准

```
虚拟化与容器化技术栈:
├── Docker Engine API (RESTful + Unix Socket)
├── Kubernetes API (RESTful + gRPC)
├── etcd API (gRPC)
├── Podman API (RESTful)
├── containerd API (gRPC)
└── libvirt API (RPC)

测试覆盖:
├── 单元测试: 51个测试用例
├── 集成测试: 5个测试场景
├── 性能测试: 完整基准测试
└── 功能集成: 测试工厂+工具
```

---

## API标准解释

### 1. RESTful API标准

**定义**: Representational State Transfer，基于HTTP协议的API设计风格。

**核心原则**:

```yaml
1. 资源导向 (Resource-Oriented):
   - URL代表资源
   - /containers/{id} 表示特定容器资源

2. HTTP方法语义:
   - GET: 获取资源
   - POST: 创建资源
   - PUT/PATCH: 更新资源
   - DELETE: 删除资源

3. 无状态 (Stateless):
   - 每个请求包含所有必要信息
   - 服务器不保存客户端状态

4. 统一接口 (Uniform Interface):
   - 标准化的资源操作
   - 一致的错误处理
```

**示例 - Docker API**:

```http
# 获取容器列表
GET /containers/json HTTP/1.1
Host: /var/run/docker.sock
Accept: application/json

Response: 200 OK
[
  {
    "Id": "abc123...",
    "Names": ["/my-container"],
    "Image": "nginx:alpine",
    "State": "running",
    "Status": "Up 2 hours"
  }
]

# 创建容器
POST /containers/create HTTP/1.1
Content-Type: application/json

{
  "Image": "nginx:alpine",
  "Cmd": ["nginx", "-g", "daemon off;"],
  "ExposedPorts": {
    "80/tcp": {}
  }
}

Response: 201 Created
{
  "Id": "def456...",
  "Warnings": []
}
```

### 2. gRPC API标准

**定义**: Google Remote Procedure Call，基于HTTP/2的高性能RPC框架。

**核心特性**:

```yaml
1. Protocol Buffers:
   - 强类型定义
   - 高效的二进制序列化
   - 跨语言支持

2. 双向流式传输:
   - 服务器流式 (Server Streaming)
   - 客户端流式 (Client Streaming)
   - 双向流式 (Bidirectional Streaming)

3. 内置功能:
   - 负载均衡
   - 截止时间 (Deadline)
   - 认证授权
   - 压缩
```

**示例 - etcd API**:

```protobuf
// etcd KV服务定义
service KV {
  // 存储键值对
  rpc Put(PutRequest) returns (PutResponse) {}

  // 获取键值对
  rpc Range(RangeRequest) returns (RangeResponse) {}

  // 删除键值对
  rpc DeleteRange(DeleteRangeRequest) returns (DeleteRangeResponse) {}

  // 事务操作
  rpc Txn(TxnRequest) returns (TxnResponse) {}
}

// Go客户端使用
client, _ := clientv3.New(clientv3.Config{
    Endpoints: []string{"localhost:2379"},
})

// Put操作
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

resp, err := client.Put(ctx, "/config/app", "value")
```

### 3. Unix Socket通信

**定义**: 本地进程间通信(IPC)机制，高效的本地API调用。

**特点**:

```yaml
优势:
  ✅ 无需网络开销
  ✅ 更高的安全性
  ✅ 更快的传输速度
  ✅ 自动权限控制

使用场景:
  - Docker守护进程通信
  - 容器运行时通信
  - 本地服务调用
```

**示例 - Docker Unix Socket**:

```go
// Go客户端通过Unix Socket连接
client, err := client.NewClientWithOpts(
    client.WithHost("unix:///var/run/docker.sock"),
    client.WithAPIVersionNegotiation(),
)

// curl通过Unix Socket调用
curl --unix-socket /var/run/docker.sock \
     http://localhost/containers/json
```

---

## Docker API标准

### API版本与兼容性

```yaml
API版本管理:
  当前版本: 1.43
  最低支持: 1.24
  版本协商: 自动选择兼容版本

向后兼容性:
  ✅ 新增字段不影响旧版本
  ✅ 废弃字段保留一定时间
  ✅ Breaking Change需要主版本升级
```

### 核心API分类

#### 1. 系统信息API

**用途**: 获取Docker守护进程信息和状态

```yaml
GET /version:
  描述: 获取Docker版本信息
  认证: 不需要
  返回: 版本号、API版本、Go版本、操作系统等

  测试场景:
    - 验证Docker守护进程可用
    - 检查API版本兼容性
    - 确认系统架构

GET /info:
  描述: 获取系统信息
  认证: 不需要
  返回: 容器数、镜像数、存储驱动、内核版本等

  测试场景:
    - 验证系统资源
    - 检查存储驱动
    - 确认容器运行时

GET /_ping:
  描述: 健康检查
  认证: 不需要
  返回: "OK"

  测试场景:
    - 监控服务可用性
    - 负载均衡健康检查
    - 快速连通性测试
```

**Go代码示例**:

```go
// 获取Docker版本
version, err := client.ServerVersion(ctx)
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Docker版本: %s\n", version.Version)
fmt.Printf("API版本: %s\n", version.APIVersion)

// 获取系统信息
info, err := client.Info(ctx)
if err != nil {
    log.Fatal(err)
}
fmt.Printf("容器数: %d (运行中: %d)\n", info.Containers, info.ContainersRunning)
fmt.Printf("镜像数: %d\n", info.Images)
fmt.Printf("存储驱动: %s\n", info.Driver)

// Ping测试
_, err = client.Ping(ctx)
if err != nil {
    log.Fatal("Docker守护进程不可用")
}
```

#### 2. 镜像管理API

**用途**: 管理Docker镜像生命周期

```yaml
GET /images/json:
  描述: 列出所有镜像
  参数:
    - all: 显示中间层镜像
    - filters: 过滤条件(dangling, label等)

  测试场景:
    - 验证镜像列表
    - 检查镜像存在
    - 清理悬空镜像

POST /images/create:
  描述: 拉取镜像
  参数:
    - fromImage: 镜像名称
    - tag: 标签
  流式响应: 下载进度

  测试场景:
    - 验证镜像拉取
    - 测试网络连接
    - 检查认证

GET /images/{name}/json:
  描述: 检查镜像详情
  返回: 镜像元数据、层信息、配置等

  测试场景:
    - 验证镜像完整性
    - 检查镜像配置
    - 分析镜像层

DELETE /images/{name}:
  描述: 删除镜像
  参数:
    - force: 强制删除
    - noprune: 不删除未标记的父镜像

  测试场景:
    - 清理测试镜像
    - 验证依赖检查
    - 测试强制删除
```

**Go代码示例**:

```go
// 列出镜像
images, err := client.ImageList(ctx, types.ImageListOptions{})
for _, img := range images {
    fmt.Printf("镜像: %s, 大小: %d MB\n",
        img.RepoTags[0], img.Size/1024/1024)
}

// 拉取镜像
out, err := client.ImagePull(ctx, "nginx:alpine", types.ImagePullOptions{})
if err != nil {
    log.Fatal(err)
}
defer out.Close()
io.Copy(os.Stdout, out) // 显示下载进度

// 检查镜像
inspect, _, err := client.ImageInspectWithRaw(ctx, "nginx:alpine")
fmt.Printf("镜像ID: %s\n", inspect.ID)
fmt.Printf("创建时间: %s\n", inspect.Created)
fmt.Printf("架构: %s\n", inspect.Architecture)

// 删除镜像
_, err = client.ImageRemove(ctx, "nginx:alpine", types.ImageRemoveOptions{
    Force: true,
})
```

#### 3. 容器管理API

**用途**: 管理Docker容器完整生命周期

```yaml
POST /containers/create:
  描述: 创建容器
  请求体: 容器配置(镜像、命令、环境变量、端口等)
  返回: 容器ID和警告

  测试场景:
    - 创建基础容器
    - 测试端口映射
    - 验证环境变量
    - 测试卷挂载
    - 检查网络配置

POST /containers/{id}/start:
  描述: 启动容器
  参数: detachKeys (分离键)

  测试场景:
    - 验证容器启动
    - 检查启动时间
    - 测试依赖容器

GET /containers/{id}/json:
  描述: 检查容器详情
  返回: 完整的容器状态和配置

  测试场景:
    - 验证容器状态
    - 检查运行时配置
    - 分析资源使用

GET /containers/{id}/logs:
  描述: 获取容器日志
  参数:
    - stdout/stderr: 输出流选择
    - since/until: 时间范围
    - tail: 最后N行
  流式响应: 日志流

  测试场景:
    - 验证应用输出
    - 调试容器问题
    - 收集日志数据

GET /containers/{id}/stats:
  描述: 获取容器统计信息
  流式响应: 实时统计数据

  测试场景:
    - 监控资源使用
    - 性能分析
    - 资源限制验证

POST /containers/{id}/stop:
  描述: 停止容器
  参数: t (超时秒数)

  测试场景:
    - 优雅停止
    - 超时处理
    - 信号处理

DELETE /containers/{id}:
  描述: 删除容器
  参数:
    - v: 删除关联卷
    - force: 强制删除运行中容器

  测试场景:
    - 清理测试容器
    - 验证卷清理
    - 测试强制删除
```

**Go代码示例**:

```go
// 创建容器
resp, err := client.ContainerCreate(ctx,
    &container.Config{
        Image: "nginx:alpine",
        Cmd:   []string{"nginx", "-g", "daemon off;"},
        ExposedPorts: nat.PortSet{
            "80/tcp": struct{}{},
        },
    },
    &container.HostConfig{
        PortBindings: nat.PortMap{
            "80/tcp": []nat.PortBinding{
                {HostPort: "8080"},
            },
        },
    },
    nil, nil, "my-nginx")

containerID := resp.ID

// 启动容器
err = client.ContainerStart(ctx, containerID, types.ContainerStartOptions{})

// 检查容器
inspect, err := client.ContainerInspect(ctx, containerID)
fmt.Printf("状态: %s\n", inspect.State.Status)
fmt.Printf("PID: %d\n", inspect.State.Pid)

// 获取日志
logs, err := client.ContainerLogs(ctx, containerID, types.ContainerLogsOptions{
    ShowStdout: true,
    ShowStderr: true,
    Tail:       "100",
})
io.Copy(os.Stdout, logs)

// 获取统计信息
stats, err := client.ContainerStats(ctx, containerID, false)
// 解析stats.Body获取CPU、内存等信息

// 停止容器
timeout := 10
err = client.ContainerStop(ctx, containerID, &timeout)

// 删除容器
err = client.ContainerRemove(ctx, containerID, types.ContainerRemoveOptions{
    Force:         true,
    RemoveVolumes: true,
})
```

#### 4. 网络管理API

```yaml
POST /networks/create:
  描述: 创建网络
  参数: 网络名称、驱动、IPAM配置

  测试场景:
    - 创建自定义网络
    - 测试网络驱动
    - 验证IP分配

GET /networks/{id}:
  描述: 检查网络详情
  返回: 网络配置和连接的容器

  测试场景:
    - 验证网络配置
    - 检查容器连接
    - 分析网络拓扑

POST /networks/{id}/connect:
  描述: 连接容器到网络

  测试场景:
    - 动态网络连接
    - 多网络容器
    - 网络隔离测试

DELETE /networks/{id}:
  描述: 删除网络

  测试场景:
    - 清理测试网络
    - 验证依赖检查
```

#### 5. 卷管理API

```yaml
POST /volumes/create:
  描述: 创建卷
  参数: 卷名称、驱动、标签

  测试场景:
    - 创建数据卷
    - 测试卷驱动
    - 验证持久化

GET /volumes/{name}:
  描述: 检查卷详情
  返回: 卷配置和挂载点

  测试场景:
    - 验证卷配置
    - 检查挂载点
    - 分析存储使用

DELETE /volumes/{name}:
  描述: 删除卷
  参数: force (强制删除)

  测试场景:
    - 清理测试卷
    - 验证数据清除
```

---

## Kubernetes API标准

### API架构

```yaml
API组织结构:
  核心API (Core API):
    - /api/v1/*
    - Pod, Service, Namespace, ConfigMap等

  命名空间API (Named API):
    - /apis/{group}/{version}/*
    - apps/v1: Deployment, StatefulSet
    - batch/v1: Job, CronJob
    - networking.k8s.io/v1: Ingress, NetworkPolicy

API访问方式:
  1. kubectl: 命令行工具
  2. client-go: Go客户端库
  3. REST API: 直接HTTP调用
  4. SDK: 各语言SDK
```

### 核心资源API

#### 1. Pod API

**定义**: Kubernetes中最小的部署单元

```yaml
POST /api/v1/namespaces/{namespace}/pods:
  描述: 创建Pod
  请求体: Pod规范

  测试场景:
    - 创建单容器Pod
    - 创建多容器Pod
    - 测试Init容器
    - 验证资源限制
    - 测试卷挂载

GET /api/v1/namespaces/{namespace}/pods/{name}:
  描述: 获取Pod详情
  返回: Pod状态、容器状态、事件等

  测试场景:
    - 检查Pod状态
    - 验证容器就绪
    - 分析事件日志

GET /api/v1/namespaces/{namespace}/pods:
  描述: 列出Pods
  参数: labelSelector, fieldSelector

  测试场景:
    - 按标签筛选
    - 按字段筛选
    - 验证列表分页

GET /api/v1/namespaces/{namespace}/pods/{name}/log:
  描述: 获取Pod日志
  参数: container, tailLines, since

  测试场景:
    - 获取容器日志
    - 多容器日志
    - 实时日志流

DELETE /api/v1/namespaces/{namespace}/pods/{name}:
  描述: 删除Pod
  参数: gracePeriodSeconds

  测试场景:
    - 优雅删除
    - 强制删除
    - 终止信号处理
```

**Go代码示例**:

```go
// 创建Pod
pod := &corev1.Pod{
    ObjectMeta: metav1.ObjectMeta{
        Name:      "test-pod",
        Namespace: "default",
        Labels: map[string]string{
            "app": "test",
        },
    },
    Spec: corev1.PodSpec{
        Containers: []corev1.Container{
            {
                Name:  "nginx",
                Image: "nginx:alpine",
                Ports: []corev1.ContainerPort{
                    {ContainerPort: 80},
                },
            },
        },
    },
}

createdPod, err := clientset.CoreV1().Pods("default").Create(ctx, pod, metav1.CreateOptions{})

// 获取Pod
pod, err := clientset.CoreV1().Pods("default").Get(ctx, "test-pod", metav1.GetOptions{})
fmt.Printf("状态: %s\n", pod.Status.Phase)

// 列出Pods
pods, err := clientset.CoreV1().Pods("default").List(ctx, metav1.ListOptions{
    LabelSelector: "app=test",
})

// 获取日志
req := clientset.CoreV1().Pods("default").GetLogs("test-pod", &corev1.PodLogOptions{
    Container: "nginx",
    TailLines: int64Ptr(100),
})
logs, err := req.Stream(ctx)
io.Copy(os.Stdout, logs)

// 删除Pod
err = clientset.CoreV1().Pods("default").Delete(ctx, "test-pod", metav1.DeleteOptions{})
```

#### 2. Deployment API

```yaml
POST /apis/apps/v1/namespaces/{namespace}/deployments:
  描述: 创建Deployment

  测试场景:
    - 创建基础Deployment
    - 配置副本数
    - 设置更新策略
    - 配置健康检查

GET /apis/apps/v1/namespaces/{namespace}/deployments/{name}:
  描述: 获取Deployment详情

  测试场景:
    - 检查部署状态
    - 验证副本数
    - 分析更新进度

PATCH /apis/apps/v1/namespaces/{namespace}/deployments/{name}/scale:
  描述: 扩缩容Deployment

  测试场景:
    - 水平扩展
    - 缩容测试
    - 零副本测试
```

#### 3. Service API

```yaml
POST /api/v1/namespaces/{namespace}/services:
  描述: 创建Service

  测试场景:
    - ClusterIP服务
    - NodePort服务
    - LoadBalancer服务
    - 端口映射

GET /api/v1/namespaces/{namespace}/services/{name}:
  描述: 获取Service详情

  测试场景:
    - 验证服务配置
    - 检查端点
    - 测试服务发现
```

#### 4. ConfigMap & Secret API

```yaml
POST /api/v1/namespaces/{namespace}/configmaps:
  描述: 创建ConfigMap

  测试场景:
    - 配置数据存储
    - 环境变量注入
    - 文件挂载

POST /api/v1/namespaces/{namespace}/secrets:
  描述: 创建Secret

  测试场景:
    - 敏感数据存储
    - TLS证书管理
    - Docker Registry认证
```

---

## etcd API标准

### API架构

```yaml
服务分类:
  KV服务: 键值对存储
  Watch服务: 变更监听
  Lease服务: 租约管理
  Cluster服务: 集群管理
  Maintenance服务: 维护操作
  Auth服务: 认证授权

通信协议:
  - gRPC (主要)
  - HTTP/JSON (网关)
```

### 核心API

#### 1. KV服务

```yaml
Put(PutRequest):
  描述: 存储键值对
  参数:
    - key: 键
    - value: 值
    - lease: 租约ID
    - prev_kv: 返回前一个值

  测试场景:
    - 基础存储
    - 带租约存储
    - 条件更新

Range(RangeRequest):
  描述: 获取键值对
  参数:
    - key: 键或范围起点
    - range_end: 范围终点
    - limit: 返回数量限制

  测试场景:
    - 单键查询
    - 范围查询
    - 前缀查询

DeleteRange(DeleteRangeRequest):
  描述: 删除键值对
  参数:
    - key: 键或范围起点
    - range_end: 范围终点

  测试场景:
    - 单键删除
    - 范围删除
    - 前缀删除

Txn(TxnRequest):
  描述: 事务操作
  参数:
    - compare: 比较条件
    - success: 成功操作
    - failure: 失败操作

  测试场景:
    - 原子操作
    - 条件更新
    - 乐观锁
```

**Go代码示例**:

```go
// Put操作
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

putResp, err := client.Put(ctx, "/config/app", "value")
fmt.Printf("修订版本: %d\n", putResp.Header.Revision)

// Get操作
getResp, err := client.Get(ctx, "/config/app")
for _, kv := range getResp.Kvs {
    fmt.Printf("键: %s, 值: %s\n", kv.Key, kv.Value)
}

// 范围查询
getResp, err := client.Get(ctx, "/config/", clientv3.WithPrefix())

// Delete操作
delResp, err := client.Delete(ctx, "/config/app")
fmt.Printf("删除数量: %d\n", delResp.Deleted)

// 事务操作
txn := client.Txn(ctx).
    If(clientv3.Compare(clientv3.Value("/config/app"), "=", "old-value")).
    Then(clientv3.OpPut("/config/app", "new-value")).
    Else(clientv3.OpGet("/config/app"))

txnResp, err := txn.Commit()
if txnResp.Succeeded {
    fmt.Println("事务成功")
}
```

#### 2. Watch服务

```yaml
Watch(WatchRequest):
  描述: 监听键变化
  流式响应: 变更事件流

  测试场景:
    - 单键监听
    - 范围监听
    - 前缀监听
    - 历史事件重放
```

**Go代码示例**:

```go
// Watch单个键
watchChan := client.Watch(ctx, "/config/app")
for watchResp := range watchChan {
    for _, event := range watchResp.Events {
        fmt.Printf("事件类型: %s\n", event.Type)
        fmt.Printf("键: %s, 值: %s\n", event.Kv.Key, event.Kv.Value)
    }
}

// Watch前缀
watchChan := client.Watch(ctx, "/config/", clientv3.WithPrefix())
```

#### 3. Lease服务

```yaml
LeaseGrant(LeaseGrantRequest):
  描述: 创建租约
  参数: TTL (生存时间)

  测试场景:
    - 创建租约
    - TTL验证

LeaseKeepAlive(LeaseKeepAliveRequest):
  描述: 续约
  流式请求/响应

  测试场景:
    - 自动续约
    - 租约保持

LeaseRevoke(LeaseRevokeRequest):
  描述: 撤销租约

  测试场景:
    - 手动撤销
    - 级联删除
```

---

## 测试场景梳理

### 单元测试场景

#### Docker API测试场景

```yaml
场景1: 系统信息验证
  目标: 确保Docker守护进程可用
  步骤:
    1. 调用/version获取版本
    2. 验证API版本兼容性
    3. 调用/_ping确认连通性
  断言:
    - 版本号不为空
    - API版本>=1.24
    - Ping返回OK

场景2: 镜像生命周期
  目标: 测试镜像完整生命周期
  步骤:
    1. 拉取测试镜像
    2. 检查镜像详情
    3. 使用镜像创建容器
    4. 删除容器后删除镜像
  断言:
    - 镜像成功拉取
    - 镜像详情正确
    - 容器创建成功
    - 镜像成功删除

场景3: 容器生命周期
  目标: 测试容器完整生命周期
  步骤:
    1. 创建容器
    2. 启动容器
    3. 检查容器状态
    4. 获取容器日志
    5. 停止容器
    6. 删除容器
  断言:
    - 每个操作成功
    - 状态转换正确
    - 日志可获取

场景4: 网络隔离
  目标: 测试容器网络隔离
  步骤:
    1. 创建自定义网络
    2. 创建容器1连接到网络
    3. 创建容器2不连接网络
    4. 验证网络隔离
  断言:
    - 网络创建成功
    - 容器1可访问
    - 容器2不可访问

场景5: 卷数据持久化
  目标: 测试数据持久化
  步骤:
    1. 创建数据卷
    2. 容器1挂载卷并写入数据
    3. 删除容器1
    4. 容器2挂载卷并读取数据
  断言:
    - 数据写入成功
    - 数据读取成功
    - 数据内容一致
```

#### Kubernetes API测试场景

```yaml
场景1: Pod生命周期
  目标: 测试Pod完整生命周期
  步骤:
    1. 创建Pod
    2. 等待Pod运行
    3. 检查Pod状态
    4. 获取Pod日志
    5. 删除Pod
  断言:
    - Pod创建成功
    - Pod进入Running状态
    - 容器就绪
    - 日志可获取

场景2: Deployment扩缩容
  目标: 测试应用扩缩容
  步骤:
    1. 创建Deployment (3副本)
    2. 验证副本数
    3. 扩容到5副本
    4. 验证扩容成功
    5. 缩容到2副本
    6. 验证缩容成功
  断言:
    - 每次副本数正确
    - Pod状态健康

场景3: Service服务发现
  目标: 测试服务发现机制
  步骤:
    1. 创建Deployment
    2. 创建Service
    3. 验证Service端点
    4. 测试服务访问
  断言:
    - Service创建成功
    - 端点正确
    - 服务可访问

场景4: ConfigMap配置注入
  目标: 测试配置管理
  步骤:
    1. 创建ConfigMap
    2. 创建Pod引用ConfigMap
    3. 验证配置注入
  断言:
    - ConfigMap创建成功
    - 环境变量正确
    - 文件挂载成功
```

#### etcd API测试场景

```yaml
场景1: KV基础操作
  目标: 测试基础存储功能
  步骤:
    1. Put键值对
    2. Get键值对
    3. Delete键值对
  断言:
    - Put成功
    - Get返回正确值
    - Delete成功

场景2: Watch监听
  目标: 测试变更监听
  步骤:
    1. 启动Watch
    2. 修改键值
    3. 接收Watch事件
  断言:
    - Watch启动成功
    - 事件接收正确
    - 事件类型正确

场景3: 租约管理
  目标: 测试租约功能
  步骤:
    1. 创建租约(TTL=5s)
    2. Put带租约的键
    3. 等待6秒
    4. Get键(应该不存在)
  断言:
    - 租约创建成功
    - 键自动过期

场景4: 事务操作
  目标: 测试原子操作
  步骤:
    1. 设置初始值
    2. 执行事务(条件更新)
    3. 验证结果
  断言:
    - 事务执行成功
    - 条件判断正确
    - 结果符合预期
```

### 集成测试场景

```yaml
场景1: Docker到Kubernetes
  目标: 测试跨平台镜像部署
  步骤:
    1. Docker拉取镜像
    2. 验证镜像存在
    3. Kubernetes部署该镜像
    4. 等待Pod运行
  断言:
    - 镜像可用
    - Pod成功运行

场景2: 多容器协作
  目标: 测试容器间通信
  步骤:
    1. 创建网络
    2. 创建容器A(nginx)
    3. 创建容器B(curl)
    4. 容器B访问容器A
  断言:
    - 网络连通
    - 通信成功

场景3: 数据持久化流程
  目标: 测试完整数据流
  步骤:
    1. 创建卷
    2. 容器写入数据
    3. 停止并删除容器
    4. 新容器读取数据
  断言:
    - 数据持久化
    - 数据完整性

场景4: 应用编排
  目标: 测试多组件应用
  步骤:
    1. 部署数据库
    2. 部署应用
    3. 部署前端
    4. 验证整体功能
  断言:
    - 所有组件运行
    - 服务间通信正常

场景5: 配置热更新
  目标: 测试配置动态更新
  步骤:
    1. 部署应用
    2. 更新ConfigMap
    3. 重启应用
    4. 验证新配置生效
  断言:
    - 配置更新成功
    - 应用使用新配置
```

---

## 使用说明

### 快速开始

#### 1. 环境准备

```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo systemctl start docker

# 安装Kubernetes (minikube)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube start

# 安装etcd
ETCD_VER=v3.5.10
curl -L https://github.com/etcd-io/etcd/releases/download/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz | tar xzf -
sudo mv etcd-${ETCD_VER}-linux-amd64/etcd* /usr/local/bin/
etcd --version
```

#### 2. 运行测试

```bash
# 克隆项目
cd tools/api_testing/scripts

# 安装Go依赖
make deps

# 运行所有测试
make test

# 运行特定测试
make test-docker      # Docker API测试
make test-k8s         # Kubernetes API测试
make test-etcd        # etcd API测试
make test-integration # 集成测试

# 生成测试报告
make report

# 查看覆盖率
make coverage
```

#### 3. 查看结果

```bash
# 测试输出
cat test_results/all_tests_output.txt

# HTML覆盖率报告
open test_results/coverage.html

# JSON测试报告
cat test_results/json_test_output.json
```

### 编写新测试

#### 示例: 添加Docker API测试

```go
// 在docker_api_test.go中添加新测试
func (s *DockerAPITestSuite) TestNew_MyFeature() {
    color.Cyan("\n新测试: 我的功能")

    // 1. 使用测试数据工厂
    config := s.factory.CreateDockerContainerConfig(
        "my-image:latest",
        WithContainerPorts("8080/tcp"),
    )

    // 2. 执行操作
    container, err := s.cli.ContainerCreate(s.ctx, config, nil, nil, nil,
        s.factory.GenerateTestName("test"))
    s.Require().NoError(err)

    // 3. 使用测试工具验证
    err = s.utils.WaitForContainerRunning(s.ctx, s.cli, container.ID, 30*time.Second)
    s.Require().NoError(err)

    // 4. 清理
    defer s.cli.ContainerRemove(s.ctx, container.ID, types.ContainerRemoveOptions{Force: true})

    color.Green("✅ 测试通过")
}
```

### 调试技巧

```bash
# 1. 详细日志
go test -v -run TestDockerAPI/Test01_GetDockerVersion

# 2. 使用Delve调试
dlv test -- -test.run TestDockerAPI

# 3. 查看Docker日志
docker logs <container-id>

# 4. 检查Kubernetes事件
kubectl get events --namespace default

# 5. 查看etcd日志
etcdctl --endpoints=localhost:2379 get / --prefix
```

---

## 最佳实践

### 1. 测试设计原则

```yaml
FIRST原则:
  Fast (快速):
    - 单元测试应在秒级完成
    - 使用测试工具避免sleep
    - 并行运行独立测试

  Independent (独立):
    - 测试间无依赖
    - 使用随机数据避免冲突
    - 每个测试清理资源

  Repeatable (可重复):
    - 结果一致
    - 无时间依赖
    - 无外部依赖

  Self-validating (自验证):
    - 明确的断言
    - 清晰的错误信息
    - 完整的验证

  Timely (及时):
    - 测试驱动开发
    - 持续集成
    - 快速反馈
```

### 2. 测试数据管理

```go
// ✅ 使用工厂生成唯一数据
name := factory.GenerateTestName("test") // test-abc123-1634567890

// ✅ 使用随机端口避免冲突
port := factory.RandomPort() // 10000-65535

// ❌ 不要硬编码
name := "test-container" // 可能冲突
port := 8080             // 可能被占用
```

### 3. 资源清理

```go
// ✅ 使用defer确保清理
func (s *TestSuite) TestExample() {
    container, err := createContainer()
    defer cleanup(container) // 确保清理

    // 测试逻辑...
}

// ✅ 使用标签批量清理
defer s.utils.CleanupDockerContainers(ctx, cli, "test")
```

### 4. 错误处理

```go
// ✅ 使用Require在关键步骤
container, err := createContainer()
s.Require().NoError(err, "容器创建失败")

// ✅ 使用Assert在非关键步骤
stats, err := getStats()
assert.NoError(s.T(), err, "统计信息获取失败")
// 测试继续执行
```

### 5. 性能测试

```go
// ✅ 使用工具进行基准测试
result := s.utils.Benchmark(100, func() error {
    return apiCall()
})

// 验证性能要求
s.Require().True(result.AverageDuration < time.Millisecond*100)
s.Require().Zero(result.ErrorCount)
```

---

## 总结

### API标准覆盖

```yaml
✅ Docker API:
  - 20个测试用例
  - RESTful + Unix Socket
  - 完整生命周期覆盖

✅ Kubernetes API:
  - 17个测试用例
  - RESTful + gRPC
  - 核心资源覆盖

✅ etcd API:
  - 14个测试用例
  - gRPC
  - KV/Watch/Lease覆盖

✅ 集成测试:
  - 5个测试场景
  - 跨系统协作
  - 完整工作流
```

### 测试价值

```yaml
功能保证:
  ✅ API正确性验证
  ✅ 向后兼容性检查
  ✅ 错误处理验证

性能保证:
  ✅ 响应时间测试
  ✅ 并发能力测试
  ✅ 资源使用监控

质量保证:
  ✅ 100%测试覆盖
  ✅ 自动化回归测试
  ✅ 持续集成支持
```

---

**📖 相关文档:**

- [TEST_COMPREHENSIVE_GUIDE.md](./scripts/TEST_COMPREHENSIVE_GUIDE.md) - 完整测试指南
- [INTEGRATION_EXAMPLES.md](./scripts/INTEGRATION_EXAMPLES.md) - 集成示例
- [README.md](./README.md) - 快速开始
