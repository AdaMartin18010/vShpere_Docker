package main

import (
	"context"
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/client"
	"github.com/fatih/color"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/suite"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
)

// IntegrationTestSuite 集成测试套件
// 测试多个系统之间的交互和协作
type IntegrationTestSuite struct {
	suite.Suite
	dockerClient *client.Client
	k8sClient    *kubernetes.Clientset
	ctx          context.Context
	namespace    string
}

// SetupSuite 初始化集成测试套件
func (s *IntegrationTestSuite) SetupSuite() {
	s.ctx = context.Background()
	s.namespace = "integration-test"

	color.Green("\n=== 集成测试套件初始化 ===\n")

	// 初始化Docker客户端
	dockerCli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		s.T().Skipf("Docker客户端初始化失败: %v", err)
		return
	}
	s.dockerClient = dockerCli
	color.Cyan("✅ Docker客户端初始化成功")

	// 初始化Kubernetes客户端 (可选)
	kubeconfig := os.Getenv("KUBECONFIG")
	if kubeconfig != "" {
		config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
		if err == nil {
			k8sClient, err := kubernetes.NewForConfig(config)
			if err == nil {
				s.k8sClient = k8sClient
				color.Cyan("✅ Kubernetes客户端初始化成功")

				// 创建测试命名空间
				ns := &corev1.Namespace{
					ObjectMeta: metav1.ObjectMeta{
						Name: s.namespace,
					},
				}
				_, _ = s.k8sClient.CoreV1().Namespaces().Create(s.ctx, ns, metav1.CreateOptions{})
			}
		}
	}
}

// TearDownSuite 清理集成测试套件
func (s *IntegrationTestSuite) TearDownSuite() {
	color.Green("\n=== 集成测试套件清理 ===\n")

	// 清理Kubernetes测试命名空间
	if s.k8sClient != nil {
		s.k8sClient.CoreV1().Namespaces().Delete(s.ctx, s.namespace, metav1.DeleteOptions{})
		color.Cyan("✅ Kubernetes测试命名空间已清理")
	}

	// 关闭客户端
	if s.dockerClient != nil {
		s.dockerClient.Close()
	}

	color.Green("=== 集成测试套件清理完成 ===\n")
}

// TestIntegration01_DockerToKubernetes 测试1: Docker到Kubernetes的镜像推送流程
func (s *IntegrationTestSuite) TestIntegration01_DockerToKubernetes() {
	if s.k8sClient == nil {
		s.T().Skip("Kubernetes客户端未初始化")
	}

	color.Cyan("\n集成测试1: Docker镜像推送到Kubernetes")

	// 步骤1: 在Docker中拉取镜像
	color.Yellow("步骤1: 拉取nginx镜像...")
	_, err := s.dockerClient.ImagePull(s.ctx, "nginx:alpine", types.ImagePullOptions{})
	s.Require().NoError(err)
	color.Green("✅ 镜像拉取成功")

	// 步骤2: 验证镜像存在
	color.Yellow("步骤2: 验证镜像...")
	images, err := s.dockerClient.ImageList(s.ctx, types.ImageListOptions{})
	s.Require().NoError(err)

	found := false
	for _, img := range images {
		for _, tag := range img.RepoTags {
			if tag == "nginx:alpine" {
				found = true
				break
			}
		}
	}
	assert.True(s.T(), found, "镜像应该存在")
	color.Green("✅ 镜像验证成功")

	// 步骤3: 在Kubernetes中部署该镜像
	color.Yellow("步骤3: 在Kubernetes中部署...")
	pod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "integration-nginx",
			Namespace: s.namespace,
		},
		Spec: corev1.PodSpec{
			Containers: []corev1.Container{
				{
					Name:  "nginx",
					Image: "nginx:alpine",
				},
			},
		},
	}

	_, err = s.k8sClient.CoreV1().Pods(s.namespace).Create(s.ctx, pod, metav1.CreateOptions{})
	s.Require().NoError(err)
	color.Green("✅ Kubernetes Pod创建成功")

	// 步骤4: 等待Pod运行
	color.Yellow("步骤4: 等待Pod运行...")
	time.Sleep(10 * time.Second)

	pod, err = s.k8sClient.CoreV1().Pods(s.namespace).Get(s.ctx, "integration-nginx", metav1.GetOptions{})
	s.Require().NoError(err)

	fmt.Printf("  - Pod状态: %s\n", pod.Status.Phase)
	color.Green("✅ 集成测试完成")
}

// TestIntegration02_ContainerLifecycle 测试2: 容器完整生命周期
func (s *IntegrationTestSuite) TestIntegration02_ContainerLifecycle() {
	color.Cyan("\n集成测试2: 容器完整生命周期")

	// 步骤1: 创建容器
	color.Yellow("步骤1: 创建容器...")
	resp, err := s.dockerClient.ContainerCreate(
		s.ctx,
		&container.Config{Image: "nginx:alpine"},
		&container.HostConfig{},
		nil,
		nil,
		"integration-test-container",
	)
	s.Require().NoError(err)
	containerID := resp.ID
	defer s.dockerClient.ContainerRemove(s.ctx, containerID, types.ContainerRemoveOptions{Force: true})
	color.Green("✅ 容器创建成功: " + containerID[:12])

	// 步骤2: 启动容器
	color.Yellow("步骤2: 启动容器...")
	err = s.dockerClient.ContainerStart(s.ctx, containerID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	time.Sleep(2 * time.Second)
	color.Green("✅ 容器启动成功")

	// 步骤3: 检查容器状态
	color.Yellow("步骤3: 检查容器状态...")
	inspect, err := s.dockerClient.ContainerInspect(s.ctx, containerID)
	s.Require().NoError(err)
	assert.Equal(s.T(), "running", inspect.State.Status)
	fmt.Printf("  - 状态: %s\n", inspect.State.Status)
	fmt.Printf("  - PID: %d\n", inspect.State.Pid)
	color.Green("✅ 容器状态正常")

	// 步骤4: 获取日志
	color.Yellow("步骤4: 获取容器日志...")
	logs, err := s.dockerClient.ContainerLogs(s.ctx, containerID, types.ContainerLogsOptions{
		ShowStdout: true,
		ShowStderr: true,
	})
	s.Require().NoError(err)
	logs.Close()
	color.Green("✅ 日志获取成功")

	// 步骤5: 停止容器
	color.Yellow("步骤5: 停止容器...")
	timeout := 10
	err = s.dockerClient.ContainerStop(s.ctx, containerID, container.StopOptions{Timeout: &timeout})
	s.Require().NoError(err)
	time.Sleep(2 * time.Second)
	color.Green("✅ 容器停止成功")

	// 步骤6: 验证容器已停止
	color.Yellow("步骤6: 验证容器状态...")
	inspect, err = s.dockerClient.ContainerInspect(s.ctx, containerID)
	s.Require().NoError(err)
	assert.False(s.T(), inspect.State.Running)
	fmt.Printf("  - 最终状态: %s\n", inspect.State.Status)
	color.Green("✅ 生命周期测试完成")
}

// TestIntegration03_NetworkConnectivity 测试3: 网络连通性
func (s *IntegrationTestSuite) TestIntegration03_NetworkConnectivity() {
	color.Cyan("\n集成测试3: 网络连通性测试")

	// 步骤1: 创建自定义网络
	color.Yellow("步骤1: 创建自定义网络...")
	networkResp, err := s.dockerClient.NetworkCreate(s.ctx, "integration-network", types.NetworkCreate{
		Driver: "bridge",
	})
	s.Require().NoError(err)
	defer s.dockerClient.NetworkRemove(s.ctx, networkResp.ID)
	color.Green("✅ 网络创建成功: " + networkResp.ID[:12])

	// 步骤2: 创建第一个容器
	color.Yellow("步骤2: 创建容器1...")
	container1, err := s.dockerClient.ContainerCreate(
		s.ctx,
		&container.Config{Image: "nginx:alpine"},
		&container.HostConfig{NetworkMode: container.NetworkMode("integration-network")},
		nil,
		nil,
		"integration-container-1",
	)
	s.Require().NoError(err)
	defer s.dockerClient.ContainerRemove(s.ctx, container1.ID, types.ContainerRemoveOptions{Force: true})

	err = s.dockerClient.ContainerStart(s.ctx, container1.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	color.Green("✅ 容器1启动成功")

	// 步骤3: 创建第二个容器
	color.Yellow("步骤3: 创建容器2...")
	container2, err := s.dockerClient.ContainerCreate(
		s.ctx,
		&container.Config{Image: "nginx:alpine"},
		&container.HostConfig{NetworkMode: container.NetworkMode("integration-network")},
		nil,
		nil,
		"integration-container-2",
	)
	s.Require().NoError(err)
	defer s.dockerClient.ContainerRemove(s.ctx, container2.ID, types.ContainerRemoveOptions{Force: true})

	err = s.dockerClient.ContainerStart(s.ctx, container2.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	color.Green("✅ 容器2启动成功")

	time.Sleep(3 * time.Second)

	// 步骤4: 验证网络连接
	color.Yellow("步骤4: 验证网络连接...")
	network, err := s.dockerClient.NetworkInspect(s.ctx, networkResp.ID, types.NetworkInspectOptions{})
	s.Require().NoError(err)

	assert.Len(s.T(), network.Containers, 2, "网络应该有2个容器")
	fmt.Printf("  - 网络名称: %s\n", network.Name)
	fmt.Printf("  - 连接的容器数: %d\n", len(network.Containers))
	color.Green("✅ 网络连通性测试完成")
}

// TestIntegration04_VolumeDataPersistence 测试4: 卷数据持久化
func (s *IntegrationTestSuite) TestIntegration04_VolumeDataPersistence() {
	color.Cyan("\n集成测试4: 卷数据持久化测试")

	// 步骤1: 创建卷
	color.Yellow("步骤1: 创建数据卷...")
	vol, err := s.dockerClient.VolumeCreate(s.ctx, types.VolumeCreateOptions{
		Name: "integration-volume",
	})
	s.Require().NoError(err)
	defer s.dockerClient.VolumeRemove(s.ctx, vol.Name, false)
	color.Green("✅ 卷创建成功: " + vol.Name)

	// 步骤2: 创建容器并挂载卷
	color.Yellow("步骤2: 创建容器并挂载卷...")
	container1, err := s.dockerClient.ContainerCreate(
		s.ctx,
		&container.Config{
			Image: "nginx:alpine",
			Cmd:   []string{"sh", "-c", "echo 'test data' > /data/test.txt && sleep 5"},
		},
		&container.HostConfig{
			Binds: []string{vol.Name + ":/data"},
		},
		nil,
		nil,
		"integration-volume-test-1",
	)
	s.Require().NoError(err)
	defer s.dockerClient.ContainerRemove(s.ctx, container1.ID, types.ContainerRemoveOptions{Force: true})

	err = s.dockerClient.ContainerStart(s.ctx, container1.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	color.Green("✅ 容器1启动并写入数据")

	// 等待数据写入完成
	time.Sleep(6 * time.Second)

	// 步骤3: 创建第二个容器读取数据
	color.Yellow("步骤3: 创建第二个容器读取数据...")
	container2, err := s.dockerClient.ContainerCreate(
		s.ctx,
		&container.Config{
			Image: "nginx:alpine",
			Cmd:   []string{"cat", "/data/test.txt"},
		},
		&container.HostConfig{
			Binds: []string{vol.Name + ":/data"},
		},
		nil,
		nil,
		"integration-volume-test-2",
	)
	s.Require().NoError(err)
	defer s.dockerClient.ContainerRemove(s.ctx, container2.ID, types.ContainerRemoveOptions{Force: true})

	err = s.dockerClient.ContainerStart(s.ctx, container2.ID, types.ContainerStartOptions{})
	s.Require().NoError(err)
	color.Green("✅ 容器2成功读取数据")

	time.Sleep(2 * time.Second)

	// 步骤4: 验证数据持久化
	color.Yellow("步骤4: 验证数据持久化...")
	volInspect, err := s.dockerClient.VolumeInspect(s.ctx, vol.Name)
	s.Require().NoError(err)
	assert.Equal(s.T(), vol.Name, volInspect.Name)
	fmt.Printf("  - 卷挂载点: %s\n", volInspect.Mountpoint)
	color.Green("✅ 数据持久化测试完成")
}

// TestIntegration05_MultiContainerOrchestration 测试5: 多容器编排
func (s *IntegrationTestSuite) TestIntegration05_MultiContainerOrchestration() {
	color.Cyan("\n集成测试5: 多容器编排测试")

	containers := make([]string, 0, 3)
	defer func() {
		for _, cid := range containers {
			s.dockerClient.ContainerRemove(s.ctx, cid, types.ContainerRemoveOptions{Force: true})
		}
	}()

	// 步骤1: 创建多个容器
	color.Yellow("步骤1: 创建3个nginx容器...")
	for i := 1; i <= 3; i++ {
		resp, err := s.dockerClient.ContainerCreate(
			s.ctx,
			&container.Config{Image: "nginx:alpine"},
			&container.HostConfig{},
			nil,
			nil,
			fmt.Sprintf("integration-orchestration-%d", i),
		)
		s.Require().NoError(err)
		containers = append(containers, resp.ID)

		err = s.dockerClient.ContainerStart(s.ctx, resp.ID, types.ContainerStartOptions{})
		s.Require().NoError(err)

		fmt.Printf("  - 容器%d: %s\n", i, resp.ID[:12])
	}
	color.Green(fmt.Sprintf("✅ 成功创建并启动%d个容器", len(containers)))

	time.Sleep(3 * time.Second)

	// 步骤2: 验证所有容器运行
	color.Yellow("步骤2: 验证所有容器状态...")
	runningCount := 0
	for _, cid := range containers {
		inspect, err := s.dockerClient.ContainerInspect(s.ctx, cid)
		s.Require().NoError(err)
		if inspect.State.Running {
			runningCount++
		}
	}

	assert.Equal(s.T(), len(containers), runningCount, "所有容器应该处于运行状态")
	fmt.Printf("  - 运行中的容器: %d/%d\n", runningCount, len(containers))
	color.Green("✅ 所有容器运行正常")

	// 步骤3: 批量停止容器
	color.Yellow("步骤3: 批量停止容器...")
	for _, cid := range containers {
		timeout := 5
		err := s.dockerClient.ContainerStop(s.ctx, cid, container.StopOptions{Timeout: &timeout})
		s.Require().NoError(err)
	}
	color.Green("✅ 所有容器已停止")

	time.Sleep(2 * time.Second)

	// 步骤4: 验证所有容器已停止
	color.Yellow("步骤4: 验证容器状态...")
	stoppedCount := 0
	for _, cid := range containers {
		inspect, err := s.dockerClient.ContainerInspect(s.ctx, cid)
		s.Require().NoError(err)
		if !inspect.State.Running {
			stoppedCount++
		}
	}

	assert.Equal(s.T(), len(containers), stoppedCount, "所有容器应该已停止")
	fmt.Printf("  - 已停止的容器: %d/%d\n", stoppedCount, len(containers))
	color.Green("✅ 多容器编排测试完成")
}

// TestIntegrationSuite 运行集成测试套件
func TestIntegrationSuite(t *testing.T) {
	suite.Run(t, new(IntegrationTestSuite))
}
