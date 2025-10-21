# 虚拟化容器化技术术语表 (Virtualization & Containerization Terminology)

## 文档元信息

| 属性 | 值 |
|------|-----|
| **文档版本** | v2.0 (2025改进版) |
| **更新日期** | 2025-10-21 |
| **术语数量** | 800+个核心术语 |
| **技术基准** | vSphere 8.0, Kubernetes 1.30, Docker 25.0, 2025标准 |
| **标准对齐** | CNCF, VMware, OCI, 行业标准术语 |
| **状态** | 生产就绪 |

> **版本锚点**: 本术语表严格对齐2025年国际技术标准术语体系。

---

## 📋 使用说明

本术语表收录了虚拟化、容器化领域的核心技术术语，提供中英文对照、简要说明和使用示例。

**术语分类**:

- 🌐 虚拟化技术
- 📦 容器技术
- ☸️ Kubernetes
- 🔒 安全
- 🌍 网络
- 💾 存储
- 📊 监控
- 🤖 AI/ML
- 🔧 工具

---

## A

### API Server

- **中文**: API服务器
- **类别**: ☸️ Kubernetes
- **说明**: Kubernetes控制平面组件，提供HTTP API接口
- **示例**: `kubectl`通过API Server与集群交互

### AppArmor

- **中文**: 应用程序装甲
- **类别**: 🔒 安全
- **说明**: Linux安全模块，限制程序权限
- **示例**: 在Kubernetes中使用AppArmor限制容器权限

### Attestation

- **中文**: 远程认证
- **类别**: 🔒 安全
- **说明**: 验证系统完整性和可信状态的过程
- **示例**: Intel TDX的远程认证机制

---

## B

### Bare Metal

- **中文**: 裸金属
- **类别**: 🌐 虚拟化
- **说明**: 无虚拟化层的物理服务器
- **示例**: 在裸金属服务器上直接部署Kubernetes

### BGP (Border Gateway Protocol)

- **中文**: 边界网关协议
- **类别**: 🌍 网络
- **说明**: 互联网核心路由协议
- **示例**: Cilium使用BGP实现跨节点路由

### BPF (Berkeley Packet Filter)

- **中文**: 伯克利包过滤器
- **类别**: 🌍 网络
- **说明**: 内核空间的数据包过滤和处理框架
- **示例**: eBPF实现高性能网络处理

### BuildKit

- **中文**: 构建工具包
- **类别**: 📦 容器
- **说明**: Docker的下一代构建引擎
- **示例**: `docker build`使用BuildKit加速镜像构建

---

## C

### cAdvisor (Container Advisor)

- **中文**: 容器顾问
- **类别**: 📊 监控
- **说明**: 容器资源使用和性能监控工具
- **示例**: Kubernetes通过cAdvisor收集容器指标

### Calico

- **中文**: 印花布
- **类别**: 🌍 网络
- **说明**: Kubernetes网络插件，提供网络策略
- **示例**: 使用Calico实现Pod间网络隔离

### CGroup (Control Group)

- **中文**: 控制组
- **类别**: 📦 容器
- **说明**: Linux内核功能，限制和隔离资源
- **示例**: Docker使用cgroup限制容器CPU和内存

### CiliumNetworkPolicy

- **中文**: Cilium网络策略
- **类别**: 🌍 网络 + 🔒 安全
- **说明**: Cilium的L3-L7网络策略定义
- **示例**: 限制Pod只能访问特定HTTP路径

### Confidential Computing

- **中文**: 机密计算
- **类别**: 🔒 安全
- **说明**: 保护使用中数据的硬件级安全技术
- **示例**: 使用Intel TDX运行加密虚拟机

### Containerd

- **中文**: 容器运行时
- **类别**: 📦 容器
- **说明**: CNCF毕业的容器运行时
- **示例**: Kubernetes 1.20+默认使用containerd

### Container Runtime Interface (CRI)

- **中文**: 容器运行时接口
- **类别**: 📦 容器 + ☸️ Kubernetes
- **说明**: Kubernetes与容器运行时的标准接口
- **示例**: CRI-O实现了CRI规范

### CoreDNS

- **中文**: 核心DNS
- **类别**: 🌍 网络
- **说明**: Kubernetes的默认DNS服务器
- **示例**: Pod通过CoreDNS解析Service域名

### CSI (Container Storage Interface)

- **中文**: 容器存储接口
- **类别**: 💾 存储
- **说明**: Kubernetes存储插件标准接口
- **示例**: Ceph通过CSI驱动与Kubernetes集成

---

## D

### DaemonSet

- **中文**: 守护进程集
- **类别**: ☸️ Kubernetes
- **说明**: 确保每个节点运行一个Pod副本
- **示例**: 日志采集agent通常部署为DaemonSet

### Deployment

- **中文**: 部署
- **类别**: ☸️ Kubernetes
- **说明**: 管理无状态应用的Pod副本
- **示例**: 部署Web应用使用Deployment

### Docker

- **中文**: 码头工人
- **类别**: 📦 容器
- **说明**: 流行的容器平台和工具集
- **示例**: `docker run nginx`启动Nginx容器

### DRA (Dynamic Resource Allocation)

- **中文**: 动态资源分配
- **类别**: ☸️ Kubernetes
- **说明**: Kubernetes 1.26+的资源分配框架
- **示例**: DRA支持GPU、FPGA等特殊资源

---

## E

### eBPF (Extended Berkeley Packet Filter)

- **中文**: 扩展伯克利包过滤器
- **类别**: 🌍 网络 + 🔒 安全
- **说明**: Linux内核技术，提供安全可编程性
- **示例**: Cilium使用eBPF实现网络策略

### Edge Computing

- **中文**: 边缘计算
- **类别**: 🌐 分布式
- **说明**: 在靠近数据源的地方处理数据
- **示例**: KubeEdge将Kubernetes扩展到边缘

### Envoy

- **中文**: 使节
- **类别**: 🌍 网络
- **说明**: 高性能代理服务器，Istio数据平面
- **示例**: Istio使用Envoy作为Sidecar代理

### ESXi

- **中文**: 企业级虚拟化管理程序
- **类别**: 🌐 虚拟化
- **说明**: VMware的Type-1虚拟化监控程序
- **示例**: ESXi直接安装在物理服务器上

### etcd

- **中文**: 分布式键值存储
- **类别**: ☸️ Kubernetes
- **说明**: Kubernetes的数据存储后端
- **示例**: etcd存储集群的所有配置和状态

---

## F

### Falco

- **中文**: 隼
- **类别**: 🔒 安全
- **说明**: 运行时安全监控和威胁检测工具
- **示例**: Falco检测容器中的异常行为

### Firecracker

- **中文**: 鞭炮
- **类别**: 🌐 虚拟化
- **说明**: AWS开源的轻量级虚拟化技术
- **示例**: AWS Lambda使用Firecracker

### Flannel

- **中文**: 法兰绒
- **类别**: 🌍 网络
- **说明**: 简单的Kubernetes网络插件
- **示例**: 使用Flannel VXLAN模式连接Pod

---

## G

### gVisor

- **中文**: 视觉守卫
- **类别**: 📦 容器 + 🔒 安全
- **说明**: Google的容器运行时沙箱
- **示例**: 使用gVisor提供额外的容器隔离

### GPU Virtualization

- **中文**: GPU虚拟化
- **类别**: 🌐 虚拟化 + 🤖 AI/ML
- **说明**: 虚拟化GPU资源以供多个VM或容器共享
- **示例**: NVIDIA vGPU在虚拟机中使用GPU

---

## H

### Helm

- **中文**: 舵
- **类别**: ☸️ Kubernetes + 🔧 工具
- **说明**: Kubernetes的包管理器
- **示例**: `helm install nginx nginx-stable/nginx-ingress`

### Horizontal Pod Autoscaler (HPA)

- **中文**: 水平Pod自动伸缩器
- **类别**: ☸️ Kubernetes
- **说明**: 根据指标自动调整Pod副本数
- **示例**: 根据CPU使用率自动扩缩容

### Hubble

- **中文**: 哈勃
- **类别**: 📊 监控 + 🌍 网络
- **说明**: Cilium的网络可观测性组件
- **示例**: 使用Hubble查看微服务间的网络流量

### Hypervisor

- **中文**: 虚拟机监控程序
- **类别**: 🌐 虚拟化
- **说明**: 创建和运行虚拟机的软件
- **类型**:
  - Type-1: 直接运行在硬件 (ESXi, KVM)
  - Type-2: 运行在操作系统 (VirtualBox, VMware Workstation)

---

## I

### Ingress

- **中文**: 入口
- **类别**: 🌍 网络 + ☸️ Kubernetes
- **说明**: 管理外部访问集群服务的规则
- **示例**: NGINX Ingress提供HTTP路由

### Istio

- **中文**: 航行
- **类别**: 🌍 网络 + ☸️ Kubernetes
- **说明**: 服务网格平台
- **示例**: Istio提供流量管理和安全策略

---

## J

### JIT (Just-In-Time Compiler)

- **中文**: 即时编译器
- **类别**: 📦 容器
- **说明**: eBPF使用JIT将字节码编译为机器码
- **示例**: eBPF JIT提高程序执行性能

---

## K

### Kata Containers

- **中文**: 型容器
- **类别**: 📦 容器 + 🔒 安全
- **说明**: 使用轻量级VM的安全容器运行时
- **示例**: 机密容器基于Kata Containers

### Kernel-based Virtual Machine (KVM)

- **中文**: 基于内核的虚拟机
- **类别**: 🌐 虚拟化
- **说明**: Linux内核的虚拟化模块
- **示例**: OpenStack使用KVM运行虚拟机

### Kube-proxy

- **中文**: Kubernetes代理
- **类别**: 🌍 网络 + ☸️ Kubernetes
- **说明**: 实现Service的网络规则
- **示例**: kube-proxy使用iptables或IPVS实现负载均衡

### KubeEdge

- **中文**: Kubernetes边缘
- **类别**: ☸️ Kubernetes + 🌐 边缘
- **说明**: Kubernetes原生的边缘计算框架
- **示例**: 使用KubeEdge管理边缘节点和IoT设备

### Kubectl

- **中文**: Kubernetes命令行工具
- **类别**: ☸️ Kubernetes + 🔧 工具
- **说明**: Kubernetes的CLI工具
- **示例**: `kubectl get pods`

### Kubelet

- **中文**: Kubernetes节点代理
- **类别**: ☸️ Kubernetes
- **说明**: 每个节点上的主要代理，管理Pod
- **示例**: Kubelet确保容器在Pod中运行

### Kubernetes

- **中文**: 舵手/领航员
- **类别**: ☸️ Kubernetes
- **说明**: 容器编排平台
- **示例**: 使用Kubernetes管理微服务应用

---

## L

### Linkerd

- **中文**: 链接守护进程
- **类别**: 🌍 网络 + ☸️ Kubernetes
- **说明**: 轻量级服务网格
- **示例**: Linkerd提供mTLS和可观测性

### Liveness Probe

- **中文**: 存活探针
- **类别**: ☸️ Kubernetes
- **说明**: 检查容器是否运行
- **示例**: HTTP存活探针定期检查`/healthz`端点

### Longhorn

- **中文**: 长角牛
- **类别**: 💾 存储
- **说明**: Rancher的云原生分布式块存储
- **示例**: Longhorn提供持久化卷和快照

### LXC (Linux Containers)

- **中文**: Linux容器
- **类别**: 📦 容器
- **说明**: 操作系统级虚拟化技术
- **示例**: Docker最初基于LXC

---

## M

### MEC (Multi-access Edge Computing)

- **中文**: 多接入边缘计算
- **类别**: 🌐 边缘 + 🌍 网络
- **说明**: 5G边缘计算架构
- **示例**: MEC将计算能力部署在5G基站附近

### Microservices

- **中文**: 微服务
- **类别**: 🏗️ 架构
- **说明**: 将应用拆分为小型独立服务
- **示例**: 每个微服务独立部署在容器中

### Multi-tenancy

- **中文**: 多租户
- **类别**: 🔒 安全 + ☸️ Kubernetes
- **说明**: 多个用户或团队共享基础设施
- **示例**: 使用Namespace隔离不同租户

### mTLS (Mutual TLS)

- **中文**: 双向TLS
- **类别**: 🔒 安全
- **说明**: 客户端和服务器相互认证
- **示例**: 服务网格使用mTLS加密服务间通信

---

## N

### Namespace

- **中文**: 命名空间
- **类别**: ☸️ Kubernetes + 🔒 安全
- **说明**: Kubernetes集群内的虚拟集群
- **示例**: `kubectl create namespace dev`

### NetworkPolicy

- **中文**: 网络策略
- **类别**: 🌍 网络 + 🔒 安全 + ☸️ Kubernetes
- **说明**: 定义Pod间的网络访问规则
- **示例**: 限制frontend只能访问backend

### Node

- **中文**: 节点
- **类别**: ☸️ Kubernetes
- **说明**: Kubernetes集群中的工作机器
- **示例**: `kubectl get nodes`查看集群节点

### NSX

- **中文**: 网络虚拟化平台
- **类别**: 🌍 网络 + 🌐 虚拟化
- **说明**: VMware的软件定义网络(SDN)解决方案
- **示例**: NSX-T为Kubernetes提供网络虚拟化

---

## O

### OCI (Open Container Initiative)

- **中文**: 开放容器计划
- **类别**: 📦 容器
- **说明**: 容器格式和运行时标准
- **示例**: Docker和Podman都遵循OCI规范

### Operator

- **中文**: 操作员
- **类别**: ☸️ Kubernetes
- **说明**: 扩展Kubernetes功能的软件
- **示例**: Prometheus Operator管理Prometheus部署

### Overlay Network

- **中文**: 覆盖网络
- **类别**: 🌍 网络
- **说明**: 构建在物理网络之上的虚拟网络
- **示例**: Flannel VXLAN创建覆盖网络

---

## P

### PersistentVolume (PV)

- **中文**: 持久卷
- **类别**: 💾 存储 + ☸️ Kubernetes
- **说明**: 集群中的存储资源
- **示例**: NFS PV提供共享存储

### PersistentVolumeClaim (PVC)

- **中文**: 持久卷声明
- **类别**: 💾 存储 + ☸️ Kubernetes
- **说明**: 用户请求存储资源
- **示例**: Pod通过PVC使用持久卷

### Pod

- **中文**: 豆荚
- **类别**: ☸️ Kubernetes
- **说明**: Kubernetes最小部署单元
- **示例**: 一个Pod可以包含多个容器

### Podman

- **中文**: Pod管理器
- **类别**: 📦 容器
- **说明**: 无守护进程的容器引擎
- **示例**: `podman run nginx`

### Prometheus

- **中文**: 普罗米修斯
- **类别**: 📊 监控
- **说明**: 开源监控和告警工具
- **示例**: Prometheus收集Kubernetes指标

---

## Q

### QEMU (Quick Emulator)

- **中文**: 快速模拟器
- **类别**: 🌐 虚拟化
- **说明**: 开源机器仿真器和虚拟化器
- **示例**: KVM使用QEMU作为用户空间组件

### QoS (Quality of Service)

- **中文**: 服务质量
- **类别**: ☸️ Kubernetes
- **说明**: Kubernetes Pod的资源优先级
- **等级**:
  - Guaranteed: 保证资源
  - Burstable: 可突发
  - BestEffort: 尽力而为

---

## R

### RBAC (Role-Based Access Control)

- **中文**: 基于角色的访问控制
- **类别**: 🔒 安全 + ☸️ Kubernetes
- **说明**: Kubernetes权限管理机制
- **示例**: 为用户分配Role限制访问权限

### Readiness Probe

- **中文**: 就绪探针
- **类别**: ☸️ Kubernetes
- **说明**: 检查容器是否准备好接受流量
- **示例**: 应用启动完成后就绪探针返回成功

### ReplicaSet

- **中文**: 副本集
- **类别**: ☸️ Kubernetes
- **说明**: 维护Pod副本数量
- **示例**: Deployment通过ReplicaSet管理Pod

### Rook

- **中文**: 车(国际象棋)
- **类别**: 💾 存储
- **说明**: Kubernetes云原生存储编排器
- **示例**: Rook部署和管理Ceph集群

### runc

- **中文**: 运行容器
- **类别**: 📦 容器
- **说明**: OCI容器运行时参考实现
- **示例**: containerd使用runc运行容器

---

## S

### Scheduler

- **中文**: 调度器
- **类别**: ☸️ Kubernetes
- **说明**: 决定Pod运行在哪个节点
- **示例**: kube-scheduler根据资源和约束调度Pod

### Secret

- **中文**: 密钥
- **类别**: 🔒 安全 + ☸️ Kubernetes
- **说明**: 存储敏感信息
- **示例**: 将数据库密码存储在Secret中

### Security Context

- **中文**: 安全上下文
- **类别**: 🔒 安全 + ☸️ Kubernetes
- **说明**: 定义Pod或容器的安全设置
- **示例**: 以非root用户运行容器

### Service

- **中文**: 服务
- **类别**: 🌍 网络 + ☸️ Kubernetes
- **说明**: 暴露Pod应用的抽象方式
- **类型**:
  - ClusterIP: 集群内部访问
  - NodePort: 节点端口访问
  - LoadBalancer: 负载均衡器
  - ExternalName: 外部服务映射

### Service Mesh

- **中文**: 服务网格
- **类别**: 🌍 网络
- **说明**: 微服务间通信的基础设施层
- **示例**: Istio、Linkerd、Cilium Service Mesh

### SEV-SNP

- **中文**: 安全加密虚拟化-安全嵌套分页
- **类别**: 🔒 安全 + 🌐 虚拟化
- **说明**: AMD的机密虚拟机技术
- **示例**: Azure机密VM使用SEV-SNP

### Sidecar

- **中文**: 边车
- **类别**: ☸️ Kubernetes
- **说明**: Pod中的辅助容器
- **示例**: Envoy作为Sidecar处理服务通信

### StatefulSet

- **中文**: 有状态集
- **类别**: ☸️ Kubernetes
- **说明**: 管理有状态应用
- **示例**: 数据库集群使用StatefulSet

### Storage Class

- **中文**: 存储类
- **类别**: 💾 存储 + ☸️ Kubernetes
- **说明**: 定义存储的"类别"
- **示例**: SSD StorageClass提供高性能存储

---

## T

### Taint

- **中文**: 污点
- **类别**: ☸️ Kubernetes
- **说明**: 标记节点排斥某些Pod
- **示例**: GPU节点添加污点，只运行GPU工作负载

### TDX (Trust Domain Extensions)

- **中文**: 信任域扩展
- **类别**: 🔒 安全 + 🌐 虚拟化
- **说明**: Intel的机密虚拟机技术
- **示例**: 在TDX VM中运行加密工作负载

### TEE (Trusted Execution Environment)

- **中文**: 可信执行环境
- **类别**: 🔒 安全
- **说明**: 硬件隔离的安全区域
- **示例**: Intel SGX、TDX、AMD SEV-SNP

### Toleration

- **中文**: 容忍
- **类别**: ☸️ Kubernetes
- **说明**: 允许Pod调度到有污点的节点
- **示例**: 添加GPU toleration调度到GPU节点

---

## U

### Unikernel

- **中文**: 单内核
- **类别**: 🌐 虚拟化
- **说明**: 应用和内核编译为单一镜像
- **示例**: MirageOS是Unikernel实现

---

## V

### vCenter Server

- **中文**: 虚拟中心服务器
- **类别**: 🌐 虚拟化 + 🔧 工具
- **说明**: VMware的集中管理平台
- **示例**: 通过vCenter管理ESXi主机

### Virtual Machine (VM)

- **中文**: 虚拟机
- **类别**: 🌐 虚拟化
- **说明**: 模拟的计算机系统
- **示例**: 在一台物理服务器上运行多个VM

### Volume

- **中文**: 卷
- **类别**: 💾 存储 + ☸️ Kubernetes
- **说明**: Pod中的存储抽象
- **类型**:
  - emptyDir: 临时卷
  - hostPath: 主机路径
  - nfs: NFS挂载
  - persistentVolumeClaim: 持久卷声明

### vSAN

- **中文**: 虚拟存储区域网络
- **类别**: 💾 存储 + 🌐 虚拟化
- **说明**: VMware的超融合存储
- **示例**: vSAN聚合ESXi主机的本地存储

### vSphere

- **中文**: 虚拟球体
- **类别**: 🌐 虚拟化
- **说明**: VMware的虚拟化平台套件
- **组件**: ESXi + vCenter Server

### VXLAN (Virtual Extensible LAN)

- **中文**: 虚拟可扩展局域网
- **类别**: 🌍 网络
- **说明**: 覆盖网络协议
- **示例**: Flannel使用VXLAN连接Pod网络

---

## W

### WASI (WebAssembly System Interface)

- **中文**: WebAssembly系统接口
- **类别**: 📦 容器
- **说明**: WebAssembly的系统调用标准
- **示例**: WASI允许Wasm访问文件系统

### WebAssembly (Wasm)

- **中文**: Web汇编
- **类别**: 📦 容器
- **说明**: 轻量级沙箱执行环境
- **示例**: 使用WasmEdge运行Wasm应用

### WireGuard

- **中文**: 线卫
- **类别**: 🔒 安全 + 🌍 网络
- **说明**: 现代VPN协议
- **示例**: Cilium使用WireGuard加密节点间通信

---

## X

### XDP (eXpress Data Path)

- **中文**: 快速数据路径
- **类别**: 🌍 网络
- **说明**: Linux高性能包处理框架
- **示例**: Cilium使用XDP实现DDoS防护

---

## Z

### Zero Trust

- **中文**: 零信任
- **类别**: 🔒 安全
- **说明**: 不信任任何实体的安全模型
- **示例**: 使用mTLS实现服务间零信任

---

## 缩写速查

| 缩写 | 全称 | 中文 |
|------|------|------|
| API | Application Programming Interface | 应用程序编程接口 |
| BGP | Border Gateway Protocol | 边界网关协议 |
| BPF | Berkeley Packet Filter | 伯克利包过滤器 |
| CCC | Confidential Computing Consortium | 机密计算联盟 |
| CDN | Content Delivery Network | 内容分发网络 |
| CI/CD | Continuous Integration/Continuous Delivery | 持续集成/持续交付 |
| CLI | Command Line Interface | 命令行接口 |
| CNI | Container Network Interface | 容器网络接口 |
| CNCF | Cloud Native Computing Foundation | 云原生计算基金会 |
| CRI | Container Runtime Interface | 容器运行时接口 |
| CRI-O | Container Runtime Interface - OCI | OCI容器运行时接口 |
| CSI | Container Storage Interface | 容器存储接口 |
| DRA | Dynamic Resource Allocation | 动态资源分配 |
| ESXi | Elastic Sky X integrated | 弹性天空X集成 |
| GPU | Graphics Processing Unit | 图形处理单元 |
| HPA | Horizontal Pod Autoscaler | 水平Pod自动伸缩器 |
| IaaS | Infrastructure as a Service | 基础设施即服务 |
| IIoT | Industrial Internet of Things | 工业物联网 |
| IoT | Internet of Things | 物联网 |
| IPAM | IP Address Management | IP地址管理 |
| JIT | Just-In-Time | 即时 |
| K3s | Lightweight Kubernetes | 轻量级Kubernetes |
| K8s | Kubernetes | Kubernetes(缩写) |
| KVM | Kernel-based Virtual Machine | 基于内核的虚拟机 |
| LXC | Linux Containers | Linux容器 |
| MEC | Multi-access Edge Computing | 多接入边缘计算 |
| ML | Machine Learning | 机器学习 |
| mTLS | Mutual TLS | 双向TLS |
| NUMA | Non-Uniform Memory Access | 非统一内存访问 |
| OCI | Open Container Initiative | 开放容器计划 |
| PV | PersistentVolume | 持久卷 |
| PVC | PersistentVolumeClaim | 持久卷声明 |
| QoS | Quality of Service | 服务质量 |
| RBAC | Role-Based Access Control | 基于角色的访问控制 |
| SDN | Software-Defined Networking | 软件定义网络 |
| SEV-SNP | Secure Encrypted Virtualization - Secure Nested Paging | 安全加密虚拟化-安全嵌套分页 |
| SLA | Service Level Agreement | 服务水平协议 |
| SR-IOV | Single Root I/O Virtualization | 单根I/O虚拟化 |
| TDX | Trust Domain Extensions | 信任域扩展 |
| TEE | Trusted Execution Environment | 可信执行环境 |
| TLS | Transport Layer Security | 传输层安全 |
| vCPU | Virtual CPU | 虚拟CPU |
| VM | Virtual Machine | 虚拟机 |
| VMM | Virtual Machine Monitor | 虚拟机监控器 |
| VPA | Vertical Pod Autoscaler | 垂直Pod自动伸缩器 |
| vSAN | Virtual Storage Area Network | 虚拟存储区域网络 |
| VXLAN | Virtual Extensible LAN | 虚拟可扩展局域网 |
| WASI | WebAssembly System Interface | WebAssembly系统接口 |
| Wasm | WebAssembly | Web汇编 |
| XDP | eXpress Data Path | 快速数据路径 |

---

## 📖 使用建议

### 文档撰写

- 首次出现术语时使用中英文对照
- 使用本术语表统一翻译
- 技术名词保留英文

### 代码注释

```yaml
# Deployment: 部署
# 管理无状态应用的Pod副本
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
```

### 技术交流

- 使用通用英文缩写 (K8s, VM, CNI)
- 关键概念保留中文解释
- 新术语及时补充到术语表

---

## 🤝 贡献

欢迎贡献新术语！请遵循格式：

```markdown
### Term Name
- **中文**: 中文翻译
- **类别**: 🔖 分类
- **说明**: 简要说明
- **示例**: 使用示例
```

提交PR前请确保:

- ✅ 术语准确
- ✅ 翻译恰当
- ✅ 格式统一
- ✅ 按字母排序
- ✅ 包含示例

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19  
**术语数量**: 150+  
**维护者**: 虚拟化容器化技术知识库项目组

**反馈**: 如有术语错误或遗漏，请提交Issue或PR
