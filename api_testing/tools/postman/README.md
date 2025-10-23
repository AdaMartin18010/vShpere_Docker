# Postman Collections

本目录存放Postman API测试集合和环境配置。

## 📋 可用的Collection

### ✅ Docker Engine API v1.43

**文件**: `Docker_API_Collection.json`

完整的Docker Engine API测试集合,包含:

- ✅ 系统信息查询 (版本、Info、Ping)
- ✅ 容器生命周期管理 (创建、启动、停止、删除)
- ✅ 容器监控 (日志、统计信息)
- ✅ 镜像管理 (列出、拉取、标记、删除)
- ✅ 网络管理 (创建、查看、删除)
- ✅ 卷管理 (创建、查看、删除)

### ✅ Kubernetes API v1.28

**文件**: `Kubernetes_API_Collection.json`

完整的Kubernetes API测试集合,包含:

- ✅ 集群信息查询 (API版本、健康检查、节点列表)
- ✅ 命名空间管理
- ✅ Pod生命周期管理
- ✅ Deployment管理 (创建、扩缩容、更新)
- ✅ Service管理
- ✅ ConfigMap和Secret管理

## 🚀 快速开始

### 方法1: 在Postman中使用

1. **导入Collection**
   - 打开Postman
   - File → Import
   - 选择JSON文件

2. **导入环境配置**
   - 点击右上角齿轮图标
   - Import → 选择 `environments/` 目录下的JSON文件

3. **运行测试**
   - 单个请求: 点击"Send"
   - 整个Collection: 点击"Run"

### 方法2: 使用Newman (命令行)

```bash
# 安装Newman
npm install -g newman newman-reporter-htmlextra

# 运行Docker API测试
newman run Docker_API_Collection.json \
  --environment environments/docker_local.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export docker_report.html

# 运行Kubernetes API测试
newman run Kubernetes_API_Collection.json \
  --environment environments/k8s_local.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export k8s_report.html
```

## 📁 目录结构

```
postman/
├── Docker_API_Collection.json              # Docker API完整测试集
├── Kubernetes_API_Collection.json          # Kubernetes API完整测试集
├── environments/                           # 环境配置
│   ├── docker_local.json                  # Docker本地环境
│   └── k8s_local.json                     # Kubernetes本地环境
└── README.md                               # 本文件
```

## 🧪 环境配置

### Docker Local环境

**文件**: `environments/docker_local.json`

```json
{
  "docker_host": "http://localhost:2375/v1.43",
  "container_id": "",
  "network_id": "",
  "volume_name": ""
}
```

### Kubernetes Local环境

**文件**: `environments/k8s_local.json`

```json
{
  "k8s_api_server": "https://127.0.0.1:6443",
  "k8s_token": "<your_token>",
  "namespace": "default",
  "pod_name": "",
  "deployment_name": "",
  "service_name": ""
}
```

## 🔧 自动化特性

每个Collection都包含自动化脚本:

- ✅ 自动验证HTTP状态码
- ✅ 自动提取资源ID并保存到环境变量
- ✅ 支持完整的工作流测试
- ✅ 内置测试断言

## 📊 CI/CD集成

### GitHub Actions

```yaml
- name: 运行Postman测试
  run: |
    npm install -g newman
    newman run Docker_API_Collection.json \
      --environment environments/docker_local.json
```

### GitLab CI

```yaml
postman-test:
  image: postman/newman
  script:
    - newman run Docker_API_Collection.json \
        --environment environments/docker_local.json
```

## 📚 参考资源

- [Postman官方文档](https://learning.postman.com/)
- [Newman文档](https://github.com/postmanman/newman)
- [Docker Engine API](https://docs.docker.com/engine/api/)
- [Kubernetes API](https://kubernetes.io/docs/reference/kubernetes-api/)
