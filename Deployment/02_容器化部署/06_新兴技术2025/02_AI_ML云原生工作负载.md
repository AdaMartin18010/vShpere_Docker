# AI/ML云原生工作负载

> **返回**: [新兴技术2025](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [AI/ML云原生工作负载](#aiml云原生工作负载)
  - [📋 目录](#-目录)
  - [1. AI/ML云原生技术概览](#1-aiml云原生技术概览)
    - [技术栈全景](#技术栈全景)
    - [AI/ML工作负载特点](#aiml工作负载特点)
  - [2. Kubernetes GPU调度 (2025最新)](#2-kubernetes-gpu调度-2025最新)
    - [NVIDIA GPU Operator 23.9+](#nvidia-gpu-operator-239)
    - [安装NVIDIA GPU Operator](#安装nvidia-gpu-operator)
    - [GPU资源管理 (MIG, Time-Slicing)](#gpu资源管理-mig-time-slicing)
    - [GPU拓扑感知调度](#gpu拓扑感知调度)
  - [3. KubeFlow 1.8+ ML平台](#3-kubeflow-18-ml平台)
    - [KubeFlow架构](#kubeflow架构)
    - [安装KubeFlow 1.8](#安装kubeflow-18)
    - [Kubeflow Pipeline示例](#kubeflow-pipeline示例)
  - [4. Ray + KubeRay分布式计算](#4-ray--kuberay分布式计算)
    - [Ray 2.9+核心概念](#ray-29核心概念)
    - [安装KubeRay Operator](#安装kuberay-operator)
    - [RayCluster配置](#raycluster配置)
    - [Ray分布式训练示例](#ray分布式训练示例)

---

## 1. AI/ML云原生技术概览

### 技术栈全景

```yaml
AI_ML_Cloud_Native_2025:
  核心组件:
    计算调度:
      - Kubernetes 1.28+ (GPU调度)
      - NVIDIA GPU Operator
      - AMD ROCm Operator
      - Intel GPU Plugin
    
    分布式框架:
      - Ray 2.9+ (通用分布式)
      - Kuberay (Ray on K8s)
      - Horovod (分布式训练)
      - DeepSpeed (大模型训练)
    
    ML平台:
      - Kubeflow 1.8+ (完整ML平台)
      - MLflow (实验跟踪)
      - Weights & Biases (W&B)
      - DVC (数据版本控制)
    
    模型服务:
      - KServe 0.12+ (模型推理)
      - Seldon Core (模型部署)
      - TorchServe (PyTorch)
      - TensorFlow Serving
    
    存储:
      - JuiceFS (分布式文件系统)
      - Alluxio (数据编排)
      - MinIO (对象存储)
      - NFS-CSI (共享存储)

  GPU技术栈:
    NVIDIA:
      - CUDA 12.3+
      - cuDNN 8.9+
      - NCCL 2.20+ (多GPU通信)
      - NVLink (GPU互联)
      - GPU Direct Storage
      - MIG (Multi-Instance GPU)
      - Time-Slicing (GPU时间片)
    
    AMD:
      - ROCm 6.0+
      - MIOpen
      - RCCL
    
    Intel:
      - oneAPI 2024.0
      - oneDNN
      - Level Zero

  2025新趋势:
    大模型训练:
      - LLM (GPT, LLaMA, Falcon)
      - 参数规模: 70B-175B+
      - 分布式训练: 张量并行、流水线并行
      - 混合精度: FP16, BF16, INT8
    
    推理优化:
      - TensorRT 9.0+
      - ONNX Runtime
      - OpenVINO
      - 量化加速 (INT4/INT8)
    
    边缘AI:
      - Edge TPU
      - NVIDIA Jetson
      - 模型压缩
      - 联邦学习
```

### AI/ML工作负载特点

```yaml
AI_ML_Workload_Characteristics:
  资源需求:
    GPU:
      - 训练: 高算力 (A100/H100)
      - 推理: 平衡 (T4/L4)
      - 数量: 单卡到数百卡
    
    内存:
      - GPU内存: 16GB-80GB per GPU
      - 系统内存: 256GB-2TB
      - 数据集: TB-PB级
    
    存储:
      - IOPS: 数十万到百万
      - 带宽: 10GB/s+
      - 容量: TB-PB级
    
    网络:
      - GPU间: NVLink (600GB/s)
      - 节点间: 100Gbps/200Gbps InfiniBand
      - 存储: RDMA
  
  工作负载类型:
    训练_Training:
      - 批处理
      - 长时间运行 (小时-天)
      - GPU密集
      - 通信密集 (多GPU)
    
    推理_Inference:
      - 在线服务
      - 低延迟要求 (<100ms)
      - 高吞吐量
      - 弹性伸缩
    
    超参数调优_HPO:
      - 并行任务
      - 中等时长
      - 资源多样
    
    Notebook开发:
      - 交互式
      - 长期占用
      - 中等资源
```

---

## 2. Kubernetes GPU调度 (2025最新)

### NVIDIA GPU Operator 23.9+

```yaml
NVIDIA_GPU_Operator_2025:
  核心功能:
    自动化管理:
      - GPU驱动安装
      - CUDA工具包
      - Container Toolkit
      - Device Plugin
      - GPU Feature Discovery
      - DCGM监控导出器
    
    GPU特性支持:
      - MIG (Multi-Instance GPU)
      - Time-Slicing (时间片)
      - GPU直通
      - vGPU (虚拟化)
      - GPUDirect RDMA
      - GPUDirect Storage
    
    监控可观测性:
      - DCGM指标
      - Prometheus集成
      - Grafana仪表板
      - GPU拓扑发现
```

### 安装NVIDIA GPU Operator

```bash
#!/bin/bash
# install-nvidia-gpu-operator.sh - 2025

set -e

echo "=== 安装NVIDIA GPU Operator (2025) ==="

# 1. 前置检查
echo "1. 检查GPU硬件..."
lspci | grep -i nvidia

# 检查内核版本
uname -r

# 2. 添加Helm仓库
echo "2. 添加NVIDIA Helm仓库..."
helm repo add nvidia https://nvidia.github.io/gpu-operator
helm repo update

# 3. 创建命名空间
kubectl create namespace gpu-operator --dry-run=client -o yaml | kubectl apply -f -

# 4. 安装GPU Operator
echo "3. 安装GPU Operator..."
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --version v23.9.1 \
  --set operator.defaultRuntime=containerd \
  --set driver.enabled=true \
  --set driver.version="535.129.03" \
  --set toolkit.enabled=true \
  --set devicePlugin.enabled=true \
  --set devicePlugin.version=v0.14.5 \
  --set mig.strategy=single \
  --set gfd.enabled=true \
  --set dcgmExporter.enabled=true \
  --set dcgmExporter.serviceMonitor.enabled=true \
  --set nodeStatusExporter.enabled=true

# 5. 等待部署完成
echo "4. 等待GPU Operator部署..."
kubectl -n gpu-operator rollout status daemonset/nvidia-driver-daemonset
kubectl -n gpu-operator rollout status daemonset/nvidia-container-toolkit-daemonset
kubectl -n gpu-operator rollout status daemonset/nvidia-device-plugin-daemonset

# 6. 验证GPU可用性
echo "5. 验证GPU节点..."
kubectl get nodes -o json | \
  jq '.items[] | {name: .metadata.name, gpus: .status.capacity."nvidia.com/gpu"}'

# 7. 标记GPU节点
echo "6. 标记GPU节点..."
for node in $(kubectl get nodes -o jsonpath='{.items[*].metadata.name}'); do
  GPU_COUNT=$(kubectl get node $node -o jsonpath='{.status.capacity.nvidia\.com/gpu}')
  if [ -n "$GPU_COUNT" ] && [ "$GPU_COUNT" != "0" ]; then
    kubectl label node $node gpu-type=nvidia --overwrite
    kubectl label node $node gpu-count=$GPU_COUNT --overwrite
  fi
done

# 8. 运行测试Pod
echo "7. 运行GPU测试..."
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: gpu-test
spec:
  restartPolicy: Never
  containers:
  - name: cuda-test
    image: nvidia/cuda:12.3.0-base-ubuntu22.04
    command: ["nvidia-smi"]
    resources:
      limits:
        nvidia.com/gpu: 1
EOF

kubectl wait --for=condition=Completed pod/gpu-test --timeout=120s
kubectl logs gpu-test

# 清理测试Pod
kubectl delete pod gpu-test

echo ""
echo "=== GPU Operator安装完成 ==="
echo "查看GPU节点: kubectl get nodes -l gpu-type=nvidia"
echo "查看GPU资源: kubectl describe nodes | grep nvidia.com/gpu"
```

### GPU资源管理 (MIG, Time-Slicing)

```yaml
# gpu-resource-configs.yaml

# 1. MIG配置 (Multi-Instance GPU)
# A100 GPU可分割为最多7个MIG实例
apiVersion: v1
kind: ConfigMap
metadata:
  name: mig-parted-config
  namespace: gpu-operator
data:
  config.yaml: |
    version: v1
    mig-configs:
      # A100-80GB 配置策略
      all-balanced:
        - devices: all
          mig-enabled: true
          mig-devices:
            "1g.10gb": 7    # 7个小实例
      
      half-half:
        - devices: all
          mig-enabled: true
          mig-devices:
            "3g.40gb": 2    # 2个大实例
      
      mixed:
        - devices: [0]
          mig-enabled: true
          mig-devices:
            "3g.40gb": 1
            "1g.10gb": 3
        - devices: [1]
          mig-enabled: false  # 整卡模式

---
# 2. Time-Slicing配置 (GPU时间片共享)
apiVersion: v1
kind: ConfigMap
metadata:
  name: device-plugin-config
  namespace: gpu-operator
data:
  config.yaml: |
    version: v1
    sharing:
      timeSlicing:
        resources:
        - name: nvidia.com/gpu
          replicas: 4  # 1个物理GPU虚拟为4个逻辑GPU
        
        # 不同GPU类型不同策略
        - name: nvidia.com/gpu
          selector:
            nvidia.com/gpu.product: "Tesla-T4"
          replicas: 8  # T4推理卡可以更多共享
        
        - name: nvidia.com/gpu
          selector:
            nvidia.com/gpu.product: "A100-SXM4-80GB"
          replicas: 2  # A100训练卡少量共享

---
# 3. 应用Time-Slicing的Pod
apiVersion: v1
kind: Pod
metadata:
  name: gpu-shared-pod-1
spec:
  containers:
  - name: app
    image: nvidia/cuda:12.3.0-base-ubuntu22.04
    command: ["sleep", "infinity"]
    resources:
      limits:
        nvidia.com/gpu: 1  # 获得1/4物理GPU
---
apiVersion: v1
kind: Pod
metadata:
  name: gpu-shared-pod-2
spec:
  containers:
  - name: app
    image: nvidia/cuda:12.3.0-base-ubuntu22.04
    command: ["sleep", "infinity"]
    resources:
      limits:
        nvidia.com/gpu: 1  # 另一个1/4物理GPU
```

### GPU拓扑感知调度

```yaml
# gpu-topology-aware-scheduling.yaml

# 1. NodeLabel添加GPU拓扑信息
# GPU Operator自动标记节点
# nvidia.com/gpu.count
# nvidia.com/gpu.product
# nvidia.com/gpu.memory
# nvidia.com/gpu.compute-capability
# topology.kubernetes.io/zone (物理位置)

# 2. 拓扑感知的StatefulSet (多GPU训练)
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: distributed-training
spec:
  serviceName: training
  replicas: 4  # 4个训练节点
  podManagementPolicy: Parallel
  selector:
    matchLabels:
      app: training
  template:
    metadata:
      labels:
        app: training
    spec:
      # GPU节点选择
      nodeSelector:
        gpu-type: nvidia
        nvidia.com/gpu.product: "A100-SXM4-80GB"
      
      # 拓扑感知：优先同一机架
      affinity:
        podAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: training
              topologyKey: topology.kubernetes.io/zone
        
        # 节点亲和性：需要NVLink
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: nvidia.com/gpu.count
                operator: Gt
                values: ["7"]  # 8卡节点
      
      containers:
      - name: trainer
        image: nvcr.io/nvidia/pytorch:23.12-py3
        command:
          - python
          - -m
          - torch.distributed.launch
          - --nproc_per_node=8
          - --nnodes=4
          - --node_rank=$(POD_INDEX)
          - --master_addr=training-0.training.default.svc.cluster.local
          - --master_port=23456
          - train.py
        env:
        - name: POD_INDEX
          valueFrom:
            fieldRef:
              fieldPath: metadata.labels['apps.kubernetes.io/pod-index']
        - name: NCCL_DEBUG
          value: "INFO"
        - name: NCCL_IB_DISABLE
          value: "0"  # 启用InfiniBand
        - name: NCCL_NET_GDR_LEVEL
          value: "5"  # GPUDirect RDMA
        resources:
          limits:
            nvidia.com/gpu: 8  # 每个Pod 8张GPU
            rdma/hca: 1  # InfiniBand HCA
        volumeMounts:
        - name: shm
          mountPath: /dev/shm
        - name: dataset
          mountPath: /data
      
      volumes:
      - name: shm
        emptyDir:
          medium: Memory
          sizeLimit: 64Gi  # 大shared memory for NCCL
      - name: dataset
        persistentVolumeClaim:
          claimName: imagenet-pvc
```

---

## 3. KubeFlow 1.8+ ML平台

### KubeFlow架构

```yaml
Kubeflow_1_8_Architecture_2025:
  核心组件:
    中心Dashboard:
      - 统一UI入口
      - 多租户支持
      - RBAC集成
      - 命名空间管理
    
    Notebooks:
      - Jupyter/VS Code/RStudio
      - GPU资源请求
      - PVC持久化
      - 自定义镜像
    
    Pipelines_v2:
      - ML工作流编排
      - DAG可视化
      - Artifact跟踪
      - 缓存与复用
      - Tekton后端
    
    Katib:
      - 超参数优化 (HPO)
      - Neural Architecture Search (NAS)
      - 多种算法 (Grid/Random/Bayesian/Hyperband)
      - 并行trial
    
    Training_Operators:
      - TFJob (TensorFlow)
      - PyTorchJob (PyTorch)
      - MXJob (MXNet)
      - MPIJob (Horovod)
      - XGBoostJob
      - PaddleJob
    
    KServe:
      - 模型服务
      - 自动伸缩
      - Canary部署
      - A/B测试
      - Explainability

  2025新特性:
    - KFP v2 GA (完全重写)
    - Vertex AI集成
    - MLflow集成增强
    - Ray集成
    - 多云支持
```

### 安装KubeFlow 1.8

```bash
#!/bin/bash
# install-kubeflow-1.8.sh

set -e

echo "=== 安装Kubeflow 1.8 (2025) ==="

# 1. 前置要求
echo "1. 检查前置条件..."
kubectl version --client
kustomize version

# 2. 克隆Kubeflow manifests
echo "2. 下载Kubeflow manifests..."
git clone https://github.com/kubeflow/manifests.git
cd manifests
git checkout v1.8-branch

# 3. 安装cert-manager
echo "3. 安装cert-manager..."
kubectl apply -f common/cert-manager/cert-manager/base
kubectl wait --for=condition=ready pod -l 'app in (cert-manager,webhook)' \
  --timeout=180s -n cert-manager

# 4. 安装Istio (for KubeFlow)
echo "4. 安装Istio..."
kubectl apply -f common/istio-1-20/istio-crds/base
kubectl apply -f common/istio-1-20/istio-namespace/base
kubectl apply -f common/istio-1-20/istio-install/overlays/oauth2-proxy

# 5. 安装Dex (身份认证)
echo "5. 安装Dex..."
kubectl apply -f common/dex/overlays/istio

# 6. 安装OIDC AuthService
echo "6. 安装AuthService..."
kubectl apply -f common/oidc-client/oidc-authservice/overlays/ibm-storage-class

# 7. 安装Kubeflow Namespace
echo "7. 创建Kubeflow命名空间..."
kubectl apply -f common/kubeflow-namespace/base

# 8. 安装Kubeflow Roles
kubectl apply -f common/kubeflow-roles/base
kubectl apply -f common/istio-1-20/kubeflow-istio-resources/base

# 9. 安装Kubeflow Pipelines
echo "8. 安装Kubeflow Pipelines..."
kubectl apply -f apps/pipeline/upstream/env/cert-manager/platform-agnostic-multi-user

# 等待Pipelines就绪
kubectl wait --for=condition=ready pod -l app=ml-pipeline \
  --timeout=600s -n kubeflow

# 10. 安装Katib (超参数调优)
echo "9. 安装Katib..."
kubectl apply -f apps/katib/upstream/installs/katib-cert-manager

# 11. 安装Training Operators
echo "10. 安装Training Operators..."
kubectl apply -f apps/training-operator/upstream/overlays/kubeflow

# 12. 安装Notebooks
echo "11. 安装Notebooks..."
kubectl apply -f apps/jupyter/jupyter-web-app/upstream/overlays/istio
kubectl apply -f apps/jupyter/notebook-controller/upstream/overlays/kubeflow
kubectl apply -f apps/admission-webhook/upstream/overlays/cert-manager

# 13. 安装Central Dashboard
echo "12. 安装Central Dashboard..."
kubectl apply -f apps/centraldashboard/upstream/overlays/oauth2-proxy
kubectl apply -f apps/profiles/upstream/overlays/kubeflow

# 14. 安装Volumes Web App
kubectl apply -f apps/volumes-web-app/upstream/overlays/istio

# 15. 安装Tensorboards
kubectl apply -f apps/tensorboard/tensorboards-web-app/upstream/overlays/istio
kubectl apply -f apps/tensorboard/tensorboard-controller/upstream/overlays/kubeflow

# 16. 安装KServe
echo "13. 安装KServe..."
kubectl apply -f contrib/kserve/kserve
kubectl apply -f contrib/kserve/models-web-app/overlays/kubeflow

# 17. 验证安装
echo "14. 验证安装..."
kubectl get pods -n kubeflow
kubectl get pods -n istio-system

# 18. 获取访问信息
echo ""
echo "=== Kubeflow安装完成 ==="
echo "Dashboard URL: http://<LoadBalancer-IP>"
echo "默认用户: user@example.com"
echo "默认密码: 12341234"
echo ""
echo "获取LoadBalancer IP:"
echo "kubectl get svc istio-ingressgateway -n istio-system"
```

### Kubeflow Pipeline示例

```python
# ml_pipeline.py - Kubeflow Pipeline v2
from kfp import dsl
from kfp import compiler
from kfp.dsl import Input, Output, Dataset, Model, Metrics

@dsl.component(
    base_image='python:3.10',
    packages_to_install=['pandas', 'scikit-learn']
)
def load_data(dataset_path: str, output_data: Output[Dataset]):
    """加载数据"""
    import pandas as pd
    
    # 加载数据
    df = pd.read_csv(dataset_path)
    
    # 保存到artifact
    df.to_csv(output_data.path, index=False)
    print(f"Loaded {len(df)} samples")

@dsl.component(
    base_image='python:3.10',
    packages_to_install=['pandas', 'scikit-learn']
)
def preprocess_data(
    input_data: Input[Dataset],
    train_data: Output[Dataset],
    test_data: Output[Dataset]
):
    """数据预处理"""
    import pandas as pd
    from sklearn.model_selection import train_test_split
    
    df = pd.read_csv(input_data.path)
    
    # 分割训练/测试集
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    train_df.to_csv(train_data.path, index=False)
    test_df.to_csv(test_data.path, index=False)
    print(f"Train: {len(train_df)}, Test: {len(test_df)}")

@dsl.component(
    base_image='python:3.10',
    packages_to_install=['pandas', 'scikit-learn', 'joblib']
)
def train_model(
    train_data: Input[Dataset],
    model: Output[Model],
    metrics: Output[Metrics]
):
    """训练模型"""
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    import json
    
    train_df = pd.read_csv(train_data.path)
    X = train_df.drop('target', axis=1)
    y = train_df['target']
    
    # 训练
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    # 保存模型
    joblib.dump(clf, model.path)
    
    # 记录指标
    train_score = clf.score(X, y)
    metrics.log_metric('train_accuracy', train_score)
    print(f"Training accuracy: {train_score:.4f}")

@dsl.component(
    base_image='python:3.10',
    packages_to_install=['pandas', 'scikit-learn', 'joblib']
)
def evaluate_model(
    model: Input[Model],
    test_data: Input[Dataset],
    metrics: Output[Metrics]
):
    """评估模型"""
    import pandas as pd
    import joblib
    from sklearn.metrics import accuracy_score, f1_score
    
    test_df = pd.read_csv(test_data.path)
    X_test = test_df.drop('target', axis=1)
    y_test = test_df['target']
    
    # 加载模型
    clf = joblib.load(model.path)
    
    # 预测
    y_pred = clf.predict(X_test)
    
    # 计算指标
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    metrics.log_metric('test_accuracy', accuracy)
    metrics.log_metric('f1_score', f1)
    print(f"Test accuracy: {accuracy:.4f}, F1: {f1:.4f}")

@dsl.pipeline(
    name='ML Training Pipeline',
    description='Complete ML training pipeline'
)
def ml_pipeline(dataset_path: str = 'gs://my-bucket/data.csv'):
    # 1. 加载数据
    load_task = load_data(dataset_path=dataset_path)
    
    # 2. 预处理
    preprocess_task = preprocess_data(input_data=load_task.outputs['output_data'])
    
    # 3. 训练
    train_task = train_model(train_data=preprocess_task.outputs['train_data'])
    
    # 4. 评估
    evaluate_task = evaluate_model(
        model=train_task.outputs['model'],
        test_data=preprocess_task.outputs['test_data']
    )
    
    # GPU资源配置
    train_task.set_gpu_limit(1)
    train_task.set_memory_limit('8Gi')
    train_task.set_cpu_limit('4')

# 编译Pipeline
if __name__ == '__main__':
    compiler.Compiler().compile(
        pipeline_func=ml_pipeline,
        package_path='ml_pipeline.yaml'
    )
```

```bash
# 提交Pipeline
python ml_pipeline.py

# 使用kfp SDK提交
python -c "
from kfp import Client
client = Client(host='http://kubeflow-pipelines-api.kubeflow:8888')
run = client.create_run_from_pipeline_package(
    'ml_pipeline.yaml',
    arguments={'dataset_path': 'gs://my-data/train.csv'}
)
print(f'Run ID: {run.run_id}')
"
```

---

## 4. Ray + KubeRay分布式计算

### Ray 2.9+核心概念

```yaml
Ray_2_9_Overview:
  核心特性:
    分布式计算:
      - Task并行 (@ray.remote)
      - Actor模型 (有状态)
      - Object Store (零拷贝)
      - 自动故障恢复
    
    AI库生态:
      - Ray Train (分布式训练)
      - Ray Data (数据处理)
      - Ray Serve (模型服务)
      - Ray Tune (超参数调优)
      - Ray RLlib (强化学习)
    
    资源管理:
      - CPU/GPU/Custom资源
      - 资源打包
      - 节点亲和性
      - 弹性伸缩
  
  2025新特性:
    - Native GPU支持增强
    - Kubernetes集成改进
    - 数据预处理加速
    - 大模型训练优化
```

### 安装KubeRay Operator

```bash
#!/bin/bash
# install-kuberay-operator.sh

set -e

echo "=== 安装KubeRay Operator (2025) ==="

# 1. 添加Helm仓库
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update

# 2. 安装KubeRay Operator
kubectl create namespace ray-system --dry-run=client -o yaml | kubectl apply -f -

helm install kuberay-operator kuberay/kuberay-operator \
  --namespace ray-system \
  --version 1.1.0

# 3. 等待Operator就绪
kubectl wait --for=condition=available deployment/kuberay-operator \
  -n ray-system --timeout=300s

echo "=== KubeRay Operator安装完成 ==="
```

### RayCluster配置

```yaml
# raycluster-gpu.yaml
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: ray-gpu-cluster
  namespace: ray
spec:
  # Ray版本
  rayVersion: '2.9.0'
  
  # 启用自动伸缩
  enableInTreeAutoscaling: true
  autoscalerOptions:
    upscalingMode: Default
    idleTimeoutSeconds: 60
    resources:
      limits:
        cpu: "1"
        memory: "2Gi"
      requests:
        cpu: "500m"
        memory: "1Gi"
  
  # Head节点
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
      block: 'true'
    template:
      spec:
        containers:
        - name: ray-head
          image: rayproject/ray:2.9.0-py310-gpu
          ports:
          - containerPort: 6379  # Redis
            name: redis
          - containerPort: 8265  # Dashboard
            name: dashboard
          - containerPort: 10001  # Client
            name: client
          resources:
            limits:
              cpu: "4"
              memory: "16Gi"
            requests:
              cpu: "2"
              memory: "8Gi"
          volumeMounts:
          - name: ray-logs
            mountPath: /tmp/ray
        volumes:
        - name: ray-logs
          emptyDir: {}
  
  # Worker组 (GPU)
  workerGroupSpecs:
  - groupName: gpu-workers
    replicas: 2
    minReplicas: 0
    maxReplicas: 10
    rayStartParams:
      block: 'true'
    template:
      spec:
        nodeSelector:
          gpu-type: nvidia
        containers:
        - name: ray-worker
          image: rayproject/ray:2.9.0-py310-gpu
          resources:
            limits:
              cpu: "8"
              memory: "32Gi"
              nvidia.com/gpu: "1"  # 1 GPU per worker
            requests:
              cpu: "4"
              memory: "16Gi"
              nvidia.com/gpu: "1"
          volumeMounts:
          - name: ray-logs
            mountPath: /tmp/ray
          - name: shm
            mountPath: /dev/shm
        volumes:
        - name: ray-logs
          emptyDir: {}
        - name: shm
          emptyDir:
            medium: Memory
            sizeLimit: 8Gi  # Shared memory for Ray Object Store
  
  - groupName: cpu-workers
    replicas: 4
    minReplicas: 2
    maxReplicas: 20
    rayStartParams:
      block: 'true'
    template:
      spec:
        containers:
        - name: ray-worker
          image: rayproject/ray:2.9.0-py310
          resources:
            limits:
              cpu: "4"
              memory: "16Gi"
            requests:
              cpu: "2"
              memory: "8Gi"

---
# Ray Dashboard Service
apiVersion: v1
kind: Service
metadata:
  name: ray-dashboard
  namespace: ray
spec:
  type: LoadBalancer
  selector:
    ray.io/cluster: ray-gpu-cluster
    ray.io/node-type: head
  ports:
  - name: dashboard
    port: 8265
    targetPort: 8265
  - name: client
    port: 10001
    targetPort: 10001
```

### Ray分布式训练示例

```python
# ray_distributed_training.py
import ray
from ray import train
from ray.train import ScalingConfig
from ray.train.torch import TorchTrainer
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

# 1. 定义模型
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# 2. 定义训练函数
def train_func(config):
    # 获取分布式配置
    world_size = train.get_context().get_world_size()
    rank = train.get_context().get_world_rank()
    
    print(f"Worker {rank}/{world_size} starting...")
    
    # 创建模型 (自动分布式)
    model = SimpleModel()
    model = train.torch.prepare_model(model)
    
    # 数据加载
    # ... (DataLoader)
    
    # 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # 训练循环
    for epoch in range(config['num_epochs']):
        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = nn.CrossEntropyLoss()(output, target)
            loss.backward()
            optimizer.step()
            
            if batch_idx % 100 == 0:
                print(f"Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}")
                
                # 报告指标到Ray
                train.report({'loss': loss.item(), 'epoch': epoch})

# 3. 创建Trainer
if __name__ == '__main__':
    # 连接到Ray集群
    ray.init(address='ray://ray-dashboard.ray:10001')
    
    # 配置分布式训练
    scaling_config = ScalingConfig(
        num_workers=4,  # 4个worker
        use_gpu=True,   # 使用GPU
        resources_per_worker={'CPU': 4, 'GPU': 1}  # 每个worker资源
    )
    
    # 创建Trainer
    trainer = TorchTrainer(
        train_loop_per_worker=train_func,
        train_loop_config={'num_epochs': 10},
        scaling_config=scaling_config
    )
    
    # 开始训练
    result = trainer.fit()
    print(f"Training completed: {result}")
```

---

由于响应长度限制，我将在下一部分继续完成AI/ML文档的剩余章节（模型服务、MLOps、GPU共享等）。让我保存当前进度并继续。

**文档版本**: v1.0 (进行中)  
**更新日期**: 2025-10-20  
**状态**: 🔄 **创建中 - AI/ML云原生工作负载**

---

(文档将继续添加：KServe模型服务、MLOps流程、GPU共享虚拟化、分布式训练最佳实践、存储数据管理、生产环境案例)
