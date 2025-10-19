# Kubevirt虚拟机编排

> **返回**: [虚拟机容器混合首页](README.md) | [混合部署架构首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Kubevirt虚拟机编排](#kubevirt虚拟机编排)
  - [📋 目录](#-目录)
  - [1. Kubevirt架构](#1-kubevirt架构)
  - [2. VM生命周期管理](#2-vm生命周期管理)
  - [3. VM迁移](#3-vm迁移)
  - [4. 统一运维](#4-统一运维)

---

## 1. Kubevirt架构

**Kubevirt概述**:
> KubeVirt 是一个Kubernetes插件，使Kubernetes能够管理虚拟机工作负载以及容器工作负载。

**核心组件**:

```text
┌─────────────────────────────────────┐
│     Kubernetes API Server           │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │  KubeVirt CRDs  │  (VirtualMachine, VirtualMachineInstance)
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ virt-controller │  (管理VM生命周期)
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  virt-handler   │  (节点Agent，管理libvirt)
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  virt-launcher  │  (每个VMI一个Pod，运行QEMU)
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │   QEMU/KVM      │  (虚拟机进程)
    └─────────────────┘
```

**安装Kubevirt**:

```bash
# 安装KubeVirt Operator
export KUBEVIRT_VERSION=v1.1.0
kubectl create -f https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_VERSION}/kubevirt-operator.yaml

# 安装KubeVirt CR
kubectl create -f https://github.com/kubevirt/kubevirt/releases/download/${KUBEVIRT_VERSION}/kubevirt-cr.yaml

# 验证安装
kubectl get kubevirt.kubevirt.io/kubevirt -n kubevirt -o=jsonpath="{.status.phase}"
```

---

## 2. VM生命周期管理

**创建虚拟机**:

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: ubuntu-vm
spec:
  running: true
  template:
    metadata:
      labels:
        kubevirt.io/vm: ubuntu-vm
    spec:
      domain:
        devices:
          disks:
          - name: containerdisk
            disk:
              bus: virtio
          - name: cloudinitdisk
            disk:
              bus: virtio
          interfaces:
          - name: default
            masquerade: {}
        resources:
          requests:
            memory: 2Gi
            cpu: 2
      networks:
      - name: default
        pod: {}
      volumes:
      - name: containerdisk
        containerDisk:
          image: quay.io/kubevirt/cirros-container-disk-demo:latest
      - name: cloudinitdisk
        cloudInitNoCloud:
          userData: |
            #cloud-config
            password: ubuntu
            chpasswd: { expire: False }
```

**操作虚拟机**:

```bash
# 启动VM
virtctl start ubuntu-vm

# 停止VM
virtctl stop ubuntu-vm

# 重启VM
virtctl restart ubuntu-vm

# 连接VM控制台
virtctl console ubuntu-vm

# SSH到VM
virtctl ssh ubuntu@ubuntu-vm
```

---

## 3. VM迁移

**实时迁移 (Live Migration)**:

```yaml
# 触发实时迁移
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstanceMigration
metadata:
  name: ubuntu-vm-migration
spec:
  vmiName: ubuntu-vm
```

```bash
# 使用virtctl迁移
virtctl migrate ubuntu-vm

# 查看迁移状态
kubectl get vmim
```

**自动迁移 (节点维护)**:

```bash
# 驱逐节点上的VM (自动迁移)
kubectl drain node1 --ignore-daemonsets --delete-emptydir-data

# VM会自动迁移到其他节点
kubectl get vmi -o wide
```

---

## 4. 统一运维

**VM与Pod统一管理**:

```bash
# 查看所有工作负载
kubectl get vmi,pod

# 统一监控 (Prometheus)
kubectl port-forward -n kubevirt svc/virt-api 8443:443

# 统一日志 (Fluent Bit)
kubectl logs virt-launcher-ubuntu-vm-xxxxx
```

**VM网络策略**:

```yaml
# 与容器共享NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-http
spec:
  podSelector:
    matchLabels:
      kubevirt.io/vm: ubuntu-vm
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 80
```

**VM存储管理**:

```yaml
# 使用Kubernetes PV
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: ubuntu-vm-pv
spec:
  template:
    spec:
      domain:
        devices:
          disks:
          - name: datavol
            disk:
              bus: virtio
      volumes:
      - name: datavol
        persistentVolumeClaim:
          claimName: ubuntu-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ubuntu-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: rook-ceph-block
```

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 完成
