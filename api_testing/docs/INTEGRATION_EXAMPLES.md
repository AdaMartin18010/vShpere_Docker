# 功能集成使用示例

本文档展示如何在实际测试中集成使用**测试数据工厂**(`test_factory.go`)和**测试工具**(`test_utils.go`)。

## 📚 目录

- [概述](#概述)
- [测试数据工厂集成](#测试数据工厂集成)
- [测试工具集成](#测试工具集成)
- [完整示例](#完整示例)
- [最佳实践](#最佳实践)

---

## 概述

### 为什么需要集成？

```
传统测试方式的问题:
❌ 大量重复的配置代码
❌ 手动管理资源清理
❌ 缺乏统一的测试数据生成
❌ 没有重试和等待机制
❌ 性能测试需要自己实现

集成后的优势:
✅ 工厂模式生成测试数据
✅ 自动化资源清理
✅ 统一的工具函数库
✅ 内置重试和等待机制
✅ 完整的性能测试支持
```

### 核心组件

```go
// 1. 测试数据工厂 (test_factory.go)
factory := NewTestDataFactory()
config := factory.CreateDockerContainerConfig("nginx:alpine",
    WithContainerPorts("80/tcp"),
    WithContainerEnv("ENV=test"),
)

// 2. 测试工具 (test_utils.go)
utils := NewTestUtils()
err := utils.WaitForContainerRunning(ctx, cli, containerID, 30*time.Second)
err = utils.Retry(3, time.Second, func() error { ... })
defer utils.CleanupDockerContainers(ctx, cli, "test")
```

---

## 测试数据工厂集成

### 示例1: 容器配置生成

**传统方式** (❌ 不推荐):

```go
func (s *TestSuite) TestCreateContainer() {
    // 大量重复的配置代码
    config := &container.Config{
        Image: "nginx:alpine",
        Cmd: []string{"sh", "-c", "nginx -g 'daemon off;'"},
        Env: []string{"ENV=test", "DEBUG=true"},
        ExposedPorts: nat.PortSet{
            "80/tcp": struct{}{},
        },
        Labels: map[string]string{
            "test": "api-test",
            "created_by": "manual",
        },
    }
    
    hostConfig := &container.HostConfig{
        PortBindings: nat.PortMap{
            "80/tcp": []nat.PortBinding{
                {HostPort: "8080"},
            },
        },
    }
    
    container, err := s.cli.ContainerCreate(ctx, config, hostConfig, nil, nil, "test-container")
    // ...
}
```

**工厂模式** (✅ 推荐):

```go
func (s *TestSuite) TestCreateContainer() {
    // ✅ 使用工厂生成配置（简洁清晰）
    config := s.factory.CreateDockerContainerConfig(
        "nginx:alpine",
        WithContainerCmd("sh", "-c", "nginx -g 'daemon off;'"),
        WithContainerEnv("ENV=test", "DEBUG=true"),
        WithContainerPorts("80/tcp"),
        WithContainerLabels(map[string]string{"test": "api"}),
    )
    
    hostConfig := s.factory.CreateDockerHostConfig(
        WithPortBinding("80/tcp", "8080"),
    )
    
    // ✅ 使用工厂生成随机名称
    containerName := s.factory.GenerateTestName("container")
    
    container, err := s.cli.ContainerCreate(ctx, config, hostConfig, nil, nil, containerName)
    // ...
}
```

### 示例2: 随机数据生成

```go
func (s *TestSuite) TestWithRandomData() {
    // ✅ 生成随机测试数据
    containerName := s.factory.GenerateTestName("test")    // test-abc12345-1634567890
    randomPort := s.factory.RandomPort()                   // 随机端口 10000-65535
    randomIP := s.factory.RandomIPv4()                     // 随机IP 192.168.x.x
    randomString := s.factory.RandomString(8)              // 随机字符串
    
    config := s.factory.CreateDockerContainerConfig(
        "nginx:alpine",
        WithContainerPorts(fmt.Sprintf("%d/tcp", randomPort)),
        WithContainerEnv(fmt.Sprintf("ID=%s", randomString)),
    )
    
    // 使用随机数据创建容器...
}
```

### 示例3: 使用预定义数据集

```go
func (s *TestSuite) TestWithDatasets() {
    // ✅ 使用工厂的数据集
    datasets := s.factory.CreateTestDatasets()
    
    for _, dataset := range datasets {
        switch dataset.Name {
        case "容器镜像列表":
            images := dataset.Data["images"].([]string)
            // 使用镜像列表创建多个容器
            for _, img := range images {
                config := s.factory.CreateDockerContainerConfig(img)
                // ...
            }
            
        case "测试端口映射":
            mappings := dataset.Data["mappings"].(map[string]string)
            // 使用端口映射配置
            
        case "环境变量模板":
            envs := dataset.Data["common"].(map[string]string)
            // 使用环境变量模板
        }
    }
}
```

---

## 测试工具集成

### 示例1: 等待机制

**传统方式** (❌ 不推荐):

```go
func (s *TestSuite) TestStartContainer() {
    // 启动容器
    err := s.cli.ContainerStart(ctx, containerID, types.ContainerStartOptions{})
    s.Require().NoError(err)
    
    // ❌ 硬编码sleep等待
    time.Sleep(5 * time.Second)
    
    // ❌ 手动轮询检查状态
    for i := 0; i < 10; i++ {
        inspect, err := s.cli.ContainerInspect(ctx, containerID)
        if err == nil && inspect.State.Running {
            break
        }
        time.Sleep(time.Second)
    }
}
```

**工具集成** (✅ 推荐):

```go
func (s *TestSuite) TestStartContainer() {
    // 启动容器
    err := s.cli.ContainerStart(ctx, containerID, types.ContainerStartOptions{})
    s.Require().NoError(err)
    
    // ✅ 使用工具等待容器运行（带超时）
    err = s.utils.WaitForContainerRunning(ctx, s.cli, containerID, 30*time.Second)
    s.Require().NoError(err)
    
    // ✅ 使用工具断言容器状态
    err = s.utils.AssertContainerRunning(ctx, s.cli, containerID)
    s.Require().NoError(err)
}
```

### 示例2: 重试机制

```go
func (s *TestSuite) TestWithRetry() {
    // ✅ 使用工具的重试机制（3次，间隔1秒）
    err := s.utils.Retry(3, time.Second, func() error {
        _, err := s.cli.ContainerCreate(ctx, config, hostConfig, nil, nil, name)
        return err
    })
    s.Require().NoError(err)
}
```

### 示例3: 性能测试

```go
func (s *TestSuite) TestPerformance() {
    // ✅ 使用工具进行性能测试（100次操作）
    result := s.utils.Benchmark(100, func() error {
        _, err := s.cli.Ping(ctx)
        return err
    })
    
    // ✅ 使用工具格式化结果
    fmt.Println(s.utils.FormatBenchmarkResult(result))
    /*
    性能测试结果:
      操作次数: 100
      总耗时: 1.234s
      平均耗时: 12.34ms
      最小耗时: 8.12ms
      最大耗时: 25.67ms
      错误数: 0
      成功率: 100.00%
    */
    
    // 验证性能指标
    s.Require().Equal(100, result.Operations)
    s.Require().Zero(result.ErrorCount)
    s.Require().True(result.AverageDuration < time.Second)
}
```

### 示例4: 资源清理

```go
func (s *TestSuite) SetupSuite() {
    // 初始化...
}

func (s *TestSuite) TearDownSuite() {
    // ✅ 使用工具自动清理所有测试资源
    s.utils.CleanupDockerContainers(ctx, s.cli, "test")
    s.utils.CleanupDockerNetworks(ctx, s.cli, "test")
    s.utils.CleanupDockerVolumes(ctx, s.cli, "test")
}

func (s *TestSuite) TestWithAutoCleanup() {
    // ✅ 单个测试的资源清理
    container, err := s.cli.ContainerCreate(...)
    s.Require().NoError(err)
    
    // 确保测试结束后清理
    defer s.cli.ContainerRemove(ctx, container.ID, types.ContainerRemoveOptions{Force: true})
    
    // 测试逻辑...
}
```

### 示例5: 时间测量

```go
func (s *TestSuite) TestWithTiming() {
    // ✅ 使用工具测量操作耗时
    duration, err := s.utils.MeasureTime(func() error {
        return s.utils.WaitForContainerRunning(ctx, s.cli, containerID, 30*time.Second)
    })
    
    s.Require().NoError(err)
    color.Green("容器启动耗时: %v", duration)
    
    // 验证性能要求
    s.Require().True(duration < 5*time.Second, "容器启动应该在5秒内完成")
}
```

---

## 完整示例

### 示例: 完整的容器生命周期测试（集成所有功能）

```go
func (s *DockerAPITestSuite) TestCompleteLifecycleWithIntegration() {
    color.Cyan("\n完整示例: 集成测试数据工厂和测试工具")
    
    // ===== 步骤1: 使用工厂创建网络 =====
    color.Yellow("步骤1: 创建测试网络")
    networkConfig := s.factory.CreateDockerNetworkConfig("bridge")
    networkName := s.factory.GenerateTestName("test-network")
    
    networkResp, err := s.cli.NetworkCreate(s.ctx, networkName, networkConfig)
    s.Require().NoError(err)
    defer s.cli.NetworkRemove(s.ctx, networkResp.ID)
    color.Green("✅ 网络创建成功: %s", networkResp.ID[:12])
    
    // ===== 步骤2: 使用工厂创建卷 =====
    color.Yellow("步骤2: 创建测试卷")
    volumeConfig := s.factory.CreateDockerVolumeConfig()
    volumeName := s.factory.GenerateTestName("test-volume")
    
    volumeResp, err := s.cli.VolumeCreate(s.ctx, volumeConfig)
    s.Require().NoError(err)
    defer s.cli.VolumeRemove(s.ctx, volumeResp.Name, false)
    color.Green("✅ 卷创建成功: %s", volumeResp.Name)
    
    // ===== 步骤3: 使用工厂创建容器配置 =====
    color.Yellow("步骤3: 创建容器配置")
    containerConfig := s.factory.CreateDockerContainerConfig(
        "nginx:alpine",
        WithContainerPorts("80/tcp"),
        WithContainerEnv("ENV=test", "DEBUG=true"),
        WithContainerLabels(map[string]string{
            "test": "integration",
            "lifecycle": "complete",
        }),
    )
    
    hostConfig := s.factory.CreateDockerHostConfig(
        WithNetworkMode(networkResp.ID),
        WithVolumeBinding(fmt.Sprintf("%s:/data", volumeResp.Name)),
        WithPortBinding("80/tcp", fmt.Sprintf("%d", s.factory.RandomPort())),
    )
    
    containerName := s.factory.GenerateTestName("test-container")
    color.Green("✅ 容器配置创建成功: %s", containerName)
    
    // ===== 步骤4: 创建并启动容器 =====
    color.Yellow("步骤4: 创建并启动容器")
    
    // 使用重试机制创建容器
    var containerResp container.CreateResponse
    err = s.utils.Retry(3, time.Second, func() error {
        var err error
        containerResp, err = s.cli.ContainerCreate(
            s.ctx, containerConfig, hostConfig, nil, nil, containerName)
        return err
    })
    s.Require().NoError(err)
    defer s.cli.ContainerRemove(s.ctx, containerResp.ID, types.ContainerRemoveOptions{Force: true})
    color.Green("✅ 容器创建成功: %s", containerResp.ID[:12])
    
    // 启动容器
    err = s.cli.ContainerStart(s.ctx, containerResp.ID, types.ContainerStartOptions{})
    s.Require().NoError(err)
    
    // ===== 步骤5: 使用工具等待容器运行 =====
    color.Yellow("步骤5: 等待容器运行")
    duration, err := s.utils.MeasureTime(func() error {
        return s.utils.WaitForContainerRunning(
            s.ctx, s.cli, containerResp.ID, 30*time.Second)
    })
    s.Require().NoError(err)
    color.Green("✅ 容器运行成功 (耗时: %v)", duration)
    
    // ===== 步骤6: 使用工具验证容器状态 =====
    color.Yellow("步骤6: 验证容器状态")
    err = s.utils.AssertContainerExists(s.ctx, s.cli, containerResp.ID)
    s.Require().NoError(err)
    
    err = s.utils.AssertContainerRunning(s.ctx, s.cli, containerResp.ID)
    s.Require().NoError(err)
    color.Green("✅ 容器状态验证通过")
    
    // ===== 步骤7: 性能测试 =====
    color.Yellow("步骤7: 容器操作性能测试")
    result := s.utils.Benchmark(10, func() error {
        _, err := s.cli.ContainerInspect(s.ctx, containerResp.ID)
        return err
    })
    color.Green("✅ 性能测试完成:")
    fmt.Printf("   平均耗时: %v, 成功率: %.2f%%\n",
        result.AverageDuration,
        float64(result.Operations-result.ErrorCount)/float64(result.Operations)*100)
    
    // ===== 步骤8: 停止容器 =====
    color.Yellow("步骤8: 停止容器")
    timeout := 10
    err = s.cli.ContainerStop(s.ctx, containerResp.ID, &timeout)
    s.Require().NoError(err)
    
    // 使用工具等待容器停止
    err = s.utils.WaitForContainerStopped(s.ctx, s.cli, containerResp.ID, 15*time.Second)
    s.Require().NoError(err)
    color.Green("✅ 容器停止成功")
    
    // ===== 步骤9: 清理验证 =====
    color.Yellow("步骤9: 验证资源清理")
    // 资源会在defer中自动清理
    color.Green("✅ 所有资源将自动清理")
    
    color.Green("\n🎉 完整生命周期测试成功！")
}
```

---

## 最佳实践

### 1. 测试套件初始化

```go
type MyTestSuite struct {
    suite.Suite
    client  *client.Client
    factory *TestDataFactory  // ✅ 添加工厂
    utils   *TestUtils        // ✅ 添加工具
    ctx     context.Context
}

func (s *MyTestSuite) SetupSuite() {
    s.ctx = context.Background()
    s.client = createClient()
    
    // ✅ 初始化工厂和工具
    s.factory = NewTestDataFactory()
    s.utils = NewTestUtils()
}

func (s *MyTestSuite) TearDownSuite() {
    // ✅ 使用工具清理所有资源
    s.utils.CleanupDockerContainers(s.ctx, s.client, "test")
    s.utils.CleanupDockerNetworks(s.ctx, s.client, "test")
    s.utils.CleanupDockerVolumes(s.ctx, s.client, "test")
    
    s.client.Close()
}
```

### 2. 测试数据生成

```go
func (s *MyTestSuite) TestExample() {
    // ✅ 使用工厂生成唯一的测试数据
    containerName := s.factory.GenerateTestName("test")
    
    // ✅ 使用工厂链式调用创建配置
    config := s.factory.CreateDockerContainerConfig(
        "nginx:alpine",
        WithContainerPorts("80/tcp"),
        WithContainerLabels(map[string]string{"test": "example"}),
    )
    
    // ✅ 使用工厂生成随机端口
    hostConfig := s.factory.CreateDockerHostConfig(
        WithPortBinding("80/tcp", fmt.Sprintf("%d", s.factory.RandomPort())),
    )
}
```

### 3. 错误处理和重试

```go
func (s *MyTestSuite) TestExample() {
    // ✅ 使用工具的重试机制处理临时失败
    err := s.utils.Retry(3, time.Second, func() error {
        return performOperation()
    })
    s.Require().NoError(err)
}
```

### 4. 资源等待和验证

```go
func (s *MyTestSuite) TestExample() {
    // 创建并启动容器
    container, _ := s.client.ContainerCreate(...)
    s.client.ContainerStart(...)
    
    // ✅ 使用工具等待（不要用sleep）
    err := s.utils.WaitForContainerRunning(s.ctx, s.client, container.ID, 30*time.Second)
    s.Require().NoError(err)
    
    // ✅ 使用工具验证状态
    err = s.utils.AssertContainerRunning(s.ctx, s.client, container.ID)
    s.Require().NoError(err)
}
```

### 5. 性能测试

```go
func (s *MyTestSuite) TestPerformance() {
    // ✅ 使用工具进行性能测试
    result := s.utils.Benchmark(100, func() error {
        return performOperation()
    })
    
    // ✅ 使用工具格式化结果
    fmt.Println(s.utils.FormatBenchmarkResult(result))
    
    // 验证性能要求
    s.Require().True(result.AverageDuration < time.Millisecond*100)
    s.Require().Zero(result.ErrorCount)
}
```

---

## 运行集成示例

```bash
# 运行完整的集成示例测试
cd tools/api_testing/scripts
go test -v -run TestIntegratedExample

# 运行特定的集成示例
go test -v -run TestIntegratedExample/TestExample01_UsingFactoryToCreateContainer
go test -v -run TestIntegratedExample/TestExample04_CompleteWorkflow

# 查看详细输出（彩色日志）
go test -v -run TestIntegratedExample | less -R
```

---

## 总结

### 集成前 vs 集成后

| 方面 | 集成前 ❌ | 集成后 ✅ |
|------|----------|----------|
| 代码行数 | 50+ 行 | 20 行 |
| 配置重复 | 每次都写 | 工厂生成 |
| 资源清理 | 手动管理 | 自动清理 |
| 等待机制 | sleep | 智能等待 |
| 重试机制 | 自己实现 | 内置支持 |
| 性能测试 | 手动统计 | 自动分析 |
| 随机数据 | 硬编码 | 工厂生成 |
| 可维护性 | 低 | 高 |

### 核心优势

```yaml
✅ 代码复用
  - 工厂模式避免重复配置
  - 统一的工具函数库
  - 可扩展的架构

✅ 提高效率
  - 减少70%+的代码量
  - 快速生成测试数据
  - 自动化资源管理

✅ 增强可靠性
  - 智能等待机制
  - 内置重试逻辑
  - 完整的状态验证

✅ 改善可维护性
  - 统一的代码风格
  - 清晰的函数命名
  - 完整的文档支持
```

---

**📖 更多信息请参考:**

- [test_factory.go](./test_factory.go) - 测试数据工厂源码
- [test_utils.go](./test_utils.go) - 测试工具源码
- [example_integrated_test.go](./example_integrated_test.go) - 完整示例代码
- [TEST_COMPREHENSIVE_GUIDE.md](./TEST_COMPREHENSIVE_GUIDE.md) - 完整测试指南
