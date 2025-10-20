# Docker Compose

> **返回**: [Docker部署目录](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Docker Compose](#docker-compose)
  - [📋 目录](#-目录)
  - [1. Compose概述](#1-compose概述)
  - [2. Compose安装](#2-compose安装)
  - [3. Compose文件详解](#3-compose文件详解)
    - [3.1 基本结构](#31-基本结构)
    - [3.2 Services配置](#32-services配置)
    - [3.3 Networks配置](#33-networks配置)
    - [3.4 Volumes配置](#34-volumes配置)
  - [4. Compose命令](#4-compose命令)
  - [5. 实战案例](#5-实战案例)
    - [5.1 WordPress + MySQL](#51-wordpress--mysql)
    - [5.2 完整Web应用栈](#52-完整web应用栈)
    - [5.3 微服务架构](#53-微服务架构)
  - [6. Compose最佳实践](#6-compose最佳实践)
  - [7. 生产环境使用](#7-生产环境使用)
  - [8. 故障排查](#8-故障排查)
  - [9. Compose v2新特性 (2025)](#9-compose-v2新特性-2025)
    - [9.1 Compose Watch实战](#91-compose-watch实战)
  - [10. 高级配置技巧](#10-高级配置技巧)
    - [10.1 使用扩展字段 (x-\*)](#101-使用扩展字段-x-)
    - [10.2 动态配置与插值](#102-动态配置与插值)
    - [10.3 多环境配置](#103-多环境配置)
  - [11. CI/CD集成](#11-cicd集成)
    - [11.1 GitLab CI集成](#111-gitlab-ci集成)
    - [11.2 GitHub Actions集成](#112-github-actions集成)
  - [12. 性能优化](#12-性能优化)
  - [13. 安全加固](#13-安全加固)
  - [14. 监控与观测](#14-监控与观测)
  - [相关文档](#相关文档)

---

## 1. Compose概述

```yaml
Docker_Compose_Overview:
  定义:
    - 定义和运行多容器Docker应用的工具
    - 使用YAML文件配置服务
    - 单个命令创建和启动所有服务
  
  核心概念:
    Service (服务):
      - 应用的一个组件
      - 可以运行多个容器实例
      - 例: web服务、数据库服务
    
    Network (网络):
      - 服务间的通信网络
      - 自动DNS解析
      - 隔离和安全
    
    Volume (卷):
      - 数据持久化
      - 服务间共享数据
      - 主机与容器数据交换
  
  使用场景:
    开发环境:
      - 快速搭建开发环境
      - 一致的开发体验
      - 易于分享和复现
    
    测试环境:
      - 自动化测试
      - CI/CD集成
      - 隔离的测试环境
    
    单机部署:
      - 小型应用部署
      - 简单的生产环境
      - Demo演示
  
  优势:
    - 简化配置: YAML文件易读易写
    - 快速启动: 一条命令启动所有服务
    - 环境一致: 开发、测试、生产一致
    - 版本控制: Compose文件纳入Git
    - 服务发现: 自动DNS解析
  
  版本演进:
    Compose V1:
      - 命令: docker-compose
      - Python实现
      - 已弃用
    
    Compose V2:
      - 命令: docker compose
      - Go实现
      - Docker CLI插件
      - 推荐使用
```

---

## 2. Compose安装

```bash
# ========================================
# Docker Compose V2 安装
# ========================================

# Docker Compose V2已集成到Docker中
# 安装Docker Engine时自动安装

# 验证安装
docker compose version

# 输出示例:
# Docker Compose version v2.23.0

# ========================================
# 如果需要单独安装Compose V2
# ========================================

# Linux
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# macOS (使用Homebrew)
brew install docker-compose

# Windows
# Docker Desktop已包含Compose

# ========================================
# Compose V1 到 V2 迁移
# ========================================

# V1命令
docker-compose up -d
docker-compose ps
docker-compose down

# V2命令 (推荐)
docker compose up -d
docker compose ps
docker compose down

# 创建别名 (可选)
echo "alias docker-compose='docker compose'" >> ~/.bashrc
source ~/.bashrc
```

---

## 3. Compose文件详解

### 3.1 基本结构

```yaml
# ========================================
# docker-compose.yml 基本结构
# ========================================

# 版本号 (可选，Docker Compose V2不再需要)
version: '3.8'

# 服务定义
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
  
  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: example

# 网络定义 (可选)
networks:
  frontend:
  backend:

# 卷定义 (可选)
volumes:
  db-data:
  logs:

# 配置定义 (可选)
configs:
  my-config:
    file: ./config.txt

# 密钥定义 (可选)
secrets:
  db-password:
    file: ./db-password.txt
```

### 3.2 Services配置

```yaml
# ========================================
# Services 完整配置示例
# ========================================

services:
  webapp:
    # 镜像
    image: nginx:1.21-alpine
    
    # 或从Dockerfile构建
    build:
      context: ./dir
      dockerfile: Dockerfile
      args:
        BUILD_DATE: "2025-10-19"
        VERSION: "1.0.0"
      target: production
      cache_from:
        - alpine:3.18
    
    # 容器名称
    container_name: my-webapp
    
    # 主机名
    hostname: webapp.local
    
    # 域名解析
    domainname: example.com
    
    # 端口映射
    ports:
      - "80:80"              # 主机:容器
      - "443:443"
      - "127.0.0.1:8080:8080"  # 绑定特定IP
    
    # 暴露端口 (不映射到主机)
    expose:
      - "3000"
      - "8000"
    
    # 环境变量
    environment:
      - NODE_ENV=production
      - DEBUG=false
      - DATABASE_URL=postgres://db:5432
    
    # 或使用env_file
    env_file:
      - .env
      - .env.production
    
    # 命令
    command: ["nginx", "-g", "daemon off;"]
    # 或
    command: npm start
    
    # 入口点
    entrypoint: ["docker-entrypoint.sh"]
    
    # 工作目录
    working_dir: /app
    
    # 用户
    user: "1000:1000"
    
    # 挂载卷
    volumes:
      - ./data:/data              # 主机:容器
      - db-data:/var/lib/mysql    # 命名卷
      - /var/run/docker.sock:/var/run/docker.sock:ro  # 只读
      - type: bind                 # 长格式
        source: ./config
        target: /etc/config
        read_only: true
    
    # 网络
    networks:
      - frontend
      - backend
    
    # 网络别名
    networks:
      frontend:
        aliases:
          - web
          - webapp
    
    # 依赖
    depends_on:
      - db
      - redis
    
    # 或使用条件依赖 (Compose V2)
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    
    # 重启策略
    restart: always
    # no, always, on-failure, unless-stopped
    
    # 健康检查
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # 资源限制
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    
    # 或使用旧格式
    mem_limit: 512m
    cpus: 0.5
    
    # 标签
    labels:
      - "com.example.description=Web application"
      - "com.example.version=1.0"
    
    # 日志
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    # DNS
    dns:
      - 8.8.8.8
      - 8.8.4.4
    
    # 额外主机
    extra_hosts:
      - "host.docker.internal:host-gateway"
      - "somehost:162.242.195.82"
    
    # 安全选项
    security_opt:
      - no-new-privileges:true
    
    # 特权模式
    privileged: false
    
    # Cap添加/删除
    cap_add:
      - NET_ADMIN
    cap_drop:
      - ALL
    
    # PID模式
    pid: "host"
    
    # IPC模式
    ipc: "shareable"
    
    # 设备映射
    devices:
      - "/dev/ttyUSB0:/dev/ttyUSB0"
    
    # Tmpfs挂载
    tmpfs:
      - /run
      - /tmp
    
    # 系统控制
    sysctls:
      - net.ipv4.ip_forward=1
    
    # ULimits
    ulimits:
      nproc: 65535
      nofile:
        soft: 20000
        hard: 40000
```

### 3.3 Networks配置

```yaml
# ========================================
# Networks 配置示例
# ========================================

networks:
  # 默认网络 (自动创建)
  default:
    driver: bridge
  
  # 自定义网络
  frontend:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: br-frontend
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
  
  backend:
    driver: bridge
    internal: true  # 内部网络，无法访问外网
  
  # 使用已存在的网络
  existing-network:
    external: true
    name: my-pre-existing-network
  
  # Host网络
  host:
    external: true
    name: host
```

### 3.4 Volumes配置

```yaml
# ========================================
# Volumes 配置示例
# ========================================

volumes:
  # 默认卷
  db-data:
  
  # 自定义卷
  app-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/app
  
  # NFS卷
  nfs-data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=10.0.0.1,rw
      device: ":/path/to/dir"
  
  # 使用已存在的卷
  existing-volume:
    external: true
    name: my-existing-volume
```

---

## 4. Compose命令

```bash
# ========================================
# Docker Compose 常用命令
# ========================================

# 启动服务
docker compose up
docker compose up -d  # 后台运行
docker compose up --build  # 重新构建镜像
docker compose up --force-recreate  # 强制重建容器
docker compose up --scale web=3  # 扩展服务到3个实例

# 停止服务
docker compose stop  # 停止但不删除容器
docker compose down  # 停止并删除容器、网络
docker compose down -v  # 同时删除卷
docker compose down --rmi all  # 同时删除镜像

# 查看服务
docker compose ps  # 查看运行中的服务
docker compose ps -a  # 查看所有服务
docker compose top  # 查看服务进程

# 日志
docker compose logs  # 查看所有服务日志
docker compose logs web  # 查看特定服务日志
docker compose logs -f  # 跟踪日志
docker compose logs --tail=100  # 最近100行

# 执行命令
docker compose exec web sh  # 在运行中的容器执行命令
docker compose run web npm install  # 运行一次性命令

# 构建
docker compose build  # 构建服务
docker compose build --no-cache  # 不使用缓存构建

# 拉取镜像
docker compose pull  # 拉取所有服务镜像

# 推送镜像
docker compose push  # 推送镜像到仓库

# 配置验证
docker compose config  # 验证并查看配置
docker compose config --services  # 列出服务
docker compose config --volumes  # 列出卷

# 暂停/恢复
docker compose pause  # 暂停服务
docker compose unpause  # 恢复服务

# 重启
docker compose restart  # 重启服务
docker compose restart web  # 重启特定服务

# 查看端口
docker compose port web 80  # 查看服务端口映射

# 事件
docker compose events  # 实时查看事件

# 资源使用
docker compose stats  # 查看资源使用情况
```

---

## 5. 实战案例

### 5.1 WordPress + MySQL

```yaml
# ========================================
# WordPress + MySQL 示例
# ========================================

version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: wordpress-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress
    volumes:
      - db-data:/var/lib/mysql
    networks:
      - wordpress-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  wordpress:
    image: wordpress:latest
    container_name: wordpress-app
    restart: always
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wordpress-data:/var/www/html
    networks:
      - wordpress-network
    depends_on:
      db:
        condition: service_healthy

networks:
  wordpress-network:
    driver: bridge

volumes:
  db-data:
  wordpress-data:
```

### 5.2 完整Web应用栈

```yaml
# ========================================
# 完整Web应用栈: Nginx + Node.js + PostgreSQL + Redis
# ========================================

version: '3.8'

services:
  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx-logs:/var/log/nginx
    networks:
      - frontend
    depends_on:
      - app
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3

  app:
    build:
      context: ./app
      dockerfile: Dockerfile
      target: production
    container_name: nodejs-app
    restart: always
    environment:
      - NODE_ENV=production
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=myapp
      - DB_USER=appuser
      - DB_PASSWORD=apppassword
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - app-uploads:/app/uploads
      - app-logs:/app/logs
    networks:
      - frontend
      - backend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  postgres:
    image: postgres:15-alpine
    container_name: postgres-db
    restart: always
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=apppassword
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 512M

  redis:
    image: redis:7-alpine
    container_name: redis-cache
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

volumes:
  postgres-data:
  redis-data:
  app-uploads:
  app-logs:
  nginx-logs:
```

### 5.3 微服务架构

```yaml
# ========================================
# 微服务架构示例
# ========================================

version: '3.8'

services:
  # API Gateway
  api-gateway:
    build: ./api-gateway
    container_name: api-gateway
    restart: always
    ports:
      - "8000:8000"
    environment:
      - SERVICE_DISCOVERY_URL=http://consul:8500
    networks:
      - microservices
    depends_on:
      - consul
      - user-service
      - order-service
      - product-service

  # 服务发现 - Consul
  consul:
    image: consul:latest
    container_name: consul
    restart: always
    ports:
      - "8500:8500"
    networks:
      - microservices
    command: agent -server -ui -node=server-1 -bootstrap-expect=1 -client=0.0.0.0

  # 用户服务
  user-service:
    build: ./user-service
    container_name: user-service
    restart: always
    environment:
      - DB_HOST=user-db
      - DB_PORT=5432
      - CONSUL_URL=http://consul:8500
    networks:
      - microservices
    depends_on:
      - user-db
      - consul
    deploy:
      replicas: 2

  user-db:
    image: postgres:15-alpine
    container_name: user-db
    restart: always
    environment:
      POSTGRES_DB: userdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - user-db-data:/var/lib/postgresql/data
    networks:
      - microservices

  # 订单服务
  order-service:
    build: ./order-service
    container_name: order-service
    restart: always
    environment:
      - DB_HOST=order-db
      - DB_PORT=5432
      - CONSUL_URL=http://consul:8500
    networks:
      - microservices
    depends_on:
      - order-db
      - consul
    deploy:
      replicas: 2

  order-db:
    image: postgres:15-alpine
    container_name: order-db
    restart: always
    environment:
      POSTGRES_DB: orderdb
      POSTGRES_USER: order
      POSTGRES_PASSWORD: password
    volumes:
      - order-db-data:/var/lib/postgresql/data
    networks:
      - microservices

  # 产品服务
  product-service:
    build: ./product-service
    container_name: product-service
    restart: always
    environment:
      - DB_HOST=product-db
      - DB_PORT=27017
      - CONSUL_URL=http://consul:8500
    networks:
      - microservices
    depends_on:
      - product-db
      - consul
    deploy:
      replicas: 2

  product-db:
    image: mongo:6
    container_name: product-db
    restart: always
    volumes:
      - product-db-data:/data/db
    networks:
      - microservices

  # 消息队列
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: rabbitmq
    restart: always
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    networks:
      - microservices

networks:
  microservices:
    driver: bridge

volumes:
  user-db-data:
  order-db-data:
  product-db-data:
  rabbitmq-data:
```

---

## 6. Compose最佳实践

```yaml
Best_Practices:
  文件组织:
    基础文件:
      # docker-compose.yml (基础配置)
      # docker-compose.override.yml (本地开发覆盖)
      # docker-compose.prod.yml (生产环境)
      # docker-compose.test.yml (测试环境)
    
    使用多文件:
      # 合并多个compose文件
      docker compose -f docker-compose.yml -f docker-compose.prod.yml up
    
    环境变量:
      # 使用.env文件
      # .env
      # POSTGRES_VERSION=15
      # APP_PORT=8080
      
      # docker-compose.yml
      postgres:
        image: postgres:${POSTGRES_VERSION:-14}
  
  命名规范:
    ✅ 使用有意义的服务名:
      - web
      - api
      - db
      - cache
    
    ✅ 使用有意义的卷名:
      - postgres-data
      - redis-data
      - app-logs
    
    ✅ 使用有意义的网络名:
      - frontend
      - backend
      - monitoring
  
  资源限制:
    # 总是设置资源限制
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
  
  健康检查:
    # 为关键服务设置健康检查
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
  
  依赖管理:
    # 使用condition等待服务就绪
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
  
  安全实践:
    ✅ 不要在compose文件中硬编码密码:
      # 使用环境变量或secrets
      environment:
        - DB_PASSWORD=${DB_PASSWORD}
    
    ✅ 使用非root用户:
      user: "1000:1000"
    
    ✅ 最小权限原则:
      cap_drop:
        - ALL
      cap_add:
        - NET_BIND_SERVICE
    
    ✅ 只读挂载:
      volumes:
        - ./config:/etc/config:ro
  
  网络隔离:
    # 使用多个网络隔离服务
    networks:
      frontend:  # web层
      backend:   # 应用层
        internal: true  # 无法访问外网
  
  日志管理:
    # 配置日志驱动和轮转
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 7. 生产环境使用

```yaml
# ========================================
# 生产环境 docker-compose.prod.yml
# ========================================

version: '3.8'

services:
  web:
    image: myapp:${VERSION:-latest}
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"
        compress: "true"
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    environment:
      - NODE_ENV=production
      - LOG_LEVEL=info
```

**生产环境部署脚本**:

```bash
#!/bin/bash
# ========================================
# 生产环境部署脚本
# ========================================

set -e

PROJECT_NAME="myapp"
VERSION="v1.0.0"
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"

echo "===== 生产环境部署 ====="
echo "项目: $PROJECT_NAME"
echo "版本: $VERSION"

# 1. 拉取最新代码
git pull origin main

# 2. 设置环境变量
export VERSION=$VERSION

# 3. 拉取最新镜像
docker compose $COMPOSE_FILES pull

# 4. 备份当前数据
echo "➤ 备份数据..."
docker compose $COMPOSE_FILES exec -T db pg_dump -U postgres myapp > backup-$(date +%Y%m%d-%H%M%S).sql

# 5. 更新服务 (滚动更新)
echo "➤ 更新服务..."
docker compose $COMPOSE_FILES up -d --no-deps --build web

# 6. 等待服务就绪
echo "➤ 等待服务就绪..."
sleep 30

# 7. 健康检查
echo "➤ 健康检查..."
if curl -f http://localhost/health; then
  echo "✅ 部署成功！"
else
  echo "❌ 健康检查失败，回滚..."
  docker compose $COMPOSE_FILES down
  docker compose $COMPOSE_FILES up -d
  exit 1
fi

# 8. 清理旧镜像
docker image prune -f

echo "✅ 部署完成！"
```

---

## 8. 故障排查

```yaml
Troubleshooting:
  问题1_服务无法启动:
    症状: docker compose up 失败
    
    排查:
      # 查看日志
      docker compose logs service_name
      
      # 查看配置
      docker compose config
      
      # 检查端口占用
      sudo netstat -tuln | grep PORT
    
    常见原因:
      - 端口被占用
      - 配置文件语法错误
      - 镜像不存在
      - 卷挂载路径不存在
  
  问题2_服务间无法通信:
    症状: 服务A无法访问服务B
    
    排查:
      # 检查网络
      docker compose exec service_a ping service_b
      
      # 检查DNS
      docker compose exec service_a nslookup service_b
      
      # 检查网络配置
      docker network inspect network_name
    
    解决:
      # 确保服务在同一网络
      # 使用服务名访问，而不是IP
  
  问题3_数据丢失:
    症状: 容器重启后数据丢失
    
    原因: 未使用卷持久化
    
    解决:
      volumes:
        - db-data:/var/lib/mysql
  
  问题4_性能问题:
    症状: 服务响应慢
    
    排查:
      # 查看资源使用
      docker compose stats
      
      # 检查日志
      docker compose logs --tail=100
    
    解决:
      # 调整资源限制
      deploy:
        resources:
          limits:
            memory: 2G
```

**诊断命令**:

```bash
#!/bin/bash
# Compose诊断脚本

echo "=== Compose版本 ==="
docker compose version

echo -e "\n=== 服务状态 ==="
docker compose ps

echo -e "\n=== 服务日志 (最近50行) ==="
docker compose logs --tail=50

echo -e "\n=== 资源使用 ==="
docker compose stats --no-stream

echo -e "\n=== 网络检查 ==="
docker network ls | grep $(basename $(pwd))

echo -e "\n=== 卷检查 ==="
docker volume ls | grep $(basename $(pwd))

echo -e "\n=== 配置验证 ==="
docker compose config --quiet && echo "✅ 配置正确" || echo "❌ 配置错误"
```

---

## 9. Compose v2新特性 (2025)

```yaml
Compose_V2_Features:
  1_Compose_Specification:
    版本: Compose Specification (取代version字段)
    特性:
      - 不再需要version字段
      - 统一规范
      - 向后兼容
    
    示例:
      # Compose v2 - 不需要version
      services:
        web:
          image: nginx:latest
  
  2_Profiles:
    功能: 选择性启动服务
    
    配置:
      services:
        web:
          image: nginx
        
        debug:
          image: busybox
          profiles: ["debug"]
        
        test:
          image: test-runner
          profiles: ["test"]
    
    使用:
      # 启动默认服务
      docker compose up
      
      # 启动debug profile
      docker compose --profile debug up
      
      # 启动多个profile
      docker compose --profile debug --profile test up
  
  3_Watch_Mode:
    功能: 自动重载代码变更
    
    配置:
      services:
        web:
          build: .
          develop:
            watch:
              - action: sync
                path: ./src
                target: /app/src
              
              - action: rebuild
                path: ./package.json
              
              - action: sync+restart
                path: ./config
                target: /app/config
    
    使用:
      docker compose watch
  
  4_Include:
    功能: 包含其他Compose文件
    
    配置:
      include:
        - path: ./common/database.yml
        - path: ./common/cache.yml
      
      services:
        web:
          image: nginx
  
  5_Extends_增强:
    功能: 服务继承和覆盖
    
    基础文件 (base.yml):
      services:
        common:
          image: alpine
          environment:
            - ENV=base
    
    扩展文件:
      services:
        web:
          extends:
            file: base.yml
            service: common
          environment:
            - ENV=production
```

### 9.1 Compose Watch实战

```yaml
# compose.yaml - 开发环境配置
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    develop:
      watch:
        # 同步源代码变更
        - action: sync
          path: ./frontend/src
          target: /app/src
          ignore:
            - node_modules/
        
        # package.json变更时重建
        - action: rebuild
          path: ./frontend/package.json
  
  backend:
    build:
      context: ./backend
    develop:
      watch:
        # Python代码变更后同步并重启
        - action: sync+restart
          path: ./backend/app
          target: /app
          ignore:
            - __pycache__/
            - "*.pyc"
        
        # requirements变更时重建
        - action: rebuild
          path: ./backend/requirements.txt

# 启动开发环境
# docker compose watch
```

---

## 10. 高级配置技巧

### 10.1 使用扩展字段 (x-*)

```yaml
# 定义可复用的配置块
x-logging: &default-logging
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

x-healthcheck: &default-healthcheck
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s

x-deploy-resources: &default-resources
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M

services:
  web:
    image: nginx
    logging: *default-logging
    healthcheck:
      <<: *default-healthcheck
      test: ["CMD", "curl", "-f", "http://localhost"]
    <<: *default-resources
  
  api:
    image: api:latest
    logging: *default-logging
    healthcheck:
      <<: *default-healthcheck
      test: ["CMD", "curl", "-f", "http://localhost/health"]
    <<: *default-resources
```

### 10.2 动态配置与插值

```yaml
# 使用环境变量和默认值
services:
  web:
    image: nginx:${NGINX_VERSION:-latest}
    ports:
      - "${WEB_PORT:-8080}:80"
    environment:
      - ENV=${APP_ENV:-development}
      - API_URL=${API_URL:?API_URL is required}
    
    # 条件配置
    profiles:
      - ${DEPLOY_PROFILE:-default}

# .env文件
# NGINX_VERSION=1.25
# WEB_PORT=8080
# APP_ENV=production
# API_URL=https://api.example.com
# DEPLOY_PROFILE=production
```

### 10.3 多环境配置

```bash
#!/bin/bash
# 多环境配置策略

# 目录结构:
# ├── docker-compose.yml         # 基础配置
# ├── docker-compose.dev.yml     # 开发环境
# ├── docker-compose.prod.yml    # 生产环境
# ├── .env.dev                   # 开发环境变量
# └── .env.prod                  # 生产环境变量

# 开发环境
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  --env-file .env.dev \
  up

# 生产环境
docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  --env-file .env.prod \
  up -d
```

```yaml
# docker-compose.yml (基础)
services:
  web:
    image: myapp:${VERSION}
    environment:
      - APP_ENV=${APP_ENV}

# docker-compose.dev.yml (开发覆盖)
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - ./src:/app/src
    command: npm run dev
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src

# docker-compose.prod.yml (生产覆盖)
services:
  web:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

---

## 11. CI/CD集成

### 11.1 GitLab CI集成

```yaml
# .gitlab-ci.yml
variables:
  DOCKER_DRIVER: overlay2
  COMPOSE_FILE: docker-compose.yml:docker-compose.ci.yml

stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - docker compose build
    - docker compose push
  only:
    - main

test:
  stage: test
  script:
    - docker compose up -d
    - docker compose exec -T web npm test
    - docker compose down
  coverage: '/Coverage: \d+\.\d+%/'

deploy_staging:
  stage: deploy
  script:
    - docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

deploy_production:
  stage: deploy
  script:
    - docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
  environment:
    name: production
    url: https://example.com
  when: manual
  only:
    - main
```

### 11.2 GitHub Actions集成

```yaml
# .github/workflows/docker-compose.yml
name: Docker Compose CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  COMPOSE_FILE: docker-compose.yml:docker-compose.ci.yml

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Build services
      run: docker compose build
    
    - name: Start services
      run: docker compose up -d
    
    - name: Wait for services
      run: |
        timeout 60 sh -c 'until docker compose ps | grep healthy; do sleep 1; done'
    
    - name: Run tests
      run: docker compose exec -T web npm test
    
    - name: Check logs
      if: failure()
      run: docker compose logs
    
    - name: Stop services
      if: always()
      run: docker compose down -v
  
  deploy:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to production
      run: |
        docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 12. 性能优化

```yaml
Performance_Optimization:
  1_并行启动:
    # Compose默认并行启动服务
    配置:
      COMPOSE_PARALLEL_LIMIT: 10  # 并行数
    
    命令:
      docker compose up -d --parallel
  
  2_构建缓存:
    策略:
      - 使用BuildKit
      - 多阶段构建
      - 缓存挂载
    
    配置:
      services:
        web:
          build:
            context: .
            cache_from:
              - myapp:latest
              - myapp:cache
  
  3_资源限制:
    配置:
      services:
        web:
          deploy:
            resources:
              limits:
                cpus: '2'
                memory: 2G
                pids: 100
              reservations:
                cpus: '1'
                memory: 1G
  
  4_网络优化:
    配置:
      networks:
        frontend:
          driver: bridge
          driver_opts:
            com.docker.network.driver.mtu: 1450
        
        backend:
          internal: true  # 不连接外网
  
  5_日志管理:
    配置:
      services:
        web:
          logging:
            driver: "json-file"
            options:
              max-size: "10m"
              max-file: "3"
              compress: "true"
```

---

## 13. 安全加固

```yaml
# compose-secure.yml - 安全加固示例
services:
  web:
    image: nginx:alpine
    
    # 只读根文件系统
    read_only: true
    
    # 临时文件系统
    tmpfs:
      - /tmp
      - /var/run
    
    # 删除特权
    cap_drop:
      - ALL
    
    # 添加必要权限
    cap_add:
      - NET_BIND_SERVICE
    
    # 使用非root用户
    user: "1000:1000"
    
    # 安全选项
    security_opt:
      - no-new-privileges:true
      - apparmor=docker-default
    
    # 禁用特权模式
    privileged: false
    
    # PID限制
    pids_limit: 100
    
    # 资源限制
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
    
    # 健康检查
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
    
    # 网络隔离
    networks:
      - frontend
    
    # 不暴露不必要的端口
    # ports:
    #   - "8080:80"  # 仅在需要时暴露
  
  db:
    image: postgres:16-alpine
    
    # 使用secrets
    secrets:
      - db_password
    
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    
    # 数据持久化
    volumes:
      - db-data:/var/lib/postgresql/data
    
    # 内部网络
    networks:
      - backend
    
    # 不暴露到宿主机
    expose:
      - "5432"

secrets:
  db_password:
    file: ./secrets/db_password.txt

volumes:
  db-data:
    driver: local

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

---

## 14. 监控与观测

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - monitoring
  
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    networks:
      - monitoring
    depends_on:
      - prometheus
  
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    networks:
      - monitoring
  
  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./promtail-config.yml:/etc/promtail/config.yml
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - monitoring
    depends_on:
      - loki

volumes:
  prometheus-data:
  grafana-data:
  loki-data:

networks:
  monitoring:
    driver: bridge
```

---

## 相关文档

- [Docker安装与配置](01_Docker安装与配置.md)
- [Docker镜像管理](02_Docker镜像管理.md)
- [Docker安全与最佳实践](04_Docker安全与最佳实践.md)
- [Kubernetes应用部署](../02_Kubernetes部署/03_应用部署.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪
