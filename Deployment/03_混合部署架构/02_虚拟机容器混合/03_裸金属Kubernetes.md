# 裸金属Kubernetes

> **返回**: [虚拟机容器混合首页](README.md) | [混合部署架构首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [裸金属Kubernetes](#裸金属kubernetes)
  - [📋 目录](#-目录)
  - [1. 物理机部署Kubernetes](#1-物理机部署kubernetes)
  - [2. 性能优化](#2-性能优化)
  - [3. 硬件直通](#3-硬件直通)
  - [4. GPU/FPGA支持](#4-gpufpga支持)

---

## 1. 物理机部署Kubernetes

**适用场景**:

- 高性能计算 (HPC)
- AI/ML训练
- 大数据处理
- 延迟敏感应用

**部署方式**:

```bash
# 1. 准备物理机 (CentOS/Ubuntu)
# 关闭swap
swapoff -a
sed -i '/swap/d' /etc/fstab

# 加载内核模块
modprobe br_netfilter
modprobe overlay

# 2. 安装容器运行时 (containerd)
wget https://github.com/containerd/containerd/releases/download/v1.7.0/containerd-1.7.0-linux-amd64.tar.gz
tar Cxzvf /usr/local containerd-1.7.0-linux-amd64.tar.gz

# 3. 安装kubeadm, kubelet, kubectl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
apt-get update && apt-get install -y kubeadm kubelet kubectl

# 4. 初始化Master
kubeadm init --pod-network-cidr=10.244.0.0/16 \
  --apiserver-advertise-address=<master-ip>

# 5. 加入Worker节点
kubeadm join <master-ip>:6443 --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

---

## 2. 性能优化

**CPU性能优化**:

```yaml
# CPU Manager Static Policy
apiVersion: v1
kind: ConfigMap
metadata:
  name: kubelet-config
  namespace: kube-system
data:
  kubelet: |
    apiVersion: kubelet.config.k8s.io/v1beta1
    kind: KubeletConfiguration
    cpuManagerPolicy: static
    cpuManagerReconcilePeriod: 10s
```

**内存优化**:

```yaml
# Huge Pages支持
apiVersion: v1
kind: Pod
metadata:
  name: hugepages-pod
spec:
  containers:
  - name: app
    image: app:latest
    resources:
      requests:
        memory: "2Gi"
        hugepages-2Mi: "1Gi"
      limits:
        memory: "2Gi"
        hugepages-2Mi: "1Gi"
    volumeMounts:
    - name: hugepage
      mountPath: /hugepages
  volumes:
  - name: hugepage
    emptyDir:
      medium: HugePages
```

**网络性能优化**:

```bash
# SR-IOV网络插件
kubectl apply -f https://raw.githubusercontent.com/k8snetworkplumbingwg/sriov-network-operator/master/deploy/operator.yaml

# DPDK加速
kubectl apply -f userspace-cni.yaml
```

---

## 3. 硬件直通

**PCI设备直通**:

```yaml
# 配置节点PCI设备
apiVersion: v1
kind: Node
metadata:
  name: worker-1
  annotations:
    # Intel NIC直通
    intel.com/intel_sriov_netdevice: "8"  # 8个VF
---
# Pod使用PCI设备
apiVersion: v1
kind: Pod
metadata:
  name: pci-pod
spec:
  containers:
  - name: app
    image: app:latest
    resources:
      requests:
        intel.com/intel_sriov_netdevice: "1"
      limits:
        intel.com/intel_sriov_netdevice: "1"
```

---

## 4. GPU/FPGA支持

**NVIDIA GPU支持**:

```bash
# 安装NVIDIA Device Plugin
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/main/nvidia-device-plugin.yml

# 验证GPU节点
kubectl get nodes "-o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu"
```

**GPU Pod示例**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  containers:
  - name: cuda
    image: nvidia/cuda:11.0-base
    command: ["nvidia-smi"]
    resources:
      limits:
        nvidia.com/gpu: 1  # 请求1个GPU
---
# 多GPU
apiVersion: v1
kind: Pod
metadata:
  name: multi-gpu-pod
spec:
  containers:
  - name: training
    image: tensorflow/tensorflow:latest-gpu
    resources:
      limits:
        nvidia.com/gpu: 4  # 请求4个GPU
```

**GPU共享 (时间切片)**:

```yaml
# NVIDIA GPU Operator配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: time-slicing-config
data:
  tesla-t4: |-
    version: v1
    sharing:
      timeSlicing:
        replicas: 4  # 1个GPU虚拟化为4个
```

**FPGA支持**:

```yaml
# Intel FPGA Device Plugin
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: intel-fpga-plugin
spec:
  template:
    spec:
      containers:
      - name: intel-fpga-plugin
        image: intel/intel-fpga-plugin:latest
---
# Pod使用FPGA
apiVersion: v1
kind: Pod
metadata:
  name: fpga-pod
spec:
  containers:
  - name: app
    image: fpga-app:latest
    resources:
      limits:
        intel.com/fpga: 1
```

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 完成
