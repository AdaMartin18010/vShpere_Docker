# NetworkPolicy策略

> **返回**: [容器网络目录](README.md) | [容器化部署首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [NetworkPolicy策略](#networkpolicy策略)
  - [📋 目录](#-目录)
  - [1. NetworkPolicy概述](#1-networkpolicy概述)
  - [2. NetworkPolicy规范](#2-networkpolicy规范)
  - [3. 基础策略示例](#3-基础策略示例)
    - [默认拒绝所有流量](#默认拒绝所有流量)
    - [允许特定流量](#允许特定流量)
  - [4. 高级策略配置](#4-高级策略配置)
    - [多选择器组合](#多选择器组合)
  - [5. 常用策略模式](#5-常用策略模式)
    - [Web应用三层架构](#web应用三层架构)
    - [微服务架构](#微服务架构)
    - [多租户隔离](#多租户隔离)
  - [6. Calico NetworkPolicy](#6-calico-networkpolicy)
  - [7. Cilium NetworkPolicy](#7-cilium-networkpolicy)
  - [8. 故障排查](#8-故障排查)
  - [9. 性能优化](#9-性能优化)
  - [10. 最佳实践](#10-最佳实践)
  - [相关文档](#相关文档)

---

## 1. NetworkPolicy概述

```yaml
NetworkPolicy_Overview:
  定义:
    - Kubernetes网络策略资源
    - Pod级别防火墙
    - 声明式网络安全
    - 基于标签选择
  
  工作原理:
    - CNI插件实现
    - 默认允许所有流量
    - 策略累加生效
    - Namespace级别
  
  支持的CNI:
    - Calico: ✅ 完整支持
    - Cilium: ✅ 完整支持 + L7
    - Weave: ✅ 支持
    - Flannel: ❌ 不支持
    - Kube-router: ✅ 支持
  
  策略类型:
    Ingress (入站):
      - 控制进入Pod的流量
      - 源Pod/IP/端口
    
    Egress (出站):
      - 控制离开Pod的流量
      - 目标Pod/IP/端口
  
  选择器类型:
    podSelector:
      - 选择应用策略的Pod
      - 基于标签匹配
    
    namespaceSelector:
      - 选择命名空间
      - 跨命名空间策略
    
    ipBlock:
      - CIDR范围
      - 外部IP访问控制
```

---

## 2. NetworkPolicy规范

```yaml
NetworkPolicy_Specification:
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  
  metadata:
    name: 策略名称
    namespace: 命名空间
  
  spec:
    # 应用到哪些Pod
    podSelector:
      matchLabels:
        key: value
    
    # 策略类型
    policyTypes:
    - Ingress  # 入站规则
    - Egress   # 出站规则
    
    # 入站规则
    ingress:
    - from:
      - podSelector: {}
      - namespaceSelector: {}
      - ipBlock:
          cidr: IP范围
          except: 排除IP
      ports:
      - protocol: TCP/UDP/SCTP
        port: 端口号或名称
    
    # 出站规则
    egress:
    - to:
      - podSelector: {}
      - namespaceSelector: {}
      - ipBlock: {}
      ports:
      - protocol: TCP/UDP/SCTP
        port: 端口号或名称
```

---

## 3. 基础策略示例

### 默认拒绝所有流量

```yaml
# ========================================
# 1. 拒绝所有入站流量
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}  # 应用到所有Pod
  policyTypes:
  - Ingress

---
# ========================================
# 2. 拒绝所有出站流量
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress

---
# ========================================
# 3. 拒绝所有入站和出站
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### 允许特定流量

```yaml
# ========================================
# 允许来自特定Pod的流量
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080

---
# ========================================
# 允许来自特定命名空间的流量
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-monitoring
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090

---
# ========================================
# 允许来自特定IP的流量
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-office
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: admin-panel
  ingress:
  - from:
    - ipBlock:
        cidr: 203.0.113.0/24  # 办公网IP
        except:
        - 203.0.113.5/32     # 排除特定IP
    ports:
    - protocol: TCP
      port: 443

---
# ========================================
# 允许出站到DNS
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53

---
# ========================================
# 允许出站到外部API
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-external-api
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 169.254.169.254/32  # 屏蔽云提供商元数据服务
    ports:
    - protocol: TCP
      port: 443
```

---

## 4. 高级策略配置

### 多选择器组合

```yaml
# ========================================
# AND条件: 同一from块内的选择器
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-specific-namespace-pod
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          env: production
      podSelector:
        matchLabels:
          app: frontend
    # 只允许来自production命名空间中带有app=frontend标签的Pod

---
# ========================================
# OR条件: 不同from块
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-multiple-sources
spec:
  podSelector:
    matchLabels:
      app: database
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend
  - from:
    - podSelector:
        matchLabels:
          app: cronjob
    # 允许来自backend或cronjob的Pod

---
# ========================================
# 多端口规则
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-multiple-ports
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: lb
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 8080

---
# ========================================
# 命名端口
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-named-ports
spec:
  podSelector:
    matchLabels:
      app: myapp
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: client
    ports:
    - protocol: TCP
      port: http  # 使用Pod定义的命名端口
```

---

## 5. 常用策略模式

### Web应用三层架构

```yaml
# ========================================
# 前端层 - 只允许来自Ingress
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-policy
  namespace: webapp
spec:
  podSelector:
    matchLabels:
      tier: frontend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: backend
    ports:
    - protocol: TCP
      port: 8080
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53

---
# ========================================
# 后端层 - 只允许来自前端
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: webapp
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53

---
# ========================================
# 数据库层 - 只允许来自后端
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-policy
  namespace: webapp
spec:
  podSelector:
    matchLabels:
      tier: database
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: backend
    ports:
    - protocol: TCP
      port: 5432
  egress:
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

### 微服务架构

```yaml
# ========================================
# 服务A - API网关
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-gateway-policy
  namespace: microservices
spec:
  podSelector:
    matchLabels:
      app: api-gateway
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - ipBlock:
        cidr: 0.0.0.0/0
    ports:
    - protocol: TCP
      port: 443
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: user-service
  - to:
    - podSelector:
        matchLabels:
          app: order-service
  - to:
    - podSelector:
        matchLabels:
          app: product-service
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53

---
# ========================================
# 服务间通信
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: service-mesh-policy
  namespace: microservices
spec:
  podSelector:
    matchLabels:
      service: "true"
  ingress:
  - from:
    - podSelector:
        matchLabels:
          service: "true"
  egress:
  - to:
    - podSelector:
        matchLabels:
          service: "true"
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

### 多租户隔离

```yaml
# ========================================
# 租户A命名空间隔离
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tenant-a-isolation
  namespace: tenant-a
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: tenant-a
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: tenant-a
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0

---
# ========================================
# 共享服务访问
# ========================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: shared-services-access
  namespace: shared-services
spec:
  podSelector:
    matchLabels:
      shared: "true"
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          tenant: "true"
```

---

## 6. Calico NetworkPolicy

```yaml
# Calico扩展功能
Calico_NetworkPolicy:
  GlobalNetworkPolicy:
    - 集群级别策略
    - 不限命名空间
    - 优先级控制
  
  增强功能:
    - ICMP规则
    - 更灵活的选择器
    - 日志记录
    - 优先级（order）
    - 全局策略
```

**Calico策略示例**:

```yaml
# ========================================
# Calico GlobalNetworkPolicy
# ========================================
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: deny-all-by-default
spec:
  selector: all()
  types:
  - Ingress
  - Egress
  order: 1000  # 优先级，数字越小优先级越高

---
# ========================================
# 允许集群内部通信
# ========================================
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: allow-cluster-internal
spec:
  selector: has(kubernetes.io/hostname)
  types:
  - Ingress
  ingress:
  - action: Allow
    source:
      nets:
      - 10.244.0.0/16  # Pod CIDR
      - 10.96.0.0/12   # Service CIDR
  order: 100

---
# ========================================
# ICMP规则
# ========================================
apiVersion: projectcalico.org/v3
kind: NetworkPolicy
metadata:
  name: allow-icmp
  namespace: production
spec:
  selector: app == 'myapp'
  types:
  - Ingress
  ingress:
  - action: Allow
    protocol: ICMP
    icmp:
      type: 8  # Echo Request (ping)

---
# ========================================
# 日志记录
# ========================================
apiVersion: projectcalico.org/v3
kind: NetworkPolicy
metadata:
  name: log-denied-traffic
  namespace: production
spec:
  selector: app == 'sensitive'
  types:
  - Ingress
  ingress:
  - action: Log
    protocol: TCP
    source:
      notSelector: trusted == 'true'
  - action: Deny
    protocol: TCP
    source:
      notSelector: trusted == 'true'
```

---

## 7. Cilium NetworkPolicy

```yaml
# Cilium扩展功能
Cilium_NetworkPolicy:
  CiliumNetworkPolicy:
    - L7协议感知
    - HTTP/gRPC/Kafka策略
    - DNS策略
    - 服务FQDN
  
  L7功能:
    - URL路径过滤
    - HTTP方法限制
    - Header匹配
    - API端点控制
```

**Cilium策略示例** (见[Cilium文档](03_Cilium_eBPF网络.md#7-l7网络策略))

---

## 8. 故障排查

```bash
# ========================================
# 查看NetworkPolicy
# ========================================

# 列出策略
kubectl get networkpolicy -A

# 查看详情
kubectl describe networkpolicy <policy-name> -n <namespace>

# 查看YAML
kubectl get networkpolicy <policy-name> -n <namespace> -o yaml

# ========================================
# 测试连通性
# ========================================

# 测试Pod到Pod
kubectl exec <source-pod> -- curl http://<target-pod-ip>:8080

# 测试Pod到Service
kubectl exec <source-pod> -- curl http://<service-name>

# 测试外部访问
kubectl exec <pod> -- curl https://www.google.com

# ========================================
# Calico排查
# ========================================

# 查看策略
calicoctl get networkpolicy -n <namespace>
calicoctl get globalnetworkpolicy

# 查看策略详情
calicoctl get networkpolicy <policy-name> -n <namespace> -o yaml

# 查看Endpoint策略
calicoctl get workloadendpoint -n <namespace>

# ========================================
# Cilium排查
# ========================================

# 查看策略
kubectl get ciliumnetworkpolicy -A

# 查看Endpoint策略
kubectl exec -n kube-system <cilium-pod> -- cilium endpoint list

# 查看策略详情
kubectl exec -n kube-system <cilium-pod> -- cilium policy get

# 查看被拒绝的流量
hubble observe --verdict DROPPED

# ========================================
# 常见问题
# ========================================

# 1. Pod无法访问外部
# 检查: 是否有Egress策略限制
kubectl get networkpolicy -n <namespace> -o yaml | grep -A 5 egress

# 2. Pod间无法通信
# 检查: Ingress策略是否允许
kubectl describe networkpolicy -n <namespace>

# 3. DNS解析失败
# 确保允许DNS流量
kubectl get networkpolicy -n <namespace> -o yaml | grep -A 10 -B 5 "53"
```

---

## 9. 性能优化

```yaml
Performance_Optimization:
  策略设计:
    ✅ 最小化策略数量
    ✅ 使用标签选择器而非IP
    ✅ 合并相似策略
    ✅ 避免过度复杂的规则
  
  选择器优化:
    ✅ 使用高效的标签选择
    ✅ 避免使用ipBlock大范围
    ✅ 使用namespaceSelector
  
  CNI选择:
    高性能:
      - Calico (iptables/eBPF)
      - Cilium (eBPF)
    
    中等性能:
      - Weave
      - Kube-router
  
  监控:
    关键指标:
      - 策略数量
      - iptables规则数
      - 拒绝/允许比例
      - 策略执行延迟
```

---

## 10. 最佳实践

```yaml
Best_Practices:
  安全:
    ✅ 默认拒绝所有流量
    ✅ 显式允许必要流量
    ✅ 最小权限原则
    ✅ 定期审计策略
    ✅ 使用命名空间隔离
  
  策略设计:
    ✅ 按层次组织策略
    ✅ 使用有意义的标签
    ✅ 文档化策略目的
    ✅ 版本控制策略文件
    ✅ 测试策略变更
  
  运维:
    ✅ 监控策略执行
    ✅ 记录策略变更
    ✅ 定期review策略
    ✅ 建立变更流程
    ✅ 准备回滚方案
  
  测试:
    ✅ 先在测试环境验证
    ✅ 使用连通性测试工具
    ✅ 验证预期行为
    ✅ 测试故障场景
  
  文档:
    ✅ 记录策略意图
    ✅ 说明允许/拒绝原因
    ✅ 维护网络拓扑图
    ✅ 更新troubleshooting指南
  
  常见错误:
    ❌ 忘记DNS出站规则
    ❌ 过度限制导致服务不可用
    ❌ 没有测试就应用到生产
    ❌ 策略冲突导致意外行为
    ❌ 缺乏监控和告警
```

**策略检查清单**:

```yaml
Pre_deployment_Checklist:
  1. 策略审查:
    - [ ] 策略目的明确
    - [ ] 选择器正确
    - [ ] 端口规则完整
    - [ ] DNS规则已添加
  
  2. 测试验证:
    - [ ] 测试环境验证
    - [ ] 正常流量测试
    - [ ] 异常流量测试
    - [ ] 跨命名空间测试
  
  3. 文档准备:
    - [ ] 策略文档
    - [ ] 变更说明
    - [ ] 回滚计划
    - [ ] 影响分析
  
  4. 监控就绪:
    - [ ] 告警配置
    - [ ] Dashboard准备
    - [ ] 日志收集
    - [ ] 指标监控
  
  5. 上线准备:
    - [ ] 灰度发布计划
    - [ ] 应急联系人
    - [ ] 回滚命令
    - [ ] 验证步骤
```

---

## 相关文档

- [CNI网络概述](01_CNI网络概述.md)
- [Calico网络配置](02_Calico网络配置.md)
- [Cilium eBPF网络](03_Cilium_eBPF网络.md)
- [Kubernetes网络故障排查](../02_Kubernetes部署/05_故障排查.md#3-网络故障排查)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪
