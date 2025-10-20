# 容器网络指南

> **返回**: [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [容器网络指南](#容器网络指南)
  - [📋 目录](#-目录)
  - [模块概述](#模块概述)
  - [文档列表](#文档列表)
  - [模块进度](#模块进度)
  - [学习路径](#学习路径)
    - [基础路径](#基础路径)
    - [进阶路径](#进阶路径)
    - [生产环境路径](#生产环境路径)

---

## 模块概述

本模块详细介绍Kubernetes容器网络的完整解决方案，从CNI网络规范、主流网络插件（Calico、Cilium），到网络策略配置和网络安全。涵盖生产级容器网络所需的全部知识点。

**核心内容**:

- CNI网络规范与工作原理
- 主流CNI插件对比与选型
- Calico网络配置与BGP模式
- Cilium eBPF网络与Hubble可观测性
- NetworkPolicy网络策略与安全

---

## 文档列表

1. [CNI网络概述](01_CNI网络概述.md)
2. [Calico网络配置](02_Calico网络配置.md)
3. [Cilium eBPF网络](03_Cilium_eBPF网络.md)
4. [NetworkPolicy策略](04_NetworkPolicy策略.md)

---

## 模块进度

| 文档名称 | 状态 | 备注 |
|---|---|---|
| 01_CNI网络概述.md | ✅ 已完成 | CNI规范、插件对比、网络模型 (~821行) |
| 02_Calico网络配置.md | ✅ 已完成 | Calico架构、BGP、IPAM (~917行) |
| 03_Cilium_eBPF网络.md | ✅ 已增强 | Cilium 1.14+、Gateway API、Tetragon (~1,140行) |
| 04_NetworkPolicy策略.md | ✅ 已完成 | 网络策略、Ingress/Egress规则 (~988行) |

**模块总进度**: ✅ **100%** (4/4文档，约3,866行) **↑6.2%**

**最新增强** (2025-10-19):

- ✅ Cilium模块：新增Cilium 1.14+新特性（+224行，+24%）
- ✅ Gateway API集成、Service Mesh增强、Tetragon安全
- ✅ BGP Control Plane、Cluster Mesh、性能优化

---

## 学习路径

### 基础路径

1. CNI网络概述 → NetworkPolicy策略

### 进阶路径

1. CNI网络概述 → Calico网络配置 → NetworkPolicy策略

### 生产环境路径

1. CNI网络概述 → Calico/Cilium网络配置 → NetworkPolicy策略 → 网络监控与故障排查

---

**更新时间**: 2025-10-19  
**文档版本**: v2.0  
**状态**: ✅ **模块已增强 - 2025技术标准对齐**
