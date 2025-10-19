# 02 - Kubernetes存储基础

**作者**: 云原生存储专家团队  
**创建日期**: 2025-10-19  
**最后更新**: 2025-10-19  
**版本**: v1.0

---

## 📋 本章导航

- [02 - Kubernetes存储基础](#02---kubernetes存储基础)
  - [📋 本章导航](#-本章导航)
  - [1. Volume类型详解](#1-volume类型详解)
    - [1.1 临时存储](#11-临时存储)
      - [emptyDir](#emptydir)
    - [1.2 节点本地存储](#12-节点本地存储)
      - [hostPath](#hostpath)
    - [1.3 配置与密钥](#13-配置与密钥)
      - [ConfigMap](#configmap)
      - [Secret](#secret)
    - [1.4 投射卷](#14-投射卷)
      - [Projected Volume](#projected-volume)
    - [1.5 特殊用途Volume](#15-特殊用途volume)
      - [downwardAPI](#downwardapi)
  - [2. PV和PVC深入](#2-pv和pvc深入)
    - [2.1 绑定机制](#21-绑定机制)
    - [2.2 回收策略](#22-回收策略)
    - [2.3 扩容机制](#23-扩容机制)
    - [2.4 访问模式详解](#24-访问模式详解)
  - [3. StorageClass高级特性](#3-storageclass高级特性)
    - [3.1 参数配置](#31-参数配置)
    - [3.2 拓扑感知](#32-拓扑感知)
    - [3.3 卷绑定模式](#33-卷绑定模式)
    - [3.4 允许卷扩展](#34-允许卷扩展)
  - [4. Volume快照和克隆](#4-volume快照和克隆)
    - [4.1 VolumeSnapshot](#41-volumesnapshot)
    - [4.2 VolumeSnapshotClass](#42-volumesnapshotclass)
    - [4.3 克隆机制](#43-克隆机制)
    - [4.4 实战案例](#44-实战案例)
  - [5. 实战案例](#5-实战案例)
    - [5.1 MySQL with PVC](#51-mysql-with-pvc)
    - [5.2 WordPress with NFS](#52-wordpress-with-nfs)
    - [5.3 Redis with HostPath](#53-redis-with-hostpath)
  - [6. 总结](#6-总结)
    - [6.1 本章要点](#61-本章要点)
    - [6.2 下一步学习](#62-下一步学习)
    - [6.3 最佳实践总结](#63-最佳实践总结)

---

## 1. Volume类型详解

Kubernetes支持多种Volume类型，适用于不同场景。

### 1.1 临时存储

#### emptyDir

**特点**:

- Pod创建时创建
- Pod删除时删除
- 同一Pod内多容器共享
- 默认存储在节点磁盘上

**适用场景**:

- 临时缓存
- 容器间数据交换
- Checkpoint保存

**示例1: 基本使用**:

```yaml
# emptydir-basic.yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-demo
spec:
  containers:
  - name: writer
    image: busybox
    command: ["/bin/sh"]
    args:
      - -c
      - |
        echo "Writing data every 5s..."
        while true; do
          date >> /data/log.txt
          sleep 5
        done
    volumeMounts:
    - name: cache
      mountPath: /data
  
  - name: reader
    image: busybox
    command: ["/bin/sh"]
    args:
      - -c
      - |
        echo "Reading data every 10s..."
        while true; do
          echo "=== Latest 5 lines ==="
          tail -n 5 /data/log.txt 2>/dev/null || echo "No data yet"
          sleep 10
        done
    volumeMounts:
    - name: cache
      mountPath: /data
      readOnly: true
  
  volumes:
  - name: cache
    emptyDir: {}
```

**部署和验证**:

```bash
# 1. 创建Pod
kubectl apply -f emptydir-basic.yaml

# 2. 查看Pod状态
kubectl get pod emptydir-demo

# 3. 查看writer日志
kubectl logs emptydir-demo -c writer

# 4. 查看reader日志
kubectl logs emptydir-demo -c reader

# 5. 验证数据共享
kubectl exec emptydir-demo -c writer -- cat /data/log.txt

# 6. 清理
kubectl delete pod emptydir-demo
```

**示例2: 内存emptyDir**:

```yaml
# emptydir-memory.yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-memory
spec:
  containers:
  - name: app
    image: nginx:latest
    volumeMounts:
    - name: cache
      mountPath: /cache
    resources:
      limits:
        memory: "256Mi"
      requests:
        memory: "128Mi"
  
  volumes:
  - name: cache
    emptyDir:
      medium: Memory  # 使用tmpfs (RAM)
      sizeLimit: 100Mi  # 限制大小
```

**使用场景**:

- 需要极高IOPS的临时数据
- 容器内存缓存
- 临时文件处理

**注意事项**:

```yaml
emptyDir内存模式限制:
  ⚠️ 计入容器内存限制
  ⚠️ 节点重启数据丢失
  ⚠️ 需要合理设置sizeLimit
  ⚠️ OOM可能导致Pod驱逐
```

---

### 1.2 节点本地存储

#### hostPath

**特点**:

- 直接挂载节点目录
- Pod删除后数据保留
- 绑定到特定节点
- ⚠️ 安全风险（需谨慎使用）

**Type类型**:

```yaml
hostPath Type类型:

DirectoryOrCreate:
  - 如果目录不存在则创建 (0755权限)
  - 推荐用于通用场景

Directory:
  - 必须存在的目录
  - 如果不存在则Pod启动失败

FileOrCreate:
  - 如果文件不存在则创建
  - 用于配置文件

File:
  - 必须存在的文件

Socket:
  - Unix socket (如 Docker socket)

CharDevice:
  - 字符设备

BlockDevice:
  - 块设备
```

**示例1: 日志收集**:

```yaml
# hostpath-logs.yaml
apiVersion: v1
kind: Pod
metadata:
  name: log-collector
spec:
  nodeSelector:
    kubernetes.io/hostname: worker-node-1  # 指定节点
  
  containers:
  - name: app
    image: nginx:latest
    volumeMounts:
    - name: logs
      mountPath: /var/log/nginx
  
  - name: log-processor
    image: busybox
    command: ["/bin/sh"]
    args:
      - -c
      - |
        echo "Monitoring logs..."
        tail -f /logs/access.log
    volumeMounts:
    - name: logs
      mountPath: /logs
      readOnly: true
  
  volumes:
  - name: logs
    hostPath:
      path: /var/log/pods/nginx
      type: DirectoryOrCreate
```

**示例2: Docker Socket访问**:

```yaml
# hostpath-docker.yaml
apiVersion: v1
kind: Pod
metadata:
  name: docker-cli
spec:
  containers:
  - name: docker
    image: docker:latest
    command: ["sleep", "infinity"]
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
    securityContext:
      privileged: true  # 需要特权模式
  
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
      type: Socket
```

**安全注意事项**:

```yaml
hostPath安全风险:

高风险场景:
  ❌ 挂载 /etc, /var, /root
  ❌ 挂载 Docker socket
  ❌ 挂载设备文件

安全建议:
  ✅ 使用PodSecurityPolicy限制
  ✅ 只读挂载
  ✅ 限制特定节点
  ✅ 避免在生产环境使用
  ✅ 考虑使用local PV替代

替代方案:
  - Local PersistentVolume
  - 分布式存储 (Ceph, NFS)
  - CSI驱动
```

---

### 1.3 配置与密钥

#### ConfigMap

**特点**:

- 存储非敏感配置
- 支持文件和环境变量
- 支持热更新

**示例1: 配置文件挂载**:

```yaml
# configmap-file.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    user nginx;
    worker_processes auto;
    error_log /var/log/nginx/error.log warn;
    pid /var/run/nginx.pid;

    events {
        worker_connections 1024;
    }

    http {
        include /etc/nginx/mime.types;
        default_type application/octet-stream;
        
        log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';
        
        access_log /var/log/nginx/access.log main;
        
        sendfile on;
        keepalive_timeout 65;
        
        server {
            listen 80;
            server_name localhost;
            
            location / {
                root /usr/share/nginx/html;
                index index.html;
            }
        }
    }

  index.html: |
    <!DOCTYPE html>
    <html>
    <head><title>Welcome</title></head>
    <body>
        <h1>Hello from ConfigMap!</h1>
    </body>
    </html>

---
apiVersion: v1
kind: Pod
metadata:
  name: nginx-configmap
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
    volumeMounts:
    - name: config
      mountPath: /etc/nginx/nginx.conf
      subPath: nginx.conf  # 只挂载单个文件
    - name: config
      mountPath: /usr/share/nginx/html/index.html
      subPath: index.html
  
  volumes:
  - name: config
    configMap:
      name: nginx-config
```

**示例2: 环境变量**:

```yaml
# configmap-env.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_HOST: "mysql.default.svc.cluster.local"
  DATABASE_PORT: "3306"
  DATABASE_NAME: "myapp"
  LOG_LEVEL: "info"
  CACHE_ENABLED: "true"

---
apiVersion: v1
kind: Pod
metadata:
  name: app-with-config
spec:
  containers:
  - name: app
    image: busybox
    command: ["sh", "-c", "env | grep -E '(DATABASE|LOG|CACHE)' && sleep 3600"]
    envFrom:
    - configMapRef:
        name: app-config  # 导入所有key
    env:
    - name: CUSTOM_VAR  # 单独配置
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: DATABASE_HOST
```

**热更新机制**:

```yaml
ConfigMap热更新:

挂载为Volume:
  - kubelet定期同步 (默认60s)
  - 应用需要监听文件变化
  - subPath挂载不会更新

环境变量:
  ❌ 不支持热更新
  - 需要重启Pod

验证更新:
  kubectl edit configmap nginx-config
  # 等待60s
  kubectl exec nginx-configmap -- cat /etc/nginx/nginx.conf
```

---

#### Secret

**特点**:

- 存储敏感数据（密码、Token、密钥）
- Base64编码（非加密）
- 支持加密存储（EncryptionConfiguration）

**示例1: 数据库密码**:

```yaml
# secret-db.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  # echo -n 'admin' | base64
  username: YWRtaW4=
  # echo -n 'P@ssw0rd' | base64
  password: UEBzc3cwcmQ=

---
apiVersion: v1
kind: Pod
metadata:
  name: app-with-secret
spec:
  containers:
  - name: app
    image: mysql:8.0
    env:
    - name: MYSQL_ROOT_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
    - name: MYSQL_USER
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
```

**示例2: TLS证书**:

```yaml
# secret-tls.yaml
apiVersion: v1
kind: Secret
metadata:
  name: tls-secret
type: kubernetes.io/tls
data:
  tls.crt: LS0tLS1CRUdJTi... # base64编码的证书
  tls.key: LS0tLS1CRUdJTi... # base64编码的私钥

---
apiVersion: v1
kind: Pod
metadata:
  name: nginx-tls
spec:
  containers:
  - name: nginx
    image: nginx:latest
    volumeMounts:
    - name: tls
      mountPath: /etc/nginx/ssl
      readOnly: true
  
  volumes:
  - name: tls
    secret:
      secretName: tls-secret
      items:
      - key: tls.crt
        path: server.crt
      - key: tls.key
        path: server.key
        mode: 0600  # 设置文件权限
```

**创建Secret的方式**:

```bash
# 1. 从文件创建
kubectl create secret generic db-secret \
  --from-file=username.txt \
  --from-file=password.txt

# 2. 从字面值创建
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password='P@ssw0rd'

# 3. 从TLS证书创建
kubectl create secret tls tls-secret \
  --cert=server.crt \
  --key=server.key

# 4. Docker镜像拉取Secret
kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=myuser \
  --docker-password=mypass \
  --docker-email=myemail@example.com
```

**安全最佳实践**:

```yaml
Secret安全建议:

1. 加密存储:
   ✅ 启用EncryptionConfiguration
   ✅ 使用KMS (Key Management Service)
   ✅ 定期轮换加密密钥

2. 访问控制:
   ✅ RBAC最小权限
   ✅ 限制list/watch权限
   ✅ 使用ServiceAccount

3. 外部密钥管理:
   ✅ HashiCorp Vault
   ✅ AWS Secrets Manager
   ✅ Azure Key Vault
   ✅ External Secrets Operator

4. 审计:
   ✅ 启用审计日志
   ✅ 监控Secret访问
   ✅ 告警异常访问
```

---

### 1.4 投射卷

#### Projected Volume

**特点**:

- 将多个Volume源合并到一个目录
- 支持ConfigMap、Secret、DownwardAPI、ServiceAccountToken

**示例1: 合并多个源**:

```yaml
# projected-volume.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  config.yaml: |
    app: myapp
    version: 1.0

---
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
stringData:
  api-key: "secret-api-key-12345"

---
apiVersion: v1
kind: Pod
metadata:
  name: projected-demo
  labels:
    app: myapp
spec:
  serviceAccountName: default
  containers:
  - name: app
    image: busybox
    command: ["sh", "-c", "ls -la /projected && cat /projected/* && sleep 3600"]
    volumeMounts:
    - name: all-in-one
      mountPath: /projected
      readOnly: true
  
  volumes:
  - name: all-in-one
    projected:
      sources:
      # 1. ConfigMap
      - configMap:
          name: app-config
          items:
          - key: config.yaml
            path: config.yaml
      
      # 2. Secret
      - secret:
          name: app-secret
          items:
          - key: api-key
            path: secret/api-key
      
      # 3. DownwardAPI (Pod元数据)
      - downwardAPI:
          items:
          - path: "labels"
            fieldRef:
              fieldPath: metadata.labels
          - path: "annotations"
            fieldRef:
              fieldPath: metadata.annotations
          - path: "namespace"
            fieldRef:
              fieldPath: metadata.namespace
          - path: "name"
            fieldRef:
              fieldPath: metadata.name
      
      # 4. ServiceAccount Token
      - serviceAccountToken:
          path: token
          expirationSeconds: 3600
          audience: api
```

**验证**:

```bash
# 1. 创建资源
kubectl apply -f projected-volume.yaml

# 2. 查看合并后的目录结构
kubectl exec projected-demo -- ls -la /projected

# 输出:
# total 0
# drwxrwxrwt 3 root root  140 Oct 19 12:00 .
# drwxr-xr-x 1 root root 4096 Oct 19 12:00 ..
# drwxr-xr-x 2 root root   60 Oct 19 12:00 ..2025_10_19_12_00_00.123456789
# lrwxrwxrwx 1 root root   32 Oct 19 12:00 ..data -> ..2025_10_19_12_00_00.123456789
# lrwxrwxrwx 1 root root   18 Oct 19 12:00 config.yaml -> ..data/config.yaml
# lrwxrwxrwx 1 root root   13 Oct 19 12:00 labels -> ..data/labels
# lrwxrwxrwx 1 root root   11 Oct 19 12:00 token -> ..data/token
# drwxr-xr-x 2 root root   60 Oct 19 12:00 secret

# 3. 查看内容
kubectl exec projected-demo -- cat /projected/config.yaml
kubectl exec projected-demo -- cat /projected/secret/api-key
kubectl exec projected-demo -- cat /projected/labels
kubectl exec projected-demo -- cat /projected/token
```

---

### 1.5 特殊用途Volume

#### downwardAPI

**特点**:

- 将Pod/Container元数据暴露给容器
- 支持字段和资源限制

**示例: 完整元数据暴露**:

```yaml
# downwardapi-full.yaml
apiVersion: v1
kind: Pod
metadata:
  name: downwardapi-demo
  labels:
    app: myapp
    env: production
  annotations:
    version: "1.0.0"
    build: "2025-10-19"
spec:
  containers:
  - name: app
    image: busybox
    command: ["sh", "-c", "cat /etc/podinfo/* && echo && env | grep MY_ && sleep 3600"]
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    
    # 方式1: 环境变量
    env:
    - name: MY_POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    - name: MY_POD_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: metadata.namespace
    - name: MY_POD_IP
      valueFrom:
        fieldRef:
          fieldPath: status.podIP
    - name: MY_NODE_NAME
      valueFrom:
        fieldRef:
          fieldPath: spec.nodeName
    - name: MY_CPU_REQUEST
      valueFrom:
        resourceFieldRef:
          containerName: app
          resource: requests.cpu
    - name: MY_MEM_LIMIT
      valueFrom:
        resourceFieldRef:
          containerName: app
          resource: limits.memory
    
    # 方式2: Volume文件
    volumeMounts:
    - name: podinfo
      mountPath: /etc/podinfo
      readOnly: true
  
  volumes:
  - name: podinfo
    downwardAPI:
      items:
      - path: "labels"
        fieldRef:
          fieldPath: metadata.labels
      - path: "annotations"
        fieldRef:
          fieldPath: metadata.annotations
      - path: "pod_name"
        fieldRef:
          fieldPath: metadata.name
      - path: "pod_namespace"
        fieldRef:
          fieldPath: metadata.namespace
      - path: "cpu_limit"
        resourceFieldRef:
          containerName: app
          resource: limits.cpu
          divisor: 1m
      - path: "mem_request"
        resourceFieldRef:
          containerName: app
          resource: requests.memory
          divisor: 1Mi
```

**可用字段**:

```yaml
fieldRef支持的字段:
  metadata.name: Pod名称
  metadata.namespace: 命名空间
  metadata.uid: Pod UID
  metadata.labels: 所有标签
  metadata.annotations: 所有注解
  spec.nodeName: 节点名
  spec.serviceAccountName: ServiceAccount
  status.podIP: Pod IP地址
  status.hostIP: 节点IP地址

resourceFieldRef支持的字段:
  requests.cpu: CPU请求
  requests.memory: 内存请求
  limits.cpu: CPU限制
  limits.memory: 内存限制
  
  divisor选项:
    CPU: 1 (核心), 1m (毫核)
    Memory: 1 (字节), 1Ki, 1Mi, 1Gi
```

---

## 2. PV和PVC深入

### 2.1 绑定机制

**PV和PVC的绑定过程**:

```yaml
绑定流程:

1. 用户创建PVC
   ↓
2. PVC Controller扫描PVC
   ↓
3. 查找匹配的PV
   匹配条件:
     - StorageClass相同 (或都为空)
     - AccessMode兼容
     - 容量满足 (PV >= PVC)
     - Selector匹配 (如果有)
   ↓
4. 绑定PVC到PV
   - PVC.Status.Phase = Bound
   - PV.Status.Phase = Bound
   - 双向引用
   ↓
5. Pod可以使用PVC
```

**示例1: 标签选择器绑定**:

```yaml
# pv-with-labels.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: fast-ssd-pv
  labels:
    type: fast
    media: ssd
    zone: us-west-1a
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast-storage
  hostPath:
    path: /mnt/fast-ssd

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fast-ssd-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: fast-storage
  selector:
    matchLabels:
      type: fast
      media: ssd
    matchExpressions:
    - key: zone
      operator: In
      values:
      - us-west-1a
      - us-west-1b
```

**验证绑定**:

```bash
# 1. 创建PV
kubectl apply -f pv-with-labels.yaml

# 2. 检查PV状态
kubectl get pv fast-ssd-pv
# NAME          CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      STORAGECLASS
# fast-ssd-pv   100Gi      RWO            Retain           Available   fast-storage

# 3. 创建PVC
kubectl apply -f pvc-with-selector.yaml

# 4. 验证绑定
kubectl get pvc fast-ssd-pvc
# NAME           STATUS   VOLUME        CAPACITY   ACCESS MODES   STORAGECLASS
# fast-ssd-pvc   Bound    fast-ssd-pv   100Gi      RWO            fast-storage

kubectl get pv fast-ssd-pv
# NAME          CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM
# fast-ssd-pv   100Gi      RWO            Retain           Bound    default/fast-ssd-pvc

# 5. 查看绑定详情
kubectl describe pvc fast-ssd-pvc
kubectl describe pv fast-ssd-pv
```

---

### 2.2 回收策略

**三种回收策略**:

```yaml
persistentVolumeReclaimPolicy:

1. Retain (保留):
   - PVC删除后PV保留
   - 数据保留
   - 状态变为Released
   - 需要手动清理和回收
   - 🎯 推荐用于生产环境

2. Delete (删除):
   - PVC删除后PV自动删除
   - 底层存储资源删除
   - 数据永久丢失
   - 🎯 动态供应默认策略

3. Recycle (回收 - 已废弃):
   - 执行 rm -rf /volume/*
   - ❌ Kubernetes 1.15+ 废弃
   - ❌ 不要使用
```

**示例: 回收策略对比**:

```yaml
# pv-reclaim-policies.yaml

# 策略1: Retain (推荐生产环境)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-retain
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data-retain

---
# 策略2: Delete (动态供应默认)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-delete
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  storageClassName: manual
  hostPath:
    path: /mnt/data-delete
```

**回收流程演示**:

```bash
# === Retain策略测试 ===

# 1. 创建PV和PVC
kubectl apply -f pv-retain.yaml
kubectl apply -f pvc-retain.yaml

# 2. 验证绑定
kubectl get pv pv-retain
# STATUS: Bound

# 3. 创建Pod并写入数据
kubectl apply -f pod-with-pvc-retain.yaml
kubectl exec pod-retain -- sh -c 'echo "important data" > /data/file.txt'

# 4. 删除Pod和PVC
kubectl delete pod pod-retain
kubectl delete pvc pvc-retain

# 5. 检查PV状态
kubectl get pv pv-retain
# STATUS: Released (数据保留，但不可绑定新PVC)

# 6. 手动回收PV
# 方式1: 删除claimRef，手动清理数据
kubectl patch pv pv-retain -p '{"spec":{"claimRef":null}}'
# 方式2: 删除PV并重建
kubectl delete pv pv-retain


# === Delete策略测试 ===

# 1. 创建PV和PVC
kubectl apply -f pv-delete.yaml
kubectl apply -f pvc-delete.yaml

# 2. 删除PVC
kubectl delete pvc pvc-delete

# 3. 检查PV
kubectl get pv pv-delete
# PV自动删除 (Not Found)
```

**修改回收策略**:

```bash
# 修改现有PV的回收策略
kubectl patch pv <pv-name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'

# 验证修改
kubectl get pv <pv-name> -o yaml | grep persistentVolumeReclaimPolicy
```

---

### 2.3 扩容机制

**前提条件**:

- StorageClass设置`allowVolumeExpansion: true`
- CSI驱动支持扩容
- PV使用CSI驱动

**示例: 在线扩容**:

```yaml
# storage-expand.yaml

# 1. 创建支持扩容的StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expandable-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true  # 关键配置

---
# 2. 创建PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: expandable-pv
spec:
  capacity:
    storage: 10Gi  # 初始容量
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: expandable-storage
  hostPath:
    path: /mnt/expandable-data

---
# 3. 创建PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: expandable-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi  # 初始请求
  storageClassName: expandable-storage

---
# 4. 使用PVC的Pod
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ["sleep", "infinity"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: expandable-pvc
```

**扩容步骤**:

```bash
# 1. 部署初始资源
kubectl apply -f storage-expand.yaml

# 2. 检查初始容量
kubectl get pvc expandable-pvc
# CAPACITY: 10Gi

kubectl exec app-pod -- df -h /data
# Size: 10G

# 3. 扩容PVC (编辑YAML)
kubectl edit pvc expandable-pvc
# 修改 spec.resources.requests.storage: 10Gi -> 20Gi

# 或使用patch
kubectl patch pvc expandable-pvc -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# 4. 等待扩容完成
kubectl get pvc expandable-pvc -w
# CAPACITY: 10Gi -> 20Gi (可能需要几秒到几分钟)

# 5. 验证扩容 (可能需要重启Pod)
kubectl delete pod app-pod
kubectl apply -f pod-with-pvc.yaml
kubectl exec app-pod -- df -h /data
# Size: 20G

# 6. 查看扩容事件
kubectl describe pvc expandable-pvc
# Events:
#   Normal  VolumeResizeSuccessful  FileSystemResizeRequired
#   Normal  FileSystemResizeSuccessful  MountVolume.NodeExpandVolume succeeded
```

**扩容类型**:

```yaml
两阶段扩容:

Phase 1: Controller Expansion (控制器侧扩容)
  - 扩展底层存储卷
  - PV.Spec.Capacity更新
  - PVC添加Condition: FileSystemResizeRequired

Phase 2: Node Expansion (节点侧扩容)
  - 扩展文件系统
  - 需要重启Pod (某些CSI驱动)
  - PVC.Status.Capacity更新

在线扩容 vs 离线扩容:
  在线扩容 (支持):
    ✅ 云块存储 (EBS, Azure Disk)
    ✅ Ceph RBD
    - 无需重启Pod
  
  离线扩容 (需要):
    ⚠️ hostPath, local
    ⚠️ 部分CSI驱动
    - 需要删除Pod，扩容，重建Pod
```

**注意事项**:

```yaml
扩容限制:

✅ 支持:
  - 扩大容量 (10Gi -> 20Gi)
  - 在线扩容 (取决于CSI驱动)

❌ 不支持:
  - 缩小容量 (20Gi -> 10Gi) - Kubernetes不允许
  - emptyDir, hostPath (没有StorageClass)
  - 某些旧的in-tree驱动

⚠️ 注意:
  - 扩容可能需要时间
  - 部分驱动需要重启Pod
  - 检查CSI驱动文档
  - 底层存储必须有足够空间
```

---

### 2.4 访问模式详解

**三种访问模式**:

```yaml
AccessModes:

1. ReadWriteOnce (RWO):
   - 单节点读写
   - 最常用
   - 支持: 几乎所有存储
   - 适用: 数据库、单实例应用

2. ReadOnlyMany (ROX):
   - 多节点只读
   - 较少使用
   - 支持: NFS, CephFS, 对象存储
   - 适用: 静态资源、共享配置

3. ReadWriteMany (RWX):
   - 多节点读写
   - 生产常用
   - 支持: NFS, CephFS, GlusterFS
   - 适用: 共享存储、多Pod应用

4. ReadWriteOncePod (RWOP) - Kubernetes 1.22+:
   - 单Pod读写
   - 更严格的RWO
   - 支持: 需要CSI驱动支持
   - 适用: 防止同节点多Pod访问
```

**存储类型支持矩阵**:

| 存储类型 | RWO | ROX | RWX | RWOP |
|---------|-----|-----|-----|------|
| **云块存储** | | | | |
| AWS EBS | ✅ | ❌ | ❌ | ✅ |
| Azure Disk | ✅ | ❌ | ❌ | ✅ |
| GCE PD | ✅ | ❌ | ❌ | ✅ |
| **文件存储** | | | | |
| NFS | ✅ | ✅ | ✅ | ⚠️ |
| CephFS | ✅ | ✅ | ✅ | ⚠️ |
| Azure Files | ✅ | ✅ | ✅ | ⚠️ |
| AWS EFS | ✅ | ✅ | ✅ | ⚠️ |
| **分布式块存储** | | | | |
| Ceph RBD | ✅ | ✅ | ❌ | ✅ |
| Longhorn | ✅ | ✅ | ✅ | ✅ |
| **本地存储** | | | | |
| hostPath | ✅ | ✅ | ✅ | ⚠️ |
| local PV | ✅ | ❌ | ❌ | ✅ |

**示例: 多Pod共享存储**:

```yaml
# rwx-shared-storage.yaml

# 1. NFS PV (支持RWX)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteMany  # 多节点读写
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs
  nfs:
    server: 192.168.1.100
    path: /shared/data

---
# 2. PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shared-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 50Gi
  storageClassName: nfs

---
# 3. 多个Pod使用同一个PVC
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3  # 3个副本共享存储
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        volumeMounts:
        - name: shared-data
          mountPath: /usr/share/nginx/html
      volumes:
      - name: shared-data
        persistentVolumeClaim:
          claimName: shared-pvc  # 所有Pod使用同一个PVC
```

**验证共享**:

```bash
# 1. 部署
kubectl apply -f rwx-shared-storage.yaml

# 2. 等待所有Pod就绪
kubectl wait --for=condition=Ready pod -l app=web --timeout=300s

# 3. 获取Pod列表
kubectl get pods -l app=web
# NAME                      READY   STATUS    NODE
# web-app-xxx-aaa           1/1     Running   node1
# web-app-xxx-bbb           1/1     Running   node2
# web-app-xxx-ccc           1/1     Running   node3

# 4. 在第一个Pod写入数据
POD1=$(kubectl get pods -l app=web -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD1 -- sh -c 'echo "Hello from Pod1" > /usr/share/nginx/html/index.html'

# 5. 在其他Pod验证数据可见
POD2=$(kubectl get pods -l app=web -o jsonpath='{.items[1].metadata.name}')
POD3=$(kubectl get pods -l app=web -o jsonpath='{.items[2].metadata.name}')
kubectl exec $POD2 -- cat /usr/share/nginx/html/index.html
kubectl exec $POD3 -- cat /usr/share/nginx/html/index.html
# Output (所有Pod): Hello from Pod1
```

---

## 3. StorageClass高级特性

### 3.1 参数配置

**StorageClass参数详解**:

```yaml
# storageclass-advanced.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: advanced-storage
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"  # 设置为默认StorageClass

# 存储插件
provisioner: kubernetes.io/aws-ebs

# 插件特定参数
parameters:
  type: gp3  # EBS类型: gp2, gp3, io1, io2, st1, sc1
  iops: "3000"  # 仅gp3, io1, io2
  throughput: "125"  # MB/s，仅gp3
  encrypted: "true"  # 启用加密
  kmsKeyId: "arn:aws:kms:us-east-1:123456789012:key/xxx"  # KMS密钥
  fsType: ext4  # 文件系统类型: ext4, xfs

# 回收策略
reclaimPolicy: Delete  # Retain, Delete

# 卷绑定模式
volumeBindingMode: WaitForFirstConsumer  # Immediate, WaitForFirstConsumer

# 是否允许扩容
allowVolumeExpansion: true

# 挂载选项
mountOptions:
  - debug
  - noatime

# 拓扑约束
allowedTopologies:
- matchLabelExpressions:
  - key: topology.kubernetes.io/zone
    values:
    - us-east-1a
    - us-east-1b
```

**常见存储类型参数**:

```yaml
# AWS EBS
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: aws-ebs-gp3
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
  fsType: ext4
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

---
# Azure Disk
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: azure-disk-premium
provisioner: kubernetes.io/azure-disk
parameters:
  storageaccounttype: Premium_LRS  # Standard_LRS, Premium_LRS, UltraSSD_LRS
  kind: Managed  # Managed, Shared
  cachingmode: ReadOnly  # None, ReadOnly, ReadWrite
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

---
# GCE PD
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gce-pd-ssd
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd  # pd-standard, pd-ssd, pd-balanced
  replication-type: regional-pd  # none, regional-pd
  fstype: ext4
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

---
# Ceph RBD (Rook)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-ceph-block
provisioner: rook-ceph.rbd.csi.ceph.com
parameters:
  clusterID: rook-ceph
  pool: replicapool
  imageFormat: "2"
  imageFeatures: layering
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/controller-expand-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/controller-expand-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-rbd-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
  csi.storage.k8s.io/fstype: ext4
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

---
# CephFS (Rook)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-cephfs
provisioner: rook-ceph.cephfs.csi.ceph.com
parameters:
  clusterID: rook-ceph
  fsName: myfs
  pool: myfs-data0
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/controller-expand-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/controller-expand-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-cephfs-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

---

### 3.2 拓扑感知

**拓扑约束**:

```yaml
# topology-aware-storageclass.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: topology-aware
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
volumeBindingMode: WaitForFirstConsumer  # 必须设置
allowedTopologies:
- matchLabelExpressions:
  - key: topology.kubernetes.io/zone
    values:
    - us-east-1a
    - us-east-1b
  - key: node.kubernetes.io/instance-type
    values:
    - m5.large
    - m5.xlarge
```

**拓扑感知优势**:

```yaml
拓扑感知的好处:

1. 就近调度:
   - Pod调度到存储所在可用区
   - 降低延迟
   - 避免跨AZ流量费用

2. 高可用:
   - 避免单点故障
   - 跨可用区部署

3. 合规要求:
   - 数据必须在特定区域
   - 满足监管要求

示例场景:
  AWS EBS:
    - us-east-1a的EBS只能挂载到us-east-1a的EC2
    - 拓扑约束确保Pod调度到正确的AZ
```

**示例: 拓扑感知调度**:

```yaml
# topology-demo.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: topology-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: topology-aware

---
apiVersion: v1
kind: Pod
metadata:
  name: topology-pod
spec:
  containers:
  - name: app
    image: nginx:latest
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: topology-pvc
```

**验证拓扑调度**:

```bash
# 1. 部署
kubectl apply -f topology-demo.yaml

# 2. 检查PVC (Pending状态，等待Pod)
kubectl get pvc topology-pvc
# STATUS: Pending (WaitForFirstConsumer)

# 3. 创建Pod
kubectl apply -f topology-pod.yaml

# 4. 检查Pod调度
kubectl get pod topology-pod -o wide
# NODE列会显示节点，确认在us-east-1a或us-east-1b

# 5. 检查PVC绑定
kubectl get pvc topology-pvc
# STATUS: Bound

# 6. 查看PV的拓扑信息
kubectl get pv <pv-name> -o yaml | grep -A5 nodeAffinity
```

---

### 3.3 卷绑定模式

**两种绑定模式**:

```yaml
volumeBindingMode:

1. Immediate (立即绑定):
   - PVC创建时立即供应PV
   - 不考虑Pod调度
   - 可能导致调度失败
   
   问题场景:
     - PV在zone-a创建
     - Pod只能调度到zone-b
     - Pod无法启动
   
   适用:
     - 拓扑无关的存储 (NFS, CephFS)
     - 单可用区集群

2. WaitForFirstConsumer (延迟绑定 - 推荐):
   - 等待第一个使用PVC的Pod
   - 根据Pod的调度约束供应PV
   - 确保PV在Pod可达的拓扑位置
   
   优势:
     ✅ 拓扑感知
     ✅ 避免调度失败
     ✅ 资源利用最优
   
   适用:
     - 有拓扑约束的存储 (EBS, Azure Disk)
     - 多可用区集群
     - 生产环境推荐
```

**对比示例**:

```yaml
# 方式1: Immediate (立即绑定)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: immediate-sc
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
volumeBindingMode: Immediate  # 立即绑定
allowVolumeExpansion: true

---
# 方式2: WaitForFirstConsumer (延迟绑定 - 推荐)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: wait-for-consumer-sc
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
volumeBindingMode: WaitForFirstConsumer  # 延迟绑定
allowVolumeExpansion: true
allowedTopologies:
- matchLabelExpressions:
  - key: topology.kubernetes.io/zone
    values:
    - us-east-1a
    - us-east-1b
```

---

### 3.4 允许卷扩展

**配置示例**:

```yaml
# expandable-storageclass.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expandable
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true  # 启用扩容
```

**CSI驱动扩容能力检查**:

```bash
# 查看CSI驱动支持的能力
kubectl get csidriver
# NAME                        ATTACHREQUIRED   PODINFOONMOUNT   STORAGECAPACITY   VOLUMELIFECYCLEMODES
# ebs.csi.aws.com             true             false            false             Persistent,Ephemeral

# 查看CSI驱动详情
kubectl describe csidriver ebs.csi.aws.com

# 查看StorageClass是否支持扩容
kubectl get storageclass expandable -o yaml | grep allowVolumeExpansion
# allowVolumeExpansion: true
```

## 4. Volume快照和克隆

### 4.1 VolumeSnapshot

**Volume快照特性**:

- Kubernetes 1.20+ GA
- 需要CSI驱动支持
- 保存卷的时间点副本
- 用于备份和恢复

**示例: 创建快照**:

```yaml
# volume-snapshot.yaml

# 1. VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapshot-class
driver: ebs.csi.aws.com  # CSI驱动
deletionPolicy: Delete  # Retain, Delete
parameters:
  # 驱动特定参数

---
# 2. VolumeSnapshot
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-snapshot
spec:
  volumeSnapshotClassName: csi-snapshot-class
  source:
    persistentVolumeClaim<br>: my-pvc  # 源PVC
```

**完整示例**:

```bash
# 1. 创建PVC和Pod
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: source-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: gp3-storage
---
apiVersion: v1
kind: Pod
metadata:
  name: source-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ["sleep", "infinity"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: source-pvc
EOF

# 2. 等待Pod就绪
kubectl wait --for=condition=Ready pod/source-pod --timeout=300s

# 3. 写入数据
kubectl exec source-pod -- sh -c 'echo "Important data before snapshot" > /data/data.txt'
kubectl exec source-pod -- cat /data/data.txt

# 4. 创建快照
kubectl apply -f - <<EOF
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-snapshot
spec:
  volumeSnapshotClassName: csi-snapshot-class
  source:
    persistentVolumeClaimName: source-pvc
EOF

# 5. 等待快照完成
kubectl wait --for=jsonpath='{.status.readyToUse}'=true volumesnapshot/my-snapshot --timeout=300s

# 6. 查看快照
kubectl get volumesnapshot my-snapshot
# NAME          READYTOUSE   SOURCEPVC    SOURCESNAPSHOTCONTENT   RESTORESIZE   SNAPSHOTCLASS          AGE
# my-snapshot   true         source-pvc                           10Gi          csi-snapshot-class     30s

kubectl describe volumesnapshot my-snapshot

# 7. 修改源数据 (模拟数据损坏)
kubectl exec source-pod -- sh -c 'echo "Corrupted data" > /data/data.txt'
kubectl exec source-pod -- cat /data/data.txt
# Output: Corrupted data

# 8. 从快照恢复
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: restored-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: gp3-storage
  dataSource:
    kind: VolumeSnapshot
    name: my-snapshot
    apiGroup: snapshot.storage.k8s.io
EOF

# 9. 创建Pod使用恢复的PVC
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: restored-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ["sleep", "infinity"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: restored-pvc
EOF

# 10. 验证恢复的数据
kubectl wait --for=condition=Ready pod/restored-pod --timeout=300s
kubectl exec restored-pod -- cat /data/data.txt
# Output: Important data before snapshot (恢复成功!)

# 11. 清理
kubectl delete pod source-pod restored-pod
kubectl delete pvc source-pvc restored-pvc
kubectl delete volumesnapshot my-snapshot
```

---

### 4.2 VolumeSnapshotClass

**参数配置**:

```yaml
# AWS EBS VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: ebs-snapshot-class
driver: ebs.csi.aws.com
deletionPolicy: Delete
parameters:
  tagSpecification_1: "Name=ebs-snapshot"
  tagSpecification_2: "Environment=production"

---
# Azure Disk VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: azure-disk-snapshot-class
driver: disk.csi.azure.com
deletionPolicy: Delete
parameters:
  incremental: "true"  # 增量快照
  resourceGroup: my-resource-group
  tags: "project=myapp,env=prod"

---
# Ceph RBD VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: rook-ceph-snapshot-class
driver: rook-ceph.rbd.csi.ceph.com
deletionPolicy: Delete
parameters:
  clusterID: rook-ceph
  csi.storage.k8s.io/snapshotter-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/snapshotter-secret-namespace: rook-ceph
```

---

### 4.3 克隆机制

**PVC克隆**:

```yaml
# volume-clone.yaml

# 1. 源PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: source-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: gp3-storage

---
# 2. 克隆PVC (dataSource指向源PVC)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cloned-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi  # 必须 >= 源PVC
  storageClassName: gp3-storage  # 必须相同
  dataSource:
    kind: PersistentVolumeClaim
    name: source-pvc
```

**克隆示例**:

```bash
# 1. 创建源PVC和数据
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: original-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard
---
apiVersion: v1
kind: Pod
metadata:
  name: writer-pod
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "echo 'Original data' > /data/file.txt && sleep 3600"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: original-pvc
EOF

# 2. 等待并验证数据
kubectl wait --for=condition=Ready pod/writer-pod --timeout=300s
kubectl exec writer-pod -- cat /data/file.txt
# Output: Original data

# 3. 克隆PVC
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cloned-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard
  dataSource:
    kind: PersistentVolumeClaim
    name: original-pvc
EOF

# 4. 使用克隆的PVC
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: reader-pod
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: cloned-pvc
EOF

# 5. 验证克隆的数据
kubectl wait --for=condition=Ready pod/reader-pod --timeout=300s
kubectl exec reader-pod -- cat /data/file.txt
# Output: Original data (克隆成功!)

# 6. 修改克隆的数据 (不影响原始数据)
kubectl exec reader-pod -- sh -c 'echo "Modified in clone" >> /data/file.txt'
kubectl exec reader-pod -- cat /data/file.txt
# Output:
# Original data
# Modified in clone

kubectl exec writer-pod -- cat /data/file.txt
# Output: Original data (原始数据未改变)
```

---

### 4.4 实战案例

**场景: 数据库备份和恢复**:

```yaml
# database-backup-restore.yaml

# 1. 部署MySQL
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: fast-storage

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "password"
        - name: MYSQL_DATABASE
          value: "myapp"
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-data
        persistentVolumeClaim:
          claimName: mysql-pvc

---
# 2. 创建快照 (定时备份)
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: mysql-snapshot-daily
  labels:
    backup: daily
    date: "2025-10-19"
spec:
  volumeSnapshotClassName: csi-snapshot-class
  source:
    persistentVolumeClaimName: mysql-pvc

---
# 3. 从快照恢复 (灾难恢复)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc-restored
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: fast-storage
  dataSource:
    kind: VolumeSnapshot
    name: mysql-snapshot-daily
    apiGroup: snapshot.storage.k8s.io
```

**自动化备份脚本**:

```bash
#!/bin/bash
# backup-mysql.sh

DATE=$(date +%Y%m%d-%H%M%S)
SNAPSHOT_NAME="mysql-snapshot-${DATE}"

# 创建快照
kubectl apply -f - <<EOF
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: ${SNAPSHOT_NAME}
  labels:
    app: mysql
    backup: auto
    date: "$(date +%Y-%m-%d)"
spec:
  volumeSnapshotClassName: csi-snapshot-class
  source:
    persistentVolumeClaimName: mysql-pvc
EOF

# 等待快照完成
kubectl wait --for=jsonpath='{.status.readyToUse}'=true \
  volumesnapshot/${SNAPSHOT_NAME} --timeout=600s

echo "Backup completed: ${SNAPSHOT_NAME}"

# 清理7天前的快照
CUTOFF_DATE=$(date -d '7 days ago' +%Y-%m-%d)
kubectl get volumesnapshot -l app=mysql,backup=auto -o json | \
  jq -r ".items[] | select(.metadata.labels.date < \"${CUTOFF_DATE}\") | .metadata.name" | \
  xargs -r kubectl delete volumesnapshot
```

---

## 5. 实战案例

### 5.1 MySQL with PVC

**完整部署**:

```yaml
# mysql-with-pvc.yaml

# 1. Secret (数据库密码)
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
type: Opaque
stringData:
  root-password: "MySecurePassword123!"
  user: "appuser"
  password: "AppUserPassword123!"

---
# 2. ConfigMap (MySQL配置)
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
data:
  my.cnf: |
    [mysqld]
    max_connections = 200
    innodb_buffer_pool_size = 1G
    innodb_log_file_size = 256M
    slow_query_log = 1
    slow_query_log_file = /var/lib/mysql/slow.log
    long_query_time = 2

---
# 3. PVC (持久化存储)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: fast-block-storage

---
# 4. StatefulSet (MySQL部署)
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
          name: mysql
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: root-password
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: user
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
        - name: MYSQL_DATABASE
          value: "myapp"
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        - name: mysql-config
          mountPath: /etc/mysql/conf.d/my.cnf
          subPath: my.cnf
        livenessProbe:
          exec:
            command:
            - mysqladmin
            - ping
            - -h
            - localhost
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - mysql
            - -h
            - localhost
            - -u
            - root
            - -p$(MYSQL_ROOT_PASSWORD)
            - -e
            - "SELECT 1"
          initialDelaySeconds: 5
          periodSeconds: 2
      volumes:
      - name: mysql-data
        persistentVolumeClaim:
          claimName: mysql-pvc
      - name: mysql-config
        configMap:
          name: mysql-config

---
# 5. Service (MySQL服务)
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  type: ClusterIP
  ports:
  - port: 3306
    targetPort: 3306
  selector:
    app: mysql
```

**部署和验证**:

```bash
# 1. 部署MySQL
kubectl apply -f mysql-with-pvc.yaml

# 2. 等待Pod就绪
kubectl wait --for=condition=Ready pod -l app=mysql --timeout=300s

# 3. 查看PVC
kubectl get pvc mysql-pvc
# STATUS: Bound

# 4. 连接MySQL
kubectl run mysql-client --rm -it --image=mysql:8.0 -- \
  mysql -h mysql -u root -p'MySecurePassword123!'

# 在MySQL shell中:
mysql> CREATE TABLE test (id INT, name VARCHAR(50));
mysql> INSERT INTO test VALUES (1, 'Hello'), (2, 'World');
mysql> SELECT * FROM test;
# +------+-------+
# | id   | name  |
# +------+-------+
# |    1 | Hello |
# |    2 | World |
# +------+-------+
mysql> exit

# 5. 测试数据持久化
kubectl delete pod -l app=mysql

# 等待Pod重建
kubectl wait --for=condition=Ready pod -l app=mysql --timeout=300s

# 重新连接验证数据
kubectl run mysql-client --rm -it --image=mysql:8.0 -- \
  mysql -h mysql -u root -p'MySecurePassword123!' -e "SELECT * FROM myapp.test;"
# 数据仍然存在!

# 6. 创建备份快照
kubectl apply -f - <<EOF
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: mysql-backup-$(date +%Y%m%d)
spec:
  volumeSnapshotClassName: csi-snapshot-class
  source:
    persistentVolumeClaimName: mysql-pvc
EOF

# 7. 清理
kubectl delete -f mysql-with-pvc.yaml
```

---

### 5.2 WordPress with NFS

**NFS共享存储示例**:

```yaml
# wordpress-nfs.yaml

# 1. NFS PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: wordpress-nfs-pv
spec:
  capacity:
    storage: 50Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs
  nfs:
    server: nfs-server.example.com
    path: /exports/wordpress

---
# 2. PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: wordpress-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 50Gi
  storageClassName: nfs

---
# 3. WordPress Deployment (3副本共享存储)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress
spec:
  replicas: 3  # 多副本共享NFS
  selector:
    matchLabels:
      app: wordpress
  template:
    metadata:
      labels:
        app: wordpress
    spec:
      containers:
      - name: wordpress
        image: wordpress:latest
        ports:
        - containerPort: 80
        env:
        - name: WORDPRESS_DB_HOST
          value: mysql:3306
        - name: WORDPRESS_DB_USER
          value: wordpress
        - name: WORDPRESS_DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: wordpress-secret
              key: db-password
        volumeMounts:
        - name: wordpress-data
          mountPath: /var/www/html
      volumes:
      - name: wordpress-data
        persistentVolumeClaim:
          claimName: wordpress-pvc

---
# 4. Service
apiVersion: v1
kind: Service
metadata:
  name: wordpress
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: wordpress
```

---

### 5.3 Redis with HostPath

**高性能本地存储**:

```yaml
# redis-hostpath.yaml

# 1. hostPath PV (高性能SSD)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: redis-pv
  labels:
    type: local
    performance: high
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-ssd
  hostPath:
    path: /mnt/ssd/redis
    type: DirectoryOrCreate
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - worker-node-1  # 指定节点

---
# 2. PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: local-ssd
  selector:
    matchLabels:
      type: local
      performance: high

---
# 3. Redis Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      nodeSelector:
        kubernetes.io/hostname: worker-node-1  # 与PV同节点
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server"]
        args:
          - --appendonly yes
          - --dir /data
          - --save 900 1
          - --save 300 10
          - --save 60 10000
        volumeMounts:
        - name: redis-data
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
      volumes:
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-pvc

---
# 4. Service
apiVersion: v1
kind: Service
metadata:
  name: redis
spec:
  type: ClusterIP
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    app: redis
```

**性能测试**:

```bash
# 1. 部署Redis
kubectl apply -f redis-hostpath.yaml

# 2. 等待就绪
kubectl wait --for=condition=Ready pod -l app=redis --timeout=300s

# 3. 性能测试
kubectl run redis-benchmark --rm -it --image=redis:7-alpine -- \
  redis-benchmark -h redis -p 6379 -t set,get -n 100000 -q

# 输出示例:
# SET: 85470.09 requests per second
# GET: 89285.71 requests per second

# 4. 数据持久化测试
kubectl exec -it deployment/redis -- redis-cli
127.0.0.1:6379> SET key1 "value1"
127.0.0.1:6379> SET key2 "value2"
127.0.0.1:6379> GET key1
"value1"
127.0.0.1:6379> exit

# 5. 重启Pod
kubectl delete pod -l app=redis
kubectl wait --for=condition=Ready pod -l app=redis --timeout=300s

# 6. 验证数据持久化
kubectl exec -it deployment/redis -- redis-cli GET key1
# "value1" (数据保留!)
```

---

## 6. 总结

### 6.1 本章要点

```yaml
核心知识:
  ✅ Volume类型 (emptyDir, hostPath, ConfigMap, Secret, Projected, DownwardAPI)
  ✅ PV/PVC绑定机制
  ✅ 回收策略 (Retain, Delete)
  ✅ 在线扩容
  ✅ 访问模式 (RWO, ROX, RWX, RWOP)
  ✅ StorageClass高级特性 (参数配置, 拓扑感知, 绑定模式, 扩容)
  ✅ Volume快照和克隆
  ✅ 实战案例 (MySQL, WordPress, Redis)

关键概念:
  - 临时存储 vs 持久化存储
  - 静态供应 vs 动态供应
  - 立即绑定 vs 延迟绑定
  - 控制器侧扩容 vs 节点侧扩容
  - 快照 vs 克隆

最佳实践:
  ✅ 生产环境使用Retain回收策略
  ✅ 启用allowVolumeExpansion
  ✅ 使用WaitForFirstConsumer绑定模式
  ✅ 定期创建快照备份
  ✅ 使用StorageClass标准化
```

### 6.2 下一步学习

```yaml
学习路径:

第03章: Rook/Ceph深度解析
  - Ceph架构与原理
  - Rook Operator部署
  - 块存储、文件存储、对象存储
  - 生产级调优

第04章: Velero备份恢复
  - 集群备份策略
  - 应用迁移
  - 灾难恢复演练

第05章: CSI驱动详解
  - CSI规范深入
  - 自定义CSI驱动
  - CSI Sidecar
  - 故障排查
```

### 6.3 最佳实践总结

```yaml
Volume选择:
  临时数据: emptyDir
  配置文件: ConfigMap
  密钥: Secret
  Pod元数据: DownwardAPI
  持久化数据: PVC

StorageClass配置:
  高性能数据库:
    provisioner: CSI驱动
    parameters:
      type: io2/Premium_LRS
      iops: 高IOPS
    volumeBindingMode: WaitForFirstConsumer
    allowVolumeExpansion: true

  共享文件:
    provisioner: NFS/CephFS
    accessModes: ReadWriteMany
    reclaimPolicy: Retain

  归档备份:
    provisioner: S3/对象存储
    lifecycle: 自动分层

备份策略:
  关键数据:
    - 每日快照
    - 保留7天
    - 异地备份
  
  非关键数据:
    - 每周快照
    - 保留30天
```

---

**相关章节**:

- [01_云原生存储概述与架构](./01_云原生存储概述与架构.md)
- [03_Rook/Ceph深度解析](./03_Rook_Ceph深度解析.md)
- [04_Velero备份恢复](./04_Velero备份恢复.md)

---

**完成日期**: 2025-10-19  
**版本**: v1.0  
**作者**: 云原生存储专家团队

**Tags**: `#Kubernetes` `#Volume` `#PV` `#PVC` `#StorageClass` `#VolumeSnapshot` `#Storage`
