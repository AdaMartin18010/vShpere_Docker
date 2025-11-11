# 04 - 边缘Serverless

**作者**: 云原生专家团队
**创建日期**: 2025-10-19
**最后更新**: 2025-10-19
**版本**: v1.0

---

## 📋 本章导航

- [04 - 边缘Serverless](#04---边缘serverless)
  - [📋 本章导航](#-本章导航)
  - [1. 边缘Serverless概述](#1-边缘serverless概述)
    - [1.1 什么是边缘Serverless](#11-什么是边缘serverless)
    - [1.2 核心优势](#12-核心优势)
    - [1.3 应用场景](#13-应用场景)
    - [1.4 技术对比](#14-技术对比)
  - [2. Cloudflare Workers详解](#2-cloudflare-workers详解)
    - [2.1 架构原理](#21-架构原理)
    - [2.2 快速开始](#22-快速开始)
    - [2.3 Workers KV存储](#23-workers-kv存储)
    - [2.4 Durable Objects](#24-durable-objects)
    - [2.5 生产实践](#25-生产实践)
  - [3. AWS Lambda@Edge](#3-aws-lambdaedge)
    - [3.1 架构与触发点](#31-架构与触发点)
    - [3.2 部署Lambda@Edge](#32-部署lambdaedge)
    - [3.3 实战案例](#33-实战案例)
    - [3.4 最佳实践](#34-最佳实践)
  - [4. Fastly Compute@Edge](#4-fastly-computeedge)
    - [4.1 WebAssembly优势](#41-webassembly优势)
    - [4.2 Rust开发](#42-rust开发)
    - [4.3 JavaScript开发](#43-javascript开发)
    - [4.4 边缘存储](#44-边缘存储)
  - [5. WebAssembly在边缘](#5-webassembly在边缘)
    - [5.1 WASI标准](#51-wasi标准)
    - [5.2 性能优势](#52-性能优势)
    - [5.3 多语言支持](#53-多语言支持)
    - [5.4 边缘运行时](#54-边缘运行时)
  - [6. 边缘Serverless最佳实践](#6-边缘serverless最佳实践)
    - [6.1 性能优化](#61-性能优化)
    - [6.2 安全考虑](#62-安全考虑)
    - [6.3 成本优化](#63-成本优化)
    - [6.4 监控与调试](#64-监控与调试)
  - [7. 总结](#7-总结)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 1. 边缘Serverless概述

### 1.1 什么是边缘Serverless

**边缘Serverless** 将Serverless计算推向网络边缘，在靠近用户的位置执行代码。

```yaml
边缘Serverless定义:
  在全球分布式边缘节点上运行的Serverless函数

核心特点:
  - 超低延迟 (< 50ms)
  - 全球分布
  - 自动扩缩容
  - 按需付费
  - 无需管理服务器

vs 传统Serverless:
  传统:
    - 区域性数据中心
    - 延迟: 100-500ms
    - 冷启动: 100ms-数秒

  边缘:
    - 全球200+边缘节点
    - 延迟: < 50ms
    - 冷启动: 0-5ms (V8 Isolates)

边缘Serverless平台:
  ✅ Cloudflare Workers (V8 Isolates)
  ✅ AWS Lambda@Edge (CloudFront)
  ✅ Fastly Compute@Edge (WebAssembly)
  ✅ Akamai EdgeWorkers
  ✅ Vercel Edge Functions
  ✅ Netlify Edge Functions
  ✅ Deno Deploy
```

---

### 1.2 核心优势

```yaml
1. 超低延迟:
   - 物理距离近
   - 减少网络往返
   - 改善用户体验

   示例:
     美国用户访问亚洲服务器: 200-300ms
     美国用户访问本地边缘: 10-30ms
     延迟降低: 90%

2. 高可用性:
   - 全球分布
   - 自动故障转移
   - 无单点故障

   可用性: 99.99%+

3. 零冷启动:
   - V8 Isolates技术
   - 启动时间 < 5ms
   - 对比Lambda冷启动: 100ms-3s

4. 全球扩展:
   - 自动在全球节点部署
   - 无需区域配置
   - 流量智能路由

5. 成本优化:
   - 按实际使用付费
   - 免费额度
   - 降低带宽成本

6. 安全性:
   - DDoS防护
   - 边缘加密
   - 沙箱隔离

7. 简化架构:
   - 无需CDN配置
   - 内置缓存
   - 简化运维
```

---

### 1.3 应用场景

```yaml
典型应用场景:

1. API加速:
   - RESTful API
   - GraphQL Gateway
   - 数据聚合
   - 响应转换

2. 内容个性化:
   - A/B测试
   - 地理位置定制
   - 用户特定内容
   - 动态HTML生成

3. 认证授权:
   - JWT验证
   - OAuth代理
   - 权限检查
   - 速率限制

4. 图片优化:
   - 实时压缩
   - 格式转换 (WebP)
   - 尺寸调整
   - 智能裁剪

5. 边缘缓存:
   - 智能缓存
   - 缓存预热
   - 缓存清除
   - 动态TTL

6. 请求路由:
   - 智能路由
   - 灰度发布
   - 流量切换
   - 故障转移

7. 边缘渲染:
   - SSR (Server-Side Rendering)
   - 动态页面
   - SEO优化

8. 安全防护:
   - Bot检测
   - 验证码
   - IP黑名单
   - 请求过滤

9. 实时数据处理:
   - 日志聚合
   - 指标收集
   - 事件流处理

10. IoT数据收集:
    - 设备数据接收
    - 数据预处理
    - 实时分析
```

---

### 1.4 技术对比

```yaml
主流边缘Serverless平台对比:

平台              冷启动    语言支持         定价模式          全球节点
───────────────────────────────────────────────────────────────
Cloudflare       0ms       JS/WASM/Rust     免费10万请求/天    275+
Workers          (V8)      Python(Beta)     $5/月起

AWS              ~100ms    Node.js          $0.60/百万         410+
Lambda@Edge                Python           请求

Fastly           <5ms      Rust/JS          $0.035/百万        70+
Compute@Edge     (WASM)    Go/Python        请求

Vercel Edge      0ms       JS/TS            免费10万请求/月    70+
Functions        (V8)                       $20/月起

Deno Deploy      0ms       JS/TS            免费10万请求/月    35+
                 (V8)                       $20/月起

特性对比:

Cloudflare Workers:
  优势:
    ✅ 最低延迟 (0ms冷启动)
    ✅ 最多边缘节点 (275+)
    ✅ KV/Durable Objects
    ✅ 慷慨免费额度

  劣势:
    ❌ 语言支持较少
    ❌ CPU限制 (10-50ms)
    ❌ 内存限制 (128MB)

AWS Lambda@Edge:
  优势:
    ✅ AWS生态集成
    ✅ 更多资源 (128MB-10GB)
    ✅ 长执行时间 (30s)

  劣势:
    ❌ 冷启动较慢
    ❌ 部署较慢 (5-15分钟)
    ❌ 更高成本

Fastly Compute@Edge:
  优势:
    ✅ WebAssembly (安全/快速)
    ✅ 多语言编译
    ✅ 零冷启动

  劣势:
    ❌ 节点较少
    ❌ 学习曲线高
    ❌ 生态较小

选择建议:
  Cloudflare Workers:
    ✅ 简单API
    ✅ 低延迟要求
    ✅ 全球覆盖
    ✅ 预算有限

  Lambda@Edge:
    ✅ AWS重度用户
    ✅ 复杂逻辑
    ✅ 长执行时间

  Fastly Compute@Edge:
    ✅ 性能极致追求
    ✅ Rust开发者
    ✅ 安全要求高
```

---

## 2. Cloudflare Workers详解

### 2.1 架构原理

**V8 Isolates架构**:

```yaml
V8 Isolates vs Containers:

传统容器 (Lambda):
  进程隔离 → 启动慢 (100ms+)
  资源开销大

V8 Isolates (Workers):
  V8引擎内隔离 → 启动极快 (0ms)
  资源开销小
  安全性高

架构层次:
  ┌─────────────────────────────────────┐
  │         全球275+数据中心             │
  ├─────────────────────────────────────┤
  │         Cloudflare网络              │
  ├─────────────────────────────────────┤
  │         Workers运行时               │
  │  ┌───────────────────────────────┐  │
  │  │   V8 JavaScript引擎          │  │
  │  │  ┌─────┐ ┌─────┐ ┌─────┐    │  │
  │  │  │Iso 1│ │Iso 2│ │Iso N│    │  │
  │  │  └─────┘ └─────┘ └─────┘    │  │
  │  └───────────────────────────────┘  │
  └─────────────────────────────────────┘

执行流程:
  1. 用户请求到达最近边缘节点
  2. Workers代码在V8 Isolate中执行
  3. 访问KV/Durable Objects (可选)
  4. 返回响应给用户

性能特性:
  - 冷启动: 0ms
  - 执行时间: 10-50ms (CPU时间)
  - 内存: 128MB
  - 脚本大小: 1MB (压缩后)
  - 并发: 无限制
```

---

### 2.2 快速开始

**示例1: Hello World**:

```bash
# 1. 安装Wrangler CLI
npm install -g wrangler

# 2. 登录Cloudflare
wrangler login

# 3. 创建新Worker
wrangler init my-worker

# 选择: "Fetch handler"
```

```javascript
// src/index.js
export default {
  async fetch(request, env, ctx) {
    return new Response('Hello World!', {
      headers: { 'Content-Type': 'text/plain' }
    })
  }
}
```

```bash
# 4. 本地开发
wrangler dev

# 输出:
# ⛅️ wrangler 3.0.0
# ------------------
# Your worker is listening on http://localhost:8787

# 5. 部署到Cloudflare
wrangler publish

# 输出:
# Total Upload: xxx KiB / gzip: xxx KiB
# Uploaded my-worker (x.xx sec)
# Published my-worker (x.xx sec)
#   https://my-worker.username.workers.dev
```

---

**示例2: REST API**:

```javascript
// src/index.js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url)

    // 路由处理
    if (url.pathname === '/api/hello') {
      return handleHello(request)
    }

    if (url.pathname === '/api/user') {
      return handleUser(request)
    }

    return new Response('Not Found', { status: 404 })
  }
}

async function handleHello(request) {
  const data = {
    message: 'Hello from Cloudflare Workers!',
    timestamp: new Date().toISOString(),
    cf: request.cf  // Cloudflare提供的请求信息
  }

  return new Response(JSON.stringify(data, null, 2), {
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }
  })
}

async function handleUser(request) {
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 })
  }

  try {
    const body = await request.json()
    const { name, age } = body

    // 业务逻辑
    const response = {
      success: true,
      user: { name, age, id: crypto.randomUUID() },
      location: request.cf.city  // 用户所在城市
    }

    return new Response(JSON.stringify(response), {
      headers: { 'Content-Type': 'application/json' }
    })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}
```

```bash
# 测试
curl https://my-worker.username.workers.dev/api/hello

# 输出:
# {
#   "message": "Hello from Cloudflare Workers!",
#   "timestamp": "2025-10-19T12:00:00.000Z",
#   "cf": {
#     "city": "San Francisco",
#     "country": "US",
#     "latitude": "37.77490",
#     "longitude": "-122.41940"
#   }
# }
```

---

### 2.3 Workers KV存储

**Workers KV**: 全球分布式键值存储，超低延迟读取。

```bash
# 1. 创建KV命名空间
wrangler kv:namespace create "MY_KV"

# 输出:
# 🌀 Creating namespace with title "my-worker-MY_KV"
# ✨ Success!
# Add the following to your configuration file:
# kv_namespaces = [
#   { binding = "MY_KV", id = "abc123..." }
# ]
```

```toml
# wrangler.toml
name = "my-worker"
main = "src/index.js"
compatibility_date = "2025-10-19"

kv_namespaces = [
  { binding = "MY_KV", id = "abc123..." }
]
```

```javascript
// src/index.js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url)

    // GET /kv/:key
    if (url.pathname.startsWith('/kv/')) {
      const key = url.pathname.split('/kv/')[1]

      if (request.method === 'GET') {
        const value = await env.MY_KV.get(key)
        if (value === null) {
          return new Response('Not Found', { status: 404 })
        }
        return new Response(value)
      }

      // PUT /kv/:key
      if (request.method === 'PUT') {
        const value = await request.text()
        await env.MY_KV.put(key, value)
        return new Response('OK')
      }

      // DELETE /kv/:key
      if (request.method === 'DELETE') {
        await env.MY_KV.delete(key)
        return new Response('Deleted')
      }
    }

    return new Response('Not Found', { status: 404 })
  }
}
```

**KV高级用法**:

```javascript
// 1. 带过期时间
await env.MY_KV.put('session:user123', sessionData, {
  expirationTtl: 3600  // 1小时后过期
})

// 2. 带元数据
await env.MY_KV.put('user:profile', JSON.stringify(profile), {
  metadata: { version: 1, updatedAt: Date.now() }
})

// 3. 获取带元数据
const { value, metadata } = await env.MY_KV.getWithMetadata('user:profile')

// 4. 列出所有键
const { keys } = await env.MY_KV.list()
for (const key of keys) {
  console.log(key.name, key.metadata)
}

// 5. 列出带前缀的键
const { keys } = await env.MY_KV.list({ prefix: 'user:' })

// 6. 批量操作 (注意：每个操作都是异步的)
await Promise.all([
  env.MY_KV.put('key1', 'value1'),
  env.MY_KV.put('key2', 'value2'),
  env.MY_KV.put('key3', 'value3')
])
```

---

### 2.4 Durable Objects

**Durable Objects**: 有状态的边缘对象，支持强一致性和WebSocket。

```bash
# wrangler.toml
name = "my-worker"
main = "src/index.js"

[[durable_objects.bindings]]
name = "COUNTER"
class_name = "Counter"
script_name = "my-worker"
```

```javascript
// src/index.js

// Durable Object类定义
export class Counter {
  constructor(state, env) {
    this.state = state
  }

  async fetch(request) {
    const url = new URL(request.url)

    // 获取当前计数
    if (url.pathname === '/get') {
      let value = await this.state.storage.get('counter') || 0
      return new Response(value.toString())
    }

    // 增加计数
    if (url.pathname === '/increment') {
      let value = await this.state.storage.get('counter') || 0
      value++
      await this.state.storage.put('counter', value)
      return new Response(value.toString())
    }

    return new Response('Not Found', { status: 404 })
  }
}

// Worker入口
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url)
    const counterId = url.searchParams.get('id') || 'global'

    // 获取Durable Object实例
    const id = env.COUNTER.idFromName(counterId)
    const stub = env.COUNTER.get(id)

    // 转发请求到Durable Object
    return stub.fetch(request)
  }
}
```

**WebSocket示例**:

```javascript
export class ChatRoom {
  constructor(state, env) {
    this.state = state
    this.sessions = []
  }

  async fetch(request) {
    // WebSocket升级
    const upgradeHeader = request.headers.get('Upgrade')
    if (upgradeHeader !== 'websocket') {
      return new Response('Expected WebSocket', { status: 400 })
    }

    const webSocketPair = new WebSocketPair()
    const [client, server] = Object.values(webSocketPair)

    // 接受WebSocket连接
    await this.handleSession(server)

    return new Response(null, {
      status: 101,
      webSocket: client
    })
  }

  async handleSession(webSocket) {
    webSocket.accept()
    this.sessions.push(webSocket)

    webSocket.addEventListener('message', async (event) => {
      // 广播消息给所有连接
      const message = event.data
      for (const session of this.sessions) {
        try {
          session.send(message)
        } catch (err) {
          // 移除断开的连接
          this.sessions = this.sessions.filter(s => s !== session)
        }
      }
    })

    webSocket.addEventListener('close', () => {
      this.sessions = this.sessions.filter(s => s !== webSocket)
    })
  }
}
```

---

### 2.5 生产实践

**示例: 图片优化Worker**:

```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url)

    // 解析图片参数
    const width = parseInt(url.searchParams.get('w')) || null
    const quality = parseInt(url.searchParams.get('q')) || 85
    const format = url.searchParams.get('f') || 'auto'

    // 原始图片URL
    const imageUrl = url.pathname.substring(1)
    if (!imageUrl) {
      return new Response('Missing image URL', { status: 400 })
    }

    // 缓存键
    const cacheKey = `${imageUrl}?w=${width}&q=${quality}&f=${format}`
    const cache = caches.default

    // 检查缓存
    let response = await cache.match(cacheKey)
    if (response) {
      return response
    }

    // 获取原始图片
    const imageResponse = await fetch(imageUrl, {
      cf: {
        cacheEverything: true,
        cacheTtl: 86400  // 24小时
      }
    })

    if (!imageResponse.ok) {
      return new Response('Image not found', { status: 404 })
    }

    // 图片优化选项
    const options = {
      quality: quality,
      format: format
    }

    if (width) {
      options.width = width
    }

    // Cloudflare图片优化
    response = new Response(imageResponse.body, imageResponse)
    response.headers.set('Cache-Control', 'public, max-age=86400')
    response.headers.set('CF-Polish', 'lossy')

    // 存入缓存
    ctx.waitUntil(cache.put(cacheKey, response.clone()))

    return response
  }
}
```

---

## 3. AWS Lambda@Edge

### 3.1 架构与触发点

**Lambda@Edge架构**:

```yaml
架构层次:
  用户请求
    ↓
  CloudFront边缘节点 (全球410+)
    ↓ 触发Lambda@Edge
  4个触发点:
    1. Viewer Request  (最早)
    2. Origin Request
    3. Origin Response
    4. Viewer Response (最晚)
    ↓
  源服务器 (可选)

4个触发点详解:

1. Viewer Request:
   时机: 收到用户请求后，访问缓存前
   用途:
     - 认证/授权
     - URL重写
     - A/B测试
     - Bot检测
   限制:
     - 超时: 5s
     - 内存: 128MB
     - 包大小: 1MB

2. Origin Request:
   时机: 缓存未命中，请求源服务器前
   用途:
     - 修改请求头
     - 添加认证
     - 请求合并
     - 动态源选择
   限制:
     - 超时: 30s
     - 内存: 128MB
     - 包大小: 50MB

3. Origin Response:
   时机: 收到源服务器响应后
   用途:
     - 修改响应头
     - 响应过滤
     - 内容转换
     - 缓存控制
   限制:
     - 超时: 30s
     - 内存: 128MB
     - 包大小: 1MB

4. Viewer Response:
   时机: 返回响应给用户前
   用途:
     - 添加安全头
     - Cookie处理
     - 响应定制
     - 日志记录
   限制:
     - 超时: 5s
     - 内存: 128MB
     - 包大小: 1MB
```

---

### 3.2 部署Lambda@Edge

```bash
# 1. 创建Lambda函数 (us-east-1区域必须)
# lambda-edge-viewer-request.js
```

```javascript
// lambda-edge-viewer-request.js
'use strict'

exports.handler = async (event) => {
    const request = event.Records[0].cf.request
    const headers = request.headers

    // 1. 简单认证
    const authHeader = headers['authorization']
    if (!authHeader || authHeader[0].value !== 'Bearer secret-token') {
        return {
            status: '401',
            statusDescription: 'Unauthorized',
            body: 'Unauthorized'
        }
    }

    // 2. URL重写
    if (request.uri === '/old-page') {
        request.uri = '/new-page'
    }

    // 3. 添加自定义头
    headers['x-custom-header'] = [{ value: 'custom-value' }]

    return request
}
```

```bash
# 2. 创建Lambda函数
aws lambda create-function \
  --region us-east-1 \
  --function-name viewer-request-function \
  --runtime nodejs18.x \
  --role arn:aws:iam::ACCOUNT:role/lambda-edge-role \
  --handler lambda-edge-viewer-request.handler \
  --zip-file fileb://function.zip

# 3. 发布版本
aws lambda publish-version \
  --function-name viewer-request-function

# 输出:
# {
#   "FunctionArn": "arn:aws:lambda:us-east-1:ACCOUNT:function:viewer-request-function:1",
#   "Version": "1"
# }

# 4. 关联到CloudFront
# CloudFront Distribution配置:
```

```json
{
  "DistributionConfig": {
    "DefaultCacheBehavior": {
      "LambdaFunctionAssociations": {
        "Quantity": 1,
        "Items": [
          {
            "LambdaFunctionARN": "arn:aws:lambda:us-east-1:ACCOUNT:function:viewer-request-function:1",
            "EventType": "viewer-request",
            "IncludeBody": false
          }
        ]
      }
    }
  }
}
```

---

### 3.3 实战案例

**案例1: A/B测试**:

```javascript
// viewer-request: A/B测试
'use strict'

exports.handler = async (event) => {
    const request = event.Records[0].cf.request
    const headers = request.headers

    // 检查Cookie
    const cookieHeader = headers['cookie']
    let abTestGroup = null

    if (cookieHeader) {
        const cookies = cookieHeader[0].value
        const match = cookies.match(/ab_test=([AB])/)
        if (match) {
            abTestGroup = match[1]
        }
    }

    // 随机分配组 (如果没有Cookie)
    if (!abTestGroup) {
        abTestGroup = Math.random() < 0.5 ? 'A' : 'B'
    }

    // 重写URL
    request.uri = `/version-${abTestGroup}${request.uri}`

    return request
}
```

```javascript
// viewer-response: 设置A/B测试Cookie
'use strict'

exports.handler = async (event) => {
    const request = event.Records[0].cf.request
    const response = event.Records[0].cf.response
    const headers = response.headers

    // 从请求中获取组
    const uri = request.uri
    const match = uri.match(/version-([AB])/)
    if (match) {
        const group = match[1]

        // 设置Cookie (有效期30天)
        headers['set-cookie'] = [{
            key: 'Set-Cookie',
            value: `ab_test=${group}; Path=/; Max-Age=2592000; Secure; HttpOnly`
        }]
    }

    return response
}
```

---

**案例2: 图片格式转换**:

```javascript
// origin-request: 请求WebP格式
'use strict'

exports.handler = async (event) => {
    const request = event.Records[0].cf.request
    const headers = request.headers

    // 检查浏览器是否支持WebP
    const acceptHeader = headers['accept']
    const supportsWebP = acceptHeader &&
                         acceptHeader[0].value.includes('image/webp')

    // 修改图片请求
    if (supportsWebP && request.uri.match(/\.(jpg|jpeg|png)$/)) {
        const ext = request.uri.split('.').pop()
        request.uri = request.uri.replace(new RegExp(`\\.${ext}$`), '.webp')

        // 添加自定义头告知源服务器
        headers['x-original-format'] = [{ value: ext }]
    }

    return request
}
```

---

**案例3: 安全头注入**:

```javascript
// viewer-response: 添加安全头
'use strict'

exports.handler = async (event) => {
    const response = event.Records[0].cf.response
    const headers = response.headers

    // 安全头
    headers['strict-transport-security'] = [{
        key: 'Strict-Transport-Security',
        value: 'max-age=63072000; includeSubdomains; preload'
    }]

    headers['x-content-type-options'] = [{
        key: 'X-Content-Type-Options',
        value: 'nosniff'
    }]

    headers['x-frame-options'] = [{
        key: 'X-Frame-Options',
        value: 'DENY'
    }]

    headers['x-xss-protection'] = [{
        key: 'X-XSS-Protection',
        value: '1; mode=block'
    }]

    headers['content-security-policy'] = [{
        key: 'Content-Security-Policy',
        value: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }]

    return response
}
```

---

### 3.4 最佳实践

```yaml
Lambda@Edge最佳实践:

1. 区域限制:
   ✅ 必须在us-east-1创建
   ✅ 使用版本号 (不能用$LATEST)
   ✅ 部署前充分测试

2. 性能优化:
   ✅ 减小包大小
   ✅ 避免重复初始化
   ✅ 使用缓存
   ✅ 异步处理放到Origin Request

3. 超时控制:
   ✅ Viewer Request/Response: < 5s
   ✅ Origin Request/Response: < 30s
   ✅ 设置合理超时时间

4. 错误处理:
   ✅ Try-catch所有异步操作
   ✅ 返回友好错误页面
   ✅ 记录CloudWatch日志

5. 成本控制:
   ✅ 只在必要时使用
   ✅ 避免不必要的Origin Request
   ✅ 利用CloudFront缓存

6. 安全考虑:
   ✅ 最小权限原则
   ✅ 敏感信息使用环境变量
   ✅ 输入验证
   ✅ 防止注入攻击
```

---

## 4. Fastly Compute@Edge

### 4.1 WebAssembly优势

```yaml
Fastly Compute@Edge特点:
  - 基于WebAssembly
  - 多语言编译到WASM
  - 冷启动 < 35μs (微秒!)
  - 安全沙箱隔离

WebAssembly优势:
  ✅ 接近原生性能
  ✅ 语言中立 (Rust/Go/JS/Python)
  ✅ 内存安全
  ✅ 可移植性
  ✅ 小型二进制

vs V8 Isolates vs Containers:
  WebAssembly:
    - 启动: < 35μs
    - 内存: 少
    - 安全: 高

  V8 Isolates:
    - 启动: < 5ms
    - 内存: 中
    - 安全: 高

  Containers:
    - 启动: 100ms-3s
    - 内存: 多
    - 安全: 中
```

---

### 4.2 Rust开发

```bash
# 1. 安装Fastly CLI
brew install fastly/tap/fastly
# 或
curl -L https://github.com/fastly/cli/releases/latest/download/fastly_<version>_linux_amd64.tar.gz | tar -xz

# 2. 创建新项目
fastly compute init

# 选择:
# Language: Rust
# Starter kit: Default starter for Rust
```

```rust
// src/main.rs
use fastly::http::{HeaderValue, Method, StatusCode};
use fastly::{Error, Request, Response};

#[fastly::main]
fn main(req: Request) -> Result<Response, Error> {
    // 路由
    match (req.get_method(), req.get_path()) {
        (&Method::GET, "/") => Ok(Response::from_status(StatusCode::OK)
            .with_body_text_plain("Hello from Fastly Compute@Edge!\n")),

        (&Method::GET, "/api/info") => handle_info(req),

        (&Method::POST, "/api/echo") => handle_echo(req),

        _ => Ok(Response::from_status(StatusCode::NOT_FOUND)
            .with_body_text_plain("Not Found\n")),
    }
}

fn handle_info(req: Request) -> Result<Response, Error> {
    // 获取请求信息
    let client_ip = req.get_client_ip_addr().unwrap_or_else(|| "unknown".parse().unwrap());
    let user_agent = req.get_header_str("User-Agent").unwrap_or("unknown");

    let body = format!(
        "Client IP: {}\nUser-Agent: {}\n",
        client_ip, user_agent
    );

    Ok(Response::from_status(StatusCode::OK)
        .with_body_text_plain(&body))
}

fn handle_echo(mut req: Request) -> Result<Response, Error> {
    // 读取请求体
    let body = req.take_body_str();

    Ok(Response::from_status(StatusCode::OK)
        .with_header("Content-Type", "application/json")
        .with_body_json(&serde_json::json!({
            "echo": body
        }))?)
}
```

```bash
# 3. 本地测试
fastly compute serve

# 4. 部署
fastly compute publish
```

---

**示例: 图片优化**:

```rust
// src/main.rs
use fastly::http::{Method, StatusCode};
use fastly::{Backend, Error, Request, Response};

#[fastly::main]
fn main(req: Request) -> Result<Response, Error> {
    match (req.get_method(), req.get_path()) {
        (&Method::GET, path) if path.starts_with("/img/") => {
            optimize_image(req)
        }
        _ => Ok(Response::from_status(StatusCode::NOT_FOUND)),
    }
}

fn optimize_image(req: Request) -> Result<Response, Error> {
    // 解析参数
    let query = req.get_query_str().unwrap_or("");
    let width: Option<u32> = query
        .split('&')
        .find(|s| s.starts_with("w="))
        .and_then(|s| s[2..].parse().ok());

    let quality: u8 = query
        .split('&')
        .find(|s| s.starts_with("q="))
        .and_then(|s| s[2..].parse().ok())
        .unwrap_or(85);

    // 获取原始图片
    let backend = Backend::from_name("origin").unwrap();
    let mut bereq = Request::get(req.get_path())
        .with_header("Host", "example.com");

    let mut beresp = bereq.send(backend)?;

    if !beresp.get_status().is_success() {
        return Ok(beresp);
    }

    // 这里可以集成图片处理库 (如image crate)
    // 实际生产中需要编译到WASM的图片处理库

    // 添加缓存头
    beresp.set_header("Cache-Control", "public, max-age=86400");

    Ok(beresp)
}
```

---

### 4.3 JavaScript开发

```bash
# 创建JavaScript项目
fastly compute init

# 选择:
# Language: JavaScript
```

```javascript
// src/index.js
import { includeBytes } from "fastly:experimental"

async function handleRequest(event) {
  const req = event.request
  const url = new URL(req.url)

  // 路由
  if (url.pathname === '/') {
    return new Response('Hello from Fastly Compute@Edge!', {
      status: 200,
      headers: { 'Content-Type': 'text/plain' }
    })
  }

  if (url.pathname === '/api/data') {
    return handleData(req)
  }

  // 代理到后端
  return fetch(req, {
    backend: "origin"
  })
}

async function handleData(req) {
  const data = {
    message: 'Hello from Fastly!',
    timestamp: new Date().toISOString(),
    // 客户端信息
    clientIp: req.headers.get('fastly-client-ip'),
    geo: {
      country: req.headers.get('fastly-geo-country-code'),
      city: req.headers.get('fastly-geo-city')
    }
  }

  return new Response(JSON.stringify(data, null, 2), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}

addEventListener("fetch", event => event.respondWith(handleRequest(event)))
```

---

### 4.4 边缘存储

**Fastly KV Store**:

```rust
// Rust示例
use fastly::kv_store::KVStore;

#[fastly::main]
fn main(req: Request) -> Result<Response, Error> {
    // 打开KV存储
    let kv = KVStore::open("my_store")?;

    match req.get_path() {
        "/kv/get" => {
            let key = req.get_query_parameter("key").unwrap_or("default");

            match kv.lookup(key) {
                Ok(Some(value)) => {
                    Ok(Response::from_status(StatusCode::OK)
                        .with_body_text_plain(&value.into_string()?))
                }
                Ok(None) => {
                    Ok(Response::from_status(StatusCode::NOT_FOUND)
                        .with_body_text_plain("Not Found"))
                }
                Err(e) => {
                    Ok(Response::from_status(StatusCode::INTERNAL_SERVER_ERROR)
                        .with_body_text_plain(&e.to_string()))
                }
            }
        }
        _ => Ok(Response::from_status(StatusCode::NOT_FOUND)),
    }
}
```

---

## 5. WebAssembly在边缘

### 5.1 WASI标准

```yaml
WASI (WebAssembly System Interface):
  标准化的系统接口
  允许WASM访问:
    - 文件系统
    - 网络
    - 环境变量
    - 随机数

  特点:
    ✅ 可移植
    ✅ 安全沙箱
    ✅ 跨平台
    ✅ 高性能

WASI边缘运行时:
  - Wasmtime
  - WasmEdge
  - Wasmer
  - Spin (Fermyon)
```

---

### 5.2 性能优势

```yaml
WebAssembly性能对比:

启动时间:
  WASM: 35μs
  V8 Isolates: 5ms
  Node.js: 100ms
  Python: 300ms
  Container: 1s

执行速度:
  Native C: 1.0x (基准)
  WASM: 1.2-1.5x
  JavaScript (V8): 2-5x
  Python: 10-100x

内存占用:
  WASM: 几KB-几MB
  V8: 几MB
  Node.js: 20-50MB
  Container: 50-200MB

安全性:
  WASM: 沙箱隔离 + 内存安全
  V8: 沙箱隔离
  Container: 进程隔离
```

---

### 5.3 多语言支持

**Rust编译到WASM**:

```bash
# 1. 添加WASM目标
rustup target add wasm32-wasi

# 2. 编译
cargo build --target wasm32-wasi --release

# 3. 运行
wasmtime target/wasm32-wasi/release/myapp.wasm
```

```rust
// src/main.rs
fn main() {
    println!("Hello from Rust WASM!");

    // 读取环境变量
    if let Ok(name) = std::env::var("NAME") {
        println!("Hello, {}!", name);
    }
}
```

---

**Go编译到WASM**:

```bash
# 编译 (实验性)
GOOS=wasip1 GOARCH=wasm go build -o main.wasm main.go

# 运行
wasmtime main.wasm
```

```go
// main.go
package main

import "fmt"

func main() {
    fmt.Println("Hello from Go WASM!")
}
```

---

**Python编译到WASM**:

```bash
# 使用Pyodide或wasm-python
# (Python WASM支持还在发展中)
```

---

### 5.4 边缘运行时

**Fermyon Spin**:

```bash
# 安装Spin
curl -fsSL https://developer.fermyon.com/downloads/install.sh | bash

# 创建新应用
spin new http-rust my-app
cd my-app

# 构建
spin build

# 本地运行
spin up

# 部署到Fermyon Cloud
spin deploy
```

```rust
// src/lib.rs (Spin应用)
use spin_sdk::{
    http::{Request, Response},
    http_component,
};

#[http_component]
fn handle_request(req: Request) -> Response {
    Response::builder()
        .status(200)
        .header("Content-Type", "text/plain")
        .body(Some("Hello from Spin!".into()))
        .build()
}
```

---

## 6. 边缘Serverless最佳实践

### 6.1 性能优化

```yaml
1. 最小化代码大小:
   ✅ Tree shaking
   ✅ 代码分割
   ✅ 压缩
   ✅ 移除未使用依赖

2. 减少外部调用:
   ✅ 本地处理优先
   ✅ 批量API调用
   ✅ 使用边缘存储 (KV)
   ✅ 缓存外部数据

3. 优化算法:
   ✅ O(1)查找优先
   ✅ 避免深度递归
   ✅ 流式处理大数据

4. 利用缓存:
   ✅ HTTP缓存头
   ✅ 边缘KV存储
   ✅ Durable Objects

5. 异步处理:
   ✅ Promise.all并发
   ✅ 非阻塞I/O
   ✅ 后台任务
```

---

### 6.2 安全考虑

```yaml
1. 输入验证:
   ✅ 验证所有输入
   ✅ 防止注入攻击
   ✅ 限制请求大小

2. 认证授权:
   ✅ JWT验证
   ✅ API密钥
   ✅ OAuth2.0
   ✅ 速率限制

3. 数据保护:
   ✅ HTTPS only
   ✅ 安全头 (CSP, HSTS)
   ✅ Cookie安全标志
   ✅ 敏感数据加密

4. DDoS防护:
   ✅ 速率限制
   ✅ IP黑名单
   ✅ Bot检测
   ✅ Challenge页面

5. 日志与审计:
   ✅ 记录访问日志
   ✅ 异常监控
   ✅ 安全事件告警
```

---

### 6.3 成本优化

```yaml
1. 选择合适平台:
   Cloudflare Workers: 免费额度最大
   AWS Lambda@Edge: AWS生态
   Fastly: 高性能需求

2. 优化调用次数:
   ✅ 充分利用缓存
   ✅ 减少Origin请求
   ✅ 批量处理

3. 监控使用量:
   ✅ 设置告警阈值
   ✅ 定期review账单
   ✅ 识别异常流量

4. 代码优化:
   ✅ 减少CPU时间
   ✅ 降低内存使用
   ✅ 避免超时

5. 免费额度利用:
   Cloudflare: 10万请求/天
   Vercel: 10万请求/月
   Deno Deploy: 10万请求/月
```

---

### 6.4 监控与调试

```yaml
监控指标:
  ✅ 请求数 (RPS)
  ✅ 响应时间 (P50/P95/P99)
  ✅ 错误率
  ✅ CPU时间
  ✅ 内存使用
  ✅ 缓存命中率

日志工具:
  Cloudflare: Logpush, Workers Analytics
  AWS: CloudWatch Logs
  Fastly: Real-time Log Streaming

调试技巧:
  ✅ 本地开发环境
  ✅ console.log (生产谨慎)
  ✅ 单元测试
  ✅ 集成测试
  ✅ 金丝雀部署

告警配置:
  ✅ 错误率 > 1%
  ✅ P95延迟 > 500ms
  ✅ CPU超时
  ✅ 内存溢出
```

---

## 7. 总结

```yaml
本章要点:
  ✅ 边缘Serverless概述 (定义/优势/场景)
  ✅ Cloudflare Workers (V8/KV/Durable Objects)
  ✅ AWS Lambda@Edge (4个触发点/实战)
  ✅ Fastly Compute@Edge (WASM/Rust/JS)
  ✅ WebAssembly在边缘 (WASI/性能/多语言)
  ✅ 最佳实践 (性能/安全/成本/监控)

边缘Serverless核心价值:
  ⭐ 超低延迟 (< 50ms)
  ⭐ 全球分布
  ⭐ 零冷启动
  ⭐ 自动扩缩容
  ⭐ 简化架构

平台选择建议:
  Cloudflare Workers:
    ✅ 最低延迟
    ✅ 慷慨免费额度
    ✅ 简单易用
    ✅ 全球275+节点

  AWS Lambda@Edge:
    ✅ AWS生态集成
    ✅ 企业级支持
    ✅ 灵活触发点

  Fastly Compute@Edge:
    ✅ 极致性能
    ✅ WebAssembly
    ✅ 多语言支持

关键技术:
  ✅ V8 Isolates
  ✅ WebAssembly
  ✅ 边缘KV存储
  ✅ Durable Objects
  ✅ WASI标准

应用场景:
  ✅ API加速
  ✅ 内容个性化
  ✅ 认证授权
  ✅ 图片优化
  ✅ 边缘缓存
  ✅ 安全防护
```

---

**下一章预告**:

**05 - Serverless安全**:

- Serverless安全威胁
- 认证与授权
- 数据加密
- 安全最佳实践
- 合规性要求

---

**完成日期**: 2025-10-19
**版本**: v1.0
**作者**: 云原生专家团队

**Tags**: `#EdgeServerless` `#CloudflareWorkers` `#LambdaEdge` `#WebAssembly` `#FastlyCompute`

---

## 相关文档

### 本模块相关

- [Serverless概述与架构](./01_Serverless概述与架构.md) - Serverless概述与架构
- [Knative深度解析](./02_Knative深度解析.md) - Knative深度解析
- [OpenFaaS实战](./03_OpenFaaS实战.md) - OpenFaaS实战
- [Serverless安全](./05_Serverless安全.md) - Serverless安全
- [Serverless性能优化](./06_Serverless性能优化.md) - Serverless性能优化
- [Serverless CI/CD](./07_Serverless_CICD.md) - Serverless CI/CD
- [Serverless实战案例](./08_Serverless实战案例.md) - Serverless实战案例
- [Serverless最佳实践](./09_Serverless最佳实践.md) - Serverless最佳实践
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [边缘计算技术详解](../17_边缘计算技术详解/README.md) - 边缘计算技术
- [边缘AI与推理优化](../17_边缘计算技术详解/06_边缘AI与推理优化.md) - 边缘AI与推理优化
- [WebAssembly技术详解](../10_WebAssembly技术详解/README.md) - WebAssembly技术
- [容器技术发展趋势](../09_容器技术发展趋势/README.md) - 容器技术发展趋势

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新
