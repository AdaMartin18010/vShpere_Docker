# 05 - Serverless安全

**作者**: 云原生专家团队  
**创建日期**: 2025-10-19  
**最后更新**: 2025-10-19  
**版本**: v1.0

---

## 📋 本章导航

- [05 - Serverless安全](#05---serverless安全)
  - [📋 本章导航](#-本章导航)
  - [1. Serverless安全概述](#1-serverless安全概述)
    - [1.1 安全威胁模型](#11-安全威胁模型)
    - [1.2 OWASP Serverless Top 10](#12-owasp-serverless-top-10)
    - [1.3 责任共担模型](#13-责任共担模型)
  - [2. 认证与授权](#2-认证与授权)
    - [2.1 JWT验证](#21-jwt验证)
    - [2.2 OAuth 2.0/OIDC](#22-oauth-20oidc)
    - [2.3 API密钥管理](#23-api密钥管理)
    - [2.4 细粒度权限控制](#24-细粒度权限控制)
  - [3. 数据安全](#3-数据安全)
    - [3.1 数据加密](#31-数据加密)
    - [3.2 密钥管理](#32-密钥管理)
    - [3.3 敏感数据处理](#33-敏感数据处理)
  - [4. 网络安全](#4-网络安全)
    - [4.1 DDoS防护](#41-ddos防护)
    - [4.2 速率限制](#42-速率限制)
    - [4.3 WAF规则](#43-waf规则)
    - [4.4 IP访问控制](#44-ip访问控制)
  - [5. 代码安全](#5-代码安全)
    - [5.1 依赖安全](#51-依赖安全)
    - [5.2 安全编码](#52-安全编码)
    - [5.3 Secrets管理](#53-secrets管理)
    - [5.4 代码审计](#54-代码审计)
  - [6. 合规性](#6-合规性)
    - [6.1 GDPR合规](#61-gdpr合规)
    - [6.2 HIPAA合规](#62-hipaa合规)
    - [6.3 SOC 2/PCI DSS](#63-soc-2pci-dss)
  - [7. 安全监控](#7-安全监控)
    - [7.1 审计日志](#71-审计日志)
    - [7.2 异常检测](#72-异常检测)
    - [7.3 安全事件响应](#73-安全事件响应)
  - [8. 总结](#8-总结)

---

## 1. Serverless安全概述

### 1.1 安全威胁模型

```yaml
Serverless特有安全风险:

1. 扩大的攻击面:
   - 大量分布式函数
   - 多个事件源
   - 第三方依赖
   - API Gateway暴露

2. 权限管理复杂:
   - 每个函数独立权限
   - 细粒度IAM策略
   - 跨服务访问
   - 权限过度授予

3. 数据泄露风险:
   - 日志中的敏感信息
   - 环境变量暴露
   - 临时存储泄露
   - 响应中的数据

4. 供应链攻击:
   - npm/pip包漏洞
   - 恶意依赖注入
   - 构建过程污染

5. 运行时攻击:
   - 注入攻击 (SQL/NoSQL/Command)
   - 反序列化漏洞
   - SSRF攻击
   - XXE攻击

6. 拒绝服务:
   - 资源耗尽攻击
   - 成本爆炸
   - 并发限制
   - 超时利用

7. 不安全配置:
   - 默认配置
   - 过宽权限
   - 未加密通信
   - 弱认证

8. 可见性不足:
   - 分布式追踪困难
   - 日志分散
   - 攻击检测延迟
```

---

### 1.2 OWASP Serverless Top 10

```yaml
OWASP Serverless应用安全Top 10 (2023):

1. 注入攻击 (Injection):
   风险: 高
   示例:
     - SQL注入
     - NoSQL注入
     - Command注入
     - LDAP注入
   
   防护:
     ✅ 参数化查询
     ✅ 输入验证
     ✅ 输出编码
     ✅ 最小权限原则

2. 失效的认证 (Broken Authentication):
   风险: 高
   示例:
     - 弱JWT密钥
     - 缺少令牌验证
     - 会话固定
   
   防护:
     ✅ 强认证机制
     ✅ JWT最佳实践
     ✅ 多因素认证
     ✅ 定期轮换密钥

3. 敏感数据暴露 (Sensitive Data Exposure):
   风险: 高
   示例:
     - 日志中的密码
     - 未加密传输
     - 明文存储
   
   防护:
     ✅ 数据加密
     ✅ 安全日志
     ✅ 脱敏处理
     ✅ 密钥管理

4. XML外部实体 (XXE):
   风险: 中
   示例:
     - XML解析漏洞
     - 文件读取
     - SSRF
   
   防护:
     ✅ 禁用外部实体
     ✅ 使用安全解析器
     ✅ 输入验证

5. 失效的访问控制 (Broken Access Control):
   风险: 高
   示例:
     - 越权访问
     - 水平/垂直越权
     - IDOR漏洞
   
   防护:
     ✅ 严格权限检查
     ✅ 细粒度IAM
     ✅ 最小权限原则
     ✅ 资源级别授权

6. 安全配置错误 (Security Misconfiguration):
   风险: 中
   示例:
     - 默认凭证
     - 调试模式开启
     - 错误信息泄露
   
   防护:
     ✅ 安全基线配置
     ✅ 自动化配置检查
     ✅ 定期审计

7. 跨站脚本 (XSS):
   风险: 中
   示例:
     - 反射型XSS
     - 存储型XSS
     - DOM型XSS
   
   防护:
     ✅ 输出编码
     ✅ CSP策略
     ✅ 输入验证

8. 不安全的反序列化 (Insecure Deserialization):
   风险: 高
   示例:
     - 远程代码执行
     - 权限提升
     - DoS攻击
   
   防护:
     ✅ 避免反序列化不可信数据
     ✅ 使用安全序列化格式
     ✅ 签名验证

9. 使用已知漏洞的组件 (Using Components with Known Vulnerabilities):
   风险: 高
   示例:
     - 过期npm包
     - 已知CVE漏洞
   
   防护:
     ✅ 依赖扫描
     ✅ 定期更新
     ✅ SCA工具

10. 不足的日志和监控 (Insufficient Logging & Monitoring):
    风险: 中
    示例:
      - 无审计日志
      - 攻击检测延迟
    
    防护:
      ✅ 全面日志记录
      ✅ 实时监控
      ✅ 告警机制
      ✅ SIEM集成
```

---

### 1.3 责任共担模型

```yaml
云服务商 vs 客户责任:

云服务商责任:
  ✅ 物理安全
  ✅ 网络基础设施
  ✅ 虚拟化层安全
  ✅ 平台安全更新
  ✅ DDoS基础防护
  ✅ 数据中心冗余

客户责任:
  ✅ 应用代码安全
  ✅ 依赖包管理
  ✅ 配置管理
  ✅ 密钥管理
  ✅ 访问控制
  ✅ 数据加密
  ✅ 审计日志
  ✅ 合规性

AWS Lambda示例:
  AWS负责:
    - Lambda运行时安全
    - 底层基础设施
    - 网络隔离
  
  客户负责:
    - 函数代码
    - IAM策略
    - VPC配置
    - 环境变量
    - 层安全

Cloudflare Workers示例:
  Cloudflare负责:
    - V8隔离安全
    - 边缘节点安全
    - DDoS防护
  
  客户负责:
    - Worker代码
    - KV数据
    - Secrets
    - 路由规则
```

---

## 2. 认证与授权

### 2.1 JWT验证

**JWT基础**:

```javascript
// Cloudflare Workers - JWT验证
import jwt from '@tsndr/cloudflare-worker-jwt'

export default {
  async fetch(request, env) {
    // 获取Authorization头
    const authHeader = request.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response('Unauthorized', { status: 401 })
    }
    
    const token = authHeader.substring(7)
    
    try {
      // 验证JWT
      const isValid = await jwt.verify(token, env.JWT_SECRET)
      if (!isValid) {
        return new Response('Invalid token', { status: 401 })
      }
      
      // 解码JWT
      const { payload } = jwt.decode(token)
      
      // 检查过期时间
      if (payload.exp && payload.exp < Date.now() / 1000) {
        return new Response('Token expired', { status: 401 })
      }
      
      // 检查权限
      if (!payload.scopes || !payload.scopes.includes('read')) {
        return new Response('Forbidden', { status: 403 })
      }
      
      // 业务逻辑
      return new Response(JSON.stringify({
        message: 'Success',
        user: payload.sub,
        scopes: payload.scopes
      }), {
        headers: { 'Content-Type': 'application/json' }
      })
    } catch (error) {
      return new Response('Authentication error', { status: 401 })
    }
  }
}
```

**AWS Lambda - JWT验证**:

```javascript
// lambda-jwt-authorizer.js
const jwt = require('jsonwebtoken')

exports.handler = async (event) => {
    const token = event.authorizationToken
    
    if (!token) {
        throw new Error('Unauthorized')
    }
    
    try {
        // 验证JWT
        const decoded = jwt.verify(token.replace('Bearer ', ''), process.env.JWT_SECRET)
        
        // 生成IAM策略
        return generatePolicy(decoded.sub, 'Allow', event.methodArn, decoded)
    } catch (error) {
        console.error('JWT verification failed:', error)
        throw new Error('Unauthorized')
    }
}

function generatePolicy(principalId, effect, resource, context = {}) {
    return {
        principalId: principalId,
        policyDocument: {
            Version: '2012-10-17',
            Statement: [{
                Action: 'execute-api:Invoke',
                Effect: effect,
                Resource: resource
            }]
        },
        context: {
            userId: context.sub,
            email: context.email,
            scopes: JSON.stringify(context.scopes || [])
        }
    }
}
```

**JWT最佳实践**:

```yaml
JWT安全实践:

1. 密钥管理:
   ✅ 使用强密钥 (>=256位)
   ✅ 定期轮换密钥
   ✅ 使用KMS存储密钥
   ✅ 不同环境不同密钥

2. Token配置:
   ✅ 设置合理过期时间 (15分钟-1小时)
   ✅ 使用refresh token
   ✅ 包含必要声明 (iss, sub, exp, iat)
   ✅ 添加jti (JWT ID) 防重放

3. 验证检查:
   ✅ 验证签名
   ✅ 检查过期时间
   ✅ 验证issuer
   ✅ 验证audience
   ✅ 检查not before (nbf)

4. 不要在JWT中存储:
   ❌ 密码
   ❌ 信用卡号
   ❌ 社会安全号码
   ❌ 大量数据

5. 传输安全:
   ✅ 仅通过HTTPS
   ✅ HttpOnly Cookie (如果用Cookie)
   ✅ Secure flag
   ✅ SameSite属性
```

---

### 2.2 OAuth 2.0/OIDC

**OAuth 2.0集成**:

```javascript
// AWS Lambda - OAuth 2.0验证
const axios = require('axios')

exports.handler = async (event) => {
    const token = event.headers.Authorization?.replace('Bearer ', '')
    
    if (!token) {
        return {
            statusCode: 401,
            body: JSON.stringify({ error: 'No token provided' })
        }
    }
    
    try {
        // 验证access token (调用OAuth服务器)
        const response = await axios.get(`${process.env.OAUTH_INTROSPECT_URL}`, {
            headers: {
                'Authorization': `Basic ${Buffer.from(`${process.env.CLIENT_ID}:${process.env.CLIENT_SECRET}`).toString('base64')}`
            },
            params: {
                token: token
            }
        })
        
        if (!response.data.active) {
            return {
                statusCode: 401,
                body: JSON.stringify({ error: 'Token is not active' })
            }
        }
        
        // 检查scopes
        const scopes = response.data.scope.split(' ')
        if (!scopes.includes('read:data')) {
            return {
                statusCode: 403,
                body: JSON.stringify({ error: 'Insufficient permissions' })
            }
        }
        
        // 业务逻辑
        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Success',
                user: response.data.sub,
                scopes: scopes
            })
        }
    } catch (error) {
        console.error('OAuth verification failed:', error)
        return {
            statusCode: 401,
            body: JSON.stringify({ error: 'Authentication failed' })
        }
    }
}
```

**OIDC (OpenID Connect)**:

```javascript
// Cloudflare Workers - OIDC验证
import { verify } from '@tsndr/cloudflare-worker-jwt'

export default {
  async fetch(request, env) {
    const token = request.headers.get('Authorization')?.replace('Bearer ', '')
    
    if (!token) {
      return new Response('Unauthorized', { status: 401 })
    }
    
    try {
      // 获取OIDC配置
      const discoveryUrl = `${env.OIDC_ISSUER}/.well-known/openid-configuration`
      const discoveryResponse = await fetch(discoveryUrl)
      const discovery = await discoveryResponse.json()
      
      // 获取JWKS
      const jwksResponse = await fetch(discovery.jwks_uri)
      const jwks = await jwksResponse.json()
      
      // 验证ID Token
      // (这里简化了，实际需要验证签名)
      const { header, payload } = jwt.decode(token)
      
      // 验证issuer
      if (payload.iss !== env.OIDC_ISSUER) {
        return new Response('Invalid issuer', { status: 401 })
      }
      
      // 验证audience
      if (payload.aud !== env.CLIENT_ID) {
        return new Response('Invalid audience', { status: 401 })
      }
      
      // 验证过期
      if (payload.exp < Date.now() / 1000) {
        return new Response('Token expired', { status: 401 })
      }
      
      // 返回用户信息
      return new Response(JSON.stringify({
        sub: payload.sub,
        email: payload.email,
        name: payload.name
      }), {
        headers: { 'Content-Type': 'application/json' }
      })
    } catch (error) {
      return new Response('Authentication error', { status: 401 })
    }
  }
}
```

---

### 2.3 API密钥管理

```javascript
// Cloudflare Workers - API密钥验证
export default {
  async fetch(request, env) {
    const apiKey = request.headers.get('X-API-Key')
    
    if (!apiKey) {
      return new Response('API key required', { status: 401 })
    }
    
    // 从KV存储查询API密钥
    const keyData = await env.API_KEYS.get(apiKey, { type: 'json' })
    
    if (!keyData) {
      return new Response('Invalid API key', { status: 401 })
    }
    
    // 检查密钥状态
    if (keyData.status !== 'active') {
      return new Response('API key is disabled', { status: 401 })
    }
    
    // 检查过期时间
    if (keyData.expiresAt && new Date(keyData.expiresAt) < new Date()) {
      return new Response('API key expired', { status: 401 })
    }
    
    // 检查速率限制
    const rateLimitKey = `ratelimit:${apiKey}`
    const count = await env.API_KEYS.get(rateLimitKey)
    const currentCount = parseInt(count || '0')
    
    if (currentCount >= keyData.rateLimit) {
      return new Response('Rate limit exceeded', { 
        status: 429,
        headers: {
          'X-RateLimit-Limit': keyData.rateLimit.toString(),
          'X-RateLimit-Remaining': '0'
        }
      })
    }
    
    // 增加计数
    await env.API_KEYS.put(rateLimitKey, (currentCount + 1).toString(), {
      expirationTtl: 60  // 1分钟窗口
    })
    
    // 记录使用
    await logApiKeyUsage(apiKey, keyData.userId, request)
    
    // 继续处理请求
    return new Response(JSON.stringify({
      message: 'Success',
      userId: keyData.userId,
      remaining: keyData.rateLimit - currentCount - 1
    }), {
      headers: { 
        'Content-Type': 'application/json',
        'X-RateLimit-Remaining': (keyData.rateLimit - currentCount - 1).toString()
      }
    })
  }
}

async function logApiKeyUsage(apiKey, userId, request) {
  // 发送到日志服务
  console.log({
    apiKey: apiKey.substring(0, 8) + '...',
    userId: userId,
    path: new URL(request.url).pathname,
    timestamp: new Date().toISOString()
  })
}
```

**API密钥生成**:

```javascript
// 生成安全的API密钥
function generateApiKey() {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
}

// 存储API密钥
async function createApiKey(env, userId, options = {}) {
  const apiKey = generateApiKey()
  
  const keyData = {
    userId: userId,
    status: 'active',
    createdAt: new Date().toISOString(),
    expiresAt: options.expiresAt || null,
    rateLimit: options.rateLimit || 1000,
    scopes: options.scopes || ['read']
  }
  
  await env.API_KEYS.put(apiKey, JSON.stringify(keyData))
  
  return {
    apiKey: apiKey,
    ...keyData
  }
}
```

---

### 2.4 细粒度权限控制

**基于角色的访问控制 (RBAC)**:

```javascript
// AWS Lambda - RBAC
const roles = {
  admin: ['read', 'write', 'delete', 'manage_users'],
  editor: ['read', 'write'],
  viewer: ['read']
}

exports.handler = async (event) => {
    // 从JWT或context获取用户角色
    const userRole = event.requestContext.authorizer.role || 'viewer'
    const requiredPermission = getRequiredPermission(event.httpMethod, event.path)
    
    // 检查权限
    if (!hasPermission(userRole, requiredPermission)) {
        return {
            statusCode: 403,
            body: JSON.stringify({ error: 'Forbidden' })
        }
    }
    
    // 继续处理
    return handleRequest(event, userRole)
}

function hasPermission(role, permission) {
    const permissions = roles[role] || []
    return permissions.includes(permission)
}

function getRequiredPermission(method, path) {
    if (method === 'GET') return 'read'
    if (method === 'POST' || method === 'PUT') return 'write'
    if (method === 'DELETE') return 'delete'
    return 'read'
}

function handleRequest(event, role) {
    // 业务逻辑
    return {
        statusCode: 200,
        body: JSON.stringify({
            message: 'Success',
            role: role
        })
    }
}
```

**基于属性的访问控制 (ABAC)**:

```javascript
// Cloudflare Workers - ABAC
export default {
  async fetch(request, env, ctx) {
    const user = await getUserFromToken(request, env)
    const resource = getResource(request)
    
    // ABAC策略评估
    const decision = evaluatePolicy({
      user: {
        id: user.id,
        department: user.department,
        level: user.level
      },
      resource: {
        type: resource.type,
        owner: resource.owner,
        classification: resource.classification
      },
      action: request.method,
      environment: {
        time: new Date().getHours(),
        location: request.cf.country
      }
    })
    
    if (decision === 'deny') {
      return new Response('Forbidden', { status: 403 })
    }
    
    return handleRequest(request, user, resource)
  }
}

function evaluatePolicy(context) {
  // 规则1: 管理员可以访问所有资源
  if (context.user.level === 'admin') {
    return 'allow'
  }
  
  // 规则2: 用户可以访问自己部门的资源
  if (context.resource.owner === context.user.department) {
    return 'allow'
  }
  
  // 规则3: 公开资源任何人都可以读取
  if (context.resource.classification === 'public' && context.action === 'GET') {
    return 'allow'
  }
  
  // 规则4: 工作时间限制 (9-18点)
  if (context.environment.time < 9 || context.environment.time >= 18) {
    return 'deny'
  }
  
  // 规则5: 地理位置限制
  if (!['US', 'CA', 'GB'].includes(context.environment.location)) {
    return 'deny'
  }
  
  return 'deny'
}
```

---

## 3. 数据安全

### 3.1 数据加密

**传输加密**:

```yaml
HTTPS/TLS最佳实践:

1. 强制HTTPS:
   ✅ 重定向HTTP到HTTPS
   ✅ HSTS头
   ✅ Preload list

2. TLS配置:
   ✅ TLS 1.2+
   ✅ 强加密套件
   ✅ 禁用弱协议 (SSL, TLS 1.0/1.1)
   ✅ Forward Secrecy

3. 证书管理:
   ✅ 使用可信CA
   ✅ 定期更新证书
   ✅ 自动续期
   ✅ 证书固定 (可选)
```

```javascript
// Cloudflare Workers - 强制HTTPS
export default {
  async fetch(request) {
    const url = new URL(request.url)
    
    // 重定向HTTP到HTTPS
    if (url.protocol === 'http:') {
      url.protocol = 'https:'
      return Response.redirect(url.toString(), 301)
    }
    
    // 添加安全头
    const response = await fetch(request)
    const newResponse = new Response(response.body, response)
    
    // HSTS
    newResponse.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload')
    
    return newResponse
  }
}
```

**静态加密**:

```javascript
// AWS Lambda - 数据加密存储
const AWS = require('aws-sdk')
const kms = new AWS.KMS()
const s3 = new AWS.S3()

async function encryptAndStore(data, bucket, key) {
    // 使用KMS加密数据
    const encrypted = await kms.encrypt({
        KeyId: process.env.KMS_KEY_ID,
        Plaintext: JSON.stringify(data)
    }).promise()
    
    // 存储加密数据到S3
    await s3.putObject({
        Bucket: bucket,
        Key: key,
        Body: encrypted.CiphertextBlob,
        ServerSideEncryption: 'aws:kms',
        SSEKMSKeyId: process.env.KMS_KEY_ID
    }).promise()
}

async function retrieveAndDecrypt(bucket, key) {
    // 从S3读取
    const s3Object = await s3.getObject({
        Bucket: bucket,
        Key: key
    }).promise()
    
    // 使用KMS解密
    const decrypted = await kms.decrypt({
        CiphertextBlob: s3Object.Body
    }).promise()
    
    return JSON.parse(decrypted.Plaintext.toString())
}
```

---

### 3.2 密钥管理

**AWS KMS集成**:

```javascript
// Lambda - 密钥管理
const AWS = require('aws-sdk')
const kms = new AWS.KMS()

// 加密敏感配置
async function encryptConfig(plaintext) {
    const result = await kms.encrypt({
        KeyId: process.env.KMS_KEY_ID,
        Plaintext: plaintext
    }).promise()
    
    return result.CiphertextBlob.toString('base64')
}

// 解密配置
async function decryptConfig(ciphertext) {
    const result = await kms.decrypt({
        CiphertextBlob: Buffer.from(ciphertext, 'base64')
    }).promise()
    
    return result.Plaintext.toString()
}

// Lambda handler
exports.handler = async (event) => {
    // 解密数据库密码 (启动时缓存)
    if (!global.dbPassword) {
        global.dbPassword = await decryptConfig(process.env.ENCRYPTED_DB_PASSWORD)
    }
    
    // 使用解密后的密码
    const connection = await connectDatabase(global.dbPassword)
    // ...
}
```

**Cloudflare Workers Secrets**:

```bash
# 设置Secret
wrangler secret put DB_PASSWORD
# 输入密码

wrangler secret put API_KEY
# 输入API密钥

# 列出Secrets
wrangler secret list
```

```javascript
// Workers - 使用Secrets
export default {
  async fetch(request, env) {
    // env.DB_PASSWORD 和 env.API_KEY 已自动注入
    // 绝不会出现在代码或日志中
    
    const db = await connectToDatabase({
      host: env.DB_HOST,
      user: env.DB_USER,
      password: env.DB_PASSWORD  // Secret
    })
    
    const api = await callExternalAPI({
      key: env.API_KEY  // Secret
    })
    
    return new Response('Success')
  }
}
```

---

### 3.3 敏感数据处理

**数据脱敏**:

```javascript
// 敏感数据脱敏
function maskSensitiveData(data) {
  return {
    ...data,
    // 脱敏信用卡号
    creditCard: data.creditCard ? maskCreditCard(data.creditCard) : undefined,
    // 脱敏邮箱
    email: data.email ? maskEmail(data.email) : undefined,
    // 脱敏手机号
    phone: data.phone ? maskPhone(data.phone) : undefined,
    // 完全移除敏感字段
    password: undefined,
    ssn: undefined
  }
}

function maskCreditCard(card) {
  // 4111-1111-1111-1111 → 4111-****-****-1111
  return card.replace(/(\d{4})-\d{4}-\d{4}-(\d{4})/, '$1-****-****-$2')
}

function maskEmail(email) {
  // user@example.com → u***@example.com
  const [local, domain] = email.split('@')
  return `${local[0]}${'*'.repeat(local.length - 1)}@${domain}`
}

function maskPhone(phone) {
  // +1-555-1234 → +1-***-1234
  return phone.replace(/(\+\d+)-\d{3}-(\d{4})/, '$1-***-$2')
}

// 使用
exports.handler = async (event) => {
    const user = await getUser(event.userId)
    
    // 记录日志前脱敏
    console.log('User data:', maskSensitiveData(user))
    
    // 返回响应前脱敏
    return {
        statusCode: 200,
        body: JSON.stringify(maskSensitiveData(user))
    }
}
```

**PII (个人可识别信息) 处理**:

```javascript
// 检测和处理PII
const piiPatterns = {
  email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
  ssn: /\b\d{3}-\d{2}-\d{4}\b/g,
  creditCard: /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g,
  phone: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g
}

function removePII(text) {
  let cleaned = text
  
  for (const [type, pattern] of Object.entries(piiPatterns)) {
    cleaned = cleaned.replace(pattern, `[${type.toUpperCase()}_REDACTED]`)
  }
  
  return cleaned
}

// 安全日志记录
function secureLog(level, message, data = {}) {
  const logEntry = {
    level: level,
    message: removePII(message),
    data: maskSensitiveData(data),
    timestamp: new Date().toISOString()
  }
  
  console.log(JSON.stringify(logEntry))
}
```

---

## 4. 网络安全

### 4.1 DDoS防护

**Cloudflare DDoS防护**:

```javascript
// Cloudflare Workers - DDoS防护
export default {
  async fetch(request, env, ctx) {
    const clientIP = request.headers.get('CF-Connecting-IP')
    const country = request.cf.country
    
    // 1. 地理位置过滤
    const blockedCountries = ['XX', 'YY']
    if (blockedCountries.includes(country)) {
      return new Response('Forbidden', { status: 403 })
    }
    
    // 2. 速率限制 (IP级别)
    const rateLimitKey = `ratelimit:ip:${clientIP}`
    const count = await env.KV.get(rateLimitKey)
    const currentCount = parseInt(count || '0')
    
    if (currentCount >= 100) {  // 每分钟100请求
      return new Response('Too Many Requests', { 
        status: 429,
        headers: {
          'Retry-After': '60'
        }
      })
    }
    
    // 增加计数
    ctx.waitUntil(
      env.KV.put(rateLimitKey, (currentCount + 1).toString(), {
        expirationTtl: 60
      })
    )
    
    // 3. Challenge可疑请求
    const threatScore = request.cf.clientTrustScore || 0
    if (threatScore < 30) {
      // 返回Captcha challenge
      return new Response('Please complete the challenge', {
        status: 403,
        headers: {
          'CF-Challenge': 'true'
        }
      })
    }
    
    // 4. 检测异常User-Agent
    const userAgent = request.headers.get('User-Agent') || ''
    if (isSuspiciousUserAgent(userAgent)) {
      return new Response('Forbidden', { status: 403 })
    }
    
    return handleRequest(request)
  }
}

function isSuspiciousUserAgent(ua) {
  const suspiciousPatterns = [
    /bot/i,
    /crawler/i,
    /spider/i,
    /scraper/i
  ]
  
  return suspiciousPatterns.some(pattern => pattern.test(ua))
}
```

---

### 4.2 速率限制

**令牌桶算法**:

```javascript
// AWS Lambda - 速率限制 (令牌桶)
const AWS = require('aws-sdk')
const dynamodb = new AWS.DynamoDB.DocumentClient()

class TokenBucket {
  constructor(capacity, refillRate) {
    this.capacity = capacity
    this.refillRate = refillRate  // tokens per second
  }
  
  async tryConsume(key, tokens = 1) {
    const now = Date.now()
    
    // 获取当前状态
    const result = await dynamodb.get({
      TableName: 'RateLimits',
      Key: { key }
    }).promise()
    
    let bucket = result.Item || {
      key,
      tokens: this.capacity,
      lastRefill: now
    }
    
    // 计算应补充的令牌
    const elapsed = (now - bucket.lastRefill) / 1000
    const refill = Math.floor(elapsed * this.refillRate)
    bucket.tokens = Math.min(this.capacity, bucket.tokens + refill)
    bucket.lastRefill = now
    
    // 尝试消费
    if (bucket.tokens >= tokens) {
      bucket.tokens -= tokens
      
      // 更新状态
      await dynamodb.put({
        TableName: 'RateLimits',
        Item: bucket,
        ExpirationTtl: Math.floor(now / 1000) + 3600  // 1小时过期
      }).promise()
      
      return { allowed: true, remaining: bucket.tokens }
    }
    
    return { allowed: false, remaining: bucket.tokens }
  }
}

exports.handler = async (event) => {
    const userId = event.requestContext.authorizer.userId
    const bucket = new TokenBucket(100, 10)  // 100容量, 每秒10个令牌
    
    const result = await bucket.tryConsume(`user:${userId}`, 1)
    
    if (!result.allowed) {
        return {
            statusCode: 429,
            headers: {
                'X-RateLimit-Remaining': '0',
                'Retry-After': '1'
            },
            body: JSON.stringify({ error: 'Rate limit exceeded' })
        }
    }
    
    return {
        statusCode: 200,
        headers: {
            'X-RateLimit-Remaining': result.remaining.toString()
        },
        body: JSON.stringify({ message: 'Success' })
    }
}
```

**滑动窗口**:

```javascript
// Cloudflare Workers - 滑动窗口速率限制
export default {
  async fetch(request, env) {
    const userId = getUserId(request)
    const windowSize = 60  // 60秒窗口
    const maxRequests = 100
    
    const key = `ratelimit:${userId}`
    const now = Date.now()
    const windowStart = now - (windowSize * 1000)
    
    // 获取时间戳列表
    const timestamps = await env.KV.get(key, { type: 'json' }) || []
    
    // 过滤窗口外的请求
    const validTimestamps = timestamps.filter(ts => ts > windowStart)
    
    if (validTimestamps.length >= maxRequests) {
      const oldestTimestamp = Math.min(...validTimestamps)
      const retryAfter = Math.ceil((oldestTimestamp + windowSize * 1000 - now) / 1000)
      
      return new Response('Rate limit exceeded', {
        status: 429,
        headers: {
          'X-RateLimit-Limit': maxRequests.toString(),
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': new Date(oldestTimestamp + windowSize * 1000).toISOString(),
          'Retry-After': retryAfter.toString()
        }
      })
    }
    
    // 添加当前时间戳
    validTimestamps.push(now)
    
    // 存储更新后的列表
    await env.KV.put(key, JSON.stringify(validTimestamps), {
      expirationTtl: windowSize
    })
    
    return new Response('Success', {
      headers: {
        'X-RateLimit-Limit': maxRequests.toString(),
        'X-RateLimit-Remaining': (maxRequests - validTimestamps.length).toString()
      }
    })
  }
}
```

---

### 4.3 WAF规则

**AWS WAF集成**:

```json
{
  "Name": "ServerlessWAF",
  "Rules": [
    {
      "Name": "BlockSQLInjection",
      "Priority": 1,
      "Statement": {
        "SqliMatchStatement": {
          "FieldToMatch": {
            "AllQueryArguments": {}
          },
          "TextTransformations": [
            {
              "Priority": 0,
              "Type": "URL_DECODE"
            }
          ]
        }
      },
      "Action": {
        "Block": {}
      }
    },
    {
      "Name": "BlockXSS",
      "Priority": 2,
      "Statement": {
        "XssMatchStatement": {
          "FieldToMatch": {
            "Body": {}
          },
          "TextTransformations": [
            {
              "Priority": 0,
              "Type": "HTML_ENTITY_DECODE"
            }
          ]
        }
      },
      "Action": {
        "Block": {}
      }
    },
    {
      "Name": "RateLimitPerIP",
      "Priority": 3,
      "Statement": {
        "RateBasedStatement": {
          "Limit": 2000,
          "AggregateKeyType": "IP"
        }
      },
      "Action": {
        "Block": {}
      }
    }
  ]
}
```

**Cloudflare WAF规则**:

```javascript
// Cloudflare Workers - 自定义WAF规则
export default {
  async fetch(request) {
    const url = new URL(request.url)
    const body = await request.text()
    
    // 1. SQL注入检测
    const sqlPatterns = [
      /(\bunion\b.*\bselect\b)/i,
      /(\bor\b.*=.*)/i,
      /(;.*drop\s+table)/i,
      /(exec\s*\()/i
    ]
    
    if (sqlPatterns.some(pattern => pattern.test(url.search + body))) {
      return new Response('SQL injection detected', { status: 403 })
    }
    
    // 2. XSS检测
    const xssPatterns = [
      /<script[^>]*>.*<\/script>/gi,
      /javascript:/gi,
      /onerror\s*=/gi,
      /onclick\s*=/gi
    ]
    
    if (xssPatterns.some(pattern => pattern.test(body))) {
      return new Response('XSS detected', { status: 403 })
    }
    
    // 3. Path traversal检测
    if (/\.\.\//.test(url.pathname)) {
      return new Response('Path traversal detected', { status: 403 })
    }
    
    // 4. 请求大小限制
    if (body.length > 1024 * 1024) {  // 1MB
      return new Response('Request too large', { status: 413 })
    }
    
    return fetch(request)
  }
}
```

---

### 4.4 IP访问控制

```javascript
// Cloudflare Workers - IP白名单/黑名单
const WHITELIST = new Set([
  '203.0.113.0/24',
  '198.51.100.0/24'
])

const BLACKLIST = new Set([
  '192.0.2.1',
  '192.0.2.2'
])

export default {
  async fetch(request) {
    const clientIP = request.headers.get('CF-Connecting-IP')
    
    // 检查黑名单
    if (BLACKLIST.has(clientIP)) {
      return new Response('Forbidden', { status: 403 })
    }
    
    // 检查白名单 (如果启用)
    if (WHITELIST.size > 0 && !isInWhitelist(clientIP, WHITELIST)) {
      return new Response('Forbidden', { status: 403 })
    }
    
    return handleRequest(request)
  }
}

function isInWhitelist(ip, whitelist) {
  // 简化版本，实际需要CIDR匹配
  for (const cidr of whitelist) {
    if (matchCIDR(ip, cidr)) {
      return true
    }
  }
  return false
}

function matchCIDR(ip, cidr) {
  // CIDR匹配实现
  // (这里简化，实际需要使用IP库)
  return cidr.includes(ip)
}
```

---

## 5. 代码安全

### 5.1 依赖安全

**依赖扫描**:

```bash
# npm audit
npm audit

# 修复漏洞
npm audit fix

# 强制修复
npm audit fix --force

# 生成报告
npm audit --json > audit-report.json
```

```yaml
# GitHub Actions - 依赖扫描
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # 每周日

jobs:
  scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Snyk
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high
    
    - name: Run npm audit
      run: npm audit --audit-level=high
    
    - name: Run OWASP Dependency Check
      uses: dependency-check/Dependency-Check_Action@main
      with:
        project: 'my-serverless-app'
        path: '.'
        format: 'HTML'
```

---

### 5.2 安全编码

**输入验证**:

```javascript
// 输入验证示例
function validateInput(data) {
  const errors = []
  
  // 1. 类型检查
  if (typeof data.email !== 'string') {
    errors.push('Email must be a string')
  }
  
  // 2. 格式验证
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.push('Invalid email format')
  }
  
  // 3. 长度限制
  if (data.name && data.name.length > 100) {
    errors.push('Name too long')
  }
  
  // 4. 白名单验证
  const allowedRoles = ['user', 'admin', 'editor']
  if (data.role && !allowedRoles.includes(data.role)) {
    errors.push('Invalid role')
  }
  
  // 5. 数值范围
  if (data.age && (data.age < 0 || data.age > 150)) {
    errors.push('Invalid age')
  }
  
  return {
    valid: errors.length === 0,
    errors: errors
  }
}

exports.handler = async (event) => {
    const data = JSON.parse(event.body)
    const validation = validateInput(data)
    
    if (!validation.valid) {
        return {
            statusCode: 400,
            body: JSON.stringify({ errors: validation.errors })
        }
    }
    
    // 继续处理
}
```

**SQL注入防护**:

```javascript
// 使用参数化查询
const mysql = require('mysql2/promise')

async function getUserByEmail(email) {
  const connection = await mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
  })
  
  // ✅ 安全：参数化查询
  const [rows] = await connection.execute(
    'SELECT * FROM users WHERE email = ?',
    [email]
  )
  
  // ❌ 危险：字符串拼接
  // const [rows] = await connection.execute(
  //   `SELECT * FROM users WHERE email = '${email}'`
  // )
  
  await connection.end()
  return rows[0]
}
```

---

### 5.3 Secrets管理

**AWS Secrets Manager**:

```javascript
// Lambda - Secrets Manager
const AWS = require('aws-sdk')
const secretsManager = new AWS.SecretsManager()

// 缓存secrets
let cachedSecrets = null
let cacheExpiry = null

async function getSecrets() {
  const now = Date.now()
  
  // 检查缓存
  if (cachedSecrets && cacheExpiry && now < cacheExpiry) {
    return cachedSecrets
  }
  
  // 从Secrets Manager获取
  const result = await secretsManager.getSecretValue({
    SecretId: process.env.SECRET_NAME
  }).promise()
  
  cachedSecrets = JSON.parse(result.SecretString)
  cacheExpiry = now + (5 * 60 * 1000)  // 缓存5分钟
  
  return cachedSecrets
}

exports.handler = async (event) => {
    const secrets = await getSecrets()
    
    // 使用secrets
    const apiKey = secrets.API_KEY
    const dbPassword = secrets.DB_PASSWORD
    
    // ...
}
```

---

### 5.4 代码审计

**SAST工具**:

```yaml
# .github/workflows/sast.yml
name: SAST Scan

on: [push, pull_request]

jobs:
  sast:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: SonarCloud Scan
      uses: SonarSource/sonarcloud-github-action@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    
    - name: ESLint Security
      run: |
        npm install
        npm run lint:security
    
    - name: Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/security-audit
          p/secrets
          p/owasp-top-ten
```

---

## 6. 合规性

### 6.1 GDPR合规

```yaml
GDPR要求:

1. 数据最小化:
   ✅ 只收集必要数据
   ✅ 限制数据保留期
   ✅ 定期删除过期数据

2. 用户同意:
   ✅ 明确同意机制
   ✅ 记录同意历史
   ✅ 撤销同意能力

3. 数据访问权:
   ✅ 用户可查看数据
   ✅ 数据可导出
   ✅ 机器可读格式

4. 数据删除权:
   ✅ 删除个人数据
   ✅ 匿名化处理
   ✅ 级联删除

5. 数据可移植:
   ✅ 标准格式导出
   ✅ API支持

6. 隐私设计:
   ✅ 默认隐私保护
   ✅ 数据加密
   ✅ 访问控制

7. 数据泄露通知:
   ✅ 72小时通知
   ✅ 事件记录
   ✅ 影响评估
```

```javascript
// GDPR合规示例
exports.handler = async (event) => {
    const action = event.path
    const userId = event.userId
    
    switch (action) {
        // 1. 数据访问请求
        case '/gdpr/access':
            const userData = await getUserData(userId)
            return {
                statusCode: 200,
                body: JSON.stringify({
                    user: maskSensitiveData(userData),
                    exportDate: new Date().toISOString()
                })
            }
        
        // 2. 数据导出请求
        case '/gdpr/export':
            const exportData = await exportUserData(userId)
            // 生成可下载链接
            const downloadUrl = await generateDownloadLink(exportData)
            return {
                statusCode: 200,
                body: JSON.stringify({ downloadUrl })
            }
        
        // 3. 数据删除请求
        case '/gdpr/delete':
            await deleteUserData(userId)
            await logDeletion(userId, 'GDPR request')
            return {
                statusCode: 200,
                body: JSON.stringify({ message: 'Data deleted' })
            }
        
        // 4. 同意管理
        case '/gdpr/consent':
            const consent = await getConsent(userId)
            return {
                statusCode: 200,
                body: JSON.stringify(consent)
            }
    }
}

async function deleteUserData(userId) {
    // 删除所有个人数据
    await Promise.all([
        deleteFromDatabase(userId),
        deleteFromS3(userId),
        deleteFromCache(userId),
        anonymizeAnalytics(userId)
    ])
}
```

---

### 6.2 HIPAA合规

```yaml
HIPAA要求 (医疗数据):

1. 访问控制:
   ✅ 唯一用户ID
   ✅ 紧急访问程序
   ✅ 自动登出
   ✅ 加密和解密

2. 审计控制:
   ✅ 硬件/软件/程序审计
   ✅ 记录访问尝试
   ✅ 检查活动日志

3. 完整性控制:
   ✅ 防止不当修改
   ✅ 数据完整性验证

4. 传输安全:
   ✅ 数据加密传输
   ✅ 端到端加密

5. 身份验证:
   ✅ 验证访问者身份
   ✅ 强密码策略
```

```javascript
// HIPAA合规日志
function logPHIAccess(userId, resourceId, action) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    userId: userId,
    resourceType: 'PHI',  // Protected Health Information
    resourceId: hashResourceId(resourceId),  // 不记录实际ID
    action: action,
    ipAddress: hashIPAddress(getClientIP()),
    userAgent: getUserAgent(),
    accessGranted: true
  }
  
  // 发送到SIEM
  sendToSIEM(logEntry)
  
  // 存储到审计日志 (不可变存储)
  storeAuditLog(logEntry)
}
```

---

### 6.3 SOC 2/PCI DSS

```yaml
SOC 2 Type II:

1. Security (安全):
   ✅ 访问控制
   ✅ 网络安全
   ✅ 系统监控

2. Availability (可用性):
   ✅ 性能监控
   ✅ 灾难恢复
   ✅ 备份策略

3. Processing Integrity (处理完整性):
   ✅ 数据验证
   ✅ 错误处理
   ✅ 质量保证

4. Confidentiality (机密性):
   ✅ 数据加密
   ✅ 访问控制
   ✅ 数据分类

5. Privacy (隐私):
   ✅ 数据收集通知
   ✅ 用户同意
   ✅ 数据保留政策

PCI DSS (支付卡):

1. 网络安全:
   ✅ 防火墙配置
   ✅ 供应商默认密码更改

2. 保护持卡人数据:
   ✅ 存储数据保护
   ✅ 传输加密

3. 漏洞管理:
   ✅ 防病毒软件
   ✅ 安全系统开发

4. 访问控制:
   ✅ 业务需求访问
   ✅ 唯一ID分配
   ✅ 物理访问限制

5. 监控测试:
   ✅ 跟踪监控访问
   ✅ 定期安全测试

6. 安全策略:
   ✅ 信息安全政策
```

---

## 7. 安全监控

### 7.1 审计日志

```javascript
// AWS Lambda - 结构化审计日志
const winston = require('winston')
const CloudWatchTransport = require('winston-cloudwatch')

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new CloudWatchTransport({
      logGroupName: '/aws/lambda/audit',
      logStreamName: process.env.AWS_LAMBDA_FUNCTION_NAME
    })
  ]
})

function auditLog(event) {
  logger.info('audit', {
    eventType: event.type,
    userId: event.userId,
    resourceId: event.resourceId,
    action: event.action,
    result: event.result,
    ipAddress: event.ipAddress,
    userAgent: event.userAgent,
    timestamp: new Date().toISOString(),
    requestId: event.requestId
  })
}

exports.handler = async (event) => {
    const requestId = event.requestContext.requestId
    const userId = event.requestContext.authorizer.userId
    
    // 记录访问
    auditLog({
        type: 'API_ACCESS',
        userId: userId,
        resourceId: event.pathParameters.id,
        action: event.httpMethod,
        result: 'SUCCESS',
        ipAddress: event.requestContext.identity.sourceIp,
        userAgent: event.requestContext.identity.userAgent,
        requestId: requestId
    })
    
    // 处理请求
    // ...
}
```

---

### 7.2 异常检测

```javascript
// Cloudflare Workers - 异常行为检测
export default {
  async fetch(request, env, ctx) {
    const userId = getUserId(request)
    const behavior = await analyzeBehavior(userId, request, env)
    
    if (behavior.anomalyScore > 0.8) {
      // 发送告警
      ctx.waitUntil(sendAlert({
        type: 'ANOMALY_DETECTED',
        userId: userId,
        score: behavior.anomalyScore,
        indicators: behavior.indicators,
        request: {
          path: new URL(request.url).pathname,
          method: request.method,
          ip: request.headers.get('CF-Connecting-IP')
        }
      }))
      
      // 要求额外验证
      return new Response('Additional verification required', {
        status: 403,
        headers: {
          'X-Verification-Required': 'true'
        }
      })
    }
    
    return handleRequest(request)
  }
}

async function analyzeBehavior(userId, request, env) {
  const indicators = []
  let anomalyScore = 0
  
  // 1. 访问频率异常
  const recentRequests = await getRecentRequests(userId, env)
  if (recentRequests.length > 100) {  // 1分钟内超过100请求
    indicators.push('HIGH_FREQUENCY')
    anomalyScore += 0.3
  }
  
  // 2. 异常时间访问
  const hour = new Date().getHours()
  if (hour >= 2 && hour <= 5) {  // 凌晨2-5点
    indicators.push('UNUSUAL_TIME')
    anomalyScore += 0.2
  }
  
  // 3. 地理位置变化
  const lastLocation = await getLastLocation(userId, env)
  const currentLocation = request.cf.country
  if (lastLocation && lastLocation !== currentLocation) {
    indicators.push('LOCATION_CHANGE')
    anomalyScore += 0.3
  }
  
  // 4. 新设备/浏览器
  const userAgent = request.headers.get('User-Agent')
  const knownDevices = await getKnownDevices(userId, env)
  if (!knownDevices.includes(hashUserAgent(userAgent))) {
    indicators.push('NEW_DEVICE')
    anomalyScore += 0.2
  }
  
  return {
    anomalyScore: Math.min(1, anomalyScore),
    indicators: indicators
  }
}
```

---

### 7.3 安全事件响应

```javascript
// 安全事件响应框架
class SecurityIncidentResponder {
  async handleIncident(incident) {
    // 1. 分类
    const severity = this.classifyIncident(incident)
    
    // 2. 遏制
    if (severity >= 'HIGH') {
      await this.containIncident(incident)
    }
    
    // 3. 通知
    await this.notifyStakeholders(incident, severity)
    
    // 4. 记录
    await this.logIncident(incident, severity)
    
    // 5. 分析
    await this.analyzeIncident(incident)
    
    // 6. 恢复
    await this.recoverFromIncident(incident)
  }
  
  classifyIncident(incident) {
    if (incident.type === 'DATA_BREACH') return 'CRITICAL'
    if (incident.type === 'UNAUTHORIZED_ACCESS') return 'HIGH'
    if (incident.type === 'SUSPICIOUS_ACTIVITY') return 'MEDIUM'
    return 'LOW'
  }
  
  async containIncident(incident) {
    // 立即行动
    if (incident.userId) {
      await this.suspendUser(incident.userId)
    }
    
    if (incident.ipAddress) {
      await this.blockIP(incident.ipAddress)
    }
    
    if (incident.apiKey) {
      await this.revokeAPIKey(incident.apiKey)
    }
  }
  
  async notifyStakeholders(incident, severity) {
    const notifications = []
    
    // 安全团队
    notifications.push(
      this.sendEmail({
        to: 'security@example.com',
        subject: `[${severity}] Security Incident Detected`,
        body: JSON.stringify(incident, null, 2)
      })
    )
    
    // 如果是CRITICAL，通知管理层
    if (severity === 'CRITICAL') {
      notifications.push(
        this.sendEmail({
          to: 'management@example.com',
          subject: `[CRITICAL] Security Incident`,
          body: `Critical security incident detected. Details: ${incident.type}`
        })
      )
      
      // PagerDuty告警
      notifications.push(
        this.sendPagerDutyAlert(incident)
      )
    }
    
    await Promise.all(notifications)
  }
}
```

---

## 8. 总结

```yaml
本章要点:
  ✅ Serverless安全威胁 (OWASP Top 10)
  ✅ 认证授权 (JWT/OAuth/API密钥/RBAC/ABAC)
  ✅ 数据安全 (加密/密钥管理/敏感数据处理)
  ✅ 网络安全 (DDoS/速率限制/WAF/IP控制)
  ✅ 代码安全 (依赖扫描/安全编码/Secrets/审计)
  ✅ 合规性 (GDPR/HIPAA/SOC 2/PCI DSS)
  ✅ 安全监控 (审计日志/异常检测/事件响应)

Serverless安全最佳实践:
  ⭐ 最小权限原则
  ⭐ 纵深防御
  ⭐ 安全左移
  ⭐ 持续监控
  ⭐ 事件响应计划

关键防护措施:
  ✅ 强认证 (JWT/OAuth 2.0)
  ✅ 细粒度授权 (RBAC/ABAC)
  ✅ 数据加密 (传输+静态)
  ✅ 速率限制
  ✅ 输入验证
  ✅ 依赖扫描
  ✅ 审计日志
  ✅ 异常检测

合规要求:
  ✅ GDPR (数据保护)
  ✅ HIPAA (医疗数据)
  ✅ SOC 2 (服务组织控制)
  ✅ PCI DSS (支付卡)

责任共担:
  云服务商: 基础设施安全
  客户: 应用和数据安全
```

---

**下一章预告**:

**06 - Serverless性能优化**:

- 冷启动优化
- 内存和CPU优化
- 网络优化
- 成本优化
- 监控与profiling

---

**完成日期**: 2025-10-19  
**版本**: v1.0  
**作者**: 云原生专家团队

**Tags**: `#ServerlessSecurity` `#JWT` `#OAuth` `#GDPR` `#DDoS` `#WAF` `#Compliance`
