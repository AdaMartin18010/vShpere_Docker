package main

import (
	"context"
	"fmt"
	"io"
	"strings"
	"testing"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/network"
	"github.com/docker/docker/api/types/volume"
	"github.com/docker/docker/client"
	"github.com/stretchr/testify/suite"
)

// ====================
// Docker功能联动集成测试套件
// 测试容器、网络、卷之间的协作
// ====================

// DockerIntegrationTestSuite Docker集成测试套件
type DockerIntegrationTestSuite struct {
	suite.Suite
	cli *client.Client
	ctx context.Context
}

func (s *DockerIntegrationTestSuite) SetupSuite() {
	s.ctx = context.Background()
	cli, err := client.NewClientWithOpts(
		client.FromEnv,
		client.WithAPIVersionNegotiation(),
	)
	s.Require().NoError(err)
	s.cli = cli
}

func (s *DockerIntegrationTestSuite) TearDownSuite() {
	if s.cli != nil {
		s.cli.Close()
	}
}

// ====================
// 1. 容器 + 网络 联动测试
// ====================

// TestIntegration_ContainerNetwork_SameNetwork 测试同网络容器通信
func (s *DockerIntegrationTestSuite) TestIntegration_ContainerNetwork_SameNetwork() {
	s.T().Log("=== 测试：同网络容器通信 ===")

	// 1. 创建自定义网络
	networkName := fmt.Sprintf("test-network-%d", time.Now().Unix())
	networkResp, err := s.cli.NetworkCreate(s.ctx, networkName, types.NetworkCreate{
		Driver: "bridge",
	})
	s.Require().NoError(err)
	defer s.cli.NetworkRemove(s.ctx, networkResp.ID)
	s.T().Logf("✅ 创建网络: %s", networkName)

	// 2. 创建服务端容器
	server, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "echo 'Server Ready' && nc -l -p 8080"},
	}, &container.HostConfig{
		NetworkMode: container.NetworkMode(networkName),
	}, nil, nil, "server")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, server.ID, types.ContainerRemoveOptions{Force: true})

	err = s.cli.ContainerStart(s.ctx, server.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	s.T().Log("✅ 启动服务端容器")

	// 等待服务端就绪
	time.Sleep(2 * time.Second)

	// 3. 创建客户端容器
	client, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "echo 'Hello from client' | nc server 8080"},
	}, &container.HostConfig{
		NetworkMode: container.NetworkMode(networkName),
	}, nil, nil, "client")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, client.ID, types.ContainerRemoveOptions{Force: true})

	err = s.cli.ContainerStart(s.ctx, client.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	s.T().Log("✅ 启动客户端容器并发送数据")

	// 4. 等待通信完成
	statusCh, _ := s.cli.ContainerWait(s.ctx, client.ID, container.WaitConditionNotRunning)
	status := <-statusCh

	s.Assert().Equal(int64(0), status.StatusCode, "客户端应该成功退出")
	s.T().Log("✅ 容器间通信成功")
}

// TestIntegration_ContainerNetwork_CrossNetwork 测试跨网络隔离
func (s *DockerIntegrationTestSuite) TestIntegration_ContainerNetwork_CrossNetwork() {
	s.T().Log("=== 测试：跨网络隔离 ===")

	// 1. 创建两个独立网络
	network1, err := s.cli.NetworkCreate(s.ctx, fmt.Sprintf("network1-%d", time.Now().Unix()), types.NetworkCreate{
		Driver: "bridge",
	})
	s.Require().NoError(err)
	defer s.cli.NetworkRemove(s.ctx, network1.ID)

	network2, err := s.cli.NetworkCreate(s.ctx, fmt.Sprintf("network2-%d", time.Now().Unix()), types.NetworkCreate{
		Driver: "bridge",
	})
	s.Require().NoError(err)
	defer s.cli.NetworkRemove(s.ctx, network2.ID)
	s.T().Log("✅ 创建两个独立网络")

	// 2. 在network1创建服务端
	server, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "nc -l -p 8080"},
	}, &container.HostConfig{
		NetworkMode: container.NetworkMode(network1.ID),
	}, nil, nil, "server-net1")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, server.ID, types.ContainerRemoveOptions{Force: true})

	err = s.cli.ContainerStart(s.ctx, server.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	s.T().Log("✅ 在network1启动服务端")

	// 3. 在network2创建客户端（无法访问network1的服务端）
	client, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "timeout 2 nc server-net1 8080 || echo 'Connection failed as expected'"},
	}, &container.HostConfig{
		NetworkMode: container.NetworkMode(network2.ID),
	}, nil, nil, "client-net2")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, client.ID, types.ContainerRemoveOptions{Force: true})

	err = s.cli.ContainerStart(s.ctx, client.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	s.T().Log("✅ 在network2启动客户端")

	// 4. 验证无法通信（隔离性）
	statusCh, _ := s.cli.ContainerWait(s.ctx, client.ID, container.WaitConditionNotRunning)
	<-statusCh

	s.T().Log("✅ 验证网络隔离成功")
}

// TestIntegration_ContainerNetwork_Connect 测试动态网络连接
func (s *DockerIntegrationTestSuite) TestIntegration_ContainerNetwork_Connect() {
	s.T().Log("=== 测试：动态网络连接 ===")

	// 1. 创建网络
	networkResp, err := s.cli.NetworkCreate(s.ctx, fmt.Sprintf("dynamic-network-%d", time.Now().Unix()), types.NetworkCreate{
		Driver: "bridge",
	})
	s.Require().NoError(err)
	defer s.cli.NetworkRemove(s.ctx, networkResp.ID)

	// 2. 创建容器（不指定网络）
	resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sleep", "30"},
	}, nil, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

	err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	s.T().Log("✅ 创建并启动容器")

	// 3. 动态连接到网络
	err = s.cli.NetworkConnect(s.ctx, networkResp.ID, resp.ID, &network.EndpointSettings{})
	s.Require().NoError(err)
	s.T().Log("✅ 动态连接到网络")

	// 4. 验证网络连接
	inspect, err := s.cli.ContainerInspect(s.ctx, resp.ID)
	s.Require().NoError(err)
	_, connected := inspect.NetworkSettings.Networks[networkResp.ID]
	s.Assert().True(connected, "容器应该已连接到网络")

	// 5. 断开网络连接
	err = s.cli.NetworkDisconnect(s.ctx, networkResp.ID, resp.ID, false)
	s.Require().NoError(err)
	s.T().Log("✅ 断开网络连接")

	// 6. 验证断开
	inspect, _ = s.cli.ContainerInspect(s.ctx, resp.ID)
	_, stillConnected := inspect.NetworkSettings.Networks[networkResp.ID]
	s.Assert().False(stillConnected, "容器应该已断开网络")
}

// ====================
// 2. 容器 + 卷 联动测试
// ====================

// TestIntegration_ContainerVolume_DataPersistence 测试数据持久化
func (s *DockerIntegrationTestSuite) TestIntegration_ContainerVolume_DataPersistence() {
	s.T().Log("=== 测试：数据持久化 ===")

	// 1. 创建卷
	volumeName := fmt.Sprintf("test-volume-%d", time.Now().Unix())
	vol, err := s.cli.VolumeCreate(s.ctx, volume.CreateOptions{
		Name: volumeName,
	})
	s.Require().NoError(err)
	defer s.cli.VolumeRemove(s.ctx, vol.Name, false)
	s.T().Logf("✅ 创建卷: %s", volumeName)

	// 2. 容器1写入数据
	writer, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "echo 'persistent data' > /data/test.txt && cat /data/test.txt"},
	}, &container.HostConfig{
		Binds: []string{volumeName + ":/data"},
	}, nil, nil, "")
	s.Require().NoError(err)

	err = s.cli.ContainerStart(s.ctx, writer.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	statusCh, _ := s.cli.ContainerWait(s.ctx, writer.ID, container.WaitConditionNotRunning)
	<-statusCh

	// 获取写入容器的日志
	logReader, err := s.cli.ContainerLogs(s.ctx, writer.ID, types.ContainerLogsOptions{
		ShowStdout: true,
	})
	s.Require().NoError(err)
	logBytes, _ := io.ReadAll(logReader)
	logReader.Close()

	s.cli.ContainerRemove(s.ctx, writer.ID, types.ContainerRemoveOptions{})
	s.T().Logf("✅ 容器1写入数据: %s", strings.TrimSpace(string(logBytes)))

	// 3. 容器2读取数据
	reader, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"cat", "/data/test.txt"},
	}, &container.HostConfig{
		Binds: []string{volumeName + ":/data:ro"},
	}, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, reader.ID, types.ContainerRemoveOptions{})

	err = s.cli.ContainerStart(s.ctx, reader.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	statusCh, _ = s.cli.ContainerWait(s.ctx, reader.ID, container.WaitConditionNotRunning)
	<-statusCh

	// 获取读取容器的日志
	logReader, err = s.cli.ContainerLogs(s.ctx, reader.ID, types.ContainerLogsOptions{
		ShowStdout: true,
	})
	s.Require().NoError(err)
	logBytes, _ = io.ReadAll(logReader)
	logReader.Close()

	s.Assert().Contains(string(logBytes), "persistent data", "应该读取到持久化的数据")
	s.T().Logf("✅ 容器2读取数据: %s", strings.TrimSpace(string(logBytes)))
}

// TestIntegration_ContainerVolume_SharedAccess 测试多容器共享访问
func (s *DockerIntegrationTestSuite) TestIntegration_ContainerVolume_SharedAccess() {
	s.T().Log("=== 测试：多容器共享访问 ===")

	// 1. 创建共享卷
	volumeName := fmt.Sprintf("shared-volume-%d", time.Now().Unix())
	vol, err := s.cli.VolumeCreate(s.ctx, volume.CreateOptions{
		Name: volumeName,
	})
	s.Require().NoError(err)
	defer s.cli.VolumeRemove(s.ctx, vol.Name, false)

	// 2. 创建两个容器同时写入
	containers := []string{}
	for i := 0; i < 2; i++ {
		resp, err := s.cli.ContainerCreate(s.ctx, &container.Config{
			Image: "alpine:latest",
			Cmd:   []string{"sh", "-c", fmt.Sprintf("echo 'data from container %d' >> /shared/data.txt", i)},
		}, &container.HostConfig{
			Binds: []string{volumeName + ":/shared"},
		}, nil, nil, "")
		s.Require().NoError(err)
		containers = append(containers, resp.ID)

		err = s.cli.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
		s.Require().NoError(err)
	}

	// 3. 等待所有容器完成
	for _, id := range containers {
		statusCh, _ := s.cli.ContainerWait(s.ctx, id, container.WaitConditionNotRunning)
		<-statusCh
		s.cli.ContainerRemove(s.ctx, id, types.ContainerRemoveOptions{})
	}
	s.T().Log("✅ 两个容器已写入数据")

	// 4. 读取容器验证
	reader, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"cat", "/shared/data.txt"},
	}, &container.HostConfig{
		Binds: []string{volumeName + ":/shared:ro"},
	}, nil, nil, "")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, reader.ID, types.ContainerRemoveOptions{})

	err = s.cli.ContainerStart(s.ctx, reader.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	statusCh, _ := s.cli.ContainerWait(s.ctx, reader.ID, container.WaitConditionNotRunning)
	<-statusCh

	// 验证数据
	logReader, err := s.cli.ContainerLogs(s.ctx, reader.ID, types.ContainerLogsOptions{
		ShowStdout: true,
	})
	s.Require().NoError(err)
	logBytes, _ := io.ReadAll(logReader)
	logReader.Close()

	content := string(logBytes)
	s.Assert().Contains(content, "data from container 0")
	s.Assert().Contains(content, "data from container 1")
	s.T().Log("✅ 验证共享数据成功")
}

// ====================
// 3. 容器 + 网络 + 卷 三方联动测试
// ====================

// TestIntegration_Full_ContainerNetworkVolume 测试完整联动场景
func (s *DockerIntegrationTestSuite) TestIntegration_Full_ContainerNetworkVolume() {
	s.T().Log("=== 测试：容器+网络+卷 完整联动 ===")

	// 1. 创建网络
	networkResp, err := s.cli.NetworkCreate(s.ctx, fmt.Sprintf("full-network-%d", time.Now().Unix()), types.NetworkCreate{
		Driver: "bridge",
	})
	s.Require().NoError(err)
	defer s.cli.NetworkRemove(s.ctx, networkResp.ID)
	s.T().Log("✅ 创建网络")

	// 2. 创建卷
	volumeName := fmt.Sprintf("full-volume-%d", time.Now().Unix())
	vol, err := s.cli.VolumeCreate(s.ctx, volume.CreateOptions{
		Name: volumeName,
	})
	s.Require().NoError(err)
	defer s.cli.VolumeRemove(s.ctx, vol.Name, false)
	s.T().Log("✅ 创建卷")

	// 3. 创建数据生产者容器（写入数据到卷）
	producer, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "while true; do date >> /data/logs.txt; sleep 1; done"},
	}, &container.HostConfig{
		NetworkMode: container.NetworkMode(networkResp.ID),
		Binds:       []string{volumeName + ":/data"},
	}, nil, nil, "producer")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, producer.ID, types.ContainerRemoveOptions{Force: true})

	err = s.cli.ContainerStart(s.ctx, producer.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	s.T().Log("✅ 启动数据生产者容器")

	// 4. 等待生产数据
	time.Sleep(3 * time.Second)

	// 5. 创建数据消费者容器（从卷读取数据）
	consumer, err := s.cli.ContainerCreate(s.ctx, &container.Config{
		Image: "alpine:latest",
		Cmd:   []string{"sh", "-c", "wc -l /data/logs.txt"},
	}, &container.HostConfig{
		NetworkMode: container.NetworkMode(networkResp.ID),
		Binds:       []string{volumeName + ":/data:ro"},
	}, nil, nil, "consumer")
	s.Require().NoError(err)
	defer s.cli.ContainerRemove(s.ctx, consumer.ID, types.ContainerRemoveOptions{})

	err = s.cli.ContainerStart(s.ctx, consumer.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	statusCh, _ := s.cli.ContainerWait(s.ctx, consumer.ID, container.WaitConditionNotRunning)
	<-statusCh

	// 6. 验证数据
	logReader, err := s.cli.ContainerLogs(s.ctx, consumer.ID, types.ContainerLogsOptions{
		ShowStdout: true,
	})
	s.Require().NoError(err)
	logBytes, _ := io.ReadAll(logReader)
	logReader.Close()

	s.T().Logf("✅ 消费者读取到: %s", strings.TrimSpace(string(logBytes)))
	s.Assert().Contains(string(logBytes), "/data/logs.txt", "应该成功读取数据")

	s.T().Log("=== 完整联动测试成功 ===")
}

// TestDockerIntegrationTestSuite 运行集成测试套件
func TestDockerIntegrationTestSuite(t *testing.T) {
	suite.Run(t, new(DockerIntegrationTestSuite))
}
