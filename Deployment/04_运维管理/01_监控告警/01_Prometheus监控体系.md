# Prometheus监控体系

> **返回**: [监控告警首页](README.md) | [运维管理首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Prometheus监控体系](#prometheus监控体系)
  - [📋 目录](#-目录)
  - [1. Prometheus架构](#1-prometheus架构)
  - [2. 部署配置](#2-部署配置)
    - [2.1 Kubernetes部署](#21-kubernetes部署)
    - [2.2 Prometheus配置](#22-prometheus配置)
  - [3. 指标采集](#3-指标采集)
    - [3.1 VM监控 (Node Exporter)](#31-vm监控-node-exporter)
    - [3.2 Kubernetes监控](#32-kubernetes监控)
    - [3.3 应用监控](#33-应用监控)
  - [4. 监控最佳实践](#4-监控最佳实践)
    - [4.1 指标命名规范](#41-指标命名规范)
    - [4.2 PromQL查询](#42-promql查询)
    - [4.3 数据保留策略](#43-数据保留策略)
    - [4.4 高可用架构](#44-高可用架构)

---

## 1. Prometheus架构

**核心组件**:

```text
┌──────────────────────────────────────────────────────────┐
│                   Prometheus Server                      │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐        │
│  │  Retrieval │  │   TSDB     │  │  HTTP Server │        │
│  │  (Pull)    │  │  (Storage) │  │   (PromQL)   │        │
│  └────────────┘  └────────────┘  └──────────────┘        │
└────────┬──────────────────────────────────┬──────────────┘
         │                                  │
         │ Pull Metrics                     │ Query
         │                                  │
    ┌────▼─────────┐              ┌────────▼─────────┐
    │   Targets    │              │    Grafana       │
    │              │              │   (Visualization)│
    │ - Exporters  │              └──────────────────┘
    │ - Apps       │
    │ - Kubernetes │              ┌──────────────────┐
    └──────────────┘              │  Alertmanager    │
                                  │   (Alerting)     │
                                  └──────────────────┘
```

**数据模型**:

```text
Metric Name + Labels → Time Series
  http_requests_total{method="GET", handler="/api/users"} → [timestamp, value]
```

---

## 2. 部署配置

### 2.1 Kubernetes部署

**Prometheus Operator部署**:

```bash
# 安装Prometheus Operator
kubectl create namespace monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus-operator prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=100Gi
```

**手动部署Prometheus**:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: prometheus
  namespace: monitoring
spec:
  serviceName: prometheus
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
      - name: prometheus
        image: prom/prometheus:v2.45.0
        args:
        - '--config.file=/etc/prometheus/prometheus.yml'
        - '--storage.tsdb.path=/prometheus'
        - '--storage.tsdb.retention.time=30d'
        - '--web.enable-lifecycle'
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: data
          mountPath: /prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: rook-ceph-block
      resources:
        requests:
          storage: 100Gi
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
```

### 2.2 Prometheus配置

**prometheus.yml**:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'prod'
    environment: 'production'

# 告警规则文件
rule_files:
  - '/etc/prometheus/rules/*.yml'

# Alertmanager配置
alerting:
  alertmanagers:
  - static_configs:
    - targets: ['alertmanager:9093']

# 抓取配置
scrape_configs:
# Prometheus自身监控
- job_name: 'prometheus'
  static_configs:
  - targets: ['localhost:9090']

# Kubernetes服务发现
- job_name: 'kubernetes-nodes'
  kubernetes_sd_configs:
  - role: node
  relabel_configs:
  - action: labelmap
    regex: __meta_kubernetes_node_label_(.+)

- job_name: 'kubernetes-pods'
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
    action: keep
    regex: true
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
    action: replace
    target_label: __metrics_path__
    regex: (.+)
  - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
    action: replace
    regex: ([^:]+)(?::\d+)?;(\d+)
    replacement: $1:$2
    target_label: __address__

# VM监控 (Node Exporter)
- job_name: 'vm-nodes'
  static_configs:
  - targets:
    - '172.16.1.10:9100'
    - '172.16.1.11:9100'
    - '172.16.1.12:9100'
    labels:
      env: 'vm'
      datacenter: 'dc1'

# VMware vCenter监控
- job_name: 'vmware'
  static_configs:
  - targets: ['vmware-exporter:9272']

# Kubernetes集群监控
- job_name: 'kube-state-metrics'
  static_configs:
  - targets: ['kube-state-metrics:8080']

# Kubernetes节点监控
- job_name: 'node-exporter'
  kubernetes_sd_configs:
  - role: endpoints
  relabel_configs:
  - source_labels: [__meta_kubernetes_endpoints_name]
    regex: 'node-exporter'
    action: keep
```

---

## 3. 指标采集

### 3.1 VM监控 (Node Exporter)

**安装Node Exporter**:

```bash
# 下载安装
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
sudo mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/

# 创建systemd服务
sudo tee /etc/systemd/system/node_exporter.service << EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
User=prometheus
ExecStart=/usr/local/bin/node_exporter \\
  --collector.filesystem.mount-points-exclude="^/(dev|proc|sys|run)($|/)" \\
  --collector.textfile.directory=/var/lib/node_exporter/textfile_collector

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

**关键指标**:

| 指标 | 说明 | 告警阈值 |
|------|------|---------|
| `node_cpu_seconds_total` | CPU使用时间 | >90% |
| `node_memory_MemAvailable_bytes` | 可用内存 | <10% |
| `node_filesystem_avail_bytes` | 磁盘可用空间 | <10% |
| `node_disk_io_time_seconds_total` | 磁盘I/O时间 | >80% |
| `node_network_receive_bytes_total` | 网络接收字节 | - |

### 3.2 Kubernetes监控

**部署监控组件**:

```bash
# Node Exporter (DaemonSet)
kubectl apply -f - << EOF
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9100"
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: node-exporter
        image: prom/node-exporter:v1.6.1
        args:
        - '--path.procfs=/host/proc'
        - '--path.sysfs=/host/sys'
        - '--path.rootfs=/host/root'
        - '--collector.filesystem.mount-points-exclude=^/(dev|proc|sys|run)($|/)'
        ports:
        - containerPort: 9100
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
        - name: root
          mountPath: /host/root
          readOnly: true
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
      - name: root
        hostPath:
          path: /
EOF

# Kube State Metrics
kubectl apply -f https://github.com/kubernetes/kube-state-metrics/releases/download/v2.10.0/kube-state-metrics-standard.yaml

# cAdvisor (内置于Kubelet)
# 默认监听: https://<node-ip>:10250/metrics/cadvisor
```

**关键指标**:

```yaml
# Pod监控
- container_cpu_usage_seconds_total
- container_memory_working_set_bytes
- container_network_receive_bytes_total
- container_fs_usage_bytes

# 集群监控
- kube_node_status_condition
- kube_pod_status_phase
- kube_deployment_status_replicas
- kube_service_info
```

### 3.3 应用监控

**Go应用 (内置支持)**:

```go
package main

import (
    "net/http"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    httpRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )
    
    httpRequestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "HTTP request latency",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "endpoint"},
    )
)

func init() {
    prometheus.MustRegister(httpRequestsTotal)
    prometheus.MustRegister(httpRequestDuration)
}

func main() {
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":8080", nil)
}
```

**Java应用 (Micrometer)**:

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
    <version>1.11.0</version>
</dependency>
```

```java
@Configuration
public class MonitoringConfig {
    @Bean
    MeterRegistryCustomizer<MeterRegistry> metricsCommonTags() {
        return registry -> registry.config().commonTags("application", "myapp");
    }
}
```

---

## 4. 监控最佳实践

### 4.1 指标命名规范

**命名规则**:

```text
<namespace>_<name>_<unit>

例如:
- http_requests_total          # Counter
- http_request_duration_seconds # Histogram
- node_memory_available_bytes   # Gauge
```

**标签使用**:

```text
# 好的标签
http_requests_total{method="GET", handler="/api/users", status="200"}

# 避免高基数标签
http_requests_total{user_id="12345"}  # ❌ 用户ID数量太多
http_requests_total{timestamp="..."}   # ❌ 时间戳不应作为标签
```

### 4.2 PromQL查询

**常用查询**:

```promql
# CPU使用率
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 磁盘使用率
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100

# Pod重启次数 (近1小时)
increase(kube_pod_container_status_restarts_total[1h]) > 0

# HTTP请求QPS
rate(http_requests_total[5m])

# HTTP请求P99延迟
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# 容器内存使用率Top 10
topk(10, 
  container_memory_working_set_bytes{container!="", pod!=""} / 
  container_spec_memory_limit_bytes{container!="", pod!=""} * 100
)
```

### 4.3 数据保留策略

**多层存储**:

```yaml
# 短期 (Prometheus本地)
--storage.tsdb.retention.time=30d

# 长期 (Thanos/Cortex)
apiVersion: v1
kind: ConfigMap
metadata:
  name: thanos-objstore-config
data:
  thanos.yaml: |
    type: s3
    config:
      bucket: prometheus-metrics
      endpoint: minio:9000
      access_key: ${ACCESS_KEY}
      secret_key: ${SECRET_KEY}
```

**降采样规则**:

```yaml
# Thanos Downsampling
- raw data: 30 days (5s resolution)
- 5m resolution: 180 days
- 1h resolution: 1 year
```

### 4.4 高可用架构

**Prometheus联邦**:

```yaml
# 全局Prometheus (联邦查询)
scrape_configs:
- job_name: 'federate'
  honor_labels: true
  metrics_path: '/federate'
  params:
    'match[]':
    - '{job="prometheus"}'
    - '{__name__=~"job:.*"}'
  static_configs:
  - targets:
    - 'prometheus-1:9090'
    - 'prometheus-2:9090'
```

**Thanos架构**:

```text
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Prometheus1 │  │ Prometheus2 │  │ Prometheus3 │
│ + Sidecar   │  │ + Sidecar   │  │ + Sidecar   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┴────────────────┘
                        │
              ┌─────────▼──────────┐
              │  Thanos Store      │
              │  (S3 Storage)      │
              └─────────┬──────────┘
                        │
              ┌─────────▼──────────┐
              │  Thanos Query      │
              │  (Global View)     │
              └─────────┬──────────┘
                        │
                  ┌─────▼─────┐
                  │  Grafana  │
                  └───────────┘
```

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 完成
