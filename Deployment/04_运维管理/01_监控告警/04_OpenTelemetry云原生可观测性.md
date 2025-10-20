# OpenTelemetry云原生可观测性 (2025)

> **返回**: [监控告警目录](README.md) | [运维管理首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [OpenTelemetry云原生可观测性 (2025)](#opentelemetry云原生可观测性-2025)
  - [📋 目录](#-目录)
  - [1. OpenTelemetry概述](#1-opentelemetry概述)
  - [2. 可观测性三大支柱](#2-可观测性三大支柱)
  - [3. OpenTelemetry架构](#3-opentelemetry架构)
  - [4. OpenTelemetry部署](#4-opentelemetry部署)
    - [4.1 OpenTelemetry Collector部署](#41-opentelemetry-collector部署)
    - [4.2 自动化Instrumentation](#42-自动化instrumentation)
  - [5. Traces（分布式追踪）](#5-traces分布式追踪)
  - [6. Metrics（指标）](#6-metrics指标)
  - [7. Logs（日志）](#7-logs日志)
  - [8. eBPF可观测性集成](#8-ebpf可观测性集成)
  - [9. 完整的可观测性栈](#9-完整的可观测性栈)
    - [9.1 部署Grafana统一可观测性平台](#91-部署grafana统一可观测性平台)
  - [10. 性能优化](#10-性能优化)
  - [11. 2025年最佳实践](#11-2025年最佳实践)
  - [相关文档](#相关文档)

---

## 1. OpenTelemetry概述

```yaml
OpenTelemetry_Overview:
  定义:
    - CNCF孵化项目（2019年启动）
    - 云原生可观测性标准
    - 统一的Traces、Metrics、Logs采集框架
    - 与供应商无关的可观测性API
  
  核心组件:
    OpenTelemetry_SDK:
      - 多语言支持（Java、Go、Python、Node.js等）
      - 统一的API和语义约定
      - 可扩展的导出器（Exporter）
    
    OpenTelemetry_Collector:
      - 独立的代理和网关
      - 接收、处理、导出遥测数据
      - 支持多种协议（OTLP、Jaeger、Zipkin、Prometheus）
      - 高性能、可扩展
    
    OpenTelemetry_Protocol_OTLP:
      - gRPC和HTTP/JSON传输
      - 原生支持Traces、Metrics、Logs
      - 高效的二进制协议
  
  2025年状态:
    版本: v1.20+
    成熟度:
      - Traces: ✅ GA (General Availability)
      - Metrics: ✅ GA
      - Logs: ✅ Stable
    
    采用率:
      - 主流云厂商全面支持
      - Kubernetes原生集成
      - 已成为可观测性事实标准
  
  优势:
    统一标准:
      - 单一SDK支持三大支柱
      - 减少工具碎片化
      - 简化可观测性实施
    
    供应商中立:
      - 避免供应商锁定
      - 灵活切换后端
      - 开放生态系统
    
    自动化:
      - 自动Instrumentation
      - 零代码侵入
      - 降低实施成本
    
    高性能:
      - 批量处理
      - 采样策略
      - 资源优化
```

---

## 2. 可观测性三大支柱

```yaml
Three_Pillars_of_Observability:
  Traces_分布式追踪:
    定义:
      - 请求在分布式系统中的完整路径
      - Span表示单个操作
      - Trace是Span的有向无环图（DAG）
    
    用途:
      - 定位性能瓶颈
      - 理解服务依赖
      - 故障根因分析
      - 优化关键路径
    
    关键概念:
      TraceID: 唯一标识一次请求
      SpanID: 唯一标识一个操作
      ParentSpanID: 建立Span之间的关系
      Attributes: Span的元数据（key-value）
      Events: Span中的时间点事件
      Links: 连接不同Trace的关系
    
    采样策略:
      - Head-based采样（在Trace开始时决定）
      - Tail-based采样（在Trace完成后决定）
      - 概率采样
      - 速率限制采样
      - 基于规则的采样
  
  Metrics_指标:
    定义:
      - 系统在特定时间点的数值测量
      - 时间序列数据
      - 聚合统计信息
    
    用途:
      - 实时监控系统健康
      - 容量规划
      - SLI/SLO跟踪
      - 告警触发
    
    指标类型:
      Counter: 累加计数器（如请求总数）
      Gauge: 瞬时值（如CPU使用率）
      Histogram: 分布统计（如响应时间分布）
      Summary: 分位数统计
    
    维度:
      - 多维标签（Labels）
      - 灵活的查询和聚合
      - 高基数问题注意
  
  Logs_日志:
    定义:
      - 系统事件的时间序列记录
      - 结构化或非结构化数据
      - 详细的上下文信息
    
    用途:
      - 故障排查
      - 审计追踪
      - 安全分析
      - 调试细节
    
    结构化日志:
      - JSON格式
      - 统一字段（timestamp、level、message）
      - Trace上下文关联（TraceID、SpanID）
      - 高效索引和查询
  
  三者关系:
    关联:
      - Trace提供请求级视图
      - Metrics提供聚合视图
      - Logs提供详细上下文
    
    互补:
      - Metrics发现异常 → Traces定位问题 → Logs查看细节
      - TraceID连接三者
      - 统一查询和展示
```

---

## 3. OpenTelemetry架构

```yaml
OpenTelemetry_Architecture:
  数据流:
    应用程序:
      - OpenTelemetry SDK埋点
      - 自动或手动Instrumentation
      - 生成Traces、Metrics、Logs
      
      ↓
    
    OpenTelemetry_Collector:
      Receiver:
        - 接收遥测数据
        - 支持多种协议（OTLP、Jaeger、Zipkin、Prometheus）
        - gRPC/HTTP端点
      
      Processor:
        - 数据处理和转换
        - 采样、过滤、丰富
        - 批处理、重试
      
      Exporter:
        - 导出到后端存储
        - Jaeger、Tempo、Prometheus、Loki
        - 多后端并行导出
      
      ↓
    
    后端存储:
      Traces: Jaeger, Tempo, Zipkin
      Metrics: Prometheus, Cortex, Thanos
      Logs: Loki, Elasticsearch
      
      ↓
    
    可视化:
      - Grafana统一展示
      - 关联查询
      - 仪表盘和告警
  
  部署模式:
    Agent模式:
      - 每个节点部署Collector
      - 低延迟
      - 本地缓存
      - 适合边缘采集
    
    Gateway模式:
      - 集中式Collector集群
      - 负载均衡
      - 统一处理和采样
      - 适合大规模部署
    
    混合模式:
      - Agent采集 → Gateway处理
      - 灵活的架构
      - 生产推荐
```

---

## 4. OpenTelemetry部署

### 4.1 OpenTelemetry Collector部署

```yaml
# OpenTelemetry Collector配置（Kubernetes）
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: observability
data:
  otel-collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
      
      # Prometheus metrics scraping
      prometheus:
        config:
          scrape_configs:
          - job_name: 'kubernetes-pods'
            kubernetes_sd_configs:
            - role: pod
    
    processors:
      # 批处理提高性能
      batch:
        timeout: 10s
        send_batch_size: 1024
      
      # 内存限制
      memory_limiter:
        check_interval: 1s
        limit_mib: 512
        spike_limit_mib: 128
      
      # 添加资源属性
      resource:
        attributes:
        - key: environment
          value: production
          action: insert
      
      # Tail-based采样
      tail_sampling:
        policies:
        - name: error-traces
          type: status_code
          status_code:
            status_codes: [ERROR]
        - name: slow-traces
          type: latency
          latency:
            threshold_ms: 1000
        - name: probabilistic
          type: probabilistic
          probabilistic:
            sampling_percentage: 10
    
    exporters:
      # 导出Traces到Tempo
      otlp/tempo:
        endpoint: tempo:4317
        tls:
          insecure: true
      
      # 导出Metrics到Prometheus
      prometheusremotewrite:
        endpoint: http://prometheus:9090/api/v1/write
      
      # 导出Logs到Loki
      loki:
        endpoint: http://loki:3100/loki/api/v1/push
        labels:
          attributes:
            service.name: "service_name"
            log.level: "level"
      
      # Debug导出（开发环境）
      logging:
        loglevel: debug
    
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch, tail_sampling]
          exporters: [otlp/tempo, logging]
        
        metrics:
          receivers: [otlp, prometheus]
          processors: [memory_limiter, batch]
          exporters: [prometheusremotewrite]
        
        logs:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [loki, logging]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
  namespace: observability
spec:
  replicas: 3
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
      - name: otel-collector
        image: otel/opentelemetry-collector-contrib:0.91.0
        args:
        - --config=/conf/otel-collector-config.yaml
        ports:
        - containerPort: 4317  # OTLP gRPC
          name: otlp-grpc
        - containerPort: 4318  # OTLP HTTP
          name: otlp-http
        - containerPort: 8888  # Metrics
          name: metrics
        volumeMounts:
        - name: config
          mountPath: /conf
        resources:
          limits:
            cpu: 1000m
            memory: 2Gi
          requests:
            cpu: 200m
            memory: 512Mi
      volumes:
      - name: config
        configMap:
          name: otel-collector-config
---
apiVersion: v1
kind: Service
metadata:
  name: otel-collector
  namespace: observability
spec:
  selector:
    app: otel-collector
  ports:
  - name: otlp-grpc
    port: 4317
    targetPort: 4317
  - name: otlp-http
    port: 4318
    targetPort: 4318
  - name: metrics
    port: 8888
    targetPort: 8888
```

### 4.2 自动化Instrumentation

```yaml
# OpenTelemetry Operator安装
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml

# 等待Operator就绪
kubectl wait --for=condition=available --timeout=300s deployment/opentelemetry-operator-controller-manager -n opentelemetry-operator-system

---
# 自动Instrumentation配置
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: auto-instrumentation
  namespace: default
spec:
  exporter:
    endpoint: http://otel-collector.observability:4317
  
  propagators:
    - tracecontext
    - baggage
    - b3
  
  sampler:
    type: parentbased_traceidratio
    argument: "0.1"  # 10%采样率
  
  # Java自动Instrumentation
  java:
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-java:latest
    env:
    - name: OTEL_JAVAAGENT_LOGGING
      value: "application"
  
  # Node.js自动Instrumentation
  nodejs:
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-nodejs:latest
  
  # Python自动Instrumentation
  python:
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-python:latest
  
  # .NET自动Instrumentation
  dotnet:
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-dotnet:latest
---
# 应用部署启用自动Instrumentation
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
      annotations:
        # 启用自动Instrumentation
        instrumentation.opentelemetry.io/inject-java: "true"
        # 或其他语言
        # instrumentation.opentelemetry.io/inject-python: "true"
        # instrumentation.opentelemetry.io/inject-nodejs: "true"
    spec:
      containers:
      - name: my-app
        image: my-app:latest
        ports:
        - containerPort: 8080
        env:
        - name: OTEL_SERVICE_NAME
          value: "my-app"
        - name: OTEL_RESOURCE_ATTRIBUTES
          value: "service.version=1.0.0,deployment.environment=production"
```

---

## 5. Traces（分布式追踪）

```yaml
Distributed_Tracing_Implementation:
  手动Instrumentation示例_Go:
    go
    package main
    
    import (
        "context"
        "log"
        
        "go.opentelemetry.io/otel"
        "go.opentelemetry.io/otel/attribute"
        "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
        "go.opentelemetry.io/otel/sdk/resource"
        sdktrace "go.opentelemetry.io/otel/sdk/trace"
        semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
    )
    
    func initTracer() (*sdktrace.TracerProvider, error) {
        // 创建OTLP Trace导出器
        exporter, err := otlptracegrpc.New(
            context.Background(),
            otlptracegrpc.WithEndpoint("otel-collector:4317"),
            otlptracegrpc.WithInsecure(),
        )
        if err != nil {
            return nil, err
        }
        
        // 创建Resource
        res, err := resource.New(
            context.Background(),
            resource.WithAttributes(
                semconv.ServiceName("my-service"),
                semconv.ServiceVersion("1.0.0"),
                attribute.String("environment", "production"),
            ),
        )
        if err != nil {
            return nil, err
        }
        
        // 创建TracerProvider
        tp := sdktrace.NewTracerProvider(
            sdktrace.WithBatcher(exporter),
            sdktrace.WithResource(res),
            sdktrace.WithSampler(sdktrace.ParentBased(
                sdktrace.TraceIDRatioBased(0.1), // 10%采样
            )),
        )
        
        otel.SetTracerProvider(tp)
        return tp, nil
    }
    
    func businessLogic(ctx context.Context) error {
        tracer := otel.Tracer("my-service")
        
        // 创建Span
        ctx, span := tracer.Start(ctx, "businessLogic")
        defer span.End()
        
        // 添加属性
        span.SetAttributes(
            attribute.String("user.id", "12345"),
            attribute.Int("request.size", 1024),
        )
        
        // 添加事件
        span.AddEvent("Processing started")
        
        // 调用子操作
        if err := databaseQuery(ctx); err != nil {
            span.RecordError(err)
            return err
        }
        
        span.AddEvent("Processing completed")
        return nil
    }
    
    func databaseQuery(ctx context.Context) error {
        tracer := otel.Tracer("my-service")
        
        ctx, span := tracer.Start(ctx, "databaseQuery")
        defer span.End()
        
        span.SetAttributes(
            attribute.String("db.system", "postgresql"),
            attribute.String("db.statement", "SELECT * FROM users"),
        )
        
        // 模拟数据库查询
        // ...
        
        return nil
    }
  
  Context传播:
    HTTP传播:
      go
      import (
          "net/http"
          "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
      )
      
      // HTTP客户端自动传播
      client := http.Client{
          Transport: otelhttp.NewTransport(http.DefaultTransport),
      }
      
      // HTTP服务端自动提取
      handler := otelhttp.NewHandler(
          http.HandlerFunc(myHandler),
          "my-handler",
      )
    
    gRPC传播:
      go
      import (
          "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
          "google.golang.org/grpc"
      )
      
      // gRPC客户端
      conn, err := grpc.Dial(
          "localhost:50051",
          grpc.WithUnaryInterceptor(otelgrpc.UnaryClientInterceptor()),
          grpc.WithStreamInterceptor(otelgrpc.StreamClientInterceptor()),
      )
      
      // gRPC服务端
      server := grpc.NewServer(
          grpc.UnaryInterceptor(otelgrpc.UnaryServerInterceptor()),
          grpc.StreamInterceptor(otelgrpc.StreamServerInterceptor()),
      )
```

---

## 6. Metrics（指标）

```yaml
Metrics_Implementation:
  手动Instrumentation示例_Go:
    go
    package main
    
    import (
        "context"
        "time"
        
        "go.opentelemetry.io/otel"
        "go.opentelemetry.io/otel/attribute"
        "go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
        "go.opentelemetry.io/otel/metric"
        sdkmetric "go.opentelemetry.io/otel/sdk/metric"
    )
    
    func initMeter() (*sdkmetric.MeterProvider, error) {
        exporter, err := otlpmetricgrpc.New(
            context.Background(),
            otlpmetricgrpc.WithEndpoint("otel-collector:4317"),
            otlpmetricgrpc.WithInsecure(),
        )
        if err != nil {
            return nil, err
        }
        
        mp := sdkmetric.NewMeterProvider(
            sdkmetric.WithReader(
                sdkmetric.NewPeriodicReader(exporter,
                    sdkmetric.WithInterval(10*time.Second),
                ),
            ),
        )
        
        otel.SetMeterProvider(mp)
        return mp, nil
    }
    
    func setupMetrics() error {
        meter := otel.Meter("my-service")
        
        // Counter - 请求总数
        requestCounter, err := meter.Int64Counter(
            "http.server.requests",
            metric.WithDescription("Total HTTP requests"),
            metric.WithUnit("{request}"),
        )
        if err != nil {
            return err
        }
        
        // Histogram - 请求延迟
        requestDuration, err := meter.Float64Histogram(
            "http.server.duration",
            metric.WithDescription("HTTP request duration"),
            metric.WithUnit("ms"),
        )
        if err != nil {
            return err
        }
        
        // Gauge - 活跃连接数
        activeConnections, err := meter.Int64ObservableGauge(
            "http.server.active_connections",
            metric.WithDescription("Active HTTP connections"),
        )
        if err != nil {
            return err
        }
        
        // 注册回调
        _, err = meter.RegisterCallback(
            func(_ context.Context, o metric.Observer) error {
                o.ObserveInt64(activeConnections, getActiveConnections())
                return nil
            },
            activeConnections,
        )
        
        return err
    }
    
    func handleRequest(ctx context.Context) {
        start := time.Now()
        
        // 增加计数器
        requestCounter.Add(ctx, 1,
            metric.WithAttributes(
                attribute.String("http.method", "GET"),
                attribute.String("http.route", "/api/users"),
                attribute.Int("http.status_code", 200),
            ),
        )
        
        // 处理请求...
        
        // 记录延迟
        duration := float64(time.Since(start).Milliseconds())
        requestDuration.Record(ctx, duration,
            metric.WithAttributes(
                attribute.String("http.method", "GET"),
                attribute.String("http.route", "/api/users"),
            ),
        )
    }
```

---

## 7. Logs（日志）

```yaml
Logs_Integration:
  结构化日志_JSON:
    go
    package main
    
    import (
        "context"
        "log/slog"
        
        "go.opentelemetry.io/otel/trace"
    )
    
    func setupLogging() {
        handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
            Level: slog.LevelInfo,
        })
        logger := slog.New(handler)
        slog.SetDefault(logger)
    }
    
    func logWithTrace(ctx context.Context, message string) {
        span := trace.SpanFromContext(ctx)
        spanContext := span.SpanContext()
        
        slog.InfoContext(ctx, message,
            slog.String("trace_id", spanContext.TraceID().String()),
            slog.String("span_id", spanContext.SpanID().String()),
            slog.Bool("trace_sampled", spanContext.IsSampled()),
        )
    }
  
  OpenTelemetry_Logs_API:
    go
    import (
        "go.opentelemetry.io/otel/sdk/log"
        "go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploggrpc"
    )
    
    func initLogger() (*log.LoggerProvider, error) {
        exporter, err := otlploggrpc.New(
            context.Background(),
            otlploggrpc.WithEndpoint("otel-collector:4317"),
            otlploggrpc.WithInsecure(),
        )
        if err != nil {
            return nil, err
        }
        
        lp := log.NewLoggerProvider(
            log.WithProcessor(log.NewBatchProcessor(exporter)),
        )
        
        return lp, nil
    }
```

---

## 8. eBPF可观测性集成

```yaml
eBPF_Observability:
  简介:
    - 基于Linux eBPF的零侵入可观测性
    - 内核级数据采集
    - 超低性能开销（<1%）
    - 无需修改应用代码
  
  eBPF可观测性工具:
    Pixie:
      功能:
        - 自动发现和追踪应用
        - 零配置可观测性
        - 实时协议追踪（HTTP、gRPC、MySQL、Redis等）
        - Kubernetes原生
      
      部署:
        bash
        # 安装Pixie CLI
        bash -c "$(curl -fsSL https://withpixie.ai/install.sh)"
        
        # 在Kubernetes中部署
        px deploy
        
        # 查看实时数据
        px live http_data
      
      与OpenTelemetry集成:
        - Pixie作为数据源
        - 导出到OpenTelemetry Collector
        - 统一的可观测性视图
    
    Cilium_Hubble:
      功能:
        - eBPF网络可观测性
        - L3-L7网络流量可视化
        - 服务依赖图谱
        - NetworkPolicy验证
      
      部署:
        bash
        # 启用Hubble
        cilium hubble enable --ui
        
        # 查看流量
        cilium hubble observe --follow
        
        # 服务地图
        cilium hubble ui
      
      OpenTelemetry导出:
        yaml
        # Hubble导出到OpenTelemetry
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: hubble-otel-config
        data:
          config.yaml: |
            exporters:
              otlp:
                endpoint: otel-collector:4317
    
    Tetragon:
      功能:
        - 基于eBPF的安全可观测性
        - 进程执行跟踪
        - 网络活动监控
        - 文件访问审计
        - 系统调用过滤
      
      部署:
        bash
        # 安装Tetragon
        helm install tetragon cilium/tetragon -n kube-system
        
        # 查看安全事件
        kubectl logs -n kube-system -l app.kubernetes.io/name=tetragon -c export-stdout -f
      
      TracingPolicy示例:
        yaml
        apiVersion: cilium.io/v1alpha1
        kind: TracingPolicy
        metadata:
          name: monitor-file-access
        spec:
          kprobes:
          - call: "security_file_open"
            return: true
            syscall: false
            args:
            - index: 0
              type: "file"
            returnArg:
              type: "int"
  
  eBPF+OpenTelemetry完整方案:
    架构:
      text
      应用层
        ├─ OpenTelemetry SDK（业务指标）
        ↓
      
      eBPF层
        ├─ Pixie（自动追踪）
        ├─ Cilium/Hubble（网络流量）
        ├─ Tetragon（安全审计）
        ↓
      
      OpenTelemetry Collector
        ├─ 统一接收和处理
        ├─ 关联和丰富数据
        ↓
      
      后端存储
        ├─ Traces: Tempo/Jaeger
        ├─ Metrics: Prometheus
        ├─ Logs: Loki
        ↓
      
      Grafana统一展示
    
    优势:
      - 应用层+内核层完整视图
      - 零侵入+主动埋点结合
      - 网络+安全+性能统一监控
      - 极低性能开销
```

---

## 9. 完整的可观测性栈

### 9.1 部署Grafana统一可观测性平台

```bash
#!/bin/bash
# ========================================
# 完整的OpenTelemetry+eBPF可观测性栈部署
# ========================================

echo "===== 1. 创建Namespace ====="
kubectl create namespace observability

echo "===== 2. 部署Tempo（Traces后端） ====="
helm repo add grafana https://grafana.github.io/helm-charts
helm install tempo grafana/tempo -n observability \
  --set tempo.receivers.otlp.protocols.grpc.endpoint=0.0.0.0:4317

echo "===== 3. 部署Loki（Logs后端） ====="
helm install loki grafana/loki-stack -n observability \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=10Gi \
  --set promtail.enabled=true

echo "===== 4. 部署Prometheus（Metrics后端） ====="
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n observability \
  --set prometheus.prometheusSpec.remoteWrite[0].url=http://prometheus:9090/api/v1/write

echo "===== 5. 部署OpenTelemetry Collector ====="
# 使用前面的配置
kubectl apply -f otel-collector-config.yaml -n observability

echo "===== 6. 部署OpenTelemetry Operator ====="
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
kubectl wait --for=condition=available --timeout=300s deployment/opentelemetry-operator-controller-manager -n opentelemetry-operator-system

echo "===== 7. 部署Grafana ====="
helm install grafana grafana/grafana -n observability \
  --set adminPassword=admin \
  --set persistence.enabled=true \
  --set persistence.size=10Gi

# 配置Grafana数据源
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: observability
data:
  datasources.yaml: |
    apiVersion: 1
    datasources:
    # Prometheus for Metrics
    - name: Prometheus
      type: prometheus
      access: proxy
      url: http://prometheus-kube-prometheus-prometheus:9090
      isDefault: true
    
    # Tempo for Traces
    - name: Tempo
      type: tempo
      access: proxy
      url: http://tempo:3100
      jsonData:
        tracesToLogsV2:
          datasourceUid: loki
        serviceMap:
          datasourceUid: prometheus
    
    # Loki for Logs
    - name: Loki
      type: loki
      access: proxy
      url: http://loki:3100
      jsonData:
        derivedFields:
        - datasourceUid: tempo
          matcherRegex: "trace_id=(\\w+)"
          name: TraceID
          url: "\${__value.raw}"
EOF

echo "===== 8. 部署Pixie（eBPF可观测性） ====="
bash -c "$(curl -fsSL https://withpixie.ai/install.sh)"
px deploy

echo "===== 9. 部署Cilium+Hubble（网络可观测性） ====="
cilium install --version 1.14.5 \
  --set hubble.enabled=true \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true
cilium hubble enable --ui

echo "===== 10. 部署Tetragon（安全可观测性） ====="
helm install tetragon cilium/tetragon -n kube-system \
  --set tetragon.enabled=true

echo "===== 11. 获取访问信息 ====="
GRAFANA_PASSWORD=$(kubectl get secret --namespace observability grafana -o jsonpath="{.data.admin-password}" | base64 --decode)

echo "✅ 可观测性栈部署完成！"
echo ""
echo "访问信息:"
echo "- Grafana: kubectl port-forward -n observability svc/grafana 3000:80"
echo "  用户名: admin"
echo "  密码: $GRAFANA_PASSWORD"
echo ""
echo "- Hubble UI: kubectl port-forward -n kube-system svc/hubble-ui 12000:80"
echo "- Pixie: px live"
```

---

## 10. 性能优化

```yaml
Performance_Optimization:
  采样策略:
    Head_based采样:
      - 在Trace开始时决定
      - 简单高效
      - 适合大多数场景
      
      配置:
        ParentBased: 跟随父Span决策
        TraceIDRatioBased: 基于TraceID哈希
        AlwaysOn/AlwaysOff: 总是/从不采样
    
    Tail_based采样:
      - 在Trace完成后决定
      - 保留重要Trace（错误、慢请求）
      - 需要Collector支持
      
      配置:
        yaml
        processors:
          tail_sampling:
            policies:
            - name: errors
              type: status_code
              status_code:
                status_codes: [ERROR]
            - name: slow
              type: latency
              latency:
                threshold_ms: 1000
            - name: sample
              type: probabilistic
              probabilistic:
                sampling_percentage: 10
  
  批处理:
    配置:
      yaml
      processors:
        batch:
          timeout: 10s
          send_batch_size: 1024
          send_batch_max_size: 2048
    
    效果:
      - 减少网络请求
      - 提高吞吐量
      - 降低CPU使用
  
  内存管理:
    配置:
      yaml
      processors:
        memory_limiter:
          check_interval: 1s
          limit_mib: 512
          spike_limit_mib: 128
    
    效果:
      - 防止OOM
      - 稳定的内存使用
      - 自动back-pressure
  
  高基数问题:
    问题:
      - 过多的唯一标签值
      - 内存和存储膨胀
      - 查询性能下降
    
    解决:
      - 限制标签基数
      - 使用Resource而非Attributes
      - 聚合高基数标签
      - 采样或过滤
```

---

## 11. 2025年最佳实践

```yaml
Best_Practices_2025:
  架构设计:
    ✅ 使用OpenTelemetry统一标准
    ✅ 采用混合部署模式（Agent+Gateway）
    ✅ 启用Tail-based采样
    ✅ 配置适当的批处理和内存限制
    ✅ 多后端并行导出（容错）
  
  Instrumentation:
    ✅ 优先使用自动Instrumentation
    ✅ 关键路径手动添加Span
    ✅ 使用语义约定（Semantic Conventions）
    ✅ 关联Traces、Metrics、Logs（TraceID）
    ✅ 添加业务上下文（用户ID、租户ID等）
  
  eBPF集成:
    ✅ 部署Pixie零侵入追踪
    ✅ 启用Cilium Hubble网络可观测性
    ✅ 使用Tetragon安全监控
    ✅ 结合应用层和内核层视图
    ✅ 导出eBPF数据到OpenTelemetry
  
  数据关联:
    ✅ 统一TraceID格式（W3C Trace Context）
    ✅ 日志中注入TraceID和SpanID
    ✅ Grafana配置数据源关联
    ✅ 使用Exemplars连接Metrics和Traces
    ✅ 服务地图自动生成
  
  性能与成本:
    ✅ 生产环境采样率10-20%
    ✅ 保留所有错误Trace
    ✅ 慢请求100%采样
    ✅ 配置数据保留策略（Traces: 7天, Metrics: 30天, Logs: 14天）
    ✅ 使用压缩和高效存储
  
  安全性:
    ✅ 敏感数据脱敏
    ✅ TLS加密传输
    ✅ RBAC权限控制
    ✅ 审计日志
    ✅ 遵守数据合规要求
  
  告警与SLO:
    ✅ 基于SLI设置告警（错误率、延迟）
    ✅ 多级告警（Warning、Critical）
    ✅ 告警聚合和降噪
    ✅ 自动创建Incident
    ✅ 告警与Trace关联
```

---

## 相关文档

- [Prometheus监控体系](01_Prometheus监控体系.md)
- [Grafana可视化](02_Grafana可视化.md)
- [告警管理](03_告警管理.md)
- [Loki日志聚合](../02_日志管理/02_Loki日志聚合.md)
- [Cilium eBPF网络](../../02_容器化部署/03_容器网络/03_Cilium_eBPF网络.md)
- [Kubernetes集群部署](../../02_容器化部署/02_Kubernetes部署/01_集群部署.md)

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 生产就绪 - 2025云原生可观测性标准
