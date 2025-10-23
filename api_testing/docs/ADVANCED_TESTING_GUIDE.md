# 🔬 高级测试指南

> **文档定位**: API测试的高级技术和最佳实践  
> **目标读者**: 高级测试工程师、QA架构师  
> **难度等级**: ⭐⭐⭐⭐⭐  
> **最后更新**: 2025年10月23日

---

## 📋 目录

- [🔬 高级测试指南](#-高级测试指南)
  - [📋 目录](#-目录)
  - [概述](#概述)
    - [为什么需要高级测试？](#为什么需要高级测试)
    - [测试金字塔 v2.0](#测试金字塔-v20)
  - [测试分类](#测试分类)
    - [1. 边界条件测试 (Boundary Testing)](#1-边界条件测试-boundary-testing)
    - [2. 错误处理测试 (Error Handling Testing)](#2-错误处理测试-error-handling-testing)
    - [3. 并发压力测试 (Concurrency \& Stress Testing)](#3-并发压力测试-concurrency--stress-testing)
    - [4. 性能基准测试 (Performance Benchmarking)](#4-性能基准测试-performance-benchmarking)
    - [5. 幂等性测试 (Idempotency Testing)](#5-幂等性测试-idempotency-testing)
    - [6. 状态机测试 (State Machine Testing)](#6-状态机测试-state-machine-testing)
    - [7. 资源限制测试 (Resource Limit Testing)](#7-资源限制测试-resource-limit-testing)
    - [8. 复杂场景测试 (Complex Scenario Testing)](#8-复杂场景测试-complex-scenario-testing)
  - [混沌工程 (Chaos Engineering)](#混沌工程-chaos-engineering)
    - [定义](#定义)
    - [混沌实验类型](#混沌实验类型)
      - [1. 资源耗尽](#1-资源耗尽)
      - [2. 网络延迟](#2-网络延迟)
      - [3. 随机容器终止](#3-随机容器终止)
  - [性能优化建议](#性能优化建议)
    - [1. 测试并行化](#1-测试并行化)
    - [2. 使用测试缓存](#2-使用测试缓存)
    - [3. 资源清理](#3-资源清理)
  - [最佳实践总结](#最佳实践总结)
    - [✅ DO (应该做)](#-do-应该做)
    - [❌ DON'T (不应该做)](#-dont-不应该做)
  - [相关文档](#相关文档)

---

## 概述

### 为什么需要高级测试？

基础测试只能验证**正常路径（Happy Path）**，而生产环境中：

- ✅ 70% 的问题发生在**边界条件**
- ✅ 20% 的问题发生在**并发竞争**
- ✅ 10% 的问题发生在**资源耗尽**

### 测试金字塔 v2.0

```
              /\
             /混\
            /沌工\
           /  程  \
          /--------\
         / 复杂场景 \
        /----------\
       /   并发测试  \
      /-------------\
     /   性能基准    \
    /---------------\
   /   边界条件测试   \
  /-----------------\
 /   错误处理测试    \
/-------------------\
     基础功能测试
```

---

## 测试分类

### 1. 边界条件测试 (Boundary Testing)

**定义**: 测试输入值的极限情况

**覆盖范围**:

- 空值、null、undefined
- 最小值、最大值
- 零值、负值
- 超长字符串
- 特殊字符

**示例场景**:

```go
// 测试空容器名
func TestBoundaryEmptyContainerName(t *testing.T) {
    _, err := cli.ContainerCreate(ctx, &container.Config{
        Image: "",  // 空镜像名
    }, nil, nil, nil, "")
    
    assert.Error(t, err, "空镜像名应该返回错误")
}

// 测试超长容器名
func TestBoundaryMaxContainerName(t *testing.T) {
    maxName := strings.Repeat("a", 255)    // 最大长度
    tooLong := strings.Repeat("a", 256)    // 超长
    
    // 测试最大长度（应该成功）
    _, err := cli.ContainerCreate(ctx, &container.Config{
        Image: "alpine",
    }, nil, nil, nil, maxName)
    assert.NoError(t, err)
    
    // 测试超长（应该失败）
    _, err = cli.ContainerCreate(ctx, &container.Config{
        Image: "alpine",
    }, nil, nil, nil, tooLong)
    assert.Error(t, err)
}
```

### 2. 错误处理测试 (Error Handling Testing)

**定义**: 验证系统对错误情况的处理

**覆盖范围**:

- 不存在的资源
- 非法参数
- 权限不足
- 网络超时
- 资源冲突

**示例场景**:

```python
def test_error_nonexistent_container(client):
    """测试操作不存在的容器"""
    with pytest.raises(docker.errors.NotFound):
        client.containers.get("nonexistent-id").start()
    
    with pytest.raises(docker.errors.NotFound):
        client.containers.get("nonexistent-id").stop()
    
    with pytest.raises(docker.errors.NotFound):
        client.containers.get("nonexistent-id").remove()

def test_error_network_timeout(client):
    """测试网络超时"""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("操作超时")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(1)  # 1秒超时
    
    try:
        # 执行可能超时的操作
        client.containers.list(all=True)
    except TimeoutError:
        pytest.fail("操作应该在1秒内完成")
    finally:
        signal.alarm(0)
```

### 3. 并发压力测试 (Concurrency & Stress Testing)

**定义**: 测试系统在高并发下的行为

**测试维度**:

- **并发度**: 同时执行的操作数
- **持续时间**: 压力测试的时间
- **成功率**: 成功操作的百分比
- **响应时间**: 平均响应时间

**示例场景**:

```go
func TestConcurrencyParallelCreation(t *testing.T) {
    concurrency := 50
    var wg sync.WaitGroup
    results := make(chan error, concurrency)
    
    start := time.Now()
    
    for i := 0; i < concurrency; i++ {
        wg.Add(1)
        go func(idx int) {
            defer wg.Done()
            
            resp, err := cli.ContainerCreate(ctx, &container.Config{
                Image: "alpine:latest",
            }, nil, nil, nil, fmt.Sprintf("concurrent-%d", idx))
            
            if err == nil {
                defer cli.ContainerRemove(ctx, resp.ID, 
                    types.ContainerRemoveOptions{Force: true})
            }
            
            results <- err
        }(i)
    }
    
    wg.Wait()
    close(results)
    
    duration := time.Since(start)
    
    // 统计结果
    successCount := 0
    for err := range results {
        if err == nil {
            successCount++
        }
    }
    
    successRate := float64(successCount) / float64(concurrency) * 100
    throughput := float64(successCount) / duration.Seconds()
    
    t.Logf("并发测试结果:")
    t.Logf("  - 并发度: %d", concurrency)
    t.Logf("  - 成功率: %.2f%% (%d/%d)", successRate, successCount, concurrency)
    t.Logf("  - 总耗时: %v", duration)
    t.Logf("  - 吞吐量: %.2f ops/s", throughput)
    
    assert.GreaterOrEqual(t, successRate, 95.0, "成功率应该 >= 95%")
}
```

### 4. 性能基准测试 (Performance Benchmarking)

**定义**: 量化系统性能指标

**关键指标**:

- **TPS** (Transactions Per Second): 每秒事务数
- **延迟** (Latency): 响应时间
- **P50/P95/P99**: 百分位延迟
- **资源使用**: CPU、内存、网络

**Go基准测试**:

```go
func BenchmarkContainerCreation(b *testing.B) {
    cli, _ := client.NewClientWithOpts(client.FromEnv)
    defer cli.Close()
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        resp, err := cli.ContainerCreate(context.Background(), 
            &container.Config{Image: "alpine"}, nil, nil, nil, "")
        
        if err == nil {
            cli.ContainerRemove(context.Background(), resp.ID, 
                types.ContainerRemoveOptions{Force: true})
        }
    }
}

// 运行：go test -bench=. -benchmem -benchtime=10s
// 输出：
// BenchmarkContainerCreation-8  100  120ms/op  5MB/op  1000 allocs/op
```

**Python性能测试**:

```python
import time
import statistics

def test_performance_container_lifecycle(client):
    """性能测试：完整生命周期"""
    iterations = 100
    latencies = []
    
    for i in range(iterations):
        start = time.time()
        
        # 创建
        container = client.containers.create("alpine:latest")
        
        # 启动
        container.start()
        
        # 停止
        container.stop()
        
        # 删除
        container.remove()
        
        latency = time.time() - start
        latencies.append(latency)
    
    # 统计分析
    avg_latency = statistics.mean(latencies)
    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
    
    print(f"性能指标 (n={iterations}):")
    print(f"  平均延迟: {avg_latency*1000:.2f}ms")
    print(f"  P50: {p50*1000:.2f}ms")
    print(f"  P95: {p95*1000:.2f}ms")
    print(f"  P99: {p99*1000:.2f}ms")
    print(f"  吞吐量: {iterations/(sum(latencies)):.2f} ops/s")
```

### 5. 幂等性测试 (Idempotency Testing)

**定义**: 验证重复执行操作的一致性

**幂等操作**:

- ✅ GET请求
- ✅ PUT请求（覆盖更新）
- ✅ DELETE请求
- ❌ POST请求（非幂等）

**示例场景**:

```go
func TestIdempotencyMultipleStops(t *testing.T) {
    // 创建并启动容器
    resp, _ := cli.ContainerCreate(ctx, &container.Config{
        Image: "alpine",
        Cmd:   []string{"sleep", "30"},
    }, nil, nil, nil, "")
    defer cli.ContainerRemove(ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
    
    cli.ContainerStart(ctx, resp.ID, types.ContainerStartOptions{})
    
    // 多次停止（应该都成功或返回一致的结果）
    for i := 0; i < 5; i++ {
        err := cli.ContainerStop(ctx, resp.ID, container.StopOptions{})
        t.Logf("第%d次停止: %v", i+1, err)
    }
    
    // 验证最终状态
    inspect, _ := cli.ContainerInspect(ctx, resp.ID)
    assert.False(t, inspect.State.Running)
}
```

### 6. 状态机测试 (State Machine Testing)

**定义**: 验证资源状态转换的正确性

**容器状态机**:

```
Created → Running → Paused → Running → Exited
   ↓         ↓                   ↓
Removed   Restarted          Restarted
```

**示例场景**:

```python
def test_state_machine_full_lifecycle(client):
    """测试完整状态转换"""
    container = client.containers.create(
        "alpine:latest",
        command=["sleep", "30"]
    )
    
    try:
        # 状态1: Created
        assert container.status == "created"
        
        # 状态2: Running
        container.start()
        container.reload()
        assert container.status == "running"
        
        # 状态3: Paused
        container.pause()
        container.reload()
        assert container.status == "paused"
        
        # 状态4: Running (Unpause)
        container.unpause()
        container.reload()
        assert container.status == "running"
        
        # 状态5: Exited
        container.stop()
        container.reload()
        assert container.status == "exited"
        
        # 状态6: Running (Restart)
        container.restart()
        container.reload()
        assert container.status == "running"
        
    finally:
        container.remove(force=True)
```

### 7. 资源限制测试 (Resource Limit Testing)

**定义**: 测试系统资源限制的执行

**测试场景**:

- CPU限制
- 内存限制
- OOM Killer
- 磁盘IO限制
- 网络带宽限制

**示例场景**:

```go
func TestResourceOOMKiller(t *testing.T) {
    // 创建内存限制为10MB的容器
    resp, err := cli.ContainerCreate(ctx, &container.Config{
        Image: "alpine",
        Cmd:   []string{"sh", "-c", "dd if=/dev/zero of=/tmp/file bs=1M count=20"},
    }, &container.HostConfig{
        Resources: container.Resources{
            Memory:     10 * 1024 * 1024,  // 10MB
            MemorySwap: 10 * 1024 * 1024,  // 禁用swap
        },
    }, nil, nil, "")
    
    require.NoError(t, err)
    defer cli.ContainerRemove(ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
    
    // 启动容器
    err = cli.ContainerStart(ctx, resp.ID, types.ContainerStartOptions{})
    require.NoError(t, err)
    
    // 等待容器完成或OOM
    statusCh, errCh := cli.ContainerWait(ctx, resp.ID, container.WaitConditionNotRunning)
    select {
    case status := <-statusCh:
        t.Logf("容器退出码: %d", status.StatusCode)
        // OOM killed通常退出码为137
        assert.Equal(t, int64(137), status.StatusCode)
    case err := <-errCh:
        t.Fatalf("容器等待错误: %v", err)
    }
}
```

### 8. 复杂场景测试 (Complex Scenario Testing)

**定义**: 模拟真实生产环境的复杂场景

**测试场景**:

- 多容器网络通信
- 容器间卷共享
- 服务发现
- 滚动更新
- 灰度发布
- 健康检查
- 自动重启

**示例：多容器网络通信**:

```python
def test_complex_multi_container_network(client):
    """测试多容器网络通信"""
    # 创建自定义网络
    network = client.networks.create(
        "test-network",
        driver="bridge"
    )
    
    try:
        # 创建服务端容器
        server = client.containers.run(
            "alpine:latest",
            command=["sh", "-c", "nc -l -p 8080"],
            network="test-network",
            name="server",
            detach=True
        )
        
        time.sleep(1)
        
        # 创建客户端容器
        client_container = client.containers.run(
            "alpine:latest",
            command=["sh", "-c", "echo 'hello' | nc server 8080"],
            network="test-network",
            detach=True
        )
        
        # 等待通信完成
        result = client_container.wait(timeout=5)
        
        # 验证通信成功
        assert result['StatusCode'] == 0
        
    finally:
        server.remove(force=True)
        client_container.remove(force=True)
        network.remove()
```

---

## 混沌工程 (Chaos Engineering)

### 定义

**混沌工程**: 在生产系统中进行实验，以建立对系统抵抗混乱条件能力的信心。

### 混沌实验类型

#### 1. 资源耗尽

```go
func TestChaosResourceExhaustion(t *testing.T) {
    // 创建大量容器消耗资源
    for i := 0; i < 100; i++ {
        go func() {
            cli.ContainerCreate(ctx, &container.Config{
                Image: "alpine",
                Cmd:   []string{"sleep", "infinity"},
            }, nil, nil, nil, "")
        }()
    }
}
```

#### 2. 网络延迟

```bash
# 使用tc添加网络延迟
tc qdisc add dev eth0 root netem delay 100ms 10ms

# Python测试
def test_chaos_network_latency(client):
    start = time.time()
    containers = client.containers.list()
    latency = time.time() - start
    
    assert latency < 2.0, f"高延迟下性能降级: {latency}s"
```

#### 3. 随机容器终止

```python
def test_chaos_random_termination(client):
    """随机终止容器测试恢复能力"""
    containers = []
    
    # 创建10个容器
    for i in range(10):
        c = client.containers.run(
            "alpine:latest",
            command=["sleep", "infinity"],
            detach=True,
            restart_policy={"Name": "always"}
        )
        containers.append(c)
    
    # 随机终止3个容器
    import random
    victims = random.sample(containers, 3)
    for c in victims:
        c.kill()
    
    # 验证自动重启
    time.sleep(5)
    for c in victims:
        c.reload()
        assert c.status == "running", "容器应该自动重启"
```

---

## 性能优化建议

### 1. 测试并行化

```go
func TestParallel(t *testing.T) {
    t.Run("Test1", func(t *testing.T) {
        t.Parallel()  // 启用并行
        // 测试逻辑
    })
    
    t.Run("Test2", func(t *testing.T) {
        t.Parallel()
        // 测试逻辑
    })
}

// 运行：go test -parallel 8
```

### 2. 使用测试缓存

```bash
# Go自动缓存测试结果
go test ./...  # 第一次运行
go test ./...  # 第二次使用缓存

# 强制重新运行
go test -count=1 ./...
```

### 3. 资源清理

```python
@pytest.fixture(scope="function")
def docker_client():
    client = docker.from_env()
    yield client
    
    # 清理所有测试容器
    for container in client.containers.list(all=True):
        if container.name.startswith("test-"):
            container.remove(force=True)
```

---

## 最佳实践总结

### ✅ DO (应该做)

1. **测试独立性**: 每个测试应该独立运行
2. **快速失败**: 尽早发现并报告问题
3. **详细日志**: 记录测试执行细节
4. **自动清理**: 确保资源清理
5. **持续监控**: 跟踪测试性能趋势

### ❌ DON'T (不应该做)

1. **测试依赖**: 避免测试之间的依赖
2. **硬编码**: 避免硬编码配置
3. **忽略错误**: 所有错误都应该处理
4. **资源泄漏**: 必须清理测试资源
5. **过度测试**: 避免重复测试

---

## 相关文档

- **[基础测试指南](TEST_COMPREHENSIVE_GUIDE.md)** - 测试基础
- **[集成测试示例](INTEGRATION_EXAMPLES.md)** - 集成测试
- **[性能优化指南](../QUICKSTART.md)** - 性能优化

---

**最后更新**: 2025年10月23日  
**文档版本**: v1.0  
**维护团队**: QA团队
