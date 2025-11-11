# 🚀 虚拟化测试快速入门指南

> **5分钟快速上手** - vSphere & libvirt API测试
> **最后更新**: 2025年10月23日

---

## 📋 目录

- [🚀 虚拟化测试快速入门指南](#-虚拟化测试快速入门指南)
  - [📋 目录](#-目录)
  - [前提条件](#前提条件)
    - [系统要求](#系统要求)
    - [环境要求](#环境要求)
      - [vSphere测试](#vsphere测试)
      - [libvirt测试](#libvirt测试)
  - [快速开始](#快速开始)
    - [步骤1: 安装依赖](#步骤1-安装依赖)
    - [步骤2: 配置测试环境](#步骤2-配置测试环境)
    - [步骤3: 验证连接](#步骤3-验证连接)
    - [步骤4: 运行第一个测试](#步骤4-运行第一个测试)
  - [配置说明](#配置说明)
    - [环境变量方式（推荐快速测试）](#环境变量方式推荐快速测试)
    - [配置文件方式（推荐生产环境）](#配置文件方式推荐生产环境)
  - [运行测试](#运行测试)
    - [基础命令](#基础命令)
    - [按功能运行](#按功能运行)
    - [按平台运行](#按平台运行)
    - [生成报告](#生成报告)
  - [常见场景](#常见场景)
    - [场景1: 测试vSphere认证](#场景1-测试vsphere认证)
    - [场景2: 测试VM生命周期](#场景2-测试vm生命周期)
    - [场景3: 测试libvirt性能监控](#场景3-测试libvirt性能监控)
    - [场景4: 测试资源管理](#场景4-测试资源管理)
    - [场景5: 运行完整测试套件](#场景5-运行完整测试套件)
  - [故障排查](#故障排查)
    - [问题1: vSphere连接失败](#问题1-vsphere连接失败)
    - [问题2: libvirt权限错误](#问题2-libvirt权限错误)
    - [问题3: 测试超时](#问题3-测试超时)
    - [问题4: 测试资源未清理](#问题4-测试资源未清理)
    - [问题5: 导入错误](#问题5-导入错误)
  - [📚 下一步](#-下一步)
    - [进阶阅读](#进阶阅读)
    - [扩展测试](#扩展测试)
    - [集成到CI/CD](#集成到cicd)
  - [🤝 获取帮助](#-获取帮助)

---

## 前提条件

### 系统要求

- Python 3.8+
- pip 包管理器
- （可选）虚拟环境工具

### 环境要求

#### vSphere测试

- vCenter Server 6.5+
- 具有管理员权限的账户
- 网络可访问vCenter

#### libvirt测试

- QEMU/KVM 虚拟化环境
- libvirt daemon 运行中
- root或具有libvirt组权限的用户

---

## 快速开始

### 步骤1: 安装依赖

```bash
# 进入测试目录
cd api_testing/python/tests/virtualization

# 安装vSphere依赖
pip install pyvmomi

# 安装libvirt依赖
pip install libvirt-python

# 安装测试框架
pip install pytest pytest-html pyyaml

# （可选）安装所有依赖
pip install -r ../../requirements.txt
```

### 步骤2: 配置测试环境

```bash
# 复制配置文件模板
cp config.yaml.example config.yaml

# 编辑配置文件（填写实际的连接信息）
nano config.yaml
```

**最小配置示例**:

```yaml
vsphere:
  host: "your-vcenter.example.com"
  admin:
    username: "administrator@vsphere.local"
    password: "YourPassword123!"
  ssl:
    verify_cert: false

libvirt:
  uri: "qemu:///system"
```

### 步骤3: 验证连接

```bash
# 测试vSphere连接
python3 -c "
from pyVim.connect import SmartConnectNoSSL, Disconnect
si = SmartConnectNoSSL(host='your-vcenter.example.com',
                       user='administrator@vsphere.local',
                       pwd='YourPassword123!')
print('vSphere连接成功!')
Disconnect(si)
"

# 测试libvirt连接
python3 -c "
import libvirt
conn = libvirt.open('qemu:///system')
print(f'libvirt连接成功! 主机: {conn.getHostname()}')
conn.close()
"
```

### 步骤4: 运行第一个测试

```bash
# 运行vSphere生命周期测试
pytest vsphere_lifecycle_test.py::vSphereLifecycleTestSuite::test_create_basic_vm -v -s

# 运行libvirt生命周期测试
pytest libvirt_lifecycle_test.py::LibvirtLifecycleTestSuite::test_define_domain -v -s
```

---

## 配置说明

### 环境变量方式（推荐快速测试）

```bash
# vSphere配置
export VSPHERE_HOST=vcenter.example.com
export VSPHERE_USER=administrator@vsphere.local
export VSPHERE_PASSWORD=YourPassword123!
export VSPHERE_VERIFY_SSL=false

# libvirt配置
export LIBVIRT_URI=qemu:///system

# 运行测试（无需config.yaml）
pytest vsphere_auth_test.py::vSphereAuthTestSuite::test_auth_valid_credentials -v
```

### 配置文件方式（推荐生产环境）

编辑 `config.yaml`:

```yaml
# vSphere完整配置
vsphere:
  host: "vcenter.example.com"
  port: 443

  admin:
    username: "administrator@vsphere.local"
    password: "YourAdminPassword123!"

  test_user:
    username: "testuser@vsphere.local"
    password: "YourTestPassword123!"

  ssl:
    verify_cert: false  # 测试环境可设为false
    cert_path: ""       # 生产环境指定证书路径

  test_environment:
    datacenter: "Datacenter1"
    cluster: "Cluster1"
    datastore: "datastore1"
    network: "VM Network"

  timeouts:
    connection: 30
    power_on: 300
    power_off: 120

# libvirt完整配置
libvirt:
  uri: "qemu:///system"  # 本地连接
  # uri: "qemu+ssh://user@remote-host/system"  # SSH远程连接
  # uri: "qemu+tcp://remote-host/system"       # TCP远程连接

  test_domain:
    name_prefix: "test-domain"
    vcpu_count: 2
    memory_mb: 1024
    disk_size_gb: 10

  storage:
    pool_name: "default"
    pool_path: "/var/lib/libvirt/images"
```

---

## 运行测试

### 基础命令

```bash
# 运行所有虚拟化测试
pytest -v

# 运行所有虚拟化测试（详细输出）
pytest -v -s

# 运行特定文件
pytest vsphere_lifecycle_test.py -v
pytest libvirt_advanced_test.py -v
```

### 按功能运行

```bash
# 运行生命周期测试
pytest -k "lifecycle" -v

# 运行认证测试
pytest -k "auth" -v

# 运行监控测试
pytest -k "monitor" -v

# 运行安全测试
pytest -k "security" -v
```

### 按平台运行

```bash
# 只运行vSphere测试
pytest vsphere_*.py -v

# 只运行libvirt测试
pytest libvirt_*.py -v
```

### 生成报告

```bash
# 生成HTML报告
pytest --html=report.html --self-contained-html

# 生成XML报告（JUnit格式）
pytest --junitxml=report.xml

# 生成覆盖率报告
pytest --cov=. --cov-report=html --cov-report=term
```

---

## 常见场景

### 场景1: 测试vSphere认证

```bash
# 测试基本认证
pytest vsphere_auth_test.py::vSphereAuthTestSuite::test_auth_valid_credentials -v -s

# 测试会话管理
pytest vsphere_auth_test.py::vSphereAuthTestSuite::test_session_creation -v -s

# 测试权限验证
pytest vsphere_auth_test.py::vSphereAuthTestSuite::test_permission_check_admin -v -s

# 运行所有认证测试
pytest vsphere_auth_test.py -v
```

### 场景2: 测试VM生命周期

```bash
# 完整生命周期测试
pytest vsphere_lifecycle_test.py::vSphereLifecycleTestSuite::test_full_lifecycle -v -s

# 分步测试
pytest vsphere_lifecycle_test.py::vSphereLifecycleTestSuite::test_create_basic_vm -v -s
pytest vsphere_lifecycle_test.py::vSphereLifecycleTestSuite::test_power_on_vm -v -s
pytest vsphere_lifecycle_test.py::vSphereLifecycleTestSuite::test_create_snapshot -v -s
```

### 场景3: 测试libvirt性能监控

```bash
# 测试域统计
pytest libvirt_advanced_test.py::LibvirtAdvancedTestSuite::test_monitor_domain_stats -v -s

# 测试连接统计
pytest libvirt_advanced_test.py::LibvirtAdvancedTestSuite::test_monitor_connection_stats -v -s

# 测试事件监听
pytest libvirt_advanced_test.py::LibvirtAdvancedTestSuite::test_events_lifecycle -v -s
```

### 场景4: 测试资源管理

```bash
# 测试CPU热插拔
pytest libvirt_advanced_test.py::LibvirtAdvancedTestSuite::test_resource_cpu_hotplug -v -s

# 测试内存气球
pytest libvirt_advanced_test.py::LibvirtAdvancedTestSuite::test_resource_memory_balloon -v -s

# 测试CPU绑定
pytest libvirt_advanced_test.py::LibvirtAdvancedTestSuite::test_resource_cpu_pinning -v -s
```

### 场景5: 运行完整测试套件

```bash
# 运行所有测试（输出摘要）
pytest -v --tb=short

# 运行所有测试（失败时停止）
pytest -v -x

# 运行所有测试（并行执行，需要安装pytest-xdist）
pip install pytest-xdist
pytest -v -n 4
```

---

## 故障排查

### 问题1: vSphere连接失败

**症状**: `Cannot complete login due to an incorrect user name or password`

**解决方案**:

```bash
# 1. 验证凭据
echo $VSPHERE_USER
echo $VSPHERE_HOST

# 2. 测试网络连接
ping vcenter.example.com
telnet vcenter.example.com 443

# 3. 检查SSL配置
# 如果使用自签名证书，确保 verify_cert: false
```

### 问题2: libvirt权限错误

**症状**: `Unable to connect to libvirt`

**解决方案**:

```bash
# 1. 检查libvirt服务
sudo systemctl status libvirtd

# 2. 添加用户到libvirt组
sudo usermod -a -G libvirt $USER
newgrp libvirt

# 3. 验证权限
virsh list --all
```

### 问题3: 测试超时

**症状**: 测试运行很长时间后超时

**解决方案**:

```yaml
# 在config.yaml中增加超时时间
vsphere:
  timeouts:
    connection: 60      # 增加到60秒
    power_on: 600       # 增加到10分钟

libvirt:
  timeouts:
    domain_start: 300   # 增加到5分钟
```

### 问题4: 测试资源未清理

**症状**: 测试后遗留VM/域

**解决方案**:

```bash
# 1. 手动清理vSphere测试VM
# 登录vCenter，删除名称包含 "test-vm-" 的虚拟机

# 2. 手动清理libvirt测试域
virsh list --all | grep test-domain
virsh destroy test-domain-xxxxx
virsh undefine test-domain-xxxxx

# 3. 启用自动清理
# 在config.yaml中设置
test_execution:
  cleanup:
    auto_cleanup: true
    cleanup_on_failure: true
```

### 问题5: 导入错误

**症状**: `ModuleNotFoundError: No module named 'pyVmomi'`

**解决方案**:

```bash
# 安装缺失的模块
pip install pyvmomi libvirt-python pytest pyyaml

# 使用requirements.txt安装所有依赖
pip install -r ../../requirements.txt

# 验证安装
python3 -c "import pyVmomi; print('pyvmomi OK')"
python3 -c "import libvirt; print('libvirt OK')"
```

---

## 📚 下一步

### 进阶阅读

- [虚拟化功能覆盖矩阵](VIRTUALIZATION_FULL_COVERAGE_MATRIX.md) - 完整功能列表
- [高级测试指南](ADVANCED_TESTING_GUIDE.md) - 高级测试技巧
- [测试覆盖矩阵](TEST_COVERAGE_MATRIX.md) - 容器化测试

### 扩展测试

```bash
# 编写自定义测试
cp vsphere_lifecycle_test.py my_custom_test.py
# 编辑 my_custom_test.py，添加你的测试用例

# 使用测试工具函数
from test_utils import load_test_config, Timer, retry_on_exception

# 运行自定义测试
pytest my_custom_test.py -v
```

### 集成到CI/CD

```yaml
# .github/workflows/virtualization-tests.yml
name: Virtualization Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        env:
          VSPHERE_HOST: ${{ secrets.VSPHERE_HOST }}
          VSPHERE_USER: ${{ secrets.VSPHERE_USER }}
          VSPHERE_PASSWORD: ${{ secrets.VSPHERE_PASSWORD }}
        run: |
          cd api_testing/python/tests/virtualization
          pytest --junitxml=report.xml
```

---

## 🤝 获取帮助

- 查看[完整文档](../VIRTUALIZATION_TEST_COMPLETE.md)
- 提交[Issue](../../issues)
- 查看[FAQ](FAQ.md)

---

**🎉 恭喜！您已经掌握了虚拟化测试的基础！**

继续探索高级功能，构建强大的测试体系！ 🚀
