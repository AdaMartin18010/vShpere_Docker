package main

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/docker/docker/client"
	"github.com/fatih/color"
	"github.com/stretchr/testify/suite"
)

// IntegratedExampleTestSuite 完整功能集成示例测试套件
// 展示如何在实际测试中使用test_factory和test_utils
type IntegratedExampleTestSuite struct {
	suite.Suite
	dockerClient *client.Client
	factory      *TestDataFactory
	utils        *TestUtils
	ctx          context.Context
}

// SetupSuite 初始化测试套件
func (s *IntegratedExampleTestSuite) SetupSuite() {
	s.ctx = context.Background()

	// 初始化Docker客户端
	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	s.Require().NoError(err)
	s.dockerClient = cli

	// ✅ 初始化测试数据工厂
	s.factory = NewTestDataFactory()

	// ✅ 初始化测试工具
	s.utils = NewTestUtils()

	color.Green("\n=== 功能集成示例测试套件初始化 ===\n")
	color.Cyan("✅ 测试数据工厂: 已加载")
	color.Cyan("✅ 测试工具函数: 已加载")
	color.Cyan("✅ Docker客户端: 已连接\n")
}

// TearDownSuite 清理测试套件
func (s *IntegratedExampleTestSuite) TearDownSuite() {
	if s.dockerClient != nil {
		s.dockerClient.Close()
	}

	// ✅ 使用测试工具进行最终清理
	color.Yellow("\n正在清理所有测试资源...")
	s.utils.CleanupDockerContainers(s.ctx, s.dockerClient, "test")
	s.utils.CleanupDockerNetworks(s.ctx, s.dockerClient, "test")
	s.utils.CleanupDockerVolumes(s.ctx, s.dockerClient, "test")

	color.Green("=== 功能集成示例测试套件清理完成 ===\n")
}

// TestExample01_UsingFactoryToCreateContainer 示例1: 使用工厂创建容器
func (s *IntegratedExampleTestSuite) TestExample01_UsingFactoryToCreateContainer() {
	color.Cyan("\n示例1: 使用测试数据工厂创建容器")

	// ✅ 使用工厂生成随机测试名称
	containerName := s.factory.GenerateTestName("demo-container")
	color.Yellow("  📝 生成容器名称: %s", containerName)

	// ✅ 使用工厂创建容器配置（链式调用）
	config := s.factory.CreateDockerContainerConfig(
		"nginx:alpine",
		WithContainerCmd("sh", "-c", "echo 'Hello from Factory!' && nginx -g 'daemon off;'"),
		WithContainerEnv("ENV=test", "DEBUG=true"),
		WithContainerPorts("80/tcp"),
		WithContainerLabels(map[string]string{
			"app":         "demo",
			"environment": "test",
		}),
	)
	color.Green("  ✅ 容器配置创建成功（使用工厂模式）")

	// ✅ 使用工厂创建主机配置
	hostConfig := s.factory.CreateDockerHostConfig(
		WithPortBinding("80/tcp", fmt.Sprintf("%d", s.factory.RandomPort())),
		WithNetworkMode("bridge"),
	)
	color.Green("  ✅ 主机配置创建成功（随机端口绑定）")

	// 创建容器
	resp, err := s.dockerClient.ContainerCreate(s.ctx, config, hostConfig, nil, nil, containerName)
	s.Require().NoError(err)
	defer s.dockerClient.ContainerRemove(s.ctx, resp.ID, client.ContainerRemoveOptions{Force: true})

	color.Green("  ✅ 容器创建成功: %s", resp.ID[:12])

	// 启动容器
	err = s.dockerClient.ContainerStart(s.ctx, resp.ID, client.StartOptions{})
	s.Require().NoError(err)

	// ✅ 使用测试工具等待容器运行
	color.Yellow("  ⏳ 等待容器启动...")
	err = s.utils.WaitForContainerRunning(s.ctx, s.dockerClient, resp.ID, 30*time.Second)
	s.Require().NoError(err)
	color.Green("  ✅ 容器已运行")

	// ✅ 使用测试工具断言容器状态
	err = s.utils.AssertContainerRunning(s.ctx, s.dockerClient, resp.ID)
	s.Require().NoError(err)
	color.Green("  ✅ 容器状态验证通过")

	fmt.Println()
}

// TestExample02_UsingUtilsForRetry 示例2: 使用工具进行重试
func (s *IntegratedExampleTestSuite) TestExample02_UsingUtilsForRetry() {
	color.Cyan("\n示例2: 使用测试工具的重试机制")

	attemptCount := 0
	maxAttempts := 3

	// ✅ 使用测试工具的重试机制
	color.Yellow("  ⏳ 尝试连接Docker (最多%d次)...", maxAttempts)
	err := s.utils.Retry(maxAttempts, time.Second, func() error {
		attemptCount++
		color.Cyan("    - 尝试 %d/%d", attemptCount, maxAttempts)

		// 模拟可能失败的操作
		_, err := s.dockerClient.Ping(s.ctx)
		return err
	})

	s.Require().NoError(err)
	color.Green("  ✅ 连接成功 (共尝试%d次)", attemptCount)

	fmt.Println()
}

// TestExample03_UsingUtilsForPerformance 示例3: 使用工具进行性能测试
func (s *IntegratedExampleTestSuite) TestExample03_UsingUtilsForPerformance() {
	color.Cyan("\n示例3: 使用测试工具进行性能测试")

	// ✅ 使用测试工具的性能测试功能
	color.Yellow("  ⏱️  开始性能测试 (100次操作)...")
	result := s.utils.Benchmark(100, func() error {
		_, err := s.dockerClient.Ping(s.ctx)
		return err
	})

	// ✅ 使用测试工具格式化结果
	color.Green("  ✅ 性能测试完成:")
	fmt.Print(s.utils.FormatBenchmarkResult(result))

	// 验证性能指标
	s.Require().Equal(100, result.Operations, "操作次数应该是100")
	s.Require().Zero(result.ErrorCount, "不应该有错误")
	s.Require().True(result.AverageDuration < time.Second, "平均耗时应该小于1秒")

	fmt.Println()
}

// TestExample04_CompleteWorkflow 示例4: 完整工作流集成
func (s *IntegratedExampleTestSuite) TestExample04_CompleteWorkflow() {
	color.Cyan("\n示例4: 完整工作流 - 集成所有工具")

	// 步骤1: 使用工厂创建网络配置
	color.Yellow("  📋 步骤1: 创建测试网络...")
	networkConfig := s.factory.CreateDockerNetworkConfig("bridge")
	networkResp, err := s.dockerClient.NetworkCreate(s.ctx, s.factory.GenerateTestName("test-network"), networkConfig)
	s.Require().NoError(err)
	defer s.dockerClient.NetworkRemove(s.ctx, networkResp.ID)
	color.Green("  ✅ 网络创建成功: %s", networkResp.ID[:12])

	// 步骤2: 使用工厂创建卷配置
	color.Yellow("  📋 步骤2: 创建测试卷...")
	volumeConfig := s.factory.CreateDockerVolumeConfig()
	volumeResp, err := s.dockerClient.VolumeCreate(s.ctx, volumeConfig)
	s.Require().NoError(err)
	defer s.dockerClient.VolumeRemove(s.ctx, volumeResp.Name, false)
	color.Green("  ✅ 卷创建成功: %s", volumeResp.Name)

	// 步骤3: 使用工厂创建容器（连接网络和卷）
	color.Yellow("  📋 步骤3: 创建容器并挂载卷...")
	containerConfig := s.factory.CreateDockerContainerConfig(
		"nginx:alpine",
		WithContainerLabels(map[string]string{"workflow": "complete"}),
	)
	hostConfig := s.factory.CreateDockerHostConfig(
		WithNetworkMode(networkResp.ID),
		WithVolumeBinding(fmt.Sprintf("%s:/data", volumeResp.Name)),
	)

	containerName := s.factory.GenerateTestName("workflow-container")
	containerResp, err := s.dockerClient.ContainerCreate(s.ctx, containerConfig, hostConfig, nil, nil, containerName)
	s.Require().NoError(err)
	defer s.dockerClient.ContainerRemove(s.ctx, containerResp.ID, client.ContainerRemoveOptions{Force: true})
	color.Green("  ✅ 容器创建成功: %s", containerResp.ID[:12])

	// 步骤4: 启动容器并使用工具等待
	color.Yellow("  📋 步骤4: 启动容器并等待运行...")
	err = s.dockerClient.ContainerStart(s.ctx, containerResp.ID, client.StartOptions{})
	s.Require().NoError(err)

	// ✅ 使用工具的测量时间功能
	duration, err := s.utils.MeasureTime(func() error {
		return s.utils.WaitForContainerRunning(s.ctx, s.dockerClient, containerResp.ID, 30*time.Second)
	})
	s.Require().NoError(err)
	color.Green("  ✅ 容器启动成功 (耗时: %v)", duration)

	// 步骤5: 验证容器状态
	color.Yellow("  📋 步骤5: 验证容器状态...")
	err = s.utils.AssertContainerRunning(s.ctx, s.dockerClient, containerResp.ID)
	s.Require().NoError(err)
	color.Green("  ✅ 容器状态验证通过")

	// 步骤6: 停止容器
	color.Yellow("  📋 步骤6: 停止容器...")
	timeout := 10
	err = s.dockerClient.ContainerStop(s.ctx, containerResp.ID, client.StopOptions{Timeout: &timeout})
	s.Require().NoError(err)

	// ✅ 使用工具等待容器停止
	err = s.utils.WaitForContainerStopped(s.ctx, s.dockerClient, containerResp.ID, 15*time.Second)
	s.Require().NoError(err)
	color.Green("  ✅ 容器已停止")

	color.Green("\n  🎉 完整工作流测试成功！")
	fmt.Println()
}

// TestExample05_DatasetUsage 示例5: 使用预定义数据集
func (s *IntegratedExampleTestSuite) TestExample05_DatasetUsage() {
	color.Cyan("\n示例5: 使用测试数据集")

	// ✅ 使用工厂的测试数据集
	datasets := s.factory.CreateTestDatasets()
	color.Yellow("  📦 加载测试数据集: %d个数据集", len(datasets))

	for _, dataset := range datasets {
		color.Cyan("  📋 数据集: %s", dataset.Name)
		color.Cyan("     描述: %s", dataset.Description)

		// 根据数据集类型处理
		switch dataset.Name {
		case "容器镜像列表":
			if images, ok := dataset.Data["images"].([]string); ok {
				color.Green("     ✅ 包含 %d 个镜像", len(images))
				for i, img := range images {
					if i < 3 { // 只显示前3个
						fmt.Printf("        - %s\n", img)
					}
				}
			}

		case "测试端口映射":
			if mappings, ok := dataset.Data["mappings"].(map[string]string); ok {
				color.Green("     ✅ 包含 %d 个端口映射", len(mappings))
			}

		case "环境变量模板":
			if envs, ok := dataset.Data["common"].(map[string]string); ok {
				color.Green("     ✅ 包含 %d 个环境变量", len(envs))
			}
		}
	}

	color.Green("\n  ✅ 数据集测试完成")
	fmt.Println()
}

// TestExample06_PerformanceTestConfig 示例6: 使用性能测试配置
func (s *IntegratedExampleTestSuite) TestExample06_PerformanceTestConfig() {
	color.Cyan("\n示例6: 使用性能测试配置")

	// ✅ 使用工厂的性能测试配置
	configs := []string{"light", "medium", "heavy"}

	for _, preset := range configs {
		config := s.factory.CreatePerformanceTestConfig(preset)
		color.Yellow("  📊 配置预设: %s", preset)
		color.Cyan("     - 并发请求: %d", config.ConcurrentRequests)
		color.Cyan("     - 总请求数: %d", config.TotalRequests)
		color.Cyan("     - 超时时间: %v", config.Timeout)
		color.Cyan("     - 爬坡时间: %v", config.RampUpTime)
	}

	// 使用light配置进行实际测试
	color.Yellow("\n  ⏱️  使用light配置进行测试...")
	lightConfig := s.factory.CreatePerformanceTestConfig("light")

	result := s.utils.Benchmark(lightConfig.TotalRequests, func() error {
		_, err := s.dockerClient.Ping(s.ctx)
		return err
	})

	color.Green("  ✅ 性能测试完成:")
	fmt.Printf("     - 成功率: %.2f%%\n", float64(result.Operations-result.ErrorCount)/float64(result.Operations)*100)
	fmt.Printf("     - 平均耗时: %v\n", result.AverageDuration)

	fmt.Println()
}

// TestExample07_RandomDataGeneration 示例7: 随机数据生成
func (s *IntegratedExampleTestSuite) TestExample07_RandomDataGeneration() {
	color.Cyan("\n示例7: 使用随机数据生成器")

	// ✅ 使用工厂的随机数据生成器
	color.Yellow("  🎲 生成随机测试数据:")

	// 生成随机字符串
	randomStr := s.factory.RandomString(10)
	color.Green("     ✅ 随机字符串: %s", randomStr)

	// 生成随机端口
	randomPort := s.factory.RandomPort()
	color.Green("     ✅ 随机端口: %d", randomPort)
	s.Require().GreaterOrEqual(randomPort, 10000)
	s.Require().LessOrEqual(randomPort, 65535)

	// 生成随机IP
	randomIP := s.factory.RandomIPv4()
	color.Green("     ✅ 随机IP: %s", randomIP)

	// 生成测试名称
	testName := s.factory.GenerateTestName("test")
	color.Green("     ✅ 测试名称: %s", testName)

	color.Green("\n  ✅ 随机数据生成测试完成")
	fmt.Println()
}

// TestIntegratedExample 运行集成示例测试套件
func TestIntegratedExample(t *testing.T) {
	suite.Run(t, new(IntegratedExampleTestSuite))
}
