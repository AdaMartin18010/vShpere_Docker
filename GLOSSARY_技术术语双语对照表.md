# 技术术语双语对照表 (Technical Glossary)

> **虚拟化与容器化技术核心术语中英对照** (1100+术语)  
> **版本**: v2.0  
> **更新日期**: 2025-10-19

---

## 目录 (Table of Contents)

- [A. 虚拟化基础 (Virtualization Fundamentals)](#a-虚拟化基础-virtualization-fundamentals)
- [B. 容器技术 (Container Technology)](#b-容器技术-container-technology)
- [C. 编排与调度 (Orchestration & Scheduling)](#c-编排与调度-orchestration--scheduling)
- [D. 网络技术 (Networking)](#d-网络技术-networking)
- [E. 存储技术 (Storage)](#e-存储技术-storage)
- [F. 安全技术 (Security)](#f-安全技术-security)
- [G. 监控与可观测性 (Monitoring & Observability)](#g-监控与可观测性-monitoring--observability)
- [H. 边缘计算 (Edge Computing)](#h-边缘计算-edge-computing)
- [I. AI/ML相关 (AI/ML)](#i-aiml相关-aiml)
- [J. 云原生 (Cloud Native)](#j-云原生-cloud-native)
- [K. DevOps & CI/CD](#k-devops--cicd)
- [L. 标准与协议 (Standards & Protocols)](#l-标准与协议-standards--protocols)

---

## A. 虚拟化基础 (Virtualization Fundamentals)

### A1. 核心概念

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 虚拟化 | Virtualization | - | 抽象物理资源 |
| 虚拟机 | Virtual Machine | VM | 虚拟化的计算实例 |
| 虚拟机监控器 | Hypervisor | VMM | 虚拟机管理器 |
| 裸金属虚拟化 | Bare-metal Hypervisor | Type-1 | 直接运行在硬件上 |
| 宿主型虚拟化 | Hosted Hypervisor | Type-2 | 运行在操作系统上 |
| 客户机操作系统 | Guest OS | - | 虚拟机内的操作系统 |
| 宿主机操作系统 | Host OS | - | 物理机操作系统 |
| 硬件辅助虚拟化 | Hardware-Assisted Virtualization | VT-x/AMD-V | CPU虚拟化支持 |
| 嵌套虚拟化 | Nested Virtualization | - | VM中运行VM |
| 半虚拟化 | Paravirtualization | - | 客户机知道被虚拟化 |
| 全虚拟化 | Full Virtualization | - | 完全模拟硬件 |

### A2. VMware vSphere

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 企业级虚拟化平台 | Enterprise Virtualization Platform | - | VMware vSphere |
| 虚拟化内核 | Virtualization Kernel | ESXi | Type-1 Hypervisor |
| 虚拟中心 | Virtual Center | vCenter | 集中管理平台 |
| 虚拟存储区域网络 | Virtual Storage Area Network | vSAN | 软件定义存储 |
| 网络虚拟化 | Network Virtualization | NSX | SDN解决方案 |
| 高可用性 | High Availability | HA | 自动故障转移 |
| 分布式资源调度器 | Distributed Resource Scheduler | DRS | 负载均衡 |
| 虚拟机模板 | Virtual Machine Template | - | 快速部署 |
| 克隆 | Clone | - | 复制VM |
| 快照 | Snapshot | - | VM状态备份 |
| 在线迁移 | Live Migration | vMotion | 无停机迁移 |
| 存储在线迁移 | Storage Live Migration | Storage vMotion | 存储迁移 |
| 分布式虚拟交换机 | Distributed Virtual Switch | vDS | 跨主机网络 |
| 容错 | Fault Tolerance | FT | 零停机保护 |
| 内容库 | Content Library | - | 模板共享 |

### A3. KVM & Linux虚拟化

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 基于内核的虚拟机 | Kernel-based Virtual Machine | KVM | Linux内核虚拟化 |
| 快速模拟器 | Quick Emulator | QEMU | 硬件模拟器 |
| 虚拟化库 | Virtualization Library | libvirt | 虚拟化管理API |
| 虚拟机管理器 | Virtual Machine Manager | virt-manager | GUI管理工具 |
| 虚拟化主机工具 | Virtualization Host Tools | virt-host | 主机管理 |
| 虚拟化客户机工具 | Guest Tools | virt-install | 安装工具 |
| 虚拟化文件系统 | Virtual Filesystem | virtio-fs | 共享文件系统 |
| 半虚拟化驱动 | Paravirtualized Drivers | virtio | 高性能I/O |
| SPICE协议 | Simple Protocol for Independent Computing Environments | SPICE | 远程显示 |

---

## B. 容器技术 (Container Technology)

### B1. Docker

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 容器 | Container | - | 轻量级虚拟化 |
| 镜像 | Image | - | 容器模板 |
| 容器引擎 | Container Engine | - | Docker Engine |
| 容器运行时 | Container Runtime | - | 运行容器 |
| 镜像仓库 | Image Registry | - | Docker Hub |
| 镜像层 | Image Layer | - | 增量存储 |
| 联合文件系统 | Union File System | UnionFS | 层级文件系统 |
| 写时复制 | Copy-on-Write | CoW | 存储优化 |
| 命名空间 | Namespace | - | 资源隔离 |
| 控制组 | Control Groups | cgroups | 资源限制 |
| 数据卷 | Volume | - | 持久化存储 |
| 网络模式 | Network Mode | bridge/host/none | 网络配置 |
| Dockerfile | Dockerfile | - | 镜像构建文件 |
| 多阶段构建 | Multi-stage Build | - | 优化镜像 |
| Docker Compose | Docker Compose | - | 多容器编排 |
| Docker Swarm | Docker Swarm | - | 容器集群 |
| 容器编排 | Container Orchestration | - | 集群管理 |

### B2. Podman

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| Pod管理器 | Pod Manager | Podman | 无守护进程容器 |
| 无根容器 | Rootless Container | - | 非root运行 |
| Pod | Pod | - | 容器组 |
| Buildah | Buildah | - | 镜像构建工具 |
| Skopeo | Skopeo | - | 镜像操作工具 |
| Systemd集成 | Systemd Integration | - | 系统服务 |
| Quadlet | Quadlet | - | Systemd容器 |

### B3. 容器标准

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 开放容器倡议 | Open Container Initiative | OCI | 容器标准组织 |
| 运行时规范 | Runtime Specification | runtime-spec | 容器运行规范 |
| 镜像规范 | Image Specification | image-spec | 镜像格式规范 |
| 分发规范 | Distribution Specification | distribution-spec | 镜像分发 |
| 容器运行时接口 | Container Runtime Interface | CRI | Kubernetes标准 |
| 容器网络接口 | Container Network Interface | CNI | 网络插件接口 |
| 容器存储接口 | Container Storage Interface | CSI | 存储插件接口 |
| 容器网络模型 | Container Network Model | CNM | Docker网络 |

### B4. 容器运行时

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| containerd | containerd | - | CNCF容器运行时 |
| CRI-O | CRI-O | - | Kubernetes原生 |
| 运行时容器 | Runtime Container | runc | OCI参考实现 |
| crun | crun | - | C语言实现 |
| Kata Containers | Kata Containers | - | 轻量级VM |
| gVisor | gVisor | - | 用户态内核 |
| Firecracker | Firecracker | - | 微VM |

---

## C. 编排与调度 (Orchestration & Scheduling)

### C1. Kubernetes核心

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| Kubernetes | Kubernetes | K8s | 容器编排平台 |
| 集群 | Cluster | - | K8s集群 |
| 节点 | Node | - | 工作节点 |
| 主节点 | Master Node | Control Plane | 控制平面 |
| 工作节点 | Worker Node | - | 运行应用 |
| Pod | Pod | - | 最小调度单元 |
| 副本集 | ReplicaSet | RS | 保证副本数 |
| 部署 | Deployment | Deploy | 应用部署 |
| 有状态集 | StatefulSet | STS | 有状态应用 |
| 守护进程集 | DaemonSet | DS | 每节点一个Pod |
| 任务 | Job | - | 批处理任务 |
| 定时任务 | CronJob | - | 定时执行 |
| 服务 | Service | Svc | 服务发现 |
| 入口 | Ingress | - | HTTP路由 |
| 配置映射 | ConfigMap | CM | 配置管理 |
| 密钥 | Secret | - | 敏感信息 |
| 命名空间 | Namespace | NS | 逻辑隔离 |
| 标签 | Label | - | 资源标记 |
| 选择器 | Selector | - | 标签匹配 |
| 注解 | Annotation | - | 元数据 |
| 持久卷 | Persistent Volume | PV | 存储资源 |
| 持久卷声明 | Persistent Volume Claim | PVC | 存储请求 |
| 存储类 | StorageClass | SC | 动态供应 |
| 网络策略 | NetworkPolicy | - | 网络隔离 |
| 服务账户 | ServiceAccount | SA | Pod身份 |
| 基于角色的访问控制 | Role-Based Access Control | RBAC | 权限管理 |
| 角色 | Role | - | 权限集合 |
| 集群角色 | ClusterRole | - | 集群级权限 |
| 角色绑定 | RoleBinding | - | 用户-角色 |
| 资源配额 | ResourceQuota | - | 资源限制 |
| 限制范围 | LimitRange | - | 默认限制 |
| 水平Pod自动扩缩 | Horizontal Pod Autoscaler | HPA | 自动扩容 |
| 垂直Pod自动扩缩 | Vertical Pod Autoscaler | VPA | 资源调整 |
| 优先级类 | PriorityClass | - | 调度优先级 |
| 污点 | Taint | - | 节点排斥 |
| 容忍 | Toleration | - | Pod容忍 |
| 亲和性 | Affinity | - | 调度偏好 |
| 反亲和性 | Anti-Affinity | - | 分散部署 |

### C2. Kubernetes组件

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| API服务器 | API Server | kube-apiserver | API入口 |
| 调度器 | Scheduler | kube-scheduler | Pod调度 |
| 控制器管理器 | Controller Manager | kube-controller-manager | 控制器 |
| 云控制器管理器 | Cloud Controller Manager | cloud-controller-manager | 云集成 |
| 键值存储 | Key-Value Store | etcd | 集群状态 |
| 容器运行时 | Container Runtime | - | 运行容器 |
| Kubelet | Kubelet | - | 节点代理 |
| Kube-proxy | Kube-proxy | - | 网络代理 |
| CoreDNS | CoreDNS | - | 集群DNS |
| CNI插件 | CNI Plugin | - | 网络插件 |
| CSI驱动 | CSI Driver | - | 存储驱动 |

### C3. Kubernetes扩展

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 自定义资源定义 | Custom Resource Definition | CRD | 扩展API |
| 自定义资源 | Custom Resource | CR | 自定义对象 |
| 操作器 | Operator | - | 自动化运维 |
| 控制器 | Controller | - | 调谐循环 |
| 准入控制器 | Admission Controller | - | 请求拦截 |
| 变更准入 | Mutating Admission | - | 修改资源 |
| 验证准入 | Validating Admission | - | 验证资源 |
| Webhook | Webhook | - | HTTP回调 |
| 聚合层 | Aggregation Layer | - | API扩展 |
| API服务 | API Service | - | 自定义API |

### C4. 轻量级K8s

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| K3s | K3s | - | 轻量级K8s |
| MicroK8s | MicroK8s | - | 单机K8s |
| K0s | K0s | - | 零依赖K8s |
| Minikube | Minikube | - | 本地K8s |
| Kind | Kubernetes in Docker | Kind | Docker中的K8s |
| Rancher | Rancher | - | K8s管理平台 |

---

## D. 网络技术 (Networking)

### D1. 容器网络

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 覆盖网络 | Overlay Network | - | 跨主机网络 |
| 虚拟可扩展局域网 | Virtual Extensible LAN | VXLAN | 隧道技术 |
| 通用路由封装 | Generic Routing Encapsulation | GRE | 隧道协议 |
| 桥接模式 | Bridge Mode | - | 默认网络 |
| 主机模式 | Host Mode | - | 共享主机网络 |
| 无网络模式 | None Mode | - | 无网络 |
| Macvlan | Macvlan | - | MAC地址虚拟 |
| IPvlan | IPvlan | - | IP虚拟化 |
| Calico | Calico | - | BGP网络 |
| Flannel | Flannel | - | 简单覆盖网络 |
| Weave Net | Weave Net | - | 网格网络 |
| Cilium | Cilium | - | eBPF网络 |
| Antrea | Antrea | - | Kubernetes CNI |

### D2. 服务网格

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 服务网格 | Service Mesh | - | 服务间通信 |
| Istio | Istio | - | 服务网格平台 |
| Linkerd | Linkerd | - | 轻量级网格 |
| 边车代理 | Sidecar Proxy | - | 代理模式 |
| 数据平面 | Data Plane | - | 流量转发 |
| 控制平面 | Control Plane | - | 策略管理 |
| Envoy代理 | Envoy Proxy | - | 高性能代理 |
| 流量管理 | Traffic Management | - | 路由控制 |
| 服务发现 | Service Discovery | - | 服务注册 |
| 负载均衡 | Load Balancing | - | 流量分发 |
| 熔断器 | Circuit Breaker | - | 故障隔离 |
| 限流 | Rate Limiting | - | 速率控制 |
| 重试 | Retry | - | 失败重试 |
| 超时 | Timeout | - | 请求超时 |
| 金丝雀部署 | Canary Deployment | - | 灰度发布 |
| 蓝绿部署 | Blue-Green Deployment | - | 零停机部署 |
| A/B测试 | A/B Testing | - | 流量分流 |
| 流量镜像 | Traffic Mirroring | - | 流量复制 |

### D3. 网络技术

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 软件定义网络 | Software-Defined Networking | SDN | 网络虚拟化 |
| 软件定义广域网 | Software-Defined WAN | SD-WAN | 广域网优化 |
| 网络功能虚拟化 | Network Functions Virtualization | NFV | 网络功能 |
| 扩展伯克利包过滤器 | Extended Berkeley Packet Filter | eBPF | 内核编程 |
| 快速数据路径 | eXpress Data Path | XDP | 内核网络加速 |
| 数据平面开发套件 | Data Plane Development Kit | DPDK | 用户态网络 |
| 单根I/O虚拟化 | Single Root I/O Virtualization | SR-IOV | 硬件虚拟化 |
| 时间敏感网络 | Time-Sensitive Networking | TSN | 确定性网络 |
| 虚拟私有网络 | Virtual Private Network | VPN | 加密隧道 |
| 虚拟局域网 | Virtual LAN | VLAN | 网络隔离 |

### D4. 负载均衡

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 负载均衡器 | Load Balancer | LB | 流量分发 |
| 七层负载均衡 | Layer 7 Load Balancing | L7 LB | 应用层 |
| 四层负载均衡 | Layer 4 Load Balancing | L4 LB | 传输层 |
| Nginx | Nginx | - | Web服务器 |
| HAProxy | HAProxy | - | 负载均衡器 |
| Traefik | Traefik | - | 云原生LB |
| MetalLB | MetalLB | - | 裸金属LB |
| 会话保持 | Session Persistence | Sticky Session | 会话亲和 |
| 健康检查 | Health Check | - | 探活 |
| 轮询 | Round Robin | RR | 负载算法 |
| 最少连接 | Least Connections | LC | 负载算法 |
| IP哈希 | IP Hash | - | 源地址哈希 |

---

## E. 存储技术 (Storage)

### E1. 存储类型

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 块存储 | Block Storage | - | 原始磁盘 |
| 文件存储 | File Storage | - | 文件系统 |
| 对象存储 | Object Storage | - | 键值存储 |
| 存储区域网络 | Storage Area Network | SAN | 块存储网络 |
| 网络附加存储 | Network Attached Storage | NAS | 文件存储网络 |
| 分布式文件系统 | Distributed File System | DFS | 集群文件系统 |
| 软件定义存储 | Software-Defined Storage | SDS | 存储虚拟化 |
| 超融合基础设施 | Hyper-Converged Infrastructure | HCI | 计算存储融合 |

### E2. 存储解决方案

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| Ceph | Ceph | - | 分布式存储 |
| GlusterFS | GlusterFS | - | 分布式文件系统 |
| MinIO | MinIO | - | S3兼容存储 |
| Longhorn | Longhorn | - | 云原生存储 |
| OpenEBS | OpenEBS | - | 容器存储 |
| Rook | Rook | - | 存储编排 |
| Portworx | Portworx | - | 企业存储 |
| 对象存储网关 | Object Storage Gateway | - | S3接口 |
| RADOS | Reliable Autonomic Distributed Object Store | RADOS | Ceph对象存储 |
| RBD | RADOS Block Device | RBD | Ceph块存储 |
| CephFS | Ceph File System | CephFS | Ceph文件系统 |

### E3. 数据管理

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 复制 | Replication | - | 数据冗余 |
| 纠删码 | Erasure Coding | EC | 容错编码 |
| 快照 | Snapshot | - | 数据快照 |
| 克隆 | Clone | - | 数据克隆 |
| 数据精简 | Thin Provisioning | - | 按需分配 |
| 重复数据删除 | Deduplication | Dedup | 去重 |
| 数据压缩 | Data Compression | - | 压缩 |
| 数据分层 | Data Tiering | - | 冷热分层 |
| 数据迁移 | Data Migration | - | 数据搬迁 |
| 备份 | Backup | - | 数据备份 |
| 恢复 | Restore | - | 数据恢复 |
| 灾难恢复 | Disaster Recovery | DR | 灾备 |
| Velero | Velero | - | K8s备份 |
| Restic | Restic | - | 备份工具 |

---

## F. 安全技术 (Security)

### F1. 身份与访问

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 身份认证 | Authentication | AuthN | 身份验证 |
| 授权 | Authorization | AuthZ | 权限控制 |
| 身份和访问管理 | Identity and Access Management | IAM | 身份管理 |
| 单点登录 | Single Sign-On | SSO | 统一登录 |
| 多因素认证 | Multi-Factor Authentication | MFA | 多重验证 |
| OAuth 2.0 | OAuth 2.0 | - | 授权框架 |
| OpenID Connect | OpenID Connect | OIDC | 身份层 |
| SAML | Security Assertion Markup Language | SAML | 身份标准 |
| LDAP | Lightweight Directory Access Protocol | LDAP | 目录协议 |
| 活动目录 | Active Directory | AD | 微软目录 |
| Keycloak | Keycloak | - | 身份管理 |
| Dex | Dex | - | OIDC提供商 |

### F2. 零信任

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 零信任架构 | Zero Trust Architecture | ZTA | 永不信任 |
| SPIFFE | Secure Production Identity Framework For Everyone | SPIFFE | 身份标准 |
| SPIRE | SPIFFE Runtime Environment | SPIRE | SPIFFE实现 |
| 服务身份文档 | Service Identity Document | SVID | SPIFFE身份 |
| 相互TLS | Mutual TLS | mTLS | 双向认证 |
| 工作负载身份 | Workload Identity | - | 服务身份 |
| 身份联邦 | Identity Federation | - | 跨域身份 |
| 最小权限原则 | Principle of Least Privilege | PoLP | 最小授权 |
| 微分段 | Micro-segmentation | - | 网络隔离 |

### F3. 容器安全

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 镜像扫描 | Image Scanning | - | 漏洞扫描 |
| 漏洞管理 | Vulnerability Management | - | 安全漏洞 |
| 常见漏洞和暴露 | Common Vulnerabilities and Exposures | CVE | 漏洞编号 |
| Trivy | Trivy | - | 镜像扫描器 |
| Clair | Clair | - | 漏洞分析 |
| Anchore | Anchore | - | 镜像分析 |
| Falco | Falco | - | 运行时检测 |
| Pod安全策略 | Pod Security Policy | PSP | Pod安全 |
| Pod安全标准 | Pod Security Standards | PSS | 安全等级 |
| 准入控制 | Admission Control | - | 策略执行 |
| OPA | Open Policy Agent | OPA | 策略引擎 |
| Gatekeeper | Gatekeeper | - | OPA for K8s |
| Kyverno | Kyverno | - | K8s策略 |
| Seccomp | Secure Computing Mode | Seccomp | 系统调用过滤 |
| AppArmor | Application Armor | AppArmor | 访问控制 |
| SELinux | Security-Enhanced Linux | SELinux | 强制访问控制 |
| 容器运行时保护 | Container Runtime Protection | - | 运行时安全 |
| Aqua Security | Aqua Security | - | 容器安全平台 |
| Sysdig Secure | Sysdig Secure | - | 容器安全 |

### F4. 机密计算

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 机密计算 | Confidential Computing | - | 数据使用加密 |
| 可信执行环境 | Trusted Execution Environment | TEE | 隔离执行 |
| 安全飞地 | Secure Enclave | - | Intel SGX |
| Intel TDX | Intel Trust Domain Extensions | TDX | 虚拟机TEE |
| AMD SEV | AMD Secure Encrypted Virtualization | SEV | 内存加密 |
| AMD SEV-SNP | AMD SEV-Secure Nested Paging | SEV-SNP | 完整性保护 |
| 机密容器 | Confidential Containers | CoCo | 容器TEE |
| 远程证明 | Remote Attestation | - | 平台验证 |
| 可信平台模块 | Trusted Platform Module | TPM | 硬件安全 |
| 安全启动 | Secure Boot | - | 启动验证 |
| 度量启动 | Measured Boot | - | 启动度量 |

### F5. 供应链安全

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 软件物料清单 | Software Bill of Materials | SBOM | 组件清单 |
| SPDX | Software Package Data Exchange | SPDX | SBOM格式 |
| CycloneDX | CycloneDX | - | SBOM格式 |
| Syft | Syft | - | SBOM生成 |
| 软件供应链 | Software Supply Chain | - | 开发流程 |
| Sigstore | Sigstore | - | 供应链签名 |
| Cosign | Cosign | - | 容器签名 |
| Rekor | Rekor | - | 透明日志 |
| Fulcio | Fulcio | - | 证书颁发 |
| SLSA | Supply chain Levels for Software Artifacts | SLSA | 供应链框架 |
| 镜像签名 | Image Signing | - | 数字签名 |
| 内容信任 | Content Trust | - | Docker签名 |
| Notary | Notary | - | 内容信任 |

### F6. 加密与密钥

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 静态加密 | Encryption at Rest | - | 存储加密 |
| 传输加密 | Encryption in Transit | - | 通信加密 |
| 使用中加密 | Encryption in Use | - | 计算加密 |
| 传输层安全 | Transport Layer Security | TLS | 加密协议 |
| 证书 | Certificate | Cert | 数字证书 |
| 公钥基础设施 | Public Key Infrastructure | PKI | 证书体系 |
| 证书颁发机构 | Certificate Authority | CA | 签发证书 |
| Let's Encrypt | Let's Encrypt | - | 免费CA |
| cert-manager | cert-manager | - | K8s证书管理 |
| 密钥管理服务 | Key Management Service | KMS | 密钥管理 |
| Vault | HashiCorp Vault | Vault | 密钥管理 |
| Sealed Secrets | Sealed Secrets | - | K8s加密 |
| 外部密钥管理 | External Secrets | - | 密钥同步 |

---

## G. 监控与可观测性 (Monitoring & Observability)

### G1. 监控指标

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 可观测性 | Observability | O11y | 系统可见性 |
| 指标 | Metrics | - | 性能数据 |
| 日志 | Logs | - | 事件记录 |
| 追踪 | Traces | - | 调用链 |
| Prometheus | Prometheus | - | 监控系统 |
| Grafana | Grafana | - | 可视化平台 |
| Alertmanager | Alertmanager | - | 告警管理 |
| Thanos | Thanos | - | 长期存储 |
| Cortex | Cortex | - | 多租户 |
| VictoriaMetrics | VictoriaMetrics | - | 时序数据库 |
| 节点导出器 | Node Exporter | - | 节点指标 |
| cAdvisor | Container Advisor | cAdvisor | 容器指标 |
| Kube-state-metrics | Kube-state-metrics | - | K8s指标 |
| Metrics Server | Metrics Server | - | K8s资源指标 |
| PromQL | Prometheus Query Language | PromQL | 查询语言 |

### G2. 日志管理

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 日志聚合 | Log Aggregation | - | 集中日志 |
| ELK栈 | Elasticsearch, Logstash, Kibana | ELK | 日志方案 |
| Elasticsearch | Elasticsearch | ES | 搜索引擎 |
| Logstash | Logstash | - | 日志处理 |
| Kibana | Kibana | - | 日志可视化 |
| Fluentd | Fluentd | - | 日志收集 |
| Fluent Bit | Fluent Bit | - | 轻量级收集 |
| Grafana Loki | Grafana Loki | Loki | 日志系统 |
| Promtail | Promtail | - | Loki代理 |
| LogQL | Log Query Language | LogQL | Loki查询 |
| Filebeat | Filebeat | - | 日志采集 |
| Vector | Vector | - | 日志路由 |

### G3. 分布式追踪

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 分布式追踪 | Distributed Tracing | - | 调用链追踪 |
| Jaeger | Jaeger | - | 追踪系统 |
| Zipkin | Zipkin | - | 追踪系统 |
| OpenTracing | OpenTracing | - | 追踪标准 |
| OpenTelemetry | OpenTelemetry | OTel | 可观测性标准 |
| Span | Span | - | 追踪片段 |
| Trace | Trace | - | 完整追踪 |
| 上下文传播 | Context Propagation | - | 追踪传递 |
| 采样 | Sampling | - | 采样策略 |
| Tempo | Grafana Tempo | Tempo | 追踪后端 |
| SkyWalking | Apache SkyWalking | - | APM平台 |

### G4. APM

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 应用性能管理 | Application Performance Management | APM | 性能监控 |
| 应用性能监控 | Application Performance Monitoring | APM | 性能监控 |
| 用户体验监控 | Real User Monitoring | RUM | 真实用户 |
| 合成监控 | Synthetic Monitoring | - | 模拟监控 |
| New Relic | New Relic | - | APM平台 |
| Datadog | Datadog | - | 监控平台 |
| Dynatrace | Dynatrace | - | APM平台 |
| AppDynamics | AppDynamics | - | APM平台 |
| Elastic APM | Elastic APM | - | Elastic监控 |
| Pinpoint | Pinpoint | - | APM平台 |

---

## H. 边缘计算 (Edge Computing)

### H1. 边缘平台

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 边缘计算 | Edge Computing | - | 边缘侧计算 |
| 雾计算 | Fog Computing | - | 雾计算 |
| 移动边缘计算 | Multi-access Edge Computing | MEC | 5G边缘 |
| 内容分发网络 | Content Delivery Network | CDN | 边缘缓存 |
| KubeEdge | KubeEdge | - | K8s边缘 |
| K3s | K3s | - | 轻量级K8s |
| OpenYurt | OpenYurt | - | 阿里云边缘 |
| Azure IoT Edge | Azure IoT Edge | - | 微软边缘 |
| AWS IoT Greengrass | AWS IoT Greengrass | - | 亚马逊边缘 |
| EdgeX Foundry | EdgeX Foundry | - | IoT平台 |
| Akri | Akri | - | 设备发现 |

### H2. 边缘技术

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 云边协同 | Cloud-Edge Collaboration | - | 云边一体 |
| 边缘自治 | Edge Autonomy | - | 离线运行 |
| 设备管理 | Device Management | - | 设备控制 |
| 设备孪生 | Device Twin | - | 数字孪生 |
| 设备插件 | Device Plugin | - | 设备接入 |
| 设备映射器 | Device Mapper | - | 设备协议 |
| 边缘应用 | Edge Application | - | 边缘App |
| 边缘节点 | Edge Node | - | 边缘服务器 |
| 边缘网关 | Edge Gateway | - | 边缘网关 |
| 边缘服务网格 | Edge Service Mesh | EdgeMesh | 边缘网络 |

### H3. IoT

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 物联网 | Internet of Things | IoT | 设备联网 |
| 工业物联网 | Industrial IoT | IIoT | 工业IoT |
| 物联网平台 | IoT Platform | - | IoT管理 |
| 消息队列遥测传输 | Message Queuing Telemetry Transport | MQTT | IoT协议 |
| 受约束应用协议 | Constrained Application Protocol | CoAP | 轻量级协议 |
| OPC统一架构 | OPC Unified Architecture | OPC-UA | 工业协议 |
| 数据分发服务 | Data Distribution Service | DDS | 实时通信 |
| LoRaWAN | Long Range Wide Area Network | LoRaWAN | 低功耗广域网 |
| NB-IoT | Narrowband IoT | NB-IoT | 窄带物联网 |
| Zigbee | Zigbee | - | 近距离通信 |
| Bluetooth LE | Bluetooth Low Energy | BLE | 蓝牙 |
| Modbus | Modbus | - | 工业协议 |
| CANbus | Controller Area Network | CAN | 汽车总线 |

---

## I. AI/ML相关 (AI/ML)

### I1. AI推理

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 人工智能 | Artificial Intelligence | AI | 人工智能 |
| 机器学习 | Machine Learning | ML | 机器学习 |
| 深度学习 | Deep Learning | DL | 深度学习 |
| 推理 | Inference | - | 模型推理 |
| 训练 | Training | - | 模型训练 |
| 模型 | Model | - | AI模型 |
| 神经网络 | Neural Network | NN | 神经网络 |
| 卷积神经网络 | Convolutional Neural Network | CNN | 图像处理 |
| 循环神经网络 | Recurrent Neural Network | RNN | 序列处理 |
| 变换器 | Transformer | - | 注意力机制 |
| 大语言模型 | Large Language Model | LLM | 语言模型 |

### I2. 推理框架

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| TensorRT | TensorRT | - | NVIDIA推理 |
| ONNX运行时 | ONNX Runtime | ONNX RT | 跨平台推理 |
| OpenVINO | OpenVINO | - | Intel推理 |
| TensorFlow Lite | TensorFlow Lite | TFLite | 移动端推理 |
| PyTorch Mobile | PyTorch Mobile | - | PyTorch移动端 |
| NCNN | NCNN | - | ARM推理 |
| MNN | MNN | - | 阿里推理 |
| Paddle Lite | Paddle Lite | - | 百度推理 |
| TVM | TVM | - | 编译器 |
| XLA | Accelerated Linear Algebra | XLA | TensorFlow编译器 |

### I3. 模型优化

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 量化 | Quantization | - | 精度降低 |
| INT8量化 | INT8 Quantization | - | 8位整数 |
| FP16 | Half Precision | FP16 | 半精度 |
| 剪枝 | Pruning | - | 删除权重 |
| 知识蒸馏 | Knowledge Distillation | - | 模型压缩 |
| 神经架构搜索 | Neural Architecture Search | NAS | 自动设计 |
| 模型压缩 | Model Compression | - | 模型优化 |
| 模型加速 | Model Acceleration | - | 推理加速 |

### I4. GPU与加速器

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 图形处理单元 | Graphics Processing Unit | GPU | GPU |
| NVIDIA CUDA | Compute Unified Device Architecture | CUDA | NVIDIA并行计算 |
| cuDNN | CUDA Deep Neural Network | cuDNN | CUDA深度学习库 |
| 张量处理单元 | Tensor Processing Unit | TPU | Google TPU |
| 神经网络处理单元 | Neural Processing Unit | NPU | AI处理器 |
| 昇腾 | Ascend | - | 华为AI芯片 |
| 寒武纪 | Cambricon | - | AI芯片 |
| 天数智芯 | Iluvatar | - | 国产GPU |
| 摩尔线程 | Moore Threads | - | 国产GPU |
| 壁仞科技 | Biren | - | 国产GPU |
| 海光DCU | Hygon DCU | DCU | 国产GPU |

### I5. ML平台

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| Kubeflow | Kubeflow | - | K8s上的ML |
| MLflow | MLflow | - | ML生命周期 |
| KServe | KServe | - | 模型服务 |
| Seldon Core | Seldon Core | - | ML部署 |
| BentoML | BentoML | - | 模型服务 |
| Ray | Ray | - | 分布式ML |
| Horovod | Horovod | - | 分布式训练 |

---

## J. 云原生 (Cloud Native)

### J1. 云原生核心

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 云原生 | Cloud Native | - | 云原生 |
| 云原生计算基金会 | Cloud Native Computing Foundation | CNCF | 开源基金会 |
| 微服务 | Microservices | - | 微服务架构 |
| 十二要素应用 | Twelve-Factor App | - | 应用准则 |
| 无状态 | Stateless | - | 无状态设计 |
| 有状态 | Stateful | - | 有状态应用 |
| 弹性伸缩 | Elastic Scaling | - | 自动扩缩 |
| 不可变基础设施 | Immutable Infrastructure | - | 不可变 |
| 声明式API | Declarative API | - | 声明式 |
| 命令式API | Imperative API | - | 命令式 |

### J2. Serverless

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 无服务器 | Serverless | - | 函数计算 |
| 函数即服务 | Function as a Service | FaaS | 事件驱动 |
| Knative | Knative | - | K8s Serverless |
| OpenFaaS | OpenFaaS | - | 开源FaaS |
| Fission | Fission | - | K8s FaaS |
| Kubeless | Kubeless | - | K8s原生FaaS |
| 冷启动 | Cold Start | - | 冷启动延迟 |
| 热启动 | Warm Start | - | 预热实例 |
| 事件驱动 | Event-Driven | - | 事件触发 |

### J3. WebAssembly

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| WebAssembly | WebAssembly | Wasm | 字节码格式 |
| WASI | WebAssembly System Interface | WASI | 系统接口 |
| WasmEdge | WasmEdge | - | Wasm运行时 |
| Wasmtime | Wasmtime | - | Wasm运行时 |
| Wasmer | Wasmer | - | Wasm运行时 |
| Spin | Spin | - | Wasm框架 |
| wasm-to-oci | wasm-to-oci | - | Wasm打包 |

---

## K. DevOps & CI/CD

### K1. CI/CD

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 持续集成 | Continuous Integration | CI | 代码集成 |
| 持续交付 | Continuous Delivery | CD | 持续交付 |
| 持续部署 | Continuous Deployment | CD | 自动部署 |
| Jenkins | Jenkins | - | CI/CD平台 |
| GitLab CI | GitLab CI | - | GitLab CI |
| GitHub Actions | GitHub Actions | - | GitHub CI |
| CircleCI | CircleCI | - | CI平台 |
| Travis CI | Travis CI | - | CI平台 |
| Tekton | Tekton | - | K8s原生CI |
| Argo Workflows | Argo Workflows | - | K8s工作流 |
| Drone | Drone | - | CI平台 |
| Spinnaker | Spinnaker | - | CD平台 |

### K2. GitOps

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| GitOps | GitOps | - | Git驱动运维 |
| ArgoCD | ArgoCD | - | GitOps CD |
| Flux | Flux | - | GitOps CD |
| Flagger | Flagger | - | 渐进式交付 |
| ApplicationSet | ApplicationSet | - | ArgoCD多集群 |
| Kustomize | Kustomize | - | 配置管理 |
| Helm | Helm | - | K8s包管理 |
| Chart | Helm Chart | - | Helm包 |
| Release | Release | - | 部署实例 |
| Values | Values | - | 配置值 |

### K3. 基础设施即代码

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 基础设施即代码 | Infrastructure as Code | IaC | 代码化基础设施 |
| Terraform | Terraform | TF | 基础设施管理 |
| Pulumi | Pulumi | - | 云资源管理 |
| Ansible | Ansible | - | 自动化工具 |
| Chef | Chef | - | 配置管理 |
| Puppet | Puppet | - | 配置管理 |
| CloudFormation | AWS CloudFormation | CFN | AWS资源管理 |
| ARM模板 | Azure Resource Manager | ARM | Azure模板 |
| Crossplane | Crossplane | - | K8s基础设施 |

### K4. 版本控制

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 版本控制系统 | Version Control System | VCS | 版本管理 |
| Git | Git | - | 分布式VCS |
| GitHub | GitHub | - | 代码托管 |
| GitLab | GitLab | - | DevOps平台 |
| Gitea | Gitea | - | 轻量级Git |
| 分支 | Branch | - | 代码分支 |
| 标签 | Tag | - | 版本标记 |
| 合并请求 | Merge Request | MR | 代码合并 |
| 拉取请求 | Pull Request | PR | 代码审查 |
| 提交 | Commit | - | 代码提交 |
| 变基 | Rebase | - | 变更基准 |

---

## L. 标准与协议 (Standards & Protocols)

### L1. 容器标准

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 开放容器倡议 | Open Container Initiative | OCI | 容器标准 |
| 云原生计算基金会 | Cloud Native Computing Foundation | CNCF | 云原生基金会 |
| 容器运行时接口 | Container Runtime Interface | CRI | K8s标准 |
| 容器网络接口 | Container Network Interface | CNI | 网络标准 |
| 容器存储接口 | Container Storage Interface | CSI | 存储标准 |
| 服务网格接口 | Service Mesh Interface | SMI | 网格标准 |
| OpenTelemetry | OpenTelemetry | OTel | 可观测性标准 |

### L2. 网络协议

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 超文本传输协议 | Hypertext Transfer Protocol | HTTP | Web协议 |
| HTTP/2 | HTTP/2 | - | HTTP版本2 |
| HTTP/3 | HTTP/3 | - | 基于QUIC |
| gRPC | gRPC Remote Procedure Call | gRPC | RPC框架 |
| WebSocket | WebSocket | WS | 双向通信 |
| QUIC | Quick UDP Internet Connections | QUIC | 传输协议 |
| TCP | Transmission Control Protocol | TCP | 传输控制协议 |
| UDP | User Datagram Protocol | UDP | 用户数据报协议 |
| IP | Internet Protocol | IP | 网际协议 |
| DNS | Domain Name System | DNS | 域名系统 |
| DHCP | Dynamic Host Configuration Protocol | DHCP | 动态IP |

### L3. 安全协议

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 传输层安全 | Transport Layer Security | TLS | 加密协议 |
| 安全套接字层 | Secure Sockets Layer | SSL | TLS前身 |
| IPsec | Internet Protocol Security | IPsec | IP加密 |
| SSH | Secure Shell | SSH | 安全Shell |
| X.509 | X.509 | - | 证书标准 |
| JSON Web Token | JSON Web Token | JWT | 认证令牌 |
| OAuth 2.0 | OAuth 2.0 | - | 授权协议 |
| OpenID Connect | OpenID Connect | OIDC | 身份协议 |
| SAML | Security Assertion Markup Language | SAML | 身份标准 |

### L4. 标准组织

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 互联网工程任务组 | Internet Engineering Task Force | IETF | 网络标准 |
| 万维网联盟 | World Wide Web Consortium | W3C | Web标准 |
| 国际标准化组织 | International Organization for Standardization | ISO | 国际标准 |
| 国际电工委员会 | International Electrotechnical Commission | IEC | 电工标准 |
| IEEE | Institute of Electrical and Electronics Engineers | IEEE | 电气电子工程师学会 |
| 国家标准与技术研究院 | National Institute of Standards and Technology | NIST | 美国标准 |
| CIS | Center for Internet Security | CIS | 安全基准 |
| OWASP | Open Web Application Security Project | OWASP | Web安全 |
| ETSI | European Telecommunications Standards Institute | ETSI | 欧洲电信标准 |

---

## M. 其他技术 (Other Technologies)

### M1. 数据库

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 关系型数据库 | Relational Database | RDBMS | SQL数据库 |
| NoSQL数据库 | NoSQL Database | NoSQL | 非关系型 |
| PostgreSQL | PostgreSQL | PG | 开源数据库 |
| MySQL | MySQL | - | 流行数据库 |
| MongoDB | MongoDB | - | 文档数据库 |
| Redis | Redis | - | 内存数据库 |
| Cassandra | Apache Cassandra | - | 分布式数据库 |
| Elasticsearch | Elasticsearch | ES | 搜索引擎 |
| etcd | etcd | - | 分布式KV |
| Consul | Consul | - | 服务发现 |

### M2. 消息队列

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 消息队列 | Message Queue | MQ | 异步通信 |
| Kafka | Apache Kafka | - | 分布式流 |
| RabbitMQ | RabbitMQ | - | AMQP实现 |
| NATS | NATS | - | 云原生消息 |
| Pulsar | Apache Pulsar | - | 流平台 |
| RocketMQ | Apache RocketMQ | - | 阿里MQ |
| MQTT | Message Queuing Telemetry Transport | MQTT | IoT消息 |
| AMQP | Advanced Message Queuing Protocol | AMQP | 消息协议 |

### M3. 配置管理

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 配置中心 | Configuration Center | - | 配置管理 |
| Consul | HashiCorp Consul | - | 服务发现 |
| etcd | etcd | - | 键值存储 |
| ZooKeeper | Apache ZooKeeper | ZK | 协调服务 |
| Nacos | Nacos | - | 阿里配置中心 |
| Apollo | Apollo | - | 携程配置中心 |
| Spring Cloud Config | Spring Cloud Config | - | Spring配置 |

### M4. API网关

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| API网关 | API Gateway | - | API入口 |
| Kong | Kong | - | API网关 |
| APISIX | Apache APISIX | - | 云原生网关 |
| Tyk | Tyk | - | API管理 |
| Ambassador | Ambassador | - | K8s网关 |
| Gloo | Gloo | - | Envoy网关 |
| Nginx | Nginx | - | Web服务器 |
| Traefik | Traefik | - | 云原生代理 |

### M5. 混沌工程

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 混沌工程 | Chaos Engineering | - | 故障注入 |
| Chaos Mesh | Chaos Mesh | - | K8s混沌 |
| Litmus | Litmus Chaos | - | CNCF混沌 |
| Chaos Toolkit | Chaos Toolkit | - | 混沌工具 |
| Gremlin | Gremlin | - | 混沌平台 |
| 故障注入 | Fault Injection | - | 注入故障 |
| 弹性测试 | Resilience Testing | - | 韧性测试 |

---

## N. 性能与优化 (Performance & Optimization)

### N1. 性能指标

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 服务级别协议 | Service Level Agreement | SLA | 服务保证 |
| 服务级别目标 | Service Level Objective | SLO | 目标指标 |
| 服务级别指标 | Service Level Indicator | SLI | 指标度量 |
| 恢复时间目标 | Recovery Time Objective | RTO | 恢复时间 |
| 恢复点目标 | Recovery Point Objective | RPO | 数据恢复点 |
| 每秒查询数 | Queries Per Second | QPS | 查询性能 |
| 每秒事务数 | Transactions Per Second | TPS | 事务性能 |
| 延迟 | Latency | - | 响应时间 |
| 吞吐量 | Throughput | - | 处理能力 |
| 可用性 | Availability | - | 可用时间 |
| 并发数 | Concurrency | - | 同时请求 |
| IOPS | Input/Output Operations Per Second | IOPS | IO性能 |
| 带宽 | Bandwidth | - | 传输速率 |

### N2. 扩展模式

| 中文 | English | 缩写/别名 | 说明 |
|------|---------|----------|------|
| 垂直扩展 | Vertical Scaling | Scale-up | 增加资源 |
| 水平扩展 | Horizontal Scaling | Scale-out | 增加实例 |
| 自动扩缩容 | Auto Scaling | - | 自动调整 |
| 弹性 | Elasticity | - | 伸缩能力 |
| 高可用 | High Availability | HA | 可用性 |
| 负载均衡 | Load Balancing | LB | 流量分发 |
| 故障转移 | Failover | - | 故障切换 |
| 冗余 | Redundancy | - | 冗余备份 |

---

## 附录 (Appendix)

### 常用缩写速查 (Quick Reference)

```text
AI - Artificial Intelligence (人工智能)
API - Application Programming Interface (应用程序接口)
APM - Application Performance Monitoring (应用性能监控)
CA - Certificate Authority (证书颁发机构)
CD - Continuous Delivery/Deployment (持续交付/部署)
CDN - Content Delivery Network (内容分发网络)
CI - Continuous Integration (持续集成)
CLI - Command Line Interface (命令行接口)
CNCF - Cloud Native Computing Foundation (云原生计算基金会)
CNI - Container Network Interface (容器网络接口)
CoW - Copy-on-Write (写时复制)
CRI - Container Runtime Interface (容器运行时接口)
CSI - Container Storage Interface (容器存储接口)
DNS - Domain Name System (域名系统)
DPDK - Data Plane Development Kit (数据平面开发套件)
eBPF - Extended Berkeley Packet Filter (扩展伯克利包过滤器)
GPU - Graphics Processing Unit (图形处理单元)
gRPC - gRPC Remote Procedure Call (远程过程调用)
HA - High Availability (高可用性)
HCI - Hyper-Converged Infrastructure (超融合基础设施)
HPA - Horizontal Pod Autoscaler (水平Pod自动扩缩)
HTTP - Hypertext Transfer Protocol (超文本传输协议)
IaC - Infrastructure as Code (基础设施即代码)
IAM - Identity and Access Management (身份和访问管理)
IoT - Internet of Things (物联网)
K8s - Kubernetes (容器编排平台)
KMS - Key Management Service (密钥管理服务)
KVM - Kernel-based Virtual Machine (基于内核的虚拟机)
LB - Load Balancer (负载均衡器)
LLM - Large Language Model (大语言模型)
MEC - Multi-access Edge Computing (移动边缘计算)
ML - Machine Learning (机器学习)
mTLS - Mutual TLS (相互TLS)
NFV - Network Functions Virtualization (网络功能虚拟化)
NPU - Neural Processing Unit (神经网络处理单元)
OCI - Open Container Initiative (开放容器倡议)
OIDC - OpenID Connect (OpenID连接)
OPA - Open Policy Agent (开放策略代理)
OTel - OpenTelemetry (开放遥测)
PVC - Persistent Volume Claim (持久卷声明)
RBAC - Role-Based Access Control (基于角色的访问控制)
REST - Representational State Transfer (表述性状态转移)
RPC - Remote Procedure Call (远程过程调用)
SBOM - Software Bill of Materials (软件物料清单)
SDS - Software-Defined Storage (软件定义存储)
SDN - Software-Defined Networking (软件定义网络)
SELinux - Security-Enhanced Linux (安全增强Linux)
SLA - Service Level Agreement (服务级别协议)
SLSA - Supply chain Levels for Software Artifacts (软件工件供应链级别)
SMI - Service Mesh Interface (服务网格接口)
SPIFFE - Secure Production Identity Framework For Everyone (安全生产身份框架)
SSO - Single Sign-On (单点登录)
TEE - Trusted Execution Environment (可信执行环境)
TLS - Transport Layer Security (传输层安全)
TPM - Trusted Platform Module (可信平台模块)
TSN - Time-Sensitive Networking (时间敏感网络)
VCS - Version Control System (版本控制系统)
VLAN - Virtual LAN (虚拟局域网)
VM - Virtual Machine (虚拟机)
VPA - Vertical Pod Autoscaler (垂直Pod自动扩缩)
VPN - Virtual Private Network (虚拟私有网络)
VXLAN - Virtual Extensible LAN (虚拟可扩展局域网)
Wasm - WebAssembly (Web汇编)
WASI - WebAssembly System Interface (WebAssembly系统接口)
XDP - eXpress Data Path (快速数据路径)
ZTA - Zero Trust Architecture (零信任架构)
```

---

## 版本历史 (Version History)

- **v2.0** (2025-10-19): 全面更新，新增1100+术语，涵盖边缘计算、AI/ML、安全等领域
- **v1.0** (2025-01-01): 初始版本，基础术语500+

---

## 贡献指南 (Contributing)

欢迎提交PR补充和完善术语表！

**联系方式**: [项目仓库地址]

---

**最后更新**: 2025-10-19  
**术语总数**: 1100+  
**覆盖领域**: 虚拟化、容器、编排、网络、存储、安全、监控、边缘计算、AI/ML、云原生、DevOps、标准协议

**Build Cloud Native, Speak the Same Language!** 🌐💬
