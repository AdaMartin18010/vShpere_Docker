# 07 - Serverless CI/CD

**作者**: 云原生专家团队
**创建日期**: 2025-10-19
**最后更新**: 2025-10-19
**版本**: v1.0

---

## 📋 本章导航

- [07 - Serverless CI/CD](#07---serverless-cicd)
  - [📋 本章导航](#-本章导航)
  - [1. CI/CD概述](#1-cicd概述)
    - [1.1 Serverless CI/CD特点](#11-serverless-cicd特点)
    - [1.2 Pipeline架构](#12-pipeline架构)
  - [2. 多环境管理](#2-多环境管理)
    - [2.1 环境策略](#21-环境策略)
    - [2.2 配置管理](#22-配置管理)
    - [2.3 Secrets管理](#23-secrets管理)
  - [3. 自动化测试](#3-自动化测试)
    - [3.1 单元测试](#31-单元测试)
    - [3.2 集成测试](#32-集成测试)
    - [3.3 E2E测试](#33-e2e测试)
  - [4. 部署策略](#4-部署策略)
    - [4.1 蓝绿部署](#41-蓝绿部署)
    - [4.2 金丝雀发布](#42-金丝雀发布)
    - [4.3 回滚策略](#43-回滚策略)
  - [5. GitHub Actions](#5-github-actions)
    - [5.1 基础Workflow](#51-基础workflow)
    - [5.2 多Stage部署](#52-多stage部署)
    - [5.3 高级特性](#53-高级特性)
  - [6. GitLab CI](#6-gitlab-ci)
    - [6.1 Pipeline配置](#61-pipeline配置)
    - [6.2 并行部署](#62-并行部署)
  - [7. Infrastructure as Code](#7-infrastructure-as-code)
    - [7.1 Serverless Framework](#71-serverless-framework)
    - [7.2 AWS SAM](#72-aws-sam)
    - [7.3 Terraform](#73-terraform)
  - [8. 最佳实践](#8-最佳实践)
  - [9. 总结](#9-总结)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 1. CI/CD概述

### 1.1 Serverless CI/CD特点

```yaml
Serverless vs 传统CI/CD:

传统应用:
  - 构建Docker镜像
  - 推送到镜像仓库
  - 更新Kubernetes部署
  - 滚动更新Pods

Serverless应用:
  - 打包函数代码
  - 上传到云存储 (S3)
  - 更新函数配置
  - 流量切换

Serverless CI/CD特点:

1. 快速部署:
   ✅ 无需容器构建
   ✅ 代码包小 (几MB)
   ✅ 部署时间短 (秒级)

2. 原子更新:
   ✅ 函数版本不可变
   ✅ 自动版本控制
   ✅ 易于回滚

3. 流量控制:
   ✅ Alias流量分配
   ✅ 金丝雀发布
   ✅ 蓝绿部署

4. 测试挑战:
   ⚠️ 本地环境模拟困难
   ⚠️ 集成测试复杂
   ⚠️ 依赖云服务

5. 成本优化:
   ✅ 按实际使用付费
   ✅ 无闲置资源
   ✅ 自动扩缩容

6. 监控告警:
   ✅ 内置指标
   ✅ 分布式追踪
   ✅ 实时日志
```

---

### 1.2 Pipeline架构

```yaml
标准Serverless CI/CD Pipeline:

1. Source (代码源):
   - GitHub/GitLab/Bitbucket
   - 触发器: push/PR/tag
   - Webhook集成

2. Build (构建):
   - 依赖安装 (npm/pip/go mod)
   - 代码编译 (TypeScript/Go)
   - 打包压缩
   - 生成artifacts

3. Test (测试):
   - 单元测试 (Jest/pytest)
   - 代码覆盖率
   - 安全扫描 (Snyk/SonarQube)
   - Lint检查

4. Package (打包):
   - 创建部署包
   - 上传到S3/存储
   - 生成SAM/CloudFormation模板

5. Deploy to Dev (部署开发环境):
   - 自动部署
   - 运行集成测试
   - 烟雾测试

6. Deploy to Staging (部署预发布):
   - 手动/自动触发
   - 完整测试套件
   - 性能测试

7. Deploy to Production (生产部署):
   - 审批流程
   - 金丝雀/蓝绿部署
   - 流量切换
   - 监控告警

8. Post-Deployment (部署后):
   - 健康检查
   - 自动回滚
   - 通知团队
```

**Pipeline可视化**:

```text
┌─────────────────────────────────────────────────────────┐
│                  Serverless CI/CD Pipeline              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Git Push → GitHub                                       │
│      ↓                                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  1. Build                                        │  │
│  │     - npm install                                │  │
│  │     - npm run build                              │  │
│  │     - zip package                                │  │
│  └──────────────────────────────────────────────────┘  │
│      ↓                                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  2. Test                                         │  │
│  │     - npm test                                   │  │
│  │     - npm run lint                               │  │
│  │     - security scan                              │  │
│  └──────────────────────────────────────────────────┘  │
│      ↓                                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  3. Deploy to Dev                                │  │
│  │     - serverless deploy --stage dev              │  │
│  │     - integration tests                          │  │
│  └──────────────────────────────────────────────────┘  │
│      ↓                                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  4. Deploy to Staging (manual approval)          │  │
│  │     - serverless deploy --stage staging          │  │
│  │     - full test suite                            │  │
│  └──────────────────────────────────────────────────┘  │
│      ↓                                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  5. Deploy to Production (manual approval)       │  │
│  │     - canary: 10% → 50% → 100%                   │  │
│  │     - monitor metrics                            │  │
│  │     - auto rollback if error                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 多环境管理

### 2.1 环境策略

```yaml
典型环境配置:

1. Development (开发):
   目的: 开发人员日常开发
   特点:
     - 最新代码
     - 快速迭代
     - 低成本配置
   资源:
     - Lambda: 128MB内存
     - DynamoDB: 按需计费
     - 无Provisioned Concurrency

2. Staging (预发布):
   目的: 测试和QA
   特点:
     - 接近生产环境
     - 完整测试
     - 性能测试
   资源:
     - Lambda: 512MB内存
     - DynamoDB: 低预留容量
     - 1-2个Provisioned实例

3. Production (生产):
   目的: 服务真实用户
   特点:
     - 高可用
     - 高性能
     - 完整监控
   资源:
     - Lambda: 1024MB内存
     - DynamoDB: 高预留容量
     - Auto Scaling Provisioned
     - 多区域部署

4. (可选) QA:
   目的: 专门QA测试

5. (可选) Demo:
   目的: 演示和培训
```

---

### 2.2 配置管理

**Serverless Framework多环境**:

```yaml
# serverless.yml
service: my-serverless-app

provider:
  name: aws
  runtime: nodejs18.x
  stage: ${opt:stage, 'dev'}
  region: ${opt:region, 'us-east-1'}

  # 环境变量
  environment:
    STAGE: ${self:provider.stage}
    DB_TABLE: ${self:custom.tableName}
    API_URL: ${self:custom.apiUrl.${self:provider.stage}}

custom:
  # 表名: 按stage区分
  tableName: ${self:service}-${self:provider.stage}-users

  # API URL: 不同环境
  apiUrl:
    dev: https://dev-api.example.com
    staging: https://staging-api.example.com
    prod: https://api.example.com

  # 函数配置: 按环境
  functionConfig:
    dev:
      memorySize: 128
      timeout: 10
      provisionedConcurrency: 0
    staging:
      memorySize: 512
      timeout: 30
      provisionedConcurrency: 2
    prod:
      memorySize: 1024
      timeout: 60
      provisionedConcurrency: 10

functions:
  api:
    handler: src/handler.main
    memorySize: ${self:custom.functionConfig.${self:provider.stage}.memorySize}
    timeout: ${self:custom.functionConfig.${self:provider.stage}.timeout}
    provisionedConcurrency: ${self:custom.functionConfig.${self:provider.stage}.provisionedConcurrency}
    events:
      - http:
          path: /api/{proxy+}
          method: ANY

resources:
  Resources:
    UsersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:custom.tableName}
        BillingMode: ${self:custom.dynamoConfig.${self:provider.stage}.billingMode}
        # ...
```

**部署命令**:

```bash
# 部署到dev
serverless deploy --stage dev

# 部署到staging
serverless deploy --stage staging

# 部署到production
serverless deploy --stage prod --region us-east-1
```

---

### 2.3 Secrets管理

**AWS Systems Manager Parameter Store**:

```bash
# 存储secrets (按环境)
aws ssm put-parameter \
  --name "/myapp/dev/db-password" \
  --value "dev_password_123" \
  --type SecureString

aws ssm put-parameter \
  --name "/myapp/prod/db-password" \
  --value "prod_secure_password" \
  --type SecureString

# 存储API密钥
aws ssm put-parameter \
  --name "/myapp/prod/api-key" \
  --value "sk_live_..." \
  --type SecureString
```

```yaml
# serverless.yml - 引用参数
provider:
  environment:
    DB_PASSWORD: ${ssm:/myapp/${self:provider.stage}/db-password~true}
    API_KEY: ${ssm:/myapp/${self:provider.stage}/api-key~true}
```

**GitHub Secrets**:

```yaml
# .github/workflows/deploy.yml
env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  PROD_API_KEY: ${{ secrets.PROD_API_KEY }}
  STAGING_API_KEY: ${{ secrets.STAGING_API_KEY }}
```

---

## 3. 自动化测试

### 3.1 单元测试

**Jest (Node.js)**:

```javascript
// src/handler.js
exports.main = async (event) => {
    const body = JSON.parse(event.body)
    const result = calculateTotal(body.items)

    return {
        statusCode: 200,
        body: JSON.stringify({ total: result })
    }
}

function calculateTotal(items) {
    return items.reduce((sum, item) => sum + item.price * item.quantity, 0)
}

module.exports = { calculateTotal }
```

```javascript
// __tests__/handler.test.js
const { calculateTotal } = require('../src/handler')

describe('calculateTotal', () => {
    test('should calculate total correctly', () => {
        const items = [
            { price: 10, quantity: 2 },
            { price: 5, quantity: 3 }
        ]

        expect(calculateTotal(items)).toBe(35)
    })

    test('should handle empty array', () => {
        expect(calculateTotal([])).toBe(0)
    })

    test('should handle single item', () => {
        const items = [{ price: 100, quantity: 1 }]
        expect(calculateTotal(items)).toBe(100)
    })
})
```

```json
// package.json
{
  "scripts": {
    "test": "jest",
    "test:coverage": "jest --coverage",
    "test:watch": "jest --watch"
  },
  "jest": {
    "testEnvironment": "node",
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

---

### 3.2 集成测试

```javascript
// __tests__/integration.test.js
const AWS = require('aws-sdk')
const axios = require('axios')

// 使用本地DynamoDB
const dynamodb = new AWS.DynamoDB.DocumentClient({
    endpoint: 'http://localhost:8000',
    region: 'local'
})

describe('Integration Tests', () => {
    beforeAll(async () => {
        // 创建测试表
        await createTestTable()
    })

    afterAll(async () => {
        // 清理
        await deleteTestTable()
    })

    test('should create user and retrieve it', async () => {
        // 1. 创建用户
        const user = {
            id: '123',
            name: 'Test User',
            email: 'test@example.com'
        }

        await dynamodb.put({
            TableName: 'Users',
            Item: user
        }).promise()

        // 2. 检索用户
        const result = await dynamodb.get({
            TableName: 'Users',
            Key: { id: '123' }
        }).promise()

        expect(result.Item).toEqual(user)
    })

    test('should call API endpoint', async () => {
        const apiUrl = process.env.API_URL || 'http://localhost:3000'

        const response = await axios.post(`${apiUrl}/users`, {
            name: 'Test User',
            email: 'test@example.com'
        })

        expect(response.status).toBe(201)
        expect(response.data).toHaveProperty('id')
    })
})
```

**serverless-offline (本地测试)**:

```bash
# 安装插件
npm install --save-dev serverless-offline

# serverless.yml
plugins:
  - serverless-offline

# 启动本地API
serverless offline start

# 在另一个终端运行集成测试
npm run test:integration
```

---

### 3.3 E2E测试

```javascript
// __tests__/e2e.test.js
const axios = require('axios')

const API_URL = process.env.API_URL

describe('E2E Tests', () => {
    let authToken
    let userId

    test('1. User Registration', async () => {
        const response = await axios.post(`${API_URL}/auth/register`, {
            email: 'e2e@example.com',
            password: 'Test123!',
            name: 'E2E Test User'
        })

        expect(response.status).toBe(201)
        expect(response.data).toHaveProperty('userId')
        userId = response.data.userId
    })

    test('2. User Login', async () => {
        const response = await axios.post(`${API_URL}/auth/login`, {
            email: 'e2e@example.com',
            password: 'Test123!'
        })

        expect(response.status).toBe(200)
        expect(response.data).toHaveProperty('token')
        authToken = response.data.token
    })

    test('3. Get User Profile', async () => {
        const response = await axios.get(`${API_URL}/users/${userId}`, {
            headers: { Authorization: `Bearer ${authToken}` }
        })

        expect(response.status).toBe(200)
        expect(response.data.email).toBe('e2e@example.com')
    })

    test('4. Update User Profile', async () => {
        const response = await axios.put(`${API_URL}/users/${userId}`, {
            name: 'Updated Name'
        }, {
            headers: { Authorization: `Bearer ${authToken}` }
        })

        expect(response.status).toBe(200)
        expect(response.data.name).toBe('Updated Name')
    })

    test('5. Delete User', async () => {
        const response = await axios.delete(`${API_URL}/users/${userId}`, {
            headers: { Authorization: `Bearer ${authToken}` }
        })

        expect(response.status).toBe(204)
    })
})
```

---

## 4. 部署策略

### 4.1 蓝绿部署

**AWS Lambda Alias蓝绿部署**:

```bash
# 1. 发布新版本
aws lambda publish-version --function-name my-function

# 输出: Version 2

# 2. 更新Alias指向新版本 (蓝绿切换)
aws lambda update-alias \
  --function-name my-function \
  --name prod \
  --function-version 2

# 3. 如果有问题，立即回滚到旧版本
aws lambda update-alias \
  --function-name my-function \
  --name prod \
  --function-version 1
```

**CloudFormation蓝绿部署**:

```yaml
# template.yaml
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-function
      Runtime: nodejs18.x
      Handler: index.handler
      Code:
        S3Bucket: my-bucket
        S3Key: function-v2.zip
      # 自动发布版本
      AutoPublishAlias: live

      # 部署偏好
      DeploymentPreference:
        Type: AllAtOnce  # 或 Canary10Percent5Minutes
        Alarms:
          - !Ref MyFunctionErrorAlarm
        Hooks:
          PreTraffic: !Ref PreTrafficHook
          PostTraffic: !Ref PostTrafficHook

  # 错误告警
  MyFunctionErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: MyFunction-Errors
      MetricName: Errors
      Namespace: AWS/Lambda
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: GreaterThanThreshold
```

---

### 4.2 金丝雀发布

**Lambda流量分配**:

```bash
# 1. 发布新版本
aws lambda publish-version --function-name my-function
# Version: 3

# 2. 创建Alias，分配流量 (10%到新版本)
aws lambda create-alias \
  --function-name my-function \
  --name prod \
  --function-version 3 \
  --routing-config "AdditionalVersionWeights={2=0.9}"

# 3. 监控指标，逐步增加流量
# 50% 新版本
aws lambda update-alias \
  --function-name my-function \
  --name prod \
  --routing-config "AdditionalVersionWeights={2=0.5}"

# 4. 100% 新版本
aws lambda update-alias \
  --function-name my-function \
  --name prod \
  --function-version 3
```

**SAM金丝雀部署**:

```yaml
# template.yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: nodejs18.x
      AutoPublishAlias: live

      DeploymentPreference:
        Type: Canary10Percent5Minutes
        # 可选类型:
        # - Canary10Percent30Minutes
        # - Canary10Percent5Minutes
        # - Canary10Percent10Minutes
        # - Linear10PercentEvery1Minute
        # - Linear10PercentEvery2Minutes
        # - Linear10PercentEvery3Minutes
        # - Linear10PercentEvery10Minutes
        # - AllAtOnce

        Alarms:
          - !Ref CanaryErrorsAlarm

        Hooks:
          PreTraffic: !Ref PreTrafficFunction
          PostTraffic: !Ref PostTrafficFunction

  # 金丝雀错误告警
  CanaryErrorsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${AWS::StackName}-canary-errors
      MetricName: Errors
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref MyFunction
        - Name: Resource
          Value: !Sub ${MyFunction}:live
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 2
      Threshold: 0
      ComparisonOperator: GreaterThanThreshold
      TreatMissingData: notBreaching

  # 部署前钩子
  PreTrafficFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: hooks.preTraffic
      Runtime: nodejs18.x
      Environment:
        Variables:
          NEW_VERSION: !Ref MyFunction.Version

  # 部署后钩子
  PostTrafficFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: hooks.postTraffic
      Runtime: nodejs18.x
```

**钩子函数实现**:

```javascript
// hooks.js
const AWS = require('aws-sdk')
const codedeploy = new AWS.CodeDeploy()

exports.preTraffic = async (event) => {
    console.log('PreTraffic Hook - Running pre-deployment tests')

    const newVersion = process.env.NEW_VERSION
    const functionName = event.DeploymentId

    try {
        // 运行烟雾测试
        await runSmokeTests(newVersion)

        // 成功，继续部署
        await codedeploy.putLifecycleEventHookExecutionStatus({
            deploymentId: event.DeploymentId,
            lifecycleEventHookExecutionId: event.LifecycleEventHookExecutionId,
            status: 'Succeeded'
        }).promise()

        return 'Deployment can proceed'
    } catch (error) {
        console.error('Pre-traffic tests failed:', error)

        // 失败，停止部署
        await codedeploy.putLifecycleEventHookExecutionStatus({
            deploymentId: event.DeploymentId,
            lifecycleEventHookExecutionId: event.LifecycleEventHookExecutionId,
            status: 'Failed'
        }).promise()

        throw error
    }
}

exports.postTraffic = async (event) => {
    console.log('PostTraffic Hook - Validating deployment')

    try {
        // 验证部署
        await validateDeployment()

        // 成功
        await codedeploy.putLifecycleEventHookExecutionStatus({
            deploymentId: event.DeploymentId,
            lifecycleEventHookExecutionId: event.LifecycleEventHookExecutionId,
            status: 'Succeeded'
        }).promise()

        return 'Deployment validated successfully'
    } catch (error) {
        console.error('Post-traffic validation failed:', error)

        // 失败，触发回滚
        await codedeploy.putLifecycleEventHookExecutionStatus({
            deploymentId: event.DeploymentId,
            lifecycleEventHookExecutionId: event.LifecycleEventHookExecutionId,
            status: 'Failed'
        }).promise()

        throw error
    }
}
```

---

### 4.3 回滚策略

```yaml
回滚场景:

1. 自动回滚:
   触发条件:
     - CloudWatch告警触发
     - 错误率超过阈值
     - 延迟超过阈值

   动作:
     - CodeDeploy自动回滚
     - 恢复到上一个版本
     - 发送通知

2. 手动回滚:
   场景:
     - 发现业务逻辑错误
     - 性能下降
     - 用户投诉

   步骤:
     - 确认回滚版本
     - 更新Alias
     - 验证功能
     - 通知团队

3. 部分回滚:
   场景:
     - 金丝雀发布失败
     - 流量切换过程中发现问题

   策略:
     - 停止流量切换
     - 保持当前流量分配
     - 分析问题
     - 决定继续或回滚
```

**自动回滚脚本**:

```javascript
// rollback.js
const AWS = require('aws-sdk')
const lambda = new AWS.Lambda()

async function rollback(functionName, aliasName) {
    // 1. 获取当前Alias配置
    const alias = await lambda.getAlias({
        FunctionName: functionName,
        Name: aliasName
    }).promise()

    console.log(`Current version: ${alias.FunctionVersion}`)

    // 2. 获取上一个版本
    const versions = await lambda.listVersionsByFunction({
        FunctionName: functionName,
        MaxItems: 10
    }).promise()

    const currentIndex = versions.Versions.findIndex(v => v.Version === alias.FunctionVersion)
    const previousVersion = versions.Versions[currentIndex + 1]

    if (!previousVersion) {
        throw new Error('No previous version found')
    }

    console.log(`Rolling back to version: ${previousVersion.Version}`)

    // 3. 更新Alias到上一个版本
    await lambda.updateAlias({
        FunctionName: functionName,
        Name: aliasName,
        FunctionVersion: previousVersion.Version
    }).promise()

    console.log('Rollback completed successfully')

    // 4. 发送通知
    await sendNotification({
        subject: `Rollback: ${functionName}`,
        message: `Rolled back from v${alias.FunctionVersion} to v${previousVersion.Version}`
    })
}

// 使用
rollback('my-function', 'prod').catch(console.error)
```

---

## 5. GitHub Actions

### 5.1 基础Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Serverless Application

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  NODE_VERSION: '18'
  AWS_REGION: 'us-east-1'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run linter
      run: npm run lint

    - name: Run tests
      run: npm test

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage/lcov.info

  deploy-dev:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ env.NODE_VERSION }}

    - name: Install dependencies
      run: npm ci

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Install Serverless Framework
      run: npm install -g serverless

    - name: Deploy to Dev
      run: serverless deploy --stage dev --verbose

    - name: Run integration tests
      run: npm run test:integration
      env:
        API_URL: ${{ steps.deploy.outputs.api-url }}

  deploy-prod:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: ${{ steps.deploy.outputs.api-url }}

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ env.NODE_VERSION }}

    - name: Install dependencies
      run: npm ci

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID_PROD }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY_PROD }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Install Serverless Framework
      run: npm install -g serverless

    - name: Deploy to Production
      id: deploy
      run: |
        serverless deploy --stage prod --verbose
        API_URL=$(serverless info --stage prod --verbose | grep "GET" | awk '{print $3}')
        echo "api-url=$API_URL" >> $GITHUB_OUTPUT

    - name: Notify Slack
      if: always()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: 'Production deployment ${{ job.status }}'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

### 5.2 多Stage部署

```yaml
# .github/workflows/multi-stage.yml
name: Multi-Stage Deployment

on:
  push:
    branches: [ main ]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Deploy to Staging
      run: |
        npm ci
        npm install -g serverless
        serverless deploy --stage staging
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

    - name: Run E2E tests
      run: npm run test:e2e
      env:
        API_URL: ${{ steps.get-url.outputs.url }}

  approval:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production-approval
    steps:
    - name: Wait for approval
      run: echo "Waiting for manual approval..."

  deploy-production:
    needs: approval
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Deploy to Production (Canary)
      run: |
        npm ci
        npm install -g serverless
        serverless deploy --stage prod
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID_PROD }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY_PROD }}

    - name: Monitor deployment
      run: node scripts/monitor-deployment.js
      timeout-minutes: 30

    - name: Rollback on failure
      if: failure()
      run: node scripts/rollback.js
```

---

### 5.3 高级特性

**缓存依赖**:

```yaml
- name: Cache node modules
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

**并行部署多个函数**:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        function: [api, worker, scheduler]

    steps:
    - uses: actions/checkout@v3
    - name: Deploy ${{ matrix.function }}
      run: |
        cd functions/${{ matrix.function }}
        serverless deploy --stage prod
```

---

## 6. GitLab CI

### 6.1 Pipeline配置

```yaml
# .gitlab-ci.yml
image: node:18

stages:
  - build
  - test
  - deploy-dev
  - deploy-staging
  - deploy-prod

variables:
  AWS_DEFAULT_REGION: us-east-1

cache:
  paths:
    - node_modules/

before_script:
  - npm ci

# 构建
build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour

# 测试
test:
  stage: test
  script:
    - npm run lint
    - npm test
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

# 安全扫描
security:
  stage: test
  script:
    - npm audit
    - npm install -g snyk
    - snyk test
  allow_failure: true

# 部署到Dev
deploy:dev:
  stage: deploy-dev
  script:
    - npm install -g serverless
    - serverless deploy --stage dev --verbose
  environment:
    name: development
    url: https://dev-api.example.com
  only:
    - develop

# 部署到Staging
deploy:staging:
  stage: deploy-staging
  script:
    - npm install -g serverless
    - serverless deploy --stage staging --verbose
    - npm run test:e2e
  environment:
    name: staging
    url: https://staging-api.example.com
  only:
    - main
  when: manual

# 部署到Production
deploy:prod:
  stage: deploy-prod
  script:
    - npm install -g serverless
    - serverless deploy --stage prod --verbose
  environment:
    name: production
    url: https://api.example.com
  only:
    - main
  when: manual
  before_script:
    - echo "Deploying to production..."
  after_script:
    - echo "Production deployment completed"
    - curl -X POST $SLACK_WEBHOOK -d '{"text":"Production deployed!"}'
```

---

### 6.2 并行部署

```yaml
# 并行部署多个区域
deploy:multi-region:
  stage: deploy-prod
  parallel:
    matrix:
      - REGION: [us-east-1, eu-west-1, ap-southeast-1]
  script:
    - serverless deploy --stage prod --region $REGION
  environment:
    name: production-$REGION
```

---

## 7. Infrastructure as Code

### 7.1 Serverless Framework

完整的`serverless.yml`示例已在前面章节展示。

---

### 7.2 AWS SAM

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: SAM Template for Serverless Application

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: nodejs18.x
    Environment:
      Variables:
        TABLE_NAME: !Ref UsersTable
        STAGE: !Ref Stage

Parameters:
  Stage:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/api.handler
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /api/{proxy+}
            Method: ANY
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub ${Stage}-users
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/${Stage}/
  FunctionArn:
    Description: Lambda Function ARN
    Value: !GetAtt ApiFunction.Arn
```

**SAM CLI部署**:

```bash
# 构建
sam build

# 部署到dev
sam deploy --parameter-overrides Stage=dev --stack-name myapp-dev

# 部署到prod
sam deploy --parameter-overrides Stage=prod --stack-name myapp-prod
```

---

### 7.3 Terraform

```hcl
# main.tf
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "my-terraform-state"
    key    = "serverless/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "stage" {
  type    = string
  default = "dev"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

# Lambda Function
resource "aws_lambda_function" "api" {
  filename      = "function.zip"
  function_name = "${var.stage}-api-function"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "nodejs18.x"
  memory_size   = 512
  timeout       = 30

  environment {
    variables = {
      STAGE      = var.stage
      TABLE_NAME = aws_dynamodb_table.users.name
    }
  }

  tags = {
    Environment = var.stage
  }
}

# Lambda IAM Role
resource "aws_iam_role" "lambda_role" {
  name = "${var.stage}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# DynamoDB Table
resource "aws_dynamodb_table" "users" {
  name         = "${var.stage}-users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Environment = var.stage
  }
}

# Outputs
output "function_name" {
  value = aws_lambda_function.api.function_name
}

output "function_arn" {
  value = aws_lambda_function.api.arn
}
```

**Terraform部署**:

```bash
# 初始化
terraform init

# 部署到dev
terraform workspace new dev
terraform apply -var="stage=dev"

# 部署到prod
terraform workspace new prod
terraform apply -var="stage=prod"
```

---

## 8. 最佳实践

```yaml
Serverless CI/CD最佳实践:

1. 版本控制:
   ✅ Git工作流 (feature→develop→main)
   ✅ Semantic Versioning
   ✅ Git标签管理版本
   ✅ 保护main分支

2. 环境管理:
   ✅ dev/staging/prod分离
   ✅ 环境特定配置
   ✅ Secrets安全管理
   ✅ 基础设施即代码

3. 自动化测试:
   ✅ 单元测试 (>80%覆盖率)
   ✅ 集成测试
   ✅ E2E测试
   ✅ 性能测试
   ✅ 安全扫描

4. 部署策略:
   ✅ 金丝雀发布
   ✅ 蓝绿部署
   ✅ 流量分配
   ✅ 自动回滚

5. 监控告警:
   ✅ 部署后健康检查
   ✅ 错误率监控
   ✅ 延迟监控
   ✅ 成本监控
   ✅ Slack/Email通知

6. 安全:
   ✅ 最小权限IAM
   ✅ Secrets加密
   ✅ 依赖扫描
   ✅ 代码审计

7. 文档:
   ✅ README完善
   ✅ 架构图
   ✅ API文档
   ✅ 运维手册
   ✅ 变更日志

8. 审批流程:
   ✅ PR Review
   ✅ 生产部署审批
   ✅ 变更管理
```

---

## 9. 总结

```yaml
本章要点:
  ✅ CI/CD概述 (Serverless特点/Pipeline架构)
  ✅ 多环境管理 (dev/staging/prod/配置/Secrets)
  ✅ 自动化测试 (单元/集成/E2E)
  ✅ 部署策略 (蓝绿/金丝雀/回滚)
  ✅ GitHub Actions (Workflow/多Stage/高级特性)
  ✅ GitLab CI (Pipeline/并行部署)
  ✅ IaC (Serverless Framework/SAM/Terraform)
  ✅ 最佳实践 (8大领域)

关键部署策略:
  ⭐ 蓝绿部署 (快速切换/快速回滚)
  ⭐ 金丝雀发布 (逐步验证/降低风险)
  ⭐ 自动回滚 (告警触发/保障稳定)

CI/CD工具链:
  ✅ GitHub Actions (最流行)
  ✅ GitLab CI (GitLab生态)
  ✅ Jenkins (企业传统)
  ✅ CircleCI/Travis CI (云服务)

IaC工具:
  ✅ Serverless Framework (最简单)
  ✅ AWS SAM (AWS原生)
  ✅ Terraform (多云支持)
  ✅ CDK (编程式IaC)

测试策略:
  ✅ 单元测试 (80%+覆盖率)
  ✅ 集成测试 (serverless-offline)
  ✅ E2E测试 (完整流程)
  ✅ 性能测试 (负载测试)
```

---

**下一章预告**:

**08 - Serverless实战案例**:

- REST API完整案例
- 图片处理服务
- 数据处理Pipeline
- WebSocket实时应用
- 事件驱动架构

---

**完成日期**: 2025-10-19
**版本**: v1.0
**作者**: 云原生专家团队

**Tags**: `#ServerlessCI/CD` `#GitHubActions` `#Canary` `#BlueGreen` `#IaC` `#Testing`

---

## 相关文档

### 本模块相关

- [Serverless概述与架构](./01_Serverless概述与架构.md) - Serverless概述与架构
- [Knative深度解析](./02_Knative深度解析.md) - Knative深度解析
- [OpenFaaS实战](./03_OpenFaaS实战.md) - OpenFaaS实战
- [边缘Serverless](./04_边缘Serverless.md) - 边缘Serverless
- [Serverless安全](./05_Serverless安全.md) - Serverless安全
- [Serverless性能优化](./06_Serverless性能优化.md) - Serverless性能优化
- [Serverless实战案例](./08_Serverless实战案例.md) - Serverless实战案例
- [Serverless最佳实践](./09_Serverless最佳实践.md) - Serverless最佳实践
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [容器技术实践案例](../08_容器技术实践案例/README.md) - 容器技术实践案例
- [DevOps容器化实践](../08_容器技术实践案例/03_DevOps容器化实践.md) - DevOps容器化实践
- [Kubernetes技术详解](../03_Kubernetes技术详解/README.md) - Kubernetes技术体系
- [容器编排技术](../04_容器编排技术/README.md) - 容器编排技术

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新
