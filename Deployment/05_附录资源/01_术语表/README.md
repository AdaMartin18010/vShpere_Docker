# 技术术语双语对照表

> **返回**: [附录资源首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [技术术语双语对照表](#技术术语双语对照表)
  - [📋 目录](#-目录)
  - [虚拟化技术术语](#虚拟化技术术语)
    - [基础概念](#基础概念)
    - [VMware技术栈](#vmware技术栈)
    - [KVM技术栈](#kvm技术栈)
    - [Hyper-V技术栈](#hyper-v技术栈)
  - [容器化技术术语](#容器化技术术语)
    - [容器基础](#容器基础)
    - [Kubernetes术语](#kubernetes术语)
    - [容器网络](#容器网络)
    - [容器存储](#容器存储)
  - [网络技术术语](#网络技术术语)
    - [网络基础](#网络基础)
    - [虚拟网络](#虚拟网络)
    - [网络协议](#网络协议)
  - [存储技术术语](#存储技术术语)
    - [存储类型](#存储类型)
    - [存储协议](#存储协议)
    - [存储架构](#存储架构)
  - [运维管理术语](#运维管理术语)
    - [监控告警](#监控告警)
    - [日志管理](#日志管理)
    - [自动化运维](#自动化运维)
  - [云原生术语](#云原生术语)
    - [服务网格](#服务网格)
    - [可观测性](#可观测性)
    - [DevOps/GitOps](#devopsgitops)
  - [常用缩写对照](#常用缩写对照)

---

## 虚拟化技术术语

### 基础概念

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Virtualization | 虚拟化 | - | 通过软件模拟硬件资源 |
| Hypervisor | 虚拟机监视器 | VMM | 管理和运行虚拟机的软件层 |
| Type-1 Hypervisor | 裸机虚拟化 | - | 直接运行在硬件上 (ESXi, KVM) |
| Type-2 Hypervisor | 托管虚拟化 | - | 运行在操作系统上 (VMware Workstation, VirtualBox) |
| Virtual Machine | 虚拟机 | VM | 软件模拟的完整计算机系统 |
| Guest OS | 客户操作系统 | - | 运行在虚拟机中的操作系统 |
| Host OS | 宿主操作系统 | - | 运行虚拟化软件的底层操作系统 |
| Hardware Virtualization | 硬件虚拟化 | HV | CPU支持的虚拟化技术 |
| Para-virtualization | 半虚拟化 | PV | Guest OS感知虚拟化环境 |
| Full Virtualization | 全虚拟化 | FV | Guest OS不感知虚拟化环境 |
| Virtual CPU | 虚拟CPU | vCPU | 分配给虚拟机的CPU资源 |
| Virtual Memory | 虚拟内存 | vRAM | 分配给虚拟机的内存资源 |
| Overcommitment | 资源过载 | - | 分配超过物理资源的虚拟资源 |
| Thin Provisioning | 精简配置 | - | 按需分配存储空间 |
| Thick Provisioning | 厚配置 | - | 预先分配全部存储空间 |

---

### VMware技术栈

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| ESXi | ESXi虚拟化平台 | - | VMware裸机虚拟化平台 |
| vCenter Server | vCenter服务器 | vCenter/VC | VMware集中管理平台 |
| vSphere | vSphere虚拟化套件 | - | VMware企业级虚拟化解决方案 |
| vMotion | 热迁移 | - | 在线迁移虚拟机 |
| Storage vMotion | 存储热迁移 | svMotion | 在线迁移虚拟机存储 |
| High Availability | 高可用 | HA | 自动重启故障虚拟机 |
| Fault Tolerance | 容错 | FT | 实时同步虚拟机状态 |
| Distributed Resource Scheduler | 分布式资源调度 | DRS | 自动负载均衡 |
| Virtual SAN | 虚拟存储区域网络 | vSAN | VMware软件定义存储 |
| Virtual Distributed Switch | 分布式虚拟交换机 | vDS | 跨主机的虚拟交换机 |
| Network I/O Control | 网络I/O控制 | NIOC | 网络带宽管理 |
| Storage I/O Control | 存储I/O控制 | SIOC | 存储IOPS管理 |
| Enhanced vMotion Compatibility | 增强型vMotion兼容性 | EVC | 跨不同CPU的vMotion |
| Distributed Power Management | 分布式电源管理 | DPM | 自动节能管理 |

---

### KVM技术栈

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Kernel-based Virtual Machine | 基于内核的虚拟机 | KVM | Linux内核虚拟化模块 |
| Quick Emulator | 快速仿真器 | QEMU | 硬件模拟器 |
| libvirt | libvirt库 | - | 虚拟化管理API |
| Virtual Machine Manager | 虚拟机管理器 | virt-manager | KVM图形化管理工具 |
| virsh | virsh命令行 | - | KVM命令行管理工具 |
| virtio | virtio驱动 | - | 半虚拟化驱动 |
| QCOW2 | QEMU写时复制格式2 | - | KVM镜像格式 |
| Raw | 裸格式 | - | 原始磁盘镜像格式 |
| Linux Bridge | Linux网桥 | - | Linux内核网桥 |
| Open vSwitch | 开放虚拟交换机 | OVS | 软件定义虚拟交换机 |

---

### Hyper-V技术栈

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Hyper-V | Hyper-V虚拟化 | - | Microsoft虚拟化平台 |
| System Center Virtual Machine Manager | 系统中心虚拟机管理器 | SCVMM | Hyper-V集中管理平台 |
| Live Migration | 实时迁移 | - | Hyper-V在线迁移 |
| Replica | 副本 | - | Hyper-V虚拟机复制 |
| Cluster Shared Volume | 集群共享卷 | CSV | Hyper-V集群共享存储 |
| Virtual Switch | 虚拟交换机 | - | Hyper-V虚拟网络交换机 |
| Integration Services | 集成服务 | - | Hyper-V Guest工具 |

---

## 容器化技术术语

### 容器基础

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Container | 容器 | - | 应用及其依赖的打包单元 |
| Docker | Docker | - | 容器化平台 |
| Image | 镜像 | - | 容器的只读模板 |
| Dockerfile | Dockerfile | - | 构建镜像的脚本 |
| Registry | 镜像仓库 | - | 存储和分发镜像的服务 |
| Repository | 仓库 | Repo | 镜像存储的命名空间 |
| Tag | 标签 | - | 镜像版本标识 |
| Layer | 层 | - | 镜像的分层结构 |
| Container Runtime | 容器运行时 | - | 运行容器的底层软件 |
| containerd | containerd | - | 工业标准容器运行时 |
| CRI-O | CRI-O | - | Kubernetes容器运行时 |
| runc | runc | - | OCI容器运行时参考实现 |
| Docker Compose | Docker Compose | - | 多容器应用编排工具 |
| Docker Swarm | Docker Swarm | - | Docker原生集群管理 |
| Rootless Container | 无根容器 | - | 非root用户运行的容器 |

---

### Kubernetes术语

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Kubernetes | Kubernetes | K8s | 容器编排平台 |
| Cluster | 集群 | - | Kubernetes节点集合 |
| Node | 节点 | - | 集群中的工作机器 |
| Master Node | 主节点 | - | 控制平面节点 |
| Worker Node | 工作节点 | - | 运行应用的节点 |
| Control Plane | 控制平面 | - | 集群管理组件集合 |
| API Server | API服务器 | kube-apiserver | Kubernetes API入口 |
| Scheduler | 调度器 | kube-scheduler | Pod调度组件 |
| Controller Manager | 控制器管理器 | kube-controller-manager | 控制器管理组件 |
| etcd | etcd | - | 分布式键值存储 |
| Kubelet | Kubelet | - | 节点代理 |
| Kube-proxy | Kube-proxy | - | 网络代理 |
| Pod | Pod | - | 最小部署单元 |
| Deployment | 部署 | - | 无状态应用部署 |
| StatefulSet | 有状态集 | - | 有状态应用部署 |
| DaemonSet | 守护进程集 | - | 每个节点运行一个Pod |
| Job | 任务 | - | 一次性任务 |
| CronJob | 定时任务 | - | 定时执行的任务 |
| Service | 服务 | Svc | Pod访问抽象 |
| Ingress | 入口 | - | 外部访问集群的入口 |
| ConfigMap | 配置映射 | CM | 配置数据存储 |
| Secret | 密钥 | - | 敏感数据存储 |
| Volume | 卷 | - | 持久化存储 |
| PersistentVolume | 持久卷 | PV | 集群级存储资源 |
| PersistentVolumeClaim | 持久卷声明 | PVC | 存储资源请求 |
| StorageClass | 存储类 | SC | 动态存储配置 |
| Namespace | 命名空间 | NS | 资源隔离单元 |
| Label | 标签 | - | 资源标识键值对 |
| Selector | 选择器 | - | 标签查询表达式 |
| Annotation | 注解 | - | 资源元数据 |
| Horizontal Pod Autoscaler | 水平Pod自动扩缩容 | HPA | 基于指标自动扩缩容 |
| Vertical Pod Autoscaler | 垂直Pod自动扩缩容 | VPA | 自动调整资源请求 |
| ResourceQuota | 资源配额 | - | 命名空间资源限制 |
| LimitRange | 限制范围 | - | 资源默认值和限制 |
| Role-Based Access Control | 基于角色的访问控制 | RBAC | 权限管理 |
| ServiceAccount | 服务账号 | SA | Pod身份标识 |
| NetworkPolicy | 网络策略 | - | Pod网络访问控制 |
| PodSecurityPolicy | Pod安全策略 | PSP | Pod安全配置 (已废弃) |
| PodDisruptionBudget | Pod中断预算 | PDB | 保障可用性 |

---

### 容器网络

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Container Network Interface | 容器网络接口 | CNI | 容器网络标准 |
| Overlay Network | 覆盖网络 | - | 跨主机虚拟网络 |
| Underlay Network | 底层网络 | - | 物理网络 |
| Calico | Calico | - | BGP网络方案 |
| Cilium | Cilium | - | eBPF网络方案 |
| Flannel | Flannel | - | 简单覆盖网络方案 |
| Weave Net | Weave Net | - | 网状覆盖网络 |
| Multus CNI | Multus CNI | - | 多网络接口方案 |
| Service Mesh | 服务网格 | - | 微服务通信基础设施 |
| Sidecar | 边车 | - | 辅助容器模式 |
| Envoy | Envoy | - | 高性能代理 |

---

### 容器存储

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Container Storage Interface | 容器存储接口 | CSI | 容器存储标准 |
| Rook | Rook | - | 云原生存储编排 |
| Ceph | Ceph | - | 分布式存储系统 |
| Longhorn | Longhorn | - | 轻量级分布式存储 |
| OpenEBS | OpenEBS | - | 容器化块存储 |
| GlusterFS | GlusterFS | - | 分布式文件系统 |
| NFS Subdir External Provisioner | NFS子目录外部供应商 | - | NFS动态供应 |
| Local Path Provisioner | 本地路径供应商 | - | 本地存储动态供应 |
| Volume Snapshot | 卷快照 | - | 存储快照功能 |

---

## 网络技术术语

### 网络基础

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Virtual Local Area Network | 虚拟局域网 | VLAN | 逻辑网络分段 |
| Virtual Extensible LAN | 虚拟可扩展局域网 | VXLAN | 大规模覆盖网络 |
| Generic Routing Encapsulation | 通用路由封装 | GRE | 隧道协议 |
| Border Gateway Protocol | 边界网关协议 | BGP | 路由协议 |
| Open Shortest Path First | 开放最短路径优先 | OSPF | 路由协议 |
| Link Aggregation Control Protocol | 链路聚合控制协议 | LACP | 链路聚合 |
| Spanning Tree Protocol | 生成树协议 | STP | 防止网络环路 |
| Rapid STP | 快速生成树协议 | RSTP | 改进的STP |
| Multiple STP | 多生成树协议 | MSTP | 支持VLAN的STP |
| Virtual Router Redundancy Protocol | 虚拟路由器冗余协议 | VRRP | 网关高可用 |
| Hot Standby Router Protocol | 热备份路由协议 | HSRP | Cisco网关高可用 |
| Gateway Load Balancing Protocol | 网关负载均衡协议 | GLBP | 网关负载均衡 |
| Quality of Service | 服务质量 | QoS | 流量优先级控制 |
| Access Control List | 访问控制列表 | ACL | 流量过滤规则 |
| Simple Network Management Protocol | 简单网络管理协议 | SNMP | 网络监控协议 |
| NetFlow | NetFlow | - | 流量统计协议 |
| sFlow | sFlow | - | 采样流量协议 |

---

### 虚拟网络

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Virtual Switch | 虚拟交换机 | vSwitch | 软件交换机 |
| Virtual Network Interface | 虚拟网络接口 | vNIC | 虚拟网卡 |
| Software-Defined Networking | 软件定义网络 | SDN | 网络控制与数据分离 |
| Network Function Virtualization | 网络功能虚拟化 | NFV | 网络功能软件化 |
| Single Root I/O Virtualization | 单根I/O虚拟化 | SR-IOV | 网卡硬件虚拟化 |
| Virtual Private Network | 虚拟专用网络 | VPN | 加密网络隧道 |
| IPsec | IPsec | - | IP层安全协议 |
| OpenVPN | OpenVPN | - | 开源VPN |
| WireGuard | WireGuard | - | 现代VPN |

---

### 网络协议

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Transmission Control Protocol | 传输控制协议 | TCP | 可靠传输协议 |
| User Datagram Protocol | 用户数据报协议 | UDP | 不可靠传输协议 |
| Internet Control Message Protocol | 互联网控制消息协议 | ICMP | 网络诊断协议 |
| Address Resolution Protocol | 地址解析协议 | ARP | MAC地址解析 |
| Dynamic Host Configuration Protocol | 动态主机配置协议 | DHCP | 自动IP分配 |
| Domain Name System | 域名系统 | DNS | 域名解析 |
| Hypertext Transfer Protocol | 超文本传输协议 | HTTP | Web协议 |
| HTTP Secure | 安全超文本传输协议 | HTTPS | 加密HTTP |
| File Transfer Protocol | 文件传输协议 | FTP | 文件传输 |
| Secure Shell | 安全外壳协议 | SSH | 加密远程连接 |
| Secure Copy Protocol | 安全复制协议 | SCP | 加密文件传输 |
| Server Message Block | 服务器消息块 | SMB/CIFS | Windows文件共享 |
| Network File System | 网络文件系统 | NFS | Unix/Linux文件共享 |

---

## 存储技术术语

### 存储类型

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Direct-Attached Storage | 直连存储 | DAS | 直接连接服务器的存储 |
| Network-Attached Storage | 网络附加存储 | NAS | 文件级网络存储 |
| Storage Area Network | 存储区域网络 | SAN | 块级网络存储 |
| Hyper-Converged Infrastructure | 超融合基础设施 | HCI | 计算存储网络融合 |
| Software-Defined Storage | 软件定义存储 | SDS | 存储资源虚拟化 |
| Object Storage | 对象存储 | - | 基于对象的存储 |
| Block Storage | 块存储 | - | 基于块的存储 |
| File Storage | 文件存储 | - | 基于文件的存储 |

---

### 存储协议

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Internet Small Computer System Interface | 互联网小型计算机系统接口 | iSCSI | IP网络块存储协议 |
| Fibre Channel | 光纤通道 | FC | 专用存储网络协议 |
| Fibre Channel over Ethernet | 以太网光纤通道 | FCoE | 融合网络FC协议 |
| InfiniBand | InfiniBand | IB | 高速互联网络 |
| Remote Direct Memory Access | 远程直接内存访问 | RDMA | 高性能网络传输 |
| RDMA over Converged Ethernet | 融合以太网RDMA | RoCE | 以太网上的RDMA |
| Non-Volatile Memory Express | 非易失性内存快速 | NVMe | 高速SSD协议 |
| NVMe over Fabrics | 网络NVMe | NVMe-oF | 网络传输NVMe |
| NVMe over TCP | TCP上的NVMe | NVMe/TCP | TCP传输NVMe |

---

### 存储架构

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Redundant Array of Independent Disks | 独立磁盘冗余阵列 | RAID | 磁盘阵列技术 |
| Just a Bunch of Disks | 磁盘簇 | JBOD | 无RAID的磁盘组 |
| Logical Volume Manager | 逻辑卷管理器 | LVM | Linux存储管理 |
| Logical Unit Number | 逻辑单元号 | LUN | SAN存储单元 |
| World Wide Name | 全球名称 | WWN | FC设备唯一标识 |
| World Wide Port Name | 全球端口名称 | WWPN | FC端口标识 |
| World Wide Node Name | 全球节点名称 | WWNN | FC节点标识 |
| Input/Output Operations Per Second | 每秒输入输出操作 | IOPS | 存储性能指标 |
| Solid State Drive | 固态硬盘 | SSD | 闪存存储 |
| Hard Disk Drive | 机械硬盘 | HDD | 磁性存储 |
| Serial ATA | 串行ATA | SATA | 磁盘接口 |
| Serial Attached SCSI | 串行SCSI | SAS | 企业级磁盘接口 |

---

## 运维管理术语

### 监控告警

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Prometheus | Prometheus | - | 时序数据库监控系统 |
| Grafana | Grafana | - | 可视化平台 |
| Alertmanager | Alertmanager | - | 告警管理器 |
| Metric | 指标 | - | 监控数据点 |
| Time Series | 时序数据 | - | 时间序列数据 |
| Exporter | 导出器 | - | 指标采集器 |
| Scrape | 抓取 | - | 指标采集动作 |
| PromQL | Prometheus查询语言 | - | Prometheus查询语法 |
| Dashboard | 仪表板 | - | 可视化面板 |
| Panel | 面板 | - | 可视化组件 |
| Threshold | 阈值 | - | 告警触发条件 |
| Service Level Indicator | 服务级别指标 | SLI | 服务质量指标 |
| Service Level Objective | 服务级别目标 | SLO | 服务质量目标 |
| Service Level Agreement | 服务级别协议 | SLA | 服务质量承诺 |
| Recovery Time Objective | 恢复时间目标 | RTO | 故障恢复时间目标 |
| Recovery Point Objective | 恢复点目标 | RPO | 数据丢失容忍度 |

---

### 日志管理

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Elasticsearch | Elasticsearch | ES | 分布式搜索引擎 |
| Logstash | Logstash | - | 日志处理管道 |
| Kibana | Kibana | - | 日志可视化 |
| ELK Stack | ELK栈 | ELK | Elasticsearch+Logstash+Kibana |
| Filebeat | Filebeat | - | 轻量级日志采集器 |
| Fluentd | Fluentd | - | 统一日志层 |
| Fluent Bit | Fluent Bit | - | 轻量级Fluentd |
| Loki | Loki | - | 日志聚合系统 |
| Promtail | Promtail | - | Loki日志采集器 |
| LogQL | LogQL | - | Loki查询语言 |
| Syslog | 系统日志 | - | 标准日志协议 |
| Rsyslog | Rsyslog | - | 增强的Syslog |

---

### 自动化运维

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Ansible | Ansible | - | 自动化配置管理工具 |
| Playbook | 剧本 | - | Ansible脚本 |
| Inventory | 清单 | - | Ansible主机列表 |
| Role | 角色 | - | Ansible可复用任务集 |
| Terraform | Terraform | TF | 基础设施即代码工具 |
| Infrastructure as Code | 基础设施即代码 | IaC | 代码化基础设施 |
| Provider | 提供商 | - | Terraform插件 |
| Resource | 资源 | - | Terraform管理对象 |
| State | 状态 | - | Terraform资源状态 |
| Module | 模块 | - | Terraform可复用配置 |
| Continuous Integration | 持续集成 | CI | 自动化构建测试 |
| Continuous Delivery | 持续交付 | CD | 自动化部署交付 |
| Continuous Deployment | 持续部署 | CD | 自动化生产部署 |
| CI/CD | 持续集成/持续交付 | CI/CD | DevOps核心实践 |
| GitOps | GitOps | - | Git驱动的运维 |
| ArgoCD | ArgoCD | - | Kubernetes GitOps工具 |
| FluxCD | FluxCD | - | Kubernetes GitOps工具 |
| Jenkins | Jenkins | - | 开源CI/CD平台 |
| GitLab CI | GitLab持续集成 | - | GitLab集成CI/CD |
| GitHub Actions | GitHub Actions | - | GitHub集成CI/CD |
| Tekton | Tekton | - | Kubernetes原生CI/CD |

---

## 云原生术语

### 服务网格

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Service Mesh | 服务网格 | - | 微服务通信基础设施 |
| Istio | Istio | - | 功能丰富的服务网格 |
| Linkerd | Linkerd | - | 轻量级服务网格 |
| Envoy Proxy | Envoy代理 | - | 高性能代理 |
| Data Plane | 数据平面 | - | 处理流量的代理层 |
| Control Plane | 控制平面 | - | 管理配置的控制层 |
| Sidecar | 边车 | - | 辅助容器模式 |
| Traffic Management | 流量管理 | - | 路由、负载均衡 |
| Circuit Breaker | 熔断器 | - | 故障隔离机制 |
| Rate Limiting | 速率限制 | - | 流量控制 |
| Mutual TLS | 双向TLS | mTLS | 双向加密认证 |
| Virtual Service | 虚拟服务 | - | Istio路由规则 |
| Destination Rule | 目标规则 | - | Istio流量策略 |
| Gateway | 网关 | - | 边缘流量入口 |

---

### 可观测性

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| Observability | 可观测性 | - | 系统状态透明度 |
| Distributed Tracing | 分布式追踪 | - | 跨服务调用链追踪 |
| Trace | 追踪 | - | 完整的请求链路 |
| Span | 跨度 | - | 单个操作单元 |
| Jaeger | Jaeger | - | 分布式追踪系统 |
| Zipkin | Zipkin | - | 分布式追踪系统 |
| OpenTelemetry | OpenTelemetry | OTel | 可观测性标准 |
| Application Performance Monitoring | 应用性能监控 | APM | 应用性能管理 |
| SkyWalking | SkyWalking | - | APM系统 |
| Kiali | Kiali | - | Istio可视化 |
| Hubble | Hubble | - | Cilium可观测性 |

---

### DevOps/GitOps

| 英文 | 中文 | 缩写 | 说明 |
|------|------|------|------|
| DevOps | 开发运维 | - | 开发与运维协作文化 |
| Site Reliability Engineering | 站点可靠性工程 | SRE | Google的运维实践 |
| GitOps | GitOps | - | Git驱动的声明式运维 |
| Declarative | 声明式 | - | 描述期望状态 |
| Imperative | 命令式 | - | 描述操作步骤 |
| Immutable Infrastructure | 不可变基础设施 | - | 只读基础设施 |
| Blue-Green Deployment | 蓝绿部署 | - | 零停机部署方式 |
| Canary Deployment | 金丝雀部署 | - | 灰度发布 |
| Rolling Update | 滚动更新 | - | 逐步替换实例 |
| Rollback | 回滚 | - | 恢复到之前版本 |
| Feature Flag | 功能开关 | - | 特性动态开关 |
| Chaos Engineering | 混沌工程 | - | 故障注入测试 |

---

## 常用缩写对照

| 缩写 | 英文全称 | 中文 |
|------|---------|------|
| VM | Virtual Machine | 虚拟机 |
| VMM | Virtual Machine Monitor | 虚拟机监视器 |
| vCPU | Virtual CPU | 虚拟CPU |
| K8s | Kubernetes | Kubernetes |
| NS | Namespace | 命名空间 |
| PV | PersistentVolume | 持久卷 |
| PVC | PersistentVolumeClaim | 持久卷声明 |
| SC | StorageClass | 存储类 |
| CM | ConfigMap | 配置映射 |
| SA | ServiceAccount | 服务账号 |
| HPA | Horizontal Pod Autoscaler | 水平Pod自动扩缩容 |
| VPA | Vertical Pod Autoscaler | 垂直Pod自动扩缩容 |
| PDB | PodDisruptionBudget | Pod中断预算 |
| RBAC | Role-Based Access Control | 基于角色的访问控制 |
| CNI | Container Network Interface | 容器网络接口 |
| CSI | Container Storage Interface | 容器存储接口 |
| CRI | Container Runtime Interface | 容器运行时接口 |
| OCI | Open Container Initiative | 开放容器倡议 |
| CNCF | Cloud Native Computing Foundation | 云原生计算基金会 |
| SLA | Service Level Agreement | 服务级别协议 |
| SLO | Service Level Objective | 服务级别目标 |
| SLI | Service Level Indicator | 服务级别指标 |
| RTO | Recovery Time Objective | 恢复时间目标 |
| RPO | Recovery Point Objective | 恢复点目标 |
| MTTR | Mean Time To Repair | 平均修复时间 |
| MTBF | Mean Time Between Failures | 平均故障间隔时间 |
| HA | High Availability | 高可用 |
| DR | Disaster Recovery | 灾难恢复 |
| DAS | Direct-Attached Storage | 直连存储 |
| NAS | Network-Attached Storage | 网络附加存储 |
| SAN | Storage Area Network | 存储区域网络 |
| HCI | Hyper-Converged Infrastructure | 超融合基础设施 |
| SDS | Software-Defined Storage | 软件定义存储 |
| SDN | Software-Defined Networking | 软件定义网络 |
| NFV | Network Function Virtualization | 网络功能虚拟化 |
| VLAN | Virtual Local Area Network | 虚拟局域网 |
| VXLAN | Virtual Extensible LAN | 虚拟可扩展局域网 |
| VPN | Virtual Private Network | 虚拟专用网络 |
| QoS | Quality of Service | 服务质量 |
| ACL | Access Control List | 访问控制列表 |
| RAID | Redundant Array of Independent Disks | 独立磁盘冗余阵列 |
| LVM | Logical Volume Manager | 逻辑卷管理器 |
| IOPS | Input/Output Operations Per Second | 每秒输入输出操作 |
| SSD | Solid State Drive | 固态硬盘 |
| HDD | Hard Disk Drive | 机械硬盘 |
| NVMe | Non-Volatile Memory Express | 非易失性内存快速 |
| RDMA | Remote Direct Memory Access | 远程直接内存访问 |
| iSCSI | Internet SCSI | 互联网SCSI |
| FC | Fibre Channel | 光纤通道 |
| FCoE | Fibre Channel over Ethernet | 以太网光纤通道 |
| NFS | Network File System | 网络文件系统 |
| SMB | Server Message Block | 服务器消息块 |
| CI | Continuous Integration | 持续集成 |
| CD | Continuous Delivery/Deployment | 持续交付/部署 |
| IaC | Infrastructure as Code | 基础设施即代码 |
| APM | Application Performance Monitoring | 应用性能监控 |
| SRE | Site Reliability Engineering | 站点可靠性工程 |
| OTel | OpenTelemetry | OpenTelemetry |
| mTLS | Mutual TLS | 双向TLS |

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19  
**维护状态**: ✅ 完成

---

> 💡 **提示**:
>
> - 使用 Ctrl+F (Windows) 或 Cmd+F (Mac) 快速查找术语
> - 建议结合官方文档理解术语的深层含义
> - 术语表会持续更新，欢迎反馈补充
