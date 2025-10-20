# 监控告警

> **返回**: [运维管理首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [监控告警](#监控告警)
  - [📋 目录](#-目录)
  - [模块概述](#模块概述)
  - [文档列表](#文档列表)
  - [模块进度](#模块进度)
  - [学习路径](#学习路径)

---

## 模块概述

本模块提供Prometheus + Grafana + Alertmanager的完整监控告警方案，涵盖虚拟化和容器化环境的统一监控。

---

## 文档列表

1. [Prometheus监控体系](01_Prometheus监控体系.md)
2. [Grafana可视化](02_Grafana可视化.md)
3. [告警管理](03_告警管理.md)
4. [OpenTelemetry云原生可观测性](04_OpenTelemetry云原生可观测性.md) ⭐ **2025新增**

---

## 模块进度

| 文档名称 | 状态 | 备注 |
|---|---|---|
| 01_Prometheus监控体系.md | ✅ 已完成 | Prometheus架构、指标采集 (~560行) |
| 02_Grafana可视化.md | ✅ 已完成 | Dashboard设计、数据源配置 (~400行) |
| 03_告警管理.md | ✅ 已完成 | Alertmanager配置、告警规则 (~450行) |
| 04_OpenTelemetry云原生可观测性.md | ✅ 已完成 | OTLP、eBPF、Traces/Metrics/Logs (~1,206行) |

**模块总进度**: ✅ **100%** (4/4文档，约2,616行) **↑85%**

**最新增强** (2025-10-19):

- ✅ OpenTelemetry云原生可观测性：OTLP协议、三大支柱完整实现
- ✅ eBPF可观测性集成：Pixie、Cilium Hubble、Tetragon
- ✅ 完整的可观测性栈：Tempo+Prometheus+Loki+Grafana
- ✅ 自动Instrumentation、Context传播、性能优化

---

## 学习路径

1. Prometheus监控体系 → Grafana可视化 → 告警管理

---

**更新时间**: 2025-10-19  
**文档版本**: v2.0  
**状态**: ✅ **模块已增强 - 2025云原生可观测性标准对齐**
