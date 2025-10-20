# WebAssembly容器化技术

> **返回**: [新兴技术2025](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [WebAssembly容器化技术](#webassembly容器化技术)
  - [📋 目录](#-目录)
  - [1. WebAssembly技术概览](#1-webassembly技术概览)
    - [核心概念](#核心概念)
    - [Wasm vs 容器初步对比](#wasm-vs-容器初步对比)
  - [2. Docker + Wasm (2025最新)](#2-docker--wasm-2025最新)
    - [Docker Desktop with Wasm](#docker-desktop-with-wasm)
    - [Docker + Wasm 快速开始](#docker--wasm-快速开始)
    - [高级示例：HTTP服务器 (Rust + Wasm)](#高级示例http服务器-rust--wasm)
  - [3. containerd + Wasm集成](#3-containerd--wasm集成)
    - [containerd-wasm-shims](#containerd-wasm-shims)
    - [安装 containerd-wasm-shims](#安装-containerd-wasm-shims)
    - [ctr运行Wasm容器](#ctr运行wasm容器)
  - [4. WasmEdge运行时](#4-wasmedge运行时)
    - [WasmEdge核心特性](#wasmedge核心特性)
    - [WasmEdge直接使用](#wasmedge直接使用)
    - [WasmEdge高级功能：TensorFlow推理](#wasmedge高级功能tensorflow推理)
  - [5. Kubernetes + Wasm](#5-kubernetes--wasm)
    - [RuntimeClass配置](#runtimeclass配置)
    - [Wasm Deployment示例](#wasm-deployment示例)
    - [Knative + Wasm (Serverless)](#knative--wasm-serverless)
  - [6. Wasm vs 容器对比](#6-wasm-vs-容器对比)
    - [详细性能对比](#详细性能对比)
    - [选型决策树](#选型决策树)
  - [7. 生产环境部署](#7-生产环境部署)
    - [Wasm节点准备](#wasm节点准备)
    - [Wasm CI/CD流水线](#wasm-cicd流水线)
  - [8. 应用场景与案例](#8-应用场景与案例)
    - [场景1：边缘计算（IoT）](#场景1边缘计算iot)
    - [场景2：API网关插件系统](#场景2api网关插件系统)
    - [场景3：Serverless函数 (OpenFaaS + Wasm)](#场景3serverless函数-openfaas--wasm)
  - [9. 性能优化](#9-性能优化)
    - [Wasm性能调优](#wasm性能调优)
    - [性能基准测试](#性能基准测试)
  - [10. 未来趋势](#10-未来趋势)
    - [2025-2026技术路线图](#2025-2026技术路线图)
    - [行业采用趋势](#行业采用趋势)
  - [相关文档](#相关文档)
    - [本模块文档](#本模块文档)
    - [相关模块](#相关模块)
    - [外部资源](#外部资源)

---

## 1. WebAssembly技术概览

### 核心概念

```yaml
WebAssembly_Overview_2025:
  定义:
    全称: Web Assembly (Wasm)
    本质: 二进制指令格式
    目标: 高性能、安全、可移植
    标准: W3C标准 (2019成为正式推荐)
  
  核心特性:
    性能:
      - 近原生执行速度
      - 编译型 (AOT/JIT)
      - SIMD指令支持
      - 多线程支持
    
    安全:
      - 沙箱隔离
      - 能力安全模型 (Capability-based)
      - 内存安全
      - 无需系统调用权限
    
    可移植:
      - 跨平台 (x86/ARM/RISC-V)
      - 跨操作系统
      - 跨语言编译
      - 统一字节码
    
    轻量:
      - 启动时间 <10ms
      - 内存占用 <1MB
      - 镜像大小 <2MB
      - 无需操作系统

  技术演进:
    MVP_2017: 基础功能
    2018_2020: WASI (系统接口)
    2021_2023: 组件模型、异常处理
    2024_2025: 云原生集成、容器化

  WASI_WebAssembly_System_Interface:
    定义: WebAssembly系统接口标准
    用途: 访问文件、网络、环境变量
    版本: WASI Preview 2 (2024)
    
    能力模型:
      - 文件系统访问
      - 网络套接字
      - 随机数生成
      - 时钟和时间
      - 环境变量
      - 命令行参数
```

### Wasm vs 容器初步对比

```yaml
Wasm_vs_Container_Overview:
  启动速度:
    Wasm: "<10ms"
    Container: "100ms - 1s"
    优势: Wasm 快10-100倍
  
  内存占用:
    Wasm: "<1MB"
    Container: "10-100MB+"
    优势: Wasm 小10-100倍
  
  镜像大小:
    Wasm: "1-5MB"
    Container: "100MB - 1GB+"
    优势: Wasm 小20-200倍
  
  安全隔离:
    Wasm: "能力安全模型 + 沙箱"
    Container: "Namespace + Cgroup + Seccomp"
    对比: 不同的安全模型
  
  生态成熟度:
    Wasm: "快速成长中 (2025年)"
    Container: "成熟完善"
    优势: Container 更成熟
  
  适用场景:
    Wasm: "微服务、Serverless、边缘计算、插件系统"
    Container: "通用应用、复杂系统、数据库、中间件"
```

---

## 2. Docker + Wasm (2025最新)

### Docker Desktop with Wasm

Docker Desktop 4.15+ (2023.10) 开始原生支持Wasm，2025年已完全成熟。

```yaml
Docker_Wasm_Support_2025:
  版本要求:
    Docker_Desktop: "4.15+"
    Docker_Engine: "24.0+"
    containerd: "1.7+"
  
  运行时:
    - WasmEdge
    - Wasmtime
    - WAMR (WebAssembly Micro Runtime)
    - Wasmer (实验性)
  
  特性:
    - Dockerfile构建Wasm镜像
    - docker run运行Wasm
    - docker-compose支持
    - 多架构构建 (linux/wasm32/wasi)
    - OCI镜像标准兼容
```

### Docker + Wasm 快速开始

```bash
#!/bin/bash
# docker-wasm-quickstart.sh - 2025年Docker Wasm快速上手

set -e

echo "=== Docker + Wasm 快速开始 (2025) ==="

# 1. 检查Docker版本
echo "1. 检查Docker版本..."
DOCKER_VERSION=$(docker version --format '{{.Server.Version}}')
echo "Docker版本: $DOCKER_VERSION"

if [[ $(echo "$DOCKER_VERSION 24.0" | awk '{print ($1 >= $2)}') -eq 0 ]]; then
    echo "错误: Docker版本需要 >= 24.0"
    exit 1
fi

# 2. 启用Wasm支持 (Docker Desktop自动启用)
echo "2. 验证Wasm支持..."
docker buildx version

# 3. 创建示例Rust Wasm应用
echo "3. 创建示例应用..."
mkdir -p ~/docker-wasm-demo
cd ~/docker-wasm-demo

cat > hello.rs <<'EOF'
fn main() {
    println!("Hello from WebAssembly in Docker! 🚀");
    println!("Current time: {}", std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs());
}
EOF

# 4. 创建Dockerfile
cat > Dockerfile <<'EOF'
# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM rust:1.75 AS builder

# 安装wasm32-wasi目标
RUN rustup target add wasm32-wasi

# 构建应用
WORKDIR /app
COPY hello.rs .
RUN rustc --target wasm32-wasi hello.rs -o hello.wasm

# 运行时镜像
FROM scratch
COPY --from=builder /app/hello.wasm /hello.wasm
ENTRYPOINT ["/hello.wasm"]
EOF

# 5. 构建Wasm镜像
echo "4. 构建Wasm镜像..."
docker buildx build --platform wasi/wasm --provenance=false -t hello-wasm .

# 6. 运行Wasm容器
echo "5. 运行Wasm容器..."
docker run --rm --runtime=io.containerd.wasmedge.v1 --platform=wasi/wasm hello-wasm

# 7. 性能对比测试
echo ""
echo "6. 性能对比测试..."

# Wasm启动时间
echo -n "Wasm启动时间: "
time docker run --rm --runtime=io.containerd.wasmedge.v1 --platform=wasi/wasm hello-wasm > /dev/null

# 对比：构建同样的Linux容器
cat > Dockerfile.linux <<'EOF'
FROM rust:1.75-slim AS builder
WORKDIR /app
COPY hello.rs .
RUN rustc hello.rs -o hello

FROM debian:bookworm-slim
COPY --from=builder /app/hello /hello
CMD ["/hello"]
EOF

docker build -f Dockerfile.linux -t hello-linux .

# Linux容器启动时间
echo -n "Linux容器启动时间: "
time docker run --rm hello-linux > /dev/null

echo ""
echo "=== Docker Wasm Demo完成 ==="
echo "镜像大小对比:"
docker images | grep hello
```

### 高级示例：HTTP服务器 (Rust + Wasm)

```rust
// src/main.rs - HTTP服务器 (Wasm)
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

fn handle_client(mut stream: TcpStream) {
    let mut buffer = [0; 1024];
    stream.read(&mut buffer).unwrap();

    let response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n\
                    <html><body>\
                    <h1>Hello from WebAssembly! 🎉</h1>\
                    <p>This HTTP server is running in a Wasm container.</p>\
                    </body></html>";

    stream.write(response.as_bytes()).unwrap();
    stream.flush().unwrap();
}

fn main() {
    let listener = TcpListener::bind("0.0.0.0:8080").unwrap();
    println!("Wasm HTTP Server listening on http://0.0.0.0:8080");

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => handle_client(stream),
            Err(e) => eprintln!("Error: {}", e),
        }
    }
}
```

```dockerfile
# Dockerfile for Wasm HTTP Server
FROM --platform=$BUILDPLATFORM rust:1.75 AS builder

RUN rustup target add wasm32-wasi

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src

# 构建Wasm二进制
RUN cargo build --target wasm32-wasi --release

# 最终镜像
FROM scratch
COPY --from=builder /app/target/wasm32-wasi/release/http-server.wasm /server.wasm
EXPOSE 8080
ENTRYPOINT ["/server.wasm"]
```

```bash
# 构建和运行
docker buildx build --platform wasi/wasm --provenance=false -t wasm-http-server .
docker run --rm -p 8080:8080 --runtime=io.containerd.wasmedge.v1 --platform=wasi/wasm wasm-http-server

# 测试
curl http://localhost:8080
```

---

## 3. containerd + Wasm集成

### containerd-wasm-shims

containerd 1.7+ 通过shim机制支持多个Wasm运行时。

```yaml
containerd_Wasm_Architecture:
  组件:
    containerd: "容器运行时 (1.7+)"
    shim: "Wasm运行时适配器"
    runtime: "实际Wasm引擎"
  
  支持的Wasm运行时:
    WasmEdge:
      - 高性能CNCF项目
      - 支持WASI、网络、GPU
      - Rust实现
      - shim: containerd-wasmedge-shim
    
    Wasmtime:
      - Bytecode Alliance项目
      - 安全性优先
      - Rust实现
      - shim: containerd-wasmtime-shim
    
    WAMR:
      - 嵌入式优化
      - 低资源消耗
      - C实现
      - shim: containerd-wamr-shim
    
    Wasmer:
      - 多语言支持
      - 插件系统
      - shim: containerd-wasmer-shim
```

### 安装 containerd-wasm-shims

```bash
#!/bin/bash
# install-containerd-wasm-shims.sh

set -e

echo "=== 安装 containerd Wasm Shims (2025) ==="

# 1. 检查containerd版本
CONTAINERD_VERSION=$(containerd --version | awk '{print $3}' | tr -d 'v')
echo "containerd版本: $CONTAINERD_VERSION"

if [[ $(echo "$CONTAINERD_VERSION 1.7" | awk '{print ($1 >= $2)}') -eq 0 ]]; then
    echo "错误: containerd版本需要 >= 1.7"
    exit 1
fi

# 2. 下载并安装WasmEdge shim
echo "2. 安装WasmEdge shim..."
SHIM_VERSION="v0.13.0"
wget -q https://github.com/containerd/runwasi/releases/download/${SHIM_VERSION}/containerd-wasmedge-shim-${SHIM_VERSION}-linux-amd64.tar.gz
tar -xzf containerd-wasmedge-shim-${SHIM_VERSION}-linux-amd64.tar.gz
sudo mv containerd-shim-wasmedge-v1 /usr/local/bin/
sudo chmod +x /usr/local/bin/containerd-shim-wasmedge-v1

# 3. 下载并安装Wasmtime shim
echo "3. 安装Wasmtime shim..."
wget -q https://github.com/containerd/runwasi/releases/download/${SHIM_VERSION}/containerd-wasmtime-shim-${SHIM_VERSION}-linux-amd64.tar.gz
tar -xzf containerd-wasmtime-shim-${SHIM_VERSION}-linux-amd64.tar.gz
sudo mv containerd-shim-wasmtime-v1 /usr/local/bin/
sudo chmod +x /usr/local/bin/containerd-shim-wasmtime-v1

# 4. 配置containerd
echo "4. 配置containerd..."
sudo tee /etc/containerd/config.toml > /dev/null <<EOF
version = 2

[plugins]
  [plugins."io.containerd.grpc.v1.cri"]
    [plugins."io.containerd.grpc.v1.cri".containerd]
      default_runtime_name = "runc"
      
      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
        # 标准runc运行时
        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
          runtime_type = "io.containerd.runc.v2"
        
        # WasmEdge运行时
        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.wasmedge]
          runtime_type = "io.containerd.wasmedge.v1"
        
        # Wasmtime运行时
        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.wasmtime]
          runtime_type = "io.containerd.wasmtime.v1"
EOF

# 5. 重启containerd
echo "5. 重启containerd..."
sudo systemctl restart containerd

# 6. 验证
echo "6. 验证安装..."
ls -lh /usr/local/bin/containerd-shim-*

echo ""
echo "=== 安装完成 ==="
echo "可用运行时:"
echo "- io.containerd.wasmedge.v1"
echo "- io.containerd.wasmtime.v1"
```

### ctr运行Wasm容器

```bash
#!/bin/bash
# ctr-wasm-example.sh

set -e

echo "=== ctr运行Wasm容器示例 ==="

# 1. 拉取Wasm镜像
echo "1. 拉取Wasm镜像..."
sudo ctr image pull docker.io/wasmedge/example-wasi:latest

# 2. 使用WasmEdge运行时运行
echo "2. 使用WasmEdge运行..."
sudo ctr run --rm \
    --runtime=io.containerd.wasmedge.v1 \
    docker.io/wasmedge/example-wasi:latest \
    wasi-demo

# 3. 使用Wasmtime运行时运行
echo "3. 使用Wasmtime运行..."
sudo ctr run --rm \
    --runtime=io.containerd.wasmtime.v1 \
    docker.io/wasmedge/example-wasi:latest \
    wasi-demo-2

echo "=== 完成 ==="
```

---

## 4. WasmEdge运行时

### WasmEdge核心特性

```yaml
WasmEdge_Features_2025:
  基本信息:
    组织: CNCF Sandbox → Incubating (2023)
    语言: Rust
    性能: 接近原生 (95-98%)
    许可: Apache 2.0
  
  核心特性:
    标准支持:
      - WebAssembly 1.0/2.0
      - WASI Preview 2
      - 组件模型
      - 异常处理
      - SIMD
      - 线程
    
    扩展能力:
      - TensorFlow推理
      - PyTorch推理
      - ONNX运行时
      - 图像处理
      - 密码学
    
    网络支持:
      - TCP/UDP套接字
      - HTTP客户端/服务器
      - WebSocket
      - gRPC
    
    云原生集成:
      - containerd集成
      - Kubernetes支持
      - Docker兼容
      - OCI镜像

  性能优势:
    AOT编译: 提前编译优化
    JIT编译: 即时编译支持
    SIMD加速: 向量指令
    多线程: 并行执行
```

### WasmEdge直接使用

```bash
#!/bin/bash
# wasmedge-standalone-usage.sh

set -e

echo "=== WasmEdge独立使用示例 ==="

# 1. 安装WasmEdge
echo "1. 安装WasmEdge..."
curl -sSf https://raw.githubusercontent.com/WasmEdge/WasmEdge/master/utils/install.sh | bash -s -- --version=0.13.5

source $HOME/.wasmedge/env

# 2. 验证安装
echo "2. 验证WasmEdge..."
wasmedge --version

# 3. 运行简单Wasm程序
echo "3. 运行Hello World..."
cat > hello.wat <<'EOF'
(module
  (import "wasi_snapshot_preview1" "fd_write"
    (func $fd_write (param i32 i32 i32 i32) (result i32)))
  (memory 1)
  (export "memory" (memory 0))
  
  (data (i32.const 8) "Hello from WasmEdge!\n")
  
  (func $main (export "_start")
    (i32.store (i32.const 0) (i32.const 8))
    (i32.store (i32.const 4) (i32.const 21))
    
    (call $fd_write
      (i32.const 1)
      (i32.const 0)
      (i32.const 1)
      (i32.const 20))
    drop))
EOF

# 编译WAT到Wasm
wat2wasm hello.wat -o hello.wasm

# 运行
wasmedge hello.wasm

# 4. AOT编译示例
echo "4. AOT编译优化..."
wasmedgec hello.wasm hello_aot.wasm
wasmedge hello_aot.wasm

# 5. 性能对比
echo "5. 性能对比..."
echo "解释执行："
time wasmedge hello.wasm

echo "AOT执行："
time wasmedge hello_aot.wasm

echo "=== 完成 ==="
```

### WasmEdge高级功能：TensorFlow推理

```bash
#!/bin/bash
# wasmedge-tensorflow-inference.sh

set -e

echo "=== WasmEdge TensorFlow推理示例 ==="

# 1. 安装WasmEdge with TensorFlow插件
curl -sSf https://raw.githubusercontent.com/WasmEdge/WasmEdge/master/utils/install.sh | \
    bash -s -- --version=0.13.5 --plugins wasmedge_tensorflow

# 2. 下载示例代码
git clone https://github.com/second-state/wasm-learning.git
cd wasm-learning/rust/mobilenet

# 3. 构建Wasm模块
rustup target add wasm32-wasi
cargo build --target wasm32-wasi --release

# 4. 下载MobileNet模型
wget https://storage.googleapis.com/mobilenet_v2/checkpoints/mobilenet_v2_1.4_224.tgz
tar -xzf mobilenet_v2_1.4_224.tgz

# 5. 运行推理
wasmedge --dir .:. target/wasm32-wasi/release/mobilenet.wasm mobilenet_v2_1.4_224.pb grace_hopper.jpg

echo "=== TensorFlow推理完成 ==="
```

---

## 5. Kubernetes + Wasm

### RuntimeClass配置

```yaml
# wasm-runtimeclass.yaml - Kubernetes Wasm运行时类
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: wasmedge
handler: wasmedge

---
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: wasmtime
handler: wasmtime

---
# 使用RuntimeClass的Pod
apiVersion: v1
kind: Pod
metadata:
  name: wasm-pod
  labels:
    app: wasm-demo
spec:
  runtimeClassName: wasmedge  # 使用WasmEdge运行时
  containers:
  - name: wasm-app
    image: docker.io/wasmedge/example-wasi:latest
    resources:
      requests:
        cpu: 100m
        memory: 64Mi
      limits:
        cpu: 200m
        memory: 128Mi
  nodeSelector:
    wasm.enabled: "true"
```

### Wasm Deployment示例

```yaml
# wasm-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wasm-http-server
  namespace: wasm-apps
  labels:
    app: wasm-http
spec:
  replicas: 3
  selector:
    matchLabels:
      app: wasm-http
  template:
    metadata:
      labels:
        app: wasm-http
    spec:
      runtimeClassName: wasmedge
      containers:
      - name: http-server
        image: your-registry/wasm-http-server:v1.0.0
        ports:
        - containerPort: 8080
          protocol: TCP
        env:
        - name: SERVER_PORT
          value: "8080"
        resources:
          requests:
            cpu: 50m      # Wasm资源占用极小
            memory: 32Mi
          limits:
            cpu: 100m
            memory: 64Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 1  # Wasm启动极快
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 1
          periodSeconds: 5
      nodeSelector:
        wasm.enabled: "true"

---
apiVersion: v1
kind: Service
metadata:
  name: wasm-http-server
  namespace: wasm-apps
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
  selector:
    app: wasm-http

---
# HorizontalPodAutoscaler for Wasm
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: wasm-http-hpa
  namespace: wasm-apps
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: wasm-http-server
  minReplicas: 3
  maxReplicas: 100  # Wasm轻量，可以大量扩展
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # Wasm启动快，立即扩容
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
```

### Knative + Wasm (Serverless)

```yaml
# knative-wasm-service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: wasm-function
  namespace: knative-serving
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "0"  # 可以缩容到0
        autoscaling.knative.dev/max-scale: "1000"
        autoscaling.knative.dev/target: "100"
        autoscaling.knative.dev/scale-down-delay: "30s"
    spec:
      runtimeClassName: wasmedge
      containers:
      - image: your-registry/wasm-function:v1.0
        ports:
        - containerPort: 8080
        env:
        - name: TARGET
          value: "Wasm Serverless"
        resources:
          requests:
            cpu: 10m      # 极低资源请求
            memory: 16Mi
          limits:
            cpu: 100m
            memory: 64Mi
      timeout: 30s

---
# 测试Serverless函数
apiVersion: v1
kind: ConfigMap
metadata:
  name: wasm-function-test
  namespace: knative-serving
data:
  test.sh: |
    #!/bin/bash
    # 获取Knative Service URL
    URL=$(kubectl get ksvc wasm-function -n knative-serving -o jsonpath='{.status.url}')
    
    echo "=== Wasm Serverless函数测试 ==="
    echo "URL: $URL"
    
    # 冷启动测试
    echo ""
    echo "冷启动测试 (从0实例):"
    kubectl scale deployment -n knative-serving \
      $(kubectl get deploy -n knative-serving -l serving.knative.dev/service=wasm-function -o name) \
      --replicas=0
    sleep 5
    time curl -s $URL
    
    # 热启动测试
    echo ""
    echo "热启动测试:"
    time curl -s $URL
    
    # 并发测试
    echo ""
    echo "并发测试 (100个请求):"
    ab -n 100 -c 10 $URL/
```

---

## 6. Wasm vs 容器对比

### 详细性能对比

```yaml
Detailed_Wasm_vs_Container_2025:
  启动性能:
    Wasm:
      冷启动: "5-10ms"
      热启动: "1-5ms"
      实例化: "极快"
    
    Container:
      冷启动: "100-1000ms"
      热启动: "10-100ms"
      镜像拉取: "可能需要秒级"
    
    场景:
      Serverless: Wasm优势明显
      边缘计算: Wasm更适合
      长期运行: 差异不大
  
  资源占用:
    Wasm:
      内存: "1-10MB"
      CPU: "近原生性能"
      磁盘: "1-5MB镜像"
    
    Container:
      内存: "10-100MB+"
      CPU: "接近原生"
      磁盘: "100MB-1GB+ 镜像"
    
    场景:
      资源受限: Wasm优势
      大规模部署: Wasm节省成本
      复杂应用: Container更灵活
  
  安全隔离:
    Wasm:
      模型: "能力安全 (Capability-based)"
      沙箱: "语言级沙箱"
      系统调用: "WASI接口受限"
      攻击面: "极小"
    
    Container:
      模型: "Namespace + Cgroup"
      沙箱: "内核级隔离"
      系统调用: "Seccomp过滤"
      攻击面: "较大"
    
    场景:
      多租户: Wasm更安全
      特权操作: Container更灵活
  
  生态系统:
    Wasm:
      语言: "Rust, C/C++, Go, AssemblyScript等"
      工具链: "快速发展"
      库支持: "有限但增长快"
      社区: "活跃增长"
    
    Container:
      语言: "所有语言"
      工具链: "成熟完善"
      库支持: "丰富"
      社区: "非常成熟"
  
  可移植性:
    Wasm:
      架构: "完全跨平台 (x86/ARM/RISC-V)"
      操作系统: "跨OS (甚至浏览器)"
      编译一次: "到处运行"
    
    Container:
      架构: "需要多架构镜像"
      操作系统: "Linux为主"
      平台特定: "可能需要调整"
```

### 选型决策树

```yaml
When_to_Use_Wasm_vs_Container:
  使用Wasm的场景:
    ✅_完美匹配:
      - Serverless函数 (FaaS)
      - 边缘计算节点
      - IoT设备
      - 插件系统
      - 微服务 (无状态)
      - API网关/代理
      - 数据处理函数
      - 计算密集任务
    
    条件:
      - 启动速度关键
      - 资源受限环境
      - 多租户高密度
      - 需要极致隔离
      - 跨平台要求高
      - 镜像大小敏感
  
  使用容器的场景:
    ✅_完美匹配:
      - 传统应用迁移
      - 复杂多进程应用
      - 数据库
      - 消息队列
      - 需要完整OS环境
      - 遗留系统
      - 需要内核特性
      - 需要特权操作
    
    条件:
      - 应用依赖OS库
      - 需要系统级工具
      - 生态系统成熟度优先
      - 长期运行服务
      - 复杂网络配置
  
  混合使用场景:
    🔄_最佳实践:
      - Wasm: API层、计算函数、边缘节点
      - Container: 数据库、中间件、存储
      - Istio + Wasm: 服务网格数据平面
      - Knative + Wasm: Serverless函数
      - K8s: 同时调度Wasm和容器
```

---

## 7. 生产环境部署

### Wasm节点准备

```bash
#!/bin/bash
# prepare-wasm-k8s-node.sh - 准备Kubernetes Wasm节点

set -e

echo "=== 准备Kubernetes Wasm节点 ==="

# 1. 安装containerd (如果还未安装)
if ! command -v containerd &> /dev/null; then
    echo "1. 安装containerd..."
    wget https://github.com/containerd/containerd/releases/download/v1.7.11/containerd-1.7.11-linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf containerd-1.7.11-linux-amd64.tar.gz
    
    # 安装systemd服务
    sudo mkdir -p /usr/local/lib/systemd/system
    sudo wget -O /usr/local/lib/systemd/system/containerd.service \
        https://raw.githubusercontent.com/containerd/containerd/main/containerd.service
    sudo systemctl daemon-reload
    sudo systemctl enable --now containerd
fi

# 2. 安装Wasm shims
echo "2. 安装Wasm运行时shims..."
SHIM_VERSION="v0.13.0"

# WasmEdge
wget https://github.com/containerd/runwasi/releases/download/${SHIM_VERSION}/containerd-wasmedge-shim-${SHIM_VERSION}-linux-amd64.tar.gz
tar -xzf containerd-wasmedge-shim-${SHIM_VERSION}-linux-amd64.tar.gz
sudo mv containerd-shim-wasmedge-v1 /usr/local/bin/
sudo chmod +x /usr/local/bin/containerd-shim-wasmedge-v1

# Wasmtime
wget https://github.com/containerd/runwasi/releases/download/${SHIM_VERSION}/containerd-wasmtime-shim-${SHIM_VERSION}-linux-amd64.tar.gz
tar -xzf containerd-wasmtime-shim-${SHIM_VERSION}-linux-amd64.tar.gz
sudo mv containerd-shim-wasmtime-v1 /usr/local/bin/
sudo chmod +x /usr/local/bin/containerd-shim-wasmtime-v1

# 3. 配置containerd
echo "3. 配置containerd支持Wasm..."
sudo mkdir -p /etc/containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml

# 添加Wasm运行时配置
sudo tee -a /etc/containerd/config.toml > /dev/null <<EOF

# Wasm Runtime Configurations
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.wasmedge]
  runtime_type = "io.containerd.wasmedge.v1"

[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.wasmtime]
  runtime_type = "io.containerd.wasmtime.v1"
EOF

sudo systemctl restart containerd

# 4. 标记节点支持Wasm
echo "4. 标记Kubernetes节点..."
NODE_NAME=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl label node $NODE_NAME wasm.enabled=true --overwrite

# 5. 验证
echo "5. 验证Wasm支持..."
sudo ctr plugins ls | grep wasm

echo ""
echo "=== Wasm节点准备完成 ==="
echo "节点标签: wasm.enabled=true"
echo "支持的运行时:"
echo "- io.containerd.wasmedge.v1"
echo "- io.containerd.wasmtime.v1"
```

### Wasm CI/CD流水线

```yaml
# .github/workflows/wasm-cicd.yml
name: Wasm CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/wasm-app

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Rust
      uses: actions-rs/toolchain@v1
      with:
        toolchain: stable
        target: wasm32-wasi
        override: true
    
    - name: Build Wasm binary
      run: |
        cargo build --target wasm32-wasi --release
        ls -lh target/wasm32-wasi/release/*.wasm
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=sha,prefix={{branch}}-
    
    - name: Build and push Wasm image
      uses: docker/build-push-action@v5
      with:
        context: .
        platforms: wasi/wasm
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        provenance: false  # 重要：禁用provenance for Wasm
    
    - name: Test Wasm image locally
      run: |
        docker run --rm --runtime=io.containerd.wasmedge.v1 \
          --platform=wasi/wasm \
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    
    - name: Deploy to Kubernetes (if main branch)
      if: github.ref == 'refs/heads/main'
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        
        kubectl set image deployment/wasm-app \
          wasm-app=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
          -n production
        
        kubectl rollout status deployment/wasm-app -n production
```

---

## 8. 应用场景与案例

### 场景1：边缘计算（IoT）

```yaml
# edge-iot-wasm-deployment.yaml
# 场景：IoT设备数据处理

apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: iot-data-processor
  namespace: edge-iot
spec:
  selector:
    matchLabels:
      app: iot-processor
  template:
    metadata:
      labels:
        app: iot-processor
    spec:
      runtimeClassName: wasmedge
      nodeSelector:
        node-role.kubernetes.io/edge: ""  # 边缘节点
      containers:
      - name: processor
        image: your-registry/iot-wasm-processor:v1.0
        resources:
          requests:
            cpu: 10m       # 极低资源占用
            memory: 16Mi
          limits:
            cpu: 50m
            memory: 64Mi
        env:
        - name: MQTT_BROKER
          value: "mqtt://broker.local:1883"
        - name: PROCESSING_INTERVAL
          value: "1s"
        volumeMounts:
        - name: device-data
          mountPath: /data
          readOnly: true
      volumes:
      - name: device-data
        hostPath:
          path: /var/iot/data
          type: Directory
      tolerations:
      - key: node-role.kubernetes.io/edge
        operator: Exists
```

### 场景2：API网关插件系统

```yaml
# api-gateway-wasm-plugins.yaml
# 场景：Envoy/Istio API网关的Wasm插件

apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: wasm-auth-plugin
  namespace: istio-system
spec:
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: GATEWAY
      listener:
        filterChain:
          filter:
            name: "envoy.filters.network.http_connection_manager"
            subFilter:
              name: "envoy.filters.http.router"
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.wasm
        typed_config:
          "@type": type.googleapis.com/udpa.type.v1.TypedStruct
          type_url: type.googleapis.com/envoy.extensions.filters.http.wasm.v3.Wasm
          value:
            config:
              name: "auth_plugin"
              root_id: "auth"
              vm_config:
                runtime: "envoy.wasm.runtime.v8"
                code:
                  remote:
                    http_uri:
                      uri: https://your-cdn.com/wasm-plugins/auth-v1.0.wasm
                      cluster: wasm_plugin_cluster
                      timeout: 10s
                    sha256: "abc123..."  # Wasm文件的SHA256
              configuration:
                "@type": "type.googleapis.com/google.protobuf.StringValue"
                value: |
                  {
                    "jwt_secret": "your-secret",
                    "token_header": "Authorization",
                    "allowed_paths": ["/public", "/health"]
                  }

---
# Wasm插件服务
apiVersion: v1
kind: Service
metadata:
  name: wasm-plugin-registry
  namespace: istio-system
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    name: http
  selector:
    app: wasm-plugin-registry

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wasm-plugin-registry
  namespace: istio-system
spec:
  replicas: 2
  selector:
    matchLabels:
      app: wasm-plugin-registry
  template:
    metadata:
      labels:
        app: wasm-plugin-registry
    spec:
      containers:
      - name: registry
        image: nginx:alpine
        volumeMounts:
        - name: plugins
          mountPath: /usr/share/nginx/html/plugins
      volumes:
      - name: plugins
        configMap:
          name: wasm-plugins
```

### 场景3：Serverless函数 (OpenFaaS + Wasm)

```yaml
# openfaas-wasm-function.yaml
apiVersion: openfaas.com/v1
kind: Function
metadata:
  name: image-resize-wasm
  namespace: openfaas-fn
spec:
  name: image-resize-wasm
  image: your-registry/image-resize-wasm:latest
  
  # Wasm特定配置
  annotations:
    com.openfaas.scale.min: "0"
    com.openfaas.scale.max: "1000"
    com.openfaas.scale.factor: "5"
    com.openfaas.scale.type: "rps"  # 基于RPS扩展
    com.openfaas.health.http.path: "/health"
  
  labels:
    runtime: "wasmedge"
    tier: "compute"
  
  environment:
    max_image_size: "10485760"  # 10MB
    output_format: "webp"
    quality: "85"
  
  limits:
    cpu: "100m"
    memory: "64Mi"
  requests:
    cpu: "10m"
    memory: "16Mi"
  
  # 使用Wasm RuntimeClass
  runtimeClassName: wasmedge

---
# 测试函数
apiVersion: batch/v1
kind: Job
metadata:
  name: test-wasm-function
  namespace: openfaas-fn
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: test
        image: curlimages/curl:latest
        command:
          - /bin/sh
          - -c
          - |
            # 测试函数
            curl -X POST http://gateway.openfaas:8080/function/image-resize-wasm \
              --data-binary @/test-image.jpg \
              -H "Content-Type: image/jpeg" \
              -o /tmp/resized.webp
            
            echo "Resized image saved"
```

---

## 9. 性能优化

### Wasm性能调优

```yaml
Wasm_Performance_Tuning:
  编译优化:
    Rust:
      release_profile:
        opt-level: "z"  # 优化大小
        lto: true       # Link-Time Optimization
        codegen-units: 1
        strip: true     # 去除符号
      
      example_Cargo.toml: |
        [profile.release]
        opt-level = "z"
        lto = true
        codegen-units = 1
        panic = "abort"
        strip = true
    
    wasm-opt:
      tool: "Binaryen wasm-opt"
      options:
        - "-Oz"  # 最大化大小优化
        - "--enable-simd"
        - "--enable-threads"
      
      command: |
        wasm-opt -Oz --enable-simd input.wasm -o output.wasm
  
  运行时优化:
    AOT编译:
      WasmEdge: "wasmedgec input.wasm output_aot.wasm"
      Wasmtime: "wasmtime compile input.wasm -o output.cwasm"
      优势: "消除解释开销，提升10-30%性能"
    
    内存配置:
      initial_pages: 1  # 64KB * pages
      maximum_pages: 16  # 最多1MB
      策略: "按需分配，避免浪费"
    
    线程池:
      worker_threads: 4
      async_runtime: "Tokio"
      优势: "并行处理请求"
  
  Kubernetes优化:
    资源请求:
      策略: "精确配置，避免过度分配"
      cpu: "10-100m"
      memory: "16-64Mi"
    
    HPA配置:
      min_replicas: 0  # Wasm可以从0扩展
      max_replicas: 1000
      scale_up_fast: true  # 快速扩容
      scale_down_delay: 30s
    
    节点亲和性:
      prefer_high_cpu: true
      avoid_high_memory_nodes: true
```

### 性能基准测试

```bash
#!/bin/bash
# wasm-performance-benchmark.sh

set -e

echo "=== Wasm vs Container 性能基准测试 ==="

# 1. 准备测试
mkdir -p /tmp/wasm-benchmark
cd /tmp/wasm-benchmark

# 2. 构建相同的应用 (HTTP服务器)
# Wasm版本已构建
# Container版本已构建

# 3. 冷启动测试
echo ""
echo "=== 冷启动测试 ==="

echo "Wasm冷启动:"
kubectl delete pod wasm-test --ignore-not-found=true
time kubectl run wasm-test --image=wasm-http:v1 \
  --runtime-class-name=wasmedge \
  --restart=Never \
  -- /bin/sh -c "sleep 0.001"
kubectl wait --for=condition=Ready pod/wasm-test --timeout=60s
kubectl delete pod wasm-test

echo "Container冷启动:"
kubectl delete pod container-test --ignore-not-found=true
time kubectl run container-test --image=http-server:v1 \
  --restart=Never \
  -- /bin/sh -c "sleep 0.001"
kubectl wait --for=condition=Ready pod/container-test --timeout=60s
kubectl delete pod container-test

# 4. 内存占用测试
echo ""
echo "=== 内存占用测试 ==="

kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: wasm-memory-test
spec:
  runtimeClassName: wasmedge
  containers:
  - name: wasm
    image: wasm-http:v1
    resources:
      requests:
        memory: 32Mi
      limits:
        memory: 64Mi
---
apiVersion: v1
kind: Pod
metadata:
  name: container-memory-test
spec:
  containers:
  - name: container
    image: http-server:v1
    resources:
      requests:
        memory: 32Mi
      limits:
        memory: 128Mi
EOF

kubectl wait --for=condition=Ready pod/wasm-memory-test --timeout=60s
kubectl wait --for=condition=Ready pod/container-memory-test --timeout=60s

echo "Wasm内存使用:"
kubectl top pod wasm-memory-test

echo "Container内存使用:"
kubectl top pod container-memory-test

# 5. 吞吐量测试
echo ""
echo "=== 吞吐量测试 (ab) ==="

WASM_URL=$(kubectl get svc wasm-http -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
CONTAINER_URL=$(kubectl get svc container-http -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Wasm吞吐量:"
ab -n 10000 -c 100 http://$WASM_URL/ | grep "Requests per second"

echo "Container吞吐量:"
ab -n 10000 -c 100 http://$CONTAINER_URL/ | grep "Requests per second"

# 6. 延迟测试
echo ""
echo "=== 延迟测试 (wrk) ==="

echo "Wasm延迟:"
wrk -t4 -c100 -d30s http://$WASM_URL/ | grep -E "(Latency|Requests/sec)"

echo "Container延迟:"
wrk -t4 -c100 -d30s http://$CONTAINER_URL/ | grep -E "(Latency|Requests/sec)"

# 7. 清理
kubectl delete pod wasm-memory-test container-memory-test

echo ""
echo "=== 基准测试完成 ==="
```

---

## 10. 未来趋势

### 2025-2026技术路线图

```yaml
Wasm_Future_2025_2026:
  标准化进展:
    WASI_Preview_3:
      时间: 2025 H2
      特性:
        - 异步I/O完善
        - 流式处理
        - 组件链接
        - 更多系统API
    
    Component_Model_1.0:
      时间: 2025 Q4
      特性:
        - 跨语言组件
        - 标准化接口
        - 动态链接
        - 包管理
    
    Wasm_GC:
      时间: 2025-2026
      特性:
        - 垃圾回收支持
        - 语言互操作性
        - 性能提升
  
  云原生集成:
    Kubernetes:
      - Wasm作为一等公民
      - 原生RuntimeClass
      - 更好的调度支持
      - 资源模型优化
    
    Service_Mesh:
      - Istio Ambient + Wasm
      - Envoy Wasm插件生态
      - 动态配置
      - 热更新
    
    Serverless:
      - Knative原生支持
      - OpenFaaS优化
      - AWS Lambda Wasm
      - Cloudflare Workers成熟
  
  性能提升:
    硬件加速:
      - Wasm专用指令集
      - GPU支持完善
      - SIMD优化
      - 多核并行
    
    编译优化:
      - 更快的AOT编译
      - Profile-guided优化
      - 自适应优化
      - 智能缓存
  
  应用领域扩展:
    AI_ML:
      - TensorFlow Lite Wasm
      - ONNX Runtime Wasm
      - 边缘AI推理
      - 联邦学习
    
    边缘计算:
      - 5G MEC集成
      - IoT设备支持
      - CDN边缘节点
      - 智能网关
    
    多租户SaaS:
      - 用户自定义逻辑
      - 安全插件系统
      - 低成本隔离
      - 高密度部署
```

### 行业采用趋势

```yaml
Industry_Adoption_2025:
  早期采用者:
    Cloudflare_Workers:
      状态: 生产大规模使用
      场景: 边缘计算、CDN
      规模: 数百万Wasm函数/天
    
    Fastly_Compute_Edge:
      状态: 生产使用
      场景: 边缘计算、安全
      特点: Wasmtime运行时
    
    Shopify:
      状态: 生产试点
      场景: 商家自定义脚本
      优势: 安全隔离
  
  云厂商支持:
    AWS:
      - Lambda Wasm支持 (Roadmap)
      - ECS Wasm运行时
      - CloudFront边缘
    
    Google_Cloud:
      - Cloud Run Wasm
      - GKE Wasm RuntimeClass
      - CDN边缘函数
    
    Azure:
      - Container Apps Wasm
      - AKS Wasm支持
      - CDN Functions
  
  开源项目:
    Kubernetes:
      - 原生Wasm支持提案
      - RuntimeClass成熟
      - 调度器优化
    
    Istio_Envoy:
      - Wasm插件生态
      - Ambient模式集成
      - 性能优化
    
    Knative:
      - Wasm函数支持
      - 快速冷启动
      - 高密度部署
```

---

## 相关文档

### 本模块文档

- [AI/ML工作负载](02_AI_ML云原生工作负载.md) - Kubernetes GPU调度
- [边缘计算](03_边缘计算与K3s.md) - K3s、KubeEdge
- [FinOps成本优化](04_FinOps云原生成本优化.md) - Kubecost、OpenCost
- [安全新标准](05_2025安全新标准.md) - Sigstore、GUAC、VEX

### 相关模块

- [容器存储](../04_容器存储/README.md) - Rook、Longhorn、OpenEBS
- [服务网格](../05_服务网格/README.md) - Istio Ambient、Linkerd
- [Kubernetes部署](../02_Kubernetes部署/README.md) - K8s 1.28+

### 外部资源

- [WebAssembly官网](https://webassembly.org/)
- [WASI](https://wasi.dev/)
- [WasmEdge](https://wasmedge.org/)
- [containerd runwasi](https://github.com/containerd/runwasi)
- [Docker + Wasm](https://docs.docker.com/desktop/wasm/)
- [Kubernetes Wasm](https://kubernetes.io/blog/2023/03/31/wasm-and-kubernetes/)

---

**文档版本**: v1.0  
**更新日期**: 2025-10-20  
**状态**: ✅ **WebAssembly容器化技术 - 2025最新标准对齐**
