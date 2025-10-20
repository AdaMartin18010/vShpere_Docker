# Docker安全与最佳实践

> **返回**: [Docker部署目录](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Docker安全与最佳实践](#docker安全与最佳实践)
  - [📋 目录](#-目录)
  - [1. 容器安全概述](#1-容器安全概述)
  - [2. 镜像安全](#2-镜像安全)
  - [3. 容器运行时安全](#3-容器运行时安全)
  - [4. 网络安全](#4-网络安全)
  - [5. 资源限制与隔离](#5-资源限制与隔离)
  - [6. 安全扫描与审计](#6-安全扫描与审计)
  - [7. Seccomp与AppArmor](#7-seccomp与apparmor)
  - [8. 密钥管理](#8-密钥管理)
  - [9. 生产环境最佳实践](#9-生产环境最佳实践)
  - [10. 安全检查清单](#10-安全检查清单)
  - [11. 零信任安全架构](#11-零信任安全架构)
    - [11.1 实施OPA策略](#111-实施opa策略)
    - [11.2 使用Falco进行运行时检测](#112-使用falco进行运行时检测)
  - [12. 供应链安全进阶](#12-供应链安全进阶)
    - [12.1 实施SLSA构建](#121-实施slsa构建)
  - [13. 合规性框架](#13-合规性框架)
    - [13.1 自动化合规检查](#131-自动化合规检查)
  - [14. 2025容器安全趋势](#14-2025容器安全趋势)
  - [相关文档](#相关文档)

---

## 1. 容器安全概述

```yaml
Container_Security_Overview:
  安全挑战:
    镜像安全:
      - 基础镜像漏洞
      - 恶意镜像
      - 敏感信息泄露
      - 供应链攻击
    
    运行时安全:
      - 特权容器
      - 容器逃逸
      - 资源滥用
      - 不当配置
    
    网络安全:
      - 未授权访问
      - 中间人攻击
      - DDoS攻击
      - 数据泄露
    
    主机安全:
      - 内核漏洞
      - Docker守护进程暴露
      - 文件系统攻击
  
  安全层级:
    Level 1 - 主机安全:
      - 操作系统加固
      - 内核安全
      - Docker守护进程安全
      - 审计日志
    
    Level 2 - 镜像安全:
      - 可信镜像源
      - 漏洞扫描
      - 镜像签名
      - 定期更新
    
    Level 3 - 运行时安全:
      - 非root用户
      - 只读文件系统
      - 资源限制
      - 能力限制
    
    Level 4 - 网络安全:
      - 网络隔离
      - 加密通信
      - 访问控制
      - 流量监控
    
    Level 5 - 应用安全:
      - 输入验证
      - 身份认证
      - 授权控制
      - 数据加密
  
  安全原则:
    最小权限原则:
      - 只授予必要权限
      - 禁用不需要的能力
      - 限制系统调用
    
    深度防御:
      - 多层安全措施
      - 失败安全设计
      - 冗余保护
    
    默认安全:
      - 安全的默认配置
      - 最小化攻击面
      - 及时更新
```

---

## 2. 镜像安全

```yaml
Image_Security:
  选择基础镜像:
    ✅ 使用官方镜像:
      - Docker Hub官方镜像
      - 经过验证和维护
      - 及时更新
    
    ✅ 使用最小化镜像:
      - Alpine (5MB)
      - Distroless
      - Scratch
    
    ✅ 指定明确版本:
      FROM nginx:1.21.6-alpine
      # 避免: FROM nginx:latest
    
    ❌ 避免:
      - 不明来源镜像
      - 未维护的镜像
      - latest标签
  
  Dockerfile安全实践:
    ✅ 使用非root用户:
      dockerfile
      FROM alpine:3.18
      RUN addgroup -S appgroup && adduser -S appuser -G appgroup
      USER appuser
    
    ✅ 最小化层数:
      dockerfile
      RUN apk add --no-cache \
          curl \
          wget && \
          rm -rf /tmp/*
    
    ✅ 不包含敏感信息:
      # 不要这样
      ENV API_KEY=sk_live_123456
      
      # 使用运行时注入
      ENV API_KEY=${API_KEY}
    
    ✅ 使用COPY而不是ADD:
      COPY --chown=appuser:appgroup app.jar /app/
    
    ✅ 设置健康检查:
      HEALTHCHECK CMD wget -qO- http://localhost/health || exit 1
    
    ❌ 避免:
      - 运行不必要的服务
      - 安装调试工具到生产镜像
      - 暴露不需要的端口
  
  漏洞扫描:
    工具:
      - Trivy (推荐)
      - Clair
      - Anchore
      - Snyk
      - Docker Scout
    
    扫描流程:
      1. 构建后扫描
      2. 推送前扫描
      3. 定期重新扫描
      4. CI/CD集成
    
    示例:
      bash
      # Trivy扫描
      trivy image --severity HIGH,CRITICAL myapp:v1.0
      
      # CI/CD集成
      trivy image --exit-code 1 --severity CRITICAL myapp:v1.0
```

**镜像安全示例**:

```dockerfile
# ========================================
# 安全的Dockerfile示例 - Node.js应用
# ========================================

# 阶段1: 构建
FROM node:18-alpine AS builder

# 使用非root用户构建
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /build

# 只复制必要文件 (利用缓存)
COPY --chown=nodejs:nodejs package*.json ./
RUN npm ci --only=production

COPY --chown=nodejs:nodejs . .
RUN npm run build

# 阶段2: 运行
FROM node:18-alpine

# 安装安全更新
RUN apk update && \
    apk upgrade && \
    apk add --no-cache dumb-init && \
    rm -rf /var/cache/apk/*

# 创建非root用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /app

# 从构建阶段复制文件
COPY --from=builder --chown=nodejs:nodejs /build/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /build/dist ./dist

# 只读文件系统 (需要可写目录)
RUN mkdir /tmp/app-temp && \
    chown nodejs:nodejs /tmp/app-temp

# 切换到非root用户
USER nodejs

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

# 暴露端口
EXPOSE 3000

# 使用dumb-init处理信号
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/main.js"]
```

---

## 3. 容器运行时安全

```yaml
Runtime_Security:
  非特权运行:
    ✅ 使用非root用户:
      # Dockerfile
      USER 1000:1000
      
      # docker run
      docker run --user 1000:1000 myapp
    
    ✅ 禁用特权模式:
      # ❌ 不要这样
      docker run --privileged myapp
      
      # ✅ 只授予需要的能力
      docker run --cap-add=NET_ADMIN myapp
    
    ✅ 删除所有能力后添加需要的:
      docker run \
        --cap-drop=ALL \
        --cap-add=NET_BIND_SERVICE \
        myapp
  
  Linux Capabilities:
    默认能力 (Docker默认授予):
      - CHOWN
      - DAC_OVERRIDE
      - FSETID
      - FOWNER
      - MKNOD
      - NET_RAW
      - SETGID
      - SETUID
      - SETFCAP
      - SETPCAP
      - NET_BIND_SERVICE
      - SYS_CHROOT
      - KILL
      - AUDIT_WRITE
    
    危险能力 (应该删除):
      - SYS_ADMIN (几乎等同于root)
      - NET_ADMIN (网络管理)
      - SYS_MODULE (加载内核模块)
      - SYS_RAWIO (原始IO)
      - SYS_PTRACE (跟踪进程)
    
    示例:
      bash
      # 最小权限
      docker run \
        --cap-drop=ALL \
        --cap-add=NET_BIND_SERVICE \
        nginx
  
  只读容器:
    ✅ 只读根文件系统:
      docker run --read-only myapp
    
    ✅ 挂载临时目录为可写:
      docker run \
        --read-only \
        --tmpfs /tmp \
        --tmpfs /var/run \
        myapp
  
  安全选项:
    no-new-privileges:
      # 防止进程获取新权限
      docker run --security-opt=no-new-privileges:true myapp
    
    AppArmor/SELinux:
      # AppArmor
      docker run --security-opt apparmor=docker-default myapp
      
      # SELinux
      docker run --security-opt label=type:container_runtime_t myapp
  
  资源限制:
    CPU限制:
      # 限制CPU份额
      docker run --cpus=".5" myapp
      
      # 限制CPU核心
      docker run --cpuset-cpus="0,1" myapp
    
    内存限制:
      # 限制内存
      docker run --memory="512m" --memory-swap="1g" myapp
      
      # OOM分数
      docker run --oom-score-adj=500 myapp
    
    IO限制:
      # 限制块设备读写
      docker run --device-read-bps=/dev/sda:1mb myapp
      docker run --device-write-bps=/dev/sda:1mb myapp
```

**安全运行容器示例**:

```bash
#!/bin/bash
# ========================================
# 安全运行容器脚本
# ========================================

docker run -d \
  --name secure-app \
  \
  # 用户和权限
  --user 1000:1000 \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt=no-new-privileges:true \
  \
  # 文件系统
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --tmpfs /var/run:rw,noexec,nosuid,size=50m \
  -v /app/data:/data:ro \
  \
  # 资源限制
  --memory="512m" \
  --memory-swap="512m" \
  --cpus="0.5" \
  --pids-limit=100 \
  \
  # 网络
  --network=app-network \
  --dns=8.8.8.8 \
  \
  # 日志
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  \
  # 健康检查
  --health-cmd="wget -qO- http://localhost/health || exit 1" \
  --health-interval=30s \
  --health-timeout=3s \
  --health-retries=3 \
  \
  myapp:v1.0
```

---

## 4. 网络安全

```yaml
Network_Security:
  网络隔离:
    ✅ 使用自定义网络:
      # 创建网络
      docker network create --driver bridge app-network
      
      # 使用网络
      docker run --network=app-network myapp
    
    ✅ 多网络隔离:
      # 前端网络
      docker network create frontend
      # 后端网络
      docker network create backend --internal
      
      # Web服务器连接两个网络
      docker run --network=frontend --network=backend nginx
    
    ❌ 避免使用host网络:
      # 不推荐
      docker run --network=host myapp
  
  端口管理:
    ✅ 只暴露必要端口:
      docker run -p 8080:8080 myapp
    
    ✅ 绑定到特定IP:
      docker run -p 127.0.0.1:8080:8080 myapp
    
    ❌ 避免暴露所有端口:
      # 不推荐
      docker run -P myapp
  
  加密通信:
    TLS/SSL:
      # 使用TLS证书
      docker run \
        -v /etc/ssl/certs:/etc/ssl/certs:ro \
        -e SSL_CERT_FILE=/etc/ssl/certs/ca-cert.pem \
        myapp
    
    服务间加密:
      # 使用mTLS
      - Istio Service Mesh
      - Linkerd
      - Consul Connect
  
  防火墙规则:
    iptables:
      bash
      # 只允许特定IP访问
      iptables -A DOCKER-USER -i ext_if ! -s 192.168.1.0/24 -j DROP
      
      # 限制出站流量
      iptables -A DOCKER-USER -o ext_if -d 10.0.0.0/8 -j DROP
```

---

## 5. 资源限制与隔离

```bash
# ========================================
# 资源限制最佳实践
# ========================================

# CPU限制
docker run \
  --cpus="1.5" \          # 限制1.5个CPU
  --cpu-shares=1024 \     # CPU份额
  --cpuset-cpus="0-1" \   # 绑定CPU核心
  myapp

# 内存限制
docker run \
  --memory="1g" \         # 内存限制
  --memory-swap="2g" \    # 内存+Swap限制
  --memory-reservation="512m" \  # 软限制
  --oom-kill-disable \    # 禁用OOM Kill (慎用)
  myapp

# IO限制
docker run \
  --device-read-bps=/dev/sda:10mb \
  --device-write-bps=/dev/sda:10mb \
  --device-read-iops=/dev/sda:1000 \
  --device-write-iops=/dev/sda:1000 \
  myapp

# 进程数限制
docker run --pids-limit=200 myapp

# 文件描述符限制
docker run \
  --ulimit nofile=1024:2048 \
  --ulimit nproc=512 \
  myapp
```

**Compose资源限制**:

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    ulimits:
      nofile:
        soft: 20000
        hard: 40000
      nproc: 512
```

---

## 6. 安全扫描与审计

```bash
# ========================================
# Trivy全面扫描
# ========================================

# 扫描镜像漏洞
trivy image nginx:latest

# 只显示HIGH和CRITICAL
trivy image --severity HIGH,CRITICAL nginx:latest

# 输出JSON格式
trivy image -f json -o results.json nginx:latest

# 扫描并在发现CRITICAL漏洞时失败
trivy image --exit-code 1 --severity CRITICAL myapp:v1.0

# 扫描Dockerfile
trivy config Dockerfile

# 扫描Kubernetes manifests
trivy config k8s/

# 扫描文件系统
trivy fs /path/to/project

# ========================================
# Docker Bench Security
# ========================================

# 运行Docker安全基准测试
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
  -v /etc:/etc:ro \
  -v /usr/bin/containerd:/usr/bin/containerd:ro \
  -v /usr/bin/runc:/usr/bin/runc:ro \
  -v /usr/lib/systemd:/usr/lib/systemd:ro \
  -v /var/lib:/var/lib:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --label docker_bench_security \
  docker/docker-bench-security
```

---

## 7. Seccomp与AppArmor

```yaml
Seccomp_AppArmor:
  Seccomp (Secure Computing Mode):
    概述:
      - Linux内核特性
      - 限制系统调用
      - 减少攻击面
    
    Docker默认Profile:
      - 禁用约44个危险系统调用
      - clone, mount, umount, reboot, etc.
    
    自定义Profile:
      json
      {
        "defaultAction": "SCMP_ACT_ERRNO",
        "architectures": ["SCMP_ARCH_X86_64"],
        "syscalls": [
          {
            "names": ["read", "write", "open", "close"],
            "action": "SCMP_ACT_ALLOW"
          }
        ]
      }
    
    使用:
      bash
      # 使用默认profile
      docker run --security-opt seccomp=default.json myapp
      
      # 禁用seccomp (不推荐)
      docker run --security-opt seccomp=unconfined myapp
  
  AppArmor:
    概述:
      - Linux安全模块
      - 强制访问控制
      - 限制程序权限
    
    Docker默认Profile:
      - docker-default
      - 限制文件访问
      - 限制网络操作
      - 限制能力
    
    自定义Profile:
      bash
      # /etc/apparmor.d/docker-nginx
      #include <tunables/global>
      
      profile docker-nginx flags=(attach_disconnected,mediate_deleted) {
        #include <abstractions/base>
        
        network inet tcp,
        network inet udp,
        network inet icmp,
        
        deny @{PROC}/* w,
        deny /sys/[^f]*/** wklx,
        deny /sys/f[^s]*/** wklx,
        deny /sys/fs/[^c]*/** wklx,
        deny /sys/fs/c[^g]*/** wklx,
        deny /sys/fs/cg[^r]*/** wklx,
        
        capability chown,
        capability setuid,
        capability setgid,
        
        /usr/sbin/nginx ix,
        /var/log/nginx/* w,
      }
    
    使用:
      bash
      # 加载profile
      sudo apparmor_parser -r /etc/apparmor.d/docker-nginx
      
      # 使用profile
      docker run --security-opt apparmor=docker-nginx nginx
```

---

## 8. 密钥管理

```yaml
Secrets_Management:
  ❌ 不安全的做法:
    # 硬编码在Dockerfile
    ENV DB_PASSWORD=password123
    
    # 明文在docker-compose.yml
    environment:
      - DB_PASSWORD=password123
    
    # 提交到Git
    git add .env
  
  ✅ 推荐做法:
    Docker Secrets (Swarm):
      bash
      # 创建secret
      echo "mypassword" | docker secret create db_password -
      
      # 使用secret
      docker service create \
        --name myapp \
        --secret db_password \
        myapp:latest
      
      # 在容器中访问
      # /run/secrets/db_password
    
    环境变量:
      bash
      # 运行时注入
      docker run -e DB_PASSWORD=$DB_PASSWORD myapp
      
      # 从文件读取
      docker run --env-file .env.prod myapp
    
    外部密钥管理:
      - HashiCorp Vault
      - AWS Secrets Manager
      - Azure Key Vault
      - Google Secret Manager
    
    Kubernetes Secrets:
      yaml
      apiVersion: v1
      kind: Secret
      metadata:
        name: db-secret
      type: Opaque
      data:
        password: cGFzc3dvcmQxMjM=
```

**Vault集成示例**:

```bash
# ========================================
# HashiCorp Vault集成
# ========================================

# 1. 启动Vault
docker run -d \
  --name vault \
  --cap-add=IPC_LOCK \
  -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' \
  vault:latest

# 2. 存储密钥
docker exec vault vault kv put secret/myapp \
  db_password=password123 \
  api_key=sk_live_123456

# 3. 应用读取密钥
# 在应用中使用Vault SDK
export VAULT_ADDR='http://vault:8200'
export VAULT_TOKEN='myroot'

# Node.js示例
const vault = require('node-vault')({
  endpoint: process.env.VAULT_ADDR,
  token: process.env.VAULT_TOKEN
});

const secrets = await vault.read('secret/data/myapp');
const dbPassword = secrets.data.data.db_password;
```

---

## 9. 生产环境最佳实践

```yaml
Production_Best_Practices:
  镜像管理:
    ✅ 使用私有仓库:
      - Harbor
      - AWS ECR
      - Azure ACR
      - Google GCR
    
    ✅ 镜像签名:
      - Docker Content Trust
      - Cosign
      - Notary
    
    ✅ 漏洞扫描:
      - 构建时扫描
      - 定期重新扫描
      - 阻止高危镜像
    
    ✅ 版本管理:
      - 语义化版本
      - 避免latest
      - 保留历史版本
  
  部署安全:
    ✅ 最小权限:
      - 非root用户
      - 删除不必要能力
      - 只读文件系统
    
    ✅ 网络隔离:
      - 自定义网络
      - 内部网络
      - 防火墙规则
    
    ✅ 资源限制:
      - CPU限制
      - 内存限制
      - IO限制
      - 进程数限制
    
    ✅ 日志管理:
      - 集中式日志
      - 日志轮转
      - 敏感信息脱敏
  
  监控审计:
    ✅ 容器监控:
      - Prometheus + cAdvisor
      - Grafana Dashboard
      - 告警规则
    
    ✅ 安全审计:
      - 审计日志
      - 异常检测
      - 入侵检测
    
    ✅ 合规检查:
      - CIS Docker Benchmark
      - PCI DSS
      - HIPAA
  
  备份恢复:
    ✅ 数据备份:
      - 卷备份
      - 数据库备份
      - 配置备份
    
    ✅ 灾难恢复:
      - 恢复流程
      - 定期演练
      - RTO/RPO目标
```

---

## 10. 安全检查清单

```yaml
Security_Checklist:
  镜像安全:
    ☑ 使用官方或可信基础镜像
    ☑ 指定明确的镜像版本
    ☑ 使用最小化基础镜像
    ☑ 定期更新基础镜像
    ☑ 扫描镜像漏洞
    ☑ 不在镜像中存储敏感信息
    ☑ 使用多阶段构建
    ☑ 最小化镜像层数
    ☑ 签名镜像
  
  运行时安全:
    ☑ 使用非root用户运行
    ☑ 只读根文件系统
    ☑ 删除所有能力后添加必要的
    ☑ 禁用特权模式
    ☑ 启用no-new-privileges
    ☑ 使用Seccomp/AppArmor
    ☑ 设置资源限制
    ☑ 限制进程数
  
  网络安全:
    ☑ 使用自定义网络
    ☑ 网络隔离
    ☑ 只暴露必要端口
    ☑ 绑定到特定IP
    ☑ 使用TLS/SSL
    ☑ 配置防火墙规则
  
  数据安全:
    ☑ 使用卷持久化数据
    ☑ 加密敏感数据
    ☑ 使用密钥管理系统
    ☑ 定期备份
    ☑ 限制卷权限
  
  监控审计:
    ☑ 启用审计日志
    ☑ 集中式日志管理
    ☑ 资源监控
    ☑ 安全事件告警
    ☑ 定期安全审计
  
  合规性:
    ☑ 遵循CIS Docker Benchmark
    ☑ 定期扫描合规性
    ☑ 文档化安全策略
    ☑ 安全培训
    ☑ 事件响应计划
```

**自动化安全检查脚本**:

```bash
#!/bin/bash
# ========================================
# Docker安全自动化检查脚本
# ========================================

set -e

echo "===== Docker安全检查 ====="

# 1. Docker版本
echo -e "\n➤ Docker版本:"
docker version --format '{{.Server.Version}}'

# 2. 运行Docker Bench Security
echo -e "\n➤ 运行Docker Bench Security..."
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -v /etc:/etc:ro \
  -v /var/lib:/var/lib:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  docker/docker-bench-security

# 3. 检查特权容器
echo -e "\n➤ 检查特权容器:"
PRIVILEGED=$(docker ps --filter "label=privileged=true" -q)
if [ -z "$PRIVILEGED" ]; then
  echo "✅ 没有特权容器"
else
  echo "⚠️  发现特权容器:"
  docker ps --filter "label=privileged=true"
fi

# 4. 检查以root运行的容器
echo -e "\n➤ 检查以root运行的容器:"
for container in $(docker ps -q); do
  USER=$(docker inspect --format='{{.Config.User}}' $container)
  if [ -z "$USER" ] || [ "$USER" == "root" ] || [ "$USER" == "0" ]; then
    NAME=$(docker inspect --format='{{.Name}}' $container)
    echo "⚠️  容器 $NAME 以root运行"
  fi
done

# 5. 扫描所有镜像
echo -e "\n➤ 扫描镜像漏洞:"
for image in $(docker images --format "{{.Repository}}:{{.Tag}}"); do
  echo "扫描 $image..."
  trivy image --severity HIGH,CRITICAL --quiet $image
done

echo -e "\n✅ 安全检查完成！"
```

---

## 11. 零信任安全架构

```yaml
Zero_Trust_Security:
  原则:
    - 永不信任，始终验证
    - 最小权限原则
    - 微隔离
    - 持续验证
  
  实施策略:
    1_身份验证:
      容器身份:
        - 使用Workload Identity
        - mTLS认证
        - 服务账户令牌
      
      用户身份:
        - 多因素认证(MFA)
        - RBAC权限控制
        - API密钥轮换
    
    2_网络隔离:
      微隔离:
        - NetworkPolicy
        - 服务网格(Istio/Linkerd)
        - 防火墙规则
      
      加密通信:
        - TLS 1.3
        - mTLS (双向TLS)
        - IPsec
    
    3_访问控制:
      最小权限:
        - Drop所有Capabilities
        - 只读文件系统
        - 非root用户
        - SELinux/AppArmor
      
      动态授权:
        - OPA (Open Policy Agent)
        - 动态策略评估
        - 上下文感知授权
    
    4_监控审计:
      实时监控:
        - Falco运行时检测
        - Auditd系统审计
        - 日志聚合分析
      
      异常检测:
        - 行为基线
        - 机器学习检测
        - 自动响应
```

### 11.1 实施OPA策略

```bash
#!/bin/bash
# Open Policy Agent (OPA) 策略示例

# 1. 安装OPA
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
sudo mv opa /usr/local/bin/

# 2. 编写Rego策略 (policy.rego)
cat > policy.rego <<'EOF'
package docker.authz

# 默认拒绝
default allow = false

# 允许非特权容器
allow {
    not input.Privileged
    not has_capability("SYS_ADMIN")
}

# 拒绝挂载敏感路径
deny[msg] {
    volume := input.Volumes[_]
    startswith(volume, "/")
    sensitive_paths := ["/etc", "/sys", "/proc"]
    sensitive := sensitive_paths[_]
    startswith(volume, sensitive)
    msg := sprintf("不允许挂载敏感路径: %v", [volume])
}

# 拒绝以root运行
deny[msg] {
    input.User == "root"
    msg := "不允许以root用户运行容器"
}

# 检查Capability
has_capability(cap) {
    input.CapAdd[_] == cap
}
EOF

# 3. 测试策略
opa test policy.rego
```

### 11.2 使用Falco进行运行时检测

```bash
#!/bin/bash
# Falco运行时安全监控

# 1. 安装Falco
curl -s https://falco.org/repo/falcosecurity-3672BA8F.asc | apt-key add -
echo "deb https://download.falco.org/packages/deb stable main" | tee -a /etc/apt/sources.list.d/falcosecurity.list
apt-get update
apt-get install -y falco

# 2. 自定义规则 (/etc/falco/rules.d/custom_rules.yaml)
cat > /etc/falco/rules.d/custom_rules.yaml <<'EOF'
- rule: Unauthorized Process in Container
  desc: Detect unauthorized process execution
  condition: >
    spawned_process and
    container and
    not proc.name in (nginx, node, python, java)
  output: >
    Unauthorized process started in container
    (user=%user.name command=%proc.cmdline container=%container.name)
  priority: WARNING

- rule: Write below /etc in Container
  desc: Detect writes to /etc directory
  condition: >
    write and
    container and
    fd.name startswith /etc
  output: >
    File written below /etc in container
    (user=%user.name file=%fd.name container=%container.name)
  priority: WARNING

- rule: Container Drift Detected
  desc: New executable created in container
  condition: >
    spawned_process and
    container and
    proc.is_exe_writable=true
  output: >
    Executable created in container
    (user=%user.name exe=%proc.exe container=%container.name)
  priority: ERROR
EOF

# 3. 启动Falco
systemctl start falco
systemctl enable falco

# 4. 查看Falco日志
journalctl -fu falco
```

---

## 12. 供应链安全进阶

```yaml
Supply_Chain_Security:
  1_构建安全:
    可信构建环境:
      - 隔离构建环境
      - 使用专用构建节点
      - 构建环境加固
    
    构建证明 (Build Attestation):
      工具: SLSA Framework
      
      Level_1:
        - 自动化构建
        - 版本控制
      
      Level_2:
        - 托管构建服务
        - 构建证明签名
      
      Level_3:
        - 不可变构建环境
        - 完整的依赖追踪
      
      Level_4:
        - 双方审查
        - 可重现构建
    
    依赖管理:
      - 锁定依赖版本
      - 私有依赖镜像
      - 定期更新扫描
      - SBOM生成
  
  2_镜像签名与验证:
    Cosign:
      签名:
        cosign sign --key cosign.key image:tag
      
      验证:
        cosign verify --key cosign.pub image:tag
      
      无密钥签名 (Keyless):
        cosign sign image:tag  # 使用OIDC
    
    Notary_v2:
      - OCI Artifacts标准
      - 分布式信任
      - 多签名支持
  
  3_漏洞管理:
    扫描频率:
      - CI/CD: 每次构建
      - Registry: 每日扫描
      - Runtime: 实时监控
    
    漏洞响应:
      Critical:
        - 24小时内修复
        - 立即通知
        - 自动隔离
      
      High:
        - 7天内修复
        - 告警通知
        - 计划更新
      
      Medium_Low:
        - 30天内修复
        - 定期审查
  
  4_软件物料清单 (SBOM):
    生成:
      - Syft
      - Docker Scout
      - Trivy
    
    管理:
      - 存储在Registry
      - 版本追踪
      - 漏洞关联
    
    审计:
      - 许可证合规
      - 依赖审查
      - 漏洞追踪
```

### 12.1 实施SLSA构建

```yaml
# GitHub Actions - SLSA Level 3构建
name: SLSA Build and Provenance

on:
  push:
    branches: [main]

permissions:
  contents: read
  packages: write
  id-token: write  # For OIDC

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Build with provenance
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
        provenance: true
        sbom: true
    
    - name: Sign image with Cosign
      uses: sigstore/cosign-installer@v3
    
    - name: Sign the image
      run: |
        cosign sign --yes ghcr.io/${{ github.repository }}:${{ github.sha }}
    
    - name: Verify signature
      run: |
        cosign verify ghcr.io/${{ github.repository }}:${{ github.sha }} \
          --certificate-identity=https://github.com/${{ github.repository }}/.github/workflows/build.yml@refs/heads/main \
          --certificate-oidc-issuer=https://token.actions.githubusercontent.com
```

---

## 13. 合规性框架

```yaml
Compliance_Frameworks:
  1_CIS_Docker_Benchmark:
    版本: v1.6.0 (2023)
    
    主要检查项:
      Host_Configuration:
        - 1.1 Linux内核加固
        - 1.2 Docker守护进程配置
      
      Docker_Daemon:
        - 2.1 限制网络流量
        - 2.2 日志级别设置
        - 2.3 Docker文件权限
      
      Docker_Files:
        - 3.1 /etc/docker目录权限
        - 3.2 daemon.json权限
        - 3.3 证书文件权限
      
      Container_Images:
        - 4.1 使用可信镜像
        - 4.2 不使用latest标签
        - 4.3 定期更新基础镜像
      
      Container_Runtime:
        - 5.1 只读根文件系统
        - 5.2 资源限制
        - 5.3 非root用户
        - 5.4 最小权限
    
    自动化检查:
      docker run --rm --net host --pid host --userns host \
        --cap-add audit_control \
        -v /etc:/etc:ro \
        -v /var/lib:/var/lib:ro \
        -v /var/run/docker.sock:/var/run/docker.sock:ro \
        docker/docker-bench-security
  
  2_PCI_DSS:
    适用场景: 处理支付卡信息
    
    要求:
      - 网络隔离
      - 数据加密
      - 访问控制
      - 日志审计
      - 漏洞管理
    
    实施:
      - 容器网络隔离
      - 静态数据加密
      - 传输加密(TLS)
      - RBAC权限
      - 集中日志管理
      - 定期漏洞扫描
  
  3_HIPAA:
    适用场景: 医疗健康数据
    
    要求:
      - 数据隐私
      - 访问控制
      - 审计日志
      - 数据备份
      - 灾难恢复
    
    实施:
      - 数据脱敏
      - 加密存储
      - 细粒度访问控制
      - 完整审计追踪
      - 自动备份
      - 异地容灾
  
  4_SOC_2:
    适用场景: SaaS服务提供商
    
    信任服务准则:
      Security: 安全性
      Availability: 可用性
      Processing_Integrity: 处理完整性
      Confidentiality: 机密性
      Privacy: 隐私性
    
    实施:
      - 多层安全防护
      - 高可用架构
      - 数据完整性验证
      - 数据加密
      - 隐私保护措施
```

### 13.1 自动化合规检查

```bash
#!/bin/bash
# ========================================
# Docker合规性自动化检查脚本
# ========================================

set -e

echo "===== Docker合规性检查 ====="

# 1. CIS Benchmark检查
echo -e "\n➤ 运行CIS Benchmark..."
docker run --rm --net host --pid host --userns host \
  --cap-add audit_control \
  -v /etc:/etc:ro \
  -v /var/lib:/var/lib:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  docker/docker-bench-security | tee cis-benchmark-result.txt

# 2. 检查镜像签名
echo -e "\n➤ 检查镜像签名..."
for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>"); do
  echo "验证 $image..."
  cosign verify --key cosign.pub $image 2>/dev/null && echo "✅ 已签名" || echo "⚠️  未签名"
done

# 3. 检查SBOM
echo -e "\n➤ 检查SBOM..."
for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | head -5); do
  echo "生成 $image 的SBOM..."
  syft $image -o spdx-json > "${image//\//_}-sbom.json"
done

# 4. 检查容器配置
echo -e "\n➤ 检查容器配置..."
for container in $(docker ps -q); do
  NAME=$(docker inspect --format='{{.Name}}' $container)
  
  # 检查是否使用root
  USER=$(docker inspect --format='{{.Config.User}}' $container)
  if [ -z "$USER" ]; then
    echo "⚠️  $NAME: 使用root用户"
  fi
  
  # 检查是否只读根文件系统
  READONLY=$(docker inspect --format='{{.HostConfig.ReadonlyRootfs}}' $container)
  if [ "$READONLY" != "true" ]; then
    echo "⚠️  $NAME: 根文件系统非只读"
  fi
  
  # 检查资源限制
  MEM=$(docker inspect --format='{{.HostConfig.Memory}}' $container)
  if [ "$MEM" == "0" ]; then
    echo "⚠️  $NAME: 未设置内存限制"
  fi
done

# 5. 生成合规报告
echo -e "\n➤ 生成合规报告..."
cat > compliance-report-$(date +%Y%m%d).txt <<EOF
======================================
Docker合规性检查报告
生成时间: $(date)
======================================

CIS Benchmark结果:
$(cat cis-benchmark-result.txt | grep -E "PASS|WARN|FAIL" | sort | uniq -c)

镜像扫描结果:
$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}")

容器配置审查:
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}")

建议:
1. 修复CIS Benchmark中的WARN和FAIL项
2. 为所有镜像添加签名
3. 启用只读根文件系统
4. 设置资源限制
5. 使用非root用户
EOF

echo -e "\n✅ 合规性检查完成！报告已保存。"
```

---

## 14. 2025容器安全趋势

```yaml
Container_Security_Trends_2025:
  1_eBPF安全:
    特性:
      - 内核级监控
      - 零开销性能
      - 实时威胁检测
    
    工具:
      Cilium: 网络安全和可观测性
      Falco: 运行时安全
      Tetragon: 安全可观测性
    
    应用:
      - 网络策略执行
      - 系统调用过滤
      - 进程监控
      - 文件完整性监控
  
  2_机密计算 (Confidential Computing):
    技术:
      SGX: Intel Software Guard Extensions
      SEV: AMD Secure Encrypted Virtualization
      TDX: Intel Trust Domain Extensions
    
    应用:
      - 敏感数据处理
      - 加密计算
      - 多方安全计算
    
    容器支持:
      - Kata Containers
      - gVisor
      - Confidential Containers
  
  3_供应链透明化:
    SLSA_Framework:
      - Build Provenance
      - Dependency Tracking
      - Reproducible Builds
    
    SBOM_标准化:
      - SPDX
      - CycloneDX
      - SWID Tags
    
    Sigstore_生态:
      Cosign: 镜像签名
      Rekor: 透明日志
      Fulcio: 证书颁发
  
  4_零信任容器:
    SPIFFE_SPIRE:
      - Workload Identity
      - 自动证书轮换
      - 细粒度授权
    
    Service_Mesh:
      - mTLS通信
      - 动态访问控制
      - 流量加密
  
  5_AI驱动安全:
    威胁检测:
      - 异常行为检测
      - 模式识别
      - 自动响应
    
    漏洞预测:
      - 风险评分
      - 攻击路径分析
      - 优先级排序
```

---

## 相关文档

- [Docker安装与配置](01_Docker安装与配置.md)
- [Docker镜像管理](02_Docker镜像管理.md)
- [Docker Compose](03_Docker_Compose.md)
- [Kubernetes安全](../02_Kubernetes部署/README.md)
- [网络安全策略](../../01_虚拟化部署/04_网络架构/04_网络安全策略.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪
