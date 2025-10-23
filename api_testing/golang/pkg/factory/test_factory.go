package main

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/network"
	"github.com/docker/go-connections/nat"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/util/intstr"
)

// TestDataFactory 测试数据工厂
type TestDataFactory struct {
	rand *rand.Rand
}

// NewTestDataFactory 创建测试数据工厂实例
func NewTestDataFactory() *TestDataFactory {
	return &TestDataFactory{
		rand: rand.New(rand.NewSource(time.Now().UnixNano())),
	}
}

// ====================================
// Docker测试数据工厂
// ====================================

// CreateDockerContainerConfig 创建Docker容器配置
func (f *TestDataFactory) CreateDockerContainerConfig(image string, options ...ContainerOption) *container.Config {
	config := &container.Config{
		Image: image,
		Labels: map[string]string{
			"test":       "api-test",
			"created_by": "test-factory",
			"timestamp":  time.Now().Format(time.RFC3339),
		},
	}

	for _, opt := range options {
		opt(config)
	}

	return config
}

// ContainerOption 容器配置选项
type ContainerOption func(*container.Config)

// WithContainerCmd 设置容器命令
func WithContainerCmd(cmd ...string) ContainerOption {
	return func(c *container.Config) {
		c.Cmd = cmd
	}
}

// WithContainerEnv 设置容器环境变量
func WithContainerEnv(envs ...string) ContainerOption {
	return func(c *container.Config) {
		c.Env = envs
	}
}

// WithContainerPorts 设置容器端口
func WithContainerPorts(ports ...string) ContainerOption {
	return func(c *container.Config) {
		if c.ExposedPorts == nil {
			c.ExposedPorts = make(nat.PortSet)
		}
		for _, port := range ports {
			c.ExposedPorts[nat.Port(port)] = struct{}{}
		}
	}
}

// WithContainerLabels 设置容器标签
func WithContainerLabels(labels map[string]string) ContainerOption {
	return func(c *container.Config) {
		for k, v := range labels {
			c.Labels[k] = v
		}
	}
}

// CreateDockerHostConfig 创建Docker主机配置
func (f *TestDataFactory) CreateDockerHostConfig(options ...HostConfigOption) *container.HostConfig {
	config := &container.HostConfig{
		RestartPolicy: container.RestartPolicy{
			Name: "no",
		},
	}

	for _, opt := range options {
		opt(config)
	}

	return config
}

// HostConfigOption 主机配置选项
type HostConfigOption func(*container.HostConfig)

// WithPortBinding 设置端口绑定
func WithPortBinding(containerPort, hostPort string) HostConfigOption {
	return func(h *container.HostConfig) {
		if h.PortBindings == nil {
			h.PortBindings = make(nat.PortMap)
		}
		h.PortBindings[nat.Port(containerPort)] = []nat.PortBinding{
			{HostPort: hostPort},
		}
	}
}

// WithVolumeBinding 设置卷绑定
func WithVolumeBinding(volumes ...string) HostConfigOption {
	return func(h *container.HostConfig) {
		h.Binds = append(h.Binds, volumes...)
	}
}

// WithNetworkMode 设置网络模式
func WithNetworkMode(mode string) HostConfigOption {
	return func(h *container.HostConfig) {
		h.NetworkMode = container.NetworkMode(mode)
	}
}

// CreateDockerNetworkConfig 创建Docker网络配置
func (f *TestDataFactory) CreateDockerNetworkConfig(driver string) types.NetworkCreate {
	return types.NetworkCreate{
		Driver: driver,
		IPAM: &network.IPAM{
			Config: []network.IPAMConfig{
				{
					Subnet:  fmt.Sprintf("172.%d.0.0/16", f.rand.Intn(100)+20),
					Gateway: fmt.Sprintf("172.%d.0.1", f.rand.Intn(100)+20),
				},
			},
		},
		Labels: map[string]string{
			"test":      "api-test",
			"timestamp": time.Now().Format(time.RFC3339),
		},
	}
}

// CreateDockerVolumeConfig 创建Docker卷配置
func (f *TestDataFactory) CreateDockerVolumeConfig() types.VolumeCreateOptions {
	return types.VolumeCreateOptions{
		Driver: "local",
		Labels: map[string]string{
			"test":      "api-test",
			"timestamp": time.Now().Format(time.RFC3339),
		},
	}
}

// ====================================
// Kubernetes测试数据工厂
// ====================================

// CreateK8sPod 创建Kubernetes Pod
func (f *TestDataFactory) CreateK8sPod(namespace, name, image string, options ...PodOption) *corev1.Pod {
	pod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name,
			Namespace: namespace,
			Labels: map[string]string{
				"app":        name,
				"test":       "api-test",
				"created_by": "test-factory",
			},
		},
		Spec: corev1.PodSpec{
			Containers: []corev1.Container{
				{
					Name:  name,
					Image: image,
				},
			},
			RestartPolicy: corev1.RestartPolicyAlways,
		},
	}

	for _, opt := range options {
		opt(pod)
	}

	return pod
}

// PodOption Pod配置选项
type PodOption func(*corev1.Pod)

// WithPodLabels 设置Pod标签
func WithPodLabels(labels map[string]string) PodOption {
	return func(p *corev1.Pod) {
		for k, v := range labels {
			p.ObjectMeta.Labels[k] = v
		}
	}
}

// WithPodContainerPorts 设置Pod容器端口
func WithPodContainerPorts(ports ...int32) PodOption {
	return func(p *corev1.Pod) {
		if len(p.Spec.Containers) > 0 {
			for _, port := range ports {
				p.Spec.Containers[0].Ports = append(p.Spec.Containers[0].Ports, corev1.ContainerPort{
					ContainerPort: port,
				})
			}
		}
	}
}

// WithPodEnv 设置Pod环境变量
func WithPodEnv(envs map[string]string) PodOption {
	return func(p *corev1.Pod) {
		if len(p.Spec.Containers) > 0 {
			for k, v := range envs {
				p.Spec.Containers[0].Env = append(p.Spec.Containers[0].Env, corev1.EnvVar{
					Name:  k,
					Value: v,
				})
			}
		}
	}
}

// CreateK8sService 创建Kubernetes Service
func (f *TestDataFactory) CreateK8sService(namespace, name string, selector map[string]string, port int32) *corev1.Service {
	return &corev1.Service{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name,
			Namespace: namespace,
			Labels: map[string]string{
				"test":       "api-test",
				"created_by": "test-factory",
			},
		},
		Spec: corev1.ServiceSpec{
			Selector: selector,
			Type:     corev1.ServiceTypeClusterIP,
			Ports: []corev1.ServicePort{
				{
					Port:       port,
					TargetPort: intstr.FromInt(int(port)),
					Protocol:   corev1.ProtocolTCP,
				},
			},
		},
	}
}

// CreateK8sConfigMap 创建Kubernetes ConfigMap
func (f *TestDataFactory) CreateK8sConfigMap(namespace, name string, data map[string]string) *corev1.ConfigMap {
	return &corev1.ConfigMap{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name,
			Namespace: namespace,
			Labels: map[string]string{
				"test":       "api-test",
				"created_by": "test-factory",
			},
		},
		Data: data,
	}
}

// CreateK8sSecret 创建Kubernetes Secret
func (f *TestDataFactory) CreateK8sSecret(namespace, name string, data map[string][]byte) *corev1.Secret {
	return &corev1.Secret{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name,
			Namespace: namespace,
			Labels: map[string]string{
				"test":       "api-test",
				"created_by": "test-factory",
			},
		},
		Type: corev1.SecretTypeOpaque,
		Data: data,
	}
}

// ====================================
// 随机数据生成器
// ====================================

// RandomString 生成随机字符串
func (f *TestDataFactory) RandomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyz0123456789"
	b := make([]byte, length)
	for i := range b {
		b[i] = charset[f.rand.Intn(len(charset))]
	}
	return string(b)
}

// RandomPort 生成随机端口号
func (f *TestDataFactory) RandomPort() int {
	return f.rand.Intn(65535-10000) + 10000
}

// RandomIPv4 生成随机IPv4地址
func (f *TestDataFactory) RandomIPv4() string {
	return fmt.Sprintf("192.168.%d.%d",
		f.rand.Intn(255),
		f.rand.Intn(255))
}

// GenerateTestName 生成测试名称
func (f *TestDataFactory) GenerateTestName(prefix string) string {
	return fmt.Sprintf("%s-%s-%d",
		prefix,
		f.RandomString(8),
		time.Now().Unix())
}

// ====================================
// 测试场景数据
// ====================================

// TestScenario 测试场景
type TestScenario struct {
	Name        string
	Description string
	Setup       func() error
	Test        func() error
	Teardown    func() error
}

// CreateCommonTestScenarios 创建常见测试场景
func (f *TestDataFactory) CreateCommonTestScenarios() []TestScenario {
	return []TestScenario{
		{
			Name:        "基础容器生命周期",
			Description: "测试容器的创建、启动、停止和删除",
			Setup:       func() error { return nil },
			Test:        func() error { return nil },
			Teardown:    func() error { return nil },
		},
		{
			Name:        "网络连通性",
			Description: "测试容器之间的网络连接",
			Setup:       func() error { return nil },
			Test:        func() error { return nil },
			Teardown:    func() error { return nil },
		},
		{
			Name:        "数据持久化",
			Description: "测试卷的数据持久化能力",
			Setup:       func() error { return nil },
			Test:        func() error { return nil },
			Teardown:    func() error { return nil },
		},
	}
}

// ====================================
// 性能测试数据
// ====================================

// PerformanceTestConfig 性能测试配置
type PerformanceTestConfig struct {
	ConcurrentRequests int
	TotalRequests      int
	Timeout            time.Duration
	RampUpTime         time.Duration
}

// CreatePerformanceTestConfig 创建性能测试配置
func (f *TestDataFactory) CreatePerformanceTestConfig(preset string) PerformanceTestConfig {
	configs := map[string]PerformanceTestConfig{
		"light": {
			ConcurrentRequests: 10,
			TotalRequests:      100,
			Timeout:            time.Second * 30,
			RampUpTime:         time.Second * 5,
		},
		"medium": {
			ConcurrentRequests: 50,
			TotalRequests:      500,
			Timeout:            time.Minute * 2,
			RampUpTime:         time.Second * 10,
		},
		"heavy": {
			ConcurrentRequests: 100,
			TotalRequests:      1000,
			Timeout:            time.Minute * 5,
			RampUpTime:         time.Second * 30,
		},
	}

	if config, ok := configs[preset]; ok {
		return config
	}

	return configs["light"]
}

// ====================================
// 测试数据集合
// ====================================

// TestDataset 测试数据集
type TestDataset struct {
	Name        string
	Description string
	Data        map[string]interface{}
}

// CreateTestDatasets 创建测试数据集
func (f *TestDataFactory) CreateTestDatasets() []TestDataset {
	return []TestDataset{
		{
			Name:        "容器镜像列表",
			Description: "常用的测试容器镜像",
			Data: map[string]interface{}{
				"images": []string{
					"nginx:alpine",
					"redis:alpine",
					"postgres:alpine",
					"busybox:latest",
				},
			},
		},
		{
			Name:        "测试端口映射",
			Description: "常用的端口映射配置",
			Data: map[string]interface{}{
				"mappings": map[string]string{
					"80/tcp":   "8080",
					"443/tcp":  "8443",
					"3306/tcp": "3306",
					"5432/tcp": "5432",
					"6379/tcp": "6379",
				},
			},
		},
		{
			Name:        "环境变量模板",
			Description: "常用的环境变量配置",
			Data: map[string]interface{}{
				"common": map[string]string{
					"APP_ENV":   "test",
					"DEBUG":     "true",
					"LOG_LEVEL": "debug",
					"TZ":        "Asia/Shanghai",
					"LANG":      "en_US.UTF-8",
				},
			},
		},
	}
}
