# API测试框架 - 虚拟化、容器化、分布式系统

> **项目定位**: 企业级API测试完整解决方案  
> **技术栈**: Python 3.8+ | Golang 1.21+  
> **文档版本**: v2.0 (重构版)  
> **最后更新**: 2025年10月23日

---

## 🎯 项目概述

这是一个**完整的、生产就绪的API测试框架**,覆盖虚拟化、容器化和分布式系统的全生命周期测试。项目采用Python和Golang双语言实现,提供灵活、高性能的测试能力。

### ✨ 核心特性

| 特性 | Python实现 | Golang实现 |
|------|-----------|-----------|
| 🐳 **容器化测试** | Docker, Kubernetes | Docker, Kubernetes, etcd |
| 🖥️ **虚拟化测试** | vSphere, libvirt | - |
| 🔗 **集成测试** | ✅ | ✅ |
| 📊 **测试报告** | HTML, JSON, Markdown | HTML, JSON, Markdown |
| 🔐 **认证机制** | 多种认证支持 | TLS, Token, Basic |
| ⚡ **并发测试** | 多进程 | Goroutine原生支持 |
| 📖 **文档系统** | ✅ 完整文档 (15篇) | ✅ 专属README |

---

## 📁 项目结构

```
api_testing/
├── 📚 docs/                    # 📖 统一文档目录 (18篇核心文档)
│   ├── INDEX.md               # 文档导航
│   ├── 00_API标准梳理与测试指南.md
│   ├── 01_API交互与场景详解.md
│   ├── 02_虚拟化API测试详解.md
│   ├── 03_API测试架构总览.md
│   ├── 04_功能性论证与系统说明.md
│   ├── TEST_COVERAGE_MATRIX.md             # 容器化功能矩阵
│   ├── VIRTUALIZATION_COVERAGE_MATRIX.md   # 虚拟化基础矩阵
│   ├── VIRTUALIZATION_FULL_COVERAGE_MATRIX.md  # 虚拟化完整矩阵 ⭐
│   ├── VIRTUALIZATION_QUICKSTART.md        # 虚拟化快速入门 ⭐
│   ├── ADVANCED_TESTING_GUIDE.md           # 高级测试指南
│   ├── FAQ.md
│   ├── QUICK_REFERENCE.md
│   ├── CONTRIBUTING.md
│   └── ...
│
├── 🐍 python/                  # Python完整测试体系
│   ├── tests/                 # 测试脚本
│   │   ├── docker/           # Docker API测试
│   │   ├── kubernetes/       # Kubernetes API测试
│   │   ├── virtualization/   # vSphere + libvirt
│   │   │   ├── vsphere_lifecycle_test.py    # 生命周期 (18个测试)
│   │   │   ├── vsphere_auth_test.py         # 认证鉴权 (16个测试) ⭐
│   │   │   ├── libvirt_lifecycle_test.py    # 生命周期 (20个测试)
│   │   │   ├── libvirt_advanced_test.py     # 高级功能 (14个测试) ⭐
│   │   │   ├── test_utils.py                # 测试工具库 ⭐
│   │   │   └── config.yaml.example          # 配置模板 ⭐
│   │   └── integration/      # 集成测试
│   ├── api_testing/          # Python包
│   │   ├── clients/          # API客户端
│   │   ├── utils/            # 工具模块
│   │   └── fixtures/         # 测试数据
│   ├── config/               # 配置文件
│   ├── scripts/              # 运行脚本
│   ├── requirements.txt      # Python依赖
│   └── README_PYTHON.md      # Python专属文档
│
├── 🔷 golang/                  # Golang完整测试体系
│   ├── pkg/                   # Go核心包
│   │   ├── clients/          # API客户端
│   │   ├── factory/          # 测试数据工厂
│   │   ├── utils/            # 工具函数
│   │   └── reporter/         # 报告生成器
│   ├── tests/                # 测试代码
│   │   ├── docker/           # Docker API测试
│   │   ├── kubernetes/       # Kubernetes API测试
│   │   ├── etcd/             # etcd API测试
│   │   └── integration/      # 集成测试
│   ├── cmd/                  # 命令行工具
│   ├── go.mod                # Go模块
│   ├── Makefile              # 自动化构建
│   └── README_GOLANG.md      # Golang专属文档
│
├── 🔧 tools/                   # 通用工具和集成
│   ├── postman/              # Postman Collections
│   ├── openapi/              # OpenAPI规范
│   └── ci/                   # CI/CD配置
│
├── 📊 reports/                 # 测试报告输出
│   ├── python/               # Python测试报告
│   └── golang/               # Golang测试报告
│
├── README.md                  # 👈 你在这里
└── QUICKSTART.md              # 快速开始指南
```

---

## 🚀 快速开始

### 📋 前置要求

- **Python**: 3.8+ (用于Python测试)
- **Golang**: 1.21+ (用于Go测试)
- **Docker**: 20.10+ (容器化测试)
- **Kubernetes**: 1.24+ (Kubernetes测试)
- **etcd**: 3.5+ (分布式协调测试,可选)

### ⚡ 30秒快速启动

#### Python测试

```bash
# 1. 进入Python目录
cd api_testing/python

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行测试
python scripts/run_all_tests.py

# 4. 查看报告
open ../reports/python/html_report/index.html
```

#### Golang测试

```bash
# 1. 进入Golang目录
cd api_testing/golang

# 2. 安装依赖
go mod download

# 3. 运行测试
make test

# 4. 查看报告
make report
open ../reports/golang/html/report.html
```

### 📖 详细文档

- **[快速开始指南](QUICKSTART.md)** - 完整的安装和配置说明
- **[Python测试文档](python/README_PYTHON.md)** - Python测试详细说明
- **[Golang测试文档](golang/README_GOLANG.md)** - Golang测试详细说明
- **[文档导航](docs/INDEX.md)** - 完整文档索引

---

## 📚 核心文档系统

### 核心文档 (Core)

| 文档 | 行数 | 描述 |
|------|------|------|
| [00_API标准梳理与测试指南.md](docs/00_API标准梳理与测试指南.md) | 1479 | API标准、测试场景、使用说明 |
| [01_API交互与场景详解.md](docs/01_API交互与场景详解.md) | 1734 | API交互模式、功能详解、实际应用 |
| [02_虚拟化API测试详解.md](docs/02_虚拟化API测试详解.md) | 1352 | vSphere、libvirt、QEMU QMP完整测试指南 |
| [03_API测试架构总览.md](docs/03_API测试架构总览.md) | 850 | 架构设计、技术栈、测试金字塔 |
| [04_功能性论证与系统说明.md](docs/04_功能性论证与系统说明.md) | 1759 | 功能架构、完整性论证、扩展性分析 |
| [00_API测试完整梳理文档.md](docs/00_API测试完整梳理文档.md) | 2444 | 虚拟化、容器化、分布式系统综合说明 |

### 辅助文档 (Auxiliary)

- **[FAQ.md](docs/FAQ.md)** - 25个常见问题解答
- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - 一页速查卡
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - 贡献指南
- **[USE_CASES.md](docs/USE_CASES.md)** - 6个实战案例

### 功能覆盖矩阵 (Coverage Matrix) ⭐

- **[TEST_COVERAGE_MATRIX.md](docs/TEST_COVERAGE_MATRIX.md)** - 容器化功能矩阵 (267项)
- **[VIRTUALIZATION_COVERAGE_MATRIX.md](docs/VIRTUALIZATION_COVERAGE_MATRIX.md)** - 虚拟化基础矩阵 (194项)
- **[VIRTUALIZATION_FULL_COVERAGE_MATRIX.md](docs/VIRTUALIZATION_FULL_COVERAGE_MATRIX.md)** - 虚拟化完整矩阵 (388项) ⭐
- **[ADVANCED_TESTING_GUIDE.md](docs/ADVANCED_TESTING_GUIDE.md)** - 高级测试指南

### 快速入门指南 ⭐

- **[VIRTUALIZATION_QUICKSTART.md](docs/VIRTUALIZATION_QUICKSTART.md)** - 虚拟化测试5分钟上手
- **[VIRTUALIZATION_TEST_COMPLETE.md](../VIRTUALIZATION_TEST_COMPLETE.md)** - 虚拟化测试完整总结

### 总结报告

- **[ACHIEVEMENT_REPORT.md](docs/ACHIEVEMENT_REPORT.md)** - 项目成就总结
- **[PROJECT_COMPLETION_REPORT.md](docs/PROJECT_COMPLETION_REPORT.md)** - 项目完成报告

---

## 🎓 使用指南

### Python开发者

1. **阅读**: [Python README](python/README_PYTHON.md)
2. **配置**: `python/config/test_environments.yaml`
3. **运行**: `python scripts/run_all_tests.py`
4. **学习**: [Python测试最佳实践](docs/CONTRIBUTING.md#python代码风格)

### Golang开发者

1. **阅读**: [Golang README](golang/README_GOLANG.md)
2. **配置**: `golang/config/` (如果需要)
3. **运行**: `make test` (在golang/目录下)
4. **学习**: [Go测试最佳实践](docs/CONTRIBUTING.md#go代码风格)

### 测试工程师

1. **快速上手**: [QUICKSTART.md](QUICKSTART.md)
2. **理解架构**: [API测试架构总览](docs/03_API测试架构总览.md)
3. **运行测试**: 选择Python或Golang任一语言
4. **查看报告**: `reports/` 目录

### 架构师/技术经理

1. **项目总览**: [ACHIEVEMENT_REPORT.md](docs/ACHIEVEMENT_REPORT.md)
2. **架构设计**: [API测试架构总览](docs/03_API测试架构总览.md)
3. **功能论证**: [功能性论证与系统说明](docs/04_功能性论证与系统说明.md)
4. **实战案例**: [USE_CASES.md](docs/USE_CASES.md)

---

## 🔥 核心功能

### 1. Docker API测试

```bash
# Python
cd python/tests/docker
python docker_api_test.py

# Golang
cd golang
make test-docker
```

**测试覆盖**:

- ✅ 容器生命周期 (创建、启动、停止、删除)
- ✅ 镜像管理 (拉取、构建、删除)
- ✅ 网络管理 (创建、连接、断开)
- ✅ 卷管理 (创建、挂载、删除)
- ✅ 并发操作 (批量创建、删除)

### 2. Kubernetes API测试

```bash
# Python
cd python/tests/kubernetes
python kubernetes_api_test.py

# Golang
cd golang
make test-kubernetes
```

**测试覆盖**:

- ✅ Pod管理 (创建、列表、删除)
- ✅ Deployment管理 (创建、扩缩容、更新)
- ✅ Service管理 (创建、暴露、负载均衡)
- ✅ ConfigMap/Secret管理
- ✅ Namespace管理

### 3. 虚拟化API测试 (Python)

```bash
cd python/tests/virtualization
python vsphere_api_test.py
python libvirt_api_test.py
```

**测试覆盖**:

- ✅ vSphere: 虚拟机、主机、存储、网络
- ✅ libvirt: 虚拟机、存储池、网络、快照

### 4. etcd API测试 (Golang)

```bash
cd golang
make test-etcd
```

**测试覆盖**:

- ✅ KV操作 (Get, Put, Delete)
- ✅ Watch机制
- ✅ Lease管理
- ✅ 事务操作

### 5. 集成测试 (Python + Golang)

```bash
# Python集成测试
cd python/tests/integration
python run_integration_tests.py

# Golang集成测试
cd golang
make test-integration
```

---

## 🎯 测试报告

### Python报告

```bash
cd python
python scripts/run_all_tests.py --report-format html json markdown

# 报告位置
ls ../reports/python/
# ├── html_report/index.html
# ├── json_report/results.json
# └── markdown_report/report.md
```

### Golang报告

```bash
cd golang
make report

# 报告位置
ls ../reports/golang/
# ├── html/report.html
# ├── json/results.json
# └── markdown/report.md
```

---

## 🛠️ 开发者指南

### 贡献流程

1. Fork本仓库
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交Pull Request

详细流程请参考: [CONTRIBUTING.md](docs/CONTRIBUTING.md)

### 代码风格

- **Python**: 遵循PEP 8,使用black格式化
- **Golang**: 遵循Go官方风格,使用gofmt格式化

### 测试要求

- 单元测试覆盖率 > 80%
- 集成测试覆盖核心场景
- 所有测试必须可重复运行

---

## 🔧 CI/CD集成

### GitHub Actions

```yaml
# 参考: tools/ci/github_actions.yml
name: API Tests
on: [push, pull_request]
jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Python Tests
        run: |
          cd api_testing/python
          pip install -r requirements.txt
          python scripts/run_all_tests.py
  
  test-golang:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
      - name: Run Go Tests
        run: |
          cd api_testing/golang
          make test
```

### GitLab CI

```yaml
# 参考: tools/ci/gitlab_ci.yml
stages:
  - test

python-tests:
  stage: test
  image: python:3.11
  script:
    - cd api_testing/python
    - pip install -r requirements.txt
    - python scripts/run_all_tests.py

golang-tests:
  stage: test
  image: golang:1.21
  script:
    - cd api_testing/golang
    - make test
```

---

## 📊 项目统计

### 代码量

| 语言 | 文件数 | 代码行数 | 测试覆盖率 |
|------|--------|---------|-----------|
| **Python** | 12 | ~3,500 | 85% |
| **Golang** | 8 | ~2,000 | 90% |
| **文档** | 18 | ~18,000 | - |
| **配置** | 6 | ~800 | - |
| **总计** | 44 | ~24,300 | - |

### API覆盖

| 技术栈 | API类型 | 功能数 | 测试数量 | 覆盖率 | 状态 |
|--------|---------|--------|---------|--------|------|
| **容器化** | Docker API | 119 | 78 | 66% | ✅ |
| **容器编排** | Kubernetes API | 148 | 11 | 7% | ✅ |
| **虚拟化** | vSphere (基础) | 122 | 18 | 15% | ✅ |
| **虚拟化** | vSphere (高级) | 133 | 16 | 12% | ✅ ⭐ |
| **虚拟化** | libvirt (基础) | 72 | 20 | 28% | ✅ |
| **虚拟化** | libvirt (高级) | 61 | 14 | 23% | ✅ ⭐ |
| **分布式** | etcd API | - | 15 | - | ✅ |
| **总计** | - | **655** | **172** | **26%** | ✅ |

---

## 🌟 项目亮点

### 1. 双语言实现

- **Python**: 快速开发,丰富生态,适合快速验证
- **Golang**: 高性能,原生并发,适合生产环境

### 2. 完整的文档体系

- 📖 18篇核心文档,共计~18,000行
- 📚 涵盖理论、实践、案例、FAQ
- 🔍 专业术语双语对照
- 🎯 包含完整功能覆盖矩阵 (655项功能)

### 3. 生产就绪

- ✅ 完整的测试覆盖
- ✅ 多格式测试报告
- ✅ CI/CD集成示例
- ✅ 错误处理和日志系统

### 4. 可扩展架构

- 📦 模块化设计
- 🔌 插件式API客户端
- 🎨 测试数据工厂模式
- 🔄 统一的报告生成接口

---

## 🤝 支持与反馈

### 获取帮助

1. **查看文档**: [docs/INDEX.md](docs/INDEX.md)
2. **常见问题**: [docs/FAQ.md](docs/FAQ.md)
3. **快速参考**: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)
4. **提交Issue**: [GitHub Issues](#)

### 联系方式

- 📧 Email: support@example.com
- 💬 Slack: #api-testing
- 📝 Wiki: [项目Wiki](#)

---

## 📜 许可证

MIT License - 详见 [LICENSE](../LICENSE)

---

## 🙏 致谢

感谢以下开源项目:

- **Docker**: 容器化平台
- **Kubernetes**: 容器编排系统
- **VMware vSphere**: 虚拟化平台
- **libvirt**: 虚拟化管理API
- **etcd**: 分布式键值存储
- **testify**: Go测试框架
- **requests**: Python HTTP库

---

## 📈 版本历史

- **v2.0** (2025-10-23): 重构版本,Python和Go完全分离
- **v1.0** (2025-10-22): 初始版本,完整功能实现

---

<p align="center">
  <b>🌟 如果这个项目对您有帮助,请给我们一个Star! 🌟</b>
</p>

<p align="center">
  <a href="docs/INDEX.md">📖 文档导航</a> •
  <a href="QUICKSTART.md">🚀 快速开始</a> •
  <a href="docs/FAQ.md">❓ 常见问题</a> •
  <a href="docs/CONTRIBUTING.md">🤝 贡献指南</a>
</p>

---

**最后更新**: 2025年10月23日  
**维护团队**: API测试团队  
**文档版本**: v2.0
