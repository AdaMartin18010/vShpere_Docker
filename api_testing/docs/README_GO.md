# Go API 测试套件

本目录包含使用Golang编写的API测试套件，提供与Python测试相同的功能覆盖。

## 📋 测试套件列表

### ✅ Docker API 测试

**文件**: `docker_api_test.go`

**测试用例** (20个):

```text
✅ Test01_GetDockerVersion      - 获取Docker版本
✅ Test02_GetDockerInfo          - 获取系统信息
✅ Test03_PingDocker             - Ping守护进程
✅ Test04_ListImages             - 列出镜像
✅ Test05_PullImage              - 拉取镜像
✅ Test06_InspectImage           - 查看镜像详情
✅ Test07_CreateContainer        - 创建容器
✅ Test08_StartContainer         - 启动容器
✅ Test09_InspectContainer       - 查看容器详情
✅ Test10_GetContainerLogs       - 获取容器日志
✅ Test11_GetContainerStats      - 获取容器统计
✅ Test12_ListContainers         - 列出容器
✅ Test13_CreateNetwork          - 创建网络
✅ Test14_InspectNetwork         - 查看网络详情
✅ Test15_CreateVolume           - 创建卷
✅ Test16_InspectVolume          - 查看卷详情
✅ Test17_StopContainer          - 停止容器
✅ Test18_RemoveContainer        - 删除容器
✅ Test19_RemoveNetwork          - 删除网络
✅ Test20_RemoveVolume           - 删除卷
```

### ✅ Kubernetes API 测试

**文件**: `kubernetes_api_test.go`

**测试用例** (17个):

```
✅ Test01_GetAPIVersions         - 获取API版本
✅ Test02_GetNodes               - 获取节点列表
✅ Test03_ListNamespaces         - 列出命名空间
✅ Test04_CreatePod              - 创建Pod
✅ Test05_GetPod                 - 获取Pod详情
✅ Test06_ListPods               - 列出Pods
✅ Test07_GetPodLogs             - 获取Pod日志
✅ Test08_CreateDeployment       - 创建Deployment
✅ Test09_GetDeployment          - 获取Deployment详情
✅ Test10_ScaleDeployment        - 扩缩容Deployment
✅ Test11_CreateService          - 创建Service
✅ Test12_GetService             - 获取Service详情
✅ Test13_CreateConfigMap        - 创建ConfigMap
✅ Test14_DeletePod              - 删除Pod
✅ Test15_DeleteService          - 删除Service
✅ Test16_DeleteDeployment       - 删除Deployment
✅ Test17_DeleteConfigMap        - 删除ConfigMap
```

### ✅ etcd API 测试

**文件**: `etcd_api_test.go`

**测试用例** (14个):

```
✅ Test01_GetStatus              - 获取etcd状态
✅ Test02_MemberList             - 列出集群成员
✅ Test03_PutKey                 - 存储键值对
✅ Test04_GetKey                 - 获取键值对
✅ Test05_GetKeyWithPrefix       - 按前缀获取
✅ Test06_LeaseGrant             - 创建租约
✅ Test07_PutKeyWithLease        - 存储带租约的键值对
✅ Test08_LeaseTimeToLive        - 获取租约信息
✅ Test09_LeaseKeepAlive         - 租约续约
✅ Test10_WatchKey               - 监听键变化
✅ Test11_Transaction            - 事务操作
✅ Test12_DeleteKey              - 删除键值对
✅ Test13_DeleteKeyWithPrefix    - 按前缀删除
✅ Test14_LeaseRevoke            - 撤销租约
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd tools/api_testing/scripts

# 初始化Go模块 (如果需要)
go mod download

# 或者安装特定依赖
go get github.com/docker/docker
go get k8s.io/client-go
go get go.etcd.io/etcd/client/v3
go get github.com/fatih/color
go get github.com/stretchr/testify
```

### 2. 运行测试

#### 运行所有Docker API测试

```bash
# 确保Docker守护进程正在运行
export DOCKER_HOST=tcp://localhost:2375  # 如果需要

# 运行测试
go test -v -run TestDockerAPI
```

#### 运行所有Kubernetes API测试

```bash
# 确保有有效的kubeconfig
export KUBECONFIG=~/.kube/config

# 运行测试
go test -v -run TestKubernetesAPI
```

#### 运行所有etcd API测试

```bash
# 确保etcd服务器正在运行
export ETCD_ENDPOINTS=localhost:2379

# 运行测试
go test -v -run TestEtcdAPI
```

#### 运行单个测试用例

```bash
# Docker: 只测试版本获取
go test -v -run TestDockerAPI/Test01_GetDockerVersion

# Kubernetes: 只测试Pod创建
go test -v -run TestKubernetesAPI/Test04_CreatePod

# etcd: 只测试键值对存取
go test -v -run TestEtcdAPI/Test03_PutKey
```

#### 运行所有测试

```bash
# 运行所有测试套件
go test -v ./...

# 带覆盖率
go test -v -cover ./...

# 生成覆盖率报告
go test -v -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html
```

### 3. 测试选项

```bash
# 详细输出
go test -v

# 显示覆盖率
go test -cover

# 并行运行
go test -parallel 4

# 设置超时
go test -timeout 30m

# 短测试模式 (跳过长测试)
go test -short

# 运行基准测试
go test -bench .

# 生成性能分析
go test -cpuprofile cpu.prof
go test -memprofile mem.prof
```

## 📊 测试框架

### 使用的库

```go
github.com/stretchr/testify/suite  // 测试套件框架
github.com/stretchr/testify/assert // 断言库
github.com/fatih/color             // 彩色输出
github.com/docker/docker           // Docker客户端
k8s.io/client-go                   // Kubernetes客户端
go.etcd.io/etcd/client/v3          // etcd v3客户端
```

### 测试套件结构

```go
type DockerAPITestSuite struct {
    suite.Suite
    cli         *client.Client
    ctx         context.Context
    containerID string
    // ...
}

func (s *DockerAPITestSuite) SetupSuite() {
    // 初始化客户端
}

func (s *DockerAPITestSuite) TearDownSuite() {
    // 清理资源
}

func (s *DockerAPITestSuite) Test01_GetDockerVersion() {
    // 测试用例
}
```

## 🔧 环境配置

### Docker

```bash
# Unix Socket (默认)
export DOCKER_HOST=unix:///var/run/docker.sock

# TCP
export DOCKER_HOST=tcp://localhost:2375

# TLS
export DOCKER_HOST=tcp://localhost:2376
export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH=/path/to/certs
```

### Kubernetes

```bash
# Kubeconfig路径
export KUBECONFIG=~/.kube/config

# 或者使用in-cluster配置 (Pod内)
# 自动从ServiceAccount读取
```

### etcd

```bash
# etcd端点
export ETCD_ENDPOINTS=localhost:2379

# 多端点
export ETCD_ENDPOINTS=etcd1:2379,etcd2:2379,etcd3:2379

# TLS认证 (如果需要)
export ETCD_CERT_FILE=/path/to/cert.pem
export ETCD_KEY_FILE=/path/to/key.pem
export ETCD_CA_FILE=/path/to/ca.pem
```

## 📝 测试输出示例

```
=== Docker API 测试套件初始化 ===

测试1: 获取Docker版本
✅ Docker版本获取成功:
  - Version: 24.0.7
  - API Version: 1.43
  - Go Version: go1.21.4
  - OS/Arch: linux/amd64

测试2: 获取Docker系统信息
✅ Docker系统信息获取成功:
  - Containers: 10 (Running: 3, Paused: 0, Stopped: 7)
  - Images: 25
  - Driver: overlay2
  - Memory: 16384 MB
  - CPUs: 8

...

PASS
ok      github.com/vsphere_docker/api_testing  25.432s
```

## 🎯 与Python测试的对比

| 特性 | Python | Go |
|------|--------|-----|
| **性能** | 较慢 | 非常快 ⚡ |
| **并发** | asyncio | 原生goroutine |
| **类型安全** | 动态类型 | 静态类型 ✅ |
| **依赖管理** | pip | go mod |
| **测试框架** | unittest | testify/suite |
| **编译** | 解释型 | 编译型 |
| **适用场景** | 快速开发 | 生产环境 |

## 🚀 性能优化

### 并行测试

```go
func (s *DockerAPITestSuite) Test01_GetDockerVersion() {
    s.T().Parallel() // 并行运行
    // ...
}
```

### 使用Table-Driven Tests

```go
func TestMultipleEndpoints(t *testing.T) {
    tests := []struct {
        name     string
        endpoint string
        expected string
    }{
        {"Local", "localhost:2379", ""},
        {"Remote", "remote:2379", ""},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // 测试逻辑
        })
    }
}
```

## 📖 最佳实践

1. **使用Context控制超时**

   ```go
   ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
   defer cancel()
   ```

2. **清理资源**

   ```go
   func (s *Suite) TearDownTest() {
       // 每个测试后清理
   }
   ```

3. **使用断言库**

   ```go
   assert.NoError(t, err)
   assert.Equal(t, expected, actual)
   assert.NotEmpty(t, result)
   ```

4. **彩色输出**

   ```go
   color.Green("✅ 测试通过")
   color.Red("❌ 测试失败")
   color.Yellow("⚠️ 警告")
   ```

## 🔍 调试

### 详细日志

```bash
# 启用详细输出
go test -v

# 显示测试日志
go test -v -test.v
```

### 使用Delve调试器

```bash
# 安装Delve
go install github.com/go-delve/delve/cmd/dlv@latest

# 调试测试
dlv test -- -test.run TestDockerAPI
```

## 📚 参考资源

- [Go Testing](https://golang.org/pkg/testing/)
- [Testify Documentation](https://github.com/stretchr/testify)
- [Docker Go SDK](https://docs.docker.com/engine/api/sdk/)
- [Kubernetes Go Client](https://github.com/kubernetes/client-go)
- [etcd Go Client](https://github.com/etcd-io/etcd/tree/main/client/v3)

## 💡 常见问题

### Q: 如何跳过某些测试?

```go
func (s *Suite) Test01_Skip() {
    if os.Getenv("SKIP_SLOW_TESTS") != "" {
        s.T().Skip("Skipping slow test")
    }
    // 测试代码
}
```

### Q: 如何设置测试超时?

```bash
go test -timeout 10m
```

### Q: 如何生成测试报告?

```bash
# JUnit格式
go test -v 2>&1 | go-junit-report > report.xml

# JSON格式
go test -json > report.json
```

---

**🎉 享受使用Go进行API测试！**
