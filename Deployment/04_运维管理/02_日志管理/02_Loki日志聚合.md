# Loki日志聚合

> **返回**: [日志管理首页](README.md) | [运维管理首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Loki日志聚合](#loki日志聚合)
  - [📋 目录](#-目录)
  - [1. Loki架构](#1-loki架构)
  - [2. Loki部署](#2-loki部署)
  - [3. Promtail配置](#3-promtail配置)
  - [4. LogQL查询](#4-logql查询)

---

## 1. Loki架构

**组件说明**:

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Promtail    │ →  │     Loki     │ ←  │   Grafana    │
│  (采集器)    │    │  (日志存储)  │    │  (查询界面)  │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 2. Loki部署

**Helm部署**:

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace logging \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=100Gi
```

---

## 3. Promtail配置

**DaemonSet部署**:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: promtail
  namespace: logging
spec:
  selector:
    matchLabels:
      app: promtail
  template:
    metadata:
      labels:
        app: promtail
    spec:
      containers:
      - name: promtail
        image: grafana/promtail:2.9.0
        args:
        - -config.file=/etc/promtail/promtail.yaml
        volumeMounts:
        - name: config
          mountPath: /etc/promtail
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: promtail-config
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

---

## 4. LogQL查询

**常用查询**:

```logql
# 查询特定Pod日志
{namespace="default", pod="myapp-xxxx"}

# 错误日志
{job="app"} |= "error"

# 统计错误数
sum(rate({job="app"} |= "error" [5m]))

# JSON解析
{job="app"} | json | status="500"
```

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 完成
