# 贡献指南

> **为API测试体系做出贡献**
> **创建日期**: 2025年10月23日
> **文档版本**: v1.0

---

## 📋 目录

- [贡献指南](#贡献指南)
  - [📋 目录](#-目录)
  - [欢迎贡献](#欢迎贡献)
  - [贡献方式](#贡献方式)
    - [1. 报告问题](#1-报告问题)
    - [2. 修复Bug](#2-修复bug)
    - [3. 开发新功能](#3-开发新功能)
  - [开发环境设置](#开发环境设置)
    - [前置要求](#前置要求)
    - [克隆仓库](#克隆仓库)
    - [Python环境设置](#python环境设置)
    - [Go环境设置](#go环境设置)
  - [代码贡献流程](#代码贡献流程)
    - [1. 创建分支](#1-创建分支)
    - [2. 进行更改](#2-进行更改)
    - [3. 本地测试](#3-本地测试)
    - [4. 推送更改](#4-推送更改)
  - [代码规范](#代码规范)
    - [Python代码规范](#python代码规范)
    - [Go代码规范](#go代码规范)
  - [测试要求](#测试要求)
    - [测试原则](#测试原则)
    - [测试结构](#测试结构)
    - [运行测试](#运行测试)
  - [文档贡献](#文档贡献)
    - [文档类型](#文档类型)
    - [文档规范](#文档规范)
    - [文档审查清单](#文档审查清单)
  - [提交规范](#提交规范)
    - [Commit Message格式](#commit-message格式)
    - [提交最佳实践](#提交最佳实践)
  - [Pull Request指南](#pull-request指南)
    - [创建PR前](#创建pr前)
    - [PR描述模板](#pr描述模板)
    - [PR审查流程](#pr审查流程)
    - [响应审查意见](#响应审查意见)
  - [问题报告](#问题报告)
    - [Bug报告模板](#bug报告模板)
    - [功能请求模板](#功能请求模板)
  - [行为准则](#行为准则)
    - [我们的承诺](#我们的承诺)
    - [不可接受的行为](#不可接受的行为)
    - [执行](#执行)
  - [致谢](#致谢)
    - [贡献者](#贡献者)
    - [如何获得认可](#如何获得认可)

---

## 欢迎贡献

感谢您考虑为API测试体系做出贡献！我们欢迎各种形式的贡献：

```yaml
代码贡献:
  - 新功能开发
  - Bug修复
  - 性能优化
  - 测试用例补充

文档贡献:
  - 文档完善
  - 错误修正
  - 翻译工作
  - 使用案例

其他贡献:
  - 问题报告
  - 功能建议
  - 设计反馈
  - 社区支持
```

---

## 贡献方式

### 1. 报告问题

如果您发现了bug或有改进建议：

```bash
1. 搜索现有Issues，避免重复
2. 使用Issue模板
3. 提供详细信息
4. 添加相关标签
```

### 2. 修复Bug

修复bug的步骤：

```yaml
步骤1: 寻找Issue
  - 查看 "good first issue" 标签
  - 查看 "help wanted" 标签
  - 评论表明您正在处理

步骤2: 本地复现
  - Fork项目
  - 克隆到本地
  - 复现问题
  - 编写测试

步骤3: 修复并测试
  - 实现修复
  - 运行测试套件
  - 确保通过
  - 更新文档

步骤4: 提交PR
  - 清晰的描述
  - 关联Issue
  - 等待审查
```

### 3. 开发新功能

添加新功能的流程：

```yaml
步骤1: 讨论功能
  - 创建Feature Request Issue
  - 说明用途和价值
  - 讨论实现方案
  - 获得维护者认可

步骤2: 设计方案
  - 撰写设计文档
  - 考虑向后兼容
  - 评估性能影响
  - 确定测试策略

步骤3: 实现功能
  - 遵循代码规范
  - 编写单元测试
  - 编写集成测试
  - 更新文档

步骤4: 提交审查
  - 完整的PR描述
  - 演示截图/示例
  - 性能测试结果
  - 文档更新
```

---

## 开发环境设置

### 前置要求

```bash
# 必需工具
git --version          # Git 2.0+
python --version       # Python 3.7+
go version            # Go 1.20+
docker --version      # Docker 20.0+

# 可选工具
kubectl version       # Kubernetes 1.20+
```

### 克隆仓库

```bash
# 1. Fork项目到您的账号
# 2. 克隆您的Fork
git clone https://github.com/YOUR_USERNAME/vShpere_Docker.git
cd vShpere_Docker/api_testing

# 3. 添加upstream远程仓库
git remote add upstream https://github.com/ORIGINAL_OWNER/vShpere_Docker.git

# 4. 验证remote
git remote -v
```

### Python环境设置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt  # 如果有

# 验证安装
python -c "import docker; import kubernetes; print('✅ Python环境就绪')"
```

### Go环境设置

```bash
# 设置Go代理（国内用户）
go env -w GOPROXY=https://goproxy.cn,direct

# 下载依赖
cd scripts
go mod download

# 验证
go build -v ./...
echo "✅ Go环境就绪"
```

---

## 代码贡献流程

### 1. 创建分支

```bash
# 确保主分支最新
git checkout main
git pull upstream main

# 创建功能分支
git checkout -b feature/add-podman-support
# 或修复分支
git checkout -b bugfix/fix-docker-connection

# 分支命名规范
feature/*   # 新功能
bugfix/*    # Bug修复
docs/*      # 文档改进
refactor/*  # 代码重构
test/*      # 测试改进
```

### 2. 进行更改

```yaml
编码过程:
  1. 小步提交
     - 每个提交专注一个更改
     - 提交前运行测试
     - 编写清晰的commit message

  2. 定期同步
     - git fetch upstream
     - git rebase upstream/main
     - 解决冲突

  3. 自我审查
     - 检查代码质量
     - 运行linter
     - 验证测试覆盖率
     - 更新相关文档
```

### 3. 本地测试

```bash
# Python测试
cd api_testing
python -m pytest tests/ -v
python -m pytest --cov=scripts --cov-report=html

# Go测试
cd scripts
go test -v ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# 格式检查
# Python
black scripts/
flake8 scripts/

# Go
gofmt -w .
go vet ./...
```

### 4. 推送更改

```bash
# 推送到您的Fork
git push origin feature/add-podman-support

# 如果需要强制推送（谨慎使用）
git push origin feature/add-podman-support --force-with-lease
```

---

## 代码规范

### Python代码规范

遵循 **PEP 8** 风格指南：

```python
# ✅ 好的示例
class DockerAPITestSuite(unittest.TestCase):
    """Docker API测试套件

    测试Docker Engine API的各种功能，包括容器、镜像、网络和卷管理。
    """

    def setUp(self):
        """测试前准备"""
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        self.test_containers = []

    def tearDown(self):
        """测试后清理"""
        for container in self.test_containers:
            try:
                container.remove(force=True)
            except Exception as e:
                logger.warning(f"清理容器失败: {e}")

    def test_create_container(self):
        """测试创建容器"""
        # Arrange
        image = "nginx:alpine"
        name = f"test-nginx-{uuid.uuid4().hex[:8]}"

        # Act
        container = self.client.containers.run(
            image,
            name=name,
            detach=True
        )
        self.test_containers.append(container)

        # Assert
        self.assertEqual(container.status, "running")
        self.assertIn(name, container.name)


# ❌ 不好的示例
def test1():  # 命名不清晰
    c = docker.DockerClient()  # 变量名太短
    c.containers.run("nginx")  # 没有清理
    # 没有断言
```

**关键点：**

```yaml
命名:
  - 类: PascalCase
  - 函数/方法: snake_case
  - 常量: UPPER_SNAKE_CASE
  - 私有: _leading_underscore

文档字符串:
  - 所有公共类和函数
  - 使用Google或NumPy风格
  - 包含参数和返回值说明

导入:
  - 标准库
  - 第三方库
  - 本地模块
  - 分组并按字母排序

行长度:
  - 最大79字符（代码）
  - 最大72字符（文档字符串）
```

### Go代码规范

遵循 **Effective Go** 指南：

```go
// ✅ 好的示例
package main

import (
 "context"
 "testing"
 "time"

 "github.com/docker/docker/client"
 "github.com/stretchr/testify/suite"
)

// DockerAPITestSuite Docker API测试套件
type DockerAPITestSuite struct {
 suite.Suite
 cli *client.Client
 ctx context.Context
 testContainers []string
}

// SetupSuite 套件级别的设置
func (s *DockerAPITestSuite) SetupSuite() {
 var err error
 s.cli, err = client.NewClientWithOpts(client.FromEnv)
 s.Require().NoError(err, "创建Docker客户端失败")

 s.ctx = context.Background()
 s.testContainers = make([]string, 0)
}

// TearDownTest 每个测试后的清理
func (s *DockerAPITestSuite) TearDownTest() {
 for _, containerID := range s.testContainers {
  _ = s.cli.ContainerRemove(s.ctx, containerID, types.ContainerRemoveOptions{
   Force: true,
  })
 }
 s.testContainers = s.testContainers[:0]
}

// Test01_CreateContainer 测试创建容器
func (s *DockerAPITestSuite) Test01_CreateContainer() {
 // Arrange
 image := "nginx:alpine"
 config := &container.Config{
  Image: image,
  Labels: map[string]string{
   "test": "true",
  },
 }

 // Act
 resp, err := s.cli.ContainerCreate(s.ctx, config, nil, nil, nil, "")
 s.Require().NoError(err, "创建容器失败")
 s.testContainers = append(s.testContainers, resp.ID)

 // Assert
 s.NotEmpty(resp.ID, "容器ID应该非空")
}


// ❌ 不好的示例
func test1(t *testing.T) {  // 命名不规范
 c, _ := client.NewClientWithOpts()  // 忽略错误
 c.ContainerCreate(context.Background(), nil, nil, nil, nil, "")  // 没有清理，没有断言
}
```

**关键点：**

```yaml
命名:
  - 包: 小写，单个词
  - 导出: PascalCase
  - 未导出: camelCase
  - 接口: er结尾（Reader, Writer）

注释:
  - 所有导出的标识符
  - 完整句子
  - 以标识符名称开头

错误处理:
  - 显式检查所有错误
  - 返回error类型
  - 使用errors.Wrap添加上下文

格式:
  - 使用gofmt
  - 使用goimports
  - tab缩进
```

---

## 测试要求

### 测试原则

```yaml
必须:
  - 所有新代码必须有测试
  - 修复bug必须添加回归测试
  - 测试覆盖率不能降低
  - 所有测试必须通过

推荐:
  - 单元测试覆盖率 > 80%
  - 集成测试覆盖关键路径
  - 使用表驱动测试（Go）
  - 使用参数化测试（Python）
```

### 测试结构

```python
# Python - pytest风格
import pytest

class TestDockerAPI:
    """Docker API测试类"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的设置"""
        self.client = docker.DockerClient()
        yield
        # 清理代码
        self.cleanup()

    @pytest.mark.parametrize("image,expected_status", [
        ("nginx:alpine", "running"),
        ("redis:alpine", "running"),
    ])
    def test_run_container(self, image, expected_status):
        """参数化测试运行容器"""
        container = self.client.containers.run(image, detach=True)
        assert container.status == expected_status
```

```go
// Go - testify/suite风格
func (s *DockerAPITestSuite) TestRunContainer() {
 tests := []struct {
  name          string
  image         string
  expectedState string
 }{
  {"nginx", "nginx:alpine", "running"},
  {"redis", "redis:alpine", "running"},
 }

 for _, tt := range tests {
  s.Run(tt.name, func() {
   // 测试逻辑
  })
 }
}
```

### 运行测试

```bash
# 运行所有测试
make test

# 运行特定测试
python -m pytest tests/test_docker.py::TestDockerAPI::test_create_container -v
go test -v -run TestDockerAPI/Test01_CreateContainer

# 查看覆盖率
make coverage

# 生成HTML报告
make coverage-html
```

---

## 文档贡献

### 文档类型

```yaml
代码文档:
  - 内联注释
  - 函数/类文档字符串
  - README
  - 代码示例

用户文档:
  - 使用指南
  - API参考
  - 教程
  - FAQ

开发者文档:
  - 架构设计
  - 贡献指南
  - 发布说明
  - 变更日志
```

### 文档规范

```markdown
# 标题规范

## 使用ATX风格标题（#）

### 层次结构清晰

#### 不要跳级

## 代码块

使用三个反引号并指定语言：

​```python
def hello():
    print("Hello, World!")
​```

## 链接

- 使用相对路径: [README](./README.md)
- 使用描述性文字: [查看API文档](./docs/api.md)
- 避免: 点击[这里](link)

## 列表

- 无序列表使用 -
- 保持一致
- 适当缩进

1. 有序列表使用数字
2. 按逻辑顺序
3. 清晰简洁
```

### 文档审查清单

```yaml
内容:
  - [ ] 信息准确
  - [ ] 示例可运行
  - [ ] 链接有效
  - [ ] 无拼写错误

格式:
  - [ ] Markdown格式正确
  - [ ] 代码块有语言标识
  - [ ] 标题层次合理
  - [ ] 列表格式一致

可读性:
  - [ ] 结构清晰
  - [ ] 语言简洁
  - [ ] 易于理解
  - [ ] 有必要的示例
```

---

## 提交规范

### Commit Message格式

使用 **约定式提交（Conventional Commits）**：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（Type）：**

```yaml
feat:     新功能
fix:      Bug修复
docs:     文档更新
style:    代码格式（不影响功能）
refactor: 重构
test:     测试相关
chore:    构建/工具链相关
perf:     性能优化
ci:       CI配置
```

**示例：**

```bash
# 简单提交
feat(docker): 添加Podman API支持

# 详细提交
fix(kubernetes): 修复命名空间清理问题

之前清理命名空间时，如果有Pod在Running状态，
会导致清理失败。现在会先停止所有Pod，
然后再删除命名空间。

Closes #123

# 破坏性变更
feat(api)!: 修改测试套件API

BREAKING CHANGE: TestSuite.run()方法签名已更改，
需要传入context参数。

Migration:
  旧: suite.run()
  新: suite.run(context.Background())
```

### 提交最佳实践

```yaml
原则:
  - 一个提交一个逻辑更改
  - 提交可编译可运行
  - 提交信息清晰有用
  - 频繁小提交优于少量大提交

避免:
  - ❌ "update" "fix" "改" 等无意义消息
  - ❌ 混合多个不相关更改
  - ❌ 提交调试代码
  - ❌ 提交TODO注释
```

---

## Pull Request指南

### 创建PR前

```yaml
检查清单:
  - [ ] 代码遵循项目规范
  - [ ] 所有测试通过
  - [ ] 添加必要的测试
  - [ ] 更新相关文档
  - [ ] 提交消息规范
  - [ ] 代码已自我审查
  - [ ] 无linter警告
```

### PR描述模板

```markdown
## 更改说明

简要描述本PR的目的和更改内容。

## 更改类型

- [ ] Bug修复
- [ ] 新功能
- [ ] 破坏性变更
- [ ] 文档更新
- [ ] 性能优化
- [ ] 代码重构

## 测试

描述测试方法和结果：

​```bash
cd api_testing
python -m pytest tests/test_new_feature.py -v
​```

## 截图/示例

如果适用，添加截图或使用示例。

## 检查清单

- [ ] 代码遵循项目规范
- [ ] 添加/更新了测试
- [ ] 测试全部通过
- [ ] 更新了文档
- [ ] 无linter警告

## 关联Issue

Closes #123
Related to #456
```

### PR审查流程

```yaml
提交PR后:
  1. 自动CI检查
     - 运行测试
     - 检查格式
     - 生成覆盖率

  2. 代码审查
     - 至少1个maintainer审查
     - 响应评论
     - 进行必要修改

  3. 合并
     - 所有检查通过
     - 获得批准
     - 维护者合并
```

### 响应审查意见

```yaml
态度:
  - 保持开放心态
  - 认真对待反馈
  - 礼貌友善回复
  - 及时响应

行动:
  - 理解审查意见
  - 讨论不明确的地方
  - 进行必要修改
  - 推送更新

如果不同意:
  - 礼貌地说明理由
  - 提供数据支持
  - 寻求共识
  - 尊重最终决定
```

---

## 问题报告

### Bug报告模板

```markdown
## Bug描述

清晰简洁地描述bug。

## 复现步骤

1. 执行命令 '...'
2. 修改配置 '...'
3. 观察到错误 '...'

## 预期行为

应该看到什么结果。

## 实际行为

实际看到了什么结果。

## 环境信息

- OS: [e.g. Ubuntu 22.04]
- Python版本: [e.g. 3.9.5]
- Go版本: [e.g. 1.20]
- Docker版本: [e.g. 24.0.5]
- 项目版本: [e.g. v1.0.0]

## 日志输出

​```
完整的错误日志
​```

## 附加信息

- 截图
- 配置文件
- 其他相关信息
```

### 功能请求模板

```markdown
## 功能描述

清晰简洁地描述您想要的功能。

## 问题和动机

这个功能解决什么问题？为什么需要它？

## 建议的解决方案

描述您希望如何实现这个功能。

## 替代方案

是否考虑过其他方法？

## 附加信息

- 参考资料
- 相关项目
- 示例代码
```

---

## 行为准则

### 我们的承诺

为了营造开放友好的环境，我们承诺：

```yaml
包容性:
  - 欢迎所有背景的贡献者
  - 尊重不同观点和经验
  - 接受建设性批评
  - 关注对社区最有利的事情

专业性:
  - 使用友好和包容的语言
  - 尊重不同意见
  - 优雅地接受批评
  - 展现同理心
```

### 不可接受的行为

```yaml
禁止:
  - 骚扰或歧视性言论
  - 人身攻击或贬损
  - 公开或私下骚扰
  - 未经许可发布他人信息
  - 其他不专业或不受欢迎的行为
```

### 执行

违反行为准则的行为将导致：

```yaml
1. 警告
2. 临时禁止
3. 永久禁止
```

---

## 致谢

感谢所有贡献者！您的努力使这个项目更加完善。

### 贡献者

贡献者列表：[CONTRIBUTORS.md](./CONTRIBUTORS.md)

### 如何获得认可

```yaml
自动认可:
  - PR被合并后自动添加
  - All Contributors bot
  - GitHub Contributors页面

其他方式:
  - 文档贡献
  - Issue讨论
  - 社区帮助
  - 推广宣传
```

---

**📖 相关文档:**

- [INDEX.md](./INDEX.md) - 文档导航
- [README.md](./README.md) - 项目说明
- [FAQ.md](./FAQ.md) - 常见问题
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) - 行为准则

**最后更新**: 2025年10月23日
**文档版本**: v1.0

---

**💡 感谢您的贡献！让我们一起打造优秀的API测试框架！**
