# 🎯 测试覆盖矩阵

> **完整的功能覆盖清单**  
> **最后更新**: 2025年10月23日

---

## 📊 Docker API 完整功能覆盖矩阵

### 1. 容器管理 (Container Management)

#### 1.1 容器生命周期 (Lifecycle)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **创建** | 基础创建 | 最小配置创建容器 | ✅ |
| | 完整配置创建 | 包含所有可选参数 | ❌ |
| | 从镜像创建 | 指定不同镜像版本 | ✅ |
| | 带命令创建 | 自定义启动命令 | ✅ |
| | 带环境变量创建 | 设置ENV变量 | ❌ |
| | 带标签创建 | 添加metadata标签 | ❌ |
| **启动** | 正常启动 | 启动已创建容器 | ✅ |
| | 重复启动 | 启动已运行容器 | ✅ |
| | 带附加模式启动 | 附加到容器输出 | ❌ |
| | 带检查点启动 | 从检查点恢复 | ❌ |
| **停止** | 优雅停止 | 使用SIGTERM | ✅ |
| | 强制停止 | 使用SIGKILL | ❌ |
| | 超时停止 | 设置停止超时 | ❌ |
| **重启** | 正常重启 | 重启运行中容器 | ❌ |
| | 超时重启 | 设置重启超时 | ❌ |
| **暂停/恢复** | 暂停容器 | 冻结容器进程 | ✅ |
| | 恢复容器 | 解冻容器进程 | ✅ |
| **删除** | 删除已停止容器 | 正常删除 | ✅ |
| | 强制删除运行中容器 | force=true | ✅ |
| | 批量删除 | 删除多个容器 | ❌ |
| | 删除关联卷 | 同时删除卷 | ❌ |

#### 1.2 容器配置 (Configuration)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **资源限制** | CPU限制 | CPUQuota/CPUPeriod | ✅ |
| | 内存限制 | Memory/MemorySwap | ✅ |
| | 磁盘IO限制 | BlkioWeight | ❌ |
| | PID限制 | PidsLimit | ❌ |
| **网络配置** | 默认网络 | bridge网络 | ❌ |
| | 自定义网络 | user-defined网络 | ✅ |
| | host网络 | --network=host | ❌ |
| | none网络 | 无网络 | ❌ |
| | 端口映射 | -p 8080:80 | ❌ |
| | 端口暴露 | --expose | ❌ |
| **存储配置** | 卷挂载 | -v volume:/data | ✅ |
| | 绑定挂载 | -v /host:/container | ❌ |
| | tmpfs挂载 | --tmpfs | ❌ |
| | 只读挂载 | :ro | ✅ |
| | 读写挂载 | :rw | ❌ |
| **安全配置** | 特权模式 | --privileged | ❌ |
| | capabilities | --cap-add/--cap-drop | ❌ |
| | seccomp | 安全计算模式 | ❌ |
| | AppArmor | AppArmor配置 | ❌ |

#### 1.3 容器检查与监控 (Inspection & Monitoring)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **信息查询** | 列出容器 | 全部/运行中 | ✅ |
| | 容器详情 | Inspect API | ✅ |
| | 容器进程 | Top API | ❌ |
| | 容器更改 | Changes API | ❌ |
| **日志管理** | 获取日志 | Logs API | ❌ |
| | 流式日志 | Follow logs | ❌ |
| | 日志时间戳 | Timestamps | ❌ |
| | 日志尾部 | Tail n lines | ❌ |
| **统计信息** | 资源统计 | Stats API | ❌ |
| | 流式统计 | Streaming stats | ❌ |
| **健康检查** | 健康状态 | Health status | ❌ |
| | 自定义健康检查 | Custom healthcheck | ❌ |

#### 1.4 容器操作 (Operations)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **文件操作** | 复制到容器 | Copy to container | ❌ |
| | 从容器复制 | Copy from container | ❌ |
| | 归档操作 | Archive API | ❌ |
| **执行命令** | 创建Exec | Create exec instance | ❌ |
| | 启动Exec | Start exec | ❌ |
| | 附加Exec | Attach to exec | ❌ |
| **导入导出** | 导出容器 | Export container | ❌ |
| | 提交容器 | Commit to image | ❌ |

### 2. 镜像管理 (Image Management)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **镜像操作** | 列出镜像 | List images | ✅ |
| | 拉取镜像 | Pull image | ✅ |
| | 推送镜像 | Push image | ❌ |
| | 删除镜像 | Remove image | ✅ |
| | 标签镜像 | Tag image | ❌ |
| **镜像构建** | 构建镜像 | Build from Dockerfile | ❌ |
| | 多阶段构建 | Multi-stage build | ❌ |
| **镜像检查** | 镜像详情 | Inspect image | ❌ |
| | 镜像历史 | Image history | ❌ |
| **导入导出** | 导出镜像 | Save image | ❌ |
| | 导入镜像 | Load image | ❌ |

### 3. 网络管理 (Network Management)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **网络操作** | 创建网络 | Create network | ✅ |
| | 列出网络 | List networks | ❌ |
| | 删除网络 | Remove network | ✅ |
| | 检查网络 | Inspect network | ❌ |
| **网络连接** | 连接容器 | Connect container | ❌ |
| | 断开容器 | Disconnect container | ❌ |
| **网络驱动** | bridge驱动 | Default bridge | ✅ |
| | host驱动 | Host networking | ❌ |
| | overlay驱动 | Overlay network | ❌ |
| | macvlan驱动 | Macvlan network | ❌ |

### 4. 卷管理 (Volume Management)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **卷操作** | 创建卷 | Create volume | ✅ |
| | 列出卷 | List volumes | ❌ |
| | 删除卷 | Remove volume | ✅ |
| | 检查卷 | Inspect volume | ❌ |
| **卷驱动** | local驱动 | Local volume | ✅ |
| | 外部驱动 | External drivers | ❌ |
| **卷共享** | 容器间共享 | Shared volumes | ✅ |
| | 只读共享 | Read-only volumes | ✅ |

---

## ☸️ Kubernetes API 完整功能覆盖矩阵

### 1. Pod管理

#### 1.1 Pod生命周期

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **创建Pod** | 单容器Pod | Basic pod | ✅ |
| | 多容器Pod | Sidecar pattern | ❌ |
| | Init容器 | Init containers | ❌ |
| | 临时容器 | Ephemeral containers | ❌ |
| **Pod配置** | 资源请求/限制 | Requests/Limits | ✅ |
| | 环境变量 | Env vars | ❌ |
| | ConfigMap | ConfigMap volumes | ❌ |
| | Secret | Secret volumes | ❌ |
| | 存活探针 | Liveness probe | ❌ |
| | 就绪探针 | Readiness probe | ❌ |
| | 启动探针 | Startup probe | ❌ |
| **Pod调度** | 节点选择器 | NodeSelector | ❌ |
| | 节点亲和性 | Node affinity | ❌ |
| | Pod亲和性 | Pod affinity | ❌ |
| | 污点容忍 | Tolerations | ❌ |
| **Pod安全** | SecurityContext | Security settings | ❌ |
| | PodSecurityPolicy | PSP | ❌ |
| | ServiceAccount | SA binding | ❌ |

#### 1.2 Pod操作

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **查询操作** | 列出Pod | List pods | ✅ |
| | 查看Pod详情 | Get pod | ✅ |
| | 查看Pod日志 | Get logs | ❌ |
| | 查看Pod事件 | Get events | ❌ |
| **修改操作** | 更新Pod | Update pod | ❌ |
| | Patch Pod | Patch pod | ❌ |
| **删除操作** | 删除单个Pod | Delete pod | ✅ |
| | 批量删除 | Delete collection | ❌ |
| | 优雅删除 | Graceful deletion | ❌ |
| **执行操作** | Exec进入Pod | Exec API | ❌ |
| | 端口转发 | Port forward | ❌ |
| | 附加容器 | Attach API | ❌ |

### 2. Workload资源

#### 2.1 Deployment

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **基础操作** | 创建Deployment | Create | ❌ |
| | 更新Deployment | Update | ❌ |
| | 删除Deployment | Delete | ❌ |
| **扩缩容** | 手动扩缩容 | Scale replicas | ❌ |
| | 自动扩缩容 | HPA | ❌ |
| **滚动更新** | 更新策略 | RollingUpdate | ✅ |
| | 回滚 | Rollback | ❌ |
| | 暂停/恢复 | Pause/Resume | ❌ |
| **状态检查** | 就绪状态 | Ready replicas | ❌ |
| | 更新状态 | Update status | ❌ |

#### 2.2 StatefulSet

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **基础操作** | 创建StatefulSet | Create | ❌ |
| | 更新StatefulSet | Update | ❌ |
| | 删除StatefulSet | Delete | ❌ |
| **有序管理** | 有序部署 | Ordered deployment | ❌ |
| | 有序删除 | Ordered deletion | ❌ |
| **持久化** | PVC模板 | VolumeClaimTemplates | ❌ |
| | 数据持久化 | Data persistence | ❌ |

#### 2.3 DaemonSet

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **基础操作** | 创建DaemonSet | Create | ❌ |
| | 更新DaemonSet | Update | ❌ |
| | 删除DaemonSet | Delete | ❌ |
| **调度** | 节点选择 | Node selector | ❌ |
| | 污点容忍 | Tolerations | ❌ |

#### 2.4 Job & CronJob

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **Job** | 创建Job | One-time job | ❌ |
| | 并行Job | Parallel jobs | ❌ |
| | Job完成 | Completion tracking | ❌ |
| **CronJob** | 创建CronJob | Scheduled job | ❌ |
| | Cron表达式 | Cron syntax | ❌ |
| | 并发策略 | Concurrency policy | ❌ |

### 3. Service & Networking

#### 3.1 Service

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **Service类型** | ClusterIP | Internal service | ✅ |
| | NodePort | External access | ❌ |
| | LoadBalancer | Cloud LB | ❌ |
| | ExternalName | External DNS | ❌ |
| **服务发现** | DNS解析 | Service DNS | ❌ |
| | 环境变量 | Service env vars | ❌ |
| **负载均衡** | 轮询 | Round robin | ❌ |
| | 会话亲和性 | Session affinity | ❌ |

#### 3.2 Ingress

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **Ingress规则** | 路径路由 | Path-based routing | ❌ |
| | 主机路由 | Host-based routing | ❌ |
| **TLS** | TLS终止 | TLS termination | ❌ |
| | 证书管理 | Certificate mgmt | ❌ |

#### 3.3 NetworkPolicy

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **策略类型** | Ingress策略 | Ingress rules | ❌ |
| | Egress策略 | Egress rules | ❌ |
| **选择器** | Pod选择器 | Pod selector | ❌ |
| | 命名空间选择器 | Namespace selector | ❌ |

### 4. 配置与存储

#### 4.1 ConfigMap

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **创建方式** | 字面值创建 | From literal | ❌ |
| | 文件创建 | From file | ❌ |
| | 目录创建 | From directory | ❌ |
| **使用方式** | 环境变量 | As env vars | ❌ |
| | 卷挂载 | As volumes | ❌ |
| | 命令行参数 | As args | ❌ |

#### 4.2 Secret

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **Secret类型** | Opaque | Generic secret | ❌ |
| | TLS | TLS secret | ❌ |
| | DockerConfig | Registry auth | ❌ |
| **使用方式** | 环境变量 | As env vars | ❌ |
| | 卷挂载 | As volumes | ❌ |

#### 4.3 PersistentVolume

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **PV操作** | 创建PV | Static PV | ❌ |
| | 删除PV | Delete PV | ❌ |
| **PVC操作** | 创建PVC | Claim PV | ❌ |
| | 绑定PVC | PVC binding | ❌ |
| | 扩容PVC | Resize PVC | ❌ |
| **StorageClass** | 动态供应 | Dynamic provisioning | ❌ |
| | 回收策略 | Reclaim policy | ❌ |

### 5. RBAC & 安全

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **Role/ClusterRole** | 创建角色 | Create role | ❌ |
| | 权限规则 | Rules definition | ❌ |
| **RoleBinding** | 绑定角色 | Bind role | ❌ |
| | 用户授权 | User authorization | ❌ |
| **ServiceAccount** | 创建SA | Create SA | ❌ |
| | Token管理 | Token management | ❌ |

---

## 🔗 功能联动测试矩阵

### Docker功能联动

| 主功能1 | 主功能2 | 联动场景 | 测试内容 | 状态 |
|---------|---------|----------|----------|------|
| **容器** | **网络** | 容器网络通信 | 同网络容器互通 | ✅ |
| | | 跨网络隔离 | 不同网络隔离 | ❌ |
| | | 端口映射 | 主机端口访问 | ❌ |
| **容器** | **卷** | 数据持久化 | 容器重启数据保留 | ✅ |
| | | 卷共享 | 多容器共享数据 | ✅ |
| | | 数据迁移 | 容器间数据迁移 | ❌ |
| **容器** | **镜像** | 容器构建 | 从容器创建镜像 | ❌ |
| | | 镜像更新 | 镜像版本升级 | ❌ |
| **网络** | **卷** | 网络存储 | NFS/CIFS卷 | ❌ |
| **多容器** | **编排** | 应用栈 | Docker Compose | ❌ |
| | | 依赖管理 | 容器启动顺序 | ❌ |

### Kubernetes功能联动

| 主功能1 | 主功能2 | 联动场景 | 测试内容 | 状态 |
|---------|---------|----------|----------|------|
| **Pod** | **Service** | 服务暴露 | Service发现Pod | ✅ |
| | | 负载均衡 | 流量分发 | ❌ |
| **Pod** | **ConfigMap** | 配置注入 | CM作为环境变量 | ❌ |
| | | 配置更新 | 热更新配置 | ❌ |
| **Pod** | **Secret** | 密钥注入 | Secret作为卷 | ❌ |
| | | 密钥轮转 | 密钥更新 | ❌ |
| **Deployment** | **Service** | 滚动更新 | 无缝更新 | ✅ |
| | | 金丝雀发布 | 灰度发布 | ❌ |
| **Pod** | **PV/PVC** | 持久化存储 | 数据持久化 | ❌ |
| | | 存储扩容 | PVC扩容 | ❌ |
| **Ingress** | **Service** | 外部访问 | HTTP路由 | ❌ |
| | | TLS终止 | HTTPS访问 | ❌ |
| **NetworkPolicy** | **Pod** | 网络隔离 | Pod间访问控制 | ❌ |
| **RBAC** | **ServiceAccount** | 权限控制 | API访问授权 | ❌ |

---

## 📈 测试覆盖率统计

### Docker API

- **容器管理**: 15/60 (25%)
- **镜像管理**: 3/16 (19%)
- **网络管理**: 3/16 (19%)
- **卷管理**: 4/12 (33%)
- **功能联动**: 3/15 (20%)
- **总体覆盖率**: 28/119 ≈ **24%**

### Kubernetes API

- **Pod管理**: 5/45 (11%)
- **Workload**: 1/30 (3%)
- **Service & Network**: 1/25 (4%)
- **配置与存储**: 0/24 (0%)
- **RBAC & 安全**: 0/8 (0%)
- **功能联动**: 2/16 (13%)
- **总体覆盖率**: 9/148 ≈ **6%**

### 总体

- **已实现**: 37
- **待实现**: 230
- **总体覆盖率**: 37/267 ≈ **14%**

---

## 🎯 优先级规划

### P0 - 核心功能 (必须实现)

- [x] 容器生命周期基础操作
- [ ] 容器配置完整测试
- [ ] Pod完整生命周期
- [ ] Deployment基础操作
- [ ] Service基础功能
- [ ] 存储卷基础操作

### P1 - 重要功能 (应该实现)

- [ ] 网络完整测试
- [ ] 日志和监控
- [ ] 资源配额和限制
- [ ] ConfigMap/Secret
- [ ] Ingress功能

### P2 - 扩展功能 (可以实现)

- [ ] 高级调度
- [ ] RBAC完整测试
- [ ] 自定义资源
- [ ] Operator模式

---

**最后更新**: 2025年10月23日  
**维护团队**: QA团队
