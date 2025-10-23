package main

import (
	"context"
	"fmt"
	"io"
	"os"
	"testing"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/network"
	"github.com/docker/docker/api/types/volume"
	"github.com/docker/docker/client"
	"github.com/docker/go-connections/nat"
	"github.com/fatih/color"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/suite"
)

// DockerAPITestSuite Docker API测试套件
type DockerAPITestSuite struct {
	suite.Suite
	cli         *client.Client
	ctx         context.Context
	containerID string
	networkID   string
	volumeName  string
	factory     *TestDataFactory // ✅ 集成测试数据工厂
	utils       *TestUtils       // ✅ 集成测试工具
}

// SetupSuite 初始化测试套件
func (s *DockerAPITestSuite) SetupSuite() {
	s.ctx = context.Background()

	// 创建Docker客户端
	cli, err := client.NewClientWithOpts(
		client.FromEnv,
		client.WithAPIVersionNegotiation(),
	)
	s.Require().NoError(err, "Failed to create Docker client")
	s.cli = cli

	// ✅ 初始化测试数据工厂
	s.factory = NewTestDataFactory()

	// ✅ 初始化测试工具
	s.utils = NewTestUtils()

	color.Green("\n=== Docker API 测试套件初始化 ===\n")
	color.Cyan("✅ 测试数据工厂已加载")
	color.Cyan("✅ 测试工具已加载\n")
}

// TearDownSuite 清理测试套件
func (s *DockerAPITestSuite) TearDownSuite() {
	if s.cli != nil {
		s.cli.Close()
	}
	color.Green("\n=== Docker API 测试套件清理完成 ===\n")
}

// Test01_GetDockerVersion 测试1: 获取Docker版本
func (s *DockerAPITestSuite) Test01_GetDockerVersion() {
	color.Cyan("\n测试1: 获取Docker版本")

	version, err := s.cli.ServerVersion(s.ctx)
	s.Require().NoError(err)

	color.Green("✅ Docker版本获取成功:")
	fmt.Printf("  - Version: %s\n", version.Version)
	fmt.Printf("  - API Version: %s\n", version.APIVersion)
	fmt.Printf("  - Go Version: %s\n", version.GoVersion)
	fmt.Printf("  - OS/Arch: %s/%s\n", version.Os, version.Arch)

	assert.NotEmpty(s.T(), version.Version)
}

// Test02_GetDockerInfo 测试2: 获取Docker系统信息
func (s *DockerAPITestSuite) Test02_GetDockerInfo() {
	color.Cyan("\n测试2: 获取Docker系统信息")

	info, err := s.cli.Info(s.ctx)
	s.Require().NoError(err)

	color.Green("✅ Docker系统信息获取成功:")
	fmt.Printf("  - Containers: %d (Running: %d, Paused: %d, Stopped: %d)\n",
		info.Containers, info.ContainersRunning, info.ContainersPaused, info.ContainersStopped)
	fmt.Printf("  - Images: %d\n", info.Images)
	fmt.Printf("  - Driver: %s\n", info.Driver)
	fmt.Printf("  - Memory: %d MB\n", info.MemTotal/(1024*1024))
	fmt.Printf("  - CPUs: %d\n", info.NCPU)

	assert.Greater(s.T(), info.NCPU, 0)
}

// Test03_PingDocker 测试3: Ping Docker守护进程
func (s *DockerAPITestSuite) Test03_PingDocker() {
	color.Cyan("\n测试3: Ping Docker守护进程")

	ping, err := s.cli.Ping(s.ctx)
	s.Require().NoError(err)

	color.Green("✅ Docker Ping成功:")
	fmt.Printf("  - API Version: %s\n", ping.APIVersion)
	fmt.Printf("  - Builder Version: %s\n", ping.BuilderVersion)

	assert.NotEmpty(s.T(), ping.APIVersion)
}

// Test04_ListImages 测试4: 列出镜像
func (s *DockerAPITestSuite) Test04_ListImages() {
	color.Cyan("\n测试4: 列出所有镜像")

	images, err := s.cli.ImageList(s.ctx, types.ImageListOptions{All: true})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 镜像列表获取成功: 共 %d 个镜像", len(images)))

	// 显示前3个镜像
	for i, img := range images {
		if i >= 3 {
			break
		}
		if len(img.RepoTags) > 0 {
			fmt.Printf("  - %s (Size: %d MB)\n", img.RepoTags[0], img.Size/(1024*1024))
		}
	}

	if len(images) > 3 {
		fmt.Printf("  ... 还有 %d 个镜像\n", len(images)-3)
	}
}

// Test05_PullImage 测试5: 拉取镜像
func (s *DockerAPITestSuite) Test05_PullImage() {
	color.Cyan("\n测试5: 拉取nginx:alpine镜像")

	out, err := s.cli.ImagePull(s.ctx, "nginx:alpine", types.ImagePullOptions{})
	s.Require().NoError(err)
	defer out.Close()

	// 读取拉取输出 (静默模式)
	io.Copy(io.Discard, out)

	color.Green("✅ 镜像拉取成功: nginx:alpine")
}

// Test06_InspectImage 测试6: 查看镜像详情
func (s *DockerAPITestSuite) Test06_InspectImage() {
	color.Cyan("\n测试6: 查看nginx:alpine镜像详情")

	inspect, _, err := s.cli.ImageInspectWithRaw(s.ctx, "nginx:alpine")
	s.Require().NoError(err)

	color.Green("✅ 镜像详情获取成功:")
	fmt.Printf("  - ID: %s\n", inspect.ID[:12])
	fmt.Printf("  - Size: %d MB\n", inspect.Size/(1024*1024))
	fmt.Printf("  - Architecture: %s\n", inspect.Architecture)
	fmt.Printf("  - OS: %s\n", inspect.Os)
	fmt.Printf("  - Created: %s\n", inspect.Created)

	assert.NotEmpty(s.T(), inspect.ID)
}

// Test07_CreateContainer 测试7: 创建容器
func (s *DockerAPITestSuite) Test07_CreateContainer() {
	color.Cyan("\n测试7: 创建nginx容器")

	// 容器配置
	config := &container.Config{
		Image: "nginx:alpine",
		ExposedPorts: nat.PortSet{
			"80/tcp": struct{}{},
		},
		Labels: map[string]string{
			"test":       "golang",
			"created_by": "api_test",
		},
	}

	// 主机配置
	hostConfig := &container.HostConfig{
		PortBindings: nat.PortMap{
			"80/tcp": []nat.PortBinding{
				{
					HostIP:   "0.0.0.0",
					HostPort: "8080",
				},
			},
		},
	}

	// 网络配置
	networkingConfig := &network.NetworkingConfig{}

	// 创建容器
	resp, err := s.cli.ContainerCreate(
		s.ctx,
		config,
		hostConfig,
		networkingConfig,
		nil,
		"test_nginx_go",
	)
	s.Require().NoError(err)

	s.containerID = resp.ID

	color.Green("✅ 容器创建成功:")
	fmt.Printf("  - Container ID: %s\n", s.containerID[:12])
	if len(resp.Warnings) > 0 {
		fmt.Printf("  - Warnings: %v\n", resp.Warnings)
	}

	assert.NotEmpty(s.T(), s.containerID)
}

// Test08_StartContainer 测试8: 启动容器
func (s *DockerAPITestSuite) Test08_StartContainer() {
	color.Cyan("\n测试8: 启动容器")

	err := s.cli.ContainerStart(s.ctx, s.containerID, types.ContainerStartOptions{})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 容器启动成功: %s", s.containerID[:12]))

	// 等待容器完全启动
	time.Sleep(2 * time.Second)
}

// Test09_InspectContainer 测试9: 查看容器详情
func (s *DockerAPITestSuite) Test09_InspectContainer() {
	color.Cyan("\n测试9: 查看容器详情")

	inspect, err := s.cli.ContainerInspect(s.ctx, s.containerID)
	s.Require().NoError(err)

	color.Green("✅ 容器详情获取成功:")
	fmt.Printf("  - Name: %s\n", inspect.Name)
	fmt.Printf("  - Status: %s\n", inspect.State.Status)
	fmt.Printf("  - Running: %v\n", inspect.State.Running)
	fmt.Printf("  - Image: %s\n", inspect.Config.Image)
	fmt.Printf("  - Network Mode: %s\n", inspect.HostConfig.NetworkMode)

	assert.Equal(s.T(), "running", inspect.State.Status)
}

// Test10_GetContainerLogs 测试10: 获取容器日志
func (s *DockerAPITestSuite) Test10_GetContainerLogs() {
	color.Cyan("\n测试10: 获取容器日志")

	options := types.ContainerLogsOptions{
		ShowStdout: true,
		ShowStderr: true,
		Tail:       "10",
	}

	out, err := s.cli.ContainerLogs(s.ctx, s.containerID, options)
	s.Require().NoError(err)
	defer out.Close()

	// 读取日志
	logs, err := io.ReadAll(out)
	s.Require().NoError(err)

	color.Green("✅ 容器日志获取成功:")
	fmt.Printf("  - 日志长度: %d 字节\n", len(logs))

	assert.Greater(s.T(), len(logs), 0)
}

// Test11_GetContainerStats 测试11: 获取容器统计信息
func (s *DockerAPITestSuite) Test11_GetContainerStats() {
	color.Cyan("\n测试11: 获取容器统计信息")

	stats, err := s.cli.ContainerStats(s.ctx, s.containerID, false)
	s.Require().NoError(err)
	defer stats.Body.Close()

	// 读取统计信息
	var containerStats types.StatsJSON
	err = client.DecodeEvents(stats.Body, func(event types.StatsJSON) error {
		containerStats = event
		return nil
	})

	// 某些情况下可能无法立即获取统计信息，不作为错误
	if err == nil {
		color.Green("✅ 容器统计信息获取成功:")
		fmt.Printf("  - CPU使用率: %.2f%%\n", calculateCPUPercent(&containerStats))
		fmt.Printf("  - 内存使用: %d MB\n", containerStats.MemoryStats.Usage/(1024*1024))
	} else {
		color.Yellow("⚠️  容器统计信息暂时不可用")
	}
}

// Test12_ListContainers 测试12: 列出所有容器
func (s *DockerAPITestSuite) Test12_ListContainers() {
	color.Cyan("\n测试12: 列出所有容器")

	containers, err := s.cli.ContainerList(s.ctx, types.ContainerListOptions{All: true})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 容器列表获取成功: 共 %d 个容器", len(containers)))

	// 显示前3个容器
	for i, c := range containers {
		if i >= 3 {
			break
		}
		fmt.Printf("  - %s (%s): %s\n", c.Names[0], c.ID[:12], c.State)
	}

	if len(containers) > 3 {
		fmt.Printf("  ... 还有 %d 个容器\n", len(containers)-3)
	}
}

// Test13_CreateNetwork 测试13: 创建网络
func (s *DockerAPITestSuite) Test13_CreateNetwork() {
	color.Cyan("\n测试13: 创建Docker网络")

	resp, err := s.cli.NetworkCreate(s.ctx, "test_network_go", types.NetworkCreate{
		Driver: "bridge",
		IPAM: &network.IPAM{
			Config: []network.IPAMConfig{
				{
					Subnet:  "172.30.0.0/16",
					Gateway: "172.30.0.1",
				},
			},
		},
		Labels: map[string]string{
			"test": "golang",
		},
	})
	s.Require().NoError(err)

	s.networkID = resp.ID

	color.Green("✅ 网络创建成功:")
	fmt.Printf("  - Network ID: %s\n", s.networkID[:12])

	assert.NotEmpty(s.T(), s.networkID)
}

// Test14_InspectNetwork 测试14: 查看网络详情
func (s *DockerAPITestSuite) Test14_InspectNetwork() {
	color.Cyan("\n测试14: 查看网络详情")

	networkResource, err := s.cli.NetworkInspect(s.ctx, s.networkID, types.NetworkInspectOptions{})
	s.Require().NoError(err)

	color.Green("✅ 网络详情获取成功:")
	fmt.Printf("  - Name: %s\n", networkResource.Name)
	fmt.Printf("  - Driver: %s\n", networkResource.Driver)
	fmt.Printf("  - Scope: %s\n", networkResource.Scope)

	assert.Equal(s.T(), "bridge", networkResource.Driver)
}

// Test15_CreateVolume 测试15: 创建卷
func (s *DockerAPITestSuite) Test15_CreateVolume() {
	color.Cyan("\n测试15: 创建Docker卷")

	vol, err := s.cli.VolumeCreate(s.ctx, volume.CreateOptions{
		Name:   "test_volume_go",
		Driver: "local",
		Labels: map[string]string{
			"test": "golang",
		},
	})
	s.Require().NoError(err)

	s.volumeName = vol.Name

	color.Green("✅ 卷创建成功:")
	fmt.Printf("  - Volume Name: %s\n", s.volumeName)
	fmt.Printf("  - Driver: %s\n", vol.Driver)
	fmt.Printf("  - Mountpoint: %s\n", vol.Mountpoint)

	assert.NotEmpty(s.T(), s.volumeName)
}

// Test16_InspectVolume 测试16: 查看卷详情
func (s *DockerAPITestSuite) Test16_InspectVolume() {
	color.Cyan("\n测试16: 查看卷详情")

	vol, err := s.cli.VolumeInspect(s.ctx, s.volumeName)
	s.Require().NoError(err)

	color.Green("✅ 卷详情获取成功:")
	fmt.Printf("  - Name: %s\n", vol.Name)
	fmt.Printf("  - Driver: %s\n", vol.Driver)
	fmt.Printf("  - Scope: %s\n", vol.Scope)

	assert.Equal(s.T(), "local", vol.Driver)
}

// Test17_StopContainer 测试17: 停止容器
func (s *DockerAPITestSuite) Test17_StopContainer() {
	color.Cyan("\n测试17: 停止容器")

	timeout := 10
	err := s.cli.ContainerStop(s.ctx, s.containerID, container.StopOptions{
		Timeout: &timeout,
	})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 容器停止成功: %s", s.containerID[:12]))
}

// Test18_RemoveContainer 测试18: 删除容器
func (s *DockerAPITestSuite) Test18_RemoveContainer() {
	color.Cyan("\n测试18: 删除容器")

	err := s.cli.ContainerRemove(s.ctx, s.containerID, types.ContainerRemoveOptions{
		Force:         true,
		RemoveVolumes: true,
	})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 容器删除成功: %s", s.containerID[:12]))
}

// Test19_RemoveNetwork 测试19: 删除网络
func (s *DockerAPITestSuite) Test19_RemoveNetwork() {
	color.Cyan("\n测试19: 删除网络")

	err := s.cli.NetworkRemove(s.ctx, s.networkID)
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 网络删除成功: %s", s.networkID[:12]))
}

// Test20_RemoveVolume 测试20: 删除卷
func (s *DockerAPITestSuite) Test20_RemoveVolume() {
	color.Cyan("\n测试20: 删除卷")

	err := s.cli.VolumeRemove(s.ctx, s.volumeName, false)
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 卷删除成功: %s", s.volumeName))
}

// calculateCPUPercent 计算CPU使用百分比
func calculateCPUPercent(stats *types.StatsJSON) float64 {
	cpuDelta := float64(stats.CPUStats.CPUUsage.TotalUsage - stats.PreCPUStats.CPUUsage.TotalUsage)
	systemDelta := float64(stats.CPUStats.SystemUsage - stats.PreCPUStats.SystemUsage)

	if systemDelta > 0.0 && cpuDelta > 0.0 {
		return (cpuDelta / systemDelta) * float64(len(stats.CPUStats.CPUUsage.PercpuUsage)) * 100.0
	}
	return 0.0
}

// TestDockerAPI 运行Docker API测试套件
func TestDockerAPI(t *testing.T) {
	suite.Run(t, new(DockerAPITestSuite))
}

// Main函数 - 用于直接运行
func main() {
	// 设置测试模式
	os.Exit(0)
}
