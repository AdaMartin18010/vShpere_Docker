# 容器化部署指南

> **返回**: [部署指南首页](../00_索引导航/README.md)

---

## 📋 目录

- [容器化部署指南](#容器化部署指南)
  - [📋 目录](#-目录)
  - [模块概述](#模块概述)
  - [模块列表](#模块列表)
  - [快速导航](#快速导航)
    - [Docker部署 (4文档)](#docker部署-4文档)
    - [Kubernetes部署 (5文档)](#kubernetes部署-5文档)
    - [容器网络 (4文档)](#容器网络-4文档)
    - [容器存储 (4文档)](#容器存储-4文档)
    - [服务网格 (4文档)](#服务网格-4文档)
  - [整体进度](#整体进度)
  - [学习路径](#学习路径)
    - [初学者路径](#初学者路径)
    - [进阶路径](#进阶路径)
    - [生产环境路径](#生产环境路径)
  - [技术栈对比](#技术栈对比)
  - [相关模块链接](#相关模块链接)

---

## 模块概述

容器化部署模块提供了从Docker基础到Kubernetes生产级部署的完整技术指南。涵盖容器运行时、编排系统、网络方案、存储方案、服务网格等云原生技术栈。

---

## 模块列表

| 序号 | 模块名称 | 状态 | 内容概述 |
|------|---------|------|---------|
| 01. | [Docker部署](01_Docker部署/README.md) | ✅ 已完成 | Docker安装、镜像管理、Compose、最佳实践 |
| 02. | [Kubernetes部署](02_Kubernetes部署/README.md) | ✅ 已完成 | 集群部署、组件配置、应用部署、故障排查 |
| 03. | [容器网络](03_容器网络/README.md) | ✅ 已完成 | CNI、Calico、Cilium、NetworkPolicy |
| 04. | [容器存储](04_容器存储/README.md) | ✅ 已完成 | CSI、Rook-Ceph、Longhorn、StorageClass |
| 05. | [服务网格](05_服务网格/README.md) | ✅ 已完成 | 服务网格概述、Istio、Linkerd、流量管理 |

**模块总览**: ✅ **100%** 完成 (21/21文档)

---

## 快速导航

### Docker部署 (4文档)

**子模块入口**: [Docker部署目录](01_Docker部署/README.md)

1. [Docker安装与配置](01_Docker部署/01_Docker安装与配置.md) 📝
   - Docker Engine安装 (Ubuntu/CentOS/RHEL)
   - Docker配置优化
   - Rootless Docker
   - Docker日志与监控

2. [Docker镜像管理](01_Docker部署/02_Docker镜像管理.md) 📝
   - 镜像构建最佳实践
   - Dockerfile优化
   - 多阶段构建
   - 私有镜像仓库 (Harbor)

3. [Docker Compose](01_Docker部署/03_Docker_Compose.md) 📝
   - Compose安装与配置
   - Compose文件详解
   - 多容器应用部署
   - Compose最佳实践

4. [Docker安全与最佳实践](01_Docker部署/04_Docker安全与最佳实践.md) 📝
   - 容器安全原则
   - 镜像扫描 (Trivy, Clair)
   - 安全加固 (Seccomp, AppArmor)
   - 资源限制与隔离

---

### Kubernetes部署 (5文档)

**子模块入口**: [Kubernetes部署目录](02_Kubernetes部署/README.md)

1. [Kubernetes集群部署](02_Kubernetes部署/01_集群部署.md) 📝
   - kubeadm安装部署
   - 二进制部署方式
   - 云厂商托管Kubernetes
   - 集群初始化与配置

2. [Kubernetes核心组件](02_Kubernetes部署/02_核心组件.md) 📝
   - API Server配置
   - Controller Manager
   - Scheduler调度器
   - Kubelet配置

3. [Kubernetes应用部署](02_Kubernetes部署/03_应用部署.md) 📝
   - Pod/Deployment/StatefulSet
   - Service/Ingress
   - ConfigMap/Secret
   - HPA/VPA自动扩缩容

4. [Kubernetes资源管理](02_Kubernetes部署/04_资源管理.md) 📝
   - 命名空间管理
   - 资源配额 (ResourceQuota)
   - Limit Range
   - RBAC权限管理

5. [Kubernetes故障排查](02_Kubernetes部署/05_故障排查.md) 📝
   - 常见故障场景
   - 日志收集与分析
   - 诊断命令集合
   - 故障排查流程

---

### 容器网络 (4文档)

**子模块入口**: [容器网络目录](03_容器网络/README.md)

1. [CNI网络概述](03_容器网络/01_CNI网络概述.md) 📝
   - CNI规范与工作原理
   - 主流CNI插件对比
   - 网络模型 (Overlay/Underlay)
   - 网络性能对比

2. [Calico网络配置](03_容器网络/02_Calico网络配置.md) 📝
   - Calico架构与原理
   - Calico安装部署
   - BGP模式配置
   - IP Pool管理

3. [Cilium eBPF网络](03_容器网络/03_Cilium_eBPF网络.md) 📝
   - Cilium架构与eBPF
   - Cilium安装部署
   - Hubble可观测性
   - 性能优化

4. [NetworkPolicy策略](03_容器网络/04_NetworkPolicy策略.md) 📝
   - NetworkPolicy概述
   - Ingress/Egress规则
   - 实战案例
   - 安全最佳实践

---

### 容器存储 (4文档)

**子模块入口**: [容器存储目录](04_容器存储/README.md)

1. [CSI存储概述](04_容器存储/01_CSI存储概述.md) 📝
   - CSI规范与架构
   - 存储类型对比
   - 主流CSI驱动
   - 存储选型建议

2. [Rook-Ceph存储](04_容器存储/02_Rook_Ceph存储.md) 📝
   - Rook架构与原理
   - Rook-Ceph部署
   - RBD/CephFS/RGW
   - 存储类配置

3. [Longhorn存储](04_容器存储/03_Longhorn存储.md) 📝
   - Longhorn架构
   - Longhorn部署
   - 卷管理与备份
   - 灾备恢复

4. [StorageClass最佳实践](04_容器存储/04_StorageClass最佳实践.md) 📝
   - StorageClass配置
   - 动态供应 (Dynamic Provisioning)
   - 卷快照 (VolumeSnapshot)
   - 性能优化

---

### 服务网格 (4文档)

**子模块入口**: [服务网格目录](05_服务网格/README.md)

1. [服务网格概述](05_服务网格/01_服务网格概述.md) 📝
   - 服务网格架构
   - Istio vs Linkerd对比
   - 使用场景
   - 选型建议

2. [Istio部署与配置](05_服务网格/02_Istio部署与配置.md) 📝
   - Istio架构详解
   - Istio安装部署
   - 流量管理
   - 可观测性

3. [Linkerd部署与配置](05_服务网格/03_Linkerd部署与配置.md) 📝
   - Linkerd架构
   - Linkerd安装部署
   - 服务发现与负载均衡
   - mTLS安全

4. [服务网格流量管理](05_服务网格/04_服务网格流量管理.md) 📝
   - 流量路由
   - 灰度发布 (Canary)
   - A/B测试
   - 熔断与限流

---

## 整体进度

```text
容器化部署模块进度统计
================================
📊 总计: 21个文档

✅ Docker部署:      4/4   (100%) - 约4,857行
✅ Kubernetes部署:  5/5   (100%) - 约6,230行
✅ 容器网络:        4/4   (100%) - 约5,600行
✅ 容器存储:        4/4   (100%) - 约5,800行
✅ 服务网格:        4/4   (100%) - 约5,800行
================================
✅ 总进度:        21/21  (100%)
```

**实际文档行数**: 约28,287行技术文档

**最后更新**: 2025-10-19

---

## 学习路径

### 初学者路径

**适合对象**: 容器技术初学者

**推荐顺序**:

1. **Docker基础** → [Docker安装与配置](01_Docker部署/01_Docker安装与配置.md)
2. **容器实战** → [Docker Compose](01_Docker部署/03_Docker_Compose.md)
3. **Kubernetes入门** → [Kubernetes集群部署](02_Kubernetes部署/01_集群部署.md)
4. **应用部署** → [Kubernetes应用部署](02_Kubernetes部署/03_应用部署.md)

**学习时间**: 2-4周

---

### 进阶路径

**适合对象**: 有Docker/Kubernetes基础，希望深入学习

**推荐顺序**:

1. **集群架构** → [Kubernetes核心组件](02_Kubernetes部署/02_核心组件.md)
2. **网络深入** → [CNI网络概述](03_容器网络/01_CNI网络概述.md) → [Calico](03_容器网络/02_Calico网络配置.md) 或 [Cilium](03_容器网络/03_Cilium_eBPF网络.md)
3. **存储方案** → [CSI存储概述](04_容器存储/01_CSI存储概述.md) → [Rook-Ceph](04_容器存储/02_Rook_Ceph存储.md)
4. **资源管理** → [Kubernetes资源管理](02_Kubernetes部署/04_资源管理.md)
5. **安全加固** → [Docker安全与最佳实践](01_Docker部署/04_Docker安全与最佳实践.md) + [NetworkPolicy](03_容器网络/04_NetworkPolicy策略.md)

**学习时间**: 4-8周

---

### 生产环境路径

**适合对象**: 准备在生产环境部署Kubernetes

**推荐顺序**:

1. **集群规划** → 参考 [虚拟化部署/硬件规范](../01_虚拟化部署/01_硬件规范/README.md)
2. **集群部署** → [Kubernetes集群部署](02_Kubernetes部署/01_集群部署.md)
3. **高可用配置** → [Kubernetes高可用架构](../01_虚拟化部署/05_高可用容灾/02_Kubernetes高可用架构.md)
4. **网络方案** → 选择 [Calico](03_容器网络/02_Calico网络配置.md) 或 [Cilium](03_容器网络/03_Cilium_eBPF网络.md)
5. **存储方案** → [Rook-Ceph](04_容器存储/02_Rook_Ceph存储.md) 或 [Longhorn](04_容器存储/03_Longhorn存储.md)
6. **服务网格** → [Istio](05_服务网格/02_Istio部署与配置.md) 或 [Linkerd](05_服务网格/03_Linkerd部署与配置.md)
7. **备份恢复** → [备份恢复方案](../01_虚拟化部署/05_高可用容灾/03_备份恢复方案.md)
8. **故障排查** → [Kubernetes故障排查](02_Kubernetes部署/05_故障排查.md)

**部署时间**: 2-4周 (根据规模)

---

## 技术栈对比

| 技术类别 | 推荐方案 | 备选方案 | 适用场景 |
|---------|----------|----------|---------|
| **容器运行时** | Docker | containerd, CRI-O | 通用场景 |
| **容器编排** | Kubernetes | Docker Swarm | 生产环境必选K8s |
| **网络方案** | Calico | Cilium, Flannel | Calico成熟稳定，Cilium高性能 |
| **存储方案** | Rook-Ceph | Longhorn, OpenEBS | Rook-Ceph功能全面 |
| **服务网格** | Istio | Linkerd | Istio功能丰富，Linkerd轻量 |
| **监控方案** | Prometheus + Grafana | Datadog, NewRelic | 开源首选Prometheus |
| **日志方案** | ELK/EFK | Loki, Splunk | EFK成熟，Loki轻量 |

---

## 相关模块链接

- [虚拟化部署](../01_虚拟化部署/README.md) - 基础设施部署
- [混合部署架构](../03_混合部署架构/README.md) - 虚拟化+容器化混合方案
- [运维管理](../04_运维管理/README.md) - 监控、日志、自动化

---

**模块维护**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ **模块完成！**
