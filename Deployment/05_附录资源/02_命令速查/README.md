# 常用命令速查手册

> **返回**: [附录资源首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [常用命令速查手册](#常用命令速查手册)
  - [📋 目录](#-目录)
  - [Docker命令集](#docker命令集)
    - [容器管理](#容器管理)
    - [镜像管理](#镜像管理)
    - [网络管理](#网络管理)
    - [卷管理](#卷管理)
    - [Docker Compose](#docker-compose)
  - [Kubernetes命令集](#kubernetes命令集)
    - [集群管理](#集群管理)
    - [Pod管理](#pod管理)
    - [Deployment管理](#deployment管理)
    - [Service管理](#service管理)
    - [ConfigMap与Secret](#configmap与secret)
    - [存储管理](#存储管理)
    - [故障排查](#故障排查)
  - [VMware ESXi命令](#vmware-esxi命令)
    - [虚拟机管理](#虚拟机管理)
    - [网络管理](#网络管理-1)
    - [存储管理](#存储管理-1)
    - [系统管理](#系统管理)
  - [KVM命令集](#kvm命令集)
    - [virsh命令](#virsh命令)
    - [virt-install命令](#virt-install命令)
    - [QEMU命令](#qemu命令)
  - [Linux系统命令](#linux系统命令)
    - [系统信息](#系统信息)
    - [进程管理](#进程管理)
    - [内存管理](#内存管理)
    - [磁盘管理](#磁盘管理)
    - [用户管理](#用户管理)
    - [服务管理](#服务管理)
  - [网络诊断命令](#网络诊断命令)
    - [基础网络](#基础网络)
    - [网络监控](#网络监控)
    - [防火墙](#防火墙)
  - [存储管理命令](#存储管理命令)
    - [LVM管理](#lvm管理)
    - [RAID管理](#raid管理)
    - [NFS管理](#nfs管理)
    - [iSCSI管理](#iscsi管理)
  - [💡 使用技巧](#-使用技巧)
    - [命令别名](#命令别名)
    - [Tab补全](#tab补全)
      - [Docker补全](#docker补全)
      - [Kubectl补全](#kubectl补全)

---

## Docker命令集

### 容器管理

```bash
# 运行容器
docker run -d --name myapp -p 8080:80 nginx
docker run -it --rm ubuntu bash  # 交互式运行，退出删除

# 查看容器
docker ps                # 运行中的容器
docker ps -a             # 所有容器
docker ps -a --filter "status=exited"  # 已停止的容器

# 启动/停止/重启容器
docker start <container>
docker stop <container>
docker restart <container>
docker kill <container>  # 强制停止

# 删除容器
docker rm <container>
docker rm -f <container>  # 强制删除运行中的容器
docker container prune    # 删除所有停止的容器

# 查看容器日志
docker logs <container>
docker logs -f <container>         # 实时查看
docker logs --tail 100 <container> # 查看最后100行

# 进入容器
docker exec -it <container> bash
docker exec -it <container> sh

# 查看容器详情
docker inspect <container>
docker stats <container>  # 实时资源使用
docker top <container>    # 容器内进程

# 拷贝文件
docker cp <container>:/path/file /host/path  # 从容器拷贝
docker cp /host/path <container>:/path/      # 拷贝到容器

# 提交容器为镜像
docker commit <container> myimage:tag
```

---

### 镜像管理

```bash
# 拉取镜像
docker pull nginx:latest
docker pull ubuntu:22.04

# 查看镜像
docker images
docker images -a  # 包括中间层镜像
docker image ls

# 删除镜像
docker rmi <image>
docker rmi -f <image>  # 强制删除
docker image prune     # 删除未使用的镜像
docker image prune -a  # 删除所有未使用的镜像

# 构建镜像
docker build -t myapp:v1.0 .
docker build -t myapp:v1.0 -f Dockerfile.prod .
docker build --no-cache -t myapp:v1.0 .  # 不使用缓存

# 镜像标签
docker tag myapp:v1.0 registry.example.com/myapp:v1.0

# 推送镜像
docker push registry.example.com/myapp:v1.0

# 保存/加载镜像
docker save -o myimage.tar myapp:v1.0
docker load -i myimage.tar

# 导出/导入容器
docker export <container> > container.tar
docker import container.tar myapp:v1.0

# 查看镜像历史
docker history <image>

# 查看镜像详情
docker inspect <image>
```

---

### 网络管理

```bash
# 查看网络
docker network ls

# 创建网络
docker network create mynetwork
docker network create --driver bridge --subnet 172.20.0.0/16 mynetwork

# 连接/断开网络
docker network connect mynetwork <container>
docker network disconnect mynetwork <container>

# 查看网络详情
docker network inspect mynetwork

# 删除网络
docker network rm mynetwork
docker network prune  # 删除未使用的网络
```

---

### 卷管理

```bash
# 查看卷
docker volume ls

# 创建卷
docker volume create myvolume

# 使用卷运行容器
docker run -d -v myvolume:/data nginx
docker run -d --mount source=myvolume,target=/data nginx

# 查看卷详情
docker volume inspect myvolume

# 删除卷
docker volume rm myvolume
docker volume prune  # 删除未使用的卷

# 备份卷
docker run --rm -v myvolume:/source -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz -C /source .

# 恢复卷
docker run --rm -v myvolume:/target -v $(pwd):/backup ubuntu tar xzf /backup/backup.tar.gz -C /target
```

---

### Docker Compose

```bash
# 启动服务
docker-compose up
docker-compose up -d  # 后台运行
docker-compose up --build  # 重新构建镜像

# 停止服务
docker-compose stop
docker-compose down  # 停止并删除容器
docker-compose down -v  # 同时删除卷

# 查看服务
docker-compose ps
docker-compose logs
docker-compose logs -f <service>

# 重启服务
docker-compose restart
docker-compose restart <service>

# 执行命令
docker-compose exec <service> bash

# 扩展服务
docker-compose up -d --scale web=3

# 验证配置
docker-compose config
```

---

## Kubernetes命令集

### 集群管理

```bash
# 集群信息
kubectl cluster-info
kubectl version
kubectl get nodes
kubectl describe node <node-name>
kubectl top nodes  # 节点资源使用

# 查看集群组件
kubectl get componentstatuses
kubectl get cs

# 查看API资源
kubectl api-resources
kubectl api-versions

# 查看命名空间
kubectl get namespaces
kubectl get ns

# 创建命名空间
kubectl create namespace dev
kubectl create ns dev

# 设置默认命名空间
kubectl config set-context --current --namespace=dev

# 查看上下文
kubectl config get-contexts
kubectl config current-context
kubectl config use-context <context-name>
```

---

### Pod管理

```bash
# 查看Pod
kubectl get pods
kubectl get pods -A  # 所有命名空间
kubectl get pods -n kube-system
kubectl get pods -o wide  # 显示更多信息
kubectl get pods --show-labels  # 显示标签
kubectl get pods -l app=nginx  # 标签过滤

# 查看Pod详情
kubectl describe pod <pod-name>
kubectl get pod <pod-name> -o yaml

# 创建Pod
kubectl run nginx --image=nginx
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
kubectl apply -f pod.yaml

# 删除Pod
kubectl delete pod <pod-name>
kubectl delete pod <pod-name> --force --grace-period=0  # 强制删除
kubectl delete pods --all

# 查看Pod日志
kubectl logs <pod-name>
kubectl logs <pod-name> -f  # 实时查看
kubectl logs <pod-name> -c <container-name>  # 多容器Pod
kubectl logs <pod-name> --previous  # 查看上一个容器的日志
kubectl logs <pod-name> --tail=100

# 进入Pod
kubectl exec -it <pod-name> -- bash
kubectl exec -it <pod-name> -c <container-name> -- sh

# 端口转发
kubectl port-forward <pod-name> 8080:80

# 拷贝文件
kubectl cp <pod-name>:/path/file /local/path
kubectl cp /local/path <pod-name>:/path/

# 查看Pod资源使用
kubectl top pod <pod-name>
kubectl top pods -A
```

---

### Deployment管理

```bash
# 创建Deployment
kubectl create deployment nginx --image=nginx
kubectl create deployment nginx --image=nginx --replicas=3
kubectl apply -f deployment.yaml

# 查看Deployment
kubectl get deployments
kubectl get deploy
kubectl describe deployment nginx

# 扩缩容
kubectl scale deployment nginx --replicas=5
kubectl autoscale deployment nginx --min=2 --max=10 --cpu-percent=80

# 更新镜像
kubectl set image deployment/nginx nginx=nginx:1.21
kubectl set image deployment/nginx *=nginx:1.21  # 更新所有容器

# 编辑Deployment
kubectl edit deployment nginx

# 查看更新状态
kubectl rollout status deployment nginx
kubectl rollout history deployment nginx

# 回滚
kubectl rollout undo deployment nginx
kubectl rollout undo deployment nginx --to-revision=2

# 暂停/恢复更新
kubectl rollout pause deployment nginx
kubectl rollout resume deployment nginx

# 删除Deployment
kubectl delete deployment nginx
```

---

### Service管理

```bash
# 创建Service
kubectl expose deployment nginx --port=80 --target-port=80
kubectl expose deployment nginx --type=NodePort --port=80
kubectl expose deployment nginx --type=LoadBalancer --port=80
kubectl apply -f service.yaml

# 查看Service
kubectl get services
kubectl get svc
kubectl describe service nginx

# 查看Service端点
kubectl get endpoints
kubectl get ep nginx

# 删除Service
kubectl delete service nginx
```

---

### ConfigMap与Secret

```bash
# 创建ConfigMap
kubectl create configmap app-config --from-literal=key1=value1
kubectl create configmap app-config --from-file=config.txt
kubectl create configmap app-config --from-file=config-dir/
kubectl apply -f configmap.yaml

# 查看ConfigMap
kubectl get configmaps
kubectl get cm
kubectl describe configmap app-config
kubectl get configmap app-config -o yaml

# 编辑ConfigMap
kubectl edit configmap app-config

# 删除ConfigMap
kubectl delete configmap app-config

# 创建Secret
kubectl create secret generic app-secret --from-literal=password=mypass
kubectl create secret generic app-secret --from-file=ssh-privatekey=~/.ssh/id_rsa
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass \
  --docker-email=user@example.com
kubectl apply -f secret.yaml

# 查看Secret
kubectl get secrets
kubectl describe secret app-secret
kubectl get secret app-secret -o yaml

# 解码Secret
kubectl get secret app-secret -o jsonpath='{.data.password}' | base64 -d

# 删除Secret
kubectl delete secret app-secret
```

---

### 存储管理

```bash
# 查看PV
kubectl get persistentvolumes
kubectl get pv
kubectl describe pv <pv-name>

# 创建PV
kubectl apply -f pv.yaml

# 查看PVC
kubectl get persistentvolumeclaims
kubectl get pvc
kubectl describe pvc <pvc-name>

# 创建PVC
kubectl apply -f pvc.yaml

# 查看StorageClass
kubectl get storageclasses
kubectl get sc
kubectl describe sc <sc-name>

# 设置默认StorageClass
kubectl patch storageclass <sc-name> \
  -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# 删除PV/PVC
kubectl delete pvc <pvc-name>
kubectl delete pv <pv-name>
```

---

### 故障排查

```bash
# 查看事件
kubectl get events
kubectl get events -A
kubectl get events --sort-by=.metadata.creationTimestamp

# 查看资源使用
kubectl top nodes
kubectl top pods
kubectl top pod <pod-name> --containers

# 查看Pod状态
kubectl get pods --field-selector=status.phase=Pending
kubectl get pods --field-selector=status.phase=Failed

# 诊断命令
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl exec -it <pod-name> -- sh

# 查看API Server日志
kubectl logs -n kube-system kube-apiserver-<node>

# 查看调度器日志
kubectl logs -n kube-system kube-scheduler-<node>

# 查看Controller Manager日志
kubectl logs -n kube-system kube-controller-manager-<node>

# 查看Kubelet日志 (在节点上执行)
journalctl -u kubelet -f

# 查看节点状态
kubectl get nodes -o json | jq '.items[].status.conditions'

# 强制删除资源
kubectl delete pod <pod-name> --force --grace-period=0
kubectl patch pod <pod-name> -p '{"metadata":{"finalizers":null}}'
```

---

## VMware ESXi命令

### 虚拟机管理

```bash
# 列出虚拟机
vim-cmd vmsvc/getallvms

# 查看虚拟机详情
vim-cmd vmsvc/get.summary <vmid>

# 启动/停止虚拟机
vim-cmd vmsvc/power.on <vmid>
vim-cmd vmsvc/power.off <vmid>
vim-cmd vmsvc/power.reboot <vmid>
vim-cmd vmsvc/power.shutdown <vmid>  # 优雅关机

# 虚拟机状态
vim-cmd vmsvc/power.getstate <vmid>

# 创建快照
vim-cmd vmsvc/snapshot.create <vmid> "snapshot-name" "description"

# 查看快照
vim-cmd vmsvc/snapshot.get <vmid>

# 删除快照
vim-cmd vmsvc/snapshot.remove <vmid> <snapshotid>

# 注册/注销虚拟机
vim-cmd solo/registervm /vmfs/volumes/datastore1/vm/vm.vmx
vim-cmd vmsvc/unregister <vmid>
```

---

### 网络管理

```bash
# 查看网络配置
esxcli network ip interface list
esxcli network ip interface ipv4 get
esxcli network nic list

# 配置管理网络
esxcli network ip interface ipv4 set -i vmk0 -I 192.168.1.100 -N 255.255.255.0 -t static
esxcli network ip route ipv4 add -n default -g 192.168.1.1

# 查看虚拟交换机
esxcli network vswitch standard list
esxcli network vswitch standard portgroup list

# 创建虚拟交换机
esxcli network vswitch standard add -v vSwitch1
esxcli network vswitch standard portgroup add -p "VM Network" -v vSwitch1

# 查看防火墙规则
esxcli network firewall ruleset list
esxcli network firewall ruleset set --ruleset-id=sshServer --enabled=true
```

---

### 存储管理

```bash
# 查看数据存储
esxcli storage filesystem list
esxcli storage vmfs extent list

# 查看磁盘
esxcli storage core device list
esxcli storage core adapter list

# 扫描存储
esxcli storage core adapter rescan --all

# 创建VMFS数据存储
esxcli storage vmfs create -C vmfs6 -d <device> -S datastore1

# 查看iSCSI
esxcli iscsi software get
esxcli iscsi adapter list

# 配置iSCSI
esxcli iscsi software set --enabled=true
esxcli iscsi adapter discovery sendtarget add --address=192.168.1.10 --adapter=vmhba33
```

---

### 系统管理

```bash
# 系统信息
esxcli system version get
esxcli hardware platform get
esxcli hardware cpu list
esxcli hardware memory get

# 主机名设置
esxcli system hostname set --fqdn=esxi01.example.com

# DNS配置
esxcli network ip dns server add --server=8.8.8.8
esxcli network ip dns search add --domain=example.com

# NTP配置
esxcli system ntp server add --server=ntp.example.com
esxcli system ntp set --enabled=true

# 服务管理
/etc/init.d/hostd restart
/etc/init.d/vpxa restart

# 维护模式
esxcli system maintenanceMode set --enable true
esxcli system maintenanceMode get

# 重启/关机
esxcli system shutdown reboot --reason="System maintenance"
esxcli system shutdown poweroff --reason="Scheduled maintenance"
```

---

## KVM命令集

### virsh命令

```bash
# 查看虚拟机列表
virsh list --all

# 启动/停止虚拟机
virsh start vm-name
virsh shutdown vm-name
virsh destroy vm-name  # 强制关机
virsh reboot vm-name

# 暂停/恢复虚拟机
virsh suspend vm-name
virsh resume vm-name

# 自动启动
virsh autostart vm-name
virsh autostart --disable vm-name

# 查看虚拟机信息
virsh dominfo vm-name
virsh domstate vm-name

# 删除虚拟机
virsh undefine vm-name
virsh undefine --nvram --remove-all-storage vm-name

# 快照管理
virsh snapshot-create-as vm-name snapshot1 "My snapshot"
virsh snapshot-list vm-name
virsh snapshot-revert vm-name snapshot1
virsh snapshot-delete vm-name snapshot1

# 控制台连接
virsh console vm-name

# 虚拟机克隆
virt-clone --original vm-name --name vm-clone --file /var/lib/libvirt/images/vm-clone.qcow2

# 查看虚拟网络
virsh net-list --all
virsh net-info default

# 启动/停止网络
virsh net-start default
virsh net-autostart default

# 查看存储池
virsh pool-list --all
virsh pool-info default

# 查看存储卷
virsh vol-list default
```

---

### virt-install命令

```bash
# 创建虚拟机
virt-install \
  --name vm1 \
  --ram 2048 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/vm1.qcow2,size=20 \
  --os-variant ubuntu22.04 \
  --network bridge=virbr0 \
  --graphics vnc \
  --cdrom /path/to/ubuntu-22.04.iso

# 使用网络安装
virt-install \
  --name vm2 \
  --ram 4096 \
  --vcpus 4 \
  --disk path=/var/lib/libvirt/images/vm2.qcow2,size=50,bus=virtio \
  --os-variant centos8 \
  --network bridge=br0,model=virtio \
  --graphics none \
  --console pty,target_type=serial \
  --location http://mirror.centos.org/centos/8/BaseOS/x86_64/os/ \
  --extra-args 'console=ttyS0,115200n8'
```

---

### QEMU命令

```bash
# 创建磁盘镜像
qemu-img create -f qcow2 disk.qcow2 20G

# 转换磁盘格式
qemu-img convert -f vmdk -O qcow2 source.vmdk dest.qcow2

# 查看镜像信息
qemu-img info disk.qcow2

# 调整镜像大小
qemu-img resize disk.qcow2 +10G

# 创建快照
qemu-img snapshot -c snapshot1 disk.qcow2

# 查看快照
qemu-img snapshot -l disk.qcow2

# 应用快照
qemu-img snapshot -a snapshot1 disk.qcow2

# 删除快照
qemu-img snapshot -d snapshot1 disk.qcow2
```

---

## Linux系统命令

### 系统信息

```bash
# 系统信息
uname -a                 # 系统信息
hostnamectl              # 主机名信息
cat /etc/os-release      # 发行版信息
lsb_release -a           # 发行版详情

# CPU信息
lscpu
cat /proc/cpuinfo
nproc                    # CPU核心数

# 内存信息
free -h
cat /proc/meminfo
vmstat 1                 # 内存统计

# 磁盘信息
lsblk
fdisk -l
df -h                    # 磁盘使用
du -sh *                 # 目录大小

# 系统负载
uptime
top
htop
w                        # 当前用户

# 硬件信息
lshw                     # 硬件信息
lspci                    # PCI设备
lsusb                    # USB设备
dmidecode                # DMI信息
```

---

### 进程管理

```bash
# 查看进程
ps aux
ps -ef
pstree                   # 进程树

# 查找进程
pgrep nginx
pidof nginx

# 杀死进程
kill <pid>
kill -9 <pid>            # 强制杀死
killall nginx            # 按名称杀死
pkill -f pattern         # 按模式杀死

# 后台运行
nohup command &
screen                   # 终端会话管理
tmux                     # 终端复用

# 资源监控
top
htop
atop
```

---

### 内存管理

```bash
# 内存使用
free -h
cat /proc/meminfo

# 清理缓存
sync
echo 3 > /proc/sys/vm/drop_caches

# Swap管理
swapon -s                # 查看swap
swapoff -a               # 关闭swap
swapon -a                # 开启swap

# OOM killer
dmesg | grep -i "out of memory"
cat /proc/<pid>/oom_score
```

---

### 磁盘管理

```bash
# 分区管理
fdisk -l
fdisk /dev/sdb
parted /dev/sdb

# 文件系统
mkfs.ext4 /dev/sdb1
mkfs.xfs /dev/sdb1
tune2fs -l /dev/sdb1     # 查看文件系统信息

# 挂载
mount /dev/sdb1 /mnt
umount /mnt
mount -a                 # 挂载/etc/fstab中的所有

# 磁盘使用
df -h
df -i                    # inode使用
du -sh *
du -h --max-depth=1

# 磁盘IO
iostat -x 1
iotop
```

---

### 用户管理

```bash
# 用户操作
useradd username
useradd -m -s /bin/bash username
passwd username
userdel username
userdel -r username      # 删除用户及家目录

# 用户信息
id username
whoami
who
w
last                     # 登录历史

# 组管理
groupadd groupname
usermod -aG groupname username
groups username
```

---

### 服务管理

```bash
# systemd服务
systemctl start service
systemctl stop service
systemctl restart service
systemctl reload service
systemctl status service
systemctl enable service
systemctl disable service
systemctl is-enabled service
systemctl list-units --type=service
systemctl daemon-reload

# 旧版init.d
service nginx start
service nginx stop
service nginx status
chkconfig nginx on
```

---

## 网络诊断命令

### 基础网络

```bash
# 网络接口
ip addr show
ip link show
ifconfig
ip link set eth0 up
ip link set eth0 down

# IP配置
ip addr add 192.168.1.100/24 dev eth0
ip addr del 192.168.1.100/24 dev eth0

# 路由
ip route show
route -n
ip route add default via 192.168.1.1
ip route del default

# DNS
nslookup example.com
dig example.com
host example.com
cat /etc/resolv.conf

# 连通性测试
ping 8.8.8.8
ping -c 4 example.com
traceroute example.com
mtr example.com          # 组合ping和traceroute

# 端口测试
telnet 192.168.1.1 80
nc -zv 192.168.1.1 80    # netcat
curl -v http://example.com

# 查看监听端口
ss -tunlp
netstat -tunlp
lsof -i :80

# 查看连接
ss -s
netstat -an

# ARP
ip neigh show
arp -a
arping 192.168.1.1
```

---

### 网络监控

```bash
# 抓包
tcpdump -i eth0
tcpdump -i eth0 port 80
tcpdump -i eth0 -w capture.pcap
tcpdump -r capture.pcap

# 流量统计
iftop
nethogs                  # 按进程显示流量
iptraf-ng
nload

# 带宽测试
iperf3 -s                # 服务端
iperf3 -c 192.168.1.1    # 客户端
```

---

### 防火墙

```bash
# iptables
iptables -L -n -v
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -D INPUT -p tcp --dport 80 -j ACCEPT
iptables-save > /etc/iptables/rules.v4

# firewalld
firewall-cmd --state
firewall-cmd --list-all
firewall-cmd --add-port=80/tcp --permanent
firewall-cmd --remove-port=80/tcp --permanent
firewall-cmd --reload

# UFW (Ubuntu)
ufw status
ufw enable
ufw allow 22/tcp
ufw deny 80/tcp
ufw delete allow 80/tcp
```

---

## 存储管理命令

### LVM管理

```bash
# 物理卷PV
pvcreate /dev/sdb
pvdisplay
pvs
pvremove /dev/sdb

# 卷组VG
vgcreate vg01 /dev/sdb
vgdisplay
vgs
vgextend vg01 /dev/sdc
vgreduce vg01 /dev/sdc
vgremove vg01

# 逻辑卷LV
lvcreate -L 10G -n lv01 vg01
lvcreate -l 100%FREE -n lv02 vg01
lvdisplay
lvs
lvextend -L +5G /dev/vg01/lv01
lvresize -L 20G /dev/vg01/lv01
lvremove /dev/vg01/lv01

# 扩展文件系统
resize2fs /dev/vg01/lv01         # ext4
xfs_growfs /dev/vg01/lv01        # xfs

# LVM快照
lvcreate -L 1G -s -n lv01_snap /dev/vg01/lv01
lvremove /dev/vg01/lv01_snap
```

---

### RAID管理

```bash
# mdadm
# 创建RAID1
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc

# 创建RAID5
mdadm --create /dev/md0 --level=5 --raid-devices=3 /dev/sdb /dev/sdc /dev/sdd

# 查看RAID
cat /proc/mdstat
mdadm --detail /dev/md0

# 停止RAID
mdadm --stop /dev/md0

# 删除RAID
mdadm --remove /dev/md0
mdadm --zero-superblock /dev/sdb /dev/sdc

# 修复RAID
mdadm /dev/md0 --add /dev/sde  # 添加磁盘
mdadm /dev/md0 --fail /dev/sdb # 标记故障
mdadm /dev/md0 --remove /dev/sdb # 移除磁盘
```

---

### NFS管理

```bash
# NFS服务器
# 安装
apt install nfs-kernel-server     # Ubuntu
yum install nfs-utils              # CentOS

# 配置导出
echo "/data 192.168.1.0/24(rw,sync,no_root_squash)" >> /etc/exports
exportfs -ra                       # 重新导出
exportfs -v                        # 查看导出

# 服务管理
systemctl start nfs-server
systemctl enable nfs-server

# NFS客户端
showmount -e 192.168.1.10          # 查看导出
mount -t nfs 192.168.1.10:/data /mnt
umount /mnt

# 永久挂载 /etc/fstab
192.168.1.10:/data /mnt nfs defaults 0 0
```

---

### iSCSI管理

```bash
# iSCSI Target (服务器)
# 安装targetcli
apt install targetcli-fb          # Ubuntu
yum install targetcli              # CentOS

# 配置target
targetcli
/> cd /backstores/block
/> create name=disk01 dev=/dev/sdb
/> cd /iscsi
/> create iqn.2025-01.com.example:target1
/> cd iqn.2025-01.com.example:target1/tpg1/luns
/> create /backstores/block/disk01
/> cd ../acls
/> create iqn.2025-01.com.example:initiator1
/> cd /
/> saveconfig
/> exit

# iSCSI Initiator (客户端)
# 安装initiator
apt install open-iscsi            # Ubuntu
yum install iscsi-initiator-utils # CentOS

# 配置initiator名称
echo "InitiatorName=iqn.2025-01.com.example:initiator1" > /etc/iscsi/initiatorname.iscsi

# 发现target
iscsiadm -m discovery -t st -p 192.168.1.10

# 登录target
iscsiadm -m node --targetname iqn.2025-01.com.example:target1 --portal 192.168.1.10:3260 --login

# 查看会话
iscsiadm -m session

# 登出target
iscsiadm -m node --targetname iqn.2025-01.com.example:target1 --portal 192.168.1.10:3260 --logout
```

---

## 💡 使用技巧

### 命令别名

在 `~/.bashrc` 或 `~/.zshrc` 中添加常用命令别名：

```bash
# Docker别名
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias dl='docker logs'
alias de='docker exec -it'

# Kubernetes别名
alias k='kubectl'
alias kg='kubectl get'
alias kd='kubectl describe'
alias kl='kubectl logs'
alias ke='kubectl exec -it'
alias kgp='kubectl get pods'
alias kgn='kubectl get nodes'

# 系统别名
alias ll='ls -lah'
alias lt='ls -ltrh'
alias ..='cd ..'
alias ...='cd ../..'
```

---

### Tab补全

#### Docker补全

```bash
# Ubuntu/Debian
apt install bash-completion
source /usr/share/bash-completion/bash_completion

# CentOS/RHEL
yum install bash-completion
```

#### Kubectl补全

```bash
# Bash
echo 'source <(kubectl completion bash)' >>~/.bashrc
echo 'complete -F __start_kubectl k' >>~/.bashrc  # k别名补全

# Zsh
echo 'source <(kubectl completion zsh)' >>~/.zshrc
```

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19  
**维护状态**: ✅ 完成

---

> 💡 **提示**:
>
> - 建议将常用命令添加到 `.bashrc` 别名中
> - 使用 `man <command>` 查看命令详细文档
> - 使用 `<command> --help` 查看命令帮助
