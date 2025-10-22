# API测试文件夹索引

> **目录说明**: 虚拟化与容器化API测试完整工具集  
> **创建日期**: 2025年10月22日  
> **维护负责人**: 技术团队

---

## 📁 目录结构

```
api_testing/
├── 00_API测试完整梳理文档.md      # 主文档 - API测试完整梳理
├── README.md                       # 工具集使用说明
├── INDEX.md                        # 本文件 - 目录索引
├── requirements.txt                # Python依赖
├── 
├── config/                         # 配置文件目录
│   └── test_environments.yaml     # 多环境配置
├── 
├── scripts/                        # 测试脚本目录
│   ├── docker_api_test.py         # Docker API测试
│   ├── kubernetes_api_test.py     # Kubernetes API测试
│   ├── vsphere_api_test.py        # vSphere API测试 [计划中]
│   ├── libvirt_api_test.py        # libvirt API测试 [计划中]
│   └── run_all_tests.py           # 运行所有测试的主脚本
├── 
├── utils/                          # 工具函数库
│   ├── __init__.py                # 包初始化
│   ├── auth.py                    # 认证工具
│   ├── logger.py                  # 日志工具
│   └── report.py                  # 报告生成工具
├── 
├── postman/                        # Postman Collections
│   └── [待创建]
├── 
├── openapi/                        # OpenAPI规范文档
│   └── [待创建]
├── 
├── reports/                        # 测试报告输出
│   └── [自动生成]
└── 
└── ci/                            # CI/CD集成配置
    └── [待创建]
```

---

## 📖 文档导航

### 核心文档

1. **[00_API标准梳理与测试指南.md](./00_API标准梳理与测试指南.md)** (1479行)
   - 类型: API标准详解文档
   - 内容: API标准、测试场景、使用说明
   - 涵盖: RESTful、gRPC、Unix Socket标准
   - 适用: 理解API标准和测试方法

2. **[01_API交互与场景详解.md](./01_API交互与场景详解.md)** (1734行)
   - 类型: 容器化API交互详解
   - 内容: API交互模式、功能详解、实际应用场景
   - 涵盖: Docker、Kubernetes、etcd API
   - 适用: 容器化技术API实战

3. **[02_虚拟化API测试详解.md](./02_虚拟化API测试详解.md)** (1352行)
   - 类型: 虚拟化API测试详解
   - 内容: 虚拟化API完整测试指南
   - 涵盖: VMware vSphere、libvirt、QEMU QMP
   - 适用: 虚拟化技术API实战

4. **[00_API测试完整梳理文档.md](./00_API测试完整梳理文档.md)** (2444行)
   - 类型: 完整技术梳理文档
   - 内容: 虚拟化、容器化、分布式系统API测试的完整梳理
   - 涵盖: 所有API类型的综合说明
   - 包含: API规范、测试用例、OpenAPI定义

5. **[README.md](./README.md)**
   - 类型: 快速入门指南
   - 内容: 工具集使用说明、安装步骤、测试执行方法
   - 适用: 快速上手和日常使用

6. **[requirements.txt](./requirements.txt)**
   - 类型: Python依赖清单
   - 内容: 所有测试脚本需要的Python包
   - 用途: `pip install -r requirements.txt`

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd tools/api_testing
pip install -r requirements.txt
```

### 2. 配置环境

编辑 `config/test_environments.yaml` 设置测试环境参数。

### 3. 运行测试

```bash
# 运行所有测试
python scripts/run_all_tests.py

# 运行特定测试
python scripts/run_all_tests.py --tests docker kubernetes

# 生成HTML报告
python scripts/run_all_tests.py --report-format html json markdown
```

---

## 🔧 当前进度

### 已完成 ✅

- [x] 基础目录结构创建
- [x] Docker API测试脚本 (完整)
- [x] Kubernetes API测试脚本 (完整)
- [x] 认证工具模块 (auth.py)
- [x] 日志工具模块 (logger.py)
- [x] 报告生成模块 (report.py)
- [x] 多环境配置文件
- [x] 主测试运行脚本
- [x] API测试完整梳理文档

### 进行中 🚧

- [x] vSphere API测试脚本 ✅ (437行)
- [x] libvirt API测试脚本 ✅ (450行)
- [x] Postman Collections ✅ (Docker + Kubernetes)
- [x] OpenAPI规范文档 ✅ (etcd API)
- [x] CI/CD集成配置 ✅ (GitHub Actions + GitLab CI)
- [x] Golang测试套件 ✅ (Docker + Kubernetes + etcd)

### 计划中 📋

- [ ] etcd API测试脚本
- [ ] Consul API测试脚本
- [ ] Podman API测试脚本
- [ ] containerd API测试脚本
- [ ] 性能测试工具 (Locust)
- [ ] API Mock工具
- [ ] 测试数据生成器

---

## 📚 使用场景

### 场景1: 本地开发测试

```bash
# 使用默认配置(development环境)
python scripts/docker_api_test.py
```

### 场景2: CI/CD自动化测试

```bash
# 指定测试环境
export API_TEST_ENV=testing
python scripts/run_all_tests.py --report-format json
```

### 场景3: 生产环境只读测试

```bash
# 只执行安全的只读测试
export API_TEST_ENV=production
python scripts/run_all_tests.py --tests docker kubernetes --read-only
```

---

## 🎯 后续推进计划

### 第一阶段 (当前)

- ✅ 基础框架搭建
- ✅ Docker & Kubernetes测试
- 🚧 vSphere & libvirt测试

### 第二阶段

- 完善Postman Collections
- 编写OpenAPI规范文档
- 集成CI/CD流水线

### 第三阶段

- 分布式协调服务测试 (etcd, Consul)
- 存储与网络API测试 (CSI, CNI)
- 性能与压力测试

### 第四阶段

- API Mock与测试环境搭建
- 自动化测试数据生成
- 测试报告可视化面板

---

## 💡 贡献指南

### 添加新测试

1. 在 `scripts/` 目录创建测试脚本
2. 继承或参考现有测试类结构
3. 更新 `run_all_tests.py` 添加测试入口
4. 更新本INDEX.md文档

### 更新配置

1. 编辑 `config/test_environments.yaml`
2. 添加新环境或新API配置
3. 更新README.md说明

### 提交报告

测试报告自动生成在 `reports/` 目录，格式包括:

- HTML (可视化报告)
- JSON (程序解析)
- Markdown (文档归档)

---

## 📞 联系方式

- 📧 Email: api-testing@example.com
- 💬 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 Wiki: [项目Wiki](https://github.com/your-repo/wiki)

---

## 📄 许可证

本工具集遵循项目主许可证。

---

**最后更新**: 2025年10月22日  
**文档版本**: v1.0  
**维护团队**: 技术团队
