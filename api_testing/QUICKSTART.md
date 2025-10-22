# API测试快速开始指南

> 5分钟快速上手API测试工具集

---

## 🚀 快速开始

### 步骤1: 安装依赖 (1分钟)

```bash
# 进入目录
cd tools/api_testing

# 创建虚拟环境(推荐)
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 步骤2: 测试Docker API (2分钟)

```bash
# 确保Docker正在运行
docker ps

# 运行Docker API测试
python scripts/docker_api_test.py
```

**预期输出**:

```
=================================================================
Docker Engine API 完整测试套件
==================================================================
测试1: Docker守护进程连通性
✅ Docker守护进程连接成功
  - API状态: OK

测试2: 获取Docker版本信息
✅ 版本信息获取成功:
  - Docker版本: 24.0.7
  - API版本: 1.43
...
```

### 步骤3: 测试Kubernetes API (2分钟)

```bash
# 启动kubectl proxy
kubectl proxy --port=8001 &

# 运行Kubernetes API测试
python scripts/kubernetes_api_test.py
```

**预期输出**:

```
======================================================================
Kubernetes API 完整测试套件
======================================================================
测试1: 获取API版本
✅ API版本获取成功:
  - Core API组:
    - v1

测试2: 获取API组
✅ API组获取成功: 共 45 个组
...
```

---

## 📋 常见场景

### 场景1: 运行所有测试并生成报告

```bash
python scripts/run_all_tests.py --report-format html json markdown
```

查看报告:

```bash
# 打开HTML报告
open reports/api_test_report_*.html
```

### 场景2: 只运行特定测试

```bash
# 只测试Docker
python scripts/run_all_tests.py --tests docker

# 测试Docker和Kubernetes
python scripts/run_all_tests.py --tests docker kubernetes
```

### 场景3: 切换测试环境

```bash
# 编辑配置文件
vim config/test_environments.yaml

# 或使用环境变量
export API_TEST_ENV=testing
python scripts/run_all_tests.py
```

---

## 🔧 故障排查

### 问题1: Docker连接失败

```
❌ Docker守护进程连接失败
```

**解决方案**:

1. 确保Docker正在运行: `docker ps`
2. 检查Docker Socket权限: `ls -l /var/run/docker.sock`
3. 将用户加入docker组: `sudo usermod -aG docker $USER`

### 问题2: Kubernetes连接失败

```
❌ API版本获取失败: 401
```

**解决方案**:

1. 启动kubectl proxy: `kubectl proxy --port=8001`
2. 或配置Token认证:

   ```bash
   TOKEN=$(kubectl create token default)
   export K8S_TOKEN=$TOKEN
   ```

### 问题3: 依赖安装失败

```
ERROR: Could not find a version that satisfies the requirement libvirt-python
```

**解决方案**:

```bash
# Ubuntu/Debian
sudo apt-get install libvirt-dev python3-dev

# CentOS/RHEL
sudo yum install libvirt-devel python3-devel

# macOS
brew install libvirt
```

---

## 📚 下一步

- 📖 阅读完整文档: [README.md](./README.md)
- 📖 查看技术梳理: [00_API测试完整梳理文档.md](./00_API测试完整梳理文档.md)
- 📖 浏览索引导航: [INDEX.md](./INDEX.md)
- 🔧 配置环境: [config/test_environments.yaml](./config/test_environments.yaml)

---

## 💡 提示

- ✅ 建议先在开发环境测试
- ✅ 生产环境只运行只读测试
- ✅ 定期更新测试脚本
- ✅ 保存测试报告供后续分析

---

**最后更新**: 2025年10月22日
