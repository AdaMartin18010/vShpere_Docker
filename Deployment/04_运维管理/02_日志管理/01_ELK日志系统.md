# ELK日志系统

> **返回**: [日志管理首页](README.md) | [运维管理首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [ELK日志系统](#elk日志系统)
  - [📋 目录](#-目录)
  - [1. ELK架构](#1-elk架构)
  - [2. Elasticsearch部署](#2-elasticsearch部署)
  - [3. Logstash配置](#3-logstash配置)
  - [4. Kibana可视化](#4-kibana可视化)

---

## 1. ELK架构

**组件说明**:

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Filebeat   │ →  │  Logstash    │ →  │Elasticsearch │
│  (采集器)    │    │  (处理器)    │    │  (存储)      │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                                        ┌──────▼───────┐
                                        │   Kibana     │
                                        │  (可视化)    │
                                        └──────────────┘
```

---

## 2. Elasticsearch部署

**Kubernetes部署**:

```yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: elasticsearch
  namespace: logging
spec:
  version: 8.11.0
  nodeSets:
  - name: default
    count: 3
    config:
      node.store.allow_mmap: false
    volumeClaimTemplates:
    - metadata:
        name: elasticsearch-data
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 100Gi
        storageClassName: rook-ceph-block
```

---

## 3. Logstash配置

**基础配置**:

```ruby
input {
  beats {
    port => 5044
  }
}

filter {
  if [type] == "nginx" {
    grok {
      match => { "message" => "%{COMBINEDAPACHELOG}" }
    }
    date {
      match => [ "timestamp" , "dd/MMM/yyyy:HH:mm:ss Z" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{[@metadata][beat]}-%{+YYYY.MM.dd}"
  }
}
```

---

## 4. Kibana可视化

**Kubernetes部署**:

```yaml
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: kibana
  namespace: logging
spec:
  version: 8.11.0
  count: 1
  elasticsearchRef:
    name: elasticsearch
```

**索引模式配置**:
1. Stack Management → Index Patterns
2. 创建模式: `filebeat-*`
3. 时间字段: `@timestamp`

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 完成

