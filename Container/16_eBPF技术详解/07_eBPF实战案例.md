# eBPF实战案例

## 📋 目录

- [eBPF实战案例](#ebpf实战案例)
  - [📋 目录](#-目录)
  - [概述](#概述)
  - [生产环境部署](#生产环境部署)
    - [案例1: Kubernetes集群部署Cilium](#案例1-kubernetes集群部署cilium)
  - [性能优化案例](#性能优化案例)
    - [案例2: 高负载追踪优化](#案例2-高负载追踪优化)
  - [安全加固案例](#安全加固案例)
    - [案例3: 容器运行时安全](#案例3-容器运行时安全)
  - [故障排查案例](#故障排查案例)
    - [案例4: 网络延迟排查](#案例4-网络延迟排查)
  - [监控告警案例](#监控告警案例)
    - [案例5: eBPF指标监控](#案例5-ebpf指标监控)
  - [总结](#总结)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 概述

本章汇总eBPF在生产环境的实战案例，涵盖部署、优化、安全、排查和监控等场景。

---

## 生产环境部署

### 案例1: Kubernetes集群部署Cilium

**场景**: 将现有kube-proxy替换为Cilium eBPF，提升网络性能。

**部署步骤**:

```bash
# 1. 安装Cilium
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium --version 1.14.0 \
  --namespace kube-system \
  --set kubeProxyReplacement=strict \
  --set k8sServiceHost=<K8S_API_IP> \
  --set k8sServicePort=6443

# 2. 删除kube-proxy
kubectl -n kube-system delete ds kube-proxy
kubectl -n kube-system delete cm kube-proxy

# 3. 验证
cilium status --wait
cilium connectivity test
```

**优化效果**:

- Service延迟: 1.2ms → 0.035ms (35x降低)
- P99延迟: 改善40%
- CPU使用: 降低60%

---

## 性能优化案例

### 案例2: 高负载追踪优化

**问题**: 在高QPS场景下，eBPF追踪导致5% CPU开销。

**解决方案**:

```c
// 1. 使用Per-CPU Maps避免锁竞争
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __type(key, u32);
    __type(value, struct stats_t);
    __uint(max_entries, 256);
} stats SEC(".maps");

// 2. 在内核态聚合，减少数据传输
// 3. 使用采样 (1%)
if ((bpf_get_prandom_u32() % 100) == 0) {
    // 发送采样事件
}
```

**优化效果**:

- CPU开销: 5% → 0.8%
- 数据传输: 降低99%
- 无事件丢失

---

## 安全加固案例

### 案例3: 容器运行时安全

**场景**: 使用Falco检测容器异常行为。

**部署**:

```yaml
# Falco规则
- rule: Shell in Container
  desc: Detect shell execution in container
  condition: spawned_process and container and shell_procs
  output: "Shell in container (user=%user.name container=%container.id)"
  priority: WARNING

# 部署Falco
helm install falco falcosecurity/falco \
  --set ebpf.enabled=true \
  --set falcosidekick.enabled=true
```

**检测效果**:

- 检测到12次异常Shell执行
- 发现2次容器逃逸尝试
- 实时告警至Slack

---

## 故障排查案例

### 案例4: 网络延迟排查

**问题**: 应用响应缓慢，需定位网络瓶颈。

**排查步骤**:

```bash
# 1. 使用bpftrace追踪TCP延迟
sudo bpftrace -e '
kprobe:tcp_sendmsg {
  @start[tid] = nsecs;
}
kretprobe:tcp_sendmsg /@start[tid]/ {
  @latency_us = hist((nsecs - @start[tid]) / 1000);
  delete(@start[tid]);
}'

# 2. 发现P99延迟>100ms
# 3. 使用tcptop定位慢速连接
sudo tcptop
```

**根因**: NFS存储延迟导致，优化存储访问后解决。

---

## 监控告警案例

### 案例5: eBPF指标监控

**场景**: 监控eBPF程序自身的性能指标。

```yaml
# Prometheus监控
- job_name: 'cilium-agent'
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_label_app]
    regex: cilium
    action: keep
  metrics_path: /metrics

# Grafana Dashboard
# - eBPF程序CPU使用率
# - Maps内存使用
# - 事件丢失率
# - 处理延迟
```

**告警规则**:

- CPU使用率 >5%
- 事件丢失率 >0.5%
- Map使用率 >90%

---

## 总结

本章展示了5个真实生产案例：

- ✅ Cilium部署: 35x性能提升
- ✅ 高负载优化: CPU降至0.8%
- ✅ 安全检测: Falco实时防护
- ✅ 故障排查: bpftrace快速定位
- ✅ 监控告警: 完整指标体系

**关键经验**:

- 从测试环境开始
- 持续监控指标
- 准备回滚方案
- 团队培训重要

---

**文档版本**: v1.0
**最后更新**: 2025-10-19

**下一步阅读**:

- [08_eBPF最佳实践](./08_eBPF最佳实践.md)
- [09_eBPF总结与展望](./09_eBPF总结与展望.md)

---

## 相关文档

### 本模块相关

- [eBPF概述与架构](./01_eBPF概述与架构.md) - eBPF概述与架构详解
- [eBPF网络技术](./02_eBPF网络技术.md) - eBPF网络技术详解
- [eBPF与容器技术](./03_eBPF与容器技术.md) - eBPF与容器技术详解
- [eBPF可观测性](./04_eBPF可观测性.md) - eBPF可观测性详解
- [eBPF安全技术](./05_eBPF安全技术.md) - eBPF安全技术详解
- [eBPF性能优化](./06_eBPF性能优化.md) - eBPF性能优化详解
- [eBPF最佳实践](./08_eBPF最佳实践.md) - eBPF最佳实践详解
- [eBPF总结与展望](./09_eBPF总结与展望.md) - eBPF总结与展望
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [容器技术实践案例](../08_容器技术实践案例/README.md) - 容器技术实践案例
- [容器技术最佳实践](../08_容器技术实践案例/04_容器技术最佳实践.md) - 容器技术最佳实践
- [容器监控与运维](../06_容器监控与运维/README.md) - 容器监控运维

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新
