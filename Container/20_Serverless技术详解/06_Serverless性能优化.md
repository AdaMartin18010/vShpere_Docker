# 06 - Serverless性能优化

**作者**: 云原生专家团队
**创建日期**: 2025-10-19
**最后更新**: 2025-10-19
**版本**: v1.0

---

## 📋 本章导航

- [06 - Serverless性能优化](#06---serverless性能优化)
  - [📋 本章导航](#-本章导航)
  - [1. 性能优化概述](#1-性能优化概述)
    - [1.1 性能指标](#11-性能指标)
    - [1.2 性能瓶颈识别](#12-性能瓶颈识别)
  - [2. 冷启动优化](#2-冷启动优化)
    - [2.1 冷启动原理](#21-冷启动原理)
    - [2.2 预热策略](#22-预热策略)
    - [2.3 Provisioned Concurrency](#23-provisioned-concurrency)
    - [2.4 代码优化](#24-代码优化)
  - [3. 内存优化](#3-内存优化)
    - [3.1 内存分配策略](#31-内存分配策略)
    - [3.2 内存泄漏检测](#32-内存泄漏检测)
    - [3.3 缓存优化](#33-缓存优化)
  - [4. CPU优化](#4-cpu优化)
    - [4.1 计算优化](#41-计算优化)
    - [4.2 并发处理](#42-并发处理)
  - [5. 网络优化](#5-网络优化)
    - [5.1 连接复用](#51-连接复用)
    - [5.2 HTTP优化](#52-http优化)
    - [5.3 区域就近](#53-区域就近)
  - [6. 数据库优化](#6-数据库优化)
    - [6.1 连接池管理](#61-连接池管理)
    - [6.2 查询优化](#62-查询优化)
    - [6.3 缓存策略](#63-缓存策略)
  - [7. 成本优化](#7-成本优化)
    - [7.1 执行时间优化](#71-执行时间优化)
    - [7.2 内存配置优化](#72-内存配置优化)
    - [7.3 架构优化](#73-架构优化)
  - [8. 监控与Profiling](#8-监控与profiling)
    - [8.1 性能监控](#81-性能监控)
    - [8.2 分布式追踪](#82-分布式追踪)
    - [8.3 Profiling工具](#83-profiling工具)
  - [9. 总结](#9-总结)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 1. 性能优化概述

### 1.1 性能指标

```yaml
关键性能指标 (KPI):

1. 冷启动时间 (Cold Start):
   定义: 函数首次调用或闲置后重新激活的时间
   目标:
     - JavaScript/Python: < 500ms
     - Go/Java: < 2s
     - .NET: < 3s
   影响因素:
     - 运行时类型
     - 代码包大小
     - 依赖数量
     - VPC配置

2. 热启动时间 (Warm Start):
   定义: 复用现有实例的调用时间
   目标: < 100ms
   影响因素:
     - 业务逻辑复杂度
     - 外部调用
     - 数据处理量

3. 执行时间 (Duration):
   定义: 函数实际执行时间
   目标: 根据业务场景
     - 简单API: < 100ms
     - 数据处理: < 1s
     - 批处理: < 30s
   影响因素:
     - 算法效率
     - I/O操作
     - 计算复杂度

4. 吞吐量 (Throughput):
   定义: 单位时间处理请求数
   目标: 根据业务需求
   影响因素:
     - 并发限制
     - 资源配置
     - 代码效率

5. 错误率 (Error Rate):
   定义: 失败请求占比
   目标: < 0.1%
   类型:
     - 4xx客户端错误
     - 5xx服务端错误
     - 超时错误

6. P99延迟 (P99 Latency):
   定义: 99%请求的响应时间
   目标: < 500ms
   意义: 保障大部分用户体验

7. 内存使用 (Memory Usage):
   定义: 函数运行时内存消耗
   目标: < 配置值的80%
   影响: 成本和稳定性

8. 并发数 (Concurrency):
   定义: 同时运行的函数实例数
   目标: 满足业务需求
   限制:
     - 账户级别
     - 函数级别
     - 区域级别
```

---

### 1.2 性能瓶颈识别

```yaml
常见性能瓶颈:

1. 冷启动瓶颈:
   症状:
     - 首次调用慢
     - 间歇性延迟高
   原因:
     - 大型代码包
     - 多层依赖
     - VPC配置
   识别:
     - 查看InitDuration指标
     - 分析冷启动比例

2. 内存瓶颈:
   症状:
     - OOM错误
     - GC频繁
     - 性能下降
   原因:
     - 内存泄漏
     - 配置不足
     - 数据缓存过大
   识别:
     - 监控MaxMemoryUsed
     - 内存使用率趋势

3. CPU瓶颈:
   症状:
     - 执行时间长
     - 超时
   原因:
     - 计算密集
     - 算法低效
     - 串行处理
   识别:
     - Duration vs 内存配置
     - CPU利用率

4. 网络瓶颈:
   症状:
     - 延迟高
     - 超时频繁
   原因:
     - 外部API慢
     - 无连接复用
     - 跨区域调用
   识别:
     - 分布式追踪
     - 网络调用时长

5. 数据库瓶颈:
   症状:
     - 查询慢
     - 连接超时
   原因:
     - 无连接池
     - 查询未优化
     - 索引缺失
   识别:
     - 数据库慢查询日志
     - 连接数监控

6. 串行化瓶颈:
   症状:
     - 总时长 = 各步骤之和
   原因:
     - 无并发处理
     - 顺序依赖
   识别:
     - 时间线分析
     - 调用链追踪
```

---

## 2. 冷启动优化

### 2.1 冷启动原理

```yaml
冷启动过程 (AWS Lambda):

1. 下载代码 (Download Code):
   - 从S3下载部署包
   - 时间: 100-500ms (取决于大小)

2. 创建执行环境 (Create Execution Environment):
   - 分配计算资源
   - 启动运行时
   - 时间: 100-300ms

3. 初始化运行时 (Initialize Runtime):
   - 加载运行时
   - 初始化语言环境
   - 时间: 因语言而异
     * Node.js/Python: 10-50ms
     * Java: 500-2000ms
     * .NET: 1000-3000ms

4. 初始化代码 (Initialize Code):
   - 加载依赖
   - 执行初始化代码
   - 建立数据库连接
   - 时间: 因代码而异

5. 调用Handler:
   - 执行业务逻辑
   - 时间: 取决于代码

总冷启动时间:
  Node.js/Python: 300-1000ms
  Go: 500-1500ms
  Java: 2000-5000ms
  .NET: 3000-6000ms
```

**冷启动示例**:

```javascript
// AWS Lambda冷启动分析
const AWS = require('aws-sdk')
const mysql = require('mysql2/promise')

// ❌ 问题: 每次调用都初始化
exports.handler_bad = async (event) => {
    console.log('Init Start')  // 冷启动时执行

    const s3 = new AWS.S3()
    const connection = await mysql.createConnection({
        host: process.env.DB_HOST,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD
    })

    console.log('Init End')

    // 业务逻辑
    const result = await connection.query('SELECT * FROM users')
    return { statusCode: 200, body: JSON.stringify(result) }
}

// ✅ 优化: 全局初始化，复用实例
const s3 = new AWS.S3()  // 全局变量
let connection = null

exports.handler_good = async (event) => {
    // 只在冷启动时初始化
    if (!connection) {
        console.log('Cold Start: Creating DB connection')
        connection = await mysql.createConnection({
            host: process.env.DB_HOST,
            user: process.env.DB_USER,
            password: process.env.DB_PASSWORD
        })
    }

    // 业务逻辑 (热启动快速执行)
    const result = await connection.query('SELECT * FROM users')
    return { statusCode: 200, body: JSON.stringify(result) }
}
```

---

### 2.2 预热策略

**定时预热**:

```yaml
# serverless.yml (Serverless Framework)
functions:
  myFunction:
    handler: handler.main
    events:
      - http:
          path: /api
          method: get
      # 预热事件: 每5分钟触发一次
      - schedule:
          rate: rate(5 minutes)
          input:
            warmup: true
```

```javascript
// handler.js
exports.main = async (event) => {
    // 检测预热请求
    if (event.warmup) {
        console.log('Warmup invocation')
        return { statusCode: 200, body: 'Warmed up!' }
    }

    // 正常业务逻辑
    return handleRequest(event)
}
```

**插件预热 (serverless-plugin-warmup)**:

```yaml
# serverless.yml
plugins:
  - serverless-plugin-warmup

custom:
  warmup:
    default:
      enabled: true
      events:
        - schedule: 'rate(5 minutes)'
      concurrency: 5  # 预热5个实例
      prewarm: true

functions:
  myFunction:
    handler: handler.main
    warmup:
      default:
        enabled: true
```

```javascript
// handler.js
exports.main = async (event, context) => {
    // 插件自动注入warmup字段
    if (event.source === 'serverless-plugin-warmup') {
        return 'Lambda warmed'
    }

    return handleRequest(event, context)
}
```

---

### 2.3 Provisioned Concurrency

**AWS Lambda Provisioned Concurrency**:

```bash
# AWS CLI - 配置Provisioned Concurrency
aws lambda put-provisioned-concurrency-config \
  --function-name my-function \
  --provisioned-concurrent-executions 5 \
  --qualifier prod

# 查看配置
aws lambda get-provisioned-concurrency-config \
  --function-name my-function \
  --qualifier prod
```

```yaml
# SAM模板
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: nodejs18.x
      AutoPublishAlias: live
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 5
```

**Auto Scaling**:

```yaml
# CloudFormation
Resources:
  # Auto Scaling Target
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      ServiceNamespace: lambda
      ResourceId: function:my-function:prod
      ScalableDimension: lambda:function:ProvisionedConcurrentExecutions
      MinCapacity: 1
      MaxCapacity: 100

  # Auto Scaling Policy
  ScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: TargetTrackingPolicy
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 0.70  # 70%利用率
        PredefinedMetricSpecification:
          PredefinedMetricType: LambdaProvisionedConcurrencyUtilization
```

---

### 2.4 代码优化

**减小包大小**:

```bash
# 1. 使用webpack打包
npm install --save-dev webpack webpack-cli

# webpack.config.js
module.exports = {
  entry: './src/index.js',
  target: 'node',
  mode: 'production',
  output: {
    filename: 'index.js',
    libraryTarget: 'commonjs2'
  },
  externals: {
    'aws-sdk': 'aws-sdk'  // AWS SDK已预装
  },
  optimization: {
    minimize: true
  }
}

# 打包
npx webpack

# 2. 删除dev依赖
npm prune --production

# 3. 排除不必要的文件
# .serverlessignore
node_modules/aws-sdk/**
*.md
.git/**
tests/**
*.test.js
```

**Tree Shaking (移除未使用代码)**:

```javascript
// ❌ 导入整个库
const _ = require('lodash')
_.map(array, fn)

// ✅ 只导入需要的函数
const map = require('lodash/map')
map(array, fn)

// ✅ ES6模块 (webpack会tree shake)
import { map } from 'lodash-es'
map(array, fn)
```

**延迟加载**:

```javascript
// ❌ 在顶部导入所有依赖
const heavy1 = require('./heavy-module-1')
const heavy2 = require('./heavy-module-2')
const heavy3 = require('./heavy-module-3')

exports.handler = async (event) => {
    if (event.type === 'type1') {
        return heavy1.process(event)
    }
    // heavy2和heavy3浪费加载时间
}

// ✅ 延迟加载
exports.handler = async (event) => {
    if (event.type === 'type1') {
        const heavy1 = require('./heavy-module-1')
        return heavy1.process(event)
    } else if (event.type === 'type2') {
        const heavy2 = require('./heavy-module-2')
        return heavy2.process(event)
    }
}
```

---

## 3. 内存优化

### 3.1 内存分配策略

```yaml
内存与CPU关系 (AWS Lambda):
  - Lambda内存 = CPU成正比
  - 1792MB内存 = 1 vCPU
  - 3584MB内存 = 2 vCPU
  - 更多内存 = 更快CPU = 更快执行

内存配置策略:
  1. 测试不同内存配置
  2. 找到性价比最优点
  3. 考虑成本 vs 性能

示例:
  128MB: 执行10s = $0.0000002083
  1024MB: 执行2s = $0.0000003334
  结论: 1024MB更快更便宜!
```

**性能测试脚本**:

```bash
# Lambda Power Tuning工具
# GitHub: alexcasalboni/aws-lambda-power-tuning

# 部署工具
aws cloudformation deploy \
  --template-file template.yml \
  --stack-name lambda-power-tuning \
  --capabilities CAPABILITY_IAM

# 执行测试
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:... \
  --input '{
    "lambdaARN": "arn:aws:lambda:region:account:function:my-function",
    "powerValues": [128, 256, 512, 1024, 1536, 3008],
    "num": 10,
    "payload": {}
  }'

# 结果: 可视化图表显示最优配置
```

---

### 3.2 内存泄漏检测

```javascript
// Node.js内存泄漏示例

// ❌ 问题: 全局变量累积
const cache = {}  // 永不清理
exports.handler = async (event) => {
    const key = event.id
    cache[key] = event.data  // 内存泄漏!
    return { success: true }
}

// ✅ 解决: 使用LRU缓存
const LRU = require('lru-cache')
const cache = new LRU({
    max: 500,  // 最多500项
    maxAge: 1000 * 60 * 5  // 5分钟过期
})

exports.handler = async (event) => {
    const key = event.id
    cache.set(key, event.data)  // 自动淘汰旧数据
    return { success: true }
}
```

**内存监控**:

```javascript
// 监控内存使用
exports.handler = async (event, context) => {
    const used = process.memoryUsage()

    console.log(JSON.stringify({
        rss: Math.round(used.rss / 1024 / 1024) + 'MB',  // 常驻集大小
        heapTotal: Math.round(used.heapTotal / 1024 / 1024) + 'MB',
        heapUsed: Math.round(used.heapUsed / 1024 / 1024) + 'MB',
        external: Math.round(used.external / 1024 / 1024) + 'MB'
    }))

    // 业务逻辑
    const result = await handleRequest(event)

    // 检查剩余内存
    const remaining = context.memoryLimitInMB - Math.round(used.heapUsed / 1024 / 1024)
    if (remaining < 50) {
        console.warn('Low memory warning:', remaining, 'MB remaining')
    }

    return result
}
```

---

### 3.3 缓存优化

**全局缓存**:

```javascript
// 缓存外部配置
let config = null
let configExpiry = null

async function getConfig() {
    const now = Date.now()

    // 检查缓存
    if (config && configExpiry && now < configExpiry) {
        return config
    }

    // 从Parameter Store获取
    const ssm = new AWS.SSM()
    const result = await ssm.getParameter({
        Name: '/myapp/config',
        WithDecryption: true
    }).promise()

    config = JSON.parse(result.Parameter.Value)
    configExpiry = now + (5 * 60 * 1000)  // 缓存5分钟

    return config
}

exports.handler = async (event) => {
    const cfg = await getConfig()
    // 使用配置
}
```

**连接缓存**:

```javascript
// 缓存数据库连接
const mysql = require('mysql2/promise')

let connection = null

async function getConnection() {
    if (connection && connection.connection._closing === false) {
        return connection
    }

    connection = await mysql.createConnection({
        host: process.env.DB_HOST,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        database: process.env.DB_NAME
    })

    return connection
}

exports.handler = async (event) => {
    const conn = await getConnection()
    const [rows] = await conn.query('SELECT * FROM users')
    return { statusCode: 200, body: JSON.stringify(rows) }
}
```

---

## 4. CPU优化

### 4.1 计算优化

**算法优化**:

```javascript
// ❌ O(n²) - 嵌套循环
function findPairs_slow(arr, target) {
    const pairs = []
    for (let i = 0; i < arr.length; i++) {
        for (let j = i + 1; j < arr.length; j++) {
            if (arr[i] + arr[j] === target) {
                pairs.push([arr[i], arr[j]])
            }
        }
    }
    return pairs
}

// ✅ O(n) - 哈希表
function findPairs_fast(arr, target) {
    const pairs = []
    const seen = new Set()

    for (const num of arr) {
        const complement = target - num
        if (seen.has(complement)) {
            pairs.push([complement, num])
        }
        seen.add(num)
    }

    return pairs
}

// 性能对比 (1000个元素)
// slow: ~10ms
// fast: ~1ms (10x faster!)
```

**避免阻塞操作**:

```javascript
// ❌ 同步文件读取 (阻塞)
const fs = require('fs')
exports.handler = (event) => {
    const data = fs.readFileSync('/tmp/large-file.json', 'utf8')  // 阻塞!
    return processData(data)
}

// ✅ 异步读取 (非阻塞)
const fs = require('fs').promises
exports.handler = async (event) => {
    const data = await fs.readFile('/tmp/large-file.json', 'utf8')  // 非阻塞
    return processData(data)
}
```

---

### 4.2 并发处理

**Promise.all并行**:

```javascript
// ❌ 串行处理 (慢)
exports.handler = async (event) => {
    const user = await fetchUser(event.userId)        // 100ms
    const posts = await fetchPosts(event.userId)      // 150ms
    const comments = await fetchComments(event.userId) // 120ms
    // 总时间: 100 + 150 + 120 = 370ms

    return { user, posts, comments }
}

// ✅ 并行处理 (快)
exports.handler = async (event) => {
    const [user, posts, comments] = await Promise.all([
        fetchUser(event.userId),        // 并行
        fetchPosts(event.userId),       // 并行
        fetchComments(event.userId)     // 并行
    ])
    // 总时间: max(100, 150, 120) = 150ms (2.5x faster!)

    return { user, posts, comments }
}
```

**批处理**:

```javascript
// 批量处理记录
exports.handler = async (event) => {
    const records = event.Records  // SQS/Kinesis批次

    // ❌ 逐个处理
    for (const record of records) {
        await processRecord(record)  // 串行，慢
    }

    // ✅ 批量并行处理
    await Promise.all(
        records.map(record => processRecord(record))
    )

    // ✅ 限制并发数 (避免压垮下游)
    const pLimit = require('p-limit')
    const limit = pLimit(10)  // 最多10个并发

    await Promise.all(
        records.map(record => limit(() => processRecord(record)))
    )
}
```

---

## 5. 网络优化

### 5.1 连接复用

**HTTP Keep-Alive**:

```javascript
// ❌ 每次创建新连接
const https = require('https')
exports.handler = async (event) => {
    return new Promise((resolve, reject) => {
        https.get('https://api.example.com/data', (res) => {
            let data = ''
            res.on('data', chunk => data += chunk)
            res.on('end', () => resolve(data))
        }).on('error', reject)
    })
    // 每次调用都建立新TCP连接 (慢!)
}

// ✅ 复用连接
const https = require('https')
const agent = new https.Agent({
    keepAlive: true,
    maxSockets: 50,
    maxFreeSockets: 10,
    timeout: 60000,
    keepAliveMsecs: 30000
})

exports.handler = async (event) => {
    return new Promise((resolve, reject) => {
        https.get('https://api.example.com/data', { agent }, (res) => {
            let data = ''
            res.on('data', chunk => data += chunk)
            res.on('end', () => resolve(data))
        }).on('error', reject)
    })
    // 复用连接 (快!)
}
```

**AWS SDK连接池**:

```javascript
// AWS SDK v3 - 自动连接池
const { DynamoDBClient } = require('@aws-sdk/client-dynamodb')
const { DynamoDBDocumentClient, GetCommand } = require('@aws-sdk/lib-dynamodb')

// 全局客户端 (复用连接)
const client = new DynamoDBClient({
    region: 'us-east-1',
    maxAttempts: 3,
    requestHandler: {
        connectionTimeout: 3000,
        socketTimeout: 3000,
        httpOptions: {
            agent: new https.Agent({
                keepAlive: true,
                maxSockets: 50
            })
        }
    }
})

const docClient = DynamoDBDocumentClient.from(client)

exports.handler = async (event) => {
    const result = await docClient.send(new GetCommand({
        TableName: 'Users',
        Key: { id: event.id }
    }))
    return result.Item
}
```

---

### 5.2 HTTP优化

**HTTP/2**:

```javascript
// Node.js HTTP/2客户端
const http2 = require('http2')

let client = null

function getClient() {
    if (!client) {
        client = http2.connect('https://api.example.com')
    }
    return client
}

exports.handler = async (event) => {
    const client = getClient()

    return new Promise((resolve, reject) => {
        const req = client.request({
            ':path': '/data',
            ':method': 'GET'
        })

        let data = ''
        req.on('data', chunk => data += chunk)
        req.on('end', () => resolve(data))
        req.on('error', reject)
        req.end()
    })
}
```

**压缩**:

```javascript
// 启用压缩
const axios = require('axios')
const zlib = require('zlib')

exports.handler = async (event) => {
    const response = await axios.get('https://api.example.com/large-data', {
        decompress: true,  // 自动解压
        headers: {
            'Accept-Encoding': 'gzip, deflate'
        }
    })

    return response.data
}
```

---

### 5.3 区域就近

**跨区域优化**:

```yaml
区域部署策略:

1. 全球分布:
   - us-east-1 (美东)
   - us-west-2 (美西)
   - eu-west-1 (欧洲)
   - ap-southeast-1 (亚太)

2. 使用CloudFront:
   - 边缘缓存
   - Lambda@Edge
   - 智能路由

3. 数据本地化:
   - 同区域数据库
   - 跨区域复制
   - Read Replica

4. DNS路由:
   - Route 53地理路由
   - 延迟路由
   - 故障转移
```

---

## 6. 数据库优化

### 6.1 连接池管理

**RDS Proxy**:

```yaml
# CloudFormation
Resources:
  DBProxy:
    Type: AWS::RDS::DBProxy
    Properties:
      DBProxyName: my-db-proxy
      EngineFamily: MYSQL
      Auth:
        - AuthScheme: SECRETS
          IAMAuth: DISABLED
          SecretArn: !Ref DBSecret
      RoleArn: !GetAtt DBProxyRole.Arn
      VpcSubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      RequireTLS: true
```

```javascript
// Lambda使用RDS Proxy
const mysql = require('mysql2/promise')

let connection = null

async function getConnection() {
    if (!connection) {
        connection = await mysql.createConnection({
            host: process.env.DB_PROXY_ENDPOINT,  // RDS Proxy端点
            user: process.env.DB_USER,
            password: process.env.DB_PASSWORD,
            database: process.env.DB_NAME,
            ssl: 'Amazon RDS'
        })
    }
    return connection
}

exports.handler = async (event) => {
    const conn = await getConnection()
    const [rows] = await conn.query('SELECT * FROM users WHERE id = ?', [event.id])
    return { statusCode: 200, body: JSON.stringify(rows[0]) }
}
```

---

### 6.2 查询优化

```javascript
// ❌ N+1查询问题
exports.handler = async (event) => {
    const users = await db.query('SELECT * FROM users')

    for (const user of users) {
        // N次额外查询!
        user.posts = await db.query('SELECT * FROM posts WHERE user_id = ?', [user.id])
    }

    return users
}

// ✅ JOIN查询
exports.handler = async (event) => {
    const [rows] = await db.query(`
        SELECT
            u.id, u.name, u.email,
            p.id as post_id, p.title, p.content
        FROM users u
        LEFT JOIN posts p ON p.user_id = u.id
    `)

    // 在代码中组装数据
    const users = {}
    for (const row of rows) {
        if (!users[row.id]) {
            users[row.id] = {
                id: row.id,
                name: row.name,
                email: row.email,
                posts: []
            }
        }
        if (row.post_id) {
            users[row.id].posts.push({
                id: row.post_id,
                title: row.title,
                content: row.content
            })
        }
    }

    return Object.values(users)
}
```

**索引优化**:

```sql
-- 分析慢查询
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';

-- 添加索引
CREATE INDEX idx_users_email ON users(email);

-- 复合索引
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at);
```

---

### 6.3 缓存策略

**Redis缓存**:

```javascript
// Lambda + ElastiCache Redis
const Redis = require('ioredis')

let redis = null

function getRedis() {
    if (!redis) {
        redis = new Redis({
            host: process.env.REDIS_HOST,
            port: 6379,
            password: process.env.REDIS_PASSWORD,
            db: 0,
            retryStrategy: (times) => Math.min(times * 50, 2000),
            enableOfflineQueue: false
        })
    }
    return redis
}

exports.handler = async (event) => {
    const redis = getRedis()
    const cacheKey = `user:${event.id}`

    // 1. 检查缓存
    const cached = await redis.get(cacheKey)
    if (cached) {
        console.log('Cache hit')
        return { statusCode: 200, body: cached }
    }

    // 2. 缓存未命中，查询数据库
    console.log('Cache miss')
    const conn = await getDBConnection()
    const [rows] = await conn.query('SELECT * FROM users WHERE id = ?', [event.id])
    const user = rows[0]

    // 3. 写入缓存 (TTL 5分钟)
    await redis.setex(cacheKey, 300, JSON.stringify(user))

    return { statusCode: 200, body: JSON.stringify(user) }
}
```

---

## 7. 成本优化

### 7.1 执行时间优化

```yaml
成本计算 (AWS Lambda):
  成本 = (执行时间 × 内存配置 × 价格) + 请求费用

  示例:
    128MB内存:
      执行10秒 = $0.0000208

    1024MB内存:
      执行2秒 = $0.0000334

    结论: 虽然1024MB单价更高，但总成本更低!

优化策略:
  ✅ 增加内存加速执行
  ✅ 优化代码减少时间
  ✅ 使用Compute Savings Plans
  ✅ 监控成本趋势
```

---

### 7.2 内存配置优化

**自动化测试**:

```python
# 成本优化测试脚本
import boto3
import json
from datetime import datetime

lambda_client = boto3.client('lambda')
cloudwatch = boto3.client('cloudwatch')

function_name = 'my-function'
memory_sizes = [128, 256, 512, 1024, 1536, 2048, 3008]
test_payload = json.dumps({'test': 'data'})

results = []

for memory in memory_sizes:
    # 更新内存配置
    lambda_client.update_function_configuration(
        FunctionName=function_name,
        MemorySize=memory
    )

    # 等待更新完成
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName=function_name)

    # 测试10次
    durations = []
    for i in range(10):
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=test_payload
        )
        log_result = json.loads(response['LogResult'])
        duration = extract_duration(log_result)
        durations.append(duration)

    avg_duration = sum(durations) / len(durations)

    # 计算成本
    gb_seconds = (memory / 1024) * (avg_duration / 1000)
    cost_per_invocation = gb_seconds * 0.0000166667

    results.append({
        'memory': memory,
        'avg_duration': avg_duration,
        'cost': cost_per_invocation
    })

    print(f'{memory}MB: {avg_duration:.2f}ms, ${cost_per_invocation:.10f}')

# 找到最优配置
optimal = min(results, key=lambda x: x['cost'])
print(f'\nOptimal: {optimal["memory"]}MB')
```

---

### 7.3 架构优化

**按需vs预留**:

```yaml
场景1: 低频访问API
  建议: 按需Lambda
  原因: 无需预留，成本最低

场景2: 高频稳定流量
  建议: Provisioned Concurrency
  原因: 无冷启动，用户体验好

场景3: 突发流量
  建议: 按需 + Auto Scaling Provisioned
  原因: 基础流量预留，突发流量按需

场景4: 可预测流量模式
  建议: 定时调整Provisioned
  原因: 工作时间预留，非工作时间按需
```

---

## 8. 监控与Profiling

### 8.1 性能监控

**CloudWatch Insights查询**:

```sql
-- P99延迟
fields @timestamp, @duration
| filter @type = "REPORT"
| stats pct(@duration, 99) as p99, avg(@duration) as avg, max(@duration) as max
| sort @timestamp desc

-- 冷启动率
fields @timestamp, @duration, @initDuration
| filter @type = "REPORT"
| stats
    count(*) as total,
    sum(@initDuration > 0) as coldStarts,
    sum(@initDuration > 0) / count(*) * 100 as coldStartRate

-- 内存使用
fields @timestamp, @maxMemoryUsed, @memorySize
| filter @type = "REPORT"
| stats
    max(@maxMemoryUsed) as maxUsed,
    avg(@maxMemoryUsed) as avgUsed,
    min(@memorySize) as allocated
| sort @timestamp desc

-- 错误率
fields @timestamp
| filter @type = "REPORT"
| stats
    count(*) as total,
    sum(statusCode >= 400) as errors,
    sum(statusCode >= 400) / count(*) * 100 as errorRate
```

---

### 8.2 分布式追踪

**AWS X-Ray**:

```javascript
// 启用X-Ray追踪
const AWSXRay = require('aws-xray-sdk-core')
const AWS = AWSXRay.captureAWS(require('aws-sdk'))
const http = AWSXRay.captureHTTPs(require('https'))

exports.handler = async (event, context) => {
    // 创建子段
    const segment = AWSXRay.getSegment()
    const subsegment = segment.addNewSubsegment('CustomOperation')

    try {
        // 业务逻辑
        subsegment.addAnnotation('userId', event.userId)
        subsegment.addMetadata('requestData', event)

        const result = await processRequest(event)

        subsegment.close()
        return result
    } catch (error) {
        subsegment.addError(error)
        subsegment.close()
        throw error
    }
}

async function processRequest(event) {
    // DynamoDB调用 (自动追踪)
    const dynamodb = new AWS.DynamoDB.DocumentClient()
    const data = await dynamodb.get({
        TableName: 'Users',
        Key: { id: event.userId }
    }).promise()

    // HTTP调用 (自动追踪)
    const response = await fetch('https://api.example.com/data')

    return { data, response }
}
```

---

### 8.3 Profiling工具

**Node.js Profiling**:

```javascript
// 使用clinic.js进行本地profiling
// npm install -g clinic

// 运行profiling
// clinic doctor -- node app.js
// clinic flame -- node app.js

// Lambda环境profiling
const v8Profiler = require('v8-profiler-next')
const fs = require('fs').promises

let isProfiling = false

exports.handler = async (event, context) => {
    // 通过环境变量控制profiling
    if (process.env.ENABLE_PROFILING === 'true' && !isProfiling) {
        isProfiling = true
        const profileId = `profile-${Date.now()}`
        v8Profiler.startProfiling(profileId, true)

        try {
            const result = await handleRequest(event)

            // 停止profiling
            const profile = v8Profiler.stopProfiling(profileId)

            // 导出到S3
            const profileJson = JSON.stringify(profile)
            const s3 = new AWS.S3()
            await s3.putObject({
                Bucket: process.env.PROFILE_BUCKET,
                Key: `${profileId}.cpuprofile`,
                Body: profileJson
            }).promise()

            profile.delete()
            isProfiling = false

            return result
        } catch (error) {
            isProfiling = false
            throw error
        }
    }

    return handleRequest(event)
}
```

---

## 9. 总结

```yaml
本章要点:
  ✅ 性能指标 (冷启动/热启动/P99延迟)
  ✅ 冷启动优化 (预热/Provisioned Concurrency)
  ✅ 内存优化 (配置策略/缓存/泄漏检测)
  ✅ CPU优化 (算法/并发处理)
  ✅ 网络优化 (连接复用/HTTP/2/区域就近)
  ✅ 数据库优化 (连接池/查询/缓存)
  ✅ 成本优化 (执行时间/内存配置/架构)
  ✅ 监控Profiling (CloudWatch/X-Ray/Profiling工具)

性能优化核心原则:
  ⭐ 测量优先 (不测量不优化)
  ⭐ 找准瓶颈 (80/20法则)
  ⭐ 循序渐进 (逐步优化)
  ⭐ 权衡取舍 (成本vs性能)
  ⭐ 持续监控 (性能回归)

关键优化技术:
  ✅ 全局变量复用
  ✅ 连接池管理
  ✅ 并行处理 (Promise.all)
  ✅ 缓存策略 (Redis/全局缓存)
  ✅ 代码打包优化
  ✅ RDS Proxy
  ✅ Provisioned Concurrency

成本优化策略:
  ✅ 增加内存加速执行
  ✅ 优化算法减少时间
  ✅ 合理配置预留并发
  ✅ 监控成本趋势

监控工具:
  ✅ CloudWatch Metrics
  ✅ CloudWatch Insights
  ✅ AWS X-Ray
  ✅ Lambda Power Tuning
```

---

**下一章预告**:

**07 - Serverless CI/CD**:

- CI/CD流程设计
- 多环境管理
- 自动化测试
- 金丝雀部署
- 回滚策略

---

**完成日期**: 2025-10-19
**版本**: v1.0
**作者**: 云原生专家团队

**Tags**: `#ServerlessPerformance` `#ColdStart` `#Optimization` `#Monitoring` `#Profiling`

---

## 相关文档

### 本模块相关

- [Serverless概述与架构](./01_Serverless概述与架构.md) - Serverless概述与架构
- [Knative深度解析](./02_Knative深度解析.md) - Knative深度解析
- [OpenFaaS实战](./03_OpenFaaS实战.md) - OpenFaaS实战
- [边缘Serverless](./04_边缘Serverless.md) - 边缘Serverless
- [Serverless安全](./05_Serverless安全.md) - Serverless安全
- [Serverless CI/CD](./07_Serverless_CICD.md) - Serverless CI/CD
- [Serverless实战案例](./08_Serverless实战案例.md) - Serverless实战案例
- [Serverless最佳实践](./09_Serverless最佳实践.md) - Serverless最佳实践
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [容器性能调优](../06_容器监控与运维/03_容器性能调优.md) - 容器性能调优
- [容器监控技术](../06_容器监控与运维/01_容器监控技术.md) - 容器监控技术
- [服务网格性能优化](../18_服务网格技术详解/08_服务网格性能优化与故障排查.md) - 服务网格性能优化
- [eBPF性能优化](../16_eBPF技术详解/06_eBPF性能优化.md) - eBPF性能优化

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新
