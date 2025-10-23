# Python API 测试套件

> **语言**: Python 3.8+  
> **测试框架**: unittest, pytest  
> **文档版本**: v1.0  
> **最后更新**: 2025年10月23日

---

## 📋 目录

- [Python API 测试套件](#python-api-测试套件)
  - [📋 目录](#-目录)
  - [概述](#概述)
    - [特性](#特性)
  - [目录结构](#目录结构)
  - [快速开始](#快速开始)
    - [1. 安装依赖](#1-安装依赖)
    - [2. 配置测试环境](#2-配置测试环境)
    - [3. 运行测试](#3-运行测试)
  - [测试分类](#测试分类)
    - [Docker API 测试](#docker-api-测试)
    - [Kubernetes API 测试](#kubernetes-api-测试)
    - [vSphere API 测试](#vsphere-api-测试)
    - [libvirt API 测试](#libvirt-api-测试)
  - [运行测试](#运行测试)
    - [使用主运行脚本](#使用主运行脚本)
    - [使用unittest](#使用unittest)
    - [使用pytest (如果安装)](#使用pytest-如果安装)
  - [配置说明](#配置说明)
    - [环境变量](#环境变量)
    - [配置文件优先级](#配置文件优先级)
  - [最佳实践](#最佳实践)
    - [1. 测试隔离](#1-测试隔离)
    - [2. 资源清理](#2-资源清理)
    - [3. 错误处理](#3-错误处理)
    - [4. 日志记录](#4-日志记录)
  - [故障排除](#故障排除)
    - [常见问题](#常见问题)
      - [1. Docker连接失败](#1-docker连接失败)
      - [2. Kubernetes认证失败](#2-kubernetes认证失败)
      - [3. vSphere SSL证书错误](#3-vsphere-ssl证书错误)
      - [4. 依赖安装失败](#4-依赖安装失败)
  - [相关文档](#相关文档)
  - [支持](#支持)

---

## 概述

本目录包含完整的Python API测试套件,涵盖容器化、虚拟化和分布式系统的API测试。

### 特性

- ✅ **容器化测试**: Docker API、Kubernetes API
- ✅ **虚拟化测试**: VMware vSphere API、libvirt API
- ✅ **集成测试**: 跨系统集成测试
- ✅ **认证工具**: 支持多种认证机制
- ✅ **日志系统**: 结构化日志记录
- ✅ **报告生成**: HTML、JSON、Markdown多格式报告

---

## 目录结构

```
python/
├── 📁 tests/                      # 测试脚本目录
│   ├── docker/                    # Docker API测试
│   │   └── docker_api_test.py
│   ├── kubernetes/                # Kubernetes API测试
│   │   └── kubernetes_api_test.py
│   ├── virtualization/            # 虚拟化API测试
│   │   ├── vsphere_api_test.py
│   │   └── libvirt_api_test.py
│   └── integration/               # 集成测试
│
├── 📁 api_testing/                # Python包目录
│   ├── __init__.py               # 包初始化
│   ├── clients/                  # API客户端封装
│   ├── utils/                    # 工具模块
│   │   ├── auth.py              # 认证工具
│   │   ├── logger.py            # 日志工具
│   │   └── report.py            # 报告生成
│   └── fixtures/                 # 测试数据和fixtures
│
├── 📁 config/                     # 配置文件
│   └── test_environments.yaml    # 测试环境配置
│
├── 📁 scripts/                    # 脚本工具
│   └── run_all_tests.py          # 主测试运行脚本
│
├── 📁 examples/                   # 示例代码
│
└── requirements.txt               # Python依赖清单
```

---

## 快速开始

### 1. 安装依赖

```bash
cd python
pip install -r requirements.txt
```

### 2. 配置测试环境

编辑 `config/test_environments.yaml`:

```yaml
environments:
  docker:
    unix_socket: "unix:///var/run/docker.sock"
    tcp_host: "tcp://localhost:2375"
    
  kubernetes:
    config_path: "~/.kube/config"
    context: "default"
    
  vsphere:
    host: "vcenter.example.com"
    username: "administrator@vsphere.local"
    password: "your_password"
    
  libvirt:
    connection_uri: "qemu:///system"
```

### 3. 运行测试

```bash
# 运行所有测试
python scripts/run_all_tests.py

# 运行特定类型测试
python scripts/run_all_tests.py --tests docker kubernetes

# 生成HTML报告
python scripts/run_all_tests.py --report-format html
```

---

## 测试分类

### Docker API 测试

```bash
cd tests/docker
python docker_api_test.py
```

**测试覆盖**:

- 容器生命周期管理 (创建、启动、停止、删除)
- 镜像管理 (拉取、列出、删除)
- 网络管理 (创建、连接、断开)
- 卷管理 (创建、挂载、删除)

### Kubernetes API 测试

```bash
cd tests/kubernetes
python kubernetes_api_test.py
```

**测试覆盖**:

- Pod管理 (创建、列出、删除)
- Deployment管理 (创建、扩缩容、更新)
- Service管理 (创建、暴露、删除)
- ConfigMap/Secret管理

### vSphere API 测试

```bash
cd tests/virtualization
python vsphere_api_test.py
```

**测试覆盖**:

- 虚拟机管理 (创建、克隆、快照)
- 主机资源监控
- 存储管理
- 网络配置

### libvirt API 测试

```bash
cd tests/virtualization
python libvirt_api_test.py
```

**测试覆盖**:

- 虚拟机生命周期
- 存储池管理
- 网络配置
- 快照管理

---

## 运行测试

### 使用主运行脚本

```bash
# 运行所有测试
python scripts/run_all_tests.py

# 运行特定测试
python scripts/run_all_tests.py --tests docker kubernetes

# 指定报告格式
python scripts/run_all_tests.py --report-format html json markdown

# 详细输出
python scripts/run_all_tests.py --verbose
```

### 使用unittest

```bash
# 运行单个测试文件
python -m unittest tests.docker.docker_api_test

# 运行所有测试
python -m unittest discover -s tests -p "*_test.py"
```

### 使用pytest (如果安装)

```bash
# 运行所有测试
pytest tests/

# 运行特定目录
pytest tests/docker/

# 生成覆盖率报告
pytest tests/ --cov=api_testing --cov-report=html
```

---

## 配置说明

### 环境变量

支持通过环境变量覆盖配置:

```bash
export DOCKER_HOST="unix:///var/run/docker.sock"
export KUBECONFIG="~/.kube/config"
export VSPHERE_HOST="vcenter.example.com"
export VSPHERE_USERNAME="admin"
export VSPHERE_PASSWORD="password"
```

### 配置文件优先级

1. 环境变量 (最高优先级)
2. `config/test_environments.yaml`
3. 默认配置 (最低优先级)

---

## 最佳实践

### 1. 测试隔离

- 每个测试应该是独立的,不依赖其他测试的执行顺序
- 使用 `setUp()` 和 `tearDown()` 进行测试前后的清理

### 2. 资源清理

- 测试结束后清理创建的资源
- 使用 `try...finally` 确保资源清理

```python
def test_example(self):
    container = None
    try:
        container = client.containers.create("nginx")
        # 测试逻辑
    finally:
        if container:
            container.remove(force=True)
```

### 3. 错误处理

- 捕获并记录异常信息
- 提供有意义的错误消息

```python
try:
    result = api_call()
except Exception as e:
    logger.error(f"API调用失败: {str(e)}")
    raise
```

### 4. 日志记录

```python
from api_testing.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("开始测试")
logger.debug(f"请求参数: {params}")
```

---

## 故障排除

### 常见问题

#### 1. Docker连接失败

**问题**: `Cannot connect to the Docker daemon`

**解决方案**:

```bash
# 检查Docker服务状态
sudo systemctl status docker

# 启动Docker服务
sudo systemctl start docker

# 验证连接
docker ps
```

#### 2. Kubernetes认证失败

**问题**: `Unauthorized: authentication required`

**解决方案**:

```bash
# 检查kubeconfig
kubectl config view

# 验证当前上下文
kubectl config current-context

# 切换上下文
kubectl config use-context <context-name>
```

#### 3. vSphere SSL证书错误

**问题**: `SSL certificate verify failed`

**解决方案**:

```python
# 在测试中禁用SSL验证 (仅用于开发环境)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

#### 4. 依赖安装失败

**问题**: `Could not install packages`

**解决方案**:

```bash
# 升级pip
pip install --upgrade pip

# 使用清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

---

## 相关文档

- **[主文档](../docs/INDEX.md)** - 完整文档导航
- **[快速开始](../docs/QUICKSTART.md)** - 快速入门指南
- **[API标准](../docs/00_API标准梳理与测试指南.md)** - API标准详解
- **[常见问题](../docs/FAQ.md)** - 常见问题解答
- **[贡献指南](../docs/CONTRIBUTING.md)** - 如何贡献代码

---

## 支持

如有问题或建议,请:

1. 查阅 [FAQ文档](../docs/FAQ.md)
2. 查看 [快速参考](../docs/QUICK_REFERENCE.md)
3. 提交 Issue

---

**最后更新**: 2025年10月23日  
**维护团队**: API测试团队  
**许可证**: MIT
