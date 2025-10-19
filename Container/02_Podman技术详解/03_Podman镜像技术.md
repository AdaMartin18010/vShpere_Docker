# Podman镜像技术

> 版本锚点（新增）：本文档基于 Podman 5.0+、Buildah 1.34+ 和 Skopeo 1.14+ 版本编写，版本信息统一参考《2025年技术标准最终对齐报告.md》。

## 目录

- [Podman镜像技术](#podman镜像技术)
  - [目录](#目录)
  - [1. 镜像结构与元数据（OCI）](#1-镜像结构与元数据oci)
    - [1.1 OCI镜像规范](#11-oci镜像规范)
    - [1.2 镜像层结构](#12-镜像层结构)
    - [1.3 镜像配置与标签](#13-镜像配置与标签)
  - [2. buildah 构建与缓存优化](#2-buildah-构建与缓存优化)
    - [2.1 buildah 基础](#21-buildah-基础)
    - [2.2 Dockerfile构建](#22-dockerfile构建)
    - [2.3 容器式构建](#23-容器式构建)
    - [2.4 缓存优化策略](#24-缓存优化策略)
    - [2.5 rootless 构建](#25-rootless-构建)
  - [3. 多架构镜像与 manifest](#3-多架构镜像与-manifest)
    - [3.1 多架构镜像概述](#31-多架构镜像概述)
    - [3.2 使用 buildah 构建多架构](#32-使用-buildah-构建多架构)
    - [3.3 manifest 管理](#33-manifest-管理)
    - [3.4 跨平台构建实践](#34-跨平台构建实践)
  - [4. 镜像签名、策略与供应链](#4-镜像签名策略与供应链)
    - [4.1 镜像签名机制](#41-镜像签名机制)
    - [4.2 policy.json 策略配置](#42-policyjson-策略配置)
    - [4.3 Sigstore 集成](#43-sigstore-集成)
    - [4.4 SBOM 与漏洞扫描](#44-sbom-与漏洞扫描)
  - [5. skopeo 分发与复制](#5-skopeo-分发与复制)
    - [5.1 skopeo 基础操作](#51-skopeo-基础操作)
    - [5.2 镜像复制与同步](#52-镜像复制与同步)
    - [5.3 air-gap 环境部署](#53-air-gap-环境部署)
    - [5.4 镜像格式转换](#54-镜像格式转换)
  - [6. 最佳实践与 FAQ](#6-最佳实践与-faq)
    - [6.1 镜像构建最佳实践](#61-镜像构建最佳实践)
    - [6.2 安全最佳实践](#62-安全最佳实践)
    - [6.3 性能优化](#63-性能优化)
  - [7. 实操示例](#7-实操示例)
    - [7.1 完整的多架构构建流程](#71-完整的多架构构建流程)
    - [7.2 镜像仓库同步](#72-镜像仓库同步)
    - [7.3 镜像签名与验证](#73-镜像签名与验证)
  - [8. 故障清单与排查](#8-故障清单与排查)
  - [9. FAQ](#9-faq)

## 1. 镜像结构与元数据（OCI）

### 1.1 OCI镜像规范

Podman 完全遵循 OCI (Open Container Initiative) 镜像规范，与 Docker 镜像格式完全兼容。

**OCI 镜像组成**：

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "size": 1469,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270"
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "size": 32654,
      "digest": "sha256:e692418e4cbaf90ca69d05a66403747baa33ee08806650b51fab815ad7fc331f"
    }
  ],
  "annotations": {
    "org.opencontainers.image.created": "2025-01-01T00:00:00Z",
    "org.opencontainers.image.authors": "Podman Team"
  }
}
```

**查看镜像清单**：

```bash
# 使用 podman 查看镜像详情
podman inspect alpine:3.20 | jq '.[0].Config'

# 使用 skopeo 查看远程镜像
skopeo inspect docker://docker.io/library/alpine:3.20

# 查看镜像层信息
podman history alpine:3.20
```

### 1.2 镜像层结构

Podman 使用 overlay2 存储驱动（或其他 containers/storage 支持的驱动）管理镜像层。

```bash
# 查看镜像层结构
podman inspect alpine:3.20 | jq '.[0].RootFS'

# 输出示例
{
  "Type": "layers",
  "Layers": [
    "sha256:4abcf20661432fb2d719aaf90656f55c287f8ca915dc1c92ec14ff61e67fbaf8"
  ]
}

# 查看镜像文件系统变更
podman diff alpine:3.20
```

**层目录结构**（在 rootless 模式下）：

```bash
# 镜像存储位置
$HOME/.local/share/containers/storage/

# 结构示例
storage/
├── overlay/              # overlay2 层数据
├── overlay-images/       # 镜像元数据
├── overlay-layers/       # 层链接
└── vfs-images/          # VFS驱动（如果使用）
```

### 1.3 镜像配置与标签

**OCI 标准标签（Annotations）**：

```bash
# 构建时添加标签
buildah bud \
  --label org.opencontainers.image.title="My App" \
  --label org.opencontainers.image.description="Application description" \
  --label org.opencontainers.image.version="1.0.0" \
  --label org.opencontainers.image.created="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --label org.opencontainers.image.source="https://github.com/myorg/myapp" \
  --label org.opencontainers.image.licenses="Apache-2.0" \
  -t myapp:1.0 .

# 查看标签
podman inspect myapp:1.0 | jq '.[0].Labels'
```

**镜像配置文件示例**：

```json
{
  "created": "2025-01-01T00:00:00Z",
  "author": "dev@example.com",
  "architecture": "amd64",
  "os": "linux",
  "config": {
    "User": "appuser",
    "ExposedPorts": {
      "8080/tcp": {}
    },
    "Env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "APP_ENV=production"
    ],
    "Entrypoint": ["/usr/local/bin/app"],
    "WorkingDir": "/app",
    "Labels": {
      "version": "1.0.0",
      "maintainer": "devops@example.com"
    }
  },
  "rootfs": {
    "type": "layers",
    "diff_ids": [
      "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270"
    ]
  }
}
```

## 2. buildah 构建与缓存优化

### 2.1 buildah 基础

Buildah 是专门用于构建 OCI 容器镜像的工具，完全支持 Dockerfile 并提供更灵活的命令式构建方式。

**安装 buildah**：

```bash
# Fedora/RHEL/CentOS
sudo dnf install buildah

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install buildah

# 验证安装
buildah version
```

**buildah 核心命令**：

```bash
# 创建容器
buildah from alpine:3.20

# 运行命令
buildah run alpine-working-container -- apk add nginx

# 配置容器
buildah config --entrypoint '["/usr/sbin/nginx", "-g", "daemon off;"]' alpine-working-container

# 提交镜像
buildah commit alpine-working-container myapp:latest

# 清理工作容器
buildah rm alpine-working-container
```

### 2.2 Dockerfile构建

Buildah 完全兼容 Dockerfile 语法，并提供增强功能：

```bash
# 使用 buildah 构建 Dockerfile
buildah bud -t myapp:1.0 .

# 等价于（buildah-bud 的别名）
buildah build-using-dockerfile -t myapp:1.0 .

# 指定 Dockerfile 路径
buildah bud -f Dockerfile.prod -t myapp:1.0 .

# 多阶段构建
buildah bud --layers -t myapp:1.0 .

# 设置构建参数
buildah bud --build-arg VERSION=1.0.0 -t myapp:1.0 .
```

**示例 Dockerfile**：

```dockerfile
# syntax=docker/dockerfile:1.7
FROM docker.io/library/golang:1.22-alpine AS builder

# 设置工作目录
WORKDIR /src

# 复制依赖文件
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/myapp ./cmd/myapp

# 运行阶段
FROM docker.io/library/alpine:3.20

# 安装运行时依赖
RUN apk add --no-cache ca-certificates tzdata

# 创建非root用户
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# 设置工作目录
WORKDIR /app

# 复制二进制文件
COPY --from=builder --chown=appuser:appuser /app/myapp /app/myapp

# 切换到非root用户
USER appuser

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["/app/myapp", "healthcheck"]

# 暴露端口
EXPOSE 8080

# 启动应用
ENTRYPOINT ["/app/myapp"]
CMD ["serve"]
```

### 2.3 容器式构建

Buildah 提供了更灵活的命令式构建方式，无需 Dockerfile：

```bash
#!/bin/bash
# 容器式构建脚本

# 1. 创建容器
container=$(buildah from alpine:3.20)

# 2. 挂载容器文件系统
mountpoint=$(buildah mount $container)

# 3. 直接操作文件系统
cp myapp $mountpoint/usr/local/bin/
chmod +x $mountpoint/usr/local/bin/myapp

# 或使用 buildah run
buildah run $container -- apk add --no-cache ca-certificates

# 4. 配置容器
buildah config --entrypoint '["/usr/local/bin/myapp"]' $container
buildah config --port 8080 $container
buildah config --user 1000:1000 $container
buildah config --workingdir /app $container

# 5. 添加标签
buildah config --label version="1.0.0" $container
buildah config --label maintainer="dev@example.com" $container

# 6. 卸载文件系统
buildah unmount $container

# 7. 提交镜像
buildah commit --squash $container myapp:1.0

# 8. 清理
buildah rm $container

echo "镜像构建完成: myapp:1.0"
```

**高级容器操作**：

```bash
# 从容器导出文件系统
container=$(buildah from alpine:3.20)
buildah mount $container | xargs -I{} tar -czf rootfs.tar.gz -C {} .
buildah rm $container

# 从 tar 包导入
buildah from scratch
container=$(buildah from scratch)
buildah add $container rootfs.tar.gz /
buildah commit $container myimage:latest
```

### 2.4 缓存优化策略

Buildah 支持多种缓存策略来加速构建：

**层缓存**：

```bash
# 启用层缓存（默认启用）
buildah bud --layers -t myapp:1.0 .

# 禁用缓存
buildah bud --no-cache -t myapp:1.0 .

# 从特定阶段开始构建（跳过缓存）
buildah bud --from=builder -t myapp:1.0 .
```

**优化 Dockerfile 层顺序**：

```dockerfile
# 优化前：每次代码变更都会重新安装依赖
FROM golang:1.22-alpine
WORKDIR /src
COPY . .
RUN go mod download
RUN go build -o /app/myapp ./cmd/myapp

# 优化后：依赖层可以被缓存
FROM golang:1.22-alpine
WORKDIR /src

# 先复制依赖文件（变更频率低）
COPY go.mod go.sum ./
RUN go mod download

# 再复制源代码（变更频率高）
COPY . .
RUN go build -o /app/myapp ./cmd/myapp
```

**使用 .containerignore / .dockerignore**：

```bash
# .containerignore 文件
.git/
.gitignore
*.md
.github/
.vscode/
node_modules/
.env*
*.log
tmp/
vendor/
```

**buildah 缓存目录**：

```bash
# 查看缓存位置
buildah info | grep -A 5 "store"

# 清理缓存
buildah rmi --all

# 清理未使用的层
buildah prune

# 深度清理
buildah system prune -a
```

### 2.5 rootless 构建

Buildah 的一大优势是原生支持 rootless 模式：

```bash
# rootless 模式构建（无需 sudo）
buildah bud -t myapp:1.0 .

# 检查 rootless 模式
buildah info | grep -i rootless

# rootless 配置文件
$HOME/.config/containers/storage.conf

# 示例配置
[storage]
driver = "overlay"
runroot = "$HOME/.local/share/containers/storage"
graphroot = "$HOME/.local/share/containers/storage"

[storage.options]
mountopt = "nodev"
```

**rootless 优势**：

1. 无需 root 权限，提高安全性
2. 每个用户独立的镜像存储
3. 避免权限冲突
4. 更好的多租户隔离

**rootless 限制**：

1. 不能绑定 1024 以下的端口（可用映射解决）
2. 某些存储驱动功能受限
3. 性能可能略有下降

```bash
# rootless 模式下处理端口映射
podman run -p 8080:80 nginx  # 将容器80端口映射到主机8080

# 使用 slirp4netns 提升网络性能
podman run --network slirp4netns:port_handler=slirp4netns nginx
```

## 3. 多架构镜像与 manifest

### 3.1 多架构镜像概述

多架构镜像允许同一个镜像标签支持多种 CPU 架构（如 x86_64、ARM64、ARMv7 等）。

**manifest 列表结构**：

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": 7143,
      "digest": "sha256:abc123...",
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    },
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": 7682,
      "digest": "sha256:def456...",
      "platform": {
        "architecture": "arm64",
        "os": "linux"
      }
    }
  ]
}
```

### 3.2 使用 buildah 构建多架构

**方法一：使用 QEMU 模拟**：

```bash
# 安装 QEMU 用户模式模拟
sudo dnf install qemu-user-static  # Fedora/RHEL
sudo apt-get install qemu-user-static  # Ubuntu/Debian

# 验证支持的架构
ls /proc/sys/fs/binfmt_misc/

# 为不同架构构建
buildah bud --arch amd64 -t myapp:amd64 .
buildah bud --arch arm64 -t myapp:arm64 .
buildah bud --arch arm -t myapp:armv7 .
```

**方法二：在原生架构上构建**：

```bash
# 在 x86_64 机器上构建
buildah bud -t myapp:amd64 .

# 在 ARM64 机器上构建（如树莓派、AWS Graviton）
buildah bud -t myapp:arm64 .
```

**多阶段多架构构建 Dockerfile**：

```dockerfile
# syntax=docker/dockerfile:1.7
ARG TARGETPLATFORM
ARG BUILDPLATFORM

FROM --platform=$BUILDPLATFORM golang:1.22-alpine AS builder
ARG TARGETPLATFORM
ARG TARGETOS
ARG TARGETARCH

WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -ldflags="-s -w" -o /app/myapp ./cmd/myapp

FROM --platform=$TARGETPLATFORM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=builder /app/myapp /usr/local/bin/myapp
ENTRYPOINT ["/usr/local/bin/myapp"]
```

### 3.3 manifest 管理

**创建和管理 manifest 列表**：

```bash
# 方法1：使用 buildah manifest
# 创建 manifest 列表
buildah manifest create myapp:latest

# 添加架构特定镜像到 manifest
buildah manifest add myapp:latest myapp:amd64
buildah manifest add myapp:latest myapp:arm64
buildah manifest add myapp:latest myapp:armv7

# 检查 manifest
buildah manifest inspect myapp:latest

# 推送 manifest 列表
buildah manifest push --all myapp:latest docker://registry.local/myapp:latest

# 方法2：使用 podman manifest
# 创建 manifest
podman manifest create myapp:latest

# 构建并添加到 manifest
podman build --platform linux/amd64 --manifest myapp:latest .
podman build --platform linux/arm64 --manifest myapp:latest .
podman build --platform linux/arm/v7 --manifest myapp:latest .

# 查看 manifest
podman manifest inspect myapp:latest

# 推送整个 manifest 列表
podman manifest push myapp:latest registry.local/myapp:latest
```

**一次性构建多架构**：

```bash
# 使用 podman buildx 风格命令（Podman 4.0+）
podman build --platform linux/amd64,linux/arm64,linux/arm/v7 \
  --manifest myapp:latest \
  -t myapp:latest .

# 推送
podman manifest push myapp:latest docker://registry.local/myapp:latest
```

### 3.4 跨平台构建实践

**CI/CD 多架构构建示例**：

```yaml
# .gitlab-ci.yml
build-multiarch:
  stage: build
  image: quay.io/buildah/stable:latest
  before_script:
    - buildah login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    # 构建各架构镜像
    - buildah bud --arch amd64 -t $CI_REGISTRY_IMAGE:amd64-$CI_COMMIT_SHORT_SHA .
    - buildah bud --arch arm64 -t $CI_REGISTRY_IMAGE:arm64-$CI_COMMIT_SHORT_SHA .
    
    # 推送各架构镜像
    - buildah push $CI_REGISTRY_IMAGE:amd64-$CI_COMMIT_SHORT_SHA
    - buildah push $CI_REGISTRY_IMAGE:arm64-$CI_COMMIT_SHORT_SHA
    
    # 创建并推送 manifest
    - buildah manifest create $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
    - buildah manifest add $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA $CI_REGISTRY_IMAGE:amd64-$CI_COMMIT_SHORT_SHA
    - buildah manifest add $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA $CI_REGISTRY_IMAGE:arm64-$CI_COMMIT_SHORT_SHA
    - buildah manifest push --all $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA docker://$CI_REGISTRY_IMAGE:latest
```

**验证多架构镜像**：

```bash
# 查看 manifest 支持的架构
podman manifest inspect myapp:latest | jq '.manifests[].platform'

# 拉取特定架构的镜像
podman pull --arch arm64 myapp:latest

# 在不同架构上运行（自动选择）
podman run myapp:latest  # 自动选择匹配当前架构的镜像
```

## 4. 镜像签名、策略与供应链

### 4.1 镜像签名机制

Podman 支持使用 GPG 签名来验证镜像完整性和来源。

**生成 GPG 密钥**：

```bash
# 生成 GPG 密钥对
gpg --full-generate-key

# 选择：
# (1) RSA and RSA (default)
# 4096 bits
# 有效期：0 = 永不过期
# 输入姓名和邮箱

# 列出密钥
gpg --list-keys

# 导出公钥
gpg --armor --export your@email.com > mykey.pub

# 导出私钥（小心保管！）
gpg --armor --export-secret-keys your@email.com > mykey.priv
```

**配置签名**：

```bash
# 创建签名配置目录
mkdir -p /etc/containers/registries.d/

# 配置默认签名策略
cat > /etc/containers/registries.d/default.yaml <<EOF
docker:
  registry.local:
    sigstore: file:///var/lib/containers/sigstore
    sigstore-staging: file:///var/lib/containers/sigstore
EOF

# 创建签名存储目录
sudo mkdir -p /var/lib/containers/sigstore
sudo chown -R $(whoami):$(whoami) /var/lib/containers/sigstore
```

**签名镜像**：

```bash
# 推送并签名镜像
podman push --sign-by your@email.com myapp:1.0 registry.local/myapp:1.0

# 或者分步操作
podman push myapp:1.0 registry.local/myapp:1.0
podman image sign --sign-by your@email.com registry.local/myapp:1.0

# 查看签名
ls /var/lib/containers/sigstore/

# 验证签名
podman image trust show
```

### 4.2 policy.json 策略配置

policy.json 定义了镜像拉取和运行的安全策略。

**policy.json 位置**：

- 系统级：`/etc/containers/policy.json`
- 用户级：`$HOME/.config/containers/policy.json`

**示例 policy.json**：

```json
{
  "default": [
    {
      "type": "insecureAcceptAnything"
    }
  ],
  "transports": {
    "docker": {
      "registry.local": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/containers/mykey.pub"
        }
      ],
      "docker.io": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/containers/docker-official.pub"
        }
      ],
      "quay.io": [
        {
          "type": "insecureAcceptAnything"
        }
      ]
    },
    "atomic": {
      "localhost:5000": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/containers/localhost.pub"
        }
      ]
    }
  }
}
```

**严格策略示例**：

```json
{
  "default": [
    {
      "type": "reject"
    }
  ],
  "transports": {
    "docker": {
      "registry.internal.company.com": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/containers/company-key.pub",
          "signedIdentity": {
            "type": "matchRepository"
          }
        }
      ],
      "docker.io/library": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/containers/docker-official.pub"
        }
      ]
    }
  }
}
```

**测试策略**：

```bash
# 测试策略配置
podman pull --policy-config=/path/to/policy.json registry.local/myapp:1.0

# 查看当前策略
cat /etc/containers/policy.json | jq .

# 验证策略生效
podman pull unsigned-image:latest  # 应该被拒绝
```

### 4.3 Sigstore 集成

Sigstore 是新一代的签名和验证系统，Podman 4.0+ 开始支持。

**使用 Sigstore Cosign**：

```bash
# 安装 cosign
# 方法1：使用包管理器
sudo dnf install cosign  # Fedora
sudo apt install cosign  # Ubuntu (需要添加仓库)

# 方法2：从 GitHub 下载
curl -sLO https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign

# 生成密钥对
cosign generate-key-pair

# 签名镜像（需先推送到仓库）
cosign sign --key cosign.key registry.local/myapp:1.0

# 验证签名
cosign verify --key cosign.pub registry.local/myapp:1.0

# 无密钥签名（使用 Fulcio/Rekor）
cosign sign registry.local/myapp:1.0  # 会打开浏览器进行 OIDC 认证

# 验证无密钥签名
cosign verify \
  --certificate-identity=your@email.com \
  --certificate-oidc-issuer=https://github.com/login/oauth \
  registry.local/myapp:1.0
```

**Podman 与 Cosign 集成**：

```bash
# 配置 containers policy.json 支持 Sigstore
cat > /etc/containers/policy.json <<EOF
{
  "default": [{"type": "reject"}],
  "transports": {
    "docker": {
      "registry.local": [
        {
          "type": "sigstoreSigned",
          "keyPath": "/path/to/cosign.pub",
          "signedIdentity": {
            "type": "matchRepository"
          }
        }
      ]
    }
  }
}
EOF

# 拉取时自动验证
podman pull registry.local/myapp:1.0
```

### 4.4 SBOM 与漏洞扫描

**生成 SBOM (Software Bill of Materials)**：

```bash
# 使用 syft 生成 SBOM
# 安装 syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# 生成 SPDX 格式 SBOM
syft packages myapp:1.0 -o spdx-json > sbom-spdx.json

# 生成 CycloneDX 格式 SBOM
syft packages myapp:1.0 -o cyclonedx-json > sbom-cyclonedx.json

# 直接扫描 Dockerfile
syft packages dir:. -o json > sbom.json

# 使用 buildah 集成 SBOM（未来功能）
# buildah bud --sbom=true -t myapp:1.0 .
```

**漏洞扫描**：

```bash
# 使用 trivy 扫描镜像
# 安装 trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# 扫描镜像
trivy image myapp:1.0

# 只显示高危和严重漏洞
trivy image --severity HIGH,CRITICAL myapp:1.0

# 生成 JSON 报告
trivy image -f json -o scan-report.json myapp:1.0

# 扫描 SBOM
trivy sbom sbom-spdx.json

# 使用 grype 扫描
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
grype myapp:1.0

# CI/CD 集成：扫描失败则退出
trivy image --exit-code 1 --severity CRITICAL myapp:1.0
```

**集成到构建流程**：

```bash
#!/bin/bash
# build-and-scan.sh

# 1. 构建镜像
buildah bud -t myapp:1.0 .

# 2. 生成 SBOM
syft packages myapp:1.0 -o spdx-json > sbom.json

# 3. 扫描漏洞
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:1.0

# 4. 签名镜像
cosign sign --key cosign.key myapp:1.0

# 5. 附加 SBOM 到镜像
cosign attach sbom --sbom sbom.json myapp:1.0

# 6. 推送到仓库
buildah push myapp:1.0 docker://registry.local/myapp:1.0

echo "构建、扫描、签名完成！"
```

## 5. skopeo 分发与复制

### 5.1 skopeo 基础操作

Skopeo 是一个用于操作容器镜像的命令行工具，无需运行 daemon。

**安装 skopeo**：

```bash
# Fedora/RHEL/CentOS
sudo dnf install skopeo

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install skopeo

# 验证安装
skopeo --version
```

**基本操作**：

```bash
# 查看远程镜像信息（无需下载）
skopeo inspect docker://docker.io/library/alpine:3.20

# 查看镜像标签列表
skopeo list-tags docker://docker.io/library/alpine

# 查看镜像层
skopeo inspect --raw docker://alpine:3.20 | jq '.layers'

# 删除远程镜像（需要权限）
skopeo delete docker://registry.local/myapp:old-version

# 同步镜像标签
skopeo sync --src docker --dest docker \
  docker.io/library/alpine registry.local/mirror/alpine
```

### 5.2 镜像复制与同步

**简单复制**：

```bash
# 从 Docker Hub 复制到私有仓库
skopeo copy \
  docker://docker.io/library/nginx:latest \
  docker://registry.local/nginx:latest

# 复制并修改标签
skopeo copy \
  docker://docker.io/library/nginx:1.25 \
  docker://registry.local/nginx:stable

# 从一个仓库复制到另一个仓库
skopeo copy \
  docker://registry-a.com/myapp:1.0 \
  docker://registry-b.com/myapp:1.0 \
  --src-creds user:pass \
  --dest-creds admin:secret
```

**批量同步**：

```bash
# 创建同步配置文件
cat > sync.yml <<EOF
docker.io:
  images:
    library/nginx:
      - latest
      - 1.25-alpine
    library/redis:
      - 7-alpine
      - latest
    library/postgres:
      - 15-alpine
EOF

# 执行同步
skopeo sync \
  --src yaml --dest docker \
  sync.yml registry.local/mirror \
  --dest-creds admin:password

# 同步整个仓库
skopeo sync \
  --src docker --dest docker \
  --src-registry-token=$(cat ~/.docker/config.json | jq -r '.auths["registry-a.com"].auth') \
  registry-a.com/myapp registry-b.com/backup
```

**使用目录同步（高级）**：

```yaml
# advanced-sync.yml
registry-a.com:
  tls-verify: true
  credentials:
    username: user
    password: pass
  images:
    company/app1: ["v1.0", "v1.1", "latest"]
    company/app2: ["stable"]
    
registry-b.com:
  tls-verify: false
  images-by-tag-regex:
    company/frontend: ^v[0-9]+\.[0-9]+$
```

### 5.3 air-gap 环境部署

Air-gap（离线）环境中的镜像分发策略：

**方法1：使用 OCI 目录格式**：

```bash
# 1. 在联网机器上导出镜像到目录
skopeo copy \
  docker://docker.io/library/nginx:latest \
  oci:nginx-oci:latest

# 批量导出
for image in nginx:latest redis:7-alpine postgres:15-alpine; do
  name=$(echo $image | cut -d: -f1)
  tag=$(echo $image | cut -d: -f2)
  skopeo copy docker://docker.io/library/$image oci:$name-oci:$tag
done

# 2. 打包目录
tar -czf offline-images.tar.gz *-oci/

# 3. 传输到离线环境（U盘、内网等）

# 4. 在离线环境解压并导入
tar -xzf offline-images.tar.gz
skopeo copy \
  oci:nginx-oci:latest \
  docker://registry.internal/nginx:latest \
  --dest-tls-verify=false
```

**方法2：使用 Docker archive 格式**：

```bash
# 导出为 Docker tar 格式
skopeo copy \
  docker://nginx:latest \
  docker-archive:nginx-latest.tar:nginx:latest

# 导入到私有仓库
skopeo copy \
  docker-archive:nginx-latest.tar \
  docker://registry.internal/nginx:latest
```

**方法3：使用 dir 格式（适合大量镜像）**：

```bash
# 导出到目录结构
skopeo copy \
  docker://nginx:latest \
  dir:/mnt/usb/images/nginx-latest

# 目录结构
/mnt/usb/images/nginx-latest/
├── manifest.json
├── config.json
├── layer1.tar
└── layer2.tar

# 导入
skopeo copy \
  dir:/mnt/usb/images/nginx-latest \
  docker://registry.internal/nginx:latest
```

**完整的 air-gap 分发脚本**：

```bash
#!/bin/bash
# export-images.sh - 在联网环境运行

IMAGES_FILE="images-list.txt"
OUTPUT_DIR="offline-images"
ARCHIVE_FILE="offline-images-$(date +%Y%m%d).tar.gz"

mkdir -p $OUTPUT_DIR

# 镜像列表
cat > $IMAGES_FILE <<EOF
docker.io/library/nginx:latest
docker.io/library/redis:7-alpine
docker.io/library/postgres:15-alpine
quay.io/prometheus/prometheus:latest
docker.io/grafana/grafana:latest
EOF

# 导出所有镜像
while IFS= read -r image; do
  echo "导出: $image"
  name=$(echo $image | sed 's|.*/||; s|:|-|')
  skopeo copy docker://$image oci:$OUTPUT_DIR/$name
done < $IMAGES_FILE

# 打包
tar -czf $ARCHIVE_FILE $OUTPUT_DIR/
echo "打包完成: $ARCHIVE_FILE"
echo "大小: $(du -h $ARCHIVE_FILE | cut -f1)"
```

```bash
#!/bin/bash
# import-images.sh - 在离线环境运行

ARCHIVE_FILE="offline-images-*.tar.gz"
REGISTRY="registry.internal"

# 解压
tar -xzf $ARCHIVE_FILE

# 导入所有镜像
for oci_dir in offline-images/*; do
  if [ -d "$oci_dir" ]; then
    image_name=$(basename $oci_dir | sed 's|-|:|')
    echo "导入: $image_name"
    skopeo copy \
      oci:$oci_dir \
      docker://$REGISTRY/$image_name \
      --dest-tls-verify=false
  fi
done

echo "导入完成！"
podman images
```

### 5.4 镜像格式转换

Skopeo 支持多种镜像格式互相转换：

```bash
# Docker 镜像 → OCI 格式
skopeo copy \
  docker://nginx:latest \
  oci:nginx-oci:latest

# OCI 格式 → Docker 镜像
skopeo copy \
  oci:nginx-oci:latest \
  docker://registry.local/nginx:latest

# Docker daemon → OCI 目录
skopeo copy \
  docker-daemon:nginx:latest \
  oci:nginx-oci:latest

# Docker archive → 私有仓库
skopeo copy \
  docker-archive:nginx.tar:nginx:latest \
  docker://registry.local/nginx:latest

# OCI 目录 → Docker archive
skopeo copy \
  oci:nginx-oci:latest \
  docker-archive:nginx-exported.tar:nginx:latest

# Podman 本地存储 → 仓库
skopeo copy \
  containers-storage:localhost/myapp:1.0 \
  docker://registry.local/myapp:1.0
```

**格式对比**：

| 格式 | 用途 | 优点 | 缺点 |
|------|------|------|------|
| `docker://` | 远程仓库 | 标准格式，广泛支持 | 需要网络 |
| `oci:` | OCI 目录 | 标准格式，可直接查看 | 占用空间较大 |
| `docker-archive:` | 单文件归档 | 便于传输 | 无法增量更新 |
| `dir:` | 原始目录 | 人类可读 | 不压缩 |
| `containers-storage:` | Podman本地 | 直接访问本地镜像 | 仅本地可用 |

## 6. 最佳实践与 FAQ

### 6.1 镜像构建最佳实践

**1. 使用最小化基础镜像**：

```dockerfile
# 推荐：使用 alpine 或 distroless
FROM alpine:3.20
RUN apk add --no-cache ca-certificates

# 更安全：使用 distroless
FROM gcr.io/distroless/static-debian12

# 最小：使用 scratch（仅适用于静态编译的二进制）
FROM scratch
COPY myapp /
ENTRYPOINT ["/myapp"]
```

**2. 多阶段构建减少镜像大小**：

```dockerfile
# 构建阶段
FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o app .

# 运行阶段（只包含二进制文件）
FROM alpine:3.20
COPY --from=builder /src/app /usr/local/bin/app
RUN apk add --no-cache ca-certificates
ENTRYPOINT ["/usr/local/bin/app"]
```

**3. 优化层顺序和大小**：

```dockerfile
# ❌ 不好：创建多个层
RUN apk add package1
RUN apk add package2
RUN apk add package3

# ✅ 好：合并为一层
RUN apk add --no-cache \
    package1 \
    package2 \
    package3

# ✅ 清理临时文件
RUN apk add --no-cache build-dependencies && \
    make build && \
    apk del build-dependencies && \
    rm -rf /tmp/*
```

**4. 使用 .containerignore**：

```text
# .containerignore
.git/
.github/
*.md
.vscode/
node_modules/
.env*
*.log
tmp/
test/
docs/
```

**5. 非 root 用户运行**：

```dockerfile
FROM alpine:3.20

# 创建用户
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# 设置工作目录权限
WORKDIR /app
RUN chown appuser:appuser /app

# 切换用户
USER appuser

# 复制应用
COPY --chown=appuser:appuser app /app/

ENTRYPOINT ["/app/app"]
```

### 6.2 安全最佳实践

**1. 签名所有生产镜像**：

```bash
# 在 CI/CD 中自动签名
buildah bud -t myapp:$VERSION .
buildah push --sign-by prod@company.com myapp:$VERSION docker://registry.local/myapp:$VERSION
```

**2. 实施严格的 policy.json**：

```json
{
  "default": [{"type": "reject"}],
  "transports": {
    "docker": {
      "registry.internal.company.com": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/containers/company.pub"
        }
      ]
    }
  }
}
```

**3. 定期扫描漏洞**：

```bash
# 每日自动扫描
#!/bin/bash
for image in $(podman images --format "{{.Repository}}:{{.Tag}}"); do
  echo "扫描: $image"
  trivy image --severity HIGH,CRITICAL $image
done
```

**4. 使用 rootless Podman**：

```bash
# 始终以非 root 用户运行 Podman
podman info | grep -i rootless  # 应显示 rootless: true
```

**5. 限制镜像来源**：

```bash
# /etc/containers/registries.conf
unqualified-search-registries = ["registry.internal.company.com"]

[[registry]]
location = "docker.io"
blocked = true  # 阻止直接从 Docker Hub 拉取

[[registry]]
location = "registry.internal.company.com"
insecure = false
```

### 6.3 性能优化

**1. 使用并行构建**：

```bash
# 同时构建多个架构（如果硬件支持）
buildah bud --arch amd64 -t myapp:amd64 . &
buildah bud --arch arm64 -t myapp:arm64 . &
wait
```

**2. 利用构建缓存**：

```bash
# 启用层缓存
buildah bud --layers -t myapp:1.0 .

# 在 CI/CD 中保存和恢复缓存
buildah bud --cache-from myapp:cache -t myapp:1.0 .
buildah push myapp:1.0 docker://registry.local/myapp:cache
```

**3. 优化基础镜像选择**：

```bash
# 选择合适的基础镜像大小
docker.io/library/ubuntu:22.04       # ~77MB
docker.io/library/alpine:3.20        # ~7MB
gcr.io/distroless/static-debian12    # ~2MB
scratch                              # 0MB (仅二进制)
```

**4. 使用镜像代理/缓存**：

```bash
# 配置本地 registry 缓存
[[registry]]
location = "docker.io"
[[registry.mirror]]
location = "registry-cache.internal:5000"
```

## 7. 实操示例

### 7.1 完整的多架构构建流程

```bash
#!/bin/bash
# multi-arch-build.sh
set -e

APP_NAME="myapp"
VERSION="1.0.0"
REGISTRY="registry.local"
ARCHS=("amd64" "arm64" "armv7")

echo "=== 开始多架构构建: $APP_NAME:$VERSION ==="

# 1. 为每个架构构建镜像
for arch in "${ARCHS[@]}"; do
  echo "构建 $arch 架构..."
  buildah bud \
    --arch $arch \
    --build-arg VERSION=$VERSION \
    -t $APP_NAME:$VERSION-$arch \
    -f Dockerfile .
done

# 2. 创建 manifest 列表
echo "创建 manifest 列表..."
buildah manifest create $APP_NAME:$VERSION

# 3. 添加各架构镜像到 manifest
for arch in "${ARCHS[@]}"; do
  echo "添加 $arch 到 manifest..."
  buildah manifest add $APP_NAME:$VERSION $APP_NAME:$VERSION-$arch
done

# 4. 推送 manifest 和所有架构镜像
echo "推送到仓库..."
buildah manifest push --all $APP_NAME:$VERSION docker://$REGISTRY/$APP_NAME:$VERSION
buildah manifest push --all $APP_NAME:$VERSION docker://$REGISTRY/$APP_NAME:latest

# 5. 验证
echo "验证 manifest..."
skopeo inspect docker://$REGISTRY/$APP_NAME:$VERSION | jq '.manifests[].platform'

echo "=== 构建完成！==="
echo "镜像: $REGISTRY/$APP_NAME:$VERSION"
echo "支持架构: ${ARCHS[@]}"
```

### 7.2 镜像仓库同步

```bash
#!/bin/bash
# mirror-sync.sh - 同步外部镜像到内部仓库

SOURCE_REGISTRY="docker.io"
TARGET_REGISTRY="registry.internal"
LOG_FILE="sync-$(date +%Y%m%d-%H%M%S).log"

# 镜像列表
IMAGES=(
  "library/nginx:latest"
  "library/nginx:1.25-alpine"
  "library/redis:7-alpine"
  "library/postgres:15-alpine"
  "library/mysql:8-debian"
)

echo "开始同步镜像..." | tee -a $LOG_FILE

for image in "${IMAGES[@]}"; do
  source="docker://$SOURCE_REGISTRY/$image"
  target="docker://$TARGET_REGISTRY/$image"
  
  echo "同步: $image" | tee -a $LOG_FILE
  
  if skopeo copy $source $target --dest-tls-verify=false 2>&1 | tee -a $LOG_FILE; then
    echo "✓ 成功: $image" | tee -a $LOG_FILE
  else
    echo "✗ 失败: $image" | tee -a $LOG_FILE
  fi
done

echo "同步完成！日志: $LOG_FILE" | tee -a $LOG_FILE
```

### 7.3 镜像签名与验证

```bash
#!/bin/bash
# sign-and-verify.sh

IMAGE="myapp:1.0"
REGISTRY="registry.local"
GPG_KEY="build@company.com"

echo "=== 镜像签名与验证流程 ==="

# 1. 构建镜像
echo "1. 构建镜像..."
buildah bud -t $IMAGE .

# 2. 生成 SBOM
echo "2. 生成 SBOM..."
syft packages $IMAGE -o spdx-json > sbom.json

# 3. 扫描漏洞
echo "3. 扫描漏洞..."
if trivy image --severity HIGH,CRITICAL --exit-code 1 $IMAGE; then
  echo "✓ 漏洞扫描通过"
else
  echo "✗ 发现高危漏洞，中止发布"
  exit 1
fi

# 4. 推送镜像
echo "4. 推送镜像..."
buildah push $IMAGE docker://$REGISTRY/$IMAGE

# 5. 签名镜像
echo "5. 签名镜像..."
podman image sign --sign-by $GPG_KEY docker://$REGISTRY/$IMAGE

# 6. 使用 cosign 签名（可选）
echo "6. Cosign 签名..."
cosign sign --key cosign.key $REGISTRY/$IMAGE

# 7. 附加 SBOM
echo "7. 附加 SBOM..."
cosign attach sbom --sbom sbom.json $REGISTRY/$IMAGE

echo "=== 完成！==="

# 验证
echo "验证签名..."
podman image trust show
cosign verify --key cosign.pub $REGISTRY/$IMAGE
```

## 8. 故障清单与排查

**问题1：构建缓存失效**:

```bash
# 症状：每次构建都重新执行所有步骤

# 排查：
# 1. 检查层顺序
buildah bud --layers -t myapp:1.0 .

# 2. 查看缓存
buildah images --all

# 3. 检查上下文变更
# 确保 .containerignore 排除了频繁变更的文件

# 解决方案：
# - 优化 Dockerfile 层顺序（变更少的放前面）
# - 使用 .containerignore
# - 清理并重建：buildah bud --no-cache -t myapp:1.0 .
```

**问题2：签名策略阻断拉取**:

```bash
# 症状：Error: Source image rejected: Running image docker://... is rejected by policy

# 排查：
# 1. 检查 policy.json
cat /etc/containers/policy.json

# 2. 查看签名信息
podman image trust show

# 3. 验证 GPG 密钥
gpg --list-keys

# 解决方案：
# - 临时：使用 --policy-config 指定宽松策略
podman pull --policy-config=/tmp/permissive-policy.json myimage

# - 永久：更新 policy.json 添加仓库信任
# 或者对镜像进行签名
```

**问题3：多架构镜像构建失败**:

```bash
# 症状：Error: exec format error 或 unsupported architecture

# 排查：
# 1. 检查 QEMU 支持
ls /proc/sys/fs/binfmt_misc/

# 2. 验证支持的架构
buildah info | grep -i arch

# 解决方案：
# - 安装 qemu-user-static
sudo dnf install qemu-user-static
# 或
sudo apt-get install qemu-user-static

# - 在原生架构上构建
```

**问题4：推送失败**:

```bash
# 症状：Error: authentication required / connection timeout

# 排查：
# 1. 检查认证
podman login registry.local

# 2. 检查网络
ping registry.local
curl -v https://registry.local/v2/

# 3. 检查镜像大小和网络
podman images --format "{{.Repository}}:{{.Tag}} {{.Size}}"

# 解决方案：
# - 重新登录
podman logout registry.local
podman login -u user -p pass registry.local

# - 调整网络 MTU
podman push --tls-verify=false myapp:1.0 registry.local/myapp:1.0

# - 增加超时
export PODMAN_TIMEOUT=600
```

**问题5：Rootless 权限问题**:

```bash
# 症状：Permission denied 或 operation not permitted

# 排查：
# 1. 检查 subuid/subgid
cat /etc/subuid
cat /etc/subgid

# 2. 检查用户映射
podman unshare cat /proc/self/uid_map

# 解决方案：
# - 确保用户有 subuid/subgid 配置
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER

# - 重新登录使配置生效
podman system migrate

# - 检查文件权限
podman unshare chown -R 0:0 /path/to/files
```

## 9. FAQ

**Q1: buildah 与 Dockerfile 兼容性如何？**

A: Buildah 完全兼容 Dockerfile 语法（通过 `buildah bud` 命令）。同时，buildah 还支持更细粒度的命令集，允许你用脚本方式构建镜像，提供了比 Dockerfile 更大的灵活性。

```bash
# 使用 Dockerfile
buildah bud -t myapp:1.0 .

# 或使用命令式构建
container=$(buildah from alpine:3.20)
buildah run $container -- apk add nginx
buildah commit $container myapp:1.0
```

**Q2: 如何生成 SBOM？**

A: 推荐使用 Syft 工具在 CI/CD 中生成并附加 SBOM：

```bash
# 生成 SBOM
syft packages myapp:1.0 -o spdx-json > sbom.json

# 使用 Cosign 附加到镜像
cosign attach sbom --sbom sbom.json registry.local/myapp:1.0

# 或使用 Buildah（未来版本）
buildah bud --sbom=true -t myapp:1.0 .
```

**Q3: rootless 模式有什么限制？**

A: 主要限制包括：

1. 不能绑定 < 1024 的端口（可用端口映射解决）
2. 某些存储驱动功能受限（推荐 overlay）
3. 网络性能可能略有下降（可用 pasta 改善）
4. 不能使用某些内核功能

但安全优势远大于这些限制，推荐在生产环境使用。

**Q4: 多架构镜像如何选择合适的架构？**

A: Podman 和 Docker 会自动根据当前系统架构选择匹配的镜像。你也可以手动指定：

```bash
# 自动选择
podman pull myapp:latest

# 手动指定
podman pull --arch arm64 myapp:latest
podman run --arch amd64 myapp:latest
```

**Q5: skopeo 和 podman 有什么区别？**

A:

- **Podman**: 完整的容器运行时，可以构建、运行、管理容器
- **Skopeo**: 专注于镜像操作（检查、复制、删除），无需 daemon，不能运行容器

通常组合使用：

- 使用 buildah 构建镜像
- 使用 skopeo 分发镜像
- 使用 podman 运行容器

**Q6: 如何在 CI/CD 中使用 Buildah？**

A: 示例 GitLab CI 配置：

```yaml
build:
  image: quay.io/buildah/stable:latest
  script:
    - buildah bud -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA .
    - buildah push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
  tags:
    - docker
```

**Q7: 如何处理私有 CA 证书？**

A:

```bash
# 添加 CA 证书
sudo cp my-ca.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust

# 或在容器构建时
COPY my-ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Skopeo 跳过 TLS 验证（仅测试用）
skopeo copy --src-tls-verify=false docker://registry.local/myapp:1.0 oci:myapp
```

**Q8: 如何优化镜像大小？**

A: 最佳实践：

1. 使用 alpine 或 distroless 基础镜像
2. 多阶段构建，只保留必要文件
3. 合并 RUN 命令，减少层数
4. 清理临时文件和缓存
5. 使用 .containerignore

```dockerfile
FROM golang:1.22-alpine AS builder
RUN go build -ldflags="-s -w" -o app .

FROM gcr.io/distroless/static-debian12
COPY --from=builder /app /
ENTRYPOINT ["/app"]
```

**Q9: 镜像签名是必须的吗？**

A: 对于生产环境强烈推荐：

- 防止供应链攻击
- 确保镜像完整性
- 合规性要求（如 SLSA）
- 可追溯性

开发环境可以放宽策略，但生产环境应强制签名验证。

**Q10: 如何处理大型镜像传输？**

A:

```bash
# 1. 使用压缩
buildah push --compression-format gzip myapp:1.0 docker://registry.local/myapp:1.0

# 2. 分块传输
skopeo copy --dest-compress docker://source/myapp:1.0 docker://dest/myapp:1.0

# 3. 使用 OCI 目录（便于增量传输）
skopeo copy docker://myapp:1.0 oci:myapp-oci
rsync -avz myapp-oci/ remote:/path/
skopeo copy oci:/path/myapp-oci docker://registry.local/myapp:1.0

# 4. 并行推送层
buildah push --parallel myapp:1.0 docker://registry.local/myapp:1.0
```

---

**相关资源**：

- [Buildah 官方文档](https://buildah.io/)
- [Skopeo GitHub](https://github.com/containers/skopeo)
- [Podman 官方文档](https://docs.podman.io/)
- [OCI 镜像规范](https://github.com/opencontainers/image-spec)
- [Sigstore 项目](https://www.sigstore.dev/)
- [Syft SBOM 工具](https://github.com/anchore/syft)
- [Trivy 安全扫描](https://github.com/aquasecurity/trivy)
