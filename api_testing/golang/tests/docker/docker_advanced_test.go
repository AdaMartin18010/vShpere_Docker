package main

import (
	"context"
	"fmt"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/volume"
	"github.com/docker/docker/client"
	"github.com/stretchr/testify/suite"
)

// DockerAdvancedTestSuite 高级Docker API测试套件
// 包含：边界条件、错误处理、并发、性能、复杂场景
type DockerAdvancedTestSuite struct {
	suite.Suite
	cli *client.Client
	ctx context.Context
}

// SetupSuite 初始化
func (s *DockerAdvancedTestSuite) SetupSuite() {
	s.ctx = context.Background()
	cli, err := client.NewClientWithOpts(
		client.FromEnv,
		client.WithAPIVersionNegotiation(),
	)
	s.Require().NoError(err)
	s.cli = cli
}

// TearDownSuite 清理
func (s *DockerAdvancedTestSuite) TearDownSuite() {
	if s.cli != nil {
		s.cli.Close()
	}
}

// ====================
// 1. 边界条件测试
// ====================

// TestBoundaryConditions_EmptyImageName 测试空镜像名
func (s *DockerAdvancedTestSuite) TestBoundaryConditions_EmptyImageName() {
	_, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "", // 空镜像名
	}, nil, nil, nil, "")
	
	s.Assert().Error(err, "空镜像名应该返回错误")
}

// TestBoundaryConditions_InvalidImageName 测试非法镜像名
func (s *DockerAdvancedTestSuite) TestBoundaryConditions_InvalidImageName() {
	invalidNames := []string{
		"Invalid@Image",
		"image::",
		"image::tag",
		strings.Repeat("a", 256), // 超长名称
	}
	
	for _, name := range invalidNames {
		_, err := s.cli.ContainerCreate(s.ctx, &container.Config{
			Image: name,
		}, nil, nil, nil, "")
		
		s.Assert().Error(err, fmt.Sprintf("非法镜像名 '%s' 应该返回错误", name))
	}
}

// TestBoundaryConditions_MaxContainerName 测试最大容器名长度
func (s *DockerAdvancedTestSuite) TestBoundaryConditions_MaxContainerName() {
	// Docker容器名最大长度通常为255字符
	maxName := strings.Repeat("a", 255)
	tooLongName := strings.Repeat("a", 256)
	
	// 测试最大长度（应该成功）
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
	}, nil, nil, nil, maxName)
	
	if err == nil {
		s.Assert().NotEmpty(resp.ID)
		defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	}
	
	// 测试超长名称（应该失败）
	_, err = s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
	}, nil, nil, nil, tooLongName)
	
	s.Assert().Error(err, "超长容器名应该返回错误")
}

// TestBoundaryConditions_ZeroMemoryLimit 测试零内存限制
func (s *DockerAdvancedTestSuite) TestBoundaryConditions_ZeroMemoryLimit() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
	}, &container.HostConfig{
		Resources: container.Resources{
			Memory: 0, // 零内存限制表示不限制
		},
	}, nil, nil, "")
	
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	
	inspect, err := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Require().NoError(err)
	s.Assert().Equal(int64(0), inspect.HostConfig.Memory)
}

// TestBoundaryConditions_NegativeMemoryLimit 测试负数内存限制
func (s *DockerAdvancedTestSuite) TestBoundaryConditions_NegativeMemoryLimit() {
	_, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
	}, &container.HostConfig{
		Resources: container.Resources{
			Memory: -1, // 负数应该被拒绝或转换为0
		},
	}, nil, nil, "")
	
	// Docker可能拒绝或接受（转换为0），我们记录行为
	if err != nil {
		s.T().Logf("负数内存限制被拒绝: %v", err)
	} else {
		s.T().Logf("负数内存限制被接受（可能转换为0）")
	}
}

// ====================
// 2. 错误处理测试
// ====================

// TestErrorHandling_NonExistentContainer 测试操作不存在的容器
func (s *DockerAdvancedTestSuite) TestErrorHandling_NonExistentContainer() {
	nonExistentID := "nonexistent-container-id-12345"
	
	// 测试启动
	err := s.cli.ContainerStart(s.ctx, nonExistentID, types.ContainerStartOptions{})
	s.Assert().Error(err)
	
	// 测试停止
	err = s.cli.ContainerStop(s.ctx, nonExistentID, container.StopOptions{})
	s.Assert().Error(err)
	
	// 测试删除
	err = s.cli.ContainerRemove(s.ctx, nonExistentID, types.ContainerRemoveOptions{})
	s.Assert().Error(err)
	
	// 测试检查
	_, err = s.cli.ContainerInspect(s.ctx, nonExistentID)
	s.Assert().Error(err)
}

// TestErrorHandling_StartRunningContainer 测试重复启动容器
func (s *DockerAdvancedTestSuite) TestErrorHandling_StartRunningContainer() {
	// 创建并启动容器
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "30"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	
	// 再次启动（应该返回错误或成功但无操作）
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	// Docker通常会返回304 Not Modified，不是错误
	s.T().Logf("重复启动结果: %v", err)
}

// TestErrorHandling_RemoveRunningContainer 测试删除运行中容器
func (s *DockerAdvancedTestSuite) TestErrorHandling_RemoveRunningContainer() {
	// 创建并启动容器
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "30"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	
	// 尝试删除（不使用force，应该失败）
	err = s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: false})
	s.Assert().Error(err, "删除运行中容器应该失败（不使用force）")
	
	// 使用force删除（应该成功）
	err = s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	s.Assert().NoError(err, "使用force删除运行中容器应该成功")
}

// TestErrorHandling_NetworkTimeout 测试网络超时
func (s *DockerAdvancedTestSuite) TestErrorHandling_NetworkTimeout() {
	// 创建短超时的context
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Nanosecond)
	defer cancel()
	
	time.Sleep(10 * time.Millisecond) // 确保context已超时
	
	// 尝试操作（应该超时）
	_, err := s.cli.ContainerList(ctx, types.ContainerListOptions{})
	s.Assert().Error(err)
	s.Assert().Contains(err.Error(), "context")
}

// ====================
// 3. 并发测试
// ====================

// TestConcurrency_ParallelContainerCreation 测试并发创建容器
func (s *DockerAdvancedTestSuite) TestConcurrency_ParallelContainerCreation() {
	concurrency := 20
	var wg sync.WaitGroup
	results := make(chan error, concurrency)
	containerIDs := make([]string, 0, concurrency)
	var mu sync.Mutex
	
	for i := 0; i < concurrency; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			
			resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
				Image: "alpine:latest",
				Cmd:   []string{"echo", fmt.Sprintf("container-%d", idx)},
			}, nil, nil, nil, fmt.Sprintf("concurrent-test-%d", idx))
			
			if err != nil {
				results <- err
				return
			}
			
			mu.Lock()
			containerIDs = append(containerIDs, resp.ID)
			mu.Unlock()
			
			results <- nil
		}(i)
	}
	
	wg.Wait()
	close(results)
	
	// 清理容器
	for _, id := range containerIDs {
		s.cli.ContainerRemove(s.ctx, id, types.ContainerRemoveOptions{Force: true})
	}
	
	// 检查错误
	errorCount := 0
	for err := range results {
		if err != nil {
			errorCount++
			s.T().Logf("并发创建错误: %v", err)
		}
	}
	
	successRate := float64(concurrency-errorCount) / float64(concurrency) * 100
	s.T().Logf("并发创建成功率: %.2f%% (%d/%d)", successRate, concurrency-errorCount, concurrency)
	s.Assert().GreaterOrEqual(successRate, 90.0, "成功率应该 >= 90%")
}

// TestConcurrency_RaceCondition 测试资源竞争
func (s *DockerAdvancedTestSuite) TestConcurrency_RaceCondition() {
	// 创建一个容器
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "10"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	
	// 并发启动和停止
	operations := 10
	var wg sync.WaitGroup
	
	for i := 0; i < operations; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			
			if idx%2 == 0 {
				s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
			} else {
				s.cli.ContainerStop(s.ctx, resp.ID, container.StopOptions{})
			}
		}(i)
	}
	
	wg.Wait()
	
	// 检查最终状态（容器应该仍然存在）
	_, err = s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().NoError(err, "容器应该仍然存在")
}

// ====================
// 4. 性能基准测试
// ====================

// BenchmarkContainerCreation 基准测试：容器创建
func BenchmarkContainerCreation(b *testing.B) {
	ctx := context.Background()
	cli, err := client.NewClientWithOpts(
		client.FromEnv,
		client.WithAPIVersionNegotiation(),
	)
	if err != nil {
		b.Fatal(err)
	}
	defer cli.Close()
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		resp, err := cli.ContainerCreate(ctx, &container.Config{
			Image: "alpine:latest",
		}, nil, nil, nil, "")
		
		if err == nil {
			cli.ContainerRemove(ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
		}
	}
}

// BenchmarkContainerList 基准测试：容器列表
func BenchmarkContainerList(b *testing.B) {
	ctx := context.Background()
	cli, err := client.NewClientWithOpts(
		client.FromEnv,
		client.WithAPIVersionNegotiation(),
	)
	if err != nil {
		b.Fatal(err)
	}
	defer cli.Close()
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := cli.ContainerList(ctx, types.ContainerListOptions{All: true})
		if err != nil {
			b.Fatal(err)
		}
	}
}

// ====================
// 5. 幂等性测试
// ====================

// TestIdempotency_MultipleStops 测试多次停止容器
func (s *DockerAdvancedTestSuite) TestIdempotency_MultipleStops() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "10"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	
	// 启动容器
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	
	// 多次停止
	for i := 0; i < 3; i++ {
		err = s.cli.ContainerStop(s.ctx, resp.ID, container.StopOptions{})
		s.T().Logf("第%d次停止: %v", i+1, err)
	}
	
	// 检查最终状态
	inspect, err := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Require().NoError(err)
	s.Assert().False(inspect.State.Running)
}

// TestIdempotency_MultipleRemoves 测试多次删除容器
func (s *DockerAdvancedTestSuite) TestIdempotency_MultipleRemoves() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	
	// 第一次删除（应该成功）
	err = s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{})
	s.Assert().NoError(err)
	
	// 第二次删除（应该失败）
	err = s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{})
	s.Assert().Error(err)
}

// ====================
// 6. 状态机测试
// ====================

// TestStateMachine_ContainerLifecycle 测试容器完整生命周期状态转换
func (s *DockerAdvancedTestSuite) TestStateMachine_ContainerLifecycle() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "5"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	
	// 状态1: Created
	inspect, _ := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().Equal("created", inspect.State.Status)
	
	// 状态2: Running
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	inspect, _ = s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().Equal("running", inspect.State.Status)
	
	// 状态3: Paused
	err = s.cli.ContainerPause(s.ctx, resp.ID)
	s.Require().NoError(err)
	inspect, _ = s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().Equal("paused", inspect.State.Status)
	
	// 状态4: Running (Unpause)
	err = s.cli.ContainerUnpause(s.ctx, resp.ID)
	s.Require().NoError(err)
	inspect, _ = s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().Equal("running", inspect.State.Status)
	
	// 状态5: Exited
	err = s.cli.ContainerStop(s.ctx, resp.ID, container.StopOptions{})
	s.Require().NoError(err)
	inspect, _ = s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().Equal("exited", inspect.State.Status)
}

// ====================
// 7. 资源限制测试
// ====================

// TestResourceLimits_CPULimit 测试CPU限制
func (s *DockerAdvancedTestSuite) TestResourceLimits_CPULimit() {
	cpuQuotas := []int64{10000, 50000, 100000} // 10%, 50%, 100% of one core
	
	for _, quota := range cpuQuotas {
		resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
			Image: "alpine:latest",
			Cmd:   []string{"sh", "-c", "while true; do echo test; done"},
		}, &container.HostConfig{
			Resources: container.Resources{
				CPUQuota:  quota,
				CPUPeriod: 100000,
			},
		}, nil, nil, "")
		
		s.Require().NoError(err)
		
		inspect, err := s.cli.ContainerInspect(s.ctx, resp.ID)
		s.Require().NoError(err)
		s.Assert().Equal(quota, inspect.HostConfig.CPUQuota)
		
		s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	}
}

// TestResourceLimits_MemoryOOM 测试内存OOM
func (s *DockerAdvancedTestSuite) TestResourceLimits_MemoryOOM() {
	// 创建内存限制为10MB的容器，尝试使用更多内存
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "dd if=/dev/zero of=/tmp/file bs=1M count=20"},
	}, &container.HostConfig{
		Resources: container.Resources{
			Memory:     10 * 1024 * 1024, // 10MB
			MemorySwap: 10 * 1024 * 1024, // 禁用swap
		},
	}, nil, nil, "")
	
	if err != nil {
		s.T().Skip("无法创建内存限制容器，可能需要特殊权限")
		return
	}
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	
	// 启动容器
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	
	// 等待容器完成或OOM
	statusCh, errCh := s.cli.ContainerWait(s.ctx, resp.ID, container.WaitConditionNotRunning)
	select {
	case status := <-statusCh:
		s.T().Logf("容器退出码: %d", status.StatusCode)
		// OOM killed通常退出码为137
	case err := <-errCh:
		s.T().Logf("容器等待错误: %v", err)
	case <-time.After(10 * time.Second):
		s.T().Log("容器运行超时")
	}
}

// ====================
// 8. 复杂场景测试
// ====================

// TestComplexScenario_MultiContainerNetwork 测试多容器网络通信
func (s *DockerAdvancedTestSuite) TestComplexScenario_MultiContainerNetwork() {
	// 创建自定义网络
	networkResp, err := s.cli.NetworkCreate(s.ctx, "test-network", types.NetworkCreate{
		Driver: "bridge",
	})
	s.Require().NoError(err)
	defer s.cli.NetworkRemove(s.ctx, networkResp.ID)
	
	// 创建容器1（服务端）
	server, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "nc -l -p 8080"},
	}, &container.HostConfig{
		NetworkMode: container.NetworkMode(networkResp.ID),
	}, nil, nil, "server")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, server.ID, types.ContainerRemoveOptions{Force: true})
	
	// 创建容器2（客户端）
	client, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "sleep 2 && echo 'hello' | nc server 8080"},
	}, &container.HostConfig{
		NetworkMode: container.NetworkMode(networkResp.ID),
	}, nil, nil, "client")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, client.ID, types.ContainerRemoveOptions{Force: true})
	
	// 启动服务端
	err = s.cli.ContainerStart(s.ctx, server.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	
	// 启动客户端
	err = s.cli.ContainerStart(s.ctx, client.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	
	s.T().Log("多容器网络通信测试完成")
}

// TestComplexScenario_VolumeSharing 测试容器间卷共享
func (s *DockerAdvancedTestSuite) TestComplexScenario_VolumeSharing() {
	// 创建卷
	volumeName := "shared-volume"
	_, err := s.cli.VolumeCreate(s.ctx, volume.CreateOptions{
		Name: volumeName,
	})
	s.Require().NoError(err)
	defer s.cli.VolumeRemove(s.ctx, volumeName, false)
	
	// 容器1写入数据
	writer, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "echo 'shared data' > /data/test.txt"},
	}, &container.HostConfig{
		Binds: []string{volumeName + ":/data"},
	}, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, writer.ID, types.ContainerRemoveOptions{Force: true})
	
	err = s.cli.ContainerStart(s.ctx, writer.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	
	// 等待写入完成
	statusCh, _ := s.cli.ContainerWait(s.ctx, writer.ID, container.WaitConditionNotRunning)
	<-statusCh
	
	// 容器2读取数据
	reader, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"cat", "/data/test.txt"},
	}, &container.HostConfig{
		Binds: []string{volumeName + ":/data:ro"}, // 只读挂载
	}, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, reader.ID, types.ContainerRemoveOptions{Force: true})
	
	err = s.cli.ContainerStart(s.ctx, reader.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	
	statusCh, _ = s.cli.ContainerWait(s.ctx, reader.ID, container.WaitConditionNotRunning)
	<-statusCh
	
	s.T().Log("卷共享测试完成")
}

// TestDockerAdvancedTestSuite 运行测试套件
func TestDockerAdvancedTestSuite(t *testing.T) {
	suite.Run(t, new(DockerAdvancedTestSuite))
}

