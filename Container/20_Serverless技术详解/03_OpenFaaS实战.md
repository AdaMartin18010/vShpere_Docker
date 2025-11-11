# 03 - OpenFaaS实战

**作者**: 云原生专家团队
**创建日期**: 2025-10-19
**最后更新**: 2025-10-19
**版本**: v1.0

---

## 📋 本章导航

- [03 - OpenFaaS实战](#03---openfaas实战)
  - [📋 本章导航](#-本章导航)
  - [1. OpenFaaS概述](#1-openfaas概述)
    - [1.1 什么是OpenFaaS](#11-什么是openfaas)
    - [1.2 核心特性](#12-核心特性)
    - [1.3 架构原理](#13-架构原理)
    - [1.4 vs Knative对比](#14-vs-knative对比)
  - [2. OpenFaaS快速部署](#2-openfaas快速部署)
    - [2.1 Docker Swarm部署](#21-docker-swarm部署)
    - [2.2 Kubernetes部署](#22-kubernetes部署)
    - [2.3 faasd单机部署](#23-faasd单机部署)
    - [2.4 验证安装](#24-验证安装)
  - [3. faas-cli工具详解](#3-faas-cli工具详解)
    - [3.1 安装faas-cli](#31-安装faas-cli)
    - [3.2 基础命令](#32-基础命令)
    - [3.3 函数生命周期](#33-函数生命周期)
    - [3.4 Secret管理](#34-secret管理)
  - [4. 多语言函数开发](#4-多语言函数开发)
    - [4.1 Python函数](#41-python函数)
    - [4.2 Go函数](#42-go函数)
    - [4.3 Node.js函数](#43-nodejs函数)
    - [4.4 自定义模板](#44-自定义模板)
  - [5. 高级特性](#5-高级特性)
    - [5.1 异步调用](#51-异步调用)
    - [5.2 自动扩缩容](#52-自动扩缩容)
    - [5.3 函数间调用](#53-函数间调用)
    - [5.4 NATS Streaming](#54-nats-streaming)
  - [6. 监控与日志](#6-监控与日志)
    - [6.1 Prometheus集成](#61-prometheus集成)
    - [6.2 Grafana Dashboard](#62-grafana-dashboard)
    - [6.3 日志查看](#63-日志查看)
    - [6.4 告警配置](#64-告警配置)
  - [7. CI/CD集成](#7-cicd集成)
    - [7.1 GitHub Actions](#71-github-actions)
    - [7.2 GitLab CI](#72-gitlab-ci)
    - [7.3 Jenkins Pipeline](#73-jenkins-pipeline)
    - [7.4 ArgoCD GitOps](#74-argocd-gitops)
  - [8. 实战案例](#8-实战案例)
    - [8.1 图片处理函数](#81-图片处理函数)
    - [8.2 Webhook处理](#82-webhook处理)
    - [8.3 数据ETL](#83-数据etl)
    - [8.4 微服务编排](#84-微服务编排)
  - [9. 总结](#9-总结)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 1. OpenFaaS概述

### 1.1 什么是OpenFaaS

**OpenFaaS (Functions as a Service)** 是一个开源Serverless框架，可以在Docker Swarm或Kubernetes上运行。

```yaml
OpenFaaS定位:
  - 开源Serverless平台
  - 简单易用
  - 支持任何语言
  - 容器原生

核心理念:
  "Functions as a Service, made simple"
  - 让Serverless开发变得简单
  - 无需关心基础设施
  - 专注业务逻辑

创始人:
  - Alex Ellis (2016年创建)
  - 活跃的开源社区
  - 企业级支持 (OpenFaaS Pro)

适用场景:
  - 快速原型开发
  - 事件驱动应用
  - API后端
  - Webhook处理
  - 定时任务
  - 微服务

优势:
  ✅ 简单易用 (10分钟上手)
  ✅ 多语言支持
  ✅ 强大CLI工具
  ✅ 活跃社区
  ✅ 企业级功能 (Pro版本)

劣势:
  ❌ 功能不如Knative丰富
  ❌ 事件驱动能力弱于Knative Eventing
  ❌ 企业采用不如云厂商平台广泛
```

---

### 1.2 核心特性

```yaml
核心特性:

1. 多语言支持:
   官方模板:
     - Python (2.7, 3.x)
     - Go
     - Node.js (12, 14, 16, 18)
     - Java
     - Ruby
     - PHP
     - C#
     - Rust

   社区模板:
     - R
     - Crystal
     - Elixir
     - Haskell
     - ...更多

2. 自动扩缩容:
   - 基于RPS (Requests Per Second)
   - 基于CPU/内存
   - 最小副本数: 1 (默认)
   - 最大副本数: 20 (默认)
   - 可配置

3. 简单部署:
   - Docker Swarm (单机)
   - Kubernetes (生产)
   - faasd (轻量级)
   - Docker Compose (开发)

4. 强大CLI:
   - faas-cli
   - 创建/构建/部署/调用
   - 本地开发支持
   - 模板管理

5. 监控内置:
   - Prometheus指标
   - Grafana Dashboard
   - 日志聚合
   - 告警

6. 异步调用:
   - NATS Streaming
   - 队列支持
   - 回调机制
   - 重试策略

7. Secret管理:
   - Kubernetes Secrets
   - Docker Secrets
   - 环境变量
   - 安全挂载

8. 网关功能:
   - API Gateway
   - 认证/鉴权
   - 限流
   - 路由
```

---

### 1.3 架构原理

**OpenFaaS架构图**:

```text
┌──────────────────────────────────────────────────────────────┐
│                      OpenFaaS架构                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  用户/Client                                                  │
│      ↓                                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           API Gateway (8080)                        │    │
│  │  - REST API                                         │    │
│  │  - 认证/鉴权                                         │    │
│  │  - 限流                                             │    │
│  │  - 路由                                             │    │
│  └─────────────────────────────────────────────────────┘    │
│      ↓                                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Provider (K8s/Swarm/faasd)                │    │
│  │  - 函数部署                                          │    │
│  │  - 扩缩容                                            │    │
│  │  - 健康检查                                          │    │
│  └─────────────────────────────────────────────────────┘    │
│      ↓                                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Functions (容器)                           │    │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐           │    │
│  │  │ Fn1  │  │ Fn2  │  │ Fn3  │  │ Fn4  │           │    │
│  │  │Python│  │ Go   │  │Node.js│ │Java  │           │    │
│  │  └──────┘  └──────┘  └──────┘  └──────┘           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Watchdog (容器内)                          │    │
│  │  - HTTP → 函数调用                                   │    │
│  │  - 标准输入/输出                                     │    │
│  │  - 超时控制                                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Queue Worker (可选)                        │    │
│  │  - NATS Streaming                                    │    │
│  │  - 异步调用                                          │    │
│  │  - 重试机制                                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Prometheus (监控)                          │    │
│  │  - 函数指标                                          │    │
│  │  - 调用统计                                          │    │
│  │  - 告警                                              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**核心组件**:

```yaml
1. Gateway:
   作用:
     - API入口
     - 路由请求到函数
     - 认证/鉴权
     - 指标收集

   端口:
     - 8080: HTTP API
     - 8082: Prometheus指标

2. Provider:
   作用:
     - 抽象层
     - 适配不同平台 (K8s/Swarm/faasd)
     - 函数CRUD
     - 扩缩容

   实现:
     - faas-netes (Kubernetes)
     - faas-swarm (Docker Swarm)
     - faasd (containerd)

3. Watchdog:
   作用:
     - 函数容器内代理
     - HTTP请求 → 函数调用
     - 处理标准输入/输出
     - 超时控制

   类型:
     - Classic Watchdog (HTTP → stdin/stdout)
     - of-watchdog (HTTP → HTTP)

4. Queue Worker:
   作用:
     - 异步调用
     - NATS Streaming集成
     - 重试机制
     - 回调

   可选: 默认不启用

5. Prometheus:
   作用:
     - 指标收集
     - 监控
     - 告警

   内置: 默认部署
```

**请求流程**:

```yaml
同步调用:
  Client
    ↓ POST /function/hello
  Gateway
    ↓ HTTP转发
  Function Pod (Watchdog)
    ↓ 调用函数
  函数代码执行
    ↓ 返回结果
  Gateway
    ↓ 返回给Client
  Client收到响应

异步调用:
  Client
    ↓ POST /async-function/hello
  Gateway
    ↓ 发送到NATS
  NATS Queue
    ↓
  Queue Worker
    ↓ 调用函数
  Function Pod
    ↓ 执行
  (可选) 回调URL
```

---

### 1.4 vs Knative对比

```yaml
对比维度          OpenFaaS            Knative
────────────────────────────────────────────────────────
复杂度            简单 ⭐⭐            复杂 ⭐⭐⭐⭐
学习曲线          低 (10分钟)         高 (1-2天)
部署难度          低                  中
功能丰富度        中等                高
事件驱动          基础 (NATS)         强大 (Eventing)
流量管理          基础                高级 (蓝绿/金丝雀)
扩缩容            基础 (HPA)          高级 (KPA/Scale to Zero)
多语言支持        ✅ 优秀              ✅ 优秀
CLI工具           ✅ faas-cli强大      ✅ kn
监控              ✅ Prometheus内置    ✅ 需额外配置
社区              活跃                活跃
企业采用          中等                高
CNCF项目          ❌                  ✅ 孵化

适用场景:
  OpenFaaS:
    ✅ 快速原型
    ✅ 简单应用
    ✅ 学习Serverless
    ✅ 小团队
    ✅ 预算有限

  Knative:
    ✅ 企业级应用
    ✅ 复杂事件驱动
    ✅ 高级流量管理
    ✅ 大团队
    ✅ 需要完整控制

总结:
  OpenFaaS: 简单易用，快速上手
  Knative: 功能强大，企业级
```

---

## 2. OpenFaaS快速部署

### 2.1 Docker Swarm部署

**适用场景**: 单机开发/测试

```bash
# 1. 初始化Docker Swarm
docker swarm init

# 2. 克隆OpenFaaS仓库
git clone https://github.com/openfaas/faas
cd faas

# 3. 部署OpenFaaS Stack
./deploy_stack.sh

# 输出:
# Deploying stack: func
# Creating network func_functions
# Creating service func_gateway
# Creating service func_prometheus
# Creating service func_alertmanager
# Creating service func_nats
# Creating service func_queue-worker

# 4. 等待服务就绪 (约1-2分钟)
docker service ls

# 输出:
# ID            NAME                  MODE        REPLICAS   IMAGE
# xxx           func_gateway          replicated  1/1        openfaas/gateway:latest
# xxx           func_prometheus       replicated  1/1        prom/prometheus:latest
# xxx           func_queue-worker     replicated  1/1        openfaas/queue-worker:latest
# xxx           func_nats             replicated  1/1        nats-streaming:latest

# 5. 获取Gateway密码
cat ~/password.txt
# 或自定义:
echo "admin" | docker secret create basic-auth-user -
echo "MyPassword123" | docker secret create basic-auth-password -

# 6. 访问UI
open http://127.0.0.1:8080
# 用户名: admin
# 密码: (步骤5的密码)

# 7. 登录CLI
export OPENFAAS_URL=http://127.0.0.1:8080
echo -n "MyPassword123" | faas-cli login --username admin --password-stdin

# 8. (可选) 卸载
docker stack rm func
docker swarm leave --force
```

---

### 2.2 Kubernetes部署

**适用场景**: 生产环境 (推荐)

```bash
# 前置条件: Kubernetes 1.22+
kubectl version --short

# 方式1: arkade (推荐, 最简单)
# 安装arkade
curl -sLS https://get.arkade.dev | sudo sh

# 部署OpenFaaS
arkade install openfaas

# 输出:
# = OpenFaaS has been installed.                                      =
#
#   # Get the faas-cli
#   curl -SLsf https://cli.openfaas.com | sudo sh
#
#   # Forward the gateway to your machine
#   kubectl rollout status -n openfaas deploy/gateway
#   kubectl port-forward -n openfaas svc/gateway 8080:8080 &
#
#   # If basic auth is enabled, you can now log into your gateway:
#   PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
#   echo -n $PASSWORD | faas-cli login --username admin --password-stdin
#
#   faas-cli store deploy figlet
#   faas-cli list
#
# # To remove faas:
#   arkade uninstall openfaas

# 按照输出提示操作
```

```bash
# 方式2: Helm (更多自定义)
# 添加Helm仓库
helm repo add openfaas https://openfaas.github.io/faas-netes/
helm repo update

# 创建命名空间
kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml

# 输出:
# namespace/openfaas created
# namespace/openfaas-fn created

# 生成随机密码
PASSWORD=$(head -c 12 /dev/urandom | shasum | cut -d' ' -f1)
echo $PASSWORD  # 保存密码

# 创建Secret
kubectl -n openfaas create secret generic basic-auth \
  --from-literal=basic-auth-user=admin \
  --from-literal=basic-auth-password="$PASSWORD"

# 安装OpenFaaS
helm upgrade openfaas \
  --install openfaas/openfaas \
  --namespace openfaas \
  --set functionNamespace=openfaas-fn \
  --set generateBasicAuth=false

# 输出:
# Release "openfaas" has been installed. Happy Helming!
# NAME: openfaas
# NAMESPACE: openfaas
# STATUS: deployed

# 验证安装
kubectl -n openfaas get deployments -l "release=openfaas, app=openfaas"

# 输出:
# NAME                READY   UP-TO-DATE   AVAILABLE   AGE
# alertmanager        1/1     1            1           1m
# gateway             1/1     1            1           1m
# nats                1/1     1            1           1m
# prometheus          1/1     1            1           1m
# queue-worker        1/1     1            1           1m

# 端口转发 (本地访问)
kubectl port-forward -n openfaas svc/gateway 8080:8080 &

# 或配置Ingress (生产)
```

**Ingress配置**:

```yaml
# openfaas-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openfaas-gateway
  namespace: openfaas
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - openfaas.example.com
    secretName: openfaas-tls
  rules:
  - host: openfaas.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: gateway
            port:
              number: 8080

# 应用
kubectl apply -f openfaas-ingress.yaml
```

---

### 2.3 faasd单机部署

**faasd**: 轻量级OpenFaaS，使用containerd代替Kubernetes。

```bash
# 适用场景:
# - 单机部署
# - 边缘设备
# - 树莓派
# - 低资源环境

# 安装faasd (Ubuntu/Debian)
git clone https://github.com/openfaas/faasd
cd faasd

# 运行安装脚本
./hack/install.sh

# 输出:
# [OK] faasd installed
# [OK] Basic auth configured
#
# Login with:
#   faas-cli login --gateway http://127.0.0.1:8080 --password $(sudo cat /var/lib/faasd/secrets/basic-auth-password)
#
# Gateway: http://127.0.0.1:8080
# Username: admin
# Password: (stored in /var/lib/faasd/secrets/basic-auth-password)

# 查看密码
sudo cat /var/lib/faasd/secrets/basic-auth-password

# 登录
export PASSWORD=$(sudo cat /var/lib/faasd/secrets/basic-auth-password)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin

# 验证
faas-cli list

# 管理faasd服务
sudo systemctl status faasd
sudo systemctl start faasd
sudo systemctl stop faasd
sudo systemctl restart faasd

# 卸载
sudo systemctl stop faasd
sudo rm -rf /var/lib/faasd
```

---

### 2.4 验证安装

```bash
# 1. 检查Gateway
kubectl -n openfaas get pods

# 输出:
# NAME                               READY   STATUS    RESTARTS   AGE
# alertmanager-xxx                   1/1     Running   0          2m
# gateway-xxx                        2/2     Running   0          2m
# nats-xxx                           1/1     Running   0          2m
# prometheus-xxx                     1/1     Running   0          2m
# queue-worker-xxx                   1/1     Running   0          2m

# 2. 获取密码并登录
PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin

# 输出:
# Calling the OpenFaaS server to validate the credentials...
# credentials saved for admin http://127.0.0.1:8080

# 3. 访问UI
kubectl port-forward -n openfaas svc/gateway 8080:8080

# 浏览器打开: http://localhost:8080
# 用户名: admin
# 密码: $PASSWORD

# 4. 部署测试函数
faas-cli store deploy figlet
# 或
faas-cli store deploy nodeinfo

# 5. 列出函数
faas-cli list

# 输出:
# Function    Invocations    Replicas
# figlet      0              1
# nodeinfo    0              1

# 6. 测试调用
echo "OpenFaaS" | faas-cli invoke figlet

# 输出:
#   ___                   _____           ____
#  / _ \ _ __   ___ _ __ |  ___|_ _  __ _/ ___|
# | | | | '_ \ / _ \ '_ \| |_ / _` |/ _` \___ \
# | |_| | |_) |  __/ | | |  _| (_| | (_| |___) |
#  \___/| .__/ \___|_| |_|_|  \__,_|\__,_|____/
#       |_|

# 7. 查看函数详情
faas-cli describe figlet

# 输出:
# Name:                figlet
# Status:              Ready
# Replicas:            1
# Available replicas:  1
# Invocations:         1
# Image:               functions/figlet:latest
# Function process:
# URL:                 http://127.0.0.1:8080/function/figlet
# Async URL:           http://127.0.0.1:8080/async-function/figlet
# Labels:
# Annotations:
```

---

## 3. faas-cli工具详解

### 3.1 安装faas-cli

```bash
# Linux/macOS
curl -sSL https://cli.openfaas.com | sudo sh

# macOS (Homebrew)
brew install faas-cli

# Windows (Git Bash)
curl -sSL https://cli.openfaas.com | sh

# 验证安装
faas-cli version

# 输出:
#   ___                   _____           ____
#  / _ \ _ __   ___ _ __ |  ___|_ _  __ _/ ___|
# | | | | '_ \ / _ \ '_ \| |_ / _` |/ _` \___ \
# | |_| | |_) |  __/ | | |  _| (_| | (_| |___) |
#  \___/| .__/ \___|_| |_|_|  \__,_|\__,_|____/
#       |_|
#
# CLI:
#  commit:  abc123
#  version: 0.16.20

# 配置Gateway URL (永久)
echo "export OPENFAAS_URL=http://127.0.0.1:8080" >> ~/.bashrc
source ~/.bashrc

# 或临时
export OPENFAAS_URL=http://127.0.0.1:8080
```

---

### 3.2 基础命令

```bash
# 1. 登录
echo -n "$PASSWORD" | faas-cli login --username admin --password-stdin

# 2. 查看帮助
faas-cli --help

# 主要命令:
#   login       - 登录Gateway
#   list        - 列出已部署函数
#   store       - 函数商店
#   deploy      - 部署函数
#   remove      - 删除函数
#   invoke      - 调用函数
#   build       - 构建函数镜像
#   push        - 推送镜像
#   up          - build + push + deploy
#   logs        - 查看日志
#   describe    - 查看函数详情
#   new         - 创建新函数
#   template    - 模板管理
#   secret      - Secret管理
#   namespace   - 命名空间管理

# 3. 函数商店 (预构建函数)
faas-cli store list

# 输出 (部分):
# FUNCTION                DESCRIPTION
# figlet                  Generate ASCII logos with the figlet CLI
# nodeinfo                Get info about the architecture
# env                     Print environment variables
# alpine                  Alpine Linux and curl
# sleep                   Sleep for N seconds
# cows                    ASCII cows
# wordcount               Count words in request with Python
# markdown                Markdown renderer using Python-Markdown
# youtubedl               Download YouTube videos as a function
# mquery                  Query Mongo database

# 4. 部署商店函数
faas-cli store deploy figlet

# 5. 列出已部署函数
faas-cli list

# 6. 调用函数
echo "Hello" | faas-cli invoke figlet

# 或使用curl
curl http://127.0.0.1:8080/function/figlet -d "Hello"

# 7. 查看函数详情
faas-cli describe figlet

# 8. 查看日志
faas-cli logs figlet

# 9. 删除函数
faas-cli remove figlet
```

---

### 3.3 函数生命周期

**创建新函数**:

```bash
# 1. 查看可用模板
faas-cli template store list

# 输出 (部分):
# NAME                     SOURCE             DESCRIPTION
# python3                  openfaas           Classic Python 3 template
# python3-http             openfaas           Python 3 with HTTP
# golang-http              openfaas           Golang HTTP template
# node18                   openfaas           Node.js 18 template
# dockerfile               openfaas           Dockerfile template
# ruby-http                openfaas           Ruby HTTP template
# java11                   openfaas           Java 11 template
# csharp                   openfaas           C# template

# 2. 拉取模板
faas-cli template store pull python3-http

# 3. 创建新函数
faas-cli new hello-python --lang python3-http --prefix <your-docker-hub-username>

# 输出:
# Folder: hello-python created.
#   ___                   _____           ____
#  / _ \ _ __   ___ _ __ |  ___|_ _  __ _/ ___|
# | | | | '_ \ / _ \ '_ \| |_ / _` |/ _` \___ \
# | |_| | |_) |  __/ | | |  _| (_| | (_| |___) |
#  \___/| .__/ \___|_| |_|_|  \__,_|\__,_|____/
#       |_|
#
# Function created in folder: hello-python
# Stack file written: hello-python.yml

# 目录结构:
# .
# ├── hello-python/
# │   ├── handler.py        # 函数代码
# │   └── requirements.txt  # Python依赖
# ├── hello-python.yml      # Stack配置
# └── template/             # 模板文件
#     └── python3-http/

# 4. 编辑函数代码
cat > hello-python/handler.py <<EOF
def handle(req):
    """处理请求"""
    name = req if req else "World"
    return f"Hello, {name}!"
EOF

# 5. (可选) 添加依赖
echo "requests==2.31.0" >> hello-python/requirements.txt

# 6. 构建函数
faas-cli build -f hello-python.yml

# 输出:
# [0] > Building hello-python.
# Clearing temporary build folder: ./build/hello-python/
# Preparing: ./hello-python/ build/hello-python/function
# Building: <username>/hello-python:latest with python3-http template. Please wait..
# ...
# Successfully tagged <username>/hello-python:latest
# Image: <username>/hello-python:latest built.

# 7. 推送镜像
faas-cli push -f hello-python.yml

# 8. 部署函数
faas-cli deploy -f hello-python.yml

# 9. 或一键: build + push + deploy
faas-cli up -f hello-python.yml

# 10. 测试
echo "OpenFaaS" | faas-cli invoke hello-python
# 输出: Hello, OpenFaaS!

# 11. 更新函数 (修改代码后)
faas-cli up -f hello-python.yml

# 12. 删除函数
faas-cli remove -f hello-python.yml
```

**stack.yml配置详解**:

```yaml
# hello-python.yml
version: 1.0
provider:
  name: openfaas
  gateway: http://127.0.0.1:8080  # Gateway地址

functions:
  hello-python:
    lang: python3-http             # 模板语言
    handler: ./hello-python        # 函数代码目录
    image: <username>/hello-python:latest  # 镜像名

    # 环境变量
    environment:
      write_timeout: 10s
      read_timeout: 10s
      exec_timeout: 10s

      # 自定义环境变量
      DB_HOST: postgres.default.svc.cluster.local
      API_KEY: ${API_KEY}  # 从环境变量读取

    # 资源限制
    limits:
      memory: 128Mi
      cpu: 100m
    requests:
      memory: 64Mi
      cpu: 50m

    # 标签
    labels:
      com.openfaas.scale.min: "1"
      com.openfaas.scale.max: "5"
      com.openfaas.scale.factor: "20"

      # 自定义标签
      app: hello-python
      version: v1

    # 注解
    annotations:
      topic: "faas-request"

    # Secret挂载
    secrets:
    - db-password
    - api-key

    # 约束 (Kubernetes nodeSelector)
    constraints:
    - "kubernetes.io/arch=amd64"
```

---

### 3.4 Secret管理

```bash
# 1. 创建Secret (Kubernetes)
kubectl -n openfaas-fn create secret generic db-password \
  --from-literal=db-password="MySecurePassword123"

# 或从文件
echo -n "MySecurePassword123" > password.txt
kubectl -n openfaas-fn create secret generic db-password \
  --from-file=db-password=password.txt
rm password.txt

# 2. 创建Secret (faas-cli)
faas-cli secret create db-password --from-literal="MySecurePassword123"

# 或从文件
echo -n "MySecurePassword123" | faas-cli secret create db-password

# 3. 列出Secrets
faas-cli secret list

# 4. 在函数中使用Secret
# stack.yml
functions:
  my-function:
    # ...
    secrets:
    - db-password

# 5. 函数代码中读取Secret
# Python示例
def handle(req):
    # Secret挂载在 /var/openfaas/secrets/<secret-name>
    with open('/var/openfaas/secrets/db-password', 'r') as f:
        password = f.read()

    return f"Password length: {len(password)}"

# 6. 删除Secret
faas-cli secret remove db-password
```

---

## 4. 多语言函数开发

### 4.1 Python函数

**示例1: HTTP REST API**:

```bash
# 创建函数
faas-cli new python-api --lang python3-http --prefix <username>
```

```python
# python-api/handler.py
import json

def handle(req):
    """
    处理HTTP请求
    req: 请求体 (string)
    返回: HTTP响应
    """
    try:
        # 解析JSON
        data = json.loads(req) if req else {}
        name = data.get('name', 'World')
        age = data.get('age', 0)

        # 业务逻辑
        response = {
            'message': f'Hello, {name}!',
            'age': age,
            'adult': age >= 18
        }

        return json.dumps(response)

    except Exception as e:
        error = {
            'error': str(e)
        }
        return json.dumps(error)
```

```txt
# python-api/requirements.txt
# 添加依赖
requests==2.31.0
```

```bash
# 部署
faas-cli up -f python-api.yml

# 测试
curl -X POST http://127.0.0.1:8080/function/python-api \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","age":25}'

# 输出:
# {"message": "Hello, Alice!", "age": 25, "adult": true}
```

**示例2: 图片处理**:

```python
# image-processor/handler.py
from PIL import Image
import io
import base64

def handle(req):
    """处理图片 - 转为灰度"""
    try:
        # 解码Base64图片
        image_data = base64.b64decode(req)
        image = Image.open(io.BytesIO(image_data))

        # 转为灰度
        grayscale = image.convert('L')

        # 编码为Base64
        buffer = io.BytesIO()
        grayscale.save(buffer, format='PNG')
        result = base64.b64encode(buffer.getvalue()).decode()

        return result

    except Exception as e:
        return f"Error: {str(e)}"
```

```txt
# image-processor/requirements.txt
Pillow==10.0.0
```

---

### 4.2 Go函数

**示例1: Hello World**:

```bash
# 创建函数
faas-cli new hello-go --lang golang-http --prefix <username>
```

```go
// hello-go/handler.go
package function

import (
    "encoding/json"
    "fmt"
    "net/http"
)

type Request struct {
    Name string `json:"name"`
}

type Response struct {
    Message string `json:"message"`
}

// Handle a function invocation
func Handle(w http.ResponseWriter, r *http.Request) {
    var req Request

    // 解析JSON
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        w.WriteHeader(http.StatusBadRequest)
        w.Write([]byte(fmt.Sprintf("Error parsing request: %v", err)))
        return
    }

    name := req.Name
    if name == "" {
        name = "World"
    }

    // 构建响应
    resp := Response{
        Message: fmt.Sprintf("Hello, %s!", name),
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(resp)
}
```

```bash
# 部署
faas-cli up -f hello-go.yml

# 测试
curl -X POST http://127.0.0.1:8080/function/hello-go \
  -H "Content-Type: application/json" \
  -d '{"name":"Go"}'
```

**示例2: JSON API**:

```go
// json-api/handler.go
package function

import (
    "encoding/json"
    "fmt"
    "net/http"
    "time"
)

type User struct {
    ID        int       `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}

func Handle(w http.ResponseWriter, r *http.Request) {
    // 模拟数据库查询
    users := []User{
        {ID: 1, Name: "Alice", Email: "alice@example.com", CreatedAt: time.Now()},
        {ID: 2, Name: "Bob", Email: "bob@example.com", CreatedAt: time.Now()},
    }

    w.Header().Set("Content-Type", "application/json")

    if err := json.NewEncoder(w).Encode(users); err != nil {
        w.WriteHeader(http.StatusInternalServerError)
        w.Write([]byte(fmt.Sprintf("Error: %v", err)))
    }
}
```

---

### 4.3 Node.js函数

**示例1: Express风格API**:

```bash
# 创建函数
faas-cli new node-api --lang node18 --prefix <username>
```

```javascript
// node-api/handler.js
'use strict'

module.exports = async (event, context) => {
    try {
        // 解析请求
        const body = JSON.parse(event.body || '{}')
        const name = body.name || 'World'
        const timestamp = new Date().toISOString()

        // 业务逻辑
        const response = {
            message: `Hello, ${name}!`,
            timestamp: timestamp,
            headers: event.headers
        }

        return context
            .status(200)
            .headers({ 'Content-Type': 'application/json' })
            .succeed(response)

    } catch (error) {
        return context
            .status(500)
            .succeed({ error: error.message })
    }
}
```

```json
{
  "name": "node-api",
  "version": "1.0.0",
  "description": "",
  "main": "handler.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "dependencies": {
    "axios": "^1.4.0"
  }
}
```

**示例2: HTTP请求**:

```javascript
// fetch-api/handler.js
'use strict'

const axios = require('axios')

module.exports = async (event, context) => {
    try {
        const body = JSON.parse(event.body || '{}')
        const url = body.url || 'https://api.github.com'

        // 发送HTTP请求
        const response = await axios.get(url)

        return context
            .status(200)
            .succeed({
                status: response.status,
                data: response.data
            })

    } catch (error) {
        return context
            .status(500)
            .succeed({ error: error.message })
    }
}
```

---

### 4.4 自定义模板

```bash
# 1. 创建模板目录结构
mkdir -p template/custom-python/
cd template/custom-python/

# 2. 创建template.yml
cat > template.yml <<EOF
language: custom-python
fprocess: python3 index.py
EOF

# 3. 创建Dockerfile
cat > Dockerfile <<EOF
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装of-watchdog
ADD https://github.com/openfaas/of-watchdog/releases/download/0.9.11/of-watchdog /usr/bin/
RUN chmod +x /usr/bin/of-watchdog

WORKDIR /home/app

# 复制函数代码
COPY index.py .
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置非root用户
RUN addgroup --system app && adduser --system --ingroup app app
RUN chown -R app:app /home/app
USER app

# Watchdog配置
ENV fprocess="python3 index.py"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["of-watchdog"]
EOF

# 4. 创建index.py模板
cat > index.py <<EOF
from flask import Flask, request, jsonify
import sys

app = Flask(__name__)

# 导入用户函数
sys.path.append('./function')
from handler import handle

@app.route('/', methods=['POST', 'GET'])
def main():
    req_data = request.get_data(as_text=True)
    result = handle(req_data)
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# 5. 创建function目录
mkdir function
cat > function/handler.py <<EOF
def handle(req):
    """处理请求"""
    return f"You said: {req}"
EOF

# 6. 使用自定义模板
cd ../..  # 回到项目根目录
faas-cli new my-function --lang custom-python --prefix <username>

# 7. 构建和部署
faas-cli up -f my-function.yml
```

---

## 5. 高级特性

### 5.1 异步调用

```bash
# 1. 同步调用 (默认)
curl -X POST http://127.0.0.1:8080/function/nodeinfo \
  -d "sync request"

# 等待响应

# 2. 异步调用
curl -X POST http://127.0.0.1:8080/async-function/nodeinfo \
  -d "async request"

# 立即返回202 Accepted

# 3. 异步调用 + 回调
curl -X POST http://127.0.0.1:8080/async-function/nodeinfo \
  -H "X-Callback-Url: http://example.com/callback" \
  -d "async request with callback"

# 函数执行完成后，会POST结果到回调URL

# 4. 查看异步队列状态
kubectl -n openfaas logs deploy/queue-worker -f
```

**异步处理流程**:

```yaml
Client
  ↓ POST /async-function/nodeinfo
Gateway
  ↓ 发送到NATS Queue
NATS Streaming
  ↓
Queue Worker (订阅)
  ↓ 调用函数
Function (nodeinfo)
  ↓ 执行并返回结果
Queue Worker
  ↓ (如果有X-Callback-Url)
  ↓ POST结果到回调URL
Callback URL
```

**配置Queue Worker**:

```yaml
# Helm values.yaml
queueWorker:
  replicas: 3
  ackWait: 60s
  maxInflight: 10

  # NATS配置
  nats:
    channel: "faas-request"
    clusterName: "faas-cluster"
```

---

### 5.2 自动扩缩容

```yaml
# stack.yml
functions:
  my-function:
    # ...
    labels:
      # 最小副本数
      com.openfaas.scale.min: "1"

      # 最大副本数
      com.openfaas.scale.max: "10"

      # 扩容因子 (RPS阈值)
      # 例如: 每个Pod处理20个请求/秒
      # 当总RPS达到20时，扩容到2个Pod
      com.openfaas.scale.factor: "20"

      # 缩容类型
      com.openfaas.scale.type: "rps"  # 基于RPS
      # 或: "capacity" (基于CPU/内存)

      # 缩容延迟 (秒)
      com.openfaas.scale.zero-duration: "5m"
```

**自定义HPA (Kubernetes)**:

```yaml
# custom-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-function
  namespace: openfaas-fn
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-function
  minReplicas: 1
  maxReplicas: 20
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
      stabilizationWindowSeconds: 300
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
        value: 4
        periodSeconds: 30
      selectPolicy: Max
```

---

### 5.3 函数间调用

```python
# caller-function/handler.py
import requests
import os

def handle(req):
    """调用其他函数"""

    # OpenFaaS Gateway地址
    gateway_url = os.getenv("gateway_url", "http://gateway.openfaas:8080")

    # 调用另一个函数
    function_name = "nodeinfo"
    url = f"{gateway_url}/function/{function_name}"

    try:
        response = requests.post(url, data="Hello from caller")

        return {
            'status': response.status_code,
            'result': response.text
        }

    except Exception as e:
        return {'error': str(e)}
```

**服务发现**:

```yaml
# 在Kubernetes中，函数可通过Service名称访问
# 格式: <function-name>.<namespace>.svc.cluster.local

# 例如:
# http://nodeinfo.openfaas-fn.svc.cluster.local:8080

# 或通过Gateway:
# http://gateway.openfaas:8080/function/nodeinfo
```

---

### 5.4 NATS Streaming

```bash
# 1. 查看NATS连接
kubectl -n openfaas get svc nats

# 2. 发布消息到NATS (触发函数)
# 安装NATS CLI
go install github.com/nats-io/natscli/nats@latest

# 发布消息
nats pub faas-request '{"function":"nodeinfo","data":"test"}'

# 3. 订阅NATS主题 (查看消息)
nats sub faas-request

# 4. 配置函数订阅NATS
# stack.yml
functions:
  nats-subscriber:
    # ...
    annotations:
      topic: "my-topic"  # 订阅NATS主题
```

---

## 6. 监控与日志

### 6.1 Prometheus集成

```bash
# 1. 访问Prometheus
kubectl port-forward -n openfaas svc/prometheus 9090:9090

# 浏览器打开: http://localhost:9090

# 2. 核心指标
# 函数调用次数:
gateway_function_invocation_total

# 函数调用延迟:
gateway_functions_seconds

# 副本数:
gateway_service_count

# 3. PromQL查询示例
# 每个函数的调用率 (QPS):
rate(gateway_function_invocation_total[1m])

# 函数P99延迟:
histogram_quantile(0.99, rate(gateway_functions_seconds_bucket[5m]))

# 函数错误率:
rate(gateway_function_invocation_total{code="500"}[5m])
```

---

### 6.2 Grafana Dashboard

```bash
# 1. 部署Grafana (如果未安装)
kubectl -n openfaas run grafana \
  --image=grafana/grafana:latest \
  --port=3000 \
  --env="GF_SECURITY_ADMIN_PASSWORD=admin"

kubectl -n openfaas expose pod grafana --port=3000 --type=LoadBalancer

# 2. 访问Grafana
kubectl port-forward -n openfaas svc/grafana 3000:3000

# 浏览器: http://localhost:3000
# 用户名: admin
# 密码: admin

# 3. 添加Prometheus数据源
# URL: http://prometheus:9090

# 4. 导入OpenFaaS Dashboard
# Dashboard ID: 3434
# https://grafana.com/grafana/dashboards/3434

# 5. 查看指标:
# - 函数调用数
# - 调用速率 (RPS)
# - 延迟 (P50/P90/P99)
# - 错误率
# - 副本数
```

---

### 6.3 日志查看

```bash
# 1. 查看函数日志
faas-cli logs <function-name>

# 例如:
faas-cli logs nodeinfo

# 2. 实时日志 (跟踪)
faas-cli logs nodeinfo --follow
# 或
faas-cli logs nodeinfo -f

# 3. 查看最近N行
faas-cli logs nodeinfo --tail=50

# 4. 指定时间范围
faas-cli logs nodeinfo --since=5m
faas-cli logs nodeinfo --since=2025-10-19T12:00:00Z

# 5. Kubernetes原生命令
kubectl -n openfaas-fn logs deploy/nodeinfo -f

# 6. 多Pod聚合日志
kubectl -n openfaas-fn logs -l faas_function=nodeinfo -f

# 7. (推荐) 使用日志聚合工具
# - Loki + Promtail
# - ELK Stack
# - Fluentd
```

---

### 6.4 告警配置

```yaml
# alertmanager-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: openfaas
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m

    route:
      group_by: ['alertname', 'cluster']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
      receiver: 'slack'

    receivers:
    - name: 'slack'
      slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#openfaas-alerts'
        title: 'OpenFaaS Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

---
# prometheus-rules.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-rules
  namespace: openfaas
data:
  alert.rules: |
    groups:
    - name: openfaas
      interval: 10s
      rules:

      # 函数调用失败率高
      - alert: HighFunctionErrorRate
        expr: |
          rate(gateway_function_invocation_total{code="500"}[5m]) > 0.05
        for: 1m
        labels:
          severity: warning
        annotations:
          description: "Function {{ $labels.function_name }} has high error rate"

      # 函数延迟高
      - alert: HighFunctionLatency
        expr: |
          histogram_quantile(0.99, rate(gateway_functions_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          description: "Function {{ $labels.function_name }} has high latency"

      # 函数副本数为0
      - alert: FunctionScaledToZero
        expr: |
          gateway_service_count == 0
        for: 5m
        labels:
          severity: info
        annotations:
          description: "Function {{ $labels.function_name }} scaled to zero"
```

---

## 7. CI/CD集成

### 7.1 GitHub Actions

```yaml
# .github/workflows/openfaas.yml
name: OpenFaaS CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  OPENFAAS_URL: ${{ secrets.OPENFAAS_URL }}
  DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Setup faas-cli
      run: |
        curl -sSL https://cli.openfaas.com | sudo sh

    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Pull OpenFaaS templates
      run: faas-cli template store pull python3-http

    - name: Build functions
      run: faas-cli build -f stack.yml

    - name: Push functions
      run: faas-cli push -f stack.yml

    - name: Deploy functions
      run: |
        echo "${{ secrets.OPENFAAS_PASSWORD }}" | faas-cli login \
          --username admin --password-stdin
        faas-cli deploy -f stack.yml

    - name: Test functions
      run: |
        sleep 10
        echo "Testing function..."
        curl -s http://${OPENFAAS_URL}/function/my-function -d "test"
```

---

### 7.2 GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  OPENFAAS_URL: $OPENFAAS_URL

before_script:
  - curl -sSL https://cli.openfaas.com | sh
  - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin

build:
  stage: build
  script:
    - faas-cli template store pull python3-http
    - faas-cli build -f stack.yml
    - faas-cli push -f stack.yml
  only:
    - main

test:
  stage: test
  script:
    - echo "Running tests..."
    - faas-cli invoke my-function --query="test=true"
  only:
    - main

deploy:
  stage: deploy
  script:
    - echo "$OPENFAAS_PASSWORD" | faas-cli login --username admin --password-stdin
    - faas-cli deploy -f stack.yml
  environment:
    name: production
    url: $OPENFAAS_URL
  only:
    - main
```

---

### 7.3 Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        OPENFAAS_URL = credentials('openfaas-url')
        OPENFAAS_PASSWORD = credentials('openfaas-password')
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_CREDENTIALS = credentials('docker-credentials')
    }

    stages {
        stage('Setup') {
            steps {
                sh 'curl -sSL https://cli.openfaas.com | sudo sh'
                sh 'echo $DOCKER_CREDENTIALS_PSW | docker login -u $DOCKER_CREDENTIALS_USR --password-stdin'
            }
        }

        stage('Build') {
            steps {
                sh 'faas-cli template store pull python3-http'
                sh 'faas-cli build -f stack.yml'
            }
        }

        stage('Test') {
            steps {
                sh 'echo "Running tests..."'
                // 添加测试命令
            }
        }

        stage('Push') {
            steps {
                sh 'faas-cli push -f stack.yml'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    echo "$OPENFAAS_PASSWORD" | faas-cli login \
                      --username admin --password-stdin
                    faas-cli deploy -f stack.yml
                '''
            }
        }

        stage('Verify') {
            steps {
                sh 'faas-cli list'
                sh 'curl -s $OPENFAAS_URL/function/my-function -d "test"'
            }
        }
    }

    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
```

---

### 7.4 ArgoCD GitOps

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: openfaas-functions
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/your-org/openfaas-functions.git
    targetRevision: HEAD
    path: functions

    # Kustomize (可选)
    kustomize:
      images:
      - your-username/my-function:latest

  destination:
    server: https://kubernetes.default.svc
    namespace: openfaas-fn

  syncPolicy:
    automated:
      prune: true
      selfHeal: true

    syncOptions:
    - CreateNamespace=true

    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

**函数部署为Kubernetes资源**:

```yaml
# functions/my-function.yaml
apiVersion: openfaas.com/v1
kind: Function
metadata:
  name: my-function
  namespace: openfaas-fn
spec:
  name: my-function
  image: your-username/my-function:latest

  labels:
    com.openfaas.scale.min: "1"
    com.openfaas.scale.max: "5"

  environment:
    write_timeout: "10s"
    read_timeout: "10s"

  limits:
    memory: "128Mi"
    cpu: "100m"

  requests:
    memory: "64Mi"
    cpu: "50m"
```

---

## 8. 实战案例

### 8.1 图片处理函数

```bash
# 创建函数
faas-cli new image-resizer --lang python3-http --prefix <username>
```

```python
# image-resizer/handler.py
from PIL import Image
import io
import base64
import json

def handle(req):
    """调整图片大小"""
    try:
        # 解析请求
        data = json.loads(req)
        image_b64 = data['image']
        width = data.get('width', 800)
        height = data.get('height', 600)

        # 解码图片
        image_data = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_data))

        # 调整大小
        resized = image.resize((width, height), Image.LANCZOS)

        # 编码为Base64
        buffer = io.BytesIO()
        resized.save(buffer, format='PNG')
        result_b64 = base64.b64encode(buffer.getvalue()).decode()

        return json.dumps({
            'success': True,
            'image': result_b64,
            'size': f'{width}x{height}'
        })

    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })
```

```txt
# image-resizer/requirements.txt
Pillow==10.0.0
```

```bash
# 部署
faas-cli up -f image-resizer.yml

# 测试 (准备一张测试图片)
base64 test.jpg > test.b64

# 调用函数
curl -X POST http://127.0.0.1:8080/function/image-resizer \
  -H "Content-Type: application/json" \
  -d "{\"image\":\"$(cat test.b64)\",\"width\":400,\"height\":300}"
```

---

### 8.2 Webhook处理

```python
# github-webhook/handler.py
import json
import hmac
import hashlib

def handle(req):
    """处理GitHub Webhook"""
    try:
        # 解析Webhook payload
        payload = json.loads(req)

        # 提取信息
        event_type = payload.get('action', 'unknown')
        repository = payload.get('repository', {}).get('full_name', 'unknown')
        sender = payload.get('sender', {}).get('login', 'unknown')

        # 处理不同事件
        if 'pull_request' in payload:
            pr_number = payload['pull_request']['number']
            pr_title = payload['pull_request']['title']

            message = f"PR #{pr_number}: {pr_title} - {event_type} by {sender}"

        elif 'issue' in payload:
            issue_number = payload['issue']['number']
            issue_title = payload['issue']['title']

            message = f"Issue #{issue_number}: {issue_title} - {event_type} by {sender}"

        else:
            message = f"Event: {event_type} in {repository} by {sender}"

        # 发送通知 (Slack/Email/etc)
        # send_notification(message)

        return json.dumps({
            'success': True,
            'message': message
        })

    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })
```

---

### 8.3 数据ETL

```python
# data-etl/handler.py
import json
import csv
import io

def handle(req):
    """CSV到JSON转换"""
    try:
        # 解析CSV
        csv_data = io.StringIO(req)
        reader = csv.DictReader(csv_data)

        # 转换为JSON
        records = []
        for row in reader:
            # 数据清洗
            cleaned = {
                k.strip(): v.strip()
                for k, v in row.items()
            }

            # 数据转换
            if 'age' in cleaned:
                cleaned['age'] = int(cleaned['age'])
            if 'price' in cleaned:
                cleaned['price'] = float(cleaned['price'])

            records.append(cleaned)

        # 统计
        stats = {
            'total_records': len(records),
            'columns': list(records[0].keys()) if records else []
        }

        return json.dumps({
            'success': True,
            'data': records,
            'stats': stats
        })

    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })
```

---

### 8.4 微服务编排

```python
# orchestrator/handler.py
import requests
import json
import os

def handle(req):
    """编排多个函数"""
    try:
        gateway_url = os.getenv("gateway_url", "http://gateway.openfaas:8080")
        data = json.loads(req)

        # 步骤1: 数据验证
        validation_result = call_function(
            gateway_url,
            'validator',
            json.dumps(data)
        )

        if not validation_result['valid']:
            return json.dumps({'error': 'Validation failed'})

        # 步骤2: 数据处理
        processing_result = call_function(
            gateway_url,
            'processor',
            json.dumps(validation_result['data'])
        )

        # 步骤3: 数据存储
        storage_result = call_function(
            gateway_url,
            'storage',
            json.dumps(processing_result)
        )

        # 步骤4: 发送通知
        notification_result = call_function(
            gateway_url,
            'notifier',
            json.dumps({'message': 'Processing complete'})
        )

        return json.dumps({
            'success': True,
            'steps': {
                'validation': validation_result,
                'processing': processing_result,
                'storage': storage_result,
                'notification': notification_result
            }
        })

    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })

def call_function(gateway_url, function_name, payload):
    """调用函数"""
    url = f"{gateway_url}/function/{function_name}"
    response = requests.post(url, data=payload)
    return response.json()
```

---

## 9. 总结

```yaml
本章要点:
  ✅ OpenFaaS概述 (定义/特性/架构)
  ✅ 快速部署 (Docker Swarm/K8s/faasd)
  ✅ faas-cli工具 (命令/生命周期/Secret)
  ✅ 多语言开发 (Python/Go/Node.js/自定义模板)
  ✅ 高级特性 (异步/扩缩容/函数间调用/NATS)
  ✅ 监控日志 (Prometheus/Grafana/日志/告警)
  ✅ CI/CD集成 (GitHub Actions/GitLab CI/Jenkins/ArgoCD)
  ✅ 实战案例 (图片/Webhook/ETL/编排)

OpenFaaS核心价值:
  - 简单易用 (10分钟上手)
  - 多语言支持 (任何语言)
  - 强大CLI工具 (faas-cli)
  - 容器原生
  - 活跃社区

适用场景:
  ✅ 快速原型开发
  ✅ 事件驱动应用
  ✅ API后端
  ✅ Webhook处理
  ✅ 数据ETL
  ✅ 微服务

关键特性:
  ⭐ 简单部署 (3种方式)
  ⭐ 自动扩缩容
  ⭐ 异步调用
  ⭐ 监控内置
  ⭐ CI/CD友好

vs Knative:
  OpenFaaS: 简单、快速、易用
  Knative: 功能强大、企业级
```

---

**下一章预告**:

**04 - 边缘Serverless**:

- 边缘计算与Serverless结合
- Cloudflare Workers详解
- AWS Lambda@Edge
- Fastly Compute@Edge
- WebAssembly在边缘的应用

---

**完成日期**: 2025-10-19
**版本**: v1.0
**作者**: 云原生专家团队

**Tags**: `#OpenFaaS` `#Serverless` `#FaaS` `#Docker` `#Kubernetes`

---

## 相关文档

### 本模块相关

- [Serverless概述与架构](./01_Serverless概述与架构.md) - Serverless概述与架构
- [Knative深度解析](./02_Knative深度解析.md) - Knative深度解析
- [边缘Serverless](./04_边缘Serverless.md) - 边缘Serverless
- [Serverless安全](./05_Serverless安全.md) - Serverless安全
- [Serverless性能优化](./06_Serverless性能优化.md) - Serverless性能优化
- [Serverless CI/CD](./07_Serverless_CICD.md) - Serverless CI/CD
- [Serverless实战案例](./08_Serverless实战案例.md) - Serverless实战案例
- [Serverless最佳实践](./09_Serverless最佳实践.md) - Serverless最佳实践
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [Kubernetes技术详解](../03_Kubernetes技术详解/README.md) - Kubernetes技术体系
- [容器编排技术](../04_容器编排技术/README.md) - 容器编排技术
- [Docker技术详解](../01_Docker技术详解/README.md) - Docker技术详解
- [容器技术实践案例](../08_容器技术实践案例/README.md) - 容器技术实践案例

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新
