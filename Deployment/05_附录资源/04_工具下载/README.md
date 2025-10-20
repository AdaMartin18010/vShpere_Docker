# 工具软件下载指南

> **返回**: [附录资源首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [工具软件下载指南](#工具软件下载指南)
  - [📋 目录](#-目录)
  - [虚拟化软件](#虚拟化软件)
    - [VMware产品](#vmware产品)
    - [KVM相关](#kvm相关)
    - [Hyper-V相关](#hyper-v相关)
    - [虚拟机管理工具](#虚拟机管理工具)
  - [容器化工具](#容器化工具)
    - [容器运行时](#容器运行时)
    - [Kubernetes工具](#kubernetes工具)
    - [容器镜像仓库](#容器镜像仓库)
  - [运维管理工具](#运维管理工具)
    - [监控工具](#监控工具)
    - [日志工具](#日志工具)
    - [自动化工具](#自动化工具)
  - [开发调试工具](#开发调试工具)
    - [IDE与编辑器](#ide与编辑器)
    - [API测试工具](#api测试工具)
    - [终端工具](#终端工具)
  - [性能测试工具](#性能测试工具)
    - [压力测试](#压力测试)
    - [性能分析](#性能分析)
  - [网络工具](#网络工具)
    - [网络诊断](#网络诊断)
    - [抓包分析](#抓包分析)
  - [客户端工具](#客户端工具)
    - [SSH客户端](#ssh客户端)
    - [文件传输](#文件传输)
    - [数据库客户端](#数据库客户端)
  - [💡 下载建议](#-下载建议)
    - [1. 选择合适的版本](#1-选择合适的版本)
    - [2. 下载源选择](#2-下载源选择)
    - [3. 常用国内镜像](#3-常用国内镜像)
    - [4. 许可证说明](#4-许可证说明)

---

## 虚拟化软件

### VMware产品

| 软件名称 | 版本 | 平台 | 下载链接 | 说明 |
|---------|------|------|---------|------|
| **VMware ESXi** | 8.0 | 裸机 | [官方下载](https://www.vmware.com/products/esxi-and-esx.html) | 免费版有功能限制 |
| **VMware vCenter** | 8.0 | vCSA | [官方下载](https://www.vmware.com/products/vcenter.html) | 集中管理平台 |
| **VMware Workstation Pro** | 17.x | Windows/Linux | [官方下载](https://www.vmware.com/products/workstation-pro.html) | 桌面虚拟化(商业) |
| **VMware Fusion** | 13.x | macOS | [官方下载](https://www.vmware.com/products/fusion.html) | Mac虚拟化(商业) |
| **VMware Player** | 17.x | Windows/Linux | [官方下载](https://www.vmware.com/products/workstation-player.html) | 免费个人版 |

**下载说明**:

- ESXi免费版下载需要注册账号
- vCenter Server以Appliance (OVA)形式提供
- 商业版本需要购买许可证

---

### KVM相关

| 软件名称 | 平台 | 安装方式 | 说明 |
|---------|------|---------|------|
| **KVM** | Linux | 内核模块 | `modprobe kvm kvm_intel/kvm_amd` |
| **QEMU** | Linux | 包管理器 | `apt install qemu-kvm` / `yum install qemu-kvm` |
| **libvirt** | Linux | 包管理器 | `apt install libvirt-daemon-system` |
| **virt-manager** | Linux | 包管理器 | `apt install virt-manager` |
| **virt-viewer** | Linux/Windows | 包管理器/[下载](https://virt-manager.org/) | 远程查看器 |

**安装命令**:

```bash
# Ubuntu/Debian
apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager

# CentOS/RHEL
yum install qemu-kvm libvirt virt-install bridge-utils virt-manager
```

---

### Hyper-V相关

| 软件名称 | 版本 | 平台 | 下载链接 | 说明 |
|---------|------|------|---------|------|
| **Hyper-V** | - | Windows Server/Pro | 系统功能 | Windows内置 |
| **Hyper-V Manager** | - | Windows 10/11 | 系统功能 | 图形化管理工具 |
| **Windows Admin Center** | 最新 | Web | [官方下载](https://www.microsoft.com/en-us/windows-server/windows-admin-center) | 现代化管理界面 |

**启用Hyper-V** (PowerShell管理员):

```powershell
# Windows 10/11 Pro
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Windows Server
Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart
```

---

### 虚拟机管理工具

| 工具名称 | 平台 | 下载链接 | 说明 |
|---------|------|---------|------|
| **Vagrant** | 跨平台 | [官网](https://www.vagrantup.com/downloads) | 虚拟机快速部署 |
| **Packer** | 跨平台 | [官网](https://www.packer.io/downloads) | 镜像自动化构建 |
| **Terraform** | 跨平台 | [官网](https://www.terraform.io/downloads) | 基础设施即代码 |
| **VMware vSphere CLI** | 跨平台 | [官方文档](https://code.vmware.com/web/tool/4.0.0/vmware-vsphere-cli) | ESXi命令行工具 |
| **PowerCLI** | Windows | [PowerShell Gallery](https://www.powershellgallery.com/packages/VMware.PowerCLI/) | VMware PowerShell模块 |

---

## 容器化工具

### 容器运行时

| 软件名称 | 版本 | 平台 | 下载链接 | 说明 |
|---------|------|------|---------|------|
| **Docker Engine** | 最新 | Linux | [官网](https://docs.docker.com/engine/install/) | 容器运行时 |
| **Docker Desktop** | 最新 | Windows/macOS | [官网](https://www.docker.com/products/docker-desktop/) | 桌面版Docker |
| **containerd** | 最新 | Linux | [GitHub](https://github.com/containerd/containerd/releases) | 工业标准运行时 |
| **CRI-O** | 最新 | Linux | [官网](https://cri-o.io/) | Kubernetes专用运行时 |
| **Podman** | 最新 | Linux | [官网](https://podman.io/getting-started/installation) | 无守护进程容器引擎 |

**快速安装**:

```bash
# Docker Engine (Ubuntu)
curl -fsSL https://get.docker.com | bash

# Podman (Ubuntu 22.04+)
apt install podman

# containerd
wget https://github.com/containerd/containerd/releases/download/v1.7.0/containerd-1.7.0-linux-amd64.tar.gz
tar Cxzvf /usr/local containerd-1.7.0-linux-amd64.tar.gz
```

---

### Kubernetes工具

| 工具名称 | 用途 | 下载链接 | 说明 |
|---------|------|---------|------|
| **kubectl** | K8s CLI | [官网](https://kubernetes.io/docs/tasks/tools/) | 必备命令行工具 |
| **kubeadm** | 集群部署 | [官网](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/) | 官方部署工具 |
| **kubelet** | 节点代理 | [官网](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/) | K8s节点组件 |
| **Helm** | 包管理器 | [官网](https://helm.sh/docs/intro/install/) | K8s应用包管理 |
| **k9s** | 终端UI | [GitHub](https://github.com/derailed/k9s/releases) | 终端K8s管理 |
| **Lens** | 桌面IDE | [官网](https://k8slens.dev/) | K8s可视化IDE |
| **Rancher Desktop** | 桌面K8s | [官网](https://rancherdesktop.io/) | 本地K8s环境 |
| **Minikube** | 本地K8s | [官网](https://minikube.sigs.k8s.io/docs/start/) | 单节点K8s |
| **Kind** | K8s in Docker | [官网](https://kind.sigs.k8s.io/) | Docker中的K8s |

**快速安装**:

```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# k9s
curl -sS https://webi.sh/k9s | sh

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

---

### 容器镜像仓库

| 软件名称 | 类型 | 下载链接 | 说明 |
|---------|------|---------|------|
| **Harbor** | 企业级 | [GitHub](https://github.com/goharbor/harbor/releases) | CNCF项目 |
| **Docker Registry** | 简易版 | [Docker Hub](https://hub.docker.com/_/registry) | 官方镜像仓库 |
| **Nexus Repository** | 通用仓库 | [官网](https://www.sonatype.com/products/nexus-repository) | 支持多种格式 |
| **JFrog Artifactory** | 通用仓库 | [官网](https://jfrog.com/artifactory/) | 商业级仓库 |
| **Quay** | 企业级 | [官网](https://www.redhat.com/en/technologies/cloud-computing/quay) | Red Hat产品 |

---

## 运维管理工具

### 监控工具

| 工具名称 | 用途 | 下载链接 | 说明 |
|---------|------|---------|------|
| **Prometheus** | 监控 | [官网](https://prometheus.io/download/) | 时序数据库 |
| **Grafana** | 可视化 | [官网](https://grafana.com/grafana/download) | 可视化平台 |
| **Alertmanager** | 告警 | [官网](https://prometheus.io/download/#alertmanager) | Prometheus告警 |
| **Node Exporter** | 指标采集 | [GitHub](https://github.com/prometheus/node_exporter/releases) | 节点指标 |
| **kube-state-metrics** | K8s指标 | [GitHub](https://github.com/kubernetes/kube-state-metrics/releases) | K8s资源指标 |
| **cAdvisor** | 容器指标 | [GitHub](https://github.com/google/cadvisor/releases) | Google容器监控 |
| **Zabbix** | 监控平台 | [官网](https://www.zabbix.com/download) | 老牌监控系统 |
| **Nagios** | 监控平台 | [官网](https://www.nagios.org/downloads/) | 传统监控 |
| **Datadog Agent** | APM | [官网](https://docs.datadoghq.com/agent/) | 商业APM(免费版) |

---

### 日志工具

| 工具名称 | 用途 | 下载链接 | 说明 |
|---------|------|---------|------|
| **Elasticsearch** | 搜索引擎 | [官网](https://www.elastic.co/downloads/elasticsearch) | ELK核心 |
| **Logstash** | 日志处理 | [官网](https://www.elastic.co/downloads/logstash) | 数据管道 |
| **Kibana** | 可视化 | [官网](https://www.elastic.co/downloads/kibana) | ELK可视化 |
| **Filebeat** | 日志采集 | [官网](https://www.elastic.co/downloads/beats/filebeat) | 轻量级采集 |
| **Fluentd** | 日志采集 | [官网](https://www.fluentd.org/download) | CNCF项目 |
| **Fluent Bit** | 日志采集 | [官网](https://fluentbit.io/download/) | 轻量级Fluentd |
| **Loki** | 日志聚合 | [GitHub](https://github.com/grafana/loki/releases) | Grafana日志 |
| **Promtail** | 日志采集 | [GitHub](https://github.com/grafana/loki/releases) | Loki采集器 |

---

### 自动化工具

| 工具名称 | 用途 | 下载链接 | 说明 |
|---------|------|---------|------|
| **Ansible** | 配置管理 | [官网](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) | 无代理自动化 |
| **Terraform** | IaC | [官网](https://www.terraform.io/downloads) | 基础设施即代码 |
| **Jenkins** | CI/CD | [官网](https://www.jenkins.io/download/) | 老牌CI/CD |
| **GitLab Runner** | CI/CD | [官网](https://docs.gitlab.com/runner/install/) | GitLab CI执行器 |
| **ArgoCD** | GitOps | [官网](https://argo-cd.readthedocs.io/en/stable/getting_started/) | K8s GitOps |
| **FluxCD** | GitOps | [官网](https://fluxcd.io/docs/installation/) | CNCF GitOps |
| **Tekton** | CI/CD | [官网](https://tekton.dev/docs/getting-started/) | K8s原生CI/CD |
| **Spinnaker** | CD | [官网](https://spinnaker.io/docs/setup/install/) | Netflix CD平台 |

---

## 开发调试工具

### IDE与编辑器

| 工具名称 | 平台 | 下载链接 | 说明 |
|---------|------|---------|------|
| **Visual Studio Code** | 跨平台 | [官网](https://code.visualstudio.com/) | 微软开源编辑器 |
| **IntelliJ IDEA** | 跨平台 | [官网](https://www.jetbrains.com/idea/download/) | Java IDE |
| **PyCharm** | 跨平台 | [官网](https://www.jetbrains.com/pycharm/download/) | Python IDE |
| **GoLand** | 跨平台 | [官网](https://www.jetbrains.com/go/download/) | Go IDE |
| **Vim** | Linux/Unix | 包管理器 | 终端编辑器 |
| **Sublime Text** | 跨平台 | [官网](https://www.sublimetext.com/) | 轻量级编辑器 |

**推荐VSCode插件**:

- **Docker** - Docker管理
- **Kubernetes** - K8s管理
- **Remote - SSH** - 远程开发
- **YAML** - YAML语法支持
- **GitLens** - Git增强

---

### API测试工具

| 工具名称 | 类型 | 下载链接 | 说明 |
|---------|------|---------|------|
| **Postman** | 桌面应用 | [官网](https://www.postman.com/downloads/) | API测试平台 |
| **Insomnia** | 桌面应用 | [官网](https://insomnia.rest/download) | REST客户端 |
| **curl** | 命令行 | 系统自带 | HTTP命令行工具 |
| **HTTPie** | 命令行 | [官网](https://httpie.io/cli) | 人性化HTTP客户端 |
| **grpcurl** | 命令行 | [GitHub](https://github.com/fullstorydev/grpcurl/releases) | gRPC测试 |
| **Swagger UI** | Web | [官网](https://swagger.io/tools/swagger-ui/) | API文档测试 |

---

### 终端工具

| 工具名称 | 平台 | 下载链接 | 说明 |
|---------|------|---------|------|
| **Windows Terminal** | Windows | [Microsoft Store](https://aka.ms/terminal) | 现代化终端 |
| **iTerm2** | macOS | [官网](https://iterm2.com/) | Mac终端增强 |
| **Terminator** | Linux | 包管理器 | 分屏终端 |
| **Tmux** | Linux/Unix | 包管理器 | 终端复用器 |
| **screen** | Linux/Unix | 包管理器 | 终端会话管理 |
| **Oh My Zsh** | Linux/macOS | [官网](https://ohmyz.sh/) | Zsh配置框架 |

---

## 性能测试工具

### 压力测试

| 工具名称 | 用途 | 下载链接 | 说明 |
|---------|------|---------|------|
| **Apache Bench** | HTTP压测 | 系统自带 | `ab -n 1000 -c 100 http://example.com/` |
| **wrk** | HTTP压测 | [GitHub](https://github.com/wg/wrk) | 高性能压测 |
| **hey** | HTTP压测 | [GitHub](https://github.com/rakyll/hey) | Go编写压测工具 |
| **Locust** | 分布式压测 | [官网](https://locust.io/) | Python压测框架 |
| **JMeter** | 多协议压测 | [官网](https://jmeter.apache.org/download_jmeter.cgi) | Apache压测平台 |
| **K6** | 现代化压测 | [官网](https://k6.io/docs/getting-started/installation/) | Grafana压测工具 |

---

### 性能分析

| 工具名称 | 用途 | 下载链接 | 说明 |
|---------|------|---------|------|
| **fio** | 磁盘IO | 包管理器 | 磁盘性能测试 |
| **iozone** | 文件系统 | [官网](http://www.iozone.org/) | 文件系统性能 |
| **sysbench** | 综合性能 | [GitHub](https://github.com/akopytov/sysbench) | CPU/内存/磁盘测试 |
| **iperf3** | 网络带宽 | 包管理器 | 网络性能测试 |
| **netperf** | 网络性能 | [GitHub](https://github.com/HewlettPackard/netperf) | 全面网络测试 |
| **perf** | CPU分析 | 系统自带 | Linux性能分析 |
| **strace** | 系统调用 | 系统自带 | 系统调用跟踪 |
| **ltrace** | 库调用 | 系统自带 | 库函数跟踪 |

---

## 网络工具

### 网络诊断

| 工具名称 | 用途 | 下载链接 | 说明 |
|---------|------|---------|------|
| **nmap** | 端口扫描 | 包管理器 | 网络发现 |
| **netcat** | 网络工具 | 系统自带 | TCP/UDP工具 |
| **telnet** | 远程连接 | 包管理器 | 端口测试 |
| **mtr** | 路由追踪 | 包管理器 | 网络诊断 |
| **iftop** | 流量监控 | 包管理器 | 实时流量 |
| **nethogs** | 进程流量 | 包管理器 | 进程网络使用 |
| **iptraf-ng** | 流量统计 | 包管理器 | 网络流量监控 |
| **speedtest-cli** | 速度测试 | [GitHub](https://github.com/sivel/speedtest-cli) | 网速测试 |

---

### 抓包分析

| 工具名称 | 类型 | 下载链接 | 说明 |
|---------|------|---------|------|
| **Wireshark** | GUI | [官网](https://www.wireshark.org/download.html) | 抓包分析 |
| **tcpdump** | 命令行 | 系统自带 | 抓包工具 |
| **tshark** | 命令行 | 包管理器 | Wireshark命令行版 |
| **Fiddler** | 代理抓包 | [官网](https://www.telerik.com/fiddler) | HTTP(S)抓包 |
| **Charles** | 代理抓包 | [官网](https://www.charlesproxy.com/) | HTTP(S)抓包 |
| **mitmproxy** | 代理抓包 | [官网](https://mitmproxy.org/) | 中间人代理 |

---

## 客户端工具

### SSH客户端

| 工具名称 | 平台 | 下载链接 | 说明 |
|---------|------|---------|------|
| **PuTTY** | Windows | [官网](https://www.putty.org/) | 经典SSH客户端 |
| **MobaXterm** | Windows | [官网](https://mobaxterm.mobatek.net/) | 增强型终端 |
| **Xshell** | Windows | [官网](https://www.xshell.com/zh/free-for-home-school/) | 商业SSH(个人免费) |
| **Termius** | 跨平台 | [官网](https://termius.com/) | 现代SSH客户端 |
| **SecureCRT** | 跨平台 | [官网](https://www.vandyke.com/products/securecrt/) | 商业SSH客户端 |
| **OpenSSH** | Linux/macOS | 系统自带 | 原生SSH客户端 |

---

### 文件传输

| 工具名称 | 平台 | 下载链接 | 说明 |
|---------|------|---------|------|
| **FileZilla** | 跨平台 | [官网](https://filezilla-project.org/) | FTP/SFTP客户端 |
| **WinSCP** | Windows | [官网](https://winscp.net/) | SFTP/SCP客户端 |
| **Cyberduck** | Windows/macOS | [官网](https://cyberduck.io/) | FTP/SFTP客户端 |
| **rsync** | Linux/macOS | 系统自带 | 文件同步工具 |
| **scp** | Linux/macOS | 系统自带 | SSH文件传输 |
| **rclone** | 跨平台 | [官网](https://rclone.org/) | 云存储同步 |

---

### 数据库客户端

| 工具名称 | 支持数据库 | 下载链接 | 说明 |
|---------|-----------|---------|------|
| **DBeaver** | 多种 | [官网](https://dbeaver.io/download/) | 通用数据库工具 |
| **MySQL Workbench** | MySQL | [官网](https://www.mysql.com/products/workbench/) | MySQL官方工具 |
| **pgAdmin** | PostgreSQL | [官网](https://www.pgadmin.org/download/) | PostgreSQL官方工具 |
| **MongoDB Compass** | MongoDB | [官网](https://www.mongodb.com/products/compass) | MongoDB官方工具 |
| **RedisInsight** | Redis | [官网](https://redis.com/redis-enterprise/redis-insight/) | Redis GUI |
| **DataGrip** | 多种 | [官网](https://www.jetbrains.com/datagrip/) | JetBrains数据库IDE |
| **Navicat** | 多种 | [官网](https://www.navicat.com/) | 商业数据库工具 |

---

## 💡 下载建议

### 1. 选择合适的版本

- **稳定版**: 生产环境优先选择LTS或stable版本
- **最新版**: 测试环境可以尝试最新feature
- **社区版**: 优先选择开源/社区版本

### 2. 下载源选择

- **国内镜像**: 使用清华、阿里云等国内镜像加速
- **官方源**: 重要软件建议从官方下载
- **验证签名**: 下载后验证MD5/SHA256

### 3. 常用国内镜像

```bash
# Docker
https://docker.mirrors.sjtug.sjtu.edu.cn
https://docker.m.daocloud.io

# Kubernetes
https://mirrors.aliyun.com/kubernetes/

# PyPI
https://pypi.tuna.tsinghua.edu.cn/simple

# NPM
https://registry.npmmirror.com

# Ubuntu
https://mirrors.aliyun.com/ubuntu/

# CentOS
https://mirrors.aliyun.com/centos/
```

### 4. 许可证说明

- 注意开源软件的许可证类型 (Apache, MIT, GPL等)
- 商业软件需购买或申请免费许可
- 个人学习可选择免费版或Community版

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19  
**维护状态**: ✅ 完成

---

> 💡 **提示**:
>
> - 下载前请检查系统兼容性
> - 生产环境使用稳定版本
> - 定期更新工具以获取安全补丁
> - 保存安装包以便离线安装
