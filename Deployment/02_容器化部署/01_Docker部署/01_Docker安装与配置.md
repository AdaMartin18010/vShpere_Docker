# Docker安装与配置

> **返回**: [Docker部署目录](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Docker安装与配置](#docker安装与配置)
  - [📋 目录](#-目录)
  - [1. Docker概述](#1-docker概述)
  - [2. 系统要求](#2-系统要求)
  - [3. Ubuntu安装Docker](#3-ubuntu安装docker)
    - [3.1 使用官方脚本安装 (推荐)](#31-使用官方脚本安装-推荐)
    - [3.2 使用APT仓库安装](#32-使用apt仓库安装)
  - [4. CentOS/RHEL安装Docker](#4-centosrhel安装docker)
    - [4.1 CentOS Stream 9安装](#41-centos-stream-9安装)
    - [4.2 RHEL 8/9安装](#42-rhel-89安装)
  - [5. 国产操作系统安装Docker](#5-国产操作系统安装docker)
    - [5.1 麒麟(Kylin)安装Docker](#51-麒麟kylin安装docker)
    - [5.2 统信UOS安装Docker](#52-统信uos安装docker)
  - [6. Docker配置优化](#6-docker配置优化)
    - [6.1 daemon.json完整配置](#61-daemonjson完整配置)
    - [6.2 镜像加速配置](#62-镜像加速配置)
    - [6.3 存储驱动选择](#63-存储驱动选择)
  - [7. Rootless Docker](#7-rootless-docker)
    - [7.1 Rootless Docker安装](#71-rootless-docker安装)
  - [8. Docker日志配置](#8-docker日志配置)
    - [8.1 日志驱动配置](#81-日志驱动配置)
    - [8.2 日志轮转配置](#82-日志轮转配置)
  - [9. Docker监控](#9-docker监控)
    - [9.1 cAdvisor监控](#91-cadvisor监控)
    - [9.2 Prometheus监控](#92-prometheus监控)
  - [10. 故障排查](#10-故障排查)
  - [相关文档](#相关文档)

---

## 1. Docker概述

```yaml
Docker_Overview:
  定义: 开源容器化平台
  
  核心组件:
    Docker Engine:
      - Docker守护进程 (dockerd)
      - Docker CLI (docker命令)
      - Docker API
    
    Docker镜像 (Image):
      - 只读模板
      - 分层文件系统
      - 可共享复用
    
    Docker容器 (Container):
      - 镜像的运行实例
      - 隔离的进程空间
      - 可启动、停止、删除
    
    Docker仓库 (Registry):
      - Docker Hub (公共)
      - Harbor (私有)
      - 云厂商仓库
  
  核心技术:
    Namespace (命名空间):
      - PID namespace (进程隔离)
      - NET namespace (网络隔离)
      - IPC namespace (进程间通信隔离)
      - MNT namespace (挂载点隔离)
      - UTS namespace (主机名隔离)
      - USER namespace (用户隔离)
    
    Cgroups (控制组):
      - CPU限制
      - 内存限制
      - 磁盘IO限制
      - 网络带宽限制
    
    联合文件系统 (Union FS):
      - OverlayFS
      - AUFS
      - Btrfs
      - ZFS
  
  优势:
    - 轻量级 (相比虚拟机)
    - 快速启动 (秒级)
    - 一致性 (开发/测试/生产环境)
    - 易于迁移
    - 版本管理
    - 易于扩展
  
  应用场景:
    - 微服务架构
    - 持续集成/持续部署 (CI/CD)
    - 应用快速交付
    - 开发环境标准化
    - 混合云部署
```

---

## 2. 系统要求

```yaml
System_Requirements:
  操作系统:
    Linux (推荐):
      - Ubuntu 20.04 LTS / 22.04 LTS
      - CentOS Stream 8 / 9
      - RHEL 8 / 9
      - Debian 10 / 11
      - 麒麟 V10
      - 统信 UOS 20
      - openEuler 20.03 LTS / 22.03 LTS
    
    Windows:
      - Windows 10 Pro / Enterprise (64-bit)
      - Windows 11 Pro / Enterprise
      - Windows Server 2019 / 2022
      - 需要WSL 2
    
    macOS:
      - macOS 10.15+ (Catalina)
      - Docker Desktop for Mac
  
  硬件要求:
    最低配置:
      CPU: 2核
      内存: 4GB
      磁盘: 20GB可用空间
    
    推荐配置:
      CPU: 4核+
      内存: 8GB+
      磁盘: 100GB+ SSD
  
  内核要求 (Linux):
    最低内核版本: 3.10
    推荐内核版本: 5.4+
    
    必需内核模块:
      - overlay
      - br_netfilter
      - xt_conntrack
      - nf_conntrack
      - ip_tables
      - iptable_filter
      - iptable_nat
  
  其他要求:
    - 64位操作系统
    - 开启CPU虚拟化 (对于Windows/Mac)
    - 网络连接 (用于拉取镜像)
    - root或sudo权限
```

---

## 3. Ubuntu安装Docker

### 3.1 使用官方脚本安装 (推荐)

```bash
#!/bin/bash
# ========================================
# Ubuntu Docker 一键安装脚本
# ========================================

set -e

echo "========================================="
echo "  Ubuntu Docker 安装脚本"
echo "========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
  echo "请使用root权限运行此脚本"
  exit 1
fi

# 系统信息
echo -e "\n➤ 系统信息:"
lsb_release -a
uname -r

# 1. 卸载旧版本Docker (如果存在)
echo -e "\n➤ 卸载旧版本Docker..."
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# 2. 更新软件包索引
echo -e "\n➤ 更新软件包索引..."
apt-get update

# 3. 安装依赖包
echo -e "\n➤ 安装依赖包..."
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 4. 添加Docker官方GPG密钥
echo -e "\n➤ 添加Docker GPG密钥..."
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 5. 设置Docker stable仓库
echo -e "\n➤ 设置Docker仓库..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# 6. 更新软件包索引
echo -e "\n➤ 更新软件包索引..."
apt-get update

# 7. 安装Docker Engine
echo -e "\n➤ 安装Docker Engine..."
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 8. 启动Docker服务
echo -e "\n➤ 启动Docker服务..."
systemctl start docker
systemctl enable docker

# 9. 验证安装
echo -e "\n➤ 验证Docker安装..."
docker --version
docker compose version

# 10. 运行测试容器
echo -e "\n➤ 运行Hello World测试..."
docker run --rm hello-world

# 11. 配置当前用户docker权限 (可选)
if [ -n "$SUDO_USER" ]; then
  echo -e "\n➤ 配置用户docker权限..."
  usermod -aG docker "$SUDO_USER"
  echo "✅ 用户 $SUDO_USER 已添加到docker组"
  echo "⚠️  请注销并重新登录以使权限生效"
fi

echo -e "\n========================================="
echo "✅ Docker安装完成！"
echo "========================================="
echo "Docker版本: $(docker --version)"
echo "Compose版本: $(docker compose version)"
echo ""
echo "下一步:"
echo "1. 配置docker加速器 (可选)"
echo "2. 配置daemon.json (可选)"
echo "3. 开始使用: docker run hello-world"
echo "========================================="
```

### 3.2 使用APT仓库安装

```bash
# 1. 卸载旧版本
sudo apt-get remove docker docker-engine docker.io containerd runc

# 2. 安装依赖
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release

# 3. 添加Docker官方GPG密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 4. 设置仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. 安装Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 6. 验证安装
sudo docker run hello-world
```

**使用国内镜像源 (清华/阿里云)**:

```bash
# 使用清华源
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

---

## 4. CentOS/RHEL安装Docker

### 4.1 CentOS Stream 9安装

```bash
#!/bin/bash
# ========================================
# CentOS Stream 9 Docker安装脚本
# ========================================

set -e

echo "========================================="
echo "  CentOS Stream 9 Docker 安装"
echo "========================================="

# 1. 卸载旧版本
echo "➤ 卸载旧版本..."
sudo yum remove -y docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine \
                  podman \
                  runc 2>/dev/null || true

# 2. 安装yum-utils
echo "➤ 安装依赖..."
sudo yum install -y yum-utils

# 3. 添加Docker仓库
echo "➤ 添加Docker仓库..."
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 或使用国内镜像
# sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 4. 安装Docker Engine
echo "➤ 安装Docker Engine..."
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 5. 启动Docker
echo "➤ 启动Docker服务..."
sudo systemctl start docker
sudo systemctl enable docker

# 6. 验证安装
echo "➤ 验证Docker安装..."
docker --version
docker compose version
sudo docker run --rm hello-world

echo -e "\n✅ Docker安装完成！"
```

### 4.2 RHEL 8/9安装

```bash
# RHEL需要订阅，或使用CentOS仓库

# 1. 删除podman (RHEL默认使用podman)
sudo yum remove -y podman buildah

# 2. 添加Docker仓库
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 3. 安装Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 4. 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 5. 验证
sudo docker run hello-world
```

---

## 5. 国产操作系统安装Docker

### 5.1 麒麟(Kylin)安装Docker

```bash
#!/bin/bash
# ========================================
# 麒麟V10 Docker安装脚本
# ========================================

# 麒麟V10基于Ubuntu 20.04/Debian

# 方法1: 使用系统仓库 (如果有)
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# 方法2: 使用Docker官方仓库
# 参考Ubuntu安装方法

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证
sudo docker run hello-world
```

### 5.2 统信UOS安装Docker

```bash
#!/bin/bash
# ========================================
# 统信UOS 20 Docker安装脚本
# ========================================

# UOS基于Debian

# 1. 更新软件源
sudo apt-get update

# 2. 安装Docker (使用系统仓库)
sudo apt-get install -y docker.io docker-compose

# 3. 或使用Docker官方仓库
# 添加Docker GPG密钥
curl -fsSL https://download.docker.com/linux/debian/gpg | \
  sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/debian \
  bullseye stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 4. 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 5. 验证
sudo docker run hello-world
```

---

## 6. Docker配置优化

### 6.1 daemon.json完整配置

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "insecure-registries": [
    "harbor.example.com"
  ],
  "data-root": "/var/lib/docker",
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  },
  "live-restore": true,
  "userland-proxy": false,
  "experimental": false,
  "metrics-addr": "127.0.0.1:9323",
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5,
  "default-shm-size": "64M",
  "dns": ["8.8.8.8", "8.8.4.4"],
  "bip": "172.17.0.1/16",
  "default-address-pools": [
    {
      "base": "172.18.0.0/16",
      "size": 24
    }
  ],
  "iptables": true,
  "ipv6": false,
  "fixed-cidr-v6": "2001:db8:1::/64"
}
```

**配置说明**:

```yaml
Docker_Daemon_Config:
  registry-mirrors:
    说明: 镜像加速器
    推荐:
      - 中科大: https://docker.mirrors.ustc.edu.cn
      - 网易: https://hub-mirror.c.163.com
      - 百度: https://mirror.baidubce.com
      - 阿里云: https://xxxxx.mirror.aliyuncs.com (需注册)
  
  insecure-registries:
    说明: 不安全的私有仓库 (HTTP)
    示例: ["harbor.example.com:80"]
  
  data-root:
    说明: Docker数据目录
    默认: /var/lib/docker
    建议: 独立磁盘挂载点
  
  storage-driver:
    说明: 存储驱动
    推荐: overlay2 (性能最好)
    备选: devicemapper, aufs, btrfs, zfs
  
  log-driver:
    说明: 日志驱动
    类型:
      json-file: 默认，JSON格式
      syslog: 系统日志
      journald: Systemd日志
      none: 不记录日志
      fluentd: Fluentd日志收集
      splunk: Splunk日志
  
  log-opts:
    max-size: 单个日志文件最大大小
    max-file: 保留日志文件数量
  
  live-restore:
    说明: Docker守护进程重启时保持容器运行
    推荐: true
  
  userland-proxy:
    说明: 使用用户空间代理
    推荐: false (使用hairpin NAT更高效)
  
  metrics-addr:
    说明: Prometheus监控指标地址
    示例: "127.0.0.1:9323"
```

### 6.2 镜像加速配置

```bash
# 创建docker配置目录
sudo mkdir -p /etc/docker

# 配置镜像加速
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF

# 重启Docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证配置
docker info | grep -A 5 "Registry Mirrors"
```

### 6.3 存储驱动选择

```yaml
Storage_Drivers:
  overlay2 (推荐):
    优点:
      - 性能最好
      - 支持所有主流Linux内核
      - 文件共享效率高
    
    内核要求: 4.0+
    
    适用场景: 生产环境首选
  
  devicemapper:
    优点:
      - 支持旧内核
      - 块设备级存储
    
    缺点:
      - 性能较差
      - 配置复杂
    
    适用场景: CentOS 7及更早版本
  
  btrfs:
    优点:
      - Copy-on-Write
      - 快照功能强大
    
    缺点:
      - 需要Btrfs文件系统
      - 性能不如overlay2
    
    适用场景: 需要高级快照功能
  
  zfs:
    优点:
      - 数据完整性
      - 压缩和去重
    
    缺点:
      - 内存占用高
      - 需要ZFS文件系统
    
    适用场景: 大型数据存储

Storage_Driver_Selection:
  Ubuntu_20_04_22_04: overlay2
  CentOS_8_9: overlay2
  CentOS_7: devicemapper 或 overlay2
  RHEL_8_9: overlay2
```

---

## 7. Rootless Docker

### 7.1 Rootless Docker安装

```bash
#!/bin/bash
# ========================================
# Rootless Docker 安装脚本
# ========================================

# Rootless模式: 以非root用户运行Docker守护进程

# 前提条件
echo "➤ 检查前提条件..."

# 1. 安装依赖
sudo apt-get install -y uidmap dbus-user-session

# 2. 启用cgroup v2 (Ubuntu 21.10+默认启用)
# 检查cgroup版本
stat -fc %T /sys/fs/cgroup/

# 3. 安装Rootless Docker
echo "➤ 安装Rootless Docker..."
curl -fsSL https://get.docker.com/rootless | sh

# 4. 配置环境变量
echo "➤ 配置环境变量..."
cat >> ~/.bashrc << 'EOF'

# Docker Rootless
export PATH=$HOME/bin:$PATH
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock
EOF

source ~/.bashrc

# 5. 启动Docker
echo "➤ 启动Docker (Rootless)..."
systemctl --user start docker
systemctl --user enable docker

# 6. 配置开机自启 (可选)
sudo loginctl enable-linger $(whoami)

# 7. 验证
echo "➤ 验证Rootless Docker..."
docker version
docker run --rm hello-world

echo "✅ Rootless Docker安装完成！"
```

**Rootless Docker限制**:

```yaml
Rootless_Docker_Limitations:
  限制:
    - 不支持AppArmor, SELinux
    - 不支持Checkpoint/restore (CRIU)
    - 不支持--net=host (使用slirp4netns)
    - 性能略低于root模式
    - 端口< 1024需要额外配置
  
  优势:
    - 安全性更高 (非root运行)
    - 多用户隔离
    - 不需要root权限
  
  适用场景:
    - 开发环境
    - 多用户系统
    - 安全性要求高的环境
```

---

## 8. Docker日志配置

### 8.1 日志驱动配置

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3",
    "compress": "true",
    "labels": "production_status,geo",
    "env": "os,customer"
  }
}
```

### 8.2 日志轮转配置

```bash
# 方法1: Docker daemon配置 (推荐)
# 已在daemon.json配置

# 方法2: 容器启动时配置
docker run -d \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=5 \
  nginx:latest

# 方法3: 使用logrotate
sudo tee /etc/logrotate.d/docker << 'EOF'
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  size=10M
  missingok
  delaycompress
  copytruncate
}
EOF
```

**查看容器日志**:

```bash
# 查看最近100行
docker logs --tail 100 container_name

# 实时跟踪日志
docker logs -f container_name

# 查看最近5分钟日志
docker logs --since 5m container_name

# 查看指定时间范围日志
docker logs --since 2025-10-19T10:00:00 --until 2025-10-19T11:00:00 container_name
```

---

## 9. Docker监控

### 9.1 cAdvisor监控

```bash
# 运行cAdvisor
docker run -d \
  --name=cadvisor \
  --restart=always \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --volume=/dev/disk/:/dev/disk:ro \
  --publish=8080:8080 \
  --privileged \
  --device=/dev/kmsg \
  google/cadvisor:latest

# 访问
# http://服务器IP:8080
```

### 9.2 Prometheus监控

```yaml
# docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: always
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
  
  cadvisor:
    image: google/cadvisor:latest
    container_name: cadvisor
    restart: always
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"
  
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'docker'
    static_configs:
      - targets: ['172.17.0.1:9323']
  
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

---

## 10. 故障排查

```yaml
Common_Issues:
  问题1_Docker服务无法启动:
    症状: systemctl start docker 失败
    
    排查步骤:
      1. 查看日志:
        - journalctl -u docker.service -n 50
        - journalctl -xe
      
      2. 检查配置:
        - dockerd --validate
        - cat /etc/docker/daemon.json
      
      3. 检查存储驱动:
        - df -h /var/lib/docker
        - docker info | grep Storage
    
    常见原因:
      - daemon.json配置错误
      - 磁盘空间不足
      - 存储驱动不兼容
      - 端口冲突
    
    解决方法:
      - 修复daemon.json语法错误
      - 清理磁盘空间
      - 更换存储驱动
      - 修改监听端口

  问题2_容器无法启动:
    症状: docker run 失败
    
    排查:
      docker logs container_name
      docker inspect container_name
      dmesg | tail
    
    常见原因:
      - 镜像损坏
      - 端口冲突
      - 资源不足
      - 权限问题
    
    解决:
      - 重新拉取镜像
      - 更换端口
      - 增加资源配额
      - 检查SELinux/AppArmor

  问题3_网络连接问题:
    症状: 容器无法访问外网
    
    排查:
      docker network ls
      docker network inspect bridge
      iptables -L -n
      cat /proc/sys/net/ipv4/ip_forward
    
    解决:
      # 启用IP转发
      echo 1 > /proc/sys/net/ipv4/ip_forward
      
      # 重启Docker
      systemctl restart docker
      
      # 检查防火墙规则
      iptables -L -n | grep DOCKER

  问题4_磁盘空间不足:
    症状: no space left on device
    
    排查:
      df -h
      docker system df
      du -sh /var/lib/docker/*
    
    清理:
      # 清理未使用的资源
      docker system prune -a -f
      
      # 清理卷
      docker volume prune -f
      
      # 清理构建缓存
      docker builder prune -a -f
```

**诊断命令集合**:

```bash
#!/bin/bash
# Docker诊断命令集合

echo "=== Docker版本信息 ==="
docker version

echo -e "\n=== Docker系统信息 ==="
docker info

echo -e "\n=== Docker磁盘使用 ==="
docker system df

echo -e "\n=== 运行中的容器 ==="
docker ps

echo -e "\n=== 所有容器 ==="
docker ps -a

echo -e "\n=== Docker镜像 ==="
docker images

echo -e "\n=== Docker网络 ==="
docker network ls

echo -e "\n=== Docker卷 ==="
docker volume ls

echo -e "\n=== Docker服务状态 ==="
systemctl status docker

echo -e "\n=== Docker日志 (最近50行) ==="
journalctl -u docker -n 50 --no-pager
```

---

## 相关文档

- [Docker镜像管理](02_Docker镜像管理.md)
- [Docker Compose](03_Docker_Compose.md)
- [Docker安全与最佳实践](04_Docker安全与最佳实践.md)
- [Kubernetes集群部署](../02_Kubernetes部署/01_集群部署.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪
