# 🚀 快速开始指南

> **文档定位**: API测试框架快速入门  
> **预计时间**: 15分钟  
> **难度等级**: ⭐⭐☆☆☆  
> **最后更新**: 2025年10月23日

---

## 📋 目录

- [前置要求](#前置要求)
- [Python测试快速启动](#python测试快速启动)
- [Golang测试快速启动](#golang测试快速启动)
- [选择测试语言](#选择测试语言)
- [运行第一个测试](#运行第一个测试)
- [查看测试报告](#查看测试报告)
- [常见问题](#常见问题)
- [下一步](#下一步)

---

## 前置要求

### 必需环境

根据您选择的测试语言,安装以下工具:

#### Python测试 (Python路径)

```bash
# 检查Python版本 (需要 3.8+)
python --version
# 或
python3 --version

# 检查pip
pip --version
```

**没有Python?** 安装指南:

- **Windows**: https://www.python.org/downloads/
- **macOS**: `brew install python@3.11`
- **Linux**: `sudo apt install python3 python3-pip`

#### Golang测试 (Go路径)

```bash
# 检查Go版本 (需要 1.21+)
go version
```

**没有Go?** 安装指南:

- **所有平台**: https://go.dev/doc/install
- **macOS**: `brew install go`
- **Linux**: `sudo snap install go --classic`

### 测试目标环境

根据您要测试的API类型,确保以下服务可用:

#### Docker API测试

```bash
# 检查Docker
docker --version
docker ps

# 没有Docker?
# Windows/macOS: https://www.docker.com/products/docker-desktop
# Linux: sudo apt install docker.io
```

#### Kubernetes API测试

```bash
# 检查Kubernetes
kubectl version
kubectl cluster-info

# 没有Kubernetes?
# 本地测试: 安装Minikube或Kind
# minikube start
# 或
# kind create cluster
```

#### 虚拟化API测试 (仅Python)

```bash
# vSphere: 需要访问vCenter服务器
# libvirt: 需要libvirt服务
sudo systemctl status libvirtd
```

#### etcd API测试 (仅Golang)

```bash
# 检查etcd
etcdctl version

# 没有etcd?
# macOS: brew install etcd
# Linux: sudo apt install etcd
```

---

## Python测试快速启动

### 第1步: 克隆/进入项目

```bash
# 如果还没有项目
git clone <your-repo-url>
cd vShpere_Docker/api_testing/python

# 或直接进入
cd api_testing/python
```

### 第2步: 安装依赖

```bash
# 创建虚拟环境 (推荐)
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**依赖安装慢?** 使用国内镜像:

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第3步: 配置测试环境 (可选)

编辑 `config/test_environments.yaml`:

```yaml
environments:
  docker:
    unix_socket: "unix:///var/run/docker.sock"  # Linux/macOS
    # tcp_host: "tcp://localhost:2375"          # Windows
    
  kubernetes:
    config_path: "~/.kube/config"
    context: "default"
```

### 第4步: 运行测试

```bash
# 方式1: 使用主运行脚本 (推荐)
python scripts/run_all_tests.py

# 方式2: 运行特定测试
python tests/docker/docker_api_test.py

# 方式3: 使用unittest
python -m unittest discover -s tests -p "*_test.py"
```

### 第5步: 查看报告

```bash
# 生成HTML报告
python scripts/run_all_tests.py --report-format html

# 报告位置
open ../reports/python/html_report/index.html
# Windows: start ..\reports\python\html_report\index.html
```

**🎉 恭喜! Python测试环境搭建完成!**

---

## Golang测试快速启动

### 第1步: 克隆/进入项目

```bash
# 如果还没有项目
git clone <your-repo-url>
cd vShpere_Docker/api_testing/golang

# 或直接进入
cd api_testing/golang
```

### 第2步: 安装依赖

```bash
# 下载Go模块
go mod download

# 验证依赖
go mod verify
```

**依赖下载慢?** 使用国内代理:

```bash
export GOPROXY=https://goproxy.cn,direct
go mod download
```

### 第3步: 配置测试环境 (可选)

Go测试通常使用环境变量或代码内配置:

```bash
# 设置Docker主机
export DOCKER_HOST="unix:///var/run/docker.sock"

# 设置Kubernetes配置
export KUBECONFIG="~/.kube/config"

# 设置etcd端点
export ETCD_ENDPOINTS="localhost:2379"
```

### 第4步: 运行测试

```bash
# 方式1: 使用Makefile (推荐)
make test

# 方式2: 使用go test
go test ./tests/...

# 方式3: 详细输出
go test -v ./tests/...

# 方式4: 运行特定测试
make test-docker      # Docker测试
make test-kubernetes  # Kubernetes测试
make test-etcd        # etcd测试
```

### 第5步: 生成报告

```bash
# 生成所有格式报告
make report

# 或单独生成
make report-html      # HTML报告
make report-json      # JSON报告
make report-markdown  # Markdown报告

# 查看报告
open ../reports/golang/html/report.html
# Windows: start ..\reports\golang\html\report.html
```

### 第6步: 查看覆盖率

```bash
# 生成覆盖率报告
make coverage

# HTML覆盖率报告
make coverage-html
open ../reports/golang/coverage/coverage.html
```

**🎉 恭喜! Golang测试环境搭建完成!**

---

## 选择测试语言

不确定选择Python还是Golang? 以下是决策指南:

### 选择Python,如果您

✅ 需要测试虚拟化API (vSphere, libvirt)  
✅ 熟悉Python生态  
✅ 需要快速原型验证  
✅ 团队主要使用Python  
✅ 需要丰富的第三方库支持

**适用场景**:

- 虚拟化平台自动化测试
- 快速POC和验证
- DevOps脚本集成
- 数据分析和报告

### 选择Golang,如果您

✅ 需要高性能测试  
✅ 需要原生并发能力  
✅ 需要测试etcd等Go生态组件  
✅ 团队主要使用Go  
✅ 需要编译后的独立可执行文件

**适用场景**:

- 高并发负载测试
- 云原生系统测试
- 微服务API测试
- CI/CD pipeline集成
- 性能基准测试

### 🌟 推荐: 两者都用

- **Python**: 用于虚拟化和快速验证
- **Golang**: 用于容器编排和高性能测试

---

## 运行第一个测试

### Python示例: Docker容器测试

```bash
cd api_testing/python/tests/docker
python docker_api_test.py
```

**预期输出**:

```
======================================================================
测试: Docker API 基本功能
----------------------------------------------------------------------
开始时间: 2025-10-23 10:00:00
环境: Docker Engine 24.0.0

测试 1: 拉取nginx镜像 ... OK (5.2s)
测试 2: 创建nginx容器 ... OK (1.1s)
测试 3: 启动容器 ... OK (0.8s)
测试 4: 停止容器 ... OK (2.3s)
测试 5: 删除容器 ... OK (0.5s)

----------------------------------------------------------------------
运行 5 个测试,耗时 10.9s
结果: OK (5 passed, 0 failed, 0 errors)
======================================================================
```

### Golang示例: Kubernetes Pod测试

```bash
cd api_testing/golang
make test-kubernetes
```

**预期输出**:

```
=== RUN   TestKubernetesAPISuite
=== RUN   TestKubernetesAPISuite/TestCreatePod
=== RUN   TestKubernetesAPISuite/TestListPods
=== RUN   TestKubernetesAPISuite/TestDeletePod
--- PASS: TestKubernetesAPISuite (8.45s)
    --- PASS: TestKubernetesAPISuite/TestCreatePod (2.13s)
    --- PASS: TestKubernetesAPISuite/TestListPods (0.52s)
    --- PASS: TestKubernetesAPISuite/TestDeletePod (5.80s)
PASS
ok      your-module/tests/kubernetes    8.456s
```

---

## 查看测试报告

### Python报告

```bash
cd api_testing/python

# 生成所有格式报告
python scripts/run_all_tests.py --report-format html json markdown

# 报告位置
ls ../reports/python/
```

**报告包含**:

- ✅ 测试总览 (通过/失败/错误)
- ✅ 详细测试日志
- ✅ 执行时间分析
- ✅ 错误堆栈跟踪
- ✅ 趋势图表 (如果多次运行)

### Golang报告

```bash
cd api_testing/golang

# 生成报告
make report

# 查看报告
ls ../reports/golang/
```

**报告包含**:

- ✅ 测试覆盖率统计
- ✅ 性能基准数据
- ✅ 并发测试结果
- ✅ 失败测试详情
- ✅ Go测试框架原生输出

---

## 常见问题

### Q1: Docker连接失败

**错误**: `Cannot connect to the Docker daemon`

**解决方案**:

```bash
# Linux/macOS
sudo systemctl start docker
export DOCKER_HOST="unix:///var/run/docker.sock"

# Windows
# 启动Docker Desktop
```

### Q2: Kubernetes认证失败

**错误**: `Unable to connect to the server: Unauthorized`

**解决方案**:

```bash
# 检查kubeconfig
kubectl config view

# 设置正确的上下文
kubectl config use-context <your-context>

# 验证连接
kubectl cluster-info
```

### Q3: Python依赖冲突

**错误**: `Conflicting dependencies`

**解决方案**:

```bash
# 使用虚拟环境 (强烈推荐)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 清理pip缓存
pip cache purge
pip install -r requirements.txt
```

### Q4: Go模块下载失败

**错误**: `go: cannot find module providing package`

**解决方案**:

```bash
# 使用国内代理
export GOPROXY=https://goproxy.cn,direct

# 清理模块缓存
go clean -modcache

# 重新下载
go mod download
```

### Q5: 测试超时

**错误**: `test timed out`

**解决方案**:

```bash
# Python: 增加超时时间 (在代码中修改)
# Golang: 设置测试超时
go test -v -timeout 30m ./tests/...

# Makefile
make test TIMEOUT=30m
```

### Q6: 权限错误

**错误**: `Permission denied`

**解决方案**:

```bash
# Docker权限 (Linux)
sudo usermod -aG docker $USER
newgrp docker

# 文件权限
chmod +x scripts/*.sh
```

---

## 下一步

### 📚 深入学习

1. **阅读核心文档**
   - [API标准梳理与测试指南](docs/00_API标准梳理与测试指南.md)
   - [API交互与场景详解](docs/01_API交互与场景详解.md)
   - [虚拟化API测试详解](docs/02_虚拟化API测试详解.md)

2. **了解架构**
   - [API测试架构总览](docs/03_API测试架构总览.md)
   - [功能性论证与系统说明](docs/04_功能性论证与系统说明.md)

3. **实战案例**
   - [USE_CASES.md](docs/USE_CASES.md) - 6个完整案例

### 🔧 定制化

1. **配置测试环境**
   - Python: `python/config/test_environments.yaml`
   - Golang: 环境变量或配置文件

2. **扩展测试用例**
   - 参考: [CONTRIBUTING.md](docs/CONTRIBUTING.md)
   - 添加新的API测试
   - 创建自定义测试套件

3. **集成CI/CD**
   - 参考: `tools/ci/github_actions.yml`
   - 参考: `tools/ci/gitlab_ci.yml`

### 🎯 实践项目

选择一个实际场景开始:

1. **微服务CI/CD自动化**
   - 使用Golang测试Docker + Kubernetes
   - 自动化部署验证

2. **混合云平台统一管理**
   - 使用Python测试vSphere + Kubernetes
   - 跨平台资源编排

3. **容器安全扫描系统**
   - 使用Golang测试Docker镜像
   - 漏洞检测和合规性检查

4. **虚拟化平台自动化运维**
   - 使用Python测试vSphere/libvirt
   - 自动化备份、快照、迁移

---

## 📞 获取帮助

- **文档导航**: [docs/INDEX.md](docs/INDEX.md)
- **常见问题**: [docs/FAQ.md](docs/FAQ.md)
- **快速参考**: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)
- **贡献指南**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## 🎉 祝贺

您已经完成了快速开始指南! 现在您可以:

✅ 运行Python或Golang API测试  
✅ 生成和查看测试报告  
✅ 理解基本的项目结构  
✅ 解决常见问题

**继续探索** → [返回主文档](README.md) | [查看完整文档](docs/INDEX.md)

---

<p align="center">
  <b>🚀 Happy Testing! 🚀</b>
</p>

---

**最后更新**: 2025年10月23日  
**文档版本**: v2.0  
**维护团队**: API测试团队
