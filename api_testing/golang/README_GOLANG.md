# Golang API 测试套件

> **语言**: Go 1.21+  
> **测试框架**: testing, testify/suite  
> **文档版本**: v1.0  
> **最后更新**: 2025年10月23日

---

## 📋 目录

- [Golang API 测试套件](#golang-api-测试套件)
  - [📋 目录](#-目录)
  - [概述](#概述)
    - [特性](#特性)
  - [目录结构](#目录结构)
  - [快速开始](#快速开始)
    - [1. 安装依赖](#1-安装依赖)
    - [2. 验证环境](#2-验证环境)
    - [3. 运行测试](#3-运行测试)
  - [测试分类](#测试分类)
    - [Docker API 测试](#docker-api-测试)
    - [Kubernetes API 测试](#kubernetes-api-测试)
    - [etcd API 测试](#etcd-api-测试)
    - [集成测试](#集成测试)
  - [运行测试](#运行测试)
    - [基本命令](#基本命令)
    - [使用测试工厂和工具](#使用测试工厂和工具)
  - [Makefile命令](#makefile命令)
  - [最佳实践](#最佳实践)
    - [1. 使用testify/suite进行结构化测试](#1-使用testifysuite进行结构化测试)
    - [2. 使用context进行超时控制](#2-使用context进行超时控制)
    - [3. 使用defer确保资源清理](#3-使用defer确保资源清理)
    - [4. 利用goroutine进行并发测试](#4-利用goroutine进行并发测试)
    - [5. 使用表驱动测试](#5-使用表驱动测试)
  - [故障排除](#故障排除)
    - [常见问题](#常见问题)
      - [1. 依赖下载失败](#1-依赖下载失败)
      - [2. Docker连接失败](#2-docker连接失败)
      - [3. Kubernetes认证失败](#3-kubernetes认证失败)
      - [4. etcd连接超时](#4-etcd连接超时)
      - [5. 测试超时](#5-测试超时)
  - [性能优化](#性能优化)
    - [1. 并行测试](#1-并行测试)
    - [2. 缓存测试结果](#2-缓存测试结果)
    - [3. 跳过长时间测试](#3-跳过长时间测试)
  - [相关文档](#相关文档)
  - [支持](#支持)

---

## 概述

本目录包含完整的Golang API测试套件,使用Go原生测试框架和testify/suite,提供高性能的API测试能力。

### 特性

- ✅ **容器化测试**: Docker API、Kubernetes API、etcd API
- ✅ **集成测试**: 跨系统集成测试
- ✅ **并发测试**: 利用goroutine实现并发测试
- ✅ **测试工厂**: 标准化测试数据生成
- ✅ **测试工具**: 丰富的测试辅助函数
- ✅ **报告生成**: HTML、JSON、Markdown多格式报告

---

## 目录结构

```
golang/
├── 📁 pkg/                        # Go包目录
│   ├── clients/                   # API客户端封装
│   ├── factory/                   # 测试数据工厂
│   │   └── test_factory.go
│   ├── utils/                     # 工具函数
│   │   └── test_utils.go
│   └── reporter/                  # 报告生成器
│       └── test_report.go
│
├── 📁 tests/                      # 测试目录
│   ├── docker/                    # Docker API测试
│   │   └── docker_api_test.go
│   ├── kubernetes/                # Kubernetes API测试
│   │   └── kubernetes_api_test.go
│   ├── etcd/                      # etcd API测试
│   │   └── etcd_api_test.go
│   └── integration/               # 集成测试
│       ├── integration_test.go
│       └── example_integrated_test.go
│
├── 📁 cmd/                        # 命令行工具
│   ├── run-tests/                 # 测试运行器
│   └── report-gen/                # 报告生成器
│
├── 📁 config/                     # 配置文件
│
├── 📁 examples/                   # 示例代码
│
├── go.mod                         # Go模块文件
├── go.sum                         # Go模块校验文件
└── Makefile                       # 构建和测试自动化
```

---

## 快速开始

### 1. 安装依赖

```bash
cd golang
go mod download
```

### 2. 验证环境

```bash
# 检查Go版本
go version  # 需要 Go 1.21+

# 检查Docker
docker ps

# 检查Kubernetes
kubectl cluster-info

# 检查etcd (如果需要)
etcdctl version
```

### 3. 运行测试

```bash
# 使用Makefile (推荐)
make test

# 使用go test
go test ./tests/...

# 详细输出
go test -v ./tests/...
```

---

## 测试分类

### Docker API 测试

```bash
# 使用Makefile
make test-docker

# 使用go test
go test -v ./tests/docker/
```

**测试覆盖**:

- 容器生命周期管理
- 镜像管理
- 网络管理
- 卷管理
- 并发操作测试

### Kubernetes API 测试

```bash
# 使用Makefile
make test-kubernetes

# 使用go test
go test -v ./tests/kubernetes/
```

**测试覆盖**:

- Pod管理
- Deployment管理
- Service管理
- ConfigMap/Secret管理
- 批量操作

### etcd API 测试

```bash
# 使用Makefile
make test-etcd

# 使用go test
go test -v ./tests/etcd/
```

**测试覆盖**:

- KV操作 (Get, Put, Delete)
- Watch机制
- Lease管理
- 事务操作
- 集群管理

### 集成测试

```bash
# 使用Makefile
make test-integration

# 使用go test
go test -v ./tests/integration/
```

**测试覆盖**:

- Docker + Kubernetes集成
- etcd + Kubernetes配置同步
- 跨系统数据一致性验证

---

## 运行测试

### 基本命令

```bash
# 运行所有测试
go test ./tests/...

# 详细输出
go test -v ./tests/...

# 显示覆盖率
go test -cover ./tests/...

# 生成覆盖率报告
go test -coverprofile=coverage.out ./tests/...
go tool cover -html=coverage.out

# 运行特定测试
go test -v ./tests/docker/ -run TestDockerAPI

# 并行运行
go test -v -parallel 4 ./tests/...

# 运行基准测试
go test -v -bench=. ./tests/...

# 设置超时
go test -v -timeout 10m ./tests/...
```

### 使用测试工厂和工具

```go
package test

import (
    "testing"
    "github.com/stretchr/testify/suite"
    "your-module/pkg/factory"
    "your-module/pkg/utils"
)

type MyTestSuite struct {
    suite.Suite
    factory *factory.TestDataFactory
    utils   *utils.TestUtils
}

func (suite *MyTestSuite) SetupTest() {
    suite.factory = factory.NewTestDataFactory()
    suite.utils = utils.NewTestUtils()
}

func (suite *MyTestSuite) TestExample() {
    // 使用工厂生成测试数据
    config := suite.factory.GenerateContainerConfig("nginx", "latest")
    
    // 使用工具函数
    suite.utils.WaitForCondition(func() bool {
        return true
    }, 10)
}

func TestMyTestSuite(t *testing.T) {
    suite.Run(t, new(MyTestSuite))
}
```

---

## Makefile命令

```bash
# 测试相关
make test               # 运行所有测试
make test-docker        # 运行Docker测试
make test-kubernetes    # 运行Kubernetes测试
make test-etcd          # 运行etcd测试
make test-integration   # 运行集成测试

# 覆盖率相关
make coverage           # 生成覆盖率报告
make coverage-html      # 生成HTML覆盖率报告

# 报告生成
make report             # 生成测试报告 (HTML + JSON + Markdown)
make report-html        # 生成HTML报告
make report-json        # 生成JSON报告
make report-markdown    # 生成Markdown报告

# 代码质量
make lint               # 运行代码检查
make fmt                # 格式化代码
make vet                # 运行go vet

# 构建和清理
make build              # 构建所有命令行工具
make clean              # 清理生成的文件

# 依赖管理
make deps               # 下载依赖
make deps-update        # 更新依赖

# 帮助
make help               # 显示所有可用命令
```

---

## 最佳实践

### 1. 使用testify/suite进行结构化测试

```go
type DockerTestSuite struct {
    suite.Suite
    client *client.Client
}

func (suite *DockerTestSuite) SetupSuite() {
    // 套件级别的初始化
}

func (suite *DockerTestSuite) SetupTest() {
    // 每个测试前的初始化
}

func (suite *DockerTestSuite) TearDownTest() {
    // 每个测试后的清理
}

func (suite *DockerTestSuite) TestExample() {
    // 测试逻辑
    suite.Assert().NotNil(suite.client)
}
```

### 2. 使用context进行超时控制

```go
func (suite *DockerTestSuite) TestWithTimeout() {
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    
    container, err := suite.client.ContainerCreate(ctx, ...)
    suite.Require().NoError(err)
}
```

### 3. 使用defer确保资源清理

```go
func (suite *DockerTestSuite) TestWithCleanup() {
    container, err := suite.client.ContainerCreate(ctx, ...)
    suite.Require().NoError(err)
    
    defer func() {
        suite.client.ContainerRemove(ctx, container.ID, types.ContainerRemoveOptions{Force: true})
    }()
    
    // 测试逻辑
}
```

### 4. 利用goroutine进行并发测试

```go
func (suite *DockerTestSuite) TestConcurrent() {
    var wg sync.WaitGroup
    results := make(chan error, 10)
    
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            err := suite.doSomething(id)
            results <- err
        }(i)
    }
    
    wg.Wait()
    close(results)
    
    for err := range results {
        suite.Assert().NoError(err)
    }
}
```

### 5. 使用表驱动测试

```go
func (suite *DockerTestSuite) TestTableDriven() {
    tests := []struct {
        name    string
        image   string
        wantErr bool
    }{
        {"valid nginx", "nginx:latest", false},
        {"valid alpine", "alpine:latest", false},
        {"invalid image", "nonexistent:tag", true},
    }
    
    for _, tt := range tests {
        suite.Run(tt.name, func() {
            _, err := suite.pullImage(tt.image)
            if tt.wantErr {
                suite.Assert().Error(err)
            } else {
                suite.Assert().NoError(err)
            }
        })
    }
}
```

---

## 故障排除

### 常见问题

#### 1. 依赖下载失败

**问题**: `go: cannot find module providing package`

**解决方案**:

```bash
# 清理模块缓存
go clean -modcache

# 重新下载依赖
go mod download

# 使用国内代理
export GOPROXY=https://goproxy.cn,direct
go mod download
```

#### 2. Docker连接失败

**问题**: `Cannot connect to the Docker daemon`

**解决方案**:

```bash
# 检查Docker服务
sudo systemctl status docker

# 设置环境变量
export DOCKER_HOST="unix:///var/run/docker.sock"

# 在Go代码中使用
client, err := client.NewClientWithOpts(
    client.FromEnv,
    client.WithAPIVersionNegotiation(),
)
```

#### 3. Kubernetes认证失败

**问题**: `Unable to connect to the server`

**解决方案**:

```bash
# 检查kubeconfig
kubectl config view

# 在Go代码中使用
config, err := clientcmd.BuildConfigFromFlags("", "/path/to/kubeconfig")
clientset, err := kubernetes.NewForConfig(config)
```

#### 4. etcd连接超时

**问题**: `context deadline exceeded`

**解决方案**:

```go
// 增加超时时间
cli, err := clientv3.New(clientv3.Config{
    Endpoints:   []string{"localhost:2379"},
    DialTimeout: 30 * time.Second,
})

// 在操作中使用context
ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
defer cancel()
```

#### 5. 测试超时

**问题**: `test timed out after 10m0s`

**解决方案**:

```bash
# 增加超时时间
go test -v -timeout 30m ./tests/...

# 在Makefile中设置
TIMEOUT ?= 30m
test:
    go test -v -timeout $(TIMEOUT) ./tests/...
```

---

## 性能优化

### 1. 并行测试

```bash
# 设置并行数
go test -v -parallel 8 ./tests/...
```

### 2. 缓存测试结果

```bash
# Go会自动缓存测试结果
go test ./tests/...  # 第一次运行
go test ./tests/...  # 第二次会使用缓存

# 强制重新运行
go test -count=1 ./tests/...
```

### 3. 跳过长时间测试

```go
func TestLongRunning(t *testing.T) {
    if testing.Short() {
        t.Skip("跳过长时间测试")
    }
    // 测试逻辑
}
```

```bash
# 跳过长时间测试
go test -short ./tests/...
```

---

## 相关文档

- **[主文档](../docs/INDEX.md)** - 完整文档导航
- **[快速开始](../QUICKSTART.md)** - 快速入门指南
- **[API标准](../docs/00_API标准梳理与测试指南.md)** - API标准详解
- **[常见问题](../docs/FAQ.md)** - 常见问题解答
- **[贡献指南](../docs/CONTRIBUTING.md)** - 如何贡献代码

---

## 支持

如有问题或建议,请:

1. 查阅 [FAQ文档](../docs/FAQ.md)
2. 查看 [快速参考](../docs/QUICK_REFERENCE.md)
3. 提交 Issue

---

**最后更新**: 2025年10月23日  
**维护团队**: API测试团队  
**许可证**: MIT
