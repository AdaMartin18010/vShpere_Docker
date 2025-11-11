# 04 - Velero备份恢复

**作者**: 云原生存储专家团队
**创建日期**: 2025-10-19
**最后更新**: 2025-10-19
**版本**: v1.0

---

## 📋 本章导航

- [04 - Velero备份恢复](#04---velero备份恢复)
  - [📋 本章导航](#-本章导航)
  - [1. Velero架构与原理](#1-velero架构与原理)
    - [1.1 Velero概述](#11-velero概述)
    - [1.2 核心组件](#12-核心组件)
    - [1.3 备份原理](#13-备份原理)
    - [1.4 恢复原理](#14-恢复原理)
  - [2. Velero部署](#2-velero部署)
    - [2.1 部署前准备](#21-部署前准备)
    - [2.2 安装Velero](#22-安装velero)
    - [2.3 配置对象存储](#23-配置对象存储)
    - [2.4 验证安装](#24-验证安装)
  - [3. 备份策略设计](#3-备份策略设计)
    - [3.1 定时备份](#31-定时备份)
    - [3.2 按需备份](#32-按需备份)
    - [3.3 选择性备份](#33-选择性备份)
    - [3.4 备份生命周期](#34-备份生命周期)
  - [4. 恢复演练](#4-恢复演练)
    - [4.1 完整恢复](#41-完整恢复)
    - [4.2 选择性恢复](#42-选择性恢复)
    - [4.3 跨集群恢复](#43-跨集群恢复)
    - [4.4 灾难恢复演练](#44-灾难恢复演练)
  - [5. 多集群备份](#5-多集群备份)
    - [5.1 多集群架构](#51-多集群架构)
    - [5.2 集中式备份](#52-集中式备份)
    - [5.3 备份复制](#53-备份复制)
  - [6. 应用迁移](#6-应用迁移)
    - [6.1 同版本迁移](#61-同版本迁移)
    - [6.2 跨版本迁移](#62-跨版本迁移)
    - [6.3 跨云迁移](#63-跨云迁移)
  - [7. 最佳实践](#7-最佳实践)
    - [7.1 备份策略](#71-备份策略)
    - [7.2 性能优化](#72-性能优化)
    - [7.3 安全加固](#73-安全加固)
    - [7.4 监控告警](#74-监控告警)
  - [8. 总结](#8-总结)
    - [8.1 本章要点](#81-本章要点)
    - [8.2 推荐资源](#82-推荐资源)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 1. Velero架构与原理

### 1.1 Velero概述

**Velero**（原名Ark）是VMware开源的Kubernetes集群资源备份、恢复和迁移工具。

```yaml
Velero核心特性:
  ✅ 集群资源备份
  ✅ PV数据备份
  ✅ 定时备份
  ✅ 按需恢复
  ✅ 灾难恢复
  ✅ 应用迁移
  ✅ 多云支持

支持的存储后端:
  ✅ AWS S3
  ✅ Azure Blob
  ✅ Google Cloud Storage
  ✅ MinIO
  ✅ Alibaba Cloud OSS
  ✅ 兼容S3的对象存储

使用场景:
  - 灾难恢复 (DR)
  - 集群迁移
  - 应用迁移
  - 开发/测试环境复制
  - 合规备份
  - 数据保护
```

---

### 1.2 核心组件

**Velero架构图**:

```text
Velero架构:

┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Velero Server (Deployment)                  │ │
│  │  - Backup Controller                                   │ │
│  │  - Restore Controller                                  │ │
│  │  - Schedule Controller                                 │ │
│  │  - BackupStorageLocation Controller                    │ │
│  │  - VolumeSnapshotLocation Controller                   │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                         │
│         ┌─────────┼──────────┬──────────┬──────────┐        │
│         │         │          │          │          │        │
│    ┌────▼────┐┌───▼─────┐┌───▼─────┐┌───▼─────┐┌───▼────┐   │
│    │ Backup  ││ Restore ││Schedule ││BackupSL ││VolumeSL│   │
│    │  (CRD)  ││  (CRD)  ││  (CRD)  ││  (CRD)  ││ (CRD)  │   │
│    └─────────┘└─────────┘└─────────┘└─────────┘└────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Restic DaemonSet (Optional)                  │ │
│  │  - File-level backup for PV                            │ │
│  │  - Runs on each node                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         CSI VolumeSnapshotClass (Optional)             │ │
│  │  - Snapshot-based backup for PV                        │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Object Storage (S3)  │
                    │  - Backup metadata    │
                    │  - Resource YAML      │
                    │  - PV data (Restic)   │
                    └───────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │ Volume Snapshot (CSI) │
                    │  - PV snapshots       │
                    └───────────────────────┘
```

**核心组件说明**:

```yaml
1. Velero Server:
   功能:
     - 监听Backup/Restore CRD
     - 执行备份/恢复逻辑
     - 与对象存储交互
     - 协调Restic备份

   部署:
     - Deployment (1 replica)
     - 运行在控制平面
     - 需要RBAC权限

2. Restic DaemonSet (可选):
   功能:
     - 文件级PV备份
     - 增量备份
     - 适用于不支持快照的PV

   部署:
     - DaemonSet (每个节点)
     - privileged模式
     - 访问hostPath

3. BackupStorageLocation (BSL):
   作用:
     - 定义对象存储位置
     - 存储备份元数据
     - 存储资源YAML

   支持:
     - AWS S3
     - Azure Blob
     - GCS
     - MinIO
     - S3兼容

4. VolumeSnapshotLocation (VSL):
   作用:
     - 定义卷快照位置
     - 使用CSI快照
     - 云原生快照

   支持:
     - AWS EBS
     - Azure Disk
     - GCE PD
     - CSI驱动

5. Backup CRD:
   作用:
     - 定义备份任务
     - 指定备份范围
     - 配置TTL

   字段:
     - includedNamespaces
     - excludedResources
     - ttl (生命周期)
     - storageLocation

6. Schedule CRD:
   作用:
     - 定义定时备份
     - Cron表达式
     - 自动化

   示例:
     - 每日备份
     - 每周备份
     - 自定义调度

7. Restore CRD:
   作用:
     - 定义恢复任务
     - 指定恢复范围
     - 冲突处理

   字段:
     - backupName
     - includedNamespaces
     - restorePVs
```

---

### 1.3 备份原理

**备份流程**:

```yaml
备份流程详解:

1. 用户创建Backup CRD
   ↓
2. Velero Server监听到Backup事件
   ↓
3. 验证BackupStorageLocation可达
   ↓
4. 收集集群资源 (API Server)
   - Kubernetes资源 (Pod, Deployment, Service, etc.)
   - 根据includedNamespaces/excludedResources过滤
   - 序列化为JSON
   ↓
5. 备份PV数据 (2种方式)

   方式1: Restic (文件级)
     - Restic DaemonSet执行
     - 文件级增量备份
     - 适用于所有PV类型
     - 较慢，但通用

   方式2: Volume Snapshot (快照)
     - CSI VolumeSnapshot
     - 块级快照
     - 快速
     - 需要CSI驱动支持
   ↓
6. 上传到对象存储
   - 元数据: <backup-name>/velero-backup.json
   - 资源: <backup-name>/<namespace>/<resource>.json
   - Restic数据: restic/<repo>/
   ↓
7. 更新Backup状态
   - Phase: InProgress -> Completed/Failed
   - ExpireTime: now + TTL
   - Statistics: itemsBackedUp, warnings, errors

备份内容:
  集群资源:
    ✅ Namespaces
    ✅ ConfigMaps, Secrets
    ✅ Deployments, StatefulSets, DaemonSets
    ✅ Services, Ingresses
    ✅ PVC定义
    ✅ ServiceAccounts, RBAC
    ✅ CRD和CR

  PV数据:
    ✅ PVC关联的PV数据
    ✅ 使用Restic或Snapshot
    ✅ 可选择性备份

  不备份:
    ❌ Events
    ❌ Node
    ❌ PV (定义，但数据会备份)
    ❌ 临时Token

备份格式:
  对象存储结构:
    backups/
      <backup-name>/
        velero-backup.json      # 备份元数据
        <backup-name>.tar.gz    # 压缩的资源YAML
        <backup-name>-logs.gz   # 备份日志

    restic/
      <repo>/                   # Restic仓库
        config
        data/
        index/
        keys/
        snapshots/
```

---

### 1.4 恢复原理

**恢复流程**:

```yaml
恢复流程详解:

1. 用户创建Restore CRD
   ↓
2. Velero Server监听到Restore事件
   ↓
3. 从对象存储下载备份元数据
   ↓
4. 解析备份内容
   - 读取velero-backup.json
   - 解压资源YAML
   - 根据includedNamespaces/excludedResources过滤
   ↓
5. 恢复资源 (分阶段)

   Phase 1: 预恢复
     - CustomResourceDefinitions (CRD)
     - Namespaces
     - PersistentVolumes (PV)
     - PersistentVolumeClaims (PVC)

   Phase 2: 核心资源
     - ServiceAccounts
     - Secrets
     - ConfigMaps
     - Services

   Phase 3: 工作负载
     - Deployments
     - StatefulSets
     - DaemonSets
     - Jobs, CronJobs

   Phase 4: 其他资源
     - Ingress
     - NetworkPolicy
     - Custom Resources
   ↓
6. 恢复PV数据

   方式1: Restic恢复
     - Init Container恢复数据
     - 挂载PVC
     - Restic restore
     - 完成后启动应用容器

   方式2: Snapshot恢复
     - 从快照创建PV
     - PVC绑定到新PV
     - 快速
   ↓
7. 更新Restore状态
   - Phase: InProgress -> Completed/PartiallyFailed/Failed
   - Statistics: itemsRestored, warnings, errors
   ↓
8. 验证 (可选)
   - 检查Pod状态
   - 验证数据完整性

恢复策略:
  资源冲突处理:
    - none: 跳过已存在资源
    - update: 更新已存在资源

  命名空间映射:
    - 恢复到不同命名空间
    - 跨集群迁移

  选择性恢复:
    - 按命名空间
    - 按资源类型
    - 按标签选择器

注意事项:
  ⚠️ 恢复顺序很重要
  ⚠️ PVC需要等待PV创建
  ⚠️ Pod需要等待依赖资源 (Secret/ConfigMap)
  ⚠️ Restic恢复会延迟Pod启动
  ⚠️ 需要验证恢复完整性
```

---

## 2. Velero部署

### 2.1 部署前准备

**系统要求**:

```yaml
Kubernetes集群:
  版本: 1.16+
  推荐: 1.25+

节点资源:
  Velero Server:
    CPU: 500m - 1 core
    Memory: 256Mi - 512Mi

  Restic DaemonSet (可选):
    CPU: 500m per node
    Memory: 512Mi per node

对象存储:
  AWS S3 / MinIO / Azure Blob / GCS
  需要:
    - Bucket
    - 访问凭证 (AccessKey/SecretKey)
    - 网络可达

权限:
  Kubernetes:
    - 集群管理员权限
    - 创建CRD
    - 创建Namespace
    - RBAC权限

  对象存储:
    - 读写权限
    - ListBucket
    - GetObject / PutObject
```

**准备对象存储** (以MinIO为例):

```bash
# 1. 部署MinIO (如果没有)
kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: minio
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: minio-pvc
  namespace: minio
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: rook-ceph-block
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio
  namespace: minio
spec:
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
      - name: minio
        image: minio/minio:latest
        args:
        - server
        - /data
        - --console-address
        - :9001
        env:
        - name: MINIO_ROOT_USER
          value: "minio"
        - name: MINIO_ROOT_PASSWORD
          value: "minio123"
        ports:
        - containerPort: 9000
        - containerPort: 9001
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: minio-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: minio
  namespace: minio
spec:
  type: ClusterIP
  ports:
  - name: api
    port: 9000
    targetPort: 9000
  - name: console
    port: 9001
    targetPort: 9001
  selector:
    app: minio
EOF

# 2. 等待MinIO就绪
kubectl -n minio wait --for=condition=Ready pod -l app=minio --timeout=300s

# 3. 创建Bucket (使用mc客户端)
kubectl run mc-client --rm -it --image=minio/mc --command -- /bin/sh
# 在容器中:
mc alias set myminio http://minio.minio.svc.cluster.local:9000 minio minio123
mc mb myminio/velero
mc ls myminio/
exit
```

---

### 2.2 安装Velero

**安装Velero CLI**:

```bash
# Linux
wget https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/velero-v1.12.0-linux-amd64.tar.gz
tar -xvf velero-v1.12.0-linux-amd64.tar.gz
sudo mv velero-v1.12.0-linux-amd64/velero /usr/local/bin/
velero version --client-only

# macOS
brew install velero

# Windows
choco install velero
```

**创建凭证文件**:

```bash
# 创建MinIO凭证
cat > credentials-velero <<EOF
[default]
aws_access_key_id = minio
aws_secret_access_key = minio123
EOF
```

**安装Velero Server**:

```bash
# 使用Velero CLI安装
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket velero \
  --secret-file ./credentials-velero \
  --use-volume-snapshots=false \
  --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://minio.minio.svc.cluster.local:9000 \
  --use-node-agent \
  --uploader-type=restic

# 参数说明:
# --provider: 存储提供商
# --plugins: Velero插件
# --bucket: 对象存储bucket名称
# --secret-file: 凭证文件
# --use-volume-snapshots: 是否使用卷快照
# --backup-location-config: BackupStorageLocation配置
# --use-node-agent: 启用Node Agent (Restic)
# --uploader-type: 上传器类型 (restic或kopia)

# 输出:
# CustomResourceDefinition/backups.velero.io: attempting to create resource
# CustomResourceDefinition/backups.velero.io: created
# CustomResourceDefinition/backupstoragelocations.velero.io: attempting to create resource
# CustomResourceDefinition/backupstoragelocations.velero.io: created
# ...
# Velero is installed! ⛵ Use 'kubectl logs deployment/velero -n velero' to view the status.
```

**验证安装**:

```bash
# 1. 检查Velero Namespace
kubectl get ns velero

# 2. 检查Velero Pods
kubectl -n velero get pods
# NAME                      READY   STATUS    RESTARTS   AGE
# node-agent-xxx            1/1     Running   0          1m
# node-agent-yyy            1/1     Running   0          1m
# node-agent-zzz            1/1     Running   0          1m
# velero-xxx                1/1     Running   0          1m

# 3. 检查BackupStorageLocation
velero backup-location get
# NAME      PROVIDER   BUCKET/PREFIX   PHASE       LAST VALIDATED
# default   aws        velero          Available   2025-10-19 12:00:00 +0000 UTC

# 4. 检查Velero日志
kubectl -n velero logs deployment/velero
```

---

### 2.3 配置对象存储

**BackupStorageLocation配置**:

```yaml
# 查看默认BSL
kubectl -n velero get backupstoragelocation default -o yaml

# 手动创建BSL
apiVersion: velero.io/v1
kind: BackupStorageLocation
metadata:
  name: default
  namespace: velero
spec:
  provider: aws
  objectStorage:
    bucket: velero
    prefix: backups  # 可选，对象存储前缀
  config:
    region: minio
    s3ForcePathStyle: "true"
    s3Url: http://minio.minio.svc.cluster.local:9000
  credential:
    name: cloud-credentials
    key: cloud
  default: true
  accessMode: ReadWrite  # ReadWrite或ReadOnly
```

**AWS S3配置示例**:

```bash
# AWS S3凭证
cat > credentials-velero <<EOF
[default]
aws_access_key_id = <YOUR_AWS_ACCESS_KEY>
aws_secret_access_key = <YOUR_AWS_SECRET_KEY>
EOF

# 安装Velero (AWS S3)
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket velero-backup \
  --secret-file ./credentials-velero \
  --backup-location-config region=us-east-1 \
  --snapshot-location-config region=us-east-1 \
  --use-node-agent
```

**Azure Blob配置示例**:

```bash
# Azure凭证
cat > credentials-velero <<EOF
AZURE_SUBSCRIPTION_ID=<YOUR_SUBSCRIPTION_ID>
AZURE_TENANT_ID=<YOUR_TENANT_ID>
AZURE_CLIENT_ID=<YOUR_CLIENT_ID>
AZURE_CLIENT_SECRET=<YOUR_CLIENT_SECRET>
AZURE_RESOURCE_GROUP=<YOUR_RESOURCE_GROUP>
EOF

# 安装Velero (Azure)
velero install \
  --provider azure \
  --plugins velero/velero-plugin-for-microsoft-azure:v1.8.0 \
  --bucket velero-backup \
  --secret-file ./credentials-velero \
  --backup-location-config resourceGroup=<RESOURCE_GROUP>,storageAccount=<STORAGE_ACCOUNT> \
  --snapshot-location-config apiTimeout=5m \
  --use-node-agent
```

---

### 2.4 验证安装

**创建测试备份**:

```bash
# 1. 创建测试命名空间和资源
kubectl create namespace nginx-example
kubectl -n nginx-example create deployment nginx --image=nginx:latest --replicas=3
kubectl -n nginx-example expose deployment nginx --port=80

# 2. 等待Pod就绪
kubectl -n nginx-example wait --for=condition=Ready pod -l app=nginx --timeout=300s

# 3. 创建备份
velero backup create nginx-backup --include-namespaces nginx-example --wait

# 4. 查看备份状态
velero backup describe nginx-backup --details

# 5. 查看备份列表
velero backup get

# 6. 删除测试资源
kubectl delete namespace nginx-example

# 7. 恢复备份
velero restore create --from-backup nginx-backup --wait

# 8. 验证恢复
kubectl -n nginx-example get all

# 9. 清理
kubectl delete namespace nginx-example
velero backup delete nginx-backup
```

---

## 3. 备份策略设计

### 3.1 定时备份

**Schedule CRD**:

```yaml
# 每日备份
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: daily-backup
  namespace: velero
spec:
  # Cron表达式 (UTC时间)
  schedule: "0 2 * * *"  # 每天凌晨2点

  # 备份模板
  template:
    includedNamespaces:
    - production
    - staging

    excludedResources:
    - events
    - events.events.k8s.io

    ttl: 168h0m0s  # 7天

    storageLocation: default

    volumeSnapshotLocations:
    - default

    # Restic备份PV
    defaultVolumesToRestic: true

    # 备份标签
    labels:
      schedule: daily
      environment: production

---
# 每周备份
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: weekly-backup
  namespace: velero
spec:
  schedule: "0 3 * * 0"  # 每周日凌晨3点
  template:
    includedNamespaces:
    - "*"  # 所有命名空间
    ttl: 720h0m0s  # 30天
    storageLocation: default
    defaultVolumesToRestic: true
    labels:
      schedule: weekly
      retention: long-term

---
# 每月备份
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: monthly-backup
  namespace: velero
spec:
  schedule: "0 4 1 * *"  # 每月1号凌晨4点
  template:
    includedNamespaces:
    - "*"
    ttl: 2160h0m0s  # 90天
    storageLocation: default
    defaultVolumesToRestic: true
    labels:
      schedule: monthly
      retention: archive
```

**创建定时备份**:

```bash
# 方式1: 使用velero CLI
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --include-namespaces production,staging \
  --ttl 168h \
  --default-volumes-to-restic

# 方式2: 使用YAML
kubectl apply -f schedule-daily.yaml

# 查看Schedule
velero schedule get

# 查看Schedule详情
velero schedule describe daily-backup

# 暂停Schedule
velero schedule pause daily-backup

# 恢复Schedule
velero schedule unpause daily-backup

# 删除Schedule
velero schedule delete daily-backup
```

---

### 3.2 按需备份

**手动备份**:

```bash
# 备份整个集群
velero backup create full-backup \
  --include-cluster-resources=true \
  --wait

# 备份特定命名空间
velero backup create app-backup \
  --include-namespaces myapp \
  --wait

# 备份多个命名空间
velero backup create multi-ns-backup \
  --include-namespaces prod,staging,dev \
  --wait

# 排除特定资源
velero backup create no-events-backup \
  --include-namespaces myapp \
  --exclude-resources events,events.events.k8s.io \
  --wait

# 只备份特定资源
velero backup create only-deployments \
  --include-resources deployments \
  --include-namespaces myapp \
  --wait

# 使用标签选择器
velero backup create labeled-backup \
  --selector "app=nginx,env=prod" \
  --wait

# 备份前执行Hook
velero backup create mysql-backup \
  --include-namespaces database \
  --default-volumes-to-restic \
  --wait
```

---

### 3.3 选择性备份

**按命名空间备份**:

```yaml
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: selective-backup
  namespace: velero
spec:
  # 包含的命名空间
  includedNamespaces:
  - production
  - staging

  # 排除的命名空间
  excludedNamespaces:
  - kube-system
  - kube-public

  # 排除的资源类型
  excludedResources:
  - events
  - events.events.k8s.io
  - nodes

  # 包含的资源类型 (如果设置，只备份这些)
  # includedResources:
  # - deployments
  # - services
  # - configmaps

  # 标签选择器
  labelSelector:
    matchLabels:
      backup: "true"
    matchExpressions:
    - key: environment
      operator: In
      values:
      - production
      - staging

  # 是否包含集群资源 (PV, StorageClass, etc.)
  includeClusterResources: true

  # TTL (生命周期)
  ttl: 720h0m0s  # 30天

  # 存储位置
  storageLocation: default

  # 快照位置
  volumeSnapshotLocations:
  - default

  # 默认使用Restic备份PV
  defaultVolumesToRestic: true

  # 有序备份
  orderedResources:
    pods: namespaces/name
    persistentvolumeclaims: namespaces/name
```

---

### 3.4 备份生命周期

**TTL管理**:

```bash
# 创建备份时设置TTL
velero backup create short-term-backup \
  --include-namespaces myapp \
  --ttl 24h

# 修改现有备份的TTL
kubectl -n velero patch backup my-backup \
  --type merge \
  --patch '{"spec":{"ttl":"720h"}}'

# 查看备份过期时间
velero backup get
# NAME               STATUS      CREATED                         EXPIRES   ...
# my-backup          Completed   2025-10-19 12:00:00 +0000 UTC   29d       ...

# 手动删除备份
velero backup delete my-backup

# 删除所有已完成的备份
velero backup delete --all --confirm

# 查看即将过期的备份
velero backup get | grep -E "([0-9]d|[0-9]h)"
```

**备份保留策略**:

```yaml
备份保留建议:

日备份 (Daily):
  TTL: 7天
  频率: 每天
  用途: 快速恢复

周备份 (Weekly):
  TTL: 30天
  频率: 每周
  用途: 中期恢复

月备份 (Monthly):
  TTL: 90天 或 1年
  频率: 每月
  用途: 长期归档

季度备份 (Quarterly):
  TTL: 2年
  频率: 每季度
  用途: 合规要求

示例策略:
  生产环境:
    - 每日: 7天
    - 每周: 4周
    - 每月: 12个月

  开发环境:
    - 每日: 3天
    - 每周: 2周
```

---

## 4. 恢复演练

### 4.1 完整恢复

```bash
# 1. 查看可用备份
velero backup get

# 2. 查看备份详情
velero backup describe my-backup --details

# 3. 完整恢复
velero restore create --from-backup my-backup --wait

# 4. 查看恢复状态
velero restore get
velero restore describe my-restore --details

# 5. 查看恢复日志
velero restore logs my-restore

# 6. 验证恢复的资源
kubectl get all -A
```

---

### 4.2 选择性恢复

```bash
# 只恢复特定命名空间
velero restore create --from-backup my-backup \
  --include-namespaces production \
  --wait

# 排除特定资源
velero restore create --from-backup my-backup \
  --exclude-resources services,ingresses \
  --wait

# 恢复到不同命名空间
velero restore create --from-backup my-backup \
  --namespace-mappings old-ns:new-ns \
  --wait

# 只恢复特定资源
velero restore create --from-backup my-backup \
  --include-resources deployments,configmaps \
  --wait
```

---

### 4.3 跨集群恢复

```bash
# 场景: 从集群A恢复到集群B

# 集群A: 创建备份
velero backup create cluster-a-backup \
  --include-namespaces myapp \
  --wait

# 集群A: 确认备份完成
velero backup describe cluster-a-backup

# 切换到集群B
kubectl config use-context cluster-b

# 集群B: 安装Velero (使用相同的对象存储)
velero install \
  --provider aws \
  --bucket velero \
  --secret-file ./credentials-velero \
  --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://minio.minio.svc.cluster.local:9000 \
  --use-node-agent

# 集群B: 同步备份
velero backup get
# 应该能看到cluster-a-backup

# 集群B: 恢复
velero restore create --from-backup cluster-a-backup --wait

# 集群B: 验证
kubectl -n myapp get all
```

---

### 4.4 灾难恢复演练

**DR演练脚本**:

```bash
#!/bin/bash
# dr-drill.sh - 灾难恢复演练

set -e

echo "=== 灾难恢复演练开始 ==="

# 1. 记录当前状态
echo "1. 记录当前状态..."
kubectl get ns > /tmp/ns-before.txt
kubectl get pods -A > /tmp/pods-before.txt

# 2. 创建备份
echo "2. 创建备份..."
BACKUP_NAME="dr-drill-$(date +%Y%m%d-%H%M%S)"
velero backup create $BACKUP_NAME \
  --include-namespaces myapp \
  --wait

# 3. 验证备份
echo "3. 验证备份..."
velero backup describe $BACKUP_NAME

# 4. 模拟灾难 (删除资源)
echo "4. 模拟灾难..."
kubectl delete namespace myapp --wait=false

# 5. 等待删除完成
echo "5. 等待删除完成..."
sleep 30

# 6. 执行恢复
echo "6. 执行恢复..."
velero restore create --from-backup $BACKUP_NAME --wait

# 7. 验证恢复
echo "7. 验证恢复..."
kubectl get ns
kubectl -n myapp get pods

# 8. 对比状态
echo "8. 对比状态..."
kubectl get ns > /tmp/ns-after.txt
kubectl get pods -A > /tmp/pods-after.txt

diff /tmp/ns-before.txt /tmp/ns-after.txt || true
diff /tmp/pods-before.txt /tmp/pods-after.txt || true

# 9. 生成报告
echo "9. 生成报告..."
cat > /tmp/dr-report.txt <<EOF
DR演练报告
==========
时间: $(date)
备份名称: $BACKUP_NAME
恢复耗时: $(velero restore describe ${BACKUP_NAME}-* | grep "Completion timestamp" | awk '{print $3}')
恢复状态: $(velero restore describe ${BACKUP_NAME}-* | grep "Phase:" | awk '{print $2}')
恢复警告: $(velero restore describe ${BACKUP_NAME}-* | grep "Warnings:" | awk '{print $2}')
恢复错误: $(velero restore describe ${BACKUP_NAME}-* | grep "Errors:" | awk '{print $2}')
EOF

cat /tmp/dr-report.txt

echo "=== 灾难恢复演练完成 ==="
```

---

## 5. 多集群备份

### 5.1 多集群架构

```yaml
多集群备份架构:

集群A (生产)         集群B (灾备)         集群C (开发)
    ↓                   ↓                    ↓
    └───────────────────┴────────────────────┘
                        ↓
                共享对象存储 (S3/MinIO)
                        ↓
                ┌───────┴───────┐
                │   Backups:    │
                │  - cluster-a  │
                │  - cluster-b  │
                │  - cluster-c  │
                └───────────────┘

优势:
  ✅ 集中管理
  ✅ 跨集群恢复
  ✅ 成本优化
  ✅ 合规审计
```

---

### 5.2 集中式备份

**配置多个集群**:

```bash
# 集群A配置
kubectl config use-context cluster-a
velero install \
  --provider aws \
  --bucket velero-multi \
  --prefix cluster-a \
  --secret-file ./credentials-velero \
  --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://minio:9000

# 集群B配置
kubectl config use-context cluster-b
velero install \
  --provider aws \
  --bucket velero-multi \
  --prefix cluster-b \
  --secret-file ./credentials-velero \
  --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://minio:9000

# 集群C配置
kubectl config use-context cluster-c
velero install \
  --provider aws \
  --bucket velero-multi \
  --prefix cluster-c \
  --secret-file ./credentials-velero \
  --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://minio:9000
```

---

### 5.3 备份复制

**跨区域备份**:

```yaml
# 主存储位置
apiVersion: velero.io/v1
kind: BackupStorageLocation
metadata:
  name: primary
  namespace: velero
spec:
  provider: aws
  objectStorage:
    bucket: velero-primary
  config:
    region: us-east-1
  default: true

---
# 备份存储位置
apiVersion: velero.io/v1
kind: BackupStorageLocation
metadata:
  name: secondary
  namespace: velero
spec:
  provider: aws
  objectStorage:
    bucket: velero-secondary
  config:
    region: us-west-2
  default: false
```

---

## 6. 应用迁移

### 6.1 同版本迁移

```bash
# 场景: Kubernetes 1.28 -> Kubernetes 1.28

# 源集群: 备份
velero backup create migration-backup \
  --include-namespaces myapp \
  --wait

# 目标集群: 安装Velero (相同对象存储)
velero install --provider aws --bucket velero ...

# 目标集群: 恢复
velero restore create --from-backup migration-backup --wait
```

---

### 6.2 跨版本迁移

```bash
# 场景: Kubernetes 1.25 -> Kubernetes 1.28

# 注意事项:
# ⚠️ 检查API版本兼容性
# ⚠️ 某些资源可能需要转换
# ⚠️ 测试恢复
```

---

### 6.3 跨云迁移

```bash
# 场景: AWS -> Azure

# AWS集群: 备份到S3
velero backup create aws-backup ...

# 使用工具同步S3到Azure Blob
# rclone, aws s3 sync等

# Azure集群: 从Azure Blob恢复
velero install --provider azure ...
velero restore create --from-backup aws-backup
```

---

## 7. 最佳实践

### 7.1 备份策略

```yaml
生产环境建议:

1. 备份频率:
   关键应用:
     - 每6小时增量
     - 每日全量
   一般应用:
     - 每日1次

2. 保留策略:
   - 日备份: 7天
   - 周备份: 4周
   - 月备份: 12个月

3. 验证:
   - 定期恢复测试
   - DR演练 (每季度)

4. 监控:
   - 备份成功率
   - 存储使用
   - 告警配置
```

---

### 7.2 性能优化

```yaml
Restic性能:
  - 并发: --default-volumes-to-restic-concurrency=4
  - 限速: --default-restic-prune-limit
  - 压缩: zstd

对象存储:
  - 多线程上传
  - 就近部署
  - 专用网络
```

---

### 7.3 安全加固

```yaml
安全建议:
  ✅ 对象存储加密
  ✅ RBAC权限最小化
  ✅ 网络隔离
  ✅ 审计日志
```

---

### 7.4 监控告警

```yaml
监控指标:
  - 备份成功率
  - 备份耗时
  - 存储容量
  - 恢复时间 (RTO)

告警:
  - 备份失败
  - 存储满
  - 长时间未备份
```

---

## 8. 总结

### 8.1 本章要点

```yaml
核心知识:
  ✅ Velero架构 (Server, Restic, BSL, VSL)
  ✅ 备份原理 (资源+PV数据)
  ✅ 恢复原理 (分阶段恢复)
  ✅ 部署配置 (MinIO/S3/Azure)
  ✅ 备份策略 (定时/按需/选择性)
  ✅ 恢复演练 (完整/选择性/跨集群)
  ✅ 多集群备份
  ✅ 应用迁移
  ✅ 最佳实践

代码示例:
  - 25+ YAML配置
  - 50+ CLI命令
  - DR演练脚本
  - 多集群配置

技术覆盖:
  - Velero完整架构
  - 3种对象存储配置 (MinIO/AWS/Azure)
  - 定时备份 (日/周/月)
  - 灾难恢复 (DR)
  - 跨集群迁移
  - 安全与监控
```

### 8.2 推荐资源

```yaml
官方文档:
  - Velero: https://velero.io/docs/
  - Restic: https://restic.net/

社区资源:
  - GitHub: https://github.com/vmware-tanzu/velero
  - Slack: Kubernetes #velero

最佳实践:
  - CNCF Backup & Restore Best Practices
  - Disaster Recovery for Kubernetes
```

---

**完成日期**: 2025-10-19
**版本**: v1.0
**作者**: 云原生存储专家团队

**Tags**: `#Velero` `#Backup` `#DisasterRecovery` `#Migration` `#CloudNativeStorage`

---

## 相关文档

### 本模块相关

- [云原生存储概述与架构](./01_云原生存储概述与架构.md) - 云原生存储概述与架构
- [Kubernetes存储基础](./02_Kubernetes存储基础.md) - Kubernetes存储基础
- [Rook Ceph深度解析](./03_Rook_Ceph深度解析.md) - Rook Ceph深度解析
- [CSI驱动详解](./05_CSI驱动详解.md) - CSI驱动详解
- [存储性能优化](./06_存储性能优化.md) - 存储性能优化
- [多云存储](./07_多云存储.md) - 多云存储
- [存储安全](./08_存储安全.md) - 存储安全
- [实战案例](./09_实战案例.md) - 实战案例
- [最佳实践](./10_最佳实践.md) - 最佳实践
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [容器监控与运维](../06_容器监控与运维/README.md) - 容器监控运维
- [容器故障诊断](../06_容器监控与运维/04_容器故障诊断.md) - 容器故障诊断
- [Kubernetes技术详解](../03_Kubernetes技术详解/README.md) - Kubernetes技术体系
- [容器技术实践案例](../08_容器技术实践案例/README.md) - 容器技术实践案例

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新
