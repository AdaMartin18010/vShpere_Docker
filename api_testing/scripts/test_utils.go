package main

import (
	"context"
	"fmt"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/client"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
)

// TestUtils 测试工具类
type TestUtils struct{}

// NewTestUtils 创建测试工具实例
func NewTestUtils() *TestUtils {
	return &TestUtils{}
}

// ====================================
// Docker工具函数
// ====================================

// WaitForContainerRunning 等待容器进入运行状态
func (u *TestUtils) WaitForContainerRunning(ctx context.Context, cli *client.Client, containerID string, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)

	for time.Now().Before(deadline) {
		inspect, err := cli.ContainerInspect(ctx, containerID)
		if err != nil {
			return err
		}

		if inspect.State.Running {
			return nil
		}

		time.Sleep(time.Second)
	}

	return fmt.Errorf("container did not start within %v", timeout)
}

// WaitForContainerStopped 等待容器停止
func (u *TestUtils) WaitForContainerStopped(ctx context.Context, cli *client.Client, containerID string, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)

	for time.Now().Before(deadline) {
		inspect, err := cli.ContainerInspect(ctx, containerID)
		if err != nil {
			return err
		}

		if !inspect.State.Running {
			return nil
		}

		time.Sleep(time.Second)
	}

	return fmt.Errorf("container did not stop within %v", timeout)
}

// CleanupDockerContainers 清理Docker容器
func (u *TestUtils) CleanupDockerContainers(ctx context.Context, cli *client.Client, labelFilter string) error {
	containers, err := cli.ContainerList(ctx, types.ContainerListOptions{All: true})
	if err != nil {
		return err
	}

	for _, container := range containers {
		if label, ok := container.Labels[labelFilter]; ok && label == "api-test" {
			cli.ContainerRemove(ctx, container.ID, types.ContainerRemoveOptions{Force: true})
		}
	}

	return nil
}

// CleanupDockerNetworks 清理Docker网络
func (u *TestUtils) CleanupDockerNetworks(ctx context.Context, cli *client.Client, labelFilter string) error {
	networks, err := cli.NetworkList(ctx, types.NetworkListOptions{})
	if err != nil {
		return err
	}

	for _, network := range networks {
		if label, ok := network.Labels[labelFilter]; ok && label == "api-test" {
			cli.NetworkRemove(ctx, network.ID)
		}
	}

	return nil
}

// CleanupDockerVolumes 清理Docker卷
func (u *TestUtils) CleanupDockerVolumes(ctx context.Context, cli *client.Client, labelFilter string) error {
	volumes, err := cli.VolumeList(ctx, types.VolumeListOptions{})
	if err != nil {
		return err
	}

	for _, volume := range volumes.Volumes {
		if label, ok := volume.Labels[labelFilter]; ok && label == "api-test" {
			cli.VolumeRemove(ctx, volume.Name, false)
		}
	}

	return nil
}

// ====================================
// Kubernetes工具函数
// ====================================

// WaitForPodRunning 等待Pod进入运行状态
func (u *TestUtils) WaitForPodRunning(ctx context.Context, clientset *kubernetes.Clientset, namespace, podName string, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)

	for time.Now().Before(deadline) {
		pod, err := clientset.CoreV1().Pods(namespace).Get(ctx, podName, metav1.GetOptions{})
		if err != nil {
			return err
		}

		if pod.Status.Phase == corev1.PodRunning {
			// 检查所有容器是否就绪
			allReady := true
			for _, status := range pod.Status.ContainerStatuses {
				if !status.Ready {
					allReady = false
					break
				}
			}
			if allReady {
				return nil
			}
		}

		time.Sleep(time.Second * 2)
	}

	return fmt.Errorf("pod did not become ready within %v", timeout)
}

// WaitForPodDeleted 等待Pod被删除
func (u *TestUtils) WaitForPodDeleted(ctx context.Context, clientset *kubernetes.Clientset, namespace, podName string, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)

	for time.Now().Before(deadline) {
		_, err := clientset.CoreV1().Pods(namespace).Get(ctx, podName, metav1.GetOptions{})
		if err != nil {
			// Pod不存在，删除成功
			return nil
		}

		time.Sleep(time.Second)
	}

	return fmt.Errorf("pod was not deleted within %v", timeout)
}

// CleanupK8sResources 清理Kubernetes资源
func (u *TestUtils) CleanupK8sResources(ctx context.Context, clientset *kubernetes.Clientset, namespace string) error {
	// 删除所有Pods
	pods, err := clientset.CoreV1().Pods(namespace).List(ctx, metav1.ListOptions{
		LabelSelector: "test=api-test",
	})
	if err == nil {
		for _, pod := range pods.Items {
			clientset.CoreV1().Pods(namespace).Delete(ctx, pod.Name, metav1.DeleteOptions{})
		}
	}

	// 删除所有Services
	services, err := clientset.CoreV1().Services(namespace).List(ctx, metav1.ListOptions{
		LabelSelector: "test=api-test",
	})
	if err == nil {
		for _, svc := range services.Items {
			clientset.CoreV1().Services(namespace).Delete(ctx, svc.Name, metav1.DeleteOptions{})
		}
	}

	// 删除所有ConfigMaps
	configmaps, err := clientset.CoreV1().ConfigMaps(namespace).List(ctx, metav1.ListOptions{
		LabelSelector: "test=api-test",
	})
	if err == nil {
		for _, cm := range configmaps.Items {
			clientset.CoreV1().ConfigMaps(namespace).Delete(ctx, cm.Name, metav1.DeleteOptions{})
		}
	}

	return nil
}

// ====================================
// 通用工具函数
// ====================================

// Retry 重试函数
func (u *TestUtils) Retry(attempts int, sleep time.Duration, fn func() error) error {
	var err error
	for i := 0; i < attempts; i++ {
		err = fn()
		if err == nil {
			return nil
		}

		if i < attempts-1 {
			time.Sleep(sleep)
		}
	}
	return fmt.Errorf("after %d attempts, last error: %w", attempts, err)
}

// MeasureTime 测量函数执行时间
func (u *TestUtils) MeasureTime(fn func() error) (time.Duration, error) {
	start := time.Now()
	err := fn()
	duration := time.Since(start)
	return duration, err
}

// CheckTimeout 检查是否超时
func (u *TestUtils) CheckTimeout(ctx context.Context) bool {
	select {
	case <-ctx.Done():
		return true
	default:
		return false
	}
}

// ====================================
// 断言工具
// ====================================

// AssertContainerExists 断言容器存在
func (u *TestUtils) AssertContainerExists(ctx context.Context, cli *client.Client, containerID string) error {
	_, err := cli.ContainerInspect(ctx, containerID)
	if err != nil {
		return fmt.Errorf("container does not exist: %w", err)
	}
	return nil
}

// AssertContainerRunning 断言容器正在运行
func (u *TestUtils) AssertContainerRunning(ctx context.Context, cli *client.Client, containerID string) error {
	inspect, err := cli.ContainerInspect(ctx, containerID)
	if err != nil {
		return err
	}

	if !inspect.State.Running {
		return fmt.Errorf("container is not running, status: %s", inspect.State.Status)
	}

	return nil
}

// AssertPodExists 断言Pod存在
func (u *TestUtils) AssertPodExists(ctx context.Context, clientset *kubernetes.Clientset, namespace, podName string) error {
	_, err := clientset.CoreV1().Pods(namespace).Get(ctx, podName, metav1.GetOptions{})
	if err != nil {
		return fmt.Errorf("pod does not exist: %w", err)
	}
	return nil
}

// AssertPodRunning 断言Pod正在运行
func (u *TestUtils) AssertPodRunning(ctx context.Context, clientset *kubernetes.Clientset, namespace, podName string) error {
	pod, err := clientset.CoreV1().Pods(namespace).Get(ctx, podName, metav1.GetOptions{})
	if err != nil {
		return err
	}

	if pod.Status.Phase != corev1.PodRunning {
		return fmt.Errorf("pod is not running, phase: %s", pod.Status.Phase)
	}

	return nil
}

// ====================================
// 性能测试工具
// ====================================

// BenchmarkResult 性能测试结果
type BenchmarkResult struct {
	Operations      int
	TotalDuration   time.Duration
	AverageDuration time.Duration
	MinDuration     time.Duration
	MaxDuration     time.Duration
	ErrorCount      int
}

// Benchmark 执行性能测试
func (u *TestUtils) Benchmark(operations int, fn func() error) BenchmarkResult {
	result := BenchmarkResult{
		Operations:  operations,
		MinDuration: time.Hour, // 初始化为很大的值
	}

	durations := make([]time.Duration, 0, operations)

	for i := 0; i < operations; i++ {
		start := time.Now()
		err := fn()
		duration := time.Since(start)

		durations = append(durations, duration)
		result.TotalDuration += duration

		if duration < result.MinDuration {
			result.MinDuration = duration
		}
		if duration > result.MaxDuration {
			result.MaxDuration = duration
		}

		if err != nil {
			result.ErrorCount++
		}
	}

	if operations > 0 {
		result.AverageDuration = result.TotalDuration / time.Duration(operations)
	}

	return result
}

// FormatBenchmarkResult 格式化性能测试结果
func (u *TestUtils) FormatBenchmarkResult(result BenchmarkResult) string {
	return fmt.Sprintf(`
性能测试结果:
  操作次数: %d
  总耗时: %v
  平均耗时: %v
  最小耗时: %v
  最大耗时: %v
  错误数: %d
  成功率: %.2f%%
`,
		result.Operations,
		result.TotalDuration,
		result.AverageDuration,
		result.MinDuration,
		result.MaxDuration,
		result.ErrorCount,
		float64(result.Operations-result.ErrorCount)/float64(result.Operations)*100,
	)
}
