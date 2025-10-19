# Kubernetes高可用架构

> **返回**: [高可用容灾目录](README.md) | [虚拟化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Kubernetes高可用架构](#kubernetes高可用架构)
  - [📋 目录](#-目录)
  - [1. Kubernetes HA概述](#1-kubernetes-ha概述)
  - [2. 控制平面高可用](#2-控制平面高可用)
    - [2.1 使用kubeadm部署HA集群](#21-使用kubeadm部署ha集群)
    - [2.2 手动部署HA集群 (外部etcd)](#22-手动部署ha集群-外部etcd)
  - [3. etcd集群高可用](#3-etcd集群高可用)
    - [3.1 etcd维护与监控](#31-etcd维护与监控)
    - [3.2 etcd故障恢复](#32-etcd故障恢复)
  - [4. 工作节点高可用](#4-工作节点高可用)
    - [4.1 配置Pod反亲和性](#41-配置pod反亲和性)
  - [5. 负载均衡配置](#5-负载均衡配置)
    - [5.1 Keepalived + HAProxy配置](#51-keepalived--haproxy配置)
  - [6. 应用高可用](#6-应用高可用)
    - [6.1 应用高可用配置示例](#61-应用高可用配置示例)
  - [7. 存储高可用](#7-存储高可用)
    - [7.1 Ceph RBD StorageClass配置](#71-ceph-rbd-storageclass配置)
  - [8. 监控与故障恢复](#8-监控与故障恢复)
    - [8.1 Prometheus告警规则](#81-prometheus告警规则)
    - [8.2 故障恢复脚本](#82-故障恢复脚本)
  - [9. 最佳实践](#9-最佳实践)
  - [相关文档](#相关文档)

---

## 1. Kubernetes HA概述

```yaml
Kubernetes_HA_Overview:
  架构组件:
    控制平面 (Control Plane):
      - kube-apiserver: API服务器 (可多实例)
      - kube-controller-manager: 控制器管理器
      - kube-scheduler: 调度器
      - etcd: 分布式键值存储
    
    工作节点 (Worker Nodes):
      - kubelet: 节点代理
      - kube-proxy: 网络代理
      - 容器运行时: containerd/CRI-O/Docker
    
    负载均衡:
      - 外部LB: HAProxy/Nginx/F5/云LB
      - 内部LB: kube-proxy (Service)
  
  高可用策略:
    控制平面HA:
      - 至少3个Master节点 (奇数)
      - API Server多实例主动-主动
      - Controller Manager/Scheduler主备模式
      - 负载均衡分发API请求
    
    etcd HA:
      - 至少3节点集群 (推荐5节点)
      - Raft共识算法
      - 自动Leader选举
      - 数据多副本
    
    工作节点HA:
      - 多副本Pod部署
      - 节点故障自动重新调度
      - 健康检查与自愈
    
    应用HA:
      - Deployment/StatefulSet多副本
      - Pod亲和性与反亲和性
      - PodDisruptionBudget (PDB)
      - HPA自动扩缩容

HA拓扑模式:
  堆叠etcd拓扑 (Stacked etcd):
    架构:
      - etcd与控制平面组件共享节点
      - 每个Master节点运行etcd
    
    优点:
      - 部署简单
      - 资源需求较少
      - 管理方便
    
    缺点:
      - 控制平面与etcd耦合
      - 单节点故障影响更大
      - 不适合超大规模集群
    
    适用场景:
      - 中小型集群 (< 100节点)
      - 资源有限
      - 简化管理
  
  外部etcd拓扑 (External etcd):
    架构:
      - etcd独立集群
      - 控制平面单独部署
    
    优点:
      - 解耦控制平面与etcd
      - 更高可靠性
      - 独立扩展
      - 适合大规模集群
    
    缺点:
      - 部署复杂
      - 资源需求高
      - 管理复杂
    
    适用场景:
      - 大型集群 (> 100节点)
      - 生产环境
      - 高可用要求

HA集群规模建议:
  小型HA (测试/开发):
    Master: 3节点
    Worker: 3-10节点
    etcd: 3节点 (堆叠)
    
  中型HA (生产):
    Master: 3节点
    Worker: 10-50节点
    etcd: 3-5节点 (堆叠或外部)
    
  大型HA (企业生产):
    Master: 3-5节点
    Worker: 50-500节点
    etcd: 5节点 (外部)
```

---

## 2. 控制平面高可用

```yaml
Control_Plane_HA:
  kube-apiserver:
    特点:
      - 无状态服务
      - 可多实例运行
      - 主动-主动模式
      - 通过LB分发请求
    
    部署方式:
      - 每个Master节点运行1个实例
      - 监听不同IP (节点IP)
      - 共享同一端口 (6443)
      - 前端LB负载均衡
    
    配置示例:
      - --advertise-address=<NodeIP>
      - --secure-port=6443
      - --etcd-servers=<etcd集群地址>
      - --service-cluster-ip-range=10.96.0.0/12
  
  kube-controller-manager:
    特点:
      - 有状态服务
      - 主备模式 (Leader Election)
      - 同时只有1个实例活动
      - 自动故障切换
    
    Leader选举:
      - 通过etcd或K8s Lease实现
      - 租约机制
      - 心跳续约
      - 故障自动切换
    
    配置示例:
      - --leader-elect=true
      - --leader-elect-lease-duration=15s
      - --leader-elect-renew-deadline=10s
      - --leader-elect-retry-period=2s
  
  kube-scheduler:
    特点:
      - 有状态服务
      - 主备模式 (Leader Election)
      - 同时只有1个实例活动
      - 调度决策需要一致性
    
    配置:
      与controller-manager类似
      使用Leader Election

控制平面部署脚本:
  SystemD服务:
    kube-apiserver.service:
      - 多实例同时运行
      - 监听本地IP
      - 连接etcd集群
    
    kube-controller-manager.service:
      - 启用Leader选举
      - 连接本地API Server
      - 自动故障切换
    
    kube-scheduler.service:
      - 启用Leader选举
      - 连接本地API Server
      - 自动故障切换
```

### 2.1 使用kubeadm部署HA集群

```bash
#!/bin/bash
# ========================================
# kubeadm部署K8s HA集群 (堆叠etcd)
# ========================================

# 环境规划:
# - 3个Master节点 (master01/02/03)
# - 3个Worker节点 (worker01/02/03)
# - 1个负载均衡器 (HAProxy)

# ========================================
# 准备工作 (所有节点)
# ========================================

# 1. 系统配置
cat <<EOF | tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

modprobe overlay
modprobe br_netfilter

cat <<EOF | tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sysctl --system

# 2. 禁用swap
swapoff -a
sed -i '/ swap / s/^/#/' /etc/fstab

# 3. 安装容器运行时 (containerd)
apt update
apt install -y containerd

mkdir -p /etc/containerd
containerd config default > /etc/containerd/config.toml

# 配置containerd使用systemd cgroup driver
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

systemctl restart containerd
systemctl enable containerd

# 4. 安装kubeadm, kubelet, kubectl
apt update
apt install -y apt-transport-https ca-certificates curl

curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg

echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] \
    https://apt.kubernetes.io/ kubernetes-xenial main" | \
    tee /etc/apt/sources.list.d/kubernetes.list

apt update
apt install -y kubelet=1.28.0-00 kubeadm=1.28.0-00 kubectl=1.28.0-00
apt-mark hold kubelet kubeadm kubectl

systemctl enable kubelet

# ========================================
# 配置负载均衡器 (HAProxy节点)
# ========================================

# 安装HAProxy
apt install -y haproxy

# 配置HAProxy
cat > /etc/haproxy/haproxy.cfg << 'EOF'
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000

# Kubernetes API Server Frontend
frontend k8s-api
    bind *:6443
    mode tcp
    option tcplog
    default_backend k8s-api-backend

# Kubernetes API Server Backend
backend k8s-api-backend
    mode tcp
    balance roundrobin
    option tcp-check
    server master01 192.168.10.101:6443 check fall 3 rise 2
    server master02 192.168.10.102:6443 check fall 3 rise 2
    server master03 192.168.10.103:6443 check fall 3 rise 2

# Stats页面
listen stats
    bind *:8080
    mode http
    stats enable
    stats uri /stats
    stats refresh 30s
    stats realm HAProxy\ Statistics
    stats auth admin:admin
EOF

# 启动HAProxy
systemctl restart haproxy
systemctl enable haproxy

# 验证HAProxy
curl http://localhost:8080/stats

# ========================================
# 初始化第一个Master节点 (master01)
# ========================================

# 创建kubeadm配置文件
cat > kubeadm-config.yaml << 'EOF'
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v1.28.0
controlPlaneEndpoint: "192.168.10.100:6443"  # HAProxy VIP
networking:
  serviceSubnet: "10.96.0.0/12"
  podSubnet: "10.244.0.0/16"
apiServer:
  certSANs:
    - "192.168.10.100"  # HAProxy VIP
    - "192.168.10.101"  # master01
    - "192.168.10.102"  # master02
    - "192.168.10.103"  # master03
    - "master01"
    - "master02"
    - "master03"
    - "k8s-api.example.com"
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: "192.168.10.101"  # master01 IP
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///var/run/containerd/containerd.sock
  taints:
    - key: node-role.kubernetes.io/control-plane
      effect: NoSchedule
EOF

# 初始化集群
kubeadm init --config=kubeadm-config.yaml --upload-certs

# 配置kubectl (master01)
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

# 保存join命令 (用于其他节点加入)
# kubeadm会输出类似以下命令:

# Master节点加入命令:
# kubeadm join 192.168.10.100:6443 --token <token> \
#     --discovery-token-ca-cert-hash sha256:<hash> \
#     --control-plane --certificate-key <cert-key>

# Worker节点加入命令:
# kubeadm join 192.168.10.100:6443 --token <token> \
#     --discovery-token-ca-cert-hash sha256:<hash>

# 安装CNI网络插件 (Calico)
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# 验证第一个Master节点
kubectl get nodes
kubectl get pods -A

# ========================================
# 加入其他Master节点 (master02, master03)
# ========================================

# 在master02和master03上执行 (使用上面保存的join命令):
kubeadm join 192.168.10.100:6443 --token <token> \
    --discovery-token-ca-cert-hash sha256:<hash> \
    --control-plane --certificate-key <cert-key> \
    --apiserver-advertise-address=<master0X-IP>

# 配置kubectl (master02, master03)
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

# ========================================
# 加入Worker节点 (worker01/02/03)
# ========================================

# 在所有Worker节点上执行:
kubeadm join 192.168.10.100:6443 --token <token> \
    --discovery-token-ca-cert-hash sha256:<hash>

# ========================================
# 验证集群
# ========================================

# 检查所有节点
kubectl get nodes
# 应该看到3个Master节点和3个Worker节点都是Ready状态

# 检查控制平面组件
kubectl get pods -n kube-system
# 应该看到:
# - 每个Master节点上: kube-apiserver, kube-controller-manager, kube-scheduler, etcd
# - 所有节点: calico, kube-proxy, coredns

# 检查etcd集群健康
kubectl exec -n kube-system etcd-master01 -- etcdctl \
    --endpoints=https://127.0.0.1:2379 \
    --cacert=/etc/kubernetes/pki/etcd/ca.crt \
    --cert=/etc/kubernetes/pki/etcd/server.crt \
    --key=/etc/kubernetes/pki/etcd/server.key \
    endpoint health

# 检查Leader选举
kubectl get lease -n kube-system
# 应该看到kube-controller-manager和kube-scheduler的lease

echo "✅ Kubernetes HA集群部署完成"
```

### 2.2 手动部署HA集群 (外部etcd)

```bash
#!/bin/bash
# ========================================
# 手动部署K8s HA集群 (外部etcd)
# ========================================

# 架构:
# - 3个独立etcd节点 (etcd01/02/03)
# - 3个Master节点 (master01/02/03)
# - 3个Worker节点 (worker01/02/03)

# ========================================
# 1. 部署独立etcd集群
# ========================================

# 在etcd01节点:
ETCD_NAME=etcd01
ETCD_IP=192.168.10.201
INITIAL_CLUSTER="etcd01=https://192.168.10.201:2380,etcd02=https://192.168.10.202:2380,etcd03=https://192.168.10.203:2380"

# 下载etcd
ETCD_VER=v3.5.10
wget https://github.com/etcd-io/etcd/releases/download/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz
tar xzf etcd-${ETCD_VER}-linux-amd64.tar.gz
cp etcd-${ETCD_VER}-linux-amd64/etcd* /usr/local/bin/

# 生成证书 (使用cfssl或openssl)
# ... (证书生成步骤略)

# 创建etcd systemd服务
cat > /etc/systemd/system/etcd.service << EOF
[Unit]
Description=etcd
Documentation=https://github.com/etcd-io/etcd

[Service]
Type=notify
ExecStart=/usr/local/bin/etcd \\
  --name ${ETCD_NAME} \\
  --cert-file=/etc/etcd/ssl/server.pem \\
  --key-file=/etc/etcd/ssl/server-key.pem \\
  --peer-cert-file=/etc/etcd/ssl/peer.pem \\
  --peer-key-file=/etc/etcd/ssl/peer-key.pem \\
  --trusted-ca-file=/etc/etcd/ssl/ca.pem \\
  --peer-trusted-ca-file=/etc/etcd/ssl/ca.pem \\
  --peer-client-cert-auth \\
  --client-cert-auth \\
  --initial-advertise-peer-urls https://${ETCD_IP}:2380 \\
  --listen-peer-urls https://${ETCD_IP}:2380 \\
  --listen-client-urls https://${ETCD_IP}:2379,https://127.0.0.1:2379 \\
  --advertise-client-urls https://${ETCD_IP}:2379 \\
  --initial-cluster-token etcd-cluster-1 \\
  --initial-cluster ${INITIAL_CLUSTER} \\
  --initial-cluster-state new \\
  --data-dir=/var/lib/etcd
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable etcd
systemctl start etcd

# 在etcd02和etcd03重复上述步骤 (修改ETCD_NAME和ETCD_IP)

# 验证etcd集群
etcdctl --endpoints=https://192.168.10.201:2379,https://192.168.10.202:2379,https://192.168.10.203:2379 \
    --cacert=/etc/etcd/ssl/ca.pem \
    --cert=/etc/etcd/ssl/server.pem \
    --key=/etc/etcd/ssl/server-key.pem \
    endpoint health

# ========================================
# 2. 部署Kubernetes控制平面 (master01)
# ========================================

# kubeadm配置文件 (外部etcd)
cat > kubeadm-config-external-etcd.yaml << 'EOF'
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v1.28.0
controlPlaneEndpoint: "192.168.10.100:6443"
networking:
  serviceSubnet: "10.96.0.0/12"
  podSubnet: "10.244.0.0/16"
etcd:
  external:
    endpoints:
      - https://192.168.10.201:2379
      - https://192.168.10.202:2379
      - https://192.168.10.203:2379
    caFile: /etc/kubernetes/pki/etcd/ca.crt
    certFile: /etc/kubernetes/pki/apiserver-etcd-client.crt
    keyFile: /etc/kubernetes/pki/apiserver-etcd-client.key
apiServer:
  certSANs:
    - "192.168.10.100"
    - "192.168.10.101"
    - "192.168.10.102"
    - "192.168.10.103"
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: "192.168.10.101"
  bindPort: 6443
EOF

# 初始化
kubeadm init --config=kubeadm-config-external-etcd.yaml --upload-certs

# 配置kubectl
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config

# 安装CNI
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# 其他Master节点加入 (master02, master03)
# ... (使用kubeadm join命令)

echo "✅ 外部etcd模式K8s HA集群部署完成"
```

---

## 3. etcd集群高可用

```yaml
etcd_HA:
  架构特点:
    - 分布式键值存储
    - Raft共识算法
    - Leader选举
    - 强一致性
  
  集群规模:
    3节点:
      - 最小HA配置
      - 容忍1个节点故障
      - 推荐中小型集群
    
    5节点:
      - 推荐生产配置
      - 容忍2个节点故障
      - 更高可用性
      - 推荐大型集群
    
    7节点:
      - 超大规模集群
      - 容忍3个节点故障
      - 注意性能开销
  
  Raft共识:
    角色:
      Leader:
        - 处理所有写请求
        - 同步到Follower
        - 发送心跳
      
      Follower:
        - 接收Leader日志
        - 参与选举
        - 转发写请求到Leader
      
      Candidate:
        - 选举中的临时角色
    
    选举过程:
      1. Follower超时未收到心跳
      2. 转变为Candidate
      3. 请求其他节点投票
      4. 获得多数票成为Leader
      5. 开始发送心跳
    
    数据一致性:
      - 日志复制
      - 多数派确认
      - 写入持久化
      - 读取一致性保证

etcd配置优化:
  性能调优:
    --heartbeat-interval: 100      # 心跳间隔 (ms)
    --election-timeout: 1000        # 选举超时 (ms)
    --snapshot-count: 10000         # 快照触发阈值
    --quota-backend-bytes: 8589934592  # 8GB存储配额
  
  网络配置:
    - 专用网络
    - 低延迟 (<5ms)
    - 高带宽 (1Gbps+)
    - 防火墙开放端口 (2379, 2380)
  
  磁盘配置:
    - SSD磁盘 (推荐NVMe)
    - 独立磁盘 (不与其他IO竞争)
    - 低延迟 (<10ms)
    - 高IOPS
  
  备份策略:
    定期备份:
      - 每天全量备份
      - 保留7天
      - 异地存储
    
    快照备份:
      - 自动快照
      - 增量备份
      - 快速恢复
```

### 3.1 etcd维护与监控

```bash
#!/bin/bash
# ========================================
# etcd集群维护脚本
# ========================================

ETCDCTL_API=3
ENDPOINTS="https://192.168.10.201:2379,https://192.168.10.202:2379,https://192.168.10.203:2379"
CACERT="/etc/etcd/ssl/ca.pem"
CERT="/etc/etcd/ssl/server.pem"
KEY="/etc/etcd/ssl/server-key.pem"

# 1. 健康检查
echo "=== etcd健康检查 ==="
etcdctl --endpoints=$ENDPOINTS \
    --cacert=$CACERT --cert=$CERT --key=$KEY \
    endpoint health

# 2. 成员列表
echo -e "\n=== etcd成员列表 ==="
etcdctl --endpoints=$ENDPOINTS \
    --cacert=$CACERT --cert=$CERT --key=$KEY \
    member list -w table

# 3. Leader查询
echo -e "\n=== etcd Leader ==="
etcdctl --endpoints=$ENDPOINTS \
    --cacert=$CACERT --cert=$CERT --key=$KEY \
    endpoint status -w table

# 4. 性能监控
echo -e "\n=== etcd性能指标 ==="
etcdctl --endpoints=$ENDPOINTS \
    --cacert=$CACERT --cert=$CERT --key=$KEY \
    endpoint status --write-out=table

# 5. 碎片整理
echo -e "\n=== 碎片整理 (定期执行) ==="
for endpoint in $(echo $ENDPOINTS | tr ',' ' '); do
    echo "Defragmenting $endpoint"
    etcdctl --endpoints=$endpoint \
        --cacert=$CACERT --cert=$CERT --key=$KEY \
        defrag
done

# 6. 快照备份
echo -e "\n=== 创建快照备份 ==="
BACKUP_DIR="/backup/etcd"
BACKUP_FILE="$BACKUP_DIR/etcd-snapshot-$(date +%Y%m%d-%H%M%S).db"

mkdir -p $BACKUP_DIR
etcdctl --endpoints=$ENDPOINTS \
    --cacert=$CACERT --cert=$CERT --key=$KEY \
    snapshot save $BACKUP_FILE

# 验证快照
etcdctl --write-out=table snapshot status $BACKUP_FILE

# 7. 数据库大小
echo -e "\n=== etcd数据库大小 ==="
etcdctl --endpoints=$ENDPOINTS \
    --cacert=$CACERT --cert=$CERT --key=$KEY \
    endpoint status -w table | awk '{print $3, $5}'

echo "✅ etcd维护完成"
```

### 3.2 etcd故障恢复

```bash
#!/bin/bash
# ========================================
# etcd灾难恢复
# ========================================

# 场景1: 单个节点故障
# 如果节点可恢复，直接重启etcd服务
systemctl restart etcd

# 如果节点不可恢复，移除故障节点并添加新节点
# 1. 移除故障节点
etcdctl member remove <member-id>

# 2. 添加新节点
etcdctl member add etcd-new \
    --peer-urls=https://192.168.10.204:2380

# 3. 在新节点启动etcd (使用--initial-cluster-state existing)

# 场景2: 多数节点故障 (需要从快照恢复)
# 1. 停止所有etcd节点
systemctl stop etcd

# 2. 从快照恢复 (在每个节点执行)
ETCD_NAME=etcd01
ETCD_INITIAL_CLUSTER="etcd01=https://192.168.10.201:2380,etcd02=https://192.168.10.202:2380,etcd03=https://192.168.10.203:2380"
SNAPSHOT_FILE="/backup/etcd/etcd-snapshot-20251019.db"

etcdctl snapshot restore $SNAPSHOT_FILE \
    --name $ETCD_NAME \
    --initial-cluster $ETCD_INITIAL_CLUSTER \
    --initial-cluster-token etcd-cluster-1 \
    --initial-advertise-peer-urls https://192.168.10.201:2380 \
    --data-dir /var/lib/etcd-restore

# 3. 替换数据目录
rm -rf /var/lib/etcd
mv /var/lib/etcd-restore /var/lib/etcd

# 4. 启动etcd
systemctl start etcd

# 5. 验证恢复
etcdctl endpoint health

echo "✅ etcd恢复完成"
```

---

## 4. 工作节点高可用

```yaml
Worker_Node_HA:
  节点冗余:
    最小配置:
      - 至少3个Worker节点
      - N+1冗余
      - 负载分散
    
    推荐配置:
      - 5个以上Worker节点
      - N+2冗余
      - 更高容错能力
  
  Pod高可用:
    副本数:
      - Deployment: replicas >= 2
      - StatefulSet: replicas >= 2
      - DaemonSet: 每节点1个
    
    分布策略:
      podAntiAffinity:
        - preferredDuringSchedulingIgnoredDuringExecution
        - requiredDuringSchedulingIgnoredDuringExecution
      
      topologySpreadConstraints:
        - 跨可用区分布
        - 跨节点分布
        - 均匀分布
    
    PodDisruptionBudget (PDB):
      - minAvailable: 最少可用Pod数
      - maxUnavailable: 最多不可用Pod数
      - 保护应用可用性
      - 控制滚动更新速度
  
  健康检查:
    livenessProbe:
      - 检测Pod存活
      - 失败则重启Pod
      - HTTP/TCP/Exec探测
    
    readinessProbe:
      - 检测Pod就绪
      - 未就绪则移出Service
      - 流量隔离
    
    startupProbe:
      - 检测应用启动
      - 慢启动应用
      - 避免过早检查

节点故障处理:
  故障检测:
    kubelet心跳:
      - 默认10秒
      - node-status-update-frequency
    
    节点状态:
      - Ready: 正常
      - NotReady: 故障
      - Unknown: 失联
  
  Pod驱逐:
    驱逐条件:
      - 节点NotReady超过40秒
      - --pod-eviction-timeout=5m (已废弃)
    
    驱逐行为:
      - Pod标记为Terminating
      - 在其他节点重新创建
      - StatefulSet按序重建
  
  节点恢复:
    自动恢复:
      - 节点重启后自动加入
      - Pod自动调度回来 (如果仍需要)
    
    手动干预:
      - 检查节点状态
      - 清理故障Pod
      - 验证集群健康
```

### 4.1 配置Pod反亲和性

```yaml
# ========================================
# Deployment with Pod Anti-Affinity
# ========================================
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      # Pod反亲和性 (强制)
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchExpressions:
                  - key: app
                    operator: In
                    values:
                      - web
              topologyKey: kubernetes.io/hostname
      
      containers:
        - name: web
          image: nginx:1.25
          ports:
            - containerPort: 80
          
          # 健康检查
          livenessProbe:
            httpGet:
              path: /healthz
              port: 80
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          
          readinessProbe:
            httpGet:
              path: /ready
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi

---
# ========================================
# PodDisruptionBudget
# ========================================
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
spec:
  minAvailable: 2  # 至少保持2个Pod可用
  selector:
    matchLabels:
      app: web

---
# ========================================
# Topology Spread Constraints
# ========================================
apiVersion: apps/v1
kind: Deployment
metadata:
  name: distributed-app
spec:
  replicas: 6
  selector:
    matchLabels:
      app: distributed
  template:
    metadata:
      labels:
        app: distributed
    spec:
      # 拓扑分布约束
      topologySpreadConstraints:
        # 跨节点均匀分布
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: distributed
        
        # 跨可用区分布
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app: distributed
      
      containers:
        - name: app
          image: myapp:latest
          ports:
            - containerPort: 8080
```

---

## 5. 负载均衡配置

```yaml
Load_Balancer_Types:
  外部负载均衡:
    用途: 分发API Server请求
    
    HAProxy:
      优点:
        - 开源免费
        - 高性能
        - 灵活配置
        - TCP/HTTP支持
      
      配置:
        - frontend监听6443
        - backend多个API Server
        - 健康检查
        - 会话保持
    
    Nginx:
      优点:
        - 成熟稳定
        - 易于配置
        - stream模块支持TCP
      
      配置:
        - stream块配置
        - upstream多个API Server
        - 健康检查
    
    云LB:
      - AWS ELB/NLB
      - Azure Load Balancer
      - GCP Load Balancer
      - 自动故障切换
      - 高可用性
  
  内部负载均衡:
    kube-proxy:
      模式:
        iptables:
          - 默认模式
          - 基于iptables规则
          - 随机负载均衡
        
        ipvs:
          - 高性能
          - 多种负载均衡算法
          - 推荐大规模集群
        
        userspace:
          - 已废弃
          - 性能较差
      
      Service类型:
        ClusterIP:
          - 集群内部访问
          - 虚拟IP
          - 负载均衡
        
        NodePort:
          - 节点端口暴露
          - 外部访问
          - 自动负载均衡
        
        LoadBalancer:
          - 云环境
          - 外部LB集成
          - 自动配置

Keepalived + HAProxy HA:
  架构:
    - 2个HAProxy节点
    - Keepalived提供VIP
    - VRRP协议
    - 自动故障切换
  
  VIP (Virtual IP):
    - 192.168.10.100
    - 浮动IP
    - Master持有
    - Backup自动接管
```

### 5.1 Keepalived + HAProxy配置

```bash
#!/bin/bash
# ========================================
# Keepalived + HAProxy HA配置
# ========================================

# 在HAProxy-01 (Master)节点

# 1. 安装软件
apt install -y haproxy keepalived

# 2. 配置HAProxy (与前面相同)
cat > /etc/haproxy/haproxy.cfg << 'EOF'
# ... (HAProxy配置，见前面章节)
EOF

# 3. 配置Keepalived (Master)
cat > /etc/keepalived/keepalived.conf << 'EOF'
global_defs {
    router_id LB-MASTER
}

vrrp_script check_haproxy {
    script "/usr/bin/killall -0 haproxy"
    interval 2
    weight -5
    fall 2
    rise 2
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    
    authentication {
        auth_type PASS
        auth_pass K8s@2025
    }
    
    virtual_ipaddress {
        192.168.10.100/24
    }
    
    track_script {
        check_haproxy
    }
    
    notify_master "/etc/keepalived/notify.sh MASTER"
    notify_backup "/etc/keepalived/notify.sh BACKUP"
    notify_fault "/etc/keepalived/notify.sh FAULT"
}
EOF

# 4. 创建通知脚本
cat > /etc/keepalived/notify.sh << 'EOF'
#!/bin/bash
TYPE=$1
NAME=$2
STATE=$3

case $STATE in
    "MASTER") echo "$(date) - Became MASTER" >> /var/log/keepalived-notify.log
              ;;
    "BACKUP") echo "$(date) - Became BACKUP" >> /var/log/keepalived-notify.log
              ;;
    "FAULT")  echo "$(date) - Fault detected" >> /var/log/keepalived-notify.log
              ;;
    *)        echo "$(date) - Unknown state: $STATE" >> /var/log/keepalived-notify.log
              ;;
esac
EOF

chmod +x /etc/keepalived/notify.sh

# 5. 启动服务
systemctl restart haproxy
systemctl enable haproxy

systemctl restart keepalived
systemctl enable keepalived

# 6. 验证VIP
ip addr show eth0
# 应该看到192.168.10.100

# ========================================
# 在HAProxy-02 (Backup)节点
# ========================================

# 安装软件 (同Master)
apt install -y haproxy keepalived

# 配置HAProxy (同Master)
# ...

# 配置Keepalived (Backup - priority较低)
cat > /etc/keepalived/keepalived.conf << 'EOF'
global_defs {
    router_id LB-BACKUP
}

vrrp_script check_haproxy {
    script "/usr/bin/killall -0 haproxy"
    interval 2
    weight -5
    fall 2
    rise 2
}

vrrp_instance VI_1 {
    state BACKUP
    interface eth0
    virtual_router_id 51
    priority 90  # 低于Master
    advert_int 1
    
    authentication {
        auth_type PASS
        auth_pass K8s@2025
    }
    
    virtual_ipaddress {
        192.168.10.100/24
    }
    
    track_script {
        check_haproxy
    }
    
    notify_master "/etc/keepalived/notify.sh MASTER"
    notify_backup "/etc/keepalived/notify.sh BACKUP"
    notify_fault "/etc/keepalived/notify.sh FAULT"
}
EOF

# 通知脚本 (同Master)
# ...

# 启动服务
systemctl restart haproxy keepalived
systemctl enable haproxy keepalived

# ========================================
# 测试故障切换
# ========================================

# 在Master节点停止HAProxy
systemctl stop haproxy

# 在Backup节点检查VIP是否漂移
ip addr show eth0
# 应该看到192.168.10.100已经在Backup节点

# 恢复Master节点
systemctl start haproxy
# VIP应该自动漂回Master (如果配置了抢占)

echo "✅ Keepalived + HAProxy HA配置完成"
```

---

## 6. 应用高可用

```yaml
Application_HA_Strategies:
  无状态应用:
    Deployment:
      - 多副本部署
      - 滚动更新
      - 自动重启
      - 健康检查
    
    HPA (Horizontal Pod Autoscaler):
      - CPU/内存自动扩缩容
      - 自定义指标扩缩容
      - 最小/最大副本数
      - 扩缩容策略
    
    配置示例:
      replicas: 3
      strategy:
        rollingUpdate:
          maxSurge: 1
          maxUnavailable: 0
      
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
  
  有状态应用:
    StatefulSet:
      - 稳定的网络标识
      - 有序部署和扩展
      - 持久化存储
      - 有序终止
    
    Headless Service:
      - DNS记录指向Pod
      - 稳定的网络身份
      - 支持主从架构
    
    持久化:
      - PVC/PV
      - StorageClass
      - 数据持久化
      - 备份恢复
  
  数据库HA:
    MySQL:
      - MySQL Group Replication
      - MySQL InnoDB Cluster
      - 或使用MySQL Operator
      - 主从复制
    
    PostgreSQL:
      - Patroni + etcd
      - Streaming Replication
      - Pgpool-II
      - Zalando Postgres Operator
    
    MongoDB:
      - Replica Set
      - Sharding
      - MongoDB Operator
      - 自动故障切换
    
    Redis:
      - Redis Sentinel
      - Redis Cluster
      - Redis Operator
      - 高可用性

服务发现与注册:
  Service:
    - ClusterIP (默认)
    - NodePort
    - LoadBalancer
    - ExternalName
  
  Endpoints:
    - 自动管理
    - 健康Pod
    - 负载均衡
  
  DNS:
    - CoreDNS
    - 服务发现
    - Pod DNS
    - 自动解析
```

### 6.1 应用高可用配置示例

```yaml
# ========================================
# 无状态应用 HA配置
# ========================================
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-ha
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  
  # 滚动更新策略
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 更新时最多额外创建1个Pod
      maxUnavailable: 0  # 更新时最多0个Pod不可用
  
  template:
    metadata:
      labels:
        app: nginx
    spec:
      # Pod反亲和性
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - nginx
                topologyKey: kubernetes.io/hostname
      
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
              name: http
          
          # 资源限制
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          
          # 存活探针
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            successThreshold: 1
            failureThreshold: 3
          
          # 就绪探针
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            successThreshold: 1
            failureThreshold: 3

---
# Service
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
  sessionAffinity: ClientIP  # 会话保持
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800

---
# PodDisruptionBudget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: nginx-pdb
spec:
  minAvailable: 2  # 至少2个Pod可用
  selector:
    matchLabels:
      app: nginx

---
# HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-ha
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5分钟稳定期
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
        - type: Pods
          value: 2
          periodSeconds: 30
      selectPolicy: Max

---
# ========================================
# 有状态应用 HA配置 (MySQL示例)
# ========================================
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  ports:
    - port: 3306
  clusterIP: None  # Headless Service
  selector:
    app: mysql

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  
  template:
    metadata:
      labels:
        app: mysql
    spec:
      initContainers:
        - name: init-mysql
          image: mysql:8.0
          command:
            - bash
            - "-c"
            - |
              set -ex
              # 根据Pod序号生成server-id
              [[ `hostname` =~ -([0-9]+)$ ]] || exit 1
              ordinal=${BASH_REMATCH[1]}
              echo [mysqld] > /mnt/conf.d/server-id.cnf
              echo server-id=$((100 + $ordinal)) >> /mnt/conf.d/server-id.cnf
              # 复制配置到正确位置
              if [[ $ordinal -eq 0 ]]; then
                cp /mnt/config-map/master.cnf /mnt/conf.d/
              else
                cp /mnt/config-map/slave.cnf /mnt/conf.d/
              fi
          volumeMounts:
            - name: conf
              mountPath: /mnt/conf.d
            - name: config-map
              mountPath: /mnt/config-map
      
      containers:
        - name: mysql
          image: mysql:8.0
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: password
          ports:
            - name: mysql
              containerPort: 3306
          
          volumeMounts:
            - name: data
              mountPath: /var/lib/mysql
              subPath: mysql
            - name: conf
              mountPath: /etc/mysql/conf.d
          
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 2000m
              memory: 4Gi
          
          livenessProbe:
            exec:
              command: ["mysqladmin", "ping"]
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
          
          readinessProbe:
            exec:
              command: ["mysql", "-h", "127.0.0.1", "-e", "SELECT 1"]
            initialDelaySeconds: 5
            periodSeconds: 2
            timeoutSeconds: 1
      
      volumes:
        - name: conf
          emptyDir: {}
        - name: config-map
          configMap:
            name: mysql-config
  
  # 持久化存储
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: "fast-ssd"
        resources:
          requests:
            storage: 10Gi
```

---

## 7. 存储高可用

```yaml
Storage_HA:
  持久化存储:
    本地存储:
      - Local PV
      - HostPath (不推荐生产)
      - 性能好
      - 无冗余
    
    网络存储:
      NFS:
        - ReadWriteMany
        - 共享存储
        - 简单易用
        - 性能一般
      
      iSCSI:
        - ReadWriteOnce
        - 块存储
        - 性能好
        - 需要多路径
      
      Ceph RBD:
        - 分布式存储
        - 高可用
        - 自动副本
        - 性能好
      
      云存储:
        - AWS EBS
        - Azure Disk
        - GCP Persistent Disk
        - 自动高可用
  
  StorageClass:
    动态配置:
      - 自动创建PV
      - 按需分配
      - 回收策略
    
    参数:
      - provisioner: 存储提供者
      - parameters: 存储参数
      - reclaimPolicy: Retain/Delete
      - volumeBindingMode: Immediate/WaitForFirstConsumer
  
  CSI (Container Storage Interface):
    优点:
      - 标准化接口
      - 插件化
      - 厂商中立
      - 功能丰富
    
    常用CSI:
      - Ceph CSI
      - NFS CSI
      - Local Path Provisioner
      - Cloud Provider CSI

备份策略:
  应用级备份:
    - Velero
    - 备份K8s资源
    - 备份PV数据
    - 灾难恢复
  
  存储级备份:
    - 存储快照
    - 定期备份
    - 异地复制
    - 快速恢复
```

### 7.1 Ceph RBD StorageClass配置

```yaml
# ========================================
# Ceph RBD StorageClass (高可用存储)
# ========================================
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ceph-rbd-ssd
provisioner: rbd.csi.ceph.com
parameters:
  clusterID: <ceph-cluster-id>
  pool: kubernetes
  imageFeatures: layering
  csi.storage.k8s.io/provisioner-secret-name: csi-rbd-secret
  csi.storage.k8s.io/provisioner-secret-namespace: ceph-csi
  csi.storage.k8s.io/controller-expand-secret-name: csi-rbd-secret
  csi.storage.k8s.io/controller-expand-secret-namespace: ceph-csi
  csi.storage.k8s.io/node-stage-secret-name: csi-rbd-secret
  csi.storage.k8s.io/node-stage-secret-namespace: ceph-csi
  csi.storage.k8s.io/fstype: ext4
reclaimPolicy: Retain  # 保留数据
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer

---
# ========================================
# NFS StorageClass (ReadWriteMany)
# ========================================
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-client
provisioner: cluster.local/nfs-client-provisioner
parameters:
  archiveOnDelete: "true"
reclaimPolicy: Retain
volumeBindingMode: Immediate

---
# ========================================
# Local Path Provisioner (本地SSD)
# ========================================
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-path
provisioner: rancher.io/local-path
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
```

---

## 8. 监控与故障恢复

```yaml
Monitoring_Stack:
  Prometheus:
    组件:
      - Prometheus Server: 指标收集和存储
      - Alertmanager: 告警管理
      - Node Exporter: 节点指标
      - kube-state-metrics: K8s对象指标
      - Grafana: 可视化
    
    关键指标:
      集群级别:
        - 节点状态
        - Pod状态
        - API Server请求速率
        - etcd性能
      
      节点级别:
        - CPU使用率
        - 内存使用率
        - 磁盘IO
        - 网络流量
      
      应用级别:
        - Pod重启次数
        - 容器CPU/内存
        - 请求延迟
        - 错误率
  
  日志聚合:
    EFK Stack:
      - Elasticsearch: 存储
      - Fluentd/Filebeat: 收集
      - Kibana: 查询分析
    
    Loki:
      - Promtail: 收集
      - Loki: 存储
      - Grafana: 查询
      - 轻量级

故障自愈:
  自动重启:
    - livenessProbe失败
    - 容器崩溃
    - OOM Killed
    - 自动重启Pod
  
  自动重新调度:
    - 节点故障
    - Pod被驱逐
    - 资源不足
    - 调度到其他节点
  
  自动扩缩容:
    - HPA (Pod自动扩缩容)
    - VPA (垂直扩缩容)
    - Cluster Autoscaler (节点自动扩缩容)
```

### 8.1 Prometheus告警规则

```yaml
# ========================================
# Prometheus AlertRules for K8s HA
# ========================================
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-rules
  namespace: monitoring
data:
  kubernetes.rules: |
    groups:
      - name: kubernetes-ha-alerts
        interval: 30s
        rules:
          # 节点故障告警
          - alert: NodeDown
            expr: up{job="node-exporter"} == 0
            for: 2m
            labels:
              severity: critical
            annotations:
              summary: "Node {{ $labels.instance }} is down"
              description: "Node {{ $labels.instance }} has been down for more than 2 minutes."
          
          # 节点资源告警
          - alert: NodeHighCPU
            expr: (100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)) > 80
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "Node {{ $labels.instance }} high CPU usage"
              description: "CPU usage is above 80% (current: {{ $value }}%)"
          
          - alert: NodeHighMemory
            expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "Node {{ $labels.instance }} high memory usage"
              description: "Memory usage is above 85% (current: {{ $value }}%)"
          
          # Pod故障告警
          - alert: PodCrashLooping
            expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash looping"
              description: "Pod {{ $labels.namespace }}/{{ $labels.pod }} is restarting {{ $value }} times per second."
          
          - alert: PodNotReady
            expr: kube_pod_status_phase{phase!="Running",phase!="Succeeded"} > 0
            for: 10m
            labels:
              severity: warning
            annotations:
              summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} not ready"
              description: "Pod has been in {{ $labels.phase }} state for more than 10 minutes."
          
          # API Server告警
          - alert: APIServerDown
            expr: up{job="kubernetes-apiservers"} == 0
            for: 1m
            labels:
              severity: critical
            annotations:
              summary: "API Server {{ $labels.instance }} is down"
              description: "API Server has been down for more than 1 minute."
          
          - alert: APIServerHighLatency
            expr: histogram_quantile(0.99, sum(rate(apiserver_request_duration_seconds_bucket{verb!~"WATCH"}[5m])) by (verb, le)) > 1
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "API Server high latency"
              description: "99th percentile latency is {{ $value }}s for {{ $labels.verb }} requests."
          
          # etcd告警
          - alert: etcdDown
            expr: up{job="etcd"} == 0
            for: 1m
            labels:
              severity: critical
            annotations:
              summary: "etcd {{ $labels.instance }} is down"
              description: "etcd instance has been down for more than 1 minute."
          
          - alert: etcdNoLeader
            expr: etcd_server_has_leader == 0
            for: 1m
            labels:
              severity: critical
            annotations:
              summary: "etcd cluster has no leader"
              description: "etcd cluster has no leader for more than 1 minute."
          
          - alert: etcdHighFsyncDuration
            expr: histogram_quantile(0.99, rate(etcd_disk_wal_fsync_duration_seconds_bucket[5m])) > 0.5
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "etcd high fsync duration"
              description: "99th percentile fsync duration is {{ $value }}s."
          
          # Deployment副本告警
          - alert: DeploymentReplicasMismatch
            expr: kube_deployment_spec_replicas != kube_deployment_status_replicas_available
            for: 10m
            labels:
              severity: warning
            annotations:
              summary: "Deployment {{ $labels.namespace }}/{{ $labels.deployment }} replicas mismatch"
              description: "Deployment has {{ $value }} available replicas, expected {{ $labels.spec_replicas }}."
          
          # PV容量告警
          - alert: PersistentVolumeAlmostFull
            expr: (kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes) > 0.9
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "PersistentVolume {{ $labels.persistentvolumeclaim }} almost full"
              description: "PV usage is above 90% (current: {{ $value | humanizePercentage }})"
```

### 8.2 故障恢复脚本

```bash
#!/bin/bash
# ========================================
# Kubernetes集群故障恢复脚本
# ========================================

# 场景1: Master节点故障
# 如果使用kubeadm部署，etcd在Master节点上

# 1. 移除故障Master节点
kubectl delete node master02

# 2. 在故障节点重置kubeadm
kubeadm reset -f

# 3. 重新加入集群 (使用之前保存的join命令或重新生成token)
kubeadm token create --print-join-command

# 4. 在故障节点执行join命令
kubeadm join <control-plane-endpoint>:6443 --token <token> \
    --discovery-token-ca-cert-hash sha256:<hash> \
    --control-plane --certificate-key <cert-key>

# 场景2: etcd数据损坏 (使用快照恢复)
# 见前面etcd恢复章节

# 场景3: 所有Master节点故障
# 1. 从备份恢复etcd快照
# 2. 重新部署控制平面
# 3. Worker节点会自动重新连接

# 场景4: Worker节点故障
# 节点故障会自动触发Pod重新调度，无需手动干预
# 如果节点恢复，重新加入集群:
systemctl start kubelet

# 场景5: CNI网络故障
# 重新部署CNI插件
kubectl delete -f https://docs.projectcalico.org/manifests/calico.yaml
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# 场景6: CoreDNS故障
kubectl rollout restart deployment coredns -n kube-system

# ========================================
# 健康检查脚本
# ========================================

check_cluster_health() {
    echo "=== 集群健康检查 ==="
    
    # 检查节点状态
    echo -e "\n1. 节点状态:"
    kubectl get nodes
    
    NOT_READY=$(kubectl get nodes --no-headers | grep -v Ready | wc -l)
    if [ $NOT_READY -gt 0 ]; then
        echo "⚠️  警告: $NOT_READY 个节点Not Ready"
    else
        echo "✅ 所有节点Ready"
    fi
    
    # 检查控制平面Pod
    echo -e "\n2. 控制平面组件:"
    kubectl get pods -n kube-system | grep -E "kube-apiserver|kube-controller|kube-scheduler|etcd"
    
    # 检查CoreDNS
    echo -e "\n3. CoreDNS状态:"
    kubectl get pods -n kube-system -l k8s-app=kube-dns
    
    # 检查CNI
    echo -e "\n4. CNI插件状态:"
    kubectl get pods -n kube-system | grep -E "calico|flannel|cilium|weave"
    
    # 检查PV/PVC
    echo -e "\n5. 持久化存储:"
    kubectl get pv,pvc --all-namespaces
    
    # 检查有问题的Pod
    echo -e "\n6. 问题Pod:"
    kubectl get pods --all-namespaces --field-selector=status.phase!=Running,status.phase!=Succeeded
    
    # 检查最近事件
    echo -e "\n7. 最近告警事件:"
    kubectl get events --all-namespaces --sort-by='.metadata.creationTimestamp' | grep -i "error\|warning" | tail -20
}

# 执行健康检查
check_cluster_health

echo "✅ 健康检查完成"
```

---

## 9. 最佳实践

```yaml
Kubernetes_HA_Best_Practices:
  集群规划:
    ✅ Master节点奇数个 (3或5)
    ✅ Master节点分布在不同机架/可用区
    ✅ Worker节点至少3个
    ✅ 使用外部etcd (大型集群)
    ✅ 配置负载均衡器冗余 (Keepalived)
  
  高可用配置:
    ✅ 启用Leader选举 (controller-manager/scheduler)
    ✅ 配置etcd定期备份
    ✅ 配置API Server审计日志
    ✅ 使用RBAC进行权限控制
    ✅ 启用Pod Security Policy/Standards
  
  应用部署:
    ✅ 关键应用: replicas >= 3
    ✅ 配置Pod反亲和性
    ✅ 配置PodDisruptionBudget
    ✅ 配置健康检查 (liveness/readiness)
    ✅ 配置资源请求和限制
    ✅ 使用HPA自动扩缩容
  
  存储配置:
    ✅ 使用持久化存储 (PV/PVC)
    ✅ 选择合适的StorageClass
    ✅ 配置备份策略
    ✅ 使用副本数>1的存储方案
  
  监控告警:
    ✅ 部署Prometheus监控
    ✅ 配置关键指标告警
    ✅ 集中日志收集 (EFK/Loki)
    ✅ 定期审查监控数据
    ✅ 建立故障响应流程
  
  安全加固:
    ✅ 启用TLS加密 (所有组件)
    ✅ 定期轮换证书
    ✅ 网络策略隔离
    ✅ 镜像扫描
    ✅ 定期更新K8s版本
    ✅ 最小权限原则
  
  备份恢复:
    ✅ 定期备份etcd (每天)
    ✅ 备份K8s资源定义
    ✅ 备份持久化数据
    ✅ 定期测试恢复流程
    ✅ 异地备份
  
  容量规划:
    ✅ Master节点: 4C8G (最小), 8C16G (推荐)
    ✅ Worker节点: 根据负载规划
    ✅ etcd: SSD磁盘, 低延迟网络
    ✅ 预留30%资源用于故障切换
  
  故障演练:
    ✅ 定期Master节点故障演练
    ✅ etcd恢复演练
    ✅ 网络分区测试
    ✅ 存储故障测试
    ✅ 文档化演练结果

常见陷阱:
  ❌ Master节点数量为偶数
  ❌ 所有Master节点在同一机架
  ❌ 未配置资源requests/limits
  ❌ 单副本部署关键应用
  ❌ 未配置健康检查
  ❌ 未备份etcd
  ❌ 使用HostPath存储
  ❌ 未配置PDB
  ❌ 未启用监控告警
  ❌ 未定期测试恢复流程

生产级检查清单:
  部署前:
    ✅ 硬件资源充足
    ✅ 网络规划合理
    ✅ 负载均衡配置正确
    ✅ etcd备份策略就绪
    ✅ 监控告警配置完成
    ✅ 文档完整
  
  部署后:
    ✅ 所有节点Ready
    ✅ 所有系统Pod Running
    ✅ API Server可访问
    ✅ DNS解析正常
    ✅ 网络连通性正常
    ✅ 存储可用
  
  定期检查:
    ✅ 集群组件健康
    ✅ 资源使用率
    ✅ 证书过期时间
    ✅ 备份完整性
    ✅ 日志告警
    ✅ 版本更新
```

---

## 相关文档

- [VMware高可用配置](01_VMware高可用配置.md)
- [备份恢复方案](03_备份恢复方案.md)
- [容灾演练流程](04_容灾演练流程.md)
- [存储容灾与备份](../03_存储架构/07_存储容灾与备份.md)
- [网络高可用](../04_网络架构/03_负载均衡与高可用.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪
