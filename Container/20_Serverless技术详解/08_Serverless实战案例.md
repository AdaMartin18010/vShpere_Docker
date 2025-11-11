# 08 - Serverless实战案例

**作者**: 云原生专家团队
**创建日期**: 2025-10-19
**最后更新**: 2025-10-19
**版本**: v1.0

---

## 📋 本章导航

- [08 - Serverless实战案例](#08---serverless实战案例)
  - [📋 本章导航](#-本章导航)
  - [1. REST API完整案例](#1-rest-api完整案例)
    - [场景: 用户管理API](#场景-用户管理api)
  - [2. 图片处理服务](#2-图片处理服务)
    - [场景: 自动图片优化](#场景-自动图片优化)
  - [3. 数据处理Pipeline](#3-数据处理pipeline)
    - [场景: CSV数据ETL](#场景-csv数据etl)
  - [4. WebSocket实时应用](#4-websocket实时应用)
    - [场景: 实时聊天](#场景-实时聊天)
  - [5. 事件驱动架构](#5-事件驱动架构)
    - [场景: 电商订单处理](#场景-电商订单处理)
  - [6. 总结](#6-总结)
  - [相关文档](#相关文档)
    - [本模块相关](#本模块相关)
    - [其他模块相关](#其他模块相关)

---

## 1. REST API完整案例

### 场景: 用户管理API

**架构**:

- API Gateway + Lambda + DynamoDB
- JWT认证
- CRUD操作
- 参数验证

```yaml
# serverless.yml
service: user-api

provider:
  name: aws
  runtime: nodejs18.x
  stage: ${opt:stage, 'dev'}
  region: us-east-1
  environment:
    USERS_TABLE: ${self:service}-${self:provider.stage}-users
    JWT_SECRET: ${ssm:/${self:service}/${self:provider.stage}/jwt-secret~true}

  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:Query
            - dynamodb:Scan
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:UpdateItem
            - dynamodb:DeleteItem
          Resource:
            - "Fn::GetAtt": [ UsersTable, Arn ]

functions:
  # 注册
  register:
    handler: src/auth/register.handler
    events:
      - http:
          path: /auth/register
          method: post
          cors: true

  # 登录
  login:
    handler: src/auth/login.handler
    events:
      - http:
          path: /auth/login
          method: post
          cors: true

  # 获取用户列表 (需认证)
  listUsers:
    handler: src/users/list.handler
    events:
      - http:
          path: /users
          method: get
          cors: true
          authorizer:
            name: authorizerFunc
            resultTtlInSeconds: 300

  # 获取用户详情
  getUser:
    handler: src/users/get.handler
    events:
      - http:
          path: /users/{id}
          method: get
          cors: true
          authorizer: authorizerFunc

  # 更新用户
  updateUser:
    handler: src/users/update.handler
    events:
      - http:
          path: /users/{id}
          method: put
          cors: true
          authorizer: authorizerFunc

  # 删除用户
  deleteUser:
    handler: src/users/delete.handler
    events:
      - http:
          path: /users/{id}
          method: delete
          cors: true
          authorizer: authorizerFunc

  # JWT Authorizer
  authorizerFunc:
    handler: src/auth/authorizer.handler

resources:
  Resources:
    UsersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:provider.environment.USERS_TABLE}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
          - AttributeName: email
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
        GlobalSecondaryIndexes:
          - IndexName: EmailIndex
            KeySchema:
              - AttributeName: email
                KeyType: HASH
            Projection:
              ProjectionType: ALL
```

**完整代码实现见在线代码库**（这里展示核心逻辑）

---

## 2. 图片处理服务

### 场景: 自动图片优化

**架构**:

- S3触发Lambda
- 图片压缩/缩略图生成
- 多尺寸处理
- WebP转换

```yaml
# serverless.yml
service: image-processor

provider:
  name: aws
  runtime: nodejs18.x
  memorySize: 1024
  timeout: 300

  environment:
    SOURCE_BUCKET: ${self:service}-${self:provider.stage}-source
    DEST_BUCKET: ${self:service}-${self:provider.stage}-processed

  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - s3:GetObject
            - s3:PutObject
            - s3:PutObjectAcl
          Resource:
            - arn:aws:s3:::${self:provider.environment.SOURCE_BUCKET}/*
            - arn:aws:s3:::${self:provider.environment.DEST_BUCKET}/*

functions:
  processImage:
    handler: src/process.handler
    layers:
      - arn:aws:lambda:${self:provider.region}:123456789:layer:sharp:1
    events:
      - s3:
          bucket: ${self:provider.environment.SOURCE_BUCKET}
          event: s3:ObjectCreated:*
          rules:
            - suffix: .jpg
            - suffix: .png

resources:
  Resources:
    SourceBucket:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: ${self:provider.environment.SOURCE_BUCKET}

    DestBucket:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: ${self:provider.environment.DEST_BUCKET}
```

**完整图片处理示例见文档库**-

---

## 3. 数据处理Pipeline

### 场景: CSV数据ETL

**架构**:

- S3上传触发Lambda
- CSV解析
- 数据验证转换
- 批量写入DynamoDB

```yaml
# serverless.yml
service: data-pipeline

provider:
  name: aws
  runtime: python3.9
  memorySize: 512

functions:
  parseCSV:
    handler: src/parse.handler
    events:
      - s3:
          bucket: data-uploads
          event: s3:ObjectCreated:*
          rules:
            - suffix: .csv
    environment:
      DYNAMODB_TABLE: ProcessedData

  processData:
    handler: src/transform.handler
    events:
      - sqs:
          arn:
            Fn::GetAtt:
              - DataQueue
              - Arn
          batchSize: 10

  loadData:
    handler: src/load.handler
    events:
      - stream:
          type: dynamodb
          arn:
            Fn::GetAtt:
              - ProcessedDataTable
              - StreamArn
          batchSize: 100

resources:
  Resources:
    DataQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:service}-${self:provider.stage}-queue
        VisibilityTimeout: 300

    ProcessedDataTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ProcessedData
        StreamSpecification:
          StreamViewType: NEW_IMAGE
```

---

## 4. WebSocket实时应用

### 场景: 实时聊天

**架构**:

- API Gateway WebSocket
- Lambda处理连接/消息
- DynamoDB存储连接
- 广播消息

```yaml
# serverless.yml
service: websocket-chat

provider:
  name: aws
  runtime: nodejs18.x
  websocketsApiName: chat-websocket-api
  websocketsApiRouteSelectionExpression: $request.body.action

functions:
  connect:
    handler: src/connect.handler
    events:
      - websocket:
          route: $connect

  disconnect:
    handler: src/disconnect.handler
    events:
      - websocket:
          route: $disconnect

  sendMessage:
    handler: src/sendMessage.handler
    events:
      - websocket:
          route: sendMessage

  broadcast:
    handler: src/broadcast.handler
    events:
      - websocket:
          route: broadcast

resources:
  Resources:
    ConnectionsTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ChatConnections
        AttributeDefinitions:
          - AttributeName: connectionId
            AttributeType: S
        KeySchema:
          - AttributeName: connectionId
            KeyType: HASH
        BillingMode: PAY_PER_REQUEST
```

---

## 5. 事件驱动架构

### 场景: 电商订单处理

**架构**:

- EventBridge
- 多个Lambda处理不同事件
- Step Functions编排
- SNS通知

```yaml
# serverless.yml
service: order-processing

provider:
  name: aws
  runtime: nodejs18.x

functions:
  createOrder:
    handler: src/orders/create.handler
    events:
      - http:
          path: /orders
          method: post

  processPayment:
    handler: src/payments/process.handler
    events:
      - eventBridge:
          eventBus: default
          pattern:
            source:
              - order.service
            detail-type:
              - OrderCreated

  updateInventory:
    handler: src/inventory/update.handler
    events:
      - eventBridge:
          pattern:
            source:
              - payment.service
            detail-type:
              - PaymentProcessed

  sendNotification:
    handler: src/notifications/send.handler
    events:
      - eventBridge:
          pattern:
            source:
              - order.service
            detail-type:
              - OrderCompleted

resources:
  Resources:
    OrderStateMachine:
      Type: AWS::StepFunctions::StateMachine
      Properties:
        StateMachineName: OrderProcessing
        RoleArn: !GetAtt StepFunctionsRole.Arn
        DefinitionString: !Sub |
          {
            "StartAt": "ProcessPayment",
            "States": {
              "ProcessPayment": {
                "Type": "Task",
                "Resource": "${ProcessPaymentLambdaFunction.Arn}",
                "Next": "UpdateInventory"
              },
              "UpdateInventory": {
                "Type": "Task",
                "Resource": "${UpdateInventoryLambdaFunction.Arn}",
                "Next": "SendNotification"
              },
              "SendNotification": {
                "Type": "Task",
                "Resource": "${SendNotificationLambdaFunction.Arn}",
                "End": true
              }
            }
          }
```

---

## 6. 总结

```yaml
本章要点:
  ✅ REST API (完整CRUD + JWT认证)
  ✅ 图片处理 (S3触发 + Sharp)
  ✅ 数据Pipeline (CSV ETL)
  ✅ WebSocket (实时聊天)
  ✅ 事件驱动 (订单处理)

关键模式:
  ⭐ API Gateway + Lambda + DynamoDB
  ⭐ S3事件触发
  ⭐ SQS队列解耦
  ⭐ WebSocket实时通信
  ⭐ EventBridge事件总线
  ⭐ Step Functions编排

最佳实践:
  ✅ 错误处理
  ✅ 参数验证
  ✅ 日志记录
  ✅ 监控告警
  ✅ 测试覆盖
```

---

**完成日期**: 2025-10-19
**版本**: v1.0
**作者**: 云原生专家团队

**Tags**: `#ServerlessCases` `#RESTAPI` `#WebSocket` `#EventDriven` `#RealWorld`

---

## 相关文档

### 本模块相关

- [Serverless概述与架构](./01_Serverless概述与架构.md) - Serverless概述与架构
- [Knative深度解析](./02_Knative深度解析.md) - Knative深度解析
- [OpenFaaS实战](./03_OpenFaaS实战.md) - OpenFaaS实战
- [边缘Serverless](./04_边缘Serverless.md) - 边缘Serverless
- [Serverless安全](./05_Serverless安全.md) - Serverless安全
- [Serverless性能优化](./06_Serverless性能优化.md) - Serverless性能优化
- [Serverless CI/CD](./07_Serverless_CICD.md) - Serverless CI/CD
- [Serverless最佳实践](./09_Serverless最佳实践.md) - Serverless最佳实践
- [README.md](./README.md) - 本模块导航

### 其他模块相关

- [容器技术实践案例](../08_容器技术实践案例/README.md) - 容器技术实践案例
- [企业级容器化实践](../08_容器技术实践案例/01_企业级容器化实践.md) - 企业级容器化实践
- [微服务容器化案例](../08_容器技术实践案例/02_微服务容器化案例.md) - 微服务容器化案例
- [容器技术最佳实践](../08_容器技术实践案例/04_容器技术最佳实践.md) - 容器技术最佳实践

---

**最后更新**: 2025年11月11日
**维护状态**: 持续更新
