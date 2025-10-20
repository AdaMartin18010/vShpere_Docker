# 自动化脚本集合

> **返回**: [附录资源首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [自动化脚本集合](#自动化脚本集合)
  - [📋 目录](#-目录)
  - [环境初始化脚本](#环境初始化脚本)
    - [Linux系统初始化](#linux系统初始化)
    - [Docker安装](#docker安装)
    - [Kubernetes节点初始化](#kubernetes节点初始化)
  - [自动化部署脚本](#自动化部署脚本)
    - [Docker Compose部署](#docker-compose部署)
    - [Kubernetes部署](#kubernetes部署)
  - [备份恢复脚本](#备份恢复脚本)
    - [Docker卷备份](#docker卷备份)
    - [etcd备份](#etcd备份)
    - [MySQL备份](#mysql备份)
  - [监控告警脚本](#监控告警脚本)
    - [系统监控脚本](#系统监控脚本)
    - [告警脚本](#告警脚本)
  - [运维工具脚本](#运维工具脚本)
    - [批量操作脚本](#批量操作脚本)
    - [日志分析脚本](#日志分析脚本)
  - [配置文件模板](#配置文件模板)
    - [Docker Compose模板](#docker-compose模板)
    - [Kubernetes清单模板](#kubernetes清单模板)
    - [Prometheus配置模板](#prometheus配置模板)

---

## 环境初始化脚本

### Linux系统初始化

**用途**: 快速初始化Linux服务器，配置基础环境

```bash
#!/bin/bash
# init_linux.sh - Linux系统初始化脚本
# Usage: sudo bash init_linux.sh

set -e

echo "========== Linux系统初始化 =========="

# 更新系统
echo "[1/8] 更新系统..."
apt update && apt upgrade -y || yum update -y

# 安装常用工具
echo "[2/8] 安装常用工具..."
if command -v apt &> /dev/null; then
    apt install -y vim git curl wget net-tools htop iotop sysstat \
        ncdu tree jq unzip lsof tcpdump nmap
elif command -v yum &> /dev/null; then
    yum install -y vim git curl wget net-tools htop iotop sysstat \
        ncdu tree jq unzip lsof tcpdump nmap
fi

# 配置时区
echo "[3/8] 配置时区..."
timedatectl set-timezone Asia/Shanghai

# 配置NTP
echo "[4/8] 配置NTP..."
if command -v apt &> /dev/null; then
    apt install -y chrony
    systemctl enable chrony
    systemctl start chrony
elif command -v yum &> /dev/null; then
    yum install -y chrony
    systemctl enable chronyd
    systemctl start chronyd
fi

# 禁用Swap
echo "[5/8] 禁用Swap..."
swapoff -a
sed -i '/swap/d' /etc/fstab

# 内核参数优化
echo "[6/8] 优化内核参数..."
cat >> /etc/sysctl.conf << EOF
# 网络优化
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_max_syn_backlog = 8192
net.core.netdev_max_backlog = 5000
net.core.somaxconn = 1024
net.ipv4.tcp_syncookies = 1

# 文件系统优化
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 8192

# 虚拟内存优化
vm.swappiness = 0
vm.max_map_count = 262144
EOF

# 加载br_netfilter模块
modprobe br_netfilter
echo "br_netfilter" > /etc/modules-load.d/br_netfilter.conf

sysctl -p

# 配置limits
echo "[7/8] 配置limits..."
cat >> /etc/security/limits.conf << EOF
* soft nofile 655360
* hard nofile 655360
* soft nproc 655360
* hard nproc 655360
EOF

# 配置SSH
echo "[8/8] 优化SSH配置..."
sed -i 's/#UseDNS yes/UseDNS no/' /etc/ssh/sshd_config
sed -i 's/GSSAPIAuthentication yes/GSSAPIAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

echo "========== 系统初始化完成 =========="
echo "建议重启系统以使所有设置生效: reboot"
```

---

### Docker安装

**用途**: 一键安装Docker CE

```bash
#!/bin/bash
# install_docker.sh - Docker安装脚本
# Usage: sudo bash install_docker.sh

set -e

echo "========== Docker CE 安装 =========="

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "无法检测操作系统"
    exit 1
fi

# 卸载旧版本
echo "[1/5] 卸载旧版本Docker..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get remove -y docker docker-engine docker.io containerd runc || true
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum remove -y docker docker-client docker-client-latest docker-common \
        docker-latest docker-latest-logrotate docker-logrotate docker-engine || true
fi

# 安装依赖
echo "[2/5] 安装依赖..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get update
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # 添加Docker GPG密钥
    curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # 添加Docker仓库
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装Docker
    echo "[3/5] 安装Docker..."
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum install -y yum-utils device-mapper-persistent-data lvm2
    
    # 添加Docker仓库
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    # 安装Docker
    echo "[3/5] 安装Docker..."
    yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

# 配置Docker
echo "[4/5] 配置Docker..."
mkdir -p /etc/docker

cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.sjtug.sjtu.edu.cn",
    "https://docker.m.daocloud.io"
  ],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "live-restore": true,
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 10
}
EOF

# 启动Docker
echo "[5/5] 启动Docker..."
systemctl daemon-reload
systemctl enable docker
systemctl start docker

# 验证安装
docker version
docker run --rm hello-world

echo "========== Docker安装完成 =========="
echo "Docker版本: $(docker --version)"
echo "添加用户到docker组: usermod -aG docker \$USER"
```

---

### Kubernetes节点初始化

**用途**: 准备Kubernetes节点环境

```bash
#!/bin/bash
# init_k8s_node.sh - Kubernetes节点初始化脚本
# Usage: sudo bash init_k8s_node.sh

set -e

K8S_VERSION="1.28"

echo "========== Kubernetes节点初始化 =========="

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "无法检测操作系统"
    exit 1
fi

# 禁用Swap
echo "[1/7] 禁用Swap..."
swapoff -a
sed -i '/swap/d' /etc/fstab

# 加载内核模块
echo "[2/7] 加载内核模块..."
cat > /etc/modules-load.d/k8s.conf << EOF
overlay
br_netfilter
EOF

modprobe overlay
modprobe br_netfilter

# 配置内核参数
echo "[3/7] 配置内核参数..."
cat > /etc/sysctl.d/k8s.conf << EOF
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sysctl --system

# 安装containerd
echo "[4/7] 安装containerd..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get update
    apt-get install -y containerd
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum install -y containerd.io
fi

# 配置containerd
mkdir -p /etc/containerd
containerd config default > /etc/containerd/config.toml

# 修改为systemd cgroup driver
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

systemctl restart containerd
systemctl enable containerd

# 安装kubeadm、kubelet、kubectl
echo "[5/7] 安装kubeadm、kubelet、kubectl..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get install -y apt-transport-https ca-certificates curl
    
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v${K8S_VERSION}/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v${K8S_VERSION}/deb/ /" | tee /etc/apt/sources.list.d/kubernetes.list
    
    apt-get update
    apt-get install -y kubelet kubeadm kubectl
    apt-mark hold kubelet kubeadm kubectl
    
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    cat > /etc/yum.repos.d/kubernetes.repo << EOF
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v${K8S_VERSION}/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v${K8S_VERSION}/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF
    
    yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
    systemctl enable kubelet
fi

# 关闭SELinux (CentOS/RHEL)
if [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    echo "[6/7] 关闭SELinux..."
    setenforce 0 || true
    sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
fi

# 配置crictl
echo "[7/7] 配置crictl..."
cat > /etc/crictl.yaml << EOF
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
EOF

echo "========== Kubernetes节点初始化完成 =========="
echo "kubeadm版本: $(kubeadm version -o short)"
echo "kubelet版本: $(kubelet --version)"
echo "kubectl版本: $(kubectl version --client -o yaml | grep gitVersion)"
echo ""
echo "接下来可以:"
echo "  - 创建集群: kubeadm init ..."
echo "  - 加入集群: kubeadm join ..."
```

---

## 自动化部署脚本

### Docker Compose部署

**用途**: 自动部署Docker Compose应用

```bash
#!/bin/bash
# deploy_compose.sh - Docker Compose自动部署脚本
# Usage: bash deploy_compose.sh [start|stop|restart|logs|ps]

set -e

COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="myapp"

function start() {
    echo "启动应用..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps
}

function stop() {
    echo "停止应用..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME stop
}

function restart() {
    echo "重启应用..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME restart
}

function logs() {
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
}

function ps_status() {
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps
}

function remove() {
    echo "删除应用..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down -v
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    ps)
        ps_status
        ;;
    remove)
        remove
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|ps|remove}"
        exit 1
        ;;
esac
```

---

### Kubernetes部署

**用途**: 自动部署Kubernetes应用

```bash
#!/bin/bash
# deploy_k8s_app.sh - Kubernetes应用自动部署脚本
# Usage: bash deploy_k8s_app.sh <app-name> <namespace>

set -e

APP_NAME=$1
NAMESPACE=${2:-default}
MANIFESTS_DIR="./k8s"

if [ -z "$APP_NAME" ]; then
    echo "Usage: $0 <app-name> [namespace]"
    exit 1
fi

echo "========== 部署应用: $APP_NAME =========="

# 创建命名空间
echo "[1/4] 创建命名空间 $NAMESPACE..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# 应用ConfigMap
if [ -f "$MANIFESTS_DIR/configmap.yaml" ]; then
    echo "[2/4] 应用ConfigMap..."
    kubectl apply -f $MANIFESTS_DIR/configmap.yaml -n $NAMESPACE
fi

# 应用Secret
if [ -f "$MANIFESTS_DIR/secret.yaml" ]; then
    echo "[3/4] 应用Secret..."
    kubectl apply -f $MANIFESTS_DIR/secret.yaml -n $NAMESPACE
fi

# 应用应用清单
echo "[4/4] 部署应用..."
kubectl apply -f $MANIFESTS_DIR/ -n $NAMESPACE

# 等待部署完成
echo "等待Deployment就绪..."
kubectl wait --for=condition=available --timeout=300s deployment/$APP_NAME -n $NAMESPACE

# 显示状态
echo ""
echo "========== 部署完成 =========="
kubectl get all -n $NAMESPACE -l app=$APP_NAME
```

---

## 备份恢复脚本

### Docker卷备份

**用途**: 备份Docker卷数据

```bash
#!/bin/bash
# backup_docker_volume.sh - Docker卷备份脚本
# Usage: bash backup_docker_volume.sh <volume-name> [backup-dir]

set -e

VOLUME_NAME=$1
BACKUP_DIR=${2:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${VOLUME_NAME}_${TIMESTAMP}.tar.gz"

if [ -z "$VOLUME_NAME" ]; then
    echo "Usage: $0 <volume-name> [backup-dir]"
    exit 1
fi

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "========== 备份Docker卷: $VOLUME_NAME =========="

# 备份卷
docker run --rm \
    -v $VOLUME_NAME:/source:ro \
    -v $(pwd)/$BACKUP_DIR:/backup \
    alpine \
    tar czf /backup/$(basename $BACKUP_FILE) -C /source .

echo "备份完成: $BACKUP_FILE"
ls -lh $BACKUP_FILE
```

---

### etcd备份

**用途**: 备份Kubernetes etcd数据

```bash
#!/bin/bash
# backup_etcd.sh - etcd备份脚本
# Usage: bash backup_etcd.sh [backup-dir]

set -e

BACKUP_DIR=${1:-./etcd-backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/etcd-snapshot-${TIMESTAMP}.db"

# etcd配置
ETCD_ENDPOINTS="https://127.0.0.1:2379"
ETCD_CACERT="/etc/kubernetes/pki/etcd/ca.crt"
ETCD_CERT="/etc/kubernetes/pki/etcd/server.crt"
ETCD_KEY="/etc/kubernetes/pki/etcd/server.key"

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "========== 备份etcd =========="

# 执行备份
ETCDCTL_API=3 etcdctl \
    --endpoints=$ETCD_ENDPOINTS \
    --cacert=$ETCD_CACERT \
    --cert=$ETCD_CERT \
    --key=$ETCD_KEY \
    snapshot save $BACKUP_FILE

echo "备份完成: $BACKUP_FILE"

# 验证备份
ETCDCTL_API=3 etcdctl snapshot status $BACKUP_FILE -w table

# 清理旧备份 (保留最近7天)
find $BACKUP_DIR -name "etcd-snapshot-*.db" -mtime +7 -delete

echo "========== 备份成功 =========="
```

---

### MySQL备份

**用途**: 自动备份MySQL数据库

```bash
#!/bin/bash
# backup_mysql.sh - MySQL备份脚本
# Usage: bash backup_mysql.sh

set -e

# 配置
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
MYSQL_USER="backup"
MYSQL_PASSWORD="backup_password"
BACKUP_DIR="/backup/mysql"
RETENTION_DAYS=7

# 创建备份目录
mkdir -p $BACKUP_DIR

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "========== MySQL备份开始 =========="

# 获取所有数据库
DATABASES=$(mysql -h$MYSQL_HOST -P$MYSQL_PORT -u$MYSQL_USER -p$MYSQL_PASSWORD -e "SHOW DATABASES;" | grep -Ev "(Database|information_schema|performance_schema|mysql|sys)")

for DB in $DATABASES; do
    echo "备份数据库: $DB"
    
    BACKUP_FILE="$BACKUP_DIR/${DB}_${TIMESTAMP}.sql.gz"
    
    mysqldump -h$MYSQL_HOST -P$MYSQL_PORT -u$MYSQL_USER -p$MYSQL_PASSWORD \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --hex-blob \
        $DB | gzip > $BACKUP_FILE
    
    echo "完成: $BACKUP_FILE"
done

# 清理旧备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "========== MySQL备份完成 =========="
```

---

## 监控告警脚本

### 系统监控脚本

**用途**: 监控系统资源使用情况

```bash
#!/bin/bash
# monitor_system.sh - 系统资源监控脚本
# Usage: bash monitor_system.sh

# 阈值配置
CPU_THRESHOLD=80
MEM_THRESHOLD=80
DISK_THRESHOLD=85

# 获取CPU使用率
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d% -f1 | awk '{print int($1)}')

# 获取内存使用率
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')

# 获取磁盘使用率
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | cut -d% -f1)

echo "========== 系统资源监控 =========="
echo "时间: $(date)"
echo "CPU使用率: ${CPU_USAGE}%"
echo "内存使用率: ${MEM_USAGE}%"
echo "磁盘使用率: ${DISK_USAGE}%"

# 检查告警
if [ $CPU_USAGE -gt $CPU_THRESHOLD ]; then
    echo "⚠️  警告: CPU使用率过高 (${CPU_USAGE}% > ${CPU_THRESHOLD}%)"
fi

if [ $MEM_USAGE -gt $MEM_THRESHOLD ]; then
    echo "⚠️  警告: 内存使用率过高 (${MEM_USAGE}% > ${MEM_THRESHOLD}%)"
fi

if [ $DISK_USAGE -gt $DISK_THRESHOLD ]; then
    echo "⚠️  警告: 磁盘使用率过高 (${DISK_USAGE}% > ${DISK_THRESHOLD}%)"
fi

echo "===================================="
```

---

### 告警脚本

**用途**: 发送告警通知

```bash
#!/bin/bash
# send_alert.sh - 告警通知脚本
# Usage: bash send_alert.sh "告警消息"

MESSAGE=$1

if [ -z "$MESSAGE" ]; then
    echo "Usage: $0 \"alert message\""
    exit 1
fi

# 配置
WEBHOOK_URL="https://your-webhook-url"

# 发送到企业微信/钉钉
curl -X POST $WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d "{
        \"msgtype\": \"text\",
        \"text\": {
            \"content\": \"【系统告警】\n$MESSAGE\n时间: $(date)\"
        }
    }"

echo "告警已发送"
```

---

## 运维工具脚本

### 批量操作脚本

**用途**: 批量操作多台服务器

```bash
#!/bin/bash
# batch_ssh.sh - 批量SSH执行命令
# Usage: bash batch_ssh.sh "command"

COMMAND=$1
HOSTS_FILE="hosts.txt"  # 每行一个IP或主机名

if [ -z "$COMMAND" ]; then
    echo "Usage: $0 \"command\""
    exit 1
fi

if [ ! -f "$HOSTS_FILE" ]; then
    echo "主机列表文件不存在: $HOSTS_FILE"
    exit 1
fi

echo "========== 批量执行命令 =========="
echo "命令: $COMMAND"
echo "=================================="

while IFS= read -r HOST; do
    echo ""
    echo ">>> $HOST"
    ssh -o StrictHostKeyChecking=no $HOST "$COMMAND"
done < "$HOSTS_FILE"

echo ""
echo "========== 执行完成 =========="
```

---

### 日志分析脚本

**用途**: 分析日志文件

```bash
#!/bin/bash
# analyze_log.sh - 日志分析脚本
# Usage: bash analyze_log.sh <log-file>

LOG_FILE=$1

if [ -z "$LOG_FILE" ] || [ ! -f "$LOG_FILE" ]; then
    echo "Usage: $0 <log-file>"
    exit 1
fi

echo "========== 日志分析: $LOG_FILE =========="
echo ""

# 总行数
TOTAL_LINES=$(wc -l < $LOG_FILE)
echo "总行数: $TOTAL_LINES"

# 错误统计
ERROR_COUNT=$(grep -ci "error" $LOG_FILE || true)
echo "错误数量: $ERROR_COUNT"

# 警告统计
WARN_COUNT=$(grep -ci "warn" $LOG_FILE || true)
echo "警告数量: $WARN_COUNT"

# 最近10条错误
echo ""
echo "========== 最近10条错误 =========="
grep -i "error" $LOG_FILE | tail -10

echo ""
echo "========== IP访问统计TOP10 =========="
awk '{print $1}' $LOG_FILE | sort | uniq -c | sort -rn | head -10

echo ""
echo "========== 状态码统计 =========="
awk '{print $9}' $LOG_FILE | sort | uniq -c | sort -rn

echo ""
echo "========== 分析完成 =========="
```

---

## 配置文件模板

### Docker Compose模板

**用途**: 标准的Docker Compose配置模板

```yaml
version: '3.8'

services:
  # Web应用
  web:
    image: nginx:latest
    container_name: web
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./html:/usr/share/nginx/html:ro
      - ./logs:/var/log/nginx
    networks:
      - app-network
    depends_on:
      - app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # 应用服务
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: app
    restart: always
    ports:
      - "8080:8080"
    environment:
      - APP_ENV=production
      - DB_HOST=db
      - DB_PORT=3306
      - DB_NAME=myapp
      - DB_USER=appuser
      - DB_PASSWORD_FILE=/run/secrets/db_password
    volumes:
      - ./app:/app
      - app-data:/data
    networks:
      - app-network
    depends_on:
      - db
      - redis
    secrets:
      - db_password
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  # 数据库
  db:
    image: mysql:8.0
    container_name: db
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD_FILE=/run/secrets/db_root_password
      - MYSQL_DATABASE=myapp
      - MYSQL_USER=appuser
      - MYSQL_PASSWORD_FILE=/run/secrets/db_password
    volumes:
      - db-data:/var/lib/mysql
      - ./initdb.d:/docker-entrypoint-initdb.d:ro
    networks:
      - app-network
    secrets:
      - db_root_password
      - db_password
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

  # 缓存
  redis:
    image: redis:7-alpine
    container_name: redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - app-network
    command: redis-server --appendonly yes

volumes:
  app-data:
  db-data:
  redis-data:

networks:
  app-network:
    driver: bridge

secrets:
  db_root_password:
    file: ./secrets/db_root_password.txt
  db_password:
    file: ./secrets/db_password.txt
```

---

### Kubernetes清单模板

**用途**: 标准的Kubernetes应用清单

```yaml
---
# Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
  labels:
    name: myapp

---
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
  namespace: myapp
data:
  app.conf: |
    server {
        listen 80;
        location / {
            proxy_pass http://myapp-service:8080;
        }
    }

---
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secret
  namespace: myapp
type: Opaque
data:
  db-password: cGFzc3dvcmQ=  # base64编码

---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: DB_HOST
          value: mysql-service
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: myapp-secret
              key: db-password
        volumeMounts:
        - name: config
          mountPath: /etc/myapp
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: myapp-config

---
# Service
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: myapp
spec:
  selector:
    app: myapp
  ports:
  - name: http
    port: 8080
    targetPort: 8080
  type: ClusterIP

---
# Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: myapp
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-service
            port:
              number: 8080

---
# HorizontalPodAutoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
  namespace: myapp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

### Prometheus配置模板

**用途**: Prometheus监控配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'prod'
    region: 'us-west-2'

# Alertmanager配置
alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093

# 规则文件
rule_files:
  - "alerts/*.yml"

# 抓取配置
scrape_configs:
  # Prometheus自身
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']

  # Node Exporter
  - job_name: 'node'
    static_configs:
    - targets:
      - 'node1:9100'
      - 'node2:9100'
      - 'node3:9100'

  # Kubernetes服务发现
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:$2
      target_label: __address__

  # Docker容器
  - job_name: 'docker'
    static_configs:
    - targets: ['cadvisor:8080']
```

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19  
**维护状态**: ✅ 完成

---

> 💡 **提示**:
>
> - 所有脚本使用前请先在测试环境验证
> - 根据实际环境修改脚本中的配置参数
> - 定期备份重要数据和配置
> - 使用版本控制管理脚本和配置文件
