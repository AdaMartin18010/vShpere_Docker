package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/fatih/color"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/suite"
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/resource"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

// KubernetesAPITestSuite Kubernetes API测试套件
type KubernetesAPITestSuite struct {
	suite.Suite
	clientset      *kubernetes.Clientset
	ctx            context.Context
	namespace      string
	podName        string
	deploymentName string
	serviceName    string
	configMapName  string
}

// SetupSuite 初始化测试套件
func (s *KubernetesAPITestSuite) SetupSuite() {
	s.ctx = context.Background()
	s.namespace = "default"

	// 获取kubeconfig路径
	kubeconfig := os.Getenv("KUBECONFIG")
	if kubeconfig == "" {
		if home := homedir.HomeDir(); home != "" {
			kubeconfig = filepath.Join(home, ".kube", "config")
		}
	}

	// 构建配置
	config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
	s.Require().NoError(err, "Failed to build kubeconfig")

	// 创建clientset
	clientset, err := kubernetes.NewForConfig(config)
	s.Require().NoError(err, "Failed to create Kubernetes clientset")
	s.clientset = clientset

	color.Green("\n=== Kubernetes API 测试套件初始化 ===\n")
}

// TearDownSuite 清理测试套件
func (s *KubernetesAPITestSuite) TearDownSuite() {
	color.Green("\n=== Kubernetes API 测试套件清理完成 ===\n")
}

// Test01_GetAPIVersions 测试1: 获取API版本
func (s *KubernetesAPITestSuite) Test01_GetAPIVersions() {
	color.Cyan("\n测试1: 获取Kubernetes API版本")

	version, err := s.clientset.Discovery().ServerVersion()
	s.Require().NoError(err)

	color.Green("✅ API版本获取成功:")
	fmt.Printf("  - Version: %s\n", version.GitVersion)
	fmt.Printf("  - Platform: %s\n", version.Platform)
	fmt.Printf("  - Go Version: %s\n", version.GoVersion)

	assert.NotEmpty(s.T(), version.GitVersion)
}

// Test02_GetNodes 测试2: 获取节点列表
func (s *KubernetesAPITestSuite) Test02_GetNodes() {
	color.Cyan("\n测试2: 获取节点列表")

	nodes, err := s.clientset.CoreV1().Nodes().List(s.ctx, metav1.ListOptions{})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 节点列表获取成功: 共 %d 个节点", len(nodes.Items)))

	for i, node := range nodes.Items {
		if i >= 3 {
			break
		}

		// 获取节点状态
		status := "Unknown"
		for _, condition := range node.Status.Conditions {
			if condition.Type == corev1.NodeReady {
				if condition.Status == corev1.ConditionTrue {
					status = "Ready"
				} else {
					status = "NotReady"
				}
			}
		}

		fmt.Printf("  - %s: %s (%s)\n", node.Name, status, node.Status.NodeInfo.KubeletVersion)
	}

	assert.Greater(s.T(), len(nodes.Items), 0)
}

// Test03_ListNamespaces 测试3: 列出所有命名空间
func (s *KubernetesAPITestSuite) Test03_ListNamespaces() {
	color.Cyan("\n测试3: 列出所有命名空间")

	namespaces, err := s.clientset.CoreV1().Namespaces().List(s.ctx, metav1.ListOptions{})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ 命名空间列表获取成功: 共 %d 个命名空间", len(namespaces.Items)))

	for i, ns := range namespaces.Items {
		if i >= 5 {
			break
		}
		fmt.Printf("  - %s (Phase: %s)\n", ns.Name, ns.Status.Phase)
	}

	if len(namespaces.Items) > 5 {
		fmt.Printf("  ... 还有 %d 个命名空间\n", len(namespaces.Items)-5)
	}
}

// Test04_CreatePod 测试4: 创建Pod
func (s *KubernetesAPITestSuite) Test04_CreatePod() {
	color.Cyan("\n测试4: 创建nginx Pod")

	s.podName = "test-nginx-go"

	pod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      s.podName,
			Namespace: s.namespace,
			Labels: map[string]string{
				"app":  "nginx",
				"test": "golang",
			},
		},
		Spec: corev1.PodSpec{
			Containers: []corev1.Container{
				{
					Name:  "nginx",
					Image: "nginx:alpine",
					Ports: []corev1.ContainerPort{
						{
							ContainerPort: 80,
						},
					},
					Resources: corev1.ResourceRequirements{
						Requests: corev1.ResourceList{
							corev1.ResourceCPU:    parseQuantity("100m"),
							corev1.ResourceMemory: parseQuantity("128Mi"),
						},
						Limits: corev1.ResourceList{
							corev1.ResourceCPU:    parseQuantity("200m"),
							corev1.ResourceMemory: parseQuantity("256Mi"),
						},
					},
				},
			},
			RestartPolicy: corev1.RestartPolicyAlways,
		},
	}

	createdPod, err := s.clientset.CoreV1().Pods(s.namespace).Create(s.ctx, pod, metav1.CreateOptions{})
	s.Require().NoError(err)

	color.Green("✅ Pod创建成功:")
	fmt.Printf("  - Name: %s\n", createdPod.Name)
	fmt.Printf("  - Namespace: %s\n", createdPod.Namespace)
	fmt.Printf("  - UID: %s\n", createdPod.UID)

	// 等待Pod启动
	color.Yellow("  - 等待Pod启动...")
	time.Sleep(5 * time.Second)
}

// Test05_GetPod 测试5: 获取Pod详情
func (s *KubernetesAPITestSuite) Test05_GetPod() {
	color.Cyan("\n测试5: 获取Pod详情")

	pod, err := s.clientset.CoreV1().Pods(s.namespace).Get(s.ctx, s.podName, metav1.GetOptions{})
	s.Require().NoError(err)

	color.Green("✅ Pod详情获取成功:")
	fmt.Printf("  - Name: %s\n", pod.Name)
	fmt.Printf("  - Phase: %s\n", pod.Status.Phase)
	fmt.Printf("  - Node: %s\n", pod.Spec.NodeName)
	fmt.Printf("  - IP: %s\n", pod.Status.PodIP)
	fmt.Printf("  - Start Time: %v\n", pod.Status.StartTime)

	assert.Equal(s.T(), s.podName, pod.Name)
}

// Test06_ListPods 测试6: 列出Pods
func (s *KubernetesAPITestSuite) Test06_ListPods() {
	color.Cyan("\n测试6: 列出所有Pods")

	pods, err := s.clientset.CoreV1().Pods(s.namespace).List(s.ctx, metav1.ListOptions{})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ Pod列表获取成功: 共 %d 个Pods", len(pods.Items)))

	for i, pod := range pods.Items {
		if i >= 5 {
			break
		}
		fmt.Printf("  - %s: %s\n", pod.Name, pod.Status.Phase)
	}

	if len(pods.Items) > 5 {
		fmt.Printf("  ... 还有 %d 个Pods\n", len(pods.Items)-5)
	}
}

// Test07_GetPodLogs 测试7: 获取Pod日志
func (s *KubernetesAPITestSuite) Test07_GetPodLogs() {
	color.Cyan("\n测试7: 获取Pod日志")

	// 等待Pod完全运行
	time.Sleep(5 * time.Second)

	tailLines := int64(10)
	req := s.clientset.CoreV1().Pods(s.namespace).GetLogs(s.podName, &corev1.PodLogOptions{
		TailLines: &tailLines,
	})

	logs, err := req.DoRaw(s.ctx)
	if err != nil {
		color.Yellow("⚠️  Pod日志暂时不可用 (Pod可能还在初始化)")
	} else {
		color.Green("✅ Pod日志获取成功:")
		fmt.Printf("  - 日志长度: %d 字节\n", len(logs))
	}
}

// Test08_CreateDeployment 测试8: 创建Deployment
func (s *KubernetesAPITestSuite) Test08_CreateDeployment() {
	color.Cyan("\n测试8: 创建nginx Deployment")

	s.deploymentName = "nginx-deployment-go"
	replicas := int32(3)

	deployment := &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name:      s.deploymentName,
			Namespace: s.namespace,
		},
		Spec: appsv1.DeploymentSpec{
			Replicas: &replicas,
			Selector: &metav1.LabelSelector{
				MatchLabels: map[string]string{
					"app": "nginx-go",
				},
			},
			Template: corev1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: map[string]string{
						"app": "nginx-go",
					},
				},
				Spec: corev1.PodSpec{
					Containers: []corev1.Container{
						{
							Name:  "nginx",
							Image: "nginx:alpine",
							Ports: []corev1.ContainerPort{
								{
									ContainerPort: 80,
								},
							},
						},
					},
				},
			},
		},
	}

	createdDeployment, err := s.clientset.AppsV1().Deployments(s.namespace).Create(
		s.ctx, deployment, metav1.CreateOptions{})
	s.Require().NoError(err)

	color.Green("✅ Deployment创建成功:")
	fmt.Printf("  - Name: %s\n", createdDeployment.Name)
	fmt.Printf("  - Replicas: %d\n", *createdDeployment.Spec.Replicas)
	fmt.Printf("  - UID: %s\n", createdDeployment.UID)

	// 等待Deployment创建
	time.Sleep(3 * time.Second)
}

// Test09_GetDeployment 测试9: 获取Deployment详情
func (s *KubernetesAPITestSuite) Test09_GetDeployment() {
	color.Cyan("\n测试9: 获取Deployment详情")

	deployment, err := s.clientset.AppsV1().Deployments(s.namespace).Get(
		s.ctx, s.deploymentName, metav1.GetOptions{})
	s.Require().NoError(err)

	color.Green("✅ Deployment详情获取成功:")
	fmt.Printf("  - Name: %s\n", deployment.Name)
	fmt.Printf("  - Desired Replicas: %d\n", *deployment.Spec.Replicas)
	fmt.Printf("  - Available Replicas: %d\n", deployment.Status.AvailableReplicas)
	fmt.Printf("  - Ready Replicas: %d\n", deployment.Status.ReadyReplicas)

	assert.Equal(s.T(), s.deploymentName, deployment.Name)
}

// Test10_ScaleDeployment 测试10: 扩缩容Deployment
func (s *KubernetesAPITestSuite) Test10_ScaleDeployment() {
	color.Cyan("\n测试10: 扩容Deployment至5副本")

	deployment, err := s.clientset.AppsV1().Deployments(s.namespace).Get(
		s.ctx, s.deploymentName, metav1.GetOptions{})
	s.Require().NoError(err)

	replicas := int32(5)
	deployment.Spec.Replicas = &replicas

	updatedDeployment, err := s.clientset.AppsV1().Deployments(s.namespace).Update(
		s.ctx, deployment, metav1.UpdateOptions{})
	s.Require().NoError(err)

	color.Green("✅ Deployment扩容成功:")
	fmt.Printf("  - New Replicas: %d\n", *updatedDeployment.Spec.Replicas)

	assert.Equal(s.T(), int32(5), *updatedDeployment.Spec.Replicas)
}

// Test11_CreateService 测试11: 创建Service
func (s *KubernetesAPITestSuite) Test11_CreateService() {
	color.Cyan("\n测试11: 创建nginx Service")

	s.serviceName = "nginx-service-go"

	service := &corev1.Service{
		ObjectMeta: metav1.ObjectMeta{
			Name:      s.serviceName,
			Namespace: s.namespace,
		},
		Spec: corev1.ServiceSpec{
			Selector: map[string]string{
				"app": "nginx-go",
			},
			Type: corev1.ServiceTypeClusterIP,
			Ports: []corev1.ServicePort{
				{
					Protocol:   corev1.ProtocolTCP,
					Port:       80,
					TargetPort: intstr.FromInt(80),
				},
			},
		},
	}

	createdService, err := s.clientset.CoreV1().Services(s.namespace).Create(
		s.ctx, service, metav1.CreateOptions{})
	s.Require().NoError(err)

	color.Green("✅ Service创建成功:")
	fmt.Printf("  - Name: %s\n", createdService.Name)
	fmt.Printf("  - Type: %s\n", createdService.Spec.Type)
	fmt.Printf("  - Cluster IP: %s\n", createdService.Spec.ClusterIP)

	assert.NotEmpty(s.T(), createdService.Spec.ClusterIP)
}

// Test12_GetService 测试12: 获取Service详情
func (s *KubernetesAPITestSuite) Test12_GetService() {
	color.Cyan("\n测试12: 获取Service详情")

	service, err := s.clientset.CoreV1().Services(s.namespace).Get(
		s.ctx, s.serviceName, metav1.GetOptions{})
	s.Require().NoError(err)

	color.Green("✅ Service详情获取成功:")
	fmt.Printf("  - Name: %s\n", service.Name)
	fmt.Printf("  - Type: %s\n", service.Spec.Type)
	fmt.Printf("  - Cluster IP: %s\n", service.Spec.ClusterIP)
	fmt.Printf("  - Ports: %v\n", service.Spec.Ports)

	assert.Equal(s.T(), s.serviceName, service.Name)
}

// Test13_CreateConfigMap 测试13: 创建ConfigMap
func (s *KubernetesAPITestSuite) Test13_CreateConfigMap() {
	color.Cyan("\n测试13: 创建ConfigMap")

	s.configMapName = "test-config-go"

	configMap := &corev1.ConfigMap{
		ObjectMeta: metav1.ObjectMeta{
			Name:      s.configMapName,
			Namespace: s.namespace,
		},
		Data: map[string]string{
			"config.json": `{"env":"test","debug":true}`,
			"app.conf":    "server {\n  listen 80;\n}",
		},
	}

	createdConfigMap, err := s.clientset.CoreV1().ConfigMaps(s.namespace).Create(
		s.ctx, configMap, metav1.CreateOptions{})
	s.Require().NoError(err)

	color.Green("✅ ConfigMap创建成功:")
	fmt.Printf("  - Name: %s\n", createdConfigMap.Name)
	fmt.Printf("  - Data Keys: %d\n", len(createdConfigMap.Data))

	assert.Equal(s.T(), 2, len(createdConfigMap.Data))
}

// Test14_DeletePod 测试14: 删除Pod
func (s *KubernetesAPITestSuite) Test14_DeletePod() {
	color.Cyan("\n测试14: 删除Pod")

	err := s.clientset.CoreV1().Pods(s.namespace).Delete(
		s.ctx, s.podName, metav1.DeleteOptions{})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ Pod删除成功: %s", s.podName))
}

// Test15_DeleteService 测试15: 删除Service
func (s *KubernetesAPITestSuite) Test15_DeleteService() {
	color.Cyan("\n测试15: 删除Service")

	err := s.clientset.CoreV1().Services(s.namespace).Delete(
		s.ctx, s.serviceName, metav1.DeleteOptions{})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ Service删除成功: %s", s.serviceName))
}

// Test16_DeleteDeployment 测试16: 删除Deployment
func (s *KubernetesAPITestSuite) Test16_DeleteDeployment() {
	color.Cyan("\n测试16: 删除Deployment")

	deletePolicy := metav1.DeletePropagationForeground
	err := s.clientset.AppsV1().Deployments(s.namespace).Delete(
		s.ctx, s.deploymentName, metav1.DeleteOptions{
			PropagationPolicy: &deletePolicy,
		})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ Deployment删除成功: %s", s.deploymentName))
}

// Test17_DeleteConfigMap 测试17: 删除ConfigMap
func (s *KubernetesAPITestSuite) Test17_DeleteConfigMap() {
	color.Cyan("\n测试17: 删除ConfigMap")

	err := s.clientset.CoreV1().ConfigMaps(s.namespace).Delete(
		s.ctx, s.configMapName, metav1.DeleteOptions{})
	s.Require().NoError(err)

	color.Green(fmt.Sprintf("✅ ConfigMap删除成功: %s", s.configMapName))
}

// Helper functions

// parseQuantity 解析资源量
func parseQuantity(quantity string) resource.Quantity {
	q, _ := resource.ParseQuantity(quantity)
	return q
}

// intstr 辅助结构
type intstr struct{}

func (intstr) FromInt(val int) intOrString {
	return intOrString{IntVal: int32(val)}
}

type intOrString struct {
	IntVal int32
}

// TestKubernetesAPI 运行Kubernetes API测试套件
func TestKubernetesAPI(t *testing.T) {
	suite.Run(t, new(KubernetesAPITestSuite))
}

// Main函数 - 用于直接运行
func main() {
	os.Exit(0)
}
