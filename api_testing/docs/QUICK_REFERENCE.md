# API测试快速参考卡

> **一页纸快速参考** - 最常用的命令和概念
> **创建日期**: 2025年10月23日

---

## ⚡ 快速开始

```bash
# 1. 安装依赖
cd api_testing
pip install -r requirements.txt    # Python
cd scripts && go mod download       # Go

# 2. 运行测试
python scripts/docker_api_test.py                # Python单个测试
cd scripts && go test -v -run TestDockerAPI     # Go单个测试

# 3. 运行所有测试
python scripts/run_all_tests.py                 # Python全部
cd scripts && make test                          # Go全部
```

---

## 📁 目录结构速览

```
api_testing/
├── 📄 00-04_*.md        # 核心文档(6篇)
├── 📄 README.md         # 主说明
├── 📄 QUICKSTART.md     # 快速开始
├── 📄 INDEX.md          # 文档导航
├── scripts/             # 测试脚本
│   ├── *.py            # Python测试
│   ├── *_test.go       # Go测试
│   └── Makefile        # Go自动化
├── utils/               # 工具库
├── config/              # 配置文件
├── postman/             # Postman集合
├── openapi/             # OpenAPI规范
├── ci/                  # CI/CD配置
└── reports/             # 测试报告
```

---

## 🐳 Docker API常用测试

```python
# Python
from docker import DockerClient

client = DockerClient(base_url='unix://var/run/docker.sock')

# 基础操作
client.version()                           # 获取版本
client.containers.list()                   # 列出容器
client.containers.run('nginx', detach=True) # 运行容器
client.images.pull('alpine')               # 拉取镜像
```

```go
// Go
import "github.com/docker/docker/client"

cli, _ := client.NewClientWithOpts(client.FromEnv)
ctx := context.Background()

// 基础操作
cli.ServerVersion(ctx)                     // 获取版本
cli.ContainerList(ctx, types.ContainerListOptions{}) // 列出容器
cli.ContainerCreate(ctx, config, nil, nil, nil, "") // 创建容器
cli.ImagePull(ctx, "alpine:latest", types.ImagePullOptions{}) // 拉取镜像
```

---

## ☸️ Kubernetes API常用测试

```python
# Python
from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()

# 基础操作
v1.list_namespaced_pod('default')          # 列出Pod
v1.create_namespaced_pod('default', body)  # 创建Pod
v1.delete_namespaced_pod(name, 'default')  # 删除Pod
```

```go
// Go
import "k8s.io/client-go/kubernetes"

config, _ := clientcmd.BuildConfigFromFlags("", kubeconfig)
clientset, _ := kubernetes.NewForConfig(config)

// 基础操作
clientset.CoreV1().Pods("default").List(ctx, metav1.ListOptions{}) // 列出Pod
clientset.CoreV1().Pods("default").Create(ctx, pod, metav1.CreateOptions{}) // 创建Pod
clientset.CoreV1().Pods("default").Delete(ctx, name, metav1.DeleteOptions{}) // 删除Pod
```

---

## 🗄️ etcd API常用测试

```go
// Go only
import clientv3 "go.etcd.io/etcd/client/v3"

cli, _ := clientv3.New(clientv3.Config{
    Endpoints: []string{"localhost:2379"},
})

// 基础操作
cli.Put(ctx, "/key", "value")              // 写入
cli.Get(ctx, "/key")                        // 读取
cli.Delete(ctx, "/key")                     // 删除
cli.Watch(ctx, "/prefix", clientv3.WithPrefix()) // 监听
```

---

## 🖥️ vSphere API常用测试

```python
# Python
import requests

# 创建会话
response = requests.post(
    f'https://{vcenter}/rest/com/vmware/cis/session',
    auth=(username, password),
    verify=False
)
session_id = response.json()['value']

# 基础操作
headers = {'vmware-api-session-id': session_id}
requests.get(f'https://{vcenter}/rest/vcenter/vm', headers=headers) # 列出VM
requests.get(f'https://{vcenter}/rest/vcenter/vm/{vm_id}', headers=headers) # 获取VM
```

---

## 🧪 Make命令速查 (Go)

```bash
make deps              # 安装依赖
make test              # 运行所有测试
make test-docker       # Docker API测试
make test-k8s          # Kubernetes API测试
make test-etcd         # etcd API测试
make test-integration  # 集成测试
make coverage          # 生成覆盖率
make bench             # 运行基准测试
make fmt               # 格式化代码
make lint              # 代码检查
make clean             # 清理产物
make help              # 显示帮助
```

---

## 🔧 常用环境变量

```bash
# Docker
export DOCKER_HOST=unix:///var/run/docker.sock
export DOCKER_API_VERSION=1.41

# Kubernetes
export KUBECONFIG=~/.kube/config

# etcd
export ETCD_ENDPOINTS=localhost:2379

# vSphere
export VCENTER_HOST=vcenter.example.com
export VCENTER_USER=administrator@vsphere.local
export VCENTER_PASSWORD=********
```

---

## 📊 测试报告生成

```bash
# Python - 多格式报告
python scripts/run_all_tests.py --report-format html json markdown

# Go - 覆盖率报告
cd scripts
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html

# Go - JSON报告
go test -json ./... > test-report.json
```

---

## 🐛 故障排查速查

```yaml
Docker连接失败:
  1. 检查: docker ps
  2. 权限: sudo chmod 666 /var/run/docker.sock
  3. 变量: echo $DOCKER_HOST

Kubernetes连接失败:
  1. 检查: kubectl cluster-info
  2. 配置: kubectl config view
  3. Context: kubectl config use-context <name>

测试资源未清理:
  Docker: docker system prune -af
  K8s: kubectl delete namespace test-*
  etcd: etcdctl del --prefix /test/

依赖安装失败:
  Python: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
  Go: go env -w GOPROXY=https://goproxy.cn,direct
```

---

## 📖 文档阅读路径

```yaml
新手 (1小时):
  1. README.md
  2. QUICKSTART.md
  3. 运行第一个测试

进阶 (1天):
  1. 00_API标准梳理与测试指南.md
  2. 01_API交互与场景详解.md 或 02_虚拟化API测试详解.md
  3. 编写自定义测试

高级 (1周):
  1. 03_API测试架构总览.md
  2. 04_功能性论证与系统说明.md
  3. 扩展框架功能
```

---

## 🎯 测试用例命名规范

```yaml
Python:
  文件: test_*.py
  类: TestDockerAPI
  方法: test_get_version, test_create_container

Go:
  文件: *_test.go
  函数: TestDockerAPI
  子测试: Test01_GetVersion, Test02_ListContainers

清晰描述:
  ✅ test_create_container_with_valid_config
  ✅ test_should_fail_with_invalid_image
  ❌ test1, test2, test3
  ❌ test_something
```

---

## 🔑 最佳实践快记

```yaml
FIRST原则:
  Fast        - 快速执行
  Independent - 测试独立
  Repeatable  - 可重复
  Self-Validating - 自动验证
  Timely      - 及时编写

3A模式:
  Arrange  - 准备数据
  Act      - 执行操作
  Assert   - 验证结果

资源清理:
  - 使用 try-finally (Python)
  - 使用 defer (Go)
  - 验证清理完成
  - 使用唯一标识

测试数据:
  - 工厂模式生成
  - 使用UUID/时间戳
  - 环境隔离
  - 及时清理
```

---

## 🚀 CI/CD集成片段

```yaml
# GitHub Actions
- name: Run API Tests
  run: |
    cd api_testing
    pip install -r requirements.txt
    python scripts/run_all_tests.py

# GitLab CI
api_tests:
  script:
    - cd api_testing
    - pip install -r requirements.txt
    - python scripts/run_all_tests.py
```

---

## 📱 快速联系

```yaml
文档位置: api_testing/
主文档: README.md
快速开始: QUICKSTART.md
完整索引: INDEX.md
常见问题: FAQ.md
参考卡: QUICK_REFERENCE.md (本文档)
```

---

## 💡 实用技巧

```yaml
调试技巧:
  - Python: pytest -v -s
  - Go: go test -v
  - 单独测试: -run TestName
  - 详细日志: --log-cli-level=DEBUG

性能优化:
  - 并行测试: pytest -n auto 或 go test -parallel 10
  - 跳过慢测试: -m "not slow"
  - 只运行失败: pytest --lf

代码质量:
  - Python: black, flake8, mypy
  - Go: gofmt, golint, go vet
  - 覆盖率: >80% (单元), >60% (集成)
```

---

**📄 完整文档**: 查看 [INDEX.md](./INDEX.md) 获取所有文档列表

**🆘 需要帮助**: 查看 [FAQ.md](./FAQ.md) 解决常见问题

**最后更新**: 2025年10月23日
