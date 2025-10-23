# OpenAPI规范文档

本目录存放OpenAPI 3.0规范文件,用于API文档生成和测试。

## 📋 可用的OpenAPI规范

### ✅ etcd API v3

**文件**: `etcd_api_spec.yaml`

完整的etcd v3 API OpenAPI规范,包含:

- ✅ KV存储操作 (Put, Get, Delete)
- ✅ Watch监听机制
- ✅ Lease租约管理
- ✅ Cluster集群管理
- ✅ Maintenance维护操作
- ✅ 完整的Schema定义

## 🚀 使用OpenAPI规范

### 1. 生成客户端代码

```bash
# 安装openapi-generator
npm install -g @openapitools/openapi-generator-cli

# 生成Python客户端
openapi-generator generate \
  -i etcd_api_spec.yaml \
  -g python \
  -o generated/python-etcd-client

# 生成Go客户端
openapi-generator generate \
  -i etcd_api_spec.yaml \
  -g go \
  -o generated/go-etcd-client
```

### 2. 生成API文档

```bash
# 使用Redoc生成HTML文档
npm install -g redoc-cli
redoc-cli bundle etcd_api_spec.yaml -o etcd_api_docs.html

# 使用Swagger UI
docker run -p 8080:8080 \
  -e SWAGGER_JSON=/specs/etcd_api_spec.yaml \
  -v $(pwd):/specs \
  swaggerapi/swagger-ui
```

### 3. 模拟API服务器

```bash
# 使用Prism创建Mock Server
npm install -g @stoplight/prism-cli
prism mock etcd_api_spec.yaml

# 测试Mock API
curl http://127.0.0.1:4010/v3/kv/range \
  -X POST \
  -H "Content-Type: application/json"
```

## 📁 目录结构

```
openapi/
├── etcd_api_spec.yaml          # etcd v3 API规范 ✅
└── README.md                   # 本文件
```

## 🛠️ 规范开发工具

### VS Code扩展

- OpenAPI (Swagger) Editor - 语法高亮和验证
- Swagger Viewer - 实时预览
- 42Crunch OpenAPI - 安全扫描

### 在线编辑器

- [Swagger Editor](https://editor.swagger.io/)
- [Stoplight Studio](https://stoplight.io/studio)

### 验证工具

```bash
# Spectral (规范Linter)
npm install -g @stoplight/spectral-cli
spectral lint etcd_api_spec.yaml

# OpenAPI CLI Tools
npm install -g @apidevtools/swagger-cli
swagger-cli validate etcd_api_spec.yaml
```

## 📊 CI/CD集成

### GitHub Actions

```yaml
- name: 验证OpenAPI规范
  run: |
    npm install -g @stoplight/spectral-cli
    spectral lint tools/api_testing/openapi/*.yaml
```

## 📚 计划创建的规范

### 高优先级

- [ ] Docker Engine API OpenAPI Spec (v1.43)
- [ ] Kubernetes Core API OpenAPI Spec (v1.28)
- [ ] Consul API OpenAPI Spec (v1.16)

### 中优先级

- [ ] Podman API OpenAPI Spec
- [ ] containerd API OpenAPI Spec
- [ ] OpenShift API Extensions OpenAPI Spec

## 📖 参考资源

- [OpenAPI Specification](https://spec.openapis.org/oas/v3.0.3)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Swagger Tools](https://swagger.io/tools/)
- [Stoplight Platform](https://stoplight.io/)
