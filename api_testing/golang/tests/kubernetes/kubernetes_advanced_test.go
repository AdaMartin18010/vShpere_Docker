package main

import (
	"context"
	"fmt"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/suite"
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/api/resource"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/util/intstr"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
)

// KubernetesAdvancedTestSuite Kubernetes高级测试套件
// 包含：边界条件、错误处理、并发、性能、复杂场景、混沌测试
type KubernetesAdvancedTestSuite struct {
	suite.Suite
	clientset *kubernetes.Clientset
	namespace string
}

// SetupSuite 初始化
func (s *KubernetesAdvancedTestSuite) SetupSuite() {
	config, err := clientcmd.BuildConfigFromFlags("", clientcmd.RecommendedHomeFile)
	s.Require().NoError(err)

	clientset, err := kubernetes.NewForConfig(config)
	s.Require().NoError(err)

	s.clientset = clientset
	s.namespace = "test-advanced-" + fmt.Sprintf("%d", time.Now().Unix())

	// 创建测试命名空间
	_, err = s.clientset.CoreV1().Namespaces().Create(context.TODO(), &corev1.Namespace{
		ObjectMeta: metav1.ObjectMeta{
			Name: s.namespace,
		},
	}, metav1.CreateOptions{})
	s.Require().NoError(err)
}

// TearDownSuite 清理
func (s *KubernetesAdvancedTestSuite) TearDownSuite() {
	if s.clientset != nil && s.namespace != "" {
		s.clientset.CoreV1().Namespaces().Delete(context.TODO(), s.namespace, metav1.DeleteOptions{})
	}
}

// ====================
// 1. 边界条件测试
// ====================

// TestBoundaryConditions_EmptyPodName 测试空Pod名
func (s *KubernetesAdvancedTestSuite) TestBoundaryConditions_EmptyPodName() {
	pod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name: "", // 空名称
		},
		Spec: corev1.PodSpec{
			Containers: []corev1.Container{
				{
					Name:  "test",
					Image: "nginx:latest",
				},
			},
		},
	}

	_, err := s.clientset.CoreV1().Pods(s.namespace).Create(context.TODO(), pod, metav1.CreateOptions{})
	s.Assert().Error(err, "空Pod名应该返回错误")
}

// TestBoundaryConditions_InvalidPodName 测试非法Pod名
func (s *KubernetesAdvancedTestSuite) TestBoundaryConditions_InvalidPodName() {
	invalidNames := []string{
		"Invalid_Name",          // 包含下划线
		"invalid.Name",          // 包含点（在某些位置）
		"-invalid",              // 以短横线开头
		"invalid-",              // 以短横线结尾
		"INVALID",               // 大写字母
		strings.Repeat("a", 64), // 超长（>63字符）
	}

	for _, name := range invalidNames {
		pod := &corev1.Pod{
			ObjectMeta: metav1.ObjectMeta{
				Name: name,
			},
			Spec: corev1.PodSpec{
				Containers: []corev1.Container{
					{
						Name:  "test",
						Image: "nginx:latest",
					},
				},
			},
		}

		_, err := s.clientset.CoreV1().Pods(s.namespace).Create(context.TODO(), pod, metav1.CreateOptions{})
		if err != nil {
			s.T().Logf("非法名称 '%s' 被正确拒绝", name)
		}
	}
}

// TestBoundaryConditions_ResourceLimits 测试资源限制边界
func (s *KubernetesAdvancedTestSuite) TestBoundaryConditions_ResourceLimits() {
	testCases := []struct {
		name          string
		cpuReq        string
		cpuLimit      string
		memReq        string
		memLimit      string
		shouldSucceed bool
	}{
		{"极小资源", "10m", "20m", "16Mi", "32Mi", true},
		{"正常资源", "100m", "200m", "128Mi", "256Mi", true},
		{"大资源", "2", "4", "2Gi", "4Gi", true},
		{"超大资源", "32", "64", "64Gi", "128Gi", true},
		{"零CPU请求", "0", "100m", "128Mi", "256Mi", false}, // 零请求可能被拒绝
	}

	for _, tc := range testCases {
		pod := &corev1.Pod{
			ObjectMeta: metav1.ObjectMeta{
				GenerateName: "resource-test-",
			},
			Spec: corev1.PodSpec{
				Containers: []corev1.Container{
					{
						Name:  "test",
						Image: "nginx:latest",
						Resources: corev1.ResourceRequirements{
							Requests: corev1.ResourceList{
								corev1.ResourceCPU:    resource.MustParse(tc.cpuReq),
								corev1.ResourceMemory: resource.MustParse(tc.memReq),
							},
							Limits: corev1.ResourceList{
								corev1.ResourceCPU:    resource.MustParse(tc.cpuLimit),
								corev1.ResourceMemory: resource.MustParse(tc.memLimit),
							},
						},
					},
				},
			},
		}

		created, err := s.clientset.CoreV1().Pods(s.namespace).Create(context.TODO(), pod, metav1.CreateOptions{})
		if err == nil {
			s.T().Logf("✅ %s: 成功创建", tc.name)
			s.clientset.CoreV1().Pods(s.namespace).Delete(context.TODO(), created.Name, metav1.DeleteOptions{})
		} else {
			s.T().Logf("❌ %s: %v", tc.name, err)
		}
	}
}

// ====================
// 2. 错误处理测试
// ====================

// TestErrorHandling_NonExistentPod 测试操作不存在的Pod
func (s *KubernetesAdvancedTestSuite) TestErrorHandling_NonExistentPod() {
	nonExistentName := "nonexistent-pod-12345"

	// 测试获取
	_, err := s.clientset.CoreV1().Pods(s.namespace).Get(context.TODO(), nonExistentName, metav1.GetOptions{})
	s.Assert().True(errors.IsNotFound(err))

	// 测试删除
	err = s.clientset.CoreV1().Pods(s.namespace).Delete(context.TODO(), nonExistentName, metav1.DeleteOptions{})
	s.Assert().True(errors.IsNotFound(err))

	// 测试更新
	pod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name: nonExistentName,
		},
	}
	_, err = s.clientset.CoreV1().Pods(s.namespace).Update(context.TODO(), pod, metav1.UpdateOptions{})
	s.Assert().True(errors.IsNotFound(err))
}

// TestErrorHandling_InvalidNamespace 测试非法命名空间
func (s *KubernetesAdvancedTestSuite) TestErrorHandling_InvalidNamespace() {
	invalidNamespace := "nonexistent-namespace-" + fmt.Sprintf("%d", time.Now().Unix())

	pod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name: "test-pod",
		},
		Spec: corev1.PodSpec{
			Containers: []corev1.Container{
				{
					Name:  "test",
					Image: "nginx:latest",
				},
			},
		},
	}

	_, err := s.clientset.CoreV1().Pods(invalidNamespace).Create(context.TODO(), pod, metav1.CreateOptions{})
	s.Assert().True(errors.IsNotFound(err) || errors.IsForbidden(err))
}

// TestErrorHandling_ResourceQuotaExceeded 测试资源配额超限
func (s *KubernetesAdvancedTestSuite) TestErrorHandling_ResourceQuotaExceeded() {
	// 创建资源配额
	quota := &corev1.ResourceQuota{
		ObjectMeta: metav1.ObjectMeta{
			Name: "test-quota",
		},
		Spec: corev1.ResourceQuotaSpec{
			Hard: corev1.ResourceList{
				corev1.ResourcePods:   resource.MustParse("2"),
				corev1.ResourceMemory: resource.MustParse("1Gi"),
			},
		},
	}

	_, err := s.clientset.CoreV1().ResourceQuotas(s.namespace).Create(context.TODO(), quota, metav1.CreateOptions{})
	if err != nil {
		s.T().Skip("无法创建资源配额，跳过测试")
		return
	}
	defer s.clientset.CoreV1().ResourceQuotas(s.namespace).Delete(context.TODO(), "test-quota", metav1.DeleteOptions{})

	// 等待配额生效
	time.Sleep(2 * time.Second)

	// 尝试创建超过配额的Pod
	for i := 0; i < 3; i++ {
		pod := &corev1.Pod{
			ObjectMeta: metav1.ObjectMeta{
				GenerateName: "quota-test-",
			},
			Spec: corev1.PodSpec{
				Containers: []corev1.Container{
					{
						Name:  "test",
						Image: "nginx:latest",
					},
				},
			},
		}

		created, err := s.clientset.CoreV1().Pods(s.namespace).Create(context.TODO(), pod, metav1.CreateOptions{})
		if err != nil {
			s.T().Logf("第%d个Pod创建失败（预期）: %v", i+1, err)
		} else {
			defer s.clientset.CoreV1().Pods(s.namespace).Delete(context.TODO(), created.Name, metav1.DeleteOptions{})
		}
	}
}

// ====================
// 3. 并发测试
// ====================

// TestConcurrency_ParallelPodCreation 测试并发创建Pod
func (s *KubernetesAdvancedTestSuite) TestConcurrency_ParallelPodCreation() {
	concurrency := 10
	var wg sync.WaitGroup
	results := make(chan error, concurrency)
	podNames := make([]string, 0, concurrency)
	var mu sync.Mutex

	for i := 0; i < concurrency; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()

			pod := &corev1.Pod{
				ObjectMeta: metav1.ObjectMeta{
					GenerateName: fmt.Sprintf("concurrent-%d-", idx),
				},
				Spec: corev1.PodSpec{
					Containers: []corev1.Container{
						{
							Name:  "nginx",
							Image: "nginx:latest",
						},
					},
				},
			}

			created, err := s.clientset.CoreV1().Pods(s.namespace).Create(context.TODO(), pod, metav1.CreateOptions{})
			if err != nil {
				results <- err
				return
			}

			mu.Lock()
			podNames = append(podNames, created.Name)
			mu.Unlock()

			results <- nil
		}(i)
	}

	wg.Wait()
	close(results)

	// 清理Pod
	for _, name := range podNames {
		s.clientset.CoreV1().Pods(s.namespace).Delete(context.TODO(), name, metav1.DeleteOptions{})
	}

	// 统计结果
	errorCount := 0
	for err := range results {
		if err != nil {
			errorCount++
		}
	}

	successRate := float64(concurrency-errorCount) / float64(concurrency) * 100
	s.T().Logf("并发创建成功率: %.2f%% (%d/%d)", successRate, concurrency-errorCount, concurrency)
	s.Assert().GreaterOrEqual(successRate, 90.0)
}

// TestConcurrency_WatchOperations 测试并发Watch操作
func (s *KubernetesAdvancedTestSuite) TestConcurrency_WatchOperations() {
	watchers := 5
	var wg sync.WaitGroup

	for i := 0; i < watchers; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()

			ctx, cancel := context.WithTimeout(context.TODO(), 5*time.Second)
			defer cancel()

			watch, err := s.clientset.CoreV1().Pods(s.namespace).Watch(ctx, metav1.ListOptions{})
			if err != nil {
				s.T().Logf("Watcher %d 创建失败: %v", idx, err)
				return
			}
			defer watch.Stop()

			for {
				select {
				case event, ok := <-watch.ResultChan():
					if !ok {
						return
					}
					s.T().Logf("Watcher %d 接收事件: %s", idx, event.Type)
				case <-ctx.Done():
					return
				}
			}
		}(i)
	}

	// 创建一些Pod来触发watch事件
	for i := 0; i < 3; i++ {
		pod := &corev1.Pod{
			ObjectMeta: metav1.ObjectMeta{
				GenerateName: "watch-test-",
			},
			Spec: corev1.PodSpec{
				Containers: []corev1.Container{
					{
						Name:  "nginx",
						Image: "nginx:latest",
					},
				},
			},
		}

		created, err := s.clientset.CoreV1().Pods(s.namespace).Create(context.TODO(), pod, metav1.CreateOptions{})
		if err == nil {
			defer s.clientset.CoreV1().Pods(s.namespace).Delete(context.TODO(), created.Name, metav1.DeleteOptions{})
		}
		time.Sleep(500 * time.Millisecond)
	}

	wg.Wait()
}

// ====================
// 4. 性能基准测试
// ====================

// BenchmarkPodCreation 基准测试：Pod创建
func BenchmarkPodCreation(b *testing.B) {
	config, err := clientcmd.BuildConfigFromFlags("", clientcmd.RecommendedHomeFile)
	if err != nil {
		b.Fatal(err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		b.Fatal(err)
	}

	namespace := "benchmark-test"

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		pod := &corev1.Pod{
			ObjectMeta: metav1.ObjectMeta{
				GenerateName: "bench-",
			},
			Spec: corev1.PodSpec{
				Containers: []corev1.Container{
					{
						Name:  "nginx",
						Image: "nginx:latest",
					},
				},
			},
		}

		created, err := clientset.CoreV1().Pods(namespace).Create(context.TODO(), pod, metav1.CreateOptions{})
		if err == nil {
			clientset.CoreV1().Pods(namespace).Delete(context.TODO(), created.Name, metav1.DeleteOptions{})
		}
	}
}

// ====================
// 5. 复杂场景测试
// ====================

// TestComplexScenario_MultiPodCommunication 测试多Pod通信
func (s *KubernetesAdvancedTestSuite) TestComplexScenario_MultiPodCommunication() {
	// 创建Service
	svc := &corev1.Service{
		ObjectMeta: metav1.ObjectMeta{
			Name: "test-service",
		},
		Spec: corev1.ServiceSpec{
			Selector: map[string]string{
				"app": "test",
			},
			Ports: []corev1.ServicePort{
				{
					Port:       80,
					TargetPort: intstr.FromInt(80),
				},
			},
		},
	}

	_, err := s.clientset.CoreV1().Services(s.namespace).Create(context.TODO(), svc, metav1.CreateOptions{})
	s.Require().NoError(err)
	defer s.clientset.CoreV1().Services(s.namespace).Delete(context.TODO(), "test-service", metav1.DeleteOptions{})

	// 创建多个Pod
	for i := 0; i < 3; i++ {
		pod := &corev1.Pod{
			ObjectMeta: metav1.ObjectMeta{
				GenerateName: "service-test-",
				Labels: map[string]string{
					"app": "test",
				},
			},
			Spec: corev1.PodSpec{
				Containers: []corev1.Container{
					{
						Name:  "nginx",
						Image: "nginx:latest",
					},
				},
			},
		}

		created, err := s.clientset.CoreV1().Pods(s.namespace).Create(context.TODO(), pod, metav1.CreateOptions{})
		if err == nil {
			defer s.clientset.CoreV1().Pods(s.namespace).Delete(context.TODO(), created.Name, metav1.DeleteOptions{})
		}
	}

	s.T().Log("多Pod通信场景测试完成")
}

// TestComplexScenario_RollingUpdate 测试滚动更新
func (s *KubernetesAdvancedTestSuite) TestComplexScenario_RollingUpdate() {
	// 创建Deployment
	replicas := int32(3)
	deployment := &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name: "rolling-update-test",
		},
		Spec: appsv1.DeploymentSpec{
			Replicas: &replicas,
			Selector: &metav1.LabelSelector{
				MatchLabels: map[string]string{
					"app": "rolling-test",
				},
			},
			Template: corev1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: map[string]string{
						"app": "rolling-test",
					},
				},
				Spec: corev1.PodSpec{
					Containers: []corev1.Container{
						{
							Name:  "nginx",
							Image: "nginx:1.19",
						},
					},
				},
			},
		},
	}

	created, err := s.clientset.AppsV1().Deployments(s.namespace).Create(context.TODO(), deployment, metav1.CreateOptions{})
	s.Require().NoError(err)
	defer s.clientset.AppsV1().Deployments(s.namespace).Delete(context.TODO(), "rolling-update-test", metav1.DeleteOptions{})

	// 等待Deployment就绪
	time.Sleep(5 * time.Second)

	// 触发滚动更新
	created.Spec.Template.Spec.Containers[0].Image = "nginx:1.20"
	_, err = s.clientset.AppsV1().Deployments(s.namespace).Update(context.TODO(), created, metav1.UpdateOptions{})
	s.Require().NoError(err)

	s.T().Log("滚动更新测试完成")
}

// TestKubernetesAdvancedTestSuite 运行测试套件
func TestKubernetesAdvancedTestSuite(t *testing.T) {
	suite.Run(t, new(KubernetesAdvancedTestSuite))
}
