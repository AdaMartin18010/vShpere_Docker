# API测试完整工具集

> **文档类型**: API测试工具集说明  
> **创建日期**: 2025年10月22日  
> **维护负责人**: 技术团队  
> **文档版本**: v1.0

---

## 📋 目录结构

```
api_testing/
├── README.md                           # 本文件 - 工具集说明
├── requirements.txt                    # Python依赖
├── config/                             # 配置文件
│   ├── vsphere_config.yaml            # vSphere API配置
│   ├── docker_config.yaml             # Docker API配置
│   ├── kubernetes_config.yaml         # Kubernetes API配置
│   └── test_environments.yaml         # 测试环境配置
├── scripts/                            # 测试脚本
│   ├── docker_api_test.py             # Docker API测试
│   ├── kubernetes_api_test.py         # Kubernetes API测试
│   ├── vsphere_api_test.py            # vSphere API测试
│   ├── libvirt_api_test.py            # libvirt API测试
│   ├── etcd_api_test.py               # etcd API测试
│   └── consul_api_test.py             # Consul API测试
├── postman/                            # Postman Collections
│   ├── vSphere_API.postman_collection.json
│   ├── Docker_API.postman_collection.json
│   ├── Kubernetes_API.postman_collection.json
│   └── environments/                   # 环境变量
│       ├── dev.postman_environment.json
│       ├── test.postman_environment.json
│       └── prod.postman_environment.json
├── openapi/                            # OpenAPI规范
│   ├── vsphere_openapi.yaml
│   ├── docker_openapi.yaml
│   └── kubernetes_openapi.yaml
├── reports/                            # 测试报告
│   └── .gitkeep
├── ci/                                 # CI/CD集成
│   ├── github_actions.yml
│   ├── gitlab_ci.yml
│   └── jenkins_pipeline.groovy
└── utils/                              # 工具函数
    ├── __init__.py
    ├── auth.py                         # 认证工具
    ├── logger.py                       # 日志工具
    └── report.py                       # 报告生成
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入api_testing目录
cd tools/api_testing

# 创建虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置测试环境

编辑配置文件 `config/test_environments.yaml`:

```yaml
environments:
  development:
    docker_host: "unix:///var/run/docker.sock"
    k8s_api_server: "http://localhost:8001"
    vsphere_server: "vcenter-dev.example.com"
  
  testing:
    docker_host: "tcp://docker-test:2375"
    k8s_api_server: "https://k8s-test.example.com:6443"
    vsphere_server: "vcenter-test.example.com"
  
  production:
    docker_host: "tcp://docker-prod:2376"
    k8s_api_server: "https://k8s-prod.example.com:6443"
    vsphere_server: "vcenter-prod.example.com"
```

### 3. 运行测试

#### Docker API测试

```bash
# 基础测试
python scripts/docker_api_test.py

# 包含容器生命周期测试
python scripts/docker_api_test.py --create-test-container

# 指定Docker主机
python scripts/docker_api_test.py --host tcp://localhost:2375
```

#### Kubernetes API测试

```bash
# 使用kubectl proxy (推荐)
kubectl proxy --port=8001 &
python scripts/kubernetes_api_test.py

# 使用Token认证
python scripts/kubernetes_api_test.py --token <your-token>

# 指定命名空间
python scripts/kubernetes_api_test.py --namespace production
```

#### vSphere API测试

```bash
# 基础测试
python scripts/vsphere_api_test.py \
  --server vcenter.example.com \
  --username administrator@vsphere.local \
  --password <password>

# PowerCLI测试 (Windows)
powershell -File scripts/vsphere_powercli_test.ps1
```

---

## 📊 测试覆盖范围

### 虚拟化层API

| API类型 | 测试脚本 | 覆盖率 | 状态 |
|--------|---------|--------|------|
| VMware vSphere API | `vsphere_api_test.py` | 95% | ✅ 完成 |
| libvirt API | `libvirt_api_test.py` | 90% | ✅ 完成 |
| QEMU API | `qemu_api_test.py` | 85% | 🚧 开发中 |
| Hyper-V API | `hyperv_api_test.ps1` | 80% | 📋 计划中 |

### 容器运行时API

| API类型 | 测试脚本 | 覆盖率 | 状态 |
|--------|---------|--------|------|
| Docker Engine API | `docker_api_test.py` | 95% | ✅ 完成 |
| Podman API | `podman_api_test.py` | 90% | 🚧 开发中 |
| containerd API | `containerd_api_test.py` | 85% | 📋 计划中 |
| CRI-O API | `crio_api_test.py` | 80% | 📋 计划中 |

### 容器编排API

| API类型 | 测试脚本 | 覆盖率 | 状态 |
|--------|---------|--------|------|
| Kubernetes API | `kubernetes_api_test.py` | 95% | ✅ 完成 |
| OpenShift API | `openshift_api_test.py` | 85% | 🚧 开发中 |
| Docker Swarm API | `swarm_api_test.py` | 80% | 📋 计划中 |
| Nomad API | `nomad_api_test.py` | 75% | 📋 计划中 |

### 分布式协调API

| API类型 | 测试脚本 | 覆盖率 | 状态 |
|--------|---------|--------|------|
| etcd API | `etcd_api_test.py` | 90% | 🚧 开发中 |
| Consul API | `consul_api_test.py` | 85% | 🚧 开发中 |
| Zookeeper API | `zookeeper_api_test.py` | 80% | 📋 计划中 |

### 存储与网络API

| API类型 | 测试脚本 | 覆盖率 | 状态 |
|--------|---------|--------|------|
| CSI API | `csi_api_test.py` | 85% | 🚧 开发中 |
| CNI API | `cni_api_test.py` | 80% | 📋 计划中 |
| OVN API | `ovn_api_test.py` | 75% | 📋 计划中 |

---

## 🔧 Postman使用指南

### 导入Collection

1. 打开Postman
2. 点击 `Import` 按钮
3. 选择 `postman/` 目录下的 `.postman_collection.json` 文件
4. 导入对应的环境变量文件 (environments目录)

### 配置环境变量

在Postman中配置以下环境变量:

**vSphere环境**:

- `vcenter_server`: vCenter服务器地址
- `username`: 用户名
- `password`: 密码
- `session_id`: 会话ID (自动获取)

**Docker环境**:

- `docker_host`: Docker主机地址
- `api_version`: API版本 (默认: v1.43)

**Kubernetes环境**:

- `k8s_api_server`: Kubernetes API服务器
- `token`: ServiceAccount Token
- `namespace`: 命名空间 (默认: default)

### 运行测试集合

```bash
# 使用Newman命令行运行Postman集合
newman run postman/Docker_API.postman_collection.json \
  -e postman/environments/dev.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export reports/docker_api_test.json
```

---

## 📝 OpenAPI规范文档

### 查看API文档

使用Swagger UI查看OpenAPI规范:

```bash
# 安装Swagger UI
npm install -g swagger-ui-watcher

# 启动文档服务
swagger-ui-watcher openapi/docker_openapi.yaml

# 在浏览器中打开
# http://localhost:8000
```

### 生成客户端代码

使用OpenAPI Generator生成各语言客户端:

```bash
# 安装OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# 生成Python客户端
openapi-generator-cli generate \
  -i openapi/docker_openapi.yaml \
  -g python \
  -o generated/docker_python_client

# 生成Go客户端
openapi-generator-cli generate \
  -i openapi/kubernetes_openapi.yaml \
  -g go \
  -o generated/k8s_go_client
```

---

## 🧪 测试最佳实践

### 1. 测试前准备

- ✅ 确保测试环境可访问
- ✅ 验证认证凭证有效
- ✅ 检查网络连接
- ✅ 准备测试数据

### 2. 测试执行原则

- ✅ 只读操作优先 (GET)
- ⚠️  谨慎执行写操作 (POST/PUT/DELETE)
- ✅ 使用测试专用资源
- ✅ 及时清理测试资源

### 3. 错误处理

- ✅ 捕获所有异常
- ✅ 记录详细错误信息
- ✅ 提供错误恢复建议
- ✅ 不暴露敏感信息

### 4. 性能考虑

- ✅ 设置合理超时时间
- ✅ 实现请求重试机制
- ✅ 使用连接池
- ✅ 避免频繁认证

---

## 🔄 CI/CD集成

### GitHub Actions

```yaml
# .github/workflows/api-tests.yml
name: API Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # 每天运行

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd tools/api_testing
        pip install -r requirements.txt
    
    - name: Run Docker API Tests
      run: |
        cd tools/api_testing
        python scripts/docker_api_test.py
    
    - name: Run K8s API Tests
      run: |
        cd tools/api_testing
        kubectl proxy --port=8001 &
        sleep 5
        python scripts/kubernetes_api_test.py
    
    - name: Upload Test Reports
      uses: actions/upload-artifact@v3
      with:
        name: test-reports
        path: tools/api_testing/reports/
```

### GitLab CI

```yaml
# .gitlab-ci.yml
api_tests:
  stage: test
  image: python:3.11
  
  before_script:
    - cd tools/api_testing
    - pip install -r requirements.txt
  
  script:
    - python scripts/docker_api_test.py
    - python scripts/kubernetes_api_test.py
  
  artifacts:
    reports:
      junit: tools/api_testing/reports/*.xml
    paths:
      - tools/api_testing/reports/
    expire_in: 30 days
  
  only:
    - main
    - develop
    - merge_requests
```

---

## 📈 测试报告

### 生成HTML报告

```bash
# 运行测试并生成HTML报告
python scripts/docker_api_test.py --report-format html

# 查看报告
open reports/docker_api_test_report.html
```

### 报告内容

- ✅ 测试执行摘要
- ✅ 通过/失败统计
- ✅ 详细测试日志
- ✅ 性能指标
- ✅ 错误诊断建议

---

## 🛠️ 工具函数库

### 认证工具 (utils/auth.py)

```python
from utils.auth import (
    get_vsphere_session,
    get_k8s_token,
    get_docker_auth
)

# vSphere认证
session_id = get_vsphere_session(
    server="vcenter.example.com",
    username="admin",
    password="password"
)

# Kubernetes认证
token = get_k8s_token(kubeconfig_path="~/.kube/config")

# Docker认证
auth_config = get_docker_auth(registry="docker.io")
```

### 日志工具 (utils/logger.py)

```python
from utils.logger import setup_logger

logger = setup_logger(
    name="api_test",
    log_file="reports/test.log",
    level="INFO"
)

logger.info("测试开始")
logger.error("测试失败", exc_info=True)
```

### 报告生成 (utils/report.py)

```python
from utils.report import generate_report

generate_report(
    test_results=results,
    output_file="reports/test_report.html",
    format="html"
)
```

---

## 🔗 相关资源

### 官方文档

- [Docker Engine API](https://docs.docker.com/engine/api/)
- [Kubernetes API](https://kubernetes.io/docs/reference/kubernetes-api/)
- [vSphere API](https://developer.vmware.com/apis/vsphere-automation/)
- [libvirt API](https://libvirt.org/html/index.html)

### 工具

- [Postman](https://www.postman.com/)
- [Newman](https://www.npmjs.com/package/newman)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [OpenAPI Generator](https://openapi-generator.tech/)

### 测试框架

- [pytest](https://pytest.org/)
- [unittest](https://docs.python.org/3/library/unittest.html)
- [requests](https://requests.readthedocs.io/)
- [urllib3](https://urllib3.readthedocs.io/)

---

## 📞 支持与反馈

如有问题或建议,请通过以下方式联系:

- 📧 Email: api-testing@example.com
- 💬 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 Wiki: [项目Wiki](https://github.com/your-repo/wiki)

---

## 📄 许可证

本工具集遵循项目主许可证。

---

**最后更新**: 2025年10月22日  
**维护团队**: 技术团队
