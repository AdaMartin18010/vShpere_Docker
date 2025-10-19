# 边缘计算技术详解

## 📋 目录概览

本目录系统介绍边缘计算技术，涵盖KubeEdge、K3s、5G MEC等主流平台和技术。

---

## 📚 文档列表

### 00_边缘计算内容规划.md

**内容**: 完整的边缘计算专题规划

- 10个章节详细大纲
- 编写标准和质量要求
- 实施时间表
- 参考资料

**状态**: ✅ 完成

---

### 01_边缘计算概述与架构.md

**内容**: 边缘计算基础概念和架构设计

- 边缘计算定义和价值
- ETSI边缘计算参考架构
- 云原生边缘架构
- 主流技术栈对比（KubeEdge, K3s, OpenYurt等）
- 典型应用场景
- 技术挑战和解决方案
- 发展趋势

**字数**: 18,000+字  
**状态**: ✅ 完成

---

### 02_KubeEdge技术详解.md

**内容**: 华为KubeEdge深度解析

- 项目背景和架构
- CloudCore和EdgeCore组件
- 设备管理
- 应用部署
- 边缘自治
- 云边协同

**状态**: 🚧 规划中

---

### 03_K3s轻量级Kubernetes.md

**内容**: Rancher K3s详细指南

- K3s架构和特点
- 快速部署
- 高可用配置
- 边缘场景优化
- 与K8s对比

**状态**: 🚧 规划中

---

### 04_5G边缘计算(MEC).md

**内容**: 5G MEC技术详解

- MEC架构和标准
- 5G网络集成
- 超低延迟技术
- 网络切片
- 应用场景（车联网、工业互联网等）

**状态**: 🚧 规划中

---

### 05_边缘存储与数据管理.md

**内容**: 边缘存储方案

- 存储挑战
- Local Path Provisioner
- Longhorn, Rook, OpenEBS
- 数据分层和同步

**状态**: 🚧 规划中

---

### 06_边缘网络与服务网格.md

**内容**: 边缘网络技术

- 边缘网络特点
- CNI插件选择
- 云边通信机制
- 服务网格下沉

**状态**: 🚧 规划中

---

### 07_边缘安全.md

**内容**: 边缘安全架构

- 安全威胁
- 零信任架构
- 加密通信
- 运行时安全
- 合规性

**状态**: 🚧 规划中

---

### 08_边缘AI与MLOps.md

**内容**: 边缘AI技术

- 边缘AI概述
- 推理框架（TensorFlow Lite, ONNX Runtime, OpenVINO）
- 边缘训练和联邦学习
- MLOps实践
- 硬件加速

**状态**: 🚧 规划中

---

### 09_边缘监控与可观测性.md

**内容**: 边缘监控方案

- 监控挑战
- Prometheus边缘部署
- 日志管理（Fluentd, Loki）
- 可观测性（OpenTelemetry）

**状态**: 🚧 规划中

---

### 10_边缘计算最佳实践.md

**内容**: 生产实践总结

- 架构设计
- 资源规划
- 部署策略
- 故障处理
- 性能优化
- 案例研究

**状态**: 🚧 规划中

---

## 🎯 学习路径

### 初学者路径

```text
01_概述与架构 → 03_K3s快速上手 → 实践部署
```

**推荐步骤**:

1. 阅读[01_边缘计算概述与架构](./01_边缘计算概述与架构.md)理解基本概念
2. 学习[03_K3s轻量级Kubernetes](./03_K3s轻量级Kubernetes.md)（最简单入门）
3. 在树莓派或虚拟机上实践部署

### 进阶路径

```text
02_KubeEdge → 04_5G MEC → 05_存储 → 06_网络 → 07_安全
```

**推荐步骤**:

1. 深入[02_KubeEdge技术详解](./02_KubeEdge技术详解.md)学习企业级边缘
2. 理解[04_5G边缘计算](./04_5G边缘计算MEC.md)的MEC架构
3. 掌握边缘存储、网络和安全技术

### 专家路径

```text
全面学习 → AI边缘化 → 监控运维 → 最佳实践
```

**推荐步骤**:

1. 系统学习所有章节
2. 重点研究[08_边缘AI与MLOps](./08_边缘AI与MLOps.md)
3. 实施[10_边缘计算最佳实践](./10_边缘计算最佳实践.md)

---

## 📊 技术选型指南

### 快速选型表

| 场景 | 推荐技术 | 原因 |
|------|---------|------|
| **资源极度受限** | K3s | 内存<512MB，极简架构 |
| **大规模IoT设备** | KubeEdge | 10K+设备，内置设备管理 |
| **现有K8s扩展** | OpenYurt | 无侵入，平滑迁移 |
| **Azure生态** | Azure IoT Edge | 深度集成，企业支持 |
| **AWS生态** | AWS Greengrass | Lambda@Edge，ML推理 |
| **5G场景** | MEC平台 | 超低延迟，网络切片 |
| **AI推理** | K3s + TensorRT | GPU加速，轻量部署 |

### 详细选型对比

参考[01_边缘计算概述与架构 - 技术栈对比](./01_边缘计算概述与架构.md#技术栈对比)章节。

---

## 🛠️ 快速开始

### 环境要求

**最小配置**:

- CPU: 1核
- 内存: 512MB
- 存储: 10GB
- OS: Linux (Ubuntu 22.04推荐)

**推荐配置**:

- CPU: 2核+
- 内存: 2GB+
- 存储: 50GB+
- 网络: 稳定互联网连接

### K3s快速安装

```bash
# Server节点
curl -sfL https://get.k3s.io | sh -

# 验证
kubectl get nodes

# Agent节点加入
curl -sfL https://get.k3s.io | K3S_URL=https://server-ip:6443 K3S_TOKEN=<token> sh -
```

### KubeEdge快速安装

```bash
# 云端安装CloudCore
keadm init --advertise-address="<cloud-ip>" --kubeedge-version=v1.18.0

# 获取token
keadm gettoken

# 边缘节点安装EdgeCore
keadm join --cloudcore-ipport="<cloud-ip>:10000" --token="<token>"
```

---

## 📈 项目进度

| 章节 | 规划 | 编写 | 审核 | 状态 |
|------|------|------|------|------|
| 00_内容规划 | ✅ | ✅ | ✅ | 完成 |
| 01_概述与架构 | ✅ | ✅ | 🚧 | 完成 |
| 02_KubeEdge | ✅ | ⬜ | ⬜ | 规划中 |
| 03_K3s | ✅ | ⬜ | ⬜ | 规划中 |
| 04_5G MEC | ✅ | ⬜ | ⬜ | 规划中 |
| 05_存储 | ✅ | ⬜ | ⬜ | 规划中 |
| 06_网络 | ✅ | ⬜ | ⬜ | 规划中 |
| 07_安全 | ✅ | ⬜ | ⬜ | 规划中 |
| 08_AI/ML | ✅ | ⬜ | ⬜ | 规划中 |
| 09_监控 | ✅ | ⬜ | ⬜ | 规划中 |
| 10_实践 | ✅ | ⬜ | ⬜ | 规划中 |

**完成度**: 20% (2/10章节完成)

---

## 🤝 贡献指南

欢迎贡献边缘计算相关内容！

**贡献方式**:

1. 补充现有章节内容
2. 添加实践案例
3. 提供配置示例
4. 完善技术细节
5. 翻译英文资料

**贡献流程**:

1. Fork项目
2. 创建分支: `git checkout -b docs/edge-xxx`
3. 提交修改: 遵循[贡献指南](../../CONTRIBUTING.md)
4. 提交PR: 详细说明变更内容

---

## 📞 反馈与支持

**问题反馈**:

- GitHub Issues: [提交Issue](https://github.com/YOUR_USERNAME/vShpere_Docker/issues)
- 标签: `edge-computing`, `documentation`

**技术讨论**:

- GitHub Discussions: [参与讨论](https://github.com/YOUR_USERNAME/vShpere_Docker/discussions)
- 主题: 边缘计算技术交流

---

## 📚 相关资源

**社区**:

- [CNCF Edge Computing WG](https://github.com/cncf/wg-edge)
- [KubeEdge Community](https://kubeedge.io/community/)
- [K3s Community](https://k3s.io/community/)
- [LF Edge](https://www.lfedge.org/)

**官方文档**:

- [KubeEdge Docs](https://kubeedge.io/docs/)
- [K3s Docs](https://docs.k3s.io/)
- [OpenYurt Docs](https://openyurt.io/docs/)
- [ETSI MEC](https://www.etsi.org/technologies/multi-access-edge-computing)

**技术博客**:

- [CNCF Blog - Edge](https://www.cncf.io/blog/tag/edge/)
- [KubeEdge Blog](https://kubeedge.io/blog/)
- [Rancher Blog - K3s](https://www.rancher.com/blog/tag/k3s)

---

**文档版本**: v1.0  
**最后更新**: 2025-10-19  
**维护者**: 虚拟化容器化技术知识库项目组

**返回**: [Container目录](../README.md) | [项目首页](../../README.md)
