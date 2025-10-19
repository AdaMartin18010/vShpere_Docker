# Docker镜像管理

> **返回**: [Docker部署目录](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Docker镜像管理](#docker镜像管理)
  - [📋 目录](#-目录)
  - [1. Docker镜像基础](#1-docker镜像基础)
  - [2. Dockerfile详解](#2-dockerfile详解)
    - [2.1 Dockerfile指令](#21-dockerfile指令)
    - [2.2 Dockerfile最佳实践](#22-dockerfile最佳实践)
  - [3. 镜像构建](#3-镜像构建)
    - [3.1 基础构建](#31-基础构建)
    - [3.2 多阶段构建](#32-多阶段构建)
    - [3.3 BuildKit增强构建](#33-buildkit增强构建)
  - [4. 镜像优化](#4-镜像优化)
    - [4.1 镜像体积优化](#41-镜像体积优化)
    - [4.2 构建速度优化](#42-构建速度优化)
    - [4.3 镜像层优化](#43-镜像层优化)
  - [5. 私有镜像仓库](#5-私有镜像仓库)
    - [5.1 Harbor部署](#51-harbor部署)
    - [5.2 Harbor配置与使用](#52-harbor配置与使用)
  - [6. 镜像扫描与安全](#6-镜像扫描与安全)
    - [6.1 使用Trivy扫描](#61-使用trivy扫描)
    - [6.2 使用Clair扫描](#62-使用clair扫描)
  - [7. 镜像签名与验证](#7-镜像签名与验证)
  - [8. 镜像管理最佳实践](#8-镜像管理最佳实践)
  - [相关文档](#相关文档)

---

## 1. Docker镜像基础

```yaml
Docker_Image_Basics:
  定义:
    - 只读模板
    - 用于创建容器
    - 分层文件系统
    - 可共享和复用
  
  镜像组成:
    Layer (层):
      - 每个指令创建一层
      - 只读层
      - 使用Union FS合并
      - 可共享复用
    
    Base Image (基础镜像):
      - 最底层镜像
      - 通常是操作系统
      - 例: ubuntu, alpine, debian
    
    Parent Image (父镜像):
      - 当前镜像基于的镜像
      - FROM指令指定
    
    Manifest (清单):
      - 描述镜像元数据
      - 包含架构信息
      - 支持多架构镜像
  
  镜像标识:
    Image ID:
      - SHA256哈希值
      - 64位十六进制
      - 唯一标识镜像
    
    Image Tag (标签):
      - 人类可读标识
      - 格式: repository:tag
      - 默认tag为latest
      - 示例: nginx:1.21, redis:6-alpine
  
  镜像命名规范:
    完整格式: [registry/][namespace/]repository[:tag][@digest]
    
    示例:
      - nginx:latest (Docker Hub)
      - docker.io/library/nginx:1.21
      - harbor.example.com/prod/myapp:v1.0.0
      - quay.io/prometheus/prometheus:v2.40.0

  常用基础镜像:
    Alpine:
      大小: ~5MB
      特点: 极小、安全、musl libc
      适用: 生产环境首选
      缺点: 某些软件包不兼容
    
    Ubuntu:
      大小: ~70MB
      特点: 完整、软件包丰富
      适用: 需要完整系统工具
      缺点: 体积较大
    
    Debian:
      大小: ~50MB
      特点: 稳定、兼容性好
      适用: 通用场景
    
    CentOS/Rocky:
      大小: ~200MB
      特点: 企业级、RHEL兼容
      适用: 企业环境
      缺点: 体积最大
    
    Scratch:
      大小: 0MB
      特点: 空镜像
      适用: 静态编译二进制
      示例: Go编译程序
    
    Distroless:
      大小: 变量
      特点: 无包管理器、无shell
      适用: 高安全要求
      来源: Google
```

**镜像基本操作**:

```bash
# 拉取镜像
docker pull nginx:latest
docker pull nginx:1.21-alpine

# 查看本地镜像
docker images
docker images nginx

# 查看镜像详情
docker inspect nginx:latest

# 查看镜像历史
docker history nginx:latest

# 删除镜像
docker rmi nginx:latest
docker rmi $(docker images -q -f "dangling=true")  # 删除悬空镜像

# 镜像打标签
docker tag nginx:latest harbor.example.com/prod/nginx:v1.0

# 推送镜像
docker push harbor.example.com/prod/nginx:v1.0

# 保存镜像为tar文件
docker save -o nginx.tar nginx:latest

# 从tar文件加载镜像
docker load -i nginx.tar

# 导出容器为镜像
docker export container_name > container.tar
docker import container.tar myimage:v1
```

---

## 2. Dockerfile详解

### 2.1 Dockerfile指令

```dockerfile
# ========================================
# Dockerfile完整指令示例
# ========================================

# FROM - 基础镜像
FROM ubuntu:22.04 AS builder
# 支持变量
ARG BASE_IMAGE=ubuntu:22.04
FROM ${BASE_IMAGE}

# LABEL - 元数据标签
LABEL maintainer="admin@example.com"
LABEL version="1.0"
LABEL description="My Application"

# ARG - 构建时变量
ARG APP_VERSION=1.0.0
ARG BUILD_DATE
ARG VCS_REF

# ENV - 环境变量
ENV APP_HOME=/app \
    APP_PORT=8080 \
    PATH=/app/bin:$PATH

# WORKDIR - 工作目录
WORKDIR /app

# COPY - 复制文件
COPY package.json .
COPY src/ ./src/
# 支持--chown
COPY --chown=user:group app.jar /app/

# ADD - 复制文件 (支持URL和自动解压)
ADD https://example.com/file.tar.gz /tmp/
ADD app.tar.gz /app/
# 注意: 推荐使用COPY，除非需要URL或解压功能

# RUN - 执行命令
RUN apt-get update && \
    apt-get install -y curl wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 支持多种shell
RUN ["/bin/bash", "-c", "echo hello"]

# USER - 切换用户
RUN useradd -m -u 1000 appuser
USER appuser
# 或
USER 1000:1000

# EXPOSE - 声明端口
EXPOSE 8080
EXPOSE 8443/tcp

# VOLUME - 声明卷
VOLUME ["/data", "/logs"]

# HEALTHCHECK - 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# 或禁用健康检查
HEALTHCHECK NONE

# ONBUILD - 触发器指令
ONBUILD COPY package.json /app/
ONBUILD RUN npm install

# STOPSIGNAL - 停止信号
STOPSIGNAL SIGTERM

# SHELL - 设置shell
SHELL ["/bin/bash", "-c"]

# CMD - 容器启动命令
CMD ["nginx", "-g", "daemon off;"]
# 或 shell形式
CMD nginx -g "daemon off;"

# ENTRYPOINT - 入口点
ENTRYPOINT ["docker-entrypoint.sh"]
# 配合CMD使用
ENTRYPOINT ["java", "-jar"]
CMD ["app.jar"]
```

**指令说明对比**:

```yaml
Dockerfile_Instructions:
  COPY vs ADD:
    COPY:
      - 简单复制文件
      - 推荐使用
      - 透明明确
    
    ADD:
      - 支持URL下载
      - 自动解压tar/gzip
      - 功能过多，不推荐
    
    建议: 优先使用COPY
  
  CMD vs ENTRYPOINT:
    CMD:
      - 容器启动命令
      - 可被docker run参数覆盖
      - 示例: CMD ["nginx"]
    
    ENTRYPOINT:
      - 容器入口点
      - 不会被覆盖，除非--entrypoint
      - 示例: ENTRYPOINT ["docker-entrypoint.sh"]
    
    最佳实践:
      - ENTRYPOINT设置固定命令
      - CMD设置默认参数
      - 示例:
        ENTRYPOINT ["java", "-jar"]
        CMD ["app.jar"]
      
      # docker run会覆盖CMD
      docker run myapp app-dev.jar
  
  RUN vs CMD vs ENTRYPOINT:
    RUN:
      - 构建时执行
      - 创建新层
      - 安装软件、配置系统
    
    CMD:
      - 运行时执行
      - 不创建层
      - 容器启动命令
    
    ENTRYPOINT:
      - 运行时执行
      - 容器固定入口
```

### 2.2 Dockerfile最佳实践

```dockerfile
# ========================================
# Dockerfile最佳实践示例
# ========================================

# 1. 使用明确的基础镜像标签
FROM node:18.17-alpine3.18
# 避免: FROM node:latest

# 2. 使用多阶段构建
FROM golang:1.21-alpine AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o app

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /build/app .
CMD ["./app"]

# 3. 最小化层数 - 合并RUN命令
RUN apt-get update && \
    apt-get install -y \
        curl \
        wget \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 4. 利用构建缓存 - 先复制依赖文件
COPY package.json package-lock.json ./
RUN npm ci --only=production
COPY . .

# 5. 使用.dockerignore
# 创建.dockerignore文件:
# node_modules
# .git
# *.md
# .env

# 6. 不要以root运行
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# 7. 使用HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/health || exit 1

# 8. 设置合理的元数据
LABEL org.opencontainers.image.source="https://github.com/example/app"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"

# 9. 清理不必要文件
RUN apt-get update && \
    apt-get install -y package && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 10. 使用构建参数
ARG VERSION=1.0.0
ARG BUILD_DATE
ENV APP_VERSION=${VERSION}
```

---

## 3. 镜像构建

### 3.1 基础构建

```bash
# 基本构建
docker build -t myapp:v1.0 .

# 指定Dockerfile
docker build -f Dockerfile.prod -t myapp:prod .

# 使用构建参数
docker build \
  --build-arg VERSION=1.0.0 \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  -t myapp:v1.0 .

# 不使用缓存
docker build --no-cache -t myapp:v1.0 .

# 指定目标平台
docker build --platform linux/amd64 -t myapp:v1.0 .

# 多平台构建
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myapp:v1.0 \
  --push .
```

### 3.2 多阶段构建

```dockerfile
# ========================================
# 多阶段构建示例 - Java应用
# ========================================

# 阶段1: 构建
FROM maven:3.9-openjdk-17 AS build
WORKDIR /build

# 复制pom.xml并下载依赖 (利用缓存)
COPY pom.xml .
RUN mvn dependency:go-offline

# 复制源码并构建
COPY src ./src
RUN mvn package -DskipTests

# 阶段2: 运行
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# 从构建阶段复制jar
COPY --from=build /build/target/*.jar app.jar

# 创建非root用户
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD wget -qO- http://localhost:8080/actuator/health || exit 1

EXPOSE 8080
ENTRYPOINT ["java"]
CMD ["-jar", "app.jar"]
```

```dockerfile
# ========================================
# 多阶段构建示例 - Go应用
# ========================================

# 阶段1: 构建
FROM golang:1.21-alpine AS builder
WORKDIR /build

# 安装编译依赖
RUN apk add --no-cache git ca-certificates

# 复制go mod文件并下载依赖
COPY go.mod go.sum ./
RUN go mod download

# 复制源码并编译
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-s -w" \
    -o app \
    .

# 阶段2: 运行 (使用scratch最小镜像)
FROM scratch
WORKDIR /app

# 复制CA证书 (用于HTTPS)
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# 复制二进制文件
COPY --from=builder /build/app .

# 声明端口
EXPOSE 8080

# 运行应用
ENTRYPOINT ["./app"]
```

```dockerfile
# ========================================
# 多阶段构建示例 - Node.js应用
# ========================================

# 阶段1: 依赖安装
FROM node:18-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# 阶段2: 构建
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# 阶段3: 运行
FROM node:18-alpine
WORKDIR /app

# 复制生产依赖
COPY --from=deps /app/node_modules ./node_modules
# 复制构建产物
COPY --from=builder /app/dist ./dist
COPY package.json ./

# 创建非root用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs

EXPOSE 3000
CMD ["node", "dist/main.js"]
```

### 3.3 BuildKit增强构建

```bash
# 启用BuildKit
export DOCKER_BUILDKIT=1

# 或每次构建时启用
DOCKER_BUILDKIT=1 docker build -t myapp:v1.0 .

# BuildKit特性: 缓存挂载
```

```dockerfile
# 使用BuildKit缓存挂载
FROM golang:1.21-alpine
WORKDIR /build

# 挂载go mod缓存
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=bind,source=go.sum,target=go.sum \
    --mount=type=bind,source=go.mod,target=go.mod \
    go mod download

# 挂载构建缓存
RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
    --mount=type=bind,target=. \
    go build -o /app .
```

```dockerfile
# BuildKit秘密挂载
# docker build --secret id=npmrc,src=$HOME/.npmrc -t myapp .

FROM node:18-alpine
WORKDIR /app

# 挂载秘密文件
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm install

COPY . .
RUN npm run build
```

---

## 4. 镜像优化

### 4.1 镜像体积优化

```yaml
Image_Size_Optimization:
  策略1_使用Alpine基础镜像:
    对比:
      ubuntu:22.04: ~77MB
      node:18: ~950MB
      node:18-alpine: ~170MB
      
    示例:
      FROM node:18-alpine
      # 而不是 FROM node:18
  
  策略2_多阶段构建:
    效果: 减少50%-90%体积
    
    示例:
      # 构建阶段: 1GB
      FROM golang:1.21 AS builder
      RUN go build -o app
      
      # 运行阶段: 10MB
      FROM alpine:3.18
      COPY --from=builder /build/app .
  
  策略3_清理包管理器缓存:
    Ubuntu/Debian:
      RUN apt-get update && \
          apt-get install -y package && \
          apt-get clean && \
          rm -rf /var/lib/apt/lists/*
    
    Alpine:
      RUN apk add --no-cache package
      # 或
      RUN apk add package && \
          rm -rf /var/cache/apk/*
    
    CentOS/RHEL:
      RUN yum install -y package && \
          yum clean all && \
          rm -rf /var/cache/yum
  
  策略4_合并RUN命令:
    ❌ 不好:
      RUN apt-get update
      RUN apt-get install -y curl
      RUN apt-get install -y wget
      # 创建3层
    
    ✅ 好:
      RUN apt-get update && \
          apt-get install -y curl wget && \
          apt-get clean
      # 创建1层
  
  策略5_使用.dockerignore:
    # .dockerignore
    node_modules
    .git
    .DS_Store
    *.md
    .env
    .vscode
    coverage
    dist
    build
  
  策略6_删除不必要文件:
    RUN wget https://example.com/file.tar.gz && \
        tar -xzf file.tar.gz && \
        rm file.tar.gz
```

**镜像体积对比示例**:

```bash
# 优化前
FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install flask
COPY app.py .
CMD ["python3", "app.py"]
# 大小: ~500MB

# 优化后
FROM python:3.11-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
# 大小: ~60MB
```

### 4.2 构建速度优化

```yaml
Build_Speed_Optimization:
  策略1_利用构建缓存:
    # 先复制依赖文件
    COPY package.json package-lock.json ./
    RUN npm ci
    # 后复制源码
    COPY . .
    # 这样源码改变时，依赖层不需要重建
  
  策略2_使用BuildKit并行构建:
    export DOCKER_BUILDKIT=1
    # BuildKit自动并行执行独立的RUN指令
  
  策略3_使用本地缓存:
    # 使用--cache-from
    docker build \
      --cache-from myapp:latest \
      -t myapp:v2.0 .
  
  策略4_减少COPY操作:
    # 只复制需要的文件
    COPY package.json .
    # 而不是
    COPY . .
```

### 4.3 镜像层优化

```dockerfile
# ========================================
# 镜像层优化示例
# ========================================

# ❌ 不好 - 创建多个层
FROM alpine:3.18
RUN apk add --no-cache curl
RUN apk add --no-cache wget
RUN apk add --no-cache git
RUN rm -rf /tmp/*
# 4个层

# ✅ 好 - 合并为一层
FROM alpine:3.18
RUN apk add --no-cache \
    curl \
    wget \
    git && \
    rm -rf /tmp/*
# 1个层

# ========================================
# 优化COPY指令
# ========================================

# ❌ 不好 - 每次修改都重新复制所有文件
FROM node:18-alpine
COPY . .
RUN npm install

# ✅ 好 - 利用缓存
FROM node:18-alpine
WORKDIR /app
# 先复制依赖文件 (变化少)
COPY package*.json ./
RUN npm ci
# 后复制源码 (变化多)
COPY . .

# ========================================
# 清理临时文件
# ========================================

# ❌ 不好 - 删除在不同层，文件仍占用空间
RUN wget https://example.com/large.tar.gz
RUN tar -xzf large.tar.gz
RUN rm large.tar.gz  # 文件已在前面的层中

# ✅ 好 - 在同一层中下载、解压、删除
RUN wget https://example.com/large.tar.gz && \
    tar -xzf large.tar.gz && \
    rm large.tar.gz
```

---

## 5. 私有镜像仓库

### 5.1 Harbor部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  registry:
    image: goharbor/registry-photon:v2.9.0
    container_name: registry
    restart: always
    volumes:
      - /data/registry:/storage
      - ./common/config/registry/:/etc/registry/:z
    networks:
      - harbor
    environment:
      - REGISTRY_HTTP_SECRET=CHANGEME
    command:
      - serve
      - /etc/registry/config.yml

  registryctl:
    image: goharbor/harbor-registryctl:v2.9.0
    container_name: registryctl
    restart: always
    volumes:
      - /data/registry:/storage
      - ./common/config/registry/:/etc/registry/:z
      - ./common/config/registryctl/config.yml:/etc/registryctl/config.yml:z
    networks:
      - harbor

  postgresql:
    image: goharbor/harbor-db:v2.9.0
    container_name: harbor-db
    restart: always
    volumes:
      - /data/database:/var/lib/postgresql/data
    networks:
      - harbor
    environment:
      - POSTGRES_PASSWORD=changeit

  core:
    image: goharbor/harbor-core:v2.9.0
    container_name: harbor-core
    restart: always
    volumes:
      - /data/ca_download/:/etc/core/ca/:z
      - /data/:/data/:z
      - ./common/config/core/app.conf:/etc/core/app.conf:z
      - ./common/config/core/private_key.pem:/etc/core/private_key.pem:z
    networks:
      - harbor
    depends_on:
      - registry
      - postgresql

  portal:
    image: goharbor/harbor-portal:v2.9.0
    container_name: harbor-portal
    restart: always
    networks:
      - harbor
    depends_on:
      - core

  jobservice:
    image: goharbor/harbor-jobservice:v2.9.0
    container_name: harbor-jobservice
    restart: always
    volumes:
      - /data/job_logs:/var/log/jobs:z
      - ./common/config/jobservice/config.yml:/etc/jobservice/config.yml:z
    networks:
      - harbor
    depends_on:
      - core

  proxy:
    image: goharbor/nginx-photon:v2.9.0
    container_name: nginx
    restart: always
    volumes:
      - ./common/config/nginx:/etc/nginx:z
    networks:
      - harbor
    ports:
      - 80:8080
      - 443:8443
    depends_on:
      - registry
      - core
      - portal

networks:
  harbor:
    external: false
```

**Harbor一键安装脚本**:

```bash
#!/bin/bash
# ========================================
# Harbor一键安装脚本
# ========================================

set -e

HARBOR_VERSION="v2.9.0"
HARBOR_HOSTNAME="harbor.example.com"
HARBOR_ADMIN_PASSWORD="Harbor12345"
DATA_VOLUME="/data/harbor"

echo "===== Harbor安装脚本 ====="
echo "版本: $HARBOR_VERSION"
echo "主机名: $HARBOR_HOSTNAME"

# 1. 下载Harbor离线安装包
echo "➤ 下载Harbor..."
wget https://github.com/goharbor/harbor/releases/download/$HARBOR_VERSION/harbor-offline-installer-$HARBOR_VERSION.tgz

# 2. 解压
tar xzvf harbor-offline-installer-$HARBOR_VERSION.tgz
cd harbor

# 3. 配置harbor.yml
cp harbor.yml.tmpl harbor.yml

sed -i "s/hostname: .*/hostname: $HARBOR_HOSTNAME/" harbor.yml
sed -i "s/harbor_admin_password: .*/harbor_admin_password: $HARBOR_ADMIN_PASSWORD/" harbor.yml
sed -i "s|data_volume: .*|data_volume: $DATA_VOLUME|" harbor.yml

# 如果不使用HTTPS，注释掉https相关配置
sed -i 's/^https:/#https:/' harbor.yml
sed -i 's/^  port: 443/#  port: 443/' harbor.yml
sed -i 's|^  certificate: .*|#  certificate: /your/certificate/path|' harbor.yml
sed -i 's|^  private_key: .*|#  private_key: /your/private/key/path|' harbor.yml

# 4. 安装Harbor
echo "➤ 安装Harbor..."
./install.sh --with-trivy --with-chartmuseum

echo "✅ Harbor安装完成！"
echo "访问地址: http://$HARBOR_HOSTNAME"
echo "用户名: admin"
echo "密码: $HARBOR_ADMIN_PASSWORD"
```

### 5.2 Harbor配置与使用

```bash
# 1. Docker客户端配置 (HTTP仓库)
# 编辑/etc/docker/daemon.json
{
  "insecure-registries": ["harbor.example.com"]
}

# 重启Docker
sudo systemctl restart docker

# 2. 登录Harbor
docker login harbor.example.com
# 输入用户名和密码

# 3. 推送镜像
# 打标签
docker tag myapp:v1.0 harbor.example.com/library/myapp:v1.0

# 推送
docker push harbor.example.com/library/myapp:v1.0

# 4. 拉取镜像
docker pull harbor.example.com/library/myapp:v1.0

# 5. Harbor CLI操作
# 创建项目
curl -X POST "http://harbor.example.com/api/v2.0/projects" \
  -H "Content-Type: application/json" \
  -u "admin:Harbor12345" \
  -d '{
    "project_name": "myproject",
    "public": false
  }'

# 列出镜像
curl -X GET "http://harbor.example.com/api/v2.0/projects/library/repositories" \
  -u "admin:Harbor12345"
```

---

## 6. 镜像扫描与安全

### 6.1 使用Trivy扫描

```bash
# 安装Trivy
# Ubuntu/Debian
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# 扫描镜像
trivy image nginx:latest

# 扫描并输出JSON
trivy image -f json -o results.json nginx:latest

# 只显示HIGH和CRITICAL漏洞
trivy image --severity HIGH,CRITICAL nginx:latest

# 扫描本地镜像
trivy image myapp:v1.0

# 扫描Dockerfile
trivy config Dockerfile

# CI/CD集成
trivy image --exit-code 1 --severity CRITICAL myapp:v1.0
# exit-code 1: 发现CRITICAL漏洞时返回1
```

### 6.2 使用Clair扫描

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: clair
    volumes:
      - postgres_data:/var/lib/postgresql/data

  clair:
    image: quay.io/projectquay/clair:latest
    depends_on:
      - postgres
    ports:
      - "6060:6060"
      - "6061:6061"
    volumes:
      - ./clair-config.yaml:/etc/clair/config.yaml

volumes:
  postgres_data:
```

```bash
# 使用clairctl扫描
clairctl analyze myapp:v1.0
clairctl report myapp:v1.0
```

---

## 7. 镜像签名与验证

```bash
# 使用Docker Content Trust (DCT)
export DOCKER_CONTENT_TRUST=1

# 推送签名镜像
docker push myregistry.com/myapp:v1.0
# 会提示输入签名密钥密码

# 拉取时自动验证签名
docker pull myregistry.com/myapp:v1.0

# 查看镜像签名信息
docker trust inspect myregistry.com/myapp:v1.0

# 使用Cosign签名 (推荐)
# 安装Cosign
wget https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign

# 生成密钥对
cosign generate-key-pair

# 签名镜像
cosign sign --key cosign.key myregistry.com/myapp:v1.0

# 验证签名
cosign verify --key cosign.pub myregistry.com/myapp:v1.0
```

---

## 8. 镜像管理最佳实践

```yaml
Image_Management_Best_Practices:
  命名规范:
    ✅ 使用语义化版本:
      - myapp:v1.0.0
      - myapp:v1.0.0-beta.1
    
    ✅ 使用Git commit SHA:
      - myapp:commit-abc1234
    
    ✅ 使用构建日期:
      - myapp:20251019
    
    ❌ 避免使用latest:
      - 不可预测
      - 无法回滚
      - 缓存问题
  
  标签策略:
    多标签:
      # 同时打多个标签
      docker tag myapp:build-123 myapp:v1.0.0
      docker tag myapp:build-123 myapp:latest
      docker tag myapp:build-123 myapp:stable
    
    环境标签:
      - myapp:dev
      - myapp:test  
      - myapp:staging
      - myapp:prod
  
  镜像清理:
    定期清理:
      # 清理悬空镜像
      docker image prune -f
      
      # 清理所有未使用镜像
      docker image prune -a -f
      
      # 清理30天前的镜像
      docker images --filter "until=720h" -q | xargs docker rmi
    
    Harbor自动清理:
      # 配置镜像保留策略
      - 保留最近N个版本
      - 保留N天内的镜像
      - 按标签规则保留
  
  安全最佳实践:
    ✅ 使用非root用户:
      RUN adduser -D appuser
      USER appuser
    
    ✅ 扫描漏洞:
      - 使用Trivy/Clair
      - CI/CD集成扫描
      - 定期重新扫描
    
    ✅ 使用最小基础镜像:
      - Alpine
      - Distroless
      - Scratch
    
    ✅ 不在镜像中存储敏感信息:
      - 使用Secret管理
      - 使用环境变量
      - 使用外部配置
    
    ✅ 签名镜像:
      - 使用Cosign
      - 启用DCT
  
  构建自动化:
    CI/CD流水线:
      # GitLab CI示例
      build:
        stage: build
        script:
          - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
          - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
      
      scan:
        stage: scan
        script:
          - trivy image --exit-code 1 --severity CRITICAL $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
      
      tag:
        stage: tag
        script:
          - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
          - docker push $CI_REGISTRY_IMAGE:latest
  
  监控与审计:
    镜像使用监控:
      - 跟踪镜像版本使用
      - 监控镜像拉取次数
      - 审计镜像访问日志
    
    漏洞监控:
      - 定期扫描
      - 订阅安全公告
      - 及时更新基础镜像
```

---

## 相关文档

- [Docker安装与配置](01_Docker安装与配置.md)
- [Docker Compose](03_Docker_Compose.md)
- [Docker安全与最佳实践](04_Docker安全与最佳实践.md)
- [Kubernetes应用部署](../02_Kubernetes部署/03_应用部署.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪
