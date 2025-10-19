# Grafana可视化

> **返回**: [监控告警首页](README.md) | [运维管理首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Grafana可视化](#grafana可视化)
  - [📋 目录](#-目录)
  - [1. Grafana部署](#1-grafana部署)
    - [1.1 Kubernetes部署](#11-kubernetes部署)
    - [1.2 配置文件](#12-配置文件)
  - [2. 数据源配置](#2-数据源配置)
    - [2.1 Prometheus数据源](#21-prometheus数据源)
    - [2.2 多集群数据源](#22-多集群数据源)
  - [3. Dashboard设计](#3-dashboard设计)
    - [3.1 集群监控Dashboard](#31-集群监控dashboard)
    - [3.2 应用监控Dashboard](#32-应用监控dashboard)
    - [3.3 变量与模板](#33-变量与模板)
    - [3.4 推荐Dashboard](#34-推荐dashboard)
  - [4. 告警配置](#4-告警配置)
    - [4.1 Grafana告警规则](#41-grafana告警规则)
    - [4.2 通知渠道](#42-通知渠道)
    - [4.3 告警最佳实践](#43-告警最佳实践)

---

## 1. Grafana部署

### 1.1 Kubernetes部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:10.2.0
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_USER
          value: admin
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-secret
              key: admin-password
        - name: GF_INSTALL_PLUGINS
          value: "grafana-piechart-panel,grafana-worldmap-panel"
        volumeMounts:
        - name: data
          mountPath: /var/lib/grafana
        - name: config
          mountPath: /etc/grafana/grafana.ini
          subPath: grafana.ini
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: grafana-pvc
      - name: config
        configMap:
          name: grafana-config
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
spec:
  type: LoadBalancer
  selector:
    app: grafana
  ports:
  - port: 80
    targetPort: 3000
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-pvc
  namespace: monitoring
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: rook-ceph-block
```

### 1.2 配置文件

**grafana.ini**:

```ini
[server]
protocol = http
http_port = 3000
domain = grafana.example.com
root_url = %(protocol)s://%(domain)s/

[security]
admin_user = admin
admin_password = ${GF_SECURITY_ADMIN_PASSWORD}

[auth]
disable_login_form = false

[auth.anonymous]
enabled = false

[database]
type = sqlite3
path = /var/lib/grafana/grafana.db

[session]
provider = file
provider_config = sessions

[analytics]
reporting_enabled = false
check_for_updates = true

[log]
mode = console
level = info
```

---

## 2. 数据源配置

### 2.1 Prometheus数据源

**通过UI配置**:

1. Configuration → Data Sources → Add data source
2. 选择 Prometheus
3. 配置:
   - Name: `Prometheus`
   - URL: `http://prometheus:9090`
   - Access: `Server (default)`
   - Scrape interval: `15s`

**通过配置文件**:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: monitoring
data:
  datasources.yaml: |
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      access: proxy
      url: http://prometheus:9090
      isDefault: true
      jsonData:
        timeInterval: "15s"
        httpMethod: "POST"
    - name: Loki
      type: loki
      access: proxy
      url: http://loki:3100
      jsonData:
        maxLines: 1000
```

### 2.2 多集群数据源

```yaml
datasources:
- name: Prometheus-Prod
  type: prometheus
  url: http://prometheus-prod:9090
- name: Prometheus-Dev
  type: prometheus
  url: http://prometheus-dev:9090
- name: Prometheus-Global (Thanos)
  type: prometheus
  url: http://thanos-query:9090
```

---

## 3. Dashboard设计

### 3.1 集群监控Dashboard

**Kubernetes集群概览**:

```json
{
  "dashboard": {
    "title": "Kubernetes集群监控",
    "panels": [
      {
        "title": "节点状态",
        "targets": [{
          "expr": "kube_node_status_condition{condition=\"Ready\",status=\"true\"}"
        }],
        "type": "stat"
      },
      {
        "title": "Pod数量",
        "targets": [{
          "expr": "sum(kube_pod_info)"
        }],
        "type": "stat"
      },
      {
        "title": "CPU使用率",
        "targets": [{
          "expr": "100 - (avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
        }],
        "type": "gauge"
      },
      {
        "title": "内存使用率",
        "targets": [{
          "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"
        }],
        "type": "gauge"
      }
    ]
  }
}
```

### 3.2 应用监控Dashboard

**HTTP服务监控**:

| Panel | Query | 可视化类型 |
|-------|-------|-----------|
| **请求QPS** | `rate(http_requests_total[5m])` | Graph |
| **错误率** | `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100` | Graph |
| **P99延迟** | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` | Graph |
| **Top慢接口** | `topk(10, histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])))` | Table |

### 3.3 变量与模板

**Dashboard变量**:

```json
{
  "templating": {
    "list": [
      {
        "name": "datasource",
        "type": "datasource",
        "query": "prometheus"
      },
      {
        "name": "cluster",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(up, cluster)"
      },
      {
        "name": "namespace",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(kube_pod_info{cluster=\"$cluster\"}, namespace)"
      },
      {
        "name": "pod",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(kube_pod_info{namespace=\"$namespace\"}, pod)"
      }
    ]
  }
}
```

### 3.4 推荐Dashboard

**官方Dashboard ID**:

| ID | 名称 | 适用场景 |
|----|------|---------|
| 315 | Kubernetes cluster monitoring | K8s集群监控 |
| 1860 | Node Exporter Full | 主机监控 |
| 13639 | Kubernetes / Views / Pods | Pod详细监控 |
| 12006 | Kubernetes apiserver | API Server监控 |
| 7249 | Kubernetes Cluster (Prometheus) | 集群总览 |

**导入方法**:

```bash
# 通过ID导入
Dashboard → Import → 输入Dashboard ID

# 通过JSON导入
Dashboard → Import → 上传JSON文件
```

---

## 4. 告警配置

### 4.1 Grafana告警规则

```json
{
  "alert": {
    "name": "High CPU Usage",
    "conditions": [
      {
        "evaluator": {
          "params": [90],
          "type": "gt"
        },
        "operator": {
          "type": "and"
        },
        "query": {
          "params": ["A", "5m", "now"]
        },
        "reducer": {
          "type": "avg"
        },
        "type": "query"
      }
    ],
    "frequency": "1m",
    "handler": 1,
    "message": "CPU使用率超过90%",
    "name": "High CPU Usage"
  }
}
```

### 4.2 通知渠道

**配置Slack**:

```yaml
apiVersion: 1
contactPoints:
- orgId: 1
  name: Slack
  receivers:
  - uid: slack-1
    type: slack
    settings:
      url: https://hooks.slack.com/services/xxx/yyy/zzz
      recipient: '#alerts'
      username: Grafana
```

**配置Email**:

```ini
[smtp]
enabled = true
host = smtp.gmail.com:587
user = your-email@gmail.com
password = your-password
from_address = grafana@example.com
from_name = Grafana
```

**配置钉钉**:

```yaml
contactPoints:
- name: DingTalk
  receivers:
  - type: webhook
    settings:
      url: https://oapi.dingtalk.com/robot/send?access_token=xxxxx
      httpMethod: POST
```

### 4.3 告警最佳实践

**告警级别**:

```text
Critical (P1): 立即处理
  - 服务完全不可用
  - 数据丢失风险
  
High (P2): 1小时内处理
  - 性能严重下降
  - 部分功能不可用
  
Medium (P3): 当天处理
  - 资源使用率高
  - 非关键服务异常
  
Low (P4): 周内处理
  - 优化建议
  - 预警信息
```

**告警抑制**:

```yaml
# 避免告警风暴
inhibit_rules:
- source_match:
    severity: 'critical'
  target_match:
    severity: 'warning'
  equal: ['alertname', 'instance']
```

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 完成
