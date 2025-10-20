# 常见问题解答 (FAQ)

> **返回**: [附录资源首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [常见问题解答 (FAQ)](#常见问题解答-faq)
  - [📋 目录](#-目录)
  - [虚拟化常见问题](#虚拟化常见问题)
    - [VMware相关](#vmware相关)
    - [KVM相关](#kvm相关)
  - [容器化常见问题](#容器化常见问题)
    - [Docker基础](#docker基础)
    - [Docker网络](#docker网络)
    - [Docker存储](#docker存储)
  - [Kubernetes常见问题](#kubernetes常见问题)
    - [集群部署](#集群部署)
    - [Pod问题](#pod问题)
    - [网络问题](#网络问题)
    - [存储问题](#存储问题)
    - [资源管理](#资源管理)
  - [网络故障排查](#网络故障排查)
    - [连通性问题](#连通性问题)
    - [DNS问题](#dns问题)
    - [负载均衡问题](#负载均衡问题)
  - [存储故障排查](#存储故障排查)
    - [存储挂载问题](#存储挂载问题)
    - [性能问题](#性能问题)
  - [性能优化问题](#性能优化问题)
    - [CPU优化](#cpu优化)
    - [内存优化](#内存优化)
    - [IO优化](#io优化)
  - [安全相关问题](#安全相关问题)
    - [镜像安全](#镜像安全)
    - [网络安全](#网络安全)
    - [权限管理](#权限管理)
  - [日常运维问题](#日常运维问题)
    - [备份恢复](#备份恢复)
    - [监控告警](#监控告警)
    - [日志管理](#日志管理)

---

## 虚拟化常见问题

### VMware相关

**Q1: ESXi无法启动，卡在"Relocating modules and starting up the kernel..."**-

**A**: 可能原因和解决方法：

1. **硬件不兼容**

   ```bash
   # 检查硬件兼容性
   - 访问VMware HCL网站验证硬件兼容性
   - 更新BIOS到最新版本
   ```

2. **内存问题**
   - 测试内存是否有故障
   - 尝试移除部分内存模块

3. **BIOS设置**
   - 确保VT-x/AMD-V已启用
   - 禁用Secure Boot

---

**Q2: vMotion失败，报错"A general system error occurred: PBM error occurred during PreMigrateCheckCallback"**-

**A**: 解决步骤：

```bash
# 1. 检查存储策略
- vCenter界面查看虚拟机存储策略
- 确保目标主机存储满足策略要求

# 2. 重启vCenter的sps服务
service-control --stop vmware-sps
service-control --start vmware-sps

# 3. 清除存储策略缓存
service-control --stop vmware-vpostgres
rm -rf /storage/db/vpostgres
service-control --start vmware-vpostgres
```

---

**Q3: 如何扩展VMware虚拟机磁盘？**

**A**: 扩展步骤：

1. **在vCenter中扩展虚拟磁盘**
   - 右键虚拟机 → 编辑设置 → 选择硬盘 → 增加容量

2. **在Guest OS中扩展分区 (Linux)**

   ```bash
   # 扫描磁盘
   echo 1 > /sys/class/block/sda/device/rescan
   
   # 使用growpart扩展分区
   growpart /dev/sda 1
   
   # 扩展文件系统
   # ext4
   resize2fs /dev/sda1
   
   # xfs
   xfs_growfs /
   
   # LVM
   pvresize /dev/sda1
   lvextend -l +100%FREE /dev/mapper/vg-lv
   resize2fs /dev/mapper/vg-lv
   ```

---

### KVM相关

**Q4: KVM虚拟机性能差，如何优化？**

**A**: 性能优化建议：

1. **使用virtio驱动**

   ```xml
   <!-- 磁盘virtio -->
   <disk type='file' device='disk'>
     <driver name='qemu' type='qcow2' cache='none' io='native'/>
     <target dev='vda' bus='virtio'/>
   </disk>
   
   <!-- 网卡virtio -->
   <interface type='bridge'>
     <model type='virtio'/>
   </interface>
   ```

2. **CPU绑定**

   ```xml
   <vcpu placement='static' cpuset='0-3'>4</vcpu>
   <cputune>
     <vcpupin vcpu='0' cpuset='0'/>
     <vcpupin vcpu='1' cpuset='1'/>
     <vcpupin vcpu='2' cpuset='2'/>
     <vcpupin vcpu='3' cpuset='3'/>
   </cputune>
   ```

3. **大页内存**

   ```bash
   # 配置大页
   echo 1024 > /proc/sys/vm/nr_hugepages
   
   # 永久配置
   echo "vm.nr_hugepages = 1024" >> /etc/sysctl.conf
   sysctl -p
   ```

---

**Q5: 如何将VMware虚拟机迁移到KVM？**

**A**: 迁移步骤：

```bash
# 1. 转换VMDK到qcow2
qemu-img convert -f vmdk -O qcow2 vm.vmdk vm.qcow2

# 2. 创建KVM虚拟机
virt-install \
  --name vm-name \
  --ram 4096 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/vm.qcow2,bus=virtio \
  --import \
  --os-variant ubuntu20.04 \
  --network bridge=br0,model=virtio \
  --graphics vnc

# 3. 安装virtio驱动 (Windows guest需要)
# 下载: https://fedorapeople.org/groups/virt/virtio-win/
```

---

## 容器化常见问题

### Docker基础

**Q6: Docker容器无法启动，报错"docker: Error response from daemon: OCI runtime create failed"**-

**A**: 常见原因：

1. **SELinux问题** (CentOS/RHEL)

   ```bash
   # 临时禁用
   setenforce 0
   
   # 永久禁用
   sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
   ```

2. **cgroup驱动不匹配**

   ```bash
   # 检查Docker cgroup驱动
   docker info | grep "Cgroup Driver"
   
   # 配置systemd cgroup驱动
   cat > /etc/docker/daemon.json <<EOF
   {
     "exec-opts": ["native.cgroupdriver=systemd"]
   }
   EOF
   
   systemctl restart docker
   ```

3. **存储驱动问题**

   ```bash
   # 切换到overlay2
   cat > /etc/docker/daemon.json <<EOF
   {
     "storage-driver": "overlay2"
   }
   EOF
   ```

---

**Q7: 如何清理Docker占用的磁盘空间？**

**A**: 清理方法：

```bash
# 1. 查看磁盘使用
docker system df

# 2. 清理未使用的镜像
docker image prune -a

# 3. 清理未使用的容器
docker container prune

# 4. 清理未使用的卷
docker volume prune

# 5. 清理未使用的网络
docker network prune

# 6. 一键清理所有未使用资源
docker system prune -a --volumes

# 7. 定期自动清理 (cron)
0 2 * * * docker system prune -af --volumes > /dev/null 2>&1
```

---

**Q8: 容器内时间与宿主机不一致？**

**A**: 解决方法：

```bash
# 方法1: 挂载宿主机时区
docker run -v /etc/localtime:/etc/localtime:ro \
           -v /etc/timezone:/etc/timezone:ro \
           myimage

# 方法2: 设置TZ环境变量
docker run -e TZ=Asia/Shanghai myimage

# 方法3: Dockerfile设置
FROM ubuntu:22.04
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
```

---

### Docker网络

**Q9: Docker容器无法访问外网？**

**A**: 排查步骤：

```bash
# 1. 检查IP转发
cat /proc/sys/net/ipv4/ip_forward  # 应该返回1
sysctl -w net.ipv4.ip_forward=1

# 2. 检查iptables NAT规则
iptables -t nat -L -n | grep MASQUERADE

# 3. 添加NAT规则 (如果缺失)
iptables -t nat -A POSTROUTING -s 172.17.0.0/16 ! -o docker0 -j MASQUERADE

# 4. 检查DNS配置
docker run --rm alpine cat /etc/resolv.conf

# 5. 自定义DNS
cat > /etc/docker/daemon.json <<EOF
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF
systemctl restart docker
```

---

**Q10: Docker容器间无法通信？**

**A**: 解决方法：

```bash
# 1. 确保在同一网络
docker network ls
docker network inspect bridge

# 2. 创建自定义网络
docker network create mynetwork

# 3. 启动容器到同一网络
docker run --network mynetwork --name app1 nginx
docker run --network mynetwork --name app2 alpine ping app1

# 4. 连接已有容器到网络
docker network connect mynetwork existing-container

# 5. 检查防火墙规则
iptables -L DOCKER-USER -n
```

---

### Docker存储

**Q11: 如何持久化容器数据？**

**A**: 三种方式：

1. **Volume (推荐)**

   ```bash
   # 创建volume
   docker volume create mydata
   
   # 使用volume
   docker run -v mydata:/data nginx
   
   # 查看volume
   docker volume ls
   docker volume inspect mydata
   ```

2. **Bind Mount**

   ```bash
   # 挂载主机目录
   docker run -v /host/path:/container/path nginx
   
   # 只读挂载
   docker run -v /host/path:/container/path:ro nginx
   ```

3. **tmpfs Mount** (临时数据)

   ```bash
   docker run --tmpfs /tmp nginx
   ```

---

**Q12: Docker磁盘空间不足，如何迁移到其他分区？**

**A**: 迁移步骤：

```bash
# 1. 停止Docker
systemctl stop docker

# 2. 迁移数据目录
rsync -aP /var/lib/docker/ /new/path/docker/

# 3. 配置Docker使用新路径
cat > /etc/docker/daemon.json <<EOF
{
  "data-root": "/new/path/docker"
}
EOF

# 4. 启动Docker
systemctl start docker

# 5. 验证
docker info | grep "Docker Root Dir"

# 6. 删除旧数据 (确认无误后)
rm -rf /var/lib/docker
```

---

## Kubernetes常见问题

### 集群部署

**Q13: kubeadm init失败，报错"[ERROR FileContent--proc-sys-net-bridge-bridge-nf-call-iptables]"**

**A**: 解决方法：

```bash
# 1. 加载br_netfilter模块
modprobe br_netfilter

# 2. 配置内核参数
cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF

sysctl --system

# 3. 禁用Swap
swapoff -a
sed -i '/swap/d' /etc/fstab

# 4. 重新初始化
kubeadm reset -f
kubeadm init --pod-network-cidr=10.244.0.0/16
```

---

**Q14: kubectl连接集群超时？**

**A**: 排查步骤：

```bash
# 1. 检查kubeconfig
cat ~/.kube/config
kubectl config view

# 2. 检查API Server状态
systemctl status kube-apiserver  # 二进制部署
kubectl get pods -n kube-system | grep apiserver  # kubeadm部署

# 3. 检查证书是否过期
kubeadm certs check-expiration

# 4. 更新证书
kubeadm certs renew all
systemctl restart kubelet

# 5. 检查防火墙
firewall-cmd --list-all
# 开放6443端口
firewall-cmd --permanent --add-port=6443/tcp
firewall-cmd --reload
```

---

### Pod问题

**Q15: Pod一直处于Pending状态？**

**A**: 常见原因：

```bash
# 1. 查看Pod事件
kubectl describe pod <pod-name>

# 常见原因和解决方法：

# 原因1: 资源不足
kubectl describe nodes  # 查看节点资源
kubectl get pods --all-namespaces  # 查看资源使用

# 原因2: NodeSelector不匹配
kubectl get nodes --show-labels
# 删除或修改NodeSelector

# 原因3: Taint/Toleration
kubectl describe node <node-name> | grep Taint
# 添加toleration或移除taint
kubectl taint nodes <node-name> key:NoSchedule-

# 原因4: PVC未绑定
kubectl get pvc
# 检查StorageClass和PV
```

---

**Q16: Pod状态CrashLoopBackOff？**

**A**: 排查方法：

```bash
# 1. 查看Pod日志
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # 查看上一个容器日志

# 2. 查看Pod事件
kubectl describe pod <pod-name>

# 3. 进入容器调试
kubectl exec -it <pod-name> -- sh

# 4. 常见原因：
# - 应用启动失败 → 检查配置和依赖
# - 健康检查失败 → 调整探针配置
# - 资源限制 → 增加资源limits
# - 权限问题 → 检查securityContext

# 5. 调试Pod (使用debug容器)
kubectl debug <pod-name> -it --image=busybox
```

---

**Q17: Pod无法拉取镜像，报错"ImagePullBackOff"？**

**A**: 解决方法：

```bash
# 1. 检查镜像名称
kubectl describe pod <pod-name> | grep Image

# 2. 检查镜像是否存在
docker pull <image-name>

# 3. 配置私有镜像仓库认证
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email>

# 在Pod中使用Secret
spec:
  imagePullSecrets:
  - name: regcred

# 4. 使用镜像代理
# 修改containerd配置
cat >> /etc/containerd/config.toml <<EOF
[plugins."io.containerd.grpc.v1.cri".registry.mirrors]
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
    endpoint = ["https://docker.mirrors.sjtug.sjtu.edu.cn"]
EOF

systemctl restart containerd
```

---

### 网络问题

**Q18: Pod之间无法通信？**

**A**: 排查步骤：

```bash
# 1. 检查CNI插件
kubectl get pods -n kube-system | grep -E "calico|flannel|cilium"

# 2. 检查NetworkPolicy
kubectl get networkpolicy --all-namespaces
kubectl describe networkpolicy <policy-name>

# 3. 测试Pod间连通性
# 创建测试Pod
kubectl run test --image=busybox --rm -it -- sh
# 在Pod内测试
ping <target-pod-ip>
wget -O- http://<service-name>

# 4. 检查kube-proxy
kubectl get pods -n kube-system | grep kube-proxy
kubectl logs -n kube-system <kube-proxy-pod>

# 5. 检查iptables规则
iptables-save | grep <service-name>

# 6. 重启网络组件
kubectl delete pod -n kube-system -l k8s-app=kube-dns
kubectl delete pod -n kube-system -l k8s-app=calico-node
```

---

**Q19: Service无法访问？**

**A**: 排查方法：

```bash
# 1. 检查Service
kubectl get svc
kubectl describe svc <service-name>

# 2. 检查Endpoints
kubectl get endpoints <service-name>
# 如果endpoints为空，检查selector

# 3. 测试Service
# ClusterIP
kubectl run test --image=busybox --rm -it -- wget -O- http://<service-ip>

# NodePort
curl http://<node-ip>:<node-port>

# 4. 检查DNS
kubectl run test --image=busybox --rm -it -- nslookup <service-name>

# 5. 查看kube-proxy日志
kubectl logs -n kube-system -l k8s-app=kube-proxy

# 6. 检查防火墙
iptables -L -n | grep <service-port>
firewall-cmd --list-all
```

---

### 存储问题

**Q20: PVC一直处于Pending状态？**

**A**: 解决方法：

```bash
# 1. 查看PVC详情
kubectl describe pvc <pvc-name>

# 常见原因：

# 原因1: 没有可用的PV
kubectl get pv
# 创建PV或配置StorageClass动态供应

# 原因2: StorageClass不存在
kubectl get storageclass
# 创建或指定正确的StorageClass

# 原因3: 访问模式不匹配
# PVC和PV的accessModes必须兼容
# ReadWriteOnce, ReadOnlyMany, ReadWriteMany

# 原因4: 容量不足
# PV容量必须 >= PVC请求容量

# 示例: 创建本地PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteOnce
  hostPath:
    path: /mnt/data
```

---

**Q21: Pod挂载存储失败？**

**A**: 排查步骤：

```bash
# 1. 查看Pod事件
kubectl describe pod <pod-name>

# 2. 检查PVC状态
kubectl get pvc

# 3. 查看PV详情
kubectl describe pv <pv-name>

# 4. 检查CSI驱动 (如果使用)
kubectl get pods -n kube-system | grep csi
kubectl logs -n kube-system <csi-pod>

# 5. 检查节点挂载
# 在Pod所在节点上
mount | grep <volume-path>
df -h

# 6. NFS挂载问题
# 检查NFS服务器
showmount -e <nfs-server>
# 手动测试挂载
mount -t nfs <nfs-server>:/path /mnt/test

# 7. iSCSI挂载问题
# 检查iscsid服务
systemctl status iscsid
# 发现target
iscsiadm -m discovery -t st -p <iscsi-server>
```

---

### 资源管理

**Q22: 如何限制Pod资源使用？**

**A**: 资源限制方法：

```yaml
# 1. Pod级别限制
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:v1
    resources:
      requests:  # 调度使用，保证最小资源
        memory: "256Mi"
        cpu: "250m"
      limits:    # 运行时限制，超过会被杀死
        memory: "512Mi"
        cpu: "500m"

# 2. 命名空间级别限制 (ResourceQuota)
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: dev
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"

# 3. 默认资源限制 (LimitRange)
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limit
  namespace: dev
spec:
  limits:
  - default:      # 默认limits
      cpu: 500m
      memory: 512Mi
    defaultRequest:  # 默认requests
      cpu: 250m
      memory: 256Mi
    type: Container
```

---

**Q23: OOMKilled，Pod被杀死？**

**A**: 解决方法：

```bash
# 1. 查看Pod状态
kubectl get pod <pod-name>
# STATUS: OOMKilled

# 2. 查看Pod事件
kubectl describe pod <pod-name>
# Reason: OOMKilled

# 3. 查看容器日志
kubectl logs <pod-name> --previous

# 4. 增加内存limits
spec:
  containers:
  - name: app
    resources:
      limits:
        memory: "2Gi"  # 增加内存限制

# 5. 优化应用内存使用
# - 检查内存泄漏
# - 调整JVM堆大小 (Java应用)
# - 使用内存分析工具

# 6. 使用VPA自动调整
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: myapp-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: myapp
  updatePolicy:
    updateMode: "Auto"
```

---

## 网络故障排查

### 连通性问题

**Q24: 无法ping通某个IP？**

**A**: 排查步骤：

```bash
# 1. 检查网络接口
ip addr show
ip link show

# 2. 检查路由
ip route show
# 添加路由
ip route add 192.168.1.0/24 via 192.168.0.1

# 3. 检查防火墙
iptables -L -n
firewall-cmd --list-all

# 4. 检查ICMP是否被禁用
# 临时允许
iptables -A INPUT -p icmp -j ACCEPT
# 或
firewall-cmd --add-protocol=icmp

# 5. 使用tcpdump抓包
tcpdump -i eth0 icmp

# 6. 检查对端主机
# 确保对端主机在线
# 确保对端防火墙允许ICMP
```

---

### DNS问题

**Q25: 域名解析失败？**

**A**: 排查方法：

```bash
# 1. 检查DNS配置
cat /etc/resolv.conf

# 2. 测试DNS解析
nslookup example.com
dig example.com
host example.com

# 3. 测试特定DNS服务器
nslookup example.com 8.8.8.8
dig @8.8.8.8 example.com

# 4. 检查DNS服务器连通性
ping 8.8.8.8

# 5. Kubernetes DNS问题
# 检查CoreDNS
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns

# 测试集群DNS
kubectl run test --image=busybox --rm -it -- nslookup kubernetes.default

# 6. 配置正确的DNS
# Docker
cat > /etc/docker/daemon.json <<EOF
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF

# Kubernetes Pod
spec:
  dnsPolicy: "None"
  dnsConfig:
    nameservers:
    - 8.8.8.8
    searches:
    - default.svc.cluster.local
    - svc.cluster.local
```

---

### 负载均衡问题

**Q26: Nginx负载均衡不均匀？**

**A**: 优化配置：

```nginx
upstream backend {
    # 默认: 轮询
    server backend1:8080;
    server backend2:8080;
    
    # 加权轮询
    server backend1:8080 weight=3;
    server backend2:8080 weight=1;
    
    # 最少连接
    least_conn;
    
    # IP Hash (会话保持)
    ip_hash;
    
    # 健康检查
    server backend1:8080 max_fails=3 fail_timeout=30s;
    server backend2:8080 max_fails=3 fail_timeout=30s;
    
    # 备份服务器
    server backend3:8080 backup;
    
    # Keepalive连接
    keepalive 32;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
        
        # 保持客户端信息
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

---

## 存储故障排查

### 存储挂载问题

**Q27: NFS挂载失败？**

**A**: 排查步骤：

```bash
# 1. 检查NFS服务器
systemctl status nfs-server

# 2. 检查导出配置
cat /etc/exports
exportfs -v

# 3. 测试NFS服务器连通性
ping <nfs-server>
showmount -e <nfs-server>

# 4. 检查防火墙
# NFS需要开放: 111, 2049, 20048端口
firewall-cmd --permanent --add-service=nfs
firewall-cmd --permanent --add-service=mountd
firewall-cmd --permanent --add-service=rpc-bind
firewall-cmd --reload

# 5. 手动挂载测试
mount -t nfs <nfs-server>:/path /mnt/test
# 如果失败，查看详细错误
mount -t nfs -v <nfs-server>:/path /mnt/test

# 6. 检查权限
ls -ld /path/on/nfs-server
# 确保no_root_squash或正确的用户映射

# 7. 常见错误:
# mount.nfs: access denied → 检查/etc/exports的IP限制
# mount.nfs: Connection refused → 检查nfs-server服务和防火墙
# mount.nfs: No such file or directory → 检查导出路径
```

---

### 性能问题

**Q28: 磁盘IO性能差？**

**A**: 性能优化：

```bash
# 1. 测试磁盘性能
# 顺序写
dd if=/dev/zero of=/tmp/test bs=1M count=1024
# 顺序读
dd if=/tmp/test of=/dev/null bs=1M

# 使用fio全面测试
fio --name=randwrite --ioengine=libaio --iodepth=16 \
    --rw=randwrite --bs=4k --direct=1 --size=1G \
    --numjobs=4 --runtime=60 --group_reporting

# 2. 检查IO使用情况
iostat -x 1
iotop

# 3. 优化文件系统
# 使用noatime减少写入
mount -o remount,noatime /

# /etc/fstab
/dev/sda1  /data  ext4  noatime,nodiratime  0 2

# 4. 调整IO调度器
# 查看当前调度器
cat /sys/block/sda/queue/scheduler

# SSD使用noop或none
echo noop > /sys/block/sda/queue/scheduler

# HDD使用deadline或cfq
echo deadline > /sys/block/sda/queue/scheduler

# 5. 增加缓存
# 增加page cache
sysctl -w vm.dirty_ratio=40
sysctl -w vm.dirty_background_ratio=10

# 6. 使用RAID提升性能
# RAID0: 性能最高，无冗余
# RAID10: 性能和冗余平衡
```

---

## 性能优化问题

### CPU优化

**Q29: CPU使用率过高？**

**A**: 优化方法：

```bash
# 1. 查找CPU占用高的进程
top -o %CPU
htop

# 2. 查看进程详情
ps -eLf | grep <pid>  # 查看线程
pidstat -p <pid> 1    # CPU使用详情

# 3. 分析CPU使用
# 查看系统调用
strace -p <pid> -c

# 查看函数调用
perf top -p <pid>
perf record -p <pid> -g -- sleep 10
perf report

# 4. 容器CPU限制
docker run --cpus=2 myapp     # 限制2个CPU
docker run --cpu-shares=512 myapp  # CPU权重

# Kubernetes CPU限制
resources:
  limits:
    cpu: 2000m

# 5. 优化应用
# - 减少计算密集型操作
# - 使用缓存
# - 异步处理
# - 负载均衡
```

---

### 内存优化

**Q30: 内存占用过高？**

**A**: 优化方法：

```bash
# 1. 查看内存使用
free -h
vmstat 1

# 2. 查找内存占用高的进程
top -o %MEM
ps aux --sort=-%mem | head

# 3. 查看进程内存详情
pmap -x <pid>
cat /proc/<pid>/status | grep -i vm

# 4. 分析内存泄漏
valgrind --leak-check=full ./myapp

# 5. 清理缓存
sync
echo 3 > /proc/sys/vm/drop_caches

# 6. 调整swap使用
sysctl -w vm.swappiness=10  # 减少swap使用

# 7. 容器内存限制
docker run -m 512m myapp

# Kubernetes内存限制
resources:
  limits:
    memory: 2Gi

# 8. 优化应用
# - 修复内存泄漏
# - 调整JVM堆大小
# - 使用对象池
```

---

### IO优化

**Q31: 磁盘IO瓶颈？**

**A**: 优化方案：

```bash
# 1. 监控IO
iostat -x 1
iotop -o

# 2. 查找IO占用高的进程
iotop
pidstat -d 1

# 3. 使用SSD
# - 系统盘使用SSD
# - 数据库使用SSD
# - 日志可以使用HDD

# 4. 使用RAID
# RAID0: 最高性能
# RAID10: 性能和冗余

# 5. 文件系统优化
# ext4优化
tune2fs -o journal_data_writeback /dev/sda1

# xfs优化
mount -o noatime,nodiratime,logbufs=8 /dev/sda1 /data

# 6. 数据库优化
# MySQL
[mysqld]
innodb_flush_log_at_trx_commit = 2
innodb_buffer_pool_size = 70% of RAM

# 7. Docker存储驱动
# 使用overlay2
cat > /etc/docker/daemon.json <<EOF
{
  "storage-driver": "overlay2"
}
EOF
```

---

## 安全相关问题

### 镜像安全

**Q32: 如何扫描镜像漏洞？**

**A**: 扫描方法：

```bash
# 1. 使用Trivy扫描
trivy image nginx:latest

# 详细扫描
trivy image --severity HIGH,CRITICAL nginx:latest

# 2. 使用Clair扫描
# 部署Clair服务器
docker run -p 5432:5432 -d --name clairdb postgres:11
docker run -p 6060-6061:6060-6061 -d --name clair \
  --link clairdb:postgres \
  quay.io/coreos/clair:latest

# 使用clairctl扫描
clairctl analyze nginx:latest

# 3. 使用Anchore
anchore-cli image add nginx:latest
anchore-cli image wait nginx:latest
anchore-cli image vuln nginx:latest all

# 4. Harbor内置扫描
# Harbor UI中启用镜像扫描

# 5. 最佳实践
# - 使用最小化基础镜像 (alpine, distroless)
# - 定期更新镜像
# - 不要在镜像中存储敏感信息
# - 使用多阶段构建
```

---

### 网络安全

**Q33: 如何实现Kubernetes网络隔离？**

**A**: 网络策略配置：

```yaml
# 1. 默认拒绝所有入站流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress

# 2. 只允许特定Pod访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080

# 3. 允许特定命名空间访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-namespace
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: production

# 4. 限制出站流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-external
spec:
  podSelector:
    matchLabels:
      app: secure-app
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector: {}  # 只允许同命名空间
```

---

### 权限管理

**Q34: 如何配置最小权限RBAC？**

**A**: RBAC配置：

```yaml
# 1. 创建ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: default

# 2. 创建Role (命名空间级别)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

# 3. 绑定Role到ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: myapp-sa
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

# 4. 在Pod中使用
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  serviceAccountName: myapp-sa
  containers:
  - name: app
    image: myapp:v1

# 5. ClusterRole (集群级别)
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "watch"]
```

---

## 日常运维问题

### 备份恢复

**Q35: 如何备份Kubernetes集群？**

**A**: 备份方案：

```bash
# 1. 备份etcd (最重要)
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# 验证备份
ETCDCTL_API=3 etcdctl snapshot status /backup/etcd-snapshot.db -w table

# 2. 恢复etcd
systemctl stop etcd
rm -rf /var/lib/etcd
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-snapshot.db \
  --data-dir=/var/lib/etcd
systemctl start etcd

# 3. 使用Velero备份集群资源
# 安装Velero
velero install --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.5.0 \
  --bucket velero-backups \
  --secret-file ./credentials-velero

# 备份整个集群
velero backup create full-backup

# 备份特定命名空间
velero backup create prod-backup --include-namespaces production

# 恢复
velero restore create --from-backup full-backup

# 4. 备份证书
tar czf /backup/k8s-certs.tar.gz /etc/kubernetes/pki/

# 5. 备份配置
kubectl get all --all-namespaces -o yaml > all-resources.yaml
```

---

### 监控告警

**Q36: 如何配置Prometheus告警？**

**A**: 告警配置：

```yaml
# 1. Prometheus告警规则
# alerts.yml
groups:
- name: node
  interval: 30s
  rules:
  # CPU使用率过高
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"
      description: "CPU usage is above 80% (current: {{ $value }}%)"
  
  # 内存使用率过高
  - alert: HighMemoryUsage
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"
      description: "Memory usage is above 85% (current: {{ $value }}%)"
  
  # 磁盘空间不足
  - alert: DiskSpaceLow
    expr: (node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"}) * 100 < 15
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Disk space low on {{ $labels.instance }}"
      description: "Disk {{ $labels.mountpoint }} has less than 15% space left"

# 2. Alertmanager配置
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
  - match:
      severity: critical
    receiver: 'critical'
  - match:
      severity: warning
    receiver: 'warning'

receivers:
- name: 'default'
  webhook_configs:
  - url: 'http://alertmanager-webhook:5001/'

- name: 'critical'
  email_configs:
  - to: 'ops@example.com'
    from: 'alertmanager@example.com'
    smarthost: 'smtp.gmail.com:587'
    auth_username: 'alertmanager@example.com'
    auth_password: 'password'
  webhook_configs:
  - url: 'http://your-webhook-url'

- name: 'warning'
  webhook_configs:
  - url: 'http://your-webhook-url'
```

---

### 日志管理

**Q37: 如何收集和分析日志？**

**A**: 日志方案：

```bash
# 1. Docker日志
# 查看容器日志
docker logs <container>
docker logs -f --tail 100 <container>

# 配置日志驱动
cat > /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

# 2. Kubernetes日志
# 查看Pod日志
kubectl logs <pod-name>
kubectl logs <pod-name> -c <container-name>
kubectl logs -f <pod-name>

# 查看所有Pod日志
kubectl logs -l app=myapp

# 3. 使用ELK Stack
# Filebeat配置
filebeat.inputs:
- type: container
  paths:
    - /var/log/containers/*.log

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "kubernetes-%{+yyyy.MM.dd}"

# 4. 使用Loki
# Promtail配置
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
- job_name: kubernetes-pods
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_name]
    target_label: pod

# 5. Grafana查询Loki
{namespace="production", pod=~"myapp-.*"}
```

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19  
**维护状态**: ✅ 完成

---

> 💡 **提示**:
>
> - 遇到问题先查看日志和事件
> - 使用官方文档和社区资源
> - 保持系统和软件更新
> - 定期备份重要数据
> - 在测试环境验证解决方案
