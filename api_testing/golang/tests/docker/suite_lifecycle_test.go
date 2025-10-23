package main

import (
	"context"
	"testing"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/client"
	"github.com/stretchr/testify/suite"
)

// ====================
// 容器生命周期测试套件
// 按功能模块组织：创建、启动、停止、重启、暂停/恢复、删除
// ====================

// ContainerLifecycleTestSuite 容器生命周期测试套件
type ContainerLifecycleTestSuite struct {
	suite.Suite
	cli *client.Client
	ctx context.Context
}

func (s *ContainerLifecycleTestSuite) SetupSuite() {
	s.ctx = context.Background()
	cli, err := client.NewClientWithOpts(
		client.FromEnv,
		client.WithAPIVersionNegotiation(),
	)
	s.Require().NoError(err)
	s.cli = cli
}

func (s *ContainerLifecycleTestSuite) TearDownSuite() {
	if s.cli != nil {
		s.cli.Close()
	}
}

// ====================
// 1. 容器创建测试 (Container Creation)
// ====================

// TestCreate_BasicConfiguration 测试基础配置创建
func (s *ContainerLifecycleTestSuite) TestCreate_BasicConfiguration() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
	}, nil, nil, nil, "")

	s.Require().NoError(err)
	s.Assert().NotEmpty(resp.ID)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
}

// TestCreate_WithCommand 测试带命令创建
func (s *ContainerLifecycleTestSuite) TestCreate_WithCommand() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"echo", "hello world"},
	}, nil, nil, nil, "")

	s.Require().NoError(err)
	s.Assert().NotEmpty(resp.ID)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
}

// TestCreate_WithEnvironmentVariables 测试带环境变量创建
func (s *ContainerLifecycleTestSuite) TestCreate_WithEnvironmentVariables() {
	envVars := []string{
		"TEST_VAR=test_value",
		"DEBUG=true",
		"PORT=8080",
	}

	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Env:   envVars,
		Cmd:   []string{"env"},
	}, nil, nil, nil, "")

	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 验证环境变量
	inspect, err := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Require().NoError(err)
	s.Assert().Contains(inspect.Config.Env, "TEST_VAR=test_value")
}

// TestCreate_WithLabels 测试带标签创建
func (s *ContainerLifecycleTestSuite) TestCreate_WithLabels() {
	labels := map[string]string{
		"app":         "test-app",
		"environment": "testing",
		"version":     "1.0.0",
	}

	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image:  "alpine:latest",
		Labels: labels,
	}, nil, nil, nil, "")

	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 验证标签
	inspect, err := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Require().NoError(err)
	s.Assert().Equal("test-app", inspect.Config.Labels["app"])
}

// TestCreate_WithWorkingDirectory 测试带工作目录创建
func (s *ContainerLifecycleTestSuite) TestCreate_WithWorkingDirectory() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image:      "alpine:latest",
		WorkingDir: "/app",
		Cmd:        []string{"pwd"},
	}, nil, nil, nil, "")

	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 验证工作目录
	inspect, err := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Require().NoError(err)
	s.Assert().Equal("/app", inspect.Config.WorkingDir)
}

// TestCreate_WithUser 测试带用户创建
func (s *ContainerLifecycleTestSuite) TestCreate_WithUser() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		User:  "1000:1000",
		Cmd:   []string{"id"},
	}, nil, nil, nil, "")

	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 验证用户
	inspect, err := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Require().NoError(err)
	s.Assert().Equal("1000:1000", inspect.Config.User)
}

// ====================
// 2. 容器启动测试 (Container Start)
// ====================

// TestStart_Normal 测试正常启动
func (s *ContainerLifecycleTestSuite) TestStart_Normal() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "10"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 启动容器
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	// 验证状态
	inspect, _ := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().True(inspect.State.Running)
}

// TestStart_AlreadyRunning 测试重复启动
func (s *ContainerLifecycleTestSuite) TestStart_AlreadyRunning() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "10"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 第一次启动
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	// 第二次启动（应该无错误或304）
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.T().Logf("重复启动结果: %v", err)
}

// ====================
// 3. 容器停止测试 (Container Stop)
// ====================

// TestStop_GracefulShutdown 测试优雅停止
func (s *ContainerLifecycleTestSuite) TestStop_GracefulShutdown() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "30"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 启动容器
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	// 优雅停止
	timeout := 10
	err = s.cli.ContainerStop(s.ctx, resp.ID, container.StopOptions{
		Timeout: &timeout,
	})
	s.Require().NoError(err)

	// 验证状态
	inspect, _ := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().False(inspect.State.Running)
	s.Assert().Equal("exited", inspect.State.Status)
}

// TestStop_WithTimeout 测试带超时停止
func (s *ContainerLifecycleTestSuite) TestStop_WithTimeout() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "trap '' TERM; sleep 30"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 启动容器
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	// 短超时停止
	start := time.Now()
	timeout := 2
	err = s.cli.ContainerStop(s.ctx, resp.ID, container.StopOptions{
		Timeout: &timeout,
	})
	duration := time.Since(start)

	s.T().Logf("停止耗时: %v", duration)
	s.Assert().LessOrEqual(duration.Seconds(), 5.0, "停止应该在超时后快速完成")
}

// ====================
// 4. 容器重启测试 (Container Restart)
// ====================

// TestRestart_Running 测试重启运行中容器
func (s *ContainerLifecycleTestSuite) TestRestart_Running() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "30"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 启动容器
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	// 获取启动时间
	inspect1, _ := s.cli.ContainerInspect(s.ctx, resp.ID)
	startedAt1 := inspect1.State.StartedAt

	time.Sleep(1 * time.Second)

	// 重启容器
	timeout := 10
	err = s.cli.ContainerRestart(s.ctx, resp.ID, container.StopOptions{
		Timeout: &timeout,
	})
	s.Require().NoError(err)

	// 验证重启后的状态
	inspect2, _ := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().True(inspect2.State.Running)
	s.Assert().NotEqual(startedAt1, inspect2.State.StartedAt, "启动时间应该更新")
}

// TestRestart_Stopped 测试重启已停止容器
func (s *ContainerLifecycleTestSuite) TestRestart_Stopped() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"echo", "hello"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 启动并等待退出
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	statusCh, _ := s.cli.ContainerWait(s.ctx, resp.ID, container.WaitConditionNotRunning)
	<-statusCh

	// 重启容器
	timeout := 10
	err = s.cli.ContainerRestart(s.ctx, resp.ID, container.StopOptions{
		Timeout: &timeout,
	})
	s.Require().NoError(err)

	// 验证状态
	time.Sleep(500 * time.Millisecond)
	inspect, _ := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.T().Logf("重启后状态: %s", inspect.State.Status)
}

// ====================
// 5. 容器暂停/恢复测试 (Container Pause/Unpause)
// ====================

// TestPause_Normal 测试正常暂停
func (s *ContainerLifecycleTestSuite) TestPause_Normal() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "30"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 启动容器
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	// 暂停容器
	err = s.cli.ContainerPause(s.ctx, resp.ID)
	s.Require().NoError(err)

	// 验证状态
	inspect, _ := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().True(inspect.State.Paused)
	s.Assert().Equal("paused", inspect.State.Status)
}

// TestUnpause_Normal 测试正常恢复
func (s *ContainerLifecycleTestSuite) TestUnpause_Normal() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "30"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 启动并暂停
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	err = s.cli.ContainerPause(s.ctx, resp.ID)
	s.Require().NoError(err)

	// 恢复容器
	err = s.cli.ContainerUnpause(s.ctx, resp.ID)
	s.Require().NoError(err)

	// 验证状态
	inspect, _ := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().False(inspect.State.Paused)
	s.Assert().True(inspect.State.Running)
}

// TestPause_PauseUnpauseCycle 测试多次暂停/恢复循环
func (s *ContainerLifecycleTestSuite) TestPause_PauseUnpauseCycle() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "60"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 启动容器
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	// 多次暂停/恢复循环
	for i := 0; i < 3; i++ {
		// 暂停
		err = s.cli.ContainerPause(s.ctx, resp.ID)
		s.Require().NoError(err)

		inspect, _ := s.cli.ContainerInspect(s.ctx, resp.ID)
		s.Assert().True(inspect.State.Paused)

		time.Sleep(100 * time.Millisecond)

		// 恢复
		err = s.cli.ContainerUnpause(s.ctx, resp.ID)
		s.Require().NoError(err)

		inspect, _ = s.cli.ContainerInspect(s.ctx, resp.ID)
		s.Assert().False(inspect.State.Paused)

		time.Sleep(100 * time.Millisecond)

		s.T().Logf("完成第%d次暂停/恢复循环", i+1)
	}
}

// ====================
// 6. 容器删除测试 (Container Remove)
// ====================

// TestRemove_Stopped 测试删除已停止容器
func (s *ContainerLifecycleTestSuite) TestRemove_Stopped() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
	}, nil, nil, nil, "")
	s.Require().NoError(err)

	// 删除容器
	err = s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{})
	s.Assert().NoError(err)

	// 验证容器已删除
	_, err = s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().Error(err)
}

// TestRemove_Running_WithForce 测试强制删除运行中容器
func (s *ContainerLifecycleTestSuite) TestRemove_Running_WithForce() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "30"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)

	// 启动容器
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	// 强制删除
	err = s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})
	s.Assert().NoError(err)
}

// TestRemove_Running_WithoutForce 测试非强制删除运行中容器（应该失败）
func (s *ContainerLifecycleTestSuite) TestRemove_Running_WithoutForce() {
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "30"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	// 启动容器
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	// 尝试删除（不使用force）
	err = s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: false})
	s.Assert().Error(err, "删除运行中容器应该失败")
}

// TestRemove_WithVolumes 测试删除容器及关联卷
func (s *ContainerLifecycleTestSuite) TestRemove_WithVolumes() {
	// 创建匿名卷的容器
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
	}, &container.HostConfig{
		Binds: []string{"/data"},
	}, nil, nil, "")
	s.Require().NoError(err)

	// 删除容器和卷
	err = s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{
		RemoveVolumes: true,
	})
	s.Assert().NoError(err)
}

// ====================
// 7. 完整生命周期测试
// ====================

// TestFullLifecycle_CreateStartStopRemove 测试完整生命周期
func (s *ContainerLifecycleTestSuite) TestFullLifecycle_CreateStartStopRemove() {
	s.T().Log("=== 完整生命周期测试 ===")

	// 1. 创建
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "5"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	s.T().Logf("✅ 创建容器: %s", resp.ID[:12])

	// 2. 启动
	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	s.T().Log("✅ 启动容器")

	// 3. 验证运行状态
	inspect, _ := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().True(inspect.State.Running)
	s.T().Log("✅ 验证运行状态")

	// 4. 停止
	timeout := 10
	err = s.cli.ContainerStop(s.ctx, resp.ID, container.StopOptions{
		Timeout: &timeout,
	})
	s.Require().NoError(err)
	s.T().Log("✅ 停止容器")

	// 5. 验证停止状态
	inspect, _ = s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().False(inspect.State.Running)
	s.T().Log("✅ 验证停止状态")

	// 6. 删除
	err = s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{})
	s.Require().NoError(err)
	s.T().Log("✅ 删除容器")

	// 7. 验证删除
	_, err = s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Assert().Error(err)
	s.T().Log("✅ 验证删除成功")

	s.T().Log("=== 完整生命周期测试完成 ===")
}

// TestContainerLifecycleTestSuite 运行生命周期测试套件
func TestContainerLifecycleTestSuite(t *testing.T) {
	suite.Run(t, new(ContainerLifecycleTestSuite))
}
